---
name: small-power
role: validator
version: 1.0.0
---

# Small Power — Validator Prompt (v1.0.0)

You are validating a small-power IR document produced by the `electrical/small-power` skill generator.

## Inputs

- An IR JSON document at the user-provided path.
- The canonical schema at `electrical/small-power/schemas/small-power-ir.schema.json`.
- The intent schema at `electrical/small-power/schemas/small-power-intent.schema.json`.
- The repo root (so any future cross-skill `consumed_intent_path` values can be resolved).

## Validation procedure

### 1. Schema validation

Run JSON-schema validation against `small-power-ir.schema.json`.

- If invalid: STOP. Emit `{"valid": false, "stage": "schema", "errors": [...]}`.

### 2. Cross-field invariants

Run all 12 INV checks below (INV-01 → INV-12). For each, emit a violation if the rule fails. Severities are either **Hard fail** (blocks `valid: true`) or **Warning** (does not block but appears in `warnings[]`). INV-11 is conditional on cable-sizing intent consumption (v1.1 hybrid mode) — it is a no-op when no cable-sizing intent is consumed. INV-12 is conditional on Part-7 room_type presence — it is N/A when no room uses a Part-7 room_type.

---

## INV-01: Schema shape conformance

**Rule:** The IR document conforms exactly to `small-power-ir.schema.json` (Draft-07). All required top-level fields are present (`drawing_type`, `version`, `meta`, `jurisdiction`, `supply_origin`, `parent_db`, `circuits`, `rooms`, `drawing_layout`, `compliance_summary`, `rationale`). All enum values are members of their declared enum sets. `additionalProperties: false` is enforced at every object level — no rogue fields permitted. The `drawing_type` constant value must be exactly `"small_power_layout"`.

**Severity:** Hard fail.

**Fail message:**

```
INV-01: schema validation failed at <JSON_POINTER>. <DETAIL>. Required fields missing or rogue fields present — every object level enforces additionalProperties: false.
```

---

## INV-02: Cross-reference integrity (socket → circuit)

**Rule:** Every `rooms[].sockets[].circuit_id` value MUST resolve to a `circuit_id` declared in `circuits[]`. No socket may reference a circuit that does not exist in this IR. This catches the most common generator drift: adding a socket to a room but forgetting to declare the circuit, or renaming a circuit without updating the per-socket references.

**Severity:** Hard fail.

**Fail message:**

```
INV-02: socket <SOCKET_ID> in room <ROOM_ID> references circuit_id=<C_ID> which does not exist in circuits[]. Every socket must reference a declared circuit.
```

---

## INV-03: Cross-reference integrity (circuit → rooms)

**Rule:** Every entry in `circuits[].rooms_covered[]` MUST resolve to a `room_id` declared in `rooms[]`. No circuit may claim to cover a room that is not present in this IR. This catches the inverse drift to INV-02: declaring a circuit covers a room that was removed from the IR.

**Severity:** Hard fail.

**Fail message:**

```
INV-03: circuit <CIRCUIT_ID> declares rooms_covered=<ROOM_ID> but no room with that room_id exists in rooms[]. Every rooms_covered[] entry must reference a declared room.
```

---

## INV-04: Topology by jurisdiction

**Rule:** `topology == "ring"` is only allowed for `jurisdiction in {"GB", "KE"}`. Ring final circuits are a UK convention (BS 7671:2018+A2:2022 §433.1.5 + IET On-Site Guide §8.4.4) inherited by Kenya via the KS 1700:2018 §313 routing chain. Other jurisdictions (INT, EU, US) use radial-only topology because their standards (IEC 60364, NEC 2023) do not codify the ring-final-circuit construct. The validator does not accept an engineer override on this rule — if a ring is genuinely required outside GB/KE, the engineer must change the `jurisdiction` input.

**Severity:** Hard fail.

**Fail message:**

```
INV-04: circuit <CIRCUIT_ID> has topology=ring but jurisdiction is <JURISDICTION>. Ring final circuits are only valid for GB + KE (KE via KS 1700 §313 routing to BS 7671). Change topology to radial or dedicated_radial.
```

---

## INV-05: Special-location enforcement

**Rule:** Special-location rooms must obey their jurisdictional Part 7 rules. Five sub-rules (four enforced; wet_area is engineer-judgement):

