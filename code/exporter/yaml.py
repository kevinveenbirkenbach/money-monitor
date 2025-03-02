from .base import Exporter
import yaml

class YamlExporter(Exporter):
    """Exports transactions to a YAML file."""
    def export(self):
        if not self.transactions:
            self.logger.warning("No transactions found to save.")
            return
        if yaml is None:
            self.logger.error("PyYAML is not installed. Cannot export to YAML.")
            return
        data = self.get_data_as_dicts()
        try:
            with open(self.output_file, "w", encoding="utf-8") as f:
                yaml.dump(data, f, allow_unicode=True)
            self.logger.success(f"YAML file created: {self.output_file}")
        except Exception as e:
            self.logger.error(f"Error exporting YAML: {e}")