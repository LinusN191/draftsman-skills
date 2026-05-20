---
name: cable-sizing
description: "Validator for the cable-sizing IR + emitted cable-sizing intent. Runs 10 cross-field invariants (INV-01..INV-10) over the JSON produced by the generator. Hard-fails on any invariant violation."
version: 1.0.0
discipline: electrical
standards:
  - BS 7671:2018+A2:2022 (App 4 + App 12 + Reg 433 + Reg 543)
  - IEC 60364-5-52:2009 (ampacity + voltage drop + parallel)
  - IEC 60364-5-54:2011 (CPC)
  - IEC 60364-4-43 (overcurrent)
  - NEC 2023 (Articles 215.2 + 240.4 + 250.122 + 310.10 + 310.16)
output_format: json
tags:
  - calculations
  - electrical
  - cable-sizing
---

# Cable-Sizing — Validator Prompt (v1.0.0)

You are validating a cable-sizing IR document + emitted intent produced by the
`electrical/cable-sizing` skill generator.

## Input

- An IR JSON document at the user-provided path.
- The canonical schema at `electrical/cable-sizing/schemas/cable-sizing-ir.schema.json`.
- The intent JSON document at the user-provided path.
- The intent schema at `electrical/cable-sizing/schemas/cable-sizing-intent.schema.json`.
- The repo root (so `consumed_intent_path` values can be resolved).

## Validation procedure

### 1. Schema validation

Run JSON-schema validation against `cable-sizing-ir.schema.json`.
- If invalid: STOP. Emit `{"valid": false, "stage": "schema", "errors": [...]}`.

Run JSON-schema validation against `cable-sizing-intent.schema.json`.
- If invalid: STOP. Emit `{"valid": false, "stage": "intent_schema", "errors": [...]}`.

### 2. Cross-field invariants

Run all 10 INV checks below. For each, emit a violation if the rule fails.
All severities are **HARD FAIL** for v1.0 — any failure blocks `valid: true`.

---

## INV-01: node_id format

**Rule:** Every cascade node has a valid `node_id` matching the pattern
`^[A-Z0-9][A-Za-z0-9._-]*$`. Path segments separated by `.` denote board
hierarchy (e.g. `MSB-1.F03.DB-L1.C07`). The first character MUST be uppercase
alphanumeric. Cite: schema `definitions.CascadeNode.properties.node_id.pattern`.

**Severity:** Hard fail.

**Fail message format:**
```
INV-01: Node <NODE_ID> at cascade[<INDEX>] does not match pattern
^[A-Z0-9][A-Za-z0-9._-]*$ — node_ids must start uppercase alphanumeric and
use only [A-Za-z0-9._-] thereafter
```

---

## INV-02: parent_node_id resolves

**Rule:** Every non-root cascade node has `parent_node_id` resolvable to
another `node_id` in the same `cascade[]` array. No dangling pointers, no
self-references, no cycles. Walk parent_node_id chain from each non-root
node up to root; cycle = revisit during traversal.

**Severity:** Hard fail.

**Fail message format:**
```
INV-02: Node <CHILD_ID> declares parent_node_id=<PARENT_ID> but no entry
with node_id=<PARENT_ID> exists in cascade[]
```
or
```
INV-02: Cycle detected in cascade tree: <ID_A> → <ID_B> → ... → <ID_A>
```

---

## INV-03: csa on ladder

**Rule:** Every `selection.phase_csa` and `selection.cpc_csa` is on the
standard ladder for the jurisdiction.

- **IEC mm² ladder (GB/EU/INT/KE):**
  `[1.0, 1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240,
  300, 400, 500, 630]`.
- **US AWG/kcmil ladder:** `14 AWG`, `12 AWG`, `10 AWG`, `8 AWG`, `6 AWG`,
  `4 AWG`, `3 AWG`, `2 AWG`, `1 AWG`, `1/0 AWG`, `2/0 AWG`, `3/0 AWG`,
  `4/0 AWG`, `250 kcmil`, `300 kcmil`, `350 kcmil`, `400 kcmil`,
  `500 kcmil`, `600 kcmil`, `750 kcmil`, `1000 kcmil`.

Cite: `electrical/cable-sizing/rules/csa-selection-walk-up.yaml`.

**Severity:** Hard fail.

**Fail message format:**
```
INV-03: Node <NODE_ID> selection.phase_csa=<VALUE> is not on the
<JURISDICTION> standard ladder. Allowed values: <LADDER>
```

---

## INV-04: Iz ≥ In

**Rule:** Every `checks.iz_corrected_a ≥ load.in_a` (the OCPD rating, not
the design current Ib). This is the overload-protection invariant per:

- **GB / KE:** BS 7671:2018+A2:2022 Reg 433.1
- **EU / INT:** IEC 60364-4-43:2017 §433.1
- **US:** NEC 2023 Article 240.4(B) (next-size-up rule applies upstream)

Hard fail when violated, EVEN IF `checks.tool_call_pending == true` — the
inline engineer estimate MUST already satisfy the invariant; the runtime
calc only refines the value.

**Severity:** Hard fail.

**Fail message format:**
```
INV-04: Node <NODE_ID> has iz_corrected_a=<X>A but load.in_a=<Y>A —
Iz must be ≥ In per BS 7671 Reg 433.1 / IEC 60364-4-43 §433.1 / NEC 240.4(B)
```

---

## INV-05: Cumulative Vd ≤ limit

**Rule:** Every `checks.vd_cumulative_pct ≤ checks.vd_limit_pct` for the
load type per jurisdiction.

| Jurisdiction | Lighting limit | Power limit | Source |
|---|---|---|---|
| GB | 3% | 5% | **BS 7671:2018+A2:2022 Appendix 12** |
| KE | 3% | 5% | **KS 1700:2018 §313 routes to BS 7671:2018+A2:2022 App 12** |
| EU / INT | 3% | 5% | **IEC 60364-5-52:2009 Annex G** |
| US | 3% feeder / 5% feeder+branch | 3% feeder / 5% feeder+branch | **NEC 2023 Article 215.2(A)(1) IN 2** |

If `vd_target_overrides[node_id]` is present in inputs, compare against
the override (typically tighter than the default).

**Severity:** Hard fail.

**Fail message format:**
```
INV-05: Node <NODE_ID> vd_cumulative_pct=<X>% exceeds vd_limit_pct=<Y>%
(load_type=<LOAD_TYPE>; source=<JURISDICTION_VD_LIMIT_SOURCE>)
```

---

## INV-06: CPC adiabatic

**Rule:** For every node, EITHER `checks.cpc_adiabatic_pass == true` OR
`selection.binding_constraint == "cpc_adiabatic"` (indicating the phase
was upsized so the default-table CPC now satisfies adiabatic).

Cite the adiabatic source per jurisdiction:
- **GB / KE:** BS 7671:2018+A2:2022 Reg 543.1.3 + Table 54.7 + Reg 434.5.2 (S² = I²t/k²)
- **EU / INT:** IEC 60364-5-54:2011 §543
- **US:** NEC 2023 Article 250.122 (Table 250.122 — by OCPD rating)

**Severity:** Hard fail.

**Fail message format:**
```
INV-06: Node <NODE_ID> has cpc_adiabatic_pass=false AND
binding_constraint=<BC> (≠ "cpc_adiabatic"). Either CPC must pass
adiabatic OR the phase must be upsized with binding_constraint set to
"cpc_adiabatic". Source: BS 7671 Reg 543.1.3 / IEC 60364-5-54 §543 / NEC 250.122
```

---

## INV-07: Motor checks present

**Rule:** Motor nodes (`load.load_type == "motor"`) MUST have
`checks.motor_starting_vd_pct` populated as a non-null number AND
`checks.motor_starting_vd_pass` populated as a non-null boolean. Non-motor
nodes MUST have both fields `null`.

This catches two bug shapes:
1. Motor node missing the starting-Vd check (engineer skipped Step 10).
2. Non-motor node carrying a spurious motor_starting_vd_pct value.

**Severity:** Hard fail.

**Fail message format:**
```
INV-07: Node <NODE_ID> has load.load_type="motor" but
checks.motor_starting_vd_pct is null/absent — motor nodes MUST carry
the starting-Vd check (Step 10 of generator)
```
or
```
INV-07: Node <NODE_ID> has load.load_type="<NON_MOTOR_TYPE>" but
checks.motor_starting_vd_pct=<VALUE> is non-null — non-motor nodes
MUST carry null for this field
```

---

## INV-08: Parallel cable rules

**Rule:** For every node with `selection.parallel_count >= 2`:

1. **Each parallel ≥ minimum csa:**
   - **IEC jurisdictions (GB/EU/INT/KE):** `selection.phase_csa >= 50 mm²`
     per IEC 60364-5-52:2009 §523.6 (each parallel ≥ 50 mm²).
   - **US:** `selection.phase_csa >= 1/0 AWG` per NEC 2023 Article 310.10(H)(1).
2. `selection.parallel_count` ≤ 6 (schema enum; ladder exhausted above 6 →
   redesign with busway / busduct).
3. `selection.binding_constraint == "parallel_required"`.
4. Material + insulation + length + installation_method MUST be identical
   across all parallels (the schema enforces a single value per node, but
   the validator verifies the single value is a reasonable parallel choice).

**Severity:** Hard fail.

