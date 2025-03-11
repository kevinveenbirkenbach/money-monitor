import re
import pdfplumber
import yaml
from code.model.log import Log
from .booking_line_parser import BarclaysBookingLineParser
from .additional_info_parser import BarclaysAdditionalInfoParser
from .iban_parser import BarclaysIBANParser
from .transaction_builder import BarclaysTransactionBuilder
from ..abstract import AbstractPDFExtractor
from code.converter.pdf import PDFConverter
from code.model.log import Log
from code.model.configuration import Configuration

class BarclaysPDFExtractor(AbstractPDFExtractor):
    """
    Extractor for Barclays account statements.
    Splits the PDF pages into lines and uses helper parsers and the transaction builder
    to create Transaction objects. Attempts to match as many fields as possible.
    """
    def __init__(self, source: str, log: Log, configuration:Configuration, pdf_converter:PDFConverter):
        super().__init__(source, log, configuration, pdf_converter)
        self.transactions = []
        self.booking_parser = BarclaysBookingLineParser()
        self.additional_parser = BarclaysAdditionalInfoParser()
        self.iban_parser = BarclaysIBANParser()
    
    def extract_transactions(self):
        pages = self.pdf_converter.getLazyPages()
        if not pages:
            self.log.warning(f"No pages found in {self.source}")
            return []
        
        # Gesamten PDF-Text lesen, um die IBAN zu extrahieren
        full_text = self.pdf_converter.getLazyFullText()
        account_iban = self.iban_parser.extract(full_text)
        if account_iban is None:
            self.log.warning(f"IBAN could not be extracted correctly from {self.source}")
        
        # Erstelle den TransactionBuilder mit den Barclays-spezifischen Daten
        builder = BarclaysTransactionBuilder(self.log, self.source, account_iban)
        
        # Iteriere seitenweise über die Zeilen
        for page in pages:
            lines = page.extract_text().splitlines()
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                booking_data = self.booking_parser.parse(line)
                if booking_data:
                    additional_infos = []
                    j = i + 1
                    # Sammle zusätzliche Informationszeilen, bis eine neue Buchungszeile gefunden wird
                    while j < len(lines):
                        sub_line = lines[j].strip()
                        if self.booking_parser.booking_line_pattern.match(sub_line):
                            break
                        info = self.additional_parser.parse(sub_line)
                        if info:
                            additional_infos.append(info)
                        j += 1
                    
                    transaction = builder.build_transaction(booking_data, additional_infos)
                    if transaction:
                        self.transactions.append(transaction)
                    i = j
                else:
                    i += 1
        return self.transactions
