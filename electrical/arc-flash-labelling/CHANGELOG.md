# Changelog — electrical/arc-flash-labelling

All notable changes. Follows [Keep a Changelog](https://keepachangelog.com).

## [1.1.0] - 2026-06-01 — Floor plan context portability

### Changed
- Replaced previous Sprint 4-AB `architectural_state` section in
  `prompts/{generator,reviewer,validator}.md` with the generic
  `## Floor plan context` contract. Prompt is now portable across AI
  runtimes that inject room-list markdown under that heading.
- Inlined the contract per-file; deleted the previous
  `shared/architectural_state_contract.md` dependency.

### Added (IR schema — `schemas/labels-ir.schema.json`)
- NEW optional top-level `floor_plan_context_consumed: boolean`
  (default `false`). IR sets `true` when the prompt context included
  a `## Floor plan context` block.

## [1.0.2] - 2026-05-25 — M4 non-provisional provenance worked example

### Added
- New worked example `examples/uk-bs5499-final-with-provenance/` exercising
  the NON-PROVISIONAL label branch (DEFECT_REGISTER M4: high-consequence
  branch had no example coverage). Consumes the refreshed
  `electrical/arc-flash/examples/uk-lv-switchgear/intent-out.json` and emits
  BS 5499-4:2013 + BS EN ISO 7010 labels with `provenance.is_provisional =
  false`, DRAFT marker SUPPRESSED on `header_line`, and QR codes populated.
- Provenance block fully populated per Sprint A.2 C2 cause-fix schema:
  `method_applied = ieee_1584_2018`, `computed_at`, `calc_tool_version`,
  `is_provisional = false`, `provenance_note` explaining Sprint A.3
  verification rationale (IEEE 1584-2018 600V VCB coefficients now
  transcribed; upstream Lee 1982 fallback no longer in play).
- INVs populated in `invariants[]`: INV-01 (node_id uniqueness), INV-04
  (PPE Cat ↔ signal_word), INV-05 (NFPA 70E §130.5(H) content fields),
  INV-06 (SVG content + no template placeholders), INV-08 (intent shape +
  1-to-1 with IR), INV-09 (provenance block + DRAFT marker suppression).

### Rationale
Sprint C Task C.3 — closes M4 (untested safety branches). Counterpart to
the existing `uk-bs5499-label-set` example which exercises the provisional
/ DRAFT branch. Together the two examples demonstrate that the C2
provenance disclosure mechanism is a genuine decision gate — the SAME
upstream cascade produces DIFFERENT label output depending on
`is_provisional` state. Non-provisional labels are approved for
OPERATIONAL FIELD USE (print + laminate + affix).

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

### Added — v1.0.0 beta (unified Phase A + B sprint)

**Phase A — standards layers shipped alongside:**
- `shared/standards/electrical/ANSI-Z535-4/` promoted stub → production (11 files)
- `shared/standards/electrical/ISO-7010/` NEW layer (6 files)
- `shared/standards/electrical/BS-5499/` NEW layer (4 files)

**Phase B — the skill:**
- 12-step generator chain (`prompts/generator.md`)
- Labels IR + slim labels intent (`schemas/`)
- 4 rules: jurisdiction-format-selection, signal-word-policy, label-content-population, ppe-clothing-description
- 3 constraints: required-content-present, colour-spec-compliance, letter-height-legibility
- 3 validation YAMLs (9 deterministic checks)
- 2 ontology files: label-formats (4 entries) + signal-words (5 entries)
- 4 SVG templates: ansi-z535-4 / iso-7010 / bs-5499 / restricted
- 8 evals (5 WI5 categories + 3 skill-specific)
- 3 worked examples (US ANSI / UK BS-5499 / INT ISO-7010)

**New calc contract:**
- `calc.render_label` at `shared/calculations/electrical/render-label.json` (SVG → PDF/PNG, deferred per WI3)

### Consumes intents
- `arc-flash` (per-equipment IE / AFB / PPE / shock-approach / label_recommended)

### Produces intent
- `labels` (per-equipment label metadata; consumed by facility-management / digital-twin systems)

### Renderings
- SVG inline (LLM-produced from template; engineers preview in browser)
- PDF / PNG / project-label-index PDF deferred to `calc.render_label` runtime tool per WI3

### Method scope
- ANSI Z535.4 (US default)
- ISO 7010 (EU/INT default)
- BS 5499 (GB default)
- RESTRICTED format (IE > 40 cal/cm² — safety override; supersedes jurisdiction)
