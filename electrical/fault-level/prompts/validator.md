# Fault-Level — Validator Prompt

You are validating a fault-level IR document produced by the `electrical/fault-level` skill generator.

## Input
- IR JSON at user-provided path
- Schemas at `electrical/fault-level/schemas/{fault-level-ir,fault-level-intent}.schema.json`

## Validation procedure

### 1. Schema validation
Run JSON-schema validation against `fault-level-ir.schema.json`. If invalid → STOP, emit `{"valid": false, "stage": "schema", "errors": [...]}`.

### 2. Cross-field invariants

**INV-01: Cascade tree integrity.**
Every `cascade[*].parent_node_id` must reference an existing `cascade[*].node_id`. No orphans (except root). No cycles.

**INV-02: Cascade node_id uniqueness.**
All `cascade[*].node_id` values unique. Path-like ids (`MSB-1.F01.DB-L1.C03`) preferred.

**INV-03: Voltage factor c applied.**
Every cascade node with `ifault_ka_max` AND `ifault_ka_min` has `ifault_ka_max > ifault_ka_min`. Difference within `(1.05/0.95 - 1) × ifault = 10.5%` tolerance.

**INV-04: Ifault monotonicity downstream.**
Walking the cascade tree from source: `cascade[child].ifault_ka_max ≤ cascade[parent].ifault_ka_max`. Exception: motor back-feed point may add to downstream — flag as expected.

**INV-05: Peak factor κ consistency.**
For every node, verify `ipk_ka ≈ κ × √2 × ifault_ka_max` where `κ = 1.02 + 0.98 × exp(-3 × R/X)`. Tolerance ±2%.

**INV-06: Breaker adequacy.**
Every entry in `selectivity_implications[*]`: if `adequate: false`, `compliance_summary.compliant` must be `false` AND a `BREAKER_UNDERRATED_FOR_FAULT_LEVEL` flag must exist.

**INV-07: Tool call pending consistency.**
If any `cascade[*].tool_call_pending == true`, top-level `flags` must include `TOOL-CALL-PENDING`.

**INV-08: Source impedance bounds.**
`project_supply.lv_source.z_percent` in [3.0, 12.0] OR flag in non_compliance_flags.
Source X/R in [0.5, 50] OR flag.

**INV-09: Standards citations format.**
Every `compliance_summary.non_compliance_flags[].code_clause` uses canonical format:
- IEC 60909 (analytical method, all jurisdictions): `"IEC 60909-0:2016 §N.N"` or `"IEC 60909-0:2016 Table N"`
- BS 7671 (GB): `"BS 7671:2018+A2:2022 Reg N.N.N"`
- KS 1700 (KE): `"KS 1700:2018 §N.N.N"` direct form — Annex E §VIII routing-note suffix permitted when leading with `KS 1700:` (e.g. `"KS 1700:2018 §434.5 (Annex E: adopts BS 7671:2018+A2 Reg 434.5 verbatim)"`). The trailing annotation `"BS 7671 ... (adopted by KS 1700)"` is BANNED — flag as INV-09 fail.
- IEC 60364 (EU/INT): `"IEC 60364-N-NN:YYYY Clause N.N"`
- NEC (US): `"NEC 2023 Art NNN.N"` or `"NFPA 70:2023 Article NNN.N"`

Cross-contamination ban: `KS 1700` MUST NOT appear when `jurisdiction != "KE"`. `BS 7671` MUST NOT appear as a primary citation when `jurisdiction != "GB"` AND `jurisdiction != "KE"`.

**INV-10: Rationale presence.**
`rationale` block exists with `chat_summary` (40-500 chars) and `sections[]` with ≥8 entries.

