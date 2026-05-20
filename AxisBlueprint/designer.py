"""Tkinter GUI for interactive figure layout design."""

import json
import os
import subprocess
import sys

import tkinter as tk
from tkinter import filedialog, messagebox

from .alignment import (
    align_boxes_bottom,
    align_boxes_center_horizontal,
    align_boxes_center_vertical,
    align_boxes_left,
    align_boxes_right,
    align_boxes_top,
    distribute_boxes_horizontally,
    distribute_boxes_vertically,
)
from .constants import (
    A4_HEIGHT_CM,
    A4_WIDTH_CM,
    CANVAS_HEIGHT,
    CANVAS_WIDTH,
    JOURNAL_WIDTH_PRESETS,
    SCALE,
    default_panel_label,
)
from .dialogs import (
    CodeDialog,
    FloatValueDialog,
    MarginsDialog,
    PreviewDialog,
    ResizeCanvasDialog,
    SaveTemplateDialog,
)
from .export import generate_matplotlib_code
from .geometry import overlapping_box_indices, snap_move_to_guides
from .layout import build_layout_document, parse_layout_data, snap_to_grid
from .models import AxisBox
from .recent_layouts import add_recent_path, load_recent_paths
from .templates import get_templates_dir

SNAP_GUIDE_CM = 0.25
UNDO_MAX = 50
RUBBER_PIXEL_THRESHOLD = 5


def _open_folder(path):
    path = os.path.abspath(os.path.expanduser(path))
    if not os.path.isdir(path):
        return
    try:
        if sys.platform == "win32":
            os.startfile(path)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.run(["open", path], check=False)
        else:
            subprocess.run(["xdg-open", path], check=False)
    except OSError:
        messagebox.showerror("Error", f"Could not open folder:\n{path}")


