"""
Warren Shepard and Nand Patel
Dartmouth CS60 25F Final Project
19 Nov 2025

Control plane for UPF.

AI Statement: None.
"""

from common import formatter, logging
from messages import api
from . import rules


SERVICE_NAME = "upf_control"


def handle_message(msg):
    """
    Handles a single control plane message for the UPF.
    Returns the reply message (as a dictionary).
    """
    msg_type = formatter.get_type(msg)  # get message type
    src = formatter.get_src(msg)
    id = formatter.get_id(msg)
    body = msg["body"]

    if msg_type == api.upf.RULE_INSTALL:
        # get the session_id
        session_id = body["session_id"]

        # store the body as a whole for simplicity
        rules.install_rule(session_id, body)

        reply_body = {
            "session_id": session_id,
            "ok": True,
        }
        return formatter.format_message(
            src=SERVICE_NAME,
            dst=src, # send back to src
            msg_type=api.upf.RULE_INSTALL_OK,
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
