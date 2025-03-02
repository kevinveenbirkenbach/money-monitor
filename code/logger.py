import sys

class Logger:
    RESET = "\033[0m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    WHITE = "\033[97m"
    GREEN = "\033[92m"
    PINK = "\033[35m"

    def __init__(self, debug=False, quiet=False):
        self.debug_enabled = debug
        self.quiet = quiet
        self.warnings_count = 0
        self.success_count = 0

    def info(self, message):
        if self.quiet:
            return
        print(f"{self.BLUE}[INFO]{self.RESET} {message}")

    def warning(self, message):
        self.warnings_count += 1
        if self.quiet:
            return
        print(f"{self.YELLOW}[WARNING]{self.RESET} {message}")

    def error(self, message):
        if self.quiet:
            return
        print(f"{self.RED}[ERROR]{self.RESET} {message}")
        # Exit the script with a non-zero exit code
        sys.exit(1)

    def debug(self, message):
        if self.quiet or not self.debug_enabled:
            return
        print(f"{self.PINK}[DEBUG]{self.RESET} {message}")

    def success(self, message):
        self.success_count += 1
        if self.quiet:
            return
        print(f"{self.GREEN}[SUCCESS]{self.RESET} {message}")
