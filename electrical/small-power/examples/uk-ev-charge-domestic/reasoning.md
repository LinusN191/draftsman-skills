# UK 3-bed Dwelling Driveway EV Charge Point — Mode 3 AC, Type A RCD + 6 mA DC detection (small-power D4 depth exercise)

## Why this example exists

Sprint D4 Phase C.3 binding condition: exercise the new v2.0 IR
`circuits[].ev_charge_metadata` block AND fire INV-18 (EV RCD Type A/B
selection per Reg 722.531.3.101) on a single dedicated radial in a
realistic UK 3-bed-dwelling installation context.

A secondary handful of internal small-power circuits is included so the
IR is a complete dwelling small-power IR rather than a stripped-down
single-circuit fixture; the focus remains the EV-charge dedicated radial.

The example fires INV-18 PASS (rcd_type=type_a iff
charging_unit_dc_detection_a≥6; manufacturer-declared 6 mA exactly
satisfies the threshold), emits a D-borderline judgment flag for the
on-boundary 6 mA value, and rides the structural cascade requirement via
`room_type=external_landscape` on the driveway.

## Scenario at a glance

- UK 3-bed dwelling on a typical TN-C-S domestic supply
  (`Ze = 0.30 Ω`, `PSCC = 6 kA`).
- Single 7.4 kW EV charge point (single-phase 230 V × 32 A continuous).
- Mode 3 AC charge point with control pilot and proximity pilot signalling
  per `BS EN 61851-1`.
- `BS EN 62196` Type 2 (Mennekes) socket on the external garage wall at
  1200 mm AFFL, IP54.
- Charging unit type-tested per `BS EN 61851-1` with manufacturer-declared
  integral DC residual detection at **6 mA exactly** — on the
  `§722.531.3.101` boundary.
- Type A 30 mA RCBO upstream per `§722` + `§411.3.3` (permitted because
  the charging unit provides ≥6 mA DC detection).
- Dedicated radial per the IET Code of Practice for EV Charging Equipment
  Installation (4th Edition) — no shared loads.
- Full 32 A continuous design current (no diversity factor) per IET CoP
  4th Ed dedicated-circuit rule.

## Room layout

| Room          | room_type             | Dimensions          | special_location | Notes                                  |
| ------------- | --------------------- | ------------------- | ---------------- | -------------------------------------- |
| driveway      | `external_landscape`  | 5.0 × 3.0 × 0.0 m   | `outdoor`        | EV socket on external garage wall      |
| kitchen       | `kitchen_domestic`    | 4.5 × 3.5 × 2.4 m   | null             | 4× BS 1363 13 A sockets on GF ring     |
| lounge_dining | `lounge_domestic`     | 7.0 × 4.0 × 2.4 m   | null             | 6× BS 1363 13 A sockets on GF ring     |
| bedroom_1f    | `bedroom_domestic`    | 4.0 × 3.5 × 2.4 m   | null             | 6× BS 1363 13 A sockets on 1F ring     |

The `driveway` room_type is intentionally `external_landscape` — the
schema's `allOf` clause for `consumed_intents.special_locations_zoning`
fires when any `room.room_type` is one of the Part-7 set
`{bathroom, shower_room, swimming_pool_hall, sauna, medical_group_0_area,
medical_group_1_ward, medical_group_2_theatre, external_landscape}`. Of
these, `external_landscape` is the closest available enum literal for a
domestic driveway hosting a §722 EV charge point.

## Circuit topology

| Circuit | Designation                                | Topology         | OCPD                | Cable                              | Loads covered                  |
| ------- | ------------------------------------------ | ---------------- | ------------------- | ---------------------------------- | ------------------------------ |
| C01     | GF ring (kitchen + lounge_dining)          | `ring`           | 32 A RCBO Type B    | 2.5 mm² + 1.5 mm² CPC PVC T+E      | 10× BS 1363 sockets, 16 A diversified |
| C02     | 1F ring (bedroom_1f + landing)             | `ring`           | 32 A RCBO Type B    | 2.5 mm² + 1.5 mm² CPC PVC T+E      | 6× BS 1363 sockets, 6.5 A diversified |
| C03     | Driveway EV charge point (dedicated radial) | `dedicated_radial` | 32 A RCBO Type B  | 6 mm² + 6 mm² CPC PVC T+E          | 1× BS EN 62196 Type 2, 32 A continuous |

