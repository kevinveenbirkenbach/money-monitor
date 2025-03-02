import csv
from datetime import datetime
from ...model.transaction import Transaction
from ...logger import Logger
from .base import CSVExtractor

class PayPalCSVExtractor(CSVExtractor):
    def extract_transactions(self):
        with open(self.source, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=',')
            headers = reader.fieldnames
            transaction = Transaction(self.logger, self.source);
            if not headers or "Transaktionscode" not in headers:
                self.logger.error(f"Headers missing or 'Transaktionscode' not found in {self.source}.")
                return []
            for row in reader:
                try:
                    transaction.date = datetime.strptime(row.get('\ufeff"Datum"', ""), "%d.%m.%Y").strftime("%Y-%m-%d").strip()
                except Exception as e:
                    self.logger.error(f"Date conversion error in {self.source}: {e}")
                    transaction.date = row.get('\ufeff"Datum"', "").strip()
                transaction.partner     = row.get("Absender E-Mail-Adresse", "").strip() + row.get("Name", "").strip()
                transaction.id          = row.get("Transaktionscode", "").strip()
                transaction.description             = row.get("Beschreibung", "").strip()
                transaction.currency                = row.get("Währung", "").strip()
                transaction.value                   = float(row.get("Netto", "").replace(",", ".").strip())
                transaction.invoice                 = row.get("Rechnungsnummer", "").strip() if "Rechnungsnummer" in row else ""
                transaction.source   = self.source
                transaction.finance_institute       = "PayPal"
                self.appendTransaction(transaction);
        return self.transactions
