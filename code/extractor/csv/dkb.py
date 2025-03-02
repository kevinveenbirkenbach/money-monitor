import csv
from ...model.transaction import Transaction
from ...logger import Logger
from .base import CSVExtractor
from code.model.account import Account, OwnerAccount


class DKBCSVExtractor(CSVExtractor):
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
            self.logger.error(f"Failed to convert amount '{amount_str}' in file {self.source}: {e}")

    def extract_transactions(self):
        with open(self.source, newline='', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            rows = list(reader)
            
        giro_iban = "test"

        header_row_index = next((i for i, row in enumerate(rows) if row and row[0].strip().lower() == "buchungsdatum"), None)
        if header_row_index is None:
            self.logger.error(f"No valid header row found in {self.source}.")
            return []

        headers = [h.strip().replace('"', '') for h in rows[header_row_index]]
        data_rows = rows[header_row_index + 1:]

        for row in data_rows:
            if not any(field.strip() for field in row):
                continue
            data                                    =   dict(zip(headers, row))
            transaction                             =   Transaction(self.logger,self.source);
            transaction.value                       =   self.parse_amount(data.get("Betrag (€)", "0"))
            transaction.owner                       =   OwnerAccount(self.logger,id=giro_iban,institute="DKB")
            partner                                 =   Account(self.logger,id=data.get("IBAN", "").strip())
            if transaction.value > 0:
                transaction.owner.name              =   data.get("Zahlungsempfänger*in", "").strip()
                transaction.setReceiver(transaction.owner)
                transaction.partner.name = data.get("Zahlungspflichtige*r", "").strip()
                transaction.setSender(transaction.partner)
            transaction.currency                    =   "EUR"
            transaction.description                 =   data.get("Verwendungszweck", "").strip()
            transaction.invoice_id                  =   data.get("Kundenreferenz", "").strip()
            transaction.setTransactionDate(data.get("Buchungsdatum", ""));
            self.appendTransaction(transaction)
        return self.transactions
