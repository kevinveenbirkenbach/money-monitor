import re

class AdditionalInfoParser:
    mandat_pattern = re.compile(r"^Mandat:\s*(\S+)")
    referenz_pattern = re.compile(r"^Referenz:\s*(\S+)")

    def parse(self, line: str) -> dict:
        """
        Parst zusätzliche Zeilen, die z. B. eine Transaktions-ID, Mandats- oder Referenzinformationen enthalten.
        """
        tokens = line.split(maxsplit=1)
        result = {}
        if tokens and len(tokens[0]) > 5 and tokens[0].startswith(("ARN", "1024", "NR")):
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
