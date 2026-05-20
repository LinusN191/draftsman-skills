# Small-Power v1.1 — Cable-Sizing Intent Consumer Migration — Design Spec

**Date:** 2026-05-20
**Status:** Approved — ready for implementation plan
**Target:** `electrical/small-power` v1.1.0 beta
**Sprint type:** Migration (additive, non-breaking). small-power v1.0 examples stay valid.

**Base:**
- small-power v1.0.0 shipped 2026-05-20 (commit f471cc3 era) as a leaf skill (`consumes_intents: []`).
- cable-sizing v1.0.0 shipped 2026-05-20 (commit eee98c2 era) with intent carrying `r1_plus_r2_milliohm_per_m_at_operating_temp` + `reactance_milliohm_per_m` per circuit — the Zs-resolution helper fields documented as small-power v1.1's migration target.
- This sprint executes that migration.

**Pattern parents:**
- SLD v1.3 → v1.4 (leaf → multi-skill consumer of 3 intents) — closest structural precedent
- cable-sizing v1.0 refresh §2 (forward-compat contract that v1.1 fulfils)
- lighting-layout v1.3 (flexible-inputs pattern — supports both intent consumption and engineer-declared fallback)

---

## 1. Goal

Migrate small-power from leaf to optional consumer of `cable-sizing` intent. When the intent is provided in the skill's inputs:

- Look up each small-power circuit in the cable-sizing intent's `circuits[]`
- Compute `verified_zs_ohm = Ze + (r1_plus_r2 / 1000) × length + (reactance / 1000) × length` per circuit (mΩ/m → Ω/m conversion implicit)
- Populate the existing `verified_zs_ohm` field (currently nullable)
- Flip the existing `tool_call_pending_for_zs_verification` field from `true` to `false`
- Remove the `TOOL-CALL-PENDING:calc.zs_loop_impedance` flag from `flags[]`

When the intent is absent (no `consumed_intents` entry of type `cable-sizing`):

- Fall back to v1.0 deferral behaviour
- `verified_zs_ohm` stays absent, `tool_call_pending_for_zs_verification: true`, `TOOL-CALL-PENDING:calc.zs_loop_impedance` flag retained

This is a non-breaking additive change. All 4 existing v1.0 examples remain valid and continue to demonstrate the hybrid fallback path.

---

## 2. Scope

### 2.1 In scope (v1.1)

- Manifest update: `consumes_intents` populated, version bump
- IR schema: typed `consumed_intents.items` + new optional `cable_sizing_node_id` field per circuit
- Generator: 12 → 13 steps (new Step 12 inserted: Zs resolution from cable-sizing intent)
- Validator: new INV-11 (lookup failure hard-fail when intent consumed)
- Reviewer: new D-7 (Zs resolution provenance audit)
- 1 new worked example demonstrating v1.1 consumption mode
- 1 new eval covering v1.1 consumption behaviour
- CHANGELOG, SKILLS_STATUS, ARCHITECTURE bookkeeping

### 2.2 Out of scope (deferred to v1.2+)

- Multi-board small-power consumption (v1.0 is single-board scoped via single `parent_db` field)
- Earthing intent consumption (deferred — v1.2+ may add this for `system_type` cross-verification)
- Fault-level intent consumption (deferred — v1.2+ may add PFC cross-verification at circuit OCPD breaker)
- Updating existing 4 v1.0 examples to consume intent (kept untouched — they document hybrid fallback)

---

## 3. Manifest changes

`electrical/small-power/skill.manifest.json`:

```diff
- "version": "1.0.0",
+ "version": "1.1.0",
```

```diff
- "consumes_intents": [],
+ "consumes_intents": ["cable-sizing"],
```

No other manifest field changes. `standards[]`, `ontology[]`, `calculations[]` unchanged.

---

## 4. Schema changes (small-power-ir.schema.json)

### 4.1 Type `meta.consumed_intents.items` properly

Currently:

```json
"consumed_intents": {
  "type": "array",
  "items": { "type": "object" },
  "default": []
}
```

Change to (match SLD v1.4 shape):

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

### 4.2 Add optional `cable_sizing_node_id` per circuit

In `properties.circuits.items.properties`, add:

