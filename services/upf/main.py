"""
Warren Shepard and Nand Patel
Dartmouth CS60 25F Final Project
19 Nov 2025

Main logic for SMF.

AI Statement: None.
"""

import sys
import threading

from common import tcp, logging, config
from . import control_plane, data_plane

SERVICE_NAME = "upf"


def control_listener(host, port):
    """Listener for the control plane."""
    logging.log_info(SERVICE_NAME, f"-control listening on {host}:{port}")

    server_sock = tcp.listen(host, port)    # for listening

    while True:
        # TODO: does this need to be multithreaded? i don't think so for our purposes...?
        client_sock, addr = server_sock.accept()   # for sending
        logging.log_info(SERVICE_NAME, f"-control accepted connection from {addr}")

        msg = tcp.recv_json(client_sock)
        if msg is not None:
            reply = control_plane.handle_message(msg)
            tcp.send_json(client_sock, reply)

        client_sock.close() # better to only keep connections open during use


def data_listener(host, port):
    """Listener for the data plane."""
    logging.log_info(SERVICE_NAME, f"-data listening on {host}:{port}")

    server_sock = tcp.listen(host, port)    # for listening

    while True:
        # TODO: does this need to be multithreaded? i don't think so for our purposes...?
        client_sock, addr = server_sock.accept()   # for sending
        logging.log_info(SERVICE_NAME, f"-data accepted connection from {addr}")

        msg = tcp.recv_json(client_sock)
        if msg is not None:
            reply = data_plane.handle_message(msg)
            tcp.send_json(client_sock, reply)

        client_sock.close() # better to only keep connections open during use


def main():
    host = "127.0.0.1"

    # TODO: (IMPORTANT) put these in the config then use the method to get them
    control_port = 9300
    data_port = 9301

    control_thread = threading.Thread(
        target=control_listener,
        args=(host, control_port),
        daemon=True
    )

    data_thread = threading.Thread(
        target=data_listener,
        args=(host, data_port),
        daemon=True
    )

    control_thread.start()
    data_thread.start()

    logging.info(SERVICE_NAME, " started (control + data)")

    control_thread.join()
    data_thread.join()


if __name__ == "__main__":
    
    if len(sys.argv) > 1:
        pass

    main()
