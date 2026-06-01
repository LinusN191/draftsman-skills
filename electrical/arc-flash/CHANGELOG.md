# Changelog — electrical/arc-flash

All notable changes to the arc-flash skill. Follows [Keep a Changelog](https://keepachangelog.com).

## [1.2.0] - 2026-06-01 — Floor plan context portability

### Changed
- Replaced previous Sprint 4-AB `architectural_state` section in
  `prompts/{generator,reviewer,validator}.md` with the generic
  `## Floor plan context` contract. Prompt is now portable across AI
  runtimes that inject room-list markdown under that heading.
- Inlined the contract per-file; deleted the previous
  `shared/architectural_state_contract.md` dependency.

### Added (IR schema — `schemas/arc-flash-ir.schema.json`)
- NEW optional top-level `floor_plan_context_consumed: boolean`
  (default `false`). IR sets `true` when the prompt context included
  a `## Floor plan context` block.

## [1.1.0] - 2026-05-25 — Sprint D1.4 equipment-condition + abnormal IE adjustment

### Added
- **Per-cascade-node `equipment_condition` block** per NFPA 70E §130.5(A):
  `{condition: normal|abnormal, justification (≥20c when abnormal),
  last_maintenance_date (ISO date when abnormal), ie_adjustment_factor
  (1.0 normal / 1.25 default abnormal / engineer-overrideable in
  [1.0, 2.0]), ie_adjustment_source (cited reference)}`.
- **Per-cascade-node `worker_position`** enum standing|kneeling|reaching.
- **IR-root `equipment_condition_basis`** carrying project-level defaults
  + the abnormal_ie_adjustment_factor_default (1.25) + cited industry
  source (ETAP/EasyPower — NOT NFPA 70E prescription).
- **Per-node `arc_flash.incident_energy_base_cal_per_cm2`** optional
  traceability field carrying the pre-adjustment IE so the multiplier
  arithmetic is auditable.
- **Per-node `checks.abnormal_condition_provisional_forced`** boolean
  recording that the INV-11 rule (is_provisional forced when condition is
  abnormal) has been honoured.
- **Validator INV-11** — abnormal-condition defensive posture. Asserts
  abnormal nodes carry justification + last_maintenance_date +
  ie_adjustment_factor >= 1.0 + cited source + provenance.is_provisional
  forced to true. Normal nodes have ie_adjustment_factor == 1.0.
- **Generator prompt Step 15** applying the 1.25× adjustment when abnormal,
  forcing is_provisional via Sprint C3 IR-level provenance + flagging
  the RESTRICTED branch when adjusted IE > 40 cal/cm².
- **Compliance flag `ABNORMAL_EQUIPMENT_CONDITION`** added to the
  non_compliance_flags enum for error-severity reporting when condition
  is abnormal at any node.
- **NEW example** `uk-abnormal-condition-water-damaged/` — basement
  plant-room LV panel with water-damaged busbar; base IE 5.2 cal/cm²
  (Lee 1982 fallback per Sprint A.3 600V coefficient pending) ×
  1.25 = 6.5 cal/cm² → PPE Cat 2 with is_provisional=true forced.
  Operational consequence: live-work prohibited pending remediation +
  re-assessment.
- 4 existing examples (uk-lv-switchgear, intl-mv-substation,
  us-pv-with-dcfc, intl-hv-restricted-substation) gain
  equipment_condition: normal + ie_adjustment_factor: 1.0 on every
  cascade node, and equipment_condition_basis at root. No IE change for
  normal nodes.

### Honest disclosure
- NFPA 70E §130.5(A) does NOT prescribe the abnormal-condition adder.
  The 1.25× default is industry consensus (ETAP Arc Flash Analysis App
  Note 2020 + EasyPower technical bulletin TB-AF-2019; 1.2–1.5× range).
  Engineer must validate against site assessment. ie_adjustment_source
  cites this on every node + at the project-level basis.
- The new example's base IE uses Lee 1982 fallback because IEEE
  1584-2018 600V coefficients carry _status: pending-transcription per
  Sprint A.3 IEEE Xplore paywall. Documented in provenance_note.

### Rationale
Sprint D1 Task D1.4 — closes the equipment-condition depth item inside
the arc-flash beta skill. Resolves NFPA 70E §130.5(A) requirement by
exposing the engineer's site-assessment finding as a first-class IR
field that defensively gates downstream label/permit consumers. The 1.25×
multiplier is sourced honestly (industry consensus, not NFPA
prescription) per the Sprint C3 honesty pattern + `[[feedback-no-trim-non-consequential]]`.

## [1.0.2] - 2026-05-25 — M4 RESTRICTED branch worked example

### Added
- New worked example `examples/intl-hv-restricted-substation/` exercising the
  IE > 40 cal/cm² RESTRICTED branch (DEFECT_REGISTER M4: high-consequence
  branch had no example coverage). 11 kV indoor metal-clad MV switchgear,
  HCB electrode configuration, 25 kA bolted fault, 0.5 s clearing time,
  910 mm working distance, 153 mm gap. IEEE 1584-2018 2700V model class
  coefficients applied per Sprint A.3 transcription — no Lee 1982 fallback.
- Computed results: I_arc ≈ 22.7 kA, IE ≈ 48.2 cal/cm², AFB ≈ 4275 mm.
  ppe_category = null (per validator.md INV-07: IE > 40 → null);
  INCIDENT_ENERGY_GT_40_RESTRICTED flag emitted at error severity;
  compliance_summary.compliant = false; live-work PROHIBITED per
  IEEE 1584-2018 §13.1 + NFPA 70E:2024 Table 130.7(C)(15)(A)(b).
- INVs populated in `invariants[]`: INV-04 (method vocabulary), INV-05
  (method matches fallback trail — single applied entry), INV-06 (numeric
  outputs gated by method), INV-07 (RESTRICTED branch encoding), INV-08
  (shock-approach block complete).

### Rationale
Sprint C Task C.3 — closes M4 (untested safety branches). Demonstrates the
upper-bound safety branch fires correctly: ppe_category null + RESTRICTED
flag + compliant=false + operational consequence (de-energise or remote
rack) documented in `assumptions[]`. Counterpart in arc-flash-labelling
exercises non-provisional provenance.

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

## [1.0.0-beta] — 2026-05-17

### Added — v1.0.0 beta (Phase B)
- 14-step generator chain (`prompts/generator.md`) — IEEE 1584:2018 + IEEE 1584:2002 + Lee 1982 + NFPA 70E table method + Doan/Stokes & Oppenlander for DC
- Project-scoped cascade IR (`schemas/arc-flash-ir.schema.json`) with method-fallback-trail per node
- Slim downstream `arc-flash` intent (`schemas/arc-flash-intent.schema.json`) — consumed by future `electrical/arc-flash-labelling` skill
- 5 rules: method-fallback-chain, electrode-config-inference, t-clear-defaults, ppe-category-mapping, label-required-equipment
- 4 constraints: incident-energy-finite, boundary-distance-physical, ppe-category-monotonic, method-fallback-consistency
- 4 validation YAMLs (12 deterministic checks)
- 2 ontology files: method-types (5 methods + pending), current-types (ac/dc with applicable methods)
- 9 evals (6 WI5 categories + 3 skill-specific)
- 3 worked examples: UK LV switchgear / INT MV substation / US PV+DCFC

### Phase A dependencies (already shipped)
- `shared/standards/electrical/IEEE1584/` (28 files, production)
- `shared/standards/electrical/NFPA70E/` (25 files, production)
- `shared/schemas/core/standards-{formula,table,section}.schema.json`
- `shared/validation/standards/*.py` (3 validation scripts)

### Tool calls awaiting runtime (WI3 deferral)
- `calc.arc_flash_incident_energy` (contract: `shared/calculations/electrical/arc-flash-incident-energy.json` — shipped this sprint)

### Consumes intents
- `fault-level` (per-node Ibf + ipk + X/R)
- `db-layout-rollup` (per-board equipment_type + ocpd_type + voltage)
- Engineer-declared fallback when intents absent

### Produces intent
- `arc-flash` — per-node IE + AFB + PPE + shock-approach + label_recommended; consumed by future `electrical/arc-flash-labelling` skill (stub committed 2026-05-17 at `electrical/arc-flash-labelling/`)

### Known limitations
- DC > 1000V not supported (utility PV 1500V systems deferred to v1.1)
- 17 IEEE 1584 coefficient files in Phase A standards layer are pending-verification; skill falls back gracefully to Lee 1982 or NFPA 70E table method until coefficients are transcribed
- Arc-flash label content generation is a separate future skill (arc-flash-labelling)
- Time-graded protection coordination is a separate future skill (refines t_clear precision)
