# Reasoning — uk-bathroom-standard-bath-and-shower

## Step 0 — Cascade prereq check

Standalone example. No upstream `lighting-layout` intent consumed.
`consumed_lighting_layout_intent` is set to `null` in the intent payload.
`existing_fixtures` are supplied directly in the input (3 entries:
2 luminaires + 1 shaver socket). Skill proceeds in `full_analysis` mode
because fixture data is present and the input set is otherwise complete.

## Step 1 — Room classification

`room.room_type` is `bathroom` → BS 7671:2018 Part 7 §701 applies.
Room polygon is a 2700 × 2100 mm rectangle (`area_m2 = 5.67`); ceiling at
2400 mm. `is_wet_room: false` → Zone 1 does NOT expand to full floor area.
Floor finish `tiles` is the normal UK-domestic substrate; no IP-routing
implications beyond §701 baseline.

## Step 2 — Anchor inventory

Two anchors:

- `bath_1` — `bath_basin`, rectangular 1700 × 700 × 550 (height) mm.
  Position vector points to the bottom-left corner at `(500, 0)` →
  bath footprint spans `(500, 0) → (2200, 700)`. `bath_kind: standard`
  (NOT whirlpool), so INV-06 does not trigger.
  `_extraction_source: architectural_drawing_extraction` (strongest tier).
- `shower_1` — `shower_position`, located at `(1050, 350)` (midpoint of
  bath length, on the bath-internal axis), with `shower_head_height_mm: 2100`.
  Shower head height caps the shower-derived Zone 1 at 2100 mm AFF.

Both anchors carry full provenance notes (~165 chars each, well above
the 40-char minimum per INV-09). Both are extracted from the same
architectural Rev-C plan — single source of truth, no inconsistency to
flag.

## Step 3 — Zone derivation (BS 7671:2018 §701 zone-table)

The §701 zone-table convention specifies three concentric zones around a
bath:

- **Zone 0** — interior of the basin (volume bounded by the bath itself).
- **Zone 1** — vertical projection above the bath, from rim level to the
  higher of 2250 mm AFF or the fixed shower head height.
- **Zone 2** — 600 mm horizontal extension of Zone 1, sharing the same
  vertical bounds.

Because the shower is "over the bath" (a single wet area), both anchors
contribute zones with coincident plan polygons. The skill emits separate
zone entries per anchor per INV-01 ("every anchor produces ≥1 zone"),
with explicit `overlapping_with_zone_ids[]` cross-references — no silent
merges.

### Derived zones (5 total)

| zone_id              | zone_type   | source_anchor | polygon                                       | height_min | height_max | IPmin | maxV |
|----------------------|-------------|---------------|-----------------------------------------------|-----------:|-----------:|-------|-----:|
| `zone_bath_1_z0`     | bath_zone_0 | bath_1        | bath rectangle (500,0)-(2200,700)             | 0          | 550        | IPx7  | 12   |
| `zone_bath_1_z1`     | bath_zone_1 | bath_1        | bath rectangle (500,0)-(2200,700)             | 550        | 2250       | IPx4  | 230  |
| `zone_shower_1_z1`   | bath_zone_1 | shower_1      | bath rectangle (500,0)-(2200,700)             | 0          | 2100       | IPx4  | 230  |
| `zone_bath_1_z2`     | bath_zone_2 | bath_1        | unclipped (-100,-600)-(2800,1300) extension   | 0          | 2250       | IPx4  | 230  |
| `zone_shower_1_z2`   | bath_zone_2 | shower_1      | unclipped (-100,-600)-(2800,1300) extension   | 0          | 2100       | IPx4  | 230  |

The Zone 2 polygons are shown unclipped here for derivation transparency
(`_derivation_note` records that the runtime intersection with the room
polygon `(0,0)-(2700,2100)` yields `(0,0)-(2700,1300)`).

### Overlap declaration

Per INV-01, the catalogue records:

