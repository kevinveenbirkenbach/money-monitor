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
        """Wandelt die Transaktionen in eine Liste von Dictionaries um, inklusive aller Felder."""
        data = []
        for t in self.transactions:
            data.append({
                "Date": t.date,
                "Description": t.description,
                "Amount (EUR)": t.amount,
                "Account": t.account,
                "File Path": t.file_path,
                "Bank": t.bank,
                "ID": t.id
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
            writer.writerow(["Date", "Description", "Amount (EUR)", "Account", "File Path", "Bank", "ID"])
            for t in self.transactions:
                writer.writerow([t.date, t.description, t.amount, t.account, t.file_path, t.bank, t.id])
        print(f"CSV file created: {self.output_file}")

class HTMLExporter(BaseExporter):
    """Exportiert die Transaktionen in eine HTML-Datei mit filterbarer und sortierbarer Tabelle mittels DataTables."""
    def export(self):
        if not self.transactions:
            print("No transactions found to save.")
            return

        # Bootstrap CSS, DataTables CSS und Bootstrap Icons einbinden
        html = (
            '<html><head><meta charset="utf-8"><title>Transactions</title>'
            # Bootstrap CSS
            '<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/css/bootstrap.min.css" rel="stylesheet" '
            'integrity="sha384-Zenh87qX5JnK2Jl0vWa8Ck2rdkQ2Bzep5IDxbcnCeuOxjzrPF/et3URy9Bv1WTRi" crossorigin="anonymous">'
            # DataTables CSS for Bootstrap 5
            '<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.13.4/css/dataTables.bootstrap5.min.css"/>'
            # Bootstrap Icons
            '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.9.1/font/bootstrap-icons.css">'
            '</head><body>'
            "<div class='container my-4'>"
            "<h1 class='mb-4'>Transactions</h1>"
            "<table id='transactionsTable' class='table table-striped table-hover'>"
            "<thead class='table-dark'><tr>"
            "<th>Date</th><th>Description</th><th>Amount (EUR)</th>"
            "<th>Account</th><th><i class='bi bi-file-earmark-text me-1'></i> File</th><th>Bank</th><th>ID</th>"
            "</tr></thead><tbody>"
        )
        for t in self.transactions:
            tr_class=""
            if t.amount is None:
                amount_html = f'<span class="text-danger"> No Value defined! </span>'
                icon = '<i class="bi bi-exclamation-triangle-fill text-warning me-1"></i>'
                tr_class="table-warning" 
            elif t.amount < 0:
                amount_html = f'<span class="text-danger">{t.amount}</span>'
                icon = '<i class="bi bi-arrow-down-circle-fill text-danger me-1"></i>'
            else:
                amount_html = f'<span class="text-success">{t.amount}</span>'
                icon = '<i class="bi bi-arrow-up-circle-fill text-success me-1"></i>'
            file_link = f'<a href="{t.file_path}">{os.path.basename(t.file_path)}</a>'
            html += (
                f"<tr class='{tr_class}'>"
                f"<td>{t.date}</td>"
                f"<td>{t.description}</td>"
                f"<td>{icon}{amount_html}</td>"
                f"<td>{t.account}</td>"
                f"<td>{file_link}</td>"
                f"<td>{t.bank}</td>"
                f"<td>{t.id}</td>"
                f"</tr>"
            )
        html += (
            "</tbody></table></div>"
            # jQuery und DataTables JS einbinden
            '<script src="https://code.jquery.com/jquery-3.6.0.min.js" crossorigin="anonymous"></script>'
            '<script type="text/javascript" src="https://cdn.datatables.net/1.13.4/js/jquery.dataTables.min.js"></script>'
            '<script type="text/javascript" src="https://cdn.datatables.net/1.13.4/js/dataTables.bootstrap5.min.js"></script>'
            # DataTables initialisieren
            '<script>'
            '$(document).ready(function() {'
            '  $("#transactionsTable").DataTable({'
            '    "order": [[ 0, "desc" ]],'
            '    "pageLength": 25'
            '  });'
            '});'
            '</script>'
            "</body></html>"
        )
        with open(self.output_file, "w", encoding="utf-8") as f:
            f.write(html)
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
