# 🤑 Money Monitor (momo)
![GitHub license](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python version](https://img.shields.io/badge/Python-3.x-blue.svg)

**Money Monitor** is a comprehensive Python tool for scanning, organizing, and logging your financial documents. It processes bank statement PDFs, CSV files, invoices, and more—automatically extracting transactions and sorting them into a unified financial log.

## 🎯 Purpose

Money Monitor simplifies the process of tracking your financial data by:
- Scanning bank documents and invoices.
- Extracting and consolidating transaction data.
- Organizing and exporting transactions into various formats (CSV, HTML, JSON, YAML) for further analysis or reporting.

Whether you're preparing for tax declarations or simply need a centralized financial log, Money Monitor helps you keep your records in order.

## 🚀 Features

- **Multi-source Document Processing:** Automatically scans bank statements and invoice files from multiple financial institutions.
- **Transaction Extraction:** Identifies and extracts transaction details including dates, amounts, descriptions, and account information.
- **Date Filtering:** Use date filters to include transactions within a specified range.
- **Multiple Export Formats:** Export your consolidated transactions as CSV, HTML, JSON, or YAML.
- **Bulk Processing:** Process documents from multiple banks and create both individual and combined exports.
- **Interactive HTML Export:** View your transactions in an interactive HTML table with sorting, filtering, and pagination.

## 📥 Installation

Money Monitor can be easily installed using [Kevin's Package Manager](https://github.com/kevinveenbirkenbach/package-manager). Once you have the package manager set up, simply run:

```bash
pkgmgr install momo
```

This command will install Money Monitor on your system with the alias **momo**.

## 🚀 Usage

### Bulk Processing

The `bulk.py` script processes transactions for each bank individually and then creates a combined export.

Example command:
```bash
python bulk.py "Barclays" "ING-DiBa" "Consorsbank" "Paypal" --from 2023-01-01 --to 2023-12-31
```
This command will:
- Process each bank’s statements found in their respective directories.
- Apply a date filter (January 1, 2023 to December 31, 2023).
- Generate CSV and HTML exports for each bank, as well as a combined export.

### Main Script

Run the main script to extract transactions from bank documents and invoices:
```bash
python main.py <input_paths> <output_base> [options]
```

Example:
```bash
python main.py "/path/to/documents" "/path/to/output/transactions" --csv --html --from 2023-01-01 --to 2023-12-31
```

### Options

- `input_paths`: One or more paths to PDF/CSV files or directories containing financial documents.
- `output_base`: The base path for the output file(s); the appropriate extension will be appended.
- `--console`: Print transactions to the console.
- `--csv`, `--html`, `--json`, `--yaml`: Choose one or more export formats.
- `-r, --recursive`: Recursively search for files in subdirectories.
- `--from`: Only include transactions on or after this date (YYYY-MM-DD).
- `--to`: Only include transactions on or before this date (YYYY-MM-DD).
- `--create-dirs`: Automatically create parent directories for the output base.
- `--config`: Path to a YAML config file with default values.
- `--validate`: Enable additional validation based on the config file.
- `--print-cmd`: Print the constructed command-line commands without executing them.
- `-q, --quiet`: Suppress non-essential output.
- `-d, --debug`: Enable detailed debug output.

## 📜 License

This project is licensed under the **MIT License**.

## 👨‍💻 Author

Developed by **Kevin Veen-Birkenbach**  
- 🌐 [cybermaster.space](https://cybermaster.space/)  
- 📧 [kevin@veen.world](mailto:kevin@veen.world)

## ⚠️ Disclaimer

Money Monitor is designed for educational and practical purposes. Always back up your data before processing any financial documents. Use at your own risk.

---

Happy logging! 🚀💸
