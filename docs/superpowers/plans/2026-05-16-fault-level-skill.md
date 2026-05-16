# `electrical/fault-level` Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `electrical/fault-level` skill (v1.0.0 beta) — produces IEC 60909 prospective fault current cascade IR (HV+LV) for any node in a project's distribution tree; emits the stable `fault-level` intent that resolves db-layout's selectivity tool_call_pending entries.

**Architecture:** Two coordinated artefact sets shipped together as a single coherent change:
- **Phase A (Tasks 1-8):** New `shared/standards/electrical/IEC60909/` standards layer — 11 files implementing IEC 60909-0:2016 method (fundamentals, peak-factor κ, voltage-factor c, transformer Zpu, generator subtransient, motor contribution).
- **Phase B (Tasks 9-35):** `electrical/fault-level/` skill — 44 files matching the artefact pattern proven in `electrical/earthing` and `electrical/db-layout` (just shipped). 14-step generator chain. Two schemas (full IR + slim intent). 9 evals across all 6 WI5 categories + 3 skill-specific.

**Tech Stack:** JSON Schema (draft-07), YAML, Python 3 (`jsonschema` + `PyYAML` already installed). Calc contract `calc.iec60909_cascade` already shipped at `shared/calculations/electrical/iec60909-cascade.json` (commit `34e28e7`). No runtime code — pure declarative artefacts.

**Reference predecessors:**
- `electrical/lighting-layout` (v1.3.0 production — top-level pattern)
- `electrical/earthing` (v1.0.0 beta — sibling, identical artefact set structure)
- `electrical/db-layout` (v1.0.0 beta — primary downstream consumer of fault-level intent)
- Plans: `docs/superpowers/plans/2026-05-15-earthing-skill.md`, `docs/superpowers/plans/2026-05-15-db-layout-skill.md`

---

## File Structure Overview

```
shared/standards/electrical/IEC60909/         (Phase A — Tasks 1-8, 11 files)
├── README.md                                 (Task 1)
├── meta.json                                 (Task 1)
├── terminology.md                            (Task 2)
├── amendments-summary.md                     (Task 2)
├── part0-fundamentals.json                   (Task 3, Ik" + c + near/far)
├── part0-method.md                           (Task 4, step-by-step)
├── peak-factor-kappa.json                    (Task 5)
├── voltage-factor-c.json                     (Task 5)
├── source-impedances.json                    (Task 6)
├── transformer-zpu-table.json                (Task 6)
├── generator-subtransient-tables.json        (Task 7)
├── motor-contribution-rules.json             (Task 7)
└── compliance-checklist.md                   (Task 8)

electrical/fault-level/                       (Phase B — Tasks 9-35, 44 files)
├── README.md                                 (Task 34)
├── CHANGELOG.md                              (Task 9)
├── skill.manifest.json                       (Task 13)
├── inputs.json                               (Task 12)
├── prompts/
│   ├── generator.md                          (Task 16, 14-step chain)
│   ├── validator.md                          (Task 17, 10 INV invariants)
│   └── reviewer.md                           (Task 18, 8 D dimensions)
├── schemas/
│   ├── fault-level-ir.schema.json            (Task 10)
│   └── fault-level-intent.schema.json        (Task 11)
├── rules/
│   ├── source-impedance-defaults.yaml        (Task 14)
│   ├── motor-contribution-thresholds.yaml    (Task 14)
│   ├── voltage-factor-c-selection.yaml       (Task 14)
│   ├── ups-current-limiting.yaml             (Task 14)
│   └── peak-factor-kappa.yaml                (Task 14)
├── constraints/
│   ├── breaker-icn-vs-ifault.yaml            (Task 15)
│   ├── busbar-ipk-vs-cascade-ipk.yaml        (Task 15)
│   ├── cable-i2t-vs-cascade.yaml             (Task 15)
│   └── source-impedance-bounds.yaml          (Task 15)
├── validation/
│   ├── cascade-tree-integrity.yaml           (Task 19)
│   ├── ifault-monotonicity.yaml              (Task 19)
│   ├── tool-call-resolved.yaml               (Task 19)
│   └── intent-shape.yaml                     (Task 19)
├── ontology/
│   ├── source-types.json                     (Task 20)
│   └── cascade-node-kinds.json               (Task 20)
├── docs/
│   ├── engineering-philosophy.md             (Task 21)
│   └── known-limitations.md                  (Task 21)
├── evals/
│   ├── runner-config.json                    (Task 22)
│   ├── eval-01-uk-domestic-cu-cascade.yaml         (Task 22, happy_path)
│   ├── eval-02-tpn-commercial-with-gen.yaml        (Task 23, edge_case)
│   ├── eval-03-undersized-breaker-trap.yaml        (Task 24, validation_trap)
│   ├── eval-04-missing-source-data.yaml            (Task 25, missing_input)
│   ├── eval-05-jurisdiction-us-with-hv.yaml        (Task 26, jurisdiction_switch)
│   ├── eval-06-rationale-block.yaml                (Task 27, rationale_block)
│   ├── eval-07-multi-source-coordination.yaml      (Task 28, skill_specific)
│   ├── eval-08-induction-motor-contribution.yaml   (Task 29, skill_specific)
│   └── eval-09-intent-shape.yaml                   (Task 30, skill_specific)
└── examples/
    ├── uk-domestic-single-source/            (Task 31)
    ├── intl-commercial-with-genset/          (Task 32)
    └── us-industrial-with-motors/            (Task 33)
```

Final verification + SKILLS_STATUS update: Task 35.

## Validation Conventions

After each JSON/YAML file write, run:
```bash
python3 -c "import json; json.load(open('<path>'))" && echo OK   # for JSON
python3 -c "import yaml; yaml.safe_load(open('<path>'))" && echo OK   # for YAML
```

For schema validation, use the existing earthing/db-layout idiom — inline the rationale schema to bypass `$ref` resolver issues:
```python
import json
from jsonschema import Draft7Validator
ir_schema = json.load(open('electrical/fault-level/schemas/fault-level-ir.schema.json'))
rationale_schema = json.load(open('shared/schemas/core/rationale.schema.json'))
ir_no_id = dict(ir_schema)
ir_no_id.pop('$id', None)
ir_no_id['properties']['rationale'] = rationale_schema
Draft7Validator(ir_no_id).validate(json.load(open('example/output.json')))
```

---

# PHASE A — IEC 60909 Standards Layer (Tasks 1-8)

## Task 1: Create IEC60909 folder + README + meta.json

**Files:**
- Create: `shared/standards/electrical/IEC60909/README.md`
- Create: `shared/standards/electrical/IEC60909/meta.json`

- [ ] **Step 1: Create the folder and write README**

```bash
mkdir -p shared/standards/electrical/IEC60909
```

```markdown
# IEC 60909 — Short-Circuit Currents in Three-Phase AC Systems

**Status:** v1.0.0 beta
**Released:** 2026-05-16
**Primary consumer:** `electrical/fault-level` skill v1.0.0

## Standard

IEC 60909-0:2016 — Calculation of currents. The international reference for prospective short-circuit current calculation. Used by:
- Switchgear breaking-capacity (IEC 60947, IEC 60898) verification
- Cable adiabatic protection (IEC 60364-4-43, BS 7671 Reg 434)
- Selectivity coordination (IEC 60364-5-53, BS 7671 Reg 536)

## What this layer covers

- Fundamental method (§3): Ik" symmetrical initial short-circuit current, voltage factor c
- Peak current (§4.3): ipk via κ factor per IEC 60865-1
- Source impedance modelling: utility / transformer / generator / UPS / motor (§4.2 - §4.5)
- Near-generator decrement (§3.5)
- Far-from-generator constant-source (§3.4)
- Multi-source superposition (§3.6)

## What this layer does NOT cover

- IEEE 1584 arc-flash (separate `arc-flash` skill scope)
- Time-graded protection coordination (separate `protection-coordination` skill scope)
- DC fault analysis (PV strings, battery storage — separate skill)
- HV transformer differential protection (out of building-services scope)

## Loaded by

- `electrical/fault-level/skill.manifest.json` (primary)
- `electrical/db-layout/skill.manifest.json` (cross-reference for cascade context)
- Other skills consuming `fault-level` intent: earthing, cable-sizing, generator-sizing

## Files

| File | Purpose |
|---|---|
| `part0-fundamentals.json` | Core definitions: Ik", c-factor, near/far-from-generator classification |
| `part0-method.md` | Step-by-step IEC 60909-0 calculation method |
| `peak-factor-kappa.json` | κ peak factor formula + table by X/R ratio |
| `voltage-factor-c.json` | c=1.05 (Ik"max) and c=0.95 (Ik"min) selection rules |
| `source-impedances.json` | Unified source-impedance reference (utility/TX/gen/UPS/motor) |
| `transformer-zpu-table.json` | Typical Zpu values by transformer kVA |
| `generator-subtransient-tables.json` | X"d, X'd, Xd by machine type and rating |
| `motor-contribution-rules.json` | IEC 60909-0 §4.5 induction motor short-circuit contribution |
| `compliance-checklist.md` | Verification checklist for fault-level study deliverables |
| `terminology.md` | Glossary aligning IEC 60909 terms with BS 7671 / NEC equivalents |
| `amendments-summary.md` | Notes on IEC 60909-0:2016 amendments + national derivations |
```

- [ ] **Step 2: Write meta.json**

```json
{
  "standard": "IEC 60909-0",
  "title": "Short-circuit currents in three-phase AC systems — Calculation of currents",
  "publisher": "IEC (International Electrotechnical Commission)",
  "edition": "Edition 3.0",
  "publication_year": 2016,
  "version_tag": "IEC 60909-0:2016",
  "jurisdiction_scope": ["GB", "EU", "INT", "US"],
  "us_alignment": "NEC 110.9 (Interrupting Rating) + 240.86 (Series Ratings) cite IEC 60909 as the method for cascade calculation",
  "related_standards": [
    "IEC 60909-1:2002 (Factors for calculating short-circuit currents)",
    "IEC 60909-2:2008 (Data of electrical equipment for calculation)",
    "IEC 60909-3:2009 (Currents during two separate simultaneous short-circuits)",
    "IEC 60909-4:2000 (Examples for calculation of short-circuit currents)",
    "IEC 60865-1:2011 (Effects of short-circuit currents — calculation peak factor κ)"
  ],
  "primary_application": "Calculation of prospective short-circuit current (Ik\", ipk) for breaker selection, cable adiabatic protection, selectivity coordination",
  "version": "1.0.0",
  "layer_status": "beta"
}
```

- [ ] **Step 3: Validate JSON syntax + commit**

```bash
python3 -c "import json; json.load(open('shared/standards/electrical/IEC60909/meta.json'))" && echo OK
git add shared/standards/electrical/IEC60909/README.md shared/standards/electrical/IEC60909/meta.json
git commit -m "feat: IEC60909 standards layer — README + meta.json (Phase A start)"
```

---

## Task 2: terminology.md + amendments-summary.md

**Files:**
- Create: `shared/standards/electrical/IEC60909/terminology.md`
- Create: `shared/standards/electrical/IEC60909/amendments-summary.md`

- [ ] **Step 1: Write terminology.md**

```markdown
# IEC 60909 Terminology — Cross-Reference

Glossary aligning IEC 60909 terms with BS 7671 / NEC equivalents used in `electrical/fault-level` and downstream skills.

## Core terms

| IEC 60909 Term | Symbol | Unit | BS 7671 Equivalent | NEC Equivalent | Description |
|---|---|---|---|---|---|
| Initial symmetrical short-circuit current | Ik" | A (kA) | PSCC (prospective short-circuit current) | Available fault current | RMS value of the AC symmetrical component at instant of fault |
| Peak short-circuit current | ipk | A (kA) | i_p, peak fault current | Peak short-circuit current | First-cycle maximum instantaneous value |
| Voltage factor | c | dimensionless | — | — | 1.05 for Ik"max; 0.95 for Ik"min; per Table 1 |
| Peak factor | κ (kappa) | dimensionless | — | — | ipk / (√2 × Ik"); depends on R/X |
| Near-from-generator | NG | — | — | — | Synchronous machine within calculation path with declining contribution |
| Far-from-generator | FG | — | — | — | Source contribution stays constant over fault duration |
| Per-unit impedance | Zpu | % or pu | — | — | Transformer impedance referenced to its rated capacity |
| Symmetrical breaking current | Ib | A (kA) | Icn (breaking capacity) | Interrupting Rating | RMS at instant of contact separation |
| Steady-state short-circuit current | Ik | A (kA) | — | — | RMS at end of transient |

## Source contribution terms

| Term | Symbol | Description |
|---|---|---|
| Synchronous generator subtransient reactance | X"d | First-cycle reactance, smallest |
| Synchronous generator transient reactance | X'd | Reactance after subtransient decay, ~100ms |
| Synchronous generator synchronous reactance | Xd | Steady-state reactance, ~seconds |
| Induction motor locked-rotor reactance | X"M | First-cycle motor back-feed reactance |
| Transformer short-circuit impedance | Zk | Equivalent positive-sequence impedance referred to rated voltage |
| Network feeder impedance | ZQ | Equivalent network impedance from feeder substation perspective |

## Calculation method terms

| Term | Description |
|---|---|
| Equivalent voltage source method | The IEC 60909 method: replace all active sources with a single equivalent EMF c × Un at fault point |
| Voltage factor c_max | 1.05 (LV systems with Un ≥ 100 V); for maximum Ik" — drives breaker rating verification |
| Voltage factor c_min | 0.95 (LV systems with Un ≥ 100 V); for minimum Ik" — drives ADS protection setting verification |
| Source path | Series chain of impedances from supply to fault location |

## Jurisdiction-specific terms

**UK (BS 7671):** "PSCC" (prospective short-circuit current) maps to Ik". UK practice typically uses LV TN-C-S Ze (declared by DNO) as a shortcut to derive PSCC at the LV service.

**EU/INT (IEC 60364):** IEC 60909 terminology used directly. Ik" + ipk are the standard reporting values for switchgear and protection sizing.

**US (NEC):** "Available fault current" maps to Ik". NEC 110.9 requires equipment to be rated for the available fault current. NEC 110.24 requires marking of available fault current on service equipment.
```

- [ ] **Step 2: Write amendments-summary.md**

```markdown
# IEC 60909-0:2016 — Amendments and National Derivations

## Edition history

- **IEC 60909-0:1988** — first edition, three-phase symmetrical short-circuit calculation
- **IEC 60909-0:2001** — Edition 2.0, expanded to cover unbalanced faults
- **IEC 60909-0:2016** — Edition 3.0 (current), refined induction motor contribution, voltage factor c clarifications

## Key 2016 amendments

- **§3.5 near-from-generator** — clarified subtransient time interval to first peak (≤10 ms)
- **§4.2 voltage factor c** — Table 1 updated to align with IEC 60038 (Standard voltages) Edition 7
- **§4.5 induction motor contribution** — threshold tightened: motors with sum ≥ 1% of supply Sk" must be considered
- **Annex A** — equivalent voltage source method now mandatory for short-circuits supplied by interconnected meshed networks

## National derivations / equivalents

### UK (BS 7671:2018+A3)

- Reg 434.5: Adiabatic protection check uses Ik" per IEC 60909
- App 3 device curves: time-current characteristic verified at Ik" computed per IEC 60909
- IET commentary: UK practice in dwellings typically uses DNO-declared Ze + an X/R ratio of 1.0 (resistive supply assumption) — IEC 60909 method preserves this as a limiting case

### EU (IEC 60364)

- IEC 60364-4-43 cites IEC 60909 directly for cable adiabatic protection
- IEC 60364-5-53 cites IEC 60909 for selectivity coordination
- National CENELEC HDs add minor formatting differences but the method is preserved

### US (NFPA 70 / NEC)

- NEC 110.9: equipment "interrupting rating sufficient for the available fault current" — IEC 60909 Ik" is the calculation method accepted by AHJs
- NEC 110.24: marking of available fault current at service equipment — typically computed per IEEE 141 (Red Book) which converges with IEC 60909 for utility-source cases
- NEC 240.86: series ratings — IEC 60909 cascade method aligns with the series-rating verification path
- NEC Chapter 9 Table 9 provides R + X for ac-rated conductors (used in this skill's Step 9 cable impedance lookup)

## Cross-skill alignment

- `electrical/db-layout` v1.0.0 — `selectivity_results[*].source` enum includes `"iec_60909_calc"` to record when fault-level (via this layer) was the basis
- `electrical/earthing` v1.0.0 — accepts engineer-declared Ze (DNO PME convention) OR a fault-level intent reference; future v1.1 will cross-validate against this layer
```

- [ ] **Step 3: Validate + commit**

```bash
test -s shared/standards/electrical/IEC60909/terminology.md && \
test -s shared/standards/electrical/IEC60909/amendments-summary.md && \
echo OK
git add shared/standards/electrical/IEC60909/terminology.md shared/standards/electrical/IEC60909/amendments-summary.md
git commit -m "feat: IEC60909 terminology + amendments summary"
```

---

## Task 3: part0-fundamentals.json

**Files:**
- Create: `shared/standards/electrical/IEC60909/part0-fundamentals.json`

The canonical reference for Ik" definition + voltage factor c + near/far-from-generator classification.

- [ ] **Step 1: Write the file**

```json
{
  "_title": "IEC 60909-0:2016 §3 — Fundamentals of Short-Circuit Current Calculation",
  "_version": "1.0.0",
  "_basis": "IEC 60909-0:2016 Edition 3.0 §3.1–§3.7, Annex A (equivalent voltage source method)",

  "ik_doubleprime_definition": {
    "name": "Initial symmetrical short-circuit current",
    "symbol": "Ik\"",
    "unit": "A (RMS)",
    "definition": "RMS value of the AC symmetrical component of a prospective (available) short-circuit current at the instant of short-circuit if the impedance retains its value at time zero",
    "formula": "Ik\" = c × Un / (√3 × |Zk|) for three-phase faults",
    "formula_single_phase": "Ik\" = c × Un / (2 × |Zk|) for line-to-line faults",
    "reference": "IEC 60909-0:2016 §3.3"
  },

  "voltage_factor_c": {
    "purpose": "Adjusts nominal voltage Un to account for variations in supply (load voltage drop, tap settings, transformer regulation)",
    "table_1_lv_systems": {
      "_reference": "IEC 60909-0:2016 Table 1",
      "_scope": "Low-voltage systems with Un ≥ 100 V (e.g. 230 V, 400 V, 480 V)",
      "c_max": {
        "value": 1.05,
        "use_for": "Calculation of maximum short-circuit current (Ik\"max) — drives breaker breaking-capacity verification",
        "rationale": "Allows for over-voltage from no-load transformer secondary, normal supply tolerance"
      },
      "c_min": {
        "value": 0.95,
        "use_for": "Calculation of minimum short-circuit current (Ik\"min) — drives protection setting verification (ADS disconnection time)",
        "rationale": "Accounts for under-voltage from supply variation, drop on heavily loaded transformers"
      }
    },
    "table_1_hv_systems": {
      "_scope": "Systems with Un > 1 kV up to 230 kV",
      "c_max": 1.1,
      "c_min": 1.0
    }
  },

  "near_or_far_from_generator": {
    "purpose": "Classifies whether synchronous source contribution changes over fault duration",
    "near_from_generator": {
      "_reference": "IEC 60909-0:2016 §3.5",
      "definition": "Calculation path includes a synchronous machine whose internal voltage decays during the fault (subtransient → transient → steady-state)",
      "applicable_when": [
        "Generator supplies the fault (standby genset, on-site generation)",
        "Synchronous motor contributes via back-EMF"
      ],
      "calculation_basis": "Use subtransient reactance X\"d for first cycle (Ik\"); transient X'd at ~100 ms (Ib); steady-state Xd at long times (Ik)",
      "decrement_factor_mu": "Apply IEC 60909-0 §3.5 decrement factor μ × Ik\" for breaking-current calculation at contact-separation time tmin"
    },
    "far_from_generator": {
      "_reference": "IEC 60909-0:2016 §3.4",
      "definition": "Source contribution stays approximately constant over fault duration (utility transformer, large interconnected network)",
      "applicable_when": [
        "Utility / DNO supply is far enough that source EMF doesn't decay",
        "Building services projects fed from public distribution grid"
      ],
      "calculation_basis": "Ik = Ib = Ik\" (constant source) — no decrement applied"
    },
    "selection_rule": "If ΣP_synchronous_generation > 5% of source Sk\" → use near-from-generator method. Otherwise far-from-generator."
  },

  "equivalent_voltage_source_method": {
    "_reference": "IEC 60909-0:2016 Annex A",
    "principle": "Replace all active EMFs with a single equivalent voltage source c × Un at the fault location. All other generators and motors are replaced with their internal impedances only.",
    "advantages": [
      "Avoids tracking individual source EMFs over time",
      "Compatible with steady-state load-flow analysis tools",
      "Standard accepted by IEC 60909-2 data tables"
    ],
    "computation_steps": [
      "1. Identify fault location and three-phase fault type",
      "2. Build positive-sequence impedance network from each source to fault",
      "3. Apply c × Un at fault → compute Ik\" = c × Un / (√3 × |Z_total|)",
      "4. For peak current: ipk = κ × √2 × Ik\" where κ = 1.02 + 0.98 × exp(-3 R/X)",
      "5. For breaking current (near-from-generator): Ib = μ × Ik\""
    ]
  },

  "fault_types_covered": {
    "_reference": "IEC 60909-0:2016 §1",
    "three_phase_balanced": {
      "description": "Symmetrical three-phase short-circuit",
      "formula": "Ik\"_3ph = c × Un / (√3 × |Zk_positive|)",
      "usage": "Standard breaker breaking-capacity verification; usually the highest current case"
    },
    "line_to_line": {
      "description": "Two-phase short-circuit (no earth contact)",
      "formula": "Ik\"_2ph = (√3 / 2) × Ik\"_3ph (when only positive-sequence considered)"
    },
    "line_to_earth": {
      "description": "Single-phase to earth — used for ADS disconnection time verification",
      "formula": "Ik\"_1ph = c × Un × √3 / |Z1 + Z2 + Z0|",
      "usage": "Earthing systems coordination, ADS check"
    }
  },

  "cross_reference": {
    "method_walkthrough": "part0-method.md",
    "peak_factor": "peak-factor-kappa.json",
    "source_impedances": "source-impedances.json"
  }
}
```

- [ ] **Step 2: Validate + commit**

```bash
python3 -c "import json; json.load(open('shared/standards/electrical/IEC60909/part0-fundamentals.json'))" && echo OK
git add shared/standards/electrical/IEC60909/part0-fundamentals.json
git commit -m "feat: IEC60909 part0-fundamentals.json — Ik\" + c-factor + near/far classification"
```

