import argparse
from code.processor import TransactionProcessor
from code.logger import Logger
import yaml

def main():
    parser = argparse.ArgumentParser(
        description="Extract transactions from bank statement PDFs and save to one or more output formats."
    )
    parser.add_argument("input_paths", type=str, nargs="+", help="Paths to the input PDF file(s) or directory(ies).")
    parser.add_argument("output_base", type=str, help="Base path to save the output file(s).")
    parser.add_argument("--console", action="store_true", help="Print all transactions to the console.")
    parser.add_argument("-r", "--recursive", action="store_true", help="Recursively search for PDF files.")
    parser.add_argument("--from", dest="from_date", type=str, help="Only include transactions on or after this date.")
    parser.add_argument("--to", dest="to_date", type=str, help="Only include transactions on or before this date.")
    parser.add_argument("--create-dirs", action="store_true", help="Create parent directories for output base.")
    parser.add_argument("--export-types", nargs="+", choices=["csv", "html", "json", "yaml"],
                        help="Export formats (choose one or more: csv, html, json, yaml)")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress all output (except CMD if --print-cmd).")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable detailed debug output.")
    parser.add_argument("--print-cmd", action="store_true", help="Print constructed CMD commands before execution.")
    parser.add_argument("--config", type=str, help="Path to a YAML config file with default values.")
    parser.add_argument("--validate", action="store_true", help="Enable validation based on config.")
    
    args = parser.parse_args()

    # Initialize logger
    logger = Logger(debug=args.debug, quiet=args.quiet)
    logger.info("Starting main process...")

    # Load YAML config if provided
    config_data = {}
    if args.config:
        try:
            with open(args.config, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load config file '{args.config}': {e}")
            config_data = {}

    # Pass config_data to the TransactionProcessor
    processor = TransactionProcessor(
        input_paths=args.input_paths,
        output_base=args.output_base,
        print_transactions=args.console,
        recursive=args.recursive,
        export_types=args.export_types or [],
        from_date=args.from_date,
        to_date=args.to_date,
        create_dirs=args.create_dirs,
        quiet=args.quiet,
        logger=logger,
        print_cmd=args.print_cmd,
        config=config_data,
        validate=args.validate, 
    )
    processor.process()

if __name__ == "__main__":
    main()
