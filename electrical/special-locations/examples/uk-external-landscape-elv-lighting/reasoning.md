# Reasoning — uk-external-landscape-elv-lighting

## Step 0 — Cascade prereq check

Standalone external landscape ELV example. No upstream
`lighting-layout` intent consumed. 6 existing fixtures supplied
directly (one `elv_luminaire` per bollard). Skill runs in
`full_analysis` mode.

## Step 1 — Room classification

- `room.room_type = external_landscape` → BS 7671:2018 §715 applies
  (SELV / PELV / FELV extra-low-voltage installations) AND the
  external installation surcharge (Appendix 4 Table 4B1 ambient
  de-rating considerations).
- Geometry: 20000 × 15000 mm; area 300 m²; nominal "ceiling" 3000 mm
  (treated as a virtual ceiling for zone height-cap purposes; no
  physical roof exists on an external installation).
- Floor finish `soft_landscape` (grass + planted beds + paved paths
  per landscape architect's drawing).
- `is_external: true` — this is the trigger for the D-5 reviewer
  flag because no ambient_temperature_c was supplied in the input.
- `is_wet_room: false`.

## Step 2 — Anchor inventory

Six anchors: `elv_bollard_1` through `elv_bollard_6`. Each is an
`elv_luminaire` (12 V SELV LED bollard), 100 mm diameter, mounted at
z=1000 mm AFF (typical 1 m path bollard height).

| Bollard | x_mm | y_mm | Provenance tier |
|---|---|---|---|
| elv_bollard_1 | 3000 | 3000 | architectural_drawing_extraction |
| elv_bollard_2 | 7000 | 3000 | architectural_drawing_extraction |
| elv_bollard_3 | 11000 | 3000 | architectural_drawing_extraction |
| elv_bollard_4 | 5000 | 10000 | engineer_manual_entry |
| elv_bollard_5 | 10000 | 10000 | engineer_manual_entry |
| elv_bollard_6 | 15000 | 7500 | inferred_from_room_type |

This deliberately mixes all three `_extraction_source` tiers
(strongest, middle, weakest) to exercise INV-09 + the D-1
informational flag.

`_provenance_note` lengths: 165 / 159 / 159 / 188 / 167 / 195 chars
— all ≥40 per INV-09. Mixed-tier surfaced honestly via D-1 entry in
`_engineering_judgments[]`.

## Step 3 — Zone derivation (ELV barrier zones)

Per **spec §5.4 ELV barrier-zone convention**, each ELV bollard
generates an `elv_barrier_zone` = 500 mm radius cylinder around the
bollard, height 0 to 1500 mm AFF (covers the cable rise through the
1000 mm bollard plus a 500 mm tolerance).

Per **spec §5.7 geometry-validation convention**, each cylinder is
approximated by a 12-sided regular polygon. Vertices computed at
30° intervals from each bollard centroid with r=500.

Working through bollard 1 at (3000, 3000):

```
v_k = (3000 + 500·cos(k·30°), 3000 + 500·sin(k·30°))  for k = 0..11
```

- v_0  = (3000 + 500, 3000 + 0)    = (3500, 3000)
- v_1  = (3000 + 433, 3000 + 250)  = (3433, 3250)
- v_2  = (3000 + 250, 3000 + 433)  = (3250, 3433)
- v_3  = (3000 + 0,   3000 + 500)  = (3000, 3500)
- v_4  = (3000 - 250, 3000 + 433)  = (2750, 3433)
- v_5  = (3000 - 433, 3000 + 250)  = (2567, 3250)
- v_6  = (3000 - 500, 3000 + 0)    = (2500, 3000)
- v_7  = (3000 - 433, 3000 - 250)  = (2567, 2750)
- v_8  = (3000 - 250, 3000 - 433)  = (2750, 2567)
- v_9  = (3000 + 0,   3000 - 500)  = (3000, 2500)
- v_10 = (3000 + 250, 3000 - 433)  = (3250, 2567)
- v_11 = (3000 + 433, 3000 - 250)  = (3433, 2750)

Same template applied to bollards 2..6 — see `output.json` polygons.

### Overlap audit

Pairwise centre-to-centre distances and overlap check (sum of radii
= 1000 mm):

| Pair | Distance | Overlap? |
|---|---|---|
| 1↔2 | 4000 mm | no |
| 2↔3 | 4000 mm | no |
| 1↔3 | 8000 mm | no |
| 4↔5 | 5000 mm | no |
| 1↔4 | ≈7280 mm | no |
| 5↔6 | ≈5590 mm | no |
| (others) | all >5000 mm | no |

All zones isolated; `overlapping_with_zone_ids` empty on every zone.

## Step 4 — Electrical constraints (ELV separation)

Per BS 7671:2018 §715, ELV bollard circuits require:
1. ≥100 mm separation from LV (230 V) cabling OR a physical
   insulated barrier OR routing in a separate conduit.
2. Cable labelling so future maintainers do not confuse 12 V with
   230 V (banishing the "voltage assumption" failure mode).
3. The SELV isolating transformer must be short-circuit protected
   per BS EN 61558-2-6 §17 (transformer-secondary fault tolerance).

The single `elv_separation` constraint declares:

```
applies_to_room_polygon: true
applies_to_zone_ids: [all 6 barrier zones]
lv_cable_spacing_mm_min: 100
barrier_required: true
label_required: true
transformer_short_circuit_protected: true
_clause_citation: BS 7671:2018 §715 + BS EN 61558-2-6 (no §715 sub-clauses in verified file)
_elv_general_citation: BS 7671:2018 §715 + BS EN 61558-2-6 (no §715 sub-clauses in verified file)
```

The `_elv_general_citation` field is the schema-mandated honest
disclosure: no §715 sub-clauses are verified-file-valid, so the
constraint cites only the top-level §715 plus the
companion BS EN 61558-2-6.

**No banned sub-clauses** appear anywhere in this example — every
§715 reference is the verified top-level citation only.

## Step 5 — Existing fixtures audit

Six fixtures supplied — each is an `elv_luminaire` at the
corresponding bollard position:

| ID | x | y | z | IP | V | RCD | Zone |
|---|---|---|---|---|---|---|---|
| ext_elv_1 | 3000 | 3000 | 1000 | IPx5 | 12 | no | zone_elv_bollard_1_barrier |
| ext_elv_2 | 7000 | 3000 | 1000 | IPx5 | 12 | no | zone_elv_bollard_2_barrier |
| ext_elv_3 | 11000 | 3000 | 1000 | IPx5 | 12 | no | zone_elv_bollard_3_barrier |
| ext_elv_4 | 5000 | 10000 | 1000 | IPx5 | 12 | no | zone_elv_bollard_4_barrier |
| ext_elv_5 | 10000 | 10000 | 1000 | IPx5 | 12 | no | zone_elv_bollard_5_barrier |
| ext_elv_6 | 15000 | 7500 | 1000 | IPx5 | 12 | no | zone_elv_bollard_6_barrier |

For each fixture the four sub-rules check:
- **type_prohibited**: `elv_luminaire` is permitted (not in the
  prohibited list `["socket_230v", "luminaire_lv_non_selv"]`). PASS.
- **ip_below_min**: IPx5 meets `ip_rating_min: IPx4`. PASS.
- **switch_distance_too_close**: switch_position_min_distance_mm
  null on the zone → no constraint. PASS.
- **voltage_above_max**: 12 V matches `max_voltage_v: 12`. PASS.

All 6 fixtures `compliant`. The `is_rcd_protected: false` is
correct — SELV bypasses the §415.1 RCD obligation per §414.4
because the SELV barrier provides equivalent safety.

## Step 6 — Calculation summary

```
compliant: true
zone_count: 6
constraint_count: 1
violation_count_critical: 0
violation_count_high: 0
non_compliance_flags: []
```

Four assumptions recorded:
1. ELV barrier zone modelled as 500 mm radius cylinder per spec
   §5.4; 12-sided polygon per §5.7.
2. Ambient temperature missing — default 30°C per Appendix 4 Table
   4B1.
3. Bollard heights uniform 1000 mm; height_max=1500 mm covers cable
   rise + tolerance.
4. Single SELV isolating transformer sourced from indoor plant room.

Two `_engineering_judgments[]` entries:
- **D-5** (primary): missing ambient_temperature_c on an external
  installation. Default 30°C de-rating assumed; engineer-of-record
  to verify against site temperature data before sign-off.
- **D-1** (informational): bollard 6 sourced via
  `inferred_from_room_type` — weakest provenance tier. Engineer to
  verify final feature-tree position. Recorded for transparency
  even though D-5 is the primary trigger for this example.

## Step 7 — Invariant evaluation

| INV | Pass | Notes |
|---|---|---|
| INV-01 | ✓ | 6 anchors → 6 zones; all pairwise separations exceed 1000mm (sum of radii); no overlaps; no silent merges. |
| INV-02 | ✓ | 6 fixtures all compliant; non_compliance_flags[] empty. |
| INV-03 | ✓ | No Group 2 envelope → N/A vacuously passes. |
| INV-04 | ✓ | Not a bathroom/sauna → §701/§703 RCD blanket N/A. |
| INV-05 | ✓ | Not a pool hall → §702.415.1 N/A. |
| INV-06 | ✓ | No bath_basin → §701.512.2 whirlpool N/A. |
| INV-07 | ✓ | 6 elv_luminaire anchors → elv_separation constraint present with all 4 boolean obligations true (≥100mm + barrier + label + transformer SC-protected). _elv_general_citation honest-disclosure stamped. |
| INV-08 | ✓ | 6 fixtures inspected, all 4 sub-rules PASS for each. |
| INV-09 | ✓ | Mixed provenance tiers honestly disclosed (3 extracted + 2 manual + 1 inferred); all _provenance_note ≥40 chars. |
| INV-10 | ✓ | Self-consistency: compliant=true, no critical violations, D-flags only informational. |

## Step 8 — Honest disclosures

1. **§715 has no verified sub-clauses** — every zone citation and
   the constraint citation read
   "BS 7671:2018 §715 + BS EN 61558-2-6 (no §715 sub-clauses in
   verified file)". The spec §3.2 banned-list governs; none of the
   banned numbers are used anywhere in this example.
