import re

class ConsorsbankIBANParser:
    """
    Extracts the IBAN from Consorsbank statements.
    
    Example: "IBAN DE15760300800260337647"
    """
    IBAN_REGEX = re.compile(r"IBAN\s+(DE[0-9\s]{20,30})")
    
    def extract(self, text: str) -> str:
        match = self.IBAN_REGEX.search(text)
        if match:
            raw_iban = match.group(1)
            account_iban = re.sub(r"\s+", "", raw_iban)
            if len(account_iban) != 22:
                return None
            return account_iban
        return None
