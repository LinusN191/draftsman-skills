# Cable-Sizing Skill — Design Spec

**Date:** 2026-05-16
**Status:** Approved — ready for implementation plan
**Target:** `electrical/cable-sizing` v1.0.0 beta
**Tier-1 sequence item:** 3 of 7 (after Item 1 calc contracts + Item 2 fault-level)

---

## 1. Overview

The `cable-sizing` skill produces per-circuit cable selection (phase csa + CPC csa + insulation + installation method + parallel count) for every cable run in a project's distribution cascade, with the *binding constraint named* per node. It consumes upstream intents (`db-layout-rollup` + `fault-level`) where available, falls back to engineer-declared inputs, and emits a slim `cable-sizing` intent consumed by `cable-schedule`, `riser`, and `cable-containment`.

The skill walks the standard csa ladder from below for each circuit, accepts the smallest size that simultaneously satisfies `Iz ≥ In`, cumulative `Vd ≤ limit`, and the CPC adiabatic equation. The walk-up trail and binding constraint are recorded per node so tender reviewers and DRC checkers can verify every selection without rerunning the calc.

### 1.1 Drawing type + version

- `drawing_type: "cable_sizing_study"`
- `version: "1.0.0"`
- `status: "beta"`

### 1.2 Pattern parent

Same artefact pattern as `electrical/earthing`, `electrical/db-layout`, and `electrical/fault-level` — 14-step generator + 10-INV validator + 8-D reviewer, project-scoped cascade IR, 9 evals (6 WI5 + 3 skill-specific), 3 worked examples.

---

## 2. Scope

### 2.1 In-scope (v1.0.0)

| Dimension | Coverage |
|---|---|
| Jurisdictions | GB (BS 7671 App 4), EU/INT (IEC 60364-5-52), US (NEC Chapter 9 + 310.16) |
| Conductor material | Copper + aluminium |
| Sizing units | IEC mm² (1.0 – 630) + AWG (14 AWG – 1000 kcmil) |
| Cable types | PVC singles, XLPE/EPR, MICC, SWA, fire-rated (FP200/CWZ); THWN-2 / THHN / XHHW-2 for NEC |
| Phases | Single-phase 2-wire, three-phase 3-wire, three-phase 4-wire (with neutral) |
| Installation methods | A1, A2, B1, B2, C, D1, D2, E, F, G (IEC) + NEC conduit / cable-tray / direct-burial / free-air |
| Extra engineering checks | Cumulative Vd, motor-starting Vd, parallel cables, harmonic derating |

### 2.2 Out-of-scope (deferred)

- DC circuit sizing (PV strings, EV DCFC, battery interconnects) → `dc-cable-sizing` sibling skill
- IEC 60287 thermal modelling beyond standard tables (very large buried cable groups)
- Arc-flash incident-energy boundary marking → `arc-flash` sibling skill
- Communications + data cables (Cat6, fibre) → different standards family

---

## 3. File structure

```
electrical/cable-sizing/
├── README.md
├── CHANGELOG.md
├── skill.manifest.json
├── inputs.json

├── prompts/
│   ├── generator.md        (14-step chain)
│   ├── validator.md        (10 INV invariants)
│   └── reviewer.md         (8 D dimensions)

├── schemas/
│   ├── cable-sizing-ir.schema.json
│   └── cable-sizing-intent.schema.json

├── rules/                  (5 YAMLs)
│   ├── csa-selection-walk-up.yaml
│   ├── voltage-drop-targets.yaml
│   ├── correction-factor-stack.yaml
│   ├── parallel-cables-threshold.yaml
│   └── harmonic-derating-trigger.yaml

├── constraints/            (4 YAMLs)
│   ├── iz-vs-in-vs-ib.yaml
│   ├── vd-cumulative-limit.yaml
│   ├── cpc-adiabatic-passes.yaml
│   └── motor-starting-vd-limit.yaml

├── validation/             (4 YAMLs, 12 checks)
│   ├── cascade-tree-integrity.yaml
│   ├── csa-on-standard-ladder.yaml
│   ├── tool-call-resolved.yaml
│   └── intent-shape.yaml

├── ontology/
│   ├── cable-types.json
│   └── installation-methods.json

├── docs/
│   ├── engineering-philosophy.md
│   └── known-limitations.md

├── evals/
│   ├── runner-config.yaml
│   └── eval-01 … eval-09.yaml

└── examples/
    ├── uk-domestic-final-circuits/
    ├── intl-commercial-with-feeders/
    └── us-industrial-with-motors/
```

