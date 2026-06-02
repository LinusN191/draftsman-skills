# Reasoning — cascade-db-layout-uk-bathroom-rcd-enforcement

## Cascade context

Cascade retrofit of C.1 standalone
`uk-bathroom-standard-bath-and-shower` for the **db-layout consumer**.
Upstream db-layout intent (synthetic at
`electrical/db-layout/examples/uk-bathroom-cascade-source/intent-out.json`)
models the bathroom-serving circuit catalogue, with **every circuit
routed through a 30 mA RCD** per BS 7671:2018 §701.411.3.3.

The zones, constraints, and 3 existing fixtures (2 luminaires + 1
shaver socket) are identical to the C.1 source. The cascade
demonstrates **db-layout INV-16 sub-check 3** (`rcd_blanket_by_room`
enforcement).

## Step 0 — Cascade prereq check

- `_special_locations_cascade_source.upstream_consumer_intent_location` set
  → `full_analysis` mode.
- `existing_fixtures[]` carry `_consumed_from` markers recording the
  upstream db-layout circuit's protective device type
  (`RCBO_30mA`).
- `consumed_lighting_layout_intent` in intent-out points at the
  upstream db-layout intent path (single field; consumer skill recorded
  via `_special_locations_cascade_source.consumer_skill: db-layout`).

## Step 1 — Room classification

Identical to C.1 source: bathroom; 2 700 × 2 100 mm; ceiling 2 400 mm;
`is_wet_room: false`.

## Step 2 — Anchor inventory

Identical to C.1 source: `bath_1` (1 700 × 700 × 550 mm) + `shower_1`
(head at 2 100 mm AFF). Both `_extraction_source:
architectural_drawing_extraction`.

## Step 3 — Zone derivation (BS 7671:2018 §701 zone-table)

5 zones (same as C.1):

| zone_id              | zone_type   | source_anchor | height_min | height_max | IPmin | maxV |
|----------------------|-------------|---------------|-----------:|-----------:|-------|-----:|
| `zone_bath_1_z0`     | bath_zone_0 | bath_1        | 0          | 550        | IPx7  | 12   |
| `zone_bath_1_z1`     | bath_zone_1 | bath_1        | 550        | 2250       | IPx4  | 230  |
| `zone_shower_1_z1`   | bath_zone_1 | shower_1      | 0          | 2100       | IPx4  | 230  |
| `zone_bath_1_z2`     | bath_zone_2 | bath_1        | 0          | 2250       | IPx4  | 230  |
| `zone_shower_1_z2`   | bath_zone_2 | shower_1      | 0          | 2100       | IPx4  | 230  |

## Step 4 — Electrical constraint derivation

Single constraint: `rcd_blanket_by_room` per **§701.411.3.3**.

This is the **engineering payload** of this cascade for db-layout INV-16
sub-check 3.

## Step 5 — Consume db-layout intent

3 fixtures consumed; each `_consumed_from` records the upstream
db-layout circuit's protective device type as `RCBO_30mA`:

| fixture_id | type            | upstream protective device |
|------------|-----------------|----------------------------|
| `lum_1`    | luminaire       | RCBO_30mA                  |
| `lum_2`    | luminaire       | RCBO_30mA                  |
| `shaver_1` | shaver_socket   | RCBO_30mA                  |

## Step 6 — INV-08 sub-rule walk-through

Identical to cascade #9 (`cascade-lighting-layout-uk-bathroom`).
12 sub-rule evaluations (3 fixtures × 4 sub-rules) all PASS. All 3
fixtures sit OUTSIDE the §701 zone polygons in plan or above max-height;
`derived_zone_id: null` for all 3.

## Step 7 — Consumer-side hand-off — db-layout INV-16 sub-check 3 (the cascade core)

db-layout v1.5 INV-16 sub-check 3 (`rcd_blanket_by_room` enforcement)
iterates over every circuit in the db-layout output IR whose final load
is inside the bathroom polygon. For each circuit, it verifies:

`upstream_protective_device.type ∈ {RCD_30mA, RCBO_30mA_combined_protection}`

For this cascade, db-layout's synthetic upstream intent models:

| circuit_id           | load             | upstream device              |
|----------------------|------------------|------------------------------|
| `bathroom_lighting`  | lum_1 + lum_2    | RCBO_B6 with 30 mA RCD       |
| `bathroom_shaver`    | shaver_1         | RCBO_B6 with 30 mA RCD       |
| `bathroom_fan_rsv`   | (reserved)       | RCBO_B6 with 30 mA RCD       |

Every circuit routes through a 30 mA RCD-element. **INV-16 sub-check 3
PASSes.**

## Step 8 — Invariants

