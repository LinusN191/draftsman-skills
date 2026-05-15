# Earthing Skill — Design Spec (Stage 1: Schematic)

**Date:** 2026-05-15
**Status:** Approved
**Scope:** Build `electrical/earthing` as a production-grade vertical-slice skill that proves the standards-consumption pattern. Stage 1 produces an earthing single-line schematic IR; stage 2 (plan-view) and stage 3 (declaration-only) are deferred.

---

## 1. Goal

Populate `electrical/earthing/` with a complete skill artefact set so that:

1. **The consumption pattern is proven.** The generator prompt names specific files from BS 7671, IEC 60364, NFPA 70, and IEC 60617 layers — not folders. The runtime fetches only the named files. This is the first real test of the architecture documented in our recent pace-discussion.
2. **The IR contract is exercised.** The skill produces an `earthing-ir.json` validating against a new `earthing-ir.schema.json`, plus a separate stable `earthing-intent.json` per the WI4 cross-drawing contract.
3. **The upstream work items integrate.** The skill exercises WI1 (inputs.json), WI2 (rationale block in IR), WI3 (calculation executor declarations — declared tool-calls for iterative calcs), WI4 (intent envelope), and WI5 (eval standardisation).
4. **The lighting-layout pattern is replicable.** The artefact set matches `electrical/lighting-layout/` exactly so the result is a 1:1 template for the remaining 79 stub skills.

This is the **first end-to-end skill that bridges from authored standards to running engineering output.** Before this slice, all skill prompts referenced standards loosely or by folder. This slice nails the contract.

---

## 2. Decisions Made

| Decision | Choice | Rationale |
|---|---|---|
| Output type | Earthing single-line schematic | One drawing type, manageable in 3 sessions, touches all 4 standards layers |
| Sequencing | Stage 1 (schematic) only | Plan-view (stage 2) and declaration (stage 3) deferred. Same end state, faster first checkpoint. |
| Earthing systems | TN-C-S + TT only | ~85% of real designs. Adds breadth without exploding scope. TN-S + IT deferred. |
| Jurisdictions | GB (BS 7671), EU/INT (IEC 60364), US (NFPA 70) | Drawn from `inputs.jurisdiction`; selects which standards files the prompt loads |
| Computation depth | Hybrid: inline lookups + declared tool calls | Closed-form table lookups inline (LLM-safe); iterative calcs (electrode resistance) declared as tool-calls per WI3 — `tool_call_pending` flag until runtime tool exists |
| Cross-drawing consumption | Full triple: db-layout + lighting-layout + small-power | Matches WI4 spec exactly. Proves the consumer side of the cross-drawing contract. |
| Cross-drawing production | `produces_intent: "earthing"` | Per WI4. Sized for downstream cable-containment / riser / panel-schedule consumption. |
| Artefact pattern | Match `electrical/lighting-layout/` exactly | True production-grade pattern, transferable to remaining 79 stubs |
| File count | ~35 files | Higher than initially scoped (~25) because examples are 3 files each not 1 |

---

## 3. Current State

| File | Status |
|---|---|
| `electrical/earthing/README.md` | Stub — must be rewritten |
| `electrical/earthing/skill.manifest.json` | Stub (status `stub`, empty inputs/outputs) — must be rewritten |
| `electrical/earthing/{docs,evals,examples,prompts}/` | Empty placeholder folders |

Everything else must be created from scratch.

---

## 4. Architecture (the consumption pattern)

```
User input ──→ skill.manifest.json (loads inputs.json + generator.md)
                            │
                            ▼
                 prompts/generator.md
                            │
       ┌────────────────────┼────────────────────┐
       ▼ (jurisdiction-     ▼ (always)           ▼ (always)
        gated)
   IF GB:                 IEC 60617:            cross_drawing_context:
   - BS7671/                symbol-index.json     db-layout intent
     reg411-disc...json     part2-general.json    lighting-layout intent
     reg411-rcd-req.json                          small-power intent
   IF EU / INT:           
   - IEC60364/             
     part4-41.json           
     part5-54-earthing.json
   IF US:
   - NFPA70/
     art250-grounding-bonding.json
     grounding-and-bonding.json
                            │
                            ▼
                Skill produces earthing-ir.json
                            │
                ┌───────────┴───────────┐
                ▼                       ▼
        Runtime validates       Runtime renders DXF
        against schema          using IEC 60617 symbols
                            │
                            ▼
                Skill also produces earthing-intent.json
                (stable subset for downstream skills)
```