**Standards layer:** No new standards files required. All references exist in `shared/standards/electrical/BS7671/`, `IEC60364/`, and `NFPA70/`.

**Calc contracts:** All three required calc contracts exist in `shared/calculations/electrical/`:
- `cable-ampacity.json` → `calc.cable_ampacity`
- `voltage-drop.json` → `calc.voltage_drop`
- `cpc-adiabatic.json` → `calc.cpc_adiabatic`

---

## 4. Data flow

### 4.1 Inputs (hybrid mode)

**Consumed from upstream intents (preferred):**

| Source intent | Fields used | If absent |
|---|---|---|
| `db-layout-rollup` | Per-circuit: `Ib`, `In`, `load_type`, `phases`, `parent_board`, `selectivity_pending`, `t_clear_at_ifault_s` (from OCPD time-current curve) | Engineer declares full circuit list AND engineer-declared `t_clear` per node |
| `fault-level` | Per-node: `ifault_ka_max`, `ifault_ka_min`, `x_over_r`, `z_total_ohm` | Engineer declares per-node Ifault |

`t_clear` is the OCPD clearing time at the prospective fault current — sourced from `db-layout-rollup` (which ran selectivity against device curves) when available, otherwise engineer-declared per node. It feeds `calc.cpc_adiabatic` directly.

**Always engineer-declared (route data):**

- `length_m` per cable segment
- `installation_method` per circuit
- `ambient_c` per segment (default 30°C)
- `grouping_count` per segment (default 1)
- `in_thermal_insulation` boolean (default false)
- `harmonic_content_pct` per circuit (default 0%)
- `terminal_temp_rating_c` for US jurisdiction (default 75°C)
- `cable_type_preference` per segment (defaults: PVC domestic, XLPE commercial feeders)

### 4.2 IR shape — project-scoped cascade tree

Top-level structure mirrors `fault-level-ir`. Every cascade node carries:

```json
{
  "node_id": "MSB-1.F03.DB-L1.C07",
  "parent_node_id": "MSB-1.F03.DB-L1",
  "node_kind": "final_circuit | feeder | sub_feeder | service_entrance",
  "designation": "Lighting circuit L1-C07",
  "load": {"ib_a": 8.5, "in_a": 10, "phases": "single", "load_type": "lighting", "pf": 1.0},
  "route": {
    "length_m": 32,
    "installation_method": "B1",
    "ambient_c": 30,
    "grouping_count": 2,
    "in_thermal_insulation": false
  },
  "harmonic_content_pct": 0,
  "selection": {
    "phase_csa_mm2": 2.5,
    "cpc_csa_mm2": 1.5,
    "material": "copper",
    "insulation": "pvc_70",
    "cable_type": "pvc_singles",
    "parallel_count": 1,
    "binding_constraint": "vd_cumulative",
    "walk_up_trail": [
      {"csa_mm2": 1.5, "rejected_by": "vd_cumulative", "vd_cumulative_pct": 4.2},
      {"csa_mm2": 2.5, "accepted": true, "vd_cumulative_pct": 2.9}
    ]
  },
  "checks": {
    "iz_corrected_a": 23.1,
    "iz_vs_in_pass": true,
    "vd_segment_pct": 1.7,
    "vd_cumulative_pct": 2.9,
    "vd_pass": true,
    "vd_limit_pct": 3.0,
    "vd_limit_source": "BS 7671:2018 App 12 lighting circuits",
    "cpc_adiabatic_pass": true,
    "motor_starting_vd_pct": null,
    "tool_call_pending": true
  }
}
```

