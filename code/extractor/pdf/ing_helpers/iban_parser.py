import re

class IBANParser:
    """
    Parser zur Extraktion der IBAN aus einem Text.
    """
    IBAN_REGEX = re.compile(r"IBAN\s+(DE[0-9\s]{20,30})")
    
    def extract(self, text: str) -> str:
        """
        Versucht, aus dem übergebenen Text eine IBAN zu extrahieren.
        Gibt die IBAN als String zurück, falls gefunden und korrekt formatiert,
        sonst None.
        """
        match = self.IBAN_REGEX.search(text)
        if match:
            raw_iban = match.group(1)
            account_iban = re.sub(r"\s+", "", raw_iban)
            if len(account_iban) != 22:
                return None
            return account_iban
        return None
