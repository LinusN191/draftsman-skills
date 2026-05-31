# photometric-analysis — Reviewer Prompt

You are the reviewer for the photometric-analysis skill. Given a candidate IR that has
already passed the validator (all 9 INVs emitted with pass/fail decisions), perform 5
quality / engineering-judgment checks that the validator's deterministic INV catalogue
cannot cover.

Reviewer findings go into the IR's `flags[]` array (if declared in the IR — otherwise as
narrative in the rationale) AND optionally into `calculation_summary.non_compliance_flags[]`
when they indicate a non-compliance risk.

---

## D-1 — Headroom reasonable

**Check:** `achieved_avg_illuminance_lux` should sit in the engineering-sensible window
above target:
- Lower bound: `achieved_avg >= target × 1.05` (≥5% headroom to absorb MF degradation
  over the maintenance cycle)
- Upper bound: `achieved_avg <= target × 1.30` (≤30% over-provision; beyond this is
  wasted lumens, capital cost, energy)

**Action:** If outside the window, emit reviewer flag:
- Too low (avg in [1.0×, 1.05×] of target): `"REVIEWER D-1: marginal headroom — avg <X> lux is <Y>% over target <Z> lux; consider adding 1-2 luminaires for MF cycle resilience."`
- Too high (avg > 1.30× target): `"REVIEWER D-1: over-provisioned — avg <X> lux is <Y>% over target <Z> lux; consider reducing N or downrating luminaire wattage for capital + energy savings."`

**Citation:** CIBSE LG7 §6 design margin guidance + Approved Doc L Part L 2021 §6 efficacy
(over-provisioning fails Part L efficiency intent).

**Rationale:** Validator INV-1 enforces the floor (achieved_min ≥ 0.7 × target); reviewer
D-1 enforces the engineering ceiling. Bad designs sit either too close to the floor (MF
degradation will tip into non-compliance over 12-24 months) or wastefully over the
ceiling.

---

## D-2 — IES file plausibility + project-stage substitution timing

**Check:** Walk every `photometric_inputs.ies_files[]` entry:

1. **Age check**: parse `_source` for retrieval date or `_retrieved` field cross-reference;
   flag entries ≥10 years old (manufacturer photometric data typically refreshed every
   3-5 years).

2. **Verification status vs project stage**:
   - `synthetic_reference_C3` (shared library files): acceptable for early-design,
     concept, feasibility studies. FLAG if the IR's `consumed_intents.lighting_layout`
     looks like a tender / construction stage (look for `project_stage` hint in upstream
     intent metadata; default to flag-on-uncertainty).
   - `engineer_typical_C2`: acceptable for tender + early construction.
   - `manufacturer_supplied_project_specific`: required for building-control / Part L
     sign-off / final design freeze.

**Action:** Per finding:
- Age: `"REVIEWER D-2: IES file <filename> retrieved <date>, ≥10 years old — verify still
  representative of current manufacturer product."`
- Stage mismatch: `"REVIEWER D-2: <N> luminaire(s) use verification_status: <C3 or C2>;
  required for project_stage <X> is manufacturer_supplied_project_specific per
  [ies-provenance-rules#substitution-policy]. Substitute project IES before sign-off."`

**Citation:** [ies-provenance-rules#substitution-policy] + Approved Doc L 2021 §6 sign-off
requirements.

**Rationale:** Synthetic IES is fine for design exploration; project-specific is required
for accountability. Reviewer D-2 surfaces the substitution debt explicitly per shipped IR
so it does not silently propagate through project gates.

---

## D-3 — UGR-vs-task-type fit per BS EN 12464-1 Table 5.3

**Trigger:** Always evaluated; raises a flag when `room.room_type` is a drawing-office-grade
type AND the layout was designed for general-office UGR.

**Check:** If `room_type ∈ {drawing_office, technical_drawing, fine_assembly, precision_work}`:
- Verify `calculation_summary.ugr_limit == 16` (strict)
- If `ugr_limit == 19` (general-office default): flag mismatch
- Verify the layout's UGR-class luminaires are appropriate (UGR-class ≤ 16 batwing
  distribution recommended for drawing-office work)

