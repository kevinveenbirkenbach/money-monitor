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
    def __init__(self, transactions, output_file, debug=False, quiet=False):
        self.transactions = sorted(transactions, key=lambda t: t.date)
        self.output_file = output_file
        self.logger = Logger(debug=debug, quiet=quiet)

    def get_data_as_dicts(self):
        return [
            {
                "id": t.id,
                "bank": t.bank,
                "date": t.date,
                "sender": t.sender,
                "to": t.to,
                "amount": t.amount,
                "currency": t.currency,
                "description": t.description,
                "invoice": t.invoice,
                "file_path": t.file_path
            }
            for t in self.transactions
        ]

class CSVExporter(BaseExporter):
    def export(self):
        if not self.transactions:
            self.logger.warning("No transactions found to save.")
            return
        try:
            with open(self.output_file, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Date", "Description", "Amount (EUR)", "From", "File Path", "Bank", "ID"])
                for t in self.transactions:
                    writer.writerow([t.date, t.description, t.amount, t.sender, t.file_path, t.bank, t.id])
            self.logger.info(f"CSV file created: {self.output_file}")
        except Exception as e:
            self.logger.error(f"Error exporting CSV: {e}")

class HTMLExporter(BaseExporter):
    def __init__(self, transactions, output_file, from_date=None, to_date=None, debug=False, quiet=False):
        super().__init__(transactions, output_file, debug=debug, quiet=quiet)
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

        for t in self.transactions:
            t.file_name = os.path.basename(t.file_path)

        env = Environment(loader=FileSystemLoader(searchpath="./templates"))
        template = env.get_template("transactions_template.html.j2")
        rendered_html = template.render(filter_info=filter_info, transactions=self.transactions)
        try:
            with open(self.output_file, "w", encoding="utf-8") as f:
                f.write(rendered_html)
            self.logger.info(f"HTML file created: {self.output_file}")
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
            self.logger.info(f"JSON file created: {self.output_file}")
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
            self.logger.info(f"YAML file created: {self.output_file}")
        except Exception as e:
            self.logger.error(f"Error exporting YAML: {e}")
