from code.model.log import Log

class Account:
    def __init__(self, log:Log, id=None, name=None, institute=None):
        self.log = log        # Log class
        self.id = id                # ID of the account like IBAN
        self.name = name            # Owner of the Account like Max Mustermann
        self.institute = institute  # The institute the account belongs to  

    def isValid(self)->bool:
        if bool(self.id or self.name or self.institute):
            return True
        else:
            self.log.warning(f"Account with ID {self.id} isn't valid.")
            return False
    
    def getDictionary(self)-> dict:
        return {
            "id":           self.id,
            "name":         self.name,
            "institute":    self.institute,
        }
    
    def getIdentity(self)-> str:
        if self.id:
            return self.id
        if self.name:
            return self.name
        if self.institute:
            return self.institute
        self.log.warning(f"Account with ID {self.id} doesn't have a valid identity.")
        return ""
    
class OwnerAccount(Account):
    # Verifies if accout is valid
    def isValid(self)->bool:
        if bool((self.id or self.name) and self.institute):
            return True
        else: 
            self.log.warning("OwnerAccount isn't valid.")
            return False
                
    