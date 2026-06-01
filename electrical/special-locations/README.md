# special-locations — DraftsMan MEP Engineering Skill

**Path:** `electrical/special-locations/`
**Status:** production (v1.0.0)
**Discipline:** electrical / compliance
**Role:** calc-primitive companion (emits intent + IR; does NOT produce a primary drawing)
**Standards:** BS 7671:2018+A2:2022 Part 7 §701 + §702 + §703 + §710 + §715; HTM 06-01; BS EN 60601 series; BS EN 61557-8; BS EN 61558-2-6; BS 5266-1

## What this skill does

Auto-derives BS 7671:2018+A2:2022 Part 7 zoning and electrical constraints from upstream
architectural-extracted anchor fixtures. Given the room geometry and anchor points (bath edge,
pool surround, sauna heater, medical zone boundary, ELV luminaire positions), the skill
computes the exact regulatory zone layout for each Part 7 location type:

- **§701 Bathrooms and shower rooms** — Zones 0/1/2 derived from bath/shower tray boundaries.
  Constraint set: SELV ≤12 V in Zone 0 (§701.414.4.5); 30 mA RCD blanket (§701.411.3.3);
  supplementary equipotential bonding (§701.415.2); socket outlets ≥3 m from Zone 1
  (§701.512.3); IPx5 where water jets used (§701.512.2).
- **§702 Swimming pools** — Zones A/B/C/D from pool surround + diving platform + water jet.
  Constraint set: main equipotential bonding (§702.415.1); supplementary bonding (§702.415.2);
  Zone 2 changing-room overlap handling (§702.55.4).
- **§703 Saunas** — 3-zone split (heater, 0.5 m belt, remainder) from heater anchor.
  Constraint set: RCD blanket (§703.411.3.3) with heater exempt per clause body.
- **§710 Medical locations** — Group 0/1/2 classification + medical IT system requirements.
  Constraint set: IMD 8 s alarm response per BS EN 61557-8; NHS safety service categories
  per HTM 06-01 (takes precedence on NHS sites); BS EN 60601 cross-reference for equipment.
- **§715 Extra-low voltage lighting** — ELV zone derivation for external/landscape lighting.
  Constraint set: transformer short-circuit protection per BS EN 61558-2-6.

The skill does NOT render a drawing. It emits a `special-locations-zoning` intent consumed
by three downstream skills that enforce per-zone fixture-placement compliance at draw time.

## Cascade contract

**Produces:** `special-locations-zoning` v1.0.0 intent — consumed by:
- `electrical/lighting-layout/` v1.6 (enforce zone-restricted luminaire placement; IP rating
  per zone; SELV ≤12 V in Zone 0; ELV transformer spec for §715)
- `electrical/small-power/` v1.2 (enforce socket-outlet exclusion zones; isolation distances;
  §702 bonding socket suppression; §715 ELV circuit separation)
- `electrical/db-layout/` v1.5 (enforce 30 mA RCD allocation per §701/§702/§703 zone;
  medical IT system distribution board for §710 Group 2; ELV transformer circuit in §715)

**Consumes:** `lighting-layout` v^1.5 intent — trigger fires when
`room.room_type` ∈ Part 7 set (bathroom, shower_room, swimming_pool_hall, sauna,
medical_group_0_area, medical_group_1_ward, medical_group_2_theatre, external_landscape).

## Inputs (per `inputs.json`)

**Required:**
- `anchor_fixtures[]` — list of anchor points extracted from architectural drawings (bath
  edge coordinates, pool surround polygon, sauna heater position, zone-boundary polylines,
  ELV luminaire positions). Each entry carries `anchor_type`, `coordinates_mm`, and
  `room_reference_id`.
- `room` — room descriptor: `room_type`, `floor_area_m2`, `ceiling_height_mm`,
  `jurisdiction` (GB / KE / INT), `site_type` (domestic / commercial / NHS / other).

**Optional:**
- `water_jet_present` (boolean) — when `true`, triggers §701.512.2 IPx5 requirement for
  whirlpool/spa baths and upgrades the zone-constraint set.
- `medical_group_override` (0 / 1 / 2) — override auto-derived medical group when the
  architectural drawings already carry Group classification.
- `it_system_present` (boolean) — explicit flag for medical IT system (§710); auto-derived
  from Group 2 classification if not supplied.
- `nhs_site` (boolean) — when `true`, HTM 06-01 NHS safety-service-category rules take
  precedence over BS 7671 §710 defaults.

## Outputs

**IR (`special-locations-ir`):**
- `zone_layout[]` — per-room zone polygons with `zone_id`, `regulation_ref`, `constraint_set[]`
- `constraint_summary` — aggregated constraint list with `clause_citation`, `severity`
  (MANDATORY / ADVISORY), `enforcement_target` (lighting / small_power / distribution_board)
