from .abstract import AbstractProcessor
from code.model.transactions_wrapper import TransactionsWrapper
from code.model.configuration import Configuration
from code.factories.extractor import ExtractorFactory
import os
import concurrent.futures


class LoadProcessor(AbstractProcessor):

    def extract_from_file(self, file_path):
        extractor_factory = ExtractorFactory(self.log, configuration=self.configuration)
        extractor = extractor_factory.create_extractor(file_path)
        if extractor:
            return extractor.extract_transactions()
        return []

    def process(self)->TransactionsWrapper:
        pdf_csv_files = []
        for path in self.configuration.getInputPaths():
            if os.path.isdir(path):
                if self.configuration.shouldRecursiveScan():
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
                self.log.warning(f"Invalid input path: {path}")
        if not pdf_csv_files:
            self.log.warning("No PDF/CSV files found in the given paths.")
            return
        self.log.info(f"Found {len(pdf_csv_files)} files.")

        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(executor.map(self.extract_from_file, pdf_csv_files))
            for transactions in results:
                self.transactions_wrapper.extendTransactions(transactions)
                
        return self.transactions_wrapper