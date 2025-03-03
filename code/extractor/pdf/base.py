from ..base import Extractor
from code.converter.pdf import PDFConverter
import yaml
from code.logger import Logger

class PDFExtractor(Extractor):
    def __init__(self, source: str, logger: Logger, config: yaml, pdf_converter:PDFConverter):
        super().__init__(source, logger, config)
        self.pdf_converter = pdf_converter