class LayoutDesigner:
    def __init__(self, master):
        self.master = master
        master.title("AxisBlueprint")

        self.grid_spacing_cm = 0.5
        self.margin_left = 1.0
        self.margin_right = 1.0
        self.margin_top = 1.0
        self.margin_bottom = 1.0
        self.dynamic_canvas = False
        self.canvas_width_cm = A4_WIDTH_CM
        self.canvas_height_cm = A4_HEIGHT_CM

        self._selection = []
        self._undo_stack = []
        self._redo_stack = []
        self._suspend_undo = False
        self._drag_undo_pending = False
        self._rubber = None
        self._rubber_rect_id = None
        self._multi_base = None

        self._build_menubar()

        self.canvas = tk.Canvas(
            master, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="white"
        )
        self.canvas.pack(side=tk.LEFT)

        self.mode = tk.StringVar(value="move")
        self.mode_frame = tk.Frame(master)
        self.mode_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
        tk.Label(self.mode_frame, text="Interaction Mode").pack(pady=5)
        tk.Radiobutton(
            self.mode_frame, text="Move", variable=self.mode, value="move"
        ).pack(anchor="w")
        tk.Radiobutton(
            self.mode_frame, text="Resize", variable=self.mode, value="resize"
        ).pack(anchor="w")

        tk.Label(self.mode_frame, text="Selected Axis Bounds (cm)").pack(pady=(15, 0))
        self.entry_x = self._add_labeled_entry("X:", self.mode_frame)
        self.entry_y = self._add_labeled_entry("Y:", self.mode_frame)
        self.entry_w = self._add_labeled_entry("Width:", self.mode_frame)
        self.entry_h = self._add_labeled_entry("Height:", self.mode_frame)

        tk.Label(self.mode_frame, text="Panel label").pack(pady=(15, 0))
        self.entry_panel_label = tk.Entry(self.mode_frame, width=10)
        self.entry_panel_label.pack(anchor="w")
        self.entry_panel_label.bind("<Return>", lambda e: self._update_panel_label())

        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.canvas.bind("<Button-3>", self.on_right_click)

        self.master.bind("<Delete>", self._on_delete_key)
        self.master.bind("<Control-s>", self._on_ctrl_s)
        self.master.bind("<Control-S>", self._on_ctrl_s)
        self.master.bind("<Control-z>", self._on_undo)
        self.master.bind("<Control-Z>", self._on_undo)
        self.master.bind("<Control-y>", self._on_redo)
        self.master.bind("<Control-Y>", self._on_redo)
        self.master.bind("<Control-Shift-Z>", self._on_redo)
        self.master.bind("<Control-Shift-z>", self._on_redo)
        for keysym, dx, dy in (
            ("<Left>", -1, 0),
            ("<Right>", 1, 0),
            ("<Up>", 0, -1),
            ("<Down>", 0, 1),
        ):
            self.master.bind(
                keysym,
                lambda e, ddx=dx, ddy=dy: self._nudge_selection(ddx, ddy),
            )

        self.boxes = []
        self.drag_offset_x = 0
        self.drag_offset_y = 0

        self.init_default_layout()
        self.save_default_template()
        self.redraw()

    @property
    def selected_box(self):
        return self._selection[-1] if self._selection else None

    @selected_box.setter
    def selected_box(self, value):
        self._selection = [] if value is None else [value]

    def _build_menubar(self):
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)

        self._file_menu = tk.Menu(menubar, tearoff=0, postcommand=self._refresh_recent_menu)
        self._file_menu.add_command(label="Load", command=self.load_layout)
        self._file_menu.add_command(label="Save", command=self.save_layout)
        self._recent_menu = tk.Menu(self._file_menu, tearoff=0)
        self._file_menu.add_cascade(label="Open Recent", menu=self._recent_menu)
        self._file_menu.add_command(
            label="Open Templates Folder", command=lambda: _open_folder(get_templates_dir())
        )
        self._file_menu.add_separator()
        self._file_menu.add_command(label="Preview JSON", command=self.preview_json)
        self._file_menu.add_command(label="Preview Code", command=self.preview_code)
        menubar.add_cascade(label="File", menu=self._file_menu)

        canvas_menu = tk.Menu(menubar, tearoff=0)
        canvas_menu.add_command(label="Resize Canvas", command=self.resize_canvas_dialog)
        canvas_menu.add_command(label="Set Margins", command=self.set_margins_dialog)
        canvas_menu.add_command(
            label="Set Grid Spacing", command=self.set_grid_spacing_dialog
        )
        journal_menu = tk.Menu(canvas_menu, tearoff=0)
        for name, width_cm in JOURNAL_WIDTH_PRESETS:
            journal_menu.add_command(
                label=name,
                command=lambda w=width_cm: self.apply_journal_width(w),
            )
        canvas_menu.add_cascade(label="Journal Width", menu=journal_menu)
        menubar.add_cascade(label="Edit Canvas", menu=canvas_menu)

        axis_menu = tk.Menu(menubar, tearoff=0)
        axis_menu.add_command(label="Add", command=self.add_axis)
        axis_menu.add_command(label="Remove", command=self.remove_axis)
        axis_menu.add_command(label="Duplicate", command=self.duplicate_axis)
        menubar.add_cascade(label="Edit Axis", menu=axis_menu)
        self._axis_menu = axis_menu

        layout_menu = tk.Menu(menubar, tearoff=0)
        layout_menu.add_command(label="Snap to Grid", command=self.optimize_layout)
        layout_menu.add_command(label="Fit to Canvas", command=self.fit_canvas_to_axes)
        layout_menu.add_command(label="Rotate 90° CW", command=self.rotate_layout_90_cw)
        align_menu = tk.Menu(layout_menu, tearoff=0)
        align_menu.add_command(label="Align Left", command=self.align_left)
        align_menu.add_command(label="Align Right", command=self.align_right)
        align_menu.add_command(label="Align Top", command=self.align_top)
        align_menu.add_command(label="Align Bottom", command=self.align_bottom)
        align_menu.add_command(
            label="Align Center Horizontally", command=self.align_center_h
        )
        align_menu.add_command(
            label="Align Center Vertically", command=self.align_center_v
        )
        layout_menu.add_cascade(label="Align", menu=align_menu)
        distribute_menu = tk.Menu(layout_menu, tearoff=0)
        distribute_menu.add_command(
            label="Distribute Horizontally", command=self.distribute_horizontal
        )
        distribute_menu.add_command(
            label="Distribute Vertically", command=self.distribute_vertical
        )
        layout_menu.add_cascade(label="Distribute", menu=distribute_menu)
        layout_menu.add_command(
            label="Auto-Assign Panel Labels", command=self.auto_assign_panel_labels
        )
        menubar.add_cascade(label="Layout", menu=layout_menu)

        self._edit_menu = tk.Menu(menubar, tearoff=0)
        self._edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        self._edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        menubar.add_cascade(label="Edit", menu=self._edit_menu)

    def _refresh_recent_menu(self):
        self._recent_menu.delete(0, tk.END)
        paths = [p for p in load_recent_paths() if os.path.isfile(p)]
        if not paths:
            self._recent_menu.add_command(label="(No recent files)", state=tk.DISABLED)
            return
        for p in paths:
            label = p if len(p) < 48 else "…" + p[-44:]
            self._recent_menu.add_command(
                label=label,
                command=lambda path=p: self._load_recent_file(path),
            )

    def _load_recent_file(self, path):
        try:
            with open(path, "r") as f:
                data = json.load(f)
            doc = parse_layout_data(data)
            self.apply_document(doc)
            add_recent_path(path)
            self.redraw()
        except (ValueError, json.JSONDecodeError, OSError) as e:
            messagebox.showerror("Error", f"Failed to load layout:\n{e}")

    def _on_delete_key(self, event=None):
        self.remove_axis()
        return "break"

    def _on_ctrl_s(self, event=None):
        self.save_layout()
        return "break"

    def _on_undo(self, event=None):
        self.undo()
        return "break"

    def _on_redo(self, event=None):
        self.redo()
        return "break"

    def _nudge_selection(self, dx, dy):
        if not self._selection:
            return "break"
        step = self.grid_spacing_cm
        if step <= 0:
            step = 0.1
        self.push_undo()
        for b in self._selection:
            b.x = max(0.0, b.x + dx * step)
            b.y = max(0.0, b.y + dy * step)
        self.redraw()
        return "break"

    def _snapshot(self):
        return {
            "boxes": [b.to_dict() for b in self.boxes],
            "canvas_width_cm": self.canvas_width_cm,
            "canvas_height_cm": self.canvas_height_cm,
            "margin_left": self.margin_left,
            "margin_right": self.margin_right,
            "margin_top": self.margin_top,
            "margin_bottom": self.margin_bottom,
            "grid_spacing_cm": self.grid_spacing_cm,
        }

    def _apply_snapshot(self, snap):
        from .layout import validate_box_dict

        self.boxes = [
            validate_box_dict(d, i) for i, d in enumerate(snap["boxes"])
        ]
        self.canvas_width_cm = snap["canvas_width_cm"]
        self.canvas_height_cm = snap["canvas_height_cm"]
        self.margin_left = snap["margin_left"]
        self.margin_right = snap["margin_right"]
        self.margin_top = snap["margin_top"]
        self.margin_bottom = snap["margin_bottom"]
        self.grid_spacing_cm = snap["grid_spacing_cm"]
        self.dynamic_canvas = (
            self.canvas_width_cm != A4_WIDTH_CM
            or self.canvas_height_cm != A4_HEIGHT_CM
        )

    def push_undo(self):
        if self._suspend_undo:
            return
        self._undo_stack.append(self._snapshot())
        if len(self._undo_stack) > UNDO_MAX:
            self._undo_stack.pop(0)
        self._redo_stack.clear()

    def undo(self):
        if not self._undo_stack:
            return
        self._redo_stack.append(self._snapshot())
        snap = self._undo_stack.pop()
        self._suspend_undo = True
        try:
            self._apply_snapshot(snap)
            self._selection = []
        finally:
            self._suspend_undo = False
        self.redraw()

    def redo(self):
        if not self._redo_stack:
            return
        self._undo_stack.append(self._snapshot())
        snap = self._redo_stack.pop()
        self._suspend_undo = True
        try:
            self._apply_snapshot(snap)
            self._selection = []
        finally:
            self._suspend_undo = False
        self.redraw()

    def _update_menu_state(self):
        has_sel = bool(self._selection)
        self._axis_menu.entryconfig("Remove", state=tk.NORMAL if has_sel else tk.DISABLED)
        dup_state = tk.NORMAL if len(self._selection) == 1 else tk.DISABLED
        self._axis_menu.entryconfig("Duplicate", state=dup_state)

    def get_layout_document(self):
        return build_layout_document(
            self.boxes,
            self.canvas_width_cm,
            self.canvas_height_cm,
            margin_left=self.margin_left,
            margin_right=self.margin_right,
            margin_top=self.margin_top,
            margin_bottom=self.margin_bottom,
        )

    def apply_document(self, doc):
        self.boxes = doc.boxes
        self.canvas_width_cm = doc.width_cm
        self.canvas_height_cm = doc.height_cm
        self.margin_left = doc.margin_left
        self.margin_right = doc.margin_right
        self.margin_top = doc.margin_top
        self.margin_bottom = doc.margin_bottom
        self.dynamic_canvas = (
            doc.width_cm != A4_WIDTH_CM or doc.height_cm != A4_HEIGHT_CM
        )
        self._selection = []
        self._undo_stack.clear()
        self._redo_stack.clear()

    def apply_layout(self, boxes, canvas_width_cm, canvas_height_cm):
        """Backward-compatible: uniform default margins."""
        from .layout import LayoutDocument

        self.apply_document(
            LayoutDocument(
                boxes=boxes,
                width_cm=canvas_width_cm,
                height_cm=canvas_height_cm,
            )
        )

    def _add_labeled_entry(self, label, parent):
        frame = tk.Frame(parent)
        frame.pack(anchor="w")
        tk.Label(frame, text=label).pack(side=tk.LEFT)
        entry = tk.Entry(frame, width=10)
        entry.pack(side=tk.LEFT)
        entry.bind("<Return>", lambda e: self._update_selected_box())
        return entry

    def _update_selected_box(self):
        if not self.selected_box:
            return
        try:
            self.selected_box.x = float(self.entry_x.get())
            self.selected_box.y = float(self.entry_y.get())
            self.selected_box.width = float(self.entry_w.get())
            self.selected_box.height = float(self.entry_h.get())
            self.redraw()
        except ValueError:
            pass

    def _update_panel_label(self):
        if not self.selected_box:
            return
        self.selected_box.panel_label = self.entry_panel_label.get().strip()
        self.redraw()

    def save_layout(self):
        json_str = json.dumps(self.get_layout_document(), indent=2)
        SaveTemplateDialog(
            self.master,
            json_str,
            on_saved=lambda path: add_recent_path(path),
        )

    def resize_canvas_dialog(self):
        ResizeCanvasDialog(
            self.master,
            self.canvas_width_cm,
            self.canvas_height_cm,
            on_apply=self._apply_canvas_size,
        )

    def apply_journal_width(self, width_cm):
        self._apply_canvas_size(width_cm, self.canvas_height_cm)

    def _apply_canvas_size(self, width_cm, height_cm):
        self.push_undo()
        old_w = self.canvas_width_cm
        old_h = self.canvas_height_cm
        if old_w > 0 and old_h > 0 and (width_cm != old_w or height_cm != old_h):
            sx = width_cm / old_w
            sy = height_cm / old_h
            for box in self.boxes:
                box.x *= sx
                box.y *= sy
                box.width *= sx
                box.height *= sy
        self.canvas_width_cm = width_cm
        self.canvas_height_cm = height_cm
        self.dynamic_canvas = (
            width_cm != A4_WIDTH_CM or height_cm != A4_HEIGHT_CM
        )
        self.redraw()

    def set_margins_dialog(self):
        MarginsDialog(
            self.master,
            self.margin_left,
            self.margin_right,
            self.margin_top,
            self.margin_bottom,
            on_apply=self._apply_margins,
        )

    def _apply_margins(self, ml, mr, mt, mb):
        self.push_undo()
        self.margin_left = ml
        self.margin_right = mr
        self.margin_top = mt
        self.margin_bottom = mb
        self.redraw()

    def set_grid_spacing_dialog(self):
        FloatValueDialog(
            self.master,
            title="Set Grid Spacing",
            label="Grid spacing (cm):",
            initial_value=self.grid_spacing_cm,
            on_apply=self._apply_grid_spacing,
        )

    def _apply_grid_spacing(self, spacing_cm):
        self.push_undo()
        self.grid_spacing_cm = spacing_cm
        self.redraw()

    def rotate_layout_90_cw(self):
        if not self.boxes:
            return
        self.push_undo()
        W, H = self.canvas_width_cm, self.canvas_height_cm
        for box in self.boxes:
            x, y, w, h = box.x, box.y, box.width, box.height
            box.x = y
            box.y = W - x - w
            box.width = h
            box.height = w
        self.canvas_width_cm = H
        self.canvas_height_cm = W
        ml, mr, mt, mb = (
            self.margin_left,
            self.margin_right,
            self.margin_top,
            self.margin_bottom,
        )
        self.margin_left, self.margin_right, self.margin_top, self.margin_bottom = (
            mt,
            mb,
            mr,
            ml,
        )
        self._selection = []
        self.redraw()

    def fit_canvas_to_axes(self):
        if not self.boxes:
            return
        self.push_undo()
        ml, mr, mt, mb = (
            self.margin_left,
            self.margin_right,
            self.margin_top,
            self.margin_bottom,
        )
        min_x = min(box.x for box in self.boxes)
        min_y = min(box.y for box in self.boxes)
        max_x = max(box.x + box.width for box in self.boxes)
        max_y = max(box.y + box.height for box in self.boxes)

        def round_up(val):
            return (
                (val + self.grid_spacing_cm - 1e-5) // self.grid_spacing_cm + 1
            ) * self.grid_spacing_cm

        def round_down(val):
            return ((val + 1e-5) // self.grid_spacing_cm) * self.grid_spacing_cm

        width = round_up(max_x + mr) - round_down(min_x - ml)
        height = round_up(max_y + mb) - round_down(min_y - mt)

        self.canvas_width_cm = max(width, ml + mr + 1)
        self.canvas_height_cm = max(height, mt + mb + 1)
        self.dynamic_canvas = True

        self.canvas.config(
            width=int(self.canvas_width_cm * SCALE),
            height=int(self.canvas_height_cm * SCALE),
        )
        self.redraw()

    def init_default_layout(self):
        ml, mr, mt, mb = (
            self.margin_left,
            self.margin_right,
            self.margin_top,
            self.margin_bottom,
        )
        spacing = 0.5
        available_width = A4_WIDTH_CM - ml - mr - spacing
        box_width = available_width / 2
        available_height = (A4_HEIGHT_CM / 2) - mt - mb - spacing
        box_height = available_height / 2
        positions = [
            (ml, mt),
            (ml + box_width + spacing, mt),
            (ml, mt + box_height + spacing),
            (ml + box_width + spacing, mt + box_height + spacing),
        ]
        self.boxes = [
            AxisBox(x, y, box_width, box_height, panel_label=default_panel_label(i))
            for i, (x, y) in enumerate(positions)
        ]

    def save_default_template(self):
        templates_dir = get_templates_dir()
        default_path = os.path.join(templates_dir, "default.json")
        if not os.path.isfile(default_path):
            with open(default_path, "w") as f:
                json.dump(self.get_layout_document(), f, indent=2)

    def _alignment_targets(self):
        return list(self._selection) if self._selection else list(self.boxes)

    def redraw(self):
        canvas_width_px = int(self.canvas_width_cm * SCALE)
        canvas_height_px = int(self.canvas_height_cm * SCALE)
        self.canvas.config(width=canvas_width_px, height=canvas_height_px)
        self.canvas.delete("all")

        step = int(SCALE * self.grid_spacing_cm)
        for i in range(0, canvas_width_px, step):
            self.canvas.create_line(i, 0, i, canvas_height_px, fill="#eeeeee")
        for j in range(0, canvas_height_px, step):
            self.canvas.create_line(0, j, canvas_width_px, j, fill="#eeeeee")

        ml = self.margin_left * SCALE
        mr = self.margin_right * SCALE
        mt = self.margin_top * SCALE
        mb = self.margin_bottom * SCALE
        self.canvas.create_line(ml, 0, ml, canvas_height_px, fill="black")
        self.canvas.create_line(
            canvas_width_px - mr, 0, canvas_width_px - mr, canvas_height_px, fill="black"
        )
        self.canvas.create_line(0, mt, canvas_width_px, mt, fill="black")
        self.canvas.create_line(
            0,
            canvas_height_px - mb,
            canvas_width_px,
            canvas_height_px - mb,
            fill="black",
        )

        overlap_idx = overlapping_box_indices(self.boxes)

        for i, box in enumerate(self.boxes):
            x1 = box.x * SCALE
            y1 = box.y * SCALE
            x2 = (box.x + box.width) * SCALE
            y2 = (box.y + box.height) * SCALE
            outside = box.is_outside_margins(
                self.margin_left,
                self.margin_right,
                self.margin_top,
                self.margin_bottom,
                self.canvas_width_cm,
                self.canvas_height_cm,
            )
            sel = box in self._selection
            if outside:
                self.canvas.create_rectangle(
                    x1, y1, x2, y2, outline="black", fill="red", width=2
                )
            else:
                color = "red" if sel else "blue"
                self.canvas.create_rectangle(
                    x1, y1, x2, y2, outline=color, width=2
                )
            if i in overlap_idx:
                self.canvas.create_rectangle(
                    x1 - 2, y1 - 2, x2 + 2, y2 + 2, outline="#cc6600", width=3
                )
            label_x = (x1 + x2) / 2
            label_y = (y1 + y2) / 2
            self.canvas.create_text(
                label_x,
                label_y,
                text=str(i + 1),
                fill="black",
                font=("Helvetica", 12, "bold"),
            )
            if box.panel_label:
                pad = 0.15 * SCALE
                self.canvas.create_text(
                    x1 + pad,
                    y1 + pad,
                    text=box.panel_label,
                    fill="black",
                    anchor="nw",
                    font=("Helvetica", 11, "bold"),
                )

        if self.selected_box and len(self._selection) == 1:
            self.entry_x.delete(0, tk.END)
            self.entry_y.delete(0, tk.END)
            self.entry_w.delete(0, tk.END)
            self.entry_h.delete(0, tk.END)
            self.entry_x.insert(0, str(self.selected_box.x))
            self.entry_y.insert(0, str(self.selected_box.y))
            self.entry_w.insert(0, str(self.selected_box.width))
            self.entry_h.insert(0, str(self.selected_box.height))
            self.entry_panel_label.delete(0, tk.END)
            self.entry_panel_label.insert(0, self.selected_box.panel_label)
        else:
            for entry in [self.entry_x, self.entry_y, self.entry_w, self.entry_h]:
                entry.delete(0, tk.END)
            self.entry_panel_label.delete(0, tk.END)
            if len(self._selection) > 1:
                self.entry_panel_label.insert(0, "(multiple)")

        self._update_menu_state()

    def on_mouse_down(self, event):
        x_cm = event.x / SCALE
        y_cm = event.y / SCALE
        shift = bool(event.state & 0x0001)

        for box in self.boxes:
            if box.contains(x_cm, y_cm):
                if shift:
                    if box in self._selection:
                        self._selection = [b for b in self._selection if b is not box]
                    else:
                        self._selection = self._selection + [box]
                else:
                    self._selection = [box]
                self._multi_base = None
                if self.mode.get() == "move":
                    self.drag_offset_x = x_cm - box.x
                    self.drag_offset_y = y_cm - box.y
                self._drag_undo_pending = True
                self.redraw()
                return

        self._rubber = {
            "x0": event.x,
            "y0": event.y,
            "shift": shift,
        }
        self._multi_base = None
        self._drag_undo_pending = False
        if not shift:
            self._selection = []
        self.redraw()

    def on_mouse_move(self, event):
        if self._rubber is not None:
            if self._rubber_rect_id is not None:
                self.canvas.delete(self._rubber_rect_id)
            x0, y0 = self._rubber["x0"], self._rubber["y0"]
            self._rubber_rect_id = self.canvas.create_rectangle(
                x0, y0, event.x, event.y, dash=(4, 4), outline="gray"
            )
            return

        x_cm = event.x / SCALE
        y_cm = event.y / SCALE
        if self.selected_box and self._drag_undo_pending:
            self.push_undo()
            self._drag_undo_pending = False

        if (
            len(self._selection) == 1
            and self.selected_box
            and self.mode.get() == "move"
        ):
            nx = max(0.0, x_cm - self.drag_offset_x)
            ny = max(0.0, y_cm - self.drag_offset_y)
            others = [b for b in self.boxes if b is not self.selected_box]
            nx, ny = snap_move_to_guides(
                nx,
                ny,
                self.selected_box.width,
                self.selected_box.height,
                others,
                SNAP_GUIDE_CM,
            )
            self.selected_box.x = nx
            self.selected_box.y = ny
            self.redraw()
        elif len(self._selection) == 1 and self.selected_box and self.mode.get() == "resize":
            self.selected_box.width = max(0.5, x_cm - self.selected_box.x)
            self.selected_box.height = max(0.5, y_cm - self.selected_box.y)
            self.redraw()
        elif len(self._selection) > 1 and self.mode.get() == "move":
            if self._multi_base is None:
                self._multi_base = {id(b): (b.x, b.y) for b in self._selection}
                self._multi_anchor = (x_cm, y_cm)
            ax, ay = self._multi_anchor
            dx = x_cm - ax
            dy = y_cm - ay
            for b in self._selection:
                ox, oy = self._multi_base[id(b)]
                b.x = max(0.0, ox + dx)
                b.y = max(0.0, oy + dy)
            self.redraw()

    def on_mouse_up(self, event):
        if self._rubber is not None:
            x0, y0 = self._rubber["x0"], self._rubber["y0"]
            shift = self._rubber["shift"]
            self._rubber = None
            if self._rubber_rect_id is not None:
                self.canvas.delete(self._rubber_rect_id)
                self._rubber_rect_id = None
            dx = abs(event.x - x0)
            dy = abs(event.y - y0)
            if dx < RUBBER_PIXEL_THRESHOLD and dy < RUBBER_PIXEL_THRESHOLD:
                if not shift:
                    self._selection = []
                self._multi_base = None
                self.redraw()
                return
            x1, x2 = sorted((x0 / SCALE, event.x / SCALE))
            y1, y2 = sorted((y0 / SCALE, event.y / SCALE))
            picked = []
            for i, box in enumerate(self.boxes):
                cx = box.x + box.width / 2
                cy = box.y + box.height / 2
                if x1 <= cx <= x2 and y1 <= cy <= y2:
                    picked.append(box)
            self.push_undo()
            if shift:
                for b in picked:
                    if b not in self._selection:
                        self._selection.append(b)
            else:
                self._selection = picked
            self._multi_base = None
            self.redraw()
            return

        self._drag_undo_pending = False
        self._multi_base = None
        self.redraw()

    def on_right_click(self, event):
        self._selection = []
        self.redraw()

    def add_axis(self):
        self.push_undo()
        label = default_panel_label(len(self.boxes))
        self.boxes.append(AxisBox(5, 5, 5, 5, panel_label=label))
        self.redraw()

    def duplicate_axis(self):
        if len(self._selection) != 1:
            return
        self.push_undo()
        src = self._selection[0]
        dup = AxisBox(
            src.x + 1,
            src.y + 1,
            src.width,
            src.height,
            panel_label=src.panel_label,
        )
        self.boxes.append(dup)
        self._selection = [dup]
        self.redraw()

    def auto_assign_panel_labels(self):
        self.push_undo()
        for i, box in enumerate(self.boxes):
            box.panel_label = default_panel_label(i)
        self.redraw()

    def _align_and_redraw(self, align_fn):
        targets = self._alignment_targets()
        if not targets:
            return
        self.push_undo()
        align_fn(targets)
        self.redraw()

    def align_left(self):
        self._align_and_redraw(align_boxes_left)

    def align_right(self):
        self._align_and_redraw(align_boxes_right)

    def align_top(self):
        self._align_and_redraw(align_boxes_top)

    def align_bottom(self):
        self._align_and_redraw(align_boxes_bottom)

    def align_center_h(self):
        self._align_and_redraw(align_boxes_center_horizontal)

    def align_center_v(self):
        self._align_and_redraw(align_boxes_center_vertical)

    def distribute_horizontal(self):
        self._align_and_redraw(distribute_boxes_horizontally)

    def distribute_vertical(self):
        self._align_and_redraw(distribute_boxes_vertically)

    def remove_axis(self):
        if not self._selection:
            return
        self.push_undo()
        for b in list(self._selection):
            if b in self.boxes:
                self.boxes.remove(b)
        self._selection = []
        self.redraw()

    def optimize_layout(self):
        self.push_undo()
        spacing = self.grid_spacing_cm
        for box in self.boxes:
            box.x = snap_to_grid(box.x, spacing)
            box.y = snap_to_grid(box.y, spacing)
            box.width = snap_to_grid(box.width, spacing)
            box.height = snap_to_grid(box.height, spacing)
        self.redraw()

    def preview_json(self):
        json_str = json.dumps(self.get_layout_document(), indent=2)
        PreviewDialog(self.master, json_str)

    def load_layout(self):
        templates_dir = get_templates_dir()
        filename = filedialog.askopenfilename(
            initialdir=templates_dir,
            title="Select layout JSON file",
            filetypes=(("JSON Files", "*.json"),),
        )
        if filename:
            try:
                with open(filename, "r") as f:
                    data = json.load(f)
                doc = parse_layout_data(data)
                self.apply_document(doc)
                add_recent_path(filename)
                self.redraw()
            except (ValueError, json.JSONDecodeError, OSError) as e:
                messagebox.showerror("Error", f"Failed to load layout:\n{e}")

    def preview_code(self):
        code_str = generate_matplotlib_code(
            self.boxes, self.canvas_width_cm, self.canvas_height_cm
        )
        CodeDialog(self.master, code_str)

    def generate_code(self):
        """Backward-compatible alias for preview_code."""
        self.preview_code()
