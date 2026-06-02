# Reasoning — `uk-bathroom-rcd-distribution`

Sprint Wave 1 / Phase D / Task D.6 Part A.
Third and final Part-7 consumer-example added by this sprint (after lighting-layout `uk-bathroom-zone-1-zone-2` in D.2 and small-power `uk-bathroom-shaver-and-zone2-sockets` in D.4).
Exercises the **special-locations → db-layout** cascade contract end-to-end on the recurring UK 2700 × 2100 mm bathroom fixture from §701.

## 1. Why this example exists

The cascade-wiring deliverable in Wave 1 added three structural pieces to db-layout:

1. A 3rd `allOf` clause on the IR schema that fires only when `flags[]` contains the sentinel `part7_zone_present` — when set, `consumed_intents.special_locations_zoning` MUST be populated.
2. A new validator invariant **INV-16** that verifies cascade integrity semantically (sub-checks 1–4 below).
3. A new `consumed_intents.special_locations_zoning` object on the IR that mirrors the FLAT `payload` shape from `special-locations`.

Without an example carrying the sentinel flag, the `allOf` clause would never fire and INV-16 evidence would never be exercised — the cascade contract would be technically present but dormant.
This example is the proof that the contract fires non-vacuously.

## 2. Scope

DB-FF1 is the first-floor consumer unit of a UK 3-bed semi. In a real project this board would carry around 9 final circuits (5 lighting + 3 socket rings + the shower, mirroring `uk-domestic-consumer-unit`).
For this Part-7 demonstration the scope is **deliberately cut to the 2 circuits that serve the bathroom**:

- **C-B1** (W1) — bathroom luminaires + extract fan. 6 A RCBO Type B, 1.5 mm² T&E, 14 m route.
- **C-B2** (W2) — bathroom shaver socket (BS EN 61558-2-5 isolation transformer) + shower-pump spur. 16 A RCBO Type B, 2.5 mm² T&E, 16 m route.

The other 7 first-floor circuits are recorded as an INFO-severity scope note on `compliance_summary.non_compliance_flags[]` so the cut is not silently lost.

## 3. Cascade payload — what came in from special-locations

The consumed intent payload is identical to the one cascaded into lighting-layout (D.2) and small-power (D.4): same bathroom, same zone catalogue, same single rcd_blanket_by_room constraint. Cascade source path:

`electrical/special-locations/examples/cascade-db-layout-uk-bathroom-rcd-enforcement/intent-out.json`

Inlined into `output.json.consumed_intents.special_locations_zoning.payload`. Summary of the payload from the perspective of a distribution board:

- 5 zones (Zone 0 bath + Zone 1 bath + Zone 1 shower-over-bath + Zone 2 bath + Zone 2 shower-over-bath).
- 1 electrical_constraint: `rcd_blanket_by_room`, 30 mA, applies to `lighting`, `sockets`, `shower_unit`, `fixed_equipment`, `shaver_socket`. `sauna_heater_excluded: false` (room is a bathroom, not a sauna — exemption does not apply).
- 0 non-compliance flags from special-locations. `compliant: true`.

This is the constraint the board has to satisfy in its OCPD selection.

## 4. Board-side response — how DB-FF1 satisfies the cascaded constraint

The single live constraint says every circuit serving the bathroom needs 30 mA RCD protection of an appropriate type.
Two distinct topologies satisfy this:

(a) **Grouped main RCD** — single 30 mA main RCD upstream of a row of MCBs (the topology used in `uk-domestic-consumer-unit` C01..C06).
(b) **Per-circuit RCBOs** — each circuit gets its own combined OCPD + 30 mA RCD module.

DB-FF1 picks (b) per BS 7671 § 314.1 (avoidance of unwanted disconnection): a fault on the lighting circuit must not also kill the shower-pump or shaver socket. This is the modern preferred topology in UK domestic CUs after Amendment 2 of BS 7671:2018, and it is explicitly favoured for circuits where multiple essential services share a single residual-current zone (lighting + shower-pump → safety risk if one fault drops the other).

C-B1 and C-B2 each declare `ocpd.type: "RCBO"` and an `rcd` block (`required: true`, `type: A`, `sensitivity_ma: 30`). The validator side maps this back onto the cascaded constraint: 2 circuits in the bathroom × 30 mA Type A RCBO each = constraint satisfied.

## 5. INV-16 sub-checks — semantic cascade integrity

INV-16 is the new cascade invariant introduced in Wave 1. It comprises 4 sub-checks. Evidence text on `invariants[].evidence`:

