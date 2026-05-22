# Sprint 3-W2a — Schema Standardisation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Standardise eval + inputs schemas across all 9 skills so the golden CI harness can validate evals and inputs.json files (not just example outputs), and document the established sprint workflow in CLAUDE.md.

**Architecture:** Mechanical key-renames + schema authoring + 1 harness extension + 1 doc rewrite. No engineering content authoring. 6 tasks across 5 phases. ~44 file ops, 1-2 dev days. Format A (canonical) is the gold target — Format C (23 evals) gets mechanical renames; Format D (17 evals) needs structural conversion of `expected.*` blocks into `checks[]` array entries.

**Tech Stack:** YAML (eval files), JSON Schema Draft-07 (eval.schema.json + inputs.schema.json), Python 3 (harness extension to validate-examples.py), Markdown (CLAUDE.md).

**Pattern parents (verified at commit 0b600d4):**
- `electrical/lighting-layout/evals/eval-01-office-happy-path.yaml` — canonical Format A target shape (name / skill / description / category / input / checks[] with assertion+description+standard_ref).
- `shared/schemas/core/eval.schema.json` — current 5-category enum + assertion_grammar block — modify in place.
- `shared/schemas/core/rationale.schema.json` — already at maxLength 800 (Sprint 3-W Phase E, commit b11ebca). Don't touch.
- `scripts/validate-examples.py` — 136-line single-pass harness. Extend with two more passes (evals + inputs.json), preserve `strip_refs()` helper.
- `electrical/db-layout/evals/eval-01-uk-domestic-cu-tn-cs.yaml` — Format C sample (id / category / severity / description / inputs / assertions[kind:...] / expected_status).
- `electrical/arc-flash-labelling/evals/eval-01-us-mixed-cascade-ansi-labels.yaml` — Format D sample (eval_id / skill / input / expected.ir_structural + expected.per_label).
- `electrical/arc-flash-labelling/evals/eval-08-qr-code-conditional-emission.yaml` — 2-scenario A/B eval; needs special handling per Phase B Task 3.
- Recent shipped memory shape: `small-power-v1.1-shipped.md` / `cable-sizing-shipped.md` / `sprint-3w-shipped.md`.

**Final state target (acceptance):**
- `scripts/validate-examples.py` runs 3 passes: examples (53/53) + evals (80/80) + inputs.json (9/9). Exit 0 on full pass.
- `eval.schema.json` v2: 9-value category enum, `oneOf: [input, input_fixtures]`, required = `[name, skill, checks]`.
- `inputs.schema.json` new file: `oneOf: [items, inputs, input_groups]`.
- 23 Format C evals migrated (id→name, inputs→input, assertions→checks).
- 17 Format D evals migrated (eval_id→name, expected.*→checks[]).
- `arc-flash-labelling/eval-08` reshaped to a single canonical eval with `input_fixtures` (or split into 8a+8b — implementer judgment).
- `CLAUDE.md` rewritten covering folder structure + brainstorm/spec/plan/subagent workflow + Sonnet+Opus rule + golden CI gate.

**Model selection (per [[feedback-no-haiku-sonnet-opus-only]]):**
- Sonnet: Task 1 (mechanical schema edits), Task 2 (mechanical Format C renames), Task 4 (mechanical Python additions).
- Opus: Task 3 (Format D structural conversion + eval-08 reshape — needs judgment), Task 5 (CLAUDE.md rewrite — engineering judgment about what workflow patterns deserve documenting), Task 6 (ship-readiness judgment).

---

## File Structure

**Files modified (5):**
- `shared/schemas/core/eval.schema.json` — extend category enum, swap required, add oneOf for input/input_fixtures.
- `scripts/validate-examples.py` — refactor into 3 named pass functions, aggregate exit code.
- `CLAUDE.md` — full revision (~150-200 lines).
- 23 Format C eval YAMLs (Task 2).
- 17 Format D eval YAMLs (Task 3).

**Files created (1 or 2):**
- `shared/schemas/core/inputs.schema.json` — new metaschema for skill inputs.json files.
- Optionally `electrical/arc-flash-labelling/evals/eval-08a-qr-code-emitted.yaml` + `eval-08b-qr-code-suppressed.yaml` IF implementer chooses the split path over input_fixtures.

**Files referenced but unchanged (verification only):**
- All 9 `electrical/*/inputs.json` files — must satisfy the new inputs.schema.json oneOf without edits.
- All 53 `electrical/*/examples/*/output.json` files — must keep passing the existing examples pass.

---

## Task 1: Schema authoring (Phase A) — Sonnet

**Why Sonnet:** Mechanical schema edits with explicit target shapes. No judgment about what to write — only how to land the edits cleanly.

**Files:**
- Modify: `shared/schemas/core/eval.schema.json`
- Create: `shared/schemas/core/inputs.schema.json`
- Test: re-run `python3 scripts/validate-examples.py` to confirm the new eval.schema.json doesn't break example validation (it shouldn't — the examples pass uses `*-ir.schema.json`, not eval.schema.json).

### Step 1: Read the current eval.schema.json end-to-end

- [ ] Read `shared/schemas/core/eval.schema.json` in full. Confirm current required is `["name", "skill", "input", "checks"]` and the category enum has 5 values (`happy_path`, `edge_case`, `compliance_failure`, `cross_validation`, `skill_specific`).

### Step 2: Update required to drop "input"

- [ ] Edit `required` array at line ~7 from:
```json
"required": ["name", "skill", "input", "checks"],
```
to:
```json
"required": ["name", "skill", "checks"],
```

### Step 3: Add oneOf for input vs input_fixtures

After the closing `}` of the `properties` block and before `assertion_grammar`, add the oneOf clause. The full updated structure (showing the change point):