**INV-11: Internal consistency — Ik reconciles to c·U/(div·Z).**
Severity HIGH. For every cascade node, the stored `ifault_ka_max` MUST reconcile to the documented IEC 60909 formula within 1%: three-phase `Ik = c × U / (√3 × Z)`, single-phase TN `Ik = c × U₀ / (2 × Z)`, or HV declared PSCC `Ik = declared_value` (do NOT re-multiply by c — ZQ is back-calculated as `ZQ = c × U / (√3 × Ik_declared)` per IEC 60909-0:2016 §3.3.2). Use c = 1.10 for HV nodes (voltage_class > 1 kV) and c = 1.05 for LV nodes per IEC 60909-0:2016 Table 1; U is line-to-line for 3-phase and phase-to-neutral for 1-phase; Z is the node `z_total_ohm` after all upstream impedances summed in series. Validator action: for each node in `cascade[]`, compute the expected Ik from c, U, div, Z; compare to stored `ifault_ka_max`; flag any deviation > 1% with the formula used and the expected value. Special cases: declared PSCC nodes (where `calculation_basis` contains "declared") skip reconciliation but assert the ZQ back-calc holds; motor superposition nodes skip (oracle limitation documented in `functional_audit.py` false-positive disclosure). Rationale: prevents H1+H2+H3 class of defects (TX-1 sub-impedance, double-c-factor on declared PSCC, single-phase z disconnect).

---

**INV-12: Breaking-capacity verdict internal consistency.**

**Severity:** HIGH

**Rule:** For every cascade node carrying a `breaking_capacity` block, the following must hold:

1. **Ik3 self-consistency (with multi-source exception):** `breaking_capacity.ik3_node_ka` MUST equal the actual fault current the device will interrupt at this node. Two cases:
   - **Single-source nodes (utility-only):** `ik3_node_ka` reconciles to `c × U / (div × z_total_ohm) / 1000` within 1% (matches INV-11). The formula and stored `ifault_ka_max` agree.
   - **Multi-source nodes (motor/UPS superposition per IEC 60909-0:2016 §4.5):** `ik3_node_ka` equals the stored `ifault_ka_max` (which includes the motor/UPS contribution). The formula-from-z gives only the utility component and is NOT the device's interrupting requirement. Sprint D1.2 makes the superposition explicit via `superposition_contribution_ka`; until then, infer multi-source nodes from divergence between `ifault_ka_max` and `c·U/(div·Z)` exceeding INV-11's 1% tolerance.

**Validator action update:** for nodes where `ifault_ka_max` diverges from `c·U/(div·Z)` by more than 1% (i.e. multi-source per IEC 60909 §4.5), require `ik3_node_ka == ifault_ka_max` within 0.1%, NOT the formula recompute. For single-source nodes, the original Rule 1 holds.

2. **Headroom arithmetic:** `headroom_pct` reconciles to `((min(device_icn_ka, device_icu_ka) − ik3_node_ka) / ik3_node_ka) × 100` within 0.5%.

3. **Verdict threshold match:** `verdict` matches the threshold table:
   - `ok` if `headroom_pct >= 10`
   - `marginal` if `0 <= headroom_pct < 10`
   - `inadequate` if `headroom_pct < 0`

4. **Data source consistency:** `data_source ∈ {"db_layout_intent", "engineer_declared"}`. If `"db_layout_intent"`, then `meta.consumed_intents[]` must include a db-layout entry.

5. **At least one device rating present:** at least one of `device_icn_ka` or `device_icu_ka` must be present and > 0.

**Validator action:** for each cascade node with `breaking_capacity`, recompute ik3 and headroom_pct; assert verdict matches threshold; assert data_source consistency. Flag any mismatch > 1% (ik3) or > 0.5% (headroom) or wrong verdict bucket.

**Rationale:** Makes fault-level self-sufficient for switchgear selection per BS 7671 Reg 432.1.2 / NEC §110.9 / IEC 60947-2 — engineer no longer has to manually cross-check Ik vs device Icn/Icu. INV catches authoring drift.

---

**INV-13: Superposition self-consistency.**

**Severity:** HIGH

**Rule:** For every cascade node carrying `superposition_contribution_ka`:

1. **Internal sum match:** `total == Σ(non-total entries)` within 1%.

