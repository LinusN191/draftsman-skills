"""Unit tests for §715 ELV barrier zone derivation."""

from __future__ import annotations

import pathlib
import sys
import unittest

_TESTS_DIR = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_TESTS_DIR))
from _bootstrap import elv  # noqa: E402


def _elv_anchor() -> dict:
    return {
        "type": "elv_lighting_circuit_anchor",
        "id": "elv_track_1",
        "position": {"x_mm": 1500.0, "y_mm": 1500.0, "z_floor_mm": 2400.0},
        "shape_kind": "rectangular",
        "dimensions": {"length_mm": 200.0, "width_mm": 200.0, "height_mm": 50.0},
    }


class TestElvBarrierZone(unittest.TestCase):
    def test_barrier_required_true(self) -> None:
        zone = elv.elv_barrier_zone(_elv_anchor())
        self.assertTrue(zone["barrier_required"])

    def test_label_required_true(self) -> None:
        zone = elv.elv_barrier_zone(_elv_anchor())
        self.assertTrue(zone["label_required"])

    def test_transformer_short_circuit_protected(self) -> None:
        zone = elv.elv_barrier_zone(_elv_anchor())
        self.assertTrue(zone["transformer_short_circuit_protected"])

    def test_citation_includes_61558_2_6(self) -> None:
        zone = elv.elv_barrier_zone(_elv_anchor())
        self.assertIn("61558-2-6", zone["_clause_citation"])

    def test_no_banned_715_subclause(self) -> None:
        zone = elv.elv_barrier_zone(_elv_anchor())
        for banned in ("§715.560", "§715.521", "§715.422"):
            self.assertNotIn(banned, zone["_clause_citation"])

    def test_polygon_scales_with_lv_spacing(self) -> None:
        small = elv.elv_barrier_zone(_elv_anchor(), lv_cable_spacing_mm_min=50.0)
        large = elv.elv_barrier_zone(_elv_anchor(), lv_cable_spacing_mm_min=300.0)
        small_xs = [p[0] for p in small["boundary_plan_polygon_mm"]]
        large_xs = [p[0] for p in large["boundary_plan_polygon_mm"]]
        self.assertLess(
            max(small_xs) - min(small_xs),
            max(large_xs) - min(large_xs),
        )

    def test_rejects_zero_spacing(self) -> None:
        with self.assertRaises(ValueError):
            elv.elv_barrier_zone(_elv_anchor(), lv_cable_spacing_mm_min=0.0)

    def test_zone_type_is_elv_barrier_zone(self) -> None:
        zone = elv.elv_barrier_zone(_elv_anchor())
        self.assertEqual(zone["zone_type"], "elv_barrier_zone")


if __name__ == "__main__":
    unittest.main()
