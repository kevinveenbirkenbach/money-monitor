from code.model.configuration import Configuration

class Log:
    RESET = "\033[0m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    WHITE = "\033[97m"
    GREEN = "\033[92m"
    PINK = "\033[35m"

    def __init__(self, configuration:Configuration):
        self.configuration = configuration
        self.warnings_count = 0
        self.success_count = 0
        self.error_count = 0

    def info(self, message):
        if self.configuration.isQuiet():
            return
        print(f"{self.BLUE}[INFO]{self.RESET} {message}")

    def warning(self, message):
        self.warnings_count += 1
        if self.configuration.isQuiet():
            return
        print(f"{self.YELLOW}[WARNING]{self.RESET} {message}")

    def error(self, message):
        self.error_count += 1
        if self.configuration.isQuiet():
            return
        print(f"{self.RED}[ERROR]{self.RESET} {message}")

    def debug(self, message):
        if self.configuration.isQuiet() or not self.configuration.shouldDebug():
            return
        print(f"{self.PINK}[DEBUG]{self.RESET} {message}")

    def success(self, message):
        self.success_count += 1
        if self.configuration.isQuiet():
            return
        print(f"{self.GREEN}[SUCCESS]{self.RESET} {message}")
