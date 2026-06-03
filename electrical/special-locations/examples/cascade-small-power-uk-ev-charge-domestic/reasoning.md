# Reasoning — cascade-small-power-uk-ev-charge-domestic

## Cascade context

D.1 producer-side fixture closing the integrity loop for the
**small-power consumer** example `uk-ev-charge-domestic` (Phase C.3 of
the Sprint D4 dispatch).

At C.3-ship the consumer INLINED its
`consumed_intents.special_locations_zoning.payload` with the cascade
payload because this producer fixture did not yet exist
(DEFERRED-POINTER state honest-disclosed in the C.3 input.json
`_cascade_disclosure` block). D.1 emits the producer-side
`intent-out.json` byte-identical to that inlined payload — verified by
Python dict equality at D.1 ship.

## Step 0 — Cascade prereq check

- `_special_locations_cascade_source.consumer_skill` = `small-power`
- `_special_locations_cascade_source.consumer_invariant_signalled`
  records INV-12 (4 sub-check sequence) on
  `rooms[].room_type='external_landscape'` Part-7 enum trigger.
- `_special_locations_cascade_source.upstream_consumer_intent_location`
  = `null` — special-locations is the PRODUCER in this cascade;
  small-power is the CONSUMER. One-way emission. The
  `consumed_lighting_layout_intent` field in `intent-out.json` is
  `null` accordingly.

## Step 1 — Room classification

Driveway 5 000 × 3 000 mm rectangle (matches the small-power C.3
`input.json.room_briefs.driveway` dimensions). `room_type =
external_landscape` — the Part-7 enum trigger that forces the
consumer's `allOf` clause requiring
`consumed_intents.special_locations_zoning`. `is_external = true`;
`is_wet_room = false`; ambient 20 °C.

## Step 2 — Anchor inventory (empty)

`anchor_fixtures[]` is **empty**. The §722 EV charge point is
wall-mounted equipment, **not** a §701/§702/§703/§710 zone-deriving
anchor. The schema permits this (`minItems: 0` on the IR's
`anchor_fixtures` array).

## Step 3 — Zone derivation (empty)

`zones[]` is empty. §722 is NOT zonal in the §701 bath / §702 pool /
§703 sauna / §710 medical / §715 ELV sense — it is **constraint-only**.
The Part-7 enum trigger for the consumer's `allOf` clause fires on
`room_type='external_landscape'` regardless of zone-derivation
outcome — the trigger is room-type-driven, not zone-driven.

## Step 4 — Electrical constraints

1 constraint of type `rcd_blanket_by_room` with
`applies_to_room_polygon: true`. Extended per `additionalProperties:
true` on the constraints schema:

| Field                                  | Value                              |
|----------------------------------------|------------------------------------|
| `dedicated_circuit_required`           | `true`                             |
| `mode_required`                        | `3`                                |
| `charging_unit_standard`               | `BS EN 61851-1`                    |
| `socket_standard`                      | `BS EN 62196 Type 2 Mennekes`      |
| `upstream_rcd_type_min`                | `A`                                |
| `charging_unit_dc_detection_a_min`     | `6`                                |
| `diversity_factor`                     | `1.0`                              |
| `outdoor_ip_rating_min`                | `IP54`                             |

Citation:
`BS 7671:2018+A2:2022 §722 + §411.3.3 + IET Code of Practice for EV
Charging Equipment Installation (4th Edition)`.

The 6 mA value sits **EXACTLY** on the §722.531.3.101 boundary that
permits Type A upstream — engineer-of-record commissioning check
verifies the manufacturer-declared value against the on-site product
datasheet. The borderline-value flag is surfaced by small-power at the
consumer level (severity `info`), not duplicated at the
special-locations IR level (separation of concerns: special-locations
emits the constraint envelope; small-power surfaces the borderline
flag against the as-installed product).

## Step 5 — Consume small-power intent (1 fixture)

1 socket consumed from the upstream small-power C03 dedicated radial:

| fixture_id    | position (x,y,z)   | IP   | V   |
|---------------|--------------------|------|-----|
| `ev_socket_1` | (4800, 1500, 1200) | IP54 | 230 |

`derived_zone_id = null` because `zones[]` is empty.
`compliance_status = compliant`.

## Step 6 — INV-08 walk-through (vacuous on zones; constraint-only)

For 1 fixture:

- **(a) type_prohibited:** N/A — no zone to prohibit against
  (`zones[]` empty). PASS.
- **(b) ip_below_min:** N/A at the zone level; constraint-level
  `outdoor_ip_rating_min = IP54` is met (IP54 ≥ IP54). PASS.
- **(c) switch_distance_too_close:** N/A — not a switch. PASS.
- **(d) voltage_above_max:** N/A at zone level (no zone); 230 V is the
  expected charge-point voltage. PASS.