2. **Missing ambient temperature** is THE primary teaching of this
   example — external installations REQUIRE the engineer to verify
   ambient before locking down cable CSAs. D-5 flag fires loud and
   clear in `_engineering_judgments[]`.
3. **Mixed provenance tiers** (3 / 2 / 1 across the three enum
   values) are honestly surfaced via INV-09 + the D-1 informational
   note; this exercises the full anchor_source_summary distribution
   for downstream consumers.
4. **SELV bypasses RCD** — `is_rcd_protected: false` is the
   CORRECT setting for 12 V SELV per §414.4 (the SELV barrier
   provides the safety function that an RCD would otherwise
   provide on an LV circuit).

## Step 9 — Failure modes considered

- If `lv_cable_spacing_mm_min` were set <100 (e.g. 50 mm), the
  elv_separation constraint would FAIL and INV-07 would FAIL.
  Catalogued in the validator INV-07 spec.
- If `transformer_short_circuit_protected: false`, INV-07 would
  FAIL — the BS EN 61558-2-6 §17 obligation is non-negotiable.
- If a 230 V LV cable were laid within 100 mm of any barrier zone
  WITHOUT an insulated barrier, the cross-skill check would
  forward this as a non_compliance_flag from small-power or
  cable-containment back upstream.
- If `_elv_general_citation` were omitted, schema validation would
  FAIL (`required` list includes it) and the IR would be rejected
  by the gate.
