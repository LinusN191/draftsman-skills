# Changelog — lighting-layout

## [1.6.0] - 2026-06-01 — Floor plan context portability

### Changed
- Replaced previous Sprint 4-AB `architectural_state` section in
  `prompts/{generator,reviewer,validator}.md` with the generic
  `## Floor plan context` contract. Prompt is now portable across AI
  runtimes that inject room-list markdown under that heading.
- Inlined the contract per-file; deleted the previous
  `shared/architectural_state_contract.md` dependency.

### Added (IR schema — `schemas/lighting-layout-ir.schema.json`)
- NEW optional top-level `floor_plan_context_consumed: boolean`
  (default `false`). IR sets `true` when the prompt context included
  a `## Floor plan context` block.

## [1.5.0] - 2026-05-30 — Photometric cascade contract activation (Wave 1)

### Changed
- `skill.manifest.json` version 1.4.0 → 1.5.0 (additive; backward-compatible IR additions)
- `consumes_intents[]` populated with photometric-grid cascade entry (trigger:
  `mode == 'full_drawing'`; consumed fields: `achieved_avg_illuminance_lux`,
  `achieved_min_illuminance_lux`, `achieved_uniformity_u0`, `ugr_max`,
  `task_area_compliant`, `non_compliance_flags`) — first downstream-cascade
  consumer for this skill.

### Added (IR schema — `shared/schemas/electrical/lighting-layout-ir.schema.json`)
- NEW `consumed_intents` top-level block with `photometric_grid` sub-object
  (`intent_version` + `source_path` + `payload` via `$ref` to
  `photometric-grid-intent.schema.json`).
- Extended D3.A.3 `allOf` else-branch: `required[]` now includes `consumed_intents`
  alongside the 9 existing fields (10 entries total).
- NEW 2nd `allOf` clause: when `mode == full_drawing`,
  `consumed_intents.photometric_grid` is structurally required (semantic content
  enforced by INV-11).
- `invariants[].evidence` `maxLength` raised 800 → 1200 per
  `[[feedback-no-trim-non-consequential]]`: failure-mode INV-11 evidence carries
  cascade source path + lux comparison numbers + flag attribution + remediation
  guidance, which legitimately exceeds the prior style cap (833–849 chars).

### Added (intent schema — `electrical/lighting-layout/schemas/lighting-layout-intent.schema.json`)
- NEW `consumed_intents.photometric_grid` permissive sub-object so the cascade
  block mirrored on the intent-out side passes Pass-4 validation. Semantic
  gating remains on the IR side via the typed `$ref`.

### Changed (validator — `prompts/validator.md`)
- INV-11 appended (no prior placeholder existed) — 4 sub-check cascade rule:
  1. `consumed_intents.photometric_grid` present
  2. `payload.task_area_compliant == true`
  3. `payload.achieved_avg_illuminance_lux >= target_illuminance_lux`
  4. `non_compliance_flags` cascading with `_cascaded_from` attribution
- Severity HIGH when `mode == full_drawing`; N/A when `calc_only`.

### Changed (7 examples retrofit)
- All 7 existing examples (office-open-plan, reception-lobby, warehouse-highbay,
  uk-undersized-lighting-vs-target, uk-multi-entrance-classroom,
  uk-part-l-fail-incandescent, uk-open-plan-office-10x8-dali) now consume the
  photometric-grid intent from the corresponding
  `electrical/photometric-analysis/examples/cascade-<example-name>/intent-out.json`.
- `input.json`: added `photometric_ies_paths[]` top-level key referencing
  `shared/photometric/ies/<type>.ies`.
- `output.json`: added `consumed_intents.photometric_grid` block + appended
  INV-11 evidence entry citing all 4 sub-checks with real cascade values.
- `intent-out.json`: mirrored `consumed_intents.photometric_grid` block.

### Failure-mode cascade demonstrations
- `uk-undersized-lighting-vs-target` demonstrates end-to-end failure cascade:
  photometric INV-01 + INV-02 FAIL → cascade `non_compliance_flags` → lighting-
  layout INV-11 FAIL HIGH + cascade attribution via `_cascaded_from:
  "photometric-analysis"` (no silent suppression).
