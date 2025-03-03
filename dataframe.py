from code.extractor.pdf.consorsbank.dataframe import extract_kontoauszug
import pandas as pd

import pdfplumber

def shift_trigger_columns(df):
    triggers = ["*** Kontostand zum", "LASTSCHRIFT", "EURO-UEBERW.", "GEBUEHREN"]
    cols_to_shift = ["Datum", "PNNr", "Wert", "Soll", "Haben"]

    def is_trigger_in_text(text):
        for t in triggers:
            if t in text:
                return True
        return False

    for i in range(len(df) - 1):
        if is_trigger_in_text(str(df.loc[i, "Text/Verwendungszweck"])):
            # Verschiebe Spalten von Zeile i -> i+1
            for col in cols_to_shift:
                df.loc[i+1, col] = (str(df.loc[i+1, col]) + " " + str(df.loc[i, col])).strip()
                df.loc[i, col] = ""
    return df
    
path = "/home/kevinveenbirkenbach/Documents/institutions/Financial Institutes/Consorsbank/Bank Statements/KONTOAUSZUG_GIROKONTO_260337647_dat20221031_id1169277587.pdf"
    
with pdfplumber.open(path) as pdf:
     for page in pdf.pages:
         words = page.extract_words()
         for w in words:
             print(f"Text: {w['text']} | x0: {w['x0']} | x1: {w['x1']} | top: {w['top']}")

df=extract_kontoauszug(path)
print(df)
print(shift_trigger_columns(df))

df.to_csv("kontoauszug.csv", index=False, encoding="utf-8-sig")