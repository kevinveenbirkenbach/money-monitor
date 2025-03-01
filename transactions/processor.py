import os
import concurrent.futures
from .extractor import PDFTransactionExtractor
from .exporter import CSVExporter

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
