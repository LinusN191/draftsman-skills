# Small-Power v1.1 Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate small-power from leaf (`consumes_intents: []`) to optional consumer of `cable-sizing` intent. When the intent is provided, resolve `verified_zs_ohm` per circuit and flip `tool_call_pending_for_zs_verification` to false. When absent, fall back to v1.0 deferral behaviour (zero churn to 4 existing examples).

**Architecture:** Hybrid intent consumption pattern matching SLD v1.4 multi-skill precedent. Schema bumps are additive (non-breaking): typed `meta.consumed_intents.items` + new optional `cable_sizing_node_id` field per circuit. Lookup uses implicit `f"{parent_db.designation}.{circuit_id}"` composition by default, with optional explicit override. Zs computation: `Zs = Ze + (r1_plus_r2 / 1000) × length + (reactance / 1000) × length`. 12 → 13 step generator, 10 → 11 INV validator, 6 → 7 D-check reviewer. 1 new worked example + 1 new eval covering v1.1 mode; 4 existing examples + 9 existing evals untouched.

**Tech Stack:** JSON Schema Draft-07 + YAML 1.2 + Markdown. No code — all artefacts are content (schema, prompts, example IR, eval YAML).

**Specs referenced:**
- Design: `docs/superpowers/specs/2026-05-20-small-power-v1.1-migration-design.md` (commit 2bb4195)

---

## Reference table — pre-flight verifications

| Verification | Result |
|---|---|
| small-power v1.0 generator step count | 12 (will become 13) |
| small-power v1.0 validator INV count | 10 (will become 11) |
| small-power v1.0 reviewer D count | 6 (will become 7) |
| small-power v1.0 schema has `verified_zs_ohm` (optional) | YES — semantic-only change in v1.1 |
| small-power v1.0 schema has `tool_call_pending_for_zs_verification` (default true) | YES |
| `meta.consumed_intents.items` currently typed | NO — just `{"type": "object"}` — v1.1 tightens to SLD v1.4 shape |
| Pattern parent: SLD v1.4 typed consumed_intents | `electrical/sld/schemas/sld-ir.schema.json` |
| Pattern parent: cable-sizing UK intent | `electrical/cable-sizing/examples/uk-domestic-final-circuits/intent-out.json` |
| Pattern parent: small-power UK 3-bed | `electrical/small-power/examples/uk-3bed-dwelling/output.json` |
| Net file ops | 5 new + 7 modifications = 12 |

---

## Phase A — Schema (Task 1)

### Task 1: Manifest + IR schema updates

**Model:** Opus (schema judgment — typed `consumed_intents.items` + optional `cable_sizing_node_id` placement under closed `additionalProperties: false`).

**Files:**
- Modify: `electrical/small-power/skill.manifest.json`
- Modify: `electrical/small-power/schemas/small-power-ir.schema.json`

- [ ] **Step 1: Read existing small-power manifest**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
cat electrical/small-power/skill.manifest.json | head -20
```

- [ ] **Step 2: Bump manifest version + add consumes_intents**

Use Edit to apply two changes to `electrical/small-power/skill.manifest.json`:

Change 1 (version):
- Find: `"version": "1.0.0",`
- Replace: `"version": "1.1.0",`

Change 2 (consumes_intents):
- Find: `"consumes_intents": [],`
- Replace: `"consumes_intents": ["cable-sizing"],`

No other manifest fields change.

- [ ] **Step 3: Validate manifest still parses + version + consumes_intents updated**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
python3 -c "
import json
m = json.load(open('electrical/small-power/skill.manifest.json'))
assert m['version'] == '1.1.0'
assert m['consumes_intents'] == ['cable-sizing']
assert m['produces_intent'] == 'small-power'
print('manifest OK: version=1.1.0, consumes_intents=[\"cable-sizing\"]')
"
```

Expected: `manifest OK: version=1.1.0, consumes_intents=["cable-sizing"]`

- [ ] **Step 4: Read SLD v1.4 consumed_intents.items shape for reference**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
python3 -c "
import json
s = json.load(open('electrical/sld/schemas/sld-ir.schema.json'))
ci = s['properties']['meta']['properties']['consumed_intents']
print(json.dumps(ci, indent=2))
"
```

- [ ] **Step 5: Read existing small-power IR consumed_intents shape**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
python3 -c "
import json
s = json.load(open('electrical/small-power/schemas/small-power-ir.schema.json'))
ci = s['properties']['meta']['properties']['consumed_intents']
print(json.dumps(ci, indent=2))
"
```

Expected current shape:
```json
{
  "type": "array",
  "items": { "type": "object" },
  "default": []
}
```

- [ ] **Step 6: Type meta.consumed_intents.items in IR schema**

Use Edit on `electrical/small-power/schemas/small-power-ir.schema.json`:

- Find:
```json
        "consumed_intents": { "type": "array", "items": { "type": "object" }, "default": [] }
```

- Replace:
```json
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
          },
          "default": []
        }
```

Preserve the trailing comma if the field is not the last in its containing object.

- [ ] **Step 7: Add optional cable_sizing_node_id field per circuit**

Use Edit on the same file. Locate the circuit-level `properties` block (under `properties.circuits.items.properties`). Find an existing optional string field on the circuit (e.g., `rcd_exception_citation`) to use as the anchor for the new field placement. Add `cable_sizing_node_id` immediately after `circuit_id`:

- Find:
```json
          "circuit_id":  { "type": "string", "pattern": "^C[0-9]{2}$" },
          "designation": { "type": "string" },
```

- Replace:
```json
          "circuit_id":  { "type": "string", "pattern": "^C[0-9]{2}$" },
          "cable_sizing_node_id": {
            "type": "string",
            "pattern": "^[A-Z0-9][A-Za-z0-9._-]*$",
            "description": "Optional explicit reference to a cable-sizing intent circuits[].node_id when consuming cable-sizing intent. When absent, v1.1 falls back to implicit composition f\"{parent_db.designation}.{circuit_id}\"."
          },
          "designation": { "type": "string" },
```

The `cable_sizing_node_id` field is NOT added to the circuit's `required` array — it stays optional.

- [ ] **Step 8: Validate schema parses + new fields present**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
python3 -c "
import json, jsonschema
s = json.load(open('electrical/small-power/schemas/small-power-ir.schema.json'))
jsonschema.Draft7Validator.check_schema(s)
print('IR schema: valid Draft-07')

ci = s['properties']['meta']['properties']['consumed_intents']
items = ci['items']
assert items['required'] == ['intent_type', 'intent_version', 'produced_by']
assert items['additionalProperties'] == False
assert items['properties']['intent_type']['pattern'] == '^[a-z][a-z0-9-]*\$'
print('consumed_intents.items typed correctly')

c = s['properties']['circuits']['items']['properties']
assert 'cable_sizing_node_id' in c
assert c['cable_sizing_node_id']['type'] == 'string'
assert c['cable_sizing_node_id']['pattern'] == '^[A-Z0-9][A-Za-z0-9._-]*\$'
# cable_sizing_node_id NOT in required
assert 'cable_sizing_node_id' not in s['properties']['circuits']['items']['required']
print('cable_sizing_node_id field added (optional)')

# v1.0 examples still validate against v1.1 schema
import os
for ex in ['uk-3bed-dwelling', 'ke-nairobi-small-office', 'intl-open-plan-floor', 'us-residential-dwelling']:
    out_path = f'electrical/small-power/examples/{ex}/output.json'
    if not os.path.exists(out_path):
        continue
    out = json.load(open(out_path))
    # Inline rationale ref bypass to test structure
    import copy
    s_test = copy.deepcopy(s)
    s_test['properties']['rationale'] = {'type': 'object'}
    try:
        jsonschema.validate(out, s_test)
        print(f'{ex}: still validates against v1.1 schema')
    except jsonschema.ValidationError as e:
        print(f'{ex}: VALIDATION ERROR — {e.message[:150]}')
        raise
