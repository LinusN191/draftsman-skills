# uk-bathroom-zone-1-zone-2 — engineering reasoning

## 1 Scope

A 2.7 m × 2.1 m UK domestic en-suite bathroom with a 1.7 m × 0.7 m
acrylic bath against the south wall and an over-bath shower at
2.1 m AFF. Two ceiling-mounted IPx4 LED downlights on a single
6 A Type B MCB. One 1-gang switch on the east wall by the north
entrance, and one shaver socket on the west wall.

The example is the first `lighting-layout` shipped scenario to fire
**INV-12** (Wave 1 special-locations cascade) end-to-end alongside
**INV-11** (Wave 1 photometric cascade). It exists because the D.1
hand-trace found that none of the seven existing `lighting-layout`
examples carry a `room.room_type` in the Part-7 set — without this
new example the schema's third `allOf` clause would never fire on
the golden CI gate.

## 2 Room and occupancy class

The room is classed as `bathroom` per the
`lighting-layout-ir.schema.json` room-type enum (15 values per
BS EN 12464-1:2021 Table 5.x). Working plane 0.75 m, ceiling 2.25 m
chosen to match the §701 Zone 1 vertical ceiling (2250 mm) exactly so
that ceiling luminaires sit at the upper boundary of Zone 1 by
inclusive height check.

`environment_type` = `damp`. `ip_required` = `IPx4` is set at room
level — every electrical fixture inside the room footprint must meet
or exceed IPx4 unless the special-locations payload tightens the
floor further (e.g. Zone 0 demands IPx7).

## 3 Target illuminance

BS EN 12464-1:2021 Table 5.x for `bathroom` sets
`task_illuminance_maintained ≥ 200 lx` (general task plane) with
`UGR_L ≤ 22` and `U_0 ≥ 0.40`. We adopt 200 lx maintained.

CIBSE TM 3-25 supports the 200 lx general illuminance target for
washrooms and en-suite bathrooms in domestic and small-hospitality
fit-outs.

## 4 Lumen-method calculation

Lumen method gives the minimum luminaire count:

```text
N_min = (E × A) / (Φ × UF × MF)
      = (200 × 5.67) / (1500 × 0.60 × 0.80)
      = 1134 / 720
      = 1.575  → round UP → N = 2
```

Inputs:

- `E` = 200 lx maintained target.
- `A` = 5.67 m² floor area.
- `Φ` = 1500 lm per luminaire (LED_DOWNLIGHT_IPX4 ontology default).
- `UF` = 0.60 from the CIBSE SLL standard reflectance table for a
  low-RI tiled bathroom at `RI = 0.79` and reflectances
  `0.5 / 0.5 / 0.2` (light tiled walls + ceiling).
- `MF` = 0.80 for a clean domestic bathroom on a 3-year cleaning
  cycle per CIBSE TM 3-25.

Round-UP is mandatory — round-to-nearest would give 1.58 → 2 by
coincidence here but the CIBSE SLL convention is round-UP regardless.

Achieved illuminance back-substituted:

```text
E_achieved = (N × Φ × UF × MF) / A
           = (2 × 1500 × 0.60 × 0.80) / 5.67
           = 1440 / 5.67
           = 254 lx
```

254 lx ≥ 200 lx target. **INV-1 PASS.**

S/H ratio check: `Hm = 2250 - 750 = 1500 mm`. The two luminaires
straddle the 1350 mm centreline; spacing between them is 700 mm.
`SHR_max = 1.5` (LED_DOWNLIGHT_IPX4 ontology default) gives limit
2250 mm — 700 mm spacing well within envelope. **INV-2 PASS.**

## 5 Special-locations cascade — what the upstream told us

The producer-side cascade
(`electrical/special-locations/examples/cascade-lighting-layout-uk-bathroom/intent-out.json`)
emits a 5-zone payload derived from the 2 anchor fixtures plus 1
electrical constraint:

| Zone id          | Source   | Polygon (mm)                                | Height (mm) | IP min | V max | Prohibited                                                          |
| ---------------- | -------- | ------------------------------------------- | ----------- | ------ | ----- | ------------------------------------------------------------------- |
| zone_bath_1_z0   | bath_1   | (500, 0) → (2200, 700)                      | 0–550       | IPx7   | 12    | socket_230v, switch_230v, luminaire_non_ip_rated, shaver_socket, fixed_heater_230v |
| zone_bath_1_z1   | bath_1   | (500, 0) → (2200, 700)                      | 550–2250    | IPx4   | 230   | socket_230v, switch_230v, luminaire_non_ip_rated                    |
| zone_shower_1_z1 | shower_1 | (500, 0) → (2200, 700)                      | 0–2100      | IPx4   | 230   | socket_230v, switch_230v, luminaire_non_ip_rated                    |
| zone_bath_1_z2   | bath_1   | (-100, -600) → (2800, 1300)                 | 0–2250      | IPx4   | 230   | socket_230v                                                          |
| zone_shower_1_z2 | shower_1 | (-100, -600) → (2800, 1300)                 | 0–2100      | IPx4   | 230   | socket_230v                                                          |

`electrical_constraints[]` carries one `rcd_blanket_by_room`
constraint per BS 7671:2018+A2:2022 §701.411.3.3 — 30 mA RCD on
every LV circuit serving a location containing a bath or shower.

`payload.compliant = true`, `violation_count_critical = 0`,
`violation_count_high = 0`, `non_compliance_flags = []`.

## 6 Luminaire placement decisions

Two LED_DOWNLIGHT_IPX4 fixtures on the 1350 mm centreline (X):

- **L01** at (1350, 1050, 2250). Point-in-polygon vs Zone 2 footprint
  (-100..2800 X, -600..1300 Y) → INSIDE; height 2250 ≤ 2250 → INSIDE
  bath_1_z2 inclusive. Required `ip_rating_min = IPx4`; luminaire
  declares `ip_rating = IPx4` → PASS per BS 7671:2018+A2:2022
  §701.512.2. `max_voltage_v = 230` → 230 V Class 2 driver PASS.
- **L02** at (1350, 350, 2250). Point-in-polygon vs bath_1_z1
  polygon (500..2200 X, 0..700 Y) → INSIDE; height 2250 ≤ 2250 →
  INSIDE bath_1_z1 inclusive. `IPx4` matched, 230 V matched. PASS
  per BS 7671:2018+A2:2022 §701.512.2.

The over-bath luminaire L02 is the load-bearing engineering case
here: in standard UK domestic practice it is the bath-side luminaire
that fails IP compliance most often when a non-engineered fixture
spec is dropped in. Holding L02 to IPx4 with explicit cross-check
against `payload.zones[bath_1_z1].ip_rating_min` is the canonical
INV-12 sub-check 3 demonstration.

## 7 Switch placement

The wall switch sits at (2550, 1900, 1200 mm AFF) on the east wall,
latch-side of the north entrance at x = 2400. y = 1900 > 1300 →
OUTSIDE the Zone 2 polygon (which y_max = 1300). The switch is
therefore not subject to the §701 Zone 2 switch-distance constraint
(`switch_position_min_distance_mm = 3000` from Zone 1 boundary).

A 230 V switch inside Zone 2 would also be permitted in pure §701
terms — Zone 2 lists only `socket_230v` as a prohibited fixture
type — but engineer's practice is to keep switches outside the
splash envelope where possible. Holding to 1200 mm AFF matches the
`switching-rules#height` convention.

## 8 Shaver socket

The shaver socket SS01 at (50, 1900, 1400 mm AFF) on the west wall
also sits at y = 1900 > 1300 → OUTSIDE all §701 zones. Shaver
sockets are permitted under BS 7671:2018+A2:2022 §701.512.3 when
supplied via a BS EN 61558-2-5 isolating transformer. The fixture
itself is annotated in `drawing_notes` but does not appear in the
`lighting-layout` IR's `switches[]` or `luminaires[]` arrays — it is
a Part-7 ancillary that the `small-power` skill picks up downstream
when it consumes this `lighting-layout` intent plus the same
special-locations cascade.

## 9 Circuit and RCD

Single circuit C-L01 on DB L1 feeds both luminaires:

- `total_load_w` = 2 × 13 W = 26 W.
- `mcb_rating_a` = 6 A Type B (BS EN 60898-1).
- 80 % continuous-load cap: 6 × 230 × 0.8 = 1104 W → 26 W is
  2.4 % of cap. INV-5 PASS per BS 7671:2018+A2:2022 §433.1.1 plus
  IET OSG App A.
