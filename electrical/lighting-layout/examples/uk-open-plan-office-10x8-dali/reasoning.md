# Example: UK Open-Plan Office 10×8 m DALI — Reasoning

D3.C.3 canonical re-test example. Built from the user's verbatim
original prompt that produced the bad CAD output. Doubles as the
spec-level re-test gate AND the few-shot canonical that future
generators copy from.

v1.7.0 D5 RETROFIT (2026-06-04). Single Z2 zone split into Z2 task +
Z3 surrounding per BS EN 12464-1:2021 §4.2.2.2 ≥500 mm perimeter band.
This is the FIRST example across the lighting-layout example set
where INV-14 fires non-vacuously: surrounding ratio 250/500 = 0.500
∈ [0.3, 0.5] PASS (upper boundary of the Table 6 simplified-rule
band). See §D5 below for the 4-place honest disclosure.

All 19 INVs PASS (10 originals + INV-11 cascade + INV-13..19 v1.7
area-split; INV-12 was removed in C.0 sprint).

## 1. Why this example exists

### 1.1 The user's verbatim prompt

> "Lighting layout for a 10m × 8m open-plan office room with a 2.7m
> suspended ceiling. Target 500 lux maintained illuminance to
> BS EN 12464-1. Use 4000K (neutral white) LED panels at ~6000 lumens
> each, recessed into a 600mm modular ceiling grid. UK new-build,
> BS 7671 code basis. DALI controls. No glazed walls. Drawing number
> L-001, revision P1, scale 1:50, A3 sheet."

### 1.2 What the original CAD got wrong

The pre-D3 generator turned this prompt into a CAD drawing with:

1. **Z-pattern daisy-chain.** Single circuit zig-zagging diagonally
   across rows instead of running parallel down rows.
2. **Fourth column flush with the east wall.** No edge clearance —
   the rightmost column sat 0 mm from the wall, blocking the
   ceiling tile.
3. **No homerun arrow.** Renderer drew no cable exit indicator at the
   DB-facing wall.
4. **No luminaire schedule.** Drawing shipped without a parts list.
5. **No title block.** L-001 / P1 / 1:50 / A3 nowhere on the sheet.
6. **No dimensions or scale bar.** Drawing read as a floating sketch.
7. **Uneven row spacing.** Rows 1 and 2 closer together than rows
   2 and 3 — failed S/H uniformity.
8. **Only 12 luminaires.** Lumen-method math demanded more; the
   generator silently rounded down to fit a 3×4 grid.

§10 maps each of these bugs to the specific D3 invariant that
structurally prevents it. This example is the canonical PASS that
exercises every fix.

## 2. Site brief

- Room: 10000 × 8000 mm UK new-build open-plan office, 2700 mm
  suspended ceiling
