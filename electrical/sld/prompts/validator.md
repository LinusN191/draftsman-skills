# SLD — Validator Prompt (v1.5.0)

You are validating an SLD IR document produced by the `electrical/sld` skill generator.

## Input

- An IR JSON document at the user-provided path.
- The canonical schema at `electrical/sld/schemas/sld-ir.schema.json`.
- The intent schema at `electrical/sld/schemas/sld-intent.schema.json`.
- The repo root (so `consumed_intent_path` values can be resolved).

## Validation procedure

### 1. Schema validation

Run JSON-schema validation against `sld-ir.schema.json`.
- If invalid: STOP. Emit `{"valid": false, "stage": "schema", "errors": [...]}`.

### 2. Cross-field invariants

Run all 10 INV checks below. For each, emit a violation if the rule fails. All severities are **CRITICAL** for v1.3 — any failure blocks `valid: true`.

---

## INV-01: Single root in distribution_hierarchy

**Condition:** Exactly ONE entry in `ir.distribution_hierarchy[]` has `parent_board_id == null`.

**IR field paths:**
- `$.distribution_hierarchy[*].parent_board_id`

**Severity:** CRITICAL

**Failure message templates:**
- Zero roots: `"INV-01: No root board found in distribution_hierarchy — exactly one entry must have parent_board_id: null (the root MSB)"`
- Multiple roots: `"INV-01: Multiple roots found in distribution_hierarchy (count=<N>) — exactly one entry must have parent_board_id: null"`

---

## INV-02: All non-root nodes resolve to an existing parent

**Condition:** For every entry in `ir.distribution_hierarchy[]` where `parent_board_id != null`, that `parent_board_id` value MUST match the `board_id` of another entry in the same array. No dangling pointers, no self-references, no cycles.

**IR field paths:**
- `$.distribution_hierarchy[*].parent_board_id`
- `$.distribution_hierarchy[*].board_id`

**Severity:** CRITICAL

**Failure message templates:**
- Dangling pointer: `"INV-02: Board <CHILD_ID> declares parent_board_id=<PARENT_ID> but no entry with board_id=<PARENT_ID> exists in distribution_hierarchy"`
- Self-reference: `"INV-02: Board <ID> has parent_board_id pointing to itself — cycle detected"`
- Cycle: `"INV-02: Cycle detected in distribution_hierarchy: <ID_A> → <ID_B> → ... → <ID_A>"`

Implementation note: traverse from each non-root upward to root following `parent_board_id`; if traversal revisits a node, it is a cycle.

---

## INV-03: All boards have a resolvable consumed_intent_path

**Condition:** For every entry in `ir.distribution_hierarchy[]`, the `consumed_intent_path` field MUST point to a file that exists relative to the repo root.

**IR field paths:**
- `$.distribution_hierarchy[*].consumed_intent_path`

**Severity:** CRITICAL

**Failure message templates:**
- Missing file: `"INV-03: Board <ID> consumed_intent_path=<PATH> does not resolve to an existing file (relative to repo root)"`
- Empty/null path: `"INV-03: Board <ID> consumed_intent_path is empty or null — every board must reference its db-layout intent-out.json"`

