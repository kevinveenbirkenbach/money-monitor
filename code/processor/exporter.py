from .abstract import AbstractProcessor
from code.model.log import Log
from code.model.transactions_wrapper import TransactionsWrapper
from code.model.configuration import Configuration
import importlib

class ExportProcessor(AbstractProcessor):
    def process(self)->TransactionsWrapper:
        # Export logic: iterate over all specified export types
        for export_type in self.configuration.getExportTypes():
            ext = f".{export_type}"
            output_file = self.configuration.getOutputBase()
            if not output_file.endswith(ext):
                output_file += ext
            if self.configuration.shouldCreateDirs():
                os.makedirs(os.path.dirname(output_file), exist_ok=True)

            module = importlib.import_module(f".exporter.{export_type}", package=__package__)
            class_name = export_type.capitalize() + "Exporter"
            exporter_class = getattr(module, class_name)
            exporter = exporter_class(self.transactions_wrapper.getAll(), output_file)
            exporter.export()
        self.transactions_wrapper