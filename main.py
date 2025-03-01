import argparse
from transactions.processor import TransactionProcessor

def main():
    parser = argparse.ArgumentParser(
        description="Extract transactions from bank statement PDFs and save to one or more output formats. Optionally, print all transactions to the console."
    )
    # Mehrere Eingabepfade (Dateien oder Verzeichnisse) möglich
    parser.add_argument("input_paths", type=str, nargs="+", 
                        help="Paths to the input PDF file(s) or directory(ies) containing PDFs.")
    # Basisname der Ausgabedatei
    parser.add_argument("output_base", type=str, 
                        help="Base path to save the output file(s). The appropriate extension will be appended if missing.")
    parser.add_argument("--console", action="store_true", 
                        help="Print all transactions to the console.")
    # Exportformate
    parser.add_argument("--csv", action="store_true", 
                        help="Export transactions to CSV.")
    parser.add_argument("--html", action="store_true", 
                        help="Export transactions to HTML.")
    parser.add_argument("--json", action="store_true", 
                        help="Export transactions to JSON.")
    parser.add_argument("--yaml", action="store_true", 
                        help="Export transactions to YAML.")
    parser.add_argument("-r", "--recursive", action="store_true", 
                        help="Recursively search for PDF files in subdirectories.")
    # Neue Filterparameter
    parser.add_argument("--from", dest="from_date", type=str,
                        help="Only include transactions on or after this date (YYYY-MM-DD).")
    parser.add_argument("--to", dest="to_date", type=str,
                        help="Only include transactions on or before this date (YYYY-MM-DD).")
    args = parser.parse_args()

    export_formats = {
        "csv": args.csv,
        "html": args.html,
        "json": args.json,
        "yaml": args.yaml
    }

    processor = TransactionProcessor(
        input_paths=args.input_paths, 
        output_base=args.output_base,
        print_transactions=args.console, 
        recursive=args.recursive,
        export_formats=export_formats,
        from_date=args.from_date,
        to_date=args.to_date
    )
    processor.process()

if __name__ == "__main__":
    main()
