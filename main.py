import argparse
from transactions.processor import TransactionProcessor

def main():
    parser = argparse.ArgumentParser(
        description="Extract transactions from bank statement PDFs and save to CSV. Optionally, print all transactions."
    )
    # Mit nargs="+" können mehrere Eingabepfade übergeben werden
    parser.add_argument("input_paths", type=str, nargs="+", help="Paths to the input PDF file(s) or directory(ies) containing PDFs.")
    parser.add_argument("output_csv", type=str, help="Path to save the output CSV file.")
    parser.add_argument("--cat", action="store_true", help="Print all transactions to the console.")
    parser.add_argument("-r", "--recursive", action="store_true", help="Recursively search for PDF files in subdirectories.")
    args = parser.parse_args()

    processor = TransactionProcessor(args.input_paths, args.output_csv,
                                     print_transactions=args.cat, recursive=args.recursive)
    processor.process()

if __name__ == "__main__":
    main()
