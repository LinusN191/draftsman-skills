# Changelog — earthing

## [1.4.1] - 2026-05-25 — C.1 / M2 genuine TT example

### Added
- **M2**: genuine TT example authored at `examples/intl-rural-tt/` — completes
  the Sprint A.1 cause-fix (the previously misnamed folder was renamed to
  `intl-rural-tncs/`; the genuine TT case was untested). Rural off-grid
  single-storey cottage at Ze=Ra=200 Ω on a single 3 m driven rod, four final
  circuits (lighting + 3 socket circuits) each with 30 mA RCD per
  IEC 60364-4-41 §411.5. Disconnection condition §411.5.3: Ra·IΔn = 200 × 0.030
  = 6.0 V ≤ 50 V passes with ~8× margin. RCD type per §531.3.3: Type AC on
  lighting, Type A on socket-outlet circuits.
- Five validator INVs populated in `ir.invariants[]`: INV-02 (electrode
  jurisdiction-system match), INV-04 (CPC sizing method per jurisdiction),
  **INV-06 (RCD requirement) — now fires PASS on a real example for the
  first time**; the safest earthing branch was previously untested. Plus
  INV-09 (tool deferral shape) and INV-10 (no cross-contamination KE↔INT
  citation form).

### Changed
- `evals/eval-02-rural-tt-system.yaml` re-pointed from inline GB rural-TT
  input to `input_fixture: electrical/earthing/examples/intl-rural-tt/input.json`
  (Option (a) per Sprint C.1 plan — single canonical TT eval consuming the
  canonical TT example). Two assertion updates to match the new fixture:
  `ir.earthing_system.system_type` path (was `ir.earthing_system`, but the
  schema is a nested object); `ra_ohm_specified <= 1666` (the §411.5.3
  disconnection ceiling at 30 mA, replacing the prior `<= 100`); citation
  regex switched to IEC 60364-4-41:2017 §411.5 (was BS 7671:2018+A3 Reg 411.5.3).
- Examples count: 5 → 6.

### Why this sprint
Reviewer 1 / DEFECT_REGISTER M2 closed. The Sprint A.1 fix renamed the
misnamed folder but left the TT slot empty, so the safest earthing branch
(TT + RCD on every circuit per §411.5) had thorough prompt logic but no
example exercising it. Sprint C.1 / M2 closes the gap with an off-grid
cottage example demonstrating: TT mandate by site context (no PEN bond),
high-Ra electrode design, OCPD-path-fails / RCD-path-succeeds Zs strategy,
§411.5.3 disconnection-condition hand-check, §531.3.3 RCD type selection.

### Verification
- `validate-examples.py`: 164/164 (was 163/163). New example adds 1.
- `functional_audit.py`: 6 findings held (no new findings; M2 has no direct
  audit signature, but the cause-fix is closed in the example fabric).

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

## [1.4.0] - 2026-05-18

### Added
- New example: `uk-commercial-3storey` — UK 3-storey commercial office TN-C-S, 4-board cascade
  - Ze=0.35Ω, MET in ground-floor plant room
  - 24 circuits (3 MCCB-D 100A feeders + 21 MCB-B final circuits)
  - 15 circuits RCD-protected per BS 7671:2018+A2 §411.3.3 AMD 2 (sockets ≤32A + mobile equipment outdoors)
  - 5 main bonding entries (water + gas + structural steel × 3 floors per §411.3.1.2)
  - Type 2 SPD per §443 (commercial moderate lightning)
  - Consumes 4 db-layout intents (one per board) per WI4 cascade pattern

### Changed
- Examples count: 4 → 5

### Why this sprint
Pairs with SLD v1.4 multi-skill intent consumption sprint. SLD UK example consumes this earthing intent to verify `supply_origin.system_type` cross-skill consistency (INV-11). Also pairs with fault-level uk-commercial-3storey for cross-skill Ze + system_type alignment.

### Pattern parent
- earthing v1.3 (shipped 2026-05-18) — single-board WI4 consumption; v1.4 adds commercial multi-board scenario without changing the consumption pattern

## [1.3.0] - 2026-05-18

### Added
- **Cross-skill intent consumption demonstrated end-to-end** across all 4 worked examples (KE, UK, INT, US). Each `input.json` now carries `consumed_intent_path` referencing a paired `db-layout/examples/<X>/intent-out.json`. Each `output.json` populates `meta.consumed_intents[]` with the db-layout provenance.
- **Generator prompt Step 0.5** (Resolve upstream intents) — instructs LLM to adopt upstream circuits[] verbatim (circuit_id, breaker_rating, breaker_curve, voltage_class, route_length) and add earthing-specific fields per circuit.
- **eval-09-db-layout-intent-consumption.yaml** — 10 assertions verifying cross-file circuit_id consistency + field-level alignment across all 4 example pairs.
- **ARCHITECTURE.md "Worked example pattern" subsection** under Cross-drawing intents — documents the 4 pairs + generalization for future consumer skills.

