# Reasoning — cascade-lighting-layout-uk-pool-hall

## Cascade context

This is the cascade retrofit version of the C.1 standalone example
`uk-pool-hall-with-changing-room-adjacency`. The standalone example
treats `existing_fixtures` as engineer-supplied input; this cascade
treats them as **consumed from an upstream lighting-layout intent**
(synthetic intent file at
`electrical/lighting-layout/examples/uk-pool-hall-cascade-source/intent-out.json`).

The math, zones, constraints, and D-2 reviewer judgment are **identical**
to the C.1 source. The cascade hand-off contract wires
`existing_fixtures_audit[]` to mirror the consumed 4 IPx5 ceiling
luminaires.

## Step 0 — Cascade prereq check

- `_special_locations_cascade_source.upstream_consumer_intent_location` set
  in input → skill enters `full_analysis` mode.
- `existing_fixtures[]` carry `_consumed_from` provenance markers.
- `consumed_lighting_layout_intent` in intent-out set to the upstream
  path string.

## Step 1 — Room classification

- `room.room_type: swimming_pool_hall` → BS 7671:2018 Part 7 §702.
- 12 000 × 6 000 mm; `area_m2 = 72`; ceiling 4 500 mm.
- Adjacent changing room on the SOUTH wall (y=0) at the standalone's
  request — drives D-2 reviewer flag.

## Step 2 — Anchor inventory

- `pool_main` — `pool_basin`, rectangular 10 000 × 5 000 × 1 800 mm;
  position `(1000, 500)` → footprint `(1000, 500) → (11000, 5500)`.
- `_extraction_source: architectural_drawing_extraction`.

## Step 3 — Zone derivation (BS 7671:2018 §702 zone-table)

3 zones (same as C.1 source):

| zone_id              | zone_type   | height_min | height_max | IPmin | maxV |
|----------------------|-------------|-----------:|-----------:|-------|-----:|
| `zone_pool_main_z0`  | pool_zone_0 | 0          | 200        | IPx8  | 12   |
| `zone_pool_main_z1`  | pool_zone_1 | 200        | 2500       | IPx5  | 230  |
| `zone_pool_main_z2`  | pool_zone_2 | 200        | 2500       | IPx4  | 230  |

The Zone 2 unclipped polygon extends to y=-3000 (south of room
boundary), triggering D-2: pool_zone_2 enters the adjacent changing room
polygon. Per §702.55.4, Zone 2 extension into a changing room is
permitted only where a fixed barrier ≥2.5 m AFF separates the changing
room from the pool zone. Engineer-of-record must confirm presence and
compliance.

## Step 4 — Per-zone safety properties

- Zone 0: IPx8 (submersible) + SELV ≤12 V per §702 zone-table.
- Zone 1: IPx5 (splash + pool jets typical); 230 V permitted with RCD.
- Zone 2: IPx4; sockets prohibited unless ≥3 m from Zone 1 (handled by
  §702 zone-table, similar in spirit to §701.512.3).

## Step 5 — Electrical constraint derivation

Single constraint: `pool_main_equipotential_bonding` per
**§702.415.1** — main equipotential bonding ≥10 mm² to all
extraneous-conductive-parts (pool basin, water-circulation pipework,
deck reinforcement).

## Step 6 — Consume lighting-layout intent

4 ceiling luminaires consumed from the upstream lighting-layout intent:

| fixture_id | position (x,y,z)       | IP   | V   | RCD  |
|------------|------------------------|------|-----|------|
| `lum_1`    | (3000, 1500, 4500)     | IPx5 | 230 | true |
| `lum_2`    | (3000, 4500, 4500)     | IPx5 | 230 | true |
| `lum_3`    | (9000, 1500, 4500)     | IPx5 | 230 | true |
| `lum_4`    | (9000, 4500, 4500)     | IPx5 | 230 | true |

All sit at z=4500 mm (ceiling level), ABOVE pool_zone_1 height_max
2500 mm — ceiling-mounted outside the §702 zone vertical extent.

## Step 7 — INV-08 sub-rule walk-through

For each of 4 fixtures:

- **(a) type_prohibited:** luminaire permitted in pool_zone_1/2 when
  IPx5+ per §702 zone-table. **PASS.**
