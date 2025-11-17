"""
Warren Shepard and Nand Patel
Dartmouth CS60 25F Final Project
13 Nov 2025

Common TCP functions for sending/recieving JSON objects.

AI Statement: used ChatGPT to figure out how the json library worked.
"""

import json
import socket


def connect(host, port):
    """Connects to host:port and returns the connected socket."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    return sock


# note: may want to add a backlog here to limit the number of connections that
# can be "waiting in line" at any given moment
def listen(host, port):
    """Binds and listens on host:port and returns the listening socket."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.listen()
    return sock


def send_json(sock, message):
    """
    Sends a JSON object with new line at end to denote end. 
    `message` is assumed to be a dictionary.
    """
    data = json.dumps(message)  # convert to JSON
    sock.sendall((data + "\n").encode("utf-8")) # newline denotes end of file


def recv_json(sock):
    """
    Recieves a json object.
    Returns in form of a dictionary.
    """
    buffer = []
    while True:
        chunk = sock.recv(1)
        if not chunk:
            break
        if chunk == b"\n":  # signals end of JSON object
            break
        buffer.append(chunk)

    line = b"".join(buffer).decode("utf-8")
    if not line:
        return None
    return json.loads(line) # convert to JSON object