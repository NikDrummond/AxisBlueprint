"""Align and distribute axis boxes for tidy multi-panel layouts."""


def align_boxes_left(boxes):
    if not boxes:
        return
    target = min(b.x for b in boxes)
    for box in boxes:
        box.x = target


def align_boxes_right(boxes):
    if not boxes:
        return
    target = max(b.x + b.width for b in boxes)
    for box in boxes:
        box.x = target - box.width


def align_boxes_top(boxes):
    if not boxes:
        return
    target = min(b.y for b in boxes)
    for box in boxes:
        box.y = target


def align_boxes_bottom(boxes):
    if not boxes:
        return
    target = max(b.y + b.height for b in boxes)
    for box in boxes:
        box.y = target - box.height


def align_boxes_center_horizontal(boxes):
    if not boxes:
        return
    avg = sum(b.x + b.width / 2 for b in boxes) / len(boxes)
    for box in boxes:
        box.x = avg - box.width / 2


def align_boxes_center_vertical(boxes):
    if not boxes:
        return
    avg = sum(b.y + b.height / 2 for b in boxes) / len(boxes)
    for box in boxes:
        box.y = avg - box.height / 2


def distribute_boxes_horizontally(boxes):
    if len(boxes) < 2:
        return
    ordered = sorted(boxes, key=lambda b: b.x)
    left = ordered[0].x
    right = ordered[-1].x + ordered[-1].width
    total_width = sum(b.width for b in ordered)
    n = len(ordered)
    gap = (right - left - total_width) / (n - 1)
    x = left
    for box in ordered:
        box.x = x
        x += box.width + gap


def distribute_boxes_vertically(boxes):
    if len(boxes) < 2:
        return
    ordered = sorted(boxes, key=lambda b: b.y)
    top = ordered[0].y
    bottom = ordered[-1].y + ordered[-1].height
    total_height = sum(b.height for b in ordered)
    n = len(ordered)
    gap = (bottom - top - total_height) / (n - 1)
    y = top
    for box in ordered:
        box.y = y
        y += box.height + gap
