# Reasoning — cascade-lighting-layout-uk-bathroom

## Cascade context

This is the cascade retrofit version of the C.1 standalone example
`uk-bathroom-standard-bath-and-shower`. The standalone example treats
`existing_fixtures` as engineer-supplied input; this cascade example
treats them as **consumed from an upstream lighting-layout intent**
(synthetic intent file at
`electrical/lighting-layout/examples/uk-bathroom-cascade-source/intent-out.json`).

The math, zones, constraints, and compliance verdict are **identical** to
the C.1 source. What differs is the hand-off contract:

1. `existing_fixtures_audit[]` is wired up to mirror the consumed fixture
   catalogue (3 fixtures: `lum_1`, `lum_2`, `shaver_1`).
2. The special-locations intent payload propagates
   `non_compliance_flags=[]` downstream so:
   - **lighting-layout INV-12** (cross-check special-locations zoning
     against luminaire positions) PASSes on cascade.
   - **db-layout INV-16 sub-check 3** (RCD-blanket-by-room enforcement)
     PASSes on cascade because `rcd_blanket_by_room` is present in
     `electrical_constraints[]`.

## Step 0 — Cascade prereq check

- `_special_locations_cascade_source.upstream_consumer_intent_location` is set
  in the input. The skill enters `full_analysis` mode.
- `existing_fixtures[]` carry `_consumed_from` provenance markers
  identifying the source lighting-layout intent.
- `consumed_lighting_layout_intent` in the intent-out.json is set to the
  upstream path string (NOT `null`, distinguishing this cascade run from
  the C.1 standalone run).

## Step 1 — Room classification

Identical to C.1 source:

- `room.room_type` is `bathroom` → BS 7671:2018 Part 7 §701 applies.
- Room polygon: 2700 × 2100 mm rectangle; `area_m2 = 5.67`.
- Ceiling at 2400 mm; `is_wet_room: false`.

## Step 2 — Anchor inventory

Identical to C.1 source:

- `bath_1` — `bath_basin`, rectangular 1700 × 700 × 550 mm; position at
  `(500, 0)` → footprint `(500, 0) → (2200, 700)`.
- `shower_1` — `shower_position` at `(1050, 350)`; head at 2100 mm AFF.

Both anchors `_extraction_source: architectural_drawing_extraction`
(strongest tier); provenance notes ≥40 chars each (INV-09 PASS).

## Step 3 — Zone derivation (BS 7671:2018 §701 zone-table)

5 zones derived (same as C.1 source):

| zone_id              | zone_type   | source_anchor | height_min | height_max | IPmin | maxV |
|----------------------|-------------|---------------|-----------:|-----------:|-------|-----:|
| `zone_bath_1_z0`     | bath_zone_0 | bath_1        | 0          | 550        | IPx7  | 12   |
| `zone_bath_1_z1`     | bath_zone_1 | bath_1        | 550        | 2250       | IPx4  | 230  |
| `zone_shower_1_z1`   | bath_zone_1 | shower_1      | 0          | 2100       | IPx4  | 230  |
| `zone_bath_1_z2`     | bath_zone_2 | bath_1        | 0          | 2250       | IPx4  | 230  |
| `zone_shower_1_z2`   | bath_zone_2 | shower_1      | 0          | 2100       | IPx4  | 230  |

Overlap declarations populated per INV-01 (zone_bath_1_z1↔zone_shower_1_z1
and zone_bath_1_z2↔zone_shower_1_z2). No silent merges.

## Step 4 — Per-zone safety properties

Identical to C.1 source: Zone 0 IPx7+SELV per §701.414.4.5; Zones 1 & 2
IPx4 + 30 mA RCD per §701.411.3.3; Zone 2 socket-distance 3 m per
§701.512.3.

## Step 5 — Electrical constraint derivation

Single constraint: `rcd_blanket_by_room` per §701.411.3.3.

