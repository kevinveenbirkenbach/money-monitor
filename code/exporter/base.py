import os
from ..logger import Logger

class Exporter:
    def __init__(self, transactions, output_file, logger=Logger(), quiet=False):
        self.transactions = sorted(transactions, key=lambda t: t.date)
        self.output_file = output_file
        self.logger = logger

    def get_data_as_dicts(self):
        return [
            t.__dict__ for t in self.transactions
        ]