---

## Task 4: part0-method.md

**Files:**
- Create: `shared/standards/electrical/IEC60909/part0-method.md`

The step-by-step IEC 60909-0 calculation walkthrough — the canonical reference the generator prompt cites in Step 10 (cascade Ifault computation).

- [ ] **Step 1: Write the method walkthrough**

```markdown
# IEC 60909-0:2016 — Calculation Method (Step-by-Step)

This file is the canonical reference for the calculation steps the `electrical/fault-level` generator prompt walks every IR through. The math itself runs in the `calc.iec60909_cascade` runtime tool (per the WI3 deferral pattern); this document tells engineers what the tool does.

## Inputs (preconditions)

Before applying the method, the engineer/skill must know:

1. **Fault location:** every node in the cascade tree where Ik" is needed
2. **Source(s):** utility transformer rating + Zpu OR generator(s) + X"d profile OR UPS rated current + bypass path OR running motor load (for motor back-feed)
3. **Cascade path:** series chain of impedances from each source to each fault point — typically:
   - HV primary (network impedance ZQ if HV supply present)
   - Transformer (Zk referred to LV)
   - LV mains cable (R + jX per length, csa, insulation)
   - Sub-DB feeder cable
   - Final-circuit cable
4. **Voltage factor c:** 1.05 for Ik"max (breaker rating); 0.95 for Ik"min (protection setting)

## Step 1 — Classify the system

**Near-from-generator (NG)** or **Far-from-generator (FG)?**

- If ΣP_synchronous_generation > 5% of source Sk" at the fault → NG method (apply subtransient → transient → steady-state decrement)
- Otherwise FG method (Ik = Ib = Ik", constant source)

Building-services projects fed from public DNO grid are almost always FG. Standby-generator projects switch to NG when on gen.

## Step 2 — Compute source impedance ZQ

For a utility supply with known Sk" at primary substation:
- `ZQ = c × U²_n / Sk"` (positive sequence)
- `XQ ≈ ZQ × X/R_ratio / √(1 + (X/R)²)`
- `RQ ≈ ZQ / √(1 + (X/R)²)`

For a transformer LV-side calculation (typical building services):
- `Zk_TX_ohm = Zpu × U²_LV / S_TX_kVA` (where Zpu = transformer % impedance from nameplate)
- Split Zk into R + jX using transformer X/R (typical 5-10 for distribution transformers)

