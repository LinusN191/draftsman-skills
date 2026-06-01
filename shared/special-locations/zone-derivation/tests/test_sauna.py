"""Unit tests for §703 sauna 3-zone derivation."""

from __future__ import annotations

import pathlib
import sys
import unittest

_TESTS_DIR = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_TESTS_DIR))
from _bootstrap import common, sauna  # noqa: E402


def _heater_anchor() -> dict:
    """500 x 500 x 1000 mm heater near a corner of the sauna room."""
    return {
        "type": "sauna_heater",
        "id": "heater_1",
        "position": {"x_mm": 400.0, "y_mm": 400.0, "z_floor_mm": 0.0},
        "dimensions": {"length_mm": 500.0, "width_mm": 500.0, "height_mm": 1000.0},
        "shape_kind": "rectangular",
    }


def _sauna_room_polygon() -> list[tuple[float, float]]:
    """2400 x 2000 sauna room footprint."""
    return [(0.0, 0.0), (2400.0, 0.0), (2400.0, 2000.0), (0.0, 2000.0)]


SAUNA_ROOM_AREA = 2400.0 * 2000.0


class TestSaunaZone1(unittest.TestCase):
    def test_zone_1_padded_500mm_around_heater(self) -> None:
        zone = sauna.sauna_zone_1(_heater_anchor())
        xs = [p[0] for p in zone["boundary_plan_polygon_mm"]]
        ys = [p[1] for p in zone["boundary_plan_polygon_mm"]]
        # Heater 500x500 + 500 padding each side = 1500x1500
        self.assertAlmostEqual(max(xs) - min(xs), 1500.0)
        self.assertAlmostEqual(max(ys) - min(ys), 1500.0)

    def test_zone_1_rcd_exempt_per_703_411_3_3(self) -> None:
        zone = sauna.sauna_zone_1(_heater_anchor())
        self.assertIsNone(zone["rcd_required_ma"])
        self.assertIn("703.411.3.3", zone["_clause_citation"])

    def test_zone_1_prohibits_pvc_cable(self) -> None:
        zone = sauna.sauna_zone_1(_heater_anchor())
        self.assertIn("cable_pvc_insulated", zone["prohibited_fixture_types"])


class TestSaunaZone2(unittest.TestCase):
    def test_zone_2_registers_heater_overlap(self) -> None:
        zone = sauna.sauna_zone_2(_heater_anchor(), _sauna_room_polygon())
        self.assertIn("sauna_zone_1", zone["overlapping_with_zone_ids"])

    def test_zone_2_rcd_blanket_30ma(self) -> None:
        zone = sauna.sauna_zone_2(_heater_anchor(), _sauna_room_polygon())
        self.assertEqual(zone["rcd_required_ma"], 30)

    def test_zone_2_polygon_area_equals_sauna_room(self) -> None:
        # Reference impl returns the outer polygon; runtime project does exact
        # subtraction. The documented invariant: outer polygon area >= zone_1
        # polygon area (heater inside room).
        zone_2 = sauna.sauna_zone_2(_heater_anchor(), _sauna_room_polygon())
        zone_1 = sauna.sauna_zone_1(_heater_anchor())
        area_2 = common.polygon_area_mm2(zone_2["boundary_plan_polygon_mm"])
        area_1 = common.polygon_area_mm2(zone_1["boundary_plan_polygon_mm"])
        self.assertGreater(area_2, area_1)
        # Outer polygon area matches the sauna room area
        self.assertAlmostEqual(area_2, SAUNA_ROOM_AREA)


class TestSaunaZone3(unittest.TestCase):
    def test_zone_3_starts_at_1500mm(self) -> None:
        zone = sauna.sauna_zone_3(_sauna_room_polygon(), ceiling_height_mm=2100.0)
        self.assertEqual(zone["height_min_mm"], 1500.0)
        self.assertEqual(zone["height_max_mm"], 2100.0)

    def test_zone_3_polygon_matches_full_room(self) -> None:
        zone = sauna.sauna_zone_3(_sauna_room_polygon(), ceiling_height_mm=2100.0)
        area = common.polygon_area_mm2(zone["boundary_plan_polygon_mm"])
        self.assertAlmostEqual(area, SAUNA_ROOM_AREA)

    def test_zone_3_rcd_blanket_30ma(self) -> None:
        zone = sauna.sauna_zone_3(_sauna_room_polygon(), ceiling_height_mm=2100.0)
        self.assertEqual(zone["rcd_required_ma"], 30)


class TestSauna3ZoneSplit(unittest.TestCase):
    def test_three_zones_emit_three_zone_types(self) -> None:
        zone_1 = sauna.sauna_zone_1(_heater_anchor())
        zone_2 = sauna.sauna_zone_2(_heater_anchor(), _sauna_room_polygon())
        zone_3 = sauna.sauna_zone_3(_sauna_room_polygon(), ceiling_height_mm=2100.0)
        self.assertEqual(zone_1["zone_type"], "sauna_zone_1")
        self.assertEqual(zone_2["zone_type"], "sauna_zone_2")
        self.assertEqual(zone_3["zone_type"], "sauna_zone_3")

    def test_no_banned_703_citation_in_emitted_clauses(self) -> None:
        anchor = _heater_anchor()
        room = _sauna_room_polygon()
        for zone in (
            sauna.sauna_zone_1(anchor),
            sauna.sauna_zone_2(anchor, room),
            sauna.sauna_zone_3(room, ceiling_height_mm=2100.0),
        ):
            for banned in ("§703.55", "§703.512", "§703.413"):
                self.assertNotIn(banned, zone["_clause_citation"])

    def test_zone_2_height_max_aligns_with_zone_3_floor(self) -> None:
        anchor = _heater_anchor()
        room = _sauna_room_polygon()
        zone_2 = sauna.sauna_zone_2(anchor, room)
        zone_3 = sauna.sauna_zone_3(room, ceiling_height_mm=2100.0)
        self.assertEqual(zone_2["height_max_mm"], zone_3["height_min_mm"])


if __name__ == "__main__":
    unittest.main()