**Three structural inputs the prompt selectively loads** (proving the consumption pattern):

| Always loaded | Jurisdiction-gated | On demand |
|---|---|---|
| `IEC60617/symbol-index.json` (the few-KB index, not full symbol files) | `BS7671/` files (UK projects) | Full per-symbol files when geometry needed |
| `IEC60617/part2-general.json` (only file with earth/PE symbols) | `IEC60364/` files (international/EU) | Standards Annex/Table contents |
| `inputs.json` | `NFPA70/` files (US) | |
| `cross_drawing_context` intent payloads | | |

**Cross-drawing intents:**

- **Consumes:** db-layout, lighting-layout, small-power → for breaker ratings, circuit IDs, route lengths, voltage class
- **Produces:** earthing-intent → for downstream cable-containment, riser, schematic, panel-schedule, sld skills

**No drawing geometry in this slice.** Schematic-only. The IR carries logical topology (supply → MET → bonding → electrode → CPC routes) but no x/y coordinates. The runtime can render a basic single-line from the topology + symbol library; refined drawing geometry is plan-view-skill scope (stage 2).

---

## 5. File Set — ~35 files

Matches the `electrical/lighting-layout/` artefact pattern.

### 5.1 Skill-level (4)

| File | Content |
|---|---|
| `skill.manifest.json` | Manifest: status `beta`, full inputs at `inputs_path`, `standards` (per-file paths — not folders — the consumption-pattern proof), `produces_intent: "earthing"`, `consumes_intents: ["db-layout", "lighting-layout", "small-power"]`, `output_schema`, evals/examples lists, validators list |
| `README.md` | Layer index + standards consumption diagram |
| `CHANGELOG.md` | v1.0.0 entry — schematic vertical slice |
| `inputs.json` | ~18 items per WI1 schema: jurisdiction, earthing_system, supply_voltage_v, supply_phase, ze_ohm_declared, dno_pscc_ka, building_type, has_lightning_protection, extraneous_parts (struct_list), ground_conditions, electrode_count_planned, electrode_type_planned, target_ra_ohm, db_designations (struct_list), met_location, supplementary_bonding_required_locations |

### 5.2 Prompts (3)

| File | Content |
|---|---|
| `prompts/generator.md` | 12-step reasoning chain — see Section 6 |
| `prompts/validator.md` | Post-generation IR cross-check |
| `prompts/reviewer.md` | Rationale-block review |

### 5.3 Schemas (2)

| File | Content |
|---|---|
| `schemas/earthing-ir.schema.json` | Full IR — see Section 7 |
| `schemas/earthing-intent.schema.json` | Stable subset for downstream — see Section 8 |

### 5.4 Rules + Constraints (4)

| File | Content |
|---|---|
| `rules/electrode-selection.yaml` | When to use rod / plate / mat / Ufer / ground-ring; depth and length defaults |
| `rules/cpc-sizing.yaml` | Jurisdiction-gated CPC/EGC sizing rules |
| `constraints/electrode-resistance.yaml` | Target Ra by earthing system + jurisdiction: TT GB (≤200 Ω typical), TT EU (per IEC 60364-5-54), TT US (≤25 Ω per NEC 250.53(A)(2) or second electrode) |
| `constraints/bonding-geometry.yaml` | Min CSA + max length for main protective bonding conductors |

### 5.5 Validation (3)

| File | Content |
|---|---|
| `validation/zs-compliance.yaml` | `ir.circuits[*].zs_ohm ≤ zs_max_ohm` for ADS |
| `validation/bonding-completeness.yaml` | Every entry in `inputs.extraneous_parts` appears in `ir.main_bonding[]` OR has explicit waiver |
| `validation/cpc-sizing.yaml` | `cpc_csa_mm2` meets the per-jurisdiction sizing table |

