from datetime import datetime
from code.model.transaction import Transaction
from code.model.invoice import Invoice
from code.model.account import OwnerAccount, Account

class BarclaysTransactionBuilder:
    def __init__(self, logger, source, account_iban):
        self.logger = logger
        self.source = source
        self.account_iban = account_iban
        
    def build_transaction(self, booking_data: dict, additional_infos: list = []):
        """
        Erstellt und konfiguriert ein Transaction-Objekt anhand der übergebenen Daten.
        """
        transaction = Transaction(logger=self.logger, source=self.source)
        # Setze den Kontoinhaber (Owner) mit der extrahierten IBAN
        transaction.owner = OwnerAccount(
            logger=self.logger,
            id=self.account_iban,
            institute="Barclays"
        )
        # Erstelle eine leere Rechnung
        transaction.invoice = Invoice()
        
        # Setze das Transaktionsdatum (Buchungsdatum)
        transaction.setTransactionDate(booking_data["booking_date_str"])
        # Setze das Valutadatum
        transaction.setValutaDate(booking_data["valuta_date_str"])
        
        # Betrag-String bereinigen
        amount_str = booking_data["amount_str"].strip()
        if amount_str.endswith('-'):
            amount_str = '-' + amount_str[:-1]
        elif amount_str.endswith('+'):
            amount_str = amount_str[:-1]
        amount_str = amount_str.replace(".", "").replace(",", ".")
        try:
            transaction.value = float(amount_str)
        except ValueError as e:
            self.logger.error(
                f"Error converting amount '{booking_data['amount_str']}' in source {self.source}: {e}"
            )
            return None        
        
        transaction.currency = "EUR"
        # Typ (Lastschrift/Gutschrift) anhand des Vorzeichens bestimmen
        transaction.type = "Lastschrift" if transaction.value < 0 else "Gutschrift"
        
        # Setze das Medium, falls Card-Informationen vorhanden sind
        transaction.medium = "Visa" if booking_data.get("card_country") else None
        
        # Setze den Partnernamen aus der Beschreibung
        transaction.partner.name = booking_data["description"]
        
        # Verarbeite zusätzliche Informationen
        for info in additional_infos:
            if "mandate_reference" in info:
                transaction.invoice.mandate_reference = info["mandate_reference"]
            if "creditor_id" in info:
                transaction.invoice.creditor_id = info["creditor_id"]
            if "extra_description" in info:
                if transaction.description:
                    transaction.description += " "
                transaction.description += info["extra_description"]
        
        if not transaction.id:
            transaction.id = ""
        transaction.setTransactionId()
        
        # Setze Sender und Empfänger basierend auf dem Betrag
        if transaction.value < 0:
            transaction.setSender(transaction.owner)
            transaction.setReceiver(transaction.partner)
        else:
            transaction.setSender(transaction.partner)
            transaction.setReceiver(transaction.owner)
        
        return transaction
