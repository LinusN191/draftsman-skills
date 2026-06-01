"""§703 sauna zone derivation (3 zones per the verified standards file).

The v1.0.1 correction realigns the library to the verified standards file
which specifies three sauna zones:
- zone_1: small footprint around the heater (high-temperature zone)
- zone_2: within the sauna room, away from the heater
- zone_3: above 1.5 m height for accessories (full room footprint)

Cables in zone_1 must be silicone-insulated for 170 C ambient. Light fittings
in zone_2 / zone_3 must be IPx4 minimum + T-rated to 125 C. RCD blanket per
§703.411.3.3 with the sauna heater circuit exempt.

Only the top-level §703 + §703.411.3.3 citations are valid per spec §3.2.
See the README verification-status policy for the full list of banned
brainstorm-era §703 sub-clauses.
"""

from __future__ import annotations

from typing import Any, Sequence

from .common import Point, Polygon, polygon_subtract, rectangular_zone

# §703 thresholds per verified standards file + spec §5.2
HEATER_PADDING_MM = 500.0  # rectangular footprint padded 500 mm around heater anchor
ZONE_3_HEIGHT_FLOOR_MM = 1500.0  # §703 Zone 3 starts above 1.5 m


def _heater_zone_1_footprint(heater_anchor: dict[str, Any]) -> Polygon:
    """Build the high-temperature footprint around the heater anchor.

    The verified standards file does not give an explicit dimension; the
    library uses HEATER_PADDING_MM (500 mm) around the heater anchor as the
    minimum-defensible footprint. Engineer overrides via
    ``zone_polygon_override[]`` per spec §4.5 when the heater is unusually
    large.
    """
    position = heater_anchor["position"]
    dimensions = heater_anchor.get("dimensions", {})
    centre: Point = (float(position["x_mm"]), float(position["y_mm"]))
    length_mm = float(dimensions.get("length_mm", 0.0)) + 2.0 * HEATER_PADDING_MM
    width_mm = float(dimensions.get("width_mm", 0.0)) + 2.0 * HEATER_PADDING_MM
    if length_mm <= 0:
        length_mm = 2.0 * HEATER_PADDING_MM
    if width_mm <= 0:
        width_mm = 2.0 * HEATER_PADDING_MM
    return rectangular_zone(centre, length_mm=length_mm, width_mm=width_mm)


def sauna_zone_1(heater_anchor: dict[str, Any]) -> dict[str, Any]:
    """§703 Zone 1 — around the heater (high-temperature zone).

    Cables in this zone must be silicone-insulated for 170 C ambient per the
    verified §703 key_requirements. 30 mA RCD is NOT required on the heater
    circuit itself per §703.411.3.3 (heater is exempt) — the IR emits this
    via the sibling ``rcd_blanket_by_room`` constraint with
    ``sauna_heater_excluded: true``.
    """
    polygon = _heater_zone_1_footprint(heater_anchor)
    position = heater_anchor["position"]
    dimensions = heater_anchor.get("dimensions", {})
    heater_top_z = float(position["z_floor_mm"]) + float(
        dimensions.get("height_mm", 1000.0)
    )

    return {
        "zone_type": "sauna_zone_1",
        "source_anchor_id": heater_anchor["id"],
        "derivation_clause": "BS 7671:2018 §703",
        "boundary_plan_polygon_mm": polygon,
        "height_min_mm": 0.0,
        "height_max_mm": heater_top_z,
        "ip_rating_min": "IPx4",
        "max_voltage_v": 230,
        "rcd_required_ma": None,  # heater exempt per §703.411.3.3
        "isolation_required": True,
        "allowed_equipment_classes": ["class_1"],
        "prohibited_fixture_types": [
            "luminaire_non_heat_rated",
            "cable_pvc_insulated",
            "socket_230v",
            "switch_230v",
        ],
        "switch_position_min_distance_mm": None,
        "overlapping_with_zone_ids": [],
        "_clause_citation": "BS 7671:2018 §703 + §703.411.3.3 (heater RCD-exempt)",
        "_derivation_note": (
            "Zone 1 footprint padded 500 mm around the heater anchor (verified "
            "§703 has no explicit dimension; this is a defensible minimum). "
            "Cables must be silicone-insulated for 170 C ambient per the "
            "verified §703 key_requirements; heater circuit RCD-exempt per "
            "§703.411.3.3."
        ),
    }


