from .abstract import AbstractProcessor
from code.validator.transaction import TransactionValidator
from code.model.transactions_wrapper import TransactionsWrapper

class ValidatorProcessor(AbstractProcessor):

    def process(self)->TransactionsWrapper:
        for transaction in self.transactions_wrapper.getAll():
            if not transaction.isValid():
                self.log.error(f"Unvalid transaction: {transaction}");

        if self.configuration.validate:
            # Create an instance of TransactionValidator and validate transactions
            validator = TransactionValidator(self.configuration, self.log)
            validator.validate(self.transactions_wrapper.getAll())
        
        return self.transactions_wrapper