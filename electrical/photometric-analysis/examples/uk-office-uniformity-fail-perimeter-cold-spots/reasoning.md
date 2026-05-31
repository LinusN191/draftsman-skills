# uk-office-uniformity-fail-perimeter-cold-spots — reasoning

Synthetic skill self-test example demonstrating the U₀ failure mode — the spatial
uniformity defect that lumen-method INV-1 alone cannot detect, but photometric-analysis
catches structurally via per-point illuminance + the BS EN 12464-1 §4.4 minimum
threshold + uniformity target.

## §1 Why this example exists

The lumen-method calculation in lighting-layout produces a single room-average lux value
and compares it to the BS EN 12464-1 Table 5.3 target. If the average lands within
±10–15% of target, lumen-method INV-1 PASSes. But the lumen-method is spatially blind —
it cannot tell whether the achieved average is the result of:
(a) a uniform grid producing ~500 lux everywhere, or
(b) a clustered grid producing 900 lux at the centre and 150 lux at the corners.

Both produce a similar average lux figure; only (a) is compliant under BS EN 12464-1
§4.4 (per-point min ≥ 0.7 × target) + the uniformity U₀ requirement (≥0.6 for
open_plan_office). This example contrives case (b) to demonstrate the structural check
photometric-analysis provides on top of lumen-method.

## §2 Cascade context

Upstream: `electrical/photometric-analysis/examples/uk-office-uniformity-fail-perimeter-cold-spots/synthetic-upstream-intent.json` (sibling file in this example directory) —
a synthetic lighting-layout intent that places 16 LED_PANEL_600 panels at a 4×4 grid
within a central 4.5×4.5 m region of a 10×8 m office. The perimeter 2 m strip on all
4 sides has zero luminaires.

Downstream consumer: lighting-layout INV-11 on the upstream synthetic intent (notional —
not a real lighting-layout example). The intent payload from this skill cascades
`task_area_compliant: false` + the 2 non-compliance flags upstream; the engineer-of-record
sees both flags in the chat thread + sees lighting-layout INV-11 FAIL HIGH.

The synthetic upstream intent is the established pattern for skill self-test
demonstrations of INV failure paths where no real upstream example exercises that path.
This is documented in the plan (Step 5 fallback for INV-9 + schema requirement on
`consumed_intents.lighting_layout`).

## §3 Grid resolution derivation

Same 9×7 m task area as Example 1 (10×8 m room minus 500 mm perimeter border per
BS EN 12464-1 §4.3). d=9m; corrected §6.2 formula `p = 0.2 × 5^log₁₀(9) × 1000 ≈ 922 mm`
snapped to 900 mm nominal. 11 cols × 9 rows = 99 grid points.

The grid is a function of room geometry, NOT luminaire placement — the failure here is
in the LUMINAIRE layout (clustered), not the evaluation grid. The same grid resolution
correctly detects both the happy-path (Example 1) and the failure path (this example).
That is the structural integrity of the photometric-analysis verification: the grid is
the rule, the layout is the variable under test.

## §4 Per-point illuminance results

Runtime `calc.lumen_grid_solver` (same Lambertian distribution + inverse-square + cosine
+ form-factor as Example 1, on the clustered 16-panel layout):

- **achieved_avg: 478 lux** — already 4% below the 500 target. A real engineer running
  lumen-method-only would see this as a marginal-but-arguably-PASS result (target band
  typically ±10–15%). The full-cascade verification will FAIL it correctly.
- **achieved_min: 150 lux** at SE corner (8600, 7500), and similar 150–168 lux at the
  other 3 corners — 4-fold symmetry from the centred 4×4 cluster. This is the
  cold-corner defect lumen-method misses.
- **achieved_max: 908 lux** at room centre (5000, 4000), directly beneath 4 cluster
  panels with overlap of their inverse-square contributions.
- **achieved_uniformity_u0: 0.31** = 150/478. Far below the 0.6 office target. The
  6× ratio between max (908) and min (150) is the clustered-grid signature.

10-point representative slice carried in output.json `illuminance_grid[]` covering the
4 corners + 4 axis midpoints + room centre + one mid-cluster point. The full 99-point
grid is emitted by the runtime calc.

## §5 UGR per CIE 117

