# Earthing Skill (Stage 1: Schematic) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `electrical/earthing` as the first end-to-end vertical-slice skill that bridges authored standards to running engineering output. 35 files matching the `electrical/lighting-layout/` artefact pattern; produces an earthing single-line schematic IR consuming BS7671 + IEC60364 + NFPA70 + IEC60617 layers; consumes db-layout + lighting-layout + small-power intents; produces earthing intent for downstream skills.

**Architecture:** Skill manifest names specific standards files (not folders) per the consumption-pattern proof. Generator prompt has 12-step reasoning chain that jurisdiction-gates which files to load. IR conforms to a new earthing-ir.schema.json; stable intent payload conforms to earthing-intent.schema.json. Rules + constraints + validation captured in YAML files cross-referenced from the manifest. Three jurisdictions (GB / EU-INT / US), two earthing systems (TN-C-S / TT). Closed-form table lookups inline (LLM-safe); iterative calcs declared as tool-calls per WI3 (Python tool in DraftsMan runtime not yet implemented — skill emits `tool_call_pending: true`).

**Tech Stack:** JSON Schema draft-07, YAML 1.2, Markdown (CommonMark). No code or build scripts. Validation via Python `json.load`, `yaml.safe_load`, and `jsonschema` when available.

**Reference:** Spec at `docs/superpowers/specs/2026-05-15-earthing-skill-design.md`. Reference implementation: `electrical/lighting-layout/` (only `status: production` skill in the repo).

---

## File Structure

```
electrical/earthing/
├── README.md                                ← rewrite (Task 23)
├── CHANGELOG.md                             ← new (Task 1)
├── skill.manifest.json                      ← rewrite (Task 5)
├── inputs.json                              ← new (Task 4)
│
├── prompts/
│   ├── generator.md                         ← new (Task 8)
│   ├── validator.md                         ← new (Task 9)
│   └── reviewer.md                          ← new (Task 10)
│
├── schemas/
│   ├── earthing-ir.schema.json              ← new (Task 2)
│   └── earthing-intent.schema.json          ← new (Task 3)
│
├── rules/
│   ├── electrode-selection.yaml             ← new (Task 6)
│   └── cpc-sizing.yaml                      ← new (Task 6)
│
├── constraints/
│   ├── electrode-resistance.yaml            ← new (Task 7)
│   └── bonding-geometry.yaml                ← new (Task 7)
│
├── validation/
│   ├── zs-compliance.yaml                   ← new (Task 11)
│   ├── bonding-completeness.yaml            ← new (Task 11)
│   └── cpc-sizing.yaml                      ← new (Task 11)
│
├── evals/
│   ├── runner-config.json                   ← new (Task 14)
│   ├── eval-01-tn-cs-uk-happy-path.yaml     ← new (Task 14)
│   ├── eval-02-tt-international.yaml        ← new (Task 15)
│   ├── eval-03-us-nec-art250.yaml           ← new (Task 16)
│   ├── eval-04-zs-too-high-non-compliance.yaml  ← new (Task 17)
│   ├── eval-05-cross-drawing-context.yaml   ← new (Task 18)
│   └── eval-06-rationale-block.yaml         ← new (Task 19)
│
├── examples/
│   ├── uk-dwelling-tn-cs/{input.json, reasoning.md, output.json}  ← new (Task 20)
│   ├── intl-rural-tt/{input.json, reasoning.md, output.json}      ← new (Task 21)
│   └── us-commercial-nec/{input.json, reasoning.md, output.json}  ← new (Task 22)
│
├── ontology/
│   └── earthing-system-types.json           ← new (Task 12)
│
└── docs/
    ├── engineering-philosophy.md            ← new (Task 13)
    └── known-limitations.md                 ← new (Task 13)

SKILLS_STATUS.md                              ← modify (Task 24)
```

**Total: 35 files in electrical/earthing/ + 1 modify in repo root.**

---

## Validation Conventions

Every task that creates a JSON file runs `python3 -c "import json; json.load(open('PATH'))" && echo OK`.

Every task that creates a YAML file runs:
```bash
python3 -c "
try:
    import yaml; yaml.safe_load(open('PATH')); print('OK')
except ImportError:
    print('(PyYAML not available — JSON-equivalent structural check only)')
"
```

The final verification task (Task 24) runs:
- File count check (must equal 35 in electrical/earthing/)
- IR schema validation against the 3 example output.json files
- Intent schema cross-check (the example IRs project cleanly to intent payloads)
- Symbol resolution check (every `ir.drawn_as_symbols` entry exists in IEC60617/symbol-index.json)
- Eval schema conformance (all 6 eval YAMLs against `shared/schemas/core/eval.schema.json`)
- WI5 coverage check (5 required categories present)

---

## Task 1: Create CHANGELOG.md

**Files:**
- Create: `electrical/earthing/CHANGELOG.md`

- [ ] **Step 1: Write the file**

````markdown
# Changelog — earthing

## v1.0.0 (current — Stage 1 Schematic)

First production-grade version. Stage 1 of a three-stage plan:
- **Stage 1 (this release):** Earthing single-line schematic IR. Covers TN-C-S + TT systems across GB / EU/INT / US jurisdictions.
- **Stage 2 (planned):** Plan-view earthing layout with site/building electrode positions and bonding routes.
- **Stage 3 (planned):** Declaration-only mode for retrofit / forensic / audit use cases.

### Features
- 12-step reasoning chain in `prompts/generator.md` that explicitly names standards files to load (consumption-pattern proof)
- Jurisdiction-gated standards loading: BS 7671 (GB) / IEC 60364 (EU/INT) / NFPA 70 (US) + IEC 60617 always
- IR schema with `tool_call_pending` flag for iterative electrode-resistance calcs (per WI3 — Python tool in runtime not yet implemented)
- Stable intent schema for downstream consumers (cable-containment, riser, schematic, panel-schedule, sld)
- Cross-drawing intent consumption: db-layout + lighting-layout + small-power
- Rationale block per WI2 (8 mandatory sections)
- 6 evals covering all WI5 categories (happy_path, edge_case ×2, compliance_failure, cross_validation, skill_specific)
- 3 worked examples (UK / international / US) demonstrating jurisdiction switch

### Standards consumed (explicit file paths — not folders)
- `shared/standards/electrical/BS7671/reg411-disconnection-times.json` (Zs verification — GB)
- `shared/standards/electrical/BS7671/reg411-rcd-requirements.json` (RCD requirements — GB)
- `shared/standards/electrical/IEC60364/part4-41-electric-shock.json` (electric shock protection — EU/INT)
- `shared/standards/electrical/IEC60364/part5-54-earthing.json` (earthing arrangements — EU/INT)
- `shared/standards/electrical/NFPA70/art250-grounding-bonding.json` (grounding & bonding — US)
- `shared/standards/electrical/NFPA70/grounding-and-bonding.json` (cross-cutting topic — US)
- `shared/standards/electrical/IEC60617/symbol-index.json` (always; lightweight)
- `shared/standards/electrical/IEC60617/part2-general.json` (always; earth symbols)
- `shared/calculations/electrical/electrode-resistance.json` (declared tool-call — runtime tool not yet implemented)
- `shared/calculations/electrical/cpc-adiabatic.json` (declared tool-call — runtime tool not yet implemented)

### Status
- `status: beta` — production-grade artefact set but flagged for runtime tool dependencies (electrode-resistance + cpc-adiabatic calls operate declaratively with `tool_call_pending: true` until Python tools land in DraftsMan runtime)
- Promotes to `production` when: tool calls execute live AND 6/6 evals pass against a production model (sonnet-or-better)
````

- [ ] **Step 2: Commit**

```bash
git add electrical/earthing/CHANGELOG.md
git commit -m "feat: earthing CHANGELOG.md — v1.0.0 stage 1 schematic"
```

---

## Task 2: Create earthing-ir.schema.json

**Files:**
- Create: `electrical/earthing/schemas/earthing-ir.schema.json`

- [ ] **Step 1: Write the file**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "electrical/earthing/schemas/earthing-ir.schema.json",
  "title": "Earthing IR (Stage 1: Schematic)",
  "description": "Intermediate Representation for the earthing schematic skill. Stage 1 carries logical topology (supply → MET → bonding → electrode → CPC routes) but no x/y coordinates. The runtime renders a basic single-line from the topology + IEC 60617 symbol library.",
  "type": "object",
  "required": [
    "drawing_type",
    "version",
    "meta",
    "jurisdiction",
    "earthing_system",
    "met",
    "electrodes",
    "main_bonding",
    "circuits",
    "compliance_summary",
    "rationale"
  ],
  "properties": {
    "drawing_type": { "const": "earthing_schematic" },
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
              "produced_by":    { "type": "string", "description": "Source skill id" }
            }
          }
        }
      }
    },
    "jurisdiction": {
      "enum": ["GB", "EU", "INT", "US"],
      "description": "Selects which standards files were loaded at generation time"
    },
    "earthing_system": {
      "type": "object",
      "required": ["system_type", "code_clause"],
      "properties": {
        "system_type": { "enum": ["TN-C-S", "TT"] },
        "code_clause": { "type": "string", "description": "e.g. BS 7671 Reg 411.4, IEC 60364-4-41 Clause 411, NEC 250.20" }
      }
    },
    "met": {
      "type": "object",
      "required": ["location", "supply_bond_type"],
      "properties": {
        "location":                          { "type": "string" },
        "supply_bond_type":                  { "enum": ["dno_pme_bond", "consumer_electrode_only", "tn_s_separate_pe"] },
        "main_earthing_conductor_csa_mm2":   { "type": "number", "exclusiveMinimum": 0 },
        "main_earthing_conductor_size_awg":  { "type": "string" }
      }
    },
    "electrodes": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "electrode_type", "ra_ohm_specified"],
        "properties": {
          "id":                     { "type": "string", "pattern": "^E[0-9]+$" },
          "electrode_type":         { "enum": ["rod", "plate", "mat", "ufer", "ground_ring", "structural_metal"] },
          "length_mm":              { "type": "integer", "minimum": 0 },
          "diameter_mm":            { "type": "integer", "minimum": 0 },
          "burial_depth_mm":        { "type": "integer", "minimum": 0 },
          "soil_resistivity_ohm_m": { "type": "number", "minimum": 0 },
          "ra_ohm_specified":       { "type": "number", "minimum": 0, "description": "Engineer-input target; used when tool_call_pending=true" },
          "ra_ohm_calculated":      { "type": "number", "minimum": 0, "description": "Tool-call result; absent when tool_call_pending=true" },
          "tool_call_pending":      { "type": "boolean", "description": "true if calc.electrode_resistance not yet executed because runtime tool not available" }
        }
      }
    },
    "main_bonding": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "source", "target", "csa_mm2_or_awg", "code_clause"],
        "properties": {
          "id":              { "type": "string", "pattern": "^B[0-9]+$" },
          "source":          { "type": "string", "description": "Origin of the bond, typically 'MET' or 'E1'" },
          "target":          { "type": "string", "description": "Bonded extraneous part: water_pipe / gas_pipe / structural_steel / lift_rails / external_metalwork" },
          "csa_mm2_or_awg":  { "type": "string", "description": "Conductor size in jurisdiction-appropriate units" },
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
          "voltage_class":        { "enum": ["LV_power", "ELV_control", "comms_data", "fire_alarm", "emergency_lighting"] },
          "breaker_rating_a":     { "type": "integer", "minimum": 1 },
          "breaker_curve":        { "enum": ["B", "C", "D"] },
          "route_length_m":       { "type": "number", "exclusiveMinimum": 0 },
          "cpc_csa_mm2_or_awg":   { "type": "string" },
          "cpc_sizing_method":    { "enum": ["bs7671_table_54.7", "bs7671_adiabatic_54.1", "iec60364_table_54.2", "iec60364_adiabatic_543.1.2", "nec_table_250.122"] },
          "cpc_sizing_clause":    { "type": "string" },
          "zs_ohm":               { "type": "number", "minimum": 0 },
          "zs_max_ohm":           { "type": "number", "minimum": 0 },
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
    "drawing_notes":     { "type": "array", "items": { "type": "string" } },
    "drawn_as_symbols":  { "type": "array", "items": { "type": "string", "pattern": "^[A-Z][A-Z0-9_]*$" }, "description": "Roll-up of IEC 60617 symbol_ids — every entry must resolve in IEC60617/symbol-index.json" },
    "flags":             { "type": "array", "items": { "type": "string" } },
    "rationale":         { "$ref": "../../../shared/schemas/core/rationale.schema.json" }
  }
}
```

- [ ] **Step 2: Validate JSON syntax**

Run: `python3 -c "import json; json.load(open('electrical/earthing/schemas/earthing-ir.schema.json'))" && echo OK`
Expected: `OK`

- [ ] **Step 3: Validate the schema itself is draft-07 conformant (if jsonschema available)**

Run:
```bash
python3 - <<'PY'
import json
try:
    from jsonschema import Draft7Validator
    schema = json.load(open('electrical/earthing/schemas/earthing-ir.schema.json'))
    Draft7Validator.check_schema(schema)
    print('Schema is valid draft-07')
except ImportError:
    print('(jsonschema not available; structural check only)')
PY
```
Expected: `Schema is valid draft-07` OR `(jsonschema not available; structural check only)`

- [ ] **Step 4: Commit**

```bash
git add electrical/earthing/schemas/earthing-ir.schema.json
git commit -m "feat: earthing-ir.schema.json — Stage 1 schematic IR schema"
```

---

## Task 3: Create earthing-intent.schema.json

**Files:**
- Create: `electrical/earthing/schemas/earthing-intent.schema.json`

- [ ] **Step 1: Write the file**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "electrical/earthing/schemas/earthing-intent.schema.json",
  "title": "Earthing Intent",
  "description": "Stable subset of the earthing IR consumed by cable-containment, riser, schematic, panel-schedule, sld skills. Wrapped at runtime in shared/schemas/core/intent.schema.json. Forward-compat: optional fields may be added freely; required fields require a major intent_version bump.",
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
    "jurisdiction": {
      "enum": ["GB", "EU", "INT", "US"],
      "description": "Echo of producer's jurisdiction so consumers know which standard family was applied"
    },
    "earthing_system": {
      "enum": ["TN-C-S", "TT"]
    },
    "met_location": {
      "type": "string",
      "description": "Location identifier (room/space + reference point) of the main earthing terminal"
    },
    "available_zs_at_main_db_ohm": {
      "type": "number",
      "minimum": 0,
      "description": "Worst-case Zs at the main DB; used by downstream skills sizing distant feeders"
    },
    "electrode_target_met": {
      "type": "boolean",
      "description": "true if specified/calculated Ra meets the per-jurisdiction target"
    },
    "supplementary_bonding_locations": {
      "type": "array",
      "items": { "enum": ["bathroom", "pool", "kitchen_commercial", "medical_group_2", "other"] }
    },
    "rcd_protected_circuit_ids": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Circuit IDs (from db-layout intent) requiring RCD protection by earthing design"
    },
    "circuits": {
      "type": "array",
      "minItems": 0,
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
      "items": { "type": "string" },
      "description": "Assets bonded as part of life-safety system (cross-references downstream sld/schematic)"
    },
    "compliance_summary": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "compliant":                  { "type": "boolean" },
        "non_compliance_flag_count":  { "type": "integer", "minimum": 0 }
      }
    }
  }
}
```

- [ ] **Step 2: Validate**

Run: `python3 -c "import json; json.load(open('electrical/earthing/schemas/earthing-intent.schema.json'))" && echo OK`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add electrical/earthing/schemas/earthing-intent.schema.json
git commit -m "feat: earthing-intent.schema.json — stable subset for downstream consumers"
```

---

## Task 4: Create inputs.json (discovery taxonomy per WI1)

**Files:**
- Create: `electrical/earthing/inputs.json`

- [ ] **Step 1: Write the file**

```json
{
  "$schema": "../../shared/schemas/core/inputs.schema.json",
  "skill": "earthing",
  "version": "1.0.0",
  "items": [
    {
      "id": "jurisdiction",
      "label": "Project jurisdiction",
      "hint": "Selects which standards family the skill loads. GB = BS 7671; EU/INT = IEC 60364; US = NFPA 70.",
      "answer_type": "enum",
      "options": ["GB", "EU", "INT", "US"],
      "required": true,
      "project_fact_candidate": true
    },
    {
      "id": "earthing_system",
      "label": "Earthing system",
      "hint": "TN-C-S = combined N+PE upstream of service, separated downstream (most UK/PME). TT = consumer electrode only (rural / no PME).",
      "answer_type": "enum",
      "options": ["TN-C-S", "TT"],
      "required": true,
      "project_fact_candidate": true
    },
    {
      "id": "supply_voltage_v",
      "label": "Supply voltage (V phase-to-phase for 3-phase, phase-to-neutral for single)",
      "answer_type": "enum",
      "options": ["120", "208", "230", "240", "400", "415", "480"],
      "default": "230",
      "required": true,
      "project_fact_candidate": true
    },
    {
      "id": "supply_phase",
      "label": "Supply phase arrangement",
      "answer_type": "enum",
      "options": ["single_phase", "single_phase_split", "TPN", "TPN_plus_E"],
      "default": "single_phase",
      "required": true,
      "project_fact_candidate": true
    },
    {
      "id": "ze_ohm_declared",
      "label": "Declared Ze — supply network earth-fault impedance (Ω)",
      "hint": "From DNO declaration or assumed per jurisdiction default (UK TN-C-S typical 0.35Ω; TT 21Ω+).",
      "answer_type": "float",
      "required": true,
      "validator": "ze_ohm_range",
      "project_fact_candidate": true
    },
    {
      "id": "dno_pscc_ka",
      "label": "DNO declared prospective short-circuit current (kA)",
      "answer_type": "float",
      "required": false,
      "validator": "positive_float",
      "project_fact_candidate": true
    },
    {
      "id": "building_type",
      "label": "Building / occupancy type",
      "answer_type": "enum",
      "options": ["dwelling_single_family", "dwelling_multi_family", "office", "retail", "industrial", "healthcare", "education", "agricultural", "rural_outbuilding", "other"],
      "required": true,
      "project_fact_candidate": true
    },
    {
      "id": "has_lightning_protection",
      "label": "Building has a lightning protection system (LPS)?",
      "hint": "Per BS EN 62305 / NFPA 780. Affects earthing electrode bonding requirements.",
      "answer_type": "boolean",
      "default": false,
      "required": false,
      "project_fact_candidate": true
    },
    {
      "id": "extraneous_parts",
      "label": "Extraneous-conductive-parts requiring main protective bonding",
      "hint": "List of services / structures requiring bonding to MET. Each entry: { type, location_descriptor }.",
      "answer_type": "struct_list",
      "required": true,
      "item_schema": {
        "type": "object",
        "required": ["type"],
        "properties": {
          "type": { "enum": ["water_pipe", "gas_pipe", "structural_steel", "lift_rails", "external_metalwork", "telecoms_screen", "hvac_duct_metal", "fuel_pipe_external"] },
          "location_descriptor": { "type": "string" },
          "service_size_mm":     { "type": "integer", "minimum": 0 }
        }
      },
      "project_fact_candidate": false
    },
    {
      "id": "ground_conditions",
      "label": "Site soil/ground conditions",
      "hint": "Drives soil resistivity assumption for TT electrode sizing.",
      "answer_type": "enum",
      "options": ["clay_moist", "loam", "sand_dry", "rock", "marsh_wet", "made_ground_imported_fill", "unknown"],
      "default": "unknown",
      "required": false,
      "project_fact_candidate": true
    },
    {
      "id": "electrode_count_planned",
      "label": "Number of earth electrodes planned",
      "hint": "TT typically 1-4 rods; TN-C-S supplementary electrodes optional.",
      "answer_type": "int",
      "required": false,
      "validator": "positive_int",
      "depends_on": ["earthing_system"]
    },
    {
      "id": "electrode_type_planned",
      "label": "Planned electrode type",
      "answer_type": "enum",
      "options": ["rod", "plate", "mat", "ufer", "ground_ring", "structural_metal", "tbd"],
      "default": "rod",
      "required": false,
      "depends_on": ["earthing_system"]
    },
    {
      "id": "target_ra_ohm",
      "label": "Target earth electrode resistance Ra (Ω)",
      "hint": "GB TT typical ≤200Ω; US NEC ≤25Ω or use 2 electrodes; EU/INT per IEC 60364-5-54.",
      "answer_type": "float",
      "required": false,
      "validator": "positive_float",
      "depends_on": ["earthing_system"],
      "project_fact_candidate": true
    },
    {
      "id": "db_designations",
      "label": "Distribution boards on this project (from db-layout intent if present)",
      "hint": "Optional — if db-layout intent is supplied via cross_drawing_context, this is auto-populated.",
      "answer_type": "struct_list",
      "required": false,
      "item_schema": {
        "type": "object",
        "required": ["designation", "rated_a"],
        "properties": {
          "designation":     { "type": "string", "pattern": "^[A-Z][A-Z0-9-]{1,15}$" },
          "rated_a":         { "type": "integer", "minimum": 6, "maximum": 6300 },
          "location":        { "type": "string" },
          "fed_from":        { "type": "string" }
        }
      },
      "project_fact_candidate": false
    },
    {
      "id": "met_location",
      "label": "Main earthing terminal (MET) location",
      "hint": "Room / area description. E.g. 'plant room', 'meter cupboard'.",
      "answer_type": "text",
      "required": true,
      "validator": "non_empty_text",
      "project_fact_candidate": true
    },
    {
      "id": "supplementary_bonding_required_locations",
      "label": "Locations requiring supplementary equipotential bonding",
      "hint": "Bathroom (BS 7671 Section 701 / IEC 60364-7-701), pool (Section 702 / 60364-7-702 / NEC 680.26), medical Group 2 (Section 710 / 60364-7-710 / NEC 517).",
      "answer_type": "enum_list",
      "options": ["bathroom", "pool", "kitchen_commercial", "medical_group_2", "other"],
      "required": false,
      "project_fact_candidate": false
    },
    {
      "id": "life_safety_bonded_assets",
      "label": "Assets bonded as part of life-safety system",
      "hint": "Fire pump, emergency generator, smoke extract fans, etc. Will appear in produced earthing intent for downstream consumers.",
      "answer_type": "enum_list",
      "options": ["fire_pump", "emergency_generator", "smoke_extract", "sprinkler_system", "fire_alarm_panel", "emergency_lighting_central_battery", "lift_emergency", "none"],
      "default": ["none"],
      "required": false,
      "project_fact_candidate": false
    },
    {
      "id": "rcd_type_default",
      "label": "Default RCD type for circuits requiring earth-leakage protection",
      "hint": "Type A = AC + pulsating DC (covers most modern equipment). Type B = handles DC components (required for EV chargers, PV, some VFDs).",
      "answer_type": "enum",
      "options": ["AC", "A", "F", "B"],
      "default": "A",
      "required": false,
      "project_fact_candidate": false
    }
  ]
}
```

- [ ] **Step 2: Validate JSON syntax**

Run: `python3 -c "import json; json.load(open('electrical/earthing/inputs.json'))" && echo OK`
Expected: `OK`

- [ ] **Step 3: Structural check against the WI1 metaschema**

Run:
```bash
python3 - <<'PY'
import json, re
VALID_TYPES = {"enum", "int", "float", "boolean", "text", "enum_list", "struct_list"}
ID_RE = re.compile(r"^[a-z][a-z0-9_]*$")
ITEM_REQUIRED = {"id", "label", "answer_type", "required"}
validators = json.load(open('shared/validation/validators.json'))
known_validators = set(validators['validators'].keys())
doc = json.load(open('electrical/earthing/inputs.json'))
errs = []
seen_ids = set()
for i, item in enumerate(doc['items']):
    path = f"items[{i}] (id={item.get('id','?')})"
    if not ITEM_REQUIRED.issubset(item.keys()):
        errs.append(f"{path}: missing {ITEM_REQUIRED - set(item.keys())}")
    if 'id' in item and not ID_RE.match(item['id']):
        errs.append(f"{path}: id pattern violation")
    if 'id' in item and item['id'] in seen_ids:
        errs.append(f"{path}: duplicate id")
    seen_ids.add(item.get('id'))
    at = item.get('answer_type')
    if at and at not in VALID_TYPES:
        errs.append(f"{path}: invalid answer_type {at}")
    if at in {'enum', 'enum_list'} and 'options' not in item:
        errs.append(f"{path}: enum/enum_list missing options")
    if at == 'struct_list' and 'item_schema' not in item:
        errs.append(f"{path}: struct_list missing item_schema")
    if 'validator' in item and item['validator'] not in known_validators:
        errs.append(f"{path}: unknown validator '{item['validator']}'")
