# Changelog — electrical/cable-sizing

All notable changes to the cable-sizing skill. Follows [Keep a Changelog](https://keepachangelog.com).

## [1.0.0-beta] — 2026-05-17

### Added — v1.0.0 beta — Tier-1 Item 3
- 14-step generator chain (`prompts/generator.md`) — IEC 60364-5-52 / BS 7671 App 4 / NEC Ch 9 cascade walk
- Project-scoped cascade IR (`schemas/cable-sizing-ir.schema.json`) with walk-up trail + binding constraint
- Slim downstream `cable-sizing` intent (`schemas/cable-sizing-intent.schema.json`) — consumed by cable-schedule, riser, cable-containment
- 5 rules: csa-selection-walk-up, voltage-drop-targets, correction-factor-stack, parallel-cables-threshold, harmonic-derating-trigger
- 4 constraints: iz-vs-in-vs-ib, vd-cumulative-limit, cpc-adiabatic-passes, motor-starting-vd-limit
- 4 validation YAMLs (12 deterministic checks): cascade-tree-integrity, csa-on-standard-ladder, tool-call-resolved, intent-shape
- 2 ontology files: cable-types (PVC/XLPE/MICC/SWA/FP200/CWZ/THWN-2/THHN/XHHW-2), installation-methods (A1–G + NEC)
- 9 evals: 6 WI5 categories + 3 skill-specific (motor-starting Vd, parallel cables, harmonic derating)
- 3 worked examples: UK domestic finals / INT commercial with feeders / US industrial with motors

### Tool calls awaiting runtime (WI3 deferral)
- `calc.cable_ampacity` (contract: `shared/calculations/electrical/cable-ampacity.json`)
- `calc.voltage_drop` (contract: `shared/calculations/electrical/voltage-drop.json`)
- `calc.cpc_adiabatic` (contract: `shared/calculations/electrical/cpc-adiabatic.json`)

### Consumes intents
- `db-layout-rollup` — circuit list + Ib + In + load_type + t_clear (preferred)
- `fault-level` — per-node Ik" + X/R + Z_total (preferred)
- Engineer-declared fallback when intents absent

### Produces intent
- `cable-sizing` — per-circuit selection slim subset; forward-compatible with cable-schedule, riser, cable-containment consumers
