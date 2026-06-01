"""§701 bath/shower-room zone derivation (3 zones + whirlpool default).

Verified against shared/standards/electrical/BS7671/part7-special-locations.json
section_701_bathrooms_and_shower_rooms. Only top-level §701 + the verified
sub-clauses on the spec §3.2 cross-reference table are emitted.
"""

from __future__ import annotations

from typing import Any

from .common import (
    Point,
    Polygon,
    expand_polygon_horizontally,
    rectangular_zone,
)

# §701 thresholds per verified standards file
ZONE_1_DEFAULT_HEIGHT_MM = 2250.0  # §701 Zone 1: above Zone 0 to 2.25 m or higher of shower head
ZONE_2_HORIZONTAL_EXTENSION_MM = 600.0  # §701 Zone 2: 0.6 m horizontal extension


def _bath_footprint(bath_anchor: dict[str, Any]) -> Polygon:
    """Build the bath basin plan polygon from anchor position + dimensions."""
    position = bath_anchor["position"]
    dimensions = bath_anchor["dimensions"]
    centre: Point = (float(position["x_mm"]), float(position["y_mm"]))
    return rectangular_zone(
        centre,
        length_mm=float(dimensions["length_mm"]),
        width_mm=float(dimensions["width_mm"]),
    )


def bath_zone_0(bath_anchor: dict[str, Any]) -> dict[str, Any]:
    """§701 Zone 0 — inside the basin volume.

    height_min = 0 (basin bottom at floor finish reference)
    height_max = basin top z = position.z_floor_mm + dimensions.height_mm

    IPx7 + SELV <=12 V only per BS 7671:2018 §701.414.4.5.
    """
    polygon = _bath_footprint(bath_anchor)
    position = bath_anchor["position"]
    dimensions = bath_anchor["dimensions"]
    basin_top_z = float(position["z_floor_mm"]) + float(dimensions["height_mm"])

    return {
        "zone_type": "bath_zone_0",
        "source_anchor_id": bath_anchor["id"],
        "derivation_clause": "BS 7671:2018 §701",
        "boundary_plan_polygon_mm": polygon,
        "height_min_mm": 0.0,
        "height_max_mm": basin_top_z,
        "ip_rating_min": "IPx7",
        "max_voltage_v": 12,
        "rcd_required_ma": 30,
        "isolation_required": True,
        "allowed_equipment_classes": ["class_3_SELV"],
        "prohibited_fixture_types": [
            "socket_230v",
            "switch_230v",
            "luminaire_non_ip_rated",
        ],
        "switch_position_min_distance_mm": None,
        "overlapping_with_zone_ids": [],
        "_clause_citation": "BS 7671:2018 §701 + §701.414.4.5 (SELV <=12 V in Zone 0)",
        "_derivation_note": (
            "Zone 0 footprint matches bath basin plan rectangle; height bound by "
            "basin rim. SELV-only per §701.414.4.5; IPx7 ingress per §701 zone "
            "table. Derived from anchor dimensions; no manufacturer-specific data."
        ),
    }


