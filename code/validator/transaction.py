from datetime import datetime, date
import logging
from typing import List
from code.model.transaction import Transaction
import yaml
from code.helper.datetime import createComparatableTime

class Validator:
    def __init__(self, start_value: float, start_date: date, end_value: float, end_date: date, margin: float, logger: logging.Logger, institute: str = None):
        self.start_value = start_value
        self.start_date = createComparatableTime(start_date)
        self.end_value = end_value
        self.end_date = createComparatableTime(end_date)
        self.margin = margin  # Margin for tolerance
        self.logger = logger  # Logger instance to log messages
        self.institute = institute.lower() if institute else None  # Optional: filter by owner institute
        # Debugging: Log the initialization of the Validator
        self.logger.debug(f"Validator initialized with start_value: {start_value}, start_date: {start_date}, "
                          f"end_value: {end_value}, end_date: {end_date}, institute: {institute}, margin: {margin}")

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
            transaction_date = createComparatableTime(transaction.date)
            
            self.logger.debug(f"Checking transaction {transaction.id} on {transaction_date} against date range "
                                f"{self.start_date} to {self.end_date}")

            # Check if the transaction date is within the specified date range
            if self.start_date <= transaction_date <= self.end_date:
                total_value += transaction.value  # Add the transaction value
                self.logger.debug(f"Added {transaction.value} for transaction {transaction.id} on {transaction.date}")

        total_value = round(total_value, 2)
        
        # Log the total value after adding all relevant transactions
        self.logger.debug(f"Total calculated value after transactions: {total_value}")

        # Margin tolerance check based on whether the margin is positive or negative
        if self.margin > 0:  # Positive margin: total_value can be larger than expected
            if total_value >= self.end_value and total_value <= (self.end_value + self.margin):
                self.logger.warning(f"Validation for {self.start_date} and {self.end_date} passed with warning:\nThe total value is within the margin tolerance "
                                    f"of {self.margin}. Total value: {total_value}, expected: {self.end_value}, difference: {round(total_value - self.end_value, 2)}.")
                return True
        elif self.margin < 0:  # Negative margin: total_value can be smaller than expected
            if total_value >= (self.end_value + self.margin) and total_value <= self.end_value:
                self.logger.warning(f"Validation for {self.start_date} and {self.end_date} passed with warning:\nThe total value is within the margin tolerance "
                                    f"of {self.margin}. Total value: {total_value}, expected: {self.end_value}, difference: {round(total_value - self.end_value, 2)}.")
                return True


        # Compare the total value with the expected end value
        if total_value == self.end_value:
            self.logger.success(f"Validation passed for the period between {self.start_date} and {self.end_date}. "
                                f"Total value matches the expected end value.")
            return True
        else:
            self.logger.error(f"Validation failed for the period between {self.start_date} and {self.end_date}. "
                                f"\nTotal value is {total_value}, but expected {self.end_value}.\nDifference: {round(total_value - self.end_value, 2)}")
            return False

class TransactionValidator:
    def __init__(self, config: yaml, logger: logging.Logger, from_date: str = None, to_date: str = None):
        self.config = config
        self.logger = logger
        self.from_date = createComparatableTime(datetime.strptime(from_date, "%Y-%m-%d")) if from_date else None
        self.to_date = createComparatableTime(datetime.strptime(from_date, "%Y-%m-%d")) if to_date else None

    def validate(self, transactions):
        """Validates transactions based on the provided config data."""
        if 'institutes' in self.config:
            for institute, data in self.config['institutes'].items():
                if 'validate' in data:
                    self.logger.debug(f"Validating institute: {institute}")
                    validate_list = sorted(data['validate'], key=lambda x: x['date'])  # Sort by date
                    self.logger.debug(f"Sorted validation data: {validate_list}")

                    # Filter the validation data to include only values within the date range
                    filtered_validate_list = [
                        validate for validate in validate_list
                        if (not self.from_date or createComparatableTime(validate['date']) >= self.from_date) and
                           (not self.to_date or createComparatableTime(validate['date']) <= self.to_date)
                    ]

                    if not filtered_validate_list:
                        self.logger.debug(f"No validation data found for {institute} within the date range. Skipping validation.")
                        continue

                    # Check if there are any transactions associated with this institute
                    institute_transactions = [
                        txn for txn in transactions if txn.owner.institute.lower() == institute
                    ]

                    if not institute_transactions:
                        self.logger.debug(f"No transactions found for institute {institute}. Skipping validation.")
                        continue  # Skip validation for this institute if no transactions are associated with it

                    # Loop through pairs of dates and values for validation
                    for i in range(1, len(filtered_validate_list)):
                        start_point = filtered_validate_list[i-1]
                        end_point = filtered_validate_list[i]

                        # Debug: Log the current validation pair
                        self.logger.debug(f"Validating for {institute} between {start_point['date']} and {end_point['date']}")

                        # Prepare the validator for this date range
                        margin = end_point.get("margin", 0)  # Get the margin for tolerance if provided
                        validator = Validator(
                            start_value=start_point['value'],
                            start_date=start_point['date'],
                            end_value=end_point['value'],
                            end_date=end_point['date'],
                            margin=margin,  # Add margin to the validation
                            logger=self.logger,
                            institute=institute  # Optional filtering by institute owner
                        )

                        # Perform validation for this range of transactions
                        if not validator.validate_transactions(institute_transactions):
                            self.logger.error(f"Validation failed for {institute} between {start_point['date']} and {end_point['date']}")

                            # Log all transactions in the date range and their values
                            self.logger.debug(f"Displaying transactions for {institute} between {start_point['date']} and {end_point['date']}:")
                            for txn in institute_transactions:
                                txn_date = txn.date
                                if start_point['date'] <= txn_date <= end_point['date']:
                                    self.logger.debug(f"Transaction ID: {txn.id}, Date: {txn_date}, Value: {txn.value}, Description: {txn.description}")
                        else:
                            self.logger.debug(f"Validation passed for {institute} between {start_point['date']} and {end_point['date']}")
                else:
                    self.logger.debug(f"No validation data for {institute} passed.")
        else:
            self.logger.debug(f"No institutes for validation defined in the config.")
