"""
Warren Shepard and Nand Patel
Dartmouth CS60 25F Final Project
13 Nov 2025

Main logic for NRF.

AI Statement: None.

Supported (incoming) message types and formats:
- Register: {name, host, port}
- Lookup: {name}

Outgoing message types and formats:
- RegisterOk: {ok <bool>}
- LookupResult: {found <bool>, host, port}
"""
# TODO: ^put the message body formats above somewhere in the messages folder
# and also change the note to "see <file> for supported message types and formats" or something like that

import sys

from common import formatter, tcp, logging
from messages import api
from . import store

SERVICVE_NAME = "nrf"

def handle_message(msg):
    """Handles a single incoming request. Returns the reply message (as a dictionary)."""
    # get message info
    msg_type = formatter.get_type(msg)
    src = formatter.get_src(msg)
    id = formatter.get_id(msg)
    body = msg["body"]

    if msg_type == api.nrf.REGISTER:
        # get info
        # TODO: potentially add helper function in messages.py to get this info which
        # could return a custom error if it's not there. Then we can try/catch this
        # for invalid message format. IMPORTANT: this could also be handled by some function in the API,
        # idk how exactly that would look though
        name = body["name"]
        host = body["host"]
        port = body["port"]

        store.register(name, host, port)    # register

        # format registration confirmation
        reply_body ={"ok": True}
        return formatter.format_message(
            src=SERVICVE_NAME,
            dst=src,
            msg_type=api.nrf.REGISTER_OK,
            body=reply_body,
            id=id,
        )
    
    if msg_type == api.nrf.LOOKUP:
        # TODO: same as above
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
        return formatter.format_message(
            src=SERVICVE_NAME,
            dst=src,
            msg_type=api.nrf.LOOKUP_RESULT,
            body=reply_body,
            id=id,
        )

    # if other message type sent, return an error
    reply_body = {"error": f"unknown message type: {msg_type}"}
    return formatter.format_message(
        src=SERVICVE_NAME,
        dst=src,
        msg_type=api.common.ERROR,
        body=reply_body,
        id=id,
    )


def main(host, port):
    logging.log_info(SERVICVE_NAME, f"listening on {host}:{port}")

    server_sock = tcp.listen(host, port)    # for listening

    while True:
        # TODO: does this need to be multithreaded? i don't think so for our purposes...?
        client_sock, addr = server_sock.accept()   # for sending
        logging.log_info(SERVICVE_NAME, f"accepted connection from {addr}")

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
        port = 9000

    main(host, port)
