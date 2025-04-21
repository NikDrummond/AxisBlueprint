# import tkinter as tk
# from tkinter import messagebox, filedialog
# import json
# import os

# # For the FigureFromLayout function:
# import matplotlib.pyplot as plt

# # Constants: Using 20 pixels per cm for a visible interface.
# SCALE = 20  # pixels per cm
# A4_WIDTH_CM = 21
# A4_HEIGHT_CM = 29.7
# CANVAS_WIDTH = int(A4_WIDTH_CM * SCALE)  # e.g., 21*20 = 420
# CANVAS_HEIGHT = int(A4_HEIGHT_CM * SCALE)  # e.g., 29.7*20 ≈ 594


# class AxisBox:
#     def __init__(self, x, y, width, height):
#         # All dimensions in centimeters.
#         self.x = x
#         self.y = y
#         self.width = width
#         self.height = height

#     def to_dict(self):
#         return {"x": self.x, "y": self.y, "width": self.width, "height": self.height}

#     @staticmethod
#     def from_dict(data):
#         return AxisBox(data["x"], data["y"], data["width"], data["height"])

#     def contains(self, px, py):
#         # Check if a point (in cm) is within this box.
#         return (
#             self.x <= px <= self.x + self.width and self.y <= py <= self.y + self.height
#         )


# class LayoutDesigner:
#     def __init__(self, master):
#         self.master = master
#         master.title("AxisBlueprint")

#         # Toolbar frame at the top.
#         self.toolbar = tk.Frame(master)
#         self.toolbar.pack(side=tk.TOP, fill=tk.X)

#         self.btn_add = tk.Button(self.toolbar, text="Add Axis", command=self.add_axis)
#         self.btn_add.pack(side=tk.LEFT)
#         self.btn_duplicate = tk.Button(
#             self.toolbar, text="Duplicate Axis", command=self.duplicate_axis
#         )
#         self.btn_duplicate.pack(side=tk.LEFT)
#         self.btn_remove = tk.Button(
#             self.toolbar, text="Remove Axis", command=self.remove_axis
#         )
#         self.btn_remove.pack(side=tk.LEFT)
#         self.btn_optimize = tk.Button(
#             self.toolbar, text="Optimize", command=self.optimize_layout
#         )
#         self.btn_optimize.pack(side=tk.LEFT)
#         # Rename the Save button to "Preview JSON"
#         self.btn_preview = tk.Button(
#             self.toolbar, text="Preview JSON", command=self.preview_json
#         )
#         self.btn_preview.pack(side=tk.LEFT)
#         self.btn_load = tk.Button(
#             self.toolbar, text="Load Layout", command=self.load_layout
#         )
#         self.btn_load.pack(side=tk.LEFT)
#         self.btn_generate = tk.Button(
#             self.toolbar, text="Generate Code", command=self.generate_code
#         )
#         self.btn_generate.pack(side=tk.LEFT)

#         # Canvas for drawing the A4 page.
#         self.canvas = tk.Canvas(
#             master, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="white"
#         )
#         self.canvas.pack(side=tk.LEFT)

#         # Side panel for interaction mode.
#         self.mode = tk.StringVar(value="move")  # default mode is "move"
#         self.mode_frame = tk.Frame(master)
#         self.mode_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
#         tk.Label(self.mode_frame, text="Interaction Mode").pack(pady=5)
#         tk.Radiobutton(
#             self.mode_frame, text="Move", variable=self.mode, value="move"
#         ).pack(anchor="w")
#         tk.Radiobutton(
#             self.mode_frame, text="Resize", variable=self.mode, value="resize"
#         ).pack(anchor="w")

#         # Bind mouse events.
#         self.canvas.bind("<Button-1>", self.on_mouse_down)
#         self.canvas.bind("<B1-Motion>", self.on_mouse_move)
#         self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
#         self.canvas.bind("<Button-3>", self.on_right_click)  # right-click to deselect

#         # Initialize boxes and state.
#         self.boxes = []
#         self.selected_box = None
#         self.drag_offset_x = 0
#         self.drag_offset_y = 0
#         self.resizing = False

#         self.init_default_layout()
#         self.save_default_template()  # Save the default template if not already saved.
#         self.redraw()

#     def init_default_layout(self):
#         # Create a default 2×2 grid of boxes in the top half.
#         margin = 1  # cm
#         spacing = 0.5  # cm
#         available_width = A4_WIDTH_CM - 2 * margin - spacing
#         box_width = available_width / 2
#         available_height = (A4_HEIGHT_CM / 2) - margin - spacing
#         box_height = available_height / 2
#         self.boxes = [
#             AxisBox(margin, margin, box_width, box_height),
#             AxisBox(margin + box_width + spacing, margin, box_width, box_height),
#             AxisBox(margin, margin + box_height + spacing, box_width, box_height),
#             AxisBox(
#                 margin + box_width + spacing,
#                 margin + box_height + spacing,
#                 box_width,
#                 box_height,
#             ),
#         ]

