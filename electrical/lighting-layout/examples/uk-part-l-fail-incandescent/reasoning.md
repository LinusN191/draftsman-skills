# Example: UK Part L Halogen Refurbishment FAIL — Reasoning

D3.C.2 failure-mode example #3. Demonstrates INV-6 critical FAIL on a
legacy UK office refurbishment with inherited 50W GU10 halogen downlights.
Lamp efficacy 15 lm/W ≪ 95 lm/W Approved Doc L (Part L 2021) §6 target,
plus no daylight-linking despite glazed W wall, plus no occupancy
detection — three severity=critical non_compliance_flags entries.
INV-10 composite FAIL. INV-1 still PASSes because the engineer
brute-force over-provisioned the fitting count.

## 1. Why this example exists

The end-to-end test surfaced a separate Part L failure mode: refurb
projects that inherit pre-2010 halogen estates often pass INV-1 (lux
target met) by sheer fitting density, hiding the underlying Part L
non-compliance. INV-6 catches that class of bug deterministically by
checking the four sub-checks (assessment + occupancy + daylight +
efficacy) independently of the lumen-method outcome.

This example shows the canonical inherited-halogen-estate refurb where:
- INV-1 PASSes (343 lux ≥ 300 lux target) ✓
- INV-6 FAILs on 3 of 4 sub-checks ✗
- INV-10 composite FAILs (non_compliance_flags populated) ✗

The cluster catches a real engineering risk: a project that ticks the
illuminance box but ships a non-compliant Part L assessment to the
warranty / handover pack.

## 2. Site brief

- Room: 8000 × 6000 mm UK private office, 2700 mm ceiling, 750 mm
  working plane (desk-based)
- Major refurbishment scope (cosmetic + M&E upgrade, not full strip-out)
- is_uk_new_build=true because major refurbishment triggers Part L 2021
  §6 per Approved Doc L Vol 2 §0.4
- Glazed W wall (existing window, retained)
- Single S-wall entrance (offset 3500 mm, width 900 mm,
  inward_latch_right)
- controls_protocol=switched (legacy single wall switch retained)
- Inherited luminaire: 50W GU10 halogen recessed downlight (750 initial
  lm, 2800K, CRI 100, IP20) — 50 fittings in 5×10 grid (1 per m²)

## 3. Lumen-method walk (PASS by brute-force fitting count)

```
Area A     = 8 × 6                          = 48 m²
Hm         = 2700 − 750                     = 1950 mm  = 1.95 m
RI         = (8 × 6) / (1.95 × (8 + 6))     = 48 / 27.3
                                            = 1.76
            → ontology table key 1.5 (next-lower band per LG7 §6.2)
UF         = 0.55  [LED_DOWNLIGHT ontology proxy @ RI=1.5, refs 0.7/0.5/0.2]
             (halogen GU10 shares similar 100 mm aperture + narrow beam
              optic with LED_DOWNLIGHT, so UF table is a reasonable proxy
              — engineer must confirm against the actual halogen file)
MF         = 0.80  (generous; halogen LLMF degrades faster than LED —
                    stricter assessment with MF=0.70 gives achieved 301
                    lux, still ≥ 300 but with no margin)
Engineer N = 50    (inherited halogen estate, 1 fitting per m² "wash"
                    density typical for pre-2010 halogen specifications)
Achieved   = (50 × 750 × 0.55 × 0.80) / 48
           = 16500 / 48                     = 343.75 lux
                                              ≥ 300 target  → INV-1 PASS
                                              14.6 % headroom

(For comparison: a principled LED redesign would reach 300 lux with
N=5 fittings @ 1000 lm × 100 lm/W — see remediation section.)
```

Reference: `[spacing-rules#lumen-method-formula]`, `[spacing-rules#room-index]`.

## 4. The Part L assessment — three critical failures (INV-6)

`inputs.new_build=true` AND `jurisdiction=england_wales` triggers Part L
2021 §6 enforcement. Sub-checks per validator.md INV-6:

| Sub-check | Required state                                            | Actual    | Result          |
|-----------|-----------------------------------------------------------|-----------|-----------------|
| 1         | controls.part_l_assessed == true                          | true      | PASS            |
| 2         | controls.required[] includes 'occupancy'                  | [] (no)   | **FAIL crit**   |
| 3         | glazed_walls=['west'] → daylight_linking required         | [] (no)   | **FAIL crit**   |
| 4         | controls.lamp_efficacy_lm_per_w ≥ 95                      | 15        | **FAIL crit**   |

