import os
import importlib
from pdfminer.high_level import extract_text
from code.converter.pdf import PDFConverter

class ExtractorFactory:
    """
    Factory class that decides which extractor to use for a given file
    based on extension and textual patterns.
    """
    def __init__(self, logger, config=None):
        self.logger = logger
        self.config = config or {}
        
        # Mappings for CSV-based extractors:
        # Each entry is: (condition_func, module_name, class_name)
        # condition_func receives a string containing the first ~10 lines
        self.csv_extractor_mappings = [
            (
                lambda content: "Transaktionscode" in content or "PayPal" in content,
                "code.extractor.csv.paypal",    # e.g. .extractor_csv_paypal
                "PayPalCSVExtractor"
            ),
            (
                lambda content: "Buchungsdatum" in content,
                "code.extractor.csv.dkb", 
                "DKBCSVExtractor"
            ),
        ]

        # Mappings for PDF-based extractors:
        # Each entry is: (condition_func, module_name, class_name)
        # condition_func receives (text, lower_text)
        self.pdf_extractor_mappings = [
            (
                lambda text, lower_text: "paypal" in lower_text
                                         and ("händlerkonto-id" in lower_text
                                              or "transaktionsübersicht" in lower_text),
                "PayPal"
            ),
            (
                lambda text, lower_text: "ing-diba" in lower_text or "ingddeffxxx" in lower_text,
                "Ing"
            ),
            (
                lambda text, lower_text: "consorsbank" in lower_text or "kontoauszug" in lower_text,
                "Consorsbank",
            ),
            (
                lambda text, lower_text: "barclaycard" in lower_text or "barcdehaxx" in lower_text,
                "Barclays"
            ),
        ]

    def create_extractor(self, file_path):
        """
        Chooses and instantiates the correct extractor based on the file extension
        and file content. Returns an extractor instance or None if no match is found.
        """
        ext = os.path.splitext(file_path)[1].lower()

        # Handle CSV
        if ext == ".csv":
            with open(file_path, encoding="utf-8") as f:
                # Read first ~10 lines to detect patterns
                lines = [f.readline() for _ in range(10)]
            content = " ".join(lines)

            # Go through each CSV mapping
            for condition_func, module_name, class_name in self.csv_extractor_mappings:
                if condition_func(content):
                    return self._instantiate_extractor(module_name, class_name, file_path)

            self.logger.info(f"No matching CSV extractor found for '{file_path}'.")
            return None

        # Handle PDF
        elif ext == ".pdf":
            pdf_converter = PDFConverter(self.logger, file_path);
            
            first_page_text = pdf_converter.getFirstPage()
            if first_page_text:
                lower_first_page_text = first_page_text.lower()
            else:
                return None

            # Go through each PDF mapping
            for condition_func, name in self.pdf_extractor_mappings:
                if condition_func(first_page_text, lower_first_page_text):
                    module_name = f"code.extractor.pdf.{name.lower()}.extractor"
                    class_name = f"{name}PDFExtractor"
                    self.logger.debug(f"Using extractor {module_name}.{class_name} for {file_path}")        
                    return self._instantiate_extractor(module_name, class_name, file_path)

            self.logger.info(f"No matching PDF extractor found for '{file_path}'.")
            return None

        # Unsupported extension
        else:
            self.logger.info(f"Unsupported file extension '{ext}' for {file_path}.")
            return None

    def _instantiate_extractor(self, module_name, class_name, file_path):
        """
        Dynamically imports the extractor module and instantiates the extractor class.
        """
        try:
            # Assuming the extractor modules are in the same package directory:
            module = importlib.import_module(f"{module_name}")
            extractor_class = getattr(module, class_name)
            # If your extractor needs a logger, pass it here as well
            return extractor_class(file_path, self.logger, config=self.config)
        except Exception as e:
            self.logger.error(f"Failed to instantiate extractor {class_name} from {module_name}: {e}")
            return None
