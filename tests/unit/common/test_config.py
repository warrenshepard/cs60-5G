"""
Warren Shepard and Nand Patel
Dartmouth CS60 25F Final Project
20 Nov 2025

Unit tests for common.config methods.

This was used to debug common.config.py (and helped catch several bugs).

Run with: `pytest tests/unit/common/test_config.py`

AI Statement: ChatGPT wrote almost this whole thing (with Piersons permission to do this).
    To generate, we described each method that we wanted and what the input and correct output that should
    be tested should be. 

    Note that we did check each method that ChatGPT came up with thoroughly and modified it as we saw fit!
"""

import json
import os
import tempfile

from common.config import load_policies, get_service_config, get_port


def write_temp_policies(data: dict) -> str:
    """Helper to write a temporary policies.json and return the file path."""
    fd, path = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, "w") as f:
        json.dump(data, f)
    return path


def test_load_policies_reads_file_and_caches():
    test_data = {
        "services": {"amf": {"threads": 2}},
        "ports": {"amf": 9001},
    }
    path = write_temp_policies(test_data)

    # Clear cache before testing
    load_policies.cache_clear()

    policies = load_policies(path)
    assert policies == test_data

    # Call again: should return same object from cache
    again = load_policies(path)
    assert again is policies


def test_get_service_config_returns_correct_section():
    test_data = {
        "services": {
            "amf": {"threads": 4},
            "smf": {"threads": 6},
        }
    }
    path = write_temp_policies(test_data)

    load_policies.cache_clear()
    cfg = get_service_config("amf", path)
    assert cfg == {"threads": 4}

    cfg = get_service_config("smf", path)
    assert cfg == {"threads": 6}


def test_get_service_config_unknown_returns_empty_dict():
    test_data = {"services": {"amf": {"threads": 2}}}
    path = write_temp_policies(test_data)

    load_policies.cache_clear()
    cfg = get_service_config("unknown", path)
    assert cfg == {}


def test_get_port():
    """Tests that get_port gets the correct ports from the config file."""
    test_data = {
        "ports": {
            "amf": 9001,
            "upf": 9300
        }
    }
    path = write_temp_policies(test_data)

    load_policies.cache_clear()
    load_policies(path)  # prime cache

    assert get_port("amf", path) == 9001
    assert get_port("upf", path) == 9300


def test_get_port_unknown_returns_none():
    """Tests that get_port returns None for an unknown service."""
    test_data = {"ports": {"amf": 9001}}
    path = write_temp_policies(test_data)

    load_policies.cache_clear()
    load_policies(path)

    assert get_port("5g_networks_cause_cancer", path) is None