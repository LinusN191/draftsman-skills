# Sprint D1 — Protection & Safety depth (design spec)

**Date:** 2026-05-25
**Sprint program:** within-skill depth (D1/D2/D3) closing depth gaps inside 5 beta skills before pivoting to breadth-first new-skill builds. See `[[within-skill-depth-plan]]` memory.
**Scope:** 4 depth items across 2 skills (fault-level + arc-flash); ~3 Opus dev-days.
**Predecessor:** Sprints A–C cleared the 43-finding external audit. The Sprint D follow-up (commit `bd17594`) created 9 separate-skill stubs for depth items that warranted their own skill. This sprint covers the 4 items that stay INSIDE fault-level + arc-flash.

---

## §1 Architecture overview

Four depth items, sequential within fault-level (each builds on the prior's schema), arc-flash item parallel near the end.

| # | Skill | Item | Effort |
|---|---|---|---|
| 1 | fault-level | Breaking-capacity verdict per cascade node (hybrid db-layout consumer + engineer fallback) | ~1 day |
| 2 | fault-level | Explicit motor/UPS superposition modeling (hybrid: `sources[]` root authority + per-node contribution map) | ~0.5 day |
| 3 | fault-level | Decrement curves for near-generator nodes (full Park's-equations time-series) | ~1 day |
| 4 | arc-flash | Equipment-condition assumptions with full calc adjustment (1.25× IE adder for abnormal) | ~0.5 day |

Each item follows the established pattern:

1. **IR schema addition** (additive — new optional properties; existing examples don't break)
2. **Generator prompt step** (new numbered step instructing the LLM how to populate)
3. **Validator INV** (asserts internal consistency of the new fields)
4. **Example update** (existing examples gain the new field where applicable; 1 new example added for arc-flash abnormal-condition)
5. **CHANGELOG patch-bump** (per skill)

**INV-numbering placeholders** (`INV-NN`, `INV-NN+1`, `INV-NN+2`, etc. throughout this spec) **resolve at plan-writing time** by reading each validator.md's current count and appending sequentially (e.g. if fault-level/prompts/validator.md currently ends at INV-11, the breaking-capacity INV becomes INV-12; superposition INV becomes INV-13; decrement INV becomes INV-14). The plan must do this resolution explicitly and zero-pad per the Sprint B.5 fix-pass-2 convention (INV-01 not INV-1).

**Pre-flight assumption:** validate-examples.py stays at 219/219+ after each item; functional_audit.py stays ≤ 1 finding (the motor-superposition disclaimed FP). New examples increase the denominator; never decrease pass count.

---

## §2 Item 1 — fault-level breaking-capacity verdict (hybrid consumer)

### Engineering intent

Today fault-level outputs `ifault_ka_max` per node. The engineer then manually checks each switching device's Icn/Icu against that Ik to decide if the design is safe. This item makes that check first-class: every cascade node carries a `breaking_capacity` block with the device data, the recomputed Ik3, the headroom, and a verdict (ok / marginal / inadequate). The skill becomes self-sufficient for switchgear-rating verification per BS 7671 Reg 432.1.2 / NEC §110.9 / IEC 60947-2.

### Schema addition (per cascade node, optional initially)

```json
"breaking_capacity": {
  "device_id": "string (engineer reference, e.g. 'MS-1' or 'OCPD-C03')",
  "device_type": "MCB | MCCB | ACB | fuse_BS88 | fuse_NEC | air_circuit_breaker",
  "device_icn_ka": "number (rated short-circuit breaking capacity per BS EN 60898 / IEC 60947-2 Annex)",
  "device_icu_ka": "number (ultimate short-circuit breaking capacity, IEC 60947-2)",
  "device_ics_ka": "number (service short-circuit breaking capacity, optional — typically 0.5–1.0 × Icu)",
  "device_icw_ka_1s": "number (rated short-time withstand at 1 second, optional, ACBs only)",
  "ik3_node_ka": "number (recomputed from this node's z_total_ohm)",
  "headroom_pct": "number (((min(Icn, Icu) − Ik3) / Ik3) × 100)",
  "verdict": "ok | marginal | inadequate",
  "verdict_basis": "string (citation: BS 7671:2018+A2:2022 Reg 432.1.2 / NEC 2023 §110.9 / IEC 60947-2)",
  "data_source": "db_layout_intent | engineer_declared"
}
```

### Data source (hybrid pattern)

Matches the established cable-sizing v1.1 + small-power v1.1 hybrid-consumer precedent:

1. **When `db-layout` is in `consumed_intents`:** generator reads `main_switch.rating_a` + `main_switch.icn_ka` + `outgoing_circuits[*].ocpd` from the consumed intent. `data_source: "db_layout_intent"`.
2. **When `db-layout` intent absent:** engineer declares device data in the existing `cascade_topology_declared` block per-node. `data_source: "engineer_declared"`.

This keeps fault-level usable standalone (early-stage design before db-layout is authored) while closing the cross-skill story when both are present.

### Verdict thresholds

| Headroom | Verdict | Engineering meaning |
|---|---|---|
| ≥ 10% | `ok` | Comfortable margin against transformer impedance tolerance + future load growth |
| 0 – 10% | `marginal` | Within tolerance but no growth headroom; consider uprating at next refresh |
| < 0% | `inadequate` | Device cannot interrupt the prospective short-circuit — non-compliant per Reg 432.1.2 / NEC §110.9 |

### Generator prompt step (insert in fault-level/prompts/generator.md)

```markdown
### Step N: Breaking-capacity verdict per cascade node

For every cascade node, look up the device protecting it (the OCPD upstream
of the node OR the main switch at the supply boundary):

1. If `db-layout` is in `consumed_intents`: read device data from the
   consumed intent. `main_switch.rating_a + .icn_ka` for the service-entrance
   node; `outgoing_circuits[*].ocpd` for downstream nodes (match by node_id).
2. Otherwise read engineer-declared device data from
   `cascade_topology_declared[*].device`.

Compute the verdict:

```
headroom_pct = ((min(device_icn_ka, device_icu_ka) - ik3_node_ka) / ik3_node_ka) × 100
verdict = "ok" if headroom_pct ≥ 10
        else "marginal" if 0 ≤ headroom_pct < 10
        else "inadequate"
```

Emit the breaking_capacity block per spec §2. Cite verdict_basis per
jurisdiction (BS 7671 Reg 432.1.2 GB; NEC §110.9 US; IEC 60947-2 INT;
KS 1700 §432 routes to BS 7671 for KE).
```

### Validator INV — `INV-NN: breaking-capacity-verdict-internal-consistency`

**Rule:** For every cascade node carrying a `breaking_capacity` block:
- `ik3_node_ka` reconciles to `c · U / (div · z_total_ohm) / 1000` within 1% (uses the Sprint B.1 INV-11 reconcile rule on the same node)
- `headroom_pct = ((min(device_icn_ka, device_icu_ka) − ik3_node_ka) / ik3_node_ka) × 100` within 0.5%
- `verdict` matches the threshold table for the computed headroom
- `data_source` ∈ {`db_layout_intent`, `engineer_declared`}; if `db_layout_intent`, then `consumed_intents` must include a db-layout entry

**Severity:** HIGH.

### Example updates

All 6 existing fault-level examples gain the `breaking_capacity` block on at least:
- The service-entrance node (HV-1 / TX-1 / lv_source)
- The MSB main switch node
- One representative downstream node per example

`uk-commercial-3storey`, `us-strip-mall-retail`, `ke-nairobi-industrial`: clean engineering, all verdicts `ok`.
`intl-commercial-with-genset`: TX-1 verdict reflects the corrected 43.49 kA Ik (post-Sprint-B.1) — likely shows `marginal` headroom at 50 kA Icu (13% — already documented in B.1 SLD ripple).
`uk-domestic-single-source`: trivial — 60A consumer-unit Icn vs 1.5 kA Ik → ok with massive headroom.
`us-industrial-with-motors`: MCC-1 verdict uses 35.0 kA Ik (post-superposition from Item 2 below).

---

## §3 Item 2 — fault-level explicit motor/UPS superposition (hybrid representation)

### Engineering intent

Today, motor contribution at the us-industrial MCC node is stored as the final value (`ifault_ka_max: 35.0`) without breakdown. The audit oracle flags this as a discrepancy because its recompute formula uses utility-only (`Ik = c·U/(√3·Z) ≈ 31.98`); the missing 3 kA is the motor back-feed per IEC 60909 §4.5. This item makes the breakdown explicit so consumers (arc-flash, sld, the audit oracle) can attribute every kA.

### Schema additions (two locations — hybrid pattern per Q2 decision)

**At IR root (canonical authority):** extend the existing `sources[]` entries with `contributes_to_nodes`:

```json
"sources": [
  {
    "id": "S1",
    "kind": "utility",
    "ik3_at_source_ka": 22.5,
    "contributes_to_nodes": {
      "HV-1": 22.5,
      "TX-1": 41.86,
      "MSB-1": 33.34,
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
    "_source_aggregation": "Σ I_LR for declared motors per IEC 60909 §3.8"
  }
]
```

**At each cascade node (read-convenience map):**

```json
"superposition_contribution_ka": {
  "utility_S1": 31.98,
  "motor_aggregate_S2": 3.02,
  "total": 35.0
}
```

The two representations carry the same data — the root-level `sources[].contributes_to_nodes` is authoritative; the per-node map is for downstream-consumer read convenience (arc-flash reads it directly without cross-walking).

### Generator prompt step

```markdown
### Step N+1: Motor/UPS superposition explicit modeling per IEC 60909 §4.5

For each cascade node, identify every source that contributes fault current
to it. Standard sources:

- Utility transformer: contributes via z-cascade (already covered by INV-11)
- Generator (when bonded by ATS in normal-supply state): contributes via
  z-cascade; in standby state, ATS open, no contribution
- Motor aggregate (induction motors > 100 kW typically; or > 1% of node Ik):
  contributes back-feed per IEC 60909 §3.8 formula
  Ik_motor_aggregate ≈ 1 / Z_M_pu × I_n × √(rated_power_kva / 1000)
  Sum across declared motors. Decays per IEC 60909 §4.3 — see Item 3 if
  applicable.
- UPS (static inverter, output-bonded): contributes let-through current
  during inverter short-circuit current limit phase (typically 1.0–2.0 × In
  for 100 ms before electronic trip). Treat as engineer-declared until the
  electrical/ups/ skill ships its intent (planned in breadth-first phase).

Populate both representations:
1. sources[].contributes_to_nodes: per-source contributions to each node
2. cascade[].superposition_contribution_ka: per-node breakdown + total

Verify sum(per-node-map) == ifault_ka_max within 1%.
```

### Validator INV — `INV-NN+1: superposition-self-consistency`

**Rule:** For every cascade node carrying `superposition_contribution_ka`:
- `sum(non-total entries) == .total` within 1%
- `.total == ifault_ka_max` within 1%
- Every source_id in the contribution map exists in IR root `sources[*].id`
- Conversely, every `sources[*].contributes_to_nodes[node_id]` value matches the node's `superposition_contribution_ka.{source_kind}_{source_id}` within 1%

**Severity:** HIGH.

### Example updates

`us-industrial-with-motors/MCC-1`: gains the explicit breakdown — clears the motor-superposition oracle FP (the audit will see the contribution_map and stop flagging).
`intl-commercial-with-genset`: generator contribution made explicit when ATS in normal-supply state.
`uk-commercial-3storey, ke-nairobi-industrial, us-strip-mall-retail, uk-domestic-single-source`: utility-only contributions; per-node map degenerates to `{utility_S1: <ik>, total: <ik>}`.

### Forward compatibility: UPS + motor-design skills

Per `electrical/ups/` stub (status: stub, future build) — when that skill ships, it will produce a `ups` intent including a `fault_contribution: {let_through_ka, time_to_trip_ms, ...}` block. fault-level will then **consume that intent** when `consumed_intents` includes ups, automatically populating `sources[].kind: "ups"` entries — matching the hybrid pattern in Item 1 for db-layout consumption. Until then, UPS entries in `sources[]` are engineer-declared.

Same forward-compatibility applies to `motor_aggregate`: when a future `motor-design` skill (not yet stubbed) ships, fault-level will consume its intent for motor data. No `motor-design` stub exists today; the depth gap for motor selection lives in the breadth-first roadmap.

---

## §4 Item 3 — fault-level decrement curves (full Park's time-series)

### Engineering intent

For cascade nodes downstream of a synchronous machine (generator) or large induction motor in fault-feed mode, Ik decays over time per IEC 60909 §4.3 — from the subtransient state Ik″ (t = 0+, used for switchgear rating + arc-flash) through transient Ik′ (~100 ms – 3 s, used for protection coordination) to steady-state Ik (> 3 s, used for sizing + thermal). The full time-series captures all three regimes plus DC component decay per Park's equations.

### Schema addition (per cascade node — only when applies)

```json
"decrement_curve": {
  "applies_when": "downstream of synchronous_generator OR large induction motor (>1000 kW) in fault-feed mode",
  "ik_initial_subtransient_ka": "Ik\" at t=0+",
  "ik_transient_ka": "Ik' at ~100ms–3s (Park's transient state)",
  "ik_steady_state_ka": "Ik at >3s",
  "subtransient_time_constant_td_pp_ms": "Td\" per IEC 60909 §4.3 (typical 30-50 ms for synchronous gen)",
  "transient_time_constant_td_p_ms": "Td' per IEC 60909 §4.3 (typical 0.5-2 s)",
  "armature_time_constant_ta_ms": "Ta — DC component decay (typical 50-200 ms)",
  "machine_reactances_pu": {
    "xd_pp_pu": "Xd\" subtransient (typical 0.10-0.20)",
    "xd_p_pu": "Xd' transient (typical 0.15-0.30)",
    "xd_pu": "Xd synchronous (typical 1.0-2.0)"
  },
  "time_series_samples": [
    {"t_ms": 0, "ik_ka": "...", "x_over_r": "..."},
    {"t_ms": 10, "ik_ka": "...", "x_over_r": "..."},
    {"t_ms": 50, "ik_ka": "...", "x_over_r": "..."},
    {"t_ms": 100, "ik_ka": "...", "x_over_r": "..."},
    {"t_ms": 500, "ik_ka": "...", "x_over_r": "..."},
    {"t_ms": 1000, "ik_ka": "...", "x_over_r": "..."},
    {"t_ms": 3000, "ik_ka": "...", "x_over_r": "..."},
    {"t_ms": 10000, "ik_ka": "...", "x_over_r": "..."}
  ],
  "decrement_model": "iec_60909_4_3_full_park",
  "machine_data_source": "engineer_declared | nameplate | typical_iec_50050 | typical_ieee_c50_13",
  "_source": "IEC 60909-0:2016 §4.3 + IEEE C50.13 generator typical characteristics"
}
```

### Compute model

Park's equations (cite IEC 60909-0:2016 §4.3):

```
Ik(t) = (Ik" - Ik') × e^(-t/Td") + (Ik' - Ik) × e^(-t/Td') + Ik
     + DC_component(t) where DC_component(t) = √2 × Ik" × e^(-t/Ta)
```

When the engineer doesn't provide machine reactances, use typical values per IEEE C50.13 Table 1 (synchronous machine typical characteristics), cited in the example reasoning.

### Generator prompt step

```markdown
### Step N+2: Decrement curves for synchronous-machine-bonded nodes

For each cascade node downstream of a synchronous generator (when ATS is
in standby state, or always for permanent-bonded standby), OR a large
induction motor aggregate (>1000 kW total) in fault-feed mode:

1. Identify the synchronous machine. Read machine reactances (Xd", Xd',
   Xd) and time constants (Td", Td', Ta) from input.json if engineer
   declared them, OR fall back to IEEE C50.13 typical-machine table
   (cite the table reference).
2. Apply Park's full model (IEC 60909 §4.3):
   - Ik" at t=0+ — use this for switchgear rating + arc-flash incident
     energy
   - Ik' at ~Td' (~1 second typically) — use this for protection
     coordination (relay time-grading)
   - Ik at steady state (> 3 × Td') — use this for thermal sizing
3. Generate the 8-point time-series sample at t = 0, 10, 50, 100, 500,
   1000, 3000, 10000 ms.
4. Set decrement_model = "iec_60909_4_3_full_park". Set
   machine_data_source per where the data came from.
```

### Validator INV — `INV-NN+2: decrement-monotonicity-and-bounds`

**Rule:** For every cascade node carrying `decrement_curve`:
- `ik_initial_subtransient_ka >= ik_transient_ka >= ik_steady_state_ka` (monotonic decay)
- All `time_series_samples[*].ik_ka` between Ik_steady (lower bound) and Ik" (upper bound)
- `time_series_samples[*].t_ms` strictly increasing
- `ik_initial_subtransient_ka == ifault_ka_max` (or within 1% — the node's headline Ik = the subtransient initial)
- If `machine_data_source == "typical_ieee_c50_13"`: machine_reactances_pu values fall within published IEEE C50.13 typical ranges (Xd": 0.10–0.20; Xd': 0.15–0.30; Xd: 1.0–2.0)

**Severity:** HIGH.

### Example updates

`intl-commercial-with-genset`: TX-1 and MSB-1 (generator-fed path in standby state) gain `decrement_curve`. The 2 MVA standby gen has documented reactances → typical IEC C50.13 values: Xd" = 0.15, Xd' = 0.25, Xd = 1.8. Td" = 30 ms, Td' = 1.2 s, Ta = 100 ms. Cite IEEE C50.13 §3.2 + IEC 60909 §4.3.

Other examples (no generator or small generator < 100 kVA): decrement_curve omitted — schema-optional.

---

## §5 Item 4 — arc-flash equipment-condition with full calc adjustment

### Engineering intent

NFPA 70E §130.5(A) requires the arc-flash hazard analysis to consider equipment condition (normal vs abnormal — water damage, prior arc damage, corrosion, improperly maintained). The standard doesn't quantify a specific IE adder for abnormal condition — it says the analysis "warrants different posture." Industry references (ETAP application notes, EasyPower technical bulletins) use 1.2–1.5× IE multipliers as defensible defaults.

This item adds equipment-condition fields to the arc-flash IR and applies a **1.25× IE adder** when condition is abnormal, with **mandatory `is_provisional: true`** (using the Sprint C3 IR-level provenance pattern) and an **explicit cited source** for the adder. The honest engineering posture: "we adjust the IE upward by a defensible industry default; we don't claim NFPA 70E prescribes this exact value; we mark the output provisional pending site assessment."

### Schema additions

**At IR root:**

```json
"equipment_condition_basis": {
  "default_condition": "normal | abnormal",
  "default_worker_position": "standing | kneeling | reaching",
  "working_distance_basis": "standard_18in | custom_mm",
  "abnormal_ie_adjustment_factor_default": 1.25,
  "abnormal_ie_adjustment_source": "ETAP Arc Flash Analysis App Note 2020 + EasyPower technical bulletin TB-AF-2019 (industry consensus 1.2–1.5× range; NFPA 70E §130.5(A) does NOT prescribe — engineer must validate against site assessment)"
}
```

**Per cascade node:**

```json
"equipment_condition": {
  "condition": "normal | abnormal",
  "justification": "string (required when abnormal, 20–500 chars: e.g. 'water-damaged distribution panel; last inspection 2024-08-12 flagged corrosion on busbar mounts')",
  "last_maintenance_date": "ISO date | null (recommended when normal; required when abnormal)",
  "ie_adjustment_factor": "number (1.0 for normal; 1.25 default for abnormal per root.abnormal_ie_adjustment_factor_default; engineer can override)",
  "ie_adjustment_source": "string (cited reference for the factor — use root.abnormal_ie_adjustment_source when default)"
},
"worker_position": "standing | kneeling | reaching"
```

### Generator prompt step

```markdown
### Step N: Equipment-condition + worker-position assumptions per NFPA 70E §130.5(A)

For every cascade node, the engineer must declare equipment_condition.
Default to `normal` unless the input.json declares otherwise.

When equipment_condition.condition == "abnormal":

1. Require justification (≥ 20 chars) and last_maintenance_date in the
   node's equipment_condition block.
2. Apply ie_adjustment_factor (default 1.25; engineer can override in input).
   Modify the computed incident energy:
       IE_adjusted = IE_base × ie_adjustment_factor
   Use IE_adjusted for ppe_category selection and afb_mm.
3. Set provenance.is_provisional = true (via the Sprint C3 IR-level
   provenance block). The output IS provisional — abnormal condition
   warrants site assessment, not a desk-study verdict.
4. Cite ie_adjustment_source: use root.equipment_condition_basis.
   abnormal_ie_adjustment_source unless the engineer overrides.
5. If IE_adjusted > 40 cal/cm² → RESTRICTED branch (the Sprint A.3 +
   Sprint C.3 logic already handles this — ppe_category=null, live-work
   prohibited).

For normal-condition nodes: ie_adjustment_factor = 1.0; no provisional
flag forced from this rule (other rules may still set it).

worker_position affects working_distance only if working_distance_basis
== "standard_18in"; for custom_mm, the engineer-declared distance
overrides regardless of position.
```

### Validator INV — `INV-NN: abnormal-condition-defensive`

**Rule:** For every cascade node carrying `equipment_condition`:
- `condition ∈ {normal, abnormal}`
- If `condition == "abnormal"`:
  - `justification` is present and ≥ 20 chars
  - `last_maintenance_date` is present and is a valid ISO date
  - `ie_adjustment_factor >= 1.0` (no negative-adjustment via this field)
  - `ie_adjustment_source` is non-empty
  - The top-level `provenance.is_provisional == true`
- If `condition == "normal"`:
  - `ie_adjustment_factor == 1.0` (no abnormal-adder on a normal node)

**Severity:** HIGH.

### Example updates

`electrical/arc-flash/examples/uk-lv-switchgear` + `intl-mv-substation` + `us-pv-with-dcfc` + `intl-hv-restricted-substation`: all gain `equipment_condition: {condition: "normal", ...}` on every cascade node (default state). No IE change for any of them.

**New example:** `electrical/arc-flash/examples/uk-abnormal-condition-water-damaged/` demonstrates the abnormal-condition branch:
- Indoor LV switchboard at 400 V, water-damaged from a prior plumbing leak
- Base IE = 5.2 cal/cm² (PPE Cat 2 normal)
- ie_adjustment_factor = 1.25 → IE_adjusted = 6.5 cal/cm² (still PPE Cat 2 but flagged provisional)
- justification documents the leak + corrosion observation
- last_maintenance_date pre-leak
- provenance.is_provisional = true
- ie_adjustment_source cites ETAP / EasyPower industry default
- Reasoning narrates the §130.5(A) reasoning + recommends shutdown for repair before live-work

---

## §6 Testing + ship plan

### Per-task gates

Each item ships as its own commit. Before commit:

- `python3 scripts/validate-examples.py` — 219/219+ across 4 passes (held; new examples increase denominator)
- `python3 functional_audit.py` — ≤ 1 finding (motor-superposition disclaimed FP remains visible after Item 2 ships UNLESS the audit oracle is updated to read the new `superposition_contribution_ka` field; **oracle update is OUT OF SCOPE for D1** — Item 2 ships the data as explicit so a future oracle improvement CAN read it, but improving the oracle itself is a separate task post-D-program)
- Manual hand-check on at least 1 example per item:
  - Item 1: pick `intl-commercial-with-genset` MSB-1, verify `headroom_pct` matches the device/Ik arithmetic
  - Item 2: pick `us-industrial-with-motors` MCC-1, verify `sum(superposition_contribution_ka.{non-total}) == .total` and `.total == ifault_ka_max`
  - Item 3: pick `intl-commercial-with-genset` TX-1, verify `Ik" >= Ik' >= Ik_steady` and Park's-equation Ik(t) at t=100ms matches the stored sample within 1%
  - Item 4: pick the new `uk-abnormal-condition-water-damaged`, verify IE_adjusted = 1.25 × IE_base, `is_provisional == true`, and INV-NN fires PASS

### Commit sequence

1. `feat(fault-level): D1.1 breaking-capacity verdict (hybrid db-layout consumer)`
2. `feat(fault-level): D1.2 motor/UPS superposition explicit (hybrid representation)`
3. `feat(fault-level): D1.3 decrement curves (IEC 60909 §4.3 full Park's model)`
4. `feat(arc-flash): D1.4 equipment-condition + 1.25× abnormal IE adjustment`

### Sprint ship

- Write `sprint-D1-shipped.md` memory file at user's auto-memory directory
- Update `MEMORY.md` index
- Push all 4 commits to origin/main (no tag; defer to a single D-program tag after D3 ships)
- Update fault-level CHANGELOG [1.1.1 → 1.2.0] (minor: new features) + arc-flash CHANGELOG [1.0.2 → 1.1.0]

### Risks

| # | Risk | Mitigation |
|---|---|---|
| R1 | Decrement curve scope (Item 3 — full time-series per user pick) requires machine-reactance data not in current examples | Use IEEE C50.13 typical-machine table (cited in example reasoning) as defensible default when engineer doesn't declare specific values; `machine_data_source: typical_ieee_c50_13` flags this |
| R2 | 1.25× abnormal IE adder (Item 4) is not NFPA 70E prescription | Cited as industry default (ETAP / EasyPower); engineer-overrideable; `is_provisional=true` forces site-assessment before field use |
| R3 | Hybrid consumer pattern (Item 1) introduces a new edge in the cross-skill graph (fault-level → db-layout) | Verify db-layout intent shape carries device ratings (it does — `main_switch.rating_a` per H6 work). Fallback to engineer-declared in the same input.json slot when db-layout absent |
| R4 | Item 2's per-node contribution map may diverge from `sources[].contributes_to_nodes` (the hybrid representation) | Validator INV-NN+1 asserts cross-walk match within 1%; CI catches drift |
| R5 | New example for Item 4 (uk-abnormal-condition-water-damaged) needs honest engineering — IE base must reconcile from actual IEEE 1584-2018 (or Lee fallback if LV coefficients still pending per C3) | Use Lee fallback for the base IE; mark `is_provisional=true` already from the C3 IR-level provenance pattern; the 1.25× adder + abnormal-condition INV fire independently of the C3 transcription status |

---

## §7 Out of scope (explicit deferrals)

- **Lightning protection interface** — already its own skill (`electrical/lightning-protection` stub). Not part of D1.
- **Full UPS design** — `electrical/ups/` stub (future build). fault-level consumes a fragment of UPS data via `sources[].kind: "ups"` (engineer-declared in D1; consumed from ups intent when that skill ships).
- **Motor design / selection** — no stub yet (depth gap for the breadth-first roadmap). fault-level treats motor aggregate as engineer-declared input.
- **Protection coordination study** — `electrical/protection-coordination` stub (Sprint D follow-up). Item 1's breaking-capacity verdict is a NODE-level check; full TCC discrimination across the cascade is the coordination skill's job.
- **Energised-work permit document** — `documents/energised-work-permit` stub. Item 4 populates the IR fields the permit consumes; the permit deliverable itself is a separate skill.

---

## §8 Ship criteria

Sprint D1 considered shipped when:

- All 4 items committed in sequence
- `validate-examples.py` 219/219+ across 4 passes
- `functional_audit.py` ≤ 1 finding (Item 2 may reduce to 0)
- 1 new example shipped (uk-abnormal-condition-water-damaged for Item 4)
- 4 CHANGELOG entries (fault-level + arc-flash; minor version bumps)
- `sprint-D1-shipped.md` memory file written
- All commits pushed to origin/main

After D1 ships, D2 (Sizing & Boards — cable-sizing + db-layout) starts following the same brainstorming → writing-plans → subagent-driven-development workflow.
