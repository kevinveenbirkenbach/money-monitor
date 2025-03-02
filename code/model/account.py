class Account:
    def __init__(self, id=None, name=None, institute=None):
        self.id = id                # ID of the account like IBAN
        self.name = name            # Owner of the Account like Max Mustermann
        self.institute = institute  # The institute the account belongs to  

    # Verifies if accout is valid
    def isValid(self):
        return bool(self.id or self.name or self.institute)
    
    def getDictionary(self)-> dict:
        return {
            "id":           self.id,
            "name":         self.name,
            "institute":    self.institute,
        }
        
    def getIdentification(self)-> str:
        return str(str(self.id) + str(self.name) + str(self.institute))[:18]
    
class OwnerAccount(Account):
    # Verifies if accout is valid
    def isValid(self):
        return bool(
            (self.id or self.name) 
            and self.institute
            )
    