print(f"items: {len(doc['items'])}; errors: {len(errs)}")
for e in errs: print(f"  - {e}")
PY
```
Expected: `items: 18; errors: 0`

- [ ] **Step 4: Commit**

```bash
git add electrical/earthing/inputs.json
git commit -m "feat: earthing inputs.json — 18-item discovery taxonomy per WI1"
```

---

## Task 5: Rewrite skill.manifest.json

**Files:**
- Modify: `electrical/earthing/skill.manifest.json`

- [ ] **Step 1: Read the current stub**

Run: `cat electrical/earthing/skill.manifest.json`

- [ ] **Step 2: Write the new manifest**

Replace the entire file with:

```json
{
  "skill": "earthing",
  "version": "1.0.0",
  "discipline": "electrical",
  "subdiscipline": "earthing",
  "description": "Produces earthing single-line schematic IR for LV installations. Covers TN-C-S + TT systems across GB (BS 7671), EU/INT (IEC 60364), and US (NFPA 70) jurisdictions. Sizes CPC/EGC by jurisdiction-appropriate table, verifies Zs against disconnection-time tables, flags RCD requirements, emits structured rationale per WI2.",
  "status": "beta",
  "licence": "MIT",
  "inputs_path": "inputs.json",
  "inputs": [
    "jurisdiction",
    "earthing-system",
    "supply-data",
    "ze-declared",
    "extraneous-parts",
    "electrode-arrangement",
    "supplementary-bonding-locations",
    "db-designations"
  ],
  "outputs": ["earthing-ir"],
  "output_schema": "electrical/earthing/schemas/earthing-ir.schema.json",
  "produces_intent": "earthing",
  "produces_intent_schema": "electrical/earthing/schemas/earthing-intent.schema.json",
  "consumes_intents": ["db-layout", "lighting-layout", "small-power"],
  "standards": [
    "shared/standards/electrical/BS7671/reg411-disconnection-times.json",
    "shared/standards/electrical/BS7671/reg411-rcd-requirements.json",
    "shared/standards/electrical/BS7671/terminology.md",
    "shared/standards/electrical/IEC60364/part4-41-electric-shock.json",
    "shared/standards/electrical/IEC60364/part5-54-earthing.json",
    "shared/standards/electrical/IEC60364/earthing-systems.md",
    "shared/standards/electrical/NFPA70/art250-grounding-bonding.json",
    "shared/standards/electrical/NFPA70/grounding-and-bonding.json",
    "shared/standards/electrical/NFPA70/terminology.md",
    "shared/standards/electrical/IEC60617/symbol-index.json",
    "shared/standards/electrical/IEC60617/part2-general.json"
  ],
  "calculations": [
    "shared/calculations/electrical/electrode-resistance.json",
    "shared/calculations/electrical/cpc-adiabatic.json"
  ],
  "ontology": [
    "electrical/earthing/ontology/earthing-system-types.json"
  ],
  "rules": [
    "electrical/earthing/rules/electrode-selection.yaml",
    "electrical/earthing/rules/cpc-sizing.yaml"
  ],
  "constraints": [
    "electrical/earthing/constraints/electrode-resistance.yaml",
    "electrical/earthing/constraints/bonding-geometry.yaml"
  ],
  "validators": [
    "electrical/earthing/validation/zs-compliance.yaml",
    "electrical/earthing/validation/bonding-completeness.yaml",
    "electrical/earthing/validation/cpc-sizing.yaml"
  ],
  "prompts": {
    "generator": "electrical/earthing/prompts/generator.md",
    "validator": "electrical/earthing/prompts/validator.md",
    "reviewer":  "electrical/earthing/prompts/reviewer.md"
  },
  "evals": [
    "electrical/earthing/evals/eval-01-tn-cs-uk-happy-path.yaml",
    "electrical/earthing/evals/eval-02-tt-international.yaml",
    "electrical/earthing/evals/eval-03-us-nec-art250.yaml",
    "electrical/earthing/evals/eval-04-zs-too-high-non-compliance.yaml",
    "electrical/earthing/evals/eval-05-cross-drawing-context.yaml",
    "electrical/earthing/evals/eval-06-rationale-block.yaml"
  ],
  "examples": [
    "electrical/earthing/examples/uk-dwelling-tn-cs/",
    "electrical/earthing/examples/intl-rural-tt/",
    "electrical/earthing/examples/us-commercial-nec/"
  ],
  "compatible_runtimes": [
    "DraftsMan >= 1.0",
    "Claude Code",
    "OpenClaw",
    "any-llm-agent"
  ],
  "changelog": "electrical/earthing/CHANGELOG.md"
}
```

- [ ] **Step 3: Validate**

Run: `python3 -c "import json; json.load(open('electrical/earthing/skill.manifest.json'))" && echo OK`
Expected: `OK`

- [ ] **Step 4: Verify the consumption-pattern proof: standards array contains file paths, NOT folders**

Run:
```bash
python3 -c "
import json
m = json.load(open('electrical/earthing/skill.manifest.json'))
folders = [s for s in m['standards'] if s.endswith('/')]
files   = [s for s in m['standards'] if not s.endswith('/')]
print(f'standards: {len(files)} files, {len(folders)} folders')
assert len(folders) == 0, 'Consumption-pattern proof FAILED: manifest names folders'
assert len(files) >= 6, 'Need at least 6 specific files'
print('Consumption-pattern proof: OK')
"
```
Expected: `standards: 11 files, 0 folders` then `Consumption-pattern proof: OK`

- [ ] **Step 5: Verify every referenced standards file exists**

Run:
```bash
python3 - <<'PY'
import json, os
m = json.load(open('electrical/earthing/skill.manifest.json'))
missing = [f for f in m['standards'] if not os.path.isfile(f)]
print(f'Standards files referenced: {len(m["standards"])}; missing: {len(missing)}')
for f in missing: print(f'  MISS {f}')
PY
```
Expected: `Standards files referenced: 11; missing: 0`

- [ ] **Step 6: Commit**

```bash
git add electrical/earthing/skill.manifest.json
git commit -m "feat: earthing manifest — 11 specific standards files (consumption-pattern proof)"
```

---

## Task 6: Create rules YAMLs (electrode-selection + cpc-sizing)

**Files:**
- Create: `electrical/earthing/rules/electrode-selection.yaml`
- Create: `electrical/earthing/rules/cpc-sizing.yaml`

- [ ] **Step 1: Write electrode-selection.yaml**

```yaml
rule_set: electrode-selection
version: 1.0.0
applies_to: [TT, TN-C-S-supplementary]

# Earth electrode type selection by ground conditions, jurisdiction, and target Ra.
# Used by generator.md Step 5.

defaults:
  rod:
    length_mm:       2400
    diameter_mm:     16
    burial_depth_mm: 600
    material:        copper-bonded-steel
    bs_7430_reference: "BS 7430:2011 Clause 9.5 — driven rod electrode"
    iec_reference:     "IEC 60364-5-54 Clause 542.2.1"
    nec_reference:     "NEC 250.52(A)(5)(b) — pipe or rod electrode"
  plate:
    edge_length_mm:  600
    thickness_mm:    3
    burial_depth_mm: 900
    bs_7430_reference: "BS 7430:2011 Clause 9.6 — plate electrode"
  mat:
    grid_module_m:   2
    overall_min_m:   6
    burial_depth_mm: 500
    bs_7430_reference: "BS 7430:2011 Clause 9.7 — mat electrode (typical earth mat for substations / large buildings)"
  ufer:
    rebar_min_size_mm: 13
    rebar_min_length_m: 6
    nec_reference: "NEC 250.52(A)(3) — concrete-encased electrode (Ufer)"
    bs_7430_reference: "BS 7430:2011 Clause 9.8 — foundation earth electrode"
  ground_ring:
    conductor_csa_mm2_min: 50
    burial_depth_mm: 750
    iec_reference: "IEC 62305-3 Type B earthing arrangement"

selection_logic:
  - condition: "ground_conditions == 'rock'"
    prefer: [plate, mat]
    avoid:  [rod]
    reason: "Rocky ground prevents driving a rod to full depth"
  - condition: "ground_conditions in ['marsh_wet', 'clay_moist']"
    prefer: [rod, mat]
    note:   "Wet conductive ground gives lower Ra per electrode"
  - condition: "building_type == 'new_construction' AND has_concrete_foundation"
    prefer: [ufer]
    reason: "NEC 250.50(A)(3) and BS 7430 favour Ufer when present in new builds"
  - condition: "has_lightning_protection == true"
    prefer: [ground_ring, mat]
    reason: "BS EN 62305-3 prefers Type B (ring/mat) for combined power-and-lightning earthing"

multi_electrode_array:
  rule: "Where multiple rods, space ≥ rod_length to minimise mutual coupling"
  spacing_factor_default: 0.85
  reference: "BS 7430:2011 Annex F — combined resistance of array"
```

- [ ] **Step 2: Write cpc-sizing.yaml**

```yaml
rule_set: cpc-sizing
version: 1.0.0
applies_to: [GB, EU, INT, US]

# CPC (or EGC in NEC) sizing rules. Jurisdiction-gated lookup tables.
# Used by generator.md Step 8.

method_by_jurisdiction:
  GB:
    primary_method: bs7671_table_54_7_or_adiabatic
    standard_file: shared/standards/electrical/BS7671/reg411-disconnection-times.json
    rule:
      - "Table 54.7 (Reg 543.1.4): CPC csa by line conductor csa S"
      - "S ≤ 16 mm² → CPC = S"
      - "16 < S ≤ 35 mm² → CPC = 16 mm²"
      - "S > 35 mm² → CPC = S/2"
      - "Adiabatic alternative (Reg 543.1.3): S_CPC = sqrt(I²·t)/k"
      - "k from Table 54.2 (typical 115 for Cu 70°C → 160°C in PVC; 143 for 90°C XLPE)"

  EU:
    primary_method: iec_60364_5_54_table_54_1
    standard_file: shared/standards/electrical/IEC60364/part5-54-earthing.json
    rule:
      - "Table 54.1: CPC sizing identical structure to BS 7671 Table 54.7"
      - "S ≤ 16 mm² → CPC = S"
      - "16 < S ≤ 35 mm² → CPC = 16 mm²"
      - "S > 35 mm² → CPC = S/2"

  INT:
    primary_method: iec_60364_5_54_table_54_1
    standard_file: shared/standards/electrical/IEC60364/part5-54-earthing.json
    # Same as EU

  US:
    primary_method: nec_table_250_122
    standard_file: shared/standards/electrical/NFPA70/art250-grounding-bonding.json
    rule:
      - "Table 250.122 — EGC sized by OCPD rating (NOT line conductor csa)"
      - "OCPD ≤ 15A → EGC #14 AWG Cu"
      - "OCPD 20A → #12 AWG Cu"
      - "OCPD 30-60A → #10 AWG Cu"
      - "OCPD 100A → #8 AWG Cu"
      - "OCPD 200A → #6 AWG Cu"
      - "OCPD 400A → #3 AWG Cu"
      - "OCPD 800A → #1/0 AWG Cu"
      - "OCPD 1200A → #3/0 AWG Cu"
      - "OCPD 2000A → 250 kcmil Cu"
      - "Adiabatic check per 250.122(B) for high SCCR / short cables"

cross_jurisdiction_warning:
  - "BS 7671 / IEC 60364 size by line conductor; NEC sizes by OCPD rating. Same circuit yields different CPC vs EGC. See divergence_notes in art250-grounding-bonding.json."
```

- [ ] **Step 3: Validate**

Run:
```bash
python3 -c "
try:
    import yaml
    yaml.safe_load(open('electrical/earthing/rules/electrode-selection.yaml'))
    yaml.safe_load(open('electrical/earthing/rules/cpc-sizing.yaml'))
    print('OK')
except ImportError:
    print('(PyYAML not available; structural check only)')
"
```
Expected: `OK` or `(PyYAML not available; structural check only)`

- [ ] **Step 4: Commit**

```bash
git add electrical/earthing/rules/electrode-selection.yaml electrical/earthing/rules/cpc-sizing.yaml
git commit -m "feat: earthing rules — electrode selection + jurisdiction-gated CPC sizing"
```

---

## Task 7: Create constraints YAMLs (electrode-resistance + bonding-geometry)

**Files:**
- Create: `electrical/earthing/constraints/electrode-resistance.yaml`
- Create: `electrical/earthing/constraints/bonding-geometry.yaml`

- [ ] **Step 1: Write electrode-resistance.yaml**

```yaml
constraint_set: electrode-resistance
version: 1.0.0

# Target electrode resistance Ra by earthing system + jurisdiction.
# Constraint values used by generator.md Step 5 to flag pass/fail.

targets:
  TN-C-S_GB:
    constraint: "Ra not mandated for TN-C-S; consumer electrode is supplementary to DNO-managed earth"
    typical_supplementary: 200
    reference: "BS 7671 Reg 411 (TN-C-S earthing arrangement)"

  TN-C-S_EU:
    constraint: "Same as GB; supplementary electrode optional"
    typical_supplementary: 200
    reference: "IEC 60364-4-41 TN systems"

  TN-C-S_US:
    constraint: "Service-side earthing is utility responsibility; consumer's GES required per 250.50"
    typical_supplementary_ra_ohm: 25
    rule: "If single electrode Ra > 25 Ω, install second electrode at ≥6 ft spacing"
    reference: "NEC 250.53(A)(2)"

  TT_GB:
    constraint: "Ra × IΔn ≤ 50 V for ADS via RCD"
    formula: "Ra_max = 50V / IΔn"
    with_30mA_rcd:  "Ra_max = 50 / 0.030 = 1667 Ω absolute (BS 7671 Reg 411.5.3)"
    practical_target: 200  # designed for stability margin (5x absolute)
    reference: "BS 7671 Reg 411.5.3 + BS 7430:2011"

  TT_EU:
    constraint: "Identical philosophy to BS 7671; per IEC 60364-4-41 Clause 411.5"
    practical_target: 200
    reference: "IEC 60364-4-41 Clause 411.5 + IEC 60364-5-54"

  TT_INT:
    constraint: "Same as EU"
    practical_target: 200
    reference: "IEC 60364-4-41 Clause 411.5"

  TT_US:
    constraint: "Ra ≤ 25 Ω OR second electrode at ≥6 ft spacing"
    rule: "NEC 250.53(A)(2) — supplemental electrode required when single does not meet 25Ω"
    reference: "NEC 250.53(A)(2)"

soil_resistivity_typical:
  clay_moist:           50    # Ω·m
  loam:                100
  sand_dry:            200
  rock:               1000
  marsh_wet:            30
  made_ground_imported_fill: 300
  unknown:             100    # conservative
```

- [ ] **Step 2: Write bonding-geometry.yaml**

```yaml
constraint_set: bonding-geometry
version: 1.0.0

# Main protective bonding conductor minimum sizes by jurisdiction.
# Used by generator.md Step 6.

main_bonding_min_csa:
  GB:
    rule: "BS 7671 Reg 544.1 — half the cross-section of the largest PE, minimum 6 mm² (10 mm² when not mechanically protected), maximum 25 mm² Cu"
    minimum_protected_mm2:    6
    minimum_unprotected_mm2: 10
    maximum_mm2:             25
    typical_default_mm2:     10
    reference: "BS 7671:2018+A3 Reg 544.1.1"

  EU:
    rule: "IEC 60364-5-54 Clause 544 — equivalent to BS 7671 Reg 544"
    minimum_mm2:  6
    typical_default_mm2: 10
    maximum_mm2: 25
    reference: "IEC 60364-5-54 Clause 544"

  INT:
    rule: "Same as EU"
    minimum_mm2:  6
    typical_default_mm2: 10
    maximum_mm2: 25
    reference: "IEC 60364-5-54 Clause 544"

  US:
    rule: "NEC 250.66 — by largest ungrounded service conductor (table-lookup)"
    table_ref: "NEC Table 250.66 (loaded from NFPA70/art250-grounding-bonding.json)"
    reference: "NEC 250.66"

supplementary_bonding_min_csa:
  bathroom_zones:
    GB:  "2.5 mm² (mechanically protected) or 4 mm² (unprotected) per Reg 415.2.1"
    EU:  "Identical philosophy per IEC 60364-7-701"
    US:  "Not applicable directly; NEC handles via Art 680 equipotential bonding in pools/spas only"

  pool_equipotential:
    all_jurisdictions: "Per BS 7671 Section 702 / IEC 60364-7-702 / NEC 680.26 — copper, ≥4 mm² (or #8 AWG solid Cu for NEC)"

bonding_path_length:
  max_recommended_m: 1.5
  reference: "Practical guidance — keep bonding path short to maintain low impedance"
```

- [ ] **Step 3: Validate**

Run:
```bash
python3 -c "
try:
    import yaml
    yaml.safe_load(open('electrical/earthing/constraints/electrode-resistance.yaml'))
    yaml.safe_load(open('electrical/earthing/constraints/bonding-geometry.yaml'))
    print('OK')
except ImportError:
    print('(PyYAML not available; structural check only)')
