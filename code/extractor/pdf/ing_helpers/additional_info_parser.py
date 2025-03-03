import re

class AdditionalInfoParser:
    mandat_pattern = re.compile(r"^Mandat:\s*(\S+)")
    referenz_pattern = re.compile(r"^Referenz:\s*(\S+)")
    
    # Neuer Regex, der den ID-Teil und den Partnernamen trennt:
    # Er geht davon aus, dass der String mit "ARN", "1024" oder "NR" beginnt,
    # gefolgt von einer oder mehreren Ziffern und dann einem oder mehreren Buchstaben.
    id_partner_pattern = re.compile(r"^(ARN|1024|NR)(\d+)([A-Za-z].*)$")

    def parse(self, line: str) -> dict:
        """
        Parst zusätzliche Zeilen, die z. B. eine Transaktions-ID, Mandats- oder Referenzinformationen enthalten.
        """
        tokens = line.split(maxsplit=1)
        result = {}
        if tokens and len(tokens[0]) > 5 and tokens[0].startswith(("ARN", "1024", "NR")):
            # Versuche, den String in ID und Partner zu zerlegen
            match = self.id_partner_pattern.match(tokens[0])
            if match:
                # ID besteht aus Präfix + Ziffern
                result["id"] = match.group(1) + match.group(2)
                # Partner-Name aus dem restlichen Text; optional kannst du CamelCase in Leerzeichen auflösen
                partner_institute = match.group(3)
                # Beispiel: CamelCase in "GooglePay" -> "Google Pay"
                partner_institute = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', partner_institute)
                result["partner_institute"] = partner_institute.strip()
            else:
                # Fallback: Den gesamten Token als ID verwenden
                result["id"] = tokens[0]
            if len(tokens) > 1:
                result["description"] = tokens[1]
        else:
            mandat_match = self.mandat_pattern.match(line)
            if mandat_match:
                result["mandate_reference"] = mandat_match.group(1)
            else:
                referenz_match = self.referenz_pattern.match(line)
                if referenz_match:
                    result["customer_reference"] = referenz_match.group(1)
                else:
                    result["description"] = line
        return result
