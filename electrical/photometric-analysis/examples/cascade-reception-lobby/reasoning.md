# cascade-reception-lobby — reasoning

Cascade retrofit of `electrical/lighting-layout/examples/reception-lobby` — a
zoned 5-circuit design with daylight-linked perimeter and occupancy-controlled
interior. Verifies narrow-beam downlight uniformity against the relaxed
`reception_lobby` U₀ target (0.4 vs 0.6 office). All 9 INVs PASS; intent
payload sets `task_area_compliant: true`.

## §1 Why this cascade example exists

The reception-lobby upstream is a classic mixed-zone example: perimeter
daylight-linked (Z1, 6 downlights along the glazed edge) plus interior
occupancy-controlled (Z2, 24 downlights in 4 rows of 6). The lumen-method
INV-1 cannot detect narrow-beam downlight scalloping per-point or per-observer
UGR — both are required by BS EN 12464-1 §4.4 + §6.6 for full sign-off.
This cascade closes that gap and serves as the worked example for "narrow-beam
downlight uniformity" — a different luminaire type from the LED panel
examples that dominate Wave 1.

## §2 Cascade context

Upstream: `electrical/lighting-layout/examples/reception-lobby/intent-out.json`
(30 LED_DOWNLIGHT at 1000 lm each; 5 circuits C-L01..C-L05; 0-10V dimming;
Part L assessed + compliant). The lighting-layout calc reports
`achieved_illuminance_lux: 302.4` (lumen-method room average, UF≈0.50 + MF≈0.80).

Photometric-analysis runs the per-point calc assuming full output (no daylight
contribution, no dimming) — the worst-case static snapshot. This is the
correct verification basis: the standard requires per-point compliance under
the design operating condition (full luminaire output), with controls treated
as an energy + amenity overlay, not a compliance prerequisite.

## §3 Grid resolution derivation

Task area: room 8×5 m minus 500 mm perimeter border per BS EN 12464-1:2021 §4.3
→ 7×4 m task area (x_min=500, x_max=7500, y_min=500, y_max=4500).

BS EN 12464-1:2021 §6.2 adaptive formula (B.1 fix-pass corrected):

- `d_m = max(7, 4) = 7.0`
- `p = 0.2 × 5^log₁₀(7.0) × 1000 mm`
- `log₁₀(7.0) ≈ 0.845`
- `5^0.845 ≈ 3.90`
- `p ≈ 0.2 × 3.90 × 1000 ≈ 779 mm`
- Clamped to [50, 1000] mm → in range
- Snapped to nominal 800 mm
- Grid fitted to bounds: 10 cols × 6 rows = 60 grid points (x-step ~778 mm
  to fit 7000mm extent across 9 intervals; y-step 800 mm fits 4000 mm
  extent across 5 intervals)

## §4 Per-point illuminance — narrow-beam behaviour

Runtime `calc.lumen_grid_solver` computed with the synthetic
`LED_DOWNLIGHT.ies` (70° beam, 540 cd max intensity):

- **achieved_avg: 305 lux** (matches upstream lumen-method 302.4 within 1%)
- **achieved_min: 235 lux** at NW corner (500, 4500) of the perimeter
  daylight-linked zone Z1; the perimeter downlights are spaced wider than
  the interior cluster, so the corner sees less light
- **achieved_max: 412 lux** directly beneath a downlight near the interior
  cluster centre
- **achieved_uniformity_u0: 0.77** = 235 / 305; comfortable margin over the
  0.4 reception_lobby target

The max/min ratio (412/235 ≈ 1.75) reflects the narrow-beam scalloping
characteristic of downlights — visibly more uneven than LED panels but
within reception_lobby's relaxed uniformity target. Lumen-method INV-1
detects neither the scalloping nor the corner cold-spot; this skill does.

## §5 UGR per CIE 117

