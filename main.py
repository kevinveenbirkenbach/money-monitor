import argparse
from transactions.processor import TransactionProcessor

def main():
    parser = argparse.ArgumentParser(
        description="Extract transactions from bank statement PDFs and save to CSV. Optionally, print all transactions."
    )
    parser.add_argument("input_path", type=str, help="Path to the input PDF file or directory containing PDFs.")
    parser.add_argument("output_csv", type=str, help="Path to save the output CSV file.")
    parser.add_argument("--cat", action="store_true", help="Print all transactions to the console.")
    args = parser.parse_args()

    processor = TransactionProcessor(args.input_path, args.output_csv, print_transactions=args.cat)
    processor.process()

if __name__ == "__main__":
    main()
