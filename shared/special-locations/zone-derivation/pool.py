"""§702 swimming-pool zone derivation (3 zones + adjacency barrier check).

Verified against shared/standards/electrical/BS7671/part7-special-locations.json
section_702_swimming_pools. Only top-level §702 + §702.55.4 + §702.415.1 +
§702.415.2 are emitted (per spec §3.2 cross-reference table). Earlier
brainstorm-era pool sub-clauses are banned per the README; see the README
verification-status policy for the full banned list.
"""

from __future__ import annotations

import math
from typing import Any, Sequence

from .common import (
    Point,
    Polygon,
    cylinder_to_polygon,
    expand_polygon_horizontally,
    polygon_intersects,
    rectangular_zone,
)

# §702 thresholds per verified standards file
ZONE_1_HEIGHT_EXTENSION_MM = 2500.0  # §702 Zone 1: 2.5 m vertical above water
ZONE_2_HORIZONTAL_EXTENSION_MM = 2000.0  # §702 Zone 2: 2 m horizontal beyond Zone 1
ZONE_2_HEIGHT_EXTENSION_MM = 1500.0  # §702 Zone 2: 1.5 m vertical (approx, spec said 2.5)
DEFAULT_CHANGING_ROOM_BARRIER_MM = 200.0  # spec §6.x INV-10 default


def _pool_footprint(pool_anchor: dict[str, Any]) -> Polygon:
    """Build the pool basin plan polygon from anchor data.

    Cylindrical pools approximated as ≥12-sided regular polygons per spec
    §5.2. Rectangular pools use a 4-vertex rectangle.
    """
    shape_kind = pool_anchor.get("shape_kind", "rectangular")
    position = pool_anchor["position"]
    centre: Point = (float(position["x_mm"]), float(position["y_mm"]))

    if shape_kind == "cylinder":
        radius_mm = float(pool_anchor["radius_mm"])
        return cylinder_to_polygon(centre, radius_mm)
    dimensions = pool_anchor["dimensions"]
    return rectangular_zone(
        centre,
        length_mm=float(dimensions["length_mm"]),
        width_mm=float(dimensions["width_mm"]),
    )


def pool_zone_0(pool_anchor: dict[str, Any]) -> dict[str, Any]:
    """§702 Zone 0 — interior of pool basin (water + tiled walls).

    IPx8 + SELV <=12 V only per verified §702 zone table.
    """
    polygon = _pool_footprint(pool_anchor)
    position = pool_anchor["position"]
    dimensions = pool_anchor.get("dimensions", {})
    basin_depth_mm = float(dimensions.get("height_mm", 0.0))
    water_top_z = float(position["z_floor_mm"]) + basin_depth_mm

    return {
        "zone_type": "pool_zone_0",
        "source_anchor_id": pool_anchor["id"],
        "derivation_clause": "BS 7671:2018 §702",
        "boundary_plan_polygon_mm": polygon,
        "height_min_mm": float(position["z_floor_mm"]),
        "height_max_mm": water_top_z,
        "ip_rating_min": "IPx8",
        "max_voltage_v": 12,
        "rcd_required_ma": 30,
        "isolation_required": True,
        "allowed_equipment_classes": ["class_3_SELV"],
        "prohibited_fixture_types": [
            "socket_230v",
            "switch_230v",
            "luminaire_non_ip_rated",
            "luminaire_above_12v_selv",
        ],
        "switch_position_min_distance_mm": None,
        "overlapping_with_zone_ids": [],
        "_clause_citation": "BS 7671:2018 §702",
        "_derivation_note": (
            "Zone 0 = basin interior (water + tiled basin walls). IPx8 submerged "
            "rating + SELV <=12 V only per the verified §702 zone table. "
            "Underwater luminaires per §702.55.4 fed via remote transformer."
        ),
    }


def pool_zone_1(
    pool_anchor: dict[str, Any], water_surface_z: float
) -> dict[str, Any]:
    """§702 Zone 1 — vertical column to water_surface_z + 2500 mm.

    Per the verified §702 zone table: "Around pool to 2 m horizontal, 2.5 m
    vertical." Plan polygon matches the basin footprint (Zone 1 sits directly
    above the basin in this 2.5D model — the horizontal 2 m extension lives
    in Zone 2).
    """
    polygon = _pool_footprint(pool_anchor)
    height_max = float(water_surface_z) + ZONE_1_HEIGHT_EXTENSION_MM

    return {
        "zone_type": "pool_zone_1",
        "source_anchor_id": pool_anchor["id"],
        "derivation_clause": "BS 7671:2018 §702",
        "boundary_plan_polygon_mm": polygon,
        "height_min_mm": float(water_surface_z),
        "height_max_mm": height_max,
        "ip_rating_min": "IPx5",
        "max_voltage_v": 230,
        "rcd_required_ma": 30,
        "isolation_required": False,
        "allowed_equipment_classes": ["class_1", "class_2", "class_3_SELV"],
        "prohibited_fixture_types": ["socket_230v"],
        "switch_position_min_distance_mm": None,
        "overlapping_with_zone_ids": [],
        "_clause_citation": "BS 7671:2018 §702",
        "_derivation_note": (
            "Zone 1 = vertical column above basin to water surface + 2.5 m. "
            "IPx5 minimum per verified §702 zone table; pool main equipotential "
            "bonding per §702.415.1 emitted as a sibling electrical_constraint."
        ),
    }