- 30 mA RCD protection per BS 7671:2018+A2:2022 §701.411.3.3,
  cascaded from `electrical_constraints[0].rcd_blanket_by_room`. The
  RCD belongs in the upstream DB skill output — `lighting-layout`
  only annotates the requirement in `drawing_notes` and surfaces the
  cascaded constraint in `consumed_intents.special_locations_zoning.payload.electrical_constraints[]`.

## 10 Part L efficacy

`new_build = true` gates the BS-compliance check.
`lamp_efficacy_lm_per_w = 1500 / 13 = 115.4 lm/W` exceeds the
Building Regulations Approved Document L Volume 1 (2021) lighting
efficacy floor for new domestic buildings (65 lm/W threshold for
fixed lighting circuits). **INV-6 PASS.**

## 11 Photometric cascade

`consumed_intents.photometric_grid` is sourced from the Part-7
retrofit cascade
(`electrical/photometric-analysis/examples/cascade-uk-bathroom-zone-1-zone-2/intent-out.json`).
This is a production cascade source — the D.2 synthetic helper
(`_synthetic_photometric_intent.json`) was a temporary substitution
used at D.2 ship time when no Part-7 photometric cascade source
existed; the Part-7 retrofit task ships the real cascade and deletes
the helper. The headline numbers match the synthetic helper
byte-for-byte so this walkthrough did not need to change:

- `achieved_avg_illuminance_lux = 254` — matches IR's
  `calculation_summary.achieved_illuminance_lux`.
- `target_illuminance_lux = 200` — matches IR target.
- `ugr_max = 18.2 ≤ ugr_target = 19` (BS EN 12464-1:2021 Table 5.36
  bathroom_domestic UGR ceiling per the photometric-analysis spec
  design parameter).
- `achieved_uniformity_u0 = 0.66 ≥ uniformity_target = 0.40` (Table
  5.36 bathroom_domestic U_0 floor).
- `task_area_compliant = true`.
- `non_compliance_flags = []` → nothing to cascade.
- `ies_source_summary.verification_status_lowest =
  synthetic_reference_C3` — the engineer-of-record must substitute
  manufacturer IES (Aurora, JCC, Collingwood IPx4 series, etc.)
  before final design freeze.

**INV-11 PASS** with all four sub-checks satisfied.

## 12 Special-locations cascade — INV-12 sub-check walkthrough

Sub-check 1 — presence: `consumed_intents.special_locations_zoning`
present. PASS.

Sub-check 2 — upstream compliance: `payload.compliant = true`,
`zone_count = 5`, `violation_count_critical = 0`,
`violation_count_high = 0`. PASS.

Sub-check 3 — fixture cross-walk: for each luminaire find the
containing zone(s) by point-in-polygon plus inclusive height check,
then verify (a) luminaire type ∉ `zone.prohibited_fixture_types`,
(b) luminaire `ip_rating` ≥ `zone.ip_rating_min`, (c) luminaire
voltage ≤ `zone.max_voltage_v`.

- L01 (1350, 1050, 2250) → bath_1_z2: IPx4 matched, 230 V matched,
  luminaire ∉ {socket_230v}. PASS.
- L02 (1350, 350, 2250) → bath_1_z1: IPx4 matched, 230 V matched,
  luminaire ∉ {socket_230v, switch_230v, luminaire_non_ip_rated}
  (IPx4 is an IP-rated luminaire, not the prohibited non-IP class).
  PASS.

Sub-check 4 — flag cascade: `payload.non_compliance_flags = []` →
vacuously satisfied; nothing needs to appear in
`calculation_summary.non_compliance_flags`. PASS.

All four sub-checks PASS → **INV-12 PASS HIGH**.

## 13 Honest disclosures

- The `photometric_grid` cascade source now resolves to a real
  photometric-analysis example
  (`electrical/photometric-analysis/examples/cascade-uk-bathroom-zone-1-zone-2/intent-out.json`)
  shipped by the Part-7 retrofit task. The D.2 synthetic helper
  (`_synthetic_photometric_intent.json`) has been deleted. The
  cascade payload headline numbers are byte-identical to the previous
  synthetic helper (254 / 168 / 0.66 / 18.2 / 200 / true), so the
  INV-11 walkthrough did not change in substance — only the cascade
  source path repoint and the UGR limit reference (22 → 19 to match
  the photometric-analysis spec design parameter for bathrooms).