#     def save_default_template(self):
#         # Ensure the templates folder exists.
#         templates_dir = os.path.join(os.getcwd(), "templates")
#         if not os.path.exists(templates_dir):
#             os.makedirs(templates_dir)
#         # Save the default layout as default.json if it doesn't already exist.
#         default_path = os.path.join(templates_dir, "default.json")
#         if not os.path.isfile(default_path):
#             layout_data = [box.to_dict() for box in self.boxes]
#             with open(default_path, "w") as f:
#                 json.dump(layout_data, f, indent=2)

#     def redraw(self):
#         self.canvas.delete("all")
#         # Draw grid lines every 0.5 cm.
#         step = SCALE // 2
#         for i in range(0, CANVAS_WIDTH, step):
#             self.canvas.create_line(i, 0, i, CANVAS_HEIGHT, fill="#eeeeee")
#         for j in range(0, CANVAS_HEIGHT, step):
#             self.canvas.create_line(0, j, CANVAS_WIDTH, j, fill="#eeeeee")
#         # Draw each axis box with a numerical label.
#         for i, box in enumerate(self.boxes):
#             x1 = box.x * SCALE
#             y1 = box.y * SCALE
#             x2 = (box.x + box.width) * SCALE
#             y2 = (box.y + box.height) * SCALE
#             color = "red" if box == self.selected_box else "blue"
#             self.canvas.create_rectangle(x1, y1, x2, y2, outline=color, width=2)
#             label_x = (x1 + x2) / 2
#             label_y = (y1 + y2) / 2
#             self.canvas.create_text(
#                 label_x,
#                 label_y,
#                 text=str(i + 1),
#                 fill="black",
#                 font=("Helvetica", 12, "bold"),
#             )



                
    def on_mouse_down(self, event):
        x_cm = event.x / SCALE
        y_cm = event.y / SCALE
        # Check if a box is clicked.
        for box in self.boxes:
            if box.contains(x_cm, y_cm):
                self.selected_box = box
                if self.mode.get() == "move":
                    self.drag_offset_x = x_cm - box.x
                    self.drag_offset_y = y_cm - box.y
                self.redraw()
                return
        self.selected_box = None
        self.redraw()

    def on_mouse_move(self, event):
        x_cm = event.x / SCALE
        y_cm = event.y / SCALE
        if self.selected_box:
            if self.mode.get() == "move":
                self.selected_box.x = max(0, x_cm - self.drag_offset_x)
                self.selected_box.y = max(0, y_cm - self.drag_offset_y)
            elif self.mode.get() == "resize":
                new_width = max(0.5, x_cm - self.selected_box.x)
                new_height = max(0.5, y_cm - self.selected_box.y)
                self.selected_box.width = new_width
                self.selected_box.height = new_height
            self.redraw()

    def on_mouse_up(self, event):
        self.redraw()

    def on_right_click(self, event):
        # Right-click deselects the current box.
        self.selected_box = None
        self.redraw()

    def add_axis(self):
        new_box = AxisBox(5, 5, 5, 5)
        self.boxes.append(new_box)
        self.redraw()

    def duplicate_axis(self):
        if self.selected_box:
            dup = AxisBox(
                self.selected_box.x + 1,
                self.selected_box.y + 1,
                self.selected_box.width,
                self.selected_box.height,
            )
            self.boxes.append(dup)
            self.redraw()

    def remove_axis(self):
        if self.selected_box:
            self.boxes.remove(self.selected_box)
            self.selected_box = None
            self.redraw()

    def optimize_layout(self):
        # Snap box values to the nearest 0.5 cm.
        for box in self.boxes:
            box.x = round(box.x * 2) / 2
            box.y = round(box.y * 2) / 2
            box.width = round(box.width * 2) / 2
            box.height = round(box.height * 2) / 2
        self.redraw()

    def preview_json(self):
        # Open a dialog to preview the JSON layout and offer a save option.
        layout_data = [box.to_dict() for box in self.boxes]
        json_str = json.dumps(layout_data, indent=2)
        PreviewDialog(self.master, json_str)

    def load_layout(self):
        # Open a file dialog to select a JSON file from the templates folder.
        templates_dir = os.path.join(os.getcwd(), "templates")
        filename = filedialog.askopenfilename(
            initialdir=templates_dir,
            title="Select layout JSON file",
            filetypes=(("JSON Files", "*.json"),),
        )
        if filename:
            try:
                with open(filename, "r") as f:
                    data = json.load(f)
                self.boxes = [AxisBox.from_dict(item) for item in data]
                self.redraw()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load layout:\n{e}")

    def generate_code(self):
        code_lines = []
        code_lines.append("import matplotlib.pyplot as plt")
        # Convert A4 dimensions from cm to inches (1 inch = 2.54 cm).
        fig_width = A4_WIDTH_CM / 2.54
        fig_height = A4_HEIGHT_CM / 2.54
        code_lines.append(
            f"fig = plt.figure(figsize=({fig_width:.2f}, {fig_height:.2f}))  # A4 size in inches"
        )
        for i, box in enumerate(self.boxes):
            left = box.x / A4_WIDTH_CM
            bottom = (A4_HEIGHT_CM - (box.y + box.height)) / A4_HEIGHT_CM
            width = box.width / A4_WIDTH_CM
            height = box.height / A4_HEIGHT_CM
            code_lines.append(
                f"ax{i+1} = fig.add_axes([{left:.2f}, {bottom:.2f}, {width:.2f}, {height:.2f}])"
            )
        code_lines.append("plt.show()")
        code_str = "\n".join(code_lines)
        CodeDialog(self.master, code_str)


