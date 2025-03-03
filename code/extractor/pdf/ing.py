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
      - transaction.medium = 'Visa' (only if line contains "VISA")
      - transaction.partner.name (everything after "VISA")
      - transaction.id
      - transaction.description
    """

    # 1) Regex to capture date, description, amount in one line
    booking_line_pattern = re.compile(
        r"^(\d{2}\.\d{2}\.\d{4})\s+(.+?)\s+(-?\d{1,3}(?:\.\d{3})*(?:,\d{2}))\s*(.*)?$"
    )

    # 2) Regex to capture a line with Valuta date + leftover text
    valuta_line_pattern = re.compile(
        r"^(\d{2}\.\d{2}\.\d{4})(?:\s+(.*))?$"
    )

    # 3) Regex to capture "Mandat: ..." or "Referenz: ..."
    mandat_pattern = re.compile(r"^Mandat:\s*(\S+)")
    referenz_pattern = re.compile(r"^Referenz:\s*(\S+)")

    # 4) Regex to detect "Lastschrift" or "Gutschrift" in the line
    type_pattern = re.compile(r"\b(Lastschrift|Gutschrift)\b", re.IGNORECASE)

    # 5) Regex to detect "VISA" in the line (for setting transaction.medium = "Visa")
    visa_pattern = re.compile(r"\bVISA\b", re.IGNORECASE)

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

            # Attempt to extract IBAN from the full text
            iban_match = re.search(r"IBAN\s+(DE[0-9\s]{20,30})", full_text)
            account_iban = None
            if iban_match:
                raw_iban = iban_match.group(1)
                account_iban = re.sub(r"\s+", "", raw_iban)
                if len(account_iban) != 22:
                    self.logger.warning(f"Found IBAN but length != 22: {account_iban}")

            # Parse page by page
            for page in pdf.pages:
                lines = page.extract_text().splitlines()
                i = 0
                while i < len(lines):
                    line = lines[i].strip()
                    booking_match = self.booking_line_pattern.match(line)

                    if booking_match:
                        # Group(1) => date (buchung_date_str)
                        # Group(2) => text until amount (rest_of_line)
                        # Group(3) => amount_str
                        # Group(4) => leftover_after_amount
                        buchung_date_str = booking_match.group(1)
                        rest_of_line = booking_match.group(2).strip()
                        amount_str = booking_match.group(3).replace(".", "").replace(",", ".")
                        leftover_after_amount = booking_match.group(4) or ""

                        # -------------- DETECT transaction.type --------------
                        transaction_type = None
                        type_match = self.type_pattern.search(rest_of_line)
                        if type_match:
                            # e.g. "Lastschrift" or "Gutschrift"
                            transaction_type = type_match.group(1).title()
                            # Remove that word from the partner name
                            rest_of_line = re.sub(self.type_pattern, "", rest_of_line, count=1).strip()

                        # -------------- DETECT "VISA" only --------------
                        transaction_medium = None
                        visa_match = self.visa_pattern.search(rest_of_line)
                        if visa_match:
                            transaction_medium = "Visa"
                            # Everything AFTER "VISA" becomes partner name
                            partner_name = rest_of_line[visa_match.end():].strip()
                        else:
                            # If no "VISA" found, the entire rest_of_line is the partner name
                            partner_name = rest_of_line

                        # Create the Transaction object
                        transaction = Transaction(
                            logger=self.logger,
                            source=self.source
                        )
                        # Set the owner (ING)
                        transaction.owner = OwnerAccount(
                            logger=self.logger,
                            id=account_iban,
                            institute="ING"
                        )
                        # Create an empty Invoice
                        transaction.invoice = Invoice()

                        # Parse the booking date
                        transaction.setTransactionDate(buchung_date_str)

                        # Convert the amount
                        try:
                            transaction.value = float(amount_str)
                        except ValueError as e:
                            self.logger.error(
                                f"Error converting amount '{amount_str}' in line '{line}' in file {self.source}: {e}"
                            )
                            i += 1
                            continue

                        # Basic fields
                        transaction.currency = "EUR"
                        transaction.type = transaction_type   # e.g. "Lastschrift"
                        transaction.medium = transaction_medium  # e.g. "Visa"
                        transaction.partner.name = partner_name  # e.g. "ESTACION DE SERVICIOS"

                        # Start the description with leftover_after_amount
                        transaction.description = leftover_after_amount.strip()

                        # Decide sender/receiver based on sign
                        if transaction.value < 0:
                            transaction.setSender(transaction.owner)
                            transaction.setReceiver(transaction.partner)
                        else:
                            transaction.setSender(transaction.partner)
                            transaction.setReceiver(transaction.owner)

                        # Check next line for Valuta date
                        j = i + 1
                        if j < len(lines):
                            next_line = lines[j].strip()
                            valuta_match = self.valuta_line_pattern.match(next_line)
                            if valuta_match:
                                # If there's a Valuta date
                                valuta_date_str = valuta_match.group(1)
                                transaction.setValutaDate(valuta_date_str)

                                leftover_text = valuta_match.group(2)
                                if leftover_text:
                                    if transaction.description:
                                        transaction.description += " "
                                    transaction.description += leftover_text.strip()
                                j += 1

                        # Parse additional lines for ID, Mandat, Referenz, leftover desc
                        while j < len(lines):
                            sub_line = lines[j].strip()

                            # If new booking line or new Valuta line => break
                            if self.booking_line_pattern.match(sub_line):
                                break
                            if self.valuta_line_pattern.match(sub_line):
                                break

                            tokens = sub_line.split(maxsplit=1)
                            # If the first token looks like an ID (ARN..., 1024..., NR...)
                            if len(tokens[0]) > 5 and tokens[0].startswith(("ARN", "1024", "NR")):
                                transaction.id = tokens[0]
                                if len(tokens) > 1:
                                    if transaction.description:
                                        transaction.description += " "
                                    transaction.description += tokens[1]
                            else:
                                # If Mandat: or Referenz:
                                mandat_match = self.mandat_pattern.match(sub_line)
                                if mandat_match:
                                    transaction.invoice.mandate_reference = mandat_match.group(1)
                                else:
                                    referenz_match = self.referenz_pattern.match(sub_line)
                                    if referenz_match:
                                        transaction.invoice.customer_reference = referenz_match.group(1)
                                    else:
                                        # Append to description
                                        if transaction.description:
                                            transaction.description += " "
                                        transaction.description += sub_line
                            j += 1

                        if not transaction.id:
                            transaction.id = ""

                        transaction.setTransactionId()
                        self.transactions.append(transaction)
                        i = j
                    else:
                        i += 1

        return self.transactions
