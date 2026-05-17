# `electrical/arc-flash` Skill v1.0.0 — Design Spec (Phase B)

**Date:** 2026-05-17
**Status:** Approved — ready for implementation plan
**Sprint scope:** Phase B (the skill). Phase A standards layers (IEEE 1584 + NFPA 70E) shipped in the prior sprint (commits `b34976f..08e2521`).
**Pattern parent:** `electrical/fault-level/` + `electrical/cable-sizing/` — same artefact shape.

---

## 1. Overview & Scope

This sprint builds the `electrical/arc-flash` skill (~49 files) that consumes the IEEE 1584 + NFPA 70E standards layers shipped in Phase A. The skill produces project-scoped arc-flash analysis IR with per-node incident energy, arc-flash boundary, shock-approach boundaries, and PPE category.

### 1.1 Skill identity

- Name: `electrical/arc-flash`
- Version: `1.0.0` beta
- Drawing type: `arc_flash_study`
- Discipline: electrical / subdiscipline: safety-analysis

### 1.2 What it produces

Per cascade node:

- Incident energy at working distance (cal/cm²)
- Arc-flash boundary distance (where E = 1.2 cal/cm² = 2nd-degree burn threshold)
- Limited + Restricted shock-approach boundaries (NFPA 70E §130.4 — bundled because every arc-flash label carries them)
- PPE category 1–4 per NFPA 70E Table 130.7(C)(15)(c) + engineer override allowed
- `label_recommended: true | false` per NFPA 70E §130.5(H)
- `method_applied` tag identifying which of 5 methods produced the result
- `method_fallback_trail[]` showing every method tried + why earlier methods didn't fire

### 1.3 Five methods + fallback chain (controlled vocabulary)

| Method | Source | Bias | When used |
|---|---|---|---|
| `ieee1584_2018` | IEEE 1584:2018 §§6-10 + Annex C | Most realistic | Preferred for AC; requires transcribed coefficients |
| `ieee1584_2002` | IEEE 1584:2002 (Doughty/Neal) | Slightly conservative vs 2018 | Legacy compatibility OR fallback when 2018 coefficients null |
| `lee_1982` | Ralph Lee 1982 theoretical | **Significantly conservative** (2-5× higher IE than 2018) | Always-available fallback when no empirical coefficients transcribed |
| `nfpa70e_table` | NFPA 70E Table 130.7(C)(15)(a)/(b) | **Most conservative** — equipment-class lookup, no IE computed | Fallback when equipment can't be modelled |
| `dc_doan` | NFPA 70E Annex D §D.1 + Stokes & Oppenlander §D.2 | Realistic for DC | DC nodes only (current_type == "dc") |
| `pending` | — | — | tool_call_pending: true; all numeric outputs null |

### 1.4 Voltage range + current type

- 208V – 15 kV AC (IEEE 1584:2018 full range)
- DC up to 1000V (NFPA 70E Annex D scope)
- Unified cascade tree with per-node `current_type: ac | dc` tag

### 1.5 Out of scope (deferred)

- DC > 1000V (utility-scale PV 1500V systems) — v1.1
- BESS-specific safety analysis — separate `bess-safety` skill
- Arc-flash label content generation — separate `electrical/arc-flash-labelling` skill (stubbed for roadmap visibility)
- Time-graded protection coordination — separate `protection-coordination` skill (refines t_clear precision)
- Utility-MV-side fault contribution beyond what fault-level handles

---

## 2. File Structure (~49 files)

```
electrical/arc-flash/
├── README.md
├── CHANGELOG.md
├── skill.manifest.json
├── inputs.json                          (16-item discovery taxonomy)
│
├── prompts/
│   ├── generator.md                     (14-step chain)
│   ├── validator.md                     (10 INV invariants)
│   └── reviewer.md                      (8 D dimensions)
│
├── schemas/
│   ├── arc-flash-ir.schema.json
│   └── arc-flash-intent.schema.json
│
├── rules/                               (5 YAMLs)
│   ├── method-fallback-chain.yaml
│   ├── electrode-config-inference.yaml
│   ├── t-clear-defaults.yaml
│   ├── ppe-category-mapping.yaml
│   └── label-required-equipment.yaml
│
├── constraints/                         (4 YAMLs)
│   ├── incident-energy-finite.yaml
│   ├── boundary-distance-physical.yaml
│   ├── ppe-category-monotonic.yaml
│   └── method-fallback-consistency.yaml
│
├── validation/                          (4 YAMLs, 12 checks)
│   ├── cascade-tree-integrity.yaml
│   ├── method-applied-from-vocabulary.yaml
│   ├── tool-call-resolved.yaml
│   └── intent-shape.yaml
│
├── ontology/
│   ├── method-types.json
│   └── current-types.json
│
├── docs/
│   ├── engineering-philosophy.md
│   └── known-limitations.md
│
├── evals/
│   ├── runner-config.json
│   └── eval-01 … eval-09.yaml
│
└── examples/
    ├── uk-lv-switchgear/
    ├── intl-mv-substation/
    └── us-pv-with-dcfc/

shared/calculations/electrical/
└── arc-flash-incident-energy.json       (NEW — calc contract for calc.arc_flash_incident_energy)
```