# Dialog to preview JSON and offer to save it.
class PreviewDialog(tk.Toplevel):
    def __init__(self, master, json_str):
        super().__init__(master)
        self.title("Preview Layout JSON")
        self.geometry("600x400")
        self.json_str = json_str
        text = tk.Text(self, width=80, height=20)
        text.insert("1.0", json_str)
        text.config(state=tk.DISABLED)
        text.pack(padx=10, pady=10)
        # Button to open the save template dialog.
        btn = tk.Button(self, text="Save to Templates", command=self.open_save_dialog)
        btn.pack(pady=5)
        # Button to close the preview.
        tk.Button(self, text="Close", command=self.destroy).pack(pady=5)

    def open_save_dialog(self):
        self.destroy()
        SaveTemplateDialog(self.master, self.json_str)


# Dialog to let the user name their layout and then save it.
class SaveTemplateDialog(tk.Toplevel):
    def __init__(self, master, json_str):
        super().__init__(master)
        self.title("Save Layout Template")
        self.geometry("400x150")
        self.json_str = json_str
        tk.Label(self, text="Enter a name for your layout (without .json):").pack(
            pady=5
        )
        self.entry = tk.Entry(self, width=30)
        self.entry.pack(pady=5)
        btn = tk.Button(self, text="Save", command=self.save_template)
        btn.pack(pady=5)

    def save_template(self):
        name = self.entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a valid name.")
            return
        templates_dir = os.path.join(os.getcwd(), "templates")
        if not os.path.exists(templates_dir):
            os.makedirs(templates_dir)
        path = os.path.join(templates_dir, f"{name}.json")
        try:
            with open(path, "w") as f:
                f.write(self.json_str)
            messagebox.showinfo("Success", f"Layout saved as {name}.json")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save layout:\n{e}")


# Dialog to display generated Matplotlib code.
class CodeDialog(tk.Toplevel):
    def __init__(self, master, code_str):
        super().__init__(master)
        self.title("Generated Matplotlib Code")
        self.geometry("700x400")
        text = tk.Text(self, width=80, height=20)
        text.insert("1.0", code_str)
        text.config(state=tk.NORMAL)
        text.pack(padx=10, pady=10)
        tk.Button(self, text="Close", command=self.destroy).pack(pady=5)


def BlueprintBuilder():
    # Entry point for launching the Tkinter toolbox.
    root = tk.Tk()
    app = LayoutDesigner(root)
    root.mainloop()


def FigureFromLayout(layout_name):
    """
    Given the name of a JSON file in the templates folder (without the .json extension),
    load the layout and create a matplotlib figure with axes arranged as specified.

    Returns:
        fig: The matplotlib figure.
        axes_list: A list of axes objects corresponding to each layout box.
    """
    templates_dir = os.path.join(os.getcwd(), "templates")
    filepath = os.path.join(templates_dir, f"{layout_name}.json")
    if not os.path.isfile(filepath):
        raise FileNotFoundError(
            f"Template file {layout_name}.json not found in templates folder."
        )

    with open(filepath, "r") as f:
        data = json.load(f)
    boxes = [AxisBox.from_dict(item) for item in data]

    # Create a matplotlib figure with A4 dimensions in inches.
    fig_width = A4_WIDTH_CM / 2.54
    fig_height = A4_HEIGHT_CM / 2.54
    fig = plt.figure(figsize=(fig_width, fig_height))

    axes_list = []
    for box in boxes:
        left = box.x / A4_WIDTH_CM
        bottom = (A4_HEIGHT_CM - (box.y + box.height)) / A4_HEIGHT_CM
        width = box.width / A4_WIDTH_CM
        height = box.height / A4_HEIGHT_CM
        ax = fig.add_axes([left, bottom, width, height])
        axes_list.append(ax)

    return fig, axes_list


def main():
    BlueprintBuilder()


if __name__ == "__main__":
    main()
