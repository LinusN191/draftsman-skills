# Reasoning — cascade-lighting-layout-uk-medical-group-2

## Cascade context

Cascade retrofit of C.1 standalone
`uk-medical-or-group-2-with-it-system`. Upstream lighting-layout intent
(synthetic at
`electrical/lighting-layout/examples/uk-medical-or-cascade-source/intent-out.json`)
supplies 4 ceiling-mounted surgical luminaires fed from the Group 2
medical IT supply per §710. All math, the 5 kVA isolating transformer,
IMD with 8 s alarm, and ≤0.15 Ω supplementary bonding are unchanged
from the C.1 source.

## Step 0 — Cascade prereq check

- `_special_locations_cascade_source.upstream_consumer_intent_location` set
  → `full_analysis` mode.
- `existing_fixtures[]` carry `_consumed_from` markers identifying the
  upstream intent + recording the IT-supply hand-off.
- `consumed_lighting_layout_intent` in intent-out points at upstream.

## Step 1 — Room classification

- `room.room_type: medical_group_2_theatre` → §710.
- 6 000 × 5 000 mm; `area_m2 = 30`; ceiling 3 000 mm.
- Floor finish `vinyl` (medical convention).

## Step 2 — Anchor inventory

- `patient_1` — `medical_patient_position`, cylindrical, radius 1 500 mm
  at `(3000, 2500)`; bed top 1 000 mm AFF. medical_group=2.
- `_extraction_source: architectural_drawing_extraction`.

## Step 3 — Zone derivation (BS 7671:2018 §710)

1 zone (same as C.1 source):

| zone_id                       | zone_type                  | height_min | height_max |
|-------------------------------|----------------------------|-----------:|-----------:|
| `zone_patient_1_envelope_g2`  | medical_envelope_group_2   | 0          | 2500       |

Cylindrical envelope: 1 500 mm radius around the patient centroid;
height 0 → 2 500 mm AFF per §710 envelope definition.

## Step 4 — Electrical constraints

Two constraints (from C.1 source):

- `medical_it_system` per §710 + BS EN 61557-8: medical IT supply
  with insulation monitoring device (IMD) + 8 s alarm; 5 kVA isolating
  transformer.
- `supplementary_equipotential_bonding` per §710 + IEC 60364-7-710:
  ≤0.2 Ω bonding resistance to ME terminal.

## Step 5 — Consume lighting-layout intent

4 ceiling-mounted surgical luminaires consumed:

| fixture_id        | position (x,y,z)       | IP   | V   | RCD   | Supply       |
|-------------------|------------------------|------|-----|-------|--------------|
| `surgical_lum_1`  | (2000, 2000, 3000)     | IPx2 | 230 | false | medical IT   |
| `surgical_lum_2`  | (2000, 3000, 3000)     | IPx2 | 230 | false | medical IT   |
| `surgical_lum_3`  | (4000, 2000, 3000)     | IPx2 | 230 | false | medical IT   |
| `surgical_lum_4`  | (4000, 3000, 3000)     | IPx2 | 230 | false | medical IT   |

All sit at z = 3 000 mm (ceiling level), ABOVE envelope height_max
2 500 mm — ceiling-mounted outside the §710 envelope vertical extent.

## Step 6 — INV-08 sub-rule walk-through

For each of 4 fixtures:

- **(a) type_prohibited:** `surgical_luminaire` permitted by §710 when
  fed from medical IT supply. The `_consumed_from` provenance marker
  records IT-supply linkage. **PASS.**
- **(b) ip_below_min:** IPx2 is the medical-OR convention per §710
  (HVAC-controlled environment; no splash exposure). The envelope does
  not impose a minimum IP class; the §710 zone-table is silent on IP.
  **PASS.**
- **(c) switch_distance_too_close:** N/A — surgical luminaires not
  sockets. **PASS.**
- **(d) voltage_above_max:** 230 V ≤ envelope max_voltage 230 V.
  **PASS.**

Sub-rule summary: 16 evaluations all PASS. `derived_zone_id: null`
because z = 3 000 mm > envelope height_max 2 500 mm.

