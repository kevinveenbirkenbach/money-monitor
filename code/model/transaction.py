import hashlib
import base64
from ..logger import Logger
from datetime import datetime
from code.model.account import Account

class Transaction:
    """Represents a single transaction."""
    def __init__(self, logger:Logger, source_document:str, partner:Account=None, owner:Account = None):
        self.logger             = logger
        self.description        = ""                                # Optional
        self.value              = None                              # Needs to be defined type integer
        self.owner              = owner                             # Owner of this transaction
        self.partner            = partner or Account(self.logger)   # Optional: The transaction partner
        self.source_document    = source_document                   # Obligatoric: File in which the transaction was found
        self.currency           = None                              # Obligatoric    
        self.invoice_id         = ""                                # Optional: The invoice number   
        self.date               = None                              # Obligatoric: The date when the transaction was done
        self.id                 = None                              # Obligatoric: The unique identifier of the transaction
        
    def setTransactionDate(self,date_string):
        date_string = date_string.strip().replace('"', '')
        for fmt in ("%d.%m.%Y", "%d.%m.%y"):
            try:
                self.date = datetime.strptime(date_string, fmt).strftime("%Y-%m-%d")
                return
            except ValueError:
                continue
        self.logger.error(f"Invalid date format '{date_string}' in file {self.source_document}.")

    def setTransactionId(self):
        if not self.id:
            digest = hashlib.sha256(self.__str__().encode()).digest()
            hash_base32 = base64.b32encode(digest).decode('utf-8').rstrip('=')
            fixed_length = 15
            self.id = "TID" + hash_base32[:fixed_length]
    
    def setReceiver(self, receiver:Account):
        if self.value < 0:
            self.partner = receiver
        else:
            self.account_name = receiver

    def setSender(self, sender:Account):
        if self.value > 0:
            self.partner = sender
        else:
            self.account_name = sender
    
    def getReceiver(self)-> Account:
        if self.value < 0:
            if self.partner:
                return self.partner
        if self.value > 0:
            return self.owner
        return None;
    
    def getSender(self)-> Account:
        if self.value > 0:
            if self.partner:
                return self.partner
        if self.value < 0:
            return self.owner
        return None;
    
    def isValid(self):
        # Dictionary with variable names as keys and expected types as values
        validations = {
            "value":                float,      # value needs to be of type int
            "owner":                Account,    # Owner account
            "partner":              Account,    # The partner account
            "source_document":      str,        # source_document should be a string (file path)
            "currency":             str,        # currency should be a string (e.g., 'EUR', 'USD')
            "date":                 str,        # date can be either a string (date)
            "id":                   str,        # id can be either a string
            "description":          str,        # description should be a string (optional)
            "invoice_id":           str,        # invoice should be a string (optional)
        }
        
        for var_name, expected_type in validations.items():
            var_value = getattr(self, var_name, None)  # Get the value of the attribute dynamically
            if not isinstance(var_value, expected_type):
                self.logger.error(f"{var_name} should be of type {expected_type.__name__}\n Type <<{type(var_value)}>> isn't correct.")
                return False         
        return self.owner.isValid(), self.partner.isValid()

    def getDictionary(self)-> dict:
        dictionary = {
            "id":              self.id,
            "date":            self.date,
            "currency":        self.currency,
            "value":           self.value,
            "sender":          self.getSender() and self.getSender().getIdentity(),
            "receiver":        self.getReceiver() and self.getReceiver().getIdentity(),
            "description":     self.description,
            "source_document": self.source_document,
            "invoice_id":      self.invoice_id,
        }
        for key, value in self.partner.getDictionary().items():
            dictionary["partner_" + key]  = value        
        
        for key, value in self.owner.getDictionary().items():
            dictionary["owner_" + key]  = value
        
        return dictionary

    def __str__(self):
        output = ""
        data = self.getDictionary()
        for key, value in data.items():
            value_str = value if value is not None else "N/A"
            output += f"{key.replace('_', ' ').title()}: {value_str} \n"
        return output