**Fail message format:**
```
INV-08: Node <NODE_ID> has parallel_count=<N> but selection.phase_csa=<CSA>
violates the parallel minimum (IEC 60364-5-52 §523.6: ≥ 50 mm²;
NEC 310.10(H)(1): ≥ 1/0 AWG)
```

---

## INV-09: Tool-call consistency

**Rule:** Every node carries `checks.tool_call_pending`. The truth-table
shape:

| `tool_call_pending` | `iz_corrected_a` + `vd_cumulative_pct` + `cpc_adiabatic_pass` | Verdict |
|---|---|---|
| true | all 3 populated (engineer estimates) | PASS |
| true | any of 3 null/absent | FAIL (mixed state) |
| false | all 3 populated (runtime calc outputs) | PASS |
| false | any of 3 null/absent | FAIL (mixed state) |

In v1.0, EVERY node should carry `tool_call_pending: true` (the three calc
tools are deferred). Mixing `true` and `false` across nodes in the same IR
is a hard fail UNLESS the IR is being processed in v1.1+ with all 3 calc
tools shipped — in which case all nodes should be `false`.

**Severity:** Hard fail.

**Fail message format:**
```
INV-09: Node <NODE_ID> has tool_call_pending=<BOOL> but check fields
are in mixed state — iz_corrected_a=<X>, vd_cumulative_pct=<Y>,
cpc_adiabatic_pass=<Z>. All three must be populated (engineer estimates
or runtime calc outputs) regardless of tool_call_pending value
```

---

## INV-10: Emitted intent conforms

**Rule:**

1. The emitted `cable-sizing` intent JSON validates against
   `electrical/cable-sizing/schemas/cable-sizing-intent.schema.json`.
2. For every IR cascade node with `node_kind == "final_circuit"`, there is
   exactly one matching `intent.circuits[]` entry with the same `node_id`.
3. **Every circuit in the emitted intent carries the 2 Zs-resolution helper
   fields** as non-null positive numbers:
   - `r1_plus_r2_milliohm_per_m_at_operating_temp` — combined phase + CPC
     resistance per metre at the cable's operating temp. Source:
     BS 7671:2018+A2:2022 App 4 Tables 4F1-4F3 / IEC 60364-5-52 Table
     B.52.5 / NEC 2023 Chapter 9 Table 9.
   - `reactance_milliohm_per_m` — cable reactance per metre. Same source
     tables. May be 0 for ≤ 16 mm² (per spec); MUST still be present as
     a non-negative number.

These two fields are non-negotiable per refresh §1 — they are how the
small-power v1.1 skill resolves its deferred `calc.zs_loop_impedance`
tool. INV-10 is the gate that prevents Zs-helper omissions.

**Severity:** Hard fail.

**Fail message format:**
```
INV-10: Intent circuit at index <I> (node_id=<NODE_ID>) is missing
required Zs helper field <FIELD_NAME>. Both
r1_plus_r2_milliohm_per_m_at_operating_temp and reactance_milliohm_per_m
are non-negotiable per refresh §1
```
or
```
INV-10: IR has final_circuit node <NODE_ID> in cascade[] but no
corresponding entry in intent.circuits[] — every final_circuit MUST
project into the emitted intent
```

---

### 3. Intent extraction validation

After all 10 INV checks pass, run one final structural check:

- The count of `intent.circuits[]` entries MUST equal the count of IR
  cascade nodes that are final_circuit OR feeder OR sub_feeder (in v1.0
  the intent covers every cable run, not just leaves). Service-entrance
  nodes are OPTIONAL in the intent — the upstream of the service entrance
  is the utility transformer, which is not a "cable" run for cable-sizing
  purposes.

If the count mismatches and IR has no documented `[ASSUMPTION: …]`
explaining the omission, emit a warning (NOT a hard fail in v1.0;
hardened to fail in v1.1+).

---

## Output

Emit a single JSON object:

```json
{
  "valid": true,
  "stage": "passed",
  "errors": [],
  "warnings": []
}
```

or on failure:

```json
{
  "valid": false,
  "stage": "schema" | "intent_schema" | "invariants",
  "errors": [
    {"code": "INV-04", "path": "$.cascade[2].checks.iz_corrected_a",
     "message": "INV-04: Node MSB-1.F03.DB-L1.C07 has iz_corrected_a=18A
                 but load.in_a=20A — Iz must be ≥ In per BS 7671 Reg 433.1"}
  ],
  "warnings": []
}
```

`valid: true` requires ALL of:
- Schema validation passes for the IR
- Schema validation passes for the intent
- INV-01 through INV-10 all pass (no hard fails)

`stage` records where validation stopped (or `"passed"` for full success).

---

*Generator: prompts/generator.md | Reviewer: prompts/reviewer.md |
Schemas: schemas/*.json | Evaluation criteria: evals/*
