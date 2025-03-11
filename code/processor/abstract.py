from code.model.log import Log
from code.model.transactions_wrapper import TransactionsWrapper
from abc import ABC, abstractmethod
from code.model.configuration import Configuration

class AbstractProcessor:
    def __init__(self,log:Log,configuration:Configuration,transactions_wrapper:TransactionsWrapper=None):
        self.log=log
        self.configuration = configuration
        if transactions_wrapper:
            self.transactions_wrapper = transactions_wrapper
        else:
            self.transactions_wrapper = TransactionsWrapper(self.log)
    
    @abstractmethod
    def process(self)->TransactionsWrapper:
        pass
    