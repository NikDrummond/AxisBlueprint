"""Tkinter dialogs for previewing, saving, and exporting layouts."""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .constants import CANVAS_PRESETS
from .templates import get_templates_dir, sanitize_template_name


class FloatValueDialog(tk.Toplevel):
    """Prompt for a single positive float (e.g. margin or grid spacing)."""

    def __init__(self, master, title, label, initial_value, on_apply, min_value=0.0):
        super().__init__(master)
        self.title(title)
        self.on_apply = on_apply
        self.min_value = min_value
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        tk.Label(self, text=label).pack(padx=10, pady=(10, 5))
        self.entry = tk.Entry(self, width=12)
        self.entry.insert(0, str(initial_value))
        self.entry.pack(padx=10, pady=5)
        self.entry.bind("<Return>", lambda e: self._apply())
        self.entry.focus_set()

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Apply", command=self._apply).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side=tk.LEFT, padx=5)

    def _apply(self):
        try:
            value = float(self.entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number.", parent=self)
            return
        if value <= self.min_value:
            messagebox.showerror(
                "Error",
                f"Value must be greater than {self.min_value}.",
                parent=self,
            )
            return
        self.on_apply(value)
        self.destroy()


class MarginsDialog(tk.Toplevel):
    """Set left, right, top, and bottom margins (cm)."""

    def __init__(self, master, margin_left, margin_right, margin_top, margin_bottom, on_apply):
        super().__init__(master)
        self.title("Set Margins")
        self.on_apply = on_apply
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self.entries = {}
        for row, (key, label, val) in enumerate(
            [
                ("left", "Left (cm):", margin_left),
                ("right", "Right (cm):", margin_right),
                ("top", "Top (cm):", margin_top),
                ("bottom", "Bottom (cm):", margin_bottom),
            ]
        ):
            f = tk.Frame(self)
            f.pack(padx=10, pady=4, anchor="w")
            tk.Label(f, text=label, width=12, anchor="w").pack(side=tk.LEFT)
            e = tk.Entry(f, width=10)
            e.insert(0, str(val))
            e.pack(side=tk.LEFT)
            self.entries[key] = e

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=12)
        tk.Button(btn_frame, text="Apply", command=self._apply).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side=tk.LEFT, padx=5)

    def _apply(self):
        out = {}
        for key, entry in self.entries.items():
            try:
                v = float(entry.get())
            except ValueError:
                messagebox.showerror("Error", f"Invalid number for {key}.", parent=self)
                return
            if v < 0:
                messagebox.showerror("Error", "Margins must be non-negative.", parent=self)
                return
            out[key] = v
        self.on_apply(out["left"], out["right"], out["top"], out["bottom"])
        self.destroy()


class ResizeCanvasDialog(tk.Toplevel):
    """Set canvas page size in cm, with journal/paper presets."""

    def __init__(self, master, width_cm, height_cm, on_apply):
        super().__init__(master)
        self.title("Resize Canvas")
        self.on_apply = on_apply
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        preset_frame = tk.Frame(self)
        preset_frame.pack(padx=10, pady=(10, 5), anchor="w")
        tk.Label(preset_frame, text="Preset:").pack(side=tk.LEFT)
        preset_names = ["Custom"] + [name for name, _, _ in CANVAS_PRESETS]
        self.preset_var = tk.StringVar(value="Custom")
        self.preset_menu = ttk.Combobox(
            preset_frame,
            textvariable=self.preset_var,
            values=preset_names,
            state="readonly",
            width=36,
        )
        self.preset_menu.pack(side=tk.LEFT, padx=(5, 0))
        self.preset_menu.bind("<<ComboboxSelected>>", self._on_preset_selected)

        size_frame = tk.Frame(self)
        size_frame.pack(padx=10, pady=10, anchor="w")
        tk.Label(size_frame, text="Width (cm):").grid(row=0, column=0, sticky="w")
        self.width_entry = tk.Entry(size_frame, width=10)
        self.width_entry.insert(0, str(width_cm))
        self.width_entry.grid(row=0, column=1, padx=(5, 0), pady=2)

        tk.Label(size_frame, text="Height (cm):").grid(row=1, column=0, sticky="w")
        self.height_entry = tk.Entry(size_frame, width=10)
        self.height_entry.insert(0, str(height_cm))
        self.height_entry.grid(row=1, column=1, padx=(5, 0), pady=2)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Apply", command=self._apply).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side=tk.LEFT, padx=5)

    def _on_preset_selected(self, _event=None):
        name = self.preset_var.get()
        if name == "Custom":
            return
        for preset_name, width, height in CANVAS_PRESETS:
            if preset_name == name:
                self.width_entry.delete(0, tk.END)
                self.width_entry.insert(0, str(width))
                self.height_entry.delete(0, tk.END)
                self.height_entry.insert(0, str(height))
                return

    def _apply(self):
        try:
            width = float(self.width_entry.get())
            height = float(self.height_entry.get())
        except ValueError:
            messagebox.showerror(
                "Error", "Width and height must be valid numbers.", parent=self
            )
            return
        if width <= 0 or height <= 0:
            messagebox.showerror(
                "Error", "Width and height must be positive.", parent=self
            )
            return
        self.on_apply(width, height)
        self.destroy()


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
        btn = tk.Button(self, text="Save to Templates", command=self.open_save_dialog)
        btn.pack(pady=5)
        tk.Button(self, text="Close", command=self.destroy).pack(pady=5)

    def open_save_dialog(self):
        self.destroy()
        SaveTemplateDialog(self.master, self.json_str)