### 5.6 Evals (7 = 6 evals + runner config, per WI5)

| File | Category | Content |
|---|---|---|
| `evals/runner-config.json` | — | `minimum_status_evals`: production 5 / beta 3 / draft 1; `minimum_model_class: sonnet_or_better`; `production_block_on_failure: true` |
| `evals/eval-01-tn-cs-uk-happy-path.yaml` | happy_path | UK dwelling TN-C-S, water + gas bonding |
| `evals/eval-02-tt-international.yaml` | edge_case | International TT with rod electrode |
| `evals/eval-03-us-nec-art250.yaml` | edge_case | US commercial NEC Art 250 with Ufer + rod |
| `evals/eval-04-zs-too-high-non-compliance.yaml` | compliance_failure | Long cable forcing Zs > Zs_max |
| `evals/eval-05-cross-drawing-context.yaml` | cross_validation | 3 sibling intents present; verify earthing covers all circuit_ids |
| `evals/eval-06-rationale-block.yaml` | skill_specific | Asserts rationale schema compliance + mandatory section titles |

### 5.7 Examples (9 = 3 folders × 3 files)

| Folder | Scenario |
|---|---|
| `examples/uk-dwelling-tn-cs/{input.json, reasoning.md, output.json}` | Standard UK domestic TN-C-S, 100 A service |
| `examples/intl-rural-tt/{input.json, reasoning.md, output.json}` | International rural building, no PME, TT with rod array |
| `examples/us-commercial-nec/{input.json, reasoning.md, output.json}` | US commercial 200 A per NEC Art 250 |

### 5.8 Ontology + Docs (3)

| File | Content |
|---|---|
| `ontology/earthing-system-types.json` | TN-C-S / TT definitions with jurisdiction-mapping |
| `docs/engineering-philosophy.md` | When to use which earthing system; conservative defaults |
| `docs/known-limitations.md` | Stage-1 scope: schematic only; no plan-view; no IT; tool execution deferred |

**Total: 35 files** (4 skill + 3 prompts + 2 schemas + 4 rules/constraints + 3 validation + 7 evals + 9 examples + 3 ontology/docs).

---

## 6. Generator Prompt — 12-Step Reasoning Chain

**Step 1 — Discovery check.** If sibling intents are in `cross_drawing_context`, extract; if missing, flag in `rationale.flags`.

**Step 2 — Jurisdiction-gated standards file load.** Based on `inputs.jurisdiction`:
- `GB` → `BS7671/reg411-disconnection-times.json` + `reg411-rcd-requirements.json` + `terminology.md`
- `EU` / `INT` → `IEC60364/part4-41-electric-shock.json` + `part5-54-earthing.json` + `earthing-systems.md`
- `US` → `NFPA70/art250-grounding-bonding.json` + `grounding-and-bonding.json` (cross-cutting) + `terminology.md`
- Always: `IEC60617/symbol-index.json` + `IEC60617/part2-general.json`

This step is the consumption-pattern proof — the prompt names specific files.

**Step 3 — Earthing-system classification.** From `inputs.earthing_system`. State system in `ir.earthing_system`. Annotate jurisdictional terminology equivalent.

**Step 4 — Main earthing terminal (MET).** Locate per `inputs.met_location`. Conductor route from supply. For TN-C-S: N-PE bond at supply (DNO side per BS 7671 Reg 542.1 / NEC 250.142). For TT: MET bonded only to consumer electrode.

**Step 5 — Earth electrode arrangement.** Specify count, type, dimensions. Compute Ra per BS 7430 / IEC 60364-5-54 / NEC 250.53. Declare `tool_call` to `calc.electrode_resistance` per WI3; until tool exists, take engineer-input Ra and emit `tool_call_pending: true`.

**Step 6 — Main protective bonding.** Bond all `inputs.extraneous_parts`. Conductor sizes:
- `GB`: BS 7671 Reg 544.1.1
- `EU`/`INT`: IEC 60364-5-54 Clause 544 (1/2 × CSA of largest PE up to 25 mm²)
- `US`: NEC 250.66 table

