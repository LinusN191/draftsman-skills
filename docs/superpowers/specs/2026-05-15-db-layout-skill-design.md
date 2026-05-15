# `electrical/db-layout` Skill — v1.0.0 Design Spec

> **Date:** 2026-05-15
> **Status:** Approved for implementation
> **Predecessor:** `electrical/earthing` v1.0.0 (shipped same day; pattern reference)
> **Successor of:** Existing stub at `electrical/db-layout/` (v0.2.0 status=stub with a single drafted intent schema)

---

## 1. Goal

Build a production-grade `electrical/db-layout` skill that produces distribution board schedules, single-line face schematics, and cascade selectivity verification — and emits two stable intent contracts consumed by `earthing`, `cable-containment`, `panel-schedule`, `riser`, and `sld`.

Status target on first release: `beta`. Promotion to `production` gated on running the 8 evals against a production model and meeting all WI5 thresholds AND the dedicated `fault-level` skill landing for selectivity tool-calls.

## 2. Decisions

| # | Decision | Reasoning |
|---|---|---|
| D1 | Stage scope = **schedule + DB schematic + selectivity** | User explicitly chose full scope despite the slice-discipline alternative. ~3-4 sessions, ~43 files. |
| D2 | Jurisdictions = **GB + EU/INT + US** | Match earthing; lets earthing examples consume db-layout intents in all three jurisdictions. |
| D3 | IR granularity = **one board per IR** + **project-rollup intent** | IR is canonical per-board (clean unit boundary). Project rollup is a separate emitted intent for earthing. |
| D4 | Selectivity = **IEC 60909 cascade via `fault-level` intent** | db-layout consumes a `fault-level` intent for fault currents; declares `tool_call_pending` until `fault-level` ships. Cascade lookup uses manufacturer tables + the loaded `fault-current.json` schema. |
| D5 | Two emitted intent types | `db-layout` (single-board, for panel-schedule/riser/cable-containment) AND `db-layout-rollup` (project-wide, for earthing). Manifest's `produces_intent` becomes an array (spec extension). |
| D6 | Match earthing pattern | 13-step generator prompt; 11 INV invariants in validator; 9 D dimensions in reviewer; rationale block per WI2. |

## 3. Current State

`electrical/db-layout/` already exists as a stub with:
- `skill.manifest.json` (status=stub, v0.2.0, no standards, no inputs)
- `schemas/db-layout-intent.schema.json` (single-board shape: `db_id, incoming_supply, circuits, spare_ways, form_separation, icw_ka_1s`)
- Empty subdirectories: `prompts/`, `docs/`, `evals/`, `examples/`

**Open issue:** the earthing skill (shipped same day) emits a `db-layout` intent payload with shape `{boards[], outgoing_circuits[]}` — a project rollup, not a single-board shape. This is reconciled by introducing TWO intent types (D5).

## 4. Architecture

Six layers, all under `electrical/db-layout/`:

1. **Skill-level metadata:** `README.md`, `CHANGELOG.md`, `skill.manifest.json`, `inputs.json` (WI1 discovery taxonomy)
2. **Prompts:** `generator.md` (the 13-step reasoning chain — heart of the skill), `validator.md`, `reviewer.md`
3. **Schemas:** `db-layout-ir.schema.json`, `db-layout-intent.schema.json` (single-board), `db-layout-rollup-intent.schema.json` (project rollup)
4. **Engineering rules/constraints/validation:** 4 rules YAMLs, 3 constraints YAMLs, 4 validation YAMLs
5. **Ontology + docs:** `board-types.json`, `ocpd-types.json`, engineering-philosophy + known-limitations
6. **Evals + examples:** 8 evals (covers all WI5 categories + selectivity + intent-rollup-shape), 3 worked examples (UK + INT + US)

**Cross-drawing intent contract:**

| Direction | Intent | Producer / Consumer |
|---|---|---|
| Produces | `db-layout` | Single-board intent — consumed by `panel-schedule`, `riser`, `cable-containment` |
| Produces | `db-layout-rollup` | Project rollup intent — consumed by `earthing` |
| Consumes | `fault-level` | Prospective fault currents for selectivity (when that skill ships) |

## 5. File Set (43 files)

