from code.model.transaction import Transaction
from code.model.log import Log
from code.model.configuration import Configuration
from abc import ABC, abstractmethod

class AbstractExtractor(ABC):
    def __init__(self, source:str, log:Log, configuration:Configuration):
        self.source         = source
        self.transactions   = []
        self.log            = log
        self.configuration  = configuration
    
    def appendTransaction(self, transaction:Transaction):
        transaction.setTransactionId()
        if transaction.isValid():
            self.transactions.append(transaction)
            self.log.debug(f"Transaction {transaction} is valid and appended.")
        else:
            self.log.warning(f"This transaction isn't valid:\n{transaction}")