import os
from pdfminer.high_level import extract_text
from code.logger import Logger

class PDFConverter:
    def __init__(self, logger: Logger, pdf_path:str):
        self.pdf_path  = pdf_path
        self.logger     = logger
            
    def getText(self,maxpages=0)->str:
        try:
            text = extract_text(pdf_file=self.pdf_path, maxpages=maxpages)
            if self.logger.debug_enabled:
                self.logger.debug(f"File '{self.pdf_path}' converts to:\n{text}")
            return text
        except Exception as e:
            self.logger.warning(f"Could not extract text from '{self.pdf_path}'. Reason: {e}")
            return None
    
    def getFirstPage(self):
        return self.getText(maxpages=1)
