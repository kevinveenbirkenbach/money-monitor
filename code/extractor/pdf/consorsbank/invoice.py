import re
from typing import List, Tuple

def extract_and_remove_invoices(text: str) -> Tuple[List[str], str]:
    """
    1) Finds any of these keywords in 'text':
         - Rechnungsnr.:
         - Rechnungsnummer:
         - Rechnung
         - Rechnungs-Nr.:
       followed by one non-whitespace block (the invoice number).
       
    2) Extracts just the invoice number (the part after the keyword).
    3) Removes the entire matched segment (keyword + invoice number) from the original string.
    
    Returns:
      (invoice_list, new_text)
        - invoice_list: all invoice numbers found (in the order they appear)
        - new_text: the original text with those matches removed
    """

    # Regex to capture the invoice number (group 1),
    # while also matching the entire phrase (keyword + number).
    # We use a look-behind style approach with parentheses around (\\S+),
    # but for removing, we'll do a second pattern that matches the entire chunk.
    pattern_for_extraction = r'(?:Rechnungsnr\.?:|Rechnungsnummer:|Rechnung|Rechnungs-Nr\.?:)\s*(\S+)'

    # 1) Extract all invoice numbers (the part after the keyword).
    invoice_list = re.findall(pattern_for_extraction, text)

    # 2) Remove the entire matched segment (keyword + invoice number).
    #    We just remove everything matched by a slightly simpler pattern
    #    that does not capture groups, but includes the keyword + whitespace + invoice number.
    pattern_for_removal = r'(?:Rechnungsnr\.?:|Rechnungsnummer:|Rechnung|Rechnungs-Nr\.?:)\s*\S+'
    new_text = re.sub(pattern_for_removal, '', text)

    return invoice_list, new_text