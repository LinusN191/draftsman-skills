# UK Pool Hall — Sockets and Isolation with §702 Cascade (small-power Part-7 exercise)

## Why this example exists

Sprint D4 Phase C.1 binding condition: extend small-power's special-locations cascade
proof beyond §701 bathrooms into §702 swimming pools. The existing
`uk-bathroom-shaver-and-zone2-sockets` example fires INV-12 against a §701 cascade
payload. This example fires INV-12 against the §702 cascade payload sourced from
`electrical/special-locations/examples/cascade-lighting-layout-uk-pool-hall/intent-out.json`,
exercising:

- the pool_main anchor-driven 3-zone derivation (z0/z1/z2),
- the §702.415.1 pool main equipotential bonding constraint,
- the §702.55.4 changing-room overlap rule (Zone 2 effective-clipping at the
  architect-coordinated fixed barrier), and
- a 3-phase 16 A dedicated radial for a pool circulation pump alongside a 1-phase ring
  for cleaning-equipment sockets in the adjacent changing room.

`room_type = "swimming_pool_hall"` is selected as the exact-match Part-7 enum literal
so the schema's `allOf` clause for `consumed_intents.special_locations_zoning`
presence fires structurally and the validator's INV-12 fires semantically.

## Room context — UK commercial swimming pool hall + changing room

A 12.0 m × 6.0 m × 4.5 m commercial pool hall containing:

- a single rectangular pool basin (10 m × 5 m, depth 1.8 m, footprint in room-local
  coordinates `(1000, 500) → (11000, 5500)`, water surface at 200 mm above pool deck),
- a 4500 mm ceiling, and
- no socket outlets anywhere on the pool deck.

Adjacent to the pool hall on the south wall is a 4.0 m × 3.0 m changing room at
`y in [-3000, 0]`, `x in [4000, 8000]` in pool-hall-local coordinates. The changing
room participates in this example to host the cleaning-equipment sockets — the design
deliberately keeps the pool hall socket-free per §702 zone-table prohibitions and uses
the §702.55.4 barrier-clipping rule to legitimise placing 230 V sockets in the
changing-room volume south of an architect-coordinated full-height divider.

## Cascade prerequisite — what special-locations told us

`consumed_intents.special_locations_zoning.payload` carries the full upstream contract,
byte-identical to the source file:

- **3 zones** derived from the `pool_main` anchor:
  1. `zone_pool_main_z0` — Zone 0, pool basin interior volume, height 0–200 mm above
     deck, IPx8 + SELV ≤12 V only.
  2. `zone_pool_main_z1` — Zone 1, pool basin polygon extended 2 m horizontally,
     200–2500 mm AFF, IPx5 minimum, 230 V permitted with RCD.
  3. `zone_pool_main_z2` — Zone 2, further 1.5 m horizontal extension (total 3.5 m
     from pool edge), 200–2500 mm AFF, IPx4 minimum, 230 V permitted but
     `prohibited_fixture_types = [socket_230v]`.
- **1 electrical constraint**: `pool_main_equipotential_bonding`,
  `conductor_csa_min_mm2 = 10`, applies to `pool ladder rails`, `pool pipe fittings`,
  `pool surrounds`, `metallic balustrade`, `deck drain grilles`.
- `compliant = true`, `non_compliance_flags = []`.

Important geometry detail: the Zone 2 polygon `(-2500, -3000) → (14500, 9000)` is
shown **unclipped** in the cascade derivation. Runtime is expected to intersect it
with the room polygon. The cascade source's `_derivation_note` on `zone_pool_main_z2`
explicitly calls this out:

> Polygon shown unclipped — south edge at y=-3000 enters the adjacent changing-room
> polygon (located at y=-3000 to 0). Within 200mm threshold triggers reviewer D-2
> (§702.55.4 changing-room barrier check).

That `(§702.55.4 changing-room barrier check)` is the carry-forward judgment that this
small-power consumer must resolve.

The cascade source path is:
`electrical/special-locations/examples/cascade-lighting-layout-uk-pool-hall/intent-out.json`.

