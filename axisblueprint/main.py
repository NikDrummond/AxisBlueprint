"""
Public API and backward-compatible entry point.

Prefer importing from AxisBlueprint submodules for new code:
  - models.AxisBox
  - layout.parse_layout_data, build_layout_document, snap_to_grid
  - export.figure_from_layout, boxes_to_axes_params, generate_matplotlib_code
  - designer.LayoutDesigner
  - app.BlueprintBuilder
"""

from .app import BlueprintBuilder, main
from .constants import (
    A4_HEIGHT_CM,
    A4_WIDTH_CM,
    CANVAS_HEIGHT,
    CANVAS_WIDTH,
    CM_PER_INCH,
    JOURNAL_WIDTH_PRESETS,
    SCALE,
    default_panel_label,
)
from .designer import LayoutDesigner
from .dialogs import CodeDialog, PreviewDialog, SaveTemplateDialog
from .export import (
    boxes_to_axes_params,
    figure_from_layout,
    generate_matplotlib_code,
)
from .alignment import (
    align_boxes_left,
    align_boxes_right,
    align_boxes_top,
    align_boxes_bottom,
    align_boxes_center_horizontal,
    align_boxes_center_vertical,
    distribute_boxes_horizontally,
    distribute_boxes_vertically,
)
from .layout import (
    LAYOUT_VERSION,
    LayoutDocument,
    build_layout_document,
    parse_layout_data,
    snap_to_grid,
)
from .models import AxisBox
from .templates import get_templates_dir, sanitize_template_name

# Historical name used in README and early releases.
FigureFromLayout = figure_from_layout

__all__ = [
    "A4_HEIGHT_CM",
    "A4_WIDTH_CM",
    "AxisBox",
    "BlueprintBuilder",
    "CANVAS_HEIGHT",
    "CANVAS_WIDTH",
    "CM_PER_INCH",
    "CodeDialog",
    "FigureFromLayout",
    "LayoutDesigner",
    "PreviewDialog",
    "SaveTemplateDialog",
    "SCALE",
    "boxes_to_axes_params",
    "LAYOUT_VERSION",
    "LayoutDocument",
    "build_layout_document",
    "figure_from_layout",
    "generate_matplotlib_code",
    "get_templates_dir",
    "main",
    "parse_layout_data",
    "sanitize_template_name",
    "snap_to_grid",
]

if __name__ == "__main__":
    main()
