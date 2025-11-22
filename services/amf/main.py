"""
Warren Shepard and Nand Patel
Dartmouth CS60 25F Final Project
14 Nov 2025

Main logic for AMF.
                   
                Base Station
                     |
                     |
                     |
           HERE --> AMF - - - Policy
                     |
                     |
                     |
                    SMF

LOGIC:                                                      MESSAGE:
    if RegistrationRequest recieved:                        (RegistrationRequest <- Base Station)
        call policy to get the allowed slices               (AllowedSlices -> Policy)
        register device and store allowed slices
    
    if SessionReqeust recieved:                             (SessionRequest <- Base Station)
        make sure device is registered
        ask policy if device is allowd on this slice        (Admit -> Policy)
        ask smf to register session                         ()
        
AI Statement: None.
"""

import sys

from common import formatter, tcp, logging, config
from common.nrf_client import NRFClient
from messages import api
from . import store

SERVICE_NAME = "amf"
nrf_client = NRFClient(service=SERVICE_NAME)


def call_policy(msg_type, body):
    """Sends a request to the policy service and returns the reply."""
    _, policy_port = nrf_client.lookup("policy")

    if policy_port is not None:

        sock = tcp.connect("127.0.0.1", policy_port)    # connect a socket
        msg = formatter.format_message(
            src=SERVICE_NAME,
            dst="policy",       # TODO: add all of these to a "constants" file or something in /common
            msg_type=msg_type,
            body=body,
        )
        tcp.send_json(sock, msg)
        reply = tcp.recv_json(sock)
        sock.close()
        return reply
    
    return False


def call_smf(msg_type, body):
    """Sends a request to the SMF service and returns the reply."""
    _, smf_port = nrf_client.lookup("smf")

    sock = tcp.connect("127.0.0.1", smf_port)    # connect a socket
    msg = formatter.format_message(
        src=SERVICE_NAME,
        dst="smf",
        msg_type=msg_type,
        body=body,
    )
    tcp.send_json(sock, msg)
    reply = tcp.recv_json(sock)
    sock.close()
    return reply


def handle_registration_request(request):
    """
    Handles a registration request.
    RegistrationRequest: {device_id}
    """
    # get header info
    src = formatter.get_src(request)
    id = formatter.get_id(request)

    # get type specific info
    body = request["body"]
    device_id = body["device_id"]

    # get allowed slices from policy service
    # TODO: error handling if the device is not in the policy
    policy_reply = call_policy(
        api.policy.GET_ALLOWED_SLICES,
        {"device_id": device_id}
    )

    # check for any errors
    policy_reply_type = formatter.get_type(policy_reply)

    if policy_reply_type == api.common.ERROR:
        # then the device cannot be registered
        error = policy_reply["body"]["error"]
        reply_body = {
            "registered": False,
            "device_id": device_id,
            "allowed_slices": None,
            "error": error
        }
        logging.log_error(SERVICE_NAME, f"revieced error from policy: {error}")
    else:
        # then we can successfully register the device
        # TODO: add some wrapper to ensure the correct message was recieved
        allowed_slices = policy_reply["body"]["allowed_slices"]

        # register device
        store.add_device(device_id, allowed_slices)

        # format reply
        reply_body = {
            "registered": True,
            "device_id": device_id,
            "allowed_slices": allowed_slices,
        }

    return formatter.format_message(
        src=SERVICE_NAME,
        dst=src,
        msg_type=api.amf.REGISTRATION_RESPONSE,
        body=reply_body,
        id=id,
    )


def handle_session_request(request):
    """
    Handles a session request.
    SessionRequest: {device_id, slice_id}
    """
    # get header info
    src = formatter.get_src(request)
    id = formatter.get_id(request)

    # get type specific info
    body = request["body"]
    device_id = body["device_id"]
    slice_id = body["slice_id"]

    registered = store.is_registered(device_id)
    if not registered:
        reply_body = {
            "admitted": False,
            "device_id": device_id,
            "slice_id": slice_id,
            "additional": "device not registered.",
        }
        logging.log_error(SERVICE_NAME, f"device {device_id} not registered.")
        return formatter.format_message(
            src=SERVICE_NAME,
            dst=src,
            msg_type=api.amf.SESSTION_RESPONSE,
            body=reply_body,
            id=id
        )

    # ask policy service if device is allowed on this slice
    admit_reply = call_policy(
        api.policy.ADMIT,
        {"device_id": device_id, "slice_id" :slice_id}
    )
    admit = admit_reply["body"]["admit"]

    if not admit:    # reject request
        reply_body = {
            "admitted": False,
            "device_id": device_id,
            "slice_id": slice_id,
            "additional": "slice not allowed or availible for device.",
        }
        logging.log_error(SERVICE_NAME, f"slice_id {slice_id} not allowed or availible for device")
        return formatter.format_message(
            src=SERVICE_NAME,
            dst=src,
            msg_type=api.amf.SESSTION_RESPONSE,
            body=reply_body,
            id=id,
        )

    # create session via SMF service
    smf_reply = call_smf(
        api.smf.CREATE_SESSION,
        {"device_id": device_id, "slice_id" :slice_id}
    )

    session_id = smf_reply["body"]["session_id"]
    ip_addr = smf_reply["body"]["ip_addr"]

    store.add_session(session_id, device_id, slice_id)

    # format reply
    # TODO: (IMPORTANT) probably send IP address as well
    reply_body = {
        "admitted": True,
        "device_id": device_id,
        "slice_id": slice_id,
        "session_id": session_id,
        "ip_addr": ip_addr,
    }
    return formatter.format_message(
        src=SERVICE_NAME,
        dst=src,
        msg_type=api.amf.SESSTION_RESPONSE,
        body=reply_body,
        id=id
    )


def handle_message(msg):
    """Handles a single incoming request. Returns the reply message (as a dictionary)."""
    msg_type = formatter.get_type(msg)  # get message type

    if msg_type == api.amf.REGISTRATION_REQUEST:
        return handle_registration_request(msg)
    if msg_type == api.amf.SESSTION_REQUEST:
        return handle_session_request(msg)
    
    # if other message type sent, return an error
    reply_body = {"error": f"unknown message type: {msg_type}"}
    logging.log_error(SERVICE_NAME, f"recieved unknown message type: {msg_type}")
    return formatter.format_message(
        src=SERVICE_NAME,
        dst=formatter.get_src(msg), # send back to src
        msg_type=api.common.ERROR,
        body=reply_body,
        id=formatter.get_id(msg),
    )


def main(host, port):
    logging.log_info(SERVICE_NAME, f"listening on {host}:{port}")

    # register service
    nrf_client.register(SERVICE_NAME, host, port)

    server_sock = tcp.listen(host, port)

    # listen for connections
    while True:
        client_sock, addr = server_sock.accept()
        logging.log_info(SERVICE_NAME, f"accepted connection from {addr}")

        # listen for messages until connection closes
        while True:
            msg = tcp.recv_json(client_sock)
            if msg is None:
                logging.log_info(SERVICE_NAME, "client closed connection.")
                break

            reply = handle_message(msg)
            tcp.send_json(client_sock, reply)

        client_sock.close()


if __name__ == "__main__":
    host = "127.0.0.1"

    # TODO: add parseargs to this cuz i don't like this format
    if len(sys.argv) >= 2:
        port = int(sys.argv[1])
    else:
        port = config.get_port("amf")

    main(host, port)