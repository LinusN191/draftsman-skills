# Example: UK Per-Zone Target Violation — Reasoning

D5 sprint Task C.12 NEW example (2026-06-04). **CANONICAL FAIL-BY-DESIGN**
exemplar for the INV-19 HIGH-severity band (`gap_pct ≥ 50%`).

## 1. Why this example exists — CANONICAL FAIL-BY-DESIGN disclosure

This example is **DELIBERATELY FAIL-by-design** to exercise INV-19's
HIGH-severity band. The companion `uk-undersized-lighting-vs-target`
example sits in the INFO `marginal` band (gap_pct=13.2%). This C.12
example pushes the same root cause (value-engineered panel
substitution) to the HIGH band by choosing a wildly under-spec'd
2000 lm panel (vs the canonical 4500 lm `LED_PANEL_600` ontology
entry).

The few-shot library needs HIGH-band coverage so a downstream
generator pattern-matches the band-table mapping correctly on
synthesised IRs.

**Compliance state:**

- `calculation_summary.compliant = false` BY DESIGN
- `compliance_summary.compliant = false` BY DESIGN (intent-out mirror)
- `non_compliance_flags[]` carries 3 layered critical entries
  (INV-19-violation + INV-1 + cascaded INV-11)
- `flags[]` shipped chat-side carry the FAIL-BY-DESIGN tag

Engineer-of-record would either bump to ≥31 panels OR replace with
6000 lm uplift panels keeping the 4×3 grid (achieved 595 lx — clears
all three INVs simultaneously). This is **NOT** a layout that would
ever issue for construction in real practice.

## 2. Site brief

- Room: 10000 × 6000 mm UK private office, 3000 mm finished ceiling
- Working plane 750 mm (BS EN 12464-1 Table 5 — desk-based office)
- Target maintained illuminance 500 lux (private_office task category)
- UGR ≤ 19 (confirm from photometric data)
- UK new-build → Part L 2021 §6 applies (PASSES — efficacy is fine)
- No glazing (interior room)
- Single S-wall entrance, inward-opening latch-right door
- Controls protocol: DALI (single master switch at the entrance)
- Engineer specification: 12 × LED_PANEL_600 @ **2000 lm** in 4×3 grid
  (ultra-low-lumen value-engineered variant — canonical
  `LED_PANEL_600` is 4500 lm)

## 3. Lumen-method walk

```
Area A     = 10 × 6                          = 60 m²
Hm         = 3000 − 750                      = 2250 mm  = 2.25 m
RI         = (10 × 6) / (2.25 × (10 + 6))    = 60 / 36
                                             = 1.67
            → ontology table key 1.5 (next-lower band per LG7 §6.2)
UF         = 0.62  [LED_PANEL_600 @ RI=1.5, reflectances 0.7/0.5/0.2]
             (ontology source: CIBSE LG7 §6.2 + BS EN 12464-1 §4.4)
MF         = 0.80  (clean office LED, 3-year cleaning cycle, CIBSE TM 3-25)
Required N = (Em × A) / (Φ × UF × MF)
           = (500 × 60) / (2000 × 0.62 × 0.80)
           = 30000 / 992                     = 30.24
           → round UP to 31  (never under-provide light per
                              [spacing-rules#lumen-method-formula])

Engineer chose N = 12 → achieved
           = (12 × 2000 × 0.62 × 0.80) / 60
           = 11904 / 60                      = 198.4 lux
Photometric cascade resolves                 = 200 lux (authoritative)
                                               < 500 target → INV-1 FAIL
                                               shortfall 300 lux (60.0%)
```

The root cause is the swap from the canonical 4500 lm panel to a wildly
under-spec'd 2000 lm variant. With the canonical 4500 lm panels at
N=12:

```
Achieved (4500 lm × N=12) = (12 × 4500 × 0.62 × 0.80) / 60 = 446 lux
                                                            (still 11% short)
```

Even with the canonical 4500 lm panels at N=12, the layout is still
marginal — bumping to 6000 lm panels at N=12 clears all three INVs:

```
Achieved (6000 lm × N=12) = (12 × 6000 × 0.62 × 0.80) / 60 = 595 lux ≥ 500 ✓
```