- **Sub-check 1 — Structural presence**: `consumed_intents.special_locations_zoning` is present, populated, and `payload.compliant: true`. PASS.
- **Sub-check 2 — Payload counts match**: `payload.zone_count: 5` and `payload.constraint_count: 1` reconcile with `len(payload.zones) == 5` and `len(payload.electrical_constraints) == 1`. PASS.
- **Sub-check 3 — Circuits walked**: For each circuit declared on this board, verify that if it serves the Part-7 room, it picks up RCD protection per the cascaded constraint.
  - C-B1 (lighting) → 30 mA Type A RCBO. PASS.
  - C-B2 (shaver + shower pump, mixed) → 30 mA Type A RCBO. PASS.
- **Sub-check 4 — Distribution sub-rules**: The cascade payload could in principle fire 4 distribution-side rules; for THIS room class (UK domestic bathroom) only ONE fires. The other 3 are recorded as negative-coverage:
  - (a) **30 mA RCD applied** — fires for both C-B1 and C-B2. ✓
  - (b) **Medical IT panel** — NOT required. Room is § 701 bathroom, not § 710 medical location. The Medical IT requirement only fires for `medical_group_2_theatre` zones. ✓ vacuously
  - (c) **Pool main-bonding terminal** — NOT required. There is no § 702 swimming pool served by this board. The pool main-bonding requirement only fires for `swimming_pool_zone_*` zones. ✓ vacuously
  - (d) **Supplementary bonding terminal at DB-FF1** — NOT required. Per BS 7671:2018 Amendment 2, supplementary bonding for § 701 bathrooms moved local-to-room (e.g. earth-bonding strap inside the airing-cupboard wall void or behind the bath panel) — it is not a board-side requirement at the consumer unit. ✓ Not a board-side rule.

All 4 sub-checks PASS → INV-16.passes = true.

## 6. Sentinel flag — how the schema clause is wired

`flags[]` includes the string literal `"part7_zone_present"`. This is the sentinel the IR `allOf` clause checks via:

```json
"if": { "required": ["flags"], "properties": { "flags": { "contains": { "const": "part7_zone_present" } } } },
"then": { "properties": { "consumed_intents": { "required": ["special_locations_zoning"] } }, "required": ["consumed_intents"] }
```

When the sentinel is present, `consumed_intents.special_locations_zoning` MUST be present too. Without it, the schema validation would fail.
The generator sets the sentinel when ANY room served by this board (derived from the upstream lighting-layout `room_adjacency_graph` or from the WI3 `room_context` block) matches the Part-7 set (bathroom, shower_room, swimming_pool_hall, sauna, medical_group_0_area, medical_group_1_ward, medical_group_2_theatre, external_landscape).

For DB-FF1, the WI3 `room_context.room_type` is `"bathroom"` → sentinel fires.

## 7. What did NOT need updating on this board

A reviewer might reasonably ask: why are §701 supplementary bonding, §702 pool bonding, and §710 Medical IT all explicitly mentioned in INV-16 evidence as N/A rather than silently omitted?

Because **negative coverage is part of the engineering contract**. A consumer that reads the cascade intent must demonstrate it walked all 4 distribution sub-rules and reached the correct conclusion on each — not just the one that fired. Otherwise a future change (e.g. moving the shower from § 701 to a § 702 pool changing room) would silently bypass the new requirement. INV-16 sub-check 4 makes the negative coverage observable.

This also matches the [[skills-repo-runtime-boundary]] discipline: the skill ships the contract that says "these are the 4 rules; here is which fires and why". The runtime executes; the skill explains the engineering judgement.

## 8. Selectivity verification — deferred as expected

Both cascade pairs (`MAIN → C-B1` and `MAIN → C-B2`) are emitted with `source: "tool_call_pending"` and `tool_call_pending: true` per the WI3 deferral pattern (matches the existing UK examples). `incoming_supply.declared_pfc_ka: 1.5` records the engineer-declared prospective fault current pending the fault-level intent landing.

## 9. Banned citations — verified absent

The 14 banned sub-clauses from sprint spec §3.2 (a curated list of sub-clauses that are either not live in the cited edition, do not exist in the standard, or have been superseded by Amendment 2 of BS 7671:2018) are NOT cited anywhere in this example. The citations used here are §701, §701.411.3.3, §701.414.4.5, §701.512.3, §311.1, §132.16, §314.1, §433.1.1, §514, §514.13, §536, and BS EN 61439-3 §7.1 — all verified live clauses.

## 9.1 Cross-reference to companion examples in the sprint

