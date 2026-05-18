# `sld` — Single Line Diagram Generator

**Status:** `beta`
**Version:** `1.3.0`
**Drawing type:** `single_line_diagram`
**Reference:** `electrical/lighting-layout` (production skill — same pattern)

## What this skill produces

A single-line diagram (SLD) Intermediate Representation (IR) that captures:

- The distribution hierarchy from utility intake → main switchboard (MSB) → intermediate boards → final circuit groups
- Board types (main switchboard, sub-distribution board, panel, sub-panel, fire alarm panel, life-safety panel, UPS distribution)
- Feeder circuits between boards, including load current, cable sizing placeholders, and protection device specifications
- Protection coordination verdicts (selectivity, partial selectivity, or non-selective)
- Fault level context at each board location (prospective fault current — PFC)
- Surge protection device (SPD) type assignments per jurisdiction and board location
- Life-safety circuit isolation requirements (fire alarm, emergency lighting, fire pump, smoke control)
- A structured `rationale` block per WI2 (9 sections + chat_summary)

This is **stage 1** of the SLD skill — logical topology only (parent-child hierarchy, protection specs, selectivity verdicts). Plan-view schematic and 3D routing are deferred to v1.4+.

## Standards layers consumed

| Standard | Purpose | Role |
|----------|---------|------|
| **BS 7671:2018** | UK electrical safety code | Primary for GB; defines board roles (Reg 311), protection selectivity (Reg 533), RCD blanket rules (Reg 411) |
| **BS EN 60617** | Electrical symbols | SLD drawing conventions (contact symbols, device types, earthing symbols) |
| **BS EN 61439-1:2020** | Low-voltage switchgear assemblies | Distribution board design (busbar sizing, thermal limits, breaking capacity verification) |
| **IEC 60364-4-44:2019** | Protection for safety — overcurrent protection | Tiered selectivity framework; applies across EU, INT, and adoptive jurisdictions (KE) |
| **IEC 62305-3:2010** | Lightning protection — bonding and earthing | SPD type 1 placement for buildings with external lightning conductor |
| **NEC 2023 / NFPA 70** | US electrical code | Panel sizing, sub-panel interconnection, service-entrance SPD requirements, AIC ratings |

## Jurisdictions supported

| Jurisdiction | Primary Standard | Board Role Convention | Device Rating Convention |
|---|---|---|---|
| GB | BS 7671:2018 | MSB, SDB | Icu per IEC 60947-2 |
| EU | IEC 60364 | MSB, SDB | Icu per IEC 60947-2 |
| INT | IEC 60364 (adopted) | MSB, SDB | Icu per IEC 60947-2 |
| **KE** | **KS 1700:2018 (primary) + IEC 60364 (fallback)** | **MSB, SDB (IEC-aligned)** | **Icu per IEC 60947-2** |
| US | NEC 2023 | Panel, Sub-Panel | AIC per UL 489 |

## Cross-drawing intent contract

| Direction | Intent | Purpose |
|---|---|---|
| **Consumes** | `db-layout` | Board structure (MSB id, sub-board roles, outgoing circuit list) |
| **Consumes** | `fault-level` (planned v1.5) | PFC at each board (for breaking capacity verification); deferred in v1.3 |
| **Produces** | `sld` | Distribution hierarchy, feeder specs, protection coordination verdicts, life-safety flags |

## File structure

