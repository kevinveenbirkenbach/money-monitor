import csv
from .transaction import Transaction
from .logger import Logger
from .extractor_csv import BaseCSVExtractor


class DKBCSVExtractor(BaseCSVExtractor):
    def parse_amount(self, amount_str):
        amount_str = amount_str.strip().replace('"', '').replace("\u00A0", "").replace(" ", "")
        sign = 1
        if amount_str.endswith('+'):
            amount_str = amount_str[:-1].strip()
        elif amount_str.endswith('-'):
            amount_str = amount_str[:-1].strip()
            sign = -1
        try:
            return sign * float(amount_str.replace(".", "").replace(",", "."))
        except ValueError as e:
            self.logger.error(f"Failed to convert amount '{amount_str}' in file {self.transaction_source_document}: {e}")

    def extract_transactions(self):
        with open(self.transaction_source_document, newline='', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            rows = list(reader)

        header_row_index = next((i for i, row in enumerate(rows) if row and row[0].strip().lower() == "buchungsdatum"), None)
        if header_row_index is None:
            self.logger.error(f"No valid header row found in {self.transaction_source_document}.")
            return []

        headers = [h.strip().replace('"', '') for h in rows[header_row_index]]
        data_rows = rows[header_row_index + 1:]

        for row in data_rows:
            if not any(field.strip() for field in row):
                continue
            data                                    = dict(zip(headers, row))
            transaction                             = Transaction(self.logger,self.transaction_source_document);
            transaction.setTransactionDate(data.get("Buchungsdatum", ""));  
            transaction.account_id                  = data.get("IBAN", "").strip()
            transaction.value                       = self.parse_amount(data.get("Betrag (€)", "0"))
            transaction.transaction_partner         = data.get("Kundenreferenz", "").strip()
            transaction.finance_institute           = "DKB"
            transaction.currency                    = "EUR"
            transaction.description                 = data.get("Verwendungszweck", "").strip()
            self.appendTransaction(transaction)
        return self.transactions
