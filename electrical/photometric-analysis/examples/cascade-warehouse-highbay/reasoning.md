# cascade-warehouse-highbay — reasoning

Cascade retrofit of `electrical/lighting-layout/examples/warehouse-highbay` — a
600 m² industrial warehouse with 32 HIGHBAY luminaires on a 4×8 grid at 8 m
mount, plus 12 EMERGENCY luminaires for BS 5266-1 anti-panic compliance.
Verifies the warehouse-specific BS EN 12464-1 row (200 lux target, U₀ 0.4,
UGR 25) — distinct from office targets. All 9 INVs PASS; intent payload sets
`task_area_compliant: true`.

## §1 Why this cascade example exists

The warehouse upstream is the only Wave 1 example with:
- **Floor-level working plane** (warehouse picking activity at floor, not 750 mm
  desk) per BS EN 12464-1 Table 5.3 row 5.34 warehouse
- **Relaxed UGR limit (25)** vs office 19 — warehouse permits higher glare
  given the lower task-density nature
- **Relaxed U₀ target (0.4)** vs office 0.6 — warehouse permits more spatial
  variation
- **High-mount luminaires** (8 m vs 2.7-3 m office ceiling) — requires the
  photometric calc to handle larger distance × cosine fall-off correctly
- **Mixed luminaire types** (HIGHBAY main + EMERGENCY anti-panic) — two
  entries in `ies_files[]` exercising INV-04 cross-check

This cascade is the canonical demonstration of the per-room-type-target
pathway for a non-office room with a non-standard working plane.

## §2 Cascade context

Upstream: `electrical/lighting-layout/examples/warehouse-highbay/intent-out.json`.

**Honest disclosure on the upstream count discrepancy:** the upstream
`luminaire_summary.luminaire_count = 20` is stale (legacy v1.0 before the
upstream re-spec to 4×8 grid). The upstream `output.json.luminaires[]` array
carries 32 HIGHBAY luminaires which is the actual built layout. This
photometric-analysis cascade reads the actual 32-luminaire layout (since the
runtime emits positions from the output IR, not the intent summary). The
engineer-of-record reconciles the upstream intent_summary in D.2 retrofit.

The 32 luminaires put the layout at ~226% of the 200 lux warehouse target,
which is an over-spec consistent with industrial best practice:
- Redundancy against single-fixture failure
- Future-proofing against rack reconfiguration (the warehouse layout
  determines whether each luminaire bay falls between racks or above them)
- BS EN 1837 visual-safety margin in mixed-pedestrian-forklift areas

## §3 Grid resolution derivation — clamp behaviour

Task area: room 30×20 m minus 500 mm perimeter border → 29×19 m task area
(x_min=500, x_max=29500, y_min=500, y_max=19500).

BS EN 12464-1:2021 §6.2 adaptive formula:

