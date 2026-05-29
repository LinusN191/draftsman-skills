# Example: Reception Lobby — Reasoning

Demonstrates the full lighting-layout vocabulary on an 8×5 m UK commercial
reception lobby with a glazed entrance wall. Promoted from `calc_only` stub
to `full_drawing` depth in Sprint D3.C.1.

## 1. Site brief

- Room: 8000 × 5000 mm reception lobby (40 m²), 2700 mm finished ceiling
- Glazed entrance wall on south (primary entrance, full-height glazing)
- Working plane: floor level (0 mm) per BS EN 12464-1:2021 Table 5.3
  reception (lobby circulation lighting is general, not task-based)
- Target maintained illuminance: 300 lux per BS EN 12464-1:2021 Table 5.3
  entry for `reception_lobby`
- UGR limit: ≤19 (confirm from photometric data)
- New-build UK (jurisdiction=england_wales) — Approved Doc L (Part L 2021)
  §6 controls + Table 6.2 efficacy target applies
- Selected luminaire: LED_DOWNLIGHT (100 mm recessed prismatic), 1000 design
  lumens, 10 W, 3000 K CCT (warm welcome tone), CRI ≥ 90 (art / display
  rendering), IP20

## 2. Lumen-method walk

```
Area A     = 8 × 5                          = 40 m²
Hm         = 2700 − 0                       = 2700 mm  = 2.7 m
RI         = (8 × 5) / (2.7 × (8 + 5))      = 40 / 35.1
                                            = 1.14
            → ontology table key 1.0 (next-lower band per LG7 §6.2)
UF         = 0.48  [LED_DOWNLIGHT @ RI=1.0, reflectances 0.7/0.5/0.2]
             (ontology source: CIBSE LG7 §6.2 + BS EN 12464-1 §4.4)
LLMF       = 0.88   (normal indoor maintenance, 6000h schedule)
LMF        = 0.95   (clean lobby, no industrial deposit)
MF         = LLMF × LMF
           = 0.88 × 0.95                    = 0.836  ≈ 0.84
N          = (Em × A) / (Φ × UF × MF)
           = (300 × 40) / (1000 × 0.48 × 0.84)
           = 12000 / 403.2                  = 29.77
           → round UP to 30  (never under-provide light)
Achieved   = (N × Φ × UF × MF) / A
           = (30 × 1000 × 0.48 × 0.84) / 40
           = 302.4 lux                      ≥ 300 target  → INV-1 PASS
```

Reference: `[spacing-rules#lumen-method-formula]`, `[spacing-rules#room-index]`.

## 3. S/H ratio enforcement

30 luminaires arranged in a 5 rows × 6 cols grid in an 8000 × 5000 room with
300 mm edge clearance (per `[placement-rules#edge-clearance]` — within the
300–600 mm wall-clearance band).

```
Edge clearance      = 300 mm  (both axes)
Cols (x-axis)       = 6   → spacings between centres = 5
S_x   = (8000 − 2 × 300) / 5 = 7400 / 5    = 1480 mm
Rows (y-axis)       = 5   → spacings between centres = 4
S_y   = (5000 − 2 × 300) / 4 = 4400 / 4    = 1100 mm

Hm           = 2700 mm
SHR_max      = 1.4   (LED_DOWNLIGHT ontology default — narrow beam)
Limit        = SHR_max × Hm = 1.4 × 2700   = 3780 mm
S_x = 1480 mm  ≤  3780 mm  → PASS
S_y = 1100 mm  ≤  3780 mm  → PASS
                                           → INV-2 PASS
```

Both directions sit well under the SHR_max ceiling — the narrow beam of the
LED_DOWNLIGHT is fully respected. The room is small enough that we are
operating in the "spacing limited by grid symmetry" regime, not the
"spacing limited by SHR" regime.

## 4. Part L 2021 zoning

The glazed south entrance wall triggers a perimeter daylight zone (per
`[control-rules#part-l-daylight]` + Approved Doc L 2021 §6.2 + BS EN 15193-1
§6.2). All luminaires within 1500 mm of the glazed wall move to a separately
switched / dimmed circuit:

| Zone | zone_type | Control protocol | Luminaires       | Circuits | Load |
|------|-----------|------------------|------------------|----------|------|
| Z1   | perimeter | daylight_linked  | L01..L06 (row 0) | C-L01    | 60 W |
| Z2   | interior  | occupancy        | L07..L30 (rows 1..4) | C-L02..C-L05 | 240 W |

- Z1 (6 luminaires at y=300, within 1500 mm of glazed S wall): 0-10V dimming
  driven by photocell + manual override at SW01
- Z2 (24 luminaires, rows 1–4 at y ∈ {1400, 2500, 3600, 4700}): occupancy
  detection (presence-with-absence-detection) + manual override at SW01