- `uk-part-l-fail-incandescent` demonstrates photometric/Part-L compliance
  independence: INV-11 PASS at photometric level + lighting-layout INV-6 FAIL
  at Part-L level (the two compliance regimes are evaluated separately).

### Honest disclosures preserved
- All cascades use `synthetic_reference_C3` IES files from
  `shared/photometric/ies/`.
- Engineer-of-record substitutes project IES before final design freeze per
  `[ies-provenance-rules#substitution-policy]`.
- Flag `_cascaded_from` attribution makes the photometric origin traceable
  end-to-end through the lighting-layout `calculation_summary.non_compliance_flags[]`.

### Cross-references
- photometric-analysis spec: `docs/superpowers/specs/2026-05-30-photometric-analysis-design.md`
- photometric-analysis sprint plan: `docs/superpowers/plans/2026-05-30-photometric-analysis-sprint.md`
- Cluster roadmap: `docs/superpowers/specs/2026-05-29-lighting-cluster-roadmap.md`

### Gates
- `validate-examples.py`: 236/236 (post-D3) → 262/262 (+26 across Wave 1 sprint).
- `functional_audit.py`: 1 finding unchanged (disclosed motor-superposition oracle FP).

## [1.4.0] - 2026-05-29 — Sprint D3 (lighting-layout depth)

### Added (Phase A — foundations)
- **ontology/luminaire-types.json**: photometric block per type
  (uf_table_by_ri + shr_max + llmf_schedule + _citation). 5 types
  (LED_PANEL_600, LINEAR_LED, LED_DOWNLIGHT, HIGHBAY, EMERGENCY).
  Citations: CIBSE LG7 §6.2 + BS EN 12464-1:2021 §4.4 + CIBSE LG12.
- **ontology/switching-types.json**: electrical ratings + symbol
  mapping + 4 new types (3_gang, daylight_sensor, presence_with_dimming,
  dali_application_controller).
- **NEW ontology/emergency-types.json**: 5 emergency-luminaire types
  per BS 5266-1:2016 (non_maintained_self_test, maintained_self_test,
  escape_route_luminaire, open_area_anti_panic, high_risk_task_area).
