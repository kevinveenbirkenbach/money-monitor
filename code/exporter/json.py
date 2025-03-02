from .base import Exporter
import json

class JSONExporter(Exporter):
    """Exports transactions to a JSON file."""
    def export(self):
        if not self.transactions:
            self.logger.warning("No transactions found to save.")
            return
        data = self.get_data_as_dicts()
        try:
            with open(self.output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.logger.success(f"JSON file created: {self.output_file}")
        except Exception as e:
            self.logger.error(f"Error exporting JSON: {e}")
