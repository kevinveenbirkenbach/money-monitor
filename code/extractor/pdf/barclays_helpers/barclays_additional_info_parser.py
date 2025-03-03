import re

class BarclaysAdditionalInfoParser:
    """
    Parses additional information lines for Barclays transactions.
    For example, a mandate reference or creditor identifier.
    """
    # Mandate reference: beginnt typischerweise mit 'P' gefolgt von Ziffern
    mandate_pattern = re.compile(r"^(P\d+)$")
    # Creditor identifier: beginnt typischerweise mit 'DE' gefolgt von Ziffern und Großbuchstaben
    creditor_pattern = re.compile(r"^(DE\d{2}[A-Z0-9]+)$")
    
    def parse(self, line: str) -> dict:
        result = {}
        line = line.strip()
        if not line:
            return result
        
        mandate_match = self.mandate_pattern.match(line)
        if mandate_match:
            result["mandate_reference"] = mandate_match.group(1)
            return result
        
        creditor_match = self.creditor_pattern.match(line)
        if creditor_match:
            result["creditor_id"] = creditor_match.group(1)
            return result
        
        # Falls die Zeile keinem bekannten Muster entspricht, als extra Beschreibung speichern
        result["extra_description"] = line
        return result
