# `electrical/fault-level` Skill — v1.0.0 Design Spec

> **Date:** 2026-05-16
> **Status:** Approved for implementation
> **Predecessor:** `electrical/db-layout` v1.0.0 beta (consumer of fault-level intent)
> **Companion:** New `shared/standards/electrical/IEC60909/` standards layer (11 files), shipped alongside

---

## 1. Goal

Build a production-grade `electrical/fault-level` skill that computes prospective short-circuit current (Ik" + ipk + X/R) at every node in a project's distribution cascade — from HV primary supply through to every final-circuit endpoint — and emits a stable `fault-level` intent contract that `db-layout`, `earthing`, and `cable-sizing` consume.

This is **Item 2** in the 7-item Tier 1 sequence (post runtime-stripping). Calc contract for `calc.iec60909_cascade` was shipped in Item 1; this skill provides the prompts, schemas, evals, examples that drive that tool.

Status target on first release: `beta`. Promotion to `production` gated on running the 9 evals against a production model AND the dedicated `calc.iec60909_cascade` runtime tool existing in the separate runtime project.

## 2. Decisions

| # | Decision | Reasoning |
|---|---|---|
| D1 | **Voltage scope = HV + LV (full IEC 60909)** | User explicitly chose comprehensive scope. Adds 11/22/33 kV primary modelling, transformer Z%, ring main + radial topologies. |
| D2 | **All four source types** (utility / generator / UPS / motor back-feed) | User chose all. Generator subtransient decrement, UPS current-limited contribution, IEC 60909-0 §4.5 induction motor contribution all modelled. |
| D3 | **Hybrid cascade input** — consume db-layout-rollup intent if present; else engineer-declared cascade | Flexible. Two input shapes; both validate. Resolves circular db-layout↔fault-level dependency via WI4 iteration pattern. |
| D4 | **Per-node + per-circuit output granularity** | Maximal detail. ifault_ka_max + ifault_ka_min + ipk + X/R at every cascade node. Drives db-layout selectivity AND earthing ADS check AND breaker IcW check. |
| D5 | Two artefacts shipped together | New `IEC60909/` standards layer (11 files) AND new `fault-level/` skill (44 files) = 55 files. Standards layer is a hard prerequisite. |
| D6 | Match earthing/db-layout pattern | 14-step generator chain; 10 INV invariants in validator; 8 D dimensions in reviewer; rationale block per WI2. |

## 3. Current State

`electrical/fault-level/` does NOT exist yet (no stub folder). Calc contract `shared/calculations/electrical/iec60909-cascade.json` was shipped in Item 1 (this Tier 1 sequence, commit `34e28e7`).

**Standards-layer gap:** `shared/standards/electrical/IEC60909/` does NOT exist yet. Only LV adiabatic content exists (`BS7671/reg434-fault-current.json`, `IEC60364/fault-current.json`). The 11-file IEC 60909 standards layer is part of this work, not a separate sub-project.

**Cross-skill open contract:** `electrical/db-layout/skill.manifest.json` already declares `consumes_intents: ["fault-level", "lighting-layout"]` — the consumer side of the contract exists, this skill provides the producer side.

## 4. Architecture

Six layers under `electrical/fault-level/`:

1. **Skill-level metadata** — README, CHANGELOG, skill.manifest.json, inputs.json (WI1 discovery taxonomy)
2. **Prompts** — generator.md (14-step chain), validator.md, reviewer.md
3. **Schemas** — fault-level-ir.schema.json (full IR), fault-level-intent.schema.json (stable downstream subset)
4. **Engineering rules/constraints/validation** — 5 rules + 4 constraints + 4 validation YAMLs
5. **Ontology + docs** — source-types.json, cascade-node-kinds.json, engineering-philosophy + known-limitations
6. **Evals + examples** — 9 evals (all 6 WI5 categories + 3 skill-specific), 3 worked examples

**Cross-drawing intent contract:**

| Direction | Intent | Purpose |
|---|---|---|
| Produces | `fault-level` | Per-node Ifault values — consumed by db-layout (selectivity), earthing (ADS check), cable-sizing (adiabatic), generator-sizing |
| Consumes | `db-layout-rollup` | Cascade topology — boards[] tree + outgoing_circuits[]. Optional (engineer-declared cascade is the fallback). |

## 5. File Set (~55 files)

### 5a. New standards layer (11 files)

```
shared/standards/electrical/IEC60909/
├── README.md
├── meta.json
├── terminology.md
├── compliance-checklist.md
├── amendments-summary.md
├── part0-fundamentals.json          # Ik" definition, c-factor, near/far-from-generator
├── part0-method.md                  # step-by-step calculation walkthrough
├── peak-factor-kappa.json           # κ formula + table by X/R
├── source-impedances.json           # utility / transformer / generator / UPS / motor
├── transformer-zpu-table.json       # typical Zpu by kVA rating
├── generator-subtransient-tables.json # X"d, X'd, Xd by machine type
├── motor-contribution-rules.json    # IEC 60909-0 §4.5 induction motor
└── voltage-factor-c.json            # c=1.05 max / 0.95 min selection
```

### 5b. New skill (44 files)

```
electrical/fault-level/
├── README.md, CHANGELOG.md, skill.manifest.json, inputs.json   [4]
├── prompts/
│   ├── generator.md          (14-step reasoning chain)
│   ├── validator.md          (10 INV invariants)
│   └── reviewer.md           (8 D dimensions)                  [3]
├── schemas/
│   ├── fault-level-ir.schema.json
│   └── fault-level-intent.schema.json                          [2]
├── rules/
│   ├── source-impedance-defaults.yaml
│   ├── motor-contribution-thresholds.yaml
│   ├── voltage-factor-c-selection.yaml
│   ├── ups-current-limiting.yaml
│   └── peak-factor-kappa.yaml                                  [5]
├── constraints/
│   ├── breaker-icn-vs-ifault.yaml
│   ├── busbar-ipk-vs-cascade-ipk.yaml
│   ├── cable-i2t-vs-cascade.yaml
│   └── source-impedance-bounds.yaml                            [4]
├── validation/
│   ├── cascade-tree-integrity.yaml
│   ├── ifault-monotonicity.yaml
│   ├── tool-call-resolved.yaml
│   └── intent-shape.yaml                                       [4]
├── ontology/
│   ├── source-types.json
│   └── cascade-node-kinds.json                                 [2]
├── docs/
│   ├── engineering-philosophy.md
│   └── known-limitations.md                                    [2]
├── evals/
│   ├── runner-config.json
│   ├── eval-01-uk-domestic-cu-cascade.yaml
│   ├── eval-02-tpn-commercial-with-gen.yaml
│   ├── eval-03-undersized-breaker-trap.yaml
│   ├── eval-04-missing-source-data.yaml
│   ├── eval-05-jurisdiction-us-with-hv.yaml
│   ├── eval-06-rationale-block.yaml
│   ├── eval-07-multi-source-coordination.yaml
│   ├── eval-08-induction-motor-contribution.yaml
│   └── eval-09-intent-shape.yaml                               [10]
└── examples/
    ├── uk-domestic-single-source/    (input.json, reasoning.md, output.json)
    ├── intl-commercial-with-genset/  (input.json, reasoning.md, output.json)
    └── us-industrial-with-motors/    (input.json, reasoning.md, output.json)  [9]
```

**Total: 11 standards-layer + 44 skill = 55 files.**

## 6. 14-Step Generator Reasoning Chain

1. **Discovery check** — verify inputs; record consumed intents (db-layout-rollup if present)
2. **Jurisdiction-gated standards file load** — IEC 60909 family (always) + jurisdiction-specific LV references
3. **Cascade topology assembly** — build the tree from db-layout-rollup intent OR engineer-declared JSON; emit path-keyed `node_id`s
4. **HV-side modelling** — engineer-declared PSCC at primary OR network arrangement; apply voltage factor c=1.05 (max) AND c=0.95 (min) per IEC 60909-0 §3.7
5. **Transformer impedance** — Zpu + X/R → Z_tx_ohm = Zpu × (V_LV² / S_tx_kVA)
6. **Generator modelling** — subtransient X"d for first cycle, with decrement profile (X"d → X'd → Xd) per IEC 60909-0 §3.5 near-generator
7. **UPS / inverter modelling** — current-limited: ~2-3× rated for first half-cycle, then bypass-fed
8. **Induction motor contribution** — IEC 60909-0 §4.5 aggregate kVA + rule for inclusion (>5% source kVA threshold)
9. **Cable impedance per cascade stage** — R + jX from tables (BS 7671 App 4 Tables 4D5/4F; IEC 60364-5-52 Annex E; NEC Chapter 9 Table 9)
10. **Cascade Ifault computation** — `Ik"_max = c_max × V / (√3 × |Z_total|)`, `Ik"_min = c_min × V / (√3 × |Z_total|)`, `ipk = κ × √2 × Ik"_max`
11. **Tool call dispatch** — declare `calc.iec60909_cascade`; mark `tool_call_pending: true` until runtime executes (skill NEVER inline-computes the cascade math)
12. **Selectivity implications** — for each protective device in the cascade, check `Ifault_at_device ≤ device.icn_ka`; emit `selectivity_implications[*]` with `adequate` + `recommendation`
13. **Compliance flag emission** — breaker under-rated for Ifault → CRITICAL; motor contribution >20% of total → WARNING; HV PSCC declared without c-factor → WARNING; tool call pending → INFO
14. **Emit rationale block** — per WI2 (8 sections + chat_summary)

## 7. Standards Files Consumed (Consumption-Pattern Proof)

Manifest references **specific files, not folders**. ≥20 files total.

**Always loaded (new IEC 60909 layer):**
- `shared/standards/electrical/IEC60909/part0-fundamentals.json`
- `shared/standards/electrical/IEC60909/part0-method.md`
- `shared/standards/electrical/IEC60909/peak-factor-kappa.json`
- `shared/standards/electrical/IEC60909/source-impedances.json`
- `shared/standards/electrical/IEC60909/transformer-zpu-table.json`
- `shared/standards/electrical/IEC60909/generator-subtransient-tables.json`
- `shared/standards/electrical/IEC60909/motor-contribution-rules.json`
- `shared/standards/electrical/IEC60909/voltage-factor-c.json`

**Always loaded (other):**
- `shared/standards/electrical/IEC60617/symbol-index.json`
- `shared/standards/electrical/IEC60617/part7-switchgear.json`

**GB:**
- `shared/standards/electrical/BS7671/reg434-fault-current.json`
- `shared/standards/electrical/BS7671/pscc-determination.md`
- `shared/standards/electrical/BS7671/appendix4-cable-ratings.json` (for R + X per circuit)

**EU/INT:**
- `shared/standards/electrical/IEC60364/fault-current.json`
- `shared/standards/electrical/IEC60364/pscc-determination.md`
- `shared/standards/electrical/IEC60364/part5-52-cable-ratings-copper.json`
- `shared/standards/electrical/IEC60364/part5-52-cable-ratings-aluminium.json`

**US:**
- `shared/standards/electrical/NFPA70/chapter1-general.json` *(covers NEC Article 110 — 110.9 short-circuit current rating)*
- `shared/standards/electrical/NFPA70/art240-overcurrent.json`
- `shared/standards/electrical/NFPA70/ocpd-coordination.json`
- `shared/standards/electrical/NFPA70/chapter9-tables.json` *(Table 9 — cable AC resistance + reactance for cascade impedance)*

**Total: 21 specific files** (8 IEC 60909 + 2 IEC 60617 + 3 GB + 4 EU/INT + 4 US).

## 8. IR Schema Shape

`fault-level-ir.schema.json` — required root fields:

```
drawing_type: const "fault_level_study"
version: semver
meta: { project_id, skill_version, produced_at, consumed_intents[] }
jurisdiction: enum [GB, EU, INT, US]
project_supply: {
  hv_side?: { voltage_kv, network_arrangement, declared_pscc_at_primary_ka, x_over_r_at_primary },
  lv_source: { type, kva, voltage_v, z_percent, x_over_r, near_or_far_from_generator }
}
sources: [ { id, kind, contribution_method, ifault_contribution_ka, decrement_profile } ]
cascade: [
  { node_id, parent_node_id, node_kind, designation,
    feeder: { length_m, csa_mm2_or_awg, material, insulation },
    z_addition_ohm: { r, x },
    ifault_ka_max, ifault_ka_min, ipk_ka, x_over_r_at_node, z_total_ohm,
    tool_call_pending? }
]
selectivity_implications: [
  { breaker_id, breaker_rating_a, breaker_icn_ka, ifault_at_breaker_ka, adequate, recommendation }
]
compliance_summary: { compliant, non_compliance_flags[], assumptions[] }
drawn_as_symbols: string[]
flags: string[]
rationale: $ref shared/schemas/core/rationale.schema.json
```

## 9. Intent Shape

`fault-level-intent.schema.json` — stable downstream-facing subset:

```
{
  project_id,
  source_summary: { type, kva, voltage_v, x_over_r },
  fault_currents: [
    { node_id, node_kind, ifault_ka_max, ifault_ka_min, ipk_ka, x_over_r_ratio, z_total_ohm }
  ],
  intent_version
}
```

Consumed by:
- `db-layout`: resolves `selectivity_results[*].tool_call_pending: true` entries with computed values
- `earthing` (v1.1, optional): cross-validate Ze + R1 + R2 against `node_kind: "board_busbar"` `ifault_ka_min`
- `cable-sizing` (Tier 1 Item 3): adiabatic check uses `ifault_ka_max` at the cable's downstream end
- `generator-sizing` (future): generator Iek dimension from `node_kind: "lv_source"` outputs

## 10. Eval Coverage Matrix

| Eval ID | Category | What it tests |
|---|---|---|
| eval-01-uk-domestic-cu-cascade | happy_path | 100A TN-C-S service, single utility transformer, simple cascade |
| eval-02-tpn-commercial-with-gen | edge_case | 400V TPN MSB + standby genset, transfer-scheme dual-source |
| eval-03-undersized-breaker-trap | validation_trap | MCB Icn 6 kA at a node where cascade Ifault = 12 kA. Generator MUST flag. |
| eval-04-missing-source-data | missing_input | No Z%, no DNO PSCC. Skill must emit tool_call_pending, never invent. |
| eval-05-jurisdiction-us-with-hv | jurisdiction_switch | US 12.47 kV → 480V TPN. NEC 110.9 + 240.86 cited; IEC 60909 math used. |
| eval-06-rationale-block | rationale_block | 8-section taxonomy + clause-cited decisions per WI2 |
| eval-07-multi-source-coordination | skill_specific | Utility + gen + UPS simultaneously (data centre) |
| eval-08-induction-motor-contribution | skill_specific | Industrial site with 500 kW motor load — back-feed material |
| eval-09-intent-shape | skill_specific | Emitted intent satisfies what db-layout's eval-04 consumes |

All 6 WI5 categories + 3 skill-specific.

## 11. Worked Examples

Three examples × `{input.json, reasoning.md, output.json}`:

1. **`examples/uk-domestic-single-source/`** — UK 3-bed semi. 100A TN-C-S service from 500 kVA DNO transformer (~1.5 kA PSCC at service head). Single-source utility only. Cascade: utility → service head → CU → 6 final circuits. Verifies eval-01.

2. **`examples/intl-commercial-with-genset/`** — INT small commercial. 1600 kVA DNO transformer (~25 kA PSCC) + 800 kVA standby gen (~12 kA contribution, near-generator decrement). ATS coordination between utility + gen modes. Cascade: utility/gen → MSB → 3 sub-DBs → final circuits. Verifies eval-02 + eval-07.

3. **`examples/us-industrial-with-motors/`** — US 480V TPN, 12.47 kV HV primary, 2500 kVA transformer (~35 kA PSCC). 500 kW total motor load (material back-feed per IEC 60909-0 §4.5). NEMA panelboards + MCC. Cascade: HV → TX → MSB → MCC + 3 sub-DBs. Verifies eval-05 + eval-08.

## 12. Cross-References

- `electrical/db-layout` (v1.0.0 beta) — primary downstream consumer. fault-level intent resolves db-layout's `selectivity_results[*].tool_call_pending: true` entries.
- `electrical/earthing` (v1.0.0 beta) — optional consumer at v1.1. Earthing's Zs assumption can be cross-validated against fault-level's per-board Ifault.
- `electrical/cable-sizing` (Tier 1 Item 3, future) — adiabatic check at the cable's downstream Ifault.
- `electrical/lighting-layout` (v1.3.0 production) — no direct dependency.
- `shared/calculations/electrical/iec60909-cascade.json` — the deterministic tool fault-level dispatches (shipped Item 1).

## 13. Out of Scope (v1.0)

- Time-graded HV protection coordination (IDMT relays, definite-time, distance) → separate `protection-coordination` skill, post-Tier 1
- DC fault analysis (PV strings, battery storage, EV DCFC) → `dc-fault-level` skill, post v1.0
- Arc-flash incident energy calculation (IEEE 1584 / NFPA 70E) → separate `arc-flash` skill
- Lightning-induced transients (BS EN 62305 surge / NFPA 780) → separate scope
- HV transformer differential protection — outside building services
- Sub-cycle current flow (DC offset envelope, asymmetry decay) — beyond IEC 60909 scope, requires EMT simulation

## 14. Tool Calls Awaiting Runtime (Per WI3)

| Tool | Purpose | Status |
|---|---|---|
| `calc.iec60909_cascade` | Compute Ik" + ipk + X/R at every cascade node | Contract shipped (Item 1, commit `34e28e7`). tool_call_pending until runtime project implements. |

Per the earthing + db-layout pattern, this skill declares the tool-call contract and accepts engineer-input Ifault values (where present) as fallback. Once the runtime tool exists, fault-level becomes a pure tool-call dispatcher.

## 15. Success Criteria

The skill ships as `status: beta` when:

1. ✅ All 55 files exist (verified via Python file-existence check)
2. ✅ IEC 60909 standards layer (11 files) all on disk
3. ✅ `skill.manifest.json` references ≥20 specific standards files, zero folders (consumption-pattern proof)
4. ✅ All ≥20 referenced standards files exist on disk
5. ✅ Both schemas valid draft-07 (`fault-level-ir.schema.json`, `fault-level-intent.schema.json`)
6. ✅ All 3 example outputs validate against IR schema (with embedded rationale schema)
7. ✅ Emitted intent payload from each example satisfies `fault-level-intent.schema.json` AND structurally matches what db-layout's eval-04 expects to consume
8. ✅ Generator prompt explicitly cites IEC 60909-0 §3 + §4 in Step 2 standards load
9. ✅ All 9 evals registered in `runner-config.json` with no orphans
10. ✅ `calc.iec60909_cascade` tool reference in `produces_intent_schemas` matches the contract at `shared/calculations/electrical/iec60909-cascade.json`

Promotion to `status: production` requires: all 9 evals pass against a production model AND `calc.iec60909_cascade` runtime tool exists in the runtime project.

---

**End of design spec.**
