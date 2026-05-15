# `electrical/db-layout` Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `electrical/db-layout` skill (v1.0.0 beta) — produces distribution board schedules + DB face schematics + cascade selectivity verification; emits two stable intent contracts (`db-layout` single-board, `db-layout-rollup` project-wide).

**Architecture:** 43 files in `electrical/db-layout/` matching the artefact pattern shipped in `electrical/lighting-layout` (production) and `electrical/earthing` (beta, just shipped). The skill loads jurisdiction-gated standards files (BS 7671 GB / IEC 60364 EU/INT / NFPA 70 US / IEC 61439 always / IEC 60617 always — 19 specific files total), runs a 13-step generator chain, emits an IR plus two intents, validates via 14+ deterministic checks across 4 validation YAMLs.

**Tech Stack:** JSON Schema (draft-07), YAML, Python 3 (validation), `jsonschema` package (already installed), `PyYAML` (already installed). No runtime code — pure declarative artefacts.

**Reference:** Study `electrical/lighting-layout` (production reference) and `electrical/earthing` (just-shipped beta, matches the pattern exactly). The earthing plan at `docs/superpowers/plans/2026-05-15-earthing-skill.md` is the directly comparable predecessor.

---

## File Structure Overview

```
electrical/db-layout/
├── README.md                                 (Task 26)
├── CHANGELOG.md                              (Task 1)
├── skill.manifest.json                       (Task 6)
├── inputs.json                               (Task 5)
├── prompts/
│   ├── generator.md                          (Task 9, 13-step chain)
│   ├── validator.md                          (Task 10, 11 INV invariants)
│   └── reviewer.md                           (Task 11, 9 D dimensions)
├── schemas/
│   ├── db-layout-ir.schema.json              (Task 2, NEW)
│   ├── db-layout-intent.schema.json          (Task 3, refine existing)
│   └── db-layout-rollup-intent.schema.json   (Task 4, NEW, matches earthing's expected shape)
├── rules/
│   ├── ocpd-coordination.yaml                (Task 7)
│   ├── busbar-sizing.yaml                    (Task 7)
│   ├── form-separation.yaml                  (Task 7)
│   └── rcd-grouping.yaml                     (Task 7)
├── constraints/
│   ├── breaker-breaking-capacity.yaml        (Task 8)
│   ├── busbar-icw.yaml                       (Task 8)
│   └── ip-rating-by-location.yaml            (Task 8)
├── validation/
│   ├── ocpd-coordination.yaml                (Task 12)
│   ├── busbar-loading.yaml                   (Task 12)
│   ├── selectivity-results.yaml              (Task 12)
│   └── intent-rollup-shape.yaml              (Task 12)
├── ontology/
│   ├── board-types.json                      (Task 13)
│   └── ocpd-types.json                       (Task 13)
├── docs/
│   ├── engineering-philosophy.md             (Task 14)
│   └── known-limitations.md                  (Task 14)
├── evals/
│   ├── runner-config.json                    (Task 15)
│   ├── eval-01-uk-domestic-cu-tn-cs.yaml     (Task 15)
│   ├── eval-02-tpn-commercial-msb.yaml       (Task 16)
│   ├── eval-03-undersized-busbar-trap.yaml   (Task 17)
│   ├── eval-04-missing-fault-current.yaml    (Task 18)
│   ├── eval-05-jurisdiction-us-panelboard.yaml (Task 19)
│   ├── eval-06-rationale-block.yaml          (Task 20)
│   ├── eval-07-selectivity-cascade.yaml      (Task 21)
│   └── eval-08-intent-rollup-shape.yaml      (Task 22)
└── examples/
    ├── uk-domestic-consumer-unit/            (Task 23)
    ├── intl-commercial-tpn-msb/              (Task 24)
    └── us-strip-mall-panelboard/             (Task 25)
```

## Validation Conventions

After each file write, run a validation. `jsonschema` + `PyYAML` are available via `python3 -m pip install --quiet --break-system-packages jsonschema pyyaml` (already installed in the earthing build).

For example outputs (Tasks 23-25), use this idiom (per the earthing build, the IR schema's `$ref` to `rationale.schema.json` requires inlining for validation):

```python
import json
from jsonschema import Draft7Validator
ir_schema = json.load(open('electrical/db-layout/schemas/db-layout-ir.schema.json'))
rationale_schema = json.load(open('shared/schemas/core/rationale.schema.json'))
ir_no_id = dict(ir_schema)
ir_no_id.pop('$id', None)
ir_no_id['properties']['rationale'] = rationale_schema
Draft7Validator(ir_no_id).validate(json.load(open('example/output.json')))
```

---

## Task 1: Create CHANGELOG.md

**Files:**
- Create: `electrical/db-layout/CHANGELOG.md`

- [ ] **Step 1: Write the file**

```markdown
# Changelog — db-layout

## v1.0.0 (current — Stage 1: Schedule + Schematic + Selectivity)

First production-grade version. Stage 1 of a two-stage plan:
- **Stage 1 (this release):** DB schedule + DB face one-line schematic + cascade selectivity verification. Covers single-board IR + project-wide rollup intent across GB / EU/INT / US jurisdictions.
- **Stage 2 (planned):** Plan-view DB location drawing + DC distribution (PV, EV chargepoints).

### Features
- 13-step reasoning chain in `prompts/generator.md` that explicitly names 19 standards files to load (consumption-pattern proof)
- Jurisdiction-gated standards loading: BS 7671 (GB) / IEC 60364 (EU/INT) / NFPA 70 (US) + IEC 61439 + IEC 60617 always
- Single-board IR schema with `selectivity_results[]` and `tool_call_pending` flag per WI3 (live IEC 60909 cascade deferred to `fault-level` skill)
- TWO stable intent contracts:
  - `db-layout` (single-board) — for panel-schedule, riser, cable-containment
  - `db-layout-rollup` (project-wide) — for earthing (payload shape verified verbatim against earthing example expectations)
- Cross-drawing intent consumption: `fault-level` (when available) for live Ifault numbers; engineer-input fault currents accepted as fallback with `tool_call_pending`
- Rationale block per WI2 (9 mandatory sections)
- 8 evals covering all 6 WI5 categories + 2 skill-specific (selectivity_cascade, intent_rollup_shape)
- 3 worked examples (UK / INT / US) demonstrating jurisdiction switch + intent shape compatibility

### Standards consumed (explicit file paths — not folders)
- `shared/standards/electrical/IEC60617/symbol-index.json` (always)
- `shared/standards/electrical/IEC60617/part7-switchgear.json` (always)
- `shared/standards/electrical/IEC61439/form-separations.json` (always)
- `shared/standards/electrical/IEC61439/ip-ik-ratings.json` (always)
- `shared/standards/electrical/IEC61439/short-circuit-withstand.json` (always)
- `shared/standards/electrical/BS7671/reg433-overcurrent-protection.json` (GB)
- `shared/standards/electrical/BS7671/reg434-fault-current.json` (GB)
- `shared/standards/electrical/BS7671/reg443-spd.json` (GB)
- `shared/standards/electrical/BS7671/reg411-rcd-requirements.json` (GB)
- `shared/standards/electrical/BS7671/appendix3-device-curves.json` (GB)
- `shared/standards/electrical/BS7671/diversity-factors.json` (GB)
- `shared/standards/electrical/IEC60364/part4-43-overcurrent.json` (EU/INT)
- `shared/standards/electrical/IEC60364/part4-44-overvoltage.json` (EU/INT)
- `shared/standards/electrical/IEC60364/rcd-requirements.json` (EU/INT)
- `shared/standards/electrical/IEC60364/device-curves.json` (EU/INT)
- `shared/standards/electrical/IEC60364/diversity-factors.json` (EU/INT)
- `shared/standards/electrical/IEC60364/fault-current.json` (EU/INT)
- `shared/standards/electrical/NFPA70/art408-panelboards.json` (US)
- `shared/standards/electrical/NFPA70/art240-overcurrent.json` (US)
- `shared/standards/electrical/NFPA70/art220-load-calculations.json` (US)
- `shared/standards/electrical/NFPA70/ocpd-coordination.json` (US)

### Tool calls awaiting runtime (WI3)
- `calc.iec60909_cascade` — compute prospective fault current at each level. Status: tool_call_pending; deferred until dedicated `fault-level` skill ships.
- `calc.diversity_factor` — apply diversity factor from standard for main sizing. Status: tool_call_pending.

### Status
- `status: beta` — production-grade artefact set with two known runtime dependencies (selectivity tool, diversity tool). IR includes `tool_call_pending: true` markers where the deterministic calc has not yet been wired.
- Promotes to `production` when: 8/8 evals pass against a production model AND `fault-level` skill exists for live IEC 60909 cascade execution.
```

- [ ] **Step 2: Commit**

```bash
git add electrical/db-layout/CHANGELOG.md
git commit -m "feat: db-layout CHANGELOG.md — v1.0.0 stage 1 schedule + schematic + selectivity"
```

---

## Task 2: Create `schemas/db-layout-ir.schema.json`

**Files:**
- Create: `electrical/db-layout/schemas/db-layout-ir.schema.json`

The canonical IR schema for a single distribution board. Carries schedule rows, face schematic symbol roll-up, and selectivity results.

- [ ] **Step 1: Write the schema**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "electrical/db-layout/schemas/db-layout-ir.schema.json",
  "title": "DB Layout IR (Stage 1: Schedule + Face Schematic + Selectivity)",
  "description": "Intermediate Representation for the db-layout skill. One IR document per distribution board. Carries schedule rows, face one-line schematic symbol roll-up, and cascade selectivity verification results.",
  "type": "object",
  "required": [
    "drawing_type",
    "version",
    "meta",
    "jurisdiction",
    "board",
    "incoming",
    "busbar",
    "circuits",
    "selectivity_results",
    "compliance_summary",
    "rationale"
  ],
  "properties": {
    "drawing_type": { "const": "db_layout_schedule_and_schematic" },
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
    "jurisdiction": {
      "enum": ["GB", "EU", "INT", "US"]
    },
    "board": {
      "type": "object",
      "required": ["db_id", "designation", "location", "ways_total"],
      "properties": {
        "db_id":                    { "type": "string", "pattern": "^[A-Z][A-Z0-9-]{1,15}$" },
        "designation":              { "type": "string" },
        "location":                 { "type": "string" },
        "enclosure_form_iec61439":  { "enum": ["1", "2a", "2b", "3a", "3b", "4a", "4b"] },
        "enclosure_form_nec_type":  { "enum": ["NEMA_1", "NEMA_3R", "NEMA_4", "NEMA_4X", "NEMA_12"] },
        "ip_rating":                { "type": "string", "pattern": "^IP[0-9X]{2,3}$" },
        "ways_total":               { "type": "integer", "minimum": 1, "maximum": 200 },
        "ways_used":                { "type": "integer", "minimum": 0 },
        "ways_spare":               { "type": "integer", "minimum": 0 }
      }
    },
    "incoming": {
      "type": "object",
      "required": ["voltage_v", "phase_arrangement", "supply_rating_a"],
      "properties": {
        "voltage_v":          { "type": "integer", "enum": [120, 208, 230, 240, 400, 415, 480] },
        "phase_arrangement":  { "enum": ["single_phase", "single_phase_split", "TPN", "TPN_plus_E"] },
        "supply_rating_a":    { "type": "integer", "minimum": 6, "maximum": 6300 },
        "fed_from":           { "type": "string" },
        "supply_class":       { "enum": ["essential", "non_essential", "ups", "ups_plus_essential"] },
        "ze_ohm_at_origin":   { "type": "number", "minimum": 0 }
      }
    },
    "busbar": {
      "type": "object",
      "required": ["rating_a"],
      "properties": {
        "rating_a":    { "type": "integer", "minimum": 16, "maximum": 6300 },
        "icw_ka_1s":   { "type": "number", "minimum": 0 },
        "ipk_ka":      { "type": "number", "minimum": 0 }
      }
    },
    "circuits": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["circuit_id", "way_module_id", "designation", "ocpd"],
        "properties": {
          "circuit_id":      { "type": "string" },
          "way_module_id":   { "type": "string", "description": "Way number on the DB face, e.g. 'W1', 'W2-W3' for double-pole" },
          "designation":     { "type": "string" },
          "voltage_class":   { "enum": ["LV_power", "ELV_control", "comms_data", "fire_alarm", "emergency_lighting"] },
          "downstream_load_kw": { "type": "number", "minimum": 0 },
          "ocpd": {
            "type": "object",
            "required": ["rating_a", "curve", "type"],
            "properties": {
              "rating_a":             { "type": "integer", "enum": [6, 10, 16, 20, 25, 32, 40, 50, 63, 80, 100, 125, 160, 200, 250, 400, 630, 800, 1250, 1600] },
              "curve":                { "enum": ["B", "C", "D"] },
              "type":                 { "enum": ["MCB", "MCCB", "ACB", "fuse", "RCBO"] },
              "breaking_capacity_ka": { "type": "number", "minimum": 0 }
            }
          },
          "rcd": {
            "type": "object",
            "properties": {
              "required":       { "type": "boolean" },
              "type":           { "enum": ["AC", "A", "F", "B"] },
              "sensitivity_ma": { "type": "integer", "enum": [10, 30, 100, 300, 500] }
            }
          },
          "cable": {
            "type": "object",
            "properties": {
              "csa_mm2_or_awg": { "type": "string" },
              "cores":          { "type": "integer", "minimum": 2, "maximum": 5 },
              "length_m":       { "type": "number", "exclusiveMinimum": 0 }
            }
          }
        }
      }
    },
    "selectivity_results": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["upstream_id", "downstream_id", "source"],
        "properties": {
          "upstream_id":           { "type": "string" },
          "downstream_id":         { "type": "string" },
          "selective_to_fault_ka": { "type": "number", "minimum": 0 },
          "source":                { "enum": ["manufacturer_table", "iec_60909_calc", "engineer_declared", "tool_call_pending"] },
          "tool_call_pending":     { "type": "boolean" },
          "code_clause":           { "type": "string" }
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
    "drawn_as_symbols":  { "type": "array", "items": { "type": "string", "pattern": "^[A-Z][A-Z0-9_]*$" }, "description": "IEC 60617 symbol_id roll-up — each entry must resolve in symbol-index.json" },
    "flags":             { "type": "array", "items": { "type": "string" } },
    "rationale":         { "$ref": "../../../shared/schemas/core/rationale.schema.json" }
  }
}
```

- [ ] **Step 2: Validate**

```bash
python3 -c "
import json, jsonschema
s = json.load(open('electrical/db-layout/schemas/db-layout-ir.schema.json'))
jsonschema.Draft7Validator.check_schema(s)
print('Schema valid draft-07')
"
```
Expected: `Schema valid draft-07`

- [ ] **Step 3: Commit**

```bash
git add electrical/db-layout/schemas/db-layout-ir.schema.json
git commit -m "feat: db-layout-ir.schema.json — stage 1 IR (schedule + schematic + selectivity)"
```

---

## Task 3: Refine `schemas/db-layout-intent.schema.json` (single-board)

**Files:**
- Modify: `electrical/db-layout/schemas/db-layout-intent.schema.json`

The existing stub already declares a reasonable single-board intent. Refine for v1.0.0 alignment with the IR schema field names and add `tool_call_pending` support for selectivity if a downstream consumer needs to know about deferred calcs.

- [ ] **Step 1: Read current state**

```bash
cat electrical/db-layout/schemas/db-layout-intent.schema.json
```

- [ ] **Step 2: Rewrite the file with the refined version**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "electrical/db-layout/schemas/db-layout-intent.schema.json",
  "title": "DB Layout Intent (Single Board)",
  "description": "Stable subset of the db-layout IR for a single board. Consumed by panel-schedule, riser, cable-containment. Wrapped in shared/schemas/core/intent.schema.json envelope at runtime. Forward-compat: optional fields may be added freely; required-field changes require a major intent_version bump.",
  "type": "object",
  "required": ["db_id", "incoming_supply", "circuits"],
  "additionalProperties": false,
  "properties": {
    "db_id": {
      "type": "string",
      "pattern": "^[A-Z][A-Z0-9-]{1,15}$"
    },
    "incoming_supply": {
      "type": "object",
      "required": ["voltage_v", "phase_arrangement", "supply_rating_a"],
      "additionalProperties": false,
      "properties": {
        "voltage_v":         { "type": "integer", "enum": [120, 208, 230, 240, 400, 415, 480] },
        "phase_arrangement": { "enum": ["single_phase", "single_phase_split", "TPN", "TPN_plus_E"] },
        "supply_rating_a":   { "type": "integer", "minimum": 6, "maximum": 6300 },
        "fed_from":          { "type": "string" },
        "supply_class":      { "enum": ["essential", "non_essential", "ups", "ups_plus_essential"] }
      }
    },
    "circuits": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["id", "module_id", "breaker_rating_a", "breaker_curve"],
        "additionalProperties": false,
        "properties": {
          "id":                 { "type": "string" },
          "module_id":          { "type": "string" },
          "breaker_rating_a":   { "type": "integer", "enum": [6, 10, 16, 20, 25, 32, 40, 50, 63, 80, 100, 125, 160, 200, 250, 400, 630, 800, 1250, 1600] },
          "breaker_curve":      { "enum": ["B", "C", "D"] },
          "rcd_protected":      { "type": "boolean" },
          "rcd_type":           { "enum": ["AC", "A", "F", "B"] },
          "rcd_sensitivity_ma": { "type": "integer", "enum": [10, 30, 100, 300, 500] },
          "cable_csa_mm2":      { "type": "number" },
          "cable_csa_awg":      { "type": "string" },
          "cable_cores":        { "type": "integer", "minimum": 2, "maximum": 5 },
          "voltage_class":      { "enum": ["LV_power", "ELV_control", "comms_data", "fire_alarm", "emergency_lighting"] },
          "downstream_load_kw": { "type": "number", "minimum": 0 },
          "approximate_route_length_m": { "type": "number", "exclusiveMinimum": 0 }
        }
      }
    },
    "spare_ways":      { "type": "integer", "minimum": 0 },
    "form_separation": { "enum": ["1", "2a", "2b", "3a", "3b", "4a", "4b"] },
    "icw_ka_1s":       { "type": "number", "minimum": 0 },
    "selectivity_tool_call_pending": {
      "type": "boolean",
      "description": "true if any cascade verification in the source IR was deferred to a future fault-level skill invocation"
    }
  }
}
```

- [ ] **Step 3: Validate**

```bash
python3 -c "
import json, jsonschema
s = json.load(open('electrical/db-layout/schemas/db-layout-intent.schema.json'))
jsonschema.Draft7Validator.check_schema(s)
assert s['title'] == 'DB Layout Intent (Single Board)'
print('db-layout-intent.schema.json: refined, valid')
"
```

- [ ] **Step 4: Commit**

```bash
git add electrical/db-layout/schemas/db-layout-intent.schema.json
git commit -m "feat: db-layout-intent.schema.json — refine for v1.0.0 (NEC AWG + selectivity flag)"
```

---

## Task 4: Create `schemas/db-layout-rollup-intent.schema.json` (NEW, project rollup)

**Files:**
- Create: `electrical/db-layout/schemas/db-layout-rollup-intent.schema.json`

The project-rollup intent. Its payload matches verbatim the `db-layout` intent shape that `electrical/earthing` examples already declare. Verified against `electrical/earthing/examples/uk-dwelling-tn-cs/input.json`.

