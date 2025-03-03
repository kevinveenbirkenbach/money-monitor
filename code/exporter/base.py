from code.logger import Logger
from datetime import datetime, date  # Import both datetime and date
import pytz  # Import pytz for timezone management (optional, if using time zones)

class Exporter:
    def __init__(self, transactions, output_file, logger=Logger(), quiet=False):
        self.output_file = output_file
        self.logger = logger
        # Sorting the transactions by date, using the normalization method
        self.transactions = sorted(
            transactions, 
            key=lambda t: self._normalize_to_datetime(t)
        )

    def get_data_as_dicts(self):
        return [
            t.__dict__ for t in self.transactions
        ]
        
    def _normalize_to_datetime(self, t):
        self.logger.debug(f"Normalizing date: {t.date} (Type: {type(t.date)})")  # Debugging print to see the type
        if isinstance(t.date, datetime):  # Check if it's already a datetime object
            # If the datetime is timezone-aware, we convert it to naive by removing the time zone info
            if t.date.tzinfo is not None:
                return t.date.replace(tzinfo=None)  # Make the datetime naive
            return t.date  # Already naive, return as is
        elif isinstance(t.date, date):  # Check if it's a datetime.date object (date class in the datetime module)
            return datetime.combine(t.date, datetime.min.time())  # Convert to datetime object (naive)
        else:
            raise ValueError(f"Unexpected type for date: {type(t.date)}")  # Handle unexpected types
