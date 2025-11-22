"""
Warren Shepard and Nand Patel
Dartmouth CS60 25F Final Project
12 Nov 2025

Common logging functions.

AI Statement: Used ChatGPT for _log_to_file bug (see note about that there).
"""

import sys
import threading


VERBOSE_ENABLED = True  # set to False to switch off verbose logging.

LOG_FILE_PATH = "logs/all.log"

# NOTE: can change "a" to "w" if you want to overwrite for every
# run instead of append (or vice versa)
LOG_FILE = open(LOG_FILE_PATH, "a")

log_lock = threading.Lock() # to synchronize logging.


def _log_to_file(line):
    """Helper to write the the log file."""
    try:
        LOG_FILE.write(line + "\n")
        LOG_FILE.flush()                # for some reason this is needed for VERBOSE to show up
    except:
        pass


def log(service, type, msg):
    """
    Logging function for a particular service.
    Only write verbose logging to the log file.
    Everything else goes to the log file AND terminal.
    """
    line = f"[{service}] [{type}] {msg}"

    with log_lock:
        _log_to_file(line)

        if type != "VERBOSE":
            print(line, file=sys.stdout, flush=True)


def log_info(service, msg):
    "Log info."
    log(service, "INFO", msg)


def log_error(service, msg):
    "Log an error"
    log(service, "ERROR", msg)


def log_verbose(service, msg):
    """
    Log verbose (extra/additional) information.
    Can be turned on and off
    """
    if VERBOSE_ENABLED:
        log(service, "VERBOSE", msg)