**Total: 49 files** (48 in `electrical/arc-flash/` + 1 calc contract under `shared/`).

**Standards layer references (manifest): 36 specific files**, 0 folders. All 36 already on disk from Phase A. Zero new standards files.

---

## 3. Data Flow

### 3.1 Inputs (hybrid mode)

**Consumed from upstream intents (preferred):**

| Source intent | Fields used | If absent |
|---|---|---|
| `fault-level` | Per-node: `ifault_ka_max`, `ifault_ka_min`, `ipk_ka`, `x_over_r_ratio`, `z_total_ohm`, `node_id`, `node_kind` | Engineer declares per-node Ifault (BLOCKING if missing — cannot compute incident energy) |
| `db-layout-rollup` | Per-board / per-circuit: `equipment_type` (drives electrode_config inference + label requirement), `ocpd_type` (drives t_clear default), `voltage_v`, `phases`, `location` | Engineer declares per-node |

**Always engineer-declared (no upstream source):**

- `t_clear_s` per node — OCPD clearing time at predicted I_arc; defaults from `rules/t-clear-defaults.yaml`
- `working_distance_mm` per node — defaults from Phase A `working-distance-defaults.json`
- `current_type` per node — `ac` (default) | `dc` (PV/battery/DCFC); auto-inferred if equipment_type matches
- `electrode_config` override (optional)

### 3.2 IR shape — project-scoped cascade tree

Each cascade node carries:

```json
{
  "node_id": "MSB-1.F03.DB-L1",
  "parent_node_id": "MSB-1.F03",
  "node_kind": "sub_feeder",
  "designation": "DB-L1 incoming sub-feeder",
  "equipment": {
    "type": "LV panelboard",
    "current_type": "ac",
    "voltage_v": 400,
    "voltage_class": "600V",
    "electrode_config": "VCB",
    "electrode_config_source": "auto_inferred_from_equipment_type"
  },
  "fault_inputs": {
    "ibf_ka_max": 22.5,
    "ibf_ka_min": 20.4,
    "x_over_r": 7
  },
  "ocpd_inputs": {
    "ocpd_type": "MCCB_thermal_magnetic",
    "t_clear_s": 0.2,
    "t_clear_source": "engineer_declared"
  },
  "geometry": {
    "working_distance_mm": 455,
    "gap_distance_mm": 32,
    "enclosure_volume_mm3": 318000000
  },
  "arc_flash": {
    "method_applied": "ieee1584_2018",
    "method_fallback_trail": [
      {"method": "ieee1584_2018", "result": "applied", "reason": "coefficients available"}
    ],
    "arcing_current_a": 21500,
    "incident_energy_cal_per_cm2": 6.4,
    "arc_flash_boundary_mm": 1280,
    "ppe_category": 2,
    "ppe_category_source": "computed_from_E"
  },
  "shock_approach": {
    "limited_approach_movable_mm": 3050,
    "limited_approach_fixed_mm": 1070,
    "restricted_approach_mm": 305,
    "source": "NFPA 70E:2024 Table 130.4(C)(a) — 151V to 750V row"
  },
  "label": {
    "label_recommended": true,
    "label_required_per": "NFPA 70E §130.5(H) — LV panelboard ≥240V",
    "engineer_can_skip_with_reason": false
  },
  "checks": {
    "incident_energy_finite": true,
    "boundary_ge_working_distance": true,
    "tool_call_pending": false
  }
}
```

### 3.3 Output intent (`arc-flash`)

Slim downstream subset (~14 required fields per node) consumed by future `electrical/arc-flash-labelling` skill. Forward-compatible with the labelling consumer's anticipated `consumed_intent` shape.

