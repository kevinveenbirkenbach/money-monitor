import csv
from datetime import datetime
from zoneinfo import ZoneInfo
from code.model.transaction import Transaction
from code.model.log import Log
from ..abstract import AbstractCSVExtractor
from code.model.account import Account, OwnerAccount

class PaypalCSVExtractor(AbstractCSVExtractor):
    def getConfigurationElement(self,identifiers:[str]):
        filtered = self.configuration.configuration_file_data
        for element in identifiers:
            self.log.debug(f"Getting element '{element}'.")
            filtered = filtered.get(element)
            self.log.debug(f"Filtered '{element}'.")
        return filtered
    
    def extract_transactions(self):
        with open(self.source, newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f, delimiter=',')
            headers = reader.fieldnames
            for row in reader:
                transaction = Transaction(self.log, self.source)
                transaction.owner = OwnerAccount(self.log)
                transaction.owner.id = self.getConfigurationElement(["institutes","paypal","owner","id"])
                transaction.owner.name = self.getConfigurationElement(["institutes","paypal","owner","name"])
                transaction.owner.institute = "Paypal"

                # -------------------------
                # 1) Parse Date, Time, TZ
                # -------------------------
                # Extract strings for date, time, and time zone
                date_str = row.get("Datum", "").strip()
                time_str = row.get("Uhrzeit", "").strip()
                tz_str   = row.get("Zeitzone", "").strip()
                transaction.setTransactionDate(date_str)
                transaction.addTime(time_str, tz_str)

                # --------------------------------------
                # 2) Parse Partner (Sender) Information
                # --------------------------------------
                transaction.partner.id          = row.get("Absender E-Mail-Adresse", "").strip()
                transaction.partner.name        = row.get("Name", "").strip()
                transaction.partner.institute   = row.get("Name der Bank", "").strip() or "Paypal"


                # -------------------------------
                # 3) Transaction Metadata
                # -------------------------------
                transaction.id                      = row.get("Transaktionscode", "").strip()
                transaction.description             = row.get("Beschreibung", "").strip()
                transaction.currency                = row.get("Währung", "").strip()
                transaction.related_transaction_id  = row.get("Zugehöriger Transaktionscode", "").strip()

                # Convert 'Netto' to float
                net_str = row.get("Netto", "").strip().replace(",", ".")
                try:
                    transaction.setValue(net_str)
                except ValueError:
                    self.log.error(f"Error parsing net amount '{net_str}' in {self.source}")
                    transaction.setValue(0.0)

                # Optional invoice number
                # transaction.invoice is an Invoice object; store the "Rechnungsnummer" in its id
                if "Rechnungsnummer" in row:
                    transaction.invoice.id = row["Rechnungsnummer"].strip()
                else:
                    transaction.invoice.id = ""

                # Set additional metadata
                transaction.source             = self.source
                transaction.finance_institute  = "PayPal"

                # -------------------------
                # 4) Append Transaction
                # -------------------------
                self.appendTransaction(transaction)

        return self.transactions
