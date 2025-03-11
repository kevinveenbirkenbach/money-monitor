import re
from datetime import datetime
from ...model.transaction import Transaction
from .code.model.log import Log
from .base import PDFExtractor

# ATM using csv
class PayPalPDFExtractor(PDFExtractor):
    def extract_transactions(self):
        text = self.pdf_converter.getText()
        lines = text.splitlines()

        header_index = None
        for i, line in enumerate(lines):
            if "Transaktionscode" in line:
                header_index = i
                break

        if header_index is None:
            self.log.error(f"No 'Transaktionscode' header found in {self.source}.")
            return []

        for line in lines[header_index + 1:]:
            if not re.match(r"^\d{2}\.\d{2}\.\d{4}", line):
                continue

            parts = line.split()
            if len(parts) < 6:
                self.log.warning(f"Skipping line due to insufficient columns in {self.source}.")
                continue

            date_str = parts[0]
            try:
                iso_date = datetime.strptime(date_str, "%d.%m.%Y").strftime("%Y-%m-%d")
            except Exception as e:
                self.log.error(f"Date conversion error in {self.source} for '{date_str}': {e}")
                iso_date = date_str

            description = " ".join(parts[1:4])
            try:
                amount = float(parts[-1].replace(",", "."))
            except Exception as e:
                self.log.error(f"Amount conversion error in {self.source} for '{line}': {e}")
                amount = 0.0

            sender = ""
            currency = ""
            invoice = ""
            to_field = ""
            bank = "PayPal"
            transaction_code = parts[4]

            # Hier setzen wir das Account-Feld basierend auf dem Betrag
            account = sender if amount < 0 else to_field

            transaction = Transaction(iso_date, description, amount, sender, to_field, account, self.source, bank, currency, invoice)
            transaction.id = transaction_code
            self.transactions.append(transaction)

        return self.transactions
