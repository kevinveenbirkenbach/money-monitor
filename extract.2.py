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

# 1. Aufteilen in Blöcke: Jeder Block beginnt mit einem Transaktionstyp
block_pattern = re.compile(
    r'^(?P<type>LASTSCHRIFT|EURO-UEBERW\.|GUTSCHRIFT)\s*\n'
    r'(?P<block>.*?)(?=^(?:LASTSCHRIFT|EURO-UEBERW\.|GUTSCHRIFT)\s*\n|\Z)',
    re.DOTALL | re.MULTILINE
)

# 2. Detail-Patterns
# Multiline-Pattern (für LASTSCHRIFT, EURO-UEBERW.)
multiline_pattern = re.compile(
    r'(?P<datum>\d{2}\.\d{2}\.)\s+(?P<pnnr>\d{3,4})\s*\n\s*(?P<wert>\d{2}\.\d{2}\.)\s*\n\s*(?P<amount>[\d.,]+[+-])',
    re.MULTILINE
)
# Inline-Pattern (speziell für GUTSCHRIFT, wo alle Felder in einer Zeile stehen können)
inline_pattern = re.compile(
    r'(?P<datum>\d{2}\.\d{2}\.)\s+(?P<pnnr>\d{3,4})\s+(?P<wert>\d{2}\.\d{2}\.)\s+(?P<amount>[\d.,]+[+-])'
)

# Fallback: Falls weder inline noch multiline etwas finden – suche im gesamten Block nach einem typischen Betragsmuster.
fallback_amount_pattern = re.compile(r'(\d{1,3}(?:\.\d{3})*,\d{2}[+-])')

transactions = []

for m_block in block_pattern.finditer(text):
    trans_type = m_block.group('type').strip()
    block = m_block.group('block')
    
    # Für GUTSCHRIFT verwenden wir das inline Pattern; sonst das multiline Pattern.
    if trans_type == "GUTSCHRIFT":
        detail_match = inline_pattern.search(block)
    else:
        detail_match = multiline_pattern.search(block)
    
    if not detail_match:
        # Fallback: Falls kein Detail gefunden wird, suche im Block nach einem Geldbetrag (nur für GUTSCHRIFT)
        if trans_type == "GUTSCHRIFT":
            m_fallback = fallback_amount_pattern.search(block)
            if m_fallback:
                # Setze Datum und Wert als leere Felder, falls nicht vorhanden – oder versuche alternativ zu extrahieren.
                datum = ""
                pnnr = ""
                wert = ""
                amount = m_fallback.group(1).strip()
                detail_match = True  # Signalisiere, dass wir einen Betrag haben.
            else:
                continue
        else:
            continue

    if detail_match is not True:
        datum = detail_match.group('datum').strip()
        pnnr = detail_match.group('pnnr').strip() if detail_match.group('pnnr') else ""
        wert = detail_match.group('wert').strip()
        amount = detail_match.group('amount').strip()
    # Falls wir per Fallback den Betrag gefunden haben, sind Datum, PNNr, Wert ggf. leer.
    if amount:
        if amount.endswith('+'):
            haben = amount
            soll = ""
        elif amount.endswith('-'):
            soll = amount
            haben = ""
        else:
            soll = ""
            haben = ""
    else:
        soll = ""
        haben = ""
    
    # Beschreibung: Alles vor dem Beginn der Detaildaten (falls detail_match vorhanden) oder den gesamten Block (Fallback)
    if detail_match is not True:
        description = block.strip().replace('\n', ' ')
    else:
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
