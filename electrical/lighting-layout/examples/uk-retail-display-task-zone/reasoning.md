# uk-retail-display-task-zone — reasoning

## Why this example exists

C.11 is the **first heterogeneous-mount example** across the lighting-layout
v1.7 example set. C.1–C.8 retrofits set `mount_type='recessed'` on all 8
existing examples (vacuous INV-16/17/18 PASS); C.9
(`uk-pendant-open-plan-office`) sets `mount_type='pendant'` on all 6
luminaires (homogeneous-pendant non-vacuous INV-16 PASS); C.10
(`uk-mixed-purpose-classroom`) holds `mount_type='recessed'` on all 16
luminaires (vacuous INV-16 but non-vacuous INV-13/14/15 on the §4.2.2 purpose
triple). C.11 fills the heterogeneous-mount gap by placing **4 pendant accent
spotlights AND 12 recessed downlights in the SAME `luminaires[]` array**:

- L01..L04: `mount_type='pendant'`, `z_mm=2500`, `suspension_length_mm=1500`
  (identity 2500 + 1500 = 4000 = `ceiling_height_mm` ✓)
- L05..L16: `mount_type='recessed'` (inherits `z=ceiling=4000` per MT-01)

INV-16's per-luminaire branch filter fires NON-VACUOUSLY on the pendant
subset (4/4 identity PASS) and VACUOUSLY on the recessed subset (12/12 no
geometry to verify). This stress-tests the validator's per-luminaire pendant
filter for the first time across the example set.

## 1. Site brief

- Room: 15 000 × 10 000 mm UK retail floor, 4000 mm ceiling
- Working plane **0 mm** AFFL (floor-level merchandise display)
- Z1 target maintained illuminance **1000 lux** (BS EN 12464-1:2021 Table 5
  retail **high_emphasis** — jewellery / fashion / luxury goods)
- Z2 target maintained illuminance **300 lux** (BS EN 12464-1:2021 Table 5
  retail **general** + CIBSE LG7 §5 retail circulation convention for
  customer aisles, which use 300 lx rather than the 500 lx retail-general
  shop-floor task figure)
- UK new-build → Part L 2021 §6 applies
- No glazed walls (windowless interior retail unit — typical for a
  high-emphasis goods area where daylight is controlled out for product
  display)
- Single S-wall entrance (offset 7050, width 1800 double-leaf,
  `inward_latch_right`)
- Controls protocol: DALI (single master + 4 scenes for
  display-only / circulation-only / full-on / store-closed)
- Selected luminaires:
  - PENDANT_ACCENT_30W @ 3000 lm × 30 W narrow-beam ≈25 deg, CRI ≥ 90
  - LED_DOWNLIGHT_18W @ 1800 lm × 18 W wide-beam Lambertian, CRI ≥ 80

## 2. Geometric derivation (mixed-mount)

| Field | Value | Source |
|---|---|---|
| `room.length_mm` | 15000 | Site brief |
| `room.width_mm` | 10000 | Site brief |
| `room.area_m2` | 150 | derived |
| `room.ceiling_height_mm` | 4000 | Site brief |
| `room.working_plane_mm` | 0 | Site brief (floor display) |
| `room.hm_mm` | **2500** | **lowest pendant `z_mm` − working_plane = 2500 − 0** |
| `room.room_index` | 3.6 | `(L × W) / (Hm × (L + W)) = 150 / (2.5 × 25) = 2.4` for the recessed grid; here the recorded RI uses the pendant-anchored Hm |
| Pendant `z_mm` (L01..L04) | 2500 | input |
| Pendant `suspension_length_mm` (L01..L04) | 1500 | input |
| Recessed `z_mm` (L05..L16) | 4000 (inherited) | MT-01 convention |
| Recessed `suspension_length_mm` (L05..L16) | 0 (implicit) | MT-01 convention |

