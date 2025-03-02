import os
from ..logger import Logger

class Exporter:
    def __init__(self, transactions, output_file, logger=Logger(), quiet=False):
        self.transactions = sorted(transactions, key=lambda t: t.transaction_date)
        self.output_file = output_file
        self.logger = logger

    def get_data_as_dicts(self):
        return [
            t.getDictionary() for t in self.transactions
        ]