That cascade was authored against the lighting-layout downstream consumer. Since
special-locations IR is anchor-driven (3 zones come from `pool_main` geometry, 1
bonding constraint comes from the same anchor — neither depends on luminaire-vs-socket
intent), the payload is engineering-equivalent for the small-power consumer. The
honest disclosure: a small-power-specific `cascade-small-power-uk-pool-hall-pass` does
not exist at v1.0; a future Wave 2 sprint will backfill it on the special-locations
producer side once a small-power-anchor variant is needed by another downstream skill.

## §702.55.4 changing-room overlap rule and barrier coordination

`§702.55.4` (per the cascade source's `_clause_citation` and `_derivation_note`
convention) is the changing-room overlap rule: Zone 2 extension into a changing room
is permitted only where a fixed barrier of height ≥2.5 m AFF separates the
changing-room volume from the pool-zone side. Where the barrier is present and
verified, the effective Zone 2 polygon is clipped at the pool-side face of the
barrier.

The design installs an architect-coordinated **full-height fixed divider wall at
y = -1500 mm** inside the changing-room polygon. The divider runs the full
4000 mm changing-room width (x=4000..8000) and rises to 2.5 m AFF (full ceiling
height — the changing room ceiling is 2.5 m, so the divider effectively goes
ceiling-to-floor). Per §702.55.4:

- North of the barrier (y in [-1500, 0]) — Zone 2 applies. No 230 V socket may be
  placed here.
- South of the barrier (y in [-3000, -1500]) — Zone 2 is effectively clipped. 230 V
  sockets are permitted, subject to the §702 zone-table general requirements (RCD
  protection, IP rating in line with the local splash exposure).

The 2 cleaning-equipment sockets are placed on the changing-room south wall at
y = -3000 mm — 1500 mm beyond the barrier, well outside the effective Zone 2 envelope.

Barrier compliance is engineer-of-record's commissioning verification per Part 6.
This is encoded in three places:

1. `input.json._barrier_declaration` — captures the architect coordination.
2. `compliance_summary.assumptions[4]` — captures the engineer-of-record verification
   commitment.
3. `compliance_summary.non_compliance_flags[2]` — info-severity flag making the
   commissioning action visible to the runtime / engineer.

## Socket placement decisions

The design ships zero 230 V general-purpose sockets inside the pool-hall room
polygon. Pool hall `sockets[] = []`. The changing room carries exactly two sockets:

1. `changing-S01`: `BS_EN_60309_2_industrial_16A_230V_blue`, mounted on the south
   wall at room-local (5000, -3000, 450). IP55 rated.
2. `changing-S02`: same type, mounted at (7000, -3000, 450). IP55 rated.

Both at 450 mm AFFL. Both outside the effective Zone 2 polygon after §702.55.4
clipping. Type literal `BS_EN_60309_2_industrial_16A_230V_blue` is distinct from the
zone's `prohibited_fixture_types = [socket_230v]` enum literal — even without the
§702.55.4 barrier clipping, the strict literal-match interpretation would already
pass. The barrier clipping provides defence in depth.

The pool circulation pump is **not** a socket — it's a hard-wired 3-phase 5.5 kW
motor in the adjacent plant room (outside the pool-hall room polygon, therefore
outside all §702 zones). The motor frame is separately bonded to the ME terminal via
a 10 mm² supplementary tail per §702.415.1.

## Circuit topology + RCD posture

Two circuits:

- **C01 — Changing-room cleaning ring final**. 20 A Type B RCBO + 2.5 mm² +
  1.5 mm² CPC PVC T+E ring, 22 m total run. Ring endpoints both land at
  `mcb_way_id = DB-POOL-1-WAY-1`. Diversified load 8.7 A (well inside the 20 A
  breaker rating). Type A 30 mA RCD per BS 7671:2018+A2:2022 §411.3.3 default
  for sockets ≤32 A; §702.415.1 cascaded constraint reinforces this.
- **C02 — Pool pump dedicated 3-phase radial**. 16 A Type C RCBO + 2.5 mm²
  5-core SWA (XLPE 90 °C insulation, suited to plant-room ambient), 18 m run.
  Diversified load 9.5 A. Type A 30 mA RCD per §702.415.1 (which mandates 30 mA RCD
  on all circuits supplying or passing through Zone 0/1/2 — though the pump motor
  is OUTSIDE the §702 zones, the dedicated supply still passes the deck-area
  containment via the cable route between DB-POOL-1 and the plant room).