**Step 7 — Supplementary bonding.** For bathroom (BS 7671 Section 701 / IEC 60364-7-701) and pool (Section 702 / 60364-7-702 / NEC 680.26) zones.

**Step 8 — CPC sizing per circuit.** For each circuit in `cross_drawing_context.db_layout.circuits[]`:
- `GB`: BS 7671 Table 54.7 (adiabatic) or by line CSA alternative
- `EU`/`INT`: IEC 60364-5-54 Table 54.1
- `US`: NEC Table 250.122 (by OCPD rating)
- Inline lookup (closed-form, LLM-safe). Record `cpc_csa_mm2_or_awg` + `cpc_sizing_clause`.

**Step 9 — Zs verification.** For each circuit: Zs = Ze + R1+R2 over circuit length. Compare against `Zs_max` from Table 41.1/41.3 (GB) or equivalent (EU/US). Flag if `Zs > Zs_max`.

**Step 10 — RCD requirement check.** TT: all final circuits require 30 mA RCD. TN-C-S: per jurisdiction rules (BS 7671 Reg 411.3.3 for sockets ≤32 A, mobile equipment, bathroom).

**Step 11 — Compliance flag emission.** Roll up `compliance_summary.compliant` (bool) + `non_compliance_flags[]` with code clause references.

**Step 12 — Emit rationale block** (per WI2). Required sections: Earthing System, Electrodes, Main Bonding, Supplementary Bonding (if any), CPC + Zs Verification, RCD Requirements, Compliance, Assumptions.

---

