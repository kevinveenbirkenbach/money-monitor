import pdfplumber
import pandas as pd

def extract_kontoauszug(pdf_path):
    # Erwartete Spaltennamen in der Kopfzeile
    # (so wie sie ungefähr im PDF stehen)
    expected_headers = ["Text/Verwendungszweck", "Datum", "PNNr", "Wert", "Soll", "Haben"]

    with pdfplumber.open(pdf_path) as pdf:
        # ---- 1) Header-Informationen von der ersten Seite ermitteln ----
        page = pdf.pages[0]
        words = page.extract_words()

        # Dictionary für gefundene Spalten: {spaltenname: (x0, x1)}
        found_columns = {}

        # Suchschleife: wir gleichen jedes Wort mit unseren erwarteten Headers ab
        for w in words:
            text = w["text"].strip()
            if text in expected_headers:
                found_columns[text] = (w["x0"], w["x1"])

        # Falls nicht alle Header gefunden wurden -> ggf. abbrechen oder Warnung
        missing_headers = [h for h in expected_headers if h not in found_columns]
        if missing_headers:
            print(f"Warnung: Nicht alle erwarteten Header gefunden: {missing_headers}")
            # Hier ggf. return oder fallback-Logik

        # ---- 2) Spalten sortieren & Grenzen definieren ----
        # Wir sortieren nach x0, damit die Reihenfolge stimmt
        sorted_cols = sorted(found_columns.items(), key=lambda x: x[1][0])
        # Example: [('Text/Verwendungszweck', (10, 70)), ('Datum', (80, 100)), ...]

        # Spalten-Grenzen so definieren, dass sie sich nicht überschneiden.
        # Wir nehmen jeweils die Mitte zwischen x1 (Spalte i) und x0 (Spalte i+1)
        columns_boundaries = {}
        for i in range(len(sorted_cols)):
            col_name, (col_x0, col_x1) = sorted_cols[i]

            # Wenn es eine "nächste" Spalte gibt, Grenze dazwischen
            if i < len(sorted_cols) - 1:
                next_col_name, (next_col_x0, next_col_x1) = sorted_cols[i+1]
                boundary = (col_x1 + next_col_x0) / 2
                columns_boundaries[col_name] = (col_x0, boundary)
            else:
                # Letzte Spalte: Wir geben ihr einen "großen" Bereich
                columns_boundaries[col_name] = (col_x0, col_x1 + 1000)

        # ---- 3) Alle Seiten durchgehen & Wörter zuordnen ----
        all_rows = []
        for page in pdf.pages:
            words = page.extract_words()
            # Temporäre Struktur, um Zeilen & Spalten zu sammeln
            rows = {}

            for w in words:
                x_left = w["x0"]
                x_right = w["x1"]
                top = w["top"]

                # Einfaches Beispiel für Zeilen-ID: runde "top" etwas ab
                row_key = int(round(top / 5.0))

                # Finde passende Spalte
                assigned = False
                for col_name, (col_min, col_max) in columns_boundaries.items():
                    if (x_left >= col_min) and (x_right <= col_max):
                        if row_key not in rows:
                            # Zeile initialisieren
                            rows[row_key] = {c: "" for c in columns_boundaries.keys()}
                        # Text anhängen
                        rows[row_key][col_name] += w["text"] + " "
                        assigned = True
                        break

                # Falls assigned = False, liegt das Wort evtl. außerhalb der erwarteten Spalten
                # -> je nach Bedarf ignorieren oder in "Rest"-Spalte packen

            # Sortiere Zeilen nach row_key
            sorted_rows = sorted(rows.items(), key=lambda x: x[0])
            data = [r[1] for r in sorted_rows]
            all_rows.extend(data)

        # ---- 4) DataFrame bauen ----
        df = pd.DataFrame(all_rows)
        return df