Despite the catastrophic U₀ failure, UGR still PASSes:

- N-wall: 17.2
- S-wall: 17.6 (worst)
- E-wall: 16.8
- W-wall: 16.9

Max UGR 17.6 ≤ 19 office limit. INV-03 PASS.

**Why UGR PASSes when U₀ FAILs**: UGR depends on observer-to-luminaire angles per
CIE 117. The perimeter observers (1500/8500 mm from centre walls) still see roughly the
same set of luminaires from similar angles whether the luminaires are clustered or
uniformly distributed. Clustering moves all luminaires toward the room centre — closer
to the observer-to-window line of sight for the centre walls — but the L/A² geometry
doesn't blow up under that perturbation. Glare is observer-geometry-driven, not
spatial-distribution-driven; that's the structural difference between INV-02 and INV-03.

## §6 Engineering signal

Engineer-of-record sees:

1. `task_area_compliant: false` propagated via intent to lighting-layout INV-11
2. 2 critical-severity non_compliance_flags with diagnostic messages
3. lighting-layout INV-11 FAIL HIGH in the upstream IR + chat thread
4. Reviewer D-1 flag (BS EN 12464-1 §4.4 per-point failure)

Required action (per the flag message): redistribute the 16 panels into a uniform 4×5
or 4×4 grid covering the full task area, OR add 4 perimeter panels to break the
cold-corner deficit. After re-run of the cascade (lighting-layout regenerates → emits
new intent → photometric-analysis re-verifies), the achieved per-point min rises into
the 350+ lux range and U₀ rises above 0.6 office target.

The engineer cannot ship the lighting-layout to the next stage (controls + circuits
sign-off) until this is resolved — the photometric-analysis cascade is part of the
lighting-layout `full_drawing` IR completion path per spec §10.3.

## §7 Honest disclosures

- **Synthetic upstream intent**: this example consumes a sibling-file synthetic intent
  (`electrical/photometric-analysis/examples/uk-office-uniformity-fail-perimeter-cold-spots/synthetic-upstream-intent.json`), not a real lighting-layout example. The shape
  mirrors the real lighting-layout intent contract; the clustered layout is the
  contrived defect under test. This is an acceptable pattern for skill self-test
  examples that exercise INV failure paths.
- **Synthetic IES** (`shared/photometric/ies/LED_PANEL_600.ies`): same
  `verification_status: synthetic_reference_C3` Lambertian archetype used in Example 1.
  Engineer-of-record must substitute project IES before final design freeze per
  [ies-provenance-rules#substitution-policy].
- **The numbers in this IR** are runtime-calc-computable on the geometry described; they
  are not arbitrary worst-case values. Lambertian distribution + 16 clustered panels +
  centre-to-corner geometry produces 150 lux at the corners by direct inverse-square
  calculation (the dominant 4 corner cluster panels are ~5 m from each corner,
  contributing each ~30–40 lux direct + diffuse).

## §8 Cascade signal to lighting-layout INV-11

Intent payload (`intent-out.json`) sets `task_area_compliant: false` + populates
`non_compliance_flags[]` with 2 critical entries. When lighting-layout INV-11 reads this:

1. `consumed_intents.photometric_grid` present ✓ (cascade resolved)
2. `payload.task_area_compliant == false` → INV-11 FAIL HIGH
3. `payload.non_compliance_flags[]` cascaded into INV-11 evidence string for visibility
   in the upstream chat thread

→ lighting-layout INV-11 FAIL HIGH with the photometric flags in evidence. Engineer
sees the failure end-to-end at the lighting-layout level + has the spatial-distribution
diagnostic immediately available.

## §8.5 INV walkthrough

- **INV-01 (HIGH) FAIL**: min 150 < 0.7×500 = 350. Cold corners detected.
- **INV-02 (HIGH) FAIL**: U₀ 0.31 < 0.6. 6× max-to-min ratio.
- **INV-03 (HIGH) PASS**: max UGR 17.6 ≤ 19. UGR is geometry-driven, uniformity-blind.
- **INV-04..09 PASS**: structural checks (IES match, grid, observers, provenance,
  cascade-complete) all hold; the failure is purely engineering (the layout doesn't
  meet BS EN 12464-1 §4.4 requirements).
