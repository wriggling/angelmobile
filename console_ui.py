

import os
import sys
import time
import threading
import traceback
from datetime import datetime
from colorama import init

# Preserve ANSI colors in supported terminals, including Linux hosts.
init(autoreset=False, strip=False)

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
CLEAR = "\033[2J\033[H"

REFRESH_SECONDS = 30 * 60

# RGB gradient: purple -> blue -> cyan
GRADIENT = [
    (190, 60, 255),
    (110, 90, 255),
    (50, 160, 255),
    (40, 230, 220),
]


def rgb(r, g, b):
    return f"\033[38;2;{r};{g};{b}m"


def gradient(text, colors=GRADIENT):
    if not text:
        return ""

    result = []
    length = max(len(text) - 1, 1)

    for i, char in enumerate(text):
        position = i / length * (len(colors) - 1)
        index = min(int(position), len(colors) - 2)
        fraction = position - index

        start = colors[index]
        end = colors[index + 1]

        r = int(start[0] + (end[0] - start[0]) * fraction)
        g = int(start[1] + (end[1] - start[1]) * fraction)
        b = int(start[2] + (end[2] - start[2]) * fraction)

        result.append(rgb(r, g, b) + char)

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
        print(gradient(art))
        print(gradient("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"))
        print(gradient("              SYSTEM CONSOLE"))
        print(gradient("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"))
        print(f" {rgb(150, 150, 255)}Started:{RESET}  {self.timestamp()}")
        print(f" {rgb(150, 150, 255)}Uptime:   {self.uptime()}")
        print(f" {rgb(150, 150, 255)}Refresh:  Every 30 minutes")
        print(gradient("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"))
        print()

    def clear(self):
        with self.lock:
            # ANSI screen clearing works in supported terminals.
            # Some hosted log viewers retain their historical output.
            if sys.stdout.isatty():
                print(CLEAR, end="")

            self.last_refresh = time.monotonic()
            self.banner()
            print(gradient(" RECENT EVENTS"))

            for event in self.events[-self.max_events:]:
                print(event)

            print()
            print(
                f"{DIM}Next refresh on the next log event "
                f"after 30 minutes.{RESET}\n"
            )

    def refresh_if_needed(self):
        if time.monotonic() - self.last_refresh >= REFRESH_SECONDS:
            self.clear()

    def log(self, level, message, color):
        with self.lock:
            self.refresh_if_needed()

            time_color = rgb(130, 145, 170)
            level_color = rgb(*color)

            line = (
                f"{time_color}[{self.timestamp()}]{RESET} "
                f"{level_color}[{level:^7}]{RESET} "
                f"{message}{RESET}"
            )

            self.events.append(line)
            self.events = self.events[-self.max_events:]
            print(line, flush=True)

    def info(self, message):
        self.log("INFO", message, (60, 190, 255))

    def success(self, message):
        self.log("SUCCESS", message, (60, 230, 140))

    def warning(self, message):
        self.log("WARNING", message, (255, 190, 50))

    def error(self, message):
        self.log("ERROR", message, (255, 75, 95))

    def exception(self, message):
        with self.lock:
            self.error(message)
            traceback.print_exc(file=sys.stdout)
            sys.stdout.flush()

    def startup(self):
        with self.lock:
            if sys.stdout.isatty():
                print(CLEAR, end="")
            self.last_refresh = time.monotonic()
            self.banner()
            self.success("Console initialized")
            self.info("RGB gradient enabled")
            self.info("Timestamped logging enabled")
            self.info("30-minute refresh configured")

    def shutdown(self):
        self.info(f"Application stopping | Uptime: {self.uptime()}")


console = ConsoleUI()