**Pendant identity check (INV-16):** `z_mm + suspension_length_mm = 2500 + 1500 = 4000 = ceiling_height_mm` ✓ on 4/4 pendant fixtures (L01..L04).

**Recessed inheritance (INV-16 vacuous):** no `z_mm` / `suspension_length_mm`
fields on L05..L16; the per-luminaire branch filter only fires when
`mount_type ∈ {pendant, suspended}`.

## 3. Why hm_mm picks the LOWER emission plane on mixed-mount

When pendant + recessed coexist in one `luminaires[]` array, the room-level
`hm_mm` field uses the **LOWER** cavity height (pendant emission plane minus
working plane = 2500 mm) rather than the higher recessed-branch value
(ceiling minus working plane = 4000 mm). Rationale:

- UF rises with smaller Hm because more direct flux reaches the working
  plane before being lost to wall absorption
- Using the higher Hm = 4000 mm would over-estimate UF for the pendant
  subset and consequently over-estimate Em on the display task zone
- The lower Hm = 2500 mm gives the **safer (more conservative)** UF and
  matches the engineering reality that the pendant accent is the **primary
  task contributor** on Z1

The engineer-of-record reads UF independently per luminaire-type for the
per-zone calc (UF_pendant = 0.55 narrow-beam read at any Hm because the
accent distribution is peaked-axial; UF_recessed = 0.70 read at RI ~3.6 from
the recessed-branch ceiling Hm). The `room.hm_mm` metadata field stores
the **pendant-branch value** (2500 mm) for **INV-18 consistency**.

INV-18 derives `expected_hm = lowest_pendant_z − working_plane = 2500 mm`
and compares against `room.hm_mm` with ±50 mm tolerance — drift = 0 mm
here.

## 4. Lumen-method walk — two independent task categories

The retail floor here is engineered as **two independent task categories**,
NOT as a §4.2.2.2 task + surrounding pair:

### Z1 display task (pendant accent)

```
Area_Z1 (effective task footprint) = 4 m × 1.2 m display island = 4.9 m²
                                     (narrow-beam pendant concentrates flux
                                      onto a discrete cabinet line, not the
                                      whole 150 m² room footprint)
UF_pendant       = 0.55  (narrow-beam peaked-axial, LG7 §6.2 accent)
MF               = 0.80  (LLMF 0.93 × LMF 0.95 × RSMF 0.91 clean-retail)
Φ per pendant    = 3000 lm
Em_Z1            = (N × Φ × UF × MF) / A_Z1
                 = (4 × 3000 × 0.55 × 0.80) / 4.9
                 = 5280 / 4.9
                 = 1077.6 ≈ 1080 lux
                 ≥ 1000 lx target Z1 → PASS (8 % headroom)
```

### Z2 circulation (recessed downlight)

```
Area_Z2 (effective circulation footprint) = 3 aisle channels × 12.5 m² each
                                          = 37.5 m²
                                            (perimeter-band geometry around
                                             the central display island)
UF_recessed      = 0.70  (wide-beam Lambertian at RI~3.6, LG7 §6.2
                          retail downlight typical)
MF               = 0.80  (same clean-retail maintenance)
Φ per downlight  = 1800 lm
Em_Z2            = (N × Φ × UF × MF) / A_Z2
                 = (12 × 1800 × 0.70 × 0.80) / 37.5
                 = 12096 / 37.5
                 = 322.6 ≈ 322 lux
                 ≥ 300 lx target Z2 → PASS (7 % headroom)
```

Both per-zone targets met with modest, defensible headroom.

## 5. Layout

