# photometric-analysis — Validator Prompt

You are the validator for the photometric-analysis skill. Given a candidate IR (per
`schemas/photometric-analysis-ir.schema.json`), verify that all 9 INVs below PASS or emit
an explicit failure with severity classification.

Validate the IR in this order:

1. **Schema-level checks first** (JSON Schema validation against the IR schema — the golden
   CI gate `scripts/validate-examples.py` does this automatically; treat as precondition).
2. **Per-INV checks** in numeric order INV-01 → INV-09.

For each INV, emit an entry into the IR's `invariants[]` array per the shape:
- `id`: matches pattern `^INV-[0-9]{2,3}$` (use two-digit zero-padded form: `INV-01` .. `INV-09`)
- `passes`: boolean
- `severity`: enum {critical, high, medium, low}
- `evidence`: prose 20-800 chars stating WHY the rule passed/failed; cite specific values
  from the IR; NEVER boilerplate.

If a check requires data the generator did not emit, set `passes: false` AND `severity:
high` (the schema enforces the required fields; missing data is a generator bug).

---

## INV-01 — Achieved minimum illuminance ≥ 70% of target (HIGH)

**Severity:** HIGH

**Rule:** `calculation_summary.achieved_min_illuminance_lux >= calculation_summary.target_illuminance_lux × 0.7`

**Validator action:**
- Read both values from calculation_summary.
- Compute the 70% threshold: `threshold = target_illuminance_lux × 0.7`.
- If achieved_min_illuminance_lux ≥ threshold: PASS. Evidence cites both values + the
  computed ratio.
- If achieved_min_illuminance_lux < threshold: FAIL HIGH. Evidence states the actual
  deficit + cites the cold point coordinates (find the point in illuminance_grid[] with
  the minimum E_lux value) + cites the room_type-driven target.

**Citation:** BS EN 12464-1:2021 Table 5.3 + §4.4 (maintained illuminance task-area minima).

**Rationale:** Lumen-method gives average; lumen-method-passing layouts routinely fail the
per-point minimum at task-area corners (the bug photometric-analysis was built to catch).
70% is the standard's typical task-area uniformity floor before U₀ explicitly enforces.

---

## INV-02 — Achieved uniformity U₀ ≥ target (HIGH)

**Severity:** HIGH

**Rule:** `calculation_summary.achieved_uniformity_u0 >= calculation_summary.uniformity_u0_target`

Target per room_type (from [ugr-rules#per-room-type-limits] cross-reference — same room_type
enum applies to U₀ targets per BS EN 12464-1 Table 5.3):
- office/classroom/meeting/consulting/ward: 0.6
- drawing_office/technical_drawing/fine_assembly/precision_work: 0.7
- corridor/escape_route/plantroom: 0.4
- reception_lobby/bathroom/kitchen_commercial: 0.4
- warehouse/warehouse_aisle: 0.4

**Validator action:**
- Read achieved_uniformity_u0 + uniformity_u0_target from calculation_summary.
- If achieved_uniformity_u0 ≥ uniformity_u0_target: PASS. Evidence cites both values.
- If achieved_uniformity_u0 < uniformity_u0_target: FAIL HIGH. Evidence cites the
  ratio + which room_type-typical target applies + cites the cold point (E_min
  coordinates) driving the failure.

**Citation:** BS EN 12464-1:2021 §4.4 + Table 5.3 per-room-type U₀.

**Rationale:** Uniformity is the per-point distribution test BS EN 12464-1 §4.4 mandates
separately from average illuminance. Lumen-method has no U₀ output; photometric-analysis
is the cascade gate.

---

## INV-03 — UGR maximum ≤ limit (HIGH)

**Severity:** HIGH

**Rule:** `calculation_summary.max_ugr_across_view_positions <= calculation_summary.ugr_limit`

UGR limit per room_type per [ugr-rules#per-room-type-limits]:
- office/classroom/meeting/consulting/ward: 19
- drawing_office/technical_drawing/fine_assembly/precision_work: 16 (stricter)
- reception_lobby/kitchen_commercial/bathroom: 22
- warehouse_aisle: 22
- corridor/warehouse/escape_route/plantroom: 25
- external: N/A (UGR not defined for outdoor)

**Validator action:**
- Read max_ugr_across_view_positions + ugr_limit from calculation_summary.
- If max_ugr_across_view_positions ≤ ugr_limit: PASS. Evidence cites both values + the
  worst observer position from ugr_results[].
- If max_ugr_across_view_positions > ugr_limit: FAIL HIGH. Evidence cites the worst
  observer position (label + bearing) + the UGR value + the room_type-driven limit.

**Citation:** BS EN 12464-1:2021 §6.6 + Table 5.3 + CIE 117 (UGR formula).

**Rationale:** Glare is a per-observer-direction failure mode; an avg-only calc misses it
structurally. Drawing offices (UGR ≤ 16) are notably stricter — workstations laid out for
general-office UGR ≤ 19 fail when the room is reclassified for drafting work.

---

## INV-04 — IES file per luminaire_type required (HIGH)

**Severity:** HIGH

**Rule:** For every distinct `luminaire_type.symbol` in the upstream lighting-layout intent:
1. There MUST be a matching entry in `photometric_inputs.ies_files[]` (matched by
   `luminaire_type` field).
2. The matching entry's `path` MUST resolve to a readable LM-63 file (runtime parser
   confirms via `parsed_summary` block).

**Validator action:**
- Enumerate distinct luminaire_type symbols from
  `consumed_intents.lighting_layout.consumed_summary`.
- Verify 1:1 coverage in `photometric_inputs.ies_files[]` (one entry per distinct symbol).
- Verify each entry's `parsed_summary` block is populated (non-null total_lumens,
  candela_grid_dimensions, etc.).
