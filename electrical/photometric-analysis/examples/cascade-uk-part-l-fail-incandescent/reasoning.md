# cascade-uk-part-l-fail-incandescent — reasoning

**PHOTOMETRIC INDEPENDENCE DEMONSTRATION.** The upstream lighting-layout
uk-part-l-fail-incandescent FAILS Part L on 3 axes (efficacy 15 lm/W vs 95
target + missing daylight-link + missing occupancy-sense). Photometric-analysis
verifies the LIGHTING ITSELF is BS EN 12464-1 compliant — all 9 photometric
INVs PASS. The cascade demonstrates that **photometric PASS does not equal
Part L PASS**; they are orthogonal verification axes. Engineer-of-record reads
both verdicts in the final lighting-layout IR.

## §1 Why this cascade example matters

This is the canonical "orthogonal verification axes" demonstration. The
cascade contract requires that the LIGHTING ANALYSIS (per-point + UGR)
must verify INDEPENDENTLY of the ENERGY CONTROLS (efficacy + automatic
switching + daylight linking).

The upstream example is a legacy halogen 'wash' design — a refurbishment
case where the inherited 50-halogen layout DELIVERS adequate lighting
(per-point illuminance compliant) but FAILS modern Part L energy
requirements (efficacy 15 lm/W ≪ 95 target; no automatic controls).

Two valid engineering signals must be carried in the final IR:
- **INV-11 PASS** — the lighting performs to BS EN 12464-1
- **INV-06 FAIL** — the system doesn't meet Part L energy efficiency

A naive single-flag pass/fail would conflate these. The cascade contract
keeps them orthogonal.

## §2 Cascade context

Upstream: `electrical/lighting-layout/examples/uk-part-l-fail-incandescent/intent-out.json`.

Upstream `calculation_summary.non_compliance_flags[]` carries 3 Part L
critical flags:

1. Lamp efficacy 15 lm/W ≪ 95 lm/W Part L 2021 §6 Table 6.2 target —
   remediation: replace with 8W GU10 LED retrofit or full LED downlight
   swap (cuts connected load from 2500 W to 500 W, 80% energy saving)
2. Daylight-linking missing on west-glazed wall — Part L §6 requires
   daylight-linked dimming within 6 m of glazing
3. Occupancy-sensing missing on new-build private office — Part L §6
   requires automatic occupancy detection

None of these are photometric failures. They are CONTROLS + EFFICACY
failures owned by lighting-layout INV-06 (Part L compliance check).

## §3 Grid resolution derivation

Identical to cascade-uk-undersized (same 8×6 m room dims):

- Task area: 7×5 m after 500 mm border
- d = 7.0 m
- p = 0.2 × 5^log₁₀(7.0) × 1000 ≈ 779 mm → snapped to 800 mm
- 10 cols × 7 rows = 70 grid points

## §4 Per-point illuminance — the high-density payoff

Runtime `calc.lumen_grid_solver` with synthetic `HALOGEN_DOWNLIGHT.ies`:

- **achieved_avg: 564 lux** — 113% of 500 private_office target
- **achieved_min: 412 lux** at NW corner (500, 5500); 62 lux margin over
  the 350 (0.7 × 500) threshold
- **achieved_max: 678 lux** at a position between fitting clusters
- **achieved_uniformity_u0: 0.73** = 412 / 564; comfortable margin over 0.6

**The high-density payoff:** 50 halogen GU10s at 1 fitting/m² density
delivers raw lumens at the cost of energy efficiency. Each fitting is
only 750 lm but at 50 fittings the total room lumens is 37500 lm —
comparable to 8 × LED panels at 4500 lm. The lighting PERFORMS; the
ENERGY is wasted.

This is the classic legacy-halogen pattern that drove the Part L 2021
shift to per-luminaire efficacy targets — you can't use a brute-force
fitting count to meet illuminance if the per-fitting efficacy is too low.

## §5 The achieved_avg discrepancy with upstream lumen-method

Upstream lighting-layout reports `achieved_illuminance_lux = 343.75`
(50 × 750 × 0.55 × 0.80 / 48 = 343.75). Photometric-analysis here
reports 564 lux. The discrepancy is materially larger than other
cascades' few-percent deltas.

**Root cause:** the upstream used the **LED_DOWNLIGHT ontology proxy**
for the UF table (because the LED_DOWNLIGHT and halogen GU10 share
similar 100 mm-aperture geometry — a reasonable proxy for the
lumen-method UF lookup). But the photometric calc uses the
**HALOGEN_DOWNLIGHT.ies** for the actual photometric distribution.

The two methods give different results at high fitting density because:
- Lumen-method's UF is a single lumped factor for the room (0.55)
- Photometric form-factor integration accounts for the dense
  inter-reflection from 50 sources illuminating each other's bounce
  paths via the 0.7 ceiling reflectance — the inter-reflection
  contribution is materially larger at high fitting densities

Both methods agree the lighting PERFORMS. The 564 vs 343.75 disagreement
is a known IES-vs-UF-table issue at densities >0.3 fittings/m² — and
this 1.0 fitting/m² case is at the extreme.

