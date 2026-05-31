# cascade-uk-multi-entrance-classroom — reasoning

Cascade retrofit of `electrical/lighting-layout/examples/uk-multi-entrance-classroom`
— a 10×8 m classroom with 16 LED_PANEL_600 panels in a 4×4 grid and 3
entrance switches per BS 7671 §559.5. Verifies the BS EN 12464-1 Table 5.3
classroom row (300 lux target, U₀ 0.6, UGR 19) — distinct from the
open_plan_office row (500 lux target). All 9 INVs PASS; intent payload sets
`task_area_compliant: true`.

## §1 Why this cascade example matters

This cascade demonstrates the per-room-type target distinction. The classroom
room type sits next to open_plan_office in BS EN 12464-1 Table 5.3 but has
a materially lower task-illuminance target:

| Room type | Target (lux) | U₀ | UGR |
|---|---|---|---|
| open_plan_office | 500 | 0.6 | 19 |
| classroom | 300 | 0.6 | 19 |

A well-provisioned classroom with the same panel layout as a 500-lux office
will easily over-shoot the 300 target. This cascade verifies that the
photometric-analysis applies the correct row for the upstream `room.room_type`
declaration.

This is also one of the few examples with **multi-entrance switching**
(3 switches) — BS 7671 §559.5 requires every entrance to have switching
control. Photometric-analysis treats switches as a controls overlay and
verifies under full output (matching the convention in cascade-reception-lobby).

## §2 Cascade context

Upstream: `electrical/lighting-layout/examples/uk-multi-entrance-classroom/intent-out.json`.

Lumen-method (upstream) detail per upstream calculation_summary:
- N (minimum) = 10.75 → rounded UP to 11
- Actual N = 16 (bumped for 4×4 grid symmetry + S/H margin)
- UF = 0.62, MF = 0.80
- achieved_illuminance_lux = 446.4 (room average)
- ugr_status = "UGR ≤ 19 — confirm from photometric data (classroom task)"

The upstream lumen-method INV-1 already PASSes (446.4 > 300). This cascade
adds the per-point + UGR verification that the lumen-method INV-1 cannot
deliver.

## §3 Grid resolution derivation

Identical geometry to cascade-office-open-plan and
cascade-uk-open-plan-office-10x8-dali (all are 10×8 m rooms):

- Task area: 9×7 m after 500mm border per BS EN 12464-1 §4.3
- d = 9.0 m
- p = 0.2 × 5^log₁₀(9.0) × 1000 ≈ 929 mm → snapped to 900 mm
- 11 cols × 9 rows = 99 grid points

## §4 Per-point illuminance — classroom target

Runtime `calc.lumen_grid_solver` with synthetic `LED_PANEL_600-4500lm.ies`:

- **achieved_avg: 482 lux** — 161% of 300 classroom target; matches upstream
  lumen-method 446.4 within 8% (the small delta reflects the photometric
  engine's per-point integration vs the lumen-method's lumped UF, both at
  the same 4500 lm × 16 panels total)
- **achieved_min: 380 lux** at NW corner (500, 7500); 170 lux margin over
  the 210 (0.7 × 300) threshold — well-provisioned classroom
- **achieved_max: 569 lux** at room centre under the 4-panel cluster
- **achieved_uniformity_u0: 0.79** = 380 / 482; comfortable margin over the
  0.6 classroom target

The 4×4 uniform grid produces smooth spatial distribution; max/min ratio
~1.5× is typical for a panel layout matched to the room dimensions.

## §5 UGR per CIE 117 — classroom limit

4 default observer positions:

- **N-wall observer** at (5000, 6500, 1200), azimuth 180°: UGR 17.4
- **S-wall observer** at (5000, 1500, 1200), azimuth 0°: UGR 17.8 (worst)
- **E-wall observer** at (8500, 4000, 1200), azimuth 270°: UGR 16.9
- **W-wall observer** at (1500, 4000, 1200), azimuth 90°: UGR 17.1

`max_ugr_across_view_positions = 17.8 ≤ 19` classroom limit per BS EN 12464-1
Table 5.3 row 5.34 classroom. PASS with 1.2 margin.

The classroom UGR-19 limit is the same as open_plan_office despite the
lower illuminance target. UGR is geometry × luminance-driven, not
target-illuminance-driven; classrooms with the same luminaires get the
same UGR scores as offices with the same layout.

The upstream `ugr_status: "UGR ≤ 19 — confirm from photometric data
(classroom task)"` flag is now resolved with a hard photometric
verification; the flag drops from the post-D.2 retrofit drawing notes.

## §6 Working plane = 700 mm (student desk)

`room.working_plane_mm = 700` reflects student desk height per BS EN 12464-1
Table 5.x classroom. Differs from:

- private_office / open_plan_office: 750 mm (adult desk)
- reception_lobby: 750 mm (counter)
- warehouse: 0 mm (floor)
- meeting_room: 750 mm

The 50 mm difference between classroom (700) and office (750) is small;
at the 2.8 m ceiling height it doesn't materially change achieved values
(cosine fall-off is gentle in the central rays). It's important nonetheless
for the standard's correct application.

## §7 Multi-entrance switching (informational)

3 entrance switches (SW01..SW03) per BS 7671 §559.5: each entrance must
have switching control of either the whole room or its local zone.
Photometric-analysis treats switches as a controls overlay — the
verification basis is full output (all 16 panels on).

This matches the convention used in cascade-reception-lobby (0-10V
dimming treated as controls overlay; full output is the verification
basis). The reasoning is consistent: BS EN 12464-1 verification requires
per-point compliance under the design lighting condition (full output);
dimming and switching are amenity / energy features that don't loosen
the compliance basis.

## §8 INV walkthrough

All 9 INVs PASS:

- **INV-01 (HIGH) PASS**: min 380 ≥ 210 (0.7×300)
- **INV-02 (HIGH) PASS**: U₀ 0.79 ≥ 0.6 classroom target
- **INV-03 (HIGH) PASS**: max UGR 17.8 ≤ 19 classroom limit
- **INV-04 (HIGH) PASS**: 1 luminaire_type matched by 1 IES file
- **INV-05 (HIGH) PASS**: grid_spacing 900 mm matches §6.2 corrected formula
- **INV-06 (HIGH) PASS**: 99 grid points; representative slice in IR
- **INV-07 (MEDIUM) PASS**: 4 CIE 117 default observers
- **INV-08 (MEDIUM) PASS**: _source 262 chars + verification_status enum match
- **INV-09 (HIGH) PASS**: cascade completed; tool_call_pending=false

## §9 Cascade signal to lighting-layout INV-11

Intent payload sets `task_area_compliant: true` AND `non_compliance_flags: []`.
Lighting-layout INV-11 PASS HIGH. uk-multi-entrance-classroom full_drawing IR
is sign-off-ready.

## §10 Honest disclosures

- **IES file** is `synthetic_reference_C3` — Lambertian archetype, NOT
  manufacturer-measured. Engineer-of-record substitutes project IES.
- **Reflectances 0.7/0.5/0.2** assume clean classroom. Real classrooms
  with dark furniture, chalk-board / display-board walls, or carpet may
  have lower wall and floor reflectance (0.3-0.4 wall typical), reducing
  achieved_avg by ~5-8%. This margin is comfortably absorbed by the
  current 482 lux value over the 300 target.
- **Working plane simplification**: real classrooms have varied task
  surfaces (student desks, teacher's desk, demonstration bench at the
  front). The 700 mm plane is the BS EN 12464-1 standard reference;
  the engineer-of-record may run a separate task-area calc for the
  teacher's bench or demonstration zones if those have different working
  plane heights.
