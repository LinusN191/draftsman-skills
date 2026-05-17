# Arc-Flash Skill (Phase B) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `electrical/arc-flash` v1.0.0 beta — per-node arc-flash analysis (IE / AFB / PPE / shock-approach) consuming fault-level + db-layout-rollup intents, producing arc-flash intent for downstream labelling skill.

**Architecture:** Project-scoped cascade tree mirroring `fault-level`. Five-method controlled vocabulary with fallback chain (ieee1584_2018 → ieee1584_2002 → lee_1982 → nfpa70e_table → pending; dc_doan for DC nodes). Unified cascade with `current_type: ac | dc` tag. All math deferred to new `calc.arc_flash_incident_energy` tool (WI3 pattern; tool_call_pending: true on every node until DraftsMan runtime ships).

**Tech Stack:** JSON Schema draft-07 (schemas), YAML 1.2 (rules/constraints/validation/evals), Markdown (prompts/docs/READMEs), `jq` + Python `jsonschema` for parse validation.

**Reference:** Spec at `docs/superpowers/specs/2026-05-17-arc-flash-skill-design.md`. Pattern parents: `electrical/fault-level/` + `electrical/cable-sizing/` (just shipped). Phase A standards layers at `shared/standards/electrical/IEEE1584/` + `NFPA70E/` (shipped commits `b34976f..08e2521`).

---

## Task list (23 tasks)

| # | Task | Files | Layer |
|---|---|---|---|
| 1 | New calc contract `calc.arc_flash_incident_energy` | 1 | shared/calculations |
| 2 | Bootstrap folder + CHANGELOG + initial README | 3 | electrical/arc-flash |
| 3 | `schemas/arc-flash-ir.schema.json` (project-scoped cascade IR) | 1 | electrical/arc-flash |
| 4 | `schemas/arc-flash-intent.schema.json` (downstream slim subset) | 1 | electrical/arc-flash |
| 5 | `inputs.json` (16-item discovery taxonomy) | 1 | electrical/arc-flash |
| 6 | `skill.manifest.json` (36 standards + 1 calc references) | 1 | electrical/arc-flash |
| 7 | 5 rules YAMLs | 5 | electrical/arc-flash |
| 8 | 4 constraints YAMLs | 4 | electrical/arc-flash |
| 9 | 2 ontology JSONs (method-types + current-types) | 2 | electrical/arc-flash |
| 10 | `prompts/generator.md` (14-step chain) | 1 | electrical/arc-flash |
| 11 | `prompts/validator.md` (10 INV invariants) | 1 | electrical/arc-flash |
| 12 | `prompts/reviewer.md` (8 D dimensions) | 1 | electrical/arc-flash |
| 13 | 4 validation YAMLs (12 deterministic checks) | 4 | electrical/arc-flash |
| 14 | 2 docs files (engineering-philosophy + known-limitations) | 2 | electrical/arc-flash |
| 15 | `evals/runner-config.json` + eval-01 UK happy path | 2 | electrical/arc-flash |
| 16 | eval-02 (MV cascade) + eval-03 (coefficient fallback trap) | 2 | electrical/arc-flash |
| 17 | eval-04 (missing fault data) + eval-05 (US restricted IE>40) | 2 | electrical/arc-flash |
| 18 | eval-06 (rationale block) + eval-07 (DC PV string) | 2 | electrical/arc-flash |
| 19 | eval-08 (conservative t_clear) + eval-09 (shock-approach OOR) | 2 | electrical/arc-flash |
| 20 | Example 1 — UK LV switchgear (4 files) | 4 | electrical/arc-flash |
| 21 | Example 2 — INT MV substation (4 files) | 4 | electrical/arc-flash |
| 22 | Example 3 — US PV+DCFC (4 files) | 4 | electrical/arc-flash |
| 23 | Final README rewrite + SKILLS_STATUS update + push | 2 | repo root |

**Total file count:** 49 (48 in `electrical/arc-flash/` + 1 calc contract in `shared/calculations/electrical/`).

---

## Task 1: New calc contract `calc.arc_flash_incident_energy`

**Files:**
- Create: `shared/calculations/electrical/arc-flash-incident-energy.json`

- [ ] **Step 1: Write the calc contract**

File: `shared/calculations/electrical/arc-flash-incident-energy.json`

```json
{
  "id": "arc-flash-incident-energy",
  "executor": "tool",
  "tool_name": "calc.arc_flash_incident_energy",
  "description": "Compute arc-flash incident energy, arc-flash boundary, and arcing current per IEEE 1584:2018 (preferred), IEEE 1584:2002 (legacy), Lee 1982 (theoretical fallback), NFPA 70E table method (lookup), or Doan + Stokes & Oppenlander (DC). Method is selected by caller via `method` input; `method=auto` triggers the full fallback chain.",
  "version": "1.0.0",
  "inputs": [
    {"id": "method", "type": "enum", "values": ["auto", "ieee1584_2018", "ieee1584_2002", "lee_1982", "nfpa70e_table", "dc_doan"], "required": true, "description": "Method selection; `auto` runs the fallback chain"},
    {"id": "current_type", "type": "enum", "values": ["ac", "dc"], "required": true, "description": "AC routes through IEEE 1584 / Lee / NFPA70E; DC routes through Doan + Stokes & Oppenlander"},
    {"id": "voltage_v", "type": "number", "min": 50, "max": 15000, "required": true, "unit": "V"},
    {"id": "bolted_fault_current_a", "type": "number", "min": 100, "max": 200000, "required": true, "unit": "A"},
    {"id": "arcing_time_s", "type": "number", "min": 0.005, "max": 5.0, "required": true, "unit": "s"},
    {"id": "working_distance_mm", "type": "number", "min": 100, "max": 2000, "required": true, "unit": "mm"},
    {"id": "gap_mm", "type": "number", "min": 5, "max": 254, "required": false, "unit": "mm", "description": "Required for ieee1584_2018 + ieee1584_2002 + dc_doan; defaulted from gap-distance-table when omitted"},
    {"id": "electrode_config", "type": "enum", "values": ["VCB", "VCBB", "HCB", "VOA", "HOA"], "required": false, "description": "Required for AC IEEE methods; null for DC"},
    {"id": "enclosure_volume_mm3", "type": "number", "required": false, "description": "Required for ieee1584_2018 §10.5 enclosure-size adjustment"},
    {"id": "equipment_type", "type": "string", "required": false, "description": "Required for nfpa70e_table method lookup"}
  ],
  "outputs": [
    {"id": "applied_method", "type": "enum", "values": ["ieee1584_2018", "ieee1584_2002", "lee_1982", "nfpa70e_table", "dc_doan", "pending"], "description": "Which method actually produced the result"},
    {"id": "method_fallback_trail", "type": "array", "description": "Full trail of methods tried with skipped/applied + reason"},
    {"id": "arcing_current_a", "type": "number", "unit": "A", "nullable": true},
    {"id": "incident_energy_cal_per_cm2", "type": "number", "unit": "cal/cm²", "nullable": true, "description": "Null when method=nfpa70e_table OR method=pending"},
    {"id": "arc_flash_boundary_mm", "type": "number", "unit": "mm", "nullable": true},
    {"id": "voltage_class_used", "type": "string", "description": "600V | 2700V | 14300V | intermediate | dc"},
    {"id": "ppe_category_suggestion", "type": "integer", "min": 1, "max": 4, "nullable": true, "description": "From NFPA 70E Table 130.7(C)(15)(c) lookup based on IE; null when IE is null"}
  ],
  "references": [
    "shared/standards/electrical/IEEE1584/method-2018-600V-coefficients.json",
    "shared/standards/electrical/IEEE1584/method-2018-2700V-coefficients.json",
    "shared/standards/electrical/IEEE1584/method-2018-14300V-coefficients.json",
    "shared/standards/electrical/IEEE1584/intermediate-voltage-interpolation.json",
    "shared/standards/electrical/IEEE1584/incident-energy-formula.json",
    "shared/standards/electrical/IEEE1584/boundary-distance-formula.json",
    "shared/standards/electrical/IEEE1584/arc-current-formula.json",
    "shared/standards/electrical/IEEE1584/arc-current-variation-high-low.json",
    "shared/standards/electrical/IEEE1584/method-2002-lee-formula.json",
    "shared/standards/electrical/IEEE1584/method-2002-doughty-neal-formula.json",
    "shared/standards/electrical/IEEE1584/adjustment-factor-non-standard-gap.json",
    "shared/standards/electrical/IEEE1584/adjustment-factor-non-standard-distance.json",
    "shared/standards/electrical/IEEE1584/adjustment-factor-enclosure-size.json",
    "shared/standards/electrical/IEEE1584/equipment-classification.json",
    "shared/standards/electrical/NFPA70E/annex-d-1-doan-method.json",
    "shared/standards/electrical/NFPA70E/annex-d-2-stokes-oppenlander-method.json",
    "shared/standards/electrical/NFPA70E/table-130-7-C-15-a-ac-tasks.json",
    "shared/standards/electrical/NFPA70E/table-130-7-C-15-b-dc-tasks.json",
    "shared/standards/electrical/NFPA70E/table-130-7-C-15-c-ppe-categories.json"
  ],
  "verification_status": "verified-against-source",
  "implementation_note": "Contract only — runtime implementation deferred per WI3 until DraftsMan runtime ships. Consumer skills (electrical/arc-flash) carry tool_call_pending: true on every cascade node until then.",
  "license_note": "Tool contract; no copyrighted standards content reproduced — references point to Phase A files that hold the factual coefficients."
}
```

- [ ] **Step 2: Verify JSON parses + register in REQUIRED_TOOLS.json**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
jq . shared/calculations/electrical/arc-flash-incident-energy.json > /dev/null && echo "OK"
```

Expected: `OK`.

Check whether `shared/calculations/REQUIRED_TOOLS.json` exists and lists registered tools. If it does, append `calc.arc_flash_incident_energy` to its list.

```bash
test -f shared/calculations/REQUIRED_TOOLS.json && echo "registry exists" || echo "no registry — skip"
```

If registry exists, edit it to add the new tool entry. Match the pattern of existing entries (each is a `{tool_name, registered_for, spec_summary, owner, since_version}` object).

- [ ] **Step 3: Commit**

```bash
git add shared/calculations/electrical/arc-flash-incident-energy.json shared/calculations/REQUIRED_TOOLS.json
git commit -m "feat(calc): calc.arc_flash_incident_energy contract — IEEE 1584 / Lee / NFPA70E / Doan fallback chain"
```

---

## Task 2: Bootstrap folder + CHANGELOG + initial README

**Files:**
- Create: `electrical/arc-flash/CHANGELOG.md`
- Create: `electrical/arc-flash/README.md` (initial — full rewrite in Task 23)
- Create directory structure under `electrical/arc-flash/`

- [ ] **Step 1: Create directory structure**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
mkdir -p electrical/arc-flash/{prompts,schemas,rules,constraints,validation,ontology,docs,evals,examples}
mkdir -p electrical/arc-flash/examples/{uk-lv-switchgear,intl-mv-substation,us-pv-with-dcfc}
```

- [ ] **Step 2: Create CHANGELOG.md**

File: `electrical/arc-flash/CHANGELOG.md`

