# Changelog — fault-level

## [1.1.0] - 2026-05-18

### Added
- 3 new examples (pairs with SLD v1.4 multi-skill consumption sprint):
  - `uk-commercial-3storey` — 4-board UK cascade, TN-C-S 400V, BS 7671:2018+A2 + IEC 60909-0:2016
  - `ke-nairobi-industrial` — 2-board KE cascade, KPLC TN-S 415V, KS 1700:2018 direct citation form + IEC 60909-0:2016 §3.8.1 motor threshold (strict-rule exclusion documented)
  - `us-strip-mall-retail` — 4-tenant US cascade, 208Y/120V PoCo, NEC 2023 §110.9 AIC verification

### Changed
- All 6 fault-level examples now ship with `intent-out.json` conforming to `fault-level-intent.schema.json` (strict `additionalProperties: false`)
- 3 pre-existing examples (uk-domestic-single-source, intl-commercial-with-genset, us-industrial-with-motors) backfilled with intent-out.json — completes the WI4 producer contract

### Engineering details
- κ recomputed per cascade node per IEC 60909-0:2016 Eq 29: `κ = 1.02 + 0.98·exp(-3/(X/R))` — not frozen at upstream value
- Cable impedance from IEC 60364-5-52:2009 Annex E (IEC examples) and NEC 2023 Chapter 9 Table 9 (US example)

### Pattern parent
- db-layout v1.1 intent-out backfill (shipped 2026-05-17) — same backfill convention applied

---

## v1.0.0 (current — IEC 60909 HV+LV cascade)

First production-grade version. Single-stage skill (no sub-stages planned at v1).

### Features
- 14-step reasoning chain in `prompts/generator.md` that explicitly names 21 standards files (consumption-pattern proof)
- New IEC 60909 standards layer at `shared/standards/electrical/IEC60909/` (13 files) shipped as Phase A
- HV+LV scope: handles 11/22/33 kV primary modelling + LV cascade
- Four source types modelled per IEC 60909-0: utility / generator (subtransient decrement) / UPS (current-limited) / induction motor back-feed
- Two stable artefacts emitted: fault-level IR (full audit trail) + fault-level intent (slim downstream-facing subset)
- Hybrid cascade input: prefer `db-layout-rollup` intent; fall back to engineer-declared cascade
- Calculation deferred per WI3 to `calc.iec60909_cascade` runtime tool (contract at `shared/calculations/electrical/iec60909-cascade.json`)
- Cross-skill integration: emitted intent resolves `db-layout` selectivity `tool_call_pending` entries
- Rationale block per WI2 (8 mandatory sections)
- 9 evals covering all 6 WI5 categories + 3 skill-specific (multi-source coordination, motor contribution, intent shape verification)
- 3 worked examples (UK / INT / US) demonstrating jurisdiction switch + source-type diversity

### Standards consumed (explicit file paths — not folders)
- `shared/standards/electrical/IEC60909/part0-fundamentals.json` (always)
- `shared/standards/electrical/IEC60909/part0-method.md` (always)
- `shared/standards/electrical/IEC60909/peak-factor-kappa.json` (always)
- `shared/standards/electrical/IEC60909/voltage-factor-c.json` (always)
- `shared/standards/electrical/IEC60909/source-impedances.json` (always)
- `shared/standards/electrical/IEC60909/transformer-zpu-table.json` (always)
- `shared/standards/electrical/IEC60909/generator-subtransient-tables.json` (always)
- `shared/standards/electrical/IEC60909/motor-contribution-rules.json` (always)
- `shared/standards/electrical/IEC60617/symbol-index.json` (always)
- `shared/standards/electrical/IEC60617/part7-switchgear.json` (always)
- `shared/standards/electrical/BS7671/reg434-fault-current.json` (GB)
- `shared/standards/electrical/BS7671/pscc-determination.md` (GB)
- `shared/standards/electrical/BS7671/appendix4-cable-ratings.json` (GB — R+X per cable)
- `shared/standards/electrical/IEC60364/fault-current.json` (EU/INT)
- `shared/standards/electrical/IEC60364/pscc-determination.md` (EU/INT)
- `shared/standards/electrical/IEC60364/part5-52-cable-ratings-copper.json` (EU/INT)
- `shared/standards/electrical/IEC60364/part5-52-cable-ratings-aluminium.json` (EU/INT)
- `shared/standards/electrical/NFPA70/chapter1-general.json` (US — NEC 110.9)
- `shared/standards/electrical/NFPA70/art240-overcurrent.json` (US)
- `shared/standards/electrical/NFPA70/ocpd-coordination.json` (US)
- `shared/standards/electrical/NFPA70/chapter9-tables.json` (US — Chapter 9 Table 9 R+X)

### Tool calls awaiting runtime (WI3)
- `calc.iec60909_cascade` — IEC 60909-0 prospective fault current cascade computation. Status: contract shipped (Item 1 of Tier 1 sequence, commit `34e28e7`); tool_call_pending until runtime project implements.

### Status
- `status: beta` — production-grade artefact set with one known runtime dependency. IR includes `tool_call_pending: true` markers where the cascade tool has not yet executed.
- Promotes to `production` when: 9/9 evals pass against a production model AND `calc.iec60909_cascade` runtime tool exists.
