"""§710 medical envelope derivation (Group 0 / 1 / 2).

Verified against shared/standards/electrical/BS7671/part7-special-locations.json
section_710_medical_locations. Only top-level §710 is emitted (per spec §3.2
cross-reference table) — no §710 sub-clauses exist in the verified file. The
medical IT system depth comes from cross-reference standards BS EN 61557-8
(IMD with 8 s alarm response, NOT 0.5 s — that prior misattribution is now
corrected) and HTM 06-01.

See the README verification-status policy for the full list of banned
brainstorm-era §710 sub-clauses.
"""

from __future__ import annotations

from typing import Any

from .common import Point, Polygon, cylinder_to_polygon

# §710 envelope radius per spec §5.2 + verified file body
PATIENT_ENVELOPE_RADIUS_MM = 1500.0
PATIENT_ENVELOPE_HEIGHT_MAX_MM = 2500.0


def _envelope_polygon(patient_position: dict[str, Any]) -> Polygon:
    """Build a 1.5 m radius cylindrical envelope around the patient position."""
    centre: Point = (
        float(patient_position["x_mm"]),
        float(patient_position["y_mm"]),
    )
    return cylinder_to_polygon(centre, PATIENT_ENVELOPE_RADIUS_MM)


def medical_envelope(
    patient_position: dict[str, Any],
    medical_group: int,
    ceiling_height_mm: float,
) -> dict[str, Any]:
    """§710 medical envelope.

    1.5 m radius cylindrical envelope around the patient position
    (approximated as a >=12-sided polygon), height bound by floor (0) and
    the lesser of the room ceiling and the §710 envelope max (2500 mm).

    Per Group:
    - Group 0: standard supply (TN-S / TN-C-S); no constraint emission needed.
    - Group 1: requires sibling ``supplementary_equipotential_bonding``
      constraint (caller responsibility).
    - Group 2: MANDATORY medical IT system + IMD (8 s alarm response per
      BS EN 61557-8) emitted as a sibling ``medical_it_system`` constraint.
      Returned zone carries ``zone_type: medical_envelope_group_2`` as the
      schema discriminator that the IR validator pairs with the constraint.

    Args:
        patient_position: {x_mm, y_mm, z_floor_mm} room-local coords.
        medical_group: 0, 1, or 2.
        ceiling_height_mm: room ceiling AFF.

    Returns:
        Zone dict matching the IR schema. Side-effect responsibilities (emit
        IT system + bonding constraints) are documented in
        electrical/special-locations/prompts/generator.md and enforced at the
        IR-schema allOf branch.
    """
    if medical_group not in (0, 1, 2):
        raise ValueError(f"medical_group must be 0, 1, or 2; got {medical_group}")

    polygon = _envelope_polygon(patient_position)
    height_max = min(
        float(ceiling_height_mm), PATIENT_ENVELOPE_HEIGHT_MAX_MM
    )
    zone_type = f"medical_envelope_group_{medical_group}"

    if medical_group == 0:
        ip_rating = "IPx0"
        rcd = 30  # general RCD per verified file Group 0 body
        prohibited: list[str] = []
        derivation_note = (
            "Group 0: medical location with no medical electrical equipment in "
            "patient contact (consulting / general clinical). Standard TN-S or "
            "TN-C-S supply; 30 mA RCD per general BS 7671 requirements. No "
            "medical IT system; no supplementary bonding requirement beyond "
            "general §544."
        )
        clause = "BS 7671:2018 §710 (Group 0)"
    elif medical_group == 1:
        ip_rating = "IPx0"
        rcd = 30
        prohibited = []
        derivation_note = (
            "Group 1: short-term patient contact (examination, recovery, "
            "dialysis). TN-S preferred; 30 mA RCD on socket outlets; "
            "supplementary equipotential bonding within patient environment "
            "emitted as a sibling constraint. Reference: verified §710 file "
            "body; cross-ref BS EN 60601 series for the equipment standard."
        )
        clause = "BS 7671:2018 §710 (Group 1)"
    else:
        # Group 2 — surgical / life-supporting / ICU
        ip_rating = "IPx0"
        rcd = None  # NO RCDs on patient-essential equipment per verified file
        prohibited = [
            "rcd_on_patient_essential_circuit",
            "shared_circuit_with_non_medical_load",
        ]
        derivation_note = (
            "Group 2: surgical / life-supporting / ICU. Medical IT system "
            "(IT-M) with isolating transformer + insulation monitoring device "
            "(BS EN 61557-8, 8 s alarm response — NOT 0.5 s as in earlier "
            "drafts). NO RCDs on patient-essential equipment (a trip during "
            "surgery is unacceptable). Supplementary bonding mandatory + "
            "extensive; max 0.2 ohm to any point per verified §710 body. NHS "
            "sites: HTM 06-01 takes precedence."
        )
        clause = (
            "BS 7671:2018 §710 (Group 2) + BS EN 61557-8 (IMD 8 s alarm) "
            "+ HTM 06-01 (NHS precedence)"
        )

    return {
        "zone_type": zone_type,
        "source_anchor_id": patient_position.get("anchor_id", "medical_patient"),
        "derivation_clause": "BS 7671:2018 §710",
        "boundary_plan_polygon_mm": polygon,
        "height_min_mm": 0.0,
        "height_max_mm": height_max,
        "ip_rating_min": ip_rating,
        "max_voltage_v": 230,
        "rcd_required_ma": rcd,
        "isolation_required": medical_group == 2,
        "allowed_equipment_classes": ["class_1", "class_2"],
        "prohibited_fixture_types": prohibited,
        "switch_position_min_distance_mm": None,
        "overlapping_with_zone_ids": [],
        "_clause_citation": clause,
        "_derivation_note": derivation_note,
    }
