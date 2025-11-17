"""
Warren Shepard and Nand Patel
Dartmouth CS60 25F Final Project
14 Nov 2025

Functions to directly evaluate against the configured policies

AI Statement: None.
"""

from common.config import load_policies

def get_allowed_slices(device_id):
    """Returns list of allowed slice IDs for given device."""
    policies = load_policies()
    device_config = policies.get("device_id, {}")
    return device_config.get("allowed_slices", [])


def admit(device_id, slice_id):
    """
    Decides if a device can be admitted to a given slice.
    For now just admit if the slice is in allowed_slices.
    TODO: add logic to this to reject if say too many devices have sessions on a slice
    or if the slice is availible in that particular region (this would be really cool)
    """
    # TODO: check if slice is not at capacity
        # might need to make a class called "store" to store this data, idk,
        # if this should even go here cuz it's not necissarily policy stuff
        # as it requires a live data layer to keep track of which are connected

    # TODO: check if slice is availible in given region
        # probably by longitude/latitude
        # this will defintly go here

    allowed = get_allowed_slices(device_id)
    return slice_id in allowed


def get_profile(slice_id):
    """Gets the profile dictionary for a slice"""
    policies = load_policies()
    slices = policies.get("slices", {})
    slice_config = slices.get(slice_id, {})
    return slice_config.get("profile", {})