import re
import csv
from pdfminer.high_level import extract_text

# Pfade festlegen
pdf_path = '/home/kevinveenbirkenbach/Documents/institutions/Finanzinstitute/Consorsbank/bank statements/KONTOAUSZUG_GIROKONTO_260337647_dat20220429_id1112239756.pdf'
txt_path = 'kontoauszug.txt'
csv_path = 'transactions.csv'

print("Extrahiere Text aus der PDF...")
text = extract_text(pdf_path)
with open(txt_path, 'w', encoding='utf-8') as f:
    f.write(text)
print(f"Text wurde in '{txt_path}' gespeichert.")

# Zuerst teilen wir den Text in Blöcke auf – jeder Block beginnt mit einem Transaktionstyp.
# Wir gehen davon aus, dass der Typ (LASTSCHRIFT, EURO-UEBERW. oder GUTSCHRIFT) in einer eigenen Zeile steht.
block_pattern = re.compile(
    r'^(?P<type>LASTSCHRIFT|EURO-UEBERW\.|GUTSCHRIFT)\s*\n'
    r'(?P<block>.*?)(?=^(?:LASTSCHRIFT|EURO-UEBERW\.|GUTSCHRIFT)\s*\n|\Z)',
    re.DOTALL | re.MULTILINE
)

# Detailfelder: Erwartet werden in der Regel drei Zeilen:
# 1. Buchungsdatum und PNNr (z. B. "01.04. 8420")
# 2. Wertdatum (z. B. "01.04.")
# 3. Betrag (z. B. "7.291,73+") – dieser Teil ist jetzt optional.
detail_pattern = re.compile(
    r'(?P<datum>\d{2}\.\d{2}\.)\s+(?P<pnnr>\d{3,4})\s*\n'
    r'\s*(?P<wert>\d{2}\.\d{2}\.)\s*\n'
    r'\s*(?P<amount>[\d.,]+[+-])?',
    re.MULTILINE
)
# Fallback‑Pattern, falls die Felder ohne Zeilenumbruch zusammengeführt sind:
detail_pattern_merged = re.compile(
    r'(?P<datum>\d{2}\.\d{2}\.)(?P<pnnr>\d{3,4})?(?P<wert>\d{2}\.\d{2}\.)(?P<amount>[\d.,]+[+-])?'
)

transactions = []

for m_block in block_pattern.finditer(text):
    trans_type = m_block.group('type').strip()
    block = m_block.group('block')
    # Suche in diesem Block nach den Detailfeldern.
    detail_match = detail_pattern.search(block)
    if not detail_match:
        detail_match = detail_pattern_merged.search(block)
    if not detail_match:
        continue

    datum = detail_match.group('datum').strip()
    pnnr = detail_match.group('pnnr').strip() if detail_match.group('pnnr') else ""
    wert = detail_match.group('wert').strip()
    amount = detail_match.group('amount')
    amount = amount.strip() if amount else ""
    
    if amount.endswith('+'):
        haben = amount
        soll = ""
    elif amount.endswith('-'):
        soll = amount
        haben = ""
    else:
        soll = ""
        haben = ""
    
    # Die Beschreibung ist alles, was vor dem Beginn der Detailfelder im Block steht.
    description = block[:detail_match.start()].strip().replace('\n', ' ')
    
    transactions.append({
        'Type': trans_type,
        'Datum': datum,
        'PNNr': pnnr,
        'Wert': wert,
        'Soll': soll,
        'Haben': haben,
        'Beschreibung': description
    })

with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['Type', 'Datum', 'PNNr', 'Wert', 'Soll', 'Haben', 'Beschreibung']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for trans in transactions:
        writer.writerow(trans)

print(f"CSV-Datei '{csv_path}' wurde erstellt mit {len(transactions)} Transaktion(en).")
