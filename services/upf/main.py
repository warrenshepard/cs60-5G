"""
Warren Shepard and Nand Patel
Dartmouth CS60 25F Final Project
19 Nov 2025

Main logic for SMF.

                Base Station             SMF        
                     |                    |
                     |                    |
                     |                    |
         HERE --> UPF Data - - - - - UPF Control
                     |
                     |
                     |
                Application

AI Statement: None.
"""

import sys
import threading

from common import tcp, logging, config
from common.nrf_client import NRFClient
from . import control_plane, data_plane

SERVICE_NAME = "upf"
nrf_client = NRFClient(service=SERVICE_NAME)


def control_listener(host, port):
    """Listener for the control plane."""
    logging.log_info(SERVICE_NAME, f"control listening on {host}:{port}")

    server_sock = tcp.listen(host, port)    # for listening

    while True:
        client_sock, addr = server_sock.accept()   # for sending
        logging.log_info(SERVICE_NAME, f"control accepted connection from {addr}")

        msg = tcp.recv_json(client_sock)
        if msg is not None:
            reply = control_plane.handle_message(msg)
            tcp.send_json(client_sock, reply)

        client_sock.close() # better to only keep connections open during use


def data_listener(host, port):
    """Listener for the data plane."""
    logging.log_info(SERVICE_NAME, f"data listening on {host}:{port}")

    server_sock = tcp.listen(host, port)    # for listening

    while True:
        client_sock, addr = server_sock.accept()   # for sending
        logging.log_info(SERVICE_NAME, f"data accepted connection from {addr}")

        msg = tcp.recv_json(client_sock)
        if msg is not None:
            reply = data_plane.handle_message(msg)
            tcp.send_json(client_sock, reply)

        client_sock.close() # better to only keep connections open during use


def main():
    host = "127.0.0.1"

    control_port = config.get_port("upf_control")
    data_port = config.get_port("upf_data")

    nrf_client.register("upf_control", host, control_port)
    nrf_client.register("upf_data", host, data_port)

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

    logging.log_info(SERVICE_NAME, "started (control + data)")

    control_thread.join()
    data_thread.join()


if __name__ == "__main__":

    if len(sys.argv) > 1:
        pass

    main()
