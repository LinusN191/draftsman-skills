# Reasoning — cascade-small-power-uk-medical-group-2-isolation

## Cascade context

Cascade retrofit of C.1 standalone
`uk-medical-or-group-2-with-it-system` for the **small-power consumer**.
Upstream small-power intent (synthetic at
`electrical/small-power/examples/uk-medical-or-cascade-source/intent-out.json`)
supplies 6 `medical_isolating_socket` positions fed from the Group 2
medical IT supply via `isolation_path: medical_it_panel`.

The math, the 5 kVA isolating transformer, IMD with 8 s alarm, and
≤0.15 Ω supplementary bonding are unchanged from the C.1 source.

## Step 0 — Cascade prereq check

- `_special_locations_cascade_source.upstream_consumer_intent_location` set
  → `full_analysis` mode.
- `existing_fixtures[]` carry `isolation_path: medical_it_panel`
  markers recording the IT-supply hand-off (the central engineering
  value of this cascade).
- `consumed_lighting_layout_intent` in intent-out points at upstream
  small-power (the intent schema currently uses a single
  `consumed_lighting_layout_intent` field; for small-power consumers
  the path resolves to the small-power upstream intent, with the
  consumer skill recorded in the input's
  `_special_locations_cascade_source` block).

## Step 1 — Room classification

Identical to C.1 source: `medical_group_2_theatre`; 6 000 × 5 000 mm;
ceiling 3 000 mm; floor `vinyl`.

## Step 2 — Anchor inventory

Identical to C.1 source: 1 anchor `patient_1`
(`medical_patient_position`) cylindrical r=1500 mm at `(3000, 2500)`.

## Step 3 — Zone derivation (BS 7671:2018 §710)

1 envelope:

| zone_id                       | zone_type                  | height_min | height_max |
|-------------------------------|----------------------------|-----------:|-----------:|
| `zone_patient_1_envelope_g2`  | medical_envelope_group_2   | 0          | 2500       |

Same as C.1 source. Cylindrical, radius 1 500 mm.

## Step 4 — Electrical constraints

Same as C.1 source: `medical_it_system` (§710 + BS EN 61557-8) and
`supplementary_equipotential_bonding` (§710 + IEC 60364-7-710).

## Step 5 — Consume small-power intent

6 medical isolating sockets at z = 1 100 mm (typical OR socket height,
inside envelope vertical extent 0–2 500 mm):

| fixture_id       | position (x,y,z)       | IP   | V   | isolation_path     |
|------------------|------------------------|------|-----|--------------------|
| `med_socket_1`   | (1000, 1000, 1100)     | IPx4 | 230 | medical_it_panel   |
| `med_socket_2`   | (1000, 4000, 1100)     | IPx4 | 230 | medical_it_panel   |
| `med_socket_3`   | (5000, 1000, 1100)     | IPx4 | 230 | medical_it_panel   |
| `med_socket_4`   | (5000, 4000, 1100)     | IPx4 | 230 | medical_it_panel   |
| `med_socket_5`   | (3000, 500,  1100)     | IPx4 | 230 | medical_it_panel   |
| `med_socket_6`   | (3000, 4500, 1100)     | IPx4 | 230 | medical_it_panel   |

All 6 sockets sit OUTSIDE the 1 500 mm radius envelope cylinder in plan.
Minimum distance to envelope edge ≈ 1 500 mm at the closest socket
(`med_socket_5` at (3000, 500); envelope edge at (3000, 1000)). The
envelope does not impose a distance rule on sockets when they are
fed from the medical IT supply — the IT supply IS the safety barrier.

## Step 6 — INV-08 sub-rule walk-through (the cascade core)

For each of 6 sockets:

- **(a) type_prohibited:** `medical_isolating_socket` permitted by §710
  when on medical IT supply (`isolation_path: medical_it_panel` records
  this hand-off). General `socket_230v` fed from LV would be
  prohibited in/near the Group 2 envelope; this socket type is the
  §710-compliant alternative. **PASS.**
