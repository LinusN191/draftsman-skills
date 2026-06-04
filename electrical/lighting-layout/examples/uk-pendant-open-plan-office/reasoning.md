# uk-pendant-open-plan-office — reasoning

## Why this example exists

C.9 is the **first fully-pendant example** across the lighting-layout example set. C.1–C.8 retrofits added `mount_type='recessed'` to all 8 existing examples; C.9 is the first NEW example where `mount_type='pendant'` is the canonical choice. The scenario stress-tests the MT-02 pendant geometric identity end-to-end:

> `z_mm + suspension_length_mm = ceiling_height_mm`

Until C.9 all INV-16 / INV-17 / INV-18 evidence across the example set was VACUOUS (no pendant or suspended luminaires present). From C.9 onward the example set demonstrates the pendant geometric contract under three structural invariants firing non-vacuously at the same time.

## 1. Geometric derivation

| Field | Value | Source |
|---|---|---|
| `room.length_mm` | 12000 | Spec §8.2 NEW#1 |
| `room.width_mm` | 8000 | Spec §8.2 NEW#1 |
| `room.ceiling_height_mm` | 3500 | Spec §8.2 NEW#1 |
| `room.working_plane_mm` | 750 | BS EN 12464-1:2021 Table 5.26.1 office desk plane |
| `room.hm_mm` | 1950 | Derived: `z_mm − working_plane_mm = 2700 − 750 = 1950` |
| `luminaire.mount_type` | pendant | MT-02 |
| `luminaire.suspension_length_mm` | 800 | Spec §8.2 NEW#1 |
| `luminaire.z_mm` | 2700 | Derived: `ceiling − suspension = 3500 − 800 = 2700` |

**Pendant identity check:** `z_mm + suspension_length_mm = 2700 + 800 = 3500 = ceiling_height_mm` ✓

This identity verifies on all 6 luminaires (L01..L06) — INV-16 NON-VACUOUS PASS.

## 2. Why this matters: the wrong-Hm bug class

Before MT-02 the canonical engineer mistake on pendant designs was computing `hm_mm = ceiling_height_mm − working_plane_mm = 3500 − 750 = 2750 mm` — treating the pendant as if it were recessed at ceiling level. That over-states cavity height by 800 mm (41 %), which feeds into the room-index calculation:

- **Wrong RI** (using Hm=2750): `RI = 96 / (2.75 × 20) = 1.75` → UF band 1.5 = 0.60
- **Correct RI** (using Hm=1950): `RI = 96 / (1.95 × 20) = 2.46` → UF band 2.5 = 0.69

A 15 % UF underestimate would inflate the required luminaire count and waste budget. The pendant identity catches the wrong-Hm bug **structurally**: INV-18 derives `expected_hm = z_mm − working_plane = 1950` and compares against `room.hm_mm` with a 50 mm tolerance — drift = 0 mm here.

## 3. Lumen-method walk (per-zone Em derivation)

| Step | Value |
|---|---|
| Area `A` | `12 × 8 = 96 m²` |
| Cavity height `Hm` | `z − wp = 2700 − 750 = 1950 mm = 1.95 m` |
| Room index `RI` | `(L × W) / (Hm × (L + W)) = 96 / (1.95 × 20) = 96 / 39 = 2.46` → band 2.5 |
| UF (LINEAR_LED @ RI=2.5, 0.7/0.5/0.2) | 0.69 |
| MF (LLMF 0.95 × LMF/RSMF combined) | 0.80 |
| Φ per luminaire | 15600 lm (design) |
| `N_required` | `(500 × 96) / (15600 × 0.69 × 0.80) = 48000 / 8610.24 = 5.575` |
| `N_final` | round UP → 6 |
| Achieved Em | `(6 × 15600 × 0.69 × 0.80) / 96 = 51667.2 / 96 = 538.2 lx` |
| Target Em | 500 lx |
| Headroom | 7.6 % |

Single Z2 task zone covers the full 12 × 8 m footprint — no §4.2.2.2 surrounding/background split because the 3 × 2 pendant rhythm distributes uniformly without an inset task rectangle.

## 4. Layout (3 rows × 2 cols)

