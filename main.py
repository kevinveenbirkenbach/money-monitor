import argparse
from transactions.processor import TransactionProcessor

def main():
    parser = argparse.ArgumentParser(
        description="Extract transactions from bank statement PDFs and save to one or more output formats. Optionally, print all transactions to the console."
    )
    # Mehrere Eingabepfade (Dateien oder Verzeichnisse) möglich
    parser.add_argument("input_paths", type=str, nargs="+", 
                        help="Paths to the input PDF file(s) or directory(ies) containing PDFs.")
    # Hier wird der Basisname der Ausgabedatei angegeben (ohne Suffix, falls noch nicht vorhanden)
    parser.add_argument("output_base", type=str, 
                        help="Base path to save the output file(s). The appropriate extension will be appended if missing.")
    parser.add_argument("--console", action="store_true", 
                        help="Print all transactions to the console.")
    # Exportformate: Nur wenn einer der Flags gesetzt ist, erfolgt der Export
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
        export_formats=export_formats
    )
    processor.process()

if __name__ == "__main__":
    main()
