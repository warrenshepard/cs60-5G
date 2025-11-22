"""
Warren Shepard and Nand Patel
Dartmouth CS60 25F Final Project
13 Nov 2025

Main logic for NRF.

AI Statement: None.

                Any Service
                     |
                     |
                     |
           HERE --> NRF

Supported (incoming) message types and formats:
- Register: {name, host, port}
- Lookup: {name}

Outgoing message types and formats:
- RegisterOk: {ok <bool>}
- LookupResult: {found <bool>, host, port}
"""

import sys

from common import formatter, tcp, logging, config
from messages import api
from . import store

SERVICE_NAME = "nrf"


def handle_message(msg):
    """Handles a single incoming request. Returns the reply message (as a dictionary)."""
    # get message info
    msg_type = formatter.get_type(msg)
    src = formatter.get_src(msg)
    id = formatter.get_id(msg)
    body = msg["body"]

    if msg_type == api.nrf.REGISTER:
        # get info
        name = body["name"]
        host = body["host"]
        port = body["port"]

        logging.log_info(SERVICE_NAME, f"{name} registered on {host}:{port}")

        store.register(name, host, port)    # register

        # format registration confirmation
        reply_body ={"ok": True}
        return formatter.format_message(
            src=SERVICE_NAME,
            dst=src,
            msg_type=api.nrf.REGISTER_OK,
            body=reply_body,
            id=id
        )
    
    if msg_type == api.nrf.LOOKUP:
        name = body["name"]

        entry = store.lookup(name)
        
        # format reply
        if entry is None:
            reply_body = {"found": False}
        else:
            reply_body = {
                "found": True,
                "host": entry["host"],
                "port": entry["port"],
                }
        logging.log_error(SERVICE_NAME, f"entry of name {name} not found.")
        return formatter.format_message(
            src=SERVICE_NAME,
            dst=src,
            msg_type=api.nrf.LOOKUP_RESULT,
            body=reply_body,
            id=id
        )
    
    if msg_type == api.nrf.REMOVE:
        # get the name and remove it from the registry
        name = body["name"]

        _ = store.remove(name)

        reply_body = {"removed": name}
        return formatter.format_message(
            src=SERVICE_NAME,
            dst=src,
            msg_type=api.nrf.REMOVE_RESULT,
            body=reply_body,
            id=id
        )


    # if unknown message type sent, return an error
    reply_body = {"error": f"unknown message type: {msg_type}"}
    logging.log_error(SERVICE_NAME, f"recieved unknown message type: {msg_type}")
    return formatter.format_message(
        src=SERVICE_NAME,
        dst=src,
        msg_type=api.common.ERROR,
        body=reply_body,
        id=id
    )


def main(host, port):
    logging.log_info(SERVICE_NAME, f"listening on {host}:{port}")

    server_sock = tcp.listen(host, port)    # for listening

    while True:
        client_sock, addr = server_sock.accept()   # for sending
        logging.log_info(SERVICE_NAME, f"accepted connection from {addr}")

        msg = tcp.recv_json(client_sock)
        if msg is not None:
            reply = handle_message(msg)
            tcp.send_json(client_sock, reply)

        client_sock.close() # better to only keep connections open during use


if __name__ == "__main__":
    host = "127.0.0.1"

    if len(sys.argv) >= 2:
        port = int(sys.argv[1])
    else:
        port = config.get_port("nrf")

    main(host, port)