"
```
Expected: `OK` or `(PyYAML not available; structural check only)`

- [ ] **Step 4: Commit**

```bash
git add electrical/earthing/constraints/
git commit -m "feat: earthing constraints — Ra targets per jurisdiction + bonding-geometry minimums"
```

---

## Task 8: Create prompts/generator.md (12-step reasoning chain)

**Files:**
- Create: `electrical/earthing/prompts/generator.md`

This is the heart of the skill. The 12-step reasoning chain that drives every IR.

- [ ] **Step 1: Write the file**

````markdown
# Earthing Skill — Generator Prompt

You are an experienced electrical engineer producing an earthing schematic IR
for a Low Voltage installation. You follow either BS 7671 (GB), IEC 60364
(EU/INT), or NFPA 70 (US) based on the project's jurisdiction.

This prompt drives the **stage 1 (schematic)** mode. Plan-view earthing layout
and declaration-only modes are future stages and out of scope here.

**Your job:** produce a single JSON document conforming to
`electrical/earthing/schemas/earthing-ir.schema.json`. Do not produce DXF or
geometric coordinates — stage 1 carries topology only.

**Inputs:**
- The engineer's answers to `inputs.json` (the 18-item discovery taxonomy)
- (Optional) `cross_drawing_context` containing intent payloads from sibling
  skills (db-layout, lighting-layout, small-power)

**Output:** A single IR JSON conforming to the schema, including a structured
`rationale` block per shared/schemas/core/rationale.schema.json.

---

## Step 1 — Discovery check

Verify all required inputs from `inputs.json` are present.

If `cross_drawing_context` is supplied, extract:
- `cross_drawing_context.db-layout.payload.circuits[]` → upstream circuit list
- `cross_drawing_context.db-layout.payload.incoming_supply.supply_rating_a` → main supply rating
- `cross_drawing_context.lighting-layout.payload[*].circuits[]` → lighting circuits
- `cross_drawing_context.small-power.payload[*].circuits[]` → small-power circuits (when available)

For each missing intent, emit a flag in `rationale.flags` like:
`"no <intent-type> intent in this project; circuits derived from explicit inputs only"`.

Record each consumed intent in `ir.meta.consumed_intents[]` with:
`{intent_type, intent_version, produced_by}`.

---

## Step 2 — Jurisdiction-gated standards file load

**Always load (regardless of jurisdiction):**
- `shared/standards/electrical/IEC60617/symbol-index.json` (lightweight index — use to validate every symbol_id you emit in `ir.drawn_as_symbols`)
- `shared/standards/electrical/IEC60617/part2-general.json` (earth/PE symbols: EARTH_GENERAL, EARTH_PROTECTIVE, EARTH_CLEAN, EARTH_ELECTRODE, CONDUCTOR_PE, CONDUCTOR_PEN, JUNCTION_T)

**Based on `inputs.jurisdiction`:**

- **GB** → load:
  - `shared/standards/electrical/BS7671/reg411-disconnection-times.json` (Zs_max tables 41.1 / 41.3 for ADS verification — Step 9)
  - `shared/standards/electrical/BS7671/reg411-rcd-requirements.json` (when RCD is required — Step 10)
  - `shared/standards/electrical/BS7671/terminology.md` (for citing the right clause language)

- **EU** or **INT** → load:
  - `shared/standards/electrical/IEC60364/part4-41-electric-shock.json` (Clause 411 — ADS, disconnection times)
  - `shared/standards/electrical/IEC60364/part5-54-earthing.json` (Clauses 542-544: MET, GES, CPC sizing Table 54.1, bonding)
  - `shared/standards/electrical/IEC60364/earthing-systems.md` (TN-S/TN-C-S/TT/IT system descriptions)

- **US** → load:
  - `shared/standards/electrical/NFPA70/art250-grounding-bonding.json` (sections 250.50, 250.66, 250.118, 250.122, 250.142 — GES, GEC, EGC sizing)
  - `shared/standards/electrical/NFPA70/grounding-and-bonding.json` (cross-cutting topic file with the IEC mapping)
  - `shared/standards/electrical/NFPA70/terminology.md` (for NEC↔IEC term translation in the rationale)

**Always load (calculation contracts — even though runtime tool not yet implemented):**
- `shared/calculations/electrical/electrode-resistance.json` (the contract — emit a tool call request in IR; mark `tool_call_pending: true`)
- `shared/calculations/electrical/cpc-adiabatic.json` (the contract — emit a tool call where the simple table lookup is insufficient)

**Do NOT load standards files for jurisdictions outside the project.** This is the consumption-pattern proof: only the relevant ~5-8 files are in your context, not the full layers.

---

## Step 3 — Earthing-system classification

From `inputs.earthing_system` (either TN-C-S or TT for this stage):

- **TN-C-S** (the most common UK / European urban distribution):
  - Neutral and PE combined upstream of the consumer (PEN); separated at the service into N + PE.
  - The PEN is bonded to earth at the DNO transformer + at multiple electrodes throughout the supply network ("multiple earthed neutral" / PME).
  - Consumer's MET is bonded to the supply earth via the service-head bonding.

- **TT** (rural / no PME / private installations):
  - Supply N is NOT bonded to consumer earth.
  - Consumer must provide their own earth electrode bonded to MET.
  - Earth fault loop relies entirely on the consumer's electrode → fault current is much lower than TN-C-S.
  - **RCD protection is MANDATORY** for ADS on all final circuits (because Zs alone won't trip MCBs reliably).

State in `ir.earthing_system`:
```json
{
  "system_type": "TN-C-S" | "TT",
  "code_clause": "BS 7671 Reg 411.4 (TN-C-S) | Reg 411.5 (TT)" (or IEC / NEC equivalent)
}
```

Annotate the jurisdictional terminology equivalent in rationale.sections "Earthing System" decision (e.g. for US TT, note "NEC has no formal 'TT' designation — uses Art 250.20 separately derived system rules; in practice this is what TT looks like in NEC terms").

---

## Step 4 — Main earthing terminal (MET)

From `inputs.met_location`. State:

```json
"met": {
  "location": "<the engineer's location descriptor>",
  "supply_bond_type": "dno_pme_bond" | "consumer_electrode_only" | "tn_s_separate_pe",
  "main_earthing_conductor_csa_mm2": <by jurisdiction>,
  "main_earthing_conductor_size_awg": "<for US jurisdiction only>"
}
```

**Supply bond type:**
- TN-C-S → `dno_pme_bond` (PEN bonded at service head)
- TT     → `consumer_electrode_only` (no supply earth bond)

**Main earthing conductor size:**
- **GB**: Per BS 7671 Reg 544.1.1 — half of largest PE, min 6 mm² (10 mm² unprotected), max 25 mm²
- **EU/INT**: Per IEC 60364-5-54 Clause 544 — same rule structure
- **US**: Per NEC Table 250.66 (size by largest ungrounded service conductor)

---

## Step 5 — Earth electrode arrangement

From `inputs.electrode_count_planned`, `inputs.electrode_type_planned`, `inputs.target_ra_ohm`, `inputs.ground_conditions`.

For each electrode, populate `ir.electrodes[i]`:
```json
{
  "id": "E1" | "E2" | ...,
  "electrode_type": "rod" | "plate" | "mat" | "ufer" | "ground_ring" | "structural_metal",
  "length_mm": <from rules/electrode-selection.yaml defaults>,
  "diameter_mm": <from defaults>,
  "burial_depth_mm": <from defaults>,
  "soil_resistivity_ohm_m": <from constraints/electrode-resistance.yaml typical values for inputs.ground_conditions>,
  "ra_ohm_specified": <inputs.target_ra_ohm OR jurisdiction default>,
  "tool_call_pending": true
}
```

**Critical: declare the tool call for Ra computation but do not attempt to compute Ra inline.**

`calc.electrode_resistance` (per WI3) is declared as `executor: "tool"` because BS 7430 Annex F iterative array convergence diverges from LLM inline by 10-25%. Until the Python runtime tool is implemented, emit `tool_call_pending: true` and use the engineer-input Ra (which the engineer has typically derived from a hand calc, prior measurement, or BS 7430 table).

Flag in rationale: "Ra value taken from inputs; tool execution pending runtime support per WI3."

**Ra target check** (from `constraints/electrode-resistance.yaml`):
- TT GB / EU / INT: Ra ≤ 200 Ω practical, Ra × IΔn ≤ 50 V absolute
- TT US: Ra ≤ 25 Ω OR install 2nd electrode (NEC 250.53(A)(2))
- TN-C-S: Ra typically supplementary; no hard target

If Ra fails the target, emit a flag in `compliance_summary.non_compliance_flags[]`:
```json
{"message": "Specified Ra <value>Ω exceeds target per <code clause>", "code_clause": "...", "severity": "warning"}
```

---

## Step 6 — Main protective bonding

For each entry in `inputs.extraneous_parts`, emit one `ir.main_bonding[]` row:

```json
{
  "id": "B1" | "B2" | ...,
  "source": "MET",
  "target": "<water_pipe | gas_pipe | structural_steel | ...>",
  "csa_mm2_or_awg": "<from constraints/bonding-geometry.yaml>",
  "code_clause": "BS 7671 Reg 544.1.1" | "IEC 60364-5-54 Clause 544" | "NEC 250.66"
}
```

**Conductor size (from constraints/bonding-geometry.yaml):**
- GB: Default 10 mm² Cu (typical; oversize for unprotected runs)
- EU/INT: 10 mm² Cu typical (per IEC 60364-5-54)
- US: Per NEC Table 250.66 by largest ungrounded service conductor (e.g. for #4 AWG Cu service → 8 AWG GEC; for 250 kcmil service → 2 AWG)

**Code clause field** must cite the relevant rule precisely (with the appendix where applicable, e.g. "BS 7671 Reg 544.1.1" not just "BS 7671").

---

## Step 7 — Supplementary bonding (only if applicable)

If `inputs.supplementary_bonding_required_locations` is non-empty, emit one
`ir.supplementary_bonding[]` row per location:

```json
{
  "location": "bathroom" | "pool" | ...,
  "items_bonded": [<list — typically all metalwork in the zone>],
  "csa_mm2_or_awg": "<from constraints/bonding-geometry.yaml supplementary>",
  "code_clause": "BS 7671 Section 701 Reg 415.2.1" | "IEC 60364-7-701" | "NEC 680.26"
}
```

For bathrooms — typical items: bath taps, towel rail, exposed pipework, light fitting metalwork.
For pools — pool steel reinforcement, deck steel, metal fittings, equipment within 5 ft.

If no supplementary bonding required, omit `ir.supplementary_bonding` entirely OR include as `[]`.

---

## Step 8 — CPC sizing per circuit

For each circuit:
- Source priority: `cross_drawing_context.db-layout.payload.circuits[]` (if present)
- Fallback: `inputs.db_designations` and any user-provided circuit list

For each circuit, populate `ir.circuits[i]`:

```json
{
  "circuit_id": "<from intent or input>",
  "db_designation": "<board id>",
  "voltage_class": "LV_power" | "ELV_control" | ...,
  "breaker_rating_a": <integer>,
  "breaker_curve": "B" | "C" | "D",
  "route_length_m": <from intent or input>,
  "cpc_csa_mm2_or_awg": "<sized per cpc-sizing.yaml>",
  "cpc_sizing_method": "bs7671_table_54.7" | "bs7671_adiabatic_54.1" | "iec60364_table_54.2" | "iec60364_adiabatic_543.1.2" | "nec_table_250.122",
  "cpc_sizing_clause": "BS 7671 Table 54.7" | "IEC 60364-5-54 Table 54.2" | "NEC Table 250.122",
  "zs_ohm": <computed in Step 9>,
  "zs_max_ohm": <from Zs table in Step 9>,
  "zs_compliance": "<set in Step 9>",
  "rcd_required": <set in Step 10>,
  "rcd_type": <set in Step 10>,
  "rcd_sensitivity_ma": <set in Step 10>
}
```

**CPC sizing logic (from rules/cpc-sizing.yaml):**

- **GB (BS 7671 Table 54.7):** emit `cpc_sizing_method: "bs7671_table_54.7"`
  - S ≤ 16 mm² → CPC = S
  - 16 < S ≤ 35 mm² → CPC = 16 mm²
  - S > 35 mm² → CPC = S/2

- **EU / INT (IEC 60364-5-54 Table 54.2):** emit `cpc_sizing_method: "iec60364_table_54.2"`
  - Same banded rule as BS 7671 Table 54.7

- **US (NEC Table 250.122 by OCPD rating):** emit `cpc_sizing_method: "nec_table_250.122"`
  - OCPD ≤ 15 A → EGC #14 AWG Cu
  - 20 A → #12; 30-60 A → #10; 100 A → #8; 200 A → #6; 400 A → #3; 800 A → #1/0; 1200 A → #3/0; 2000 A → 250 kcmil

Use the adiabatic variant (`bs7671_adiabatic_54.1` or `iec60364_adiabatic_543.1.2`) only when the engineer has specified an adiabatic calc or when the table method yields an impractical CSA. If `calc.cpc_adiabatic` is needed but the runtime tool is absent, set `tool_call_pending: true` on the cpc object instead of changing the enum.

---

## Step 9 — Zs verification at each circuit endpoint

For each circuit:

```
Zs = Ze + R1 + R2
```

Where:
- `Ze` = inputs.ze_ohm_declared (supply side, from DNO)
- `R1` = line conductor impedance over circuit length = (resistivity_Ω·mm²/m / line_csa_mm²) × length_m
- `R2` = CPC impedance over circuit length, computed analogously

For a quick approximation, use:
- Cu @ 70°C resistivity: 22 mΩ·mm²/m (BS 7671 Table I1)
- For Al, use 35 mΩ·mm²/m

Look up `zs_max_ohm` from the loaded standards file:
- **GB**: `BS7671/reg411-disconnection-times.json` — Tables 41.1 (5 s) / 41.3 (0.4 s) by breaker type + rating + curve
- **EU/INT**: `IEC60364/part4-41-electric-shock.json` — same logic, IEC clause references
- **US**: NEC doesn't have a direct Zs_max table; use 250.4(A)(5) effective ground-fault path requirement → Zs ≤ 230 V / breaker rating for instantaneous magnetic trip

Set `zs_compliance`:
- `pass` if Zs ≤ zs_max_ohm
- `fail_needs_rcd` if Zs > zs_max_ohm BUT 30 mA RCD installed downstream (passes via RCD ADS path)
- `fail_oversize_cpc` if Zs > zs_max_ohm AND no RCD; recommend oversizing CPC
- `pass_with_rcd` if both conditions met (Zs > zs_max AND RCD present and required regardless)

For TT system: zs_compliance is always evaluated against RCD-based ADS (because no realistic Zs meets the disconnection time without RCD).

---

## Step 10 — RCD requirement check

For each circuit, determine `rcd_required`:

**TT system (any jurisdiction):** ALL circuits require 30 mA RCD for ADS.

**TN-C-S GB:** Per BS 7671 Reg 411.3.3 — RCD required for:
- All socket outlets rated ≤ 32 A (Reg 411.3.3)
- Mobile equipment rated ≤ 32 A (Reg 411.3.3)
- Bathroom circuits (Section 701)
- Outdoor receptacles (Reg 411.3.3)
- Cables concealed in walls at depth < 50 mm (Reg 522.6.202)
- EV chargers (Section 722)
- Lighting circuits in domestic premises (Amendment 2; 17th Ed onwards)

**TN-C-S EU/INT:** Per IEC 60364-4-41 — similar pattern + national supplements.

**TN-C-S US (NEC):** GFCI required for specific locations per NEC 210.8 (bathrooms, kitchens, garages, outdoor, basements, dishwashers, near sinks, etc.); AFCI per 210.12 (most dwelling-unit circuits).

For each `rcd_required: true` circuit:
- `rcd_type`: default to `inputs.rcd_type_default` (typically "A"); upgrade to "B" if circuit serves EV charger / PV / VFD-driven equipment per the breaker_curve / voltage_class context
- `rcd_sensitivity_ma`: 30 mA for personnel protection (standard); 6 mA for NEC GFCI; 100/300 mA for fire protection only

Add to `compliance_summary.assumptions[]` any RCD type upgrade reasoning.

---

## Step 11 — Compliance flag emission

Roll up the per-circuit and per-bonding outcomes:

```json
"compliance_summary": {
  "compliant": <true if all zs_compliance in {pass, pass_with_rcd} AND all required bonding present AND all required RCDs flagged>,
  "non_compliance_flags": [
    {"message": "<specific issue>", "code_clause": "<specific clause>", "severity": "critical" | "warning" | "info"}
  ],
  "assumptions": [
    "<list of ASSUMPTIONS made during the design — e.g. 'Ra=180Ω assumed from engineer input pending runtime tool; soil resistivity 100Ω·m assumed from ground_conditions=unknown'>"
  ]
}
```

Emit a top-level `flags` array with chat-facing high-signal markers:
- `"NON-COMPLIANCE"` if `compliance_summary.compliant == false`
- `"INCOMPLETE-INPUT"` if any required input missing
- `"TOOL-CALL-PENDING"` if any electrode `tool_call_pending == true` (runtime tool not yet implemented)

---

## Step 12 (final) — Emit rationale block

Per WI2 (shared/schemas/core/rationale.schema.json), populate `ir.rationale`:

### chat_summary (40-500 chars)

Tell the engineer:
1. Earthing system + jurisdiction (1 sentence)
2. Key decisions on bonding and electrodes (1-2 sentences)
3. Any flags or assumptions (1 sentence)
4. Invitation to refine (1 short)

Example: "TN-C-S earthing for a UK dwelling, MET in meter cupboard with PME bond at DNO supply. Water + gas main bonding at 10 mm² Cu. 1 supplementary electrode (rod, 2.4 m, target Ra ≤ 200 Ω) — tool-call pending for live Ra calc. All 8 circuits Zs-compliant under PME; 2 require RCD per Reg 411.3.3. Reply to refine, e.g. 'add solar PV'."

### sections (in this order, only if applicable)

1. **Earthing System** — always. Cite the system type + jurisdictional clause + terminology equivalent.
2. **Main Earthing Terminal** — always. Location + supply bond type + main earthing conductor size.
3. **Electrodes** — always (even for TN-C-S, state what supplementary or none).
4. **Main Bonding** — always. List each bonded extraneous part with conductor size + clause.
5. **Supplementary Bonding** — only if any.
6. **CPC + Zs Verification** — always. Summarize the sizing method and verification result.
7. **RCD Requirements** — always. Summarize which circuits require RCD and why.
8. **Compliance** — always. Final pass/fail + non-compliance flag list.
9. **Assumptions** — always (one decision per assumption).

Each section: `{title, summary, decisions}`.

Each decision: `{label, summary, rule, code_clause, inputs}` — where `code_clause` cites the specific section/regulation, and `inputs` captures the structured map of values that drove the decision.

**The whole rationale is your audit trail.** Skipping a section because "it's obvious" is wrong — every design dimension must produce a decision record.

---

## Final output

Emit a single JSON document that:
1. Conforms to `electrical/earthing/schemas/earthing-ir.schema.json` exactly
2. Has `drawing_type: "earthing_schematic"`
3. Has `version: "1.0.0"`
4. Has `meta.skill_version: "1.0.0"`, `meta.produced_at` ISO 8601 timestamp, `meta.consumed_intents` per Step 1
5. Has `drawn_as_symbols` — every entry must resolve in `IEC60617/symbol-index.json` (typical entries: `EARTH_GENERAL`, `EARTH_PROTECTIVE`, `EARTH_ELECTRODE`, `CONDUCTOR_PE`, `CONDUCTOR_PEN`, `JUNCTION_T`, `BUSBAR`)
6. Has a fully populated `rationale` block per Step 12

**Do not invent symbol IDs.** Validate every `drawn_as_symbols` entry against `IEC60617/symbol-index.json` before emitting.

**Do not paraphrase code clauses.** Cite them exactly as they appear in the loaded standards file (e.g. "BS 7671:2018+A3 Reg 411.5.3", not just "BS 7671 411.5").

**Do not skip the rationale.** It is the engineer's audit trail.
````

- [ ] **Step 2: Validate file is non-empty and has all 12 step markers**

Run:
```bash
test -s electrical/earthing/prompts/generator.md && echo "OK: file exists and is non-empty"
grep -c "^## Step " electrical/earthing/prompts/generator.md
```
Expected: `OK: file exists and is non-empty` then `12`

- [ ] **Step 3: Verify the prompt references specific standards files (consumption-pattern proof)**

Run:
```bash
python3 -c "
text = open('electrical/earthing/prompts/generator.md').read()
files_referenced = sum(text.count(p) > 0 for p in [
    'BS7671/reg411-disconnection-times.json',
    'BS7671/reg411-rcd-requirements.json',
    'IEC60364/part4-41-electric-shock.json',
    'IEC60364/part5-54-earthing.json',
    'NFPA70/art250-grounding-bonding.json',
    'NFPA70/grounding-and-bonding.json',
    'IEC60617/symbol-index.json',
    'IEC60617/part2-general.json',
])
folders_referenced = sum(p in text for p in ['BS7671/', 'IEC60364/', 'NFPA70/', 'IEC60617/'])
# Standard folder paths appear as part of file paths, so we exclude file paths from the folder count
print(f'Specific standards files referenced: {files_referenced} / 8')
assert files_referenced == 8, 'Generator prompt must reference all 8 standards files explicitly'
print('Consumption-pattern proof in generator.md: OK')
"
```
Expected: `Specific standards files referenced: 8 / 8` then `Consumption-pattern proof in generator.md: OK`

- [ ] **Step 4: Commit**

```bash
git add electrical/earthing/prompts/generator.md
git commit -m "feat: earthing generator.md — 12-step reasoning chain, consumption-pattern proof"
```

---

### Task 9: Create `prompts/validator.md`

**Files:**
- Create: `electrical/earthing/prompts/validator.md`

This prompt is invoked by the eval runner. It validates that an emitted IR conforms to the schema AND to the engineering rules (not just JSON-schema-valid but engineering-valid).

- [ ] **Step 1: Write the validator prompt**

````markdown
# Earthing Schematic — Validator Prompt

You are validating an earthing schematic IR document produced by the `electrical/earthing` skill generator.

## Input
- An IR JSON document at the user-provided path.
- The canonical schema at `electrical/earthing/schemas/earthing-ir.schema.json`.
- The intent schema at `electrical/earthing/schemas/earthing-intent.schema.json`.

## Validation procedure

### 1. Schema validation
Run JSON-schema validation against `earthing-ir.schema.json`.
- If invalid: STOP. Emit `{"valid": false, "stage": "schema", "errors": [...]}`.

### 2. Cross-field invariants

For each item below, emit a violation if the rule fails.

**INV-1: MET reference integrity.**
Every `circuits[*].cpc.terminated_at_met_id` must equal `met.id`.

**INV-2: Electrode jurisdiction-system match.**

| jurisdiction | earthing_system | electrodes required |
|---|---|---|
| GB | TN-C-S | ≥0 (PME — DNO provides earth) |
| GB | TT | ≥1 |
| EU/INT | TN-C-S | ≥0 |
| EU/INT | TT | ≥1 |
| US | TN-S (NEC default) | ≥2 supplemental electrodes per NEC 250.53(A)(2) unless one rod meets ≤25Ω |

**INV-3: Bonding completeness.**
If `extraneous_parts` (from inputs.json) lists any item, every item must appear in `main_bonding.conductors[]` OR be marked `bonded_via: "structural"` in the rationale.

**INV-4: CPC sizing method per jurisdiction.**

| jurisdiction | allowed cpc_sizing_method values |
|---|---|
| GB | `bs7671_table_54.7`, `bs7671_adiabatic_54.1` |
| EU/INT | `iec60364_table_54.2`, `iec60364_adiabatic_543.1.2` |
| US | `nec_table_250.122` |

**INV-5: Zs check arithmetic.**
For every circuit: `zs_calculated_ohm == ze_ohm + r1_ohm + r2_ohm` (within 0.001Ω rounding). And `zs_calculated_ohm ≤ zs_max_ohm`.

**INV-6: RCD requirement.**
- TT system: every circuit must have `rcd_required: true`.
- TN-C-S + GB + circuit serving socket-outlets ≤32A in domestic: `rcd_required: true` per BS 7671 Reg 411.3.3.

**INV-7: Symbol references.**
Every `drawn_as_symbols[*].symbol_id` must exist in `shared/standards/electrical/IEC60617/symbol-index.json`.

**INV-8: Rationale presence.**
`rationale` block must exist at root and contain `chat_summary`, all 8 taxonomy keys, and `decisions` array with ≥3 entries.

**INV-9: Standards citations.**
Every `compliance_summary.clauses_cited[]` entry must use exact clause format:
- BS 7671: `"BS 7671:2018+A3 Reg N.N.N"` or `"BS 7671:2018+A3 Table N.N"`
- IEC 60364: `"IEC 60364-N-NN:YYYY clause N.NN.N"`
- NEC: `"NEC 2023 Art NNN.NN"` or `"NEC 2023 Table NNN.NN"`

### 3. Intent extraction validation

Project the IR down to the intent shape declared by `earthing-intent.schema.json`. Validate against that schema. The intent must contain the stable subset: `jurisdiction, earthing_system, met_location, available_zs_at_main_db_ohm, electrode_target_met, circuits`.

## Output

Emit a single JSON object:

```json
{
  "valid": true | false,
  "stage": "schema" | "invariants" | "intent" | "passed",
  "errors": [
    {"code": "INV-N", "path": "$.circuits[2].cpc", "message": "..."}
  ],
  "warnings": [...]
}
```

`valid: true` requires ALL of: schema pass, all 9 invariants pass, intent extraction valid.
````

- [ ] **Step 2: Validate file exists and contains all 9 invariants**

Run:
```bash
test -s electrical/earthing/prompts/validator.md && echo "OK"
grep -c "^\*\*INV-" electrical/earthing/prompts/validator.md
```
Expected: `OK` then `9`

- [ ] **Step 3: Commit**

```bash
git add electrical/earthing/prompts/validator.md
git commit -m "feat: earthing validator.md — 9 cross-field invariants + intent extraction check"
```

---

### Task 10: Create `prompts/reviewer.md`

**Files:**
- Create: `electrical/earthing/prompts/reviewer.md`

The reviewer prompt is invoked by the eval runner to score qualitative aspects that schema/invariant validation cannot catch: was the reasoning sound, was the cited clause actually relevant, is the design defensible?

- [ ] **Step 1: Write the reviewer prompt**

````markdown
# Earthing Schematic — Reviewer Prompt

You are a senior chartered electrical engineer reviewing an earthing schematic IR produced by the `electrical/earthing` skill.

You are NOT validating schema — that has already been done. You are reviewing **engineering judgement**.

## Input
- IR JSON document
- Inputs JSON (engineer's brief)
- For UK projects: the relevant BS 7671:2018+A3 regulations
- For international projects: IEC 60364-4-41 and -5-54
- For US projects: NEC 2023 Article 250

## Review dimensions

For each dimension, give a score 1–5 and a one-line justification.

### D1: Earthing-system classification correctness
Did the IR correctly identify TN-C-S vs TT vs TN-S based on the brief? Common mistakes:
- Treating PME (TN-C-S) as TN-S
- Missing TT requirement when DNO declines to provide PME earth
- Misclassifying generator-fed installations

### D2: Electrode adequacy
For TT systems, is the target Ra ≤ R_target_ohm reasonable given the soil type (if declared)?
- Sandy soil: 1–2 rods rarely achieve ≤200Ω, design must declare additional electrodes or plate.
- Rocky terrain: rod method may be infeasible — design must flag this.

### D3: Bonding completeness
Did the design bond every extraneous-conductive-part declared in `inputs.extraneous_parts`?
Common omissions:
- Structural steel
- Gas service pipe at point of entry
- Water service pipe (UK) or metallic pipe to outside (US)
- Lightning protection system bond (where applicable, BS EN 62305)

### D4: Supplementary bonding judgement
For locations of increased shock risk (bathrooms, swimming pools, agricultural), did the design require supplementary bonding where appropriate?
- BS 7671 Section 701 (bathrooms): supplementary bonding required UNLESS all of three conditions met.
- BS 7671 Section 702 (pools): supplementary bonding always required in Zones 0–2.
- NEC 680 (pools): equipotential bonding grid required.

### D5: CPC sizing method appropriateness
Was the chosen `cpc_sizing_method` defensible for the circuit?
- Table method (54.7) is conservative and fast — appropriate when the phase conductor is small.
- Adiabatic method (54.1) is required when table method is impractical or yields oversize CPC.

### D6: Zs vs Zs_max margin
Are the Zs values realistic given the cable length and CSA? Is there enough headroom for temperature correction (BS 7671 calls for 1.20× factor)?

### D7: Rationale quality
Is the rationale's `chat_summary` a faithful one-paragraph explanation a building-control officer could read and understand? Are decisions actually justified, not just listed?

### D8: Standards citation accuracy
For each clause cited in `compliance_summary.clauses_cited`, does the clause actually support the decision the IR claims it supports? (Read the clause from the loaded standards file before answering.)

## Output

```json
{
  "scores": {
    "D1": 5, "D2": 4, "D3": 5, "D4": 5, "D5": 4, "D6": 4, "D7": 5, "D8": 5
  },
  "justifications": {
    "D1": "...",
    "D2": "..."
  },
  "verdict": "pass" | "pass-with-warnings" | "fail",
  "must_fix": ["..."],
  "should_fix": ["..."],
  "consider": ["..."]
}
```

- **pass**: all dimensions ≥4, no must-fix.
- **pass-with-warnings**: all dimensions ≥3, no D1/D3/D4/D8 below 4.
- **fail**: any dimension at 1–2, or D1/D3/D4/D8 below 4.

Be honest. A failing earthing design risks electric shock — this is not a place for false positives.
````

- [ ] **Step 2: Validate file exists and contains all 8 dimensions**

Run:
```bash
test -s electrical/earthing/prompts/reviewer.md && echo "OK"
grep -c "^### D" electrical/earthing/prompts/reviewer.md
```
Expected: `OK` then `8`

- [ ] **Step 3: Commit**

```bash
git add electrical/earthing/prompts/reviewer.md
git commit -m "feat: earthing reviewer.md — 8 engineering-judgement dimensions"
```

---

### Task 11: Create 3 validation YAMLs

**Files:**
- Create: `electrical/earthing/validation/zs-compliance.yaml`
- Create: `electrical/earthing/validation/bonding-completeness.yaml`
- Create: `electrical/earthing/validation/cpc-sizing.yaml`

These validation files declare deterministic checks the runtime can apply against any earthing IR. They are JSONPath + assertion rules.

- [ ] **Step 1: Write `zs-compliance.yaml`**

```yaml
# Earthing — Zs compliance validation
# Asserts every circuit meets Zs ≤ Zs_max per its protective device
version: 1.0.0
applies_to_drawing_types: ["earthing_schematic"]

