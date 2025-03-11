import argparse
from code.model.log import Log
import yaml
import sys
from code.processor.load import LoadProcessor
from code.processor.filter import FilterProcessor
from code.model.configuration import Configuration
from code.processor.validator import ValidatorProcessor
from code.processor.exporter import ExportProcessor

def main():
    parser = argparse.ArgumentParser(
        description="Extract transactions from bank statement PDFs and save to one or more output formats."
    )
    parser.add_argument("input_paths", type=str, nargs="+", help="Paths to the input PDF file(s) or directory(ies).")
    parser.add_argument("output_base", type=str, help="Base path to save the output file(s).")
    parser.add_argument("-r", "--recursive", action="store_true", help="Recursively search for PDF files.")
    parser.add_argument("--from", dest="from_date", type=str, help="Only include transactions on or after this date.")
    parser.add_argument("--to", dest="to_date", type=str, help="Only include transactions on or before this date.")
    parser.add_argument("--create-dirs", action="store_true", default=False, help="Create parent directories for output base.")
    parser.add_argument("--export-types", nargs="+", choices=["csv", "html", "json", "yaml","console"],
                        help="Export formats (choose one or more: csv, html, json, yaml)")
    parser.add_argument("-q", "--quiet", action="store_true",default=False, help="Suppress all output (except CMD if --print-cmd).")
    parser.add_argument("-d", "--debug", action="store_true",default=False, help="Enable detailed debug output.")
    parser.add_argument("--print-cmd", action="store_true", help="Print constructed CMD commands before execution.")
    parser.add_argument("-c", "--configuration-file", type=str, help="Path to a YAML config file with default values.")
    parser.add_argument("--validate", action="store_true", help="Enable validation based on configuration.")
    
    args = parser.parse_args()
    
    # Initialize Configuration
    configuration = Configuration(
        configuration_file=args.configuration_file,
        input_paths=args.input_paths,
        output_base=args.output_base,
        export_types=args.export_types,
        create_dirs=args.create_dirs,
        quiet=args.quiet,
        debug=args.debug,
        validate=args.validate,
        print_cmd=args.print_cmd,
        recursive=args.recursive
        )
    if args.from_date:
        configuration.setFromDate(args.from_date)
    if args.to_date:
        configuration.setToDate(args.to_date)

    # Initialize log
    log = Log(configuration)
    log.info("Starting main process...")
    
    # Load
    loaded_transactions_wrapper = LoadProcessor(
        log=log,
        configuration=configuration
        ).process()
    
    # Sort Transactions by Date
    loaded_transactions_wrapper.sortByDate()
    
    # Filter
    filtered_transactions_wrapper=FilterProcessor(
        log=log,
        configuration=configuration,
        transactions_wrapper=loaded_transactions_wrapper
        ).process()
    
    # Validate
    valid_transactions_wrapper=ValidatorProcessor(
        log=log,
        configuration=configuration,
        transactions_wrapper=filtered_transactions_wrapper
        ).process()

    # Export
    exported_transactions_wrapper=ExportProcessor(
        log=log,
        configuration=configuration,
        transactions_wrapper=valid_transactions_wrapper
        ).process() 
    
    if log.error_count > 0:
        log.warning(f"This program produced {log.error_count} errors.")
        log.error("Program failed.")
        sys.exit(log.error_count)

if __name__ == "__main__":
    main()
