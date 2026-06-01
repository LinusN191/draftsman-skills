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

Run all 11 INV checks below. For each, emit a violation if the rule fails. Severities are either **Hard fail** (blocks `valid: true`) or **Warning** (does not block but appears in `warnings[]`). INV-11 is conditional on cable-sizing intent consumption (v1.1 hybrid mode) — it is a no-op when no cable-sizing intent is consumed.

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
- INV-01 through INV-09 all pass (no hard fails); INV-10 is warning-only and does not block valid: true; INV-11 (v1.1) must pass when cable-sizing intent is consumed, otherwise it is a no-op
- Intent extraction validates against `small-power-intent.schema.json`

Warnings from INV-06 (unjustified Type B) and INV-10 (drafting standard mismatch) do not block `valid: true` but appear in `warnings[]` for engineer review.

`stage` records where validation stopped (or `"passed"` for full success).

## Architectural state (Sprint 4-AB)

When `architectural_state` is present, the validator MUST surface a
finding for any of:

1. An entity whose centroid is not contained by any
   `floors_in_scope[].rooms[].polygon` in scope.
2. `unconfirmed_rooms_in_scope > 0` AND the IR's `assumptions` array
   does not mention the unconfirmed rooms.
3. The IR's `building_label` field (if present) does not match
   `architectural_state.building.label`.

Findings should reference the room ID and the architectural state
payload location so the reviewer can correlate.

See `shared/architectural_state_contract.md` for the full contract.