Three of four sub-checks FAIL → Rule 6 FAIL. Per validator.md INV-6:
"emit non_compliance_flags entry with severity=critical AND set this
INV to FAIL" — three entries emitted, all severity=critical, all
reference Approved Doc L 2021 §6.

The honest reading: sub-check 1 (assessment ran) PASSes because the
engineer DID run the Part L check — they just got a fail on three
of four sub-checks. The assessment itself is the value-add; the
fitting-level fail is the assessment's deliverable.

## 5. Remediation — three changes for Part L sign-off

| # | Change                                          | Effort | Cost (50-fitting estate) | Savings                 |
|---|-------------------------------------------------|--------|--------------------------|-------------------------|
| 1 | GU10 LED retrofit lamps (8W/800lm/100 lm/W)     | Low    | ~£20/fitting × 50 = £1k  | 2100 W load cut (84 %)  |
| 2 | Split column 0 into perimeter zone Z1 + 0-10V dimming + photocell | Med | ~£800 + ~£200/fitting × 5 = £1.8k | Daylight savings (~30 %)|
| 3 | Add PIR occupancy sensor + override at SW01     | Low    | ~£500 (sensor + wire)    | Occupancy savings (~20 %)|

Total ~£3-5k. Payback period <2 years from energy savings alone:
2100 W × 2500 h/year × £0.30/kWh = £1575/year.

After remediation:
- (1) lamp_efficacy_lm_per_w becomes 100 → sub-check 4 PASS
- (2) controls.daylight_linking becomes true + perimeter zone declared
  → sub-check 3 PASS + INV-7 perimeter consistency PASS
- (3) controls.occupancy_sensing becomes true → sub-check 2 PASS
- All four sub-checks PASS → INV-6 PASS → controls.part_l_compliant
  becomes true → INV-10 composite PASSes

## 6. S/H ratio check (PASS — halogen wash density)

```
10 cols across 8 m  →  S_x = (8000 − 600) / 9 = 822 mm
5 rows across 6 m   →  S_y = (6000 − 600) / 4 = 1350 mm

Hm           = 1950 mm
SHR_max      = 1.4   (LED_DOWNLIGHT ontology default, narrow beam)
Limit        = SHR_max × Hm = 1.4 × 1950   = 2730 mm

S_x = 822 mm   ≤  2730 mm  → PASS (30 % of limit)
S_y = 1350 mm  ≤  2730 mm  → PASS (49 % of limit)
                                           → INV-2 PASS
```

The halogen wash density sits at ~30 % of S/H limit on the long axis —
the engineer-of-record could comfortably halve the fitting count after
the LED retrofit if they want to reset spacing to a principled S/H ratio.

## 7. Zone assignment (INV-7 PASS — INV-6 catches the perimeter gap)

All 50 luminaires in single Z2 interior zone with control='manual'.
`inputs.glazed_walls=['west']` non-empty, but `zones[]` contains NO
perimeter zone.

INV-7 Rule 3 wording: "if a zone has zone_type == 'perimeter', the
zone's luminaire positions must be within 6 m of a wall declared in
inputs.glazed_wall_positions. Conversely, if inputs.glazed_wall_positions
== [], NO zone may have zone_type == 'perimeter'."

The check is one-way: "perimeter zone declared → must match glazed wall"
+ "no glazed wall → no perimeter zone". It does NOT say "glazed wall
present → perimeter zone required". So a layout with glazed walls but
no perimeter zone PASSes INV-7 structurally.

The missing perimeter zone IS a Part L violation, surfaced by INV-6
sub-check 3 (daylight_linking absent). The cooperation pattern:

- INV-7 confirms no broken zone definitions exist
- INV-6 catches the regulatory requirement for daylight-linked control
- Together they form the full Part L 2021 §6 envelope without
  double-counting the same fail

## 8. Switch + circuit topology (INV-3 + INV-4 + INV-5 PASS)

Single S-wall entrance + controls_protocol=switched → 1 switch required,
1 emitted (SW01 1-gang at S latch side, x=3500, y=200, 1200 AFF).
INV-3 PASS.