class SaveTemplateDialog(tk.Toplevel):
    def __init__(self, master, json_str, on_saved=None):
        super().__init__(master)
        self.title("Save Layout Template")
        self.geometry("400x150")
        self.json_str = json_str
        self.on_saved = on_saved
        tk.Label(self, text="Enter a name for your layout (without .json):").pack(
            pady=5
        )
        self.entry = tk.Entry(self, width=30)
        self.entry.pack(pady=5)
        btn = tk.Button(self, text="Save", command=self.save_template)
        btn.pack(pady=5)

    def save_template(self):
        try:
            name = sanitize_template_name(self.entry.get())
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return
        templates_dir = get_templates_dir()
        path = os.path.join(templates_dir, f"{name}.json")
        try:
            with open(path, "w") as f:
                f.write(self.json_str)
            messagebox.showinfo("Success", f"Layout saved as {name}.json")
            if self.on_saved:
                self.on_saved(path)
            self.destroy()
        except OSError as e:
            messagebox.showerror("Error", f"Failed to save layout:\n{e}")


class CodeDialog(tk.Toplevel):
    def __init__(self, master, code_str):
        super().__init__(master)
        self.title("Preview Matplotlib Code")
        self.geometry("700x400")
        self.code_str = code_str
        self.text_widget = tk.Text(self, width=80, height=20)
        self.text_widget.insert("1.0", code_str)
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.pack(padx=10, pady=10)
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=5)
        tk.Button(
            btn_frame, text="Copy to Clipboard", command=self.copy_to_clipboard
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Close", command=self.destroy).pack(
            side=tk.LEFT, padx=5
        )

    def copy_to_clipboard(self):
        self.clipboard_clear()
        self.clipboard_append(self.code_str)
        self.update()
        messagebox.showinfo("Copied", "Code copied to clipboard.", parent=self)