### 4.3 Output intent — slim downstream subset

```json
{
  "intent_kind": "cable-sizing",
  "version": "1.0.0",
  "circuits": [
    {
      "node_id": "MSB-1.F03.DB-L1.C07",
      "designation": "Lighting circuit L1-C07",
      "phase_csa_mm2_or_awg": "2.5 mm²",
      "cpc_csa_mm2_or_awg": "1.5 mm²",
      "material": "copper",
      "insulation": "pvc_70",
      "cable_type": "pvc_singles",
      "parallel_count": 1,
      "cable_od_mm": 8.4,
      "weight_kg_per_m": 0.18,
      "length_m": 32,
      "installation_method": "B1",
      "parent_node_id": "MSB-1.F03.DB-L1"
    }
  ]
}
```

`cable_od_mm` and `weight_kg_per_m` are looked up from `shared/standards/electrical/<juris>/` cable-physical-data tables (already present in `BS7671/cable-types-overview.md` and `NFPA70/chapter9-tables.json`).

---

## 5. CSA-selection algorithm

### 5.1 Walk-the-ladder procedure (per cascade node)

```
Given (Ib, In, length, route, load_type, parent_node_ifault, harmonic_pct):

1. Determine starting csa from In:
   - GB/EU/INT: smallest csa where Iz_tabulated × selected_correction_factors ≥ In
   - US: smallest csa where Iz_tabulated × Ca × Cg ≥ In, then cap by terminal_temp_rating per 110.14(C)

2. For each csa on the standard ladder, in order:
     a. calc.cable_ampacity → Iz_corrected
     b. Check Iz_corrected ≥ In [Reg 433.1 / NEC 240.4(B)]
     c. calc.voltage_drop → vd_segment_pct
     d. cumulative_vd_pct = vd_segment_pct + parent_cumulative_vd_pct
     e. Check cumulative_vd_pct ≤ vd_limit_for_load_type
     f. calc.cpc_adiabatic with parent_ifault_ka_max + t_clear → required_cpc_csa
     g. Check cpc_csa fits adiabatic_pass
     h. If load_type == "motor": compute motor_starting_vd at LRA × Ib_motor; check ≤ 10%
   IF all pass → ACCEPT, record binding_constraint = the rejection reason at csa_one_below_selected
                 (i.e., the check that forced the walk up). If the start csa passed all checks with
                 no walk-up, binding_constraint = "iz_vs_in" (sized purely by overcurrent rule).
   IF any fail → record reason, advance to next ladder size

3. If ladder exhausted at single-cable scope:
     - Engage parallel-cables rule
     - Smallest N where N × Iz_corrected ≥ In, N integer ≥ 2
     - Each parallel ≥ 50 mm² (IEC Reg 523.7) or ≥ 1/0 AWG (NEC 310.10(H))
     - Same length / csa / material / installation per parallel

4. Emit selection + walk_up_trail + binding_constraint per node.
```

### 5.2 Standard ladder

```yaml
ladder_mm2: [1.0, 1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240, 300, 400, 500, 630]
ladder_awg:  ["14", "12", "10", "8", "6", "4", "3", "2", "1", "1/0", "2/0", "3/0", "4/0", "250", "300", "350", "400", "500", "600", "750", "1000"]
```

### 5.3 CPC sizing

CPC csa is determined after the phase csa locks in:
- BS 7671 Table 54.7 + Reg 543.1.3: CPC via adiabatic OR Table 54.3 minimum, whichever larger
- IEC 60364-5-54 equivalent
- NEC 250.122: from Table 250.122 based on OCPD rating

CPC can be smaller than phase (e.g., 16 mm² phase + 6 mm² CPC if adiabatic passes).