5 row circuits on DB L1:

```
Circuit   Zone   Row   Luminaires       Load    MCB     Homerun
C-L01     Z2     0     L01..L10         500 W   6A B    (0, 300,  W)
C-L02     Z2     1     L11..L20         500 W   6A B    (0, 1650, W)
C-L03     Z2     2     L21..L30         500 W   6A B    (0, 3000, W)
C-L04     Z2     3     L31..L40         500 W   6A B    (0, 4350, W)
C-L05     Z2     4     L41..L50         500 W   6A B    (0, 5700, W)
```

INV-4: each circuit's `luminaire_ids` share single row_index → no
Z-pattern, PASS. Homeruns all on W wall.

INV-5: 500 W per circuit ≤ 1104 W (6A × 0.8 × 230) per BS 7671:2018+
A2:2022 §433.1.1 + IET OSG App A. 45 % of headroom — limiting factor
here is the inherited halogen lamp wattage, not the OCPD.

## 9. INV walkthrough

| INV    | Severity | Status | Evidence                                              |
|--------|----------|--------|-------------------------------------------------------|
| INV-01 | high     | PASS   | 343 lux ≥ 300 (brute-force fitting density 1/m²)      |
| INV-02 | high     | PASS   | S_x=822, S_y=1350 ≤ 2730 (SHR limit)                  |
| INV-03 | high     | PASS   | 1 entrance / 1 switch, latch, 1200 AFF                |
| INV-04 | high     | PASS   | 5 row circuits, no Z-pattern, homerun W               |
| INV-05 | high     | PASS   | 500 W per circuit ≤ 1104 W (6A 80 % cap, 45 %)        |
| INV-06 | high     | FAIL   | efficacy 15 ≪ 95 + no daylight + no occupancy         |
| INV-07 | medium   | PASS   | No perimeter zone declared (INV-6 catches the gap)    |
| INV-08 | medium   | PASS   | selection_source.ontology_default + halogen override  |
| INV-09 | medium   | PASS   | drafting_furniture complete, Arial 8/10 pt            |
| INV-10 | high     | FAIL   | non_compliance_flags×3 critical, compliant=false      |

2 of 10 INVs FAIL (INV-6 + INV-10 composite). The remaining 8 PASS
demonstrate that the lighting layout is structurally sound — the
fittings are correctly laid out, circuited, and switched. The only
issue is the inherited halogen specification + missing controls
automation, both caught by INV-6.

## 10. Engineer notes

- **Part L 2021 vs Part L 2013 transition**: Part L 2021 (in force
  15 June 2022) raised the efficacy target from 60 lm/W (2013) to
  95 lm/W (2021) for general office display lighting. A 2018 refurb
  might have used 60 lm/W target. A 2026 refurb uses 95 lm/W. The
  validator reads the current 95 lm/W from
  controls.part_l_efficacy_target_lm_per_w — adjust if running against
  an earlier Approved Doc L.
- **LLMF for halogen vs LED**: halogen lamps lose ~20 % output in the
  first 200 hours of burn-in, then stabilise. LED maintains output
  for thousands of hours. A formal LLMF assessment per CIBSE TM 3-25
  would use 0.70 for the halogen here vs 0.95 for the LED retrofit.
  The example uses MF=0.80 as a generous middle figure to keep the
  INV-1 PASS unambiguous.
- **CRI vs efficacy trade-off**: halogen CRI 100 is the strongest
  reason a designer might retain halogen (art galleries, retail, food
  service). For a private office CRI 80 (typical LED) is sufficient
  per BS EN 12464-1 Table 5.3 (Ra ≥ 80 for office). The retrofit
  doesn't degrade colour rendering meaningfully for this task.
- **Inherited dimming hardware**: the 50W halogen fittings likely have
  trailing-edge or leading-edge phase-cut dimmers. GU10 LED retrofit
  lamps are usually compatible with leading-edge dimmers but trailing-
  edge is preferred — survey the existing dimmer hardware before
  specifying the LED retrofit lamp to avoid flicker / buzz.
- **Existing transformer survey**: 50W GU10 halogen runs at mains
  voltage (230V GU10), no transformer in the circuit. If the inherited
  estate is actually MR16 12V halogen, the 12V toroidal transformer
  must be removed before fitting GU10 LED retrofit lamps — different
  base + different drive electronics. Survey the lamp base before
  ordering retrofits.