Implementation note: resolve each path against the repo root used for validation (typically the validation host's working directory). If file not found, emit failure.

---

## INV-04: consumed_intents[] count matches distribution_hierarchy[] count

**Condition:** `len(ir.meta.consumed_intents) == len(ir.distribution_hierarchy)`. Every board contributes exactly one entry to the consumed_intents trace.

**IR field paths:**
- `$.meta.consumed_intents[*]`
- `$.distribution_hierarchy[*]`

**Severity:** CRITICAL

**Failure message templates:**
- Count mismatch: `"INV-04: meta.consumed_intents length (<M>) does not match distribution_hierarchy length (<N>) — every board must contribute one consumed-intent trace entry"`

Implementation note: this catches the case where the generator forgot to register one of the board's intent consumption in the meta trace.

---

## INV-05: Intake current capacity adequate

**Condition:** `ir.system_metrics.imax_total_a <= ir.supply_origin.main_switch_rating_a`.

**IR field paths:**
- `$.system_metrics.imax_total_a`
- `$.supply_origin.main_switch_rating_a`

**Severity:** CRITICAL

**Failure message templates:**
- Undersized: `"INV-05: Intake undersized — imax_total_a=<N>A exceeds main_switch_rating_a=<M>A. Upgrade main switch or split supplies."`

Note: this is an arithmetic check on what the generator should have detected in Step 5. The validator independently re-verifies and refuses to bless an undersized intake.

---

## INV-06: Intake breaking capacity adequate

**Condition:** `ir.system_metrics.peak_pfc_ka <= ir.supply_origin.main_switch_breaking_capacity_ka`.

**IR field paths:**
- `$.system_metrics.peak_pfc_ka`
- `$.supply_origin.main_switch_breaking_capacity_ka`

**Severity:** CRITICAL

**Failure message templates:**
- Insufficient Icu: `"INV-06: Main switch breaking capacity insufficient — peak_pfc_ka=<P> kA exceeds main_switch_breaking_capacity_ka=<I> kA. Specify device with higher Icu."`

Note: independent verification of Step 5 Check 2 in the generator.

---

## INV-07: selectivity_cascade has exactly N-1 entries for N boards

**Condition:** `len(ir.selectivity_cascade) == len(ir.distribution_hierarchy) - 1`. One selectivity entry per parent→child link (root has no parent, so N-1 links for N boards).

**IR field paths:**
- `$.selectivity_cascade[*]`
- `$.distribution_hierarchy[*]`

**Severity:** CRITICAL

**Failure message templates:**
- Count mismatch: `"INV-07: selectivity_cascade has <C> entries; expected <N>-1 = <E> entries for the <N>-board cascade. Every parent→child link must have a selectivity verdict."`
- Orphan entry: `"INV-07: selectivity_cascade entry references child_board_id=<ID> which has no entry in distribution_hierarchy"`
- Missing entry: `"INV-07: Non-root board <CHILD_ID> (parent=<PARENT_ID>) has no entry in selectivity_cascade"`

Implementation note: also verify each entry's `parent_board_id` + `child_board_id` correspond to a real parent→child relationship in `distribution_hierarchy` (the child's `parent_board_id` matches the entry's `parent_board_id`).

---

## INV-08: SPD assessment present + jurisdiction-appropriate code_clause

**Condition:** `ir.system_metrics.spd_assessment` is present (required by schema) AND the `code_clause` field starts with the jurisdiction-appropriate prefix per the routing table below.

**IR field paths:**
- `$.system_metrics.spd_assessment`
- `$.system_metrics.spd_assessment.code_clause`
- `$.jurisdiction`

**Severity:** CRITICAL

**Routing table (per jurisdiction):**

| Jurisdiction | code_clause MUST start with |
|---|---|
| GB | `"BS 7671:"` |
| EU / INT | `"IEC 60364"` |
| KE | `"KS 1700:"` (or `"IEC 60364"` for Annex E §VIII routed clauses) |
| US | `"NEC 2023"` or `"NFPA 70:"` |

**Failure message templates:**
- Missing block: `"INV-08: system_metrics.spd_assessment missing — SPD assessment is mandatory per Step 7"`
- Wrong jurisdiction prefix: `"INV-08: SPD code_clause=<CLAUSE> does not start with jurisdiction-appropriate prefix for <JURISDICTION>. Expected prefix: <EXPECTED>"`

---

## INV-09: Tool deferral shape consistency

**Condition:** The pair `(tool_call_pending_for_system_metrics, flags[contains TOOL-CALL-PENDING string])` MUST be coherent.

**IR field paths:**
- `$.system_metrics.tool_call_pending_for_system_metrics`
- `$.flags[*]`

**Severity:** CRITICAL

**Truth table:**

| `tool_call_pending_for_system_metrics` | `flags[]` contains `TOOL-CALL-PENDING:sld_system_metrics` string | Verdict |
|---|---|---|
| true | yes | PASS |
| true | no | FAIL (mismatched) |
| false | yes | FAIL (mismatched) |
| false | no | PASS |
| absent | no | PASS (default false) |
| absent | yes | FAIL (mismatched) |

**Failure message templates:**
- Flag-without-bool: `"INV-09: flags[] contains TOOL-CALL-PENDING:sld_system_metrics but tool_call_pending_for_system_metrics is false/absent — mismatched deferral shape"`
- Bool-without-flag: `"INV-09: tool_call_pending_for_system_metrics=true but flags[] does not contain TOOL-CALL-PENDING:sld_system_metrics — mismatched deferral shape"`

The TOOL-CALL-PENDING string MUST match the prefix `^TOOL-CALL-PENDING:sld_system_metrics` (suffix may carry the disclaimer text).

---

## INV-10: Jurisdiction routing for all code citations

**Condition:** Every `code_clause` field in the IR MUST start with the jurisdiction-appropriate prefix per the routing table. This includes (non-exhaustive list of citation-bearing paths):

- `$.system_metrics.spd_assessment.code_clause`
- `$.compliance_summary.non_compliance_flags[*].code_clause`
- `$.rationale.sections[*].decisions[*].code_clause`

**IR field paths:** all string fields named `code_clause` recursively in the IR.

**Severity:** CRITICAL

**Routing table (per jurisdiction):**

| Jurisdiction | code_clause MUST start with |
|---|---|
| GB | `"BS 7671:"` (e.g., `"BS 7671:2018+A2 Reg 443"`) |
| EU / INT | `"IEC 60364"` (e.g., `"IEC 60364-4-44:2007 Clause 443"`) |
| KE | `"KS 1700:"` (e.g., `"KS 1700:2018 §443"`) OR `"IEC 60364"` (for Annex E §VIII routed clauses, e.g. `"IEC 60364-7-722 (via KS 1700 Annex E §VIII)"`) |
| US | `"NEC 2023"` OR `"NFPA 70:"` (e.g., `"NEC 2023 Article 285"` or `"NFPA 70:2023 Article 700"`) |

**Cross-contamination ban:**

- When `jurisdiction != "KE"`, the string `"KS 1700"` MUST NOT appear in any `code_clause` field
- When `jurisdiction != "GB"` AND `jurisdiction != "KE"`, the string `"BS 7671"` MUST NOT appear in any `code_clause` field
- When `jurisdiction == "KE"`, the v1.1 annotation pattern `"(adopted by KS 1700)"` MUST NOT appear in any `code_clause` field (banned in v1.2+ — direct KS citation only). Leading citations of the form `"KS 1700:2018 §X.Y.Z (Annex E: adopts BS 7671:... verbatim)"` are permitted because they lead with `KS 1700:`.

**Failure message templates:**
- Wrong jurisdiction prefix: `"INV-10: code_clause=<CLAUSE> at <PATH> does not start with jurisdiction-appropriate prefix for <JURISDICTION>. Expected prefix: <EXPECTED>"`
- Cross-contamination: `"INV-10: code_clause=<CLAUSE> at <PATH> contains <BANNED_STRING> which is not permitted for jurisdiction <JURISDICTION>"`
- Banned annotation pattern: `"INV-10: code_clause=<CLAUSE> at <PATH> uses the banned '(adopted by KS 1700)' annotation pattern — KE citations must lead with 'KS 1700:'"`

---

### 3. Intent extraction validation

Project the IR down to the intent shape declared by `sld-intent.schema.json` (per generator Step 11). Validate against that schema.

Required fields per intent schema:
`intent_type, intent_version, produced_by_skill_version, project_id, jurisdiction, supply_summary, board_count, msb_board_id, boards, spd_assessment_verdict, selectivity_overall_verdict, compliant, produced_at`

Schema is `additionalProperties: false` — emit only the declared fields.

If the intent extraction fails schema validation, emit `{"valid": false, "stage": "intent", "errors": [...]}`.

## Output

Emit a single JSON object:

```json
{
  "valid": true | false,
  "stage": "schema" | "invariants" | "intent" | "passed",
  "errors": [
    {"code": "INV-N", "path": "$.distribution_hierarchy[2].parent_board_id", "message": "..."}
  ],
  "warnings": [...]
}
```

`valid: true` requires ALL of:
- Schema validation passes
- All 11 INV checks pass (INV-11 only when both intent paths are present)
- Intent extraction validates against `sld-intent.schema.json`

---

## INV-11: Multi-skill intent consumption shape (v1.4+)

**When this check fires:** Only when both `input.earthing_intent_path` AND `input.fault_level_intent_path` are present (backward-compatible — v1.3 examples skip INV-11 entirely).

**Field-name reference (verified against live schemas + working intent files):**
- Earthing intent: top-level `system_type` field (NOT nested `earthing_system.system_type`)
- Fault-level intent: peak PFC = `fault_currents[]` entry where `node_kind == "transformer_secondary"` → `ifault_ka_max`
- Fault-level intent schema forbids `intent_type` field; earthing intent schema permits it

**Checks (1-5 are hard fails; 6-7 emit warning flags):**

1. `output.meta.consumed_intents.length == output.distribution_hierarchy.length + 2`
   - Fail message: `"INV-11: meta.consumed_intents length (<M>) does not match distribution_hierarchy length + 2 (<N>+2=<E>) — v1.4 multi-skill examples must declare N db-layout + 1 earthing + 1 fault-level intent entries"`

2. Exactly 1 entry in `meta.consumed_intents[]` has `intent_type == "earthing"`
   - Fail message: `"INV-11: meta.consumed_intents has <N> entries with intent_type='earthing'; expected exactly 1 for v1.4 multi-skill examples"`

3. Exactly 1 entry in `meta.consumed_intents[]` has `intent_type == "fault-level"`
   - Fail message: `"INV-11: meta.consumed_intents has <N> entries with intent_type='fault-level'; expected exactly 1 for v1.4 multi-skill examples"`

4. `input.earthing_intent_path` resolves to an existing file (relative to repo root)
   - Fail message: `"INV-11: earthing_intent_path=<PATH> does not resolve to an existing file"`

5. `input.fault_level_intent_path` resolves to an existing file
   - Fail message: `"INV-11: fault_level_intent_path=<PATH> does not resolve to an existing file"`

6. **(Warning)** SLD `supply_origin.system_type` equals earthing intent's top-level `system_type` (string equality)
   - Warning message: `"INV-11: cross-skill mismatch — SLD supply_origin.system_type=<S1> but earthing intent system_type=<S2>. Engineer override is valid for cross-skill design tensions but should be documented in compliance_summary.assumptions."`

7. **(Warning)** SLD `system_metrics.peak_pfc_ka` is within ±0.5 kA of the fault-level intent's `fault_currents[]` entry where `node_kind == "transformer_secondary"` → `ifault_ka_max`
   - Warning message: `"INV-11: cross-skill peak_pfc mismatch — SLD system_metrics.peak_pfc_ka=<P1> but fault-level intent declares <P2> (Δ=<DELTA>kA > 0.5kA tolerance)"`

### Backward compatibility

If `earthing_intent_path` is absent OR `fault_level_intent_path` is absent, skip INV-11 entirely. v1.3 examples (which lack both fields) remain valid under v1.4 validation rules.

### Special case — INT example genset filtering

If the fault-level intent's `source_summary.type == "mixed"` (utility + genset dual-source), the SLD models utility-source PFC only. Check 7 tolerance still applies but the engineer must document the genset filtering in `compliance_summary.assumptions[]`. Absence of such documentation while mixed-source is detected = warning flag `"INV-11-genset-filtering-undocumented"`.

`stage` records where validation stopped (or `"passed"` for full success).

## INV-12: drawing_layout shape conformance (v1.5+)

**When this check fires:** Only when `output.drawing_layout` is present (backward-compatible — v1.3/v1.4 examples without drawing_layout skip INV-12 entirely).

**Checks (all hard fails):**

1. All `drawing_layout.boards.<id>` keys match a `distribution_hierarchy[].board_id` (no orphan board entries)
   - Fail: `"INV-12: drawing_layout.boards has key <ID> but no board with that board_id in distribution_hierarchy"`

2. All boards in `distribution_hierarchy` appear as keys in `drawing_layout.boards` (no missing entries)
   - Fail: `"INV-12: board <ID> is in distribution_hierarchy but missing from drawing_layout.boards"`

3. All `boards[*].sheet_id` reference an existing `sheets[].sheet_id` (no dangling refs)
   - Fail: `"INV-12: board <BID> declares sheet_id=<SID> but no sheet with that sheet_id in sheets[]"`

4. All `tree_layer` values are ≥0
   - Fail: `"INV-12: board <BID> tree_layer=<N> must be ≥ 0"`

5. All `layout_group` values are in {`main`, `general_power`, `lighting`, `mechanical`, `fire_alarm_life_safety`, `emergency_power`, `comms`, `other`}
   - Fail: `"INV-12: board <BID> layout_group=<G> is not a valid enum value"`

6. All `routing_intent` values are in {`via_main_spine`, `via_dedicated_riser`, `via_shared_tray`, `direct_from_msb`, `via_genset_changeover`}
   - Fail: `"INV-12: board <BID> routing_intent=<R> is not a valid enum value"`

7. All `sheet_size` values are in {`A0`, `A1`, `A2`, `A3`, `Arch_E`, `Arch_D`, `Arch_C`}
   - Fail: `"INV-12: sheet <SID> sheet_size=<S> is not a valid enum value"`

## INV-13: Jurisdictional sheet size (warning, not hard fail)

**When this check fires:** Only when `output.drawing_layout` is present.

**Checks:**

- jurisdiction ∈ {`GB`, `EU`, `INT`, `KE`} → `sheets[*].sheet_size` MUST be ISO (`A0`/`A1`/`A2`/`A3`)
- jurisdiction == `US` → `sheets[*].sheet_size` MUST be ANSI (`Arch_E`/`Arch_D`/`Arch_C`)

**Severity:** WARNING (not hard fail). Engineer override valid if drawing exports both ISO and ANSI formats.

- Warning: `"INV-13: jurisdiction=<J> typically uses <EXPECTED_FAMILY> sheet sizes; sheet <SID> uses <ACTUAL_SIZE>. Override valid if export covers both formats."`

## INV-14: Multi-sheet split logic conformance (v1.5+)

**When this check fires:** Only when `output.drawing_layout` is present.

**Checks:**

1. **Single-sheet rule:** if `len(distribution_hierarchy) ≤ 8` AND no `fire_alarm_life_safety` + `general_power` coexistence → MUST be exactly 1 sheet
   - Hard fail: `"INV-14: <N> boards (≤8) with no life-safety isolation requirement — drawing_layout MUST have exactly 1 sheet, found <M>"`

2. **Multi-sheet rule (count):** if `len(distribution_hierarchy) > 8` → MUST be ≥2 sheets
   - Hard fail: `"INV-14: <N> boards (>8) — drawing_layout MUST have ≥2 sheets, found <M>"`

3. **Life-safety isolation rule:** if any board has `layout_group == "fire_alarm_life_safety"` AND any board has `layout_group == "general_power"` → those boards MUST be on different sheets
   - Hard fail: `"INV-14:life-safety-coexistence — fire_alarm_life_safety board <FAID> shares sheet <SID> with general_power board <GPID>. Required isolation per BS 9999 §6.4 / IEC 60364-5-56:2018 §560 / NFPA 72 §10.6"`

### Backward compatibility

If `drawing_layout` is absent, skip INV-12, INV-13, and INV-14 entirely. v1.3/v1.4 examples remain valid under v1.5 validation rules.

## Architectural state (Sprint 4-AB)

When `architectural_state` is present, the validator MUST surface a
finding for any of:

1. The IR includes geometric placement coordinates derived from the
   architectural state (this is a context-only skill).
2. `unconfirmed_rooms_in_scope > 0` AND the IR's `assumptions` array
   does not mention the unconfirmed rooms when the skill consumed
   them.
3. The IR's `building_label` field (if present) does not match
   `architectural_state.building.label`.

Findings should reference the room ID and the architectural state
payload location so the reviewer can correlate.

See `shared/architectural_state_contract.md` for the full contract.