For a generator (near-from-generator):
- `X"d_ohm = (X"d_pu) × U²_LV / S_gen_kVA` for the subtransient period (Ik")
- `X'd_ohm = (X'd_pu) × U²_LV / S_gen_kVA` for the transient period (Ib at ~100 ms)
- `Xd_ohm = (Xd_pu) × U²_LV / S_gen_kVA` for the steady-state period

## Step 3 — Build series impedance to each fault point

Walk the cascade tree from source to fault, summing R + jX of each link:

| Link | R contribution | X contribution |
|---|---|---|
| Source (utility OR gen) | RQ + R_TX | XQ + X_TX |
| Main feeder cable | r × L_main | x × L_main |
| Sub-DB feeder cable | r × L_sub | x × L_sub |
| Final circuit cable | r × L_final | x × L_final |

Where:
- `r` = cable resistance per metre (Ω/m) at conductor operating temperature
- `x` = cable reactance per metre (Ω/m)
- `L` = one-way length in metres

Get r + x from:
- **GB:** BS 7671 Appendix 4 Tables 4D5 (R), Table 4F (X)
- **EU/INT:** IEC 60364-5-52 Annex E
- **US:** NEC 2023 Chapter 9 Table 9 (ac resistance + reactance)

## Step 4 — Compute Ik" at each node

For a three-phase symmetrical fault:
```
Ik" = c × Un / (√3 × |Z_total|)
```

Where `|Z_total| = √(R_total² + X_total²)`.

For maximum (breaker rating check): `c = c_max = 1.05` (LV)
For minimum (ADS check):           `c = c_min = 0.95` (LV)

## Step 5 — Compute peak current ipk

```
ipk = κ × √2 × Ik"
```

Where κ (kappa) is the peak factor per IEC 60865-1:
```
κ = 1.02 + 0.98 × exp(-3 R/X)
```

| X/R ratio | κ | Interpretation |
|---|---|---|
| 0.5 | 1.02 + 0.98 × exp(-6) ≈ 1.022 | Highly resistive — small peak |
| 1 | 1.02 + 0.98 × exp(-3) ≈ 1.069 | Moderate |
| 5 | 1.02 + 0.98 × exp(-0.6) ≈ 1.557 | Industrial typical |
| 10 | 1.02 + 0.98 × exp(-0.3) ≈ 1.747 | Large transformer |
| 30+ | 1.02 + 0.98 × exp(-0.1) ≈ 1.907 | Generator/large MV — close to maximum 2.0 |

See `peak-factor-kappa.json` for the table.

## Step 6 — For near-from-generator: apply decrement

If the fault is supplied by a synchronous generator (standby genset on a transfer scheme):

- **First cycle (subtransient):** Use X"d → compute Ik"
- **Breaking-current time tmin (≈ 30-90 ms for MCCB/ACB):** Apply decrement factor μ:
  - `Ib_NG = μ × Ik"`
  - `μ` from IEC 60909-0 §3.5 Table 4 (function of Ik"_gen / In_gen and tmin)
  - Typical μ ≈ 0.75-0.85 for tmin ≈ 90 ms
- **Steady state:** `Ik = λ × In_gen` where λ from Table 5 (function of X"d, X'd, Xd)

For far-from-generator: skip this step. Ik = Ib = Ik".

## Step 7 — Multi-source superposition

When utility + generator + UPS + motors contribute simultaneously (data centre topology, ATS in parallel-paths mode):

```
Ik"_total = Σ Ik"_source_i
```

Each source contributes its own Ik" via its source path to the fault. Sum the complex values:
```
I_total_complex = Σ (c × Un / (√3 × Z_path_i))
|Ik"_total| = |I_total_complex|
```

For most building services: utility OR generator (transfer scheme = one source at a time). For data centres: utility + UPS + sometimes static gen → multi-source applies.

## Step 8 — Output

Emit at each cascade node:

```json
{
  "node_id": "MSB-1.F01.DB-L1",
  "ifault_ka_max": 23.4,    // Ik"max with c=1.05
  "ifault_ka_min": 21.1,    // Ik"min with c=0.95
  "ipk_ka": 35.7,            // κ × √2 × Ik"max
  "x_over_r_at_node": 4.2,   // R+jX at this point
  "z_total_ohm": 0.024
}
```

## What does NOT happen here

- DC arc-flash calculation (separate IEEE 1584 method)
- Lightning surge analysis (BS EN 62305 / NFPA 780)
- Sub-cycle dynamic simulation (EMT-level — beyond IEC 60909 scope)
- Time-graded protection curves (separate protection-coordination scope)
```

- [ ] **Step 2: Validate + commit**

```bash
test -s shared/standards/electrical/IEC60909/part0-method.md && echo OK
git add shared/standards/electrical/IEC60909/part0-method.md
git commit -m "feat: IEC60909 part0-method.md — step-by-step calculation walkthrough"
```

---

## Task 5: peak-factor-kappa.json + voltage-factor-c.json

**Files:**
- Create: `shared/standards/electrical/IEC60909/peak-factor-kappa.json`
- Create: `shared/standards/electrical/IEC60909/voltage-factor-c.json`

- [ ] **Step 1: Write peak-factor-kappa.json**

```json
{
  "_title": "IEC 60909-0 + IEC 60865-1 — Peak Factor κ (Kappa)",
  "_version": "1.0.0",
  "_reference": "IEC 60909-0:2016 §4.3; IEC 60865-1:2011 §2.2",
  "purpose": "Compute the peak short-circuit current ipk from the initial RMS short-circuit current Ik\" via the peak factor κ, which depends on the R/X ratio at the fault.",
  "formula": {
    "ipk": "κ × √2 × Ik\"",
    "kappa": "1.02 + 0.98 × exp(-3 × R/X)",
    "alternative_for_meshed_networks": "κb method per IEC 60909-0 §4.3.1.2"
  },
  "lookup_table_by_x_over_r": [
    { "x_over_r": 0.5,  "kappa": 1.022, "regime": "highly_resistive_cable" },
    { "x_over_r": 1.0,  "kappa": 1.069, "regime": "moderate" },
    { "x_over_r": 2.0,  "kappa": 1.180, "regime": "lv_cable_typical" },
    { "x_over_r": 3.0,  "kappa": 1.279, "regime": "lv_busbar" },
    { "x_over_r": 5.0,  "kappa": 1.439, "regime": "industrial_typical" },
    { "x_over_r": 7.0,  "kappa": 1.557, "regime": "large_transformer_secondary" },
    { "x_over_r": 10.0, "kappa": 1.668, "regime": "transformer_terminals" },
    { "x_over_r": 15.0, "kappa": 1.768, "regime": "generator_terminals" },
    { "x_over_r": 20.0, "kappa": 1.823, "regime": "mv_busbar" },
    { "x_over_r": 30.0, "kappa": 1.873, "regime": "high_voltage_close_to_source" },
    { "x_over_r": 50.0, "kappa": 1.910, "regime": "approaching_maximum" },
    { "x_over_r": 100.0,"kappa": 1.940, "regime": "near_maximum_pure_inductive" }
  ],
  "asymptotic_limits": {
    "min": { "value": 1.0, "condition": "pure resistive — instantaneous current = RMS × √2 with no DC offset envelope" },
    "max": { "value": 2.0, "condition": "pure inductive — full DC offset adds to first peak" }
  },
  "engineering_notes": [
    "For LV cable-dominated paths (X/R typically 1-3): κ ≈ 1.1-1.3 — moderate first peak",
    "For transformer-dominated paths near MV (X/R 5-10): κ ≈ 1.5-1.7 — significant first peak",
    "For generator-dominated paths (X/R 15-30): κ ≈ 1.8-1.9 — large first peak, approaches theoretical max",
    "Peak current drives busbar Ipk_withstand and breaker rated peak withstand (IEC 60947-2 Ipk) checks"
  ],
  "cross_reference": {
    "consumed_by": [
      "electrical/fault-level (generator Step 5)",
      "electrical/db-layout (busbar Ipk withstand check via fault-level intent)"
    ]
  }
}
```

- [ ] **Step 2: Write voltage-factor-c.json**

```json
{
  "_title": "IEC 60909-0 — Voltage Factor c (Table 1)",
  "_version": "1.0.0",
  "_reference": "IEC 60909-0:2016 §3.7 Table 1; IEC 60038:2009 Standard voltages",
  "purpose": "Adjust nominal voltage Un to account for normal supply variation (tap changing, no-load TX secondary, regulation drops)",
  "table_1": {
    "lv_systems_ge_100v": {
      "_scope": "Three-phase LV: 230/400 V (IEC), 277/480 V (NEC). Single-phase LV: 230 V (IEC), 120/240 V (NEC).",
      "c_max": {
        "value": 1.05,
        "use_for": "Calculation of maximum Ik\" — drives breaker breaking-capacity verification + busbar Ipk withstand check",
        "rationale": "Accounts for normal over-voltage at lightly loaded transformer secondary"
      },
      "c_min": {
        "value": 0.95,
        "use_for": "Calculation of minimum Ik\" — drives ADS (automatic disconnection of supply) protection setting verification",
        "rationale": "Accounts for under-voltage at heavily loaded transformer + cable drop"
      }
    },
    "lv_systems_lt_100v": {
      "_scope": "ELV systems",
      "c_max": 1.10,
      "c_min": 0.95
    },
    "mv_hv_systems": {
      "_scope": "Un > 1 kV up to 230 kV (11 kV, 33 kV, 132 kV typical)",
      "c_max": 1.10,
      "c_min": 1.00
    }
  },
  "engineering_application": {
    "for_breaker_selection": "Always use c_max for Ik\"_max — under-sizing a breaker on c=1.0 is unsafe",
    "for_protection_setting": "Use c_min for Ik\"_min — over-setting protection on c=1.0 can leave faults unprotected (ADS fails)",
    "for_selectivity_coordination": "Use c_max for upstream Icn check, c_min for downstream sensitivity check"
  },
  "cross_reference": {
    "consumed_by": [
      "electrical/fault-level (generator Steps 4, 10)",
      "electrical/db-layout (selectivity verification per IEC 60364-5-53)"
    ]
  }
}
```

- [ ] **Step 3: Validate + commit**

```bash
python3 -c "
import json
json.load(open('shared/standards/electrical/IEC60909/peak-factor-kappa.json'))
json.load(open('shared/standards/electrical/IEC60909/voltage-factor-c.json'))
print('OK')
"
git add shared/standards/electrical/IEC60909/peak-factor-kappa.json shared/standards/electrical/IEC60909/voltage-factor-c.json
git commit -m "feat: IEC60909 peak-factor κ + voltage-factor c tables"
```

---

## Task 6: source-impedances.json + transformer-zpu-table.json

**Files:**
- Create: `shared/standards/electrical/IEC60909/source-impedances.json`
- Create: `shared/standards/electrical/IEC60909/transformer-zpu-table.json`

- [ ] **Step 1: Write source-impedances.json**

```json
{
  "_title": "IEC 60909 — Source Impedance Reference",
  "_version": "1.0.0",
  "_reference": "IEC 60909-0:2016 §4.2 (network feeder), §4.3 (transformer), §4.4 (generator), §4.5 (motor); IEC 60909-2:2008 data tables",
  "purpose": "Unified reference for source-impedance modelling across all source types used by the IEC 60909 method.",

  "network_feeder_zq": {
    "_reference": "IEC 60909-0:2016 §4.2",
    "definition": "Equivalent impedance of the upstream network seen from the LV-side primary of the building's incoming transformer (or service entrance)",
    "from_declared_pscc": {
      "method": "If DNO/POCO declares PSCC (Sk\") at primary substation:",
      "formula_zq": "ZQ = c × U²_n_primary / Sk\"",
      "split_into_r_x": "Use X/R_ratio from declaration; XQ = ZQ × X/R / √(1 + (X/R)²); RQ = ZQ / √(1 + (X/R)²)",
      "typical_x_over_r": {
        "11_kv_urban_dense": 5,
        "11_kv_rural": 3,
        "33_kv": 8,
        "132_kv": 15
      }
    },
    "default_when_not_declared": {
      "_warning": "Use only when no DNO declaration available; engineer must flag this as an assumption",
      "uk_typical_11kv_supply": { "sk_mva": 200, "x_over_r": 5 },
      "us_typical_12_47kv": { "sk_mva": 300, "x_over_r": 6 }
    }
  },

  "transformer_zk": {
    "_reference": "IEC 60909-0:2016 §4.3; transformer nameplate Zpu",
    "definition": "Transformer short-circuit impedance referred to LV side",
    "formula": "Zk_TX = Zpu × U²_LV / S_TX_kVA × 1000  (result in ohms)",
    "rk_xk_split": {
      "for_distribution_tx_below_1000_kva": "Use X/R = 5 (typical)",
      "for_distribution_tx_1000_to_3150_kva": "Use X/R = 8 (typical)",
      "for_distribution_tx_above_3150_kva": "Use X/R = 12 (typical)",
      "from_nameplate": "If nameplate provides cu losses (Pcu) and Zpu: Rk = (Pcu × U²_LV) / S²_TX; Xk = √(Zk² − Rk²)"
    },
    "reference_table": "transformer-zpu-table.json"
  },

  "generator_xd_subtransient_xd_prime_xd": {
    "_reference": "IEC 60909-0:2016 §4.4; near-from-generator",
    "definition": "Synchronous generator subtransient X\"d (first cycle), transient X'd (~100ms), synchronous Xd (steady-state)",
    "formula_subtransient": "X\"d_ohm = X\"d_pu × U²_LV / S_gen_kVA × 1000",
    "decrement_application": [
      "First cycle (t = 0+, for Ik\"): use X\"d",
      "Breaking time (tmin = 30-90 ms, for Ib): apply decrement factor μ from §3.5 Table 4",
      "Steady state (long t, for Ik): use Xd; apply λ-factor from §3.5 Table 5"
    ],
    "reference_table": "generator-subtransient-tables.json"
  },

  "ups_battery_inverter_zups": {
    "_reference": "Not directly in IEC 60909-0 (manufacturer-specific); IEC 62040-3 UPS standard",
    "definition": "UPS / static inverter — current-limited source, very different from rotating machines",
    "first_half_cycle": "Inverter output current limited to 2-3 × I_rated by IGBT/IGCT current sensors. First-half-cycle Ik\"_UPS = 2 × I_rated_UPS typical (manufacturer-specific)",
    "after_first_cycle": "Most UPSes transition to bypass within 4-5 ms during sustained fault. After bypass: source becomes upstream utility — use utility path Ik\".",
    "modelling_recommendation": [
      "For first-cycle breaker rating: include UPS contribution + utility (worst case)",
      "For sustained-fault protection: UPS is bypassed → use utility path only"
    ]
  },

  "induction_motor_xm_doubleprime": {
    "_reference": "IEC 60909-0:2016 §4.5",
    "definition": "Induction motor short-circuit contribution via subtransient reactance (back-EMF from rotating mass)",
    "inclusion_threshold": "Sum of motor kVA contribution > 1% of Sk\"_total at fault location (2016 amendment tightened from 5%)",
    "formula": "Ik\"_motor = ILR / In_motor × I_rated_motor, where ILR is the locked-rotor current ratio (typical 5-7 × FLC)",
    "aggregate_contribution": "Σ Ik\"_motor_i for all motors connected at or downstream of the fault location",
    "exclusion": "If sum < 1% of Ik\"_source — exclude (per §4.5.1.2)",
    "reference_table": "motor-contribution-rules.json"
  }
}
```

- [ ] **Step 2: Write transformer-zpu-table.json**

```json
{
  "_title": "Typical Distribution Transformer Z-pu by Rating (Indicative Defaults)",
  "_version": "1.0.0",
  "_reference": "IEC 60076-5 (Power Transformers Part 5: Ability to withstand short-circuit), IEC 60076-1 Table 1 — typical Zk%",
  "purpose": "Default Zpu values for engineer use when no nameplate is available. Real designs MUST use nameplate Zpu — these are last-resort defaults.",
  "table_distribution_transformers": [
    { "kva_min": 100,   "kva_max": 315,   "zpu_typical_percent": 4.0, "x_over_r_typical": 4,  "_note": "Small distribution TX (5kV pri / 400V sec or 25 kV / 277 V)" },
    { "kva_min": 400,   "kva_max": 800,   "zpu_typical_percent": 4.0, "x_over_r_typical": 5,  "_note": "Medium distribution TX" },
    { "kva_min": 1000,  "kva_max": 1600,  "zpu_typical_percent": 5.0, "x_over_r_typical": 6,  "_note": "Large distribution TX (commercial substation)" },
    { "kva_min": 2000,  "kva_max": 2500,  "zpu_typical_percent": 6.0, "x_over_r_typical": 8,  "_note": "Heavy commercial / industrial" },
    { "kva_min": 3150,  "kva_max": 5000,  "zpu_typical_percent": 7.0, "x_over_r_typical": 10, "_note": "Industrial / utility primary" },
    { "kva_min": 6300,  "kva_max": 10000, "zpu_typical_percent": 8.0, "x_over_r_typical": 12, "_note": "Large industrial / sub-station" }
  ],
  "table_dry_type_transformers": [
    { "kva_min": 100,   "kva_max": 1000,  "zpu_typical_percent": 5.75, "x_over_r_typical": 4, "_note": "NEMA dry-type — typical US data centre / commercial fit-out" },
    { "kva_min": 1000,  "kva_max": 2500,  "zpu_typical_percent": 5.75, "x_over_r_typical": 6, "_note": "NEMA dry-type — larger commercial" }
  ],
  "warnings": [
    "These are INDICATIVE typical values from IEC 60076-1. Always use the actual transformer nameplate Zpu when available.",
    "Off-load tap-changer position affects Zpu — nameplate values are at principal tap; consider tap-changer range for accurate cascade.",
    "Dry-type transformers have higher Zpu than equivalent oil-filled — reduces fault current but adds voltage drop.",
    "Zpu tolerance is typically ±10% per IEC 60076-1; for breaker breaking-capacity verification, use the MINIMUM Zpu (highest fault) as worst case."
  ],
  "cross_reference": {
    "consumed_by": [
      "electrical/fault-level (generator Step 5 transformer impedance)",
      "shared/calculations/electrical/iec60909-cascade.json (source_z_percent default fallback)"
    ]
  }
}
```

- [ ] **Step 3: Validate + commit**

```bash
python3 -c "
import json
json.load(open('shared/standards/electrical/IEC60909/source-impedances.json'))
json.load(open('shared/standards/electrical/IEC60909/transformer-zpu-table.json'))
print('OK')
"
git add shared/standards/electrical/IEC60909/source-impedances.json shared/standards/electrical/IEC60909/transformer-zpu-table.json
git commit -m "feat: IEC60909 source-impedances + transformer-zpu-table"
```

---

## Task 7: generator-subtransient-tables.json + motor-contribution-rules.json

**Files:**
- Create: `shared/standards/electrical/IEC60909/generator-subtransient-tables.json`
- Create: `shared/standards/electrical/IEC60909/motor-contribution-rules.json`

- [ ] **Step 1: Write generator-subtransient-tables.json**

```json
{
  "_title": "Synchronous Generator Subtransient / Transient / Synchronous Reactance Reference",
  "_version": "1.0.0",
  "_reference": "IEC 60909-0:2016 §4.4 + §3.5; IEC 60034-1 (rotating machines); IEC 60909-2:2008 Annex C (typical generator data)",
  "purpose": "Default X\"d, X'd, Xd values for engineer use when no manufacturer data is available. Real designs MUST use manufacturer data — these are last-resort defaults.",
  "table_typical_values_per_unit": [
    {
      "machine_type": "salient_pole_with_damper_windings",
      "typical_rating_kva": "10 - 1000",
      "x_d_doubleprime_pu": 0.12,
      "x_d_prime_pu":      0.20,
      "x_d_pu":            1.10,
      "_application": "Small standby gensets (≤ 1 MVA), engine-driven"
    },
    {
      "machine_type": "salient_pole_with_damper_windings_medium",
      "typical_rating_kva": "1000 - 5000",
      "x_d_doubleprime_pu": 0.15,
      "x_d_prime_pu":      0.25,
      "x_d_pu":            1.20,
      "_application": "Medium standby gensets (1-5 MVA) — large commercial, healthcare"
    },
    {
      "machine_type": "cylindrical_rotor_no_damper",
      "typical_rating_kva": "5000 - 20000",
      "x_d_doubleprime_pu": 0.18,
      "x_d_prime_pu":      0.28,
      "x_d_pu":            1.50,
      "_application": "Large standby + cogeneration units (5-20 MVA)"
    },
    {
      "machine_type": "turbogenerator",
      "typical_rating_kva": "20000 +",
      "x_d_doubleprime_pu": 0.20,
      "x_d_prime_pu":      0.30,
      "x_d_pu":            1.80,
      "_application": "Power-station turbogenerators (out of building services scope)"
    }
  ],
  "decrement_factor_mu": {
    "_reference": "IEC 60909-0:2016 §3.5 Table 4",
    "purpose": "Apply to Ik\" to obtain breaking current Ib at contact-separation time tmin",
    "_typical_values": {
      "tmin_30ms": 0.85,
      "tmin_50ms": 0.80,
      "tmin_90ms": 0.75,
      "tmin_250ms": 0.68
    },
    "engineering_note": "tmin depends on protection device clearing time. MCCB ≈ 30-50 ms; ACB with short delay ≈ 50-100 ms; with definite-time intentional delay ≈ 200-500 ms."
  },
  "steady_state_lambda": {
    "_reference": "IEC 60909-0:2016 §3.5 Table 5",
    "purpose": "Steady-state short-circuit current as λ × I_rated",
    "_typical_values": {
      "machine_with_avr_overshoot": 2.0,
      "machine_with_avr_normal": 1.5,
      "machine_without_avr": 0.4
    }
  },
  "warnings": [
    "These are INDICATIVE typical values. Always use manufacturer data sheet for actual generator.",
    "Subtransient X\"d defines first-cycle Ik\" — drives breaker breaking-capacity check on gen-fed side.",
    "Decrement matters when breaking time tmin > 30 ms — for fast MCCBs near-generator approximation simplifies to FG."
  ],
  "cross_reference": {
    "consumed_by": [
      "electrical/fault-level (generator Step 6 generator modelling)",
      "shared/calculations/electrical/iec60909-cascade.json (source generator inputs)"
    ]
  }
}
```

- [ ] **Step 2: Write motor-contribution-rules.json**

```json
{
  "_title": "IEC 60909-0 §4.5 — Induction Motor Short-Circuit Contribution Rules",
  "_version": "1.0.0",
  "_reference": "IEC 60909-0:2016 §4.5 + §4.5.1; IEC 60909-0:2016 amendment (2016) tightened threshold from 5% to 1%",
  "purpose": "Determine when and how to include running induction motor back-feed into the cascade Ik\".",
  "principle": "Running induction motors store kinetic energy in the rotor. On a downstream fault, the motor briefly back-feeds via its subtransient reactance (locked-rotor reactance), contributing Ik\"_motor for ~1-2 cycles before mechanical decay dominates.",

  "inclusion_threshold": {
    "_reference": "IEC 60909-0:2016 §4.5.1.2 (2016 amendment)",
    "rule": "Include motor contribution in Ik\" if: Σ(P_motors_rated_kW) ≥ 1% × Sk\"_at_fault",
    "old_threshold_2001": "Pre-2016 amendment used 5% — many existing studies still cite this",
    "rationale": "For non-industrial sites (offices, retail, residential), motor load is small fraction of supply — exclude. For industrial with material motor load, must include."
  },

  "calculation_formula": {
    "ik_doubleprime_motor": "Ik\"_motor = ILR × I_rated_motor",
    "where": {
      "ILR": "Locked-rotor current ratio. NEMA Code Letters: B=3.5×, F=5.5×, K=8.5×. IEC Letters: H=4.5×, K=6.5×, L=8×. Typical: 5-7 × FLC for general-purpose motors.",
      "I_rated_motor": "Motor full-load current at rated voltage"
    },
    "aggregate_contribution": "Σ Ik\"_motor_i for all running motors connected at or downstream of fault location. Sum is to FIRST CYCLE only — motors decay rapidly."
  },

  "calculation_simplification_when_motors_dispersed": {
    "method": "When motors are spread across many small loads (e.g. air handling units 5-20 kW each in a commercial building):",
    "simplified_formula": "Ik\"_motor_total ≈ ILR_avg × (Σ P_motors_kW / V) / √3",
    "default_ILR_avg": "5 (representing IEC Letter K — common for HVAC fans, pumps, compressors)"
  },

  "decrement_after_first_cycle": {
    "rule": "Motor contribution decays within 1-2 cycles (~20-40 ms at 50 Hz)",
    "ib_motor_at_breaking_time": "Ib_motor ≈ 0.5 × Ik\"_motor for tmin ≥ 30 ms",
    "ik_motor_steady_state": "Zero — motors do not sustain steady-state fault current"
  },

  "exclusions": [
    "Motors stopped or in standby — no rotational kinetic energy, no contribution",
    "VFD-driven motors — VFD blocks back-feed via DC link",
    "Motors fed via soft-starter in run mode — DOL back-feed only (soft-starter is bypassed in run)"
  ],

  "warnings": [
    "Motor contribution increases Ik\" by 10-30% in industrial sites with material motor load",
    "Ignoring motor contribution can under-rate breakers near MCCs and motor distribution boards",
    "Conversely, over-counting non-running motors (only counting nameplate) gives unrealistic worst case — use realistic running motor load"
  ],

  "cross_reference": {
    "consumed_by": [
      "electrical/fault-level (generator Step 8 induction motor contribution)",
      "shared/calculations/electrical/iec60909-cascade.json (motor source path)"
    ]
  }
}
```

- [ ] **Step 3: Validate + commit**

```bash
python3 -c "
import json
json.load(open('shared/standards/electrical/IEC60909/generator-subtransient-tables.json'))
json.load(open('shared/standards/electrical/IEC60909/motor-contribution-rules.json'))
print('OK')
"
git add shared/standards/electrical/IEC60909/generator-subtransient-tables.json shared/standards/electrical/IEC60909/motor-contribution-rules.json
git commit -m "feat: IEC60909 generator + motor contribution data tables"
```

---

## Task 8: compliance-checklist.md

**Files:**
- Create: `shared/standards/electrical/IEC60909/compliance-checklist.md`

- [ ] **Step 1: Write compliance-checklist.md**

```markdown
# IEC 60909 Compliance Checklist

Verification checklist for any fault-level study deliverable produced by `electrical/fault-level` or referenced by downstream skills (db-layout, earthing, cable-sizing).

## Source data documented?

- [ ] Utility / DNO source: PSCC declared at primary, OR transformer kVA + Zpu + X/R documented
- [ ] HV-side voltage and network arrangement (radial / ring) stated
- [ ] Standby generator: X"d, X'd, Xd, kVA, voltage documented (if present)
- [ ] UPS: rated kVA, output current limit, bypass path described (if present)
- [ ] Motor load: total connected kW + ILR (locked-rotor current ratio) declared (if > 1% threshold)

## Cascade topology completeness?

- [ ] Every node in the cascade tree has a parent (single tree, no orphans)
- [ ] Cable impedance source declared per stage (BS 7671 App 4 / IEC 60364-5-52 / NEC Chapter 9 Table 9)
- [ ] All sub-DBs and final-circuit endpoints present (no gaps in the tree)

## Calculation method?

- [ ] IEC 60909-0:2016 method explicitly cited
- [ ] Voltage factor c selection documented: c=1.05 for Ik"max, c=0.95 for Ik"min
- [ ] Near-or-far-from-generator classification stated per source
- [ ] Peak factor κ derived from X/R at each node (not assumed constant)
- [ ] Multi-source superposition applied where utility + gen + UPS + motors are simultaneously active

## Output verification?

- [ ] Ik"max + Ik"min + ipk + X/R + Z_total emitted at every cascade node
- [ ] Breaker Icn ≥ Ik"max checked at every node — flagged if not
- [ ] Busbar Ipk_withstand ≥ ipk checked at every board — flagged if not
- [ ] Cable adiabatic check (I²t ≤ k²S²) verified at every cable using Ik"max
- [ ] Selectivity coordination notes flagged where upstream-downstream Icn relationship needs verification

## Tool execution status?

- [ ] If `calc.iec60909_cascade` runtime tool was invoked: results documented in IR
- [ ] If tool not available: `tool_call_pending: true` emitted per WI3 deferral pattern
- [ ] Engineer-input fault currents (fallback path) clearly distinguished from computed values in IR

## Cross-skill integration?

- [ ] Emitted `fault-level` intent satisfies the shape expected by `electrical/db-layout` v1.0.0
- [ ] db-layout selectivity tool_call_pending entries resolved when fault-level intent is present

## Rationale block?

- [ ] WI2 rationale block present at IR root
- [ ] 8 sections (Source Specification / Cascade Topology / HV-side Assumptions / Transformer + Source Impedances / Motor Contribution Assessment / Per-node Ifault Computation / Selectivity Implications / Compliance + Assumptions)
- [ ] chat_summary 40-500 chars
- [ ] All decisions cite IEC 60909-0 clauses verbatim
```

- [ ] **Step 2: Verify entire IEC60909 layer + commit**

```bash
ls shared/standards/electrical/IEC60909/ | sort
python3 -c "
import json
files_to_check = [
    'meta.json',
    'part0-fundamentals.json',
    'peak-factor-kappa.json',
    'voltage-factor-c.json',
    'source-impedances.json',
    'transformer-zpu-table.json',
    'generator-subtransient-tables.json',
    'motor-contribution-rules.json'
]
for f in files_to_check:
    json.load(open(f'shared/standards/electrical/IEC60909/{f}'))
    print(f'{f}: OK')
"
git add shared/standards/electrical/IEC60909/compliance-checklist.md
git commit -m "feat: IEC60909 compliance-checklist.md — completes Phase A standards layer"
```

Expected: 11 files in shared/standards/electrical/IEC60909/, all 8 JSON files parse, 3 markdown files exist.

---

# PHASE B — fault-level Skill (Tasks 9-35)

The 44 files implementing the skill. Same artefact pattern as earthing/db-layout.

## Task 9: Create CHANGELOG.md

**Files:**
- Create: `electrical/fault-level/CHANGELOG.md`

- [ ] **Step 1: Write the file**

```markdown
# Changelog — fault-level

## v1.0.0 (current — IEC 60909 HV+LV cascade)

First production-grade version. Single-stage skill (no sub-stages planned at v1).

### Features
- 14-step reasoning chain in `prompts/generator.md` that explicitly names 21 standards files (consumption-pattern proof)
- New IEC 60909 standards layer at `shared/standards/electrical/IEC60909/` (11 files) shipped as Phase A
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
```

- [ ] **Step 2: Commit**

```bash
git add electrical/fault-level/CHANGELOG.md
git commit -m "feat: fault-level CHANGELOG.md — v1.0.0 IEC 60909 HV+LV cascade"
```

---

## Task 10: Create `schemas/fault-level-ir.schema.json`

**Files:**
- Create: `electrical/fault-level/schemas/fault-level-ir.schema.json`

The canonical IR schema. One IR per project (not per board — cascade is project-scoped).

- [ ] **Step 1: Write the schema**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "electrical/fault-level/schemas/fault-level-ir.schema.json",
  "title": "Fault-Level IR (IEC 60909 cascade)",
  "description": "Intermediate Representation for the fault-level skill. One IR per project. Carries cascade tree + source modelling + per-node Ik\"/ipk/X-R + selectivity implications + rationale.",
  "type": "object",
  "required": [
    "drawing_type",
    "version",
    "meta",
    "jurisdiction",
    "project_supply",
    "sources",
    "cascade",
    "selectivity_implications",
    "compliance_summary",
    "rationale"
  ],
  "properties": {
    "drawing_type": { "const": "fault_level_study" },
    "version":      { "type": "string", "pattern": "^\\d+\\.\\d+(\\.\\d+)?$" },
    "meta": {
      "type": "object",
      "required": ["project_id", "skill_version", "produced_at"],
      "properties": {
        "project_id":    { "type": "string" },
        "skill_version": { "type": "string" },
        "produced_at":   { "type": "string", "format": "date-time" },
        "consumed_intents": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["intent_type", "intent_version", "produced_by"],
            "properties": {
              "intent_type":    { "type": "string", "pattern": "^[a-z][a-z0-9-]*$" },
              "intent_version": { "type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$" },
              "produced_by":    { "type": "string" }
            }
          }
        }
      }
    },
    "jurisdiction": { "enum": ["GB", "EU", "INT", "US"] },
    "project_supply": {
      "type": "object",
      "required": ["lv_source"],
      "properties": {
        "hv_side": {
          "type": "object",
          "properties": {
            "voltage_kv":                    { "type": "number", "exclusiveMinimum": 1.0 },
            "network_arrangement":           { "enum": ["radial", "ring_main", "interconnected_mesh"] },
            "declared_pscc_at_primary_ka":   { "type": "number", "minimum": 0 },
            "x_over_r_at_primary":           { "type": "number", "minimum": 0 }
          }
        },
        "lv_source": {
          "type": "object",
          "required": ["type", "voltage_v"],
          "properties": {
            "type":                       { "enum": ["utility_transformer", "generator", "ups", "mixed"] },
            "kva":                        { "type": "number", "minimum": 0 },
            "voltage_v":                  { "type": "integer", "enum": [120, 208, 230, 240, 277, 400, 415, 480] },
            "z_percent":                  { "type": "number", "minimum": 0, "maximum": 30 },
            "x_over_r":                   { "type": "number", "minimum": 0 },
            "near_or_far_from_generator": { "enum": ["near", "far"] }
          }
        }
      }
    },
    "sources": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "kind"],
        "properties": {
          "id":                       { "type": "string" },
          "kind":                     { "enum": ["utility", "generator", "ups", "motor_aggregate"] },
          "contribution_method":      { "enum": ["constant", "subtransient_decrement", "current_limited", "locked_rotor"] },
          "ifault_contribution_ka":   { "type": "number", "minimum": 0 },
          "decrement_profile":        { "type": "object" }
        }
      }
    },
    "cascade": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["node_id", "node_kind"],
        "properties": {
          "node_id":             { "type": "string", "description": "Path-like id, e.g. 'HV-1', 'TX-1', 'MSB-1', 'MSB-1.F01.DB-L1.C03'" },
          "parent_node_id":      { "type": "string" },
          "node_kind":           { "enum": ["hv_source", "transformer_secondary", "board_incoming", "board_busbar", "board_outgoing_feeder", "final_circuit_endpoint"] },
          "designation":         { "type": "string" },
          "feeder": {
            "type": "object",
            "properties": {
              "length_m":           { "type": "number", "exclusiveMinimum": 0 },
              "csa_mm2_or_awg":     { "type": "string" },
              "material":           { "enum": ["copper", "aluminium"] },
              "insulation":         { "enum": ["pvc_70", "xlpe_90", "epr_90", "thermosetting_90"] }
            }
          },
          "z_addition_ohm":      {
            "type": "object",
            "properties": {
              "r": { "type": "number", "minimum": 0 },
              "x": { "type": "number", "minimum": 0 }
            }
          },
          "ifault_ka_max":       { "type": "number", "minimum": 0, "description": "Ik\"max with c=1.05" },
          "ifault_ka_min":       { "type": "number", "minimum": 0, "description": "Ik\"min with c=0.95" },
          "ipk_ka":              { "type": "number", "minimum": 0, "description": "κ × √2 × Ik\"max" },
          "x_over_r_at_node":    { "type": "number", "minimum": 0 },
          "z_total_ohm":         { "type": "number", "minimum": 0 },
          "tool_call_pending":   { "type": "boolean", "description": "true when calc.iec60909_cascade has not yet executed" }
        }
      }
    },
    "selectivity_implications": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["breaker_id", "ifault_at_breaker_ka", "adequate"],
        "properties": {
          "breaker_id":             { "type": "string" },
          "breaker_rating_a":       { "type": "integer" },
          "breaker_icn_ka":         { "type": "number", "minimum": 0 },
          "ifault_at_breaker_ka":   { "type": "number", "minimum": 0 },
          "adequate":               { "type": "boolean" },
          "recommendation":         { "type": "string" }
        }
      }
    },
    "compliance_summary": {
      "type": "object",
      "required": ["compliant", "non_compliance_flags", "assumptions"],
      "properties": {
        "compliant":            { "type": "boolean" },
        "non_compliance_flags": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["message"],
            "properties": {
              "message":      { "type": "string" },
              "code_clause":  { "type": "string" },
              "severity":     { "enum": ["critical", "warning", "info"] }
            }
          }
        },
        "assumptions":          { "type": "array", "items": { "type": "string" } }
      }
    },
    "drawn_as_symbols": { "type": "array", "items": { "type": "string", "pattern": "^[A-Z][A-Z0-9_]*$" } },
    "flags":            { "type": "array", "items": { "type": "string" } },
    "rationale":        { "$ref": "../../../shared/schemas/core/rationale.schema.json" }
  }
}
```

- [ ] **Step 2: Validate + commit**

```bash
python3 -c "
import json, jsonschema
s = json.load(open('electrical/fault-level/schemas/fault-level-ir.schema.json'))
jsonschema.Draft7Validator.check_schema(s)
print('fault-level-ir.schema.json: valid')
"
git add electrical/fault-level/schemas/fault-level-ir.schema.json
git commit -m "feat: fault-level-ir.schema.json — IEC 60909 cascade IR (project-scoped)"
```

---

## Task 11: Create `schemas/fault-level-intent.schema.json`

**Files:**
- Create: `electrical/fault-level/schemas/fault-level-intent.schema.json`

The stable downstream-facing subset of the IR. Consumed by db-layout, earthing, cable-sizing, generator-sizing.

- [ ] **Step 1: Write the schema**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "electrical/fault-level/schemas/fault-level-intent.schema.json",
  "title": "Fault-Level Intent (Downstream-Facing)",
  "description": "Stable subset of the fault-level IR. Consumed by db-layout (selectivity resolution), earthing (ADS cross-check), cable-sizing (adiabatic verification), generator-sizing (Iek). Forward-compat: optional fields may be added; required-field changes require a major intent_version bump.",
  "type": "object",
  "required": ["project_id", "source_summary", "fault_currents"],
  "additionalProperties": false,
  "properties": {
    "project_id": { "type": "string" },
    "intent_version": { "type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$" },
    "source_summary": {
      "type": "object",
      "required": ["type", "voltage_v"],
      "additionalProperties": false,
      "properties": {
        "type":        { "enum": ["utility_transformer", "generator", "ups", "mixed"] },
        "kva":         { "type": "number", "minimum": 0 },
        "voltage_v":   { "type": "integer", "enum": [120, 208, 230, 240, 277, 400, 415, 480] },
        "x_over_r":    { "type": "number", "minimum": 0 }
      }
    },
    "fault_currents": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["node_id", "node_kind", "ifault_ka_max"],
        "additionalProperties": false,
        "properties": {
          "node_id":          { "type": "string" },
          "node_kind":        { "enum": ["hv_source", "transformer_secondary", "board_incoming", "board_busbar", "board_outgoing_feeder", "final_circuit_endpoint"] },
          "ifault_ka_max":    { "type": "number", "minimum": 0, "description": "Ik\"max with c=1.05 — for breaker rating verification" },
          "ifault_ka_min":    { "type": "number", "minimum": 0, "description": "Ik\"min with c=0.95 — for ADS / protection setting" },
          "ipk_ka":           { "type": "number", "minimum": 0, "description": "Peak — for busbar Ipk_withstand check" },
          "x_over_r_ratio":   { "type": "number", "minimum": 0 },
          "z_total_ohm":      { "type": "number", "minimum": 0 }
        }
      }
    }
  }
}
```

- [ ] **Step 2: Validate + commit**

```bash
python3 -c "
import json, jsonschema
s = json.load(open('electrical/fault-level/schemas/fault-level-intent.schema.json'))
jsonschema.Draft7Validator.check_schema(s)
print('fault-level-intent.schema.json: valid')
"
git add electrical/fault-level/schemas/fault-level-intent.schema.json
git commit -m "feat: fault-level-intent.schema.json — stable downstream subset"
```

---

## Task 12: Create `inputs.json` (16-item discovery taxonomy)

**Files:**
- Create: `electrical/fault-level/inputs.json`

- [ ] **Step 1: Write the file**

```json
{
  "$schema": "../../shared/schemas/core/inputs.schema.json",
  "skill": "fault-level",
  "version": "1.0.0",
  "items": [
    { "id": "jurisdiction", "label": "Project jurisdiction", "hint": "GB=BS 7671 + IEC 60909; EU/INT=IEC 60364 + IEC 60909; US=NFPA 70 + IEC 60909 method.", "answer_type": "enum", "options": ["GB", "EU", "INT", "US"], "required": true, "project_fact_candidate": true },
    { "id": "project_id", "label": "Project identifier", "answer_type": "text", "required": true, "validator": "non_empty_text", "project_fact_candidate": true },
    { "id": "supply_voltage_v", "label": "LV nominal voltage (V)", "answer_type": "enum", "options": ["120", "208", "230", "240", "277", "400", "415", "480"], "required": true, "project_fact_candidate": true },
    { "id": "hv_side_present", "label": "Project has HV (>1 kV) primary supply?", "hint": "Yes if utility transformer is on site (private substation). No if fed from existing LV service.", "answer_type": "boolean", "default": false, "required": true, "project_fact_candidate": true },
    { "id": "hv_voltage_kv", "label": "HV primary voltage (kV)", "answer_type": "enum", "options": ["6.6", "11", "12.47", "22", "33", "66"], "required": false, "depends_on": ["hv_side_present"], "project_fact_candidate": true },
    { "id": "hv_pscc_at_primary_ka", "label": "DNO-declared PSCC at HV primary (kA)", "answer_type": "float", "required": false, "validator": "positive_float", "depends_on": ["hv_side_present"] },
    { "id": "primary_transformer_kva", "label": "Primary transformer rating (kVA)", "answer_type": "int", "required": false, "validator": "positive_int", "project_fact_candidate": true },
    { "id": "primary_transformer_zpu_pct", "label": "Primary transformer Z (% impedance)", "hint": "From transformer nameplate. Typical 4-7% for distribution.", "answer_type": "float", "required": false, "validator": "positive_float", "depends_on": ["primary_transformer_kva"] },
    { "id": "primary_transformer_xover_r", "label": "Primary transformer X/R ratio", "hint": "Typical 5-10 for distribution transformers.", "answer_type": "float", "default": 6, "required": false },
    { "id": "standby_generator_present", "label": "Project includes standby generator?", "answer_type": "boolean", "default": false, "required": true, "project_fact_candidate": true },
    { "id": "standby_generator_kva", "label": "Standby generator rating (kVA)", "answer_type": "int", "required": false, "validator": "positive_int", "depends_on": ["standby_generator_present"] },
    { "id": "ups_present", "label": "Project includes UPS / battery inverter?", "answer_type": "boolean", "default": false, "required": true, "project_fact_candidate": true },
    { "id": "ups_kva", "label": "UPS rating (kVA)", "answer_type": "int", "required": false, "depends_on": ["ups_present"] },
    { "id": "motor_load_kw", "label": "Total connected motor load (kW)", "hint": "Sum of all running induction motors. If > 1% of source Sk\" → motor back-feed material. Industrial sites only typically.", "answer_type": "float", "default": 0, "required": false, "validator": "positive_float" },
    { "id": "cascade_topology_source", "label": "Cascade topology source", "hint": "Where the cascade tree comes from. Prefer db-layout intent; engineer-declared as fallback.", "answer_type": "enum", "options": ["db_layout_rollup_intent", "engineer_declared"], "required": true, "default": "db_layout_rollup_intent" },
    { "id": "cascade_engineer_declared", "label": "Engineer-declared cascade tree (JSON)", "hint": "Required if cascade_topology_source = engineer_declared. JSON array of {node_id, parent_node_id, node_kind, feeder{...}}.", "answer_type": "struct_list", "required": false, "item_schema": {
        "type": "object",
        "required": ["node_id", "node_kind"],
        "properties": {
          "node_id":         { "type": "string" },
          "parent_node_id":  { "type": "string" },
          "node_kind":       { "enum": ["hv_source", "transformer_secondary", "board_incoming", "board_busbar", "board_outgoing_feeder", "final_circuit_endpoint"] },
          "designation":     { "type": "string" },
          "feeder":          { "type": "object" }
        }
      }
    }
  ]
}
```

- [ ] **Step 2: Validate + commit**

```bash
python3 - <<'PY'
import json, re
VALID_TYPES = {"enum", "int", "float", "boolean", "text", "enum_list", "struct_list"}
ITEM_REQUIRED = {"id", "label", "answer_type", "required"}
doc = json.load(open('electrical/fault-level/inputs.json'))
errs = []
for i, item in enumerate(doc['items']):
    if not ITEM_REQUIRED.issubset(item.keys()):
        errs.append(f"{item.get('id', '?')}: missing required keys")
    at = item.get('answer_type')
    if at not in VALID_TYPES: errs.append(f"{item['id']}: bad answer_type")
    if at in {'enum', 'enum_list'} and 'options' not in item: errs.append(f"{item['id']}: missing options")
    if at == 'struct_list' and 'item_schema' not in item: errs.append(f"{item['id']}: missing item_schema")