- `zone_bath_1_z1.overlapping_with_zone_ids: ["zone_shower_1_z1"]`
- `zone_shower_1_z1.overlapping_with_zone_ids: ["zone_bath_1_z1"]`
- `zone_bath_1_z2.overlapping_with_zone_ids: ["zone_shower_1_z2"]`
- `zone_shower_1_z2.overlapping_with_zone_ids: ["zone_bath_1_z2"]`

These are expected overlaps (shower-over-bath), not silent merges. INV-01
passes.

## Step 4 — Per-zone safety properties

For each zone, the skill instantiates:

- `ip_rating_min`: Zone 0 → IPx7 (immersion); Zones 1 & 2 → IPx4 (splash).
- `max_voltage_v`: Zone 0 → 12 V SELV per **§701.414.4.5**; Zones 1 & 2 →
  230 V permitted with RCD.
- `rcd_required_ma: 30` across all three zones per **§701.411.3.3**.
- `isolation_required`: Zone 0 → true; Zone 1 & 2 → false.
- `prohibited_fixture_types`: Zone 0 prohibits everything except SELV
  fixtures; Zone 1 prohibits sockets, switches, and non-IP-rated
  luminaires; Zone 2 prohibits sockets only.
- `switch_position_min_distance_mm: 3000` on Zone 2 per **§701.512.3**
  (socket outlets ≥3 m from Zone 1 boundary).

## Step 5 — Electrical constraint derivation

One constraint: `rcd_blanket_by_room` per **§701.411.3.3**.

- `applies_to_room_polygon: true` — covers the full bathroom polygon.
- `rcd_rating_ma: 30`.
- `applies_to_circuit_types: ["lighting", "sockets", "shower_unit",
  "fixed_equipment", "shaver_socket"]` — every LV circuit on the
  bathroom side of the room boundary.
- `sauna_heater_excluded: false` — heater exemption is a §703 sauna
  carve-out, not applicable to §701.

## Step 6 — Existing-fixture audit

Three fixtures supplied in `existing_fixtures[]`. For each one, the
skill performs the 4-sub-rule INV-08 check:

1. **`lum_1` — luminaire, IPX4, 230 V, RCD-protected, at (1350, 1400, 2400)**
   - Zone lookup: outside bath_zone_0 (not in bath polygon), outside
     bath_zone_1 (z=2400 > 2250 max), outside bath_zone_2 (y=1400 > 1300
     clipped max).
   - `derived_zone_id: null` (sits in the room but outside all derived
     zones — i.e., in the "outside-zones" remainder per §701).
   - Status: **compliant**.

2. **`lum_2` — luminaire, IPX4, 230 V, RCD-protected, at (1050, 350, 2400)**
   - Zone lookup: ceiling-mounted at z=2400 mm. Zone 1 height_max =
     2250 (bath_1) or 2100 (shower_1) → fixture is above both. Zone 2
     extends to 2250 max → again above.
   - `derived_zone_id: null` (above Zone 1 ceiling).
   - Type-rule: luminaire allowed; IP-rule: IPx4 ≥ Zone 2 IPx4 min;
     voltage-rule: 230 V ≤ 230 V; switch-rule: not a switch.
   - Status: **compliant**.

3. **`shaver_1` — shaver_socket, IPX0, 230 V, RCD-protected, at (2400, 1800, 1400)**
   - Zone lookup: x=2400 sits inside the unclipped Zone 2 x-range
     (-100 to 2800), but y=1800 is OUTSIDE the clipped Zone 2 y-range
     (-600 to 1300).
   - `derived_zone_id: null`.
   - BS EN 61558-2-5 shaver sockets are explicitly permitted in Zone 2
     even at IPx0 because the integral isolating transformer provides
     the safety barrier; outside Zone 2 the rule is even looser.
   - The §701.512.3 3 m socket rule prohibits **generic** 230 V sockets
     within 3 m of Zone 1 boundary, but shaver sockets are a distinct
     fixture_type to which the rule does not apply.
   - Status: **compliant**.

