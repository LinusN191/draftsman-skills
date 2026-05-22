# Schematic Skill v1.0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the schematic skill v1.0 — 10th electrical skill — covering control + protection schematics across 4 jurisdictions (KE/UK/INT/US) with hybrid consumer pattern (db-layout-rollup + fault-level + earthing intents, leaf-mode fallback).

**Architecture:** 12 tasks across 5 phases. Phase A scaffolds infrastructure (manifest + schemas + symbol library). Phase B authors 3 prompts. Phase C ships 8 examples in 2 jurisdictional-category bundles. Phase D authors evals + rules + inputs.json + bookkeeping. Phase E ships. Per-schematic IR (one schematic = one IR) mirrors db-layout's pattern. Hybrid consumer pattern mirrors small-power v1.1.

**Tech Stack:** JSON Schema Draft-07 (IR + intent + inputs schemas), JSON (manifest + symbols + examples + ontology), YAML (rules + constraints + validation + evals), Markdown (README + CHANGELOG + prompts + reasoning).

**Pattern parents (verified at commit `dd1149d`):**
- `electrical/sld/skill.manifest.json` — closest multi-intent consumer manifest reference (consumes db-layout + earthing + fault-level + KS1700 in standards)
- `electrical/small-power/skill.manifest.json` — 4-jurisdiction reference (BS7671 + IEC60364 + KS1700 + NFPA70 standards + leaf-mode hybrid consumer)
- `electrical/db-layout/schemas/db-layout-ir.schema.json` (post-3W2c) — IR schema pattern with board_kind oneOf discriminator + jurisdiction enum [GB, EU, INT, US, KE] + strict additionalProperties
- `electrical/db-layout/prompts/generator.md` (post-3W2c) — canonical 12-step generator prompt with KE jurisdiction + board_kind + post-3W2c citation form table
- `electrical/db-layout/examples/uk-domestic-consumer-unit/output.json` (post-3W2c) — main_switchboard rationale precedent (9 sections + chat_summary 40-500)
- `electrical/db-layout/examples/ke-nairobi-gh-db/output.json` (post-3W2c) — specialty_board rationale precedent (6 sections + KE citation form)
- `shared/symbols/electrical/luminaires/LED_PANEL_600.json` — per-symbol JSON shape: symbol_id, version, category, subcategory, standard_reference, display_name, geometry, cad, default_rotation, typical_specs, tag_format
- `shared/schemas/core/eval.schema.json` (post-3W2a) — canonical eval shape (name+skill+input+checks)
- `shared/schemas/core/inputs.schema.json` (post-3W2a) — items[] InputItem taxonomy with depends_on graph

**Final state acceptance:**
- Harness AGGREGATE 162/162 exit 0 (143 baseline + 8 example outputs + ~10 evals + 1 inputs.json = +19)
- 3 new producer→consumer pairs verified clean (db-layout-rollup → schematic; fault-level → schematic; earthing → schematic) — graph grows from 15 to 18 pairs
- Schema files (IR + intent) Draft-07 valid; positive + negative tests pass for oneOf branches
- 8 examples validate against schematic-ir.schema.json
- inputs.json validates against shared/schemas/core/inputs.schema.json
- 12 task commits + 2 doc commits (spec dd1149d + this plan) = 14 commits

**Model selection per [[feedback-no-haiku-sonnet-opus-only]]:**
- Sonnet × 4: Tasks 1 (skeleton), 3 (symbol library), 10 (rules + inputs.json), 11 (bookkeeping)
- Opus × 8: Tasks 2 (IR + intent schemas), 4-6 (3 prompts), 7-8 (2 example bundles), 9 (evals), 12 (final ship)

