from .base import Exporter
from ..logger import Logger
from jinja2 import Environment, FileSystemLoader

class HTMLExporter(Exporter):
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
            "source": "bi bi-file-earmark-text me-1"
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