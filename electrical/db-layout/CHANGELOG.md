# Changelog — db-layout

## [1.1.0] - 2026-05-18

### Added
- **NEW KE Nairobi industrial 100A TPN example** (`examples/ke-nairobi-industrial-100A-tpn/`) — 5 files: input.json, output.json, intent-out.json, reasoning.md, sample-schedule.md. 8 circuits matching the KE earthing example 1:1 for cross-skill consumption demonstration.
- **intent-out.json backfill for existing 3 examples** — uk-domestic-consumer-unit, intl-commercial-tpn-msb, us-strip-mall-panelboard. Brings all 4 db-layout examples to feature parity with arc-flash + arc-flash-labelling + earthing pattern.

### Notes
- intent-out.json schema field names differ from output.json IR field names (id vs circuit_id, breaker_rating_a vs ocpd.rating_a, etc.). The intent contract is at `electrical/db-layout/schemas/db-layout-intent.schema.json`.
- Downstream consumer: `electrical/earthing` v1.3 (paired sprint, shipped 2026-05-18).

## v1.0.0 (current — Stage 1: Schedule + Schematic + Selectivity)

First production-grade version. Stage 1 of a two-stage plan:
- **Stage 1 (this release):** DB schedule + DB face one-line schematic + cascade selectivity verification. Covers single-board IR + project-wide rollup intent across GB / EU/INT / US jurisdictions.
- **Stage 2 (planned):** Plan-view DB location drawing + DC distribution (PV, EV chargepoints).

### Features
- 13-step reasoning chain in `prompts/generator.md` that explicitly names 19 standards files to load (consumption-pattern proof)
- Jurisdiction-gated standards loading: BS 7671 (GB) / IEC 60364 (EU/INT) / NFPA 70 (US) + IEC 61439 + IEC 60617 always
- Single-board IR schema with `selectivity_results[]` and `tool_call_pending` flag per WI3 (live IEC 60909 cascade deferred to `fault-level` skill)
- TWO stable intent contracts:
  - `db-layout` (single-board) — for panel-schedule, riser, cable-containment
  - `db-layout-rollup` (project-wide) — for earthing (payload shape verified verbatim against earthing example expectations)
- Cross-drawing intent consumption: `fault-level` (when available) for live Ifault numbers; engineer-input fault currents accepted as fallback with `tool_call_pending`
- Rationale block per WI2 (9 mandatory sections)
- 8 evals covering all 6 WI5 categories + 2 skill-specific (selectivity_cascade, intent_rollup_shape)
- 3 worked examples (UK / INT / US) demonstrating jurisdiction switch + intent shape compatibility

### Standards consumed (explicit file paths — not folders)
- `shared/standards/electrical/IEC60617/symbol-index.json` (always)
- `shared/standards/electrical/IEC60617/part7-switchgear.json` (always)
- `shared/standards/electrical/IEC61439/form-separations.json` (always)
- `shared/standards/electrical/IEC61439/ip-ik-ratings.json` (always)
- `shared/standards/electrical/IEC61439/short-circuit-withstand.json` (always)
- `shared/standards/electrical/BS7671/reg433-overcurrent-protection.json` (GB)
- `shared/standards/electrical/BS7671/reg434-fault-current.json` (GB)
- `shared/standards/electrical/BS7671/reg443-spd.json` (GB)
- `shared/standards/electrical/BS7671/reg411-rcd-requirements.json` (GB)
- `shared/standards/electrical/BS7671/appendix3-device-curves.json` (GB)
- `shared/standards/electrical/BS7671/diversity-factors.json` (GB)
- `shared/standards/electrical/IEC60364/part4-43-overcurrent.json` (EU/INT)
- `shared/standards/electrical/IEC60364/part4-44-overvoltage.json` (EU/INT)
- `shared/standards/electrical/IEC60364/rcd-requirements.json` (EU/INT)
- `shared/standards/electrical/IEC60364/device-curves.json` (EU/INT)
- `shared/standards/electrical/IEC60364/diversity-factors.json` (EU/INT)
- `shared/standards/electrical/IEC60364/fault-current.json` (EU/INT)
- `shared/standards/electrical/NFPA70/art408-panelboards.json` (US)
- `shared/standards/electrical/NFPA70/art240-overcurrent.json` (US)
- `shared/standards/electrical/NFPA70/art220-load-calculations.json` (US)
- `shared/standards/electrical/NFPA70/ocpd-coordination.json` (US)

### Tool calls awaiting runtime (WI3)
- `calc.iec60909_cascade` — compute prospective fault current at each level. Status: tool_call_pending; deferred until dedicated `fault-level` skill ships.
- `calc.diversity_factor` — apply diversity factor from standard for main sizing. Status: tool_call_pending.

### Status
- `status: beta` — production-grade artefact set with two known runtime dependencies (selectivity tool, diversity tool). IR includes `tool_call_pending: true` markers where the deterministic calc has not yet been wired.
- Promotes to `production` when: 8/8 evals pass against a production model AND `fault-level` skill exists for live IEC 60909 cascade execution.
