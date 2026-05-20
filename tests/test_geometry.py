"""Tests for geometry helpers."""

import unittest

from AxisBlueprint.geometry import boxes_overlap, overlapping_box_indices
from AxisBlueprint.models import AxisBox


class TestGeometry(unittest.TestCase):
    def test_no_overlap_touching(self):
        a = AxisBox(0, 0, 2, 2)
        b = AxisBox(2, 0, 2, 2)
        self.assertFalse(boxes_overlap(a, b))

    def test_overlap(self):
        a = AxisBox(0, 0, 3, 3)
        b = AxisBox(2, 2, 3, 3)
        self.assertTrue(boxes_overlap(a, b))

    def test_overlapping_indices(self):
        boxes = [
            AxisBox(0, 0, 3, 3),
            AxisBox(2, 2, 3, 3),
            AxisBox(10, 10, 2, 2),
        ]
        idx = overlapping_box_indices(boxes)
        self.assertEqual(idx, {0, 1})


if __name__ == "__main__":
    unittest.main()
