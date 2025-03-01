import hashlib
import base64

class Transaction:
    """Represents a single transaction."""
    def __init__(self, date, description, amount, sender, receiver, account, file_path, bank, currency="", invoice=""):
        self.description = description
        self.amount = amount
        self.sender = sender
        self.receiver = receiver
        self.account = account  # Neues Feld für das Konto
        self.file_path = file_path
        self.bank = bank
        self.currency = currency
        self.invoice = invoice
        self._set_date(date)
        self.id = self.generate_id()

    def generate_id(self):
        digest = hashlib.sha256(f"{self.date}_{self.description}_{self.amount}_{self.sender}_{self.receiver}_{self.file_path}_{self.bank}_{self.currency}_{self.invoice}_{self.account}".encode()).digest()
        hash_base32 = base64.b32encode(digest).decode('utf-8').rstrip('=')
        prefix = "TI01"
        fixed_length = 14
        return prefix + hash_base32[:fixed_length]

    def to_list(self):
        return [self.date, self.description, self.amount, self.sender, self.receiver, self.account, self.file_path, self.bank, self.id]

    def _set_date(self,date):
        if date:
            self.date = date
        else:
            raise Exception(f"Date is not defined.")
        
    def __str__(self):
        return (
            f"Transaction(ID: {self.id}, Date: {self.date}, Description: {self.description}, "
            f"Amount: {self.amount}, Sender: {self.sender}, Receiver: {self.receiver}, Account: {self.account}, "
            f"Currency: {self.currency}, Invoice: {self.invoice}, File Path: {self.file_path}, Bank: {self.bank})"
        )