- If `ambient_temperature_c` were supplied at e.g. 35°C, D-5 would
  NOT fire, and a Table 4B1 de-rating factor of ≈0.94 (PVC) or
  ≈0.96 (90°C TP) would apply — surfaced in
  `calculation_summary.assumptions[]` instead of as a reviewer flag.

## Step 10 — Cross-skill cascade preview

If a downstream `small-power` skill consumes this intent:
- `zones[]` x6 with `max_voltage_v: 12` and
  `prohibited_fixture_types: ["socket_230v", "luminaire_lv_non_selv"]`
  prevent any 230 V socket from being placed inside a bollard
  barrier zone.
- `electrical_constraints[]` x1 (`elv_separation`) drives the
  small-power cable schedule to call out ≥100 mm spacing + barrier
  + label per circuit.
- `compliant: true` and `non_compliance_flags: []` mean no cascade
  flags propagate upstream — but the consumer must surface the D-5
  reviewer flag in its own engineering judgment block because
  external ambient is a cross-skill design input.
- `anchor_source_summary.all_extracted: false` AND
  `extraction_source_lowest: inferred_from_room_type` — downstream
  D-1-style provenance gating will fire on the consumer side for
  bollard 6 specifically (any small-power circuit referencing
  bollard 6 should propagate the inferred-tier warning).
