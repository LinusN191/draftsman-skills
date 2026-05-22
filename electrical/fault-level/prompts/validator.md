# Fault-Level — Validator Prompt

You are validating a fault-level IR document produced by the `electrical/fault-level` skill generator.

## Input
- IR JSON at user-provided path
- Schemas at `electrical/fault-level/schemas/{fault-level-ir,fault-level-intent}.schema.json`

## Validation procedure

### 1. Schema validation
Run JSON-schema validation against `fault-level-ir.schema.json`. If invalid → STOP, emit `{"valid": false, "stage": "schema", "errors": [...]}`.

### 2. Cross-field invariants

**INV-1: Cascade tree integrity.**
Every `cascade[*].parent_node_id` must reference an existing `cascade[*].node_id`. No orphans (except root). No cycles.

**INV-2: Cascade node_id uniqueness.**
All `cascade[*].node_id` values unique. Path-like ids (`MSB-1.F01.DB-L1.C03`) preferred.

**INV-3: Voltage factor c applied.**
Every cascade node with `ifault_ka_max` AND `ifault_ka_min` has `ifault_ka_max > ifault_ka_min`. Difference within `(1.05/0.95 - 1) × ifault = 10.5%` tolerance.

**INV-4: Ifault monotonicity downstream.**
Walking the cascade tree from source: `cascade[child].ifault_ka_max ≤ cascade[parent].ifault_ka_max`. Exception: motor back-feed point may add to downstream — flag as expected.

**INV-5: Peak factor κ consistency.**
For every node, verify `ipk_ka ≈ κ × √2 × ifault_ka_max` where `κ = 1.02 + 0.98 × exp(-3 × R/X)`. Tolerance ±2%.

**INV-6: Breaker adequacy.**
Every entry in `selectivity_implications[*]`: if `adequate: false`, `compliance_summary.compliant` must be `false` AND a `BREAKER_UNDERRATED_FOR_FAULT_LEVEL` flag must exist.

**INV-7: Tool call pending consistency.**
If any `cascade[*].tool_call_pending == true`, top-level `flags` must include `TOOL-CALL-PENDING`.

**INV-8: Source impedance bounds.**
`project_supply.lv_source.z_percent` in [3.0, 12.0] OR flag in non_compliance_flags.
Source X/R in [0.5, 50] OR flag.

**INV-9: Standards citations format.**
Every `compliance_summary.non_compliance_flags[].code_clause` uses canonical format:
- IEC 60909 (analytical method, all jurisdictions): `"IEC 60909-0:2016 §N.N"` or `"IEC 60909-0:2016 Table N"`
- BS 7671 (GB): `"BS 7671:2018+A2:2022 Reg N.N.N"`
- KS 1700 (KE): `"KS 1700:2018 §N.N.N"` direct form — Annex E §VIII routing-note suffix permitted when leading with `KS 1700:` (e.g. `"KS 1700:2018 §434.5 (Annex E: adopts BS 7671:2018+A2 Reg 434.5 verbatim)"`). The trailing annotation `"BS 7671 ... (adopted by KS 1700)"` is BANNED — flag as INV-9 fail.
- IEC 60364 (EU/INT): `"IEC 60364-N-NN:YYYY Clause N.N"`
- NEC (US): `"NEC 2023 Art NNN.N"` or `"NFPA 70:2023 Article NNN.N"`

Cross-contamination ban: `KS 1700` MUST NOT appear when `jurisdiction != "KE"`. `BS 7671` MUST NOT appear as a primary citation when `jurisdiction != "GB"` AND `jurisdiction != "KE"`.

**INV-10: Rationale presence.**
`rationale` block exists with `chat_summary` (40-500 chars) and `sections[]` with ≥8 entries.

### 3. Intent extraction validation

Project IR → `fault-level` intent shape. Validate against `fault-level-intent.schema.json`. Intent must contain `project_id`, `source_summary`, `fault_currents[]` (≥1 entry).

## Output

```json
{
  "valid": true | false,
  "stage": "schema" | "invariants" | "intent" | "passed",
  "errors": [
    {"code": "INV-N", "path": "$.cascade[2]", "message": "..."}
  ],
  "warnings": [...]
}
```

`valid: true` requires schema pass + all 10 invariants pass + intent extraction valid.
