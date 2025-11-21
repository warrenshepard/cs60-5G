"""
Warren Shepard and Nand Patel
Dartmouth CS60 25F Final Project
20 Nov 2025

Unit tests for common.config methods.

This was used to debug common.config.py (and helped catch several bugs).

Run with: `pytest tests/unit/common/test_tcp.py`

AI Statement: ChatGPT wrote almost this whole thing (with Piersons permission to do this).
    To generate, we described each method that we wanted and what the input and correct output that should
    be tested should be. 

    Note that we did check each method that ChatGPT came up with thoroughly and modified it as we saw fit!
"""

import socket

from common import tcp


def test_send_and_recv_json_round_trip_over_tcp():
    """
    Full round trip using listen() and connect() on localhost.
    This exercises listen, connect, send_json, and recv_json together.
    """
    host = "127.0.0.1"

    # Start a listening socket on an ephemeral port (0 = let OS choose)
    server_sock = tcp.listen(host, 0)
    server_host, server_port = server_sock.getsockname()

    # Connect a client to the server
    client_sock = tcp.connect(server_host, server_port)

    # Accept the connection on the server side
    conn_sock, _ = server_sock.accept()

    try:
        message = {"hello": "world", "number": 42}

        # Client sends JSON
        tcp.send_json(client_sock, message)

        # Server receives JSON
        received = tcp.recv_json(conn_sock)

        assert received == message
    finally:
        client_sock.close()
        conn_sock.close()
        server_sock.close()


def test_send_and_recv_json_with_socketpair():
    """
    Use a local socketpair to test send_json and recv_json without networking.
    """
    sock_a, sock_b = socket.socketpair()

    try:
        msg = {"type": "test", "value": "abc"}

        # A sends, B receives
        tcp.send_json(sock_a, msg)
        received = tcp.recv_json(sock_b)

        assert received == msg
    finally:
        sock_a.close()
        sock_b.close()


def test_send_json_appends_newline():
    """
    Ensure send_json terminates the JSON with a newline, so recv_json knows where to stop.
    """
    sock_a, sock_b = socket.socketpair()

    try:
        msg = {"foo": "bar"}
        tcp.send_json(sock_a, msg)

        # Read raw bytes on the other side
        data = sock_b.recv(1024)
        assert data.endswith(b"\n")
    finally:
        sock_a.close()
        sock_b.close()


def test_recv_json_returns_none_on_empty_stream():
    """
    If the other side closes without sending anything, recv_json should return None.
    """
    sock_a, sock_b = socket.socketpair()

    try:
        # Close the writer without sending
        sock_a.close()

        # Receiver should get None
        result = tcp.recv_json(sock_b)
        assert result is None
    finally:
        # sock_a is already closed
        sock_b.close()