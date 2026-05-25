# Changelog

## [1.0.1] - 2026-05-25

### Fixed
- **H4** (3-phase circuits): voltage drop formula was dividing by 230 V (phase
  voltage) instead of line-line voltage (400 V INT/EU, 415 V KE/GB). Per BS 7671
  Appendix 4 + Appendix 12 the mV/A/m tables are referenced to line-line for
  3-phase. Inflated every 3-phase Vd by √3 (~73%). Recomputed circuits:
  - `ke-nairobi-commercial-with-msb/MSB-1.F02` segment 1.8 → 0.96% (25 mm²
    selection preserved per spec; cumulative 1.27%; downstream F02.C03 now
    4.47% with headroom)
  - `ke-nairobi-commercial-with-msb/MSB-1.F03` segment 1.05 → 0.55%
    (selection unchanged at 16 mm²)
  - `intl-commercial-with-feeders/RISER.L3.C07` segment 1.4 → 0.79%
    (selection unchanged at 6 mm²; binding remains `harmonic_derating`)
- Diagnostic + rationale prose in `ke-nairobi-commercial-with-msb/output.json`
  updated to mirror corrected Vd numbers (F02 walk-up explanation now shows
  16 mm² rejected at cumulative 1.81% would push F02.C03 to 5.01% over limit;
  25 mm² accepted at cumulative 1.27% leaves F02.C03 at 4.47% comfortable).
- `ke-nairobi-commercial-with-msb/intent-out.json` cascade ripple applied
  (emitted intent re-reflects corrected segment + cumulative values).

### Added
- Generator prompt now explicitly distinguishes 1-phase (÷230 V) vs 3-phase
  (÷U_LL where U_LL = 400 V INT/EU, 415 V KE/GB) Vd formulas, with the
  equivalent r/x formulation also shown for IEC 60364-5-52 / NEC Ch 9 Table 9
  workflows. The two forms are documented as equivalent when sourced from the
  same impedance table.
- Validator **INV-11**: detects ÷230 anomaly on 3-phase circuits (HIGH) by
  recomputing both denominators and flagging the ÷230 vs ÷U_LL match pattern.

## [1.0.0] - 2026-05-20

### Added — first ship (beta)

- **Multi-skill consumer**: consumes `db-layout-rollup` + `fault-level` intents (pattern matches SLD v1.4). Falls back to engineer-declared inputs when intents absent.
- **Project-scoped cascade IR**: mirrors `fault-level-ir` structure. Every node carries `node_id`, `parent_node_id`, `node_kind`, route data, selection, and checks.
- **Walk-the-ladder CSA selection**: each node records `binding_constraint` (from 6-token vocabulary) + `walk_up_trail[]` (every csa tried + rejection reason).
- **4 extra engineering checks**: cumulative Vd, motor-starting Vd, parallel cables, harmonic derating.
- **WI3 tool-call deferral**: `tool_call_pending: true` per cascade node until runtime ships `calc.cable_ampacity` / `calc.voltage_drop` / `calc.cpc_adiabatic`. All 3 calc contracts exist on disk (REUSED, not created).
- **Output intent (4 downstream consumers)**: `cable-schedule` (full per-circuit set) + `riser` (feeder + parent_node_id) + `cable-containment` (cable_od_mm + weight_kg_per_m + parallel_count) + `small-power v1.1` (Zs-resolution helper fields).
- **Zs-resolution helper fields per refresh 2026-05-20**: `r1_plus_r2_milliohm_per_m_at_operating_temp` + `reactance_milliohm_per_m` on every emitted circuit. Lookups from BS 7671:2018+A2:2022 App 4 Tables 4F1-4F3 / IEC 60364-5-52 Table B.52.5 / NEC 2023 Chapter 9 Table 9.
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
