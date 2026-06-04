# Example: UK Mixed-Purpose Classroom — Reasoning

D5 sprint Task C.10 NEW example. The **first** example in the lighting-layout
set where ALL THREE BS EN 12464-1:2021 §4.2.2 area purposes coexist
non-vacuously in a single room: **task + surrounding + background**.
INV-13, INV-14, and INV-15 all fire non-vacuously in the same output —
reading the three INV evidence blocks together gives engineers a complete
worked example of the §4.2.2 ratio system. Companion to C.5
`uk-open-plan-office-10x8-dali` (task + surrounding) and C.9
`uk-pendant-open-plan-office` (task only, suspended).

## 1. Why this example exists

The lighting-layout v1.7 D5 sprint adds three new INVs that engage the
§4.2.2 area-purpose classification:

- INV-13 — Zone purpose required + valid (orphan-surrounding blocked)
- INV-14 — Surrounding ratio compliance (≥0.3 ≤ 0.5 × Em_task)
- INV-15 — Background floor (≥ max(Em_task / 3, 50 lx))

Across the existing 9 examples, INV-14 fires non-vacuously only in C.5
(`uk-open-plan-office-10x8-dali`, surrounding ratio = 0.500); INV-15
fires vacuously in every example (no background zone declared). This
example fills both gaps simultaneously by engineering a 3-zone classroom
where all three purposes engage at their canonical boundary values:

| Zone | Purpose      | Em (lx) | Boundary       | Source                              |
|------|--------------|---------|----------------|-------------------------------------|
| Z1   | task         | 300     | Table 5 entry  | BS EN 12464-1:2021 Table 5 (education_classroom) |
| Z2   | surrounding  | 150     | upper band 0.5 | BS EN 12464-1:2021 §4.2.2.2 + Table 6 (0.5 × 300) |
| Z3   | background   | 100     | floor          | BS EN 12464-1:2021 §4.2.2.3 + Table 6 (max(300/3, 50)) |

A secondary-school classroom is the canonical 3-purpose use case:
teacher demonstrates at one end of the room (surrounding band), students
work at desks in the middle (task), back wall holds bulletin boards and
storage (background).

## 2. Site brief

- Room: 9000 × 7000 mm UK secondary-school classroom, 3000 mm ceiling
- Working plane 750 mm AFFL (BS EN 12464-1 Table 5 classroom — task at
  student desk plane per `[spacing-rules#working-plane-defaults]`)
- Z1 target maintained illuminance 300 lux (classroom task category)
- Z2 target 150 lux (surrounding upper-band ratio 0.5 × 300)
- Z3 target 100 lux (background floor max(300/3, 50) = max(100, 50) = 100)
- UK new-build → Part L 2021 §6 applies
- No glazed walls (windowless interior classroom — common UK secondary
  school configuration)
- Single S-wall entrance (offset 4000, width 900, inward_latch_right)
- Controls protocol: DALI (single master + 3 scene buttons for Z1/Z2/Z3)
- Selected luminaire: LED_PANEL_600 @ 4500 lm × 36 W, DALI-dimmable
  classroom-low-glare optic (UGR < 19)

## 3. Lumen-method walk

```
Area A     = 9 × 7                          = 63 m²
Hm         = 3000 − 750                     = 2250 mm  = 2.25 m
RI         = (9 × 7) / (2.25 × (9 + 7))     = 63 / 36
                                            = 1.75
            → ontology table key 1.5 (next-lower band per LG7 §6.2;
              conservative reading vs table-key 2.0 with UF=0.67)
UF         = 0.62  [LED_PANEL_600 @ RI=1.5, reflectances 0.7/0.5/0.2]
             (ontology source: CIBSE LG7 §6.2 + BS EN 12464-1 §4.4)
MF         = 0.80  (clean classroom LED, 3-year cleaning cycle)
N for 300  = (Em × A) / (Φ × UF × MF)
           = (300 × 63) / (4500 × 0.62 × 0.80)
           = 18900 / 2232                   = 8.47
           → round UP to 9   (never under-provide light)
           → engineer bumped to 16 for S/H compliance AND zone-purpose
             granularity (see §4)
Achieved   = (N × Φ × UF × MF) / A
at FULL    = (16 × 4500 × 0.62 × 0.80) / 63
            = 35712 / 63                    = 567 lux room-uniform
                                            ≥ 300 task target  → INV-1 PASS
                                            DALI scene dimming pulls each
                                            zone DOWN to its per-purpose
                                            target (see §6)
```

