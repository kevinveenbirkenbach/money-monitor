from datetime import datetime, date
import logging
from typing import List
from code.model.transaction import Transaction
import yaml

class Validator:
    def __init__(self, start_value: float, start_date: date, end_value: float, end_date: date, logger: logging.Logger, institute: str = None):
        self.start_value = start_value
        self.start_date = self._getDatetime(start_date)
        self.end_value = end_value
        self.end_date = self._getDatetime(end_date)
        self.logger = logger  # Logger instance to log messages
        self.institute = institute.lower()  # Optional: filter by owner institute

        # Debugging: Log the initialization of the Validator
        self.logger.debug(f"Validator initialized with start_value: {start_value}, start_date: {start_date}, "
                          f"end_value: {end_value}, end_date: {end_date}, institute: {institute}")
    
    def _getDatetime(self, date_and_or_time):
        # If it's a date (but not datetime), convert it to datetime
        if isinstance(date_and_or_time, date) and not isinstance(date_and_or_time, datetime):
            return datetime.combine(date_and_or_time, datetime.min.time())
        
        # If it's already a datetime, ensure it's naive (remove timezone info if it's aware)
        if isinstance(date_and_or_time, datetime):
            if date_and_or_time.tzinfo is not None:
                return date_and_or_time.replace(tzinfo=None)  # Convert aware datetime to naive datetime
            return date_and_or_time  # It's already naive, so return as is
        
        # Return the value if it's neither date nor datetime
        return None

        
    def validate_transactions(self, transactions: List[Transaction]) -> bool:
        """Validates the sum of transactions between start_date and end_date."""
        
        total_value = self.start_value
        self.logger.debug(f"Starting validation for transactions between {self.start_date} and {self.end_date}")

        # Iterate over all transactions and sum the values within the date range
        for transaction in transactions:
            # If an owner institute is specified, only consider transactions where the institute matches
            if self.institute and transaction.owner.institute.lower() != self.institute:
                self.logger.debug(f"Skipping transaction {transaction.id} due to owner institute mismatch")
                continue

            # Convert transaction date if it's a string or date
            transaction_date = self._getDatetime(transaction.date)
            
            self.logger.debug(f"Checking transaction {transaction.id} on {transaction_date} against date range "
                              f"{self.start_date} to {self.end_date}")

            # Check if the transaction date is within the specified date range
            if self.start_date <= transaction_date <= self.end_date:
                total_value += transaction.value  # Add the transaction value
                self.logger.debug(f"Added {transaction.value} for transaction {transaction.id} on {transaction.date}")

        total_value = round(total_value, 2)
        
        # Log the total value after adding all relevant transactions
        self.logger.debug(f"Total calculated value after transactions: {total_value}")

        # Compare the total value with the expected end value
        if total_value == self.end_value:
            self.logger.success(f"Validation passed for the period between {self.start_date} and {self.end_date}. "
                             f"Total value matches the expected end value.")
            return True
        else:
            self.logger.error(f"Validation failed for the period between {self.start_date} and {self.end_date}. "
                              f"Total value is {total_value}, but expected {self.end_value}.")
            return False

class TransactionValidator:
    def __init__(self, config: yaml, logger: logging.Logger):
        self.config = config
        self.logger = logger

    def validate(self, transactions):
        """Validates transactions based on the provided config data."""
        if 'institutes' in self.config:
            for institute, data in self.config['institutes'].items():
                if 'validate' in data:
                    self.logger.debug(f"Validating institute: {institute}")
                    validate_list = sorted(data['validate'], key=lambda x: x['date'])  # Sort by date
                    self.logger.debug(f"Sorted validation data: {validate_list}")

                    # Check if there are any transactions associated with this institute
                    institute_transactions = [
                        txn for txn in transactions if txn.owner.institute.lower() == institute
                    ]

                    if not institute_transactions:
                        self.logger.debug(f"No transactions found for institute {institute}. Skipping validation.")
                        continue  # Skip validation for this institute if no transactions are associated with it

                    # Loop through pairs of dates and values for validation
                    for i in range(1, len(validate_list)):
                        start_point = validate_list[i-1]
                        end_point = validate_list[i]

                        # Debug: Log the current validation pair
                        self.logger.debug(f"Validating for {institute} between {start_point['date']} and {end_point['date']}")

                        # Prepare the validator for this date range
                        validator = Validator(
                            start_value=start_point['value'],
                            start_date=start_point['date'],
                            end_value=end_point['value'],
                            end_date=end_point['date'],
                            logger=self.logger,
                            institute=institute  # Optional filtering by institute owner
                        )

                        # Perform validation for this range of transactions
                        if not validator.validate_transactions(institute_transactions):
                            self.logger.error(f"Validation failed for {institute} between {start_point['date']} and {end_point['date']}")
                        else:
                            self.logger.debug(f"Validation passed for {institute} between {start_point['date']} and {end_point['date']}")
                else:
                    self.logger.debug(f"No validation data for {institute} passed.")
        else:
            self.logger.debug(f"No institutes for validation defined in the config.")

