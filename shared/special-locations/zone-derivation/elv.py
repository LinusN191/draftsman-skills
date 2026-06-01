"""§715 extra-low-voltage lighting barrier-zone derivation.

Verified against shared/standards/electrical/BS7671/part7-special-locations.json
section_715_extra_low_voltage_lighting. Only the top-level §715 citation +
cross-reference BS EN 61558-2-6 (transformer short-circuit protection) are
emitted per spec §3.2.

See the README verification-status policy for the full list of banned
brainstorm-era §715 sub-clauses.
"""

from __future__ import annotations

from typing import Any

from .common import Point, Polygon, rectangular_zone

# §715 default LV cable spacing per spec §5.3 elv_separation constraint
DEFAULT_LV_CABLE_SPACING_MM = 100.0
DEFAULT_BARRIER_FOOTPRINT_MM = 600.0  # defensible barrier footprint size


def elv_barrier_zone(
    elv_anchor: dict[str, Any],
    lv_cable_spacing_mm_min: float = DEFAULT_LV_CABLE_SPACING_MM,
) -> dict[str, Any]:
    """§715 ELV barrier zone.

    Builds a rectangular barrier footprint centred on the ELV anchor with
    side length = 2 * (DEFAULT_BARRIER_FOOTPRINT_MM + lv_cable_spacing_mm_min)
    so the barrier physically separates ELV cabling from LV cabling at the
    spec-defined spacing. Caller emits a sibling ``elv_separation`` constraint
    with the matching spacing.

    Returns:
        Zone dict with:
        - ``zone_type``: ``elv_barrier_zone``
        - ``barrier_required``: True
        - ``label_required``: True
        - ``transformer_short_circuit_protected``: True (per BS EN 61558-2-6)
    """
    if lv_cable_spacing_mm_min <= 0:
        raise ValueError("lv_cable_spacing_mm_min must be positive")

    position = elv_anchor["position"]
    centre: Point = (float(position["x_mm"]), float(position["y_mm"]))
    side_mm = 2.0 * (DEFAULT_BARRIER_FOOTPRINT_MM + float(lv_cable_spacing_mm_min))
    polygon: Polygon = rectangular_zone(centre, length_mm=side_mm, width_mm=side_mm)

    return {
        "zone_type": "elv_barrier_zone",
        "source_anchor_id": elv_anchor["id"],
        "derivation_clause": "BS 7671:2018 §715",
        "boundary_plan_polygon_mm": polygon,
        "height_min_mm": 0.0,
        "height_max_mm": float(position.get("z_floor_mm", 0.0)) + 2500.0,
        "ip_rating_min": "IPx4",
        "max_voltage_v": 50,  # ELV upper bound per BS 7671 §414
        "rcd_required_ma": None,
        "isolation_required": True,
        "allowed_equipment_classes": ["class_3_SELV"],
        "prohibited_fixture_types": ["lv_cable_without_barrier"],
        "switch_position_min_distance_mm": None,
        "overlapping_with_zone_ids": [],
        "_clause_citation": "BS 7671:2018 §715 + BS EN 61558-2-6 (transformer SC protection)",
        "_derivation_note": (
            "ELV barrier zone padded by the spec-defined LV cable spacing "
            "around the ELV anchor; sibling elv_separation constraint emits "
            "barrier_required + label_required + "
            "transformer_short_circuit_protected per BS EN 61558-2-6. No §715 "
            "sub-clauses exist in the verified standards file; generic §715 + "
            "cross-reference standard applies."
        ),
        "barrier_required": True,
        "label_required": True,
        "transformer_short_circuit_protected": True,
    }
