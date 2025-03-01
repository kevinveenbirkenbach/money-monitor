import os
import concurrent.futures
from pdfminer.high_level import extract_text
from .extractor import PDFTransactionExtractor
from .extractor_consorsbank import PDFConsorsbankExtractor
from .extractor_dkb_csv import DKBCSVExtractor

class TransactionProcessor:
    """Koordiniert das Einlesen der Dateien (PDF, CSV) aus mehreren Pfaden und den Export der Transaktionen."""
    def __init__(self, input_paths, output_base, print_transactions=False, recursive=False, export_formats=None, from_date=None, to_date=None):
        self.input_paths = input_paths
        self.output_base = output_base
        self.all_transactions = []
        self.print_transactions = print_transactions
        self.recursive = recursive
        self.export_formats = export_formats or {}
        # Filterparameter als Strings im Format YYYY-MM-DD
        self.from_date = from_date
        self.to_date = to_date

    def process(self):
        pdf_csv_files = []
        for path in self.input_paths:
            if os.path.isdir(path):
                if self.recursive:
                    for root, _, files in os.walk(path):
                        for file_name in files:
                            if file_name.lower().endswith((".pdf", ".csv")):
                                pdf_csv_files.append(os.path.join(root, file_name))
                else:
                    pdf_csv_files.extend([
                        os.path.join(path, file_name)
                        for file_name in os.listdir(path)
                        if file_name.lower().endswith((".pdf", ".csv"))
                    ])
            elif os.path.isfile(path) and path.lower().endswith((".pdf", ".csv")):
                pdf_csv_files.append(path)
            else:
                print(f"Invalid input path: {path}")

        if not pdf_csv_files:
            print("No PDF/CSV files found in the given paths.")
            return

        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(executor.map(self.extract_from_file, pdf_csv_files))
            for transactions in results:
                self.all_transactions.extend(transactions)

        # Filterung der Transaktionen anhand der Datum-Parameter:
        if self.from_date or self.to_date:
            filtered = []
            for t in self.all_transactions:
                # t.date ist im Format YYYY-MM-DD, also kann ein einfacher Stringvergleich funktionieren,
                # sofern die Daten immer korrekt formatiert sind.
                if self.from_date and t.date < self.from_date:
                    continue
                if self.to_date and t.date > self.to_date:
                    continue
                filtered.append(t)
            self.all_transactions = filtered

        # (Export-Logik, wie vorher)
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
                    # Übergib zusätzlich die Filterinformationen an den HTMLExporter
                    exporter = HTMLExporter(self.all_transactions, output_file, from_date=self.from_date, to_date=self.to_date)
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
    def extract_from_file(file_path):
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".csv":
            # Read the first few lines of the file to determine its type.
            with open(file_path, encoding="utf-8") as f:
                lines = [f.readline() for _ in range(10)]
            content = " ".join(lines)
            # If the file contains "Transaktionscode" or "PayPal", use the PayPal CSV extractor.
            if "Transaktionscode" in content or "PayPal" in content:
                from .extractor_paypal_csv import PayPalCSVExtractor
                extractor = PayPalCSVExtractor(file_path)
                return extractor.extract_transactions()
            # If the file contains "Buchungsdatum", assume it is a DKB CSV file.
            elif "Buchungsdatum" in content:
                from .extractor_dkb_csv import DKBCSVExtractor
                extractor = DKBCSVExtractor(file_path)
                return extractor.extract_transactions()
            else:
                # Unrecognized CSV format – return empty list.
                return []
        elif ext == ".pdf":
            try:
                text = extract_text(file_path, maxpages=1)
            except Exception:
                text = ""
            if "PayPal" in text and ("Händlerkonto-ID" in text or "Transaktionsübersicht" in text):
                from .extractor_paypal_pdf import PayPalPDFExtractor
                extractor = PayPalPDFExtractor(file_path)
                return extractor.extract_transactions()
            if "Consorsbank" in text or "KONTOAUSZUG" in text:
                from .extractor_consorsbank import PDFConsorsbankExtractor
                extractor = PDFConsorsbankExtractor(file_path)
            else:
                from .extractor import PDFTransactionExtractor
                extractor = PDFTransactionExtractor(file_path)
            return extractor.extract_transactions()
        else:
            return []


    def console_output(self):
        print("\nAlle Transaktionen:")
        for t in self.all_transactions:
            print(f"{t.date}\t{t.description}\t{t.amount}\t{t.account}\t{t.file_path}\t{t.bank}\t{t.id}")