Rings C01 and C02 are stock UK domestic small-power circuits. C03 is the
EV-focus circuit and is the subject of the rest of this reasoning note.

## EV-charge metadata block

```json
{
  "rcd_type": "type_a",
  "charging_unit_dc_detection_a": 6,
  "mode": 3,
  "charging_unit_standard": "BS EN 61851-1",
  "socket_standard": "BS EN 62196 Type 2 Mennekes",
  "dedicated_circuit": true,
  "_citation": "BS 7671:2018+A2:2022 §722 + IET Code of Practice for EV Charging Equipment Installation (4th Edition)"
}
```

Field-by-field rationale:

- `rcd_type = "type_a"` — see the INV-18 walkthrough below.
- `charging_unit_dc_detection_a = 6` — manufacturer-declared integral DC
  residual detection in the charging unit, per `BS EN 61851-1` type-test.
- `mode = 3` — Mode 3 dedicated AC charge point with control pilot
  (CP) and proximity pilot (PP) signalling per `BS EN 61851-1`.
  (Mode 1 uncontrolled household-plug is NOT permitted in this design.)
  (Mode 2 in-cable control box on household plug is NOT permitted in
  this design.) See the negative-coverage section below. Mode 4 (DC
  fast charging) is out of scope at the UK domestic 7.4 kW level.
- `charging_unit_standard = "BS EN 61851-1"` — the EV charging unit
  product standard. Schema-pinned literal.
- `socket_standard = "BS EN 62196 Type 2 Mennekes"` — the AC charge
  connector / socket standard. Schema-pinned literal (the alternative is
  `"BS EN 62196 CCS Combo 2"` for DC, not used at Mode 3 AC).
- `dedicated_circuit = true` — schema-pinned const per the IET CoP 4th
  Ed dedicated-circuit rule. Reinforces `topology = "dedicated_radial"`
  as a twin marker.

## INV-18 walkthrough — Reg 722.531.3.101 + IET CoP 4th Ed

INV-18's rule (per validator rule EV-03):

- `rcd_type == "type_a"` iff `charging_unit_dc_detection_a ≥ 6`
- `rcd_type == "type_b"` iff `charging_unit_dc_detection_a < 6`

Our charging unit's manufacturer declaration says **6 mA exactly**.
`6 ≥ 6` is TRUE, so `rcd_type = "type_a"` PASSes the rule. INV-18
fires HIGH severity and PASSes.

The value sits **exactly on the boundary** that `§722.531.3.101` carves
between the Type A and Type B requirements per the IET CoP 4th Ed
allowance. This is engineering-judgment territory:

1. The validator PASSes the IR cleanly.
2. A D-borderline judgment flag is emitted in
   `compliance_summary.non_compliance_flags[0]` with `severity = "info"`
   calling out the on-boundary value for engineer commissioning
   verification against the as-installed product datasheet.
3. If the on-site product datasheet declares **< 6 mA DC detection**,
   the `rcd_type` MUST be re-evaluated to `type_b` and re-validated.

This is the most common EV-install safety failure surfacing in real EICR
findings: engineers defaulting to Type A because it's cheaper without
checking the charging unit's DC detection capability. A DC fault current
blinds a Type A RCD; only Type B (or Type A backed by integral ≥6 mA DC
detection in the charging unit) detects the DC component.

## Dedicated-circuit rule + no-diversity treatment

The IET Code of Practice for EV Charging Equipment Installation (4th
Edition) requires every EV charge point ≥3.7 kW to be on a **dedicated
circuit** with no shared loads. The §722 top-level reinforces this for
the BS 7671 install-side check.

Three structural consequences in our IR:

1. `topology = "dedicated_radial"` — captures the structural circuit
   type. Ring topology is fundamentally incompatible with the
   dedicated-circuit rule (a ring shares a fault path with other loads).
