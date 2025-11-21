"""
Warren Shepard and Nand Patel
Dartmouth CS60 25F Final Project
20 Nov 2025

To test the base station layer.

AI Statement: None
"""

from common import tcp, config, formatter
from messages import api

HOST = "127.0.0.1"
DEVICE_PORT = 8640

def test_device_base_station_connection():
    """Tests that the device can connect to the base station."""

    # connect to the base station
    sock = tcp.connect(HOST, DEVICE_PORT)

    # craft a registration request
    msg = formatter.format_message(
        src="device",
        dst="base_station",
        msg_type="UnknownType",
        body={"device_id": "001"}
    )

    tcp.send_json(sock, msg)

    # passes as long as we got here without any errors
    assert True


def test_unknown_message_type_from_device():
    """Tests that error is given if unknown message type is send to base station."""

    # connect to the base station
    sock = tcp.connect(HOST, DEVICE_PORT)

    # craft a registration request
    msg = formatter.format_message(
        src="device",
        dst="base_station",
        msg_type="UnknownType",
        body={"device_id": "001"}
    )

    tcp.send_json(sock, msg)

    reply = tcp.recv_json(sock)

    expected_error = "unknown message type: UnknownType"
    
    reply_type = formatter.get_type(reply)
    error = reply["body"]["error"]

    assert reply_type == api.common.ERROR
    assert error == expected_error


def test_registration_request():
    """Tests that the device can register in the network."""

    # connect to the base station
    sock = tcp.connect(HOST, DEVICE_PORT)

    # craft a registration request
    msg = formatter.format_message(
        src="device",
        dst="base_station",
        msg_type=api.amf.REGISTRATION_REQUEST,
        body={"device_id": "001"},
        id="test"
    )

    tcp.send_json(sock, msg)

    reply = tcp.recv_json(sock)

    reply_id = formatter.get_id(reply)
    reply_type = formatter.get_type(reply)
    reply_body = reply["body"]
    device_registered = reply_body["registered"]

    assert reply_id == "test"
    assert reply_type == api.amf.REGISTRATION_RESPONSE
    assert device_registered == True


def test_registration_request_bad_device():
    """Tests that the device cannot register if it is unsubscribed."""

    # connect to the base station
    sock = tcp.connect(HOST, DEVICE_PORT)

    # craft a registration request
    msg = formatter.format_message(
        src="device",
        dst="base_station",
        msg_type=api.amf.REGISTRATION_REQUEST,
        body={"device_id": "067"},
        id="test"
    )

    tcp.send_json(sock, msg)

    reply = tcp.recv_json(sock)

    print(reply)

    reply_id = formatter.get_id(reply)
    reply_type = formatter.get_type(reply)
    reply_body = reply["body"]
    device_registered = reply_body["registered"]
    error = reply_body["error"]
    allowed_slices = reply_body["allowed_slices"]
    device_id = reply_body["device_id"]

    assert reply_id == "test"
    assert reply_type == api.amf.REGISTRATION_RESPONSE
    assert device_registered == False
    assert error == "device 067 not subscribed"
    assert device_id == "067"
    assert allowed_slices is None