```json
"properties": {
  "name": { "type": "string", "description": "Unique within the skill. Convention: eval-NN-short-slug." },
  "skill": { "type": "string", "description": "Skill id matching the parent skill.manifest.json" },
  "description": { "type": "string", "description": "One-line summary of what this eval verifies" },
  "category": {
    "enum": [
      "happy_path",
      "edge_case",
      "compliance_failure",
      "cross_validation",
      "skill_specific",
      "validation_trap",
      "rationale_block",
      "jurisdiction_switch",
      "missing_input"
    ],
    "description": "Eval-coverage-matrix bucket. happy_path / edge_case / compliance_failure / cross_validation / skill_specific are the original 5. validation_trap / rationale_block / jurisdiction_switch / missing_input are emerged conventions formalised in Sprint 3-W2a."
  },
  "input": {
    "type": "object",
    "description": "Inline input dict. Mutually exclusive with input_fixtures.",
    "additionalProperties": true
  },
  "input_fixtures": {
    "type": "array",
    "description": "References to example folders that serve as inputs for this eval. Mutually exclusive with input.",
    "items": { "type": "string" },
    "minItems": 1
  },
  "expected_compliance": { "type": "object", "description": "Optional declarations of the compliance outcome the skill should report.", "additionalProperties": true },
  "expected_flags": { "type": "array", "description": "Substrings the runtime expects to find in ir.flags or ir.rationale flags.", "items": { "type": "string" } },
  "checks": {
    "type": "array",
    "minItems": 1,
    "items": { "$ref": "#/definitions/Check" }
  }
},
"oneOf": [
  { "required": ["input"] },
  { "required": ["input_fixtures"] }
],
```

Implementation note: keep the rest of the file intact — `assertion_grammar`, `definitions.Check`, and the existing operators list are unchanged.

### Step 4: Create inputs.schema.json

- [ ] Create `shared/schemas/core/inputs.schema.json` with:
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "shared/schemas/core/inputs.schema.json",
  "title": "Skill inputs.json metaschema",
  "description": "Validates the top-level shape of every per-skill inputs.json. Three accepted top-level keys reflect the three established conventions: items[] (flat input list), inputs[] (legacy alias used by arc-flash skills), input_groups[] (grouped form used by cable-sizing and small-power).",
  "type": "object",
  "required": ["skill"],
  "additionalProperties": true,
  "properties": {
    "skill": { "type": "string", "description": "Skill id matching the parent skill.manifest.json." },
    "version": { "type": "string", "description": "Skill version this inputs file targets." },
    "description": { "type": "string", "description": "Optional human description of the input set." },
    "$schema": { "type": "string", "description": "Optional pointer to a meta-schema URL." },
    "items": { "type": "array", "minItems": 0, "description": "Flat list of input items. Used by db-layout, earthing, fault-level, lighting-layout, sld." },
    "inputs": { "type": "array", "minItems": 0, "description": "Legacy alias used by arc-flash + arc-flash-labelling. Semantically equivalent to items[]." },
    "input_groups": { "type": "array", "minItems": 0, "description": "Grouped input list with per-group metadata. Used by cable-sizing + small-power." }
  },
  "oneOf": [
    { "required": ["items"] },
    { "required": ["inputs"] },
    { "required": ["input_groups"] }
  ]
}
```

### Step 5: Verify the eval.schema.json is well-formed Draft-07

Run:
```bash
python3 -c "import json, jsonschema; s = json.load(open('shared/schemas/core/eval.schema.json')); jsonschema.Draft7Validator.check_schema(s); print('eval.schema.json OK')"
python3 -c "import json, jsonschema; s = json.load(open('shared/schemas/core/inputs.schema.json')); jsonschema.Draft7Validator.check_schema(s); print('inputs.schema.json OK')"
```
Expected: both print OK with no exception.

### Step 6: Run the existing harness to confirm examples pass still works

Run:
```bash
python3 scripts/validate-examples.py
```
Expected: 39/53 baseline (no regression from Sprint 3-W end state — eval.schema.json change does not affect the examples pass, which uses skill-specific `*-ir.schema.json`).

### Step 7: Commit

```bash
git add shared/schemas/core/eval.schema.json shared/schemas/core/inputs.schema.json
git commit -m "feat(sprint-3w2a): Phase A schemas — eval.schema.json v2 (9-value category enum + oneOf input/input_fixtures) + new inputs.schema.json with oneOf items/inputs/input_groups"
```

---

## Task 2: Format C migration (Phase B-1) — Sonnet

**Why Sonnet:** Mechanical key renames + assertion-grammar translation using a fixed mapping table. 23 files × ~6 grammar swaps each = ~140 mechanical edits. Predictable.

**Scope:** 23 evals across 3 skills:
- `electrical/db-layout/evals/eval-01..08-*.yaml` (8 files)
- `electrical/fault-level/evals/eval-01..09-*.yaml` (9 files)
- `electrical/earthing/evals/eval-01..06-*.yaml` (6 files — eval-07/08/09 already use canonical `name` key, skip them)

**Migration ruleset (apply to every file):**

1. Rename top-level `id:` → `name:`.
2. Rename top-level `inputs:` → `input:` (the dict-valued form). DO NOT rename to `input_fixtures` — these all have inline dicts.
3. Rename top-level `assertions:` → `checks:` and translate every item per the grammar table below.
4. Add `skill: <skill-name>` field directly after `name:` if missing (most Format C files lack it).
5. Drop top-level `expected_status:` (not part of canonical schema; severity now lives per-check).
6. Move top-level `severity:` into each check item (`severity: critical` for items previously top-level critical, default critical for happy_path).

**Format C `assertions[]` → canonical `checks[]` grammar table:**

| Format C item | Canonical check item |
|---|---|
| `- kind: schema_valid` `schema: "X-ir.schema.json"` | `- assertion: ir matches "X-ir.schema.json"` `description: "Output validates against the skill IR schema"` |
| `- kind: jsonpath_equals` `path: "$.X"` `expected: Y` | `- assertion: "ir.X == Y"` `description: "<rephrase from path semantics>"` |
| `- kind: jsonpath_count_equals` `path: "$.X[*]"` `expected: N` | `- assertion: "ir.X.length == N"` `description: "<rephrase>"` |
| `- kind: jsonpath_lte` `path: "$.X"` `maximum: M` | `- assertion: "ir.X <= M"` `description: "<rephrase>"` |
| `- kind: jsonpath_gte` `path: "$.X"` `minimum: M` | `- assertion: "ir.X >= M"` `description: "<rephrase>"` |
| `- kind: jsonpath_contains` `path: "$.X"` `value: V` | `- assertion: "ir.X contains V"` `description: "<rephrase>"` |
| `- kind: invariant_passes` `invariant: "INV-N"` `note: "..."` | `- assertion: "ir.invariants.INV-N.passes == true"` `description: "<note value>"` |
| `- kind: clause_cited` `clause_pattern: "..."` `minimum_count: N` | `- assertion: 'ir.citations matches "..."'` `description: "At least N citations match pattern"` `severity: warning` (advisory) |
| `- kind: rationale_present` `require_sections: [A, B, C]` | Generate N separate check items, one per required section: `- assertion: 'ir.rationale.sections[*].title contains "A"'` `description: "Rationale must include section: A"` |

Notes for the implementer:
- The `$.` JSONPath prefix is dropped in the canonical assertion form (canonical uses `ir.X`, not `$.X`).
- Replace numeric path indexing (`$.X[0]`) with array selector (`ir.X[*]`) when the original meant "any item".
- For `clause_cited` patterns, the canonical form uses `matches` operator with the pattern as a quoted value. Use single quotes around the outer YAML string when the pattern contains double quotes.
- For `rationale_present` with N sections, emit N check items so each is independently testable.
- Pull the `severity:` value from the top-level Format C `severity:` field if present, default to `critical`.

### Step 1: Inventory Format C files

- [ ] List all 23 files:
```bash
find electrical/db-layout/evals electrical/fault-level/evals -name "eval-*.yaml" -type f
find electrical/earthing/evals -name "eval-*.yaml" -type f | head -6
```
Confirm: 8 db-layout + 9 fault-level + 6 earthing = 23 files. The remaining 3 earthing evals (eval-07/08/09) use `name:` already — skip.

### Step 2: Verify each file's first key

- [ ] For every file in the inventory:
```bash
for f in <files>; do echo "$f: $(grep -E '^[a-z_]+:' "$f" | head -1)"; done
```
Expected: all show `id: ...` as first non-comment key. If any show `name:` or `eval_id:` already, exclude from this task.

### Step 3: Apply the rename ruleset to one file as proof-of-concept

Pick `electrical/db-layout/evals/eval-01-uk-domestic-cu-tn-cs.yaml`. After migration the head should look like:

```yaml
# Eval 01 — UK domestic consumer unit, TN-C-S
# Category: happy_path
# Standard refs: BS 7671:2018+A3, IEC 61439-3, IEC 60617

