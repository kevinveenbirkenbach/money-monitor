import re
import pdfplumber
from datetime import datetime
from ...model.transaction import Transaction
from ...model.invoice import Invoice
from ...model.account import Account, OwnerAccount
from ...logger import Logger
from .base import PDFExtractor

class IngPDFExtractor(PDFExtractor):
    """
    Extractor for ING Girokonto statements that show:
      - First line: Buchung date, description, amount
      - Second line: Valuta date, optional extra text appended to description
      - Possible subsequent lines with "Mandat: ..." or "Referenz: ..."

    """

    # ----------------------------------------------------------

    # ----------------------------------------------------------
    # group(1): Buchung date (dd.mm.yyyy)
    # group(2): Description (any text until last space group)
    # group(3): Amount (possibly negative, e.g. -70,99)
    # Group(1) = date, Group(2) = description, Group(3) = amount, 
    # then optionally allow leftover text we can ignore.
    booking_line_pattern = re.compile(
        r"^(\d{2}\.\d{2}\.\d{4})\s+(.+?)\s+(-?\d{1,3}(?:\.\d{3})*(?:,\d{2}))\s*(.*)?$"
    )

    # ----------------------------------------------------------
    # 2) CHANGED: Regex to capture a line with Valuta date + leftover text
    #    e.g.: "30.12.2022 Cleaning"
    # ----------------------------------------------------------
    # group(1): Valuta date (dd.mm.yyyy)
    # group(2): Any leftover text appended to description
    valuta_line_pattern = re.compile(
        r"^(\d{2}\.\d{2}\.\d{4})(?:\s+(.*))?$"
    )

    # Regex for Mandat and Referenz lines
    mandat_pattern = re.compile(r"^Mandat:\s*(\S+)")
    referenz_pattern = re.compile(r"^Referenz:\s*(\S+)")

    def extract_transactions(self):
        # Attempt to open and read the PDF
        with pdfplumber.open(self.source) as pdf:
            if not pdf.pages:
                self.logger.warning(f"No pages found in {self.source}")
                return []

            # ----------------------------------------------------------
            # 3) CHANGED: We first read the entire PDF text to find the IBAN
            # ----------------------------------------------------------
            full_text = ""
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                full_text += page_text + "\n"

            # Search for a full 22-char IBAN, ignoring spaces
            iban_match = re.search(r"IBAN\s+(DE[0-9\s]{20,30})", full_text)
            if iban_match:
                raw_iban = iban_match.group(1)
                account_iban = re.sub(r"\s+", "", raw_iban)  # e.g. "DE86500105175426768795"
                if len(account_iban) != 22:
                    self.logger.warning(f"Found IBAN but length != 22: {account_iban}")
            else:
                account_iban = None

            # ----------------------------------------------------------
            # 4) CHANGED: Now parse line-by-line for each page
            # ----------------------------------------------------------
            for page in pdf.pages:
                lines = page.extract_text().splitlines()
                i = 0
                while i < len(lines):
                    line = lines[i].strip()
                    booking_match = self.booking_line_pattern.match(line)

                    if booking_match:
                        # We found a "Buchung" line with date, description, amount
                        buchung_date_str = booking_match.group(1)
                        description      = booking_match.group(2).strip()
                        amount_str       = booking_match.group(3).replace(".", "").replace(",", ".")

                        # Create Transaction
                        transaction = Transaction(
                            logger=self.logger,
                            source=self.source
                        )
                        # Assign an OwnerAccount
                        transaction.owner = OwnerAccount(
                            logger=self.logger,
                            id=account_iban,
                            institute="ING"
                        )
                        # Invoice object
                        transaction.invoice = Invoice()

                        # Set the booking date
                        transaction.setTransactionDate(buchung_date_str)

                        # Parse amount
                        try:
                            transaction.value = float(amount_str)
                        except ValueError as e:
                            self.logger.error(
                                f"Error converting amount '{amount_str}' "
                                f"for line '{line}' in file {self.source}: {e}"
                            )
                            i += 1
                            continue

                        transaction.currency = "EUR"
                        transaction.description = description

                        # Decide sender/receiver based on sign of transaction.value
                        if transaction.value < 0:
                            transaction.setSender(transaction.owner)
                            transaction.partner = Account(self.logger)
                            transaction.setReceiver(transaction.partner)
                        else:
                            transaction.partner = Account(self.logger)
                            transaction.setSender(transaction.partner)
                            transaction.setReceiver(transaction.owner)

                        # ----------------------------------------------------------
                        # 5) CHANGED: Check the NEXT line for Valuta date
                        #    e.g. "30.12.2022 Cleaning"
                        # ----------------------------------------------------------
                        j = i + 1
                        if j < len(lines):
                            next_line = lines[j].strip()
                            valuta_match = self.valuta_line_pattern.match(next_line)
                            if valuta_match:
                                # If there's a Valuta date on the next line:
                                valuta_date_str = valuta_match.group(1)
                                transaction.setValutaDate(valuta_date_str)

                                # If leftover text after the date, append to description
                                leftover_text = valuta_match.group(2)
                                if leftover_text:
                                    # Add a space + leftover to transaction.description
                                    transaction.description += f" {leftover_text}"
                                j += 1

                        # ----------------------------------------------------------
                        # 6) CHANGED: Additional lines for Mandat / Referenz
                        # ----------------------------------------------------------
                        while j < len(lines):
                            sub_line = lines[j].strip()

                            # If we see a new "Buchung" line, break
                            if self.booking_line_pattern.match(sub_line):
                                break
                            # If we see a new Valuta line, it might be a new transaction => break
                            if self.valuta_line_pattern.match(sub_line):
                                break

                            # Mandat?
                            mandat_match = self.mandat_pattern.match(sub_line)
                            if mandat_match:
                                transaction.invoice.mandate_reference = mandat_match.group(1)

                            # Referenz?
                            referenz_match = self.referenz_pattern.match(sub_line)
                            if referenz_match:
                                transaction.invoice.customer_reference = referenz_match.group(1)

                            j += 1

                        # Generate a transaction ID
                        transaction.setTransactionId()

                        # Append the transaction
                        self.transactions.append(transaction)

                        # Move the outer pointer
                        i = j
                    else:
                        # No match => move to next line
                        i += 1

        return self.transactions
