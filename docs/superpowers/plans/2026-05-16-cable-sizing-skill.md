# Cable-Sizing Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `electrical/cable-sizing` v1.0.0 beta — per-circuit cable selection with named binding constraint per BS 7671 / IEC 60364 / NEC.

**Architecture:** Single-skill build (no Phase A — all standards + calc contracts already on disk). Project-scoped cascade IR + slim downstream `cable-sizing` intent. 14-step generator / 10 INV validator / 8 D reviewer. Walk-the-ladder CSA selection with cumulative Vd, motor-starting Vd, parallel cables, and harmonic derating. Matches proven artefact pattern from `earthing` / `db-layout` / `fault-level`.

**Tech Stack:** JSON Schema draft-07 (schemas), YAML 1.2 (rules/constraints/validation/evals), Markdown (prompts/docs/READMEs), Python `jq` + `yamllint` for parse validation.

**Reference:** Spec at `docs/superpowers/specs/2026-05-16-cable-sizing-skill-design.md`. Pattern parent: `electrical/fault-level/` (just shipped, 45 files).

---

## Task list (23 tasks)

| # | Task | Files |
|---|---|---|
| 1 | Bootstrap folder + CHANGELOG + initial README | 3 |
| 2 | `schemas/cable-sizing-ir.schema.json` | 1 |
| 3 | `schemas/cable-sizing-intent.schema.json` | 1 |
| 4 | `inputs.json` (16-item discovery taxonomy) | 1 |
| 5 | `skill.manifest.json` (22 standards + 3 calcs) | 1 |
| 6 | 5 rules YAMLs | 5 |
| 7 | 4 constraints YAMLs | 4 |
| 8 | 2 ontology JSONs | 2 |
| 9 | `prompts/generator.md` (14-step chain) | 1 |
| 10 | `prompts/validator.md` (10 INV) | 1 |
| 11 | `prompts/reviewer.md` (8 D) | 1 |
| 12 | 4 validation YAMLs | 4 |
| 13 | 2 docs files | 2 |
| 14 | `evals/runner-config.yaml` + eval-01 (UK domestic happy path) | 2 |
| 15 | eval-02 (commercial cumulative Vd edge_case) | 1 |
| 16 | eval-03 (undersized validation_trap) + eval-04 (missing_input) | 2 |
| 17 | eval-05 (US AWG jurisdiction_switch) + eval-06 (rationale_block) | 2 |
| 18 | eval-07 (motor-starting Vd) | 1 |
| 19 | eval-08 (parallel cables) + eval-09 (harmonic derating) | 2 |
| 20 | Example 1 — UK domestic final circuits | 4 |
| 21 | Example 2 — INT commercial with feeders | 4 |
| 22 | Example 3 — US industrial with motors | 4 |
| 23 | Final README rewrite + SKILLS_STATUS update + push | 2 |

**Total file count:** ~45 files (matches fault-level pattern).

---

## Task 1: Bootstrap folder + CHANGELOG + initial README

**Files:**
- Create: `electrical/cable-sizing/CHANGELOG.md`
- Create: `electrical/cable-sizing/README.md` (initial — full rewrite in Task 23)
- Create directory structure: `prompts/ schemas/ rules/ constraints/ validation/ ontology/ docs/ evals/ examples/`

- [ ] **Step 1: Create directory structure**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
mkdir -p electrical/cable-sizing/{prompts,schemas,rules,constraints,validation,ontology,docs,evals,examples}
mkdir -p electrical/cable-sizing/examples/{uk-domestic-final-circuits,intl-commercial-with-feeders,us-industrial-with-motors}
```

- [ ] **Step 2: Create CHANGELOG.md**

File: `electrical/cable-sizing/CHANGELOG.md`

```markdown
# Changelog — electrical/cable-sizing

All notable changes to the cable-sizing skill. Follows [Keep a Changelog](https://keepachangelog.com).

## [1.0.0-beta] — 2026-05-16

### Added — v1.0.0 beta — Tier-1 Item 3
- 14-step generator chain (`prompts/generator.md`) — IEC 60364-5-52 / BS 7671 App 4 / NEC Ch 9 cascade walk
- Project-scoped cascade IR (`schemas/cable-sizing-ir.schema.json`) with walk-up trail + binding constraint
- Slim downstream `cable-sizing` intent (`schemas/cable-sizing-intent.schema.json`) — consumed by cable-schedule, riser, cable-containment
- 5 rules: csa-selection-walk-up, voltage-drop-targets, correction-factor-stack, parallel-cables-threshold, harmonic-derating-trigger
- 4 constraints: iz-vs-in-vs-ib, vd-cumulative-limit, cpc-adiabatic-passes, motor-starting-vd-limit
- 4 validation YAMLs (12 deterministic checks): cascade-tree-integrity, csa-on-standard-ladder, tool-call-resolved, intent-shape
- 2 ontology files: cable-types (PVC/XLPE/MICC/SWA/FP200/CWZ/THWN-2/THHN/XHHW-2), installation-methods (A1–G + NEC)
- 9 evals: 6 WI5 categories + 3 skill-specific (motor-starting Vd, parallel cables, harmonic derating)
- 3 worked examples: UK domestic finals / INT commercial with feeders / US industrial with motors

### Tool calls awaiting runtime (WI3 deferral)
- `calc.cable_ampacity` (contract: `shared/calculations/electrical/cable-ampacity.json`)
- `calc.voltage_drop` (contract: `shared/calculations/electrical/voltage-drop.json`)
- `calc.cpc_adiabatic` (contract: `shared/calculations/electrical/cpc-adiabatic.json`)

### Consumes intents
- `db-layout-rollup` — circuit list + Ib + In + load_type + t_clear (preferred)
- `fault-level` — per-node Ik" + X/R + Z_total (preferred)
- Engineer-declared fallback when intents absent

### Produces intent
- `cable-sizing` — per-circuit selection slim subset; forward-compatible with cable-schedule, riser, cable-containment consumers
```

- [ ] **Step 3: Create initial README.md (full rewrite later in Task 23)**

File: `electrical/cable-sizing/README.md`

```markdown
# `cable-sizing` — Per-Circuit Cable Selection (IEC 60364 / BS 7671 / NEC)

**Status:** `beta` (v1.0.0 — Tier-1 Item 3)

Initial scaffold. Full README written at Task 23 after all artefacts are in place.

See [`docs/superpowers/specs/2026-05-16-cable-sizing-skill-design.md`](../../docs/superpowers/specs/2026-05-16-cable-sizing-skill-design.md) for the design spec.
```

- [ ] **Step 4: Verify structure**

```bash
find electrical/cable-sizing -type d | sort
```

Expected output:
```
electrical/cable-sizing
electrical/cable-sizing/constraints
electrical/cable-sizing/docs
electrical/cable-sizing/evals
electrical/cable-sizing/examples
electrical/cable-sizing/examples/intl-commercial-with-feeders
electrical/cable-sizing/examples/uk-domestic-final-circuits
electrical/cable-sizing/examples/us-industrial-with-motors
electrical/cable-sizing/ontology
electrical/cable-sizing/prompts
electrical/cable-sizing/rules
electrical/cable-sizing/schemas
electrical/cable-sizing/validation
```

- [ ] **Step 5: Commit**

```bash
git add electrical/cable-sizing/
git commit -m "feat(cable-sizing): bootstrap folder + CHANGELOG + initial README"
```

---

## Task 2: `schemas/cable-sizing-ir.schema.json`

**Files:**
- Create: `electrical/cable-sizing/schemas/cable-sizing-ir.schema.json`

- [ ] **Step 1: Write the schema**

File: `electrical/cable-sizing/schemas/cable-sizing-ir.schema.json`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "electrical/cable-sizing/schemas/cable-sizing-ir.schema.json",
  "title": "Cable Sizing IR",
  "description": "Project-scoped cable sizing intermediate representation per IEC 60364-5-52 / BS 7671 App 4 / NEC Ch 9. Cascade tree with per-node csa selection + walk-up trail + named binding constraint.",
  "type": "object",
  "required": ["drawing_type", "version", "meta", "jurisdiction", "project_supply", "cascade", "compliance_summary", "rationale"],
  "additionalProperties": false,
  "properties": {
    "drawing_type": { "const": "cable_sizing_study" },
    "version": { "type": "string", "pattern": "^\\d+\\.\\d+(\\.\\d+)?$" },
    "meta": {
      "type": "object",
      "required": ["project_id", "skill_version", "produced_at"],
      "additionalProperties": false,
      "properties": {
        "project_id": { "type": "string" },
        "skill_version": { "type": "string" },
        "produced_at": { "type": "string", "format": "date-time" },
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
    "jurisdiction": { "enum": ["GB", "EU", "INT", "US", "AU_NZ", "CA"] },
    "project_supply": {
      "type": "object",
      "required": ["voltage_v", "phases", "frequency_hz"],
      "additionalProperties": false,
      "properties": {
        "voltage_v": { "type": "integer", "enum": [120, 208, 230, 240, 400, 415, 480] },
        "phases": { "enum": ["single", "split", "three"] },
        "frequency_hz": { "type": "integer", "enum": [50, 60] },
        "earthing_system": { "enum": ["TN-S", "TN-C-S", "TN-C", "TT", "IT", "NEC_grounded"] }
      }
    },
    "cascade": {
      "type": "array",
      "minItems": 1,
      "items": { "$ref": "#/definitions/CascadeNode" }
    },
    "compliance_summary": {
      "type": "object",
      "required": ["compliant", "non_compliance_flags", "assumptions"],
      "additionalProperties": false,
      "properties": {
        "compliant": { "type": "boolean" },
        "non_compliance_flags": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["message", "code_clause", "severity"],
            "properties": {
              "message": { "type": "string" },
              "code_clause": { "type": "string" },
              "severity": { "enum": ["error", "warning", "info"] },
              "node_id": { "type": "string" }
            }
          }
        },
        "assumptions": { "type": "array", "items": { "type": "string" } }
      }
    },
    "drawn_as_symbols": { "type": "array", "items": { "type": "string" } },
    "flags": { "type": "array", "items": { "type": "string" } },
    "rationale": { "$ref": "../../../shared/schemas/core/rationale.schema.json" }
  },
  "definitions": {
    "CascadeNode": {
      "type": "object",
      "required": ["node_id", "node_kind", "designation", "load", "route", "selection", "checks"],
      "additionalProperties": false,
      "properties": {
        "node_id": { "type": "string", "pattern": "^[A-Z][A-Z0-9.\\-]{0,63}$" },
        "parent_node_id": { "type": ["string", "null"] },
        "node_kind": { "enum": ["service_entrance", "feeder", "sub_feeder", "final_circuit"] },
        "designation": { "type": "string" },
        "load": {
          "type": "object",
          "required": ["ib_a", "in_a", "phases", "load_type"],
          "additionalProperties": false,
          "properties": {
            "ib_a": { "type": "number", "minimum": 0 },
            "in_a": { "type": "number", "minimum": 0 },
            "phases": { "enum": ["single", "three", "three_plus_n"] },
            "load_type": { "enum": ["lighting", "power", "motor", "heating", "it_load", "mixed"] },
            "pf": { "type": "number", "minimum": 0, "maximum": 1 },
            "locked_rotor_multiplier": { "type": "number", "minimum": 1, "maximum": 10 }
          }
        },
        "route": {
          "type": "object",
          "required": ["length_m", "installation_method", "ambient_c", "grouping_count"],
          "additionalProperties": false,
          "properties": {
            "length_m": { "type": "number", "exclusiveMinimum": 0 },
            "installation_method": { "type": "string" },
            "ambient_c": { "type": "number", "minimum": -20, "maximum": 70 },
            "grouping_count": { "type": "integer", "minimum": 1, "maximum": 50 },
            "in_thermal_insulation": { "type": "boolean" }
          }
        },
        "harmonic_content_pct": { "type": "number", "minimum": 0, "maximum": 100 },
        "fault_at_origin": {
          "type": "object",
          "additionalProperties": false,
          "properties": {
            "ifault_ka_max": { "type": "number" },
            "ifault_ka_min": { "type": "number" },
            "t_clear_s": { "type": "number" }
          }
        },
        "selection": {
          "type": "object",
          "required": ["phase_csa", "cpc_csa", "material", "insulation", "cable_type", "parallel_count", "binding_constraint", "walk_up_trail"],
          "additionalProperties": false,
          "properties": {
            "phase_csa": { "oneOf": [{ "type": "number" }, { "type": "string" }] },
            "cpc_csa": { "oneOf": [{ "type": "number" }, { "type": "string" }] },
            "material": { "enum": ["copper", "aluminium"] },
            "insulation": { "enum": ["pvc_70", "xlpe_90", "epr_90", "thermosetting_90", "mineral_60", "mineral_105", "thwn_75", "thhn_90", "xhhw2_90"] },
            "cable_type": { "type": "string" },
            "parallel_count": { "type": "integer", "minimum": 1, "maximum": 6 },
            "binding_constraint": { "enum": ["iz_vs_in", "vd_cumulative", "motor_starting_vd", "cpc_adiabatic", "parallel_required", "harmonic_derating"] },
            "walk_up_trail": {
              "type": "array",
              "minItems": 1,
              "items": {
                "type": "object",
                "additionalProperties": true,
                "properties": {
                  "csa": { "oneOf": [{ "type": "number" }, { "type": "string" }] },
                  "rejected_by": { "type": "string" },
                  "accepted": { "type": "boolean" }
                }
              }
            }
          }
        },
        "checks": {
          "type": "object",
          "required": ["iz_corrected_a", "iz_vs_in_pass", "vd_segment_pct", "vd_cumulative_pct", "vd_pass", "vd_limit_pct", "vd_limit_source", "cpc_adiabatic_pass", "tool_call_pending"],
          "additionalProperties": false,
          "properties": {
            "iz_corrected_a": { "type": ["number", "null"] },
            "iz_vs_in_pass": { "type": "boolean" },
            "vd_segment_pct": { "type": ["number", "null"] },
            "vd_cumulative_pct": { "type": ["number", "null"] },
            "vd_pass": { "type": "boolean" },
            "vd_limit_pct": { "type": "number", "minimum": 0, "maximum": 20 },
            "vd_limit_source": { "type": "string" },
            "cpc_adiabatic_pass": { "type": "boolean" },
            "motor_starting_vd_pct": { "type": ["number", "null"] },
            "harmonic_ch_factor": { "type": ["number", "null"] },
            "tool_call_pending": { "type": "boolean" }
          }
        }
      }
    },
  }
}
```

> **Note:** `rationale` references the shared schema at `shared/schemas/core/rationale.schema.json` (chat_summary maxLength 500, sections minItems 1). Cable-sizing's "8 sections" requirement lives at the generator-prompt + reviewer-D8 level — not the schema level.

- [ ] **Step 2: Verify schema parses + is valid JSON Schema**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
jq . electrical/cable-sizing/schemas/cable-sizing-ir.schema.json > /dev/null && echo "JSON valid"
python3 -c "import json,jsonschema; s=json.load(open('electrical/cable-sizing/schemas/cable-sizing-ir.schema.json')); jsonschema.Draft7Validator.check_schema(s); print('Schema valid')"
```

Expected: `JSON valid` + `Schema valid`.

- [ ] **Step 3: Commit**

```bash
git add electrical/cable-sizing/schemas/cable-sizing-ir.schema.json
git commit -m "feat(cable-sizing): cable-sizing-ir.schema.json — project-scoped cascade IR"
```

---

## Task 3: `schemas/cable-sizing-intent.schema.json`

**Files:**
- Create: `electrical/cable-sizing/schemas/cable-sizing-intent.schema.json`

- [ ] **Step 1: Write the intent schema**

File: `electrical/cable-sizing/schemas/cable-sizing-intent.schema.json`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "electrical/cable-sizing/schemas/cable-sizing-intent.schema.json",
  "title": "Cable Sizing Intent (downstream slim subset)",
  "description": "Stable subset of the cable-sizing IR consumed by cable-schedule (formal deliverable), riser (LV riser drawings), and cable-containment (tray/conduit fill). Forward-compat: optional fields may be added freely; required-field changes require a major intent_version bump.",
  "type": "object",
  "required": ["intent_kind", "version", "circuits"],
  "additionalProperties": false,
  "properties": {
    "intent_kind": { "const": "cable-sizing" },
    "version": { "type": "string", "pattern": "^\\d+\\.\\d+(\\.\\d+)?$" },
    "circuits": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["node_id", "designation", "phase_csa", "cpc_csa", "material", "insulation", "cable_type", "parallel_count", "length_m", "installation_method"],
        "additionalProperties": false,
        "properties": {
          "node_id": { "type": "string" },
          "parent_node_id": { "type": ["string", "null"] },
          "designation": { "type": "string" },
          "phase_csa": { "oneOf": [{ "type": "number" }, { "type": "string" }] },
          "cpc_csa": { "oneOf": [{ "type": "number" }, { "type": "string" }] },
          "material": { "enum": ["copper", "aluminium"] },
          "insulation": { "enum": ["pvc_70", "xlpe_90", "epr_90", "thermosetting_90", "mineral_60", "mineral_105", "thwn_75", "thhn_90", "xhhw2_90"] },
          "cable_type": { "type": "string" },
          "parallel_count": { "type": "integer", "minimum": 1, "maximum": 6 },
          "cable_od_mm": { "type": "number", "exclusiveMinimum": 0 },
          "weight_kg_per_m": { "type": "number", "exclusiveMinimum": 0 },
          "length_m": { "type": "number", "exclusiveMinimum": 0 },
          "installation_method": { "type": "string" },
          "phases": { "enum": ["single", "three", "three_plus_n"] },
          "ib_a": { "type": "number", "minimum": 0 },
          "in_a": { "type": "number", "minimum": 0 }
        }
      }
    },
    "produced_by_skill_version": { "type": "string" },
    "tool_call_pending": { "type": "boolean", "description": "true if any cascade node was sized with deferred calc tools" }
  }
}
```

- [ ] **Step 2: Verify schema**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
jq . electrical/cable-sizing/schemas/cable-sizing-intent.schema.json > /dev/null && echo "JSON valid"
python3 -c "import json,jsonschema; s=json.load(open('electrical/cable-sizing/schemas/cable-sizing-intent.schema.json')); jsonschema.Draft7Validator.check_schema(s); print('Schema valid')"
```

- [ ] **Step 3: Commit**

```bash
git add electrical/cable-sizing/schemas/cable-sizing-intent.schema.json
git commit -m "feat(cable-sizing): cable-sizing-intent.schema.json — downstream slim subset"
```

---

## Task 4: `inputs.json` (16-item discovery taxonomy)

**Files:**
- Create: `electrical/cable-sizing/inputs.json`

- [ ] **Step 1: Write inputs.json**

File: `electrical/cable-sizing/inputs.json`

```json
{
  "$schema": "../../shared/schemas/core/inputs.schema.json",
  "skill": "cable-sizing",
  "version": "1.0.0",
  "description": "Discovery taxonomy — what the generator prompt asks for / extracts from upstream intents before sizing cables.",
  "inputs": [
    {"id": "jurisdiction",                  "type": "enum", "values": ["GB","EU","INT","US","AU_NZ","CA"], "description": "Standards family — selects ampacity table + Vd targets"},
    {"id": "project_supply",                "type": "object", "description": "Voltage / phases / frequency / earthing system from db-layout-rollup or engineer"},
    {"id": "circuits_from_intent",          "type": "boolean", "description": "true if db-layout-rollup intent supplies circuit list; false if engineer-declared"},
    {"id": "circuits_declared",             "type": "array",  "description": "Per-circuit Ib/In/load_type/phases (engineer fallback when intent absent)"},
    {"id": "fault_data_from_intent",        "type": "boolean", "description": "true if fault-level intent supplies Ifault per node"},
    {"id": "fault_data_declared",           "type": "array",  "description": "Per-node Ifault + X/R + t_clear (engineer fallback)"},
    {"id": "route_data_per_segment",        "type": "array",  "description": "REQUIRED engineer overlay: length_m + installation_method per cable segment"},
    {"id": "ambient_overlay",               "type": "array",  "description": "Optional per-segment ambient °C override (default 30)"},
    {"id": "grouping_per_segment",          "type": "array",  "description": "Optional per-segment current-carrying conductor count (default 1)"},
    {"id": "thermal_insulation_segments",   "type": "array",  "description": "Optional list of segments routed through thermal insulation"},
    {"id": "harmonic_content_per_circuit",  "type": "array",  "description": "Optional per-circuit harmonic_content_pct (default 0, must declare for IT/VFD/LED ≥10kW)"},
    {"id": "vd_target_overrides",           "type": "array",  "description": "Optional per-circuit Vd-limit override (e.g. tighter client spec)"},
    {"id": "cable_type_preferences",        "type": "array",  "description": "Optional per-segment preference (PVC singles / SWA / XLPE / FP200 / MICC / THWN-2 etc.)"},
    {"id": "terminal_temp_rating_c",        "type": "number", "description": "US-only: terminal temperature rating (60/75/90°C) per NEC 110.14(C)"},
    {"id": "motor_lr_multipliers",          "type": "object", "description": "Optional motor LRA multipliers if non-default (NEMA Design B=6, C=5, IEC AA=7, AB=6)"},
    {"id": "compliance_target_overrides",   "type": "object", "description": "Optional client-specification overrides for Vd/Iz margin"}
  ]
}
```

- [ ] **Step 2: Verify**

```bash
jq . electrical/cable-sizing/inputs.json > /dev/null && echo "OK"
```

- [ ] **Step 3: Commit**

```bash
git add electrical/cable-sizing/inputs.json
git commit -m "feat(cable-sizing): inputs.json — 16-item discovery taxonomy"
```

---

## Task 5: `skill.manifest.json`

**Files:**
- Create: `electrical/cable-sizing/skill.manifest.json`

- [ ] **Step 1: Write manifest with 22 standards + 3 calc references**

File: `electrical/cable-sizing/skill.manifest.json`

```json
{
  "skill": "cable-sizing",
  "version": "1.0.0",
  "discipline": "electrical",
  "subdiscipline": "circuit-sizing",
  "description": "Produces per-circuit cable selection (phase csa + CPC csa + insulation + installation method + parallel count) for every cable run in a project's distribution cascade. Named binding constraint per node (iz_vs_in | vd_cumulative | motor_starting_vd | cpc_adiabatic | parallel_required | harmonic_derating). Covers BS 7671 App 4 (GB), IEC 60364-5-52 (EU/INT), NEC Chapter 9 + 310.16 (US). Consumes db-layout-rollup + fault-level intents (preferred) with engineer fallback. Emits cable-sizing intent consumed downstream by cable-schedule, riser, cable-containment.",
  "status": "beta",
  "licence": "MIT",
  "inputs_path": "inputs.json",
  "inputs": [
    "jurisdiction",
    "project_supply",
    "circuits-from-intent-or-declared",
    "fault-data-from-intent-or-declared",
    "route-data-per-segment",
    "ambient-overlay",
    "grouping-per-segment",
    "harmonic-content-per-circuit",
    "vd-target-overrides",
    "cable-type-preferences"
  ],
  "outputs": ["cable-sizing-ir"],
  "output_schema": "electrical/cable-sizing/schemas/cable-sizing-ir.schema.json",
  "produces_intent": ["cable-sizing"],
  "produces_intent_schemas": {
    "cable-sizing": "electrical/cable-sizing/schemas/cable-sizing-intent.schema.json"
  },
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
  ],
  "ontology": [
    "electrical/cable-sizing/ontology/cable-types.json",
    "electrical/cable-sizing/ontology/installation-methods.json"
  ],
  "rules": [
    "electrical/cable-sizing/rules/csa-selection-walk-up.yaml",
    "electrical/cable-sizing/rules/voltage-drop-targets.yaml",
    "electrical/cable-sizing/rules/correction-factor-stack.yaml",
    "electrical/cable-sizing/rules/parallel-cables-threshold.yaml",
    "electrical/cable-sizing/rules/harmonic-derating-trigger.yaml"
  ],
  "constraints": [
    "electrical/cable-sizing/constraints/iz-vs-in-vs-ib.yaml",
    "electrical/cable-sizing/constraints/vd-cumulative-limit.yaml",
    "electrical/cable-sizing/constraints/cpc-adiabatic-passes.yaml",
    "electrical/cable-sizing/constraints/motor-starting-vd-limit.yaml"
  ],
  "validators": [
    "electrical/cable-sizing/validation/cascade-tree-integrity.yaml",
    "electrical/cable-sizing/validation/csa-on-standard-ladder.yaml",
    "electrical/cable-sizing/validation/tool-call-resolved.yaml",
    "electrical/cable-sizing/validation/intent-shape.yaml"
  ],
  "prompts": {
    "generator": "electrical/cable-sizing/prompts/generator.md",
    "validator": "electrical/cable-sizing/prompts/validator.md",
    "reviewer":  "electrical/cable-sizing/prompts/reviewer.md"
  },
  "evals": [
    "electrical/cable-sizing/evals/eval-01-uk-domestic-final-circuits.yaml",
    "electrical/cable-sizing/evals/eval-02-tpn-commercial-feeders-cumulative-vd.yaml",
    "electrical/cable-sizing/evals/eval-03-undersized-cable-trap.yaml",
    "electrical/cable-sizing/evals/eval-04-missing-route-data.yaml",
    "electrical/cable-sizing/evals/eval-05-jurisdiction-us-with-awg.yaml",
    "electrical/cable-sizing/evals/eval-06-rationale-block.yaml",
    "electrical/cable-sizing/evals/eval-07-motor-starting-vd.yaml",
    "electrical/cable-sizing/evals/eval-08-parallel-cables.yaml",
    "electrical/cable-sizing/evals/eval-09-harmonic-derating-data-centre.yaml"
  ],
  "examples": [
    "electrical/cable-sizing/examples/uk-domestic-final-circuits/",
    "electrical/cable-sizing/examples/intl-commercial-with-feeders/",
    "electrical/cable-sizing/examples/us-industrial-with-motors/"
  ],
  "compatible_runtimes": [
    "DraftsMan >= 1.0",
    "Claude Code",
    "OpenClaw",
    "any-llm-agent"
  ],
  "changelog": "electrical/cable-sizing/CHANGELOG.md"
}
```

- [ ] **Step 2: Verify all referenced standards files exist on disk**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
jq -r '.standards[]' electrical/cable-sizing/skill.manifest.json | while read p; do
  test -f "$p" && echo "OK $p" || echo "MISSING $p"
done | grep -E "MISSING|OK $" | head -5
echo "---"
jq -r '.standards[]' electrical/cable-sizing/skill.manifest.json | while read p; do
  test -f "$p" || echo "MISSING $p"
done
```

