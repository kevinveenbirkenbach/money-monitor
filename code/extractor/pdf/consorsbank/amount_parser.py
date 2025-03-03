import re

class AmountParser:
    """Verarbeitet Beträge und formatiert diese."""
    
    @staticmethod
    def parse_amount(s):
        """Wandelt einen Betrag in float um."""
        s = s.strip()
        print(f"Raw amount string: {s}")  # Debug-Ausgabe
        sign = 1
        if s.endswith('+'):
            sign = 1
        elif s.endswith('-'):
            sign = -1
        s = s[:-1].strip()  # Entferne das Vorzeichenzeichen
        s = s.replace('.', '').replace(',', '.')
        print(f"Formatted amount string: {s}")  # Debug-Ausgabe
        try:
            return sign * float(s)
        except Exception as e:
            print(f"Error parsing amount: {e}")  # Debug-Ausgabe
            return None

    @staticmethod
    def format_amount(val):
        """Formatiert einen Betrag ins deutsche Format."""
        if val is None:
            return ""
        s = f"{abs(val):.2f}".replace('.', ',')
        return s + ("+" if val >= 0 else "-")