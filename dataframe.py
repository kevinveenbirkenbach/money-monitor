import pandas as pd
from code.logger import Logger
from code.extractor.pdf.consorsbank.dataframe import ConsorbankDataFrame

    
#with pdfplumber.open(path) as pdf:
#     for page in pdf.pages:
#         words = page.extract_words()
#         for w in words:
#             print(f"Text: {w['text']} | x0: {w['x0']} | x1: {w['x1']} | top: {w['top']}")
logger = Logger(True)
path = "/home/kevinveenbirkenbach/Documents/institutions/Financial Institutes/Consorsbank/Bank Statements/KONTOAUSZUG_GIROKONTO_260337647_dat20221031_id1169277587.pdf"
c_dataframe = ConsorbankDataFrame(path,logger)
df = c_dataframe.extract_data()
print(df)
df.to_csv("kontoauszug.csv", index=False, encoding="utf-8-sig")