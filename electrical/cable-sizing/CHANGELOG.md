# Changelog

## [1.0.2] - 2026-05-25

### Standards data (M3 cause-fix)
- **M3** (data provenance): added `shared/standards/electrical/BS7671/appendix4-table-4D1A-pvc-twin-earth.json` — UK domestic PVC twin-and-earth Iz + mVAm per Methods C / A / 100 / 101 / 102 / 103.
- **M3**: added `shared/standards/electrical/BS7671/appendix4-table-4D5A-pvc-swa.json` — PVC SWA Iz + mVAm per Methods C / D.
- **M3**: added 1.0 mm² row to existing `appendix4-cable-ratings.json` (4D2A XLPE Cu, all 5 method blocks: A1, B1, C, E_trefoil, F_flat); previously absent despite being a standard UK lighting CSA.
- All new tables flagged `verification_status: engineer_transcription_C2` — values transcribed from industry-standard references; engineer-verify against published BS 7671:2018+A2:2022 Appendix 4 before runtime use.
- Methods 101 / 102 / 103 (4D1A) and Method D (4D5A) additionally flagged `verification_status: pending_engineer_transcription` with `_TODO` notes — engineering estimates only; must be verified against published edition before runtime use.

Closes DEFECT_REGISTER M3 (Reviewer 1: "PVC and SWA cables sized from values not present in shipped XLPE-only tables; 1.0 mm² absent entirely").

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
