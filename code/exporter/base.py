from code.logger import Logger
from datetime import datetime, date  # Import both datetime and date
import pytz  # Import pytz for timezone management (optional, if using time zones)
from code.helper.datetime import createComparatableTime

class Exporter:
    def __init__(self, transactions, output_file, logger=Logger(), quiet=False):
        self.output_file = output_file
        self.logger = logger
        # Sorting the transactions by date, using the normalization method
        self.transactions = sorted(
            transactions, 
            key=lambda t: createComparatableTime(t.date)
        )

    def get_data_as_dicts(self):
        return [
            t.__dict__ for t in self.transactions
        ]
        
