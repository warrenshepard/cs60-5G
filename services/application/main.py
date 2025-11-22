"""
Warren Shepard and Nand Patel
Dartmouth CS60 25F Final Project
19 Nov 2025

Main logic for application layer.

AI Statement: None.
"""

import sys

from common import formatter, tcp, logging, config
from common.nrf_client import NRFClient
from messages import api

SERVICE_NAME = "application"
nrf_client = NRFClient(service=SERVICE_NAME)


def handle_message(msg):
    """Handles a single incoming request. Returns the reply message (as a dictionary)."""
    # get message info
    msg_type = formatter.get_type(msg)
    src = formatter.get_src(msg)
    id = formatter.get_id(msg)
    body = msg["body"]

    if msg_type == api.application.ECHO_REQUEST:
        # just return the paylaod in an "EchoReply" message
        payload = body["payload"]
        reply_body = {"payload": "APPLICATION ECHO: " + payload}

        return formatter.format_message(
            src=SERVICE_NAME,
            dst=src,
            msg_type=api.application.ECHO_REPLY,
            body=reply_body,
            id=id
        )
    
    # TODO: add functionality for more complex requests, like requesting a file.
    
    # if unknown message type sent, return an error
    reply_body = {"error": f"unknown message type: {msg_type}"}
    return formatter.format_message(
        src=SERVICE_NAME,
        dst=src,
        msg_type=api.common.ERROR,
        body=reply_body,
        id=id
    )


def main(host, port):
    logging.log_info(SERVICE_NAME, f"listening on {host}:{port}")

    # register service
    nrf_client.register(SERVICE_NAME, host, port)

    server_sock = tcp.listen(host, port)    # for listening

    while True:
        # TODO: does this need to be multithreaded? i don't think so for our purposes...?
        client_sock, addr = server_sock.accept()   # for sending
        logging.log_info(SERVICE_NAME, f"accepted connection from {addr}")

        msg = tcp.recv_json(client_sock)
        if msg is not None:
            reply = handle_message(msg)
            tcp.send_json(client_sock, reply)

        client_sock.close() # better to only keep connections open during use


if __name__ == "__main__":
    host = "127.0.0.1"

    # TODO: add parseargs to this cuz i don't like this format
    if len(sys.argv) >= 2:
        port = int(sys.argv[1])
    else:
        port = config.get_port("application")

    main(host, port)
