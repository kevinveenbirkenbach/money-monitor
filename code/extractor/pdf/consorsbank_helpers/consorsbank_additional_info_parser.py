import re

class ConsorsbankAdditionalInfoParser:
    """
    Parses additional information lines for Consorsbank transactions.
    Captures extra description and, if found, extracts partner institute information when VISA is mentioned.
    """
    visa_pattern = re.compile(r"\bVISA\b", re.IGNORECASE)
    
    def parse(self, line: str) -> dict:
        line = line.strip()
        if not line:
            return {}
        result = {}
        # Check if the line contains "VISA"
        visa_match = self.visa_pattern.search(line)
        if visa_match:
            result["medium"] = "Visa"
            # Everything after the "VISA" token is treated as partner institute information
            partner_institute = line[visa_match.end():].strip()
            if partner_institute:
                result["partner_institute"] = partner_institute
        else:
            # Otherwise, simply store the line as part of the transaction description.
            result["description"] = line
        return result
