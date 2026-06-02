# UK Bathroom — Shaver Supply with Adjacent Hall Ring (small-power Part-7 cascade exercise)

## Why this example exists

Sprint D.4's binding condition: the small-power skill ships INV-12 (special-locations cascade
resolution) at v1.2, but every pre-existing small-power example uses `room_type =
"bathroom_domestic"` for the wet room — which is **not** in the Part-7 enum trigger set
`{bathroom, shower_room, swimming_pool_hall, sauna, medical_group_0_area,
medical_group_1_ward, medical_group_2_theatre, external_landscape}`. The result was that
INV-12 was wired but never actually fired on any shipped example. This example fixes that
by using the exact literal `room_type = "bathroom"` so:

- the schema's `allOf` clause requiring `consumed_intents.special_locations_zoning` is
  forced to evaluate,
- the validator's INV-12 condition triggers,
- the 4 sub-checks run end-to-end against a real cascade payload, and
- the example's `invariants[]` records `INV-12 passes: true` with concrete evidence.

This is the small-power mirror of the D.2 lighting-layout work: ADD a Part-7 exact-match
example rather than retrofit existing ones.

## Room context — UK domestic bathroom

A 2.7 m × 2.1 m × 2.4 m UK domestic bathroom containing:

- a single bath (footprint 500–2200 mm × 0–700 mm in room-local coordinates, rim at 550
  mm AFFL), and
- an overhead shower head at 2100 mm AFFL above the bath polygon.

Adjacent to the bathroom (shared wall to the south) is a 3.0 m × 1.5 m hall. The hall is
not a Part-7 location and only participates in this example to give the IR a credible
second circuit (a small 32 A ring) — small-power IRs with a single dedicated radial would
still validate but would not exercise the multi-circuit RCD-posture invariants.

## Cascade prerequisite — what special-locations told us

`consumed_intents.special_locations_zoning.payload` carries the full upstream contract:

- **5 zones** derived from the two anchors (`bath_1`, `shower_1`):
  1. `zone_bath_1_z0` — Zone 0, the bath interior volume, height 0–550 mm, SELV-only.
  2. `zone_bath_1_z1` — Zone 1 above the bath polygon, 550–2250 mm AFF.
  3. `zone_shower_1_z1` — Zone 1 around the shower head, 0–2100 mm AFF.
  4. `zone_bath_1_z2` — Zone 2, the 600 mm horizontal extension of bath Zone 1,
     0–2250 mm AFF, polygon `[-100, -600] → [2800, 1300]`.
  5. `zone_shower_1_z2` — Zone 2 around the shower, 0–2100 mm.
- **1 electrical constraint**: `rcd_blanket_by_room`, `rcd_rating_ma = 30`, applies to
  `[lighting, sockets, shower_unit, fixed_equipment, shaver_socket]` per
  BS 7671:2018+A2:2022 §701.411.3.3.
- `compliant = true`, `non_compliance_flags = []`.

The cascade source path is:
`electrical/special-locations/examples/cascade-lighting-layout-uk-bathroom/intent-out.json`.

That cascade was authored by the lighting-layout consumer. Since special-locations IR is
anchor-driven (zones come from `bath_1 + shower_1` geometry, not from luminaire-vs-socket
intent), the same payload is engineering-equivalent for the small-power consumer. The
honest disclosure: a small-power-specific `cascade-small-power-uk-bathroom-pass` does
not exist at v1.0; a future Wave 2 sprint will backfill it on the special-locations side
once the small-power-bathroom anchor variant is needed by another downstream skill.

## Socket placement decisions

The design ships zero 230 V general-purpose sockets inside any §701 zone. There are
exactly three sockets in the IR:

1. `bathroom-S01`: `BS_EN_61558_2_5_shaver_supply_unit`, mounted on the south wall at
   1400 mm AFFL. In room-local coordinates this falls outside the bath_1 + shower_1 Zone
   0/1 footprints (which span 500..2200 × 0..700 mm). It does fall inside Zone 2's
   horizontal envelope `[-100, -600] → [2800, 1300]`, but Zone 2's
   `prohibited_fixture_types` is `[socket_230v]` only — BS EN 61558-2-5 shaver supplies
   are explicitly excluded from that list. The shaver supply's secondary side provides
   electrical separation per BS 7671:2018+A2:2022 §413.
2. `hall-S01` and `hall-S02`: `BS_1363_double_switched_13A` on the hall ring. Both sit
   outside the bathroom room polygon entirely (and therefore outside every §701 zone in
   the payload — the zones are bounded by the bathroom room polygon at the upstream
   special-locations stage).

