from datetime import datetime
import logging
from typing import List
from code.model.transaction import Transaction
import yaml
from datetime import date

class Validator:
    def __init__(self, start_value: float, start_date: date, end_value: float, end_date: date, logger: logging.Logger, owner_institute: str = None):
        self.start_value = start_value
        print(start_date)
        self.start_date = start_date
        self.end_value = end_value
        self.end_date = end_date
        self.logger = logger  # Logger instance to log messages
        self.owner_institute = owner_institute  # Optional: filter by owner institute

    def validate_transactions(self, transactions: List[Transaction]) -> bool:
        """Validates the sum of transactions between start_date and end_date."""
        
        total_value = self.start_value

        # Log the initial state
        self.logger.info(f"Starting validation with start_value: {self.start_value}, start_date: {self.start_date}, end_value: {self.end_value}, end_date: {self.end_date}")

        # Iterate over all transactions and sum the values within the date range
        for transaction in transactions:
            # If an owner institute is specified, only consider transactions where the institute matches
            if self.owner_institute and transaction.owner.institute != self.owner_institute:
                continue

            # Convert transaction date
            transaction_date = datetime.strptime(transaction.transaction_date, "%Y-%m-%d")
            
            # Check if the transaction date is within the specified date range
            if self.start_date <= transaction_date <= self.end_date:
                total_value += transaction.value  # Add the transaction value
                self.logger.debug(f"Added {transaction.value} for transaction {transaction.id} on {transaction.transaction_date}")

        # Log the total value after adding all relevant transactions
        self.logger.info(f"Total calculated value: {total_value}")

        # Compare the total value with the expected end value
        if total_value == self.end_value:
            self.logger.sucess(f"Validation passed for the period between {self.start_date} and {self.end_date}. Total value matches the expected end value.")
            return True
        else:
            self.logger.error(f"Validation failed for the period between {self.start_date} and {self.end_date}. Total value is {total_value}, but expected {self.end_value}.")
            return False

class TransactionValidator:
    def __init__(self, config:yaml, logger: logging.Logger):
        self.config = config
        self.logger = logger

    def validate(self, transactions):
        """Validates transactions based on the provided config data."""
        if 'institutes' in self.config:
            for institute, data in self.config['institutes'].items():
                if 'validate' in data:
                    self.logger.debug(f"Validating institute: {institute}")
                    validate_list = sorted(data['validate'], key=lambda x: x['date'])  # Sort by date

                    # Loop through pairs of dates and values for validation
                    for i in range(1, len(validate_list)):
                        start_point = validate_list[i-1]
                        end_point = validate_list[i]

                        # Prepare the validator for this date range
                        validator = Validator(
                            start_value=start_point['value'],
                            start_date=start_point['date'],
                            end_value=end_point['value'],
                            end_date=end_point['date'],
                            logger=self.logger,
                            owner_institute=data['owner']['id']  # Optional filtering by institute owner
                        )

                        # Perform validation for this range of transactions
                        if not validator.validate_transactions(transactions):
                            self.logger.error(f"Validation failed for {institute} between {start_point['date']} and {end_point['date']}")
                else:
                    self.logger.debug(f"No validation data for {institute} passed.")
        else:
            self.logger.debug(f"No institutes for validation defined in {config.data}")
