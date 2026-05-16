# `draftsman-skills` Upstream Contributions — Work Spec

**Repo target:** https://github.com/LinusN191/draftsman-skills
**Date:** 2026-05-14
**Author:** Linus + Claude (DraftsMan runtime side)
**For:** The agent working on `draftsman-skills` so it can act in parallel while the DraftsMan runtime is being restructured

---

## Why this exists

DraftsMan is migrating to a **skill-driven architecture**: engineering domain
knowledge (prompts, standards, rules, schemas, evals) lives in
`draftsman-skills`; the DraftsMan repo becomes a runtime that loads any
valid skill and renders its IR output to DXF / LISP / SVG / PDF.

The contract between the two layers is the **IR JSON document** — produced
by the AI using the skill's generator prompt, validated against the skill's
IR JSON Schema, consumed by the runtime renderer.

This document specifies **5 upstream work items** that need landing on
`draftsman-skills` so DraftsMan can implement the runtime side without
blocking on schema drift. Each work item is self-contained, has acceptance
criteria, and can land as an independent PR.

> The agent picking this up should treat `electrical/lighting-layout` as
> the reference skill — it's currently the only `status: production` skill
> and should be the first one updated for each work item below.

---

## How the layers split

| Concern | Owned by | Why |
|---------|----------|-----|
| Question taxonomy (what to ask the engineer) | Skill repo | Engineering knowledge; same across runtimes |
| Standards values (BS 7671 tables etc.) | Skill repo (`shared/standards/`) | Versioned, jurisdiction-tagged data |
| Generator prompt (LLM reasoning steps) | Skill repo (`prompts/generator.md`) | Engineering reasoning |
| Rule definitions (`if X then Y`) | Skill repo (`rules/`, `constraints/`) | Engineering judgement |
| Calculation definitions (formulas + execution mode) | Skill repo (`shared/calculations/`, skill-local overrides) | Engineering math + safety classification |
| Evaluations (eval YAMLs) | Skill repo (`evals/`) | Behavioural spec of the skill |
| IR JSON Schema | Skill repo (`schemas/`, `shared/schemas/`) | Contract surface |
| Cross-drawing declarations | Skill repo (`skill.manifest.json`) | Domain dependency graph |
| --- | --- | --- |
| Python tool implementations | DraftsMan runtime | Math precision; deterministic execution |
| Discovery chat Q&A driver | DraftsMan runtime | UX layer |
| LLM call + IR validation | DraftsMan runtime | Operational |
| DXF/LISP/SVG rendering | DraftsMan runtime | Output format |
| Storage + auth + chat state | DraftsMan runtime | Infrastructure |
| Eval CI + skill registry + production gating | DraftsMan runtime | Operational |

---

## Work Item 1 — Discovery richness via `inputs.json` per skill

**Status:** new file per skill; current `inputs: [...]` array in manifest stays for back-compat but moves to a richer adjacent schema.

### Problem

`skill.manifest.json` currently lists inputs as bare strings:
```json
"inputs": ["room-dimensions", "ceiling-height", "room-type", ...]
```

Runtimes can't drive a chat-based discovery interview from this — they
don't know question text, answer types, validation rules, defaults,
dependencies, or display order.

### Solution

Add a new file `inputs.json` per skill at the same level as `skill.manifest.json`.
Manifest gets a new key `inputs_path: "inputs.json"` pointing to it.

### File: `electrical/lighting-layout/inputs.json` (example)

