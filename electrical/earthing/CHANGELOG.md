# Changelog — earthing

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
- **Validator INV-9** — Enforce tool_call_pending shape consistency.

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
