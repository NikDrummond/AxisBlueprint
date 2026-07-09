"""Matplotlib figure construction and code generation from layouts."""

import json
import os

import matplotlib.pyplot as plt

from .constants import CM_PER_INCH
from .layout import parse_layout_data
from .templates import get_templates_dir


def boxes_to_axes_params(boxes, page_width_cm, page_height_cm):
    """Convert layout boxes to matplotlib add_axes [left, bottom, width, height] tuples."""
    params = []
    for box in boxes:
        left = box.x / page_width_cm
        bottom = (page_height_cm - (box.y + box.height)) / page_height_cm
        width = box.width / page_width_cm
        height = box.height / page_height_cm
        params.append((left, bottom, width, height))
    return params


def generate_matplotlib_code(boxes, page_width_cm, page_height_cm):
    """Return a Python script string that recreates the layout with matplotlib."""
    fig_width = page_width_cm / CM_PER_INCH
    fig_height = page_height_cm / CM_PER_INCH
    code_lines = [
        "import matplotlib.pyplot as plt",
        (
            f"fig = plt.figure(figsize=({fig_width:.2f}, {fig_height:.2f}))  "
            f"# {page_width_cm:.1f} x {page_height_cm:.1f} cm"
        ),
    ]
    for i, (box, (left, bottom, width, height)) in enumerate(
        zip(boxes, boxes_to_axes_params(boxes, page_width_cm, page_height_cm))
    ):
        code_lines.append(
            f"ax{i + 1} = fig.add_axes([{left:.2f}, {bottom:.2f}, {width:.2f}, {height:.2f}])"
        )
        if box.panel_label:
            label = box.panel_label.replace("\\", "\\\\").replace('"', '\\"')
            code_lines.append(
                f'ax{i + 1}.text(0.02, 0.98, "{label}", transform=ax{i + 1}.transAxes, '
                f"fontweight='bold', va='top', ha='left')"
            )
    code_lines.append("plt.show()")
    return "\n".join(code_lines)


def figure_from_layout(layout_name, layouts_dir=None):
    """
    Load a named layout JSON and create a matplotlib figure with arranged axes.

    Args:
        layout_name: Base name of the layout file (without ``.json``).
        layouts_dir: If given, load from ``{layouts_dir}/{layout_name}.json``.
            If omitted, uses the default templates directory (see
            ``AXISBLUEPRINT_TEMPLATES_DIR`` and ``get_templates_dir()``).

    Returns:
        fig: The matplotlib figure.
        axes_list: Axes objects for each layout box, in order.
    """
    if layouts_dir is None:
        templates_dir = get_templates_dir()
    else:
        templates_dir = os.path.abspath(os.path.expanduser(layouts_dir))
        if not os.path.isdir(templates_dir):
            raise FileNotFoundError(
                f"Layouts directory does not exist or is not a directory: {templates_dir!r}"
            )

    filepath = os.path.join(templates_dir, f"{layout_name}.json")
    if not os.path.isfile(filepath):
        raise FileNotFoundError(
            f"Template file {layout_name}.json not found in {templates_dir}."
        )

    with open(filepath, "r") as f:
        data = json.load(f)
    doc = parse_layout_data(data)
    boxes = doc.boxes
    page_width_cm = doc.width_cm
    page_height_cm = doc.height_cm

    fig_width = page_width_cm / CM_PER_INCH
    fig_height = page_height_cm / CM_PER_INCH
    fig = plt.figure(figsize=(fig_width, fig_height))

    axes_list = []
    for box, (left, bottom, width, height) in zip(
        boxes, boxes_to_axes_params(boxes, page_width_cm, page_height_cm)
    ):
        ax = fig.add_axes([left, bottom, width, height])
        if box.panel_label:
            ax.text(
                0.02,
                1.05,
                box.panel_label,
                transform=ax.transAxes,
                fontweight="bold",
                va="top",
                ha="left",
            )
        axes_list.append(ax)

    return fig, axes_list
