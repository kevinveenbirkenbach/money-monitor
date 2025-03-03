import re
from .date_parser import DateParser
from code.model.transaction import Transaction

class TransactionParser:
    """Parses transaction details from a block."""
    
    @staticmethod
    def parse_transaction_details(block, trans_type, global_year, transaction:Transaction):
        """Extracts details from a transaction block."""
        
        # Debug: Output the first 100 characters of the block for inspection
        print(f"Parsing block: {block[:100]}...")  # Only the first 100 characters for preview

        # Extract the first line of the block as the receiver
        first_line = block.splitlines()[0].strip()  # Get the first line
        transaction.partner.name = first_line

        # Extract the date and amount
        if trans_type in {"LASTSCHRIFT", "EURO-UEBERW."}:
            detail_pattern = re.compile(
                r'(?P<datum>\d{2}\.\d{2}\.)\s+(?P<pnnr>\d{3,4})\s*\n\s*'
                r'(?P<wert>\d{2}\.\d{2}\.)\s*\n\s*'
                r'(?P<amount>[\d.,]+[+-])',
                re.MULTILINE
            )
            detail_match = detail_pattern.search(block)
            if not detail_match:
                return None, "", "", ""
            datum_raw = detail_match.group('datum').strip()
            wert_raw = detail_match.group('wert').strip()
            amount_extracted = detail_match.group('amount').strip()
            datum_iso = DateParser.convert_to_iso(datum_raw, global_year) if datum_raw else ""
            return datum_raw, wert_raw, amount_extracted, datum_iso
        
        # If no transaction type is found
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        datum_raw, wert_raw, amount_extracted = "", "", ""
        for idx, line in enumerate(lines):
            m_date = re.match(r'^(\d{2}\.\d{2}\.?\d{0,4})', line)
            if m_date:
                datum_raw = m_date.group(1)
                if idx + 1 < len(lines):
                    m_date2 = re.match(r'^(\d{2}\.\d{2}\.?\d{0,4})', lines[idx+1])
                    if m_date2:
                        wert_raw = m_date2.group(1)
                break
        return datum_raw, wert_raw, amount_extracted, ""
