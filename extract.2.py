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

# Wir nutzen ein Pattern, um den Text an den Transaktionstypen zu splitten.
# Die Annahme: Die Transaktionstypen stehen jeweils alleine in einer Zeile.
type_pattern = re.compile(r'^(LASTSCHRIFT|EURO-UEBERW\.|GUTSCHRIFT)$', re.MULTILINE)
parts = type_pattern.split(text)
# parts enthält dann: [Header, type1, Segment1, type2, Segment2, ...]

transactions = []

# Standard‑Pattern: erwartet
#   Zeile: Datum (DD.MM.) optional gefolgt von PNNr (3-4 Ziffern)
#   Zeile: Wertdatum (DD.MM.)
#   Zeile: Betrag (Format z. B. 7.291,73+)
detail_pattern = re.compile(
    r'(\d{2}\.\d{2}\.)\s*(\d{3,4})?\s*\n\s*(\d{2}\.\d{2}\.)\s*\n\s*([\d.,]+[+-])',
    re.MULTILINE
)
# Fallback‑Pattern für zusammengeführte Detailzeile (wenn kein Zeilenumbruch zwischen PNNr und Wertdatum vorliegt):
# z. B. "24269/2022/12452513.04.909,43-"
detail_pattern_merged = re.compile(
    r'(\d{2}\.\d{2}\.)\s*(\d{3,4})?(\d{2}\.\d{2}\.)\s*([\d.,]+[+-])'
)

# Iteriere über alle gefundenen Transaktionen.
# parts[0] enthält Headertext, dann folgen Paare: [type, segment]
for i in range(1, len(parts), 2):
    trans_type = parts[i].strip()
    segment = parts[i+1]
    
    # Zunächst: Beschreibung = Text bis zum ersten Auftreten der Detaildaten
    # Wir suchen mit dem Standard‑Pattern:
    m = detail_pattern.search(segment)
    if not m:
        m = detail_pattern_merged.search(segment)
    if not m:
        # Falls in diesem Segment keine Detaildaten gefunden wurden, überspringen
        continue

    datum = m.group(1).strip()
    pnnr = m.group(2).strip() if m.group(2) else ""
    wert = m.group(3).strip()
    amount = m.group(4).strip()
    
    if amount.endswith('+'):
        haben = amount
        soll = ""
    else:
        soll = amount
        haben = ""
    
    # Die Beschreibung nehmen wir als den Text vor m.start() – dabei Zeilenumbrüche durch Leerzeichen ersetzen
    desc = segment[:m.start()].strip().replace('\n', ' ')
    transactions.append({
        'Type': trans_type,
        'Datum': datum,
        'PNNr': pnnr,
        'Wert': wert,
        'Soll': soll,
        'Haben': haben,
        'Beschreibung': desc
    })

with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['Type', 'Datum', 'PNNr', 'Wert', 'Soll', 'Haben', 'Beschreibung']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for trans in transactions:
        writer.writerow(trans)

print(f"CSV-Datei '{csv_path}' wurde erstellt mit {len(transactions)} Transaktion(en).")