name: eval-01-uk-domestic-cu-tn-cs
skill: db-layout
category: happy_path
description: |
  Standard UK 3-bed semi-detached dwelling on PME supply (TN-C-S). 100A main switch +
  12-way Hager consumer unit + 30mA main RCD + 6 final circuits (lighting × 2, sockets × 2,
  cooker, shower). All circuits RCBO or behind main RCD. Form 1 enclosure.

input:
  jurisdiction: "GB"
  board_type: "consumer_unit"
  # ... (unchanged inline dict)

checks:
  - assertion: 'ir matches "db-layout-ir.schema.json"'
    description: Output validates against the db-layout IR schema
    severity: critical

  - assertion: "ir.jurisdiction == GB"
    description: Jurisdiction must be GB
    severity: critical

  - assertion: "ir.board.db_id == CU-G"
    description: Board id must match declared db_designation
    severity: critical

  - assertion: 'ir.board.enclosure_form_iec61439 == "1"'
    description: Form 1 separation per IEC 61439-3 for domestic CU
    severity: critical
    standard_ref: IEC 61439-3

  - assertion: "ir.circuits.length == 6"
    description: Six final circuits declared
    severity: critical

  - assertion: "ir.board.ways_used <= 12"
    description: Way usage must not exceed total ways
    severity: critical

  - assertion: "ir.invariants.INV-1.passes == true"
    description: Way accounting (INV-1)
    severity: critical

  - assertion: "ir.invariants.INV-3.passes == true"
    description: Busbar rating coverage (INV-3)
    severity: critical

  - assertion: "ir.invariants.INV-4.passes == true"
    description: OCPD-cable coordination (INV-4)
    severity: critical

  - assertion: 'ir.citations matches "^BS 7671:2018\\+A3 Reg 4(11|33)\\."'
    description: At least 2 citations match the BS 7671 Reg 411 / 433 pattern
    severity: warning

  - assertion: 'ir.rationale.sections[*].title contains "Board Classification"'
    description: "Rationale must include section: Board Classification"
    severity: critical

  - assertion: 'ir.rationale.sections[*].title contains "Incoming Supply"'
    description: "Rationale must include section: Incoming Supply"
    severity: critical

  - assertion: 'ir.rationale.sections[*].title contains "Busbar Sizing"'
    description: "Rationale must include section: Busbar Sizing"
    severity: critical

  - assertion: 'ir.rationale.sections[*].title contains "Way Assignment"'
    description: "Rationale must include section: Way Assignment"
    severity: critical

  - assertion: 'ir.rationale.sections[*].title contains "OCPD Selection"'
    description: "Rationale must include section: OCPD Selection"
    severity: critical

  - assertion: 'ir.rationale.sections[*].title contains "RCD Strategy"'
    description: "Rationale must include section: RCD Strategy"
    severity: critical

  - assertion: 'ir.rationale.sections[*].title contains "Cable Selection"'
    description: "Rationale must include section: Cable Selection"
    severity: critical

  - assertion: 'ir.rationale.sections[*].title contains "Selectivity Verification"'
    description: "Rationale must include section: Selectivity Verification"
    severity: critical

  - assertion: 'ir.rationale.sections[*].title contains "Compliance"'
    description: "Rationale must include section: Compliance"
    severity: critical
