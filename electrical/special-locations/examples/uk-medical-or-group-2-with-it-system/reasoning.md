# Reasoning — uk-medical-or-group-2-with-it-system

## Step 0 — Cascade prereq check

Standalone Group 2 operating room example. No upstream `lighting-layout`
intent consumed. 2 existing fixtures supplied directly +
`medical_it_system_override` supplied to drive the IT-system
constraint. Skill runs in `full_analysis` mode.

## Step 1 — Room classification

- `room.room_type = medical_group_2_theatre` → BS 7671:2018 §710
  applies, specifically Group 2 (life-support / surgical work area).
- Geometry: 6000 × 5000 mm theatre; area 30 m²; ceiling 3000 mm.
- Floor finish `vinyl` (typical conductive vinyl for operating
  theatres).
- `is_wet_room: false`, `is_external: false`.

## Step 2 — Anchor inventory

Single anchor: `patient_1`, a `medical_patient_position` at the room
centroid (3000, 2500) with `medical_group: 2` and `radius_mm: 1500`.
Position z=1000 mm AFF (operating table top).

Provenance: `architectural_drawing_extraction`, 173-char
`_provenance_note` recording the operating-table centroid and
equipment-schedule reference.

## Step 3 — Zone derivation (Group 2 patient envelope)

Per §710 Group 2 convention, the patient envelope is a **1.5 m radius
cylinder** centred on the patient position, extending vertically from
floor to 2500 mm AFF.

The schema stores zones as plan polygons (it cannot store a cylinder
primitive). Per **spec §5.7 geometry-validation convention**, cylinder
zones are approximated by a **12-sided regular polygon** (≥12 sides
mandated by the schema).

### Vertex computation

Centre (3000, 2500); r = 1500; 12 vertices at 30° intervals starting
from 0° (east). Computed values (rounded to nearest mm):

| i  | angle | x    | y    |
|----|-------|------|------|
| 0  | 0°    | 4500 | 2500 |
| 1  | 30°   | 4299 | 3250 |
| 2  | 60°   | 3750 | 3799 |
| 3  | 90°   | 3000 | 4000 |
| 4  | 120°  | 2250 | 3799 |
| 5  | 150°  | 1701 | 3250 |
| 6  | 180°  | 1500 | 2500 |
| 7  | 210°  | 1701 | 1750 |
| 8  | 240°  | 2250 | 1201 |
| 9  | 270°  | 3000 | 1000 |
| 10 | 300°  | 3750 | 1201 |
| 11 | 330°  | 4299 | 1750 |

`height_min_mm: 0`, `height_max_mm: 2500`.

## Step 4 — Per-zone safety properties

The Group 2 envelope sits OUTSIDE the §701 / §702 / §703 zoning
paradigm. Its key properties:

- `ip_rating_min: IPx4`.
- `max_voltage_v: 230` (the medical IT system delivers 230 V into the
  envelope at floating reference).
- **`rcd_required_ma: null`** — Group 2 explicitly REPLACES RCD
  protection with a medical IT (insulated) system per §710. An RCD on
  the IT system would trip on the first earth fault and lose life
  support during a procedure — the IMD instead raises an alarm.
- `prohibited_fixture_types[]` excludes non-medical 230 V sockets and
  switches and any TN-C circuit (the IT system requires reference
  isolation).
- `isolation_required: false` (the IT system handles isolation).

## Step 5 — Electrical constraint derivation

Two constraints (this is the FULL medical example):

### 5a — `medical_it_system`

Per **BS 7671:2018 §710** (top-level only — no §710 sub-clauses are
valid in the verified file) + **BS EN 61557-8** (IMD) + **HTM 06-01**
(NHS precedence).

All schema-required fields populated:

- `isolating_transformer_va_min: 5000` (from the input override; 5 kVA).
- `insulation_monitoring_device_required: true`.
- `imd_alarm_response_time_s_max: 8` (schema const; **NOT 0.5 s** —
  that was a prior misattribution corrected during the brainstorm).
