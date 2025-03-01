import csv
from datetime import datetime
from .transaction import Transaction

class PayPalCSVExtractor:
    """Extrahiert Transaktionen aus einer PayPal CSV-Datei, sofern das Format passt."""
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.transactions = []

# ... (Importe und Docstring bleiben unverändert)

    def extract_transactions(self):
        with open(self.csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=',')
            headers = reader.fieldnames
            if not headers or "Transaktionscode" not in headers:
                return []  # kein PayPal-CSV-Format
            for row in reader:
                iso_date = datetime.strptime(row.get('\ufeff"Datum"', ""), "%d.%m.%Y").strftime("%Y-%m-%d").strip()
                description = " ".join([
                    row.get("Beschreibung", "").strip(),
                    row.get("Typ", "").strip()
                ]).strip()
                amount_str = row.get("Netto", "").replace(",", ".").strip()
                try:
                    amount = float(amount_str)
                except Exception:
                    amount = 0.0
                # Ersetze Account durch From:
                sender = row.get("PayPal-ID", "").strip()
                # Neue Felder; hier beispielhaft aus optionalen Spalten (falls vorhanden)
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
