# Changelog — lighting-layout

## [1.7.0] - 2026-06-05 — Wave 2: task/ambient zone-purpose split + 3D pendant placement

_Wave 2 second deliverable. Adds zone-purpose semantics (task / surrounding / background), 3D luminaire placement fields, per-zone lux achievement tracking, 7 new invariants (INV-13..19), 3 new reviewer D-checks, 5 new evals, 12 examples (8 retrofit + 4 new), and 1 new verified standards file. Additive minor bump; existing IRs remain valid (all new fields optional)._

### Changed
- `skill.manifest.json` version 1.6.0 → 1.7.0 (additive; backward-compatible IR additions).

### Added (IR schema — `schemas/lighting-layout-ir.schema.json`)
- **`zones[].purpose`** — required string enum when `zones[]` is present:
  `task | surrounding | background`. Aligns to BS EN 12464-1:2021 §4.2.2.
- **`zones[].em_target_lux`** — optional integer; emergency maintained lux
  target for this zone (BS EN 12464-1:2021 Table 5 + BS EN 1838:2013 §5.3).
- **`luminaires[].mount_type`** — optional string enum:
  `surface | recessed | pendant | suspended | track | pole | wall`.
- **`luminaires[].z_mm`** — optional integer; mounting height above finished
  floor level in mm.
- **`luminaires[].suspension_length_mm`** — optional integer; rod/cable drop
  from ceiling in mm.
- **`calc.per_zone_achieved[]`** — optional array; per-zone lux achievement
  records keyed to `zone_id`, carrying `achieved_lux`, `target_lux`,
  `ratio_compliance`, and `gap_pct`. Populated when photometric-grid cascade
  present (INV-11) or lumen-balance calc available; vacuously empty otherwise.
- **allOf clause 3** — pendant/suspended `mount_type` requires both `z_mm`
  AND `suspension_length_mm` to be present (structural enforcement; semantic
  verification by INV-16).
- **allOf clause 4** — pendant identity constraint: if `mount_type = pendant`,
  then `suspension_length_mm > 0`.
- **allOf clause 5** — orphan-surrounding blocked: a zone with
  `purpose = surrounding` MUST NOT exist without at least one `task` zone in
  the same room (structural + INV-14 semantic enforcement).

### Added (validator — `prompts/validator.md`)
- **INV-13 — Zone purpose required + valid (HIGH)**: every zone has a
  `purpose` from the allowed enum; surrounding zones have a task sibling.
- **INV-14 — Surrounding ratio compliance (HIGH)**: surrounding-zone target
  ≥ ⅓ task-zone target per BS EN 12464-1:2021 §4.2.2.2 (Table 4.2).
- **INV-15 — Background floor (HIGH)**: background-zone target ≥ ⅓
  surrounding-zone target per §4.2.2.3; if no surrounding zone then ≥ ⅓ of
  lowest task zone.
- **INV-16 — mount_type ↔ z_mm/suspension consistency (HIGH)**: pendant and
  suspended luminaires carry both `z_mm` and `suspension_length_mm`; surface
  and recessed never carry `suspension_length_mm`.
- **INV-17 — Ceiling clearance + working-plane floor (HIGH)**: `z_mm` ≤
  `room.ceiling_height_mm`; for pendant/suspended `z_mm` ≥ `working_plane_mm`
  + 2000 mm (2 m headroom clearance).
- **INV-18 — hm_mm derivation consistency (MEDIUM)**: when `z_mm` present,
  `luminaire.hm_mm` (mounting height above working plane) = `z_mm −
  working_plane_mm` ± 5 mm tolerance.
- **INV-19 — Per-zone achievement (graded severity, INFO/MEDIUM/HIGH)**:
  graded per band — `gap_pct < 5 %` → INFO; `5–15 %` → MEDIUM; `> 15 %` →
  HIGH; aggregate FAIL if any zone is `fail`.

### Added (reviewer — `prompts/reviewer.md`)
- **D-11 — Suspension length sanity check**: pendant suspension_length_mm
  should be < (ceiling_height_mm − 2100); flag where clearance < 200 mm.
- **D-12 — Background-only rooms flag**: rooms containing only background
  zones with no task zone are unusual; reviewer notes for engineer sign-off.
- **D-13 — Task-zone density flag**: task zones covering < 20 % of total room
  area trigger a reviewer comment on whether coverage intent is met.

### Added (rules)
- `rules/zone-purpose-rules.yaml` — zone-purpose hierarchy rules, ratio
  thresholds, and enforcement mapping to INV-13/14/15.
- `rules/mount-type-rules.yaml` — 3D placement rules, mount_type enum
  definitions, suspension geometry constraints, and enforcement mapping to
  INV-16/17/18.

### Added (verified standards file)
- `shared/standards/lighting/BSEN12464/area-definitions.json` —
  machine-readable transcription of BS EN 12464-1:2021 §4.2.2.1/2/3 and
  Table 6 area-type/purpose definitions. Joins existing `lux-levels.json`.