## 7. IR Schema (`earthing-ir.schema.json`)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "shared/schemas/electrical/earthing-ir.schema.json",
  "type": "object",
  "required": [
    "drawing_type", "version", "meta",
    "jurisdiction", "earthing_system",
    "met", "electrodes", "main_bonding",
    "circuits", "compliance_summary",
    "rationale"
  ],
  "properties": {
    "drawing_type": { "const": "earthing_schematic" },
    "version":      { "type": "string" },
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
            "properties": {
              "intent_type":    { "type": "string" },
              "intent_version": { "type": "string" },
              "produced_by":    { "type": "string" }
            }
          }
        }
      }
    },
    "jurisdiction":    { "enum": ["GB", "EU", "INT", "US"] },
    "earthing_system": {
      "type": "object",
      "required": ["system_type", "code_clause"],
      "properties": {
        "system_type": { "enum": ["TN-C-S", "TT"] },
        "code_clause": { "type": "string" }
      }
    },
    "met": {
      "type": "object",
      "required": ["location", "supply_bond_type"],
      "properties": {
        "location":                          { "type": "string" },
        "supply_bond_type":                  { "enum": ["dno_pme_bond", "consumer_electrode_only", "tn_s_separate_pe"] },
        "main_earthing_conductor_csa_mm2":   { "type": "number" },
        "main_earthing_conductor_size_awg":  { "type": "string" }
      }
    },
    "electrodes": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "electrode_type", "ra_ohm_specified"],
        "properties": {
          "id":                     { "type": "string" },
          "electrode_type":         { "enum": ["rod", "plate", "mat", "ufer", "ground_ring", "structural_metal"] },
          "length_mm":              { "type": "integer" },
          "diameter_mm":            { "type": "integer" },
          "burial_depth_mm":        { "type": "integer" },
          "soil_resistivity_ohm_m": { "type": "number" },
          "ra_ohm_specified":       { "type": "number" },
          "ra_ohm_calculated":      { "type": "number" },
          "tool_call_pending":      { "type": "boolean" }
        }
      }
    },
    "main_bonding": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "source", "target", "csa_mm2_or_awg", "code_clause"],
        "properties": {
          "id":              { "type": "string" },
          "source":          { "type": "string" },
          "target":          { "type": "string" },
          "csa_mm2_or_awg":  { "type": "string" },
          "code_clause":     { "type": "string" }
        }
      }
    },
    "supplementary_bonding": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["location", "items_bonded", "csa_mm2_or_awg"],
        "properties": {
          "location":       { "enum": ["bathroom", "pool", "kitchen_commercial", "medical_group_2", "other"] },
          "items_bonded":   { "type": "array", "items": { "type": "string" } },
          "csa_mm2_or_awg": { "type": "string" },
          "code_clause":    { "type": "string" }
        }
      }
    },
    "circuits": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["circuit_id", "cpc_csa_mm2_or_awg", "zs_compliance"],
        "properties": {
          "circuit_id":           { "type": "string" },
          "db_designation":       { "type": "string" },
          "voltage_class":        { "type": "string" },
          "breaker_rating_a":     { "type": "integer" },
          "breaker_curve":        { "enum": ["B", "C", "D"] },
          "route_length_m":       { "type": "number" },
          "cpc_csa_mm2_or_awg":   { "type": "string" },
          "cpc_sizing_method":    { "enum": ["table_lookup", "adiabatic", "tool_call_pending"] },
          "cpc_sizing_clause":    { "type": "string" },
          "zs_ohm":               { "type": "number" },
          "zs_max_ohm":           { "type": "number" },
          "zs_compliance":        { "enum": ["pass", "fail_needs_rcd", "fail_oversize_cpc", "pass_with_rcd"] },
          "rcd_required":         { "type": "boolean" },
          "rcd_type":             { "enum": ["AC", "A", "F", "B"] },
          "rcd_sensitivity_ma":   { "type": "integer", "enum": [10, 30, 100, 300, 500] }
        }
      }
    },
    "compliance_summary": {
      "type": "object",
      "required": ["compliant", "non_compliance_flags", "assumptions"],
      "properties": {
        "compliant":              { "type": "boolean" },
        "non_compliance_flags": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["message"],
            "properties": {
              "message":     { "type": "string" },
              "code_clause": { "type": "string" },
              "severity":    { "enum": ["critical", "warning", "info"] }
            }
          }
        },
        "assumptions":            { "type": "array", "items": { "type": "string" } }
      }
    },
    "drawing_notes":     { "type": "array", "items": { "type": "string" } },
    "drawn_as_symbols":  { "type": "array", "items": { "type": "string" } },
    "flags":             { "type": "array", "items": { "type": "string" } },
    "rationale":         { "$ref": "../core/rationale.schema.json" }
  }
}
```

**Notable design choices:**

- `tool_call_pending` flag — explicit signal that an iterative calc is declared but not yet executed.
- `cpc_sizing_method` field — declares whether the value came from table lookup, adiabatic, or pending tool call. Makes the consumption pattern auditable.
- `drawn_as_symbols` is a roll-up array — every symbol ID must resolve in `IEC60617/symbol-index.json` (eval asserts).
- `rationale` `$ref`s `shared/schemas/core/rationale.schema.json` (WI2).
- `meta.consumed_intents` records sibling intents consumed at production time with versions (WI4 auditability).

---

## 8. Intent Schema (`earthing-intent.schema.json`)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "electrical/earthing/schemas/earthing-intent.schema.json",
  "title": "Earthing Intent",
  "description": "Stable subset of the earthing IR consumed by cable-containment, riser, schematic, panel-schedule, sld skills. Wrapped at runtime in shared/schemas/core/intent.schema.json.",
  "type": "object",
  "required": [
    "jurisdiction",
    "earthing_system",
    "met_location",
    "available_zs_at_main_db_ohm",
    "electrode_target_met",
    "circuits"
  ],
  "additionalProperties": false,
  "properties": {
    "jurisdiction":                 { "enum": ["GB", "EU", "INT", "US"] },
    "earthing_system":              { "enum": ["TN-C-S", "TT"] },
    "met_location":                 { "type": "string" },
    "available_zs_at_main_db_ohm":  { "type": "number", "minimum": 0 },
    "electrode_target_met":         { "type": "boolean" },
    "supplementary_bonding_locations": {
      "type": "array",
      "items": { "enum": ["bathroom", "pool", "kitchen_commercial", "medical_group_2", "other"] }
    },
    "rcd_protected_circuit_ids": {
      "type": "array",
      "items": { "type": "string" }
    },
    "circuits": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["circuit_id", "cpc_csa_mm2_or_awg", "zs_compliance"],
        "additionalProperties": false,
        "properties": {
          "circuit_id":         { "type": "string" },
          "cpc_csa_mm2_or_awg": { "type": "string" },
          "zs_compliance":      { "enum": ["pass", "fail_needs_rcd", "fail_oversize_cpc", "pass_with_rcd"] },
          "rcd_required":       { "type": "boolean" },
          "rcd_type":           { "enum": ["AC", "A", "F", "B"] },
          "rcd_sensitivity_ma": { "type": "integer", "enum": [10, 30, 100, 300, 500] }
        }
      }
    },
    "life_safety_bonded_assets": {
      "type": "array",
      "items": { "type": "string" }
    },
    "compliance_summary": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "compliant":                 { "type": "boolean" },
        "non_compliance_flag_count": { "type": "integer", "minimum": 0 }
      }
    }
  }
}
```