C02 Type C curve rationale: 5.5 kW 3-phase motors typically exhibit 6× FLC start-up
inrush. Type C tripping band (5–10×) accommodates this; Type B (3–5×) would
nuisance-trip on every start. Selection per BS EN 60898-1 and IET OSG general motor
guidance.

20 A breaker on the ring (versus the 32 A maximum permitted by IET OSG §8.4.4)
matches the diversified cleaning-equipment load with comfortable headroom while
giving better cable-thermal margin on the small 22 m ring.

## INV-12 cascade evidence (4 sub-checks walked)

The validator's INV-12 evidence string (≤800 chars per IR schema cap):

> Cascade source: electrical/special-locations/examples/cascade-lighting-layout-uk-pool-hall/intent-out.json.
> Sub-check 1 PASS (consumed_intents.special_locations_zoning present).
> Sub-check 2 PASS (payload.compliant=true, 3 zones, 1 pool_main_equipotential_bonding constraint, 0 flags).
> Sub-check 3 PASS — walked sockets: pool_hall.sockets[]=[] (zero); changing-S01 + changing-S02 are
> BS_EN_60309_2 industrial type (not socket_230v literal) AND at y=-3000 sit ≥1500 mm beyond the
> §702.55.4 architect-coordinated fixed barrier at y=-1500, outside the effective Zone 2 envelope.
> Sub-check 4 PASS — payload.non_compliance_flags=[]; nothing to cascade.
> BS 7671:2018+A2:2022 §702.415.1 + §702.55.4.

Walking each sub-check explicitly:

1. **Sub-check 1 — cascade present.** `consumed_intents.special_locations_zoning.payload`
   is populated with `intent_version=1.0.0`, source_path pointing at the lighting-layout
   pool-hall PASS cascade, and the full payload object byte-identical to the source.
   The schema's `allOf` clause for `room_type=swimming_pool_hall` is satisfied.
2. **Sub-check 2 — upstream compliant.** `payload.compliant == true`. The 3 zones
   reconcile (z0 contained within pool basin footprint, z1 = z0 polygon plus 2 m
   horizontal extension, z2 = z1 plus a further 1.5 m). The single
   pool_main_equipotential_bonding constraint is well-formed with conductor CSA
   ≥10 mm² and an explicit extraneous-parts list.
3. **Sub-check 3 — socket/zone cross-walk.** The pool hall has `sockets[] = []` so
   zero work for that room. The changing-room sockets each get walked against the
   zone catalogue:
   - **Geometry containment.** Both sockets at y=-3000 sit within the unclipped Zone 2
     polygon `(-2500, -3000) → (14500, 9000)` because the polygon includes its south
     edge. But §702.55.4 clipping applies: with the architect-coordinated barrier at
     y=-1500, the effective Zone 2 polygon is the unclipped polygon intersected with
     the pool-side region (y ≥ -1500). Both sockets at y=-3000 are 1500 mm south of
     the barrier, OUTSIDE the effective Zone 2 polygon.
   - **Type literal.** `BS_EN_60309_2_industrial_16A_230V_blue` is not the string
     `socket_230v`, so even without §702.55.4 clipping the prohibited-fixture-type
     literal match fails (in favour of the design). The IP55 rating exceeds the
     IPx4 minimum Zone 2 would have required.
   - PASS recorded with reference to the §702.55.4 barrier-clipping decision.
4. **Sub-check 4 — flag cascading.** `payload.non_compliance_flags[]` is empty.
   Nothing to cascade. The `compliance_summary.non_compliance_flags[]` present in this
   IR contains only `severity: info` design / engineering-judgment notes (NOT
   cascaded failures), so no `_cascaded_from: special-locations` attribution is
   required (and the schema's strict `additionalProperties: false` on flag items
   would reject one anyway).

All four sub-checks resolve PASS. INV-12's IR record carries
`{id: "INV-12", passes: true, severity: "high", evidence: "…"}`.

## INV-13 through INV-19 walk-through

- **INV-13 (building_diversity self-consistency, HIGH/N-A)** — `building_diversity`
  is intentionally absent. The validator's INV-13 wording explicitly resolves to
  "N/A and trivially PASS when absent (input not supplied)". This example's
  engineering scope is the §702 cascade + ring-vs-radial mix; building-wide demand
  calculation is out of scope (covered by Phase A/B examples).
