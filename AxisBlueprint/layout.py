"""Layout document parsing, validation, and grid snapping."""

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Union

from .constants import A4_HEIGHT_CM, A4_WIDTH_CM
from .models import AxisBox

LAYOUT_VERSION = 1


@dataclass
class LayoutDocument:
    """Parsed layout file contents."""

    boxes: List[AxisBox]
    width_cm: float
    height_cm: float
    margin_left: float = 1.0
    margin_right: float = 1.0
    margin_top: float = 1.0
    margin_bottom: float = 1.0
    version: int = LAYOUT_VERSION


def snap_to_grid(value, spacing):
    if spacing <= 0:
        return value
    return round(value / spacing) * spacing


def validate_box_dict(data, index):
    if not isinstance(data, dict):
        raise ValueError(
            f"Box {index + 1}: expected an object, got {type(data).__name__}"
        )
    box = {}
    for key in ("x", "y", "width", "height"):
        if key not in data:
            raise ValueError(f"Box {index + 1}: missing required field '{key}'")
        try:
            val = float(data[key])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Box {index + 1}: '{key}' must be a number") from exc
        if key in ("width", "height") and val <= 0:
            raise ValueError(f"Box {index + 1}: '{key}' must be positive")
        if key in ("x", "y") and val < 0:
            raise ValueError(f"Box {index + 1}: '{key}' must be non-negative")
        box[key] = val
    panel_label = ""
    if "panel_label" in data:
        raw = data["panel_label"]
        if raw is not None and not isinstance(raw, str):
            raise ValueError(f"Box {index + 1}: 'panel_label' must be a string")
        panel_label = (raw or "").strip()
    return AxisBox(
        box["x"], box["y"], box["width"], box["height"], panel_label=panel_label
    )


def _parse_margins(canvas: Dict[str, Any]) -> Tuple[float, float, float, float]:
    """Return (left, right, top, bottom) in cm."""
    m = canvas.get("margins")
    if isinstance(m, dict):
        try:
            return (
                float(m.get("left", 1.0)),
                float(m.get("right", 1.0)),
                float(m.get("top", 1.0)),
                float(m.get("bottom", 1.0)),
            )
        except (TypeError, ValueError) as exc:
            raise ValueError("Canvas margins must be numeric") from exc
    if "margin_cm" in canvas:
        try:
            u = float(canvas["margin_cm"])
            return (u, u, u, u)
        except (TypeError, ValueError) as exc:
            raise ValueError("Canvas margin_cm must be a number") from exc
    return (1.0, 1.0, 1.0, 1.0)


def build_layout_document(
    boxes,
    canvas_width_cm,
    canvas_height_cm,
    *,
    margin_left: float,
    margin_right: float,
    margin_top: float,
    margin_bottom: float,
    version: int = LAYOUT_VERSION,
):
    return {
        "version": version,
        "canvas": {
            "width_cm": canvas_width_cm,
            "height_cm": canvas_height_cm,
            "margins": {
                "left": margin_left,
                "right": margin_right,
                "top": margin_top,
                "bottom": margin_bottom,
            },
        },
        "boxes": [box.to_dict() for box in boxes],
    }


def parse_layout_data(data: Union[list, dict]) -> LayoutDocument:
    """
    Parse layout JSON (document format or legacy list of boxes).
    """
    if isinstance(data, list):
        boxes = [validate_box_dict(item, i) for i, item in enumerate(data)]
        return LayoutDocument(
            boxes=boxes,
            width_cm=A4_WIDTH_CM,
            height_cm=A4_HEIGHT_CM,
        )

    if isinstance(data, dict):
        version = int(data.get("version", 1))
        canvas = data.get("canvas") or {}
        try:
            width_cm = float(canvas.get("width_cm", A4_WIDTH_CM))
            height_cm = float(canvas.get("height_cm", A4_HEIGHT_CM))
        except (TypeError, ValueError) as exc:
            raise ValueError("Canvas width_cm and height_cm must be numbers") from exc
        if width_cm <= 0 or height_cm <= 0:
            raise ValueError("Canvas dimensions must be positive")
        ml, mr, mt, mb = _parse_margins(canvas)
        if "boxes" not in data:
            raise ValueError("Layout must contain a 'boxes' array")
        if not isinstance(data["boxes"], list):
            raise ValueError("'boxes' must be an array")
        boxes = [
            validate_box_dict(item, i) for i, item in enumerate(data["boxes"])
        ]
        return LayoutDocument(
            boxes=boxes,
            width_cm=width_cm,
            height_cm=height_cm,
            margin_left=ml,
            margin_right=mr,
            margin_top=mt,
            margin_bottom=mb,
            version=version,
        )

    raise ValueError("Layout file must be a JSON object or array of boxes")
