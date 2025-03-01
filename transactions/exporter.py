import csv
import json
try:
    import yaml
except ImportError:
    yaml = None

class CSVExporter:
    """Exportiert die Transaktionen in eine CSV-Datei."""
    def __init__(self, transactions, output_file):
        self.transactions = transactions
        self.output_file = output_file

    def export(self):
        if not self.transactions:
            print("No transactions found to save.")
            return
        self.transactions.sort(key=lambda t: t.date)
        with open(self.output_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Date", "Description", "Amount (EUR)", "Account", "File Path", "Transaction Hash"])
            for t in self.transactions:
                writer.writerow(t.to_list())
        print(f"CSV file created: {self.output_file}")

class HTMLExporter:
    """Exportiert die Transaktionen in eine HTML-Datei."""
    def __init__(self, transactions, output_file):
        self.transactions = transactions
        self.output_file = output_file

    def export(self):
        if not self.transactions:
            print("No transactions found to save.")
            return
        self.transactions.sort(key=lambda t: t.date)
        html = "<html><head><meta charset='utf-8'><title>Transactions</title></head><body>"
        html += "<table border='1'><tr><th>Date</th><th>Description</th><th>Amount (EUR)</th><th>Account</th><th>File Path</th><th>Transaction Hash</th></tr>"
        for t in self.transactions:
            html += f"<tr><td>{t.date}</td><td>{t.description}</td><td>{t.amount}</td><td>{t.account}</td><td>{t.file_path}</td><td>{t.hash}</td></tr>"
        html += "</table></body></html>"
        with open(self.output_file, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"HTML file created: {self.output_file}")

class JSONExporter:
    """Exportiert die Transaktionen in eine JSON-Datei."""
    def __init__(self, transactions, output_file):
        self.transactions = transactions
        self.output_file = output_file

    def export(self):
        if not self.transactions:
            print("No transactions found to save.")
            return
        self.transactions.sort(key=lambda t: t.date)
        data = []
        for t in self.transactions:
            data.append({
                "Date": t.date,
                "Description": t.description,
                "Amount (EUR)": t.amount,
                "Account": t.account,
                "File Path": t.file_path,
                "Transaction Hash": t.hash
            })
        with open(self.output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"JSON file created: {self.output_file}")

class YamlExporter:
    """Exportiert die Transaktionen in eine YAML-Datei."""
    def __init__(self, transactions, output_file):
        self.transactions = transactions
        self.output_file = output_file

    def export(self):
        if not self.transactions:
            print("No transactions found to save.")
            return
        if yaml is None:
            print("PyYAML is not installed. Cannot export to YAML.")
            return
        self.transactions.sort(key=lambda t: t.date)
        data = []
        for t in self.transactions:
            data.append({
                "Date": t.date,
                "Description": t.description,
                "Amount (EUR)": t.amount,
                "Account": t.account,
                "File Path": t.file_path,
                "Transaction Hash": t.hash
            })
        with open(self.output_file, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True)
        print(f"YAML file created: {self.output_file}")