```

(The `expected_status: "pass"` line is dropped.)

### Step 4: Validate the proof-of-concept file against the new eval.schema.json

Run:
```bash
python3 -c "
import json, yaml, jsonschema, sys
schema = json.load(open('shared/schemas/core/eval.schema.json'))
data = yaml.safe_load(open('electrical/db-layout/evals/eval-01-uk-domestic-cu-tn-cs.yaml'))
try:
    jsonschema.validate(data, schema)
    print('PASS')
except jsonschema.ValidationError as e:
    print('FAIL:', e.message[:200]); sys.exit(1)
"
```
Expected: `PASS`.

### Step 5: Apply the rename ruleset to the remaining 22 files

- [ ] Walk the 7 remaining db-layout files (eval-02 through eval-08), 9 fault-level files, and 6 earthing files (eval-01 through eval-06).
- [ ] For each file, apply the ruleset deterministically. Preserve the entire `input:` block verbatim — only its key name changes.
- [ ] For `description:` blocks: preserve the existing prose. Do not paraphrase.
- [ ] For each `kind:` assertion item: consult the grammar table and emit the canonical check form.
- [ ] If a file has an assertion `kind:` not in the grammar table, halt and report — do not invent a translation.

### Step 6: Validate all 23 migrated files

```bash
python3 -c "
import json, yaml, jsonschema, glob, sys
schema = json.load(open('shared/schemas/core/eval.schema.json'))
files = sorted(glob.glob('electrical/db-layout/evals/eval-*.yaml')
             + glob.glob('electrical/fault-level/evals/eval-*.yaml')
             + glob.glob('electrical/earthing/evals/eval-0[1-6]-*.yaml'))
fail = 0
for f in files:
    data = yaml.safe_load(open(f))
    try: jsonschema.validate(data, schema); print(f'PASS {f}')
    except jsonschema.ValidationError as e: print(f'FAIL {f}: {e.message[:120]}'); fail += 1
sys.exit(fail)
"
```
Expected: 23/23 PASS, exit 0.

### Step 7: Commit

```bash
git add electrical/db-layout/evals/ electrical/fault-level/evals/ electrical/earthing/evals/
git commit -m "feat(sprint-3w2a): Phase B-1 — migrate 23 Format C evals to canonical schema (db-layout + fault-level + earthing 01-06; id→name, inputs→input, assertions→checks with grammar translation)"
```

---

## Task 3: Format D migration (Phase B-2) — Opus

**Why Opus:** Format D's `expected.ir_structural` + `expected.per_label` blocks aren't flat — they're nested structural assertions that need converting into a `checks[]` array of single-line `assertion + description` entries. Some judgment required around JSONPath shape for per-label assertions. Also, `eval-08` is a 2-scenario A/B test that doesn't fit the canonical schema cleanly — decide between split-into-two and input_fixtures+inline-conditional.

**Scope:** 17 evals across 2 skills:
- `electrical/arc-flash/evals/eval-01..09-*.yaml` (9 files)
- `electrical/arc-flash-labelling/evals/eval-01..08-*.yaml` (8 files)

**Migration ruleset:**

1. Rename top-level `eval_id:` → `name:`. Keep `skill:` (already present).
2. `skill_version:` → drop (not part of canonical schema; lives in the skill manifest).
3. `subcategory:` → drop (not part of canonical schema).
4. Top-level `input:` is already canonical — keep as-is.
5. Convert `expected:` block into `checks[]` using the grammar below.
6. Keep `category:` value — only swap to one of the 9 enum values if a non-canonical value is used (rare in Format D).

**Format D `expected.*` → `checks[]` grammar:**

For each scalar under `expected.ir_structural`:
- `expected.ir_structural.X: V` → `- assertion: "ir.X == V"` `description: "<infer from key name>"` `severity: critical`
- `expected.ir_structural.flags_must_include: [F1, F2]` → one check per flag: `- assertion: 'ir.flags contains "F1"'` `description: "Output must include flag F1"`
- `expected.ir_structural.flags_must_not_include: [F1]` → `- assertion: 'ir.flags not_contains "F1"'` `description: "Output must not include flag F1"`
- `expected.ir_structural.<count_key>: N` (e.g. `labels_count: 4`) → `- assertion: "ir.<derived_path>.length == N"` `description: "Expected N items"`. Derive the path from the key name (e.g. `labels_count` → `ir.labels`).

For each entry under `expected.per_label` (and `per_circuit`, `per_node`, etc.):
- Each per-label item has a `node_id` discriminator. Emit one assertion per non-discriminator key per item:
  - `- assertion: 'ir.labels[?(@.node_id=="SERVICE-480V")].format_applied == "ansi_z535_4"'` `description: "Label for SERVICE-480V uses ANSI Z535.4 format"`
- For `_must_contain_text` keys: use the `contains` operator on the field path the key implies (e.g. `svg_content_must_contain_text: "QR"` → `'ir.labels[?(@.node_id=="X")].svg_content contains "QR"'`).
- For `_must_not_contain_text`: use `not_contains`.

For `expected_compliance:` blocks if present (legacy survivor): preserve as a top-level `expected_compliance:` (canonical schema permits it).

**Special case: `arc-flash-labelling/eval-08-qr-code-conditional-emission.yaml`**

This eval is structurally a 2-scenario A/B test:
- `input_a` + `expected_a` (qr_code_base_url present → labels carry URL)
- `input_b` + `expected_b` (qr_code_base_url null → labels carry null + no QR in SVG)

Two acceptable resolutions — pick one and document the choice in the commit message:

**Resolution X (split):** Create two files, archive the original:
- `eval-08a-qr-code-emitted.yaml` — input=input_a, checks=converted from expected_a + the "no fake URL" pass criterion.
- `eval-08b-qr-code-suppressed.yaml` — input=input_b, checks=converted from expected_b + "no QR-code SVG element" pass criterion.
- Move the original to `electrical/arc-flash-labelling/evals/_archive/eval-08-qr-code-conditional-emission.yaml.original` (preserves the A/B-pair semantics for future LLM-vs-golden harness).

**Resolution Y (input_fixtures):** Convert to a single canonical eval with:
- `input_fixtures:` pointing at the matching example folder(s) under `electrical/arc-flash-labelling/examples/` that exercise the conditional emission.
- `checks[]:` covering the union of A/B expectations expressed as scenario-conditional assertions.

**Recommended:** Resolution X. The A/B nature is genuine and each scenario is independently testable. Resolution Y collapses the test fidelity. Note: this is the implementer's judgment call — design spec §3 Phase B says "input_fixtures + TODO", but Resolution X better preserves test semantics. Pick the cleaner option.

### Step 1: Inventory Format D files

- [ ] List:
```bash
find electrical/arc-flash/evals electrical/arc-flash-labelling/evals -name "eval-*.yaml" -type f | sort
```
Expected: 17 files (9 arc-flash + 8 arc-flash-labelling).

### Step 2: Apply rename + structural conversion to one proof-of-concept

Pick `electrical/arc-flash-labelling/evals/eval-01-us-mixed-cascade-ansi-labels.yaml`. Migrate to canonical shape per the ruleset above. After migration:

```yaml
name: eval-01-us-mixed-cascade-ansi-labels
skill: arc-flash-labelling
category: happy_path
description: |
  US mixed-cascade switchboard with arc-flash + restricted-equipment intents present.
  Verifies ANSI Z535.4 format adoption per node + TOOL-CALL-PENDING flag for PDF/PNG rendering.

