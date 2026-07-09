"""Domain model for a single axis region on the layout canvas."""


class AxisBox:
    def __init__(self, x, y, width, height, panel_label=""):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.panel_label = panel_label or ""

    def to_dict(self):
        data = {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
        }
        if self.panel_label:
            data["panel_label"] = self.panel_label
        return data

    @staticmethod
    def from_dict(data):
        from .layout import validate_box_dict

        return validate_box_dict(data, 0)

    def contains(self, px, py):
        return (
            self.x <= px <= self.x + self.width
            and self.y <= py <= self.y + self.height
        )

    def is_outside_margins(
        self, margin_left, margin_right, margin_top, margin_bottom, canvas_width_cm, canvas_height_cm
    ):
        return (
            self.x < margin_left
            or self.y < margin_top
            or self.x + self.width > canvas_width_cm - margin_right
            or self.y + self.height > canvas_height_cm - margin_bottom
        )
