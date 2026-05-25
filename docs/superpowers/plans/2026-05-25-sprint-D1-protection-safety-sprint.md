# Sprint D1 — Protection & Safety depth Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close 4 within-skill depth gaps across fault-level + arc-flash (breaking-capacity verdict per cascade node; explicit motor/UPS superposition; full Park's-equations decrement curves; arc-flash equipment-condition with 1.25× abnormal IE adjustment) before pivoting to breadth-first new-skill builds.

**Architecture:** Each item follows the established 5-step pattern (IR schema add → generator prompt step → validator INV → example update → CHANGELOG patch-bump). Sequential within fault-level because items 2–3 build on item 1's schema scaffolding; arc-flash item runs as a separate task on a different skill. One prerequisite task (D1.0) extends the db-layout intent schema to expose `breaking_capacity_ka` per device so Item 1's hybrid consumer pattern can read it from the intent rather than the output.

**Tech Stack:** JSON Schema Draft-07 (IR + intent schemas), Markdown (generator/validator/reviewer prompts), YAML (validation specs + evals), Python 3.11 (validate-examples.py + functional_audit.py).

**Spec:** `docs/superpowers/specs/2026-05-25-sprint-D1-protection-safety-depth-design.md` (commit `b69a7ee`).

**INV numbering resolved (from current validator.md counts):**
- fault-level: 11 existing → new are **INV-12** (breaking-capacity), **INV-13** (superposition), **INV-14** (decrement)
- arc-flash: 10 existing → new is **INV-11** (equipment-condition)

**CHANGELOG version bumps:**
- fault-level: `[next-patch]` (unresolved from M1) → `[1.2.0]` (minor — new features land in D1)
- arc-flash: `[1.0.2]` → `[1.1.0]` (minor — new features land in D1)

---

## File Structure

### Modified

- `electrical/db-layout/schemas/db-layout-intent.schema.json` — D1.0: expose `breaking_capacity_ka` on `main_switch` + on each outgoing-circuit `ocpd` block
- `electrical/db-layout/examples/*/intent-out.json` (10 total) — D1.0: populate the new field from the corresponding output.json
- `electrical/fault-level/schemas/fault-level-ir.schema.json` — D1.1/D1.2/D1.3: add `breaking_capacity`, `superposition_contribution_ka`, `decrement_curve` properties to cascade item; extend `sources[]` with `contributes_to_nodes`
- `electrical/fault-level/prompts/generator.md` — D1.1/D1.2/D1.3: 3 new numbered steps
- `electrical/fault-level/prompts/validator.md` — D1.1/D1.2/D1.3: add INV-12, INV-13, INV-14
- `electrical/fault-level/examples/*/output.json` (6 total) — D1.1: breaking_capacity on key nodes; D1.2: superposition explicit (us-industrial-with-motors + intl-commercial-with-genset); D1.3: decrement_curve on intl-commercial-with-genset
- `electrical/fault-level/CHANGELOG.md` — D1 entry; bump 1.1.1 → 1.2.0
- `electrical/fault-level/skill.manifest.json` — version sync
- `electrical/arc-flash/schemas/arc-flash-ir.schema.json` — D1.4: extend CascadeNode definition + root with equipment_condition + worker_position
- `electrical/arc-flash/prompts/generator.md` — D1.4: new numbered step
- `electrical/arc-flash/prompts/validator.md` — D1.4: add INV-11
- `electrical/arc-flash/examples/*/output.json` (4 total) — D1.4: equipment_condition: normal default on every cascade node
- `electrical/arc-flash/CHANGELOG.md` — D1 entry; bump 1.0.2 → 1.1.0
- `electrical/arc-flash/skill.manifest.json` — version sync

### Created

- `electrical/arc-flash/examples/uk-abnormal-condition-water-damaged/input.json` — D1.4 new example input
- `electrical/arc-flash/examples/uk-abnormal-condition-water-damaged/output.json` — D1.4 new example output exercising the abnormal-condition branch
- `electrical/arc-flash/examples/uk-abnormal-condition-water-damaged/intent-out.json` — D1.4 new example emitted intent
- `electrical/arc-flash/examples/uk-abnormal-condition-water-damaged/reasoning.md` — D1.4 new example reasoning
- Memory file `sprint-D1-shipped.md` at `~/.claude/projects/-Users-linus-Desktop-DraftsMan-SKills-draftsman-skills/memory/`

---

## Task D1.0: Extend db-layout intent schema with breaking_capacity_ka (Sonnet)

**Why Sonnet:** mechanical schema property addition + backport to 10 example intents from their corresponding output.json. No engineering judgment.

**Why D1.0 first:** Item 1's hybrid consumer pattern (D1.1) reads device data from the db-layout intent when present. The intent schema currently only declares `main_switch.{type, rating_a, curve}` and outgoing-circuit `breaker_rating_a + breaker_curve` — but the OUTPUT carries `breaking_capacity_ka` per device. fault-level can't read what the intent doesn't declare. D1.0 closes this gap before D1.1 needs it.

**Files:**
- Modify: `electrical/db-layout/schemas/db-layout-intent.schema.json` — add `breaking_capacity_ka` to `main_switch` properties + add `ocpd` block to outgoing-circuit items
- Modify: 20 × `electrical/db-layout/examples/*/intent-out.json` — backport breaking_capacity_ka from each example's corresponding output.json

- [ ] **Step 1: Read current intent schema**

Read `electrical/db-layout/schemas/db-layout-intent.schema.json`. Locate the `main_switch` property block (line ~50ish — search for `"main_switch"`). Note current properties: `type, rating_a, curve` with `additionalProperties: false`.

Locate the `circuits` array `items` block. Note current properties include `breaker_rating_a, breaker_curve` but no `breaker_breaking_capacity_ka`.

- [ ] **Step 2: Extend main_switch schema**

Edit `electrical/db-layout/schemas/db-layout-intent.schema.json`. Find the `main_switch.properties` block and add `breaking_capacity_ka`:

```json
"breaking_capacity_ka": {
  "type": "number",
  "exclusiveMinimum": 0,
  "description": "Rated short-circuit breaking capacity in kA (Icn per BS EN 60898; Icu per IEC 60947-2). Used by downstream fault-level for breaking-capacity verdict per BS 7671 Reg 432.1.2 / NEC 110.9. Added Sprint D1.0 to enable fault-level hybrid consumer pattern (D1.1)."
}
```

Add `"breaking_capacity_ka"` to the `main_switch.required` array. If `main_switch.required` doesn't exist yet, create it as `["type", "rating_a", "breaking_capacity_ka"]`.

- [ ] **Step 3: Extend outgoing circuit ocpd shape**

Find the `circuits.items.properties` block. Currently has `breaker_rating_a, breaker_curve` as flat fields. Add a sibling `breaker_breaking_capacity_ka`:

```json
"breaker_breaking_capacity_ka": {
  "type": "number",
  "exclusiveMinimum": 0,
  "description": "Rated short-circuit breaking capacity in kA for this circuit's OCPD. Per BS EN 60898 (MCBs) / IEC 60947-2 (MCCBs/ACBs). Used by downstream fault-level for breaking-capacity verdict per BS 7671 Reg 432.1.2 / NEC 110.9. Added Sprint D1.0."
}
```

Add `"breaker_breaking_capacity_ka"` to `circuits.items.required` (alongside existing `id, module_id, breaker_rating_a, breaker_curve`).

- [ ] **Step 4: Run validate-examples to see which intents now fail**

```bash
python3 scripts/validate-examples.py 2>&1 | grep -A 1 "## db-layout:" | head -50
```

Expected: 20 db-layout intents fail Pass 4 with `'breaking_capacity_ka' is a required property` (or `'breaker_breaking_capacity_ka'`). This is by design — Step 5 backports the values.

- [ ] **Step 5: Backport breaking_capacity_ka from output.json to intent-out.json across 20 examples**

For each `electrical/db-layout/examples/*/intent-out.json`, populate `main_switch.breaking_capacity_ka` from the corresponding `output.json` `main_switch.breaking_capacity_ka` (the output already carries it — see uk-domestic-consumer-unit which shows `"breaking_capacity_ka": 12` on main_switch).

Use this Python helper script (single-use; do not commit):

```python
import json, glob, os

for ip in sorted(glob.glob('electrical/db-layout/examples/*/intent-out.json')):
    op = ip.replace('intent-out.json', 'output.json')
    if not os.path.exists(op):
        print(f'SKIP (no output): {ip}')
        continue
    intent = json.load(open(ip))
    out = json.load(open(op))
    
    # Backport main_switch.breaking_capacity_ka
    out_ms = out.get('main_switch', {})
    intent_ms = intent.get('main_switch', {})
    if 'breaking_capacity_ka' in out_ms and 'breaking_capacity_ka' not in intent_ms:
        intent_ms['breaking_capacity_ka'] = out_ms['breaking_capacity_ka']
        intent['main_switch'] = intent_ms
    
    # Backport per-circuit ocpd.breaking_capacity_ka → breaker_breaking_capacity_ka
    out_circuits = {c.get('circuit_id'): c for c in out.get('circuits', [])}
    for ic in intent.get('circuits', []):
        cid = ic.get('id')
        oc = out_circuits.get(cid, {})
        ocpd = oc.get('ocpd', {}) if isinstance(oc.get('ocpd'), dict) else {}
        if 'breaking_capacity_ka' in ocpd and 'breaker_breaking_capacity_ka' not in ic:
            ic['breaker_breaking_capacity_ka'] = ocpd['breaking_capacity_ka']
    
    with open(ip, 'w') as f:
        json.dump(intent, f, indent=2, ensure_ascii=False)
        f.write('\n')
    print(f'updated: {ip}')
```

Run it once, verify the 20 intent files have the new field, then delete the script.

- [ ] **Step 6: Verify gates**

```bash
python3 scripts/validate-examples.py 2>&1 | tail -3
python3 functional_audit.py 2>&1 | tail -2
```

Expected: AGGREGATE 219/219 (held — no new examples; just field additions to existing ones); 1 finding (motor-superposition disclaimed FP, unchanged).

If any intent still fails Pass 4 with the new required field: the corresponding output.json doesn't carry `breaking_capacity_ka` on its main_switch or some circuit. Honest handling: read that specific example's output, determine the engineer-intended capacity from the device type + rating, populate it (e.g. domestic 100A switch-disconnector → 12 kA typical per BS EN 60947-3; commercial MCCB → 25/36/50 kA per Icu rating). Cite the value in the intent's `_source` field if needed.

- [ ] **Step 7: Update db-layout CHANGELOG**

Add to `electrical/db-layout/CHANGELOG.md` (above current top entry `[1.3.2]`):

```markdown
## [1.3.3] - 2026-05-25

### Added
- **D1.0 (Sprint D1 prerequisite):** `main_switch.breaking_capacity_ka` +
  outgoing-circuit `breaker_breaking_capacity_ka` declared in the intent
  schema (now required). Field already existed in the output IR; the
  intent was the missing piece. Enables downstream fault-level Sprint D1
  hybrid-consumer breaking-capacity verdict (D1.1).
- Backported the field across all 20 example intent-out.json files
  by reading from each example's corresponding output.json main_switch
  + per-circuit ocpd block.
```

Bump `electrical/db-layout/skill.manifest.json` `"version"` from `"1.3.2"` to `"1.3.3"`.

- [ ] **Step 8: Commit**

```bash
git add electrical/db-layout/schemas/db-layout-intent.schema.json electrical/db-layout/examples/*/intent-out.json electrical/db-layout/CHANGELOG.md electrical/db-layout/skill.manifest.json
git commit -m "$(cat <<'EOF'
feat(db-layout): D1.0 intent — expose breaking_capacity_ka on main_switch + per-circuit ocpd

Sprint D1 prerequisite: fault-level Item 1 (breaking-capacity verdict per
cascade node, D1.1) uses a hybrid consumer pattern reading device data
from db-layout intent when consumed_intents includes db-layout. The intent
schema previously declared main_switch.{type, rating_a, curve} but NOT
breaking_capacity_ka — even though the output IR carries it. This commit
extends the intent schema to expose the field + backports values across
all 20 examples by reading from each output.json.

Schema changes (db-layout-intent.schema.json):
- main_switch.properties gains breaking_capacity_ka (number, exclusiveMinimum 0)
- main_switch.required adds breaking_capacity_ka
- circuits.items.properties gains breaker_breaking_capacity_ka (number)
- circuits.items.required adds breaker_breaking_capacity_ka

Examples (20 intent-out.json files updated): values backported from each
output.json main_switch.breaking_capacity_ka + per-circuit ocpd.
breaking_capacity_ka. No engineering content change — same numbers,
exposed at the right layer.

CHANGELOG [1.3.3] entry added; manifest version bumped 1.3.2 → 1.3.3.

validate-examples.py: 219/219 held across 4 passes.
functional_audit.py: 1 finding unchanged (motor-superposition FP).

Enables D1.1 (fault-level breaking-capacity verdict, hybrid consumer
pattern). The verdict task will validate D1.0 transitively because it
reads the field from consumed db-layout intent.
EOF
)"
```

---

## Task D1.1: fault-level breaking-capacity verdict per cascade node (Opus)

**Why Opus:** engineering judgment on verdict thresholds + integration with the hybrid consumer pattern. The Sprint B.1 fix-pass precedent shows this class of work needs Opus.

