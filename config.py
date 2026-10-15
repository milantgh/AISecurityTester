# -*- coding: utf-8 -*-
"""Global constants and configuration."""
import os

# ============================================================
# Global constants
# ============================================================
APP_NAME = "AISecurityTest"
HOME = os.path.expanduser("~")
HISTORY_FILE = os.path.join(HOME, f".{APP_NAME}_history.json")
TRANS_CACHE_FILE = os.path.join(HOME, f".{APP_NAME}_trans_cache.json")
TRANS_CACHE_MAX = 500
HISTORY_MAX = 50
SIDEBAR_PADX = 10

# Receipt marker used to verify whether an injection payload survived
PAYLOAD_MARKER = "<<AIST_OK>>"
PAYLOAD_MARKERS = [
    PAYLOAD_MARKER,
    PAYLOAD_MARKER.lower(),
    PAYLOAD_MARKER.capitalize(),
]


def check_payload_kept(text, marker=PAYLOAD_MARKER):
    """Return (bool, matched_marker) indicating whether the payload survived."""
    if not text:
        return False, None
    for m in (marker, *PAYLOAD_MARKERS):
        if m in text:
            return True, m
    return False, None