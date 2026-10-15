# -*- coding: utf-8 -*-
"""
Compatibility layer exposing CASE_LIB/CATEGORIES/CAT_META/TOOL_PAGES.
Actual data lives in cases/*.yaml. Falls back to a minimal built-in
CAT_META when YAML is unavailable.
"""
from .case_loader import load_cases, load_meta

_FALLBACK_CAT_META = {
    "Direct Prompt Injection": ("💉", "Instruction override, role jailbreak, attachment injection"),
}

# Load case library
try:
    CASE_LIB, CATEGORIES = load_cases()
except Exception as e:
    print(f"[case_lib] case loading failed: {e}")
    CASE_LIB, CATEGORIES = {}, {}

# Load metadata (category icons + tool pages)
try:
    CAT_META, TOOL_PAGES = load_meta()
except Exception as e:
    print(f"[case_lib] metadata loading failed: {e}")
    CAT_META, TOOL_PAGES = {}, []

if not CAT_META:
    CAT_META = dict(_FALLBACK_CAT_META)

# Ensure every category has an icon entry
for _cat in CATEGORIES:
    CAT_META.setdefault(_cat, ("📄", _cat))