from datetime import datetime
import logging
from typing import List
from code.model.transaction import Transaction

class Validator:
    def __init__(self, start_value: float, start_date: str, end_value: float, end_date: str, logger: logging.Logger, owner_institute: str = None):
        self.start_value = start_value
        self.start_date = start_date
        self.end_value = end_value
        self.end_date = end_date
        self.logger = logger  # Logger instance to log messages
        self.owner_institute = owner_institute  # Optional: filter by owner institute

    def validate_transactions(self, transactions: List[Transaction]) -> bool:
        """Validates all transactions by summing the values from the start date to the end date."""
        start_date = datetime.strptime(self.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(self.end_date, "%Y-%m-%d")
        
        total_value = self.start_value  # Start with the start value

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
            if start_date <= transaction_date <= end_date:
                total_value += transaction.value  # Add the transaction value
                self.logger.debug(f"Added {transaction.value} for transaction {transaction.id} on {transaction.transaction_date}")

        # Log the total value after adding all relevant transactions
        self.logger.info(f"Total calculated value: {total_value}")

        # Compare the total value with the expected end value
        if total_value == self.end_value:
            self.logger.info("Validation passed: The total value matches the expected end value.")
            return True
        else:
            self.logger.error(f"Validation failed: The total value is {total_value}, but the expected end value is {self.end_value}.")
            return False
