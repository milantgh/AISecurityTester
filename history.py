# -*- coding: utf-8 -*-
"""History persistence."""
import json
import os

from .config import HISTORY_FILE, HISTORY_MAX

# ============================================================
# History
# ============================================================
def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f) or []
        except Exception:
            return []
    return []


def save_history(records):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(records[-HISTORY_MAX:], f, ensure_ascii=False, indent=2)
    except Exception:
        pass