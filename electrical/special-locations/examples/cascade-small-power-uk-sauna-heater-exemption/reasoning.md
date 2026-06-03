# Reasoning — cascade-small-power-uk-sauna-heater-exemption

## Cascade context

D.1 producer-side fixture closing the integrity loop for the
**small-power consumer** example `uk-sauna-with-heater-exemption`
(Phase C.4 of the Sprint D4 dispatch).

At C.4-ship the consumer INLINED its
`consumed_intents.special_locations_zoning.payload` with the cascade
payload because this producer fixture did not yet exist
(DEFERRED-POINTER state honest-disclosed in the C.4 input.json
`_cascade_disclosure` block). D.1 emits the producer-side
`intent-out.json` byte-identical to that inlined payload — verified by
Python dict equality at D.1 ship.

The fixture is **functionally identical** to the existing standalone
`electrical/special-locations/examples/uk-sauna-with-3-zone-derivation/`
example but explicitly tagged as a small-power-consumer cascade source
via `_special_locations_cascade_source`. The file-tree naming makes
the producer-side intent of "this is the small-power-consumer source"
auditable.

## Step 0 — Cascade prereq check

- `_special_locations_cascade_source.consumer_skill = small-power`
- `_special_locations_cascade_source.consumer_invariant_signalled`
  records INV-12 (4 sub-check sequence) on
  `rooms[].room_type='sauna'` Part-7 enum trigger.
- `_special_locations_cascade_source.upstream_consumer_intent_location
  = null` — special-locations is the PRODUCER; small-power is the
  CONSUMER. One-way emission. `consumed_lighting_layout_intent` in
  `intent-out.json` is `null` accordingly.

## Step 1 — Room classification

UK 2 400 × 2 000 mm domestic sauna cabin. `room_type = sauna` — the
Part-7 enum trigger that forces the consumer's `allOf` clause
requiring `consumed_intents.special_locations_zoning`. Ceiling 2 400
mm; floor tiles; ambient 90 °C; `is_wet_room: false` (sauna is dry
heat, not bath); `is_external: false`.

## Step 2 — Anchor inventory

1 anchor `heater_1`, `sauna_heater`, 400 × 400 mm at NW corner
`(200, 1600)`. 6 kW BS EN 60335-2-53 floor-standing electric heater.
Provenance: `architectural_drawing_extraction` (strongest tier).

## Step 3 — Zone derivation (BS 7671:2018 §703)

3 zones per the §703 zone-table convention:

| zone_id              | zone_type     | plan polygon (mm)                              | height (mm) | IP_min | V_max | RCD     |
|----------------------|---------------|------------------------------------------------|-------------|--------|-------|---------|
| `zone_heater_1_z1`   | sauna_zone_1  | (0,1100)-(1100,1100)-(1100,2000)-(0,2000)      | 0–2400      | IPx4   | 230   | n/a*    |
| `zone_heater_1_z2`   | sauna_zone_2  | (0,0)-(2400,0)-(2400,2000)-(0,2000)            | 0–2400      | IPx4   | 230   | 30 mA   |
| `zone_heater_1_z3`   | sauna_zone_3  | (0,0)-(2400,0)-(2400,2000)-(0,2000)            | 1500–2400   | IPx4   | 230   | 30 mA   |

*Zone 1 `rcd_required_ma = null` records the heater-circuit exemption
per §703.411.3.3.

Zone 1 = heater footprint + 500 mm padding per §703 zone-table; the
unclipped polygon `(-300,1100)-(1100,2500)` is clipped to the room
polygon yielding `(0,1100)-(1100,2000)`. Zone 2 = sauna body polygon
(shown as full room rectangle for derivation transparency; runtime
subtracts Zone 1 for plan rendering — `overlapping_with_zone_ids`
records the z1↔z2 overlap). Zone 3 = full room polygon at
`height_min: 1500` mm to ceiling 2 400 mm; vertical-separation overlap
with Zone 2 declared.

## Step 4 — Electrical constraints

1 constraint of type `rcd_blanket_by_room`:

- `applies_to_room_polygon: true`
- `rcd_rating_ma: 30`
- `applies_to_circuit_types`: `lighting`, `sockets`, `control_gear`,
  `thermostat`, `extract_fan` (deliberately OMITS the sauna heater
  circuit)
- `sauna_heater_excluded: true` ← preserves the §703.411.3.3
  heater-exclusion language

Citation: `BS 7671:2018 §703.411.3.3`.

## Step 5 — Consume small-power intent (1 fixture)

1 fixture consumed from the upstream small-power C01 dedicated radial:

| fixture_id                      | type                                | position           | IP   | V   | derived_zone     |
|---------------------------------|-------------------------------------|--------------------|------|-----|------------------|
| `heater_circuit_termination`    | `sauna_heater_hardwired_termination`| (200, 1600, 200)   | IPx4 | 230 | `zone_heater_1_z1` |

