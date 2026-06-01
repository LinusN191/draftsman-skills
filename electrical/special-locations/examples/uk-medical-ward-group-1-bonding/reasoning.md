# Reasoning — uk-medical-ward-group-1-bonding

## Step 0 — Cascade prereq check

Standalone Group 1 recovery ward example. No upstream
`lighting-layout` intent consumed. 5 existing fixtures (4 bedside
medical isolating sockets + 1 central ceiling luminaire) supplied
directly via the input. Skill runs in `full_analysis` mode.

## Step 1 — Room classification

- `room.room_type = medical_group_1_ward` → BS 7671:2018 §710 applies,
  specifically Group 1 (normal patient care / observation; mains
  failure tolerable for short period; medical electrical equipment
  used externally and applied to skin, but NOT life-supporting in the
  Group 2 sense).
- Geometry: 8000 × 6000 mm; area 48 m²; ceiling 2800 mm.
- Floor finish `vinyl` (typical conductive sheet vinyl for ward
  environments — anti-static where required, sourced per HBN 00-03).
- `is_wet_room: false`, `is_external: false`.

## Step 2 — Anchor inventory

Four anchors: `bed_1`, `bed_2`, `bed_3`, `bed_4`. Each is a
`medical_patient_position` (echoed in the IR as `medical_bed`
`fixture_type` per the enum), with `medical_group: 1` and
`radius_mm: 1500`. Positions are arranged in a 2×2 grid:

| Bed | x_mm | y_mm | z_mm (bed top) |
|---|---|---|---|
| bed_1 | 1500 | 1500 | 700 |
| bed_2 | 4000 | 1500 | 700 |
| bed_3 | 1500 | 4500 | 700 |
| bed_4 | 4000 | 4500 | 700 |

Inter-bed centre-to-centre spacing: 2500 mm along the long axis
(bed_1↔bed_2 and bed_3↔bed_4); 3000 mm across the central corridor
(bed_1↔bed_3 and bed_2↔bed_4). HBN 04-01 recommends 2500 mm minimum
between bed centres on the same wall and 2400 mm clear between the
foot of beds opposing each other — both satisfied here.

Provenance: all four anchors use
`architectural_drawing_extraction` (strongest tier).
`_provenance_note` lengths: 189 / 193 / 160 / 156 chars — all ≥40
per INV-09.

## Step 3 — Zone derivation (Group 1 patient envelopes)

Per §710 Group 1 convention, each patient environment is a **1.5 m
radius cylinder** centred on the patient/bed centroid, extending
vertically from floor to 2500 mm AFF. The 1.5 m radius is the
"patient environment" radius for the cohort where applied parts of
medical electrical equipment can reach the patient.

The schema stores zones as plan polygons (it cannot store a cylinder
primitive). Per **spec §5.7 geometry-validation convention**,
cylinder zones are approximated by a **12-sided regular polygon**
(≥12 sides mandated by the schema's `boundary_plan_polygon_mm`
`minItems: 3` plus the derivation convention).

### Vertex computation

For each anchor at `(cx, cy)` with `r=1500`, vertices computed at
30° intervals (starting at 0° on the +x axis):

```
v_k = (cx + r·cos(k·30°), cy + r·sin(k·30°))   for k = 0..11
```

Working through bed_1 at (1500, 1500):
- v_0  = (1500 + 1500, 1500 + 0)    = (3000, 1500)
- v_1  = (1500 + 1299, 1500 + 750)  = (2799, 2250)
- v_2  = (1500 + 750,  1500 + 1299) = (2250, 2799)
- v_3  = (1500 + 0,    1500 + 1500) = (1500, 3000)
- v_4  = (1500 - 750,  1500 + 1299) = (750,  2799)
- v_5  = (1500 - 1299, 1500 + 750)  = (201,  2250)
- v_6  = (1500 - 1500, 1500 + 0)    = (0,    1500)
- v_7  = (1500 - 1299, 1500 - 750)  = (201,  750)
- v_8  = (1500 - 750,  1500 - 1299) = (750,  201)
- v_9  = (1500 + 0,    1500 - 1500) = (1500, 0)
- v_10 = (1500 + 750,  1500 - 1299) = (2250, 201)
- v_11 = (1500 + 1299, 1500 - 750)  = (2799, 750)

Same template applied to bed_2 (offset +2500 in x), bed_3 (offset
+3000 in y), bed_4 (both offsets) — see `output.json` polygons.

### Overlap audit