```json
{
  "$schema": "../../shared/schemas/core/inputs.schema.json",
  "skill": "lighting-layout",
  "version": "1.0.0",
  "items": [
    {
      "id": "room_type",
      "label": "Room type / occupancy",
      "hint": "Determines lux target, UGR limit, and Ra minimum per BS EN 12464-1 Table 5.3",
      "answer_type": "enum",
      "options": [
        "open_plan_office",
        "private_office",
        "meeting_room",
        "corridor",
        "warehouse",
        "classroom",
        "consulting_room",
        "ward",
        "kitchen_commercial",
        "bathroom",
        "reception_lobby"
      ],
      "required": true,
      "project_fact_candidate": false
    },
    {
      "id": "room_length_mm",
      "label": "Room length (mm, internal clear)",
      "answer_type": "int",
      "required": true,
      "validator": "in_range_500_100000",
      "project_fact_candidate": false
    },
    {
      "id": "room_width_mm",
      "label": "Room width (mm, internal clear)",
      "answer_type": "int",
      "required": true,
      "validator": "in_range_500_100000"
    },
    {
      "id": "ceiling_height_mm",
      "label": "Ceiling height (mm AFF)",
      "answer_type": "int",
      "required": true,
      "validator": "in_range_2000_20000",
      "project_fact_candidate": true
    },
    {
      "id": "luminaire_lumens",
      "label": "Luminaire lumen output (lm)",
      "hint": "State whether this is INITIAL (rated at t=0) or DESIGN/MAINTAINED lumens",
      "answer_type": "int",
      "required": true
    },
    {
      "id": "lumen_type",
      "label": "Lumen value type",
      "answer_type": "enum",
      "options": ["initial", "design", "unknown"],
      "required": true,
      "depends_on": ["luminaire_lumens"]
    },
    {
      "id": "ceiling_grid_mm",
      "label": "Ceiling grid module (mm)",
      "answer_type": "int",
      "default": 600,
      "required": false
    },
    {
      "id": "is_uk_new_build",
      "label": "UK new-build or major refurbishment?",
      "hint": "Triggers Part L 2021 compliance checks",
      "answer_type": "boolean",
      "default": false,
      "required": false
    },
    {
      "id": "controls_protocol",
      "label": "Lighting controls protocol",
      "answer_type": "enum",
      "options": ["none", "switched", "0-10V", "DALI", "DALI-2"],
      "default": "none",
      "required": false
    },
    {
      "id": "luminaire_environment",
      "label": "Installation environment",
      "answer_type": "enum",
      "options": ["normal", "bathroom_zone_1", "bathroom_zone_2",
                  "kitchen_commercial", "external_covered", "car_park"],
      "default": "normal",
      "required": false
    },
    {
      "id": "db_designation",
      "label": "Distribution board designation",
      "hint": "E.g. DB-L1; links to db-layout + cable-sizing skills",
      "answer_type": "text",
      "required": false
    }
  ]
}
```

