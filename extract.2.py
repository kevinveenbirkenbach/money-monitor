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

# Wir splitten den gesamten Text an den Kontostand-Markern, die das Ende eines Transaktionsblocks anzeigen.
blocks = re.split(r'\*\*\*\s*Kontostand.*', text)

# Bekannte Transaktionstypen (diese Liste ggf. erweitern)
transaction_types = {"LASTSCHRIFT", "EURO-UEBERW.", "GUTSCHRIFT"}

transactions = []

# Regex-Muster für die Detailzeile: z. B. "01.04. 8420"
detail_pattern = re.compile(r'^(\d{2}\.\d{2}\.)\s+(\d{3,4})$')
# Regex für das Wertdatum (z.B. "01.04.") – wir erlauben auch Leerzeichen
wert_pattern = re.compile(r'^(\d{2}\.\d{2}\.)$')
# Regex für den Betrag (z.B. "7.291,73+")
amount_pattern = re.compile(r'^([\d.,]+)([+-])$')

for block in blocks:
    # Blockzeilen bereinigen
    lines = [line.strip() for line in block.splitlines() if line.strip()]
    if not lines:
        continue

    # Suche nach einem bekannten Transaktionstyp in diesem Block
    trans_type = None
    type_index = None
    for idx, line in enumerate(lines):
        if line in transaction_types:
            trans_type = line
            type_index = idx
            break
    if trans_type is None:
        continue

    # Ab Zeile nach dem Typ sammeln wir Beschreibungszeilen, bis wir auf eine Detailzeile stoßen
    desc_lines = []
    detail_index = None
    datum = ""
    pnnr = ""
    for j in range(type_index + 1, len(lines)):
        # Überspringe gängige Labels
        if lines[j] in {"Text/Verwendungszweck", "Datum PNNr Wert", "Soll", "Haben"}:
            continue
        m_detail = detail_pattern.match(lines[j])
        if m_detail:
            datum = m_detail.group(1)
            pnnr = m_detail.group(2)
            detail_index = j
            break
        else:
            desc_lines.append(lines[j])
    if detail_index is None:
        continue

    # Nach der Detailzeile erwarten wir das Wertdatum. Falls vorhanden, darf es z. B. "01.04." sein.
    wert = ""
    if detail_index + 1 < len(lines):
        if wert_pattern.match(lines[detail_index + 1]):
            wert = lines[detail_index + 1]
        else:
            # Auch wenn es nicht exakt passt, nehmen wir die Zeile als Wertdatum
            wert = lines[detail_index + 1]

    # Danach suchen wir in den folgenden Zeilen nach einem Betrag
    amount = ""
    amount_index = None
    for k in range(detail_index + 2, len(lines)):
        m_amount = amount_pattern.match(lines[k])
        if m_amount:
            amount = m_amount.group(1) + m_amount.group(2)
            amount_index = k
            break
    if not amount:
        continue

    # Betrag zuordnen: Bei Plus in Haben, bei Minus in Soll
    if amount.endswith('+'):
        haben = amount
        soll = ""
    else:
        soll = amount
        haben = ""

    # Die Beschreibung setzen wir aus den gesammelten Zeilen zusammen.
    description = " ".join(desc_lines)

    transactions.append({
        'Type': trans_type,
        'Datum': datum,
        'PNNr': pnnr,
        'Wert': wert,
        'Soll': soll,
        'Haben': haben,
        'Beschreibung': description
    })

# Schreibe die extrahierten Transaktionen in eine CSV-Datei
with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['Type', 'Datum', 'PNNr', 'Wert', 'Soll', 'Haben', 'Beschreibung']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for trans in transactions:
        writer.writerow(trans)

print(f"CSV-Datei '{csv_path}' wurde erstellt mit {len(transactions)} Transaktion(en).")
