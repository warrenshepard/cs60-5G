"""
Warren Shepard and Nand Patel
Dartmouth CS60 25F Final Project
19 Nov 2025

Rule store for UPF.
"""

rules = {}  # session-id -> rule


def install_rule(session_id, rule):
    """Add or update the rule for a session."""
    rules[session_id] = rule


def get_rule(session_id):
    """Get the rule for a session."""
    return rules.get(session_id, None)