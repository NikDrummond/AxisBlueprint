"""Recently opened/saved layout file paths (for File menu)."""

import json
import os

MAX_RECENT = 10


def _recent_path():
    base = os.path.join(os.path.expanduser("~"), ".config", "axisblueprint")
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, "recent_layouts.json")


def load_recent_paths():
    path = _recent_path()
    if not os.path.isfile(path):
        return []
    try:
        with open(path, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return []
    if not isinstance(data, list):
        return []
    out = []
    for p in data:
        if isinstance(p, str) and p:
            out.append(os.path.normpath(p))
    return out


def save_recent_paths(paths):
    path = _recent_path()
    try:
        with open(path, "w") as f:
            json.dump(paths[:MAX_RECENT], f, indent=2)
    except OSError:
        pass


def add_recent_path(filepath):
    filepath = os.path.normpath(os.path.abspath(filepath))
    paths = load_recent_paths()
    paths = [p for p in paths if p != filepath]
    paths.insert(0, filepath)
    save_recent_paths(paths)
