# AxisBlueprint

[![PyPI - Version](https://img.shields.io/pypi/v/axisblueprint)](https://pypi.org/project/axisblueprint/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/axisblueprint)](https://pypi.org/project/axisblueprint/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub](https://img.shields.io/badge/github-NikDrummond/AxisBlueprint-blue?logo=github)](https://github.com/NikDrummond/AxisBlueprint)

**AxisBlueprint** is a lightweight Python toolbox for interactively designing multi-panel scientific figure layouts. Built with Tkinter, it provides a drag-and-drop GUI for arranging axis boxes on a grid, then exports Matplotlib code or renders the layout directly.

## Installation

```bash
pip install axisblueprint
```

For `FigureFromLayout` and generated Matplotlib previews, install the optional plotting dependency:

```bash
pip install "axisblueprint[plot]"
```

### Requirements

- **Python 3.8+**
- **Tkinter** (usually included with Python; on Ubuntu/Debian: `sudo apt install python3-tk`)
- **Matplotlib** (optional, for `[plot]` extra)

## Quick Start

In a Jupyter Notebook (with Tkinter event loop enabled):

```python
%gui tk
from axisblueprint import BlueprintBuilder
BlueprintBuilder()
```

Or from the command line:

```bash
axisblueprint
```

## Features

- **Interactive Layout Design** — Create, duplicate, and remove axis boxes on an A4 canvas with a half-centimeter grid overlay.
- **Move & Resize Modes** — Drag boxes to reposition them, or resize from the top-left corner.
- **Snap-to-Grid** — Optimize your layout by snapping boxes to the nearest half-centimeter.
- **Save, Save As & Load** — Save overwrites the current file; Save As writes to a new location; Load opens any `.json` layout.
- **Default Templates** — Save your current layout as the startup default (including canvas size and margins), loaded automatically on next launch.
- **Settings Window** — Configure default canvas size, margins, grid spacing, and templates directory via File → Settings.
- **Matplotlib Code Generation** — Automatically generate Python code that recreates your layout.
- **FigureFromLayout** — Load saved layouts as Matplotlib figures programmatically.
- **Undo/Redo** — Full undo/redo support via the Edit menu or Ctrl+Z / Ctrl+Y.
- **Keyboard Shortcuts** — Delete, Ctrl+S, arrow keys for nudging.
- **Multi-Select** — Shift+click or rubber-band select; align/distribute operations use the selection.
- **Layout Aids** — Snap-to-guides while moving, overlap detection (orange outline), 90° rotation.
- **Per-Side Margins** — Configure left, right, top, and bottom margins independently.
- **Open Recent** — Track recently opened layouts.
- **Auto Panel Labels** — Automatically assign sequential labels (a., b., c., ...) to panels.

## Usage

### GUI

1. **Select a box:** Left-click on an axis box to select it (highlighted in red).
2. **Choose Interaction Mode:** Use the radio buttons on the right panel for **Move** or **Resize**.
3. **Add boxes:** Click the **New Panel** button.
4. **Deselect:** Right-click anywhere on the canvas.
5. **Optimize:** Click **Optimize** to snap all boxes to the nearest half-centimeter.
6. **Save/Load:** Use **File → Save** (Ctrl+S) to overwrite the current file, **File → Save As...** to choose a new location, or **File → Load** to open a saved layout.
7. **Default Template:** Use **File → Save as Default Template** to set the current layout (including canvas size and margins) as the startup default.
8. **Settings:** Use **File → Settings** to configure default canvas size, margins, grid spacing, and templates directory.
9. **Generate Code:** Click **Generate Code** to create a Matplotlib code snippet.

### Programmatic: FigureFromLayout

Once you have a layout saved, generate it directly in Python:

```python
from axisblueprint import FigureFromLayout
fig, axes = FigureFromLayout("default")
```

Load from a custom directory:

```python
fig, axes = FigureFromLayout("my_layout", "/path/to/my/layouts")
```

Returns a `matplotlib.Figure` and a list of `matplotlib.axes.Axes` objects.

## Layout File Format

Layouts are saved as JSON files. The format includes versioning for forward compatibility:

```json
{
  "version": 1,
  "canvas": {
    "width_cm": 21.0,
    "height_cm": 29.7,
    "margins": { "left": 1.0, "right": 1.0, "top": 1.0, "bottom": 1.0 }
  },
  "boxes": [
    { "x": 1.0, "y": 1.0, "width": 9.25, "height": 6.675, "panel_label": "A" }
  ]
}
```

## API Reference

### `AxisBox(x, y, width, height, panel_label="")`
A single panel in the layout. Coordinates and dimensions are in centimeters.

### `BlueprintBuilder()`
Launch the Tkinter GUI.

### `LayoutDesigner(parent)`
Embed the layout designer in an existing Tkinter application.

### `figure_from_layout(layout_name, layouts_dir=None)`
Load a saved layout and return a Matplotlib figure with axes.

### `generate_matplotlib_code(boxes, page_width_cm, page_height_cm)`
Generate a Python script string for the given layout.

## Configuration

- **Settings:** `~/.config/axisblueprint/settings.json` — default canvas size, margins, grid spacing, and templates directory (editable via **File → Settings** in the GUI).
- **Templates directory:** `~/.config/axisblueprint/templates/` — contains saved layouts and `default.json` (loaded on startup).
- **Override:** Set the `AXISBLUEPRINT_TEMPLATES_DIR` environment variable to use a custom templates directory.
- **Recent layouts:** `~/.config/axisblueprint/recent_layouts.json`

## Contributing

Contributions are welcome! Please open [issues](https://github.com/NikDrummond/AxisBlueprint/issues) or submit pull requests on [GitHub](https://github.com/NikDrummond/AxisBlueprint).

### Development

Clone and install in editable mode:

```bash
git clone https://github.com/NikDrummond/AxisBlueprint.git
cd AxisBlueprint
pip install -e ".[plot]"
```

Run tests:

```bash
python -m pytest tests/
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
