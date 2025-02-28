import re
import csv
from pdfminer.high_level import extract_text

# Pfade festlegen
pdf_path = '/home/kevinveenbirkenbach/Documents/institutions/Finanzinstitute/Consorsbank/bank statements/KONTOAUSZUG_GIROKONTO_260337647_dat20220429_id1112239756.pdf'
txt_path = 'kontoauszug.txt'
csv_path = 'transactions.csv'

# 1. PDF in Text umwandeln und als Textdatei speichern
print("Extrahiere Text aus der PDF...")
text = extract_text(pdf_path)
with open(txt_path, 'w', encoding='utf-8') as f:
    f.write(text)
print(f"Text wurde in '{txt_path}' gespeichert.")

# 2. Zeilenweises Parsen des Textes mit einem einfachen Zustandsautomaten
transactions = []
lines = text.splitlines()

# Liste bekannter Transaktionstypen (diese können ggf. ergänzt werden)
transaction_types = {"LASTSCHRIFT", "EURO-UEBERW.", "GUTSCHRIFT"}

i = 0
while i < len(lines):
    line = lines[i].strip()
    # Überspringe leere Zeilen und Überschriften/Trennzeilen (z. B. "*** Kontostand", "Kontoauszug", etc.)
    if not line or line.startswith('***') or line.startswith('Kontoauszug'):
        i += 1
        continue

    # Prüfe, ob diese Zeile ein bekannter Transaktionstyp ist
    if line in transaction_types:
        trans_type = line
        i += 1

        # Sammle Beschreibungszeilen (alle Zeilen bis zur ersten Zeile, die mit Datum beginnt)
        description_lines = []
        while i < len(lines):
            current = lines[i].strip()
            # Überspringe Labels, die nicht zur Beschreibung gehören
            if current in {"Text/Verwendungszweck", "Datum PNNr Wert", "Soll", "Haben"}:
                i += 1
                continue
            # Wenn die Zeile mit einem Datum beginnt (Format DD.MM.), beenden wir die Beschreibung
            if re.match(r'^\d{2}\.\d{2}\.', current):
                break
            description_lines.append(current)
            i += 1

        # Nun erwarten wir die Detailzeile mit Datum und eventuell PNNr
        datum = ""
        pnnr = ""
        if i < len(lines):
            m = re.match(r'^(\d{2}\.\d{2}\.)(?:\s+(\d{3,4}))?$', lines[i].strip())
            if m:
                datum = m.group(1)
                pnnr = m.group(2) if m.group(2) else ""
            i += 1

        # Nächste Zeile: Wertdatum
        wert = ""
        if i < len(lines):
            wert = lines[i].strip()
            i += 1

        # Überspringe ggf. Labelzeilen "Soll" oder "Haben"
        while i < len(lines) and lines[i].strip() in {"Soll", "Haben"}:
            i += 1

        # Nächste Zeile: Betrag
        soll = ""
        haben = ""
        if i < len(lines):
            amount_line = lines[i].strip()
            m_amount = re.match(r'^([\d.,]+)([+-])$', amount_line)
            if m_amount:
                amount = m_amount.group(1) + m_amount.group(2)
                if amount.endswith('+'):
                    haben = amount
                else:
                    soll = amount
            i += 1

        # Erstelle das Transaktions-Dictionary
        transactions.append({
            'Type': trans_type,
            'Datum': datum,
            'PNNr': pnnr,
            'Wert': wert,
            'Soll': soll,
            'Haben': haben,
            'Beschreibung': " ".join(description_lines)
        })
    else:
        i += 1

# 3. Speichere die Transaktionen in eine CSV-Datei
with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['Type', 'Datum', 'PNNr', 'Wert', 'Soll', 'Haben', 'Beschreibung']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for trans in transactions:
        writer.writerow(trans)

print(f"CSV-Datei '{csv_path}' wurde erstellt mit {len(transactions)} Transaktion(en).")