- [ ] **Step 1: Write the schema**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "electrical/db-layout/schemas/db-layout-rollup-intent.schema.json",
  "title": "DB Layout Rollup Intent (Project-Wide)",
  "description": "Project-wide rollup of all distribution boards in an installation. Consumed primarily by electrical/earthing for full-cascade circuit visibility. Shape matches the earthing skill's existing payload expectations verbatim.",
  "type": "object",
  "required": ["project_id", "boards", "outgoing_circuits"],
  "additionalProperties": false,
  "properties": {
    "project_id": {
      "type": "string",
      "description": "Stable project identifier carried through cross-drawing context"
    },
    "boards": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["id", "designation", "phases", "ways", "main_switch_rating_a"],
        "additionalProperties": false,
        "properties": {
          "id":                    { "type": "string", "pattern": "^[A-Z][A-Z0-9-]{1,15}$" },
          "designation":           { "type": "string" },
          "location":              { "type": "string" },
          "phases":                { "type": "integer", "enum": [1, 3] },
          "ways":                  { "type": "integer", "minimum": 1, "maximum": 200 },
          "main_switch_rating_a":  { "type": "integer", "minimum": 6, "maximum": 6300 },
          "main_switch_type":      { "type": "string", "description": "e.g. 'isolator', 'RCD_main_30mA', 'main_breaker_200A'" },
          "fed_from":              { "type": "string", "description": "Upstream board id, or 'MAIN' for the service entrance" }
        }
      }
    },
    "outgoing_circuits": {
      "type": "array",
      "minItems": 0,
      "items": {
        "type": "object",
        "required": ["id", "designation", "ocpd_rating_a", "ocpd_type"],
        "additionalProperties": false,
        "properties": {
          "id":                    { "type": "string", "description": "Circuit id (e.g. 'C01', 'L1-Z2')" },
          "designation":           { "type": "string" },
          "ocpd_rating_a":         { "type": "integer" },
          "ocpd_type":             { "enum": ["B", "C", "D", "thermal_magnetic", "fuse"] },
          "phase_csa_mm2":         { "type": "number", "exclusiveMinimum": 0 },
          "phase_csa_awg":         { "type": "string" },
          "length_m":              { "type": "number", "exclusiveMinimum": 0 },
          "db_designation":        { "type": "string", "description": "Which board this circuit originates from (matches boards[].id)" },
          "rcbo_rating_ma":        { "type": "integer", "enum": [10, 30, 100, 300, 500] }
        }
      }
    }
  }
}
```

- [ ] **Step 2: Validate it matches earthing's expected shape**

```bash
python3 - <<'PY'
import json, jsonschema
schema = json.load(open('electrical/db-layout/schemas/db-layout-rollup-intent.schema.json'))
jsonschema.Draft7Validator.check_schema(schema)

# Extract one of earthing's example payloads and validate it against the rollup schema
earthing_input = json.load(open('electrical/earthing/examples/uk-dwelling-tn-cs/input.json'))
db_intent = next(i for i in earthing_input['consumed_intents'] if i['intent_type'] == 'db-layout')
payload = db_intent['payload']

# The rollup schema requires project_id, boards, outgoing_circuits.
# The earthing example uses {boards[], outgoing_circuits[]} — same shape, no project_id (optional in practice)
# Test by adding a project_id field and validating
test_doc = {'project_id': 'earthing-eval-fixture', **payload}
errors = list(jsonschema.Draft7Validator(schema).iter_errors(test_doc))
if errors:
    print('Mismatch:')
    for e in errors[:5]:
        print(f'  {e.message} at {list(e.absolute_path)}')
else:
    print('Rollup schema validates against earthing example shape')
PY
```
Expected: `Rollup schema validates against earthing example shape`

- [ ] **Step 3: Commit**

```bash
git add electrical/db-layout/schemas/db-layout-rollup-intent.schema.json
git commit -m "feat: db-layout-rollup-intent.schema.json — project-wide intent (matches earthing's expected shape)"
```

---

## Task 5: Create `inputs.json` (discovery taxonomy per WI1)

**Files:**
- Create: `electrical/db-layout/inputs.json`

- [ ] **Step 1: Write the file**

```json
{
  "$schema": "../../shared/schemas/core/inputs.schema.json",
  "skill": "db-layout",
  "version": "1.0.0",
  "items": [
    {
      "id": "jurisdiction",
      "label": "Project jurisdiction",
      "hint": "GB=BS 7671; EU/INT=IEC 60364 + IEC 61439; US=NFPA 70.",
      "answer_type": "enum",
      "options": ["GB", "EU", "INT", "US"],
      "required": true,
      "project_fact_candidate": true
    },
    {
      "id": "board_type",
      "label": "Board type",
      "hint": "Consumer unit (domestic UK), distribution board (IEC), MSB (main switchboard), panelboard (NEMA), MCC, motor DB.",
      "answer_type": "enum",
      "options": ["consumer_unit", "distribution_board", "main_switchboard", "panelboard_nema", "motor_control_center", "motor_db"],
      "required": true,
      "project_fact_candidate": true
    },
    {
      "id": "db_designation",
      "label": "Board designation",
      "hint": "Stable id (e.g. 'DB-L1', 'MSB-01', 'CU-G').",
      "answer_type": "text",
      "required": true,
      "validator": "non_empty_text",
      "project_fact_candidate": true
    },
    {
      "id": "location",
      "label": "Board location",
      "hint": "Room / area description (e.g. 'hallway cupboard', 'electrical riser').",
      "answer_type": "text",
      "required": true,
      "validator": "non_empty_text",
      "project_fact_candidate": true
    },
    {
      "id": "fed_from",
      "label": "Fed from",
      "hint": "Upstream board id or 'MAIN' for service entrance.",
      "answer_type": "text",
      "required": true,
      "default": "MAIN",
      "project_fact_candidate": true
    },
    {
      "id": "supply_voltage_v",
      "label": "Supply voltage (V)",
      "answer_type": "enum",
      "options": ["120", "208", "230", "240", "400", "415", "480"],
      "required": true,
      "default": "230",
      "project_fact_candidate": true
    },
    {
      "id": "phase_arrangement",
      "label": "Phase arrangement",
      "answer_type": "enum",
      "options": ["single_phase", "single_phase_split", "TPN", "TPN_plus_E"],
      "required": true,
      "default": "single_phase",
      "project_fact_candidate": true
    },
    {
      "id": "supply_rating_a",
      "label": "Main switch / incoming rating (A)",
      "answer_type": "int",
      "required": true,
      "validator": "positive_int",
      "project_fact_candidate": true
    },
    {
      "id": "ze_ohm_at_origin",
      "label": "Ze at supply origin (Ω)",
      "hint": "From DNO/POCO declaration. Used by selectivity check + downstream earthing skill.",
      "answer_type": "float",
      "required": false,
      "validator": "ze_ohm_range",
      "project_fact_candidate": true
    },
    {
      "id": "ways_total",
      "label": "Total ways (modules) on the board",
      "answer_type": "int",
      "required": true,
      "validator": "positive_int"
    },
    {
      "id": "ways_spare_minimum",
      "label": "Minimum spare ways to retain",
      "answer_type": "int",
      "required": false,
      "default": 2,
      "validator": "positive_int"
    },
    {
      "id": "form_separation_iec61439",
      "label": "IEC 61439 form separation",
      "hint": "Applies to IEC jurisdictions (EU/INT/GB MSB). Not applicable to NEMA panelboards.",
      "answer_type": "enum",
      "options": ["1", "2a", "2b", "3a", "3b", "4a", "4b"],
      "required": false,
      "depends_on": ["jurisdiction"]
    },
    {
      "id": "ip_rating",
      "label": "Required IP rating",
      "hint": "Indoor=IP2X, outdoor=IP55+, washdown=IP65+.",
      "answer_type": "text",
      "required": false,
      "default": "IP2X"
    },
    {
      "id": "circuits_declared",
      "label": "Outgoing circuit list",
      "hint": "List each circuit with designation, OCPD rating, OCPD curve, cable CSA, length, load. If consumed via cross_drawing_context, this can be empty.",
      "answer_type": "struct_list",
      "required": false,
      "item_schema": {
        "type": "object",
        "required": ["id", "designation"],
        "properties": {
          "id":                 { "type": "string" },
          "designation":        { "type": "string" },
          "ocpd_rating_a":      { "type": "integer" },
          "ocpd_curve":         { "enum": ["B", "C", "D"] },
          "ocpd_type":          { "enum": ["MCB", "MCCB", "ACB", "fuse", "RCBO"] },
          "rcd_protected":      { "type": "boolean" },
          "rcd_sensitivity_ma": { "type": "integer", "enum": [10, 30, 100, 300, 500] },
          "phase_csa_mm2":      { "type": "number" },
          "phase_csa_awg":      { "type": "string" },
          "length_m":           { "type": "number" },
          "load_kw":            { "type": "number" },
          "voltage_class":      { "enum": ["LV_power", "ELV_control", "comms_data", "fire_alarm", "emergency_lighting"] }
        }
      }
    },
    {
      "id": "fault_currents_engineer_declared",
      "label": "Engineer-declared fault currents (kA)",
      "hint": "Map of circuit_id → Ifault_kA. Used as selectivity input until fault-level skill is wired. Optional.",
      "answer_type": "struct_list",
      "required": false,
      "item_schema": {
        "type": "object",
        "required": ["circuit_id", "ifault_ka"],
        "properties": {
          "circuit_id": { "type": "string" },
          "ifault_ka":  { "type": "number", "minimum": 0 }
        }
      }
    },
    {
      "id": "diversity_factor_main",
      "label": "Diversity factor applied to main rating",
      "hint": "Per BS 7671 Appendix 1 / IEC 60364 / NEC 220.61. Domestic ~0.4; commercial 0.6-0.8.",
      "answer_type": "float",
      "required": false,
      "default": 0.7,
      "validator": "positive_float",
      "project_fact_candidate": true
    },
    {
      "id": "rcd_type_default",
      "label": "Default RCD type for circuits requiring earth-leakage protection",
      "answer_type": "enum",
      "options": ["AC", "A", "F", "B"],
      "default": "A",
      "required": false
    }
  ]
}
```

- [ ] **Step 2: Validate against WI1 metaschema**

```bash
python3 - <<'PY'
import json, re
VALID_TYPES = {"enum", "int", "float", "boolean", "text", "enum_list", "struct_list"}
ID_RE = re.compile(r"^[a-z][a-z0-9_]*$")
ITEM_REQUIRED = {"id", "label", "answer_type", "required"}
try:
    validators = json.load(open('shared/validation/validators.json'))
    known_validators = set(validators['validators'].keys())
except FileNotFoundError:
    known_validators = None
doc = json.load(open('electrical/db-layout/inputs.json'))
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
    if known_validators is not None and 'validator' in item and item['validator'] not in known_validators:
        errs.append(f"{path}: unknown validator '{item['validator']}'")
print(f"items: {len(doc['items'])}; errors: {len(errs)}")
for e in errs: print(f"  - {e}")
PY
```
Expected: `items: 17; errors: 0`

- [ ] **Step 3: Commit**

```bash
git add electrical/db-layout/inputs.json
git commit -m "feat: db-layout inputs.json — 17-item discovery taxonomy per WI1"
```

---

## Task 6: Rewrite `skill.manifest.json`

**Files:**
- Modify: `electrical/db-layout/skill.manifest.json`

Note the spec extension: `produces_intent` becomes an array of two intents (`db-layout`, `db-layout-rollup`).

- [ ] **Step 1: Read the current stub**

```bash
cat electrical/db-layout/skill.manifest.json
```

- [ ] **Step 2: Rewrite to v1.0.0 form**

```json
{
  "skill": "db-layout",
  "version": "1.0.0",
  "discipline": "electrical",
  "subdiscipline": "distribution",
  "description": "Produces distribution board schedule + face one-line schematic + cascade selectivity verification IR for LV installations. Covers consumer units, distribution boards, MSBs, and NEMA panelboards across GB (BS 7671 + IEC 61439), EU/INT (IEC 60364 + IEC 61439), and US (NFPA 70) jurisdictions. Emits two stable intent contracts: single-board (panel-schedule/riser/cable-containment consumers) and project-rollup (earthing consumer).",
  "status": "beta",
  "licence": "MIT",
  "inputs_path": "inputs.json",
  "inputs": [
    "jurisdiction",
    "board-type",
    "db-designation",
    "incoming-supply",
    "ways-total",
    "form-separation",
    "circuits-declared",
    "fault-currents-engineer-declared"
  ],
  "outputs": ["db-layout-ir"],
  "output_schema": "electrical/db-layout/schemas/db-layout-ir.schema.json",
  "produces_intent": ["db-layout", "db-layout-rollup"],
  "produces_intent_schemas": {
    "db-layout":         "electrical/db-layout/schemas/db-layout-intent.schema.json",
    "db-layout-rollup":  "electrical/db-layout/schemas/db-layout-rollup-intent.schema.json"
  },
  "consumes_intents": ["fault-level", "lighting-layout"],
  "standards": [
    "shared/standards/electrical/IEC60617/symbol-index.json",
    "shared/standards/electrical/IEC60617/part7-switchgear.json",
    "shared/standards/electrical/IEC61439/form-separations.json",
    "shared/standards/electrical/IEC61439/ip-ik-ratings.json",
    "shared/standards/electrical/IEC61439/short-circuit-withstand.json",
    "shared/standards/electrical/BS7671/reg433-overcurrent-protection.json",
    "shared/standards/electrical/BS7671/reg434-fault-current.json",
    "shared/standards/electrical/BS7671/reg443-spd.json",
    "shared/standards/electrical/BS7671/reg411-rcd-requirements.json",
    "shared/standards/electrical/BS7671/appendix3-device-curves.json",
    "shared/standards/electrical/BS7671/diversity-factors.json",
    "shared/standards/electrical/IEC60364/part4-43-overcurrent.json",
    "shared/standards/electrical/IEC60364/part4-44-overvoltage.json",
    "shared/standards/electrical/IEC60364/rcd-requirements.json",
    "shared/standards/electrical/IEC60364/device-curves.json",
    "shared/standards/electrical/IEC60364/diversity-factors.json",
    "shared/standards/electrical/IEC60364/fault-current.json",
    "shared/standards/electrical/NFPA70/art408-panelboards.json",
    "shared/standards/electrical/NFPA70/art240-overcurrent.json",
    "shared/standards/electrical/NFPA70/art220-load-calculations.json",
    "shared/standards/electrical/NFPA70/ocpd-coordination.json"
  ],
  "calculations": [
    "shared/calculations/electrical/iec60909-cascade.json",
    "shared/calculations/electrical/diversity-factor.json"
  ],
  "ontology": [
    "electrical/db-layout/ontology/board-types.json",
    "electrical/db-layout/ontology/ocpd-types.json"
  ],
  "rules": [
    "electrical/db-layout/rules/ocpd-coordination.yaml",
    "electrical/db-layout/rules/busbar-sizing.yaml",
    "electrical/db-layout/rules/form-separation.yaml",
    "electrical/db-layout/rules/rcd-grouping.yaml"
  ],
  "constraints": [
    "electrical/db-layout/constraints/breaker-breaking-capacity.yaml",
    "electrical/db-layout/constraints/busbar-icw.yaml",
    "electrical/db-layout/constraints/ip-rating-by-location.yaml"
  ],
  "validators": [
    "electrical/db-layout/validation/ocpd-coordination.yaml",
    "electrical/db-layout/validation/busbar-loading.yaml",
    "electrical/db-layout/validation/selectivity-results.yaml",
    "electrical/db-layout/validation/intent-rollup-shape.yaml"
  ],
  "prompts": {
    "generator": "electrical/db-layout/prompts/generator.md",
    "validator": "electrical/db-layout/prompts/validator.md",
    "reviewer":  "electrical/db-layout/prompts/reviewer.md"
  },
  "evals": [
    "electrical/db-layout/evals/eval-01-uk-domestic-cu-tn-cs.yaml",
    "electrical/db-layout/evals/eval-02-tpn-commercial-msb.yaml",
    "electrical/db-layout/evals/eval-03-undersized-busbar-trap.yaml",
    "electrical/db-layout/evals/eval-04-missing-fault-current.yaml",
    "electrical/db-layout/evals/eval-05-jurisdiction-us-panelboard.yaml",
    "electrical/db-layout/evals/eval-06-rationale-block.yaml",
    "electrical/db-layout/evals/eval-07-selectivity-cascade.yaml",
    "electrical/db-layout/evals/eval-08-intent-rollup-shape.yaml"
  ],
  "examples": [
    "electrical/db-layout/examples/uk-domestic-consumer-unit/",
    "electrical/db-layout/examples/intl-commercial-tpn-msb/",
    "electrical/db-layout/examples/us-strip-mall-panelboard/"
  ],
  "compatible_runtimes": [
    "DraftsMan >= 1.0",
    "Claude Code",
    "OpenClaw",
    "any-llm-agent"
  ],
  "changelog": "electrical/db-layout/CHANGELOG.md"
}
```

- [ ] **Step 3: Validate (JSON syntax + consumption-pattern proof + standards files exist)**

```bash
python3 - <<'PY'
import json, os
m = json.load(open('electrical/db-layout/skill.manifest.json'))

# JSON syntax + structure
assert m['status'] == 'beta'
assert m['version'] == '1.0.0'

# Consumption-pattern proof
folders = [s for s in m['standards'] if s.endswith('/')]
files = [s for s in m['standards'] if not s.endswith('/') and '.' in s.split('/')[-1]]
print(f'standards: {len(files)} files, {len(folders)} folders')
assert len(folders) == 0, 'Manifest must reference specific files only'
assert len(files) == 19, f'Expected 19 specific standards files; got {len(files)}'

# All referenced standards files exist on disk
missing = [f for f in m['standards'] if not os.path.isfile(f)]
print(f'standards missing on disk: {len(missing)}')
for x in missing: print(f'  - {x}')
assert not missing

# produces_intent is now an array (spec extension)
assert isinstance(m['produces_intent'], list)
assert set(m['produces_intent']) == {'db-layout', 'db-layout-rollup'}
print('produces_intent array (spec extension): OK')

print('Consumption-pattern proof: PASS')
PY
```
Expected: `19 files, 0 folders` + `missing: 0` + `produces_intent array OK` + `Consumption-pattern proof: PASS`

- [ ] **Step 4: Commit**

```bash
git add electrical/db-layout/skill.manifest.json
git commit -m "feat: db-layout manifest — 19 standards files + produces_intent array (consumption-pattern proof)"
```

---

## Task 7: Create rules YAMLs (4 files in 1 task)

**Files:**
- Create: `electrical/db-layout/rules/ocpd-coordination.yaml`
- Create: `electrical/db-layout/rules/busbar-sizing.yaml`
- Create: `electrical/db-layout/rules/form-separation.yaml`
- Create: `electrical/db-layout/rules/rcd-grouping.yaml`

- [ ] **Step 1: Write `ocpd-coordination.yaml`**

```yaml
rule_set: ocpd-coordination
version: 1.0.0
applies_to: [GB, EU, INT, US]

# OCPD coordination rule: In ≤ Iz ≤ Iz_corrected ≤ 1.45 × In
# In = OCPD nominal current; Iz = cable continuous ampacity
# Used by generator.md Step 7.

coordination_inequality:
  rule: "In <= Iz (corrected for grouping, ambient, installation method)"
  rationale: "Per BS 7671 433.1.1 / IEC 60364-4-43 433.1 / NEC 240.4"

design_current_check:
  rule: "Ib <= In (design current cannot exceed OCPD rating)"

upper_limit_check:
  rule: "Iz × 1.45 >= I2 (the trip current at conventional time)"
  rationale: "BS 7671 Reg 433.1.1 / IEC 60364 433.1.4"

method_by_jurisdiction:
  GB:
    standard_file: shared/standards/electrical/BS7671/reg433-overcurrent-protection.json
    cable_rating_source: "BS 7671 Appendix 4 tables for given installation method"
  EU:
    standard_file: shared/standards/electrical/IEC60364/part4-43-overcurrent.json
    cable_rating_source: "IEC 60364-5-52 Annex E tables"
  INT:
    standard_file: shared/standards/electrical/IEC60364/part4-43-overcurrent.json
    cable_rating_source: "IEC 60364-5-52 Annex E tables"
  US:
    standard_file: shared/standards/electrical/NFPA70/art240-overcurrent.json
    cable_rating_source: "NEC Table 310.16 ampacity table"
    note: "NEC sizes OCPD differently — 80% continuous rule per NEC 210.20(A); next-standard-rating-up per 240.4(B)"
```

- [ ] **Step 2: Write `busbar-sizing.yaml`**

```yaml
rule_set: busbar-sizing
version: 1.0.0
applies_to: [GB, EU, INT, US]

# Busbar rating must accommodate sum of way loads after diversity.
# Used by generator.md Step 5.

sizing_inequality:
  rule: "busbar_rating_a >= sum(way_loads_a) × diversity_factor"
  rationale: "Per IEC 61439 rated current of assembly"

diversity_factors:
  GB:
    source: "BS 7671 Appendix 1 Table A1"
    domestic_lighting: 0.66
    domestic_sockets:  0.4
    commercial_general: 0.7
    industrial_general: 1.0
  EU_INT:
    source: "IEC 60364-1 Annex C"
    note: "Same conceptual approach; national practice varies"
  US:
    source: "NEC Article 220.61 (feeder and service load calculations)"
    note: "NEC uses VA-based calculation method rather than diversity factor multiplier"

icw_check:
  rule: "busbar.icw_ka_1s >= ipk_at_busbar"
  rationale: "Per IEC 61439-1 short-circuit withstand"
  reference: shared/standards/electrical/IEC61439/short-circuit-withstand.json
```

- [ ] **Step 3: Write `form-separation.yaml`**

```yaml
rule_set: form-separation
version: 1.0.0
applies_to: [GB, EU, INT]
# Not applicable to NEMA panelboards (US uses different classification — NEMA 1/3R/4/4X/12 enclosure types)