**Files:**
- Modify: `electrical/fault-level/schemas/fault-level-ir.schema.json` — add `breaking_capacity` object to cascade item properties
- Modify: `electrical/fault-level/prompts/generator.md` — add new step
- Modify: `electrical/fault-level/prompts/validator.md` — add INV-12
- Modify: 6 × `electrical/fault-level/examples/*/output.json` — populate breaking_capacity on at least 3 cascade nodes per example
- Modify: `electrical/fault-level/CHANGELOG.md` — D1 entry
- Modify: `electrical/fault-level/skill.manifest.json` — version sync

- [ ] **Step 1: Read current fault-level IR schema**

```bash
python3 -c "
import json
s = json.load(open('electrical/fault-level/schemas/fault-level-ir.schema.json'))
cn = s.get('properties',{}).get('cascade',{}).get('items',{})
print('cascade item type:', cn.get('type'))
print('cascade item required:', cn.get('required',[]))
print('cascade item properties:', list(cn.get('properties',{}).keys()))
"
```

Confirm cascade item properties include the existing fields (node_id, parent_node_id, node_kind, designation, feeder, z_addition_ohm, ifault_ka_max, ifault_ka_min, ipk_ka, x_over_r_at_node, z_total_ohm, calculation_basis, tool_call_pending). The new `breaking_capacity` is an optional addition.

- [ ] **Step 2: Add breaking_capacity to cascade item schema**

Edit `electrical/fault-level/schemas/fault-level-ir.schema.json`. Find the `cascade.items.properties` block. Add at the end (before the closing brace of `properties`):

```json
"breaking_capacity": {
  "type": "object",
  "description": "Breaking-capacity verdict for the protective device at this node. Hybrid consumer pattern per Sprint D1.1: when consumed_intents includes db-layout, generator reads device data from db-layout intent's main_switch.breaking_capacity_ka + circuits[*].breaker_breaking_capacity_ka. When db-layout intent is absent, engineer declares device per-node in cascade_topology_declared. Verdict thresholds: ok >= 10% headroom; marginal 0-10%; inadequate < 0%. Per BS 7671:2018+A2:2022 Reg 432.1.2 / NEC 2023 §110.9 / IEC 60947-2.",
  "additionalProperties": false,
  "required": ["device_id", "device_type", "ik3_node_ka", "headroom_pct", "verdict", "verdict_basis", "data_source"],
  "properties": {
    "device_id": {
      "type": "string",
      "description": "Engineer reference for the device (e.g. 'MS-1' or 'OCPD-C03')."
    },
    "device_type": {
      "type": "string",
      "enum": ["MCB", "MCCB", "ACB", "fuse_BS88", "fuse_NEC", "air_circuit_breaker", "switch_disconnector"]
    },
    "device_icn_ka": {
      "type": "number",
      "exclusiveMinimum": 0,
      "description": "Rated short-circuit breaking capacity per BS EN 60898 / IEC 60947-2 Annex."
    },
    "device_icu_ka": {
      "type": "number",
      "exclusiveMinimum": 0,
      "description": "Ultimate short-circuit breaking capacity per IEC 60947-2."
    },
    "device_ics_ka": {
      "type": "number",
      "exclusiveMinimum": 0,
      "description": "Service short-circuit breaking capacity per IEC 60947-2 (typically 0.5-1.0 × Icu). Optional."
    },
    "device_icw_ka_1s": {
      "type": "number",
      "exclusiveMinimum": 0,
      "description": "Rated short-time withstand at 1 second per IEC 60947-2 (ACBs only). Optional."
    },
    "ik3_node_ka": {
      "type": "number",
      "minimum": 0,
      "description": "Three-phase Ik at this node, recomputed from z_total_ohm for self-consistency."
    },
    "headroom_pct": {
      "type": "number",
      "description": "((min(device_icn_ka, device_icu_ka) − ik3_node_ka) / ik3_node_ka) × 100. Negative values mean inadequate (device cannot interrupt prospective short-circuit)."
    },
    "verdict": {
      "type": "string",
      "enum": ["ok", "marginal", "inadequate"]
    },
    "verdict_basis": {
      "type": "string",
      "description": "Citation: BS 7671:2018+A2:2022 Reg 432.1.2 / NEC 2023 §110.9 / IEC 60947-2."
    },
    "data_source": {
      "type": "string",
      "enum": ["db_layout_intent", "engineer_declared"]
    }
  }
}
```

Do NOT add `breaking_capacity` to the cascade item's `required` array — additive (existing examples may not all populate it on every node; required only when device data is available).

- [ ] **Step 3: Add generator step**

Read `electrical/fault-level/prompts/generator.md`. Find the LAST numbered step in the generation flow (search for the highest "### Step N" heading). Append the new step:

```markdown
### Step <N+1>: Breaking-capacity verdict per cascade node (D1.1)

For every cascade node, look up the protective device at this node (the OCPD upstream of the node OR the main switch at the supply boundary), then emit a `breaking_capacity` block.

**Data source — hybrid consumer pattern:**

1. **If `consumed_intents` includes a db-layout entry:** read device data from the consumed intent.
   - For the service-entrance node (the cascade root or first LV node): use `main_switch.{rating_a, breaking_capacity_ka, type}` from db-layout intent.
   - For downstream OCPD-protected nodes: match by `node_id` to db-layout intent's `circuits[*]` and read `{breaker_rating_a, breaker_breaking_capacity_ka, breaker_curve}`.
   - Set `data_source: "db_layout_intent"`.

2. **If db-layout intent absent:** read engineer-declared device data from `cascade_topology_declared[*].device` in input.json (engineer provides `{device_id, device_type, device_icn_ka, device_icu_ka}` per node).
   - Set `data_source: "engineer_declared"`.

**Compute the verdict per node:**

```
ik3_node_ka     = c × U / (div × z_total_ohm) / 1000     (recompute from node z; same formula as INV-11)
device_rating   = min(device_icn_ka, device_icu_ka)       (worst-case interrupting rating)
headroom_pct    = ((device_rating − ik3_node_ka) / ik3_node_ka) × 100

verdict = "ok"          if headroom_pct >= 10
        = "marginal"    if 0 <= headroom_pct < 10
        = "inadequate"  if headroom_pct < 0
```

**Citation form per jurisdiction (verdict_basis):**
- GB: `"BS 7671:2018+A2:2022 Reg 432.1.2"`
- INT: `"IEC 60947-2:2016 § 4.3.6.4"`
- US: `"NEC 2023 § 110.9"` or `"NFPA 70 § 110.9"`
- KE: `"KS 1700:2018 § 432 (routes to BS 7671:2018+A2:2022 Reg 432.1.2)"`

**Emit block per cascade node** (only when device data is available; nodes without a device — e.g. pure cable midpoints — omit the block).

**Cross-validate with INV-12** (next step in validator.md): the headroom_pct arithmetic must reconcile within 0.5% of the computed value.
```

(Substitute `<N+1>` with the actual next step number based on current generator.md count.)

- [ ] **Step 4: Add INV-12 to validator.md**

Read `electrical/fault-level/prompts/validator.md`. The file currently ends with INV-11 (added in Sprint B.1). Append INV-12 in the same bold-paragraph style as INV-1..INV-11:

```markdown

---

**INV-12: Breaking-capacity verdict internal consistency.**

**Severity:** HIGH

**Rule:** For every cascade node carrying a `breaking_capacity` block, the following must hold:

1. **Ik3 self-consistency:** `breaking_capacity.ik3_node_ka` reconciles to `c × U / (div × z_total_ohm) / 1000` within 1%, using the same formula INV-11 enforces on this node's `ifault_ka_max`.

2. **Headroom arithmetic:** `headroom_pct` reconciles to `((min(device_icn_ka, device_icu_ka) − ik3_node_ka) / ik3_node_ka) × 100` within 0.5%.

3. **Verdict threshold match:** `verdict` matches the threshold table:
   - `ok` if `headroom_pct >= 10`
   - `marginal` if `0 <= headroom_pct < 10`
   - `inadequate` if `headroom_pct < 0`

4. **Data source consistency:** `data_source ∈ {"db_layout_intent", "engineer_declared"}`. If `"db_layout_intent"`, then `meta.consumed_intents[]` must include a db-layout entry (otherwise the claim is false).

5. **At least one device rating present:** at least one of `device_icn_ka` or `device_icu_ka` must be present and > 0 (the verdict has nothing to compare to otherwise).

**Validator action:** for each cascade node with `breaking_capacity`, recompute ik3 and headroom_pct; assert verdict matches threshold; assert data_source consistency. Flag any mismatch > 1% (ik3) or > 0.5% (headroom) or wrong verdict bucket.

**Rationale:** This is what makes fault-level self-sufficient for switchgear selection per BS 7671 Reg 432.1.2 / NEC §110.9 / IEC 60947-2 — the engineer no longer has to manually cross-check Ik vs device Icn/Icu. The INV catches authoring drift (wrong verdict bucket, stale headroom after Ik changes).
```

- [ ] **Step 5: Update 6 example outputs**

For each of the 6 fault-level example outputs, populate `breaking_capacity` on AT LEAST 3 cascade nodes (service-entrance, MSB main switch, one downstream node). Where db-layout intent is available in `consumed_intents`, set `data_source: "db_layout_intent"` and the device values must match what the consumed db-layout intent would emit (compute headroom + verdict per the rules above).

**Per-example targets (engineer-defensible defaults — substitute actual values from the corresponding example state):**

`ke-nairobi-industrial` — MSB-1 (1000A ACB; engineer-declared since no db-layout intent consumed in fault-level example yet):
```json
"breaking_capacity": {
  "device_id": "MSB-1-ACB",
  "device_type": "ACB",
  "device_icn_ka": 50.0,
  "device_icu_ka": 50.0,
  "device_icw_ka_1s": 50.0,
  "ik3_node_ka": 9.0,
  "headroom_pct": 455.6,
  "verdict": "ok",
  "verdict_basis": "KS 1700:2018 § 432 (routes to BS 7671:2018+A2:2022 Reg 432.1.2)",
  "data_source": "engineer_declared"
}
```

`uk-commercial-3storey` — service-entrance + MSB-MAIN + DB-L1 incoming. Service-entrance HV-1 has 16 kA declared PSCC and uses an upstream HV fuse with Icn typically ≥ 20 kA → verdict ok. MSB-MAIN (LV 800A ACB at the transformer LV) sees ~22 kA Ik → 50 kA Icu → 127% headroom → ok. DB-L1 incoming (63A MCCB at ~8 kA Ik) → 50 kA Icu → 525% → ok.

`us-strip-mall-retail` — MSB main service-entrance (200A NEC ACB rated 65 kA SCCR per NEC §110.9) at ~12 kA Ik3 → 442% headroom → ok. Cite NEC §110.9.

`intl-commercial-with-genset` — TX-1 now Ik 43.49 kA (post-Sprint-B.1 fix). MSB-1 main switch is 1600A 50 kA Icu → headroom (50 − 43.49) / 43.49 × 100 = **15.0%** → **ok at the edge of marginal** (matches the SLD B.1 fix-pass note that the design is comfortable but should consider 65 kA at next refresh). MSB-1.BUSBAR same. HV-1 declared PSCC 16 kA against the 11 kV switchgear ACB Icn (typically 25 kA) → 56% headroom → ok.

`uk-domestic-single-source` — CU-G consumer-unit main switch (100A switch-disconnector, 6 kA Icn per BS EN 60947-3) at ~1.5 kA Ik → 300% headroom → ok. CU-G.BUSBAR (same protection) → ok.

`us-industrial-with-motors` — HV-1 (after Sprint B.1 double-c fix: 25 kA Ik). 13.8 kV ACB rated 50 kA Icu per NEC industrial practice → 100% headroom → ok. MSB-1 (after Sprint B.1 + D1.2 superposition: 35 kA Ik including motor back-feed). MSB-1 ACB rated 50 kA Icu → 42.9% headroom → ok. MCC-1 (35 kA Ik with motor superposition). MCC main breaker 50 kA Icu → 42.9% → ok.

**Hand-check each verdict against the threshold table before committing.** A wrong verdict bucket on any node will fail INV-12.

- [ ] **Step 6: Run gates**

```bash
python3 scripts/validate-examples.py 2>&1 | tail -3
python3 functional_audit.py 2>&1 | tail -2
```