input:
  jurisdiction: US
  # ... (unchanged from original)

checks:
  - assertion: "ir.labels.length == 4"
    description: Expected 4 labels emitted across the cascade
    severity: critical

  - assertion: 'ir.flags contains "TOOL-CALL-PENDING-FOR-PDF-PNG"'
    description: PDF/PNG rendering must be flagged as tool-call-pending
    severity: critical

  - assertion: 'ir.labels[?(@.node_id=="SERVICE-480V")].format_applied == "ansi_z535_4"'
    description: SERVICE-480V label uses ANSI Z535.4 format
    severity: critical
    standard_ref: ANSI Z535.4
  # ... (one check per per_label entry × non-discriminator key)
```

### Step 3: Validate the proof-of-concept

```bash
python3 -c "
import json, yaml, jsonschema, sys
schema = json.load(open('shared/schemas/core/eval.schema.json'))
data = yaml.safe_load(open('electrical/arc-flash-labelling/evals/eval-01-us-mixed-cascade-ansi-labels.yaml'))
jsonschema.validate(data, schema); print('PASS')
"
```
Expected: `PASS`.

### Step 4: Apply ruleset to remaining 15 standard files

- [ ] Walk the remaining 8 arc-flash evals (01-09 except those already migrated) and 6 arc-flash-labelling evals (01-07 except eval-08).
- [ ] For each file, apply the ruleset deterministically.
- [ ] If `expected.*` contains a structure not covered by the grammar table, surface it in the commit message and add a brief comment in the YAML.

### Step 5: Handle eval-08 special case

- [ ] Decide Resolution X (split) or Resolution Y (input_fixtures). Recommended: Resolution X.
- [ ] If X: create `eval-08a-qr-code-emitted.yaml` + `eval-08b-qr-code-suppressed.yaml`, archive original.
- [ ] If Y: rewrite as single canonical eval with `input_fixtures: [examples/<best-match-folder>]`. Add a `# TODO: lift remaining A/B conditional grammar once runtime supports scenario flags` comment.

### Step 6: Validate all 17 migrated files (or 18 if split)

```bash
python3 -c "
import json, yaml, jsonschema, glob, sys
schema = json.load(open('shared/schemas/core/eval.schema.json'))
files = sorted(glob.glob('electrical/arc-flash/evals/eval-*.yaml')
             + glob.glob('electrical/arc-flash-labelling/evals/eval-*.yaml'))
files = [f for f in files if '_archive' not in f]
fail = 0
for f in files:
    data = yaml.safe_load(open(f))
    try: jsonschema.validate(data, schema); print(f'PASS {f}')
    except jsonschema.ValidationError as e: print(f'FAIL {f}: {e.message[:120]}'); fail += 1
sys.exit(fail)
"
```
Expected: 17/17 PASS (or 18/18 if eval-08 was split).

### Step 7: Commit

```bash
git add electrical/arc-flash/evals/ electrical/arc-flash-labelling/evals/
git commit -m "feat(sprint-3w2a): Phase B-2 — migrate 17 Format D evals to canonical schema (arc-flash + arc-flash-labelling; eval_id→name, expected.ir_structural+per_label→checks[]; eval-08 split into 8a/8b for A/B conditional emission)"
```

---

## Task 4: Harness extension (Phase C) — Sonnet

**Why Sonnet:** Mechanical Python additions. Pattern is already established by the existing examples pass — extend with two parallel passes that reuse the same helpers (`strip_refs`, jsonschema validation).

**File:** Modify `scripts/validate-examples.py`.

**Architectural shape:**

Refactor `main()` to:
1. Discover skill dirs (as today).
2. Run 3 named passes — each returns `(total, failures, lines_to_print)` and the aggregate exit code is the OR of all three.
3. Print one report block per pass with a clear header. Combine into a final total.

