from .abstract import AbstractProcessor
from code.validator.transaction import TransactionValidator
from code.model.transactions_wrapper import TransactionsWrapper

class ValidatorProcessor(AbstractProcessor):

    def process(self)->TransactionsWrapper:
        if self.configuration.validate:
            # Create an instance of TransactionValidator and validate transactions
            validator = TransactionValidator(self.configuration, self.log)
            validator.validate(transactions)
        
        return self.transactions_wrapper