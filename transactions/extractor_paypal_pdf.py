import re
from datetime import datetime
from pdfminer.high_level import extract_text
from .transaction import Transaction

class PayPalPDFExtractor:
    """Extrahiert Transaktionen aus einem PayPal PDF-Kontoauszug.
    Dabei wird der PayPal Transaktionscode als Transaction Hash gesetzt."""
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.transactions = []

    def extract_transactions(self):
        text = extract_text(self.pdf_path)
        lines = text.splitlines()
        # Finde die Header-Zeile, in der "Transaktionscode" vorkommt.
        header_index = None
        for i, line in enumerate(lines):
            if "Transaktionscode" in line:
                header_index = i
                break
        if header_index is None:
            return []  # Kein Hinweis auf PayPal-Transaktionen
        # Ab der Header-Zeile werden die Transaktionszeilen angenommen.
        for line in lines[header_index+1:]:
            # Wir nehmen Zeilen, die mit einem Datum (DD.MM.YYYY) beginnen
            if not re.match(r"^\d{2}\.\d{2}\.\d{4}", line):
                continue
            parts = line.split()
            if len(parts) < 6:
                continue  # nicht genügend Spalten
            # Spaltenbeispiel (vereinfachte Annahme):
            # parts[0]: Datum, parts[4]: Transaktionscode, parts[-1]: Netto-Betrag
            date_str = parts[0]
            try:
                iso_date = datetime.strptime(date_str, "%d.%m.%Y").strftime("%Y-%m-%d")
            except Exception:
                iso_date = date_str
            # Für die Beschreibung kombinieren wir z.B. Typ und Name (Spalten 1 bis 3)
            description = " ".join(parts[1:4])
            # Betrag: Letzte Spalte (Netto) – ersetze Komma durch Punkt
            try:
                amount = float(parts[-1].replace(",", "."))
            except Exception:
                amount = 0.0
            account = ""  # Kein Konto-Feld vorhanden
            bank = "PayPal"
            transaction_code = parts[4]  # Annahme: 5. Spalte enthält den Transaktionscode
            transaction = Transaction(iso_date, description, amount, account, self.pdf_path, bank)
            # Setze den Transaction Hash auf den PayPal Transaktionscode
            transaction.hash = transaction_code
            self.transactions.append(transaction)
        return self.transactions