- `UF = 0.60` and `MF = 0.80` are CIBSE-table defaults — neither
  was derived from a project-specific photometric file. The
  engineer-of-record must confirm before issue.
- IPx4 is the minimum rating that satisfies §701.512.2 in both Zone
  1 and Zone 2. A higher rating (IPx5 / IPx7) would be acceptable;
  the example uses IPx4 to exercise the boundary case.
- The bath polygon, shower head height, and ceiling height match the
  C.2 producer cascade exactly so that INV-12 sub-check 3's
  point-in-polygon + height check fires on real geometry — not on
  derived approximations.

## 14 Standards cited (verified subset only)

- BS EN 12464-1:2021 — Table 5.x bathroom task illuminance / UGR /
  U_0.
- BS 7671:2018+A2:2022 §701 — Locations containing a bath or
  shower (top-level chapter).
- BS 7671:2018+A2:2022 §701.411.3.3 — 30 mA RCD blanket-by-room.
- BS 7671:2018+A2:2022 §701.414.4.5 — SELV ≤ 12 V in Zone 0
  (cascaded from upstream payload; not enforced in this example).
- BS 7671:2018+A2:2022 §701.512.2 — IPx4 fixture minimum in Zones
  1 and 2.
- BS 7671:2018+A2:2022 §701.512.3 — Shaver-socket allowance with
  BS EN 61558-2-5 isolation.
- BS 7671:2018+A2:2022 §433.1.1 — Conductor overload protection
  (referenced for the 6 A MCB sizing).
- BS EN 61558-2-5 — Particular requirements for shaver
  transformers and supply units.
- CIBSE SLL Code for Lighting 2012 — Standard reflectance table.
- CIBSE TM 3-25 — Maintenance factor convention.
- Approved Document L Volume 1 (2021) — Domestic lighting efficacy.

## 15 What downstream consumers see

The intent-out.json carries:

- `room_id`, `room_type = bathroom`.
- `luminaire_summary`: 2 × 13 W IPx4 fixtures.
- `circuits[0]`: C-L01 on DB L1, 26 W, `voltage_class = LV_power`,
  `mcb_rating_a_suggested = 6`.
- `consumed_intents.photometric_grid` mirror (so db-layout etc. can
  read the photometric verdict without re-loading the upstream
  intent-out).
- `consumed_intents.special_locations_zoning` mirror (so db-layout
  can size the RCD and small-power can read the zone polygons
  directly).

This is the key contract for Wave 1 cascade: every downstream skill
that consumes the `lighting-layout` intent gets the full upstream
cascade chain for free, without having to re-resolve the
photometric-analysis or special-locations cascade themselves.

## §D5 RETROFIT (2026-06-04)

This example was authored at v1.6.0 with a single
`target_illuminance_lux` per room. v1.7.0 splits target into per-zone
`em_target_lux` per BS EN 12464-1:2021 §4.2.2 + Table 6. This retrofit
applies the backwards-compatibility defaults without changing any
engineering numbers or the Wave-1 cascade payloads.

**Zone purpose decision**

The single Z2 "Bathroom interior" zone receives `purpose: "circulation"`
(ZP-05) and `em_target_lux: 200`. Justification:

- The plan-template recipe is *vanity → task (500 lx) / entry →
  circulation (200 lx)*. This bathroom carries no vanity anchor in
  `inputs.anchor_fixtures` — only `bath_1` + `shower_1` are declared.
  There is no mirror, sink, or vanity counter over which to layer a
  500 lx task sub-zone.
- The scenario is therefore a single general-occupancy bathroom zone.
  Per `zone-purpose-rules.yaml` ZP-05, a circulation/general-occupancy
  area takes its Em directly from BS EN 12464-1:2021 Table 5 (200 lx
  bathroom/washroom entry) — not subject to the §4.2.2.2 /
  §4.2.2.3 task/surrounding/background ratio rules.
