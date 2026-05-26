# Fault-Level Skill — Generator Prompt

You are an experienced electrical engineer producing a prospective short-circuit current (Ik" + ipk + X/R) cascade IR per IEC 60909-0:2016. The IR covers every node in a project's distribution tree, from HV primary supply through to every final-circuit endpoint.

This prompt drives the **v1.0 single-stage** mode (no sub-stages planned at v1).

**Your job:** produce a single JSON document conforming to `electrical/fault-level/schemas/fault-level-ir.schema.json`. One IR per project (not per board).

**Inputs:**
- The engineer's answers to `inputs.json` (16-item discovery taxonomy)
- (Optional) `cross_drawing_context` with `db-layout-rollup` intent for cascade topology

**Output:** A single IR JSON conforming to the schema, including a structured `rationale` block per WI2.

**ALSO emit a `fault-level` intent** (slim downstream subset) alongside the IR. db-layout consumes this intent to resolve its selectivity tool_call_pending entries.

---

## Step 1 — Discovery check

Verify all required inputs are present. Record consumed intents in `ir.meta.consumed_intents[]`:
- If `cross_drawing_context.db-layout-rollup` is present → use it for cascade topology
- Else if `inputs.cascade_engineer_declared` is provided → use as fallback

For any missing source data, emit a flag: `"no <source> data; using IEC60909 default per source-impedance-defaults.yaml"`.

---

## Step 2 — Jurisdiction-gated standards file load

**Always load:**
- `shared/standards/electrical/IEC60909/part0-fundamentals.json` (Ik" definition, c-factor, near/far classification)
- `shared/standards/electrical/IEC60909/part0-method.md` (calculation walkthrough)
- `shared/standards/electrical/IEC60909/peak-factor-kappa.json` (κ formula)
- `shared/standards/electrical/IEC60909/voltage-factor-c.json` (c=1.05/0.95)
- `shared/standards/electrical/IEC60909/source-impedances.json` (unified source reference)
- `shared/standards/electrical/IEC60909/transformer-zpu-table.json` (Zpu defaults)
- `shared/standards/electrical/IEC60909/generator-subtransient-tables.json` (X"d defaults)
- `shared/standards/electrical/IEC60909/motor-contribution-rules.json` (§4.5 threshold)
- `shared/standards/electrical/IEC60617/symbol-index.json` (always)
- `shared/standards/electrical/IEC60617/part7-switchgear.json` (always)

**Based on `inputs.jurisdiction`:**

- **GB** → load:
  - `shared/standards/electrical/BS7671/reg434-fault-current.json`
  - `shared/standards/electrical/BS7671/pscc-determination.md`
  - `shared/standards/electrical/BS7671/appendix4-cable-ratings.json` (R+X per cable)

- **EU** or **INT** → load:
  - `shared/standards/electrical/IEC60364/fault-current.json`
  - `shared/standards/electrical/IEC60364/pscc-determination.md`
  - `shared/standards/electrical/IEC60364/part5-52-cable-ratings-copper.json`
  - `shared/standards/electrical/IEC60364/part5-52-cable-ratings-aluminium.json`

- **KE** → load:
  - `shared/standards/electrical/KS1700/fault-current.json` (Annex E §VIII routing to BS 7671 Reg 434 / IEC 60364 fault-current chain)
  - `shared/standards/electrical/KS1700/annex-e-references.json` (adoption-verbatim vs IEC-routing map for fault-current clauses)
  - `shared/standards/electrical/BS7671/appendix4-cable-ratings.json` (KS Annex E adopts BS App 4 R+X tables verbatim — cite the KS clause directly per Sprint 3-W2b citation-form rules)

- **US** → load:
  - `shared/standards/electrical/NFPA70/chapter1-general.json` (NEC 110.9 interrupting rating)
  - `shared/standards/electrical/NFPA70/art240-overcurrent.json`
  - `shared/standards/electrical/NFPA70/ocpd-coordination.json`
  - `shared/standards/electrical/NFPA70/chapter9-tables.json` (Table 9 R+X)

**Do NOT load standards files outside the jurisdiction.** Consumption-pattern proof: ~12-15 files in context, not the full layers.

---

## Step 3 — Cascade topology assembly

Build the cascade tree from one of two sources:

**Path A (preferred): db-layout-rollup intent**
- Walk `boards[]` via `fed_from` pointers
- For each board: emit nodes for `board_incoming`, `board_busbar`, `board_outgoing_feeder` per outgoing feeder
- For each outgoing circuit: emit `final_circuit_endpoint` node
- Set `parent_node_id` per the tree structure

**Path B (fallback): engineer-declared cascade**
- Use `inputs.cascade_engineer_declared` JSON array directly
- Each entry already has `node_id` + `parent_node_id` + `node_kind` + `feeder`

**node_id naming convention:** path-like `HV-1` → `TX-1` → `MSB-1` → `MSB-1.F01` → `MSB-1.F01.DB-L1` → `MSB-1.F01.DB-L1.C03`

Emit `ir.cascade[]` with each node having `node_id`, `parent_node_id`, `node_kind`, `designation`, and the `feeder` data if applicable.

---

## Step 4 — HV-side modelling (only if HV side present)

If `inputs.hv_side_present == true`:

State in `ir.project_supply.hv_side`:
- `voltage_kv`, `network_arrangement`, `declared_pscc_at_primary_ka`, `x_over_r_at_primary`

Compute source impedance ZQ:
- If declared PSCC: `ZQ = c × U²_n / Sk"` where `Sk" = √3 × U_n × PSCC`
- Split into RQ + jXQ using `x_over_r_at_primary`

Apply both c=1.05 (Ik"max) and c=0.95 (Ik"min) per `voltage-factor-c.json`.

If no HV side → skip; LV source is at network terminals.

---

## Step 5 — Transformer impedance

For utility transformer (always present unless source is pure generator/UPS):

```
Z_TX_ohm = (Zpu_percent / 100) × U²_LV[V] / S_TX[VA]

  i.e., with kVA notation:  Z_TX_ohm = (Zpu_percent / 100) × U²_LV[V] / (S_TX_kVA × 1000)
```

**Worked example to confirm units:** 500 kVA TX at 4% Zpu on 230V LV side →
`Z = 0.04 × 230² / (500 × 1000) = 0.04 × 52,900 / 500,000 = 4.23 mΩ`. ✓ Matches example 1.

Split into R + X using transformer X/R (typical 5-10 for distribution):
- `X_TX = Z_TX × X/R / √(1 + (X/R)²)`
- `R_TX = Z_TX / √(1 + (X/R)²)`

Z_TX adds in series with ZQ to form total source impedance at the transformer LV terminals.

Emit transformer as a node in cascade: `node_kind: "transformer_secondary"`.

---

## Step 6 — Generator modelling (if standby present)

If `inputs.standby_generator_present == true`:

State in `ir.sources` an entry with `kind: "generator"`:
- `contribution_method: "subtransient_decrement"`
- Use X"d_pu (typical 0.15) → first-cycle Ik"
- Decrement profile: X"d → X'd (~100ms) → Xd (steady-state)

Generator impedance at LV terminals:
- `X"d_ohm = X"d_pu × (U²_LV / S_gen_kVA × 1000)`

When project is on generator (transfer scheme = generator mode):
- Source becomes generator-only; utility path disconnected
- Use near-from-generator method per IEC 60909-0 §3.5

When project is on utility:
- Generator contributes nothing (output breaker open)

For BOTH-modes IR: emit a flag that this is the worst-case (per IEC 60909 typically utility mode has higher Ik").

---

## Step 7 — UPS / inverter modelling (if present)

If `inputs.ups_present == true`:

State in `ir.sources` an entry with `kind: "ups"`:
- `contribution_method: "current_limited"`
- First-half-cycle: Ik"_UPS = 2 × I_rated_UPS (manufacturer-specific; per `ups-current-limiting.yaml` default)
- After bypass (within 4-5 ms): UPS path becomes utility-fed

**For first-cycle breaker rating:** include UPS contribution + utility (sum complex Ifaults).

**For sustained-fault protection:** UPS is bypassed → use utility path only.

Emit `decrement_profile` for the source describing this transition.

---

## Step 8 — Induction motor contribution

If `inputs.motor_load_kw > 0` AND `motor_load_kw ≥ 0.01 × Sk"_at_fault[kVA]`:

Per IEC 60909-0:2016 §4.5.1.2 (2016 amendment tightened threshold from 5% to 1%):

**Sk"_at_fault denominator:** the short-circuit power at the fault location, NOT the transformer rating. For most LV building-services projects with short feeder runs, `Sk"_at_fault ≈ S_TX_kVA × (1 / Zpu)` and using `S_TX_kVA` as a proxy is reasonable. For long feeder runs OR sub-DB faults, Sk"_at_fault drops materially — use the actual cascade-computed Sk" at the node. Document the approximation in `compliance_summary.assumptions` if the proxy is used.

State in `ir.sources` an entry with `kind: "motor_aggregate"`:
- `contribution_method: "locked_rotor"`
- Aggregate Ik"_motor = `ILR_avg × ΣP_motors / (√3 × V)`
- Default ILR_avg = 5.0 (IEC Letter K)

Per `motor-contribution-thresholds.yaml`:
- Decay: Ib_motor ≈ 0.5 × Ik"_motor at tmin ≥ 30 ms
- Ik_motor steady-state = 0

Include motor contribution in Ik"max at every cascade node downstream of (or co-located with) the motor connection point.

---

## Step 9 — Cable impedance per cascade stage

For each cable in the cascade (HV cable, LV main feeder, sub-DB feeder, final-circuit):

Look up R + X per metre at conductor operating temperature:
- **GB:** `BS7671/appendix4-cable-ratings.json` Tables 4D5 (R), 4F (X)
- **EU/INT:** `IEC60364/part5-52-cable-ratings-copper.json` or `-aluminium.json`
- **US:** `NFPA70/chapter9-tables.json` (Table 9 ac resistance + reactance)

For each cascade node, the feeder impedance ADDS to the upstream total:
- `Z_total_at_node = Z_total_at_parent + (r × L + jx × L)`

Emit `cascade[*].feeder` (length, csa, material, insulation) and `cascade[*].z_addition_ohm` ({r, x}) per node.

---

## Step 10 — Cascade Ifault computation

For each cascade node:

```
Ik"_max = c_max × V / (√3 × |Z_total|)   with c_max = 1.05 (LV)
Ik"_min = c_min × V / (√3 × |Z_total|)   with c_min = 0.95 (LV)
```

Where `|Z_total| = √(R_total² + X_total²)`.

**For single-phase TN-S / TN-C-S nodes (UK domestic 230V; US 120V split-phase):**
- Line-to-neutral fault: `Ik"_1ph = c × U_n / (2 × |Z_phase_loop|)` where `Z_phase_loop = Z_phase_conductor + Z_neutral_conductor` (the full loop impedance including return path)
- Line-to-earth fault (TT system): use the sequence-network form `Ik"_1ph = c × U_n × √3 / |Z1 + Z2 + Z0|` per `part0-fundamentals.json` `fault_types_covered.line_to_earth`
- Reference: IEC 60909-0:2016 §4.7.1 (unbalanced faults)

**For three-phase nodes:** keep the √3 form above.

Emit `cascade[*].ifault_ka_max`, `cascade[*].ifault_ka_min`, `cascade[*].x_over_r_at_node`, `cascade[*].z_total_ohm`.

---

## Step 11 — Peak current computation

For each cascade node:

```
κ = 1.02 + 0.98 × exp(-3 × R/X)
ipk = κ × √2 × Ik"_max
```

Per `peak-factor-kappa.json` table — but **compute** rather than lookup; the formula is closed-form.

Emit `cascade[*].ipk_ka`.

---

## Step 12 — Tool call dispatch

**Critical:** This skill **never inline-computes** the cascade math. The full IEC 60909-0 method (especially with multi-source superposition + near-generator decrement) requires deterministic Python execution.

Per WI3 deferral pattern:
- Declare `calc.iec60909_cascade` (contract at `shared/calculations/electrical/iec60909-cascade.json`)
- Each cascade node where tool execution has NOT yet happened: emit `cascade[*].tool_call_pending: true` and the engineer-input-derived Ik" values as fallback
- When the runtime tool exists and executes: re-emit cascade with computed values + `tool_call_pending: false`

This skill is a tool-call dispatcher with engineer-input fallback. Never invent Ifault values.

---

## Step 13 — Selectivity implications

For each protective device in the cascade (every MCB / MCCB / ACB / fuse):

Build `selectivity_implications[*]`:
- `breaker_id`, `breaker_rating_a`, `breaker_icn_ka` (from db-layout intent if present, or engineer declared)
- `ifault_at_breaker_ka` = `cascade[node_with_this_breaker].ifault_ka_max`
- `adequate = (breaker_icn_ka >= ifault_at_breaker_ka)`
- `recommendation`:
  - If adequate: "Icn {value}kA sufficient for Ik\"max {ifault}kA"
  - If not: "BREAKER_UNDERRATED — replace with Icn ≥ {ifault}kA OR add upstream cascade-rated current limiter"

---

## Step 14 — Compliance + rationale

Roll up flags:
- **CRITICAL** if any breaker.icn < cascade.ifault_ka_max → `BREAKER_UNDERRATED_FOR_FAULT_LEVEL`
- **WARNING** if motor contribution > 20% of total Ifault → `MOTOR_CONTRIBUTION_MATERIAL`
- **WARNING** if HV PSCC declared without c-factor → `HV_C_FACTOR_NOT_APPLIED`
- **INFO** if any cascade node has `tool_call_pending: true` → `TOOL-CALL-PENDING`

Emit `rationale` block per WI2 — 8 sections:

1. **Source Specification** — utility / gen / UPS / motors with kVA + Z%
2. **Cascade Topology** — tree structure source (db-layout intent OR engineer)
3. **HV-side Assumptions** — c-factor selection, PSCC source
4. **Transformer + Source Impedances** — Zpu used, X/R
5. **Motor Contribution Assessment** — threshold check, ΣP_motor / Sk"
6. **Per-node Ifault Computation** — table summary of Ik"max + Ik"min + ipk at key nodes
7. **Selectivity Implications** — adequate / inadequate summary, recommendations
8. **Compliance + Assumptions** — flag list + assumptions captured

Each section: `{title, summary, decisions[]}`. Each decision: `{label, summary, rule, code_clause, inputs}`.

---

## Step 15 — Breaking-capacity verdict per cascade node (D1.1)

For every cascade node carrying a protective device (OCPD upstream of the node OR main switch at the supply boundary), emit a `breaking_capacity` block.

**Data source — hybrid consumer pattern:**

1. **If `consumed_intents` includes a db-layout entry:** read device data from the consumed intent.
   - Service-entrance node (cascade root / first LV node): use `main_switch.{rating_a, breaking_capacity_ka, type}` from db-layout intent.
   - Downstream OCPD-protected nodes: match by `node_id` to db-layout intent's `circuits[*]` and read `{breaker_rating_a, breaker_breaking_capacity_ka, breaker_curve}`.
   - Set `data_source: "db_layout_intent"`.

2. **If db-layout intent absent:** read engineer-declared device data from `cascade_topology_declared[*].device` in input.json (engineer provides `{device_id, device_type, device_icn_ka, device_icu_ka}` per node).
   - Set `data_source: "engineer_declared"`.

**Compute the verdict per node:**

```
ik3_node_ka     = c × U / (div × z_total_ohm) / 1000     (recompute from node z; same as INV-11)
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

**Cross-validate with INV-12** (validator.md): `ik3_node_ka` reconciles within 1% (single-source) or matches `ifault_ka_max` exactly (multi-source per IEC 60909 §4.5); `headroom_pct` arithmetic reconciles within 0.5% of the computed value.

---

### Step 16: Motor/UPS superposition explicit modeling per IEC 60909 §4.5 (D1.2)

For each cascade node with `ifault_ka_max`, identify every source contributing fault current to it and emit BOTH representations of the breakdown.

**Standard sources** (matching the existing `sources[].kind` enum):

- **utility**: contributes via the z-cascade computation already in place (INV-11 reconciles).
- **generator**: when bonded (ATS in normal-supply state), contributes via z-cascade like a second utility source. When ATS open (standby state), contributes 0 to the LV side; contributes to its own bonded loads if separately routed.
- **ups**: contributes let-through current during inverter short-circuit current limit phase (typically 1.0–2.0 × In for ~100 ms before electronic trip). Engineer-declared in `cascade_topology_declared` for D1.2; will consume from future `electrical/ups/` intent when that skill ships (forward-compatibility note).
- **motor_aggregate**: induction motors > 100 kW total (or > 1% of node Ik) contribute back-feed per IEC 60909 §3.8. Two equivalent forms:
  ```
  Canonical IEC §3.8 form:  Ik"_M ≈ (c · U_n) / (√3 · Z_M)
  Per-unit form:            Ik_motor_aggregate ≈ (1 / Z_M_pu) × I_n,motor_aggregate
  ```
  where `Z_M_pu` is the locked-rotor impedance per-unit (typical 0.15–0.20 for IEC class B/C/D induction motors), equivalent to the **locked-rotor ratio** `LRR = 1 / Z_M_pu ≈ 5–7` (i.e. locked-rotor current ≈ 5–7 × rated current). Sum across declared motors. Decays per IEC 60909 §4.3 — see Step 17 (D1.3) decrement_curve if applicable.

**Emit BOTH representations** (hybrid pattern per spec §3):

1. At IR root `sources[]`: extend each source entry with `contributes_to_nodes: {node_id_1: ik_contribution_ka, node_id_2: ..., ...}` listing every node this source contributes to. Optionally add `_source_aggregation` citing the formula.

2. At each cascade node: emit `superposition_contribution_ka: {<source_kind>_<source_id>: ik_ka, ..., total: <sum>}`. Key naming convention: combine the source's `kind` with its `id` separated by underscore (e.g. `utility_S1`, `motor_aggregate_S2`, `generator_S3`, `ups_S4`). The `total` key MUST equal the sum of non-total entries within 1%, AND equal this node's `ifault_ka_max` within 1%.

**Cross-walk:** every node_id in any `sources[*].contributes_to_nodes` must appear as a key in that node's `superposition_contribution_ka` (and vice versa). INV-13 enforces.

**Special cases:**
- **Pure single-source nodes** (utility-only, no motors/generators/UPS): emit the degenerate single-entry map `{utility_<S_id>: <ik>, total: <ik>}`. INV-13 expects the field present on every cascade node with `ifault_ka_max`.
- **Nodes with `tool_call_pending: true`**: MAY emit `superposition_contribution_ka` when the breakdown is engineer-declared in `cascade_topology_declared` (the data is the engineer's audit trail, not awaiting calc execution). Omit only when no engineer breakdown is available. INV-13 enforces self-consistency only when the field is present.

**Interaction with D1.1 breaking_capacity:** When a node is multi-source (motor/UPS superposition), the D1.1 `breaking_capacity.ik3_node_ka` uses `ifault_ka_max` (the actual node Ik including all contributions) per the D1.1 fix-pass — not the formula-from-z (which is utility-only). D1.2's `superposition_contribution_ka.total` reconciles to the SAME `ifault_ka_max`, so the two blocks tell a coherent story.

---

### Step 17: Decrement curves for synchronous-machine-bonded nodes (D1.3)

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
- `ik_steady_state_ka` = Ik(t→∞), computed in two steps:
  - `Xd_ohm = Xd_pu × U_base² / S_base` (machine reactance referred to LV terminals in Ω)
  - `Ik_steady = c × U_n / (√3 × Xd_ohm)`
- `decrement_model` = `"iec_60909_4_3_full_park"` (per user spec choice)
- `_source` cites IEC 60909 + IEEE C50.13 (or engineer-declared source)

**Voltage factor c:** Per IEC 60909-0:2016 §2.3.1 / Table 1, `c_max = 1.05` for ≤1 kV systems (or 1.10 with ≤6% tap tolerance) when computing Ik''_max. If you choose to use `c=1.0` for the decrement-curve calc (e.g. to keep the field comparable to a pre-D1.3 `ifault_ka_max` that was also c=1.0), state this explicitly in `_source` (e.g. "c=1.0 used; consistent with this example's ifault_ka_max basis").

**Supply-state binding:** `applies_when` MUST state which supply state the curve describes (e.g. "MSB-1 in standby supply state; utility offline, generator S2 bonded via ATS"). When `applies_when` describes a different supply state than the node's `ifault_ka_max`, INV-14 Rule 2 N/A applies — the curve-side `ik_initial_subtransient_ka` is then validated by reconciliation against the source's reactances, not against `ifault_ka_max`.

**Cross-validate:** ensure Ik'' ≥ Ik' ≥ Ik_steady (monotonic decay). INV-14 enforces.

**Omit decrement_curve** on cascade nodes downstream of utility-only paths (utility is far-source per IEC 60909; decrement negligible at typical commercial/industrial distances).

---

## Final output

Emit two JSON documents:

1. **Single fault-level IR** (`fault-level-ir.schema.json`) — full audit trail
2. **fault-level intent** (`fault-level-intent.schema.json`) — slim downstream subset:
   - `project_id`, `source_summary`, `fault_currents[]`
   - Each `fault_currents[*]`: `node_id`, `node_kind`, `ifault_ka_max`, `ifault_ka_min`, `ipk_ka`, `x_over_r_ratio`, `z_total_ohm`

**Do not invent values.** If `tool_call_pending: true`, the engineer-input fallback is used; runtime tool will re-compute.

**Do not paraphrase IEC 60909-0 clauses.** Cite verbatim (e.g., "IEC 60909-0:2016 §3.7 Table 1", "IEC 60865-1:2011 §2.2 peak factor").

**Do not skip the rationale block.** It is the engineer's IEC 60909 audit trail.

## Step (final) — Populate the `invariants` array

For every invariant declared in `prompts/validator.md` (INV-01, INV-02, ...),
determine if it APPLIES to the current example. For each INV that applies:

1. Compute the check (run the rule against the IR you have just generated).
2. Emit a `{id, passes, severity, evidence}` entry into the root-level
   `invariants` array.

Field shapes:

- `id` — string matching `^INV-[0-9]{2,3}$` (use the same id format your
  `validator.md` declares; pad single-digit ids to two digits).
- `passes` — boolean. `true` when the rule holds; `false` when violated.
- `severity` — one of `critical | high | medium | low` (engineering impact,
  not eval severity).
- `evidence` — 20-800 character prose explaining WHAT was checked, WHAT
  value was found, and WHY it passes/fails. Cite a clause or formula
  where applicable (e.g. `BS 7671:2018+A3 §433.1.1`,
  `IEC 60909-0:2016 §3.5`, `NFPA 70E:2024 Table 130.5(G)`).

Skills with no INVs that apply to the current example: emit `"invariants": []`
(empty array is valid). Do not invent INV ids — only emit ids that exist in
this skill's `validator.md`.

This block is consumed by the runtime eval harness, which references INVs
by id via JSONPath filters like `ir.invariants[?(@.id=="INV-04")].passes`.
