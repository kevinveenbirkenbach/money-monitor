import csv
from .abstract import AbstractExporter

class CsvExporter(AbstractExporter):
    """Exports transactions to a CSV file."""
    def export(self)->None:
        if not self.doTransactionsExist():
            return
        try:
            with open(self.output_file, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                # Get the header keys from the first transaction's dictionary
                header = list(self.transactions_wrapper.getAll()[0].getDictionary().keys())
                writer.writerow(header)
                # Write each transaction's values in the same order as the header
                for transaction in self.transactions_wrapper.getAll():
                    data = transaction.getDictionary()
                    row = [data.get(key, "") for key in header]
                    writer.writerow(row)
            self.log.success(f"CSV file created: {self.output_file}")
        except Exception as e:
            self.log.error(f"Error exporting CSV: {e}")