#!/usr/bin/env python3
import os
import subprocess
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="Process bank statements for multiple banks and export transactions."
    )
    parser.add_argument("banks", nargs="+",
                        help="List of bank names (e.g., 'Barclays Bank Ireland PLC' 'ING-DiBa AG' 'Consorsbank' 'Paypal')")
    parser.add_argument("--base_dir", default=os.path.expanduser("~/Documents/institutions/Financial Institutes"),
                        help="Base directory where bank folders are located (default: ~/Documents/institutions/Financial Institutes)")
    parser.add_argument("--from", dest="from_date", type=str, default="",
                        help="Start date filter in YYYY-MM-DD format (only include transactions on or after this date)")
    parser.add_argument("--to", dest="to_date", type=str, default="",
                        help="End date filter in YYYY-MM-DD format (only include transactions on or before this date)")
    # Neuer Parameter, um die Befehle auszugeben
    parser.add_argument("--print-cmd", action="store_true",
                        help="Print the CMD commands instead of (or in addition to) executing them.")
    args = parser.parse_args()

    base_dir = args.base_dir
    banks = args.banks
    # Process each bank individually
    for bank in banks:
        input_path = os.path.join(base_dir, bank, "Bank Statements")
        output_file = os.path.join(base_dir, bank, "Transactions/transactions")  # base output name without extension
        print(f"Processing {bank} from {input_path} ...")
        cmd = ["python", "main.py", "-r", input_path, output_file, "--export-types", "csv", "html"]
        if args.from_date:
            cmd.extend(["--from", args.from_date])
        if args.to_date:
            cmd.extend(["--to", args.to_date])
        cmd.extend(["--create-dir"])
        # Falls der Flag gesetzt ist, gebe den Befehl aus:
        if args.print_cmd:
            print("CMD:", " ".join(cmd))
        subprocess.run(cmd)

    # Now process all banks together for a combined export
    combined_input_paths = []
    for bank in banks:
        combined_input_paths.append(os.path.join(base_dir, bank, "Bank Statements"))
    combined_output = os.path.join(base_dir, "transactions")
    cmd = ["python", "main.py", "-r"] + combined_input_paths + [combined_output, "--export-types", "csv", "html"]
    if args.from_date:
        cmd.extend(["--from", args.from_date])
    if args.to_date:
        cmd.extend(["--to", args.to_date])
    if args.print_cmd:
        print("CMD:", " ".join(cmd))
    subprocess.run(cmd)

if __name__ == "__main__":
    main()