**Why a separate intent vs full IR?** The full IR is ~150–300 lines per project. Downstream skills need <30 fields. Forward-compat rules per WI4:
- Optional field added → minor `intent_version` bump
- Required field added → major bump
- Required field removed/renamed → major bump only

---

## 9. Evals (6 covering all WI5 categories)

| # | Name | Category | Scenario |
|---|---|---|---|
| 01 | tn-cs-uk-happy-path | happy_path | UK dwelling, TN-C-S, water + gas bonding, simple circuit list |
| 02 | tt-international | edge_case | International TT, single rod electrode, Ra = 180 Ω |
| 03 | us-nec-art250 | edge_case | US commercial NEC Art 250, Ufer + ground rod + water-pipe bonding |
| 04 | zs-too-high-non-compliance | compliance_failure | Long cable forcing Zs > Zs_max; skill flags non-compliance |
| 05 | cross-drawing-context | cross_validation | All 3 sibling intents present; verify earthing covers all circuit_ids |
| 06 | rationale-block | skill_specific | Asserts rationale schema compliance + mandatory section titles |

**Runner config:** `minimum_status_evals` = {production: 5, beta: 3, draft: 1}; `minimum_model_class: sonnet_or_better`; `production_block_on_failure: true`.

---

## 10. Examples (3 — one per jurisdiction)

| Folder | Scenario | What it demonstrates |
|---|---|---|
| `uk-dwelling-tn-cs/` | UK domestic 100 A TN-C-S, kitchen + bathroom + 2 bedrooms | BS 7671 path: Reg 411/542/Table 54.7 + IEC 60617 symbols |
| `intl-rural-tt/` | International rural building, no PME, TT with rod array | IEC 60364 path: Part 4-41 + Part 5-54; RCD-mandatory pattern |
| `us-commercial-nec/` | US commercial 200 A per NEC Art 250 with Ufer + rod + water | NEC path: Art 250.50 + 250.66 + 250.122; jurisdiction switch in action |

Each example: `input.json` + `reasoning.md` + `output.json` (validates against IR schema).

---

## 11. Cross-references

### Out (this skill references)
- **Standards layers (5 paths):** `BS7671/reg411-*.json` + `IEC60364/part4-41 + part5-54.json` + `NFPA70/art250 + grounding-and-bonding.json` + `IEC60617/symbol-index + part2-general.json`
- **Core schemas:** `shared/schemas/core/rationale.schema.json` (WI2), `intent.schema.json` (WI4), `inputs.schema.json` (WI1), `eval.schema.json` (WI5), `calculation.schema.json` (WI3)
- **Calculation contracts:** `shared/calculations/electrical/electrode-resistance.json` (declared tool-call), `cpc-adiabatic.json` (declared tool-call)
- **Sibling intent schemas (consumed):** `electrical/db-layout/schemas/db-layout-intent.schema.json`, `electrical/lighting-layout/schemas/lighting-layout-intent.schema.json`; `electrical/small-power/schemas/small-power-intent.schema.json` (when authored — handled as absent intent if not present)