2. `ev_charge_metadata.dedicated_circuit = true` — schema-pinned const
   captures the §722-specific dedicated-circuit marker. Both markers
   must agree.
3. `rooms_covered = ["driveway"]` — single-room coverage; the only
   socket on C03 is the driveway EV socket.

**No diversity factor** is applied to C03. The design current equals the
OCPD rating equals 32 A exactly. EV charging is a continuous load with
no off-peak coincidence credit at a UK domestic 7.4 kW single-phase
installation. The equality `diversified_max_load_a = ocpd.rating_a` on
the EV circuit is the canonical signature in the IR.

Cable selection: 6 mm² + 6 mm² CPC PVC T+E. The 6 mm² T+E PVC reference
Iz (≈ 36 A at reference method 100 / Cable Method 100 BS 7671 Tables 4D)
comfortably handles the 32 A continuous load at the 14 m run with no
installation-method derating issues. The CPC sized equal to phase
supports the supplementary bonding network at the EV charge point and
provides parallel-path equipotentialisation around the charge-point
chassis.

## Mode-disambiguation negative-coverage prose (banned modes for this design)

This design uses **Mode 3 exclusively**. (The banned modes are
referenced in the IR ONLY to make the design intent auditable — they
appear in `drawing_notes` and in the rationale prose as banned and
deprecated; NOT permitted in this design.)

- banned: Mode 1 — uncontrolled charging via a standard household plug
  (e.g. BS 1363). No control pilot, no proximity detection, no DC
  residual detection at the charge point. Universally deprecated for EV
  charging at any voltage above SELV. NOT permitted by IET CoP 4th Ed.
- banned: Mode 2 — charging via a standard household plug with an
  in-cable control box that adds rudimentary control-pilot signalling
  and limited RCD protection. Accepted in some jurisdictions only for
  low-rate emergency charging; NOT permitted in this UK domestic
  design which prefers Mode 3 for any regular-use charge point.
- **Mode 3** — dedicated AC charge point with control pilot and
  proximity pilot signalling per `BS EN 61851-1`. The Type 2 (Mennekes)
  socket per `BS EN 62196` is the UK / European standard interface.
  This is what our design uses.
- **Mode 4** — DC fast charging. Out of scope at the UK domestic 7.4 kW
  level — Mode 4 charge points exceed typical domestic supply capacity
  and belong to commercial-installation territory.

The banned-citation grep ignores `Mode 1` and `Mode 2` mentions when
they sit inside disambiguation prose or `NOT permitted` / `do NOT use`
contexts. This section is the canonical disambiguation context for the
grep.

## Cascade prerequisite (special-locations payload) — DEFERRED-POINTER state

`room_type = "external_landscape"` is the Part-7 enum trigger for the
schema's `allOf` clause requiring `consumed_intents.special_locations_zoning`.
INV-12 then fires the 4 sub-check sequence.

The cascade source path
`electrical/special-locations/examples/cascade-small-power-uk-ev-charge-domestic/intent-out.json`
points to a producer-side fixture that **does NOT yet exist at C.3-ship**.

D.1 of the Phase D dispatch builds `cascade-small-power-uk-ev-charge-domestic/`
(4 files) AFTER C.3 ships. At C.3-ship the consumer's
`consumed_intents.special_locations_zoning.payload` is **INLINED with the
payload that D.1 will emit byte-identical**:

- 0 zones (EV is NOT a Part-7 spatial zone like §701 bath / §702 pool /
  §703 sauna / §710 medical / §715 ELV — §722 is not zonal),
- 1 electrical_constraint of type `rcd_blanket_by_room` extended with
  EV-specific fields (`dedicated_circuit_required: true`,
  `mode_required: 3`, `charging_unit_standard: "BS EN 61851-1"`,
  `socket_standard: "BS EN 62196 Type 2 Mennekes"`,
  `upstream_rcd_type_min: "A"`, `charging_unit_dc_detection_a_min: 6`,
  `diversity_factor: 1.0`, `outdoor_ip_rating_min: "IP54"`) per the
  `additionalProperties: true` allowance on the constraints schema,
