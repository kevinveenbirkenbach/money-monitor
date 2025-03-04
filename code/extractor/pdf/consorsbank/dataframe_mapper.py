import pandas as pd
import re
from typing import List, Optional
from code.model.transaction import Transaction
from code.logger import Logger


class ConsorsbankMapper:
    """
    Maps rows from a Consorsbank PDF DataFrame to a list of Transaction objects.
    
    A new transaction starts when the 'Text/Verwendungszweck' contains
    one of these triggers:
        - *** Kontostand zum
        - LASTSCHRIFT
        - GEBUEHREN
        - EURO-UEBERW.
        - GUTSCHRIFT
        - DAUERAUFTRAG
    
    The next lines populate partner info, description, date, PNNr, and value
    until the next trigger is found. Non-mappable lines produce a debug message.
    """
    TRIGGERS = ["*** Kontostand zum", "LASTSCHRIFT", "GEBUEHREN", "EURO-UEBERW.", "GUTSCHRIFT", "DAUERAUFTRAG"]

    def __init__(self, logger:Logger):
        self.logger = logger

    def map_transactions(self, df: pd.DataFrame) -> List[Transaction]:
        transactions: List[Transaction] = []
        current_tx: Optional[Transaction] = None
        line_index = 0  # We'll track which "line" of the transaction we're on (1..5)

        for i, row in df.iterrows():
            text_val = str(row.get("Text/Verwendungszweck", "")).strip()
            date_val = str(row.get("Datum", "")).strip()
            pnnr_val = str(row.get("PNNr", "")).strip()
            soll_val = str(row.get("Soll", "")).strip()
            haben_val = str(row.get("Haben", "")).strip()
            
            # 1) Check if this row is a trigger for a new transaction
            if any(trigger in text_val for trigger in self.TRIGGERS):
                # If we were building a transaction, save it first
                if current_tx is not None:
                    transactions.append(current_tx)
                
                # Start a new transaction
                current_tx = Transaction()
                
                # If it's not the *** Kontostand zum, we treat the text as the type
                # (If you want *** Kontostand zum to be a type, remove this check.)
                if text_val != "*** Kontostand zum":
                    current_tx.type = text_val
                
                line_index = 1
                # Don't skip the bounding-box columns; maybe we want to see if date/soll/haben is also in this row
                # so we continue to parse the rest of this row below if needed.
                continue

            # 2) If there's no active transaction, we can't map anything
            if not current_tx:
                if self.logger:
                    self.logger.debug(f"Row {i} not mapped (no active transaction): {row.to_dict()}")
                continue

            # 3) Map lines to transaction fields
            if line_index == 1:
                # This line is the partner name
                current_tx.partner_name = text_val
                line_index += 1
            elif line_index == 2:
                # This line is the partner institute
                current_tx.partner_institute = text_val
                line_index += 1
            elif line_index == 3:
                # This line is the description
                # If you want to accumulate description across multiple lines, 
                # you could append text_val instead of overwriting it
                current_tx.description = text_val
                line_index += 1
            elif line_index == 4:
                # This line presumably has date, PNNr, value
                current_tx.id = pnnr_val  # e.g. '8420'
                
                # Parse the date
                # If date_val has multiple dates, e.g. "31.10.22 10.10.", 
                # you might need more complex logic. Example:
                dates_found = date_val.split()
                if len(dates_found) >= 1:
                    current_tx.date = self._parse_date(dates_found[0])
                if len(dates_found) >= 2:
                    current_tx.valuta = self._parse_date(dates_found[1])
                
                # Evaluate the value from Soll or Haben
                current_tx.value = self._parse_value(soll_val, haben_val)
                
                # Once we've read line 4, we consider this transaction complete
                # If you want more lines, adapt line_index usage accordingly.
                line_index = 0
            else:
                # If we get here, we have an unexpected extra line
                if self.logger:
                    self.logger.debug(f"Row {i} not mapped (unexpected line index={line_index}): {row.to_dict()}")

        # 4) End of loop: if there's an unfinished transaction, add it
        if current_tx:
            transactions.append(current_tx)

        return transactions

    def _parse_date(self, date_str: str) -> str:
        """
        Converts a date like '31.10.22' to '2022-10-31'.
        If parsing fails, returns the original string or logs a debug message.
        """
        # Simple example with regex
        match = re.match(r'(\d{1,2})\.(\d{1,2})\.(\d{2,4})', date_str)
        if match:
            day, month, year = match.groups()
            # Heuristics to handle 2-digit vs 4-digit years:
            if len(year) == 2:
                year = "20" + year  # e.g. '22' -> '2022'
            # Build ISO string
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        else:
            if self.logger:
                self.logger.debug(f"Could not parse date from '{date_str}'")
            return date_str  # fallback

    def _parse_value(self, soll_str: str, haben_str: str) -> Optional[float]:
        """
        Parses a numeric value from either the Soll (negative) or Haben (positive) column.
        Example:
            soll_str = '5.000,00-' -> -5000.00
            haben_str = '19.159,00+' -> 19159.00
        """
        if soll_str:
            # Remove dots, convert comma to dot, remove trailing '-' if any
            val_str = soll_str.replace('.', '').replace(',', '.').replace('-', '')
            try:
                return -float(val_str)
            except ValueError:
                if self.logger:
                    self.logger.debug(f"Could not parse soll value from '{soll_str}'")
                return None
        elif haben_str:
            # Remove dots, convert comma to dot, remove trailing '+' if any
            val_str = haben_str.replace('.', '').replace(',', '.').replace('+', '')
            try:
                return float(val_str)
            except ValueError:
                if self.logger:
                    self.logger.debug(f"Could not parse haben value from '{haben_str}'")
                return None
        return None