import re
import pdfplumber
import yaml
from code.model.log import Log
from .booking_line_parser import BookingLineParser
from .valuta_line_parser import ValutaLineParser
from .additional_info_parser import AdditionalInfoParser
from .transaction_builder import TransactionBuilder
from .iban_parser import IBANParser
from ..abstract import AbstractPDFExtractor
from code.converter.pdf import PDFConverter
from code.model.configuration import Configuration

class IngPDFExtractor(AbstractPDFExtractor):
    """
    Extraktor für ING Girokonto-Auszüge.
    Verantwortlich für das Aufteilen der PDF-Seiten in Zeilen und das Verwenden der
    kleineren Parser-Klassen sowie des TransactionBuilders zur Erstellung von Transaction-Objekten.
    """
    def __init__(self, source: str, log: Log, configuration:Configuration, pdf_converter:PDFConverter):
        super().__init__(source, log, configuration, pdf_converter)
        self.transactions = []
        self.booking_parser = BookingLineParser()
        self.valuta_parser = ValutaLineParser()
        self.additional_parser = AdditionalInfoParser()
        self.iban_parser = IBANParser()

    def extract_transactions(self):
        if not self.pdf_converter.getLazyPages():
            self.log.warning(f"No pages found in {self.source}")
            return []
        
        # Gesamten PDF-Text lesen, um die IBAN zu finden
        full_text = ""
        for page in self.pdf_converter.getLazyPages():
            page_text = page.extract_text() or ""
            full_text += page_text + "\n"
            
        # IBAN extrahieren mithilfe des IBAN-Parsers
        account_iban = self.iban_parser.extract(full_text)
        if account_iban is None:
            self.log.warning(f"IBAN konnte nicht korrekt extrahiert werden aus {self.source}")
            
        # Transaktionen seitenweise parsen
        builder = TransactionBuilder(self.log, self.source, account_iban)
        for page in self.pdf_converter.getLazyPages():
            lines = page.extract_text().splitlines()
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                booking_data = self.booking_parser.parse(line)
                if booking_data:
                    valuta_data = None
                    additional_infos = []
                    j = i + 1
                    
                    # Prüfe, ob die nächste Zeile ein Valuta-Datum enthält
                    if j < len(lines):
                        next_line = lines[j].strip()
                        temp_valuta = self.valuta_parser.parse(next_line)
                        if temp_valuta:
                            valuta_data = temp_valuta
                            j += 1
                            
                    # Sammle zusätzliche Informationen
                    while j < len(lines):
                        sub_line = lines[j].strip()
                        # Beende, wenn eine neue Buchungs- oder Valuta-Zeile beginnt
                        if self.booking_parser.booking_line_pattern.match(sub_line) or \
                           self.valuta_parser.valuta_line_pattern.match(sub_line):
                            break
                        additional_infos.append(self.additional_parser.parse(sub_line))
                        j += 1
                    transaction = builder.build_transaction(booking_data, valuta_data, additional_infos)
                    if transaction:
                        self.transactions.append(transaction)
                    i = j
                else:
                    i += 1
        return self.transactions
