from datetime import datetime
from code.model.transaction import Transaction
from code.model.invoice import Invoice
from code.model.account import OwnerAccount, Account

class ConsorsbankTransactionBuilder:
    def __init__(self, logger, source, account_iban, default_year):
        self.logger = logger
        self.source = source
        self.account_iban = account_iban
        self.default_year = default_year  # Default year to append to dates like "01.11."
        
    def _parse_date(self, date_str: str) -> str:
        """
        Append the default year to a date string if the year is missing.
        Example: "01.11." -> "01.11.<default_year>"
        """
        if date_str.endswith('.'):
            date_str = date_str + str(self.default_year)
        return date_str
        
    def build_transaction(self, transaction_type: str, booking_data: dict, additional_infos: list = []):
        """
        Build and configure a Transaction object from the parsed data.
        :param transaction_type: The type indicator (e.g., "LASTSCHRIFT" or "GUTSCHRIFT")
        :param booking_data: Parsed booking line data.
        :param additional_infos: List of dictionaries from additional lines.
        """
        transaction = Transaction(logger=self.logger, source=self.source)
        # Set the account owner with Consorsbank-specific institute information.
        transaction.owner = OwnerAccount(
            logger=self.logger,
            id=self.account_iban,
            institute="Consorsbank"
        )
        transaction.invoice = Invoice()
        
        # Process booking and valuta dates by appending the default year.
        booking_date_str = self._parse_date(booking_data["booking_date_str"])
        valuta_date_str = self._parse_date(booking_data["valuta_date_str"])
        
        transaction.setTransactionDate(booking_date_str)
        transaction.setValutaDate(valuta_date_str)
        
        # Process the amount string: handle trailing '-' or '+'.
        amount_str = booking_data["amount_str"].strip()
        if amount_str.endswith('-'):
            amount_str = '-' + amount_str[:-1]
        elif amount_str.endswith('+'):
            amount_str = amount_str[:-1]
        # Check for comma as the decimal separator and remove thousand separators.
        if "," in amount_str:
            amount_str = amount_str.replace(".", "").replace(",", ".")
        try:
            transaction.value = float(amount_str)
        except ValueError as e:
            self.logger.error(
                f"Error converting amount '{booking_data['amount_str']}' in source {self.source}: {e}"
            )
            return None
        
        transaction.currency = "EUR"
        # Set the transaction type (e.g., Lastschrift/Gutschrift) based on the provided type indicator.
        transaction.type = transaction_type.title()  # "Lastschrift" or "Gutschrift"
        
        # Process additional info lines for medium, partner institute, and extra description.
        for info in additional_infos:
            if "medium" in info:
                transaction.medium = info["medium"]
            if "partner_institute" in info:
                transaction.partner.institute = info["partner_institute"]
            if "description" in info:
                if transaction.description:
                    transaction.description += " "
                transaction.description += info["description"]
        
        # If no partner name is set from additional info, use any description from the booking data.
        if not transaction.partner.name:
            transaction.partner.name = booking_data.get("description", "")
        
        if not transaction.id:
            transaction.id = ""
        transaction.setTransactionId()
        
        # Determine sender and receiver based on the sign of the amount.
        if transaction.value < 0:
            transaction.setSender(transaction.owner)
            transaction.setReceiver(transaction.partner)
        else:
            transaction.setSender(transaction.partner)
            transaction.setReceiver(transaction.owner)
        
        return transaction