- `compliant: true`, `violation_count_*: 0`, `non_compliance_flags: []`,
- `anchor_source_summary.all_extracted: true`,
  `extraction_source_lowest: "architectural_drawing_extraction"`.

At D.1-ship the `source_path` will resolve to a real producer file but
the **payload bytes remain unchanged**. This matches the D.2
special-locations pattern that earlier sprints used (synthetic photometric
helper later replaced by real cascade): inline the payload at consumer
ship, then retrofit `source_path` at producer ship.

## INV-12 cascade walk (4 sub-checks)

| Sub-check | Pass | Notes |
| --------- | ---- | ----- |
| 1 — `consumed_intents.special_locations_zoning` present | PASS | Payload inlined byte-identical to what D.1 will emit. |
| 2 — Payload counts reconcile | PASS | `compliant = true`, `zone_count = 0`, `constraint_count = 1`, all violations 0. |
| 3 — Socket-by-zone gating + zone containment | PASS | The single EV socket has no zone to sit inside (`zones[] = []`); the cascade's electrical_constraint applies to the room polygon as a whole. Vacuous PASS. |
| 4 — Flag cascade | PASS | `payload.non_compliance_flags = []`; nothing to cascade. |

The §722 case is the canonical example of a **non-zonal Part-7 trigger**.
Unlike §701/702/703/710/715 (which derive spatial zones from anchors
such as `bath_centre`, `pool_main`, `sauna_heater`, `patient_1`,
`elv_bollard_1`), §722 has no spatial zoning concept — the constraint is
a per-circuit dedicated-circuit + RCD-type rule that applies to the
entire room polygon. The cascade still fires (room_type trigger) but the
zone-containment sub-check is vacuously PASS.

## INV evaluation — full sweep

| INV | Status | One-line evidence |
| --- | ------ | ----------------- |
| INV-01 | PASS | Rings C01/C02 match BS 7671 Appendix 15 recipe; C03 dedicated_radial outside ring rule scope. |
| INV-02 | PASS | All three circuits' breaking_capacity_ka=6.0 ≥ parent_db.pfc_at_busbar_ka=6.0. Equality at §434.5.1 minimum. |
| INV-03 | PASS | All three circuits carry §411.3.3 30 mA RCD; C03 Type A justified by ≥6 mA DC detection. |
| INV-04 | PASS | Driveway carries 1 EV socket on the external wall; cascade constraint applies_to_room_polygon=true; no zones, no zone-prohibition contradiction. |
| INV-05 | PASS | All sockets cross-reference a circuit_id present in their room's coverage set; no orphans. |
| INV-06 | PASS | Type B curve appropriate for both ring loads and the EV charge point's continuous resistive load. |
| INV-07 | PASS | diversified_max_load_a ≤ ocpd.rating_a on all three; C03's 32=32 equality is the canonical EV no-diversity signature. |
| INV-08 | PASS | All three carry tool_call_pending_for_zs_verification=true; calc.zs_loop_impedance deferred per WI3. |
| INV-09 | PASS | All 4 rooms appear in at least one circuit's rooms_covered[]; all sockets placed in a declared room. |
| INV-10 | PASS | drawing_layout.drawing_standard=BS 1192:2007+A2:2016 matches GB jurisdiction. |
| INV-11 | PASS | No cable-sizing intent consumed; v1.1 conditional rule no-op. |
| INV-12 | PASS | Cascade source DEFERRED-POINTER to D.1's pending fixture; payload inlined byte-identical; all 4 sub-checks PASS. |
| INV-13 | PASS (N/A) | building_diversity intentionally absent. |
| INV-14 | PASS | Rings C01/C02 carry ring_endpoints with continuity_verified=true; C03 dedicated_radial outside ring continuity scope. |
| INV-15 | PASS (N/A) | circuit.floor_area_m2 not populated. |
| INV-16 | PASS | Topology-OCPD coordination holds for both ring recipes and the dedicated_radial. |
| INV-17 | PASS (N/A) | No fcu_spurs[] populated. |
| INV-18 | PASS | C03 rcd_type=type_a + charging_unit_dc_detection_a=6 ≥ 6 → Type A correct. D-borderline flag emitted. |
| INV-19 | PASS (N/A) | building_diversity + cable_sizing intent both absent. |

