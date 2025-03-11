import pandas as pd
import re
from typing import List, Optional
from code.model.transaction import Transaction
from code.model.log import Log
from .text import TextExtractor
from .date_parser import DateParser
from .invoice import extract_and_remove_invoices

class ConsorsbankDataframeMapper:
    """
    Maps rows from a Consorsbank PDF DataFrame to a list of Transaction objects.
    
    A new transaction starts whenever the 'Text/Verwendungszweck' contains
    one of these triggers.
    
    We first collect rows in 'blocks' until the next trigger is found.
    Then each block is mapped to a single Transaction object.
    """
    TRIGGERS = [
        "*** Kontostand zum",
        "LASTSCHRIFT",
        "GEBUEHREN",
        "EURO-UEBERW.",
        "GUTSCHRIFT",
        "DAUERAUFTRAG",
        "ABSCHLUSS"]

    def __init__(self, log: Log, source: str, textextractor:TextExtractor):
        self.log = log
        self.source = source
        self.textextractor = textextractor
        self.year = textextractor.getYear()

    def map_transactions(self, df: pd.DataFrame) -> List[Transaction]:
        """
        Main entry point: 
        1) Split the DataFrame rows into blocks, each block ends when a new trigger is found.
        2) Map each block to a Transaction.
        """
        blocks = self._split_into_blocks(df)
        transactions = []

        for idx, block in enumerate(blocks):
            transaction = self._map_block_to_transaction(block)
            if transaction:
                transactions.append(transaction)
            else:
                # Optionally log if the block couldn't be mapped
                self.log.debug(f"Block {idx} could not be mapped: {[r.to_dict() for r in block]}")

        return transactions

    def _split_into_blocks(self, df: pd.DataFrame) -> List[List[pd.Series]]:
        """
        Splits the DataFrame into a list of blocks (each block is a list of rows).
        A new block is started whenever we encounter a trigger in 'Text/Verwendungszweck'.
        """
        blocks: List[List[pd.Series]] = []
        current_block: List[pd.Series] = []

        for i, row in df.iterrows():
            text_val = str(row.get("Text/Verwendungszweck", "")).strip()

            # If we find a trigger, we finish the current block (if any) and start a new one
            if any(trigger in text_val for trigger in self.TRIGGERS):
                # Falls der current_block schon gefüllt ist, speichern wir ihn
                if current_block:
                    blocks.append(current_block)
                # Neuer Block mit der aktuellen Zeile als Start
                current_block = [row]
            else:
                # Einfach zur aktuellen Block-Liste hinzufügen
                current_block.append(row)

        # Am Ende den letzten Block noch anhängen
        if current_block:
            blocks.append(current_block)

        return blocks

    def _map_block_to_transaction(self, block: List[pd.Series]) -> Optional[Transaction]:
        """
        Converts a block (list of DataFrame rows) into a Transaction object.
        Returns None if the rows do not form a valid transaction.
        """
        if not block:
            return None

        first_row = block[0]
        text_val = str(first_row.get("Text/Verwendungszweck", "")).strip()

        # ---------------------------------------------------------
        # 1) Special case: Treat "ABSCHLUSS" as its own transaction
        # ---------------------------------------------------------
        if "ABSCHLUSS" in text_val:
            # Create a new transaction
            transaction = Transaction(self.log, self.source)
            transaction.type = "ABSCHLUSS"

            # Extract booking date + value date from columns "Datum" or "Wert"
            transaction.setTransactionDate(
                DateParser.convert_to_iso(first_row.get("Datum", ""), self.year)
            )
            transaction.setValutaDate(
                DateParser.convert_to_iso(first_row.get("Wert", ""), self.year)
            )

            # Owner data (if needed)
            transaction.owner.name = self.textextractor.getAccountHolder()
            transaction.owner.id = self.textextractor.getIBAN()
            transaction.owner.institute = "Consorsbank"

            # Parse amount from debit/credit
            debit_str = str(first_row.get("Soll", "")).strip()
            credit_str = str(first_row.get("Haben", "")).strip()
            transaction.value = self._parse_value(debit_str, credit_str) or 0.0

            # Optionally set a fixed description or extract from row
            transaction.description = "Closing fee (ABSCHLUSS)"

            # Generate a transaction ID
            transaction.setTransactionId()

            return transaction

        # ---------------------------------------------------------
        # 2) Ignore lines that are not actual transactions
        # ---------------------------------------------------------
        if "*** Kontostand zum" in text_val or "Consorsbank" in text_val:
            return None

        # ---------------------------------------------------------
        # 3) Normal bookings (e.g., LASTSCHRIFT, EURO-UEBERW.)
        # ---------------------------------------------------------
        # Example: Adapt to your data structure as needed
        # ---------------------------------------------------------

        transaction = Transaction(self.log, self.source)
        transaction.posting_number = str(first_row.get("PNNr", "")).strip()
        transaction.setValutaDate(
            DateParser.convert_to_iso(first_row.get("Wert", ""), self.year)
        )
        transaction.setTransactionDate(
            DateParser.convert_to_iso(first_row.get("Datum", ""), self.year)
        )
        transaction.type = text_val  # e.g., "LASTSCHRIFT"
        transaction.currency = self.textextractor.getCurrency()
        transaction.owner.name = self.textextractor.getAccountHolder()
        transaction.owner.id = self.textextractor.getIBAN()
        transaction.owner.institute = "Consorsbank"

        # For instance, partner data might be in block[1] + block[2] - watch out for indexing
        if len(block) > 1:
            transaction.partner.name = str(block[1].get("Text/Verwendungszweck", "")).strip()
        if len(block) > 2:
            transaction.partner.institute = str(block[2].get("Text/Verwendungszweck", "")).strip()

        # Build the description
        transaction.description = self._get_description(block)

        # Parse the transaction amount
        transaction.value = self._parse_value(
            str(first_row.get("Soll", "")).strip(),
            str(first_row.get("Haben", "")).strip()
        ) or 0.0
        
        invoices, cleaned_text = extract_and_remove_invoices(transaction.description)
        if invoices:
            transaction.description = cleaned_text
            transaction.invoice.id = "\n".join(invoices)
        transaction.setTransactionId()
        return transaction
    
    def _get_description(self,block):
        # Collect description lines from block[3] onward
        description_lines = []
        for row in block[3:]:
            # Gather the non-empty values from all columns in this row
            row_parts = []
            for col_name, col_val in row.items():
                val_str = str(col_val).strip()
                if val_str:
                    row_parts.append(val_str)
            
            # If this row has any non-empty columns, join them into a single string
            if row_parts:
                line_text = "".join(row_parts)
                description_lines.append(line_text)

        # Join all row strings into one final description
        if description_lines:
            description = " ".join(description_lines)
        return description


    def _parse_date(self, date_str: str) -> str:
        """
        Converts a date like '31.10.22' to '2022-10-31'.
        If parsing fails, returns the original string or logs a debug message.
        """
        match = re.match(r'(\d{1,2})\.(\d{1,2})\.(\d{2,4})', date_str)
        if match:
            day, month, year = match.groups()
            if len(year) == 2:
                year = "20" + year
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        else:
            self.log.debug(f"Could not parse date from '{date_str}'")
            return date_str

    def _parse_value(self, soll_str: str, haben_str: str) -> Optional[float]:
        if soll_str:
            val_str = soll_str.replace('.', '').replace(',', '.').replace('-', '')
            try:
                return -float(val_str)
            except ValueError:
                self.log.debug(f"Could not parse soll value from '{soll_str}'")
        elif haben_str:
            val_str = haben_str.replace('.', '').replace(',', '.').replace('+', '')
            try:
                return float(val_str)
            except ValueError:
                self.log.debug(f"Could not parse haben value from '{haben_str}'")
        return None
