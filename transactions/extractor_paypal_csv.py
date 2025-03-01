import csv
from datetime import datetime
from .transaction import Transaction

class PayPalCSVExtractor:
    """Extrahiert Transaktionen aus einer PayPal CSV-Datei, sofern das Format passt."""
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.transactions = []

    def extract_transactions(self):
        with open(self.csv_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=',')
            headers = reader.fieldnames
            if not headers or "Transaktionscode" not in headers:
                return []  # kein PayPal-CSV-Format
            for row in reader:
                iso_date = datetime.strptime(row.get('\ufeff"Datum"', ""), "%d.%m.%Y").strftime("%Y-%m-%d").strip()
                # Beschreibung: Kombiniere z.B. Typ, Name und E-Mail-Adresse
                description = " ".join([
                    row.get("Beschreibung", "").strip(),
                    row.get("Typ", "").strip(),
                    row.get("Name", "").strip(),
                    row.get("E-Mail-Adresse", "").strip()
                ]).strip()
                # Betrag: Wir verwenden den Netto-Betrag und ersetzen Komma durch Punkt
                amount_str = row.get("Netto", "").replace(",", ".").strip()
                try:
                    amount = float(amount_str)
                except Exception:
                    amount = 0.0
                account = row.get("PayPal-ID", "").strip()
                file_path = self.csv_path
                bank = "PayPal"
                transaction_code = row.get("Transaktionscode", "").strip()
                transaction = Transaction(iso_date, description, amount, account, file_path, bank)
                # Setze den Transaktionscode als id, falls vorhanden.
                if transaction_code:
                    transaction.id = transaction_code
                self.transactions.append(transaction)
        return self.transactions
