# File: tests/test_qif_mapper.py

import os
import tempfile
import unittest
from decimal import Decimal
from code.mapper.qif_mapper import parse_amount_german, parse_date_to_qif, build_qif_from_csv

class TestQifMapper(unittest.TestCase):
    def test_parse_amount_german_positive(self):
        self.assertEqual(parse_amount_german("6.664,00"), Decimal("6664.00"))
        self.assertEqual(parse_amount_german("150,50"), Decimal("150.50"))
        self.assertEqual(parse_amount_german("0,00"), Decimal("0.00"))

    def test_parse_amount_german_negative_suffix(self):
        self.assertEqual(parse_amount_german("150,00-"), Decimal("-150.00"))
        self.assertEqual(parse_amount_german("1.234,56-"), Decimal("-1234.56"))

    def test_parse_amount_german_negative_prefix(self):
        self.assertEqual(parse_amount_german("-150,00"), Decimal("-150.00"))
        self.assertEqual(parse_amount_german("-1.234,56"), Decimal("-1234.56"))

    def test_parse_amount_german_malformed(self):
        # Malformed string should default to 0.00
        self.assertEqual(parse_amount_german("not a number"), Decimal("0.00"))
        self.assertEqual(parse_amount_german(""), Decimal("0.00"))

    def test_parse_date_to_qif_yyyy_mm_dd(self):
        self.assertEqual(parse_date_to_qif("2023-01-09"), "01/09/2023")
        self.assertEqual(parse_date_to_qif("2023-12-31"), "12/31/2023")

    def test_parse_date_to_qif_dd_mm_yyyy(self):
        self.assertEqual(parse_date_to_qif("09.01.2023"), "01/09/2023")
        self.assertEqual(parse_date_to_qif("31.12.2023"), "12/31/2023")

    def test_parse_date_to_qif_invalid(self):
        with self.assertRaises(ValueError):
            parse_date_to_qif("20230109")
        with self.assertRaises(ValueError):
            parse_date_to_qif("09-01-2023")

    def test_build_qif_from_csv_basic(self):
        # Create a temporary CSV file with two rows (one income, one expense)
        csv_content = (
            "id,date,brutto value,currency,sender,description,Kategorie,netto value,Vat value\n"
            "TID1,2023-01-09,6664,EUR,diconium digital,Invoice 0001,Betriebseinnahmen,5600,1064\n"
            "TID2,2023-02-15,-200,EUR,Office Depot,Stationery,Bürobedarf,168,32\n"
        )
        tmp_csv = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        tmp_csv.write(csv_content.encode("utf-8"))
        tmp_csv.close()

        # Prepare output QIF path
        tmp_qif = tempfile.NamedTemporaryFile(delete=False, suffix=".qif")
        tmp_qif.close()

        # Build QIF for all categories (no filter)
        build_qif_from_csv(
            input_csv=tmp_csv.name,
            output_qif=tmp_qif.name,
            bank_account_name="Assets:Bank:Consorsbank",
            income_account_name="Income:Sales",
            expense_account_name="Expenses:Office Supplies",
            vat_output_account_name="Liabilities:VAT Output 19%",
            vat_input_account_name="Assets:VAT Input 19%",
            filter_category=None
        )

        # Read QIF and verify contents
        with open(tmp_qif.name, "r", encoding="utf-8") as f:
            qif_lines = [line.rstrip("\n") for line in f]

        # Expected header lines
        self.assertEqual(qif_lines[0], "!Account")
        self.assertEqual(qif_lines[1], "NAssets:Bank:Consorsbank")
        self.assertEqual(qif_lines[2], "TBank")
        self.assertEqual(qif_lines[3], "^")
        self.assertEqual(qif_lines[5], "!Type:Bank")

        # Check first transaction (income)
        idx_income = qif_lines.index("D01/09/2023")
        self.assertEqual(qif_lines[idx_income + 1], "T6664.00")
        self.assertEqual(qif_lines[idx_income + 2], "Pdiconium digital")
        self.assertEqual(qif_lines[idx_income + 3], "MInvoice 0001")
        self.assertEqual(qif_lines[idx_income + 4], "NTID1")
        # Splits for income: net and VAT
        self.assertEqual(qif_lines[idx_income + 5], "SIncome:Sales")
        self.assertEqual(qif_lines[idx_income + 6], "$-5600.00")
        self.assertEqual(qif_lines[idx_income + 7], "%Net (income)")
        self.assertEqual(qif_lines[idx_income + 8], "SLiabilities:VAT Output 19%")
        self.assertEqual(qif_lines[idx_income + 9], "$-1064.00")
        self.assertEqual(qif_lines[idx_income + 10], "%VAT (output)")
        self.assertEqual(qif_lines[idx_income + 11], "^")

        # Check second transaction (expense)
        idx_expense = qif_lines.index("D02/15/2023")
        self.assertEqual(qif_lines[idx_expense + 1], "T-200.00")
        self.assertEqual(qif_lines[idx_expense + 2], "POffice Depot")
        self.assertEqual(qif_lines[idx_expense + 3], "MStationery")
        self.assertEqual(qif_lines[idx_expense + 4], "NTID2")
        # Splits for expense: net and VAT
        self.assertEqual(qif_lines[idx_expense + 5], "SExpenses:Office Supplies")
        self.assertEqual(qif_lines[idx_expense + 6], "$168.00")
        self.assertEqual(qif_lines[idx_expense + 7], "%Net (expense)")
        self.assertEqual(qif_lines[idx_expense + 8], "SAssets:VAT Input 19%")
        self.assertEqual(qif_lines[idx_expense + 9], "$32.00")
        self.assertEqual(qif_lines[idx_expense + 10], "%VAT (input)")
        self.assertEqual(qif_lines[idx_expense + 11], "^")

        # Clean up temp files
        os.unlink(tmp_csv.name)
        os.unlink(tmp_qif.name)

    def test_build_qif_from_csv_with_category_filter(self):
        # CSV with multiple categories, only one matches filter
        csv_content = (
            "id,date,brutto value,currency,sender,description,Kategorie,netto value,Vat value\n"
            "A,2023-01-01,100,EUR,Payee A,Desc A,Kat1,84,16\n"
            "B,2023-01-02,200,EUR,Payee B,Desc B,Kat2,168,32\n"
        )
        tmp_csv = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        tmp_csv.write(csv_content.encode("utf-8"))
        tmp_csv.close()

        tmp_qif = tempfile.NamedTemporaryFile(delete=False, suffix=".qif")
        tmp_qif.close()

        # Only include rows where Kategorie == "Kat1"
        build_qif_from_csv(
            input_csv=tmp_csv.name,
            output_qif=tmp_qif.name,
            bank_account_name="Assets:Bank:Consorsbank",
            income_account_name="Income:Sales",
            expense_account_name="Expenses:Office Supplies",
            vat_output_account_name="Liabilities:VAT Output 19%",
            vat_input_account_name="Assets:VAT Input 19%",
            filter_category="Kat1"
        )

        with open(tmp_qif.name, "r", encoding="utf-8") as f:
            qif_lines = [line.strip() for line in f if line.strip()]

        # Header should exist
        self.assertIn("!Account", qif_lines)
        self.assertIn("!Type:Bank", qif_lines)

        # There should be exactly one transaction (for "Kat1"), so only one "D01/01/2023"
        self.assertEqual(qif_lines.count("D01/01/2023"), 1)
        self.assertNotIn("D01/02/2023", qif_lines)

        # Cleanup
        os.unlink(tmp_csv.name)
        os.unlink(tmp_qif.name)


if __name__ == "__main__":
    unittest.main()
