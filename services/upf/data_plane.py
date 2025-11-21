"""
Warren Shepard and Nand Patel
Dartmouth CS60 25F Final Project
19 Nov 2025

Data plane for UPF.

AI Statement: None.
"""

from common import formatter, config, tcp
from messages import api
from . import rules

SERVICVE_NAME = "upf_control"


def call_application(msg_type, body):
    """Sends a request to the application service and returns the reply."""
    application_port = config.get_port("application") 
    # TODO: instead of this, services should register themselves in the NRF
    # and we should make a request from there instead

    sock = tcp.connect("127.0.0.1", application_port)    # connect a socket
    msg = formatter.format_message(
        src=SERVICVE_NAME,
        dst="application",       # TODO: add all of these to a "constants" file or something in /common
        msg_type=msg_type,
        body=body,
    )
    tcp.send_json(sock, msg)
    reply = tcp.recv_json(sock)
    sock.close()
    return reply


def handle_message(msg):
    """
    Handles a single control plane message for the UPF.
    Returns the reply message (as a dictionary).
    """
    msg_type = formatter.get_type(msg)  # get message type
    src = formatter.get_src(msg)
    id = formatter.get_id(msg)
    body = msg["body"]

    # TODO: write code for handling different message types
    if msg_type == api.upf.USER_DATA_UP:
        session_id = body["session_id"]
        request_type = body["request_type"]
        payload = body["payload"]

        if request_type == "ECHO":  #TODO: make this a constant somewhere or just use the one in api.applicaiton
            echo_request_body = {"payload": payload}
            app_reply = call_application(
                api.application.ECHO_REQUEST,
                echo_request_body
            )

            app_body = app_reply["body"]
            app_payload = app_body["payload"]

            reply_body = {
                "session_id": session_id,
                "payload": app_payload
            }
            # TODO: actually enfore the session rules!
            return formatter.format_message(
                src=SERVICVE_NAME,
                dst=src, # send back to src
                msg_type=api.upf.USER_DATA_DOWN,
                body=reply_body,
                id=id
            )
        else:
            reply_body = {"error": f"unknown request type: {request_type}"}
            return formatter.format_message(
                src=SERVICVE_NAME,
                dst=src, # send back to src
                msg_type=api.common.ERROR,
                body=reply_body,
                id=id
            )

    reply_body = {"error": f"unknown message type: {msg_type}"}
    return formatter.format_message(
        src=SERVICVE_NAME,
        dst=src, # send back to src
        msg_type=api.common.ERROR,
        body=reply_body,
        id=id
    )