**Critical post-3W2c citation lessons (apply throughout):**
- Single-frame voltage references (don't dual-quote percentages — pair % with absolute volts if needed)
- No fabricated standard publication years (omit year unless cross-verified)
- Use `§ 311.1` not bare `§ 311`
- Use `main_switch_fused` canonical enum (not informal `switch-fuse`)
- Use `BS EN 61009-1:2012+A12:2014` not bare `:2012`
- KE citation form: `KS 1700:2018 § X (route to BS 7671 via §313)`
- jurisdiction enum includes `KE`

---

## File Structure

**Files created (~80-90):**

`electrical/schematic/` directory tree:
- `skill.manifest.json` (rewrite — replaces stub at v0.1.0)
- `README.md` (rewrite — replaces stub)
- `CHANGELOG.md` (new v1.0.0 entry)
- `inputs.json` (~25-30 items[] taxonomy)
- `schemas/schematic-ir.schema.json` (Draft-07 IR with oneOf branching)
- `schemas/schematic-intent.schema.json` (terminal intent emission)
- `prompts/generator.md` (12-step generation flow)
- `prompts/validator.md` (10 INV invariants)
- `prompts/reviewer.md` (6 D-decisions)
- `ontology/schematic-types.json` (7-value taxonomy)
- `rules/motor-protection-coordination.yaml`
- `rules/contactor-rating.yaml`
- `rules/overload-class.yaml`
- `rules/differential-stability.yaml`
- `rules/busbar-protection-zoning.yaml`
- `constraints/schema-cross-references.yaml`
- `constraints/protection-coordination.yaml`
- `validation/banned-annotations.yaml`
- `evals/eval-01-control-dol-happy-path.yaml`
- `evals/eval-02-protection-idmt-happy-path.yaml`
- `evals/eval-03-leaf-mode-fallback.yaml`
- `evals/eval-04-missing-protection-setting.yaml`
- `evals/eval-05-intent-cascade-verified.yaml`
- `evals/eval-06-jurisdiction-citation-form.yaml`
- `evals/eval-07-rationale-block.yaml`
- `evals/eval-08-symbol-library-resolution.yaml`
- `evals/eval-09-banned-annotation-trap.yaml`
- `evals/eval-10-schematic-type-classification.yaml`
- 8 × `examples/<scenario>/{input.json, output.json, reasoning.md}` (+ optional sample-schedule.md or protection-settings-table.md)

`shared/symbols/electrical/schematic/` directory tree:
- `README.md` (new — symbol library index)
- 40 × `<SYMBOL_ID>.json` (BS EN 60617 symbols organised by subcategory: motor_starter, protection, auxiliary, control_logic)

**Files modified (~3-4):**
- `SKILLS_STATUS.md` (Task 11)
- `CLAUDE.md` (Task 11 — build status 9 → 10 shipped, 3 → 2 drawings remaining)
- `ARCHITECTURE.md` (Task 11 — if any cross-skill pattern surfaced)
- `/Users/linus/.claude/projects/-Users-linus-Desktop-DraftsMan-SKills-draftsman-skills/memory/MEMORY.md` (Task 12 — index entry)

**Files created outside repo (1):**
- `/Users/linus/.claude/projects/.../memory/schematic-shipped.md` (Task 12)

---

## Phase A — Infrastructure (Tasks 1-3)

## Task 1: Skill skeleton + manifest (Sonnet)

**Files:**
- Modify: `electrical/schematic/skill.manifest.json` (replace stub at v0.1.0)
- Create: `electrical/schematic/README.md` (replace stub)
- Create: `electrical/schematic/CHANGELOG.md`
- Create: `electrical/schematic/schemas/` directory (empty for Task 2)
- Create: `electrical/schematic/rules/` directory (empty for Task 10)
- Create: `electrical/schematic/constraints/` directory (empty for Task 10)
- Create: `electrical/schematic/validation/` directory (empty for Task 10)
- Create: `electrical/schematic/ontology/` directory (for Task 3)

### Step 1: Read pattern parents

- [ ] Read `electrical/sld/skill.manifest.json` and `electrical/small-power/skill.manifest.json` end-to-end. Note the manifest field shape (skill / version / discipline / subdiscipline / status / licence / description / inputs_path / outputs / output_schema / produces_intent / produces_intent_schema / consumes_intents / standards / calculations / ontology / rules / constraints / validators / evals / examples / symbols / templates / docs / changelog / compatible_runtimes).

### Step 2: Author `electrical/schematic/skill.manifest.json`

- [ ] Write the new manifest:

```json
{
  "skill": "schematic",
  "version": "1.0.0",
  "last_updated": "2026-05-22",
  "discipline": "electrical",
  "subdiscipline": "schematic_diagrams",
  "status": "beta",
  "licence": "MIT",
  "description": "Schematic control + protection diagrams per BS EN 60617 / BS EN 61082 / IEC 60255 / IEC 61850 / NEC 2023 / IEEE Std 315. Hybrid consumer of db-layout-rollup + fault-level + earthing intents (leaf-mode fallback when intents absent). Produces schematic IR for control circuits (motor starter / changeover / sequence) + protection schemes (IDMT overcurrent / differential / motor protection / busbar protection). 4 jurisdictions: GB / KE / INT / US.",
  "inputs_path": "inputs.json",
  "outputs": ["schematic-ir"],
  "output_schema": "electrical/schematic/schemas/schematic-ir.schema.json",
  "produces_intent": "schematic",
  "produces_intent_schema": "electrical/schematic/schemas/schematic-intent.schema.json",
  "consumes_intents": [
    "db-layout-rollup",
    "fault-level",
    "earthing"
  ],
  "standards": [
    "shared/standards/electrical/BS7671/",
    "shared/standards/electrical/IEC60364/",
    "shared/standards/electrical/IEC60617/",
    "shared/standards/electrical/IEC60255/",
    "shared/standards/electrical/IEC61850/",
    "shared/standards/electrical/NFPA70/",
    "shared/standards/electrical/KS1700/"
  ],
  "calculations": [],
  "ontology": [
    "electrical/schematic/ontology/schematic-types.json"
  ],
  "rules": [
    "electrical/schematic/rules/motor-protection-coordination.yaml",
    "electrical/schematic/rules/contactor-rating.yaml",
    "electrical/schematic/rules/overload-class.yaml",
    "electrical/schematic/rules/differential-stability.yaml",
    "electrical/schematic/rules/busbar-protection-zoning.yaml"
  ],
  "constraints": [
    "electrical/schematic/constraints/schema-cross-references.yaml",
    "electrical/schematic/constraints/protection-coordination.yaml"
  ],
  "validators": [
    "electrical/schematic/validation/banned-annotations.yaml"
  ],
  "symbols": "shared/symbols/electrical/schematic/",
  "evals": "electrical/schematic/evals/",
  "examples": "electrical/schematic/examples/",
  "prompts": {
    "generator": "electrical/schematic/prompts/generator.md",
    "validator": "electrical/schematic/prompts/validator.md",
    "reviewer": "electrical/schematic/prompts/reviewer.md"
  },
  "docs": "electrical/schematic/docs/",
  "changelog": "electrical/schematic/CHANGELOG.md",
  "compatible_runtimes": ["DraftsMan >= 1.0", "Claude Code", "OpenClaw"]
}
```

### Step 3: Create empty subdirectories

- [ ] Run:
```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
mkdir -p electrical/schematic/{schemas,rules,constraints,validation,ontology}
```

### Step 4: Author `electrical/schematic/CHANGELOG.md`

- [ ] Create:

```markdown
# Schematic Skill — Changelog

## v1.0.0 — 2026-05-22

Initial release. Control + protection schematics with hybrid consumer pattern.

### Added
- Per-schematic IR (one schematic = one IR document)
- 7-value `schematic_type` enum with oneOf branching (control_motor_starter / control_changeover / control_sequence / protection_overcurrent / protection_differential / protection_motor / protection_busbar)
- 40 BS EN 60617 symbols (motor starter + protection + auxiliary + control logic)
- 8 jurisdictional examples: 4 control (KE/UK/INT/US) + 4 protection (KE/UK/INT/US)
- Hybrid consumer of `db-layout-rollup` + `fault-level` + `earthing` intents with leaf-mode fallback
- Terminal `schematic` intent emission for future tender-report / om-manual consumption

### Standards
- BS 7671:2018+A2:2022, BS EN 60617, BS EN 61082, BS EN 61009-1:2012+A12:2014 (UK)
- KS 1700:2018 routing to BS 7671 via §313 + IEC 60617 + IEC 60255 (KE)
- IEC 60364-X-XX + IEC 60617 + IEC 60255 + IEC 61850 (INT)
- NEC 2023 / NFPA 70 + IEEE Std 315 + IEEE C37.x (US)

### Lessons applied from Sprint 3-W2c
- Single-frame voltage references (no dual-frame % collision)
- No fabricated standard publication years
- Canonical enums (`main_switch_fused`, `§ 311.1`)
- Africa-first KE jurisdiction first-class
```

### Step 5: Author `electrical/schematic/README.md`

- [ ] Create (replaces stub):

```markdown
# Schematic Skill

**Status:** beta (v1.0.0)
**Discipline:** electrical → schematic_diagrams
**Standards:** BS EN 60617, BS EN 61082, IEC 60255, IEC 61850, NEC 2023, IEEE Std 315

## What this skill produces

Schematic control + protection diagrams as structured IR. One schematic = one IR document. Two categories:

- **Control schematics**: motor starter circuits (DOL / star-delta / VSD), contactor logic, sequence of operations, generator/UPS changeover
- **Protection schematics**: IDMT overcurrent, differential (87T / 87B), restricted earth fault (87N), motor protection (49/50/51/86), busbar protection

## Cross-skill integration (hybrid consumer)

When upstream intents are available:
- `db-layout-rollup` — upstream OCPD context (breaker type + rating + curve)
- `fault-level` — PFC at protected node + protection coordination
- `earthing` — system type + CPC return paths + earth-fault loop impedance

When intents absent (leaf-mode), engineer provides equivalent context via inputs.json.

## Jurisdictions covered

GB (BS 7671:2018+A2:2022), KE (KS 1700:2018 + BS 7671 routing), INT (IEC 60364-X-XX), US (NEC 2023 / NFPA 70).

## Outputs

- `schematic-ir.schema.json` — structured IR
- `schematic-intent.schema.json` — terminal intent for downstream consumption

## Examples

See `examples/` — 8 canonical examples spanning control + protection across all 4 jurisdictions.
```

### Step 6: Validate manifest is parseable JSON + verify schematic-ir.schema.json reference is correct

- [ ] Run:
```bash
python3 -c "import json; d = json.load(open('electrical/schematic/skill.manifest.json')); print(f'OK: version={d[\"version\"]}, status={d[\"status\"]}, produces_intent={d[\"produces_intent\"]}, consumes_intents={d[\"consumes_intents\"]}')"
```
Expected: `OK: version=1.0.0, status=beta, produces_intent=schematic, consumes_intents=['db-layout-rollup', 'fault-level', 'earthing']`

### Step 7: Confirm harness still 143/143 (no regression — new skill not yet in scope)

- [ ] Run:
```bash
python3 scripts/validate-examples.py 2>&1 | tail -3
```
Expected: 143/143 exit 0 (or 1 from baseline; the new manifest doesn't yet have evals/inputs/examples).

### Step 8: Commit

- [ ] Run:
```bash
git add electrical/schematic/
git commit -m "feat(schematic): Phase A Task 1 — skill skeleton v1.0.0 (manifest + README + CHANGELOG + empty subdirs); hybrid consumer of db-layout-rollup + fault-level + earthing; produces_intent schematic; 4 jurisdictions"
```

---

## Task 2: IR + intent schemas (Opus)

**Why Opus:** Schema authoring with oneOf discriminator + strict additionalProperties + 7-value enum + branching by schematic_type. Requires judgment about field shapes + positive/negative test design.

**Files:**
- Create: `electrical/schematic/schemas/schematic-ir.schema.json`
- Create: `electrical/schematic/schemas/schematic-intent.schema.json`

### Step 1: Read post-3W2c pattern parent

- [ ] Read `electrical/db-layout/schemas/db-layout-ir.schema.json` end-to-end. Note:
- Top-level `required: [drawing_type, version, meta, jurisdiction, board, ...]`
- `drawing_type: { "const": "..." }`
- `jurisdiction: { "enum": ["GB", "EU", "INT", "US", "KE"] }` (post-3W2c additions)
- Strict per-property `additionalProperties: false`
- `meta.consumed_intents[]` shape (intent_type + intent_version + produced_by)
- `oneOf` discriminator on board (main_switchboard vs specialty_board)
- $ref to `../../../shared/schemas/core/rationale.schema.json` for rationale block

### Step 2: Author `schematic-ir.schema.json`

- [ ] Create the IR schema:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "electrical/schematic/schemas/schematic-ir.schema.json",
  "title": "Schematic IR (v1.0)",
  "description": "Intermediate Representation for the schematic skill. One IR document per schematic sheet. Carries items[] (devices), connections[] (wires), labels[], protection_settings[] (protection only) or sequence_of_operation (control only), and rationale.",
  "type": "object",
  "required": [
    "drawing_type",
    "version",
    "meta",
    "jurisdiction",
    "schematic_type",
    "sheet",
    "items",
    "connections",
    "labels",
    "compliance_summary",
    "rationale"
  ],
  "properties": {
    "drawing_type": { "const": "schematic" },
    "version": { "type": "string", "pattern": "^\\d+\\.\\d+(\\.\\d+)?$" },
    "meta": {
      "type": "object",
      "required": ["project_id", "skill_version", "produced_at"],
      "additionalProperties": false,
      "properties": {
        "project_id":    { "type": "string" },
        "skill_version": { "type": "string" },
        "produced_at":   { "type": "string", "format": "date-time" },
        "consumed_intents": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["intent_type", "intent_version", "produced_by"],
            "additionalProperties": false,
            "properties": {
              "intent_type":    { "type": "string", "pattern": "^[a-z][a-z0-9-]*$" },
              "intent_version": { "type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$" },
              "produced_by":    { "type": "string" }
            }
          }
        }
      }
    },
    "jurisdiction": { "enum": ["GB", "EU", "INT", "US", "KE"] },
    "schematic_type": {
      "enum": [
        "control_motor_starter",
        "control_changeover",
        "control_sequence",
        "protection_overcurrent",
        "protection_differential",
        "protection_motor",
        "protection_busbar"
      ]
    },
    "sheet": {
      "type": "object",
      "required": ["sheet_id", "title", "page_of"],
      "additionalProperties": false,
      "properties": {
        "sheet_id": { "type": "string", "pattern": "^[A-Z][A-Z0-9-]{0,15}$" },
        "title": { "type": "string" },
        "page_of": { "type": "string", "pattern": "^\\d+/\\d+$" }
      }
    },
    "items": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["item_id", "device_class", "bs_en_60617_ref"],
        "additionalProperties": false,
        "properties": {
          "item_id":   { "type": "string", "pattern": "^[A-Z][A-Z0-9_-]{1,15}$" },
          "device_class": {
            "enum": [
              "contactor", "overload", "isolator", "motor", "thermistor", "ptc",
              "idmt_relay", "instantaneous_relay", "differential_relay", "ref_relay",
              "distance_relay", "lockout_relay", "uv_relay", "ov_relay",
              "breaker", "ct", "vt",
              "terminal", "wire_reference", "lamp", "push_button", "selector_switch",
              "timer", "counter", "latch", "logic_gate", "signal_converter"
            ]
          },
          "bs_en_60617_ref":  { "type": "string" },
          "ieee_std_315_ref": { "type": "string" },
          "rating":           { "type": "string" },
          "ansi_function_code": { "type": "string", "pattern": "^[0-9]{1,3}[A-Z]?(T|B|N|G)?$" }
        }
      }
    },
    "connections": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["wire_id", "from_item", "to_item", "function"],
        "additionalProperties": false,
        "properties": {
          "wire_id":         { "type": "string", "pattern": "^W[0-9]+$" },
          "from_item":       { "type": "string" },
          "from_terminal":   { "type": "string" },
          "to_item":         { "type": "string" },
          "to_terminal":     { "type": "string" },
          "conductor_csa_mm2": { "type": "number" },
          "voltage_class":   { "enum": ["control_LV", "aux_DC", "aux_AC", "power_LV", "power_HV"] },
          "function":        { "type": "string" }
        }
      }
    },
    "labels": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["anchor_item", "text", "kind"],
        "additionalProperties": false,
        "properties": {
          "anchor_item": { "type": "string" },
          "text":        { "type": "string" },
          "kind":        { "enum": ["device_tag", "sequence_note", "terminal_number", "wire_number"] }
        }
      }
    },
    "protection_settings": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["ansi_code", "device_id"],
        "additionalProperties": false,
        "properties": {
          "ansi_code": { "type": "string", "pattern": "^[0-9]{1,3}[A-Z]?(T|B|N|G)?$" },
          "device_id": { "type": "string" },
          "set_value": { "type": ["number", "string"] },
          "set_unit":  { "type": "string" },
          "time_curve": { "type": "string" },
          "ct_ratio":  { "type": "string" },
          "tool_call_pending": { "type": "boolean" }
        }
      }
    },
    "sequence_of_operation": { "type": "string" },
    "compliance_summary": {
      "type": "object",
      "required": ["compliant"],
      "additionalProperties": false,
      "properties": {
        "compliant":             { "type": "boolean" },
        "non_compliance_flags":  { "type": "array", "items": { "type": "object" } },
        "assumptions":           { "type": "array", "items": { "type": "string" } }
      }
    },
    "drawn_as_symbols": { "type": "array", "items": { "type": "object" } },
    "flags": { "type": "array", "items": { "type": "object" } },
    "rationale": { "$ref": "../../../shared/schemas/core/rationale.schema.json" }
  },
  "additionalProperties": false,
  "oneOf": [
    {
      "properties": { "schematic_type": { "pattern": "^control_" } },
      "required": ["sequence_of_operation"]
    },
    {
      "properties": { "schematic_type": { "pattern": "^protection_" } },
      "required": ["protection_settings"]
    }
  ]
}
```

### Step 3: Verify IR schema is Draft-07 valid

- [ ] Run:
```bash
python3 -c "import json, jsonschema; s = json.load(open('electrical/schematic/schemas/schematic-ir.schema.json')); jsonschema.Draft7Validator.check_schema(s); print('Schema OK')"
```
Expected: `Schema OK`.

### Step 4: Author positive + negative tests

- [ ] Run:
```bash
python3 << 'EOF'
import json, jsonschema
schema = json.load(open('electrical/schematic/schemas/schematic-ir.schema.json'))

# Positive 1: minimal valid control_motor_starter
positive_control = {
    "drawing_type": "schematic",
    "version": "1.0",
    "meta": {"project_id": "TEST", "skill_version": "schematic/1.0.0", "produced_at": "2026-05-22T00:00:00Z"},
    "jurisdiction": "GB",
    "schematic_type": "control_motor_starter",
    "sheet": {"sheet_id": "SHT-001", "title": "DOL Starter", "page_of": "1/1"},
    "items": [{"item_id": "K1", "device_class": "contactor", "bs_en_60617_ref": "S00211"}],
    "connections": [],
    "labels": [],
    "sequence_of_operation": "Press START → K1 energises → motor runs. Press STOP → K1 de-energises → motor stops.",
    "compliance_summary": {"compliant": True},
    "rationale": {"chat_summary": "Minimal test rationale for positive_control case.", "sections": [{"title": "Test", "summary": "ok"}]}
}
try:
    jsonschema.validate(positive_control, schema)
    print("Positive control OK")
except jsonschema.ValidationError as e:
    print(f"FAIL control: {e.message[:200]}")

# Positive 2: minimal valid protection_overcurrent
positive_protection = dict(positive_control)
positive_protection["schematic_type"] = "protection_overcurrent"
positive_protection["items"] = [{"item_id": "R51", "device_class": "idmt_relay", "bs_en_60617_ref": "S00425", "ansi_function_code": "51"}]
positive_protection["protection_settings"] = [{"ansi_code": "51", "device_id": "R51", "set_value": 100, "set_unit": "A", "time_curve": "SI", "ct_ratio": "200/5"}]
del positive_protection["sequence_of_operation"]
try:
    jsonschema.validate(positive_protection, schema)
    print("Positive protection OK")
