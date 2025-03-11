import re
from code.model.transaction import Transaction
from ..abstract import AbstractPDFExtractor
import yaml
from code.model.log import Log
from code.converter.pdf import PDFConverter
from .dataframe_mapper import ConsorsbankDataframeMapper
from .dataframe import ConsorbankDataFrame
from .text import TextExtractor
from code.model.configuration import Configuration

class ConsorsbankPDFExtractor(AbstractPDFExtractor):
    """Extrahiert Transaktionen aus einem Consorsbank-PDF."""
    
    def __init__(self, source: str, log: Log, configuration:Configuration, pdf_converter:PDFConverter):
        super().__init__(source, log, configuration, pdf_converter)
        self.previous_balance = None
        self.transactions = None
        textextractor = TextExtractor(self.log,self.pdf_converter.getLazyFullText())
        dataframe = ConsorbankDataFrame(self.source,self.log)
        dataframe_mapper = ConsorsbankDataframeMapper(self.log,self.source,textextractor)
        self.transactions = dataframe_mapper.map_transactions(dataframe.extract_data())
    
    def extract_transactions(self):
        return self.transactions


