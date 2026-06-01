# Reasoning — uk-bathroom-whirlpool-with-pump

## Step 0 — Cascade prereq check

Standalone example. No upstream `lighting-layout` intent consumed.
`existing_fixtures` are supplied directly in the input (3 entries).
Skill proceeds in `full_analysis` mode.

## Step 1 — Room classification

`room.room_type = bathroom` → BS 7671:2018 §701 applies. Geometry is
identical to the standard-bath example (2700 × 2100 mm; 5.67 m²;
ceiling 2400 mm; `is_wet_room: false`). The deltas in this example
are concentrated in the bath anchor (`bath_kind`), zone IP ratings,
and the constraint set.

## Step 2 — Anchor inventory

Two anchors, same positions and geometry as the standard-bath example.
**Key delta:** `bath_1.bath_kind = "whirlpool"` (was `standard`).
The input does NOT supply a `whirlpool_pump_position` — this is the
trigger for reviewer D-3.

Both anchors are `architectural_drawing_extraction`. Provenance notes
explicitly disclose that the pump location was NOT shown on the
architectural drawing.

## Step 3 — Zone derivation (same plan, raised IP)

5 zones derived (same topology as the standard-bath case). The
material delta is `ip_rating_min`:

| zone_id              | zone_type   | source_anchor | IPmin (standard) | IPmin (whirlpool) |
|----------------------|-------------|---------------|------------------|-------------------|
| `zone_bath_1_z0`     | bath_zone_0 | bath_1        | IPx7             | IPx7              |
| `zone_bath_1_z1`     | bath_zone_1 | bath_1        | IPx4             | **IPx5**          |
| `zone_shower_1_z1`   | bath_zone_1 | shower_1      | IPx4             | **IPx5**          |
| `zone_bath_1_z2`     | bath_zone_2 | bath_1        | IPx4             | IPx4              |
| `zone_shower_1_z2`   | bath_zone_2 | shower_1      | IPx4             | IPx4              |

The IPx5 lift on Zone 1 is the direct consequence of **BS 7671:2018
§701.512.2** (water jets). Whirlpool jets satisfy the water-jets trigger
even when the bath is a domestic acrylic unit, not a commercial spa.

Zone 2 IPmin remains IPx4 because the jets do not project beyond Zone 1.
Zone 0 stays IPx7 (immersion) per the §701 zone-table convention.

The verified BS 7671:2018+A2:2022 file contains **no §701 sub-clause
specifically for whirlpools** — the IPx5 derivation is routed through
the general §701.512.2 water-jets clause. This is recorded in the
constraint's `_whirlpool_general_citation` field as an honest
disclosure (see Step 11 below).

## Step 4 — Electrical constraint derivation

Two constraints:

1. **`rcd_blanket_by_room`** — per §701.411.3.3.
   - `applies_to_circuit_types[]` explicitly includes `whirlpool_pump`
     so the downstream `db-layout` consumer cannot route it on a
     non-RCD final circuit.
   - `sauna_heater_excluded: false` (heater exemption is §703-only).

2. **`whirlpool_pump_circuit`** — per §701 + §701.512.2.
   - `pump_position_zone: zone_bath_1_z1` — defaulted because input
     did not supply `whirlpool_pump_position`.
   - `requires_local_isolation: true` — needed for safe maintenance
     access without isolating the whole bathroom RCD.
   - `ip_rating_min: IPx5` (const per schema, derived from §701.512.2).
   - `_whirlpool_general_citation: "BS 7671:2018 §701 (no sub-clause
     for whirlpools in verified file) — IPx5 derived from §701.512.2"`
     — honest disclosure that the §701 sub-clause for whirlpools is not
     present in the verified standards file.

The pump constraint binds to `zone_bath_1_z1` via `applies_to_zone_ids`.
The downstream `small-power` consumer reads this binding to enforce
local isolation switch placement.

## Step 5 — Existing-fixture audit

3 fixtures supplied (identical to the standard-bath case). The
whirlpool IPx5 lift does NOT change the fixture compliance outcome
because all 3 fixtures sit outside the whirlpool Zone 1 polygon:

- `lum_1` ceiling-mounted at (1350, 1400, 2400) — outside Zone 1 plan
  polygon (Zone 1 is the bath rectangle (500,0)-(2200,700); fixture is
  at y=1400). Outside Zone 2 (y=1400 > clipped Zone 2 y_max=1300).
- `lum_2` ceiling-mounted at (1050, 350, 2400) — inside Zone 1 plan
  polygon, but at z=2400 mm > Zone 1 height_max=2250 mm. Outside zone.
- `shaver_1` BS EN 61558-2-5 shaver socket at (2400, 1800, 1400) —
  outside Zone 2.

