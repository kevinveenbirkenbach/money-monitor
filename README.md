# Financial Helper 💰📊

[Financial Helper](https://github.com/kevinveenbirkenbach/financial-helper) is a set of Python scripts designed to extract and export transactions from bank statement PDFs and CSV files. This tool was created by [Kevin Veen-Birkenbach](https://www.veen.world) to simplify the tax declaration process. It supports multiple banks (e.g., Barclays, ING-DiBa, Consorsbank, DKB, PayPal) and provides filtering by date range, along with various export formats (CSV, HTML, JSON, YAML).

## Features ✨

- **Multi-bank support:** Process statements from several banks including DKB CSVs, PayPal CSVs/PDFs, Barclays, ING-DiBa, Consorsbank, and more.
- **Date filtering:** Use `--from` and `--to` parameters to include only transactions within a specified date range (YYYY-MM-DD).
- **Multiple export formats:** Choose between CSV, HTML (with interactive DataTables for sorting, filtering, and pagination), JSON, and YAML.
- **Interactive HTML export:** The HTML export uses a Jinja2 template and DataTables with per-column filters (dropdowns for columns with ≤12 unique values or text inputs otherwise) and a reset filters button.
- **Bulk processing:** A bulk script (`bulk.py`) allows you to process multiple banks at once and create both individual and combined exports.

## Requirements 🛠️

- Python 3.6+
- Required Python packages:
  - `pdfplumber`
  - `pdfminer.six`
  - `jinja2`
  - (Optional) `pyyaml` for YAML export
- Internet access for loading Bootstrap, DataTables, and Bootstrap Icons from CDNs

Install the required packages using pip:

```bash
pip install pdfplumber pdfminer.six jinja2 pyyaml
```

## Installation & Setup 🚀

1. **Clone the repository:**

   ```bash
   git clone https://github.com/kevinveenbirkenbach/financial-helper.git
   cd financial-helper
   ```

2. **Configure your bank statement directories:**

   Ensure your bank statement files (PDF/CSV) are organized by bank name under the base directory (default: `~/Documents/institutions/Financial Institutes`). For example:

   ```
   ~/Documents/institutions/Financial Institutes/
     ├── Barclays Bank Ireland PLC/
     │     └── Bank Statements/
     ├── ING-DiBa AG/
     │     └── Bank Statements/
     ├── Consorsbank/
     │     └── Bank Statements/
     └── PayPal/
           └── Bank Statements/
   ```

## Usage ⚙️

### Running the Bulk Processor

The `bulk.py` script processes transactions for each bank individually and then creates a combined export.

Example command:

```bash
python bulk.py "Barclays Bank Ireland PLC" "ING-DiBa AG" "Consorsbank" "Paypal" --from 2023-01-01 --to 2023-12-31
```

This command will:
- Process each bank’s statements found in the corresponding `Bank Statements` folder.
- Apply a date filter to include only transactions from January 1, 2023 to December 31, 2023.
- Generate CSV and HTML exports for each bank as well as a combined export.

### Running the Main Script

You can also run the main script directly:

```bash
python main.py <input_paths> <output_base> [options]
```

Example:

```bash
python main.py "/path/to/Bank Statements" "/path/to/output/transactions" --csv --html --from 2023-01-01 --to 2023-12-31
```

### Options

- `input_paths`: One or more paths to PDF/CSV files or directories containing bank statements.
- `output_base`: The base path for the output file(s); the appropriate extension will be appended.
- `--console`: Print transactions to the console.
- `--csv`, `--html`, `--json`, `--yaml`: Select one or more export formats.
- `-r, --recursive`: Recursively search for files in subdirectories.
- `--from`: Only include transactions on or after this date (YYYY-MM-DD).
- `--to`: Only include transactions on or before this date (YYYY-MM-DD).

## License 📄

This project is licensed under the MIT License.

## Author

**Kevin Veen-Birkenbach**  
[https://www.veen.world](https://www.veen.world)  
Created to simplify the tax declaration process.

---

Happy processing! 🚀💸