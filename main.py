import argparse
from transactions.processor import TransactionProcessor

def main():
    parser = argparse.ArgumentParser(
        description="Extract transactions from a bank statement PDF and save to CSV."
    )
    parser.add_argument("input_path", type=str, help="Path to the input PDF file or directory containing PDFs.")
    parser.add_argument("output_csv", type=str, help="Path to save the output CSV file.")
    args = parser.parse_args()

    processor = TransactionProcessor(args.input_path, args.output_csv)
    processor.process()

if __name__ == "__main__":
    main()