def sauna_zone_2(
    heater_anchor: dict[str, Any],
    sauna_room_polygon: Sequence[Point],
) -> dict[str, Any]:
    """§703 Zone 2 — within sauna room, away from heater.

    Computed as ``sauna_room_polygon - sauna_zone_1`` via
    ``common.polygon_subtract``. The reference implementation returns the
    sauna room polygon and registers the heater zone overlap via
    ``overlapping_with_zone_ids``; the runtime project hosts exact polygon
    subtraction for non-convex inner shapes.

    Light fittings in this zone must be IPx4 + T-rated to 125 C per the
    verified §703 key_requirements.
    """
    zone_1_polygon = _heater_zone_1_footprint(heater_anchor)
    room_polygon_list: Polygon = [(float(x), float(y)) for x, y in sauna_room_polygon]
    zone_2_polygon = polygon_subtract(room_polygon_list, zone_1_polygon)

    return {
        "zone_type": "sauna_zone_2",
        "source_anchor_id": heater_anchor["id"],
        "derivation_clause": "BS 7671:2018 §703",
        "boundary_plan_polygon_mm": zone_2_polygon,
        "height_min_mm": 0.0,
        "height_max_mm": ZONE_3_HEIGHT_FLOOR_MM,  # zone_2 sits below zone_3 floor
        "ip_rating_min": "IPx4",
        "max_voltage_v": 230,
        "rcd_required_ma": 30,
        "isolation_required": False,
        "allowed_equipment_classes": ["class_1", "class_2"],
        "prohibited_fixture_types": ["luminaire_non_T125_rated", "socket_230v"],
        "switch_position_min_distance_mm": None,
        "overlapping_with_zone_ids": ["sauna_zone_1"],
        "_clause_citation": "BS 7671:2018 §703 + §703.411.3.3 (30 mA RCD blanket)",
        "_derivation_note": (
            "Zone 2 = sauna room polygon minus Zone 1 footprint per spec §5.2 "
            "3-zone split. Reference library returns the full room polygon and "
            "registers the heater zone overlap; runtime project handles exact "
            "subtraction for non-convex inner shapes. Light fittings IPx4 + "
            "T125-rated per verified §703 key_requirements."
        ),
    }


def sauna_zone_3(
    sauna_room_polygon: Sequence[Point],
    ceiling_height_mm: float,
) -> dict[str, Any]:
    """§703 Zone 3 — above 1.5 m for accessories.

    height_min = 1500 mm; height_max = ceiling_height_mm. Plan polygon spans
    the full sauna room footprint per spec §5.2.
    """
    polygon: Polygon = [(float(x), float(y)) for x, y in sauna_room_polygon]

    return {
        "zone_type": "sauna_zone_3",
        "source_anchor_id": "sauna_room",
        "derivation_clause": "BS 7671:2018 §703",
        "boundary_plan_polygon_mm": polygon,
        "height_min_mm": ZONE_3_HEIGHT_FLOOR_MM,
        "height_max_mm": float(ceiling_height_mm),
        "ip_rating_min": "IPx4",
        "max_voltage_v": 230,
        "rcd_required_ma": 30,
        "isolation_required": False,
        "allowed_equipment_classes": ["class_1", "class_2"],
        "prohibited_fixture_types": ["luminaire_non_T125_rated"],
        "switch_position_min_distance_mm": None,
        "overlapping_with_zone_ids": [],
        "_clause_citation": "BS 7671:2018 §703 + §703.411.3.3 (30 mA RCD blanket)",
        "_derivation_note": (
            "Zone 3 = full sauna room footprint above 1.5 m AFF for accessories "
            "per spec §5.2 3-zone split. T125-rated luminaires required per "
            "verified §703 key_requirements."
        ),
    }