```
y axis (8000 mm)
  ↑
  │           edge_x = 3000             edge_x = 3000
  │              ↓                          ↓
8000┌──────────────────────────────────────────┐
  │ │                                          │
6667│        ● L05                  ● L06       │  ← row 2
  │ │                                          │
  │ │                                          │
4000│        ● L03                  ● L04       │  ← row 1
  │ │                                          │
  │ │                                          │
1333│        ● L01                  ● L02       │  ← row 0
  │ │                                          │
  0  └──────────────────────────────────────────┘
     0      3000                  9000      12000  → x axis (12000 mm)
                  ┘                       └
                S_x = 6000 mm (longitudinal — linear axis along x;
                               not subject to SHR_max per LG7 §6.2 convention)

     S_y = 2667 mm transverse between rows ≤ SHR_max × Hm = 3120 mm PASS
```

Luminaires `LINEAR_LED_PENDANT_1200` are 1200 mm long × 200 mm wide, suspension drop 800 mm, emission plane at z = 2700 mm.

## 5. S/H ratio — transverse-only for linear pendants

SHR_max = 1.6 (LINEAR_LED ontology default per CIBSE LG7 §6.2 linear LED batten convention). Hm = 1950 mm; limit = `1.6 × 1950 = 3120 mm`.

- **Transverse** S_y between rows = `(8000 − 2 × 1333) / (3 − 1) = 5334 / 2 = 2667 mm ≤ 3120 PASS` (85 % of limit)
- **Longitudinal** S_x within a row = `(12000 − 2 × 3000) / (2 − 1) = 6000 mm` — NOT subject to SHR_max under the linear-luminaire convention because the lengthwise extent of the linear luminaire fills the longitudinal distribution.

Per **CIBSE LG7 §6.2** the S/H check applies transverse to the linear luminaire's long axis (here the 1200 mm axis runs along x). This convention is explicit in LG7 §6.2 for linear LED battens and architectural pendants. INV-2 PASS on the transverse axis.

## 6. INV-16 / INV-17 / INV-18 NON-VACUOUS PASS commentary

| INV | Verdict | Evidence |
|---|---|---|
| **INV-16** mount ↔ z_mm/suspension consistency | NON-VACUOUS PASS | 6 pendants; identity `2700 + 800 = 3500 = ceiling` on 6/6 (drift 0 mm). FIRST non-vacuous INV-16 PASS across the example set. |
| **INV-17** ceiling clearance + working-plane floor | NON-VACUOUS PASS | 6/6 pendants: `z_mm = 2700 > working_plane = 750` (clearance 1950 mm = Hm); `z_mm + suspension = 3500 ≤ ceiling = 3500` PASS. |
| **INV-18** hm_mm derivation consistency | NON-VACUOUS PASS | Pendant branch: `expected_hm = z_mm − working_plane = 2700 − 750 = 1950 mm`; recorded `hm_mm = 1950 mm`; drift = 0 mm ≤ tolerance ±50 mm PASS. |

These three invariants now form a closed proof: the pendant emission plane is **above** the working plane (INV-17 floor), the suspension fits **inside** the ceiling cavity (INV-17 ceiling + INV-16 identity), and the cavity height **propagates correctly** into the lumen-method via `hm_mm` (INV-18). Until C.9 this proof chain was vacuous across every shipped example.

## 7. 4-place canonical honest disclosure

Mirrored in `output.calculation_summary.assumptions[]` and `output.rationale.sections[]`.

- **PLACE 1 — zone topology.** Single Z2 task zone covers the full 12 × 8 m footprint. No §4.2.2.2 surrounding/background split is declared because the 3 × 2 pendant rhythm distributes uniformly across the room — the perimeter-band geometry that would justify a ZP-02 separation is absent. INV-14 and INV-15 are vacuous PASS by design.
- **PLACE 2 — em_target derivation.** Z2 em_target_lux = 500 per BS EN 12464-1:2021 Table 5.26.1 open_plan_office task (no per-zone override).
- **PLACE 3 — mount_type ALL pendant.** All 6 luminaires receive mount_type='pendant' per MT-02 with explicit z_mm=2700 + suspension_length_mm=800 satisfying the algebraic identity `2700 + 800 = 3500 = ceiling_height_mm`. INV-16 fires NON-VACUOUSLY for the first time across the lighting-layout example set (6/6 pendants pass the identity check).
- **PLACE 4 — INV-17/18 non-vacuous.** INV-17 ceiling-clearance fires NON-VACUOUSLY: z_mm = 2700 > working_plane = 750 with 1950 mm clearance; INV-18 hm_mm derivation fires NON-VACUOUSLY: `hm_mm = z_mm − working_plane = 1950 mm`, drift = 0 mm, tolerance ±50 mm PASS. INV-13 PASS (Z2 declares purpose=task); INV-14/15 vacuous PASS (no surrounding / background zones); INV-19 PASS (Z2 task: target 500, achieved 538.2, ratio_compliance=pass).