print(f'items: {len(doc["items"])}; errors: {len(errs)}')
for e in errs: print(f'  - {e}')
PY
git add electrical/fault-level/inputs.json
git commit -m "feat: fault-level inputs.json — 16-item discovery taxonomy per WI1"
```

---

## Task 13: Create `skill.manifest.json`

**Files:**
- Create: `electrical/fault-level/skill.manifest.json`

The manifest. References 21 specific standards files (8 IEC60909 + 2 IEC60617 + 3 GB + 4 EU/INT + 4 US).

- [ ] **Step 1: Write the file**

```json
{
  "skill": "fault-level",
  "version": "1.0.0",
  "discipline": "electrical",
  "subdiscipline": "fault-analysis",
  "description": "Produces IEC 60909-0 prospective short-circuit current (Ik\" + ipk + X/R) cascade IR for any node in a project's distribution tree, HV+LV. Models four source types: utility transformer, standby generator (with subtransient decrement), UPS (current-limited), and induction motor back-feed. Emits stable fault-level intent that resolves db-layout selectivity tool_call_pending entries.",
  "status": "beta",
  "licence": "MIT",
  "inputs_path": "inputs.json",
  "inputs": [
    "jurisdiction", "project-id", "supply-voltage", "hv-side", "primary-transformer",
    "standby-generator", "ups", "motor-load", "cascade-topology"
  ],
  "outputs": ["fault-level-ir"],
  "output_schema": "electrical/fault-level/schemas/fault-level-ir.schema.json",
  "produces_intent": "fault-level",
  "produces_intent_schema": "electrical/fault-level/schemas/fault-level-intent.schema.json",
  "consumes_intents": ["db-layout-rollup"],
  "standards": [
    "shared/standards/electrical/IEC60909/part0-fundamentals.json",
    "shared/standards/electrical/IEC60909/part0-method.md",
    "shared/standards/electrical/IEC60909/peak-factor-kappa.json",
    "shared/standards/electrical/IEC60909/voltage-factor-c.json",
    "shared/standards/electrical/IEC60909/source-impedances.json",
    "shared/standards/electrical/IEC60909/transformer-zpu-table.json",
    "shared/standards/electrical/IEC60909/generator-subtransient-tables.json",
    "shared/standards/electrical/IEC60909/motor-contribution-rules.json",
    "shared/standards/electrical/IEC60617/symbol-index.json",
    "shared/standards/electrical/IEC60617/part7-switchgear.json",
    "shared/standards/electrical/BS7671/reg434-fault-current.json",
    "shared/standards/electrical/BS7671/pscc-determination.md",
    "shared/standards/electrical/BS7671/appendix4-cable-ratings.json",
    "shared/standards/electrical/IEC60364/fault-current.json",
    "shared/standards/electrical/IEC60364/pscc-determination.md",
    "shared/standards/electrical/IEC60364/part5-52-cable-ratings-copper.json",
    "shared/standards/electrical/IEC60364/part5-52-cable-ratings-aluminium.json",
    "shared/standards/electrical/NFPA70/chapter1-general.json",
    "shared/standards/electrical/NFPA70/art240-overcurrent.json",
    "shared/standards/electrical/NFPA70/ocpd-coordination.json",
    "shared/standards/electrical/NFPA70/chapter9-tables.json"
  ],
  "calculations": [
    "shared/calculations/electrical/iec60909-cascade.json"
  ],
  "ontology": [
    "electrical/fault-level/ontology/source-types.json",
    "electrical/fault-level/ontology/cascade-node-kinds.json"
  ],
  "rules": [
    "electrical/fault-level/rules/source-impedance-defaults.yaml",
    "electrical/fault-level/rules/motor-contribution-thresholds.yaml",
    "electrical/fault-level/rules/voltage-factor-c-selection.yaml",
    "electrical/fault-level/rules/ups-current-limiting.yaml",
    "electrical/fault-level/rules/peak-factor-kappa.yaml"
  ],
  "constraints": [
    "electrical/fault-level/constraints/breaker-icn-vs-ifault.yaml",
    "electrical/fault-level/constraints/busbar-ipk-vs-cascade-ipk.yaml",
    "electrical/fault-level/constraints/cable-i2t-vs-cascade.yaml",
    "electrical/fault-level/constraints/source-impedance-bounds.yaml"
  ],
  "validators": [
    "electrical/fault-level/validation/cascade-tree-integrity.yaml",
    "electrical/fault-level/validation/ifault-monotonicity.yaml",
    "electrical/fault-level/validation/tool-call-resolved.yaml",
    "electrical/fault-level/validation/intent-shape.yaml"
  ],
  "prompts": {
    "generator": "electrical/fault-level/prompts/generator.md",
    "validator": "electrical/fault-level/prompts/validator.md",
    "reviewer":  "electrical/fault-level/prompts/reviewer.md"
  },
  "evals": [
    "electrical/fault-level/evals/eval-01-uk-domestic-cu-cascade.yaml",
    "electrical/fault-level/evals/eval-02-tpn-commercial-with-gen.yaml",
    "electrical/fault-level/evals/eval-03-undersized-breaker-trap.yaml",
    "electrical/fault-level/evals/eval-04-missing-source-data.yaml",
    "electrical/fault-level/evals/eval-05-jurisdiction-us-with-hv.yaml",
    "electrical/fault-level/evals/eval-06-rationale-block.yaml",
    "electrical/fault-level/evals/eval-07-multi-source-coordination.yaml",
    "electrical/fault-level/evals/eval-08-induction-motor-contribution.yaml",
    "electrical/fault-level/evals/eval-09-intent-shape.yaml"
  ],
  "examples": [
    "electrical/fault-level/examples/uk-domestic-single-source/",
    "electrical/fault-level/examples/intl-commercial-with-genset/",
    "electrical/fault-level/examples/us-industrial-with-motors/"
  ],
  "compatible_runtimes": ["DraftsMan >= 1.0", "Claude Code", "OpenClaw", "any-llm-agent"],
  "changelog": "electrical/fault-level/CHANGELOG.md"
}
```

- [ ] **Step 2: Validate + consumption-pattern proof + commit**

```bash
python3 - <<'PY'
import json, os
m = json.load(open('electrical/fault-level/skill.manifest.json'))
folders = [s for s in m['standards'] if s.endswith('/')]
files = [s for s in m['standards'] if not s.endswith('/')]
print(f'standards: {len(files)} files, {len(folders)} folders')
assert len(folders) == 0 and len(files) == 21
missing = [f for f in m['standards'] if not os.path.isfile(f)]
print(f'missing on disk: {len(missing)}')
for x in missing: print(f'  - {x}')
assert not missing
print('Consumption-pattern proof: PASS')
PY
git add electrical/fault-level/skill.manifest.json
git commit -m "feat: fault-level manifest — 21 specific standards files (consumption-pattern proof)"
```

Expected: `21 files, 0 folders`, `missing: 0`, `Consumption-pattern proof: PASS`

---

## Task 14: Create 5 rules YAMLs

**Files:**
- Create: `electrical/fault-level/rules/source-impedance-defaults.yaml`
- Create: `electrical/fault-level/rules/motor-contribution-thresholds.yaml`
- Create: `electrical/fault-level/rules/voltage-factor-c-selection.yaml`
- Create: `electrical/fault-level/rules/ups-current-limiting.yaml`
- Create: `electrical/fault-level/rules/peak-factor-kappa.yaml`

- [ ] **Step 1: Write source-impedance-defaults.yaml**

```yaml
rule_set: source-impedance-defaults
version: 1.0.0
applies_to: [GB, EU, INT, US]

# Defaults for source impedance when engineer doesn't provide nameplate data.
# Used by generator.md Steps 5 + 6.
# THESE ARE FALLBACK ONLY — real designs use nameplate Zpu / X"d / etc.

defaults_by_source_type:
  utility_transformer:
    zpu_percent_by_rating:
      _reference: shared/standards/electrical/IEC60909/transformer-zpu-table.json
      below_400_kva: 4.0
      400_to_1000_kva: 4.0
      1000_to_2500_kva: 5.0
      2500_to_5000_kva: 6.0
      above_5000_kva: 7.0
    x_over_r_default: 6
    flag_when_default_used: "Utility transformer Zpu = {value}% assumed from IEC60909/transformer-zpu-table.json (kVA-banded default). Real design must use nameplate Zpu."

  generator:
    x_d_doubleprime_pu_default: 0.15
    x_d_prime_pu_default: 0.25
    x_d_pu_default: 1.20
    x_over_r_default: 8
    flag_when_default_used: "Generator X\"d = {value} pu assumed from IEC60909/generator-subtransient-tables.json. Real design must use manufacturer data."

  ups:
    i_rated_multiplier_first_cycle: 2.0
    bypass_switchover_ms: 5
    flag_when_default_used: "UPS first-cycle contribution = 2 × I_rated assumed. UPS manufacturer data must confirm output current limit."

  motor_aggregate:
    ilr_default: 5.5
    flag_when_default_used: "Motor ILR = 5.5 × FLC assumed (IEC Letter K). Real design must verify per motor nameplate code letter."
```

- [ ] **Step 2: Write motor-contribution-thresholds.yaml**

```yaml
rule_set: motor-contribution-thresholds
version: 1.0.0

# IEC 60909-0:2016 §4.5 motor contribution inclusion rules.
# Used by generator.md Step 8.

inclusion_threshold:
  current_threshold: "Σ P_motors_kW ≥ 1% × Sk\"_at_fault"
  rationale: "Motors contribute via subtransient reactance for 1-2 cycles. Below 1% threshold, contribution is rounding error."
  reference: shared/standards/electrical/IEC60909/motor-contribution-rules.json

calculation:
  formula_aggregate: "Ik\"_motor = ILR_avg × ΣP_motor / (√3 × V)"
  default_ilr_avg: 5.0
  rationale: "ILR average for HVAC + general industrial motors (IEC Letter K)"

decay:
  ib_at_breaking_time: "Ib_motor ≈ 0.5 × Ik\"_motor for tmin ≥ 30 ms"
  ik_steady_state: 0
  rationale: "Motor contribution decays within 1-2 cycles (20-40 ms at 50 Hz). Negligible at steady state."

exclusions:
  - "VFD-driven motors (VFD blocks back-feed via DC link)"
  - "Soft-starter motors in run mode (soft-starter bypassed; treat as DOL)"
  - "Stopped or standby motors (no rotational kinetic energy)"
```

- [ ] **Step 3: Write voltage-factor-c-selection.yaml**

```yaml
rule_set: voltage-factor-c-selection
version: 1.0.0

# IEC 60909-0:2016 Table 1 — voltage factor c selection rules.
# Used by generator.md Steps 4 + 10.

selection_rules:
  for_breaker_breaking_capacity_check:
    c_value: 1.05
    use_when_lv: "Un ≥ 100 V"
    use_when_mv_hv: "Un > 1 kV (use c=1.10 instead)"
    rationale: "Maximum Ik\" — ensures breaker can interrupt worst-case fault current"

  for_ads_protection_setting:
    c_value: 0.95
    use_when_lv: "Un ≥ 100 V"
    use_when_mv_hv: "Un > 1 kV (use c=1.00 instead)"
    rationale: "Minimum Ik\" — ensures protection responds even at supply under-voltage"

  for_cascade_selectivity:
    use_both: true
    rationale: "Upstream breaker rated to c_max Ifault; downstream protection set to c_min Ifault sensitivity"

reference_file: shared/standards/electrical/IEC60909/voltage-factor-c.json
```

- [ ] **Step 4: Write ups-current-limiting.yaml**

```yaml
rule_set: ups-current-limiting
version: 1.0.0

# UPS / battery inverter fault contribution rules (IEC 60909-0 + IEC 62040-3).
# Used by generator.md Step 7.

contribution_model:
  first_half_cycle:
    duration_ms: 8.33
    duration_ms_at_60hz: 6.94
    current_basis: "I_rated_UPS_a × 2.0 (IGBT/IGCT current sensor limit)"
    rationale: "Inverter output current limited by IGBT/IGCT switching protection. Typical limit 2-3× I_rated."

  after_first_cycle:
    behavior: "UPS transitions to bypass within 4-5 ms during sustained fault"
    source_after_bypass: "Upstream utility / generator path — UPS effectively absent"
    rationale: "UPS internal protection trips inverter; bypass switch closes"

modelling_decision:
  for_first_cycle_breaker_rating: "Include UPS contribution + utility/gen contribution (worst case)"
  for_sustained_fault_protection: "Exclude UPS; treat as bypass-fed from upstream"
  for_ads_check: "Use sustained-fault path (post-bypass)"

manufacturer_specific:
  typical_static_ups_2024: { current_limit_x_rated: 2.0, bypass_ms: 4 }
  typical_modular_ups_2024: { current_limit_x_rated: 2.5, bypass_ms: 3 }
  flow_battery_inverter: { current_limit_x_rated: 1.2, bypass_ms: 8, _note: "Conservative; varies widely" }
```

- [ ] **Step 5: Write peak-factor-kappa.yaml**

```yaml
rule_set: peak-factor-kappa
version: 1.0.0

# IEC 60909-0:2016 §4.3 + IEC 60865-1 — peak factor κ calculation.
# Used by generator.md Step 5.

formula:
  expression: "κ = 1.02 + 0.98 × exp(-3 × R/X)"
  ipk_relationship: "ipk = κ × √2 × Ik\""
  reference: shared/standards/electrical/IEC60909/peak-factor-kappa.json

selection_per_path:
  rule: "Compute κ at each cascade node using the X/R at that node (not at the source)"
  rationale: "Cable resistance increases R faster than X as you walk downstream — κ decreases"

asymptotic_bounds:
  min: { value: 1.0, condition: "Pure resistive (R/X → ∞)" }
  max: { value: 2.0, condition: "Pure inductive (R/X → 0)" }

simplification:
  for_lv_cable_dominated_paths:
    typical_xr: "1-3"
    typical_kappa: "1.1-1.3"
    note: "Use formula even when range is narrow"
```

- [ ] **Step 6: Validate + commit**

```bash
python3 -c "
import yaml
for f in ['source-impedance-defaults', 'motor-contribution-thresholds', 'voltage-factor-c-selection', 'ups-current-limiting', 'peak-factor-kappa']:
    yaml.safe_load(open(f'electrical/fault-level/rules/{f}.yaml'))
    print(f'{f}.yaml: OK')
"
git add electrical/fault-level/rules/
git commit -m "feat: fault-level rules — 5 YAMLs (source defaults, motor thresholds, c-factor, UPS, kappa)"
```

---

## Task 15: Create 4 constraints YAMLs

**Files:**
- Create: `electrical/fault-level/constraints/breaker-icn-vs-ifault.yaml`
- Create: `electrical/fault-level/constraints/busbar-ipk-vs-cascade-ipk.yaml`
- Create: `electrical/fault-level/constraints/cable-i2t-vs-cascade.yaml`
- Create: `electrical/fault-level/constraints/source-impedance-bounds.yaml`

- [ ] **Step 1: Write breaker-icn-vs-ifault.yaml**

```yaml
constraint_set: breaker-icn-vs-ifault
version: 1.0.0

# Every breaker downstream must have Icn ≥ Ik"max at its installation point.
# Used by generator.md Step 12 to populate selectivity_implications.

constraint:
  rule: "breaker.icn_ka >= ifault_ka_max_at_breaker"
  rationale: "Per IEC 60947-2 / IEC 60898 / NEC 110.9 — breaker must safely interrupt the worst-case fault"

severity_levels:
  critical:
    condition: "breaker.icn_ka < ifault_ka_max"
    flag: "BREAKER_UNDERRATED_FOR_FAULT_LEVEL"
    recommendation: "Replace with higher Icn breaker OR add upstream cascade-rated current limiter (HRC fuse, current-limiting breaker)"

  warning:
    condition: "breaker.icn_ka < 1.2 × ifault_ka_max"
    flag: "BREAKER_MARGIN_LOW"
    recommendation: "20% headroom recommended for future-proofing"

cascade_rating_alternative:
  per_iec_60947_2_annex_d: "Series ratings allow lower-Icn downstream breaker if upstream device demonstrates compatible let-through"
  manufacturer_table_required: "Cascade ratings are manufacturer-specific (Hager, Schneider, Eaton, ABB cascade tables)"
  emit_in_selectivity_implications: "If cascade rating applied: note in recommendation field"
```

- [ ] **Step 2: Write busbar-ipk-vs-cascade-ipk.yaml**

```yaml
constraint_set: busbar-ipk-vs-cascade-ipk
version: 1.0.0

# Assembly's rated peak withstand current (Ipk) must exceed prospective ipk at busbar.
# Used by generator.md Step 12 + db-layout-side validation.

constraint:
  rule: "busbar.ipk_withstand_ka >= ipk_ka_at_busbar"
  rationale: "Per IEC 61439-1 clause 5.3.7 — busbar mechanical force from peak current must not damage assembly"

ipk_derivation:
  formula: "ipk = κ × √2 × Ik\"max"
  k_factor_source: "IEC 60865-1 κ formula (see rules/peak-factor-kappa.yaml)"

cross_reference:
  related_constraint: "Icw 1-sec withstand must also exceed RMS Ifault — separate check"
  related_file: "electrical/db-layout/validation/busbar-loading.yaml"

severity_levels:
  critical:
    condition: "busbar.ipk_withstand_ka < ipk_ka"
    flag: "BUSBAR_IPK_INADEQUATE"
    recommendation: "Increase assembly rating to higher Ipk class OR add upstream current-limiting"
```

- [ ] **Step 3: Write cable-i2t-vs-cascade.yaml**

```yaml
constraint_set: cable-i2t-vs-cascade
version: 1.0.0

# Cable adiabatic survival: cable I²t withstand ≥ protective device I²t let-through at Ifault.
# Used by generator.md Step 12.

constraint:
  rule: "k² × S² >= I²t_let_through"
  rationale: "Per BS 7671 Reg 434.5 / IEC 60364-4-43 434.5 / NEC 240.4 — cable must survive thermal energy of fault"

variables:
  k: "Material constant from BS 7671 Table 54.7 / IEC 60364-5-54 Table 54.2 (Cu 70°C = 115; XLPE 90°C = 143)"
  S: "Cable phase conductor csa (mm²)"
  i_squared_t: "Energy let-through from protective device — manufacturer-specific I²t curve at fault current"

simplification_for_thermal_region:
  applicable_when: "Fault current is in the thermal (long) region of the trip curve"
  formula: "I²t = I² × t_trip from device time/current curve"
  note: "For instantaneous magnetic trip region: must use manufacturer I²t let-through data — not I² × t"

cross_reference:
  related_calc: "shared/calculations/electrical/cpc-adiabatic.json"
  consumers: ["electrical/cable-sizing (skill, future)", "electrical/db-layout (validation)"]
```

- [ ] **Step 4: Write source-impedance-bounds.yaml**

```yaml
constraint_set: source-impedance-bounds
version: 1.0.0

# Sanity bounds on engineer-declared source-impedance values.
# Used by generator.md Step 5/6 to flag impossible inputs.

transformer_zpu_bounds:
  min_realistic_pct: 3.0
  max_realistic_pct: 12.0
  flag_below_min: "TX Zpu < 3% — flag as suspicious; recheck nameplate (typical 4-7%)"
  flag_above_max: "TX Zpu > 12% — flag as suspicious; very high impedance (most likely typo, or stand-by transformer)"

generator_x_d_doubleprime_bounds:
  min_realistic_pu: 0.08
  max_realistic_pu: 0.30
  flag_below_min: "Generator X\"d < 0.08 pu — flag as suspicious"
  flag_above_max: "Generator X\"d > 0.30 pu — flag as suspicious; check machine type (turbogen ≈ 0.20)"

x_over_r_bounds:
  min_realistic: 0.5
  max_realistic: 50
  flag_below_min: "X/R < 0.5 — flag as suspicious"
  flag_above_max: "X/R > 50 — extremely inductive; check (typical LV cable 1-3, transformer 5-10, gen 15-30)"

hv_pscc_bounds:
  min_realistic_ka: 5
  max_realistic_ka: 50
  flag_below_min_at_primary: "HV PSCC < 5 kA — very weak supply; flag for confirmation with DNO"
  flag_above_max_at_primary: "HV PSCC > 50 kA — unusually strong; check decimal place"
