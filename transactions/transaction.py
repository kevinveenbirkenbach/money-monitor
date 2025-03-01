import hashlib
import base64
from .logger import Logger
from datetime import datetime

class Transaction:
    """Represents a single transaction."""
    def __init__(self, logger:Logger, transaction_source_document:str):
        self.logger                         = logger
        self.description                    = ""                            # Optional
        self.value                          = None                          # Needs to be defined type integer
        self.transaction_partner            = None                          # Optional: The transaction partner
        self.account_id                     = None                          # Obligatoric: IBAN, Paypal address
        self.transaction_source_document    = transaction_source_document   # Obligatoric: File in which the transaction was found
        self.finance_institute              = None                          # The finance institute which served the transaction
        self.currency                       = None                          # Obligatoric    
        self.invoice                        = ""                            # Optional: The invoice number   
        self.transaction_date               = None                          # Obligatoric: The date when the transaction was done
        self.transaction_id                 = None                          # Obligatoric: The unique identifier of the transaction
        
    def setTransactionDate(self,date_string):
        date_string = date_string.strip().replace('"', '')
        for fmt in ("%d.%m.%Y", "%d.%m.%y"):
            try:
                self.transaction_date = datetime.strptime(date_string, fmt).strftime("%Y-%m-%d")
                return
            except ValueError:
                continue
        self.logger.error(f"Invalid date format '{date_string}' in file {self.transaction_source_document}.")

    def setTransactionId(self):
        if not self.transaction_id:
            digest = hashlib.sha256(self.__str__().encode()).digest()
            hash_base32 = base64.b32encode(digest).decode('utf-8').rstrip('=')
            fixed_length = 18
            self.transaction_id = hash_base32[:fixed_length]
    
    def getReceiver(self):
        if self.value < 0:
            if self.transaction_partner:
                return self.transaction_partner
        if self.value > 0:
            return self.account_id
        return "";
    
    def getSender(self):
        if self.value > 0:
            if self.transaction_partner:
                return self.transaction_partner
        if self.value < 0:
            return self.account_id
        return "";
    
    def isValid(self):
        # Dictionary with variable names as keys and expected types as values
        validations = {
            "value":                        float,  # value needs to be of type int
            "account_id":                   str,    # account_id can be either a string (IBAN, Paypal address)
            "transaction_source_document":  str,    # transaction_source_document should be a string (file path)
            "finance_institute":            str,    # finance_institute can be either a string
            "currency":                     str,    # currency should be a string (e.g., 'EUR', 'USD')
            "transaction_date":             str,    # transaction_date can be either a string (date)
            "transaction_id":               str,    # id can be either a string
            "description":                  str,    # description should be a string (optional)
            "invoice":                      str,    # invoice should be a string (optional)
        }
        
        for var_name, expected_type in validations.items():
            var_value = getattr(self, var_name, None)  # Get the value of the attribute dynamically
            if not isinstance(var_value, expected_type):
                self.logger.error(f"{var_name} should be of type {expected_type.__name__}\n Type <<{type(var_value)}>> isn't correct.")
                return False         
        return True

    def getDictionary(self):
        return {
            "transaction_id":               self.transaction_id,
            "finance_institute":            self.finance_institute,
            "account_id":                   self.account_id,
            "transaction_date":             self.transaction_date,
            "value":                        self.value,
            "currency":                     self.currency,
            "sender":                       self.getSender(),
            "receiver":                     self.getReceiver(),
            "description":                  self.description,
            "transaction_partner":          self.transaction_partner,
            "transaction_source_document":  self.transaction_source_document,
            "invoice":                      self.invoice,
            
        }

    def __str__(self):
        output = ""
        data = self.getDictionary()
        for key, value in data.items():
            value_str = value if value is not None else "N/A"
            output += f"{key.replace('_', ' ').title()}: {value_str} \n"
        return output
