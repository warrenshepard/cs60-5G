"""
Warren Shepard and Nand Patel
Dartmouth CS60 25F Final Project
19 Nov 2025

IP allocator for SMF.
"""

import ipaddress

next_ip = ipaddress.IPv4Address("10.0.0.1")

def get_next_ip():
    """Return the next availible (sequential) IP address (as a string)."""
    global next_ip

    ip_str = str(next_ip)
    next_ip += 1
    return ip_str