checks:
  - id: zs-001-arithmetic
    name: Zs arithmetic must equal Ze + R1 + R2
    severity: critical
    jsonpath: "$.circuits[*]"
    assert: "abs(zs_calculated_ohm - (ze_ohm + r1_ohm + r2_ohm)) <= 0.001"
    message: "Circuit {circuit_id}: declared zs_calculated_ohm does not equal ze_ohm + r1_ohm + r2_ohm"
    standard_ref: "BS 7671:2018+A3 Reg 411.4.4"

  - id: zs-002-within-limit
    name: Zs must not exceed Zs_max
    severity: critical
    jsonpath: "$.circuits[*]"
    assert: "zs_calculated_ohm <= zs_max_ohm"
    message: "Circuit {circuit_id}: Zs ({zs_calculated_ohm}Ω) exceeds Zs_max ({zs_max_ohm}Ω) — disconnection time will not be met"
    standard_ref: "BS 7671:2018+A3 Reg 411.4.5"

  - id: zs-003-temperature-correction
    name: Zs_max must be the temperature-corrected value (0.8× of tabulated)
    severity: high
    jsonpath: "$.circuits[*]"
    assert: "zs_max_source in ['table_41.2_corrected', 'table_41.3_corrected', 'table_41.4_corrected', 'nec_calculated']"
    message: "Circuit {circuit_id}: Zs_max source must be a temperature-corrected reference"
    standard_ref: "BS 7671:2018+A3 Appendix 14"

  - id: zs-004-rcd-fallback
    name: If Zs is high, an RCD must be present to meet disconnection time
    severity: high
    jsonpath: "$.circuits[?(@.zs_calculated_ohm > @.zs_max_ohm_no_rcd)]"
    assert: "rcd_required == true and rcd_rating_ma <= 300"
    message: "Circuit {circuit_id}: Zs exceeds the no-RCD limit but no RCD is specified"
    standard_ref: "BS 7671:2018+A3 Reg 411.4.204"
```

- [ ] **Step 2: Write `bonding-completeness.yaml`**

```yaml
# Earthing — bonding completeness validation
version: 1.0.0
applies_to_drawing_types: ["earthing_schematic"]

checks:
  - id: bond-001-met-exists
    name: Main earthing terminal must be declared
    severity: critical
    jsonpath: "$.met"
    assert: "id != null and location != null"
    message: "MET (Main Earthing Terminal) is missing — every earthing schematic must declare a MET"
    standard_ref: "BS 7671:2018+A3 Reg 542.4.1"

  - id: bond-002-water-service-bonded-gb
    name: GB — water service entry must be bonded if metallic
    severity: high
    jsonpath: "$"
    when: "jurisdiction == 'GB' and inputs.water_service_metallic == true"
    assert: "any(b.bonds_to == 'water_service_entry' for b in main_bonding.conductors)"
    message: "Metallic water service is declared but no main bonding conductor terminates there"
    standard_ref: "BS 7671:2018+A3 Reg 411.3.1.2"

  - id: bond-003-gas-service-bonded-gb
    name: GB — gas service entry must be bonded if metallic
    severity: high
    jsonpath: "$"
    when: "jurisdiction == 'GB' and inputs.gas_service_metallic == true"
    assert: "any(b.bonds_to == 'gas_service_entry' for b in main_bonding.conductors)"
    message: "Metallic gas service is declared but no main bonding conductor terminates there"
    standard_ref: "BS 7671:2018+A3 Reg 411.3.1.2"

  - id: bond-004-structural-steel-bonded
    name: Structural steel must be bonded where it is an extraneous-conductive-part
    severity: high
    jsonpath: "$"
    when: "any(e.kind == 'structural_steel' for e in inputs.extraneous_parts)"
    assert: "any(b.bonds_to == 'structural_steel' for b in main_bonding.conductors)"
    message: "Structural steel declared as extraneous-conductive-part but not bonded to MET"
    standard_ref: "BS 7671:2018+A3 Reg 411.3.1.2 / IEC 60364-4-41 clause 411.3.1.2"

  - id: bond-005-supplementary-bathroom
    name: Bathroom locations must have supplementary bonding unless exemption met
    severity: high
    jsonpath: "$"
    when: "any(loc.kind == 'bathroom' for loc in inputs.supplementary_bonding_required_locations)"
    assert: "supplementary_bonding.zones[?(@.zone_kind == 'bathroom')] != null OR exemption_701.415.2_met == true"
    message: "Bathroom requires supplementary bonding per BS 7671 Section 701 unless the 701.415.2 exemption is documented"
    standard_ref: "BS 7671:2018+A3 Section 701"

  - id: bond-006-cpc-size-not-smaller-than-l
    name: For circuits using table method, CPC must not be smaller than required by Table 54.7
    severity: critical
    jsonpath: "$.circuits[?(@.cpc.cpc_sizing_method == 'bs7671_table_54.7')]"
    assert: "cpc.csa_mm2 >= table_54_7_required_csa_mm2"
    message: "Circuit {circuit_id}: CPC of {cpc.csa_mm2}mm² is undersized for phase {line_csa_mm2}mm² per Table 54.7"
    standard_ref: "BS 7671:2018+A3 Table 54.7"
```

- [ ] **Step 3: Write `cpc-sizing.yaml`**

```yaml
# Earthing — CPC sizing rule validation per jurisdiction
version: 1.0.0
applies_to_drawing_types: ["earthing_schematic"]

checks:
  - id: cpc-001-method-jurisdiction-match
    name: cpc_sizing_method enum must match jurisdiction
    severity: critical
    jsonpath: "$.circuits[*].cpc"
    assert: |
      (jurisdiction == 'GB' and cpc_sizing_method in ['bs7671_table_54.7', 'bs7671_adiabatic_54.1'])
      or (jurisdiction in ['EU', 'INT'] and cpc_sizing_method in ['iec60364_table_54.2', 'iec60364_adiabatic_543.1.2'])
      or (jurisdiction == 'US' and cpc_sizing_method == 'nec_table_250.122')
    message: "Circuit {circuit_id}: cpc_sizing_method {cpc_sizing_method} is not valid for jurisdiction {jurisdiction}"
    standard_ref: "manifest standards table"

  - id: cpc-002-bs7671-table-54.7-minimums
    name: BS 7671 Table 54.7 minimum CSAs
    severity: critical
    jsonpath: "$.circuits[?(@.cpc.cpc_sizing_method == 'bs7671_table_54.7')]"
    assert: |
      (line_csa_mm2 <= 16 and cpc.csa_mm2 == line_csa_mm2)
      or (line_csa_mm2 > 16 and line_csa_mm2 <= 35 and cpc.csa_mm2 == 16)
      or (line_csa_mm2 > 35 and cpc.csa_mm2 == line_csa_mm2 / 2)
    message: "Circuit {circuit_id}: CPC CSA does not match Table 54.7 for L={line_csa_mm2}mm²"
    standard_ref: "BS 7671:2018+A3 Table 54.7"

  - id: cpc-003-nec-table-250.122-rating-based
    name: NEC Table 250.122 sizes EGC by OCPD rating, not by phase CSA
    severity: critical
    jsonpath: "$.circuits[?(@.cpc.cpc_sizing_method == 'nec_table_250.122')]"
    assert: |
      (ocpd_rating_a <= 15 and cpc.csa_awg == '14')
      or (ocpd_rating_a <= 20 and cpc.csa_awg == '12')
      or (ocpd_rating_a <= 60 and cpc.csa_awg == '10')
      or (ocpd_rating_a <= 100 and cpc.csa_awg == '8')
      or (ocpd_rating_a <= 200 and cpc.csa_awg == '6')
    message: "Circuit {circuit_id}: EGC size does not match NEC Table 250.122 for OCPD {ocpd_rating_a}A"
    standard_ref: "NEC 2023 Table 250.122"

  - id: cpc-004-min-csa-mechanical
    name: Minimum CPC CSA where not part of cable assembly (BS 7671 Reg 543.1.1)
    severity: high
    jsonpath: "$.circuits[?(@.cpc.in_same_wiring_system == false)]"
    assert: "cpc.csa_mm2 >= 4 or (cpc.csa_mm2 >= 2.5 and cpc.mechanically_protected == true)"
    message: "Circuit {circuit_id}: separate CPC must be ≥4mm² (or ≥2.5mm² if mechanically protected)"
    standard_ref: "BS 7671:2018+A3 Reg 543.1.1"
```

- [ ] **Step 4: Validate all 3 files**

Run:
```bash
test -s electrical/earthing/validation/zs-compliance.yaml && \
test -s electrical/earthing/validation/bonding-completeness.yaml && \
test -s electrical/earthing/validation/cpc-sizing.yaml && \
echo "OK: all 3 validation files exist"
python3 -c "
import yaml
for f in ['zs-compliance', 'bonding-completeness', 'cpc-sizing']:
    d = yaml.safe_load(open(f'electrical/earthing/validation/{f}.yaml'))
    print(f'{f}: {len(d[\"checks\"])} checks')
"
```
Expected: `OK: all 3 validation files exist`, then 4 + 6 + 4 = 14 total checks

- [ ] **Step 5: Commit**

```bash
git add electrical/earthing/validation/
git commit -m "feat: earthing validation — 14 deterministic checks (Zs/bonding/CPC)"
```

---

### Task 12: Create `ontology/earthing-system-types.json`

**Files:**
- Create: `electrical/earthing/ontology/earthing-system-types.json`

This ontology file is a machine-readable lookup that the generator and validator both reference. It declares the canonical earthing-system taxonomy and what each implies.

- [ ] **Step 1: Write the ontology**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "ontology_type": "earthing_system_types",
  "version": "1.0.0",
  "source": "IEC 60364-1 clause 312.2, BS 7671:2018+A3 Part 2",
  "systems": [
    {
      "id": "TN-S",
      "name": "TN-S",
      "description": "Separate Neutral and Protective Earth conductors throughout the supply",
      "earth_source": "DNO transformer star point via separate PE conductor",
      "common_in": ["GB pre-1970 installations", "US (NEC default)"],
      "electrode_required_at_consumer": false,
      "typical_ze_ohm_range": [0.05, 0.5],
      "typical_use_case": "Older UK installations, all US installations",
      "rcd_blanket_requirement": false,
      "notes": "In NEC terms this is the standard grounded-system arrangement: neutral grounded at service, EGC bonded to grounded conductor only at service equipment."
    },
    {
      "id": "TN-C-S",
      "name": "TN-C-S (PME)",
      "description": "Combined Neutral and Earth (PEN) from transformer to service head, then separate within installation",
      "earth_source": "DNO PEN conductor — Protective Multiple Earthing",
      "common_in": ["GB post-1970 installations (~95%)", "Most of EU"],
      "electrode_required_at_consumer": false,
      "electrode_optional_at_consumer": true,
      "typical_ze_ohm_range": [0.10, 0.35],
      "typical_use_case": "Default for UK domestic and commercial; PME earth provided by DNO",
      "rcd_blanket_requirement": false,
      "rcd_required_for": ["sockets ≤32A in domestic per BS 7671 411.3.3", "outdoor circuits", "bathroom circuits", "EV chargepoints (open-PEN risk)"],
      "notes": "PME has open-PEN risk; EV chargers, marinas, agricultural require special measures (BS 7671 Section 722, 709, 705)."
    },
    {
      "id": "TT",
      "name": "TT",
      "description": "No DNO earth — installation provides its own earth electrode",
      "earth_source": "Local earth electrode (rod, plate, mat) at the installation",
      "common_in": ["Rural UK (where DNO declines PME)", "Rural EU", "Caravan sites"],
      "electrode_required_at_consumer": true,
      "typical_ra_ohm_target_max": 200,
      "typical_ra_ohm_target_preferred": 100,
      "rcd_blanket_requirement": true,
      "rcd_blanket_requirement_reason": "Disconnection time cannot be met by overcurrent alone — Ra is too high. RCD enforces 30/100/300mA fault disconnection per BS 7671 411.5.3",
      "notes": "TT requires an RCD on every final circuit (or upstream covering all circuits). Ra target ≤200Ω is the disconnection floor; ≤100Ω is the design target for headroom."
    },
    {
      "id": "IT",
      "name": "IT",
      "description": "Source is either isolated from earth or earthed through high impedance; exposed-conductive-parts earthed locally",
      "earth_source": "Local earth electrode; source impedance to earth limits first-fault current",
      "common_in": ["Hospitals — Group 2 medical locations", "Industrial processes that must not trip on first fault"],
      "electrode_required_at_consumer": true,
      "rcd_blanket_requirement": false,
      "first_fault_behaviour": "no_disconnection_required",
      "second_fault_behaviour": "disconnection_required",
      "notes": "Out of scope for stage 1 of this skill. Requires Insulation Monitoring Device (IMD)."
    },
    {
      "id": "TN-C",
      "name": "TN-C",
      "description": "Combined Neutral+Earth conductor throughout — NO separation within the installation",
      "earth_source": "DNO PEN, not split inside installation",
      "common_in": [],
      "electrode_required_at_consumer": false,
      "rcd_blanket_requirement": false,
      "permitted": false,
      "permitted_reason": "Prohibited in installations covered by BS 7671 and most current EU/IEC codes — RCDs cannot function correctly on a TN-C system",
      "notes": "Listed for completeness only. Never specify in a new design."
    }
  ],
  "jurisdiction_defaults": {
    "GB": {
      "default_system": "TN-C-S",
      "rural_fallback": "TT",
      "permitted_systems": ["TN-S", "TN-C-S", "TT"]
    },
    "EU": {
      "default_system": "TN-C-S",
      "rural_fallback": "TT",
      "permitted_systems": ["TN-S", "TN-C-S", "TT", "IT"]
    },
    "INT": {
      "default_system": "TN-C-S",
      "rural_fallback": "TT",
      "permitted_systems": ["TN-S", "TN-C-S", "TT", "IT"]
    },
    "US": {
      "default_system": "TN-S",
      "rural_fallback": "TN-S",
      "permitted_systems": ["TN-S"],
      "notes": "NEC uses different terminology — 'grounded system' ≈ TN-S. NEC 250 requires supplemental grounding electrodes regardless."
    }
  }
}
```