```

- [ ] **Step 5: Validate + commit**

```bash
python3 -c "
import yaml
for f in ['breaker-icn-vs-ifault', 'busbar-ipk-vs-cascade-ipk', 'cable-i2t-vs-cascade', 'source-impedance-bounds']:
    yaml.safe_load(open(f'electrical/fault-level/constraints/{f}.yaml'))
    print(f'{f}.yaml: OK')
"
git add electrical/fault-level/constraints/
git commit -m "feat: fault-level constraints — breaker Icn + busbar Ipk + cable I²t + source-Z bounds"
```

---

## Task 16: Create `prompts/generator.md` (14-step chain)

**Files:**
- Create: `electrical/fault-level/prompts/generator.md`

The heart of the skill. 14-step IEC 60909 cascade computation chain.

- [ ] **Step 1: Write the prompt**

````markdown
# Fault-Level Skill — Generator Prompt

You are an experienced electrical engineer producing a prospective short-circuit current (Ik" + ipk + X/R) cascade IR per IEC 60909-0:2016. The IR covers every node in a project's distribution tree, from HV primary supply through to every final-circuit endpoint.

This prompt drives the **v1.0 single-stage** mode (no sub-stages planned at v1).

**Your job:** produce a single JSON document conforming to `electrical/fault-level/schemas/fault-level-ir.schema.json`. One IR per project (not per board).

**Inputs:**
- The engineer's answers to `inputs.json` (16-item discovery taxonomy)
- (Optional) `cross_drawing_context` with `db-layout-rollup` intent for cascade topology

**Output:** A single IR JSON conforming to the schema, including a structured `rationale` block per WI2.

**ALSO emit a `fault-level` intent** (slim downstream subset) alongside the IR. db-layout consumes this intent to resolve its selectivity tool_call_pending entries.

---

## Step 1 — Discovery check

Verify all required inputs are present. Record consumed intents in `ir.meta.consumed_intents[]`:
- If `cross_drawing_context.db-layout-rollup` is present → use it for cascade topology
- Else if `inputs.cascade_engineer_declared` is provided → use as fallback

For any missing source data, emit a flag: `"no <source> data; using IEC60909 default per source-impedance-defaults.yaml"`.

---

## Step 2 — Jurisdiction-gated standards file load

**Always load:**
- `shared/standards/electrical/IEC60909/part0-fundamentals.json` (Ik" definition, c-factor, near/far classification)
- `shared/standards/electrical/IEC60909/part0-method.md` (calculation walkthrough)
- `shared/standards/electrical/IEC60909/peak-factor-kappa.json` (κ formula)
- `shared/standards/electrical/IEC60909/voltage-factor-c.json` (c=1.05/0.95)
- `shared/standards/electrical/IEC60909/source-impedances.json` (unified source reference)
- `shared/standards/electrical/IEC60909/transformer-zpu-table.json` (Zpu defaults)
- `shared/standards/electrical/IEC60909/generator-subtransient-tables.json` (X"d defaults)
- `shared/standards/electrical/IEC60909/motor-contribution-rules.json` (§4.5 threshold)
- `shared/standards/electrical/IEC60617/symbol-index.json` (always)
- `shared/standards/electrical/IEC60617/part7-switchgear.json` (always)

**Based on `inputs.jurisdiction`:**

- **GB** → load:
  - `shared/standards/electrical/BS7671/reg434-fault-current.json`
  - `shared/standards/electrical/BS7671/pscc-determination.md`
  - `shared/standards/electrical/BS7671/appendix4-cable-ratings.json` (R+X per cable)

- **EU** or **INT** → load:
  - `shared/standards/electrical/IEC60364/fault-current.json`
  - `shared/standards/electrical/IEC60364/pscc-determination.md`
  - `shared/standards/electrical/IEC60364/part5-52-cable-ratings-copper.json`
  - `shared/standards/electrical/IEC60364/part5-52-cable-ratings-aluminium.json`

- **US** → load:
  - `shared/standards/electrical/NFPA70/chapter1-general.json` (NEC 110.9 interrupting rating)
  - `shared/standards/electrical/NFPA70/art240-overcurrent.json`
  - `shared/standards/electrical/NFPA70/ocpd-coordination.json`
  - `shared/standards/electrical/NFPA70/chapter9-tables.json` (Table 9 R+X)

**Do NOT load standards files outside the jurisdiction.** Consumption-pattern proof: ~12-15 files in context, not the full layers.

---

## Step 3 — Cascade topology assembly

Build the cascade tree from one of two sources:

**Path A (preferred): db-layout-rollup intent**
- Walk `boards[]` via `fed_from` pointers
- For each board: emit nodes for `board_incoming`, `board_busbar`, `board_outgoing_feeder` per outgoing feeder
- For each outgoing circuit: emit `final_circuit_endpoint` node
- Set `parent_node_id` per the tree structure

**Path B (fallback): engineer-declared cascade**
- Use `inputs.cascade_engineer_declared` JSON array directly
- Each entry already has `node_id` + `parent_node_id` + `node_kind` + `feeder`

**node_id naming convention:** path-like `HV-1` → `TX-1` → `MSB-1` → `MSB-1.F01` → `MSB-1.F01.DB-L1` → `MSB-1.F01.DB-L1.C03`

Emit `ir.cascade[]` with each node having `node_id`, `parent_node_id`, `node_kind`, `designation`, and the `feeder` data if applicable.

---

## Step 4 — HV-side modelling (only if HV side present)

If `inputs.hv_side_present == true`:

State in `ir.project_supply.hv_side`:
- `voltage_kv`, `network_arrangement`, `declared_pscc_at_primary_ka`, `x_over_r_at_primary`

Compute source impedance ZQ:
- If declared PSCC: `ZQ = c × U²_n / Sk"` where `Sk" = √3 × U_n × PSCC`
- Split into RQ + jXQ using `x_over_r_at_primary`

Apply both c=1.05 (Ik"max) and c=0.95 (Ik"min) per `voltage-factor-c.json`.

If no HV side → skip; LV source is at network terminals.

---

## Step 5 — Transformer impedance

For utility transformer (always present unless source is pure generator/UPS):

`Z_TX_ohm = (Zpu / 100) × (U²_LV / S_TX_kVA × 1000)` (result in ohms)

Split into R + X using transformer X/R (typical 5-10 for distribution):
- `X_TX = Z_TX × X/R / √(1 + (X/R)²)`
- `R_TX = Z_TX / √(1 + (X/R)²)`

Z_TX adds in series with ZQ to form total source impedance at the transformer LV terminals.

Emit transformer as a node in cascade: `node_kind: "transformer_secondary"`.

---

## Step 6 — Generator modelling (if standby present)

If `inputs.standby_generator_present == true`:

State in `ir.sources` an entry with `kind: "generator"`:
- `contribution_method: "subtransient_decrement"`
- Use X"d_pu (typical 0.15) → first-cycle Ik"
- Decrement profile: X"d → X'd (~100ms) → Xd (steady-state)

Generator impedance at LV terminals:
- `X"d_ohm = X"d_pu × (U²_LV / S_gen_kVA × 1000)`

When project is on generator (transfer scheme = generator mode):
- Source becomes generator-only; utility path disconnected
- Use near-from-generator method per IEC 60909-0 §3.5

When project is on utility:
- Generator contributes nothing (output breaker open)

For BOTH-modes IR: emit a flag that this is the worst-case (per IEC 60909 typically utility mode has higher Ik").

---

## Step 7 — UPS / inverter modelling (if present)

If `inputs.ups_present == true`:

State in `ir.sources` an entry with `kind: "ups"`:
- `contribution_method: "current_limited"`
- First-half-cycle: Ik"_UPS = 2 × I_rated_UPS (manufacturer-specific; per `ups-current-limiting.yaml` default)
- After bypass (within 4-5 ms): UPS path becomes utility-fed

**For first-cycle breaker rating:** include UPS contribution + utility (sum complex Ifaults).

**For sustained-fault protection:** UPS is bypassed → use utility path only.

Emit `decrement_profile` for the source describing this transition.

---

## Step 8 — Induction motor contribution

If `inputs.motor_load_kw > 0` AND `motor_load_kw / source_kva ≥ 0.01`:

Per IEC 60909-0:2016 §4.5 (2016 amendment tightened threshold from 5% to 1%):

State in `ir.sources` an entry with `kind: "motor_aggregate"`:
- `contribution_method: "locked_rotor"`
- Aggregate Ik"_motor = `ILR_avg × ΣP_motors / (√3 × V)`
- Default ILR_avg = 5.0 (IEC Letter K)

Per `motor-contribution-thresholds.yaml`:
- Decay: Ib_motor ≈ 0.5 × Ik"_motor at tmin ≥ 30 ms
- Ik_motor steady-state = 0

Include motor contribution in Ik"max at every cascade node downstream of (or co-located with) the motor connection point.

---

## Step 9 — Cable impedance per cascade stage

For each cable in the cascade (HV cable, LV main feeder, sub-DB feeder, final-circuit):

Look up R + X per metre at conductor operating temperature:
- **GB:** `BS7671/appendix4-cable-ratings.json` Tables 4D5 (R), 4F (X)
- **EU/INT:** `IEC60364/part5-52-cable-ratings-copper.json` or `-aluminium.json`
- **US:** `NFPA70/chapter9-tables.json` (Table 9 ac resistance + reactance)

For each cascade node, the feeder impedance ADDS to the upstream total:
- `Z_total_at_node = Z_total_at_parent + (r × L + jx × L)`

Emit `cascade[*].feeder` (length, csa, material, insulation) and `cascade[*].z_addition_ohm` ({r, x}) per node.

---

## Step 10 — Cascade Ifault computation

For each cascade node:

```
Ik"_max = c_max × V / (√3 × |Z_total|)   with c_max = 1.05 (LV)
Ik"_min = c_min × V / (√3 × |Z_total|)   with c_min = 0.95 (LV)
```

Where `|Z_total| = √(R_total² + X_total²)`.

For single-phase nodes (UK domestic, US 120V): replace `√3` with appropriate divisor per IEC 60909-0 §1.3.

Emit `cascade[*].ifault_ka_max`, `cascade[*].ifault_ka_min`, `cascade[*].x_over_r_at_node`, `cascade[*].z_total_ohm`.

---

## Step 11 — Peak current computation

For each cascade node:

```
κ = 1.02 + 0.98 × exp(-3 × R/X)
ipk = κ × √2 × Ik"_max
```

Per `peak-factor-kappa.json` table — but **compute** rather than lookup; the formula is closed-form.

Emit `cascade[*].ipk_ka`.

---

## Step 12 — Tool call dispatch

**Critical:** This skill **never inline-computes** the cascade math. The full IEC 60909-0 method (especially with multi-source superposition + near-generator decrement) requires deterministic Python execution.

Per WI3 deferral pattern:
- Declare `calc.iec60909_cascade` (contract at `shared/calculations/electrical/iec60909-cascade.json`)
- Each cascade node where tool execution has NOT yet happened: emit `cascade[*].tool_call_pending: true` and the engineer-input-derived Ik" values as fallback
- When the runtime tool exists and executes: re-emit cascade with computed values + `tool_call_pending: false`

This skill is a tool-call dispatcher with engineer-input fallback. Never invent Ifault values.

---

## Step 13 — Selectivity implications

For each protective device in the cascade (every MCB / MCCB / ACB / fuse):

Build `selectivity_implications[*]`:
- `breaker_id`, `breaker_rating_a`, `breaker_icn_ka` (from db-layout intent if present, or engineer declared)
- `ifault_at_breaker_ka` = `cascade[node_with_this_breaker].ifault_ka_max`
- `adequate = (breaker_icn_ka >= ifault_at_breaker_ka)`
- `recommendation`:
  - If adequate: "Icn {value}kA sufficient for Ik\"max {ifault}kA"
  - If not: "BREAKER_UNDERRATED — replace with Icn ≥ {ifault}kA OR add upstream cascade-rated current limiter"

---

## Step 14 — Compliance + rationale

Roll up flags:
- **CRITICAL** if any breaker.icn < cascade.ifault_ka_max → `BREAKER_UNDERRATED_FOR_FAULT_LEVEL`
- **WARNING** if motor contribution > 20% of total Ifault → `MOTOR_CONTRIBUTION_MATERIAL`
- **WARNING** if HV PSCC declared without c-factor → `HV_C_FACTOR_NOT_APPLIED`
- **INFO** if any cascade node has `tool_call_pending: true` → `TOOL-CALL-PENDING`

Emit `rationale` block per WI2 — 8 sections:

1. **Source Specification** — utility / gen / UPS / motors with kVA + Z%
2. **Cascade Topology** — tree structure source (db-layout intent OR engineer)
3. **HV-side Assumptions** — c-factor selection, PSCC source
4. **Transformer + Source Impedances** — Zpu used, X/R
5. **Motor Contribution Assessment** — threshold check, ΣP_motor / Sk"
6. **Per-node Ifault Computation** — table summary of Ik"max + Ik"min + ipk at key nodes
7. **Selectivity Implications** — adequate / inadequate summary, recommendations
8. **Compliance + Assumptions** — flag list + assumptions captured

Each section: `{title, summary, decisions[]}`. Each decision: `{label, summary, rule, code_clause, inputs}`.

---

## Final output

Emit two JSON documents:

1. **Single fault-level IR** (`fault-level-ir.schema.json`) — full audit trail
2. **fault-level intent** (`fault-level-intent.schema.json`) — slim downstream subset:
   - `project_id`, `source_summary`, `fault_currents[]`
   - Each `fault_currents[*]`: `node_id`, `node_kind`, `ifault_ka_max`, `ifault_ka_min`, `ipk_ka`, `x_over_r_ratio`, `z_total_ohm`

**Do not invent values.** If `tool_call_pending: true`, the engineer-input fallback is used; runtime tool will re-compute.

**Do not paraphrase IEC 60909-0 clauses.** Cite verbatim (e.g., "IEC 60909-0:2016 §3.7 Table 1", "IEC 60865-1:2011 §2.2 peak factor").

**Do not skip the rationale block.** It is the engineer's IEC 60909 audit trail.
````

- [ ] **Step 2: Validate file + standards file references**

```bash
test -s electrical/fault-level/prompts/generator.md && echo OK
n=$(grep -c "^## Step " electrical/fault-level/prompts/generator.md) && echo "Step markers: $n (expected 14)"
python3 -c "
text = open('electrical/fault-level/prompts/generator.md').read()
required = [
    'IEC60909/part0-fundamentals.json',
    'IEC60909/part0-method.md',
    'IEC60909/peak-factor-kappa.json',
    'IEC60909/voltage-factor-c.json',
    'IEC60909/source-impedances.json',
    'IEC60909/transformer-zpu-table.json',
    'IEC60909/generator-subtransient-tables.json',
    'IEC60909/motor-contribution-rules.json',
    'IEC60617/symbol-index.json',
    'IEC60617/part7-switchgear.json',
    'BS7671/reg434-fault-current.json',
    'BS7671/pscc-determination.md',
    'BS7671/appendix4-cable-ratings.json',
    'IEC60364/fault-current.json',
    'IEC60364/pscc-determination.md',
    'IEC60364/part5-52-cable-ratings-copper.json',
    'IEC60364/part5-52-cable-ratings-aluminium.json',
    'NFPA70/chapter1-general.json',
    'NFPA70/art240-overcurrent.json',
    'NFPA70/ocpd-coordination.json',
    'NFPA70/chapter9-tables.json',
]
hits = sum(1 for f in required if f in text)
print(f'Specific standards files referenced: {hits} / {len(required)}')
assert hits == len(required), f'Consumption-pattern proof FAILED: only {hits}/{len(required)} files referenced'
print('Consumption-pattern proof: PASS')
"
```
Expected: `Step markers: 14`, `Specific standards files referenced: 21 / 21`, `Consumption-pattern proof: PASS`

- [ ] **Step 3: Commit**

```bash
git add electrical/fault-level/prompts/generator.md
git commit -m "feat: fault-level generator.md — 14-step IEC 60909 cascade chain, consumption-pattern proof"
```

---

## Task 17: Create `prompts/validator.md` (10 INV invariants)

**Files:**
- Create: `electrical/fault-level/prompts/validator.md`

- [ ] **Step 1: Write the file**

````markdown
# Fault-Level — Validator Prompt

You are validating a fault-level IR document produced by the `electrical/fault-level` skill generator.

## Input
- IR JSON at user-provided path
- Schemas at `electrical/fault-level/schemas/{fault-level-ir,fault-level-intent}.schema.json`

## Validation procedure

### 1. Schema validation
Run JSON-schema validation against `fault-level-ir.schema.json`. If invalid → STOP, emit `{"valid": false, "stage": "schema", "errors": [...]}`.

### 2. Cross-field invariants

**INV-1: Cascade tree integrity.**
Every `cascade[*].parent_node_id` must reference an existing `cascade[*].node_id`. No orphans (except root). No cycles.

**INV-2: Cascade node_id uniqueness.**
All `cascade[*].node_id` values unique. Path-like ids (`MSB-1.F01.DB-L1.C03`) preferred.

**INV-3: Voltage factor c applied.**
Every cascade node with `ifault_ka_max` AND `ifault_ka_min` has `ifault_ka_max > ifault_ka_min`. Difference within `(1.05/0.95 - 1) × ifault = 10.5%` tolerance.

**INV-4: Ifault monotonicity downstream.**
Walking the cascade tree from source: `cascade[child].ifault_ka_max ≤ cascade[parent].ifault_ka_max`. Exception: motor back-feed point may add to downstream — flag as expected.

**INV-5: Peak factor κ consistency.**
For every node, verify `ipk_ka ≈ κ × √2 × ifault_ka_max` where `κ = 1.02 + 0.98 × exp(-3 × R/X)`. Tolerance ±2%.

**INV-6: Breaker adequacy.**
Every entry in `selectivity_implications[*]`: if `adequate: false`, `compliance_summary.compliant` must be `false` AND a `BREAKER_UNDERRATED_FOR_FAULT_LEVEL` flag must exist.

**INV-7: Tool call pending consistency.**
If any `cascade[*].tool_call_pending == true`, top-level `flags` must include `TOOL-CALL-PENDING`.

**INV-8: Source impedance bounds.**
`project_supply.lv_source.z_percent` in [3.0, 12.0] OR flag in non_compliance_flags.
Source X/R in [0.5, 50] OR flag.

**INV-9: Standards citations format.**
Every `compliance_summary.non_compliance_flags[].code_clause` uses canonical format:
- IEC 60909: `"IEC 60909-0:2016 §N.N"` or `"IEC 60909-0:2016 Table N"`
- BS 7671: `"BS 7671:2018+A3 Reg N.N.N"`
- IEC 60364: `"IEC 60364-N-NN:YYYY clause N.N"`
- NEC: `"NEC 2023 Art NNN.N"`

**INV-10: Rationale presence.**
`rationale` block exists with `chat_summary` (40-500 chars) and `sections[]` with ≥8 entries.

### 3. Intent extraction validation

Project IR → `fault-level` intent shape. Validate against `fault-level-intent.schema.json`. Intent must contain `project_id`, `source_summary`, `fault_currents[]` (≥1 entry).

## Output

```json
{
  "valid": true | false,
  "stage": "schema" | "invariants" | "intent" | "passed",
  "errors": [
    {"code": "INV-N", "path": "$.cascade[2]", "message": "..."}
  ],
  "warnings": [...]
}
```

`valid: true` requires schema pass + all 10 invariants pass + intent extraction valid.
````

- [ ] **Step 2: Validate + commit**

```bash
test -s electrical/fault-level/prompts/validator.md && echo OK
n=$(grep -c "^\*\*INV-" electrical/fault-level/prompts/validator.md) && echo "INV count: $n (expected 10)"
git add electrical/fault-level/prompts/validator.md
git commit -m "feat: fault-level validator.md — 10 cross-field invariants"
```

---

## Task 18: Create `prompts/reviewer.md` (8 D dimensions)

**Files:**
- Create: `electrical/fault-level/prompts/reviewer.md`

- [ ] **Step 1: Write the file**

````markdown
# Fault-Level — Reviewer Prompt

You are a senior chartered electrical engineer reviewing a fault-level IR. You review **engineering judgement**, not schema (validator handles schema).

## Input
- IR JSON document
- For GB: BS 7671:2018+A3 Reg 434 + Appendix 3 + IEC 60909-0:2016
- For EU/INT: IEC 60364-4-43 + IEC 60909-0:2016
- For US: NEC 2023 Art 110.9 + 240.86 + IEC 60909-0:2016 method

## Review dimensions

Score each 1-5 with one-line justification.

### D1: Source modelling correctness
Are utility / gen / UPS / motor source models defensible?
- Utility Zpu within 4-7% typical?
- Generator X"d within 0.12-0.20 pu typical?
- UPS current limit within 2-3× rated typical?
- Motor inclusion only when ≥1% threshold per IEC 60909-0:2016 §4.5.1.2?

### D2: Cascade topology accuracy
Does the cascade tree match the project topology (boards, feeders, final circuits)?
- All boards covered?
- Path-like node_ids consistent?
- parent_node_id structure forms a valid tree?

### D3: Voltage factor c application
- c_max=1.05 used for Ik"max (breaker rating)?
- c_min=0.95 used for Ik"min (ADS / protection)?
- HV-side using c=1.10 / 1.00 if Un > 1 kV?

### D4: Near-or-far-from-generator classification
- Utility-fed (FG) used constant source method correctly?
- Generator-fed (NG) applied subtransient decrement μ for breaking time tmin?

### D5: Peak factor κ derivation
- κ computed per X/R at each node (not assumed constant)?
- Bounds (1 < κ < 2) respected?
- ipk = κ × √2 × Ik"max applied uniformly?

### D6: Selectivity implications correctness
- Every breaker in cascade has an implication entry?
- adequate: false only when truly under-rated?
- Recommendations cite manufacturer cascade tables or upstream current-limiting?

### D7: Tool call discipline
- `cascade[*].tool_call_pending: true` only when calc.iec60909_cascade hasn't executed?
- Engineer-input fallback values reasonable (within IEC 60909 source-impedance bounds)?
- Never invented values?

### D8: Rationale quality
- chat_summary 40-500 chars + tells engineer + chartered engineer review-ready?
- 8 sections all populated?
- Decisions cite IEC 60909-0 / BS 7671 / IEC 60364 / NEC verbatim?

## Output

```json
{
  "scores": {"D1": 5, "D2": 4, "D3": 5, "D4": 4, "D5": 5, "D6": 4, "D7": 5, "D8": 5},
  "justifications": {"D1": "...", ...},
  "verdict": "pass" | "pass-with-warnings" | "fail",
  "must_fix": ["..."],
  "should_fix": ["..."],
  "consider": ["..."]
}
```

- **pass**: all ≥4, no must-fix
- **pass-with-warnings**: all ≥3, D1/D3/D4 not below 4
- **fail**: any 1-2, OR D1/D3/D4 below 4

A failing fault-level design risks breaker under-rating and cable damage — not a place for false positives.
````

- [ ] **Step 2: Validate + commit**

```bash
test -s electrical/fault-level/prompts/reviewer.md && echo OK
n=$(grep -c "^### D" electrical/fault-level/prompts/reviewer.md) && echo "D count: $n (expected 8)"
git add electrical/fault-level/prompts/reviewer.md
git commit -m "feat: fault-level reviewer.md — 8 engineering-judgement dimensions"
```

---

## Task 19: Create 4 validation YAMLs

**Files:**
- Create: `electrical/fault-level/validation/cascade-tree-integrity.yaml`
- Create: `electrical/fault-level/validation/ifault-monotonicity.yaml`
- Create: `electrical/fault-level/validation/tool-call-resolved.yaml`
- Create: `electrical/fault-level/validation/intent-shape.yaml`

- [ ] **Step 1: Write cascade-tree-integrity.yaml**

```yaml
version: 1.0.0
applies_to_drawing_types: ["fault_level_study"]
checks:
  - id: tree-001-parent-exists
    name: Every cascade node's parent_node_id must reference an existing node_id
    severity: critical
    jsonpath: "$.cascade[*]"
    assert: "parent_node_id is null OR parent_node_id in [n.node_id for n in cascade]"
    message: "Node {node_id} has parent_node_id '{parent_node_id}' which does not exist"
    standard_ref: "design integrity check"

  - id: tree-002-no-cycles
    name: Cascade tree must be acyclic (no node is its own ancestor)
    severity: critical
    target: "cascade_tree_walk"
    assert: "walk_from_root_visits_every_node_exactly_once"
    message: "Cycle detected in cascade tree"
    standard_ref: "design integrity check"

  - id: tree-003-single-root
    name: Exactly one cascade root (parent_node_id is null)
    severity: critical
    target: "cascade_roots"
    assert: "count_of_nodes_with_null_parent == 1"
    message: "Cascade has {n} roots; expected exactly 1"
    standard_ref: "design integrity check"

  - id: tree-004-node-id-unique
    name: All cascade node_id values must be unique
    severity: critical
    target: "cascade_node_ids"
    assert: "len(set(node_ids)) == len(node_ids)"
    message: "Duplicate node_id detected"
    standard_ref: "design integrity check"