except jsonschema.ValidationError as e:
    print(f"FAIL protection: {e.message[:200]}")

# Negative 1: cross-shape (control_* but missing sequence_of_operation)
negative = dict(positive_control)
del negative["sequence_of_operation"]
try:
    jsonschema.validate(negative, schema)
    print("FAIL: negative cross-shape unexpectedly passed")
except jsonschema.ValidationError as e:
    if "sequence_of_operation" in e.message:
        print(f"Negative correctly rejected: {e.message[:160]}")
    else:
        print(f"Negative rejected wrong reason: {e.message[:160]}")

# Negative 2: protection_* but missing protection_settings
negative2 = dict(positive_protection)
del negative2["protection_settings"]
try:
    jsonschema.validate(negative2, schema)
    print("FAIL: negative2 (protection without settings) unexpectedly passed")
except jsonschema.ValidationError as e:
    print(f"Negative2 correctly rejected: {e.message[:160]}")
EOF
```

Expected:
- Positive control OK
- Positive protection OK
- Negative correctly rejected (mentions sequence_of_operation)
- Negative2 correctly rejected (mentions protection_settings)

If negatives don't reject, the oneOf is broken — halt and re-author Step 2.

### Step 5: Author `schematic-intent.schema.json`

- [ ] Create the intent schema:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "electrical/schematic/schemas/schematic-intent.schema.json",
  "title": "Schematic Intent (v1.0)",
  "description": "Terminal intent emitted by the schematic skill for downstream consumption (future tender-report / om-manual). Carries summary of schematic_type, sheet identification, jurisdiction, and high-level item count for cross-document reference.",
  "type": "object",
  "required": ["intent_type", "intent_version", "jurisdiction", "schematic_type", "sheet_id", "summary"],
  "additionalProperties": false,
  "properties": {
    "intent_type":    { "const": "schematic" },
    "intent_version": { "type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$" },
    "jurisdiction":   { "enum": ["GB", "EU", "INT", "US", "KE"] },
    "schematic_type": {
      "enum": [
        "control_motor_starter",
        "control_changeover",
        "control_sequence",
        "protection_overcurrent",
        "protection_differential",
        "protection_motor",
        "protection_busbar"
      ]
    },
    "sheet_id":   { "type": "string" },
    "summary": {
      "type": "object",
      "required": ["item_count", "connection_count"],
      "additionalProperties": false,
      "properties": {
        "item_count":        { "type": "integer", "minimum": 1 },
        "connection_count":  { "type": "integer", "minimum": 0 },
        "protection_settings_count": { "type": "integer", "minimum": 0 },
        "ansi_codes_present": { "type": "array", "items": { "type": "string" } }
      }
    }
  }
}
```

### Step 6: Verify intent schema is Draft-07 valid

- [ ] Run:
```bash
python3 -c "import json, jsonschema; s = json.load(open('electrical/schematic/schemas/schematic-intent.schema.json')); jsonschema.Draft7Validator.check_schema(s); print('OK')"
```
Expected: `OK`.

### Step 7: Confirm harness still 143/143

- [ ] Run:
```bash
python3 scripts/validate-examples.py 2>&1 | tail -3
```
Expected: 143/143 exit 0.

### Step 8: Commit

- [ ] Run:
```bash
git add electrical/schematic/schemas/
git commit -m "feat(schematic): Phase A Task 2 — IR + intent schemas (Draft-07; 7-value schematic_type enum with oneOf branching control vs protection; jurisdiction enum [GB/EU/INT/US/KE] per post-3W2c; strict additionalProperties; rationale \$ref to shared/schemas/core/rationale.schema.json); positive + negative tests pass"
```

## Task 2 Self-Review

- [ ] Both schemas Draft-07 valid
- [ ] Positive tests for control_motor_starter + protection_overcurrent both pass
- [ ] Negative cross-shape tests both correctly rejected
- [ ] Harness still 143/143

---

## Task 3: Symbol library + ontology (Sonnet)

**Why Sonnet:** ~40 deterministic JSON files following the per-symbol pattern. Mechanical authoring.

**Files:**
- Create: `shared/symbols/electrical/schematic/README.md`
- Create: `shared/symbols/electrical/schematic/<SYMBOL_ID>.json` × 40
- Create: `electrical/schematic/ontology/schematic-types.json`

### Step 1: Read symbol pattern parent

- [ ] Read `shared/symbols/electrical/luminaires/LED_PANEL_600.json` end-to-end. Note shape: `symbol_id, version, category, subcategory, standard_reference, display_name, geometry (with type + shape-specific keys), cad (block_name + default_layer + annotation_anchor), default_rotation, typical_specs (subcategory-specific), tag_format`.

### Step 2: Create subcategory subdirectories

- [ ] Run:
```bash
mkdir -p shared/symbols/electrical/schematic/{motor_starter,protection,auxiliary,control_logic}
```

### Step 3: Author motor_starter subcategory (10 symbols)

For each symbol, create a JSON file at `shared/symbols/electrical/schematic/motor_starter/<SYMBOL_ID>.json` following this template:

```json
{
  "symbol_id": "<UPPER_SNAKE_CASE_ID>",
  "version": "1.0.0",
  "category": "schematic",
  "subcategory": "motor_starter",
  "standard_reference": "BS EN 60617 IEC 617-<sheet>",
  "display_name": "<Human readable name>",
  "geometry": { "type": "schematic_symbol", "width_mm": <int>, "height_mm": <int> },
  "cad": {
    "default_layer": "E-CTRL-SYM",
    "block_name": "<BLOCK_NAME>",
    "annotation_anchor_mm": [0, 0]
  },
  "default_rotation": 0,
  "typical_specs": { "<key>": "<value>" },
  "tag_format": "<format>"
}
```

10 motor_starter symbols (one file each):
1. `CONTACTOR_1NO` — Contactor 1 normally-open contact
2. `CONTACTOR_1NC` — Contactor 1 normally-closed contact
3. `CONTACTOR_3POLE` — 3-pole contactor (power)
4. `CONTACTOR_4POLE` — 4-pole contactor (power + N)
5. `OVERLOAD_THERMAL` — Thermal overload relay (Class 10/20 selectable)
6. `ISOLATOR_3POLE` — 3-pole isolator (manual)
7. `MOTOR_3PHASE` — 3-phase induction motor
8. `MOTOR_1PHASE` — 1-phase capacitor-start motor
9. `THERMISTOR` — Motor thermistor (PTC element)
10. `PTC_RELAY` — PTC monitoring relay

Each gets `standard_reference` per BS EN 60617 sheet (e.g. `BS EN 60617 IEC 617-7` for switchgear). `tag_format`:
- Contactors: `K{index}`
- Overloads: `F{index:02d}`
- Isolators: `Q{index}`
- Motors: `M{index}`
- Thermistor/PTC: `B{index}`

### Step 4: Author protection subcategory (12 symbols)

12 protection symbols under `shared/symbols/electrical/schematic/protection/`:
1. `IDMT_RELAY_51` — IDMT overcurrent relay (ANSI 51)
2. `INSTANTANEOUS_RELAY_50` — Instantaneous overcurrent relay (ANSI 50)
3. `DIFFERENTIAL_RELAY_87T` — Transformer differential relay (ANSI 87T)
4. `RESTRICTED_EF_RELAY_87N` — Restricted earth fault relay (ANSI 87N)
5. `DISTANCE_RELAY_21` — Distance relay (ANSI 21)
6. `LOCKOUT_RELAY_86` — Lockout (master) relay (ANSI 86)
7. `UNDERVOLTAGE_RELAY_27` — Undervoltage relay (ANSI 27)
8. `OVERVOLTAGE_RELAY_59` — Overvoltage relay (ANSI 59)
9. `BREAKER_52` — Circuit breaker (ANSI 52)
10. `CT_GENERIC` — Current transformer
11. `VT_GENERIC` — Voltage transformer
12. `ANSI_TABLE_REFERENCE` — ANSI function-code reference table (annotation block)

Each gets `standard_reference: "BS EN 60617 IEC 617-7"` (switchgear) or `IEC 60255 (for relays)`. `tag_format`:
- Relays: `<ansi>F{index}` (e.g. 51F1, 87T-F1)
- Breakers: `Q{index}`
- CT: `T{index}`
- VT: `T{index}V`

### Step 5: Author auxiliary subcategory (10 symbols)

10 auxiliary symbols under `shared/symbols/electrical/schematic/auxiliary/`:
1. `TERMINAL_RAIL` — DIN-rail terminal block (generic)
2. `TERMINAL_STRIP` — Strip-mounted terminal
3. `WIRE_REFERENCE` — Wire reference indicator (sheet-cross-reference)
4. `LAMP_RED` — Indication lamp red
5. `LAMP_GREEN` — Indication lamp green
6. `LAMP_AMBER` — Indication lamp amber
7. `LAMP_BLUE` — Indication lamp blue
8. `LAMP_WHITE` — Indication lamp white
9. `PUSHBUTTON_NO` — Push-button normally-open
10. `PUSHBUTTON_EMERGENCY` — Emergency-stop push-button (mushroom head, twist-release)

Plus the existing list of 10 is correct — but the spec listed selector_switch (2-pos/3-pos) as a separate item. To keep at exactly 10: include `PUSHBUTTON_NC` (normally-closed) and `SELECTOR_SWITCH_2POS` + `SELECTOR_SWITCH_3POS` — but that's 13. Trim to 10:
- Keep: TERMINAL_RAIL, TERMINAL_STRIP, WIRE_REFERENCE, LAMP_RED, LAMP_GREEN, LAMP_AMBER, LAMP_BLUE, LAMP_WHITE, PUSHBUTTON_NO, SELECTOR_SWITCH_3POS

(Trim: drop PUSHBUTTON_NC + PUSHBUTTON_EMERGENCY + SELECTOR_SWITCH_2POS — these can go to v1.1)

`standard_reference: BS EN 60617 IEC 617-7` for switchgear + auxiliary. `tag_format`:
- Terminals: `X{index}`
- Wire ref: `W{from}-{to}`
- Lamps: `H{index}`
- Push-buttons + selectors: `S{index}`

### Step 6: Author control_logic subcategory (8 symbols)

8 control_logic symbols under `shared/symbols/electrical/schematic/control_logic/`:
1. `TIMER_ON_DELAY` — On-delay timer
2. `TIMER_OFF_DELAY` — Off-delay timer
3. `COUNTER` — Generic counter
4. `LATCH_SET_RESET` — Set/reset latch
5. `LOGIC_AND` — AND gate
6. `LOGIC_OR` — OR gate
7. `LOGIC_NOT` — NOT gate
8. `SIGNAL_CONVERTER` — 4-20mA / 0-10V signal converter

`standard_reference: BS EN 60617 IEC 617-12` (logic symbols). `tag_format`:
- Timers/counters: `KT{index}` or `KC{index}`
- Latches: `KL{index}`
- Gates: `=`/`>=1`/`1` block notation per BS EN 60617

### Step 7: Author symbol library README

- [ ] Create `shared/symbols/electrical/schematic/README.md`:

```markdown
# Schematic Symbols (BS EN 60617)

40 symbols organised by subcategory for the schematic skill v1.0.

## Subcategories

- `motor_starter/` (10): contactors, overload, isolator, motors, thermistor/PTC
- `protection/` (12): ANSI relays (51/50/87T/87N/21/86/27/59), breakers, instrument transformers
- `auxiliary/` (10): terminals, wire references, lamps, push-buttons, selector switches
- `control_logic/` (8): timers, counters, latches, logic gates, signal converter

## Standard references

- BS EN 60617 IEC 617-7 (switchgear + controlgear symbols)
- BS EN 60617 IEC 617-12 (logic function symbols)
- IEC 60255 (protection relay device-class semantics)
- IEEE Std 315 (US equivalent — referenced for symbol_id cross-mapping)

## Out of scope (v1.1+)

- PUSHBUTTON_NC, PUSHBUTTON_EMERGENCY, SELECTOR_SWITCH_2POS
- Distance protection variants (21B / 21P / 21N)
- HV-specific symbols (gas-insulated switchgear, vacuum interrupters)
```

