"""Unit tests for §701 bath zone derivation."""

from __future__ import annotations

import pathlib
import sys
import unittest

_TESTS_DIR = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_TESTS_DIR))
from _bootstrap import bath  # noqa: E402


def _standard_bath_anchor() -> dict:
    """1700 x 700 x 500 standard bath at room origin."""
    return {
        "type": "bath_basin",
        "id": "bath_1",
        "position": {"x_mm": 850.0, "y_mm": 350.0, "z_floor_mm": 0.0},
        "dimensions": {"length_mm": 1700.0, "width_mm": 700.0, "height_mm": 500.0},
        "shape_kind": "rectangular",
        "bath_kind": "standard",
    }


def _room_polygon_3000_2500() -> list[tuple[float, float]]:
    return [(0.0, 0.0), (3000.0, 0.0), (3000.0, 2500.0), (0.0, 2500.0)]


class TestBathZone0(unittest.TestCase):
    def test_zone_0_polygon_matches_basin_footprint(self) -> None:
        anchor = _standard_bath_anchor()
        zone = bath.bath_zone_0(anchor)
        self.assertEqual(zone["zone_type"], "bath_zone_0")
        self.assertEqual(len(zone["boundary_plan_polygon_mm"]), 4)
        # Basin area = 1700 * 700 = 1,190,000 mm^2
        xs = [p[0] for p in zone["boundary_plan_polygon_mm"]]
        ys = [p[1] for p in zone["boundary_plan_polygon_mm"]]
        self.assertAlmostEqual(max(xs) - min(xs), 1700.0)
        self.assertAlmostEqual(max(ys) - min(ys), 700.0)

    def test_zone_0_is_selv_only(self) -> None:
        zone = bath.bath_zone_0(_standard_bath_anchor())
        self.assertEqual(zone["max_voltage_v"], 12)
        self.assertEqual(zone["ip_rating_min"], "IPx7")

    def test_zone_0_height_bounded_by_basin_rim(self) -> None:
        zone = bath.bath_zone_0(_standard_bath_anchor())
        self.assertEqual(zone["height_min_mm"], 0.0)
        self.assertEqual(zone["height_max_mm"], 500.0)


class TestBathZone1(unittest.TestCase):
    def test_zone_1_default_height_is_2250(self) -> None:
        zone = bath.bath_zone_1(_standard_bath_anchor(), room_ceiling_mm=2400.0)
        self.assertEqual(zone["height_max_mm"], 2250.0)
        self.assertEqual(zone["ip_rating_min"], "IPx4")

    def test_zone_1_takes_higher_of_shower_head(self) -> None:
        zone = bath.bath_zone_1(
            _standard_bath_anchor(),
            room_ceiling_mm=2700.0,
            shower_head_height_mm=2350.0,
        )
        self.assertEqual(zone["height_max_mm"], 2350.0)

    def test_zone_1_capped_by_ceiling(self) -> None:
        zone = bath.bath_zone_1(_standard_bath_anchor(), room_ceiling_mm=2100.0)
        # Even though default is 2250, ceiling caps it
        self.assertEqual(zone["height_max_mm"], 2100.0)

    def test_wet_room_expansion_fills_room_polygon(self) -> None:
        zone = bath.bath_zone_1(
            _standard_bath_anchor(),
            room_ceiling_mm=2400.0,
            is_wet_room=True,
            room_polygon_mm=_room_polygon_3000_2500(),
        )
        xs = [p[0] for p in zone["boundary_plan_polygon_mm"]]
        ys = [p[1] for p in zone["boundary_plan_polygon_mm"]]
        self.assertAlmostEqual(max(xs) - min(xs), 3000.0)
        self.assertAlmostEqual(max(ys) - min(ys), 2500.0)

    def test_wet_room_requires_room_polygon(self) -> None:
        with self.assertRaises(ValueError):
            bath.bath_zone_1(
                _standard_bath_anchor(),
                room_ceiling_mm=2400.0,
                is_wet_room=True,
            )


class TestBathZone2(unittest.TestCase):
    def test_zone_2_extends_600mm_horizontally(self) -> None:
        zone = bath.bath_zone_2(_standard_bath_anchor())
        xs = [p[0] for p in zone["boundary_plan_polygon_mm"]]
        ys = [p[1] for p in zone["boundary_plan_polygon_mm"]]
        # Bath spans 0..1700 x 0..700; Zone 2 expands 600mm each side
        self.assertAlmostEqual(max(xs) - min(xs), 1700.0 + 2 * 600.0)
        self.assertAlmostEqual(max(ys) - min(ys), 700.0 + 2 * 600.0)

    def test_zone_2_socket_distance_is_3m(self) -> None:
        zone = bath.bath_zone_2(_standard_bath_anchor())
        self.assertEqual(zone["switch_position_min_distance_mm"], 3000.0)

    def test_zone_2_citation_includes_701_512_3(self) -> None:
        zone = bath.bath_zone_2(_standard_bath_anchor())
        self.assertIn("701.512.3", zone["_clause_citation"])


class TestWhirlpoolPumpDefault(unittest.TestCase):
    def test_default_position_flagged_as_assumption(self) -> None:
        pump = bath.whirlpool_pump_position_default(_standard_bath_anchor())
        self.assertTrue(pump["_assumption_default_placement"])

    def test_default_position_on_long_side(self) -> None:
        pump = bath.whirlpool_pump_position_default(_standard_bath_anchor())
        # Long-side midpoint: x = 850 (bath centre), y = 350 + 350 = 700
        self.assertAlmostEqual(pump["x_mm"], 850.0)
        self.assertAlmostEqual(pump["y_mm"], 700.0)

    def test_default_citation_includes_701_512_2(self) -> None:
        pump = bath.whirlpool_pump_position_default(_standard_bath_anchor())
        self.assertIn("701.512.2", pump["_citation"])


if __name__ == "__main__":
    unittest.main()
