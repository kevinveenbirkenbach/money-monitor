from datetime import date, datetime, time
import yaml

class Configuration:
    """ Collector Class for the configuration """
    def __init__(
        self,
        configuration_file:str,
        input_paths:[str],
        output_base:str,
        export_types:[str],
        create_dirs:bool,
        quiet:bool,
        debug:bool,
        validate:bool,
        print_cmd:bool,
        recursive:bool,
        from_date:date=None,
        to_date:date=None,
        ):
        self.configuration_file = configuration_file
        self.configuration_file_data = {}
        self.input_paths = input_paths
        self.output_base = output_base
        self.export_types = export_types
        self._from_date  = from_date
        self._to_date = to_date
        self.create_dirs = create_dirs
        self.quiet=quiet
        self.debug=debug
        self.validate=validate
        self.print_cmd=print_cmd
        self.recursive=recursive
        self._loadConfigurationFile()
        self.log = None # Placeholder - Log sets itself 
        
    
    def setFromDate(self,from_date:str)->None:
        self._from_date = self._getDatetimeByString(from_date)
        
    def setToDate(self,to_date:str)->None:
        self._to_date = self._getDatetimeByString(to_date)
    
    def _getDatetimeByString(self,date_string:str)->datetime:
        return datetime.strptime(date_string, "%Y-%m-%d").date()
 
    def _loadConfigurationFile(self)->None:   
        # Load YAML config
        try:
            with open(self.configuration_file, "r", encoding="utf-8") as f:
                self.configuration_file_data = yaml.safe_load(f)
        except Exception as e:
            self.log.error(f"Failed to load config file '{self.configuration_file}': {e}")
            sys.exit(1)
    
    def getInputPaths(self)->[str]:
        return self.input_paths
    
    def getOutputBase(self)->str:
        return self.output_base
    
    def getExportTypes(self)->str:
        return self.export_types
    
    def shouldCreateDirs(self)->bool:
        return self.create_dirs
    
    def isQuiet(self)->bool:
        return self.quiet
    
    def shouldDebug(self)->bool:
        return self.debug

    def shouldValidate(self)->bool:
        return self.validate

    def shouldPrintCmd(self)->bool:
        return self.print_cmd
    
    def getFromDatetime(self)->datetime:
        if not self._from_date:
            return None
        return datetime.combine(self._from_date, time(0, 0, 0)).replace(tzinfo=None)

    def getToDatetime(self)->datetime:
        if not self._to_date:
            return None
        return datetime.combine(self._to_date, time(23, 59, 59)).replace(tzinfo=None)
    
    def shouldRecursiveScan(self)->bool:
        return self.recursive