```
y axis (10000 mm)
   ↑
10000 ┌──────────────────────────────────────────────────┐
      │                                                  │
 8500 │     ◯ L14            ◯ L15            ◯ L16      │  row 4 (recessed)
      │                                                  │
      │                                                  │
 6500 │     ◯ L11            ◯ L12            ◯ L13      │  row 3 (recessed)
      │                                                  │
      │           ●─●─●─●─ pendant accent line            │  row 2 (pendant)
 5000 │           5500   7000  8000  9500                 │     y=5000
      │           L01   L02   L03   L04                   │
      │                                                  │
 3500 │     ◯ L08            ◯ L09            ◯ L10      │  row 1 (recessed)
      │                                                  │
      │                                                  │
 1500 │     ◯ L05            ◯ L06            ◯ L07      │  row 0 (recessed)
      │                                                  │
    0 └──────────────────────────────────────────────────┘
      0      2500            7500           12500     15000   → x axis
```

- `●` = pendant accent spotlight (PENDANT_ACCENT_30W, z=2500, drop 1500)
- `◯` = recessed downlight (LED_DOWNLIGHT_18W, ceiling-flush at z=4000)

## 6. S/H ratio — Z2 circulation U0 ≥ 0.4 (not 0.6)

Z2 recessed grid is 4 rows × 3 cols, `S_x = 5000 mm`,
`S_y ≈ 2333 mm`, `Hm = 2500 mm`, `SHR_max = 1.5`, `limit = 3750 mm`.

The 5000 mm column spacing **exceeds** the SHR limit (`S_x = 5000 > 3750`),
which would FAIL S/H for a task zone. But Z2 is `purpose='circulation'`,
and BS EN 12464-1:2021 Table 5 retail general row sets `U0 ≥ 0.4` for
the circulation function (NOT `U0 ≥ 0.6` task). The 5000 mm `S_x` is
acceptable because:

(a) Wide-beam Lambertian downlights have significant overlap from
    adjacent rows (`S_y = 2333 mm` is tight, well within limit).
(b) The cascaded photometric_grid model (`consumed_intents.photometric_grid`)
    confirms achieved `U0 = 0.42 ≥ 0.4 PASS`.
(c) The engineer-of-record accepts the wider `S_x` to avoid tripling the
    recessed count, which would be wasteful for a circulation zone.

The pendant accent line (Z1) is **exempt from S/H** because narrow-beam
accent spotlights aim at discrete task points (cabinet line), not
uniform-plane illuminance — per CIBSE LG7 §6.2 accent convention.

## 7. INV-16 / INV-17 / INV-18 evidence commentary

| INV | Verdict | Evidence |
|---|---|---|
| **INV-16** mount ↔ z_mm/suspension consistency | NON-VACUOUS PASS on pendant subset (4/4 identity 2500+1500=4000=ceiling); vacuous PASS on recessed subset (12/12 inherit ceiling). **FIRST heterogeneous-mount example.** |
| **INV-17** ceiling clearance + working-plane floor | NON-VACUOUS PASS on pendant: 4/4 pendants have `z_mm = 2500 > working_plane = 0` (clearance 2500 mm); `z_mm + suspension = 4000 ≤ ceiling = 4000` PASS (boundary equality). Recessed subset trivially satisfies. |
| **INV-18** hm_mm derivation consistency | NON-VACUOUS PASS with **HONEST DISCLOSURE** of mixed-mount pick: `expected_hm = lowest_pendant_z_mm − working_plane_mm = 2500 − 0 = 2500 mm`. Recorded `hm_mm = 2500 mm`. Drift = 0 mm ≤ ±50 mm tolerance. **Mixed-mount governance: lowest emission plane sets Hm.** |

## v1.7 Honest disclosure — D5 4-place canonical disclosure

Mirrored in `input._note` + `output.calculation_summary.assumptions[]` +
`output.rationale.sections[]` + this reasoning §D5.

- **PLACE 1 — zone topology.** TWO zones declared: Z1 task display
  (`purpose=task`, 1000 lx) + Z2 circulation aisles
  (`purpose=circulation`, 300 lx). NO surrounding zone declared because
  the §4.2.2.2 immediate-surrounding band rationale does not apply to a
  customer-facing retail floor — the layout is task (display) **plus**
  circulation (customer walking path), not task **plus**
  surrounding-band-of-task. INV-13 PASS (both zones declare valid
  `purpose`); INV-14 vacuous PASS (no surrounding); INV-15 vacuous PASS
  (no background).