### 3.4 New calc contract — `calc.arc_flash_incident_energy`

Contract at `shared/calculations/electrical/arc-flash-incident-energy.json`. Defines:

- Inputs: `method` (enum incl. `auto`), `current_type`, `voltage_v`, `bolted_fault_current_a`, `gap_mm`, `working_distance_mm`, `arcing_time_s`, `electrode_config`, `enclosure_volume_mm3`, `equipment_type`
- Outputs: `arcing_current_a`, `incident_energy_cal_per_cm2`, `arc_flash_boundary_mm`, `applied_method`, `method_fallback_trail`, `voltage_class_used`, `ppe_category_suggestion`
- References: 10 specific Phase A standards files

Same WI3 deferral pattern — every node carries `tool_call_pending: true` until DraftsMan runtime ships.

---

## 4. Method Fallback Algorithm

### 4.1 Per-node method selection (encoded in `rules/method-fallback-chain.yaml`)

```
If current_type == "dc":
  If voltage_v <= 1000: method = "dc_doan"
  Else: method = "pending"

Else (AC):
  If IEEE 1584:2018 coefficients available for (voltage_class, electrode_config):
    method = "ieee1584_2018"
  Elif IEEE 1584:2002 Doughty/Neal coefficients transcribed:
    method = "ieee1584_2002"
  Elif Lee 1982 applicable (50 V ≤ V ≤ 15 kV, t_clear ≤ 5 s):
    method = "lee_1982"
  Elif equipment_type matches NFPA 70E table-method row:
    method = "nfpa70e_table"  (returns PPE category, no IE/AFB)
  Else:
    method = "pending"
```

### 4.2 What each method produces

| Method | IE | AFB | PPE | Notes |
|---|---|---|---|---|
| ieee1584_2018 | Number | Number | From IE | Best |
| ieee1584_2002 | Number | Number | From IE | Legacy + fallback |
| lee_1982 | Number (upper bound) | Number (conservative) | From IE | Always available |
| nfpa70e_table | `null` | `null` | Direct lookup | No IE; category only |
| dc_doan | Number | Number | From IE | DC only |
| pending | `null` | `null` | `null` | tool_call_pending |

### 4.3 method_fallback_trail

Every node records every method attempted with reason. Example:

```json
"method_fallback_trail": [
  {"method": "ieee1584_2018", "result": "skipped", "reason": "coefficients pending-verification for VCB 600V"},
  {"method": "ieee1584_2002", "result": "skipped", "reason": "Doughty/Neal coefficients also pending"},
  {"method": "lee_1982", "result": "applied", "reason": "theoretical formula; v_nom 480V within range"}
],
"method_applied": "lee_1982"
```

The fallback trail is auditable by the reviewer (D2) and surfaced in the rationale.

---

## 5. Engineering Checks per Node

### 5.1 Electrode-config auto-inference

`rules/electrode-config-inference.yaml` maps `equipment_type` strings via Phase A `equipment-classification.json`:

- "metal-clad switchgear" / "LV panelboard" / "MCC" → VCB
- "switchgear with arc-resistant barrier" → VCBB
- "drawout breaker" / "racked switchgear" → HCB
- "overhead service drop" / "open-bus" → VOA
- "substation bus" / "riser bus" → HOA
- Fallback: VCB
- Engineer override allowed; recorded as `electrode_config_source: engineer_override`

### 5.2 t_clear sourcing (OCPD-type defaults)

`rules/t-clear-defaults.yaml`:

| OCPD type | Default t_clear (s) |
|---|---|
| Instantaneous magnetic-only MCB | 0.05 |
| MCB Type B/C/D | 0.10 |
| MCCB thermal-magnetic | 0.20 |
| MCCB electronic LSI | 0.10 |
| ACB electronic | 0.30 |
| ACB with intentional delay | 0.50 |
| HV current-limiting fuse | 0.05 |
| LV general-purpose fuse | 0.20 |
| No curve data available | 2.0 (conservative) |

Priority: engineer-declared > ocpd-type default > 2.0s conservative. The IR's `t_clear_source` field records which path resolved the value.

### 5.3 Shock-approach boundaries (always bundled)

Every node looks up Limited + Restricted approach distances from `NFPA70E/table-130-4-C-a-AC-approach.json` (AC) or `table-130-4-C-b-DC-approach.json` (DC). Pure table lookup keyed on voltage class.

### 5.4 Label-required check

`rules/label-required-equipment.yaml` sets `label.label_recommended` per NFPA 70E §130.5(H):

