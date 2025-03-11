from code.extractor.abstract import AbstractExtractor
from code.converter.pdf import PDFConverter
from code.model.log import Log
from code.model.configuration import Configuration

class AbstractPDFExtractor(AbstractExtractor):
    def __init__(self, source: str, log: Log, configuration:Configuration, pdf_converter:PDFConverter):
        super().__init__(source, log, configuration)
        self.pdf_converter = pdf_converter