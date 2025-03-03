import re

class ValutaLineParser:
    # Regex zum Erfassen einer Valutazeile
    valuta_line_pattern = re.compile(r"^(\d{2}\.\d{2}\.\d{4})(?:\s+(.*))?$")

    def parse(self, line: str) -> dict:
        """Parst eine Valutazeile und liefert ein Dict mit Valuta-Datum und eventuell vorhandenem Text."""
        match = self.valuta_line_pattern.match(line)
        if match:
            return {
                "valuta_date_str": match.group(1),
                "leftover_text": match.group(2)  # Kann None sein
            }
        return None
