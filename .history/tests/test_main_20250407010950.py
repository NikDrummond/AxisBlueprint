import unittest
import tkinter as tk
import json
import os
import tempfile
import matplotlib.pyplot as plt
from unittest.mock import patch
import tkinter.filedialog as fd

# Import from your package. Adjust the case as necessary.
from AxisBlueprint.main import AxisBox, LayoutDesigner, FigureFromLayout, PreviewDialog, SaveTemplateDialog

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
        box = AxisBox(2.5, 3.5, 4, 5)
        d = box.to_dict()
        self.assertEqual(d, {"x": 2.5, "y": 3.5, "width": 4, "height": 5})
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
        # Create a hidden Tk root for testing.
        self.root = tk.Tk()
        self.root.withdraw()
        self.ld = LayoutDesigner(self.root)
    
    def tearDown(self):
        self.root.destroy()
    
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
        # Set non-rounded values and then optimize.
        box = self.ld.boxes[0]
        box.x = 1.23
        box.y = 2.34
        box.width = 3.45
        box.height = 4.56
        self.ld.optimize_layout()
        self.assertAlmostEqual(box.x, round(1.23 * 2) / 2)
        self.assertAlmostEqual(box.y, round(2.34 * 2) / 2)
        self.assertAlmostEqual(box.width, round(3.45 * 2) / 2)
        self.assertAlmostEqual(box.height, round(4.56 * 2) / 2)
    
    def test_generate_code_output(self):
        # Patch CodeDialog to capture the generated code instead of opening a dialog.
        with patch("AxisBlueprint.main.CodeDialog") as mock_code_dialog:
            self.ld.generate_code()
            # Verify that CodeDialog was called.
            mock_code_dialog.assert_called_once()
            # Retrieve the arguments passed to CodeDialog.
            args, kwargs = mock_code_dialog.call_args
            code_str = args[1]  # The generated code string.
            self.assertIn("plt.show()", code_str)
    
    def test_save_load_layout(self):
        # Save the current layout to JSON.
        layout_data = [box.to_dict() for box in self.ld.boxes]
        json_str = json.dumps(layout_data, indent=2)
        # Create a new LayoutDesigner instance and simulate loading the layout.
        new_ld =_