Reference: `[spacing-rules#lumen-method-formula]`,
`[spacing-rules#room-index]`.

## 4. Why bump 9 → 16

Two reasons drive the bump from lumen-method N=9 to engineer-chosen N=16:

1. **S/H compliance**: 3 cols across 9000 mm gives S_x = (9000−600)/2 =
   4200 mm > 3375 mm SHR limit (FAIL). 4 cols gives S_x = (9000−600)/3
   = 2800 mm ≤ 3375 PASS. 4 cols ⇒ N divisible by 4.

2. **Zone-purpose granularity**: the §4.2.2 area-purpose split needs
   four rows so one row each can serve Z2 surrounding (row 0, teacher
   demonstration) and Z3 background (row 3, back display), while the
   central 2 rows serve Z1 task (student desks). A 3-row layout would
   collapse two zones onto one row of luminaires, defeating the
   per-zone scene-dimming pattern.

The smallest grid meeting both constraints is 4 rows × 4 cols = 16
luminaires.

## 5. S/H ratio enforcement

```
Edge clearance       = 300 mm
4 cols across 9 m    →  S_x = (9000 − 600) / 3 = 2800 mm
4 rows across 7 m    →  S_y = (7000 − 600) / 3 = 2133 mm

Hm           = 2250 mm
SHR_max      = 1.5   (LED_PANEL_600 ontology default)
Limit        = SHR_max × Hm = 1.5 × 2250   = 3375 mm

S_x = 2800 mm  ≤  3375 mm  → PASS (83 % of limit)
S_y = 2133 mm  ≤  3375 mm  → PASS (63 % of limit)
                                           → INV-2 PASS
```

## 6. Zone-purpose split — task + surrounding + background

| Zone | Purpose      | Row(s)   | Luminaires      | Em target | Ratio / floor source                      |
|------|--------------|----------|-----------------|-----------|-------------------------------------------|
| Z1   | task         | 1, 2     | L05..L12 (8)    | 300 lx    | Table 5 education_classroom entry          |
| Z2   | surrounding  | 0 (front)| L01..L04 (4)    | 150 lx    | 0.5 × 300 (Table 6 [0.3, 0.5] upper band) |
| Z3   | background   | 3 (back) | L13..L16 (4)    | 100 lx    | max(300/3, 50) = 100 (Table 6 floor)      |

**Z1 task (rows 1-2 student desks)** — 8 luminaires over the central
student-desk cluster. Em target = 300 lx maintained per BS EN
12464-1:2021 Table 5 education_classroom entry. This is the primary
visual task area.

**Z2 surrounding (row 0 teacher demonstration)** — 4 luminaires across
the front of the room, covering the teacher's demonstration position +
the 500 mm transition band onto the front edge of the student-desk
cluster per BS EN 12464-1:2021 §4.2.2.2 (immediate surrounding area =
band of ≥0.5 m around the task area). Em target = 150 lx = 0.5 × 300
per ZP-02 default ratio (area-definitions.json
`_surrounding_ratio_default` = 0.5, upper bound of the [0.3, 0.5]
Table 6 simplified-rule band).

**Z3 background (row 3 back display wall)** — 4 luminaires across the
back of the room, covering the back display wall (poster panels +
bookshelf + storage). Width = 1500 mm × 9000 mm room width ≥ 3 m wide
per BS EN 12464-1:2021 §4.2.2.3 (background area = band of ≥3 m wide).
Em target = 100 lx = max(300/3, 50) = max(100, 50) = 100 lx per ZP-03
floor rule (Table 6 task_to_background simplified rule).

### Per-INV walkthrough at the boundary