```python
def validate_examples_pass(skill_dirs) -> tuple[int, int, list[str]]:
    """Existing examples pass — extracted as a function."""
    # ... existing logic, returns (total, failures, report_lines)

def validate_evals_pass(skill_dirs, eval_schema) -> tuple[int, int, list[str]]:
    """For each skill dir, validate every eval-*.yaml against eval.schema.json."""
    # ... yaml.safe_load each file; jsonschema.validate against eval_schema

def validate_inputs_pass(skill_dirs, inputs_schema) -> tuple[int, int, list[str]]:
    """For each skill dir, validate inputs.json against inputs.schema.json."""
    # ... json.load each inputs.json; jsonschema.validate

def main(repo_root="."):
    os.chdir(repo_root)
    skill_dirs = discover_skill_dirs()
    eval_schema = strip_refs(json.load(open("shared/schemas/core/eval.schema.json")))
    inputs_schema = strip_refs(json.load(open("shared/schemas/core/inputs.schema.json")))

    ex_tot, ex_fail, ex_lines = validate_examples_pass(skill_dirs)
    ev_tot, ev_fail, ev_lines = validate_evals_pass(skill_dirs, eval_schema)
    in_tot, in_fail, in_lines = validate_inputs_pass(skill_dirs, inputs_schema)

    print("=== Pass 1 — Example outputs ===")
    for line in ex_lines: print(line)
    print(f"\nSubtotal: {ex_tot - ex_fail}/{ex_tot} pass\n")

    print("=== Pass 2 — Eval files ===")
    for line in ev_lines: print(line)
    print(f"\nSubtotal: {ev_tot - ev_fail}/{ev_tot} pass\n")

    print("=== Pass 3 — Inputs files ===")
    for line in in_lines: print(line)
    print(f"\nSubtotal: {in_tot - in_fail}/{in_tot} pass\n")

    total = ex_tot + ev_tot + in_tot
    total_fail = ex_fail + ev_fail + in_fail
    print(f"\n=== AGGREGATE: {total - total_fail}/{total} pass ({total_fail} failures) ===")
    sys.exit(0 if total_fail == 0 else 1)
```

### Step 1: Read the current harness

- [ ] Read `scripts/validate-examples.py` in full. Note `strip_refs()`, `main()`, the skill-dir discovery, and the per-example validation loop.

### Step 2: Extract the examples loop into `validate_examples_pass()`

- [ ] Refactor lines that handle the examples pass into a function returning `(total, failures, lines)`. Keep all the existing edge-case handling (SCHEMA-JSON-PARSE, REF-SCHEMA-PARSE, META-SCHEMA-INVALID, JSON-PARSE, FAIL).

### Step 3: Add `validate_evals_pass()`

For each skill dir, glob `evals/eval-*.yaml`, run `yaml.safe_load`, then `jsonschema.validate(data, eval_schema)`. Skip `runner-config.yaml` (cable-sizing has one). Report shape mirrors examples pass:
- `PASS {skill}/{eval-name}` on success
- `FAIL [YAML-PARSE] {eval-name} -> {error}` for YAML parse failures
- `FAIL [SCHEMA] {eval-name} -> {path}: {message}` for jsonschema validation failures

Requires importing `yaml` at the top of the file:
```python
try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Install: pip install pyyaml", file=sys.stderr)
    sys.exit(2)
```

### Step 4: Add `validate_inputs_pass()`

For each skill dir, look for `inputs.json` at the skill root (not under evals/, not under examples/). Run `json.load`, then `jsonschema.validate(data, inputs_schema)`. Report shape:
- `PASS {skill}/inputs.json`
- `FAIL [JSON-PARSE] {skill}/inputs.json -> {error}`
- `FAIL [SCHEMA] {skill}/inputs.json -> {path}: {message}`

### Step 5: Rewire main() to run all 3 passes and aggregate exit

Per the architectural shape above. Aggregate `total_fail` and exit 0 only if zero failures across all three passes.

### Step 6: Run the harness end-to-end

```bash
python3 scripts/validate-examples.py
```
Expected output structure:
```
=== Pass 1 — Example outputs ===
...
Subtotal: 39/53 pass

=== Pass 2 — Eval files ===
...
Subtotal: 80/80 pass

=== Pass 3 — Inputs files ===
...
Subtotal: 9/9 pass

=== AGGREGATE: 128/142 pass (14 failures) ===
```
Exit code: 1 (because Sprint 3-W2b will fix the 14 db-layout content failures; examples pass still has those). The aggregate is informational — what matters for Sprint 3-W2a acceptance is that the evals pass and inputs pass are 100% green.

Note for the implementer: If the evals pass or inputs pass shows any failure, fix it before committing. The 14 db-layout example failures are out-of-scope for this sprint (deferred to 3-W2b).

### Step 7: Commit

```bash
git add scripts/validate-examples.py
git commit -m "feat(sprint-3w2a): Phase C — extend validate-examples.py harness to 3 passes (examples + evals + inputs.json); pass 2 + pass 3 use the new shared/schemas/core/eval.schema.json + inputs.schema.json"
```

---

## Task 5: CLAUDE.md full revision (Phase D) — Opus

**Why Opus:** Engineering judgment about what to formalise vs leave implicit. The repo has grown from 1 skill (lighting-layout reference) to 9 shipped skills + 6 sprints of established sprint workflow (brainstorm → spec → plan → subagent-driven-development → push → memory save). The current CLAUDE.md (44 lines) is from the lighting-layout era — it lists skill folders + "never do" rules but doesn't document the sprint workflow or model rules. Opus chooses what to include and what to omit.

**File:** Rewrite `CLAUDE.md` end-to-end. ~150-200 lines.

**Required sections (per design spec §3 Phase D):**

1. **Repo intent** — one sentence: open-source MEP engineering skills for AI agents.
2. **Repo shape** — folder structure (electrical/ + mechanical/ + plumbing/ + fire-protection/ + shared/ + docs/ + scripts/), per-skill folder (SKILL.md + EVALS.md + EXAMPLES.md + assets/ + evals/ + examples/ + inputs.json + schemas/ + skill.manifest.json + generator.md + validator.md + reviewer.md).
3. **Schema contracts (shared/schemas/core/)** — list the 4 metaschemas: ir.schema.json, eval.schema.json, inputs.schema.json (new), rationale.schema.json. One sentence per file.
4. **Sprint workflow** — describe the proven brainstorm → spec → plan → subagent execution loop:
   - Brainstorm via superpowers:brainstorming skill, output goes to `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`.
   - Spec self-review + user approval gate.
   - Plan via superpowers:writing-plans skill, output goes to `docs/superpowers/plans/YYYY-MM-DD-<feature>-sprint.md`.
   - Execute via superpowers:subagent-driven-development with two-stage review (spec compliance → code quality).
   - Memory-save the sprint result on ship.
