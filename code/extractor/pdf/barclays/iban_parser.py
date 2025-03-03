import re

class BarclaysIBANParser:
    """
    Extracts the IBAN from the full text of the Barclays statement.
    Example line: "IBAN: DE86 5001 0517 5426 7687 95"
    """
    IBAN_REGEX = re.compile(r"IBAN\s*:\s*(DE[0-9\s]{20,30})")
    
    def extract(self, text: str) -> str:
        match = self.IBAN_REGEX.search(text)
        if match:
            raw_iban = match.group(1)
            account_iban = re.sub(r"\s+", "", raw_iban)
            if len(account_iban) != 22:
                return None
            return account_iban
        return None
