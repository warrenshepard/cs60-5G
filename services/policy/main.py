"""
Warren Shepard and Nand Patel
Dartmouth CS60 25F Final Project
14 Nov 2025

Main logic for policy services.

AI Statement: None.
"""

import sys

from common import formatter, tcp, logging, config
from messages import api
from . import evaluator

SERVICVE_NAME = "policy"

def handle_message(msg):
    """Handles a single incoming request. Returns the reply message (as a dictionary)"""
    # get message info
    msg_type = formatter.get_type(msg)
    src = formatter.get_src(msg)
    id = formatter.get_id(msg)
    body = msg["body"]

    # GetAllowedSlices: {device_id}
    if msg_type == api.policy.GET_ALLOWED_SLICES:
        device_id = body["device_id"]

        try:
            allowed_slices = evaluator.get_allowed_slices(device_id)
        except ValueError:
            # the device is not subscribed to the 5G carrier.
            reply_body = {"error": f"device {device_id} not subscribed"}
            return formatter.format_message(
                src=SERVICVE_NAME,
                dst=src,
                msg_type=api.common.ERROR,
                body=reply_body,
                id=id
            )

        reply_body = {
            "device_id": device_id,
            "allowed_slices": allowed_slices,
        }

        logging.log_verbose(SERVICVE_NAME, f"reply body: {reply_body}")

        return formatter.format_message(
            src=SERVICVE_NAME,
            dst=src,
            msg_type=api.policy.ALLOWED_SLICES,
            body=reply_body,
            id=id
        )
    
    # Admit: {device_id, slice_id}
    if msg_type == api.policy.ADMIT:
        device_id = body["device_id"]
        slice_id = body["slice_id"]
        allowed_slices = evaluator.admit(device_id, slice_id)

        reply_body = {
            "device_id": device_id,
            "slice_id": slice_id,
            "allowed_slices": allowed_slices,
        }

        return formatter.format_message(
            src=SERVICVE_NAME,
            dst=src,
            msg_type=api.policy.ADMIT_OK,
            body=reply_body,
            id=id,
        )
    
    # GetProfile: {slice_id}
    if msg_type == api.policy.GET_PROFILE:
        slice_id = body["slice_id"]
        profile = evaluator.get_profile(slice_id)

        reply_body = {
            "slice_id": slice_id,
            "profile": profile,
        }
        return formatter.format_message(
            src=SERVICVE_NAME,
            dst=src,
            msg_type=api.policy.PROFILE,
            body=reply_body,
            id=id,
        )
    
    # if other message type sent, return an error
    reply_body = {"error": f"unknown message type: {msg_type}"}
    logging.log_error(SERVICVE_NAME, f"recieved unknown message type: {msg_type}")
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
        port = config.get_port("policy")

    main(host, port)