- **bed_1 ↔ bed_2** (centres 2500 mm apart, sum of radii = 3000 mm):
  envelopes overlap by ~500 mm width along the central spine
  between x=2500 and x=3000. Catalogued in
  `calculation_summary.assumptions[]`.
- **bed_3 ↔ bed_4**: identical to bed_1 ↔ bed_2 (south-row mirror).
- **bed_1 ↔ bed_3** (centres 3000 mm apart, sum of radii = 3000 mm):
  envelopes are tangent at the central y=3000 line — zero overlap
  area.
- **bed_2 ↔ bed_4**: identical to bed_1 ↔ bed_3.
- **Diagonals**: 3905 mm separation (√(2500² + 3000²)) > 3000 mm —
  no overlap.

The overlap pairs (bed_1↔bed_2, bed_3↔bed_4) are explicitly
catalogued in `assumptions[]` for INV-01 transparency; this avoids
the "silent merge" failure mode INV-01 is designed to catch. The
schema-level `overlapping_with_zone_ids[]` field is left empty
because the runtime treats the long-axis overlap as a documented
geometric consequence of HBN 04-01 spacing rather than a true zone
conflict — bonding is room-polygon-wide.

## Step 4 — Electrical constraints (Group 1 → bonding only)

Per BS 7671:2018 §710, Group 1 mandates **supplementary
equipotential bonding** within each patient environment. Group 1
does NOT mandate a medical IT system — that obligation is Group 2
only.

The single `supplementary_equipotential_bonding` constraint
declares:
- `applies_to_room_polygon: true` — bonding network covers the
  whole ward, not zone-by-zone (bonding cannot stop and restart at
  envelope boundaries).
- `applies_to_zone_ids`: all 4 zone IDs listed for cross-reference.
- `metallic_parts_listed`: bed frames (×4), headboard medical-gas
  terminal units (×4), ward radiator, patient monitor chassis (×4).
- `bonding_conductor_csa_min_mm2: 4` — typical 4 mm² PVC-insulated
  bonding conductor sized per BS 7671 Table 54.7 (½ × CPC; for a 6
  mm² CPC the half is 3 mm² → next standard up = 4 mm²).
- `_clause_citation`: `BS 7671:2018 §710 + §701.415.2` — sourcing
  the bonding obligation via the §701.415.2 supplementary-bonding
  clause that §710 cross-references (no §710 sub-clauses are
  verified-file-valid).

**No `medical_it_system` constraint is emitted** because Group 1
does not require one. The schema-level allOf rule
"Group 2 envelope ⇒ medical_it_system constraint" only fires when a
`medical_envelope_group_2` zone is present — none here, so the rule
is N/A. This is the structural Group 1 vs Group 2 distinction and
is the core teaching of this example.

## Step 5 — Existing fixtures audit

Five fixtures supplied:

| ID | Type | x | y | z | IP | V | RCD | Zone |
|---|---|---|---|---|---|---|---|---|
| iso_socket_bed_1 | medical_isolating_socket | 1500 | 100 | 1100 | IPx4 | 230 | yes | zone_bed_1_envelope_g1 |
| iso_socket_bed_2 | medical_isolating_socket | 4000 | 100 | 1100 | IPx4 | 230 | yes | zone_bed_2_envelope_g1 |
| iso_socket_bed_3 | medical_isolating_socket | 1500 | 5900 | 1100 | IPx4 | 230 | yes | zone_bed_3_envelope_g1 |
| iso_socket_bed_4 | medical_isolating_socket | 4000 | 5900 | 1100 | IPx4 | 230 | yes | zone_bed_4_envelope_g1 |
| lum_central | luminaire | 4000 | 3000 | 2800 | IPx4 | 230 | yes | null |

- The four `medical_isolating_socket` entries are at the headboard
  wall positions (y=100 north wall for beds 1+2; y=5900 south wall
  for beds 3+4). Each falls within its corresponding 12-sided
  envelope polygon (centre 1500 mm from wall → wall position at
  y=100 is 1400 mm clear of centre, comfortably inside r=1500).
- Group 1 ward `prohibited_fixture_types: []` is empty — Group 1
  envelopes do not exclude any fixture types by enum match. The
  judgment that medical-isolating sockets are the correct headboard
  socket type is a design-stage decision sourced from HBN 04-01,
  not from §710 prohibited-list logic.
- `lum_central` at (4000, 3000, 2800) sits in the central corridor
  area at ceiling height — z=2800 mm > envelope `height_max=2500`,
  so the luminaire is outside all 4 zones by elevation. `derived_zone_id: null`.

All 5 fixtures `compliant`. `violation_count_critical: 0`;
`violation_count_high: 0`; `non_compliance_flags: []`.

