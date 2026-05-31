# cascade-uk-open-plan-office-10x8-dali — reasoning

Cascade retrofit of `electrical/lighting-layout/examples/uk-open-plan-office-10x8-dali`
— the Sprint D3 canonical lighting-layout example. This is the post-D.2
retrofit complement to the C.1 standalone example
`uk-open-plan-office-10x8-dali-photometric`. The math is identical; the
difference is the cascade contract: this example points at the REAL
lighting-layout intent-out.json, demonstrating the production cascade flow.

All 9 INVs PASS; intent payload sets `task_area_compliant: true` for
upstream lighting-layout INV-11.

## §1 Why this cascade example matters

The D3 canonical lighting-layout shipped v1.4.0 with INV-11 declared as a
placeholder (it asserted "photometric verification cascade resolved" but
the cascade contract was not yet wired — no photometric-analysis skill
existed in the repo). This cascade demonstrates the resolved state:

- **C.1 standalone** (`uk-open-plan-office-10x8-dali-photometric`) shipped the
  happy-path verification using a same-named-but-synthetic upstream intent
  (because the real D3 canonical's intent shape didn't carry photometric_grid
  yet — the cascade contract wasn't bilateral)
- **C.2 cascade** (this example) shipped after the C.1 standalone — points at
  the REAL D3 canonical's intent-out.json directly, demonstrating the
  production cascade chain end-to-end

The two examples are complementary: the standalone is the lab-bench
verification (controlled synthetic upstream); the cascade is the production
verification (real upstream lighting-layout intent).

The D.2 retrofit (next sprint phase after C.2) will rewrite the D3
canonical's lighting-layout output to consume THIS cascade's intent-out.json
in its INV-11 evidence — closing the bilateral cascade contract.

## §2 Cascade context

Upstream: `electrical/lighting-layout/examples/uk-open-plan-office-10x8-dali/intent-out.json`
— the D3 canonical Sprint D3 final form (post-D3 INV-4 Z-pattern fix
with 5 row-circuits per panel row).

Design specs:
- 20 × LED_PANEL_600 panels at 6000 lm each on 4×5 grid
- DALI master control protocol
- 5 row-circuits C-L01..C-L05 (one per panel row) — the D3 INV-4 Z-pattern fix
- Part L compliant: DALI provides automatic occupancy + daylight-link on
  perimeter zone
- Lumen-method (upstream) achieved 804 lux (UF=0.67, MF=0.80)

## §3 Grid resolution derivation

Identical to cascade-office-open-plan and cascade-uk-multi-entrance-classroom
(all are 10×8 m rooms):

- Task area: 9×7 m after 500 mm border per BS EN 12464-1 §4.3
- d = 9.0 m
- p = 0.2 × 5^log₁₀(9.0) × 1000 ≈ 929 mm → snapped to 900 mm
- 11 cols × 9 rows = 99 grid points (x-step 900, y-step 875)

## §4 Per-point illuminance — 50% margin design

Runtime `calc.lumen_grid_solver` with synthetic `LED_PANEL_600.ies`:

- **achieved_avg: 752 lux** — 150% of 500 target (50% margin)
- **achieved_min: 612 lux** at NW corner (500, 7500); 262 lux margin over
  the 350 (0.7 × 500) threshold
- **achieved_max: 891 lux** at a central position under the 4-panel cluster
- **achieved_uniformity_u0: 0.81** = 612 / 752; comfortably above 0.6 target

The 6000 lm panel (the D3 canonical's design point — vs the 4500 lm panel
in cascade-office-open-plan) delivers the 50% margin. This is a comfortable
design point that absorbs:

- Maintenance factor variation (project MF may be 0.7 vs 0.8 assumption)
- Reflectance variation (project decor may be slightly darker)
- IES variation (project luminaire may have 10-15% lower throw than
  synthetic Lambertian)
- DALI dimming headroom (most projects run DALI at ~80% to maintain
  visual comfort during normal operation while keeping full output
  available for high-task moments)

## §5 UGR per CIE 117

Same 4 default observer positions as cascade-office-open-plan (same room
dims):

- **N-wall** at (5000, 6500, 1200): UGR 17.8
- **S-wall** at (5000, 1500, 1200): UGR 18.2 (worst)
- **E-wall** at (8500, 4000, 1200): UGR 17.1
- **W-wall** at (1500, 4000, 1200): UGR 17.4

`max_ugr_across_view_positions = 18.2 ≤ 19` office limit. PASS with 0.8 margin.

The 6000 lm panel produces slightly higher UGR than the 4500 lm panel
(cascade-office-open-plan = 17.9) because per-luminaire luminance is
~33% higher (same physical aperture, more lumens). Still well within
the 19 office limit.

## §6 DALI controls overlay (informational)

Upstream specifies DALI master control with daylight-linking + occupancy-sensing
on perimeter zone (Part L 2021 §6 compliant per upstream INV-06 PASS).

Photometric-analysis treats DALI as a controls overlay:
- Verification basis: full output (the worst-case static snapshot)
- Dimming during normal operation reduces actual delivered lux but does
  NOT change the design-condition compliance basis

This matches the convention from cascade-reception-lobby (0-10V dimming
overlay) and cascade-uk-multi-entrance-classroom (multi-switch controls
overlay). The BS EN 12464-1 compliance basis is design lighting condition;
controls are amenity + energy features.

## §7 Cascade signal to lighting-layout INV-11

Intent payload sets:
- `task_area_compliant: true`
- `non_compliance_flags: []`
- `verification_status_lowest: synthetic_reference_C3`

When lighting-layout INV-11 reads this (per post-D.2 retrofit):

1. `consumed_intents.photometric_grid` present ✓
2. `payload.task_area_compliant == true` ✓
3. `payload.achieved_avg_illuminance_lux` (752) ≥ `target_illuminance_lux` (500) ✓
4. No flags to cascade ✓

→ **lighting-layout INV-11 PASS HIGH**. The D3 canonical full_drawing IR
is sign-off-ready for the photometric dimension; engineer proceeds to
controls + circuits + drafting sign-off layers without a photometric blocker.

## §8 INV walkthrough

All 9 INVs PASS:

- **INV-01 (HIGH) PASS**: min 612 ≥ 350 (0.7×500)
- **INV-02 (HIGH) PASS**: U₀ 0.81 ≥ 0.6 office target
- **INV-03 (HIGH) PASS**: max UGR 18.2 ≤ 19 office limit
- **INV-04 (HIGH) PASS**: 1 luminaire_type matched by 1 IES file
- **INV-05 (HIGH) PASS**: grid_spacing 900 mm matches §6.2 corrected formula
- **INV-06 (HIGH) PASS**: 99 grid points; representative slice in IR
- **INV-07 (MEDIUM) PASS**: 4 CIE 117 default observers
- **INV-08 (MEDIUM) PASS**: _source 270 chars + verification_status enum match
- **INV-09 (HIGH) PASS**: cascade completed; tool_call_pending=false

## §9 Standalone vs cascade — IR comparison

| Field | C.1 standalone | C.2 cascade (this) |
|---|---|---|
| example_id | uk-open-plan-office-10x8-dali-photometric | cascade-uk-open-plan-office-10x8-dali |
| consumed_intents.lighting_layout.source_path | electrical/lighting-layout/examples/uk-open-plan-office-10x8-dali/intent-out.json | electrical/lighting-layout/examples/uk-open-plan-office-10x8-dali/intent-out.json |
| achieved values (avg/min/max/U₀/UGR) | 752/612/891/0.81/18.2 | 752/612/891/0.81/18.2 (IDENTICAL) |
| Pass 1 (output.json validation) | ✓ | ✓ |
| Pass 4 (intent-out.json validation) | ✓ | ✓ |
| Role | demonstrates the verification in isolation | demonstrates the production cascade flow |

**Surprise:** the `source_path` field is identical in both. This is by
design — both examples target the same upstream lighting-layout example.
The C.1 standalone exists to test the photometric-analysis skill BEFORE
the cascade contract is bilaterally wired; the C.2 cascade exists to
demonstrate the post-D.2 bilateral state where lighting-layout INV-11
will actually read THIS cascade's intent-out.json.

The two examples are not duplicate; they're complementary verification
of the same engineering math under different cascade-contract states.

## §10 Honest disclosures

- **IES file** is `synthetic_reference_C3` (LED_PANEL_600.ies, 6000 lm
  Lambertian opal). NOT manufacturer-measured. Engineer-of-record must
  substitute project IES before final design freeze.
- **Identical to C.1 standalone** in engineering output — see that example's
  reasoning.md (§3–§7) for the full per-step derivation. This file
  emphasises the cascade-contract difference; the standalone reasoning
  document holds the deep engineering walkthrough.
- **DALI dimming**: photometric verification is full output. Real DALI
  systems will dim to maintain target lux ± visual comfort during normal
  operation; the engineer-of-record may run a separate "dimmed-condition"
  photometric calc to confirm Part L energy-saving estimates, but that's
  the Part L verification path, not the BS EN 12464-1 verification path.
