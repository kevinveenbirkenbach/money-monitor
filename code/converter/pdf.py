import os
from pdfminer.high_level import extract_text, extract_pages
from pdfminer.layout import LTTextContainer, LTChar
from code.model.log import Log
import pdfplumber
import pandas

class PDFConverter:
    def __init__(self, log: Log, pdf_path: str):
        self.pdf_path = pdf_path
        self.log = log
        self.pdf = None
        self.full_text = None
        self.pages = None
        self.pages_data_frame=None
    
    def __del__(self):
        if self.pdf:
            self.pdf.close()  
            
    def getLazyPdf(self): 
        if self.pdf:
            return self.pdf
        self.pdf = pdfplumber.open(self.pdf_path)
        return self.pdf 

    def getLazyFullText(self)->str:
        if not self.full_text:
            self.full_text = ""
            pages = self.getLazyPages()
            if pages:
                for page in pages:
                    page_text = page.extract_text() or ""
                    self.full_text += page_text + "\n"
            else:
                return None
        return self.full_text

    def getLazyPages(self)->[]:
        if self.pages:
            return self.pages
        self.pages = self.getLazyPdf().pages or []
        return self.pages

    
    def getPageDataFrame(self,page):
        table = page.extract_table()
        dataframe = pandas.DataFrame(table[1:], columns=table[0])
        return dataframe
    
    def getLazyPagesDataFrame(self):
        if self.pages_data_frame:
            return self.pages_data_frame
        self.pages_data_frame = []  # Initialisierung außerhalb der Schleife
        for page in self.getLazyPages():
            self.pages_data_frame.append(self.getPageDataFrame(page))
        return self.pages_data_frame
        
    def getText(self) -> str:
        """Extrahiert den Text aus dem gesamten PDF oder einer begrenzten Anzahl von Seiten."""
        try:
            text = extract_text(self.pdf_path)
            if self.log.debug_enabled:
                self.log.debug(f"File '{self.pdf_path}' converts to:\n{text}")
            return text
        except Exception as e:
            self.log.warning(f"Could not extract text from '{self.pdf_path}'. Reason: {e}")
            return None

    def getFirstPage(self):
        """Extrahiert den Text der ersten Seite."""
        return extract_text(self.pdf_path,maxpages=1)

    def getStructuredData(self, maxpages=0):
        """Extrahiert strukturierte Daten wie Text und Positionen der Textblöcke."""
        structured_data = []

        try:
            # Extrahiert Layout-Daten
            for page_layout in extract_pages(self.pdf_path, maxpages=maxpages):
                page_data = []
                for element in page_layout:
                    if isinstance(element, LTTextContainer):
                        # Textblock extrahieren und Position ermitteln
                        text = element.get_text()
                        x0, y0, x1, y1 = element.bbox  # Position der Textbox
                        page_data.append({
                            'text': text.strip(),
                            'x0': x0,
                            'y0': y0,
                            'x1': x1,
                            'y1': y1
                        })
                    elif isinstance(element, LTChar):
                        # Extrahiert Details zu einzelnen Zeichen (z.B. Schriftart und -größe)
                        fontname = element.fontname
                        size = element.size
                        text = element.get_text()
                        page_data.append({
                            'text': text.strip(),
                            'fontname': fontname,
                            'size': size,
                            'x0': element.x0,
                            'y0': element.y0
                        })
                
                structured_data.append(page_data)

            if self.log.debug_enabled:
                self.log.debug(f"Structured data for '{self.pdf_path}': {structured_data}")

            return structured_data

        except Exception as e:
            self.log.warning(f"Could not extract structured data from '{self.pdf_path}'. Reason: {e}")
            return None