- True for: switchgear, switchboards, panelboards, MCCs, industrial control panels, meter sockets ≥240V
- False for: single-family residential service, equipment <240V where no examination work performed
- Engineer override requires explicit justification (auditable)

### 5.5 Constraint checks (encoded in `constraints/*.yaml`)

| File | Check | Severity |
|---|---|---|
| `incident-energy-finite.yaml` | When method ≠ pending AND method ≠ nfpa70e_table: IE is finite positive | Error |
| `boundary-distance-physical.yaml` | AFB ≥ working_distance; AFB = working_distance when E = 1.2 | Error |
| `ppe-category-monotonic.yaml` | If IE_a < IE_b, then PPE_a ≤ PPE_b across all cascade nodes | Error |
| `method-fallback-consistency.yaml` | method_applied = last "applied" entry in method_fallback_trail | Error |

### 5.6 Non-compliance flags

| Flag code | Trigger | Severity |
|---|---|---|
| `ARC_FLASH_PENDING` | Any node has method_applied = pending | Warning |
| `LEE_1982_FALLBACK_USED` | Any node fell back to Lee 1982 | Info |
| `NFPA70E_TABLE_METHOD_USED` | Any node fell back to table method | Info |
| `INCIDENT_ENERGY_GT_40_RESTRICTED` | Any node has IE > 40 cal/cm² | Error |
| `CONSERVATIVE_T_CLEAR_DEFAULT_USED` | Any node uses 2.0s conservative default | Warning |
| `SHOCK_APPROACH_BEYOND_TABLE_RANGE` | Voltage > 46 kV (out of Table 130.4 range) | Error |

---

## 6. Prompts

### 6.1 Generator — 14-step chain

1. Ingest fault-level intent → per-node fault data
2. Ingest db-layout-rollup intent → equipment + OCPD data
3. Determine jurisdiction → regulatory framing
4. Build cascade tree (node_id paths from fault-level)
5. Per-node: auto-infer current_type (ac default; dc from equipment matches)
6. Per-node: auto-infer electrode_config (VCB/VCBB/HCB/VOA/HOA) + engineer override
7. Per-node: determine t_clear_s (engineer > ocpd_type default > 2.0s)
8. Per-node: select method via fallback chain; record method_fallback_trail
9. Per-node: call calc.arc_flash_incident_energy → IE, AFB, arc current
10. Per-node: lookup shock-approach distances (limited movable + fixed + restricted)
11. Per-node: PPE category from Table 130.7(C)(15)(c) (or table method lookup)
12. Per-node: evaluate label_recommended per §130.5(H)
13. Run all 4 constraints; emit non_compliance_flags[]
14. Emit arc-flash intent + assemble 8-section rationale block

### 6.2 Validator — 10 INV invariants

| INV | Statement |
|---|---|
| INV-01 | Valid node_id pattern; parent_node_id resolves |
| INV-02 | current_type is ac or dc |
| INV-03 | AC nodes have electrode_config from VCB/VCBB/HCB/VOA/HOA; DC nodes have none |
| INV-04 | method_applied from controlled vocabulary |
| INV-05 | method_applied = last "applied" in method_fallback_trail |
| INV-06 | When method ≠ pending AND ≠ nfpa70e_table: IE finite positive, AFB ≥ working_distance |
| INV-07 | PPE category 1/2/3/4 OR null; thresholds match Table 130.7(C)(15)(c) |
| INV-08 | shock_approach block has all 3 distances from appropriate Table 130.4(C)(a/b) |
| INV-09 | DC nodes use dc_doan OR pending (no AC method) |
| INV-10 | Emitted intent matches schema; 1-to-1 with cascade nodes |

### 6.3 Reviewer — 8 D dimensions

| D | Dimension |
|---|---|
| D1 | Standards citations specific per node |
| D2 | method_fallback_trail auditable (skipped reasons named; applied is last) |
| D3 | Conservative-fallback warnings present when Lee 1982 or nfpa70e_table fired |
| D4 | Per-node AFB arithmetic spot-check (±2%) |
| D5 | PPE category thresholds match Table 130.7(C)(15)(c) for each IE |
| D6 | shock_approach lookups consistent with Table 130.4 rows + current_type |
| D7 | DC nodes use Doan + Stokes & Oppenlander; no electrode_config on DC |
| D8 | Rationale: 8 sections per WI2; chat_summary ≤ 200 words; citations present |

