import csv
import json
import os
try:
    import yaml
except ImportError:
    yaml = None
from .logger import Logger
from jinja2 import Environment, FileSystemLoader

class BaseExporter:
    def __init__(self, transactions, output_file, logger=Logger(), quiet=False):
        self.transactions = sorted(transactions, key=lambda t: t.transaction_date)
        self.output_file = output_file
        self.logger = logger

    def get_data_as_dicts(self):
        return [
            t.getDictionary() for t in self.transactions
        ]

class CSVExporter(BaseExporter):
    """Exports transactions to a CSV file."""
    def export(self):
        if not self.transactions:
            self.logger.warning("No transactions found to save.")
            return
        try:
            with open(self.output_file, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                # Get the header keys from the first transaction's dictionary
                header = list(self.transactions[0].getDictionary().keys())
                writer.writerow(header)
                # Write each transaction's values in the same order as the header
                for t in self.transactions:
                    data = t.getDictionary()
                    row = [data.get(key, "") for key in header]
                    writer.writerow(row)
            self.logger.success(f"CSV file created: {self.output_file}")
        except Exception as e:
            self.logger.error(f"Error exporting CSV: {e}")

class HTMLExporter(BaseExporter):
    def __init__(self, transactions, output_file, from_date=None, to_date=None, logger=Logger(), quiet=False):
        super().__init__(transactions, output_file, logger, quiet=quiet)
        self.from_date = from_date
        self.to_date = to_date

    def export(self):
        if not self.transactions:
            self.logger.warning("No transactions found to save.")
            return

        filter_info = ""
        if self.from_date and self.to_date:
            filter_info = f"Filtered: {self.from_date} to {self.to_date}"
        elif self.from_date:
            filter_info = f"Filtered: on or after {self.from_date}"
        elif self.to_date:
            filter_info = f"Filtered: on or before {self.to_date}"
        
        icon_map = {
            "id": "bi bi-hash me-1",
            "bank": "bi bi-bank me-1",
            "account": "bi bi-bank me-1",
            "date": "bi bi-calendar me-1",
            "sender": "bi bi-person me-1",
            "receiver": "bi bi-person-lines-fill me-1",
            "value": "bi bi-currency-euro me-1",
            "currency": "bi bi-cash-stack me-1",
            "description": "bi bi-card-text me-1",
            "invoice": "bi bi-receipt me-1",
            "transaction_source_document": "bi bi-file-earmark-text me-1"
        }

        env = Environment(loader=FileSystemLoader(searchpath="./templates"))
        template = env.get_template("transactions_template.html.j2")
        rendered_html = template.render(filter_info=filter_info, transactions=self.transactions,icon_map=icon_map)
        try:
            with open(self.output_file, "w", encoding="utf-8") as f:
                f.write(rendered_html)
            self.logger.success(f"HTML file created: {self.output_file}")
        except Exception as e:
            self.logger.error(f"Error exporting HTML: {e}")

class JSONExporter(BaseExporter):
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

class YamlExporter(BaseExporter):
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