This constraint is the *engineering payload* of the cascade for the
db-layout consumer (#15) — it triggers db-layout INV-16 sub-check 3
("every bathroom-serving circuit routed through 30 mA RCD").

## Step 6 — Consume lighting-layout intent (the cascade core)

The cascade input declares `_special_locations_cascade_source` and lists
3 existing fixtures consumed from a synthetic upstream lighting-layout
intent:

| fixture_id | type            | position (x,y,z)         | IP    | V   | RCD   |
|------------|-----------------|--------------------------|-------|-----|-------|
| `lum_1`    | luminaire       | (1350, 1400, 2400)       | IPX4  | 230 | true  |
| `lum_2`    | luminaire       | (1050, 350, 2400)        | IPX4  | 230 | true  |
| `shaver_1` | shaver_socket   | (2400, 1800, 1400)       | IPX0  | 230 | true  |

Each is recorded in `existing_fixtures_audit[]` with
`compliance_status: compliant`, `violation_sub_rule: null`,
`violation_clause: null`, `severity: null`.

## Step 7 — INV-08 sub-rule walk-through (the cascade core)

For each of 3 fixtures, all 4 sub-rules are evaluated:

### lum_1 at (1350, 1400, 2400)

- **(a) type_prohibited:** luminaire is permitted in all bathroom zones.
  Position (1350, 1400) is OUTSIDE all zone polygons in plan
  (`zone_bath_1_z2` extends to y=1300 unclipped → 1400 > 1300; outside
  Zone 2). At z=2400 it sits ABOVE Zone 1 max-height 2250 mm. **PASS.**
- **(b) ip_below_min:** IPx4 ≥ IPx4 (Zone 1/2 minimum). **PASS.**
- **(c) switch_distance_too_close:** N/A (luminaire is not a socket).
  **PASS.**
- **(d) voltage_above_max:** 230 V ≤ Zone 1/2 max_voltage 230 V. **PASS.**

### lum_2 at (1050, 350, 2400)

- **(a) type_prohibited:** position (1050, 350) sits WITHIN the bath
  polygon plan extents `(500,0)-(2200,700)` (inside Zone 1 plan). At
  z=2400 it sits ABOVE Zone 1 max-height 2250 mm AND ABOVE the
  shower-derived Zone 1 max-height 2100 mm. So vertically out-of-zone;
  the luminaire is effectively a ceiling-mounted IPx4 fixture outside
  any §701 zone. **PASS.**
- **(b) ip_below_min:** IPx4 (would meet Zone 1 IPx4 minimum even if
  in-zone). **PASS.**
- **(c) switch_distance_too_close:** N/A. **PASS.**
- **(d) voltage_above_max:** 230 V ≤ 230 V. **PASS.**

### shaver_1 at (2400, 1800, 1400)

- **(a) type_prohibited:** shaver_socket is explicitly permitted in
  bathroom Zone 2 per the §701 zone-table BS EN 61558-2-5 derogation.
  Position (2400, 1800) sits OUTSIDE Zone 2 unclipped polygon
  (y=1800 > y_max=1300). **PASS.**
- **(b) ip_below_min:** IPx0 is the special-case permitted IP for
  BS EN 61558-2-5 isolating-transformer shaver sockets per the §701
  zone-table derogation. **PASS.**
- **(c) switch_distance_too_close:** The 3 m rule on Zone 2 applies to
  generic socket_230v fixtures per §701.512.3. Shaver sockets are
  explicitly excluded from this rule by the §701 zone-table BS EN
  61558-2-5 derogation (the integral isolating transformer provides the
  safety barrier in lieu of the distance rule). **PASS.**
- **(d) voltage_above_max:** 230 V primary ≤ Zone 2 max_voltage 230 V.
  **PASS.**

**Sub-rule summary:** all 12 evaluations (3 fixtures × 4 sub-rules) PASS.
`existing_fixtures_audit[]` records all 3 as `compliance_status:
compliant`. `non_compliance_flags[]` is empty.

## Step 8 — Invariants

All 10 INVs PASS:

- **INV-01** zone catalogue integrity: 2 anchors → 5 zones with declared
  overlaps. PASS.
- **INV-02** existing_fixtures_audit ↔ non_compliance_flags 1:1: zero
  violations on both sides; vacuously holds. PASS.
- **INV-03** medical IT N/A (not Group 2). PASS vacuously.
- **INV-04** rcd_blanket_by_room PRESENT with rcd_rating_ma=30 and
  sauna_heater_excluded=false. PASS.
- **INV-05** main equipotential bonding N/A (not pool). PASS vacuously.
- **INV-06** whirlpool pump N/A (standard bath). PASS vacuously.
- **INV-07** ELV separation N/A (no ELV anchors). PASS vacuously.
- **INV-08** existing_fixtures audit: 12 sub-rule evaluations all PASS.
- **INV-09** anchor provenance: both anchors strongest tier; ≥40-char
  provenance notes. PASS.
- **INV-10** rollup self-consistency: compliant=true ∧
  violation_count_critical=0 ∧ violation_count_high=0 ∧
  non_compliance_flags=[] ∧ declared overlaps only. PASS.

## Step 9 — Consumer-side hand-off expectations

When the cascade is consumed by downstream skills:

### lighting-layout v1.6 INV-12 (cross-check)

INV-12 iterates over each consumed_summary luminaire from the
lighting-layout side and verifies it does NOT violate any derived zone
in this special-locations intent. Because all 3 fixtures are recorded as
`compliance_status: compliant` in `existing_fixtures_audit[]` AND
`non_compliance_flags=[]`, lighting-layout INV-12 PASSes vacuously on the
special-locations side of the contract. The lighting-layout output IR's
`special_locations_cross_check_compliant` flag will be set to `true`.

### db-layout v1.5 INV-16 sub-check 3 (RCD enforcement)

INV-16 sub-check 3 fires because `rcd_blanket_by_room` is present in
`electrical_constraints[]`. db-layout iterates over every circuit in its
output IR that serves a load WITHIN the bathroom polygon and verifies
the upstream protective device is a 30 mA RCD (or RCBO with 30 mA
RCD-element). For this cascade, all 3 consumed fixtures `is_rcd_protected:
true` in the input, mirroring the constraint downstream.

### small-power v1.2 INV-12 (socket zone exclusion)

INV-12 on the small-power side checks that no socket is placed inside
Zone 1 plan polygon OR within 3 m of Zone 1 (per
`switch_position_min_distance_mm: 3000` on Zone 2). For this cascade,
`shaver_1` is the only socket-like fixture; it is correctly typed as
`shaver_socket` (not `socket_230v`), so the §701.512.3 rule does not
fire. small-power INV-12 PASSes.

## Step 10 — Honest disclosures

- **Synthetic upstream intent.** The lighting-layout v1.6 hand-off
  contract is not yet shipped. The upstream intent file is synthetic for
  this example. Cascade contract integrity is verified via Pass 4 of the
  golden CI gate (intent-out validation against
  `special-locations-zoning-intent.schema.json`), NOT via runtime
  consumption of a real lighting-layout intent.
- **Bath rim height** assumed 550 mm (typical UK acrylic bath); engineer
  of record to verify against manufacturer datasheet.
- **shaver_1 IPx0** is correct per the §701 zone-table BS EN 61558-2-5
  derogation; not a derogation that needs an engineering judgment flag.
- **Position-vs-zone semantics.** All 3 fixtures are technically OUTSIDE
  the §701 zone polygons (lum_1/2 above max-height; shaver_1 in plan
  outside Zone 2 unclipped boundary). The cascade audit therefore
  records `derived_zone_id: null` for all 3 — they are in the room
  polygon but not in any §701 zone — and `compliance_status: compliant`
  because the §701 prohibitions don't apply to fixtures outside the
  zones.

## Step 11 — Failure modes considered

If `shaver_1` were re-typed as `socket_230v` instead of `shaver_socket`,
sub-rule (c) `switch_distance_too_close` would fire because the position
(2400, 1800) is only ~500 mm clear of the Zone 2 unclipped boundary
y=1300 — well inside the 3 m exclusion. The cascade would then report
`compliance_status: violation`, `violation_sub_rule:
switch_distance_too_close`, `violation_clause: BS 7671:2018 §701.512.3`,
`severity: critical`, and 1 entry in `non_compliance_flags[]`. This
failure-mode is exercised in cascade #12
(`cascade-small-power-uk-bathroom-violation`).

## Cross-references

- C.1 source: `electrical/special-locations/examples/uk-bathroom-standard-bath-and-shower/`
- Spec §9.2 cascade row 9: PASS case
- Plan portion 3 Task C.2 Step 2