- **(b) ip_below_min:** IPx4 (cleanable OR convention; the §710
  zone-table is silent on IP minimum for the envelope; clean-room
  surface convention IPx4). **PASS.**
- **(c) switch_distance_too_close:** N/A — envelope does not impose a
  distance rule on IT-supply-fed sockets. **PASS.**
- **(d) voltage_above_max:** 230 V ≤ envelope max_voltage 230 V.
  **PASS.**

Sub-rule summary: 24 evaluations (6 fixtures × 4 sub-rules) all PASS.
`derived_zone_id: null` for all 6 because they sit outside the envelope
in plan.

## Step 7 — INV-03 medical IT (Group 2)

`zone_patient_1_envelope_g2` is a Group 2 envelope. The IR records
both `medical_it_system` and `supplementary_equipotential_bonding`
constraints. **PASS.**

## Step 8 — Invariants

All 10 INVs PASS:

- **INV-01** zone catalogue: 1 anchor → 1 envelope. PASS.
- **INV-02** audit ↔ flags 1:1: zero violations both sides. PASS.
- **INV-03** medical IT system constraint PRESENT. PASS.
- **INV-04** rcd_blanket N/A. PASS vacuously.
- **INV-05** N/A. PASS vacuously.
- **INV-06** N/A. PASS vacuously.
- **INV-07** N/A. PASS vacuously.
- **INV-08** 24/24 sub-rule evaluations PASS.
- **INV-09** anchor provenance strongest tier. PASS.
- **INV-10** rollup self-consistency holds. PASS.

## Step 9 — Consumer-side hand-off expectations

### small-power v1.2 INV-12 (socket zone-exclusion + isolation)

INV-12 has two sub-checks on the small-power side:

1. **Zone exclusion** — verify no socket is placed inside a derived
   zone polygon where its `type_prohibited` would fire. All 6 sockets
   sit outside the envelope in plan; PASS.
2. **Isolation enforcement** — for sockets near/inside the Group 2
   envelope, verify `isolation_path` carries the medical IT supply
   linkage. All 6 sockets record `isolation_path: medical_it_panel`;
   PASS.

### db-layout v1.5 INV-16 sub-check 4 (medical IT distribution)

db-layout must model:

- 5 kVA isolating transformer as the medical IT panel root.
- IMD with 8 s alarm response on the secondary side.
- ME terminal with supplementary bonding ≤0.2 Ω.
- All 6 socket circuits routed via this panel — every circuit's
  upstream protective device traces back to the medical IT panel, not
  the general LV board.

If db-layout's modelled `isolating_transformer_va` ≠ 5 kVA, INV-16
sub-check 4 fails. The C.1 source records 5 kVA within the §710
3.15–8 kVA plausibility band → D-4 NOT raised.

## Step 10 — Honest disclosures

- **Synthetic upstream intent.** small-power v1.2 hand-off not yet
  shipped; cascade contract integrity verified via golden CI Pass 4.
- **isolation_path field.** Recorded on each socket entry; small-power
  v1.2 surfaces this in its own INV-12 sub-check 2.
- **Socket height 1 100 mm.** Typical OR convention (above anaesthetic
  machine impact-protection band 0–500 mm).
- **medical_isolating_socket type.** Distinct from `socket_230v` —
  §710 explicitly permits this fixture type when fed from the IT
  supply. General `socket_230v` from LV would be prohibited in/near
  the Group 2 envelope per §710 zone-table.

## Step 11 — Failure modes considered

- If `isolation_path` were NULL or pointed at the general LV board,
  small-power INV-12 sub-check 2 would FAIL HIGH, propagating a
  non_compliance_flag with severity=critical and clause = BS 7671:2018
  §710.
- If a `socket_230v` (general LV) were placed INSIDE the envelope
  cylinder, sub-rule (a) `type_prohibited` would fire and the cascade
  compliance verdict would flip to false.

## Cross-references

- C.1 source: `electrical/special-locations/examples/uk-medical-or-group-2-with-it-system/`
- Spec §9.2 cascade row 13: PASS case
- Plan portion 3 Task C.2 Step 4
