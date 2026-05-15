# `db-layout` — Distribution Board Schedule + Schematic + Selectivity Generator

**Status:** `beta`
**Version:** `1.0.0`
**Drawing type:** `db_layout_schedule_and_schematic`
**Reference:** `electrical/lighting-layout` (production reference) + `electrical/earthing` (sibling beta — same pattern)

## What this skill produces

A single-board IR (Intermediate Representation) per distribution board, capturing:

- The board (consumer unit / DB / MSB / NEMA panelboard) — IEC 61439 form OR NEMA enclosure type
- Incoming supply specification (voltage / phase / supply rating / Ze)
- Busbar sizing (rating + IcW + Ipk)
- Way assignment (used / spare / multi-pole accounting)
- Circuit schedule (OCPD + RCD/GFCI + cable per circuit)
- IEC 60617 face one-line schematic symbol roll-up
- Cascade selectivity verification (manufacturer table OR IEC 60909 OR `tool_call_pending`)
- A structured `rationale` block per WI2 (9 sections + chat_summary)

**Plus a project-rollup intent** (`db-layout-rollup`) emitted alongside aggregating all boards in the project — this is what the `earthing` skill consumes.

This is **stage 1** of the db-layout skill — schedule + face schematic + selectivity. Plan-view DB location and DC distribution are deferred.

## Jurisdictions supported

| Jurisdiction | Primary standards | OCPD sizing | Selectivity reference |
|---|---|---|---|
| GB | BS 7671:2018+A3 + IEC 61439 | BS 7671 Reg 433 + Appendix 3 device curves | BS 7671 Reg 536 + manufacturer cascade tables |
| EU | IEC 60364 + IEC 61439 | IEC 60364-4-43 + IEC 60364 device curves | IEC 60364-5-53 + manufacturer cascade tables |
| INT | IEC 60364 + IEC 61439 | Same as EU | Same as EU |
| US | NFPA 70 Art 408 + 240 + 220 | NEC 240 OCPD coordination | NEC 240.12 + ocpd-coordination |

## Cross-drawing intent contract

| Direction | Intent | Purpose |
|---|---|---|
| Produces | `db-layout` | Single-board intent — consumed by `panel-schedule`, `riser`, `cable-containment` |
| Produces | `db-layout-rollup` | Project-rollup intent — consumed by `earthing` |
| Consumes | `fault-level` | Prospective fault currents at each cascade level (when that skill ships) |
| Consumes | `lighting-layout` | Lighting circuit loads + lengths (optional — alternative to engineer-input circuit data) |

## File structure

```
electrical/db-layout/
├── README.md
├── CHANGELOG.md
├── skill.manifest.json
├── inputs.json
├── prompts/
│   ├── generator.md      (13-step reasoning chain)
│   ├── validator.md      (11 INV invariants)
│   └── reviewer.md       (9 D dimensions)
├── schemas/
│   ├── db-layout-ir.schema.json
│   ├── db-layout-intent.schema.json          (single board)
│   └── db-layout-rollup-intent.schema.json   (project rollup — matches earthing's expected shape)
├── rules/                (4 YAMLs)
├── constraints/          (3 YAMLs)
├── validation/           (4 YAMLs — 14 deterministic checks)
├── ontology/             (2 JSONs: board-types, ocpd-types)
├── docs/                 (engineering-philosophy + known-limitations)
├── evals/                (runner-config + 8 evals)
└── examples/             (3 worked examples × 3 files each)
```

## Eval coverage matrix

| Eval ID | Category | Tests |
|---|---|---|
| eval-01-uk-domestic-cu-tn-cs | happy_path | 100A TN-C-S CU, 6 circuits, all RCD-protected |
| eval-02-tpn-commercial-msb | edge_case | 800A TPN MSB Form 4b + 4-way cascade |
| eval-03-undersized-busbar-trap | validation_trap | Generator must flag/correct undersized busbar |
| eval-04-missing-fault-current | missing_input | No Ifault → selectivity must defer, not invent |
| eval-05-jurisdiction-us-panelboard | jurisdiction_switch | NEMA panelboard, NEC Art 408, no BS 7671 citations |
| eval-06-rationale-block | rationale_block | 9-section rationale per WI2 |
| eval-07-selectivity-cascade | skill_specific | Two-level cascade with manufacturer-table verdicts |
| eval-08-intent-rollup-shape | skill_specific | Rollup intent matches earthing's expected shape verbatim |

All 6 WI5 categories + 2 skill-specific = 8 evals.

## Tool calls awaiting runtime

Per WI3, this skill declares — but defers — these calculation tools.

| Tool name | Purpose |
|---|---|
| `calc.iec60909_cascade` | Compute Ifault at each cascade level |
| `calc.diversity_factor` | Apply diversity factor from standards |

When `fault-level` skill ships + WI3 runtime tools land, selectivity_results entries currently emitted as `source: "tool_call_pending"` will be re-emitted as `source: "iec_60909_calc"` with computed `selective_to_fault_ka`.

## Known limitations

See `docs/known-limitations.md`. Stage 1 does NOT cover:
- Plan-view DB location drawing (stage 2)
- DC distribution (PV, EV chargepoints) — v1.1.0
- Live IEC 60909 calculation — deferred until `fault-level` skill ships
- MCC internal compartment detail
- Arc-flash hazard analysis (NFPA 70E / IEEE 1584)
- Generator + UPS transfer scheme coordination
- Voltage drop verification (separate `voltage-drop` / `cable-sizing` skill scope)

## Versioning

- **Minor bumps** (1.x.0) add new jurisdictions / examples / evals
- **Major bump** (2.0.0) reserved for stage 2 plan-view release
- **Patch bumps** (1.0.x) for rules / constraints / validation bug fixes

## License

See repository root `LICENSE`.