### `inputs.json` schema — `shared/schemas/core/inputs.schema.json`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "shared/schemas/core/inputs.schema.json",
  "title": "Skill inputs schema",
  "type": "object",
  "required": ["skill", "version", "items"],
  "properties": {
    "skill":   { "type": "string" },
    "version": { "type": "string" },
    "items": {
      "type": "array",
      "items": { "$ref": "#/definitions/InputItem" }
    }
  },
  "definitions": {
    "InputItem": {
      "type": "object",
      "required": ["id", "label", "answer_type", "required"],
      "properties": {
        "id":           { "type": "string", "pattern": "^[a-z][a-z0-9_]*$" },
        "label":        { "type": "string" },
        "hint":         { "type": "string" },
        "answer_type": {
          "enum": ["enum", "int", "float", "boolean", "text", "enum_list", "struct_list"]
        },
        "options":      { "type": "array", "items": { "type": "string" } },
        "default":      { },
        "required":     { "type": "boolean" },
        "validator":    { "type": "string" },
        "depends_on":   { "type": "array", "items": { "type": "string" } },
        "project_fact_candidate": { "type": "boolean" },
        "item_schema": {
          "description": "When answer_type=struct_list, the shape of each list element",
          "type": "object"
        }
      }
    }
  }
}
```

### Validators registry — `shared/validation/validators.json`

Named validators referenced by `validator: "..."` strings. Examples engineers actually need:

```json
{
  "in_range_1_2000_A":       { "kind": "int_range",   "min": 1,    "max": 2000   },
  "in_range_500_100000":     { "kind": "int_range",   "min": 500,  "max": 100000 },
  "in_range_2000_20000":     { "kind": "int_range",   "min": 2000, "max": 20000  },
  "positive_int":            { "kind": "int_range",   "min": 1 },
  "positive_float":          { "kind": "float_range", "min_exclusive": 0 },
  "non_empty_text":          { "kind": "text_length", "min": 1 },
  "valid_isodate":           { "kind": "regex", "pattern": "^\\d{4}-\\d{2}-\\d{2}$" }
}
```

### `struct_list` example — for cable-containment's runs table

```json
{
  "id": "runs",
  "label": "Containment runs",
  "answer_type": "struct_list",
  "required": true,
  "item_schema": {
    "type": "object",
    "required": ["name", "floor_id", "orientation", "voltage_class", "family"],
    "properties": {
      "name":             { "type": "string" },
      "floor_id":         { "type": "string" },
      "orientation":      { "enum": ["horizontal", "vertical_riser"] },
      "voltage_class":    { "enum": ["LV_power", "ELV_control", "comms_data",
                                     "fire_alarm", "emergency_lighting"] },
      "family":           { "enum": ["cable_tray", "cable_basket", "cable_ladder",
                                     "cable_trunking", "conduit"] },
      "material":         { "type": "string" },
      "ip_rating":        { "type": "string" },
      "fire_rated":       { "type": "boolean" },
      "cpc_strategy":     { "enum": ["separate_conductor", "containment_as_cpc", "both"] },
      "approximate_length_m": { "type": "number", "exclusiveMinimum": 0 },
      "floors_served":    { "type": "array", "items": { "type": "integer" } },
      "assigned_circuit_ids": { "type": "array", "items": { "type": "string" } }
    }
  }
}
```

### Manifest update

Add to `skill.manifest.json`:
```json
"inputs_path": "inputs.json"
```

The old `inputs: [...]` array can stay as a quick-reference summary or be removed in v2.

### Acceptance criteria

- [ ] `shared/schemas/core/inputs.schema.json` exists and validates against draft-07
- [ ] `shared/validation/validators.json` lists at minimum the validators referenced by lighting-layout
- [ ] `electrical/lighting-layout/inputs.json` exists, validates against the schema, contains all required + optional inputs from the current generator prompt's "Inputs Required" section
- [ ] `electrical/lighting-layout/skill.manifest.json` declares `inputs_path: "inputs.json"`
- [ ] `electrical/lighting-layout/CHANGELOG.md` entry for the inputs.json addition
- [ ] At least one more skill (suggested: `electrical/sld` — currently beta) gets the same treatment

### Notes for the upstream agent

- Don't try to enumerate every possible `room_type` perfectly — start with the 11 we've shown, expand as we go
- `project_fact_candidate: true` is a forward-compat flag for a future runtime feature (project-wide memory that pre-fills answers); just set it for items that describe the building, not items that describe THIS room/design
- The `struct_list` shape's `item_schema` is just JSON Schema — keep it simple, no `$ref`s for now

---

## Work Item 2 — Rationale block in IR

**Status:** add `rationale` to each skill's IR schema; add a generator-prompt step that populates it.

### Problem

Today's IR has `compliance: { lux_ok: true, ... }` and `flags: [...]`. That's
concise but doesn't carry the structured reasoning chain that the engineer
sees when reviewing a generated design.

The DraftsMan runtime currently builds a "layered rationale" (chat summary
+ collapsible sections + downloadable audit.md) from a bespoke Python
function per drawing type. We want to delete that Python and read the
rationale straight from IR.

### Solution

Extend each skill's IR schema with a `rationale` block. Update generator
prompts so the LLM emits it as the final reasoning step.

### IR schema addition — applies to every skill

Add to `shared/schemas/core/rationale.schema.json`:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "shared/schemas/core/rationale.schema.json",
  "title": "Rationale block embedded in every IR document",
  "type": "object",
  "required": ["chat_summary", "sections"],
  "properties": {
    "chat_summary": {
      "type": "string",
      "description": "3-5 sentence summary shown inline in the chat thread",
      "maxLength": 500
    },
    "sections": {
      "type": "array",
      "minItems": 1,
      "items": { "$ref": "#/definitions/Section" }
    }
  },
  "definitions": {
    "Section": {
      "type": "object",
      "required": ["title", "summary", "decisions"],
      "properties": {
        "title":    { "type": "string" },
        "summary":  { "type": "string", "maxLength": 200 },
        "decisions": {
          "type": "array",
          "items": { "$ref": "#/definitions/Decision" }
        }
      }
    },
    "Decision": {
      "type": "object",
      "required": ["label", "summary", "rule"],
      "properties": {
        "label":       { "type": "string" },
        "summary":     { "type": "string" },
        "rule":        { "type": "string", "description": "The deterministic rule or engineering principle invoked" },
        "code_clause": { "type": "string", "description": "BS / IEC / NEC clause reference, e.g. 'BS 7671 § 411.3.3'" },
        "inputs":      { "type": "object", "additionalProperties": true }
      }
    }
  }
}
```

Each skill's IR schema `$ref`s this block:

```json
"rationale": { "$ref": "../../shared/schemas/core/rationale.schema.json" }
```

### Generator prompt addition