- [ ] **Step 2: Validate JSON parses and contains all 5 systems**

Run:
```bash
python3 -c "
import json
d = json.load(open('electrical/earthing/ontology/earthing-system-types.json'))
ids = [s['id'] for s in d['systems']]
assert set(ids) == {'TN-S', 'TN-C-S', 'TT', 'IT', 'TN-C'}, f'Wrong systems: {ids}'
assert set(d['jurisdiction_defaults'].keys()) == {'GB', 'EU', 'INT', 'US'}
print('Ontology OK — 5 systems + 4 jurisdictions')
"
```
Expected: `Ontology OK — 5 systems + 4 jurisdictions`

- [ ] **Step 3: Commit**

```bash
git add electrical/earthing/ontology/earthing-system-types.json
git commit -m "feat: earthing ontology — TN-S/TN-C-S/TT/IT/TN-C + jurisdiction defaults"
```

---

### Task 13: Create 2 docs files

**Files:**
- Create: `electrical/earthing/docs/engineering-philosophy.md`
- Create: `electrical/earthing/docs/known-limitations.md`

These mirror the pattern from `electrical/lighting-layout/docs/` and document the *why* behind the skill design.

- [ ] **Step 1: Write `engineering-philosophy.md`**

```markdown
# Earthing Skill — Engineering Philosophy

## Why this skill exists

Earthing design is the single largest source of electrical safety failures in real buildings. Most CAD packages let designers draw an earthing schematic without ever asking whether the disconnection time will actually be met. This skill enforces the BS 7671 / IEC 60364 / NEC reasoning chain *before* the IR is emitted.

## What "good earthing design" looks like

A correct earthing schematic answers six questions in order:

1. **What earthing system applies?** (TN-C-S / TT / TN-S — driven by DNO declaration, not designer preference)
2. **Where is the MET?** (single point, accessible, labelled)
3. **What electrodes — if any — are needed?** (TT: always; TN-C-S: optional but recommended ≤200Ω; NEC: always supplemental)
4. **What bonding is required?** (every extraneous-conductive-part to the MET)
5. **What CPC for every circuit?** (table method OR adiabatic OR NEC 250.122)
6. **Does Zs meet the disconnection time?** (Ze + R1 + R2 ≤ Zs_max for that protective device)

Question 6 is the gate. A design that passes 1–5 but fails 6 is not a design.

## The standards-consumption pattern

This skill's generator prompt names specific JSON files from `shared/standards/` rather than the standards as a body of work. The runtime loads only what the jurisdiction requires:

- GB project → load BS 7671 files
- EU/INT project → load IEC 60364 files
- US project → load NFPA 70 (NEC) files
- All projects → load IEC 60617 symbol files

This selective consumption is what makes the skill viable at production scale — the LLM never sees the 70%+ of standards content irrelevant to the current job.

## Why we defer iterative calculations

Earth electrode resistance (Ra) is a function of soil resistivity, electrode geometry, and arrangement. Iterative calculations are not the LLM's strength — small arithmetic errors compound. This skill declares a tool-call contract (`calc.electrode_resistance`) and marks the result `tool_call_pending: true`. The deterministic Python tool will run when the WI3 runtime lands; until then, the engineer provides Ra as input and the skill validates it against the target.

## What this skill will NOT do

- It will not invent soil resistivity values. If the engineer hasn't provided one, the skill emits a compliance flag asking for it.
- It will not paraphrase code clauses. Every cited clause is taken verbatim from the loaded standards JSON.
- It will not silently switch jurisdictions. The first input is `jurisdiction` and the skill refuses to proceed without it.
- It will not draw a plan-view earthing layout in stage 1. That ships in stage 2.
```

- [ ] **Step 2: Write `known-limitations.md`**

```markdown
# Earthing Skill — Known Limitations (Stage 1)

This is the stage 1 (schematic) release. The following are known limitations that will be resolved in later stages.

## Stage 1 scope

- **Output:** schematic IR only
- **Systems supported:** TN-C-S, TT (≈85% of designs)
- **Jurisdictions:** GB, EU, INT, US
- **Calculations:** inline lookup-style only; iterative calcs deferred via `tool_call_pending`

## What is OUT of scope

### IT systems
IT systems (hospitals Group 2, certain industrial) require an Insulation Monitoring Device and have different disconnection rules. Not supported in stage 1. Engineers working on Group 2 medical locations should not use this skill yet.

### Plan-view earthing layout
Stage 1 emits the schematic only. The plan-view layer (which physically locates the MET, electrode runs, ring conductor route, bonding routes) ships in stage 2. The schematic IR will be consumed by the plan-view skill when it exists.

### Declaration-only stage
A lightweight "no-design" mode that emits a compliance declaration referencing an existing earthing design (for tender response, M&E coordination) is deferred to stage 3.

### Earth-fault current calculations
Prospective earth-fault current (Ief) is needed for selectivity and breaking capacity decisions. Not calculated in stage 1 — engineer provides Ze and the skill calculates Zs.

### Lightning protection bonding
BS EN 62305 lightning protection bonding interfaces with the earthing system but is its own skill scope. Stage 1 marks lightning-protection bonds as `bonded_via: "structural"` and defers the design.

### EV charger earthing
Open-PEN protection (BS 7671 Section 722, IET Code of Practice for EV) requires specific measures beyond standard PME treatment. Stage 1 emits a compliance flag if an EV circuit is detected but does not design the open-PEN mitigation.

### Generator-fed earthing
Standby generators have specific earthing requirements (BS 7671 Chapter 55, NEC 250.30). Not supported in stage 1.

## What may produce false positives in evals

- **D6 (Zs margin):** if the engineer provides exact measured Ze (rather than declared), the design may pass with very small margins that the reviewer flags as "low headroom". This is correct engineering judgement, not a bug.
- **INV-3 (bonding completeness):** the skill cannot detect un-declared extraneous-conductive-parts. Garbage-in-garbage-out applies.

## Tool calls awaiting runtime

| Tool name | Purpose | Status |
|---|---|---|
| `calc.electrode_resistance` | Compute Ra from soil resistivity + electrode geometry | tool_call_pending |
| `calc.adiabatic_cpc` | Compute CPC CSA via adiabatic equation for fault energy let-through | tool_call_pending |

When WI3 runtime tools land, the generator prompt's calculation steps will be updated to invoke them instead of accepting engineer input.
```

- [ ] **Step 3: Validate both docs files**

Run:
```bash
test -s electrical/earthing/docs/engineering-philosophy.md && \
test -s electrical/earthing/docs/known-limitations.md && \
echo "OK: both docs files exist"
```
Expected: `OK: both docs files exist`

- [ ] **Step 4: Commit**

```bash
git add electrical/earthing/docs/
git commit -m "docs: earthing engineering-philosophy + known-limitations"
```

---

### Task 14: Create `evals/runner-config.json` and `evals/eval-01-uk-dwelling-tn-cs.yaml`

**Files:**
- Create: `electrical/earthing/evals/runner-config.json`
- Create: `electrical/earthing/evals/eval-01-uk-dwelling-tn-cs.yaml`

This task starts the eval suite. There are 6 evals (eval-01 through eval-06) covering all WI5 categories: happy path, edge cases, validation traps, missing-input handling, jurisdiction switching, rationale block.

- [ ] **Step 1: Write `runner-config.json`**

```json
{
  "$schema": "../../../shared/schemas/core/eval-runner-config.schema.json",
  "skill": "earthing",
  "version": "1.0.0",
  "minimum_model_class": "sonnet",
  "minimum_status": {
    "happy_path": "pass",
    "edge_case": "pass-with-warnings",
    "validation_trap": "pass",
    "missing_input": "pass",
    "jurisdiction_switch": "pass",
    "rationale_block": "pass"
  },
  "evals": [
    "eval-01-uk-dwelling-tn-cs.yaml",
    "eval-02-rural-tt-system.yaml",
    "eval-03-cpc-undersized-trap.yaml",
    "eval-04-missing-soil-resistivity.yaml",
    "eval-05-jurisdiction-us-nec.yaml",
    "eval-06-rationale-block.yaml"
  ],
  "scoring": {
    "schema_validity_weight": 0.25,
    "invariant_pass_weight": 0.35,
    "reviewer_score_weight": 0.30,
    "rationale_quality_weight": 0.10
  }
}
```

- [ ] **Step 2: Write `eval-01-uk-dwelling-tn-cs.yaml`** (happy path)

```yaml
# Eval 01 — UK dwelling, TN-C-S, all consumed-intent layers present
# Category: happy_path
# Standard refs: BS 7671:2018+A3, IEC 60617

id: eval-01-uk-dwelling-tn-cs
category: happy_path
severity: critical
description: |
  Standard UK 3-bed semi-detached dwelling on PME supply. All four upstream skills
  (db-layout, lighting-layout, small-power, plus jurisdictional defaults) have
  produced their intents. Earthing skill must produce a complete TN-C-S schematic
  with correct Zs verification on every circuit.

inputs:
  jurisdiction: "GB"
  earthing_system_declared: "TN-C-S"
  supply_voltage_v: 230
  ze_ohm_declared: 0.35
  water_service_metallic: true
  gas_service_metallic: true
  extraneous_parts:
    - { kind: "structural_steel", location: "loft truss steel" }
  met_location: "consumer unit cupboard, ground floor hallway"
  supplementary_bonding_required_locations:
    - { kind: "bathroom", zone: "first_floor_main_bathroom" }
  consumed_intents:
    - { intent_type: "db-layout", intent_version: "1.0.0", produced_by: "electrical/db-layout/v1.0.0", payload_ref: "test-fixtures/db-layout-eval01.json" }
    - { intent_type: "lighting-layout", intent_version: "1.3.0", produced_by: "electrical/lighting-layout/v1.3.0", payload_ref: "test-fixtures/lighting-eval01.json" }
    - { intent_type: "small-power", intent_version: "1.0.0", produced_by: "electrical/small-power/v1.0.0", payload_ref: "test-fixtures/small-power-eval01.json" }

assertions:
  - kind: schema_valid
    schema: "earthing-ir.schema.json"
  - kind: jsonpath_equals
    path: "$.earthing_system"
    expected: "TN-C-S"
  - kind: jsonpath_equals
    path: "$.jurisdiction"
    expected: "GB"
  - kind: jsonpath_present
    path: "$.met"
  - kind: jsonpath_count_gte
    path: "$.main_bonding.conductors[*]"
    minimum: 3
    note: "water + gas + structural_steel"
  - kind: jsonpath_count_gte
    path: "$.supplementary_bonding.zones[*]"
    minimum: 1
    note: "first_floor bathroom"
  - kind: jsonpath_all_lte
    path: "$.circuits[*].zs_calculated_ohm"
    field_compared_to: "zs_max_ohm"
    note: "Every circuit must satisfy Zs ≤ Zs_max"
  - kind: invariant_passes
    invariant: "INV-5"
    note: "Zs arithmetic"
  - kind: invariant_passes
    invariant: "INV-3"
    note: "Bonding completeness"
  - kind: clause_cited
    clause_pattern: "^BS 7671:2018\\+A3 Reg 411\\."
    minimum_count: 2
  - kind: rationale_present
    require_sections: ["chat_summary", "engineering_objectives", "constraints", "regulatory_basis", "key_decisions", "assumptions", "design_methodology", "risks", "evidence"]

expected_status: "pass"
```

- [ ] **Step 3: Validate both eval files parse**

Run:
```bash
python3 -c "
import json, yaml
rc = json.load(open('electrical/earthing/evals/runner-config.json'))
assert len(rc['evals']) == 6, f'Expected 6 evals listed, got {len(rc[\"evals\"])}'
e1 = yaml.safe_load(open('electrical/earthing/evals/eval-01-uk-dwelling-tn-cs.yaml'))
assert e1['category'] == 'happy_path'
assert len(e1['assertions']) >= 8
print('Eval-01 + runner-config: OK')
"
```
Expected: `Eval-01 + runner-config: OK`

- [ ] **Step 4: Commit**

```bash
git add electrical/earthing/evals/runner-config.json electrical/earthing/evals/eval-01-uk-dwelling-tn-cs.yaml
git commit -m "feat: earthing eval-01 happy-path UK dwelling TN-C-S + runner-config"
```

---

### Task 15: Create `evals/eval-02-rural-tt-system.yaml`

**Files:**
- Create: `electrical/earthing/evals/eval-02-rural-tt-system.yaml`

- [ ] **Step 1: Write `eval-02-rural-tt-system.yaml`** (edge case — TT system with electrode)

```yaml
# Eval 02 — Rural UK dwelling, TT (no PME), all circuits need RCD
# Category: edge_case

id: eval-02-rural-tt-system
category: edge_case
severity: critical
description: |
  Rural UK farm cottage. DNO has declined to provide PME earth. Installation is TT
  with a local rod electrode. Soil is loam, engineer declares Ra=85Ω after installation.
  Every final circuit must have RCD per BS 7671 411.5.3 to meet disconnection time.

inputs:
  jurisdiction: "GB"
  earthing_system_declared: "TT"
  supply_voltage_v: 230
  ze_ohm_declared: 85.0
  electrode_target_ra_ohm: 100
  electrode_measured_ra_ohm: 85.0
  electrode_arrangement: "single_rod_1200mm_copper_clad"
  soil_type: "loam"
  water_service_metallic: false
  gas_service_metallic: true
  extraneous_parts:
    - { kind: "gas_service_entry", location: "kitchen utility" }
  met_location: "boot room"
  supplementary_bonding_required_locations: []
  consumed_intents:
    - { intent_type: "db-layout", intent_version: "1.0.0", produced_by: "electrical/db-layout/v1.0.0", payload_ref: "test-fixtures/db-layout-eval02.json" }

assertions:
  - kind: schema_valid
    schema: "earthing-ir.schema.json"
  - kind: jsonpath_equals
    path: "$.earthing_system"
    expected: "TT"
  - kind: jsonpath_count_gte
    path: "$.electrodes[*]"
    minimum: 1
  - kind: jsonpath_lte
    path: "$.electrodes[0].ra_measured_ohm"
    maximum: 100
    note: "Ra below target"
  - kind: jsonpath_all_equals
    path: "$.circuits[*].rcd_required"
    expected: true
    note: "TT requires RCD on every circuit"
  - kind: invariant_passes
    invariant: "INV-6"
    note: "RCD requirement check"
  - kind: clause_cited
    clause_pattern: "BS 7671:2018\\+A3 Reg 411\\.5\\.3"
    minimum_count: 1
  - kind: tool_call_pending_marked
    path: "$.electrodes[0]"
    note: "calc.electrode_resistance is deferred — engineer-provided Ra accepted with pending flag"

expected_status: "pass"
```

- [ ] **Step 2: Validate eval-02 parses and is TT category**

Run:
```bash
python3 -c "
import yaml
e = yaml.safe_load(open('electrical/earthing/evals/eval-02-rural-tt-system.yaml'))
assert e['category'] == 'edge_case'
assert 'TT' in e['description']
print('Eval-02: OK')
"
```
Expected: `Eval-02: OK`

- [ ] **Step 3: Commit**

```bash
git add electrical/earthing/evals/eval-02-rural-tt-system.yaml
git commit -m "feat: earthing eval-02 rural TT system with electrode + blanket RCD"
```

---

### Task 16: Create `evals/eval-03-cpc-undersized-trap.yaml`

**Files:**
- Create: `electrical/earthing/evals/eval-03-cpc-undersized-trap.yaml`

- [ ] **Step 1: Write the validation-trap eval**

```yaml
# Eval 03 — Generator MUST detect and reject an undersized CPC
# Category: validation_trap

id: eval-03-cpc-undersized-trap
category: validation_trap
severity: critical
description: |
  The input feeds a circuit where the engineer has declared a 1.5mm² CPC on a
  10mm² phase circuit. Per BS 7671 Table 54.7 this is incorrect — for L>16mm² ÷ 2
  would give 5mm², but for L≤16mm² CPC must equal L. The generator must EITHER
  (a) emit cpc.csa_mm2 == 10 with method 'bs7671_table_54.7', OR
  (b) emit cpc.csa_mm2 lower via adiabatic with method 'bs7671_adiabatic_54.1' and an
      adiabatic-computed value justified by I²t.
  Emitting 1.5mm² is a critical fail.

inputs:
  jurisdiction: "GB"
  earthing_system_declared: "TN-C-S"
  supply_voltage_v: 230
  ze_ohm_declared: 0.30
  water_service_metallic: true
  gas_service_metallic: true
  extraneous_parts: []
  met_location: "service intake"
  supplementary_bonding_required_locations: []
  trap_input_circuit:
    circuit_id: "L1"
    designation: "cooker circuit"
    line_csa_mm2: 10
    declared_cpc_csa_mm2: 1.5
    ocpd_rating_a: 32
    ocpd_type: "B"
    length_m: 18
  consumed_intents:
    - { intent_type: "db-layout", intent_version: "1.0.0", produced_by: "electrical/db-layout/v1.0.0", payload_ref: "test-fixtures/db-layout-eval03.json" }

assertions:
  - kind: schema_valid
    schema: "earthing-ir.schema.json"
  - kind: jsonpath_not_equals
    path: "$.circuits[?(@.circuit_id=='L1')].cpc.csa_mm2"
    forbidden: 1.5
    note: "Generator must NOT accept the undersized declared CPC"
  - kind: jsonpath_in
    path: "$.circuits[?(@.circuit_id=='L1')].cpc.cpc_sizing_method"
    allowed: ["bs7671_table_54.7", "bs7671_adiabatic_54.1"]
  - kind: invariant_passes
    invariant: "INV-4"
    note: "CPC sizing method must match jurisdiction"
  - kind: compliance_flag_emitted
    flag_code_pattern: "CPC_OVERRIDE_"
    note: "Generator should emit a compliance flag explaining the CPC was uprated from declared"

expected_status: "pass"
```

- [ ] **Step 2: Validate**

Run:
```bash
python3 -c "
import yaml
e = yaml.safe_load(open('electrical/earthing/evals/eval-03-cpc-undersized-trap.yaml'))
assert e['category'] == 'validation_trap'
assert e['inputs']['trap_input_circuit']['declared_cpc_csa_mm2'] == 1.5
print('Eval-03: OK')
"
```
Expected: `Eval-03: OK`

- [ ] **Step 3: Commit**

```bash
git add electrical/earthing/evals/eval-03-cpc-undersized-trap.yaml
git commit -m "feat: earthing eval-03 CPC-undersized validation trap"
```

---

### Task 17: Create `evals/eval-04-missing-soil-resistivity.yaml`

**Files:**
- Create: `electrical/earthing/evals/eval-04-missing-soil-resistivity.yaml`

- [ ] **Step 1: Write the missing-input eval**

```yaml
# Eval 04 — TT system with soil_type unknown — generator must request, not invent
# Category: missing_input

id: eval-04-missing-soil-resistivity
category: missing_input
severity: high
description: |
  TT system. Engineer has not declared soil_type or electrode_measured_ra_ohm.
  The generator must NOT invent a value. It must either:
  (a) emit a compliance flag asking the engineer to provide soil data and Ra measurement, OR
  (b) emit electrodes[0].tool_call_pending: true with a clear note that Ra is required.

inputs:
  jurisdiction: "GB"
  earthing_system_declared: "TT"
  supply_voltage_v: 230
  ze_ohm_declared: null
  electrode_target_ra_ohm: 100
  electrode_measured_ra_ohm: null
  electrode_arrangement: null
  soil_type: null
  water_service_metallic: false
  gas_service_metallic: false
  extraneous_parts: []
  met_location: "service intake cupboard"
  supplementary_bonding_required_locations: []
  consumed_intents:
    - { intent_type: "db-layout", intent_version: "1.0.0", produced_by: "electrical/db-layout/v1.0.0", payload_ref: "test-fixtures/db-layout-eval04.json" }

assertions:
  - kind: schema_valid
    schema: "earthing-ir.schema.json"
  - kind: jsonpath_present
    path: "$.compliance_summary.flags[*]"
    note: "Generator must emit at least one compliance flag for missing soil/Ra data"
  - kind: jsonpath_contains_substring
    path: "$.compliance_summary.flags[*].code"
    substring: "ELECTRODE"
  - kind: no_invented_values
    paths_must_be_null_or_pending:
      - "$.electrodes[0].ra_measured_ohm"
      - "$.electrodes[0].soil_resistivity_ohm_m"
    or_tool_call_pending: true
    note: "Generator must not invent soil data"

expected_status: "pass"
```

- [ ] **Step 2: Validate**

Run:
```bash
python3 -c "
import yaml
e = yaml.safe_load(open('electrical/earthing/evals/eval-04-missing-soil-resistivity.yaml'))
assert e['category'] == 'missing_input'
print('Eval-04: OK')
"
```
Expected: `Eval-04: OK`

- [ ] **Step 3: Commit**