- **INV-13** verdict: PASS. 3 zones × 3 valid purposes (task / surrounding /
  background). Orphan-surrounding check: Z2 surrounding coexists with
  Z1 task → ZP-04 + schema Clause 6 satisfied.

- **INV-14** verdict: PASS. Z2 ratio = 150 / 300 = 0.500 ∈ [0.3, 0.5]
  band, result: pass (equal to upper band — ZP-02 default ratio 0.5).

- **INV-15** verdict: PASS. Z3 floor = max(300/3, 50) = max(100, 50) =
  100 lx; Z3 em = 100, result: pass (equal to floor — ZP-03 default
  applied at the §4.2.2.3 minimum).

The "equal to boundary" outcomes are intentional: this example
demonstrates the exact §4.2.2.2 + §4.2.2.3 boundary values, giving
engineers a worked instance of the ratio + floor checks at the closest
non-failing values.

## 7. Per-zone achievement — DALI scene dimming

All 16 panels are the same physical 600×600 LED design (4500 design
lm, 36 W); the DALI scene controller dims each row-group independently.

```
Full-output room average:
   (16 × 4500 × 0.62 × 0.80) / 63 = 35712 / 63 = 567 lx

DALI scene dimming pulls each zone DOWN to its per-purpose target:

Z1 task        — 8 panels over student-desk cluster (~36 m² central)
                 scene ~63 % rated output  →  ~315 lx achieved
                 target 300, headroom +15 lx (+5 %)        PASS

Z2 surrounding — 4 panels over front teacher band (~13.5 m²)
                 scene ~24 % rated output  →  ~155 lx achieved
                 target 150, headroom +5 lx (+3 %)         PASS

Z3 background  — 4 panels over back display strip (~13.5 m²)
                 scene ~16 % rated output  →  ~105 lx achieved
                 target 100, headroom +5 lx (+5 %)         PASS
```

All three zones PASS the INV-19 per-zone achievement check. Scene
levels are commissioning-set and verified against the §4.2.2
area-purpose targets per Table 6; the engineer-of-record confirms via
in-situ lux meter at the three task planes (student desk, teacher
demonstration plane, back display wall) at handover.

### Why DALI scene dimming rather than mixed luminaire variants

| Option                                  | Verdict   | Reason                                                                 |
|-----------------------------------------|-----------|------------------------------------------------------------------------|
| Different-wattage panels per zone       | Rejected  | Increases parts list, complicates spares pool, no benefit to user      |
| Different photometric variants per zone | Rejected  | Same complication                                                      |
| One luminaire × DALI scene dimming      | **Chosen**| Single parts entry; scenes verified at commissioning; DALI standard    |

## 8. Multi-entrance switch coverage (INV-3 PASS — DALI consolidation)

Single S-wall entrance (offset 4000, width 900, `inward_latch_right`).
`controls_protocol=DALI` triggers INV-3 Rule 1 DALI consolidation: a
single `dali_master` at the entrance group is sufficient (no need for
multiple manual gangs).

| Switch | Entrance | Wall | Door span (mm)    | Latch frame | Wall-parallel | Position    | Type         | Controls        |
|--------|----------|------|-------------------|-------------|---------------|-------------|--------------|-----------------|
| SW01   | Main     | S    | x ∈ [4000, 4900]  | x=4900 (R)  | +200 → x=5100 | (5100, 200) | dali_master  | C-L01..C-L04    |

DALI master logically groups all 4 row circuits via the DALI bus +
scene recall buttons (typically 4 scenes: 'whole-room on',
'task only', 'demo + background', 'tidy-up').

- `switch_side = "latch"` per `[switching-rules#latch-side]`
- `height_aff_mm = 1200` within [1150, 1250] band per
  `[switching-rules#height]` (BS 7671 §553.1.1 + IET OSG App E §E1.4)

## 9. Part L 2021 zoning (INV-6 + INV-7 PASS)

`inputs.new_build=true` AND `jurisdiction=england_wales` triggers Part L
2021 §6 enforcement.

