class Invoice:
    def __init__(
        self,
        id: str = None,                 # Unique identifier for the invoice
        document: str = None,           # Path or location of the invoice document
        customer_reference: str = None, # Reference identifying the customer
        creditor_id: str = None,        # Creditor Identifier (Gläubiger-ID)
        mandate_reference: str = None   # Mandate Reference (Mandatsreferenz) for the direct debit
    ):
        self.id = id
        self.document = document
        self.customer_reference = customer_reference
        self.creditor_id = creditor_id
        self.mandate_reference = mandate_reference
        
    # Verifies if invoice is valid
    def isValid(self):
        return True
    
    def getDictionary(self):
        return self.__dict__.copy()
