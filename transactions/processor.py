import os
import concurrent.futures
from pdfminer.high_level import extract_text
from .extractor import PDFTransactionExtractor
from .extractor_consorsbank import PDFConsorsbankExtractor
from .extractor_dkb_csv import DKBCSVExtractor
from .logger import Logger

class TransactionProcessor:
    """Coordinates reading files (PDF, CSV) from multiple paths and exporting transactions."""
    def __init__(self, input_paths, output_base, print_transactions=False, recursive=False, export_types=None,
                 from_date=None, to_date=None, create_dirs=False, quiet=False, debug=False, print_cmd=False):
        self.input_paths = input_paths
        self.output_base = output_base
        self.all_transactions = []
        self.print_transactions = print_transactions
        self.recursive = recursive
        self.export_types = export_types or []
        self.from_date = from_date
        self.to_date = to_date
        self.create_dirs = create_dirs
        self.quiet = quiet
        self.debug = debug
        self.print_cmd = print_cmd
        self.logger = Logger(debug=self.debug, quiet=self.quiet)

    def log(self, message, level="info"):
        if level == "debug":
            self.logger.debug(message)
        elif level == "warning":
            self.logger.warning(message)
        elif level == "error":
            self.logger.error(message)
        else:
            self.logger.info(message)

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
                self.log(f"Invalid input path: {path}", level="warning")
        if not pdf_csv_files:
            self.log("No PDF/CSV files found in the given paths.", level="warning")
            return
        self.log(f"Found {len(pdf_csv_files)} files.", level="debug")

        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(executor.map(self.extract_from_file, pdf_csv_files))
            for transactions in results:
                self.all_transactions.extend(transactions)

        # Filter transactions based on date parameters
        if self.from_date or self.to_date:
            filtered = []
            for t in self.all_transactions:
                if self.from_date and t.date < self.from_date:
                    continue
                if self.to_date and t.date > self.to_date:
                    continue
                filtered.append(t)
            self.all_transactions = filtered

        # Export logic: iterate over all specified export types
        for fmt in self.export_types:
            ext = f".{fmt}"
            output_file = self.output_base
            if not output_file.endswith(ext):
                output_file += ext
            if self.create_dirs:
                os.makedirs(os.path.dirname(output_file), exist_ok=True)

            if fmt == "csv":
                from .exporter import CSVExporter
                exporter = CSVExporter(self.all_transactions, output_file)
                exporter.export()
            elif fmt == "html":
                from .exporter import HTMLExporter
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
            with open(file_path, encoding="utf-8") as f:
                lines = [f.readline() for _ in range(10)]
            content = " ".join(lines)
            if "Transaktionscode" in content or "PayPal" in content:
                from .extractor_paypal_csv import PayPalCSVExtractor
                extractor = PayPalCSVExtractor(file_path)
                return extractor.extract_transactions()
            elif "Buchungsdatum" in content:
                from .extractor_dkb_csv import DKBCSVExtractor
                extractor = DKBCSVExtractor(file_path, debug=True)
                return extractor.extract_transactions()
            else:
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
                extractor = PDFConsorsbankExtractor(file_path, debug=True)
            else:
                from .extractor import PDFTransactionExtractor
                extractor = PDFTransactionExtractor(file_path, debug=True)
            return extractor.extract_transactions()
        else:
            return []

    def console_output(self):
        if self.quiet:
            return
        print("\nAll Transactions:")
        for t in self.all_transactions:
            print(f"{t.date}\t{t.description}\t{t.amount}\t{t.sender}\t{t.file_path}\t{t.bank}\t{t.id}")