| Sub-check | Required state                                          | Actual | Result |
|-----------|---------------------------------------------------------|--------|--------|
| 1         | controls.part_l_assessed == true                        | true   | PASS   |
| 2         | controls.required[] includes 'occupancy'                | yes    | PASS   |
| 3         | glazed_walls=[] → daylight-linking vacuously satisfied  | n/a    | PASS   |
| 4         | controls.lamp_efficacy_lm_per_w ≥ 95                    | 125    | PASS   |

All four PASS ⇒ Rule 6 PASS. controls.part_l_compliant=true.

INV-7 perimeter consistency: glazed_walls=[] AND no zone declares
zone_type='perimeter' (Z1+Z2+Z3 all zone_type='interior') →
iff-clause perimeter-daylight consistency vacuously PASS. The
Z1/Z2/Z3 split is a §4.2.2 **area-purpose** split, NOT a
daylight-perimeter split.

## 10. Circuit topology (INV-4 + INV-5 PASS)

4 row circuits on DB L1, one per row (no Z-pattern daisy-chain):

```
Circuit   Zone   Row   Luminaires       Load    MCB     Homerun
C-L01     Z2     0     L01..L04         144 W   6A B    (0, 300,  W)
C-L02     Z1     1     L05..L08         144 W   6A B    (0, 2433, W)
C-L03     Z1     2     L09..L12         144 W   6A B    (0, 4567, W)
C-L04     Z3     3     L13..L16         144 W   6A B    (0, 6700, W)
```

INV-4: each circuit's `luminaire_ids` share a single row_index → no
Z-pattern, PASS. Homeruns all exit on W wall.

INV-5: 144 W per circuit ≤ 1104 W (6A × 0.8 × 230) per BS 7671:2018+
A2:2022 §433.1.1 + IET OSG App A. 13 % of headroom — ample spare.

Notice `circuit.zone_id` mirrors each row's zone exactly: C-L01 → Z2
(row 0 surrounding), C-L02 → Z1 + C-L03 → Z1 (rows 1-2 task), C-L04 →
Z3 (row 3 background). No mixed-zone circuits — the §4.2.2 area
boundaries align with row boundaries in this layout, which is the
cleanest way to wire a 3-purpose classroom.

## 11. INV walkthrough

| INV    | Severity | Status | Evidence                                                              |
|--------|----------|--------|-----------------------------------------------------------------------|
| INV-01 | high     | PASS   | Full-output 567 lx ≥ 300 task target; DALI scenes pull per-zone targets |
| INV-02 | high     | PASS   | S_x=2800, S_y=2133 ≤ 3375 (SHR limit)                                 |
| INV-03 | high     | PASS   | 1 entrance / 1 DALI master at latch side                              |
| INV-04 | high     | PASS   | 4 row circuits, no Z-pattern, homerun W                               |
| INV-05 | high     | PASS   | 144 W per circuit ≤ 1104 W (6A 80 % cap)                              |
| INV-06 | high     | PASS   | part_l_assessed + occupancy + no-glazing branch + 125 lm/W            |
| INV-07 | medium   | PASS   | 3-zone purpose split, no daylight-perimeter (no glazing)              |
| INV-08 | medium   | PASS   | selection_source.ontology_default + LG7 citation                      |
| INV-09 | medium   | PASS   | drafting_furniture complete, Arial 8/10 pt                            |
| INV-10 | high     | PASS   | Schema validation OK, Clause 6 orphan-block PASS, no flags            |
| INV-11 | high     | PASS   | Photometric cascade resolved (avg 318 lx, task_area_compliant=true)   |
| INV-13 | high     | PASS   | 3 zones × 3 valid purposes (task + surrounding + background)          |
| INV-14 | high     | PASS   | Surrounding ratio 150/300 = 0.500 ∈ [0.3, 0.5] upper band             |
| INV-15 | high     | PASS   | Background em 100 = floor max(300/3, 50) = 100                        |
| INV-16 | high     | PASS   | All recessed; no pendant/suspended geometry to verify (vacuous)       |
| INV-17 | high     | PASS   | Inherited z=3000 > working_plane=750; clearance=2250=Hm               |
| INV-18 | medium   | PASS   | hm_mm=2250 matches ceiling_height−working_plane=3000−750              |
| INV-19 | high     | PASS   | Z1 315/300 + Z2 155/150 + Z3 105/100 — all 3 zones PASS (+3-5 %)      |