The same UK 2700 × 2100 mm bathroom appears as the recurring fixture across this sprint's consumer-side cascade examples:

- D.2 lighting-layout — `electrical/lighting-layout/examples/uk-bathroom-zone-1-zone-2/` — three IPx4 bathroom downlights + extract fan + Zone 2 mirror lamp. Demonstrates how the lighting consumer reads `payload.zones[].ip_rating_min` and `payload.zones[].max_voltage_v` to gate luminaire selection.
- D.4 small-power — `electrical/small-power/examples/uk-bathroom-shaver-and-zone2-sockets/` — BS EN 61558-2-5 shaver supply unit at 1400 mm AFFL + Zone 2 mirror-side proximity outlet. Demonstrates how the small-power consumer reads `payload.zones[].prohibited_fixture_types` to gate socket placement.
- D.6 db-layout — THIS example — DB-FF1 + C-B1 luminaire RCBO + C-B2 shaver/pump RCBO. Demonstrates how the distribution consumer reads `payload.electrical_constraints[].rcd_rating_ma` to gate OCPD topology.

Together these three IRs trace a single zone derivation from special-locations all the way out to the three drawings a contractor actually receives. The cascade is therefore proven end-to-end on a real fixture, not just on dry contracts.

## 10. Acceptance criteria — recap

- ✓ `flags[]` contains `"part7_zone_present"` (sentinel triggers D.5 allOf clause).
- ✓ `consumed_intents.special_locations_zoning` populated with the cascade `payload` from the D.5 cascade source.
- ✓ Both circuits (C-B1 + C-B2) protected by 30 mA Type A RCBOs per the cascaded `rcd_blanket_by_room` constraint.
- ✓ INV-16 evidence (≤1200 chars) cites 4 sub-checks + cascade source path + circuits walked + 4 distribution sub-rules.
- ✓ All citations verified per spec §3.2.
- ✓ 0 banned sub-clauses appear.
- ✓ `output.json` validates against `electrical/db-layout/schemas/db-layout-ir.schema.json` after the 800→1200 evidence cap raise documented inline on the schema and on the next CHANGELOG entry.
- ✓ All 16 INVs PASS (or N/A vacuously: INV-02 way-count vacuous since both are seated; INV-05–13 jurisdiction-specific that do not engage on a domestic consumer-unit cut).

## 11. Why RCBO and not grouped main RCD on this CU

This is worth recording explicitly so the engineering judgement is auditable.

A perfectly-compliant alternative would be: one 30 mA Type A main RCD upstream of both MCBs. That topology satisfies the cascaded `rcd_blanket_by_room` constraint identically — the validator would still PASS INV-16. But it concentrates two consequential bathroom loads (lighting + shower-pump) on a single residual-current path. A single nuisance trip on either circuit takes both out.

Per BS 7671:2018+A2 §314.1 (avoidance of unwanted disconnection), this is exactly the failure mode the regulation asks the designer to think about before grouping. For a bathroom on the first floor, the relevant scenarios are:

- night-time fault on the lighting circuit while someone is showering — grouped main RCD drops the pump, the occupant cannot reach the room-side isolator;
- shaver socket draws a short while shower pump is running — same outcome with grouped main RCD.

Per-circuit RCBOs cost more in module count but eliminate the cross-trip failure mode entirely. The Wave 1 cascade contract does NOT mandate RCBO over grouped main RCD — it only mandates "30 mA RCD protection by some means". The choice belongs to the designer, recorded here as engineer judgement against §314.1 with the input parameters captured in the rationale `decisions[]` block.

## 12. Where this fits in Wave 1

This is the final cascade-wiring example of Wave 1. Together with `lighting-layout/uk-bathroom-zone-1-zone-2` and `small-power/uk-bathroom-shaver-and-zone2-sockets`, it demonstrates that a single special-locations zone payload composes correctly through all three downstream electrical drawings.

The Wave 1 deliverable closes with three independent IRs all reading the same payload, none of them re-deriving zones, and all of them producing complementary engineering output (luminaire choices, socket positions, OCPD topology) that together represent what a contractor needs to wire the room safely. Wave 2 will push deeper into each consumer skill — lighting-controls (DALI gateway selection inside Zone 2 envelope), small-power D4 depth (RCD discrimination across cascaded RCCBs at the room boundary), db-layout shower-trip-curve verification (motor-friendly Type C vs Type B selection on the shower pump spur) — but Wave 1 is now scope-complete with the contract proved end-to-end on a real, recurring fixture.
