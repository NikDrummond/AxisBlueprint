import unittest

from AxisBlueprint.models import AxisBox
from AxisBlueprint.alignment import (
    align_boxes_left,
    distribute_boxes_horizontally,
)
from AxisBlueprint.constants import default_panel_label
from AxisBlueprint.export import generate_matplotlib_code
from AxisBlueprint.layout import validate_box_dict


class TestAlignment(unittest.TestCase):
    def test_align_left(self):
        boxes = [AxisBox(2, 0, 3, 2), AxisBox(5, 0, 3, 2)]
        align_boxes_left(boxes)
        self.assertEqual(boxes[0].x, 2)
        self.assertEqual(boxes[1].x, 2)

    def test_distribute_horizontally(self):
        boxes = [AxisBox(0, 0, 2, 2), AxisBox(6, 0, 2, 2), AxisBox(12, 0, 2, 2)]
        distribute_boxes_horizontally(boxes)
        self.assertAlmostEqual(boxes[0].x, 0)
        self.assertAlmostEqual(boxes[2].x + boxes[2].width, 14)
        self.assertAlmostEqual(boxes[1].x, 6)


class TestPanelLabels(unittest.TestCase):
    def test_default_panel_label(self):
        self.assertEqual(default_panel_label(0), "A")
        self.assertEqual(default_panel_label(3), "D")
        self.assertEqual(default_panel_label(25), "Z")
        self.assertEqual(default_panel_label(26), "AA")

    def test_roundtrip_panel_label(self):
        box = validate_box_dict(
            {"x": 1, "y": 2, "width": 3, "height": 4, "panel_label": "B"}, 0
        )
        self.assertEqual(box.panel_label, "B")
        self.assertEqual(box.to_dict()["panel_label"], "B")

    def test_code_includes_panel_label(self):
        boxes = [AxisBox(1, 1, 5, 5, panel_label="A")]
        code = generate_matplotlib_code(boxes, 21, 29.7)
        self.assertIn('text(0.02, 0.98, "A"', code)


if __name__ == "__main__":
    unittest.main()
