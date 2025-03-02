class Account:
    def __init__(self):
        self.id     = None  # ID of the account like IBAN
        self.owner  = None  # Owner of the Account like Max Mustermann
    # Verifies if accout is valid
    def isValid(self):
        return (self.id or self.owner)