4 default observer positions per [ugr-rules#default-observer-positions]
(adapted to 8×5 m room dims):

- **N-wall observer** at (4000, 4000, 1200), azimuth 180°: UGR 16.8
- **S-wall observer** at (4000, 1000, 1200), azimuth 0°: UGR 17.2 (worst)
- **E-wall observer** at (7000, 2500, 1200), azimuth 270°: UGR 16.4
- **W-wall observer** at (1000, 2500, 1200), azimuth 90°: UGR 16.6

`max_ugr_across_view_positions = 17.2 ≤ 19` reception limit per BS EN 12464-1:2021
Table 5.3 row 5.34. PASS with 1.8 margin.

Downlights with 70° beams direct most of their flux downward, putting less
intensity in the eye-line angle that drives UGR. This is why downlight rooms
typically have lower UGR scores than open-celled panels at the same lumen
density — a known characteristic that photometric-analysis correctly captures.

## §6 Reception U₀ target rationale

BS EN 12464-1 Table 5.3 row `reception_lobby` sets U₀ ≥ 0.4 — a deliberately
relaxed target vs the 0.6 office target. The relaxed target reflects
reception's mixed-task nature:

- Circulation + waiting (low task demand)
- Occasional reading at the reception desk (higher task demand, but
  task-specific lighting often provided by the desk-mounted fixture)
- Mood / aesthetic component (uniform-perimeter lighting often unwanted
  for visual interest)

Photometric-analysis applies the BS EN 12464-1 per-room-type target to the
correct row. Engineer-of-record verifies the room_type was correctly
declared upstream — that is the engineer's responsibility, not the skill's.

## §7 Honest disclosures

- **IES file** `shared/photometric/ies/LED_DOWNLIGHT.ies` is
  `synthetic_reference_C3` — a Lambertian-with-70°-cutoff archetype, NOT
  a manufacturer-measured photometric file. Real downlights from different
  manufacturers vary widely in beam angle (40°–90°), polar plot, and CCT;
  the engineer-of-record MUST substitute project IES before design freeze.
- **Daylight contribution NOT modelled** — the achieved values are static
  full-output photometric only. BS EN 12464-1 verification is performed
  under design lighting condition; daylight is an amenity benefit modelled
  separately (potentially via `daylight` skill in a future sprint).
- **Dimming NOT modelled** — 0-10V dimming is treated by photometric-analysis
  as a controls-layer overlay. The compliance basis is full output; dimming
  is a Part L energy-saving feature, not a compliance-loosening device.

## §8 INV walkthrough

All 9 INVs PASS — see `invariants[]` in `output.json`:

- **INV-01 (HIGH) PASS**: min 235 ≥ 210 (0.7×300)
- **INV-02 (HIGH) PASS**: U₀ 0.77 ≥ 0.4 reception target
- **INV-03 (HIGH) PASS**: max UGR 17.2 ≤ 19 reception limit
- **INV-04 (HIGH) PASS**: 1 luminaire_type matched by 1 IES file
- **INV-05 (HIGH) PASS**: grid_spacing 800 mm matches §6.2 corrected formula
- **INV-06 (HIGH) PASS**: 60 grid points consistent with metadata
- **INV-07 (MEDIUM) PASS**: 4 CIE 117 default observers (room-adapted positions)
- **INV-08 (MEDIUM) PASS**: _source 234 chars + verification_status enum match
- **INV-09 (HIGH) PASS**: cascade completed; tool_call_pending=false

## §9 Cascade signal to lighting-layout INV-11

Intent payload sets `task_area_compliant: true` AND `non_compliance_flags: []`.
Lighting-layout INV-11 PASS HIGH. Reception-lobby full_drawing IR is
sign-off-ready for the photometric dimension.

This cascade demonstrates two things the LED-panel examples don't:

1. **Narrow-beam downlight uniformity** can still pass U₀ when the beam
   spacing is matched to room dimensions (1.3 m spacing here for ~3 m
   ceiling).
2. **Per-room-type targets** (reception_lobby 300/0.4 vs office 500/0.6)
   give different acceptance criteria; photometric-analysis applies the
   correct row from BS EN 12464-1 Table 5.3 based on the upstream
   `room.room_type` declaration.