1. **`bathroom_zone_1`** — `sockets[]` MUST be empty. Even shaver supplies (BS EN 61558-2-5) are forbidden in zone 1 per BS 7671 Part 7-701 §701.512 and IEC 60364-7-701 §701.512.
2. **`bathroom_zone_2`** — every socket MUST be of a `type` matching the shaver-supply convention (e.g. `bs_en_61558_2_5_shaver` or per the ontology). No general-purpose BS 1363 / Schuko / NEMA sockets permitted in zone 2.
3. **`bathroom_zone_3`** — every socket MUST be fed by a circuit whose `rcd_posture` is either `type_a_30ma_per_§411_3_3` or `type_b_30ma_per_§531_3_3`. The `no_rcd_with_documented_§411_exception` value is NOT permitted in a bathroom — RCD protection is mandatory regardless of any §411 exception elsewhere on the system.
4. **`outdoor`** — every socket MUST carry an explicit `ip_rating` field of `IP55` or higher (numerical comparison on both digits). BS 7671 §522.6.201 + IEC 60364-5-51 §512.2.1 set the minimum for an exposed outdoor socket.
5. **`wet_area`** — No hard rule. Engineer applies judgement (BS 7671 §522.3 for wet commercial environments). INV-05 does not block `valid: true` for `wet_area` rooms.

**Severity:** Hard fail.

**Fail message:**

```
INV-05: special-location violation in room <ROOM_ID> (special_location=<LOC>): <SUB_RULE_DETAIL>.
Examples:
  - bathroom_zone_1 contains socket <SOCKET_ID> (must be empty)
  - bathroom_zone_2 contains non-shaver socket type=<TYPE>
  - bathroom_zone_3 socket <SOCKET_ID> fed by circuit <C_ID> with rcd_posture=no_rcd_with_documented_§411_exception (forbidden in zone 3)
  - outdoor socket <SOCKET_ID> missing ip_rating field OR ip_rating=<IP> below IP55 minimum
```

---

## INV-06: RCD posture validity

**Rule:** Three sub-rules govern `rcd_posture` per circuit:

1. **Default** — `type_a_30ma_per_§411_3_3` is the expected default for every socket circuit ≤32 A. No further justification required.
2. **Type B** — `type_b_30ma_per_§531_3_3` requires explicit justification: either the circuit's `designation` field references an IT-load / DC-leakage context (e.g. "Server room", "EVSE", "VFD-fed") OR the `compliance_summary.assumptions[]` array contains a Type B justification entry. Unjustified Type B emits a **warning** (not hard fail) — engineer may override but should document.
3. **No-RCD exception** — `no_rcd_with_documented_§411_exception` MUST be accompanied by a non-empty `rcd_exception_citation` field with an explicit BS 7671 §411 / IEC 60364-4-41 §411 reference. Missing citation is a hard fail.

**Severity:** Hard fail for sub-rule 3 (missing citation). Warning for sub-rule 2 (unjustified Type B).

**Fail / warning messages:**

```
INV-06 (hard fail): circuit <C_ID> rcd_posture=no_rcd_with_documented_§411_exception but rcd_exception_citation is empty or missing. Populate with an explicit BS 7671 §411 / IEC §411 reference.

INV-06 (warning): circuit <C_ID> rcd_posture=type_b_30ma_per_§531_3_3 but designation=<DESIG> contains no IT-load justification and no Type B entry in compliance_summary.assumptions[]. Document the DC-leakage / IT-load context.
```

---

## INV-07: Diversified load below OCPD rating

**Rule:** For every circuit, `diversified_max_load_a < ocpd.rating_a`. This is the engineer-estimate sanity check while `calc.diversity_factor` is deferred. A circuit whose diversified load equals or exceeds its breaker rating will nuisance-trip under design conditions, so the validator hard-fails any circuit where the inequality is not strict. When the diversity calc tool ships in v1.1+, this check stays in place — it is a logical invariant, not a deferred-tool flag.

**Severity:** Hard fail.

**Fail message:**

```
INV-07: circuit <C_ID> has diversified_max_load_a=<D>A which is >= ocpd.rating_a=<R>A. Circuit will nuisance-trip under design conditions. Re-split the load or upgrade the OCPD rating.
```

---

## INV-08: Zs deferral consistency

**Rule:** While `calc.zs_loop_impedance` is deferred in v1.0, every circuit must declare its Zs verification pending state consistently. The pair `(circuits[].tool_call_pending_for_zs_verification, ir.flags[] contains "TOOL-CALL-PENDING:calc.zs_loop_impedance")` MUST be coherent across the whole IR:

| Per-circuit bool | `flags[]` contains TOOL-CALL-PENDING string | Verdict |
|---|---|---|
| All circuits `true` | yes | PASS |
| All circuits `true` | no | FAIL (flag missing) |
| All circuits `false` | yes | FAIL (flag stale) |
| All circuits `false` | no | PASS (calc tool has shipped — v1.1+) |
| Mixed across circuits | any | FAIL (inconsistent) |

The bool and the flag move together. The TOOL-CALL-PENDING string MUST match the prefix `TOOL-CALL-PENDING:calc.zs_loop_impedance` (suffix may carry a disclaimer).

**Severity:** Hard fail.

**Fail message:**

```
INV-08: Zs deferral shape inconsistent. <COUNT_TRUE> circuits have tool_call_pending_for_zs_verification=true; <COUNT_FALSE> have it false; flags[] contains TOOL-CALL-PENDING:calc.zs_loop_impedance = <PRESENT|ABSENT>. All circuits' bools and the IR-level flag must move together.
```

---

## INV-09: chat_summary length

**Rule:** `rationale.chat_summary` length MUST be ≤ 500 characters. The chat summary is the engineer's first-glance read of the design — runtime UIs render it inline before the audit panel opens. Anything longer crowds the UI and reduces signal density.

**Severity:** Hard fail.

**Fail message:**

```
INV-09: rationale.chat_summary length is <N> characters; the limit is 500. Trim the summary to the four ordered beats: what you designed → key decisions → flags → invitation to refine.
```

---

## INV-10: Drafting standards consumed per jurisdiction

**Rule:** `drawing_layout.drawing_standard`, `drawing_layout.sheet_size`, and `drawing_layout.drawing_scale` must be present (schema enforces presence) AND should match the jurisdiction defaults declared in `electrical/small-power/inputs.json`:

| Jurisdiction | `drawing_standard` | `sheet_size` | `drawing_scale` |
|---|---|---|---|
| GB | `BS 1192:2007+A2:2016` | `A1` | `1:50` |
| KE | `BS 1192:2007+A2:2016` (via KS routing) | `A1` | `1:50` |
| INT / EU | `ISO 19650:2018` | `A1` | `1:100` |
| US | `AIA CAD Layer Guidelines 2007` | `Arch_D` | `1/4"=1'` |

Mismatches do not block validity — engineer override is valid for justified reasons (e.g. small-domestic plan fits on A3, or a large-residential plan needs Arch_E). A warning is emitted so the engineer is reminded to document the override in `compliance_summary.assumptions[]`.

**Severity:** Warning (not hard fail).

**Warning message:**

```
INV-10: jurisdiction=<J> drawing-layout mismatch — expected drawing_standard=<DS_EXPECT>, sheet_size=<SS_EXPECT>, drawing_scale=<SC_EXPECT>; got drawing_standard=<DS_ACTUAL>, sheet_size=<SS_ACTUAL>, drawing_scale=<SC_ACTUAL>. Engineer override valid if documented in compliance_summary.assumptions[].
```

---

## INV-11: Cable-Sizing Intent Lookup Integrity (v1.1)

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

---

## INV-12 — Special-locations zoning cascade resolved (HIGH)

**Severity:** HIGH when any `rooms[].room_type IN Part-7 set`; N/A otherwise.