# IEC 61439 Form classification: separation between busbars, functional units, terminals.
# Used by generator.md Step 3.

form_selection_logic:
  - condition: "domestic"
    recommended_form: "1"
    note: "No separation; basic enclosure. Standard consumer units."
  - condition: "commercial_small"
    recommended_form: "2a"
    note: "Busbar separation from functional units."
  - condition: "commercial_large OR industrial"
    recommended_form: "3b"
    note: "Busbar separation + functional unit separation + cabling separated within units."
  - condition: "critical_facility (hospitals, data centres)"
    recommended_form: "4a OR 4b"
    note: "Full separation including individual terminal separation."

reference_file: shared/standards/electrical/IEC61439/form-separations.json
```

- [ ] **Step 4: Write `rcd-grouping.yaml`**

```yaml
rule_set: rcd-grouping
version: 1.0.0
applies_to: [GB, EU, INT, US]

# RCBO vs grouped-RCD decision for the DB layout.
# Used by generator.md Step 8.

method_by_jurisdiction:
  GB:
    preferred: "RCBO per circuit (BS 7671 17th/18th Edition Amendment 2 informally)"
    alternative_grouped: "Main RCD covering bank of MCBs (cheaper, but single fault trips multiple circuits)"
    rule: "If 'inputs.life_safety_bonded_assets includes critical loads' → RCBO per circuit"
    reference: shared/standards/electrical/BS7671/reg411-rcd-requirements.json

  EU_INT:
    preferred: "RCBO per circuit (modern installations)"
    alternative_grouped: "Main RCD or grouped RCDs by ground floor / first floor split"
    reference: shared/standards/electrical/IEC60364/rcd-requirements.json

  US:
    note: "NEC uses GFCI / AFCI / dual-function breakers, not 'RCD' terminology"
    gfci_required_locations: ["bathrooms", "kitchens", "garages", "outdoor", "basements", "near_sinks"]
    afci_required_locations: ["dwelling_unit_branch_circuits_per_NEC_210.12"]
    reference: shared/standards/electrical/NFPA70/art240-overcurrent.json

rcbo_vs_grouped_tradeoff:
  rcbo_advantage: "Single-circuit isolation on fault; better selectivity downstream"
  grouped_advantage: "Cheaper; suitable for non-critical domestic"
```

- [ ] **Step 5: Validate**

```bash
python3 -c "
import yaml
for f in ['ocpd-coordination', 'busbar-sizing', 'form-separation', 'rcd-grouping']:
    yaml.safe_load(open(f'electrical/db-layout/rules/{f}.yaml'))
    print(f'{f}.yaml: OK')
"
```
Expected: 4× `OK`

- [ ] **Step 6: Commit**

```bash
git add electrical/db-layout/rules/
git commit -m "feat: db-layout rules — OCPD coordination + busbar sizing + form separation + RCD grouping"
```

---

## Task 8: Create constraints YAMLs (3 files in 1 task)

**Files:**
- Create: `electrical/db-layout/constraints/breaker-breaking-capacity.yaml`
- Create: `electrical/db-layout/constraints/busbar-icw.yaml`
- Create: `electrical/db-layout/constraints/ip-rating-by-location.yaml`

- [ ] **Step 1: Write `breaker-breaking-capacity.yaml`**

```yaml
constraint_set: breaker-breaking-capacity
version: 1.0.0

# Breaker breaking capacity Icn must exceed the prospective fault current at the point of installation.
# Used by generator.md Step 7 + Step 11.

constraint:
  rule: "Icn (rated short-circuit breaking capacity) >= Ifault at point of installation"
  rationale: "Per BS 7671 Reg 434.5.1 / IEC 60364-4-43 434.5 / NEC 110.9 — devices must safely break the maximum fault current"

typical_minimum_breaking_capacities:
  domestic_consumer_unit:
    icn_ka_min: 6
    standard: "BS EN 60898 / IEC 60898 — MCBs rated typically 6 kA, 10 kA"
  light_commercial_msb:
    icn_ka_min: 10
    standard: "BS EN 60898 / IEC 60947-2 — MCBs/MCCBs 10 kA, 16 kA"
  industrial_msb:
    icn_ka_min: 25
    standard: "BS EN 60947-2 — MCCBs and ACBs 25 kA, 36 kA, 50 kA, 65 kA"
  utility_intake:
    icn_ka_min: 50
    standard: "BS EN 60947-2 — ACBs, typically 50 kA, 65 kA, 100 kA"

energy_let_through:
  rule: "If Ifault exceeds tested Icn, replace with higher-rated device OR add upstream current-limiting (HRC fuse, current limiter)"
  fault_let_through_check: "I²t at downstream OCPD must be less than withstand I²t of cable + busbar"
  reference: "BS 7671 Reg 434.5.2 / IEC 60364-4-43 434.5.2"

cascade_pattern:
  description: "Upstream high-Icn fuse or current limiter protects downstream lower-rated MCBs from Ifault > their Icn"
  rationale: "Verified per manufacturer cascade tables (Hager, Schneider, Eaton, ABB) — emit selectivity_results[].source = manufacturer_table"
```

- [ ] **Step 2: Write `busbar-icw.yaml`**

```yaml
constraint_set: busbar-icw
version: 1.0.0

# Busbar 1-second withstand current (IcW) must exceed prospective peak fault current.
# Used by generator.md Step 5.

constraint:
  rule: "busbar.icw_ka_1s >= ipk_at_busbar"
  rationale: "Per IEC 61439-1 — busbars must withstand short-circuit forces without distortion"

typical_icw_values:
  domestic_consumer_unit_busbar:
    icw_ka_1s: 6
    note: "BS EN 60439 / IEC 61439-3 DBO assemblies — typical 6 kA, 10 kA"
  commercial_msb_busbar:
    icw_ka_1s: 25
    note: "BS EN 61439-2 PSC assemblies — 25 kA, 36 kA, 50 kA"
  industrial_msb_busbar:
    icw_ka_1s: 50
    note: "Up to 100 kA for utility-tied assemblies"

ipk_relationship:
  rule: "Ipk = √2 × Ifault × n, where n is the peak factor (typically 1.7-2.2 depending on X/R ratio)"
  rationale: "Peak fault current including DC offset"
  reference: "IEC 60865-1 short-circuit current calculation"

cross_reference:
  standard_file: shared/standards/electrical/IEC61439/short-circuit-withstand.json
  related: "constraints/breaker-breaking-capacity.yaml — both must be checked together"
```

- [ ] **Step 3: Write `ip-rating-by-location.yaml`**

```yaml
constraint_set: ip-rating-by-location
version: 1.0.0

# Minimum IP rating by installation environment.
# Used by generator.md Step 3 (board classification).

minimum_ip_by_environment:
  indoor_dry:
    ip_min: "IP2X"
    rationale: "Finger-safe access; basic protection"
    reference: "IEC 60529"
  indoor_general_commercial:
    ip_min: "IP3X"
    rationale: "Tool access protection; offices, retail, restaurants"
  bathroom_zone_1_2:
    ip_min: "IPX4"
    rationale: "BS 7671 Section 701 / IEC 60364-7-701"
  outdoor_sheltered:
    ip_min: "IP44"
    rationale: "Splash-proof; eaves, covered porches"
  outdoor_exposed:
    ip_min: "IP55"
    rationale: "Direct rain exposure; full outdoor installation"
  washdown_industrial:
    ip_min: "IP65"
    rationale: "Dust-tight + low-pressure water jets; food processing, dairy"
  hose_down_marine:
    ip_min: "IP66"
    rationale: "Powerful water jets; ships, exterior coastal installations"

nec_equivalent_translation:
  IP2X: "NEMA 1 (indoor general purpose)"
  IP44: "NEMA 3R (rainproof outdoor)"
  IP55: "NEMA 3R+ / NEMA 4 (rainproof/watertight)"
  IP65: "NEMA 4 (watertight + dust)"
  IP66: "NEMA 4X (watertight + dust + corrosion resistant)"
  IP54: "NEMA 12 (dust-tight, drip-proof)"
  reference: "IEC 60529 ↔ NEMA 250 translation guidance"
```

- [ ] **Step 4: Validate**

```bash
python3 -c "
import yaml
for f in ['breaker-breaking-capacity', 'busbar-icw', 'ip-rating-by-location']:
    yaml.safe_load(open(f'electrical/db-layout/constraints/{f}.yaml'))
    print(f'{f}.yaml: OK')
