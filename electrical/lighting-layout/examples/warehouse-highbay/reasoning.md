# Example: Warehouse Highbay — Reasoning

Demonstrates the full lighting-layout vocabulary on a 30×20 m UK industrial
warehouse main floor with anti-panic emergency coverage. Promoted from
`calc_only` stub to `full_drawing` depth in Sprint D3.C.1.

## 1. Site brief

- Room: 30000 × 20000 mm warehouse main floor (600 m²), 8000 mm structural
  ceiling, no windows
- Existing building (`new_build=false`) — Approved Doc L (Part L 2021) §6
  controls regime does NOT apply
- Working plane: floor level (0 mm) per BS EN 12464-1:2021 Table 5.3
  warehouse (picking activity is at floor / pallet level)
- Target maintained illuminance: 200 lux per BS EN 12464-1:2021 Table 5.3
  entry for warehouse main aisle
- UGR limit: ≤25 (relaxed vs office 19; appropriate for non-screen-task
  industrial work)
- Open area 600 m² > 60 m² threshold → BS 5266-1:2016 §5.3 anti-panic
  emergency lighting regime applies
- Selected luminaire: HIGHBAY (industrial narrow-beam LED), 22000 design
  lumens, 250 W, 4000 K CCT, CRI ≥ 70, IP54 (industrial environment with
  in-air dust — not full washdown so IP54 rather than IP65)

## 2. Lumen-method walk

```
Area A     = 30 × 20                        = 600 m²
Hm         = 8000 − 0                       = 8000 mm  = 8 m
RI         = (30 × 20) / (8 × (30 + 20))    = 600 / 400
                                            = 1.50
            → ontology table key 1.5 (exact match per LG12)
UF         = 0.62  [HIGHBAY @ RI=1.5, reflectances 0.3/0.3/0.2 industrial]
             (ontology source: CIBSE LG12 + BS EN 12464-1 §4.4)
LLMF       = 0.85   (industrial maintenance, 6000h schedule)
LMF        = 0.78   (industrial dust deposit, 1-year clean cycle)
MF         = LLMF × LMF
           = 0.85 × 0.78                    = 0.663  ≈ 0.66
N          = (Em × A) / (Φ × UF × MF)
           = (200 × 600) / (22000 × 0.62 × 0.66)
           = 120000 / 9002                  = 13.33
           → round UP to 14
                                            (then bumped to 20 by S/H, §3)
Achieved   = (N × Φ × UF × MF) / A
           = (20 × 22000 × 0.62 × 0.66) / 600
           = 300.1 lux                      ≥ 200 target  → INV-1 PASS
```

The achieved value (300 lux) is 50% over the target — this is expected
when the S/H ratio forces a larger grid than the lumen method requires.
Engineering judgment: never under-provide, and excess illuminance can be
trimmed at commissioning or with a DALI retrofit. The 50% headroom also
buys margin against MF degradation between cleaning cycles.

Reference: `[spacing-rules#lumen-method-formula]`, `[spacing-rules#room-index]`.

## 3. S/H ratio enforcement (iterative bump 14 → 16 → 20)

HIGHBAY has SHR_max = 1.0 (narrow beam — most of the light goes straight
down) per ontology default. Hm = 8000 mm → limit = 1.0 × 8000 = 8000 mm.

```
Attempt 1: N = 14 in 2 × 7 grid (edge 1500 mm)
  S_x = (30000 − 3000) / 6 = 4500 mm    ≤ 8000  PASS
  S_y = (20000 − 3000) / 1 = 17000 mm   > 8000  FAIL  ← only 2 rows
  → reject

Attempt 2: N = 16 in 4 × 4 grid (edge 1500 mm)
  S_x = (30000 − 3000) / 3 = 9000 mm    > 8000  FAIL  ← only 4 cols
  S_y = (20000 − 3000) / 3 = 5667 mm    ≤ 8000  PASS
  → reject

Attempt 3: N = 20 in 4 × 5 grid (edge 1500 mm)
  S_x = (30000 − 3000) / 4 = 6750 mm    ≤ 8000  PASS
  S_y = (20000 − 3000) / 3 = 5667 mm    ≤ 8000  PASS
  → accept   → INV-2 PASS
```