The heater is **hard-wired** (not a socket). The upstream C01 circuit
has `rcd_posture = no_rcd_with_documented_§411_exception` with
`rcd_exception_citation` routing to §703.411.3.3 + BS EN 60335-2-53 —
this preserves at the small-power layer the §703.411.3.3
heater-exclusion expressed in the constraint here.

## Step 6 — INV-08 walk-through (1 fixture)

For `heater_circuit_termination` inside Zone 1:

- **(a) type_prohibited:** `sauna_heater_hardwired_termination` is
  NOT in Zone 1's prohibited list
  (`socket_230v`/`switch_230v`/`luminaire_non_ip_rated`/`non_heat_rated_cable_load`).
  The heater itself is permitted at the heater anchor position by
  construction. PASS.
- **(b) ip_below_min:** IPx4 ≥ IPx4. PASS.
- **(c) switch_distance_too_close:** N/A — not a switch. PASS.
- **(d) voltage_above_max:** 230 V ≤ 230 V. PASS.

## Step 7 — Invariants

All 10 INVs PASS:

- **INV-01** 1 anchor → 3 zones; z1↔z2 + z2↔z3 overlaps declared.
- **INV-02** 1 compliant audit; 0 flags. 1:1 trivially holds.
- **INV-03** No §710 envelope. PASS.
- **INV-04** Sauna; `sauna_heater_excluded=true` records §703.411.3.3
  carve-out. PASS.
- **INV-05** Not a pool. PASS.
- **INV-06** No bath/whirlpool. PASS.
- **INV-07** No ELV anchor. PASS.
- **INV-08** 1 fixture (heater termination in Zone 1); all 4 sub-rules
  PASS.
- **INV-09** Architectural-extraction provenance (strongest tier).
- **INV-10** Rollup self-consistency holds.

## Step 8 — Consumer-side hand-off expectations

### small-power v2.0 INV-12 (4 sub-check sequence)

1. **Sub-check 1 (presence):** PASS — cascade present.
2. **Sub-check 2 (rollup):** PASS — `payload.compliant=true`,
   `zone_count=3`, `constraint_count=1`, all violation counts 0.
3. **Sub-check 3 (per-fixture):** PASS — sauna cabin has
   `sockets[]=[]` so zone-containment is vacuous on sockets; the
   hard-wired heater is not a socket (it is a hardwired termination
   consumed from C01).
4. **Sub-check 4 (flags + heater-exclusion):** PASS —
   `payload.non_compliance_flags=[]`; the cascade's
   `sauna_heater_excluded=true` is honoured by C01's
   `rcd_posture=no_rcd_with_documented_§411_exception` +
   `rcd_exception_citation` routing.

## Step 9 — Honest disclosures

- **Functional identity with standalone fixture.** This producer
  fixture is functionally identical to the existing
  `electrical/special-locations/examples/uk-sauna-with-3-zone-derivation/`
  fixture. The duplication is intentional: the file-tree naming makes
  the producer-side intent of "this is the small-power-consumer
  source" auditable. The standalone fixture is the GENERIC sauna
  reference; this fixture is the CONSUMER-TAGGED twin.
- **`existing_fixtures_audit[]` difference.** The standalone fixture
  audits a sauna luminaire + thermostat. This fixture audits the
  hard-wired heater termination consumed from upstream C01. The
  `special_locations_zoning` intent block (the cascade payload) is
  identical to the standalone fixture because the audit content does
  not propagate into the cascade payload — only zones + constraints
  + rollup propagate.
- **500 mm heater padding** is engineering convention (not numerically
  codified in verified §703); recorded in
  `calculation_summary.assumptions[]`.
- **Payload byte-equality.** Producer-side `intent-out.json`
  `special_locations_zoning` block is byte-identical to the payload
  inlined at C.4-ship in
  `electrical/small-power/examples/uk-sauna-with-heater-exemption/output.json
  consumed_intents.special_locations_zoning.payload`. Verified by
  Python dict equality at D.1 ship.

## Step 10 — Failure modes considered

- If `sauna_heater_excluded=false` were emitted in error, the heater
  would trip during normal operation due to thermal-pulse residual
  current — INV-04 would FAIL with sub-rule
  `sauna_heater_excluded_required_true` and the small-power C01
  `rcd_posture=no_rcd_with_documented_§411_exception` would lose its
  constraint-side anchor.
- If a generic 230 V socket were placed in Zone 1, INV-08 sub-rule
  `type_prohibited` would FAIL.
- If a non-IP-rated luminaire were placed at any height inside the
  sauna, INV-08 sub-rule `type_prohibited` would FAIL
  (`luminaire_non_ip_rated` is in all 3 zones' prohibited list).

## Cross-references

- Consumer:
  `electrical/small-power/examples/uk-sauna-with-heater-exemption/`
  (Sprint D4 Phase C.4).
- Functional twin (standalone):
  `electrical/special-locations/examples/uk-sauna-with-3-zone-derivation/`.
- Plan portion 4 Task D.1 Step 2 — producer-side fixture build.
