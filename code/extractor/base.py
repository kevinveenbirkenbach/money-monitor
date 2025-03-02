from ..model.transaction import Transaction
from ..logger import Logger
class Extractor:
    def __init__(self, source:str, logger:Logger):
        self.source    = source
        self.transactions                   = []
        self.logger                         = logger
    
    def appendTransaction(self, transaction:Transaction):
        transaction.setTransactionId()
        if transaction.isValid():
            self.transactions.append(transaction)
            self.logger.debug(f"Transaction {transaction} is valid and appended.")
        else:
            self.logger.warning(f"This transaction isn't valid:\n{transaction}")