- `bonding_requirements` — supplementary and main bonding schedule (feeds bonding-schedule
  document skill)
- `non_compliance_flags[]` — pre-populated if input anchor data reveals a prospective
  violation before downstream layout is generated
- `rationale` — embedded rationale block (chat_summary + sections[])
- `provenance` — standards version + verification_status

**Intent (`special-locations-zoning`):**
- Flat payload consumed by downstream skills; carries `zones[]` with constraint_sets and
  `jurisdiction` field for KE §313 routing.

## Validator (10 INVs)

HIGH severity:
- **INV-01** Zone geometry completeness — all anchor_fixtures[] have produced a closed zone
  polygon; no unbounded or open-ended zones emitted.
- **INV-02** SELV voltage in Zone 0 — any §701 Zone 0 fixture must be SELV ≤12 V
  (§701.414.4.5); voltage > 12 V in Zone 0 is a CRITICAL flag.
- **INV-03** Medical IMD alarm response — §710 Group 2 must include IMD with ≤8 s alarm
  response per BS EN 61557-8; missing IMD spec is a CRITICAL flag.
- **INV-04** RCD 30 mA blanket — §701/§702/§703 zones must have 30 mA RCD on all circuits
  (§701.411.3.3; §703.411.3.3); heater-exempt flag must be explicitly set for §703 heater
  circuit, not silently suppressed.
- **INV-05** Main equipotential bonding — §702 pool zones must emit a bonding_requirements
  entry referencing §702.415.1 (NOT §702.55.1 — that clause does not exist).
- **INV-06** IPx5 whirlpool/spa — when `water_jet_present == true`, §701.512.2 constraint
  must appear in constraint_set for every Zone 1 and Zone 2 fixture.

MEDIUM severity:
- **INV-07** ELV transformer short-circuit — §715 ELV circuits must reference
  BS EN 61558-2-6 transformer spec in constraint_set.
- **INV-08** Socket outlet exclusion — §701.512.3 socket ≥3 m from Zone 1 boundary must
  appear in constraint_set for every §701 room.
- **INV-09** KE jurisdiction routing — when `jurisdiction == 'KE'`, every clause citation
  must carry both the KS 1700:2018 §313 local reference and the routed BS 7671 clause.
- **INV-10** Provenance completeness — IR `provenance._source` ≥40 chars;
  `verification_status` must match allowed enum from
  `shared/standards/electrical/BS7671/part7-special-locations.json`.

## Reviewer (5 D-checks)

- **D-1** Room-type vs zone-type consistency — does the assigned Part 7 section match the
  architectural room description? (e.g., a "wet room" tagged as standard bathroom may need
  §701.512.2 IPx5 treatment even without explicit `water_jet_present` flag)
- **D-2** Changing-room adjacency — §702 pool hall with adjacent changing room; Zone 2
  overlap per §702.55.4 requires specific bonding continuity check (D-2 flags if
  `changing_room_adjacency` is not declared in input but floor-plan geometry implies it)
- **D-3** Medical group plausibility — Group 2 classification outside NHS / private hospital
  site should be flagged as unusual; auto-derived Group must be confirmed by engineer
- **D-4** ELV lighting external hazard — §715 external landscape circuits; reviewer checks
  that IP rating of ELV luminaires is consistent with external exposure class
- **D-5** Bonding schedule completeness — supplementary bonding schedule entries must cover
  all metallic services (gas, water, HVAC) within the zone perimeter, not only electrical
  fixtures; D-5 flags incomplete bonding_requirements entries for engineer review

## Examples

17 total: 8 standalone + 9 cascade.

**Standalone (8):**
1. `uk-bathroom-standard-bath-and-shower` — §701 standard Zone 0/1/2 derivation; domestic
2. `uk-bathroom-whirlpool-with-pump` — §701 + §701.512.2 IPx5; whirlpool pump in Zone 1
3. `uk-shower-room-wet-room-floor` — §701 wet-room floor; no bath tray anchor
4. `uk-pool-hall-with-changing-room-adjacency` — §702 Zones A/B/C/D + §702.55.4 changing room
5. `uk-sauna-with-3-zone-derivation` — §703 heater-anchor 3-zone split; heater circuit exempt
6. `uk-medical-or-group-2-with-it-system` — §710 Group 2 operating room + IMD + HTM 06-01
7. `uk-medical-ward-group-1-bonding` — §710 Group 1 ward + supplementary bonding schedule
8. `uk-external-landscape-elv-lighting` — §715 ELV external; BS EN 61558-2-6 transformer

**Cascade (9):**
9–11. `cascade-lighting-layout-uk-*` — lighting-layout v1.6 consumes zoning intent; zone-aware
  luminaire placement enforcement across bathroom / pool hall / medical Group 2
12–14. `cascade-small-power-uk-*` — small-power v1.2 socket exclusion + isolation enforcement;
  bathroom violation demo; medical Group 2 isolation; external ELV violation