### Step 8: Author `electrical/schematic/ontology/schematic-types.json`

- [ ] Create:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "schematic_type_taxonomy": {
    "control_motor_starter": {
      "description": "Single-motor starter control circuit (DOL, star-delta, autotransformer, soft-start, VFD start logic). Requires sequence_of_operation describing start/stop/protection-trip sequence.",
      "typical_items": ["contactor", "overload", "push_button", "lamp", "selector_switch"],
      "typical_standards": ["BS EN 60617 IEC 617-7", "IEC 60364-5-55", "BS 7671 § 552"]
    },
    "control_changeover": {
      "description": "Generator / UPS / mains-mains changeover schemes. Requires sequence_of_operation describing source-priority logic + transfer-time constraints.",
      "typical_items": ["contactor", "timer", "logic_and", "logic_not"],
      "typical_standards": ["BS 7671 § 560", "BS 7671 § 537", "IEC 60364-5-56"]
    },
    "control_sequence": {
      "description": "Multi-step control sequence (HVAC stage start, plant interlock, etc.). Requires sequence_of_operation describing state machine.",
      "typical_items": ["contactor", "timer", "counter", "latch_set_reset"],
      "typical_standards": ["BS EN 60617 IEC 617-12", "IEC 61131-3"]
    },
    "protection_overcurrent": {
      "description": "IDMT or instantaneous overcurrent protection (ANSI 50/51). Requires protection_settings with ansi_code + set_value + time_curve + ct_ratio.",
      "typical_items": ["idmt_relay", "instantaneous_relay", "ct", "breaker"],
      "typical_standards": ["IEC 60255-151", "IEC 60044-1 (CT)", "IEEE C37.96"]
    },
    "protection_differential": {
      "description": "Transformer differential (87T) or busbar differential (87B). Requires protection_settings with bias slope + stabilising resistor + ct ratio matching.",
      "typical_items": ["differential_relay", "ct", "breaker", "lockout_relay"],
      "typical_standards": ["IEC 60255-187", "IEC 61850-9-2"]
    },
    "protection_motor": {
      "description": "Motor protection scheme (49 thermal + 50/51 overcurrent + 86 lockout + 37 undercurrent + 47 phase rotation). Requires protection_settings per ANSI code.",
      "typical_items": ["idmt_relay", "instantaneous_relay", "lockout_relay", "thermistor", "ct"],
      "typical_standards": ["IEC 60255-149", "IEEE C37.96", "NEC Article 430"]
    },
    "protection_busbar": {
      "description": "Busbar protection (87B + 50BF breaker failure + zone overlap). Requires protection_settings with zone-mapping + 50BF time grading.",
      "typical_items": ["differential_relay", "instantaneous_relay", "lockout_relay", "ct", "breaker"],
      "typical_standards": ["IEC 60255-187", "IEC 61850-9-2 (process bus)", "IEEE C37.234"]
    }
  }
}
```

### Step 9: Validate all 41 JSON files parse

- [ ] Run:
```bash
python3 << 'EOF'
import json, glob
files = sorted(glob.glob('shared/symbols/electrical/schematic/**/*.json', recursive=True))
files += sorted(glob.glob('electrical/schematic/ontology/*.json'))
fail = 0
for f in files:
    try:
        json.load(open(f))
        print(f"OK {f}")
    except json.JSONDecodeError as e:
        print(f"FAIL {f}: {e}"); fail += 1
print(f"\n{len(files) - fail}/{len(files)} files parse")
EOF
```
Expected: all parse cleanly. Files: 40 symbols + 1 ontology + 1 README (skip README in the JSON count) = 41 JSON files.

### Step 10: Confirm harness still 143/143

- [ ] Run:
```bash
python3 scripts/validate-examples.py 2>&1 | tail -3
```
Expected: 143/143 exit 0.

### Step 11: Commit

- [ ] Run:
```bash
git add shared/symbols/electrical/schematic/ electrical/schematic/ontology/
git commit -m "feat(schematic): Phase A Task 3 — symbol library (40 BS EN 60617 symbols: 10 motor_starter + 12 protection + 10 auxiliary + 8 control_logic) + ontology/schematic-types.json (7-value taxonomy with typical_items + typical_standards per type)"
```

## Task 3 Self-Review

- [ ] 40 symbol JSONs + 1 ontology JSON authored
- [ ] All parse cleanly + each carries symbol_id + version + standard_reference + tag_format
- [ ] Harness still 143/143

---

## Phase B — Prompts (Tasks 4-6)

## Task 4: generator.md (Opus)

**Why Opus:** Engineering content authoring with 12-step flow. Requires judgment about hybrid-mode handling + per-jurisdiction citation form + LLM emission guidance.

**File:** Create `electrical/schematic/prompts/generator.md`

### Step 1: Read pattern parent

- [ ] Read `electrical/db-layout/prompts/generator.md` (post-3W2c) end-to-end. Note structure: front-matter context + 12-step procedure + citation form table + banned annotations + jurisdiction-specific guidance.

### Step 2: Author the generator prompt

- [ ] Create the prompt with the 12-step flow specified in spec §3 Phase B Task 4. The file should cover:

1. **Step 1 — Validate consumed intents**: read consumed_intents[] array; flag missing intents and switch to leaf-mode if all absent.
2. **Step 2 — Identify schematic_type**: from inputs.json schematic_type_selector OR engineer-provided context. Validate against 7-value enum.
3. **Step 3 — Resolve symbol library**: walk shared/symbols/electrical/schematic/ for symbol_id references. Halt if any required symbol missing (defer to v1.1).
4. **Step 4 — Place items[]**: enumerate devices per the chosen schematic_type. Use ontology/schematic-types.json typical_items as guidance.
5. **Step 5 — Wire connections[]**: control vs auxiliary vs power circuit. Connection wire_id pattern `^W[0-9]+$`. voltage_class enum [control_LV / aux_DC / aux_AC / power_LV / power_HV].
6. **Step 6 — Protection settings or sequence**: for protection_*, populate protection_settings[] with ansi_code + set_value + ct_ratio + time_curve. For control_*, write sequence_of_operation prose.
7. **Step 7 — Labels**: device tags (kind=device_tag) + sequence notes (kind=sequence_note) + terminal numbers + wire numbers.
8. **Step 8 — tool_call_pending flagging**: where calc.x.y deferred (e.g. CT ratio computation), flag tool_call_pending: true with descriptive code_clause.
9. **Step 9 — Rationale emission**: 6-9 sections + chat_summary 40-500 chars. Section titles per ontology/schematic-types.json typical sections.
10. **Step 10 — Per-jurisdiction citation form** table (GB / KE / INT / US) with explicit templates.
11. **Step 11 — Hybrid-mode fallback**: when intents absent, use engineer-provided context from inputs.json. Document this in rationale Schedule Notes.
12. **Step 12 — Self-validate against schematic-ir.schema.json**: confirm oneOf branch satisfied + all required fields populated + additionalProperties: false respected.

Include explicit guidance:
- **Citation form** per jurisdiction (post-3W2c-aligned table)
- **Banned annotations** (no `switch-fuse`; use `main_switch_fused`. No bare `§ 311`; use `§ 311.1`. No fabricated publication years. No dual-frame VD %.)
- **board_kind awareness** when consuming db-layout-rollup (main_switchboard vs specialty_board)
- **KE jurisdiction first-class** (per Africa-first strategy)
- **Tool-call-pending discipline**: defer rather than invent

### Step 3: Verify the prompt references real files

- [ ] Run:
```bash
# Find all referenced shared/symbols/ paths in the prompt and verify they exist
grep -oE 'shared/symbols/electrical/schematic/[a-z_/]+\.json' electrical/schematic/prompts/generator.md | sort -u | while read f; do
  if [ ! -f "$f" ]; then echo "MISSING: $f"; fi
done
# Similarly for ontology references
grep -oE 'electrical/schematic/ontology/[a-z-]+\.json' electrical/schematic/prompts/generator.md | sort -u | while read f; do
  if [ ! -f "$f" ]; then echo "MISSING: $f"; fi
done
```
Expected: no MISSING output.

### Step 4: Confirm harness still 143/143

- [ ] Run:
```bash
python3 scripts/validate-examples.py 2>&1 | tail -3
```
Expected: 143/143.

### Step 5: Commit

- [ ] Run:
```bash
git add electrical/schematic/prompts/generator.md
git commit -m "feat(schematic): Phase B Task 4 — generator.md (12-step generation flow with hybrid-consumer pattern + per-jurisdiction citation form table + post-3W2c banned annotations + board_kind awareness + KE jurisdiction first-class + tool-call-pending discipline)"
```

## Task 4 Self-Review

- [ ] 12 steps covered explicitly
- [ ] Per-jurisdiction citation form table present (GB / KE / INT / US)
- [ ] Hybrid-mode fallback documented
- [ ] All file references resolve (Step 3 grep clean)

---

## Task 5: validator.md (Opus)

**Why Opus:** 10 invariants requiring engineering judgment about acceptable check forms + severity policy + cross-skill cascade verification.

**File:** Create `electrical/schematic/prompts/validator.md`

### Step 1: Read pattern parent

- [ ] Read `electrical/db-layout/prompts/validator.md` (post-3W2c) end-to-end. Note: invariants table with INV-N + severity + clause + verification procedure.

### Step 2: Author the validator prompt

- [ ] Create the prompt with 10 invariants (INV-1 to INV-10) per spec §3 Phase B Task 5:

- **INV-1 — schema_valid**: IR validates against `electrical/schematic/schemas/schematic-ir.schema.json` (Draft-07). Severity: critical.
- **INV-2 — schematic_type ↔ items consistency**: control_motor_starter requires at least one contactor + one motor; protection_overcurrent requires at least one idmt_relay or instantaneous_relay + one ct. Severity: critical.
- **INV-3 — Connection topology valid**: every connection.from_item + to_item resolves to an items[].item_id; no orphan items (every item appears in at least one connection); no dangling wires. Severity: critical.
- **INV-4 — oneOf branch satisfied**: control_* requires non-empty sequence_of_operation; protection_* requires non-empty protection_settings[]. Severity: critical.
- **INV-5 — Symbol resolution**: every item.bs_en_60617_ref resolves to a symbol JSON in shared/symbols/electrical/schematic/. Severity: critical.
- **INV-6 — consumed_intents shape**: each meta.consumed_intents[] entry has intent_type matching the manifest's consumes_intents and resolves to a producer skill. Severity: critical.
- **INV-7 — Per-jurisdiction citation form**: jurisdiction GB uses BS 7671:2018+A2:2022 form; KE uses KS 1700:2018 § X (route to BS 7671 via §313) form; INT uses IEC 60364-X-XX form; US uses NEC 2023 / NFPA 70 form. Severity: warning.
- **INV-8 — Banned annotations absent**: no `switch-fuse` (must be `main_switch_fused`); no bare `§ 311` (must be `§ 311.1`); no dual-frame VD %; no fabricated standard publication years. Severity: warning.
- **INV-9 — Rationale block complete**: chat_summary 40-500 chars; sections 6-9 with title + non-empty summary. Severity: critical.
- **INV-10 — Cross-skill cascade consistency**: when db-layout-rollup consumed, the schematic's upstream OCPD references must match a board in the rollup; when fault-level consumed, protection_settings.set_value must be defensible against the fault-level intent's PFC at the protected node. Severity: warning.

Include severity policy: critical = halt; warning = report but allow ship; info = report only.

### Step 3: Verify references real files

- [ ] Run:
```bash
grep -oE 'electrical/schematic/schemas/[a-z-]+\.schema\.json' electrical/schematic/prompts/validator.md | sort -u | while read f; do
  if [ ! -f "$f" ]; then echo "MISSING: $f"; fi
