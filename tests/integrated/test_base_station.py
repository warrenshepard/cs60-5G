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
BASE_STATION_PORT = config.get_port("base_station")


def _create_session(sock):
    """Creates session for device_id 001"""  

    # first send session request (for a device that already registered)
    request_body = {
        "device_id": "001",
        "slice_id": "eMBB" 
    }
    msg = formatter.format_message(
        src="device",
        dst="base_station",
        msg_type=api.amf.SESSTION_REQUEST,
        body=request_body,
        id="test"
    )

    tcp.send_json(sock, msg)

    reply = tcp.recv_json(sock)

    # get the session id
    reply_body = reply["body"]
    session_id = reply_body["session_id"]

    return session_id



def test_device_base_station_connection():
    """Tests that the device can connect to the base station."""

    # connect to the base station
    sock = tcp.connect(HOST, BASE_STATION_PORT)

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
    sock = tcp.connect(HOST, BASE_STATION_PORT)

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
    sock = tcp.connect(HOST, BASE_STATION_PORT)

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
    sock = tcp.connect(HOST, BASE_STATION_PORT)

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


def test_session_request():
    """Tests that the device can request a session."""

    # connect to the base station
    sock = tcp.connect(HOST, BASE_STATION_PORT)

    # craft a session request (for a device that already registered)
    request_body = {
        "device_id": "001",
        "slice_id": "eMBB" 
    }
    msg = formatter.format_message(
        src="device",
        dst="base_station",
        msg_type=api.amf.SESSTION_REQUEST,
        body=request_body,
        id="test"
    )

    tcp.send_json(sock, msg)

    reply = tcp.recv_json(sock)

    print(reply)

    reply_id = formatter.get_id(reply)
    reply_type = formatter.get_type(reply)
    reply_body = reply["body"]
    device_admitted = reply_body["admitted"]

    assert reply_id == "test"
    assert reply_type == api.amf.SESSTION_RESPONSE
    assert device_admitted == True


def test_session_request_device_not_registered():
    """Tests that the device can request a session."""

    # connect to the base station
    sock = tcp.connect(HOST, BASE_STATION_PORT)

    # craft a session request (for a device that's not registered)
    request_body = {
        "device_id": "003",
        "slice_id": "eMBB" 
    }
    msg = formatter.format_message(
        src="device",
        dst="base_station",
        msg_type=api.amf.SESSTION_REQUEST,
        body=request_body,
        id="test"
    )

    tcp.send_json(sock, msg)

    reply = tcp.recv_json(sock)

    print(reply)

    reply_id = formatter.get_id(reply)
    reply_type = formatter.get_type(reply)
    reply_body = reply["body"]
    device_admitted = reply_body["admitted"]
    additional = reply_body["additional"]

    assert reply_id == "test"
    assert reply_type == api.amf.SESSTION_RESPONSE
    assert device_admitted == False
    assert additional == "device not registered."


def test_session_request_device_not_subscribed_or_registered():
    """Tests that the device can request a session."""

    # connect to the base station
    sock = tcp.connect(HOST, BASE_STATION_PORT)

    # craft a session request (for a device that already registered)
    request_body = {
        "device_id": "idontbelong",
        "slice_id": "eMBB" 
    }
    msg = formatter.format_message(
        src="device",
        dst="base_station",
        msg_type=api.amf.SESSTION_REQUEST,
        body=request_body,
        id="test"
    )

    tcp.send_json(sock, msg)

    reply = tcp.recv_json(sock)

    print(reply)

    reply_id = formatter.get_id(reply)
    reply_type = formatter.get_type(reply)
    reply_body = reply["body"]
    device_admitted = reply_body["admitted"]
    additional = reply_body["additional"]

    assert reply_id == "test"
    assert reply_type == api.amf.SESSTION_RESPONSE
    assert device_admitted == False
    assert additional == "device not registered."


def test_session_request_bad_slice_id():
    """Tests that the device can request a session."""

    # connect to the base station
    sock = tcp.connect(HOST, BASE_STATION_PORT)

    # craft a session request (for a device that already registered)
    request_body = {
        "device_id": "001",
        "slice_id": "idontexist" 
    }
    msg = formatter.format_message(
        src="device",
        dst="base_station",
        msg_type=api.amf.SESSTION_REQUEST,
        body=request_body,
        id="test"
    )

    tcp.send_json(sock, msg)

    reply = tcp.recv_json(sock)

    print(reply)

    reply_id = formatter.get_id(reply)
    reply_type = formatter.get_type(reply)
    reply_body = reply["body"]
    device_admitted = reply_body["admitted"]
    additional = reply_body["additional"]

    assert reply_id == "test"
    assert reply_type == api.amf.SESSTION_RESPONSE
    assert device_admitted == False
    assert additional == "slice not allowed or availible for device."