Constraint-level check: the room-polygon-wide `rcd_blanket_by_room`
constraint's `dedicated_circuit_required = true` is satisfied by the
upstream small-power C03 `dedicated_radial` topology +
`ev_charge_metadata.dedicated_circuit = true`. PASS.

## Step 7 — Invariants

All 10 INVs PASS:

- **INV-01** 0 anchors → 0 zones. Catalogue trivially holds.
- **INV-02** 1 compliant audit entry; 0 flags. 1:1 trivially holds.
- **INV-03** No Group 2 envelope. §710 medical IT N/A. PASS.
- **INV-04** Not bath/sauna; §701/§703 RCD blanket N/A. (The
  rcd_blanket_by_room constraint here is the §722 EV carve-out, not
  the §701/§703 blanket.) PASS.
- **INV-05** Not a pool. §702 main bonding N/A. PASS.
- **INV-06** No bath/whirlpool. §701.512.2 N/A. PASS.
- **INV-07** No `elv_luminaire` anchor. §715 ELV separation N/A.
  PASS.
- **INV-08** 1 vacuous-zone fixture + constraint-level checks all
  PASS.
- **INV-09** Empty anchor set; `anchor_source_summary` defaults
  per spec §5.5. PASS.
- **INV-10** Rollup self-consistency holds.

## Step 8 — Consumer-side hand-off expectations

### small-power v2.0 INV-12 (4 sub-check sequence)

When the small-power C.3 consumer runs INV-12 against this cascade:

1. **Sub-check 1 (presence):** PASS —
   `consumed_intents.special_locations_zoning` is present with
   `payload` (the producer's `special_locations_zoning` block, copied
   byte-identical from the intent-out's `special_locations_zoning`).
2. **Sub-check 2 (rollup):** PASS — `payload.compliant=true`,
   `zone_count=0`, `constraint_count=1`, all violation counts 0,
   `non_compliance_flags=[]`.
3. **Sub-check 3 (per-fixture):** PASS — the EV socket
   `BS_EN_62196_Type_2_Mennekes_socket_32A_AC` does NOT sit inside any
   zone (`zone_count=0` makes zone-containment vacuous); the cascade
   constraint applies to the room polygon and the IP rating +
   dedicated-circuit + DC-detection requirements are met by C03's
   `dedicated_radial` topology + `ev_charge_metadata` block.
4. **Sub-check 4 (flags):** PASS — `payload.non_compliance_flags=[]`;
   nothing to cascade.

## Step 9 — Honest disclosures

- **`anchor_fixtures[]` empty** is intentional and schema-permitted
  (`minItems: 0` on the IR's `anchor_fixtures` array; `minItems: 0` on
  the intent payload's `zones` array).
- **6 mA DC residual detection borderline.** Sits exactly on the
  §722.531.3.101 Type A boundary. Surfaced as a small-power
  `non_compliance_flag` severity=info at C.3 (separation of concerns).
- **`anchor_source_summary` on empty anchor set.** `all_extracted=true`
  and `extraction_source_lowest='architectural_drawing_extraction'`
  are the well-defined defaults per spec §5.5.
- **Payload byte-equality.** Producer-side `intent-out.json`
  `special_locations_zoning` block is byte-identical to the payload
  inlined at C.3-ship in
  `electrical/small-power/examples/uk-ev-charge-domestic/output.json
  consumed_intents.special_locations_zoning.payload`. Verified by
  Python dict equality at D.1 ship.

## Step 10 — Failure modes considered

- If the EV charge point lacked integral DC residual detection (or
  declared < 6 mA), `upstream_rcd_type_min` would flip to `B` per
  §722.531.3.101; the small-power C03's `rcd_type=type_a` would then
  fail INV-18 (EV RCD type-vs-DC-detection rule) and a HIGH
  non-compliance flag would cascade.
- If `dedicated_circuit_required=true` were violated by an upstream
  small-power circuit (e.g. a shared ring picking up the EV socket),
  the IET CoP 4th Ed rule would fire a CRITICAL flag.
- If the EV socket's IP rating were below IP54, the cascade
  constraint's `outdoor_ip_rating_min=IP54` would fire INV-08
  sub-rule (b) `ip_below_min`.

## Cross-references

- Consumer: `electrical/small-power/examples/uk-ev-charge-domestic/`
  (Sprint D4 Phase C.3).
- Analogous external-landscape pattern:
  `electrical/special-locations/examples/uk-external-landscape-elv-lighting/`
  (the only other production `room_type='external_landscape'` example
  in the special-locations skill).
- Plan portion 4 Task D.1 Step 2 — producer-side fixture build.
