# uk-drawing-office-strict-ugr — reasoning

Synthetic skill self-test example demonstrating the UGR failure mode that fires when
`room_type=drawing_office` tightens the UGR limit to 16 per BS EN 12464-1:2021 Table 5.3
row 5.34. The layout-level illuminance + uniformity targets PASS comfortably; the
failure is in luminaire selection (general-office UGR-class panels in a drawing-office
context). photometric-analysis catches the per-room-type UGR mismatch structurally.

## §1 Why this example exists

BS EN 12464-1:2021 Table 5.3 defines per-room-type UGR limits:

- General offices: UGR ≤ 19 (typical opal-diffuser panels suffice)
- Drawing offices / technical drawing / fine assembly / precision work: UGR ≤ 16
  (requires UGR-class-rated luminaires with batwing or asymmetric distribution)

The 4 drawing-office-grade room_types were added to the IR schema's enum specifically to
trigger the stricter UGR limit in INV-03. This example demonstrates that mechanism: a
12×9 m drawing office with general-office UGR-class panels passes the lumen-method
illuminance + uniformity targets, but fails the per-room-type UGR check.

The engineering signal is "substitute luminaire selection" — not "redistribute layout"
(as in Example 2). This distinction matters: the photometric-analysis skill distinguishes
between layout-geometry failures (Example 2) and luminaire-spec failures (this example)
through which INVs fail.

## §2 Cascade context

Upstream: `electrical/photometric-analysis/examples/uk-drawing-office-strict-ugr/synthetic-upstream-intent.json` (sibling file) — a synthetic lighting-layout
intent that places 24 LED_PANEL_600 panels in a uniform 4×6 grid in a 12×9 m drawing
office. The 4×6 grid is the engineering correct layout for the room geometry; the
defect is in the panel UGR-class.

Downstream consumer: lighting-layout INV-11 on the upstream synthetic intent. The intent
payload cascades `task_area_compliant: false` + 1 critical non_compliance_flag with the
substitute-luminaire-class recommendation.

## §3 Grid resolution derivation

Task area: room 12×9 m minus 500 mm perimeter border per BS EN 12464-1 §4.3 → 11×8 m
task area (x_min=500, x_max=11500, y_min=500, y_max=8500).

BS EN 12464-1:2021 §6.2 adaptive formula (corrected B.1 fix-pass):

