import pdfplumber
import csv
import re
import os
import argparse

def extract_transactions(pdf_path):
    """Extract transactions from a given PDF bank statement."""
    transactions = []
    account = ""
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines = text.split("\n")
                
                # Extract IBAN and BIC explicitly
                iban_match = re.search(r"IBAN\s+(DE\d{2}\s\d{4}\s\d{4}\s\d{4}\s\d{2})", text)
                bic_match = re.search(r"BIC\s+([A-Z0-9]+)", text)
                
                if iban_match:
                    account = iban_match.group(1).replace(" ", "")  # Normalize IBAN by removing spaces
                
                for i in range(len(lines)):
                    match = re.match(r"(\d{2}\.\d{2}\.\d{4})\s+(.+?)\s+(-?\d{1,3}(?:\.\d{3})*(?:,\d{2})?)", lines[i])
                    if match:
                        date = match.group(1)
                        description = match.group(2).strip()
                        amount = match.group(3).replace(".", "").replace(",", ".")
                        transactions.append([date, description, float(amount), account])
    
    return transactions

def save_to_csv(transactions, output_file):
    """Save extracted transactions into a CSV file."""
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Date", "Description", "Amount (EUR)", "Account"])
        writer.writerows(transactions)

def process_input_path(input_path, output_csv):
    """Process a single file or all PDF files in a given directory."""
    all_transactions = []
    
    if os.path.isdir(input_path):
        for file_name in os.listdir(input_path):
            if file_name.endswith(".pdf"):
                file_path = os.path.join(input_path, file_name)
                all_transactions.extend(extract_transactions(file_path))
    elif os.path.isfile(input_path) and input_path.endswith(".pdf"):
        all_transactions.extend(extract_transactions(input_path))
    else:
        print("Invalid input path. Please provide a valid PDF file or directory.")
        return
    
    save_to_csv(all_transactions, output_csv)
    print(f"CSV file created: {output_csv}")

def main():
    """Main function to parse arguments and execute processing."""
    parser = argparse.ArgumentParser(description="Extract transactions from a bank statement PDF and save to CSV.")
    parser.add_argument("input_path", type=str, help="Path to the input PDF file or directory containing PDFs.")
    parser.add_argument("output_csv", type=str, help="Path to save the output CSV file.")
    args = parser.parse_args()
    
    process_input_path(args.input_path, args.output_csv)

if __name__ == "__main__":
    main()