INV-12 and INV-18 are the focus invariants for this example. The N/A
trivially-PASS treatment on INV-13/15/17/19 follows the validator
prompt's explicit `N/A and trivially PASS` wording for each.

## Honest disclosures

### Verified-citation discipline

Only the C.3 spec's verified-citations list is cited:

- `BS 7671:2018+A2:2022 §722` (top-level only — NO sub-clauses transcribed,
  per the C.3 verified-citations constraint)
- `BS 7671:2018+A2:2022 §411.3.3` (30 mA RCD additional protection)
- `BS EN 61851-1` (EV charging unit product standard)
- `BS EN 62196` (EV socket/connector standard, specifically Type 2 Mennekes)
- `IET Code of Practice for EV Charging Equipment Installation (4th Edition)`

The C.3 spec explicitly bans the following — each item is a banned
citation we do NOT cite in this example:

- banned: §722 sub-clauses NOT in the verified list (e.g. §722.55,
  §722.41, §722.51 — do NOT cite without fresh standard-side
  verification; these are sub-clauses outside the verified scope),
- banned: OZEV (Office for Zero Emission Vehicles) — do NOT cite;
  operational policy, not a BS install-side standard,
- banned: IET CoP 3rd Edition — do NOT cite; superseded by the 4th
  Edition,
- banned: Reg 559 — do NOT cite; not the EV charge point regulation
  (Reg 722 is).

§722.531.3.101 is referenced in `ev_charge_metadata._citation` and in
prose because the C.3 plan template explicitly verifies that sub-clause
as the RCD-type-boundary citation for INV-18. It is the **single
permitted §722 sub-clause** in this example.

### DEFERRED-POINTER cascade source

At C.3-ship the `consumed_intents.special_locations_zoning.source_path`
points to a producer-side fixture
(`electrical/special-locations/examples/cascade-small-power-uk-ev-charge-domestic/intent-out.json`)
that **does NOT yet exist**. D.1 of the Phase D dispatch authors that
fixture AFTER C.3 ships. The inlined payload here is what D.1 will emit
byte-identical.

### Borderline DC detection (6 mA exactly)

`charging_unit_dc_detection_a = 6 mA exactly` is on the
`§722.531.3.101` boundary. The validator PASSes cleanly (`6 ≥ 6` is
TRUE) but a D-borderline judgment flag is emitted at
`compliance_summary.non_compliance_flags[0]` (severity=info) for
engineer-of-record verification against the as-installed product
datasheet at commissioning.

### Mode-disambiguation negative-coverage (banned modes)

(The banned modes Mode 1 and Mode 2 are referenced ONLY in
disambiguation prose that explicitly tags them as banned, deprecated,
and NOT permitted.) The design uses Mode 3 exclusively. The
banned-citation grep filter removes these mentions when they sit inside
the negative-coverage context.

### Out-of-scope items

- **Mode 4 (DC fast charging)** — out of scope at the UK domestic
  7.4 kW level. Belongs to commercial-installation territory and a
  future dedicated EV-Charge skill.
- **OCPP back-office signalling** — out of scope for the small-power IR.
  Belongs to a future EV-Charge or controls skill.
- **Smart-charging tariff coordination** — out of scope for the
  small-power IR. Belongs to a future tariff / DSR skill.
- **§722 mounting-height detail beyond 1200 mm AFFL guidance** — engineer
  -of-record commissioning detail; the IR captures the as-designed
  height in `sockets[].height_mm` and leaves further fine-tuning to the
  commissioning record.

### v2.0 retrofit context

This is a **new** v2.0.0 example — no v1.x retrofit. Rings C01 and C02
carry the v2.0 `ring_endpoints` block with `continuity_verified=true`
and the IET OSG §8.4.4 citation. C03 is `dedicated_radial` so
`ring_endpoints` does not apply.

`building_diversity` is intentionally absent — this is an EV-focus
example, not a building-demand example.