- **rules/*.yaml** (all 5): promoted to structured {id, value,
  citation, rationale} form. Drift fix: switching-rules#height
  standardised to 1200 mm AFF (was inconsistent with generator's
  1350 mm). Each rule cites BS 7671 + IET OSG + Approved Doc L
  (Part L 2021) §6 + BS EN 15193-1 + BS 5266-1 + CIBSE LG7.

### Added (Phase A — schemas)
- **IR schema (shared/schemas/electrical/lighting-layout-ir.schema.json)**:
  - zones[]: zone_type enum (perimeter|interior|task|emergency) +
    control enum + circuit_ids[] + luminaire_ids[].
  - circuits[]: row_index + homerun_endpoint {x_mm, y_mm, wall}
    (wall required).
  - circuits[].total_load_w: allOf-conditional max per mcb_rating_a
    (BS 7671 §433.1.1 80% rule: 6A→1104, 10A→1840, 16A→2944, 20A→3680,
    32A→5888).
  - room.room_type: 15-value enum (was bare string).
  - drafting_furniture top-level (required when mode=full_drawing):
    title_block + scale_bar + dimensions[] + luminaire_schedule, all
    with explicit font_family + font_size_pt. Negative-space coords
    permitted on dimensions[] + scale_bar (CAD convention).
  - selection_source top-level: photometric_source enum + citation.
- **Intent schema**: extended payload with zones + circuits_topology
  (NEW per A.3 to avoid name collision with legacy circuits[]) +
  switches.
- **inputs.json**: door_swing required on entrance_positions item
  (5-value enum); photometric_override optional struct;
  ceiling_grid_mm tightened to enum [0, 600, 1200].

### Added (Phase B — prompts)
- **Generator Step 6 (lumen method) rewritten**: full worked example
  with concrete numbers (N=12.44 → round UP to 13) + counter-example
  showing round-to-nearest under-provides at 482 lux + calc.lumen_grid_solver
  output spec documented inline.
- **Generator Step 7 (S/H ratio) rewritten**: explicit enforcement loop
  with iterative grid bump (12→16→20 walk).
- **Generator Step 11 (NEW) circuit topology**: Part L zone assignment
  decision tree + per-row load limit table + homerun selection logic.
- **Generator Step 12 (switch placement) rewritten**: deterministic
  entrance → switch mapping via door_swing latch-side resolution table.
- **Generator Step 15 (NEW) drafting furniture**: title_block + scale_bar
  + dimensions[≥2] + luminaire_schedule emission with explicit font fields.
- **Generator Step 16 (NEW) intent payload emission**: zones + circuits
  + circuits_topology + switches per extended intent schema (FLAT shape).
- **Validator prompt (4 → ~250 lines)**: full INV-1..INV-10 catalogue.
- **Reviewer prompt (4 → ~150 lines)**: D-1..D-6 quality checks.

### Added (Phase C — examples)
- **reception-lobby promoted**: calc_only → full_drawing (104 → ~400
  lines). 30 LED_DOWNLIGHT in 5×6 grid; 2 zones (Z1 perimeter
  daylight-linked + Z2 interior); all 10 INVs PASS.
- **warehouse-highbay promoted**: calc_only → full_drawing (89 → ~400
  lines). 20 HIGHBAY in 4×5 grid + 12 EMERGENCY anti-panic (3×4 grid
  for BS 5266-1 §5.3 coverage); 4 row circuits at 1250W on 10A MCBs;
  all 10 INVs PASS.
- **NEW uk-undersized-lighting-vs-target**: demonstrates INV-1 FAIL
  (434 < 500 lux) + INV-6 FAIL (part_l_assessed=false on new-build)
  + INV-10 FAIL (composite).
- **NEW uk-multi-entrance-classroom**: demonstrates INV-3 multi-entrance
  coverage (3 switches at 3 latch sides). All 10 INVs PASS.
- **NEW uk-part-l-fail-incandescent**: demonstrates INV-6 FAIL critical
  (halogen 15 lm/W ≪ 95 lm/W Part L target).
- **NEW uk-open-plan-office-10x8-dali (canonical re-test)**: user's
  verbatim original prompt; 20 luminaires in 4×5 grid + 4 row circuits
  + DALI master + L-001 P1 1:50 A3 drafting furniture; all 10 INVs PASS;
  reasoning.md §10 maps each visible bug from original CAD output to
  the INV that catches it.

### New INVs (10 total in validator.md)
- INV-1 (HIGH): achieved_illuminance_lux ≥ target_illuminance_lux
- INV-2 (HIGH): S_x ≤ SHR_max × Hm AND S_y ≤ SHR_max × Hm
- INV-3 (HIGH): switch coverage + 1200 mm AFF + latch placement
- INV-4 (HIGH): no Z-pattern + homerun on wall
- INV-5 (HIGH): circuit total_load_w ≤ 80% × mcb × 230V
- INV-6 (HIGH): Part L compliance when is_uk_new_build
- INV-7 (MEDIUM): zone assignment + perimeter ↔ glazing iff consistency
- INV-8 (MEDIUM): photometric source resolved (no improvisation)
- INV-9 (MEDIUM/HIGH): drafting furniture complete with font fields
- INV-10 (HIGH): schema fields populated + non_compliance_flags shape

### Honest disclosures
- Photometric ontology values flagged verification_status=engineer_typical_C2
  — values are industry-typical per CIBSE LG7; engineer-of-record must
  verify against manufacturer photometric file for project-critical
  installations.
- BS5266 standards directory is a stub (README + meta.json only);
  emergency-types.json + emergency-rules.yaml cite the published
  BS 5266-1:2016 directly.
- §714 misattribution corrected: §714 in BS 7671 + IEC 60364 is
  External Lighting installations (NOT occupancy controls). All
  control-related cites use Approved Doc L (Part L 2021) §6
  consistently. Guard notes added to control-rules.yaml + spec to
  prevent regression.

### Gates
- validate-examples.py: 225 → **236** (+11 across phases: 2 promoted
  stubs gain intent-out.json + reasoning regen, 3 failure-mode examples
  × 2 files, 1 canonical × 2 files).
- functional_audit.py: 1 finding unchanged (motor-superposition oracle
  FP on us-industrial-with-motors/MCC-1, disclosed in D1.1).

### Schema migration impact
- IR schema adds 7 new required-in-full-drawing-mode fields (zones,
  drafting_furniture, selection_source) + tightens circuits.total_load_w
  per mcb_rating_a + permits negative-space coords on dimensions[] +
  scale_bar (CAD convention). Existing v1.3.x consumers reading 1.4.0
  outputs: additive fields are ignored if unrecognised. Consumers that
  DO need zones / homerun / drafting_furniture must be aware of the
  schema bump.

## [1.3.1] - 2026-05-25 — M1 hybrid eval-vs-IR fix

### Added
- `invariants[]` field added to the IR root (required). Each entry is
  `{id: "INV-NN", passes: bool, severity: critical|high|medium|low, evidence: 20-800c prose}`.
- Generator prompt gained a step instructing it to populate `invariants[]` per
  validator-INV that applies to the current example.

### Changed
- Eval assertions reconciled to actual IR field locations. Where evals
  referenced runtime-fan-out fields (`ir.emitted_intents`, `ir.intent_emitted`,
  `ir.citations` at root), assertions now point at the equivalent IR field
  (rationale section summaries / decisions[*].code_clause / sibling IR root
  fields). `ir.invariants.INV-NN.passes` rewritten as
  `ir.invariants[?(@.id=="INV-NN")].passes` to match the new array shape.

### Rationale
Sprint B Task B.5 — closes M1 (functional_audit MEDIUM eval-vs-output drift).
Evals were aspirational specs that had drifted from the IR schemas; this
change makes the validator-INV evidence visible to the runtime eval harness
and fixes the dangling-path findings without weakening the engineering
contract.

## v1.3.0 (current)
- Add `inputs.json` carrying full discovery taxonomy (15 items with answer_type, validators, defaults, depends_on)
- Add `inputs_path: "inputs.json"` to manifest pointing at the new taxonomy
- Bare-string `inputs: [...]` array retained for back-compat; will be removed in v2.0.0
- Conforms to new `shared/schemas/core/inputs.schema.json` metaschema (upstream Work Item 1)
- Rewrite all 7 evals (`eval-01` … `eval-07`) to conform to `shared/schemas/core/eval.schema.json` — restricted assertion grammar, category field, severity, standard refs
- Add `evals/runner-config.json` declaring minimum status thresholds and minimum model class
- README documents eval coverage matrix (5 required categories + 2 skill-specific) (upstream Work Item 5)
- IR schema bump — `rationale` block now required at IR root per `shared/schemas/core/rationale.schema.json`
- Canonical IR schema authored at `shared/schemas/electrical/lighting-layout-ir.schema.json` (resolves the previously-dangling $ref)
- Generator prompt gains Step 14 — rationale emission (chat_summary + 8-section taxonomy + decision shape)
- All 3 example outputs regenerated with rationale blocks consistent with their reasoning
- Add `eval-08-rationale-block.yaml` asserting rationale presence, length bounds, and decision-rule citations (upstream Work Item 2)
- Declare `produces_intent: "lighting-layout"` + schema at `schemas/lighting-layout-intent.schema.json` (stable subset: room_id, luminaire_summary, circuits, emergency_lighting_present, controls_summary)
- `consumes_intents: []` for now — earthing / cable-containment will be added when those skills are authored (upstream Work Item 4)

## v1.2.0
- MF environment cross-check table (7 environment types)
- BS 8300 luminance ratios for entrance transition zones
- Door swing direction input and latch-side switch placement
- db_designation field in circuits and metadata

## v1.1.0
- Part L efficacy check and controls matrix
- Zone-based circuit naming (Z1 perimeter, Z2 interior)
- LLMF detection and design lumen conversion
- IP rating check by environment type
- CCT appropriateness table
- Dimming protocol comparison table
- UGR disclaimer on every layout
- Perimeter zone identification (2000mm from glazed wall)
- Vertical illuminance requirements (whiteboard, faces)

## v1.0.0
- Initial production release
- Lumen method calculation
- Grid layout with 50mm snap
- Circuit load check (10A MCB, 80% rule)
- BS EN 12464-1:2021 lux targets table