```markdown
# Changelog — electrical/arc-flash

All notable changes to the arc-flash skill. Follows [Keep a Changelog](https://keepachangelog.com).

## [1.0.0-beta] — 2026-05-17

### Added — v1.0.0 beta (Phase B)
- 14-step generator chain (`prompts/generator.md`) — IEEE 1584:2018 + IEEE 1584:2002 + Lee 1982 + NFPA 70E table method + Doan/Stokes & Oppenlander for DC
- Project-scoped cascade IR (`schemas/arc-flash-ir.schema.json`) with method-fallback-trail per node
- Slim downstream `arc-flash` intent (`schemas/arc-flash-intent.schema.json`) — consumed by future `electrical/arc-flash-labelling` skill
- 5 rules: method-fallback-chain, electrode-config-inference, t-clear-defaults, ppe-category-mapping, label-required-equipment
- 4 constraints: incident-energy-finite, boundary-distance-physical, ppe-category-monotonic, method-fallback-consistency
- 4 validation YAMLs (12 deterministic checks)
- 2 ontology files: method-types (5 methods + pending), current-types (ac/dc with applicable methods)
- 9 evals (6 WI5 categories + 3 skill-specific)
- 3 worked examples: UK LV switchgear / INT MV substation / US PV+DCFC

### Phase A dependencies (already shipped)
- `shared/standards/electrical/IEEE1584/` (28 files, production)
- `shared/standards/electrical/NFPA70E/` (25 files, production)
- `shared/schemas/core/standards-{formula,table,section}.schema.json`
- `shared/validation/standards/*.py` (3 validation scripts)

### Tool calls awaiting runtime (WI3 deferral)
- `calc.arc_flash_incident_energy` (contract: `shared/calculations/electrical/arc-flash-incident-energy.json` — shipped this sprint)

### Consumes intents
- `fault-level` (per-node Ibf + ipk + X/R)
- `db-layout-rollup` (per-board equipment_type + ocpd_type + voltage)
- Engineer-declared fallback when intents absent

### Produces intent
- `arc-flash` — per-node IE + AFB + PPE + shock-approach + label_recommended; consumed by future `electrical/arc-flash-labelling` skill (stub committed 2026-05-17 at `electrical/arc-flash-labelling/`)

### Known limitations
- DC > 1000V not supported (utility PV 1500V systems deferred to v1.1)
- 17 IEEE 1584 coefficient files in Phase A standards layer are pending-verification; skill falls back gracefully to Lee 1982 or NFPA 70E table method until coefficients are transcribed
- Arc-flash label content generation is a separate future skill (arc-flash-labelling)
- Time-graded protection coordination is a separate future skill (refines t_clear precision)
```

- [ ] **Step 3: Create initial README.md (full rewrite in Task 23)**

File: `electrical/arc-flash/README.md`

```markdown
# `arc-flash` — Per-Node Arc-Flash Analysis (IEEE 1584 + NFPA 70E)

**Status:** `beta` (v1.0.0 — Phase B)

Initial scaffold. Full README written at Task 23 after all artefacts are in place.

See [`docs/superpowers/specs/2026-05-17-arc-flash-skill-design.md`](../../docs/superpowers/specs/2026-05-17-arc-flash-skill-design.md) for the design spec.
Phase A (IEEE 1584 + NFPA 70E standards layers) already shipped — see `shared/standards/electrical/IEEE1584/` and `NFPA70E/`.
```

- [ ] **Step 4: Verify structure**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
find electrical/arc-flash -type d | sort
```

Expected output:
```
electrical/arc-flash
electrical/arc-flash/constraints
electrical/arc-flash/docs
electrical/arc-flash/evals
electrical/arc-flash/examples
electrical/arc-flash/examples/intl-mv-substation
electrical/arc-flash/examples/uk-lv-switchgear
electrical/arc-flash/examples/us-pv-with-dcfc
electrical/arc-flash/ontology
electrical/arc-flash/prompts
electrical/arc-flash/rules
electrical/arc-flash/schemas
electrical/arc-flash/validation
```

- [ ] **Step 5: Commit**

```bash
git add electrical/arc-flash/
git commit -m "feat(arc-flash): bootstrap folder + CHANGELOG + initial README"
```

---

## Task 3: `schemas/arc-flash-ir.schema.json` (project-scoped cascade IR)

**Files:**
- Create: `electrical/arc-flash/schemas/arc-flash-ir.schema.json`

- [ ] **Step 1: Write the IR schema**

File: `electrical/arc-flash/schemas/arc-flash-ir.schema.json`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "electrical/arc-flash/schemas/arc-flash-ir.schema.json",
  "title": "Arc-Flash IR (project-scoped cascade)",
  "description": "Project-scoped arc-flash analysis IR per IEEE 1584:2018 + NFPA 70E. Cascade tree mirrors fault-level; each node carries method-applied + method-fallback-trail + IE/AFB/PPE/shock-approach.",
  "type": "object",
  "required": ["drawing_type", "version", "meta", "jurisdiction", "project_supply", "cascade", "compliance_summary", "rationale"],
  "additionalProperties": false,
  "properties": {
    "drawing_type": { "const": "arc_flash_study" },
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
    "jurisdiction": { "enum": ["GB", "EU", "INT", "US"] },
    "project_supply": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "voltage_v": { "type": "integer" },
        "phases": { "enum": ["single", "split", "three"] },
        "frequency_hz": { "type": "integer", "enum": [50, 60] }
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
            "required": ["code", "message", "severity"],
            "properties": {
              "code": { "enum": ["ARC_FLASH_PENDING", "LEE_1982_FALLBACK_USED", "NFPA70E_TABLE_METHOD_USED", "INCIDENT_ENERGY_GT_40_RESTRICTED", "CONSERVATIVE_T_CLEAR_DEFAULT_USED", "SHOCK_APPROACH_BEYOND_TABLE_RANGE"] },
              "message": { "type": "string" },
              "severity": { "enum": ["error", "warning", "info"] },
              "node_id": { "type": "string" }
            }
          }
        },
        "assumptions": { "type": "array", "items": { "type": "string" } }
      }
    },
    "flags": { "type": "array", "items": { "type": "string" } },
    "rationale": { "$ref": "../../../shared/schemas/core/rationale.schema.json" }
  },
  "definitions": {
    "CascadeNode": {
      "type": "object",
      "required": ["node_id", "node_kind", "designation", "equipment", "fault_inputs", "ocpd_inputs", "geometry", "arc_flash", "shock_approach", "label", "checks"],
      "additionalProperties": false,
      "properties": {
        "node_id": { "type": "string", "pattern": "^[A-Z][A-Z0-9.\\-]{0,63}$" },
        "parent_node_id": { "type": ["string", "null"] },
        "node_kind": { "enum": ["service_entrance", "feeder", "sub_feeder", "final_circuit"] },
        "designation": { "type": "string" },
        "equipment": {
          "type": "object",
          "required": ["type", "current_type", "voltage_v"],
          "additionalProperties": false,
          "properties": {
            "type": { "type": "string" },
            "current_type": { "enum": ["ac", "dc"] },
            "voltage_v": { "type": "number", "minimum": 50, "maximum": 15000 },
            "voltage_class": { "enum": ["600V", "2700V", "14300V", "intermediate", "dc"] },
            "electrode_config": { "enum": ["VCB", "VCBB", "HCB", "VOA", "HOA"], "nullable": true, "description": "null for DC nodes" },
            "electrode_config_source": { "enum": ["auto_inferred_from_equipment_type", "engineer_override", "default_VCB", "not_applicable_dc"] }
          }
        },
        "fault_inputs": {
          "type": "object",
          "required": ["ibf_ka_max"],
          "additionalProperties": false,
          "properties": {
            "ibf_ka_max": { "type": "number", "minimum": 0 },
            "ibf_ka_min": { "type": "number", "minimum": 0 },
            "x_over_r": { "type": "number", "minimum": 0 },
            "z_total_ohm": { "type": "number", "minimum": 0 }
          }
        },
        "ocpd_inputs": {
          "type": "object",
          "required": ["t_clear_s", "t_clear_source"],
          "additionalProperties": false,
          "properties": {
            "ocpd_type": { "type": "string" },
            "t_clear_s": { "type": "number", "minimum": 0.001, "maximum": 5.0 },
            "t_clear_source": { "enum": ["engineer_declared", "ocpd_type_default", "conservative_default"] }
          }
        },
        "geometry": {
          "type": "object",
          "required": ["working_distance_mm"],
          "additionalProperties": false,
          "properties": {
            "working_distance_mm": { "type": "number", "minimum": 100, "maximum": 2000 },
            "gap_distance_mm": { "type": "number", "minimum": 5, "maximum": 254 },
            "enclosure_volume_mm3": { "type": "number", "minimum": 0 }
          }
        },
        "arc_flash": {
          "type": "object",
          "required": ["method_applied", "method_fallback_trail"],
          "additionalProperties": false,
          "properties": {
            "method_applied": { "enum": ["ieee1584_2018", "ieee1584_2002", "lee_1982", "nfpa70e_table", "dc_doan", "pending"] },
            "method_fallback_trail": {
              "type": "array",
              "minItems": 1,
              "items": {
                "type": "object",
                "required": ["method", "result", "reason"],
                "properties": {
                  "method": { "enum": ["ieee1584_2018", "ieee1584_2002", "lee_1982", "nfpa70e_table", "dc_doan"] },
                  "result": { "enum": ["applied", "skipped"] },
                  "reason": { "type": "string" }
                }
              }
            },
            "arcing_current_a": { "type": ["number", "null"] },
            "incident_energy_cal_per_cm2": { "type": ["number", "null"], "minimum": 0 },
            "arc_flash_boundary_mm": { "type": ["number", "null"], "minimum": 0 },
            "ppe_category": { "type": ["integer", "null"], "minimum": 1, "maximum": 4 },
            "ppe_category_source": { "enum": ["computed_from_E", "engineer_override", "nfpa70e_table_lookup", "null_when_pending"] }
          }
        },
        "shock_approach": {
          "type": "object",
          "required": ["limited_approach_movable_mm", "limited_approach_fixed_mm", "restricted_approach_mm", "source"],
          "additionalProperties": false,
          "properties": {
            "limited_approach_movable_mm": { "type": ["number", "string"], "description": "Number for direct distances; string when value is non-numeric (e.g. 'avoid contact' for <50V)" },
            "limited_approach_fixed_mm": { "type": ["number", "string"] },
            "restricted_approach_mm": { "type": ["number", "string"] },
            "source": { "type": "string", "description": "Citation to NFPA 70E Table 130.4(C)(a) or (b) row" }
          }
        },
        "label": {
          "type": "object",
          "required": ["label_recommended"],
          "additionalProperties": false,
          "properties": {
            "label_recommended": { "type": "boolean" },
            "label_required_per": { "type": "string" },
            "engineer_can_skip_with_reason": { "type": "boolean" }
          }
        },
        "checks": {
          "type": "object",
          "required": ["tool_call_pending"],
          "additionalProperties": false,
          "properties": {
            "incident_energy_finite": { "type": "boolean" },
            "boundary_ge_working_distance": { "type": "boolean" },
            "ppe_category_consistent_with_E": { "type": "boolean" },
            "method_fallback_consistent": { "type": "boolean" },
            "tool_call_pending": { "type": "boolean" }
          }
        }
      }
    }
  }
}
```

- [ ] **Step 2: Verify schema parses + is valid JSON Schema Draft-07**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
jq . electrical/arc-flash/schemas/arc-flash-ir.schema.json > /dev/null && echo "JSON valid"
python3 -c "import json,jsonschema; s=json.load(open('electrical/arc-flash/schemas/arc-flash-ir.schema.json')); jsonschema.Draft7Validator.check_schema(s); print('Schema valid')"
```

Expected: `JSON valid` + `Schema valid`.

- [ ] **Step 3: Commit**

```bash
git add electrical/arc-flash/schemas/arc-flash-ir.schema.json
git commit -m "feat(arc-flash): arc-flash-ir.schema.json — project-scoped cascade IR"
```

---

## Task 4: `schemas/arc-flash-intent.schema.json` (downstream slim subset)

**Files:**
- Create: `electrical/arc-flash/schemas/arc-flash-intent.schema.json`

- [ ] **Step 1: Write the intent schema**

File: `electrical/arc-flash/schemas/arc-flash-intent.schema.json`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "electrical/arc-flash/schemas/arc-flash-intent.schema.json",
  "title": "Arc-Flash Intent (downstream slim subset)",
  "description": "Stable subset of the arc-flash IR consumed by future electrical/arc-flash-labelling skill. One entry per cascade node carrying everything needed to render an arc-flash label per ANSI Z535.4 + NFPA 70E §130.5(H). Forward-compat: optional fields may be added freely; required-field changes require a major intent_version bump.",
  "type": "object",
  "required": ["intent_kind", "version", "nodes"],
  "additionalProperties": false,
  "properties": {
    "intent_kind": { "const": "arc-flash" },
    "version": { "type": "string", "pattern": "^\\d+\\.\\d+(\\.\\d+)?$" },
    "produced_by_skill_version": { "type": "string" },
    "tool_call_pending": { "type": "boolean", "description": "true if any node has method_applied: pending" },
    "nodes": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["node_id", "designation", "equipment_type", "voltage_v", "working_distance_mm", "limited_approach_movable_mm", "limited_approach_fixed_mm", "restricted_approach_mm", "method_applied", "label_recommended", "produced_at"],
        "additionalProperties": false,
        "properties": {
          "node_id": { "type": "string" },
          "parent_node_id": { "type": ["string", "null"] },
          "designation": { "type": "string" },
          "equipment_type": { "type": "string" },
          "current_type": { "enum": ["ac", "dc"] },
          "voltage_v": { "type": "number" },
          "incident_energy_cal_per_cm2": { "type": ["number", "null"] },
          "arc_flash_boundary_mm": { "type": ["number", "null"] },
          "working_distance_mm": { "type": "number" },
          "limited_approach_movable_mm": { "type": ["number", "string"] },
          "limited_approach_fixed_mm": { "type": ["number", "string"] },
          "restricted_approach_mm": { "type": ["number", "string"] },
          "ppe_category": { "type": ["integer", "null"], "minimum": 1, "maximum": 4 },
          "method_applied": { "enum": ["ieee1584_2018", "ieee1584_2002", "lee_1982", "nfpa70e_table", "dc_doan", "pending"] },
          "label_recommended": { "type": "boolean" },
          "label_required_per": { "type": "string" },
          "produced_at": { "type": "string", "format": "date" }
        }
      }
    }
  }
}
```

- [ ] **Step 2: Verify**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
jq . electrical/arc-flash/schemas/arc-flash-intent.schema.json > /dev/null && echo "JSON valid"
python3 -c "import json,jsonschema; s=json.load(open('electrical/arc-flash/schemas/arc-flash-intent.schema.json')); jsonschema.Draft7Validator.check_schema(s); print('Schema valid')"
```

- [ ] **Step 3: Commit**

```bash
git add electrical/arc-flash/schemas/arc-flash-intent.schema.json
git commit -m "feat(arc-flash): arc-flash-intent.schema.json — downstream slim subset"
```

---

## Task 5: `inputs.json` (16-item discovery taxonomy)

**Files:**
- Create: `electrical/arc-flash/inputs.json`

- [ ] **Step 1: Write inputs.json**

File: `electrical/arc-flash/inputs.json`

```json
{
  "$schema": "../../shared/schemas/core/inputs.schema.json",
  "skill": "arc-flash",
  "version": "1.0.0",
  "description": "Discovery taxonomy — what the generator prompt asks for / extracts from upstream intents before computing arc-flash.",
  "inputs": [
    {"id": "jurisdiction",                   "type": "enum",   "values": ["GB","EU","INT","US"], "description": "Standards family / regulatory framing"},
    {"id": "project_supply",                 "type": "object", "description": "Voltage / phases / frequency from db-layout-rollup or engineer"},
    {"id": "fault_data_from_intent",         "type": "boolean","description": "true if fault-level intent supplies per-node Ifault"},
    {"id": "fault_data_declared",            "type": "array",  "description": "Per-node Ibf + X/R + Z (engineer fallback when intent absent)"},
    {"id": "equipment_data_from_intent",     "type": "boolean","description": "true if db-layout-rollup supplies per-board equipment_type + ocpd_type"},
    {"id": "equipment_data_declared",        "type": "array",  "description": "Per-node equipment_type + ocpd_type (engineer fallback)"},
    {"id": "current_type_per_node",          "type": "array",  "description": "Optional per-node ac | dc override (default ac unless equipment_type matches dc patterns)"},
    {"id": "electrode_config_overrides",     "type": "array",  "description": "Optional per-node VCB/VCBB/HCB/VOA/HOA override when auto-inference is wrong"},
    {"id": "t_clear_per_node",               "type": "array",  "description": "Engineer-declared t_clear (s) per node; overrides ocpd-type default"},
    {"id": "working_distance_overrides",     "type": "array",  "description": "Optional per-node working-distance override (default from Phase A working-distance-defaults.json)"},
    {"id": "gap_distance_overrides",         "type": "array",  "description": "Optional per-node gap-distance override (default from Phase A gap-distance-table.json)"},
    {"id": "enclosure_volume_overrides",     "type": "array",  "description": "Optional per-node enclosure-volume for §10.5 adjustment"},
    {"id": "ppe_category_overrides",         "type": "array",  "description": "Optional per-node PPE category override (e.g. uprate for safety margin)"},
    {"id": "method_force_per_node",          "type": "array",  "description": "Optional per-node method override (skip fallback chain) — for legacy-label reproduction"},
    {"id": "label_skip_with_reason",         "type": "array",  "description": "Optional per-node label-skip declaration with justification (rare, requires explicit reason)"},
    {"id": "compliance_target_overrides",    "type": "object", "description": "Optional client-specification overrides (e.g. tighter PPE thresholds)"}
  ]
}
```

- [ ] **Step 2: Verify**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
jq '.inputs | length' electrical/arc-flash/inputs.json
```

Expected: `16`.

- [ ] **Step 3: Commit**

```bash
git add electrical/arc-flash/inputs.json
git commit -m "feat(arc-flash): inputs.json — 16-item discovery taxonomy"
```

---

## Task 6: `skill.manifest.json` (36 standards + 1 calc references)

**Files:**
- Create: `electrical/arc-flash/skill.manifest.json`

- [ ] **Step 1: Write the manifest**

File: `electrical/arc-flash/skill.manifest.json`

```json
{
  "skill": "arc-flash",
  "version": "1.0.0",
  "discipline": "electrical",
  "subdiscipline": "safety-analysis",
  "description": "Per-node arc-flash analysis per IEEE 1584:2018 (primary) + fallback chain (IEEE 1584:2002 → Lee 1982 → NFPA 70E table method) + DC method (Doan + Stokes & Oppenlander). Produces incident energy, arc-flash boundary, shock-approach boundaries, and PPE category 1-4. Consumes fault-level + db-layout-rollup intents; emits arc-flash intent for downstream labelling skill. Unified AC/DC cascade with per-node current_type tag.",
  "status": "beta",
  "licence": "MIT",
  "inputs_path": "inputs.json",
  "inputs": [
    "jurisdiction",
    "project_supply",
    "fault-data-from-intent-or-declared",
    "equipment-data-from-intent-or-declared",
    "current-type-per-node",
    "electrode-config-overrides",
    "t-clear-per-node",
    "working-distance-overrides",
    "gap-distance-overrides",
    "method-force-per-node"
  ],
  "outputs": ["arc-flash-ir"],
  "output_schema": "electrical/arc-flash/schemas/arc-flash-ir.schema.json",
  "produces_intent": ["arc-flash"],
  "produces_intent_schemas": {
    "arc-flash": "electrical/arc-flash/schemas/arc-flash-intent.schema.json"
  },
  "consumes_intents": ["fault-level", "db-layout-rollup"],
  "standards": [
    "shared/standards/electrical/IEEE1584/method-2018-600V-coefficients.json",
    "shared/standards/electrical/IEEE1584/method-2018-2700V-coefficients.json",
    "shared/standards/electrical/IEEE1584/method-2018-14300V-coefficients.json",
    "shared/standards/electrical/IEEE1584/intermediate-voltage-interpolation.json",
    "shared/standards/electrical/IEEE1584/electrode-config-VCB-coefficients.json",
    "shared/standards/electrical/IEEE1584/electrode-config-VCBB-coefficients.json",
    "shared/standards/electrical/IEEE1584/electrode-config-HCB-coefficients.json",
    "shared/standards/electrical/IEEE1584/electrode-config-VOA-coefficients.json",
    "shared/standards/electrical/IEEE1584/electrode-config-HOA-coefficients.json",
    "shared/standards/electrical/IEEE1584/arc-current-formula.json",
    "shared/standards/electrical/IEEE1584/arc-current-variation-high-low.json",
    "shared/standards/electrical/IEEE1584/incident-energy-formula.json",
    "shared/standards/electrical/IEEE1584/boundary-distance-formula.json",
    "shared/standards/electrical/IEEE1584/adjustment-factor-non-standard-gap.json",
    "shared/standards/electrical/IEEE1584/adjustment-factor-non-standard-distance.json",
    "shared/standards/electrical/IEEE1584/adjustment-factor-enclosure-size.json",
    "shared/standards/electrical/IEEE1584/method-2002-lee-formula.json",
    "shared/standards/electrical/IEEE1584/method-2002-doughty-neal-formula.json",
    "shared/standards/electrical/IEEE1584/voltage-classes.json",
    "shared/standards/electrical/IEEE1584/gap-distance-table.json",
    "shared/standards/electrical/IEEE1584/working-distance-defaults.json",
    "shared/standards/electrical/IEEE1584/equipment-classification.json",
    "shared/standards/electrical/NFPA70E/section-130-4-shock-boundaries.json",
    "shared/standards/electrical/NFPA70E/section-130-5-arc-flash-risk-assessment.json",
    "shared/standards/electrical/NFPA70E/section-130-7-ppe.json",
    "shared/standards/electrical/NFPA70E/table-130-4-C-a-AC-approach.json",
    "shared/standards/electrical/NFPA70E/table-130-4-C-b-DC-approach.json",
    "shared/standards/electrical/NFPA70E/table-130-5-G-equipment-table.json",
    "shared/standards/electrical/NFPA70E/table-130-5-H-label-requirements.json",
    "shared/standards/electrical/NFPA70E/table-130-7-C-15-a-ac-tasks.json",
    "shared/standards/electrical/NFPA70E/table-130-7-C-15-b-dc-tasks.json",
    "shared/standards/electrical/NFPA70E/table-130-7-C-15-c-ppe-categories.json",
    "shared/standards/electrical/NFPA70E/table-130-7-C-16-ppe-required-items.json",
    "shared/standards/electrical/NFPA70E/annex-d-1-doan-method.json",
    "shared/standards/electrical/NFPA70E/annex-d-2-stokes-oppenlander-method.json",
    "shared/standards/electrical/NFPA70E/article-130-overview.md"
  ],
  "calculations": [
    "shared/calculations/electrical/arc-flash-incident-energy.json"
  ],
  "ontology": [
    "electrical/arc-flash/ontology/method-types.json",
    "electrical/arc-flash/ontology/current-types.json"
  ],
  "rules": [
    "electrical/arc-flash/rules/method-fallback-chain.yaml",
    "electrical/arc-flash/rules/electrode-config-inference.yaml",
    "electrical/arc-flash/rules/t-clear-defaults.yaml",
    "electrical/arc-flash/rules/ppe-category-mapping.yaml",
    "electrical/arc-flash/rules/label-required-equipment.yaml"
  ],
  "constraints": [
    "electrical/arc-flash/constraints/incident-energy-finite.yaml",
    "electrical/arc-flash/constraints/boundary-distance-physical.yaml",
    "electrical/arc-flash/constraints/ppe-category-monotonic.yaml",
    "electrical/arc-flash/constraints/method-fallback-consistency.yaml"
  ],
  "validators": [
    "electrical/arc-flash/validation/cascade-tree-integrity.yaml",
    "electrical/arc-flash/validation/method-applied-from-vocabulary.yaml",
    "electrical/arc-flash/validation/tool-call-resolved.yaml",
    "electrical/arc-flash/validation/intent-shape.yaml"
  ],
  "prompts": {
    "generator": "electrical/arc-flash/prompts/generator.md",
    "validator": "electrical/arc-flash/prompts/validator.md",
    "reviewer":  "electrical/arc-flash/prompts/reviewer.md"
  },
  "evals": [
    "electrical/arc-flash/evals/eval-01-uk-lv-switchboard-happy-path.yaml",
    "electrical/arc-flash/evals/eval-02-mv-cascade-with-drawout.yaml",
    "electrical/arc-flash/evals/eval-03-coefficient-fallback-trap.yaml",
    "electrical/arc-flash/evals/eval-04-missing-fault-data.yaml",
    "electrical/arc-flash/evals/eval-05-jurisdiction-us-with-restricted.yaml",
    "electrical/arc-flash/evals/eval-06-rationale-block.yaml",
    "electrical/arc-flash/evals/eval-07-dc-pv-string.yaml",
    "electrical/arc-flash/evals/eval-08-conservative-t-clear-default.yaml",
    "electrical/arc-flash/evals/eval-09-shock-approach-out-of-range.yaml"
  ],
  "examples": [
    "electrical/arc-flash/examples/uk-lv-switchgear/",
    "electrical/arc-flash/examples/intl-mv-substation/",
    "electrical/arc-flash/examples/us-pv-with-dcfc/"
  ],
  "compatible_runtimes": [
    "DraftsMan >= 1.0",
    "Claude Code",
    "OpenClaw",
    "any-llm-agent"
  ],
  "changelog": "electrical/arc-flash/CHANGELOG.md"
}
```

- [ ] **Step 2: Verify every standards reference exists**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
jq -r '.standards[]' electrical/arc-flash/skill.manifest.json | while read p; do
  test -f "$p" || echo "MISSING $p"
done
```

Expected: no `MISSING` lines (all 36 already shipped in Phase A).

- [ ] **Step 3: Verify calc contract exists**

```bash
jq -r '.calculations[]' electrical/arc-flash/skill.manifest.json | while read p; do
  test -f "$p" || echo "MISSING $p"
done
```

Expected: no `MISSING` lines (calc contract shipped in Task 1).

- [ ] **Step 4: Commit**

```bash
git add electrical/arc-flash/skill.manifest.json
git commit -m "feat(arc-flash): skill.manifest.json — 36 standards + 1 calc reference"
```

---

## Task 7: 5 rules YAMLs

**Files (all create):**
- `electrical/arc-flash/rules/method-fallback-chain.yaml`
- `electrical/arc-flash/rules/electrode-config-inference.yaml`
- `electrical/arc-flash/rules/t-clear-defaults.yaml`
- `electrical/arc-flash/rules/ppe-category-mapping.yaml`
- `electrical/arc-flash/rules/label-required-equipment.yaml`

- [ ] **Step 1: method-fallback-chain.yaml**

```yaml
rule: method_fallback_chain
version: 1.0.0
description: |
  Per-node method selection. DC nodes always route through dc_doan.
  AC nodes try methods in order: ieee1584_2018 → ieee1584_2002 → lee_1982 → nfpa70e_table → pending.
  Record method_fallback_trail with skipped/applied + reason for every method attempted.
algorithm:
  dc_path:
    - condition: "current_type == 'dc' AND voltage_v <= 1000"
      action: "method = dc_doan"
    - condition: "current_type == 'dc' AND voltage_v > 1000"
      action: "method = pending"
      reason: "DC > 1000V out of Phase A scope"
  ac_path_ordered:
    - id: try_ieee1584_2018
      condition: "coefficients available for (voltage_class, electrode_config) per IEEE1584/method-2018-<class>-coefficients.json"
      on_success: "method = ieee1584_2018; trail = [{method: ieee1584_2018, result: applied, reason: 'coefficients available'}]"
      on_skip:    "trail.append({method: ieee1584_2018, result: skipped, reason: 'coefficients pending-verification (null) for voltage_class=<X>, electrode_config=<Y>'})"
    - id: try_ieee1584_2002
      condition: "Doughty/Neal coefficients transcribed per IEEE1584/method-2002-doughty-neal-formula.json"
      on_success: "method = ieee1584_2002"
      on_skip:    "trail.append({method: ieee1584_2002, result: skipped, reason: 'Doughty/Neal coefficients pending-verification'})"
    - id: try_lee_1982
      condition: "50 V <= voltage_v <= 15000 V AND t_clear_s <= 5.0"
      on_success: "method = lee_1982; emit non_compliance_flag LEE_1982_FALLBACK_USED"
      on_skip:    "trail.append({method: lee_1982, result: skipped, reason: 'voltage or t_clear out of range'})"
    - id: try_nfpa70e_table
      condition: "equipment_type matches a row in NFPA70E/table-130-7-C-15-a-ac-tasks.json or 130-7-C-15-b-dc-tasks.json"
      on_success: "method = nfpa70e_table; IE = null; AFB = null; PPE from table lookup; emit NFPA70E_TABLE_METHOD_USED"
      on_skip:    "trail.append({method: nfpa70e_table, result: skipped, reason: 'equipment_type not in table-method ontology'})"
    - id: pending
      condition: "fallthrough"
      on_apply: "method = pending; tool_call_pending = true; emit ARC_FLASH_PENDING"
binding_method_record:
  rule: "method_applied = last item in method_fallback_trail where result == 'applied'"
  validator: "validation/method-applied-from-vocabulary.yaml + constraints/method-fallback-consistency.yaml"
```

- [ ] **Step 2: electrode-config-inference.yaml**

```yaml
rule: electrode_config_inference
version: 1.0.0
description: |
  Auto-infer IEEE 1584 electrode configuration (VCB/VCBB/HCB/VOA/HOA) from db-layout-rollup
  equipment_type via Phase A ontology (IEEE1584/equipment-classification.json).
  Engineer override allowed per node; recorded in electrode_config_source.
inference_table:
  - if_equipment_type_matches: ["metal-clad switchgear", "LV switchgear", "MV switchgear", "LV panelboard", "load centre", "MCC", "Motor Control Centre", "industrial control panel", "meter socket enclosure"]
    map_to: VCB
    source_id: "IEEE 1584:2018 §5.1 + Annex C"
  - if_equipment_type_matches: ["switchgear with arc-resistant barrier", "arc-quench switchgear", "LV switchgear with insulating barrier"]
    map_to: VCBB
    source_id: "IEEE 1584:2018 §5.1"
  - if_equipment_type_matches: ["drawout breaker", "drawout switchgear", "racked-in switchgear", "horizontal-bus distribution"]
    map_to: HCB
    source_id: "IEEE 1584:2018 §5.1"
  - if_equipment_type_matches: ["overhead service drop", "open-bus distribution", "outdoor MV switchgear no enclosure", "exposed bus duct"]
    map_to: VOA
    source_id: "IEEE 1584:2018 §5.1"
  - if_equipment_type_matches: ["substation horizontal bus", "riser bus assembly", "horizontal exposed conductors"]
    map_to: HOA
    source_id: "IEEE 1584:2018 §5.1"
fallback:
  map_to: VCB
  rationale: "VCB is the most common LV configuration; lowest-risk default for 'unknown enclosed equipment'"
engineer_override:
  allowed: true
  recorded_as: "electrode_config_source = engineer_override"
dc_handling:
  applies: false
  recorded_as: "electrode_config = null AND electrode_config_source = not_applicable_dc"
```

- [ ] **Step 3: t-clear-defaults.yaml**

```yaml
rule: t_clear_defaults
version: 1.0.0
description: |
  Default OCPD clearing time (s) at predicted I_arc, by OCPD type. Priority:
  engineer_declared > ocpd_type_default > conservative 2.0s.
  Source tracked in t_clear_source field of the IR.
defaults_by_ocpd_type:
  instantaneous_only_magnetic:      0.05
  MCB_type_B_C_D:                   0.10
  MCCB_thermal_magnetic:            0.20
  MCCB_electronic_LSI:              0.10
  ACB_electronic:                   0.30
  ACB_with_intentional_delay:       0.50
  fuse_HV_full_range:               0.05
  fuse_LV_general_purpose:          0.20
  no_curve_data_available:          2.0
  unknown:                          2.0
priority_order:
  - engineer_declared
  - ocpd_type_default
  - conservative_default
record_field: t_clear_source
non_compliance_flags:
  - code: CONSERVATIVE_T_CLEAR_DEFAULT_USED
    severity: warning
    trigger: "t_clear_source == 'conservative_default'"
    message: "Conservative 2.0s default used for t_clear at node <node_id>. Refine via protection coordination study or declare ocpd_type."
```

- [ ] **Step 4: ppe-category-mapping.yaml**

```yaml
rule: ppe_category_mapping
version: 1.0.0
description: |
  Map computed incident energy (cal/cm²) to PPE category 1-4 per NFPA 70E:2024
  Table 130.7(C)(15)(c). Engineer may uprate (override to higher category) for safety
  margin but never downgrade.
source: "NFPA 70E:2024 Table 130.7(C)(15)(c)"
mapping:
  - if_incident_energy_cal_per_cm2_gte: 1.2
    and_lt: 4.0
    category: 1
  - if_incident_energy_cal_per_cm2_gte: 4.0
    and_lt: 8.0
    category: 2
  - if_incident_energy_cal_per_cm2_gte: 8.0
    and_lt: 25.0
    category: 3
  - if_incident_energy_cal_per_cm2_gte: 25.0
    and_lte: 40.0
    category: 4
  - if_incident_energy_cal_per_cm2_gt: 40.0
    category: null
    flag: INCIDENT_ENERGY_GT_40_RESTRICTED
    severity: error
    message: "IE > 40 cal/cm² — equipment restricted. Energized work only by specialised teams per facility risk assessment."
  - if_incident_energy_cal_per_cm2_lt: 1.2
    category: 0
    note: "Below threshold for 2nd-degree burn; no AR clothing required per §130.7. Skill still emits Cat 1 minimum for any energized work per industry convention."
engineer_override:
  uprate_allowed: true
  downrate_allowed: false
  recorded_as: "ppe_category_source = engineer_override"
table_method_path:
  when_method_applied: nfpa70e_table
  category_from: "NFPA 70E Table 130.7(C)(15)(a) for AC or 130.7(C)(15)(b) for DC"
  recorded_as: "ppe_category_source = nfpa70e_table_lookup"
```

- [ ] **Step 5: label-required-equipment.yaml**

```yaml
rule: label_required_equipment
version: 1.0.0
description: |
  Set label.label_recommended per NFPA 70E:2024 §130.5(H). Required for switchgear,
  switchboards, panelboards, MCCs, industrial control panels, meter sockets ≥240V.
  Exempt for single-family residential service + equipment <240V where no examination work performed.
source: "NFPA 70E:2024 §130.5(H) + Table 130.5(H)"
label_recommended_when:
  all_of:
    - equipment_type in:
        - "metal-clad switchgear"
        - "LV switchgear"
        - "MV switchgear"
        - "switchboard"
        - "LV panelboard"
        - "load centre"
        - "MCC"
        - "Motor Control Centre"
        - "industrial control panel"
        - "meter socket enclosure"
        - "drawout breaker"
    - voltage_v >= 240
exemptions:
  - condition: "equipment_type == 'single-family residential service'"
    label_recommended: false
    rationale: "Residential exemption per §130.5(H)"
  - condition: "voltage_v < 240 AND no examination work performed"
    label_recommended: false
    rationale: "Low-voltage exemption per §130.5(H)"
jurisdictional_notes:
  US: "Mandatory per OSHA + NFPA 70E §130.5(H). Required label content: nominal voltage, IE at working distance, AFB, PPE category, date of analysis."
  GB: "Voluntary but recommended best practice (HSG48 + IET CoP). Rationale notes this."
  EU: "Voluntary best practice. Rationale notes regional convention."
  INT: "Follow IEEE 1584 / NFPA 70E as de facto international best practice."
engineer_skip:
  allowed: true
  requires_justification: true
  recorded_as: "label.engineer_can_skip_with_reason = true + assumption logged"
```

- [ ] **Step 6: Verify all 5 YAMLs parse**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
for f in electrical/arc-flash/rules/*.yaml; do
  python3 -c "import yaml; yaml.safe_load(open('$f'))" && echo "OK $f"
done
```

Expected: 5 `OK` lines.

- [ ] **Step 7: Commit**

```bash
git add electrical/arc-flash/rules/
git commit -m "feat(arc-flash): 5 rules YAMLs — method fallback + electrode-config inference + t_clear defaults + PPE mapping + label requirements"
```

---

## Task 8: 4 constraints YAMLs

**Files (all create):**
- `electrical/arc-flash/constraints/incident-energy-finite.yaml`
- `electrical/arc-flash/constraints/boundary-distance-physical.yaml`
- `electrical/arc-flash/constraints/ppe-category-monotonic.yaml`
- `electrical/arc-flash/constraints/method-fallback-consistency.yaml`

- [ ] **Step 1: incident-energy-finite.yaml**

```yaml
constraint: incident_energy_finite
version: 1.0.0
description: |
  When method_applied is not pending AND not nfpa70e_table, the incident_energy_cal_per_cm2
  field must be a finite positive number (not null, NaN, or infinity). nfpa70e_table returns
  PPE category without computing IE — null is acceptable. pending means tool_call_pending —
  null is acceptable.
triggered_for: "every cascade node"
checks:
  - id: ie_finite_when_method_computes_it
    expression: |
      for each node n:
        if n.arc_flash.method_applied not in [pending, nfpa70e_table]:
          n.arc_flash.incident_energy_cal_per_cm2 is numeric AND
          n.arc_flash.incident_energy_cal_per_cm2 > 0 AND
          n.arc_flash.incident_energy_cal_per_cm2 < 10000  (sanity max)
    severity: error
    message: "Incident energy at {node_id} is not a finite positive number (method={method_applied}, IE={incident_energy_cal_per_cm2})"
  - id: ie_null_when_method_is_pending_or_table
    expression: |
      for each node n where n.arc_flash.method_applied in [pending, nfpa70e_table]:
        n.arc_flash.incident_energy_cal_per_cm2 is null
    severity: error
    message: "Method {method_applied} should return null incident energy; got {incident_energy_cal_per_cm2} at {node_id}"
source: "Sanity check — physical incident energy is always positive + bounded"
```

- [ ] **Step 2: boundary-distance-physical.yaml**

```yaml
constraint: boundary_distance_physical
version: 1.0.0
description: |
  Arc-flash boundary distance must be physical: AFB >= working_distance_mm (a worker
  standing at working_distance must be at or inside the boundary). When E = 1.2 cal/cm²
  exactly, AFB = working_distance.
triggered_for: "every cascade node where arc_flash_boundary_mm is numeric (not null)"
checks:
  - id: afb_ge_working_distance
    expression: |
      for each node n where n.arc_flash.arc_flash_boundary_mm is numeric:
        n.arc_flash.arc_flash_boundary_mm >= n.geometry.working_distance_mm
    severity: error
    message: "AFB ({afb_mm}mm) < working_distance ({working_distance_mm}mm) at {node_id} — unphysical"
  - id: afb_equals_working_distance_at_threshold
    expression: |
      for each node n where 1.19 <= n.arc_flash.incident_energy_cal_per_cm2 <= 1.21:
        abs(n.arc_flash.arc_flash_boundary_mm - n.geometry.working_distance_mm) <= 5  (mm tolerance)
    severity: warning
    message: "At E=1.2 cal/cm² (boundary threshold), AFB should equal working_distance ±5mm; got AFB={afb_mm}, D={working_distance_mm}"
source: "IEEE 1584:2018 §8 — AFB = D × (E/1.2)^(1/x); at E=1.2, AFB=D"
```

- [ ] **Step 3: ppe-category-monotonic.yaml**

```yaml
constraint: ppe_category_monotonic
version: 1.0.0
description: |
  Across all cascade nodes where IE is numeric, PPE category must be monotonic with IE.
  If IE_a < IE_b then PPE_a <= PPE_b. Catches lookup errors in the PPE-category-mapping
  rule. Cross-node integrity check.
triggered_for: "the cascade as a whole (not per-node)"
checks:
  - id: monotonic_pairwise
    expression: |
      for every pair (a, b) of nodes where both have numeric IE + numeric PPE:
        if a.arc_flash.incident_energy_cal_per_cm2 < b.arc_flash.incident_energy_cal_per_cm2:
          a.arc_flash.ppe_category <= b.arc_flash.ppe_category
    severity: error
    message: "PPE non-monotonic: node {a.node_id} (IE={a.IE}, Cat={a.cat}) vs {b.node_id} (IE={b.IE}, Cat={b.cat})"
  - id: category_matches_mapping_rule
    expression: |
      for each node n where IE is numeric:
        n.arc_flash.ppe_category matches the mapping rule per rules/ppe-category-mapping.yaml
        (IE 1.2-4 = 1; 4-8 = 2; 8-25 = 3; 25-40 = 4; >40 = null + RESTRICTED flag)
    severity: error
    message: "PPE category {cat} at {node_id} doesn't match mapping for IE={IE}"
source: "NFPA 70E:2024 Table 130.7(C)(15)(c) thresholds"
```

- [ ] **Step 4: method-fallback-consistency.yaml**

```yaml
constraint: method_fallback_consistency
version: 1.0.0
description: |
  method_applied must equal the last 'applied' entry in method_fallback_trail. Catches
  generator bugs where the trail and applied tag disagree.
triggered_for: "every cascade node"
checks:
  - id: trail_last_applied_matches_method_applied
    expression: |
      for each node n:
        let applied_entries = [e for e in n.arc_flash.method_fallback_trail if e.result == 'applied']
        if applied_entries is empty:
          n.arc_flash.method_applied == 'pending'
        else:
          applied_entries.length == 1 AND
          applied_entries[0].method == n.arc_flash.method_applied
    severity: error
    message: "method_applied={method_applied} doesn't match last 'applied' entry in fallback trail at {node_id}"
  - id: skipped_entries_have_reason
    expression: |
      for each node n:
        for each entry in n.arc_flash.method_fallback_trail where entry.result == 'skipped':
          entry.reason is non-empty
    severity: error
    message: "Skipped fallback entry without reason at {node_id} (method={entry.method})"
source: "Audit requirement — every skipped fallback must explain why"
```

- [ ] **Step 5: Verify all 4 YAMLs parse**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
for f in electrical/arc-flash/constraints/*.yaml; do
  python3 -c "import yaml; yaml.safe_load(open('$f'))" && echo "OK $f"
done
```

Expected: 4 `OK` lines.

- [ ] **Step 6: Commit**

```bash
git add electrical/arc-flash/constraints/
git commit -m "feat(arc-flash): 4 constraints YAMLs — IE finite + AFB physical + PPE monotonic + fallback consistency"
```

---

## Task 9: 2 ontology JSONs (method-types + current-types)

**Files (all create):**
- `electrical/arc-flash/ontology/method-types.json`
- `electrical/arc-flash/ontology/current-types.json`

- [ ] **Step 1: method-types.json**

```json
{
  "$schema": "../../../shared/schemas/core/ontology.schema.json",
  "ontology": "method-types",
  "version": "1.0.0",
  "description": "Enumeration of arc-flash calculation methods supported by the arc-flash skill. Each entry maps method id → applicability + bias + source standard.",
  "entries": [
    {
      "id": "ieee1584_2018",
      "label": "IEEE 1584:2018 (current empirical method)",
      "source_standard": "IEEE 1584:2018",
      "voltage_range_v": [208, 15000],
      "current_type": "ac",
      "bias": "most_realistic",
      "applies_when": "Coefficients available for (voltage_class, electrode_config)",
      "fallback_priority": 1
    },
    {
      "id": "ieee1584_2002",
      "label": "IEEE 1584:2002 (Doughty/Neal empirical)",
      "source_standard": "IEEE 1584:2002",
      "voltage_range_v": [208, 15000],
      "current_type": "ac",
      "bias": "slightly_conservative_vs_2018",
      "applies_when": "Doughty/Neal coefficients transcribed",
      "fallback_priority": 2,
      "primary_use": "legacy_label_reproduction"
    },
    {
      "id": "lee_1982",
      "label": "Lee 1982 (theoretical upper bound)",
      "source_standard": "Lee 1982 IEEE-IAS paper + IEEE 1584:2018 §2",
      "voltage_range_v": [50, 15000],
      "current_type": "ac",
      "bias": "significantly_conservative_2_to_5x",
      "applies_when": "Always available (no coefficients needed)",
      "fallback_priority": 3,
      "primary_use": "fallback_when_empirical_coefficients_pending_verification"
    },
    {
      "id": "nfpa70e_table",
      "label": "NFPA 70E Table Method (equipment-class lookup)",
      "source_standard": "NFPA 70E:2024 Table 130.7(C)(15)(a)/(b)",
      "voltage_range_v": [50, 15000],
      "current_type": "ac_or_dc",
      "bias": "most_conservative",
      "applies_when": "equipment_type matches table-method ontology row",
      "fallback_priority": 4,
      "output_note": "Returns PPE category only — no incident energy or arc-flash boundary computed"
    },
    {
      "id": "dc_doan",
      "label": "Doan 2007 + Stokes & Oppenlander 1991 (DC method)",
      "source_standard": "NFPA 70E:2024 Annex D §D.1 + §D.2",
      "voltage_range_v": [50, 1000],
      "current_type": "dc",
      "bias": "realistic_for_dc",
      "applies_when": "current_type == dc AND voltage_v <= 1000",
      "fallback_priority": "exclusive_for_dc"
    },
    {
      "id": "pending",
      "label": "tool_call_pending (no method fired)",
      "source_standard": "WI3 deferral pattern",
      "voltage_range_v": "any",
      "current_type": "any",
      "bias": "no_output",
      "applies_when": "Fallthrough — no method in chain applies",
      "fallback_priority": "terminal_fallback",
      "output_note": "All numeric outputs null; tool_call_pending: true; assumption logged"
    }
  ]
}
```

- [ ] **Step 2: current-types.json**

```json
{
  "$schema": "../../../shared/schemas/core/ontology.schema.json",
  "ontology": "current-types",
  "version": "1.0.0",
  "description": "Enumeration of current types (AC / DC) with applicable arc-flash methods + electrode-config applicability + shock-approach table reference.",
  "entries": [
    {
      "id": "ac",
      "label": "Alternating current",
      "applicable_methods": ["ieee1584_2018", "ieee1584_2002", "lee_1982", "nfpa70e_table"],
      "electrode_config_required": true,
      "shock_approach_table": "NFPA 70E:2024 Table 130.4(C)(a)",
      "voltage_range_v": [50, 15000],
      "auto_inference_hint": "Default when equipment_type does not match DC patterns",
      "common_equipment": ["LV switchgear", "MV switchgear", "panelboard", "MCC", "drawout breaker"]
    },
    {
      "id": "dc",
      "label": "Direct current",
      "applicable_methods": ["dc_doan"],
      "electrode_config_required": false,
      "shock_approach_table": "NFPA 70E:2024 Table 130.4(C)(b)",
      "voltage_range_v": [50, 1000],
      "auto_inference_hint": "Auto-set when equipment_type matches: PV string, PV combiner, DC fast charger (DCFC), battery bank, battery room, BESS, telecom DC system",
      "common_equipment": ["PV combiner box", "PV string", "DCFC unit", "battery bank", "BESS rack", "telecom 48V DC bus"]
    }
  ]
}
```

- [ ] **Step 3: Verify both parse + count entries**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
jq -r '.entries | length' electrical/arc-flash/ontology/method-types.json
jq -r '.entries | length' electrical/arc-flash/ontology/current-types.json
```

Expected: `6` (5 methods + pending) and `2` (ac + dc).

- [ ] **Step 4: Commit**

```bash
git add electrical/arc-flash/ontology/
git commit -m "feat(arc-flash): 2 ontology JSONs — method-types (6) + current-types (2)"
```

---

## Task 10: `prompts/generator.md` (14-step chain)

**Files:**
- Create: `electrical/arc-flash/prompts/generator.md`

- [ ] **Step 1: Write the generator prompt**

File: `electrical/arc-flash/prompts/generator.md`

```markdown
# Arc-Flash — Generator Prompt

You are a senior electrical safety engineer producing an arc-flash analysis per IEEE 1584:2018 (primary) with fallback to IEEE 1584:2002 / Lee 1982 / NFPA 70E table method, plus Doan + Stokes & Oppenlander for DC. Your output is a structured IR conforming to `electrical/arc-flash/schemas/arc-flash-ir.schema.json` plus an emitted `arc-flash` intent conforming to `electrical/arc-flash/schemas/arc-flash-intent.schema.json`.

## Inputs (resolution order)

1. **Preferred — consumed intents:**
   - `fault-level` (per-node ibf_ka_max + ibf_ka_min + ipk_ka + x_over_r_ratio + z_total_ohm)
   - `db-layout-rollup` (per-board equipment_type + ocpd_type + voltage_v + phases + location)
2. **Engineer overlay (always required where intents don't cover):**
   - t_clear_s per node (with OCPD-type defaults from rules/t-clear-defaults.yaml as fallback)
   - working_distance_mm per node (defaults from Phase A IEEE1584/working-distance-defaults.json)
   - current_type override (auto-inferred from equipment_type; engineer override per node)
   - electrode_config override (auto-inferred from equipment_type via Phase A IEEE1584/equipment-classification.json; engineer override)
3. **Engineer fallback (when intents absent):**
   - Full per-node fault data + equipment data declarations

## The 14-step chain

### Step 1 — Ingest fault-level intent
Extract per-node `ibf_ka_max`, `ibf_ka_min`, `ipk_ka`, `x_over_r_ratio`, `z_total_ohm`, `node_id`, `node_kind`. If intent absent: take engineer-declared per-node fault data; record in `meta.consumed_intents` and `compliance_summary.assumptions[]`.

### Step 2 — Ingest db-layout-rollup intent
Extract per-board (or per-circuit): `equipment_type`, `ocpd_type`, `voltage_v`, `phases`, `location`. If intent absent: engineer fallback.

### Step 3 — Determine jurisdiction
Read `jurisdiction` from inputs. Load applicable regulatory framing:
- **US:** NFPA 70E §130.5(H) labels mandatory; PPE category enforcement strict
- **GB / EU / INT:** Best-practice (HSG48 + IET CoP); labels recommended but voluntary

### Step 4 — Build cascade tree
Construct the cascade tree using `node_id` paths from the fault-level intent. Naming pattern matches fault-level (e.g., `MSB-1.F03.DB-L1`). Root nodes have `parent_node_id: null` and `node_kind: "service_entrance"`.

### Step 5 — Per-node: auto-infer current_type
Default `ac`. Switch to `dc` if equipment_type matches: "PV string", "PV combiner box", "DC fast charger", "DCFC", "battery bank", "battery room", "BESS", "telecom DC". Engineer override allowed per node via `current_type_per_node` input.

### Step 6 — Per-node: auto-infer electrode_config (AC nodes only)
Match equipment_type against `rules/electrode-config-inference.yaml` patterns:
- "metal-clad switchgear" / "LV panelboard" / "MCC" → VCB
- "switchgear with arc-resistant barrier" → VCBB
- "drawout breaker" / "racked switchgear" → HCB
- "overhead service drop" / "open-bus" → VOA
- "substation bus" / "riser bus" → HOA
- Fallback: VCB

Record `electrode_config_source: auto_inferred_from_equipment_type | engineer_override | default_VCB | not_applicable_dc`.

### Step 7 — Per-node: determine t_clear_s
Priority chain:
1. Engineer-declared `t_clear_per_node` for this node
2. OCPD-type default from `rules/t-clear-defaults.yaml`
3. Conservative 2.0s

Record `t_clear_source: engineer_declared | ocpd_type_default | conservative_default`. If `conservative_default` used, emit `CONSERVATIVE_T_CLEAR_DEFAULT_USED` flag.

### Step 8 — Per-node: select method via fallback chain
Execute `rules/method-fallback-chain.yaml`:
- **DC nodes:** if voltage_v ≤ 1000 → `dc_doan`; else → `pending`.
- **AC nodes:** try in order: `ieee1584_2018` → `ieee1584_2002` → `lee_1982` → `nfpa70e_table` → `pending`. Record `method_fallback_trail[]` with `result: applied | skipped` and `reason` for every attempt.

Set `method_applied` = last entry in trail where `result == applied` (or `pending` if no method applied).

### Step 9 — Per-node: call calc.arc_flash_incident_energy
Pass: `method` (from Step 8), `current_type`, `voltage_v`, `bolted_fault_current_a` (use ibf_ka_max × 1000), `arcing_time_s` (= t_clear_s), `working_distance_mm`, `gap_mm` (from Phase A gap-distance-table.json or engineer), `electrode_config`, `enclosure_volume_mm3`, `equipment_type`.

Receive: `arcing_current_a`, `incident_energy_cal_per_cm2`, `arc_flash_boundary_mm`, `voltage_class_used`, `ppe_category_suggestion`.

Until DraftsMan runtime ships, the calc tool returns nothing — set `checks.tool_call_pending: true` AND use senior-engineer estimates for the numeric values (so the IR is human-readable). Mark in `compliance_summary.assumptions[]`.

### Step 10 — Per-node: lookup shock-approach distances
For AC nodes: `NFPA70E/table-130-4-C-a-AC-approach.json` keyed on voltage range.
For DC nodes: `NFPA70E/table-130-4-C-b-DC-approach.json`.

Populate `shock_approach.limited_approach_movable_mm`, `limited_approach_fixed_mm`, `restricted_approach_mm`, and `source` (citation to row used).

If voltage > 46 kV (out of Table 130.4 range): emit `SHOCK_APPROACH_BEYOND_TABLE_RANGE` flag (error severity).

### Step 11 — Per-node: assign PPE category
**If method_applied is ieee1584_2018 / ieee1584_2002 / lee_1982 / dc_doan:**
- Apply `rules/ppe-category-mapping.yaml` to `incident_energy_cal_per_cm2`
- 1.2–4 → Cat 1; 4–8 → Cat 2; 8–25 → Cat 3; 25–40 → Cat 4; >40 → null + `INCIDENT_ENERGY_GT_40_RESTRICTED` error
- Record `ppe_category_source: computed_from_E`

**If method_applied is nfpa70e_table:**
- Lookup row in `NFPA70E/table-130-7-C-15-a-ac-tasks.json` (AC) or `(b)-dc-tasks.json` (DC)
- Use the category from the matched row
- Record `ppe_category_source: nfpa70e_table_lookup`

**Engineer override (if specified for this node):**
- Allowed UP only (Cat 2 → Cat 3 OK; Cat 3 → Cat 2 NOT OK)
- Record `ppe_category_source: engineer_override`

**If method_applied is pending:**
- `ppe_category: null`
- `ppe_category_source: null_when_pending`

### Step 12 — Per-node: evaluate label_recommended
Apply `rules/label-required-equipment.yaml`:
- True when equipment_type ∈ {switchgear, switchboard, panelboard, MCC, industrial control panel, meter socket} AND voltage_v ≥ 240
- False for single-family residential service OR voltage < 240V with no examination work

Record `label_required_per` with the matched rule + clause reference. Set `engineer_can_skip_with_reason` if engineer explicitly declared a skip with justification.

### Step 13 — Run all 4 constraint files
Execute checks from `constraints/*.yaml`:
- `incident-energy-finite`: IE finite positive when method computes it; null when pending/table
- `boundary-distance-physical`: AFB ≥ working_distance; AFB = working_distance at E=1.2
- `ppe-category-monotonic`: cross-node monotonicity + per-node mapping consistency
- `method-fallback-consistency`: method_applied matches trail's last applied entry

Emit any violations to `compliance_summary.non_compliance_flags[]`.

### Step 14 — Emit arc-flash intent + assemble rationale block

**Intent emission:**
Build the slim downstream intent: one entry per cascade node containing required fields from `arc-flash-intent.schema.json`.

**Rationale block (8 sections per WI2):**

1. **Input Ingestion** — what came from each intent vs engineer-declared
2. **Cascade Topology** — node count by kind, AC/DC mix, naming convention
3. **Jurisdictional Framing** — US mandatory vs GB/EU/INT best-practice
4. **Method Selection Summary** — group nodes by method_applied; flag any pending or Lee/table fallbacks
5. **Per-node Arc-Flash Results** — IE / AFB / PPE per node (or group by category)
6. **Shock-Approach Boundaries** — table 130.4 row used per voltage class
7. **Label Recommendations** — which equipment requires labels + any engineer-justified skips
8. **Compliance + Assumptions + Tool-call Status** — pending flags, conservative defaults used, tool_call_pending count

`chat_summary` ≤ 200 words: lead with cascade scale, methods used, any pending/fallback flags, label count, key compliance findings.

## Output formatting

Emit two JSON documents:
1. The IR (`drawing_type: "arc_flash_study"`)
2. The intent (`intent_kind: "arc-flash"`)

Both must validate against their respective schemas.

## Tool-call deferral (WI3)

Until DraftsMan runtime ships `calc.arc_flash_incident_energy`, every affected node carries `checks.tool_call_pending: true` AND uses senior-engineer estimates for numeric values. Same pattern as fault-level + cable-sizing.

## Hard rules (never violate)

- Never invent IEEE 1584 coefficients — fallback chain handles null coefficients
- Never set `method_applied` outside the controlled vocabulary: `ieee1584_2018 | ieee1584_2002 | lee_1982 | nfpa70e_table | dc_doan | pending`
- Never produce negative IE or negative AFB
- Never skip `method_fallback_trail` — every node must show what was tried
- Every `shock_approach` block cites NFPA 70E:2024 Table 130.4(C)(a) or (b)
- DC nodes never use IEEE 1584 methods (different physics)
- t_clear > 5.0s is out of physical range — flag as error
- Never emit fewer than 8 rationale sections
- AC nodes must have an electrode_config from {VCB, VCBB, HCB, VOA, HOA}; DC nodes have electrode_config = null
```

- [ ] **Step 2: Verify step count**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
grep -c "^### Step " electrical/arc-flash/prompts/generator.md
```

Expected: `14`.

- [ ] **Step 3: Commit**

```bash
git add electrical/arc-flash/prompts/generator.md
git commit -m "feat(arc-flash): generator.md — 14-step chain with fallback method selection"
```

---

## Task 11: `prompts/validator.md` (10 INV invariants)

**Files:**
- Create: `electrical/arc-flash/prompts/validator.md`

- [ ] **Step 1: Write the validator prompt**

File: `electrical/arc-flash/prompts/validator.md`

```markdown
# Arc-Flash — Validator Prompt

You are a static analyzer running deterministic invariants over the IR produced by `prompts/generator.md`. Output a pass/fail report per invariant with offending `node_id`s. Do NOT modify the IR; do NOT make engineering judgement calls — only report whether each invariant holds.

## Inputs

- The IR JSON document (must validate against `arc-flash-ir.schema.json`)
- The emitted `arc-flash` intent JSON (must validate against `arc-flash-intent.schema.json`)

## Output shape

```json
{
  "validator_version": "1.0.0",
  "ir_valid_against_schema": true,
  "intent_valid_against_schema": true,
  "invariants": [
    { "id": "INV-01", "pass": true,  "summary": "All node_ids match path pattern", "offenders": [] },
    { "id": "INV-04", "pass": false, "summary": "Invalid method tag at 2 nodes", "offenders": ["MSB-1.F03", "DB-L1.C03"] }
  ],
  "overall_pass": false
}
```

## The 10 INV invariants

### INV-01 — Valid node_id path pattern + parent resolution
Every `cascade[].node_id` matches `^[A-Z][A-Z0-9.\-]{0,63}$`. Every non-null `parent_node_id` resolves to another node in `cascade[]`.

### INV-02 — current_type from controlled vocabulary
Every `equipment.current_type` is `ac` OR `dc`.

### INV-03 — Electrode config required for AC, null for DC
For every AC node: `equipment.electrode_config` is one of `VCB | VCBB | HCB | VOA | HOA`.
For every DC node: `equipment.electrode_config` is `null` AND `electrode_config_source == "not_applicable_dc"`.

### INV-04 — method_applied from controlled vocabulary
Every `arc_flash.method_applied` is one of: `ieee1584_2018 | ieee1584_2002 | lee_1982 | nfpa70e_table | dc_doan | pending`. No free-form strings.

### INV-05 — method_applied matches fallback trail
`method_applied` equals the `method` of the last entry in `method_fallback_trail` where `result == "applied"`. If no entry has `result: applied`, then `method_applied == "pending"`.

### INV-06 — Numeric outputs gated by method
- When `method_applied not in [pending, nfpa70e_table]`: `incident_energy_cal_per_cm2` is a finite positive number AND `arc_flash_boundary_mm >= working_distance_mm`.
- When `method_applied in [pending, nfpa70e_table]`: `incident_energy_cal_per_cm2 is null` AND `arc_flash_boundary_mm is null`.

### INV-07 — PPE category in 1-4 OR null
Every `arc_flash.ppe_category` is an integer 1-4 OR null. If IE numeric, it matches the mapping per Table 130.7(C)(15)(c): 1.2-4=1, 4-8=2, 8-25=3, 25-40=4. If IE > 40: `ppe_category` is null AND `INCIDENT_ENERGY_GT_40_RESTRICTED` flag is in `non_compliance_flags`.

### INV-08 — Shock-approach block complete
Every `shock_approach` block has all 3 distance fields (`limited_approach_movable_mm`, `limited_approach_fixed_mm`, `restricted_approach_mm`) populated (number or string like "avoid contact"), and `source` cites either Table 130.4(C)(a) for AC nodes or Table 130.4(C)(b) for DC nodes.

### INV-09 — DC nodes use dc_doan or pending only
For every node where `equipment.current_type == "dc"`: `method_applied` is `dc_doan` OR `pending`. Never an AC method.

### INV-10 — Intent shape + 1-to-1 mapping
The emitted `arc-flash` intent validates against `arc-flash-intent.schema.json`. AND for every cascade node in the IR, there is exactly one matching entry (by `node_id`) in `intent.nodes[]`. No extras, no missing.

## Reporting rules

- For each invariant: `pass | fail | not_applicable`
- `not_applicable` only when invariant's preconditions don't apply (e.g., INV-09 if no DC nodes exist)
- `offenders` is always an array (empty allowed)
- `overall_pass` is true iff every invariant is `pass` or `not_applicable`
- Do NOT propose fixes — that's the reviewer's job
```

- [ ] **Step 2: Verify invariant count**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
grep -c "^### INV-" electrical/arc-flash/prompts/validator.md
```

Expected: `10`.

- [ ] **Step 3: Commit**

```bash
git add electrical/arc-flash/prompts/validator.md
git commit -m "feat(arc-flash): validator.md — 10 INV invariants"
```

---

## Task 12: `prompts/reviewer.md` (8 D dimensions)

**Files:**
- Create: `electrical/arc-flash/prompts/reviewer.md`

- [ ] **Step 1: Write the reviewer prompt**

File: `electrical/arc-flash/prompts/reviewer.md`

```markdown
# Arc-Flash — Reviewer Prompt

You are a senior electrical safety engineer reviewing the IR + emitted intent produced by `prompts/generator.md` and validated by `prompts/validator.md`. Where the validator answers "is this self-consistent?", you answer "is this engineering work I'd put my name on for safety labels?".

## Inputs
- IR JSON
- emitted `arc-flash` intent JSON
- validator output JSON

## Output shape

```json
{
  "reviewer_version": "1.0.0",
  "dimensions": [
    { "id": "D1", "score": "pass", "notes": "..." },
    { "id": "D4", "score": "fail", "notes": "AFB at MSB-1 derives from E=10.4 + D=455 + x=1.85 → expected ~1500mm; reported 1280mm. Spot-check error." }
  ],
  "verdict": "approve | request_changes",
  "summary": "..."
}
```

## The 8 D dimensions

### D1 — Standards citations specific per node
Every per-node IE / AFB result references a clause (e.g., "IEEE 1584:2018 §7.5 incident energy formula"). Every PPE category cites Table 130.7(C)(15)(c). Every shock-approach distance cites Table 130.4(C)(a) or (b) row. No "per the standard" hand-waves.

### D2 — method_fallback_trail auditable
For every node with a multi-entry trail, each `skipped` entry names a specific reason (e.g., "coefficients pending-verification for VCB 600V"). The `applied` entry is the last one. Trail entries appear in fallback-priority order (2018 → 2002 → Lee → table → pending). Spot-check 3 random nodes; if any are scrambled, fail.

### D3 — Conservative-fallback warnings present
When `method_applied == lee_1982` OR `method_applied == nfpa70e_table`: the rationale's "Method Selection Summary" section explicitly notes the conservatism + recommends the action that would un-block IEEE 1584:2018 (e.g., "transcribe coefficients from IEEE 1584:2018 Annex C Table 4"). Failure: silent fallback with no warning.

### D4 — Per-node AFB arithmetic spot-check
Pick 2 random nodes with `method_applied` ∈ `{ieee1584_2018, ieee1584_2002, lee_1982, dc_doan}` and numeric IE. Manually verify:

```
AFB = D × (E / 1.2)^(1/x)
```

Where `x` is the distance exponent from the relevant coefficient table. The reported AFB should match within ±2%. If it diverges, fail and name the nodes.

### D5 — PPE category thresholds correct
Cross-check every node where IE is numeric:
- 1.2 ≤ IE < 4: Cat 1
- 4 ≤ IE < 8: Cat 2
- 8 ≤ IE < 25: Cat 3
- 25 ≤ IE ≤ 40: Cat 4
- IE > 40: null + RESTRICTED flag

Engineer overrides allowed UP only (Cat 2 → Cat 3 OK; Cat 3 → Cat 2 NOT OK).

### D6 — Shock-approach lookups consistent
For every node, verify the matched row of Table 130.4(C)(a) (AC) or (b) (DC):
- AC voltage 50-150V → row 1
- AC voltage 151-750V → row 2 (limited movable 3050mm, fixed 1070mm, restricted 305mm)
- AC voltage 751V-15kV → row 3
- AC voltage 15.1-36kV → row 4
- AC voltage 36.1-46kV → row 5
- AC voltage > 46kV: SHOCK_APPROACH_BEYOND_TABLE_RANGE flag present

DC rows similar via Table 130.4(C)(b). Verify the cited row matches the voltage_v.

### D7 — DC handling correct
For every DC node:
- `method_applied` is `dc_doan` OR `pending` (never IEEE 1584)
- `electrode_config` is null
- `electrode_config_source` is `not_applicable_dc`
- `shock_approach.source` cites Table 130.4(C)(b) (DC), not (a)

### D8 — Rationale block conformance
- `rationale.sections.length == 8` exactly
- `rationale.chat_summary.length ≤ 1200` characters (per shared rationale schema)
- Every section is non-empty (or explicitly says "none triggered" for inapplicable sections)
- Every decision in `sections[].decisions[]` has `label`, `summary`, `rule`, `code_clause`
- Section titles in order: Input Ingestion, Cascade Topology, Jurisdictional Framing, Method Selection Summary, Per-node Arc-Flash Results, Shock-Approach Boundaries, Label Recommendations, Compliance + Assumptions + Tool-call Status

## Severity + verdict

- Any D dimension `fail` → verdict = `request_changes`
- All D dimensions `pass` → verdict = `approve`
- `notes` should be specific (node_id / numeric value); avoid generic "review the analysis"

## What is OUT of scope for the reviewer

- Re-running the calc tool (the generator's tool calls handle that)
- Modifying the IR (return a verdict, never edits)
- Engineering style preferences not tied to a citable rule
- Whether the upstream fault-level intent is correct (that's the fault-level skill's reviewer)
```

- [ ] **Step 2: Verify D-dimension count**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
grep -c "^### D[0-9]" electrical/arc-flash/prompts/reviewer.md
```

Expected: `8`.

- [ ] **Step 3: Commit**

```bash
git add electrical/arc-flash/prompts/reviewer.md
git commit -m "feat(arc-flash): reviewer.md — 8 D dimensions"
```

---

## Task 13: 4 validation YAMLs (12 deterministic checks)

**Files (all create):**
- `electrical/arc-flash/validation/cascade-tree-integrity.yaml`
- `electrical/arc-flash/validation/method-applied-from-vocabulary.yaml`
- `electrical/arc-flash/validation/tool-call-resolved.yaml`
- `electrical/arc-flash/validation/intent-shape.yaml`

- [ ] **Step 1: cascade-tree-integrity.yaml (3 checks)**

```yaml
validator: cascade_tree_integrity
version: 1.0.0
description: |
  Structural integrity checks over the cascade tree. Catches broken parent_node_id refs,
  duplicate node_ids, and cycles before downstream consumers fail.
checks:
  - id: unique_node_ids
    description: "Every cascade[].node_id appears exactly once"
    expression: "len(distinct(cascade[].node_id)) == len(cascade)"
    severity: error
  - id: parent_refs_resolve
    description: "Every non-null parent_node_id points to a node in cascade"
    expression: "for each node n where n.parent_node_id != null: exists m in cascade where m.node_id == n.parent_node_id"
    severity: error
  - id: no_cycles
    description: "Cascade is a DAG; no parent chain loops back to itself"
    expression: "topological_sort(cascade) succeeds"
    severity: error
```

- [ ] **Step 2: method-applied-from-vocabulary.yaml (3 checks)**

```yaml
validator: method_applied_from_vocabulary
version: 1.0.0
description: |
  Enforce the controlled method vocabulary across cascade nodes and the emitted intent.
controlled_vocabulary:
  - ieee1584_2018
  - ieee1584_2002
  - lee_1982
  - nfpa70e_table
  - dc_doan
  - pending
checks:
  - id: method_applied_in_vocabulary
    description: "Every node's arc_flash.method_applied is in the controlled vocabulary"
    expression: "for each node n: n.arc_flash.method_applied in controlled_vocabulary"
    severity: error
  - id: dc_nodes_use_dc_method
    description: "DC nodes use dc_doan or pending (never AC methods)"
    expression: |
      for each node n where n.equipment.current_type == 'dc':
        n.arc_flash.method_applied in ['dc_doan', 'pending']
    severity: error
  - id: ac_nodes_dont_use_dc_method
    description: "AC nodes never use dc_doan"
    expression: |
      for each node n where n.equipment.current_type == 'ac':
        n.arc_flash.method_applied != 'dc_doan'
    severity: error
```

- [ ] **Step 3: tool-call-resolved.yaml (3 checks)**

```yaml
validator: tool_call_resolved
version: 1.0.0
description: |
  Tool-call status consistency across the IR. Same pattern as fault-level + cable-sizing:
  WI3 deferral allows tool_call_pending: true with engineer-estimated placeholder values
  visible in the IR. The validator only enforces that the boolean flag is well-formed.
checks:
  - id: tool_call_pending_is_boolean
    description: "Every node has checks.tool_call_pending as a boolean"
    expression: "for each node n: type(n.checks.tool_call_pending) == 'boolean'"
    severity: error
  - id: resolved_means_numeric_when_method_computes_ie
    description: |
      When tool_call_pending == false AND method_applied not in [pending, nfpa70e_table]:
      incident_energy_cal_per_cm2 + arc_flash_boundary_mm + arcing_current_a are all numeric
    expression: |
      for each node n where n.checks.tool_call_pending == false AND n.arc_flash.method_applied not in ['pending', 'nfpa70e_table']:
        n.arc_flash.incident_energy_cal_per_cm2 is numeric AND
        n.arc_flash.arc_flash_boundary_mm is numeric AND
        n.arc_flash.arcing_current_a is numeric
    severity: error
  - id: pending_flag_in_assumptions
    description: |
      If any node has method_applied == pending OR tool_call_pending == true,
      compliance_summary.assumptions[] mentions calc.arc_flash_incident_energy
    expression: |
      if any node has method_applied == 'pending' OR checks.tool_call_pending == true then
        compliance_summary.assumptions[] contains substring 'calc.arc_flash_incident_energy'
    severity: error
```

- [ ] **Step 4: intent-shape.yaml (3 checks)**

```yaml
validator: intent_shape
version: 1.0.0
description: |
  Emitted arc-flash intent satisfies its own schema AND covers the downstream consumer's
  (arc-flash-labelling skill) required fields. 1-to-1 mapping with cascade nodes.
checks:
  - id: validates_against_schema
    description: "Intent JSON validates against schemas/arc-flash-intent.schema.json"
    severity: error
  - id: one_to_one_with_cascade
    description: "Every cascade node has exactly one matching intent.nodes[] entry (by node_id)"
    expression: |
      for each node n in cascade:
        count(intent.nodes where node_id == n.node_id) == 1
      AND for each entry in intent.nodes:
        exists node n in cascade where n.node_id == entry.node_id
    severity: error
  - id: downstream_required_fields_present
    description: |
      Every intent.nodes[] entry has the required fields for the future arc-flash-labelling
      consumer: node_id, designation, equipment_type, voltage_v, working_distance_mm,
      limited_approach_movable_mm, limited_approach_fixed_mm, restricted_approach_mm,
      method_applied, label_recommended, produced_at
    expression: "all required fields present and non-null on every nodes[] entry"
    severity: error
```

- [ ] **Step 5: Verify all 4 YAMLs parse + count checks = 12**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
for f in electrical/arc-flash/validation/*.yaml; do
  python3 -c "import yaml; d=yaml.safe_load(open('$f')); print('OK', '$f', len(d['checks']), 'checks')"
done
```

Expected: 4 `OK` lines totalling 3+3+3+3 = 12 checks.

- [ ] **Step 6: Commit**

```bash
git add electrical/arc-flash/validation/
git commit -m "feat(arc-flash): 4 validation YAMLs — 12 deterministic IR-integrity checks"
```

---

## Task 14: 2 docs files (engineering-philosophy + known-limitations)

**Files (all create):**
- `electrical/arc-flash/docs/engineering-philosophy.md`
- `electrical/arc-flash/docs/known-limitations.md`

- [ ] **Step 1: engineering-philosophy.md**

```markdown
# Engineering Philosophy — Arc-Flash

This skill encodes a senior-engineer mental model for arc-flash analysis rather than just running calc formulas. The model:

## 1. Method fallback, not method blindness

When IEEE 1584:2018 empirical coefficients aren't available for a (voltage_class, electrode_config) pair, the skill doesn't return null — it falls through a chain: 2018 → 2002 → Lee 1982 → NFPA 70E table method → pending. Every node records the full trail so an engineer reading the IR can see exactly which methods were tried and why.

This matches what NFPA 70E §130.5 actually requires: "if you can't do an incident-energy analysis, use the table method." Falling back gracefully gives the engineer useful output (a conservative upper bound) instead of a blank screen.

## 2. Conservatism is acceptable; silence isn't

Lee 1982 typically produces 2-5× higher IE than IEEE 1584:2018 (Lee treats the arc as a black-body radiator with spherical dispersion — real arcs are far less efficient). NFPA 70E table method is even more conservative. The skill emits **info-severity flags** when these fallbacks fire (`LEE_1982_FALLBACK_USED`, `NFPA70E_TABLE_METHOD_USED`) so the engineer sees that the answer is conservative and knows the action to un-block it: transcribe IEEE 1584:2018 coefficients.

## 3. Shock-approach distances belong on every arc-flash label

Engineers sometimes ship arc-flash labels with only the thermal boundary. NFPA 70E §130.5(H) actually requires both: thermal (arc-flash) + shock (limited + restricted approach). The skill bundles them — every node carries both, sourced from Table 130.4(C)(a) (AC) or (b) (DC). The future labelling skill doesn't have to compute shock-approach separately.

## 4. DC is different physics; treat it differently

DC arcs sustain at lower voltages, have different arc-voltage characteristics, and aren't covered by IEEE 1584 (which is AC-only). The skill routes DC nodes through Doan + Stokes & Oppenlander (NFPA 70E Annex D §D.1 + §D.2). DC nodes get `electrode_config: null` (the IEEE 1584 electrode-config concept doesn't apply), and shock-approach comes from Table 130.4(C)(b), not (a).

A unified cascade tree with `current_type: ac | dc` per node — instead of two separate trees — keeps the parent-child relationships clean (a PV string is a child of its inverter; the inverter is AC, the string is DC, both live in the same cascade).

## 5. t_clear is the dominant uncertainty

Incident energy is approximately linear in arcing time. A 0.1s vs 0.3s clearing time is a 3× IE difference. The skill's t_clear handling reflects this: engineer-declared (most authoritative) > OCPD-type default (reasonable) > conservative 2.0s (worst case). When the 2.0s default fires, an explicit warning flag tells the engineer to refine via protection coordination.

## 6. Defer math to deterministic tools

The empirical IE formula, the log-log interpolation between voltage classes, the adjustment factors for non-standard gap/distance/enclosure — all LLM-unreliable. We push them to `calc.arc_flash_incident_energy` per the WI3 pattern. Until the DraftsMan runtime ships, every node carries `tool_call_pending: true` + senior-engineer estimates as placeholders.

## 7. Engineer judgement stays at the prompt layer

What lives in the prompt: method fallback policy, electrode-config inference, t_clear defaults, label-required rules, PPE override policy. What lives in calc tools: the actual formulas + table lookups. Split deliberately — same separation as fault-level / cable-sizing.

## 8. Forward-compatible intent contract for the labelling skill

The `arc-flash` intent is designed as a superset of what the future `electrical/arc-flash-labelling` skill will consume. When that skill ships, it conforms to this contract — not the other way round. We've stubbed `electrical/arc-flash-labelling/` (commit `711ebd5`) so the roadmap shows the dependency.

## 9. Hard rules over soft guidance

Things the generator MUST never do (invent IEEE 1584 coefficients, set method_applied outside vocabulary, emit negative IE/AFB, skip the method_fallback_trail). These live as `hard_rules:` in the generator prompt, not as suggestions. The validator enforces them mechanically.
```

- [ ] **Step 2: known-limitations.md**

```markdown
# Known Limitations — Arc-Flash v1.0.0

What v1.0.0 does NOT cover. These are deliberate scope boundaries, not bugs.

## Out of scope (v1.0.0)

| Topic | Why not | Where it goes |
|---|---|---|
| DC > 1000V | NFPA 70E Annex D scope stops at 1000V; utility-scale PV strings at 1500V need different methods | v1.1 OR `dc-high-voltage-arc-flash` future skill |
| BESS-specific safety analysis (Li-ion thermal runaway, gas evolution) | Different physics + different standards (UL 9540A, IEC 62619, NFPA 855) | Future `bess-safety` skill |
| Arc-flash label content generation (printable PDFs/SVGs) | Document production is a separate concern from engineering analysis | Future `electrical/arc-flash-labelling` skill (stubbed at commit `711ebd5`) |
| Time-graded protection coordination | Refines t_clear precision via OCPD time-current curve interaction; complex enough for its own skill | Future `protection-coordination` skill |
| MV utility-side fault contribution beyond what fault-level handles | Multi-source fault contributions need fault-level v1.1 first | After fault-level v1.1 |
| Lee 1982 sanity-check uppper bound enforcement (auto-cap IE ≤ Lee result) | Useful safety net but complicates the fallback chain; deferred | v1.1 if engineers report unrealistic IEEE 1584:2018 results |
| Arc-resistant equipment derate (some equipment vendors publish lower IE for their arc-resistant gear) | Vendor-specific data; not standardised | Engineer-declared override per node |

## Inputs the skill cannot derive (require engineer)

These cannot come from any upstream intent and must be declared per cascade node:

- `t_clear_s` — engineer-declared with OCPD-type default fallback (rules/t-clear-defaults.yaml)
- `working_distance_mm` — defaults from Phase A working-distance-defaults.json (455mm LV, 914mm MV); engineer override per node
- `current_type` (`ac | dc`) — auto-inferred from equipment_type pattern matching; engineer override
- `electrode_config` — auto-inferred from equipment_type; engineer override per node
- `enclosure_volume_mm3` — required for §10.5 adjustment when non-standard; defaults to typical box dimensions otherwise

If any required input is missing AND no upstream intent provides it, the generator sets `method_applied: pending` for that node and emits `ARC_FLASH_PENDING` flag.

## Phase A pending-verification coefficients

17 files in `shared/standards/electrical/IEEE1584/` are pending-verification:
- 3 method-2018-*V-coefficients files (k1..k7 per electrode config)
- 5 electrode-config-*-coefficients files
- 3 adjustment-factor-*.json files
- 1 method-2002-doughty-neal-formula.json
- (Plus 5 NFPA 70E lookup tables also pending)

The skill handles this gracefully via the method fallback chain: when 2018 coefficients are null, falls through to Lee 1982 (always available) or NFPA 70E table method. When the coefficients are eventually transcribed in a future micro-sprint, the skill auto-promotes (no code changes — fallback chain re-runs at runtime).

## Forward-compatibility caveats

- The emitted `arc-flash` intent's shock-approach fields use `oneOf [number, string]` because Table 130.4(C)(a) row 1 contains `"avoid contact"` for <50V. Downstream consumers (labelling skill) must handle both.
- PPE category 0 (IE < 1.2 cal/cm²) is recorded as Cat 1 minimum per industry convention — even though NFPA 70E doesn't strictly require AR clothing below the threshold, any energized work in practice uses Cat 1 PPE.
- DC nodes always have `electrode_config: null`. The intent schema enforces this; the labelling skill should not attempt to render electrode config for DC nodes.

## Pre-existing standards-layer tech debt

The Phase A standards layers (IEEE1584 + NFPA70E) carry `clause_ref` fields per the new convention. Pre-existing electrical standards layers (BS7671, IEC60364, IEC60909, etc.) lack `clause_ref` — known cross-cutting tech debt scheduled for a future micro-sprint. The `standards-clause-check.py` validation script is scoped to IEEE1584 + NFPA70E to avoid noise from pre-existing layers.
```

- [ ] **Step 3: Verify both files non-empty**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
for f in electrical/arc-flash/docs/*.md; do
  test -s "$f" && echo "OK $f"
done
```

Expected: 2 `OK` lines.

- [ ] **Step 4: Commit**

```bash
git add electrical/arc-flash/docs/
git commit -m "docs(arc-flash): engineering-philosophy + known-limitations"
```

---

## Task 15: `evals/runner-config.json` + eval-01 (UK happy path)

**Files (create):**
- `electrical/arc-flash/evals/runner-config.json`
- `electrical/arc-flash/evals/eval-01-uk-lv-switchboard-happy-path.yaml`

- [ ] **Step 1: runner-config.json**

```json
{
  "runner": "draftsman-eval",
  "version": "1.0.0",
  "skill": "arc-flash",
  "skill_version": "1.0.0",
  "description": "Eval runner config for electrical/arc-flash v1.0.0. Mirrors electrical/fault-level/evals/runner-config.json structure.",
  "evals": [
    "electrical/arc-flash/evals/eval-01-uk-lv-switchboard-happy-path.yaml",
    "electrical/arc-flash/evals/eval-02-mv-cascade-with-drawout.yaml",
    "electrical/arc-flash/evals/eval-03-coefficient-fallback-trap.yaml",
    "electrical/arc-flash/evals/eval-04-missing-fault-data.yaml",
    "electrical/arc-flash/evals/eval-05-jurisdiction-us-with-restricted.yaml",
    "electrical/arc-flash/evals/eval-06-rationale-block.yaml",
    "electrical/arc-flash/evals/eval-07-dc-pv-string.yaml",
    "electrical/arc-flash/evals/eval-08-conservative-t-clear-default.yaml",
    "electrical/arc-flash/evals/eval-09-shock-approach-out-of-range.yaml"
  ],
  "coverage": {
    "wi5_categories": {
      "happy_path": ["eval-01"],
      "edge_case": ["eval-02"],
      "validation_trap": ["eval-03"],
      "missing_input": ["eval-04"],
      "jurisdiction_switch": ["eval-05"],
      "rationale_block": ["eval-06"]
    },
    "skill_specific": {
      "dc_pv_string": ["eval-07"],
      "conservative_default_behaviour": ["eval-08"],
      "shock_approach_edge_case": ["eval-09"]
    }
  }
}
```

- [ ] **Step 2: eval-01-uk-lv-switchboard-happy-path.yaml**

```yaml
eval_id: eval-01-uk-lv-switchboard-happy-path
category: happy_path
skill: arc-flash
skill_version: 1.0.0
description: |
  UK commercial 400V TPN main switchboard + 1 sub-DB. Standard VCB equipment, MCCB OCPD,
  fault data from fault-level intent. IEEE 1584:2018 method fires (assuming coefficients
  transcribed); otherwise fallback chain demotes to Lee 1982. Tests baseline cascade analysis.
input:
  jurisdiction: GB
  project_supply:
    voltage_v: 400
    phases: three
    frequency_hz: 50
  consumed_intents:
    fault_level: { present: true, source: "electrical/fault-level/1.0.0" }
    db_layout_rollup: { present: true, source: "electrical/db-layout/1.0.0" }
  cascade_declared:
    - id: "MSB-1"
      parent_node_id: null
      node_kind: service_entrance
      designation: "Main MSB 2500A incomer"
      equipment: { type: "metal-clad LV switchgear", current_type: ac, voltage_v: 400 }
      fault_inputs: { ibf_ka_max: 22.5, ibf_ka_min: 20.4, x_over_r: 7 }
      ocpd_inputs: { ocpd_type: "ACB_electronic", t_clear_s: 0.3 }
      geometry: { working_distance_mm: 455 }
    - id: "MSB-1.DB-L1"
      parent_node_id: "MSB-1"
      node_kind: sub_feeder
      designation: "DB-L1 incoming"
      equipment: { type: "LV panelboard", current_type: ac, voltage_v: 400 }
      fault_inputs: { ibf_ka_max: 18.0, ibf_ka_min: 16.5, x_over_r: 5 }
      ocpd_inputs: { ocpd_type: "MCCB_thermal_magnetic", t_clear_s: 0.2 }
      geometry: { working_distance_mm: 455 }
expected:
  cascade_node_count: 2
  per_node:
    - node_id: "MSB-1"
      electrode_config: "VCB"
      electrode_config_source: "auto_inferred_from_equipment_type"
      method_applied_one_of: ["ieee1584_2018", "lee_1982"]
      shock_approach_limited_movable_mm: 3050
      shock_approach_limited_fixed_mm: 1070
      shock_approach_restricted_mm: 305
      shock_approach_source_contains: "151V to 750V"
      label_recommended: true
    - node_id: "MSB-1.DB-L1"
      electrode_config: "VCB"
      ppe_category_one_of: [1, 2, 3]
      label_recommended: true
  invariants_pass: ["INV-01","INV-02","INV-03","INV-04","INV-05","INV-08","INV-09","INV-10"]
pass_criteria:
  - "IR validates against schema"
  - "Both nodes have method_applied from controlled vocabulary"
  - "Both nodes auto-inferred to VCB electrode config"
  - "Both nodes have shock-approach distances from Table 130.4(C)(a) row 151V-750V"
  - "Both nodes label_recommended: true (LV switchgear + panelboard ≥240V)"
  - "If method_applied == lee_1982: LEE_1982_FALLBACK_USED flag present"
```

- [ ] **Step 3: Verify both files parse**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
jq . electrical/arc-flash/evals/runner-config.json > /dev/null && echo "OK runner-config"
python3 -c "import yaml; yaml.safe_load(open('electrical/arc-flash/evals/eval-01-uk-lv-switchboard-happy-path.yaml'))" && echo "OK eval-01"
```

- [ ] **Step 4: Commit**

```bash
git add electrical/arc-flash/evals/runner-config.json electrical/arc-flash/evals/eval-01-*.yaml
git commit -m "feat(arc-flash): runner-config + eval-01 UK LV switchboard happy path"
```

---

## Task 16: eval-02 (MV cascade) + eval-03 (coefficient fallback trap)

**Files (all create):**
- `electrical/arc-flash/evals/eval-02-mv-cascade-with-drawout.yaml`
- `electrical/arc-flash/evals/eval-03-coefficient-fallback-trap.yaml`

- [ ] **Step 1: eval-02-mv-cascade-with-drawout.yaml**

```yaml
eval_id: eval-02-mv-cascade-with-drawout
category: edge_case
skill: arc-flash
skill_version: 1.0.0
description: |
  11kV MV switchgear with drawout breakers (HCB electrode config) cascaded to 400V LV.
  Tests voltage-class crossing (14300V class for MV → 600V class for LV) + interleaved
  electrode configs (HCB at MV, VCB at LV). Verifies different methods/configs in one cascade.
input:
  jurisdiction: INT
  project_supply: { voltage_v: 11000, phases: three, frequency_hz: 50 }
  cascade_declared:
    - id: "MV-SWB"
      parent_node_id: null
      node_kind: service_entrance
      designation: "11 kV switchboard 1600A — drawout breakers"
      equipment: { type: "drawout switchgear", current_type: ac, voltage_v: 11000 }
      fault_inputs: { ibf_ka_max: 12, x_over_r: 15 }
      ocpd_inputs: { ocpd_type: "ACB_with_intentional_delay", t_clear_s: 0.5 }
      geometry: { working_distance_mm: 910 }
    - id: "MV-SWB.TX-1.LV-MSB"
      parent_node_id: "MV-SWB"
      node_kind: feeder
      designation: "LV MSB 3200A (downstream of 11kV/400V transformer)"
      equipment: { type: "LV switchgear", current_type: ac, voltage_v: 400 }
      fault_inputs: { ibf_ka_max: 35, x_over_r: 8 }
      ocpd_inputs: { ocpd_type: "ACB_electronic", t_clear_s: 0.3 }
      geometry: { working_distance_mm: 455 }
expected:
  per_node:
    - node_id: "MV-SWB"
      voltage_class: "14300V"
      electrode_config: "HCB"
      electrode_config_source: "auto_inferred_from_equipment_type"
      shock_approach_source_contains: "751V to 15 kV"
      shock_approach_restricted_mm: 660
    - node_id: "MV-SWB.TX-1.LV-MSB"
      voltage_class: "600V"
      electrode_config: "VCB"
      shock_approach_source_contains: "151V to 750V"
pass_criteria:
  - "Two voltage classes resolved correctly (14300V + 600V)"
  - "Drawout switchgear inferred to HCB; LV switchgear to VCB"
  - "Each node gets shock-approach from correct voltage row"
  - "Cascade tree consistent (parent_node_id resolves)"
```

- [ ] **Step 2: eval-03-coefficient-fallback-trap.yaml**

```yaml
eval_id: eval-03-coefficient-fallback-trap
category: validation_trap
skill: arc-flash
skill_version: 1.0.0
description: |
  IEEE 1584:2018 coefficients are null (pending-verification) for one or more (voltage_class,
  electrode_config) pairs. Skill MUST fall back to Lee 1982 (or NFPA 70E table) AND record
  the trail AND emit the LEE_1982_FALLBACK_USED flag. Verifies the fallback chain doesn't
  silently fail with null IE.
input:
  jurisdiction: US
  project_supply: { voltage_v: 480, phases: three, frequency_hz: 60 }
  simulated_environment:
    ieee1584_2018_coefficients_available: false
    ieee1584_2002_coefficients_available: false
  cascade_declared:
    - id: "PNL-A1"
      parent_node_id: null
      node_kind: final_circuit
      designation: "480V panelboard PNL-A1"
      equipment: { type: "LV panelboard", current_type: ac, voltage_v: 480 }
      fault_inputs: { ibf_ka_max: 30 }
      ocpd_inputs: { ocpd_type: "MCCB_thermal_magnetic", t_clear_s: 0.2 }
      geometry: { working_distance_mm: 455 }
expected:
  per_node:
    - node_id: "PNL-A1"
      method_applied: "lee_1982"
      method_fallback_trail_length_min: 3
      method_fallback_trail_must_contain:
        - method: "ieee1584_2018"
          result: "skipped"
        - method: "ieee1584_2002"
          result: "skipped"
        - method: "lee_1982"
          result: "applied"
      incident_energy_cal_per_cm2_gt: 1.0
      arc_flash_boundary_mm_gt: 455
  non_compliance_flags_must_include:
    - code: "LEE_1982_FALLBACK_USED"
      severity: "info"
pass_criteria:
  - "method_applied = lee_1982 (not pending — fallback chain works)"
  - "method_fallback_trail records all skipped attempts with reasons"
  - "LEE_1982_FALLBACK_USED flag emitted with info severity"
  - "Lee 1982 produces a numeric IE (conservative upper bound)"
  - "No silent failure — engineer sees the fallback chain"
```

- [ ] **Step 3: Verify both YAMLs parse**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
for f in electrical/arc-flash/evals/eval-0{2,3}-*.yaml; do
  python3 -c "import yaml; yaml.safe_load(open('$f'))" && echo "OK $f"
done
```

- [ ] **Step 4: Commit**

```bash
git add electrical/arc-flash/evals/eval-02-*.yaml electrical/arc-flash/evals/eval-03-*.yaml
git commit -m "feat(arc-flash): eval-02 MV cascade + eval-03 coefficient fallback trap"
```

---

## Task 17: eval-04 (missing fault data) + eval-05 (US restricted IE>40)

**Files (all create):**
- `electrical/arc-flash/evals/eval-04-missing-fault-data.yaml`
- `electrical/arc-flash/evals/eval-05-jurisdiction-us-with-restricted.yaml`

- [ ] **Step 1: eval-04-missing-fault-data.yaml**

```yaml
eval_id: eval-04-missing-fault-data
category: missing_input
skill: arc-flash
skill_version: 1.0.0
description: |
  No fault-level intent + no engineer-declared per-node Ibf. Skill must NOT invent
  fault current — emits method_applied: pending + ARC_FLASH_PENDING flag + logs assumption.
input:
  jurisdiction: GB
  project_supply: { voltage_v: 400, phases: three, frequency_hz: 50 }
  consumed_intents:
    fault_level: { present: false }
  cascade_declared:
    - id: "DB-X1"
      parent_node_id: null
      node_kind: final_circuit
      designation: "Panel DB-X1 — fault data missing"
      equipment: { type: "LV panelboard", current_type: ac, voltage_v: 400 }
      fault_inputs: {}  # deliberately empty
      ocpd_inputs: { ocpd_type: "MCCB_thermal_magnetic", t_clear_s: 0.2 }
      geometry: { working_distance_mm: 455 }
expected:
  per_node:
    - node_id: "DB-X1"
      method_applied: "pending"
      checks_tool_call_pending: true
      incident_energy_cal_per_cm2: null
      arc_flash_boundary_mm: null
      ppe_category: null
  compliance_summary:
    assumptions_must_contain_text:
      - "calc.arc_flash_incident_energy"
      - "ibf_ka_max missing"
  non_compliance_flags_must_include:
    - code: "ARC_FLASH_PENDING"
      severity: "warning"
pass_criteria:
  - "No invented Ibf; method_applied = pending"
  - "Numeric outputs are null"
  - "ARC_FLASH_PENDING flag emitted"
  - "Assumption explicitly names the missing input"
  - "Shock-approach still computed (doesn't depend on fault data) + label_recommended still set"
```

- [ ] **Step 2: eval-05-jurisdiction-us-with-restricted.yaml**

```yaml
eval_id: eval-05-jurisdiction-us-with-restricted
category: jurisdiction_switch
skill: arc-flash
skill_version: 1.0.0
description: |
  US industrial cascade with one node having very high fault current + slow OCPD → IE > 40
  cal/cm². Skill emits INCIDENT_ENERGY_GT_40_RESTRICTED error + ppe_category: null. Tests
  the restricted-equipment path.
input:
  jurisdiction: US
  project_supply: { voltage_v: 480, phases: three, frequency_hz: 60 }
  cascade_declared:
    - id: "MSB-RESTRICTED"
      parent_node_id: null
      node_kind: service_entrance
      designation: "480V service entrance — high fault current + slow ACB"
      equipment: { type: "metal-clad switchgear", current_type: ac, voltage_v: 480 }
      fault_inputs: { ibf_ka_max: 65, x_over_r: 10 }
      ocpd_inputs: { ocpd_type: "ACB_with_intentional_delay", t_clear_s: 0.5 }
      geometry: { working_distance_mm: 455 }
expected:
  per_node:
    - node_id: "MSB-RESTRICTED"
      incident_energy_cal_per_cm2_gt: 40
      ppe_category: null
  non_compliance_flags_must_include:
    - code: "INCIDENT_ENERGY_GT_40_RESTRICTED"
      severity: "error"
      message_contains: "specialised teams"
pass_criteria:
  - "IE > 40 cal/cm² computed"
  - "ppe_category set to null (no Cat 5 in NFPA 70E)"
  - "INCIDENT_ENERGY_GT_40_RESTRICTED flag at error severity"
  - "Flag message recommends specialised-team handling"
  - "shock_approach still populated (separate concern)"
```

- [ ] **Step 3: Verify + Commit**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
for f in electrical/arc-flash/evals/eval-0{4,5}-*.yaml; do
  python3 -c "import yaml; yaml.safe_load(open('$f'))" && echo "OK $f"
done
git add electrical/arc-flash/evals/eval-04-*.yaml electrical/arc-flash/evals/eval-05-*.yaml
git commit -m "feat(arc-flash): eval-04 missing fault data + eval-05 US restricted IE>40"
```

---

## Task 18: eval-06 (rationale block) + eval-07 (DC PV string)

**Files (all create):**
- `electrical/arc-flash/evals/eval-06-rationale-block.yaml`
- `electrical/arc-flash/evals/eval-07-dc-pv-string.yaml`

- [ ] **Step 1: eval-06-rationale-block.yaml**

```yaml
eval_id: eval-06-rationale-block
category: rationale_block
skill: arc-flash
skill_version: 1.0.0
description: |
  Verify the rationale block conforms to WI2: exactly 8 sections + chat_summary + every
  decision cites a rule + clause. Reuses eval-01 scenario.
input:
  reuse_from: "electrical/arc-flash/evals/eval-01-uk-lv-switchboard-happy-path.yaml"
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
        - "Jurisdictional Framing"
        - "Method Selection Summary"
        - "Per-node Arc-Flash Results"
        - "Shock-Approach Boundaries"
        - "Label Recommendations"
        - "Compliance + Assumptions + Tool-call Status"
      every_decision_has: [label, summary, rule, code_clause]
pass_criteria:
  - "rationale.sections.length == 8 exactly"
  - "Every section is non-empty (or explicitly says 'none triggered')"
  - "Every decision cites a rule + clause from IEEE 1584 or NFPA 70E"
  - "chat_summary ≤ 200 words"
```

- [ ] **Step 2: eval-07-dc-pv-string.yaml**

```yaml
eval_id: eval-07-dc-pv-string
category: skill_specific
subcategory: dc_pv_string
skill: arc-flash
skill_version: 1.0.0
description: |
  600V DC PV string with combiner box. current_type auto-inferred to dc from equipment_type.
  dc_doan method fires. shock-approach from Table 130.4(C)(b) DC row. electrode_config null.
input:
  jurisdiction: US
  project_supply: { voltage_v: 480, phases: three, frequency_hz: 60 }  # project-wide AC supply
  cascade_declared:
    - id: "PV-INV-1"
      parent_node_id: null
      node_kind: feeder
      designation: "100kW PV inverter (AC side)"
      equipment: { type: "LV switchgear", current_type: ac, voltage_v: 480 }
      fault_inputs: { ibf_ka_max: 20 }
      ocpd_inputs: { ocpd_type: "MCCB_electronic_LSI", t_clear_s: 0.1 }
      geometry: { working_distance_mm: 455 }
    - id: "PV-INV-1.DC-STR-1"
      parent_node_id: "PV-INV-1"
      node_kind: final_circuit
      designation: "PV string 600V DC combiner box"
      equipment: { type: "PV combiner box", current_type: dc, voltage_v: 600 }
      fault_inputs: { ibf_ka_max: 0.5 }  # PV is current-limited
      ocpd_inputs: { ocpd_type: "fuse_LV_general_purpose", t_clear_s: 0.2 }
      geometry: { working_distance_mm: 455 }
expected:
  per_node:
    - node_id: "PV-INV-1"
      equipment_current_type: "ac"
      method_applied_one_of: ["ieee1584_2018", "lee_1982"]
      shock_approach_source_contains: "Table 130.4(C)(a)"
    - node_id: "PV-INV-1.DC-STR-1"
      equipment_current_type: "dc"
      equipment_electrode_config: null
      method_applied: "dc_doan"
      shock_approach_source_contains: "Table 130.4(C)(b)"
      shock_approach_source_contains_voltage_range: "301V to 1 kV"
pass_criteria:
  - "DC node auto-inferred current_type = dc from 'PV combiner box' equipment_type"
  - "DC node has electrode_config: null"
  - "DC node method_applied = dc_doan (NOT IEEE 1584)"
  - "DC node shock-approach from Table 130.4(C)(b), not (a)"
  - "AC node retains IEEE 1584 path"
  - "Unified cascade tree with parent_node_id linking inverter to string"
```

- [ ] **Step 3: Verify + Commit**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
for f in electrical/arc-flash/evals/eval-0{6,7}-*.yaml; do
  python3 -c "import yaml; yaml.safe_load(open('$f'))" && echo "OK $f"
done
git add electrical/arc-flash/evals/eval-06-*.yaml electrical/arc-flash/evals/eval-07-*.yaml
git commit -m "feat(arc-flash): eval-06 rationale block + eval-07 DC PV string"
```

---

## Task 19: eval-08 (conservative t_clear) + eval-09 (shock-approach OOR)

**Files (all create):**
- `electrical/arc-flash/evals/eval-08-conservative-t-clear-default.yaml`
- `electrical/arc-flash/evals/eval-09-shock-approach-out-of-range.yaml`

- [ ] **Step 1: eval-08-conservative-t-clear-default.yaml**

```yaml
eval_id: eval-08-conservative-t-clear-default
category: skill_specific
subcategory: conservative_default_behaviour
skill: arc-flash
skill_version: 1.0.0
description: |
  No engineer-declared t_clear + no ocpd_type from db-layout-rollup. Conservative 2.0s
  default kicks in. Skill emits CONSERVATIVE_T_CLEAR_DEFAULT_USED warning + still produces
  useful IE numbers (just high).
input:
  jurisdiction: GB
  project_supply: { voltage_v: 400, phases: three, frequency_hz: 50 }
  cascade_declared:
    - id: "DB-NO-OCPD-INFO"
      parent_node_id: null
      node_kind: final_circuit
      designation: "Panel with no OCPD curve data"
      equipment: { type: "LV panelboard", current_type: ac, voltage_v: 400 }
      fault_inputs: { ibf_ka_max: 15 }
      ocpd_inputs: {}  # no ocpd_type, no t_clear_s
      geometry: { working_distance_mm: 455 }
expected:
  per_node:
    - node_id: "DB-NO-OCPD-INFO"
      ocpd_inputs_t_clear_s: 2.0
      ocpd_inputs_t_clear_source: "conservative_default"
  non_compliance_flags_must_include:
    - code: "CONSERVATIVE_T_CLEAR_DEFAULT_USED"
      severity: "warning"
      message_contains: "Refine via protection coordination"
pass_criteria:
  - "t_clear_s = 2.0 (conservative default)"
  - "t_clear_source = conservative_default"
  - "CONSERVATIVE_T_CLEAR_DEFAULT_USED flag emitted at warning severity"
  - "IE still computed (just high due to long arcing time)"
  - "PPE category likely 3 or 4 due to high IE"
```

- [ ] **Step 2: eval-09-shock-approach-out-of-range.yaml**

```yaml
eval_id: eval-09-shock-approach-out-of-range
category: skill_specific
subcategory: shock_approach_edge_case
skill: arc-flash
skill_version: 1.0.0
description: |
  Voltage at 36 kV (in-range — last row of Table 130.4(C)(a)) vs 47 kV (out-of-range —
  beyond 46 kV row). Verifies edge-case handling.
input:
  jurisdiction: US
  project_supply: { voltage_v: 36000, phases: three, frequency_hz: 60 }
  cascade_declared:
    - id: "MV-36KV"
      parent_node_id: null
      node_kind: service_entrance
      designation: "36 kV substation — within table range"
      equipment: { type: "MV switchgear", current_type: ac, voltage_v: 36000 }
      fault_inputs: { ibf_ka_max: 25 }
      ocpd_inputs: { ocpd_type: "ACB_with_intentional_delay", t_clear_s: 0.5 }
      geometry: { working_distance_mm: 914 }
    - id: "MV-47KV"
      parent_node_id: null
      node_kind: service_entrance
      designation: "47 kV substation — out-of-range"
      equipment: { type: "MV switchgear", current_type: ac, voltage_v: 47000 }
      fault_inputs: { ibf_ka_max: 25 }
      ocpd_inputs: { ocpd_type: "ACB_with_intentional_delay", t_clear_s: 0.5 }
      geometry: { working_distance_mm: 914 }
expected:
  per_node:
    - node_id: "MV-36KV"
      shock_approach_source_contains: "15.1 kV to 36 kV"
      shock_approach_restricted_mm_one_of: [790, 840]
    - node_id: "MV-47KV"
      shock_approach_source_contains: "out_of_table_range"
  non_compliance_flags_must_include:
    - code: "SHOCK_APPROACH_BEYOND_TABLE_RANGE"
      severity: "error"
      node_id: "MV-47KV"
pass_criteria:
  - "36 kV node matches Table 130.4(C)(a) row '15.1 kV to 36 kV' or '36.1 kV to 46 kV'"
  - "47 kV node triggers SHOCK_APPROACH_BEYOND_TABLE_RANGE error"
  - "Skill doesn't silently extrapolate beyond table range"
  - "Engineer must supply approach distances manually for >46 kV"
```

- [ ] **Step 3: Verify + Commit**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
for f in electrical/arc-flash/evals/eval-0{8,9}-*.yaml; do
  python3 -c "import yaml; yaml.safe_load(open('$f'))" && echo "OK $f"
done
git add electrical/arc-flash/evals/eval-08-*.yaml electrical/arc-flash/evals/eval-09-*.yaml
git commit -m "feat(arc-flash): eval-08 conservative t_clear + eval-09 shock-approach out-of-range"
```

---

## Task 20: Example 1 — UK LV switchgear

**Files (all create):**
- `electrical/arc-flash/examples/uk-lv-switchgear/input.json`
- `electrical/arc-flash/examples/uk-lv-switchgear/output.json`
- `electrical/arc-flash/examples/uk-lv-switchgear/intent-out.json`
- `electrical/arc-flash/examples/uk-lv-switchgear/reasoning.md`

- [ ] **Step 1: input.json**

```json
{
  "project_id": "uk-lv-af-eg01",
  "jurisdiction": "GB",
  "project_supply": { "voltage_v": 400, "phases": "three", "frequency_hz": 50 },
  "consumed_intents_present": ["fault-level", "db-layout-rollup"],
  "cascade_declared": [
    {
      "id": "MSB-1",
      "parent_node_id": null,
      "node_kind": "service_entrance",
      "designation": "Main switchboard 2500A incomer",
      "equipment": { "type": "metal-clad LV switchgear", "current_type": "ac", "voltage_v": 400 },
      "fault_inputs": { "ibf_ka_max": 22.5, "ibf_ka_min": 20.4, "x_over_r": 7 },
      "ocpd_inputs": { "ocpd_type": "ACB_electronic", "t_clear_s": 0.3 },
      "geometry": { "working_distance_mm": 455, "gap_distance_mm": 32 }
    },
    {
      "id": "MSB-1.DB-L1",
      "parent_node_id": "MSB-1",
      "node_kind": "sub_feeder",
      "designation": "DB-L1 incoming sub-feeder 200A",
      "equipment": { "type": "LV panelboard", "current_type": "ac", "voltage_v": 400 },
      "fault_inputs": { "ibf_ka_max": 18.0, "ibf_ka_min": 16.5, "x_over_r": 5 },
      "ocpd_inputs": { "ocpd_type": "MCCB_thermal_magnetic", "t_clear_s": 0.2 },
      "geometry": { "working_distance_mm": 455, "gap_distance_mm": 32 }
    }
  ]
}
```

- [ ] **Step 2: output.json (full IR — using Lee 1982 fallback since IEEE 1584:2018 coefficients pending)**

```json
{
  "drawing_type": "arc_flash_study",
  "version": "1.0.0",
  "meta": {
    "project_id": "uk-lv-af-eg01",
    "skill_version": "arc-flash/1.0.0",
    "produced_at": "2026-05-17T12:00:00Z",
    "consumed_intents": [
      {"intent_type": "fault-level", "intent_version": "1.0.0", "produced_by": "electrical/fault-level/1.0.0"},
      {"intent_type": "db-layout-rollup", "intent_version": "1.0.0", "produced_by": "electrical/db-layout/1.0.0"}
    ]
  },
  "jurisdiction": "GB",
  "project_supply": { "voltage_v": 400, "phases": "three", "frequency_hz": 50 },
  "cascade": [
    {
      "node_id": "MSB-1",
      "parent_node_id": null,
      "node_kind": "service_entrance",
      "designation": "Main switchboard 2500A incomer",
      "equipment": {
        "type": "metal-clad LV switchgear",
        "current_type": "ac",
        "voltage_v": 400,
        "voltage_class": "600V",
        "electrode_config": "VCB",
        "electrode_config_source": "auto_inferred_from_equipment_type"
      },
      "fault_inputs": { "ibf_ka_max": 22.5, "ibf_ka_min": 20.4, "x_over_r": 7, "z_total_ohm": 0.0103 },
      "ocpd_inputs": { "ocpd_type": "ACB_electronic", "t_clear_s": 0.3, "t_clear_source": "engineer_declared" },
      "geometry": { "working_distance_mm": 455, "gap_distance_mm": 32 },
      "arc_flash": {
        "method_applied": "lee_1982",
        "method_fallback_trail": [
          {"method": "ieee1584_2018", "result": "skipped", "reason": "coefficients pending-verification for VCB 600V (k1-k7 null)"},
          {"method": "ieee1584_2002", "result": "skipped", "reason": "Doughty/Neal coefficients pending-verification"},
          {"method": "lee_1982", "result": "applied", "reason": "theoretical formula always available; V_nom 400V within 50-15000V range"}
        ],
        "arcing_current_a": 19500,
        "incident_energy_cal_per_cm2": 9.8,
        "arc_flash_boundary_mm": 1650,
        "ppe_category": 3,
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
        "label_required_per": "NFPA 70E:2024 §130.5(H) — metal-clad LV switchgear ≥240V (UK: voluntary best practice per HSG48)",
        "engineer_can_skip_with_reason": false
      },
      "checks": {
        "incident_energy_finite": true,
        "boundary_ge_working_distance": true,
        "ppe_category_consistent_with_E": true,
        "method_fallback_consistent": true,
        "tool_call_pending": true
      }
    },
    {
      "node_id": "MSB-1.DB-L1",
      "parent_node_id": "MSB-1",
      "node_kind": "sub_feeder",
      "designation": "DB-L1 incoming sub-feeder 200A",
      "equipment": {
        "type": "LV panelboard",
        "current_type": "ac",
        "voltage_v": 400,
        "voltage_class": "600V",
        "electrode_config": "VCB",
        "electrode_config_source": "auto_inferred_from_equipment_type"
      },
      "fault_inputs": { "ibf_ka_max": 18.0, "ibf_ka_min": 16.5, "x_over_r": 5 },
      "ocpd_inputs": { "ocpd_type": "MCCB_thermal_magnetic", "t_clear_s": 0.2, "t_clear_source": "engineer_declared" },
      "geometry": { "working_distance_mm": 455, "gap_distance_mm": 32 },
      "arc_flash": {
        "method_applied": "lee_1982",
        "method_fallback_trail": [
          {"method": "ieee1584_2018", "result": "skipped", "reason": "coefficients pending-verification for VCB 600V"},
          {"method": "ieee1584_2002", "result": "skipped", "reason": "Doughty/Neal coefficients pending-verification"},
          {"method": "lee_1982", "result": "applied", "reason": "theoretical formula always available"}
        ],
        "arcing_current_a": 15800,
        "incident_energy_cal_per_cm2": 5.2,
        "arc_flash_boundary_mm": 1050,
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
        "label_required_per": "NFPA 70E:2024 §130.5(H) — LV panelboard ≥240V (UK: voluntary best practice)",
        "engineer_can_skip_with_reason": false
      },
      "checks": {
        "incident_energy_finite": true,
        "boundary_ge_working_distance": true,
        "ppe_category_consistent_with_E": true,
        "method_fallback_consistent": true,
        "tool_call_pending": true
      }
    }
  ],
  "compliance_summary": {
    "compliant": true,
    "non_compliance_flags": [
      { "code": "LEE_1982_FALLBACK_USED", "message": "Both cascade nodes fell back to Lee 1982 (conservative upper bound). Transcribe IEEE 1584:2018 Table 4 coefficients for VCB 600V class to get realistic IE values.", "severity": "info" }
    ],
    "assumptions": [
      "fault-level intent consumed; per-node Ibf + X/R from it",
      "db-layout-rollup intent consumed; equipment_type + ocpd_type from it; electrode_config auto-inferred to VCB for both nodes",
      "t_clear_s engineer-declared (0.3s for ACB at MSB; 0.2s for MCCB at DB)",
      "IE values are Lee 1982 conservative upper bounds — actual IE per IEEE 1584:2018 will be 2-5× lower when coefficients are transcribed",
      "tool_call_pending: true on both nodes — calc.arc_flash_incident_energy contract shipped but runtime tool not yet implemented"
    ]
  },
  "flags": ["TOOL-CALL-PENDING", "LEE_1982_FALLBACK_USED"],
  "rationale": {
    "chat_summary": "UK 400V TPN commercial: 2-node cascade (MSB → DB-L1). IEEE 1584:2018 coefficients pending-verification → fell back to Lee 1982 theoretical (conservative upper bound). MSB IE ≈ 9.8 cal/cm² → Cat 3; DB-L1 IE ≈ 5.2 → Cat 2. Both nodes auto-inferred to VCB. Shock-approach distances from Table 130.4(C)(a) 151V-750V row. Labels recommended (UK best practice). tool_call_pending across cascade.",
    "sections": [
      { "title": "Input Ingestion", "summary": "Both intents consumed; engineer declared t_clear per node.", "decisions": [] },
      { "title": "Cascade Topology", "summary": "2-node depth-2 cascade: service_entrance → sub_feeder. All AC.", "decisions": [] },
      { "title": "Jurisdictional Framing", "summary": "GB — voluntary best practice per HSG48 + IET CoP. Labels recommended, not statutory.", "decisions": [{ "label": "GB jurisdiction applied", "summary": "HSG48 + IET CoP best practice", "rule": "HSG48 + IET Code of Practice for In-Service Inspection", "code_clause": "HSG48 §3.2" }] },
      { "title": "Method Selection Summary", "summary": "Both nodes fell back through IEEE 1584:2018 (skipped — coefficients pending) → IEEE 1584:2002 (skipped — pending) → Lee 1982 (applied). LEE_1982_FALLBACK_USED flag emitted info severity.", "decisions": [
        { "label": "Lee 1982 fallback both nodes", "summary": "IEEE 1584:2018 + 2002 coefficients null. Lee theoretical applied as conservative upper bound.", "rule": "rules/method-fallback-chain.yaml", "code_clause": "Lee 1982 (cited by IEEE 1584:2018 §2 + IEEE 1584:2002 Annex B)" }
      ] },
      { "title": "Per-node Arc-Flash Results", "summary": "MSB: IE 9.8 → Cat 3 / AFB 1650mm. DB-L1: IE 5.2 → Cat 2 / AFB 1050mm.", "decisions": [
        { "label": "MSB Cat 3", "summary": "IE 9.8 cal/cm² in 8-25 range", "rule": "NFPA 70E:2024 Table 130.7(C)(15)(c)", "code_clause": "NFPA 70E:2024 Table 130.7(C)(15)(c)", "inputs": { "ie": 9.8, "category": 3 } },
        { "label": "DB-L1 Cat 2", "summary": "IE 5.2 cal/cm² in 4-8 range", "rule": "NFPA 70E:2024 Table 130.7(C)(15)(c)", "code_clause": "NFPA 70E:2024 Table 130.7(C)(15)(c)", "inputs": { "ie": 5.2, "category": 2 } }
      ] },
      { "title": "Shock-Approach Boundaries", "summary": "Both nodes: 400V → Table 130.4(C)(a) row '151V to 750V'. Limited movable 3050mm, fixed 1070mm; restricted 305mm.", "decisions": [] },
      { "title": "Label Recommendations", "summary": "Both nodes label_recommended: true. UK regulatory context: HSG48 + IET CoP best practice (voluntary, not statutory like US NFPA 70E §130.5(H)).", "decisions": [] },
      { "title": "Compliance + Assumptions + Tool-call Status", "summary": "Compliant. Lee fallback flagged info-severity. tool_call_pending on both nodes. IE will be re-computed (lower) when IEEE 1584:2018 coefficients transcribed.", "decisions": [] }
    ]
  }
}
```

- [ ] **Step 3: intent-out.json**

```json
{
  "intent_kind": "arc-flash",
  "version": "1.0.0",
  "produced_by_skill_version": "arc-flash/1.0.0",
  "tool_call_pending": true,
  "nodes": [
    {
      "node_id": "MSB-1",
      "parent_node_id": null,
      "designation": "Main switchboard 2500A incomer",
      "equipment_type": "metal-clad LV switchgear",
      "current_type": "ac",
      "voltage_v": 400,
      "incident_energy_cal_per_cm2": 9.8,
      "arc_flash_boundary_mm": 1650,
      "working_distance_mm": 455,
      "limited_approach_movable_mm": 3050,
      "limited_approach_fixed_mm": 1070,
      "restricted_approach_mm": 305,
      "ppe_category": 3,
      "method_applied": "lee_1982",
      "label_recommended": true,
      "label_required_per": "NFPA 70E:2024 §130.5(H)",
      "produced_at": "2026-05-17"
    },
    {
      "node_id": "MSB-1.DB-L1",
      "parent_node_id": "MSB-1",
      "designation": "DB-L1 incoming sub-feeder 200A",
      "equipment_type": "LV panelboard",
      "current_type": "ac",
      "voltage_v": 400,
      "incident_energy_cal_per_cm2": 5.2,
      "arc_flash_boundary_mm": 1050,
      "working_distance_mm": 455,
      "limited_approach_movable_mm": 3050,
      "limited_approach_fixed_mm": 1070,
      "restricted_approach_mm": 305,
      "ppe_category": 2,
      "method_applied": "lee_1982",
      "label_recommended": true,
      "label_required_per": "NFPA 70E:2024 §130.5(H)",
      "produced_at": "2026-05-17"
    }
  ]
}
```

- [ ] **Step 4: reasoning.md**

```markdown
# UK LV Switchgear — Worked Example

## Scenario

UK 400V TPN commercial office building. Two-node cascade:
- `MSB-1`: Main switchboard 2500A with ACB (t_clear 0.3s)
- `MSB-1.DB-L1`: DB-L1 sub-feeder 200A with MCCB (t_clear 0.2s)

Both consumed from fault-level + db-layout-rollup intents.

## Why both nodes fell back to Lee 1982

IEEE 1584:2018 Annex C Table 4 coefficients for VCB 600V class are currently pending-verification (null in Phase A). The fallback chain:

1. **ieee1584_2018**: SKIPPED — coefficients pending-verification
2. **ieee1584_2002**: SKIPPED — Doughty/Neal coefficients also pending-verification
3. **lee_1982**: APPLIED — theoretical formula always available; V_nom 400V within 50-15000V range

`LEE_1982_FALLBACK_USED` info-severity flag emitted. Lee 1982 gives a **conservative upper bound** — actual IE per IEEE 1584:2018 will likely be 2-5× lower when coefficients are transcribed.

## Per-node results

### MSB-1
- Lee 1982 formula: `E = 5.12 × 10⁵ × V × I_bf × t / D²`
- V = 0.4 kV, I_bf = 22.5 kA, t = 0.3 s, D = 18 inches (455 mm)
- E ≈ 9.8 cal/cm² → **PPE Category 3**
- AFB = 1650 mm (where E drops to 1.2 cal/cm²)
- Shock-approach from Table 130.4(C)(a) row 151V-750V

### MSB-1.DB-L1
- V = 0.4 kV, I_bf = 18 kA, t = 0.2 s
- E ≈ 5.2 cal/cm² → **PPE Category 2**
- AFB = 1050 mm
- Same shock-approach row (same voltage class)

## Electrode-config auto-inference

Both nodes auto-inferred to VCB:
- "metal-clad LV switchgear" → VCB pattern match
- "LV panelboard" → VCB pattern match

Engineer override not needed.

## Label recommendations

Both nodes `label_recommended: true`:
- LV switchgear ≥240V → NFPA 70E §130.5(H) — even in GB, this is best practice per HSG48
- LV panelboard ≥240V → same

Labels would carry: nominal voltage (400V), incident energy at 455mm (cal/cm² value), arc-flash boundary (mm), required PPE category, date of analysis.

## What changes when IEEE 1584:2018 coefficients ship

When the coefficient transcription micro-sprint completes:
- `method_applied` auto-promotes from `lee_1982` → `ieee1584_2018`
- IE values drop by 2-5× (more realistic empirical values)
- PPE category may drop one level (e.g., MSB Cat 3 → Cat 2)
- AFB shrinks accordingly
- No skill code changes — fallback chain re-runs at runtime

This is the clean separation that came from doing Phase A and Phase B in separate sprints.

## tool_call_pending status

Both nodes carry `tool_call_pending: true`. The numeric values in `arc_flash` are senior-engineer estimates from the Lee 1982 formula — runtime tool will recompute when DraftsMan runtime ships.
```

- [ ] **Step 5: Validate against schema + Commit**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
python3 -c "
import json, jsonschema
s = json.load(open('electrical/arc-flash/schemas/arc-flash-ir.schema.json'))
d = json.load(open('electrical/arc-flash/examples/uk-lv-switchgear/output.json'))
jsonschema.validate(d, s); print('IR OK')
s2 = json.load(open('electrical/arc-flash/schemas/arc-flash-intent.schema.json'))
d2 = json.load(open('electrical/arc-flash/examples/uk-lv-switchgear/intent-out.json'))
jsonschema.validate(d2, s2); print('Intent OK')
"
git add electrical/arc-flash/examples/uk-lv-switchgear/
git commit -m "feat(arc-flash): example 1 — UK LV switchgear with Lee 1982 fallback"
```

---

## Task 21: Example 2 — INT MV substation

**Files (all create):**
- `electrical/arc-flash/examples/intl-mv-substation/input.json`
- `electrical/arc-flash/examples/intl-mv-substation/output.json`
- `electrical/arc-flash/examples/intl-mv-substation/intent-out.json`
- `electrical/arc-flash/examples/intl-mv-substation/reasoning.md`

Follow the same template as Task 20 but for an international industrial 11kV → 400V substation with HCB (drawout breakers) at MV + VCB at LV. Cascade:

```
MV-SWB (11kV, HCB, ACB delayed) → MV-SWB.TX-1.LV-MSB (400V, VCB, ACB electronic)
```

- [ ] **Step 1: input.json**

```json
{
  "project_id": "intl-mv-af-eg02",
  "jurisdiction": "INT",
  "project_supply": { "voltage_v": 11000, "phases": "three", "frequency_hz": 50 },
  "consumed_intents_present": ["fault-level", "db-layout-rollup"],
  "cascade_declared": [
    {
      "id": "MV-SWB",
      "parent_node_id": null,
      "node_kind": "service_entrance",
      "designation": "11 kV main switchboard 1600A — drawout breakers",
      "equipment": { "type": "drawout switchgear", "current_type": "ac", "voltage_v": 11000 },
      "fault_inputs": { "ibf_ka_max": 12, "ibf_ka_min": 11, "x_over_r": 15 },
      "ocpd_inputs": { "ocpd_type": "ACB_with_intentional_delay", "t_clear_s": 0.5 },
      "geometry": { "working_distance_mm": 910, "gap_distance_mm": 76 }
    },
    {
      "id": "MV-SWB.TX-1.LV-MSB",
      "parent_node_id": "MV-SWB",
      "node_kind": "feeder",
      "designation": "LV MSB 3200A (downstream of 11kV/400V 2MVA TX)",
      "equipment": { "type": "LV switchgear", "current_type": "ac", "voltage_v": 400 },
      "fault_inputs": { "ibf_ka_max": 35, "ibf_ka_min": 32, "x_over_r": 8 },
      "ocpd_inputs": { "ocpd_type": "ACB_electronic", "t_clear_s": 0.3 },
      "geometry": { "working_distance_mm": 455, "gap_distance_mm": 32 }
    }
  ]
}
```

- [ ] **Step 2: output.json** — produce IR with:
  - MV-SWB: voltage_class "14300V", electrode_config "HCB" (auto-inferred from "drawout switchgear"), method lee_1982 fallback (IEEE 1584 coefficients pending), IE ≈ 14 cal/cm² (Cat 3), AFB ≈ 2200mm, shock-approach from row "751V to 15 kV"
  - LV-MSB: voltage_class "600V", electrode_config "VCB" (auto-inferred), method lee_1982 fallback, IE ≈ 8.5 cal/cm² (Cat 3), AFB ≈ 1300mm, shock-approach from row "151V to 750V"
  - Both nodes carry tool_call_pending: true + LEE_1982_FALLBACK_USED flag
  - Rationale block: 8 sections; chat_summary describes the voltage-class crossing

- [ ] **Step 3: intent-out.json** — slim downstream subset matching the IR's 2 nodes.

- [ ] **Step 4: reasoning.md** — narrative explaining the voltage-class crossing (14300V at MV → 600V at LV), why HCB vs VCB on each node, how the cascade tree threading works for a TX-mediated cascade.

- [ ] **Step 5: Validate + Commit**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
python3 -c "
import json, jsonschema
s = json.load(open('electrical/arc-flash/schemas/arc-flash-ir.schema.json'))
d = json.load(open('electrical/arc-flash/examples/intl-mv-substation/output.json'))
jsonschema.validate(d, s); print('IR OK')
s2 = json.load(open('electrical/arc-flash/schemas/arc-flash-intent.schema.json'))
d2 = json.load(open('electrical/arc-flash/examples/intl-mv-substation/intent-out.json'))
jsonschema.validate(d2, s2); print('Intent OK')
"
git add electrical/arc-flash/examples/intl-mv-substation/
git commit -m "feat(arc-flash): example 2 — INT 11kV/400V MV+LV cascade with HCB drawout + VCB"
```

---

## Task 22: Example 3 — US PV + DCFC

**Files (all create):**
- `electrical/arc-flash/examples/us-pv-with-dcfc/input.json`
- `electrical/arc-flash/examples/us-pv-with-dcfc/output.json`
- `electrical/arc-flash/examples/us-pv-with-dcfc/intent-out.json`
- `electrical/arc-flash/examples/us-pv-with-dcfc/reasoning.md`

Demonstrates unified AC + DC cascade with `current_type` tag. Cascade:

```
SERVICE-480V (AC, VCB, ACB) → SERVICE-480V.PV-INV-1 (AC, VCB, MCCB) → PV-INV-1.DC-STR-1 (DC, dc_doan)
                            → SERVICE-480V.DCFC-1 (AC inverter portion, VCB, MCCB) → DCFC-1.DC-OUT (DC, dc_doan)
```

- [ ] **Step 1: input.json** — 480V US service + 100kW PV inverter + 50kW DCFC; 2 DC nodes (PV combiner 600V DC + DCFC output 500V DC).

- [ ] **Step 2: output.json** — IR with:
  - Service entrance (AC, VCB): lee_1982 fallback, IE ≈ 12 cal/cm² (Cat 3), shock Table 130.4(C)(a) row 151-750V
  - PV inverter AC side (AC, VCB): lee_1982 fallback, IE ≈ 7 cal/cm² (Cat 2)
  - PV combiner DC side (DC, electrode_config: null): dc_doan method, low fault current (PV is current-limited 0.5 kA), IE ≈ 2 cal/cm² (Cat 1), shock from Table 130.4(C)(b) row "301V to 1 kV"
  - DCFC AC input (AC, VCB): lee_1982 fallback, Cat 2
  - DCFC DC output (DC, electrode_config: null): dc_doan, higher fault current ≈ 5 kA, IE ≈ 6 cal/cm² (Cat 2), shock from Table 130.4(C)(b)

- [ ] **Step 3: intent-out.json** — 5 nodes (mix of AC + DC).

- [ ] **Step 4: reasoning.md** — narrative explaining:
  - How current_type was auto-inferred from equipment_type for DC nodes ("PV combiner box" → dc; "DC fast charger output" → dc)
  - Why DC nodes have electrode_config: null (the IEEE 1584 concept doesn't apply)
  - Why DC nodes use dc_doan (combined Doan + Stokes & Oppenlander)
  - Why shock-approach for DC comes from Table 130.4(C)(b), not (a)
  - How the unified cascade keeps AC parent → DC child relationships intact

- [ ] **Step 5: Validate + Commit**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
python3 -c "
import json, jsonschema
s = json.load(open('electrical/arc-flash/schemas/arc-flash-ir.schema.json'))
d = json.load(open('electrical/arc-flash/examples/us-pv-with-dcfc/output.json'))
jsonschema.validate(d, s); print('IR OK')
s2 = json.load(open('electrical/arc-flash/schemas/arc-flash-intent.schema.json'))
d2 = json.load(open('electrical/arc-flash/examples/us-pv-with-dcfc/intent-out.json'))
jsonschema.validate(d2, s2); print('Intent OK')
"
git add electrical/arc-flash/examples/us-pv-with-dcfc/
git commit -m "feat(arc-flash): example 3 — US 480V AC + 600V PV DC + DCFC unified cascade"
```

---

## Task 23: Final README rewrite + SKILLS_STATUS update + push

**Files:**
- Modify: `electrical/arc-flash/README.md` (full rewrite, replacing the Task 2 stub)
- Modify: `SKILLS_STATUS.md` (promote arc-flash from stub → beta)

- [ ] **Step 1: Rewrite README.md**

File: `electrical/arc-flash/README.md` (overwrite)

```markdown
# `arc-flash` — Per-Node Arc-Flash Analysis (IEEE 1584 + NFPA 70E)

**Status:** `beta`
**Version:** `1.0.0`
**Drawing type:** `arc_flash_study`
**Phase:** B (Phase A standards layers shipped previous sprint)
**Reference:** `electrical/fault-level/` (production reference) + `electrical/cable-sizing/` (sibling beta — proven artefact pattern)

## What this skill produces

A project-scoped arc-flash IR with per-node:

- Incident energy (cal/cm²) at working distance
- Arc-flash boundary distance (where E = 1.2 cal/cm²)
- Limited + Restricted shock-approach boundaries (NFPA 70E §130.4 — bundled because every label needs them)
- PPE category 1–4 (NFPA 70E Table 130.7(C)(15)(c)) + engineer override
- `label_recommended` boolean per NFPA 70E §130.5(H)
- `method_applied` tag + `method_fallback_trail[]` showing every method tried

**Plus an `arc-flash` intent** (slim downstream subset) emitted alongside — consumed by future `electrical/arc-flash-labelling` skill (stub committed 2026-05-17 at `electrical/arc-flash-labelling/`).

## Five methods + fallback chain

| Method | Source | Bias | When used |
|---|---|---|---|
| `ieee1584_2018` | IEEE 1584:2018 §§6-10 + Annex C | Most realistic | Preferred for AC; requires transcribed coefficients |
| `ieee1584_2002` | IEEE 1584:2002 (Doughty/Neal) | Slightly conservative vs 2018 | Legacy compatibility + fallback |
| `lee_1982` | Lee 1982 IEEE-IAS paper | **Significantly conservative (2-5× higher IE)** | Always-available fallback |
| `nfpa70e_table` | NFPA 70E Table 130.7(C)(15)(a)/(b) | **Most conservative** | Equipment-class lookup, no IE computed |
| `dc_doan` | NFPA 70E Annex D §D.1+D.2 | Realistic for DC | DC nodes only (current_type=dc) |

For each AC node: 2018 → 2002 → Lee 1982 → NFPA 70E table → pending. Every node records the full trail.

## Jurisdictions supported

| Jurisdiction | Regulatory framing | Label policy |
|---|---|---|
| GB | HSG48 + IET CoP (voluntary best practice) | Recommended but not statutory |
| EU / INT | IEEE 1584 (de facto international standard) | Best practice |
| US | NFPA 70E §130.5(H) (mandatory under OSHA) | Required for switchgear / panelboards / MCCs ≥240V |

## Voltage range

208V – 15 kV AC + DC up to 1000V.

## Cross-drawing intent contract

| Direction | Intent | Purpose |
|---|---|---|
| Produces | `arc-flash` | Per-node IE/AFB/PPE/shock-approach → consumed by future arc-flash-labelling skill |
| Consumes | `fault-level` | Per-node Ibf + ipk + X/R for arc-current calc |
| Consumes | `db-layout-rollup` | Equipment type + OCPD type + voltage for inference |

## File structure

```
electrical/arc-flash/
├── README.md
├── CHANGELOG.md
├── skill.manifest.json
├── inputs.json
├── prompts/        (generator 14-step / validator 10 INV / reviewer 8 D)
├── schemas/        (IR + intent)
├── rules/          (5 YAMLs)
├── constraints/    (4 YAMLs)
├── validation/     (4 YAMLs, 12 checks)
├── ontology/       (method-types + current-types)
├── docs/           (engineering-philosophy + known-limitations)
├── evals/          (runner-config + 9 evals)
└── examples/       (UK LV / INT MV / US PV+DCFC)
```

Plus the new calc contract at `shared/calculations/electrical/arc-flash-incident-energy.json` (shipped this sprint).

## Eval coverage matrix

| Eval ID | Category | Tests |
|---|---|---|
| eval-01-uk-lv-switchboard-happy-path | happy_path | 400V UK commercial cascade, baseline |
| eval-02-mv-cascade-with-drawout | edge_case | 11kV + 400V cascade, HCB + VCB |
| eval-03-coefficient-fallback-trap | validation_trap | 2018 coefficients null → Lee 1982 fallback |
| eval-04-missing-fault-data | missing_input | No Ifault → method_applied: pending |
| eval-05-jurisdiction-us-with-restricted | jurisdiction_switch | IE > 40 → RESTRICTED |
| eval-06-rationale-block | rationale_block | 8 sections + chat_summary |
| eval-07-dc-pv-string | skill_specific | DC node with dc_doan method |
| eval-08-conservative-t-clear-default | skill_specific | No ocpd_type → 2.0s default + warning |
| eval-09-shock-approach-out-of-range | skill_specific | 47 kV → SHOCK_APPROACH_BEYOND_TABLE_RANGE |

All 6 WI5 categories + 3 skill-specific.

## Phase A dependencies (already shipped)

- `shared/standards/electrical/IEEE1584/` (28 files, production)
- `shared/standards/electrical/NFPA70E/` (25 files, production)
- `shared/schemas/core/standards-{formula,table,section}.schema.json` (3 schemas)
- `shared/validation/standards/*.py` (3 validation scripts)

## Tool calls awaiting runtime

| Tool name | Purpose |
|---|---|
| `calc.arc_flash_incident_energy` | IEEE 1584 / Lee / NFPA 70E / Doan fallback chain. Contract at `shared/calculations/electrical/arc-flash-incident-energy.json`. Status: tool_call_pending until runtime ships. |

## Pending-verification coefficients

17 IEEE 1584 coefficient files in the Phase A standards layer carry null values (pending transcription from a paid copy). The skill handles this gracefully via the method fallback chain — when 2018 coefficients are null, auto-demotes to Lee 1982 or NFPA 70E table method.

When the coefficients are eventually transcribed (a future micro-sprint), the skill auto-promotes from `lee_1982` to `ieee1584_2018` with no code changes.

## Known limitations

See `docs/known-limitations.md`. v1.0.0 does NOT cover:
- DC > 1000V (utility-scale PV 1500V systems) → v1.1
- BESS-specific safety analysis → separate `bess-safety` skill
- Arc-flash label content generation → separate `electrical/arc-flash-labelling` skill (stubbed)
- Time-graded protection coordination → separate `protection-coordination` skill (refines t_clear)
- MV utility-side fault contribution beyond fault-level

## Versioning

- Minor bumps (1.x.0): new jurisdictions, new evals, DC > 1000V support
- Major bump (2.0.0): breaking IR schema change OR IEEE 1584:2028 adoption
- Patch bumps (1.0.x): rules/constraints/validation fixes

## License

See repository root `LICENSE`.
```

- [ ] **Step 2: Update SKILLS_STATUS.md (promote arc-flash from stub → beta)**

Find the arc-flash row (currently absent or under stubs — there's no existing row to modify; we add one). In the Electrical section, add a new row for arc-flash near the related entries:

```
| arc-flash | `electrical/arc-flash` | **beta** | IEEE 1584:2018, NFPA 70E:2024, Lee 1982, Doan 2007, Stokes & Oppenlander 1991 | 9/3 ✓ | v1.0.0 Phase B. 14-step generator, IR + intent schemas, 12 deterministic checks, 9 evals (6 WI5 + 3 skill-specific), 3 worked examples (UK LV / INT MV / US PV+DCFC). 5-method fallback chain (2018→2002→Lee→table→pending; dc_doan for DC). Math deferred to calc.arc_flash_incident_energy runtime tool per WI3. Consumes fault-level + db-layout-rollup intents; emits arc-flash intent for future labelling skill. |
```

Insert it near the arc-flash-labelling stub row (added in commit `711ebd5`) so they're co-located in the table.

Update Summary counts:
- Production: 1 (lighting-layout)
- Beta: 6 (sld, db-layout, earthing, fault-level, cable-sizing, **arc-flash**)
- Stub: existing minus 0 + 0 = unchanged (arc-flash row is new, was never a stub; arc-flash-labelling stays stub)
- Total: existing + 1

Update Beta list in the summary section to include `electrical/arc-flash`.

Update Roadmap section to mark arc-flash shipped + clarify sprint sequence:

```markdown
## Roadmap — next skills to promote

Tier 1 sequence (live):

1. ✅ Tighten calc contracts in `shared/calculations/electrical/` (shipped)
2. ✅ `electrical/fault-level` v1.0.0 beta (shipped 2026-05-16)
3. ✅ `electrical/cable-sizing` v1.0.0 beta (shipped 2026-05-16)
4. ✅ Phase A: IEEE 1584 + NFPA 70E standards layers (shipped 2026-05-17)
5. ✅ Phase B: `electrical/arc-flash` v1.0.0 beta (shipped 2026-05-17)
6. 🔄 clause_ref retrofit for 93 pre-existing files (1.5 hr micro-sprint)
7. `electrical/arc-flash-labelling` + ANSI Z535.4 promotion
8. `electrical/earthing` v1.1 — TN-S + Zs table
9. `electrical/db-layout` v1.1 — DC distribution + Type B RCD
10. `electrical/voltage-drop` (or fold into cable-sizing)
11. `electrical/sld` v1.2 — eval split
```

- [ ] **Step 3: Final verification — all artefacts in place**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
echo "=== Artefact inventory ==="
find electrical/arc-flash -type f | wc -l                    # expect 48
test -f shared/calculations/electrical/arc-flash-incident-energy.json && echo "Calc contract present"
echo "=== Schema validations ==="
for ex in electrical/arc-flash/examples/*/; do
  python3 -c "
