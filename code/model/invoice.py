class Invoice:
    def __init__(self):
        self.id         = None  # ID of the invoice
        self.document   = None  # Path to the document
    # Verifies if accout is valid
    def isValid(self):
        return bool(self.id or self.document)