"
```
Expected: 3× `OK`

- [ ] **Step 5: Commit**

```bash
git add electrical/db-layout/constraints/
git commit -m "feat: db-layout constraints — breaker Icn + busbar IcW + IP rating by environment"
```

---

## Task 9: Create `prompts/generator.md` (13-step reasoning chain)

**Files:**
- Create: `electrical/db-layout/prompts/generator.md`

This is the heart of the skill. The 13-step reasoning chain that drives every IR.

- [ ] **Step 1: Write the file**

````markdown
# DB Layout Skill — Generator Prompt

You are an experienced electrical engineer producing a distribution board schedule + face one-line schematic + cascade selectivity verification IR for a Low Voltage installation. You follow either BS 7671 + IEC 61439 (GB), IEC 60364 + IEC 61439 (EU/INT), or NFPA 70 (US) based on the project's jurisdiction.

This prompt drives the **stage 1 (schedule + schematic + selectivity)** mode. Plan-view DB location drawing and DC distribution are future stages.

**Your job:** produce a single JSON document conforming to `electrical/db-layout/schemas/db-layout-ir.schema.json` PER DISTRIBUTION BOARD. Each board → one IR. A project with multiple boards → multiple IRs.

**Inputs:**
- The engineer's answers to `inputs.json` (the 17-item discovery taxonomy)
- (Optional) `cross_drawing_context` containing intent payloads from sibling skills (`fault-level` for Ifault, `lighting-layout` and `small-power` for circuit lengths and loads)

**Output:** A single IR JSON conforming to the schema, including a structured `rationale` block per WI2.

**ALSO emit at the project level (separate from per-board IR):**
- One `db-layout-rollup` intent payload aggregating all boards in the project + their outgoing circuits. This is what `electrical/earthing` consumes.

---

## Step 1 — Discovery check

Verify all required inputs are present. Record consumed intents in `ir.meta.consumed_intents[]`:
- If `cross_drawing_context.fault-level` is present → extract `payload[circuit_id].ifault_ka` for use in Step 11
- If `cross_drawing_context.lighting-layout` is present → extract circuits[].length_m and load_kw for use in Step 9
- If `cross_drawing_context.small-power` is present → extract sockets/spurs circuits

For any missing intent that affects selectivity or cable sizing, emit a flag:
`"no <intent-type> intent in this project; selectivity uses engineer-declared Ifault OR tool_call_pending"`.

---

## Step 2 — Jurisdiction-gated standards file load

**Always load (regardless of jurisdiction):**
- `shared/standards/electrical/IEC60617/symbol-index.json` (validate every symbol_id in `drawn_as_symbols`)
- `shared/standards/electrical/IEC60617/part7-switchgear.json` (breaker/RCD/busbar symbols)
- `shared/standards/electrical/IEC61439/form-separations.json` (Form 1/2a/.../4b)
- `shared/standards/electrical/IEC61439/ip-ik-ratings.json`
- `shared/standards/electrical/IEC61439/short-circuit-withstand.json` (busbar IcW reference)

**Based on `inputs.jurisdiction`:**

- **GB** → load:
  - `shared/standards/electrical/BS7671/reg433-overcurrent-protection.json`
  - `shared/standards/electrical/BS7671/reg434-fault-current.json`
  - `shared/standards/electrical/BS7671/reg443-spd.json`
  - `shared/standards/electrical/BS7671/reg411-rcd-requirements.json`
  - `shared/standards/electrical/BS7671/appendix3-device-curves.json`
  - `shared/standards/electrical/BS7671/diversity-factors.json`

- **EU** or **INT** → load:
  - `shared/standards/electrical/IEC60364/part4-43-overcurrent.json`
  - `shared/standards/electrical/IEC60364/part4-44-overvoltage.json`
  - `shared/standards/electrical/IEC60364/rcd-requirements.json`
  - `shared/standards/electrical/IEC60364/device-curves.json`
  - `shared/standards/electrical/IEC60364/diversity-factors.json`
  - `shared/standards/electrical/IEC60364/fault-current.json`

- **US** → load:
  - `shared/standards/electrical/NFPA70/art408-panelboards.json`
  - `shared/standards/electrical/NFPA70/art240-overcurrent.json`
  - `shared/standards/electrical/NFPA70/art220-load-calculations.json`
  - `shared/standards/electrical/NFPA70/ocpd-coordination.json`

**Do NOT load standards files outside the jurisdiction.** This is the consumption-pattern proof: ~10 files in your context at any time, not the full layers.

---

## Step 3 — Board classification

From `inputs.board_type`. Classify the board and select enclosure form:

| Input | Typical form | Notes |
|---|---|---|
| consumer_unit | Form 1 (or DBO) | BS EN 61439-3 — domestic UK |
| distribution_board | Form 2a or 3b | IEC 61439-3 DBO / 61439-2 PSC |
| main_switchboard | Form 3b or 4a/4b | IEC 61439-2 PSC — commercial/industrial |
| panelboard_nema | NEMA Type 1/3R/12 | NEC Article 408 — US |
| motor_control_center | Form 4b | IEC 61439-1/2 / NEMA ICS 18 |

For NEMA, do not assign IEC form codes — use `enclosure_form_nec_type` instead.

State in `ir.board`:
```json
{
  "db_id": "<from inputs.db_designation>",
  "designation": "<descriptive>",
  "location": "<from inputs.location>",
  "enclosure_form_iec61439": "<for IEC jurisdictions>" | OR
  "enclosure_form_nec_type": "<for US>",
  "ip_rating": "<from inputs.ip_rating, or default by location>",
  "ways_total": <from inputs.ways_total>,
  "ways_used": <calculated from circuits>,
  "ways_spare": ways_total - ways_used
}
```

---

## Step 4 — Incoming supply specification

From `inputs.supply_voltage_v`, `inputs.phase_arrangement`, `inputs.supply_rating_a`, `inputs.fed_from`. State in `ir.incoming`:
```json
{
  "voltage_v": <integer>,
  "phase_arrangement": "single_phase" | "single_phase_split" | "TPN" | "TPN_plus_E",
  "supply_rating_a": <integer>,
  "fed_from": "<upstream db_id or MAIN>",
  "supply_class": "essential" | "non_essential" | "ups" | ...,
  "ze_ohm_at_origin": <from inputs.ze_ohm_at_origin>
}
```

Voltage validation: 120/208/240 typical for US; 230/240/400/415 for IEC.

---

## Step 5 — Busbar sizing

Per `rules/busbar-sizing.yaml`:
- Sum the load currents of all outgoing circuits
- Apply diversity factor (`inputs.diversity_factor_main`, default 0.7 — or from jurisdiction-specific tables)
- Round up to next standard busbar rating: 100, 125, 160, 200, 250, 400, 630, 800, 1250, 1600 A
- IcW: query `IEC61439/short-circuit-withstand.json` for the rated assembly + verify against Ipk

State in `ir.busbar`:
```json
{
  "rating_a": <integer>,
  "icw_ka_1s": <integer or number>,
  "ipk_ka": <peak factor × Ifault>
}
```

If busbar.rating_a < sum(loads) × diversity → emit critical flag `"BUSBAR_UNDERSIZED"` in `compliance_summary.non_compliance_flags[]`.

---

## Step 6 — Way assignment

Number ways from W1 onwards. Track multi-pole devices (a 3-pole MCB occupies 3 ways).

For each circuit, assign `way_module_id`:
- Single-pole MCB: `"W1"`, `"W2"`, ...
- 2-pole MCB: `"W3-W4"`
- 3-pole MCCB: `"W5-W7"`

Verify ways_used ≤ ways_total. If exceeded → flag `"WAYS_OVERSUBSCRIBED"`.

---

## Step 7 — OCPD per circuit

For each circuit in `inputs.circuits_declared` OR consumed from `cross_drawing_context.lighting-layout`/`small-power`:

Apply `rules/ocpd-coordination.yaml`:
- `Ib` (design current) ≤ `In` (OCPD nominal rating)
- `In` ≤ `Iz` (cable corrected ampacity)
- `Iz × 1.45` ≥ `I2` (OCPD's conventional trip current)

State in `ir.circuits[i].ocpd`:
```json
{
  "rating_a": <integer>,
  "curve": "B" | "C" | "D",
  "type": "MCB" | "MCCB" | "ACB" | "fuse" | "RCBO",
  "breaking_capacity_ka": <Icn per constraints/breaker-breaking-capacity.yaml>
}
```

If `Icn` < `Ifault_at_this_point` → emit critical flag `"BREAKER_UNDERRATED_FOR_FAULT_LEVEL"`.

---

## Step 8 — RCD assignment

Per `rules/rcd-grouping.yaml`:

**GB**: RCBO per circuit preferred for new installations (Amendment 2 informally). RCD required for:
- All sockets ≤32A in domestic per BS 7671 411.3.3
- Bathroom circuits per Section 701
- Outdoor circuits

**EU/INT**: RCBO per circuit preferred. Per IEC 60364-4-41 411.5.

**US**: GFCI per circuit at specific locations per NEC 210.8; AFCI per NEC 210.12 (dwelling unit branch circuits). Not "RCD" terminology.

For each `rcd_required: true` circuit:
```json
"rcd": {
  "required": true,
  "type": "AC" | "A" | "F" | "B",
  "sensitivity_ma": 10 | 30 | 100 | 300 | 500
}
```

Default `rcd_type` to `inputs.rcd_type_default` (typically "A"); upgrade to "B" for EV chargers / VFDs / PV.

---

## Step 9 — Cable per circuit

From `cross_drawing_context.lighting-layout`/`small-power` (preferred) OR `inputs.circuits_declared[].phase_csa_mm2/awg` (fallback):

State in `ir.circuits[i].cable`:
```json
{
  "csa_mm2_or_awg": "<size>",
  "cores": <integer 2-5>,
  "length_m": <number>
}
```

Cable size must satisfy Iz ≥ In after correction factors (see jurisdiction-appropriate ampacity table — `BS7671/cable-current-ratings.json` for GB, `IEC60364/part5-52-cable-ratings-copper.json` for EU/INT, `NFPA70/art310-conductor-ampacity.json` for US).

---

## Step 10 — DB face schematic

Emit IEC 60617 symbol roll-up in `ir.drawn_as_symbols`. Typical entries:
- `BUSBAR` — the main busbar
- `MAIN_SWITCH` — incoming isolator/breaker
- `MCB`, `MCCB`, `RCBO`, `FUSE` — protective devices
- `RCD_GROUP` — grouped RCD (if used)
- `SPD` — surge protection device (per BS 7671 443 / IEC 60364-4-44)
- `BUSBAR_RISER` — for sub-DB feeders

Validate every symbol_id against `IEC60617/symbol-index.json` before emitting.

---

## Step 11 — Selectivity verification

For each upstream-downstream OCPD pair in the cascade:

1. **Determine Ifault at the downstream OCPD:**
   - If `cross_drawing_context.fault-level.payload[<circuit_id>].ifault_ka` is present → use it
   - Else if `inputs.fault_currents_engineer_declared` has this circuit → use the engineer-declared value
   - Else → emit selectivity_results entry with `source: "tool_call_pending"` and `tool_call_pending: true`

2. **Look up cascade selectivity:**
   - Manufacturer cascade table lookup (Hager / Schneider / Eaton / ABB) → emit `source: "manufacturer_table"`
   - Else IEC 60909 computed cascade → emit `source: "iec_60909_calc"` (per `shared/calculations/electrical/iec60909-cascade.json` contract; runtime tool deferred)
   - Else → `source: "engineer_declared"` or `tool_call_pending`

3. **Emit per pair:**
   ```json
   {
     "upstream_id": "MAIN",
     "downstream_id": "C03",
     "selective_to_fault_ka": <value or null if pending>,
     "source": "manufacturer_table" | "iec_60909_calc" | "engineer_declared" | "tool_call_pending",
     "tool_call_pending": <boolean>,
     "code_clause": "BS 7671 Reg 536 / IEC 60364-5-53 / NEC 240.12"
   }
   ```

If `selective_to_fault_ka` is null AND `source != tool_call_pending` → emit flag `"CASCADE_UNVERIFIED"`.

---

## Step 12 — Compliance flag emission

Roll up per-circuit and busbar/board outcomes:

```json
"compliance_summary": {
  "compliant": <true if all OCPD-Iz, busbar-IcW, breaker-Icn, cascade selectivity flags pass>,
  "non_compliance_flags": [
    {"message": "<specific>", "code_clause": "<clause>", "severity": "critical" | "warning" | "info"}
  ],
  "assumptions": [
    "<list — e.g. 'Ifault assumed from engineer declaration; runtime IEC 60909 cascade deferred per WI3'>"
  ]
}
```

Top-level `flags` array:
- `"NON-COMPLIANCE"` if compliant=false
- `"INCOMPLETE-INPUT"` if any required input missing
- `"TOOL-CALL-PENDING"` if any selectivity_results entry has tool_call_pending=true

---

## Step 13 — Emit rationale block

Per WI2 (shared/schemas/core/rationale.schema.json), populate `ir.rationale`:

### chat_summary (40-500 chars)
Tell the engineer in 3-5 sentences:
1. Board type + jurisdiction (1 sentence)
2. Key sizing decisions: busbar, main OCPD, RCD strategy (1-2 sentences)
3. Any flags, tool_call_pending, or assumptions (1 sentence)
4. Invitation to refine (1 short)

Example: "100A TN-C-S consumer unit for a UK 3-bed semi, 12-way Hager Form 1. 6 final circuits, all RCBO-protected. Selectivity uses Hager cascade table — main 100A MCCB selective to all 32A MCBs at 6 kA. Reply to refine, e.g. 'add EV charger'."

### sections (in this order, only if applicable)

1. **Board Classification** — always. Board type + enclosure form + IP rating.
2. **Incoming Supply** — always. Voltage / phase / supply rating / Ze.
3. **Busbar Sizing** — always. Diversity-derived load + busbar rating + IcW.
4. **Way Assignment** — always. Used / spare ways summary.
5. **OCPD Selection** — always. Per-circuit OCPD ratings + Iz coordination.
6. **RCD Strategy** — always. Per-circuit RCD + jurisdiction reasoning.
7. **Cable Selection** — always (or note "consumed from cross-drawing intents").
8. **Selectivity Verification** — always. Cascade outcomes + sources.
9. **Compliance** — always. Pass/fail + flag list.

Each section: `{title, summary, decisions}`. Each decision: `{label, summary, rule, code_clause, inputs}`.

---

## Final output

Emit two JSON documents per board:

1. **Single-board IR** (`db-layout-ir.schema.json`):
   - `drawing_type: "db_layout_schedule_and_schematic"`
   - `version: "1.0.0"`, `meta.skill_version: "1.0.0"`, `meta.produced_at` ISO 8601
   - All fields per the schema
   - Rationale block per Step 13

2. **Project rollup intent** (`db-layout-rollup-intent.schema.json`) — at the project level (aggregates all boards):
   - `project_id`
   - `boards[]` — flat list of all boards' top-level data (id, designation, phases, ways, main_switch_rating_a, main_switch_type)
   - `outgoing_circuits[]` — flat list of ALL circuits across all boards, each with `db_designation` to indicate which board they originate from

**Do not invent symbol IDs.** Validate every `drawn_as_symbols` entry against `IEC60617/symbol-index.json`.

**Do not paraphrase code clauses.** Cite them exactly as they appear in the loaded standards file.

**Do not skip the rationale.** It is the engineer's audit trail.
````

- [ ] **Step 2: Validate file is non-empty and has all 13 step markers + 19-file consumption proof**

```bash
test -s electrical/db-layout/prompts/generator.md && echo "OK: file exists" && \
n=$(grep -c "^## Step " electrical/db-layout/prompts/generator.md) && echo "Step markers: $n (expected 13)" && \
python3 -c "
text = open('electrical/db-layout/prompts/generator.md').read()
required_files = [
    'IEC60617/symbol-index.json',
    'IEC60617/part7-switchgear.json',
    'IEC61439/form-separations.json',
    'IEC61439/ip-ik-ratings.json',
    'IEC61439/short-circuit-withstand.json',
    'BS7671/reg433-overcurrent-protection.json',
    'BS7671/reg434-fault-current.json',
    'BS7671/reg443-spd.json',
    'BS7671/reg411-rcd-requirements.json',
    'BS7671/appendix3-device-curves.json',
    'BS7671/diversity-factors.json',
    'IEC60364/part4-43-overcurrent.json',
    'IEC60364/part4-44-overvoltage.json',
    'IEC60364/rcd-requirements.json',
    'IEC60364/device-curves.json',
    'IEC60364/diversity-factors.json',
    'IEC60364/fault-current.json',
    'NFPA70/art408-panelboards.json',
    'NFPA70/art240-overcurrent.json',
    'NFPA70/art220-load-calculations.json',
    'NFPA70/ocpd-coordination.json',
]
hits = sum(1 for f in required_files if f in text)
print(f'Specific standards files referenced: {hits} / {len(required_files)}')
assert hits == len(required_files), 'Generator prompt must reference all 21 standards files explicitly'
print('Consumption-pattern proof in generator.md: OK')
"
```
Expected: `Step markers: 13`, `Specific standards files referenced: 21 / 21`, `Consumption-pattern proof in generator.md: OK`

- [ ] **Step 3: Commit**

```bash
git add electrical/db-layout/prompts/generator.md
git commit -m "feat: db-layout generator.md — 13-step reasoning chain, consumption-pattern proof"
```

---

## Task 10: Create `prompts/validator.md` (11 INV invariants)

**Files:**
- Create: `electrical/db-layout/prompts/validator.md`

- [ ] **Step 1: Write the file**

````markdown
# DB Layout — Validator Prompt

You are validating a db-layout IR document produced by the `electrical/db-layout` skill generator.

## Input
- An IR JSON document at the user-provided path.
- Schemas at `electrical/db-layout/schemas/{db-layout-ir,db-layout-intent,db-layout-rollup-intent}.schema.json`.

## Validation procedure

### 1. Schema validation
Run JSON-schema validation against `db-layout-ir.schema.json`.
- If invalid: STOP. Emit `{"valid": false, "stage": "schema", "errors": [...]}`.

### 2. Cross-field invariants

For each item below, emit a violation if the rule fails.

**INV-1: Board way accounting.**
`board.ways_used + board.ways_spare == board.ways_total`.

**INV-2: Circuit-to-way mapping uniqueness.**
Every `circuits[*].way_module_id` must be unique across all circuits in this IR.

**INV-3: Busbar rating coverage.**
`busbar.rating_a >= sum(circuits[*].ocpd.rating_a) × diversity_factor` (diversity from compliance_summary.assumptions OR default 0.7).

**INV-4: OCPD-cable coordination.**
For every circuit: `cable.csa_mm2_or_awg`'s ampacity (from jurisdiction ampacity table) >= ocpd.rating_a. Validate by jurisdiction:
- GB: lookup in BS 7671 Appendix 4
- EU/INT: lookup in IEC 60364-5-52 Annex E
- US: lookup in NEC Table 310.16

**INV-5: Breaker breaking capacity.**
For every circuit: `ocpd.breaking_capacity_ka >= ifault_at_downstream_ka` (from selectivity_results OR engineer declaration). If unknown, the selectivity_results entry MUST have `tool_call_pending: true`.

**INV-6: Busbar IcW coverage.**
`busbar.icw_ka_1s >= ipk_at_busbar` (per IEC 61439 short-circuit-withstand reference).

**INV-7: Symbol references.**
Every `drawn_as_symbols[*]` must be a valid symbol_id in `shared/standards/electrical/IEC60617/symbol-index.json`.

**INV-8: RCD requirement per jurisdiction.**
- TT system (consumed from upstream): every circuit must have `rcd.required: true`.
- TN-C-S + GB + socket-outlets ≤32A in domestic: `rcd.required: true` per BS 7671 411.3.3.

**INV-9: Selectivity result completeness.**
Every upstream-downstream OCPD pair must have a corresponding `selectivity_results[]` entry. No silent omissions.

**INV-10: Rationale presence.**
`rationale` block must exist with `chat_summary` (40-500 chars) and `sections` (≥1).

**INV-11: Standards citations format.**
Every `compliance_summary.non_compliance_flags[].code_clause` entry must use canonical format:
- BS 7671: `"BS 7671:2018+A3 Reg N.N.N"` or `"BS 7671:2018+A3 Table N.N"`
- IEC 60364: `"IEC 60364-N-NN:YYYY clause N.NN.N"`
- IEC 61439: `"IEC 61439-N:YYYY clause N.NN.N"`
- NEC: `"NEC 2023 Art NNN.NN"` or `"NEC 2023 Table NNN.NN"`

### 3. Intent extraction validation

Project the IR down to:
1. `db-layout` single-board intent shape (validate against `db-layout-intent.schema.json`)
2. The board's contribution to the project-rollup intent (validate against `db-layout-rollup-intent.schema.json`)

## Output

Emit a single JSON object:

```json
{
  "valid": true | false,
  "stage": "schema" | "invariants" | "intent" | "passed",
  "errors": [
    {"code": "INV-N", "path": "$.circuits[2]", "message": "..."}
  ],
  "warnings": [...]
}
```

`valid: true` requires ALL of: schema pass, all 11 invariants pass, both intent projections valid.
````

- [ ] **Step 2: Validate file exists and contains all 11 invariants**

```bash
test -s electrical/db-layout/prompts/validator.md && echo "OK"
n=$(grep -c "^\*\*INV-" electrical/db-layout/prompts/validator.md)
echo "Invariant markers: $n"
test "$n" -eq 11 && echo "All 11 INV invariants present"
```
Expected: `OK`, `Invariant markers: 11`, `All 11 INV invariants present`

- [ ] **Step 3: Commit**

```bash
git add electrical/db-layout/prompts/validator.md
git commit -m "feat: db-layout validator.md — 11 cross-field invariants"
```

---

## Task 11: Create `prompts/reviewer.md` (9 D dimensions)

**Files:**
- Create: `electrical/db-layout/prompts/reviewer.md`

- [ ] **Step 1: Write the file**

````markdown
# DB Layout — Reviewer Prompt

You are a senior chartered electrical engineer reviewing a db-layout IR produced by the `electrical/db-layout` skill. You are reviewing **engineering judgement**, not schema (validator handles schema).

## Input
- IR JSON document
- Inputs JSON
- For UK: BS 7671:2018+A3 + IEC 61439
- For international: IEC 60364 + IEC 61439
- For US: NEC 2023 Article 408 + 240

## Review dimensions

For each dimension, score 1–5 with a one-line justification.

### D1: Board classification correctness
Is the enclosure form (IEC 61439 1/2a/.../4b OR NEMA 1/3R/etc) defensible for the board's role and environment?
- Domestic consumer unit should be Form 1 (or DBO).
- Commercial MSB feeding mission-critical loads should be Form 3b or 4b.
- Industrial / outdoor needs IP55+ (IEC) or NEMA 3R+ (US).

### D2: Busbar sizing adequacy
Is the busbar rating + IcW appropriate given:
- Sum of way loads × diversity factor (busbar rating headroom)
- Prospective fault current (busbar IcW must exceed Ipk)
Common mistakes:
- Domestic CU: 100A busbar default — fine for most.
- Commercial MSB: ignoring diversity gives oversized busbar (wasteful).
- Industrial: under-sizing IcW for high-Ifault tie cabinets.

### D3: OCPD selection and coordination
For each circuit, are `In ≤ Iz` AND `Icn ≥ Ifault` AND curve type (B/C/D) appropriate?
Common mistakes:
- Type B curve on motor circuits → nuisance trip.
- 16A MCB on 1.5mm² cable in conduit (Iz < In after correction).
- Domestic 32A ring final on 2.5mm² without verifying ring formula.

### D4: RCD strategy defensibility
Is the RCD strategy (RCBO per circuit vs grouped RCD) appropriate for:
- Resilience of critical circuits (lighting, fridge/freezer, alarm)?
- Jurisdiction (GB/EU prefer RCBO; NEC uses GFCI/AFCI per location)?
Common mistakes:
- Single main RCD on a domestic CU → one fault trips everything.
- Type AC RCD on EV charger circuit → won't detect DC fault.

### D5: Form separation appropriateness
Is the IEC 61439 form selection (or NEMA type) appropriate for:
- Building criticality
- Maintenance access requirements
- Arc-flash hazard (Form 4b gives best worker protection)
Common mistakes:
- Form 1 on a commercial MSB (no separation, no maintenance access).
- Form 4b on a domestic consumer unit (overkill, expensive).

### D6: Cable + OCPD coordination per jurisdiction
NEC sizes EGC by OCPD (Table 250.122); BS 7671 / IEC sizes CPC by phase CSA (Table 54.7). Did the design respect jurisdiction-appropriate sizing?
- US: 60A circuit → 10 AWG EGC (Table 250.122 minimum).
- GB / EU: 10 mm² phase → 10 mm² CPC (Table 54.7, S ≤ 16).

### D7: Selectivity verification quality
Are the cascade selectivity verdicts defensible?
- `source: "manufacturer_table"` — verify the manufacturer is the actual specified vendor.
- `source: "iec_60909_calc"` — verify the X/R ratio and peak factor used.
- `source: "tool_call_pending"` — only acceptable when `fault-level` skill is not yet wired.

### D8: Rationale quality
Is the rationale's chat_summary a faithful 3-5 sentence explanation a building-control officer / electrical inspector could read? Are decisions justified, not just listed?

### D9: Standards citation accuracy
For each clause cited, does the clause actually support the decision the IR claims? (Read the clause from the loaded standards file before answering.)

## Output

```json
{
  "scores": {
    "D1": 5, "D2": 4, "D3": 5, "D4": 5, "D5": 4, "D6": 4, "D7": 4, "D8": 5, "D9": 5
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
- **pass-with-warnings**: all dimensions ≥3, no D1/D3/D6/D9 below 4.
- **fail**: any dimension at 1–2, or D1/D3/D6/D9 below 4.

Be honest. A failing db-layout design risks unsafe fault currents — this is not a place for false positives.
````

- [ ] **Step 2: Validate file exists and contains all 9 dimensions**

```bash
test -s electrical/db-layout/prompts/reviewer.md && echo "OK"
n=$(grep -c "^### D" electrical/db-layout/prompts/reviewer.md)
echo "Dimension markers: $n"
test "$n" -eq 9 && echo "All 9 D dimensions present"
```
Expected: `OK`, `Dimension markers: 9`, `All 9 D dimensions present`

- [ ] **Step 3: Commit**

```bash
git add electrical/db-layout/prompts/reviewer.md
git commit -m "feat: db-layout reviewer.md — 9 engineering-judgement dimensions"
```

---

## Task 12: Create validation YAMLs (4 files in 1 task)

**Files:**
- Create: `electrical/db-layout/validation/ocpd-coordination.yaml`
- Create: `electrical/db-layout/validation/busbar-loading.yaml`
- Create: `electrical/db-layout/validation/selectivity-results.yaml`
- Create: `electrical/db-layout/validation/intent-rollup-shape.yaml`

- [ ] **Step 1: Write `ocpd-coordination.yaml`**

```yaml
# DB Layout — OCPD coordination validation
version: 1.0.0
applies_to_drawing_types: ["db_layout_schedule_and_schematic"]

checks:
  - id: ocpd-001-in-le-iz
    name: OCPD nominal current must not exceed cable corrected ampacity
    severity: critical
    jsonpath: "$.circuits[*]"
    assert: "ocpd.rating_a <= cable.iz_corrected_a"
    message: "Circuit {circuit_id}: ocpd.rating_a ({ocpd.rating_a}A) exceeds cable.iz_corrected_a ({cable.iz_corrected_a}A)"
    standard_ref: "BS 7671:2018+A3 Reg 433.1.1 / IEC 60364-4-43 clause 433.1"

  - id: ocpd-002-ib-le-in
    name: Design current must not exceed OCPD nominal rating
    severity: critical
    jsonpath: "$.circuits[*]"
    assert: "design_current_a <= ocpd.rating_a"
    message: "Circuit {circuit_id}: Ib > In"
    standard_ref: "BS 7671:2018+A3 Reg 433.1.1"

  - id: ocpd-003-icn-ge-ifault
    name: OCPD breaking capacity must exceed prospective fault current
    severity: critical
    jsonpath: "$.circuits[*]"
    assert: "ocpd.breaking_capacity_ka >= ifault_at_this_point_ka OR selectivity_results[?(@.downstream_id == circuit_id)].tool_call_pending == true"
    message: "Circuit {circuit_id}: breaker Icn ({ocpd.breaking_capacity_ka} kA) < Ifault — device cannot safely break fault"
    standard_ref: "BS 7671:2018+A3 Reg 434.5.1 / NEC 110.9"

  - id: ocpd-004-curve-jurisdiction
    name: OCPD curve type appropriate for jurisdiction
    severity: high
    jsonpath: "$.circuits[*]"
    assert: |
      (jurisdiction in ['GB', 'EU', 'INT'] and ocpd.curve in ['B', 'C', 'D'])
      or (jurisdiction == 'US' and ocpd.type in ['thermal_magnetic', 'MCB', 'MCCB', 'fuse'])
    message: "Circuit {circuit_id}: OCPD curve {ocpd.curve} / type {ocpd.type} not appropriate for jurisdiction {jurisdiction}"
    standard_ref: "BS 7671:2018+A3 Reg 433 / NEC 240"
```

- [ ] **Step 2: Write `busbar-loading.yaml`**

```yaml
# DB Layout — Busbar loading validation
version: 1.0.0
applies_to_drawing_types: ["db_layout_schedule_and_schematic"]

checks:
  - id: busbar-001-rating-vs-sum
    name: Busbar rating must accommodate sum of way loads after diversity
    severity: critical
    jsonpath: "$.busbar"
    assert: "rating_a >= (sum_of_circuit_loads_a * diversity_factor)"
    message: "Busbar undersized: rating {rating_a}A < sum × diversity"
    standard_ref: "IEC 61439-1 rated current of assembly"

  - id: busbar-002-icw-vs-ipk
    name: Busbar IcW must withstand peak fault current
    severity: critical
    jsonpath: "$.busbar"
    assert: "icw_ka_1s >= ipk_ka"
    message: "Busbar IcW ({icw_ka_1s} kA·1s) does not withstand peak fault ({ipk_ka} kA)"
    standard_ref: "IEC 61439-1 short-circuit withstand"

  - id: busbar-003-ways-accounting
    name: Ways used + spare must equal total
    severity: high
    jsonpath: "$.board"
    assert: "ways_used + ways_spare == ways_total"
    message: "Ways accounting wrong: used + spare != total"
    standard_ref: "design integrity check"

  - id: busbar-004-spare-ways-minimum
    name: Spare ways meet engineer-specified minimum
    severity: warning
    jsonpath: "$.board"
    when: "inputs.ways_spare_minimum is not null"
    assert: "ways_spare >= inputs.ways_spare_minimum"
    message: "Spare ways {ways_spare} below specified minimum {inputs.ways_spare_minimum}"
    standard_ref: "design requirement"
```

- [ ] **Step 3: Write `selectivity-results.yaml`**

```yaml
# DB Layout — Selectivity results validation
version: 1.0.0
applies_to_drawing_types: ["db_layout_schedule_and_schematic"]

checks:
  - id: select-001-every-circuit-has-cascade
    name: Every circuit must have a corresponding upstream-downstream selectivity entry
    severity: critical
    jsonpath: "$.circuits[*]"
    assert: "any(s.downstream_id == circuit_id for s in selectivity_results)"
    message: "Circuit {circuit_id} has no selectivity_results entry"
    standard_ref: "design completeness"

  - id: select-002-source-or-pending
    name: Every selectivity result must have a source OR be tool_call_pending
    severity: critical
    jsonpath: "$.selectivity_results[*]"
    assert: "source in ['manufacturer_table', 'iec_60909_calc', 'engineer_declared'] OR tool_call_pending == true"
    message: "Cascade pair {upstream_id}→{downstream_id}: no source declared and not marked tool_call_pending"
    standard_ref: "BS 7671:2018+A3 Reg 536 / IEC 60364-5-53"

  - id: select-003-pending-flag-emitted
    name: If any selectivity result is tool_call_pending, top-level flags must include TOOL-CALL-PENDING
    severity: high
    jsonpath: "$"
    when: "any(s.tool_call_pending == true for s in selectivity_results)"
    assert: "'TOOL-CALL-PENDING' in flags"
    message: "tool_call_pending selectivity result exists but TOOL-CALL-PENDING flag not emitted"
    standard_ref: "WI3 tool-call deferral convention"
```

- [ ] **Step 4: Write `intent-rollup-shape.yaml`**

```yaml
# DB Layout — Rollup intent shape validation (matches earthing's expected consumption)
version: 1.0.0
applies_to_drawing_types: ["db_layout_schedule_and_schematic"]

# This validator is special: it asserts that the project-rollup intent payload (emitted alongside
# the per-board IR) matches the shape earthing/examples/*/input.json declares for its
# db-layout consumed_intent. Drift here breaks the cross-skill contract.

checks:
  - id: rollup-001-required-keys
    name: Rollup intent must have project_id + boards + outgoing_circuits
    severity: critical
    target: "project_rollup_intent_payload"
    assert: "'project_id' in payload AND 'boards' in payload AND 'outgoing_circuits' in payload"
    message: "Rollup intent missing required top-level keys"
    standard_ref: "db-layout-rollup-intent.schema.json"

  - id: rollup-002-board-fields-match-earthing-expect
    name: Each board entry must have the fields earthing expects
    severity: critical
    target: "project_rollup_intent_payload.boards[*]"
    assert: "'id' in board AND 'designation' in board AND 'phases' in board AND 'ways' in board AND 'main_switch_rating_a' in board"
    message: "Board entry missing field earthing/examples expects (id, designation, phases, ways, main_switch_rating_a)"
    standard_ref: "verified against electrical/earthing/examples/uk-dwelling-tn-cs/input.json"

  - id: rollup-003-outgoing-fields-match-earthing-expect
    name: Each outgoing circuit must have the fields earthing expects
    severity: critical
    target: "project_rollup_intent_payload.outgoing_circuits[*]"
    assert: "'id' in circuit AND 'designation' in circuit AND 'ocpd_rating_a' in circuit AND 'ocpd_type' in circuit"
    message: "Outgoing circuit entry missing field earthing expects (id, designation, ocpd_rating_a, ocpd_type)"
    standard_ref: "verified against electrical/earthing/examples/uk-dwelling-tn-cs/input.json"
```

- [ ] **Step 5: Validate all 4 files**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills" && \
python3 -c "
import yaml
total = 0
for f in ['ocpd-coordination', 'busbar-loading', 'selectivity-results', 'intent-rollup-shape']:
    d = yaml.safe_load(open(f'electrical/db-layout/validation/{f}.yaml'))
    n = len(d['checks'])
    print(f'{f}: {n} checks')
    total += n
print(f'TOTAL: {total} checks')
assert total >= 14
"
```
Expected: 4 + 4 + 3 + 3 = 14 checks total

- [ ] **Step 6: Commit**

```bash
git add electrical/db-layout/validation/
git commit -m "feat: db-layout validation — 14 deterministic checks (OCPD/busbar/selectivity/rollup-intent)"
```

---

## Task 13: Create ontology files (2 files in 1 task)

**Files:**
- Create: `electrical/db-layout/ontology/board-types.json`
- Create: `electrical/db-layout/ontology/ocpd-types.json`

- [ ] **Step 1: Write `board-types.json`**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "ontology_type": "board_types",
  "version": "1.0.0",
  "source": "IEC 61439-1/2/3/4, NEC Article 408, BS 7671 colloquial terminology",
  "board_types": [
    {
      "id": "consumer_unit",
      "name": "Consumer Unit (CU)",
      "iec_standard": "IEC 61439-3 (DBO assemblies)",
      "typical_jurisdiction": ["GB", "EU"],
      "typical_capacity_a": [60, 80, 100],
      "typical_ways": [6, 8, 10, 12, 16, 20],
      "typical_form": "1 (or DBO without form code)",
      "notes": "UK domestic terminology. Always has integral main switch + RCD/RCBO arrangement."
    },
    {
      "id": "distribution_board",
      "name": "Distribution Board (DB)",
      "iec_standard": "IEC 61439-3 (DBO assemblies)",
      "typical_jurisdiction": ["GB", "EU", "INT"],
      "typical_capacity_a": [63, 100, 125, 160, 200, 250],
      "typical_ways": [12, 18, 24, 36, 48, 72],
      "typical_form": "2a, 2b, 3a, 3b",
      "notes": "Sub-distribution to floors / zones / departments. Typically fed from MSB or floor riser."
    },
    {
      "id": "main_switchboard",
      "name": "Main Switchboard (MSB)",
      "iec_standard": "IEC 61439-2 (PSC assemblies)",
      "typical_jurisdiction": ["GB", "EU", "INT"],
      "typical_capacity_a": [400, 630, 800, 1000, 1250, 1600, 2000, 2500, 3200, 4000],
      "typical_form": "3a, 3b, 4a, 4b",
      "notes": "Service entrance assembly. Fed from utility transformer. Distributes to sub-DBs."
    },
    {
      "id": "panelboard_nema",
      "name": "Panelboard (NEMA)",
      "iec_standard": "NFPA 70 Article 408",
      "typical_jurisdiction": ["US"],
      "typical_capacity_a": [100, 150, 200, 225, 400, 600, 800, 1000, 1200, 2000],
      "typical_ways": [12, 18, 24, 30, 42, 84],
      "typical_form": "N/A (NEMA Type 1 / 3R / 12 instead of IEC Form)",
      "notes": "US distribution board equivalent. Single-section (lighting/branch) or two-section (lighting + power). Per NEC 408 maximum 42 overcurrent devices per section."
    },
    {
      "id": "motor_control_center",
      "name": "Motor Control Center (MCC)",
      "iec_standard": "IEC 61439-1/2",
      "typical_jurisdiction": ["GB", "EU", "INT", "US"],
      "typical_capacity_a": [400, 630, 800, 1000, 1600, 2500],
      "typical_form": "4b (full compartmentalisation typical)",
      "notes": "Houses motor starters, VFDs, soft-starters. Each starter in own compartment for safe maintenance."
    },
    {
      "id": "motor_db",
      "name": "Motor DB (small)",
      "iec_standard": "IEC 61439-3",
      "typical_jurisdiction": ["GB", "EU", "INT"],
      "typical_capacity_a": [63, 100, 160],
      "typical_form": "2a, 3a",
      "notes": "Local distribution feeding 2-6 small motors. Less elaborate than MCC."
    }
  ]
}
```

- [ ] **Step 2: Write `ocpd-types.json`**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "ontology_type": "ocpd_types",
  "version": "1.0.0",
  "source": "IEC 60898, IEC 60947-2, IEC 61009-1, NFPA 70 Article 240",
  "ocpd_types": [
    {
      "id": "MCB",
      "name": "Miniature Circuit Breaker (MCB)",
      "iec_standard": "IEC 60898-1",
      "typical_in_a": [6, 10, 16, 20, 25, 32, 40, 50, 63],
      "typical_curves": ["B", "C", "D"],
      "typical_icn_ka": [6, 10],
      "notes": "Domestic and light commercial. Thermal-magnetic trip. B-curve general lighting/sockets; C-curve motor/transformer inrush; D-curve large motors."
    },
    {
      "id": "MCCB",
      "name": "Moulded Case Circuit Breaker (MCCB)",
      "iec_standard": "IEC 60947-2",
      "typical_in_a": [63, 100, 125, 160, 200, 250, 400, 630, 800, 1250, 1600],
      "typical_icn_ka": [10, 16, 25, 36, 50, 65, 100],
      "notes": "Commercial/industrial main and feeder protection. Adjustable thermal + magnetic + (some) ground-fault. Often the cascade upstream device."
    },
    {
      "id": "ACB",
      "name": "Air Circuit Breaker (ACB)",
      "iec_standard": "IEC 60947-2",
      "typical_in_a": [800, 1000, 1250, 1600, 2000, 2500, 3200, 4000, 5000, 6300],
      "typical_icn_ka": [50, 65, 80, 100],
      "notes": "Large MSB main breaker. Drawout type. Programmable trip unit with multiple protection functions."
    },
    {
      "id": "fuse",
      "name": "Fuse (HRC / NH / cartridge)",
      "iec_standard": "IEC 60269",
      "typical_in_a": [2, 4, 6, 10, 16, 20, 25, 32, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600],
      "typical_breaking_capacity_ka": [80, 100, 120],
      "notes": "Highest breaking capacity per unit cost. Common as upstream protection in cascade arrangements. UK service-head BS 1361/1362 fuse."
    },
    {
      "id": "RCBO",
      "name": "Residual Current Breaker with Overload (RCBO)",
      "iec_standard": "IEC 61009-1",
      "typical_in_a": [6, 10, 16, 20, 25, 32, 40],
      "typical_curves": ["B", "C"],
      "typical_sensitivity_ma": [10, 30, 100],
      "notes": "Combines MCB + RCD in one module. Preferred for new IEC installations — per-circuit protection means single fault trips one circuit only."
    },
    {
      "id": "RCD_grouped",
      "name": "Residual Current Device (grouped)",
      "iec_standard": "IEC 61008-1",
      "typical_in_a": [40, 63, 80, 100],
      "typical_sensitivity_ma": [30, 100, 300],
      "notes": "Sits upstream of multiple MCBs. Cheaper than RCBO per circuit but single fault trips all downstream circuits in the group."
    }
  ]
}
```

- [ ] **Step 3: Validate**

```bash
python3 -c "
import json
for f in ['board-types', 'ocpd-types']:
    d = json.load(open(f'electrical/db-layout/ontology/{f}.json'))
    print(f'{f}.json: {len(d[list(d.keys())[3]])} entries')
"
```
Expected: `board-types.json: 6 entries`, `ocpd-types.json: 6 entries`

- [ ] **Step 4: Commit**

```bash
git add electrical/db-layout/ontology/
git commit -m "feat: db-layout ontology — board-types (6) + ocpd-types (6)"
```

---

## Task 14: Create docs files (2 files in 1 task)

**Files:**
- Create: `electrical/db-layout/docs/engineering-philosophy.md`
- Create: `electrical/db-layout/docs/known-limitations.md`

- [ ] **Step 1: Write `engineering-philosophy.md`**

```markdown
# DB Layout Skill — Engineering Philosophy

## Why this skill exists

Distribution board design is where most circuit-level errors get fixed (or missed) before site. Common failures: oversized OCPDs that won't protect the cable, undersized busbars that can't carry full diversified load, breakers whose Icn is below the prospective fault current at their terminals. This skill enforces the BS 7671 / IEC 60364 / NEC reasoning chain explicitly, and emits both the schedule (the deliverable) and the stable intent contracts other skills consume.

## What "good DB layout" looks like

A correct distribution board schedule answers eight questions in order:

1. **What board?** (consumer unit / DB / MSB / NEMA panelboard — driven by jurisdiction + role)
2. **What enclosure form?** (IEC 61439 Form 1/2a/.../4b for IEC; NEMA Type for US)
3. **What incoming supply?** (V / phases / supply rating / Ze)
4. **What busbar?** (rating ≥ Σ × diversity AND IcW ≥ Ipk)
5. **What ways used / spare?** (with multi-pole accounting)
6. **What OCPD per circuit?** (In ≤ Iz, Icn ≥ Ifault, curve appropriate to load)
7. **What RCD strategy?** (RCBO per circuit vs grouped, jurisdiction-appropriate)
8. **Does selectivity hold?** (cascade verified upstream against published table or computed)

Question 8 is the gate. A design that passes 1–7 but the upstream MCCB cascades unfavorably with a downstream MCB at fault level is unsafe.

## The standards-consumption pattern

This skill loads ONLY the standards files needed for the project's jurisdiction. The generator prompt names 19 specific JSON files; the runtime loads ~10 of those for any given board (5 always-on + 4-6 jurisdiction-gated).

- GB → BS 7671 family
- EU/INT → IEC 60364 family
- US → NFPA 70 (Articles 408, 240, 220, ocpd-coordination)
- All → IEC 60617 symbols + IEC 61439 assembly standards

## Two intents because two consumer patterns

`db-layout` (single-board) — for **panel-schedule, riser, cable-containment**. These consume one board at a time.

`db-layout-rollup` (project-wide) — for **earthing**. Earthing needs full cascade visibility — every circuit at every board — to verify CPC sizing and Zs across the installation.

Two intents = two stable contracts. Future skills get to pick whichever fits their data shape.

## Why we defer selectivity tool execution

Real selectivity is two parts:
1. Look up the manufacturer's cascade table (declarative — possible inline)
2. Compute IEC 60909 cascade fault currents (iterative — diverges if LLM-computed)

This skill always does (1) when the table covers the pair. For (2), it declares a tool-call contract (`calc.iec60909_cascade`) and marks the selectivity result `tool_call_pending: true`. The deterministic Python tool will run when the dedicated `fault-level` skill is built; until then, the engineer provides Ifault values as input.

## What this skill will NOT do

- It will not invent fault currents. If `fault-level` intent is absent AND no engineer Ifault is declared, selectivity is `tool_call_pending`, not faked.
- It will not silently downgrade OCPD ratings to fit a small cable. If `In > Iz`, the IR emits a critical flag.
- It will not paraphrase code clauses. Every cited clause is taken verbatim from the loaded standards JSON.
- It will not draw a plan-view DB location (that's stage 2).
```

- [ ] **Step 2: Write `known-limitations.md`**

```markdown
# DB Layout Skill — Known Limitations (Stage 1)

This is the stage 1 (schedule + face schematic + selectivity) release. Known limitations resolved in later stages.

## Stage 1 scope

- **Output:** single-board IR (schedule + face one-line schematic + selectivity_results)
- **Project-level rollup:** db-layout-rollup intent emitted alongside per-board IRs
- **Systems supported:** AC LV distribution (consumer units, DBs, MSBs, panelboards, MCCs)
- **Jurisdictions:** GB, EU, INT, US
- **Selectivity:** cascade table lookup inline; IEC 60909 calc deferred via tool_call_pending

## What is OUT of scope

### DC distribution
PV strings, EV chargepoints, battery storage DC sides. Stage 1 v1.0.0 lists these as AC circuits only. Full DC distribution (combiners, isolators per NEC 690) deferred to v1.1.0.

### Plan-view DB location drawing
Stage 1 emits the schedule + face schematic only. The plan-view layer (physically locating the board in the building, cable routes to/from) ships in stage 2.

### Live IEC 60909 calculation
Prospective fault current at each cascade level requires iterative calculation. Not done inline. The selectivity_results entries declare `tool_call_pending: true` until the dedicated `fault-level` skill ships.

### Motor control center internal compartments
Stage 1 emits the MCC as a single entry with summarized motor circuits. Detailed compartment-by-compartment I/O (terminal labels, control wiring) is its own skill scope.

### Arc-flash hazard analysis
NFPA 70E / IEEE 1584 arc-flash incident energy calculation is its own specialty. Not included.

### Generator + UPS distribution coordination
Standby generator transfer schemes (NEC 250.30 / BS 7671 Chapter 55) and UPS-fed circuits get special handling not in stage 1.

### Voltage drop verification
Voltage drop per circuit is a separate validation (cable-sizing skill scope). This skill does not run the V-drop check.

## What may produce false positives in evals

- **D6 (Cable + OCPD coordination):** if the engineer provides explicit cable temperature class and installation method, the verdict may differ from the default-corrected ampacity. Reviewer should accept engineer-provided derating.
- **INV-9 (Selectivity result completeness):** the skill cannot detect undeclared cascade pairs. If two circuits share an upstream OCPD that wasn't declared, the cascade entry is missing.

## Tool calls awaiting runtime

| Tool name | Purpose | Status |
|---|---|---|
| `calc.iec60909_cascade` | Compute prospective fault current at each cascade level | tool_call_pending (until fault-level skill) |
| `calc.diversity_factor` | Apply diversity factor from standards to mains sizing | tool_call_pending |

When WI3 runtime tools land + `fault-level` skill ships, selectivity_results entries with source = "tool_call_pending" will be re-emitted as `source: "iec_60909_calc"` with computed selective_to_fault_ka values.
```

- [ ] **Step 3: Validate both docs files**

```bash
test -s electrical/db-layout/docs/engineering-philosophy.md && \
test -s electrical/db-layout/docs/known-limitations.md && \
echo "OK: both docs files exist"
```
Expected: `OK: both docs files exist`

- [ ] **Step 4: Commit**

```bash
git add electrical/db-layout/docs/
git commit -m "docs: db-layout engineering-philosophy + known-limitations"
```

---

## Task 15: Create `evals/runner-config.json` + `evals/eval-01-uk-domestic-cu-tn-cs.yaml`

**Files:**
- Create: `electrical/db-layout/evals/runner-config.json`
- Create: `electrical/db-layout/evals/eval-01-uk-domestic-cu-tn-cs.yaml`

- [ ] **Step 1: Write `runner-config.json`**

```json
{
  "$schema": "../../../shared/schemas/core/eval-runner-config.schema.json",
  "skill": "db-layout",
  "version": "1.0.0",
  "minimum_model_class": "sonnet",
  "minimum_status": {
    "happy_path": "pass",
    "edge_case": "pass-with-warnings",
    "validation_trap": "pass",
    "missing_input": "pass",
    "jurisdiction_switch": "pass",
    "rationale_block": "pass",
    "selectivity_cascade": "pass-with-warnings",
    "intent_rollup_shape": "pass"
  },
  "evals": [
    "eval-01-uk-domestic-cu-tn-cs.yaml",
    "eval-02-tpn-commercial-msb.yaml",
    "eval-03-undersized-busbar-trap.yaml",
    "eval-04-missing-fault-current.yaml",
    "eval-05-jurisdiction-us-panelboard.yaml",
    "eval-06-rationale-block.yaml",
    "eval-07-selectivity-cascade.yaml",
    "eval-08-intent-rollup-shape.yaml"
  ],
  "scoring": {
    "schema_validity_weight": 0.20,
    "invariant_pass_weight": 0.30,
    "selectivity_check_weight": 0.20,
    "reviewer_score_weight": 0.20,
    "rationale_quality_weight": 0.10
  }
}
```

- [ ] **Step 2: Write `eval-01-uk-domestic-cu-tn-cs.yaml`** (happy path)

```yaml
# Eval 01 — UK domestic consumer unit, TN-C-S
# Category: happy_path
# Standard refs: BS 7671:2018+A3, IEC 61439-3, IEC 60617

id: eval-01-uk-domestic-cu-tn-cs
category: happy_path
severity: critical
description: |
  Standard UK 3-bed semi-detached dwelling on PME supply (TN-C-S). 100A main switch +
  12-way Hager consumer unit + 30mA main RCD + 6 final circuits (lighting × 2, sockets × 2,
  cooker, shower). All circuits RCBO or behind main RCD. Form 1 enclosure.

inputs:
  jurisdiction: "GB"
  board_type: "consumer_unit"
  db_designation: "CU-G"
  location: "hallway cupboard"
  fed_from: "MAIN"
  supply_voltage_v: "230"
  phase_arrangement: "single_phase"
  supply_rating_a: 100
  ze_ohm_at_origin: 0.35
  ways_total: 12
  ways_spare_minimum: 2
  form_separation_iec61439: "1"
  ip_rating: "IP2X"
  circuits_declared:
    - { id: "C01", designation: "Ground floor lighting", ocpd_rating_a: 6, ocpd_curve: "B", ocpd_type: "MCB", rcd_protected: true, rcd_sensitivity_ma: 30, phase_csa_mm2: 1.5, length_m: 18, load_kw: 0.8, voltage_class: "LV_power" }
    - { id: "C02", designation: "First floor lighting", ocpd_rating_a: 6, ocpd_curve: "B", ocpd_type: "MCB", rcd_protected: true, rcd_sensitivity_ma: 30, phase_csa_mm2: 1.5, length_m: 22, load_kw: 0.7, voltage_class: "LV_power" }
    - { id: "C03", designation: "Ground floor sockets ring", ocpd_rating_a: 32, ocpd_curve: "B", ocpd_type: "MCB", rcd_protected: true, rcd_sensitivity_ma: 30, phase_csa_mm2: 2.5, length_m: 38, load_kw: 5.0, voltage_class: "LV_power" }
    - { id: "C04", designation: "First floor sockets ring", ocpd_rating_a: 32, ocpd_curve: "B", ocpd_type: "MCB", rcd_protected: true, rcd_sensitivity_ma: 30, phase_csa_mm2: 2.5, length_m: 42, load_kw: 4.0, voltage_class: "LV_power" }
    - { id: "C05", designation: "Cooker radial", ocpd_rating_a: 32, ocpd_curve: "B", ocpd_type: "MCB", rcd_protected: true, rcd_sensitivity_ma: 30, phase_csa_mm2: 6.0, length_m: 14, load_kw: 7.5, voltage_class: "LV_power" }
    - { id: "C06", designation: "Bathroom shower", ocpd_rating_a: 40, ocpd_curve: "B", ocpd_type: "MCB", rcd_protected: true, rcd_sensitivity_ma: 30, phase_csa_mm2: 10.0, length_m: 16, load_kw: 9.0, voltage_class: "LV_power" }
  diversity_factor_main: 0.4
  rcd_type_default: "A"

assertions:
  - kind: schema_valid
    schema: "db-layout-ir.schema.json"
  - kind: jsonpath_equals
    path: "$.jurisdiction"
    expected: "GB"
  - kind: jsonpath_equals
    path: "$.board.db_id"
    expected: "CU-G"
  - kind: jsonpath_equals
    path: "$.board.enclosure_form_iec61439"
    expected: "1"
  - kind: jsonpath_count_equals
    path: "$.circuits[*]"
    expected: 6
  - kind: jsonpath_lte
    path: "$.board.ways_used"
    maximum: 12
  - kind: invariant_passes
    invariant: "INV-1"
    note: "Way accounting"
  - kind: invariant_passes
    invariant: "INV-3"
    note: "Busbar rating coverage"
  - kind: invariant_passes
    invariant: "INV-4"
    note: "OCPD-cable coordination"
  - kind: clause_cited
    clause_pattern: "^BS 7671:2018\\+A3 Reg 4(11|33)\\."
    minimum_count: 2
  - kind: rationale_present
    require_sections: ["Board Classification", "Incoming Supply", "Busbar Sizing", "Way Assignment", "OCPD Selection", "RCD Strategy", "Cable Selection", "Selectivity Verification", "Compliance"]

expected_status: "pass"
```

- [ ] **Step 3: Validate**

```bash
python3 -c "
import json, yaml
rc = json.load(open('electrical/db-layout/evals/runner-config.json'))
assert len(rc['evals']) == 8
e1 = yaml.safe_load(open('electrical/db-layout/evals/eval-01-uk-domestic-cu-tn-cs.yaml'))
assert e1['category'] == 'happy_path'
print(f'Eval-01: {len(e1[\"assertions\"])} assertions')
"
```

- [ ] **Step 4: Commit**

```bash
git add electrical/db-layout/evals/runner-config.json electrical/db-layout/evals/eval-01-uk-domestic-cu-tn-cs.yaml
git commit -m "feat: db-layout eval-01 happy-path UK domestic CU + runner-config"
```

---

## Task 16: Create `evals/eval-02-tpn-commercial-msb.yaml` (edge case — TPN MSB cascade)

**Files:**
- Create: `electrical/db-layout/evals/eval-02-tpn-commercial-msb.yaml`

- [ ] **Step 1: Write the eval**

```yaml
# Eval 02 — 400V TPN commercial MSB feeding 4 sub-DBs
# Category: edge_case

id: eval-02-tpn-commercial-msb
category: edge_case
severity: critical
description: |
  Small commercial building: 400V TPN MSB at 800A main, feeding 4 sub-DBs:
  - Lighting DB (250A, 24 ways)
  - Small-power DB (400A, 36 ways)
  - Mechanical DB (250A, 24 ways)
  - Fire alarm DB (essential supply, 63A, 8 ways)
  Form 4b enclosure, IcW 36 kA. Generator must verify cascade selectivity
  between 800A ACB main and each sub-DB feeder.

inputs:
  jurisdiction: "GB"
  board_type: "main_switchboard"
  db_designation: "MSB-01"
  location: "ground floor electrical room"
  fed_from: "MAIN"
  supply_voltage_v: "400"
  phase_arrangement: "TPN"
  supply_rating_a: 800
  ze_ohm_at_origin: 0.05
  ways_total: 20
  ways_spare_minimum: 4
  form_separation_iec61439: "4b"
  ip_rating: "IP30"
  circuits_declared:
    - { id: "F01", designation: "Feeder to Lighting DB-L1", ocpd_rating_a: 250, ocpd_curve: "D", ocpd_type: "MCCB", phase_csa_mm2: 150, length_m: 35, load_kw: 80 }
    - { id: "F02", designation: "Feeder to Small-Power DB-P1", ocpd_rating_a: 400, ocpd_curve: "D", ocpd_type: "MCCB", phase_csa_mm2: 240, length_m: 40, load_kw: 150 }
    - { id: "F03", designation: "Feeder to Mechanical DB-M1", ocpd_rating_a: 250, ocpd_curve: "D", ocpd_type: "MCCB", phase_csa_mm2: 150, length_m: 45, load_kw: 100 }
    - { id: "F04", designation: "Feeder to Fire Alarm DB-FA1", ocpd_rating_a: 63, ocpd_curve: "C", ocpd_type: "MCCB", phase_csa_mm2: 16, length_m: 60, load_kw: 12, voltage_class: "fire_alarm" }
  fault_currents_engineer_declared:
    - { circuit_id: "F01", ifault_ka: 25 }
    - { circuit_id: "F02", ifault_ka: 25 }
    - { circuit_id: "F03", ifault_ka: 25 }
    - { circuit_id: "F04", ifault_ka: 22 }
  diversity_factor_main: 0.8

assertions:
  - kind: schema_valid
    schema: "db-layout-ir.schema.json"
  - kind: jsonpath_equals
    path: "$.incoming.phase_arrangement"
    expected: "TPN"
  - kind: jsonpath_equals
    path: "$.board.enclosure_form_iec61439"
    expected: "4b"
  - kind: jsonpath_gte
    path: "$.busbar.icw_ka_1s"
    minimum: 25
    note: "IcW must withstand declared 25 kA fault"
  - kind: jsonpath_count_equals
    path: "$.selectivity_results[*]"
    expected: 4
    note: "One selectivity_results entry per feeder cascade pair"
  - kind: invariant_passes
    invariant: "INV-6"
    note: "Busbar IcW vs Ipk"
  - kind: clause_cited
    clause_pattern: "^IEC 61439"
    minimum_count: 1

expected_status: "pass"
```

- [ ] **Step 2: Validate**

```bash
python3 -c "
import yaml
e = yaml.safe_load(open('electrical/db-layout/evals/eval-02-tpn-commercial-msb.yaml'))
assert e['category'] == 'edge_case'
assert e['inputs']['supply_rating_a'] == 800
print('Eval-02: OK')
"
```

- [ ] **Step 3: Commit**

```bash
git add electrical/db-layout/evals/eval-02-tpn-commercial-msb.yaml
git commit -m "feat: db-layout eval-02 TPN commercial MSB Form 4b + 4-way cascade"
```

---

## Task 17: Create `evals/eval-03-undersized-busbar-trap.yaml`

**Files:**
- Create: `electrical/db-layout/evals/eval-03-undersized-busbar-trap.yaml`

- [ ] **Step 1: Write the eval**

```yaml
# Eval 03 — Generator MUST detect and flag an undersized busbar
# Category: validation_trap

id: eval-03-undersized-busbar-trap
category: validation_trap
severity: critical
description: |
  Engineer declares busbar rating 200A but sum of way loads × diversity = 230A.
  Generator must either:
  (a) Emit busbar.rating_a = 250 (next standard rating up) AND flag the engineer
      override in compliance_summary.non_compliance_flags, OR
  (b) Accept the 200A only with a critical flag "BUSBAR_UNDERSIZED".
  Silently accepting 200A is a FAIL.

inputs:
  jurisdiction: "GB"
  board_type: "distribution_board"
  db_designation: "DB-X1"
  location: "test fixture"
  fed_from: "MSB-01"
  supply_voltage_v: "400"
  phase_arrangement: "TPN"
  supply_rating_a: 200
  busbar_rating_a_declared: 200
  ways_total: 12
  form_separation_iec61439: "2a"
  circuits_declared:
    - { id: "C01", designation: "Trap load 1", ocpd_rating_a: 80, ocpd_curve: "C", ocpd_type: "MCCB", load_kw: 50 }
    - { id: "C02", designation: "Trap load 2", ocpd_rating_a: 80, ocpd_curve: "C", ocpd_type: "MCCB", load_kw: 50 }
    - { id: "C03", designation: "Trap load 3", ocpd_rating_a: 80, ocpd_curve: "C", ocpd_type: "MCCB", load_kw: 50 }
    - { id: "C04", designation: "Trap load 4", ocpd_rating_a: 50, ocpd_curve: "C", ocpd_type: "MCCB", load_kw: 30 }
  diversity_factor_main: 0.85

assertions:
  - kind: schema_valid
    schema: "db-layout-ir.schema.json"
  - kind: any_one_of_must_be_true
    options:
      - condition: "$.busbar.rating_a >= 250"
        note: "Generator chose next-rating-up"
      - condition: "any(f.message contains 'BUSBAR' for f in $.compliance_summary.non_compliance_flags)"
        note: "Generator flagged the undersize"
  - kind: jsonpath_not_equals
    path: "$.busbar.rating_a"
    forbidden: 200
    note_if_violated: "Generator silently accepted the trap input — critical fail"
  - kind: invariant_passes
    invariant: "INV-3"
    note: "Busbar rating coverage"

expected_status: "pass"
```

- [ ] **Step 2: Validate**

```bash
python3 -c "
import yaml
e = yaml.safe_load(open('electrical/db-layout/evals/eval-03-undersized-busbar-trap.yaml'))
assert e['category'] == 'validation_trap'
print('Eval-03: OK')
"
```

- [ ] **Step 3: Commit**

```bash
git add electrical/db-layout/evals/eval-03-undersized-busbar-trap.yaml
git commit -m "feat: db-layout eval-03 undersized-busbar validation trap"
```

---

## Task 18: Create `evals/eval-04-missing-fault-current.yaml`

**Files:**
- Create: `electrical/db-layout/evals/eval-04-missing-fault-current.yaml`

- [ ] **Step 1: Write the eval**

```yaml
# Eval 04 — No fault-level intent + no engineer Ifault — selectivity must defer, not invent
# Category: missing_input

id: eval-04-missing-fault-current
category: missing_input
severity: high
description: |
  Engineer has not declared fault currents, fault-level intent is absent.
  Generator must NOT invent values. Every selectivity_results entry must:
  (a) Set source = "tool_call_pending", AND
  (b) Set tool_call_pending = true, AND
  (c) The top-level flags array must include "TOOL-CALL-PENDING".

inputs:
  jurisdiction: "EU"
  board_type: "distribution_board"
  db_designation: "DB-EU1"
  location: "EU test installation"
  fed_from: "MSB-01"
  supply_voltage_v: "400"
  phase_arrangement: "TPN"
  supply_rating_a: 250
  ways_total: 18
  form_separation_iec61439: "3a"
  circuits_declared:
    - { id: "C01", designation: "Office lighting", ocpd_rating_a: 16, ocpd_curve: "B", ocpd_type: "MCB", phase_csa_mm2: 2.5, length_m: 30, load_kw: 3 }
    - { id: "C02", designation: "Office receptacles", ocpd_rating_a: 20, ocpd_curve: "C", ocpd_type: "MCB", phase_csa_mm2: 2.5, length_m: 35, load_kw: 4 }
  # No fault_currents_engineer_declared
  # No cross_drawing_context.fault-level

assertions:
  - kind: schema_valid
    schema: "db-layout-ir.schema.json"
  - kind: jsonpath_all_equals
    path: "$.selectivity_results[*].source"
    expected: "tool_call_pending"
  - kind: jsonpath_all_equals
    path: "$.selectivity_results[*].tool_call_pending"
    expected: true
  - kind: jsonpath_contains
    path: "$.flags"
    must_contain: "TOOL-CALL-PENDING"
  - kind: invariant_passes
    invariant: "INV-9"
    note: "Selectivity result completeness via tool_call_pending"

expected_status: "pass"
```

- [ ] **Step 2: Validate**

```bash
python3 -c "
import yaml
e = yaml.safe_load(open('electrical/db-layout/evals/eval-04-missing-fault-current.yaml'))
assert e['category'] == 'missing_input'
print('Eval-04: OK')
"
```

- [ ] **Step 3: Commit**

```bash
git add electrical/db-layout/evals/eval-04-missing-fault-current.yaml
git commit -m "feat: db-layout eval-04 missing-fault-current (selectivity must defer, not invent)"
```

---

## Task 19: Create `evals/eval-05-jurisdiction-us-panelboard.yaml`

**Files:**
- Create: `electrical/db-layout/evals/eval-05-jurisdiction-us-panelboard.yaml`

- [ ] **Step 1: Write the eval**

```yaml
# Eval 05 — US strip mall panelboard, NEC Art 408
# Category: jurisdiction_switch

id: eval-05-jurisdiction-us-panelboard
category: jurisdiction_switch
severity: critical
description: |
  US 200A 120/240V split-phase NEMA panelboard for a strip-mall retail fit-out.
  Must:
  (a) Use NEMA enclosure type (not IEC Form code)
  (b) Reference NFPA 70 Art 408 + Art 240 (not BS 7671 / IEC 60364)
  (c) Size by NEC table values (Table 220 for load, Table 250.122 for EGC)
  (d) Use GFCI/AFCI terminology, not RCD

inputs:
  jurisdiction: "US"
  board_type: "panelboard_nema"
  db_designation: "PB-1"
  location: "back-of-house service room"
  fed_from: "MAIN"
  supply_voltage_v: "240"
  phase_arrangement: "single_phase_split"
  supply_rating_a: 200
  ze_ohm_at_origin: 0.20
  ways_total: 24
  ip_rating: "NEMA_1"
  circuits_declared:
    - { id: "C01", designation: "General lighting", ocpd_rating_a: 20, ocpd_type: "MCB", phase_csa_awg: "12", length_m: 25, load_kw: 1.5 }
    - { id: "C02", designation: "General receptacles", ocpd_rating_a: 20, ocpd_type: "MCB", phase_csa_awg: "12", length_m: 30, load_kw: 1.5 }
    - { id: "C03", designation: "Reach-in cooler dedicated", ocpd_rating_a: 30, ocpd_type: "MCB", phase_csa_awg: "10", length_m: 18, load_kw: 3 }
    - { id: "C04", designation: "RTU HVAC unit", ocpd_rating_a: 60, ocpd_type: "MCCB", phase_csa_awg: "6", length_m: 35, load_kw: 11 }
  diversity_factor_main: 0.8

assertions:
  - kind: schema_valid
    schema: "db-layout-ir.schema.json"
  - kind: jsonpath_equals
    path: "$.jurisdiction"
    expected: "US"
  - kind: jsonpath_present
    path: "$.board.enclosure_form_nec_type"
    note: "US must use NEMA type, not IEC Form"
  - kind: jsonpath_absent
    path: "$.board.enclosure_form_iec61439"
    note: "US must NOT emit IEC Form code"
  - kind: clause_cited
    clause_pattern: "^NEC 2023 Art (408|240|220|250)"
    minimum_count: 2
  - kind: clause_not_cited
    clause_pattern: "^BS 7671"
    note: "US project must not cite UK regs"
  - kind: clause_not_cited
    clause_pattern: "^IEC 60364"
    note: "US project must not cite IEC 60364"

expected_status: "pass"
```

- [ ] **Step 2: Validate**

```bash
python3 -c "
import yaml
e = yaml.safe_load(open('electrical/db-layout/evals/eval-05-jurisdiction-us-panelboard.yaml'))
assert e['category'] == 'jurisdiction_switch'
print('Eval-05: OK')
"
```

- [ ] **Step 3: Commit**

```bash
git add electrical/db-layout/evals/eval-05-jurisdiction-us-panelboard.yaml
git commit -m "feat: db-layout eval-05 jurisdiction-switch US NEC panelboard"
```

---

## Task 20: Create `evals/eval-06-rationale-block.yaml`

**Files:**
- Create: `electrical/db-layout/evals/eval-06-rationale-block.yaml`

- [ ] **Step 1: Write the eval**

```yaml
# Eval 06 — Rationale block must be present and substantive
# Category: rationale_block

id: eval-06-rationale-block
category: rationale_block
severity: high
description: |
  Reuses eval-01 happy-path scenario but targets the rationale block specifically.
  Per WI2 the rationale block is mandatory and must contain 9 sections + chat_summary
  + decisions with clause citations.

inputs:
  reuse_eval: "eval-01-uk-domestic-cu-tn-cs"

assertions:
  - kind: schema_valid
    schema: "db-layout-ir.schema.json"
  - kind: jsonpath_present
    path: "$.rationale.chat_summary"
  - kind: jsonpath_length_gte
    path: "$.rationale.chat_summary"
    minimum: 40
    maximum: 500
    note: "Per rationale schema constraint"
  - kind: jsonpath_count_gte
    path: "$.rationale.sections[*]"
    minimum: 9
    note: "9 sections per Step 13 of generator"
  - kind: jsonpath_all_present
    path: "$.rationale.sections[*].title"
  - kind: jsonpath_all_present
    path: "$.rationale.sections[*].summary"
  - kind: jsonpath_pattern_match
    path: "$.rationale.sections[*].decisions[*].code_clause"
    pattern: "^(BS 7671:2018\\+A3|IEC 60364-[0-9]+-[0-9]+|IEC 61439-[0-9]+|NEC 2023)"
    note: "Citations must use canonical format"
  - kind: jsonpath_count_gte
    path: "$.rationale.sections[?(@.title=='OCPD Selection')].decisions[*]"
    minimum: 1
    note: "OCPD Selection section must have at least one decision"

expected_status: "pass"
```

- [ ] **Step 2: Validate**

```bash
python3 -c "
import yaml
e = yaml.safe_load(open('electrical/db-layout/evals/eval-06-rationale-block.yaml'))
assert e['category'] == 'rationale_block'
print('Eval-06: OK')
"
```

- [ ] **Step 3: Commit**

```bash
git add electrical/db-layout/evals/eval-06-rationale-block.yaml
git commit -m "feat: db-layout eval-06 rationale block (9 sections + chat_summary per WI2)"
```

---

## Task 21: Create `evals/eval-07-selectivity-cascade.yaml`

**Files:**
- Create: `electrical/db-layout/evals/eval-07-selectivity-cascade.yaml`

- [ ] **Step 1: Write the eval**

```yaml
# Eval 07 — Two-level cascade selectivity verification
# Category: skill_specific (selectivity_cascade)

id: eval-07-selectivity-cascade
category: skill_specific
severity: high
description: |
  MSB 1000A ACB main → 250A MCCB feeder → 32A MCB final.
  Engineer-declared fault currents:
  - At MSB busbar: 35 kA
  - At sub-DB busbar: 25 kA
  - At final circuit: 6 kA
  Generator must emit selectivity_results entries for all three cascade pairs and
  verify cascade is "selective_to_fault_ka" for each (using manufacturer table source).

inputs:
  jurisdiction: "GB"
  board_type: "main_switchboard"
  db_designation: "MSB-CASC"
  location: "switchroom"
  fed_from: "MAIN"
  supply_voltage_v: "400"
  phase_arrangement: "TPN"
  supply_rating_a: 1000
  ze_ohm_at_origin: 0.03
  ways_total: 12
  form_separation_iec61439: "4a"
  circuits_declared:
    - { id: "F01", designation: "Feeder to DB-1", ocpd_rating_a: 250, ocpd_curve: "D", ocpd_type: "MCCB", phase_csa_mm2: 150, length_m: 30, load_kw: 120 }
    - { id: "C01", designation: "Final 32A circuit at DB-1", ocpd_rating_a: 32, ocpd_curve: "C", ocpd_type: "MCB", phase_csa_mm2: 6, length_m: 25, load_kw: 6, upstream_ocpd: "F01" }
  fault_currents_engineer_declared:
    - { circuit_id: "MAIN-BUSBAR", ifault_ka: 35 }
    - { circuit_id: "F01", ifault_ka: 25 }
    - { circuit_id: "C01", ifault_ka: 6 }

assertions:
  - kind: schema_valid
    schema: "db-layout-ir.schema.json"
  - kind: jsonpath_count_gte
    path: "$.selectivity_results[*]"
    minimum: 2
    note: "At least MAIN→F01 and F01→C01 cascade pairs"
  - kind: jsonpath_all_in
    path: "$.selectivity_results[*].source"
    allowed: ["manufacturer_table", "iec_60909_calc", "engineer_declared"]
    note: "All cascades resolved (no tool_call_pending since fault currents given)"
  - kind: jsonpath_all_present
    path: "$.selectivity_results[*].selective_to_fault_ka"
    note: "Every cascade has a verdict"
  - kind: invariant_passes
    invariant: "INV-9"
    note: "Selectivity result completeness"

expected_status: "pass"
```

- [ ] **Step 2: Validate**

```bash
python3 -c "
import yaml
e = yaml.safe_load(open('electrical/db-layout/evals/eval-07-selectivity-cascade.yaml'))
assert e['category'] == 'skill_specific'
print('Eval-07: OK')
"
```

- [ ] **Step 3: Commit**

```bash
git add electrical/db-layout/evals/eval-07-selectivity-cascade.yaml
git commit -m "feat: db-layout eval-07 selectivity cascade (skill_specific)"
```

---

## Task 22: Create `evals/eval-08-intent-rollup-shape.yaml`

**Files:**
- Create: `electrical/db-layout/evals/eval-08-intent-rollup-shape.yaml`

- [ ] **Step 1: Write the eval**

```yaml
# Eval 08 — Rollup intent shape must satisfy earthing skill's existing expectation
# Category: skill_specific (intent_rollup_shape)

id: eval-08-intent-rollup-shape
category: skill_specific
severity: critical
description: |
  Reuses eval-01 inputs but specifically validates that the emitted db-layout-rollup
  intent payload is structurally compatible with what electrical/earthing examples
  declare as their consumed_intent for db-layout.

  Verifies the cross-skill contract is intact — drift here breaks earthing.

inputs:
  reuse_eval: "eval-01-uk-domestic-cu-tn-cs"

assertions:
  - kind: emitted_intent_validates
    intent_type: "db-layout-rollup"
    schema: "db-layout-rollup-intent.schema.json"
  - kind: emitted_intent_field_present
    intent_type: "db-layout-rollup"
    path: "$.project_id"
  - kind: emitted_intent_field_present
    intent_type: "db-layout-rollup"
    path: "$.boards[*].id"
  - kind: emitted_intent_field_present
    intent_type: "db-layout-rollup"
    path: "$.boards[*].main_switch_rating_a"
  - kind: emitted_intent_field_present
    intent_type: "db-layout-rollup"
    path: "$.outgoing_circuits[*].id"
  - kind: emitted_intent_field_present
    intent_type: "db-layout-rollup"
    path: "$.outgoing_circuits[*].ocpd_rating_a"
  - kind: emitted_intent_field_present
    intent_type: "db-layout-rollup"
    path: "$.outgoing_circuits[*].ocpd_type"
  - kind: cross_skill_compatibility_check
    consumer_skill: "electrical/earthing"
    consumer_example: "electrical/earthing/examples/uk-dwelling-tn-cs/input.json"
    consumer_field_path: "consumed_intents[?(@.intent_type=='db-layout')].payload"
    note: "Earthing example's expected db-layout payload shape must structurally match the emitted rollup intent"

expected_status: "pass"
```

- [ ] **Step 2: Validate all 8 evals exist + registered**

```bash
python3 -c "
import json, os
rc = json.load(open('electrical/db-layout/evals/runner-config.json'))
listed = set(rc['evals'])
on_disk = set(f for f in os.listdir('electrical/db-layout/evals/') if f.startswith('eval-'))
missing = listed - on_disk
extra = on_disk - listed
assert not missing
assert not extra
print(f'All {len(listed)} evals exist and registered')
"
```
Expected: `All 8 evals exist and registered`

- [ ] **Step 3: Commit**

```bash
git add electrical/db-layout/evals/eval-08-intent-rollup-shape.yaml
git commit -m "feat: db-layout eval-08 intent-rollup-shape (cross-skill contract verification)"
```

---

## Task 23: Create example 1 — UK domestic consumer unit

**Files:**
- Create: `electrical/db-layout/examples/uk-domestic-consumer-unit/input.json`
- Create: `electrical/db-layout/examples/uk-domestic-consumer-unit/reasoning.md`
- Create: `electrical/db-layout/examples/uk-domestic-consumer-unit/output.json`

This example pairs to eval-01 (UK domestic CU). The output IR is the **per-board IR**; the project rollup intent is embedded alongside in the same output (see notes in generator.md Final output).

- [ ] **Step 1: Write `input.json`** (reuses eval-01 inputs verbatim with project_meta added)

```json
{
  "$schema": "../../inputs.json",
  "project_meta": {
    "project_id": "uk-dom-cu-eg01",
    "name": "23 Elm Crescent — 3-bed Semi",
    "client": "Private",
    "designer": "DraftsMan Skills demo",
    "date": "2026-05-15",
    "revision": "P01"
  },
  "jurisdiction": "GB",
  "board_type": "consumer_unit",
  "db_designation": "CU-G",
  "location": "consumer unit cupboard, ground floor hallway",
  "fed_from": "MAIN",
  "supply_voltage_v": "230",
  "phase_arrangement": "single_phase",
  "supply_rating_a": 100,
  "ze_ohm_at_origin": 0.35,
  "ways_total": 12,
  "ways_spare_minimum": 2,
  "form_separation_iec61439": "1",
  "ip_rating": "IP2X",
  "diversity_factor_main": 0.4,
  "rcd_type_default": "A",
  "circuits_declared": [
    { "id": "C01", "designation": "Ground floor lighting", "ocpd_rating_a": 6, "ocpd_curve": "B", "ocpd_type": "MCB", "rcd_protected": true, "rcd_sensitivity_ma": 30, "phase_csa_mm2": 1.5, "length_m": 18, "load_kw": 0.8, "voltage_class": "LV_power" },
    { "id": "C02", "designation": "First floor lighting", "ocpd_rating_a": 6, "ocpd_curve": "B", "ocpd_type": "MCB", "rcd_protected": true, "rcd_sensitivity_ma": 30, "phase_csa_mm2": 1.5, "length_m": 22, "load_kw": 0.7, "voltage_class": "LV_power" },
    { "id": "C03", "designation": "Ground floor sockets ring", "ocpd_rating_a": 32, "ocpd_curve": "B", "ocpd_type": "MCB", "rcd_protected": true, "rcd_sensitivity_ma": 30, "phase_csa_mm2": 2.5, "length_m": 38, "load_kw": 5.0, "voltage_class": "LV_power" },
    { "id": "C04", "designation": "First floor sockets ring", "ocpd_rating_a": 32, "ocpd_curve": "B", "ocpd_type": "MCB", "rcd_protected": true, "rcd_sensitivity_ma": 30, "phase_csa_mm2": 2.5, "length_m": 42, "load_kw": 4.0, "voltage_class": "LV_power" },
    { "id": "C05", "designation": "Cooker radial", "ocpd_rating_a": 32, "ocpd_curve": "B", "ocpd_type": "MCB", "rcd_protected": true, "rcd_sensitivity_ma": 30, "phase_csa_mm2": 6.0, "length_m": 14, "load_kw": 7.5, "voltage_class": "LV_power" },
    { "id": "C06", "designation": "Bathroom shower", "ocpd_rating_a": 40, "ocpd_curve": "B", "ocpd_type": "MCB", "rcd_protected": true, "rcd_sensitivity_ma": 30, "phase_csa_mm2": 10.0, "length_m": 16, "load_kw": 9.0, "voltage_class": "LV_power" }
  ]
}
```

- [ ] **Step 2: Write `reasoning.md`**

```markdown
# Reasoning — UK Domestic Consumer Unit (TN-C-S)

## Step 1 — Discovery check
Inputs all present. No `cross_drawing_context` (no fault-level intent supplied). Single-board project — emit one IR + a rollup intent with this one board.

## Step 2 — Standards files loaded (GB)
- `shared/standards/electrical/BS7671/reg433-overcurrent-protection.json`
- `shared/standards/electrical/BS7671/reg434-fault-current.json`
- `shared/standards/electrical/BS7671/reg443-spd.json`
- `shared/standards/electrical/BS7671/reg411-rcd-requirements.json`
- `shared/standards/electrical/BS7671/appendix3-device-curves.json`
- `shared/standards/electrical/BS7671/diversity-factors.json`
- `shared/standards/electrical/IEC60617/symbol-index.json`
- `shared/standards/electrical/IEC60617/part7-switchgear.json`
- `shared/standards/electrical/IEC61439/form-separations.json`
- `shared/standards/electrical/IEC61439/ip-ik-ratings.json`
- `shared/standards/electrical/IEC61439/short-circuit-withstand.json`

(IEC 60364 and NFPA 70 files NOT loaded — jurisdiction filters them out.)

## Step 3 — Board classification
- consumer_unit (UK domestic)
- IEC 61439-3 DBO assembly; Form 1
- IP2X (indoor dry — under-stair cupboard)
- Ways: 12 total

## Step 4 — Incoming supply
230V single-phase, 100A main switch, fed from MAIN, Ze 0.35 Ω (DNO declared PME).

## Step 5 — Busbar sizing
Sum of way loads: 0.8 + 0.7 + 5.0 + 4.0 + 7.5 + 9.0 = 27 kW = ~117A at 230V.
With diversity 0.4: 47A. Standard 100A busbar adequate.
IcW: 6 kA per typical consumer unit (BS EN 60439 / IEC 61439-3 DBO).

## Step 6 — Way assignment
6 circuits = 6 ways used (all single-pole MCBs). 6 ways spare. Meets minimum 2.

## Step 7 — OCPD per circuit
All MCBs Type B (domestic standard). Coordination check:
- C01 (6A on 1.5mm²): Iz=14A after grouping correction → 6 ≤ 14 ✓
- C03 (32A on 2.5mm² ring): special ring formula — Iz_effective ≈ 20A from each leg, 32A total ✓
- C06 (40A on 10mm²): Iz=57A → 40 ≤ 57 ✓
Icn 6 kA exceeds typical TN-C-S fault current 1-3 kA at this point.

## Step 8 — RCD assignment
All 6 circuits RCBO-protected via consumer unit's main 30mA RCD. Per BS 7671 411.3.3 + Section 701 (bathroom).

## Step 9 — Cable selection
Cables already provided in inputs. No upstream lighting/small-power intent to consume.

## Step 10 — DB face schematic
Symbols: `BUSBAR`, `MAIN_SWITCH`, `RCD_GROUP`, `MCB` (×6), `EARTH_GENERAL`.

## Step 11 — Selectivity verification
Cascade pairs to verify:
- MAIN → C01 ... C06 (each MCB downstream of the 100A main isolator)
Engineer Ifault not declared, fault-level intent not present → emit `tool_call_pending: true` for all selectivity_results entries.
Top-level flags includes `TOOL-CALL-PENDING`.

## Step 12 — Compliance flags
- INFO: Selectivity verification pending fault-level intent / engineer Ifault declaration
- None critical

## Step 13 — Rationale block
9-section taxonomy emitted with BS 7671 / IEC 61439 citations. See output.json.

## Project rollup intent (alongside per-board IR)
Single-board project — rollup contains just CU-G plus the 6 outgoing_circuits.
```

- [ ] **Step 3: Write `output.json`**

```json
{
  "$schema": "../../schemas/db-layout-ir.schema.json",
  "drawing_type": "db_layout_schedule_and_schematic",
  "version": "1.0.0",
  "meta": {
    "project_id": "uk-dom-cu-eg01",
    "skill_version": "db-layout/1.0.0",
    "produced_at": "2026-05-15T12:00:00Z",
    "consumed_intents": []
  },
  "jurisdiction": "GB",
  "board": {
    "db_id": "CU-G",
    "designation": "Main Consumer Unit",
    "location": "consumer unit cupboard, ground floor hallway",
    "enclosure_form_iec61439": "1",
    "ip_rating": "IP2X",
    "ways_total": 12,
    "ways_used": 6,
    "ways_spare": 6
  },
  "incoming": {
    "voltage_v": 230,
    "phase_arrangement": "single_phase",
    "supply_rating_a": 100,
    "fed_from": "MAIN",
    "supply_class": "non_essential",
    "ze_ohm_at_origin": 0.35
  },
  "busbar": {
    "rating_a": 100,
    "icw_ka_1s": 6,
    "ipk_ka": 7.5
  },
  "circuits": [
    { "circuit_id": "C01", "way_module_id": "W1", "designation": "Ground floor lighting", "voltage_class": "LV_power", "downstream_load_kw": 0.8, "ocpd": { "rating_a": 6, "curve": "B", "type": "MCB", "breaking_capacity_ka": 6 }, "rcd": { "required": true, "type": "A", "sensitivity_ma": 30 }, "cable": { "csa_mm2_or_awg": "1.5mm²", "cores": 3, "length_m": 18 } },
    { "circuit_id": "C02", "way_module_id": "W2", "designation": "First floor lighting", "voltage_class": "LV_power", "downstream_load_kw": 0.7, "ocpd": { "rating_a": 6, "curve": "B", "type": "MCB", "breaking_capacity_ka": 6 }, "rcd": { "required": true, "type": "A", "sensitivity_ma": 30 }, "cable": { "csa_mm2_or_awg": "1.5mm²", "cores": 3, "length_m": 22 } },
    { "circuit_id": "C03", "way_module_id": "W3", "designation": "Ground floor sockets ring", "voltage_class": "LV_power", "downstream_load_kw": 5.0, "ocpd": { "rating_a": 32, "curve": "B", "type": "MCB", "breaking_capacity_ka": 6 }, "rcd": { "required": true, "type": "A", "sensitivity_ma": 30 }, "cable": { "csa_mm2_or_awg": "2.5mm²", "cores": 3, "length_m": 38 } },
    { "circuit_id": "C04", "way_module_id": "W4", "designation": "First floor sockets ring", "voltage_class": "LV_power", "downstream_load_kw": 4.0, "ocpd": { "rating_a": 32, "curve": "B", "type": "MCB", "breaking_capacity_ka": 6 }, "rcd": { "required": true, "type": "A", "sensitivity_ma": 30 }, "cable": { "csa_mm2_or_awg": "2.5mm²", "cores": 3, "length_m": 42 } },
    { "circuit_id": "C05", "way_module_id": "W5", "designation": "Cooker radial", "voltage_class": "LV_power", "downstream_load_kw": 7.5, "ocpd": { "rating_a": 32, "curve": "B", "type": "MCB", "breaking_capacity_ka": 6 }, "rcd": { "required": true, "type": "A", "sensitivity_ma": 30 }, "cable": { "csa_mm2_or_awg": "6mm²", "cores": 3, "length_m": 14 } },
    { "circuit_id": "C06", "way_module_id": "W6", "designation": "Bathroom shower", "voltage_class": "LV_power", "downstream_load_kw": 9.0, "ocpd": { "rating_a": 40, "curve": "B", "type": "MCB", "breaking_capacity_ka": 6 }, "rcd": { "required": true, "type": "A", "sensitivity_ma": 30 }, "cable": { "csa_mm2_or_awg": "10mm²", "cores": 3, "length_m": 16 } }
  ],
  "selectivity_results": [
    { "upstream_id": "MAIN", "downstream_id": "C01", "source": "tool_call_pending", "tool_call_pending": true, "code_clause": "BS 7671:2018+A3 Reg 536" },
    { "upstream_id": "MAIN", "downstream_id": "C02", "source": "tool_call_pending", "tool_call_pending": true, "code_clause": "BS 7671:2018+A3 Reg 536" },
    { "upstream_id": "MAIN", "downstream_id": "C03", "source": "tool_call_pending", "tool_call_pending": true, "code_clause": "BS 7671:2018+A3 Reg 536" },
    { "upstream_id": "MAIN", "downstream_id": "C04", "source": "tool_call_pending", "tool_call_pending": true, "code_clause": "BS 7671:2018+A3 Reg 536" },
    { "upstream_id": "MAIN", "downstream_id": "C05", "source": "tool_call_pending", "tool_call_pending": true, "code_clause": "BS 7671:2018+A3 Reg 536" },
    { "upstream_id": "MAIN", "downstream_id": "C06", "source": "tool_call_pending", "tool_call_pending": true, "code_clause": "BS 7671:2018+A3 Reg 536" }
  ],
  "compliance_summary": {
    "compliant": true,
    "non_compliance_flags": [],
    "assumptions": [
      "Diversity factor 0.4 (domestic typical per BS 7671 Appendix 1).",
      "Selectivity verification deferred — fault-level intent absent and engineer Ifault not declared per WI3.",
      "Cable ampacity check assumes BS 7671 Appendix 4 Reference Method C (clipped direct)."
    ]
  },
  "drawn_as_symbols": ["BUSBAR", "MAIN_SWITCH", "RCD_GROUP", "MCB", "EARTH_GENERAL"],
  "flags": ["TOOL-CALL-PENDING"],
  "rationale": {
    "chat_summary": "100A TN-C-S consumer unit for a UK 3-bed semi, 12-way Form 1 Hager-style enclosure. 6 final circuits all RCBO-protected via the main 30mA RCD. Busbar 100A IcW 6kA accommodates 47A diversified load. Selectivity verification pending fault-level intent — emitted as tool_call_pending per WI3. Reply to refine, e.g. 'add EV charger'.",
    "sections": [
      { "title": "Board Classification", "summary": "UK domestic consumer unit, IEC 61439-3 DBO Form 1, IP2X for indoor cupboard installation.", "decisions": [ { "label": "Form 1 enclosure", "summary": "Standard for domestic CUs — no separation between busbar and functional units required at this rating.", "rule": "IEC 61439-3 DBO assembly", "code_clause": "IEC 61439-3:2012 clause 7.1", "inputs": { "board_type": "consumer_unit", "form": "1" } } ] },
      { "title": "Incoming Supply", "summary": "230V single-phase 100A main switch from PME supply (Ze 0.35Ω declared).", "decisions": [ { "label": "100A main switch", "summary": "Standard UK domestic main switch rating.", "rule": "DNO service rating", "code_clause": "BS 7671:2018+A3 Reg 132.16", "inputs": { "supply_rating_a": 100 } } ] },
      { "title": "Busbar Sizing", "summary": "100A busbar, IcW 6kA. Sum of way loads ~117A → 47A diversified at 0.4 → 100A busbar adequate with headroom.", "decisions": [ { "label": "100A busbar adequate", "summary": "47A diversified load × 1.5 future expansion factor fits 100A.", "rule": "IEC 61439-1 rated current of assembly", "code_clause": "IEC 61439-3:2012 clause 5.3", "inputs": { "busbar_a": 100, "diversified_a": 47 } } ] },
      { "title": "Way Assignment", "summary": "6 ways used (W1–W6), 6 ways spare. Meets engineer-specified minimum 2.", "decisions": [] },
      { "title": "OCPD Selection", "summary": "All MCBs Type B (domestic standard). In ≤ Iz verified for every circuit. Icn 6kA exceeds prospective fault current.", "decisions": [ { "label": "Type B curve for all circuits", "summary": "Domestic loads (lighting, sockets, cooker, shower) have no significant inrush.", "rule": "BS 7671 Appendix 3 — Type B for general lighting/socket loads", "code_clause": "BS 7671:2018+A3 Appendix 3", "inputs": { "curve": "B" } } ] },
      { "title": "RCD Strategy", "summary": "All 6 final circuits 30mA RCBO-protected via main RCD. Per BS 7671 411.3.3 (sockets ≤32A in domestic) + Section 701 (bathroom shower).", "decisions": [ { "label": "30mA Type A RCD on every circuit", "summary": "Type A handles AC + pulsating DC residual — covers modern electronics.", "rule": "BS 7671 Reg 411.3.3", "code_clause": "BS 7671:2018+A3 Reg 411.3.3", "inputs": { "rcd_type": "A", "sensitivity_ma": 30 } } ] },
      { "title": "Cable Selection", "summary": "Cables provided in inputs (twin-and-earth 6242Y typical). All sizes pass In ≤ Iz check at Reference Method C.", "decisions": [] },
      { "title": "Selectivity Verification", "summary": "6 cascade pairs (MAIN → each MCB) emitted as tool_call_pending. fault-level intent absent; engineer Ifault not declared. Will re-emit once fault-level skill ships.", "decisions": [ { "label": "All cascades tool_call_pending", "summary": "Per WI3 deferral pattern.", "rule": "BS 7671 Reg 536 / IEC 60364-5-53", "code_clause": "BS 7671:2018+A3 Reg 536", "inputs": { "tool_call_pending": true } } ] },
      { "title": "Compliance", "summary": "Compliant. One TOOL-CALL-PENDING flag for deferred selectivity.", "decisions": [] }
    ]
  }
}
```

- [ ] **Step 4: Validate output IR against schema**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills" && \
python3 - <<'PY'
import json
from jsonschema import Draft7Validator
ir_schema = json.load(open('electrical/db-layout/schemas/db-layout-ir.schema.json'))
rationale_schema = json.load(open('shared/schemas/core/rationale.schema.json'))
ir_no_id = dict(ir_schema)
ir_no_id.pop('$id', None)
ir_no_id['properties']['rationale'] = rationale_schema
v = Draft7Validator(ir_no_id)
out = json.load(open('electrical/db-layout/examples/uk-domestic-consumer-unit/output.json'))
errors = list(v.iter_errors(out))
if errors:
    for e in errors[:8]:
        print(f'  ERR @ {"/".join(str(p) for p in e.absolute_path)}: {e.message}')
    print(f'TOTAL: {len(errors)}')
else:
    print('Example 1 IR schema-valid')
PY
```
Expected: `Example 1 IR schema-valid`

- [ ] **Step 5: Commit**

```bash
git add electrical/db-layout/examples/uk-domestic-consumer-unit/
git commit -m "feat: db-layout example 1 — UK domestic consumer unit (schema-conformant)"
```

---

## Task 24: Create example 2 — INT commercial TPN MSB

**Files:**
- Create: `electrical/db-layout/examples/intl-commercial-tpn-msb/input.json`
- Create: `electrical/db-layout/examples/intl-commercial-tpn-msb/reasoning.md`
- Create: `electrical/db-layout/examples/intl-commercial-tpn-msb/output.json`

Follow Task 23's pattern. Differences from Example 1:

**input.json:** jurisdiction "INT", board_type "main_switchboard", supply_voltage_v "400", phase_arrangement "TPN", supply_rating_a 800, form_separation_iec61439 "4b", 4 feeder circuits to sub-DBs, engineer-declared fault currents (because it's commercial and the engineer has run a load study).

**reasoning.md:** Standards loaded are IEC 60364 family + IEC 61439 + IEC 60617 (no BS 7671, no NFPA 70). Step 11 uses engineer-declared Ifault values; selectivity_results emit source = "engineer_declared" (NOT tool_call_pending since values are present).

**output.json:** earthing_system equivalent here is irrelevant (db-layout doesn't carry earthing_system in IR), but jurisdiction MUST be "INT". IR has 4 circuits all MCCB (commercial), busbar 800A IcW 36kA, Form 4b (full compartmentalisation).

- [ ] **Step 1: Write `input.json`** (use eval-02 structure verbatim with project_meta added; jurisdiction = INT instead of GB)

[Engineer: copy eval-02-tpn-commercial-msb.yaml's `inputs` block; add `project_meta` similar to Task 23; set jurisdiction "INT".]

- [ ] **Step 2: Write `reasoning.md`** (9 steps × few lines each; cite IEC 60364 + IEC 61439 clauses verbatim)

- [ ] **Step 3: Write `output.json`** (full IR per the schema)

Key fields to populate:
- `jurisdiction: "INT"`
- `board.enclosure_form_iec61439: "4b"`
- `board.ip_rating: "IP30"`
- `incoming.voltage_v: 400`, `incoming.phase_arrangement: "TPN"`, `incoming.supply_rating_a: 800`
- `busbar.rating_a: 800`, `busbar.icw_ka_1s: 36`, `busbar.ipk_ka: 80`
- 4 circuits with MCCB OCPD, breaking_capacity_ka >= 25
- 4 selectivity_results, source = "engineer_declared" with selective_to_fault_ka values
- Compliance flags: none critical
- Rationale: 9 sections; cite `IEC 60364-4-43 clause 433.1`, `IEC 61439-2:2020 clause 5.3`, `IEC 61439-1 clause 9.10` (busbar IcW)

- [ ] **Step 4: Validate**

Run the same schema validation idiom as Task 23 Step 4.

- [ ] **Step 5: Commit**

```bash
git add electrical/db-layout/examples/intl-commercial-tpn-msb/
git commit -m "feat: db-layout example 2 — INT commercial TPN MSB (Form 4b + engineer-declared cascade)"
```

---

## Task 25: Create example 3 — US strip-mall panelboard

**Files:**
- Create: `electrical/db-layout/examples/us-strip-mall-panelboard/input.json`
- Create: `electrical/db-layout/examples/us-strip-mall-panelboard/reasoning.md`
- Create: `electrical/db-layout/examples/us-strip-mall-panelboard/output.json`

Follow Task 23's pattern. Differences:

**input.json:** jurisdiction "US", board_type "panelboard_nema", supply_voltage_v "240", phase_arrangement "single_phase_split", ip_rating "NEMA_1", 4 circuits with AWG cable sizes.

**reasoning.md:** Standards loaded are NFPA 70 family + IEC 61439 (form-separations not strictly applicable for NEMA but IEC 60617 symbols still apply) + IEC 60617. NEC terminology throughout: panelboard not DB, EGC not CPC, GFCI not RCD.

**output.json:**
- `jurisdiction: "US"`
- `board.enclosure_form_nec_type: "NEMA_1"` (NOT `enclosure_form_iec61439`)
- `incoming.voltage_v: 240`, `incoming.phase_arrangement: "single_phase_split"`, `incoming.supply_rating_a: 200`
- 4 circuits with AWG cables (12 AWG, 10 AWG, 10 AWG, 6 AWG)
- Each circuit `cable.csa_mm2_or_awg: "12 AWG Cu"` etc.
- Selectivity_results all marked `source: "tool_call_pending"` (no fault-level given)
- Cite NEC 2023 Art 408 (panelboards), Art 240 (overcurrent), Art 220 (load calc), Art 250 (grounding/EGC)
- Rationale chat_summary uses NEC terminology (panelboard, EGC, GFCI)

- [ ] **Step 1: Write `input.json`**
- [ ] **Step 2: Write `reasoning.md`** (NEC clauses only — confirm no BS 7671 / IEC 60364 references)
- [ ] **Step 3: Write `output.json`**
- [ ] **Step 4: Validate IR schema + confirm NEC-only citations**

```bash
python3 - <<'PY'
import json
from jsonschema import Draft7Validator
ir_schema = json.load(open('electrical/db-layout/schemas/db-layout-ir.schema.json'))
rationale_schema = json.load(open('shared/schemas/core/rationale.schema.json'))
ir_no_id = dict(ir_schema)
ir_no_id.pop('$id', None)
ir_no_id['properties']['rationale'] = rationale_schema
out = json.load(open('electrical/db-layout/examples/us-strip-mall-panelboard/output.json'))
Draft7Validator(ir_no_id).validate(out)
print('US example schema-valid')

# Confirm no UK/IEC citations leaked
import json
text = json.dumps(out)
assert 'BS 7671' not in text, 'US example must not cite BS 7671'
assert 'IEC 60364' not in text, 'US example must not cite IEC 60364'
print('US example: NEC-only citations confirmed')
PY
```

- [ ] **Step 5: Commit**

```bash
git add electrical/db-layout/examples/us-strip-mall-panelboard/
git commit -m "feat: db-layout example 3 — US strip-mall NEMA panelboard (NEC-only)"
```

---

## Task 26: Rewrite `README.md`

**Files:**
- Rewrite: `electrical/db-layout/README.md`

Mirror the structure of `electrical/earthing/README.md` and `electrical/lighting-layout/README.md`.

- [ ] **Step 1: Read the reference READMEs**

```bash
cat electrical/earthing/README.md | head -50
cat electrical/lighting-layout/README.md | head -50
```

- [ ] **Step 2: Write the new README**

```markdown
# `db-layout` — Distribution Board Schedule + Schematic + Selectivity Generator

**Status:** `beta`
**Version:** `1.0.0`
**Drawing type:** `db_layout_schedule_and_schematic`
**Reference:** `electrical/lighting-layout` (production reference) + `electrical/earthing` (sibling beta — same pattern)

## What this skill produces

A single-board IR (Intermediate Representation) per distribution board, capturing:

- The board (consumer unit / DB / MSB / NEMA panelboard) — IEC 61439 form OR NEMA enclosure type
- Incoming supply specification (voltage / phase / supply rating / Ze)
- Busbar sizing (rating + IcW + Ipk)
- Way assignment (used / spare / multi-pole accounting)
- Circuit schedule (OCPD + RCD/GFCI + cable per circuit)
- IEC 60617 face one-line schematic symbol roll-up
- Cascade selectivity verification (manufacturer table OR IEC 60909 OR `tool_call_pending`)
- A structured `rationale` block per WI2 (9 sections + chat_summary)

**Plus a project-rollup intent** (`db-layout-rollup`) emitted alongside aggregating all boards in the project — this is what the `earthing` skill consumes.

This is **stage 1** of the db-layout skill — schedule + face schematic + selectivity. Plan-view DB location and DC distribution are deferred.

## Jurisdictions supported

| Jurisdiction | Primary standards | OCPD sizing | Selectivity reference |
|---|---|---|---|
| GB | BS 7671:2018+A3 + IEC 61439 | BS 7671 Reg 433 + Appendix 3 device curves | BS 7671 Reg 536 + manufacturer cascade tables |
| EU | IEC 60364 + IEC 61439 | IEC 60364-4-43 + IEC 60364 device curves | IEC 60364-5-53 + manufacturer cascade tables |
| INT | IEC 60364 + IEC 61439 | Same as EU | Same as EU |
| US | NFPA 70 Art 408 + 240 + 220 | NEC 240 OCPD coordination | NEC 240.12 + ocpd-coordination |

## Cross-drawing intent contract

| Direction | Intent | Purpose |
|---|---|---|
| Produces | `db-layout` | Single-board intent — consumed by `panel-schedule`, `riser`, `cable-containment` |
| Produces | `db-layout-rollup` | Project-rollup intent — consumed by `earthing` |
| Consumes | `fault-level` | Prospective fault currents at each cascade level (when that skill ships) |
| Consumes | `lighting-layout` | Lighting circuit loads + lengths (optional — alternative to engineer-input circuit data) |

## File structure

```
electrical/db-layout/
├── README.md
├── CHANGELOG.md
├── skill.manifest.json
├── inputs.json
├── prompts/
│   ├── generator.md      (13-step reasoning chain)
│   ├── validator.md      (11 INV invariants)
│   └── reviewer.md       (9 D dimensions)
├── schemas/
│   ├── db-layout-ir.schema.json
│   ├── db-layout-intent.schema.json          (single board)
│   └── db-layout-rollup-intent.schema.json   (project rollup — matches earthing's expected shape)
├── rules/                (4 YAMLs)
├── constraints/          (3 YAMLs)
├── validation/           (4 YAMLs — 14 deterministic checks)
├── ontology/             (2 JSONs: board-types, ocpd-types)
├── docs/                 (engineering-philosophy + known-limitations)
├── evals/                (runner-config + 8 evals)
└── examples/             (3 worked examples × 3 files each)
```

## Eval coverage matrix

| Eval ID | Category | Tests |
|---|---|---|
| eval-01-uk-domestic-cu-tn-cs | happy_path | 100A TN-C-S CU, 6 circuits, all RCD-protected |
| eval-02-tpn-commercial-msb | edge_case | 800A TPN MSB Form 4b + 4-way cascade |
| eval-03-undersized-busbar-trap | validation_trap | Generator must flag/correct undersized busbar |
| eval-04-missing-fault-current | missing_input | No Ifault → selectivity must defer, not invent |
| eval-05-jurisdiction-us-panelboard | jurisdiction_switch | NEMA panelboard, NEC Art 408, no BS 7671 citations |
| eval-06-rationale-block | rationale_block | 9-section rationale per WI2 |
| eval-07-selectivity-cascade | skill_specific | Two-level cascade with manufacturer-table verdicts |
| eval-08-intent-rollup-shape | skill_specific | Rollup intent matches earthing's expected shape verbatim |

All 6 WI5 categories + 2 skill-specific = 8 evals.

## Tool calls awaiting runtime

Per WI3, this skill declares — but defers — these calculation tools.

| Tool name | Purpose |
|---|---|
| `calc.iec60909_cascade` | Compute Ifault at each cascade level |
| `calc.diversity_factor` | Apply diversity factor from standards |

When `fault-level` skill ships + WI3 runtime tools land, selectivity_results entries currently emitted as `source: "tool_call_pending"` will be re-emitted as `source: "iec_60909_calc"` with computed `selective_to_fault_ka`.

## Known limitations

See `docs/known-limitations.md`. Stage 1 does NOT cover:
- Plan-view DB location drawing (stage 2)
- DC distribution (PV, EV chargepoints) — v1.1.0
- Live IEC 60909 calculation — deferred until `fault-level` skill ships
- MCC internal compartment detail
- Arc-flash hazard analysis (NFPA 70E / IEEE 1584)
- Generator + UPS transfer scheme coordination
- Voltage drop verification (separate `voltage-drop` / `cable-sizing` skill scope)

## Versioning

- **Minor bumps** (1.x.0) add new jurisdictions / examples / evals
- **Major bump** (2.0.0) reserved for stage 2 plan-view release
- **Patch bumps** (1.0.x) for rules / constraints / validation bug fixes

## License

See repository root `LICENSE`.
```

- [ ] **Step 3: Validate the README structure**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills" && \
python3 -c "
new = [l.strip() for l in open('electrical/db-layout/README.md') if l.startswith('## ')]
required = ['## What this skill produces', '## Jurisdictions supported', '## Cross-drawing intent contract', '## File structure', '## Eval coverage matrix', '## Tool calls awaiting runtime', '## Known limitations', '## Versioning']
for r in required:
    assert r in new, f'Missing section: {r}'
print(f'db-layout README: {len(new)} sections, all required present')
"
```

- [ ] **Step 4: Commit**

```bash
git add electrical/db-layout/README.md
git commit -m "docs: db-layout README rewrite — eval coverage + jurisdiction table + intent contracts"
```

---

## Task 27: Final verification + SKILLS_STATUS.md update

**Files:**
- Modify: `SKILLS_STATUS.md`
- Verify: All 43 files in `electrical/db-layout/`

- [ ] **Step 1: Run full file-count verification**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills" && \
python3 << 'PYEOF'
import os
root = 'electrical/db-layout'
expected = {
    'skill-level': ['README.md', 'CHANGELOG.md', 'skill.manifest.json', 'inputs.json'],
    'prompts': ['generator.md', 'validator.md', 'reviewer.md'],
    'schemas': ['db-layout-ir.schema.json', 'db-layout-intent.schema.json', 'db-layout-rollup-intent.schema.json'],
    'rules': ['ocpd-coordination.yaml', 'busbar-sizing.yaml', 'form-separation.yaml', 'rcd-grouping.yaml'],
    'constraints': ['breaker-breaking-capacity.yaml', 'busbar-icw.yaml', 'ip-rating-by-location.yaml'],
    'validation': ['ocpd-coordination.yaml', 'busbar-loading.yaml', 'selectivity-results.yaml', 'intent-rollup-shape.yaml'],
    'ontology': ['board-types.json', 'ocpd-types.json'],
    'docs': ['engineering-philosophy.md', 'known-limitations.md'],
    'evals': ['runner-config.json', 'eval-01-uk-domestic-cu-tn-cs.yaml', 'eval-02-tpn-commercial-msb.yaml', 'eval-03-undersized-busbar-trap.yaml', 'eval-04-missing-fault-current.yaml', 'eval-05-jurisdiction-us-panelboard.yaml', 'eval-06-rationale-block.yaml', 'eval-07-selectivity-cascade.yaml', 'eval-08-intent-rollup-shape.yaml'],
    'examples/uk-domestic-consumer-unit':   ['input.json', 'reasoning.md', 'output.json'],
    'examples/intl-commercial-tpn-msb':     ['input.json', 'reasoning.md', 'output.json'],
    'examples/us-strip-mall-panelboard':    ['input.json', 'reasoning.md', 'output.json'],
}
missing, total = [], 0
for subdir, files in expected.items():
    base = root if subdir == 'skill-level' else f'{root}/{subdir}'
    for f in files:
        total += 1
        p = f'{base}/{f}'
        if not os.path.isfile(p):
            missing.append(p)
print(f'Expected files: {total}')
print(f'Missing: {len(missing)}')
for m in missing: print(f'  - {m}')
assert not missing
print('All files present')
PYEOF
```
Expected: `Expected files: 43`, `Missing: 0`, `All files present`

- [ ] **Step 2: Consumption-pattern proof + standards exist**

```bash
python3 -c "
import json, os
m = json.load(open('electrical/db-layout/skill.manifest.json'))
folders = [s for s in m['standards'] if s.endswith('/')]
files = [s for s in m['standards'] if not s.endswith('/') and '.' in s.split('/')[-1]]
print(f'Folders: {len(folders)}, Files: {len(files)}')
assert len(folders) == 0
assert len(files) == 19
missing = [f for f in m['standards'] if not os.path.isfile(f)]
print(f'Missing on disk: {len(missing)}')
assert not missing
print('Consumption-pattern proof: PASS')
"
```

- [ ] **Step 3: Schemas valid**

```bash
python3 -c "
import json, jsonschema
for f in ['db-layout-ir.schema.json', 'db-layout-intent.schema.json', 'db-layout-rollup-intent.schema.json']:
    s = json.load(open(f'electrical/db-layout/schemas/{f}'))
    jsonschema.Draft7Validator.check_schema(s)
    print(f'{f}: schema valid')
"
```

- [ ] **Step 4: All 3 examples schema-valid**

```bash
python3 - <<'PY'
import json, glob
from jsonschema import Draft7Validator
ir_schema = json.load(open('electrical/db-layout/schemas/db-layout-ir.schema.json'))
rationale_schema = json.load(open('shared/schemas/core/rationale.schema.json'))
ir_no_id = dict(ir_schema)
ir_no_id.pop('$id', None)
ir_no_id['properties']['rationale'] = rationale_schema
v = Draft7Validator(ir_no_id)
for out_path in sorted(glob.glob('electrical/db-layout/examples/*/output.json')):
    name = out_path.split('/')[-2]
    errors = list(v.iter_errors(json.load(open(out_path))))
    print(f'{name}: {"PASS" if not errors else f"FAIL ({len(errors)} errors)"}')
PY
```
Expected: 3× `PASS`

- [ ] **Step 5: Cross-skill contract check — rollup intent matches earthing's expectation**

```bash
python3 - <<'PY'
import json
schema = json.load(open('electrical/db-layout/schemas/db-layout-rollup-intent.schema.json'))
earthing_input = json.load(open('electrical/earthing/examples/uk-dwelling-tn-cs/input.json'))
db_intent = next(i for i in earthing_input['consumed_intents'] if i['intent_type'] == 'db-layout')
payload = dict(db_intent['payload'])
payload['project_id'] = 'cross-skill-contract-test'
from jsonschema import Draft7Validator
errors = list(Draft7Validator(schema).iter_errors(payload))
if errors:
    for e in errors[:5]:
        print(f'  ERR: {e.message}')
else:
    print('Cross-skill contract: db-layout-rollup-intent satisfies earthing example shape')
PY
```
Expected: `Cross-skill contract: db-layout-rollup-intent satisfies earthing example shape`

- [ ] **Step 6: Update `SKILLS_STATUS.md`**

```bash
grep -nE "^\| db-layout" SKILLS_STATUS.md
```

Edit the matching line:
- Old: `| db-layout | electrical/db-layout | stub | BS 7671:2018, BS EN 61439 | — | — |`
- New: `| db-layout | electrical/db-layout | **beta** | BS 7671:2018, IEC 60364, IEC 61439, NFPA 70 (NEC 2023), IEC 60617 | 8/3 ✓ | v1.0.0 schedule + schematic + selectivity. 13-step generator prompt, IR + 2 intent schemas (single-board + rollup), 14 deterministic checks, 8 evals (all WI5 + selectivity_cascade + intent_rollup_shape), 3 worked examples (UK CU, INT TPN MSB, US NEMA panelboard). Selectivity uses fault-level intent (deferred via tool_call_pending until that skill ships). |`

- [ ] **Step 7: Final commit**

```bash
git add electrical/db-layout/ SKILLS_STATUS.md
git commit -m "feat(db-layout): v1.0.0 beta - schedule + schematic + selectivity complete"
```

- [ ] **Step 8: Skill summary check**

```bash
find electrical/db-layout -type f | sort | wc -l
find electrical/db-layout -type f -exec wc -l {} + | tail -1
```
Expected: 43 files; total line count between 3500–6000.

---

## Self-Review Checklist

After all 27 tasks execute:

1. **Spec coverage:** Re-read `docs/superpowers/specs/2026-05-15-db-layout-skill-design.md` § File Set table. Every named file must exist.
2. **Type consistency:** `enclosure_form_iec61439` (string "1"..."4b") and `ocpd.type` (MCB/MCCB/ACB/fuse/RCBO) must hold across schema + generator + rules + validation + examples.
3. **Cross-task path references:** Task 6 (manifest), Task 9 (generator), Tasks 15-22 (evals), Tasks 23-25 (examples) — all reference the same 19 standards files.
4. **Consumption-pattern proof:** Task 27 Step 2 verifies; should pass.
5. **Cross-skill contract:** Task 27 Step 5 verifies db-layout-rollup-intent against earthing's existing expected payload. Drift here breaks earthing.
6. **WI alignment:**
   - WI1 (inputs taxonomy): Task 5 — inputs.json
   - WI2 (rationale block): Task 2 (schema $ref), Task 9 (Step 13), eval-06
   - WI3 (calc executor deferral): selectivity_results entries with tool_call_pending, declared in Task 2 schema + Task 9 Step 11 + Task 14 docs
   - WI4 (cross-drawing intents): Tasks 3-4 (intent schemas), Task 6 (manifest produces/consumes), eval-08
   - WI5 (eval categories): Tasks 15-22 cover all 6 + 2 skill-specific
7. **No placeholders:** Search for "TODO" / "TBD" / "implement later" — none should remain.

---

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-05-15-db-layout-skill.md`.**

Two execution options:

**1. Subagent-Driven (recommended)** — Dispatch a fresh subagent per task, review between tasks, fast iteration. Used successfully for the earthing skill yesterday.

**2. Inline Execution** — Execute tasks in this session using `executing-plans`, batch execution with checkpoints.

Which approach?
