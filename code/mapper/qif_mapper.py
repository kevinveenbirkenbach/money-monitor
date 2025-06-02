# File: code/mapper/qif_mapper.py

import csv
import sys
from decimal import Decimal
from datetime import datetime


def parse_amount_german(s: str) -> Decimal:
    """
    Convert a German-format amount string like "6.664,00" or "150,00-"
    into a Decimal. A trailing or leading "-" indicates a negative value.
    """
    t = s.strip()
    if not t:
        return Decimal("0.00")
    negative = False
    if t.endswith("-"):
        negative = True
        t = t[:-1].strip()
    elif t.startswith("-"):
        negative = True
        t = t[1:].strip()
    # Remove thousands separator and replace decimal comma with dot
    t = t.replace(".", "").replace(",", ".")
    try:
        val = Decimal(t)
    except Exception:
        val = Decimal("0.00")
    return -val if negative else val


def parse_date_to_qif(date_str: str) -> str:
    """
    Parse a date string in "YYYY-MM-DD" or "DD.MM.YYYY" format
    and return it in "MM/DD/YYYY" for QIF.
    """
    s = date_str.strip()
    for fmt in ("%Y-%m-%d", "%d.%m.%Y"):
        try:
            dt = datetime.strptime(s, fmt)
            return dt.strftime("%m/%d/%Y")
        except ValueError:
            pass
    raise ValueError(f"Could not parse date '{s}'")


def build_qif_from_csv(
    input_csv: str,
    output_qif: str,
    bank_account_name: str,
    income_account_name: str,
    expense_account_name: str,
    vat_output_account_name: str,
    vat_input_account_name: str,
    filter_category: str = None
):
    """
    Read a flat CSV and write a QIF file with splits manually.

    Optionally filter by the 'Kategorie' column: only process rows where
    'Kategorie' equals filter_category.

    Each CSV row must contain at least these columns:
      - id
      - date
      - brutto value
      - netto value
      - Vat value
      - sender (or partner_name)
      - description
      - Kategorie

    Splitting logic:
      * If brutto > 0 (income):
          - Top-level transaction amount = +brutto (bank deposit)
          - Split1: income_account_name with amount = -netto  (credit to income)
          - Split2: vat_output_account_name with amount = -vatAmt  (credit to VAT liability)
      * If brutto < 0 (expense):
          - Top-level transaction amount = -abs(brutto) (bank withdrawal)
          - Split1: expense_account_name with amount = +abs(netto)  (debit to expense)
          - Split2: vat_input_account_name with amount = +abs(vatAmt)  (debit to VAT asset)
      The sum of split amounts must match the top-level transaction amount.
    """

    # 1) Read CSV rows into a list of dictionaries
    try:
        with open(input_csv, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=",")
            rows = list(reader)
    except Exception as e:
        print(f"[Error] Could not read CSV: {e}", file=sys.stderr)
        return

    # 2) Prepare QIF lines
    lines = []

    # Write the account header for a Bank register
    lines.append("!Account")
    lines.append(f"N{bank_account_name}")
    lines.append("TBank")
    lines.append("^")            # <-- terminate the account header section
    lines.append("")             # blank line before transactions
    lines.append("!Type:Bank")

    for row in rows:
        # If a category filter is provided, skip rows that don't match exactly
        if filter_category is not None:
            kat = row.get("category", "").strip()
            if kat != filter_category:
                continue

        try:
            fitid = row.get("id", "").strip()
            qif_date = parse_date_to_qif(row.get("date", "").strip())
            bruto = parse_amount_german(row.get("brutto value", "").replace("€", "").strip())
            netto = parse_amount_german(row.get("netto value", "").replace("€", "").strip())
            vatAmt = parse_amount_german(row.get("Vat value", "").replace("€", "").strip())
        except Exception as e:
            print(f"[Warning] Skipping row due to parse error: {e}", file=sys.stderr)
            continue

        payee = row.get("sender", "").strip() or row.get("partner_name", "").strip() or ""
        memo = row.get("description", "").strip()

        is_expense = (bruto < 0)
        tx_amount_str = f"{bruto:.2f}"

        # Write top-level transaction header
        lines.append(f"D{qif_date}")       # Date line
        lines.append(f"T{tx_amount_str}")  # Amount line
        if payee:
            lines.append(f"P{payee}")      # Payee/Payor
        if memo:
            lines.append(f"M{memo}")       # Memo
        if fitid:
            lines.append(f"N{fitid}")      # Check/Number (using transaction ID)

        if is_expense:
            # EXPENSE: bruto is negative
            # Split1: Expense account (positive, increase)
            split1_amt = f"{abs(netto):.2f}"   # e.g. "126.05"
            # Split2: VAT Input account (positive, increase)
            split2_amt = f"{abs(vatAmt):.2f}"  # e.g. "23.95"

            # Write split lines:
            lines.append(f"S{expense_account_name}")       # category for net
            lines.append(f"${split1_amt}")                 # Amount for net
            lines.append(f"%Net (expense)")                 # Memo for net

            lines.append(f"S{vat_input_account_name}")     # category for VAT
            lines.append(f"${split2_amt}")                 # Amount for VAT
            lines.append(f"%VAT (input)")                   # Memo for VAT

        else:
            # INCOME: bruto is positive
            # Split1: Income account (negative, credit)
            split1_amt = f"{-abs(netto):.2f}"   # e.g. "-2000.00"
            # Split2: VAT Output account (negative, credit)
            split2_amt = f"{-abs(vatAmt):.2f}"  # e.g. "-380.00"

            # Write split lines:
            lines.append(f"S{income_account_name}")        # category for net
            lines.append(f"${split1_amt}")                # Amount for net
            lines.append(f"%Net (income)")                 # Memo for net

            lines.append(f"S{vat_output_account_name}")    # category for VAT
            lines.append(f"${split2_amt}")                # Amount for VAT
            lines.append(f"%VAT (output)")                 # Memo for VAT

        # Transaction terminator
        lines.append("^")

    # 3) Write all lines to the QIF file
    try:
        with open(output_qif, "w", encoding="utf-8") as f_out:
            f_out.write("\n".join(lines))
        print(f"[QIFMapper] Created QIF file: {output_qif}")
    except Exception as e:
        print(f"[Error] Could not write QIF: {e}", file=sys.stderr)
