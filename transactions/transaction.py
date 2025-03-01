import hashlib
import base64

class Transaction:
    """Repräsentiert eine einzelne Transaktion."""
    def __init__(self, date, description, amount, sender, file_path, bank, currency="", invoice="", to=""):
        self.date = date
        self.description = description
        self.amount = amount
        self.sender = sender
        self.file_path = file_path
        self.bank = bank
        self.currency = currency
        self.invoice = invoice
        self.to = to
        self.id = self.generate_id()

    def generate_id(self):
        digest = hashlib.sha256(f"{self.date}_{self.description}_{self.amount}_{self.sender}_{self.file_path}_{self.bank}_{self.currency}_{self.invoice}_{self.to}".encode()).digest()
        hash_base32 = base64.b32encode(digest).decode('utf-8').rstrip('=')
        prefix = "TI01"
        fixed_length = 14
        return prefix + hash_base32[:fixed_length]

    def to_list(self):
        return [self.date, self.description, self.amount, self.sender, self.currency, self.invoice, self.to, self.file_path, self.bank, self.id]
    
    def __str__(self):
        return (
            f"Transaction(ID: {self.id}, Date: {self.date}, Description: {self.description}, "
            f"Amount: {self.amount}, Sender: {self.sender}, Currency: {self.currency}, "
            f"Invoice: {self.invoice}, To: {self.to}, File Path: {self.file_path}, Bank: {self.bank})"
        )

