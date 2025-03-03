import re

class ConsorsbankBookingLineParser:
    """
    Parser for Consorsbank booking lines.
    
    Expected booking line format (example):
      "01.11. 8999 01.11. 8,99-"
    
    Groups:
      1. Booking date (DD.MM.)
      2. Valuta date (DD.MM.)
      3. Amount with sign (e.g., "8,99-" or "16.422,00+")
    """
    booking_line_pattern = re.compile(
        r"^(\d{2}\.\d{2}\.)\s+\d+\s+(\d{2}\.\d{2}\.)\s+([\d.,]+[-+])$"
    )
    
    def parse(self, line: str) -> dict:
        match = self.booking_line_pattern.match(line)
        if not match:
            return None
        booking_date = match.group(1).strip()
        valuta_date = match.group(2).strip()
        amount_str = match.group(3).strip()
        # Optionally, you could add a default description if desired
        return {
            "booking_date_str": booking_date,
            "valuta_date_str": valuta_date,
            "amount_str": amount_str,
            # In Consorsbank, the booking line itself does not contain a description.
            # The description can be later accumulated from additional lines.
            "description": ""
        }
