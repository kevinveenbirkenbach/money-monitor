from code.model.log import Log
from datetime import datetime, date  # Import both datetime and date
import pytz  # Import pytz for timezone management (optional, if using time zones)
from abc import ABC, abstractmethod
from code.model.configuration import Configuration
from code.model.transactions_wrapper import TransactionsWrapper

class AbstractExporter(ABC):
    def __init__(self, transactions_wrapper:TransactionsWrapper, configuration:Configuration, log:Log):
        self.output_file = output_file
        self.log = log
        self.configuration = configuration
        self.transactions_wrapper = transactions_wrapper
        self.transactions_wrapper.sortByDate()

    def get_data_as_dicts(self):
        return [
            t.__dict__ for t in self.transactions_wrapper.getAll()
        ]
    
    @abstractmethod
    def export(self)->None:
        pass
    
    def doTransactionsExist(self)->bool:
        if self.transactions_wrapper.getAll():
            return True
        self.log.warning("No transactions found to save.")
        return False
        