def bath_zone_1(
    bath_anchor: dict[str, Any],
    room_ceiling_mm: float,
    is_wet_room: bool = False,
    shower_head_height_mm: float | None = None,
    room_polygon_mm: list[Point] | None = None,
) -> dict[str, Any]:
    """§701 Zone 1 — above Zone 0 to max(2250 mm, shower head height).

    When ``is_wet_room`` is True, the polygon expands to the full room floor
    area per IET GN7 wet-room commentary. The verified standards file does NOT
    contain a §701 sub-clause for wet rooms, so the generic §701 citation
    applies.
    """
    if is_wet_room:
        if room_polygon_mm is None:
            raise ValueError(
                "is_wet_room=True requires room_polygon_mm for full-floor expansion"
            )
        polygon: Polygon = [(float(x), float(y)) for x, y in room_polygon_mm]
        derivation_note = (
            "Wet-room expansion: Zone 1 plan polygon spans the full room floor "
            "area per IET GN7 wet-room commentary. No §701 sub-clause exists in "
            "the verified standards file for wet rooms; generic §701 citation "
            "applies. Height = max(2250 mm, shower head height)."
        )
    else:
        polygon = _bath_footprint(bath_anchor)
        derivation_note = (
            "Zone 1 plan polygon matches Zone 0 footprint (above the bath basin). "
            "Height bounded below by basin top, above by max(2250 mm, shower head "
            "height). IPx4 minimum per §701 zone table."
        )

    height_max = ZONE_1_DEFAULT_HEIGHT_MM
    if shower_head_height_mm is not None:
        height_max = max(ZONE_1_DEFAULT_HEIGHT_MM, float(shower_head_height_mm))
    height_max = min(height_max, float(room_ceiling_mm))

    position = bath_anchor["position"]
    dimensions = bath_anchor["dimensions"]
    basin_top_z = float(position["z_floor_mm"]) + float(dimensions["height_mm"])

    return {
        "zone_type": "bath_zone_1",
        "source_anchor_id": bath_anchor["id"],
        "derivation_clause": "BS 7671:2018 §701",
        "boundary_plan_polygon_mm": polygon,
        "height_min_mm": basin_top_z,
        "height_max_mm": height_max,
        "ip_rating_min": "IPx4",
        "max_voltage_v": 230,
        "rcd_required_ma": 30,
        "isolation_required": False,
        "allowed_equipment_classes": ["class_1", "class_2", "class_3_SELV"],
        "prohibited_fixture_types": ["socket_230v"],
        "switch_position_min_distance_mm": None,
        "overlapping_with_zone_ids": [],
        "_clause_citation": "BS 7671:2018 §701",
        "_derivation_note": derivation_note,
    }


def bath_zone_2(
    bath_anchor: dict[str, Any],
    room_polygon_mm: list[Point] | None = None,
) -> dict[str, Any]:
    """§701 Zone 2 — 0.6 m horizontal extension beyond Zone 1.

    Socket outlets must be >=3 m from the Zone 1 boundary per BS 7671:2018
    §701.512.3.
    """
    bath_footprint = _bath_footprint(bath_anchor)
    expanded = expand_polygon_horizontally(
        bath_footprint, ZONE_2_HORIZONTAL_EXTENSION_MM
    )

    return {
        "zone_type": "bath_zone_2",
        "source_anchor_id": bath_anchor["id"],
        "derivation_clause": "BS 7671:2018 §701",
        "boundary_plan_polygon_mm": expanded,
        "height_min_mm": 0.0,
        "height_max_mm": ZONE_1_DEFAULT_HEIGHT_MM,
        "ip_rating_min": "IPx4",
        "max_voltage_v": 230,
        "rcd_required_ma": 30,
        "isolation_required": False,
        "allowed_equipment_classes": ["class_1", "class_2", "class_3_SELV"],
        "prohibited_fixture_types": ["socket_230v_within_3m_of_zone_1"],
        "switch_position_min_distance_mm": 3000.0,
        "overlapping_with_zone_ids": [],
        "_clause_citation": "BS 7671:2018 §701 + §701.512.3 (sockets >=3 m from Zone 1)",
        "_derivation_note": (
            "Zone 2 expands 600 mm horizontally beyond the bath footprint per the "
            "verified §701 zone table. Socket outlets prohibited within 3 m of "
            "Zone 1 boundary per §701.512.3. Height bound matches Zone 1 default."
        ),
    }


def whirlpool_pump_position_default(bath_anchor: dict[str, Any]) -> dict[str, Any]:
    """Default whirlpool pump position to bath edge midpoint (long-side centre).

    Triggered when an anchor with ``bath_kind == 'whirlpool'`` lacks an
    explicit ``whirlpool_pump_position``. Flags the placement as an
    assumption so reviewer D-3 can challenge it.
    """
    position = bath_anchor["position"]
    dimensions = bath_anchor["dimensions"]
    centre_x = float(position["x_mm"])
    centre_y = float(position["y_mm"])
    width_mm = float(dimensions["width_mm"])

    # Long-side midpoint: offset along +y axis by half the width
    pump_x = centre_x
    pump_y = centre_y + width_mm / 2.0
    pump_z = float(position["z_floor_mm"])

    return {
        "x_mm": pump_x,
        "y_mm": pump_y,
        "z_mm": pump_z,
        "_assumption_default_placement": True,
        "_citation": (
            "BS 7671:2018 §701 + §701.512.2 (IPx5 where water jets used)"
        ),
    }