class SettingsDialog(tk.Toplevel):
    def __init__(self, master, settings, on_save):
        super().__init__(master)
        self.title("Settings")
        self.settings = dict(settings)
        self.on_save = on_save
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        row = 0

        tk.Label(self, text="Templates Directory:", anchor="w").grid(
            row=row, column=0, sticky="w", padx=10, pady=(10, 0)
        )
        self.templates_dir_var = tk.StringVar(value=self.settings.get("templates_dir", ""))
        self.templates_dir_entry = tk.Entry(
            self, textvariable=self.templates_dir_var, width=40
        )
        self.templates_dir_entry.grid(row=row, column=1, padx=(5, 0), pady=(10, 0))
        tk.Button(
            self, text="Browse...", command=self._browse_templates_dir
        ).grid(row=row, column=2, padx=(5, 10), pady=(10, 0))
        row += 1

        tk.Label(self, text="Leave empty to use default:").grid(
            row=row, column=1, sticky="w", padx=(5, 0)
        )
        row += 1
        default_path = os.path.join(
            os.path.expanduser("~"), ".config", "axisblueprint", "templates"
        )
        tk.Label(self, text=default_path, fg="gray", anchor="w").grid(
            row=row, column=1, sticky="w", padx=(5, 0), pady=(0, 10)
        )
        row += 1

        sep = ttk.Separator(self, orient="horizontal")
        sep.grid(row=row, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
        row += 1

        tk.Label(self, text="Default Canvas Size:", anchor="w").grid(
            row=row, column=0, sticky="w", padx=10
        )
        self.canvas_width_var = tk.StringVar(
            value=str(self.settings.get("default_canvas_width_cm", 21.0))
        )
        self.canvas_height_var = tk.StringVar(
            value=str(self.settings.get("default_canvas_height_cm", 29.7))
        )
        w_entry = tk.Entry(self, textvariable=self.canvas_width_var, width=8)
        w_entry.grid(row=row, column=1, sticky="w", padx=(5, 0))
        tk.Label(self, text="x").grid(row=row, column=1, padx=(70, 0))
        h_entry = tk.Entry(self, textvariable=self.canvas_height_var, width=8)
        h_entry.grid(row=row, column=1, padx=(85, 0))
        tk.Label(self, text="cm").grid(row=row, column=1, padx=(155, 0))
        row += 1

        sep2 = ttk.Separator(self, orient="horizontal")
        sep2.grid(row=row, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
        row += 1

        tk.Label(self, text="Default Margins (cm):", anchor="w").grid(
            row=row, column=0, sticky="w", padx=10
        )
        row += 1
        margins = self.settings.get("default_margins", {})
        self.margin_vars = {}
        for i, (key, label_text) in enumerate(
            [("left", "Left"), ("right", "Right"), ("top", "Top"), ("bottom", "Bottom")]
        ):
            var = tk.StringVar(value=str(margins.get(key, 1.0)))
            self.margin_vars[key] = var
            tk.Label(self, text=f"{label_text}:").grid(
                row=row, column=0, sticky="e", padx=(20, 5)
            )
            tk.Entry(self, textvariable=var, width=8).grid(
                row=row, column=1, sticky="w"
            )
            row += 1

        sep3 = ttk.Separator(self, orient="horizontal")
        sep3.grid(row=row, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
        row += 1

        tk.Label(self, text="Default Grid Spacing (cm):", anchor="w").grid(
            row=row, column=0, sticky="w", padx=10
        )
        self.grid_spacing_var = tk.StringVar(
            value=str(self.settings.get("default_grid_spacing_cm", 0.2))
        )
        tk.Entry(self, textvariable=self.grid_spacing_var, width=8).grid(
            row=row, column=1, sticky="w", padx=(5, 0)
        )
        row += 1

        sep4 = ttk.Separator(self, orient="horizontal")
        sep4.grid(row=row, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
        row += 1

        btn_frame = tk.Frame(self)
        btn_frame.grid(row=row, column=0, columnspan=3, pady=15)
        tk.Button(btn_frame, text="Save", command=self._save).pack(
            side=tk.LEFT, padx=5
        )
        tk.Button(btn_frame, text="Cancel", command=self.destroy).pack(
            side=tk.LEFT, padx=5
        )

    def _browse_templates_dir(self):
        path = filedialog.askdirectory(title="Select templates directory")
        if path:
            self.templates_dir_var.set(path)

    def _save(self):
        try:
            w = float(self.canvas_width_var.get())
            h = float(self.canvas_height_var.get())
        except ValueError:
            messagebox.showerror("Error", "Canvas dimensions must be numbers.", parent=self)
            return
        if w <= 0 or h <= 0:
            messagebox.showerror("Error", "Canvas dimensions must be positive.", parent=self)
            return

        try:
            gs = float(self.grid_spacing_var.get())
        except ValueError:
            messagebox.showerror("Error", "Grid spacing must be a number.", parent=self)
            return
        if gs <= 0:
            messagebox.showerror("Error", "Grid spacing must be positive.", parent=self)
            return

        margins = {}
        for key in ("left", "right", "top", "bottom"):
            try:
                v = float(self.margin_vars[key].get())
            except ValueError:
                messagebox.showerror(
                    "Error", f"{key.capitalize()} margin must be a number.", parent=self
                )
                return
            if v < 0:
                messagebox.showerror(
                    "Error", "Margins must be non-negative.", parent=self
                )
                return
            margins[key] = v

        self.settings["templates_dir"] = self.templates_dir_var.get().strip()
        self.settings["default_canvas_width_cm"] = w
        self.settings["default_canvas_height_cm"] = h
        self.settings["default_margins"] = margins
        self.settings["default_grid_spacing_cm"] = gs

        self.on_save(self.settings)
        self.destroy()
