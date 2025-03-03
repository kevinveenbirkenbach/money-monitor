import re

class BookingLineParser:
    # Regex zum Erfassen der Buchungszeile
    booking_line_pattern = re.compile(
        r"^(\d{2}\.\d{2}\.\d{4})\s+(.+?)\s+(-?\d{1,3}(?:\.\d{3})*(?:,\d{2}))\s*(.*)?$"
    )
    # Regex zur Erkennung von "Lastschrift" oder "Gutschrift"
    type_pattern = re.compile(r"\b(Lastschrift|Gutschrift)\b", re.IGNORECASE)
    # Regex zur Erkennung von "VISA"
    visa_pattern = re.compile(r"\bVISA\b", re.IGNORECASE)

    def parse(self, line: str) -> dict:
        """Parst eine Buchungszeile und liefert ein Dict mit den extrahierten Werten zurück."""
        booking_match = self.booking_line_pattern.match(line)
        if not booking_match:
            return None

        buchung_date_str = booking_match.group(1)
        rest_of_line = booking_match.group(2).strip()
        amount_str = booking_match.group(3).replace(".", "").replace(",", ".")
        leftover_after_amount = booking_match.group(4) or ""

        # Transaktionstyp erkennen (z.B. "Lastschrift" oder "Gutschrift")
        transaction_type = None
        type_match = self.type_pattern.search(rest_of_line)
        if type_match:
            transaction_type = type_match.group(1).title()
            # Entferne den Typ aus dem Partnernamen
            rest_of_line = re.sub(self.type_pattern, "", rest_of_line, count=1).strip()

        # "VISA" erkennen
        transaction_medium = None
        visa_match = self.visa_pattern.search(rest_of_line)
        if visa_match:
            transaction_medium = "Visa"
            # Alles nach "VISA" als Partnername interpretieren
            partner_name = rest_of_line[visa_match.end():].strip()
        else:
            partner_name = rest_of_line

        return {
            "buchung_date_str": buchung_date_str,
            "partner_name": partner_name,
            "amount_str": amount_str,
            "leftover_after_amount": leftover_after_amount,
            "transaction_type": transaction_type,
            "transaction_medium": transaction_medium,
        }