### Changed
- **All 4 earthing example output.json files refreshed** — circuits[] realigned to upstream db-layout circuit_ids. `meta.skill_version` bumped to `earthing/1.3.0`. Earthing-specific fields (CPC, Zs, RCD) preserved from v1.2.
- **INT example re-anchored** — previously modeled rural TT installation (3 LV circuits + electrode array); v1.3 re-anchors to commercial TPN MSB scenario (4 feeders F01-F04) to align with the paired db-layout intent. Rural TT remains a valid engineering scenario but is no longer represented by this example.
- **db-layout dependency bumped** — produced_by string carries `electrical/db-layout/v1.1.0` (the paired skill version released in the same sprint).

### Notes
- No schema changes — `meta.consumed_intents[]` was already supported in the earthing IR schema; this sprint simply populates it.
- `intent_version: 1.0.0` is the intent **schema** version (not bumped this sprint since the db-layout intent contract is unchanged); `produced_by` carries the **skill** version (1.1.0 for db-layout post-sprint).
- Future consumer skills (cable-sizing, fault-level, arc-flash) will follow this pattern in their respective minor-version sprints.

## [1.2.0] - 2026-05-18

### Added
- **KS 1700:2018 standalone standards layer** at `shared/standards/electrical/KS1700/` (28 files at parity with BS7671/). KS 1700 becomes a first-class standards body in this repo alongside BS 7671 / IEC 60364 / NFPA 70.
- **Two KS-unique files**: `KS1700/annex-E-bs7671-adoption-table.json` (clause-by-clause KS↔BS adoption map with 31 rows) and `KS1700/ks-unique-deviations.json` (6-deviation index — socket-RCD universality, climate ambient, EV §722 absence, coastal IP65, KEBS certification, EPRA inspection regime).
- **`local-codes/Kenya/` refresh** — rewrite from 1-line stub to country-context content (README + country-meta.json + adoption-pathway.md).
- **`ROADMAP.md`** — KS 1700 row added to standards layer table.
- **Validator INV-10** — KE example code_clause fields MUST start with `"KS 1700:"` (or `"IEC 60364"` for Annex E routing).
- **Eval-08-ks1700-citation-consistency.yaml** — 10 assertions verifying the citation refactor.

### Changed
- **Generator prompt** — KE jurisdiction routing updated: KS 1700 as primary standards source (with IEC 60364 fallback for clauses KS Annex E §VIII routes to IEC). Citation form `"KS 1700:2018 §X.Y.Z"` replaces `"BS 7671:... (adopted by KS 1700)"`. The v1.1 annotation pattern is now BANNED.
- **Validator prompt** — INV-10 enforces direct KS citation form.
- **KE example output.json** — every `code_clause` + `cpc_sizing_clause` refactored to direct KS 1700 form. KS deviation citations (§411.3.3) note the deviation explicitly.
- **KE example reasoning.md** — "KS 1700 vs BS 7671" subsection shortened; points at canonical KS1700/ks-unique-deviations.json + KS1700/annex-E-bs7671-adoption-table.json.
- **KE example sample-schedule.md** — footer + Notes citations switched to direct KS form.
- **KE example input.json** — standards_stack restructured (primary + annex_e_adoption_pathway + iec_routing + ks_unique_deviations).
- **Manifest version** 1.1.0 → 1.2.0; standards array gains 8 KS1700/ entries.

### Notes
- KS 1700:2018 PDF is not in repo at the time of authoring. Every KS1700/ file is marked `verification_status: "draft-from-bs7671-derivative-needs-source-verification"`. Engineering content is structurally correct; precise clause numbering and KS-specific tolerance values should be verified against the official KEBS publication before downstream skills rely on tight tolerances. A future micro-sprint will promote verification status.
- Existing 3 examples (UK / INT / US) unchanged — they don't carry KE jurisdiction.
- IR schema unchanged (KS 1700 layer is consumed at generation time; no schema break).
- Template for future African codes: NIS 197 (Nigeria), SANS 10142 (South Africa) — each becomes a future sprint following this v1.2 pattern.

## [1.1.0] - 2026-05-18