Final layout: 20 HIGHBAY in 4 rows × 5 cols, edge clearance 1500 mm.

## 4. Anti-panic emergency coverage (Z3 per BS 5266-1 §5.3)

Open area 600 m² > 60 m² threshold → BS 5266-1:2016 §5.3 anti-panic
regime applies (0.5 lux minimum on unobstructed floor area excluding a
0.5 m border, uniformity ratio ≥ 0.025, duration ≥ 60 min).

5 EMERGENCY luminaires (L21..L25) positioned on the central N-S aisle
(x = 15000 mm) at y ∈ {1000, 4350, 10000, 15650, 19000}:

| ID  | Position (mm)    | Function                              |
|-----|------------------|---------------------------------------|
| L21 | (15000, 1000)    | South entrance / freight door         |
| L22 | (15000, 4350)    | Between highbay rows 0–1              |
| L23 | (15000, 10000)   | Geometric centre (mid-aisle)          |
| L24 | (15000, 15650)   | Between highbay rows 2–3              |
| L25 | (15000, 19000)   | North wall / rear exit                |

- All 5 on dedicated circuit C-EM01, db_designation = LE (Emergency
  distribution board) per BS 5266-1 §6 independent supply requirement
- Self-test drivers (DALI or local) per BS 5266-1 §10 + BS EN 62034:2012
  (monthly function test + annual full-duration test, logged)
- 5 × 10 W = 50 W on 6A MCB (4.5% of 1104 W 80% headroom — ample spare)

**Caveat:** the lighting-layout skill does NOT model the actual emergency
illuminance point grid. Designer must verify floor average ≥ 0.5 lux +
uniformity ≥ 0.025 via the separate `emergency-lighting` skill (deferred).

## 5. Circuit topology

```
Circuit   Zone   Row    Luminaires        Load    MCB     Homerun
C-HB01    Z2     0      L01..L05          1250 W  10A B   (0, 1500, W)
C-HB02    Z2     1      L06..L10          1250 W  10A B   (0, 7200, W)
C-HB03    Z2     2      L11..L15          1250 W  10A B   (0, 12800, W)
C-HB04    Z2     3      L16..L20          1250 W  10A B   (0, 18500, W)
C-EM01    Z3     0*     L21..L25          50  W   6A  B   (0, 10000, W)
```

`*` Emergency circuit C-EM01 spans all 4 rows on the central N-S aisle.
INV-4 row-coherence applies to lighting-row circuits only; emergency
circuits are structurally excepted (they serve the building-wide escape
route per BS 5266-1 §5.3). Documented in INV-4 evidence.

INV-5 80% continuous-load check:
- Highbay rows: **1250 W per circuit**. 6A MCB cap = 0.8 × 6 × 230 =
  1104 W → **1250 > 1104 FAIL** at 6A. Engineer steps up to 10A MCB
  (cap = 1840 W) → **1250 ≤ 1840 PASS** at 67.9% of headroom.
- Emergency circuit: 50 W on 6A → 50 ≤ 1104 PASS at 4.5%.

This is the key engineering call in this example: 250 W highbays on
5-luminaire rows cannot fit a 6A circuit. Don't try to economise by
forcing 6A — step up the MCB.

## 6. Switching

Single roller-door entrance on S wall (likely freight access, possibly
with a personnel wicket door). One 1-gang switch (SW01) inside the room,
200 mm from the door frame on the latch side:

```
Switch SW01:
  type            = 1_gang            (all 4 highbay rows ON together)
  position        = (14500, 200) mm   (200 mm inside S wall from latch)
  height_aff_mm   = 1200              (centre to FFL per BS 7671 §553.1.1)
  controls        = C-HB01..C-HB04   (shift-start ON / shift-end OFF)
```

No zoning rationale for separate switching at this scale — a warehouse
is operated as a whole during a shift. If picking activity later splits
into independent aisle teams, a DALI retrofit can add per-row control
without rewiring (DALI rides on the existing power cables + addressing
layer).

