import re

class BalanceParser:
    """Extrahiert den Kontostand aus dem Text."""
    
    @staticmethod
    def parse_balance(block):
        """Extrahiert den Kontostand aus dem Block."""
        balance_pattern = re.compile(r'\*\*\*\s*Kontostand zum [^\d]*\s*(?P<balance>[\d.,]+[+-])')
        balance_match = balance_pattern.search(block)
        if balance_match:
            return AmountParser.parse_amount(balance_match.group('balance'))
        return None