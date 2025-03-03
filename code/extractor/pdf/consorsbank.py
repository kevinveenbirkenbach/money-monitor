import re
import pdfplumber
import yaml
from code.logger import Logger
from code.extractor.pdf.consorsbank_helpers.consorsbank_booking_line_parser import ConsorsbankBookingLineParser
from code.extractor.pdf.consorsbank_helpers.consorsbank_additional_info_parser import ConsorsbankAdditionalInfoParser
from code.extractor.pdf.consorsbank_helpers.consorsbank_iban_parser import ConsorsbankIBANParser
from code.extractor.pdf.consorsbank_helpers.consorsbank_transaction_builder import ConsorsbankTransactionBuilder
from .base import PDFExtractor  # Import the base extractor class

class ConsorsbankPDFExtractor(PDFExtractor):
    """
    Extractor for Consorsbank account statements.
    
    This class splits the PDF pages into lines and uses helper parsers and a transaction builder
    to create Transaction objects. It maps as many fields as possible.
    """
    def __init__(self, source: str, logger, config: yaml):
        super().__init__(source, logger, config)
        self.transactions = []
        self.booking_parser = ConsorsbankBookingLineParser()
        self.additional_parser = ConsorsbankAdditionalInfoParser()
        self.iban_parser = ConsorsbankIBANParser()
        # Use default year from config or fallback to 2022.
        self.default_year = config.get("default_year", 2022)
    
    def extract_transactions(self):
        with pdfplumber.open(self.source) as pdf:
            if not pdf.pages:
                self.logger.warning(f"No pages found in {self.source}")
                return []
            
            # Read the entire PDF text to extract the IBAN.
            full_text = ""
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                full_text += page_text + "\n"
            
            account_iban = self.iban_parser.extract(full_text)
            if account_iban is None:
                self.logger.warning(f"IBAN could not be extracted correctly from {self.source}")
            
            builder = ConsorsbankTransactionBuilder(self.logger, self.source, account_iban, self.default_year)
            
            # Collect all lines from the PDF pages.
            lines = []
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                lines.extend(page_text.splitlines())
            
            i = 0
            current_transaction_type = None
            while i < len(lines):
                line = lines[i].strip()
                # Check if the line is a transaction type indicator (e.g., "LASTSCHRIFT" or "GUTSCHRIFT").
                if line.upper() in ["LASTSCHRIFT", "GUTSCHRIFT"]:
                    current_transaction_type = line.upper()
                    i += 1
                    continue
                # Attempt to parse the booking line.
                booking_data = self.booking_parser.parse(line)
                if booking_data:
                    additional_infos = []
                    i += 1
                    # Gather additional lines until the next booking line or transaction type indicator is found.
                    while i < len(lines):
                        next_line = lines[i].strip()
                        if next_line.upper() in ["LASTSCHRIFT", "GUTSCHRIFT"]:
                            break
                        if self.booking_parser.booking_line_pattern.match(next_line):
                            break
                        info = self.additional_parser.parse(next_line)
                        if info:
                            additional_infos.append(info)
                        i += 1
                    
                    transaction = builder.build_transaction(current_transaction_type, booking_data, additional_infos)
                    if transaction:
                        self.transactions.append(transaction)
                else:
                    i += 1
            return self.transactions
