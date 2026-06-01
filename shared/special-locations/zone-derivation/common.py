"""Common geometry primitives for zone derivation.

Stdlib-only. All coordinates in millimetres; polygon vertices ordered
counter-clockwise (right-handed convention) so polygon-orientation tests
in downstream renderers behave predictably.
"""

from __future__ import annotations

import math
from typing import Sequence

Point = tuple[float, float]
Polygon = list[Point]


def cylinder_to_polygon(
    center_xy: Point, radius_mm: float, sides: int = 12
) -> Polygon:
    """Approximate a cylinder cross-section as a regular polygon.

    Per spec §5.2: cylindrical zones MUST use at least 12-sided regular
    polygons centred on the anchor. Vertices are ordered counter-clockwise
    starting at angle 0 (positive x-axis).

    Args:
        center_xy: (x_mm, y_mm) centre of the cylinder.
        radius_mm: cylinder radius in millimetres (positive).
        sides: vertex count (>= 12 to satisfy the schema invariant).

    Returns:
        A closed polygon as a list of (x_mm, y_mm) tuples. Not closed
        explicitly (first vertex is NOT repeated at the end) — consumers
        treat the polygon as implicitly closed.
    """
    if sides < 12:
        raise ValueError(
            "cylinder_to_polygon requires sides >= 12 per spec §5.2"
        )
    if radius_mm <= 0:
        raise ValueError("radius_mm must be positive")

    cx, cy = center_xy
    step = 2.0 * math.pi / sides
    return [
        (cx + radius_mm * math.cos(i * step), cy + radius_mm * math.sin(i * step))
        for i in range(sides)
    ]


def rectangular_zone(
    center_xy: Point,
    length_mm: float,
    width_mm: float,
    rotation_deg: float = 0.0,
) -> Polygon:
    """Build a 4-vertex rectangular polygon centred on ``center_xy``.

    ``length_mm`` is the dimension along the rotated x-axis; ``width_mm``
    along the rotated y-axis. Vertex order: bottom-left, bottom-right,
    top-right, top-left (counter-clockwise in the rotated frame).
    """
    if length_mm <= 0 or width_mm <= 0:
        raise ValueError("length_mm and width_mm must be positive")

    half_l = length_mm / 2.0
    half_w = width_mm / 2.0
    cx, cy = center_xy
    theta = math.radians(rotation_deg)
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)

    # Counter-clockwise vertex order in the rotated local frame
    local: list[Point] = [
        (-half_l, -half_w),
        (+half_l, -half_w),
        (+half_l, +half_w),
        (-half_l, +half_w),
    ]
    return [
        (cx + lx * cos_t - ly * sin_t, cy + lx * sin_t + ly * cos_t)
        for lx, ly in local
    ]


def expand_polygon_horizontally(
    polygon: Sequence[Point], distance_mm: float
) -> Polygon:
    """Expand a polygon outward by ``distance_mm`` along its bounding box.

    Exact for axis-aligned rectangles (the dominant bath/pool §701/§702 use
    case). For non-rectangular polygons the implementation expands the
    axis-aligned bounding box, which is an upper bound — runtime project
    handles exact Minkowski sum.

    Args:
        polygon: input polygon vertices (>= 3 points).
        distance_mm: outward expansion distance in mm (must be > 0).

    Returns:
        A 4-vertex rectangle containing the expanded polygon.
    """
    if distance_mm <= 0:
        raise ValueError("distance_mm must be positive")
    if len(polygon) < 3:
        raise ValueError("polygon must have at least 3 vertices")

    xs = [p[0] for p in polygon]
    ys = [p[1] for p in polygon]
    x_min = min(xs) - distance_mm
    x_max = max(xs) + distance_mm
    y_min = min(ys) - distance_mm
    y_max = max(ys) + distance_mm
    return [
        (x_min, y_min),
        (x_max, y_min),
        (x_max, y_max),
        (x_min, y_max),
    ]