```

- [ ] **Step 2: Write ifault-monotonicity.yaml**

```yaml
version: 1.0.0
applies_to_drawing_types: ["fault_level_study"]
checks:
  - id: monotonic-001-downstream-decrease
    name: Ifault_max decreases (or stays equal) as you walk downstream
    severity: high
    jsonpath: "$.cascade[*]"
    when: "parent_node_id is not null"
    assert: "ifault_ka_max <= cascade[parent_node_id].ifault_ka_max + (motor_contribution if motor_aggregate_present)"
    message: "Node {node_id}: Ifault_max ({ifault_ka_max} kA) > parent's Ifault_max ({parent_ifault} kA) — violates monotonicity unless motor back-feed at this node"
    standard_ref: "IEC 60909-0:2016 §3.6"
    note: "Exception: motor back-feed point can add to Ifault — check sources[] for motor_aggregate"

  - id: monotonic-002-max-ge-min
    name: ifault_ka_max must be ≥ ifault_ka_min at every node (c=1.05 ≥ c=0.95)
    severity: critical
    jsonpath: "$.cascade[*]"
    assert: "ifault_ka_max >= ifault_ka_min"
    message: "Node {node_id}: ifault_max ({ifault_ka_max}) < ifault_min ({ifault_ka_min}) — c-factor application inverted"
    standard_ref: "IEC 60909-0:2016 §3.7"

  - id: monotonic-003-c-factor-ratio
    name: ifault_ka_max / ifault_ka_min ≈ 1.10 (c_max/c_min ratio)
    severity: warning
    jsonpath: "$.cascade[*]"
    when: "ifault_ka_min > 0"
    assert: "abs(ifault_ka_max / ifault_ka_min - 1.105) < 0.05"
    message: "Node {node_id}: max/min ratio {ratio} differs from expected 1.105 (= 1.05/0.95)"
    standard_ref: "IEC 60909-0:2016 §3.7"
```

- [ ] **Step 3: Write tool-call-resolved.yaml**

```yaml
version: 1.0.0
applies_to_drawing_types: ["fault_level_study"]
checks:
  - id: tool-001-pending-flag-emitted
    name: If any cascade node is tool_call_pending, top-level flags must include TOOL-CALL-PENDING
    severity: high
    jsonpath: "$"
    when: "any(n.tool_call_pending == true for n in cascade)"
    assert: "'TOOL-CALL-PENDING' in flags"
    message: "tool_call_pending node exists but TOOL-CALL-PENDING flag not emitted"
    standard_ref: "WI3 tool-call deferral convention"

  - id: tool-002-completeness
    name: Every cascade node has Ifault values (computed OR engineer-fallback)
    severity: critical
    jsonpath: "$.cascade[*]"
    assert: "ifault_ka_max is not null"
    message: "Node {node_id}: ifault_ka_max is null (no computed value, no fallback)"
    standard_ref: "design completeness"
```

- [ ] **Step 4: Write intent-shape.yaml**

```yaml
version: 1.0.0
applies_to_drawing_types: ["fault_level_study"]
# Asserts the emitted fault-level intent satisfies db-layout's expected shape.

checks:
  - id: intent-001-required-fields
    name: Intent has project_id + source_summary + fault_currents
    severity: critical
    target: "fault_level_intent_payload"
    assert: "'project_id' in payload AND 'source_summary' in payload AND 'fault_currents' in payload"
    message: "Intent missing required top-level keys"
    standard_ref: "fault-level-intent.schema.json"

  - id: intent-002-fault-currents-per-node
    name: fault_currents[*] has node_id + ifault_ka_max minimum
    severity: critical
    target: "fault_level_intent.fault_currents[*]"
    assert: "'node_id' in fc AND 'ifault_ka_max' in fc AND 'node_kind' in fc"
    message: "fault_currents entry missing required fields"
    standard_ref: "fault-level-intent.schema.json"

  - id: intent-003-db-layout-compatibility
    name: Intent fault_currents shape matches what db-layout v1.0 expects to consume
    severity: critical
    target: "fault_level_intent"
    assert: "for each fault_currents entry: node_kind in valid_node_kinds AND ifault_ka_max is number"
    message: "Intent shape incompatible with db-layout expectations"
    standard_ref: "verified against electrical/db-layout/evals/eval-04-missing-fault-current.yaml expectations"
```

- [ ] **Step 5: Validate + commit**

```bash
python3 -c "
import yaml
total = 0
for f in ['cascade-tree-integrity', 'ifault-monotonicity', 'tool-call-resolved', 'intent-shape']:
    d = yaml.safe_load(open(f'electrical/fault-level/validation/{f}.yaml'))
    n = len(d['checks'])
    total += n
    print(f'{f}: {n} checks')
print(f'TOTAL: {total} checks')
"
git add electrical/fault-level/validation/
git commit -m "feat: fault-level validation — 12 deterministic checks (tree/monotonic/tool-call/intent)"
```

---

## Task 20: Create 2 ontology JSONs

**Files:**
- Create: `electrical/fault-level/ontology/source-types.json`
- Create: `electrical/fault-level/ontology/cascade-node-kinds.json`

- [ ] **Step 1: Write source-types.json**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "ontology_type": "fault_level_source_types",
  "version": "1.0.0",
  "source": "IEC 60909-0:2016 §4",
  "source_types": [
    {
      "id": "utility_transformer",
      "name": "Utility / DNO Transformer",
      "iec_reference": "IEC 60909-0:2016 §4.2 + §4.3",
      "contribution_method": "constant",
      "near_or_far_classification": "far",
      "typical_zpu_pct": [4, 7],
      "typical_xover_r": [5, 10],
      "notes": "Standard utility-side source. Constant EMF, no decrement. Building services projects typically use this."
    },
    {
      "id": "generator",
      "name": "Synchronous Generator (Standby / Cogen)",
      "iec_reference": "IEC 60909-0:2016 §4.4 + §3.5",
      "contribution_method": "subtransient_decrement",
      "near_or_far_classification": "near",
      "typical_xd_doubleprime_pu": [0.12, 0.20],
      "decrement_profile": "X\"d → X'd → Xd over t",
      "notes": "Standby gen or cogen unit. Subtransient X\"d first cycle. Decrement factor μ at breaking time."
    },
    {
      "id": "ups",
      "name": "UPS / Battery Inverter",
      "iec_reference": "Not directly in IEC 60909-0; IEC 62040-3 + manufacturer data",
      "contribution_method": "current_limited",
      "first_half_cycle_limit_x_rated": [2, 3],
      "bypass_switchover_ms": [3, 5],
      "notes": "Output current limited by IGBT/IGCT. Transitions to bypass during sustained fault."
    },
    {
      "id": "motor_aggregate",
      "name": "Induction Motor Aggregate Back-Feed",
      "iec_reference": "IEC 60909-0:2016 §4.5",
      "contribution_method": "locked_rotor",
      "inclusion_threshold_pct_of_sk": 1.0,
      "typical_ilr_avg": 5.0,
      "decay_to_zero_cycles": 2,
      "notes": "Running motors contribute via subtransient reactance for 1-2 cycles. 2016 amendment lowered threshold from 5% to 1%."
    }
  ]
}
```

- [ ] **Step 2: Write cascade-node-kinds.json**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "ontology_type": "fault_level_cascade_node_kinds",
  "version": "1.0.0",
  "source": "Internal ontology aligned with IEC 60909-0 + IEC 60364-4-43",
  "node_kinds": [
    {
      "id": "hv_source",
      "name": "HV Primary Supply",
      "level": "≥ 1 kV",
      "description": "DNO supply at HV primary substation. Source of Ik\"_HV. Cascade root for HV-side projects.",
      "downstream_typical": "transformer_secondary"
    },
    {
      "id": "transformer_secondary",
      "name": "Transformer LV Secondary",
      "level": "≤ 1 kV (typically 400V or 480V TPN)",
      "description": "LV side of incoming or distribution transformer. Source of Ik\"_LV. Cascade root for LV-only projects.",
      "downstream_typical": "board_incoming"
    },
    {
      "id": "board_incoming",
      "name": "Board Incoming Terminals",
      "description": "Terminals of distribution board's main switch. Ik\" check for main switch breaker rating.",
      "downstream_typical": "board_busbar"
    },
    {
      "id": "board_busbar",
      "name": "Board Busbar",
      "description": "DB busbar after main switch but before way breakers. Ipk check for busbar mechanical withstand.",
      "downstream_typical": "board_outgoing_feeder"
    },
    {
      "id": "board_outgoing_feeder",
      "name": "Outgoing Feeder Breaker Output",
      "description": "Downstream of way breaker, upstream of cable feeder. Each outgoing feeder is one node.",
      "downstream_typical": "another board_incoming OR final_circuit_endpoint"
    },
    {
      "id": "final_circuit_endpoint",
      "name": "Final Circuit End",
      "description": "End of branch circuit at load equipment. Lowest Ifault in cascade. ADS check uses Ik\"_min here.",
      "downstream_typical": "none (leaf)"
    }
  ]
}
```

- [ ] **Step 3: Validate + commit**

```bash
python3 -c "
import json
for f, key in [('source-types', 'source_types'), ('cascade-node-kinds', 'node_kinds')]:
    d = json.load(open(f'electrical/fault-level/ontology/{f}.json'))
    print(f'{f}.json: {len(d[key])} entries')
"
git add electrical/fault-level/ontology/
git commit -m "feat: fault-level ontology — source-types (4) + cascade-node-kinds (6)"
```

---

## Task 21: Create 2 docs files

**Files:**
- Create: `electrical/fault-level/docs/engineering-philosophy.md`
- Create: `electrical/fault-level/docs/known-limitations.md`

- [ ] **Step 1: Write engineering-philosophy.md**

```markdown
# Fault-Level Skill — Engineering Philosophy

## Why this skill exists