```bash
git add electrical/earthing/evals/eval-04-missing-soil-resistivity.yaml
git commit -m "feat: earthing eval-04 missing-soil-resistivity input handling"
```

---

### Task 18: Create `evals/eval-05-jurisdiction-us-nec.yaml`

**Files:**
- Create: `electrical/earthing/evals/eval-05-jurisdiction-us-nec.yaml`

- [ ] **Step 1: Write the jurisdiction-switch eval**

```yaml
# Eval 05 — Identical brief, but jurisdiction=US — must produce NEC-conformant design
# Category: jurisdiction_switch

id: eval-05-jurisdiction-us-nec
category: jurisdiction_switch
severity: critical
description: |
  Single-family dwelling, but specified as a US project. The skill must:
  (a) Use NEC terminology (EGC, not CPC; grounding electrode system, not earth electrode array)
  (b) Size EGCs from NEC Table 250.122 by OCPD rating, NOT by phase CSA
  (c) Require supplemental grounding electrodes per NEC 250.50/250.53
  (d) Cite NEC 2023 articles, NOT BS 7671 regulations
  (e) Reference NFPA70/art250-grounding-bonding.json, not BS7671 files

inputs:
  jurisdiction: "US"
  earthing_system_declared: "TN-S"
  supply_voltage_v: 120
  supply_voltage_secondary_v: 240
  ze_ohm_declared: 0.20
  water_service_metallic: true
  gas_service_metallic: true
  extraneous_parts:
    - { kind: "concrete_encased_electrode", location: "footing UFER" }
    - { kind: "structural_steel", location: "frame" }
  met_location: "main service panel, garage"
  supplementary_bonding_required_locations: []
  consumed_intents:
    - { intent_type: "db-layout", intent_version: "1.0.0", produced_by: "electrical/db-layout/v1.0.0", payload_ref: "test-fixtures/db-layout-eval05.json" }

assertions:
  - kind: schema_valid
    schema: "earthing-ir.schema.json"
  - kind: jsonpath_equals
    path: "$.jurisdiction"
    expected: "US"
  - kind: jsonpath_all_equals
    path: "$.circuits[*].cpc.cpc_sizing_method"
    expected: "nec_table_250.122"
  - kind: jsonpath_count_gte
    path: "$.electrodes[*]"
    minimum: 2
    note: "NEC requires supplemental grounding electrode system"
  - kind: clause_cited
    clause_pattern: "^NEC 2023 (Art|Table) 250\\."
    minimum_count: 2
  - kind: clause_not_cited
    clause_pattern: "^BS 7671"
    note: "US project must not cite UK regs"
  - kind: invariant_passes
    invariant: "INV-4"
    note: "CPC method jurisdiction match"

expected_status: "pass"
```

- [ ] **Step 2: Validate**

Run:
```bash
python3 -c "
import yaml
e = yaml.safe_load(open('electrical/earthing/evals/eval-05-jurisdiction-us-nec.yaml'))
assert e['category'] == 'jurisdiction_switch'
assert e['inputs']['jurisdiction'] == 'US'
print('Eval-05: OK')
"
```
Expected: `Eval-05: OK`

- [ ] **Step 3: Commit**

```bash
git add electrical/earthing/evals/eval-05-jurisdiction-us-nec.yaml
git commit -m "feat: earthing eval-05 jurisdiction-switch US NEC variant"
```

---

### Task 19: Create `evals/eval-06-rationale-block.yaml`

**Files:**
- Create: `electrical/earthing/evals/eval-06-rationale-block.yaml`

- [ ] **Step 1: Write the rationale-block eval**

```yaml
# Eval 06 — Rationale block must be present and substantive
# Category: rationale_block

id: eval-06-rationale-block
category: rationale_block
severity: high
description: |
  Reuses the eval-01 happy-path scenario but specifically targets the rationale block.
  Per upstream WI2 the rationale block is mandatory at IR root and must contain the
  8-section taxonomy plus a chat_summary and a decisions array with citations.

inputs:
  reuse_eval: "eval-01-uk-dwelling-tn-cs"

assertions:
  - kind: schema_valid
    schema: "earthing-ir.schema.json"
  - kind: jsonpath_present
    path: "$.rationale.chat_summary"
  - kind: jsonpath_length_gte
    path: "$.rationale.chat_summary"
    minimum: 100
    maximum: 800
    note: "1 paragraph, not a sentence and not an essay"
  - kind: jsonpath_present_all
    paths:
      - "$.rationale.engineering_objectives"
      - "$.rationale.constraints"
      - "$.rationale.regulatory_basis"
      - "$.rationale.key_decisions"
      - "$.rationale.assumptions"
      - "$.rationale.design_methodology"
      - "$.rationale.risks"
      - "$.rationale.evidence"
  - kind: jsonpath_count_gte
    path: "$.rationale.key_decisions[*]"
    minimum: 3
  - kind: jsonpath_all_present
    path: "$.rationale.key_decisions[*].clause_ref"
    note: "Every key decision must cite a standards clause"
  - kind: jsonpath_pattern_match
    path: "$.rationale.key_decisions[*].clause_ref"
    pattern: "^(BS 7671:2018\\+A3|IEC 60364-[0-9]+-[0-9]+|NEC 2023)"
    note: "Citations must use canonical format"

expected_status: "pass"
```

- [ ] **Step 2: Validate all 6 evals exist + listed in runner-config**

Run:
```bash
python3 -c "
import json, os
rc = json.load(open('electrical/earthing/evals/runner-config.json'))
listed = set(rc['evals'])
on_disk = set(f for f in os.listdir('electrical/earthing/evals/') if f.startswith('eval-'))
missing = listed - on_disk
extra = on_disk - listed
assert not missing, f'Listed in runner-config but missing on disk: {missing}'
assert not extra, f'On disk but not in runner-config: {extra}'
print(f'All {len(listed)} evals exist and are registered')
"
```
Expected: `All 6 evals exist and are registered`

- [ ] **Step 3: Commit**

```bash
git add electrical/earthing/evals/eval-06-rationale-block.yaml
git commit -m "feat: earthing eval-06 rationale block coverage (WI2)"
```

---

### Task 20: Create example 1 — UK dwelling TN-C-S (full triple)

**Files:**
- Create: `electrical/earthing/examples/uk-dwelling-tn-cs/input.json`
- Create: `electrical/earthing/examples/uk-dwelling-tn-cs/reasoning.md`
- Create: `electrical/earthing/examples/uk-dwelling-tn-cs/output.json`

This example is the canonical worked-example pair to eval-01. It demonstrates the end-to-end pattern with all standards consumed and all three reasoning steps visible.

- [ ] **Step 1: Write `input.json`**

```json
{
  "$schema": "../../inputs.json",
  "project_meta": {
    "name": "23 Elm Crescent — 3-bed Semi",
    "client": "Private",
    "designer": "DraftsMan Skills demo",
    "date": "2026-05-15",
    "revision": "P01"
  },
  "jurisdiction": "GB",
  "earthing_system_declared": "TN-C-S",
  "supply_voltage_v": 230,
  "supply_phases": 1,
  "ze_ohm_declared": 0.35,
  "ze_ohm_source": "DNO declared (UK Power Networks)",
  "water_service_metallic": true,
  "gas_service_metallic": true,
  "extraneous_parts": [
    { "kind": "structural_steel", "location": "loft truss steel beam over kitchen extension" }
  ],
  "met_location": "consumer unit cupboard, ground floor hallway",
  "met_terminal_kind": "earthing_block_25mm_brass_4_way",
  "supplementary_bonding_required_locations": [
    { "kind": "bathroom", "zone_id": "B-FF-01", "description": "First floor main bathroom — has bath, basin, shower" }
  ],
  "life_safety_bonded_assets": [],
  "consumed_intents": [
    {
      "intent_type": "db-layout",
      "intent_version": "1.0.0",
      "produced_by": "electrical/db-layout/v1.0.0",
      "payload": {
        "boards": [
          { "id": "MB-G", "designation": "Main Consumer Unit", "location": "hallway cupboard", "phases": 1, "ways": 12, "main_switch_rating_a": 100, "main_switch_type": "RCD_main_30mA" }
        ],
        "outgoing_circuits": [
          { "id": "C01", "designation": "Ground floor lighting", "ocpd_rating_a": 6, "ocpd_type": "B", "phase_csa_mm2": 1.5, "length_m": 18 },
          { "id": "C02", "designation": "First floor lighting", "ocpd_rating_a": 6, "ocpd_type": "B", "phase_csa_mm2": 1.5, "length_m": 22 },
          { "id": "C03", "designation": "Ground floor sockets ring", "ocpd_rating_a": 32, "ocpd_type": "B", "phase_csa_mm2": 2.5, "length_m": 38 },
          { "id": "C04", "designation": "First floor sockets ring", "ocpd_rating_a": 32, "ocpd_type": "B", "phase_csa_mm2": 2.5, "length_m": 42 },
          { "id": "C05", "designation": "Cooker radial", "ocpd_rating_a": 32, "ocpd_type": "B", "phase_csa_mm2": 6.0, "length_m": 14 },
          { "id": "C06", "designation": "Bathroom shower", "ocpd_rating_a": 40, "ocpd_type": "B", "phase_csa_mm2": 10.0, "length_m": 16 }
        ]
      }
    },
    {
      "intent_type": "lighting-layout",
      "intent_version": "1.3.0",
      "produced_by": "electrical/lighting-layout/v1.3.0",
      "payload_ref": "test-fixtures/lighting-eval01.json"
    },
    {
      "intent_type": "small-power",
      "intent_version": "1.0.0",
      "produced_by": "electrical/small-power/v1.0.0",
      "payload_ref": "test-fixtures/small-power-eval01.json"
    }
  ]
}
```

- [ ] **Step 2: Write `reasoning.md`**

```markdown
# Reasoning — UK Dwelling TN-C-S Earthing Schematic

## Step 1 — Discovery check
Confirmed `consumed_intents` array contains the triple: db-layout, lighting-layout, small-power. All circuits to earth-aware-design are visible.

## Step 2 — Standards files to load
Jurisdiction is GB. Loading:
- `shared/standards/electrical/BS7671/reg411-disconnection-times.json`
- `shared/standards/electrical/BS7671/reg411-rcd-requirements.json`
- `shared/standards/electrical/BS7671/terminology.md`
- `shared/standards/electrical/IEC60617/symbol-index.json`
- `shared/standards/electrical/IEC60617/part2-general.json`

(IEC 60364 and NFPA 70 files are NOT loaded — jurisdiction filters them out.)

## Step 3 — Earthing system classification
- `earthing_system_declared: "TN-C-S"` — DNO has provided PME earth (Ze = 0.35Ω).
- Cross-check against `electrical/earthing/ontology/earthing-system-types.json` → TN-C-S permitted for GB, electrode optional, RCD not blanket-required.
- System: **TN-C-S confirmed**.

## Step 4 — MET location
- Engineer declared: `consumer unit cupboard, ground floor hallway`.
- MET terminal kind: 25mm² brass 4-way earthing block.
- MET ID: `MET-01`. Accessibility: per BS 7671 Reg 542.4.1.

## Step 5 — Electrode arrangement
- TN-C-S → electrode optional. Engineer has not requested supplementary electrode.
- Recommendation in rationale: consider rod electrode ≤200Ω if future EV charger is installed (open-PEN mitigation).
- `electrodes: []` — no electrodes in this design.

## Step 6 — Main protective bonding
Three main bonding conductors from MET, sized per BS 7671 Reg 544.1:
- 10mm² to water service entry (consumer earthing conductor 10mm² minimum for PME)
- 10mm² to gas service entry (within 600mm of meter outlet)
- 6mm² to structural steel in loft (extraneous-conductive-part)

Cited: **BS 7671:2018+A3 Reg 411.3.1.2** (main bonding requirement), **Reg 544.1** (conductor sizing).

## Step 7 — Supplementary bonding
First floor bathroom (Zone B-FF-01) needs supplementary bonding under BS 7671 Section 701 because:
- Exposed-conductive-parts (radiator pipework, light fitting) and
- Extraneous-conductive-parts (water pipes) are present together.

Test the 701.415.2 exemption: it requires ALL of: 30mA RCD covers all bathroom circuits AND main bonding to incoming services. Since shower (C06) is on a 40A circuit which has 30mA RCD, AND main bonding is in place → **exemption could apply, but supplementary bonding included for belt-and-braces** (recommended UK practice).

Supplementary bonding: 4mm² between metallic pipework, shower enclosure earth lug, and radiator.

## Step 8 — CPC sizing per circuit (BS 7671 Table 54.7)
Apply Table 54.7 — for L ≤ 16mm², CPC = L:

| Circuit | L csa | CPC csa | Method |
|---|---|---|---|
| C01 lighting | 1.5 | 1.5 | bs7671_table_54.7 |
| C02 lighting | 1.5 | 1.5 | bs7671_table_54.7 |
| C03 ring | 2.5 | 1.5 | bs7671_table_54.7 (twin-and-earth 6242Y) |
| C04 ring | 2.5 | 1.5 | bs7671_table_54.7 |
| C05 cooker | 6.0 | 2.5 | bs7671_table_54.7 (twin-and-earth) |
| C06 shower | 10.0 | 4.0 | bs7671_table_54.7 (twin-and-earth) |

Note: 6242Y twin-and-earth cables ship with reduced CPC integral to the cable — this is the standard exception.

## Step 9 — Zs verification
Compute R1+R2 per circuit using table values for 6242Y (mΩ/m). Zs = Ze + R1 + R2.
Compare against BS 7671 Table 41.3 (Type B MCB Zs_max at 230V, 0.4s) with 0.8 correction factor (Appendix 14).

Example for C03 (32A Type B):
- Tabulated Zs_max = 1.44Ω, corrected = 1.15Ω
- R1+R2 = 38m × (7.41 + 12.10) / 1000 = 0.74Ω
- Zs = 0.35 + 0.74 = 1.09Ω
- 1.09 ≤ 1.15 ✓ pass

All 6 circuits pass.

## Step 10 — RCD requirement check
Per BS 7671 Reg 411.3.3, RCD ≤30mA required for:
- C03, C04 sockets ring (domestic ≤32A sockets)
- C06 shower (bathroom location)
- C01, C02 lighting (since they pass through bathroom — 411.3.4)

Per RCD-main consumer unit, 30mA RCD covers all final circuits. C01-C06 all RCD-protected.

## Step 11 — Compliance flags
- INFO: PME open-PEN risk noted; recommend earthing electrode if EV charger added in future (BS 7671 722.411.4.1)
- NONE critical

## Step 12 — Rationale emitted
8-section taxonomy + chat_summary + 6 key_decisions, each with BS 7671 clause citation. See `output.json` rationale block.
```

- [ ] **Step 3: Write `output.json`** (the IR — abbreviated; full file in the actual write)

```json
{
  "$schema": "../../schemas/earthing-ir.schema.json",
  "drawing_type": "earthing_schematic",
  "version": "1.0.0",
  "meta": {
    "project_name": "23 Elm Crescent — 3-bed Semi",
    "revision": "P01",
    "produced_at": "2026-05-15T12:00:00Z",
    "skill_version": "earthing/1.0.0",
    "consumed_intents": [
      { "intent_type": "db-layout", "intent_version": "1.0.0", "produced_by": "electrical/db-layout/v1.0.0" },
      { "intent_type": "lighting-layout", "intent_version": "1.3.0", "produced_by": "electrical/lighting-layout/v1.3.0" },
      { "intent_type": "small-power", "intent_version": "1.0.0", "produced_by": "electrical/small-power/v1.0.0" }
    ]
  },
  "jurisdiction": "GB",
  "earthing_system": "TN-C-S",
  "supply": {
    "voltage_v": 230,
    "phases": 1,
    "ze_ohm": 0.35,
    "ze_source": "DNO declared (UK Power Networks)"
  },
  "met": {
    "id": "MET-01",
    "location": "consumer unit cupboard, ground floor hallway",
    "terminal_kind": "earthing_block_25mm_brass_4_way",
    "drawn_as_symbols": [{ "symbol_id": "iec60617_S00020", "label": "MET" }]
  },
  "electrodes": [],
  "main_bonding": {
    "conductors": [
      { "id": "MB-1", "from": "MET-01", "bonds_to": "water_service_entry", "csa_mm2": 10, "material": "copper_green_yellow", "drawn_as_symbols": [{ "symbol_id": "iec60617_S00190", "label": "10mm² CB" }] },
      { "id": "MB-2", "from": "MET-01", "bonds_to": "gas_service_entry", "csa_mm2": 10, "material": "copper_green_yellow" },
      { "id": "MB-3", "from": "MET-01", "bonds_to": "structural_steel", "csa_mm2": 6, "material": "copper_green_yellow" }
    ]
  },
  "supplementary_bonding": {
    "zones": [
      {
        "zone_id": "B-FF-01",
        "zone_kind": "bathroom",
        "description": "First floor main bathroom",
        "bonds": [
          { "from": "metallic_water_pipework", "to": "radiator", "csa_mm2": 4 },
          { "from": "shower_enclosure_earth_lug", "to": "radiator", "csa_mm2": 4 }
        ],
        "exemption_701.415.2_met": false,
        "exemption_701.415.2_notes": "30mA RCD covers all circuits AND main bonding present — exemption could apply but belt-and-braces supplementary bonding included per UK design custom"
      }
    ]
  },
  "circuits": [
    { "circuit_id": "C01", "designation": "Ground floor lighting", "line_csa_mm2": 1.5, "ocpd_rating_a": 6, "ocpd_type": "B", "length_m": 18, "cpc": { "csa_mm2": 1.5, "cpc_sizing_method": "bs7671_table_54.7", "in_same_wiring_system": true, "terminated_at_met_id": "MET-01" }, "ze_ohm": 0.35, "r1_ohm": 0.18, "r2_ohm": 0.27, "zs_calculated_ohm": 0.80, "zs_max_ohm": 8.66, "zs_max_source": "table_41.3_corrected", "rcd_required": true, "rcd_rating_ma": 30, "rcd_rationale": "passes through bathroom — BS 7671 411.3.4" },
    { "circuit_id": "C03", "designation": "Ground floor sockets ring", "line_csa_mm2": 2.5, "ocpd_rating_a": 32, "ocpd_type": "B", "length_m": 38, "cpc": { "csa_mm2": 1.5, "cpc_sizing_method": "bs7671_table_54.7", "in_same_wiring_system": true, "terminated_at_met_id": "MET-01" }, "ze_ohm": 0.35, "r1_ohm": 0.28, "r2_ohm": 0.46, "zs_calculated_ohm": 1.09, "zs_max_ohm": 1.15, "zs_max_source": "table_41.3_corrected", "rcd_required": true, "rcd_rating_ma": 30, "rcd_rationale": "domestic ≤32A socket — BS 7671 411.3.3" },
    { "circuit_id": "C06", "designation": "Bathroom shower", "line_csa_mm2": 10.0, "ocpd_rating_a": 40, "ocpd_type": "B", "length_m": 16, "cpc": { "csa_mm2": 4.0, "cpc_sizing_method": "bs7671_table_54.7", "in_same_wiring_system": true, "terminated_at_met_id": "MET-01" }, "ze_ohm": 0.35, "r1_ohm": 0.029, "r2_ohm": 0.073, "zs_calculated_ohm": 0.45, "zs_max_ohm": 0.92, "zs_max_source": "table_41.3_corrected", "rcd_required": true, "rcd_rating_ma": 30, "rcd_rationale": "bathroom location — BS 7671 Section 701" }
  ],
  "compliance_summary": {
    "verdict": "compliant",
    "clauses_cited": [
      "BS 7671:2018+A3 Reg 411.3.1.2",
      "BS 7671:2018+A3 Reg 411.3.3",
      "BS 7671:2018+A3 Reg 411.4.5",
      "BS 7671:2018+A3 Reg 542.4.1",
      "BS 7671:2018+A3 Reg 544.1",
      "BS 7671:2018+A3 Section 701",
      "BS 7671:2018+A3 Table 54.7",
      "BS 7671:2018+A3 Appendix 14"
    ],
    "flags": [
      { "code": "INFO_PME_OPEN_PEN_EV", "severity": "info", "message": "PME open-PEN risk: if EV chargepoint added, install supplementary earth electrode or use NFI-bonded chargepoint per BS 7671 722.411.4.1" }
    ]
  },
  "rationale": {
    "chat_summary": "Standard UK PME-supplied 3-bed semi. TN-C-S confirmed from DNO declaration with Ze=0.35Ω. MET in hallway cupboard with 10mm² bonds to water and gas services and 6mm² to loft structural steel. Six final circuits, all with CPCs sized per BS 7671 Table 54.7 (twin-and-earth integral reduced CPCs). Every circuit RCD-protected via 30mA main RCD. First-floor bathroom has supplementary bonding even though the 701.415.2 exemption could apply, as a belt-and-braces measure. Zs calculated for every circuit and verified against temperature-corrected Zs_max (0.8 factor per Appendix 14) — all pass with margin. Compliance flag emitted recommending an earth electrode if EV charging is added later (open-PEN mitigation).",
    "engineering_objectives": ["Provide a fault path of sufficiently low impedance for automatic disconnection within 0.4s on every final circuit per BS 7671 411.3.2.2", "Bond all extraneous-conductive-parts to MET per 411.3.1.2", "Comply with PME special requirements for bathrooms and future-proof for EV"],
    "constraints": ["DNO provides PME earth only", "Consumer unit located in hallway cupboard (1.4m run from incomer)", "Loft contains structural steel beam over kitchen extension"],
    "regulatory_basis": ["BS 7671:2018+A3 Chapter 41 (automatic disconnection)", "BS 7671:2018+A3 Chapter 54 (earthing arrangements)", "BS 7671:2018+A3 Section 701 (locations containing a bath or shower)"],
    "key_decisions": [
      { "decision": "TN-C-S confirmed", "rationale": "DNO declared PME with Ze=0.35Ω; no DNO restriction", "clause_ref": "BS 7671:2018+A3 Reg 411.4.1" },
      { "decision": "Main bonding 10mm² to water and gas, 6mm² to structural steel", "rationale": "PME minimum CSA for service bonds per Table 54.8; structural steel sized per general 544.1", "clause_ref": "BS 7671:2018+A3 Table 54.8" },
      { "decision": "Supplementary bonding included in bathroom despite possible exemption", "rationale": "30mA RCD + main bonding satisfies 701.415.2, but UK trade custom retains supplementary bonding for resilience", "clause_ref": "BS 7671:2018+A3 Section 701" },
      { "decision": "All CPCs from Table 54.7 (twin-and-earth integral)", "rationale": "Domestic wiring with twin-and-earth cable type; integral reduced CPC is standard and table-method appropriate", "clause_ref": "BS 7671:2018+A3 Table 54.7" },
      { "decision": "30mA RCD on all final circuits via main RCD", "rationale": "All sockets ≤32A in dwelling per 411.3.3; bathroom circuits per Section 701; resilience for outdoor/loft circuits", "clause_ref": "BS 7671:2018+A3 Reg 411.3.3" },
      { "decision": "Zs verified against 0.8-corrected Zs_max", "rationale": "Temperature correction applied per Appendix 14; all margins ≥0.06Ω", "clause_ref": "BS 7671:2018+A3 Appendix 14" }
    ],
    "assumptions": ["Ze of 0.35Ω is DNO-declared, not measured; design margin allows up to Ze=0.45Ω before any circuit fails", "Twin-and-earth 6242Y is used throughout (manufacturer's stated reduced CPC csa)", "Bathroom layout matches default zone classification (Section 701)"],
    "design_methodology": "Hand-calculated R1+R2 per circuit from tabulated mΩ/m (BS 7671 Appendix 4 Table 4D5). Zs = Ze + R1 + R2. Compared to Zs_max from Table 41.3 multiplied by 0.8 (Appendix 14 temperature correction).",
    "risks": ["Future EV charger adoption will require either supplementary electrode (Ra≤200Ω) or non-fault-bonded chargepoint", "Service position changes will invalidate Ze assumption"],
    "evidence": ["DNO declaration letter for Ze (file ref: DNO/Q12345)", "BS 7671 Table 41.3 (corrected by 0.8 per App 14)", "BS 7671 Table 54.7 for CPC sizing", "Manufacturer's data sheet for 6242Y twin-and-earth"]
  }
}
```

