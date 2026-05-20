# Changelog

## [1.0.0] - 2026-05-20

### Added — first ship (beta)

- **Multi-skill consumer**: consumes `db-layout-rollup` + `fault-level` intents (pattern matches SLD v1.4). Falls back to engineer-declared inputs when intents absent.
- **Project-scoped cascade IR**: mirrors `fault-level-ir` structure. Every node carries `node_id`, `parent_node_id`, `node_kind`, route data, selection, and checks.
- **Walk-the-ladder CSA selection**: each node records `binding_constraint` (from 6-token vocabulary) + `walk_up_trail[]` (every csa tried + rejection reason).
- **4 extra engineering checks**: cumulative Vd, motor-starting Vd, parallel cables, harmonic derating.
- **WI3 tool-call deferral**: `tool_call_pending: true` per cascade node until runtime ships `calc.cable_ampacity` / `calc.voltage_drop` / `calc.cpc_adiabatic`. All 3 calc contracts exist on disk (REUSED, not created).
- **Output intent (4 downstream consumers)**: `cable-schedule` (full per-circuit set) + `riser` (feeder + parent_node_id) + `cable-containment` (cable_od_mm + weight_kg_per_m + parallel_count) + `small-power v1.1` (Zs-resolution helper fields).
- **Zs-resolution helper fields per refresh 2026-05-20**: `r1_plus_r2_milliohm_per_m_at_operating_temp` + `reactance_milliohm_per_m` on every emitted circuit. Lookups from BS 7671 App 4 Tables 4F1-4F3 / IEC 60364-5-52 Table B.52.5 / NEC Chapter 9 Table 9.
- **4 jurisdictional examples**: UK domestic + KE Nairobi commercial + INT commercial with feeders + US industrial with motors.
- **3 prompts**: generator (14-step) + validator (10 INV) + reviewer (8 D).
- **9 evals**: 6 WI5 categories + 3 skill-specific (motor-starting-vd, parallel-cables, harmonic-derating).
- **5 rules + 4 constraints + 4 validation YAMLs** (12 validation checks total).
- **Calc contract consumer updates**: small-power Task 3 precedent — `_consuming_skills[]` added to `cable-ampacity.json` + `voltage-drop.json` + `cpc-adiabatic.json` to record cable-sizing as primary v1.0.0 consumer.

### Pattern parents

- `electrical/fault-level` v1.1 — project-scoped cascade IR (closest structural match)
- `electrical/earthing` v1.4 — 4-jurisdiction example pattern + KS 1700 routing convention
- `electrical/small-power` v1.0 — KE citation form precedent (KS 1700:2018 §313 leading) + WI3 deferral
- `electrical/db-layout` v1.3.1 — multi-skill intent production (produces db-layout AND db-layout-rollup)
- `electrical/sld` v1.4 — multi-skill consumption (consumes 3 intents)

### Future direction (deferred)

- v1.1 — extend intent to cable-schedule deliverable shape; tighten cross-skill consistency checks
- v1.2 — add LV switchboard busbar sizing (BS EN 61439 Annex N)
- v2.0 — DC cable sizing (PV strings + EV DCFC + battery interconnects) breaks v1.x schema
- `dc-cable-sizing` skill — IEC 62548 / NEC 690 / IEC 61851 (separate skill)
