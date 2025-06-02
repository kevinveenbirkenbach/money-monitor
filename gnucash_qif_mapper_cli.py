# File: gnucash_qif_mapper_cli.py

#!/usr/bin/env python3

import argparse
import sys
from code.mapper.qif_mapper import build_qif_from_csv

def main():
    parser = argparse.ArgumentParser(
        description="Convert a flat CSV of transactions into a QIF file with splits (net, VAT, bank), optionally filtering by category."
    )

    parser.add_argument(
        "-i", "--input-csv",
        required=True,
        help="Path to the flat input CSV. Must contain columns: id,date,brutto value,currency,sender,description,Kategorie,netto value,Vat value"
    )
    parser.add_argument(
        "-o", "--output-qif",
        required=True,
        help="Path where the resulting QIF file will be written (e.g. 'transactions.qif')."
    )
    parser.add_argument(
        "--bank-account",
        required=True,
        help="Name of the Bank account in GnuCash (e.g. 'Assets:Bank:Consorsbank')."
    )
    parser.add_argument(
        "--income-account",
        required=True,
        help="Name of the Income account (for net amounts when brutto > 0). E.g. 'Income:Sales'."
    )
    parser.add_argument(
        "--expense-account",
        required=True,
        help="Name of the Expense account (for net amounts when brutto < 0). E.g. 'Expenses:Office Supplies'."
    )
    parser.add_argument(
        "--vat-output-account",
        required=True,
        help="Name of the VAT Output (liability) account (for brutto > 0). E.g. 'Liabilities:VAT Output 19%'."
    )
    parser.add_argument(
        "--vat-input-account",
        required=True,
        help="Name of the VAT Input (asset) account (for brutto < 0). E.g. 'Assets:VAT Input 19%'."
    )
    parser.add_argument(
        "--category",
        required=False,
        help="If set, only process rows where the 'Kategorie' column exactly matches this value."
    )

    args = parser.parse_args()

    try:
        build_qif_from_csv(
            input_csv=args.input_csv,
            output_qif=args.output_qif,
            bank_account_name=args.bank_account,
            income_account_name=args.income_account,
            expense_account_name=args.expense_account,
            vat_output_account_name=args.vat_output_account,
            vat_input_account_name=args.vat_input_account,
            filter_category=args.category
        )
    except Exception as e:
        print(f"[Error] QIF generation failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
