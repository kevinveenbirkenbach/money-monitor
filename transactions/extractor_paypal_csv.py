import csv
from datetime import datetime
from .transaction import Transaction
from .logger import Logger


class PayPalCSVExtractor:
    def __init__(self, csv_path, debug=False):
        self.csv_path = csv_path
        self.transactions = []
        self.debug = debug
        self.logger = Logger(debug=debug)

    def extract_transactions(self):
        with open(self.csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=',')
            headers = reader.fieldnames
            if not headers or "Transaktionscode" not in headers:
                self.logger.error(f"Headers missing or 'Transaktionscode' not found in {self.csv_path}.")
                return []  # not a valid PayPal CSV format
            for row in reader:
                try:
                    iso_date = datetime.strptime(row.get('\ufeff"Datum"', ""), "%d.%m.%Y").strftime("%Y-%m-%d").strip()
                except Exception as e:
                    self.logger.error(f"Date conversion error in {self.csv_path}: {e}")
                    iso_date = row.get('\ufeff"Datum"', "").strip()
                description = " ".join([
                    row.get("Beschreibung", "").strip(),
                    row.get("Typ", "").strip()
                ]).strip()
                amount_str = row.get("Netto", "").replace(",", ".").strip()
                try:
                    amount = float(amount_str)
                except Exception as e:
                    self.logger.error(f"Amount conversion error in {self.csv_path}: {e}")
                    amount = 0.0
                sender = row.get("PayPal-ID", "").strip()
                currency = row.get("Währung", "").strip() if "Währung" in row else ""
                invoice = row.get("Rechnungsnummer", "").strip() if "Rechnungsnummer" in row else ""
                to_field = row.get("Name", "").strip()
                file_path = self.csv_path
                bank = "PayPal"
                transaction_code = row.get("Transaktionscode", "").strip()
                transaction = Transaction(iso_date, description, amount, sender, file_path, bank, currency, invoice, to_field)
                if transaction_code:
                    transaction.id = transaction_code
                self.transactions.append(transaction)
        return self.transactions
