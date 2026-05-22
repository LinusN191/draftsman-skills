# Skill-Author Bug Fix Sprint (Sprint 3-W) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Clear all skill-author bugs surfaced by Sprint 3-V runtime E2E testing + the golden-example schema validation harness. Ship the harness as a permanent CI gate so the same class of bugs can't reappear.

**Architecture:** 6 phases as 6 atomic tasks, executed in order. Phase A ships the CI gate first so every subsequent fix is verified by a single `python3 scripts/validate-examples.py` command. Phases B-E apply surgical schema/example/prompt fixes per the design spec. Phase F runs the harness against the full repo (expected 53/53 pass, up from 36/53 baseline) and pushes.

**Tech Stack:** Python 3 + jsonschema (existing repo dependency), YAML 1.2 (GitHub Actions workflow), Markdown. No new code paths in any skill — only content edits (schemas, examples, prompts).

**Spec referenced:** `docs/superpowers/specs/2026-05-20-skill-author-bug-fix-sprint-design.md` (commit bfff9c9)

---

## Reference table — pre-flight verifications

| Verification | Result |
|---|---|
| Golden harness baseline | 36/53 pass (17 failures: 15 db-layout + 2 earthing) |
| db-layout NEW-shape sub-objects | Extracted from `intl-dbcomms-data/output.json` — `incoming_supply` (6 fields), `main_switch` (4 fields), `spare_ways` (integer) |
| db-layout OLD-shape survey | 6 examples; all have `board.ways_spare` populated already → easy `spare_ways` lift |
| lighting-layout schema location | `shared/schemas/electrical/lighting-layout-ir.schema.json` (the skill's local `schemas/lighting-layout-ir.schema.json` is just a `$ref` pointer) |
| lighting-layout zones[].items.required | `['zone_id', 'circuit_id']` — confirms runtime error |
| lighting-layout luminaires[].items.required | `['id', 'x_mm', 'y_mm', 'circuit_id']` — confirms runtime error |
| lighting-layout initial_lumens type | `integer` — confirms runtime error (Claude likely emits float) |
| `scripts/` folder exists | NO (Phase A creates it) |
| `.github/workflows/` exists | NO (Phase A creates it) |
| Shared rationale maxLength locations | Line 13 (chat_summary, 500 — UNCHANGED) and line 35 (Section.summary, 400 → 800) |

---

## Phase A — Golden harness CI (Task 1)

### Task 1: scripts/validate-examples.py + .github/workflows/validate-examples.yml

**Model:** Sonnet (mechanical Python + YAML; no engineering judgement).

**Files:**
- Create: `scripts/validate-examples.py`
- Create: `.github/workflows/validate-examples.yml`

- [ ] **Step 1: Create the scripts directory + write the harness**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
mkdir -p scripts
```

Then Write `scripts/validate-examples.py` with this exact content:

```python
#!/usr/bin/env python3
"""Golden-example schema validation harness.

For each skill folder that has examples/*/output.json + schemas/*-ir.schema.json,
validate every example output against its skill's IR schema. Reports per-skill
+ per-example pass/fail. Returns exit 0 on full pass, exit 1 on any failure.

Recursively strips $ref nodes to {type: object} before validation — focuses on
inline schema-shape bugs rather than external-ref resolution (rationale, intent,
etc.). Ref resolution is the runtime's job; this harness catches author bugs in
the inline schema definitions.
"""
import json
import sys
import os
import glob
import copy
from collections import defaultdict

try:
    import jsonschema
except ImportError:
    print("ERROR: jsonschema not installed. Install: pip install jsonschema", file=sys.stderr)
    sys.exit(2)


def strip_refs(node):
    """Recursively replace any {$ref: ...} with {type: object}."""
    if isinstance(node, dict):
        if "$ref" in node:
            return {"type": "object"}
        return {k: strip_refs(v) for k, v in node.items()}
    if isinstance(node, list):
        return [strip_refs(v) for v in node]
    return node


def main(repo_root="."):
    os.chdir(repo_root)
    results = defaultdict(list)
    total_examples = 0
    total_failures = 0

    # Discover skill folders by scanning for schemas/*-ir.schema.json under disciplines
    skill_glob_patterns = [
        "electrical/*/schemas/*-ir.schema.json",
        "mechanical/*/schemas/*-ir.schema.json",
        "plumbing/*/schemas/*-ir.schema.json",
        "fire-protection/*/schemas/*-ir.schema.json",
    ]
    schemas_found = []
    for pat in skill_glob_patterns:
        schemas_found.extend(glob.glob(pat))

    skill_dirs = sorted(set(os.path.dirname(os.path.dirname(p)) for p in schemas_found))

    for skill_dir in skill_dirs:
        skill_name = os.path.basename(skill_dir)
        schema_glob = glob.glob(f"{skill_dir}/schemas/*-ir.schema.json")
        if not schema_glob:
            continue
        schema_path = schema_glob[0]

        try:
            with open(schema_path) as f:
                schema = json.load(f)
        except json.JSONDecodeError as e:
            results[skill_name].append(("SCHEMA-JSON-PARSE", schema_path, str(e)[:200]))
            total_failures += 1
            continue

        # Resolve a single level of $ref at the schema root if the local schema is just a pointer
        # to shared/schemas/electrical/<skill>-ir.schema.json
        if "$ref" in schema and len(schema.keys()) <= 5:
            ref = schema["$ref"]
            # Resolve relative to the schema_path's directory
            resolved_path = os.path.normpath(os.path.join(os.path.dirname(schema_path), ref))
            if os.path.exists(resolved_path):
                try:
                    with open(resolved_path) as f:
                        schema = json.load(f)
                except json.JSONDecodeError as e:
                    results[skill_name].append(("REF-SCHEMA-PARSE", resolved_path, str(e)[:200]))
                    total_failures += 1
                    continue

        # Strip all $refs from the schema we'll test against
        schema_test = strip_refs(schema)

        # Verify the schema itself is well-formed Draft-07
        try:
            jsonschema.Draft7Validator.check_schema(schema_test)
        except Exception as e:
            results[skill_name].append(("META-SCHEMA-INVALID", schema_path, str(e)[:200]))

        examples = sorted(glob.glob(f"{skill_dir}/examples/*/output.json"))
        for ex_path in examples:
            total_examples += 1
            ex_name = os.path.basename(os.path.dirname(ex_path))
            try:
                with open(ex_path) as f:
                    out = json.load(f)
            except json.JSONDecodeError as e:
                results[skill_name].append(("JSON-PARSE", ex_name, str(e)[:200]))
                total_failures += 1
                continue
            try:
                jsonschema.validate(out, schema_test)
                results[skill_name].append(("PASS", ex_name, ""))
            except jsonschema.ValidationError as e:
                total_failures += 1
                path = ".".join(str(p) for p in list(e.absolute_path)[:6])
                results[skill_name].append(("FAIL", ex_name, f"{path}: {e.message[:160]}"))

    # Report
    print(f"=== Golden-example schema validation — {len(skill_dirs)} skills, {total_examples} examples ===\n")
    for skill in sorted(results.keys()):
        entries = results[skill]
        failures = [e for e in entries if e[0] != "PASS"]
        passes = [e for e in entries if e[0] == "PASS"]
        status = "PASS" if not failures else f"FAIL ({len(failures)} failures, {len(passes)} pass)"
        print(f"\n## {skill}: {status}")
        for kind, name, msg in entries:
            if kind == "PASS":
                print(f"  PASS {name}")
            else:
                print(f"  FAIL [{kind}] {name}")
                if msg:
                    print(f"       -> {msg}")

    print(f"\n=== TOTAL: {total_examples - total_failures}/{total_examples} pass ({total_failures} failures) ===")
    sys.exit(0 if total_failures == 0 else 1)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Make the harness executable + smoke-test**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
chmod +x scripts/validate-examples.py
python3 scripts/validate-examples.py
echo "Exit code: $?"
```

Expected output: `=== TOTAL: 36/53 pass (17 failures) ===` then `Exit code: 1`. Failures are the known db-layout (15) + earthing (2) that Phases B + C will fix.

- [ ] **Step 3: Create the GitHub Actions workflow**

```bash
mkdir -p .github/workflows
```

Then Write `.github/workflows/validate-examples.yml` with this exact content:

```yaml
name: Validate Examples

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install jsonschema

      - name: Run golden-example schema validation
        run: python3 scripts/validate-examples.py
```

- [ ] **Step 4: Smoke-test YAML parses**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
python3 -c "import yaml; d = yaml.safe_load(open('.github/workflows/validate-examples.yml')); print(d['name'], d['jobs']['validate']['runs-on'])"
```

Expected: `Validate Examples ubuntu-latest`

- [ ] **Step 5: Commit**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
git add scripts/ .github/workflows/
git commit -m "feat(ci): golden-example schema validation harness + GitHub Actions workflow (Sprint 3-W Phase A)"
```

---

## Phase B — db-layout schema migration (Task 2)

### Task 2: Schema migration + 6 example migrations + prompt update + drawn_as_symbols relaxation

**Model:** Opus (engineering judgement: extracting canonical sub-shape from NEW-shape example, migrating 6 OLD-shape examples per the documented mechanic, prompt edits).

**Files:**
- Modify: `electrical/db-layout/schemas/db-layout-ir.schema.json`
- Modify: `electrical/db-layout/examples/uk-domestic-consumer-unit/output.json`
- Modify: `electrical/db-layout/examples/us-strip-mall-common-area/output.json` (also: `severity: high` → `warning`)
- Modify: `electrical/db-layout/examples/us-strip-mall-panelboard/output.json`
- Modify: `electrical/db-layout/examples/us-strip-mall-tsp-a/output.json`
- Modify: `electrical/db-layout/examples/us-strip-mall-tsp-b/output.json`
- Modify: `electrical/db-layout/examples/intl-commercial-tpn-msb/output.json`
- Modify: `electrical/db-layout/prompts/generator.md`

- [ ] **Step 1: Read the NEW-shape canonical sub-objects (from intl-dbcomms-data)**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
python3 -c "
import json
o = json.load(open('electrical/db-layout/examples/intl-dbcomms-data/output.json'))
for k in ['incoming_supply', 'main_switch', 'spare_ways']:
    print(f'--- {k} ---')
    print(json.dumps(o[k], indent=2))
"
```

Expected output:
```
--- incoming_supply ---
{
  "voltage_v": 400,
  "phase_arrangement": "TPN_plus_E",
  "supply_rating_a": 32,
  "fed_from": "MSB-MAIN F06 ...",
  "supply_class": "essential",
  "declared_pfc_ka": 8.0
}
--- main_switch ---
{
  "type": "switch-disconnector",
  "rating_a": 32,
  "breaking_capacity_ka": 10,
  "fault_level_a_min": 8000
}
--- spare_ways ---
3
```

- [ ] **Step 2: Read current db-layout schema top-level required + incoming/busbar definitions**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
python3 -c "
import json
s = json.load(open('electrical/db-layout/schemas/db-layout-ir.schema.json'))
print('required:', s['required'])
print()
for k in ['incoming', 'busbar', 'incoming_supply', 'main_switch', 'spare_ways', 'drawn_as_symbols']:
    v = s.get('properties', {}).get(k, '(not defined)')
    print(f'--- properties.{k} ---')
    print(json.dumps(v, indent=2)[:400] if isinstance(v, dict) else v)
    print()
"
```

Use the output to know which existing property blocks to delete + which to add.

- [ ] **Step 3: Update db-layout schema — top-level required**

Use Edit on `electrical/db-layout/schemas/db-layout-ir.schema.json`:

Find the existing top-level `"required"` array:
```json
"required": ["drawing_type", "version", "meta", "jurisdiction", "board", "incoming", "busbar", "circuits", "selectivity_results", "compliance_summary", "rationale"]
```

Replace with:
```json
"required": ["drawing_type", "version", "meta", "jurisdiction", "board", "incoming_supply", "main_switch", "spare_ways", "circuits", "selectivity_results", "compliance_summary", "rationale"]
```

(The exact whitespace / line-breaks may differ — use Read first to find the exact current line.)

- [ ] **Step 4: Update db-layout schema — replace `incoming` + `busbar` property blocks with `incoming_supply` + `main_switch` + `spare_ways`**

Use Edit on `electrical/db-layout/schemas/db-layout-ir.schema.json`. The schema's `properties.incoming` and `properties.busbar` blocks need to be replaced by these three new blocks. Use Read to find the existing exact content of `properties.incoming` and `properties.busbar`, then Edit to replace.

Replace the `"incoming": { ... }` block with:

```json
"incoming_supply": {
  "type": "object",
  "required": ["voltage_v", "phase_arrangement", "supply_rating_a", "fed_from", "supply_class", "declared_pfc_ka"],
  "additionalProperties": false,
  "properties": {
    "voltage_v":          { "type": "integer", "enum": [120, 208, 230, 240, 277, 400, 415, 480] },
    "phase_arrangement":  { "enum": ["single_phase", "single_phase_split", "TPN", "TPN_plus_E"] },
    "supply_rating_a":    { "type": "number", "exclusiveMinimum": 0 },
    "fed_from":           { "type": "string" },
    "supply_class":       { "enum": ["essential", "non_essential", "life_safety", "ups_backed", "genset_backed"] },
    "declared_pfc_ka":    { "type": "number", "minimum": 0 }
  }
}
```

Replace the `"busbar": { ... }` block with:

```json
"main_switch": {
  "type": "object",
  "required": ["type", "rating_a", "breaking_capacity_ka"],
  "additionalProperties": false,
  "properties": {
    "type":                 { "enum": ["switch-disconnector", "MCCB", "isolator", "RCCB", "RCBO", "main_switch_fused"] },
    "rating_a":             { "type": "number", "exclusiveMinimum": 0 },
    "breaking_capacity_ka": { "type": "number", "exclusiveMinimum": 0 },
    "fault_level_a_min":    { "type": "number", "minimum": 0 }
  }
},
"spare_ways": { "type": "integer", "minimum": 0 }
```

(Adapt enum lists if the existing schema has wider/narrower sets — Read first to confirm.)

- [ ] **Step 5: Relax drawn_as_symbols schema (drawn_as_symbols items accept string OR object)**

Find the existing `drawn_as_symbols` definition (Step 2 output above will show its current shape):

```json
"drawn_as_symbols": {
  "type": "array",
  "items": { "type": "string", "pattern": "^[A-Z][A-Z0-9_]*$" }
}
```

Replace with:

```json
"drawn_as_symbols": {
  "type": "array",
  "items": {
    "oneOf": [
      { "type": "string", "pattern": "^[A-Z][A-Z0-9_]*$" },
      { "type": "object" }
    ]
  }
}
```

- [ ] **Step 6: Validate db-layout schema still parses as Draft-07**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
python3 -c "
import json, jsonschema
s = json.load(open('electrical/db-layout/schemas/db-layout-ir.schema.json'))
jsonschema.Draft7Validator.check_schema(s)
assert 'incoming_supply' in s['required']
assert 'main_switch' in s['required']
assert 'spare_ways' in s['required']
assert 'incoming' not in s['required']
assert 'busbar' not in s['required']
print('schema: valid Draft-07; new shape required; old shape required[] dropped')
"
```

Expected: `schema: valid Draft-07; new shape required; old shape required[] dropped`

- [ ] **Step 7: Migrate uk-domestic-consumer-unit/output.json**

Read the file first, then apply 3 Edits + 1 conditional cleanup.

**Edit 1** — Replace the `"incoming": { ... }` block with `"incoming_supply": { ... }`:

Find:
```json
"incoming": {
    "voltage_v": 230,
    "phase_arrangement": "single_phase",
    "supply_rating_a": 100,
    "fed_from": "MAIN",
    "supply_class": "non_essential",
    "ze_ohm_at_origin": 0.35
  }
```

Replace:
```json
"incoming_supply": {
    "voltage_v": 230,
    "phase_arrangement": "single_phase",
    "supply_rating_a": 100,
    "fed_from": "MAIN",
    "supply_class": "non_essential",
    "declared_pfc_ka": 7.5
  }
```

(`ze_ohm_at_origin` → `declared_pfc_ka` of `busbar.ipk_ka` value = 7.5)

**Edit 2** — Replace the `"busbar": { ... }` block with `"main_switch": { ... }` + add `"spare_ways"`:

Find:
```json
"busbar": {
    "rating_a": 100,
    "icw_ka_1s": 6,
    "ipk_withstand_ka": 12,
    "ipk_ka": 7.5
  }
```

Replace:
```json
"main_switch": {
    "type": "switch-disconnector",
    "rating_a": 100,
    "breaking_capacity_ka": 12,
    "fault_level_a_min": 7500
  },
  "spare_ways": 6
```

(`breaking_capacity_ka` from `busbar.ipk_withstand_ka` = 12; `fault_level_a_min` = `busbar.ipk_ka × 1000` = 7500; `spare_ways` from `board.ways_spare` = 6.)

**Edit 3** — Reasoning.md scan: check if it references `incoming.ze_ohm_at_origin` or `busbar` by name.

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
grep -nE 'ze_ohm_at_origin|\bbusbar\b' electrical/db-layout/examples/uk-domestic-consumer-unit/reasoning.md || echo "(no references)"
```

If matches found, update each reference to mention the new field names. Otherwise skip.

- [ ] **Step 8: Migrate us-strip-mall-common-area/output.json (+ severity fix)**

Migration mechanic identical to Step 7. Values: `incoming.supply_rating_a=60`, `incoming.ze_ohm_at_origin=0.12`, `busbar.{rating_a=60, icw_ka_1s=10, ipk_withstand_ka=22, ipk_ka=15}`, `board.ways_spare=13`.

**Edit 1** — replace `"incoming": {...}`:
```json
"incoming_supply": {
    "voltage_v": ...,
    "phase_arrangement": ...,
    "supply_rating_a": 60,
    "fed_from": "...",
    "supply_class": "...",
    "declared_pfc_ka": 15
  }
```

**Edit 2** — replace `"busbar": {...}`:
```json
"main_switch": {
    "type": "switch-disconnector",
    "rating_a": 60,
    "breaking_capacity_ka": 22,
    "fault_level_a_min": 15000
  },
  "spare_ways": 13
```

**Edit 3** — `severity: "high"` → `"warning"` in the existing non_compliance_flags entry. Use Read first to find the exact line + adjacent message context to make the edit precise:

```bash
grep -n '"severity": "high"' electrical/db-layout/examples/us-strip-mall-common-area/output.json
```

Find the exact line (in context):
```json
"severity": "high",
"message": "Bus rating concern: 60A intake busbar + 60A C05 fire pump branch leaves no headr..."
```

Replace `"severity": "high"` with `"severity": "warning"` (preserve the message + code_clause fields).

**Edit 4** — reasoning.md scan as in Step 7 Edit 3.

- [ ] **Step 9: Migrate us-strip-mall-panelboard/output.json**

Migration mechanic identical. Values: `incoming.supply_rating_a=200`, `incoming.ze_ohm_at_origin=0.20`, `busbar.{rating_a=200, ipk_withstand_ka=22, ipk_ka=15}`, `board.ways_spare=19`.

**Edit 1** — `incoming_supply.declared_pfc_ka=15`. Other fields keep existing values + rename block.

**Edit 2** — `main_switch.{type: "switch-disconnector", rating_a: 200, breaking_capacity_ka: 22, fault_level_a_min: 15000}`; `spare_ways: 19`.

**Edit 3** — reasoning.md scan.

- [ ] **Step 10: Migrate us-strip-mall-tsp-a/output.json**

Values: `incoming.supply_rating_a=100`, `incoming.ze_ohm_at_origin=0.10`, `busbar.{rating_a=100, ipk_withstand_ka=22, ipk_ka=15}`, `board.ways_spare=22`.

**Edit 1** — `incoming_supply.declared_pfc_ka=15`.

**Edit 2** — `main_switch.{type: "switch-disconnector", rating_a: 100, breaking_capacity_ka: 22, fault_level_a_min: 15000}`; `spare_ways: 22`.

**Edit 3** — reasoning.md scan.

- [ ] **Step 11: Migrate us-strip-mall-tsp-b/output.json**

Values: `incoming.supply_rating_a=100`, `incoming.ze_ohm_at_origin=0.10`, `busbar.{rating_a=100, ipk_withstand_ka=22, ipk_ka=15}`, `board.ways_spare=21`.

**Edit 1** — `incoming_supply.declared_pfc_ka=15`.

**Edit 2** — `main_switch.{type: "switch-disconnector", rating_a: 100, breaking_capacity_ka: 22, fault_level_a_min: 15000}`; `spare_ways: 21`.

**Edit 3** — reasoning.md scan.

- [ ] **Step 12: Migrate intl-commercial-tpn-msb/output.json**

Values: `incoming.supply_rating_a=800`, `incoming.ze_ohm_at_origin=0.05`, `busbar.{rating_a=800, ipk_withstand_ka=80, ipk_ka=55}`, `board.ways_spare=8`. This is a TPN MSB, so the main switch is more likely an MCCB than a switch-disconnector.

**Edit 1** — `incoming_supply.declared_pfc_ka=55`.

**Edit 2** — `main_switch.{type: "MCCB", rating_a: 800, breaking_capacity_ka: 80, fault_level_a_min: 55000}`; `spare_ways: 8`.

**Edit 3** — reasoning.md scan.

- [ ] **Step 13: Update db-layout generator.md — add jurisdiction reminder + new-shape narrative**

Read the existing generator first:

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
grep -n 'jurisdiction\|incoming\|busbar' electrical/db-layout/prompts/generator.md | head -20
```

Apply two prompt updates:

**Edit A** — Add a "Top-level required fields" reminder. Find an early step (likely "Step 1" or the "Inputs" section). Add (or strengthen existing) a paragraph reading:

```
**Top-level required fields you MUST emit:** drawing_type, version, meta, jurisdiction, board, incoming_supply, main_switch, spare_ways, circuits, selectivity_results, compliance_summary, rationale. Omitting `jurisdiction` is a common error — it's a single string at the IR root, NOT inside `meta`.
```

(If the prompt already has a required-fields list, just add the `jurisdiction` reminder + ensure the list matches the new schema's required[].)

**Edit B** — Find any step that references `incoming` or `busbar` by name and update to `incoming_supply` / `main_switch` / `spare_ways`. Use:

```bash
grep -n 'incoming\b\|busbar' electrical/db-layout/prompts/generator.md
```

For each match, update the field reference. Common patterns to look for:
- "Set `incoming.supply_rating_a`..." → "Set `incoming_supply.supply_rating_a`..."
- "The `busbar` block carries..." → "The `main_switch` block carries the OCPD device at the incomer; the busbar rating is part of the main_switch's `breaking_capacity_ka`..."

- [ ] **Step 14: Validate db-layout end-to-end with the harness**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
python3 scripts/validate-examples.py 2>&1 | grep -A 25 "## db-layout"
```

Expected: 20/20 db-layout examples PASS (no FAIL entries under db-layout).

- [ ] **Step 15: Commit**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
git add electrical/db-layout/
git commit -m "fix(db-layout): adopt NEW shape — incoming_supply + main_switch + spare_ways; migrate 6 OLD-shape examples; severity:high→warning; drawn_as_symbols relaxation; jurisdiction prompt reminder (Sprint 3-W Phase B)"
```

---

## Phase C — earthing 2 example enum migrations (Task 3)

### Task 3: uk-commercial-3storey + intl-rural-tt example fixes

**Model:** Sonnet (mechanical edits — schema stays put, only 2 example field values change).

**Files:**
- Modify: `electrical/earthing/examples/uk-commercial-3storey/output.json`
- Modify: `electrical/earthing/examples/intl-rural-tt/output.json`

- [ ] **Step 1: Read each example's met block to find exact context**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
grep -B1 -A1 'supply_bond_type' electrical/earthing/examples/uk-commercial-3storey/output.json
grep -B1 -A1 'supply_bond_type' electrical/earthing/examples/intl-rural-tt/output.json
```

- [ ] **Step 2: Migrate uk-commercial-3storey**

Use Edit on `electrical/earthing/examples/uk-commercial-3storey/output.json`:

- Find: `"supply_bond_type": "tn_c_s_pen"`
- Replace: `"supply_bond_type": "dno_pme_bond"`

(Both terms describe TN-C-S/PME at the cut-out; canonical taxonomy uses `dno_pme_bond`.)

- [ ] **Step 3: Migrate intl-rural-tt**

Use Edit on `electrical/earthing/examples/intl-rural-tt/output.json`:

- Find: `"supply_bond_type": "utility_pen_bond"`
- Replace: `"supply_bond_type": "consumer_electrode_only"`

(Filename says "tt"; TT systems by definition have NO utility bond — the original value was a terminology mistake. `consumer_electrode_only` is the correct TT taxonomy.)

- [ ] **Step 4: Check reasoning.md for both examples — if the narrative references the old term, update**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
grep -n 'tn_c_s_pen\|utility_pen_bond' electrical/earthing/examples/uk-commercial-3storey/reasoning.md electrical/earthing/examples/intl-rural-tt/reasoning.md || echo "(no narrative references)"
```

For any matches: update the narrative to use the new term + add a brief note explaining the taxonomy (e.g., "TN-C-S supply bonded at the DNO cut-out — `dno_pme_bond` in the schema taxonomy"). If no matches, skip.

- [ ] **Step 5: Validate earthing end-to-end with the harness**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
python3 scripts/validate-examples.py 2>&1 | grep -A 8 "## earthing"
```

Expected: 5/5 earthing examples PASS.

- [ ] **Step 6: Commit**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
git add electrical/earthing/examples/
git commit -m "fix(earthing): migrate 2 examples to existing supply_bond_type enum — tn_c_s_pen→dno_pme_bond + utility_pen_bond→consumer_electrode_only (Sprint 3-W Phase C)"
```

---

## Phase D — lighting-layout prompt fixes (Task 4)

### Task 4: zone_id + circuit_id + initial_lumens type precision

**Model:** Sonnet (focused prompt edit; no schema or example changes).

**Files:**
- Modify: `electrical/lighting-layout/prompts/generator.md`

- [ ] **Step 1: Confirm canonical schema field types**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
python3 -c "
import json
s = json.load(open('shared/schemas/electrical/lighting-layout-ir.schema.json'))
print('zones.items.required:', s['properties']['zones']['items']['required'])
print('luminaires.items.required:', s['properties']['luminaires']['items']['required'])
print('initial_lumens type:', s['properties']['luminaire_type']['properties']['initial_lumens'])
"
```

Expected:
```
zones.items.required: ['zone_id', 'circuit_id']
luminaires.items.required: ['id', 'x_mm', 'y_mm', 'circuit_id']
initial_lumens type: {'type': 'integer'}
```

- [ ] **Step 2: Read current lighting-layout generator.md to find insertion points**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
grep -n 'zones\|luminaires\|initial_lumens\|zone_id\|circuit_id' electrical/lighting-layout/prompts/generator.md | head -30
```

- [ ] **Step 3: Add "Field-name precision" section to generator.md**

Use Edit to add (or strengthen) field-precision guidance. The most reliable placement is in a section called "Common errors to avoid" or similar — or just after the IR shape declaration. If neither exists, add a new H2 section before "Output Format":

```markdown
## Field-name precision (avoid these common mistakes)

The IR schema is strict about field names. The LLM has a tendency to generalise these to more "natural" English keys; the runtime validator will reject these emissions, so name them exactly as below:

- **Zones**: every entry in `zones[]` carries `zone_id` (NOT `id`). The full required set for each zone is `[zone_id, circuit_id]`. The schema rejects `{"id": "Z1", ...}`.
- **Luminaires**: every entry in `luminaires[]` carries a `circuit_id` referencing the parent zone's circuit. Schema required set is `[id, x_mm, y_mm, circuit_id]`. (The luminaire's own identifier IS named `id` — only the zone uses `zone_id`.)
- **Luminaire types**: `luminaire_type.initial_lumens` is an **integer** (e.g., `4200`, not `4200.0` or `"4200"`). The schema declares `type: integer`.

If the runtime rejects your IR for one of these, re-read this section — most of the time it's a field-naming slip, not a structural problem.
```

- [ ] **Step 4: Verify the edit landed by re-reading the prompt**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
grep -A 1 '^## Field-name precision' electrical/lighting-layout/prompts/generator.md
grep -c 'zone_id\|initial_lumens.*integer\|circuit_id' electrical/lighting-layout/prompts/generator.md
```

Expected: section header present + counts > 0.

- [ ] **Step 5: Confirm harness still passes lighting-layout (no regression)**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
python3 scripts/validate-examples.py 2>&1 | grep -A 5 "## lighting-layout"
```

Expected: 3/3 lighting-layout examples PASS (no change — examples were already passing; only prompt updated).

- [ ] **Step 6: Commit**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
git add electrical/lighting-layout/prompts/generator.md
git commit -m "fix(lighting-layout): generator prompt — field-name precision (zone_id, circuit_id on luminaires, initial_lumens integer) per Sprint 3-V runtime feedback (Sprint 3-W Phase D)"
```

---

## Phase E — Shared rationale schema maxLength bump (Task 5)

### Task 5: definitions.Section.properties.summary.maxLength 400 → 800

**Model:** Sonnet (one-line edit).

**Files:**
- Modify: `shared/schemas/core/rationale.schema.json`

- [ ] **Step 1: Read the current rationale schema to find line 35 (Section.summary.maxLength)**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
sed -n '30,40p' shared/schemas/core/rationale.schema.json
```

Expected: the `Section.summary` property with `"maxLength": 400`.

- [ ] **Step 2: Apply the maxLength bump**

Use Edit on `shared/schemas/core/rationale.schema.json`. Find the `Section.summary` property block. Use enough surrounding context to disambiguate from `chat_summary.maxLength: 500` on line 13:

- Find:
```json
"summary": {
          "type": "string",
          "minLength": 1,
          "maxLength": 400,
```

- Replace:
```json
"summary": {
          "type": "string",
          "minLength": 1,
          "maxLength": 800,
```

(Adjust whitespace to match the file. The `chat_summary.maxLength: 500` is intentionally left alone — that controls the top-level inline chat summary, not the per-section summary.)

- [ ] **Step 3: Validate change landed correctly + chat_summary cap unchanged**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
python3 -c "
import json
s = json.load(open('shared/schemas/core/rationale.schema.json'))
sec = s['definitions']['Section']['properties']['summary']
cs = s['properties']['chat_summary']
print(f'Section.summary maxLength: {sec[\"maxLength\"]}')
print(f'chat_summary maxLength:    {cs[\"maxLength\"]}')
assert sec['maxLength'] == 800
assert cs['maxLength'] == 500
print('Phase E: OK (Section.summary 400→800; chat_summary stays 500)')
"
```

Expected: `Phase E: OK (Section.summary 400→800; chat_summary stays 500)`

- [ ] **Step 4: Confirm harness still passes all 53 examples (no regression)**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
python3 scripts/validate-examples.py 2>&1 | tail -5
```

Expected: `=== TOTAL: 53/53 pass (0 failures) ===`

(All existing example section summaries are well under 400 chars already, so the bump from 400 to 800 cannot cause any regression — only adds headroom for future Claude outputs.)

- [ ] **Step 5: Commit**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
git add shared/schemas/core/rationale.schema.json
git commit -m "fix(rationale): bump Section.summary maxLength 400→800 — Sprint 3-V runtime feedback (Sprint 3-W Phase E)"
```

---

## Phase F — Final validation + push (Task 6)

### Task 6: 53/53 confirmation + push to origin/main + memory save

**Model:** Opus (judgement on ship-readiness; manages the push gate).

This task makes NO new content. It validates the assembled sprint end-to-end and pushes.

- [ ] **Step 1: Run the golden harness with verbose output**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
python3 scripts/validate-examples.py
echo "Exit code: $?"
```

Expected: full output with every skill showing PASS for every example. Final line: `=== TOTAL: 53/53 pass (0 failures) ===`. Exit code: 0.

If exit code is non-zero (any FAIL), STOP. Re-read the failed example output + the schema, fix the specific drift, re-commit under the appropriate phase, re-run.

- [ ] **Step 2: List sprint commits**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
git log --oneline bfff9c9..HEAD
git status
```

Expected: 5 commits (one per Phase A-E). Working tree clean.

- [ ] **Step 3: Push to origin/main**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
git push origin main
```

If push fails (remote rejected etc.), STOP and report. Do not force push.

- [ ] **Step 4: Confirm CI workflow triggers + passes on the push**

After push, the `.github/workflows/validate-examples.yml` workflow should fire automatically. Confirm by reading the workflow run page (if `gh` CLI is available + authenticated):

```bash
gh run list --limit 3 --workflow validate-examples.yml 2>/dev/null || echo "(gh not available — verify in browser at github.com/<repo>/actions)"
```

Expected: most-recent run is `completed` `success`.

- [ ] **Step 5: Save sprint memory**

Write `/Users/linus/.claude/projects/-Users-linus-Desktop-DraftsMan-SKills-draftsman-skills/memory/sprint-3w-shipped.md`:

```markdown
---
name: sprint-3w-shipped
description: Sprint 3-W skill-author bug fix shipped 2026-05-20 — golden-example CI gate + db-layout NEW-shape adoption + earthing enum migration + lighting-layout prompt precision + shared rationale 800-char bump
metadata:
  type: project
---

**✅ SHIPPED 2026-05-20 — Sprint 3-W: Skill-author bug fix**

Cleared all bugs surfaced by Sprint 3-V E2E + the golden-example schema validation harness. Ships the harness as permanent CI gate so the same class of bugs can't reappear.

## What was fixed

- **db-layout** — 14 examples migrated forward to the NEW canonical shape (`incoming_supply` + `main_switch` + `spare_ways`); schema updated; `drawn_as_symbols[]` relaxed to accept string OR object; `severity: 'high'` → `'warning'` in us-strip-mall-common-area; generator prompt gains explicit `jurisdiction` reminder.
- **earthing** — 2 examples migrated to existing 3-value `supply_bond_type` enum (`tn_c_s_pen` → `dno_pme_bond`; `utility_pen_bond` → `consumer_electrode_only` because TT systems have no utility bond by definition).
- **lighting-layout** — generator prompt gains field-name precision section: `zone_id` (NOT `id`), `circuit_id` on every luminaire, `initial_lumens` is integer.
- **shared/schemas/core/rationale.schema.json** — `definitions.Section.properties.summary.maxLength` 400 → 800 (one-line edit, propagates to 9 skills consuming the ref).
- **CI** — `scripts/validate-examples.py` + `.github/workflows/validate-examples.yml` run on every push + PR to main.

## Golden harness end-state

53/53 examples pass (was 36/53 baseline). CI gate prevents regressions.

## Stats

- 5 phases / 6 tasks / 5 atomic commits
- 14 file ops (2 new + 12 modifications)
- ~1 dev day execution (per design budget)

## How to apply

- Future skill author: every new skill MUST have its examples pass `python3 scripts/validate-examples.py` BEFORE PR — CI gate enforces this.
- Future schema migration: check the harness first. If examples drift behind schema, harness catches in 5 seconds.
- Class of bugs NOT caught by harness (prompt-vs-runtime): the LLM-vs-golden diff harness in Sprint 3-X will surface these.

## Cross-references

- [[runtime-project-boundary]] — skills repo ships contracts; runtime executes. This sprint's CI gate keeps the contract surface honest.
- [[small-power-shipped]] / [[cable-sizing-shipped]] / [[small-power-v1.1-shipped]] — recent skills that already comply with the harness
- [[feedback-no-haiku-sonnet-opus-only]] — followed throughout sprint
```

Then update `/Users/linus/.claude/projects/-Users-linus-Desktop-DraftsMan-SKills-draftsman-skills/memory/MEMORY.md` with a 1-line index entry. Match the existing line format:

```
- [Sprint 3-W shipped](sprint-3w-shipped.md) — 2026-05-20: skill-author bug fix + golden-example CI gate + 14 file ops; 53/53 examples pass; db-layout NEW shape; earthing enum migration; lighting-layout prompt precision; rationale 800-char bump
```

- [ ] **Step 6: Final summary report**

Report back:
- Status: DONE / DONE_WITH_CONCERNS / BLOCKED
- Push SHA range (e.g., `ec202cf..XXXXXXX`)
- Golden harness end-state (expected 53/53)
- Memory file path saved
- Sprint complete summary (1-2 sentences)

---

## Self-review checklist (run after writing this plan)

- [x] **Spec coverage:** Every section of the design spec maps to a task.
  - Spec §1 Decision 1 (full scope) → all 6 phases
  - Spec §1 Decision 2 (db-layout NEW shape) → Task 2 Steps 1-12
  - Spec §1 Decision 3 (earthing migration) → Task 3 Steps 1-6
  - Spec §1 Decision 4 (rationale maxLength bump) → Task 5
  - Spec §1 Decision 5 (CI gate) → Task 1
  - Spec §2 Phase A → Task 1
  - Spec §2 Phase B → Task 2
  - Spec §2 Phase C → Task 3
  - Spec §2 Phase D → Task 4
  - Spec §2 Phase E → Task 5
  - Spec §2 Phase F → Task 6
  - Spec §6 acceptance criteria — all 7 verified in Task 6 Steps 1-4
- [x] **Placeholder scan:** No "TBD"/"implement later"/"similar to". Full content for every step.
- [x] **Type consistency:** `incoming_supply`, `main_switch`, `spare_ways` field names spelled identically across schema (Task 2 Steps 3-4), 6 example migrations (Task 2 Steps 7-12), and prompt update (Task 2 Step 13). `supply_bond_type` enum values (`dno_pme_bond`, `consumer_electrode_only`) match in both example migrations (Task 3) and the schema reference (verified pre-plan). `Section.summary maxLength: 800` cited identically in Task 5 Step 2 + Task 5 Step 3 validation. Golden harness exit code semantics (0 = pass, 1 = any failure) consistent across Task 1 Step 2 + Task 6 Step 1.

---

**Plan complete and saved to `docs/superpowers/plans/2026-05-20-skill-author-bug-fix-sprint.md`.**

Two execution options:

1. **Subagent-Driven (recommended)** — Fresh subagent per task, two-stage review after each, continuous execution. Matches the proven pattern from cable-sizing v1.0 + small-power v1.1 sprints.

2. **Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints.

Which approach?
