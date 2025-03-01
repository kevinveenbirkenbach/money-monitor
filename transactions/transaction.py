import hashlib
import base64

class Transaction:
    """Repräsentiert eine einzelne Transaktion."""
    def __init__(self, date, description, amount, account, file_path, bank):
        self.date = date
        self.description = description
        self.amount = amount
        self.account = account
        self.file_path = file_path
        self.bank = bank
        self.id = self.generate_id()

    def generate_id(self):
        # Erzeuge den SHA256-Digest
        digest = hashlib.sha256(f"{self.date}_{self.description}_{self.amount}_{self.account}_{self.file_path}_{self.bank}".encode()).digest()
        # Base32-Codierung liefert nur Großbuchstaben und Ziffern. Entferne eventuelle Padding-Zeichen.
        hash_base32 = base64.b32encode(digest).decode('utf-8').rstrip('=')
        # Kürze oder padde auf feste Länge (hier z. B. 18 Zeichen)
        fixed_length = 18
        if len(hash_base32) >= fixed_length:
            return hash_base32[:fixed_length]
        else:
            return hash_base32.ljust(fixed_length, '0')

    def to_list(self):
        return [self.date, self.description, self.amount, self.account, self.file_path, self.bank, self.id]