The §701.512.3 3 m boundary rule (no socket outlet within 3 m of Zone 1) is trivially
satisfied because no general-purpose 230 V socket is placed inside the bathroom at all.
The shaver supply is a §701.512.3 explicit exception.

## Circuit topology + RCD posture

Two circuits:

- `C01` — Hall ring final circuit. 32 A Type B RCBO + 2.5 mm² + 1.5 mm² CPC PVC T+E ring,
  14 m total run. Diversified load 4.5 A (well inside the 32 A breaker rating).
  Type A 30 mA RCD per BS 7671:2018+A2:2022 §411.3.3 default for sockets ≤32 A.
- `C02` — Bathroom shaver supply dedicated radial. 6 A Type B RCBO + 1.5 mm² T+E, 4 m
  run. Diversified load 2.2 A. Type A 30 mA RCD per the cascaded §701.411.3.3 blanket
  constraint.

Even though C01 (the hall ring) does not serve any fixture inside the bathroom room
polygon, it is on 30 mA already by the §411.3.3 default. The cascaded blanket constraint
is therefore satisfied without imposing any additional design change on the hall ring.

## INV-12 cascade evidence (4 sub-checks walked)

The validator's INV-12 evidence string (≤800 chars per IR schema cap):

> Cascade source: electrical/special-locations/examples/cascade-lighting-layout-uk-bathroom/intent-out.json.
> Sub-check 1 PASS (consumed_intents.special_locations_zoning present).
> Sub-check 2 PASS (payload.compliant=true, 5 zones, 1 rcd_blanket constraint, 0 flags).
> Sub-check 3 PASS — walked sockets: bathroom-S01 (BS_EN_61558_2_5_shaver_supply_unit,
>   1400 mm AFFL) sits in Zone 2 vertical envelope but BS EN 61558-2-5 is NOT in
>   bath_zone_2.prohibited_fixture_types (which lists only socket_230v); hall-S01,
>   hall-S02 are outside the bathroom polygon.
> Sub-check 4 PASS — payload.non_compliance_flags[]=[]; nothing to cascade so no
>   _cascaded_from attribution required. BS 7671:2018+A2:2022 §701.411.3.3 + §701.512.3.

Walking each sub-check explicitly:

1. **Sub-check 1 — cascade present.** `consumed_intents.special_locations_zoning.payload`
   is populated with `intent_version=1.0.0`, a valid `source_path`, and the full payload
   object. The schema's `allOf` clause is therefore satisfied for the
   `room_type=bathroom` trigger.
2. **Sub-check 2 — upstream compliant.** `payload.compliant == true`. No upstream INV
   failed. The 5 zones are coherent; the rcd_blanket_by_room constraint is well-formed.
3. **Sub-check 3 — socket/isolator/connection_point cross-walk.** The small-power IR
   schema only carries `sockets[]` inside rooms (no `isolators[]`, no
   `connection_points[]`), so the cross-walk reduces to three sockets:
   - `bathroom-S01`: type literal `BS_EN_61558_2_5_shaver_supply_unit`. Falls in
     `zone_bath_1_z2` vertical envelope (0..2250 mm includes 1400). The zone's
     `prohibited_fixture_types = ["socket_230v"]` — the shaver supply is not a
     `socket_230v` (the type literal is distinct). PASS.
   - `hall-S01`, `hall-S02`: BS 1363 13 A sockets in the hall room. Hall is outside the
     bathroom room polygon and therefore outside every payload zone (zones are bounded
     by the bathroom room). PASS.
4. **Sub-check 4 — flag cascading.** `payload.non_compliance_flags[]` is empty. There
   is nothing to cascade, so the rule "every payload flag must appear in
   `compliance_summary.non_compliance_flags[]` with `_cascaded_from: special-locations`
   attribution" is trivially satisfied. The `compliance_summary.non_compliance_flags[]`
   that is present in this IR contains only `severity: info` design notes — not
   cascaded failures — and the small-power IR schema's strict
   `additionalProperties: false` on flag items would in any case reject a literal
   `_cascaded_from` field. The convention used when there IS something to cascade
   (e.g. the C.2 FAIL companion `cascade-small-power-uk-bathroom-violation`) is to
   prefix the flag message text with `Cascaded from special-locations:` — see the
   second info flag in `compliance_summary.non_compliance_flags[]` for the in-text
   pattern; in the PASS path this attribution is informational only.