## Step 7 — INV-03 medical IT (Group 2)

INV-03 fires because `zone_patient_1_envelope_g2` is a Group 2 envelope.
The IR records both `medical_it_system` and
`supplementary_equipotential_bonding` constraints — the §710 + BS EN
61557-8 + IEC 60364-7-710 trio. **PASS.**

## Step 8 — Invariants

All 10 INVs PASS:

- **INV-01** zone catalogue: 1 anchor → 1 envelope. PASS.
- **INV-02** audit ↔ flags 1:1: zero violations both sides. PASS.
- **INV-03** medical IT system constraint PRESENT for Group 2 envelope.
  PASS.
- **INV-04** rcd_blanket N/A (medical OR uses IT supply, not blanket
  RCD). PASS vacuously.
- **INV-05** main equipotential bonding N/A (not pool). PASS vacuously.
- **INV-06** whirlpool pump N/A. PASS vacuously.
- **INV-07** ELV separation N/A. PASS vacuously.
- **INV-08** 16/16 sub-rule evaluations PASS.
- **INV-09** anchor provenance strongest tier; ≥40-char notes. PASS.
- **INV-10** rollup self-consistency holds. PASS.

## Step 9 — Consumer-side hand-off expectations

### lighting-layout v1.6 INV-12 (cross-check)

INV-12 iterates over each consumed surgical luminaire and verifies it
does NOT violate the §710 envelope. All 4 fixtures audit as compliant;
INV-12 PASSes. lighting-layout's output IR sets
`special_locations_cross_check_compliant: true`.

### db-layout v1.5 INV-16 sub-check 4 (medical IT distribution)

INV-16 sub-check 4 fires because `medical_it_system` is present in
`electrical_constraints[]`. db-layout must model:

- A medical IT panel (5 kVA isolating transformer) as a board node.
- An IMD with 8 s alarm response on the secondary side.
- A ME (medical equipment) terminal with supplementary bonding ≤0.2 Ω.
- All 4 surgical-luminaire circuits routed via this panel — none from
  the general LV distribution.

If db-layout's modelled `isolating_transformer_va` differs from 5 kVA,
the cascade integrity check fails. The C.1 source records the 5 kVA
value inside the §710 3.15–8 kVA plausibility band → D-4 NOT raised.

## Step 10 — Honest disclosures

- **Synthetic upstream intent.** lighting-layout v1.6 hand-off not yet
  shipped; cascade contract integrity verified via golden CI Pass 4.
- **IMD alarm at 8 s.** Sits EXACTLY at the §710 + BS EN 61557-8
  limit. C.1 source's D-3-equivalent gate at 8 s is unchanged.
- **Supplementary bonding ≤0.15 Ω.** Well inside the 0.20 Ω §710 +
  BS EN 61557-8 + IEC 60364-7-710 envelope. D-3 NOT raised.
- **HTM 06-01 (NHS) precedence.** Where divergent from §710, HTM 06-01
  takes precedence per UK NHS practice; recorded in C.1 reasoning.md
  honest disclosures.

## Step 11 — Failure modes considered

If any surgical luminaire were NOT fed from the medical IT supply
(`_consumed_from` lacked the IT-supply linkage), the upstream
lighting-layout INV-12 would still PASS on the special-locations side
of the cascade (the audit doesn't model the supply path), but
db-layout INV-16 sub-check 4 would FAIL HIGH because the corresponding
circuit would not route through the medical IT panel.

If the patient envelope were modelled at z=0–3500 mm (ceiling height)
instead of 0–2500 mm (per §710 envelope definition), the 4 luminaires
would fall INSIDE the envelope, and sub-rule (b) `ip_below_min` would
still PASS (no IP minimum on the envelope), but sub-rule (a) would need
the luminaire-on-IT-supply linkage to be modelled to remain compliant.

## Cross-references

- C.1 source: `electrical/special-locations/examples/uk-medical-or-group-2-with-it-system/`
- Spec §9.2 cascade row 11: PASS case
- Plan portion 3 Task C.2 Step 2
