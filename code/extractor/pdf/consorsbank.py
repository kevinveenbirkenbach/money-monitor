import re
from pdfminer.high_level import extract_text
from code.model.transaction import Transaction
from .base import PDFExtractor
import yaml
from code.logger import Logger
from .consorsbank_helper.amount_parser import AmountParser
from .consorsbank_helper.balance_parser import BalanceParser
from .consorsbank_helper.date_parser import DateParser
from .consorsbank_helper.transaction_parser import TransactionParser

class ConsorsbankPDFExtractor(PDFExtractor):
    """Extrahiert Transaktionen aus einem Consorsbank-PDF."""
    
    def __init__(self, source: str, logger: Logger, config: yaml):
        super().__init__(source, logger, config)
        self.previous_balance = None
    
    def extract_transactions(self):
        text = extract_text(self.source)
        global_year = self._extract_year(text)
        block_pattern = re.compile(
            r'^(?P<type>LASTSCHRIFT|EURO-UEBERW\.|GUTSCHRIFT)\s*\n'
            r'(?P<block>.*?)(?=^(?:LASTSCHRIFT|EURO-UEBERW\.|GUTSCHRIFT)\s*\n|\Z)',
            re.DOTALL | re.MULTILINE
        )
        transactions = []
        for m_block in block_pattern.finditer(text):
            trans_type = m_block.group('type').strip()
            block = m_block.group('block')
            datum_raw, wert_raw, amount_extracted, datum_iso = TransactionParser.parse_transaction_details(block, trans_type, global_year)
            current_balance = BalanceParser.parse_balance(block)
            if trans_type == "GUTSCHRIFT" and (not amount_extracted or AmountParser.parse_amount(amount_extracted) is None):
                if self.previous_balance is not None and current_balance is not None:
                    diff = current_balance - self.previous_balance
                    amount_extracted = AmountParser.format_amount(diff)
                else:
                    amount_extracted = ""
            amount_val = AmountParser.parse_amount(amount_extracted)
            full_description = f"{trans_type}: {block.strip().replace('\n', ' ')}"
            transaction = Transaction(logger=self.logger, source=self.source)
            transaction.owner.institute = "Consorsbank"
            transaction.owner.name = "Testowner"
            transaction.owner.id = "Testid"
            transaction.setValue(amount_val or 0.0)
            transaction.description = full_description
            transaction.currency = "EUR"
            transaction.partner.id = "Example id"
            transaction.setTransactionDate(datum_iso or "2000-01-01")
            transaction.setTransactionId()
            transactions.append(transaction)
            if current_balance is not None:
                self.previous_balance = current_balance
        return transactions

    def _extract_year(self, text):
        """Extrahiert das Jahr aus dem Text, falls vorhanden."""
        year_match = re.search(r'\b\d{2}\.\d{2}\.(\d{2,4})\b', text)
        if year_match:
            year_str = year_match.group(1)
            return "20" + year_str if len(year_str) == 2 else year_str
        return None