All 10 INVs PASS. The notable change vs cascade #9 is INV-04's evidence
explicitly calls out the downstream INV-16 sub-check 3 trigger.

- **INV-01** zone catalogue: 2 anchors → 5 zones with declared overlaps.
  PASS.
- **INV-02** audit ↔ flags 1:1. PASS.
- **INV-03** medical IT N/A. PASS vacuously.
- **INV-04** `rcd_blanket_by_room` PRESENT (rcd_rating_ma=30,
  sauna_heater_excluded=false). DRIVES db-layout INV-16 sub-check 3.
  PASS.
- **INV-05** main equipotential bonding N/A. PASS vacuously.
- **INV-06** whirlpool pump N/A. PASS vacuously.
- **INV-07** ELV separation N/A. PASS vacuously.
- **INV-08** 12/12 sub-rule evaluations PASS.
- **INV-09** anchor provenance strongest tier. PASS.
- **INV-10** rollup self-consistency holds. PASS.

## Step 9 — Honest disclosures

- **Synthetic upstream db-layout intent.** v1.5 hand-off contract not
  yet shipped. Cascade contract integrity verified via golden CI Pass 4
  (intent-out validation against special-locations-zoning-intent
  schema), NOT runtime consumption.
- **Bathroom polygon coverage.** The rcd_blanket_by_room constraint
  applies to all bathroom polygon circuits — including circuits whose
  load is outside the §701 zones but inside the room (e.g., bathroom
  fan, towel rail, mirror demist heater).
- **sauna_heater_excluded=false.** This is a bathroom, not a sauna; the
  §703 sauna heater exemption from rcd_blanket does NOT apply.

## Step 10 — Failure modes considered

If db-layout's upstream intent modelled a `bathroom_lighting` circuit
protected by an `MCB_B6` (no RCD element) instead of `RCBO_B6 with 30 mA
RCD`, INV-16 sub-check 3 would FAIL HIGH with severity=critical and
clause = `BS 7671:2018 §701.411.3.3`. The non_compliance_flag would
carry `_cascaded_from: special-locations` (this skill is the
authoritative side for the RCD-blanket rule).

If the supply DB is a TT-earthing-system installation (e.g., rural
property with no PEN), the upstream MAIN incoming RCD typically provides
the §701.411.3.3 blanket; db-layout INV-16 sub-check 3 must trace
back to ANY 30 mA RCD between the load and the supply origin, not
strictly the immediate-upstream device. This cascade's example does
NOT model this case (the standalone source is a typical TN-S installation).

## Step 11 — db-layout integration notes

The db-layout consumer side will surface this cascade's verdict in
several places downstream of INV-16 sub-check 3:

1. **Board schedule output.** Each bathroom-serving circuit's row in
   the BOQ-ready board schedule should annotate the protective device
   as `RCBO_B6 (BS EN 61009-1) with 30 mA RCD-element per §701.411.3.3`.
   The clause text is sourced from the special-locations intent
   `electrical_constraints[0]._clause_citation` field.
2. **Cable schedule.** The bathroom-serving circuit's source-side cable
   schedule entry should record the RCD type (Type-A minimum for
   electronic loads; Type-AC permitted for resistive-only loads in a
   simple bathroom). This level of detail is db-layout's responsibility,
   not special-locations' — the cascade only enforces the 30 mA RCD
   presence.
3. **Diversity factor.** The bathroom polygon's circuits are typically
   small-load (≤6 A for lighting; ≤16 A for shaver and fan); diversity
   is normally not applied at the bathroom level. db-layout's diversity
   computation should NOT compress these circuits' protective device
   ratings on diversity grounds.

## Step 12 — Test plan for downstream consumer

When db-layout v1.5 is shipped with INV-16 sub-check 3 wired up, the
cascade integration test should:

1. Consume this special-locations intent (intent-out.json).
2. Generate a db-layout output IR with at least 3 bathroom-serving
   circuits (lighting, shaver-socket, reserved fan).
3. Verify each circuit's upstream protective device type ∈
   {RCD_30mA, RCBO_30mA_combined_protection}.
4. Verify the cascade integrity check passes: the rcd_blanket_by_room
   constraint's clause citation matches the per-circuit protective
   device clause citation (both BS 7671:2018 §701.411.3.3).
5. Verify the special-locations intent's `non_compliance_flags=[]`
   propagates as db-layout's `non_compliance_flags=[]` for these
   circuits.

## Cross-references

- C.1 source: `electrical/special-locations/examples/uk-bathroom-standard-bath-and-shower/`
- Spec §9.2 cascade row 15: PASS case
- Plan portion 3 Task C.2 Step 6
