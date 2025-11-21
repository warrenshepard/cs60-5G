"""
Warren Shepard and Nand Patel
Dartmouth CS60 25F Final Project
12 Nov 2025

Load policies/policies.json and provide helpers to get the config and ports for a service.

AI Statement: Used ChatGPT to ask how to cache a json file.
"""

import json
from functools import lru_cache

POLICIES_PATH = "policies/policies.json"

@lru_cache(maxsize=1)
def load_policies(path=POLICIES_PATH):
    """Loads the policies json file and caches it."""
    with open(path, "r") as f:
        return json.load(f)


def get_service_config(service, path=POLICIES_PATH):
    """Get the confic for a given service"""
    policies = load_policies(path)
    services = policies.get("services", {})
    return services.get(service, {})


def get_port(service, path=POLICIES_PATH):
    """Gets the port for a given service."""
    policies = load_policies(path)
    ports = policies.get("ports", {})
    return ports.get(service)