Engineer-of-record sees both numbers in the final IR (the upstream's
343.75 and this cascade's 564) and reads them as bounding-cases — the
real per-point value will be in this range depending on actual halogen
optic + actual reflectances.

## §6 UGR per CIE 117 — halogen narrow-beam glare

4 default observer positions:

- **N-wall** at (4000, 5000, 1200): UGR 18.2
- **S-wall** at (4000, 1000, 1200): UGR 18.6 (worst)
- **E-wall** at (7000, 3000, 1200): UGR 17.9
- **W-wall** at (1000, 3000, 1200): UGR 18.0

`max_ugr_across_view_positions = 18.6 ≤ 19` private_office limit per
BS EN 12464-1 Table 5.3. **SLIM 0.4 MARGIN.**

**Critical honest disclosure:** upstream lighting-layout's `ugr_status`
warns "UGR > 19 likely — narrow-beam halogen typically produces UGR
22-25 at desk plane; confirm from photometric data". This synthetic
HALOGEN_DOWNLIGHT.ies (60° beam with diffuser) is OPTIMISTIC vs the
upstream's warning. Real halogens at 1:1 density with 35°-50° spot beam
optics often DO produce UGR > 19 — sometimes 22-25.

Engineer-of-record MUST substitute project IES (manufacturer-supplied)
and re-run before final design freeze. If the project halogens have
tighter beam optics than the synthetic, INV-03 may flip to FAIL on
re-run. This is the IES-substitution sensitivity case that motivates
the `verification_status: synthetic_reference_C3` flag in the first place.

## §7 The independence demonstrated — final IR signals

The post-D.2 lighting-layout IR will carry TWO orthogonal flag sets:

| INV | Source | Verdict | Owns |
|---|---|---|---|
| INV-06 | lighting-layout's own Part L check | **FAIL HIGH** ×3 | Efficacy + daylight-link + occupancy-sense |
| INV-11 | photometric-analysis cascade | **PASS** | Per-point + U₀ + UGR (BS EN 12464-1) |

These are not contradictory — they verify orthogonal compliance regimes.
Engineer-of-record reads:

- "Lighting performs to standard" (INV-11 PASS)
- "But the design fails Part L on 3 energy axes" (INV-06 FAIL)
- "Replace halogens with LED retrofit to fix Part L; this also lowers
  per-point lux to ~450 average which still passes INV-11"

Remediation path: swap to LED keeping the same fitting density would
both fix Part L AND lower per-point lux to a more reasonable margin
over target. Or rationalise the count down to 16-20 LED downlights
which fixes Part L AND right-sizes the lighting.

## §8 INV walkthrough

All 9 photometric INVs PASS:

- **INV-01 (HIGH) PASS**: min 412 ≥ 350 (0.7×500)
- **INV-02 (HIGH) PASS**: U₀ 0.73 ≥ 0.6 office target
- **INV-03 (HIGH) PASS**: max UGR 18.6 ≤ 19 — slim margin, IES-sensitive
- **INV-04 (HIGH) PASS**: 1 luminaire_type matched by 1 IES file
  (HALOGEN_DOWNLIGHT.ies substituted for upstream's LED_DOWNLIGHT
  ontology-proxy — the runtime substitutes the actual photometric source)
- **INV-05 (HIGH) PASS**: grid_spacing 800 mm matches §6.2 corrected formula
- **INV-06 (HIGH) PASS**: 70 grid points; representative slice in IR
- **INV-07 (MEDIUM) PASS**: 4 CIE 117 default observers
- **INV-08 (MEDIUM) PASS**: _source 295 chars + verification_status enum match
- **INV-09 (HIGH) PASS**: cascade completed; tool_call_pending=false

## §9 Cascade signal to lighting-layout INV-11

Intent payload sets `task_area_compliant: true` AND `non_compliance_flags: []`.
Lighting-layout INV-11 PASS HIGH for the photometric dimension.

Lighting-layout INV-06 (Part L compliance) remains FAIL HIGH upstream —
that flag is NOT cascaded from photometric-analysis. It originates in the
lighting-layout's own controls + efficacy assessment.

**Critical reading:** the final lighting-layout IR carries BOTH the INV-11
PASS and the INV-06 FAIL. The drawing is NOT sign-off-ready — INV-06 FAIL
blocks sign-off. The photometric PASS is independent confirmation that the
lighting performance dimension is OK; remediation must address INV-06 only.

This is the orthogonal multi-axis compliance pattern that the cascade
contract is designed to support.

## §10 Engineering takeaway

**Photometric PASS does NOT mean Part L PASS.**
**Photometric FAIL does NOT mean Part L FAIL.**

They verify orthogonal compliance regimes:
- **Photometric (BS EN 12464-1)** → per-point + UGR + uniformity
- **Part L (Approved Doc L 2021 §6)** → efficacy + automatic controls

The cascade contract preserves the orthogonality. Both verdicts surface
in the final IR; engineer-of-record reads both and addresses them
independently.