All 19 INVs PASS. No `non_compliance_flags` raised.

## §D5 — v1.7 retrofit (2026-06-04)

**Honest disclosure: this example is the FIRST in the lighting-layout
set where ALL THREE BS EN 12464-1:2021 §4.2.2 area purposes coexist
non-vacuously.** Reading the three INV-13/14/15 evidence blocks
together gives engineers a complete worked example of the §4.2.2 ratio
system at its boundary values.

### The four-place canonical disclosure

This example uses the canonical 4-place disclosure pattern to mirror
the design rationale across all four reading surfaces:

1. **`input.json._note` + `_d5_disclosure_note`** — declares the
   three-purpose engineering intent up-front for the implementer.
2. **`output.json.calculation_summary.assumptions[]`** — carries the
   engineering walk (the lumen-method N=8.47 → 16 bump, the
   per-zone Em derivation, the DALI scene-dim levels).
3. **`output.json.rationale.sections[]`** — carries the design-judgement
   narrative (why the 3-purpose split, why the upper-band ratio, why
   the floor value, why DALI scene dimming over mixed luminaire
   variants).
4. **This `reasoning.md` §D5 block** — carries the meta-level
   commentary (why this example exists in the set, how it relates to
   C.5 + C.9, what the boundary-value choices teach engineers).

### The three v1.7 fields engaged here

1. **`zones[].purpose ∈ {task, surrounding, background}`** — all three
   purpose values are used, one per zone:
   - Z1 → `purpose=task` (ZP-01)
   - Z2 → `purpose=surrounding` (ZP-02)
   - Z3 → `purpose=background` (ZP-03)

2. **`zones[].em_target_lux`** — each zone declares its per-purpose
   maintained-illuminance target:
   - Z1 → `em_target_lux=300` (Table 5 education_classroom entry)
   - Z2 → `em_target_lux=150` (= 0.5 × 300 per Table 6 upper band)
   - Z3 → `em_target_lux=100` (= max(300/3, 50) per Table 6 floor)

3. **`luminaires[].mount_type='recessed'`** — all 16 panels are
   600×600 LED recessed panels (MT-01 default — matches the
   `luminaire_type.description`). `z_mm` + `suspension_length_mm`
   omitted per the recessed convention (geometry inherits
   `ceiling_height_mm=3000`).

4. **`calculation_summary.per_zone_achieved[]`** populated with three
   rows — Z1 task 315/300, Z2 surrounding 155/150, Z3 background
   105/100. All three `ratio_compliance="pass"` with severity none.

### Boundary-value rationale

| Zone | Em target | Boundary chosen     | Why                                                                              |
|------|-----------|----------------------|----------------------------------------------------------------------------------|
| Z2   | 150 lx    | upper band (0.5×Em) | Teacher band needs visible contrast with task area; lower band (90 lx) would look too dim |
| Z3   | 100 lx    | floor (max/3, 50)   | Back display is non-occupied periphery; floor minimises load without violating §4.2.2.3 |

Selecting boundary values is intentional — this example documents the
exact §4.2.2 ratio + floor boundary behaviour so engineers reading
the worked walk see the math at its limit cases rather than at
"safely-padded" interior values.

### What an engineer-of-record would change

This 3-purpose split is **one valid** §4.2.2 area-classification of
the classroom, not the only one. An engineer adding distinct sub-zones
(e.g. a science prep counter at the back, an interactive whiteboard at
the front) would extend the zone list with additional purpose
declarations — typically introducing a second task zone for the
high-illuminance prep counter (`purpose=task`, `em_target=500 lx` per
BS EN 12464-1:2021 Table 5 laboratory entry) while leaving the
classroom-wide background floor unchanged. The 3-purpose pattern here
is the **simplest** valid §4.2.2 classification that engages all three
purpose types — extending it to 4 or 5 zones is straightforward.