done
```
Expected: no MISSING.

### Step 4: Harness check

- [ ] Run:
```bash
python3 scripts/validate-examples.py 2>&1 | tail -3
```
Expected: 143/143.

### Step 5: Commit

- [ ] Run:
```bash
git add electrical/schematic/prompts/validator.md
git commit -m "feat(schematic): Phase B Task 5 — validator.md (10 INV invariants: schema_valid / type↔items / connections / oneOf branch / symbol resolution / consumed_intents / citation form / banned annotations / rationale / cross-skill cascade); per-invariant severity policy"
```

## Task 5 Self-Review

- [ ] 10 invariants documented
- [ ] Each carries severity (critical / warning / info)
- [ ] Cross-skill cascade verification (INV-10) reference clear

---

## Task 6: reviewer.md (Opus)

**Why Opus:** 6 D-decisions require engineering-content quality judgment + standard ref verification + LLM-emission audit.

**File:** Create `electrical/schematic/prompts/reviewer.md`

### Step 1: Read pattern parent

- [ ] Read `electrical/db-layout/prompts/reviewer.md` (post-3W2c) end-to-end.

### Step 2: Author the reviewer prompt

- [ ] Create the prompt with 6 D-decisions per spec §3 Phase B Task 6:

- **D1 — Engineering correctness**: control logic sound (e.g. DOL needs hold-in contact; star-delta needs 7-second changeover; differential needs in-zone CT sense); protection settings defensible against manufacturer typicals (e.g. ABB REF615 / Siemens 7UM62 typical Class 10 overload, 1.0 In pickup, 0.5 s time multiplier). Severity: critical.
- **D2 — Standard refs grounded**: no invented clause numbers; no fabricated publication years (lesson from 3-W2c). Per-citation verification: does the cited clause actually cover the claim? Severity: critical.
- **D3 — Symbol library coverage**: every items[].bs_en_60617_ref maps to a file in shared/symbols/electrical/schematic/. Severity: critical.
- **D4 — Cross-skill cascade consistency**: consumed_intents shapes match producer skills' emitted intent schemas; references resolve. Severity: warning.
- **D5 — schematic_type appropriate to use case**: e.g. don't classify a motor protection scheme as control_motor_starter (those are different schematic_type values with different oneOf branches). Severity: critical.
- **D6 — Rationale prose quality**: engineering reasoning defensible; no LLM filler ("the schematic ensures comprehensive coverage..."); each section adds engineering content; chat_summary 40-500 + sections 6-9. Severity: warning.

### Step 3: Harness check

- [ ] Run:
```bash
python3 scripts/validate-examples.py 2>&1 | tail -3
```
Expected: 143/143.

### Step 4: Commit

- [ ] Run:
```bash
git add electrical/schematic/prompts/reviewer.md
git commit -m "feat(schematic): Phase B Task 6 — reviewer.md (6 D-decisions: engineering correctness / standard refs grounded / symbol library coverage / cross-skill cascade / schematic_type fit / rationale prose quality); severity per decision"
```

## Task 6 Self-Review

- [ ] 6 D-decisions documented
- [ ] Each carries severity + verification procedure

---

## Phase C — Jurisdictional examples (Tasks 7-8)

## Task 7: Control schematics bundle (4 examples) — Opus

**Why Opus:** Per-jurisdiction engineering content + cross-example consistency across 4 control schematics. Mirrors 3-W2b's per-jurisdiction Opus dispatch pattern.

**Files:** Create 4 example directories with input.json + output.json + reasoning.md:
- `electrical/schematic/examples/ke-nairobi-workshop-motor-starter/`
- `electrical/schematic/examples/uk-commercial-genset-changeover/`
- `electrical/schematic/examples/intl-hvac-vfd-control/`
- `electrical/schematic/examples/us-industrial-star-delta/`

### Step 1: Read pattern parents

- [ ] Read `electrical/db-layout/examples/uk-domestic-consumer-unit/output.json` (post-3W2c) for 9-section main_switchboard rationale shape. Read `electrical/db-layout/examples/ke-nairobi-gh-db/output.json` (post-3W2c) for 6-section specialty_board rationale shape + KE dual-routing citation form. Read `electrical/sld/examples/` for multi-intent-consumer per-example shape.

### Step 2: Inspect inputs.json item taxonomy (Task 10 will author full file; assume canonical shape for now)

For each control example, the input.json should carry:
- `jurisdiction` (GB / EU / INT / US / KE)
- `schematic_type` (control_motor_starter / control_changeover / control_sequence)
- Device declarations (motor rating + voltage + breaker type / changeover source priorities / sequence step list)
- `consumed_intents` array (present + fabricated_nodes if hybrid-mode; null for leaf-mode)

### Step 3: Author `ke-nairobi-workshop-motor-starter`

The 11 kW DOL grinder, KE industrial workshop. Leaf-mode (no upstream intents — engineer-provided MSP context).

input.json: jurisdiction=KE, schematic_type=control_motor_starter, motor_kw=11, motor_voltage_v=415, motor_fla_a=21, upstream_breaker_rating_a=32, upstream_breaker_curve=D (per Type D for motor inrush), consumed_intents=[].

output.json carries:
- meta.consumed_intents = [] (leaf-mode)
- jurisdiction = "KE"
- schematic_type = "control_motor_starter"
- items[] = {K1 contactor 3-pole, F1 overload Class 10, M1 motor 3-phase 11kW, S1 push-button NO start, H1 lamp green run, plus terminals}
- connections[] wiring start circuit (push-button → contactor coil) + power circuit (contactor → overload → motor)
- sequence_of_operation: "S1 (START) momentary press → K1 coil energises via auxiliary K1 NO hold contact → motor M1 runs via K1 main contacts. Press STOP (S2) or F1 overload trip → K1 de-energises → motor stops."
- 6-section rationale (specialty-board template adapted): Board Identification → Incoming Supply → Circuit Breakdown → Selectivity Analysis → Compliance Assessment → Schedule Notes
- Citations: `KS 1700:2018 § 552 (route to BS 7671 § 552 via §313)` + `IEC 60364-5-55` + `BS EN 60947-4-1` (motor starters)

reasoning.md: 200-400 word narrative explaining the DOL choice + KE jurisdiction routing + motor inrush rationale.

### Step 4: Author `uk-commercial-genset-changeover`

250 kVA standby diesel + ATS to MSB, UK office. Hybrid-mode (consumes db-layout-rollup for MSB context).

input.json: jurisdiction=GB, schematic_type=control_changeover, genset_kva=250, mains_source_priority=primary, transfer_time_s=10, consumed_intents=["db-layout-rollup"].

output.json:
- meta.consumed_intents = [{intent_type: "db-layout-rollup", intent_version: "1.3.1", produced_by: "db-layout"}]
- jurisdiction = "GB"
- schematic_type = "control_changeover"
- items[] = {K1 mains contactor 4-pole, K2 generator contactor 4-pole, KT1 transfer-delay timer, K3 mains-fail detection relay, breakers Q1 + Q2, plus standard auxiliary items}
- connections[] wiring mains-fail logic + transfer sequence
- sequence_of_operation: 8-step changeover (mains-OK → K1 closed; mains-fail → K3 detects → K1 opens after 0.5s confirm-delay → KT1 starts 10s genset-warmup → K2 closes → mains-restored → K1 closes with K2 retransfer timer)
- 6-section rationale + Compliance Assessment cites `BS 7671:2018+A2:2022 § 560 (safety services)` + `BS 7671 § 537 (transfer switches)` + `BS EN 61082`

### Step 5: Author `intl-hvac-vfd-control`

22 kW pump set with VFD + soft-start, IEC commercial. Hybrid-mode (consumes db-layout-rollup + fault-level).

input.json: jurisdiction=INT, schematic_type=control_sequence (VFD start sequence is multi-step), pump_kw=22, motor_voltage_v=400, vfd_type=soft_start_capable, consumed_intents=["db-layout-rollup", "fault-level"].

output.json:
- meta.consumed_intents = both intents
- schematic_type = "control_sequence"
- items[] = {K1 upstream isolator, KT1 soft-start enable timer, M1 pump motor, VFD controller (logic_gate device_class), F1 motor protection thermal, plus auxiliary}
- sequence_of_operation: 5-step VFD start (enable → soft-start ramp 0-3s → run permissive → at speed steady-state → stop ramp-down)
- 6-section rationale citing `IEC 60364-5-55` + `IEC 60947-4-2 (semiconductor motor controllers)` + `IEC 60617 IEC 617-12`

### Step 6: Author `us-industrial-star-delta`

15 HP star-delta starter, NEC industrial. Hybrid-mode (consumes db-layout-rollup).

input.json: jurisdiction=US, schematic_type=control_motor_starter (star-delta sub-class), motor_hp=15, motor_voltage_v=460, transition_time_s=7, consumed_intents=["db-layout-rollup"].

output.json:
- meta.consumed_intents = db-layout-rollup
- jurisdiction = "US"
- schematic_type = "control_motor_starter"
- items[] = {K1 main contactor, K2 star contactor, K3 delta contactor, KT1 transition timer 7s, F1 overload, M1 motor (US notation 460V 15HP), plus IEEE Std 315 symbols referenced}
- sequence_of_operation: star-delta logic (S1 START → K1+K2 energise simultaneously → motor runs in star for 7s → KT1 times out → K2 opens → K3 closes → motor runs in delta)
- 6-section rationale citing `NEC 2023 Article 430 (motor circuits)` + `NEC § 430.83 (controllers)` + `IEEE Std 315 (US symbol convention)`

### Step 7: Validate all 4 control examples against schematic-ir.schema.json

- [ ] Run:
```bash
python3 << 'EOF'
import json, jsonschema
schema = json.load(open('electrical/schematic/schemas/schematic-ir.schema.json'))
controls = ['ke-nairobi-workshop-motor-starter', 'uk-commercial-genset-changeover', 'intl-hvac-vfd-control', 'us-industrial-star-delta']
for ex in controls:
    d = json.load(open(f'electrical/schematic/examples/{ex}/output.json'))
    try: jsonschema.validate(d, schema); print(f'PASS {ex}')
    except jsonschema.ValidationError as e: print(f'FAIL {ex}: {e.message[:200]}')
