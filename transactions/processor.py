import os
import concurrent.futures
from pdfminer.high_level import extract_text
from .extractor import PDFTransactionExtractor
from .extractor_consorsbank import PDFConsorsbankExtractor

class TransactionProcessor:
    """Koordiniert das Einlesen der PDFs aus mehreren Pfaden und den Export der Transaktionen."""
    def __init__(self, input_paths, output_base, print_transactions=False, recursive=False, export_formats=None):
        # input_paths: Liste von Pfaden (Dateien oder Verzeichnisse)
        self.input_paths = input_paths
        self.output_base = output_base
        self.all_transactions = []
        self.print_transactions = print_transactions
        self.recursive = recursive
        # export_formats ist ein Dictionary z.B. {"csv": True, "html": False, ...}
        self.export_formats = export_formats or {}

    def process(self):
        pdf_files = []
        # Durchlaufe alle übergebenen Pfade
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

        # Exportiere in die angeforderten Formate
        for fmt, flag in self.export_formats.items():
            if flag:
                ext = f".{fmt}"
                output_file = self.output_base
                if not output_file.endswith(ext):
                    output_file += ext
                if fmt == "csv":
                    from .exporter import CSVExporter
                    exporter = CSVExporter(self.all_transactions, output_file)
                    exporter.export()
                elif fmt == "html":
                    from .exporter import HTMLExporter
                    exporter = HTMLExporter(self.all_transactions, output_file)
                    exporter.export()
                elif fmt == "json":
                    from .exporter import JSONExporter
                    exporter = JSONExporter(self.all_transactions, output_file)
                    exporter.export()
                elif fmt == "yaml":
                    from .exporter import YamlExporter
                    exporter = YamlExporter(self.all_transactions, output_file)
                    exporter.export()

        if self.print_transactions:
            self.console_output()

    @staticmethod
    def extract_from_file(pdf_file):
        # Lese die erste Seite mittels pdfminer, um den Typ zu ermitteln
        try:
            text = extract_text(pdf_file, maxpages=1)
        except Exception:
            text = ""
        # Bei typischen Stichwörtern für Consorsbank den entsprechenden Extractor verwenden
        if "Consorsbank" in text or "KONTOAUSZUG" in text:
            from .extractor_consorsbank import PDFConsorsbankExtractor
            extractor = PDFConsorsbankExtractor(pdf_file)
        else:
            from .extractor import PDFTransactionExtractor
            extractor = PDFTransactionExtractor(pdf_file)
        return extractor.extract_transactions()

    def console_output(self):
        """Gibt alle Transaktionen zeilenweise auf der Konsole aus."""
        print("\nAlle Transaktionen:")
        for t in self.all_transactions:
            print(f"{t.date}\t{t.description}\t{t.amount}\t{t.account}\t{t.file_path}\t{t.hash}")
