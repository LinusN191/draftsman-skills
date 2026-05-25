# Changelog — lighting-layout

## [next-patch] - 2026-05-25 — M1 hybrid eval-vs-IR fix

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