- If 1:1 coverage holds AND every entry parses: PASS.
- If any symbol is missing OR any entry's parsed_summary is empty/unparseable:
  FAIL HIGH + non_compliance_flags critical entry naming the offending symbol.

**Citation:** Spec §2.1 Full v1.0 scope decision (no ontology UF fallback at production).

**Rationale:** Skill refuses to compute without IES per the brainstorm decision. Approximate
output mistakenly treated as DIALux-grade was the maturity-audit pain point that motivated
the whole companion skill.

---

## INV-05 — Grid spacing matches BS EN 12464-1 §6.2 formula (HIGH)

**Severity:** HIGH

**Rule:** `photometric_inputs.grid_metadata.grid_spacing_mm` matches the §6.2 adaptive
formula output within ±50 mm tolerance.

Canonical formula (per [grid-spacing-rules#adaptive-formula]):

```
d_m         = max(task_area_length_m, task_area_width_m)   # longer task-area dimension
p_m         = 0.2 × 5^log₁₀(d_m)                            # raw spacing in metres
expected_p_mm = round_to_50(p_m × 1000) clamped to [50, 1000]
abs(grid_spacing_mm - expected_p_mm) ≤ 50
```

Reference evaluations from [grid-spacing-rules#worked-examples]:
- d_m = 4   → p_m = 0.530 m → snapped 550 mm
- d_m = 9   → p_m = 0.910 m → snapped 900 mm
- d_m = 11  → p_m = 1.058 m → snapped 1000 mm (clamped at upper bound)
- d_m = 14  → p_m = 1.273 m → snapped 1000 mm (clamped at upper bound)

**Validator action:**
- Read task_area_bounds from photometric_inputs (or from
  consumed_intents.lighting_layout if task_area_bounds is null).
- Compute d_m = max(length_mm, width_mm) / 1000.
- Compute p_m = 0.2 × 5^log₁₀(d_m).
- Compute expected_p_mm = round_to_50(p_m × 1000), clamped to [50, 1000].
- Compare grid_spacing_mm to expected_p_mm.
- If abs(grid_spacing_mm - expected_p_mm) ≤ 50: PASS. Evidence cites d_m + p_m +
  expected_p_mm + actual grid_spacing_mm.
- Else: FAIL HIGH. Evidence cites both values + the formula derivation + the deviation
  beyond the ±50 mm tolerance.

**Citation:** BS EN 12464-1:2021 §6.2 + [grid-spacing-rules#adaptive-formula] +
[grid-spacing-rules#tolerance].

**Rationale:** Standards-correct grid sizing is the difference between BS EN 12464-1
§6.2 compliance and ad-hoc per-implementer grids. Fixed-spacing alternatives over-sample
small areas + under-sample large ones; the formula matches the standard's intent.

---

## INV-06 — Grid shape consistency (HIGH)

**Severity:** HIGH

**Rule:**
1. `illuminance_grid.length == grid_metadata.point_count`
2. Every grid point `(x_mm, y_mm)` is inside `task_area_bounds` (x_min ≤ x ≤ x_max AND
   y_min ≤ y ≤ y_max).
3. No duplicate (x_mm, y_mm) coordinates across illuminance_grid[].

**Validator action:**
- Count illuminance_grid entries; compare to grid_metadata.point_count.
- For each point, verify x_min ≤ x_mm ≤ x_max AND y_min ≤ y_mm ≤ y_max against
  task_area_bounds.
- Build a set of (x_mm, y_mm) tuples; verify set size equals list length (no duplicates).
- If all three sub-conditions hold: PASS. Evidence cites the verified counts.
- If any sub-condition fails: FAIL HIGH. Evidence cites which sub-condition + the
  offending count/coordinate.

**Citation:** Spec §5.1 IR schema + §6 INV catalogue.

**Rationale:** Catches grid-emission bugs where the point list drifts from the declared
metadata. Downstream consumers (heatmap renderer, INV-01/02 evaluators) assume metadata-grid
consistency.

---

## INV-07 — UGR default observers present (MEDIUM)

**Severity:** MEDIUM

**Rule:** `ugr_results[]` carries ≥4 entries with `_source: "cie_117_default"`. Additional
entries with `_source: "engineer_supplied"` may follow (from
inputs.ugr_view_positions_override).

**Validator action:**
- Filter ugr_results[] by `_source == "cie_117_default"`.
- Count the filtered entries.
- If count ≥ 4: PASS. Evidence lists the 4 default observer labels (N, S, E, W
  wall-facing per [ugr-rules#default-observer-positions]).
- Else: FAIL MEDIUM. Evidence states which default(s) are missing (one or more of
  N, S, E, W per [ugr-rules#default-observer-positions]).

**Citation:** [ugr-rules#default-observer-positions] + CIE 117 + BS EN 12464-1:2021 §6.6.

**Rationale:** A rectangular room evaluated from only 1-2 observer directions misses
glare visible from other observer positions. 4 wall-facing defaults are the standard
minimum-meaningful coverage; engineer adds project-specific positions on top.

---

## INV-08 — IES provenance ≥40 chars + verification_status valid (MEDIUM)

**Severity:** MEDIUM

**Rule:** Every `photometric_inputs.ies_files[]._source` string is ≥40 chars AND the
file's `verification_status` is one of:
- `synthetic_reference_C3`
- `engineer_typical_C2`
- `manufacturer_supplied_project_specific`

Per [ies-provenance-rules#source-string-minimum] +
[ies-provenance-rules#verification-status-enum].

**Validator action:**
- For each entry in photometric_inputs.ies_files[]:
  - Verify `len(_source) >= 40`.
  - Verify `verification_status` is in the 3-value enum above.
- If both checks pass for every entry: PASS. Evidence cites the entry count + a
  representative provenance snippet.
- Else: FAIL MEDIUM. Evidence cites the failing entry's luminaire_type + the failing
  field (_source length OR verification_status value).

**Citation:** [ies-provenance-rules#source-string-minimum] +
[ies-provenance-rules#verification-status-enum] + D2.3 honest-disclosure pattern.

**Rationale:** Preserves the no-fabricated-citations discipline. Provenance strings under
40 chars cannot carry the 4 required content elements (manufacturer/archetype + product/model
+ date + caveat). Catches casual or lazy provenance entries before they propagate downstream
to lighting-layout INV-11 + Wave 3/4 consumers.

---

## INV-09 — Calc actually ran (HIGH)

**Severity:** HIGH

**Rule:**
1. `calculation_summary.tool_call_pending == false`
2. `calculation_summary._calc_tool == "calc.lumen_grid_solver"`
3. `calculation_summary._calc_engine_version` is a non-empty string

**Validator action:**
- Read calculation_summary.tool_call_pending, _calc_tool, _calc_engine_version.
- Verify all 3 sub-conditions.
- If all pass: PASS. Evidence cites _calc_tool + _calc_engine_version values.
- Else: FAIL HIGH. Evidence cites which sub-condition failed:
  - tool_call_pending still true (calc never resolved)
  - _calc_tool mismatch (wrong tool invoked)
  - _calc_engine_version empty (runtime did not stamp version)

**Citation:** Spec §5.1 + [[runtime-project-boundary]] (runtime is responsible for setting
`tool_call_pending: false` after `calc.lumen_grid_solver` returns).

**Rationale:** Phantom IRs that look schema-valid but never invoked the runtime calc are
the silent-failure-mode photometric-analysis must guard against. INV-09 is the structural
gate confirming the cascade actually completed end-to-end.

---

## Validator output

After running all 9 INVs, the IR's `invariants[]` array carries 9 entries in numeric
order INV-01 .. INV-09. Each entry includes example-specific evidence (NOT boilerplate).

A failing INV does NOT block emission — the IR ships with the failure recorded so
downstream consumers (lighting-layout INV-11) can react.

**Cross-skill cascade:** when this skill's IR has any FAIL among INV-01, INV-02, INV-03,
the intent payload's `photometric_grid.task_area_compliant` is set to `false` AND
`non_compliance_flags[]` carries the failure messages naming the failing INV id(s) +
the affected cold-point/observer coordinates. Lighting-layout INV-11 (per post-Wave-1
`electrical/lighting-layout/prompts/validator.md`) reads
`consumed_intents.photometric_analysis.task_area_compliant` +
`consumed_intents.photometric_analysis.non_compliance_flags[]` then cascades the failure
upstream to lighting-layout's own `non_compliance_flags[]`. This is the canonical
photometric-analysis → lighting-layout failure-propagation path established in spec §3
(cross-skill cascade contract).

Reviewer (per `prompts/reviewer.md`) runs after this validator. Reviewer D-checks
exercise engineering-judgment calls that sit beyond validator-enforceable rules
(luminaire-archetype suitability, task-area-override defensibility, UGR-observer-coverage
adequacy, IES-vintage caveats, cascade-narrative coherence).

## Floor plan context

When the prompt context includes a `## Floor plan context` markdown
block, the validator MUST surface a finding for any of:

1. IR includes coordinate-level geometric placement claims derived
   from the block (this is a context-only skill).
2. IR's `building_label` field (if present) does not match the
   building label in the block.
3. IR omits `floor_plan_context_consumed: true` when the block was
   present.

Findings should cite the room name and the block location so the
reviewer can correlate.
