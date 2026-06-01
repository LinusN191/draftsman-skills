"""Unit tests for common geometry primitives."""

from __future__ import annotations

import math
import pathlib
import sys
import unittest

# Bootstrap the hyphenated ``zone-derivation`` package via importlib.
_TESTS_DIR = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_TESTS_DIR))
from _bootstrap import common  # noqa: E402  (import after sys.path tweak)


class TestCylinderToPolygon(unittest.TestCase):
    def test_default_sides_is_twelve_per_spec(self) -> None:
        polygon = common.cylinder_to_polygon((0.0, 0.0), 1000.0)
        self.assertEqual(
            len(polygon),
            12,
            "spec §5.2 requires at least 12 sides for cylindrical zones",
        )

    def test_polygon_vertices_lie_on_circle(self) -> None:
        radius = 1500.0
        polygon = common.cylinder_to_polygon((100.0, 200.0), radius, sides=16)
        for x, y in polygon:
            distance = math.hypot(x - 100.0, y - 200.0)
            self.assertAlmostEqual(distance, radius, places=6)

    def test_rejects_under_twelve_sides(self) -> None:
        with self.assertRaises(ValueError):
            common.cylinder_to_polygon((0.0, 0.0), 100.0, sides=8)

    def test_rejects_non_positive_radius(self) -> None:
        with self.assertRaises(ValueError):
            common.cylinder_to_polygon((0.0, 0.0), 0.0)


class TestExpandPolygonHorizontally(unittest.TestCase):
    def test_axis_aligned_rectangle_expands_by_distance(self) -> None:
        rect: list[tuple[float, float]] = [
            (0.0, 0.0),
            (1000.0, 0.0),
            (1000.0, 500.0),
            (0.0, 500.0),
        ]
        expanded = common.expand_polygon_horizontally(rect, 600.0)
        # Expanded should be -600, -600 to 1600, 1100
        xs = [p[0] for p in expanded]
        ys = [p[1] for p in expanded]
        self.assertAlmostEqual(min(xs), -600.0)
        self.assertAlmostEqual(max(xs), 1600.0)
        self.assertAlmostEqual(min(ys), -600.0)
        self.assertAlmostEqual(max(ys), 1100.0)

    def test_returns_four_vertex_rectangle(self) -> None:
        rect: list[tuple[float, float]] = [
            (0.0, 0.0),
            (1000.0, 0.0),
            (1000.0, 1000.0),
            (0.0, 1000.0),
        ]
        expanded = common.expand_polygon_horizontally(rect, 200.0)
        self.assertEqual(len(expanded), 4)

    def test_rejects_zero_distance(self) -> None:
        rect: list[tuple[float, float]] = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0)]
        with self.assertRaises(ValueError):
            common.expand_polygon_horizontally(rect, 0.0)


class TestPolygonIntersects(unittest.TestCase):
    def test_overlapping_rectangles_intersect(self) -> None:
        rect_a: list[tuple[float, float]] = [
            (0.0, 0.0),
            (100.0, 0.0),
            (100.0, 100.0),
            (0.0, 100.0),
        ]
        rect_b: list[tuple[float, float]] = [
            (50.0, 50.0),
            (150.0, 50.0),
            (150.0, 150.0),
            (50.0, 150.0),
        ]
        self.assertTrue(common.polygon_intersects(rect_a, rect_b))

    def test_disjoint_rectangles_do_not_intersect(self) -> None:
        rect_a: list[tuple[float, float]] = [
            (0.0, 0.0),
            (100.0, 0.0),
            (100.0, 100.0),
            (0.0, 100.0),
        ]
        rect_b: list[tuple[float, float]] = [
            (200.0, 200.0),
            (300.0, 200.0),
            (300.0, 300.0),
            (200.0, 300.0),
        ]
        self.assertFalse(common.polygon_intersects(rect_a, rect_b))

    def test_inner_polygon_inside_outer_intersects(self) -> None:
        outer: list[tuple[float, float]] = [
            (0.0, 0.0),
            (1000.0, 0.0),
            (1000.0, 1000.0),
            (0.0, 1000.0),
        ]
        inner: list[tuple[float, float]] = [
            (400.0, 400.0),
            (600.0, 400.0),
            (600.0, 600.0),
            (400.0, 600.0),
        ]
        self.assertTrue(common.polygon_intersects(outer, inner))


class TestPointInPolygon(unittest.TestCase):
    def test_point_inside_rectangle(self) -> None:
        rect: list[tuple[float, float]] = [
            (0.0, 0.0),
            (100.0, 0.0),
            (100.0, 100.0),
            (0.0, 100.0),
        ]
        self.assertTrue(common.point_in_polygon((50.0, 50.0), rect))

    def test_point_outside_rectangle(self) -> None:
        rect: list[tuple[float, float]] = [
            (0.0, 0.0),
            (100.0, 0.0),
            (100.0, 100.0),
            (0.0, 100.0),
        ]
        self.assertFalse(common.point_in_polygon((200.0, 50.0), rect))

    def test_point_in_polygon_handles_concave(self) -> None:
        # L-shaped polygon
        l_shape: list[tuple[float, float]] = [
            (0.0, 0.0),
            (200.0, 0.0),
            (200.0, 100.0),
            (100.0, 100.0),
            (100.0, 200.0),
            (0.0, 200.0),
        ]
        # Inside the L
        self.assertTrue(common.point_in_polygon((50.0, 50.0), l_shape))
        # In the missing corner
        self.assertFalse(common.point_in_polygon((150.0, 150.0), l_shape))


class TestPolygonAreaMm2(unittest.TestCase):
    def test_unit_square_area(self) -> None:
        square: list[tuple[float, float]] = [
            (0.0, 0.0),
            (100.0, 0.0),
            (100.0, 100.0),
            (0.0, 100.0),
        ]
        self.assertAlmostEqual(common.polygon_area_mm2(square), 10000.0)

    def test_triangle_area(self) -> None:
        triangle: list[tuple[float, float]] = [
            (0.0, 0.0),
            (100.0, 0.0),
            (0.0, 100.0),
        ]
        self.assertAlmostEqual(common.polygon_area_mm2(triangle), 5000.0)

    def test_rejects_degenerate(self) -> None:
        with self.assertRaises(ValueError):
            common.polygon_area_mm2([(0.0, 0.0), (1.0, 0.0)])


if __name__ == "__main__":
    unittest.main()
