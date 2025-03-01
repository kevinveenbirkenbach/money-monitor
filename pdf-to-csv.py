import pdfplumber
import csv
import re
import os
import argparse
import hashlib
import concurrent.futures
from datetime import datetime

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

class PDFTransactionExtractor:
    """Extrahiert Transaktionen aus einem PDF-Bankauszug."""
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.transactions = []
        self.account = ""
        self.bank_type = "Unknown"

    def detect_bank_type(self, text):
        """Ermittelt den Banktyp anhand des Textinhalts."""
        if text is None:
            return "Unknown"
        if "ING-DiBa" in text or "IBAN" in text:
            return "ING"
        elif "Barclaycard" in text or "BARCDEHAXXX" in text:
            return "Barclays"
        return "Unknown"

    def extract_transactions(self):
        """Liest das PDF ein und extrahiert Transaktionen basierend auf dem Banktyp."""
        with pdfplumber.open(self.pdf_path) as pdf:
            if not pdf.pages:
                print(f"Warning: No pages found in {self.pdf_path}")
                return []

            first_page_text = pdf.pages[0].extract_text()
            self.bank_type = self.detect_bank_type(first_page_text)

            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue

                lines = text.split("\n")
                if self.bank_type == "ING":
                    iban_match = re.search(r"IBAN\s+(DE\d{2}\s\d{4}\s\d{4}\s\d{4}\s\d{2})", text)
                    if iban_match:
                        self.account = iban_match.group(1).replace(" ", "")

                    for line in lines:
                        match = re.match(r"(\d{2}\.\d{2}\.\d{4})\s+(.+?)\s+(-?\d{1,3}(?:\.\d{3})*(?:,\d{2})?)", line)
                        if match:
                            date = match.group(1)
                            description = match.group(2).strip()
                            amount = match.group(3).replace(".", "").replace(",", ".")
                            iso_date = datetime.strptime(date, "%d.%m.%Y").strftime("%Y-%m-%d")
                            transaction = Transaction(iso_date, description, float(amount), self.account, self.pdf_path)
                            self.transactions.append(transaction)

                elif self.bank_type == "Barclays":
                    iban_match = re.search(r"IBAN\s+(DE\d{2}\s\d{4}\s\d{4}\s\d{4}\s\d{2})", text)
                    if iban_match:
                        self.account = iban_match.group(1).replace(" ", "")

                    for line in lines:
                        match = re.match(r"(\d{2}\.\d{2}\.\d{4})\s+(.*?)\s+Visa\s+(-?\d{1,3}(?:\.\d{3})*(?:,\d{2})?)", line)
                        if match:
                            date = match.group(1)
                            description = match.group(2).strip()
                            amount = match.group(3).replace(".", "").replace(",", ".")
                            iso_date = datetime.strptime(date, "%d.%m.%Y").strftime("%Y-%m-%d")
                            transaction = Transaction(iso_date, description, float(amount), self.account, self.pdf_path)
                            self.transactions.append(transaction)

        return self.transactions

class CSVExporter:
    """Exportiert die extrahierten Transaktionen in eine CSV-Datei."""
    def __init__(self, transactions, output_file):
        self.transactions = transactions
        self.output_file = output_file

    def export(self):
        if not self.transactions:
            print("No transactions found to save.")
            return

        # Sortiere die Transaktionen nach Datum
        self.transactions.sort(key=lambda t: t.date)

        with open(self.output_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Date", "Description", "Amount (EUR)", "Account", "File Path", "Transaction Hash"])
            for transaction in self.transactions:
                writer.writerow(transaction.to_list())

        print(f"CSV file created: {self.output_file}")

class TransactionProcessor:
    """Koordiniert das Einlesen der PDFs und den Export der Transaktionen."""
    def __init__(self, input_path, output_csv):
        self.input_path = input_path
        self.output_csv = output_csv
        self.all_transactions = []

    def process(self):
        pdf_files = []
        if os.path.isdir(self.input_path):
            pdf_files = [os.path.join(self.input_path, file_name)
                         for file_name in os.listdir(self.input_path) if file_name.endswith(".pdf")]
        elif os.path.isfile(self.input_path) and self.input_path.endswith(".pdf"):
            pdf_files = [self.input_path]
        else:
            print("Invalid input path. Please provide a valid PDF file or directory.")
            return

        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(executor.map(self.extract_from_file, pdf_files))
            for transactions in results:
                self.all_transactions.extend(transactions)

        csv_exporter = CSVExporter(self.all_transactions, self.output_csv)
        csv_exporter.export()

    @staticmethod
    def extract_from_file(pdf_file):
        extractor = PDFTransactionExtractor(pdf_file)
        return extractor.extract_transactions()

def main():
    parser = argparse.ArgumentParser(
        description="Extract transactions from a bank statement PDF and save to CSV."
    )
    parser.add_argument("input_path", type=str, help="Path to the input PDF file or directory containing PDFs.")
    parser.add_argument("output_csv", type=str, help="Path to save the output CSV file.")
    args = parser.parse_args()

    processor = TransactionProcessor(args.input_path, args.output_csv)
    processor.process()

if __name__ == "__main__":
    main()
