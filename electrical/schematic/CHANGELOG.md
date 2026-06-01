# Schematic Skill — Changelog

## [1.1.0] - 2026-06-01 — Add floor plan context support

### Added
- `## Floor plan context` section added to
  `prompts/{generator,reviewer,validator}.md`. This skill was missed
  in the Sprint 4-AB pass. Prompt is portable across AI runtimes
  that inject room-list markdown under the `## Floor plan context`
  heading.
- NEW optional top-level `floor_plan_context_consumed: boolean`
  (default `false`) added to `schemas/schematic-ir.schema.json`.
  IR sets `true` when the prompt context included a
  `## Floor plan context` block.

## [1.0.1] - 2026-05-25 — M1 hybrid eval-vs-IR fix

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

## v1.0.0 — 2026-05-22

Initial release. Control + protection schematics with hybrid consumer pattern.

### Added
- Per-schematic IR (one schematic = one IR document)
- 7-value `schematic_type` enum with oneOf branching (control_motor_starter / control_changeover / control_sequence / protection_overcurrent / protection_differential / protection_motor / protection_busbar)
- 40 BS EN 60617 symbols (motor starter + protection + auxiliary + control logic)
- 8 jurisdictional examples: 4 control (KE/UK/INT/US) + 4 protection (KE/UK/INT/US)
- Hybrid consumer of `db-layout-rollup` + `fault-level` + `earthing` intents with leaf-mode fallback
- Terminal `schematic` intent emission for future tender-report / om-manual consumption

### Standards
- BS 7671:2018+A2:2022, BS EN 60617, BS EN 61082, BS EN 61009-1:2012+A12:2014 (UK)
- KS 1700:2018 routing to BS 7671 via §313 + IEC 60617 + IEC 60255 (KE)
- IEC 60364-X-XX + IEC 60617 + IEC 60255 + IEC 61850 (INT)
- NEC 2023 / NFPA 70 + IEEE Std 315 + IEEE C37.x (US)

### Lessons applied from Sprint 3-W2c
- Single-frame voltage references (no dual-frame % collision)
- No fabricated standard publication years
- Canonical enums (`main_switch_fused`, `§ 311.1`)
- Africa-first KE jurisdiction first-class