2. **Total matches ifault_ka_max:** `total == ifault_ka_max` within 1%.

3. **Cross-walk to sources[]:** for every key `<kind>_<id>` in `superposition_contribution_ka`, the source with `id == <id>` exists in IR root `sources[]`. Conversely, every `sources[*].contributes_to_nodes[this_node_id]` value equals the corresponding `superposition_contribution_ka[<source_kind>_<source_id>]` within 1%.

4. **Non-negative contributions:** all per-source values ≥ 0 (negative contributions are nonsensical for IEC 60909 superposition).

**Validator action:** for each cascade node, walk the contribution map; reconcile internal sum + cross-walk against sources[].contributes_to_nodes; flag any mismatch > 1%.

**Rationale:** Makes the IEC 60909 §4.5 superposition contributions explicit and attributable. Clears the audit's motor-superposition oracle false-positive on us-industrial-with-motors/MCC-1 once a future oracle update reads the contribution map (oracle update OUT OF SCOPE for D1 — Item 2 makes the data explicit; oracle improvement is post-D-program work). Pairs with D1.1's `ik3_basis` enum which schema-attests multi-source nodes from the breaking-capacity side.

---

**INV-14: Decrement curve monotonicity + bounds.**

**Severity:** HIGH

**Rule:** For every cascade node carrying `decrement_curve`:

1. **Monotonic decay:** `ik_initial_subtransient_ka >= ik_transient_ka >= ik_steady_state_ka` (Park's equations require monotonic decay; any inversion is a calc error).

2. **Initial = node Ik max (conditional):** `ik_initial_subtransient_ka == ifault_ka_max` within 1% **ONLY WHEN** `decrement_curve.applies_when` describes the same supply state that produced `ifault_ka_max`. If the two describe different supply states (e.g. `decrement_curve` documents the standby/genset-fed state while `ifault_ka_max` documents the normal/utility-fed state), Rule 2 is N/A; instead require that `ik_initial_subtransient_ka` independently reconciles to `c × U_n / (√3 × Z_M)` from the relevant source's reactances (the curve-side calc), and `applies_when` MUST state the divergence explicitly.

3. **Time-series bounds:** every `time_series_samples[*].ik_ka` lies between `ik_steady_state_ka` (lower bound) and `ik_initial_subtransient_ka` (upper bound) within 5% tolerance for numerical rounding.

4. **Monotonic time:** `time_series_samples[*].t_ms` strictly increasing.

5. **First sample at t=0:** `time_series_samples[0].t_ms == 0` and `samples[0].ik_ka == ik_initial_subtransient_ka` within 0.5%.

6. **Machine-data source consistency:** if `decrement_model == "iec_60909_4_3_full_park"` AND the producing source has `decrement_profile.machine_data_source == "typical_ieee_c50_13"`, then the machine reactances must fall within published IEEE C50.13 Table 1 typical ranges (Xd'': 0.05–0.40; Xd': 0.10–0.50; Xd: 0.5–3.0 — matches the schema's min/max).

**Validator action:** for each cascade node with `decrement_curve`, walk the samples; check monotonicity in t and Ik; verify Ik'' = ifault; verify samples lie in bounds; verify machine_reactances within typical range when claimed typical.

**Rationale:** Catches Park's-equation authoring errors (sign mistakes, non-monotonic decay, samples drifting outside bounds). Required for the protection-coordination skill (currently stubbed) to do its job — it'll consume `ik_transient_ka` for relay time-grading.

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

`valid: true` requires schema pass + all 14 invariants pass + intent extraction valid.

## Floor plan context

When the prompt context includes a `## Floor plan context` markdown
block, the validator MUST surface a finding for any of:

1. IR includes coordinate-level geometric placement claims derived
   from the block (this is a context-only skill).
2. IR's `building_label` field (if present) does not match the
   building label in the block.
3. IR omits `floor_plan_context_consumed: true` when the block was
   present.

Findings should cite the room name and the block location so the
reviewer can correlate.
