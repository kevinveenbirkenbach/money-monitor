import os
from pdfminer.high_level import extract_text, extract_pages
from pdfminer.layout import LTTextContainer, LTChar
from code.logger import Logger

class PDFConverter:
    def __init__(self, logger: Logger, pdf_path: str):
        self.pdf_path = pdf_path
        self.logger = logger

    def getText(self, maxpages=0) -> str:
        """Extrahiert den Text aus dem gesamten PDF oder einer begrenzten Anzahl von Seiten."""
        try:
            text = extract_text(pdf_file=self.pdf_path, maxpages=maxpages)
            if self.logger.debug_enabled:
                self.logger.debug(f"File '{self.pdf_path}' converts to:\n{text}")
            return text
        except Exception as e:
            self.logger.warning(f"Could not extract text from '{self.pdf_path}'. Reason: {e}")
            return None

    def getFirstPage(self):
        """Extrahiert den Text der ersten Seite."""
        return self.getText(maxpages=1)

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

            if self.logger.debug_enabled:
                self.logger.debug(f"Structured data for '{self.pdf_path}': {structured_data}")

            return structured_data

        except Exception as e:
            self.logger.warning(f"Could not extract structured data from '{self.pdf_path}'. Reason: {e}")
            return None
