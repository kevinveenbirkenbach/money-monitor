from code.logger import Logger

class Account:
    def __init__(self, logger:Logger, id=None, name=None, institute=None):
        self.logger = logger        # Logger class
        self.id = id                # ID of the account like IBAN
        self.name = name            # Owner of the Account like Max Mustermann
        self.institute = institute  # The institute the account belongs to  

    # Verifies if accout is valid
    def isValid(self)->bool:
        if bool(self.id or self.name or self.institute):
            return True
        else:
            self.logger.warning("Account isn't valid.")
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
        self.logger.warning("Account doesn't have an identity.")
        return ""
    
class OwnerAccount(Account):
    # Verifies if accout is valid
    def isValid(self)->bool:
        if bool((self.id or self.name) and self.institute):
            return True
        else: 
            self.logger.warning("OwnerAccount isn't valid.")
            return False
                
    