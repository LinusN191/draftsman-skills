# Changelog — earthing

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