```
electrical/db-layout/
├── README.md                                 # rewrite
├── CHANGELOG.md                              # new
├── skill.manifest.json                       # rewrite (produces_intent array)
├── inputs.json                               # new — WI1 discovery taxonomy
├── prompts/
│   ├── generator.md                          # new — 13-step reasoning chain
│   ├── validator.md                          # new — 11 INV invariants
│   └── reviewer.md                           # new — 9 D dimensions
├── schemas/
│   ├── db-layout-ir.schema.json              # new — single-board IR
│   ├── db-layout-intent.schema.json          # existing → refine
│   └── db-layout-rollup-intent.schema.json   # new — project rollup
├── rules/
│   ├── ocpd-coordination.yaml                # In ≤ Iz ≤ Iz_corrected by jurisdiction
│   ├── busbar-sizing.yaml                    # busbar ≥ sum × diversity
│   ├── form-separation.yaml                  # IEC 61439 Form 1…4b selection
│   └── rcd-grouping.yaml                     # RCBO vs grouped RCD per jurisdiction
├── constraints/
│   ├── breaker-breaking-capacity.yaml        # Icn ≥ Ifault at install point
│   ├── busbar-icw.yaml                       # busbar 1-sec withstand ≥ Ipk
│   └── ip-rating-by-location.yaml            # IP code by environment
├── validation/
│   ├── ocpd-coordination.yaml                # deterministic In / Iz checks
│   ├── busbar-loading.yaml                   # sum circuits vs busbar rating
│   ├── selectivity-results.yaml              # every cascade pair has verdict or tool_call_pending
│   └── intent-rollup-shape.yaml              # rollup matches earthing's expected fields verbatim
├── ontology/
│   ├── board-types.json                      # CU / DB / MSB / panelboard / MCC / motor-DB
│   └── ocpd-types.json                       # MCB / MCCB / ACB / fuse / RCBO
├── docs/
│   ├── engineering-philosophy.md
│   └── known-limitations.md
├── evals/
│   ├── runner-config.json
│   ├── eval-01-uk-domestic-cu-tn-cs.yaml         # happy_path
│   ├── eval-02-tpn-commercial-msb.yaml           # edge_case
│   ├── eval-03-undersized-busbar-trap.yaml       # validation_trap
│   ├── eval-04-missing-fault-current.yaml        # missing_input
│   ├── eval-05-jurisdiction-us-panelboard.yaml   # jurisdiction_switch
│   ├── eval-06-rationale-block.yaml              # rationale_block
│   ├── eval-07-selectivity-cascade.yaml          # skill_specific (selectivity dimension)
│   └── eval-08-intent-rollup-shape.yaml          # skill_specific (cross-skill contract)
└── examples/
    ├── uk-domestic-consumer-unit/    # input.json, reasoning.md, output.json
    ├── intl-commercial-tpn-msb/      # input.json, reasoning.md, output.json
    └── us-strip-mall-panelboard/     # input.json, reasoning.md, output.json
```

**Total: 43 files** — 4 skill-level (README, CHANGELOG, manifest, inputs.json) + 3 prompts + 3 schemas + 4 rules + 3 constraints + 4 validation + 2 ontology + 2 docs + 9 eval files (runner-config + 8 evals) + 9 example files (3 examples × 3 files each).

## 6. 13-Step Generator Reasoning Chain

The generator prompt walks every IR production through these steps in order:

1. **Discovery** — verify inputs.json answers + cross_drawing_context (fault-level if present)
2. **Jurisdiction-gated standards file load** — see § 7
3. **Board classification** — CU / DB / MSB / panelboard (from `inputs.board_type` + jurisdiction)
4. **Incoming supply specification** — voltage, phases, supply rating, Ze at origin, fed_from
5. **Busbar sizing** — sum of way loads × diversity (per jurisdiction); IcW must exceed Ipk from fault-level
6. **Way assignment** — number of ways, used, spare; module pitch (per IEC 61439 / NEMA standard)
7. **OCPD per circuit** — rating, curve, type, breaking capacity (per `ocpd-coordination.yaml` + `breaker-breaking-capacity.yaml`)
8. **RCD assignment** — required, type, sensitivity (per jurisdiction RCD rules from earthing's references)
9. **Cable per circuit** — CSA, cores, length (consumed from db-layout's own inputs or upstream `lighting-layout` / `small-power` intent if present)
10. **DB face schematic** — emit IEC 60617 symbols for incoming, busbar, ways, RCD grouping
11. **Selectivity verification** — cascade analysis (manufacturer-table lookup OR IEC 60909 calc OR `tool_call_pending`)
12. **Compliance flag emission** — non-compliance flags + assumptions; emit `flags[]` at IR root
13. **Emit rationale block** (per WI2) — 9-section taxonomy + chat_summary

## 7. Standards Files Consumed (Consumption-Pattern Proof)

Per the pattern shipped in earthing: the manifest's `standards` array references **specific files, not folders**. The validator asserts zero folders, ≥ 19 files.

**Always loaded (regardless of jurisdiction):**
- `shared/standards/electrical/IEC60617/symbol-index.json`
- `shared/standards/electrical/IEC60617/part7-switchgear.json`
- `shared/standards/electrical/IEC61439/form-separations.json`
- `shared/standards/electrical/IEC61439/ip-ik-ratings.json`
- `shared/standards/electrical/IEC61439/short-circuit-withstand.json`

**GB (jurisdiction-gated):**
- `shared/standards/electrical/BS7671/reg433-overcurrent-protection.json`
- `shared/standards/electrical/BS7671/reg434-fault-current.json`
- `shared/standards/electrical/BS7671/reg443-spd.json`
- `shared/standards/electrical/BS7671/reg411-rcd-requirements.json`
- `shared/standards/electrical/BS7671/appendix3-device-curves.json`
- `shared/standards/electrical/BS7671/diversity-factors.json`

**EU / INT (jurisdiction-gated):**
- `shared/standards/electrical/IEC60364/part4-43-overcurrent.json`
- `shared/standards/electrical/IEC60364/part4-44-overvoltage.json`
- `shared/standards/electrical/IEC60364/rcd-requirements.json`
- `shared/standards/electrical/IEC60364/device-curves.json`
- `shared/standards/electrical/IEC60364/diversity-factors.json`
- `shared/standards/electrical/IEC60364/fault-current.json`

**US (jurisdiction-gated):**
- `shared/standards/electrical/NFPA70/art408-panelboards.json`
- `shared/standards/electrical/NFPA70/art240-overcurrent.json`
- `shared/standards/electrical/NFPA70/art220-load-calculations.json`
- `shared/standards/electrical/NFPA70/ocpd-coordination.json`

**Total: 19 specific files** (5 always + 6 GB + 6 EU/INT + 4 US).

## 8. IR Schema Shape

`db-layout-ir.schema.json` — required root fields:

```
drawing_type: const "db_layout_schedule_and_schematic"
version: semver
meta: { project_id, skill_version, produced_at, consumed_intents[] }
jurisdiction: enum [GB, EU, INT, US]
board: { db_id, designation, location, enclosure_form_iec61439, ip_rating, ways_total, ways_used, ways_spare }
incoming: { voltage_v, phase_arrangement, supply_rating_a, fed_from, supply_class, ze_ohm_at_origin }
busbar: { rating_a, icw_ka_1s, ipk_ka }
circuits: [ { circuit_id, way_module_id, designation, ocpd: {...}, rcd: {...}, cable: {...}, downstream_load_kw, voltage_class } ]
selectivity_results: [ { upstream_id, downstream_id, selective_to_fault_ka, source, tool_call_pending } ]
drawn_as_symbols: string[]   # IEC 60617 symbol IDs validated against symbol-index.json
compliance_summary: { compliant, non_compliance_flags[], assumptions[] }
drawing_notes: string[]
flags: string[]
rationale: $ref shared/schemas/core/rationale.schema.json
```

## 9. Intent Shapes

**`db-layout-intent.schema.json` (single board, refined from existing stub):**
- Required: `db_id, incoming_supply, circuits`
- Optional: `spare_ways, form_separation, icw_ka_1s, supply_class`
- Consumed by `panel-schedule`, `riser`, `cable-containment`

**`db-layout-rollup-intent.schema.json` (project rollup, new):**
- Required: `project_id, boards[], outgoing_circuits[]`
- Each board: `id, designation, location, phases, ways, main_switch_rating_a, main_switch_type`
- Each outgoing circuit: `id, designation, ocpd_rating_a, ocpd_type, phase_csa_mm2_or_awg, length_m, db_designation`
- **This shape matches verbatim the earthing skill's expected payload (verified against `electrical/earthing/examples/uk-dwelling-tn-cs/input.json`).**
- Consumed by `earthing`

## 10. Eval Coverage Matrix

| Eval ID | Category | What it tests |
|---|---|---|
| eval-01-uk-domestic-cu-tn-cs | happy_path | 230V 1ph, 12-way CU, 6 final circuits. TN-C-S. Both intents emitted correctly. |
| eval-02-tpn-commercial-msb | edge_case | 400V TPN MSB → 4 sub-DBs. Form 4b. IcW selectivity check. |
| eval-03-undersized-busbar-trap | validation_trap | Engineer declares busbar 200A but ∑ ways > 200A. Must flag, not accept silently. |
| eval-04-missing-fault-current | missing_input | No fault-level intent, no engineer Ifault. selectivity_results must mark tool_call_pending. |
| eval-05-jurisdiction-us-panelboard | jurisdiction_switch | NFPA 70 Art 408 panelboard, NEC terms (panelboard, EGC), Table 250.122 EGC sizing. No BS 7671 citations. |
| eval-06-rationale-block | rationale_block | 9-section taxonomy + clause citations per WI2. |
| eval-07-selectivity-cascade | skill_specific | Two-level cascade (MSB → sub-DB → final). Manufacturer-table lookup verified. |
| eval-08-intent-rollup-shape | skill_specific | Rollup intent payload structurally validates against `earthing` example expectation. |

All 6 WI5 categories plus 2 skill-specific tests = 8 evals (≥ earthing's 6).

## 11. Worked Examples

Each = `{input.json, reasoning.md, output.json}` (output is one IR per board; rollup intent emitted at IR root for the example's project).

1. **`examples/uk-domestic-consumer-unit/`** — 3-bed semi-detached, 100A TN-C-S main, 12-way Type B consumer unit, 6 final circuits (lighting × 2, sockets × 2, cooker, shower). Verifies eval-01.

2. **`examples/intl-commercial-tpn-msb/`** — Small commercial: 400V TPN MSB with 4 sub-DBs (lighting, small-power, mechanical, fire). Form 4b enclosure. IEC 61439 verification. Verifies eval-02 + eval-07.

3. **`examples/us-strip-mall-panelboard/`** — 200A 120/240V split-phase, NEMA panelboard, 4 dedicated circuits (general lighting, general receptacles, RTU HVAC, reach-in cooler). NEC Art 408. Verifies eval-05.

## 12. Cross-References

- **`electrical/earthing` (v1.0.0 beta)** — consumes `db-layout-rollup` intent. Existing examples already declare the expected payload shape; this skill produces it verbatim.
- **`electrical/lighting-layout` (v1.3.0 production)** — produces `lighting-layout` intent which db-layout MAY consume to source circuit lengths and luminaire loads (Step 9 in generator).
- **Planned `electrical/fault-level`** — produces `fault-level` intent that db-layout consumes for selectivity (Step 11). Until that ships, selectivity emits `tool_call_pending: true`.
- **Planned `electrical/panel-schedule`** — consumes the single-board `db-layout` intent.

## 13. Out of Scope (Stage 1)

- IT systems (medical Group 2) — deferred (same as earthing v1.0.0).
- Standby generator distribution (NEC 250.30 / BS 7671 Chapter 55).
- Motor control center (MCC) full I/O schedule — db-layout v1.0.0 lists motor circuits but does not draw the MCC compartment internals.
- Plan-view DB location drawing — IR is schedule + face schematic only.
- DC distribution (PV, EV chargepoints) — deferred to v1.1.0 with `art690-solar-pv.json` + `art625-ev-charging.json`.
- Live IEC 60909 calculation — declared as a tool-call contract; engineer-input fault currents accepted with `tool_call_pending` flag until `fault-level` skill ships.

## 14. Tool Calls Awaiting Runtime (Per WI3)

| Tool | Purpose | Status |
|---|---|---|
| `calc.iec60909_cascade` | Compute Ifault at each level of the cascade | tool_call_pending (deferred until `fault-level` skill) |
| `calc.diversity_factor` | Apply diversity factor to mains sizing from standards | tool_call_pending |

Per the earthing pattern, the skill declares the tool-call contract and accepts engineer-input values with `tool_call_pending: true` until the deterministic Python runtime tool is available.

## 15. Success Criteria

The skill is ready for `status: beta` when:

1. ✅ All 50 files exist (verified via Python file-existence check)
2. ✅ `skill.manifest.json` references 19 specific standards files, zero folders (consumption-pattern proof)
3. ✅ All 19 referenced standards files exist on disk
4. ✅ Both schemas valid draft-07 (`db-layout-ir.schema.json`, both intent schemas)
5. ✅ All 3 example outputs validate against IR schema (with embedded rationale schema)
6. ✅ Rollup intent payload from each example structurally matches earthing's expected shape
7. ✅ Generator prompt explicitly cites all 19 standards files in Step 2
8. ✅ `cpc_sizing_method`-like enum consistency across schema + generator + rules + validation + examples (no enum drift)
9. ✅ All 8 evals registered in `runner-config.json` with no orphans

Promotion to `status: production` requires: all 8 evals pass against a production model AND `fault-level` skill exists for selectivity tool-call execution.

---

**End of design spec.**
