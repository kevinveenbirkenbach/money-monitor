import hashlib

class Transaction:
    """Repräsentiert eine einzelne Transaktion."""
    def __init__(self, date, description, amount, account, file_path):
        self.date = date
        self.description = description
        self.amount = amount
        self.account = account
        self.file_path = file_path
        self.hash = self.generate_hash()

    def generate_hash(self):
        """Erstellt einen einzigartigen Hash für die Transaktion."""
        hash_input = f"{self.date}_{self.description}_{self.amount}_{self.account}_{self.file_path}"
        return hashlib.sha256(hash_input.encode()).hexdigest()

    def to_list(self):
        """Gibt die Transaktion als Listenrepräsentation zurück."""
        return [self.date, self.description, self.amount, self.account, self.file_path, self.hash]