EOF
```
Expected: 4/4 PASS.

### Step 8: Run harness — expect Pass 1 jump from 53 to 57

- [ ] Run:
```bash
python3 scripts/validate-examples.py 2>&1 | tail -3
```

Expected: Pass 1 = 57/57 (was 53; +4 control examples). Pass 2 + Pass 3 unchanged. AGGREGATE 147/147 exit 0.

### Step 9: Commit Task 7

- [ ] Run:
```bash
git add electrical/schematic/examples/
git commit -m "feat(schematic): Phase C Task 7 — 4 control schematic examples (KE workshop DOL + UK genset changeover + INT VFD sequence + US star-delta); leaf-mode + hybrid-consumer variants; KS/BS/IEC/NEC citation forms; Pass 1 goes 53→57/57"
```

## Task 7 Self-Review

- [ ] 4 control examples authored (each with input.json + output.json + reasoning.md)
- [ ] All 4 validate against schematic-ir.schema.json
- [ ] Cross-example consistency: each example's consumed_intents matches manifest declared consumes_intents
- [ ] Pass 1 reached 57/57

---

## Task 8: Protection schematics bundle (4 examples) — Opus

**Why Opus:** Protection schematics are specialist engineering. CT ratios + protection settings need defensible against device manufacturer typicals. Mirrors Task 7 pattern; this is the protection counterpart.

**Files:** Create 4 example directories:
- `electrical/schematic/examples/ke-industrial-transformer-protection/`
- `electrical/schematic/examples/uk-commercial-11kv-differential/`
- `electrical/schematic/examples/intl-substation-busbar-protection/`
- `electrical/schematic/examples/us-motor-protection-relay/`

### Step 1: Read Task 7 control bundle as precedent

- [ ] Read the 4 control examples committed in Task 7. Reuse the per-example shape (input.json + output.json + reasoning.md); adapt rationale section names for protection (replace "Sequence of Operation" with "Protection Coordination" type sections).

### Step 2: Author `ke-industrial-transformer-protection`

11 kV / 415 V step-down with IDMT overcurrent + restricted earth fault, KE industrial step-down. Hybrid-mode (consumes fault-level + earthing).

input.json: jurisdiction=KE, schematic_type=protection_overcurrent, hv_kv=11, lv_kv=0.415, transformer_kva=1000, ct_primary_a=100, ct_secondary_a=5, consumed_intents=["fault-level", "earthing"].

output.json:
- meta.consumed_intents = fault-level + earthing
- jurisdiction = "KE"
- schematic_type = "protection_overcurrent"
- items[] = {R51 IDMT 51, R87N restricted EF, T1 CT 100/5, Q1 breaker 11kV, K86 lockout, plus REF wiring}
- protection_settings[] = [
    {ansi_code: "51", device_id: "R51", set_value: 100, set_unit: "A primary", time_curve: "SI (standard inverse)", ct_ratio: "100/5", tool_call_pending: false},
    {ansi_code: "87N", device_id: "R87N", set_value: 5, set_unit: "% of CT secondary", ct_ratio: "100/5", tool_call_pending: false}
  ]
- 6-section rationale citing `KS 1700:2018 § X (route to BS 7671 via §313)` + `IEC 60255-151 (IDMT)` + `IEC 60044-1 (CT class 5P10)` + `IEC 61850-9-2`

### Step 3: Author `uk-commercial-11kv-differential`

11 kV intake transformer differential (87T), UK commercial intake. Hybrid-mode (consumes fault-level + db-layout-rollup).

input.json: jurisdiction=GB, schematic_type=protection_differential, hv_kv=11, lv_kv=0.4, transformer_mva=2.5, hv_vector_group=Dyn11, ct_primary_hv_a=200, ct_primary_lv_a=4000, consumed_intents=["fault-level", "db-layout-rollup"].

output.json:
- jurisdiction = "GB"
- schematic_type = "protection_differential"
- items[] = {R87T differential 87T, T1 HV CT 200/5, T2 LV CT 4000/5, Q1 HV breaker 52, Q2 LV breaker 52, K86 lockout, plus 50/51 backup}
- protection_settings[] = [
    {ansi_code: "87T", device_id: "R87T", set_value: 0.3, set_unit: "× In bias slope", ct_ratio: "200/5 HV + 4000/5 LV", tool_call_pending: false},
    {ansi_code: "51", device_id: "R51-BACKUP", set_value: 240, set_unit: "A primary (1.2 × FLA)", time_curve: "VI", ct_ratio: "200/5", tool_call_pending: false}
  ]
- 6-section rationale citing `BS 7671:2018+A2:2022 § 314` + `IEC 60255-187 (differential)` + `ENA G99 grid code` + `IEC 60044-1 (CT class 5P20)`

### Step 4: Author `intl-substation-busbar-protection`

HV substation busbar protection (87B + 50BF), IEC substation. Leaf-mode (HV substation has no shipped-skill upstream).

input.json: jurisdiction=INT, schematic_type=protection_busbar, busbar_voltage_kv=33, busbar_zones=2, breakers_per_zone=4, ct_primary_a=1200, ct_secondary_a=5, consumed_intents=[].

output.json:
- jurisdiction = "INT"
- schematic_type = "protection_busbar"
- items[] = {R87B-Z1 differential 87B zone 1, R87B-Z2 differential 87B zone 2, R50BF-Q1..Q4 breaker failure per breaker, Q1-Q8 breakers, T1-T8 CTs 1200/5, K86 lockouts per zone}
- protection_settings[] = [
    {ansi_code: "87B", device_id: "R87B-Z1", set_value: 0.5, set_unit: "× In bias", ct_ratio: "1200/5", tool_call_pending: false},
    {ansi_code: "50BF", device_id: "R50BF-Q1", set_value: 0.2, set_unit: "s breaker failure time", tool_call_pending: false}
    // ... per breaker
  ]
- 6-section rationale citing `IEC 60255-187` + `IEC 61850-9-2 (process bus)` + `IEC 60044-1 (CT class PX/PS for differential)` + `IEC 60099-4 (surge arrester reference)`

### Step 5: Author `us-motor-protection-relay`

600V industrial motor with 49 thermal + 50/51 overcurrent + 86 lockout, NEC industrial. Hybrid-mode (consumes db-layout-rollup + fault-level).

input.json: jurisdiction=US, schematic_type=protection_motor, motor_hp=150, motor_voltage_v=600, fla_a=140, locked_rotor_a=900, service_factor=1.15, consumed_intents=["db-layout-rollup", "fault-level"].

output.json:
- jurisdiction = "US"
- schematic_type = "protection_motor"
- items[] = {R49 thermal, R50 instantaneous, R51 IDMT, R86 lockout, T1 CT 200/5, Q1 breaker 52, B1 thermistor}
- protection_settings[] = [
    {ansi_code: "49", device_id: "R49", set_value: 140, set_unit: "A FLA (1.0× pickup with thermal Class 10)", ct_ratio: "200/5", tool_call_pending: false},
    {ansi_code: "50", device_id: "R50", set_value: 1200, set_unit: "A (1.3× locked rotor)", time_curve: "instantaneous", ct_ratio: "200/5", tool_call_pending: false},
    {ansi_code: "51", device_id: "R51", set_value: 175, set_unit: "A (1.25× FLA × service factor 1.15)", time_curve: "VI", ct_ratio: "200/5", tool_call_pending: false},
    {ansi_code: "86", device_id: "R86", set_value: "manual reset", set_unit: "n/a", tool_call_pending: false}
  ]
- 6-section rationale citing `NEC 2023 Article 430` + `NEC § 430.32 (overload)` + `NEC § 430.52 (short-circuit and ground-fault)` + `IEEE C37.96 (motor protection)` + `IEEE Std 315`

### Step 6: Validate all 4 protection examples + cross-example consistency

- [ ] Run:
```bash
python3 << 'EOF'
import json, jsonschema
schema = json.load(open('electrical/schematic/schemas/schematic-ir.schema.json'))
protections = ['ke-industrial-transformer-protection', 'uk-commercial-11kv-differential', 'intl-substation-busbar-protection', 'us-motor-protection-relay']
for ex in protections:
    d = json.load(open(f'electrical/schematic/examples/{ex}/output.json'))
    try:
        jsonschema.validate(d, schema)
        # Cross-check: protection_* type requires non-empty protection_settings
        assert d['schematic_type'].startswith('protection_')
        assert len(d.get('protection_settings', [])) > 0, f"{ex} has empty protection_settings"
        # Verify every protection_settings.device_id resolves to an items[].item_id
        item_ids = {it['item_id'] for it in d['items']}
        for ps in d['protection_settings']:
            assert ps['device_id'] in item_ids, f"{ex} protection_settings device_id {ps['device_id']} not in items"
        print(f'PASS {ex}')
    except (jsonschema.ValidationError, AssertionError) as e:
        print(f'FAIL {ex}: {str(e)[:200]}')
EOF
```
Expected: 4/4 PASS.

### Step 7: Run harness — expect Pass 1 jump from 57 to 61

- [ ] Run:
```bash
python3 scripts/validate-examples.py 2>&1 | tail -3
```

Expected: Pass 1 = 61/61 (was 57; +4 protection examples). AGGREGATE 151/151 exit 0.

### Step 8: Commit Task 8

- [ ] Run:
```bash
git add electrical/schematic/examples/
git commit -m "feat(schematic): Phase C Task 8 — 4 protection schematic examples (KE transformer IDMT+87N + UK 11kV differential 87T + INT substation busbar 87B/50BF + US motor 49/50/51/86); IEC 60255 / IEC 60044 / IEEE C37 citation forms; CT ratios + protection_settings defensible against manufacturer typicals; Pass 1 goes 57→61/61"
```

## Task 8 Self-Review

- [ ] 4 protection examples authored + cross-example consistency check passes
- [ ] Every protection_settings.device_id resolves to an items[].item_id
- [ ] ANSI function codes correctly mapped per IEEE C37.2
- [ ] Pass 1 reached 61/61

---

## Phase D — Evals + rules + inputs.json + bookkeeping (Tasks 9-11)

## Task 9: Evals authoring (~10 evals) — Opus

**Why Opus:** Eval design needs judgment about what to test + which observables matter.

**Files:** Create 10 eval YAMLs under `electrical/schematic/evals/`:
- eval-01-control-dol-happy-path.yaml
- eval-02-protection-idmt-happy-path.yaml
- eval-03-leaf-mode-fallback.yaml
- eval-04-missing-protection-setting.yaml
- eval-05-intent-cascade-verified.yaml
- eval-06-jurisdiction-citation-form.yaml
- eval-07-rationale-block.yaml
- eval-08-symbol-library-resolution.yaml
- eval-09-banned-annotation-trap.yaml
- eval-10-schematic-type-classification.yaml

### Step 1: Read canonical eval shape

- [ ] Read `electrical/lighting-layout/evals/eval-01-office-happy-path.yaml` for canonical Format A (post-3W2a) shape: name + skill + description + category + input + checks[].

### Step 2: Author the 10 evals

Each eval follows the post-3W2a canonical shape:

```yaml
name: eval-NN-<slug>
skill: schematic
description: >
  <One-line summary>
category: <happy_path | edge_case | compliance_failure | cross_validation | skill_specific | validation_trap | rationale_block | jurisdiction_switch>

input:
  <inline input dict matching inputs.json items[]>

checks:
  - assertion: <jsonpath operator value>
    description: <human-readable rationale>
    severity: <critical | warning | info>
    standard_ref: <optional>
```

Per spec §3 Phase D Task 9, the 10 evals cover:
1. **eval-01 (happy_path, control)**: control_motor_starter DOL on a 11 kW grinder; checks: schema_valid, schematic_type == "control_motor_starter", items.length >= 5, sequence_of_operation != null
2. **eval-02 (happy_path, protection)**: protection_overcurrent IDMT on 11 kV transformer; checks: schema_valid, schematic_type == "protection_overcurrent", protection_settings.length >= 1, ansi_codes contain "51"
3. **eval-03 (edge_case, leaf-mode)**: control_motor_starter with no consumed_intents; checks: schema_valid, meta.consumed_intents.length == 0, compliance_summary.assumptions contains "leaf-mode"
4. **eval-04 (compliance_failure)**: protection_overcurrent missing protection_settings; checks: schema validation FAILS at oneOf branch (negative test — input crafted to violate)
5. **eval-05 (cross_validation)**: hybrid-consumer with db-layout-rollup; checks: meta.consumed_intents contains intent_type "db-layout-rollup"
6. **eval-06 (jurisdiction_switch)**: same DOL motor starter across KE/UK/INT/US (4 input_fixtures, citation form variance); checks: KE citations route to BS 7671; UK uses BS 7671 directly; INT uses IEC; US uses NEC
7. **eval-07 (rationale_block)**: chat_summary 40-500 chars + sections.length 6-9
8. **eval-08 (skill_specific)**: every items[].bs_en_60617_ref resolves to a file under shared/symbols/electrical/schematic/
9. **eval-09 (validation_trap)**: ban check — assertion "ir matches "switch-fuse"" must NOT match (banned annotation)
10. **eval-10 (skill_specific)**: schematic_type ↔ items consistency (control_motor_starter requires contactor; protection_overcurrent requires idmt or instantaneous relay)

### Step 3: Validate all 10 evals against shared/schemas/core/eval.schema.json

- [ ] Run:
```bash
python3 << 'EOF'
import json, yaml, jsonschema, glob
schema = json.load(open('shared/schemas/core/eval.schema.json'))
files = sorted(glob.glob('electrical/schematic/evals/eval-*.yaml'))
print(f'Files: {len(files)}')
for f in files:
    d = yaml.safe_load(open(f))
    try: jsonschema.validate(d, schema); print(f'PASS {f}')
    except jsonschema.ValidationError as e: print(f'FAIL {f}: {e.message[:160]}')
