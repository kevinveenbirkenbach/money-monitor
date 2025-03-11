from .abstract import AbstractExporter
import yaml

class YamlExporter(AbstractExporter):
    """Exports transactions to a YAML file."""
    def export(self)->None:
        if not self.doTransactionsExist():
            return
        if yaml is None:
            self.log.error("PyYAML is not installed. Cannot export to YAML.")
            return
        data = self.get_data_as_dicts()
        try:
            with open(self.output_file, "w", encoding="utf-8") as f:
                yaml.dump(data, f, allow_unicode=True)
            self.log.success(f"YAML file created: {self.output_file}")
        except Exception as e:
            self.log.error(f"Error exporting YAML: {e}")