from .abstract import AbstractProcessor
from code.model.transaction import Transaction
from code.model.configuration import Configuration
from code.model.transactions_wrapper import TransactionsWrapper

class FilterProcessor(AbstractProcessor):
    def _filter_by_date(self,transactions:[Transaction])->[Transaction]:
        filtered = []
        for transaction in transactions:
            if self.configuration.getFromDatetime() and transaction.getTransactionDatetime() < self.configuration.getFromDatetime():
                self.log.debug(f"{transaction.getTransactionDatetime()} is < then {self.configuration.getFromDatetime()}. Skipped.")
                continue
            if self.configuration.getToDatetime() and transaction.getTransactionDatetime() > self.configuration.getToDatetime():
                self.log.debug(f"{transaction.getTransactionDatetime()} is > then {self.configuration.getToDatetime()}. Skipped.")
                continue
            self.log.debug(f"{transaction.getTransactionDatetime()} is inside the range. Appended.")
            filtered.append(transaction)
        self.log.debug(f"{len(filtered)} had been filtered.")
        return filtered
            
    def process(self)->TransactionsWrapper:
        all_transactions = self.transactions_wrapper.getAll()
        self.transactions_wrapper = TransactionsWrapper(
            self.log,self._filter_by_date(all_transactions)
            )
        return self.transactions_wrapper