Emergency circuit C-EM01 has no switch interface — self-test independent
per BS 5266-1 §10.

## 7. No Part L assessment (existing building)

`inputs.new_build = false` → Approved Doc L (Part L 2021) §6 controls
regime is NOT triggered. Part L applies to new-build and major-refurbishment
only. Therefore:
- `controls.part_l_assessed = false`
- No occupancy / daylight requirement
- No lamp efficacy target enforcement

`controls.lamp_efficacy_lm_per_w = 88` is recorded for future audit. If
the scope ever changes to a new-build warehouse on this site, the engineer
must upgrade highbay spec to a Part L-compliant ≥ 95 lm/W model (e.g.
22000 lm / 200 W = 110 lm/W is available in the market at small premium).

## 8. INV walkthrough

| INV    | Severity | Status | Evidence                                            |
|--------|----------|--------|-----------------------------------------------------|
| INV-01 | high     | PASS   | 300.1 lux ≥ 200 target (lumen method, S/H-bumped N) |
| INV-02 | high     | PASS   | S_x=6750, S_y=5667 ≤ 8000 (SHR limit), after bumps  |
| INV-03 | high     | PASS   | 1 entrance / 1 switch, 1200 AFF, latch side         |
| INV-04 | high     | PASS   | 4 highbay rows coherent; emergency excepted (BS5266) |
| INV-05 | high     | PASS   | 1250 W ≤ 1840 W (10A 80% cap); 6A FAILS, 10A passes |
| INV-06 | high     | PASS   | new_build=false → Part L not triggered (trivial PASS) |
| INV-07 | medium   | PASS   | No glazing → no perimeter Z1; Z2+Z3 emergency only  |
| INV-08 | medium   | PASS   | selection_source.ontology_default + LG12 citation   |
| INV-09 | medium   | PASS   | drafting_furniture complete, Arial 10/12 pt         |
| INV-10 | high     | PASS   | Schema validation OK, all required fields           |

All 10 INVs PASS. No `non_compliance_flags` raised.

## 9. Engineer notes

- **CCT 4000K (neutral)**: industrial standard for picking-task visibility
  — 4000K renders barcodes, labels, and product packaging crisply. 5000K
  would feel "cooler" / more "industrial" but adds blue-light alertness
  fatigue across an 8h shift. 3000K would mask label colours.
- **CRI 70 acceptable for warehouse**: warehouses don't make colour-critical
  decisions (no merchandising display, no medical / lab work). CRI 70 lets
  manufacturers ship driver-optimised LEDs at lower premium. Upgrade to
  CRI 80 if the warehouse also serves as customer-facing showroom space.
- **IP54 vs IP65**: IP54 (dust-protected + water-spray-protected) is the
  correct call for a dry industrial warehouse with in-air dust. IP65
  (dust-tight + water-jet-protected) is for washdown environments — food
  processing, animal husbandry. Specifying IP65 unnecessarily adds 20–30%
  cost with no benefit for general warehousing.
- **8 m mounting height**: highbay narrow-beam optic delivers 220+ lux at
  floor at this mount with the 22000 lm fixture. At 6 m mount, the same
  fixture would deliver ~390 lux floor — too bright and uneven. At 10 m
  mount, the floor average drops to ~140 lux — under target. The fixture
  was selected for this specific mounting height.
- **DALI retrofit path**: the existing 230V wiring + 10A MCBs can carry
  DALI-2 signalling on the same conductors (DALI rides as a low-voltage
  digital overlay). To retrofit: replace drivers with DALI-2 models,
  add a wall controller at SW01 position, commission addressing. No
  cable replacement needed. Typical cost £25-40/luminaire driver swap.
- **Why not 6A for highbay rows?** A frequent designer trap: 1250 W
  feels like it should fit a 6A circuit (230V × 6A = 1380W rated). It
  doesn't — the BS 7671 §433.1.1 + IET OSG App A 80% continuous-load
  rule caps 6A at 1104 W. 1250 > 1104 FAIL. Step up to 10A (1840 W cap)
  or split into two 3-luminaire circuits at 750 W each on 6A. The
  10A approach is preferred for simplicity (4 circuits not 8).