- `em_target_lux=200` matches the v1.6.0 `target_illuminance_lux=200`
  byte-identical. No engineering judgement was traded.
- An engineer-of-record adding a future vanity sub-zone over a mirror
  would split Z2 into a vanity task sub-zone (`purpose="task"`,
  `em_target_lux=500` per BS EN 12464-1 Table 5 bathroom_vanity) and
  an entry circulation sub-zone (`purpose="circulation"`,
  `em_target_lux=200`). That is the canonical Table-5 split; this
  example collapses it onto one circulation zone for the reason above.

**Mount-type decision**

Both luminaires receive `mount_type: "recessed"` (MT-01 default — the
95 mm IPx4 LED recessed downlight is physically recessed by
definition per `luminaire_type.description`). `z_mm` and
`suspension_length_mm` are omitted per the recessed convention —
geometry inherits `room.ceiling_height_mm = 2250`. The §701 Zone 1
and Zone 2 vertical ceiling at 2250 mm AFF still bounds both
luminaires inclusively, so the INV-12 sub-check 3 cascade walk
(point-in-polygon + height inclusion) is unchanged from v1.6.0.

**per_zone_achieved[] population**

One entry for Z2: `target=200`, `achieved=254`, `ratio_compliance="pass"`
(room-level achievement maps directly to the single circulation zone
— INV-19 PASS by a 27% margin).

**INV-13..INV-19 walk**

- **INV-13 PASS** — Z2 declares `purpose="circulation"` ∈ enum, no
  orphan surrounding present.
- **INV-14 PASS (vacuous)** — no surrounding zone declared. ZP-05
  exempts circulation zones from the task-to-surrounding ratio anyway.
- **INV-15 PASS (vacuous)** — no background zone declared. ZP-05
  exempts circulation zones from the task-to-background ratio anyway.
- **INV-16 PASS (vacuous)** — no pendant or suspended luminaire.
  Both are recessed; MT-01 omits `z_mm` and `suspension_length_mm`.
- **INV-17 PASS** — recessed inheritance gives `z=2250 mm` for both
  luminaires; `z > working_plane (2250 > 750)` and `z ≤
  ceiling_height_mm (2250 ≤ 2250)`. The 2250 mm match also pins
  both luminaires to the upper inclusive boundary of bath_1_z1 /
  bath_1_z2 in the §701 cascade, so INV-12 sub-check 3 stays valid.
- **INV-18 PASS** — `hm_mm = ceiling_height_mm − working_plane_mm =
  2250 − 750 = 1500 mm`. Recorded `room.hm_mm = 1500`. Drift 0 mm.
- **INV-19 PASS** — Z2 (circulation): `target=200`, `achieved=254`,
  `ratio_compliance="pass"`, severity none.

**Cascade integrity**

`consumed_intents.special_locations_zoning.payload` and
`consumed_intents.photometric_grid.payload` are preserved
byte-identical from the C.2 producer cascade
(`electrical/special-locations/examples/cascade-lighting-layout-uk-bathroom/intent-out.json`)
and the Part-7 photometric retrofit
(`electrical/photometric-analysis/examples/cascade-uk-bathroom-zone-1-zone-2/intent-out.json`).
SHA-256 of the special-locations payload pre-edit equals SHA-256
post-edit
(`e03c3ff33d433789048379c58e9d44072e8892aeb3f10dbc86fcc99b05715cf4`).
INV-11 and INV-12 evidence strings unchanged.

**Honest disclosures (4-place)**

1. Engineering judgement defaults documented in
   `input._d5_retrofit_note`.
2. `output.calculation_summary.assumptions[]` carries the v1.6.0 →
   v1.7.0 retrofit explanation including the no-vanity collapse.
3. `output.rationale.sections[]` includes a "v1.7 retrofit" section
   explaining ZP-05 and MT-01 default choices for this example.
4. This `reasoning.md` §D5 section.

No engineering numbers were changed — the v1.6.0 lumen-method walk
(N=2 round-up, achieved 254 lx, S/H 700 mm within 2250 mm envelope),
the §701 zone mapping, the 6 A Type B + 30 mA RCD circuit, and the
photometric / special-locations cascade payloads all remain
identical. The retrofit is purely additive metadata to align the
example with the v1.7.0 zone-purpose / mount-type schema.