---

## 7. Evals + Examples

### 7.1 Eval coverage (9 evals)

| Eval ID | Category | What it tests |
|---|---|---|
| eval-01-uk-lv-switchboard-happy-path | happy_path | 400V UK commercial; ieee1584_2018 fires |
| eval-02-mv-cascade-with-drawout | edge_case | 11kV MV + LV cascade; HCB drawout; voltage-class crossing |
| eval-03-coefficient-fallback-trap | validation_trap | 2018 coefficients null → Lee 1982 fallback; flag emitted |
| eval-04-missing-fault-data | missing_input | No fault-level intent → tool_call_pending; no invented Ifault |
| eval-05-jurisdiction-us-with-restricted | jurisdiction_switch | 480V US industrial; one node IE > 40; RESTRICTED flag |
| eval-06-rationale-block | rationale_block | 8 sections + chat_summary + citations |
| eval-07-dc-pv-string | skill_specific | 600V DC PV combiner; dc_doan method |
| eval-08-conservative-t-clear-default | skill_specific | No ocpd_type → 2.0s default → warning flag |
| eval-09-shock-approach-out-of-range | skill_specific | 36 kV (in-range) vs 47 kV (out-of-range → error flag) |

All 6 WI5 categories + 3 skill-specific.

### 7.2 Worked examples (3)

| Example | Demonstrates |
|---|---|
| `uk-lv-switchgear/` | 11kV/400V UK office; 1600 kVA TX + MSB + DB-L1; ieee1584_2018 path |
| `intl-mv-substation/` | 11kV → 400V industrial substation; HCB at MV + VCB at LV; voltage-class crossing |
| `us-pv-with-dcfc/` | 12.47kV/480V industrial with DC PV strings + DCFC; unified cascade with ac + dc nodes |

Each example: `input.json` + `output.json` + `intent-out.json` + `reasoning.md`.

---

## 8. Cross-Skill Contracts + Manifest

### 8.1 Manifest

References 36 specific standards files (22 IEEE1584 + 14 NFPA70E) + 1 new calc contract. All 36 already on disk from Phase A.

### 8.2 Cross-skill intent contracts

| Direction | Intent | Purpose |
|---|---|---|
| Consumes | `fault-level` | Per-node Ifault + ipk + X/R |
| Consumes | `db-layout-rollup` | Per-node equipment_type + ocpd_type |
| Produces | `arc-flash` | Per-node IE + AFB + PPE + shock-approach → consumed by future `electrical/arc-flash-labelling` |

### 8.3 Phase A pending-verification coefficients — graceful handling

17 IEEE 1584 coefficient files in the Phase A layer carry null values pending transcription from a paid copy of IEEE 1584:2018.

The skill handles this gracefully via the fallback chain: when 2018 coefficients are null, automatically demote to Lee 1982 (or NFPA 70E table method). User gets useful output instead of null. When coefficients are eventually transcribed in a future micro-sprint, the skill auto-promotes to `ieee1584_2018` without code changes.

### 8.4 Versioning policy

- Minor bumps (1.x.0): new jurisdictions, new evals, DC > 1000V support
- Major bump (2.0.0): breaking IR schema change OR IEEE 1584:2028 adoption
- Patch bumps (1.0.x): rules/constraints/validation fixes

---

## 9. Sprint sequence (locked in)

| Sprint | Content | Status |
|---|---|---|
| Previous | Phase A — IEEE 1584 + NFPA 70E standards layers | ✅ Shipped |
| **This sprint** | **Phase B — `electrical/arc-flash` skill** | **In progress** |
| Next | clause_ref retrofit (93 pre-existing files, ~1.5 hr micro-sprint) | Queued |
| After | `electrical/arc-flash-labelling` + ANSI Z535.4 promotion | Stub committed for roadmap visibility (commit `711ebd5`) |
| Then | Continue Path B: earthing v1.1 + db-layout v1.1 | Queued |

---

## 10. Approval

All 8 design sections approved by user 2026-05-17. Ready for implementation plan.

**Sprint scope summary:** 49 files (48 in `electrical/arc-flash/` + 1 calc contract in `shared/calculations/electrical/`). Zero new standards files (all 36 already shipped in Phase A). Uses the proven artefact pattern (`earthing` / `db-layout` / `fault-level` / `cable-sizing`).

Next step: invoke `superpowers:writing-plans` to produce `docs/superpowers/plans/2026-05-17-arc-flash-skill.md`.