## Step 6 — Calculation summary & assumptions

```
compliant: true
zone_count: 4
constraint_count: 1
violation_count_critical: 0
violation_count_high: 0
non_compliance_flags: []
```

Three assumptions recorded:
1. 12-sided polygon approximation per spec §5.7.
2. HBN 04-01 inter-bed spacing at 2500 mm centre-to-centre; the
   resulting long-axis envelope overlaps (~500 mm width) are an
   accepted geometric consequence given the room-polygon-wide
   bonding obligation.
3. Central ceiling luminaire is above all envelope ceilings
   (z=2800 > 2500); falls outside all zones by height.

No `_engineering_judgments[]` entries — no D-checks fire on this
clean Group 1 example.

## Step 7 — Invariant evaluation

| INV | Pass | Notes |
|---|---|---|
| INV-01 | ✓ | 4 anchors → 4 zones; sibling overlaps catalogued in assumptions[] (long-axis bed_1↔bed_2 and bed_3↔bed_4). No silent merges. |
| INV-02 | ✓ | 5 fixtures audited all compliant; non_compliance_flags[] empty. |
| INV-03 | ✓ | No Group 2 envelope → N/A vacuously passes. supplementary_equipotential_bonding is present (Group 1 obligation) but the IT-system obligation does NOT apply. |
| INV-04 | ✓ | Not a bathroom/sauna → §701/§703 RCD blanket N/A. |
| INV-05 | ✓ | Not a pool hall → §702.415.1 N/A. |
| INV-06 | ✓ | No bath_basin → §701.512.2 whirlpool N/A. |
| INV-07 | ✓ | No ELV anchor → §715 elv_separation N/A. |
| INV-08 | ✓ | 5 fixtures inspected, all 4 sub-rules PASS for each. |
| INV-09 | ✓ | All 4 anchors use architectural_drawing_extraction (strongest tier); _provenance_note lengths 156–193 chars. |
| INV-10 | ✓ | Self-consistency: compliant=true ∧ violation_count=0 ∧ flags=[]. |

## Step 8 — Honest disclosures

1. **§710 has no verified sub-clauses** in the verified standards
   file — bonding obligation sourced via §701.415.2 cross-reference.
   The 14 banned sub-clauses per spec §3.2 are NOT used anywhere in
   this example.
2. **Inter-bed spacing 2500 mm** is a HBN 04-01 NHS design
   recommendation; the resulting envelope overlap (~500 mm width
   along the long axis) is acceptable because supplementary bonding
   applies room-polygon-wide.
3. **Group 1 vs Group 2 distinction**: this example exists to teach
   the structural difference — Group 1 mandates bonding only; Group
   2 mandates bonding PLUS a medical IT system PLUS IMD with 8 s
   alarm response per BS EN 61557-8.

## Step 9 — Failure modes considered

- If `supplementary_equipotential_bonding` were omitted, the IR
  would still pass schema validation (no allOf rule pins it for
  Group 1), but engineer judgment would catch the omission via the
  §710 + §701.415.2 cross-reference. No INV currently captures this
  Group 1 specific obligation — caught instead by the consumer-side
  small-power INV that requires medical-isolating sockets on the
  IT-or-bonded-RCD circuit.
- If beds were placed <1 m apart (impossible at HBN 04-01 spacing),
  the long-axis overlap would exceed ~500 mm and may warrant a
  D-style reviewer flag.
- If a generic 230 V `socket_230v_non_medical` were placed at a
  headboard, `prohibited_fixture_types: []` (empty for Group 1)
  would NOT catch it — the type is permissive at Group 1. Design
  intent is enforced via the medical_isolating_socket type choice,
  not via the IR prohibition list. (Group 2 envelopes DO list
  `socket_230v_non_medical` in prohibited_fixture_types — see the
  Group 2 OR example.)

## Step 10 — Cross-skill cascade preview

If a downstream `small-power` skill consumes this intent:
- `zones[]` x4 with `prohibited_fixture_types: []` and
  `allowed_equipment_classes: ['class_1', 'class_2',
  'class_3_SELV']` is permissive — small-power can place any socket
  type but design judgment should require medical-isolating sockets.
- `electrical_constraints[]` x1 with
  `supplementary_equipotential_bonding` listing 10 metallic parts
  drives the small-power BOQ to include the corresponding bonding
  conductors.
- `compliant: true` and `non_compliance_flags: []` mean no cascade
  flags propagate upstream.
- `anchor_source_summary.all_extracted: true` so D-1-style
  provenance gating does not fire.
