import csv
from .base import Exporter

class CSVExporter(Exporter):
    """Exports transactions to a CSV file."""
    def export(self):
        if not self.transactions:
            self.logger.warning("No transactions found to save.")
            return
        try:
            with open(self.output_file, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                # Get the header keys from the first transaction's dictionary
                header = list(self.transactions[0].__dict__.keys())
                writer.writerow(header)
                # Write each transaction's values in the same order as the header
                for t in self.transactions:
                    data = t.__dict__
                    row = [data.get(key, "") for key in header]
                    writer.writerow(row)
            self.logger.success(f"CSV file created: {self.output_file}")
        except Exception as e:
            self.logger.error(f"Error exporting CSV: {e}")