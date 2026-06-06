# DraftsMan Skills — Claude Code Context

## What this repo is

Open-source MEP engineering skills for AI agents.

Each skill teaches Claude to reason like a senior building services engineer before producing output. Output is structured IR (intermediate representation) consumed by the DraftsMan runtime — not direct CAD or drawing files. The runtime owns rendering, calc execution, project graph, and the eval harness; this repo ships contracts only.

## Repo shape

- `electrical/`, `mechanical/`, `plumbing/`, `fire-protection/` — discipline folders, one skill per subfolder.
- `documents/` — document-output skills (BOQ, tender report, method statement, etc.), one skill per subfolder.
- `coordination/` — multi-discipline coordination skills (clash detection, IFC export, 3D routing, etc.), one skill per subfolder.
- `shared/schemas/core/` — cross-skill metaschemas: `intent.schema.json`, `eval.schema.json`, `inputs.schema.json`, `rationale.schema.json`, plus `calculation.schema.json` and the `standards-*` trio.
- `shared/standards/`, `shared/symbols/`, `shared/calculations/`, `shared/ontology/`, `shared/units/`, `shared/validation/`, `shared/drafting/` — reference content reused across skills.
- `docs/superpowers/specs/` — design specs (brainstorm output).
- `docs/superpowers/plans/` — implementation plans (writing-plans output).
- `scripts/` — golden CI harness (`validate-examples.py`) and helpers.
- `.github/workflows/` — CI gates (`validate-examples.yml`).

Per-skill folder (use `electrical/lighting-layout/` as the reference shape):
- `README.md` — the skill body (YAML frontmatter + engineering content).
- `CHANGELOG.md` — version log.
- `skill.manifest.json` — manifest declaring id, version, produced intents, consumed intents.
- `inputs.json` — WI1 interview taxonomy (validated by the inputs metaschema).
- `prompts/generator.md`, `prompts/validator.md`, `prompts/reviewer.md` — the three-stage prompt chain.
- `schemas/<skill>-ir.schema.json` and `schemas/<skill>-intent.schema.json` — output and cross-drawing intent contracts.
- `evals/eval-NN-*.yaml` — per-skill evaluations (≥5 required).
- `examples/<scenario>/input.json + output.json + reasoning.md` — worked examples (≥3 required).
- `rules/`, `constraints/`, `ontology/`, `validation/`, `docs/` — supporting reference content.
- `assets/` (where applicable) — reference tables (photometric data, standards values).
- `calculations/` (where applicable) — skill-specific calc declarations.
- `annotations/` (where applicable) — annotation tags (e.g. drawing layer mapping).
- `templates/` (where applicable) — output templates (e.g. SVG label templates).

## Core schemas (shared/schemas/core/)

- `intent.schema.json` — cross-drawing intent envelope. Every skill that declares `produces_intent` emits a payload wrapped in this envelope so consumer skills can read it from sibling chats.
- `eval.schema.json` — eval YAML metaschema. Requires `[name, skill, checks]`; enforces the 9-value category enum; accepts `input` / `input_fixture` / `input_fixtures` via `oneOf`; `Check` supports `matches_inv` and `matches_nec`.
- `inputs.schema.json` — per-skill inputs.json metaschema; accepts canonical WI1 `items[]` (5 skills), legacy `inputs[]` (arc-flash family), or grouped `input_groups[]` (cable-sizing + small-power) at top level via oneOf.
- `rationale.schema.json` — embedded rationale block. `chat_summary` (40–500 chars) plus `sections[]` (each ≥1 with `title` + `summary` up to 800 chars, optional `decisions[]`).

## Sprint workflow

The established workflow. The `superpowers:*` skills are loaded on demand — do not duplicate their content here.

1. **Brainstorm.** Invoke `superpowers:brainstorming`. Output: `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`. User reviews and approves before planning.
2. **Plan.** Invoke `superpowers:writing-plans`. Output: `docs/superpowers/plans/YYYY-MM-DD-<feature>-sprint.md`. Plans carry full content per step — no placeholders.
3. **Execute.** Invoke `superpowers:subagent-driven-development`. Fresh subagent per task. Two-stage review after each task: spec compliance, then code quality.
4. **Memory save.** On ship, save a `sprint-<id>-shipped.md` entry under the user's auto-memory directory recording what shipped and what is deferred.

## Model selection rules

- **Sonnet** — mechanical tasks: key renames, schema edits, prompt tweaks, file scaffolding.
- **Opus** — judgment-heavy tasks: engineering content authoring, structural conversions, reviews, design judgment calls.
- **Never Haiku.** Enforced across all sprints. See `[[feedback-no-haiku-sonnet-opus-only]]`.

## Golden CI gate

`scripts/validate-examples.py` runs on every push and PR to `main`. **6 passes + 1 lint sub-pass** (extended in Sprint X from the original 3-pass; Sprint F.5 will extend further to 7-pass + 5 lint when resumed):

- **Pass 1** — every `examples/*/output.json` validated against the parent skill's `schemas/<skill>-ir.schema.json`.
- **Pass 2** — every `evals/eval-*.yaml` validated against `shared/schemas/core/eval.schema.json`.
- **Pass 3** — each skill's `inputs.json` validated against `shared/schemas/core/inputs.schema.json`.
- **Pass 4** — `shared/standards/spaces/ashrae/ashrae-90.1-table-9.5.2.1-lpd.json` schema validation (added Sprint X).
- **Pass 5** — `shared/standards/spaces/ashrae/ashrae-62.1-table-6-1-ventilation.json` schema validation (added Sprint X).
- **Pass 6** — `shared/standards/spaces/ifc/` subset file schema validation (added Sprint X).
- **Lint 1** — room-type `snake_case` pattern conformance across room-types catalogue entries (added Sprint X).

