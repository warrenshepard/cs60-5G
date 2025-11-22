"""
Warren Shepard and Nand Patel
Dartmouth CS60 25F Final Project
22 Nov 2025

Command-line device simulator.

Supports:
- RegistrationRequest (input device_id)
- SessionRequest (input device_id, slice_id)
- EchoRequest (input payload)
- FileRequest (input filename)

If a SessionResponse returns a session_id, it is stored and automatically
included in subsequent EchoRequest and FileRequest messages.

AI Statement: Used ChatGPT to write formatting for UI (i.e. main())
    Also, took ChatGPT's advice to not use square brackets to access items in messages,
    and to instead use `.get(item, default)`.
"""

import sys

from common import formatter, tcp, config
from common.config import load_policies
from messages import api

SERVICE_NAME = "device"
HOST = "127.0.0.1"
BASE_STATION_PORT = config.get_port("base_station")


def send_to_base_station(msg):
    """Connect to base station, send one message, receive one reply, then close."""
    try:
        sock = tcp.connect(HOST, BASE_STATION_PORT)
    except Exception as e:
        print(f"[device] ERROR: could not connect to base station: {e}")
        print("Make sure the network is up and running (`./run.sh`)")
        return None

    tcp.send_json(sock, msg)
    reply = tcp.recv_json(sock)
    sock.close()
    return reply


def do_register(device_id):
    """RegistrationRequest -> RegistrationResponse."""
    # form and send message
    body = {"device_id": device_id}
    msg = formatter.format_message(
        src=SERVICE_NAME,
        dst="base_station",
        msg_type=api.amf.REGISTRATION_REQUEST,
        body=body,
    )
    reply = send_to_base_station(msg)

    # parse reply
    if reply is None:
        print("No reply from network")
        return

    reply_type = formatter.get_type(reply)
    reply_body = reply["body"]

    if reply_type == api.common.ERROR:
        error = reply_body.get("error", "unknown")
        print(f"ERROR: {error}")
        return

    print(f"RegistrationResponse: {reply_body}")


def do_session(current_session_id, device_id, slice_id):
    """
    SessionRequest -> SessionResponse. 
    Returns updated session_id, or the old one if there was some error.
    """
    # format and send message
    body = {"device_id": device_id, "slice_id": slice_id}
    msg = formatter.format_message(
        src=SERVICE_NAME,
        dst="base_station",
        msg_type=api.amf.SESSTION_REQUEST,  # matches your existing constant
        body=body,
    )
    reply = send_to_base_station(msg)

    # parse reply
    if reply is None:
        print("No reply from network.")
        return current_session_id

    reply_type = formatter.get_type(reply)
    reply_body = reply["body"]

    if reply_type == api.common.ERROR:
        error = reply_body.get("error", "unknown")
        print(f"ERROR: {error}")
        return current_session_id

    print(f"SessionResponse: {reply_body}")

    # if not admitted try to get reason
    admitted = reply_body.get("admitted", False)
    if not admitted:
        reason = reply_body.get("additional") or reply_body.get("error") or "not admitted"
        print(f"Session not admitted: {reason}")
        return current_session_id

    # if there is a new session id then default to that
    new_session_id = reply_body.get("session_id")
    if new_session_id:
        print(f"New session_id: {new_session_id}")
        return new_session_id

    return current_session_id


def do_echo(current_session_id, payload):
    """Send an echo data-plane request using current session_id."""
    if current_session_id is None:
        print("No active session. Run 'sess' first.")
        return

    # create and send message
    body = {
        "session_id": current_session_id,
        "request_type": api.application.ECHO_REQUEST,
        "payload": payload,
    }
    msg = formatter.format_message(
        src=SERVICE_NAME,
        dst="base_station",
        msg_type=api.upf.USER_DATA_UP,
        body=body,
    )

    # get reply
    reply = send_to_base_station(msg)
    if reply is None:
        print("No reply from network.")
        return

    # parse reply
    reply_type = formatter.get_type(reply)
    reply_body = reply["body"]

    if reply_type == api.common.ERROR:
        error = reply_body.get("error", "unknown")
        print(f"ERROR: {error}")
        return

    print(f"Echo reply: {reply_body}")


def do_file(current_session_id, filename):
    """Send a file request (using current session_id)."""
    # if the user doesn't know what's going on lol
    if current_session_id is None:
        print("No active session. Run 'sess' first.")
        return

    # create and send message
    body = {
        "session_id": current_session_id,
        "request_type": api.application.FILE_REQUEST,
        "filename": filename,
    }
    msg = formatter.format_message(
        src=SERVICE_NAME,
        dst="base_station",
        msg_type=api.upf.USER_DATA_UP,
        body=body,
    )

    # get reply
    reply = send_to_base_station(msg)

    # parese reply
    if reply is None:
        print("No reply from network. Make sure the network is actually running (`./run.sh`)!")
        return

    reply_type = formatter.get_type(reply)
    reply_body = reply["body"]

    if reply_type == api.common.ERROR:
        error = reply_body.get("error", "unknown")
        print(f"ERROR: {error}")
        return

    print("File reply:")
    print(reply_body)


def main():
    print("Device Commands:")
    print("  reg  <device_id>")
    print("  sess <device_id> <slice_id>")
    print("  echo <payload...>")
    print("  file <filename>")
    print("  quit")
    print()
    print("Note that you need to run in the order of reg -> sess -> echo/file in order to" \
        "get a valid echo/file response. This is becuase a device would first need to register," \
        "then register it's session, and finally be able to access the network. We choose to do it" \
        "this way becuase it's more fun and shows you how the Network actually works. Also," \
        "you would otherwise be stuck with a really simple file fetcher which would be really boring" \
        "and stupid considering the amount of work put into this project!")
    
    print()

    policies = load_policies()
    devices = policies.get("devices", {})
    print("Available devices (from policies.json):")
    for dev_id, cfg in devices.items():
        allowed = cfg.get("allowed_slices", [])
        print(f"  {dev_id}: {allowed}")
    print()

    current_session_id = None

    while True:
        line = input("> ").strip()
        if not line:
            continue

        parts = line.split()
        cmd = parts[0].lower()
        args = parts[1:]

        if cmd in ("quit", "q", "exit"):
            print("bye")
            break

        elif cmd == "reg":
            if len(args) != 1:
                print("usage: reg <device_id>")
                continue
            do_register(args[0])

        elif cmd == "sess":
            if len(args) != 2:
                print("usage: sess <device_id> <slice_id>")
                continue
            current_session_id = do_session(current_session_id, args[0], args[1])

        elif cmd == "echo":
            if len(args) < 1:
                print("usage: echo <payload...>")
                continue
            payload = " ".join(args)
            do_echo(current_session_id, payload)

        elif cmd == "file":
            if len(args) != 1:
                print("usage: file <filename>")
                continue
            do_file(current_session_id, args[0])

        else:
            print("unknown command (use: reg, sess, echo, file, quit)")


if __name__ == "__main__":
    main()