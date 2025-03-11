#!/usr/bin/env python3
import os
import subprocess
import argparse
from code.model.log import Log
from code.model.configuration import Configuration

def prepare_cmd(base_dir, bank, input_path, output_file, from_date, to_date, quiet, debug, print_cmd, config, validate:bool):
    cmd = ["python", "main.py", "-r"]

    # If input_path is a list (multiple directories), extend them all
    if isinstance(input_path, list):
        cmd.extend(input_path)
    else:
        cmd.append(input_path)

    # Base arguments
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
    if config:
        cmd.extend(["--config", config])
    if validate:
        cmd.extend(["--validate", validate])

    if print_cmd:
        return "CMD: " + " ".join(cmd)

    return cmd

def process_banks(base_dir, banks, from_date, to_date, quiet, debug, print_cmd, log, config,validate:bool):
    for bank in banks:
        input_path = os.path.join(base_dir, bank, "Bank Statements")
        output_file = os.path.join(base_dir, bank, "Transactions/transactions")
        log.info(f"Processing {bank} from {input_path} ...")

        cmd = prepare_cmd(base_dir, bank, input_path, output_file, from_date, to_date, quiet, debug, print_cmd, config, validate)
        if print_cmd:
            log.info(cmd)
        else:
            subprocess.run(cmd)

def main():
    parser = argparse.ArgumentParser(
        description="Process bank statements for multiple banks and export transactions."
    )
    parser.add_argument("banks", nargs="+", help="List of bank names (e.g., 'Barclays', 'ING-DiBa', 'Paypal')")
    parser.add_argument("--base_dir", default=os.path.expanduser("~/Documents/institutions/Financial Institutes"),
                        help="Base directory where bank folders are located.")
    parser.add_argument("--from", dest="from_date", type=str, default="", help="Start date filter (YYYY-MM-DD)")
    parser.add_argument("--to", dest="to_date", type=str, default="", help="End date filter (YYYY-MM-DD)")
    parser.add_argument("--print-cmd", action="store_true", help="Print the CMD commands instead of executing them.")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress all output (except CMD if --print-cmd).")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable detailed debug output.")
    parser.add_argument("-c", "--configuration-file", type=str, help="Path to a YAML config file with default values.")
    parser.add_argument("--validate", action="store_true", help="Enable validation based on configuration.")
    args = parser.parse_args()
    
    # Initialize Configuration
    configuration = Configuration(
        configuration_file=args.configuration_file,
        input_paths="",
        output_base="",
        export_types="",
        create_dirs="",
        quiet=args.quiet,
        debug=args.debug,
        validate=args.validate,
        print_cmd=args.print_cmd, 
        recursive=None
        )
    if args.from_date:
        configuration.setFromDate(args.from_date)
    if args.to_date:
        configuration.setToDate(args.to_date)

    log = Log(configuration)

    # Process each bank separately
    process_banks(
        args.base_dir,
        args.banks,
        args.from_date,
        args.to_date,
        args.quiet,
        args.debug,
        args.print_cmd,
        log,
        args.configuration_file,
        args.validate
    )

    # Process all banks together for a combined export
    combined_input_paths = [os.path.join(args.base_dir, bank, "Bank Statements") for bank in args.banks]
    combined_output = os.path.join(args.base_dir, "transactions")
    cmd = prepare_cmd(args.base_dir, "all", combined_input_paths, combined_output, 
                      args.from_date, args.to_date, args.quiet, args.debug, 
                      args.print_cmd, args.configuration_file, args.validate)

    if args.print_cmd:
        log.info(cmd)
    else:
        subprocess.run(cmd)

if __name__ == "__main__":
    main()