### Added (examples — 8 retrofit + 4 new = 12 total)
Retrofit (zone-purpose + mount_type fields backfilled):
- `office-open-plan` — zones purpose + mount_type surface
- `reception-lobby` — zones purpose + mount_type surface/wall
- `warehouse-highbay` — zones purpose + mount_type pole
- `uk-open-plan-office-10x8-dali` — zones purpose + mount_type recessed
- `uk-mixed-purpose-classroom` — zones purpose + task/surrounding split
- `uk-multi-entrance-classroom` — zones purpose + mount_type surface
- `uk-part-l-fail-incandescent` — zones purpose backfill
- `uk-bathroom-zone-1-zone-2` — zones purpose + mount_type surface/wall

New (exercise new D5 features):
- `uk-pendant-open-plan-office` — pendant luminaires (z_mm + suspension),
  INV-16/17/18 PASS path, per_zone_achieved populated via photometric cascade.
- `uk-retail-display-task-zone` — task/surrounding split across retail floor
  and display bay; INV-14 ratio enforcement.
- `uk-per-zone-target-violation` — INV-19 FAIL path with graded HIGH gap
  demonstrating non_compliance_flags severity bands.
- `uk-undersized-lighting-vs-target` — photometric cascade path demonstrating
  INV-19 MEDIUM band (gap 5–15 %).

### Added (evals — 5 new)
- `eval-09-zone-purpose-emit.yaml` — INV-13 PASS: valid zone purposes emitted.
- `eval-10-task-surrounding-ratio.yaml` — INV-14 PASS/FAIL: surrounding ≥ ⅓
  task enforcement.
- `eval-11-mount-type-3d-consistency.yaml` — INV-16 PASS: pendant fields
  present; INV-17 clearance.
- `eval-12-per-zone-achievement-pass.yaml` — INV-19 PASS: all zones meet
  target within tolerance.
- `eval-13-per-zone-achievement-fail.yaml` — INV-19 FAIL: HIGH band triggered
  on > 15 % gap zone.

### Changed (inputs.json)
- Items 16–19 added covering zone-purpose interview questions:
  - WI-16: Is task lighting required in specific sub-zones?
  - WI-17: Confirm surrounding-zone area boundary.
  - WI-18: Pendant/suspended luminaire mounting height or suspension length.
  - WI-19: Per-zone lux target confirmation from photometric report.

## [1.6.0] - 2026-06-02 — Wave 1: special-locations cascade contract + Floor plan context portability

_Two parallel-shipped deliverables merged into a single version entry. The Wave 1 special-locations cascade contract (the main deliverable) is documented first; the Floor plan context portability changes (originally landed as PR #2 / commit 013861b) are appended below._


### Changed
- `skill.manifest.json` version 1.5.0 → 1.6.0 (additive; backward-compatible IR additions).
- `consumes_intents[]` extended with `special-locations-zoning` cascade entry
  (trigger: any room in `rooms[].room_type` matches the Part-7 set —
  bathroom / shower_room / swimming_pool_hall / sauna / medical_group_0_area /
  medical_group_1_ward / medical_group_2_theatre / external_landscape).
  Second downstream-cascade consumer for this skill (joins photometric-grid).

### Added (IR schema — `shared/schemas/electrical/lighting-layout-ir.schema.json`)
- 3rd `allOf` clause: when any `rooms[].room_type` matches the Part-7 set,
  `consumed_intents.special_locations_zoning` MUST be populated. Structural
  enforcement; semantic content enforced by INV-12.
- `consumed_intents.special_locations_zoning` sub-object with `intent_version`
  + `source_path` + `payload` via `$ref` to the special-locations zoning
  intent schema.

### Added (validator)
- **INV-12 — Special-locations zoning cascade resolved (HIGH)**. 4 sub-checks:
  (1) cascade structural presence; (2) payload counts reconcile with
  `payload.zones[]` + `payload.electrical_constraints[]`; (3) luminaire-by-zone
  IP/voltage gating per `payload.zones[].ip_rating_min` +
  `max_voltage_v` + `prohibited_fixture_types`; (4) negative coverage for
  non-applicable Part-7 sub-rules (pool/medical/sauna distinguishers).
- Evidence cap consistent with shared-schema cap (1200 chars) — no schema
  change needed; the shared schema already allowed 1200.

### Added (examples)
- **NEW `examples/uk-bathroom-zone-1-zone-2/`**: UK 2700 × 2100 mm bathroom
  fixture; 3 IPx4 downlights + extract fan + Zone 2 mirror lamp. Carries
  the cascaded `payload` and demonstrates INV-12 PASS on a typical
  domestic § 701 install. Shared fixture with `small-power/uk-bathroom-shaver-and-zone2-sockets`
  and `db-layout/uk-bathroom-rcd-distribution` — same room, same payload,
  three IRs cooperating.

### Honest disclosures preserved
- Cascade is read-only for the lighting consumer: the `payload` is inlined
  for reproducibility on this golden example, but in a real DraftsMan run
  the runtime resolves the `source_path` at execution time and reads the
  upstream `special-locations` intent fresh.
### Floor plan context portability (PR #2)

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