## 4. INV-19 HIGH band selection (the protagonist failure)

Per `validator.md §INV-19` band table:

```
gap         = em_target − em_achieved = 500 − 200    = 300 lux
gap_pct     = gap / em_target = 300 / 500            = 0.60 = 60.0 %

Validator §INV-19 band table:
| gap_pct range            | ratio_compliance | flag severity | INV verdict   |
|--------------------------|------------------|---------------|---------------|
| gap_pct ≤ 0              | pass             | none          | PASS          |
| 0 < gap_pct < 0.10       | marginal         | INFO          | PASS (<10%)   |
| 0.10 ≤ gap_pct < 0.25    | marginal         | INFO          | PASS (<25%)   |
| 0.25 ≤ gap_pct < 0.50    | fail             | MEDIUM        | FAIL (MEDIUM) |
| gap_pct ≥ 0.50         ← | fail             | HIGH          | FAIL (HIGH)   |

gap_pct = 0.60 sits in row 5 → ratio_compliance='fail', HIGH band,
INV-19 per-zone FAIL (HIGH).

Aggregate INV-19 verdict: FAIL (HIGH) (1 fail-HIGH, 0 fail-MEDIUM,
0 marginal, 0 pass).
```

### INV-19 entry in `invariants[]`

```json
{
  "id": "INV-19",
  "passes": false,
  "severity": "high",
  "evidence": "INV-19 verdict: FAIL (HIGH). Zones inspected: 1. Per-zone achievement: Z1 (task): target=500, achieved=200, gap=300, gap_pct=60.0%, ratio_compliance=fail, severity=HIGH. Aggregate: 0 PASS, 0 marginal, 0 MEDIUM, 1 HIGH. Citation: BS EN 12464-1:2021 §4.1 + Table 5."
}
```

### `non_compliance_flags[]` entry (flag-level severity mapping)

```json
{
  "id": "INV-19-violation",
  "severity": "critical",
  "description": "Per-zone task achievement 200 lx is 60% short of 500 lx target. Severity HIGH per INV-19 band (≥50% short).",
  "clause": "BS EN 12464-1:2021 §4.1 + Table 5"
}
```

The schema flag-level enum is `critical/warning/info`. INV-19's HIGH
severity maps to **flag-level `critical`** while the description
preserves the **"HIGH"** wording so a reader can trace the
band-table severity attribution without losing the per-zone severity
mapping. This is the canonical pattern for INV-19 fail-band
flag-level severity mapping.

## 5. Three layered failures on the same root cause

Three INVs fire FAIL HIGH on the **same** root cause (the 2000 lm panel
substitution):

| INV    | Layer                            | Verdict        | Cited evidence                                      |
|--------|----------------------------------|----------------|-----------------------------------------------------|
| INV-1  | Lumen-method binary gate         | FAIL HIGH      | achieved 200 < target 500 → round-up N=31 required  |
| INV-11 | Photometric cascade per-point    | FAIL HIGH      | task_area_compliant=false, min 128 < 0.7×target=350 |
| INV-19 | Per-zone graded band-table       | FAIL HIGH      | gap_pct 60% in HIGH band                            |

All three clear simultaneously under the canonical remediation
(replace with 6000 lm uplift panels keeping the 12-fitting 4×3 layout
→ achieved 595 lx ≥ 500). The example demonstrates the layered-
failure-detection pattern: lumen-method binary + photometric per-point
+ per-zone graded all catch the same bad specification at three
different layers, ensuring no engineer (or LLM) can squeeze a bad
panel-substitution past all three gates.

## 6. S/H ratio check (PASS — layout is dimensionally sound)

12 luminaires in 4 cols × 3 rows in 10000 × 6000 room, 300 mm edge
clearance:

```
4 cols across 10 m →  S_x = (10000 − 600) / 3 = 3133 mm
3 rows across 6 m  →  S_y = (6000 − 600) / 2 = 2700 mm

Hm           = 2250 mm
SHR_max      = 1.5   (LED_PANEL_600 ontology default)
Limit        = SHR_max × Hm = 1.5 × 2250 = 3375 mm

S_x = 3133 mm  ≤  3375 mm  → PASS (93 % of limit)
S_y = 2700 mm  ≤  3375 mm  → PASS (80 % of limit)
                                            → INV-2 PASS
```