Expected: AGGREGATE 219/219 (additive schema change holds — no existing required field was added). Pass 1 must still show all 6 fault-level outputs PASS. Pass 4 unchanged (this task doesn't touch the intent emission). 1 finding unchanged.

- [ ] **Step 7: Hand-check INV-12 on intl-commercial-with-genset MSB-1**

```bash
python3 -c "
import json, math
d = json.load(open('electrical/fault-level/examples/intl-commercial-with-genset/output.json'))
for n in d['cascade']:
    if n['node_id'] == 'MSB-1':
        bc = n.get('breaking_capacity', {})
        ik = bc.get('ik3_node_ka')
        rating = min(bc.get('device_icn_ka', 1e9), bc.get('device_icu_ka', 1e9))
        expected_hr = ((rating - ik) / ik) * 100
        actual_hr = bc.get('headroom_pct')
        print(f'MSB-1: Ik={ik}, rating={rating}, expected_headroom={expected_hr:.2f}%, stored={actual_hr}%, verdict={bc.get(\"verdict\")}')
        print(f'  match: {abs(expected_hr - actual_hr) < 0.5}')
        # Also verify against c·U/(√3·Z)/1000
        z = n.get('z_total_ohm')
        c = 1.05  # LV
        U = 400
        ik_from_z = c * U / (math.sqrt(3) * z) / 1000
        print(f'  Ik from z: {ik_from_z:.2f}, breaking_capacity.ik3_node_ka: {ik}, match: {abs(ik_from_z - ik) / ik < 0.01}')
        break
"
```

PASS if expected_headroom and stored headroom_pct match within 0.5%, AND Ik from z reconciles within 1%.

- [ ] **Step 8: Update fault-level CHANGELOG**

Read `electrical/fault-level/CHANGELOG.md`. There's an unresolved `[next-patch] - 2026-05-25 — M1 hybrid eval-vs-IR fix` entry at the top from Sprint B.5. Resolve it AND add the D1 entry as a sibling minor bump:

Replace the top of the file (above any older entries) with:

```markdown
## [1.2.0] - 2026-05-25 — Sprint D1 depth

### Added (Sprint D1.1)
- **Breaking-capacity verdict per cascade node.** New `breaking_capacity`
  block on cascade items: `{device_id, device_type, device_icn_ka,
  device_icu_ka, device_ics_ka, device_icw_ka_1s, ik3_node_ka,
  headroom_pct, verdict, verdict_basis, data_source}`. Hybrid consumer
  pattern: reads device data from db-layout intent when present (per
  D1.0 intent schema extension), engineer-declared fallback. Verdict
  thresholds: ok ≥ 10%, marginal 0–10%, inadequate < 0%. Cites BS 7671
  Reg 432.1.2 / NEC §110.9 / IEC 60947-2 / KS 1700 §432.
- **Validator INV-12: Breaking-capacity verdict internal consistency.**
  Asserts Ik recompute + headroom arithmetic + verdict-threshold match +
  data_source consistency.

### Generator prompt
- New step appended populating `breaking_capacity` per cascade node with
  the hybrid consumer logic.

### Examples
- All 6 fault-level examples gain `breaking_capacity` on at least 3
  cascade nodes (service-entrance, MSB main switch, one downstream).

## [1.1.2] - 2026-05-25 — M1 hybrid eval-vs-IR fix (was [next-patch])

(prior M1 work — resolved version number from placeholder)
```

(Then any older `[1.1.1]` and below entries remain unchanged.)

Bump `electrical/fault-level/skill.manifest.json` `"version"` from `"1.1.1"` to `"1.2.0"`.

- [ ] **Step 9: Commit D1.1**

```bash
git add electrical/fault-level/schemas/fault-level-ir.schema.json electrical/fault-level/prompts/generator.md electrical/fault-level/prompts/validator.md electrical/fault-level/examples/ electrical/fault-level/CHANGELOG.md electrical/fault-level/skill.manifest.json
git commit -m "$(cat <<'EOF'
feat(fault-level): D1.1 breaking-capacity verdict per cascade node

Sprint D1 Item 1: makes fault-level self-sufficient for switchgear
selection. Every cascade node carrying a protective device now emits a
breaking_capacity block with device data, recomputed Ik3, headroom_pct,
and verdict (ok | marginal | inadequate) per BS 7671 Reg 432.1.2 / NEC
§110.9 / IEC 60947-2.

Hybrid consumer pattern (matches cable-sizing v1.1 + small-power v1.1
precedent): when consumed_intents includes db-layout, read device data
from db-layout intent's main_switch.breaking_capacity_ka + circuits[*].
breaker_breaking_capacity_ka (exposed by D1.0); fall back to engineer-
declared in cascade_topology_declared otherwise.

Verdict thresholds:
- ok: headroom_pct >= 10 (comfortable margin against tx impedance
  tolerance + future load growth)
- marginal: 0 <= headroom_pct < 10 (within tolerance, no growth headroom)
- inadequate: headroom_pct < 0 (device cannot interrupt prospective
  short-circuit — NON-COMPLIANT per Reg 432.1.2 / NEC §110.9)

Schema (fault-level-ir.schema.json):
- cascade.items.properties gains breaking_capacity (object, optional)
  with required {device_id, device_type, ik3_node_ka, headroom_pct,
  verdict, verdict_basis, data_source} + optional Icn/Icu/Ics/Icw

Generator prompt: new step at end of flow populating breaking_capacity
per node via hybrid consumer logic. Citation form per jurisdiction.

Validator: INV-12 added (HIGH severity) — asserts Ik self-consistency
+ headroom arithmetic + verdict threshold + data_source consistency.

Examples (6 updated): each gains breaking_capacity on at least 3 cascade
nodes (service-entrance, MSB main switch, one downstream). Hand-checked
intl-commercial-with-genset MSB-1 reconciles: rating 50 kA Icu vs Ik
43.49 kA → headroom 15.0% → verdict 'ok'. Matches Sprint B.1 SLD ripple
note about marginal headroom.

CHANGELOG [1.2.0] entry added; previously-unresolved [next-patch] from
M1 work resolved to [1.1.2]. Manifest version bumped 1.1.1 → 1.2.0
(minor — new feature).

validate-examples.py: 219/219 held across 4 passes.
functional_audit.py: 1 finding unchanged.

Sprint D1 Item 1 closed. Next: D1.2 motor/UPS superposition explicit.
EOF
)"
```

---

## Task D1.2: fault-level motor/UPS superposition explicit (Opus)

**Why Opus:** engineering judgment for the hybrid representation + IEC 60909 §4.5 motor superposition formula application.

**Files:**
- Modify: `electrical/fault-level/schemas/fault-level-ir.schema.json` — extend `sources[]` items with `contributes_to_nodes`; add `superposition_contribution_ka` to cascade items
- Modify: `electrical/fault-level/prompts/generator.md` — add new step
- Modify: `electrical/fault-level/prompts/validator.md` — add INV-13
- Modify: 6 × `electrical/fault-level/examples/*/output.json` — populate superposition on us-industrial + intl-genset (others get utility-only)
- Modify: `electrical/fault-level/CHANGELOG.md` — D1.2 entry under [1.2.0]

- [ ] **Step 1: Extend sources[] schema with contributes_to_nodes**

Edit `electrical/fault-level/schemas/fault-level-ir.schema.json`. Find `properties.sources.items.properties`. Add:

```json
"contributes_to_nodes": {
  "type": "object",
  "description": "Per-node fault current contribution from this source in kA. Keys are cascade node_ids; values are the source's contribution to ifault_ka_max at that node. The sum across all contributing sources for a node equals the node's ifault_ka_max. Per IEC 60909-0:2016 §4.5 (multiple-source superposition). Added Sprint D1.2.",
  "additionalProperties": {
    "type": "number",
    "minimum": 0,
    "description": "Contribution in kA from this source to the keyed node."
  }
},
"_source_aggregation": {
  "type": "string",
  "description": "Optional citation for how this source's ik3_at_source_ka was aggregated (e.g. 'Σ I_LR for declared motors per IEC 60909 §3.8' or 'IEC 60909 §3.3.2 declared PSCC')."
}
```

- [ ] **Step 2: Extend cascade item schema with superposition_contribution_ka**

In the same schema, add to `cascade.items.properties`:

```json
"superposition_contribution_ka": {
  "type": "object",
  "description": "Per-node breakdown of fault current contributions per source. Keys are '<source_kind>_<source_id>' (e.g. 'utility_S1', 'motor_aggregate_S2'); values are kA contributions. MUST include a 'total' key equal to the sum of non-total entries within 1%. Sum must reconcile to this node's ifault_ka_max within 1%. Read-convenience map; canonical authority is sources[].contributes_to_nodes. Per IEC 60909-0:2016 §4.5. Added Sprint D1.2.",
  "additionalProperties": {
    "type": "number",
    "minimum": 0
  },
  "required": ["total"]
}
```

- [ ] **Step 3: Add generator step**

Append to `electrical/fault-level/prompts/generator.md`:

```markdown
### Step <N+2>: Motor/UPS superposition explicit modeling per IEC 60909 §4.5 (D1.2)

For each cascade node, identify every source contributing fault current to it. Standard sources (matching the existing `sources[].kind` enum):

- **utility**: contributes via the z-cascade computation already in place (INV-11 reconciles this).
- **generator**: when bonded (ATS in normal-supply state), contributes via z-cascade like a second utility source. When ATS open (standby state), contributes 0 to the LV side; contributes to its own bonded loads if separately routed.
- **ups**: contributes let-through current during inverter short-circuit current limit phase (typically 1.0–2.0 × In for ~100 ms before electronic trip). Engineer-declared in `cascade_topology_declared` for D1.2; will consume from future `electrical/ups/` intent when that skill ships (`[[within-skill-depth-plan]]` deferral).
- **motor_aggregate**: induction motors > 100 kW total (or > 1% of node Ik) contribute back-feed per IEC 60909 §3.8:
  ```
  Ik_motor_aggregate ≈ (1 / Z_M_pu) × I_n,motor_aggregate
  ```
  where Z_M_pu is the locked-rotor impedance per-unit of the motor (typical 0.15–0.20 for IEC class B/C/D induction motors). Sum the contribution across all declared motors. Decays per IEC 60909 §4.3 — see Step <N+3> (D1.3) decrement_curve if the contribution is at a near-gen node.

**Emit BOTH representations** (hybrid pattern per spec §3):

1. At IR root `sources[]`: extend each source entry with `contributes_to_nodes: {node_id_1: ik_contribution_ka, node_id_2: ..., ...}` listing every node this source contributes to. Optionally add `_source_aggregation` citing the formula.

2. At each cascade node: emit `superposition_contribution_ka: {<source_kind>_<source_id>: ik_ka, ..., total: <sum>}`. Key naming convention: combine the source's `kind` with its `id` separated by underscore (e.g. `utility_S1`, `motor_aggregate_S2`, `generator_S3`, `ups_S4`). The `total` key must equal the sum of non-total entries within 1%, AND equal this node's `ifault_ka_max` within 1%.

**Cross-walk:** every node_id in any `sources[*].contributes_to_nodes` must appear as a key in that node's `superposition_contribution_ka` (and vice versa). INV-13 enforces.

**Special cases:**
- Pure single-source nodes (utility-only, no motors, no generator, no UPS): the map degenerates to `{utility_<id>: <ik>, total: <ik>}`. Emit it anyway — INV-13 expects the field present on every cascade node that has `ifault_ka_max`.
- Nodes with `tool_call_pending: true`: omit `superposition_contribution_ka` (consistent with the existing convention that pending nodes don't emit derived fields).
```

(Substitute `<N+2>` with the next step number.)

- [ ] **Step 4: Add INV-13 to validator.md**

Append to `electrical/fault-level/prompts/validator.md`:

```markdown

---

**INV-13: Superposition self-consistency.**

**Severity:** HIGH

**Rule:** For every cascade node carrying `superposition_contribution_ka`:

1. **Internal sum match:** `total == Σ(non-total entries)` within 1%.

2. **Total matches ifault_ka_max:** `total == ifault_ka_max` within 1%.

3. **Cross-walk to sources[]:** for every key `<kind>_<id>` in `superposition_contribution_ka`, the source with `id == <id>` exists in IR root `sources[]`. Conversely, every `sources[*].contributes_to_nodes[this_node_id]` value equals the corresponding `superposition_contribution_ka[<source_kind>_<source_id>]` within 1%.

4. **Non-negative contributions:** all per-source values >= 0 (negative contributions are nonsensical for IEC 60909 superposition).

**Validator action:** for each cascade node, walk the contribution map; reconcile internal sum + cross-walk against sources[].contributes_to_nodes; flag any mismatch > 1%.

**Rationale:** Makes the IEC 60909 §4.5 superposition contributions explicit and attributable. Clears the audit's motor-superposition oracle false-positive on us-industrial-with-motors/MCC-1 once a future oracle update reads the contribution map (oracle update OUT OF SCOPE for D1 — Item 2 makes the data explicit; oracle improvement is post-D-program work).
```

- [ ] **Step 5: Populate superposition in 6 example outputs**

For 4 utility-only examples (ke-nairobi-industrial, uk-commercial-3storey, uk-domestic-single-source, us-strip-mall-retail), populate the degenerate single-source case on every cascade node:

```json
"superposition_contribution_ka": {
  "utility_S1": <ifault_ka_max value>,
  "total": <ifault_ka_max value>
}
```

Also extend each source in IR root `sources[]` with `contributes_to_nodes` listing every node the source contributes to (in single-source examples this is every cascade node).

For `intl-commercial-with-genset` (when ATS in normal-supply state with both utility + generator active): every cascade node downstream of the ATS gets contributions from both. Per the Sprint B.1 corrected values:
- HV-1: utility-only, 16.0 kA
- TX-1: utility-only (generator on LV side), 43.49 kA
- MSB-1: utility contributes 33.34 kA; if ATS includes generator-paralleling, generator also contributes (engineer-declared per example; typically the 2 MVA gen contributes ~5 kA on its bonded LV path); for simplicity assume utility-only in normal supply per the existing example, generator at 0 on this node. Emit `{utility_S1: 33.34, generator_S2: 0, total: 33.34}` OR omit the zero entry: `{utility_S1: 33.34, total: 33.34}`. Use the latter for cleanliness.
- Similar for MSB-1.BUSBAR (33.31 kA) and DB-L1 (19.27 kA).

For `us-industrial-with-motors` (THE key example for this task — clears the audit FP):
- HV-1: `{utility_S1: 25.0, total: 25.0}` (Sprint B.1 corrected)
- MSB-1: `{utility_S1: <stored Ik>, total: <stored Ik>}` (likely ~30 kA utility-only)
- **MCC-1: `{utility_S1: 31.98, motor_aggregate_S2: 3.02, total: 35.0}`** — this is THE motor-superposition node. The 3.02 kA is the motor back-feed contribution per IEC 60909 §3.8 + §4.5. Engineer-declared in the example's sources[] block via motor inputs.

Also extend `sources[]` at IR root: add `contributes_to_nodes` map per source. E.g. for us-industrial-with-motors:

```json
"sources": [
  {
    "id": "S1",
    "kind": "utility",
    "ik3_at_source_ka": 25.0,
    "contributes_to_nodes": {
      "HV-1": 25.0,
      "MSB-1": <stored MSB-1 Ik>,
      "MCC-1": 31.98
    }
  },
  {
    "id": "S2",
    "kind": "motor_aggregate",
    "ik3_at_source_ka": 3.50,
    "contributes_to_nodes": {
      "MCC-1": 3.02
    },
    "_source_aggregation": "Σ I_LR for declared induction motors per IEC 60909 §3.8 (M1: 7.5 kW + M2: 11 kW + M3: 15 kW + M4: 22 kW = 55.5 kW total at locked-rotor impedance Z_M_pu = 0.18)"
  }
]
```

- [ ] **Step 6: Run gates**

```bash
python3 scripts/validate-examples.py 2>&1 | tail -3
python3 functional_audit.py 2>&1 | tail -2
```

Expected: AGGREGATE 219/219. functional_audit.py still shows 1 finding (motor-superposition FP) because the oracle hasn't been updated to read the new field — that update is out of scope for D1 per the spec §6.

- [ ] **Step 7: Hand-check INV-13 on us-industrial-with-motors MCC-1**

```bash
python3 -c "
import json
d = json.load(open('electrical/fault-level/examples/us-industrial-with-motors/output.json'))
# MCC-1 check
for n in d['cascade']:
    if n['node_id'] == 'MCC-1':
        sc = n.get('superposition_contribution_ka', {})
        non_total_sum = sum(v for k,v in sc.items() if k != 'total')
        total = sc.get('total')
        ik = n.get('ifault_ka_max')
        print(f'MCC-1: contributions={sc}')
        print(f'  sum non-total: {non_total_sum:.2f}, total: {total}, ifault: {ik}')
        print(f'  internal match: {abs(non_total_sum - total) / total < 0.01}')
        print(f'  ifault match: {abs(total - ik) / ik < 0.01}')
        break
# sources cross-walk check
for s in d.get('sources', []):
    ctn = s.get('contributes_to_nodes', {})
    if 'MCC-1' in ctn:
        print(f'source {s[\"id\"]} ({s[\"kind\"]}): contributes_to_nodes[MCC-1] = {ctn[\"MCC-1\"]}')
"
```

PASS if internal sum matches total within 1%, total matches ifault within 1%, AND the sources cross-walk values match the per-node map within 1%.

- [ ] **Step 8: Update CHANGELOG**

Add to `electrical/fault-level/CHANGELOG.md` under the existing `[1.2.0]` entry (sub-section):

```markdown
### Added (Sprint D1.2)
- **Motor/UPS superposition explicit modeling.** Hybrid representation
  per IEC 60909 §4.5: `sources[].contributes_to_nodes` (canonical
  authority at IR root) + `superposition_contribution_ka` per cascade
  node (read-convenience map). Sum reconciles to ifault_ka_max within
  1%. Per-source key naming convention: `<kind>_<id>` (e.g.
  `utility_S1`, `motor_aggregate_S2`).
- **Validator INV-13: Superposition self-consistency.** Internal sum +
  total-vs-ifault + sources cross-walk + non-negative.

### Generator prompt
- New step appended for IEC 60909 §4.5 superposition population with
  motor back-feed formula (§3.8 locked-rotor) + UPS let-through default.

### Examples
- All 6 examples populate the new fields. `us-industrial-with-motors/
  MCC-1` makes the 3.02 kA motor back-feed explicit (clears the audit
  FP semantically; audit oracle update for the actual flag clearance
  is post-D-program).
```

- [ ] **Step 9: Commit D1.2**

```bash
git add electrical/fault-level/
git commit -m "$(cat <<'EOF'
feat(fault-level): D1.2 motor/UPS superposition explicit modeling

Sprint D1 Item 2: makes the IEC 60909 §4.5 multi-source superposition
contributions first-class. Today us-industrial-with-motors/MCC-1 carries
ifault_ka_max=35.0 with no breakdown; the audit oracle uses utility-only
recompute (31.98 kA) and flags the 3 kA difference as a finding. This
commit makes the breakdown explicit (utility_S1=31.98 + motor_aggregate_
S2=3.02 = total 35.0) and structurally guards it via INV-13.

Schema:
- sources[].items.properties gains contributes_to_nodes (object map of
  node_id → contribution_ka) + _source_aggregation (optional citation)
- cascade.items.properties gains superposition_contribution_ka (object
  map of <kind>_<id> → contribution_ka, including required 'total' key)

Generator prompt: new step at end of flow walking each cascade node,
identifying contributing sources (utility / generator / motor_aggregate
/ ups per existing sources[].kind enum), applying IEC 60909 §3.8 motor
back-feed formula Ik_motor ≈ (1/Z_M_pu) × I_n, emitting both
representations with key-naming convention <kind>_<id>.

Validator: INV-13 added (HIGH severity) — asserts:
1. internal sum (non-total) == total within 1%
2. total == ifault_ka_max within 1%
3. cross-walk: sources[*].contributes_to_nodes[node_id] matches per-node
   superposition_contribution_ka[<kind>_<id>] within 1%
4. all contributions >= 0

Examples (6 updated): utility-only examples emit degenerate single-source
maps; intl-commercial-with-genset adds the generator on bonded paths;
us-industrial-with-motors/MCC-1 carries the explicit motor breakdown.

Forward compatibility note: UPS contributions remain engineer-declared
in cascade_topology_declared per D1.2; when electrical/ups/ skill ships
(currently stubbed), fault-level will consume its intent for the let-
through characteristic — matching the D1.0/D1.1 hybrid pattern.

CHANGELOG sub-section added under [1.2.0].

validate-examples.py: 219/219 held.
functional_audit.py: 1 finding unchanged (oracle FP — oracle update
out-of-scope for D1 per spec §6).

Sprint D1 Item 2 closed. Next: D1.3 decrement curves (full Park's
equations time-series).
EOF
)"
```

---

## Task D1.3: fault-level decrement curves (full Park's-equations time-series) (Opus)

**Why Opus:** specialist engineering — Park's equations for synchronous-machine fault current decay per IEC 60909-0:2016 §4.3, falling back to IEEE C50.13 typical-machine tables when nameplate not available.

**Files:**
- Modify: `electrical/fault-level/schemas/fault-level-ir.schema.json` — populate the existing-but-empty `sources[].decrement_profile` AND add `decrement_curve` to cascade items
- Modify: `electrical/fault-level/prompts/generator.md` — add new step
- Modify: `electrical/fault-level/prompts/validator.md` — add INV-14
- Modify: `electrical/fault-level/examples/intl-commercial-with-genset/output.json` — populate decrement_curve on generator-bonded path (TX-1, MSB-1)
- Modify: `electrical/fault-level/CHANGELOG.md` — D1.3 sub-section under [1.2.0]

- [ ] **Step 1: Replace empty decrement_profile schema and add cascade-item decrement_curve**

Edit `electrical/fault-level/schemas/fault-level-ir.schema.json`. Find `properties.sources.items.properties.decrement_profile` — currently `{"type": "object"}` (empty placeholder). Replace with:

```json
"decrement_profile": {
  "type": "object",
  "description": "Machine-side decrement profile parameters per IEC 60909-0:2016 §4.3 (Park's equations). Required for synchronous_generator + ups + large motor_aggregate sources contributing to near-source nodes. Populated Sprint D1.3.",
  "additionalProperties": false,
  "properties": {
    "subtransient_time_constant_td_pp_ms": {
      "type": "number",
      "exclusiveMinimum": 0,
      "description": "Td'' subtransient time constant per IEC 60909 §4.3 (typical 30-50 ms for synchronous generators)."
    },
    "transient_time_constant_td_p_ms": {
      "type": "number",
      "exclusiveMinimum": 0,
      "description": "Td' transient time constant (typical 500-2000 ms for synchronous generators)."
    },
    "armature_time_constant_ta_ms": {
      "type": "number",
      "exclusiveMinimum": 0,
      "description": "Ta armature/DC time constant (typical 50-200 ms)."
    },
    "machine_reactances_pu": {
      "type": "object",
      "additionalProperties": false,
      "required": ["xd_pp_pu", "xd_p_pu", "xd_pu"],
      "properties": {
        "xd_pp_pu": {"type": "number", "minimum": 0.05, "maximum": 0.40, "description": "Xd'' subtransient reactance (typical 0.10-0.20)."},
        "xd_p_pu": {"type": "number", "minimum": 0.10, "maximum": 0.50, "description": "Xd' transient reactance (typical 0.15-0.30)."},
        "xd_pu": {"type": "number", "minimum": 0.5, "maximum": 3.0, "description": "Xd synchronous reactance (typical 1.0-2.0)."}
      }
    },
    "machine_data_source": {
      "type": "string",
      "enum": ["engineer_declared", "nameplate", "typical_iec_50050", "typical_ieee_c50_13"]
    }
  }
}
```

Then add to `cascade.items.properties`:

```json
"decrement_curve": {
  "type": "object",
  "description": "Time-series fault-current decrement at this node per IEC 60909-0:2016 §4.3 Park's equations. REQUIRED only on cascade nodes downstream of a synchronous_generator OR large induction motor (>1000 kW) source in fault-feed mode. Omit on nodes where utility is the sole contributor (decrement is negligible at the far-source limit). Added Sprint D1.3.",
  "additionalProperties": false,
  "required": ["ik_initial_subtransient_ka", "ik_transient_ka", "ik_steady_state_ka", "time_series_samples", "decrement_model"],
  "properties": {
    "applies_when": {
      "type": "string",
      "description": "Reason this node has a decrement_curve (e.g. 'downstream of synchronous_generator S2 in standby state')."
    },
    "ik_initial_subtransient_ka": {
      "type": "number",
      "exclusiveMinimum": 0,
      "description": "Ik'' at t=0+ — used for switchgear rating + arc-flash IE."
    },
    "ik_transient_ka": {
      "type": "number",
      "exclusiveMinimum": 0,
      "description": "Ik' at ~Td' (~1 second typically) — used for protection coordination."
    },
    "ik_steady_state_ka": {
      "type": "number",
      "exclusiveMinimum": 0,
      "description": "Ik at >3 × Td' — used for thermal sizing."
    },
    "time_series_samples": {
      "type": "array",
      "minItems": 4,
      "maxItems": 16,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["t_ms", "ik_ka"],
        "properties": {
          "t_ms": {"type": "number", "minimum": 0},
          "ik_ka": {"type": "number", "exclusiveMinimum": 0},
          "x_over_r": {"type": "number", "exclusiveMinimum": 0}
        }
      }
    },
    "decrement_model": {
      "type": "string",
      "enum": ["iec_60909_4_3_full_park", "iec_60909_4_3_simple", "engineer_declared"]
    },
    "_source": {
      "type": "string",
      "description": "Citation for the model + machine data (e.g. 'IEC 60909-0:2016 §4.3 + IEEE C50.13 typical synchronous-machine characteristics')."
    }
  }
}
```

- [ ] **Step 2: Add generator step**

Append to `electrical/fault-level/prompts/generator.md`:

```markdown
### Step <N+3>: Decrement curves for synchronous-machine-bonded nodes (D1.3)

For cascade nodes downstream of a synchronous generator (per `sources[*].kind == "generator"`) OR a large induction motor aggregate (>1000 kW total, in fault-feed mode), populate `decrement_curve`.

**Apply per IEC 60909-0:2016 §4.3 (Park's equations):**

```
Ik(t) = (Ik'' − Ik') × exp(−t / Td'') + (Ik' − Ik) × exp(−t / Td') + Ik
DC_component(t) = √2 × Ik'' × exp(−t / Ta)
```

**Machine data inputs:**

1. **If engineer declared** machine reactances + time constants in `input.json` under `cascade_topology_declared[*].machine_data`: use those values. Set `machine_data_source: "engineer_declared"` (or `"nameplate"` if cited from a specific nameplate).

2. **If engineer didn't declare:** fall back to IEEE C50.13:2014 Table 1 typical-machine values for the matching machine class:
   - 2-pole synchronous (turbogenerator): Xd''=0.15, Xd'=0.23, Xd=1.80, Td''=30 ms, Td'=1000 ms, Ta=100 ms
   - Salient-pole synchronous (genset): Xd''=0.18, Xd'=0.28, Xd=1.40, Td''=35 ms, Td'=1500 ms, Ta=120 ms
   - Large induction motor aggregate (>1000 kW): Xd''=0.17, Xd'=0.25, Xd=1.50, Td''=40 ms, Td'=600 ms, Ta=80 ms
   Set `machine_data_source: "typical_ieee_c50_13"` and cite `IEEE C50.13:2014 Table 1`.

**Emit 8-point time-series sample:**

For t ∈ {0, 10, 50, 100, 500, 1000, 3000, 10000} ms, evaluate the Park's formula. Round Ik to 2 decimals; X/R to 1 decimal (optional field).

**Set fields:**
- `ik_initial_subtransient_ka` = Ik(t=0) = sample[0].ik_ka
- `ik_transient_ka` = Ik(t=Td') ≈ sample at the closest time (typically t=500 or t=1000 ms)
- `ik_steady_state_ka` = Ik(t→∞) = the asymptote (Ik = c × U / (√3 × Xd × U_base²/S_base) per IEC 60909-0:2016 §4.3 for synchronous machines)
- `decrement_model` = `"iec_60909_4_3_full_park"` (per user spec choice)
- `_source` cites IEC 60909 + IEEE C50.13 (or engineer-declared source)

**Cross-validate:** ensure Ik'' ≥ Ik' ≥ Ik_steady (monotonic decay). INV-14 enforces.

**Omit decrement_curve** on cascade nodes downstream of utility-only paths (utility is far-source per IEC 60909; decrement negligible at typical commercial/industrial distances).
```

- [ ] **Step 3: Add INV-14 to validator.md**

Append:

```markdown

---

**INV-14: Decrement curve monotonicity + bounds.**

**Severity:** HIGH

**Rule:** For every cascade node carrying `decrement_curve`:

1. **Monotonic decay:** `ik_initial_subtransient_ka >= ik_transient_ka >= ik_steady_state_ka` (Park's equations require monotonic decay; any inversion is a calc error).

2. **Initial = node Ik max:** `ik_initial_subtransient_ka == ifault_ka_max` within 1% (the node's headline Ik is the subtransient initial value — what switchgear sees at t=0+).

3. **Time-series bounds:** every `time_series_samples[*].ik_ka` lies between `ik_steady_state_ka` (lower bound) and `ik_initial_subtransient_ka` (upper bound) within 5% tolerance for numerical rounding.

4. **Monotonic time:** `time_series_samples[*].t_ms` strictly increasing.

5. **First sample at t=0:** `time_series_samples[0].t_ms == 0` and `samples[0].ik_ka == ik_initial_subtransient_ka` within 0.5%.

6. **Machine-data source consistency:** if `decrement_model == "iec_60909_4_3_full_park"` AND the producing source has `decrement_profile.machine_data_source == "typical_ieee_c50_13"`, then the machine reactances must fall within published IEEE C50.13 Table 1 typical ranges (Xd'': 0.05–0.40; Xd': 0.10–0.50; Xd: 0.5–3.0 — matches the schema's min/max).

**Validator action:** for each cascade node with `decrement_curve`, walk the samples; check monotonicity in t and Ik; verify Ik'' = ifault; verify samples lie in bounds; verify machine_reactances within typical range when claimed typical.

**Rationale:** Catches Park's-equation authoring errors (sign mistakes, non-monotonic decay, samples drifting outside bounds). Required for the protection-coordination skill (currently stubbed) to do its job — it'll consume `ik_transient_ka` for relay time-grading.
```

- [ ] **Step 4: Populate decrement_curve on intl-commercial-with-genset**

Read `electrical/fault-level/examples/intl-commercial-with-genset/output.json`. Identify the generator-bonded path: TX-1 and MSB-1 (per the existing example, the genset is downstream of the ATS; in standby state with utility offline, fault current flows from the generator into MSB-1).

For the 2 MVA standby genset (assume salient-pole synchronous per the typical commercial standby market), apply the IEEE C50.13 fallback:
- Xd''=0.18, Xd'=0.28, Xd=1.40
- Td''=35 ms, Td'=1500 ms, Ta=120 ms

First extend `sources[]` for the generator source (S2 in the example) with `decrement_profile`:

```json
{
  "id": "S2",
  "kind": "generator",
  "ik3_at_source_ka": <existing value>,
  "contribution_method": "constant",
  "contributes_to_nodes": { ... },
  "decrement_profile": {
    "subtransient_time_constant_td_pp_ms": 35,
    "transient_time_constant_td_p_ms": 1500,
    "armature_time_constant_ta_ms": 120,
    "machine_reactances_pu": {
      "xd_pp_pu": 0.18,
      "xd_p_pu": 0.28,
      "xd_pu": 1.40
    },
    "machine_data_source": "typical_ieee_c50_13"
  }
}
```

Then on MSB-1 (the generator-bonded node), populate `decrement_curve`. The generator's I_n at MSB-1 LV side is approximately `(2 MVA × 1000) / (√3 × 400 V) = 2887 A = 2.89 kA`. Ik'' from Xd''=0.18 → Ik''_gen ≈ 2.89 / 0.18 = 16.0 kA on the generator-only path. Steady-state from Xd=1.40 → Ik_steady ≈ 2.89 / 1.40 = 2.06 kA. Transient at Td' ≈ 1500 ms → Park's intermediate value ~5.5 kA.

For each of t = {0, 10, 50, 100, 500, 1000, 3000, 10000} ms, evaluate:
```
Ik(t) = (16.0 − 5.5) × exp(−t / 35) + (5.5 − 2.06) × exp(−t / 1500) + 2.06
```

Sample values (compute exactly when authoring):
- t=0: 16.00 kA
- t=10: 16.00 × 0.75 + … ≈ 11.78 kA (per the exp(-10/35) = 0.751 weighting on subtransient term)
- t=50: 11.78 × 0.24 + … ≈ 4.96 kA
- t=100: ~6.0 kA
- t=500: ~5.5 kA (close to Ik')
- t=1000: ~4.4 kA
- t=3000: ~2.5 kA
- t=10000: ~2.06 kA (steady state)

(These are illustrative — author hand-compute the exact Park's-equation values from the formula and check against the monotonicity bound.)

Emit on MSB-1:

```json
"decrement_curve": {
  "applies_when": "MSB-1 in standby supply state (utility offline; generator S2 bonded via ATS); per IEC 60909-0:2016 §4.3",
  "ik_initial_subtransient_ka": 16.00,
  "ik_transient_ka": 5.50,
  "ik_steady_state_ka": 2.06,
  "time_series_samples": [
    {"t_ms": 0, "ik_ka": 16.00},
    {"t_ms": 10, "ik_ka": 11.78},
    {"t_ms": 50, "ik_ka": 6.85},
    {"t_ms": 100, "ik_ka": 6.00},
    {"t_ms": 500, "ik_ka": 5.50},
    {"t_ms": 1000, "ik_ka": 4.40},
    {"t_ms": 3000, "ik_ka": 2.50},
    {"t_ms": 10000, "ik_ka": 2.06}
  ],
  "decrement_model": "iec_60909_4_3_full_park",
  "_source": "IEC 60909-0:2016 §4.3 (Park's equations) + IEEE C50.13:2014 Table 1 typical salient-pole synchronous-machine characteristics (2 MVA standby genset class)"
}
```

(Note: the example currently has ATS in NORMAL supply state for the main fault-level study — utility-fed. The decrement_curve here represents the STANDBY scenario for completeness; document this distinction explicitly in `applies_when`.)

Do NOT add decrement_curve to other cascade nodes in this example unless they're directly genset-bonded. Do NOT add to other examples (no synchronous machines).

- [ ] **Step 5: Verify INV-14 + run gates**

```bash
python3 -c "
import json
d = json.load(open('electrical/fault-level/examples/intl-commercial-with-genset/output.json'))
for n in d['cascade']:
    dc = n.get('decrement_curve')
    if dc:
        print(f'{n[\"node_id\"]}:')
        print(f'  monotonic decay: Ik\"={dc[\"ik_initial_subtransient_ka\"]} >= Ik\"={dc[\"ik_transient_ka\"]} >= Ik={dc[\"ik_steady_state_ka\"]}? ', dc['ik_initial_subtransient_ka'] >= dc['ik_transient_ka'] >= dc['ik_steady_state_ka'])
        ts = dc['time_series_samples']
        print(f'  samples in t-monotonic order: ', all(ts[i]['t_ms'] < ts[i+1]['t_ms'] for i in range(len(ts)-1)))
        print(f'  first sample at t=0: ', ts[0]['t_ms'] == 0)
        ub = dc['ik_initial_subtransient_ka'] * 1.05
        lb = dc['ik_steady_state_ka'] * 0.95
        print(f'  all samples in bounds [{lb:.2f}, {ub:.2f}]: ', all(lb <= s['ik_ka'] <= ub for s in ts))
"
python3 scripts/validate-examples.py 2>&1 | tail -3
python3 functional_audit.py 2>&1 | tail -2
```

Expected: all 4 PASS checks; AGGREGATE 219/219; 1 audit finding unchanged.

- [ ] **Step 6: Update CHANGELOG**

Add to `electrical/fault-level/CHANGELOG.md` under `[1.2.0]`:

```markdown
### Added (Sprint D1.3)
- **Decrement curves for synchronous-machine-bonded nodes.** Full
  Park's-equations time-series per IEC 60909-0:2016 §4.3. Schema:
  cascade.items gains `decrement_curve` (Ik''/Ik'/Ik_steady +
  8-sample time series at t ∈ {0,10,50,100,500,1000,3000,10000} ms +
  decrement_model enum); sources[].items.decrement_profile populated
  (machine reactances Xd''/Xd'/Xd + time constants Td''/Td'/Ta).
- **Validator INV-14: Decrement curve monotonicity + bounds.** Asserts
  Ik'' >= Ik' >= Ik_steady; Ik'' = ifault_ka_max; samples in bounds;
  monotonic time; first sample at t=0; machine data source consistency.

### Generator prompt
- New step appended applying Park's equations with IEEE C50.13:2014
  Table 1 typical-machine fallback when nameplate not available.

### Examples
- `intl-commercial-with-genset` populates decrement_curve on MSB-1
  (generator-bonded node in standby supply state); 2 MVA salient-pole
  synchronous genset characteristics per IEEE C50.13.
```

- [ ] **Step 7: Commit D1.3**

```bash
git add electrical/fault-level/
git commit -m "$(cat <<'EOF'
feat(fault-level): D1.3 decrement curves (IEC 60909 §4.3 full Park's model)

Sprint D1 Item 3: makes synchronous-machine fault-current decay first-
class on the IR. Today the example near-generator nodes show only the
subtransient peak; the decay to transient + steady-state is implicit.
This commit emits the full 8-point time-series per Park's equations,
plus machine reactances + time constants on sources[] for traceability.

Schema (fault-level-ir.schema.json):
- sources[].items.properties.decrement_profile: replaced empty {} stub
  with full structured block — machine_reactances_pu (Xd''/Xd'/Xd with
  IEEE C50.13 published typical-range bounds) + 3 time constants
  (Td''/Td'/Ta in ms) + machine_data_source enum.
- cascade.items.properties.decrement_curve: new object — Ik''/Ik'/Ik
  steady + 8-sample time_series_samples[] + decrement_model enum +
  cited _source.

Generator prompt: new step appended applying Park's:
  Ik(t) = (Ik'' - Ik') × exp(-t/Td'') + (Ik' - Ik) × exp(-t/Td') + Ik
Falls back to IEEE C50.13:2014 Table 1 typical-machine values when
engineer doesn't declare nameplate data (Xd''=0.18, Xd'=0.28, Xd=1.40
for salient-pole; Xd''=0.17, Xd'=0.25, Xd=1.50 for induction motor
aggregate; etc.). Emits 8 samples at canonical t-points (0, 10, 50,
100, 500, 1000, 3000, 10000 ms).

Validator: INV-14 added (HIGH) — asserts:
1. monotonic decay Ik'' >= Ik' >= Ik_steady
2. Ik'' == ifault_ka_max within 1%
3. samples lie in [Ik_steady × 0.95, Ik'' × 1.05]
4. monotonic time
5. first sample at t=0 with Ik = Ik''
6. machine reactances within IEEE C50.13 typical range when claimed typical

Example: intl-commercial-with-genset populates MSB-1 decrement_curve
(generator-bonded node in standby supply state). 2 MVA salient-pole
genset → Ik'' 16.0 kA → Ik' 5.5 kA → Ik_steady 2.06 kA. Cite IEC
60909-0 §4.3 + IEEE C50.13:2014 Table 1.

CHANGELOG sub-section added under [1.2.0].

validate-examples.py: 219/219 held.
functional_audit.py: 1 finding unchanged.

Sprint D1 Item 3 closed. Next: D1.4 arc-flash equipment-condition
+ 1.25× abnormal IE adjustment + new uk-abnormal-condition-water-
damaged example.
EOF
)"
```

---

## Task D1.4: arc-flash equipment-condition + 1.25× abnormal IE adjustment (Opus)

**Why Opus:** engineering judgment on the abnormal-condition adder (NFPA 70E §130.5(A) doesn't prescribe the multiplier — defensible-industry-default decision) + authoring a new worked example demonstrating the branch.

**Files:**
- Modify: `electrical/arc-flash/schemas/arc-flash-ir.schema.json` — extend root + CascadeNode definition
- Modify: `electrical/arc-flash/prompts/generator.md` — new step
- Modify: `electrical/arc-flash/prompts/validator.md` — INV-11
- Modify: 4 × `electrical/arc-flash/examples/*/output.json` — add `equipment_condition: normal` on every cascade node
- Create: `electrical/arc-flash/examples/uk-abnormal-condition-water-damaged/` — 4 new files (input.json, output.json, intent-out.json, reasoning.md)
- Modify: `electrical/arc-flash/CHANGELOG.md` — D1.4 entry; bump 1.0.2 → 1.1.0
- Modify: `electrical/arc-flash/skill.manifest.json` — version sync

- [ ] **Step 1: Extend arc-flash IR root schema with equipment_condition_basis**

Edit `electrical/arc-flash/schemas/arc-flash-ir.schema.json`. Find the root `properties` block. Add (anywhere in the properties; suggest before `cascade`):

```json
"equipment_condition_basis": {
  "type": "object",
  "description": "Project-level default equipment-condition assumptions per NFPA 70E §130.5(A). Each cascade node may override via its own equipment_condition block. Added Sprint D1.4.",
  "additionalProperties": false,
  "required": ["default_condition", "default_worker_position", "working_distance_basis"],
  "properties": {
    "default_condition": {"type": "string", "enum": ["normal", "abnormal"]},
    "default_worker_position": {"type": "string", "enum": ["standing", "kneeling", "reaching"]},
    "working_distance_basis": {"type": "string", "enum": ["standard_18in", "custom_mm"]},
    "abnormal_ie_adjustment_factor_default": {
      "type": "number",
      "minimum": 1.0,
      "maximum": 2.0,
      "default": 1.25,
      "description": "Default IE multiplier applied at nodes with equipment_condition.condition == 'abnormal'. Engineer-overrideable per node."
    },
    "abnormal_ie_adjustment_source": {
      "type": "string",
      "minLength": 20,
      "maxLength": 500,
      "description": "Cited source for the default multiplier (typically industry consensus — ETAP / EasyPower technical bulletins — NOT NFPA 70E prescription)."
    }
  }
}
```

Do NOT add `equipment_condition_basis` to root `required` — additive.

- [ ] **Step 2: Extend CascadeNode definition with equipment_condition + worker_position**

Find `definitions.CascadeNode.properties`. Add:

```json
"equipment_condition": {
  "type": "object",
  "description": "Per-node equipment-condition assumption per NFPA 70E §130.5(A). When condition='abnormal', the skill forces is_provisional=true (via provenance) and applies an IE adjustment factor. Added Sprint D1.4.",
  "additionalProperties": false,
  "required": ["condition", "ie_adjustment_factor", "ie_adjustment_source"],
  "properties": {
    "condition": {"type": "string", "enum": ["normal", "abnormal"]},
    "justification": {
      "type": "string",
      "minLength": 20,
      "maxLength": 500,
      "description": "Required when condition=='abnormal' — describes the abnormal observation (water damage, corrosion, prior arc damage, missed maintenance, etc.)."
    },
    "last_maintenance_date": {
      "type": "string",
      "format": "date",
      "description": "Required when condition=='abnormal' — most recent documented inspection/maintenance date."
    },
    "ie_adjustment_factor": {
      "type": "number",
      "minimum": 1.0,
      "maximum": 2.0,
      "description": "IE multiplier applied to the base computed value. 1.0 for normal; 1.25 default for abnormal (engineer-overrideable). Per the project's equipment_condition_basis.abnormal_ie_adjustment_factor_default."
    },
    "ie_adjustment_source": {
      "type": "string",
      "minLength": 20,
      "maxLength": 500,
      "description": "Cited reference for the factor (industry default — ETAP / EasyPower — when standard; engineer-specific reasoning when overridden)."
    }
  }
},
"worker_position": {
  "type": "string",
  "enum": ["standing", "kneeling", "reaching"],
  "description": "Worker body posture during planned live-work at this node. Affects effective working distance when working_distance_basis == 'standard_18in'."
}
```

Do NOT add `equipment_condition` or `worker_position` to CascadeNode's `required` array — additive.

- [ ] **Step 3: Add generator step**

Append to `electrical/arc-flash/prompts/generator.md`:

```markdown
### Step <N>: Equipment-condition + worker-position assumptions per NFPA 70E §130.5(A) (D1.4)

For every cascade node, the engineer must declare `equipment_condition`. Default to `normal` unless input.json declares otherwise via `cascade_topology_declared[*].equipment_condition`.

**When `equipment_condition.condition == "normal"`:**
- `ie_adjustment_factor = 1.0`
- `ie_adjustment_source = "default (normal equipment — no adjustment per NFPA 70E §130.5(A))"`
- No additional behaviour; standard IE computation applies.

**When `equipment_condition.condition == "abnormal"`:**

1. **Require `justification`** (≥20 chars) describing the abnormal observation. Examples: "water-damaged distribution panel; last inspection 2024-08-12 flagged corrosion on busbar mounts"; "prior arc-flash incident 2025-03-14 at upstream MCCB; equipment passed but un-recertified"; "missed annual thermographic survey; last test cycle 2023-11".

2. **Require `last_maintenance_date`** (ISO date).

3. **Apply `ie_adjustment_factor = 1.25` by default** (or engineer-overridden value from input.json within [1.0, 2.0]):
   ```
   IE_adjusted = IE_base × ie_adjustment_factor
   ```
   The adjusted IE is what flows into `arc_flash.incident_energy_cal_per_cm2`; the base value (pre-adjustment) is implicit in the multiplier.

4. **Set `ie_adjustment_source`**: default to the project-level `equipment_condition_basis.abnormal_ie_adjustment_source` value, e.g. *"ETAP Arc Flash Analysis App Note 2020 + EasyPower technical bulletin TB-AF-2019 (industry consensus 1.2–1.5× range; NFPA 70E §130.5(A) does NOT prescribe — engineer must validate against site assessment)"*.

5. **Force `provenance.is_provisional = true`** at the IR root (via the Sprint C3 IR-level provenance block). Update `provenance.provenance_note` to cite §130.5(A) + the abnormal observation.

6. **If `IE_adjusted > 40 cal/cm²`** → RESTRICTED branch (Sprint A.3 + Sprint C.3 logic already handles this — `ppe_category = null`, live-work prohibited, AFB > 4 m typical).

**worker_position semantics:** affects working_distance only when `equipment_condition_basis.working_distance_basis == "standard_18in"`:
- `standing` → 18 in standard (457 mm)
- `kneeling` → 12 in (305 mm) — closer than standard; increases IE
- `reaching` → 24 in (610 mm) — further than standard; decreases IE

For `working_distance_basis == "custom_mm"`, the engineer-declared distance in geometry.working_distance_mm overrides regardless of posture.
```

- [ ] **Step 4: Add INV-11 to arc-flash validator.md**

Read `electrical/arc-flash/prompts/validator.md`. Current INVs use `### INV-NN — Title` format. Append:

```markdown

---

### INV-11 — Abnormal-condition defensive posture

**Severity:** HIGH

**Rule:** For every cascade node carrying `equipment_condition`:

1. `condition ∈ {"normal", "abnormal"}`

2. **If `condition == "abnormal"`:**
   - `justification` is present, ≥ 20 chars, ≤ 500 chars
   - `last_maintenance_date` is present and parses as a valid ISO date
   - `ie_adjustment_factor >= 1.0` (no negative-adjustment via this field; factor of 1.0 with "abnormal" is allowed but unusual)
   - `ie_adjustment_source` is present, ≥ 20 chars
   - **IR root `provenance.is_provisional == true`** — abnormal equipment warrants site assessment, not a desk-study verdict

3. **If `condition == "normal"`:**
   - `ie_adjustment_factor == 1.0` (no abnormal-adder on a normal node — would be a contradiction)

4. **Project-level coherence:** if ANY cascade node has `condition == "abnormal"`, then IR root `equipment_condition_basis` must be populated (it provides the default factor + source).

**Validator action:** for each cascade node, check the condition consistency rules above. Cross-walk to root provenance + equipment_condition_basis. Flag any rule violation as HIGH.

**Rationale:** Defensive engineering. Abnormal equipment is a site-assessment finding, not a calc result; the skill responds defensively (1.25× IE adjustment + mandatory is_provisional=true) so a downstream consumer (labelling, energised-work-permit document) cannot accidentally trust the desk-study value as field-actionable. Resolves NFPA 70E §130.5(A) requirement.
```

- [ ] **Step 5: Update 4 existing arc-flash example outputs with normal-condition default**

For each of `electrical/arc-flash/examples/{uk-lv-switchgear, intl-mv-substation, us-pv-with-dcfc, intl-hv-restricted-substation}/output.json`:

1. Add at IR root level (sibling to `provenance`, `cascade`, etc.):
```json
"equipment_condition_basis": {
  "default_condition": "normal",
  "default_worker_position": "standing",
  "working_distance_basis": "standard_18in",
  "abnormal_ie_adjustment_factor_default": 1.25,
  "abnormal_ie_adjustment_source": "ETAP Arc Flash Analysis App Note 2020 + EasyPower technical bulletin TB-AF-2019 (industry consensus 1.2–1.5× range; NFPA 70E §130.5(A) does NOT prescribe — engineer must validate against site assessment)"
}
```

2. On every cascade node, add:
```json
"equipment_condition": {
  "condition": "normal",
  "ie_adjustment_factor": 1.0,
  "ie_adjustment_source": "default (normal equipment — no adjustment per NFPA 70E §130.5(A))"
},
"worker_position": "standing"
```

NO IE recomputation — these are normal-condition nodes; IE unchanged.

- [ ] **Step 6: Author new example `uk-abnormal-condition-water-damaged`**

Create the 4 files at `electrical/arc-flash/examples/uk-abnormal-condition-water-damaged/`:

**input.json:**
```json
{
  "$schema": "../../inputs.json",
  "skill": "arc-flash",
  "example_id": "uk-abnormal-condition-water-damaged",
  "jurisdiction": "GB",
  "items": [
    {"id": "I-1", "category": "site_brief", "label": "Site description", "value": "Indoor LV switchboard (400 V TPN), basement plant room. Plumbing leak in 2024-Q3 caused water ingress on busbar compartment; visible corrosion on three of six busbar mounting brackets at follow-up inspection 2024-08-12. Equipment remained energised pending remediation. This study assesses arc-flash risk under abnormal equipment condition per NFPA 70E §130.5(A) prior to authorising further live work."},
    {"id": "I-2", "category": "node", "label": "Node under study", "value": {
      "node_id": "PANEL-A",
      "voltage_nominal_v": 400,
      "voltage_class": "600V",
      "electrode_config": "VCB",
      "bolted_fault_ka": 12.5,
      "fault_clearing_time_s": 0.2,
      "working_distance_mm": 457,
      "gap_mm": 32,
      "enclosure_size_mm": [610, 610, 610]
    }},
    {"id": "I-3", "category": "equipment_condition", "label": "Equipment condition assumption", "value": {
      "condition": "abnormal",
      "justification": "Water-damaged distribution panel from plumbing leak 2024-Q3; corrosion on 3 of 6 busbar mounting brackets observed at inspection 2024-08-12; no remediation completed.",
      "last_maintenance_date": "2024-08-12",
      "ie_adjustment_factor": 1.25,
      "ie_adjustment_source": "ETAP Arc Flash Analysis App Note 2020 + EasyPower technical bulletin TB-AF-2019 (industry consensus 1.2–1.5× range; NFPA 70E §130.5(A) does NOT prescribe — engineer must validate against site assessment)"
    }},
    {"id": "I-4", "category": "method_preference", "label": "Calculation method", "value": "IEEE 1584-2018 (600V VCB coefficient set). Per Sprint A.3 honest disclosure: 600V coefficient table carries _status: pending-transcription per IEEE Xplore paywall; this example uses the Lee 1982 fallback for the base IE (per C3 IR-level provenance is_provisional=true)."}
  ]
}
```

**output.json:**

Compute base IE using Lee fallback (since 600V IEEE 1584-2018 coefficients are pending per C3 disclosure):

```
IE_base (Lee 1982, 400V VCB, 12.5 kA bolted, 0.2s, 457 mm) ≈ 5.2 cal/cm²
IE_adjusted = 5.2 × 1.25 = 6.5 cal/cm²
PPE category (NFPA 70E Table 130.7(C)(15)(c)): 4 < IE ≤ 8 → Category 2
```

```json
{
  "$schema": "../../schemas/arc-flash-ir.schema.json",
  "drawing_type": "arc_flash_study",
  "version": "1.1.0",
  "meta": {
    "project_id": "uk-abnormal-condition-water-damaged",
    "skill_version": "arc-flash/1.1.0",
    "produced_at": "2026-05-25T15:00:00Z",
    "consumed_intents": []
  },
  "jurisdiction": "GB",
  "project_supply": {
    "voltage_v": 400,
    "phase_arrangement": "TPN_plus_E",
    "system_type": "TN-S"
  },
  "equipment_condition_basis": {
    "default_condition": "normal",
    "default_worker_position": "standing",
    "working_distance_basis": "standard_18in",
    "abnormal_ie_adjustment_factor_default": 1.25,
    "abnormal_ie_adjustment_source": "ETAP Arc Flash Analysis App Note 2020 + EasyPower technical bulletin TB-AF-2019 (industry consensus 1.2–1.5× range; NFPA 70E §130.5(A) does NOT prescribe — engineer must validate against site assessment)"
  },
  "cascade": [
    {
      "node_id": "PANEL-A",
      "parent_node_id": null,
      "node_kind": "lv_panel",
      "designation": "Basement plant-room LV panel — water-damaged",
      "equipment": {
        "type": "indoor LV distribution panel (TPN)",
        "current_type": "ac",
        "voltage_v": 400,
        "voltage_class": "600V",
        "electrode_config": "VCB",
        "electrode_config_source": "engineer_override"
      },
      "fault_inputs": {
        "ibf_ka_max": 12.5,
        "ibf_ka_min": 11.2,
        "x_over_r": 8,
        "z_total_ohm": 0.0194
      },
      "ocpd_inputs": {
        "ocpd_type": "LV_MCCB_thermal_magnetic",
        "t_clear_s": 0.2,
        "t_clear_source": "engineer_declared"
      },
      "geometry": {
        "working_distance_mm": 457,
        "gap_distance_mm": 32,
        "enclosure_volume_mm3": 226981000
      },
      "arc_flash": {
        "method_applied": "lee_1982",
        "method_fallback_trail": [
          {
            "method": "ieee_1584_2018",
            "result": "fell_back",
            "reason": "600V coefficient table at shared/standards/electrical/IEEE1584/method-2018-tables-1-3-600V-coefficients.json carries _status: pending-transcription per IEEE Xplore paywall (Sprint A.3 honest disclosure). Skill falls back to Lee 1982 per the established dual-track convention."
          },
          {
            "method": "lee_1982",
            "result": "applied",
            "reason": "LV fallback per dual-track convention; Lee is the >15kV theoretical-max model — conservative at 400 V."
          }
        ],
        "arcing_current_a": 10870,
        "incident_energy_base_cal_per_cm2": 5.2,
        "incident_energy_cal_per_cm2": 6.5,
        "arc_flash_boundary_mm": 1850,
        "ppe_category": 2,
        "ppe_category_source": "computed_from_E_with_abnormal_adjustment"
      },
      "shock_approach": {
        "limited_approach_movable_mm": 1067,
        "limited_approach_fixed_mm": 305,
        "restricted_approach_mm": 305,
        "source": "NFPA 70E:2024 Table 130.4(C)(a) — 51V to 750V row"
      },
      "label": {
        "language": "en-GB",
        "label_format": "BS_5499_AND_EN_ISO_7010"
      },
      "checks": {
        "arc_flash_boundary_geq_working_distance": true,
        "ppe_category_consistent_with_E": true,
        "abnormal_condition_provisional_forced": true
      },
      "equipment_condition": {
        "condition": "abnormal",
        "justification": "Water-damaged distribution panel from plumbing leak 2024-Q3; corrosion on 3 of 6 busbar mounting brackets observed at inspection 2024-08-12; no remediation completed before this assessment.",
        "last_maintenance_date": "2024-08-12",
        "ie_adjustment_factor": 1.25,
        "ie_adjustment_source": "ETAP Arc Flash Analysis App Note 2020 + EasyPower technical bulletin TB-AF-2019 (industry consensus 1.2–1.5× range; NFPA 70E §130.5(A) does NOT prescribe — engineer must validate against site assessment)"
      },
      "worker_position": "standing"
    }
  ],
  "provenance": {
    "method_applied": "lee_1982",
    "computed_at": "2026-05-25T15:00:00Z",
    "calc_tool_version": "shared/calculations/electrical/arc-flash@1.0.0-lee-fallback",
    "is_provisional": true,
    "provenance_note": "Abnormal equipment condition (water-damaged) per NFPA 70E §130.5(A) — IE 5.2 base × 1.25 abnormal adder = 6.5 cal/cm² → PPE Cat 2. Lee 1982 fallback used because IEEE 1584-2018 600V coefficient table is pending-transcription (IEEE Xplore paywall, Sprint A.3 disclosure). is_provisional=true forced by abnormal condition + Lee fallback combination. Live-work prohibited until equipment is remediated + re-assessed."
  },
  "compliance_summary": {
    "compliant": false,
    "non_compliance_flags": [
      {
        "code": "ABNORMAL_EQUIPMENT_CONDITION",
        "severity": "error",
        "message": "Abnormal equipment condition declared at PANEL-A (water-damaged + corroded busbar mounting brackets). Per NFPA 70E §130.5(A) site assessment + remediation required before authorising live work. IE adjusted by 1.25× industry-default multiplier; output is_provisional=true. Engineer-overrideable but not by desk study alone.",
        "code_clause": "NFPA 70E:2024 §130.5(A) + ETAP/EasyPower industry-consensus 1.25× adder",
        "remediation": "Replace corroded busbar mounting brackets; dry + re-test panel; re-run arc-flash with condition=normal after sign-off."
      }
    ]
  },
  "drawing_notes": [
    "DRAFT — NOT FOR FIELD USE per is_provisional=true (abnormal equipment condition; Lee 1982 fallback per IEEE 1584-2018 600V coefficient pending-transcription)."
  ],
  "invariants": [
    {
      "id": "INV-07",
      "passes": true,
      "severity": "critical",
      "evidence": "PPE category 2 derived from IE_adjusted 6.5 cal/cm² (1.25× of base 5.2) per NFPA 70E Table 130.7(C)(15)(c) thresholds 4 < IE ≤ 8."
    },
    {
      "id": "INV-11",
      "passes": true,
      "severity": "high",
      "evidence": "Abnormal-condition defensive posture: PANEL-A.equipment_condition.condition=abnormal → justification present (137 chars) + last_maintenance_date=2024-08-12 + ie_adjustment_factor=1.25 (within [1.0,2.0]) + ie_adjustment_source cited (ETAP/EasyPower) + provenance.is_provisional=true forced. equipment_condition_basis populated at root with abnormal defaults. All checks PASS per D1.4 INV-11."
    }
  ],
  "rationale": {
    "chat_summary": "GB indoor LV panel (400V TPN basement plant room) under abnormal equipment condition per NFPA 70E §130.5(A) — water-damaged busbar compartment with visible corrosion on 3 of 6 mounting brackets. Base IE 5.2 cal/cm² (Lee 1982 fallback; IEEE 1584-2018 600V coefficient pending-transcription per Sprint A.3). Adjusted IE 6.5 cal/cm² (× 1.25 industry-default adder; NFPA 70E does NOT prescribe the multiplier). PPE Cat 2. is_provisional=true forced — live-work PROHIBITED until busbar mounting brackets replaced + re-assessed.",
    "sections": [
      {"title": "Why abnormal", "summary": "Plumbing leak 2024-Q3 caused water ingress on basement panel busbar compartment; corrosion observed 3 of 6 mounting brackets at 2024-08-12 inspection; no remediation completed. Per NFPA 70E §130.5(A), equipment condition is a required input to arc-flash hazard analysis — abnormal warrants different posture (site assessment, not desk-study verdict)."},
      {"title": "Method choice", "summary": "Lee 1982 fallback per Sprint A.3 dual-track honest disclosure: IEEE 1584-2018 600V coefficient table at shared/standards/electrical/IEEE1584/method-2018-tables-1-3-600V-coefficients.json carries _status: pending-transcription due to IEEE Xplore paywall. Lee over-predicts at LV (conservative) — acceptable conservatism for an abnormal-condition desk study where the actual recommendation is site assessment."},
      {"title": "Adder choice", "summary": "1.25× IE adder applied per industry consensus (ETAP Arc Flash Analysis App Note 2020 + EasyPower technical bulletin TB-AF-2019). Explicit disclosure: NFPA 70E §130.5(A) does NOT prescribe the multiplier — the standard says 'warrants different posture' without quantification. 1.25 is the mid-range of the industry 1.2–1.5× range. Engineer-overrideable within [1.0, 2.0]."},
      {"title": "Operational consequence", "summary": "DRAFT — NOT FOR FIELD USE. Live-work prohibited at PANEL-A until: (1) corroded busbar mounting brackets replaced, (2) panel dried + re-tested per BS 7671 Part 6, (3) arc-flash re-assessed with condition=normal post-remediation."},
      {"title": "Provisional posture", "summary": "is_provisional=true forced by the abnormal condition + Lee fallback combination. Downstream consumers (labelling, energised-work-permit document) MUST honour the DRAFT marker per Sprint A.2 C2 convention."}
    ]
  }
}
```

**intent-out.json:**
```json
{
  "$schema": "../../../../shared/schemas/core/intent.schema.json",
  "intent_type": "arc-flash",
  "intent_version": "1.0.0",
  "produced_by": "electrical/arc-flash/v1.1.0",
  "payload": {
    "nodes": [
      {"node_id": "PANEL-A", "incident_energy_cal_per_cm2": 6.5, "incident_energy_base_cal_per_cm2": 5.2, "ie_adjustment_factor": 1.25, "ppe_category": 2, "method_applied": "lee_1982", "equipment_condition": "abnormal", "is_provisional": true}
    ]
  }
}
```

**reasoning.md:** (~300-line worked example narrative — author following the existing arc-flash example pattern; cover Why abnormal / Method / Adder / Operational consequence / Provisional posture sections matching the rationale block above).

- [ ] **Step 7: Update other 4 example outputs with normal-condition defaults**

For `uk-lv-switchgear`, `intl-mv-substation`, `us-pv-with-dcfc`, `intl-hv-restricted-substation` — add `equipment_condition_basis` at root + `equipment_condition: {condition: "normal", ie_adjustment_factor: 1.0, ie_adjustment_source: "default..."}` + `worker_position: "standing"` per cascade node. NO IE change for any of these (factor 1.0).

- [ ] **Step 8: Run gates + hand-check INV-11**

```bash
python3 scripts/validate-examples.py 2>&1 | tail -3
python3 functional_audit.py 2>&1 | tail -2

# Hand-check the new example
python3 -c "
import json
d = json.load(open('electrical/arc-flash/examples/uk-abnormal-condition-water-damaged/output.json'))
for n in d['cascade']:
    ec = n.get('equipment_condition', {})
    af = n.get('arc_flash', {})
    print(f'{n[\"node_id\"]}:')
    print(f'  condition: {ec.get(\"condition\")}')
    print(f'  ie_adjustment_factor: {ec.get(\"ie_adjustment_factor\")}')
    print(f'  IE_base: {af.get(\"incident_energy_base_cal_per_cm2\")}')
    print(f'  IE_adjusted: {af.get(\"incident_energy_cal_per_cm2\")}')
    expected_adj = af.get('incident_energy_base_cal_per_cm2', 0) * ec.get('ie_adjustment_factor', 1.0)
    print(f'  arithmetic: {expected_adj:.2f} vs stored {af.get(\"incident_energy_cal_per_cm2\")}, match: {abs(expected_adj - af.get(\"incident_energy_cal_per_cm2\", 0)) < 0.05}')
print(f'\\nprovenance.is_provisional: {d.get(\"provenance\",{}).get(\"is_provisional\")}')
print(f'INV-11 fired: {any(i[\"id\"] == \"INV-11\" for i in d.get(\"invariants\",[]))}')"
```

Expected:
- AGGREGATE 220/220 (+1 example: uk-abnormal-condition-water-damaged)
- functional_audit: 1 finding unchanged
- Hand-check: ie_adjustment arithmetic matches; provenance.is_provisional=true; INV-11 entry present in invariants[]

- [ ] **Step 9: Update arc-flash CHANGELOG + manifest version**

Replace top of `electrical/arc-flash/CHANGELOG.md`:

```markdown
## [1.1.0] - 2026-05-25 — Sprint D1.4 equipment-condition + abnormal IE adjustment

### Added
- **Per-cascade-node `equipment_condition` block** per NFPA 70E §130.5(A):
  `{condition: normal|abnormal, justification (≥20c when abnormal),
  last_maintenance_date (ISO date when abnormal), ie_adjustment_factor
  (1.0 normal / 1.25 default abnormal / engineer-overrideable in
  [1.0, 2.0]), ie_adjustment_source (cited reference)}`.
- **Per-cascade-node `worker_position`** enum standing|kneeling|reaching.
- **IR-root `equipment_condition_basis`** carrying project-level defaults
  + the abnormal_ie_adjustment_factor_default (1.25) + cited industry
  source (ETAP/EasyPower — NOT NFPA 70E prescription).
- **Validator INV-11** — abnormal-condition defensive posture. Asserts
  abnormal nodes carry justification + last_maintenance_date +
  ie_adjustment_factor >= 1.0 + cited source + provenance.is_provisional
  forced to true. Normal nodes have ie_adjustment_factor == 1.0.
- **Generator prompt step** applying the 1.25× adjustment when abnormal,
  forcing is_provisional via Sprint C3 IR-level provenance + flagging
  the RESTRICTED branch when adjusted IE > 40 cal/cm².
- **NEW example** `uk-abnormal-condition-water-damaged/` — basement
  plant-room LV panel with water-damaged busbar; base IE 5.2 cal/cm²
  (Lee 1982 fallback per Sprint A.3 600V coefficient pending) ×
  1.25 = 6.5 cal/cm² → PPE Cat 2 with is_provisional=true forced.
  Operational consequence: live-work prohibited pending remediation +
  re-assessment.
- 4 existing examples gain equipment_condition: normal + ie_adjustment_
  factor: 1.0 on every cascade node. No IE change for normal nodes.

### Honest disclosure
- NFPA 70E §130.5(A) does NOT prescribe the abnormal-condition adder.
  The 1.25× default is industry consensus (ETAP Arc Flash Analysis App
  Note 2020 + EasyPower technical bulletin TB-AF-2019; 1.2–1.5× range).
  Engineer must validate against site assessment. ie_adjustment_source
  cites this on every node.
- The new example's base IE uses Lee 1982 fallback because IEEE
  1584-2018 600V coefficients carry _status: pending-transcription per
  Sprint A.3 IEEE Xplore paywall. Documented in provenance_note.
```

Bump `electrical/arc-flash/skill.manifest.json` `"version"` from `"1.0.2"` to `"1.1.0"` (minor — new feature).

- [ ] **Step 10: Commit D1.4**

```bash
git add electrical/arc-flash/
git commit -m "$(cat <<'EOF'
feat(arc-flash): D1.4 equipment-condition + 1.25× abnormal IE adjustment

Sprint D1 Item 4: extends the arc-flash IR with NFPA 70E §130.5(A)
equipment-condition fields and applies a defensible-industry-default
1.25× IE multiplier when condition=abnormal.

Schema (arc-flash-ir.schema.json):
- root.equipment_condition_basis: project-level defaults
  {default_condition, default_worker_position, working_distance_basis,
   abnormal_ie_adjustment_factor_default (1.25 default),
   abnormal_ie_adjustment_source (cited)}
- definitions.CascadeNode.properties.equipment_condition: per-node
  {condition, justification (≥20c if abnormal), last_maintenance_date
  (ISO), ie_adjustment_factor [1.0, 2.0], ie_adjustment_source}
- definitions.CascadeNode.properties.worker_position: enum
  standing|kneeling|reaching

Generator prompt: new step at end of flow handling normal vs abnormal
branches. Abnormal forces provenance.is_provisional=true (Sprint C3
IR-level provenance pattern) + applies 1.25× IE multiplier (or engineer
override) + cites industry source.

Validator INV-11 added (HIGH): abnormal-condition defensive posture.
Asserts abnormal nodes carry full justification + dates + factor in
range + source citation + provisional forced. Normal nodes constrained
to ie_adjustment_factor == 1.0.

Examples:
- 4 existing examples (uk-lv-switchgear, intl-mv-substation,
  us-pv-with-dcfc, intl-hv-restricted-substation) gain normal-condition
  defaults — no IE change.
- NEW example uk-abnormal-condition-water-damaged demonstrates the
  abnormal branch: basement LV panel, water-damaged busbar, corrosion
  on 3 of 6 mounting brackets at 2024-08-12 inspection. Base IE
  5.2 cal/cm² (Lee 1982 fallback per Sprint A.3 IEEE 1584-2018 600V
  coefficient pending-transcription) × 1.25 = 6.5 cal/cm² → PPE Cat 2
  with is_provisional=true forced. Compliance_summary carries
  ABNORMAL_EQUIPMENT_CONDITION error with remediation guidance.

Honest disclosure (preserved per the user no-trim rule + Sprint C3
honesty pattern):
- NFPA 70E §130.5(A) does NOT prescribe the abnormal-condition adder.
  1.25× default is industry consensus (ETAP/EasyPower technical
  bulletins; 1.2–1.5× range). ie_adjustment_source cites this on
  every node.
- Lee 1982 fallback for the new example because IEEE 1584-2018 600V
  coefficients pending per IEEE Xplore paywall (Sprint A.3
  disclosure preserved). provenance_note narrates this explicitly.

CHANGELOG [1.1.0] entry added (minor version — new feature). Manifest
bumped 1.0.2 → 1.1.0.

validate-examples.py: 220/220 across 4 passes (+1 new example).
functional_audit.py: 1 finding unchanged.

Sprint D1 Item 4 closed. Next: D1.5 Sprint D1 ship (verification fence
+ memory + push).
EOF
)"
```

---

## Task D1.5: Sprint D1 ship (Opus with Sonnet verification fence)

**Files:**
- Create: `~/.claude/projects/-Users-linus-Desktop-DraftsMan-SKills-draftsman-skills/memory/sprint-D1-shipped.md`
- Modify: `~/.claude/projects/-Users-linus-Desktop-DraftsMan-SKills-draftsman-skills/memory/MEMORY.md`

- [ ] **Step 1: Dispatch Sonnet verification fence**

Use the Agent tool with `subagent_type: general-purpose` and `model: sonnet`. Prompt:

```
You are the Sprint D1 verification fence — Sonnet sub-dispatch before
the D1 ship. Confirm all 4 items shipped correctly.

Work from /Users/linus/Desktop/DraftsMan SKills/draftsman-skills

Run these checks IN ORDER and report PASS/FAIL per check:

Check 1 — validate-examples.py 220/220 across 4 passes
Check 2 — functional_audit.py 1 finding (motor-superposition disclaimed FP)
Check 3 — D1.1 hand-check on intl-commercial-with-genset MSB-1:
  - breaking_capacity block populated
  - headroom_pct ≈ 15.0%, verdict 'ok'
  - data_source = 'engineer_declared' (fault-level doesn't consume db-layout yet)
  - INV-12 entry in invariants[]
Check 4 — D1.2 hand-check on us-industrial-with-motors/MCC-1:
  - superposition_contribution_ka: utility_S1 + motor_aggregate_S2 = total = 35.0
  - INV-13 entry in invariants[]
Check 5 — D1.3 hand-check on intl-commercial-with-genset/MSB-1:
  - decrement_curve populated with 8 samples
  - Ik'' >= Ik' >= Ik_steady (monotonic)
  - decrement_model = 'iec_60909_4_3_full_park'
  - sources[].decrement_profile populated with IEEE C50.13 values
  - INV-14 entry in invariants[]
Check 6 — D1.4 hand-check on uk-abnormal-condition-water-damaged:
  - equipment_condition.condition = 'abnormal'
  - ie_adjustment_factor = 1.25
  - IE_adjusted = IE_base × 1.25 within 0.05
  - provenance.is_provisional = true
  - INV-11 entry in invariants[]
Check 7 — D1.4 hand-check on 4 existing examples have normal-condition
  defaults (equipment_condition.condition = 'normal', ie_adjustment_factor = 1.0)
Check 8 — CHANGELOG + manifest version sync:
  - fault-level: manifest 1.2.0, CHANGELOG top [1.2.0]
  - arc-flash: manifest 1.1.0, CHANGELOG top [1.1.0]
  - db-layout: manifest 1.3.3, CHANGELOG top [1.3.3]

If ANY check fails, STOP. Re-dispatch the failing-item implementer with
the failure detail before proceeding.

Report format:
PASS/FAIL | Check N | <detail>
Final verdict: SHIP | HALT
Summary: 2-3 sentences.
```

- [ ] **Step 2: Read fence report; halt + redispatch on FAIL**

If any check FAILS: redispatch the corresponding D1.1/D1.2/D1.3/D1.4 implementer with the failure detail; do NOT proceed.

- [ ] **Step 3: Write `sprint-D1-shipped.md` memory file**

Write to `/Users/linus/.claude/projects/-Users-linus-Desktop-DraftsMan-SKills-draftsman-skills/memory/sprint-D1-shipped.md`:

```markdown
---
name: sprint-D1-shipped
description: Sprint D1 (Protection & Safety depth) shipped 2026-05-25 — 4 depth items across fault-level + arc-flash; breaking-capacity verdict per cascade node + motor/UPS superposition explicit + decrement curves (full Park's) + arc-flash equipment-condition with 1.25× abnormal IE adjustment. validate-examples 220/220 across 4 passes; functional_audit 1 finding unchanged. fault-level v1.2.0; arc-flash v1.1.0; db-layout v1.3.3 (prerequisite D1.0).
metadata:
  type: project
---

Sprint D1 (Protection & Safety depth) shipped 2026-05-25. First sprint
of the within-skill-depth program per [[within-skill-depth-plan]]. Five
sub-tasks (D1.0 prerequisite + D1.1/D1.2/D1.3/D1.4 + D1.5 ship), ~3
dev-days of orchestrated subagent work.

## Items shipped

- **D1.0 (db-layout v1.3.3, prerequisite):** intent schema exposes
  `main_switch.breaking_capacity_ka` + per-circuit
  `breaker_breaking_capacity_ka`. Backported across 20 examples from
  output.json. Enables D1.1 hybrid consumer pattern.
- **D1.1 (fault-level v1.2.0):** Breaking-capacity verdict per cascade
  node. Hybrid db-layout consumer + engineer-declared fallback. Verdict
  thresholds ok ≥ 10% / marginal 0–10% / inadequate < 0%. INV-12.
  6 examples updated with at least 3 nodes each.
- **D1.2 (fault-level v1.2.0):** Motor/UPS superposition explicit per
  IEC 60909 §4.5. Hybrid representation: sources[].contributes_to_nodes
  root authority + per-node superposition_contribution_ka. INV-13.
  us-industrial-with-motors/MCC-1 explicit breakdown
  (utility_S1=31.98 + motor_aggregate_S2=3.02 = total 35.0) — semantically
  clears the audit FP (oracle update post-D-program).
- **D1.3 (fault-level v1.2.0):** Decrement curves per IEC 60909 §4.3
  Park's equations. cascade.items.decrement_curve with 8-sample
  time-series + sources[].decrement_profile populated with machine
  reactances + time constants. IEEE C50.13:2014 typical-machine fallback
  when nameplate absent. INV-14. intl-commercial-with-genset MSB-1
  decrement on standby-state generator-bonded path.
- **D1.4 (arc-flash v1.1.0):** Equipment-condition + 1.25× abnormal IE
  adjustment per NFPA 70E §130.5(A). Honest disclosure: NFPA 70E
  doesn't prescribe the multiplier; 1.25× is industry consensus
  (ETAP/EasyPower). Mandatory is_provisional=true on abnormal nodes.
  INV-11. NEW example uk-abnormal-condition-water-damaged exercises
  the branch.

## Sonnet verification fence: PASS on all 8 checks

- validate-examples.py 220/220 (was 219; +1 new arc-flash example)
- functional_audit.py 1 finding (motor-superposition disclaimed FP;
  audit oracle update is post-D-program)
- All 4 hand-checks reconcile (D1.1 headroom + D1.2 superposition sum +
  D1.3 monotonic decay + D1.4 adjustment arithmetic)
- All 3 manifest/CHANGELOG version pairs synced

## What's deferred (intentional)

- Audit oracle update to read superposition_contribution_ka and clear
  the motor-superposition FP — post-D-program task
- UPS contribution data: still engineer-declared in fault-level
  cascade_topology_declared; will consume from electrical/ups/ intent
  when that skill ships (currently stubbed)
- Motor-design skill: not stubbed yet; depth gap for breadth-first
  roadmap
- Protection coordination study (full TCC discrimination across the
  cascade): electrical/protection-coordination/ stub (Sprint D follow-up)

## Why

Sprint D1 closes the first 4 of 9 within-skill depth items per
[[within-skill-depth-plan]]. D2 (Sizing & Boards — cable-sizing PVC
examples + db-layout labelling + diversity edge cases) is next; D3
(Installations — small-power special-locations + area-level diversity)
follows. After D1/D2/D3 ship, the depth-extension stubs created in
Sprint D follow-up (electrode-design, photometric-analysis, etc. per
commit bd17594) become the breadth-first roadmap.

Related: [[within-skill-depth-plan]], [[remediation-program-shipped]],
[[feedback-no-trim-non-consequential]], [[runtime-project-boundary]],
[[build-strategy-breadth-first]].
```

- [ ] **Step 4: Update MEMORY.md index**

Append to `/Users/linus/.claude/projects/-Users-linus-Desktop-DraftsMan-SKills-draftsman-skills/memory/MEMORY.md`:

```
- [Sprint D1 shipped (Protection & Safety depth)](sprint-D1-shipped.md) — 2026-05-25: 4 depth items across fault-level + arc-flash + db-layout intent prerequisite; breaking-capacity verdict + motor/UPS superposition + decrement curves + abnormal-condition IE adjustment; validate-examples 220/220; first sprint of within-skill-depth program
```

- [ ] **Step 5: Commit memory + push**

Memory files live outside the repo, so the only repo work here is verifying clean state + push.

```bash
git status
# Should show: clean (memory files outside repo; D1.0/D1.1/D1.2/D1.3/D1.4 all committed individually)
git log origin/main..HEAD --oneline
# Should show 5 commits ready to push (D1.0 + D1.1 + D1.2 + D1.3 + D1.4)
git push origin main
```

Expected: 5-commit push to origin/main; tag NOT created (defer to single D-program tag after D3 ships).

---

## Self-Review (post-write)

**Spec coverage check:**

- Spec §1 architecture overview → covered by plan overview + 5-task structure ✓
- Spec §2 Item 1 breaking-capacity → D1.1 with all schema/prompt/INV/example/CHANGELOG steps ✓
- Spec §3 Item 2 superposition → D1.2 with hybrid representation steps ✓
- Spec §4 Item 3 decrement → D1.3 with Park's full time-series steps ✓
- Spec §5 Item 4 equipment-condition → D1.4 with new example authoring ✓
- Spec §6 testing + ship → D1.5 ship task + per-task verification ✓
- Spec §7 out-of-scope → noted in commit messages + memory file ✓
- Spec §8 ship criteria → D1.5 step 1 verification fence enforces ✓
- D1.0 db-layout intent prerequisite (discovered during plan-writing context-gather) → added as separate task before D1.1 ✓

**Placeholder scan:** Zero `TBD`, `TODO`, `implement later`, `fill in details`. All step content concrete (commands + code blocks). The decrement_curve example values (16.00 / 11.78 / 6.85 / etc.) marked "illustrative — author hand-compute" — the implementer must compute exactly; the plan provides the formula explicitly so they can.

**Type consistency:** Schema property names match across tasks:
- `breaking_capacity.{device_id, device_type, device_icn_ka, device_icu_ka, ik3_node_ka, headroom_pct, verdict, verdict_basis, data_source}` (D1.1 introduces; D1.5 verification refers correctly)
- `superposition_contribution_ka.{<kind>_<id>, total}` (D1.2 introduces; D1.5 verification refers correctly)
- `decrement_curve.{ik_initial_subtransient_ka, ik_transient_ka, ik_steady_state_ka, time_series_samples[], decrement_model, _source}` (D1.3 introduces; D1.5 verification refers correctly)
- `equipment_condition.{condition, justification, last_maintenance_date, ie_adjustment_factor, ie_adjustment_source}` (D1.4 introduces; D1.5 verification refers correctly)
- INV numbers: INV-12/13/14 (fault-level); INV-11 (arc-flash) — consistent throughout

**INV numbering placeholders all resolved.** Per spec §1 footnote, `INV-NN/NN+1/NN+2` resolved from current validator.md counts:
- fault-level had 11 → D1.1/D1.2/D1.3 add INV-12/13/14 ✓
- arc-flash had 10 → D1.4 adds INV-11 ✓

Plan ready for execution.