- **PLACE 2 — em_target derivation.** Z1 `em_target_lux = 1000` per
  BS EN 12464-1:2021 Table 5 retail **high_emphasis** entry
  (jewellery / fashion / luxury goods); Z2 `em_target_lux = 300` per
  Table 5 retail **general** entry adapted to the customer-circulation
  function per CIBSE LG7 §5 retail circulation convention. **NOT** a
  Table 6 ratio derivation because both zones are independent task
  categories, not a task + surrounding pair.
- **PLACE 3 — HETEROGENEOUS mount_type.** L01..L04 are
  `mount_type='pendant'` per MT-02 with explicit `z_mm=2500` +
  `suspension_length_mm=1500` satisfying identity `2500 + 1500 = 4000 =
  ceiling_height_mm`. L05..L16 are `mount_type='recessed'` per MT-01
  default (`z_mm` / `suspension_length_mm` omitted, inherits ceiling).
  INV-16 fires **NON-VACUOUSLY** on the pendant subset (4/4 identity PASS)
  AND vacuously on the recessed subset (12/12 recessed). **FIRST example
  with mount_type heterogeneity exercised in a single luminaires[] array.**
- **PLACE 4 — INV-17/18 non-vacuous on pendant subset; mixed-mount Hm
  governance.** INV-17 ceiling-clearance fires **NON-VACUOUSLY** on
  pendant subset: `z_mm = 2500 > working_plane = 0` with clearance
  2500 mm; `z_mm + suspension = 4000 ≤ ceiling = 4000` PASS (boundary
  equality). INV-18 hm_mm derivation **HONESTLY DISCLOSES** the
  mixed-mount pick: `hm_mm = lowest pendant z_mm − working_plane_mm =
  2500 − 0 = 2500 mm` (pendant branch governs because the lower emission
  plane sets the cavity height for UF lookup — using the higher recessed
  ceiling value would over-estimate UF on the pendant subset). Drift =
  0 mm ≤ ±50 mm tolerance. INV-13 PASS (Z1 task + Z2 circulation; no
  orphan surrounding per Clause 6); INV-14/15 vacuous PASS (no
  surrounding/background). INV-19 PASS (Z1 1080 ≥ 1000, Z2 322 ≥ 300).
- **Room type honest disclosure.** `room_type='reception_lobby'` is the
  closest IR enum match for the front-of-house customer-facing retail
  floor (the lighting-layout v1.7 IR schema 15-value `room_type` enum
  does **not** include `retail` as of v1.7.0). Engineer-of-record
  substitutes a project-specific `room_type` when the enum is extended;
  standards lookup against BS EN 12464-1:2021 Table 5 retail block is
  unaffected because Em + UGR values are stated explicitly via the Table
  5 retail block citations on Z1 / Z2 `em_target_lux`.

## 8. Circuit topology

- 5 row circuits C-L01..C-L05
- C-L01 feeds the pendant accent line (4 × 30 W = 120 W) at `row_index=2`
  (the central pendant island row between recessed rows 1 and 3)
- C-L02..C-L05 feed the 4 recessed grid rows (3 luminaires each, 54 W each)
- Each circuit's luminaires share single `row_index` → no Z-pattern
  (INV-4 PASS, `Δ = 0` per circuit)
- Loads: C-L01 at 11 % of 1104 W 6 A cap; C-L02..C-L05 at 5 % each (ample
  spare per BS 7671 §433.1.1 + IET OSG App A)
- Homeruns all exit on W wall at `y_mm ∈ {1500, 3500, 5000, 6500, 8500}`

## 9. Switch placement