At the end of every `prompts/generator.md`, add a final reasoning step.
Template (adapt to each skill's section list):

```markdown
### Step N (final) — Emit rationale block

After computing the IR, populate a `rationale` block at the IR root with:

- `chat_summary` — 3-5 sentences a busy engineer can read in the chat thread.
  Tell them: what you designed (1 sentence), the key decisions (1-2 sentences),
  any flags or assumptions (1 sentence), invitation to refine ("reply to refine
  e.g. 'use LED downlights instead'").

- `sections` — one section per design dimension. For lighting-layout, emit
  exactly these sections in this order, omitting any that don't apply:
    1. Illumination — lux target, UGR limit, Ra, MF/LLMF used
    2. Layout — luminaire count, spacing, ceiling-grid alignment
    3. Circuits — circuit count, load, MCB selection
    4. Switching — entrance positions, switch type, mounting height
    5. Emergency lighting — only if required for this space
    6. Part L controls — only if UK new-build flag set
    7. IP + environment — only if non-normal environment
    8. Assumptions — flags from your reasoning, each as one decision

Each decision is `{label, summary, rule, code_clause, inputs}`:
  - label: human-readable (e.g. "Lux target 500 lx maintained")
  - summary: one sentence
  - rule: the deterministic rule (e.g. "BS EN 12464-1 Table 5.3 entry
    for general_office")
  - code_clause: clause reference if applicable
  - inputs: structured map of the values that drove this decision

Do NOT skip this block. It is the engineer's audit trail.
```

### Acceptance criteria

- [ ] `shared/schemas/core/rationale.schema.json` exists
- [ ] `electrical/lighting-layout/schemas/lighting-layout-ir.schema.json` `$ref`s the rationale schema and makes `rationale` a required top-level field
- [ ] `electrical/lighting-layout/prompts/generator.md` ends with the "Step N — Emit rationale block" instructions
- [ ] All three example outputs (`office-open-plan`, `warehouse-highbay`, `reception-lobby`) regenerated to include `rationale` blocks consistent with their `reasoning.md` working
- [ ] At least one new eval YAML asserts `ir.rationale.sections.length >= 2` and `ir.rationale.chat_summary.length > 0`
- [ ] `CHANGELOG.md` entry — likely a minor bump (e.g. `v1.3.0`)

### Notes for the upstream agent

- The Decision shape mirrors what currently lives in `app/services/drawings/rationale.py` in the DraftsMan repo — keep it
- Empty sections (no decisions) are valid as long as `summary` explains why ("not applicable to this space type")
- Don't get clever with HTML or markdown in the strings — plain text only; the runtime renders

---

## Work Item 3 — Calculation executor declarations

**Status:** extend `shared/calculations/*.json` schema; map skill prompts to call calculations by ID.

### Problem

The current `shared/calculations/lighting/lumen-method.json` describes the
lumen-method formula. The LLM applies it inline. That's fine for closed-form
arithmetic.

It does NOT work for: BS 7430 electrode resistance (requires iterative
parallel-array convergence); BS 7671 Table 54.7 adiabatic CPC sizing; cable
voltage drop with derating; fault-level cascade calculations. The LLM
diverges from validated implementations by ±5-30% on these.

### Solution

Each calculation declares an `executor` mode: `inline` (LLM does the math
following the formula) or `tool` (the runtime invokes a named Python tool
and the LLM consumes the result).

### Updated `shared/calculations/lighting/lumen-method.json` (example)

```json
{
  "id": "lumen-method",
  "name": "Lumen Method (CIBSE SLL)",
  "executor": "inline",
  "inputs": [
    {"id": "lux_target",     "unit": "lx"},
    {"id": "area_m2",        "unit": "m²"},
    {"id": "uf",             "unit": "dimensionless", "description": "Utilisation Factor from photometric data"},
    {"id": "mf",             "unit": "dimensionless", "description": "Maintenance Factor; LLMF × LMF × LSF × RSMF"},
    {"id": "lumens_per_luminaire", "unit": "lm"}
  ],
  "output": {"id": "luminaire_count", "unit": "count"},
  "formula": "luminaire_count = ceil((lux_target × area_m2) / (uf × mf × lumens_per_luminaire))",
  "formula_reference": "CIBSE SLL Code for Lighting 2012, Chapter 2",
  "implementation_note": "Closed-form arithmetic. Safe for inline LLM execution. Round UP to next integer luminaire count."
}
```

### New `shared/calculations/electrical/electrode-resistance.json`

```json
{
  "id": "bs7430-electrode-resistance",
  "name": "BS 7430:2011 Earth Electrode Resistance",
  "executor": "tool",
  "tool_name": "calc.electrode_resistance",
  "inputs": [
    {"id": "electrode_type",          "type": "enum", "values": ["rod", "plate", "mat", "foundation"]},
    {"id": "soil_resistivity_ohm_m",  "unit": "Ω·m"},
    {"id": "target_resistance_ohm",   "unit": "Ω"},
    {"id": "length_or_size_mm",       "unit": "mm"},
    {"id": "rod_diameter_mm",         "unit": "mm", "default": 16},
    {"id": "burial_depth_mm",         "unit": "mm", "default": 600},
    {"id": "spacing_factor",          "unit": "dimensionless", "default": 0.85}
  ],
  "output": {
    "single_electrode_ohm": "Ω",
    "combined_ohm": "Ω",
    "count_recommended": "count",
    "target_met": "boolean",
    "formula_used": "string"
  },
  "formula_reference": "BS 7430:2011 §§ 9.5, 9.6, 9.7, Annex F",
  "implementation_note": "Iterative parallel-array convergence with spacing factor. Always invoke via tool — manual LLM calculation diverges from validated implementation by 10-25% depending on count. The tool selects rod/plate/mat/foundation formula by electrode_type, computes single-electrode resistance, then iterates count until combined_ohm ≤ target_resistance_ohm.",
  "runtime_contract": {
    "request":  "{ tool_name, inputs }",
    "response": "{ ok, result, error? }"
  }
}
```

### Updated calculation schema — `shared/schemas/core/calculation.schema.json`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "shared/schemas/core/calculation.schema.json",
  "type": "object",
  "required": ["id", "name", "executor", "inputs", "output", "formula_reference"],
  "properties": {
    "id":          { "type": "string" },
    "name":        { "type": "string" },
    "executor":    { "enum": ["inline", "tool"] },
    "tool_name":   { "type": "string", "description": "Required when executor=tool" },
    "inputs":      { "type": "array" },
    "output":      {},
    "formula":     { "type": "string", "description": "Required when executor=inline" },
    "formula_reference":   { "type": "string" },
    "implementation_note": { "type": "string" },
    "runtime_contract":    { "type": "object" }
  },
  "allOf": [
    {
      "if":   { "properties": { "executor": { "const": "tool" } } },
      "then": { "required": ["tool_name", "runtime_contract"] }
    },
    {
      "if":   { "properties": { "executor": { "const": "inline" } } },
      "then": { "required": ["formula"] }
    }
  ]
}
```

### Generator prompt convention

When a skill needs a tool-executed calculation, the generator prompt should
say (paraphrased):

```
For electrode resistance, do NOT calculate inline. Emit a tool call:

  { "tool_name": "calc.electrode_resistance",
    "inputs": { "electrode_type": "rod", "soil_resistivity_ohm_m": 80,
                "target_resistance_ohm": 200, "length_or_size_mm": 2400 } }

