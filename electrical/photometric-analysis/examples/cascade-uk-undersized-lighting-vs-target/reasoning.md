# cascade-uk-undersized-lighting-vs-target — reasoning

**Failure-mode cascade demonstration end-to-end.** The upstream
lighting-layout already FAILED its own lumen-method INV-1 (achieved 434 lux <
500 target). This cascade confirms the failure also manifests as a per-point
BS EN 12464-1 §4.4 violation, propagates `task_area_compliant: false` to
lighting-layout INV-11 with a cascaded critical flag, and demonstrates the
failure-mode cascade contract end-to-end. INV-01 FAIL HIGH; INV-02 + INV-03 +
INV-04..09 PASS.

## §1 Why this cascade example matters

This is the canonical failure-mode cascade demo. The cascade contract is:

```
lighting-layout INV-1 (lumen-method room average) FAIL
            +
photometric-analysis INV-01 (per-point) FAIL
            =
lighting-layout INV-11 (cascade) FAIL HIGH with _cascaded_from attribution
```

It demonstrates that the upstream + downstream verification layers are
INDEPENDENT but CONSISTENT — they catch the same root cause (the
value-engineered 3500 lm substitution from 4500 lm ontology default) via
two different mathematical paths:

- **Upstream (lighting-layout)**: lumen-method room average
  `N × Φ × UF × MF / A = 12 × 3500 × 0.62 × 0.80 / 48 = 434 < 500` → INV-1 FAIL
- **Downstream (photometric-analysis)**: per-point integration with cosine
  fall-off at the cold corner; the corner sees the full lumen reduction
  plus wall-shadow effect → min 275 < 350 → INV-01 FAIL

The two failure paths are not redundant — they verify different aspects:
the lumen method verifies the design intent (did the engineer specify
enough lumens?); the photometric verifies the experienced reality (does
the user at the cold corner actually get 350 lux?). Both must hold for
the sign-off to pass.

## §2 Cascade context

Upstream: `electrical/lighting-layout/examples/uk-undersized-lighting-vs-target/intent-out.json`.