```json
"cable_sizing_node_id": {
  "type": "string",
  "pattern": "^[A-Z0-9][A-Za-z0-9._-]*$",
  "description": "Optional explicit reference to a cable-sizing intent circuits[].node_id when consuming cable-sizing intent. When absent, the v1.1 generator falls back to implicit composition `f\"{parent_db.designation}.{circuit_id}\"`."
}
```

Schema validation stays `additionalProperties: false` — the new field is part of the closed property set.

### 4.3 Untouched

- `verified_zs_ohm` (already optional number, minimum 0)
- `tool_call_pending_for_zs_verification` (already boolean, default true)

Both fields exist in v1.0 schema and are now used semantically — no schema change required.

---

## 5. Generator (12 → 13 steps)

`electrical/small-power/prompts/generator.md`:

### 5.1 New Step 12 — Zs resolution from cable-sizing intent

Inserted before the existing rationale step. The new step:

1. Check if `meta.consumed_intents[]` has an entry with `intent_type == "cable-sizing"`. If absent, skip — leave `verified_zs_ohm` absent, `tool_call_pending_for_zs_verification: true`, retain `TOOL-CALL-PENDING:calc.zs_loop_impedance` flag.
2. If present, load the cable-sizing intent's `circuits[]` from the path declared in `consumed_intents[]`.
3. For each small-power circuit `c`:
   - Determine lookup key: if `c.cable_sizing_node_id` is set, use it; else compose `f"{parent_db.designation}.{circuit_id}"` (e.g., `"CU-MAIN.C01"`).
   - Find the matching `cable-sizing.circuits[i]` where `i.node_id == lookup_key`.
   - If found: compute `verified_zs_ohm = Ze + (r1_plus_r2 / 1000) × length + (reactance / 1000) × length` where r1_plus_r2 + reactance + length come from the cable-sizing entry and Ze from `supply_origin.ze_declared_ohm`. Populate `c.verified_zs_ohm`. Set `c.tool_call_pending_for_zs_verification: false`.
   - If not found: hard-fail (INV-11 fires) with message naming the unresolved lookup key.
4. If ALL circuits successfully resolved: remove `TOOL-CALL-PENDING:calc.zs_loop_impedance` from `flags[]`.

### 5.2 Renumber existing Step 12 → Step 13

The pre-existing 12th step (emit rationale block) becomes Step 13. No content change to that step.

### 5.3 Step 12 in chat_summary mention

The 8-section rationale's section 4 (RCD Posture) or section 6 (Diversity + Zs) should add a sentence covering Zs resolution provenance — either "Zs resolved from cable-sizing intent ({path})" or "Zs deferred per WI3 (v1.0 fallback — no cable-sizing intent consumed)".

---

## 6. Validator — new INV-11

`electrical/small-power/prompts/validator.md`:

### INV-11: Cable-sizing intent lookup integrity

**Rule:** When `meta.consumed_intents[]` contains an entry with `intent_type == "cable-sizing"`, every circuit's lookup MUST resolve. The lookup key is `cable_sizing_node_id` (explicit) or `f"{parent_db.designation}.{circuit_id}"` (implicit composition). A lookup that finds no matching `cable-sizing.circuits[].node_id` is a hard fail.

**Severity:** Hard fail.

**Fail message:**

```
INV-11: small-power circuit <CIRCUIT_ID> cable-sizing intent lookup failed.
Lookup key: <KEY> (source: <explicit cable_sizing_node_id | implicit composition>)
No matching cable-sizing.circuits[].node_id == <KEY> found in consumed intent at <PATH>.
Fix: either correct the parent_db.designation + circuit_id values to compose the expected node_id, 
or set an explicit cable_sizing_node_id on this circuit.
```

The other 10 INV checks (INV-01 through INV-10) are unchanged.

---

## 7. Reviewer — new D-7

`electrical/small-power/prompts/reviewer.md`:

### D-7: Zs Resolution Provenance Audit

**Question:** Is Zs resolution state consistent across all circuits?

**Look for:**
- If `meta.consumed_intents[]` contains an entry with `intent_type == "cable-sizing"`:
  - Every circuit has `verified_zs_ohm > 0` populated
  - Every circuit has `tool_call_pending_for_zs_verification == false`
  - `TOOL-CALL-PENDING:calc.zs_loop_impedance` is NOT in `flags[]`
- If `meta.consumed_intents[]` does NOT contain a `cable-sizing` entry:
  - Every circuit has `verified_zs_ohm` absent (or `null`)
  - Every circuit has `tool_call_pending_for_zs_verification == true`
  - `TOOL-CALL-PENDING:calc.zs_loop_impedance` IS in `flags[]`

**Flag when:** Mixed states detected (some circuits resolved, others deferred — without engineer-documented justification in `assumptions[]`).

D-1 through D-6 unchanged (D-3 citation-rigour sub-checks under D-1 also unchanged).

---

## 8. New worked example: `examples/uk-3bed-with-cable-sizing/`

Mirrors the existing `uk-3bed-dwelling` scenario in v1.1 consumption mode.

### 8.1 Files (5)

| File | Purpose |
|---|---|
| `input.json` | small-power inputs + references the bundled `consumed-cable-sizing-intent.json` path |
| `consumed-cable-sizing-intent.json` | Synthetic cable-sizing intent with 5 circuits matching `CU-MAIN.C01..C05`. r1_plus_r2 + reactance + length values match the cable-sizing UK domestic example precedent (`electrical/cable-sizing/examples/uk-domestic-final-circuits/intent-out.json`). |
| `output.json` | Full v1.1 IR — `meta.consumed_intents[]` populated; every circuit has `verified_zs_ohm` resolved; `tool_call_pending_for_zs_verification: false`; `TOOL-CALL-PENDING:calc.zs_loop_impedance` flag dropped |
| `intent-out.json` | Small-power intent — shape UNCHANGED from v1.0 (downstream consumers don't see the v1.1 internal Zs resolution) |
| `reasoning.md` | 8 sections — section 6 (Diversity + Zs) covers the v1.1 resolution narrative |

### 8.2 Engineering scenario

Same UK 3-bed dwelling, 5 circuits, 230V TN-C-S, Ze=0.35Ω, PSCC=6kA. With cable-sizing intent now resolving Zs:

| Circuit | csa (Cu PVC) | length (m) | r1_plus_r2 (mΩ/m) | reactance (mΩ/m) | Zs calc | verified_zs_ohm |
|---|---|---|---|---|---|---|
| C01 ring (kitchen + utility + dining + lounge) | 2.5 mm² | 32 | 18.1 | 0.08 | 0.35 + 18.1×32/1000 + 0.08×32/1000 | 0.93 |
| C02 ring (bedrooms) | 2.5 mm² | 28 | 18.1 | 0.08 | 0.35 + 18.1×28/1000 + 0.08×28/1000 | 0.86 |
| C03 cooker dedicated radial | 6 mm² | 8 | 7.95 | 0.08 | 0.35 + 7.95×8/1000 + 0.08×8/1000 | 0.41 |
| C04 immersion dedicated radial | 2.5 mm² | 4 | 18.1 | 0.08 | 0.35 + 18.1×4/1000 + 0.08×4/1000 | 0.42 |
| C05 bathroom shaver supply (SSU) | 1.5 mm² | 3 | 30.3 | 0.10 | 0.35 + 30.3×3/1000 + 0.10×3/1000 | 0.44 |

All values within Zs_max for their OCPD (BS 7671 Table 41.3 — e.g., 32A Type B MCB Zs_max ≈ 1.44Ω at 230V, 0.4s ADS).

### 8.3 Cross-reference

Reasoning.md should cite cable-sizing example provenance: r1_plus_r2 + reactance values "sourced from cable-sizing v1.0 UK domestic example shipped 2026-05-20 (commit eee98c2 era), reproduced as synthetic intent for this v1.1 demonstration".

---

## 9. New eval: `eval-10-cable-sizing-intent-consumed.yaml`

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

  - assertion: "all(c.verified_zs_ohm is not None and c.verified_zs_ohm > 0 for c in output.circuits)"
    description: Every circuit has verified_zs_ohm populated and positive
    severity: critical

  - assertion: "all(c.tool_call_pending_for_zs_verification == False for c in output.circuits)"
    description: Every circuit has tool_call_pending_for_zs_verification == false
    severity: critical

  - assertion: "'TOOL-CALL-PENDING:calc.zs_loop_impedance' not in output.flags"
    description: TOOL-CALL-PENDING:calc.zs_loop_impedance flag dropped (Zs resolved)
    severity: critical
```