def test_session_request_slice_id_not_allowed():
    """Tests that the device can request a session."""

    # connect to the base station
    sock = tcp.connect(HOST, BASE_STATION_PORT)

    # first register device 002 (since it hasn't been registered yet)
    # craft a registration request
    msg = formatter.format_message(
        src="device",
        dst="base_station",
        msg_type=api.amf.REGISTRATION_REQUEST,
        body={"device_id": "002"},
        id="test"
    )

    tcp.send_json(sock, msg)

    reply = tcp.recv_json(sock)

    print(reply)

    reply_id = formatter.get_id(reply)
    reply_type = formatter.get_type(reply)
    reply_body = reply["body"]
    device_registered = reply_body["registered"]

    assert reply_id == "test"
    assert reply_type == api.amf.REGISTRATION_RESPONSE
    assert device_registered == True

    # now craft a session request (for a device that already registered)
    request_body = {
        "device_id": "002",
        "slice_id": "URLLC" 
    }
    msg = formatter.format_message(
        src="device",
        dst="base_station",
        msg_type=api.amf.SESSTION_REQUEST,
        body=request_body,
        id="test"
    )

    print(msg)

    tcp.send_json(sock, msg)

    reply = tcp.recv_json(sock)

    print(reply)

    reply_id = formatter.get_id(reply)
    reply_type = formatter.get_type(reply)
    reply_body = reply["body"]
    device_admitted = reply_body["admitted"]
    additional = reply_body["additional"]

    assert reply_id == "test"
    assert reply_type == api.amf.SESSTION_RESPONSE
    assert device_admitted == False
    assert additional == "slice not allowed or availible for device."


def test_user_data_up_echo():
    """Tests a baic echo request."""
    # create sock
    sock = tcp.connect(HOST, BASE_STATION_PORT)

    # get the session id
    session_id = _create_session(sock)
    # then create make a request to the UPF
    request_body = {
        "device_id": "001",
        "session_id": session_id,
        "request_type": api.application.ECHO_REQUEST,
        "payload": "test123"
    }
    msg = formatter.format_message(
        src="device",
        dst="base_station",
        msg_type=api.upf.USER_DATA_UP,
        body=request_body,
        id="test"
    )
    tcp.send_json(sock, msg)

    reply = tcp.recv_json(sock)

    print(reply)

    reply_id = formatter.get_id(reply)
    reply_type = formatter.get_type(reply)
    reply_body = reply["body"]
    reply_session_id = reply_body["session_id"]
    reply_payload = reply_body["payload"]

    assert reply_id == "test"
    assert reply_type == api.upf.USER_DATA_DOWN
    assert reply_session_id == session_id
    assert reply_payload == "APPLICATION ECHO: test123"


def test_user_data_up_file_request():
    """Tests a baic echo request."""
    # create sock
    sock = tcp.connect(HOST, BASE_STATION_PORT)

    # get the session id
    session_id = _create_session(sock)
    # then create make a request to the UPF
    request_body = {
        "device_id": "001",
        "session_id": session_id,
        "request_type": api.application.FILE_REQUEST,
        "filename": "test.txt"
    }
    msg = formatter.format_message(
        src="device",
        dst="base_station",
        msg_type=api.upf.USER_DATA_UP,
        body=request_body,
        id="test"
    )
    tcp.send_json(sock, msg)

    reply = tcp.recv_json(sock)

    print(reply)

    reply_id = formatter.get_id(reply)
    reply_type = formatter.get_type(reply)
    reply_body = reply["body"]
    reply_session_id = reply_body["session_id"]
    reply_file_found = reply_body["found"]
    reply_content = reply_body["content"]

    assert reply_id == "test"
    assert reply_type == api.upf.USER_DATA_DOWN
    assert reply_session_id == session_id
    assert reply_file_found == True
    assert reply_content == "blahblahblah"

    

# TODO: 
# bad session id
# no payload
# everything that would lead to an error maybe

