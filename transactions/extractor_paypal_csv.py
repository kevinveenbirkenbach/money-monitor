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
            # Wir erwarten, dass der Header mindestens "Datum" und "Transaktionscode" enthält.
            headers = reader.fieldnames
            if not headers or "Transaktionscode" not in headers:
                return []  # kein PayPal-CSV-Format
            for row in reader:
                # Datum: Wir gehen davon aus, dass es im Format DD.MM.YYYY vorliegt
                date_str = row.get("Datum", "").strip()
                try:
                    iso_date = datetime.strptime(date_str, "%d.%m.%Y").strftime("%Y-%m-%d")
                except Exception:
                    iso_date = date_str
                # Beschreibung: Kombiniere z.B. Typ, Name und E-Mail-Adresse
                description = " ".join([
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
                # Account: Falls vorhanden (z. B. PayPal-ID)
                account = row.get("PayPal-ID", "").strip()
                # Als File-Pfad speichern wir den CSV-Pfad
                file_path = self.csv_path
                # Bank wird auf "PayPal" gesetzt
                bank = "PayPal"
                # Transaktionscode als Hash übernehmen
                transaction_code = row.get("Transaktionscode", "").strip()
                transaction = Transaction(iso_date, description, amount, account, file_path, bank)
                # Überschreibe den automatisch generierten Hash mit dem PayPal Transaktionscode,
                # sofern vorhanden.
                if transaction_code:
                    transaction.hash = transaction_code
                self.transactions.append(transaction)
        return self.transactions