15–16. `cascade-db-layout-uk-*` — db-layout v1.5 RCD allocation + medical IT distribution board
17. `cascade-multi-jurisdiction-ke-bathroom-route-to-bs` — KE §313 dual-citation path

## Honest disclosures

- **INT jurisdiction worked examples** are NOT included at v1.0. IEC 60364-7-XXX citation
  routing is declared in the manifest and supported via `_clause_citation` fields in the IR,
  but no INT input/output examples exist. Deferred to v1.1.
- **MRI rooms** are NOT in scope. IEC 60601-1 Faraday cage and RF shielding requirements
  constitute a different engineering stack. A sibling skill will be created when the first
  MRI project surfaces.
- **US NEC parallel** (NEC Article 680 for pools; Article 517 for medical) is NOT in scope.
  Sibling skill `electrical/special-locations-us/` deferred to when first US project arrives.
- **§722 EV charging** is NOT in scope at v1.0. Intersection with `electrical/ev-charging/`
  skill deferred until that skill matures.
- **Embedded heating (former §753)** — §753 does not exist in BS 7671:2018+A2:2022. v1.1
  candidate routing via §415 + §522; excluded from v1.0 scope.
- Zone geometry derivation assumes 2D plan-view anchor coordinates. 3D adjacency (e.g.,
  ceiling Zone 1 boundary above a bath) is approximated from ceiling_height_mm; engineer
  must verify 3D envelope before construction issue.

## Standards cross-reference

| Citation | Section | Used for |
|---|---|---|
| BS 7671:2018+A2:2022 §701 | §701 | Generic bathroom/shower-room scope |
| BS 7671:2018+A2:2022 §701.411.3.3 | §701 | 30 mA RCD blanket (INV-04) |
| BS 7671:2018+A2:2022 §701.414.4.5 | §701 | SELV ≤12 V in Zone 0 |
| BS 7671:2018+A2:2022 §701.415.2 | §701 | Supplementary equipotential bonding |
| BS 7671:2018+A2:2022 §701.512.2 | §701 | IPx5 where water jets used (drives whirlpool IPx5 — INV-06) |
| BS 7671:2018+A2:2022 §701.512.3 | §701 | Socket outlet ≥3 m from Zone 1 boundary |
| BS 7671:2018+A2:2022 §702 | §702 | Generic swimming-pool scope |
| BS 7671:2018+A2:2022 §702.415.1 | §702 | Main equipotential bonding (INV-05; NOT §702.55.1) |
| BS 7671:2018+A2:2022 §702.415.2 | §702 | Pool supplementary bonding |
| BS 7671:2018+A2:2022 §702.55.4 | §702 | Zone 2 changing-room overlap (D-2) |
| BS 7671:2018+A2:2022 §703 | §703 | Generic sauna scope (3-zone split) |
| BS 7671:2018+A2:2022 §703.411.3.3 | §703 | RCD blanket (heater exempt) |
| BS 7671:2018+A2:2022 §710 | §710 | Generic medical scope (Groups 0/1/2) |
| BS 7671:2018+A2:2022 §715 | §715 | Generic ELV lighting scope |
| HTM 06-01 | cross-ref | NHS technical memorandum (medical safety service categories — §710) |
| BS EN 60601 series | cross-ref | Medical equipment safety |
| BS EN 61557-8 | cross-ref | IMD spec — 8 s alarm response (§710 Group 2 — INV-03) |
| BS EN 61558-2-6 | cross-ref | ELV transformer short-circuit protection (§715 — INV-07) |
| BS 5266-1 | cross-ref | Emergency lighting in medical locations |
| BS 5489-1 | cross-ref | External area lighting (not Part 7; routes via §522 IP) |

## Why this skill exists

Created 2026-05-25 as a depth-specialist stub during the post-remediation within-skill-scope
audit (Sprint D follow-up). Identified as a gap in the lighting skill family: lighting-layout
v1.x produces fixtures but has no mechanism to enforce zone-restricted placement in Part 7
special locations. Built to v1.0.0 production in the 2026-06-01 sprint as Wave 1 second
deliverable (parallel with photometric-analysis shipped 2026-05-30).

See `docs/superpowers/specs/2026-06-01-special-locations-design.md` for the locked
architecture decisions + cascade contract context.

---

**Banned citations — do NOT use in any artifact derived from this skill:**
`§701.32` `§701.55` `§702.55.1` `§702.55.2` `§702.32` `§703.55` `§703.512` `§703.413` `§710.413.1.5` `§710.314` `§710.411.3.3` `§715.560.4` `§715.521` `§715.422` — do NOT use any of these 14 sub-clauses.

These sub-clauses do not exist in BS 7671:2018+A2:2022 and were identified as invented
citations at spec brainstorm (§3.2). Any eval, example, or prompt that references them is
incorrect and must be rejected.
