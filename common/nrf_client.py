"""
Warren Shepard and Nand Patel
Dartmouth CS60 25F Final Project
13 Nov 2025

Client for Network Registry Function (NRF).
Used as a helper that other services can go through.

AI Statement: None.
"""

from . import tcp
from . import formatter
from messages import api

class NRFClient:
    """Client for the Network Registry Function (NRF)."""

    def __init__(self, host, port, service):
        self.host = host
        self.port = port
        self.service = service

    def _send_request(self, msg_type, body):
        """Helper function to send a message to the NRF service."""
        sock = tcp.connect(self.host, self.port)
        msg = formatter.format_message(
            src=self.service,
            dst="nrf",
            msg_type=msg_type,
            body=body,
        )
        tcp.send_json(sock, msg)
        reply = tcp.recv_json(sock)
        sock.close()
        return reply
    
    def register(self, name, host, port):
        """Register name -> (host, port) in the NRF repository."""
        body = {
            "name": name,
            "host": host,
            "port": port,
        }
        return self._send_request(api.nrf.REGISTER, body)
    
    def lookup(self, name):
        """Looks up a name -> (host, port) in the NRF repository."""
        body = {"name": name}
        return self._send_request(api.nrf.LOOKUP, body)