- `safety_service_category: 1` (from HTM 06-01, NOT BS 7671 — the
  schema's description field calls this out explicitly).
- `supplementary_bonding_required: true`.
- `supplementary_bonding_max_resistance_ohm: 0.2` (schema const, per
  §710).
- `hospital_precedence: "HTM 06-01"`.
- `equipment_standard: "BS EN 60601 series"`.
- `_verified_cross_refs: ["BS EN 61557-8", "HTM 06-01", "BS EN 60601"]`.

### 5b — `supplementary_equipotential_bonding`

Per **§710 + §701.415.2** (§710 directs to §701.415.2 bonding rules).

- `metallic_parts_listed`: operating table frame, anaesthesia machine
  ground, scrub sink, surgical pendant arm, patient monitor chassis.
- `bonding_conductor_csa_min_mm2: 4` (typical for medical patient
  environment).

The supplementary-bonding resistance was measured at 0.15 Ω (input
override), below the 0.2 Ω max.

## Step 6 — Existing-fixture audit

Two fixtures supplied:

1. **`surg_lum_1` — surgical_luminaire, IPX2, 230 V, NOT RCD-protected, at (3000, 2500, 3000)**
   - Ceiling-mounted at z=3000 mm (room ceiling). Sits ABOVE the
     2500 mm envelope ceiling — `derived_zone_id: null`.
   - Surgical luminaires are medical-equipment-of-trade per HTM 06-01
     with IT-system feed bypassing RCD; the no-RCD is correct.
   - IPx2 is below the envelope's IPx4 min, but since the fixture is
     OUTSIDE the envelope, the zone IP rule does not apply.
   - **compliant**.

2. **`iso_socket_1` — medical_isolating_socket, IPX4, 230 V, NOT RCD-protected, at (4500, 2500, 1100)**
   - Position (4500, 2500) is exactly at vertex 0 of the envelope
     polygon → inside (or on boundary) of the envelope.
   - z=1100 mm < 2500 mm envelope ceiling → inside the envelope.
   - `derived_zone_id: zone_patient_1_envelope_g2`.
   - Type `medical_isolating_socket` NOT in
     `prohibited_fixture_types[]` (the prohibition is on
     `socket_230v_non_medical`).
   - IPx4 ≥ IPx4 min; voltage 230 V ≤ 230 V; not a switch; no RCD is
     correct (IT system replaces RCD).
   - **compliant**.

`existing_fixtures_audit[]` has 2 compliant entries;
`non_compliance_flags[]` empty.

## Step 7 — Invariant evaluation (10 INVs)

| INV    | Outcome | Notes                                                                |
|--------|---------|----------------------------------------------------------------------|
| INV-01 | PASS    | 1 anchor → 1 zone; no overlaps                                       |
| INV-02 | PASS    | 0 violations both sides                                              |
| INV-03 | PASS    | Group 2 zone present + medical_it_system constraint with applies_to_zone_ids matching + IMD const 8 + supp bonding const 0.2 |
| INV-04 | PASS    | not bath/shower/sauna (vacuous)                                      |
| INV-05 | PASS    | not pool (vacuous)                                                   |
| INV-06 | PASS    | no bath (vacuous)                                                    |
| INV-07 | PASS    | no ELV anchor (vacuous)                                              |
| INV-08 | PASS    | 2 fixtures compliant (surgical luminaire outside envelope; medical isolating socket inside) |
| INV-09 | PASS    | architectural extraction; provenance 173 chars                       |
| INV-10 | PASS    | compliant=true; 0 critical violations                                |

`calculation_summary.compliant: true`.

Additionally, the schema's `allOf` second `if/then` (Group 2 zone ⇒
medical_it_system constraint) is satisfied — INV-03 is enforced at
both schema level AND validator level.

## Step 8 — Assumptions recorded

Three assumptions in `calculation_summary.assumptions[]`:

1. Group 2 patient envelope approximated as 12-sided regular polygon
   (1.5 m radius cylinder) per spec §5.7 geometry-validation
   convention.
2. Isolating transformer sized at 5 kVA per input
   medical_it_system_override; within the 3.15-8 kVA plausibility
   band so no D-4 flag is raised.
3. Safety service category 1 (no-break) sourced from HTM 06-01 NHS
   technical memorandum, NOT from BS 7671 §710 (no such sub-clause
   exists in the verified file).

## Step 9 — Reviewer D-checks

- **D-1** — patient_1 is architectural extraction.
- **D-2** — not a pool zone.
- **D-3** — no whirlpool bath.
- **D-4** — `isolating_transformer_va_min = 5000` is INSIDE the
  3.15-8 kVA plausibility band (5000 > 3150 AND 5000 < 8000) →
  **D-4 NOT raised** (intentionally suppressed by the band check).
- **D-5** — `is_external=false`; no ELV anchor.

`_engineering_judgments: []`.

## Step 10 — Honest disclosures

1. **The 8 s IMD alarm response is the BS EN 61557-8 figure** (not
   0.5 s — the latter was a prior misattribution corrected at
   brainstorm). The schema's `imd_alarm_response_time_s_max` is
   declared as `const: 8` to make this audit-visible.
2. **`safety_service_category: 1` is from HTM 06-01**, not BS 7671.
   The schema's description field calls this out explicitly. NHS
   sites take HTM 06-01 precedence per the `hospital_precedence`
   field.
3. **No §710 sub-clauses are valid in the verified BS 7671 file.**
   Citations route through generic `§710` + the BS EN 61557-8 / HTM
   06-01 cross-references. The spec §3.2 banned-list governs the
   excluded §710 sub-clause numbers.
4. **Surgical-luminaire non-RCD feed is correct** under §710 IT-system
   architecture and HTM 06-01 medical-equipment-of-trade allowance —
   not a violation.

## Step 11 — Intent payload emission

Emitted `special_locations_zoning` intent contains the Group 2
envelope + both constraints + `compliant: true` +
`anchor_source_summary.all_extracted: true`. The downstream `db-layout`
consumer reads the medical_it_system constraint to route the IT
distribution board correctly (and exclude the envelope from the RCD
allocation pass).

## Step 12 — Compliance verdict

`compliant: true`. This is the full medical Group 2 IT-system example.
INV-03 PASSES with all three sub-conditions satisfied:

- medical_envelope_group_2 zone present;
- medical_it_system constraint binds to that zone;
- imd_alarm_response_time_s_max = 8 AND
  supplementary_bonding_max_resistance_ohm = 0.2.

D-4 is intentionally suppressed (5 kVA in band).

## Citation hygiene check

- `BS 7671:2018 §710` ✓ (verified, top-level only)
- `BS 7671:2018 §701.415.2` ✓ (verified — bonding rules referenced
  from §710)
- `BS EN 61557-8` ✓ (verified cross-reference)
- `HTM 06-01` ✓ (verified cross-reference)
- `BS EN 60601` ✓ (verified cross-reference)

NOT used: any §710 sub-clause on the spec §3.2 banned-list (the
verified citation table excludes those numbers — §710 cites
top-level only with named cross-references above).
