import re
from datetime import datetime
import pdfplumber
from .transaction import Transaction
from .logger import Logger
from .extractor_pdf import BasePDFExtractor

class BarclaysPDFExtractor(BasePDFExtractor):
    def create_transaction(self, iso_date, description, amount_str, sender, currency, invoice, to_field):
        try:
            amount_value = float(amount_str)
            return Transaction(iso_date, description, amount_value, sender, self.source_document, self.bank_type, currency, invoice, to_field)
        except Exception as e:
            self.logger.error(f"Error converting amount '{amount_str}' in {iso_date} for file {self.source_document}.")
            self.logger.debug(f"Description: '{description}', Sender: '{sender}', Bank: '{self.bank_type}', Currency: '{currency}', Invoice: '{invoice}', To: '{to_field}'. Exception: {e}")
            return None

    def extract_transactions(self):
        with pdfplumber.open(self.source_document) as pdf:
            if not pdf.pages:
                self.logger.warning(f"No pages found in {self.source_document}")
                return []
            first_page_text = pdf.pages[0].extract_text()
            self.bank_type = "Barclays"
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue
                lines = text.split("\n")
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
                        sign = match.group(4)
                        if sign is None and num_str and num_str[-1] in "-+":
                            sign = num_str[-1]
                            num_str = num_str[:-1].strip()
                        try:
                            value = float(num_str.replace(".", "").replace(",", "."))
                        except Exception as e:
                            self.logger.error(f"Error converting number string '{num_str}' in file {self.source_document}: {e}")
                            value = 0.0
                        if sign == "-":
                            value = -value
                        try:
                            iso_date = datetime.strptime(date, "%d.%m.%Y").strftime("%Y-%m-%d")
                        except Exception as e:
                            self.logger.error(f"Date conversion error for '{date}' in file {self.source_document}: {e}")
                            iso_date = date
                        sender = self.account
                        currency = "EUR"
                        invoice = ""
                        to_field = ""
                        transaction = self.create_transaction(iso_date, description, str(value), sender, currency, invoice, to_field)
                        if transaction:
                            self.transactions.append(transaction)
        return self.transactions