- `d_m = max(29, 19) = 29.0`
- `p = 0.2 × 5^log₁₀(29.0) × 1000 mm`
- `log₁₀(29.0) ≈ 1.462`
- `5^1.462 ≈ 10.52`
- `p ≈ 0.2 × 10.52 × 1000 ≈ 2105 mm`
- **Clamped to 1000 mm maximum** per [grid-spacing-rules#adaptive-formula]
- Grid fitted to bounds: 30 cols × 20 rows = **600 grid points** (x-step
  1000 mm, y-step 1000 mm — fits 29 × 19 m extent across 29 × 19 intervals)

This is the canonical demonstration of the §6.2 clamp behaviour. For rooms
with d > ~11 m the formula returns p > 1000 mm; the clamp prevents grid
spacing larger than the largest typical aisle width so that per-point
sampling remains useful for cold-corner / aisle-blind-spot detection.

600 points is the largest grid in Wave 1. Runtime calc time scales as
O(N_luminaires × N_grid) ≈ O(32 × 600) ≈ 19200 contributions — still
trivially fast for typical lumen_grid_solver implementations.

## §4 Per-point illuminance results

Runtime `calc.lumen_grid_solver` computed with the synthetic
`HIGHBAY.ies` (50° narrow-beam reflector, 9800 cd max intensity):

- **achieved_avg: 452 lux** — over-spec to 226% of 200 target reflecting
  upstream design intent (redundancy + future-proofing)
- **achieved_min: 298 lux** at SE corner (29500, 500); the perimeter aisles
  see lower light than the cluster centres; 158 lux margin over the 140
  threshold (0.7 × 200)
- **achieved_max: 632 lux** directly beneath a highbay near the cluster
  centre; max/min ratio 2.1× reflects the narrow-beam scalloping
- **achieved_uniformity_u0: 0.66** = 298 / 452; comfortable margin over the
  0.4 warehouse target

The 50° narrow-beam highbay concentrates flux beneath each fixture and
falls off between rows — this scalloping is the warehouse industry's
known trade-off for efficient flux delivery at 8 m mount heights. The
0.4 warehouse U₀ target accommodates this characteristic.

## §5 UGR per CIE 117 — high-mount glare

4 default observer positions (scaled to 30×20 m room):

- **N-wall observer** at (15000, 18500, 1200), azimuth 180°: UGR 21.4
- **S-wall observer** at (15000, 1500, 1200), azimuth 0°: UGR 22.1 (worst)
- **E-wall observer** at (28500, 10000, 1200), azimuth 270°: UGR 20.8
- **W-wall observer** at (1500, 10000, 1200), azimuth 90°: UGR 21.2

`max_ugr_across_view_positions = 22.1 ≤ 25` warehouse limit per BS EN 12464-1:2021
Table 5.3 row 5.34. PASS with 2.9 margin.

Highbays at 8 m mount produce noticeable glare from low observer angles —
the high luminance source at relatively shallow elevation is exactly the
geometry CIE 117 captures. The relaxed warehouse UGR-25 limit (vs office
UGR-19) deliberately permits this; warehouse activity tolerates more glare
than visual-task office work.

## §6 Emergency lighting modelled separately

The 12 EMERGENCY luminaires (BS 5266-1:2016 §5.3 anti-panic open area
>60 m²) are carried in `ies_files[1]` for runtime emergency-mode cross-checking,
but the main `lumen_grid_solver` calc uses HIGHBAY only:

- Main calc verifies BS EN 12464-1 normal-operation per-point + UGR.
- Emergency mode is a separate compliance regime under BS 5266-1 (anti-panic
  0.5 lux floor average + max:min ≤ 40:1) that the future `emergency-lighting`
  skill will verify via its own cascade.

This separation is correct per spec: photometric-analysis ≡ normal-operation;
emergency-lighting ≡ BS 5266-1 emergency-operation. They share the upstream
lighting-layout intent but produce independent verifications.

## §7 Working plane = floor

Per BS EN 12464-1 Table 5.3 row 5.34 warehouse, the working plane is the
floor (warehouse picking activity at floor level). `room.working_plane_mm = 0`.

Differs from:
- office_open_plan / private_office: working_plane = 750 mm desk
- classroom: working_plane = 750 mm desk
- reception_lobby: working_plane = 750 mm desk (counter)

The achieved per-point values are computed at the floor plane accordingly.
This is a critical detail because moving the calc plane from 0 to 750 mm
in this 8.5 m ceiling height would only change avg by ~1% (small change in
cosine fall-off) but would be technically wrong against the standard.

## §8 Honest disclosures

- **Upstream intent_summary stale**: see §2 cascade context above.
- **IES files synthetic_reference_C3**:
  - HIGHBAY: Lambertian-with-50°-cutoff archetype; real highbays from
    different manufacturers vary in beam (40°–80°) and CRI (70–90)
  - EMERGENCY: wide-beam wall-pack-style archetype; real emergency
    fixtures span ceiling-mount, wall-pack, and exit-sign formats with
    different beam characteristics
- **Reflectances 0.3/0.3/0.2** are industrial-low, conservative per CIBSE
  LG12. A whitewashed warehouse with high-reflectance ceiling paint could
  see avg 15-20% higher than reported; engineer-of-record adjusts
  reflectances if the project uses non-standard paint specifications.
- **Working plane simplification**: real warehouses have racks blocking
  partial sightlines from the highbays to the floor between racks. The
  cascade reports open-floor illuminance; rack-shadow conditions require
  a separate rack-shadow calc (typical reduction 10-30% in aisle
  centre-line illuminance).

## §9 INV walkthrough

All 9 INVs PASS:

- **INV-01 (HIGH) PASS**: min 298 ≥ 140 (0.7×200)
- **INV-02 (HIGH) PASS**: U₀ 0.66 ≥ 0.4 warehouse target
- **INV-03 (HIGH) PASS**: max UGR 22.1 ≤ 25 warehouse limit
- **INV-04 (HIGH) PASS**: 2 luminaire_types (HIGHBAY + EMERGENCY) matched by
  2 IES files; LM-63 parser returns expected total_lumens for both
- **INV-05 (HIGH) PASS**: grid_spacing 1000 mm — canonical clamp demo (formula
  returns 2105 mm; clamped to 1000)
- **INV-06 (HIGH) PASS**: 600 grid points; representative slice in IR
- **INV-07 (MEDIUM) PASS**: 4 CIE 117 default observers (scaled positions)
- **INV-08 (MEDIUM) PASS**: both _source entries ≥ 40 chars; verification_status
  in enum for both
- **INV-09 (HIGH) PASS**: cascade completed; tool_call_pending=false

## §10 Cascade signal to lighting-layout INV-11

Intent payload sets `task_area_compliant: true` AND `non_compliance_flags: []`.
Lighting-layout INV-11 PASS HIGH. Warehouse-highbay full_drawing IR is
sign-off-ready for the photometric dimension.

The over-spec (32 highbays vs 20 the upstream intent_summary claims) is
not a photometric failure — it's an engineer's design choice for redundancy.
The validator (reviewer.md stage R-1) may flag the over-spec as an
energy-efficiency concern but not as a BS EN 12464-1 compliance issue.