Wait for the tool response. Use the returned `combined_ohm` and
`count_recommended` in your IR. Cite BS 7430:2011 § 9.5 as the source.
```

The runtime intercepts the tool call, runs the Python implementation,
returns the result for the LLM to incorporate.

### Acceptance criteria

- [ ] `shared/schemas/core/calculation.schema.json` exists with `executor` enum + conditional validation
- [ ] `shared/calculations/lighting/lumen-method.json` updated with `executor: "inline"` (no behaviour change; documentation only)
- [ ] `shared/calculations/electrical/electrode-resistance.json` exists with `executor: "tool"` and full contract
- [ ] `shared/calculations/electrical/cpc-adiabatic.json` exists with `executor: "tool"` (BS 7671 Table 54.7 sizing)
- [ ] `shared/calculations/electrical/voltage-drop.json` exists with `executor: "tool"` (BS 7671 Appendix 4)
- [ ] `shared/calculations/electrical/fill-factor.json` exists with `executor: "tool"` (containment fill calc)
- [ ] Each tool-executor calc has an `implementation_note` explaining WHY it must be a tool
- [ ] List of tools required by all skills documented in `shared/calculations/REQUIRED_TOOLS.md` so the DraftsMan runtime knows which Python functions to implement

### Notes for the upstream agent

- This is documentation work — no runtime code in this repo
- The DraftsMan side will provide the Python implementations; this repo just declares the contracts
- When in doubt, prefer `executor: "tool"` for anything involving iteration, loops, or tabular lookups against standards data — those are precision-critical

---

## Work Item 4 — Cross-drawing intent declarations

**Status:** add two manifest keys; document intent schema for producer skills.

### Problem

A real project has multiple chats — earthing chat, DB chat, lighting chat,
small-power chat — and engineering decisions on one drawing affect others.
The earthing chat's Zs verification table needs to know the breaker ratings
from the DB chat. The cable-containment chat needs to know cable counts
from the DB / lighting / small-power chats.

Currently no skill declares its inter-skill data dependencies.

### Solution

`skill.manifest.json` gets two new optional keys:

```json
"consumes_intents": ["db-layout", "lighting-layout", "small-power", "earthing"],
"produces_intent":  "cable-containment"
```

When a skill declares `produces_intent`, it commits to emitting a stable
subset of its IR (the "intent payload") that downstream skills can rely on.
When a skill declares `consumes_intents`, the runtime pre-fetches the
latest intent for each declared producer from the project's other chats
and injects them as additional context in the user message.

### Intent payload schema

Each producer skill defines `intent.schema.json` adjacent to its main IR
schema, describing the **stable, publishable subset** of its IR.

#### Example: `electrical/db-layout/schemas/db-layout-intent.schema.json`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "electrical/db-layout/schemas/db-layout-intent.schema.json",
  "title": "DB Layout intent — stable subset for downstream skills",
  "type": "object",
  "required": ["db_id", "circuits", "incoming_supply"],
  "properties": {
    "db_id":       { "type": "string", "description": "e.g. DB-L1" },
    "incoming_supply": {
      "type": "object",
      "properties": {
        "voltage_V":         { "type": "integer" },
        "phase_arrangement": { "enum": ["single_phase", "TPN"] },
        "supply_rating_A":   { "type": "integer" }
      }
    },
    "circuits": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "module_id", "breaker_rating_A", "breaker_curve"],
        "properties": {
          "id":               { "type": "string" },
          "module_id":        { "type": "string" },
          "breaker_rating_A": { "type": "integer" },
          "breaker_curve":    { "enum": ["B", "C", "D"] },
          "rcd_protected":    { "type": "boolean" },
          "cable_csa_mm2":    { "type": "number" },
          "voltage_class":    { "enum": ["LV_power", "ELV_control", "comms_data",
                                         "fire_alarm", "emergency_lighting"] }
        }
      }
    }
  }
}
```

