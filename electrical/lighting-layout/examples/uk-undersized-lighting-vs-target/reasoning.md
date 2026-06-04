# Example: UK Undersized Lighting vs Target — Reasoning

D3.C.2 failure-mode example #1. Demonstrates the most common LLM-driven
lighting-layout bug — under-provision by value-engineered luminaire swap
without re-running the lumen method. Three of ten INVs FAIL deliberately
so the few-shot library covers a non-happy path.

## 1. Why this example exists

The end-to-end test that motivated Sprint D3 produced a `482 lux ≥ 500`
"compliant" CAD output — the model had round-to-nearest'd a 16-fitting
result down to 15 and shipped the failure as a pass. INV-1 was added to
catch that class of bug deterministically. This example pushes the same
button harder — engineer specified 3500 lm panels in a 12-fitting layout
for a 500 lux target. Achieved 434 lux. INV-1 fires HIGH, INV-6 also
fires (Part L assessment skipped on a new-build), and INV-10 composite
flags the populated `non_compliance_flags` array.

The companion clean example (uk-multi-entrance-classroom) and the
canonical re-test (uk-open-plan-office-10x8-dali, lands in C.3) cover
the happy path. Together the three new C.2 examples + the three
existing v1.4 examples give the few-shot library coverage of both
PASS and FAIL states across all ten INVs.

## 2. Site brief