5. **Model selection rules** — Sonnet for mechanical tasks (key renames, schema edits, prompt tweaks); Opus for judgment-heavy tasks (engineering content, structural conversions, reviews); NEVER Haiku. Reference: [[feedback-no-haiku-sonnet-opus-only]] memory.
6. **Golden CI gate** — `scripts/validate-examples.py` runs 3 passes (examples + evals + inputs); `.github/workflows/validate-examples.yml` runs on every push + PR to main. Any new skill PR must pass.
7. **Build status & priority** — current count (5 drawings + 3 calculations = 8 skills shipped; 3 drawings + 4 calculations + 7 documents remain). Reference the breadth-first build strategy.
8. **Standards reference** — keep the existing list (BS 7671:2018, BS EN 12464-1, BS EN 60617, BS 1192/ISO 19650, BS EN 61439, CIBSE Guides, CDM 2015, NRM2). Add KS 1700, IEC 60364, NEC 2023, NFPA 70 per Africa-first + multi-jurisdictional posture.
9. **Citation form rules** — per-jurisdiction conventions: GB `BS 7671:2018+A2:2022 § <reg>`, KE `KS 1700:2018 § <clause> (route to BS 7671 via KS 1700 §313)`, INT `IEC 60364-X-XX:YYYY`, US `NEC 2023 Article X / NFPA 70 § Y`.
10. **Never do** — keep stub bans, EVALS minimum, EXAMPLES minimum, standards values invention; add: never use Haiku; never skip the golden CI gate; never invent calc tool names (calc tools are reused across skills, not authored per skill); never break the 9-value eval category enum without amending eval.schema.json first.
11. **Git commit format** — keep existing.

**What to omit (judgment):** old "Build order" lists that don't reflect current progress; references to the lighting-layout era as "the gold standard" (now 9 skills exist + the schema metaschemas are the canonical reference, not one skill); the explicit drawings/calculations/documents list (move into the build status section as a high-level count rather than a checklist).

### Step 1: Read the current CLAUDE.md

- [ ] Read `CLAUDE.md` in full. Identify which sections to preserve verbatim, paraphrase, or drop.

### Step 2: Verify current repo shape

- [ ] Confirm folder structure:
```bash
ls -d electrical mechanical plumbing fire-protection shared docs scripts 2>/dev/null
ls shared/schemas/core/
ls -d electrical/lighting-layout/* | head -20
```
- [ ] Confirm shipped skill list:
```bash
ls -d electrical/*/SKILL.md 2>/dev/null | sed 's:/SKILL.md::' | sed 's:electrical/::'
```

### Step 3: Verify shared metaschemas

- [ ] List `shared/schemas/core/`:
```bash
ls shared/schemas/core/
```
Confirm: `ir.schema.json`, `eval.schema.json`, `inputs.schema.json` (created in Task 1), `rationale.schema.json`.

### Step 4: Write the new CLAUDE.md

- [ ] Replace `CLAUDE.md` with the new structure per the required-sections list above. Keep tone matter-of-fact (the existing voice). Section headings as `##`. Use short bullet lists rather than prose paragraphs where possible.
- [ ] Target length: ~150-200 lines. If the draft runs longer than 220 lines, trim — this file gets loaded into every Claude Code session, brevity matters.
- [ ] For section 9 (citation form), include 1 concrete example per jurisdiction (not multiple).
- [ ] For section 4 (sprint workflow), reference the superpowers skill names explicitly but do not duplicate their content (Claude already loads them on demand).

### Step 5: Verify the new file is well-formed Markdown

```bash
wc -l CLAUDE.md
head -5 CLAUDE.md
tail -5 CLAUDE.md
```
Expected: 150-200 lines; sensible heading at top; no truncated section at the bottom.

### Step 6: Commit

```bash
git add CLAUDE.md
git commit -m "docs(sprint-3w2a): Phase D — full CLAUDE.md revision; documents the established sprint workflow (brainstorm→spec→plan→subagent-driven-development), model rules (Sonnet+Opus only), golden CI gate (3-pass harness), and citation form per jurisdiction"
```

---

## Task 6: Final validation + push + memory save (Phase E) — Opus

**Why Opus:** Ship-readiness judgment. The aggregate harness may have residual failures from out-of-scope work (the 14 db-layout content bugs deferred to Sprint 3-W2b); the implementer must verify which failures are in-scope vs out-of-scope and only ship when the in-scope ones (evals pass + inputs pass) are 100% green.

### Step 1: Run the full harness

```bash
python3 scripts/validate-examples.py
```

Expected:
```
=== Pass 1 — Example outputs ===
Subtotal: 39/53 pass  (14 db-layout content failures — deferred to Sprint 3-W2b, out-of-scope)

=== Pass 2 — Eval files ===
Subtotal: 80/80 pass  ← MUST be 100% for Sprint 3-W2a acceptance

=== Pass 3 — Inputs files ===
Subtotal: 9/9 pass    ← MUST be 100% for Sprint 3-W2a acceptance

=== AGGREGATE: 128/142 pass (14 failures) ===
```

If Pass 2 or Pass 3 shows any failure, fix it before continuing. The Pass 1 failures are the known db-layout content drift — confirm the failure list matches the 14 examples documented in `sprint-3w-shipped.md` and proceed.

### Step 2: Confirm git state

```bash
git status
git log --oneline origin/main..HEAD
```
Expected: clean working tree, 5 commits ahead of origin/main (one per task 1-5).

### Step 3: Confirm both schema files are well-formed