- [ ] **Step 4: Validate the three files**

Run:
```bash
test -s electrical/earthing/examples/uk-dwelling-tn-cs/input.json && \
test -s electrical/earthing/examples/uk-dwelling-tn-cs/reasoning.md && \
test -s electrical/earthing/examples/uk-dwelling-tn-cs/output.json && \
echo "OK: 3 example files exist"
python3 -c "
import json
o = json.load(open('electrical/earthing/examples/uk-dwelling-tn-cs/output.json'))
assert o['earthing_system'] == 'TN-C-S'
assert len(o['main_bonding']['conductors']) == 3
assert len(o['rationale']['key_decisions']) >= 3
print('Example 1 IR validates')
"
```
Expected: `OK: 3 example files exist` then `Example 1 IR validates`

- [ ] **Step 5: Commit**

```bash
git add electrical/earthing/examples/uk-dwelling-tn-cs/
git commit -m "feat: earthing example 1 — UK dwelling TN-C-S (full triple intents)"
```

---

### Task 21: Create example 2 — INT rural TT system

**Files:**
- Create: `electrical/earthing/examples/intl-rural-tt/input.json`
- Create: `electrical/earthing/examples/intl-rural-tt/reasoning.md`
- Create: `electrical/earthing/examples/intl-rural-tt/output.json`

This example demonstrates TT system handling, IEC 60364 standards loading, electrode design, blanket RCD requirement.

- [ ] **Step 1: Write `input.json`**

```json
{
  "$schema": "../../inputs.json",
  "project_meta": { "name": "Vineyard cottage — Tuscany", "client": "Private", "designer": "DraftsMan Skills demo", "date": "2026-05-15", "revision": "P01" },
  "jurisdiction": "INT",
  "earthing_system_declared": "TT",
  "supply_voltage_v": 230,
  "supply_phases": 1,
  "ze_ohm_declared": 85.0,
  "ze_ohm_source": "measured at electrode head, post-installation (Megger DET3TC)",
  "electrode_target_ra_ohm": 100,
  "electrode_measured_ra_ohm": 85.0,
  "electrode_arrangement": "two_rods_in_parallel_5m_separation_1500mm_each",
  "soil_type": "clay_loam_typical_resistivity_50_ohm_m",
  "water_service_metallic": false,
  "gas_service_metallic": false,
  "extraneous_parts": [],
  "met_location": "service intake cupboard, north-west corner",
  "met_terminal_kind": "earthing_block_16mm_brass_2_way",
  "supplementary_bonding_required_locations": [],
  "life_safety_bonded_assets": [],
  "consumed_intents": [
    {
      "intent_type": "db-layout",
      "intent_version": "1.0.0",
      "produced_by": "electrical/db-layout/v1.0.0",
      "payload": {
        "boards": [{ "id": "MB-G", "designation": "Main board", "phases": 1, "ways": 8, "main_switch_rating_a": 63, "main_switch_type": "isolator" }],
        "outgoing_circuits": [
          { "id": "C01", "designation": "Lighting all rooms", "ocpd_rating_a": 10, "ocpd_type": "B", "phase_csa_mm2": 1.5, "length_m": 25, "rcbo_rating_ma": 30 },
          { "id": "C02", "designation": "Sockets all rooms", "ocpd_rating_a": 16, "ocpd_type": "C", "phase_csa_mm2": 2.5, "length_m": 28, "rcbo_rating_ma": 30 },
          { "id": "C03", "designation": "Water pump (outdoor)", "ocpd_rating_a": 20, "ocpd_type": "C", "phase_csa_mm2": 4.0, "length_m": 35, "rcbo_rating_ma": 30 }
        ]
      }
    }
  ]
}
```

- [ ] **Step 2: Write `reasoning.md`**

```markdown
# Reasoning — INT TT Vineyard Cottage

## Step 1 — Discovery
Single consumed intent: db-layout. lighting-layout and small-power not provided — generator must work from db-layout outgoing_circuits alone. This is acceptable for rural/simple installations.

## Step 2 — Standards files loaded
Jurisdiction is INT. Loading:
- `shared/standards/electrical/IEC60364/part4-41-electric-shock.json`
- `shared/standards/electrical/IEC60364/part5-54-earthing.json`
- `shared/standards/electrical/IEC60364/earthing-systems.md`
- `shared/standards/electrical/IEC60617/symbol-index.json`
- `shared/standards/electrical/IEC60617/part2-general.json`

BS 7671 and NFPA 70 NOT loaded.

## Step 3 — Earthing system
TT declared. Ontology lookup → TT requires ≥1 electrode at the installation; RCD blanket-required.

## Step 4 — MET location
Service intake cupboard, NW corner. MET ID: MET-01.

## Step 5 — Electrode arrangement
Engineer has declared two rods in parallel, 5m apart, 1500mm each. Measured Ra=85Ω.
- Target Ra ≤ 100Ω → 85Ω passes with 15Ω margin.
- IEC 60364-4-41 411.5.3: disconnection time satisfied if Ra·IΔn ≤ 50V → 85 × 0.030 = 2.55V ≪ 50V ✓
- `electrodes[0].tool_call_pending: true` for the future Python `calc.electrode_resistance` to verify geometry assumptions.

## Step 6 — Main bonding
No metallic water service, no metallic gas service, no extraneous-conductive-parts declared. **No main bonding conductors required** beyond the earthing conductor MET → electrode.

## Step 7 — Supplementary bonding
None declared.

## Step 8 — CPC sizing (IEC 60364-5-54 Table 54.2)
Table method per IEC 60364-5-54 Clause 543.1.1:

| Circuit | L csa | CPC csa | Method |
|---|---|---|---|
| C01 lighting | 1.5 | 1.5 | iec60364_table_54.2 |
| C02 sockets | 2.5 | 2.5 | iec60364_table_54.2 |
| C03 pump | 4.0 | 4.0 | iec60364_table_54.2 |

## Step 9 — Zs verification
TT system Zs = Ze + R1 + R2.
For TT, the disconnection time check uses Ra·IΔn ≤ 50V rule (411.5.3), not Zs vs Zs_max — but Zs is still computed for record.

## Step 10 — RCD
All three circuits have 30mA RCBO. IEC 60364-4-41 411.5.3 satisfied for every circuit.

## Step 11 — Compliance
No flags — design is fully compliant.

## Step 12 — Rationale block emitted.
```

- [ ] **Step 3: Write `output.json`** (abbreviated)

```json
{
  "$schema": "../../schemas/earthing-ir.schema.json",
  "drawing_type": "earthing_schematic",
  "version": "1.0.0",
  "meta": {
    "project_name": "Vineyard cottage — Tuscany",
    "revision": "P01",
    "produced_at": "2026-05-15T12:00:00Z",
    "skill_version": "earthing/1.0.0",
    "consumed_intents": [
      { "intent_type": "db-layout", "intent_version": "1.0.0", "produced_by": "electrical/db-layout/v1.0.0" }
    ]
  },
  "jurisdiction": "INT",
  "earthing_system": "TT",
  "supply": { "voltage_v": 230, "phases": 1, "ze_ohm": 85.0, "ze_source": "measured at electrode (Megger DET3TC)" },
  "met": { "id": "MET-01", "location": "service intake cupboard, NW corner", "terminal_kind": "earthing_block_16mm_brass_2_way", "drawn_as_symbols": [{ "symbol_id": "iec60617_S00020", "label": "MET" }] },
  "electrodes": [
    {
      "id": "EL-01",
      "kind": "rod_array",
      "arrangement": "two_rods_in_parallel",
      "rod_count": 2,
      "rod_length_mm": 1500,
      "rod_separation_m": 5,
      "rod_material": "copper_clad_steel",
      "soil_type": "clay_loam",
      "soil_resistivity_ohm_m_assumed": 50,
      "ra_target_ohm": 100,
      "ra_measured_ohm": 85.0,
      "tool_call_pending": true,
      "tool_call_pending_for": "calc.electrode_resistance",
      "drawn_as_symbols": [{ "symbol_id": "iec60617_S00021", "label": "Earth electrode" }]
    }
  ],
  "main_bonding": { "conductors": [] },
  "supplementary_bonding": { "zones": [] },
  "circuits": [
    { "circuit_id": "C01", "designation": "Lighting", "line_csa_mm2": 1.5, "ocpd_rating_a": 10, "ocpd_type": "B", "length_m": 25, "cpc": { "csa_mm2": 1.5, "cpc_sizing_method": "iec60364_table_54.2", "in_same_wiring_system": true, "terminated_at_met_id": "MET-01" }, "ze_ohm": 85.0, "r1_ohm": 0.30, "r2_ohm": 0.30, "zs_calculated_ohm": 85.60, "zs_max_ohm": null, "zs_max_source": "tt_uses_ra_idn_rule", "ra_idn_volt": 2.55, "ra_idn_limit_volt": 50, "rcd_required": true, "rcd_rating_ma": 30 },
    { "circuit_id": "C02", "designation": "Sockets", "line_csa_mm2": 2.5, "ocpd_rating_a": 16, "ocpd_type": "C", "length_m": 28, "cpc": { "csa_mm2": 2.5, "cpc_sizing_method": "iec60364_table_54.2", "in_same_wiring_system": true, "terminated_at_met_id": "MET-01" }, "ze_ohm": 85.0, "r1_ohm": 0.21, "r2_ohm": 0.21, "zs_calculated_ohm": 85.42, "zs_max_ohm": null, "zs_max_source": "tt_uses_ra_idn_rule", "ra_idn_volt": 2.55, "ra_idn_limit_volt": 50, "rcd_required": true, "rcd_rating_ma": 30 },
    { "circuit_id": "C03", "designation": "Water pump", "line_csa_mm2": 4.0, "ocpd_rating_a": 20, "ocpd_type": "C", "length_m": 35, "cpc": { "csa_mm2": 4.0, "cpc_sizing_method": "iec60364_table_54.2", "in_same_wiring_system": true, "terminated_at_met_id": "MET-01" }, "ze_ohm": 85.0, "r1_ohm": 0.16, "r2_ohm": 0.16, "zs_calculated_ohm": 85.32, "zs_max_ohm": null, "zs_max_source": "tt_uses_ra_idn_rule", "ra_idn_volt": 2.55, "ra_idn_limit_volt": 50, "rcd_required": true, "rcd_rating_ma": 30 }
  ],
  "compliance_summary": {
    "verdict": "compliant",
    "clauses_cited": [
      "IEC 60364-4-41:2017 clause 411.5.3",
      "IEC 60364-5-54:2011 clause 542.4",
      "IEC 60364-5-54:2011 clause 543.1.1",
      "IEC 60364-5-54:2011 Table 54.2"
    ],
    "flags": []
  },
  "rationale": {
    "chat_summary": "Rural Tuscany cottage on TT supply (DNO does not provide earth at this location). Two parallel earth rods 5m apart, 1500mm each, measured Ra=85Ω which beats the 100Ω target. No metallic services to bond. Three circuits, all on 30mA RCBOs to satisfy IEC 60364-4-41 411.5.3 (Ra·IΔn=2.55V ≪ 50V limit). CPCs sized per IEC 60364-5-54 Table 54.2 — full equality with phase conductor since this is the table-method default for INT projects. Electrode resistance is engineer-measured; the iterative calculator (calc.electrode_resistance) is deferred and flagged tool_call_pending.",
    "engineering_objectives": ["Provide automatic disconnection within 0.2s for end-user circuits via 30mA RCBO", "Meet Ra·IΔn ≤ 50V limit on TT system", "Limit Ra to ≤100Ω target with margin"],
    "constraints": ["No DNO earth available", "Sandy clay loam soil — two rods needed", "No metallic services entering building"],
    "regulatory_basis": ["IEC 60364-4-41:2017 (electric shock protection)", "IEC 60364-5-54:2011 (earthing arrangements)"],
    "key_decisions": [
      { "decision": "TT system confirmed", "rationale": "No DNO earth", "clause_ref": "IEC 60364-1 clause 312.2" },
      { "decision": "Two-rod parallel electrode", "rationale": "Single rod estimated 150Ω, exceeds target; parallel halves resistance", "clause_ref": "IEC 60364-5-54:2011 clause 542.2" },
      { "decision": "30mA RCBO on every circuit", "rationale": "Ra·IΔn must not exceed 50V; with Ra=85Ω, IΔn must be ≤0.588A → 30mA is the standard sub-multiple", "clause_ref": "IEC 60364-4-41:2017 clause 411.5.3" },
      { "decision": "CPC = phase CSA (Table 54.2 method)", "rationale": "Adiabatic not required for these small CSA values", "clause_ref": "IEC 60364-5-54:2011 Table 54.2" }
    ],
    "assumptions": ["Soil resistivity 50 Ω·m (clay loam typical)", "Rod electrode formula treats rods as semi-infinite (validated by post-install measurement)"],
    "design_methodology": "Two rods designed to halve single-rod resistance; verified by post-installation 3-electrode test method. CPC table method. RCD ensures disconnection.",
    "risks": ["Long-term soil moisture variation will affect Ra — annual re-test recommended"],
    "evidence": ["Megger DET3TC test certificate", "IEC 60364-5-54 Table 54.2", "IEC 60364-4-41 clause 411.5.3"]
  }
}
```

- [ ] **Step 4: Validate**

Run:
```bash
test -s electrical/earthing/examples/intl-rural-tt/input.json && \
test -s electrical/earthing/examples/intl-rural-tt/reasoning.md && \
test -s electrical/earthing/examples/intl-rural-tt/output.json && \
echo "OK"
python3 -c "
import json
o = json.load(open('electrical/earthing/examples/intl-rural-tt/output.json'))
assert o['earthing_system'] == 'TT'
assert len(o['electrodes']) == 1
assert o['electrodes'][0]['tool_call_pending'] == True
print('Example 2 IR validates')
"
```
Expected: `OK` then `Example 2 IR validates`

- [ ] **Step 5: Commit**

```bash
git add electrical/earthing/examples/intl-rural-tt/
git commit -m "feat: earthing example 2 — INT rural TT with parallel rod electrode"
```

---

### Task 22: Create example 3 — US commercial NEC

**Files:**
- Create: `electrical/earthing/examples/us-commercial-nec/input.json`
- Create: `electrical/earthing/examples/us-commercial-nec/reasoning.md`
- Create: `electrical/earthing/examples/us-commercial-nec/output.json`

This example demonstrates NEC terminology, jurisdiction switching, NFPA 70 standards loading.

- [ ] **Step 1: Write `input.json`**

```json
{
  "$schema": "../../inputs.json",
  "project_meta": { "name": "Strip mall — Suite 4 fit-out", "client": "Retail tenant", "designer": "DraftsMan Skills demo", "date": "2026-05-15", "revision": "P01" },
  "jurisdiction": "US",
  "earthing_system_declared": "TN-S",
  "supply_voltage_v": 120,
  "supply_voltage_secondary_v": 240,
  "supply_phases": 1,
  "ze_ohm_declared": 0.20,
  "ze_ohm_source": "POCO declared service grounding",
  "water_service_metallic": true,
  "gas_service_metallic": true,
  "extraneous_parts": [
    { "kind": "concrete_encased_electrode", "location": "footing UFER", "csa_or_diameter": "20ft #4 rebar" },
    { "kind": "structural_steel", "location": "exposed beam in service area" }
  ],
  "met_location": "main service panel — exterior wall",
  "met_terminal_kind": "grounding_busbar_in_service_panel",
  "supplementary_bonding_required_locations": [],
  "life_safety_bonded_assets": [],
  "consumed_intents": [
    {
      "intent_type": "db-layout",
      "intent_version": "1.0.0",
      "produced_by": "electrical/db-layout/v1.0.0",
      "payload": {
        "boards": [{ "id": "MSP", "designation": "Main Service Panel", "phases": 1, "ways": 20, "main_switch_rating_a": 200, "main_switch_type": "main_breaker_200A" }],
        "outgoing_circuits": [
          { "id": "C01", "designation": "General lighting", "ocpd_rating_a": 20, "phase_csa_awg": "12", "length_m": 25 },
          { "id": "C02", "designation": "General receptacles", "ocpd_rating_a": 20, "phase_csa_awg": "12", "length_m": 30 },
          { "id": "C03", "designation": "Reach-in cooler dedicated", "ocpd_rating_a": 30, "phase_csa_awg": "10", "length_m": 18 },
          { "id": "C04", "designation": "RTU HVAC unit", "ocpd_rating_a": 60, "phase_csa_awg": "6", "length_m": 35 }
        ]
      }
    }
  ]
}
```

- [ ] **Step 2: Write `reasoning.md`**

```markdown
# Reasoning — US Strip Mall NEC Earthing Schematic

## Step 1 — Discovery
db-layout intent only. Consumed.

## Step 2 — Standards files (US jurisdiction)
- `shared/standards/electrical/NFPA70/art250-grounding-bonding.json`
- `shared/standards/electrical/NFPA70/grounding-and-bonding.json`
- `shared/standards/electrical/NFPA70/terminology.md`
- `shared/standards/electrical/IEC60617/symbol-index.json`

BS 7671 and IEC 60364 NOT loaded — US uses NEC.

## Step 3 — Earthing system classification
NEC uses different taxonomy. This is a "grounded system" with EGC throughout — closest TN equivalent is TN-S. The earthing_system field will be `TN-S` for cross-jurisdiction comparability, but all citations are NEC.

## Step 4 — MET (NEC terminology: grounding busbar)
Main Service Panel grounding busbar. ID: MSP-GBB.

## Step 5 — Grounding electrode system (NEC 250.50)
NEC 250.50 requires bonding ALL existing grounding electrodes. Available:
- UFER (concrete-encased rebar) — required as available per 250.52(A)(3)
- Structural steel — required as available per 250.52(A)(2)
- Metal water pipe (≥10ft buried) per 250.52(A)(1)

Three electrodes bonded together via grounding electrode conductor (GEC). GEC sized per Table 250.66 — for 200A service with copper, GEC = 4 AWG copper.

## Step 6 — Main bonding jumper (NEC 250.28)
Inside service panel, neutral bonded to ground at MSP only. Main bonding jumper sized per 250.28(D) = same size as largest service conductor.

## Step 7 — Supplementary bonding
None — no special location (bathroom is NEC 680-style pool, not strip mall retail).

## Step 8 — EGC sizing (NEC Table 250.122 — by OCPD rating)

| Circuit | OCPD | EGC required | Method |
|---|---|---|---|
| C01 (20A) | 20A | 12 AWG | nec_table_250.122 |
| C02 (20A) | 20A | 12 AWG | nec_table_250.122 |
| C03 (30A) | 30A | 10 AWG | nec_table_250.122 |
| C04 (60A) | 60A | 10 AWG | nec_table_250.122 |

Note: NEC sizes by OCPD rating, NOT phase CSA — a key difference from BS 7671 / IEC 60364.

## Step 9 — Zs / fault current
NEC does not use "Zs" terminology — instead the ground-fault current path must be adequate (250.4(A)(5)). Effective ground-fault current path is verified by impedance check.

## Step 10 — GFCI / AFCI
NEC requires:
- GFCI on receptacles in retail "wet" locations (not generally applicable here unless food prep / wash sink)
- AFCI not required for non-dwelling

C02 receptacles in general retail: standard breaker OK.

## Step 11 — Compliance
- INFO: confirm rebar in footing is ≥20ft continuous and accessible at service for UFER bond

## Step 12 — Rationale.
```

