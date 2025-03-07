from code.logger import Logger

class TransactionLog:
    def __init__(self, logger: Logger, transactions: [Transaction] = None):
        self.logger = logger 
        # Initialize the list of transactions.
        # If no transactions are provided, use an empty list.
        self.transactions = transactions if transactions is not None else []

    def addTransaction(self, transaction: Transaction):
        # Add the given transaction to the list.
        self.transactions.append(transaction)

    def getAll(self):
        # Return all transactions.
        return self.transactions

    def _sort_key(self, transaction: Transaction, attribute: str):
        """
        Helper function that returns the sort key for a transaction based on the given attribute.
        If the attribute is a string, it is converted to lowercase for case-insensitive sorting.
        """
        value = getattr(transaction, attribute)
        if isinstance(value, str):
            return value.lower()
        return value

    def sort(self, attribute: str):
        """
        Sort the transactions list based on the provided attribute.
        The helper function '_sort_key' is used to generate the sort key for each transaction.
        """
        # Define a nested function to pass as the key function
        def sort_key(transaction: Transaction):
            return self._sort_key(transaction, attribute)
        
        self.transactions.sort(key=sort_key)