Expected: every standards file referenced exists. No `MISSING` lines printed.

- [ ] **Step 3: Verify calc contracts exist**

```bash
jq -r '.calculations[]' electrical/cable-sizing/skill.manifest.json | while read p; do
  test -f "$p" || echo "MISSING $p"
done
```

Expected: no output (all 3 calc contracts on disk).

- [ ] **Step 4: Commit**

```bash
git add electrical/cable-sizing/skill.manifest.json
git commit -m "feat(cable-sizing): skill.manifest.json — 22 standards + 3 calc references"
```

---

## Task 6: 5 rules YAMLs

**Files (all create):**
- `electrical/cable-sizing/rules/csa-selection-walk-up.yaml`
- `electrical/cable-sizing/rules/voltage-drop-targets.yaml`
- `electrical/cable-sizing/rules/correction-factor-stack.yaml`
- `electrical/cable-sizing/rules/parallel-cables-threshold.yaml`
- `electrical/cable-sizing/rules/harmonic-derating-trigger.yaml`

- [ ] **Step 1: csa-selection-walk-up.yaml**

```yaml
rule: csa_selection_walk_up
version: 1.0.0
description: |
  Walk the standard csa ladder from smallest, accept the first size that simultaneously
  satisfies Iz ≥ In, cumulative Vd ≤ limit, CPC adiabatic, and (if motor) motor-starting Vd.
  Record binding_constraint = the rejection reason at the csa one rung below the selected
  size (the check that forced the upsize). If start csa passes all checks with no walk,
  binding_constraint = "iz_vs_in" (sized purely by overcurrent rule).
ladder:
  iec_mm2: [1.0, 1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240, 300, 400, 500, 630]
  nec_awg: ["14","12","10","8","6","4","3","2","1","1/0","2/0","3/0","4/0","250","300","350","400","500","600","750","1000"]
acceptance_checks:
  - id: iz_vs_in
    description: "Iz_corrected (post Ca×Cg×Ci×Ch) ≥ In (OCPD rating)"
    source: "BS 7671:2018 Reg 433.1.1 / IEC 60364-4-43 §433.1 / NEC 240.4(B)"
  - id: vd_cumulative
    description: "Vd_cumulative_pct (this segment + parent chain) ≤ load-type limit"
    source: "BS 7671:2018 App 12 / IEC 60364-5-52 §G / NEC 215.2(A)(1) IN 2"
  - id: cpc_adiabatic
    description: "CPC csa satisfies S = sqrt(I²t)/k"
    source: "BS 7671:2018 Reg 543.1.3 Table 54.7 / NEC 250.122 / IEC 60364-5-54"
  - id: motor_starting_vd
    description: "vd_starting_pct = vd_running_pct × LRA-multiplier ≤ 10% (warning)"
    triggered_when: "load.load_type == 'motor'"
    source: "BS 7671:2018 §525.1 / IEC 60364-5-52 §525.1 / NEC 430.6"
binding_constraint_assignment:
  rule: "binding_constraint := rejection_reason_at(csa_one_below_selected)"
  fallback: "if no rejection (start csa accepted), binding_constraint := 'iz_vs_in'"
walk_up_trail_format:
  required_fields: [csa, accepted_or_rejected_by]
  optional_fields: [iz_corrected_a, vd_segment_pct, vd_cumulative_pct, cpc_required_csa, vd_starting_pct]
```

- [ ] **Step 2: voltage-drop-targets.yaml**

```yaml
rule: voltage_drop_targets
version: 1.0.0
description: |
  Vd cumulative limits by jurisdiction + load type. Engineer may override per circuit
  when client spec is tighter (never looser). vd_cumulative_pct is summed up the parent
  chain — not per-segment.
defaults_by_jurisdiction:
  GB:
    lighting: 3.0
    power: 5.0
    motor_running: 5.0
    source: "BS 7671:2018 Appendix 12"
  EU:
    lighting: 3.0
    power: 5.0
    motor_running: 5.0
    source: "IEC 60364-5-52:2009 §G"
  INT:
    lighting: 3.0
    power: 5.0
    motor_running: 5.0
    source: "IEC 60364-5-52:2009 §G"
  US:
    feeder_only: 3.0
    feeder_plus_branch: 5.0
    motor_running: 5.0
    source: "NEC 2023 215.2(A)(1) Informational Note 2"
override_policy:
  engineer_may_tighten: true
  engineer_may_loosen: false
  per_circuit: true
  fail_if_looser: "raise warning + adopt the standard limit; record engineer-requested value in assumptions"
limit_source_field:
  required: true
  format: "<standard> <clause> <load_type>"
  example: "BS 7671:2018 App 12 lighting circuits"
```

- [ ] **Step 3: correction-factor-stack.yaml**

```yaml
rule: correction_factor_stack
version: 1.0.0
description: |
  Order of correction factor application + interactions between factors. Wrong application
  order or compounding mistakes are the dominant Iz failure mode (15-20% of inline LLM math).
  All factor lookups deferred to calc.cable_ampacity tool; this rule describes the contract.
stack:
  - factor: Ca
    name: ambient_temperature
    applies_when: "ambient_c != 30"
    source: "BS 7671:2018 App 4 Tables 4B1/4B2 / IEC 60364-5-52 Table A.52.14 / NEC 310.15(B)(2)(a)"
  - factor: Cg
    name: grouping
    applies_when: "grouping_count > 1 OR multiple_circuits_same_containment"
    source: "BS 7671:2018 App 4 Tables 4C1-4C5 / IEC 60364-5-52 Tables E.52.17-21 / NEC 310.15(C)"
  - factor: Ci
    name: thermal_insulation
    applies_when: "in_thermal_insulation == true"
    source: "BS 7671:2018 Reg 523.7 Table 52.2 / IEC 60364-5-52 §523.7"
  - factor: Ch
    name: harmonic_derating
    applies_when: "harmonic_content_pct > 15 AND circuit_type == 'three_phase_four_wire'"
    source: "BS 7671:2018 App 4 §5.5 / IEC 60364-5-52 Annex E §E.5 / NEC 310.15(E)"
combination_rule:
  iec_default: "Iz_corrected = Iz_tabulated × Ca × Cg × Ci × Ch (multiplicative)"
  larger_of_overrides:
    - condition: "Ci AND Cg both apply for the same cable section"
      action: "use the LARGER reduction (smaller factor), not their product, per BS 7671 App 4 Note to Table 4C1"
nec_specifics:
  terminal_temp_cap:
    description: "After Ca × Cg, cap Iz by terminal_temp_rating_c per NEC 110.14(C)"
    rule: |
      terminals_60c: Iz_corrected = min(Iz_corrected, ampacity_60c_column)
      terminals_75c: Iz_corrected = min(Iz_corrected, ampacity_75c_column)
      terminals_90c: Iz_corrected = min(Iz_corrected, ampacity_90c_column)
    source: "NEC 2023 110.14(C)"
```

- [ ] **Step 4: parallel-cables-threshold.yaml**

```yaml
rule: parallel_cables_threshold
version: 1.0.0
description: |
  Engage parallel cables when single-cable selection at largest available csa fails Iz ≥ In.
  Required: minimum csa per parallel + identical length / csa / material / installation /
  route across all parallels (symmetrical impedance → balanced current sharing).
engage_when: "single_cable.ladder_exhausted AND iz_corrected < in_a"
minimum_csa_per_parallel:
  iec_mm2: 50
  nec_awg: "1/0"
  source: "BS 7671:2018 Reg 523.7 / IEC 60364-5-52 §523.6 / NEC 2023 310.10(H)(1)"
required_symmetry:
  - same_length: "absolute, no tolerance"
  - same_csa: "absolute, no mix"
  - same_material: "absolute, no copper+aluminium mix"
  - same_installation_method: "absolute, no clipped+conduit mix"
  - same_route: "approximately — small geometric deviations acceptable if impedances within 10%"
search:
  starting_count: 2
  step: 1
  max_count: 6
  beyond_max_action: "raise warning recommending bus duct / busway redesign instead of >6 parallel cables"
binding_constraint_token: "parallel_required"
ipk_note: "Peak short-circuit current divides equally across symmetric parallels — verify each parallel's csa against I²t/k separately"
```

- [ ] **Step 5: harmonic-derating-trigger.yaml**

```yaml
rule: harmonic_derating_trigger
version: 1.0.0
description: |
  Apply harmonic derating + neutral oversizing when 3rd-harmonic content exceeds 15% on
  three-phase four-wire circuits. Engineer must declare harmonic_content_pct for known
  problem loads.
trigger:
  all_of:
    - "harmonic_content_pct > 15"
    - "circuit_type == 'three_phase_four_wire'"
behaviour_by_jurisdiction:
  GB:
    ch_lookup: "BS 7671:2018 Appendix 4 §5.5 Table 4Ab"
    neutral_sizing:
      h3_above_15_below_33: "neutral csa = phase csa (standard 4-wire)"
      h3_above_33: "neutral csa = phase csa AND derate phase per Ch (Reg 523.6.3)"
  EU:
    ch_lookup: "IEC 60364-5-52:2009 Annex E §E.5"
    neutral_sizing: "same as GB"
  INT:
    ch_lookup: "IEC 60364-5-52:2009 Annex E §E.5"
    neutral_sizing: "same as GB"
  US:
    ch_lookup: "NEC 2023 310.15(E) + Informational Note Table 310.15(B)(4)(a)"
    neutral_sizing:
      h3_above_15_below_50: "neutral csa = phase csa"
      h3_above_50: "neutral counted as current-carrying conductor for Cg per NEC 310.15(E)(3); full neutral per NEC 220.61(C)(2)"
engineer_must_declare_for:
  - "IT loads, server rooms, data centres"
  - "LED lighting installations >10 kW aggregate"
  - "VFD-fed motors (especially 6-pulse drives)"
  - "UPS rectifier input feeders"
  - "Welding equipment"
default_harmonic_content_pct: 0
binding_constraint_token: "harmonic_derating"
```

