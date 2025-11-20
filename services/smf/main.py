"""
Warren Shepard and Nand Patel
Dartmouth CS60 25F Final Project
19 Nov 2025

Main logic for SMF.

AI Statement: None.
"""

import sys

from common import formatter, tcp, logging, config
from messages import api
from . import ip_allocator

SERVICVE_NAME = "smf"

def call_policy(msg_type, body):
    """Sends a request to the policy service and returns the reply."""
    #TODO: put this method in a shared location
    policy_port = config.get_port("policy")

    sock = tcp.connect("127.0.0.1", policy_port)    # connect a socket TODO: have a variable for ip here
    msg = formatter.format_message(
        src=SERVICVE_NAME,
        dst="policy",       # TODO: add all of these to a "constants" file or something in /common
        msg_type=msg_type,
        body=body,
    )
    tcp.send_json(sock, msg)
    reply = tcp.recv_json(sock)
    sock.close()
    return reply


def call_upf_control(msg_type, body):
    """Sends a request to the upf_control service and returns the reply."""
    #TODO: put this method in a shared location
    upf_control_port = config.get_port("upf_control")

    sock = tcp.connect("127.0.0.1", upf_control_port)    # connect a socket TODO: have a variable for ip here
    msg = formatter.format_message(
        src=SERVICVE_NAME,
        dst="upf_control",       # TODO: add all of these to a "constants" file or something in /common
        msg_type=msg_type,
        body=body,
    )
    tcp.send_json(sock, msg)
    reply = tcp.recv_json(sock)
    sock.close()
    return reply


def handle_create_session(request):
    """
    Handle CreateSession from AMF and return CreateSessionOk.
    CreateSession: {device_id, slice_id}
    """
    # get header info
    src = formatter.get_src(request)
    id = formatter.get_id(request)

    # get type specific info
    body = request["body"]
    device_id = body["device_id"]
    slice_id = body["slice_id"]

    # get slice profile from policy
    profile_reply = call_policy(
        api.policy.GET_PROFILE,
        {"slice_id": slice_id}
    )
    profile = profile_reply["body"]["profile"]

    # get an ip address to allocate
    ip_addr = ip_allocator.get_next_ip()


    # ask UPF control plane to install the rules for this session
    session_id = f"{device_id}-{slice_id}"

    rule_body = {
        "device_id": device_id,
        "slice_id": slice_id,
        "session_id": session_id,
        "ip_addr": ip_addr,
        "profile": profile,
    }
    # TODO: check for a successful installation
    _ = call_upf_control(
        api.upf.RULE_INSTALL,
        rule_body
    )

    # reply back to AMF with CreateSessionOk
    reply_body = rule_body  # return message is same as rule body for simplicity
    
    return formatter.format_message(
        src=SERVICVE_NAME,
        dst=src,
        msg_type=api.smf.CREATE_SESSION_OK,
        body=reply_body,
        id=id
    )

def handle_message(msg):
    """Handles a single incoming request. Returns the reply message (as a dictionary)."""
    msg_type = formatter.get_type(msg)  # get message type

    if msg_type == api.smf.CREATE_SESSION:
        return handle_create_session(msg)
    
    # if other message type sent, return an error
    reply_body = {"error": f"unknown message type: {msg_type}"}
    return formatter.format_message(
        src=SERVICVE_NAME,
        dst=formatter.get_src(msg), # send back to src
        msg_type=api.common.ERROR,
        body=reply_body,
        id=formatter.get_id(msg),
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
        port = 9200

    main(host, port)