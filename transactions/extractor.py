import re
from datetime import datetime
import pdfplumber
from .transaction import Transaction

# transactions/extractor.py
import re
from datetime import datetime
import pdfplumber
from .transaction import Transaction

class PDFTransactionExtractor:
    """Extrahiert Transaktionen aus einem PDF-Bankauszug (für ING und Barclays)."""
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.transactions = []
        self.account = ""
        self.bank_type = "Unknown"

    def detect_bank_type(self, text):
        if not text:
            return "Unknown"
        lower_text = text.lower()
        if "ing-diba" in lower_text or "INGDDEFFXXX".lower() in lower_text:
            return "ING"
        elif "barclaycard" in lower_text or "barcdehaxx" in lower_text:
            return "Barclays"
        return "Unknown"

    def create_transaction(self, iso_date, description, amount_str, sender, currency, invoice, to_field):
        try:
            amount_value = float(amount_str)
            return Transaction(iso_date, description, amount_value, sender, self.pdf_path, self.bank_type, currency, invoice, to_field)
        except Exception as e:
            print(f"Error converting amount '{amount_str}' in {iso_date}. "
                  f"Description: '{description}', From: '{sender}', File: '{self.pdf_path}', Bank: '{self.bank_type}', "
                  f"Currency: '{currency}', Invoice: '{invoice}', To: '{to_field}'. Exception: {e}")


    def extract_transactions(self):
        with pdfplumber.open(self.pdf_path) as pdf:
            if not pdf.pages:
                print(f"Warning: No pages found in {self.pdf_path}")
                return []
            first_page_text = pdf.pages[0].extract_text()
            self.bank_type = self.detect_bank_type(first_page_text)
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue
                lines = text.split("\n")
                if self.bank_type == "ING":
                    iban_match = re.search(r"IBAN\s+(DE\d{2}\s\d{4}\s\d{4}\s\d{4}\s\d{2})", text)
                    if iban_match:
                        self.account = iban_match.group(1).replace(" ", "")
                    for line in lines:
                        match = re.match(r"(\d{2}\.\d{2}\.\d{4})\s+(.+?)\s+(-?\d{1,3}(?:\.\d{3})*(?:,\d{2})?)", line)
                        if match:
                            date = match.group(1)
                            description = match.group(2).strip()
                            amount = match.group(3).replace(".", "").replace(",", ".")
                            iso_date = datetime.strptime(date, "%d.%m.%Y").strftime("%Y-%m-%d")
                            sender = self.account
                            currency = "EUR"
                            invoice = ""
                            to_field = ""
                            transaction = self.create_transaction(iso_date, description, amount, sender, currency, invoice, to_field)
                            if transaction:
                                self.transactions.append(transaction)
                                
                elif self.bank_type == "Barclays":
                    iban_match = re.search(r"(?:IBAN\s+)?(DE\d{2}(?:\s+\d{4}){3}\s+\d{2})", text)
                    if iban_match:
                        self.account = iban_match.group(1).replace(" ", "")
                    for line in lines:
                        match = re.match(
                            r"(\d{2}\.\d{2}\.\d{4})\s+(.+?)\s+(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)\s*([-+])?",
                            line
                        )
                        if match:
                            date = match.group(1)
                            description = match.group(2).strip()
                            num_str = match.group(3)
                            sign = match.group(4)  # Kann "-", "+", oder None sein.
                            
                            if sign is None and num_str and num_str[-1] in "-+":
                                sign = num_str[-1]
                                num_str = num_str[:-1].strip()
                            
                            value = float(num_str.replace(".", "").replace(",", "."))

                            if sign == "-":
                                value = -value
                            iso_date = datetime.strptime(date, "%d.%m.%Y").strftime("%Y-%m-%d")
                            # Bei ING nehmen wir die IBAN als "sender" und setzen currency beispielsweise auf "EUR"
                            sender = self.account
                            currency = "EUR"
                            invoice = ""
                            to_field = ""

                            transaction = self.create_transaction(iso_date, description, value, sender, currency, invoice, to_field)
                            if transaction:
                                self.transactions.append(transaction)
        return self.transactions