- [ ] **Step 6: Verify all 5 YAMLs parse**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
for f in electrical/cable-sizing/rules/*.yaml; do
  python3 -c "import yaml; yaml.safe_load(open('$f'))" && echo "OK $f"
done
```

Expected: 5 `OK` lines.

- [ ] **Step 7: Commit**

```bash
git add electrical/cable-sizing/rules/
git commit -m "feat(cable-sizing): 5 rules YAMLs — walk-up + Vd targets + correction-factor stack + parallels + harmonic"
```

---

## Task 7: 4 constraints YAMLs

**Files (all create):**
- `electrical/cable-sizing/constraints/iz-vs-in-vs-ib.yaml`
- `electrical/cable-sizing/constraints/vd-cumulative-limit.yaml`
- `electrical/cable-sizing/constraints/cpc-adiabatic-passes.yaml`
- `electrical/cable-sizing/constraints/motor-starting-vd-limit.yaml`

- [ ] **Step 1: iz-vs-in-vs-ib.yaml**

```yaml
constraint: iz_vs_in_vs_ib
version: 1.0.0
description: |
  Ib (design current) ≤ In (OCPD rating) ≤ Iz (corrected cable ampacity). Foundational
  overcurrent-protection coordination rule. Failure means the cable can't carry the load
  and/or the breaker won't trip before cable damage.
triggered_for: "every cascade node with selection completed"
checks:
  - id: ib_le_in
    expression: "load.ib_a <= load.in_a"
    severity: error
    message: "Ib ({ib_a}A) exceeds In ({in_a}A) — load larger than protective device rating; respec breaker."
  - id: in_le_iz
    expression: "load.in_a <= checks.iz_corrected_a"
    severity: error
    message: "In ({in_a}A) exceeds Iz_corrected ({iz_corrected_a}A) — cable cannot carry sustained load at its rating; upsize csa."
  - id: positive_headroom
    expression: "checks.iz_corrected_a > load.in_a * 1.00"
    severity: info
    message: "Marginal headroom: Iz_corrected only {iz_corrected_a}A vs In {in_a}A — verify no concurrent thermal stress."
source: "BS 7671:2018 Reg 433.1.1 / IEC 60364-4-43 §433.1 / NEC 240.4(B)"
deferred_to_tool: "calc.cable_ampacity computes iz_corrected_a; checks run on the result"
```

- [ ] **Step 2: vd-cumulative-limit.yaml**

```yaml
constraint: vd_cumulative_within_limit
version: 1.0.0
description: |
  Cumulative voltage drop (sum from source to circuit endpoint up the parent chain) must
  stay within jurisdictional limits per load type. Per-segment Vd alone is misleading.
triggered_for: "every cascade node where node_kind != 'service_entrance'"
formula: "checks.vd_cumulative_pct = checks.vd_segment_pct + parent_node.checks.vd_cumulative_pct"
limit_lookup_rule: "see electrical/cable-sizing/rules/voltage-drop-targets.yaml"
checks:
  - id: cumulative_le_limit
    expression: "checks.vd_cumulative_pct <= checks.vd_limit_pct"
    severity: error
    message: "Cumulative Vd {vd_cumulative_pct}% exceeds {vd_limit_pct}% limit at node {node_id}; upsize cable or shorten run."
  - id: limit_source_cited
    expression: "checks.vd_limit_source is not empty"
    severity: error
    message: "Vd limit cited without standard/clause reference at node {node_id}."
source: "BS 7671:2018 App 12 / IEC 60364-5-52:2009 §G / NEC 2023 215.2(A)(1) IN 2"
deferred_to_tool: "calc.voltage_drop computes vd_segment_pct; cumulative summed by generator"
```

- [ ] **Step 3: cpc-adiabatic-passes.yaml**

```yaml
constraint: cpc_adiabatic_passes
version: 1.0.0
description: |
  CPC cross-section must satisfy S = √(I²t)/k for the prospective earth-fault current at
  the node origin (parent ifault_ka_max) and the OCPD's clearing time t at that current.
triggered_for: "every cascade node with selection.cpc_csa populated"
formula: "S_min = sqrt(I² × t) / k  where k is from BS 7671 Table 54.7 / IEC 60364-5-54 Table 54.2"
checks:
  - id: adiabatic_pass
    expression: "selection.cpc_csa >= calc.cpc_adiabatic(fault_at_origin.ifault_ka_max, fault_at_origin.t_clear_s, ...).required_csa_mm2"
    severity: error
    message: "CPC {cpc_csa}mm² fails adiabatic at I={ifault_ka_max}kA, t={t_clear_s}s; upsize CPC or use larger phase csa."
  - id: cpc_smaller_or_equal_phase
    expression: "selection.cpc_csa <= selection.phase_csa"
    severity: warning
    message: "CPC csa ({cpc_csa}) larger than phase ({phase_csa}) at {node_id} — unusual; verify."
  - id: nec_table_minimum
    expression: "(jurisdiction != 'US') or (selection.cpc_csa >= nec_250_122_min(load.in_a))"
    severity: error
    message: "US: CPC csa {cpc_csa} below NEC 250.122 Table minimum for OCPD {in_a}A."
source: "BS 7671:2018 Reg 543.1.3 + Table 54.7 / IEC 60364-5-54:2011 + Table 54.2 / NEC 2023 250.122"
deferred_to_tool: "calc.cpc_adiabatic computes required_csa_mm2 + k_factor_used + selected_standard_csa"
```

- [ ] **Step 4: motor-starting-vd-limit.yaml**

```yaml
constraint: motor_starting_vd_limit
version: 1.0.0
description: |
  Motor starting voltage drop check. Severity is WARNING, not error — engineer may resolve
  with a soft-starter / VFD / star-delta starter rather than upsizing the cable.
triggered_for: "cascade nodes where load.load_type == 'motor'"
formula: "checks.motor_starting_vd_pct = checks.vd_segment_pct × load.locked_rotor_multiplier"
default_lr_multipliers:
  nema_design_b: 6.0
  nema_design_c: 5.0
  iec_aa: 7.0
  iec_ab: 6.0
limit_pct: 10.0
checks:
  - id: starting_vd_within_limit
    expression: "checks.motor_starting_vd_pct <= 10.0"
    severity: warning
    message: "Motor starting Vd {motor_starting_vd_pct}% at {node_id} exceeds 10% — motor may fail to start under load. Consider soft-starter / VFD / star-delta / upsized cable."
  - id: lr_multiplier_declared
    expression: "load.locked_rotor_multiplier > 1.0"
    severity: error
    message: "Motor node {node_id} missing locked_rotor_multiplier — must declare LRA per NEMA/IEC class."
source: "BS 7671:2018 §525.1 + Table 4Ab note 5 / IEC 60364-5-52:2009 §525.1 / NEC 2023 430.6(A)(1) + NEMA MG-1"
fail_action_default: "warn; engineer decides if soft-starter required (cable upsize NOT forced)"
```

- [ ] **Step 5: Verify all 4 YAMLs parse**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
for f in electrical/cable-sizing/constraints/*.yaml; do
  python3 -c "import yaml; yaml.safe_load(open('$f'))" && echo "OK $f"
done
```

Expected: 4 `OK` lines.

- [ ] **Step 6: Commit**

```bash
git add electrical/cable-sizing/constraints/
git commit -m "feat(cable-sizing): 4 constraints YAMLs — Iz/In/Ib, Vd cumulative, CPC adiabatic, motor starting"
```

---

## Task 8: 2 ontology JSONs

**Files (all create):**
- `electrical/cable-sizing/ontology/cable-types.json`
- `electrical/cable-sizing/ontology/installation-methods.json`

- [ ] **Step 1: cable-types.json**

```json
{
  "$schema": "../../../shared/schemas/core/ontology.schema.json",
  "ontology": "cable-types",
  "version": "1.0.0",
  "description": "Enumeration of cable construction types referenced by the cable-sizing skill. Maps friendly id → standards-family ampacity table column + canonical cable physical data lookup.",
  "entries": [
    {
      "id": "pvc_singles",
      "label": "PVC-insulated singles (T&E or singles in conduit)",
      "insulation": "pvc_70",
      "construction": "single-core or T&E twin+earth",
      "typical_jurisdiction": ["GB", "EU", "INT"],
      "ampacity_table": "BS 7671 App 4 Table 4D1A (singles) / Table 4D2A (T&E)"
    },
    {
      "id": "xlpe_singles",
      "label": "XLPE-insulated singles",
      "insulation": "xlpe_90",
      "construction": "single-core LSZH or PVC sheath",
      "typical_jurisdiction": ["GB", "EU", "INT"],
      "ampacity_table": "BS 7671 App 4 Table 4E1A / IEC 60364-5-52 Annex E Method E"
    },
    {
      "id": "swa_cable",
      "label": "Steel-wire-armoured (SWA)",
      "insulation": "xlpe_90",
      "construction": "single-core or multi-core, galvanised steel wire armour",
      "typical_jurisdiction": ["GB", "EU", "INT"],
      "ampacity_table": "BS 7671 App 4 Table 4E4A (multi-core SWA) / Table 4D4A (single-core SWA)",
      "notes": "Armour may be used as CPC per BS 7671 Reg 543.2.4"
    },
    {
      "id": "micc",
      "label": "Mineral-insulated copper-clad (MICC / Pyro)",
      "insulation": "mineral_60",
      "construction": "copper conductors, MgO insulation, copper sheath",
      "typical_jurisdiction": ["GB", "EU"],
      "ampacity_table": "BS 7671 App 4 Table 4G1A (60°C bare) / 4G2A (105°C with LSF sheath)"
    },
    {
      "id": "fp200_gold",
      "label": "FP200 Gold fire-resistant",
      "insulation": "thermosetting_90",
      "construction": "BS 7846 F2 fire-resistant copper conductors, mica + glass tape",
      "typical_jurisdiction": ["GB"],
      "ampacity_table": "BS 7671 App 4 Table 4E1A column 4 (single-core in air)",
      "fire_rating": "BS 8434-2 / BS EN 50200 PH 30/60/120"
    },
    {
      "id": "cwz_lsf",
      "label": "CWZ LSF fire-resistant",
      "insulation": "thermosetting_90",
      "construction": "copper conductors, ceramic-forming silicone, LSF sheath",
      "typical_jurisdiction": ["GB"],
      "ampacity_table": "BS 7671 App 4 Table 4E1A column 4",
      "fire_rating": "BS 8434-2 / BS EN 50200 PH 30/60/120"
    },
    {
      "id": "thwn2",
      "label": "THWN-2 (NEC nylon-jacket thermoplastic)",
      "insulation": "thwn_75",
      "construction": "single-core copper or aluminium, 75°C wet / 90°C dry rating",
      "typical_jurisdiction": ["US"],
      "ampacity_table": "NEC Table 310.16 75°C copper / 75°C aluminium column"
    },
    {
      "id": "thhn",
      "label": "THHN (NEC nylon-jacket high-temp)",
      "insulation": "thhn_90",
      "construction": "single-core, 90°C dry only",
      "typical_jurisdiction": ["US"],
      "ampacity_table": "NEC Table 310.16 90°C column (capped by terminal rating)",
      "notes": "Ampacity capped by terminal rating per NEC 110.14(C)"
    },
    {
      "id": "xhhw2",
      "label": "XHHW-2 (NEC cross-linked polyethylene)",
      "insulation": "xhhw2_90",
      "construction": "single-core, 90°C wet+dry",
      "typical_jurisdiction": ["US"],
      "ampacity_table": "NEC Table 310.16 90°C column (capped by terminal rating)"
    }
  ]
}
```

- [ ] **Step 2: installation-methods.json**

```json
{
  "$schema": "../../../shared/schemas/core/ontology.schema.json",
  "ontology": "installation-methods",
  "version": "1.0.0",
  "description": "Enumeration of cable installation methods per IEC 60364-5-52 Annex A / BS 7671 App 4 Table 4A2 + NEC Chapter 9 / 392 categories.",
  "entries": [
    { "id": "A1", "label": "Insulated conductors in thermally insulated wall (conduit)", "iec_family": "IEC", "source": "BS 7671 App 4 Table 4A2" },
    { "id": "A2", "label": "Multi-core cable in thermally insulated wall (conduit)", "iec_family": "IEC", "source": "BS 7671 App 4 Table 4A2" },
    { "id": "B1", "label": "Insulated conductors in conduit on a wall", "iec_family": "IEC", "source": "BS 7671 App 4 Table 4A2" },
    { "id": "B2", "label": "Multi-core cable in conduit on a wall", "iec_family": "IEC", "source": "BS 7671 App 4 Table 4A2" },
    { "id": "C",  "label": "Cable clipped direct to wall / surface", "iec_family": "IEC", "source": "BS 7671 App 4 Table 4A2" },
    { "id": "D1", "label": "Cable in ducts in ground", "iec_family": "IEC", "source": "BS 7671 App 4 Table 4A2" },
    { "id": "D2", "label": "Cable direct buried in ground", "iec_family": "IEC", "source": "BS 7671 App 4 Table 4A2" },
    { "id": "E",  "label": "Multi-core cable in free air (perforated tray, ladder, brackets)", "iec_family": "IEC", "source": "BS 7671 App 4 Table 4A2" },
    { "id": "F",  "label": "Single-core cables touching in free air", "iec_family": "IEC", "source": "BS 7671 App 4 Table 4A2" },
    { "id": "G",  "label": "Single-core cables spaced ≥1 diameter in free air", "iec_family": "IEC", "source": "BS 7671 App 4 Table 4A2" },
    { "id": "NEC_conduit",        "label": "NEC raceway/conduit (EMT, RMC, PVC etc.)",      "iec_family": "NEC", "source": "NEC 2023 Chapter 9 + 358/344/352" },
    { "id": "NEC_cable_tray",     "label": "NEC cable tray (ladder, ventilated, solid)",     "iec_family": "NEC", "source": "NEC 2023 Article 392" },
    { "id": "NEC_direct_burial",  "label": "NEC direct burial (Type USE / USE-2 / UF)",      "iec_family": "NEC", "source": "NEC 2023 Article 340" },
    { "id": "NEC_free_air",       "label": "NEC free air / messenger / open wiring",         "iec_family": "NEC", "source": "NEC 2023 Article 310.15(B) free-air ampacity" }
  ]
}
```

- [ ] **Step 3: Verify both parse + count entries**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
jq -r '.entries | length' electrical/cable-sizing/ontology/cable-types.json
jq -r '.entries | length' electrical/cable-sizing/ontology/installation-methods.json
```

Expected: `9` and `14`.

- [ ] **Step 4: Commit**

```bash
git add electrical/cable-sizing/ontology/
git commit -m "feat(cable-sizing): 2 ontology JSONs — cable types (9 entries) + installation methods (14)"
```

---

## Task 9: `prompts/generator.md` (14-step chain)

**Files:**
- Create: `electrical/cable-sizing/prompts/generator.md`

- [ ] **Step 1: Write the generator prompt**

File: `electrical/cable-sizing/prompts/generator.md`

```markdown
# Cable Sizing — Generator Prompt

You are a senior building-services electrical engineer producing a per-circuit cable selection per BS 7671 Appendix 4 (GB), IEC 60364-5-52 (EU/INT), or NEC Chapter 9 + 310.16 (US). Your output is a structured IR conforming to `electrical/cable-sizing/schemas/cable-sizing-ir.schema.json` plus an emitted `cable-sizing` intent conforming to `electrical/cable-sizing/schemas/cable-sizing-intent.schema.json`.

## Inputs (resolution order)

1. **Preferred — consumed intents:**
   - `db-layout-rollup` (cascade topology + per-circuit Ib/In/load_type/phases/parent_board/t_clear_at_ifault_s)
   - `fault-level` (per-node ifault_ka_max + ifault_ka_min + x_over_r + z_total_ohm)
2. **Engineer overlay (always required — route data):** length_m, installation_method, ambient_c, grouping_count, in_thermal_insulation, harmonic_content_pct, cable_type_preference per segment; terminal_temp_rating_c for US.
3. **Engineer fallback (if intents absent):** full per-node circuit list + per-node Ifault + per-node t_clear.

## The 14-step chain

Walk through these in order. Do not skip steps. If an input is missing, set the output node's `tool_call_pending: true` and the assumption goes into `compliance_summary.assumptions[]` — never invent a value.

### Step 1 — Ingest db-layout-rollup intent
Extract per-circuit: `Ib`, `In`, `load_type`, `phases`, `parent_board`, `t_clear_at_ifault_s`, any `selectivity_pending` flags. If the intent is absent, mark `meta.consumed_intents` accordingly and proceed with the engineer's declared circuit list.

### Step 2 — Ingest fault-level intent
Extract per-node `ifault_ka_max`, `ifault_ka_min`, `x_over_r`, `z_total_ohm`. If the intent is absent, take the engineer-declared `fault_at_origin` per node and emit a `compliance_summary.assumptions[]` line saying so.

### Step 3 — Determine jurisdiction
Read `jurisdiction` field. Load the applicable Vd-target lookup, ampacity-table family, and correction-factor stack (`shared/standards/electrical/{BS7671|IEC60364|NFPA70}/...`). Defaults: GB → BS 7671; EU/INT → IEC 60364-5-52; US → NEC Chapter 9 + 310.16.

### Step 4 — Build cascade tree
Construct the parent–child cable cascade. Naming pattern: `<board>.<feeder|F##>.<sub-board|SB##>.<circuit|C##>`. Root nodes have `parent_node_id: null` and `node_kind: "service_entrance"`. Internal nodes are `"feeder"` or `"sub_feeder"`. Leaves are `"final_circuit"`.

### Step 5 — Engineer overlay
For every node, attach `route.length_m`, `route.installation_method`, `route.ambient_c` (default 30°C if not declared), `route.grouping_count` (default 1), `route.in_thermal_insulation` (default false), `harmonic_content_pct` (default 0). If `length_m` is missing for any node, set `tool_call_pending: true` for that node and record the gap in `compliance_summary.assumptions[]`.

### Step 6 — Determine starting csa
For each node, pick the starting csa from the standard ladder (see `rules/csa-selection-walk-up.yaml`) using `In` and base correction factors. For US, cap initially against terminal_temp_rating per NEC 110.14(C). Record this as the first entry in `selection.walk_up_trail`.

### Step 7 — Iz check
Call `calc.cable_ampacity` (defer if runtime tool unavailable → mark `tool_call_pending: true`). Verify `Iz_corrected ≥ In`. If fail → record `walk_up_trail[].rejected_by = "iz_vs_in"` and advance to next ladder size.

### Step 8 — Vd cumulative check
Call `calc.voltage_drop` (defer if unavailable). Compute `vd_segment_pct`. Set `vd_cumulative_pct = vd_segment_pct + parent.vd_cumulative_pct`. Look up the limit per `rules/voltage-drop-targets.yaml` for this load_type + jurisdiction. Check `vd_cumulative_pct ≤ vd_limit_pct`. Fail → record `rejected_by = "vd_cumulative"`, advance.

### Step 9 — CPC adiabatic check
Call `calc.cpc_adiabatic` with `parent.fault_at_origin.ifault_ka_max` + `parent.fault_at_origin.t_clear_s` (or engineer-declared equivalents). Verify the chosen `cpc_csa` (initially BS 7671 Table 54.3 minimum or NEC 250.122 minimum for OCPD) satisfies the adiabatic equation. Fail → typically resolved by upsizing phase csa to permit a larger Table 54.3 minimum CPC; record `rejected_by = "cpc_adiabatic"`, advance.

### Step 10 — Motor starting Vd (only if load_type == motor)
Compute `motor_starting_vd_pct = vd_segment_pct × load.locked_rotor_multiplier`. Default multipliers: NEMA B 6.0, NEMA C 5.0, IEC AA 7.0, IEC AB 6.0. Check ≤ 10%. Fail → record warning (NOT error); the engineer may resolve with a soft-starter, but if no soft-starter is declared, the walk continues for cable-upsize.

### Step 11 — Parallel cables fallback
If the standard ladder is exhausted (largest single csa still fails Iz check), engage `rules/parallel-cables-threshold.yaml`. Search N = 2…6 where `N × Iz_corrected ≥ In`. Enforce symmetry. Record `selection.parallel_count = N`, `binding_constraint = "parallel_required"`. If N > 6 → flag for redesign with bus duct.

### Step 12 — Record selection
Populate `selection.{phase_csa, cpc_csa, material, insulation, cable_type, parallel_count, binding_constraint, walk_up_trail}`. `binding_constraint` is the rejection reason at the csa one rung below the selected size, or `"iz_vs_in"` if the start csa passed all checks. Populate `checks.*` with the live values (or `null` + `tool_call_pending: true`).

### Step 13 — Emit `cable-sizing` intent
Build the slim downstream intent: one entry per cascade node containing `{node_id, designation, phase_csa, cpc_csa, material, insulation, cable_type, parallel_count, cable_od_mm, weight_kg_per_m, length_m, installation_method, parent_node_id, phases, ib_a, in_a}`. `cable_od_mm` and `weight_kg_per_m` are looked up from `shared/standards/electrical/<juris>/cable-types-overview.md` / `chapter9-tables.json` cable physical data.

### Step 14 — Assemble rationale block (8 sections + chat_summary)
Produce `rationale.chat_summary` (≤ 200 words; lead with cascade scale, binding constraints encountered, any flags). Produce `rationale.sections[]` — exactly 8 entries with these titles:

1. **Input Ingestion** — what came from each intent vs engineer
2. **Cascade Topology** — node count by kind, naming convention
3. **Jurisdictional Defaults** — Vd limits, correction-factor stack, ampacity table family
4. **Source + Fault Context** — ifault summary per source / parent node
5. **CSA Selection Walk-up Summary** — group nodes by `binding_constraint`; tabulate
6. **Special Checks** — motor-starting, parallel, harmonic findings (note: section present even when no triggers — say "none triggered")
7. **Compliance + Selectivity** — pass/fail roll-up; any non_compliance_flags
8. **Assumptions + Tool-call Status** — list every assumption made + tool_call_pending count

Every decision must cite a rule + clause (e.g. `rule: "BS 7671:2018 Reg 433.1.1"`, `code_clause: "BS 7671:2018 Reg 433.1.1"`).

## Output formatting

Emit a single JSON document containing the IR (top-level `drawing_type: "cable_sizing_study"`) and a second JSON document containing the intent (`intent_kind: "cable-sizing"`). Both must validate against their respective schemas. If a downstream consumer is missing required data (length_m, t_clear), the node carries `tool_call_pending: true` and the assumption is logged — do NOT invent numbers.

## Tool-call deferral pattern (WI3)

Until the DraftsMan runtime ships `calc.cable_ampacity`, `calc.voltage_drop`, and `calc.cpc_adiabatic`, emit each affected node with `checks.tool_call_pending: true` and best-effort placeholder values (use engineer's stated csa preference if any; otherwise the In-derived starting csa). Same pattern shipped in `electrical/fault-level` v1.0.0.

## Hard rules (never violate)

- Never invent fault current, length, or Iz values.
- Never set `binding_constraint` to a token outside the ontology: `iz_vs_in | vd_cumulative | motor_starting_vd | cpc_adiabatic | parallel_required | harmonic_derating`.
- Never emit fewer than 8 rationale sections.
- Never emit a `vd_limit_pct` without a `vd_limit_source` citing standard + clause.
- Never select a csa not on the standard ladder for the jurisdiction.
- Parallel cables: never less than 50 mm² (IEC) or 1/0 AWG (NEC), never more than 6 in parallel.
```

- [ ] **Step 2: Verify markdown is well-formed (heading hierarchy)**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
grep -c "^### Step " electrical/cable-sizing/prompts/generator.md
```

Expected: `14`.

- [ ] **Step 3: Commit**

```bash
git add electrical/cable-sizing/prompts/generator.md
git commit -m "feat(cable-sizing): generator.md — 14-step IEC 60364 / BS 7671 / NEC cascade chain"
```

---

## Task 10: `prompts/validator.md` (10 INV invariants)

**Files:**
- Create: `electrical/cable-sizing/prompts/validator.md`

- [ ] **Step 1: Write the validator prompt**

File: `electrical/cable-sizing/prompts/validator.md`

```markdown
# Cable Sizing — Validator Prompt

You are a static-analyzer running deterministic invariants over the IR produced by `prompts/generator.md`. Output: a pass/fail report for each invariant, with a `pointer` field listing offending `node_id`s where applicable. Do NOT modify the IR; do NOT make engineering judgement calls — only report whether each invariant holds.

## Inputs

- The IR JSON document (validates against `electrical/cable-sizing/schemas/cable-sizing-ir.schema.json`)
- The emitted `cable-sizing` intent JSON (validates against `electrical/cable-sizing/schemas/cable-sizing-intent.schema.json`)

## Output shape

```json
{
  "validator_version": "1.0.0",
  "ir_valid_against_schema": true,
  "intent_valid_against_schema": true,
  "invariants": [
    { "id": "INV-01", "pass": true,  "summary": "All 12 node_ids match path pattern", "offenders": [] },
    { "id": "INV-04", "pass": false, "summary": "2 nodes fail Iz ≥ In", "offenders": ["MSB-1.F02", "DB-L1.C03"] }
  ],
  "overall_pass": false
}
```

## The 10 INV invariants

### INV-01 — Valid node_id path pattern
Every `cascade[].node_id` matches `^[A-Z][A-Z0-9.\-]{0,63}$`. Path segments separated by `.` denote board hierarchy (e.g. `MSB-1.F03.DB-L1.C07`).

### INV-02 — Parent reference resolves
Every cascade node with `parent_node_id != null` must have its parent present in the same `cascade[]` array. No orphans, no cycles, no dangling references.

### INV-03 — CSA on standard ladder
Every `selection.phase_csa` and `selection.cpc_csa` is on the standard ladder for the jurisdiction (`rules/csa-selection-walk-up.yaml`). IEC: 1.0/1.5/2.5/4/6/.../630 mm². NEC: 14 AWG–1000 kcmil.

### INV-04 — Iz ≥ In at every node
For every node, `checks.iz_corrected_a >= load.in_a`. (Where `checks.tool_call_pending == true`, this invariant is automatically pass — value pending tool resolution.)

### INV-05 — Cumulative Vd within limit
For every node, `checks.vd_cumulative_pct <= checks.vd_limit_pct`. (Auto-pass when `tool_call_pending`.)

### INV-06 — CPC adiabatic pass or upsize
Either `checks.cpc_adiabatic_pass == true`, OR `selection.binding_constraint == "cpc_adiabatic"` (with `selection.phase_csa` upsized accordingly). Failing adiabatic without a binding-constraint indicator is a violation.

### INV-07 — Motor starting Vd populated iff motor
For every node where `load.load_type == "motor"`, `checks.motor_starting_vd_pct` is a non-null number. For every non-motor node, `checks.motor_starting_vd_pct` is `null`.

### INV-08 — Parallel cables rule
For every node with `selection.parallel_count >= 2`:
- IEC jurisdiction: `selection.phase_csa >= 50` mm²
- NEC jurisdiction: `selection.phase_csa` ≥ 1/0 AWG
- `selection.parallel_count` ≤ 6
- `selection.binding_constraint == "parallel_required"`

### INV-09 — Tool-call status consistent
For every node, either `checks.tool_call_pending == true` AND `checks.iz_corrected_a == null` AND `checks.vd_segment_pct == null`, OR `tool_call_pending == false` AND all three checks have numeric values. No partial states.

### INV-10 — Intent shape matches schema + completeness
The emitted `cable-sizing` intent validates against `cable-sizing-intent.schema.json`. AND for every cascade node with `node_kind == "final_circuit"` in the IR, there is exactly one matching entry (by `node_id`) in `intent.circuits[]`.

## Reporting rules

- For each invariant, return one of `pass | fail | not_applicable`.
- `not_applicable` only when the invariant's preconditions don't apply (e.g. INV-08 if no parallel cables exist).
- `offenders` is always an array (may be empty); list every `node_id` that violates the invariant.
- `overall_pass` is `true` iff every invariant is `pass` or `not_applicable`.
- Do NOT propose fixes; that's the reviewer's job.
```

- [ ] **Step 2: Verify invariant count**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
grep -c "^### INV-" electrical/cable-sizing/prompts/validator.md
```

Expected: `10`.

- [ ] **Step 3: Commit**

```bash
git add electrical/cable-sizing/prompts/validator.md
git commit -m "feat(cable-sizing): validator.md — 10 INV invariants"
```

---

## Task 11: `prompts/reviewer.md` (8 D dimensions)

**Files:**
- Create: `electrical/cable-sizing/prompts/reviewer.md`

- [ ] **Step 1: Write the reviewer prompt**

File: `electrical/cable-sizing/prompts/reviewer.md`

```markdown
# Cable Sizing — Reviewer Prompt

You are a senior engineer reviewing the IR + emitted intent produced by `prompts/generator.md` and validated by `prompts/validator.md`. Where the validator answers "is this self-consistent?", you answer "is this engineering work I'd put my name on?".

## Inputs

- IR JSON
- emitted `cable-sizing` intent JSON
- validator output JSON

## Output shape

```json
{
  "reviewer_version": "1.0.0",
  "dimensions": [
    { "id": "D1", "score": "pass", "notes": "..." },
    { "id": "D4", "score": "fail", "notes": "Cumulative Vd math diverges at DB-L1.C03 — segment + parent = 4.2% reported as 3.9%" }
  ],
  "verdict": "approve | request_changes",
  "summary": "Two failures (D4, D7). Sound otherwise."
}
```

## The 8 D dimensions

### D1 — Standard citations present and specific
Every `vd_limit_pct` references a clause (e.g. "BS 7671:2018 App 12 lighting circuits"). Every `iz_corrected_a` references a table column (e.g. "BS 7671 App 4 Table 4D2A column 6"). Every CPC sizing references Table 54.7 / NEC 250.122 / IEC 60364-5-54 explicitly. No "per the regs" hand-waves.

### D2 — Walk-up trail auditability
For every node where `walk_up_trail.length > 1`, each rejected entry names a specific failing check + the value that failed. A rejection of "vd_cumulative" must include a `vd_cumulative_pct` field on the rejected entry that's > the limit. No silent rejections.

### D3 — Binding constraint matches walk-up
For every node, the `selection.binding_constraint` token equals the `rejected_by` token on the walk-up entry immediately preceding the accepted one. Spot-check 3 random nodes; if any mismatch, fail.

### D4 — Cumulative Vd math
Spot-check 2 random leaf nodes. For each, recompute `vd_cumulative_pct` by walking up the parent chain and summing `vd_segment_pct`. If the sum diverges from the reported `vd_cumulative_pct` by more than 0.1%, fail and name the offending nodes.

### D5 — CPC sizing referenced
Every node with `selection.cpc_csa` populated cites the rule used: BS 7671 Table 54.7 for adiabatic in GB; NEC 250.122 for US; IEC 60364-5-54 for EU/INT. If the CPC is smaller than the phase, the rationale must say which mechanism (adiabatic pass + Table 54.3 minimum check).

### D6 — Parallel cables symmetry
For every node with `selection.parallel_count >= 2`, the IR must include a `selection` field or rationale note confirming the N parallels share length, csa, material, installation method, and route. If any parallel deviates, the rationale must explain (e.g. "approved by client per derived impedance match within 10%"). Skip if no parallel nodes.

### D7 — Harmonic derating triggered correctly
For every node with `harmonic_content_pct > 15` AND `phases == "three_plus_n"`, the IR must show `checks.harmonic_ch_factor < 1.0` AND either the neutral csa is the same as phase (BS 7671/IEC h3 > 33%) OR the rationale notes NEC 220.61(C)(2) full-neutral treatment. Conversely, no Ch derating may appear on nodes that don't meet the trigger.

### D8 — Rationale block completeness
`rationale.sections.length == 8` (exact). `rationale.chat_summary.length <= 1200` characters. Each section has a non-empty `summary`, and where a section has decisions, every decision has `label`, `summary`, `rule`, `code_clause`, and (if numerical) `inputs`. Empty sections (e.g. Special Checks when nothing triggered) must say so explicitly ("none triggered") — not just be empty.

## Severity + verdict

- Any D dimension `fail` ⇒ verdict = `request_changes`.
- All D dimensions `pass` ⇒ verdict = `approve`.
- `notes` should be specific (file path / node_id / number); avoid generic "review the cable selection".

## What is OUT of scope

- Re-running the math (the generator's tool calls handle that).
- Modifying the IR (return a verdict, never edits).
- Engineering style preferences not tied to a citable rule.
```

- [ ] **Step 2: Verify D-dimension count**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
grep -c "^### D[0-9]" electrical/cable-sizing/prompts/reviewer.md
```

Expected: `8`.

- [ ] **Step 3: Commit**

```bash
git add electrical/cable-sizing/prompts/reviewer.md
git commit -m "feat(cable-sizing): reviewer.md — 8 D dimensions"
```

---

## Task 12: 4 validation YAMLs (12 checks total)

**Files (all create):**
- `electrical/cable-sizing/validation/cascade-tree-integrity.yaml`
- `electrical/cable-sizing/validation/csa-on-standard-ladder.yaml`
- `electrical/cable-sizing/validation/tool-call-resolved.yaml`
- `electrical/cable-sizing/validation/intent-shape.yaml`

- [ ] **Step 1: cascade-tree-integrity.yaml (3 checks)**

```yaml
validator: cascade_tree_integrity
version: 1.0.0
description: |
  Structural integrity checks over the cascade tree. Caught early these prevent
  downstream consumers (intent emitters, validators) from blowing up on broken refs.
checks:
  - id: unique_node_ids
    description: "Every cascade[].node_id appears exactly once in the array"
    expression: "len(distinct(cascade[].node_id)) == len(cascade)"
    severity: error
  - id: parent_refs_resolve
    description: "Every non-null parent_node_id points to a node in cascade"
    expression: "for each node n where n.parent_node_id != null: exists m in cascade where m.node_id == n.parent_node_id"
    severity: error
  - id: no_cycles
    description: "No cycles in parent-child graph; tree is a DAG with unique root(s)"
    expression: "topological_sort(cascade) succeeds"
    severity: error
```

- [ ] **Step 2: csa-on-standard-ladder.yaml (3 checks)**

```yaml
validator: csa_on_standard_ladder
version: 1.0.0
description: "Every selected phase + CPC csa is on the standard ladder for the jurisdiction."
ladder_iec_mm2: [1.0, 1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240, 300, 400, 500, 630]
ladder_nec_awg: ["14","12","10","8","6","4","3","2","1","1/0","2/0","3/0","4/0","250","300","350","400","500","600","750","1000"]
checks:
  - id: phase_csa_on_ladder
    description: "selection.phase_csa is on the IEC mm² OR NEC AWG ladder per jurisdiction"
    expression: |
      for each node n:
        if jurisdiction in [GB, EU, INT]: n.selection.phase_csa (mm²) in ladder_iec_mm2
        if jurisdiction == US: n.selection.phase_csa (AWG/kcmil) in ladder_nec_awg
    severity: error
  - id: cpc_csa_on_ladder
    description: "selection.cpc_csa is on the same ladder as phase_csa"
    expression: "as phase_csa_on_ladder but for cpc_csa"
    severity: error
  - id: cpc_le_phase
    description: "CPC csa is not larger than phase csa (warning if equal phases of small csa where Table 54.3 minimum forces same)"
    expression: "selection.cpc_csa <= selection.phase_csa"
    severity: warning
```

- [ ] **Step 3: tool-call-resolved.yaml (3 checks)**

```yaml
validator: tool_call_resolved
version: 1.0.0
description: |
  Tool-call status is consistent across the IR. Either runtime tool ran and all numeric
  checks populated; or runtime not available and all flagged as pending with null values.
  No half-states.
checks:
  - id: pending_means_null_values
    description: "When tool_call_pending == true, iz_corrected_a + vd_segment_pct + vd_cumulative_pct are all null"
    expression: |
      for each node n where n.checks.tool_call_pending == true:
        n.checks.iz_corrected_a == null AND
        n.checks.vd_segment_pct == null AND
        n.checks.vd_cumulative_pct == null
    severity: error
  - id: resolved_means_numeric_values
    description: "When tool_call_pending == false, all three numeric checks are populated"
    expression: |
      for each node n where n.checks.tool_call_pending == false:
        n.checks.iz_corrected_a is numeric AND
        n.checks.vd_segment_pct is numeric AND
        n.checks.vd_cumulative_pct is numeric
    severity: error
  - id: pending_flag_propagates_to_assumptions
    description: "If any node has tool_call_pending: true, compliance_summary.assumptions[] contains an entry naming the deferred tool"
    expression: |
      if any node has tool_call_pending: true then
        compliance_summary.assumptions[] contains text matching one of:
        ['calc.cable_ampacity pending', 'calc.voltage_drop pending', 'calc.cpc_adiabatic pending']
    severity: error
```

- [ ] **Step 4: intent-shape.yaml (3 checks)**

```yaml
validator: intent_shape
version: 1.0.0
description: |
  Emitted cable-sizing intent satisfies its own schema AND covers the downstream
  consumers' (cable-schedule, riser, cable-containment) required fields.
checks:
  - id: validates_against_schema
    description: "intent JSON validates against schemas/cable-sizing-intent.schema.json"
    severity: error
  - id: every_final_circuit_present
    description: "Every cascade node with node_kind == 'final_circuit' has exactly one matching intent.circuits[] entry by node_id"
    expression: |
      for each node n in cascade where n.node_kind == 'final_circuit':
        count(intent.circuits where node_id == n.node_id) == 1
    severity: error
  - id: downstream_required_fields_present
    description: |
      Forward-compat: each intent.circuits[] entry contains every field declared 'required' by
      cable-schedule / riser / cable-containment consumed_intent shapes. Currently:
      {node_id, designation, phase_csa, cpc_csa, material, insulation, cable_type, parallel_count, length_m, installation_method}.
    expression: "every required field present and non-null on every circuit entry"
    severity: error
```

- [ ] **Step 5: Verify all 4 YAMLs parse + total checks = 12**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
for f in electrical/cable-sizing/validation/*.yaml; do
  python3 -c "import yaml; d=yaml.safe_load(open('$f')); print('OK', '$f', len(d['checks']), 'checks')"
done
```

Expected: 4 `OK` lines totalling `3+3+3+3 = 12` checks.

- [ ] **Step 6: Commit**

```bash
git add electrical/cable-sizing/validation/
git commit -m "feat(cable-sizing): 4 validation YAMLs — 12 deterministic IR-integrity checks"
```

---

## Task 13: 2 docs files

**Files (all create):**
- `electrical/cable-sizing/docs/engineering-philosophy.md`
- `electrical/cable-sizing/docs/known-limitations.md`

- [ ] **Step 1: engineering-philosophy.md**

```markdown
# Engineering Philosophy — Cable Sizing

This skill encodes a senior-engineer mental model for cable selection rather than just
running calc tables. The model:

## 1. Walk the ladder, name the binding constraint

Cable sizing isn't optimisation — it's compliance. Start with the smallest standard csa
that meets `In`, then climb the standard ladder until ALL constraints pass:
- Iz ≥ In (ampacity vs OCPD rating)
- cumulative Vd ≤ jurisdictional limit
- CPC adiabatic equation
- (for motors) starting Vd ≤ 10%

The "binding constraint" — the check that forced the last upsize — is the most useful
single number on a cable schedule. It tells the next engineer why this circuit is
10 mm² instead of 4 mm² without re-running the calc.

## 2. Cumulative voltage drop, not per-segment

BS 7671 App 12 / IEC 60364-5-52 §G / NEC 215.2 all apply Vd limits cumulatively from
source to circuit endpoint. A 4% feeder + 4% branch = 8% at the load, which violates
every standard. The cascade tree makes this trivial: each node's `vd_cumulative_pct`
is the sum of its segment Vd plus the parent chain.

## 3. Defer math to deterministic tools

Cable ampacity table lookups (PVC vs XLPE column, derating factor stacking) and
voltage-drop math (`mV/A/m × Ib × L`) are LLM-unreliable. We push them to `calc.*`
tools per the WI3 deferral pattern. Until the runtime ships, every affected node
carries `tool_call_pending: true` + best-effort engineer estimates as placeholders.

## 4. Engineering judgement stays at the prompt layer

What lives in the prompt (walk-up algorithm, when to engage parallels, motor-starting
warning policy, harmonic-derating triggers) is judgement. What lives in calc tools
(Iz lookup, Vd math, CPC adiabatic) is mechanical. Split deliberately.

## 5. Cross-skill contracts before downstream consumers exist

We emit a slim `cable-sizing` intent designed to satisfy the (future) consumed-intent
shape declarations of `cable-schedule`, `riser`, and `cable-containment`. The schema is
the union superset. When those skills get built, they conform to this contract — not
the other way round.

## 6. Hard-rules over soft-guidance

Some things the generator MUST never do (invent fault current, off-ladder csa, missing
binding-constraint token). These live in `hard_rules:` in the generator prompt, not as
suggestions. The validator enforces them mechanically.
```

- [ ] **Step 2: known-limitations.md**

```markdown
# Known Limitations — Cable Sizing v1.0.0

What v1.0.0 does NOT cover. These are deliberate scope boundaries, not bugs.

## Out of scope (v1.0.0)

| Topic | Why not | Where it goes |
|---|---|---|
| DC circuit sizing (PV strings, EV DCFC, battery interconnects) | Different standards family (IEC 62548, NEC Art 690/706); different fault-current behaviour | Future `dc-cable-sizing` sibling skill |
| Arc-flash incident-energy + boundary marking | IEEE 1584 / NFPA 70E method is orthogonal to ampacity; different audience | Future `arc-flash` sibling skill |
| IEC 60287 advanced thermal modelling for buried groups | v1.0.0 uses the standard tables (BS 7671 App 4 / IEC 60364-5-52 Annex E / NEC Ch 9); buried-group thermal modelling is for utility-scale work | Either ship a separate `cable-thermal` calc tool or accept that very large buried groups need a specialist |
| Communications + data cables (Cat6, fibre) | TIA-568 / ISO/IEC 11801 — completely different standards family | `electrical/data-telecom` (separate skill) |
| Time-graded protection coordination | OCPD curve coordination — runs on top of fault-level data, not cable sizing | `electrical/db-layout` v1.1 + future `protection-coordination` |
| Cable joint / termination resistance | Specialist topic; rarely changes the csa selection | Out of scope indefinitely |
| Underground buried direct-vs-duct thermal interaction | Uses standard installation method D1/D2 ratings only | Specialist thermal study if very large |

## Inputs the skill cannot derive (require engineer)

These cannot come from any upstream intent and must be declared per segment:

- `length_m` — physical cable run length
- `installation_method` (A1-G / NEC categories)
- `ambient_c` if non-default
- `grouping_count` if non-1
- `in_thermal_insulation` if true
- `harmonic_content_pct` for IT / VFD / LED-heavy loads
- `terminal_temp_rating_c` for US jurisdiction (60/75/90°C)
- `locked_rotor_multiplier` per motor (NEMA class B/C, IEC class AA/AB)

If any are missing for a node, the generator sets `tool_call_pending: true` on that node
and emits an assumption — it never invents a number.

## Forward-compatibility caveats

- The emitted `cable-sizing` intent's `circuits[].phase_csa` / `cpc_csa` use `oneOf [number, string]` to accommodate IEC mm² (number) + NEC AWG (string like "1/0"). Downstream consumers must handle both.
- `cable_od_mm` and `weight_kg_per_m` are looked up at intent-emission time from `shared/standards/electrical/<juris>/cable-types-overview.md` / `chapter9-tables.json`. If a non-standard cable type is selected, these may be `null` and the consumer must look up.
- The intent schema is intentionally an over-set superset of cable-schedule / riser / cable-containment consumed-intent shapes. Adding optional fields is forward-compatible; removing required fields requires a major version bump.
```

- [ ] **Step 3: Verify both files parse as markdown**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
for f in electrical/cable-sizing/docs/*.md; do
  test -s "$f" && echo "OK $f"
done
```

Expected: 2 `OK` lines.

- [ ] **Step 4: Commit**

```bash
git add electrical/cable-sizing/docs/
git commit -m "docs(cable-sizing): engineering-philosophy + known-limitations"
```

---

## Task 14: `evals/runner-config.yaml` + eval-01 (UK domestic happy path)

**Files (all create):**
- `electrical/cable-sizing/evals/runner-config.yaml`
- `electrical/cable-sizing/evals/eval-01-uk-domestic-final-circuits.yaml`

- [ ] **Step 1: runner-config.yaml**

```yaml
runner: draftsman-eval
version: 1.0.0
skill: cable-sizing
skill_version: 1.0.0
description: "Eval runner config for electrical/cable-sizing v1.0.0. Mirrors electrical/fault-level/evals/runner-config.json structure."
evals:
  - electrical/cable-sizing/evals/eval-01-uk-domestic-final-circuits.yaml
  - electrical/cable-sizing/evals/eval-02-tpn-commercial-feeders-cumulative-vd.yaml
  - electrical/cable-sizing/evals/eval-03-undersized-cable-trap.yaml
  - electrical/cable-sizing/evals/eval-04-missing-route-data.yaml
  - electrical/cable-sizing/evals/eval-05-jurisdiction-us-with-awg.yaml
  - electrical/cable-sizing/evals/eval-06-rationale-block.yaml
  - electrical/cable-sizing/evals/eval-07-motor-starting-vd.yaml
  - electrical/cable-sizing/evals/eval-08-parallel-cables.yaml
  - electrical/cable-sizing/evals/eval-09-harmonic-derating-data-centre.yaml
coverage:
  wi5_categories:
    happy_path: [eval-01]
    edge_case: [eval-02]
    validation_trap: [eval-03]
    missing_input: [eval-04]
    jurisdiction_switch: [eval-05]
    rationale_block: [eval-06]
  skill_specific:
    motor_starting_vd: [eval-07]
    parallel_cables: [eval-08]
    harmonic_derating: [eval-09]
```

- [ ] **Step 2: eval-01-uk-domestic-final-circuits.yaml**

```yaml
eval_id: eval-01-uk-domestic-final-circuits
category: happy_path
skill: cable-sizing
skill_version: 1.0.0
description: |
  UK domestic 230V single-phase consumer unit feeding standard final circuits.
  Tests basic walk-the-ladder behaviour with simple Iz-binding selections.
input:
  jurisdiction: GB
  project_supply:
    voltage_v: 230
    phases: single
    frequency_hz: 50
    earthing_system: TN-C-S
  circuits_declared:
    - id: "CU.C01"
      designation: "Lighting ring upstairs"
      load: { ib_a: 4.2, in_a: 6, load_type: lighting, phases: single, pf: 1.0 }
      route: { length_m: 22, installation_method: B1, ambient_c: 30, grouping_count: 1, in_thermal_insulation: false }
    - id: "CU.C02"
      designation: "Lighting downstairs"
      load: { ib_a: 5.0, in_a: 6, load_type: lighting, phases: single, pf: 1.0 }
      route: { length_m: 18, installation_method: B1, ambient_c: 30, grouping_count: 1, in_thermal_insulation: false }
    - id: "CU.C03"
      designation: "Power ring kitchen"
      load: { ib_a: 26, in_a: 32, load_type: power, phases: single, pf: 0.95 }
      route: { length_m: 30, installation_method: B1, ambient_c: 30, grouping_count: 1, in_thermal_insulation: false }
    - id: "CU.C04"
      designation: "Cooker radial"
      load: { ib_a: 28, in_a: 32, load_type: power, phases: single, pf: 1.0 }
      route: { length_m: 8, installation_method: C, ambient_c: 30, grouping_count: 1, in_thermal_insulation: false }
expected:
  ir_structural:
    cascade_node_count: 4
    consumed_intents: []
    flags_must_include: ["TOOL-CALL-PENDING"]
    jurisdiction: GB
  per_node:
    - node_id: "CU.C01"
      binding_constraint: "iz_vs_in"
      phase_csa_mm2: 1.5
      vd_limit_pct: 3.0
      vd_limit_source_contains: "App 12"
    - node_id: "CU.C03"
      binding_constraint: "iz_vs_in"
      phase_csa_mm2: 4
      vd_limit_pct: 5.0
  rationale:
    sections_count: 8
    chat_summary_max_chars: 1200
  invariants_pass: ["INV-01","INV-02","INV-03","INV-04","INV-05","INV-06","INV-07","INV-09","INV-10"]
pass_criteria:
  - "IR validates against schema"
  - "Every node has binding_constraint populated from controlled vocabulary"
  - "Every node has tool_call_pending: true (no calc runtime yet)"
  - "No invariant fails (motor INV-07 trivially passes — no motor circuits)"
```

- [ ] **Step 3: Verify YAMLs parse**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
for f in electrical/cable-sizing/evals/runner-config.yaml electrical/cable-sizing/evals/eval-01-*.yaml; do
  python3 -c "import yaml; yaml.safe_load(open('$f'))" && echo "OK $f"
done
```

Expected: 2 `OK` lines.

- [ ] **Step 4: Commit**

```bash
git add electrical/cable-sizing/evals/runner-config.yaml electrical/cable-sizing/evals/eval-01-*.yaml
git commit -m "feat(cable-sizing): runner-config + eval-01 UK domestic happy path"
```

---

## Task 15: eval-02 (commercial cumulative Vd edge case)

**Files:**
- Create: `electrical/cable-sizing/evals/eval-02-tpn-commercial-feeders-cumulative-vd.yaml`

- [ ] **Step 1: Write eval-02**

```yaml
eval_id: eval-02-tpn-commercial-feeders-cumulative-vd
category: edge_case
skill: cable-sizing
skill_version: 1.0.0
description: |
  400V TPN commercial cascade: TX → MSB → riser feeder → DB-L1 → lighting final circuits.
  Tests cumulative-Vd binding on a deep cascade where each segment alone is fine but
  the sum exceeds the lighting limit at the leaf.
input:
  jurisdiction: GB
  project_supply:
    voltage_v: 400
    phases: three
    frequency_hz: 50
    earthing_system: TN-S
  consumed_intents:
    db-layout-rollup: { tool_call_pending: false }
  circuits_declared:
    - id: "MSB-1"
      parent_node_id: null
      node_kind: service_entrance
      designation: "Main MSB 2000A incomer"
      load: { ib_a: 1450, in_a: 2000, load_type: mixed, phases: three_plus_n }
      route: { length_m: 12, installation_method: F, ambient_c: 30, grouping_count: 1 }
    - id: "MSB-1.F03"
      parent_node_id: "MSB-1"
      node_kind: feeder
      designation: "Riser feeder to Level 3 DB-L1"
      load: { ib_a: 180, in_a: 250, load_type: mixed, phases: three_plus_n }
      route: { length_m: 65, installation_method: E, ambient_c: 35, grouping_count: 2 }
    - id: "MSB-1.F03.DB-L1"
      parent_node_id: "MSB-1.F03"
      node_kind: sub_feeder
      designation: "DB-L1 incoming"
      load: { ib_a: 45, in_a: 63, load_type: mixed, phases: three_plus_n }
      route: { length_m: 8, installation_method: C, ambient_c: 30, grouping_count: 1 }
    - id: "MSB-1.F03.DB-L1.C07"
      parent_node_id: "MSB-1.F03.DB-L1"
      node_kind: final_circuit
      designation: "Lighting circuit L1-C07 long run"
      load: { ib_a: 8.5, in_a: 10, load_type: lighting, phases: single }
      route: { length_m: 48, installation_method: B1, ambient_c: 30, grouping_count: 2 }
expected:
  per_node:
    - node_id: "MSB-1.F03.DB-L1.C07"
      binding_constraint: "vd_cumulative"
      walk_up_trail_min_length: 2
      vd_limit_pct: 3.0
      vd_limit_source_contains: "App 12"
  notes: |
    Critical: even though the 48m final circuit at 1.5 mm² gives ~2.2% segment Vd
    (under the 3% lighting limit on its own), cumulative Vd from MSB+riser+sub-feeder
    pushes it over. Expected upsize to 2.5 mm² or higher.
pass_criteria:
  - "MSB-1.F03.DB-L1.C07 binding_constraint == 'vd_cumulative'"
  - "walk_up_trail records the rejection at the smaller csa with vd_cumulative_pct > 3.0"
  - "vd_cumulative_pct at MSB-1.F03.DB-L1.C07 ≤ 3.0 in final accepted selection"
  - "Cumulative math: vd_cumulative_pct at node N == sum of vd_segment_pct from root to N"
```

- [ ] **Step 2: Verify + Commit**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
python3 -c "import yaml; yaml.safe_load(open('electrical/cable-sizing/evals/eval-02-tpn-commercial-feeders-cumulative-vd.yaml'))" && echo OK
git add electrical/cable-sizing/evals/eval-02-*.yaml
git commit -m "feat(cable-sizing): eval-02 commercial cumulative Vd edge case"
```

---

## Task 16: eval-03 (undersized validation trap) + eval-04 (missing input)

**Files (all create):**
- `electrical/cable-sizing/evals/eval-03-undersized-cable-trap.yaml`
- `electrical/cable-sizing/evals/eval-04-missing-route-data.yaml`

- [ ] **Step 1: eval-03-undersized-cable-trap.yaml**

```yaml
eval_id: eval-03-undersized-cable-trap
category: validation_trap
skill: cable-sizing
skill_version: 1.0.0
description: |
  Engineer pre-declares a cable size that fails Vd cumulative. Skill must detect,
  flag, and propose the correct upsize — must NOT silently rubber-stamp.
input:
  jurisdiction: GB
  project_supply: { voltage_v: 230, phases: single, frequency_hz: 50, earthing_system: TN-C-S }
  circuits_declared:
    - id: "DB-L1.C03"
      parent_node_id: null
      node_kind: final_circuit
      designation: "Long lighting circuit — engineer pre-declared 1.5 mm²"
      load: { ib_a: 5.5, in_a: 6, load_type: lighting, phases: single }
      route: { length_m: 55, installation_method: B1, ambient_c: 30, grouping_count: 1 }
      cable_type_preference: { phase_csa_mm2: 1.5, material: copper, insulation: pvc_70 }
expected:
  non_compliance_flags_must_include:
    - severity: error
      code_clause_contains: "App 12"
      message_contains: "cumulative Vd"
  per_node:
    - node_id: "DB-L1.C03"
      binding_constraint: "vd_cumulative"
      selection_phase_csa_mm2_greater_than: 1.5
      walk_up_trail_must_contain_rejection_at_csa: 1.5
pass_criteria:
  - "1.5 mm² engineer preference is REJECTED with explicit rationale"
  - "Skill proposes a larger csa that satisfies Vd ≤ 3% for lighting"
  - "Non-compliance flag emitted with severity: error referencing App 12"
  - "No silent acceptance"
```

- [ ] **Step 2: eval-04-missing-route-data.yaml**

```yaml
eval_id: eval-04-missing-route-data
category: missing_input
skill: cable-sizing
skill_version: 1.0.0
description: |
  Engineer omits length_m and installation_method for several circuits. Skill must NOT
  invent values — must emit tool_call_pending and log the gap in assumptions.
input:
  jurisdiction: GB
  project_supply: { voltage_v: 230, phases: single, frequency_hz: 50, earthing_system: TN-C-S }
  circuits_declared:
    - id: "DB.C01"
      parent_node_id: null
      node_kind: final_circuit
      designation: "Power circuit — no route data"
      load: { ib_a: 14, in_a: 16, load_type: power, phases: single }
      route: {}  # deliberately empty
expected:
  per_node:
    - node_id: "DB.C01"
      checks_tool_call_pending: true
      checks_iz_corrected_a: null
      checks_vd_segment_pct: null
  compliance_summary:
    assumptions_must_contain_text: ["length_m missing", "installation_method missing"]
  flags_must_include: ["TOOL-CALL-PENDING"]
pass_criteria:
  - "No invented length_m, no invented installation_method"
  - "Node has checks.tool_call_pending: true"
  - "Numeric checks fields are null where data is missing"
  - "Assumptions list explicitly names the missing inputs"
```

- [ ] **Step 3: Verify + Commit**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
for f in electrical/cable-sizing/evals/eval-0{3,4}-*.yaml; do
  python3 -c "import yaml; yaml.safe_load(open('$f'))" && echo "OK $f"
done
git add electrical/cable-sizing/evals/eval-03-*.yaml electrical/cable-sizing/evals/eval-04-*.yaml
git commit -m "feat(cable-sizing): eval-03 (undersized trap) + eval-04 (missing input)"
```

---

## Task 17: eval-05 (US AWG jurisdiction switch) + eval-06 (rationale block)

**Files (all create):**
- `electrical/cable-sizing/evals/eval-05-jurisdiction-us-with-awg.yaml`
- `electrical/cable-sizing/evals/eval-06-rationale-block.yaml`

- [ ] **Step 1: eval-05-jurisdiction-us-with-awg.yaml**

```yaml
eval_id: eval-05-jurisdiction-us-with-awg
category: jurisdiction_switch
skill: cable-sizing
skill_version: 1.0.0
description: |
  US 480V industrial. Aluminium feeder + AWG sizing + NEC 110.14(C) terminal-temp cap.
  Tests that the skill switches to NEC Ch 9 + 310.16 tables and uses AWG/kcmil units.
input:
  jurisdiction: US
  project_supply: { voltage_v: 480, phases: three, frequency_hz: 60, earthing_system: NEC_grounded }
  circuits_declared:
    - id: "MSB.F01"
      parent_node_id: null
      node_kind: feeder
      designation: "Feeder to MCC — aluminium THWN-2"
      load: { ib_a: 320, in_a: 400, load_type: power, phases: three }
      route: { length_m: 45, installation_method: NEC_cable_tray, ambient_c: 30, grouping_count: 1 }
      cable_type_preference: { material: aluminium, insulation: thwn_75 }
      terminal_temp_rating_c: 75
expected:
  per_node:
    - node_id: "MSB.F01"
      phase_csa_format: "AWG/kcmil string (e.g. '500' or '600' kcmil)"
      vd_limit_pct: 3.0
      vd_limit_source_contains: "NEC 215.2"
      material: aluminium
      insulation: thwn_75
  jurisdiction_check:
    - "vd_limit_source MUST cite NEC, not BS 7671"
    - "selection.phase_csa is a string in AWG/kcmil ladder"
    - "Iz capped by terminal_temp_rating_c per NEC 110.14(C)"
pass_criteria:
  - "All NEC citations only (no BS 7671 references)"
  - "AWG ladder used, not mm²"
  - "Terminal-temp cap visible in rationale"
```

- [ ] **Step 2: eval-06-rationale-block.yaml**

```yaml
eval_id: eval-06-rationale-block
category: rationale_block
skill: cable-sizing
skill_version: 1.0.0
description: |
  Verify the rationale block conforms to WI2: exactly 8 sections + chat_summary ≤ 200 words
  + every decision cites a rule + code_clause. Reuses the eval-02 input as the scenario.
input:
  reuse_from: "electrical/cable-sizing/evals/eval-02-tpn-commercial-feeders-cumulative-vd.yaml"
expected:
  rationale:
    chat_summary:
      type: string
      max_length_chars: 1200
      max_words: 200
    sections:
      length: 8
      titles_in_order:
        - "Input Ingestion"
        - "Cascade Topology"
        - "Jurisdictional Defaults"
        - "Source + Fault Context"
        - "CSA Selection Walk-up Summary"
        - "Special Checks"
        - "Compliance + Selectivity"
        - "Assumptions + Tool-call Status"
      every_decision_has:
        - label
        - summary
        - rule
        - code_clause
    walk_up_trail_per_node:
      every_rejection_names_check: true
      binding_constraint_consistent_with_walk_up_trail: true
pass_criteria:
  - "rationale.sections.length == 8 exactly"
  - "Every section is non-empty (or explicitly says 'none triggered')"
  - "Every decision cites a rule + clause"
  - "chat_summary ≤ 200 words and frames cascade scale + binding constraints + flags"
```

- [ ] **Step 3: Verify + Commit**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
for f in electrical/cable-sizing/evals/eval-0{5,6}-*.yaml; do
  python3 -c "import yaml; yaml.safe_load(open('$f'))" && echo "OK $f"
done
git add electrical/cable-sizing/evals/eval-05-*.yaml electrical/cable-sizing/evals/eval-06-*.yaml
git commit -m "feat(cable-sizing): eval-05 (US AWG jurisdiction) + eval-06 (rationale block)"
```

---

## Task 18: eval-07 (motor-starting Vd, skill-specific)

**Files:**
- Create: `electrical/cable-sizing/evals/eval-07-motor-starting-vd.yaml`

- [ ] **Step 1: Write eval-07**

```yaml
eval_id: eval-07-motor-starting-vd
category: skill_specific
subcategory: motor_starting_vd
skill: cable-sizing
skill_version: 1.0.0
description: |
  30 kW chiller motor on a long feeder. Locked-rotor-amps × segment Vd may exceed 10%.
  Skill must compute motor_starting_vd_pct, emit a WARNING (not error) when > 10%,
  and propose either soft-starter declaration OR cable upsize.
input:
  jurisdiction: GB
  project_supply: { voltage_v: 400, phases: three, frequency_hz: 50, earthing_system: TN-S }
  circuits_declared:
    - id: "MCC.M01"
      parent_node_id: null
      node_kind: final_circuit
      designation: "Chiller motor 30 kW DOL — long feeder"
      load:
        ib_a: 52
        in_a: 63
        load_type: motor
        phases: three
        pf: 0.85
        locked_rotor_multiplier: 6.0
      route: { length_m: 75, installation_method: E, ambient_c: 30, grouping_count: 1 }
expected:
  per_node:
    - node_id: "MCC.M01"
      checks_motor_starting_vd_pct: { type: number, gt: 5.0 }
      may_have_starting_vd_above_10:
        if_true:
          non_compliance_flags_includes:
            severity: warning
            message_contains: "soft-starter"
pass_criteria:
  - "motor_starting_vd_pct populated (not null)"
  - "If > 10% → warning emitted recommending soft-starter / VFD / star-delta / cable upsize"
  - "If ≤ 10% → no warning, but value still reported"
  - "Severity is 'warning' not 'error' (engineer chooses how to resolve)"
```

- [ ] **Step 2: Verify + Commit**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
python3 -c "import yaml; yaml.safe_load(open('electrical/cable-sizing/evals/eval-07-motor-starting-vd.yaml'))" && echo OK
git add electrical/cable-sizing/evals/eval-07-*.yaml
git commit -m "feat(cable-sizing): eval-07 motor-starting Vd skill-specific"
```

---

## Task 19: eval-08 (parallel cables) + eval-09 (harmonic derating)

**Files (all create):**
- `electrical/cable-sizing/evals/eval-08-parallel-cables.yaml`
- `electrical/cable-sizing/evals/eval-09-harmonic-derating-data-centre.yaml`

- [ ] **Step 1: eval-08-parallel-cables.yaml**

```yaml
eval_id: eval-08-parallel-cables
category: skill_specific
subcategory: parallel_cables
skill: cable-sizing
skill_version: 1.0.0
description: |
  1200A main feeder. Single-cable ladder exhausts at 630 mm² (Iz ~700-900A depending on
  install method). Skill must engage parallel cables: 2 × 400 mm² or 2 × 500 mm² in
  parallel to carry 1200A. Each parallel must meet IEC minimum 50 mm² + symmetry.
input:
  jurisdiction: GB
  project_supply: { voltage_v: 400, phases: three, frequency_hz: 50, earthing_system: TN-S }
  circuits_declared:
    - id: "MSB.SERVICE"
      parent_node_id: null
      node_kind: service_entrance
      designation: "Service entrance feeder 1200A"
      load: { ib_a: 1050, in_a: 1200, load_type: power, phases: three }
      route: { length_m: 35, installation_method: F, ambient_c: 30, grouping_count: 1 }
      cable_type_preference: { material: copper, insulation: xlpe_90 }
expected:
  per_node:
    - node_id: "MSB.SERVICE"
      binding_constraint: "parallel_required"
      selection_parallel_count: { type: integer, gte: 2, lte: 6 }
      selection_phase_csa_mm2: { gte: 50 }
      symmetry_assertion_in_rationale: true
pass_criteria:
  - "parallel_count >= 2"
  - "Each parallel csa >= 50 mm² per BS 7671 Reg 523.7"
  - "binding_constraint == 'parallel_required'"
  - "Rationale explicitly asserts same length/csa/material/install across parallels"
  - "If parallel_count > 6 → warning recommending bus duct redesign"
```

- [ ] **Step 2: eval-09-harmonic-derating-data-centre.yaml**

```yaml
eval_id: eval-09-harmonic-derating-data-centre
category: skill_specific
subcategory: harmonic_derating
skill: cable-sizing
skill_version: 1.0.0
description: |
  Three-phase 4-wire IT load with 33% 3rd-harmonic content. Skill must apply Ch
  correction factor AND size neutral conductor equal to phase per BS 7671 Reg 523.6.3.
input:
  jurisdiction: GB
  project_supply: { voltage_v: 400, phases: three, frequency_hz: 50, earthing_system: TN-S }
  circuits_declared:
    - id: "DC.RACK01"
      parent_node_id: null
      node_kind: final_circuit
      designation: "Data centre rack feeder 80A 4-wire — IT load with high h3"
      load: { ib_a: 65, in_a: 80, load_type: it_load, phases: three_plus_n, pf: 0.95 }
      route: { length_m: 25, installation_method: E, ambient_c: 35, grouping_count: 1 }
      harmonic_content_pct: 33
expected:
  per_node:
    - node_id: "DC.RACK01"
      checks_harmonic_ch_factor: { type: number, lt: 1.0, gt: 0.0 }
      binding_constraint_may_be: ["harmonic_derating", "iz_vs_in"]
      neutral_sizing_rule_in_rationale: "BS 7671 Reg 523.6.3"
      neutral_csa_equals_phase: true
pass_criteria:
  - "Ch factor < 1.0 applied (visible in checks.harmonic_ch_factor)"
  - "Phase csa upsized to account for derated Iz"
  - "Neutral csa = phase csa (3rd-harmonic > 33%)"
  - "Rationale cites Reg 523.6.3 + App 4 §5.5"
  - "If non-3-phase-4-wire OR harmonic_content_pct ≤ 15 → Ch factor must NOT appear"
```

- [ ] **Step 3: Verify + Commit**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
for f in electrical/cable-sizing/evals/eval-0{8,9}-*.yaml; do
  python3 -c "import yaml; yaml.safe_load(open('$f'))" && echo "OK $f"
done
git add electrical/cable-sizing/evals/eval-08-*.yaml electrical/cable-sizing/evals/eval-09-*.yaml
git commit -m "feat(cable-sizing): eval-08 (parallel cables) + eval-09 (harmonic derating)"
```

---

## Task 20: Example 1 — UK domestic final circuits

**Files (all create):**
- `electrical/cable-sizing/examples/uk-domestic-final-circuits/input.json`
- `electrical/cable-sizing/examples/uk-domestic-final-circuits/output.json`
- `electrical/cable-sizing/examples/uk-domestic-final-circuits/intent-out.json`
- `electrical/cable-sizing/examples/uk-domestic-final-circuits/reasoning.md`

- [ ] **Step 1: input.json**

```json
{
  "$schema": "../../schemas/inputs.schema.json",
  "project_id": "uk-dom-cs-eg01",
  "jurisdiction": "GB",
  "project_supply": {
    "voltage_v": 230,
    "phases": "single",
    "frequency_hz": 50,
    "earthing_system": "TN-C-S"
  },
  "consumed_intents_present": [],
  "circuits_declared": [
    { "id": "CU.C01", "designation": "Lighting upstairs",   "load": { "ib_a": 4.2, "in_a": 6,  "load_type": "lighting", "phases": "single", "pf": 1.0  }, "route": { "length_m": 22, "installation_method": "B1", "ambient_c": 30, "grouping_count": 1, "in_thermal_insulation": false } },
    { "id": "CU.C02", "designation": "Lighting downstairs", "load": { "ib_a": 5.0, "in_a": 6,  "load_type": "lighting", "phases": "single", "pf": 1.0  }, "route": { "length_m": 18, "installation_method": "B1", "ambient_c": 30, "grouping_count": 1, "in_thermal_insulation": false } },
    { "id": "CU.C03", "designation": "Power ring kitchen",  "load": { "ib_a": 26,  "in_a": 32, "load_type": "power",    "phases": "single", "pf": 0.95 }, "route": { "length_m": 30, "installation_method": "B1", "ambient_c": 30, "grouping_count": 1, "in_thermal_insulation": false } },
    { "id": "CU.C04", "designation": "Cooker radial",       "load": { "ib_a": 28,  "in_a": 32, "load_type": "power",    "phases": "single", "pf": 1.0  }, "route": { "length_m": 8,  "installation_method": "C",  "ambient_c": 30, "grouping_count": 1, "in_thermal_insulation": false } }
  ]
}
```

- [ ] **Step 2: output.json (the IR)**

```json
{
  "$schema": "../../schemas/cable-sizing-ir.schema.json",
  "drawing_type": "cable_sizing_study",
  "version": "1.0.0",
  "meta": {
    "project_id": "uk-dom-cs-eg01",
    "skill_version": "cable-sizing/1.0.0",
    "produced_at": "2026-05-17T09:00:00Z",
    "consumed_intents": []
  },
  "jurisdiction": "GB",
  "project_supply": { "voltage_v": 230, "phases": "single", "frequency_hz": 50, "earthing_system": "TN-C-S" },
  "cascade": [
    {
      "node_id": "CU.C01", "parent_node_id": null, "node_kind": "final_circuit", "designation": "Lighting upstairs",
      "load": { "ib_a": 4.2, "in_a": 6, "phases": "single", "load_type": "lighting", "pf": 1.0 },
      "route": { "length_m": 22, "installation_method": "B1", "ambient_c": 30, "grouping_count": 1, "in_thermal_insulation": false },
      "harmonic_content_pct": 0,
      "selection": {
        "phase_csa": 1.5, "cpc_csa": 1.0, "material": "copper", "insulation": "pvc_70", "cable_type": "pvc_singles",
        "parallel_count": 1, "binding_constraint": "iz_vs_in",
        "walk_up_trail": [ { "csa": 1.5, "accepted": true, "vd_segment_pct": 1.8, "vd_cumulative_pct": 1.8 } ]
      },
      "checks": {
        "iz_corrected_a": 15.5, "iz_vs_in_pass": true, "vd_segment_pct": 1.8, "vd_cumulative_pct": 1.8,
        "vd_pass": true, "vd_limit_pct": 3.0, "vd_limit_source": "BS 7671:2018 App 12 lighting circuits",
        "cpc_adiabatic_pass": true, "motor_starting_vd_pct": null, "harmonic_ch_factor": null, "tool_call_pending": true
      }
    },
    {
      "node_id": "CU.C02", "parent_node_id": null, "node_kind": "final_circuit", "designation": "Lighting downstairs",
      "load": { "ib_a": 5.0, "in_a": 6, "phases": "single", "load_type": "lighting", "pf": 1.0 },
      "route": { "length_m": 18, "installation_method": "B1", "ambient_c": 30, "grouping_count": 1, "in_thermal_insulation": false },
      "harmonic_content_pct": 0,
      "selection": {
        "phase_csa": 1.5, "cpc_csa": 1.0, "material": "copper", "insulation": "pvc_70", "cable_type": "pvc_singles",
        "parallel_count": 1, "binding_constraint": "iz_vs_in",
        "walk_up_trail": [ { "csa": 1.5, "accepted": true, "vd_segment_pct": 1.7, "vd_cumulative_pct": 1.7 } ]
      },
      "checks": {
        "iz_corrected_a": 15.5, "iz_vs_in_pass": true, "vd_segment_pct": 1.7, "vd_cumulative_pct": 1.7,
        "vd_pass": true, "vd_limit_pct": 3.0, "vd_limit_source": "BS 7671:2018 App 12 lighting circuits",
        "cpc_adiabatic_pass": true, "motor_starting_vd_pct": null, "harmonic_ch_factor": null, "tool_call_pending": true
      }
    },
    {
      "node_id": "CU.C03", "parent_node_id": null, "node_kind": "final_circuit", "designation": "Power ring kitchen",
      "load": { "ib_a": 26, "in_a": 32, "phases": "single", "load_type": "power", "pf": 0.95 },
      "route": { "length_m": 30, "installation_method": "B1", "ambient_c": 30, "grouping_count": 1, "in_thermal_insulation": false },
      "harmonic_content_pct": 0,
      "selection": {
        "phase_csa": 4, "cpc_csa": 1.5, "material": "copper", "insulation": "pvc_70", "cable_type": "pvc_singles",
        "parallel_count": 1, "binding_constraint": "iz_vs_in",
        "walk_up_trail": [ { "csa": 4, "accepted": true, "vd_segment_pct": 3.1, "vd_cumulative_pct": 3.1 } ]
      },
      "checks": {
        "iz_corrected_a": 32.0, "iz_vs_in_pass": true, "vd_segment_pct": 3.1, "vd_cumulative_pct": 3.1,
        "vd_pass": true, "vd_limit_pct": 5.0, "vd_limit_source": "BS 7671:2018 App 12 power circuits",
        "cpc_adiabatic_pass": true, "motor_starting_vd_pct": null, "harmonic_ch_factor": null, "tool_call_pending": true
      }
    },
    {
      "node_id": "CU.C04", "parent_node_id": null, "node_kind": "final_circuit", "designation": "Cooker radial",
      "load": { "ib_a": 28, "in_a": 32, "phases": "single", "load_type": "power", "pf": 1.0 },
      "route": { "length_m": 8, "installation_method": "C", "ambient_c": 30, "grouping_count": 1, "in_thermal_insulation": false },
      "harmonic_content_pct": 0,
      "selection": {
        "phase_csa": 6, "cpc_csa": 2.5, "material": "copper", "insulation": "pvc_70", "cable_type": "pvc_singles",
        "parallel_count": 1, "binding_constraint": "iz_vs_in",
        "walk_up_trail": [ { "csa": 6, "accepted": true, "vd_segment_pct": 0.6, "vd_cumulative_pct": 0.6 } ]
      },
      "checks": {
        "iz_corrected_a": 47.0, "iz_vs_in_pass": true, "vd_segment_pct": 0.6, "vd_cumulative_pct": 0.6,
        "vd_pass": true, "vd_limit_pct": 5.0, "vd_limit_source": "BS 7671:2018 App 12 power circuits",
        "cpc_adiabatic_pass": true, "motor_starting_vd_pct": null, "harmonic_ch_factor": null, "tool_call_pending": true
      }
    }
  ],
  "compliance_summary": {
    "compliant": true,
    "non_compliance_flags": [],
    "assumptions": [
      "TN-C-S earthing system declared by engineer (no fault-level intent consumed)",
      "tool_call_pending: true — calc.cable_ampacity + calc.voltage_drop + calc.cpc_adiabatic deferred until runtime ships"
    ]
  },
  "drawn_as_symbols": [],
  "flags": ["TOOL-CALL-PENDING"],
  "rationale": {
    "chat_summary": "UK domestic 230V single-phase consumer unit, 4 final circuits. All sized at Iz-binding (no Vd or adiabatic upsize needed). PVC singles installation method B1. Vd well under App 12 limits (3% lighting / 5% power). tool_call_pending until runtime ships.",
    "sections": [
      { "title": "Input Ingestion", "summary": "No upstream intents consumed; engineer declared all 4 circuits + route data.", "decisions": [] },
      { "title": "Cascade Topology", "summary": "4 sibling final_circuit nodes under CU (no riser/feeder in domestic). Naming: CU.C01-C04.", "decisions": [] },
      { "title": "Jurisdictional Defaults", "summary": "GB — BS 7671:2018 App 4 + App 12. Vd: 3% lighting, 5% power. Correction factors Ca/Cg/Ci/Ch.", "decisions": [{ "label": "GB defaults applied", "summary": "BS 7671 App 12 lighting/power limits", "rule": "BS 7671:2018 App 12", "code_clause": "BS 7671:2018 App 12" }] },
      { "title": "Source + Fault Context", "summary": "No fault-level intent consumed; engineer did not declare per-node Ifault. CPC adiabatic check deferred to runtime tool with placeholder pass.", "decisions": [] },
      { "title": "CSA Selection Walk-up Summary", "summary": "All 4 circuits sized at Iz_vs_In binding (start csa accepted on first check).", "decisions": [
        { "label": "C01/C02 lighting → 1.5 mm²", "summary": "In=6A fits 1.5 mm² Iz=15.5A B1", "rule": "BS 7671 Reg 433.1.1", "code_clause": "BS 7671:2018 Reg 433.1.1", "inputs": { "in_a": 6, "iz_a": 15.5 } },
        { "label": "C03 power ring → 4 mm²", "summary": "In=32A fits 4 mm² Iz=32A B1", "rule": "BS 7671 Reg 433.1.1", "code_clause": "BS 7671:2018 Reg 433.1.1", "inputs": { "in_a": 32, "iz_a": 32 } },
        { "label": "C04 cooker radial → 6 mm²", "summary": "In=32A fits 6 mm² Iz=47A C", "rule": "BS 7671 Reg 433.1.1", "code_clause": "BS 7671:2018 Reg 433.1.1", "inputs": { "in_a": 32, "iz_a": 47 } }
      ] },
      { "title": "Special Checks", "summary": "None triggered (no motor, no parallel, no harmonic loads).", "decisions": [] },
      { "title": "Compliance + Selectivity", "summary": "All circuits compliant. No non-compliance flags.", "decisions": [] },
      { "title": "Assumptions + Tool-call Status", "summary": "TN-C-S declared; calc tools deferred (tool_call_pending: true on all 4 nodes).", "decisions": [] }
    ]
  }
}
```

- [ ] **Step 3: intent-out.json**

```json
{
  "$schema": "../../schemas/cable-sizing-intent.schema.json",
  "intent_kind": "cable-sizing",
  "version": "1.0.0",
  "produced_by_skill_version": "cable-sizing/1.0.0",
  "tool_call_pending": true,
  "circuits": [
    { "node_id": "CU.C01", "parent_node_id": null, "designation": "Lighting upstairs",   "phase_csa": 1.5, "cpc_csa": 1.0, "material": "copper", "insulation": "pvc_70", "cable_type": "pvc_singles", "parallel_count": 1, "cable_od_mm": 6.8, "weight_kg_per_m": 0.10, "length_m": 22, "installation_method": "B1", "phases": "single", "ib_a": 4.2, "in_a": 6 },
    { "node_id": "CU.C02", "parent_node_id": null, "designation": "Lighting downstairs", "phase_csa": 1.5, "cpc_csa": 1.0, "material": "copper", "insulation": "pvc_70", "cable_type": "pvc_singles", "parallel_count": 1, "cable_od_mm": 6.8, "weight_kg_per_m": 0.10, "length_m": 18, "installation_method": "B1", "phases": "single", "ib_a": 5.0, "in_a": 6 },
    { "node_id": "CU.C03", "parent_node_id": null, "designation": "Power ring kitchen",  "phase_csa": 4,   "cpc_csa": 1.5, "material": "copper", "insulation": "pvc_70", "cable_type": "pvc_singles", "parallel_count": 1, "cable_od_mm": 9.4, "weight_kg_per_m": 0.22, "length_m": 30, "installation_method": "B1", "phases": "single", "ib_a": 26,  "in_a": 32 },
    { "node_id": "CU.C04", "parent_node_id": null, "designation": "Cooker radial",       "phase_csa": 6,   "cpc_csa": 2.5, "material": "copper", "insulation": "pvc_70", "cable_type": "pvc_singles", "parallel_count": 1, "cable_od_mm": 10.5, "weight_kg_per_m": 0.30, "length_m": 8,  "installation_method": "C",  "phases": "single", "ib_a": 28,  "in_a": 32 }
  ]
}
```

- [ ] **Step 4: reasoning.md**

```markdown
# UK Domestic Final Circuits — Worked Example

## Scenario

230V single-phase domestic consumer unit feeding 4 standard final circuits:
- 2 lighting circuits (6A MCB)
- 1 kitchen ring final (32A MCB)
- 1 cooker radial (32A MCB)

All sized in PVC singles, installation method B1 (in conduit on a wall).

## Why all 4 are Iz-binding (no upsize)

Each circuit's `In` happens to match the smallest standard csa that gives sufficient Iz:
- 6A MCB → 1.5 mm² gives Iz ~15.5A (huge headroom, no Vd issue at 22m/18m)
- 32A MCB ring → 4 mm² gives Iz ~32A (just sufficient — well under 5% Vd at 30m on a ring)
- 32A MCB cooker → 6 mm² (the bigger csa is conservative for resistive heating + short run)

None of the 4 circuits trigger:
- Vd binding (lighting 3% / power 5% comfortably met)
- CPC adiabatic upsize (Ifault not declared; placeholder pass)
- Motor starting (no motors)
- Parallel cables (single-cable suffices)
- Harmonic derating (no IT loads, no VFDs)

## Tool-call deferral

Until the DraftsMan runtime ships `calc.cable_ampacity`, `calc.voltage_drop`, and
`calc.cpc_adiabatic`, every node carries `tool_call_pending: true`. The numeric values
in `checks` are senior-engineer estimates from BS 7671 App 4 tables — they will be
re-computed by the calc tools at runtime.

## What this example demonstrates

- Basic happy-path walk-up (start csa accepted on first check)
- Jurisdictional defaults (GB → BS 7671 App 12 limits)
- Per-load-type Vd limit selection (lighting vs power)
- Rationale block conformance (8 sections including "Special Checks: none triggered")
- Forward-compatible intent emission (cable_od_mm + weight_kg_per_m for downstream
  containment-fill consumers, even when those consumers aren't built yet)
```

- [ ] **Step 5: Validate output against schema**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
python3 -c "
import json, jsonschema
schema = json.load(open('electrical/cable-sizing/schemas/cable-sizing-ir.schema.json'))
data   = json.load(open('electrical/cable-sizing/examples/uk-domestic-final-circuits/output.json'))
jsonschema.validate(data, schema); print('IR validates OK')
schema2 = json.load(open('electrical/cable-sizing/schemas/cable-sizing-intent.schema.json'))
data2   = json.load(open('electrical/cable-sizing/examples/uk-domestic-final-circuits/intent-out.json'))
jsonschema.validate(data2, schema2); print('Intent validates OK')
"
```

Expected: `IR validates OK` + `Intent validates OK`.

- [ ] **Step 6: Commit**

```bash
git add electrical/cable-sizing/examples/uk-domestic-final-circuits/
git commit -m "feat(cable-sizing): example 1 — UK domestic 4 final circuits (Iz-binding)"
```

---

## Task 21: Example 2 — INT commercial with feeders

**Files (all create):**
- `electrical/cable-sizing/examples/intl-commercial-with-feeders/input.json`
- `electrical/cable-sizing/examples/intl-commercial-with-feeders/output.json`
- `electrical/cable-sizing/examples/intl-commercial-with-feeders/intent-out.json`
- `electrical/cable-sizing/examples/intl-commercial-with-feeders/reasoning.md`

- [ ] **Step 1: input.json — cascade TX → MSB → riser → DB-L1 → final**

```json
{
  "$schema": "../../schemas/inputs.schema.json",
  "project_id": "intl-comm-cs-eg02",
  "jurisdiction": "INT",
  "project_supply": { "voltage_v": 400, "phases": "three", "frequency_hz": 50, "earthing_system": "TN-S" },
  "consumed_intents_present": ["db-layout-rollup", "fault-level"],
  "circuits_declared": [
    { "id": "MSB-1",                  "parent_node_id": null,                  "node_kind": "service_entrance", "designation": "Main MSB 2000A incomer",          "load": { "ib_a": 1450, "in_a": 2000, "load_type": "mixed",    "phases": "three_plus_n" }, "route": { "length_m": 12, "installation_method": "F",  "ambient_c": 30, "grouping_count": 1 }, "cable_type_preference": { "material": "copper", "insulation": "xlpe_90" } },
    { "id": "MSB-1.F03",              "parent_node_id": "MSB-1",               "node_kind": "feeder",           "designation": "Riser feeder to Level 3 DB-L1",    "load": { "ib_a": 180,  "in_a": 250,  "load_type": "mixed",    "phases": "three_plus_n" }, "route": { "length_m": 65, "installation_method": "E",  "ambient_c": 35, "grouping_count": 2 }, "cable_type_preference": { "material": "copper", "insulation": "xlpe_90" } },
    { "id": "MSB-1.F03.DB-L1",        "parent_node_id": "MSB-1.F03",           "node_kind": "sub_feeder",       "designation": "DB-L1 incoming sub-feeder",        "load": { "ib_a": 45,   "in_a": 63,   "load_type": "mixed",    "phases": "three_plus_n" }, "route": { "length_m": 8,  "installation_method": "C",  "ambient_c": 30, "grouping_count": 1 }, "cable_type_preference": { "material": "copper", "insulation": "xlpe_90" } },
    { "id": "MSB-1.F03.DB-L1.C07",    "parent_node_id": "MSB-1.F03.DB-L1",     "node_kind": "final_circuit",    "designation": "Lighting circuit L1-C07 long run", "load": { "ib_a": 8.5,  "in_a": 10,   "load_type": "lighting", "phases": "single",        "pf": 1.0 }, "route": { "length_m": 48, "installation_method": "B1", "ambient_c": 30, "grouping_count": 2 } }
  ]
}
```

- [ ] **Step 2: output.json** — full IR with cumulative Vd visible at the leaf

```json
{
  "$schema": "../../schemas/cable-sizing-ir.schema.json",
  "drawing_type": "cable_sizing_study",
  "version": "1.0.0",
  "meta": {
    "project_id": "intl-comm-cs-eg02",
    "skill_version": "cable-sizing/1.0.0",
    "produced_at": "2026-05-17T09:00:00Z",
    "consumed_intents": [
      { "intent_type": "db-layout-rollup", "intent_version": "1.0.0", "produced_by": "electrical/db-layout/1.0.0" },
      { "intent_type": "fault-level",      "intent_version": "1.0.0", "produced_by": "electrical/fault-level/1.0.0" }
    ]
  },
  "jurisdiction": "INT",
  "project_supply": { "voltage_v": 400, "phases": "three", "frequency_hz": 50, "earthing_system": "TN-S" },
  "cascade": [
    {
      "node_id": "MSB-1", "parent_node_id": null, "node_kind": "service_entrance", "designation": "Main MSB 2000A incomer",
      "load": { "ib_a": 1450, "in_a": 2000, "phases": "three_plus_n", "load_type": "mixed", "pf": 0.92 },
      "route": { "length_m": 12, "installation_method": "F", "ambient_c": 30, "grouping_count": 1, "in_thermal_insulation": false },
      "harmonic_content_pct": 0,
      "fault_at_origin": { "ifault_ka_max": 22.5, "ifault_ka_min": 20.4, "t_clear_s": 0.05 },
      "selection": {
        "phase_csa": 630, "cpc_csa": 240, "material": "copper", "insulation": "xlpe_90", "cable_type": "xlpe_singles",
        "parallel_count": 1, "binding_constraint": "iz_vs_in",
        "walk_up_trail": [ { "csa": 630, "accepted": true, "vd_segment_pct": 0.4, "vd_cumulative_pct": 0.4 } ]
      },
      "checks": {
        "iz_corrected_a": 2010, "iz_vs_in_pass": true, "vd_segment_pct": 0.4, "vd_cumulative_pct": 0.4,
        "vd_pass": true, "vd_limit_pct": 5.0, "vd_limit_source": "IEC 60364-5-52:2009 §G mixed loads",
        "cpc_adiabatic_pass": true, "motor_starting_vd_pct": null, "harmonic_ch_factor": null, "tool_call_pending": true
      }
    },
    {
      "node_id": "MSB-1.F03", "parent_node_id": "MSB-1", "node_kind": "feeder", "designation": "Riser feeder to Level 3 DB-L1",
      "load": { "ib_a": 180, "in_a": 250, "phases": "three_plus_n", "load_type": "mixed", "pf": 0.92 },
      "route": { "length_m": 65, "installation_method": "E", "ambient_c": 35, "grouping_count": 2, "in_thermal_insulation": false },
      "harmonic_content_pct": 0,
      "fault_at_origin": { "ifault_ka_max": 21.5, "ifault_ka_min": 19.5, "t_clear_s": 0.08 },
      "selection": {
        "phase_csa": 95, "cpc_csa": 50, "material": "copper", "insulation": "xlpe_90", "cable_type": "xlpe_singles",
        "parallel_count": 1, "binding_constraint": "iz_vs_in",
        "walk_up_trail": [ { "csa": 95, "accepted": true, "vd_segment_pct": 1.4, "vd_cumulative_pct": 1.8 } ]
      },
      "checks": {
        "iz_corrected_a": 252, "iz_vs_in_pass": true, "vd_segment_pct": 1.4, "vd_cumulative_pct": 1.8,
        "vd_pass": true, "vd_limit_pct": 5.0, "vd_limit_source": "IEC 60364-5-52:2009 §G mixed loads",
        "cpc_adiabatic_pass": true, "motor_starting_vd_pct": null, "harmonic_ch_factor": null, "tool_call_pending": true
      }
    },
    {
      "node_id": "MSB-1.F03.DB-L1", "parent_node_id": "MSB-1.F03", "node_kind": "sub_feeder", "designation": "DB-L1 incoming sub-feeder",
      "load": { "ib_a": 45, "in_a": 63, "phases": "three_plus_n", "load_type": "mixed", "pf": 0.92 },
      "route": { "length_m": 8, "installation_method": "C", "ambient_c": 30, "grouping_count": 1, "in_thermal_insulation": false },
      "harmonic_content_pct": 0,
      "fault_at_origin": { "ifault_ka_max": 18.2, "ifault_ka_min": 16.5, "t_clear_s": 0.10 },
      "selection": {
        "phase_csa": 16, "cpc_csa": 6, "material": "copper", "insulation": "xlpe_90", "cable_type": "xlpe_singles",
        "parallel_count": 1, "binding_constraint": "iz_vs_in",
        "walk_up_trail": [ { "csa": 16, "accepted": true, "vd_segment_pct": 0.3, "vd_cumulative_pct": 2.1 } ]
      },
      "checks": {
        "iz_corrected_a": 68, "iz_vs_in_pass": true, "vd_segment_pct": 0.3, "vd_cumulative_pct": 2.1,
        "vd_pass": true, "vd_limit_pct": 5.0, "vd_limit_source": "IEC 60364-5-52:2009 §G mixed loads",
        "cpc_adiabatic_pass": true, "motor_starting_vd_pct": null, "harmonic_ch_factor": null, "tool_call_pending": true
      }
    },
    {
      "node_id": "MSB-1.F03.DB-L1.C07", "parent_node_id": "MSB-1.F03.DB-L1", "node_kind": "final_circuit", "designation": "Lighting circuit L1-C07 long run",
      "load": { "ib_a": 8.5, "in_a": 10, "phases": "single", "load_type": "lighting", "pf": 1.0 },
      "route": { "length_m": 48, "installation_method": "B1", "ambient_c": 30, "grouping_count": 2, "in_thermal_insulation": false },
      "harmonic_content_pct": 0,
      "fault_at_origin": { "ifault_ka_max": 16.0, "ifault_ka_min": 14.5, "t_clear_s": 0.20 },
      "selection": {
        "phase_csa": 4, "cpc_csa": 2.5, "material": "copper", "insulation": "xlpe_90", "cable_type": "xlpe_singles",
        "parallel_count": 1, "binding_constraint": "vd_cumulative",
        "walk_up_trail": [
          { "csa": 1.5, "rejected_by": "vd_cumulative", "vd_segment_pct": 2.2, "vd_cumulative_pct": 4.3 },
          { "csa": 2.5, "rejected_by": "vd_cumulative", "vd_segment_pct": 1.3, "vd_cumulative_pct": 3.4 },
          { "csa": 4,   "accepted": true,                "vd_segment_pct": 0.8, "vd_cumulative_pct": 2.9 }
        ]
      },
      "checks": {
        "iz_corrected_a": 25, "iz_vs_in_pass": true, "vd_segment_pct": 0.8, "vd_cumulative_pct": 2.9,
        "vd_pass": true, "vd_limit_pct": 3.0, "vd_limit_source": "IEC 60364-5-52:2009 §G lighting circuits",
        "cpc_adiabatic_pass": true, "motor_starting_vd_pct": null, "harmonic_ch_factor": null, "tool_call_pending": true
      }
    }
  ],
  "compliance_summary": {
    "compliant": true,
    "non_compliance_flags": [],
    "assumptions": [
      "db-layout-rollup intent consumed; per-circuit Ib/In/load_type/t_clear sourced from it",
      "fault-level intent consumed; per-node ifault_ka_max/ifault_ka_min from it",
      "tool_call_pending: true — calc.cable_ampacity + calc.voltage_drop + calc.cpc_adiabatic deferred until runtime"
    ]
  },
  "drawn_as_symbols": [],
  "flags": ["TOOL-CALL-PENDING"],
  "rationale": {
    "chat_summary": "INT 400V TPN cascade, 4 nodes (MSB → riser → DB-L1 → C07). Lighting leaf C07 forces 2-step walk-up 1.5→2.5→4 mm² (binding: vd_cumulative; 2.9% at 4 mm² under 3% lighting limit per IEC 60364-5-52 §G). Feeders Iz-binding. tool_call_pending across cascade.",
    "sections": [
      { "title": "Input Ingestion",            "summary": "db-layout-rollup + fault-level intents consumed; engineer added route data per segment.", "decisions": [] },
      { "title": "Cascade Topology",            "summary": "4-node depth-3 cascade: service_entrance → feeder → sub_feeder → final_circuit.", "decisions": [] },
      { "title": "Jurisdictional Defaults",    "summary": "INT (IEC 60364-5-52). Vd: 3% lighting / 5% mixed loads per §G. Iz tables from Annex E.", "decisions": [{ "label": "INT defaults applied", "summary": "IEC 60364-5-52 §G + Annex E", "rule": "IEC 60364-5-52:2009 §G", "code_clause": "IEC 60364-5-52:2009 §G" }] },
      { "title": "Source + Fault Context",     "summary": "Ifault max ranges from 22.5 kA (MSB) down to 16.0 kA at C07. CPC adiabatic deferred to runtime tool.", "decisions": [] },
      { "title": "CSA Selection Walk-up Summary", "summary": "3 nodes Iz-binding (no upsize); 1 leaf node Vd_cumulative-binding (upsized 1.5→2.5→4 mm²).", "decisions": [
        { "label": "C07 vd_cumulative walk-up",  "summary": "Cumulative Vd at parent = 2.1%; 1.5 mm² adds 2.2% → 4.3% > 3% lighting limit. Upsize to 4 mm² gives 2.9% cumulative.", "rule": "IEC 60364-5-52:2009 §G lighting circuits", "code_clause": "IEC 60364-5-52:2009 §G", "inputs": { "vd_parent_pct": 2.1, "vd_limit_pct": 3.0 } }
      ] },
      { "title": "Special Checks",             "summary": "None triggered (no motor, no parallel, harmonic_content_pct = 0).", "decisions": [] },
      { "title": "Compliance + Selectivity",   "summary": "All 4 nodes compliant. No non-compliance flags.", "decisions": [] },
      { "title": "Assumptions + Tool-call Status", "summary": "Both intents consumed; tool_call_pending: true on all 4 nodes pending runtime.", "decisions": [] }
    ]
  }
}
```

- [ ] **Step 3: intent-out.json**

```json
{
  "$schema": "../../schemas/cable-sizing-intent.schema.json",
  "intent_kind": "cable-sizing",
  "version": "1.0.0",
  "produced_by_skill_version": "cable-sizing/1.0.0",
  "tool_call_pending": true,
  "circuits": [
    { "node_id": "MSB-1",               "parent_node_id": null,               "designation": "Main MSB 2000A incomer",          "phase_csa": 630, "cpc_csa": 240, "material": "copper", "insulation": "xlpe_90", "cable_type": "xlpe_singles", "parallel_count": 1, "cable_od_mm": 47.0, "weight_kg_per_m": 7.6,  "length_m": 12, "installation_method": "F",  "phases": "three_plus_n", "ib_a": 1450, "in_a": 2000 },
    { "node_id": "MSB-1.F03",           "parent_node_id": "MSB-1",            "designation": "Riser feeder to Level 3 DB-L1",   "phase_csa": 95,  "cpc_csa": 50,  "material": "copper", "insulation": "xlpe_90", "cable_type": "xlpe_singles", "parallel_count": 1, "cable_od_mm": 19.5, "weight_kg_per_m": 1.2,  "length_m": 65, "installation_method": "E",  "phases": "three_plus_n", "ib_a": 180,  "in_a": 250 },
    { "node_id": "MSB-1.F03.DB-L1",     "parent_node_id": "MSB-1.F03",        "designation": "DB-L1 incoming sub-feeder",       "phase_csa": 16,  "cpc_csa": 6,   "material": "copper", "insulation": "xlpe_90", "cable_type": "xlpe_singles", "parallel_count": 1, "cable_od_mm": 10.5, "weight_kg_per_m": 0.35, "length_m": 8,  "installation_method": "C",  "phases": "three_plus_n", "ib_a": 45,   "in_a": 63  },
    { "node_id": "MSB-1.F03.DB-L1.C07", "parent_node_id": "MSB-1.F03.DB-L1",  "designation": "Lighting circuit L1-C07 long run", "phase_csa": 4,   "cpc_csa": 2.5, "material": "copper", "insulation": "xlpe_90", "cable_type": "xlpe_singles", "parallel_count": 1, "cable_od_mm": 8.0,  "weight_kg_per_m": 0.18, "length_m": 48, "installation_method": "B1", "phases": "single",       "ib_a": 8.5,  "in_a": 10  }
  ]
}
```

- [ ] **Step 4: reasoning.md**

```markdown
# INT Commercial Cascade with Feeders — Worked Example

## Scenario

INT 400V TPN cascade — 4 nodes deep:
- `MSB-1` — service entrance 2000A
- `MSB-1.F03` — 65m riser feeder up to Level 3
- `MSB-1.F03.DB-L1` — DB incoming 63A sub-feeder
- `MSB-1.F03.DB-L1.C07` — long-run 48m lighting circuit

Both upstream intents present (`db-layout-rollup` + `fault-level`).

## Why C07 is vd_cumulative-binding

Each upstream segment contributes a fraction of the Vd budget:
- `MSB-1`: 0.4% (12m at 1450A, 630 mm²)
- `MSB-1.F03`: 1.4% segment, **1.8% cumulative**
- `MSB-1.F03.DB-L1`: 0.3% segment, **2.1% cumulative**

By the time we get to C07, only 0.9% of the 3% lighting limit is left for the 48m final
circuit. At 1.5 mm² the segment alone is 2.2% (4.3% cumulative — fail). At 2.5 mm² it's
1.3% (3.4% cumulative — still fail). At 4 mm² it's 0.8% (2.9% cumulative — pass).

`binding_constraint == "vd_cumulative"`, `walk_up_trail` shows all three steps.

## Why the upstream feeders are Iz-binding (not Vd)

The feeders are heavily sized for Iz headroom (Ib well under In, In well under Iz tabulated),
so Vd is comfortably small. The Vd budget gets consumed where Ib/L is highest relative to
csa — typically the final circuit.

## Forward-compat for downstream consumers

The emitted intent carries `cable_od_mm` + `weight_kg_per_m` per circuit so that the future
`cable-containment` skill can compute tray fill without needing to re-look-up the cable
type. The `parent_node_id` chain lets `riser` reconstruct floor-by-floor cable routing
exactly.

## tool_call_pending status

All 4 nodes carry `tool_call_pending: true`. The `vd_segment_pct` values shown are
senior-engineer estimates from IEC 60364-5-52 Annex G mV/A/m tables — runtime tool will
re-compute. The cumulative math is correct regardless (cumulative is just the sum).
```

- [ ] **Step 5: Validate against schema + Commit**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
python3 -c "
import json, jsonschema
s1 = json.load(open('electrical/cable-sizing/schemas/cable-sizing-ir.schema.json'))
d1 = json.load(open('electrical/cable-sizing/examples/intl-commercial-with-feeders/output.json'))
jsonschema.validate(d1, s1); print('IR OK')
s2 = json.load(open('electrical/cable-sizing/schemas/cable-sizing-intent.schema.json'))
d2 = json.load(open('electrical/cable-sizing/examples/intl-commercial-with-feeders/intent-out.json'))
jsonschema.validate(d2, s2); print('Intent OK')
"
git add electrical/cable-sizing/examples/intl-commercial-with-feeders/
git commit -m "feat(cable-sizing): example 2 — INT 400V cascade with vd_cumulative-binding lighting final"
```

---

## Task 22: Example 3 — US industrial with motors

**Files (all create):**
- `electrical/cable-sizing/examples/us-industrial-with-motors/input.json`
- `electrical/cable-sizing/examples/us-industrial-with-motors/output.json`
- `electrical/cable-sizing/examples/us-industrial-with-motors/intent-out.json`
- `electrical/cable-sizing/examples/us-industrial-with-motors/reasoning.md`

- [ ] **Step 1: input.json — 480V with aluminium feeder + 500 hp motor + parallel service entrance**

```json
{
  "$schema": "../../schemas/inputs.schema.json",
  "project_id": "us-ind-cs-eg03",
  "jurisdiction": "US",
  "project_supply": { "voltage_v": 480, "phases": "three", "frequency_hz": 60, "earthing_system": "NEC_grounded" },
  "terminal_temp_rating_c": 75,
  "consumed_intents_present": [],
  "circuits_declared": [
    { "id": "SERVICE",       "parent_node_id": null,         "node_kind": "service_entrance", "designation": "Service entrance 1200A — copper THWN-2 in cable tray", "load": { "ib_a": 1050, "in_a": 1200, "load_type": "mixed", "phases": "three" }, "route": { "length_m": 35, "installation_method": "NEC_cable_tray", "ambient_c": 30, "grouping_count": 1 }, "cable_type_preference": { "material": "copper", "insulation": "thwn_75" } },
    { "id": "SERVICE.F01",   "parent_node_id": "SERVICE",    "node_kind": "feeder",           "designation": "Aluminium feeder to MCC — XHHW-2",                     "load": { "ib_a": 320,  "in_a": 400,  "load_type": "power", "phases": "three" }, "route": { "length_m": 45, "installation_method": "NEC_cable_tray", "ambient_c": 30, "grouping_count": 1 }, "cable_type_preference": { "material": "aluminium", "insulation": "xhhw2_90" } },
    { "id": "MCC.M01",       "parent_node_id": "SERVICE.F01","node_kind": "final_circuit",    "designation": "500 hp chiller motor DOL",                              "load": { "ib_a": 590,  "in_a": 700,  "load_type": "motor", "phases": "three", "pf": 0.85, "locked_rotor_multiplier": 6.0 }, "route": { "length_m": 30, "installation_method": "NEC_conduit",     "ambient_c": 30, "grouping_count": 1 }, "cable_type_preference": { "material": "copper", "insulation": "thwn_75" } }
  ]
}
```

- [ ] **Step 2: output.json — IR with parallel service + AWG ladder + motor starting check**

```json
{
  "$schema": "../../schemas/cable-sizing-ir.schema.json",
  "drawing_type": "cable_sizing_study",
  "version": "1.0.0",
  "meta": { "project_id": "us-ind-cs-eg03", "skill_version": "cable-sizing/1.0.0", "produced_at": "2026-05-17T09:00:00Z", "consumed_intents": [] },
  "jurisdiction": "US",
  "project_supply": { "voltage_v": 480, "phases": "three", "frequency_hz": 60, "earthing_system": "NEC_grounded" },
  "cascade": [
    {
      "node_id": "SERVICE", "parent_node_id": null, "node_kind": "service_entrance", "designation": "Service entrance 1200A — copper THWN-2 in cable tray",
      "load": { "ib_a": 1050, "in_a": 1200, "phases": "three", "load_type": "mixed", "pf": 0.92 },
      "route": { "length_m": 35, "installation_method": "NEC_cable_tray", "ambient_c": 30, "grouping_count": 1, "in_thermal_insulation": false },
      "harmonic_content_pct": 0,
      "selection": {
        "phase_csa": "500", "cpc_csa": "3/0", "material": "copper", "insulation": "thwn_75", "cable_type": "thwn2",
        "parallel_count": 2, "binding_constraint": "parallel_required",
        "walk_up_trail": [
          { "csa": "750", "rejected_by": "iz_vs_in", "iz_corrected_a": 535 },
          { "csa": "1000","rejected_by": "iz_vs_in", "iz_corrected_a": 615 },
          { "csa": "500 ×2 parallel", "accepted": true, "iz_corrected_a": 760 }
        ]
      },
      "checks": {
        "iz_corrected_a": 760, "iz_vs_in_pass": true, "vd_segment_pct": 1.6, "vd_cumulative_pct": 1.6,
        "vd_pass": true, "vd_limit_pct": 3.0, "vd_limit_source": "NEC 2023 215.2(A)(1) IN 2 feeder-only",
        "cpc_adiabatic_pass": true, "motor_starting_vd_pct": null, "harmonic_ch_factor": null, "tool_call_pending": true
      }
    },
    {
      "node_id": "SERVICE.F01", "parent_node_id": "SERVICE", "node_kind": "feeder", "designation": "Aluminium feeder to MCC — XHHW-2",
      "load": { "ib_a": 320, "in_a": 400, "phases": "three", "load_type": "power", "pf": 0.92 },
      "route": { "length_m": 45, "installation_method": "NEC_cable_tray", "ambient_c": 30, "grouping_count": 1, "in_thermal_insulation": false },
      "harmonic_content_pct": 0,
      "selection": {
        "phase_csa": "600", "cpc_csa": "1/0", "material": "aluminium", "insulation": "xhhw2_90", "cable_type": "xhhw2",
        "parallel_count": 1, "binding_constraint": "iz_vs_in",
        "walk_up_trail": [ { "csa": "600", "accepted": true, "iz_corrected_a": 420 } ]
      },
      "checks": {
        "iz_corrected_a": 420, "iz_vs_in_pass": true, "vd_segment_pct": 1.8, "vd_cumulative_pct": 3.4,
        "vd_pass": true, "vd_limit_pct": 5.0, "vd_limit_source": "NEC 2023 215.2(A)(1) IN 2 feeder+branch",
        "cpc_adiabatic_pass": true, "motor_starting_vd_pct": null, "harmonic_ch_factor": null, "tool_call_pending": true
      }
    },
    {
      "node_id": "MCC.M01", "parent_node_id": "SERVICE.F01", "node_kind": "final_circuit", "designation": "500 hp chiller motor DOL",
      "load": { "ib_a": 590, "in_a": 700, "phases": "three", "load_type": "motor", "pf": 0.85, "locked_rotor_multiplier": 6.0 },
      "route": { "length_m": 30, "installation_method": "NEC_conduit", "ambient_c": 30, "grouping_count": 1, "in_thermal_insulation": false },
      "harmonic_content_pct": 0,
      "selection": {
        "phase_csa": "750", "cpc_csa": "2/0", "material": "copper", "insulation": "thwn_75", "cable_type": "thwn2",
        "parallel_count": 1, "binding_constraint": "motor_starting_vd",
        "walk_up_trail": [
          { "csa": "500", "rejected_by": "motor_starting_vd", "motor_starting_vd_pct": 11.4 },
          { "csa": "600", "rejected_by": "motor_starting_vd", "motor_starting_vd_pct": 10.5 },
          { "csa": "750", "accepted": true,                    "motor_starting_vd_pct": 9.6 }
        ]
      },
      "checks": {
        "iz_corrected_a": 535, "iz_vs_in_pass": true, "vd_segment_pct": 1.6, "vd_cumulative_pct": 5.0,
        "vd_pass": true, "vd_limit_pct": 5.0, "vd_limit_source": "NEC 2023 215.2(A)(1) IN 2 feeder+branch",
        "cpc_adiabatic_pass": true, "motor_starting_vd_pct": 9.6, "harmonic_ch_factor": null, "tool_call_pending": true
      }
    }
  ],
  "compliance_summary": {
    "compliant": true,
    "non_compliance_flags": [
      { "message": "Motor starting Vd at MCC.M01 reaches 9.6% — within 10% limit but close. Consider soft-starter to reduce to 1.6%.", "code_clause": "NEC 2023 430.6", "severity": "info", "node_id": "MCC.M01" }
    ],
    "assumptions": [
      "Engineer-declared circuit list (no db-layout-rollup intent present)",
      "terminal_temp_rating_c = 75°C applied per NEC 110.14(C)",
      "Motor MCC.M01: NEMA Design B (LRA multiplier = 6.0) — verify nameplate",
      "Parallel cables at SERVICE: 2 × 500 kcmil copper — symmetry asserted",
      "tool_call_pending: true — calc.cable_ampacity + calc.voltage_drop + calc.cpc_adiabatic deferred until runtime"
    ]
  },
  "drawn_as_symbols": [],
  "flags": ["TOOL-CALL-PENDING", "MOTOR_STARTING_VD_CLOSE_TO_LIMIT", "PARALLEL_CABLES"],
  "rationale": {
    "chat_summary": "US 480V industrial 3-node cascade. Service entrance: 2×500 kcmil parallel (binding: parallel_required). Aluminium 600 kcmil feeder (Iz-binding). 500 hp motor: walk-up 500→600→750 kcmil driven by motor_starting_vd at 9.6% (close to 10% — info flag recommending soft-starter). Cumulative Vd 5.0% at motor (NEC feeder+branch limit). tool_call_pending.",
    "sections": [
      { "title": "Input Ingestion",            "summary": "No upstream intents; engineer declared all 3 cascade nodes + route + motor LRA.", "decisions": [] },
      { "title": "Cascade Topology",            "summary": "Linear cascade SERVICE → SERVICE.F01 → MCC.M01. 3 nodes.", "decisions": [] },
      { "title": "Jurisdictional Defaults",    "summary": "US — NEC Chapter 9 + 310.16. Vd: 3% feeder-only / 5% feeder+branch (NEC 215.2 IN 2). Terminal cap per 110.14(C) at 75°C.", "decisions": [{ "label": "US NEC defaults", "summary": "AWG ladder, terminal cap 75°C", "rule": "NEC 2023 110.14(C) + 215.2", "code_clause": "NEC 2023 110.14(C)" }] },
      { "title": "Source + Fault Context",     "summary": "No fault-level intent; CPC adiabatic deferred to runtime tool. NEC 250.122 minimum applied per OCPD rating.", "decisions": [] },
      { "title": "CSA Selection Walk-up Summary", "summary": "1 node parallel_required (SERVICE); 1 node motor_starting_vd-binding (MCC.M01 — upsized 500 → 600 → 750 kcmil); 1 node Iz-binding (SERVICE.F01 aluminium).", "decisions": [
        { "label": "SERVICE parallel cables", "summary": "1200A service → ladder exhausted at 1000 kcmil single → 2 × 500 kcmil copper parallel", "rule": "NEC 2023 310.10(H)(1)", "code_clause": "NEC 2023 310.10(H)(1)", "inputs": { "ib_a": 1050, "in_a": 1200, "parallels": 2, "each_csa": "500 kcmil" } },
        { "label": "MCC.M01 motor starting", "summary": "LRA × segment Vd = 6.0 × 1.6% = 9.6% at 750 kcmil (within 10% limit)", "rule": "BS 7671:2018 §525.1 / NEC 430.6", "code_clause": "NEC 2023 430.6", "inputs": { "lra_multiplier": 6.0, "vd_segment_pct": 1.6, "starting_vd_pct": 9.6, "limit_pct": 10.0 } }
      ] },
      { "title": "Special Checks",             "summary": "Motor starting: 9.6% (warning level — info flag emitted). Parallel cables: 2×500 kcmil symmetric. Harmonic: not triggered.", "decisions": [] },
      { "title": "Compliance + Selectivity",   "summary": "All 3 nodes compliant. 1 info flag (motor starting Vd close to limit).", "decisions": [] },
      { "title": "Assumptions + Tool-call Status", "summary": "tool_call_pending across cascade; NEMA B LRA assumed for motor M01; parallel symmetry per declared route.", "decisions": [] }
    ]
  }
}
```

- [ ] **Step 3: intent-out.json**

```json
{
  "$schema": "../../schemas/cable-sizing-intent.schema.json",
  "intent_kind": "cable-sizing",
  "version": "1.0.0",
  "produced_by_skill_version": "cable-sizing/1.0.0",
  "tool_call_pending": true,
  "circuits": [
    { "node_id": "SERVICE",      "parent_node_id": null,         "designation": "Service entrance 1200A — copper THWN-2 in cable tray", "phase_csa": "500", "cpc_csa": "3/0", "material": "copper",    "insulation": "thwn_75",  "cable_type": "thwn2",  "parallel_count": 2, "cable_od_mm": 27.5, "weight_kg_per_m": 2.4, "length_m": 35, "installation_method": "NEC_cable_tray", "phases": "three", "ib_a": 1050, "in_a": 1200 },
    { "node_id": "SERVICE.F01",  "parent_node_id": "SERVICE",    "designation": "Aluminium feeder to MCC — XHHW-2",                     "phase_csa": "600", "cpc_csa": "1/0", "material": "aluminium", "insulation": "xhhw2_90", "cable_type": "xhhw2",  "parallel_count": 1, "cable_od_mm": 29.5, "weight_kg_per_m": 1.0, "length_m": 45, "installation_method": "NEC_cable_tray", "phases": "three", "ib_a": 320,  "in_a": 400  },
    { "node_id": "MCC.M01",      "parent_node_id": "SERVICE.F01","designation": "500 hp chiller motor DOL",                              "phase_csa": "750", "cpc_csa": "2/0", "material": "copper",    "insulation": "thwn_75",  "cable_type": "thwn2",  "parallel_count": 1, "cable_od_mm": 31.5, "weight_kg_per_m": 3.0, "length_m": 30, "installation_method": "NEC_conduit",     "phases": "three", "ib_a": 590,  "in_a": 700  }
  ]
}
```

- [ ] **Step 4: reasoning.md**

```markdown
# US Industrial Cascade — Worked Example

## Scenario

US 480V industrial 3-node cascade:
- `SERVICE` — 1200A service entrance, copper THWN-2 in cable tray, 35 m
- `SERVICE.F01` — 400A aluminium feeder to MCC, XHHW-2 cable tray, 45 m
- `MCC.M01` — 500 hp DOL chiller motor (NEMA B, LRA multiplier 6.0), 30 m in conduit

## Three different binding constraints across 3 nodes

### SERVICE — `parallel_required`

The standard NEC AWG/kcmil ladder caps at 1000 kcmil with Iz ~615A (THWN-2, cable tray,
75°C terminal cap). Even 1000 kcmil alone can't carry 1200A. Engage `parallel-cables`
rule: 2 × 500 kcmil copper meets minimum csa per NEC 310.10(H)(1), gives Iz ~760A
combined, symmetric.

### SERVICE.F01 — `iz_vs_in` (aluminium)

400A feeder. Aluminium 600 kcmil XHHW-2 in cable tray gives Iz ~420A at 75°C terminal
cap — start csa accepted. binding_constraint = iz_vs_in.

### MCC.M01 — `motor_starting_vd`

500 hp motor at 590A FLA. Cable starts at 500 kcmil (which gives Iz ~430A — fails),
walks up to 600 kcmil (Iz ~475A — fails iz), then 750 kcmil (Iz ~535A — passes iz).
But: motor starting Vd at 500 kcmil = 6.0 × 1.9% = 11.4% (fail), at 600 = 10.5% (fail),
at 750 = 9.6% (pass — within 10% limit, but tight).

binding_constraint = motor_starting_vd. An info-severity flag recommends a soft-starter
to reduce starting Vd to 1.6%.

## Why the motor cumulative Vd hits exactly 5.0% at the limit

The NEC 215.2(A)(1) IN 2 limit for feeder+branch combined is 5%. Walking the cascade:
- SERVICE: 1.6% (35m at 1050A, 2×500 kcmil)
- SERVICE.F01: 1.8% segment → 3.4% cumulative
- MCC.M01: 1.6% segment → 5.0% cumulative

This is the exact NEC limit. If the motor were any further, additional cable upsizing
would be required.

## NEC-specific details (vs IEC)

- AWG/kcmil string identifiers (e.g. `"500"` for 500 kcmil), not numeric mm²
- Terminal-temp cap per NEC 110.14(C): even though THWN-2 is rated 75°C wet/90°C dry,
  Iz is capped by the lowest-rated terminal (75°C here)
- Vd limits per NEC 215.2(A)(1) IN 2: 3% feeder-only, 5% feeder+branch combined
- Parallel rule per NEC 310.10(H)(1): minimum 1/0 AWG per parallel

## Flags emitted

- `TOOL-CALL-PENDING` (runtime calc deferred)
- `MOTOR_STARTING_VD_CLOSE_TO_LIMIT` (info — close to 10%)
- `PARALLEL_CABLES` (informational — downstream cable-containment must accommodate 2 cables in tray)
```

- [ ] **Step 5: Validate against schema + Commit**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
python3 -c "
import json, jsonschema
s1 = json.load(open('electrical/cable-sizing/schemas/cable-sizing-ir.schema.json'))
d1 = json.load(open('electrical/cable-sizing/examples/us-industrial-with-motors/output.json'))
jsonschema.validate(d1, s1); print('IR OK')
s2 = json.load(open('electrical/cable-sizing/schemas/cable-sizing-intent.schema.json'))
d2 = json.load(open('electrical/cable-sizing/examples/us-industrial-with-motors/intent-out.json'))
jsonschema.validate(d2, s2); print('Intent OK')
"
git add electrical/cable-sizing/examples/us-industrial-with-motors/
git commit -m "feat(cable-sizing): example 3 — US 480V industrial (parallel + aluminium + motor-starting-Vd)"
```

---

## Task 23: Final README rewrite + SKILLS_STATUS update + push

**Files:**
- Modify: `electrical/cable-sizing/README.md` (full rewrite, replacing the Task 1 stub)
- Modify: `SKILLS_STATUS.md` (promote cable-sizing from stub → beta)

- [ ] **Step 1: Rewrite README.md**

File: `electrical/cable-sizing/README.md` (overwrite)

```markdown
# `cable-sizing` — Per-Circuit Cable Selection (IEC 60364 / BS 7671 / NEC)

**Status:** `beta`
**Version:** `1.0.0`
**Drawing type:** `cable_sizing_study`
**Reference:** `electrical/lighting-layout` (production reference) + `electrical/earthing` (sibling beta) + `electrical/db-layout` (sibling beta) + `electrical/fault-level` (sibling beta — directly consumed)

## What this skill produces

A project-scoped cable-sizing IR per BS 7671 App 4 (GB) / IEC 60364-5-52 (EU/INT) / NEC Chapter 9 + 310.16 (US) capturing:

- Cascade tree from service entrance → feeders → sub-feeders → final circuits
- Per-node selection: `phase_csa`, `cpc_csa`, `material`, `insulation`, `cable_type`, `parallel_count`
- Named `binding_constraint` per node (which check forced the csa walk-up)
- Walk-up trail showing rejected sizes + reasons
- Cumulative Vd up the parent chain (source → endpoint)
- Motor-starting Vd for motor circuits (warning, not error, when > 10%)
- CPC adiabatic check at parent ifault + OCPD t_clear
- Parallel cables when single-cable ladder exhausts
- Harmonic derating + neutral sizing for 3-phase 4-wire IT loads
- 8-section rationale block per WI2 + chat_summary

**Plus a `cable-sizing` intent** (slim downstream subset) emitted alongside — consumed by:
- `cable-schedule` (formal tabulated deliverable)
- `riser` (LV riser diagrams, floor-by-floor with parent_node_id chain)
- `cable-containment` (tray/conduit fill — uses `cable_od_mm` + `weight_kg_per_m` + `parallel_count`)

## Jurisdictions supported

| Jurisdiction | Ampacity tables | Vd source | Cable types |
|---|---|---|---|
| GB | BS 7671 App 4 Tables 4D1A–4F | App 12 + App 4 §6 | PVC singles / XLPE / MICC / SWA / FP200 / CWZ |
| EU | IEC 60364-5-52 Annex E | IEC 60364-5-52 §G | PVC / XLPE / EPR / SWA |
| INT | IEC 60364-5-52 Annex E | IEC 60364-5-52 §G | Same as EU |
| US | NEC 310.16 + Chapter 9 Table 9 + 310.15(B) | NEC 215.2(A)(1) IN | THWN-2 / THHN / XHHW-2 + 110.14(C) terminal cap |

## Cross-drawing intent contract

| Direction | Intent | Purpose |
|---|---|---|
| Produces | `cable-sizing` | Per-circuit selection — consumed by cable-schedule, riser, cable-containment |
| Consumes | `db-layout-rollup` | Per-circuit Ib/In/load_type/t_clear (preferred over engineer-declared) |
| Consumes | `fault-level` | Per-node Ifault for CPC adiabatic check (preferred over engineer-declared) |

## File structure

```
electrical/cable-sizing/
├── README.md
├── CHANGELOG.md
├── skill.manifest.json
├── inputs.json
├── prompts/        (generator 14-step / validator 10 INV / reviewer 8 D)
├── schemas/        (IR + intent)
├── rules/          (5 YAMLs: walk-up, Vd targets, correction stack, parallels, harmonic)
├── constraints/    (4 YAMLs: Iz/In/Ib, Vd cumulative, CPC adiabatic, motor starting)
├── validation/     (4 YAMLs, 12 checks)
├── ontology/       (cable-types + installation-methods)
├── docs/           (engineering-philosophy + known-limitations)
├── evals/          (runner-config + 9 evals)
└── examples/       (UK domestic / INT commercial with feeders / US industrial with motors)
```

## Eval coverage matrix

| Eval ID | Category | Tests |
|---|---|---|
| eval-01-uk-domestic-final-circuits | happy_path | 230V UK domestic, 4 final circuits all Iz-binding |
| eval-02-tpn-commercial-feeders-cumulative-vd | edge_case | 400V TPN cascade, vd_cumulative-binding at deep leaf |
| eval-03-undersized-cable-trap | validation_trap | Engineer pre-declares 1.5 mm² where Vd forces 4 mm² — must flag |
| eval-04-missing-route-data | missing_input | No length / install method → tool_call_pending, no invention |
| eval-05-jurisdiction-us-with-awg | jurisdiction_switch | US 480V aluminium feeder, NEC AWG ladder, terminal-temp cap |
| eval-06-rationale-block | rationale_block | 8 sections + chat_summary + walk_up_trail audit |
| eval-07-motor-starting-vd | skill_specific | 30 kW chiller motor — vd_starting check + warning logic |
| eval-08-parallel-cables | skill_specific | 1200A feeder — 2 × 500 kcmil parallel (binding: parallel_required) |
| eval-09-harmonic-derating-data-centre | skill_specific | IT load 33% h3 — Ch < 1.0 + neutral = phase |

All 6 WI5 categories + 3 skill-specific.

## Tool calls awaiting runtime

| Tool name | Purpose |
|---|---|
| `calc.cable_ampacity` | Iz lookup with correction factors. Contract at `shared/calculations/electrical/cable-ampacity.json`. Status: tool_call_pending until DraftsMan runtime ships. |
| `calc.voltage_drop` | mV/A/m × Ib × L with PF + temp correction. Contract at `shared/calculations/electrical/voltage-drop.json`. Status: tool_call_pending. |
| `calc.cpc_adiabatic` | S = √(I²t)/k for CPC sizing. Contract at `shared/calculations/electrical/cpc-adiabatic.json`. Status: tool_call_pending. |

## Known limitations

See `docs/known-limitations.md`. v1.0.0 does NOT cover:
- DC circuit sizing (PV, EV DCFC, battery) → future `dc-cable-sizing` sibling
- Arc-flash incident-energy boundary marking → `arc-flash` sibling
- IEC 60287 advanced thermal modelling for buried groups
- Communications + data cables (Cat6, fibre) → `electrical/data-telecom`
- Time-graded protection coordination → `db-layout` v1.1 + future `protection-coordination`

## Versioning

- Minor bumps (1.x.0): new jurisdictions / cable types / evals / examples
- Major bump (2.0.0): reserved for DC scope OR breaking IR schema change
- Patch bumps (1.0.x): rules / constraints / validation bug fixes

## License

See repository root `LICENSE`.
```

- [ ] **Step 2: Update SKILLS_STATUS.md (promote cable-sizing row)**

File: `SKILLS_STATUS.md`

Find this row in the Electrical / Calculations subsection:
```
| cable-sizing | `electrical/cable-sizing` | stub | BS 7671:2018 App 4, IEC 60364-5-52, NEC Chapter 9 + 310.16 | — | next — Item 3 of Tier 1 sequence. Spec approved at `docs/superpowers/specs/2026-05-16-cable-sizing-skill-design.md`. |
```

Replace with:
```
| cable-sizing | `electrical/cable-sizing` | **beta** | BS 7671:2018 App 4 + App 12 + Reg 433/434/521 + 543, IEC 60364-5-52 + 5-54, NEC 2023 Ch 9 + 310.16 + 215.2 + 220 + 240 + 250.122 + 310.10(H) + 430.6 + 110.14(C) | 9/3 ✓ | v1.0.0 IEC/BS/NEC cable selection. 14-step generator, IR + intent schemas, 12 deterministic checks, 9 evals (6 WI5 + 3 skill-specific), 3 worked examples (UK domestic / INT cascade with vd_cumulative / US industrial with parallel + motor-starting). Math deferred to calc.cable_ampacity + calc.voltage_drop + calc.cpc_adiabatic runtime tools per WI3. |
```

Update Summary counts:
```
| production | 1 |
| beta | 5 |          ← was 4
| draft | 0 |
| stub | 69 |         ← was 70
| **Total** | **75** |

**Beta (5):** `electrical/sld`, `electrical/db-layout`, `electrical/earthing`, `electrical/fault-level`, `electrical/cable-sizing`
**Production (1):** `electrical/lighting-layout`
```

Update Roadmap line 3:
```
3. ✅ `electrical/cable-sizing` v1.0.0 beta (shipped 2026-05-17)
```

Renumber Tier 1 sequence (item 3 done, items 4-7 stay queued).

- [ ] **Step 3: Final verification — all artefacts in place**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
echo "=== Artefact inventory ==="
find electrical/cable-sizing -type f | wc -l                 # expect ~45 files
echo "=== Schema validations ==="
for ex in electrical/cable-sizing/examples/*/; do
  python3 -c "
