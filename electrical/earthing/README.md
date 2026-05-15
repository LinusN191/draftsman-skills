# `earthing` — Electrical Earthing Schematic Generator

**Status:** `beta`
**Version:** `1.0.0`
**Drawing type:** `earthing_schematic`
**Reference:** `electrical/lighting-layout` (production skill — same pattern)

## What this skill produces

A single-line earthing schematic IR (Intermediate Representation) that captures:

- The earthing system (TN-C-S / TT / TN-S)
- The Main Earthing Terminal (MET) location and arrangement
- Earth electrode(s) where required (TT: always; TN-C-S: optional; NEC: GES supplemental)
- Main protective bonding to all extraneous-conductive-parts
- Supplementary bonding in locations of increased shock risk
- Circuit protective conductor (CPC / EGC) per outgoing circuit, sized per the appropriate jurisdiction table
- Zs verification against the disconnection-time-limited Zs_max
- RCD/GFCI requirement flags per jurisdiction
- A structured `rationale` block per WI2 (9 sections + chat_summary)

This is **stage 1** of the earthing skill — schematic only. Plan-view and declaration-only stages are deferred.

## Jurisdictions supported

| Jurisdiction | Standards files loaded | CPC sizing | RCD blanket |
|---|---|---|---|
| GB | BS 7671:2018+A3 Reg 411 family, Tables 54.7/54.8 | Table 54.7 or adiabatic 54.1 | TT only |
| EU | IEC 60364-4-41, IEC 60364-5-54 | Table 54.2 or adiabatic 543.1.2 | TT only |
| INT | IEC 60364-4-41, IEC 60364-5-54 | Table 54.2 or adiabatic 543.1.2 | TT only |
| US | NEC 2023 Article 250 | Table 250.122 (by OCPD rating) | NEC GFCI rules per 210.8 |

## Cross-drawing intent contract

| Direction | Intent | Purpose |
|---|---|---|
| Consumes | `db-layout` | Board structure and outgoing circuit list |
| Consumes | `lighting-layout` | Bathroom locations, emergency-lighting circuits to verify |
| Consumes | `small-power` | Socket-outlet circuits requiring RCD per BS 7671 411.3.3 |
| Produces | `earthing` | MET location, electrode targets, bonding map, per-circuit CPC, Zs+RCD status |

## File structure

```
electrical/earthing/
├── README.md
├── CHANGELOG.md
├── skill.manifest.json
├── inputs.json
├── prompts/
│   ├── generator.md
│   ├── validator.md
│   └── reviewer.md
├── schemas/
│   ├── earthing-ir.schema.json
│   └── earthing-intent.schema.json
├── rules/
│   ├── electrode-selection.yaml
│   └── cpc-sizing.yaml
├── constraints/
│   ├── electrode-resistance.yaml
│   └── bonding-geometry.yaml
├── validation/
│   ├── zs-compliance.yaml
│   ├── bonding-completeness.yaml
│   └── cpc-sizing.yaml
├── ontology/
│   └── earthing-system-types.json
├── docs/
│   ├── engineering-philosophy.md
│   └── known-limitations.md
├── evals/
│   ├── runner-config.json
│   ├── eval-01-uk-dwelling-tn-cs.yaml
│   ├── eval-02-rural-tt-system.yaml
│   ├── eval-03-cpc-undersized-trap.yaml
│   ├── eval-04-missing-soil-resistivity.yaml
│   ├── eval-05-jurisdiction-us-nec.yaml
│   └── eval-06-rationale-block.yaml
└── examples/
    ├── uk-dwelling-tn-cs/         (input.json, reasoning.md, output.json)
    ├── intl-rural-tt/             (input.json, reasoning.md, output.json)
    └── us-commercial-nec/         (input.json, reasoning.md, output.json)
```

## Eval coverage matrix

| Eval ID | Category | Tests |
|---|---|---|
| eval-01-uk-dwelling-tn-cs | happy_path | Full triple consumed-intent, TN-C-S, 6 circuits, all pass |
| eval-02-rural-tt-system | edge_case | TT system, electrode design, blanket RCD requirement |
| eval-03-cpc-undersized-trap | validation_trap | Generator must reject an undersized declared CPC |
| eval-04-missing-soil-resistivity | missing_input | TT with no soil data — must flag, not invent |
| eval-05-jurisdiction-us-nec | jurisdiction_switch | NEC terminology, Table 250.122, no BS 7671 citations |
| eval-06-rationale-block | rationale_block | 9-section taxonomy + clause-cited decisions per WI2 |

All 6 WI5 categories covered. See `evals/runner-config.json` for scoring thresholds.

## Tool calls awaiting runtime

Per upstream WI3, this skill declares — but does not yet invoke — the following calculation tools. The IR marks affected items `tool_call_pending: true` and accepts engineer-provided values in the interim.

| Tool name | Purpose |
|---|---|
| `calc.electrode_resistance` | Compute Ra from soil resistivity and electrode geometry |
| `calc.cpc_adiabatic` | Compute CPC CSA via adiabatic equation for fault energy let-through |

## Known limitations

See `docs/known-limitations.md`. Stage 1 does NOT cover:
- IT systems (hospitals Group 2, certain industrial)
- Plan-view earthing layout
- Declaration-only mode (referencing existing earthing)
- EV chargepoint open-PEN mitigation
- Lightning protection bonding (BS EN 62305)
- Generator-fed earthing arrangements

## Versioning

This skill follows the same versioning policy as `lighting-layout`:
- **Minor bumps** (1.x.0) add new jurisdictions, new examples, new evals
- **Major bump** (2.0.0) reserved for the plan-view stage 2 release
- **Patch bumps** (1.0.x) for bug fixes in rules / constraints / validation

## License

See repository root `LICENSE`.
