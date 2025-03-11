from .abstract import AbstractProcessor
from code.model.transaction import Transaction
from code.model.configuration import Configuration
from code.model.transactions_wrapper import TransactionsWrapper

class FilterProcessor(AbstractProcessor):
    def _filter_valid_transactions(self,transactions:[Transaction])->[Transaction]:
        valid_transactions = []
        for transaction in self.transactions_wrapper.getAll():
            if transaction.isValid():
                valid_transactions.append(transaction)
            else:
                self.log.error(f"Invalid transaction: {transaction}");
        return valid_transactions
    
    def _filter_by_date(self,transactions:[Transaction])->[Transaction]:
        if self.configuration.getFromDatetime() or self.configuration.getToDatetime():
            filtered = []
            for transaction in transactions:
                if self.configuration.getFromDatetime() and transaction.getTransactionDatetime() <= self.configuration.getFromDatetime():
                    continue
                if self.configuration.getToDatetime() and transaction.getTransactionDatetime() >= self.configuration.getToDatetime():
                    continue
                filtered.append(transaction)
            return filtered
            
    def process(self)->TransactionsWrapper:
        all_transactions = self.transactions_wrapper.getAll()
        valid_transactions = self._filter_valid_transactions(all_transactions)
        filtered_by_date = self._filter_by_date(valid_transactions)
        filtered_wrapper = TransactionsWrapper(filtered_by_date)
        return filtered_wrapper