Aggregate exit 0 only when all passes and lint sub-passes are 100% green. Sprint 3-W2 (W/W2a/W2b) cleared the schema-fragmentation backlog; Sprint X extended the gate to cover the room-types taxonomy and IFC subset. Any new skill PR must add new evals and `inputs.json` and pass all passes.

Workflow: `.github/workflows/validate-examples.yml`. Local run: `python3 scripts/validate-examples.py`.

## Build status

Strategy: breadth-first — finish every skill across disciplines before scaling standards across more jurisdictions. See `[[build-strategy-breadth-first]]`.

**Drawings (6/8 shipped):** lighting-layout, sld, db-layout, earthing, small-power, schematic. Remaining: cable-containment, riser.

**Calculations (3/7 shipped):** cable-sizing, fault-level, arc-flash. Remaining: lux, load-schedule, voltage-drop, generator-sizing.

**Document skills (0/8 outstanding):** tender-report, bq, method-statement, cable-schedule, specification, om-manual, design-statement, cdm-designer-risk-register (all live under `documents/`, NOT `electrical/`).

**Other shipped:** arc-flash-labelling (companion to arc-flash).

**Sprint D follow-up — scope-coverage stubs added 2026-05-25 (19 new stubs across 8 truly-unscoped domains identified by Reviewer 1):**
- `fire-protection/` (3 new — passive fire): fire-stopping, compartmentation, fire-damper-schedule
- `commissioning/` (3 new, NEW DISCIPLINE): inspection-test-certificate, commissioning-plan, witness-testing-record
- `compliance/` (4 new, NEW DISCIPLINE): energy-statement, carbon-assessment, breeam-leed-assessment, **integrated-design-review** (the cross-discipline whole-package sign-off — the most consequential unscoped domain per Reviewer 1)
- `electrical/` (3 new): ev-charging, battery-storage, protection-coordination
- `mechanical/` (3 new): heat-pump, lifts, acoustics
- `plumbing/` (2 new): medical-gas, legionella-risk
- `documents/` (1 new): cdm-designer-risk-register

**Post-Sprint-D within-skill-depth stubs added 2026-05-25 (9 new stubs from the production-readiness audit; depth specialisms that compose with parent beta skills via intent):**
- `electrical/` (6 new): electrode-design (consumed by earthing), photometric-analysis (UGR + uniformity + point-grid; consumed by lighting-layout), lighting-controls (DALI/KNX zoning + sensors), spd-coordination (BS 7671 §443 + IEC 61643; interfaces with lightning-protection), load-flow (steady-state power flow distinct from fault-level transient), control-sequence-design (relay/PLC logic adjacent to schematic)
- `documents/` (3 new): bonding-schedule (consumed-from-earthing deliverable), energised-work-permit (HSE permit from arc-flash intent), accessory-schedule (consumed-from-small-power deliverable)

Manifest tally: **104 total** = 13 shipped (9 beta + 4 production: lighting-layout v1.7.0 + photometric-analysis v1.1.0 + special-locations v1.0.1 + small-power v2.0.0) + 91 stubs. Tally last updated 2026-06-05 after lighting-layout v1.7.0 ship (Wave 2 second deliverable; task/ambient zone-purpose + 3D placement).

All other `electrical/<skill>/` folders are scaffolds — README + manifest + evals only, awaiting `inputs.json` and `schemas/` to be considered shipped.

## Standards to apply

- **GB** — BS 7671:2018+A2:2022 (electrical primary); BS EN 12464-1:2021 (lighting); BS EN 60617 (symbols); BS 1192 / ISO 19650 (drawing management); BS EN 61439 (switchgear); CIBSE Guides A, B, F, SLL; CDM Regulations 2015; NRM2.
- **KE** — KS 1700:2018 (electrical; routes to BS 7671 via §313 — Africa-first jurisdiction).
- **INT** — IEC 60364-X-XX (electrical, multi-part).
- **US** — NEC 2023 / NFPA 70.

## Citation form per jurisdiction

- **GB** — `BS 7671:2018+A2:2022 § 411.3.3` (regulation + section).
- **KE** — `KS 1700:2018 § 313 (route to BS 7671)` (cite the local norm and the British route it references).
- **INT** — `IEC 60364-4-41:2017 § 411.3.3` (part-subpart-section).
- **US** — `NEC 2023 Article 210.8` (or `NFPA 70 § 210.8`).

## Never do

- Never write a stub. Every shipped skill must include `README.md`, `skill.manifest.json`, `inputs.json`, `schemas/`, `prompts/`, ≥5 evals, ≥3 examples.
- Never skip evals. Every `evals/eval-*.yaml` must pass `shared/schemas/core/eval.schema.json`.
- Never skip examples. Every example's `output.json` must pass the parent skill's `schemas/<skill>-ir.schema.json`.
- Never invent standards values. Reference the clause number.
- Never use Haiku. Sonnet or Opus only.
- Never skip the golden CI gate. `python3 scripts/validate-examples.py` must pass before any PR is approved.
- Never invent calc tool names. Calc tools are reused across skills, not authored per skill — see existing tools under `shared/calculations/`.
- Never break the 9-value eval category enum without amending `eval.schema.json` first.

## Git commit format

```
feat: [skill-name] skill v1.0.0
chore: [description]
fix: [skill-name] [what was fixed]
```

For sprints: `feat(sprint-<id>): Phase X — <summary>` (e.g. `feat(sprint-<id>): Phase A schemas — ...`).