EOF
```
Expected: 10/10 PASS.

### Step 4: Run harness — expect Pass 2 jump from 81 to 91

- [ ] Run:
```bash
python3 scripts/validate-examples.py 2>&1 | tail -3
```
Expected: Pass 2 = 91/91 (was 81; +10 evals). AGGREGATE 161/161 exit 0 (53+91+9=153 + 8 schematic examples = 161; or 53+8=61 + 81+10=91 + 9 = 161 — wait that's only 161 not 162. Let me recalc: Pass 1 = 53 + 8 = 61. Pass 2 = 81 + 10 = 91. Pass 3 = 9. Total = 61 + 91 + 9 = 161. Discrepancy from spec's 162. Spec said 162/162. The off-by-one is because spec assumed 1 new inputs.json adds 1 to Pass 3; that's 9 + 1 = 10. So total = 61 + 91 + 10 = 162.)

After Task 9 (just evals added, no new inputs.json yet): Pass 1 = 61, Pass 2 = 91, Pass 3 = 9 (unchanged until Task 10 adds inputs.json). AGGREGATE = 161/161 exit 0.

### Step 5: Commit Task 9

- [ ] Run:
```bash
git add electrical/schematic/evals/
git commit -m "feat(schematic): Phase D Task 9 — 10 evals (control + protection happy_path, leaf-mode edge_case, compliance_failure, intent cascade cross_validation, jurisdiction_switch, rationale_block, symbol library resolution, banned annotation trap, schematic_type classification); all conform to post-3W2a canonical eval.schema.json; Pass 2 goes 81→91/91"
```

## Task 9 Self-Review

- [ ] 10 evals authored, all canonical Format A
- [ ] All 10 validate against eval.schema.json
- [ ] Each carries category from the 9-value post-3W2a enum
- [ ] Pass 2 reached 91/91

---

## Task 10: Rules + constraints + validation + inputs.json (Sonnet)

**Why Sonnet:** Mechanical YAML/JSON authoring with explicit per-file content.

**Files:**
- 5 rules YAMLs under `electrical/schematic/rules/`
- 3 constraints/validation YAMLs under `electrical/schematic/constraints/` + `electrical/schematic/validation/`
- 1 inputs.json

### Step 1: Author 5 rules YAMLs

For each rule, write a YAML at `electrical/schematic/rules/<name>.yaml` following this template:

```yaml
rule_id: <SLUG>
rule_name: <Human readable>
applies_to_schematic_type: [<schematic_type values where rule fires>]
description: |
  <Engineering rationale>
checks:
  - check_id: <slug>
    expression: <evaluable expression>
    severity: <critical | warning | info>
    standard_ref: <citation>
```

5 rules:
1. `motor-protection-coordination.yaml` — 49 thermal vs motor full-load curve (thermal pickup ≤ 1.0× FLA × service factor; Class 10/20/30 selectable per motor service)
2. `contactor-rating.yaml` — AC-3 utilisation category for motor inrush; AC-1 for resistive loads; coordination with overload Class
3. `overload-class.yaml` — Class 5 (start ≤ 5s) / Class 10 (≤ 10s) / Class 20 (≤ 20s) / Class 30 (≤ 30s) per motor start-time
4. `differential-stability.yaml` — bias slope 30-50% + stabilising resistor sizing per IEC 60255-187 + CT class PX/PS for high-impedance differential
5. `busbar-protection-zoning.yaml` — zone-overlap with breaker failure 50BF; 87B trip → 50BF backup if breaker fails within 0.2s

### Step 2: Author 3 constraints/validation YAMLs

3 files at `electrical/schematic/constraints/` + `electrical/schematic/validation/`:

1. `constraints/schema-cross-references.yaml`:
```yaml
constraint_id: SCHEMA_CROSS_REFS
description: |
  Every items[].bs_en_60617_ref must resolve to a JSON file under shared/symbols/electrical/schematic/.
  Every connections[].from_item + to_item must resolve to an items[].item_id.
  Every protection_settings[].device_id must resolve to an items[].item_id.
checks:
  - check_id: symbol_resolution
    description: items[].bs_en_60617_ref → file existence
    severity: critical
  - check_id: connection_endpoints
    description: connections[].from_item + to_item → items[].item_id existence
    severity: critical
  - check_id: protection_device_resolution
    description: protection_settings[].device_id → items[].item_id existence
    severity: critical
```

2. `constraints/protection-coordination.yaml`:
```yaml
constraint_id: PROTECTION_COORDINATION
description: |
  Cascade selectivity rules. Upstream device must not trip before downstream device at the
  protected node's PFC. Protection settings must be defensible against device manufacturer
  typicals (ABB REF615, Siemens 7UM62, Schneider Sepam reference points).
checks:
  - check_id: cascade_selectivity
    description: Upstream operating time at downstream's max fault ≥ downstream operating time + grading margin
    severity: warning
  - check_id: typical_setting_envelope
    description: Set values within ±20% of manufacturer typical for the protection function
    severity: warning
```

3. `validation/banned-annotations.yaml`:
```yaml
validator_id: BANNED_ANNOTATIONS
description: |
  Post-3W2c lesson set. The following patterns are banned in schematic IR + rationale text.
banned_patterns:
  - pattern: switch-fuse
    replacement: main_switch_fused
    severity: warning
    reason: "Canonical enum per Sprint 3-W2a Task 1; switch-fuse is informal."
  - pattern: '§ 311(?![.0-9])'
    replacement: '§ 311.1'
    severity: warning
    reason: "§ 311 is the chapter heading; § 311.1 is the operative regulation. Lesson from 3-W2c Task 1 UK-3."
  - pattern: 'BS EN 61009-1:2012(?!\+)'
    replacement: 'BS EN 61009-1:2012+A12:2014'
    severity: warning
    reason: "Lesson from 3-W2c Task 1 UK-4 — current edition includes A12:2014 amendment."
  - pattern: '\(\d+\.\d+% of 230V phase reference\)'
    replacement: '<absolute voltage drop in volts>'
    severity: critical
    reason: "Lesson from 3-W2c Task 1 UK-1 fix — dual-frame VD % is dimensionally wrong for balanced 3-phase circuits."
  - pattern: IEC 60364-7-701 series \(water proximity\) for kitchen
    replacement: <use § 411.3.3 universal socket-circuit policy>
    severity: warning
    reason: "Lesson from 3-W2c Task 1 INT-1 — IEC 60364-7-701 is bathroom-specific, not commercial-kitchen."
```

### Step 3: Author `electrical/schematic/inputs.json`

This is the WI1 InputItem taxonomy. ~25-30 items branching by schematic_type.

- [ ] Read shared/schemas/core/inputs.schema.json to confirm InputItem shape (id + label + answer_type + required + optional fields like options + depends_on + project_fact_candidate).

Author `electrical/schematic/inputs.json`:

```json
{
  "$schema": "../../shared/schemas/core/inputs.schema.json",
  "skill": "schematic",
  "version": "1.0.0",
  "items": [
    {
      "id": "jurisdiction",
      "label": "Project jurisdiction",
      "hint": "GB=BS 7671; KE=KS 1700 routing to BS 7671 via §313; INT=IEC 60364; US=NEC 2023.",
      "answer_type": "enum",
      "options": ["GB", "EU", "INT", "US", "KE"],
      "required": true,
      "project_fact_candidate": true
    },
    {
      "id": "schematic_type",
      "label": "Schematic type",
      "hint": "Choose control_* for control schemes; protection_* for relay schemes.",
      "answer_type": "enum",
      "options": [
        "control_motor_starter", "control_changeover", "control_sequence",
        "protection_overcurrent", "protection_differential", "protection_motor", "protection_busbar"
      ],
      "required": true
    },
    {
      "id": "consumed_intents_present",
      "label": "Which upstream intents are available?",
      "hint": "Leaf-mode fallback if all absent.",
      "answer_type": "enum_list",
      "options": ["db-layout-rollup", "fault-level", "earthing"],
      "required": false
    }
  ]
}
```

Add 22-27 more items branching by schematic_type. For control_motor_starter: motor_rating_kw, motor_voltage_v, fla_a, upstream_breaker_rating_a. For protection_overcurrent: ct_primary_a, ct_secondary_a, transformer_kva. For protection_differential: hv_kv, lv_kv, transformer_kva, vector_group, bias_slope_percent. Etc.

Use `depends_on` to branch:
```json
{
  "id": "motor_rating_kw",
  "label": "Motor rating (kW)",
  "answer_type": "float",
  "required": true,
  "depends_on": ["schematic_type"],
  "hint": "Required for control_motor_starter / control_sequence / protection_motor."
}
```

### Step 4: Validate inputs.json against shared/schemas/core/inputs.schema.json

- [ ] Run:
```bash
python3 -c "
import json, jsonschema
schema = json.load(open('shared/schemas/core/inputs.schema.json'))
data = json.load(open('electrical/schematic/inputs.json'))
jsonschema.validate(data, schema)
print('inputs.json PASS')
"
```
Expected: PASS.

### Step 5: Run harness — Pass 3 jump from 9 to 10

- [ ] Run:
```bash
python3 scripts/validate-examples.py 2>&1 | tail -3
```
Expected: Pass 1 = 61, Pass 2 = 91, Pass 3 = 10. AGGREGATE 162/162 exit 0.

### Step 6: Commit Task 10

- [ ] Run:
```bash
git add electrical/schematic/rules/ electrical/schematic/constraints/ electrical/schematic/validation/ electrical/schematic/inputs.json
git commit -m "feat(schematic): Phase D Task 10 — 5 rules YAMLs (motor-protection-coordination + contactor-rating + overload-class + differential-stability + busbar-protection-zoning) + 3 constraints/validation YAMLs (schema-cross-references + protection-coordination + banned-annotations) + inputs.json with items[] taxonomy; banned-annotations captures Sprint 3-W2c lessons; Pass 3 goes 9→10/10; AGGREGATE 162/162 FULL GREEN"
```

## Task 10 Self-Review

- [ ] 5 rules YAMLs authored
- [ ] 3 constraints/validation YAMLs authored (incl. post-3W2c lesson set)
- [ ] inputs.json validates against shared/schemas/core/inputs.schema.json
- [ ] Pass 3 reached 10/10
- [ ] AGGREGATE 162/162 FULL GREEN

---

## Task 11: Bookkeeping (Sonnet)

**Why Sonnet:** Mechanical updates to status docs + cross-cutting verification.

**Files:**
- Modify: `SKILLS_STATUS.md`
- Modify: `CLAUDE.md` (build-status section)
- Modify: `ARCHITECTURE.md` (if a new cross-skill pattern surfaced — probably no)

### Step 1: Update `SKILLS_STATUS.md`

- [ ] Read the existing file. Locate the electrical drawings table. Update schematic row:
- Status: `STUB` → `SHIPPED v1.0.0`
- Add row to "Recent shipping" section: `schematic v1.0.0 (2026-05-22) — 8 examples, hybrid consumer of db-layout-rollup + fault-level + earthing`

### Step 2: Update `CLAUDE.md` build status

- [ ] Read the build-status section. Update:
- Drawings: 6 of 8 shipped (was 5) — schematic v1.0 now ships
- Update remaining list: 2 drawings (cable-containment, riser)

### Step 3: Check ARCHITECTURE.md

- [ ] Read existing file. If hybrid-consumer pattern is already documented (it is, from small-power v1.1), no update needed. If not, add a short paragraph crediting small-power v1.1 + schematic v1.0 as the canonical hybrid-consumer pattern.

### Step 4: Final harness check

- [ ] Run:
```bash
python3 scripts/validate-examples.py 2>&1 | tail -6
```
Expected: AGGREGATE 162/162 exit 0.

### Step 5: Commit Task 11

- [ ] Run:
```bash
git add SKILLS_STATUS.md CLAUDE.md ARCHITECTURE.md
git commit -m "docs(schematic): Phase D Task 11 — bookkeeping; SKILLS_STATUS schematic STUB→SHIPPED v1.0.0; CLAUDE.md build status 6/8 drawings shipped (was 5/8); 2 drawings remaining (cable-containment + riser)"
```

## Task 11 Self-Review

- [ ] SKILLS_STATUS updated
- [ ] CLAUDE.md build-status reflects 10 shipped skills
- [ ] AGGREGATE still 162/162

---

## Phase E — Final ship (Task 12, Opus)

## Task 12: Final validation + push + memory save (Opus)

**Why Opus:** Ship-readiness judgment + memory authoring.

### Step 1: Run the 3-pass harness

- [ ] Run:
```bash
python3 scripts/validate-examples.py
```

Expected:
```
Subtotal: 61/61 pass
Subtotal: 91/91 pass
Subtotal: 10/10 pass
=== AGGREGATE: 162/162 pass (0 failures) ===
```
Exit code: 0.

### Step 2: Cross-skill cascade audit — verify 3 new producer→consumer pairs

- [ ] Run:
```bash
python3 << 'EOF'
import json
shipped = ['arc-flash', 'arc-flash-labelling', 'cable-sizing', 'db-layout', 'earthing', 'fault-level', 'lighting-layout', 'sld', 'small-power', 'schematic']
producers = {}
for s in shipped:
    m = json.load(open(f'electrical/{s}/skill.manifest.json'))
    p = m.get('produces_intent')
    if isinstance(p, str): producers[p] = s
    elif isinstance(p, list):
        for pp in p: producers[pp] = s
