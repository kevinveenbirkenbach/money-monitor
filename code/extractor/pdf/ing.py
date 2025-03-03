import re
import pdfplumber
import yaml
from code.logger import Logger
from code.extractor.pdf.ing_helpers.booking_line_parser import BookingLineParser
from code.extractor.pdf.ing_helpers.valuta_line_parser import ValutaLineParser
from code.extractor.pdf.ing_helpers.additional_info_parser import AdditionalInfoParser
from code.extractor.pdf.ing_helpers.transaction_builder import TransactionBuilder
from code.extractor.pdf.ing_helpers.iban_parser import IBANParser
from .base import PDFExtractor  # Basisklasse importieren

class IngPDFExtractor(PDFExtractor):
    """
    Extraktor für ING Girokonto-Auszüge.
    Verantwortlich für das Aufteilen der PDF-Seiten in Zeilen und das Verwenden der
    kleineren Parser-Klassen sowie des TransactionBuilders zur Erstellung von Transaction-Objekten.
    """
    def __init__(self, source: str, logger: Logger, config: yaml):
        super().__init__(source, logger, config)
        self.transactions = []
        self.booking_parser = BookingLineParser()
        self.valuta_parser = ValutaLineParser()
        self.additional_parser = AdditionalInfoParser()
        self.iban_parser = IBANParser()

    def extract_transactions(self):
        with pdfplumber.open(self.source) as pdf:
            if not pdf.pages:
                self.logger.warning(f"No pages found in {self.source}")
                return []

            # Gesamten PDF-Text lesen, um die IBAN zu finden
            full_text = ""
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                full_text += page_text + "\n"

            # IBAN extrahieren mithilfe des IBAN-Parsers
            account_iban = self.iban_parser.extract(full_text)
            if account_iban is None:
                self.logger.warning(f"IBAN konnte nicht korrekt extrahiert werden aus {self.source}")

            # Transaktionen seitenweise parsen
            builder = TransactionBuilder(self.logger, self.source, account_iban)
            for page in pdf.pages:
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