Prospective short-circuit current (Ik") is the foundation of switchgear sizing, cable adiabatic protection, and selectivity coordination. Get Ik" wrong and breakers will explode on fault, cables will burn through, and selectivity coordination becomes meaningless. This skill enforces the IEC 60909-0:2016 reasoning chain explicitly.

## What "good fault-level analysis" looks like

A correct fault-level study answers seven questions in order:

1. **What sources?** Utility / generator / UPS / motors — each contributes differently
2. **What's the cascade topology?** Tree of impedances from each source to each fault
3. **What voltage factor c?** 1.05 for Ik"max (breaker rating); 0.95 for Ik"min (protection)
4. **Near or far from generator?** Apply subtransient decrement for NG; constant for FG
5. **What κ at each node?** Peak factor from R/X — drives busbar Ipk withstand
6. **What's Ik" at every protective device?** Compare against device Icn
7. **Does selectivity hold?** Each upstream-downstream pair adequately rated

Question 6 is the gate. A study that passes 1-5 but the 100A MCCB has Icn 10kA at a node where Ik" = 25kA is **unsafe**.

## The standards-consumption pattern

This skill loads jurisdiction-specific files. The generator prompt names 21 specific JSON/md files; runtime loads ~12-15 for any given project.

- All jurisdictions → IEC 60909 family (8 files) + IEC 60617 symbols (2 files)
- GB → BS 7671 fault-current + cable-ratings (3 files)
- EU/INT → IEC 60364 fault-current + cable-ratings (4 files)
- US → NEC Chapter 1, 240, Chapter 9 Table 9 (4 files)

## Two emitted artefacts: IR + intent

`fault-level-ir.schema.json` — full audit trail (every cascade node + selectivity implication + rationale)

`fault-level-intent.schema.json` — slim downstream subset (just the Ifault numbers per node). Consumed by:
- `db-layout` v1.0.0+ — resolves selectivity `tool_call_pending` entries
- `earthing` v1.1+ (future) — cross-validates Ze + R1 + R2 against board Ifault
- `cable-sizing` (Tier 1 Item 3) — adiabatic check at every cable
- `generator-sizing` (future) — Iek for generator dimensioning

## Why we defer the math

IEC 60909-0 calculation involves:
- Complex-number arithmetic (R + jX) at every node
- Iterative cascade impedance addition
- Multi-source superposition (utility + gen + UPS + motors)
- Peak factor κ from X/R (transcendental function)
- Near-generator decrement factor μ (tabulated curves)

LLM inline math diverges from validated Python by >30% in representative cases. This skill **NEVER** inline-computes. It assembles inputs, dispatches `calc.iec60909_cascade` (per WI3 + the calc contract shipped Item 1), interprets results, and emits the rationale.

## What this skill will NOT do

- It will not invent fault currents. If `calc.iec60909_cascade` hasn't run AND no engineer-input fallback is given, emit `tool_call_pending: true` per WI3.
- It will not invent source impedances. If no Zpu nameplate is given, use IEC 60909-2 typical default + a flag in compliance_summary.
- It will not paraphrase IEC 60909-0 clauses. Cite verbatim ("IEC 60909-0:2016 §3.7 Table 1").
- It will not do arc-flash (separate skill scope per NFPA 70E / IEEE 1584).
- It will not do time-graded protection coordination (separate skill scope per IEC 60255).
```

- [ ] **Step 2: Write known-limitations.md**

```markdown
# Fault-Level Skill — Known Limitations (v1.0.0)

## v1.0.0 scope

- **Output:** project-scoped fault-level IR (one IR per project, not per board)
- **Intent emitted:** fault-level intent (downstream-facing subset)
- **Systems supported:** AC fault analysis per IEC 60909-0:2016 (LV + HV)
- **Jurisdictions:** GB, EU, INT, US
- **Calculation:** deferred to `calc.iec60909_cascade` runtime tool (per WI3)

## What is OUT of scope

### DC fault analysis
PV strings, battery storage, EV DCFC fault current — separate skill `dc-fault-level` (post-v1.0).

### Arc-flash incident energy
IEEE 1584 / NFPA 70E arc-flash hazard calculation — separate skill `arc-flash` (post-v1.0).

### Time-graded protection coordination
IDMT relays, definite-time, distance protection — separate skill `protection-coordination` (post-Tier 1).

### Lightning-induced transients
BS EN 62305 / NFPA 780 surge analysis — separate scope.

### HV transformer differential protection
Outside building services scope.

### Sub-cycle dynamics
DC offset envelope, asymmetry decay below 1 cycle — requires EMT (electromagnetic transient) simulation, beyond IEC 60909 scope.

## What may produce false positives in evals

- **D2 (Cascade topology accuracy):** Engineer-declared cascade trees can have legitimate non-standard structures (loop systems, transfer schemes, parallel feeders). Reviewer should accept these when documented.
- **D5 (Peak factor κ):** Tool-computed κ might differ slightly from inline approximation due to floating-point precision; 2% tolerance applied.
- **INV-4 (Monotonicity):** Motor back-feed nodes legitimately add to downstream Ifault — flagged as expected, not as error.

## Tool calls awaiting runtime

| Tool name | Purpose | Status |
|---|---|---|
| `calc.iec60909_cascade` | Compute Ik\"max + Ik\"min + ipk + X/R at every cascade node | tool_call_pending (until DraftsMan runtime project ships) |

When the runtime tool exists, IRs currently with `cascade[*].tool_call_pending: true` will be re-emitted with computed values.
```

- [ ] **Step 3: Validate + commit**

```bash
test -s electrical/fault-level/docs/engineering-philosophy.md && \
test -s electrical/fault-level/docs/known-limitations.md && \
echo OK
git add electrical/fault-level/docs/
git commit -m "docs: fault-level engineering-philosophy + known-limitations"
```

---

## Task 22: Create `runner-config.json` + `eval-01-uk-domestic-cu-cascade.yaml`

**Files:**
- Create: `electrical/fault-level/evals/runner-config.json`
- Create: `electrical/fault-level/evals/eval-01-uk-domestic-cu-cascade.yaml`

- [ ] **Step 1: Write runner-config.json**

```json
{
  "$schema": "../../../shared/schemas/core/eval-runner-config.schema.json",
  "skill": "fault-level",
  "version": "1.0.0",
  "minimum_model_class": "sonnet",
  "minimum_status": {
    "happy_path": "pass",
    "edge_case": "pass-with-warnings",
    "validation_trap": "pass",
    "missing_input": "pass",
    "jurisdiction_switch": "pass",
    "rationale_block": "pass",
    "skill_specific": "pass-with-warnings"
  },
  "evals": [
    "eval-01-uk-domestic-cu-cascade.yaml",
    "eval-02-tpn-commercial-with-gen.yaml",
    "eval-03-undersized-breaker-trap.yaml",
    "eval-04-missing-source-data.yaml",
    "eval-05-jurisdiction-us-with-hv.yaml",
    "eval-06-rationale-block.yaml",
    "eval-07-multi-source-coordination.yaml",
    "eval-08-induction-motor-contribution.yaml",
    "eval-09-intent-shape.yaml"
  ],
  "scoring": {
    "schema_validity_weight": 0.20,
    "invariant_pass_weight": 0.30,
    "cascade_accuracy_weight": 0.20,
    "reviewer_score_weight": 0.20,
    "rationale_quality_weight": 0.10
  }
}
```

- [ ] **Step 2: Write eval-01**

```yaml
id: eval-01-uk-domestic-cu-cascade
category: happy_path
severity: critical
description: |
  UK 3-bed semi: 230V single-phase service from 500 kVA DNO transformer. Engineer declares PSCC = 1.5 kA at service head.
  100A service → CU → 6 final circuits. Single utility source. Cascade Ifault decreases as you walk downstream.

inputs:
  jurisdiction: "GB"
  project_id: "uk-dom-fl-eg01"
  supply_voltage_v: "230"
  hv_side_present: false
  primary_transformer_kva: 500
  primary_transformer_zpu_pct: 4.0
  primary_transformer_xover_r: 5
  standby_generator_present: false
  ups_present: false
  motor_load_kw: 0
  cascade_topology_source: "engineer_declared"
  cascade_engineer_declared:
    - { node_id: "TX-1", parent_node_id: null, node_kind: "transformer_secondary", designation: "DNO supply terminals" }
    - { node_id: "CU-G", parent_node_id: "TX-1", node_kind: "board_incoming", designation: "Main consumer unit", feeder: { length_m: 5, csa_mm2_or_awg: "25mm²", material: "copper", insulation: "pvc_70" } }
    - { node_id: "CU-G.BUSBAR", parent_node_id: "CU-G", node_kind: "board_busbar", designation: "CU busbar" }
    - { node_id: "CU-G.C01", parent_node_id: "CU-G.BUSBAR", node_kind: "final_circuit_endpoint", designation: "Lighting GF", feeder: { length_m: 18, csa_mm2_or_awg: "1.5mm²", material: "copper", insulation: "pvc_70" } }

assertions:
  - kind: schema_valid
    schema: "fault-level-ir.schema.json"
  - kind: jsonpath_equals
    path: "$.jurisdiction"
    expected: "GB"
  - kind: jsonpath_present
    path: "$.cascade[?(@.node_id=='TX-1')].ifault_ka_max"
  - kind: jsonpath_lte
    path: "$.cascade[?(@.node_id=='CU-G.C01')].ifault_ka_max"
    field_compared_to: "$.cascade[?(@.node_id=='CU-G')].ifault_ka_max"
    note: "Monotonicity — final circuit Ifault < CU incoming Ifault"
  - kind: invariant_passes
    invariant: "INV-4"
    note: "Monotonicity downstream"
  - kind: clause_cited
    clause_pattern: "^IEC 60909-0:2016"
    minimum_count: 2

expected_status: "pass"
```

- [ ] **Step 3: Validate + commit**

```bash
python3 -c "
import json, yaml
rc = json.load(open('electrical/fault-level/evals/runner-config.json'))
e1 = yaml.safe_load(open('electrical/fault-level/evals/eval-01-uk-domestic-cu-cascade.yaml'))
assert len(rc['evals']) == 9
assert e1['category'] == 'happy_path'
print(f'runner-config + eval-01: OK ({len(e1[\"assertions\"])} assertions)')
"
git add electrical/fault-level/evals/runner-config.json electrical/fault-level/evals/eval-01-uk-domestic-cu-cascade.yaml
git commit -m "feat: fault-level eval-01 UK happy-path + runner-config"
```

---

## Task 23: `eval-02-tpn-commercial-with-gen.yaml`

**Files:**
- Create: `electrical/fault-level/evals/eval-02-tpn-commercial-with-gen.yaml`

- [ ] **Step 1: Write the eval**

```yaml
id: eval-02-tpn-commercial-with-gen
category: edge_case
severity: critical
description: |
  400V TPN commercial: 1600 kVA DNO TX + 800 kVA standby generator on ATS scheme.
  Two-source modelling. Near-from-generator method applies in gen-mode (X"d subtransient + decrement).
  Far-from-generator method applies in utility-mode.

inputs:
  jurisdiction: "GB"
  project_id: "intl-com-fl-eg02"
  supply_voltage_v: "400"
  hv_side_present: true
  hv_voltage_kv: "11"
  hv_pscc_at_primary_ka: 16
  primary_transformer_kva: 1600
  primary_transformer_zpu_pct: 5.0
  primary_transformer_xover_r: 7
  standby_generator_present: true
  standby_generator_kva: 800
  motor_load_kw: 0
  cascade_topology_source: "engineer_declared"
  cascade_engineer_declared:
    - { node_id: "HV-1", parent_node_id: null, node_kind: "hv_source", designation: "11 kV primary" }
    - { node_id: "TX-1", parent_node_id: "HV-1", node_kind: "transformer_secondary", designation: "1600 kVA TX LV terminals" }
    - { node_id: "MSB-1", parent_node_id: "TX-1", node_kind: "board_incoming", designation: "Main MSB", feeder: { length_m: 15, csa_mm2_or_awg: "240mm²", material: "copper", insulation: "xlpe_90" } }

assertions:
  - kind: schema_valid
    schema: "fault-level-ir.schema.json"
  - kind: jsonpath_present
    path: "$.project_supply.hv_side"
  - kind: jsonpath_count_gte
    path: "$.sources[*]"
    minimum: 2
    note: "utility + generator both modelled"
  - kind: jsonpath_in
    path: "$.sources[*].kind"
    allowed: ["utility", "generator", "ups", "motor_aggregate"]
  - kind: clause_cited
    clause_pattern: "IEC 60909-0:2016 §3.5"
    minimum_count: 1
    note: "Near-from-generator method cited"

expected_status: "pass"
```

- [ ] **Step 2: Commit**

```bash
git add electrical/fault-level/evals/eval-02-tpn-commercial-with-gen.yaml
git commit -m "feat: fault-level eval-02 edge-case TPN commercial with standby genset"
```

---

## Task 24: `eval-03-undersized-breaker-trap.yaml`

**Files:**
- Create: `electrical/fault-level/evals/eval-03-undersized-breaker-trap.yaml`

- [ ] **Step 1: Write**

```yaml
id: eval-03-undersized-breaker-trap
category: validation_trap
severity: critical
description: |
  Cascade Ifault = 12 kA at MSB-1 outgoing. Engineer-declared MCB at that node has Icn = 6 kA.
  Generator MUST emit a CRITICAL flag, NOT silently pass selectivity_implications[*].adequate = true.

inputs:
  jurisdiction: "GB"
  project_id: "trap-fl-eg03"
  supply_voltage_v: "400"
  hv_side_present: false
  primary_transformer_kva: 1000
  primary_transformer_zpu_pct: 4.0
  standby_generator_present: false
  ups_present: false
  motor_load_kw: 0
  cascade_topology_source: "engineer_declared"
  cascade_engineer_declared:
    - { node_id: "TX-1", parent_node_id: null, node_kind: "transformer_secondary" }
    - { node_id: "MSB-1.F01", parent_node_id: "TX-1", node_kind: "board_outgoing_feeder", designation: "Feeder with under-rated MCB" }
  declared_devices:
    - { breaker_id: "F01-MCB", breaker_rating_a: 32, breaker_icn_ka: 6, at_node: "MSB-1.F01" }
  # Expectation: cascade computes ~12 kA at MSB-1.F01

assertions:
  - kind: schema_valid
    schema: "fault-level-ir.schema.json"
  - kind: jsonpath_equals
    path: "$.selectivity_implications[?(@.breaker_id=='F01-MCB')].adequate"
    expected: false
    note_if_violated: "Generator silently accepted the trap"
  - kind: jsonpath_contains
    path: "$.flags"
    must_contain: "BREAKER_UNDERRATED_FOR_FAULT_LEVEL"
  - kind: jsonpath_equals
    path: "$.compliance_summary.compliant"
    expected: false
  - kind: invariant_passes
    invariant: "INV-6"
    note: "Breaker adequacy check"

expected_status: "pass"
```

- [ ] **Step 2: Commit**

```bash
git add electrical/fault-level/evals/eval-03-undersized-breaker-trap.yaml
git commit -m "feat: fault-level eval-03 undersized-breaker validation trap"
```

---

## Task 25: `eval-04-missing-source-data.yaml`

**Files:**
- Create: `electrical/fault-level/evals/eval-04-missing-source-data.yaml`

- [ ] **Step 1: Write**

```yaml
id: eval-04-missing-source-data
category: missing_input
severity: high
description: |
  No transformer Zpu, no DNO PSCC, no engineer-declared Ifault.
  Skill must emit tool_call_pending: true on every cascade node + TOOL-CALL-PENDING flag, NOT invent values.

inputs:
  jurisdiction: "EU"
  project_id: "missing-data-fl-eg04"
  supply_voltage_v: "400"
  hv_side_present: false
  primary_transformer_kva: 630
  # NO primary_transformer_zpu_pct
  # NO hv_pscc_at_primary_ka
  standby_generator_present: false
  ups_present: false
  motor_load_kw: 0
  cascade_topology_source: "engineer_declared"
  cascade_engineer_declared:
    - { node_id: "TX-1", parent_node_id: null, node_kind: "transformer_secondary" }
    - { node_id: "DB-EU1", parent_node_id: "TX-1", node_kind: "board_incoming" }

assertions:
  - kind: schema_valid
    schema: "fault-level-ir.schema.json"
  - kind: jsonpath_all_equals
    path: "$.cascade[*].tool_call_pending"
    expected: true
    note: "All nodes deferred until calc.iec60909_cascade tool runs OR engineer provides Zpu"
  - kind: jsonpath_contains
    path: "$.flags"
    must_contain: "TOOL-CALL-PENDING"
  - kind: jsonpath_count_gte
    path: "$.compliance_summary.non_compliance_flags[*]"
    minimum: 1
    note: "At least one flag for missing source data"
  - kind: invariant_passes
    invariant: "INV-7"

expected_status: "pass"
```

- [ ] **Step 2: Commit**

```bash
git add electrical/fault-level/evals/eval-04-missing-source-data.yaml
git commit -m "feat: fault-level eval-04 missing-source-data (must defer, not invent)"
```

---

## Task 26: `eval-05-jurisdiction-us-with-hv.yaml`

**Files:**
- Create: `electrical/fault-level/evals/eval-05-jurisdiction-us-with-hv.yaml`

- [ ] **Step 1: Write**

```yaml
id: eval-05-jurisdiction-us-with-hv
category: jurisdiction_switch
severity: critical
description: |
  US industrial: 12.47 kV primary → 480V TPN service, 2500 kVA TX. NEC 110.9 + 240.86 cited alongside IEC 60909.
  No BS 7671 / IEC 60364 citations. Use NEC Chapter 9 Table 9 for cable impedance.

inputs:
  jurisdiction: "US"
  project_id: "us-ind-fl-eg05"
  supply_voltage_v: "480"
  hv_side_present: true
  hv_voltage_kv: "12.47"
  hv_pscc_at_primary_ka: 25
  primary_transformer_kva: 2500
  primary_transformer_zpu_pct: 6.0
  standby_generator_present: false
  ups_present: false
  motor_load_kw: 0
  cascade_topology_source: "engineer_declared"
  cascade_engineer_declared:
    - { node_id: "HV-1", parent_node_id: null, node_kind: "hv_source", designation: "12.47 kV primary" }
    - { node_id: "TX-1", parent_node_id: "HV-1", node_kind: "transformer_secondary", designation: "2500 kVA TX 480V LV" }
    - { node_id: "MSB-1", parent_node_id: "TX-1", node_kind: "board_incoming", designation: "Main switchboard", feeder: { length_m: 20, csa_mm2_or_awg: "350 kcmil", material: "copper", insulation: "thwn_75" } }

assertions:
  - kind: schema_valid
    schema: "fault-level-ir.schema.json"
  - kind: jsonpath_equals
    path: "$.jurisdiction"
    expected: "US"
  - kind: jsonpath_present
    path: "$.project_supply.hv_side"
  - kind: clause_cited
    clause_pattern: "^NEC 2023 Art (110|240)"
    minimum_count: 1
  - kind: clause_cited
    clause_pattern: "^IEC 60909-0:2016"
    minimum_count: 2
  - kind: clause_not_cited
    clause_pattern: "^BS 7671"
    note: "US project must not cite UK regs"
  - kind: clause_not_cited
    clause_pattern: "^IEC 60364"
    note: "US project must not cite IEC 60364"

expected_status: "pass"
```

- [ ] **Step 2: Commit**

```bash
git add electrical/fault-level/evals/eval-05-jurisdiction-us-with-hv.yaml
git commit -m "feat: fault-level eval-05 jurisdiction-switch US with HV primary"
```

---

## Task 27: `eval-06-rationale-block.yaml`

**Files:**
- Create: `electrical/fault-level/evals/eval-06-rationale-block.yaml`

- [ ] **Step 1: Write**

```yaml
id: eval-06-rationale-block
category: rationale_block
severity: high
description: |
  Reuses eval-01 happy-path scenario. Per WI2 the rationale block is mandatory: 8 sections + chat_summary + decisions with IEC 60909 citations.

inputs:
  reuse_eval: "eval-01-uk-domestic-cu-cascade"

assertions:
  - kind: schema_valid
    schema: "fault-level-ir.schema.json"
  - kind: jsonpath_present
    path: "$.rationale.chat_summary"
  - kind: jsonpath_length_gte
    path: "$.rationale.chat_summary"
    minimum: 40
    maximum: 500
  - kind: jsonpath_count_gte
    path: "$.rationale.sections[*]"
    minimum: 8
    note: "8 sections per Step 14 of generator"
  - kind: jsonpath_all_present
    path: "$.rationale.sections[*].title"
  - kind: jsonpath_all_present
    path: "$.rationale.sections[*].summary"
  - kind: jsonpath_pattern_match
    path: "$.rationale.sections[*].decisions[*].code_clause"
    pattern: "^(IEC 60909-0:2016|BS 7671:2018\\+A3|IEC 60364-[0-9]+-[0-9]+|NEC 2023)"

expected_status: "pass"
```

- [ ] **Step 2: Commit**

```bash
git add electrical/fault-level/evals/eval-06-rationale-block.yaml
git commit -m "feat: fault-level eval-06 rationale block (8 sections per WI2)"
```

---

## Task 28: `eval-07-multi-source-coordination.yaml`

**Files:**
- Create: `electrical/fault-level/evals/eval-07-multi-source-coordination.yaml`

- [ ] **Step 1: Write**

```yaml
id: eval-07-multi-source-coordination
category: skill_specific
severity: high
description: |
  Data centre topology: utility (1600 kVA) + standby gen (800 kVA) + UPS (500 kVA) all active simultaneously.
  Multi-source superposition per IEC 60909-0 §3.6. Sources[] must contain ≥3 entries.

inputs:
  jurisdiction: "INT"
  project_id: "dc-multi-fl-eg07"
  supply_voltage_v: "400"
  hv_side_present: false
  primary_transformer_kva: 1600
  primary_transformer_zpu_pct: 5.0
  standby_generator_present: true
  standby_generator_kva: 800
  ups_present: true
  ups_kva: 500
  motor_load_kw: 0
  cascade_topology_source: "engineer_declared"
  cascade_engineer_declared:
    - { node_id: "TX-1", parent_node_id: null, node_kind: "transformer_secondary" }
    - { node_id: "MSB-1", parent_node_id: "TX-1", node_kind: "board_incoming", feeder: { length_m: 20, csa_mm2_or_awg: "240mm²", material: "copper", insulation: "xlpe_90" } }

assertions:
  - kind: schema_valid
    schema: "fault-level-ir.schema.json"
  - kind: jsonpath_count_gte
    path: "$.sources[*]"
    minimum: 3
    note: "utility + generator + UPS"
  - kind: jsonpath_in
    path: "$.sources[*].kind"
    allowed: ["utility", "generator", "ups", "motor_aggregate"]
  - kind: clause_cited
    clause_pattern: "IEC 60909-0:2016 §3.6"
    minimum_count: 1
    note: "Multi-source superposition cited"

expected_status: "pass"
```

- [ ] **Step 2: Commit**

```bash
git add electrical/fault-level/evals/eval-07-multi-source-coordination.yaml
git commit -m "feat: fault-level eval-07 multi-source coordination (skill_specific)"
```

---

## Task 29: `eval-08-induction-motor-contribution.yaml`

**Files:**
- Create: `electrical/fault-level/evals/eval-08-induction-motor-contribution.yaml`

- [ ] **Step 1: Write**

```yaml
id: eval-08-induction-motor-contribution
category: skill_specific
severity: high
description: |
  Industrial site: 2500 kVA TX + 500 kW connected motor load (running). Motor contribution > 1% threshold per IEC 60909-0 §4.5.1.2.
  Must include motor_aggregate source in sources[] with ILR-based Ik" contribution.

inputs:
  jurisdiction: "INT"
  project_id: "ind-motor-fl-eg08"
  supply_voltage_v: "400"
  hv_side_present: false
  primary_transformer_kva: 2500
  primary_transformer_zpu_pct: 6.0
  standby_generator_present: false
  ups_present: false
  motor_load_kw: 500
  cascade_topology_source: "engineer_declared"
  cascade_engineer_declared:
    - { node_id: "TX-1", parent_node_id: null, node_kind: "transformer_secondary" }
    - { node_id: "MCC-1", parent_node_id: "TX-1", node_kind: "board_incoming", designation: "Motor control center" }

assertions:
  - kind: schema_valid
    schema: "fault-level-ir.schema.json"
  - kind: jsonpath_contains
    path: "$.sources[*].kind"
    must_contain: "motor_aggregate"
  - kind: clause_cited
    clause_pattern: "IEC 60909-0:2016 §4.5"
    minimum_count: 1
  - kind: jsonpath_present
    path: "$.compliance_summary.assumptions[*]"
    note: "Engineer-input motor ILR assumption captured"

expected_status: "pass"
```

- [ ] **Step 2: Commit**

```bash
git add electrical/fault-level/evals/eval-08-induction-motor-contribution.yaml
git commit -m "feat: fault-level eval-08 induction motor contribution (skill_specific)"
```

---

## Task 30: `eval-09-intent-shape.yaml`

**Files:**
- Create: `electrical/fault-level/evals/eval-09-intent-shape.yaml`

- [ ] **Step 1: Write**

```yaml
id: eval-09-intent-shape
category: skill_specific
severity: critical
description: |
  Reuses eval-01 inputs. Verifies the emitted fault-level intent payload satisfies db-layout v1.0's expected
  consumption shape — drift here breaks db-layout.

inputs:
  reuse_eval: "eval-01-uk-domestic-cu-cascade"

assertions:
  - kind: emitted_intent_validates
    intent_type: "fault-level"
    schema: "fault-level-intent.schema.json"
  - kind: emitted_intent_field_present
    intent_type: "fault-level"
    path: "$.project_id"
  - kind: emitted_intent_field_present
    intent_type: "fault-level"
    path: "$.source_summary"
  - kind: emitted_intent_field_present
    intent_type: "fault-level"
    path: "$.fault_currents[*].node_id"
  - kind: emitted_intent_field_present
    intent_type: "fault-level"
    path: "$.fault_currents[*].ifault_ka_max"
  - kind: emitted_intent_field_present
    intent_type: "fault-level"
    path: "$.fault_currents[*].node_kind"
  - kind: cross_skill_compatibility_check
    consumer_skill: "electrical/db-layout"
    consumer_field_path: "$.selectivity_results[*]"
    note: "db-layout selectivity_results entries get resolved from fault-level intent fault_currents[]"

expected_status: "pass"
```

- [ ] **Step 2: Verify all 9 evals registered + commit**

```bash
python3 -c "
import json, os
rc = json.load(open('electrical/fault-level/evals/runner-config.json'))
listed = set(rc['evals'])
on_disk = set(f for f in os.listdir('electrical/fault-level/evals/') if f.startswith('eval-'))
assert listed == on_disk, f'mismatch: missing={listed-on_disk}, extra={on_disk-listed}'
print(f'All {len(listed)} evals registered')
"
git add electrical/fault-level/evals/eval-09-intent-shape.yaml
git commit -m "feat: fault-level eval-09 intent-shape cross-skill contract verification"
```

---

## Task 31: Example 1 — UK domestic single-source

**Files:**
- Create: `electrical/fault-level/examples/uk-domestic-single-source/input.json`
- Create: `electrical/fault-level/examples/uk-domestic-single-source/reasoning.md`
- Create: `electrical/fault-level/examples/uk-domestic-single-source/output.json`

UK 3-bed semi, 230V single-phase, 500 kVA DNO TX → 1.5 kA PSCC. Single utility source.

- [ ] **Step 1: Write `input.json`** (reuse eval-01 inputs + project_meta)

```json
{
  "$schema": "../../inputs.json",
  "project_meta": {
    "project_id": "uk-dom-fl-eg01",
    "name": "23 Elm Crescent — 3-bed Semi",
    "client": "Private",
    "designer": "DraftsMan Skills demo",
    "date": "2026-05-16",
    "revision": "P01"
  },
  "jurisdiction": "GB",
  "supply_voltage_v": "230",
  "hv_side_present": false,
  "primary_transformer_kva": 500,
  "primary_transformer_zpu_pct": 4.0,
  "primary_transformer_xover_r": 5,
  "standby_generator_present": false,
  "ups_present": false,
  "motor_load_kw": 0,
  "cascade_topology_source": "engineer_declared",
  "cascade_engineer_declared": [
    { "node_id": "TX-1", "parent_node_id": null, "node_kind": "transformer_secondary", "designation": "500 kVA DNO TX 230V LV terminals" },
    { "node_id": "CU-G", "parent_node_id": "TX-1", "node_kind": "board_incoming", "designation": "Main consumer unit", "feeder": { "length_m": 5, "csa_mm2_or_awg": "25mm²", "material": "copper", "insulation": "pvc_70" } },
    { "node_id": "CU-G.BUSBAR", "parent_node_id": "CU-G", "node_kind": "board_busbar", "designation": "CU busbar 100A" },
    { "node_id": "CU-G.C01", "parent_node_id": "CU-G.BUSBAR", "node_kind": "final_circuit_endpoint", "designation": "GF lighting", "feeder": { "length_m": 18, "csa_mm2_or_awg": "1.5mm²", "material": "copper", "insulation": "pvc_70" } },
    { "node_id": "CU-G.C03", "parent_node_id": "CU-G.BUSBAR", "node_kind": "final_circuit_endpoint", "designation": "GF sockets ring", "feeder": { "length_m": 38, "csa_mm2_or_awg": "2.5mm²", "material": "copper", "insulation": "pvc_70" } }
  ]
}
```

- [ ] **Step 2: Write `reasoning.md`**

```markdown
# Reasoning — UK Domestic Single-Source Cascade

## Step 1 — Discovery
No `cross_drawing_context` (no db-layout intent). Engineer-declared cascade (5 nodes).

## Step 2 — Standards loaded (GB)
IEC 60909 always-on (8 files) + IEC 60617 (2 files) + BS 7671 reg434 + pscc-determination + appendix4-cable-ratings.

## Step 3 — Cascade topology
5 nodes: TX → CU-G (incoming) → CU-G.BUSBAR → 2 final circuits (C01 lighting, C03 sockets ring).

## Step 4 — HV-side
N/A — no HV present.

## Step 5 — Transformer impedance
500 kVA, Zpu = 4%, X/R = 5 → Z_TX = 0.04 × 230² / 500000 × 1000 = 4.23 mΩ at LV. R_TX ≈ 0.83 mΩ, X_TX ≈ 4.15 mΩ.

## Step 6 — Generator: N/A
## Step 7 — UPS: N/A
## Step 8 — Motor: N/A (0 kW)

## Step 9 — Cable impedance (BS 7671 App 4)
- CU incoming feeder: 25mm² Cu, 5m → R ≈ 4 mΩ, X ≈ 0.5 mΩ
- C01 lighting: 1.5mm² Cu, 18m → R ≈ 220 mΩ, X ≈ 4 mΩ
- C03 ring: 2.5mm² Cu, 38m → R ≈ 281 mΩ, X ≈ 9 mΩ (ring formula simplified for cascade)

## Step 10 — Cascade Ifault
At TX-1: Ik"max = 1.05 × 230 / (√3 × |Z_TX|) ≈ 33 kA (theoretical — DNO PSCC declared 1.5 kA so use declared)
At CU-G (after 5m feeder): ≈ 1.5 kA (DNO declared limit)
At C01 final: ≈ 0.85 kA (cable drop dominates)
At C03 final: ≈ 0.79 kA

Engineer-declared PSCC at CU-G = 1.5 kA accepted as Ik"max anchor (overrides computed since DNO authority).

## Step 11 — Peak factor
LV cable-dominated: X/R ≈ 1-2 → κ ≈ 1.07-1.18. ipk_max at CU-G ≈ 2.5 kA peak.

## Step 12 — Tool call
Since DNO PSCC is engineer-declared and cable impedances are tabulated, this IS a case where calc.iec60909_cascade would refine but engineer-input fallback is reasonable. Emit tool_call_pending: true on intermediate nodes; final circuit Ifault computed from engineer PSCC + cable drop.

## Step 13 — Selectivity
DNO service fuse 100A (BS 1361 Type II, Icn 33 kA): adequate.
CU main switch (100A): no MCB Icn check at 1.5 kA — passes.
Final circuit MCBs (6 kA Icn): adequate at 0.8-1.5 kA cascade Ifault.

## Step 14 — Rationale block emitted (see output.json).
```

- [ ] **Step 3: Write `output.json`** (abbreviated; engineer/implementer fills full 8-section rationale)

```json
{
  "$schema": "../../schemas/fault-level-ir.schema.json",
  "drawing_type": "fault_level_study",
  "version": "1.0.0",
  "meta": {
    "project_id": "uk-dom-fl-eg01",
    "skill_version": "fault-level/1.0.0",
    "produced_at": "2026-05-16T12:00:00Z",
    "consumed_intents": []
  },
  "jurisdiction": "GB",
  "project_supply": {
    "lv_source": {
      "type": "utility_transformer",
      "kva": 500,
      "voltage_v": 230,
      "z_percent": 4.0,
      "x_over_r": 5,
      "near_or_far_from_generator": "far"
    }
  },
  "sources": [
    { "id": "utility-DNO", "kind": "utility", "contribution_method": "constant", "ifault_contribution_ka": 1.5 }
  ],
  "cascade": [
    { "node_id": "TX-1",         "parent_node_id": null,         "node_kind": "transformer_secondary", "designation": "500 kVA DNO TX LV terminals", "ifault_ka_max": 1.575, "ifault_ka_min": 1.425, "ipk_ka": 2.40, "x_over_r_at_node": 5, "z_total_ohm": 0.0042, "tool_call_pending": true },
    { "node_id": "CU-G",         "parent_node_id": "TX-1",       "node_kind": "board_incoming",         "designation": "Main CU 100A",                  "feeder": { "length_m": 5, "csa_mm2_or_awg": "25mm²", "material": "copper", "insulation": "pvc_70" }, "z_addition_ohm": {"r": 0.004, "x": 0.0005}, "ifault_ka_max": 1.50, "ifault_ka_min": 1.36, "ipk_ka": 2.30, "x_over_r_at_node": 2.5, "z_total_ohm": 0.008, "tool_call_pending": true },
    { "node_id": "CU-G.BUSBAR",  "parent_node_id": "CU-G",       "node_kind": "board_busbar",           "designation": "CU busbar",                     "ifault_ka_max": 1.49, "ifault_ka_min": 1.35, "ipk_ka": 2.28, "x_over_r_at_node": 2.5, "z_total_ohm": 0.0081, "tool_call_pending": true },
    { "node_id": "CU-G.C01",     "parent_node_id": "CU-G.BUSBAR","node_kind": "final_circuit_endpoint", "designation": "GF lighting",                    "feeder": { "length_m": 18, "csa_mm2_or_awg": "1.5mm²", "material": "copper", "insulation": "pvc_70" }, "z_addition_ohm": {"r": 0.22, "x": 0.004}, "ifault_ka_max": 0.85, "ifault_ka_min": 0.77, "ipk_ka": 1.22, "x_over_r_at_node": 0.5, "z_total_ohm": 0.228, "tool_call_pending": true },
    { "node_id": "CU-G.C03",     "parent_node_id": "CU-G.BUSBAR","node_kind": "final_circuit_endpoint", "designation": "GF sockets ring",                "feeder": { "length_m": 38, "csa_mm2_or_awg": "2.5mm²", "material": "copper", "insulation": "pvc_70" }, "z_addition_ohm": {"r": 0.281, "x": 0.009}, "ifault_ka_max": 0.79, "ifault_ka_min": 0.71, "ipk_ka": 1.14, "x_over_r_at_node": 0.4, "z_total_ohm": 0.289, "tool_call_pending": true }
  ],
  "selectivity_implications": [
    { "breaker_id": "DNO-100A", "breaker_rating_a": 100, "breaker_icn_ka": 33, "ifault_at_breaker_ka": 1.575, "adequate": true, "recommendation": "BS 1361 Type II service fuse 100A Icn 33 kA — adequate" },
    { "breaker_id": "CU-MAIN", "breaker_rating_a": 100, "breaker_icn_ka": 6, "ifault_at_breaker_ka": 1.50, "adequate": true, "recommendation": "Main switch (not breaker — isolator) — Ifault well within rating" },
    { "breaker_id": "MCB-C01", "breaker_rating_a": 6, "breaker_icn_ka": 6, "ifault_at_breaker_ka": 0.85, "adequate": true, "recommendation": "6 kA MCB adequate at 0.85 kA cascade" }
  ],
  "compliance_summary": {
    "compliant": true,
    "non_compliance_flags": [],
    "assumptions": [
      "DNO declared PSCC 1.5 kA at service head — engineer input.",
      "Transformer Zpu 4% assumed (no nameplate provided) per IEC60909/transformer-zpu-table.json default for 500 kVA.",
      "Cable impedance from BS 7671 Appendix 4 Tables 4D5 (R) + 4F (X).",
      "tool_call_pending: true on all nodes — calc.iec60909_cascade runtime not yet available."
    ]
  },
  "drawn_as_symbols": ["TRANSFORMER", "BREAKER", "BUSBAR", "EARTH_GENERAL"],
  "flags": ["TOOL-CALL-PENDING"],
  "rationale": {
    "chat_summary": "UK 3-bed semi on 500 kVA DNO TX with declared PSCC 1.5 kA at service head. 5-node cascade (TX → CU → 2 final circuits). All Ifault values within standard MCB Icn 6 kA. Selectivity adequate at all nodes. tool_call_pending until calc.iec60909_cascade runs — values are engineer-input fallback.",
    "sections": [
      { "title": "Source Specification", "summary": "Single utility source. 500 kVA distribution TX. Zpu 4% assumed (IEC 60909-2 default).", "decisions": [ { "label": "Far-from-generator method", "summary": "Utility-only project, no on-site generation.", "rule": "IEC 60909-0:2016 §3.4 far-from-generator constant source", "code_clause": "IEC 60909-0:2016 §3.4", "inputs": { "kva": 500, "zpu_pct": 4.0 } } ] },
      { "title": "Cascade Topology", "summary": "5 nodes engineer-declared (no db-layout-rollup intent supplied).", "decisions": [] },
      { "title": "HV-side Assumptions", "summary": "N/A — no HV side present (LV-fed service).", "decisions": [] },
      { "title": "Transformer + Source Impedances", "summary": "Z_TX = 4.23 mΩ at 230V LV with X/R = 5.", "decisions": [ { "label": "Z_TX = 4.23 mΩ", "summary": "Computed from Zpu × U² / kVA per IEC 60909-0.", "rule": "IEC 60909-0:2016 §4.3 transformer impedance", "code_clause": "IEC 60909-0:2016 §4.3", "inputs": { "z_tx_ohm": 0.00423 } } ] },
      { "title": "Motor Contribution Assessment", "summary": "Motor load 0 kW → no motor contribution. Threshold ≥ 1% not met.", "decisions": [] },
      { "title": "Per-node Ifault Computation", "summary": "Ik\"max range 0.79-1.575 kA across cascade. ipk range 1.14-2.40 kA.", "decisions": [ { "label": "tool_call_pending across all nodes", "summary": "calc.iec60909_cascade runtime not yet available; engineer-input PSCC + cable tables used as fallback.", "rule": "WI3 deferral pattern", "code_clause": "shared/calculations/electrical/iec60909-cascade.json", "inputs": { "tool_call_pending": true } } ] },
      { "title": "Selectivity Implications", "summary": "All breakers in cascade adequate at their installation Ifault. DNO 100A fuse Icn 33 kA, CU MCBs Icn 6 kA.", "decisions": [] },
      { "title": "Compliance + Assumptions", "summary": "Compliant. Single TOOL-CALL-PENDING flag for deferred cascade tool.", "decisions": [] }
    ]
  }
}
```

- [ ] **Step 4: Validate IR + commit**

```bash
python3 - <<'PY'
import json
from jsonschema import Draft7Validator
ir_schema = json.load(open('electrical/fault-level/schemas/fault-level-ir.schema.json'))
rationale_schema = json.load(open('shared/schemas/core/rationale.schema.json'))
ir_no_id = dict(ir_schema)
ir_no_id.pop('$id', None)
ir_no_id['properties']['rationale'] = rationale_schema
out = json.load(open('electrical/fault-level/examples/uk-domestic-single-source/output.json'))
errors = list(Draft7Validator(ir_no_id).iter_errors(out))
for e in errors[:5]:
    print(f'  ERR: {e.message} at {list(e.absolute_path)}')
assert not errors, f'{len(errors)} validation errors'
print('Example 1 IR schema-valid')
PY
git add electrical/fault-level/examples/uk-domestic-single-source/
git commit -m "feat: fault-level example 1 — UK domestic single-source (schema-conformant)"
```

---

## Task 32: Example 2 — INT commercial with genset

**Files:**
- Create: `electrical/fault-level/examples/intl-commercial-with-genset/input.json`
- Create: `electrical/fault-level/examples/intl-commercial-with-genset/reasoning.md`
- Create: `electrical/fault-level/examples/intl-commercial-with-genset/output.json`

INT commercial 400V TPN: 1600 kVA DNO TX (~25 kA PSCC) + 800 kVA standby genset. Two-source modelling, near-from-generator decrement applied in gen-mode.

Follow Task 31's pattern:

- [ ] **Step 1: Write `input.json`** — jurisdiction "INT", supply_voltage_v "400", phase_arrangement "TPN" (handled by IR), primary_transformer_kva 1600 with zpu 5%, standby_generator_present true with kva 800, hv_side_present true with 11 kV declared 16 kA PSCC, engineer-declared cascade has HV-1 → TX-1 → MSB-1 → 4 sub-DBs

- [ ] **Step 2: Write `reasoning.md`** — Standards: IEC 60909 family + IEC 60364 (NOT BS 7671). HV-side modelled. Generator with subtransient decrement.

- [ ] **Step 3: Write `output.json`** — IR with:
  - `project_supply.hv_side` populated (11 kV, ring main, 16 kA, X/R 5)
  - `project_supply.lv_source.type: "mixed"` (utility + gen)
  - `sources[]` array has TWO entries: utility (`kind: "utility"`, `contribution_method: "constant"`) + generator (`kind: "generator"`, `contribution_method: "subtransient_decrement"`, decrement profile)
  - 5+ cascade nodes (HV → TX → MSB → 4 sub-DBs)
  - Rationale cites `IEC 60909-0:2016 §3.5` (near-from-generator) verbatim

- [ ] **Step 4: Validate + commit**

Run the same schema validation idiom as Task 31. Confirm sources[] has ≥ 2 entries, jurisdiction is "INT", no BS 7671 / NEC citations.

```bash
git add electrical/fault-level/examples/intl-commercial-with-genset/
git commit -m "feat: fault-level example 2 — INT commercial 1600 kVA + standby genset (multi-source)"
```

---

## Task 33: Example 3 — US industrial with motors

**Files:**
- Create: `electrical/fault-level/examples/us-industrial-with-motors/input.json`
- Create: `electrical/fault-level/examples/us-industrial-with-motors/reasoning.md`
- Create: `electrical/fault-level/examples/us-industrial-with-motors/output.json`

US 480V TPN industrial: 12.47 kV HV primary, 2500 kVA TX (~35 kA PSCC), 500 kW connected motor load (material contribution per IEC 60909-0 §4.5).

Follow Task 31's pattern:

- [ ] **Step 1: Write `input.json`** — jurisdiction "US", supply_voltage_v "480", hv_side_present true (12.47 kV, 25 kA PSCC primary), primary_transformer_kva 2500 with zpu 6%, motor_load_kw 500, engineer-declared cascade HV-1 → TX-1 → MSB-1 → MCC-1 + 3 sub-DBs

- [ ] **Step 2: Write `reasoning.md`** — Standards: IEC 60909 + IEC 60617 + NEC chapter1 + 240 + chapter9 (NOT BS 7671 / IEC 60364). Motor contribution included per §4.5.1.2. NEC 110.9 cited.

- [ ] **Step 3: Write `output.json`** — IR with:
  - `jurisdiction: "US"`
  - `project_supply.hv_side` populated
  - `sources[]` has utility + motor_aggregate (ΣP = 500 kW + ILR ≈ 5 → contribution ≈ 3 kA at MCC bus)
  - Citations: NEC 2023 Art 110.9, NEC 2023 Art 240, IEC 60909-0:2016 §4.5
  - **NO** BS 7671 / IEC 60364 citations

- [ ] **Step 4: Validate + confirm NEC-only**

```bash
python3 - <<'PY'
import json
from jsonschema import Draft7Validator
ir_schema = json.load(open('electrical/fault-level/schemas/fault-level-ir.schema.json'))
rationale_schema = json.load(open('shared/schemas/core/rationale.schema.json'))
ir_no_id = dict(ir_schema)
ir_no_id.pop('$id', None)
ir_no_id['properties']['rationale'] = rationale_schema
out = json.load(open('electrical/fault-level/examples/us-industrial-with-motors/output.json'))
Draft7Validator(ir_no_id).validate(out)
print('US example schema-valid')
text = json.dumps(out)
assert 'BS 7671' not in text, 'US example must not cite BS 7671'
assert 'IEC 60364' not in text, 'US example must not cite IEC 60364'
print('US example: NEC + IEC 60909 only confirmed')
PY
git add electrical/fault-level/examples/us-industrial-with-motors/
git commit -m "feat: fault-level example 3 — US industrial 2500 kVA + 500 kW motor (NEC-only)"
```

---

## Task 34: Rewrite `README.md`

**Files:**
- Create: `electrical/fault-level/README.md`

- [ ] **Step 1: Write the README**

```markdown
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

Sibling standards layer at `shared/standards/electrical/IEC60909/` (11 files).

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
```

- [ ] **Step 2: Validate + commit**

```bash
python3 -c "
new = [l.strip() for l in open('electrical/fault-level/README.md') if l.startswith('## ')]
required = ['## What this skill produces', '## Jurisdictions supported', '## Cross-drawing intent contract', '## File structure', '## Eval coverage matrix', '## Tool calls awaiting runtime', '## Known limitations', '## Versioning']
for r in required:
    assert r in new, f'Missing: {r}'
print(f'{len(new)} sections, all required present')
"
git add electrical/fault-level/README.md
git commit -m "docs: fault-level README — eval coverage + jurisdiction table + intent contracts"
```

---

## Task 35: Final verification + SKILLS_STATUS.md update

**Files:**
- Modify: `SKILLS_STATUS.md`
- Verify: All 55 files (11 IEC60909 + 44 skill)

- [ ] **Step 1: File-count verification**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills" && \
python3 << 'PYEOF'
import os

iec60909_files = [
    'README.md', 'meta.json', 'terminology.md', 'amendments-summary.md',
    'part0-fundamentals.json', 'part0-method.md',
    'peak-factor-kappa.json', 'voltage-factor-c.json',
    'source-impedances.json', 'transformer-zpu-table.json',
    'generator-subtransient-tables.json', 'motor-contribution-rules.json',
    'compliance-checklist.md'
]

skill_files = {
    'skill-level': ['README.md', 'CHANGELOG.md', 'skill.manifest.json', 'inputs.json'],
    'prompts': ['generator.md', 'validator.md', 'reviewer.md'],
    'schemas': ['fault-level-ir.schema.json', 'fault-level-intent.schema.json'],
    'rules': ['source-impedance-defaults.yaml', 'motor-contribution-thresholds.yaml', 'voltage-factor-c-selection.yaml', 'ups-current-limiting.yaml', 'peak-factor-kappa.yaml'],
    'constraints': ['breaker-icn-vs-ifault.yaml', 'busbar-ipk-vs-cascade-ipk.yaml', 'cable-i2t-vs-cascade.yaml', 'source-impedance-bounds.yaml'],
    'validation': ['cascade-tree-integrity.yaml', 'ifault-monotonicity.yaml', 'tool-call-resolved.yaml', 'intent-shape.yaml'],
    'ontology': ['source-types.json', 'cascade-node-kinds.json'],
    'docs': ['engineering-philosophy.md', 'known-limitations.md'],
    'evals': ['runner-config.json', 'eval-01-uk-domestic-cu-cascade.yaml', 'eval-02-tpn-commercial-with-gen.yaml', 'eval-03-undersized-breaker-trap.yaml', 'eval-04-missing-source-data.yaml', 'eval-05-jurisdiction-us-with-hv.yaml', 'eval-06-rationale-block.yaml', 'eval-07-multi-source-coordination.yaml', 'eval-08-induction-motor-contribution.yaml', 'eval-09-intent-shape.yaml'],
    'examples/uk-domestic-single-source': ['input.json', 'reasoning.md', 'output.json'],
    'examples/intl-commercial-with-genset': ['input.json', 'reasoning.md', 'output.json'],
    'examples/us-industrial-with-motors': ['input.json', 'reasoning.md', 'output.json'],
}

missing = []
total = 0
# IEC60909 layer (filter README.md duplicate — listed under skill-level too)
for f in iec60909_files[:-1]:  # 11 unique entries (one of the 13 list items duplicates somewhere)
    total += 1
    p = f'shared/standards/electrical/IEC60909/{f}'
    if not os.path.isfile(p):
        missing.append(p)

# Skill files
root = 'electrical/fault-level'
for subdir, files in skill_files.items():
    base = root if subdir == 'skill-level' else f'{root}/{subdir}'
    for f in files:
        total += 1
        p = f'{base}/{f}'
        if not os.path.isfile(p):
            missing.append(p)

print(f'Expected files: {total}')
print(f'Missing: {len(missing)}')
for m in missing: print(f'  - {m}')
assert not missing, f'{len(missing)} files missing'
print('All files present')
PYEOF
```
Expected: `Expected files: 55+`, `Missing: 0`, `All files present`

- [ ] **Step 2: Consumption-pattern proof**

```bash
python3 -c "
import json, os
m = json.load(open('electrical/fault-level/skill.manifest.json'))
folders = [s for s in m['standards'] if s.endswith('/')]
files = [s for s in m['standards'] if not s.endswith('/')]
print(f'standards: {len(files)} files, {len(folders)} folders')
assert len(folders) == 0
assert len(files) == 21
missing = [f for f in m['standards'] if not os.path.isfile(f)]
print(f'Missing on disk: {len(missing)}')
for x in missing: print(f'  - {x}')
assert not missing
print('Consumption-pattern proof: PASS')
"
```

- [ ] **Step 3: Schemas valid + examples schema-valid**

```bash
python3 - <<'PY'
import json, glob, jsonschema
from jsonschema import Draft7Validator

# 3 schemas valid
for f in ['fault-level-ir.schema.json', 'fault-level-intent.schema.json']:
    s = json.load(open(f'electrical/fault-level/schemas/{f}'))
    jsonschema.Draft7Validator.check_schema(s)
    print(f'{f}: schema valid')

# 3 examples schema-valid
ir_schema = json.load(open('electrical/fault-level/schemas/fault-level-ir.schema.json'))
rationale_schema = json.load(open('shared/schemas/core/rationale.schema.json'))
ir_no_id = dict(ir_schema)
ir_no_id.pop('$id', None)
ir_no_id['properties']['rationale'] = rationale_schema
v = Draft7Validator(ir_no_id)
for out_path in sorted(glob.glob('electrical/fault-level/examples/*/output.json')):
    name = out_path.split('/')[-2]
    errors = list(v.iter_errors(json.load(open(out_path))))
    print(f'{name}: {"PASS" if not errors else f"FAIL ({len(errors)} errors)"}')
PY
```

- [ ] **Step 4: Update SKILLS_STATUS.md**

Read the current file. If a `fault-level` row exists, update it; otherwise add one.

```bash
grep -nE "^\| fault-level" SKILLS_STATUS.md
```

Edit/add:
```
| fault-level | `electrical/fault-level` | **beta** | IEC 60909-0:2016, BS 7671 Reg 434, IEC 60364-4-43, NEC 110.9 + 240.86, IEC 60617 | 9/3 ✓ | v1.0.0 IEC 60909 HV+LV cascade. 14-step generator, IR + intent schemas, 12 deterministic checks, 9 evals (all WI5 + 3 skill-specific), 3 worked examples (UK / INT+gen / US+motors). New IEC60909 standards layer (11 files) shipped alongside. Cascade math deferred to calc.iec60909_cascade runtime tool per WI3. |
```

- [ ] **Step 5: Final commit**

```bash
git add electrical/fault-level/ shared/standards/electrical/IEC60909/ SKILLS_STATUS.md
git commit -m "feat(fault-level): v1.0.0 beta — IEC 60909 HV+LV cascade complete

55 files total:
- 11 in shared/standards/electrical/IEC60909/ (new standards layer)
- 44 in electrical/fault-level/ matching earthing + db-layout pattern

Verified:
- 21 standards files referenced as specific paths (0 folders) — consumption-pattern proof
- All standards files exist on disk
- All 2 schemas valid draft-07 (IR + intent)
- All 3 example outputs validate against IR schema
- consumes_intents: db-layout-rollup (cascade topology source)
- produces_intent: fault-level (resolves db-layout selectivity tool_call_pending)

Calc tool deferral (per WI3): calc.iec60909_cascade contract shipped Item 1 (commit 34e28e7);
runtime executor pending in separate runtime project."
```

- [ ] **Step 6: Skill summary check**

```bash
echo "=== fault-level skill ==="
find electrical/fault-level -type f | wc -l | xargs -I{} echo "Files: {}"
echo "=== IEC60909 standards layer ==="
find shared/standards/electrical/IEC60909 -type f | wc -l | xargs -I{} echo "Files: {}"
echo "=== Lines ==="
find electrical/fault-level shared/standards/electrical/IEC60909 -type f -exec wc -l {} + | tail -1
```

Expected: 44 + 11 = 55 files; line count 3500-6000.

---

## Self-Review Checklist

After all 35 tasks execute:

1. **Spec coverage:** Re-read `docs/superpowers/specs/2026-05-16-fault-level-skill-design.md` § File Set. Every named file must exist.
2. **Type consistency:** `source_types` enum (utility_transformer / generator / ups / mixed) consistent across schema + ontology + rules + examples. `node_kinds` enum (hv_source / transformer_secondary / board_incoming / board_busbar / board_outgoing_feeder / final_circuit_endpoint) consistent across schema + ontology + examples.
3. **Cross-task path references:** Task 13 (manifest), Task 16 (generator), Tasks 22-30 (evals), Tasks 31-33 (examples) all reference the same 21 standards files. Verified in Task 35 Step 2.
4. **Consumption-pattern proof:** Task 35 Step 2 verifies; should pass.
5. **Cross-skill contract:** Emitted fault-level intent satisfies db-layout v1.0's consumed_intent shape — verified by eval-09 + Task 35 Step 3.
6. **WI alignment:**
   - WI1 (inputs taxonomy): Task 12 — inputs.json
   - WI2 (rationale block): Task 10 (schema $ref), Task 16 (Step 14), eval-06
   - WI3 (calc executor deferral): cascade[*].tool_call_pending, declared in Task 10 schema + Task 16 Step 12 + Task 21 docs
   - WI4 (cross-drawing intents): Task 11 (intent schema), Task 13 (manifest consumes/produces), eval-09
   - WI5 (eval categories): Tasks 22-30 cover all 6 + 3 skill-specific

---

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-05-16-fault-level-skill.md`.**

Two execution options:

**1. Subagent-Driven (recommended)** — Dispatch a fresh subagent per task, review between tasks. Used successfully for earthing + db-layout.

**2. Inline Execution** — Execute tasks in this session via `executing-plans`, batch execution with checkpoints.

Which approach?