All four sub-checks resolve PASS. INV-12's IR record carries
`{id: "INV-12", passes: true, severity: "high", evidence: "..."}`.

## Honest disclosures

- **Cascade source reuse**: the payload was authored against the lighting-layout
  bathroom consumer. Anchor geometry and zone derivations are identical for the
  small-power case (bath_1, shower_1, the same room polygon), and the
  `rcd_blanket_by_room` constraint covers the small-power circuit types
  `[lighting, sockets, shower_unit, fixed_equipment, shaver_socket]` explicitly — the
  shaver and the sockets are both already listed. There is no engineering risk to
  this reuse; the limitation is bookkeeping (no dedicated
  `cascade-small-power-uk-bathroom-pass` exists on the special-locations producer side
  at v1.0). A Wave 2 sprint should backfill the producer-side example for symmetry
  with the FAIL companion.
- **Room scope**: only the bathroom and a small adjacent hall are modelled. A real
  dwelling would carry many more rooms (kitchen, lounge, bedrooms, utility); they are
  intentionally omitted from this example because the engineering point is the
  cascade exercise, not a complete dwelling design. The existing `uk-3bed-dwelling`
  example carries the complete-dwelling shape.
- **Zs deferred**: both circuits carry `tool_call_pending_for_zs_verification = true`
  and the IR's `flags[]` records `TOOL-CALL-PENDING:calc.zs_loop_impedance` per the
  standard WI3 deferred tool-call pattern.

## Standards cited

- BS 7671:2018+A2:2022 §411.3.3 — additional protection for socket outlets ≤32 A in
  domestic premises (Type A 30 mA RCD default).
- BS 7671:2018+A2:2022 §411.4.5 — earth fault loop impedance limits (Zs).
- BS 7671:2018+A2:2022 §413 — protection by electrical separation (shaver supply
  isolating transformer).
- BS 7671:2018+A2:2022 §433.1.5 — final-circuit overload protection (ring final
  circuits permitted in GB).
- BS 7671:2018+A2:2022 §434.5.1 — breaking capacity of OCPDs ≥ prospective fault
  current.
- BS 7671:2018+A2:2022 §701.411.3.3 — 30 mA RCD blanket for low-voltage circuits
  serving locations containing a bath or shower (the cascaded constraint).
- BS 7671:2018+A2:2022 §701.512.3 — socket outlet placement in §701 locations
  (≥3 m from Zone 1 boundary; shaver supply per BS EN 61558-2-5 is an explicit
  exception).
- BS 7671:2018+A2:2022 Table 7.1 — standard ring final circuit cable composition.
- BS EN 60898-1 — circuit breakers for overcurrent protection (curve B selection
  for domestic loads with no significant inrush).
- BS EN 61558-2-5 — particular requirements and tests for safety-isolating
  transformers for shavers, used in this example for the bathroom shaver supply unit.
- BS 1192:2007+A2:2016 — drawing-management conventions (sheet size A3, scale 1:50,
  layer naming).
- IET On-Site Guide §8.4.4 — ring final circuit floor area recommendation (100 m²
  per 32 A ring).
- IET On-Site Guide Appendix A — diversity factors for general lighting and socket
  circuits.

## Validator outcome

All 12 INVs PASS:

| INV | Severity | Result |
|-----|----------|--------|
| INV-01 | high | PASS (ring composition per Table 7.1) |
| INV-02 | high | PASS (breaking capacity 6 kA ≥ PFC 6 kA) |
| INV-03 | high | PASS (Type A 30 mA on all socket circuits) |
| INV-04 | high | PASS (Part-7 socket placement check) |
| INV-05 | high | PASS (circuit topology + socket→circuit_id refs) |
| INV-06 | low  | PASS (Type B curve — no inrush justification needed) |
| INV-07 | high | PASS (diversified load < breaker rating on every circuit) |
| INV-08 | high | PASS (Zs deferred to calc tool per WI3) |
| INV-09 | high | PASS (no orphan rooms; rooms_covered cross-refs valid) |
| INV-10 | low  | PASS (BS 1192 drafting standard matches GB jurisdiction) |
| INV-11 | high | PASS (no cable-sizing intent consumed — no-op) |
| INV-12 | high | PASS (4-sub-check cascade walk above) |

The IR validates against `electrical/small-power/schemas/small-power-ir.schema.json`
including the `allOf` Part-7 trigger clause. The downstream-facing intent extraction
in `intent-out.json` validates against `small-power-intent.schema.json` and carries
the cascade payload through `consumed_intents.special_locations_zoning` for any
further consumer.