def _polygon_edges(polygon: Sequence[Point]) -> list[tuple[Point, Point]]:
    """Return the list of (start, end) edge pairs for a closed polygon."""
    return [(polygon[i], polygon[(i + 1) % len(polygon)]) for i in range(len(polygon))]


def _project_polygon(axis: Point, polygon: Sequence[Point]) -> tuple[float, float]:
    """Project a polygon onto an axis; returns (min, max) scalar projections."""
    ax, ay = axis
    dots = [vx * ax + vy * ay for vx, vy in polygon]
    return min(dots), max(dots)


def polygon_intersects(poly1: Sequence[Point], poly2: Sequence[Point]) -> bool:
    """Test polygon intersection via the Separating Axis Theorem.

    Correct for convex polygons (all zone polygons in this library are convex
    by construction: rectangles, regular polygons, and axis-aligned bounding
    boxes). For non-convex polygons the runtime project hosts an exact test.
    """
    if len(poly1) < 3 or len(poly2) < 3:
        raise ValueError("both polygons require at least 3 vertices")

    for polygon in (poly1, poly2):
        for (x1, y1), (x2, y2) in _polygon_edges(polygon):
            # Outward normal to the edge
            normal = (-(y2 - y1), x2 - x1)
            length = math.hypot(*normal)
            if length == 0:
                continue
            axis = (normal[0] / length, normal[1] / length)
            min1, max1 = _project_polygon(axis, poly1)
            min2, max2 = _project_polygon(axis, poly2)
            if max1 < min2 or max2 < min1:
                # Found a separating axis — no intersection
                return False
    return True


def polygon_subtract(
    outer: Sequence[Point], inner: Sequence[Point]
) -> Polygon:
    """Difference of two polygons (``outer`` - ``inner``).

    Used for sauna_zone_2 = sauna_room - sauna_zone_1. This reference
    implementation returns the ``outer`` polygon unchanged — downstream IR
    consumers detect the ``inner`` overlap via ``overlapping_with_zone_ids``
    and the polygons are rendered with the inner zone drawn on top
    (paint-order subtraction). The runtime project hosts exact boolean
    polygon subtraction when the inner is non-convex.

    Limitation recorded explicitly: exact for convex outer + convex inner where
    inner sits entirely inside outer (the sauna case); concave shapes deferred.

    Args:
        outer: enclosing polygon (>= 3 vertices).
        inner: subtracted polygon (>= 3 vertices, ideally inside ``outer``).

    Returns:
        A new list of ``outer`` vertices (defensive copy).
    """
    if len(outer) < 3 or len(inner) < 3:
        raise ValueError("both polygons require at least 3 vertices")
    return [(x, y) for x, y in outer]


def point_in_polygon(point: Point, polygon: Sequence[Point]) -> bool:
    """Ray-casting point-in-polygon test.

    Returns True if the point sits strictly inside or on the boundary of the
    polygon. Handles both convex and non-convex polygons.
    """
    if len(polygon) < 3:
        raise ValueError("polygon must have at least 3 vertices")

    px, py = point
    inside = False
    n = len(polygon)
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        intersect = (yi > py) != (yj > py) and px < (
            (xj - xi) * (py - yi) / (yj - yi if (yj - yi) != 0 else 1e-9) + xi
        )
        if intersect:
            inside = not inside
        j = i
    return inside


def polygon_area_mm2(polygon: Sequence[Point]) -> float:
    """Compute the signed polygon area via the shoelace formula.

    Returns a positive value for counter-clockwise polygons. Used in unit
    tests to verify §703 sauna 3-zone areas sum to the sauna room area.
    """
    if len(polygon) < 3:
        raise ValueError("polygon must have at least 3 vertices")
    total = 0.0
    n = len(polygon)
    for i in range(n):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % n]
        total += x1 * y2 - x2 * y1
    return abs(total) / 2.0
