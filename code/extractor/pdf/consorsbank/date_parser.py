import re

class DateParser:
    """Verarbeitet und konvertiert Datumsangaben."""
    
    @staticmethod
    def convert_to_iso(datum_str, global_year):
        """Konvertiert ein Datum in das ISO-Format."""
        datum_str = datum_str.strip()
        m = re.fullmatch(r'(\d{2})\.(\d{2})\.(\d{2,4})', datum_str)
        if m:
            day, month, year = m.groups()
            if len(year) == 2:
                year = "20" + year
            return f"{year}-{month}-{day}"
        m2 = re.fullmatch(r'(\d{2})\.(\d{2})\.', datum_str)
        if m2 and global_year:
            day, month = m2.groups()
            return f"{global_year}-{month}-{day}"
        return datum_str