### Added
- **`calc.zs_loop_impedance` calc contract** (`shared/calculations/electrical/zs-loop-impedance.json`) — WI3-deferred tool for deterministic Zs verification. Jurisdiction-branching: GB/KE/EU/INT use IEC 60364-5-52 Annex B + BS 7671 Table 41.2; US uses NFPA70 Chapter 9 + NEC 5×In trip-current derivation.
- **`tool_call_pending_for_zs` + `zs_calc_tool_input`** root fields in `earthing-ir.schema.json` — replay payload captured at generation time for deterministic tool execution.
- **`KE` jurisdiction enum value** — Kenya (KS 1700:2018). Routes through BS 7671 Table 41.2 via KS 1700 Annex E.
- **KE Nairobi industrial TN-S worked example** (`examples/ke-nairobi-industrial-tn-s/`) — 8 circuits including Type D compressor and 60m submain. Exercises TN-S vs TN-C-S Ze split, KS 1700 socket-RCD policy, WI3 tool deferral. 5 files: input.json, output.json, intent-out.json, reasoning.md, sample-schedule.md.
- **`intent-out.json` backfill** for existing UK TN-C-S, INT TT, US NEC examples — brings them to feature parity with the KE example and sibling skills (cable-sizing, fault-level, arc-flash, arc-flash-labelling).
- **`validation/tool-deferral-shape.yaml`** — 2 critical checks for tool_call_pending ↔ flags pair consistency.
- **`eval-07-ke-tn-s-tool-deferral.yaml`** — 15 assertions verifying the KE example output.
- **Generator Step 9.5** — Build `zs_calc_tool_input` payload before inline Zs estimation.
- **Validator INV-09** — Enforce tool_call_pending shape consistency.

### Changed
- **Generator Step 10 reshaped** — Inline Zs estimation now sets `tool_call_pending_for_zs: true` and appends TOOL-CALL-PENDING string to top-level `flags`.
- **All 3 existing examples retrofit** — UK TN-C-S, INT TT, US NEC outputs now carry `tool_call_pending_for_zs: true` + `zs_calc_tool_input` replay payload + TOOL-CALL-PENDING string in flags. Zs numerical values unchanged from v1.0.0 (deterministic tool will refine when runtime ships).

### Notes
- Schema is backward-compatible — v1.0.0 outputs remain valid against v1.1 schema (new fields are optional).
- KS 1700 references cited as "BS 7671:2018+A2 Reg X.Y.Z (adopted by KS 1700)" to make adoption explicit.

## v1.0.0 (current — Stage 1 Schematic)

First production-grade version. Stage 1 of a three-stage plan:
- **Stage 1 (this release):** Earthing single-line schematic IR. Covers TN-C-S + TT systems across GB / EU/INT / US jurisdictions.
- **Stage 2 (planned):** Plan-view earthing layout with site/building electrode positions and bonding routes.
- **Stage 3 (planned):** Declaration-only mode for retrofit / forensic / audit use cases.

### Features
- 12-step reasoning chain in `prompts/generator.md` that explicitly names standards files to load (consumption-pattern proof)
- Jurisdiction-gated standards loading: BS 7671 (GB) / IEC 60364 (EU/INT) / NFPA 70 (US) + IEC 60617 always
- IR schema with `tool_call_pending` flag for iterative electrode-resistance calcs (per WI3 — Python tool in runtime not yet implemented)
- Stable intent schema for downstream consumers (cable-containment, riser, schematic, panel-schedule, sld)
- Cross-drawing intent consumption: db-layout + lighting-layout + small-power
- Rationale block per WI2 (8 mandatory sections)
- 6 evals covering all WI5 categories (happy_path, edge_case ×2, compliance_failure, cross_validation, skill_specific)
- 3 worked examples (UK / international / US) demonstrating jurisdiction switch

### Standards consumed (explicit file paths — not folders)
- `shared/standards/electrical/BS7671/reg411-disconnection-times.json` (Zs verification — GB)
- `shared/standards/electrical/BS7671/reg411-rcd-requirements.json` (RCD requirements — GB)
- `shared/standards/electrical/IEC60364/part4-41-electric-shock.json` (electric shock protection — EU/INT)
- `shared/standards/electrical/IEC60364/part5-54-earthing.json` (earthing arrangements — EU/INT)
- `shared/standards/electrical/NFPA70/art250-grounding-bonding.json` (grounding & bonding — US)
- `shared/standards/electrical/NFPA70/grounding-and-bonding.json` (cross-cutting topic — US)
- `shared/standards/electrical/IEC60617/symbol-index.json` (always; lightweight)
- `shared/standards/electrical/IEC60617/part2-general.json` (always; earth symbols)
- `shared/calculations/electrical/electrode-resistance.json` (declared tool-call — runtime tool not yet implemented)
- `shared/calculations/electrical/cpc-adiabatic.json` (declared tool-call — runtime tool not yet implemented)

### Status
- `status: beta` — production-grade artefact set but flagged for runtime tool dependencies (electrode-resistance + cpc-adiabatic calls operate declaratively with `tool_call_pending: true` until Python tools land in DraftsMan runtime)
- Promotes to `production` when: tool calls execute live AND 6/6 evals pass against a production model (sonnet-or-better)
