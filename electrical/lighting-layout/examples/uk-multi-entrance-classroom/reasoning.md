# Example: UK Multi-Entrance Classroom — Reasoning

D3.C.2 clean PASS example #2. Demonstrates INV-3 multi-entrance coverage
+ INV-7 perimeter-zone assignment on a glazed wall. All 10 INVs PASS.
Pair example with uk-undersized (INV-1 + INV-6 failure mode) and
uk-part-l-fail (INV-6 critical failure mode) to give the few-shot library
balanced coverage of both happy and sad paths.

## 1. Why this example exists

The existing v1.4 examples either had a single entrance (office-open-plan,
warehouse-highbay) or a single entrance with daylight zoning (reception-
lobby). None exercised the INV-3 multi-wall branch where `controls_protocol`
is `switched` (not DALI) and `switches.length >= entrances.length` must be
emitted on three different walls with three different `door_swing` values.
This example adds that coverage.

A secondary-school classroom is the canonical UK multi-entrance use case:
main door on one wall, fire-exit on the opposite wall, communicating door
to an adjoining classroom on a third wall. All three need a wall switch
at the latch side for entry-point control.

## 2. Site brief

- Room: 10000 × 8000 mm UK secondary-school classroom, 3000 mm ceiling
- Working plane 700 mm (BS EN 12464-1 Table 5 classroom — task at
  student desk plane per [spacing-rules#working-plane-defaults])
- Target maintained illuminance 300 lux (classroom task category)
- UGR ≤ 19 (confirm from photometric data; classroom prefers UGR ≤ 16
  for sustained reading — out of scope here, ontology default)
- UK new-build → Part L 2021 §6 applies
- Glazed S wall (windows for daylight + view-out)
- Three entrances on three walls:
  - S wall main entrance (offset 3500, width 900, inward_latch_right)
  - N wall fire-exit (offset 7000, width 900, outward_latch_left)
  - W wall adjoining-classroom door (offset 3000, width 800,
    inward_latch_left)
- Controls protocol: switched (not DALI — 3 wall switches needed)
- Selected luminaire: LED_PANEL_600 @ 4500 lm × 36 W canonical
  (ontology default — no value-engineering substitution this time)

## 3. Lumen-method walk

```
Area A     = 10 × 8                         = 80 m²
Hm         = 3000 − 700                     = 2300 mm  = 2.3 m
RI         = (10 × 8) / (2.3 × (10 + 8))    = 80 / 41.4
                                            = 1.93
            → ontology table key 1.5 (next-lower band per LG7 §6.2)
              (using table key 2.0 with UF=0.67 would give achieved
              482 lux instead of 446 — either choice PASSes INV-1;
              picked 1.5 for the conservative reading)
UF         = 0.62  [LED_PANEL_600 @ RI=1.5, reflectances 0.7/0.5/0.2]
             (ontology source: CIBSE LG7 §6.2 + BS EN 12464-1 §4.4)
MF         = 0.80  (clean classroom LED, 3-year cleaning cycle)
N          = (Em × A) / (Φ × UF × MF)
           = (300 × 80) / (4500 × 0.62 × 0.80)
           = 24000 / 2232                   = 10.75
           → round UP to 11  (never under-provide light)
           → engineer bumped to 16 for 4×4 grid symmetry + S/H margin
             + ceiling-grid alignment + uniformity at desk plane
Achieved   = (N × Φ × UF × MF) / A
           = (16 × 4500 × 0.62 × 0.80) / 80
           = 35712 / 80                     = 446.4 lux
                                              ≥ 300 target  → INV-1 PASS
                                              49 % headroom — acceptable
                                              for classroom (uniformity
                                              matters more than exact lux)
```

Reference: `[spacing-rules#lumen-method-formula]`, `[spacing-rules#room-index]`.

## 4. Why bump 11 → 16 (rather than 12)?

Three reasons drive the bump from lumen-method N=11 to engineer-chosen N=16:

1. **Grid symmetry**: 4×4 is square; 11 fittings cannot be laid out on a
   uniform grid in a rectangular room. 12 in 4×3 or 3×4 would work, but
   16 in 4×4 gives both row and column symmetry which matches the
   classroom's tabular desk arrangement.
2. **S/H margin**: 4×4 gives S_x=3133, S_y=2467 — both well under the
   SHR_max=3450 limit. 4×3 (12 fittings) would give S_y=(8000−600)/2=
   3700 mm > 3450 → INV-2 FAIL.
3. **Uniformity Uo**: BS EN 12464-1 §4.3 requires Uo ≥ 0.6 for classroom
   task plane. Denser layout improves uniformity. 16 fittings on 4×4
   gives better Uo than the lumen-method minimum.

(2) is the binding constraint — 12 fittings cannot pass S/H.

## 5. S/H ratio enforcement

```
Edge clearance      = 300 mm
4 cols across 10 m  →  S_x = (10000 − 600) / 3 = 3133 mm
4 rows across 8 m   →  S_y = (8000 − 600) / 3  = 2467 mm

Hm           = 2300 mm
SHR_max      = 1.5   (LED_PANEL_600 ontology default)
Limit        = SHR_max × Hm = 1.5 × 2300   = 3450 mm

S_x = 3133 mm  ≤  3450 mm  → PASS (91 % of limit)
S_y = 2467 mm  ≤  3450 mm  → PASS (72 % of limit)
                                           → INV-2 PASS
```

## 6. Multi-entrance switch coverage (INV-3 PASS)

3 entrances on 3 different walls. controls_protocol=switched →
INV-3 Rule 1 sub-check requires switches.length ≥ entrances.length:
3 ≥ 3 PASS.

| Switch | Entrance       | Wall | Latch derivation                         | Position       | Type   | Controls    |
|--------|----------------|------|------------------------------------------|----------------|--------|-------------|
| SW01   | Main           | S    | door_swing=inward_latch_right → latch L  | (3500, 200)    | 2_gang | C-L01,C-L02 |
| SW02   | Fire-exit      | N    | door_swing=outward_latch_left → latch L  | (7000, 7800)   | 1_gang | C-L04       |
| SW03   | Adjoining-room | W    | door_swing=inward_latch_left → latch L   | (200, 3000)    | 1_gang | C-L03       |

All three switches:
- `switch_side = "latch"` per [switching-rules#latch-side]
- `height_aff_mm = 1200` within [1150, 1250] band per [switching-rules#height]
  (BS 7671 §553.1.1 + IET OSG App E §E1.4)
- Placed 200 mm inside the room from the door's latch frame

**Why SW01 is 2-gang vs SW02/SW03 1-gang**: the main entrance is the
primary control point for the whole room. The 2-gang gives independent
toggle of the daylight-linked perimeter (Z1) vs the occupancy-controlled
interior (Z2). The fire-exit and adjoining-room doors are secondary
entry points where occupants typically need only local-row control —
1-gang on the nearest row circuit (C-L04 for N fire-exit; C-L03 for W
adjoining-room door).

## 7. Part L 2021 zoning (INV-6 + INV-7 PASS)

`inputs.new_build=true` AND `jurisdiction=england_wales` triggers Part L
2021 §6 enforcement.

| Sub-check | Required state                                            | Actual | Result |
|-----------|-----------------------------------------------------------|--------|--------|
| 1         | controls.part_l_assessed == true                          | true   | PASS   |
| 2         | controls.required[] includes 'occupancy'                  | yes    | PASS   |
| 3         | glazed_walls=['south'] → daylight_linking required        | yes    | PASS   |
| 4         | controls.lamp_efficacy_lm_per_w ≥ 95                      | 125    | PASS   |

All four PASS ⇒ Rule 6 PASS. controls.part_l_compliant=true.

INV-7 perimeter consistency: glazed_walls=['south'] non-empty AND zone
Z1.zone_type='perimeter' AND Z1 luminaires (L01..L04 at y=300) within
1500 mm of S wall (controls.perimeter_zones[{wall:'S', depth_mm:1500}])
→ Rule 3 perimeter-consistency PASS per [switching-rules#perimeter-circuit].

| Zone | zone_type | Control protocol | Luminaires       | Circuits | Load  |
|------|-----------|------------------|------------------|----------|-------|
| Z1   | perimeter | daylight_linked  | L01..L04 (row 0) | C-L01    | 144 W |
| Z2   | interior  | occupancy        | L05..L16 (rows 1..3) | C-L02..C-L04 | 432 W |

## 8. Circuit topology (INV-4 + INV-5 PASS)

4 row circuits on DB L1, one per row (no Z-pattern daisy-chain):

```
Circuit   Zone   Row   Luminaires       Load    MCB     Homerun
C-L01     Z1     0     L01..L04         144 W   6A B    (0, 300,  W)
C-L02     Z2     1     L05..L08         144 W   6A B    (0, 2767, W)
C-L03     Z2     2     L09..L12         144 W   6A B    (0, 5233, W)
C-L04     Z2     3     L13..L16         144 W   6A B    (0, 7700, W)
```

INV-4: each circuit's `luminaire_ids` share a single row_index → no
Z-pattern, PASS. Homeruns all exit on W wall.

INV-5: 144 W per circuit ≤ 1104 W (6A × 0.8 × 230) per BS 7671:2018+
A2:2022 §433.1.1 + IET OSG App A. 13 % of headroom — ample spare.

## 9. INV walkthrough

| INV    | Severity | Status | Evidence                                              |
|--------|----------|--------|-------------------------------------------------------|
| INV-01 | high     | PASS   | 446 lux ≥ 300 target (49 % headroom; N=16 vs req 11)  |
| INV-02 | high     | PASS   | S_x=3133, S_y=2467 ≤ 3450 (SHR limit)                 |
| INV-03 | high     | PASS   | 3 entrances / 3 switches at 3 latch sides             |
| INV-04 | high     | PASS   | 4 row circuits, no Z-pattern, homerun W               |
| INV-05 | high     | PASS   | 144 W per circuit ≤ 1104 W (6A 80 % cap)              |
| INV-06 | high     | PASS   | part_l_assessed + occupancy + daylight + 125 lm/W     |
| INV-07 | medium   | PASS   | Z1 perimeter (S glazing) + Z2 interior consistency    |
| INV-08 | medium   | PASS   | selection_source.ontology_default + LG7 citation      |
| INV-09 | medium   | PASS   | drafting_furniture complete, Arial 8/10 pt            |
| INV-10 | high     | PASS   | Schema validation OK, no non_compliance_flags         |

All 10 INVs PASS. No `non_compliance_flags` raised.

## 10. Engineer notes

- **Classroom-specific UGR**: BS EN 12464-1 prefers UGR ≤ 16 for
  sustained reading and writing tasks. This example uses the LED_PANEL_600
  ontology default UGR ≤ 19. A real classroom specification would require
  UGR ≤ 16 luminaires (typically a low-glare optic variant) — the lumen
  method itself does not change but the luminaire selection narrows.
- **Acoustic interaction**: classrooms are reverberant; suspended LED
  panels often double as acoustic panels (perforated metal pan, mineral
  wool fill). Out of scope for the lighting-layout skill; flagged for
  the acoustics skill (stub in mechanical/).
- **Fire-exit lighting independence**: the N fire-exit entry point
  (SW02) controls a single row circuit (C-L04). In a real classroom
  the fire-exit also requires BS 5266-1 emergency lighting on the
  escape route — delivered by the emergency-lighting skill (deferred)
  with self-contained luminaires and a separate emergency-lighting
  zone, not modelled here.
- **Adjoining-classroom door (W)**: communicating doors between
  classrooms often have NO wall switch (the adjoining room owns its
  own lighting controls). This example assumes the adjoining-room door
  IS controllable from the entered classroom — common when the door
  is part of a daily entry path (e.g. shared resource room or shared
  teacher office). If the door is purely for evacuation/inspection,
  SW03 can be omitted and INV-3 Rule 1 still PASSes (switches=2 for
  2 'occupant' entrances).
- **Acoustic-zone vs daylight-zone divergence**: the daylight perimeter
  (Z1) here is 4 luminaires along the S wall. The classroom's acoustic
  treatment may need a different fitting at the front-of-room
  whiteboard wall — out of scope, flagged for acoustics + integrated
  design review skills.
