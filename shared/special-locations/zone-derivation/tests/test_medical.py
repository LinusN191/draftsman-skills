"""Unit tests for §710 medical envelope derivation."""

from __future__ import annotations

import math
import pathlib
import sys
import unittest

_TESTS_DIR = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_TESTS_DIR))
from _bootstrap import medical  # noqa: E402


def _patient_position(group_anchor_id: str = "patient_1") -> dict:
    return {
        "x_mm": 3000.0,
        "y_mm": 3000.0,
        "z_floor_mm": 0.0,
        "anchor_id": group_anchor_id,
    }


class TestMedicalEnvelopeGroup0(unittest.TestCase):
    def test_group_0_zone_type(self) -> None:
        zone = medical.medical_envelope(
            _patient_position(), medical_group=0, ceiling_height_mm=2700.0
        )
        self.assertEqual(zone["zone_type"], "medical_envelope_group_0")

    def test_group_0_no_isolation_required(self) -> None:
        zone = medical.medical_envelope(
            _patient_position(), medical_group=0, ceiling_height_mm=2700.0
        )
        self.assertFalse(zone["isolation_required"])

    def test_group_0_height_capped_at_2500mm(self) -> None:
        zone = medical.medical_envelope(
            _patient_position(), medical_group=0, ceiling_height_mm=3000.0
        )
        self.assertEqual(zone["height_max_mm"], 2500.0)


class TestMedicalEnvelopeGroup1(unittest.TestCase):
    def test_group_1_zone_type(self) -> None:
        zone = medical.medical_envelope(
            _patient_position(), medical_group=1, ceiling_height_mm=2700.0
        )
        self.assertEqual(zone["zone_type"], "medical_envelope_group_1")

    def test_group_1_envelope_radius_is_1500mm(self) -> None:
        zone = medical.medical_envelope(
            _patient_position(), medical_group=1, ceiling_height_mm=2700.0
        )
        polygon = zone["boundary_plan_polygon_mm"]
        # Each vertex sits 1500 mm from the patient centre
        for x, y in polygon:
            distance = math.hypot(x - 3000.0, y - 3000.0)
            self.assertAlmostEqual(distance, 1500.0, places=4)

    def test_group_1_polygon_has_at_least_12_sides(self) -> None:
        zone = medical.medical_envelope(
            _patient_position(), medical_group=1, ceiling_height_mm=2700.0
        )
        self.assertGreaterEqual(len(zone["boundary_plan_polygon_mm"]), 12)


class TestMedicalEnvelopeGroup2(unittest.TestCase):
    def test_group_2_zone_type(self) -> None:
        zone = medical.medical_envelope(
            _patient_position(), medical_group=2, ceiling_height_mm=2700.0
        )
        self.assertEqual(zone["zone_type"], "medical_envelope_group_2")

    def test_group_2_rcd_is_null_per_verified_file(self) -> None:
        zone = medical.medical_envelope(
            _patient_position(), medical_group=2, ceiling_height_mm=2700.0
        )
        self.assertIsNone(zone["rcd_required_ma"])

    def test_group_2_citation_includes_61557_8_and_htm_06_01(self) -> None:
        zone = medical.medical_envelope(
            _patient_position(), medical_group=2, ceiling_height_mm=2700.0
        )
        self.assertIn("61557-8", zone["_clause_citation"])
        self.assertIn("HTM 06-01", zone["_clause_citation"])

    def test_group_2_isolation_required(self) -> None:
        zone = medical.medical_envelope(
            _patient_position(), medical_group=2, ceiling_height_mm=2700.0
        )
        self.assertTrue(zone["isolation_required"])


class TestMedicalEnvelopeValidation(unittest.TestCase):
    def test_invalid_group_raises(self) -> None:
        with self.assertRaises(ValueError):
            medical.medical_envelope(
                _patient_position(), medical_group=3, ceiling_height_mm=2700.0
            )

    def test_no_banned_710_subclause_in_emitted_citation(self) -> None:
        for group in (0, 1, 2):
            zone = medical.medical_envelope(
                _patient_position(), medical_group=group, ceiling_height_mm=2700.0
            )
            for banned in ("§710.413", "§710.314", "§710.411"):
                self.assertNotIn(banned, zone["_clause_citation"])

    def test_groups_differ_in_zone_type(self) -> None:
        zones = [
            medical.medical_envelope(
                _patient_position(), medical_group=g, ceiling_height_mm=2700.0
            )
            for g in (0, 1, 2)
        ]
        zone_types = {z["zone_type"] for z in zones}
        self.assertEqual(len(zone_types), 3)


if __name__ == "__main__":
    unittest.main()
