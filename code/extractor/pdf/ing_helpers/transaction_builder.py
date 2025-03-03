from datetime import datetime
from code.model.transaction import Transaction
from code.model.invoice import Invoice
from code.model.account import OwnerAccount

class TransactionBuilder:
    def __init__(self, logger, source, account_iban):
        self.logger = logger
        self.source = source
        self.account_iban = account_iban

    def build_transaction(self, booking_data: dict, valuta_data: dict = None, additional_infos: list = []):
        """Erstellt und konfiguriert ein Transaction-Objekt anhand der übergebenen Daten."""
        transaction = Transaction(logger=self.logger, source=self.source)
        # Setze den Kontoinhaber (ING)
        transaction.owner = OwnerAccount(
            logger=self.logger,
            id=self.account_iban,
            institute="ING"
        )
        # Erstelle eine leere Rechnung
        transaction.invoice = Invoice()

        # Setze das Buchungsdatum
        transaction.setTransactionDate(booking_data["buchung_date_str"])

        # Betrag konvertieren
        try:
            transaction.value = float(booking_data["amount_str"])
        except ValueError as e:
            self.logger.error(
                f"Error converting amount '{booking_data['amount_str']}' in source {self.source}: {e}"
            )
            return None

        # Grundfelder setzen
        transaction.currency = "EUR"
        transaction.type = booking_data["transaction_type"]
        transaction.medium = booking_data["transaction_medium"]
        transaction.partner.name = booking_data["partner_name"]
        transaction.description = booking_data["leftover_after_amount"].strip()

        # Falls vorhanden, Valuta-Datum und weiteren Text hinzufügen
        if valuta_data:
            transaction.setValutaDate(valuta_data["valuta_date_str"])
            leftover_text = valuta_data.get("leftover_text")
            if leftover_text:
                if transaction.description:
                    transaction.description += " "
                transaction.description += leftover_text.strip()

        # Zusätzliche Informationen parsen
        for info in additional_infos:
            # Verarbeite mehrere Keys aus demselben Dictionary
            if "id" in info:
                transaction.id = info["id"]
            if "partner_institute" in info:
                transaction.partner.institute = info["partner_institute"]
            if "description" in info:
                if transaction.description:
                    transaction.description += " "
                transaction.description += info["description"]
            if "mandate_reference" in info:
                transaction.invoice.mandate_reference = info["mandate_reference"]
            if "customer_reference" in info:
                transaction.invoice.customer_reference = info["customer_reference"]


        if not transaction.id:
            transaction.id = ""
        transaction.setTransactionId()

        # Abhängig vom Vorzeichen die Sender/Receiver setzen
        if transaction.value < 0:
            transaction.setSender(transaction.owner)
            transaction.setReceiver(transaction.partner)
        else:
            transaction.setSender(transaction.partner)
            transaction.setReceiver(transaction.owner)

        return transaction
