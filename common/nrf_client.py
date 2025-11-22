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
from . import config
from messages import api

NRF_HOST = "127.0.0.1"
NRF_PORT = config.get_port("nrf")


class NRFClient:
    """Client for the Network Registry Function (NRF)."""

    def __init__(self, service):
        self.service = service

    def _send_request(self, msg_type, body):
        """Helper function to send a message to the NRF service."""
        sock = tcp.connect(NRF_HOST, NRF_PORT)
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
        reply =  self._send_request(api.nrf.LOOKUP, body)
        

        reply_body = reply["body"]
        found = reply_body["found"]

        if found:
            host = reply_body["host"]
            port = reply_body["port"]
            return host, port
        
        # if not found, return None
        return None, None
    
    def remove(self, name):
        """Removes name from the NRF repository."""
        body = {"name": name}
        return self._send_request(api.nrf.REMOVE, body)