**Rule (4 sub-checks):**
1. `consumed_intents.special_locations_zoning` is present (cascade triggered + resolved).
2. `consumed_intents.special_locations_zoning.payload.compliant == true` (special-locations' own INVs all PASS upstream).
3. Thin sanity cross-check: walk `sockets[] + isolators[] + connection_points[]` across all rooms; for each, find the containing zone in `payload.zones[]` by point-in-polygon + height check. Specifically catches:
   - 230V socket inside `bath_zone_1` or `bath_zone_2` (≥3 m boundary rule per BS 7671:2018+A2:2022 §701.512.3)
   - Shaver socket missing BS EN 61558-2-5 compliance flag
   - Pump/heater isolator outside local-isolation reach (BS 7671:2018+A2:2022 §701 + §710 medical equipment isolation)
   - 230V socket in `elv_barrier_zone` (voltage above max per BS 7671:2018+A2:2022 §715)
4. Flag cascading: every `payload.non_compliance_flags[]` entry MUST appear in `compliance_summary.non_compliance_flags[]` with `_cascaded_from: "special-locations"` attribution. No silent suppression.

When no `rooms[].room_type` is in the Part-7 set: trivially PASS (cascade not triggered).

**Validator action:**
- Read `consumed_intents.special_locations_zoning.payload`. If absent and any room is Part-7-affected: INV-12 FAIL HIGH.
- Verify `compliant == true`. If false: INV-12 FAIL HIGH; include cascade flags + add INV-12's own evidence.
- For each socket/isolator/connection_point across all rooms: find containing zone; evaluate 4 sub-rules. Any violation: INV-12 FAIL HIGH.
- Walk `payload.non_compliance_flags[]`. For each: verify same flag exists in `compliance_summary.non_compliance_flags[]` with `_cascaded_from: "special-locations"`. If any flag missing: INV-12 FAIL HIGH.

**Citation:** Cluster roadmap §6.7 cascade contract + special-locations INV-08 upstream + spec `2026-06-01-special-locations-design.md` §10.2.

**Rationale:** Cable-sizing and building diversity (the D4 depth content scheduled for Wave 2) tell us *how* sockets are loaded. Special-locations tells us *where* sockets are LEGAL. INV-12 binds small-power to the spatial-compliance layer; without it, a 230V socket could ship inside Zone 1 with no engineer review catching it. This wires the cascade for v1.2 ship; the D4 depth engineering content lands in a separate Wave 2 sprint.

**Fail message:**

```
INV-12: special-locations cascade check failed.
Sub-check <N>: <DETAIL>.
Room(s) affected: <ROOM_IDs>. Socket/isolator: <ID>. Zone: <ZONE_NAME>.
Fix: populate consumed_intents.special_locations_zoning from the upstream special-locations intent-out.json and ensure all non_compliance_flags are cascaded with _cascaded_from attribution.
```

## INV-13 — building_diversity self-consistency (HIGH)

**Severity:** HIGH when `building_diversity` is present; N/A and trivially
PASS when absent (input not supplied).

**Rule (3 sub-checks):**
1. `building_type` is in the v2.0 enum {office, industrial, healthcare}.
   Anything else fails — retail/residential/data-center/hospitality are
   deferred to v2.1 per spec §2 deferrals.
2. `design_density_w_per_m2` is within the verified standards-file range
   for the building_type, OR an explicit reviewer D-8 flag is emitted in
   `compliance_summary._engineering_judgments[]` documenting the engineer
   override (don't FAIL INV-13 on override alone — the override is a
   legitimate engineering call backed by project-specific data; just
   enforce the disclosure).
3. `building_diversified_demand_a` is computationally consistent:
   `building_diversified_demand_a ≈ Σ(per_circuit_demand_inputs[i].post_per_load_diversity_a × per_circuit_demand_inputs[i].building_factor_applied)`
   within ±5% tolerance (rounding).

**Validator action:** read `building_diversity` block. For each sub-check,
emit PASS or FAIL with concrete numbers + standards-file ranges in evidence.

**Citation:** IET On-Site Guide 8th Edition Appendix A — Table A1 +
diversity-factors.json (verified). Rules BLD-01..BLD-05 + DIV-07 lift
table. NEVER cite the original within-skill-depth-plan floor_factor
numbers (office 0.75 / retail 0.85 / industrial 0.90) — those are NOT in
the verified file and are the spec §2 citation-hygiene catch at brainstorm.

**Rationale:** Without INV-13, the engineer could declare a building type
without using its verified diversity profile, OR could compute the
building_diversified_demand without going through the per-circuit traceability.
The cascade integration (INV-19) is impossible without per_circuit_demand_inputs[].

## INV-14 — Ring final circuit continuity (HIGH)

**Severity:** HIGH on circuits where `topology == "ring"` and
`ring_endpoints` is populated; N/A and trivially PASS when topology is not
ring OR ring_continuity_endpoints input was not supplied.

**Rule (2 sub-checks per rule TOP-09):**
1. Both endpoints of the ring (endpoint_a_xy and endpoint_b_xy) MUST
   land at the same MCB way (mcb_way_id). A ring that lands at two
   different ways is structurally broken — it's two radials sharing
   conductors, and the Zs / cable thermal protection assumptions for ring
   topology no longer apply.
2. `continuity_verified: true` MUST be set; the engineer-of-record bears
   responsibility for the verification (typically end-to-end resistance
   ≤ Zs limit per Reg 411 + visual inspection per Part 6).

**Validator action:** read `circuits[i].ring_endpoints` for every ring
circuit. Verify mcb_way_id consistency + continuity_verified=true.
Emit evidence citing the circuit_id + both mcb_way_ids (when divergent) +
the topology.

**Citation:** `IET On-Site Guide §8.4.4 (8th Edition) + BS 7671:2018+A2:2022
§526 (top-level — sub-clause §526.2 not transcribed in verified file)`.
Rule TOP-09.

**Rationale:** A broken ring continues to function until a fault occurs;
the rule catches this at design stage before commissioning.

## INV-15 — Per-circuit floor-area cross-check (HIGH)

**Severity:** HIGH on any circuit where `floor_area_m2` and `rooms_covered[]`
are both populated; N/A otherwise.

**Rule (per rule TOP-10):** `circuit.floor_area_m2` MUST equal
`Σ(rooms_covered[].floor_area_m2)` within ±5% tolerance. Drift between
the declared circuit area and the sum of room areas the circuit covers
indicates one of:
  - engineer declared an area without listing all rooms,
  - rooms_covered list is stale (room added/removed in iteration),
  - typo in either field.

**Validator action:** for each circuit, compute the Σ and compare. Emit
evidence with concrete m² values + the % drift.

**Citation:** IET On-Site Guide §8.4.4 (8th Edition). Rule TOP-10.

**Rationale:** INV-01 ring max 100 m² (existing) relies on
`circuit.floor_area_m2` being honest. INV-15 keeps the field honest.

## INV-16 — OCPD-topology coordination (HIGH)

**Severity:** HIGH on every circuit.

**Rule (per rule TOP-11):** the chosen MCB rating MUST be coordinated with
the topology and conductor csa:
- `topology=ring` → MCB ≤ 32 A
- `topology=radial AND cable_csa_mm2=2.5` → MCB ≤ 20 A
- `topology=radial AND cable_csa_mm2=4` → MCB ≤ 32 A
- `topology=dedicated_radial` → MCB sized by connected load per §433.1.1
  (cable-sizing's domain; INV-16 trivially PASSES on dedicated_radial
  because cable-sizing's INV-04 already coordinates the OCPD-cable pair)

A 32 A MCB on a 2.5 mm² radial would breach Iz before tripping under
sustained 20-32 A; the cable overheats.

**Validator action:** for each circuit, read topology + mcb_rating_a +
cable_csa_mm2; apply the rule. Emit evidence with the chosen rating + the
permitted ceiling per topology.

**Citation:** `BS 7671:2018+A2:2022 §433.1.1 (verified) + IET On-Site Guide
§8.4.4 (8th Edition)`. Rule TOP-11.

**Rationale:** the most common ring/radial misdesign is over-rating the MCB;
INV-16 catches it.

## INV-17 — AMD 2 FCU spur modelling (MEDIUM)

**Severity:** MEDIUM on circuits where `fcu_spurs[]` is populated; N/A
otherwise.

**Rule (per rule TOP-12):** every entry in `circuits[i].fcu_spurs[]` MUST
satisfy:
- `fcu_rating_a` ∈ {3, 5, 13} (the standard FCU plug sizes)
- `downstream_loads_w ≤ fcu_rating_a × 230 V` (the FCU is the
  downstream load's OCPD; overloaded FCU would still trip under fault
  but the design is breach of best practice)

**Validator action:** iterate fcu_spurs[]; compute the 230 V × fcu_rating
limit; emit evidence per FCU with the downstream load + limit + headroom %.

**Citation:** `IET On-Site Guide §8.4.4 (8th Edition, AMD 2 update) +
BS 7671:2018+A2:2022 §433 (top-level — sub-clause §433.2 not transcribed
in verified file; the FCU spur rules are in IET OSG)`. Rule TOP-12.

**Rationale:** an over-loaded FCU is a design defect but not a structural
compliance breach (because the FCU would still trip under fault). MEDIUM
severity reflects that — engineer fixes it in design iteration without
blocking the IR ship.

## INV-18 — EV RCD Type A/B selection (HIGH)

**Severity:** HIGH on every EV charge circuit (every circuit where
`load_type` matches `ev_charge_*` and `ev_charge_metadata` is present).

**Rule (per rule EV-03):** RCD type MUST follow Reg 722.531.3.101:
- `rcd_type == "type_a"` iff `charging_unit_dc_detection_a ≥ 6`
- `rcd_type == "type_b"` iff `charging_unit_dc_detection_a < 6`

Type A on a charging unit without built-in 6 mA DC residual detection is
a HIGH safety failure (DC fault current blinds the Type A; only Type B
detects DC).

**Validator action:** for each EV circuit, read both fields; apply the
rule; FAIL HIGH if mismatched. Emit evidence with the declared values +
why the rule fired the way it did.

**Citation:** `BS 7671:2018+A2:2022 §722.531.3.101 (verified) + IET Code
of Practice for EV Charging Equipment Installation (4th Ed)`. Rule EV-03.

**Rationale:** this is the most common EV install safety failure surfacing
in real EICR findings — engineers default to Type A because it's cheaper
without checking the charging unit's DC detection capability.

## INV-19 — Cable-sizing cascade integration with building_diversity (MEDIUM)

**Severity:** MEDIUM when both `building_diversity.per_circuit_demand_inputs[]`
AND `consumed_intents.cable_sizing.payload.circuits[]` are present; N/A
otherwise.

**Rule (per rule BLD-05):** every entry in `building_diversity.
per_circuit_demand_inputs[]` MUST have a matching entry in
`consumed_intents.cable_sizing.payload.circuits[]` by `circuit_id`, AND
the `post_per_load_diversity_a` value in small-power's IR MUST reconcile
with cable-sizing's `design_current_a` field for that circuit within ±5%
tolerance.

**Validator action:** iterate per_circuit_demand_inputs[]; for each entry,
find the matching cable-sizing circuit; compute the % drift; FAIL MEDIUM
if any drift exceeds 5%.

**Citation:** skill-internal cross-skill integration (cluster roadmap §6.7
cascade DSL). Rule BLD-05.

**Rationale:** without INV-19, the building_diversity output could diverge
from the cable-sizing input that small-power consumes. INV-19 makes the
cascade traceable end-to-end and catches the most common iteration
defect — small-power updates its building_diversity numbers without
re-consuming a fresh cable-sizing intent.

---

### 3. Intent extraction validation

Project the IR down to the intent shape declared by `small-power-intent.schema.json` (per generator Step 13). Validate against that schema.

Required intent fields:
`project_id`, `parent_db_designation`, `circuits[]` (each circuit must have `circuit_id`, `topology`, `breaker_rating_a`, `breaker_type`, `diversified_max_load_a`, `rooms_covered`).

Schema is `additionalProperties: false` — emit only the declared fields.

If the intent extraction fails schema validation, emit `{"valid": false, "stage": "intent", "errors": [...]}`.

## Output

Emit a single JSON object:

```json
{
  "valid": true | false,
  "stage": "schema" | "invariants" | "intent" | "passed",
  "errors": [
    {"code": "INV-NN", "path": "$.circuits[2].rcd_posture", "message": "..."}
  ],
  "warnings": [
    {"code": "INV-NN", "path": "$.drawing_layout.sheet_size", "message": "..."}
  ]
}
```

`valid: true` requires ALL of:

- Schema validation passes
- INV-01 through INV-09 all pass (no hard fails); INV-10 is warning-only and does not block valid: true; INV-11 (v1.1) must pass when cable-sizing intent is consumed, otherwise it is a no-op; INV-12 (v1.2) must pass when any room.room_type is in the Part-7 set, otherwise it is N/A
- Intent extraction validates against `small-power-intent.schema.json`

Warnings from INV-06 (unjustified Type B) and INV-10 (drafting standard mismatch) do not block `valid: true` but appear in `warnings[]` for engineer review.

`stage` records where validation stopped (or `"passed"` for full success).

## Floor plan context

When the prompt context includes a `## Floor plan context` markdown
block, the validator MUST surface a finding for any of:

1. IR places an entity in a room not listed in the block.
2. The block flagged unconfirmed rooms AND the IR's `assumptions`
   array does not mention the unconfirmed rooms when those rooms were
   consumed.
3. IR's `building_label` field (if present) does not match the
   building label in the block.
4. IR omits `floor_plan_context_consumed: true` when the block was
   present.

Findings should cite the room name and the block location so the
reviewer can correlate.