### In (anticipated consumers — no changes here)
- `electrical/cable-containment` — when authored, consumes earthing intent for separation rules
- `electrical/sld` — life-safety bonded assets surface on SLD
- `electrical/panel-schedule` — RCD requirement per circuit appears on schedule
- `electrical/riser` — available Zs at main DB drives riser cable sizing

---

## 12. Out of Scope

- Plan-view earthing layout (stage 2)
- Earthing specification / declaration-only mode (stage 3)
- IT (impedance-grounded) systems (medical Group 2, mining)
- TN-S system (older separate-PE-from-DNO)
- Lightning protection earthing (BS EN 62305 / NFPA 780 — separate discipline)
- Cathodic protection
- HV earthing
- Live runtime execution of `calc.electrode_resistance` (Python in DraftsMan-runtime repo; tool-call declared but `tool_call_pending: true`)
- DXF generation from IR (downstream renderer concern)

---

## 13. File Tree (final state)

```
electrical/earthing/
├── README.md                           ← rewrite
├── CHANGELOG.md                        ← new (v1.0.0)
├── skill.manifest.json                 ← rewrite (full taxonomy, status beta)
├── inputs.json                         ← new (per WI1)
│
├── prompts/
│   ├── generator.md                    ← new (12-step reasoning chain)
│   ├── validator.md                    ← new
│   └── reviewer.md                     ← new
│
├── schemas/
│   ├── earthing-ir.schema.json         ← new
│   └── earthing-intent.schema.json     ← new
│
├── rules/
│   ├── electrode-selection.yaml        ← new
│   └── cpc-sizing.yaml                 ← new
│
├── constraints/
│   ├── electrode-resistance.yaml       ← new
│   └── bonding-geometry.yaml           ← new
│
├── validation/
│   ├── zs-compliance.yaml              ← new
│   ├── bonding-completeness.yaml       ← new
│   └── cpc-sizing.yaml                 ← new
│
├── evals/
│   ├── runner-config.json              ← new (per WI5)
│   ├── eval-01-tn-cs-uk-happy-path.yaml
│   ├── eval-02-tt-international.yaml
│   ├── eval-03-us-nec-art250.yaml
│   ├── eval-04-zs-too-high-non-compliance.yaml
│   ├── eval-05-cross-drawing-context.yaml
│   └── eval-06-rationale-block.yaml
│
├── examples/
│   ├── uk-dwelling-tn-cs/{input.json, reasoning.md, output.json}
│   ├── intl-rural-tt/{input.json, reasoning.md, output.json}
│   └── us-commercial-nec/{input.json, reasoning.md, output.json}
│
├── ontology/
│   └── earthing-system-types.json      ← new
│
└── docs/
    ├── engineering-philosophy.md       ← new
    └── known-limitations.md            ← new
```

**Total: 35 files** (4 skill + 3 prompts + 2 schemas + 4 rules/constraints + 3 validation + 7 evals + 9 examples + 3 ontology/docs).

---

## 14. Layer Success Criteria

1. **Consumption-pattern proof:** generator prompt names ≥6 specific standards files by path (not folders); manifest's `standards` array also names files, not folders.
2. **Schema-valid IR:** all 3 example `output.json` files validate against `earthing-ir.schema.json`.
3. **Schema-valid intent:** all 3 examples also derive a valid `earthing-intent.json` (against `earthing-intent.schema.json`).
4. **Eval coverage:** all 6 evals conform to `shared/schemas/core/eval.schema.json`; all 5 required WI5 categories present.
5. **Symbol resolution:** every entry in `ir.drawn_as_symbols` resolves in `IEC60617/symbol-index.json`.
6. **Cross-jurisdiction switching:** the 3 examples produce demonstrably different IR content — different code clauses, different conductor units — proving the jurisdiction gate works.
7. **Stage 1 self-contained:** the slice can ship (commit + push) and DraftsMan-runtime work can build against the schemas before plan-view / declaration stages exist.
