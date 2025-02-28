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

# Regex-Pattern, das alle Transaktionen im Text erfasst.
# Das Pattern:
# • Erfasst den Transaktionstyp (LASTSCHRIFT, EURO-UEBERW. oder GUTSCHRIFT) am Zeilenanfang.
# • Dann wird mit (?P<desc>.*?) der gesamte (möglicherweise mehrzeilige) Beschreibungstext eingefangen,
#   bis die Detailzeile (Buchungsdatum und PNNr) erscheint.
# • Anschließend folgen das Buchungsdatum, die PNNr, das Wertdatum und der Betrag.
pattern = re.compile(
    r'(?P<type>LASTSCHRIFT|EURO-UEBERW\.|GUTSCHRIFT)\s*\n' +
    r'(?P<desc>.*?)' +
    r'(?P<datum>\d{2}\.\d{2}\.)\s+(?P<pnnr>\d{3,4})\s*\n' +
    r'(?P<wert>\d{2}\.\d{2}\.)\s*\n' +
    r'(?P<amount>[\d.,]+[+-])',
    re.DOTALL | re.MULTILINE
)

transactions = []
for m in pattern.finditer(text):
    trans_type = m.group('type').strip()
    # Die Beschreibung kann über mehrere Zeilen gehen – Zeilenumbrüche ersetzen wir durch ein Leerzeichen
    desc = m.group('desc').strip().replace('\n', ' ')
    datum = m.group('datum').strip()
    pnnr = m.group('pnnr').strip()
    wert = m.group('wert').strip()
    amount = m.group('amount').strip()
    # Betrag in Haben oder Soll einsortieren (Plus → Haben, Minus → Soll)
    if amount.endswith('+'):
        haben = amount
        soll = ""
    else:
        soll = amount
        haben = ""
    
    transactions.append({
        'Type': trans_type,
        'Datum': datum,
        'PNNr': pnnr,
        'Wert': wert,
        'Soll': soll,
        'Haben': haben,
        'Beschreibung': desc
    })

# Schreibe die extrahierten Transaktionen in eine CSV-Datei
with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['Type', 'Datum', 'PNNr', 'Wert', 'Soll', 'Haben', 'Beschreibung']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for trans in transactions:
        writer.writerow(trans)

print(f"CSV-Datei '{csv_path}' wurde erstellt mit {len(transactions)} Transaktion(en).")