- **(b) ip_below_min:** IPx5 ≥ IPx5 minimum (pool_zone_1 splash). **PASS.**
- **(c) switch_distance_too_close:** N/A — luminaires not sockets.
  **PASS.**
- **(d) voltage_above_max:** 230 V ≤ 230 V. **PASS.**

Sub-rule summary: 16 evaluations (4 fixtures × 4 sub-rules) all PASS.
`derived_zone_id: null` for all 4 because they sit vertically above the
§702 zone envelope.

## Step 8 — Invariants

All 10 INVs PASS:

- **INV-01** zone catalogue integrity: 1 anchor → 3 zones; no overlaps
  required. PASS.
- **INV-02** audit ↔ flags 1:1: zero violations both sides. PASS.
- **INV-03** medical IT N/A. PASS vacuously.
- **INV-04** rcd_blanket N/A (pool hall uses pool_main_equipotential
  not blanket RCD). PASS vacuously.
- **INV-05** pool main equipotential bonding PRESENT per §702.415.1.
  PASS.
- **INV-06** whirlpool pump N/A. PASS vacuously.
- **INV-07** ELV separation N/A. PASS vacuously.
- **INV-08** 16/16 sub-rule evaluations PASS.
- **INV-09** anchor provenance strongest tier; ≥40-char notes. PASS.
- **INV-10** rollup self-consistency holds. PASS.

## Step 9 — D-2 changing-room boundary judgment

The D-2 reviewer flag is carried forward from the C.1 source:
`pool_zone_2` polygon extends into the adjacent 4×3 m changing room
(located at y=-3000 to 0, x=4000 to 8000 per architectural plan note).
Per §702.55.4, Zone 2 extension into a changing room is permitted ONLY
where a fixed barrier of height ≥2.5 m AFF separates the changing room
from the pool zone. Engineer-of-record must confirm presence and
compliance.

This flag is surfaced via `calculation_summary._engineering_judgments[]`
— downstream consumers should propagate it to the engineer-of-record but
it does NOT downgrade the cascade `compliant=true` verdict because no
existing fixture is placed in the boundary-suspect region.

## Step 10 — Consumer-side hand-off expectations

### lighting-layout v1.6 INV-12 (cross-check)

INV-12 iterates over each consumed luminaire and verifies it does NOT
violate any §702 zone. All 4 fixtures audit as compliant; INV-12 PASSes
vacuously. The lighting-layout output IR's
`special_locations_cross_check_compliant` flag will be set to `true`.
The lighting-layout side should also propagate the D-2 changing-room
boundary judgment into its own `_engineering_judgments[]`.

### db-layout INV-16 sub-check 3

For pool halls, `rcd_blanket_by_room` is NOT issued (pool halls use
fixture-specific RCD per §702 zone properties, not blanket RCD per
§701.411.3.3). Instead, db-layout sub-check 2 fires:
`pool_main_equipotential_bonding` from `electrical_constraints[]`
requires the db-layout to model a ≥10 mm² supplementary bonding
conductor to all extraneous-conductive-parts.

## Step 11 — Honest disclosures

- **Synthetic upstream intent.** lighting-layout v1.6 hand-off not yet
  shipped; cascade contract integrity is verified via golden CI gate
  Pass 4 (intent-out validation), NOT runtime consumption.
- **Pool floor reference.** "Floor reference 0" = pool deck level;
  water surface at 200 mm above deck per the architect's hydraulic
  schedule (C.1 source).
- **D-2 carried forward.** The §702.55.4 changing-room boundary
  judgment is engineer-of-record's responsibility; the cascade does not
  re-derive it.

## Step 12 — Failure modes considered

If any of the 4 luminaires were placed at z<2500 mm (within pool_zone_1
vertical extent) AND not IPx5+, sub-rule (b) `ip_below_min` would fire
on §702 zone-table. Sub-rule (a) `type_prohibited` would fire if any
were `socket_230v` instead of `luminaire`. Neither failure-mode is
exercised in this cascade — that's the deliberate happy-path content.

## Cross-references

- C.1 source: `electrical/special-locations/examples/uk-pool-hall-with-changing-room-adjacency/`
- Spec §9.2 cascade row 10: PASS case
- Plan portion 3 Task C.2 Step 2
