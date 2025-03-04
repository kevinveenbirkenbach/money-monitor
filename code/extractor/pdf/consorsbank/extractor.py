import re
from code.model.transaction import Transaction
from ..base import PDFExtractor
import yaml
from code.logger import Logger
from code.converter.pdf import PDFConverter
from .dataframe_mapper import ConsorsbankDataframeMapper
from .dataframe import ConsorbankDataFrame
from .text import TextExtractor

class ConsorsbankPDFExtractor(PDFExtractor):
    """Extrahiert Transaktionen aus einem Consorsbank-PDF."""
    
    def __init__(self, source: str, logger: Logger, config: yaml, pdf_converter:PDFConverter):
        super().__init__(source, logger, config, pdf_converter)
        self.previous_balance = None
        self.transactions = None
        textextractor = TextExtractor(self.logger,self.pdf_converter.getLazyFullText())
        dataframe = ConsorbankDataFrame(self.source,self.logger)
        dataframe_mapper = ConsorsbankDataframeMapper(self.logger,self.source,textextractor)
        self.transactions = dataframe_mapper.map_transactions(dataframe.extract_data())
    
    def extract_transactions(self):
        return self.transactions


