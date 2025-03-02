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
    Optimized extractor for ING Girokonto statements that may span multiple lines
    per transaction. For example:
    
        01.11.2018 Ueberweisung werwe GmbH -100,00
        01.11.2018 32X3-12312123
        ...
        Mandat: 11231231
        Referenz: 123123121342423
    """

    # Regex to capture the main transaction line:
    #   1) Date (dd.mm.yyyy)
    #   2) Description (any text until the last space group)
    #   3) Amount, possibly negative (like -140,00)
    transaction_line_pattern = re.compile(
        r"^(\d{2}\.\d{2}\.\d{4})\s+(.+?)\s+(-?\d{1,3}(?:\.\d{3})*(?:,\d{2})?)$"
    )

    # Regex to capture "Mandat: <some_id>"
    mandat_pattern = re.compile(r"^Mandat:\s*(\S+)")

    # Regex to capture "Referenz: <some_id>"
    referenz_pattern = re.compile(r"^Referenz:\s*(\S+)")

    def extract_transactions(self):
        with pdfplumber.open(self.source) as pdf:
            if not pdf.pages:
                self.logger.warning(f"No pages found in {self.source}")
                return []

            # Attempt to find the IBAN anywhere in the document
            full_text = ""
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                full_text += page_text + "\n"

                # Look for "IBAN" plus something that looks like DE + up to 20 digits,
                # possibly with spaces in between. Then strip out the spaces.
                iban_match = re.search(
                    r'IBAN\s+(DE[0-9\s]{20,30})',  # "DE" + 20 digits, allowing spaces
                    full_text
                )
                if iban_match:
                    raw_iban = iban_match.group(1)                # e.g. "DE86 5001 0517 5426 7687 95"
                    account_iban = re.sub(r'\s+', '', raw_iban)   # => "DE86500105175426768795"
                    # Optionally verify we have 22 characters:
                    if len(account_iban) == 22:
                        self.logger.debug(f"Captured IBAN: {account_iban}")
                    else:
                        self.logger.warning(
                            f"Found IBAN-like text but length != 22: {account_iban}"
                        )
                else:
                    account_iban = None

            # We will process each page line by line, building transactions
            # when we match the main transaction line pattern.
            for page in pdf.pages:
                lines = page.extract_text().splitlines()
                i = 0
                while i < len(lines):
                    line = lines[i].strip()
                    main_match = self.transaction_line_pattern.match(line)

                    if main_match:
                        # We found a main transaction line
                        date_str = main_match.group(1)
                        description = main_match.group(2).strip()
                        amount_str = main_match.group(3).replace(".", "").replace(",", ".")

                        # Create the Transaction object
                        transaction = Transaction(
                            logger=self.logger,
                            source=self.source,
                        )
                        # Owner = ING account
                        transaction.owner = OwnerAccount(
                            logger=self.logger,
                            id=account_iban,
                            institute="ING"
                        )
                        # Create an empty Invoice object
                        transaction.invoice = Invoice()

                        # Attempt to parse date
                        transaction.setTransactionDate(date_str)

                        # Convert amount to float
                        try:
                            transaction.value = float(amount_str)
                        except ValueError as e:
                            self.logger.error(
                                f"Error converting amount '{amount_str}' "
                                f"for date '{date_str}' in file {self.source}: {e}"
                            )
                            i += 1
                            continue

                        # Default currency
                        transaction.currency = "EUR"
                        transaction.description = description

                        # Decide sender/receiver based on sign of transaction.value
                        if transaction.value < 0:
                            # Negative => money leaving the owner’s account
                            transaction.setSender(transaction.owner)
                            transaction.partner = Account(self.logger)
                            transaction.setReceiver(transaction.partner)
                        else:
                            # Positive => money flowing into the owner’s account
                            transaction.partner = Account(self.logger)
                            transaction.setSender(transaction.partner)
                            transaction.setReceiver(transaction.owner)

                        # Now, look ahead for subsequent lines that belong to the same transaction
                        # e.g. second line of description, Mandat, Referenz, etc.
                        j = i + 1
                        while j < len(lines):
                            sub_line = lines[j].strip()

                            # Stop if we see another main transaction line
                            if self.transaction_line_pattern.match(sub_line):
                                break

                            # Check if the sub_line is a date + partial text line
                            # (like "01.11.2018 35C3-ZF9GQDJJET"), we can append to description
                            if re.match(r"^\d{2}\.\d{2}\.\d{4}\s", sub_line):
                                transaction.description += " " + sub_line

                            # Check for "Mandat: <some_id>"
                            mandat_match = self.mandat_pattern.match(sub_line)
                            if mandat_match:
                                transaction.invoice.mandate_reference = mandat_match.group(1)

                            # Check for "Referenz: <some_id>"
                            referenz_match = self.referenz_pattern.match(sub_line)
                            if referenz_match:
                                transaction.invoice.customer_reference = referenz_match.group(1)

                            j += 1

                        transaction.setTransactionId()
                        # We have built the transaction; add it to the list
                        self.transactions.append(transaction)

                        # Move i to j (we have consumed sub-lines)
                        i = j
                    else:
                        i += 1

        return self.transactions
