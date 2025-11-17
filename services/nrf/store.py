"""
Warren Shepard and Nand Patel
Dartmouth CS60 25F Final Project
13 Nov 2025

NRF store; stores name -> {host, port} for services.
In a real network this would be a SQL (or similar) database.

AI Statement: None.
"""

registry = {}

def register(name, host, port):
    """
    Adds name -> {host, port} to registry.
    host/port is stored in another dict to be extra explicit.
    """
    registry[name] = {"host": host, "port": port}

def lookup(name):
    """Returns {host, port} for a service name, or None if not found"""
    return registry.get(name)

