"""
Warren Shepard and Nand Patel
Dartmouth CS60 25F Final Project
13 Nov 2025

Common message formatter to enforce standard headers.

Note: we choose not to put this file in the /messages folder becuase
that folder is for defining the TYPES and BODYS of specific messages,
whereas this is more for formatting the headers.

AI Statement: None
"""

import time
import uuid

# note: src and dst are strings of service names, for example "nrf"
def format_message(src, dst, msg_type, body, id=None):
    """
    Create a message with a standard format and header.
    Returns a dictionary, which can easily be converted to a json.
    """
    # assign a uuid
    if id is None:
        id = str(uuid.uuid5())

    header = {
        "src": src,
        "dst": dst,
        "type": msg_type,
        "id": id,
        "time": time.time(),
    }

    return {"header": header, "body": body}

 
def get_src(msg):
    return msg["header"]["src"]

def get_dst(msg):
    return msg["header"]["dst"]

def get_type(msg):
    return msg["header"]["type"]

def get_id(msg):
    return msg["header"]["id"]