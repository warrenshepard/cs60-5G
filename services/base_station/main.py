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

AI Statement: Used ChatGPT for debugging main()

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
            logging.log_error(SERVICVE_NAME, f"unsupported message type from device: {msg_type}")
            
            reply_body = {"error": f"unknown message type: {msg_type}"}
            reply_msg = formatter.format_message(
                src=SERVICVE_NAME,
                dst=formatter.get_src(msg), # send back to src; should just be device
                msg_type=api.common.ERROR,
                body=reply_body,
                id=formatter.get_id(msg),
            )
            tcp.send_json(device_sock, reply_msg)


def amf_to_device(amf_sock, device_sock):
    """Relays messages from the AMF to the device."""
    logging.log_info(SERVICVE_NAME, "amf_to_device relaying started.")

    while True:
        msg = tcp.recv_json(amf_sock)
        if msg is None:
            logging.log_info(SERVICVE_NAME, "amf_to_device: device or AMF closed connection.")
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
            logging.log_info(SERVICVE_NAME, "upf_to_device: device or UPF closed connection.")
            break
        
        # relay message to device
        msg_type = formatter.get_type(msg)
        logging.log_info(SERVICVE_NAME, f"forwarding data message of type {msg_type} from UPF to device.")
        tcp.send_json(device_sock, msg)

def handle_device(device_sock, addr):
    """Handles one device connection: sets up AMF+UPF links and relay threads."""
    logging.log_info(SERVICVE_NAME, f"handling new device from {addr}")

    amf_port = config.get_port("amf")
    upf_port = config.get_port("upf_data")

    # connect with AMF
    logging.log_info(SERVICVE_NAME, f"connecting to AMF on {HOST}:{amf_port}.")
    amf_sock = tcp.connect(HOST, amf_port)

    # connect with UPF
    logging.log_info(SERVICVE_NAME, f"connecting to UPF on {HOST}:{upf_port}.")
    upf_sock = tcp.connect(HOST, upf_port)

    # relay threads for this device
    device_to_core_t = threading.Thread(
        target=device_to_core,
        args=(device_sock, amf_sock, upf_sock),
        daemon=True,
    )
    amf_to_device_t = threading.Thread(
        target=amf_to_device,
        args=(amf_sock, device_sock),
        daemon=True,
    )
    upf_to_device_t = threading.Thread(
        target=upf_to_device,
        args=(upf_sock, device_sock),
        daemon=True,
    )

    logging.log_info(SERVICVE_NAME, "starting relaying threads for device.")
    device_to_core_t.start()
    amf_to_device_t.start()
    upf_to_device_t.start()

    # when the device->core thread ends (device closed), we shut things down
    device_to_core_t.join()

    # close sockets; the other threads will see recv_json return None / error and exit
    logging.log_info(SERVICVE_NAME, "device_to_core finished, closing sockets.")
    try:
        device_sock.close()
    except Exception:
        pass
    try:
        amf_sock.close()
    except Exception:
        pass
    try:
        upf_sock.close()
    except Exception:
        pass

    logging.log_info(SERVICVE_NAME, f"finished handling device {addr}")


def main():
    device_port = 8640  # listening port for device connections
    logging.log_info(SERVICVE_NAME, f"listening for devices on {HOST}:{device_port}.")

    listen_sock = tcp.listen(HOST, device_port)

    # accept multiple devices over time
    while True:
        device_sock, addr = listen_sock.accept()
        logging.log_info(SERVICVE_NAME, f"accepted device connection from {addr}.")

        # spawn a handler thread for this device
        t = threading.Thread(
            target=handle_device,
            args=(device_sock, addr),
            daemon=True,
        )
        t.start()


if __name__ == "__main__":
    main()