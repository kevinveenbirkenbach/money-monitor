from .transaction import Transaction
from .logger import Logger
class BaseExtractor:
    def __init__(self, transaction_source_document:str, logger:Logger):
        self.transaction_source_document    = transaction_source_document
        self.transactions                   = []
        self.logger                         = logger
    
    def appendTransaction(self, transaction:Transaction):
        transaction.setTransactionId()
        if transaction.isValid():
            self.transactions.append(transaction)
            self.logger.debug(f"Transaction {transaction} is valid and appended.")
        else:
            self.logger.warning(f"This transaction isn't valid:\n{transaction}")