"
```

Expected: all 4 v1.0 examples still validate against v1.1 schema (additive change is non-breaking).

- [ ] **Step 9: Commit**

```bash
git add electrical/small-power/skill.manifest.json electrical/small-power/schemas/small-power-ir.schema.json
git commit -m "feat(small-power): v1.1 schema — typed consumed_intents.items + optional cable_sizing_node_id field per circuit"
```

---

## Phase B — Prompts (Task 2)

### Task 2: Generator + Validator + Reviewer (3 files bundled)

**Model:** Opus (engineering reasoning — new Step 12 Zs resolution logic + INV-11 lookup integrity + D-7 provenance audit).

**Files:**
- Modify: `electrical/small-power/prompts/generator.md`
- Modify: `electrical/small-power/prompts/validator.md`
- Modify: `electrical/small-power/prompts/reviewer.md`

- [ ] **Step 1: Read current generator step structure**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
grep -nE "^### Step [0-9]+" electrical/small-power/prompts/generator.md
```

Expected: 12 step headings, numbered Step 1 through Step 12.

- [ ] **Step 2: Insert new Step 12 in generator (Zs resolution from cable-sizing intent)**

Use Edit on `electrical/small-power/prompts/generator.md`. Locate the existing `### Step 12 — Emit rationale block` heading. We need to insert a new Step 12 BEFORE it and renumber the existing step 12 to Step 13.

First, renumber existing Step 12 → Step 13:
- Find: `### Step 12 — Emit rationale block`
- Replace: `### Step 13 — Emit rationale block`

If the heading uses slightly different wording (e.g., `### Step 12 — Emit rationale (WI2)` or `### Step 12 — Final: Emit rationale block`), use Read first to find the exact text and adjust the find/replace accordingly. The heading prefix must remain `### Step 12 —` BEFORE the rename and `### Step 13 —` after.

Then insert the new Step 12 block immediately BEFORE the renamed Step 13 heading.

Find the location: it should be just before the renamed Step 13 heading. Use a unique anchor — the last few lines of Step 11 content (which is the previous step before Step 12).

The new Step 12 content to insert:

```markdown
### Step 12 — Resolve Zs from cable-sizing intent (v1.1, hybrid)

If the skill's input declares a consumed `cable-sizing` intent path, resolve every circuit's `verified_zs_ohm` using the intent. This is v1.1 hybrid behaviour: optional consumption, with v1.0 deferral fallback when intent is absent.

**12.1 Detect intent presence.** Check `meta.consumed_intents[]` for an entry with `intent_type == "cable-sizing"`. If absent:
- Leave `verified_zs_ohm` absent on every circuit
- Keep `tool_call_pending_for_zs_verification: true` on every circuit
- Keep `TOOL-CALL-PENDING:calc.zs_loop_impedance` in `flags[]`
- Skip 12.2 / 12.3 / 12.4
- Document in rationale §6 (Diversity + Zs): "Zs deferred per WI3 — no cable-sizing intent consumed"

**12.2 Load the intent.** Read the cable-sizing intent JSON from the path declared in the runtime's consumed-intent contract. The intent shape is defined by `electrical/cable-sizing/schemas/cable-sizing-intent.schema.json` — it carries `circuits[]` with per-circuit `node_id`, `length_m`, `r1_plus_r2_milliohm_per_m_at_operating_temp`, and `reactance_milliohm_per_m`.

**12.3 Resolve per-circuit Zs.** For each small-power `circuit` `c`:

1. **Determine lookup key:**
   - If `c.cable_sizing_node_id` is set, use it as the lookup key (explicit override)
   - Else compose `lookup_key = f"{parent_db.designation}.{circuit_id}"` (implicit default — e.g., `"CU-MAIN.C01"`)
2. **Find matching cable-sizing circuit:** Search `cable_sizing_intent.circuits[]` for the entry where `node_id == lookup_key`.
3. **If found:**
   - Read `length_m`, `r1_plus_r2_milliohm_per_m_at_operating_temp`, `reactance_milliohm_per_m` from that intent circuit
   - Compute `Zs_segment_ohm = (r1_plus_r2 / 1000) × length + (reactance / 1000) × length` (mΩ/m → Ω/m)
   - Compute `verified_zs_ohm = supply_origin.ze_declared_ohm + Zs_segment_ohm`
   - Set `c.verified_zs_ohm` to the computed value
   - Set `c.tool_call_pending_for_zs_verification: false`
4. **If NOT found:** Hard fail — emit a non_compliance_flag with severity=critical naming the unresolved `lookup_key` and the source (explicit or implicit). Do NOT silently fall back to deferral mode. The validator's INV-11 will catch this and block `valid: true`.

**12.4 Drop the pending flag if ALL circuits resolved.** If all circuits in step 12.3 successfully resolved without hard-fail, remove `TOOL-CALL-PENDING:calc.zs_loop_impedance` from `flags[]`. If any circuit hard-failed, the flag stays (since the deferral is not actually resolved for that circuit).

**12.5 Record consumed_intent in meta.** Append to `meta.consumed_intents[]`:
```json
{
  "intent_type": "cable-sizing",
  "intent_version": "1.0.0",
  "produced_by": "electrical/cable-sizing"
}
```
(`intent_version` reflects the actual cable-sizing intent semver read from its `intent_version` field; default `"1.0.0"` if absent in the source intent.)

```

After the insertion, the prompt has 13 numbered Step headings: Steps 1-11 unchanged, new Step 12 (Zs resolution), renamed Step 13 (rationale block).

- [ ] **Step 3: Update generator's "How You Think Before Acting" header step count + WI3 wording**

The generator's H2 section "How You Think Before Acting" (or equivalent) lists the steps as a numbered table or summary. If such a summary exists (Read first to confirm), update it to reflect 13 steps instead of 12. Common phrasings to check:

- "12-step" → "13-step"
- "12 internal steps" → "13 internal steps"

Search and replace:
```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
grep -n '12-step\|12 internal\|12 steps' electrical/small-power/prompts/generator.md
```

