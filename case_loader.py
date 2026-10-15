# -*- coding: utf-8 -*-
"""
YAML case loader.
Conventions:
  1. Each *.yaml / *.yml file under cases/ is a collection of test cases.
  2. Top-level structure is a mapping: key = case ID, value = case body.
  3. Required fields: cat / sub / sub3 / pre / steps / expect
                      level / defense / owasp / note
  4. Files starting with "_" are reserved (e.g. _meta.yaml) and skipped.
  5. Invalid entries print a warning and are skipped, never breaking startup.
"""
import os

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

# Fields every case must declare
REQUIRED_FIELDS = (
    "cat", "sub", "sub3", "pre", "steps",
    "expect", "level", "defense", "owasp", "note",
)

CASES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cases")


def _iter_yaml_files(cases_dir):
    """Return YAML files sorted by name for reproducible load order."""
    if not os.path.isdir(cases_dir):
        return []
    files = []
    for name in os.listdir(cases_dir):
        if not name.lower().endswith((".yaml", ".yml")):
            continue
        if name.startswith("_"):          # reserved: _meta.yaml etc.
            continue
        files.append(os.path.join(cases_dir, name))
    return sorted(files)


def _validate_case(cid, data, source):
    """Validate one case; return dict or None on failure."""
    if not isinstance(data, dict):
        print(f"[case_loader] {source}: {cid} is not a mapping, skipped")
        return None
    missing = [f for f in REQUIRED_FIELDS if f not in data]
    if missing:
        print(f"[case_loader] {source}: {cid} missing fields {missing}, skipped")
        return None
    steps = data.get("steps")
    if not isinstance(steps, list) or not steps:
        print(f"[case_loader] {source}: {cid} steps must be a non-empty list, skipped")
        return None
    return {k: data[k] for k in REQUIRED_FIELDS}


def load_cases(cases_dir=None):
    """
    Return (CASE_LIB, CATEGORIES).

    Raises RuntimeError if PyYAML is missing.
    Returns empty structures if the directory does not exist.
    """
    if not HAS_YAML:
        raise RuntimeError("PyYAML not installed. Run: pip install pyyaml")

    cases_dir = cases_dir or CASES_DIR
    case_lib = {}
    for path in _iter_yaml_files(cases_dir):
        source = os.path.basename(path)
        try:
            with open(path, "r", encoding="utf-8") as f:
                doc = yaml.safe_load(f) or {}
        except Exception as e:
            print(f"[case_loader] failed to parse {source}: {e}, skipped")
            continue

        if not isinstance(doc, dict):
            print(f"[case_loader] {source} top-level is not a mapping, skipped")
            continue

        for cid, data in doc.items():
            if cid in case_lib:
                print(f"[case_loader] duplicate case ID {cid} in {source}, overwriting")
            validated = _validate_case(cid, data, source)
            if validated is not None:
                case_lib[cid] = validated

    categories = {}
    for cid, info in case_lib.items():
        categories.setdefault(info["cat"], []).append(cid)
    for cat in categories:
        categories[cat].sort()

    return case_lib, categories


def load_meta(meta_path=None):
    """
    Read _meta.yaml and return (CAT_META, TOOL_PAGES).
    Missing file yields ({}, []) so the caller can apply fallbacks.
    """
    if not HAS_YAML:
        raise RuntimeError("PyYAML not installed. Run: pip install pyyaml")

    meta_path = meta_path or os.path.join(CASES_DIR, "_meta.yaml")
    if not os.path.isfile(meta_path):
        return {}, []

    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            doc = yaml.safe_load(f) or {}
    except Exception as e:
        print(f"[case_loader] failed to parse _meta.yaml: {e}")
        return {}, []

    raw_cat_meta = doc.get("cat_meta", {}) or {}
    cat_meta = {}
    for cat, v in raw_cat_meta.items():
        if isinstance(v, list) and len(v) >= 2:
            cat_meta[cat] = (v[0], v[1])
        elif isinstance(v, dict):
            cat_meta[cat] = (v.get("icon", "📄"), v.get("desc", ""))

    raw_tools = doc.get("tool_pages", []) or []
    tool_pages = []
    for item in raw_tools:
        if isinstance(item, list) and len(item) >= 4:
            tool_pages.append(tuple(item[:4]))
        elif isinstance(item, dict):
            tool_pages.append((
                item.get("key", ""),
                item.get("icon", "🧩"),
                item.get("title", ""),
                item.get("desc", ""),
            ))

    return cat_meta, tool_pages