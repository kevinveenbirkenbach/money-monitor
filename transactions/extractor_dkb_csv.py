import csv
from datetime import datetime
from .transaction import Transaction
from .logger import Logger

class DKBCSVExtractor:
    """
    Extracts transactions from a DKB CSV file.
    
    The file is expected to be semicolon-separated and includes a few metadata rows at the beginning.
    The header row starts with "Buchungsdatum". The transaction rows follow.
    Example header:
      "Buchungsdatum";"Wertstellung";"Status";"Zahlungspflichtige*r";
      "Zahlungsempfänger*in";"Verwendungszweck";"Umsatztyp";"IBAN";
      "Betrag (€)";"Gläubiger-ID";"Mandatsreferenz";"Kundenreferenz"
    """
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
            except Exception:
                continue
        self.logger.error(f"Date string '{date_str}' does not match expected formats (%d.%m.%Y or %d.%m.%y) in file {self.csv_path}.")
        return date_str

    def parse_amount(self, amount_str):
        amount_str = amount_str.strip().replace('"', '')
        amount_str = amount_str.replace("\u00A0", "").replace(" ", "")
        sign = 1
        if amount_str.endswith('+'):
            amount_str = amount_str[:-1].strip()
            sign = 1
        elif amount_str.endswith('-'):
            amount_str = amount_str[:-1].strip()
            sign = -1
        try:
            value = float(amount_str.replace(".", "").replace(",", "."))
            return sign * value
        except Exception as e:
            self.logger.error(f"Could not convert amount '{amount_str}' in file {self.csv_path}: {e}")
            return 0.0

    def extract_transactions(self):
        with open(self.csv_path, newline='', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            rows = list(reader)
        
        header_row_index = None
        for i, row in enumerate(rows):
            if row and row[0].strip().replace('"', '').lower() == "buchungsdatum":
                header_row_index = i
                break
        
        if header_row_index is None:
            self.logger.error(f"No header row found in {self.csv_path}. This may not be a valid DKB CSV file.")
            return []
        
        headers = [h.strip().replace('"', '') for h in rows[header_row_index]]
        data_rows = rows[header_row_index+1:]
        for row in data_rows:
            if not any(field.strip() for field in row):
                continue
            
            data = dict(zip(headers, row))
            booking_date = self.parse_date(data.get("Buchungsdatum", ""))
            description = data.get("Verwendungszweck", "").strip()
            amount = self.parse_amount(data.get("Betrag (€)", "0"))
            sender = data.get("IBAN", "").strip()
            currency = "EUR"
            invoice = data.get("Kundenreferenz", "").strip() if "Kundenreferenz" in data else ""
            to_field = data.get("Zahlungsempfänger*in", "").strip() if "Zahlungsempfänger*in" in data else ""
            file_path = self.csv_path
            bank = "DKB"
            
            transaction = Transaction(booking_date, description, amount, sender, file_path, bank, currency, invoice, to_field)
            self.transactions.append(transaction)
        return self.transactions