- `d_m = max(11, 8) = 11.0` (longest task-area dimension)
- `p = 0.2 × 5^log₁₀(11.0)`
- `log₁₀(11.0) ≈ 1.041`
- `5^1.041 ≈ 5.31`
- `p ≈ 0.2 × 5.31 m ≈ 1.062 m = 1062 mm`
- Clamped to [50, 1000] mm per [grid-spacing-rules#adaptive-formula] — `p > 1000`, so
  clamps to MAX 1000 mm
- Grid fitted to bounds: 12 cols × 9 rows = 108 grid points (x-step 1000, y-step 1000;
  fits 11000×8000 task-area extent exactly)

Note: this is the upper-clamp case — actual computed p exceeds 1000 mm. The runtime
treats this correctly per the clamp-and-cap convention. A real engineer reviewing this
might note "the room is just at the boundary where the §6.2 adaptive grid would coarsen
beyond 1m, but is capped" — that's the intended behaviour to keep per-point sensitivity
adequate even in large rooms.

## §4 Per-point illuminance results

Runtime `calc.lumen_grid_solver` (same Lambertian distribution as Example 1, on the
24-panel uniform 4×6 grid):

- **achieved_avg: 762 lux** (1.6% margin over the 750 lux drawing-office target per
  BS EN 12464-1 Table 5.3 row 5.34). The 4×6 grid + 24×6000 lm = 144000 design lumens
  spread over 108 m² with 0.7/0.5/0.2 reflectances produces ~762 lux average.
- **achieved_min: 598 lux** at SE corner (11500, 8500). 598/762 = 0.785 U₀. Above
  0.7×750 = 525 lux INV-01 threshold. PASS.
- **achieved_max: 902 lux** at central position (3500, 4500) — under the densest
  cluster of panel contributions.
- **achieved_uniformity_u0: 0.78** ≥ 0.7 drawing-office target. PASS.

INV-01 + INV-02 PASS; the layout is correctly engineered for illuminance + uniformity.

## §5 UGR per CIE 117 + per-room-type mismatch

4 default observers per [ugr-rules#default-observer-positions]:

- N-wall observer at (6000, 7500, 1200), azimuth 180°: UGR 17.1
- S-wall observer at (6000, 1500, 1200), azimuth 0°: UGR 17.5 (worst)
- E-wall observer at (10500, 4500, 1200), azimuth 270°: UGR 16.8
- W-wall observer at (1500, 4500, 1200), azimuth 90°: UGR 16.9

Max UGR 17.5 > 16 drawing-office limit per BS EN 12464-1 Table 5.3 row 5.34.
**INV-03 FAIL HIGH by 1.5 UGR units.**

### Why the Lambertian opal panel fails the drawing-office UGR limit

The synthetic LED_PANEL_600 IES uses a Lambertian cos(θ) intensity distribution per
CIBSE LG7 §6.2 typical opal panel. At a 50–60° elevation angle from the seated observer
(the glare-relevant CIE 117 band), the panel emits ~50% of its peak intensity. That's
adequate for the office UGR ≤19 limit because the L/A² ratio in the Guth formula stays
below the 19-equivalent threshold for typical office geometries.

In a drawing office, the same geometry but stricter limit (UGR ≤16) demands either:
(a) a luminaire with lower emission in the 50–60° band — typically a micro-prism panel
    or louvred specular reflector that drops emission ~70% at 50–60° vs Lambertian; or
(b) batwing distribution that re-aims peak intensity to lower elevation (under 40°),
    eliminating the high-elevation glare contribution entirely.

Both luminaire classes are commercially available (typically labelled "UGR≤16 office",
"low-glare", "VDU-rated", or "drawing-office grade"). The engineering substitution is
specification-level, not redesign-level.

## §6 Engineering signal

Engineer-of-record sees:

1. `task_area_compliant: false` propagated via intent to lighting-layout INV-11
2. 1 critical-severity non_compliance_flag with the substitute-luminaire-class
   recommendation
3. lighting-layout INV-11 FAIL HIGH in the upstream IR + chat thread
4. Reviewer D-3 flag (UGR-class mismatch with per-room-type requirement)

Required action: substitute the LED_PANEL_600 specification (UGR ≤19 opal) with a
UGR ≤16 panel (micro-prism or louvred specular reflector type). After substitution,
the cascade re-runs and max UGR drops into the 14–15 range. INV-03 PASSes; the
lighting-layout proceeds to full_drawing sign-off.

Note that the LAYOUT GEOMETRY (4×6 grid at uniform spacing) is correct — the engineer
should not redistribute. Only the luminaire spec needs to change. This distinction is
visible in the non_compliance_flag message + the reviewer D-3 flag.

## §7 Honest disclosures

- **Synthetic upstream intent**: this example consumes a sibling-file synthetic intent
  (`electrical/photometric-analysis/examples/uk-drawing-office-strict-ugr/synthetic-upstream-intent.json`), not a real lighting-layout example. The shape
  mirrors the real lighting-layout intent contract; the mismatched luminaire UGR-class
  is the contrived defect under test.
- **Synthetic IES** (`shared/photometric/ies/LED_PANEL_600.ies`): general-office
  UGR-class opal panel, `verification_status: synthetic_reference_C3`. Engineer-of-record
  must substitute project IES — and in this case must specifically substitute a
  UGR ≤16 rated product — before final design freeze per
  [ies-provenance-rules#substitution-policy].
- **UGR computation**: the 17.5 figure is computed per CIE 117 Guth-formula sum over
  all 24 luminaires for the S-wall observer geometry. Runtime calc.lumen_grid_solver
  uses the exact Guth formula on the LM-63 intensity distribution; the result is
  reproducible from the IES file + observer position.
- **The 1.5 UGR delta is qualitatively, not just numerically, significant**: a 1.5 UGR
  unit jump corresponds to a roughly 15% increase in glare sensation per CIE 117, well
  within the perceptible band for drawing-office work involving close attention to
  detail. The standards limit is not arbitrary.

## §8 Cascade signal to lighting-layout INV-11

Intent payload (`intent-out.json`) sets `task_area_compliant: false` + populates
`non_compliance_flags[]` with 1 critical entry (UGR mismatch + substitute-class
recommendation). When lighting-layout INV-11 reads this:

1. `consumed_intents.photometric_grid` present ✓ (cascade resolved)
2. `payload.task_area_compliant == false` → INV-11 FAIL HIGH
3. `payload.non_compliance_flags[]` cascaded into INV-11 evidence string

→ lighting-layout INV-11 FAIL HIGH with the UGR-class mismatch flag in evidence. The
engineer sees both the cascade-level failure and the specific luminaire-substitution
recommendation in a single read.

## §8.5 INV walkthrough

- **INV-01 (HIGH) PASS**: min 598 ≥ 525 (0.7×750). Layout illuminance is correct.
- **INV-02 (HIGH) PASS**: U₀ 0.78 ≥ 0.7 drawing-office target. Uniform 4×6 grid works.
- **INV-03 (HIGH) FAIL**: max UGR 17.5 > 16 drawing-office limit. UGR-class mismatch.
- **INV-04..09 PASS**: structural checks (IES match, grid, observers, provenance,
  cascade-complete) all hold; the failure is purely the per-room-type UGR-class
  selection.
