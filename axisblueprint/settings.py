"""Persistent user settings (loaded from ~/.config/axisblueprint/settings.json)."""

import json
import os

_CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "axisblueprint")
_SETTINGS_PATH = os.path.join(_CONFIG_DIR, "settings.json")

DEFAULT_SETTINGS = {
    "templates_dir": "",
    "default_grid_spacing_cm": 0.2,
    "default_margins": {
        "left": 1.0,
        "right": 1.0,
        "top": 1.0,
        "bottom": 1.0,
    },
    "default_canvas_width_cm": 21.0,
    "default_canvas_height_cm": 29.7,
}


def _ensure_config_dir():
    os.makedirs(_CONFIG_DIR, exist_ok=True)


def load_settings():
    _ensure_config_dir()
    if not os.path.isfile(_SETTINGS_PATH):
        return dict(DEFAULT_SETTINGS)
    try:
        with open(_SETTINGS_PATH, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return dict(DEFAULT_SETTINGS)
    merged = dict(DEFAULT_SETTINGS)
    merged.update(data)
    return merged


def save_settings(settings):
    _ensure_config_dir()
    merged = dict(DEFAULT_SETTINGS)
    merged.update(settings)
    try:
        with open(_SETTINGS_PATH, "w") as f:
            json.dump(merged, f, indent=2)
    except OSError:
        pass