### 5.4 Tool-call deferral (WI3)

Until the runtime ships `calc.cable_ampacity`, `calc.voltage_drop`, and `calc.cpc_adiabatic`, the generator emits the cascade with `tool_call_pending: true` on every node and proceeds with best-effort engineer estimates as placeholder values. Same pattern as `fault-level`.

### 5.5 Binding-constraint vocabulary

| Token | Meaning |
|---|---|
| `iz_vs_in` | Ampacity drove the csa up (or sized at start csa with no walk) |
| `vd_cumulative` | Cumulative Vd (source → endpoint sum) exceeded limit at smaller csa |
| `motor_starting_vd` | Motor inrush Vd at LRA exceeded 10% (with downsize alternative rejected) |
| `cpc_adiabatic` | CPC adiabatic failed at smaller phase csa → phase upsized to permit larger CPC |
| `parallel_required` | Single cable exhausted standard ladder; N×csa parallel cables required |
| `harmonic_derating` | Ch < 1.0 derated Iz enough to force upsize |

---

## 6. Extra engineering checks

### 6.1 Cumulative voltage drop

Per-segment Vd is misleading: a 4% feeder + 4% branch = 8% at the load, which violates BS 7671 App 12. The cascade tree supports cumulative Vd naturally — each node's `vd_cumulative_pct = vd_segment_pct + parent.vd_cumulative_pct`.

**Limits by jurisdiction + load type:**

| Jurisdiction | Lighting | Power | Motor running | Source |
|---|---|---|---|---|
| GB | 3% | 5% | 5% | BS 7671:2018 App 12 |
| EU/INT | 3% | 5% | 5% | IEC 60364-5-52 §G |
| US | feeder-only 3% / feeder+branch 5% | same | same | NEC 215.2(A)(1) IN 2 |

Engineer may override per circuit when client spec is tighter.

### 6.2 Motor-starting voltage drop

Triggered when `load_type == "motor"`:

```
vd_starting_pct = vd_running_pct × (locked_rotor_current / running_current)
```

Locked-rotor multiplier defaults: NEMA Design B = 6.0, Design C = 5.0, IEC AA = 7.0, IEC AB = 6.0.

Limit: 10% transient (load may stall above). **Severity: warning, not error** — engineer may resolve with a soft-start/VFD rather than upsizing the cable.

Source: BS 7671:2018 §525.1 + Table 4Ab note 5; IEC 60364-5-52 §525.1; NEC 430.6(A)(1) + NEMA MG-1.

### 6.3 Parallel cables

Engage when single-cable selection at largest available csa fails `Iz ≥ In`:

- Minimum csa per parallel: 50 mm² (BS 7671 Reg 523.7 / IEC 60364-5-52 §523.6) or 1/0 AWG (NEC 310.10(H)(1))
- Required identical per parallel: length, csa, material, installation method, route (symmetrical impedances → balanced current sharing)
- Search starts N = 2, steps +1, max 6 (above 6 → redesign with bus duct)

### 6.4 Harmonic derating

Triggered when `harmonic_content_pct > 15` AND `circuit_type == "three_phase_four_wire"`:

| Jurisdiction | Ch lookup | Neutral sizing |
|---|---|---|
| GB | BS 7671:2018 App 4 §5.5 Table 4Ab | Reg 523.6.3: neutral = phase when h3 > 33% |
| EU/INT | IEC 60364-5-52:2009 Annex E §E.5 | As above |
| US | NEC 310.15(E) + IN Table 310.15(B)(4)(a) | NEC 220.61(C)(2): full neutral when h3 > 50% |

Engineer must declare harmonic content for: IT loads / server rooms / data centres / LED lighting >10 kW / VFD-fed motors / UPS rectifier inputs.

---

## 7. Prompts

### 7.1 Generator — 14-step chain (`prompts/generator.md`)