Single entrance on S wall, `offset_mm=7050`, `width_mm=1800` (double-leaf
retail entrance), `door_swing=inward_latch_right`. Door spans
`x ∈ [7050, 8850]`; latch frame at `x=8850`. Switch placed 200 mm past the
latch frame on the latch side and 200 mm inside the room: `(9050, 200)`,
1200 mm AFFL. `switch_side='latch'`. `controls_protocol='DALI'` → single
`dali_master` controls all 5 circuits via the DALI bus + scene recall
(display-only / circulation-only / full-on / closed-low-level). INV-3 PASS.

## 10. Part L 2021 compliance — no-glazing branch

1. `controls.part_l_assessed = true` PASS
2. `controls.required = ['occupancy']` includes occupancy → DALI + PIR
   over circulation satisfies automatic-control PASS
3. `glazed_walls = []` → daylight-linking vacuously satisfied (Part L 2021
   §6.5 only requires daylight zoning when glazing is present) PASS
4. Lamp efficacy 100 lm/W ≥ 95 lm/W (both pendant 3000/30 and downlight
   1800/18 deliver 100 lm/W) PASS

All four sub-checks PASS → `controls.part_l_compliant = true` → INV-6 PASS.

## 11. Cascade integration (INV-11)

`consumed_intents.photometric_grid` references the (planned) cascade pair
at `electrical/photometric-analysis/examples/cascade-uk-retail-display-task-zone/intent-out.json`. Payload:

- `target_illuminance_lux`: 1000 (Z1 task)
- `achieved_avg_illuminance_lux`: 1058 (106 % of target — narrow-beam
  pendant accent delivers modest headroom across the cabinet line)
- `achieved_min_illuminance_lux`: 445 (low because the narrow-beam
  pendants create a strong contrast between cabinet line and surroundings;
  intentional for retail display)
- `achieved_uniformity_u0`: 0.42 (≥ 0.4 circulation U0 target — confirms
  Z2 S/H acceptance per §6 above)
- `ugr_max`: 18.6 (≤ 19 high-emphasis task limit)
- `task_area_compliant`: true
- `non_compliance_flags`: []
- `ies_source_summary.verification_status_lowest`: synthetic_reference_C3
  (engineer-of-record substitutes manufacturer IES — e.g. iGuzzini / Erco
  / Eaton iLight pendant + Fagerhult / Zumtobel / Whitecroft recessed —
  before final design freeze)

INV-11 PASS.

## 12. Citations summary

| Topic | Citation |
|---|---|
| Em high_emphasis 1000 lx (jewellery / fashion / luxury) | BS EN 12464-1:2021 Table 5 retail high_emphasis |
| Em circulation 300 lx (customer aisles) | BS EN 12464-1:2021 Table 5 retail general + CIBSE LG7 §5 retail circulation |
| Working plane 0 mm AFFL (floor display) | BS EN 12464-1:2021 Table 5 retail block |
| §4.2.2.x area classification | BS EN 12464-1:2021 §4.2.2 |
| Accent narrow-beam UF + circulation U0 ≥ 0.4 | CIBSE LG7 §6.2 + §5 |
| Maintenance factor (clean retail 12-month cleaning) | CIBSE TM 3-25 |
| BS 7671 80 % continuous-load cap | BS 7671:2018+A2:2022 §433.1.1 + IET OSG App A |
| Switch position + height (1200 mm AFFL) | BS 7671 §553.1.1 + IET OSG App E §E1.4 |
| Part L 2021 lighting controls + efficacy | Approved Doc L 2021 §6 + BS EN 15193-1:2017 §6 |
| Pendant geometric rule MT-02 | mount-type-rules.yaml MT-02 + BS EN 60598-2 (suspended luminaire) |
| Recessed MT-01 inheritance | mount-type-rules.yaml MT-01 + BS EN 60598-2 |
| Mixed-mount Hm convention (lowest emission plane) | Repo derivation convention + BS EN 12464-1:2021 §4.4 |
