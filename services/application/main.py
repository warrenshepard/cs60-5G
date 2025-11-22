"""
Warren Shepard and Nand Patel
Dartmouth CS60 25F Final Project
19 Nov 2025

Main logic for application layer.

AI Statement: Used ChatGPT to figure out how to normalize file paths (see read_file).
"""

import sys
import os

from common import formatter, tcp, logging, config
from common.nrf_client import NRFClient
from messages import api

SERVICE_NAME = "application"
FILE_DIR = "assets"

safe = True     # toggle configuration in policies/policies.json if you want to change this.
nrf_client = NRFClient(service=SERVICE_NAME)


def read_file(filename):
    """
    Returns found [bool], content/error message [str].
    Only returns files if they're in ./FILE_DIR.
    """
    # append FILE_DIR to form a file path.
    if safe:
        # normalize the file path to the simplest possible form
        # for example, "assets/../../passwords.txt" would be normalized to "../passwords.txt"
        # hopefully this example shows why this is important for saftey, as if this is not done
        # (with the addition of checking that the file path starts with FILE_DIR), then very 
        # bad things could happen!
        path = os.path.normpath(os.path.join(FILE_DIR, filename))
    else:
        path = os.path.join(FILE_DIR, filename)

    # check that the file is in the correct foler
    if not path.startswith(FILE_DIR):
        return False, "invalid filename"

    if not os.path.exists(path):
        return False, "file not found"

    try:
        with open(path, "r") as f:
            return True, f.read()
    except Exception as e:
        return False, str(e)


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
    
    if msg_type == api.application.FILE_REQUEST:
        # get file name
        filename = body["filename"]

        # read file
        found, result = read_file(filename)

        # format and send response
        if found:
            reply_body = {
                "found": True,
                "filename": filename,
                "content": result
            }
        else:
            reply_body = {
                "found": False,
                "filename": filename,
                "error": result
            }
            logging.log_error(SERVICE_NAME, f"file not found: {filename}")
        return formatter.format_message(
            src=SERVICE_NAME,
            dst=src,
            msg_type=api.application.FILE_RESPONSE,
            body=reply_body,
            id=id
        )

    # if unknown message type sent, return an error
    reply_body = {"error": f"unknown message type: {msg_type}"}
    logging.log_error(SERVICE_NAME, f"unknown message type recieved: {msg_type}")
    return formatter.format_message(
        src=SERVICE_NAME,
        dst=src,
        msg_type=api.common.ERROR,
        body=reply_body,
        id=id
    )


def main(host, port):
    global safe

    logging.log_info(SERVICE_NAME, f"listening on {host}:{port}")

    # register service
    nrf_client.register(SERVICE_NAME, host, port)

    # figure out if we want to be safe or not
    policies = config.get_service_config(SERVICE_NAME)
    safe = policies.get("safe", True)   # default to True for safteys sake

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
        port = config.get_port("application")

    main(host, port)