1. Ingest `db-layout-rollup` intent → extract circuit list, parent topology, Ib, In, load_type
2. Ingest `fault-level` intent → extract per-node Ik" max + Ik" min + t_clear
3. Determine jurisdiction → load applicable Vd limits + ampacity table family + correction factor stack
4. Build cascade tree (node_id paths) — service entrance → feeder → sub-feeder → final circuit
5. Engineer-declared overlay → length, installation_method, ambient, grouping, harmonic_content_pct per node
6. Per node (root → leaves): determine starting csa from In + correction factors
7. Walk-up loop: `calc.cable_ampacity` → check Iz vs In
8. `calc.voltage_drop` → compute vd_segment_pct → add parent's cumulative → check vs limit
9. `calc.cpc_adiabatic` with parent_ifault + t_clear → check CPC sizing
10. If `load_type == motor`: compute vd_starting_pct at LRA × Ib_motor → check ≤ 10%
11. If ladder exhausted: engage parallel-cables rule (minimum csa + count + symmetry)
12. Record selection + binding_constraint + walk_up_trail per node
13. Emit `cable-sizing` intent (slim downstream subset) alongside the IR
14. Assemble rationale block (8 sections + chat_summary per WI2)

### 7.2 Validator — 10 INV invariants (`prompts/validator.md`)

| INV | Statement |
|---|---|
| INV-01 | Every cascade node has a valid `node_id` matching path pattern (board.feeder.circuit) |
| INV-02 | Every non-root node has `parent_node_id` resolvable to another node |
| INV-03 | Every `selection.phase_csa` is on the standard ladder for the jurisdiction |
| INV-04 | Every `checks.iz_corrected_a` ≥ `load.in_a` |
| INV-05 | Every `checks.vd_cumulative_pct` ≤ `checks.vd_limit_pct` for its load type |
| INV-06 | Every `checks.cpc_adiabatic_pass` is true OR `binding_constraint == "cpc_adiabatic"` (with upsized phase) |
| INV-07 | Motor nodes have `motor_starting_vd_pct` populated; non-motor have it null |
| INV-08 | Parallel nodes have `parallel_count ≥ 2` AND each parallel ≥ 50 mm² (IEC) or ≥ 1/0 AWG (NEC) |
| INV-09 | Every node carries `tool_call_pending: true` OR the three calc outputs are populated |
| INV-10 | Emitted `cable-sizing` intent shape matches the schema and contains every final-circuit node |

### 7.3 Reviewer — 8 D dimensions (`prompts/reviewer.md`)

| D | Dimension |
|---|---|
| D1 | Sources cited per rule (every Vd limit + every Iz value cites a table) |
| D2 | Walk-up trail is auditable — each rejected csa names the failing check |
| D3 | Binding constraint matches the walk-up trail (no contradiction) |
| D4 | Cumulative Vd math sums up the parent chain (spot-check 2 random leaves) |
| D5 | CPC sizing references Table 54.7 (BS) / 250.122 (NEC) / IEC 60364-5-54 |
| D6 | Parallel cables (if any) satisfy symmetry + minimum csa rules |
| D7 | Harmonic derating applied where harmonic_content_pct > 15 AND 3-phase 4-wire |
| D8 | Rationale block: 8 sections present + chat_summary ≤ 200 words |

---

## 8. Rules / Constraints / Validation

### 8.1 Rules (5 YAMLs — engineering policies)

| File | Purpose |
|---|---|
| `csa-selection-walk-up.yaml` | Walk-the-ladder algorithm + acceptance criteria |
| `voltage-drop-targets.yaml` | Jurisdictional Vd limits by load type + override rules |
| `correction-factor-stack.yaml` | Order: Ca × Cg × Ci × Ch (with "larger-of" rules where standards specify) |
| `parallel-cables-threshold.yaml` | When to engage parallel + symmetry requirements |
| `harmonic-derating-trigger.yaml` | When to derate for 3rd-harmonic + neutral sizing |