- **EPC / SBEM impact**: cutting 2100 W of connected lighting load
  improves the building's SBEM rating noticeably — for a 48 m²
  office reducing lighting energy consumption by 84 % is typically
  worth 5-10 EPC points. The refurb may push the building from EPC
  E to EPC C+, satisfying MEES 2023 letting requirements as a side
  effect.
- **Beyond INV-6**: the lighting-layout skill catches the fitting-level
  Part L gap. The full Part L sign-off also requires a SBEM Section 6
  calculation (out of scope for lighting-layout; lands in the
  energy-statement / compliance skill cluster — stubs already
  declared 2026-05-25).

## §D5 RETROFIT (2026-06-04)

This example was authored at v1.6.0 with a single `target_illuminance_lux`
per room. v1.7.0 splits target into per-zone `em_target_lux` per
BS EN 12464-1:2021 §4.2.2 + Table 6. This retrofit applies the
backwards-compatibility defaults — engineering content unchanged.

- Zone Z2 (the single "Interior" zone) takes `purpose: "task"`
  (ZP-01 default — the only valid mapping for a private_office room
  targeting 300 lx) and `em_target_lux: 300` (mirrors existing
  `calculation_summary.target_illuminance_lux`).
- All 50 GU10 halogen downlights take `mount_type: "recessed"`
  (MT-01 default — the fittings are recessed by physical definition);
  `z_mm` and `suspension_length_mm` remain omitted per the recessed
  convention (geometry inherits `room.ceiling_height_mm = 2700`).
- `per_zone_achieved[]` is populated with one entry for Z2:
  target 300 lx, achieved 343 lx, `ratio_compliance: "pass"`
  (room-level achievement maps directly to the single task zone —
  INV-19 PASS).
- INV-13..INV-19 appended to `invariants[]`. INV-13, INV-17, INV-18,
  INV-19 are non-vacuous PASS; INV-14, INV-15, INV-16 are vacuous
  PASS (no surrounding, no background, no pendant/suspended).

**Part-L FAIL state PRESERVED VERBATIM**

D5 additions (zone purpose + mount_type + per-zone achievement) are
ORTHOGONAL to Part L 2021 §6 efficacy/controls compliance:

| Item                                         | v1.6.0 state | After D5 retrofit | Reason                          |
|----------------------------------------------|--------------|-------------------|---------------------------------|
| `controls.part_l_compliant`                  | false        | false             | INV-6 fields untouched          |
| 3× critical `non_compliance_flags`           | present      | present           | Flag objects untouched          |
| INV-6 (efficacy + daylight + occupancy)      | FAIL         | FAIL              | Sub-checks evaluate same fields |
| INV-10 (composite)                           | FAIL         | FAIL              | Depends on INV-6                |
| INV-1 (lumen-method 343 ≥ 300)               | PASS         | PASS              | Calculation unchanged           |
| INV-11 (photometric cascade 564 ≥ 500)       | PASS         | PASS              | Cascade payload unchanged       |
| INV-19 (per-zone achievement Z2 343 ≥ 300)   | n/a          | PASS (new)        | Photometric, not regulatory     |

This example becomes the canonical demonstration that photometric
INV-19 PASS coexists with regulatory INV-6 FAIL — the layout meets
its 300 lx target by brute-force fitting count, but ships 2500 W of
connected lighting load against a 95 lm/W Part L efficacy target.
INV-6 catches the regulatory gap; INV-19 confirms the photometric
soundness; they do not double-count.

**Honest disclosures (4-place):**

1. Engineering judgement defaults documented in `input._d5_retrofit_note`.
2. `output.calculation_summary.assumptions[]` carries the v1.6.0 → v1.7.0
   retrofit explanation including the Part-L preservation statement.
3. `output.rationale.sections[]` includes a "v1.7 retrofit" section
   explaining ZP-01, MT-01, and the D5/Part-L orthogonality.
4. This `reasoning.md` §D5 RETROFIT section.

No engineering numbers were changed — the v1.6.0 lumen-method walk,
grid layout, circuit topology, controls state, and Part-L failure
verdict all remain identical. The retrofit is purely additive
metadata to align the example with the v1.7.0 zone-purpose /
mount-type schema while preserving the failure-mode pedagogy.
