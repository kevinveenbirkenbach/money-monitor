class Account:
    def __init__(self):
        self.id         = None  # ID of the account like IBAN
        self.owner_name = None  # Owner of the Account like Max Mustermann
        self.institute  = None  # The institute the account belongs to   
    # Verifies if accout is valid
    def isValid(self):
        return bool(self.id or self.owner)
    