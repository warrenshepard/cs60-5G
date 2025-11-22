"""
Warren Shepard and Nand Patel
Dartmouth CS60 25F Final Project
20 Nov 2025

To test the base station layer.

AI Statement: Used ChatGPT to generate then signifigantly modified
"""

from common.nrf_client import NRFClient

def test_nrf_client_register_lookup_remove():
    """
    Full integration test:
    - register a service
    - lookup the same service
    - remove the service
    - lookup again (should not be found)
    """

    client = NRFClient(service="test_client")

    service_name = "test_service_x"
    host = "127.0.0.1"
    port = 9999

    # register
    reply = client.register(service_name, host, port)
    assert reply["body"]["ok"] is True

    # lookup
    reply_host, reply_port = client.lookup(service_name)
    assert reply_host == host
    assert reply_port == port

    # remove
    reply = client.remove(service_name)
    assert reply["body"]["removed"] == service_name

    # lookup again (should not exist)
    reply_host, reply_port = client.lookup(service_name)
    assert reply_host is None
    assert reply_port is None