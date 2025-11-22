"""
Warren Shepard and Nand Patel
Dartmouth CS60 25F Final Project
19 Nov 2025

Main logic for SMF.

                    AMF 
                     |
                     |
                     |
           HERE --> SMF - - - Policy
                     |
                     |
                     |
                UPF Control

AI Statement: None.
"""

import sys

from common import formatter, tcp, logging, config
from common.nrf_client import NRFClient
from messages import api
from . import ip_allocator
import uuid

SERVICE_NAME = "smf"
nrf_client = NRFClient(service=SERVICE_NAME)


def call_policy(msg_type, body):
    """Sends a request to the policy service and returns the reply."""
    _, policy_port = nrf_client.lookup("policy")

    sock = tcp.connect("127.0.0.1", policy_port)
    msg = formatter.format_message(
        src=SERVICE_NAME,
        dst="policy",
        msg_type=msg_type,
        body=body,
    )
    tcp.send_json(sock, msg)
    reply = tcp.recv_json(sock)
    sock.close()
    return reply


def call_upf_control(msg_type, body):
    """Sends a request to the upf_control service and returns the reply."""
    _, upf_control_port = nrf_client.lookup("upf_control")

    sock = tcp.connect("127.0.0.1", upf_control_port)
    msg = formatter.format_message(
        src=SERVICE_NAME,
        dst="upf_control", 
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
    sid_uuid = str(uuid.uuid4())
    session_id = f"{device_id}-{slice_id}-{sid_uuid}"

    rule_body = {
        "device_id": device_id,
        "slice_id": slice_id,
        "session_id": session_id,
        "ip_addr": ip_addr,
        "profile": profile,
    }
    _ = call_upf_control(
        api.upf.RULE_INSTALL,
        rule_body
    )

    # reply back to AMF with CreateSessionOk
    reply_body = rule_body  # return message is same as rule body for simplicity
    reply_body["admitted"] = True

    logging.log_verbose(SERVICE_NAME, f"CreateSession reply body: {reply_body}")
    
    return formatter.format_message(
        src=SERVICE_NAME,
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
    logging.log_error(SERVICE_NAME, f"unknown message type recieved: {msg_type}")
    return formatter.format_message(
        src=SERVICE_NAME,
        dst=formatter.get_src(msg), # send back to src
        msg_type=api.common.ERROR,
        body=reply_body,
        id=formatter.get_id(msg)
    )


def main(host, port):
    logging.log_info(SERVICE_NAME, f"listening on {host}:{port}")

    nrf_client.register(SERVICE_NAME, host, port)

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
        port = config.get_port("smf")

    main(host, port)