The upstream `calculation_summary.non_compliance_flags[]` already carries
the lumen-method failure flag (critical severity, "Remediation: bump to 16
panels in 4×4 grid OR upgrade to 4500 lm"). This cascade adds the per-point
flag to the cascade chain.

## §3 Grid resolution derivation

Task area: room 8×6 m minus 500 mm perimeter border → 7×5 m task area
(x_min=500, x_max=7500, y_min=500, y_max=5500).

BS EN 12464-1:2021 §6.2 adaptive formula (B.1 fix-pass corrected):

- `d_m = max(7, 5) = 7.0`
- `p = 0.2 × 5^log₁₀(7.0) × 1000 mm ≈ 779 mm`
- Snapped to 800 mm
- 10 cols × 7 rows = 70 grid points (x-step ~778 mm, y-step ~833 mm)

## §4 Per-point illuminance — the failure mode

Runtime `calc.lumen_grid_solver` with synthetic `LED_PANEL_600-3500lm.ies`
(Lambertian 3500 lm vs the 4500 lm reference):

- **achieved_avg: 434 lux** — matches upstream lumen-method exactly (434.0).
  This cross-validation is important: it confirms the photometric engine's
  integration over the IES distribution × form-factor inter-reflection
  reproduces the lumen-method result when given the same UF assumption.
- **achieved_min: 275 lux** at NW corner (500, 5500); 75 lux below the
  350 threshold (0.7 × 500). **THE FAILURE**.
- **achieved_max: 552 lux** at room centre under the central panel cluster.
- **achieved_uniformity_u0: 0.63** = 275 / 434; PASSes the 0.6 office target.

**Critical observation:** the failure is in **absolute level** (INV-01),
not in **spatial distribution** (INV-02). The 12-panel layout has acceptable
uniformity; it just doesn't have enough total lumens. This distinguishes
this failure mode from the C.1 standalone uniformity-fail example
(`uk-office-uniformity-fail-perimeter-cold-spots`) where the failure was
in spatial distribution from clustered placement.

## §5 UGR + uniformity PASS — INDEPENDENCE

INV-02 (uniformity 0.63 ≥ 0.6) and INV-03 (UGR 17.4 ≤ 19) BOTH PASS. This
demonstrates a key engineering signal:

**The three INVs verify three orthogonal aspects.** Under-provision is
NOT a uniformity problem (the layout is uniformly under-bright, not
unevenly bright); under-provision is NOT a UGR problem (per-luminaire
luminance is unchanged). Only INV-01 catches it.

Engineering takeaway: a designer reading the cascade chat sees:
- "INV-01 FAIL: cold corner under-illuminated" (the per-point failure)
- "INV-02 PASS: layout is uniform" (the layout SHAPE is fine)
- "INV-03 PASS: no glare issue" (the GLARE component is fine)

→ Diagnosis: the problem is in LUMEN COUNT (or per-fitting lumens), not in
PLACEMENT or in GLARE. Remediation: bump count OR upgrade to higher-lumen
fittings. Both match the upstream lumen-method advice.

## §6 Cascade signal — propagation

Intent payload sets:
- `task_area_compliant: false`
- `non_compliance_flags`: 1 critical entry (INV-01 cold-corner failure
  with remediation guidance mirrored from upstream)
- `verification_status_lowest: synthetic_reference_C3`

When lighting-layout INV-11 reads this (per post-D.2 retrofit of the
lighting-layout INV-11 validator logic):

1. `consumed_intents.photometric_grid` present ✓
2. `payload.task_area_compliant == false` → **INV-11 FAIL HIGH**
3. The critical flag is mirrored into lighting-layout's own
   `non_compliance_flags[]` with `_cascaded_from: "photometric-analysis"`
   attribution (per spec §10.3 sub-check 4)
4. Engineer-of-record sees both flags in the final IR: the upstream
   INV-1 (lumen-method) flag AND the cascaded INV-11 (per-point) flag
   — two-layer diagnosis confirming the same root cause

This is the canonical failure-mode cascade contract.

## §7 Honest disclosures

- **IES file** `LED_PANEL_600-3500lm.ies` is `synthetic_reference_C3` — the
  same Lambertian distribution as the 4500 lm reference but scaled to
  3500 lm output. Real value-engineered panels may have different distributions
  (sometimes tighter beam at lower lumen output, which would worsen the
  cold-corner deficit further). Engineer-of-record substitutes project IES
  before final design freeze.
- **Reflectances 0.7/0.5/0.2** assumed clean office (matching upstream
  assumptions[0]). If the project uses darker decor (lower reflectances)
  the achieved values would drop further.
- **Cross-validation with upstream**: achieved_avg 434 matches upstream
  lumen-method 434.0 exactly. This is the expected behaviour when the
  UF assumption (0.62) used by upstream and the form-factor integration
  used by photometric-analysis are consistent. The added value of the
  photometric verification is the per-point + per-observer detail, NOT
  the room average.

## §8 INV walkthrough

- **INV-01 (HIGH) FAIL**: min 275 < 350 — THE FAILURE
- **INV-02 (HIGH) PASS**: U₀ 0.63 ≥ 0.6 (uniformity is fine)
- **INV-03 (HIGH) PASS**: max UGR 17.4 ≤ 19 (glare is fine)
- **INV-04 (HIGH) PASS**: 1 luminaire_type matched by 1 IES file (3500 lm variant)
- **INV-05 (HIGH) PASS**: grid_spacing 800 mm matches §6.2 corrected formula
- **INV-06 (HIGH) PASS**: 70 grid points; representative slice in IR
- **INV-07 (MEDIUM) PASS**: 4 CIE 117 default observers
- **INV-08 (MEDIUM) PASS**: _source 298 chars + verification_status enum match
- **INV-09 (HIGH) PASS**: cascade completed; tool_call_pending=false (the
  calc ran; the result is non-compliant by design)

## §9 Remediation re-run preview

Per upstream remediation guidance:

**Option A** — bump to 16 panels in 4×4 grid:
- avg = 16 × 3500 × 0.62 × 0.8 / 48 = 579 lux ≥ 500 ✓
- min ≈ 579 × 0.75 ≈ 434 lux ≥ 350 ✓ (uniformity ratio improves with 4×4 grid)
- INV-01..03 all PASS on re-run

**Option B** — upgrade to 4500 lm panels, keep 12-fitting 3×4 layout:
- avg = 12 × 4500 × 0.62 × 0.8 / 48 = 558 lux ≥ 500 ✓
- min ≈ 558 × 0.74 ≈ 413 lux ≥ 350 ✓
- INV-01..03 all PASS on re-run

Either option clears the failure cascade. The lighting-layout retrofit
(D.2) does NOT change this cascade example's intent payload — it stays
as the demonstrated failure case. The lighting-layout's own example is
the one that gets remediated upstream; this cascade exists as the
historical-state demonstration of how the failure cascade WORKED.
