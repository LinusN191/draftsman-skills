"""Unit tests for §702 pool zone derivation."""

from __future__ import annotations

import pathlib
import sys
import unittest

_TESTS_DIR = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_TESTS_DIR))
from _bootstrap import pool  # noqa: E402


def _commercial_pool_anchor() -> dict:
    """5 x 10 m rectangular commercial pool, 1.8 m deep."""
    return {
        "type": "pool_basin",
        "id": "pool_main",
        "position": {"x_mm": 2500.0, "y_mm": 5000.0, "z_floor_mm": 0.0},
        "dimensions": {
            "length_mm": 10000.0,
            "width_mm": 5000.0,
            "height_mm": 1800.0,
        },
        "shape_kind": "rectangular",
    }


def _circular_pool_anchor() -> dict:
    return {
        "type": "pool_basin",
        "id": "pool_round",
        "position": {"x_mm": 2500.0, "y_mm": 2500.0, "z_floor_mm": 0.0},
        "shape_kind": "cylinder",
        "radius_mm": 2000.0,
    }


class TestPoolZone0(unittest.TestCase):
    def test_zone_0_is_selv_ipx8(self) -> None:
        zone = pool.pool_zone_0(_commercial_pool_anchor())
        self.assertEqual(zone["zone_type"], "pool_zone_0")
        self.assertEqual(zone["ip_rating_min"], "IPx8")
        self.assertEqual(zone["max_voltage_v"], 12)

    def test_zone_0_polygon_matches_basin(self) -> None:
        zone = pool.pool_zone_0(_commercial_pool_anchor())
        xs = [p[0] for p in zone["boundary_plan_polygon_mm"]]
        self.assertAlmostEqual(max(xs) - min(xs), 10000.0)

    def test_cylindrical_pool_uses_12_sided_polygon(self) -> None:
        zone = pool.pool_zone_0(_circular_pool_anchor())
        self.assertGreaterEqual(len(zone["boundary_plan_polygon_mm"]), 12)


class TestPoolZone1(unittest.TestCase):
    def test_zone_1_height_extends_2500mm_above_water(self) -> None:
        water_z = 1500.0
        zone = pool.pool_zone_1(_commercial_pool_anchor(), water_surface_z=water_z)
        self.assertEqual(zone["height_max_mm"], water_z + 2500.0)
        self.assertEqual(zone["ip_rating_min"], "IPx5")

    def test_zone_1_polygon_matches_basin(self) -> None:
        zone = pool.pool_zone_1(_commercial_pool_anchor(), water_surface_z=1500.0)
        xs = [p[0] for p in zone["boundary_plan_polygon_mm"]]
        self.assertAlmostEqual(max(xs) - min(xs), 10000.0)

    def test_zone_1_rcd_required(self) -> None:
        zone = pool.pool_zone_1(_commercial_pool_anchor(), water_surface_z=1500.0)
        self.assertEqual(zone["rcd_required_ma"], 30)


class TestPoolZone2(unittest.TestCase):
    def test_zone_2_spans_9m_wide_per_brief(self) -> None:
        """5 x 10 m pool → Zone 2 spans 5+2+2 = 9 m wide."""
        zone = pool.pool_zone_2(_commercial_pool_anchor(), water_surface_z=1500.0)
        ys = [p[1] for p in zone["boundary_plan_polygon_mm"]]
        self.assertAlmostEqual(max(ys) - min(ys), 5000.0 + 2 * 2000.0)

    def test_zone_2_length_extends_14m(self) -> None:
        """10 m pool length + 2 m each side = 14 m."""
        zone = pool.pool_zone_2(_commercial_pool_anchor(), water_surface_z=1500.0)
        xs = [p[0] for p in zone["boundary_plan_polygon_mm"]]
        self.assertAlmostEqual(max(xs) - min(xs), 10000.0 + 2 * 2000.0)

    def test_zone_2_citation_includes_702_55_4(self) -> None:
        zone = pool.pool_zone_2(_commercial_pool_anchor(), water_surface_z=1500.0)
        self.assertIn("702.55.4", zone["_clause_citation"])


class TestChangingRoomOverlap(unittest.TestCase):
    def _zone_2_polygon(self) -> list[tuple[float, float]]:
        return [
            (-2000.0, -2000.0),
            (12000.0, -2000.0),
            (12000.0, 7000.0),
            (-2000.0, 7000.0),
        ]

    def test_barrier_required_when_gap_below_threshold(self) -> None:
        zone_2 = self._zone_2_polygon()
        # Adjacent room 100 mm away from zone 2 edge → barrier REQUIRED
        adjacent = [
            (12100.0, 0.0),
            (15000.0, 0.0),
            (15000.0, 5000.0),
            (12100.0, 5000.0),
        ]
        self.assertTrue(
            pool.check_changing_room_overlap(
                zone_2, adjacent, barrier_distance_mm=200.0
            )
        )

    def test_barrier_not_required_when_gap_clears_threshold(self) -> None:
        zone_2 = self._zone_2_polygon()
        # Adjacent room 300 mm away — but vertex-to-vertex min distance is
        # larger; pick a clearly distant room.
        adjacent = [
            (15000.0, 15000.0),
            (16000.0, 15000.0),
            (16000.0, 16000.0),
            (15000.0, 16000.0),
        ]
        self.assertFalse(
            pool.check_changing_room_overlap(
                zone_2, adjacent, barrier_distance_mm=200.0
            )
        )

    def test_overlapping_polygons_trigger_barrier(self) -> None:
        zone_2 = self._zone_2_polygon()
        overlap = [
            (10000.0, 0.0),
            (13000.0, 0.0),
            (13000.0, 5000.0),
            (10000.0, 5000.0),
        ]
        self.assertTrue(pool.check_changing_room_overlap(zone_2, overlap))


if __name__ == "__main__":
    unittest.main()
