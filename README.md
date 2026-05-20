# AxisBlueprint

**AxisBlueprint** is a lightweight Python toolbox for interactively designing scientific figure layouts. With its easy-to-use Tkinter GUI, you can create, move, and resize axis boxes on an A4 template (with a half-centimeter grid) and then generate Matplotlib code to recreate your layout.

## Features

- **Interactive Layout Design:**  
  Create, duplicate, and remove axis boxes on a grid overlayed A4 template.
  
- **Move and Resize Modes:**  
  Switch between "Move" and "Resize" modes via the side panel.  
  - **Move Mode:** Drag a selected box to reposition it.  
  - **Resize Mode:** Drag to change the size of a selected box while keeping its top–left corner fixed.
  
- **Snap-to-Grid Optimization:**  
  Optimize your layout by snapping boxes to the nearest half-centimeter.
  
- **Save Layouts:**  
  Use the **Preview JSON** button in order to get a preview of your layout. Once you have the preview, you can save your layout. Hitting **Save to Templates** will let you name your layout and saves it.

- **Load Layouts:**
  Using the **Load Layouts** button allows you to select one of your saved layouts and preview and edit it. 
  
- **Matplotlib Code Generation:**  
  Automatically generate Matplotlib code that recreates your design for further plotting.

- **Workflow:** Undo/redo (**Edit** menu and Ctrl+Z / Ctrl+Y), keyboard shortcuts (Delete, Ctrl+S, arrow keys to nudge by grid step), **Open Recent** and **Open Templates Folder** under **File**.

- **Selection:** Shift+click to multi-select; drag on empty canvas to rubber-band select. Align and distribute use the selection when it is non-empty, otherwise all panels.

- **Layout aids:** Snap-to-guides while moving a single panel, orange outline when panels overlap, **Rotate 90° CW** under **Layout**.

- **Margins:** Per-side margins (cm) stored in the layout JSON; **Set Margins** opens a four-field dialog.

- **Layout file format:** JSON includes `"version": 1` and `canvas.margins` for forward compatibility.

Install AxisBlueprint directly from GitHub using pip:

```bash
pip install git+https://github.com/yourusername/AxisBlueprint.git@main
```

For `FigureFromLayout` and generated Matplotlib previews, install the optional plotting dependency:

```bash
pip install "axisblueprint[plot]"
# or from a clone:
pip install -e ".[plot]"
```

## Usage

In a Jupyter Notebook (with Tkinter event loop enabled), run:

```python
%gui tk
from axisblueprint.main import BlueprintBuilder
BlueprintBuilder()
```

## Using the GUI

1. **Select a box:**  
Left-click on an axis box to select it. the selected box is highlighted in red and displays its numerical label.
2. **Choose Interaction Mode:**  
Use the radio buttons on the right panel to switch between **Move** and **Resize** modes: 
    - **Move:** Drag the box and reposition it
    - **Resize:** Drag to adjust the size of a box (the top left corner remains fixed)
3. **Deselect a Box:**  
Right-click anywhere on the canvas to deselect the current box.
4. **Optimize the layout:**  
click the **Optimize** button in order to snap all boxes to the nearest half centimetre as shown but the grid on the canvas
5. **Save/Load Layout:**  
Use the **Save** and **Load** buttons to import and export saved layouts.
6. **Generate Matplotlib Code:**  
click **Generate Code** to create a code snipped that reproduces your layout using matplotlib. Simply copy and paste this into a Jupyter Notebook cell, or other code, and use whatever code to generate your figures.

## Matplotlib generation from Saved Layouts

Once you have a layout saved, you can generate it directly in python using:

```python
from axisblueprint.main import FigureFromLayout
fig, axes = FigureFromLayout("default")
```

Changing `default` to your saved layout name. This creates a `matplotlib.Figure` object, and a `List` which is the list of your ordered `matplotlib.axes` objects.

Layouts are read from the default templates directory unless you pass a second argument: a path to a folder that contains your `*.json` layout files (for example a project-specific `layouts/` directory):

```python
fig, axes = FigureFromLayout("my_layout", "/path/to/my/layouts")
```

Contributions are welcome! Please open issues or submit pull requests for bug fixes or feature improvements.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
