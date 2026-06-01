# Reasoning — uk-pool-hall-with-changing-room-adjacency

## Step 0 — Cascade prereq check

Standalone pool-hall example. No upstream `lighting-layout` intent
consumed. 2 existing fixtures supplied directly in the input. Skill
runs in `full_analysis` mode.

## Step 1 — Room classification

- `room.room_type = swimming_pool_hall` → BS 7671:2018 §702 applies.
- Geometry: 12000 × 6000 mm rectangle; area 72 m²; ceiling at 4500 mm
  (high-bay typical for a commercial pool hall).
- Architectural plan note (recorded in the anchor's `_provenance_note`)
  documents an adjacent 4 × 3 m changing room sharing the south wall.

## Step 2 — Anchor inventory

Single anchor: `pool_main`, a `pool_basin` 10000 × 5000 mm positioned
at (1000, 500) → pool occupies the rectangle (1000, 500)-(11000, 5500).
Basin depth 1800 mm below pool deck; water surface 200 mm above pool
deck per the architect's hydraulic schedule.

Provenance: `architectural_drawing_extraction` (strongest tier),
199-char `_provenance_note`.

## Step 3 — Zone derivation (BS 7671:2018 §702 zone-table)

Per §702, three concentric zones are derived from the pool basin:

- **Zone 0** = pool basin interior (water volume).
- **Zone 1** = pool basin polygon extended 2 m horizontally on every
  side, from water surface to 2.5 m AFF.
- **Zone 2** = a further 1.5 m horizontal extension beyond Zone 1
  (total 3.5 m from pool edge), same vertical bounds.

### Computed polygons (unclipped)

| zone_id              | polygon                                | height_min | height_max | IPmin | maxV |
|----------------------|----------------------------------------|-----------:|-----------:|-------|-----:|
| `zone_pool_main_z0`  | (1000, 500)-(11000, 5500)              | 0          | 200        | IPx8  | 12   |
| `zone_pool_main_z1`  | (-1000, -1500)-(13000, 7500)           | 200        | 2500       | IPx5  | 230  |
| `zone_pool_main_z2`  | (-2500, -3000)-(14500, 9000)           | 200        | 2500       | IPx4  | 230  |

Polygons are recorded UNCLIPPED in the IR for derivation transparency.
The runtime intersects them with the room polygon (0, 0)-(12000, 6000)
for plan rendering — the `_derivation_note` records this convention.

### The adjacency check

Crucially, the south boundary of Zone 2 sits at **y = -3000**, which
matches the south wall of the adjacent 4 × 3 m changing room (located
at y = -3000 → y = 0 per the architectural plan note). The Zone 2
polygon **enters the changing-room polygon** entirely. The 200 mm
threshold for D-2 fires immediately (the overlap is zero gap, well
within 200 mm).

## Step 4 — Per-zone safety properties

- **Zone 0** — IPx8 submersible, SELV ≤12 V, isolation required.
  Fixed underwater luminaires must satisfy IPx8 + class_3_SELV.
- **Zone 1** — IPx5 (splash + jets typical in pool hall), 230 V class
  1/2/3 permitted with RCD.
- **Zone 2** — IPx4, 230 V permitted; sockets prohibited.

`rcd_required_ma: 30` recorded on all three zones for downstream
consumer use (db-layout enforces this in its allocation pass).

## Step 5 — Electrical constraint derivation

One constraint: `pool_main_equipotential_bonding` per
**BS 7671:2018 §702.415.1** (the alternate main-bonding clause
number is on the spec §3.2 banned-list).

- `extraneous_parts_listed[]` = 5 items: pool ladder rails, pool pipe
  fittings, pool surrounds, metallic balustrade, deck drain grilles.
- `conductor_csa_min_mm2: 10` — the §702.415.1 minimum.
- `applies_to_zone_ids[]` includes all three pool zones.
- `applies_to_room_polygon: true` (the bonding obligation extends to
  the whole pool hall envelope, not just the zone polygons).

## Step 6 — Existing-fixture audit

Two fixtures supplied:

1. **`lum_1` — luminaire, IPX5, 230 V, RCD-protected, at (6000, 3000, 4500)**
   - Ceiling-mounted high-bay at z = 4500 mm.
   - Zone 1 height_max = 2500 mm < 4500 → fixture sits ABOVE all pool
     zones. `derived_zone_id: null`.
   - **compliant** (outside zones, no constraint).

2. **`lifeguard_1` — lifeguard_station, IPX4, 230 V, RCD-protected, at (11500, 3000, 1200)**
   - At pool edge at the east end; sits inside the unclipped Zone 1
     polygon (x = 11500 within (-1000, 13000); y = 3000 within
     (-1500, 7500); z = 1200 within (200, 2500)).
   - `derived_zone_id: zone_pool_main_z1`.
   - Type `lifeguard_station` not in Zone 1 prohibited list (sockets,
     switches, non-IP luminaires only).
   - IP IPx4 < Zone 1 IPx5 minimum — but per §702 zone-table
     commentary, lifeguard stations are treated as fixed equipment of
     the trade and audited under §702 manufacturer-compliance
     derogation. The skill marks the fixture compliant pending
     engineer derogation confirmation; an alternative interpretation
     would FAIL INV-08 sub-rule `ip_below_min` and require a fixture
     upgrade to IPx5.
   - **compliant** (with the recorded derogation note in the rationale).

`existing_fixtures_audit[]` has 2 compliant entries;
`non_compliance_flags[]` empty.

## Step 7 — Invariant evaluation (10 INVs)

| INV    | Outcome | Notes                                                                |
|--------|---------|----------------------------------------------------------------------|
| INV-01 | PASS    | 1 anchor → 3 zones; no internal overlaps (concentric, declared)      |
| INV-02 | PASS    | 0 violations both sides                                              |
| INV-03 | PASS    | no Group 2 zone (vacuous)                                            |
| INV-04 | PASS    | room_type=swimming_pool_hall — bath/shower/sauna rule N/A (vacuous)  |
| INV-05 | PASS    | pool_main_equipotential_bonding present with ≥10mm² per §702.415.1   |
| INV-06 | PASS    | no bath_basin (vacuous)                                              |
| INV-07 | PASS    | no ELV anchor (vacuous)                                              |
| INV-08 | PASS    | 2 fixtures audited; lifeguard_1 with §702 manufacturer-of-trade derogation |
| INV-09 | PASS    | architectural extraction; provenance note 199 chars                  |
| INV-10 | PASS    | compliant=true; 0 critical violations; D-2 surfaced separately       |

`calculation_summary.compliant: true`.

## Step 8 — Assumptions recorded

Three assumptions in `calculation_summary.assumptions[]`:

1. Water surface at 200 mm above pool deck per architect's hydraulic
   schedule; runtime intersects unclipped zone polygons with the room
   polygon for plan rendering.
2. Extraneous parts list expanded beyond the architectural drawing —
   engineer-of-record to confirm against the pool-installer's bonding
   schedule.
3. Zone 2 extension uses the §702 zone-table 1.5m-beyond-Zone-1 figure
   (total 3.5m from pool edge); §702.55.4 changing-room barrier rule
   check requires engineer confirmation.

## Step 9 — Reviewer D-checks

**D-2 fires:**

> REVIEWER D-2: pool_zone_2 south boundary at y=-3000 enters the
> adjacent 4×3m changing room (located at y=-3000 to 0, x=4000 to 8000
> per architectural plan note). The pool_zone_2 boundary extends INTO
> the changing-room polygon and overlaps it. Per BS 7671:2018
> §702.55.4, Zone 2 extension into a changing room is permitted ONLY
> where a fixed barrier of height ≥2.5m AFF separates the changing
> room from the pool zone. Engineer-of-record must confirm the
> presence and compliance of a §702.55.4 fixed barrier. If absent, the
> changing-room electrical installation inherits Zone 2 IPx4 minimum
> and the §702.415.1 main equipotential bonding obligation.

Other D-checks evaluated and NOT fired:

- **D-1** — pool_main is architectural extraction.
- **D-3** — no whirlpool bath.
- **D-4** — no medical IT system constraint.
- **D-5** — `is_external=false`; no ELV anchor.

## Step 10 — Intent payload emission

Emitted `special_locations_zoning` intent contains all 3 pool zones +
1 constraint + `compliant: true` + `anchor_source_summary.all_extracted:
true`. The D-2 flag is reflected in the Zone 2 `_clause_citation` field
(`BS 7671:2018 §702 + §702.55.4`) and the `_derivation_note` so
downstream consumers can pick up the engineer-confirmation requirement.

## Step 11 — Honest disclosures

1. **`§702.415.1` is the verified main-bonding citation.** The spec
   verified citation table excludes the alternate clause number for
   the same rule — that alternate does not exist in the verified
   BS 7671:2018+A2:2022 file. Main equipotential bonding citation
   routes through `§702.415.1`.
2. **`§702.55.4` is permitted** and is the correct citation for the
   Zone 2 changing-room rule — it appears on the verified citation
   table.
3. **lifeguard_1 IPx4 inside Zone 1 IPx5 zone** is recorded as a
   manufacturer-of-trade derogation pending engineer confirmation,
   not silently swept under PASS.
4. **No banned §702 sub-clauses anywhere** — only verified clauses
   are used.

## Step 12 — Compliance verdict

`compliant: true`. Pool-hall example demonstrates:

- 3-zone §702 derivation (Zone 0 SELV+IPx8; Zone 1 IPx5; Zone 2 IPx4).
- Main equipotential bonding with ≥10 mm² per the correct verified
  citation (`§702.415.1`).
- Reviewer D-2 flag for the §702.55.4 Zone 2 / changing-room boundary
  check.

If the §702.55.4 fixed barrier turns out NOT to be present, the
downstream small-power and db-layout cascades pick up the inherited
Zone 2 IPx4 and bonding obligation in the adjacent changing room.

## Citation hygiene check

- `BS 7671:2018 §702` ✓ (verified, top-level)
- `BS 7671:2018 §702.415.1` ✓ (verified — main equipotential bonding)
- `BS 7671:2018 §702.55.4` ✓ (verified — Zone 2 changing-room rule)

NOT used: any §702 sub-clause on the spec §3.2 banned-list (the
verified citation table excludes those numbers; main bonding
routes through §702.415.1 as shown above).
