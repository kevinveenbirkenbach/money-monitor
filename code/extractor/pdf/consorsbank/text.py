from code.logger import Logger
import re

class TextExtractor:
    def __init__(self, logger: Logger, text:str):
        self.text = text
        self.logger = logger

    def getIBAN(self)->str:
        match_iban =  re.search(r"(DE[0-9A-Z]{20})", self.text)
        if match_iban:
            return match_iban.group(1)
            print("IBAN:", iban)
        self.logger.error("No IBAN found.")

    def getAccountHolder(self)->str:
        # Extract the account holder (Kontoinhaber) and insert a space before uppercase letters
        #    We look for "Kontoinhaber " followed by one non-whitespace string.
        match_inhaber = re.search(r"Kontoinhaber\s+(\S+)", self.text)
        if match_inhaber:
            raw_name = match_inhaber.group(1)  # e.g., "KevinVeen-Birkenbach"
            # Insert a space wherever a lowercase letter ([a-z]) is directly followed by an uppercase letter ([A-Z]).
            return re.sub(r'([a-z])([A-Z])', r'\1 \2', raw_name)
        self.logger.error("No account holder found.")

    def getDate(self)->str:
        # Extract the date
        #    Searches for "Datum " followed by DD.MM.YY
        match_datum = re.search(r"(Datum\s+\d{2}\.\d{2}\.\d{2})", self.text)
        if match_datum:
            return match_datum.group(1)
        self.logger.error("No date found.")
        
    def getYear(self) -> str:
        """
        Extracts the year (in YYYY format) from a substring like "Datum 30.12.22".
        If the year is only two digits (e.g. '22'), it prepends '20' (=> '2022').
        Returns the four-digit year as a string, or logs an error if not found.
        """
        # This regex captures day, month, and year (either 2 or 4 digits).
        match_date = re.search(r"Datum\s+(\d{2})\.(\d{2})\.(\d{2,4})", self.text)
        if match_date:
            day, month, year = match_date.groups()
            # If the year is only two digits, convert to four digits
            if len(year) == 2:
                year = "20" + year  # e.g. '22' -> '2022'
            return year
        self.logger.warning("No valid date/year found.")
        return None

    def getCurrency(self)->str:
        match_currency = re.search(r"Kontow\S*hrung\s+([A-Z]{3})", self.text)
        if match_currency:
            return match_currency.group(1)
        self.logger.error("No currency found.")