Why a separate schema (not just the full IR)? Because:
- The full IR includes positions, drawings, presentation data — downstream skills don't need it
- The intent is a stability contract; the full IR can change in non-breaking ways without breaking downstream consumers
- It's smaller — keeps cross-drawing context payloads tight

### Generator prompt convention for consumers

When a skill declares `consumes_intents`, its `prompts/generator.md` should
explain how to consume them. Template:

```markdown
## Cross-drawing context

When this skill is invoked within a DraftsMan project that has other
completed drawings, the runtime will inject their **intents** into the
user message under a `cross_drawing_context` key:

```json
{
  "cross_drawing_context": {
    "db-layout":      { ... db-layout intent payload ... },
    "lighting-layout":[{ ... per chat ... }, ...],
    "small-power":    [{ ... per chat ... }, ...]
  }
}
```

Use these intents to:
- Sum cable demand on each named containment run
- Verify breaker ratings against your sizing assumptions
- Cite the source chat ID for traceability in the rationale

If a `consumes_intents` skill is missing from the context, generate a
flag in your `rationale.flags` indicating the gap (e.g. "no db-layout
chat in this project; cable demand is from explicit entry only").
```

### Acceptance criteria

- [ ] `electrical/db-layout/skill.manifest.json` declares `produces_intent: "db-layout"` and `consumes_intents: []`
- [ ] `electrical/db-layout/schemas/db-layout-intent.schema.json` exists
- [ ] `electrical/lighting-layout/skill.manifest.json` declares `produces_intent: "lighting-layout"`
- [ ] `electrical/lighting-layout/schemas/lighting-layout-intent.schema.json` exists (subset: circuits, luminaires count per circuit, voltage class)
- [ ] `electrical/small-power/skill.manifest.json` (when authored) declares `produces_intent: "small-power"`
- [ ] `electrical/earthing/skill.manifest.json` (when authored) declares `consumes_intents: ["db-layout", "lighting-layout", "small-power"]` AND `produces_intent: "earthing"`
- [ ] `electrical/cable-containment/skill.manifest.json` (when authored) declares `consumes_intents: ["db-layout", "lighting-layout", "small-power", "earthing"]` AND `produces_intent: "cable-containment"`
- [ ] `shared/schemas/core/intent.schema.json` provides the metaschema for intent payloads
- [ ] `ARCHITECTURE.md` updated with a "Cross-drawing intents" section describing the contract