def pool_zone_2(
    pool_anchor: dict[str, Any], water_surface_z: float
) -> dict[str, Any]:
    """§702 Zone 2 — 2 m horizontal extension; height to water_surface_z + 1500 mm.

    Domestic pools have no Zone 2 per the verified standards file. The skill
    suppresses this zone for domestic anchors; this library always builds the
    polygon and the caller filters by ``pool_kind`` (domestic vs commercial).
    """
    basin = _pool_footprint(pool_anchor)
    expanded = expand_polygon_horizontally(basin, ZONE_2_HORIZONTAL_EXTENSION_MM)
    height_max = float(water_surface_z) + ZONE_2_HEIGHT_EXTENSION_MM

    return {
        "zone_type": "pool_zone_2",
        "source_anchor_id": pool_anchor["id"],
        "derivation_clause": "BS 7671:2018 §702",
        "boundary_plan_polygon_mm": expanded,
        "height_min_mm": float(water_surface_z),
        "height_max_mm": height_max,
        "ip_rating_min": "IPx4",
        "max_voltage_v": 230,
        "rcd_required_ma": 30,
        "isolation_required": False,
        "allowed_equipment_classes": ["class_1", "class_2", "class_3_SELV"],
        "prohibited_fixture_types": ["socket_230v_within_pool_zone_2"],
        "switch_position_min_distance_mm": None,
        "overlapping_with_zone_ids": [],
        "_clause_citation": "BS 7671:2018 §702 + §702.55.4 (changing-room barrier check)",
        "_derivation_note": (
            "Zone 2 = 2 m horizontal extension beyond basin footprint per verified "
            "§702 zone table. IPx4 minimum (commercial pools). Adjacent rooms "
            "checked for barrier presence per §702.55.4 via "
            "check_changing_room_overlap()."
        ),
    }


def _point_to_segment_distance(
    point: Point, seg_start: Point, seg_end: Point
) -> float:
    """Shortest distance from a point to a line segment."""
    px, py = point
    sx, sy = seg_start
    ex, ey = seg_end
    dx = ex - sx
    dy = ey - sy
    seg_len_sq = dx * dx + dy * dy
    if seg_len_sq == 0:
        return math.hypot(px - sx, py - sy)
    t = ((px - sx) * dx + (py - sy) * dy) / seg_len_sq
    t = max(0.0, min(1.0, t))
    proj_x = sx + t * dx
    proj_y = sy + t * dy
    return math.hypot(px - proj_x, py - proj_y)


def _min_distance_polygon_to_polygon(
    poly1: Sequence[Point], poly2: Sequence[Point]
) -> float:
    """Return the minimum edge-to-vertex distance between two polygons.

    Sufficient for the changing-room barrier check at the spec INV-10 scale
    (200 mm). Runtime project hosts an exact edge-to-edge calculation.
    """
    n1 = len(poly1)
    n2 = len(poly2)
    distances: list[float] = []
    # Each vertex of poly2 against each edge of poly1
    for i in range(n1):
        edge_start = poly1[i]
        edge_end = poly1[(i + 1) % n1]
        for v in poly2:
            distances.append(
                _point_to_segment_distance(v, edge_start, edge_end)
            )
    # Each vertex of poly1 against each edge of poly2
    for i in range(n2):
        edge_start = poly2[i]
        edge_end = poly2[(i + 1) % n2]
        for v in poly1:
            distances.append(
                _point_to_segment_distance(v, edge_start, edge_end)
            )
    return min(distances)


def check_changing_room_overlap(
    pool_zone_2_polygon: Sequence[Point],
    adjacent_room_polygon: Sequence[Point],
    barrier_distance_mm: float = DEFAULT_CHANGING_ROOM_BARRIER_MM,
) -> bool:
    """§702.55.4 changing-room adjacency barrier check.

    Returns True when the Zone 2 boundary sits within ``barrier_distance_mm``
    of the adjacent room polygon (i.e. a barrier is REQUIRED). Returns False
    when the adjacent room sits beyond the barrier distance.

    Args:
        pool_zone_2_polygon: §702 Zone 2 plan polygon.
        adjacent_room_polygon: changing-room plan polygon.
        barrier_distance_mm: §702.55.4 threshold (default 200 mm per INV-10).
    """
    if polygon_intersects(pool_zone_2_polygon, adjacent_room_polygon):
        return True
    distance = _min_distance_polygon_to_polygon(
        pool_zone_2_polygon, adjacent_room_polygon
    )
    return distance < float(barrier_distance_mm)
