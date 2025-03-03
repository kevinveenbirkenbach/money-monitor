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

    Extended to also parse:
      - transaction.type (e.g. 'Lastschrift', 'Gutschrift', etc.)
      - transaction.medium (e.g. 'Visa')
      - transaction.partner.name
      - transaction.id
      - transaction.description
    """

    booking_line_pattern = re.compile(
        r"^(\d{2}\.\d{2}\.\d{4})\s+(.+?)\s+(-?\d{1,3}(?:\.\d{3})*(?:,\d{2}))\s*(.*)?$"
    )
    valuta_line_pattern = re.compile(
        r"^(\d{2}\.\d{2}\.\d{4})(?:\s+(.*))?$"
    )

    mandat_pattern = re.compile(r"^Mandat:\s*(\S+)")
    referenz_pattern = re.compile(r"^Referenz:\s*(\S+)")

    # --- NEW/CHANGED ---
    # Patterns to detect "Lastschrift" or "Gutschrift" or "VISA" or "PayPal" in a line.
    # You can refine these if you have more payment types.
    type_pattern = re.compile(r"\b(Lastschrift|Gutschrift)\b", re.IGNORECASE)
    visa_pattern = re.compile(r"\bVISA\b", re.IGNORECASE)
    paypal_pattern = re.compile(r"\bPayPal\b", re.IGNORECASE)

    def extract_transactions(self):
        with pdfplumber.open(self.source) as pdf:
            if not pdf.pages:
                self.logger.warning(f"No pages found in {self.source}")
                return []

            # Read entire PDF text to find IBAN
            full_text = ""
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                full_text += page_text + "\n"

            # IBAN check
            iban_match = re.search(r"IBAN\s+(DE[0-9\s]{20,30})", full_text)
            if iban_match:
                raw_iban = iban_match.group(1)
                account_iban = re.sub(r"\s+", "", raw_iban)
                if len(account_iban) != 22:
                    self.logger.warning(f"Found IBAN but length != 22: {account_iban}")

            for page in pdf.pages:
                lines = page.extract_text().splitlines()
                i = 0
                while i < len(lines):
                    line = lines[i].strip()
                    booking_match = self.booking_line_pattern.match(line)

                    if booking_match:
                        buchung_date_str = booking_match.group(1)
                        # The line after the date could contain "Lastschrift VISA ...",
                        # or "Gutschrift PayPal ...", etc.
                        rest_of_line = booking_match.group(2).strip()
                        amount_str = booking_match.group(3).replace(".", "").replace(",", ".")
                        leftover_after_amount = booking_match.group(4) or ""

                        # --- NEW/CHANGED ---
                        # We'll parse the "rest_of_line" to detect transaction type, medium, partner, etc.
                        # Example: "Lastschrift PayPal Europe S.a.r.l. et Cie S.C.A"
                        # or "Lastschrift VISA ESTACION DE SERVICIOS"
                        # We'll do a simple approach: look for keywords and then parse out the partner name.
                        
                        transaction_type = None
                        transaction_medium = None
                        partner_name = rest_of_line

                        # 1) Detect 'Lastschrift' or 'Gutschrift'
                        type_match = self.type_pattern.search(rest_of_line)
                        if type_match:
                            transaction_type = type_match.group(1).title()  # e.g. "Lastschrift"
                            # Remove that word from the partner name
                            partner_name = re.sub(self.type_pattern, "", partner_name, count=1).strip()

                        # 2) Detect 'VISA' or 'PayPal'
                        if self.visa_pattern.search(rest_of_line) or self.visa_pattern.search(leftover_after_amount):
                            transaction_medium = "Visa"
                            partner_name = re.sub(self.visa_pattern, "", partner_name, count=1).strip()
                        elif self.paypal_pattern.search(rest_of_line):
                            transaction_medium = "PayPal"
                            partner_name = re.sub(self.paypal_pattern, "", partner_name, count=1).strip()

                        # Now we have partner_name without "Lastschrift"/"VISA"/"PayPal" tokens.
                        # The leftover text after the amount might also contain "Google Pay" or more text.

                        # Create the Transaction
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
                        transaction.invoice = Invoice()

                        # Set the booking date
                        transaction.setTransactionDate(buchung_date_str)

                        # Parse amount
                        try:
                            transaction.value = float(amount_str)
                        except ValueError as e:
                            self.logger.error(
                                f"Error converting amount '{amount_str}' in line '{line}' in file {self.source}: {e}"
                            )
                            i += 1
                            continue

                        transaction.currency = "EUR"

                        # --- NEW/CHANGED ---
                        # Fill the newly requested fields:
                        transaction.type = transaction_type             # e.g. "Lastschrift"
                        transaction.medium = transaction_medium         # e.g. "Visa"
                        transaction.partner.name = partner_name         # e.g. "PayPal Europe S.a.r.l. et Cie S.C.A"

                        # For the initial description, let's keep what's left in leftover_after_amount,
                        # plus any additional line info we'll parse below.
                        transaction.description = leftover_after_amount.strip()

                        # Decide sender/receiver based on sign
                        if transaction.value < 0:
                            transaction.setSender(transaction.owner)
                            transaction.partner = Account(self.logger)
                            transaction.setReceiver(transaction.partner)
                        else:
                            transaction.partner = Account(self.logger)
                            transaction.setSender(transaction.partner)
                            transaction.setReceiver(transaction.owner)

                        # Check the NEXT line for Valuta date
                        j = i + 1
                        if j < len(lines):
                            next_line = lines[j].strip()
                            valuta_match = self.valuta_line_pattern.match(next_line)
                            if valuta_match:
                                valuta_date_str = valuta_match.group(1)
                                transaction.setValutaDate(valuta_date_str)

                                leftover_text = valuta_match.group(2)
                                if leftover_text:
                                    # Append to the description
                                    if transaction.description:
                                        transaction.description += " "
                                    transaction.description += leftover_text.strip()
                                j += 1

                        # Additional lines for ID, Mandat, Referenz, or leftover description
                        # E.g.:
                        #   02.01.2023 1024397222446 PP.2617.PP . Google Payment
                        #   Mandat: 43QJ2252V8UDA
                        #   Referenz: 1024397222446
                        # or
                        #   ARN74940462363319920583874 Google Pay
                        while j < len(lines):
                            sub_line = lines[j].strip()

                            # If we see a new "Buchung" line or new Valuta line => break
                            if self.booking_line_pattern.match(sub_line):
                                break
                            if self.valuta_line_pattern.match(sub_line):
                                break

                            # If sub_line looks like "ARN74940462363319920583874 Google Pay", we treat ARN... as an ID
                            # or if sub_line looks like "1024397222446 PP.2617.PP . Google Payment"
                            # we can parse out the ID from the first token if we want.
                            # This is up to you. For example:
                            tokens = sub_line.split(maxsplit=1)
                            if len(tokens[0]) > 5 and tokens[0].startswith(("ARN", "1024", "NR")):
                                # We'll guess the first token is transaction.id
                                transaction.id = tokens[0]
                                # The rest we add to the description
                                if len(tokens) > 1:
                                    if transaction.description:
                                        transaction.description += " "
                                    transaction.description += tokens[1]
                            else:
                                # If it's Mandat or Referenz
                                mandat_match = self.mandat_pattern.match(sub_line)
                                if mandat_match:
                                    transaction.invoice.mandate_reference = mandat_match.group(1)
                                else:
                                    referenz_match = self.referenz_pattern.match(sub_line)
                                    if referenz_match:
                                        transaction.invoice.customer_reference = referenz_match.group(1)
                                    else:
                                        # Otherwise, just append to description
                                        if transaction.description:
                                            transaction.description += " "
                                        transaction.description += sub_line

                            j += 1

                        # If we never found an ID above, fallback to empty or parse logic
                        if not transaction.id:
                            transaction.id = ""

                        transaction.setTransactionId()
                        self.transactions.append(transaction)
                        i = j
                    else:
                        i += 1

        return self.transactions