### Notes for the upstream agent

- A skill can produce ONE intent type only — name it the same as the skill
- A skill can consume MANY intents (others' produces_intent values)
- The intent payload is forward-compatible by design: new optional fields can be added, but required fields can never be removed without a major version bump
- A skill that consumes intents must handle the case where one or more intents are absent (empty project, sibling chat hasn't completed yet)

---

## Work Item 5 — Standardize evals + runner config

**Status:** define eval YAML schema; add `evals/runner-config.json` per skill; document required eval coverage.

### Problem

`electrical/lighting-layout/evals/` has 7 YAML files with slightly varying
shapes. The DraftsMan runtime needs to be able to run all evals for any
skill, against any LLM, and report pass/fail uniformly. There's no current
standard for what an eval YAML must contain.

Plus: skills don't declare a minimum pass threshold or which LLM models
they've been validated against.

### Solution

(a) Standardize the eval YAML schema. (b) Add a `runner-config.json` per
skill declaring expected models + pass thresholds. (c) Document the
required eval coverage tiers (status: production requires ≥5 evals; beta ≥3; draft ≥1).

### Standardized eval YAML — `shared/schemas/core/eval.schema.json`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "shared/schemas/core/eval.schema.json",
  "title": "Skill evaluation schema",
  "type": "object",
  "required": ["name", "skill", "input", "checks"],
  "properties": {
    "name":        { "type": "string" },
    "skill":       { "type": "string" },
    "description": { "type": "string" },
    "input":       { "type": "object", "description": "Maps to inputs.json answers" },
    "expected_compliance": { "type": "object" },
    "checks": {
      "type": "array",
      "minItems": 1,
      "items": { "$ref": "#/definitions/Check" }
    },
    "expected_flags": {
      "type": "array",
      "items": { "type": "string" }
    }
  },
  "definitions": {
    "Check": {
      "type": "object",
      "required": ["assertion", "description"],
      "properties": {
        "assertion":   { "type": "string", "description": "JSONPath + operator + value, e.g. 'ir.luminaires.length >= 16'" },
        "description": { "type": "string" },
        "severity":    { "enum": ["critical", "warning", "info"], "default": "critical" }
      }
    }
  }
}
```

Allowed assertion grammar (kept simple to avoid building a query engine):

```
<jsonpath>          operator value
ir.compliance.lux_ok                    == true
ir.luminaires.length                    >= 16
ir.luminaires.length                    <= 24
ir.zones.length                          == 2
ir.rationale.sections                    contains "Illumination"
ir.flags                                 not_contains "NON-COMPLIANCE"
ir.luminaires[*].circuit_id              all_equal "L1-Z2"
```

Operators: `==`, `!=`, `>=`, `<=`, `>`, `<`, `contains`, `not_contains`, `all_equal`, `matches` (regex).

### `runner-config.json` per skill

```json
{
  "skill": "lighting-layout",
  "minimum_status_evals": {
    "production": 5,
    "beta": 3,
    "draft": 1
  },
  "validated_against_models": [
    { "model": "claude-sonnet-4-5", "pass_rate_required": 1.0, "last_passed_at": "2026-04-12T00:00:00Z" },
    { "model": "claude-sonnet-4-6", "pass_rate_required": 1.0, "last_passed_at": "2026-05-13T00:00:00Z" }
  ],
  "production_block_on_failure": true
}
```

### Required eval coverage matrix

Documented in each skill's `README.md`:

| Eval # | Category | Required for `production`? |
|--------|----------|----------------------------|
| 1 | Happy path (common, complete input) | Yes |
| 2 | Edge case 1 (minimum spec; e.g. lux below standard) | Yes |
| 3 | Edge case 2 (missing optional data; engine should flag assumption) | Yes |
| 4 | Compliance failure (must surface flag) | Yes |
| 5 | Cross-validation (computed values match expected) | Yes |
| 6+ | Skill-specific scenarios | Optional |

### Acceptance criteria

- [ ] `shared/schemas/core/eval.schema.json` exists
- [ ] All 7 existing `electrical/lighting-layout/evals/*.yaml` validate against the new schema (rewrite where they don't)
- [ ] `electrical/lighting-layout/evals/runner-config.json` exists
- [ ] `electrical/lighting-layout/README.md` documents the eval coverage matrix
- [ ] `SKILLS_STATUS.md` updated with a new column: `Evals: N/M` (e.g. `7/5` for lighting-layout — has 7, needs 5 for production)
- [ ] `CONTRIBUTING.md` updated with eval authoring guide

### Notes for the upstream agent

- Use the lighting-layout existing evals as the starting point; harmonize them rather than rewriting from scratch
- The assertion grammar is intentionally minimal — if you need anything beyond what's listed, propose an extension in an issue first
- `production_block_on_failure: true` is a hint to runtimes that this skill should not be loadable if any eval fails on a target model

---

## Sequencing

Land these in this order. Each depends on the previous one being mergeable
without breaking earlier work.

1. **Work Item 1 — `inputs.json`** (Lighting only first; other skills follow)
   - Unblocks DraftsMan's discovery driver. **Do this first.**

2. **Work Item 5 — Eval standardization** (Lighting only first)
   - Unblocks DraftsMan's CI + production-gating. **Do this second** — independent of Work Items 2-4 but lets DraftsMan validate everything that follows.

3. **Work Item 2 — Rationale in IR** (Lighting only first)
   - Lets DraftsMan delete its bespoke rationale Python.

4. **Work Item 3 — Calculation executor declarations** (`shared/calculations/` + schema; lighting calcs stay inline, but document the contract for future tool-executor calcs)
   - DraftsMan implements the tool-call bridge once this is documented.

5. **Work Item 4 — Cross-drawing intent** (Lighting `produces_intent` only first; consumers later as their skills are authored)
   - Latest priority — only matters once the second drawing-type skill lands.

After Work Items 1-3 are done for lighting-layout, the DraftsMan runtime
can do a complete end-to-end vertical-slice migration of lighting. Once
that works, Work Items 4-5 extend the pattern to the rest.

---

## Validation — what "done" looks like

After all 5 work items are complete on lighting-layout:

- `electrical/lighting-layout/inputs.json` exists, well-formed
- `electrical/lighting-layout/schemas/lighting-layout-ir.schema.json` includes `rationale`
- `electrical/lighting-layout/prompts/generator.md` has the rationale-emission step
- `electrical/lighting-layout/skill.manifest.json` declares `produces_intent: "lighting-layout"` + `inputs_path: "inputs.json"`
- `electrical/lighting-layout/schemas/lighting-layout-intent.schema.json` exists
- `electrical/lighting-layout/evals/*.yaml` all validate against the eval schema
- `electrical/lighting-layout/evals/runner-config.json` exists
- All three examples (`office-open-plan`, `warehouse-highbay`, `reception-lobby`) have outputs that include the new `rationale` block
- `SKILLS_STATUS.md` shows lighting-layout's evals count, intent declarations, inputs richness
- `ARCHITECTURE.md` describes the IR contract, including the rationale block, cross-drawing intent pattern, and tool-executor calc pattern

That's the package the DraftsMan runtime will consume in Sprint 3G.

---

## Open questions to discuss before starting

These can be answered upstream by the agent, or come back to DraftsMan-side
for a decision:

1. **Versioning** — when an `inputs.json` schema changes, is that a skill major bump or minor? Recommendation: minor if optional fields added, major if required fields added/changed.
2. **Validator registry — shared or per-skill?** Recommendation: shared (proposed location `shared/validation/validators.json`). Skill-specific validators can live in `<skill>/validation/` and the runner merges them.
3. **`struct_list` answer_type complexity** — should we allow nested `struct_list`? Recommendation: no, depth 1 only. Engineers don't enter trees in chat.
4. **Intent schema versioning** — is the producer intent schema versioned independently of the skill? Recommendation: yes (semver), with a `intent_version` field on the produced payload so consumers can dispatch on version.
5. **Eval grammar extensions** — anything missing from `==/>=/contains/all_equal/matches`? Open as a GitHub issue if found.

---

## Repo etiquette

- Each work item lands as one PR (or per-skill if the change is per-skill)
- Each PR has a CHANGELOG.md entry on the affected skill
- ARCHITECTURE.md updates happen on Work Item 1's PR (foundation) and again on Work Item 4 (intents)
- Tests / evals pass before merging
- No work item depends on a DraftsMan runtime change — the contract surface is always one-directional (upstream defines, downstream consumes)

---

## Contact / sync protocol

When the upstream agent has a question about a contract detail, the answer
lives in this spec or in the DraftsMan runtime team's response. Don't
invent new contract fields without an issue + decision in the spec.

This spec is the source of truth for what upstream contributions look
like. When it's outdated, update this file in the DraftsMan repo first,
then implement.
