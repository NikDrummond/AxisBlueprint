import matplotlib
matplotlib.use('Agg')


import unittest
import tkinter as tk
import json
import os
import tempfile
import matplotlib.pyplot as plt
from unittest.mock import patch
import tkinter.filedialog as fd

# Import from your package. Adjust the case as necessary.
from AxisBlueprint.main import (
    AxisBox,
    LayoutDesigner,
    FigureFromLayout,
    PreviewDialog,
    SaveTemplateDialog,
    get_templates_dir,
    parse_layout_data,
    snap_to_grid,
    build_layout_document,
)

# -------------------------------
# Tests for the AxisBox class.
# -------------------------------
class TestAxisBox(unittest.TestCase):
    def test_contains(self):
        box = AxisBox(1, 1, 4, 4)
        # Points inside the box.
        self.assertTrue(box.contains(2, 2))
        self.assertTrue(box.contains(1, 1))
        self.assertTrue(box.contains(5, 5))
        # Points outside the box.
        self.assertFalse(box.contains(0.9, 1))
        self.assertFalse(box.contains(5.1, 5))
    
    def test_to_from_dict(self):
        box = AxisBox(2.5, 3.5, 4, 5, panel_label="C")
        d = box.to_dict()
        self.assertEqual(
            d, {"x": 2.5, "y": 3.5, "width": 4, "height": 5, "panel_label": "C"}
        )
        box2 = AxisBox.from_dict(d)
        self.assertEqual(box2.x, 2.5)
        self.assertEqual(box2.y, 3.5)
        self.assertEqual(box2.width, 4)
        self.assertEqual(box2.height, 5)