- [ ] **Step 3: Write `output.json`** (abbreviated)

```json
{
  "$schema": "../../schemas/earthing-ir.schema.json",
  "drawing_type": "earthing_schematic",
  "version": "1.0.0",
  "meta": {
    "project_name": "Strip mall — Suite 4 fit-out",
    "revision": "P01",
    "produced_at": "2026-05-15T12:00:00Z",
    "skill_version": "earthing/1.0.0",
    "consumed_intents": [
      { "intent_type": "db-layout", "intent_version": "1.0.0", "produced_by": "electrical/db-layout/v1.0.0" }
    ]
  },
  "jurisdiction": "US",
  "earthing_system": "TN-S",
  "supply": { "voltage_v": 120, "voltage_secondary_v": 240, "phases": 1, "ze_ohm": 0.20, "ze_source": "POCO declared" },
  "met": { "id": "MSP-GBB", "location": "main service panel — exterior wall", "terminal_kind": "grounding_busbar_in_service_panel", "drawn_as_symbols": [{ "symbol_id": "iec60617_S00020", "label": "GBB" }] },
  "electrodes": [
    { "id": "EL-01", "kind": "concrete_encased", "arrangement": "ufer_20ft_4awg_rebar", "drawn_as_symbols": [{ "symbol_id": "iec60617_S00021", "label": "UFER" }] },
    { "id": "EL-02", "kind": "structural_steel", "arrangement": "bonded_exposed_beam_service_area", "drawn_as_symbols": [{ "symbol_id": "iec60617_S00022", "label": "Steel" }] },
    { "id": "EL-03", "kind": "metal_water_pipe", "arrangement": "≥10ft_buried_continuous", "drawn_as_symbols": [{ "symbol_id": "iec60617_S00023", "label": "WP" }] }
  ],
  "main_bonding": {
    "conductors": [
      { "id": "GEC-1", "from": "MSP-GBB", "bonds_to": "ufer_concrete_encased_electrode", "csa_awg": "4", "csa_mm2": 21.2, "material": "copper" },
      { "id": "GEC-2", "from": "MSP-GBB", "bonds_to": "structural_steel", "csa_awg": "4", "csa_mm2": 21.2, "material": "copper" },
      { "id": "GEC-3", "from": "MSP-GBB", "bonds_to": "water_service_entry", "csa_awg": "4", "csa_mm2": 21.2, "material": "copper" },
      { "id": "MBJ", "from": "MSP-GBB", "bonds_to": "service_neutral_in_panel", "csa_awg": "4", "csa_mm2": 21.2, "material": "copper", "note": "Main Bonding Jumper per NEC 250.28" }
    ]
  },
  "supplementary_bonding": { "zones": [] },
  "circuits": [
    { "circuit_id": "C01", "designation": "General lighting", "line_csa_awg": "12", "ocpd_rating_a": 20, "ocpd_type": "thermal_magnetic", "length_m": 25, "cpc": { "csa_awg": "12", "cpc_sizing_method": "nec_table_250.122", "in_same_wiring_system": true, "terminated_at_met_id": "MSP-GBB" }, "ze_ohm": 0.20, "rcd_required": false, "gfci_required": false, "afci_required": false },
    { "circuit_id": "C02", "designation": "General receptacles", "line_csa_awg": "12", "ocpd_rating_a": 20, "ocpd_type": "thermal_magnetic", "length_m": 30, "cpc": { "csa_awg": "12", "cpc_sizing_method": "nec_table_250.122", "in_same_wiring_system": true, "terminated_at_met_id": "MSP-GBB" }, "ze_ohm": 0.20, "rcd_required": false, "gfci_required": false, "afci_required": false },
    { "circuit_id": "C03", "designation": "Reach-in cooler", "line_csa_awg": "10", "ocpd_rating_a": 30, "ocpd_type": "thermal_magnetic", "length_m": 18, "cpc": { "csa_awg": "10", "cpc_sizing_method": "nec_table_250.122", "in_same_wiring_system": true, "terminated_at_met_id": "MSP-GBB" }, "ze_ohm": 0.20, "rcd_required": false },
    { "circuit_id": "C04", "designation": "RTU HVAC", "line_csa_awg": "6", "ocpd_rating_a": 60, "ocpd_type": "thermal_magnetic", "length_m": 35, "cpc": { "csa_awg": "10", "cpc_sizing_method": "nec_table_250.122", "in_same_wiring_system": true, "terminated_at_met_id": "MSP-GBB" }, "ze_ohm": 0.20, "rcd_required": false }
  ],
  "compliance_summary": {
    "verdict": "compliant",
    "clauses_cited": [
      "NEC 2023 Art 250.4(A)(5)",
      "NEC 2023 Art 250.28",
      "NEC 2023 Art 250.50",
      "NEC 2023 Art 250.52(A)",
      "NEC 2023 Table 250.66",
      "NEC 2023 Table 250.122"
    ],
    "flags": [
      { "code": "INFO_UFER_FIELD_VERIFICATION", "severity": "info", "message": "Confirm rebar in footing is ≥20ft continuous and accessible at service before specifying UFER bond" }
    ]
  },
  "rationale": {
    "chat_summary": "US strip mall retail fit-out. 200A single-phase service with POCO-declared grounded service. Grounding electrode system bonds UFER (footing rebar), structural steel, and metal water pipe per NEC 250.50/250.52(A). GEC = 4 AWG copper sized from Table 250.66 for 200A service. EGCs sized by OCPD rating per Table 250.122 — 12 AWG for 20A circuits, 10 AWG for 30A and 60A circuits (note: the 60A RTU EGC at 10 AWG is the Table 250.122 minimum despite the larger phase conductor — this is the NEC's deliberate decoupling of EGC from phase CSA). No GFCI/AFCI required for general retail. Main bonding jumper inside service panel ties neutral to ground.",
    "engineering_objectives": ["Establish effective ground-fault current path per NEC 250.4(A)(5)", "Bond all available grounding electrodes per NEC 250.50", "Size GEC and EGCs from NEC 250 tables"],
    "constraints": ["Service is exterior-mounted strip-mall panel", "UFER must be verified in field — building is existing"],
    "regulatory_basis": ["NEC 2023 Article 250 (Grounding and Bonding)"],
    "key_decisions": [
      { "decision": "TN-S system (NEC grounded-system)", "rationale": "Standard US service with EGC throughout", "clause_ref": "NEC 2023 Art 250.4(A)" },
      { "decision": "GEC = 4 AWG copper", "rationale": "200A service ungrounded conductor → Table 250.66 row", "clause_ref": "NEC 2023 Table 250.66" },
      { "decision": "Three electrodes bonded together", "rationale": "All available electrodes must be bonded per 250.50", "clause_ref": "NEC 2023 Art 250.50" },
      { "decision": "EGCs from Table 250.122", "rationale": "NEC sizes EGC by OCPD rating, decoupling it from phase CSA", "clause_ref": "NEC 2023 Table 250.122" },
      { "decision": "Main Bonding Jumper inside service panel", "rationale": "Bond neutral to ground at service only per 250.28", "clause_ref": "NEC 2023 Art 250.28" }
    ],
    "assumptions": ["UFER rebar is continuous ≥20ft", "Metal water pipe is buried ≥10ft and electrically continuous"],
    "design_methodology": "All EGC sizing via direct Table 250.122 lookup. GEC sized via Table 250.66. No iterative calculation required for NEC method.",
    "risks": ["UFER bond depends on field verification", "Existing water pipe continuity may have been broken by replacement plastic section — visual confirmation required"],
    "evidence": ["NEC 2023 Table 250.66", "NEC 2023 Table 250.122", "POCO service confirmation letter"]
  }
}
```

- [ ] **Step 4: Validate**

Run:
```bash
test -s electrical/earthing/examples/us-commercial-nec/input.json && \
test -s electrical/earthing/examples/us-commercial-nec/reasoning.md && \
test -s electrical/earthing/examples/us-commercial-nec/output.json && \
echo "OK"
python3 -c "
import json
o = json.load(open('electrical/earthing/examples/us-commercial-nec/output.json'))
assert o['jurisdiction'] == 'US'
assert all(c['cpc']['cpc_sizing_method'] == 'nec_table_250.122' for c in o['circuits'])
assert any('NEC 2023' in c for c in o['compliance_summary']['clauses_cited'])
assert not any('BS 7671' in c for c in o['compliance_summary']['clauses_cited'])
print('Example 3 IR validates — NEC clauses only, no BS 7671 cross-citation')
"
```
Expected: `OK` then `Example 3 IR validates — NEC clauses only, no BS 7671 cross-citation`

- [ ] **Step 5: Commit**

```bash
git add electrical/earthing/examples/us-commercial-nec/
git commit -m "feat: earthing example 3 — US strip-mall NEC (Table 250.122 EGC sizing)"
```

---

### Task 23: Rewrite `README.md`

**Files:**
- Rewrite: `electrical/earthing/README.md`

The README is the human-facing entry point for the skill. It mirrors the structure of `electrical/lighting-layout/README.md` and documents: what the skill produces, eval coverage matrix, file structure, version status, jurisdiction support.

- [ ] **Step 1: Read the reference README**

Run:
```bash
cat electrical/lighting-layout/README.md
```

Use this as the structural template — every section heading present in lighting-layout must appear in earthing's README.

- [ ] **Step 2: Write the new `README.md`**

````markdown
# `earthing` — Electrical Earthing Schematic Generator

**Status:** `beta`
**Version:** `1.0.0`
**Drawing type:** `earthing_schematic`
**Reference:** `electrical/lighting-layout` (production skill — same pattern)

## What this skill produces

A single-line earthing schematic IR (Intermediate Representation) that captures:

- The earthing system (TN-C-S / TT / TN-S)
- The Main Earthing Terminal (MET) location and arrangement
- Earth electrode(s) where required (TT: always; TN-C-S: optional)
- Main protective bonding to all extraneous-conductive-parts
- Supplementary bonding in locations of increased shock risk
- Circuit protective conductor (CPC) per outgoing circuit, sized per the appropriate jurisdiction table
- Zs verification against the disconnection-time-limited Zs_max
- RCD/GFCI requirement flags per jurisdiction
- A full 8-section reasoning rationale (per upstream WI2)

This is **stage 1** of the earthing skill — schematic only. Plan-view and declaration-only stages are deferred.

## Jurisdictions supported

| Jurisdiction | Standards files loaded | CPC sizing | RCD blanket |
|---|---|---|---|
| GB | BS 7671:2018+A3 Reg 411 family, Tables 54.7/54.8 | Table 54.7 or adiabatic 54.1 | TT only |
| EU | IEC 60364-4-41, IEC 60364-5-54 | Table 54.2 or adiabatic 543.1.2 | TT only |
| INT | IEC 60364-4-41, IEC 60364-5-54 | Table 54.2 or adiabatic 543.1.2 | TT only |
| US | NEC 2023 Article 250 | Table 250.122 (by OCPD rating) | NEC GFCI rules |

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
    ├── uk-dwelling-tn-cs/
    │   ├── input.json
    │   ├── reasoning.md
    │   └── output.json
    ├── intl-rural-tt/
    │   ├── input.json
    │   ├── reasoning.md
    │   └── output.json
    └── us-commercial-nec/
        ├── input.json
        ├── reasoning.md
        └── output.json
```

## Eval coverage matrix

| Eval ID | Category | Tests |
|---|---|---|
| eval-01-uk-dwelling-tn-cs | happy_path | Full triple consumed-intent, TN-C-S, 6 circuits, all pass |
| eval-02-rural-tt-system | edge_case | TT system, electrode design, blanket RCD requirement |
| eval-03-cpc-undersized-trap | validation_trap | Generator must reject an undersized declared CPC |
| eval-04-missing-soil-resistivity | missing_input | TT with no soil data — must flag, not invent |
| eval-05-jurisdiction-us-nec | jurisdiction_switch | NEC terminology, Table 250.122, no BS 7671 citations |
| eval-06-rationale-block | rationale_block | 8-section taxonomy + clause-cited decisions per WI2 |

All 6 WI5 categories covered. See `evals/runner-config.json` for scoring thresholds.

## Tool calls awaiting runtime

Per upstream WI3, this skill declares — but does not yet invoke — the following calculation tools. The IR marks affected items `tool_call_pending: true` and accepts engineer-provided values in the interim.

| Tool name | Purpose |
|---|---|
| `calc.electrode_resistance` | Compute Ra from soil resistivity and electrode geometry |
| `calc.adiabatic_cpc` | Compute CPC CSA via adiabatic equation for fault energy let-through |

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
````

- [ ] **Step 3: Validate the README structure matches lighting-layout**

Run:
```bash
python3 -c "
ref = [l.strip() for l in open('electrical/lighting-layout/README.md') if l.startswith('## ')]
new = [l.strip() for l in open('electrical/earthing/README.md') if l.startswith('## ')]
print(f'Reference (lighting-layout) sections: {len(ref)}')
print(f'New (earthing) sections: {len(new)}')
required = ['## What this skill produces', '## Jurisdictions supported', '## Cross-drawing intent contract', '## File structure', '## Eval coverage matrix', '## Known limitations', '## Versioning']
for r in required:
    assert r in new, f'Missing section: {r}'
print('All required sections present')
"
```
Expected: section counts then `All required sections present`

- [ ] **Step 4: Commit**

```bash
git add electrical/earthing/README.md
git commit -m "docs: earthing README rewrite — eval coverage matrix + jurisdiction table + WI3 tool deferrals"
```

---

### Task 24: Final verification + SKILLS_STATUS.md update

**Files:**
- Modify: `SKILLS_STATUS.md`
- Verify: All ~35 files in `electrical/earthing/`

This is the closeout. Run the full skill-level validation and flip the status from `stub` to `beta`.

- [ ] **Step 1: Run full file-count verification**

Run:
```bash
python3 << 'PYEOF'
import os, json
root = 'electrical/earthing'
expected = {
    'skill-level': ['README.md', 'CHANGELOG.md', 'skill.manifest.json', 'inputs.json'],
    'prompts': ['generator.md', 'validator.md', 'reviewer.md'],
    'schemas': ['earthing-ir.schema.json', 'earthing-intent.schema.json'],
    'rules': ['electrode-selection.yaml', 'cpc-sizing.yaml'],
    'constraints': ['electrode-resistance.yaml', 'bonding-geometry.yaml'],
    'validation': ['zs-compliance.yaml', 'bonding-completeness.yaml', 'cpc-sizing.yaml'],
    'ontology': ['earthing-system-types.json'],
    'docs': ['engineering-philosophy.md', 'known-limitations.md'],
    'evals': ['runner-config.json', 'eval-01-uk-dwelling-tn-cs.yaml', 'eval-02-rural-tt-system.yaml', 'eval-03-cpc-undersized-trap.yaml', 'eval-04-missing-soil-resistivity.yaml', 'eval-05-jurisdiction-us-nec.yaml', 'eval-06-rationale-block.yaml'],
    'examples/uk-dwelling-tn-cs': ['input.json', 'reasoning.md', 'output.json'],
    'examples/intl-rural-tt': ['input.json', 'reasoning.md', 'output.json'],
    'examples/us-commercial-nec': ['input.json', 'reasoning.md', 'output.json'],
}

missing = []
total = 0
for subdir, files in expected.items():
    base = root if subdir == 'skill-level' else f'{root}/{subdir}'
    for f in files:
        p = f'{base}/{f}'
        total += 1
        if not os.path.isfile(p):
            missing.append(p)

print(f'Expected files: {total}')
print(f'Missing: {len(missing)}')
for m in missing:
    print(f'  - {m}')
assert not missing, f'{len(missing)} files missing'
print('All files present')
PYEOF
```
Expected: `Expected files: 35`, `Missing: 0`, `All files present`

- [ ] **Step 2: Verify manifest standards array references files (not folders) — the consumption-pattern proof**

Run:
```bash
python3 -c "
import json
m = json.load(open('electrical/earthing/skill.manifest.json'))
folders = [s for s in m['standards'] if s.endswith('/') or s.count('.') == 0]
files = [s for s in m['standards'] if not s.endswith('/') and '.' in s.split('/')[-1]]
print(f'Folders referenced: {len(folders)}')
print(f'Files referenced: {len(files)}')
assert len(folders) == 0, 'Manifest must reference specific files only — no bare folders'
assert len(files) >= 8, f'Expected at least 8 specific standards files; got {len(files)}'
print('Consumption-pattern proof: PASS')
"
```
Expected: `Folders referenced: 0`, `Files referenced: 11`, `Consumption-pattern proof: PASS`

- [ ] **Step 3: Verify all referenced standards files exist on disk**

Run:
```bash
python3 -c "
import json, os
m = json.load(open('electrical/earthing/skill.manifest.json'))
missing = [s for s in m['standards'] if not os.path.isfile(s)]
print(f'Referenced standards files: {len(m[\"standards\"])}')
print(f'Missing on disk: {len(missing)}')
for x in missing:
    print(f'  - {x}')
assert not missing
print('All standards files exist')
"
```
Expected: 11 referenced, 0 missing, `All standards files exist`

- [ ] **Step 4: Run JSON schema parse on both schemas**

Run:
```bash
python3 -c "
import json, jsonschema
for f in ['earthing-ir.schema.json', 'earthing-intent.schema.json']:
    with open(f'electrical/earthing/schemas/{f}') as fh:
        s = json.load(fh)
    jsonschema.Draft7Validator.check_schema(s)
    print(f'{f}: schema valid')
"
```
Expected: both schemas valid

- [ ] **Step 5: Run schema validation on all 3 example outputs**

Run:
```bash
python3 -c "
import json, jsonschema, os, glob
schema = json.load(open('electrical/earthing/schemas/earthing-ir.schema.json'))
resolver = jsonschema.RefResolver(base_uri=f'file://{os.path.abspath(\"electrical/earthing/schemas/\")}/', referrer=schema)
v = jsonschema.Draft7Validator(schema, resolver=resolver)
for out_path in glob.glob('electrical/earthing/examples/*/output.json'):
    d = json.load(open(out_path))
    errors = list(v.iter_errors(d))
    status = 'PASS' if not errors else f'FAIL ({len(errors)} errors)'
    print(f'{out_path}: {status}')
    for e in errors[:3]:
        print(f'  -> {e.message} at {list(e.path)}')
"
```
Expected: all three examples PASS

- [ ] **Step 6: Update `SKILLS_STATUS.md`**

Read the current file. Find the row for `electrical/earthing` and update its status from `stub` to `beta`.

```bash
grep -n "earthing" SKILLS_STATUS.md
```

Then edit the line:
- Old: `| electrical/earthing | stub | — | — |`
- New: `| electrical/earthing | beta | 1.0.0 | 2026-05-15 |`

Use the Edit tool with the appropriate old_string/new_string from the file.

- [ ] **Step 7: Final commit**

```bash
git add electrical/earthing/ SKILLS_STATUS.md
git commit -m "feat(earthing): v1.0.0 beta — schematic stage 1 complete"
```

- [ ] **Step 8: Skill summary check**

Run:
```bash
echo "=== Earthing skill summary ==="
find electrical/earthing -type f | sort
echo
echo "=== Line totals ==="
find electrical/earthing -type f -exec wc -l {} + | tail -1
```
Expected: 35 files; total line count between 2500–5000 lines.

---

## Self-review checklist

After all 24 tasks are executed:

1. **Spec coverage:** Re-read `docs/superpowers/specs/2026-05-15-earthing-skill-design.md` § File Set table. Every named file must exist in `electrical/earthing/`.
2. **Type consistency:** `cpc_sizing_method` enum used in Task 2 (schema), Task 6 (rules), Task 8 (generator), Task 11 (validation cpc-sizing.yaml) — verify all four use the same 5 string values.
3. **Cross-task path references:** Tasks 5 (manifest) → 8 (generator) → 14 (eval-01) all reference the same 11 standards files. Verify with the Step 2 script above.
4. **Consumption-pattern proof:** Tasks 5 and 8 must reference files (not folders). Verified in Tasks 8 Step 3 and 24 Step 2.
5. **WI alignment:**
   - WI1 (inputs taxonomy): Task 4 — inputs.json present
   - WI2 (rationale block): Task 2 (schema requires), Task 8 (generator emits), eval-06 (covered)
   - WI3 (calc executor deferral): Task 2 (schema flag), Task 8 (step 5), Tasks 13/24 (docs)
   - WI4 (cross-drawing intents): Task 3 (intent schema), Task 5 (consumes_intents), Task 8 (step 1)
   - WI5 (eval categories): Tasks 14–19 cover all 6 categories
6. **No placeholders:** Every step has actual content. Search for "TODO" / "TBD" / "implement later" — none should remain.

---

## Execution handoff

**Plan complete and saved to `docs/superpowers/plans/2026-05-15-earthing-skill.md`.**

Two execution options:

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration.

**2. Inline Execution** — Execute tasks in this session using `executing-plans`, batch execution with checkpoints.

Which approach?