- Room: 8000 × 5000 mm UK private office, 2700 mm finished ceiling
- Working plane 750 mm (BS EN 12464-1 Table 5.3 — desk-based office)
- Target maintained illuminance 500 lux (private_office task category)
- UGR ≤ 19 (confirm from photometric data)
- UK new-build → Part L 2021 §6 applies
- No glazing (interior room)
- Single S-wall entrance, inward-opening latch-right door
- Controls protocol: DALI (single master switch at the entrance)
- Engineer specification: 12 × LED_PANEL_600 @ 3500 lm in 4×3 grid
  (under-spec'd 3500 lm variant — canonical LED_PANEL_600 is 4500 lm)

## 3. Lumen-method walk (corrected)

```
Area A     = 8 × 6                          = 48 m²
Hm         = 2700 − 750                     = 1950 mm  = 1.95 m
RI         = (8 × 6) / (1.95 × (8 + 6))     = 48 / 27.3
                                            = 1.76
            → ontology table key 1.5 (next-lower band per LG7 §6.2)
UF         = 0.62  [LED_PANEL_600 @ RI=1.5, reflectances 0.7/0.5/0.2]
             (ontology source: CIBSE LG7 §6.2 + BS EN 12464-1 §4.4)
MF         = 0.80  (clean office LED, 3-year cleaning cycle, CIBSE TM 3-25)
Required N = (Em × A) / (Φ × UF × MF)
           = (500 × 48) / (3500 × 0.62 × 0.80)
           = 24000 / 1736                   = 13.82
           → round UP to 14  (never under-provide light per
                              [spacing-rules#lumen-method-formula])

Engineer chose N = 12 → achieved
           = (12 × 3500 × 0.62 × 0.80) / 48
           = 20832 / 48                     = 434 lux
                                              < 500 target  → INV-1 FAIL
                                              shortfall 66 lux (13.2%)
```

The root cause is the value-engineered swap from 4500 lm → 3500 lm
without re-running the lumen method. With the canonical 4500 lm panels:

```
Achieved (4500 lm × N=12) = (12 × 4500 × 0.62 × 0.80) / 48 = 558 lux ≥ 500 ✓
```

The original 12-fitting layout was correct for 4500 lm panels. The 3500
lm substitution needed N bumped to 14 (or kept the 4500 lm spec).

## 4. Remediation paths

| Path | Action                              | N  | Achieved (lux) | Trade-off                                  |
|------|-------------------------------------|----|----------------|--------------------------------------------|
| (a)  | Bump to 16 panels in 4×4 grid       | 16 | 579 (+15.7 %)  | +4 fittings, +4 DALI addresses, +1 row     |
| (b)  | Upgrade to 4500 lm panels, keep 4×3 | 12 | 558 (+11.6 %)  | Higher fitting cost, no layout rework      |

Path (b) is canonical — restore the original 4500 lm specification.
Path (a) adds resilience headroom but adds cost. Engineer-of-record
decision.

## 5. S/H ratio check (PASS — under-provision is a lumen problem, not a spacing problem)

12 luminaires in 4 cols × 3 rows in 8000 × 6000 room, 300 mm edge clearance:

```
4 cols across 8 m  →  S_x = (8000 − 600) / 3 = 2467 mm
3 rows across 6 m  →  S_y = (6000 − 600) / 2 = 2700 mm

Hm           = 1950 mm
SHR_max      = 1.5   (LED_PANEL_600 ontology default)
Limit        = SHR_max × Hm = 1.5 × 1950   = 2925 mm

S_x = 2467 mm  ≤  2925 mm  → PASS
S_y = 2700 mm  ≤  2925 mm  → PASS  (90 % of limit — close to ceiling)
                                           → INV-2 PASS
```

S_y at 2700 mm sits at 92 % of the SHR_max limit — operating near the
upper bound of acceptable spacing. The 4×4 remediation drops S_y to
(6000−600)/3 = 1800 mm which is well clear.

## 6. Switch placement (INV-3 PASS)

Single S-wall entrance, offset 3500 mm from the SW corner, 900 mm wide,
inward-opening with latch on the right (door_swing=inward_latch_right).
Latch frame at x = 3500 + 900 = 4400. Switch placed 200 mm to the latch
side: SW01 at (4600, 200), 1200 mm AFF to centre.

```
SW01: type=dali_master, x=4600, y=200, height=1200, switch_side=latch
controls_circuit=C-L01,C-L02,C-L03 (one DALI master for all 3 circuits)
```

`controls_protocol=DALI` triggers INV-3 Rule 1's DALI exception (one
master sufficient). Height 1200 mm sits in the [1150, 1250] band per
[switching-rules#height] (BS 7671 §553.1.1 + IET OSG App E §E1.4).
Switch_side='latch' satisfies [switching-rules#latch-side].

## 7. Part L assessment gap (INV-6 FAIL)

`inputs.new_build=true` AND `jurisdiction=england_wales` triggers Part L
2021 §6 enforcement per validator.md INV-6. Sub-checks:

| Sub-check | Required state                                            | Actual | Result |
|-----------|-----------------------------------------------------------|--------|--------|
| 1         | controls.part_l_assessed == true                          | false  | FAIL   |
| 2         | controls.required[] includes 'occupancy'                  | yes    | PASS   |
| 3         | glazed_walls=[] → daylight_linking NOT required           | n/a    | PASS   |
| 4         | controls.lamp_efficacy_lm_per_w ≥ 95                      | 97.2   | PASS   |

Sub-check 1 FAIL ⇒ Rule 6 FAIL. Per validator.md: "emit
non_compliance_flags entry with severity=critical AND set this INV to
FAIL" — both done. Notable: the lamp efficacy at 97.2 lm/W would
actually PASS the efficacy test once an assessment is run; the
blocker is the missing assessment itself, not the efficacy. Honest
recording of the gap (rather than silent compliance assertion) is the
whole point of INV-6.

## 8. Circuit topology (INV-4 + INV-5 PASS)

3 row circuits on DB L1, one per row (no Z-pattern daisy-chain):

```
Circuit   Zone   Row   Luminaires       Load    MCB     Homerun
C-L01     Z2     0     L01..L04         144 W   6A B    (0, 300,  W)
C-L02     Z2     1     L05..L08         144 W   6A B    (0, 3000, W)
C-L03     Z2     2     L09..L12         144 W   6A B    (0, 5700, W)
```

INV-4: each circuit's `luminaire_ids` share a single row_index → no
Z-pattern, PASS. Homeruns all exit on W wall.

INV-5: 144 W per circuit ≤ 1104 W (6A × 0.8 × 230) per BS 7671:2018+
A2:2022 §433.1.1 + IET OSG App A. 13 % of headroom — ample spare.

## 9. INV walkthrough

| INV    | Severity | Status | Evidence                                          |
|--------|----------|--------|---------------------------------------------------|
| INV-01 | high     | FAIL   | 434 lux < 500 (13 % shortfall, N=12 vs req 14)    |
| INV-02 | high     | PASS   | S_x=2467, S_y=2700 ≤ 2925 (SHR limit)             |
| INV-03 | high     | PASS   | 1 entrance, 1 dali_master, latch, 1200 AFF        |
| INV-04 | high     | PASS   | 3 row circuits, no Z-pattern, homerun W           |
| INV-05 | high     | PASS   | 144 W per circuit ≤ 1104 W (6A 80 % cap)          |
| INV-06 | high     | FAIL   | part_l_assessed=false on new-build                |
| INV-07 | medium   | PASS   | All 12 in Z2 interior; no glazing → no perimeter  |
| INV-08 | medium   | PASS   | selection_source.ontology_default + LG7 citation  |
| INV-09 | medium   | PASS   | drafting_furniture complete, Arial 8/10 pt        |
| INV-10 | high     | FAIL   | non_compliance_flags populated, compliant=false   |

3 of 10 INVs FAIL — the two genuine engineering failures (INV-1 + INV-6)
plus the INV-10 composite that flags any populated non_compliance_flags
array. The remaining 7 PASS demonstrate that under-provision and missed
Part L assessment are scoped failures, not symptoms of a wholesale
broken layout — the engineer needs to act on just those two flags.

## 10. Engineer notes

- **Value-engineering re-checks**: any luminaire substitution (lumen
  output, wattage, beam) must trigger a re-run of the lumen method.
  The lighting-layout skill emits the lumen-method walk in the
  rationale.sections + the calculation_summary so a downstream change
  request can be re-checked deterministically.
- **DALI vs switched controls**: DALI was the controls_protocol of
  record. INV-3 Rule 1's DALI exception (one master switch sufficient)
  applies, but the engineer-of-record should still add wall-mounted
  scene-controllers at the entrance and any secondary control points
  for occupant override. This example records only the master.
- **Why INV-10 composite FAIL vs PASS-with-flags**: Rule 10 sub-check 3
  ('if part_l_compliant==false: at least one severity=critical entry
  referencing Part L') is structurally PASS here. But the overall
  layout is `compliant=false` so the composite INV-10 status reflects
  the failed state honestly. Downstream consumers reading intent-out.json
  see `controls_summary.part_l_compliant=false` and skip issue-gating.
- **Path L sustainability check**: Part L 2021 also requires controls
  to support automatic notification of unscheduled overrides. The DALI
  master here supports manual override; a real Part L assessment would
  also verify the BMS link for unscheduled-override logging — out of
  scope for the lighting-layout skill (lands with the future
  building-automation-controls skill).
- **Emergency lighting**: this layout does NOT include emergency
  luminaires. A real UK private office of this size requires BS 5266-1
  emergency lighting on escape routes — delivered by the separate
  emergency-lighting skill (deferred). Adding emergency luminaires
  would not change INV-1 / INV-6 / INV-10 outcomes here.

## 11. v1.7 D5 retrofit — INV-19 surfaces the same FAIL at per-zone level

Retrofitted by the D5 sprint on 2026-06-04. v1.6.0 → v1.7.0 additions are
orthogonal to the existing INV-1 / INV-6 / INV-10 / INV-11 HIGH FAIL state.

### D5 fields populated

- `zones[].purpose = "task"` — ZP-01 backwards-compat default. Z2 is the
  only zone (a private_office with 500 lx Em target maps to task per
  BS EN 12464-1:2021 §4.2.2.1 + area-definitions.json).
- `zones[].em_target_lux = 500` — mirrors the existing
  `calculation_summary.target_illuminance_lux` unchanged.
- `luminaires[*].mount_type = "recessed"` — MT-01 default. The 600×600
  LED panel is recessed into the 600 mm ceiling grid by definition.
  `z_mm` + `suspension_length_mm` omitted per recessed convention
  (recessed luminaire emission plane inherits `ceiling_height_mm`).
- `calculation_summary.per_zone_achieved[]` — populated with one Z2 entry.

### INV-19 band selection — INFO marginal

```
gap         = target − achieved = 500 − 434     = 66 lux
gap_pct     = gap / target = 66 / 500           = 0.132 = 13.2 %

Validator §INV-19 band table:
| gap_pct range            | ratio_compliance | flag severity | INV verdict   |
|--------------------------|------------------|---------------|---------------|
| gap_pct ≤ 0              | pass             | none          | PASS          |
| 0 < gap_pct < 0.10       | marginal         | INFO          | PASS (<10%)   |
| 0.10 ≤ gap_pct < 0.25  ← | marginal         | INFO          | PASS (<25%)   |
| 0.25 ≤ gap_pct < 0.50    | fail             | MEDIUM        | FAIL (MEDIUM) |
| gap_pct ≥ 0.50           | fail             | HIGH          | FAIL (HIGH)   |

gap_pct = 0.132 sits in row 3 → ratio_compliance='marginal', INFO band,
INV-19 per-zone PASS within-25 %.

Aggregate INV-19 verdict: PASS (1 marginal, 0 fail).
```

### Why INV-1 HIGH FAIL coexists with INV-19 INFO marginal

These two INVs are by-design orthogonal:

- **INV-1** is the binary lumen-method gate. The lumen method requires
  rounding the fitting count UP and any shortfall fails HIGH — the
  engineer must add fittings OR upgrade lumens to clear it.
- **INV-19** is the §6-graded per-zone band-table roll-up against the
  cascade-resolved photometric average. The same 13.2 % shortfall here
  sits in the marginal INFO band — within the 25 % engineering
  tolerance band where the layout is recoverable without re-laying.

Both fire simultaneously on the same root cause (value-engineered 3500
lm panel substitution) and both clear simultaneously: remediation (bump
to 16 panels in a 4×4 grid OR upgrade to 4500 lm panels keeping the 4×3
layout) drives Z2 achieved ≥ 500 lx, flipping INV-1 PASS and INV-19
ratio_compliance='pass' together.

### non_compliance_flags layering (4 entries)

| # | INV    | Severity | Origin               | Subject                                |
|---|--------|----------|----------------------|----------------------------------------|
| 1 | INV-1  | critical | native (lumen)       | Avg-lux under-provision (434 < 500)    |
| 2 | INV-6  | critical | native (Part L)      | part_l_assessed=false on new-build     |
| 3 | INV-11 | critical | cascaded photometric | Per-point min lux 275 < 350 at NW      |
| 4 | INV-19 | info     | native (per-zone)    | Z2 gap_pct=13.2 % marginal INFO band   |

All four reference the SAME under-specified 3500 lm panel substitution.
Each INV catches the failure at a different layer:

- INV-1: lumen-method avg (rounded-up fitting count)
- INV-6: Part L assessment gate (new-build flag)
- INV-11: photometric per-point min (cascade)
- INV-19: per-zone graded band (cascade roll-up)

### Pre-existing FAIL state preserved verbatim

`controls.part_l_compliant=false`, `calculation_summary.compliant=false`,
INV-1 + INV-6 + INV-10 + INV-11 FAIL HIGH — all UNCHANGED. The 3
pre-existing critical flags are untouched. The new INV-19 INFO marginal
entry is appended as the 4th flag. Engineer-of-record must remediate
the lumen-method gap to clear all four INVs.
