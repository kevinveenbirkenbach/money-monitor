import csv
from ...model.transaction import Transaction
from ...logger import Logger
from .base import CSVExtractor
from code.model.account import Account, OwnerAccount

class DKBCSVExtractor(CSVExtractor):
    def parse_amount(self, amount_str):
        # Clean up the amount string: remove whitespace, quotes, and non-breaking spaces.
        amount_str = amount_str.strip().replace('"', '').replace("\u00A0", "").replace(" ", "")
        sign = 1
        if amount_str.endswith('+'):
            amount_str = amount_str[:-1].strip()
        elif amount_str.endswith('-'):
            amount_str = amount_str[:-1].strip()
            sign = -1
        try:
            # Remove thousand separators and convert the decimal comma to a dot.
            return sign * float(amount_str.replace(".", "").replace(",", "."))
        except ValueError as e:
            self.logger.error(f"Failed to convert amount '{amount_str}' in file {self.source}: {e}")

    def extract_transactions(self):
        # Open the CSV file with UTF-8 encoding and a semicolon delimiter.
        with open(self.source, newline='', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            rows = list(reader)
        # Find the header row starting from the second row (skip the first row with the Giro IBAN).
        header_row_index = next(
            (i for i, row in enumerate(rows[1:], start=1) if row and row[0].strip().lower() == "buchungsdatum"),
            None
        )
        if header_row_index is None:
            self.logger.error(f"No valid header row found in {self.source}.")
            return []

        headers = [h.strip().replace('"', '') for h in rows[header_row_index]]
        data_rows = rows[header_row_index + 1:]

        for row in data_rows:
            # Skip empty rows.
            if not any(field.strip() for field in row):
                continue
            data = dict(zip(headers, row))
            transaction = Transaction(self.logger, self.source)
            transaction.setValue(self.parse_amount(data.get("Betrag (€)", "0")))
            # Set the owner account using the extracted Giro IBAN.
            transaction.owner = OwnerAccount(
                self.logger, 
                id=rows[0][1].strip().replace('"', ''), 
                institute="DKB")
            if transaction.value > 0:
                transaction.owner.name = data.get("Zahlungsempfänger*in", "").strip()
                transaction.partner.name = data.get("Zahlungspflichtige*r", "").strip()
            else:
                transaction.owner.name = data.get("Zahlungspflichtige*r", "").strip()
                transaction.partner.name = data.get("Zahlungsempfänger*in", "").strip()
            transaction.partner.id = data.get("IBAN", "").strip()
            transaction.currency = "EUR"
            transaction.description = data.get("Verwendungszweck", "").strip()
            transaction.invoice.customer_reference = data.get("Kundenreferenz", "").strip()
            transaction.invoice.mandate_reference = data.get("Mandatsreferenz", "").strip()
            transaction.invoice.creditor_id = data.get("Gläubiger-ID", "").strip()
            transaction.setTransactionDate(data.get("Buchungsdatum", ""))
            self.appendTransaction(transaction)
        return self.transactions