All 3 fixtures compliant ⇒ `existing_fixtures_audit[]` has 3 entries
with `compliance_status: "compliant"`; `non_compliance_flags[]` is
empty. INV-02 (one-to-one drift guard) trivially holds.

## Step 7 — Invariant evaluation (10 INVs)

| INV    | Outcome | Notes                                                            |
|--------|---------|------------------------------------------------------------------|
| INV-01 | PASS    | 2 anchors → 5 zones; overlaps catalogued                         |
| INV-02 | PASS    | 0 violations on both sides                                       |
| INV-03 | PASS    | no Group 2 zone (vacuous)                                        |
| INV-04 | PASS    | rcd_blanket_by_room present with rcd_rating_ma=30                |
| INV-05 | PASS    | not a pool hall (vacuous)                                        |
| INV-06 | PASS    | bath_kind=standard, not whirlpool (vacuous)                      |
| INV-07 | PASS    | no ELV anchor (vacuous)                                          |
| INV-08 | PASS    | 3 fixtures audited; all compliant                                |
| INV-09 | PASS    | both anchors at architectural_drawing_extraction tier            |
| INV-10 | PASS    | compliant=true ∧ 0 critical violations ∧ no silent overlaps      |

`calculation_summary.compliant: true`.

## Step 8 — Assumptions recorded

Two assumptions documented in `calculation_summary.assumptions[]`:

1. Bath rim height defaulted to 550 mm AFF (typical UK acrylic bath).
2. Shower head at 2100 mm AFF treated as Zone 1 ceiling per §701
   zone-table convention.

These are engineer-visible defaults — the engineer-of-record can update
the input if the bath manufacturer datasheet differs, and the zone
derivation will re-run.

## Step 9 — Reviewer D-checks

No D-check flags raised in this happy-path example:

- **D-1** — both anchors are architectural extractions, not inferred.
- **D-2** — no pool zone, so the §702.55.4 changing-room overlap rule
  does not apply.
- **D-3** — bath_kind=standard, not whirlpool, so the whirlpool pump
  assumption does not surface.
- **D-4** — no medical IT system constraint, so transformer VA
  plausibility does not apply.
- **D-5** — `is_external=false` and no ELV anchor, so ambient
  temperature defaulting does not surface.

`calculation_summary._engineering_judgments: []`.

## Step 10 — Intent payload emission

Emitted `special_locations_zoning` intent contains:

- All 5 zones (full geometry preserved so downstream cascade consumers
  can perform per-fixture placement checks).
- 1 electrical constraint (`rcd_blanket_by_room`).
- `compliant: true`, `zone_count: 5`, `constraint_count: 1`,
  `violation_count_critical: 0`, `violation_count_high: 0`,
  `non_compliance_flags: []`.
- `anchor_source_summary.all_extracted: true`,
  `extraction_source_lowest: "architectural_drawing_extraction"`.

Downstream consumers (`lighting-layout` v1.6, `small-power` v1.2,
`db-layout` v1.5) use this payload to enforce zone-aware constraints
in their own IRs.

## Step 11 — Honest disclosures

- Bath rim height is a typical-product default. Datasheet override
  available via input refinement.
- Shaver socket compliance is correct per §701 zone-table commentary
  (shaver-socket fixture_type is distinct from generic 230 V socket),
  but the engineer-of-record should verify the device complies with
  BS EN 61558-2-5.
- `_extraction_source` field provenance is preserved end-to-end through
  the intent payload `anchor_source_summary` so D-1 cascade checks can
  surface lower-confidence anchors downstream.
- All citations use only verified clauses from spec §3.2 — no banned
  §701 sub-clauses appear anywhere in this example.

## Step 12 — Compliance verdict

`compliant: true`. This is the baseline UK domestic bathroom — standard
bath + shower-over-bath, RCD blanket, IPx4 luminaires, BS EN 61558-2-5
shaver socket. All 10 INVs PASS. No reviewer flags. No fixture
violations.