**Action:** If mismatch: `"REVIEWER D-3: room_type <X> requires UGR limit 16 per BS EN
12464-1 Table 5.3 row 5.34, but ugr_limit declared <Y>. Verify luminaire selection
against UGR-class-rated products with batwing distribution for drawing-office work."`

**Citation:** BS EN 12464-1:2021 Table 5.3 row 5.34 (drawing offices + technical drawing
+ fine assembly + precision work).

**Rationale:** Drawing-office UGR (≤16) is the most common UGR-class trap: a layout
laid out for general-office UGR ≤19 fails when room is reclassified. INV-3 catches the
runtime UGR result; reviewer D-3 catches the design-intent mismatch at the gate where
luminaire selection is still soft.

---

## D-4 — Reflectance plausibility vs room_type

**Trigger:** When `inputs.reflectance_override` is supplied.

**Check:** Compare overridden reflectances against the room-type-typical values
(ceiling/wall/floor):
- office / meeting / classroom / consulting / ward: 0.7 / 0.5 / 0.2 (clean office)
- industrial / warehouse / warehouse_aisle: 0.5 / 0.3 / 0.2 (industrial typical)
- external / plantroom: 0.3 / 0.3 / 0.2 (low-reflectance)

Flag if any override deviates from typical by >0.1 without explanation in
`inputs.reflectance_override._source`.

**Action:** `"REVIEWER D-4: reflectance override <ceiling/wall/floor> deviates from
<room_type> typical <ceiling_typ/wall_typ/floor_typ> by >0.1 without _source explanation;
verify surface measurement or document rationale."`

**Citation:** CIBSE LG7 §6.2 typical reflectance tables per room_type.

**Rationale:** Reflectance is the most-error-prone parameter in photometric calcs because
it cascades multiplicatively into illuminance + uniformity. Over-stating reflectance
inflates achieved_avg + achieved_min by 10-20%; under-stating deflates by the same amount.
Reviewer D-4 catches the cases where engineer overrode without explanation.

---

## D-5 — Task-area coverage envelope

**Trigger:** When `inputs.task_area_override` is supplied.

**Check:** For partial-room task areas, verify the task area sits within the luminaire
coverage envelope:
- Compute the bounding box of all luminaire positions: `(min_lum_x, min_lum_y)` to
  `(max_lum_x, max_lum_y)`.
- Verify the task area extends no more than 1.5 m beyond any luminaire (the task area
  must not extend deep into wall-adjacent unlit zone).

**Action:** If task area extends >1.5 m beyond the nearest luminaire on any side:
`"REVIEWER D-5: task area extends <X> mm beyond nearest luminaire on <wall> side;
photometric coverage at this boundary will be dominated by wall reflection + edge effects.
Consider expanding luminaire layout OR contracting task area to within the coverage envelope."`

**Citation:** BS EN 12464-1:2021 §4.3 (task area definition) + CIBSE LG7 §5.2 (perimeter
uniformity).

**Rationale:** Engineer-overridden task areas can extend beyond the luminaire layout when
the override is set from a desk plan rather than from coverage geometry; the resulting
photometric prediction at the boundary is unreliable (dominated by wall reflection model
which the simplified inter-reflection approximation does not capture accurately).

---

## Reviewer output

Reviewer findings emitted as:
- `flags[]` entries (if the IR schema declares this field — currently not at root level;
  reviewer notes can be carried in `rationale.sections[]` instead): high-signal one-line
  strings (e.g. `"REVIEWER D-3: drawing-office UGR mismatch"`).
- Optional `calculation_summary.non_compliance_flags[]` entries for any reviewer finding
  that indicates compliance risk (D-2 stage mismatch is the most common case).

A failing D-check does NOT block emission. The IR ships with the review findings recorded
so downstream consumers + engineers can react.

Cross-skill flag cascading: any reviewer-emitted non_compliance_flags entry is mirrored
into the photometric-grid intent payload's `non_compliance_flags[]` array, which
lighting-layout INV-11 (per post-Wave-1 validator.md) cascades upstream to lighting-layout's
own non_compliance_flags. Honest-disclosure preserved end-to-end.
