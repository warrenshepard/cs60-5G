"""
Warren Shepard and Nand Patel
Dartmouth CS60 25F Final Project
19 Nov 2025

Data plane for UPF.

AI Statement: None.
"""

import time

from common import formatter, tcp, logging
from common.nrf_client import NRFClient
from messages import api
from . import rules

SERVICE_NAME = "upf_control"
nrf_client = NRFClient(service=SERVICE_NAME)


def call_application(msg_type, body):
    """Sends a request to the application service and returns the reply."""
    _, application_port = nrf_client.lookup("application")

    sock = tcp.connect("127.0.0.1", application_port)    # connect a socket
    msg = formatter.format_message(
        src=SERVICE_NAME,
        dst="application",
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


    if msg_type == api.upf.USER_DATA_UP:
        session_id = body["session_id"]
        request_type = body["request_type"]
        
        # get the rules
        rule = rules.get_rule(session_id)
        if not rule:
            reply_body = {"error": f"session id {session_id} invalid/does not exist."}
            logging.log_error(SERVICE_NAME, f"session id {session_id} invalid/does not exist.")
            return formatter.format_message(
                src=SERVICE_NAME,
                dst=src, # send back to src
                msg_type=api.common.ERROR,
                body=reply_body,
                id=id
            )
        
        profile = rule["profile"]
        latency_ms = profile["latency_s"]

        # to simulate the latency
        # note that we do not handle the rate for simplicity
        time.sleep(latency_ms)

        # just use same body for simplicity
        app_reply = call_application(
            request_type,
            body
        )

        app_body = app_reply["body"]
        reply_body = app_body
        reply_body["session_id"] = session_id
        
        return formatter.format_message(
                src=SERVICE_NAME,
                dst=src, # send back to src
                msg_type=api.upf.USER_DATA_DOWN,
                body=reply_body,
                id=id
            )

    reply_body = {"error": f"unknown message type: {msg_type}"}
    logging.log_error(SERVICE_NAME, f"unknown message type recieved: {msg_type}")
    return formatter.format_message(
        src=SERVICE_NAME,
        dst=src, # send back to src
        msg_type=api.common.ERROR,
        body=reply_body,
        id=id
    )
