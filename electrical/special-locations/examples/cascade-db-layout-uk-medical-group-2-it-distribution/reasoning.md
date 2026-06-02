# Reasoning — cascade-db-layout-uk-medical-group-2-it-distribution

## Cascade context

Cascade retrofit of C.1 standalone
`uk-medical-or-group-2-with-it-system` for the **db-layout consumer**.
Upstream db-layout intent (synthetic at
`electrical/db-layout/examples/uk-medical-or-cascade-source/intent-out.json`)
models a **Medical IT panel** as a board node — 5 kVA isolating
transformer per §710, IMD with 8 s alarm per BS EN 61557-8, ME
terminal with supplementary bonding ≤0.15 Ω per IEC 60364-7-710.

All medical_isolating_socket and surgical_luminaire circuits route via
this panel; **none from general LV distribution**.

## Step 0 — Cascade prereq check

- `_special_locations_cascade_source.upstream_consumer_intent_location` set
  → `full_analysis` mode.
- `existing_fixtures[]` carry `isolation_path: medical_it_panel` markers
  recording the IT-supply linkage.
- `consumed_lighting_layout_intent` in intent-out points at upstream
  db-layout (single field; consumer skill recorded via
  `_special_locations_cascade_source.consumer_skill: db-layout`).

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

## Step 4 — Electrical constraints

Same as C.1 source: `medical_it_system` (§710 + BS EN 61557-8) and
`supplementary_equipotential_bonding` (§710 + IEC 60364-7-710).

## Step 5 — Consume db-layout intent

2 representative fixtures consumed (1 socket + 1 surgical luminaire);
both `_consumed_from` records the upstream db-layout circuit's routing
via `medical_it_panel`:

| fixture_id          | type                        | isolation_path     |
|---------------------|-----------------------------|--------------------|
| `med_socket_1`      | medical_isolating_socket    | medical_it_panel   |
| `surgical_lum_1`    | surgical_luminaire          | medical_it_panel   |

## Step 6 — INV-08 sub-rule walk-through

Per cascade #13 (sockets) + cascade #11 (surgical luminaires) sub-rule
treatments:

- `med_socket_1` at (1000, 1000, 1100) — sits outside the 1 500 mm
  radius envelope cylinder in plan. 4 sub-rules PASS.
- `surgical_lum_1` at (3000, 2500, 3000) — sits at envelope centroid in
  plan, ABOVE envelope max-height 2 500 mm. 4 sub-rules PASS.

8 sub-rule evaluations all PASS. `derived_zone_id: null` for both.

## Step 7 — Consumer-side hand-off — db-layout INV-16 sub-check 4 (the cascade core)

db-layout v1.5 INV-16 sub-check 4 (medical IT distribution) iterates
over the db-layout output IR and verifies:

1. **Panel node exists.** A `medical_it_panel` board node exists, with
   `isolating_transformer_va` inside the §710 plausibility band
   3.15–8 kVA.
2. **IMD modelled.** The IT panel has an associated IMD with
   `alarm_response_time_s` ≤ 8 (per BS EN 61557-8).
3. **All Group 2 circuits route via the panel.** Every circuit serving a
   Group 2 envelope fixture has its upstream protective device tracing
   back to the medical_it_panel (NOT general LV distribution board).
4. **ME terminal modelled.** A ME (medical equipment) terminal exists
   with `supplementary_bonding_resistance_ohm` ≤ 0.20 per IEC
   60364-7-710.

For this cascade:

| sub-check | modelled value           | spec limit             | result |
|-----------|--------------------------|------------------------|--------|
| (1) panel | 5 kVA                    | 3.15–8 kVA             | PASS   |
| (2) IMD   | 8 s alarm                | ≤ 8 s                  | PASS   |
| (3) routing | both circuits via panel | all-via-panel required | PASS   |
| (4) ME    | 0.15 Ω                   | ≤ 0.20 Ω               | PASS   |

**All 4 sub-checks PASS.**

## Step 8 — Invariants

All 10 INVs PASS:

- **INV-01** zone catalogue: 1 anchor → 1 envelope. PASS.
- **INV-02** audit ↔ flags 1:1: 2 entries, zero violations. PASS.
- **INV-03** medical IT system constraint PRESENT for Group 2 envelope.
  PASS.
- **INV-04** rcd_blanket N/A (medical OR uses IT supply, not blanket
  RCD). PASS vacuously.
- **INV-05** main equipotential bonding N/A (not pool). PASS vacuously.
- **INV-06** whirlpool pump N/A. PASS vacuously.
- **INV-07** ELV separation N/A. PASS vacuously.
- **INV-08** 8/8 sub-rule evaluations PASS.
- **INV-09** anchor provenance strongest tier. PASS.
- **INV-10** rollup self-consistency holds. PASS.

## Step 9 — Honest disclosures

- **Synthetic upstream db-layout intent.** v1.5 hand-off not yet shipped.
  Cascade contract integrity verified via golden CI Pass 4.
- **5 kVA inside plausibility band.** §710 specifies 3.15–8 kVA
  isolating transformer. 5 kVA = mid-band; D-4 NOT raised in C.1 source,
  carried forward unchanged.
- **IMD alarm at 8 s = spec limit.** Per §710 + BS EN 61557-8. The
  C.1 source's D-3-equivalent gate at 8 s is unchanged.
- **Supplementary bonding ≤0.15 Ω.** Well inside the 0.20 Ω §710 + BS EN
  61557-8 + IEC 60364-7-710 envelope. D-3 NOT raised.
- **HTM 06-01 (NHS) precedence.** Where divergent from §710, HTM 06-01
  takes precedence per UK NHS practice; recorded in C.1 honest
  disclosures.

## Step 10 — Failure modes considered

If db-layout's modelled `isolating_transformer_va` were 2 500 (below
3.15 kVA lower band) or 10 000 (above 8 kVA upper band), INV-16
sub-check 4 (sub-check 1) would FAIL HIGH with severity=critical and
clause = `BS 7671:2018 §710`.

If any Group 2 envelope circuit were routed from general LV (NOT via
the medical_it_panel), INV-16 sub-check 4 (sub-check 3) would FAIL HIGH
with severity=critical and clause = `BS 7671:2018 §710`. The
non_compliance_flag would carry `_cascaded_from: special-locations`.

If the IMD alarm response exceeded 8 s, INV-16 sub-check 4 (sub-check 2)
would FAIL HIGH with severity=critical and clause = `BS EN 61557-8` +
`BS 7671:2018 §710`.

If the ME terminal supplementary bonding resistance exceeded 0.20 Ω,
INV-16 sub-check 4 (sub-check 4) would FAIL HIGH with clause =
`IEC 60364-7-710` + `BS 7671:2018 §710`.

## Cross-references

- C.1 source: `electrical/special-locations/examples/uk-medical-or-group-2-with-it-system/`
- Spec §9.2 cascade row 16: PASS case
- Plan portion 3 Task C.2 Step 6