The 9 existing v1.0 evals stay unchanged. They still cover the v1.1 hybrid fallback path (because the 4 v1.0 examples don't consume the intent — they demonstrate fallback).

---

## 10. Bookkeeping

### 10.1 CHANGELOG.md

Append a `## [1.1.0] - 2026-05-20` entry under small-power's CHANGELOG covering:

- Added: cable-sizing intent consumption (hybrid mode — optional, falls back to v1.0 deferral when intent absent)
- Added: `cable_sizing_node_id` optional field on every circuit (explicit override; default implicit composition `f"{parent_db.designation}.{circuit_id}"`)
- Added: 13-step generator (was 12), INV-11 validator check, D-7 reviewer check
- Added: 1 new worked example (`uk-3bed-with-cable-sizing/`) + 1 new eval (`eval-10-cable-sizing-intent-consumed`)
- Schema: typed `meta.consumed_intents.items` (additive — matches SLD v1.4 shape)
- Non-breaking: all 4 v1.0 examples and 9 v1.0 evals remain valid

### 10.2 SKILLS_STATUS.md

Update small-power row:
- Version reference: v1.0.0 beta → v1.1.0 beta
- Notes: add "v1.1.0 — cable-sizing intent consumer (hybrid mode); new uk-3bed-with-cable-sizing example demonstrates v1.1 consumption + Zs resolution"
- Evals count: 9/4 ✓ → 10/4 ✓
- consumes_intents reference: `[]` → `["cable-sizing"]`

### 10.3 ARCHITECTURE.md

Two subsections need light updates:

- `### small-power skill (v1.0+)` — note that the leaf shape is now v1.0 only; v1.1 adds cable-sizing consumption (hybrid mode)
- `### cable-sizing skill (v1.0+)` — update the "small-power v1.1 migration target" forward reference to "small-power v1.1 SHIPPED 2026-05-20"

---

## 11. Untouched (v1.0 stays valid)

- 4 existing v1.0 examples (`uk-3bed-dwelling`, `ke-nairobi-small-office`, `intl-open-plan-floor`, `us-residential-dwelling`) — demonstrate v1.1 hybrid fallback behaviour
- All 9 existing v1.0 evals (eval-01 through eval-09)
- 5 rules + 3 constraints + 3 validation YAMLs
- Ontology (`shared/ontology/equipment/socket-types.json`)
- Symbols (`shared/symbols/electrical/sockets/`)
- inputs.json (no new engineer-facing inputs — cable-sizing intent path declared via `consumed_intents[].path` convention, standardised across the runtime)

---

## 12. Sprint structure (estimate)

Likely 4-5 tasks:

| Phase | Task | Files | Model |
|---|---|---|---|
| A | Manifest + schema | manifest + small-power-ir.schema.json | Opus (schema judgment) |
| B | Prompts | generator.md + validator.md + reviewer.md (3 files, bundled) | Opus (engineering reasoning) |
| C | New example | 5 files in uk-3bed-with-cable-sizing/ | Opus (Zs calculation correctness) |
| D | Eval + bookkeeping | eval-10.yaml + CHANGELOG + SKILLS_STATUS + ARCHITECTURE | Sonnet (mechanical) |
| E | Cross-cutting validation + push | (no new files) | Opus (judgment on ship-readiness) |

Net file ops: 5 new files + ~7 file modifications. Net 12 file ops. Fits 1-2 day budget.

---

## 13. Versioning policy

This is a minor bump (1.0.0 → 1.1.0): additive, non-breaking. Per the existing small-power versioning policy:

- Minor bumps (1.x.0): add new jurisdictions, multi-skill consumption, new evals, new examples
- Major bump (2.0.0): reserved for breaking IR schema change OR EV-charging integration
- Patch bumps (1.1.x): rules / constraints / validation bug fixes

This sprint exercises the minor bump path.

---

## 14. Approval

Approved by user 2026-05-20 via brainstorming dialogue. Three scoping decisions locked:

1. Intent posture: hybrid (optional consumption, v1.0 fallback)
2. ID mapping: implicit `{designation}.{circuit_id}` composition with optional `cable_sizing_node_id` override
3. Examples: add 1 new v1.1-only example (zero churn to 4 existing v1.0 examples)

Next step: invoke `superpowers:writing-plans` to produce `docs/superpowers/plans/2026-05-20-small-power-v1.1-migration-sprint.md`.
