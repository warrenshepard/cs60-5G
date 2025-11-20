"""
Warren Shepard and Nand Patel
Dartmouth CS60 25F Final Project
20 Nov 2025

Base Station (mock-up of a cell tower).

Messages are relayed from the device to the amf and upf, and vice versa.
           
                     Device
                        |
                        |
                        |
                  Base station
                     /    \ 
   (USER_DATA_UP)   /      \   (REGISTRATION_REQUEST, SESSION_REQUEST)
                   /        \ 
                 UPF        AMF

AI Statement: None.

TODO: multithread even more so that we can listen in on multiple devices
TODO: security wrapper
TODO: noise simulation and polar encoding (should be not too bad?)
        i think that polar coding is on radio layer so would need to make system for that
"""

import sys
import threading

from common import tcp, logging, config, formatter
from messages import api

# globals
SERVICVE_NAME = "base_station"
HOST = "127.0.0.1"

# control and data plane messages relayed
# control are all to AMF, data are all to UPF
CONTROL = [
    api.amf.REGISTRATION_REQUEST,
    api.amf.SESSTION_REQUEST
]
DATA = [
    api.upf.USER_DATA_UP
]

def device_to_core(device_sock, amf_sock, upf_sock):
    """Relays messages from device to amf and upf."""
    logging.log_info(SERVICVE_NAME, "device_to_core relaying started.")

    while True:
        msg = tcp.recv_json(device_sock)
        if msg is None:
            logging.log_info(SERVICVE_NAME, "device_to_core: device closed connection.")
            break

        msg_type = formatter.get_type(msg)

        if msg_type in CONTROL:
            logging.log_info(SERVICVE_NAME, f"forwarding control plane message {msg_type} to AMF")
            tcp.send_json(amf_sock, msg)    # forward the message to the AMF
        elif msg_type in DATA:
            logging.log_info(SERVICVE_NAME, f"forwarding data plane message {msg_type} to UPF")
            tcp.send_json(upf_sock, msg)
        else:
            # filter out unknown messages here since we don't know where to send them
            logging.log_info(SERVICVE_NAME, f"unsupported message type from device: {msg_type}")

    # clean up
    # TODO: do i need to do this here as well as in other places?
    device_sock.close()
    amf_sock.close()
    upf_sock.close()


def amf_to_device(amf_sock, device_sock):
    """Relays messages from the AMF to the device."""
    logging.log_info(SERVICVE_NAME, "amf_to_device relaying started.")

    while True:
        msg = tcp.recv_json(amf_sock)
        if msg is None:
            logging.log_info(SERVICVE_NAME, "amf_to_device: AMF closed connection.")
            break
        
        # relay message to device
        msg_type = formatter.get_type(msg)
        logging.log_info(SERVICVE_NAME, f"forwarding control message of type {msg_type} from AMF to device.")
        tcp.send_json(device_sock, msg)


def upf_to_device(upf_sock, device_sock):
    """Relays messages from the UPF to the device."""
    logging.log_info(SERVICVE_NAME, "upf_to_device relaying started.")

    while True:
        msg = tcp.recv_json(upf_sock)
        if msg is None:
            logging.log_info(SERVICVE_NAME, "upf_to_device: UPF closed connection.")
            break
        
        # relay message to device
        msg_type = formatter.get_type(msg)
        logging.log_info(SERVICVE_NAME, f"forwarding data message of type {msg_type} from UPF to device.")
        tcp.send_json(device_sock, msg)


def main():
    device_port = config.get_port("device") # TODO: change this so that we can connect with mulitple devices
    # maybe their connections can be stored in a dictionary?

    upf_port = config.get_port("upf")
    amf_port = config.get_port("amf")

    # connect with device
    # TODO: change this to be able to conect to multiple devices
    logging.log_info(SERVICVE_NAME, f"connecting to device on {HOST}:{device_port}.")
    device_listen_sock = tcp.listen(HOST, device_port)
    device_sock, addr = device_listen_sock.accept()
    logging.log_info(SERVICVE_NAME, f"accepted device connection from {addr}.")

    # connect with AMF
    logging.log_info(SERVICVE_NAME, f"connecting to AMF on {HOST}:{amf_port}.")
    amf_sock = tcp.connect(HOST, amf_port)

    # connect with UPF
    logging.log_info(SERVICVE_NAME, f"connecting to UPF on {HOST}:{upf_port}.")
    upf_sock = tcp.connect(HOST, upf_port)

    # create threads
    device_to_core_t = threading.Thread(
        target=device_to_core,
        args=(device_sock, amf_sock, upf_sock),
        daemon=True
    )
    amf_to_device_t = threading.Thread(
        target=amf_to_device,
        args=(amf_sock, device_sock),
        daemon=True
    )
    upf_to_device_t = threading.Thread(
        target=upf_to_device,
        args=(upf_sock, device_sock),
        daemon=True
    )

    # start threads
    logging.log_info(SERVICVE_NAME, f"starting all threads.")
    device_to_core_t.start()
    amf_to_device_t.start()
    upf_to_device_t.start()
    logging.log_info(SERVICVE_NAME, f"started all threads (device -> amf/upf, amf -> device, upf -> device)")

    # join threads
    device_to_core_t.join()
    amf_to_device_t.join()
    upf_to_device_t.join()

    # clean up
    device_sock.close()
    amf_sock.close()
    upf_sock.close()


if __name__ == "__main__":
    main()