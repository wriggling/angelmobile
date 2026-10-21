
import os
import sys
import time
import logging
import threading
import traceback
from datetime import datetime
from colorama import init, Fore, Style

init(autoreset=True)

RED = Fore.RED
BLUE = Fore.BLUE
CYAN = Fore.CYAN
MAGENTA = Fore.MAGENTA
GREEN = Fore.GREEN
YELLOW = Fore.YELLOW
WHITE = Fore.WHITE
DIM = Style.DIM
RESET = Style.RESET_ALL

REFRESH_SECONDS = 30 * 60


class ConsoleUI:
    def __init__(self):
        self.started = time.monotonic()
        self.lock = threading.RLock()
        self.events = []
        self.max_events = 8
        self.last_refresh = self.started
        self.running = True

    def timestamp(self):
        return datetime.now().astimezone().strftime(
            "%Y-%m-%d %H:%M:%S %Z"
        )

    def uptime(self):
        elapsed = int(time.monotonic() - self.started)
        hours, rem = divmod(elapsed, 3600)
        minutes, seconds = divmod(rem, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def banner(self):
        print(f"""{RED}
 _____             _
|  _  |___ ___ ___| |
|     |   | . | -_| |
|__|__|_|_|_  |___|_|
           |___|
{RESET}{MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{CYAN}          SYSTEM CONSOLE
{MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}
{WHITE} Started: {self.timestamp()}
 Uptime:   {self.uptime()}
{MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}
""")

    def refresh_if_needed(self):
        if time.monotonic() - self.last_refresh >= REFRESH_SECONDS:
            self.clear()

    def clear(self):
        with self.lock:
            os.system("cls" if os.name == "nt" else "clear")
            self.last_refresh = time.monotonic()
            self.banner()
            print(f"{CYAN}Recent events:{RESET}")

            for event in self.events[-self.max_events:]:
                print(event)

            print(f"\n{DIM}Next refresh in 30 minutes.{RESET}\n")

    def log(self, level, message, color=WHITE):
        with self.lock:
            self.refresh_if_needed()

            line = (
                f"{DIM}[{self.timestamp()}]{RESET} "
                f"{color}[{level.upper():7}]{RESET} {message}"
            )

            self.events.append(line)
            self.events = self.events[-self.max_events:]
            print(line, flush=True)

    def info(self, message):
        self.log("INFO", message, CYAN)

    def success(self, message):
        self.log("SUCCESS", message, GREEN)

    def warning(self, message):
        self.log("WARNING", message, YELLOW)

    def error(self, message):
        self.log("ERROR", message, RED)

    def exception(self, message):
        with self.lock:
            self.error(message)
            traceback.print_exc(file=sys.stdout)
            sys.stdout.flush()

    def startup(self):
        with self.lock:
            os.system("cls" if os.name == "nt" else "clear")
            self.banner()
            self.info("Console initialized")
            self.info("Automatic refresh: 30 minutes")
            self.info("Timestamped diagnostics enabled")

    def shutdown(self):
        self.info(f"Shutting down. Total uptime: {self.uptime()}")
        self.running = False


console = ConsoleUI()