- Working plane 750 mm (BS EN 12464-1 Table 5.26.1 office task —
  task at desk plane per [spacing-rules#working-plane-defaults])
- Target maintained illuminance 500 lux (open-plan office task)
- UGR ≤ 19 (BS EN 12464-1 office task — confirm from manufacturer
  photometric file)
- UK new-build → Approved Doc L 2021 §6 applies
- No glazed walls → no perimeter zone, daylight-linking N/A
- Single entrance on S wall (offset 4500, width 900,
  inward_latch_right)
- Controls protocol: DALI (single dali_master at entrance is
  sufficient because DALI consolidates logical zoning on the bus)
- Selected luminaire: LED_PANEL_600 @ 6000 lm × 48 W (vendor-typical
  mid-range DALI panel; 125 lm/W lamp efficacy)
- Drawing L-001 revision P1 scale 1:50 sheet size A3 (verbatim from
  user prompt)

## 3. Lumen-method walk

```
Area A     = 10 × 8                        = 80 m²
Hm         = 2700 − 750                    = 1950 mm = 1.95 m
RI         = (10 × 8) / (1.95 × (10 + 8))  = 80 / 35.1
                                           = 2.279
              → ontology table key 2.0 (closest band per LG7 §6.2)
UF         = 0.67 (LED_PANEL_600 at RI=2.0,
                   reflectances 0.7_0.5_0.2)
MF         = 0.80 (clean office, 3-year cleaning cycle, CIBSE TM 3-25)
N_required = (E × A) / (Φ × UF × MF)
           = (500 × 80) / (6000 × 0.67 × 0.80)
           = 40000 / 3216
           = 12.438
           → round UP to 13 (NEVER round down)
```

13 is prime. Only a strip layout (1×13 or 13×1) fits without sub-
dividing into a rectangular grid. A strip would fail S/H on the long
axis (S along strip ≫ SHR_max × Hm). So bump for grid symmetry.

```
Achieved   = (N_final × Φ × UF × MF) / A
           = (20 × 6000 × 0.67 × 0.80) / 80
           = 64320 / 80
           = 804.0 lux
           ≥ 500 target → INV-01 PASS with 60 % headroom
```

The 60 % headroom is the combined effect of (a) rounding 12.438 UP to
13 and then (b) bumping 13 → 20 to satisfy S/H. Acceptable for an
open-plan office where uniformity matters more than hitting the
target exactly.

## 4. S/H ratio enforcement loop

```
Hm         = 1950 mm
SHR_max    = 1.5 (LED_PANEL_600 ontology default)
limit      = SHR_max × Hm = 1.5 × 1950 = 2925 mm
edge       = 300 mm (LED_PANEL_600 + 600 mm ceiling grid)

Step 1 — N = 13 (round-UP from lumen method)
  13 is prime → only 1×13 or 13×1 strips fit
  S along strip = (room_long − edge×2) / 12 ≈ 783 mm  PASS along axis
  S across strip = room_short − edge×2 = 7400 mm    FAIL >> 2925
  → REJECT strip layout

Step 2 — N = 16 (next square layout, 4×4)
  S_x = (10000 − 600) / 3 = 9400 / 3 = 3133 mm   FAIL > 2925 by 7 %
  S_y = (8000 − 600) / 3 = 7400 / 3 = 2467 mm    PASS (84 % of limit)
  → 4×4 looks tidy but FAILS column-spacing limit

Step 3 — N = 20 (5 cols × 4 rows)
  S_x = (10000 − 600) / 4 = 9400 / 4 = 2350 mm   PASS (80 % of limit)
  S_y = (8000 − 600) / 3 = 7400 / 3 = 2467 mm    PASS (84 % of limit)
  → BOTH PASS → INV-02 PASS

Final layout: 4 rows × 5 cols = 20 luminaires
```

Snap-to-50 mm grid is applied to row positions only (column positions
already land on integer mm):

```
x positions = 300, 2650, 5000, 7350, 9700           (no snap needed)
y positions = 300, 2767→2750, 5233→5250, 7700       (snap row 2 + 3)
```

Snapped S_y values: 2750-300 = 2450; 5250-2750 = 2500; 7700-5250 =
2450 — all ≤ 2925 mm. INV-02 holds after snap.

## 5. Circuit topology (closes Z-pattern bug)

4 row circuits C-L01..C-L04, one per row:

| Circuit | row_index | Luminaires | Load   | MCB        | Homerun (W wall) |
|---------|-----------|------------|--------|------------|------------------|
| C-L01   | 0         | L01..L05   | 240 W  | 6 A curve B| (0, 300)         |
| C-L02   | 1         | L06..L10   | 240 W  | 6 A curve B| (0, 2750)        |
| C-L03   | 2         | L11..L15   | 240 W  | 6 A curve B| (0, 5250)        |
| C-L04   | 3         | L16..L20   | 240 W  | 6 A curve B| (0, 7700)        |

Each circuit's luminaire_ids reference one row only — max(row_indices)
− min(row_indices) = 0 per circuit. INV-04 Rule 4a (row-share Δ ≤ 1)
is structurally enforced: no diagonal jump is even representable.

All 4 homeruns exit on W wall at the row's y-coordinate — 4 parallel
cables back to DB L1, no Z-pattern.

INV-05: 240 W = 5 × 48 W ≤ 1104 W (6 A × 0.8 × 230 V) — each circuit
runs at 22 % of its 80 % continuous-load cap. Ample headroom for
future task lighting drops.

## 6. Switch placement (closes switch-under-fixture bug)

Single entrance on S wall:
- `offset_mm = 4500` (door left edge at x = 4500 from SW corner)
- `width_mm = 900` (door right edge at x = 5400)
- `door_swing = inward_latch_right` → latch frame is at the **right**
  end of the door span (x = 5400)

Switch derivation per [switching-rules#latch-side] (IET OSG App E
§E1.4):
- Place switch 200 mm PAST the latch frame on the latch side
  → x = 5400 + 200 = 5600
- Place switch 200 mm INSIDE the room from the wall edge
  → y = 0 + 200 = 200
- Height 1200 mm AFFL within the [1150, 1250] band per
  [switching-rules#height] (BS 7671 §553.1.1)

Result: `SW01 at (5600, 200), 1200 AFFL, switch_side='latch',
type='dali_master'`

DALI consolidation: `controls_protocol = DALI` means the single
master logically controls all 4 row circuits via the DALI bus
(`controls_circuit = "C-L01,C-L02,C-L03,C-L04"`). No per-circuit
wall switches are needed because DALI handles zoning in software at
the gateway. INV-03 Rule 1 vacuously holds: 1 switch ≥ 1 entrance.

## 7. Part L compliance (no-glazing branch)

UK new-build + jurisdiction=england_wales → Approved Doc L 2021 §6
applies. Four sub-checks:

1. **part_l_assessed = true** — engineer-of-record has run the
   compliance check. PASS.
2. **automatic control includes 'occupancy'** — DALI + PIR detector
   satisfies Part L §6 user-control + automatic-control. PASS.
3. **daylight-linking** — `glazed_walls = []` → no glazing means
   Part L §6.5 is **vacuously satisfied** (the rule only requires
   daylight zoning when there is a perimeter zone). `daylight_linking
   = false` is the correct value here. PASS.
4. **lamp efficacy ≥ 95 lm/W** — 6000 lm / 48 W = 125 lm/W ≥ 95.
   PASS.

All four → `controls.part_l_compliant = true` → INV-06 PASS.

## 8. Zone assignment (no perimeter, no glazing)

One zone Z2 interior contains all 20 luminaires, fed by 4 row
circuits. `Z2.zone_type = 'interior'`; `Z2.control = 'dali_master'`.

INV-07 Rule 3 (perimeter consistency) is the iff-clause:
- glazed_walls = []      ⇔   no Z1 perimeter zone
- glazed_walls non-empty ⇔   Z1 perimeter zone present

Here `glazed_walls = []` AND there is no Z1 in `zones[]` — both sides
of the iff hold, Rule 3 PASS. Rule 1 (1:1 luminaire→zone referential
integrity) also PASS — 20 luminaires each reference exactly Z2.

## 9. Drafting furniture (closes annotation-loss bugs)

Title block carries the verbatim user prompt values:

| Field          | Value                              |
|----------------|------------------------------------|
| project_name   | UK new-build open-plan office      |
| drawing_number | L-001                              |
| revision       | P1                                 |
| scale          | 1:50                               |
| sheet_size     | A3                                 |
| date           | 2026-05-28                         |
| font_family    | Arial                              |
| font_size_pt   | 10                                 |

Scale bar at (7500, 8500) — sits above the room (y > 8000) in the
negative-margin convention.

Dimensions [2]:
- Horizontal "10000 mm" at y = −300 (below the room)
- Vertical "8000 mm" at x = −300 (left of the room)

Negative coordinates are permitted per the D3.B.3 fix-pass — they
represent the renderer's negative-space annotation margin outside the
room rectangle (model-space origin at room SW corner).

Luminaire schedule has the required 5 columns (Ref / Manufacturer /
Lumens / Wattage / Count) + 1 row for LED_PANEL_600 × 20.

Every annotation declares `font_family = 'Arial'` and explicit
`font_size_pt` ∈ {8, 10}. No `{{placeholder}}` substrings remain.
INV-09 PASS.

## 10. How D3 fixed each visible bug in the original CAD image

| Original bug                              | D3 fix                                                                                                              | INV that catches it       |
|-------------------------------------------|---------------------------------------------------------------------------------------------------------------------|---------------------------|
| Z-pattern daisy-chain                     | 4 row circuits, each luminaire's circuit_id implies row_index — `max−min = 0` per circuit                          | INV-04 Rule 4a            |
| 4th column flush with east wall           | `[placement-rules#edge-clearance]` 300 mm — cols at 300 / 2650 / 5000 / 7350 / 9700 (last col 300 mm from east)     | INV-02 + spacing-rules    |
| No homerun arrow                          | `circuits[].homerun_endpoint = {x_mm, y_mm, wall}` on every circuit                                                | INV-04 Rule 4b            |
| No luminaire schedule                     | `drafting_furniture.luminaire_schedule` with 5-col header + LED_PANEL_600 × 20 row                                  | INV-09                    |
| No title block                            | `drafting_furniture.title_block` with L-001 / P1 / 1:50 / A3 verbatim from user prompt                              | INV-09                    |
| No dimensions / scale bar                 | `drafting_furniture.dimensions[2]` (10000 mm + 8000 mm) + `drafting_furniture.scale_bar` (2000 mm @ 500 mm ticks)   | INV-09                    |
| Uneven row spacing                        | S/H enforcement loop bumps N until S_x AND S_y both ≤ SHR_max × Hm — forces symmetric grid                          | INV-02                    |
| 12 luminaires (silently rounded down)     | Lumen-method N=12.438 must round UP to 13; S/H loop then bumps to 20 (4×5). Generator may never round down.         | INV-01 + INV-02           |

Each row in the table represents a structural constraint, not a
renderer hint. The bad CAD failure modes are no longer expressible
in a schema-valid IR — the renderer reads the IR and can't draw a
Z-pattern because the IR doesn't allow one to be encoded.

## 11. INV walkthrough (all 10 PASS)

| INV  | Sev    | Evidence summary                                                       |
|------|--------|------------------------------------------------------------------------|
| 01   | high   | 804 ≥ 500 target (60 % headroom from round-UP + S/H bump)             |
| 02   | high   | S_x=2350, S_y=2467, both ≤ 2925 limit                                  |
| 03   | high   | 1 entrance + 1 dali_master @ (5600, 200), 1200 AFFL, latch side       |
| 04   | high   | 4 row circuits, Δrow_index = 0 per circuit; homeruns on W wall        |
| 05   | high   | 240 W per circuit ≤ 1104 W (6 A × 0.8 × 230 V) — 22 % of headroom     |
| 06   | high   | UK new-build + DALI + occupancy + efficacy 125 ≥ 95; no glazing branch|
| 07   | medium | 20 luminaires → Z2 only; no Z1 (iff with glazed_walls=[])             |
| 08   | medium | photometric_source=ontology_default; citation matches LED_PANEL_600   |
| 09   | medium | drafting_furniture complete; Arial + font_size_pt; no placeholders    |
| 10   | high   | schema PASS; non_compliance_flags=[]; compliant=true; mode=full_drawing|

## D5. v1.7 Retrofit — task + surrounding split (first non-vacuous INV-14 PASS)

D5 sprint (2026-06-04) split the single Z2 zone of v1.6.0 into Z2
task + Z3 surrounding per BS EN 12464-1:2021 §4.2.2.2. This is the
**first** example across the lighting-layout example set where INV-14
fires non-vacuously — every prior retrofit (C.1–C.4) either declared
only task zones (office-open-plan, classroom) or used circulation
zones (reception-lobby, bathroom), so INV-14 short-circuited as
"surrounding zones inspected: 0 — vacuous PASS".

### D5.1. Geometric derivation of the perimeter band

BS EN 12464-1:2021 §4.2.2.2 defines the immediate surrounding area as
"a band of at least 0.5 m width around the task area within the
visual field." With no zone polygon in the lighting-layout-ir schema,
band membership is derived from luminaire (x, y):

```
Task region   = room footprint inset 500 mm from each wall
              = [500, 9500] mm × [500, 7500] mm
              (the task area itself; the surrounding band wraps it)

Surrounding   = the ring between the room walls and the task region's
band (≥500   inner edge — at least 500 mm wide on each side
mm wide)

Luminaire band membership rule used here:
- in Z3 surrounding ⇔ min(x, 10000-x, y, 8000-y) < 1500 mm
- in Z2 task        ⇔ min(x, 10000-x, y, 8000-y) ≥ 1500 mm

The 1500 mm cut buys a 500 mm safety margin so grid-edge luminaires
land in the surrounding band rather than straddling the §4.2.2.2
band/task boundary.
```

Applied to the 4×5 grid:

| Lum | x_mm | y_mm | min-dist | Zone |
|-----|------|------|----------|------|
| L01 | 300  | 300  | 300      | Z3   |
| L02 | 2650 | 300  | 300      | Z3   |
| L03 | 5000 | 300  | 300      | Z3   |
| L04 | 7350 | 300  | 300      | Z3   |
| L05 | 9700 | 300  | 300      | Z3   |
| L06 | 300  | 2750 | 300      | Z3   |
| L07 | 2650 | 2750 | 2650     | Z2   |
| L08 | 5000 | 2750 | 2750     | Z2   |
| L09 | 7350 | 2750 | 2650     | Z2   |
| L10 | 9700 | 2750 | 300      | Z3   |
| L11 | 300  | 5250 | 300      | Z3   |
| L12 | 2650 | 5250 | 2650     | Z2   |
| L13 | 5000 | 5250 | 2750     | Z2   |
| L14 | 7350 | 5250 | 2650     | Z2   |
| L15 | 9700 | 5250 | 300      | Z3   |
| L16 | 300  | 7700 | 300      | Z3   |
| L17 | 2650 | 7700 | 300      | Z3   |
| L18 | 5000 | 7700 | 300      | Z3   |
| L19 | 7350 | 7700 | 300      | Z3   |
| L20 | 9700 | 7700 | 300      | Z3   |

Result: 6 → Z2 task; 14 → Z3 surrounding.

### D5.2. em_target derivation

```
Z2 task       em_target_lux = 500
              (BS EN 12464-1:2021 Table 5.26.1 open-plan office task)

Z3 surrounding em_target_lux = 500 × _surrounding_ratio_default
                             = 500 × 0.5
                             = 250 lx

ZP-02 simplified-rule band: [0.3 × 500, 0.5 × 500] = [150, 250]
INV-14 ratio = em_target_Z3 / em_target_Z2 = 250 / 500 = 0.500
INV-14 band  = [0.3, 0.5]
INV-14 result = PASS (equal to upper bound)
```

The upper-band boundary value (0.5) is selected over the lower (0.3)
because the 4×5 uniform grid actually delivers the same 804 lx
everywhere — pulling the surrounding target down to 150 lx would
understate the design intent. 250 lx documents "the surrounding band
receives the same illuminance treatment as the task area" while still
satisfying the §4.2.2.2 floor.

### D5.3. Mount type defaults

All 20 luminaires default to `mount_type='recessed'` per MT-01 —
matches the user's verbatim prompt phrase "recessed into a 600 mm
modular ceiling grid". `z_mm` + `suspension_length_mm` omitted
(recessed inherits `ceiling_height_mm=2700` per MT-01 convention).
INV-16 + INV-17 vacuously PASS — no pendant/suspended geometry to
verify.

### D5.4. Circuit topology preserved (mixed-zone feed honest disclosure)

Circuit topology unchanged from v1.6.0: 4 row circuits C-L01..C-L04.
Each row's 5 luminaires share a single `row_index` → INV-4 PASS held.
But the new zone split means rows 1 and 2 feed luminaires across BOTH
Z2 and Z3 (3 task + 2 perimeter each):

```
C-L01 (row 0): L01..L05 → all Z3 → circuit.zone_id = Z3
C-L02 (row 1): L06 Z3, L07-L09 Z2, L10 Z3 → predominantly Z2
              → circuit.zone_id = Z2 (3 task vs 2 perimeter)
C-L03 (row 2): L11 Z3, L12-L14 Z2, L15 Z3 → predominantly Z2
              → circuit.zone_id = Z2
C-L04 (row 3): L16..L20 → all Z3 → circuit.zone_id = Z3
```

The mixed-zone circuit feed is **honest by design**: a single
electrical circuit may feed luminaires across §4.2.2 area zones
because DALI handles per-luminaire dimming on the bus. The circuit
topology is a wiring construct (BS 7671 §433.1.1 80 % rule, MCB
ratings, homerun routing); the zone is a §4.2.2 area-classification
construct (Em targets, surrounding-ratio compliance). The two
constructs are orthogonal — circuit.zone_id reflects the dominant
zone of each row for IR ergonomics, but the per-luminaire zone_id is
the source of truth for INV-7 and INV-19.

### D5.5. per_zone_achieved

```
Z2 task:        target=500, achieved=804.0 → ratio_compliance=pass
Z3 surrounding: target=250, achieved=804.0 → ratio_compliance=pass
```

Both zones inherit the uniform 804 lx achievement from the 4×5
symmetric grid — the lumen-method assumption that illuminance is
uniform across the working plane carries through to both zones
because the luminaires are distributed evenly. In a real photometric
grid (INV-11), Z3 perimeter cells would typically achieve slightly
less than Z2 cells due to wall absorption, but the cascade IES
`synthetic_reference_C3` returns 752 lx uniform — still way above
both targets. INV-19 PASSes with no marginal flags.

### D5.6. INV-13..19 — summary

| INV  | Result          | Note                                          |
|------|-----------------|-----------------------------------------------|
| 13   | PASS            | Z2 task + Z3 surrounding both declare purpose + em |
| 14   | **PASS** (first non-vacuous) | ratio 0.500 ∈ [0.3, 0.5] upper boundary |
| 15   | PASS (vacuous)  | no background zone                            |
| 16   | PASS (vacuous)  | all recessed; no pendant/suspended            |
| 17   | PASS            | z_mm inherits 2700 (recessed); clearance 1950 |
| 18   | PASS            | hm_mm=1950 = 2700−750 (recessed branch)       |
| 19   | PASS (both)     | Z2 804/500 + Z3 804/250 both ratio_compliance=pass |

## 12. Assumptions

- UF + SHR_max from CIBSE LG7 §6.2 ontology defaults (LED_PANEL_600
  @ RI=2.0, 0.7/0.5/0.2 reflectances); engineer-of-record must
  verify against manufacturer photometric file before issue
- MF = 0.80 assumes a 3-year cleaning cycle in a clean office
  (CIBSE TM 3-25)
- DALI + PIR occupancy detection assumed to satisfy Part L §6 —
  confirm against project lighting controls schedule
- Lamp efficacy 125 lm/W derived from inputs lumen_output/wattage_w
  = 6000/48 (vendor-typical for a mid-range 6000 lm DALI panel)
- Working plane = 750 mm AFFL (BS EN 12464-1:2021 Table 5.26.1 office
  task at desk plane per [spacing-rules#working-plane-defaults])