### 8.2 Constraints (4 YAMLs — hard checks)

| File | Constraint |
|---|---|
| `iz-vs-in-vs-ib.yaml` | Ib ≤ In ≤ Iz |
| `vd-cumulative-limit.yaml` | Cumulative Vd ≤ limit |
| `cpc-adiabatic-passes.yaml` | S = √(I²t)/k passes |
| `motor-starting-vd-limit.yaml` | Vd × LRA-multiplier ≤ 10% (warning) |

### 8.3 Validation (4 YAMLs — IR integrity, 12 checks)

| File | Checks |
|---|---|
| `cascade-tree-integrity.yaml` | Tree connected, no orphans, no cycles, unique node_ids |
| `csa-on-standard-ladder.yaml` | Every selection.phase_csa + cpc_csa on the standard ladder |
| `tool-call-resolved.yaml` | Tool-call status consistent across IR |
| `intent-shape.yaml` | Emitted cable-sizing intent satisfies the schema |

---

## 9. Evals (9 — 6 WI5 categories + 3 skill-specific)

| Eval ID | WI5 category | Tests |
|---|---|---|
| eval-01-uk-domestic-final-circuits | happy_path | 230V UK domestic, copper PVC, 1.5–10 mm², ring + radial finals |
| eval-02-tpn-commercial-feeders-cumulative-vd | edge_case | 400V TPN cumulative Vd: feeder → sub-feeder → branch chain |
| eval-03-undersized-cable-trap | validation_trap | Engineer-declared 6 mm² where Vd binding requires 10 mm² — must flag + upsize |
| eval-04-missing-route-data | missing_input | No length/installation_method declared → `tool_call_pending`, no invention |
| eval-05-jurisdiction-us-with-awg | jurisdiction_switch | US 480V industrial, AWG sizing, terminal-temp cap, aluminium feeders |
| eval-06-rationale-block | rationale_block | 8 sections + WI2-conformant chat_summary, walk-up trail per node |
| eval-07-motor-starting-vd | skill_specific | 30 kW chiller motor on long feeder — vd_starting check + warning logic |
| eval-08-parallel-cables | skill_specific | 1200A MSB feeder — ladder exhausts at 630 mm², 2 × 400 mm² parallel |
| eval-09-harmonic-derating-data-centre | skill_specific | 3-phase 4-wire IT load with 33% h3 — Ch derating + neutral upsize |

---

## 10. Worked examples (3)

| Example | Demonstrates |
|---|---|
| `uk-domestic-final-circuits/` | 230V single-phase, copper PVC, 1.5–10 mm², lighting + power radial + 32A ring. Vd binding on lighting circuits. |
| `intl-commercial-with-feeders/` | 400V TPN: TX → MSB → riser → DB-L1 → final circuits. Cumulative Vd, XLPE feeders, copper. Cumulative-Vd binding on a long final circuit. |
| `us-industrial-with-motors/` | 480V industrial: aluminium feeder + AWG sizing + 500 hp motor with starting-Vd check + parallel cables for 1200A service entrance. |

Each example carries `input.json` (engineer inputs + consumed intents), `output.json` (full IR), `reasoning.md` (engineering narrative), `intent-out.json` (emitted cable-sizing intent).

---

## 11. Manifest — standards + calculations consumption

