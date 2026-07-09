"""Canvas geometry helpers: overlap detection, snap guides."""


def boxes_overlap(a, b):
    """True if closed rectangles intersect with positive area (touching edges = no)."""
    if a.x + a.width <= b.x or b.x + b.width <= a.x:
        return False
    if a.y + a.height <= b.y or b.y + b.height <= a.y:
        return False
    return True


def overlapping_box_indices(boxes):
    """Indices of boxes that participate in any overlap (positive area)."""
    bad = set()
    n = len(boxes)
    for i in range(n):
        for j in range(i + 1, n):
            if boxes_overlap(boxes[i], boxes[j]):
                bad.add(i)
                bad.add(j)
    return bad


def snap_move_to_guides(nx, ny, w, h, others, threshold_cm):
    """
    Snap top-left (nx, ny) using other boxes' edges and centers.
    others: iterable of AxisBox excluding the moving box(es).
    """
    xs = []
    ys = []
    for o in others:
        xs.extend([o.x, o.x + o.width * 0.5 - w * 0.5, o.x + o.width - w])
        ys.extend([o.y, o.y + o.height * 0.5 - h * 0.5, o.y + o.height - h])

    def snap(val, candidates):
        best = val
        best_d = threshold_cm
        for c in candidates:
            d = abs(val - c)
            if d < best_d:
                best_d = d
                best = c
        return best

    if xs:
        nx = snap(nx, xs)
    if ys:
        ny = snap(ny, ys)
    return nx, ny
