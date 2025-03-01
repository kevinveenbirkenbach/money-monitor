import csv
from datetime import datetime
from .transaction import Transaction
from .logger import Logger


class DKBCSVExtractor:
    def __init__(self, csv_path, debug=False):
        self.csv_path = csv_path
        self.transactions = []
        self.debug = debug
        self.logger = Logger(debug=debug)

    def parse_date(self, date_str):
        date_str = date_str.strip().replace('"', '')
        for fmt in ("%d.%m.%Y", "%d.%m.%y"):
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
        self.logger.error(f"Invalid date format '{date_str}' in file {self.csv_path}.")
        return date_str

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
            self.logger.error(f"Failed to convert amount '{amount_str}' in file {self.csv_path}: {e}")

    def extract_transactions(self):
        with open(self.csv_path, newline='', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            rows = list(reader)

        header_row_index = next((i for i, row in enumerate(rows) if row and row[0].strip().lower() == "buchungsdatum"), None)
        if header_row_index is None:
            self.logger.error(f"No valid header row found in {self.csv_path}.")
            return []

        headers = [h.strip().replace('"', '') for h in rows[header_row_index]]
        data_rows = rows[header_row_index + 1:]

        for row in data_rows:
            if not any(field.strip() for field in row):
                continue

            data = dict(zip(headers, row))
            # Konto (IBAN) wird zu "sender" wenn Betrag negativ ist, ansonsten zu "receiver"
            account = data.get("IBAN", "").strip()
            amount = self.parse_amount(data.get("Betrag (€)", "0"))
            if amount:
                sender = account if amount < 0 else ""  # Negativer Betrag bedeutet, dass der Sender das Konto ist
                receiver = account if amount >= 0 else ""  # Positiver Betrag bedeutet, dass der Empfänger das Konto ist

                transaction = Transaction(
                    self.parse_date(data.get("Buchungsdatum", "")),
                    data.get("Verwendungszweck", "").strip(),
                    amount,
                    sender,
                    receiver,
                    account,
                    self.csv_path,
                    "DKB",
                    "EUR",
                    data.get("Kundenreferenz", "").strip()
                )
                self.transactions.append(transaction)
                self.logger.debug(f"Transaction {transaction} appended.")
            else:
                self.logger.debug(f"Transaction {data} not appended, due to missing amount.")

        return self.transactions
