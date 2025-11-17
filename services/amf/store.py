"""
Warren Shepard and Nand Patel
Dartmouth CS60 25F Final Project
14 Nov 2025

AMF store.

AI Statement: 
"""


# TODO: add something to remove stale entries from devices/sessions dictionaries

devices = {}    # did -> allowed_slices
sessions = {}   # sid -> device_id/slice_id
# next_sid = 1    # the next session id # TODO: handle this in the smf


def add_device(device_id, allowed_slices):
    devices[device_id] = {"allowed_slices": allowed_slices}


def get_device(device_id):
    return devices.get(device_id)


def is_registered(device_id):
    return device_id in devices


# TODO: handle this in the smf
# def new_sid():
#     global next_sid
#     my_sid = f"session-{next_sid}"
#     next_sid += 1
#     return my_sid


def add_session(session_id, device_id, slice_id):
    sessions[session_id] = {
        "device_id": device_id,
        "slice_id": slice_id
    }