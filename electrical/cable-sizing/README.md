# `cable-sizing` — Per-Circuit Cable Selection (IEC 60364 / BS 7671 / NEC)

**Status:** `beta`
**Version:** `1.0.0`
**Drawing type:** `cable_sizing_study`
**Reference:** `electrical/lighting-layout` (production reference) + `electrical/earthing` (sibling beta) + `electrical/db-layout` (sibling beta) + `electrical/fault-level` (sibling beta — directly consumed)

## What this skill produces

A project-scoped cable-sizing IR per BS 7671 App 4 (GB) / IEC 60364-5-52 (EU/INT) / NEC Chapter 9 + 310.16 (US) capturing:

- Cascade tree from service entrance → feeders → sub-feeders → final circuits
- Per-node selection: `phase_csa`, `cpc_csa`, `material`, `insulation`, `cable_type`, `parallel_count`
- Named `binding_constraint` per node (which check forced the csa walk-up)
- Walk-up trail showing rejected sizes + reasons
- Cumulative Vd up the parent chain (source → endpoint)
- Motor-starting Vd for motor circuits (warning, not error, when > 10%)
- CPC adiabatic check at parent ifault + OCPD t_clear
- Parallel cables when single-cable ladder exhausts
- Harmonic derating + neutral sizing for 3-phase 4-wire IT loads
- 8-section rationale block per WI2 + chat_summary

**Plus a `cable-sizing` intent** (slim downstream subset) emitted alongside — consumed by:
- `cable-schedule` (formal tabulated deliverable)
- `riser` (LV riser diagrams, floor-by-floor with parent_node_id chain)
- `cable-containment` (tray/conduit fill — uses `cable_od_mm` + `weight_kg_per_m` + `parallel_count`)

## Jurisdictions supported

| Jurisdiction | Ampacity tables | Vd source | Cable types |
|---|---|---|---|
| GB | BS 7671 App 4 Tables 4D1A–4F | App 12 + App 4 §6 | PVC singles / XLPE / MICC / SWA / FP200 / CWZ |
| EU | IEC 60364-5-52 Annex E | IEC 60364-5-52 §G | PVC / XLPE / EPR / SWA |
| INT | IEC 60364-5-52 Annex E | IEC 60364-5-52 §G | Same as EU |
| US | NEC 310.16 + Chapter 9 Table 9 + 310.15(B) | NEC 215.2(A)(1) IN | THWN-2 / THHN / XHHW-2 + 110.14(C) terminal cap |

## Cross-drawing intent contract

| Direction | Intent | Purpose |
|---|---|---|
| Produces | `cable-sizing` | Per-circuit selection — consumed by cable-schedule, riser, cable-containment |
| Consumes | `db-layout-rollup` | Per-circuit Ib/In/load_type/t_clear (preferred over engineer-declared) |
| Consumes | `fault-level` | Per-node Ifault for CPC adiabatic check (preferred over engineer-declared) |

## File structure

```
electrical/cable-sizing/
├── README.md
├── CHANGELOG.md
├── skill.manifest.json
├── inputs.json
├── prompts/        (generator 14-step / validator 10 INV / reviewer 8 D)
├── schemas/        (IR + intent)
├── rules/          (5 YAMLs: walk-up, Vd targets, correction stack, parallels, harmonic)
├── constraints/    (4 YAMLs: Iz/In/Ib, Vd cumulative, CPC adiabatic, motor starting)
├── validation/     (4 YAMLs, 12 checks)
├── ontology/       (cable-types + installation-methods)
├── docs/           (engineering-philosophy + known-limitations)
├── evals/          (runner-config + 9 evals)
└── examples/       (UK domestic / INT commercial with feeders / US industrial with motors)
```

## Eval coverage matrix

| Eval ID | Category | Tests |
|---|---|---|
| eval-01-uk-domestic-final-circuits | happy_path | 230V UK domestic, 4 final circuits all Iz-binding |
| eval-02-tpn-commercial-feeders-cumulative-vd | edge_case | 400V TPN cascade, vd_cumulative-binding at deep leaf |
| eval-03-undersized-cable-trap | validation_trap | Engineer pre-declares 1.5 mm² where Vd forces 4 mm² — must flag |
| eval-04-missing-route-data | missing_input | No length / install method → tool_call_pending, no invention |
| eval-05-jurisdiction-us-with-awg | jurisdiction_switch | US 480V aluminium feeder, NEC AWG ladder, terminal-temp cap |
| eval-06-rationale-block | rationale_block | 8 sections + chat_summary + walk_up_trail audit |
| eval-07-motor-starting-vd | skill_specific | 30 kW chiller motor — vd_starting check + warning logic |
| eval-08-parallel-cables | skill_specific | 1200A feeder — 2 × 500 kcmil parallel (binding: parallel_required) |
| eval-09-harmonic-derating-data-centre | skill_specific | IT load 33% h3 — Ch < 1.0 + neutral = phase |

All 6 WI5 categories + 3 skill-specific.

## Tool calls awaiting runtime

| Tool name | Purpose |
|---|---|
| `calc.cable_ampacity` | Iz lookup with correction factors. Contract at `shared/calculations/electrical/cable-ampacity.json`. Status: tool_call_pending until DraftsMan runtime ships. |
| `calc.voltage_drop` | mV/A/m × Ib × L with PF + temp correction. Contract at `shared/calculations/electrical/voltage-drop.json`. Status: tool_call_pending. |
| `calc.cpc_adiabatic` | S = √(I²t)/k for CPC sizing. Contract at `shared/calculations/electrical/cpc-adiabatic.json`. Status: tool_call_pending. |

## Known limitations

See `docs/known-limitations.md`. v1.0.0 does NOT cover:
- DC circuit sizing (PV, EV DCFC, battery) → future `dc-cable-sizing` sibling
- Arc-flash incident-energy boundary marking → `arc-flash` sibling
- IEC 60287 advanced thermal modelling for buried groups
- Communications + data cables (Cat6, fibre) → `electrical/data-telecom`
- Time-graded protection coordination → `db-layout` v1.1 + future `protection-coordination`

## Versioning

- Minor bumps (1.x.0): new jurisdictions / cable types / evals / examples
- Major bump (2.0.0): reserved for DC scope OR breaking IR schema change
- Patch bumps (1.0.x): rules / constraints / validation bug fixes

## License

See repository root `LICENSE`.