All 3 fixtures `compliance_status: compliant`. The IPx5 lift would
matter only if a future fixture (e.g., a downlight directly above the
whirlpool at z ≤ 2250 mm) were added at IPx4 — INV-08 would then catch
the IP-below-min violation.

## Step 6 — Invariant evaluation (10 INVs)

| INV    | Outcome | Notes                                                                       |
|--------|---------|-----------------------------------------------------------------------------|
| INV-01 | PASS    | 5 zones; overlaps catalogued                                                |
| INV-02 | PASS    | 0 violations on both sides                                                  |
| INV-03 | PASS    | no Group 2 zone (vacuous)                                                   |
| INV-04 | PASS    | rcd_blanket_by_room present with rcd_rating_ma=30                           |
| INV-05 | PASS    | not a pool hall (vacuous)                                                   |
| INV-06 | PASS    | whirlpool_pump_circuit present with IPx5 + isolation per §701 + §701.512.2  |
| INV-07 | PASS    | no ELV anchor (vacuous)                                                     |
| INV-08 | PASS    | 3 fixtures compliant                                                        |
| INV-09 | PASS    | architectural extraction for both anchors                                   |
| INV-10 | PASS    | compliant=true; 0 critical violations; declared overlaps                    |

`calculation_summary.compliant: true`.

## Step 7 — Assumptions recorded

Three assumptions in `calculation_summary.assumptions[]`:

1. **Whirlpool pump position defaulted to bath edge** (zone_bath_1_z1)
   because `whirlpool_pump_position` not supplied — IPx5 per §701.512.2.
2. Bath rim height defaulted to 550 mm AFF.
3. Shower head at 2100 mm AFF treated as Zone 1 ceiling per §701.

## Step 8 — Reviewer D-checks

**D-3 fires** because `bath_kind == whirlpool` AND
`whirlpool_pump_position` was not supplied. The flag is recorded in
`calculation_summary._engineering_judgments[]`:

> REVIEWER D-3: bath_kind=whirlpool with no whirlpool_pump_position
> supplied in input. Skill placed pump at bath edge (zone_bath_1_z1)
> with IPx5 per BS 7671:2018 §701.512.2 water-jets clause.
> Engineer-of-record must confirm actual pump location against
> installer drawing and verify access for maintenance isolation. No
> specific whirlpool sub-clause exists in the verified BS 7671:2018+
> A2:2022 file — IPx5 derivation routed through §701.512.2 (water jets).

Other D-checks evaluated and NOT fired:

- **D-1** — both anchors architectural; no inferred provenance.
- **D-2** — no pool zone.
- **D-4** — no medical IT system constraint.
- **D-5** — `is_external=false`, no ELV anchor.

## Step 9 — Intent payload emission

Emitted `special_locations_zoning` intent contains both constraints,
all 5 zones, and `anchor_source_summary.all_extracted: true`. The
downstream `db-layout` consumer will surface `whirlpool_pump` in its
circuit-allocation audit; the downstream `small-power` consumer will
enforce local isolation switch placement.

## Step 10 — Honest disclosures

1. **No §701 sub-clause for whirlpools exists in the verified BS
   7671:2018+A2:2022 file.** IPx5 derivation is routed through
   §701.512.2 (water jets) — recorded in the constraint's
   `_whirlpool_general_citation` field.
2. **Whirlpool pump position is defaulted.** The skill places the pump
   in `zone_bath_1_z1` because no `whirlpool_pump_position` was
   supplied. Engineer-of-record must verify.
3. **All citations used are on the verified citation table** in spec
   §3.2 (`§701`, `§701.411.3.3`, `§701.414.4.5`, `§701.512.2`,
   `§701.512.3`). No banned §701 sub-clauses appear anywhere.

## Step 11 — Failure modes considered

- If a future luminaire were sited directly above the whirlpool at
  z ≤ 2250 mm with IPx4 (not IPx5), INV-08 sub-rule
  `ip_below_min` would FAIL.
- If `whirlpool_pump_position` were supplied at a position outside the
  bath polygon (e.g., in an under-stair void), the constraint
  `pump_position_zone` would re-bind to whatever zone (if any) contains
  that position. If the pump were in an accessible cupboard outside all
  zones, the IPx5 requirement would relax — but local isolation would
  still apply.
- If the pump IP were under-specified at IPx4 instead of IPx5, INV-06
  would FAIL.

## Step 12 — Compliance verdict

`compliant: true`. The whirlpool variant differs from the standard-bath
case in three respects:

- Zone 1 IP minimum raised IPx4 → IPx5 per §701.512.2.
- Second `electrical_constraints[]` entry: `whirlpool_pump_circuit`.
- Reviewer D-3 flag added to `_engineering_judgments[]`.

All 10 INVs PASS. Existing fixtures unchanged from the standard-bath
case — and still compliant because none of them sit in the IPx5-lifted
zone.
