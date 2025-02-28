import re
import csv
from pdfminer.high_level import extract_text

def parse_amount(s):
    """Wandelt einen Betrag im Format '34.360,45+' oder '50,00+' in einen float um."""
    s = s.strip()
    sign = 1
    if s.endswith('+'):
        sign = 1
    elif s.endswith('-'):
        sign = -1
    s = s[:-1].strip()  # Entferne das Vorzeichenzeichen
    s = s.replace('.', '').replace(',', '.')
    try:
        return sign * float(s)
    except Exception:
        return None

def format_amount(val):
    """Formatiert einen float-Betrag ins deutsche Format, z.B. '50,00+'."""
    if val is None:
        return ""
    s = f"{abs(val):.2f}".replace('.', ',')
    return s + ("+" if val >= 0 else "-")

def convert_to_iso(datum_str, global_year):
    """
    Konvertiert einen Datumseintrag in den ISO-Standard (YYYY-MM-DD).
    Falls datum_str nur im Format "DD.MM." vorliegt, wird das global_year ergänzt.
    Falls ein Jahr vorhanden ist, wird bei zweistelliger Jahreszahl '20' vorangestellt.
    """
    datum_str = datum_str.strip()
    m = re.fullmatch(r'(\d{2})\.(\d{2})\.(\d{2,4})', datum_str)
    if m:
        day, month, year = m.groups()
        if len(year) == 2:
            year = "20" + year
        return f"{year}-{month}-{day}"
    m2 = re.fullmatch(r'(\d{2})\.(\d{2})\.', datum_str)
    if m2 and global_year:
        day, month = m2.groups()
        return f"{global_year}-{month}-{day}"
    return datum_str

# Pfade festlegen
pdf_path = "/home/kevinveenbirkenbach/Documents/institutions/Finanzinstitute/Consorsbank/bank statements/KONTOAUSZUG_GIROKONTO_260337647_dat20220429_id1112239756.pdf"
txt_path = "kontoauszug.txt"
csv_path = "transactions.csv"

print("Extrahiere Text aus der PDF...")
text = extract_text(pdf_path)
with open(txt_path, 'w', encoding='utf-8') as f:
    f.write(text)
print(f"Text wurde in '{txt_path}' gespeichert.")

# Globales Jahr extrahieren aus einem Datum im Text, z.B. "29.04.22"
global_year = None
year_match = re.search(r'\b\d{2}\.\d{2}\.(\d{2,4})\b', text)
if year_match:
    year_str = year_match.group(1)
    if len(year_str) == 2:
        global_year = "20" + year_str
    else:
        global_year = year_str
else:
    global_year = "2022"  # Fallback

# Blockaufteilung: Jeder Block beginnt mit einem bekannten Transaktionstyp.
block_pattern = re.compile(
    r'^(?P<type>LASTSCHRIFT|EURO-UEBERW\.|GUTSCHRIFT)\s*\n'
    r'(?P<block>.*?)(?=^(?:LASTSCHRIFT|EURO-UEBERW\.|GUTSCHRIFT)\s*\n|\Z)',
    re.DOTALL | re.MULTILINE
)

# Für LASTSCHRIFT und EURO‑UEBERW.: Detaildaten in drei Zeilen
detail_pattern = re.compile(
    r'(?P<datum>\d{2}\.\d{2}\.)\s+(?P<pnnr>\d{3,4})\s*\n\s*'
    r'(?P<wert>\d{2}\.\d{2}\.)\s*\n\s*'
    r'(?P<amount>[\d.,]+[+-])',
    re.MULTILINE
)

# Kontostand-Pattern: z. B. "*** Kontostand zum 20.04. *** 34.360,45+"
balance_pattern = re.compile(r'\*\*\*\s*Kontostand zum [^\d]*\s*(?P<balance>[\d.,]+[+-])')

transactions = []
previous_balance = None

for m_block in block_pattern.finditer(text):
    trans_type = m_block.group('type').strip()
    block = m_block.group('block')
    
    if trans_type in {"LASTSCHRIFT", "EURO-UEBERW."}:
        detail_match = detail_pattern.search(block)
        if not detail_match:
            continue
        datum_raw = detail_match.group('datum').strip()
        pnnr = detail_match.group('pnnr').strip() if detail_match.group('pnnr') else ""
        wert_raw = detail_match.group('wert').strip()
        amount_extracted = detail_match.group('amount').strip()
    else:  # GUTSCHRIFT
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        datum_raw, pnnr, wert_raw = "", "", ""
        for idx, line in enumerate(lines):
            m_date = re.match(r'^(\d{2}\.\d{2}\.?\d{0,4})', line)
            if m_date:
                datum_raw = m_date.group(1)
                parts = line.split()
                if len(parts) >= 2 and re.fullmatch(r'\d{3,4}', parts[1]):
                    pnnr = parts[1]
                if idx + 1 < len(lines):
                    m_date2 = re.match(r'^(\d{2}\.\d{2}\.?\d{0,4})', lines[idx+1])
                    if m_date2:
                        wert_raw = m_date2.group(1)
                break
        amount_extracted = ""
    
    # Datum in ISO-Format konvertieren
    datum_iso = convert_to_iso(datum_raw, global_year) if datum_raw else ""
    wert_iso = convert_to_iso(wert_raw, global_year) if wert_raw else ""
    
    # Kontostand im Block ermitteln
    current_balance = None
    balance_match = balance_pattern.search(block)
    if balance_match:
        current_balance = parse_amount(balance_match.group('balance'))
    
    # Für GUTSCHRIFT: Falls kein Betrag vorliegt, berechne ihn als Differenz
    if trans_type == "GUTSCHRIFT" and (amount_extracted == "" or parse_amount(amount_extracted) is None):
        if previous_balance is not None and current_balance is not None:
            diff = current_balance - previous_balance
            amount_extracted = format_amount(diff)
        else:
            amount_extracted = ""
    
    if amount_extracted.endswith('+'):
        haben = amount_extracted
        soll = ""
    elif amount_extracted.endswith('-'):
        soll = amount_extracted
        haben = ""
    else:
        soll = ""
        haben = ""
    
    if trans_type in {"LASTSCHRIFT", "EURO-UEBERW."} and detail_pattern.search(block):
        description = block[:detail_pattern.search(block).start()].strip().replace('\n', ' ')
    else:
        description = block.strip().replace('\n', ' ')
    
    transactions.append({
        'Type': trans_type,
        'Datum': datum_iso,
        'PNNr': pnnr,
        'Wert': wert_iso,
        'Soll': soll,
        'Haben': haben,
        'Beschreibung': description
    })
    
    if current_balance is not None:
        previous_balance = current_balance

with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['Type', 'Datum', 'PNNr', 'Wert', 'Soll', 'Haben', 'Beschreibung']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for trans in transactions:
        writer.writerow(trans)

print(f"CSV-Datei '{csv_path}' wurde erstellt mit {len(transactions)} Transaktion(en).")
