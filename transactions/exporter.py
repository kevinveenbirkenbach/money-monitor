import csv
import json
import os
try:
    import yaml
except ImportError:
    yaml = None

class BaseExporter:
    """Basisklasse für Exporter. Sie sortiert die Transaktionen und stellt eine gemeinsame Methode
    zur Umwandlung in ein Dictionary bereit, das alle Felder (inklusive Bank) enthält."""
    def __init__(self, transactions, output_file):
        # Sortiere die Transaktionen nach Datum
        self.transactions = sorted(transactions, key=lambda t: t.date)
        self.output_file = output_file

    def get_data_as_dicts(self):
        data = []
        for t in self.transactions:
            data.append({
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
            })
        return data

class CSVExporter(BaseExporter):
    """Exportiert die Transaktionen in eine CSV-Datei."""
    def export(self):
        if not self.transactions:
            print("No transactions found to save.")
            return
        with open(self.output_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Date", "Description", "Amount (EUR)", "From", "File Path", "Bank", "ID"])
            for t in self.transactions:
                writer.writerow([t.date, t.description, t.amount, t.sender, t.file_path, t.bank, t.id])

        print(f"CSV file created: {self.output_file}")

import os
from jinja2 import Environment, FileSystemLoader

class HTMLExporter(BaseExporter):
    """Exports transactions to an HTML file using a Jinja2 template."""
    def __init__(self, transactions, output_file, from_date=None, to_date=None):
        super().__init__(transactions, output_file)
        self.from_date = from_date
        self.to_date = to_date

    def export(self):
        if not self.transactions:
            print("No transactions found to save.")
            return

        # Build filter information
        filter_info = ""
        if self.from_date and self.to_date:
            filter_info = f"Filtered: {self.from_date} to {self.to_date}"
        elif self.from_date:
            filter_info = f"Filtered: on or after {self.from_date}"
        elif self.to_date:
            filter_info = f"Filtered: on or before {self.to_date}"

        for t in self.transactions:
            t.file_name = os.path.basename(t.file_path)

        # Set up Jinja2 environment and load the template
        env = Environment(loader=FileSystemLoader(searchpath="./templates"))
        template = env.get_template("transactions_template.html.j2")

        rendered_html = template.render(
            filter_info=filter_info,
            transactions=self.transactions
        )

        with open(self.output_file, "w", encoding="utf-8") as f:
            f.write(rendered_html)
        print(f"HTML file created: {self.output_file}")


class JSONExporter(BaseExporter):
    """Exportiert die Transaktionen in eine JSON-Datei."""
    def export(self):
        if not self.transactions:
            print("No transactions found to save.")
            return
        data = self.get_data_as_dicts()
        with open(self.output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"JSON file created: {self.output_file}")

class YamlExporter(BaseExporter):
    """Exportiert die Transaktionen in eine YAML-Datei."""
    def export(self):
        if not self.transactions:
            print("No transactions found to save.")
            return
        if yaml is None:
            print("PyYAML is not installed. Cannot export to YAML.")
            return
        data = self.get_data_as_dicts()
        with open(self.output_file, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True)
        print(f"YAML file created: {self.output_file}")
