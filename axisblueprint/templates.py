"""Template file storage paths and naming rules."""

import os
import re

_TEMPLATE_NAME_RE = re.compile(r"^[a-zA-Z0-9_-]+$")


def get_templates_dir():
    """Return the templates directory, creating it if needed."""
    override = os.environ.get("AXISBLUEPRINT_TEMPLATES_DIR")
    if override:
        path = os.path.expanduser(override)
    else:
        path = os.path.join(
            os.path.expanduser("~"), ".config", "axisblueprint", "templates"
        )
    os.makedirs(path, exist_ok=True)
    return path


def sanitize_template_name(name):
    """Validate a template basename; raises ValueError if unsafe or empty."""
    name = name.strip()
    if not name or not _TEMPLATE_NAME_RE.match(name):
        raise ValueError(
            "Name must be non-empty and contain only letters, numbers, "
            "underscores, or hyphens."
        )
    return name
