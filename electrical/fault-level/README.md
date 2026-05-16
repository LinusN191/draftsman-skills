# `fault-level` — IEC 60909 Prospective Fault Current Cascade

**Status:** `beta`
**Version:** `1.0.0`
**Drawing type:** `fault_level_study`
**Reference:** `electrical/lighting-layout` (production reference) + `electrical/earthing` (sibling beta) + `electrical/db-layout` (sibling beta, primary downstream consumer)

## What this skill produces

A project-scoped fault-level IR per IEC 60909-0:2016 capturing:

- HV-side modelling (≥ 1 kV primary if present): network arrangement, transformer Zpu, c-factor
- LV source modelling: utility transformer, standby generator (subtransient decrement), UPS (current-limited), induction motor back-feed
- Cascade tree: every node from source to final circuit endpoint, with path-like node_id
- Per-node Ik"max (c=1.05) + Ik"min (c=0.95) + ipk + X/R + Z_total
- Selectivity implications: breaker-by-breaker adequacy check
- Rationale block per WI2 (8 sections + chat_summary)

**Plus a `fault-level` intent** (slim downstream subset) emitted alongside — consumed by:
- `electrical/db-layout` (resolves selectivity `tool_call_pending` entries)
- `electrical/earthing` v1.1+ (optional cross-validation of Ze)
- `electrical/cable-sizing` (adiabatic check)
- `electrical/generator-sizing` (future, generator Iek dimensioning)

## Jurisdictions supported

| Jurisdiction | Standards loaded | LV cable R+X source | Notes |
|---|---|---|---|
| GB | IEC 60909 + BS 7671 reg434 + App 4 | BS 7671 Appendix 4 Table 4D5 + 4F | UK-typical 230V/400V; PSCC from DNO declaration |
| EU | IEC 60909 + IEC 60364-4-43 | IEC 60364-5-52 Annex E | 230V/400V; PSCC from utility per IEC 60909-0 |
| INT | IEC 60909 + IEC 60364-4-43 | IEC 60364-5-52 Annex E | Same as EU |
| US | IEC 60909 + NEC 110.9 + 240.86 + NEC Chapter 9 Table 9 | NEC Chapter 9 Table 9 | 120/240V split, 480V TPN; available fault current marking per NEC 110.24 |

## Cross-drawing intent contract

| Direction | Intent | Purpose |
|---|---|---|
| Produces | `fault-level` | Per-node Ifault values — consumed by db-layout, earthing, cable-sizing, generator-sizing |
| Consumes | `db-layout-rollup` | Cascade topology (preferred); engineer-declared cascade is the fallback |

## File structure

```
electrical/fault-level/
├── README.md
├── CHANGELOG.md
├── skill.manifest.json
├── inputs.json
├── prompts/        (generator 14-step / validator 10 INV / reviewer 8 D)
├── schemas/        (IR + intent)
├── rules/          (5 YAMLs: source defaults, motor thresholds, c-factor, UPS, kappa)
├── constraints/    (4 YAMLs: breaker Icn, busbar Ipk, cable I²t, source-Z bounds)
├── validation/     (4 YAMLs: tree integrity, monotonicity, tool-call, intent shape)
├── ontology/       (source-types + cascade-node-kinds)
├── docs/           (engineering-philosophy + known-limitations)
├── evals/          (runner-config + 9 evals)
└── examples/       (UK domestic / INT commercial+gen / US industrial+motors)
```

Sibling standards layer at `shared/standards/electrical/IEC60909/` (13 files).

## Eval coverage matrix

| Eval ID | Category | Tests |
|---|---|---|
| eval-01-uk-domestic-cu-cascade | happy_path | 230V UK domestic, single utility source |
| eval-02-tpn-commercial-with-gen | edge_case | 400V TPN MSB + standby genset (NG decrement) |
| eval-03-undersized-breaker-trap | validation_trap | MCB Icn 6kA at 12kA cascade — must flag |
| eval-04-missing-source-data | missing_input | No Zpu/PSCC → tool_call_pending, no invention |
| eval-05-jurisdiction-us-with-hv | jurisdiction_switch | US 12.47 kV HV + 480V LV, NEC citations only |
| eval-06-rationale-block | rationale_block | 8 sections + WI2-conformant chat_summary |
| eval-07-multi-source-coordination | skill_specific | utility + gen + UPS simultaneously |
| eval-08-induction-motor-contribution | skill_specific | 500 kW motor back-feed per IEC §4.5 |
| eval-09-intent-shape | skill_specific | Intent satisfies db-layout's consumed_intent shape |

All 6 WI5 categories + 3 skill-specific.

## Tool calls awaiting runtime

| Tool name | Purpose |
|---|---|
| `calc.iec60909_cascade` | IEC 60909-0 cascade computation. Contract at `shared/calculations/electrical/iec60909-cascade.json`. Status: tool_call_pending until DraftsMan runtime project ships. |

## Known limitations

See `docs/known-limitations.md`. v1.0.0 does NOT cover:
- DC fault analysis (PV / battery / EV DCFC) → separate `dc-fault-level` skill
- Arc-flash incident energy (IEEE 1584 / NFPA 70E) → separate `arc-flash` skill
- Time-graded protection coordination → separate `protection-coordination` skill
- Lightning-induced transients (BS EN 62305 / NFPA 780)
- Sub-cycle dynamic simulation (beyond IEC 60909 scope)

## Versioning

- **Minor bumps** (1.x.0) add new jurisdictions / examples / evals
- **Major bump** (2.0.0) reserved for DC fault analysis OR multi-mode IR
- **Patch bumps** (1.0.x) for rules / constraints / validation bug fixes

## License

See repository root `LICENSE`.