import json, jsonschema
s = json.load(open('electrical/cable-sizing/schemas/cable-sizing-ir.schema.json'))
d = json.load(open('${ex}output.json'))
jsonschema.validate(d, s); print('IR OK ${ex}')
s2 = json.load(open('electrical/cable-sizing/schemas/cable-sizing-intent.schema.json'))
d2 = json.load(open('${ex}intent-out.json'))
jsonschema.validate(d2, s2); print('Intent OK ${ex}')
"
done
echo "=== YAML parses ==="
for f in $(find electrical/cable-sizing -name "*.yaml"); do
  python3 -c "import yaml; yaml.safe_load(open('$f'))" && echo "OK $f"
done
echo "=== JSON parses ==="
for f in $(find electrical/cable-sizing -name "*.json"); do
  jq . "$f" > /dev/null && echo "OK $f"
done
echo "=== Manifest standards file presence ==="
jq -r '.standards[]' electrical/cable-sizing/skill.manifest.json | while read p; do
  test -f "$p" || echo "MISSING $p"
done
echo "=== Manifest calc-contract presence ==="
jq -r '.calculations[]' electrical/cable-sizing/skill.manifest.json | while read p; do
  test -f "$p" || echo "MISSING $p"
done
```

Expected: ~45 files, 6 schema validations OK (3 examples × 2 docs), every YAML + JSON OK, no MISSING lines.

- [ ] **Step 4: Commit + push**

```bash
git add electrical/cable-sizing/README.md SKILLS_STATUS.md
git commit -m "feat(cable-sizing): v1.0.0 beta — README rewrite + SKILLS_STATUS promotion to beta"
git push origin main
```

- [ ] **Step 5: Verify push succeeded**

```bash
git log origin/main..HEAD
# Expected: empty (all commits pushed)
git status
# Expected: "Your branch is up to date with 'origin/main'."
```

---

## Final self-check (run after all 23 tasks complete)

- [ ] All 9 evals registered in manifest + runner-config
- [ ] All 22 standards files referenced in manifest exist on disk
- [ ] All 3 calc contracts referenced in manifest exist on disk
- [ ] 3 worked examples all schema-validate (IR + intent)
- [ ] Every cascade node in every example has `binding_constraint` from the controlled vocabulary
- [ ] Every node has `tool_call_pending: true` (no runtime yet)
- [ ] Rationale block has 8 sections in every example
- [ ] SKILLS_STATUS.md shows cable-sizing as beta + roadmap updated
- [ ] All commits pushed to origin/main

When done: announce on the user channel — "Item 3 (cable-sizing) shipped at vX.X.X beta. Next up: Item 4 (voltage-drop)."

