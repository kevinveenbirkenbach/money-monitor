import hashlib
import base64
from ..logger import Logger
from datetime import datetime
from code.model.account import Account, OwnerAccount
from .invoice import Invoice
from datetime import date, datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


class Transaction:
    """Represents a single transaction."""
    def __init__(self, 
                 logger:Logger, 
                 source:str, 
                 partner:Account=None, 
                 owner:Account = None, 
                 invoice: Invoice = None,
                 date: date = None,
                 related_transaction: str = None
                 ):
        self.logger                 = logger
        self.description            = ""                                # Optional
        self.value                  = None                              # Needs to be defined type integer
        self.owner                  = owner                             # Owner of this transaction
        self.partner                = partner or Account(self.logger)   # Optional: The transaction partner
        self.source                 = source                            # Obligatoric: File in which the transaction was found
        self.currency               = None                              # Obligatoric    
        self.invoice                = invoice or Invoice(self.logger)   # Optional: The linked invoice
        self.date                   = date                              # Obligatoric: The date when the transaction was done
        self.id                     = None                              # Obligatoric: The unique identifier of the transaction
        self.related_transaction_id = None                              # Optional: ID of the related transaction
        self.valuta_date            = None                              # Optional: Date when the booking was ordered
        self.type                   = None
        self.medium                 = None
        

    def setValutaDate(self, date_string):
        """
        Similar to setTransactionDate, but for Valuta (value date).
        """
        date_string = date_string.strip().replace('"', '')
        for fmt in ("%d.%m.%Y", "%d.%m.%y"):
            try:
                parsed_date = datetime.strptime(date_string, fmt).date()
                self.valuta_date = parsed_date
                return
            except ValueError:
                continue
        self.logger.error(f"Invalid valuta date format '{date_string}' in file {self.source}.")

    def setTransactionDate(self, date_string):
        # Remove extra whitespace and quotes
        date_string = date_string.strip().replace('"', '')

        # Attempt parsing with multiple date formats
        for fmt in ("%d.%m.%Y", "%d.%m.%y"):
            try:
                # Parse the string into a datetime, then convert to a date object
                parsed_date = datetime.strptime(date_string, fmt).date()
                self.date = parsed_date
                return
            except ValueError:
                continue

        # If parsing failed for all formats, log an error
        self.logger.error(f"Invalid date format '{date_string}' in file {self.source}.")

    def addTime(self, time_string: str, tz_string: str):
        """
        Adds a time component and a time zone to self.date (currently a date object).
        The resulting self.date will be a timezone-aware datetime object.
    
        :param time_string: Time in the format "HH:MM" or "HH:MM:SS" (e.g., "21:30" or "21:30:04").
        :param tz_string:   A valid IANA time zone string (e.g., "Europe/Berlin", "UTC").
        """
        try:
            parsed_time = None
    
            # Try multiple time formats
            for fmt in ("%H:%M:%S", "%H:%M"):
                try:
                    parsed_time = datetime.strptime(time_string, fmt).time()
                    break
                except ValueError:
                    pass
                
            if parsed_time is None:
                # Neither format matched the time_string
                raise ValueError(f"Time string '{time_string}' did not match '%H:%M' or '%H:%M:%S'")
    
            # 1. Combine the existing date (self.date) with the parsed time to create a naive datetime.
            combined_dt = datetime.combine(self.date, parsed_time)
    
            # 2. Attach the specified time zone to the datetime.
            combined_dt = combined_dt.replace(tzinfo=ZoneInfo(tz_string))
    
            # 3. Store the resulting timezone-aware datetime in self.date.
            self.date = combined_dt
    
        except ValueError as e:
            # This error occurs if time_string does not match "%H:%M" or "%H:%M:%S"
            self.logger.error(f"Invalid time format '{time_string}' in file {self.source}: {e}")
        except ZoneInfoNotFoundError:
            # This error occurs if tz_string is not a valid time zone (e.g., "Europe/Invalid")
            self.logger.error(f"Invalid time zone '{tz_string}' in file {self.source}.")


    

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
            self.owner = receiver

    def setSender(self, sender:Account):
        if self.value > 0:
            self.partner = sender
        else:
            self.owner = sender
    
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
            "value":        float,          # value needs to be of type int
            "owner":        OwnerAccount,   # Owner account
            "partner":      Account,        # The partner account
            "source":       str,            # source should be a string (file path)
            "currency":     str,            # currency should be a string (e.g., 'EUR', 'USD')
            "date":         date,           # date can be either a string (date)
            "id":           str,            # id can be either a string
            "description":  str,            # description should be a string (optional)
            "invoice":      Invoice,        
        }
        
        for var_name, expected_type in validations.items():
            var_value = getattr(self, var_name, None)  # Get the value of the attribute dynamically
            if not isinstance(var_value, expected_type):
                self.logger.error(f"{var_name} should be of type {expected_type.__name__}\n Type <<{type(var_value)}>> isn't correct.")
                return False         
        return self.owner.isValid() and self.partner.isValid() and self.invoice.isValid()
    

    def _get_time_with_tz(self)->str:
        """
        Returns a string in the format HH:MM±HH:MM based on self.date.

        - Example output: "14:30+01:00" or "09:15-05:00"
        - Only works if self.date is a datetime object with a valid tzinfo.
        """
        if not isinstance(self.date, datetime):
            return None

        if self.date.tzinfo is None:
            return None

        # Extract just the time (HH:MM)
        time_str = self.date.strftime("%H:%M")

        # Extract the offset in the form +HHMM or -HHMM (e.g., +0100, -0500)
        offset_str = self.date.strftime("%z")

        # If offset_str is empty or not the expected length, handle it
        if len(offset_str) != 5:
            return f"{time_str} (Invalid or missing offset: '{offset_str}')"

        # Reformat +0100 / -0500 to +01:00 / -05:00
        offset_str = offset_str[:3] + ":" + offset_str[3:]

        return f"{time_str}{offset_str}"


    def getDictionary(self)-> dict:
        dictionary = {
            "id":                       self.id,
            "date":                     self.date.strftime("%Y-%m-%d"),
            "value":                    self.value,
            "currency":                 self.currency,
            "sender":                   self.getSender() and self.getSender().getIdentity(),
            "receiver":                 self.getReceiver() and self.getReceiver().getIdentity(),
            "description":              self.description,
            "valuta_date":              self.valuta_date and self.valuta_date.strftime("%Y-%m-%d") or self.date.strftime("%Y-%m-%d"),
            "source":                   self.source,
            "time":                     self._get_time_with_tz(),
            "medium":                   self.medium,
            "type":                     self.type,
            "related_transaction_id":   self.related_transaction_id,
        }
        for key, value in self.partner.getDictionary().items():
            dictionary["partner_" + key]  = value        
        
        for key, value in self.owner.getDictionary().items():
            dictionary["owner_" + key]  = value
        
        for key, value in self.invoice.getDictionary().items():
            dictionary["invoice_" + key]  = value
        
        return dictionary

    def __str__(self)->str:
        output = ""
        data = self.__dict__
        for key, value in data.items():
            value_str = value if value is not None else "N/A"
            output += f"{key.replace('_', ' ').title()}: {value_str} \n"
        return output
