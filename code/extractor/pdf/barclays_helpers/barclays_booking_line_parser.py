import re

class BarclaysBookingLineParser:
    """
    Parser for Barclays booking lines.
    Expected format:
      BookingDate ValutaDate Description [CardInfo] Amount
    Example:
      25.02.2022 28.02.2022 RST PRAIA REIS MAGOS   CANICO        PT Visa             17,00-
    """
    # Regex, um:
    #  - Gruppe 1: Buchungsdatum (z.B. 25.02.2022)
    #  - Gruppe 2: Valutadatum (z.B. 28.02.2022)
    #  - Gruppe 3: Beschreibung (alles zwischen den beiden Daten und dem optionalen CardInfo)
    #  - Gruppe 4: Optionaler Card-Info-Teil (z.B. PT, DE oder LU vor "Visa")
    #  - Gruppe 5: Betrag (z.B. 17,00-)
    booking_line_pattern = re.compile(
        r"^(\d{2}\.\d{2}\.\d{4})\s+(\d{2}\.\d{2}\.\d{4})\s+(.+?)\s+(?:(PT|DE|LU)\s+Visa\s+)?\s*([-]?\d{1,3}(?:\.\d{3})*(?:,\d{2})(?:[-+])?)$"
    )
    
    def parse(self, line: str) -> dict:
        match = self.booking_line_pattern.match(line)
        if not match:
            return None
        booking_date = match.group(1)
        valuta_date = match.group(2)
        description = match.group(3).strip()
        card_country = match.group(4)  # Optional: falls vorhanden
        amount_str = match.group(5).strip()
        
        # Betrag wird weiter unten in einen float konvertiert – entferne Tausenderpunkte und ersetze Komma
        amount_str = amount_str.replace(".", "").replace(",", ".")
        
        return {
            "booking_date_str": booking_date,
            "valuta_date_str": valuta_date,
            "description": description,
            "card_country": card_country,
            "amount_str": amount_str,
        }
