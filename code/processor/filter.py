from .abstract import AbstractProcessor
from code.model.transaction import Transaction
from code.model.configuration import Configuration

class FilterProcessor(AbstractProcessor):
    def _filter_by_date(self):
        if self.configuration.getFromDate() or self.configuration.getToDate():
            filtered = []
            for transaction in self.transactions_wrapper.getAll():
                if self.configuration.getFromDate() and transaction.getDictionary().get("date") < self.configuration.getFromDate():
                    continue
                if self.configuration.getToDate() and transaction.getDictionary().get("date") > self.configuration.getToDate():
                    continue
                filtered.append(transaction)
            return filtered
            
    def process(self):
        return self._filter_by_date()