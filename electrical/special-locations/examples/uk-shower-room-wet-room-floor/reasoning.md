# Reasoning — uk-shower-room-wet-room-floor

## Step 0 — Cascade prereq check

Standalone wet-room example. No upstream `lighting-layout` intent
consumed. 2 existing fixtures supplied in input. Skill runs in
`full_analysis` mode.

## Step 1 — Room classification

- `room.room_type = shower_room` → BS 7671:2018 §701 applies (the same
  section that covers baths, because §701 is "Locations containing a
  bath or shower").
- `is_wet_room: true` — this is the critical input flag that triggers
  the Zone 1 floor-area expansion described below.
- Geometry: 1800 × 1500 mm rectangle; area 2.7 m²; ceiling at 2300 mm.
- Floor finish `tiles` with linear floor drain (mentioned in the
  shower's provenance note).

## Step 2 — Anchor inventory

Single anchor: `shower_1` — a `shower_position` at the central point
of the room (900, 750), with `shower_head_height_mm: 2150`. No bath
anchor. Provenance is `architectural_drawing_extraction` (strongest
tier), 175-char `_provenance_note` describing the wet-room linear
floor drain.

## Step 3 — Zone derivation (wet-room expansion)

This example exercises the key non-standard §701 case: the wet-room
Zone 1 expansion.

**Standard §701 zone-table** (used in examples #1 and #2):

- Zone 0 = interior of bath basin.
- Zone 1 = vertical projection above bath polygon, to higher of
  2250 mm or shower head height.
- Zone 2 = 600 mm horizontal extension of Zone 1.

**Wet-room §701 expansion** (used here):

- Zone 0 omitted — there is no basin to enclose (no bath, just a tiled
  floor with a drain).
- **Zone 1 EXPANDS to the full floor area** to 2.25 m AFF because the
  entire floor is treated as a wet area.
- Zone 2 omitted because Zone 1 already covers the full room polygon —
  there is no further 600 mm horizontal extension possible inside the
  room.

The wet-room rule is **NOT codified as a §701 sub-clause in the
verified BS 7671:2018+A2:2022 file**. The convention is sourced from
IET GN7 (Guidance Note 7) commentary on wet rooms. The skill cites
generic `BS 7671:2018 §701` and explicitly records the IET GN7
cross-reference in `_clause_citation` and `_derivation_note`. **The
banned-list §701 sub-clause for the wet-room rule is NOT used.**

### Net zones derived (1 total)

| zone_id                       | zone_type   | polygon                    | height_min | height_max | IPmin | maxV |
|-------------------------------|-------------|----------------------------|-----------:|-----------:|-------|-----:|
| `zone_shower_1_z1_wetroom`    | bath_zone_1 | full room (0,0)-(1800,1500)| 0          | 2250       | IPx4  | 230  |

`overlapping_with_zone_ids[]` is empty — only one zone exists.

## Step 4 — Per-zone safety properties

- `ip_rating_min: IPx4` — baseline §701 Zone 1 IP (no whirlpool/water
  jets, so §701.512.2 IPx5 lift does not apply).
- `max_voltage_v: 230` with `rcd_required_ma: 30` — Zone 1 permits
  230 V class_1/2/3 fixtures with the bathroom RCD blanket.
- `prohibited_fixture_types: ["socket_230v", "switch_230v",
  "luminaire_non_ip_rated"]` — standard Zone 1 prohibitions.

## Step 5 — Electrical constraint derivation

One constraint: `rcd_blanket_by_room` per **§701.411.3.3** (the
same blanket §701 imposes on bathrooms).

- `applies_to_room_polygon: true`.
- `rcd_rating_ma: 30`.
- `applies_to_circuit_types: ["lighting", "sockets", "shower_unit",
  "fixed_equipment", "extract_fan"]` — extract fan added because the
  existing-fixtures list includes one.
- `sauna_heater_excluded: false` (sauna-only exemption).

## Step 6 — Existing-fixture audit

Two fixtures supplied:

1. **`lum_1` — luminaire, IPX5, 230 V, RCD-protected, at (900, 750, 2300)**
   - Ceiling-mounted directly above the shower head (same plan
     coordinates).
   - z = 2300 > Zone 1 height_max = 2250 → fixture sits in the
     "outside-zones" remainder above the wet-room zone ceiling.
   - `derived_zone_id: null`.
   - Type allowed; IP IPx5 ≥ IPx4 min; voltage 230 V ≤ 230 V; not a
     switch. **compliant**.

2. **`fan_1` — wall_extract_fan, IPX4, 230 V, RCD-protected, at (1750, 750, 2100)**
   - Wall-mounted on east wall at 2100 mm AFF.
   - Position (1750, 750, 2100) sits INSIDE Zone 1 (full floor polygon;
     2100 < 2250 max). `derived_zone_id: zone_shower_1_z1_wetroom`.
   - Type `wall_extract_fan` not in `prohibited_fixture_types` for
     Zone 1; IPx4 ≥ IPx4 min; 230 V ≤ 230 V max; not a switch.
   - **compliant**.

Both fixtures compliant ⇒ no `non_compliance_flags`. INV-02 holds
trivially.

## Step 7 — Invariant evaluation (10 INVs)

| INV    | Outcome | Notes                                                                |
|--------|---------|----------------------------------------------------------------------|
| INV-01 | PASS    | 1 anchor → 1 zone; no overlaps                                       |
| INV-02 | PASS    | 0 violations both sides                                              |
| INV-03 | PASS    | no Group 2 zone (vacuous)                                            |
| INV-04 | PASS    | rcd_blanket_by_room present                                          |
| INV-05 | PASS    | not a pool hall (vacuous)                                            |
| INV-06 | PASS    | no bath_basin (vacuous)                                              |
| INV-07 | PASS    | no ELV anchor (vacuous)                                              |
| INV-08 | PASS    | 2 fixtures compliant                                                 |
| INV-09 | PASS    | architectural extraction for shower_1                                |
| INV-10 | PASS    | compliant=true; 0 critical; non_compliance_flags=[]                  |

`calculation_summary.compliant: true`.

## Step 8 — Assumptions recorded

Three assumptions in `calculation_summary.assumptions[]`:

1. Wet-room Zone 1 expansion is sourced from IET GN7 commentary; the
   verified BS 7671:2018+A2:2022 file contains no §701 sub-clause for
   the wet-room expansion — citation reverts to generic §701.
2. Shower head at 2150 mm AFF; Zone 1 ceiling capped at the lower of
   2250 mm or shower-head height = 2250 mm (shower head sits 100 mm
   below the default Zone 1 ceiling).
3. Zone 0 omitted: wet-room shower has no basin to enclose.

## Step 9 — Reviewer D-checks

No D-checks fire in this example:

- **D-1** — shower_1 is architectural extraction, not inferred.
- **D-2** — no pool zone.
- **D-3** — no whirlpool bath.
- **D-4** — no medical IT constraint.
- **D-5** — `is_external=false`; no ELV anchor.

`_engineering_judgments: []`.

## Step 10 — Honest disclosures (this example exercises 3)

1. **Wet-room Zone 1 expansion is not codified in the verified BS
   7671 file.** It comes from IET GN7 commentary. The skill records
   this in `_clause_citation` and `_derivation_note` rather than
   claiming a non-existent §701 sub-clause.
2. **Zone 0 omitted explicitly** — assumptions list records why (no
   basin in a wet-room shower).
3. **Shower head at 2150 mm < 2250 mm default Zone 1 ceiling** — the
   skill applies the lower-of rule and records the choice.

## Step 11 — Intent payload emission

Emitted `special_locations_zoning` intent contains 1 zone + 1
constraint + `compliant: true` + `anchor_source_summary.all_extracted:
true`. Downstream consumers (lighting-layout, small-power, db-layout)
receive the full-floor wet-room polygon and apply per-fixture checks
against it.

## Step 12 — Compliance verdict

`compliant: true`. Wet-room demonstrates the §701 floor-area expansion
on the smallest sensible footprint (1800 × 1500 mm). The expansion
shrinks the zone count from 5 (standard bath case) to 1 (everything
becomes Zone 1) but tightens IP requirements across the whole floor.
All 10 INVs PASS.

## Citation hygiene check

Citations used in this example:

- `BS 7671:2018 §701` ✓ (verified, top-level)
- `BS 7671:2018 §701.411.3.3` ✓ (verified)
- `IET GN7` ✓ (named cross-reference per spec §3.2)

Banned citations NOT used: any §701 sub-clause on the spec §3.2
banned-list. The wet-room expansion cites generic §701 + IET GN7
cross-reference instead.
