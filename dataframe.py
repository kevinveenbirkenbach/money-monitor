from code.extractor.pdf.consorsbank.dataframe import extract_kontoauszug
import pandas as pd

df=extract_kontoauszug("/home/kevinveenbirkenbach/Documents/institutions/Financial Institutes/Consorsbank/Bank Statements/KONTOAUSZUG_GIROKONTO_260337647_dat20221031_id1169277587.pdf")
print(df)
df.to_csv("kontoauszug.csv", index=False, encoding="utf-8-sig")