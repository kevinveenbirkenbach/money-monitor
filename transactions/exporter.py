import csv

class CSVExporter:
    """Exportiert die extrahierten Transaktionen in eine CSV-Datei."""
    def __init__(self, transactions, output_file):
        self.transactions = transactions
        self.output_file = output_file

    def export(self):
        if not self.transactions:
            print("No transactions found to save.")
            return

        # Sortiere die Transaktionen nach Datum
        self.transactions.sort(key=lambda t: t.date)

        with open(self.output_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Date", "Description", "Amount (EUR)", "Account", "File Path", "Transaction Hash"])
            for transaction in self.transactions:
                writer.writerow(transaction.to_list())

        print(f"CSV file created: {self.output_file}")
