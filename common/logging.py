"""
Warren Shepard and Nand Patel
Dartmouth CS60 25F Final Project
12 Nov 2025

Common logging functions.

AI Statement: None.
"""

import sys

def log(service, type, msg):
    """Logging function for a particular service."""
    line = f"[{service}] [{type}] {msg}"
    print(line, file=sys.stdout, flush=True)


def log_info(service, msg):
    "Log info."
    log(service, "INFO", msg)


def log_error(service, msg):
    "Log an error"
    log(service, "ERROR", msg)

def log_verbose(service, msg):
    "Log verbose (can be turned on and off)"
    log(service, "VERBOSE", msg)

# log_info and log_error should only be used in main method of each service?

# TODO: add log_verbose and a switch to turn it on/off
# good for logging things NOT in the main method of each service