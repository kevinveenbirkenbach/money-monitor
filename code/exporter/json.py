from .abstract import AbstractExporter
import json

class JsonExporter(AbstractExporter):
    """Exports transactions to a JSON file."""
    def export(self)->None:
        if not self.doTransactionsExist():
            return
        data = self.get_data_as_dicts()
        try:
            with open(self.output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.log.success(f"JSON file created: {self.output_file}")
        except Exception as e:
            self.log.error(f"Error exporting JSON: {e}")
