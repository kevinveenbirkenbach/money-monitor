from .abstract import AbstractExporter

class ConsoleExporter(AbstractExporter):
    """Prints the transactions on the console"""
    def export(self)->None:
        if not self.doTransactionsExist():
            return
        for transaction in self.transactions_wrapper.getAll():
            print(f"{transaction.date}\t{transaction.description}\t{transaction.value}\t{transaction.sender}\t{transaction.source}\t{transaction.bank}\t{transaction.id}")