import json, jsonschema
s = json.load(open('electrical/arc-flash/schemas/arc-flash-ir.schema.json'))
d = json.load(open('${ex}output.json'))
jsonschema.validate(d, s); print('IR OK ${ex}')
s2 = json.load(open('electrical/arc-flash/schemas/arc-flash-intent.schema.json'))
d2 = json.load(open('${ex}intent-out.json'))
jsonschema.validate(d2, s2); print('Intent OK ${ex}')
"
done
echo "=== YAML parses ==="
for f in $(find electrical/arc-flash -name "*.yaml"); do
  python3 -c "import yaml; yaml.safe_load(open('$f'))" && echo "OK $f"
done
echo "=== JSON parses ==="
for f in $(find electrical/arc-flash -name "*.json"); do
  jq . "$f" > /dev/null && echo "OK $f"
done
echo "=== Manifest standards file presence ==="
jq -r '.standards[]' electrical/arc-flash/skill.manifest.json | while read p; do
  test -f "$p" || echo "MISSING $p"
done
echo "=== Manifest calc-contract presence ==="
jq -r '.calculations[]' electrical/arc-flash/skill.manifest.json | while read p; do
  test -f "$p" || echo "MISSING $p"
done
```

Expected: ~48 files in electrical/arc-flash + calc contract present, 6 schema validations OK (3 examples × 2 docs), every YAML + JSON OK, no MISSING lines.

- [ ] **Step 4: Commit + push**

```bash
git add electrical/arc-flash/README.md SKILLS_STATUS.md
git commit -m "feat(arc-flash): v1.0.0 beta — README rewrite + SKILLS_STATUS promotion to beta"
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
- [ ] All 36 standards files referenced in manifest exist on disk (Phase A files)
- [ ] New calc contract `shared/calculations/electrical/arc-flash-incident-energy.json` exists
- [ ] 3 worked examples all schema-validate (IR + intent)
- [ ] Every cascade node in every example has `method_applied` from controlled vocabulary
- [ ] Every node has `method_fallback_trail[]` populated (never empty)
- [ ] Every node has `shock_approach` block with citation
- [ ] Rationale block has 8 sections in every example
- [ ] SKILLS_STATUS.md shows arc-flash as beta + roadmap updated
- [ ] All commits pushed to origin/main

When done: announce on the user channel — "arc-flash v1.0.0 beta shipped (Phase B complete). Next: clause_ref retrofit micro-sprint."

