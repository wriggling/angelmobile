
import sys
import time
import threading
import traceback
from datetime import datetime
from colorama import init

# Preserve ANSI escape sequences in hosted logs.
init(autoreset=False, strip=False)

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
CLEAR = "\033[2J\033[H"

# Refresh banner after 30 minutes, when a new log arrives.
REFRESH_SECONDS = 30 * 60

# RGB gradient: purple -> blue -> cyan
GRADIENT = [
    (190, 60, 255),
    (110, 90, 255),
    (50, 160, 255),
    (40, 230, 220),
]

# Standard ANSI colors for regular log messages.
STANDARD = {
    "INFO": "\033[36m",       # Cyan
    "SUCCESS": "\033[32m",    # Green
    "WARNING": "\033[33m",    # Yellow
    "ERROR": "\033[31m",      # Red
    "TIME": "\033[90m",       # Gray
    "LABEL": "\033[35m",      # Magenta
}


def rgb(r, g, b):
    return f"\033[38;2;{r};{g};{b}m"


def gradient(text, colors=GRADIENT):
    """Apply a left-to-right RGB gradient without changing spacing."""
    if not text:
        return ""

    result = []
    visible_chars = [c for c in text if c not in ("\r", "\n")]
    length = max(len(visible_chars) - 1, 1)
    position_index = 0

    for char in text:
        if char in ("\r", "\n"):
            result.append(RESET + char)
            continue

        position = position_index / length * (len(colors) - 1)
        index = min(int(position), len(colors) - 2)
        fraction = position - index

        start = colors[index]
        end = colors[index + 1]

        r = round(start[0] + (end[0] - start[0]) * fraction)
        g = round(start[1] + (end[1] - start[1]) * fraction)
        b = round(start[2] + (end[2] - start[2]) * fraction)

        result.append(rgb(r, g, b) + char)
        position_index += 1

    return "".join(result) + RESET


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
        art = r"""
 _____             _
|  _  |___ ___ ___| |
|     |   | . | -_| |
|__|__|_|_|_  |___|_|
           |___|
"""
        # Color each line independently so ANSI resets never
        # leak across lines or disturb the artwork's spacing.
        for line in art.splitlines():
            print(gradient(line))

        print(gradient("----------------------------------------"))
        print(gradient("             SYSTEM CONSOLE"))
        print(gradient("----------------------------------------"))

        print(
            f" {STANDARD['LABEL']}Started:{RESET}  "
            f"{self.timestamp()}"
        )
        print(
            f" {STANDARD['LABEL']}Uptime:{RESET}   "
            f"{self.uptime()}"
        )
        print(
            f" {STANDARD['LABEL']}Refresh:{RESET}  "
            f"Every 30 minutes"
        )
        print(gradient("----------------------------------------"))
        print()

    def clear(self):
        with self.lock:
            # Render's log viewer is historical, not a terminal.
            # Only clear an actual interactive terminal.
            if sys.stdout.isatty():
                print(CLEAR, end="", flush=True)

            self.last_refresh = time.monotonic()
            self.banner()
            print(gradient(" RECENT EVENTS"))

            for event in self.events[-self.max_events:]:
                print(event)

            print()
            print(
                f"{DIM}Next refresh after 30 minutes, "
                f"when another log arrives.{RESET}\n"
            )

    def refresh_if_needed(self):
        if time.monotonic() - self.last_refresh >= REFRESH_SECONDS:
            self.clear()

    def log(self, level, message):
        with self.lock:
            self.refresh_if_needed()

            time_color = STANDARD["TIME"]
            level_color = STANDARD.get(level, STANDARD["INFO"])

            line = (
                f"{time_color}[{self.timestamp()}]{RESET} "
                f"{level_color}[{level:^7}]{RESET} "
                f"{message}{RESET}"
            )

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
            self.info("RGB banner gradient enabled")
            self.info("Standard ANSI log colors enabled")
            self.info("Timestamped logging enabled")
            self.info("30-minute refresh configured")

    def shutdown(self):
        self.info(f"Application stopping | Uptime: {self.uptime()}")


console = ConsoleUI()