pairs = []
for s in shipped:
    m = json.load(open(f'electrical/{s}/skill.manifest.json'))
    for c in (m.get('consumes_intents') or []):
        producer = producers.get(c, '???')
        pairs.append((producer, c, s))
print(f'Total pairs: {len(pairs)}')
schematic_pairs = [p for p in pairs if p[2] == 'schematic']
print(f'\nSchematic consumes (3 expected):')
for p in schematic_pairs: print(f'  {p[0]} produces "{p[1]}" → consumed by schematic')
EOF
```

Expected: 18 total pairs (15 previous + 3 schematic-new). Schematic-new pairs:
- db-layout produces "db-layout-rollup" → consumed by schematic
- fault-level produces "fault-level" → consumed by schematic
- earthing produces "earthing" → consumed by schematic

### Step 3: Confirm git state

- [ ] Run:
```bash
git log --oneline origin/main..HEAD
git status
```
Expected: 12 task commits + 2 doc commits (spec + plan) ahead of origin/main; clean working tree.

### Step 4: Push to origin/main

- [ ] Run:
```bash
git push origin main
```
Expected: clean push, no force, hooks pass.

After push:
```bash
git log --oneline origin/main..HEAD
```
Expected: empty.

### Step 5: Save schematic-shipped memory

- [ ] Write `/Users/linus/.claude/projects/-Users-linus-Desktop-DraftsMan-SKills-draftsman-skills/memory/schematic-shipped.md`:

```markdown
---
name: schematic-shipped
description: Schematic skill v1.0.0 shipped 2026-05-22 — 10th electrical skill; control + protection schematics across 4 jurisdictions (KE/UK/INT/US); hybrid consumer of db-layout-rollup + fault-level + earthing with leaf-mode fallback; harness AGGREGATE 162/162 FULL GREEN
metadata:
  type: project
---

**✅ SHIPPED 2026-05-22 — Schematic Skill v1.0.0** (commits dd1149d..<TIP_SHA>, pushed to origin/main)

10th electrical skill. Closes 6 of 8 drawings (cable-containment + riser remain). Hybrid consumer of 3 upstream intents.

## What was delivered

- Per-schematic IR + intent schemas (7-value schematic_type enum with oneOf branching)
- 40 BS EN 60617 symbols across 4 subcategories (motor_starter / protection / auxiliary / control_logic)
- 3 prompts (generator 12-step / validator 10 INV / reviewer 6 D)
- 8 jurisdictional examples: 4 control (KE workshop DOL + UK genset changeover + INT VFD + US star-delta) + 4 protection (KE transformer IDMT+87N + UK 11kV differential + INT busbar protection + US motor 49/50/51/86)
- 10 evals (post-3W2a canonical Format A)
- 5 rules YAMLs + 3 constraints/validation YAMLs (including post-3W2c banned-annotations lesson set)
- inputs.json with ~25-30 items[] taxonomy
- Bookkeeping (SKILLS_STATUS + CLAUDE.md + ARCHITECTURE.md updates)

## Harness state

- Pass 1 (examples): 61/61 (53 baseline + 8 schematic)
- Pass 2 (evals): 91/91 (81 baseline + 10 schematic)
- Pass 3 (inputs.json): 10/10 (9 baseline + 1 schematic)
- AGGREGATE: 162/162 exit 0 (FULL GREEN held)

## Cross-skill graph (15 → 18 pairs)

3 new producer→consumer pairs verified clean:
- db-layout → "db-layout-rollup" → schematic
- fault-level → "fault-level" → schematic
- earthing → "earthing" → schematic

## Known follow-up (v1.1)

- BS EN 60617 symbol library expansion (~200 total)
- Sequence-of-operation TEXT generation (extended prose)
- Ladder-logic / PLC ST code emission (IEC 61131-3)
- HV substation protection beyond busbar (distance, autoreclose)
- US protection beyond motor + transformer (27/59/81 generator)
- 3-W2c carried items: lighting-layout content overhaul; Bucket C Tier-4 evals

## Cross-references

- [[sprint-3w2c-shipped]] — predecessor; runtime-ready baseline
- [[small-power-v1.1-shipped]] — hybrid consumer precedent
- [[runtime-project-boundary]]
- [[feedback-no-haiku-sonnet-opus-only]]
- [[build-strategy-breadth-first]]

## How to apply

- Schematic v1.0 ships the full control + protection coverage in 4 jurisdictions
- 2 drawings remain: cable-containment + riser
- Skills repo runtime-readiness preserved (harness 162/162; 18 producer/consumer pairs)
- Next sprint should be either cable-containment / riser OR a runtime-testing pause
```

### Step 6: Update MEMORY.md index

- [ ] Read `/Users/linus/.claude/projects/.../memory/MEMORY.md`. Add an entry after the most recent sprint entry:

```markdown
- [Schematic shipped](schematic-shipped.md) — 2026-05-22: 10th electrical skill; control + protection schematics across 4 jurisdictions; hybrid consumer; harness AGGREGATE 162/162 FULL GREEN
```

### Step 7: Report to user

- [ ] Final summary (≤ 8 lines):
- Push status (success + final SHA)
- Harness 3-pass result + AGGREGATE
- Schematic v1.0 shipped (10th electrical skill)
- 3 new producer→consumer pairs verified
- Memory file path
- 2 drawings remaining (cable-containment + riser)
- Next focal point: cable-containment OR riser OR runtime testing pause

## Task 12 Self-Review

- [ ] Harness 162/162 exit 0 confirmed
- [ ] 3 new producer→consumer pairs documented + verified
- [ ] Push succeeded
- [ ] Memory + index updated
- [ ] User report includes runtime-ready declaration

---

## Risks & Mitigations

- **R1 — IR schema complexity.** *Mitigation:* Task 2 writes positive + negative tests for each oneOf branch before downstream consumes. Halt if Task 2 > 1 dev-day.
- **R2 — Symbol library scope creep.** *Mitigation:* Task 3 freezes the ~40-symbol list at start. v1.1 territory beyond.
- **R3 — Cross-skill cascade test failure.** *Mitigation:* Task 12 Step 2 explicit audit; halt before push if fails.
- **R4 — Protection schematic engineering depth.** *Mitigation:* Task 8 dispatch carries explicit manufacturer typical references (ABB REF615, Siemens 7UM62, Schneider Sepam). Defer-with-note if a setting can't be grounded.
- **R5 — Numeric refinement reversal (3-W2c lesson).** *Mitigation:* validation/banned-annotations.yaml explicitly captures the dual-frame VD % regression. Task 4 prompt cites it.
- **R6 — Prompt drift from post-3W2c additions.** *Mitigation:* Tasks 4-6 implementer reads `electrical/db-layout/prompts/generator.md` (post-3W2c) as the canonical reference.
- **R7 — Inputs.json depends_on graph cycles.** *Mitigation:* Task 10 Step 4 validates against shared/schemas/core/inputs.schema.json + the depends_on graph integrity check from 3-W2c.
- **R8 — Eval count + harness baseline shift.** *Mitigation:* Tasks 7-10 each run harness after commit; any regression below 143 halts.
- **R9 — Runtime testing deferred.** *Mitigation:* Task 12 commit message acknowledges runtime testing may surface issues this sprint can't see.

---

## Self-Review

**Spec coverage check:**
- §1 locked decisions D1-D6 ✓ — D1 scope reflected in Tasks 7+8; D2 hybrid consumer in Task 1 manifest + Task 4 generator + Task 7+8 examples; D3 produces_intent in Task 1+2; D4 per-schematic IR in Task 2; D5 ~40 symbols in Task 3; D6 banned-annotations in Task 10
- §2 scope (8 examples + IR shape + jurisdictions) ✓ — Tasks 7+8 author the 8 examples; Task 2 the IR; Tasks 4-6 the per-jurisdiction citation guidance
- §3 phases A-E ✓ mapped to Tasks 1-12
- §4 file ops ~80-90 ✓ — actual estimate: 40 symbols + 1 manifest + 1 README + 1 CHANGELOG + 1 ontology + 1 IR schema + 1 intent schema + 3 prompts + 8 examples × 3 files = 24 + 10 evals + 5 rules + 3 constraints/validation + 1 inputs.json = 89
- §5 risks R1-R9 ✓ mirrored
- §6 acceptance (162/162 + 3 new pairs + post-3W2c-aligned + 12 commits) ✓ Task 12 verification
- §7 out-of-scope handoff ✓ Task 12 memory file
- §8 model selection (Sonnet × 4 + Opus × 8) ✓ — Tasks 1, 3, 10, 11 Sonnet; Tasks 2, 4, 5, 6, 7, 8, 9, 12 Opus
- §9 sprint workflow ✓ Task 12 closes loop

**Placeholder scan:** No TBD/TODO/"implement later". Every code/prose step shows the actual content. The symbol-library breakdown trim from 13 → 10 (Step 5 Task 3) is documented explicitly. Memory file template marks `<TIP_SHA>` as fill-in-when-known (Task 12 Step 5).

**Type consistency:**
- `schematic_type` 7-value enum consistent (Task 2 schema + Task 4 generator + Task 9 eval categories + Task 10 inputs.json options + Task 12 cross-check)
- `device_class` enum consistent (Task 2 schema + Task 3 symbol category mapping)
- `ansi_function_code` pattern `^[0-9]{1,3}[A-Z]?(T|B|N|G)?$` consistent (Task 2 schema)
- File paths: `electrical/schematic/<subdir>/<file>` consistent across all tasks
- Memory file path: `/Users/linus/.claude/projects/-Users-linus-Desktop-DraftsMan-SKills-draftsman-skills/memory/schematic-shipped.md` consistent
- AGGREGATE arithmetic: 53+8=61 (Pass 1) + 81+10=91 (Pass 2) + 9+1=10 (Pass 3) = 162. Verified.
- 15 + 3 = 18 producer/consumer pairs after schematic ships. Verified.