```bash
python3 -c "import json, jsonschema; jsonschema.Draft7Validator.check_schema(json.load(open('shared/schemas/core/eval.schema.json'))); print('eval OK')"
python3 -c "import json, jsonschema; jsonschema.Draft7Validator.check_schema(json.load(open('shared/schemas/core/inputs.schema.json'))); print('inputs OK')"
```
Expected: both print OK.

### Step 4: Confirm all 9 skills' inputs.json validate

```bash
python3 -c "
import json, jsonschema, glob
schema = json.load(open('shared/schemas/core/inputs.schema.json'))
for f in sorted(glob.glob('electrical/*/inputs.json')):
    data = json.load(open(f))
    jsonschema.validate(data, schema)
    print(f'PASS {f}')
"
```
Expected: 9/9 PASS.

### Step 5: Confirm all 80 evals validate

```bash
python3 -c "
import json, yaml, jsonschema, glob
schema = json.load(open('shared/schemas/core/eval.schema.json'))
files = sorted(f for f in glob.glob('electrical/*/evals/eval-*.yaml') if '_archive' not in f and 'runner-config' not in f)
print(f'Found {len(files)} eval files')
for f in files:
    data = yaml.safe_load(open(f))
    jsonschema.validate(data, schema)
print(f'All {len(files)} evals pass')
"
```
Expected: 80 (or 81 if eval-08 was split into 8a+8b) eval files all pass.

### Step 6: Push

```bash
git push origin main
```
Expected: successful push, no force, hooks pass.

### Step 7: Save sprint-shipped memory

- [ ] Create `/Users/linus/.claude/projects/-Users-linus-Desktop-DraftsMan-SKills-draftsman-skills/memory/sprint-3w2a-shipped.md` following the shape of `sprint-3w-shipped.md`:
  - Frontmatter: name=sprint-3w2a-shipped, type=project, description≈ "Sprint 3-W2a Schema Standardisation shipped <date> — eval.schema.json v2 + inputs.schema.json + 40-eval migration + 3-pass harness + CLAUDE.md rewrite".
  - Body sections: **✅ SHIPPED YYYY-MM-DD** with commit range; **What was delivered** (6 task summary); **Harness end-state** (80/80 evals + 9/9 inputs + 39/53 examples — 14 example failures still pending Sprint 3-W2b); **Known follow-up** (Sprint 3-W2b content completion: 10 db-layout rationale blocks + 4 board sub-shape reconciliations + lighting-layout assets/validator/reviewer/manifest + missing standards files + compliance_failure evals); **Cross-references** (link to [[sprint-3w-shipped]], [[runtime-project-boundary]], [[feedback-no-haiku-sonnet-opus-only]], [[build-strategy-breadth-first]]).
- [ ] Update `MEMORY.md` with a 1-line index entry pointing at `sprint-3w2a-shipped.md`.

### Step 8: Report to user

Summary report ≤ 8 lines covering: commit range pushed, evals pass result, inputs pass result, examples pass unchanged (14 known failures deferred), next sprint (3-W2b content completion). Quote the harness aggregate line verbatim.

---

## Risks & Mitigations

- **Format C grammar gap risk** — A Format C `assertions[]` item uses a `kind:` not in the grammar table. Mitigation: halt and surface; do not invent a translation. Task 2 Step 5 explicitly bans inventing.
- **Format D per-label expansion bloat** — A single `expected.per_label` with 6 items × 4 keys = 24 check items. Mitigation: accept the bloat; the canonical form is explicit by design. The runtime will roll up reporting per-eval anyway.
- **eval-08 ambiguity** — Resolution X vs Y is judgment-dependent. Mitigation: implementer documents the choice in the commit message; both resolutions are acceptable to the schema.
- **CLAUDE.md drift from skill set** — If a new skill ships during this sprint, the build status section is stale. Mitigation: no other sprint runs in parallel with 3-W2a (single-thread sprint discipline).
- **Harness Python yaml dep risk** — If PyYAML is missing in CI, Pass 2 fails. Mitigation: Task 4 Step 3 imports yaml at the top with a friendly error; the existing GitHub Action installs `jsonschema` — adding `pyyaml` is a 1-line workflow edit. Verify before pushing.
- **Memory write path risk** — The memory directory is under `~/.claude/projects/...`, not the repo. Mitigation: Task 6 Step 7 uses absolute path; no risk of accidentally committing memory into the repo.

---

## Self-Review (after writing)

Did the plan cover every spec section?
- §1 locked decisions ✓ (formalise emerged conventions in Task 1; inputs.schema.json in Task 1; harness extension in Task 4; CLAUDE.md rewrite in Task 5)
- §2 gap inventory addressed-vs-deferred ✓ (addressed in Tasks 1-5; out-of-scope items called out in Task 6 Step 7 follow-up list)
- §3 Phase A-E ✓ (Tasks 1, 2+3, 4, 5, 6)
- §4 file-ops summary ✓ (~44 ops mapped: 2 schemas + 40 evals + 1 harness + 1 doc + 0-2 split files)
- §5 risks ✓ (mirrored in Risks section)
- §6 out-of-scope handoff ✓ (Sprint 3-W2b queue documented in Task 6 Step 7)
- §7 acceptance criteria ✓ (Task 6 Step 1 expected output explicit; 80/80 + 9/9 mandatory, 39/53 examples is acceptable carryover)

Placeholder scan: no TBD, no "implement later", no "similar to Task N" without code. Every step that changes code shows the full target shape or the deterministic ruleset.

Type consistency: `name`, `skill`, `category`, `input`, `input_fixtures`, `checks`, `assertion`, `description`, `severity`, `standard_ref` — used consistently across tasks 1, 2, 3 with the schema in Task 1.

Spec quote alignment: design spec §3 Phase B said "input_fixtures + TODO" for eval-08; this plan offers Resolution X (split) as a recommended alternative because it preserves test fidelity better. Documented as a judgment call — both options are accepted by the canonical schema. No spec contradiction.