# -------------------------------
# Tests for the LayoutDesigner class.
# -------------------------------
class TestLayoutDesigner(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.templates_dir = os.path.join(self.temp_dir.name, "templates")
        os.makedirs(self.templates_dir, exist_ok=True)
        self._orig_templates_env = os.environ.get("AXISBLUEPRINT_TEMPLATES_DIR")
        os.environ["AXISBLUEPRINT_TEMPLATES_DIR"] = self.templates_dir
        self.root = tk.Tk()
        self.root.withdraw()
        self.ld = LayoutDesigner(self.root)

    def tearDown(self):
        self.root.destroy()
        if self._orig_templates_env is None:
            os.environ.pop("AXISBLUEPRINT_TEMPLATES_DIR", None)
        else:
            os.environ["AXISBLUEPRINT_TEMPLATES_DIR"] = self._orig_templates_env
        self.temp_dir.cleanup()
    
    def test_default_layout(self):
        # Check that the default layout has exactly 4 boxes.
        self.assertEqual(len(self.ld.boxes), 4)
    
    def test_add_axis(self):
        initial = len(self.ld.boxes)
        self.ld.add_axis()
        self.assertEqual(len(self.ld.boxes), initial + 1)
    
    def test_duplicate_axis(self):
        # Duplicate the first box.
        if self.ld.boxes:
            self.ld.selected_box = self.ld.boxes[0]
            initial = len(self.ld.boxes)
            self.ld.duplicate_axis()
            self.assertEqual(len(self.ld.boxes), initial + 1)
            dup = self.ld.boxes[-1]
            self.assertAlmostEqual(dup.x, self.ld.boxes[0].x + 1)
            self.assertAlmostEqual(dup.y, self.ld.boxes[0].y + 1)
    
    def test_remove_axis(self):
        initial = len(self.ld.boxes)
        self.ld.selected_box = self.ld.boxes[0]
        self.ld.remove_axis()
        self.assertEqual(len(self.ld.boxes), initial - 1)
    
    def test_optimize_layout(self):
        box = self.ld.boxes[0]
        box.x = 1.23
        box.y = 2.34
        box.width = 3.45
        box.height = 4.56
        spacing = self.ld.grid_spacing_cm
        self.ld.optimize_layout()
        self.assertAlmostEqual(box.x, snap_to_grid(1.23, spacing))
        self.assertAlmostEqual(box.y, snap_to_grid(2.34, spacing))
        self.assertAlmostEqual(box.width, snap_to_grid(3.45, spacing))
        self.assertAlmostEqual(box.height, snap_to_grid(4.56, spacing))
    
    def test_generate_code_output(self):
        # Patch CodeDialog to capture the generated code instead of opening a dialog.
        with patch("AxisBlueprint.designer.CodeDialog") as mock_code_dialog:
            self.ld.preview_code()
            # Verify that CodeDialog was called.
            mock_code_dialog.assert_called_once()
            # Retrieve the arguments passed to CodeDialog.
            args, kwargs = mock_code_dialog.call_args
            code_str = args[1]  # The generated code string.
            self.assertIn("plt.show()", code_str)
    
    def test_save_load_layout(self):
        layout_data = self.ld.get_layout_document()
        new_ld = LayoutDesigner(self.root)
        doc = parse_layout_data(layout_data)
        new_ld.apply_document(doc)
        self.assertEqual(len(new_ld.boxes), len(self.ld.boxes))
        for b1, b2 in zip(new_ld.boxes, self.ld.boxes):
            self.assertAlmostEqual(b1.x, b2.x)
            self.assertAlmostEqual(b1.y, b2.y)
            self.assertAlmostEqual(b1.width, b2.width)
            self.assertAlmostEqual(b1.height, b2.height)

# -------------------------------
# Tests for template functions and dialogs.
# -------------------------------
class TestTemplateFunctions(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.templates_dir = os.path.join(self.temp_dir.name, "templates")
        os.makedirs(self.templates_dir, exist_ok=True)
        self._orig_templates_env = os.environ.get("AXISBLUEPRINT_TEMPLATES_DIR")
        os.environ["AXISBLUEPRINT_TEMPLATES_DIR"] = self.templates_dir
        self.root = tk.Tk()
        self.root.withdraw()
        self.ld = LayoutDesigner(self.root)

    def tearDown(self):
        self.root.destroy()
        if self._orig_templates_env is None:
            os.environ.pop("AXISBLUEPRINT_TEMPLATES_DIR", None)
        else:
            os.environ["AXISBLUEPRINT_TEMPLATES_DIR"] = self._orig_templates_env
        self.temp_dir.cleanup()
    
    def test_save_default_template(self):
        """Test that the default template is saved in the templates folder."""
        default_path = os.path.join(get_templates_dir(), "default.json")
        self.assertTrue(os.path.isfile(default_path))
        with open(default_path, "r") as f:
            data = json.load(f)
        self.assertIn("canvas", data)
        self.assertIn("boxes", data)
        self.assertEqual(data.get("version"), 1)
        self.assertGreater(len(data["boxes"]), 0)
    
    def test_FigureFromLayout(self):
        """Test that FigureFromLayout returns a valid matplotlib figure and axes."""
        templates_dir = get_templates_dir()
        test_layout = {
            "canvas": {"width_cm": 21, "height_cm": 29.7},
            "boxes": [
                {"x": 1, "y": 1, "width": 5, "height": 5},
                {"x": 7, "y": 1, "width": 5, "height": 5},
            ],
        }
        layout_name = "testlayout"
        test_path = os.path.join(templates_dir, f"{layout_name}.json")
        with open(test_path, "w") as f:
            json.dump(test_layout, f, indent=2)
        fig, axes = FigureFromLayout(layout_name)
        self.assertIsInstance(fig, plt.Figure)
        self.assertEqual(len(axes), 2)
        plt.close(fig)

    def test_FigureFromLayout_custom_directory(self):
        """Load layout from an explicit directory path."""
        custom_dir = os.path.join(self.temp_dir.name, "custom_layouts")
        os.makedirs(custom_dir, exist_ok=True)
        test_layout = {
            "canvas": {"width_cm": 10, "height_cm": 10},
            "boxes": [{"x": 1, "y": 1, "width": 4, "height": 4}],
        }
        layout_name = "custom_fig"
        with open(os.path.join(custom_dir, f"{layout_name}.json"), "w") as f:
            json.dump(test_layout, f, indent=2)
        fig, axes = FigureFromLayout(layout_name, custom_dir)
        self.assertIsInstance(fig, plt.Figure)
        self.assertEqual(len(axes), 1)
        plt.close(fig)
    
    def test_load_layout(self):
        """Simulate loading a layout via the file dialog."""
        templates_dir = get_templates_dir()
        test_layout = build_layout_document(
            [AxisBox(2, 2, 6, 6)],
            25.0,
            30.0,
            margin_left=1.0,
            margin_right=1.0,
            margin_top=1.0,
            margin_bottom=1.0,
        )
        test_file = os.path.join(templates_dir, "single.json")
        with open(test_file, "w") as f:
            json.dump(test_layout, f, indent=2)
        
        original_askopenfilename = fd.askopenfilename
        fd.askopenfilename = lambda **kwargs: test_file
        
        self.ld.load_layout()
        self.assertEqual(len(self.ld.boxes), 1)
        box = self.ld.boxes[0]
        self.assertEqual(box.x, 2)
        self.assertEqual(box.y, 2)
        self.assertEqual(box.width, 6)
        self.assertEqual(box.height, 6)
        self.assertEqual(self.ld.canvas_width_cm, 25.0)
        self.assertEqual(self.ld.canvas_height_cm, 30.0)
        fd.askopenfilename = original_askopenfilename  # restore
    
    def test_preview_dialog_instantiation(self):
        """Test that the preview dialog can be created with valid JSON."""
        json_str = json.dumps(self.ld.get_layout_document(), indent=2)
        preview = PreviewDialog(self.root, json_str)
        self.assertIsNotNone(preview)
        preview.destroy()
    
    def test_save_template_dialog(self):
        """Test that SaveTemplateDialog saves a file when a name is provided."""
        json_str = json.dumps(self.ld.get_layout_document(), indent=2)
        dialog = SaveTemplateDialog(self.root, json_str)
        dialog.entry.insert(0, "unittest_layout")
        dialog.save_template()
        expected_path = os.path.join(get_templates_dir(), "unittest_layout.json")
        self.assertTrue(os.path.isfile(expected_path))
        os.remove(expected_path)
        dialog.destroy()

if __name__ == "__main__":
    unittest.main()
