import pdfplumber
import pandas as pd

def extract_kontoauszug(pdf_path):
    """
    Liest das PDF ein und erzeugt einen DataFrame,
    bei dem jede neue Zeile durch einen der folgenden
    Trigger-Texte eingeleitet wird (case-sensitive):
        - '*** Kontostand zum'
        - 'LASTSCHRIFT'
        - 'EURO-UEBERW.'
        - 'GEBUEHREN'

    Die Zuordnung der Wörter zu Spalten erfolgt anhand
    fester X-Koordinaten.
    """
    # 1) Feste Spaltenbereiche laut deiner Debug-Ausgabe:
    columns = {
        "Text/Verwendungszweck": (46.2, 153.204),
        "Datum": (233.1, 261.101),
        "PNNr": (272.75, 295.251),
        "Wert": (311.55, 331.547),
        "Soll": (433.45, 449.952),
        "Haben": (521.6, 549.099)
    }

    # 2) Trigger-Wörter (case-sensitive) für einen Zeilenumbruch
    triggers = ["*** Kontostand zum", "LASTSCHRIFT", "EURO-UEBERW.", "GEBUEHREN", "DAUERAUFTRAG", "GUTSCHRIFT"]

    # Hier sammeln wir alle Zeilen
    rows = []
    # Die aktuelle Zeile (Dictionary mit Spalten)
    current_row = None

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # words ist eine Liste von Dictionaries mit Koordinaten und Text
            words = page.extract_words()

            for w in words:
                text = w["text"].strip()
                x_left = w["x0"]
                x_right = w["x1"]

                # (A) Prüfen, ob dieses Wort einer der Trigger ist
                if text in triggers:
                    # 1) Falls schon eine Zeile existiert, beenden wir sie
                    if current_row:
                        rows.append(current_row)
                    # 2) Neue Zeile anlegen
                    current_row = {col: "" for col in columns.keys()}
                    # Optional: Trigger direkt in die Spalte "Text/Verwendungszweck" schreiben
                    # (falls du das möchtest und es immer dort hingehört)
                    # current_row["Text/Verwendungszweck"] = text + " "
                    #
                    # An dieser Stelle geht es direkt weiter zur nächsten Word-Schleife
                    # *ohne* nochmal unten die Spaltenzuordnung zu durchlaufen.
                    # Wenn du es lieber in die Spalte per Koordinate packen willst,
                    # nimm kein 'continue'.
                    # 
                    # Hier machen wir NICHT continue, damit pdfplumbers x-Koordinate
                    # ggf. auch eine andere Spalte treffen kann, falls gewünscht.

                # (B) Wenn wir eine aktive Zeile haben, verteilen wir die Wörter
                if current_row:
                    assigned = False
                    for col_name, (col_min, col_max) in columns.items():
                        if x_left >= col_min and x_right <= col_max:
                            current_row[col_name] += text + " "
                            assigned = True
                            break
                    # Falls nichts passt, ignorieren wir das Wort
                    # (oder du definierst eine "Rest"-Spalte)

        # Am Ende der letzten Seite noch die letzte Zeile abschließen
        if current_row:
            rows.append(current_row)

    # 3) DataFrame bauen
    df = pd.DataFrame(rows)
    return df
