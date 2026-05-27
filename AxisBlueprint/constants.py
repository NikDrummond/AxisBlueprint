"""Physical and display constants for the layout canvas."""

SCALE = 20  # pixels per cm
A4_WIDTH_CM = 21
A4_HEIGHT_CM = 29.7
CANVAS_WIDTH = int(A4_WIDTH_CM * SCALE)
CANVAS_HEIGHT = int(A4_HEIGHT_CM * SCALE)
CM_PER_INCH = 2.54

# (label, width_cm, height_cm) — common page and journal figure sizes
CANVAS_PRESETS = [
    ("A4", 21.0, 29.7),
    ("A5", 14.8, 21.0),
    ("US Letter", 21.6, 27.9),
    ("Nature single column (89 mm)", 8.9, 12.0),
    ("Nature double column (183 mm)", 18.3, 12.0),
    ("Science / AAAS single column (~85 mm)", 8.5, 11.0),
    ("Cell single column (~85 mm)", 8.5, 11.0),
    ("PLOS ONE max width (7.5 in)", 19.05, 12.0),
    ("Square (12 cm)", 12.0, 12.0),
    ("Wide panel (16 x 10 cm)", 16.0, 10.0),
]

# (label, width_cm) — one-click journal column widths (height unchanged; axes scaled)
JOURNAL_WIDTH_PRESETS = [
    ("Nature single column (89 mm)", 8.9),
    ("Nature double column (183 mm)", 18.3),
    ("Science / AAAS single column (~85 mm)", 8.5),
    ("Cell single column (~85 mm)", 8.5),
    ("PLOS ONE max width (7.5 in)", 19.05),
    ("PNAS single column (87 mm)", 8.7),
    ("eLife full width (170 mm)", 17.0),
]


def default_panel_label(index):
    """Return A, B, … Z, then AA, AB, … for panel index (0-based)."""
    label = "."
    n = index + 1
    while n:
        n, rem = divmod(n - 1, 26)
        label = chr(ord('a') + rem) + label
    return label