```json
{
  "skill": "cable-sizing",
  "version": "1.0.0",
  "discipline": "electrical",
  "subdiscipline": "circuit-sizing",
  "status": "beta",
  "inputs": [
    "jurisdiction",
    "circuits-from-intent-or-declared",
    "route-data-per-segment",
    "ambient-overlay",
    "grouping-per-segment",
    "harmonic-content-per-circuit",
    "vd-target-overrides",
    "cable-type-preferences"
  ],
  "outputs": ["cable-sizing-ir"],
  "produces_intent": ["cable-sizing"],
  "consumes_intents": ["db-layout-rollup", "fault-level"],
  "standards": [
    "shared/standards/electrical/BS7671/appendix4-cable-ratings.json",
    "shared/standards/electrical/BS7671/appendix4-cable-ratings-aluminium.json",
    "shared/standards/electrical/BS7671/appendix4-correction-factors.json",
    "shared/standards/electrical/BS7671/appendix12-voltage-drop.json",
    "shared/standards/electrical/BS7671/reg433-overcurrent-protection.json",
    "shared/standards/electrical/BS7671/reg434-fault-current.json",
    "shared/standards/electrical/BS7671/reg521-installation-methods.json",
    "shared/standards/electrical/BS7671/cable-types-fire-rated.json",
    "shared/standards/electrical/BS7671/cable-current-ratings.json",
    "shared/standards/electrical/IEC60364/part5-52-cable-ratings-copper.json",
    "shared/standards/electrical/IEC60364/part5-52-cable-ratings-aluminium.json",
    "shared/standards/electrical/IEC60364/part5-52-correction-factors.json",
    "shared/standards/electrical/IEC60364/part5-52-voltage-drop.json",
    "shared/standards/electrical/IEC60364/part5-52-installation-methods.json",
    "shared/standards/electrical/IEC60364/part4-43-overcurrent.json",
    "shared/standards/electrical/IEC60364/part5-54-earthing.json",
    "shared/standards/electrical/NFPA70/chapter9-tables.json",
    "shared/standards/electrical/NFPA70/art310-conductor-ampacity.json",
    "shared/standards/electrical/NFPA70/art240-overcurrent.json",
    "shared/standards/electrical/NFPA70/art215-feeders.json",
    "shared/standards/electrical/NFPA70/art210-branch-circuits.json",
    "shared/standards/electrical/NFPA70/ampacity-correction-factors.json"
  ],
  "calculations": [
    "shared/calculations/electrical/cable-ampacity.json",
    "shared/calculations/electrical/voltage-drop.json",
    "shared/calculations/electrical/cpc-adiabatic.json"
  ]
}
```

**Consumption-pattern proof:** 22 specific standards file references, 0 folders, 3 calc contract references — all already on disk.

---

## 12. Cross-skill contract verification

Before v1.0.0 ships, the emitted `cable-sizing` intent must satisfy the `consumed_intent` declaration in three downstream skill manifests (forward-compatible contract):

| Downstream skill | Consumes for | Required fields |
|---|---|---|
| `cable-schedule` | Formal tabulated deliverable | Full per-circuit set: csa, type, length, designation, OCPD ref |
| `riser` | LV riser diagrams floor-by-floor | Feeder-level + `parent_node_id` for parent-child rendering |
| `cable-containment` | Tray/conduit fill calculations | `cable_od_mm`, `weight_kg_per_m`, `parallel_count` per segment |

The `cable-sizing-intent.schema.json` is designed as the union superset. `validation/intent-shape.yaml` asserts schema coverage of this union.

---

## 13. Known limitations (v1.0.0)

Documented in `docs/known-limitations.md`. Does NOT cover:

- DC fault analysis or DC cable sizing → `dc-cable-sizing` future sibling
- Arc-flash incident-energy boundary marking → `arc-flash` sibling
- IEC 60287 advanced thermal modelling for buried cable groups (uses standard tables only)
- Communications/data cables (Cat6, fibre)
- Time-graded protection curve coordination (handled by `db-layout` + future `protection-coordination`)

---

## 14. Versioning policy

- Minor bumps (1.x.0): add new jurisdictions / cable types / evals / examples
- Major bump (2.0.0): reserved for DC scope OR breaking IR schema change
- Patch bumps (1.0.x): rules / constraints / validation bug fixes

---

## 15. Approval

All 7 design sections approved by user (2026-05-16). Ready for implementation plan.

Next step: invoke `superpowers:writing-plans` to produce `docs/superpowers/plans/2026-05-16-cable-sizing-skill.md`.