The layout is **dimensionally sound** — the failure is purely a
lumen-output problem (the 2000 lm panel is the wrong panel, not the
wrong grid). This is the clean way to isolate the INV-19 protagonist
failure: choose a luminaire spec that fails illuminance while keeping
the spacing topology compliant.

## 7. Switch placement (INV-3 PASS)

Single S-wall entrance, offset 4000 mm from the SW corner, 900 mm wide,
inward-opening with latch on the right (`door_swing=inward_latch_right`).
Latch frame at x = 4000 + 900 = 4900. Switch placed 200 mm to the latch
side: SW01 at (5100, 200), 1200 mm AFF to centre.

```
SW01: type=dali_master, x=5100, y=200, height=1200, switch_side=latch
controls_circuit=C-L01,C-L02,C-L03 (one DALI master for all 3 circuits)
```

`controls_protocol=DALI` triggers INV-3 Rule 1's DALI exception (one
master sufficient). Height 1200 mm sits in the [1150, 1250] band per
[switching-rules#height] (BS 7671 §553.1.1 + IET OSG App E §E1.4).
`switch_side='latch'` satisfies [switching-rules#latch-side].

## 8. Part L 2021 §6 PASSES — failure is NOT a Part L gap

```
Sub-check 1: controls.part_l_assessed = true                   PASS
Sub-check 2: controls.required includes 'occupancy'            PASS
Sub-check 3: glazed_walls = [] → daylight_linking N/A          PASS (vacuous)
Sub-check 4: controls.lamp_efficacy_lm_per_w = 111.1 ≥ 95      PASS
```

`controls.part_l_compliant = true`. INV-6 PASS.

The 2000 lm panel at 18 W gives 111.1 lm/W which **exceeds** the Part
L 2021 Table 6.2 95 lm/W efficacy target. The failure here is **NOT**
a Part L compliance gap — the panels are efficacy-compliant; they
just don't emit enough total lumens at the panel level to hit the
maintained illuminance target.

This is an important nuance: a luminaire can be **efficient** while
being **under-spec'd** for the task. The lumen-method gate (INV-1)
and the per-zone graded gate (INV-19) catch the under-spec; the
Part L efficacy gate (INV-6) does not.

## 9. Circuit topology (INV-4 + INV-5 PASS)

3 row circuits on DB L1, one per row (no Z-pattern daisy-chain):

```
Circuit   Zone   Row   Luminaires       Load   MCB     Homerun
C-L01     Z1     0     L01..L04         72 W   6A B    (0, 300,  W)
C-L02     Z1     1     L05..L08         72 W   6A B    (0, 3000, W)
C-L03     Z1     2     L09..L12         72 W   6A B    (0, 5700, W)
```

INV-4: each circuit's `luminaire_ids` share a single row_index → no
Z-pattern, PASS. Homeruns all exit on W wall.

INV-5: 72 W per circuit ≤ 1104 W (6A × 0.8 × 230) per BS 7671:2018+
A2:2022 §433.1.1 + IET OSG App A. Only **6.5 %** of headroom —
circuits are extremely lightly loaded because the panels themselves
are under-lumened. The wrong-panel substitution shows up at the load
layer too (a canonical 4500 lm 36W panel would draw 4× the current
at the same fitting count, and a 6000 lm 50W panel would draw ~6×).

## 10. INV walkthrough

| INV    | Severity | Status | Evidence                                                        |
|--------|----------|--------|-----------------------------------------------------------------|
| INV-01 | high     | FAIL   | 200 lx < 500 (60 % shortfall, N=12 vs req 31)                   |
| INV-02 | high     | PASS   | S_x=3133, S_y=2700 ≤ 3375 (SHR limit)                           |
| INV-03 | high     | PASS   | 1 entrance, 1 dali_master, latch, 1200 AFF                      |
| INV-04 | high     | PASS   | 3 row circuits, no Z-pattern, homerun W                         |
| INV-05 | high     | PASS   | 72 W per circuit ≤ 1104 W (6A 80 % cap)                         |
| INV-06 | high     | PASS   | part_l_assessed=true, efficacy 111.1 ≥ 95                       |
| INV-07 | medium   | PASS   | All 12 in Z1 interior; no glazing → no perimeter                |
| INV-08 | medium   | PASS   | selection_source.ontology_default + LG7 citation                |
| INV-09 | medium   | PASS   | drafting_furniture complete, Arial 8/10 pt                      |
| INV-10 | high     | FAIL   | non_compliance_flags populated, compliant=false                 |
| INV-11 | high     | FAIL   | photometric task_area_compliant=false                           |
| INV-13 | high     | PASS   | Z1 purpose=task                                                 |
| INV-14 | high     | PASS   | no surrounding zone — vacuous                                   |
| INV-15 | high     | PASS   | no background zone — vacuous                                    |
| INV-16 | high     | PASS   | all recessed; no pendant geometry — vacuous                     |
| INV-17 | high     | PASS   | inherited z=3000 > working_plane=750; clearance 2250            |
| INV-18 | medium   | PASS   | hm_mm 2250 = 3000 − 750 (drift 0)                               |
| INV-19 | high     | FAIL   | **Z1 gap_pct=60% → HIGH band — protagonist failure**            |

**3 of 18 INVs FAIL** — the three layered failures on the same root
cause (INV-1 + INV-11 + INV-19), plus the INV-10 composite that flags
any populated `non_compliance_flags` array. That's a clean failure
fingerprint: the engineer's panel-substitution shows up at exactly
the three layers designed to catch it, while every other INV
(spacing, switches, circuits, Part L, zones, mount, ceiling) passes.

## v1.7 Honest disclosure — D5 fields and FAIL-BY-DESIGN disclosure

This example is shipped at v1.7.0 with the new D5 fields populated
from the start (not a retrofit):

- `zones[].purpose = "task"` (ZP-01) — Z1 is the only zone, a
  private_office with a 500 lx Em target maps to task per
  BS EN 12464-1:2021 §4.2.2.1.
- `zones[].em_target_lux = 500` — BS EN 12464-1:2021 Table 5
  private_office entry.
- `luminaires[*].mount_type = "recessed"` (MT-01) — the 600×600 mm
  LED panel is recessed into the 600 mm ceiling grid by definition.
  `z_mm` + `suspension_length_mm` omitted per recessed convention
  (recessed inherits `ceiling_height_mm`).
- `calculation_summary.per_zone_achieved[]` — populated with one Z1
  entry: target 500 lx, achieved 200 lx (photometric authoritative),
  `ratio_compliance='fail'` per validator §INV-19 band 5.

### CANONICAL FAIL-BY-DESIGN — 4-place disclosure

Per the C.12 contract, the FAIL-by-design intent is disclosed in **4
canonical places**:

1. `input.json._note` — top-of-file disclosure naming INV-19 HIGH band.
2. `output.json.calculation_summary.assumptions[0]` — first
   assumption is the CANONICAL FAIL-BY-DESIGN DISCLOSURE statement.
3. `output.json.rationale.sections[0]` — first rationale section is
   "Why this example exists — CANONICAL FAIL-BY-DESIGN".
4. `reasoning.md §1` (above) + §11 (this section) — body-text
   disclosure for human readers.

The intent-out.json cannot carry an additional disclosure block (its
schema sets `additionalProperties: false`), so the FAIL state is
conveyed at the intent layer via `controls_summary.part_l_compliant`
(here `true` — the failure is illuminance, not Part L) plus the
cascaded `consumed_intents.photometric_grid.payload.task_area_compliant=false`,
matching the canonical layered-failure attribution pattern.

### Why the FAIL is preserved (not "fixed")

The failure is **the point**. Removing the failure would defeat the
purpose of the C.12 example — the few-shot library would lose its
HIGH-band coverage and downstream generators would have no PASS/FAIL
contrast in the INV-19 band-table mapping. The example is shipped
WITH all three layered FAIL HIGH verdicts intact, every INV cited
honestly, and the compliance state recorded as `compliant=false`.

Engineer-of-record encountering this layout in a real project would
**reject** the panel specification and demand the canonical 6000 lm
uplift (path c in §11.3 of the remediation guidance). The example
exists so a generator confronted with a similar bad panel
substitution emits the same layered failure flags rather than
silently asserting compliance.
