import re
from pdfminer.high_level import extract_text
from code.model.transaction import Transaction
from ..base import PDFExtractor
import yaml
from code.logger import Logger
from .amount_parser import AmountParser
from .balance_parser import BalanceParser
from .date_parser import DateParser
from .transaction_parser import TransactionParser
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
            transaction = Transaction(logger=self.logger, source=self.source)
            transaction.type = m_block.group('type').strip()
            block = m_block.group('block')
            datum_raw, wert_raw, amount_extracted, datum_iso = TransactionParser.parse_transaction_details(block, transaction.type, global_year, transaction)
            current_balance = BalanceParser.parse_balance(block)
            
            if transaction.type == "GUTSCHRIFT" and (not amount_extracted or AmountParser.parse_amount(amount_extracted) is None):
                if self.previous_balance is not None and current_balance is not None:
                    diff = current_balance - self.previous_balance
                    amount_extracted = AmountParser.format_amount(diff)
                else:
                    amount_extracted = ""
                    
            amount_val = AmountParser.parse_amount(amount_extracted)
            transaction.owner.institute = "Consorsbank"
            transaction.owner.name = "Testowner"
            transaction.owner.id = "Testid"
            transaction.setValue(amount_val or 0.0)
            transaction.description = block.strip().replace(transaction.partner.name, "")
            transaction.currency = "EUR"
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