- **INV-14 (ring continuity, HIGH)** — C01's `ring_endpoints` is populated:
  `endpoint_a_xy = (4200, -2900)`, `endpoint_b_xy = (7800, -2900)`, both at
  `mcb_way_id = DB-POOL-1-WAY-1`, `continuity_verified = true`. Sub-check 1 (both
  ends at same way) PASS. Sub-check 2 (continuity_verified=true) PASS. C02 is
  dedicated_radial — INV-14 does not apply to radial circuits.
- **INV-15 (per-circuit floor-area cross-check, HIGH/N-A)** — `circuit.floor_area_m2`
  is not populated on either circuit (the v2.0 field is optional). INV-15 only
  evaluates when both `floor_area_m2` AND `rooms_covered[]` are populated; absent
  the former, no Σ-tolerance reconciliation is computed.
- **INV-16 (OCPD-topology coordination, HIGH)** — C01 ring 20 A on 2.5 mm² T+E
  satisfies the sub-rule `topology=ring → MCB ≤ 32 A` with 12 A spare. C02
  dedicated_radial 16 A on 2.5 mm² 5-core SWA — the validator INV-16 wording
  explicitly says `topology=dedicated_radial → MCB sized by connected load per
  §433.1.1 (cable-sizing's domain; INV-16 trivially PASSES on dedicated_radial)`.
- **INV-17 (FCU spur modelling, MEDIUM/N-A)** — neither circuit has `fcu_spurs[]`
  populated. Industrial-socket cleaning equipment uses BS EN 60309-2 plug
  interface, not FCU-fed. The pump is a direct-wired motor, not FCU-fed.
- **INV-18 (EV RCD type, HIGH/N-A)** — no circuit has `load_type` matching
  `ev_charge_*`. INV-18 only evaluates on EV-charge circuits where
  `ev_charge_metadata` and `rcd_type ↔ charging_unit_dc_detection_a` are present.
- **INV-19 (cable-sizing + building_diversity cascade, MEDIUM/N-A)** — neither
  `building_diversity.per_circuit_demand_inputs[]` nor
  `consumed_intents.cable_sizing.payload.circuits[]` is present. The reconciliation
  rule (post_per_load_diversity_a ≈ design_current_a ±5 %) has nothing to reconcile.

All 19 INVs emit; INV-12 + INV-14 + INV-16 PASS as genuine PASSes; INV-13/15/17/18/19
PASS as N/A-vacuous; INV-01 through INV-11 PASS as genuine PASSes against the
baseline small-power rules. Zero FAILs.

## Honest disclosures (4-place)

The D.4 special-locations cascade pattern requires the engineer-of-record cascade-source
reuse to be disclosed in four places — this example places the disclosure as follows:

1. **`input.json._cascade_disclosure`** — explicit human-readable narrative naming the
   lighting-layout source and the anchor-driven equivalence argument.
2. **`output.json.compliance_summary.assumptions[6]`** — engineering assumption
   recording the REUSE relationship and the Wave 2 backfill plan on the producer side.
3. **`output.json.rationale.sections[6]` (Honest disclosures section)** — narrative
   summary in the chat-visible rationale exposing the reuse decision.
4. **`reasoning.md` (this file) "Cascade prerequisite" and "Honest disclosures (4-place)"
   sections** — long-form engineering walkthrough making the reuse and its limitations
   explicit.

Additional disclosures captured in `compliance_summary.assumptions[]`:

- **§702.55.4 barrier verification commitment** (assumption #5) — the barrier
  ≥2.5 m AFF height and full-width continuity is architect-coordinated input + EOR
  commissioning verification.
- **Pool pump location outside §702 zones** (assumption #4) — the plant-room
  location keeps the pump motor outside Zone 0/1/2 vertical+horizontal extents.
- **BS EN 60309-2 selection rationale** (assumption #3) — the IP55 rating is
  defensive over-rating given the changing-room splash exposure.
- **v2.0 retrofit context** (assumption #8) — this is a NEW v2.0.0 example so no
  v1.x retrofit is needed; the `ring_endpoints` are designed-from-fresh, not
  retrofitted.
- **INV-13/19 N-A scope discipline** (assumption #9) — making the intentional
  absence of `building_diversity` explicit.

## Standards cited

Only the verified citations per the small-power v2.0.0 D4 sprint spec §2.3 verified
table:

- BS 7671:2018+A2:2022 §411.3.3 — additional protection for socket outlets ≤32 A
  (Type A 30 mA RCD default; reinforced by §702.415.1 in pool locations).
- BS 7671:2018+A2:2022 §411.4.5 — earth fault loop impedance limits (Zs deferred to
  calc.zs_loop_impedance per WI3).
- BS 7671:2018+A2:2022 §433.1.1 — overcurrent protection coordination with cable
  current-carrying capacity (used by INV-16).
- BS 7671:2018+A2:2022 §434.5.1 — breaking capacity of OCPDs ≥ prospective fault
  current (used by INV-02).
- BS 7671:2018+A2:2022 §526 (top-level) — terminations (referenced by ring_endpoints
  `_citation`).
- BS 7671:2018+A2:2022 §702 (top-level) — Special Installations or Locations: pool
  basins, paddling pools, fountains.
- BS 7671:2018+A2:2022 §702.415.1 — pool main equipotential bonding (≥10 mm²
  conductor to all extraneous-conductive-parts).
- BS 7671:2018+A2:2022 §702.55.4 — changing-room overlap rule (Zone 2 extension into
  changing rooms permitted only beyond a fixed barrier ≥2.5 m AFF).
- BS 1192:2007+A2:2016 — drawing-management conventions (sheet size A2, scale 1:50).
- BS EN 60898-1 — circuit breakers for overcurrent protection (curve B for C01
  cleaning ring, curve C for C02 motor inrush).
- BS EN 61008 — RCD selection (Type A 30 mA on both circuits).
- BS EN 60309-2 — industrial plug and socket-outlet system (16 A blue 230 V
  selection for cleaning-equipment plug-in).
- IET On-Site Guide §8.4.4 (8th Edition) — ring final circuit topology + ring
  composition recommendation (used by INV-14 ring_endpoints citation).
- IET On-Site Guide Appendix A — diversity factors for general-purpose sockets.

## Validator outcome

All 19 INVs emit; all PASS:

| INV | Severity | Result |
|-----|----------|--------|
| INV-01 | high   | PASS (ring composition per Table 7.1) |
| INV-02 | high   | PASS (breaking capacity 10 kA ≥ PFC 10 kA both circuits) |
| INV-03 | high   | PASS (Type A 30 mA on all socket-circuit sockets) |
| INV-04 | high   | PASS (Part-7 socket placement — pool hall socket-free + §702.55.4 clipping) |
| INV-05 | high   | PASS (circuit topology + socket→circuit_id refs) |
| INV-06 | low    | PASS (Type B on C01, Type C on C02 motor) |
| INV-07 | high   | PASS (diversified load < breaker rating on every circuit) |
| INV-08 | high   | PASS (Zs deferred to calc tool per WI3) |
| INV-09 | high   | PASS (no orphan rooms; rooms_covered cross-refs valid) |
| INV-10 | low    | PASS (BS 1192 drafting standard matches GB jurisdiction) |
| INV-11 | high   | PASS (no cable-sizing intent consumed — no-op) |
| INV-12 | high   | PASS (4-sub-check §702 cascade walk above) |
| INV-13 | low    | PASS (N/A — building_diversity absent) |
| INV-14 | high   | PASS (C01 ring_endpoints continuity verified, both ends at WAY-1) |
| INV-15 | high   | PASS (N/A — circuit.floor_area_m2 not populated) |
| INV-16 | high   | PASS (C01 ring 20 A ≤32 A; C02 dedicated_radial trivial PASS) |
| INV-17 | medium | PASS (N/A — no fcu_spurs[]) |
| INV-18 | high   | PASS (N/A — no EV-charge circuit) |
| INV-19 | medium | PASS (N/A — no building_diversity AND no cable-sizing intent) |

The IR validates against `electrical/small-power/schemas/small-power-ir.schema.json`
including the `allOf` Part-7 trigger clause AND the v2.0 ring-endpoints allOf clause
(C01 ring has `ring_endpoints` populated). The downstream-facing intent extraction
in `intent-out.json` validates against `small-power-intent.schema.json` and carries
the cascade payload through `consumed_intents.special_locations_zoning` for any
further consumer.
