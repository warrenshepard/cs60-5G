"""
Warren Shepard and Nand Patel
Dartmouth CS60 25F Final Project
19 Nov 2025

Data plane for UPF.

AI Statement: None.
"""

from common import formatter
from messages import api
import rules


SERVICVE_NAME = "upf_control"


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


    reply_body = {"error": f"unknown message type: {msg_type}"}
    return formatter.format_message(
        src=SERVICVE_NAME,
        dst=src, # send back to src
        msg_type=api.common.ERROR,
        body=reply_body,
        id=id
    )
