# Reasoning — uk-sauna-with-3-zone-derivation

## Step 0 — Cascade prereq check

Standalone sauna example. No upstream `lighting-layout` intent
consumed. 2 existing fixtures supplied directly. Skill runs in
`full_analysis` mode.

## Step 1 — Room classification

- `room.room_type = sauna` → BS 7671:2018 §703 applies.
- Geometry: 2400 × 2000 mm cabin; area 4.8 m²; ceiling 2400 mm.
- `is_wet_room: false` (sauna is dry-air, not wet).
- `ambient_temperature_c: 90` (typical sauna operating temperature) —
  this triggers heat-rated-cable assumption and acts as a soft
  cross-check (no D-5 flag because D-5 is external-installation
  specific).
- Floor finish `tiles`.

## Step 2 — Anchor inventory

Single anchor: `heater_1`, a `sauna_heater` 400 × 400 mm × 800 mm tall
electric heater at the NW corner (200, 1600). Provenance:
`architectural_drawing_extraction`, 169-char `_provenance_note`
recording the 6 kW heater rating and corner placement.

## Step 3 — Zone derivation (BS 7671:2018 §703 3-zone split)

This is the key example showing the §703 3-zone derivation. Per the
§703 zone-table (verified in spec §3.2):

- **Zone 1** around the heater (footprint + 500 mm padding).
- **Zone 2** = the sauna body (cabin polygon minus Zone 1).
- **Zone 3** = full cabin polygon at height_min = 1500 mm to ceiling
  (the upper-volume zone).

### Computed polygons

Heater footprint (200, 1600)-(600, 2000). Padded 500 mm on every side:
unclipped polygon (-300, 1100)-(1100, 2500). Clipped to room polygon
(0, 0)-(2400, 2000) → final Zone 1 polygon **(0, 1100)-(1100, 2000)**.

| zone_id              | zone_type     | polygon                    | height_min | height_max | IPmin | rcd  |
|----------------------|---------------|----------------------------|-----------:|-----------:|-------|------|
| `zone_heater_1_z1`   | sauna_zone_1  | (0,1100)-(1100,2000)       | 0          | 2400       | IPx4  | null |
| `zone_heater_1_z2`   | sauna_zone_2  | (0,0)-(2400,2000) full     | 0          | 2400       | IPx4  | 30   |
| `zone_heater_1_z3`   | sauna_zone_3  | (0,0)-(2400,2000) full     | 1500       | 2400       | IPx4  | 30   |

`rcd_required_ma: null` on Zone 1 records the heater-circuit exemption
per §703.411.3.3 — the heater circuit is EXCLUDED from the 30 mA RCD
blanket because tripping the heater on a thermal-pulse residual current
would defeat the heating function. Fault protection is provided by the
dedicated heater controller instead.

### Overlap declarations

- `zone_heater_1_z1.overlapping_with_zone_ids: ["zone_heater_1_z2"]`
  — Zone 2 polygon as written includes the Zone 1 region; the runtime
  subtracts for plan rendering. Overlap declared to keep INV-01
  catalogue intact.
- `zone_heater_1_z2.overlapping_with_zone_ids: ["zone_heater_1_z1", "zone_heater_1_z3"]`
- `zone_heater_1_z3.overlapping_with_zone_ids: ["zone_heater_1_z2"]`
  — Zone 3 polygon coincides with Zone 2 in plan but is separated
  vertically (height_min ≥ 1500 mm). Overlap declared.

## Step 4 — Per-zone safety properties

- **Zone 1** (heater zone) — IPx4 minimum; 230 V class_1/2 with heat-
  rated cable. `rcd_required_ma: null` (heater exemption).
  `isolation_required: true` for the heater circuit. Prohibited
  fixtures include `non_heat_rated_cable_load`.
- **Zone 2** (sauna body) — IPx4 minimum; 230 V; 30 mA RCD; isolation
  optional. Heat-rated cable required.
- **Zone 3** (upper volume) — IPx4 minimum; 230 V; 30 mA RCD. Cooler
  vertical band (heat rises) but still inside the sauna envelope —
  heat-rated cable still required for cables passing through.

## Step 5 — Electrical constraint derivation

One constraint: `rcd_blanket_by_room` per **§703.411.3.3** — with
**`sauna_heater_excluded: true`**.

- `applies_to_room_polygon: true`.
- `rcd_rating_ma: 30`.
- `applies_to_circuit_types: ["lighting", "sockets", "control_gear",
  "thermostat", "extract_fan"]` — the heater circuit is intentionally
  NOT in this list.
- `sauna_heater_excluded: true` — the §703-specific carve-out.

## Step 6 — Existing-fixture audit

Two fixtures supplied:

1. **`lum_1` — sauna_luminaire, IPX4, 230 V, RCD-protected, at (1200, 1000, 2400)**
   - Ceiling-mounted at z = 2400 mm = top of Zone 3 (height_max =
     2400; the top edge is inclusive). Plan position (1200, 1000)
     sits inside Zone 3 polygon (the full room).
   - `derived_zone_id: zone_heater_1_z3` (chosen over Zone 2 because
     z=2400 ≥ 1500 places it in the upper-volume zone).
   - Type `sauna_luminaire` not in Zone 3 prohibited list; IPx4 ≥ IPx4
     min; voltage 230 V ≤ 230 V; not a switch.
   - **compliant**.

2. **`thermostat_1` — thermostat_sensor, IPX4, 230 V, RCD-protected, at (1800, 1800, 1600)**
   - Wall-mounted thermostat sensor at z=1600 mm (≥1500 mm) → sits in
     Zone 3.
   - `derived_zone_id: zone_heater_1_z3`.
   - Type allowed; IPx4 ≥ IPx4 min; voltage 230 V ≤ 230 V; not a
     switch.
   - **compliant**.

Both compliant. `non_compliance_flags[]` empty.

## Step 7 — Invariant evaluation (10 INVs)

| INV    | Outcome | Notes                                                                |
|--------|---------|----------------------------------------------------------------------|
| INV-01 | PASS    | 1 anchor → 3 zones; overlaps catalogued                              |
| INV-02 | PASS    | 0 violations both sides                                              |
| INV-03 | PASS    | no Group 2 zone (vacuous)                                            |
| INV-04 | PASS    | rcd_blanket_by_room with rcd_rating_ma=30 + sauna_heater_excluded=true |
| INV-05 | PASS    | not a pool hall (vacuous)                                            |
| INV-06 | PASS    | no bath_basin (vacuous)                                              |
| INV-07 | PASS    | no ELV anchor (vacuous)                                              |
| INV-08 | PASS    | 2 fixtures compliant                                                 |
| INV-09 | PASS    | architectural extraction; provenance 169 chars                       |
| INV-10 | PASS    | compliant=true; declared overlaps; 0 critical                        |

`calculation_summary.compliant: true`.

## Step 8 — Assumptions recorded

Three assumptions in `calculation_summary.assumptions[]`:

1. Sauna heater Zone 1 padding defaulted to 500 mm per §703
   zone-table convention.
2. Heat-rated cable assumed for all circuits inside the sauna cabin
   (ambient_temperature_c = 90°C per input).
3. Zone 2 polygon shown as full room rectangle in IR; runtime
   subtracts Zone 1 footprint for plan rendering — overlap with
   Zone 1 declared accordingly.

## Step 9 — Reviewer D-checks

No D-checks fire:

- **D-1** — heater_1 is architectural extraction.
- **D-2** — not a pool zone.
- **D-3** — no whirlpool bath.
- **D-4** — no medical IT system constraint.
- **D-5** — `is_external=false`; no ELV anchor. (Sauna ambient
  temperature is captured in `room.ambient_temperature_c` and used
  in the heat-rated-cable assumption — D-5 specifically targets the
  external+ELV combination.)

`_engineering_judgments: []`.

## Step 10 — Honest disclosures (this example)

1. **Heater exemption from RCD blanket is the §703-specific carve-out.**
   Setting `sauna_heater_excluded: true` correctly preserves the
   §703.411.3.3 clause body exemption — and the schema declares this
   field explicitly to make the exemption auditable.
2. **500 mm padding is a §703 zone-table engineering convention.**
   The verified BS 7671:2018+A2:2022 file does not give a numeric
   value for the heater padding — the 500 mm figure is recorded as
   an assumption.
3. **Zone 2 polygon shown as the full room rectangle** for derivation
   transparency. The runtime subtracts Zone 1 for plan rendering, and
   the overlap is declared via `overlapping_with_zone_ids[]` so the
   catalogue is not silently incomplete.
4. **No banned §703 sub-clauses used.** Only verified `§703` +
   `§703.411.3.3` per the spec §3.2 verified table.

## Step 11 — Intent payload emission

Emitted `special_locations_zoning` intent contains all 3 sauna zones +
1 constraint + `compliant: true` + `anchor_source_summary.all_extracted:
true`. The sauna_heater_excluded flag on the constraint is preserved
so the downstream `db-layout` consumer knows to allocate the heater
circuit OUTSIDE the RCD blanket.

## Step 12 — Compliance verdict

`compliant: true`. The 3-zone sauna split is the canonical §703
derivation:

- Zone 1 around heater (heat-rated, isolation-required, RCD-exempt).
- Zone 2 cabin body (heat-rated, RCD-protected).
- Zone 3 upper volume (cooler, but still IPx4 + heat-rated).

The sauna_heater_excluded=true carve-out is the key §703 sub-rule
exercised. INV-04 PASSES specifically because BOTH conditions hold:
rcd_rating_ma=30 AND sauna_heater_excluded=true.

## Citation hygiene check

- `BS 7671:2018 §703` ✓ (verified, top-level)
- `BS 7671:2018 §703.411.3.3` ✓ (verified)

NOT used: any §703 sub-clause on the spec §3.2 banned-list (the
verified citation table excludes those numbers).
