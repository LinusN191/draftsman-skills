# Example: Open Plan Office — Reasoning

## Step 1 — Check inputs
Room 10×8m, ceiling 3.0m. Luminaire: 600×600 LED panel, 4500 lm design, 36W, IP20.
No initial lumens flag — design lumens used directly.
No glazed walls specified — no perimeter zone required.
New build England — Part L efficacy check required.
Efficacy = 4500 / 36 = 125 lm/W >> 65 lm/W target. PASS.

## Step 2 — Target illuminance
Room type: open plan office → Em = 500 lux, UGR ≤ 19, Ra ≥ 80.
Source: BS EN 12464-1:2021 Table 5.3.

## Step 3 — Room Index
Hm = 3.0 - 0.75 = 2.25m
RI = (10 × 8) / (2.25 × (10 + 8)) = 80 / 40.5 = 1.98 → use 2.00

## Step 4 — Utilisation Factor
UF from table for RI = 2.00, reflectances 70/50/20: UF = 0.67
[ASSUMPTION: UF = 0.67 from standard reflectance table. Confirm from photometric data.]

## Step 5 — Maintenance Factor
MF = LLMF × LSF × LMF × RSMF = 0.90 × 1.00 × 0.90 × 0.94 = 0.76 → use 0.80 standard
[ASSUMPTION: MF = 0.80 for clean office, LED luminaire. Confirm cleaning schedule with FM.]

## Step 6 — Fixture count (minimum)
N = (500 × 80) / (4500 × 0.67 × 0.80)
N = 40,000 / 2,412 = 16.58 → minimum 17 luminaires required

## Step 7 — Grid selection
17 satisfies the lux equation but cannot form a uniform grid in a 600mm ceiling tile
system. Irregular grids cause uneven illuminance and misaligned tiles.

Candidate grids that meet or exceed 17:
- 3 × 6 = 18: spacing x = 10/3 = 3.33m ≤ 3.375m ✓, spacing y = 8/6 = 1.33m ✓
- 4 × 5 = 20: spacing x = 10/4 = 2.5m ≤ 3.375m ✓,  spacing y = 8/5 = 1.6m ✓

Select 4 × 5 = 20: column pitch 2500mm and row pitch 1600mm both divide cleanly into
the 600mm ceiling grid (2400mm, 3600mm column positions; 1600mm, 3200mm row positions).
The 3 × 6 option gives an x-pitch of 3333mm which does not align to the 600mm module.

S_max = SHR_max × Hm = 1.5 × 2.25 = 3.375m
Spacing x = 2.5m ≤ 3.375m ✓
Spacing y = 1.6m ≤ 3.375m ✓
Proceed with N = 20.

## Step 8 — Positions (snapped to 600mm grid)
Row spacing y: 800, 2400, 4000, 5600, 7200 mm
Col spacing x: 1250, 3750, 6250, 8750 mm → snap to 1200, 3600, 6000, 8400 mm

## Step 9 — Achieved illuminance
E = (20 × 4500 × 0.67 × 0.80) / 80 = 48,240 / 80 = 603 lux ✓ (≥ 500)

## Step 10 — Circuits
20 × 36W = 720W total. 720W < 1840W → 1 circuit.
Circuit L1-Z2: all 20 luminaires, 720W on DB L1.
Switch position: latch side of main door, 1200mm AFF.

## §D5 RETROFIT (2026-06-03)

This example was authored at v1.6.0 with a single `target_illuminance_lux` per room.
v1.7.0 splits target into per-zone `em_target_lux` per BS EN 12464-1:2021 §4.2.2 +
Table 6. This retrofit applies the backwards-compatibility defaults:

- Zone Z2 (the single "Interior" zone) takes `purpose: "task"` (ZP-01 default — the
  only valid mapping for an open_plan_office room targeting 500 lx) and
  `em_target_lux: 500` (BS EN 12464-1:2021 Table 5 open_plan_office entry).
- All 20 luminaires take `mount_type: "recessed"` (MT-01 default — matches the
  600×600 ceiling-grid LED panel description); `z_mm` and `suspension_length_mm`
  remain omitted per the recessed convention (geometry inherits
  `room.ceiling_height_mm = 3000`).
- `per_zone_achieved[]` is populated with one entry for Z2: target 500 lx,
  achieved 603 lx, `ratio_compliance: "pass"` (room-level achievement maps
  directly to the single task zone — INV-19 PASS).
- INV-13..INV-19 are appended to `invariants[]`. INV-13 and INV-19 are
  non-vacuous PASS (single task zone with achieved ≥ target). INV-14, INV-15,
  INV-16 are vacuous PASS (no surrounding, no background, no
  pendant/suspended). INV-17 and INV-18 are non-vacuous PASS using the
  recessed inherit-ceiling geometry (hm_mm derives cleanly from
  3000 − 750 = 2250 mm).

**Honest disclosures (4-place):**

1. Engineering judgement defaults documented in `input._d5_retrofit_note`.
2. `output.calculation_summary.assumptions[]` carries the v1.6.0 → v1.7.0
   retrofit explanation.
3. `output.rationale.sections[]` includes a "v1.7 retrofit" section explaining
   ZP-01 and MT-01 default choices for this example.
4. This `reasoning.md` §D5 section.

No engineering numbers were changed — the v1.6.0 lumen-method walk, grid
selection, circuit, and switch all remain identical. The retrofit is purely
additive metadata to align the example with the v1.7.0 zone-purpose / mount-type
schema.