For each match, use Edit to update the count. If no matches (the summary doesn't quantify step count), skip.

- [ ] **Step 4: Update generator rationale section guidance for Zs provenance**

Locate the §6 "Diversity + Zs" sub-section in the rationale block guidance (now Step 13). Add one sentence covering Zs provenance:

- Find the existing line containing "Diversity + Zs":
```
6. **Diversity + Zs** — diversified_max_load_a estimates per IET OSG App A; calc.zs_loop_impedance pending per WI3
```
(Exact text may differ — Read first.)

- Replace with:
```
6. **Diversity + Zs** — diversified_max_load_a estimates per IET OSG App A; Zs resolution provenance: when cable-sizing intent is consumed (v1.1 hybrid mode), `verified_zs_ohm` is computed per circuit from `Ze + r1+r2 × length + reactance × length` and `tool_call_pending_for_zs_verification` is flipped to false; when intent absent, the v1.0 deferral pattern holds and `TOOL-CALL-PENDING:calc.zs_loop_impedance` remains in `flags[]`
```

- [ ] **Step 5: Verify generator now has 13 steps**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
grep -cE "^### Step [0-9]+" electrical/small-power/prompts/generator.md
grep -nE "^### Step 12|^### Step 13" electrical/small-power/prompts/generator.md
```

Expected: count = 13. Step 12 = "Resolve Zs from cable-sizing intent (v1.1, hybrid)". Step 13 = "Emit rationale block".

- [ ] **Step 6: Add INV-11 to validator**

Read the existing validator structure first to find the right insertion point:

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
grep -nE "^### INV-|^## INV-" electrical/small-power/prompts/validator.md
```

Locate INV-10 (the last existing check). Add INV-11 immediately after INV-10's full block (before the `valid: true` gate paragraph if there is one).

The INV-11 content to insert:

```markdown
### INV-11: Cable-Sizing Intent Lookup Integrity (v1.1)

**Rule:** When `meta.consumed_intents[]` contains an entry with `intent_type == "cable-sizing"`, every small-power circuit MUST successfully resolve its cable-sizing intent counterpart. The lookup key is `c.cable_sizing_node_id` (explicit override, when set) or `f"{parent_db.designation}.{circuit_id}"` (implicit composition default). A lookup that finds no matching `cable-sizing.circuits[].node_id` is a hard fail.

This rule is only triggered when the cable-sizing intent is actively consumed. When the intent is absent (v1.0 fallback mode), INV-11 is a no-op — the v1.0 INV checks (INV-01 through INV-10) carry full enforcement.

**Severity:** Hard fail.

**Fail message format:**

```
INV-11: small-power circuit <CIRCUIT_ID> cable-sizing intent lookup failed.
Lookup key: <KEY> (source: <explicit cable_sizing_node_id | implicit composition from parent_db.designation + circuit_id>)
No matching cable-sizing.circuits[].node_id == <KEY> found in consumed intent.
Fix: either correct parent_db.designation + circuit_id so they compose the expected node_id, or set an explicit cable_sizing_node_id on this circuit.
```

If the `valid: true` gate paragraph exists at the end of the validator file (e.g., "valid: true requires INV-01 through INV-10 all pass"), update it to "INV-01 through INV-11 all pass (no hard fails)".
```

After insertion, the validator has 11 INV checks (INV-01 through INV-11).

- [ ] **Step 7: Verify validator now has 11 INV checks**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
grep -cE "^### INV-|^## INV-" electrical/small-power/prompts/validator.md
```

Expected: count = 11. Confirm INV-11 heading reads "Cable-Sizing Intent Lookup Integrity (v1.1)".

- [ ] **Step 8: Add D-7 to reviewer**

Read the existing reviewer structure first:

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
grep -nE "^### D-|^## D-" electrical/small-power/prompts/reviewer.md
```

Locate D-6 (the last existing check). Add D-7 immediately after D-6's full block.

The D-7 content to insert:

```markdown
### D-7 — Zs Resolution Provenance Audit (v1.1)

**Question:** Is the Zs resolution state consistent across all circuits? In v1.1 hybrid mode the answer must be uniform — either every circuit resolved from cable-sizing intent, or every circuit deferred (no mixed states).

**Look for:**

When `meta.consumed_intents[]` contains a `cable-sizing` entry:
- Every circuit has `verified_zs_ohm` populated and > 0
- Every circuit has `tool_call_pending_for_zs_verification == false`
- `TOOL-CALL-PENDING:calc.zs_loop_impedance` is NOT in `flags[]`
- Rationale §6 (Diversity + Zs) narrates the resolution

When `meta.consumed_intents[]` does NOT contain a `cable-sizing` entry:
- Every circuit has `verified_zs_ohm` absent
- Every circuit has `tool_call_pending_for_zs_verification == true`
- `TOOL-CALL-PENDING:calc.zs_loop_impedance` IS in `flags[]`
- Rationale §6 documents the v1.0 deferral path

**Flag when:** Mixed states detected — e.g., some circuits resolved while others deferred, without engineer-documented justification in `assumptions[]`. Also flag if the cable-sizing intent is consumed but the TOOL-CALL-PENDING flag was not dropped from `flags[]` (book-keeping leak).
```

After insertion, the reviewer has 7 D-checks (D-1 through D-7).

- [ ] **Step 9: Verify reviewer now has 7 D-checks**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
grep -cE "^### D-|^## D-" electrical/small-power/prompts/reviewer.md
```

Expected: count = 7. Confirm D-7 heading reads "Zs Resolution Provenance Audit (v1.1)".

- [ ] **Step 10: Commit**

```bash
git add electrical/small-power/prompts/
git commit -m "feat(small-power): v1.1 prompts — Step 12 Zs resolution + INV-11 lookup integrity + D-7 provenance audit"
```

---

## Phase C — New worked example (Task 3)

### Task 3: uk-3bed-with-cable-sizing/ example (5 files)

**Model:** Opus (Zs calculation correctness across 5 circuits; matches small-power UK 3-bed scenario + cable-sizing UK domestic intent anchor values).

**Files (all 5 new under `electrical/small-power/examples/uk-3bed-with-cable-sizing/`):**
- Create: `input.json`
- Create: `consumed-cable-sizing-intent.json`
- Create: `output.json`
- Create: `intent-out.json`
- Create: `reasoning.md`

- [ ] **Step 1: Verify directory does not exist (fresh example)**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
ls electrical/small-power/examples/uk-3bed-with-cable-sizing/ 2>/dev/null || mkdir -p electrical/small-power/examples/uk-3bed-with-cable-sizing
```

If a stub from an earlier sprint exists, OVERWRITE files. The new example is a v1.1-only addition; v1.0 `uk-3bed-dwelling/` stays untouched.

- [ ] **Step 2: Write input.json**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
```

Use Write to create `electrical/small-power/examples/uk-3bed-with-cable-sizing/input.json`:

```json
{
  "project_id": "uk-3bed-with-cable-sizing-eg01",
  "jurisdiction": "GB",
  "site_brief": "Same UK 3-bed dwelling scenario as uk-3bed-dwelling, but with cable-sizing intent now consumed in v1.1 hybrid mode. Demonstrates Zs resolution from cable-sizing intent's r1_plus_r2 + reactance + length per circuit, replacing the v1.0 calc.zs_loop_impedance deferral.",
  "supply": {
    "voltage_v": 230,
    "phase_arrangement": "single_phase",
    "system_type": "TN-C-S",
    "ze_declared_ohm": 0.35,
    "psc_declared_ka": 6.0
  },
  "parent_db": {
    "designation": "CU-MAIN",
    "pfc_at_busbar_ka": 6.0
  },
  "room_briefs": [
    {"room_id": "kitchen",   "room_type": "kitchen_domestic", "dimensions_m": {"length": 4.5, "width": 3.5, "height": 2.4}, "special_location": null,             "anticipated_loads_kw": 4.5, "socket_count_target": 6},
    {"room_id": "utility",   "room_type": "utility_domestic", "dimensions_m": {"length": 2.5, "width": 2.0, "height": 2.4}, "special_location": null,             "anticipated_loads_kw": 3.0, "socket_count_target": 3},
    {"room_id": "dining",    "room_type": "dining_domestic",  "dimensions_m": {"length": 3.5, "width": 3.0, "height": 2.4}, "special_location": null,             "anticipated_loads_kw": 1.0, "socket_count_target": 4},
    {"room_id": "lounge",    "room_type": "lounge_domestic",  "dimensions_m": {"length": 5.0, "width": 4.0, "height": 2.4}, "special_location": null,             "anticipated_loads_kw": 1.5, "socket_count_target": 6},
    {"room_id": "bedroom-1", "room_type": "bedroom_domestic", "dimensions_m": {"length": 4.0, "width": 3.5, "height": 2.4}, "special_location": null,             "anticipated_loads_kw": 0.8, "socket_count_target": 4},
    {"room_id": "bedroom-2", "room_type": "bedroom_domestic", "dimensions_m": {"length": 3.5, "width": 3.0, "height": 2.4}, "special_location": null,             "anticipated_loads_kw": 0.6, "socket_count_target": 3},
    {"room_id": "bedroom-3", "room_type": "bedroom_domestic", "dimensions_m": {"length": 3.0, "width": 2.5, "height": 2.4}, "special_location": null,             "anticipated_loads_kw": 0.6, "socket_count_target": 3},
    {"room_id": "bathroom",  "room_type": "bathroom_domestic","dimensions_m": {"length": 2.5, "width": 2.0, "height": 2.4}, "special_location": "bathroom_zone_3","anticipated_loads_kw": 0.5, "socket_count_target": 1}
  ],
  "design_intent": {
    "preferred_topology": "auto_by_jurisdiction",
    "drawing_standard": "BS 1192:2007+A2:2016",
    "sheet_size": "A1",
    "drawing_scale": "1:50"
  },
  "consumed_intents_paths": {
    "cable-sizing": "electrical/small-power/examples/uk-3bed-with-cable-sizing/consumed-cable-sizing-intent.json"
  }
}
```

- [ ] **Step 3: Write consumed-cable-sizing-intent.json (synthetic)**

Use Write to create `electrical/small-power/examples/uk-3bed-with-cable-sizing/consumed-cable-sizing-intent.json`. Values match cable-sizing v1.0 UK domestic example anchor data (BS 7671 App 4 Tables 4F1-4F3 for r1+r2 + reactance at 70°C PVC Cu):

```json
{
  "project_id": "uk-3bed-with-cable-sizing-eg01",
  "intent_version": "1.0.0",
  "circuits": [
    {
      "node_id": "CU-MAIN.C01",
      "parent_node_id": "CU-MAIN",
      "designation": "Ground-floor ring final circuit",
      "phase_csa_mm2_or_awg": "2.5",
      "cpc_csa_mm2_or_awg": "1.5",
      "material": "copper",
      "insulation": "pvc_70",
      "cable_type": "pvc_singles",
      "parallel_count": 1,
      "cable_od_mm": 8.4,
      "weight_kg_per_m": 0.18,
      "length_m": 32,
      "installation_method": "B1",
      "r1_plus_r2_milliohm_per_m_at_operating_temp": 18.1,
      "reactance_milliohm_per_m": 0.08
    },
    {
      "node_id": "CU-MAIN.C02",
      "parent_node_id": "CU-MAIN",
      "designation": "First-floor ring final circuit",
      "phase_csa_mm2_or_awg": "2.5",
      "cpc_csa_mm2_or_awg": "1.5",
      "material": "copper",
      "insulation": "pvc_70",
      "cable_type": "pvc_singles",
      "parallel_count": 1,
      "cable_od_mm": 8.4,
      "weight_kg_per_m": 0.18,
      "length_m": 28,
      "installation_method": "B1",
      "r1_plus_r2_milliohm_per_m_at_operating_temp": 18.1,
      "reactance_milliohm_per_m": 0.08
    },
    {
      "node_id": "CU-MAIN.C03",
      "parent_node_id": "CU-MAIN",
      "designation": "Cooker dedicated radial",
      "phase_csa_mm2_or_awg": "6",
      "cpc_csa_mm2_or_awg": "2.5",
      "material": "copper",
      "insulation": "pvc_70",
      "cable_type": "pvc_singles",
      "parallel_count": 1,
      "cable_od_mm": 10.6,
      "weight_kg_per_m": 0.34,
      "length_m": 8,
      "installation_method": "C",
      "r1_plus_r2_milliohm_per_m_at_operating_temp": 7.95,
      "reactance_milliohm_per_m": 0.08
    },
    {
      "node_id": "CU-MAIN.C04",
      "parent_node_id": "CU-MAIN",
      "designation": "Immersion heater dedicated radial",
      "phase_csa_mm2_or_awg": "2.5",
      "cpc_csa_mm2_or_awg": "1.5",
      "material": "copper",
      "insulation": "pvc_70",
      "cable_type": "pvc_singles",
      "parallel_count": 1,
      "cable_od_mm": 8.4,
      "weight_kg_per_m": 0.18,
      "length_m": 4,
      "installation_method": "C",
      "r1_plus_r2_milliohm_per_m_at_operating_temp": 18.1,
      "reactance_milliohm_per_m": 0.08
    },
    {
      "node_id": "CU-MAIN.C05",
      "parent_node_id": "CU-MAIN",
      "designation": "Bathroom shaver supply (BS EN 61558-2-5)",
      "phase_csa_mm2_or_awg": "1.5",
      "cpc_csa_mm2_or_awg": "1.0",
      "material": "copper",
      "insulation": "pvc_70",
      "cable_type": "pvc_singles",
      "parallel_count": 1,
      "cable_od_mm": 7.2,
      "weight_kg_per_m": 0.13,
      "length_m": 3,
      "installation_method": "C",
      "r1_plus_r2_milliohm_per_m_at_operating_temp": 30.3,
      "reactance_milliohm_per_m": 0.10
    }
  ]
}
```

- [ ] **Step 4: Validate the consumed-cable-sizing-intent.json against cable-sizing intent schema**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
python3 -c "
import json, jsonschema
schema = json.load(open('electrical/cable-sizing/schemas/cable-sizing-intent.schema.json'))
intent = json.load(open('electrical/small-power/examples/uk-3bed-with-cable-sizing/consumed-cable-sizing-intent.json'))
jsonschema.validate(intent, schema)
print('consumed-cable-sizing-intent: VALID against cable-sizing-intent schema')
assert len(intent['circuits']) == 5
print(f'circuits: {[c[\"node_id\"] for c in intent[\"circuits\"]]}')
"
```

Expected: VALID + 5 circuits with node_ids `CU-MAIN.C01..C05`.

- [ ] **Step 5: Pre-compute the 5 expected verified_zs_ohm values**

Reference computation (paste into a scratch Python check):

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
python3 -c "
ze = 0.35  # supply_origin.ze_declared_ohm
circuits = [
    ('C01', 32, 18.1, 0.08),
    ('C02', 28, 18.1, 0.08),
    ('C03',  8,  7.95, 0.08),
    ('C04',  4, 18.1, 0.08),
    ('C05',  3, 30.3, 0.10),
]
print(f'{\"id\":<5}{\"L\":<6}{\"r1+r2\":<8}{\"X\":<6}{\"Zs_seg\":<10}{\"Zs\":<8}')
for cid, L, r1r2, X in circuits:
    Zs_seg = (r1r2 / 1000) * L + (X / 1000) * L
    Zs = ze + Zs_seg
    print(f'{cid:<5}{L:<6}{r1r2:<8}{X:<6}{Zs_seg:.4f}    {Zs:.4f}')
"
```

Expected output (these are the verified_zs_ohm values that will appear in output.json):
```
id   L     r1+r2   X     Zs_seg    Zs
C01  32    18.1    0.08  0.5818    0.9318
C02  28    18.1    0.08  0.5091    0.8591
C03  8     7.95    0.08  0.0642    0.4142
C04  4     18.1    0.08  0.0727    0.4227
C05  3     30.3    0.1   0.0912    0.4412
```

Round to 4 decimal places for output.json. These match the spec §8.2 expected values (rounded to 2 dp in the spec: 0.93, 0.86, 0.41, 0.42, 0.44).

- [ ] **Step 6: Read existing uk-3bed-dwelling/output.json for structural reference**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
python3 -c "
import json
o = json.load(open('electrical/small-power/examples/uk-3bed-dwelling/output.json'))
print('top-level keys:', list(o.keys()))
print('meta keys:', list(o['meta'].keys()))
print('circuit count:', len(o['circuits']))
print('room count:', len(o['rooms']))
print('flags:', o['flags'])
print('rationale sections:', [s['title'] for s in o['rationale']['sections']])
"
```

- [ ] **Step 7: Write output.json (full v1.1 IR with resolved Zs)**

Use Write to create `electrical/small-power/examples/uk-3bed-with-cable-sizing/output.json`. The IR is a v1.1 version of the existing uk-3bed-dwelling output, with these v1.1-specific changes:

**Key differences from v1.0 uk-3bed-dwelling output:**

1. `meta.consumed_intents` is populated:
```json
"consumed_intents": [
  {
    "intent_type": "cable-sizing",
    "intent_version": "1.0.0",
    "produced_by": "electrical/cable-sizing"
  }
]
```

2. Each of the 5 circuits has:
   - `verified_zs_ohm` populated with the computed value (4 dp): 0.9318, 0.8591, 0.4142, 0.4227, 0.4412
   - `tool_call_pending_for_zs_verification: false`

3. `flags[]` does NOT contain `TOOL-CALL-PENDING:calc.zs_loop_impedance` (resolved). Other flags from v1.0 uk-3bed-dwelling unchanged.

4. `compliance_summary.assumptions[]` adds:
```
"Zs resolved from consumed cable-sizing intent (electrical/cable-sizing v1.0.0) — verified_zs_ohm per circuit computed from Ze + (r1_plus_r2 / 1000) × length_m + (reactance / 1000) × length_m. v1.1 hybrid consumption mode (cable-sizing intent present)."
```

5. `rationale.chat_summary` is updated to mention v1.1 Zs resolution explicitly. Stay within 40-500 char limit. Example:

```
"UK 3-bed dwelling, TN-C-S 230V, Ze=0.35Ω, PSCC=6kA. small-power v1.1 hybrid consumption of cable-sizing intent — 5 circuits with verified_zs_ohm resolved (range 0.41-0.93Ω, all within Zs_max for 32A type-B MCB per BS 7671:2018+A2:2022 Table 41.3). 2 ring finals + 3 dedicated radials. Bathroom zone_3 SSU only. All RCD type-A 30mA. calc.zs_loop_impedance deferral cleared by intent consumption."
```

6. `rationale.sections[5]` (Diversity + Zs, 0-indexed = index 5) — narrative updated to cite Zs resolution per the new Step 12 guidance.

All other content (circuits topologies, OCPDs, rooms, sockets, drawing_layout, etc.) mirrors the v1.0 uk-3bed-dwelling example. The full IR is large (~500 lines). To minimise drift, the implementer should:

(a) Read `electrical/small-power/examples/uk-3bed-dwelling/output.json` in full.
(b) Copy it to the new location.
(c) Apply the 6 changes above.

Concrete edit sequence using Read + Write:

```bash
# Step 7a: Copy v1.0 output as starting point
cp electrical/small-power/examples/uk-3bed-dwelling/output.json electrical/small-power/examples/uk-3bed-with-cable-sizing/output.json
```

Then use Edit on the new file to apply the 6 changes:

Edit 1 — Populate `meta.consumed_intents`:
- Find: `"consumed_intents": []`
- Replace:
```json
"consumed_intents": [
      {
        "intent_type": "cable-sizing",
        "intent_version": "1.0.0",
        "produced_by": "electrical/cable-sizing"
      }
    ]
```

Edit 2-6 — Per circuit, find the existing `"tool_call_pending_for_zs_verification": true` AND populate the `verified_zs_ohm` field. The exact format depends on whether the v1.0 example has `verified_zs_ohm` already present (as null/absent) or not. Use Read first to see the per-circuit structure, then for each of C01-C05 use Edit to set both fields. Example for C01:

If the v1.0 has `"tool_call_pending_for_zs_verification": true` and no `verified_zs_ohm` key:
- Find (in C01's circuit object):
```json
        "tool_call_pending_for_zs_verification": true,
```
- Replace:
```json
        "tool_call_pending_for_zs_verification": false,
        "verified_zs_ohm": 0.9318,
```

Repeat for C02 (0.8591), C03 (0.4142), C04 (0.4227), C05 (0.4412). Make each Edit precise to the specific circuit's surrounding context (e.g., include the line above and below to disambiguate).

Edit 7 — Remove TOOL-CALL-PENDING from flags. Find the flags array entry:
- Find: `"TOOL-CALL-PENDING:calc.zs_loop_impedance",` (with surrounding comma)
- Replace: (empty string, removing the entry — be careful with the JSON array structure; the easiest is to make this a precise find that captures the full line including the trailing newline OR remove just the value if it's the last array entry)

Edit 8 — Add Zs resolution assumption:
- Find the `"assumptions": [` array opening
- Insert as the FIRST entry:
```json
      "Zs resolved from consumed cable-sizing intent (electrical/cable-sizing v1.0.0) — verified_zs_ohm per circuit computed from Ze + (r1_plus_r2 / 1000) × length_m + (reactance / 1000) × length_m. v1.1 hybrid consumption mode (cable-sizing intent present).",
```

Edit 9 — Update rationale.chat_summary to the v1.1 string shown above.

Edit 10 — Update rationale.sections[5].summary (Diversity + Zs) to mention v1.1 resolution. Keep summary ≤ 400 chars.

- [ ] **Step 8: Write intent-out.json (small-power intent — shape unchanged from v1.0)**

```bash
cp electrical/small-power/examples/uk-3bed-dwelling/intent-out.json electrical/small-power/examples/uk-3bed-with-cable-sizing/intent-out.json
```

Then update `project_id` field:

- Find: `"project_id": "uk-3bed-dwelling-eg01"` (or whatever the v1.0 example uses)
- Replace: `"project_id": "uk-3bed-with-cable-sizing-eg01"`

No other field changes. The small-power intent shape is unchanged in v1.1 — downstream consumers see the same contract.

- [ ] **Step 9: Write reasoning.md**

Use Write to create `electrical/small-power/examples/uk-3bed-with-cable-sizing/reasoning.md`. 8 H2 sections matching rationale.sections[] titles. Section 6 (Diversity + Zs) is the focus — it narrates the v1.1 Zs resolution.

Section 6 template (~50 lines):

```markdown
## Diversity + Zs

### Diversity factors

Per IET On-Site Guide Appendix A Table A1: socket-outlet circuits use 40% diversity on the sum of OCPD ratings, plus 5A per socket. For this dwelling:

- C01 ring (kitchen + utility + dining + lounge, ~19 sockets): diversified_max_load_a ≈ 16 A
- C02 ring (3 bedrooms, ~10 sockets): diversified_max_load_a ≈ 6.5 A
- C03 cooker: first 10 A at 100% + 30% of remainder (22 A − 10 A = 12 A × 0.3 = 3.6 A) + 5 A per cooker socket → 18.6 A
- C04 immersion: 100% (continuous load, not diversified)
- C05 shaver SSU: trivial diversification not applied

### Zs resolution (v1.1 mode — cable-sizing intent consumed)

This is a small-power v1.1 example demonstrating the migration target documented in `docs/superpowers/specs/2026-05-20-cable-sizing-skill-design-refresh.md §2`. The cable-sizing intent at `consumed-cable-sizing-intent.json` carries per-circuit `r1_plus_r2_milliohm_per_m_at_operating_temp` + `reactance_milliohm_per_m` + `length_m` — small-power v1.1's Step 12 uses these to resolve Zs.

**Lookup mechanic.** For each small-power circuit, the lookup key is `f"{parent_db.designation}.{circuit_id}"` — here `"CU-MAIN.C01"` through `"CU-MAIN.C05"`. The cable-sizing intent's `circuits[].node_id` matches these implicit keys directly. No `cable_sizing_node_id` explicit overrides are required for this example.

**Computation.** Per circuit:

```
verified_zs_ohm = Ze + (r1_plus_r2 / 1000) × length_m + (reactance / 1000) × length_m
```

Ze comes from `supply_origin.ze_declared_ohm` (0.35 Ω for this TN-C-S installation). The /1000 converts mΩ/m → Ω/m. Results:

| circuit_id | length (m) | r1+r2 (mΩ/m) | reactance (mΩ/m) | Zs_segment (Ω) | Zs total (Ω) | OCPD Zs_max (Ω) |
|---|---|---|---|---|---|---|
| C01 | 32 | 18.1 | 0.08 | 0.5818 | 0.9318 | 1.44 (32A Type-B MCB, 0.4s ADS) |
| C02 | 28 | 18.1 | 0.08 | 0.5091 | 0.8591 | 1.44 |
| C03 | 8  | 7.95 | 0.08 | 0.0642 | 0.4142 | 1.44 |
| C04 | 4  | 18.1 | 0.08 | 0.0727 | 0.4227 | 2.87 (16A Type-B MCB, 5s ADS) |
| C05 | 3  | 30.3 | 0.10 | 0.0912 | 0.4412 | 7.68 (6A Type-B MCB, 5s ADS) |

All Zs values are well within Zs_max for their OCPD per BS 7671:2018+A2:2022 Table 41.3 (Type-B MCBs at 230V, with 0.4s ADS for socket-outlet circuits ≤ 32 A per Reg 411.3.2.2 and 5s for fixed-equipment circuits per Reg 411.3.2.3).

**Provenance.** The resolution is recorded in:
- `meta.consumed_intents[]` — declares the cable-sizing intent at `intent_type: "cable-sizing", intent_version: "1.0.0", produced_by: "electrical/cable-sizing"`
- Per-circuit `verified_zs_ohm` populated, `tool_call_pending_for_zs_verification: false`
- `TOOL-CALL-PENDING:calc.zs_loop_impedance` flag dropped from `flags[]` (compare with the v1.0 `uk-3bed-dwelling` example which retains the flag — that example demonstrates the hybrid fallback path)

**Comparison with v1.0 fallback.** The companion v1.0 example `electrical/small-power/examples/uk-3bed-dwelling/` is the same dwelling scenario without intent consumption. In that example, `verified_zs_ohm` is absent on every circuit, `tool_call_pending_for_zs_verification: true`, and the TOOL-CALL-PENDING flag is retained — the engineer would resolve Zs later when calc.zs_loop_impedance ships (WI3 deferral). v1.1 hybrid mode is non-breaking: small-power runs either way.
```

The other 7 rationale sections (Jurisdiction + Supply, Circuit Topology, Special Locations, RCD Posture, OCPD + Cable, Compliance + Assumptions, Drafting References) mirror the v1.0 `uk-3bed-dwelling/reasoning.md` content closely — copy from there and adjust the project_id reference. Aim for total ~210-250 lines.

- [ ] **Step 10: Validate the new example IR against v1.1 schema + check Zs values**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
python3 << 'PY'
import json, jsonschema, copy
schema = json.load(open('electrical/small-power/schemas/small-power-ir.schema.json'))
o = json.load(open('electrical/small-power/examples/uk-3bed-with-cable-sizing/output.json'))
i = json.load(open('electrical/small-power/examples/uk-3bed-with-cable-sizing/intent-out.json'))

# Inline rationale to bypass RefResolver
s_test = copy.deepcopy(schema)
s_test['properties']['rationale'] = {'type': 'object', 'required': ['chat_summary', 'sections']}
jsonschema.validate(o, s_test)
print('output.json: VALID against v1.1 IR schema')

# Check consumed_intents
ci = o['meta']['consumed_intents']
assert len(ci) == 1
assert ci[0]['intent_type'] == 'cable-sizing'
assert ci[0]['intent_version'] == '1.0.0'
assert ci[0]['produced_by'] == 'electrical/cable-sizing'
print('meta.consumed_intents: OK')

# Check every circuit has verified_zs_ohm + tool_call_pending=false
expected_zs = {'C01': 0.9318, 'C02': 0.8591, 'C03': 0.4142, 'C04': 0.4227, 'C05': 0.4412}
for c in o['circuits']:
    cid = c['circuit_id']
    assert c.get('verified_zs_ohm') is not None, f'{cid}: verified_zs_ohm missing'
    assert c['tool_call_pending_for_zs_verification'] == False, f'{cid}: tool_call_pending should be false'
    assert abs(c['verified_zs_ohm'] - expected_zs[cid]) < 0.001, f'{cid}: Zs {c["verified_zs_ohm"]} vs expected {expected_zs[cid]}'
    print(f'  {cid}: verified_zs_ohm={c["verified_zs_ohm"]} (expected {expected_zs[cid]}) ✓')

# Flag dropped
assert 'TOOL-CALL-PENDING:calc.zs_loop_impedance' not in o.get('flags', [])
print('TOOL-CALL-PENDING flag dropped: OK')

# chat_summary
cs = o['rationale']['chat_summary']
print(f'chat_summary length: {len(cs)}')
assert 40 <= len(cs) <= 500

# section count + summaries
assert len(o['rationale']['sections']) == 8
for s in o['rationale']['sections']:
    assert len(s['summary']) <= 400

print()
print('=== Task 3 example validation: ALL PASS ===')
PY
```

Expected: all assertions pass + 5 Zs values match within 0.001 Ω.

- [ ] **Step 11: Commit**

```bash
git add electrical/small-power/examples/uk-3bed-with-cable-sizing/
git commit -m "feat(small-power): v1.1 new example uk-3bed-with-cable-sizing — 5 circuits with resolved verified_zs_ohm from cable-sizing intent"
```

---

## Phase D — Eval + Bookkeeping (Task 4)

### Task 4: eval-10 + CHANGELOG + SKILLS_STATUS + ARCHITECTURE

**Model:** Sonnet (mechanical YAML + text edits — all content is prescribed; no engineering judgment).

**Files:**
- Create: `electrical/small-power/evals/eval-10-cable-sizing-intent-consumed.yaml`
- Modify: `electrical/small-power/CHANGELOG.md`
- Modify: `SKILLS_STATUS.md`
- Modify: `ARCHITECTURE.md`

- [ ] **Step 1: Write eval-10**

Use Write to create `electrical/small-power/evals/eval-10-cable-sizing-intent-consumed.yaml`:

```yaml
name: eval-10-cable-sizing-intent-consumed
skill: electrical/small-power
description: |
  Skill-specific: v1.1 cable-sizing intent consumption. Verifies that the new
  uk-3bed-with-cable-sizing example resolves verified_zs_ohm on every circuit
  AND flips tool_call_pending_for_zs_verification to false AND drops the
  TOOL-CALL-PENDING:calc.zs_loop_impedance flag.
category: skill_specific
input_fixtures:
  - ../examples/uk-3bed-with-cable-sizing/output.json

checks:
  - assertion: "any(i.intent_type == 'cable-sizing' for i in output.meta.consumed_intents)"
    description: meta.consumed_intents[] includes a cable-sizing entry
    severity: critical
    matches_inv: INV-11

  - assertion: "all(c.get('verified_zs_ohm') is not None and c['verified_zs_ohm'] > 0 for c in output.circuits)"
    description: Every circuit has verified_zs_ohm populated and positive
    severity: critical

  - assertion: "all(c['tool_call_pending_for_zs_verification'] == False for c in output.circuits)"
    description: Every circuit has tool_call_pending_for_zs_verification == false
    severity: critical

  - assertion: "'TOOL-CALL-PENDING:calc.zs_loop_impedance' not in output.flags"
    description: TOOL-CALL-PENDING:calc.zs_loop_impedance flag dropped (Zs resolved by intent)
    severity: critical

  - assertion: "all(c['verified_zs_ohm'] < 1.5 for c in output.circuits)"
    description: All circuits within UK Type-B MCB 32A Zs_max=1.44Ω per BS 7671:2018+A2:2022 Table 41.3 (sanity check; specific OCPD-aware checks left to validator INV-08)
    severity: critical

  - assertion: "next((i.intent_version for i in output.meta.consumed_intents if i.intent_type == 'cable-sizing'), None) == '1.0.0'"
    description: cable-sizing intent version is 1.0.0 (matches consumed-cable-sizing-intent.json declared semver)
    severity: critical
```

- [ ] **Step 2: Validate eval-10**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
python3 -c "
import yaml, os
d = yaml.safe_load(open('electrical/small-power/evals/eval-10-cable-sizing-intent-consumed.yaml'))
assert d['skill'] == 'electrical/small-power'
assert d['category'] == 'skill_specific'
assert len(d['checks']) == 6
for fixture in d['input_fixtures']:
    resolved = os.path.normpath(os.path.join('electrical/small-power/evals', fixture))
    assert os.path.exists(resolved), f'missing fixture {resolved}'
print(f'eval-10: {len(d[\"checks\"])} checks, fixture resolves')
"
```

- [ ] **Step 3: Append v1.1.0 entry to small-power CHANGELOG.md**

Read the current CHANGELOG first to find the right insertion point:

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
head -30 electrical/small-power/CHANGELOG.md
```

Use Edit to insert a new `## [1.1.0]` section directly after the `# Changelog` heading (before the existing `## [1.0.0]` section). The new entry:

```markdown
## [1.1.0] - 2026-05-20

### Added — cable-sizing intent consumer migration (hybrid mode)

- **Multi-skill consumption**: `consumes_intents: ["cable-sizing"]` (was `[]`). Hybrid posture — when cable-sizing intent is provided in runtime inputs, every circuit's `verified_zs_ohm` is resolved from `Ze + (r1_plus_r2 / 1000) × length + (reactance / 1000) × length`; when intent is absent, v1.0 deferral behaviour holds (no breaking change).
- **Schema (additive, non-breaking)**: typed `meta.consumed_intents.items` (matches SLD v1.4 shape — required `intent_type` + `intent_version` + `produced_by`); new optional `cable_sizing_node_id` field per circuit (explicit override for the implicit `f"{parent_db.designation}.{circuit_id}"` composition).
- **Generator**: 12 → 13 steps (new Step 12 inserted: "Resolve Zs from cable-sizing intent"); existing rationale step renumbered to Step 13.
- **Validator**: 10 → 11 INV checks (new INV-11: cable-sizing intent lookup integrity — hard fail when intent consumed but a circuit's lookup fails).
- **Reviewer**: 6 → 7 D-checks (new D-7: Zs resolution provenance audit — flags mixed states where some circuits resolved and others deferred).
- **New worked example**: `examples/uk-3bed-with-cable-sizing/` (5 files: input.json + consumed-cable-sizing-intent.json + output.json + intent-out.json + reasoning.md). Mirrors the v1.0 `uk-3bed-dwelling` scenario but in v1.1 consumption mode with resolved Zs per circuit.
- **New eval**: `eval-10-cable-sizing-intent-consumed.yaml` (skill_specific category) — 6 checks covering v1.1 consumption behaviour.

### Unchanged from v1.0 (additive sprint — no breaking changes)

- All 4 existing v1.0 examples (`uk-3bed-dwelling`, `ke-nairobi-small-office`, `intl-open-plan-floor`, `us-residential-dwelling`) — now demonstrate v1.1 hybrid fallback behaviour when no intent is consumed
- All 9 existing v1.0 evals (eval-01 through eval-09)
- 5 rules + 3 constraints + 3 validation YAMLs
- Ontology (`shared/ontology/equipment/socket-types.json`) + symbols (`shared/symbols/electrical/sockets/`)
- Manifest `standards[]`, `ontology[]`, `calculations[]` arrays (no path changes)

### Pattern parents

- SLD v1.3 → v1.4 (leaf → multi-skill consumer) — closest structural precedent
- cable-sizing v1.0 refresh §2 (forward-compat contract this sprint fulfils)
- lighting-layout v1.3 (flexible-inputs pattern)
```

- [ ] **Step 4: Update SKILLS_STATUS.md cable-sizing row + small-power row**

Read the current SKILLS_STATUS.md cable-sizing + small-power rows first:

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
grep -n 'cable-sizing\|small-power' SKILLS_STATUS.md | head -10
```

For the cable-sizing row, find any forward-reference text mentioning "small-power v1.1" as a future consumer and flip it to "small-power v1.1 SHIPPED 2026-05-20".

For the small-power row, update:
- Status reference: `v1.0.0 beta` → `v1.1.0 beta`
- Evals count: `9/4 ✓` → `10/4 ✓`
- Notes: append (or prepend) a sentence covering v1.1 migration. The exact target sentence:

```
v1.1.0 — migrated from leaf to hybrid consumer of cable-sizing intent (consumes_intents: ["cable-sizing"]). New example uk-3bed-with-cable-sizing demonstrates resolved verified_zs_ohm per circuit from r1_plus_r2 × length + reactance × length + Ze. New INV-11 + D-7 + eval-10. Original 4 v1.0 examples + 9 v1.0 evals unchanged (demonstrate hybrid fallback).
```

If the user/linter has previously modified the small-power row (per the SKILLS_STATUS.md system-reminder note from the earlier sprint), respect their edits — only append v1.1-relevant content; do not revert their formatting.

- [ ] **Step 5: Update ARCHITECTURE.md**

Find the `### small-power skill (v1.0+)` subsection. Update title to `### small-power skill (v1.0+ / v1.1+)` AND add a paragraph at the end of the subsection describing v1.1:

```markdown
**v1.1 — Cable-sizing intent consumer (shipped 2026-05-20).** small-power v1.1 migrates from leaf to hybrid consumer of `cable-sizing` intent. When the intent is provided in runtime inputs, every circuit's `verified_zs_ohm` is resolved from `Ze + (r1_plus_r2 / 1000) × length + (reactance / 1000) × length`. When the intent is absent, v1.0 deferral behaviour holds — non-breaking additive change. Lookup uses implicit `f"{parent_db.designation}.{circuit_id}"` composition (default) or explicit `cable_sizing_node_id` per circuit (override). Generator gains Step 12 (Zs resolution), validator gains INV-11 (lookup integrity), reviewer gains D-7 (provenance audit). New worked example `uk-3bed-with-cable-sizing/` demonstrates the consumption mode; the 4 v1.0 examples now demonstrate the hybrid fallback path.
```

Then find the `### cable-sizing skill (v1.0+)` subsection. Locate the forward reference about "small-power v1.1 migration target" and update to "small-power v1.1 (shipped 2026-05-20) is now the live consumer of these helper fields".

- [ ] **Step 6: Validate all 4 file changes**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
python3 -c "
import yaml, os
d = yaml.safe_load(open('electrical/small-power/evals/eval-10-cable-sizing-intent-consumed.yaml'))
assert d['skill'] == 'electrical/small-power'
print('eval-10: present and parseable')
"
grep -c '## \[1.1.0\]' electrical/small-power/CHANGELOG.md
grep -c 'v1.1.0\|small-power v1.1' SKILLS_STATUS.md
grep -c 'small-power skill (v1.0+ / v1.1+)\|v1.1 — Cable-sizing intent consumer' ARCHITECTURE.md
```

Expected: eval-10 parseable; CHANGELOG has `## [1.1.0]` once; SKILLS_STATUS mentions v1.1.0 at least once; ARCHITECTURE mentions either the updated title or the v1.1 paragraph.

- [ ] **Step 7: Commit**

```bash
git add electrical/small-power/evals/ electrical/small-power/CHANGELOG.md SKILLS_STATUS.md ARCHITECTURE.md
git commit -m "docs+eval(small-power): v1.1.0 — eval-10 cable-sizing consumption + CHANGELOG + SKILLS_STATUS + ARCHITECTURE"
```

---

## Phase E — Cross-cutting validation + push (Task 5)

### Task 5: Final validation + push

**Model:** Opus (judgment on ship-readiness; manages the push gate; saves sprint memory).

This task makes NO new content edits unless cross-cutting validation finds a blocker. It validates the assembled v1.1 migration end-to-end, dispatches a code-review subagent if desired, and pushes to origin/main.

- [ ] **Step 1: Cross-cutting validation pass**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"

# 1.1 — Manifest reflects v1.1.0 + consumes_intents
python3 -c "
import json
m = json.load(open('electrical/small-power/skill.manifest.json'))
assert m['version'] == '1.1.0'
assert m['consumes_intents'] == ['cable-sizing']
print('manifest: v1.1.0 + consumes cable-sizing ✓')
"

# 1.2 — IR schema has typed consumed_intents.items + cable_sizing_node_id field
python3 -c "
import json
s = json.load(open('electrical/small-power/schemas/small-power-ir.schema.json'))
ci = s['properties']['meta']['properties']['consumed_intents']['items']
assert ci['required'] == ['intent_type', 'intent_version', 'produced_by']
assert ci['additionalProperties'] == False
assert 'cable_sizing_node_id' in s['properties']['circuits']['items']['properties']
print('schema: typed consumed_intents + cable_sizing_node_id field ✓')
"

# 1.3 — Generator has 13 steps, validator has 11 INV, reviewer has 7 D
python3 -c "
import re
gen = open('electrical/small-power/prompts/generator.md').read()
val = open('electrical/small-power/prompts/validator.md').read()
rev = open('electrical/small-power/prompts/reviewer.md').read()
n_steps = len(re.findall(r'^### Step [0-9]+', gen, flags=re.MULTILINE))
n_inv = len(re.findall(r'^### INV-|^## INV-', val, flags=re.MULTILINE))
n_d = len(re.findall(r'^### D-|^## D-', rev, flags=re.MULTILINE))
print(f'generator steps: {n_steps} (expect 13)')
print(f'validator INV checks: {n_inv} (expect 11)')
print(f'reviewer D-checks: {n_d} (expect 7)')
assert n_steps == 13 and n_inv == 11 and n_d == 7
"

# 1.4 — All 4 v1.0 examples still validate against v1.1 schema (hybrid fallback path)
python3 -c "
import json, jsonschema, copy
s = json.load(open('electrical/small-power/schemas/small-power-ir.schema.json'))
s_test = copy.deepcopy(s)
s_test['properties']['rationale'] = {'type': 'object'}
for ex in ['uk-3bed-dwelling','ke-nairobi-small-office','intl-open-plan-floor','us-residential-dwelling']:
    o = json.load(open(f'electrical/small-power/examples/{ex}/output.json'))
    jsonschema.validate(o, s_test)
    print(f'  {ex}: still validates against v1.1 schema (hybrid fallback)')
"

# 1.5 — New uk-3bed-with-cable-sizing example: all 5 circuits have verified_zs_ohm + tool_call_pending=false + flag dropped
python3 -c "
import json
o = json.load(open('electrical/small-power/examples/uk-3bed-with-cable-sizing/output.json'))
ci = o['meta']['consumed_intents']
assert len(ci) == 1 and ci[0]['intent_type'] == 'cable-sizing'
expected_zs = {'C01': 0.9318, 'C02': 0.8591, 'C03': 0.4142, 'C04': 0.4227, 'C05': 0.4412}
for c in o['circuits']:
    cid = c['circuit_id']
    assert c.get('verified_zs_ohm') is not None
    assert c['tool_call_pending_for_zs_verification'] == False
    assert abs(c['verified_zs_ohm'] - expected_zs[cid]) < 0.001
assert 'TOOL-CALL-PENDING:calc.zs_loop_impedance' not in o['flags']
print('uk-3bed-with-cable-sizing example: v1.1 invariants OK')
"

# 1.6 — File counts
echo '--- New + modified file count ---'
find electrical/small-power/examples/uk-3bed-with-cable-sizing -type f | wc -l
ls electrical/small-power/evals/eval-10*.yaml
```

- [ ] **Step 2: Spot-check final code review (optional subagent dispatch OR direct inspection)**

If using subagent-driven-development with sufficient budget, dispatch a code-reviewer subagent against the full diff (~14 files). The reviewer should look for:

- CRITICAL/HIGH: any v1.0 example now fails to validate against v1.1 schema (would be a breaking change — must be a CRITICAL)
- HIGH: the new example's Zs values don't match the computed expected values within 0.001 Ω
- MEDIUM: any internal inconsistency between generator Step 12 wording, validator INV-11 wording, reviewer D-7 wording (they reference the same lookup mechanic — should be consistent)
- MEDIUM: SKILLS_STATUS / ARCHITECTURE / CHANGELOG forward references between cable-sizing and small-power are aligned

If skipping the subagent (budget-constrained), read these files directly:
- `electrical/small-power/skill.manifest.json` — v1.1.0 + consumes_intents
- `electrical/small-power/schemas/small-power-ir.schema.json` — typed consumed_intents.items + cable_sizing_node_id
- `electrical/small-power/prompts/generator.md` Step 12 (Zs resolution) — verify the Ze + r1+r2/1000 × length + X/1000 × length formula is exact
- `electrical/small-power/examples/uk-3bed-with-cable-sizing/output.json` — verify the 5 Zs values
- `SKILLS_STATUS.md` cable-sizing + small-power rows aligned

If any blocker found, STOP and report. Do NOT push.

- [ ] **Step 3: Push**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
git log --oneline 2bb4195^..HEAD | head -10
git status
git push origin main
```

Expected: 5-6 commits pushed (Tasks 1-4 implementation commits + this plan/spec commit pair). If the push fails (e.g., remote rejected), report the error and stop.

- [ ] **Step 4: Save sprint memory**

Write `/Users/linus/.claude/projects/-Users-linus-Desktop-DraftsMan-SKills-draftsman-skills/memory/small-power-v1.1-shipped.md`:

```markdown
---
name: small-power-v1.1-shipped
description: small-power v1.1.0 beta shipped 2026-05-20 — hybrid consumer of cable-sizing intent, resolves Zs per circuit via r1_plus_r2 × length + Ze
metadata:
  type: project
---

**✅ SHIPPED 2026-05-20 — small-power v1.1.0 beta**

Migration sprint completed. small-power moved from leaf (consumes_intents: []) to hybrid consumer of cable-sizing intent. Validates the cable-sizing v1.0 refresh §2 forward-compat contract.

## Architecture captured

- Hybrid intent posture: optional consumption, v1.0 fallback when intent absent (non-breaking)
- Lookup: implicit f"{parent_db.designation}.{circuit_id}" composition default + optional cable_sizing_node_id explicit override
- Zs computation: verified_zs_ohm = Ze + (r1_plus_r2 / 1000) × length + (reactance / 1000) × length
- Generator 12 → 13 steps (new Step 12 — Zs resolution)
- Validator 10 → 11 INV (new INV-11 — lookup integrity hard-fail when intent consumed)
- Reviewer 6 → 7 D-checks (new D-7 — provenance audit)
- Manifest version 1.0.0 → 1.1.0, consumes_intents: ["cable-sizing"]
- New example uk-3bed-with-cable-sizing/ (5 files) + new eval-10
- 4 v1.0 examples + 9 v1.0 evals untouched — they demonstrate hybrid fallback

## Stats

- ~12 file ops (5 new + 7 modifications)
- 1 new worked example with 5 resolved Zs values matching cable-sizing UK domestic anchor data
- 1 new eval (eval-10, skill_specific category, 6 checks)
- ~1-2 day sprint (per design budget)

## How to apply

- Future cable-schedule skill v1.0: same hybrid consumer pattern (consume cable-sizing intent for tabulated deliverable)
- Future riser skill v1.0: same pattern for floor-by-floor LV riser rendering
- Future cable-containment skill v1.0: same pattern for tray/conduit fill
- Pattern parent for future skills consuming intents: small-power v1.1 + SLD v1.4 (hybrid vs hard-require)

## Cross-references

- [[small-power-shipped]] — v1.0 baseline (still valid; v1.1 is additive)
- [[cable-sizing-shipped]] — provides the intent v1.1 consumes
- [[runtime-project-boundary]] — intent contracts ship from skills; runtime consumes
- [[feedback-no-haiku-sonnet-opus-only]] — followed throughout sprint
- [[build-strategy-breadth-first]] — closes Tier 1 cable-sizing↔small-power loop
```

Then update `MEMORY.md` in the same directory with a 1-line index entry pointing at the new file.

- [ ] **Step 5: Final summary report**

Report back:
- Status: DONE / DONE_WITH_CONCERNS / BLOCKED
- Push status: SHA range pushed (e.g., `eee98c2..XXXXXXX`)
- File count delta
- Sprint complete summary (1-2 sentences)

---

## Self-review checklist (run after writing this plan)

- [x] **Spec coverage:** Every section of the design spec has a task implementing it.
  - Spec §3 Manifest changes → Task 1 Steps 2-3
  - Spec §4 Schema changes → Task 1 Steps 6-7
  - Spec §5 Generator new Step 12 → Task 2 Step 2
  - Spec §6 Validator INV-11 → Task 2 Step 6
  - Spec §7 Reviewer D-7 → Task 2 Step 8
  - Spec §8 New example → Task 3 Steps 1-11
  - Spec §9 eval-10 → Task 4 Steps 1-2
  - Spec §10 Bookkeeping → Task 4 Steps 3-7
  - Spec §11 Untouched verification → Task 5 Step 1.4
- [x] **Placeholder scan:** No "TBD"/"TODO"/"add validation"/"similar to". Full content for every step.
- [x] **Type consistency:** `cable_sizing_node_id` field name used identically in schema (Task 1), generator Step 12 (Task 2), validator INV-11 (Task 2), reviewer D-7 (Task 2), example output (Task 3 — not used in this example since implicit composition works, but available). `verified_zs_ohm`, `tool_call_pending_for_zs_verification`, `TOOL-CALL-PENDING:calc.zs_loop_impedance` strings all spelled identically across tasks. Zs computation formula `Zs = Ze + (r1_plus_r2 / 1000) × length + (reactance / 1000) × length` used identically in generator Step 12, reasoning.md, and validation steps.

---

**Plan complete and saved to `docs/superpowers/plans/2026-05-20-small-power-v1.1-migration-sprint.md`.**

Two execution options:

1. **Subagent-Driven (recommended)** — Fresh subagent per task, two-stage review (spec compliance → code quality) after each, continuous execution. Matches the proven pattern from small-power v1.0 + cable-sizing v1.0 sprints.

2. **Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints for user review.

Which approach?