## 8. Circuit topology

- 3 row circuits C-L01..C-L03, one per row, sharing single row_index (0, 1, 2)
- Each circuit: 2 × 105 W = 210 W on a 6 A MCB curve B (BS 7671 §433.1.1 + IET OSG App A)
- 210 W = 19 % of 1104 W 80 %-continuous-load cap — ample spare
- Homeruns exit on W wall at `y_mm ∈ {1333, 4000, 6667}`
- INV-4 row-share rule PASS (max−min = 0 per circuit); INV-5 80 % cap PASS

## 9. Switch placement

Single entrance on S wall, offset_mm=5500, width_mm=900, door_swing=inward_latch_right. Door spans x ∈ [5500, 6400]; latch frame at x=6400. Switch placed 200 mm past the latch frame on the latch side and 200 mm inside the room: (6600, 200), 1200 mm AFFL. switch_side='latch'. controls_protocol='DALI' → single dali_master controls all 3 row circuits via the DALI bus (no per-circuit gangs needed). INV-3 PASS.

## 10. Part L 2021 compliance — no-glazing branch

1. `controls.part_l_assessed = true` PASS
2. `controls.required = ['occupancy']` includes occupancy → DALI + PIR satisfies automatic-control PASS
3. `glazed_walls = []` → daylight-linking vacuously satisfied (Part L 2021 §6.5 only requires daylight zoning when glazing is present) PASS
4. `controls.lamp_efficacy_lm_per_w = 15600 / 105 = 148.6 ≥ 95` PASS

All four sub-checks PASS → `controls.part_l_compliant = true` → INV-6 PASS.

## 11. Cascade integration (INV-11)

`consumed_intents.photometric_grid` references the (planned) cascade pair at `electrical/photometric-analysis/examples/cascade-uk-pendant-open-plan-office/intent-out.json`. Payload:

- `target_illuminance_lux`: 500
- `achieved_avg_illuminance_lux`: 521 (104 % of target — modest headroom given the 3 × 2 pendant grid and direct/indirect distribution)
- `achieved_min_illuminance_lux`: 412
- `achieved_uniformity_u0`: 0.79 (≥ 0.6 office task target)
- `ugr_max`: 17.4 (≤ 19 office task limit)
- `task_area_compliant`: true
- `non_compliance_flags`: []
- `ies_source_summary.verification_status_lowest`: synthetic_reference_C3 (engineer-of-record substitutes project IES before final design freeze)

INV-11 PASS.

## 12. Citations summary

| Topic | Citation |
|---|---|
| Em task target 500 lx open-plan office | BS EN 12464-1:2021 Table 5.26.1 |
| Working plane 750 mm AFFL office desk | BS EN 12464-1:2021 §4.4 |
| Uniformity Uo ≥ 0.6 office task | BS EN 12464-1:2021 §4.3 |
| §4.2.2.x area classification | BS EN 12464-1:2021 §4.2.2 |
| Linear pendant SHR_max + UF + LLMF | CIBSE LG7 §6.2 |
| Maintenance factor (clean office 3-yr cleaning) | CIBSE TM 3-25 |
| BS 7671 80 % continuous-load cap | BS 7671:2018+A2:2022 §433.1.1 + IET OSG App A |
| Switch position + height (1200 mm AFFL) | BS 7671 §553.1.1 + IET OSG App E §E1.4 |
| Part L 2021 lighting controls + efficacy | Approved Doc L 2021 §6 + BS EN 15193-1:2017 §6 |
| Pendant geometric rule MT-02 | mount-type-rules.yaml MT-02 + BS EN 60598-2 (suspended luminaire) |
