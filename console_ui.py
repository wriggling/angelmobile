
import sys
import time
import threading
import traceback
from datetime import datetime
from colorama import init

init(autoreset=False, strip=False)

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
CLEAR = "\033[2J\033[H"

REFRESH_SECONDS = 30 * 60

# Standard ANSI colors
COLORS = {
    "INFO": "\033[36m",       # Cyan
    "SUCCESS": "\033[32m",    # Green
    "WARNING": "\033[33m",   # Yellow
    "ERROR": "\033[31m",     # Red
    "TIME": "\033[90m",      # Gray
    "TITLE": "\033[35m",     # Magenta
    "BANNER": "\033[34m",    # Blue
}


class ConsoleUI:
    def __init__(self):
        self.started = time.monotonic()
        self.last_refresh = self.started
        self.lock = threading.RLock()
        self.events = []
        self.max_events = 12

    def timestamp(self):
        return datetime.now().astimezone().strftime(
            "%Y-%m-%d %H:%M:%S %Z"
        )

    def uptime(self):
        seconds = int(time.monotonic() - self.started)
        hours, remaining = divmod(seconds, 3600)
        minutes, seconds = divmod(remaining, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def banner(self):
        blue = COLORS["BANNER"]
        magenta = COLORS["TITLE"]
        gray = COLORS["TIME"]

        # Your original ASCII art
        art = [
            r" _____             _",
            r"|  _  |___ ___ ___| |",
            r"|     |   | . | -_| |",
            r"|__|__|_|_|_  |___|_|",
            r"           |___|",
        ]

        print()
        for line in art:
            print(f"{blue}{line}{RESET}")

        print(f"{magenta}----------------------------------------{RESET}")
        print(f"{BOLD}{magenta}{'SYSTEM CONSOLE':^40}{RESET}")
        print(f"{magenta}----------------------------------------{RESET}")

        print(f"{gray}Started:{RESET} {self.timestamp()}")
        print(f"{gray}Uptime:  {RESET} {self.uptime()}")
        print(f"{gray}Refresh: Every 30 minutes")

        print(f"{magenta}----------------------------------------{RESET}")
        print()

    def clear(self):
        with self.lock:
            if sys.stdout.isatty():
                print(CLEAR, end="", flush=True)

            self.last_refresh = time.monotonic()
            self.banner()
            print(f"{COLORS['INFO']}RECENT EVENTS{RESET}")

            for event in self.events[-self.max_events:]:
                print(event)

            print(
                f"\n{DIM}Refresh occurs on the next log event "
                f"after 30 minutes.{RESET}\n"
            )

    def refresh_if_needed(self):
        if time.monotonic() - self.last_refresh >= REFRESH_SECONDS:
            self.clear()

    def log(self, level, message):
        with self.lock:
            self.refresh_if_needed()

            timestamp = (
                f"{COLORS['TIME']}[{self.timestamp()}]{RESET}"
            )
            color = COLORS.get(level, COLORS["INFO"])
            label = f"{color}[{level}]{RESET}"

            line = f"{timestamp} {label} {message}{RESET}"

            self.events.append(line)
            self.events = self.events[-self.max_events:]
            print(line, flush=True)

    def info(self, message):
        self.log("INFO", message)

    def success(self, message):
        self.log("SUCCESS", message)

    def warning(self, message):
        self.log("WARNING", message)

    def error(self, message):
        self.log("ERROR", message)

    def exception(self, message):
        with self.lock:
            self.error(message)
            traceback.print_exc(file=sys.stdout)
            sys.stdout.flush()

    def startup(self):
        with self.lock:
            if sys.stdout.isatty():
                print(CLEAR, end="", flush=True)

            self.last_refresh = time.monotonic()
            self.banner()
            self.success("Console initialized")
            self.info("Standard ANSI colors enabled")
            self.info("Timestamped logging enabled")
            self.info("30-minute refresh configured")

    def shutdown(self):
        self.info(f"Application stopping | Uptime: {self.uptime()}")


console = ConsoleUI()
