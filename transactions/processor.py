import os
import concurrent.futures
from pdfminer.high_level import extract_text
from .extractor import PDFTransactionExtractor
from .extractor_consorsbank import PDFConsorsbankExtractor
from .exporter import CSVExporter

class TransactionProcessor:
    """Koordiniert das Einlesen der PDFs aus mehreren Pfaden und den Export der Transaktionen."""
    def __init__(self, input_paths, output_csv, print_transactions=False, recursive=False):
        # input_paths ist eine Liste von Pfaden (Dateien oder Verzeichnisse)
        self.input_paths = input_paths
        self.output_csv = output_csv
        self.all_transactions = []
        self.print_transactions = print_transactions
        self.recursive = recursive

    def process(self):
        pdf_files = []
        # Iteriere über alle übergebenen Pfade
        for path in self.input_paths:
            if os.path.isdir(path):
                if self.recursive:
                    # Rekursive Suche mit os.walk
                    for root, _, files in os.walk(path):
                        for file_name in files:
                            if file_name.endswith(".pdf"):
                                pdf_files.append(os.path.join(root, file_name))
                else:
                    # Nur oberste Ebene durchsuchen
                    pdf_files.extend(
                        [os.path.join(path, file_name)
                         for file_name in os.listdir(path) if file_name.endswith(".pdf")]
                    )
            elif os.path.isfile(path) and path.endswith(".pdf"):
                pdf_files.append(path)
            else:
                print(f"Invalid input path: {path}")

        if not pdf_files:
            print("No PDF files found in the given paths.")
            return

        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(executor.map(self.extract_from_file, pdf_files))
            for transactions in results:
                self.all_transactions.extend(transactions)

        csv_exporter = CSVExporter(self.all_transactions, self.output_csv)
        csv_exporter.export()

        if self.print_transactions:
            self.cat_transactions()

    @staticmethod
    def extract_from_file(pdf_file):
        # Lese die erste Seite mit pdfminer, um den Typ zu ermitteln.
        try:
            text = extract_text(pdf_file, maxpages=1)
        except Exception:
            text = ""
        # Wenn typische Stichwörter für Consorsbank vorhanden sind, benutze den Consorsbank-Extractor.
        if "Consorsbank" in text or "KONTOAUSZUG" in text:
            extractor = PDFConsorsbankExtractor(pdf_file)
        else:
            extractor = PDFTransactionExtractor(pdf_file)
        return extractor.extract_transactions()

    def cat_transactions(self):
        """Gibt alle Transaktionen zeilenweise auf der Konsole aus."""
        print("\nAlle Transaktionen:")
        for t in self.all_transactions:
            print(f"{t.date}\t{t.description}\t{t.amount}\t{t.account}\t{t.file_path}\t{t.hash}")