Lamp efficacy 100 lm/W ≥ Part L 2021 Table 6.2 target 95 lm/W → PASS per
`[control-rules#part-l-efficacy-target]`. `controls.required` lists both
`occupancy` and `daylight_linking` — both delivered (INV-7 PASS).

## 5. Switch placement

Single primary entrance on the S wall. One 2-gang switch (SW01) inside the
room, 200 mm from the door frame on the latch side (`door_swing` =
`inward_latch_right` → latch on the right when entering → switch goes to
the right of the door):

```
Switch SW01:
  type            = 2_gang           (independent Z1 + Z2 control)
  position        = (2700, 200) mm   (200 mm inside S wall from latch side)
  height_aff_mm   = 1200             (centre to FFL per BS 7671 §553.1.1
                                     + IET OSG App E §E1.2)
  controls        = C-L01, C-L02     (master for daylight + occupancy)
```

Manual override via SW01 satisfies Approved Doc L 2021 §6.2 user-control
requirement for automatic controls (`[control-rules#manual-switch-override]`).

## 6. Circuit topology

5 row circuits on DB L1, one per row (avoiding any Z-pattern daisy-chain
that would mix rows on a single circuit):

```
Circuit   Zone   Row   Luminaires            Load   MCB     Homerun
C-L01     Z1     0     L01..L06              60 W   6A B    (0, 300, W)
C-L02     Z2     1     L07..L12              60 W   6A B    (0, 1400, W)
C-L03     Z2     2     L13..L18              60 W   6A B    (0, 2500, W)
C-L04     Z2     3     L19..L24              60 W   6A B    (0, 3600, W)
C-L05     Z2     4     L25..L30              60 W   6A B    (0, 4700, W)
```

Every circuit's `luminaire_ids` share the same `row_index` — INV-4 PASS
(no Z-pattern). Homeruns all exit on W wall, stacked at each row's y_mm.

INV-5 80% continuous-load check: each circuit carries 6 × 10 W = 60 W,
which is 5.4% of the 6 A MCB headroom (0.8 × 6 × 230 = 1104 W). Massive
spare for future fixture additions. PASS per BS 7671:2018+A2:2022 §433.1.1
+ IET OSG App A.

## 7. INV walkthrough

| INV    | Severity | Status | Evidence                                      |
|--------|----------|--------|-----------------------------------------------|
| INV-01 | high     | PASS   | 302.4 lux ≥ 300 target (lumen method)         |
| INV-02 | high     | PASS   | S_x=1480, S_y=1100 ≤ 3780 (SHR limit)         |
| INV-03 | high     | PASS   | 1 entrance / 1 switch, 1200 AFF, latch side   |
| INV-04 | high     | PASS   | 5 row circuits, no Z-pattern, homerun on W    |
| INV-05 | high     | PASS   | 60 W per circuit ≤ 1104 W (6A 80% cap)        |
| INV-06 | high     | PASS   | Lamp 100 lm/W ≥ Part L 95 lm/W target         |
| INV-07 | medium   | PASS   | Glazed S → Z1 perimeter present + controls    |
| INV-08 | medium   | PASS   | selection_source.ontology_default + citation  |
| INV-09 | medium   | PASS   | drafting_furniture complete, Arial 8/10 pt    |
| INV-10 | high     | PASS   | Schema validation OK, all required fields     |

All 10 INVs PASS. No `non_compliance_flags` raised.

## 8. Engineer notes

- **CCT 3000K (warm)**: appropriate for lobby ambience and hospitality —
  cooler temperatures (4000K+) would feel clinical at an entrance.
- **CRI ≥ 90**: lobbies often display art, joinery, or feature finishes —
  CRI 90 reproduces those colours faithfully. CRI 80 would suffice
  technically but reads "cheap" against finishes.
- **0-10V dimming vs DALI cost trade-off**: For a small 2-zone lobby,
  0-10V is the right answer — cheaper drivers, simpler commissioning,
  no addressing overhead. DALI would only pay off above ~4 independent
  zones or when scene control is part of the brief. Spec'd 0-10V here;
  the validator does not penalise this choice for a lobby of this size.
- **Entrance transition (BS 8300-2)**: in bright daylight the exterior
  illuminance may reach 50,000 lux at the door threshold. The 300 lux
  lobby gives a 167:1 step ratio. This is too steep for accessible
  transition; mitigation is the daylight-linked perimeter Z1 (boosts
  the immediate-inside-door zone toward exterior levels when daylight
  is high). BS 8300-2:2018 §10 informs this design; full transition
  zone modelling is out of scope for the lobby skill and lands in a
  future `transition-luminance` skill (deferred).
- **Emergency lighting**: this layout does NOT include emergency luminaires.
  The lobby is the primary entrance / escape route and requires BS 5266-1
  emergency lighting in a real project — that is delivered by the separate
  `emergency-lighting` skill (deferred). The lighting-layout IR could
  declare an emergency zone Z3 here; the example keeps scope tight to
  general lighting + Part L controls for D3.C.1 demonstration.
