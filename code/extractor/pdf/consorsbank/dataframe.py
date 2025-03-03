import pdfplumber
import pandas as pd

def extract_kontoauszug(pdf_path):
    """
    Liest das PDF ein und erzeugt einen DataFrame, 
    wobei jede Zeile anhand ihrer `top`-Koordinate definiert wird. 
    Keine Trigger-Wörter mehr für Zeilentrennung.
    Die Zuordnung der Wörter zu Spalten erfolgt anhand fester X-Koordinaten.
    """
    margin = 30
    min_top_threshold=10
    columns = {
        "Text/Verwendungszweck": (46.2 -margin, 153.204 +margin),
        "Datum": (233.1 - margin, 261.101 + margin),
        "PNNr": (272.75 - margin, 295.251 + margin),
        "Wert": (311.55 - margin, 331.547 + margin),
        "Soll": (433.45 - margin, 449.952 + margin),
        "Haben": (521.6 - margin, 549.099 + margin)
    }

    rows = []
    current_row = None
    last_top = None  # Hilfsvariable, um Zeilen anhand `top` zu gruppieren

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            words = page.extract_words()

            for w in words:
                text = w["text"].strip()
                x_left = w["x0"]
                x_right = w["x1"]
                top = w["top"]

                if top < min_top_threshold:
                    continue  # Wörter, die oberhalb der Höhe liegen, überspringen

                # Wenn wir eine neue Zeile erkennen, basierend auf dem Unterschied in der `top`-Koordinate
                if last_top is None or abs(last_top - top) > 4:  # Wenn der Unterschied in der Höhe zu groß ist
                    if current_row:
                        rows.append(current_row)
                    current_row = {col: "" for col in columns.keys()}

                # Nun weisen wir das Wort der entsprechenden Spalte zu, basierend auf den X-Koordinaten
                assigned = False
                for col_name, (col_min, col_max) in columns.items():
                    if x_left >= col_min and x_right <= col_max:
                        current_row[col_name] += text + " "
                        assigned = True
                        break
                
                # Wenn das Wort nicht in eine Spalte passt, ignorieren wir es
                if not assigned:
                    continue

                # Speichern der aktuellen `top`-Position für die nächste Zeile
                last_top = top

        # Am Ende der letzten Seite noch die letzte Zeile abschließen
        if current_row:
            rows.append(current_row)

    df = pd.DataFrame(rows)
    return df