```
electrical/sld/
├── README.md
├── CHANGELOG.md
├── skill.manifest.json
├── inputs.json
├── prompts/
│   ├── generator.md
│   ├── validator.md
│   └── reviewer.md
├── schemas/
│   ├── sld-ir.schema.json
│   └── sld-intent.schema.json
├── rules/
│   ├── distribution-hierarchy.yaml       (6 rules: tree structure, board role enums, fire-alarm routing)
│   ├── device-selection.yaml             (4 rules + 1 extension: MCCB vs MCB, type curves, breaking capacity, AIC vs Icu)
│   ├── spd-policy.yaml                   (4 rules per jurisdiction: Type 1/2/3 tiering)
│   └── life-safety-isolation.yaml        (6 rules: fire alarm, emergency lighting, UPS, mixed boards)
├── constraints/
│   ├── selectivity-cascade.yaml          (3 checks: every parent-child has verdict, verdict enum validation, non-selective rationale)
│   ├── intake-capacity.yaml              (2 checks: MSB rating vs total demand, breaking capacity vs PFC)
│   └── intent-shape.yaml                 (3 checks: board count alignment, MSB id match, boards array 1:1 mapping)
├── validation/
│   ├── ir-integrity.yaml                 (3 checks: root exists, non-root parent resolution, consumed path existence)
│   ├── jurisdiction-routing.yaml         (3 checks: BS citations for GB, KS citations for KE, NEC for US)
│   └── tool-deferral-shape.yaml          (3 checks: tool_call_pending_for_system_metrics consistency with flags array)
├── ontology/
│   ├── board-roles.json                  (7 entries: main_switchboard, sub_distribution_board, panel, sub_panel, fire_alarm_panel, life_safety_panel, ups_distribution)
│   └── distribution-types.json           (5 entries: radial, ring, split_phase, tpn, tpn_plus_e)
├── docs/
│   ├── engineering-philosophy.md
│   └── known-limitations.md
├── assets/
│   ├── spd-type-selection-matrix.md      (jurisdiction × building type → SPD type)
│   └── device-rating-table.md            (MCCB/MCB selection by feeder current)
├── evals/
│   ├── runner-config.json
│   └── [7 eval YAMLs covering WI5 categories + skill-specific]
└── examples/
    ├── gb-three-phase-office/            (input.json, reasoning.md, output.json, intent-out.json)
    ├── us-residential-split-phase/       (input.json, reasoning.md, output.json, intent-out.json)
    ├── ke-industrial-tpn/                (input.json, reasoning.md, output.json, intent-out.json)
    └── partial-selective-large-building/ (input.json, reasoning.md, output.json, intent-out.json)
```

## Eval coverage matrix

| Eval ID | Category | Tests |
|---|---|---|
| eval-01-gb-three-phase | happy_path | GB office, TN-C-S, MSB + 2 SDBs, full selectivity verdicts |
| eval-02-us-residential | edge_case | US split-phase dwelling, service SPD, AIC rating convention |
| eval-03-selectivity-trap | validation_trap | Generator must reject non-selective verdict without documented rationale |
| eval-04-fire-alarm-isolation | edge_case | Fire alarm panel must have no upstream RCD; verify isolation rules enforced |
| eval-05-jurisdiction-switch | jurisdiction_switch | KE design: KS 1700 citations only (not "BS adopted by KS"), PFC context from fault-level intent |
| eval-06-rationale-block | rationale_block | 9-section taxonomy + clause-cited decisions per WI2 |
| eval-07-intent-alignment | skill_specific | Intent output boards[] count matches IR hierarchy; MSB id resolves correctly |

7 evals: 5 WI5 categories + 2 skill-specific. See `evals/runner-config.json` for scoring thresholds.

## Tool calls awaiting runtime

Per upstream WI3, this skill declares — but does not yet invoke — the following calculation tools. The IR marks affected items `tool_call_pending: true` and accepts engineer-provided values in the interim.

| Tool name | Purpose | Status | Input placeholder |
|---|---|---|---|
| `calc.sld_system_metrics` | Calculate PFC at each board (requires db-layout hierarchy + upstream fault-level); derive total site Imax | tool_call_pending (since v1.3.0) | `system_metrics_calc_tool_input` |

Until the DraftsMan runtime ships the `calc.sld_system_metrics` implementation, the generator accepts engineer-provided PFC estimates and flags the deferred state with `tool_call_pending_for_system_metrics: true` + `TOOL-CALL-PENDING:sld_system_metrics` in the flags array.

## Known limitations

See `docs/known-limitations.md`. Stage 1 does NOT cover:

- Plan-view / schematic routing (cable tray, conduit, wall placement)
- 3D spatial layouts or site plan integration
- Dynamic load calculation (diversity factors, simultaneity)
- Protection coordination curves (TT/TN-C-S/TN-S trip time plots)
- Harmonic loading effects on device selectivity
- Generator-fed boards and parallel-source switching
- Ring main distribution (legacy UK; rare in modern builds)

## Versioning

This skill follows the same versioning policy as `lighting-layout`:

- **Minor bumps** (1.x.0) add new jurisdictions, new examples, new evals, refinements to existing rules
- **Major bump** (2.0.0) reserved for stage 2 (plan-view schematic + 3D routing)
- **Patch bumps** (1.0.x) for bug fixes in rules / constraints / validation

**Current roadmap:**

- **v1.3.0** (current) — logical topology, selectivity verdicts, life-safety rules, jurisdiction routing
- **v1.4.0** (planned) — intent output refinement, tool input schema for calc.sld_system_metrics, 2 additional evals
- **v1.5.0** (planned) — fault-level integration (calc.sld_system_metrics invoked), PFC at each board, breaking capacity verification automated

## License

See repository root `LICENSE`.
