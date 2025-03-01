#!/usr/bin/env python3
import os
import subprocess
import argparse
from transactions.logger import Logger

def prepare_cmd(base_dir, bank, input_path, output_file, from_date, to_date, quiet, debug, print_cmd):
    cmd = ["python", "main.py", "-r"]
    
    # Wenn es sich um eine einzelne Bank handelt, fügen wir den einzelnen input_path hinzu
    if isinstance(input_path, list):  # Falls eine Liste übergeben wird
        cmd.extend(input_path)  # Füge alle Elemente aus input_path hinzu
    else:
        cmd.append(input_path)  # Für den Fall einer einzelnen Bank, wie "all"

    cmd.extend([output_file, "--export-types", "csv", "html"])
    if from_date:
        cmd.extend(["--from", from_date])
    if to_date:
        cmd.extend(["--to", to_date])
    cmd.append("--create-dir")
    if quiet:
        cmd.append("--quiet")
    if debug:
        cmd.append("--debug")
    
    if print_cmd:
        return "CMD: " + " ".join(cmd)
    
    return cmd

def process_banks(base_dir, banks, from_date, to_date, quiet, debug, print_cmd, logger):
    for bank in banks:
        input_path = os.path.join(base_dir, bank, "Bank Statements")
        output_file = os.path.join(base_dir, bank, "Transactions/transactions")
        logger.info(f"Processing {bank} from {input_path} ...")

        cmd = prepare_cmd(base_dir, bank, input_path, output_file, from_date, to_date, quiet, debug, print_cmd)
        if print_cmd:
            logger.info(cmd)
        else:
            subprocess.run(cmd)


def main():
    parser = argparse.ArgumentParser(
        description="Process bank statements for multiple banks and export transactions."
    )
    parser.add_argument("banks", nargs="+", help="List of bank names (e.g., 'Barclays', 'ING-DiBa', 'Paypal')")
    parser.add_argument("--base_dir", default=os.path.expanduser("~/Documents/institutions/Financial Institutes"),
                        help="Base directory where bank folders are located (default: ~/Documents/institutions/Financial Institutes)")
    parser.add_argument("--from", dest="from_date", type=str, default="", help="Start date filter (YYYY-MM-DD)")
    parser.add_argument("--to", dest="to_date", type=str, default="", help="End date filter (YYYY-MM-DD)")
    parser.add_argument("--print-cmd", action="store_true", help="Print the CMD commands instead of executing them.")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress all output (except CMD if --print-cmd is set)")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable detailed debug output")
    args = parser.parse_args()

    logger = Logger(debug=args.debug, quiet=args.quiet)

    process_banks(args.base_dir, args.banks, args.from_date, args.to_date, args.quiet, args.debug, args.print_cmd, logger)

    # Process all banks together for a combined export
    combined_input_paths = [os.path.join(args.base_dir, bank, "Bank Statements") for bank in args.banks]
    combined_output = os.path.join(args.base_dir, "transactions")
    cmd = prepare_cmd(args.base_dir, "all", combined_input_paths, combined_output, args.from_date, args.to_date, args.quiet, args.debug, args.print_cmd)
    if args.print_cmd:
        logger.info(cmd)
    else:
        subprocess.run(cmd)


if __name__ == "__main__":
    main()
