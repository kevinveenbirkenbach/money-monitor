from .abstract import AbstractExporter
from code.model.log import Log
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

class HtmlExporter(AbstractExporter):
    def export(self)->None:
        if not self.doTransactionsExist():
            return
        filter_info = ""
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self and self.configuration.getToDatetime():
            filter_info = f"Filtered: {self.configuration.getFromDatetime()} to {self.configuration.getToDatetime()}<br />Created: {timestamp}"
        elif self.configuration.getFromDatetime():
            filter_info = f"Filtered: on or after {self.configuration.getFromDatetime()}<br />Created: {timestamp}"
        elif self.configuration.getToDatetime():
            filter_info = f"Filtered: on or before {self.configuration.getToDatetime()}<br />Created: {timestamp} "
        
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
        rendered_html = template.render(filter_info=filter_info, transactions=self.transactions_wrapper.getAll(),icon_map=icon_map)
        try:
            with open(self.output_file, "w", encoding="utf-8") as f:
                f.write(rendered_html)
            self.log.success(f"HTML file created: {self.output_file}")
        except Exception as e:
            self.log.error(f"Error exporting HTML: {e}")