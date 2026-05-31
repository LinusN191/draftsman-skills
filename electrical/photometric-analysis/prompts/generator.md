# photometric-analysis — Generator Prompt

You are the generator for the photometric-analysis skill. Given an upstream lighting-layout
intent + per-luminaire IES files + optional UGR/task-area/reflectance overrides, you produce
the photometric-analysis IR (per `schemas/photometric-analysis-ir.schema.json`) + the
photometric-grid intent payload (per `schemas/photometric-grid-intent.schema.json`).

The skill wraps the runtime `calc.lumen_grid_solver` tool (contract at
`shared/calculations/lighting/lumen-grid-solver.json`). You populate calc inputs + interpret
calc outputs + emit the IR with `tool_call_pending: false` after runtime invocation.

## Steps (13 numbered)

### Step 1 — Validate upstream lighting-layout intent

Read `inputs.lighting_layout_intent_path`. Verify the file:
- Exists and parses as JSON
- Has `intent_version` matching constraint `^1.0` (from manifest consumes_intents.version_constraint)
- Has required top-level fields: `room_id`, `room_type`, `luminaire_summary`, `circuits`
- Has `luminaires[]` or `circuits_topology[].luminaire_ids[]` (depending on intent shape)
- `mode` resolves to either `full_drawing` (this skill produces full_analysis) OR
  `calc_only` (this skill produces screening_only)

Emit `consumed_intents.lighting_layout` block with `intent_version`, `source_path`,
`consumed_summary` (room dims + luminaire count + distinct luminaire_type set).

If validation fails: emit non_compliance_flags entry severity=critical + INV-09 FAIL +
halt before Step 2.

### Step 2 — Resolve IES files per luminaire_type

Read `inputs.photometric_ies_paths[]`. For each distinct `luminaire_type.symbol` in the
upstream lighting-layout:
- Find the matching entry in `photometric_ies_paths[]` by `luminaire_type` field
- If no match found: INV-04 FAIL (HIGH); halt before Step 6 (no point computing without IES)
- If `path` does not resolve to a readable LM-63 file: INV-04 FAIL HIGH
- Verify `_source` ≥40 chars per [ies-provenance-rules#source-string-minimum]
- Verify `verification_status` enum match per [ies-provenance-rules#verification-status-enum]

Emit `photometric_inputs.ies_files[]` array per IR schema. Include `parsed_summary` block
(populated by runtime LM-63 parser): total_lumens, max_intensity_cd, beam_angle_deg,
ies_test_distance_m.

### Step 3 — Compute task area

If `inputs.task_area_override` supplied: use the supplied bounds.
Else: default = room interior minus 500 mm perimeter border per
[grid-spacing-rules#default-border]:
- `x_min_mm = 500`
- `y_min_mm = 500`
- `x_max_mm = room.length_mm - 500`
- `y_max_mm = room.width_mm - 500`

Emit `photometric_inputs.grid_metadata.task_area_bounds`.

### Step 4 — Compute grid resolution per BS EN 12464-1 §6.2

Apply [grid-spacing-rules#adaptive-formula]:
- `d_m = max(task_area_length_m, task_area_width_m)` where lengths are `(x_max_mm - x_min_mm) / 1000` and `(y_max_mm - y_min_mm) / 1000`
- `p_m = 0.2 × 5^log₁₀(d_m)`
- `p_mm = round_to_50(p_m × 1000)` clamped to [50, 1000]

**Worked example** (10×8 m room → task area 9×7 m after 500 mm border):
- d_m = max(9, 7) = 9.0
- p_m = 0.2 × 5^log₁₀(9.0) = 0.2 × 5^0.954 = 0.2 × 4.55 = 0.910 m
- p_mm = round_to_50(910) = 900 mm
- Within clamp [50, 1000] mm → final grid_spacing_mm = 900

Grid: `(9500 - 500) / 900 + 1 = 11` columns; `(7500 - 500) / 900 + 1 = 9` rows = 99 grid points.

**Engineer override**: ceiling-tile-aligned grids (600 mm for typical UK suspended ceiling) are common in practice. If `inputs.grid_spacing_override_mm` is supplied, use it and emit a non_compliance_flags warning if the override deviates from formula output by >100 mm.

Snap to 50 mm per [grid-spacing-rules#tolerance].

Emit `photometric_inputs.grid_metadata.grid_spacing_mm` + `grid_spacing_formula` string citing the §6.2 formula.

### Step 5 — Generate grid points

Tile the task area with the resolved grid spacing:
- `n_cols = floor((x_max_mm - x_min_mm) / grid_spacing_mm) + 1`
- `n_rows = floor((y_max_mm - y_min_mm) / grid_spacing_mm) + 1`
- Grid point (i, j) at `(x_min_mm + i × grid_spacing_mm, y_min_mm + j × grid_spacing_mm)`

Emit `photometric_inputs.grid_metadata.point_count = n_cols × n_rows`.

### Step 6 — Compute per-point illuminance (LM-63 distribution + inverse-square + cosine law)

For each grid point `(x_g, y_g)` at working plane height `h_wp`:

```
E_point = Σ over each luminaire L of:
    I(θ_L, φ_L) × cos³(θ_L) / d_L²
```

Where:
- `θ_L` = angle from luminaire's downward axis to the line from luminaire to grid point
- `φ_L` = azimuth angle around luminaire's downward axis
- `I(θ, φ)` = luminous intensity from the IES file's distribution table (interpolated)
- `d_L` = distance from luminaire to grid point (3D Euclidean)
- `cos³(θ_L)` = combines (a) cosine for projected area on horizontal task plane and
  (b) inverse-square distance attenuation along the angled path

Plus inter-reflection contribution per CIBSE LG7 §6.2 simplification:
```
E_indirect ≈ E_direct × (ρ_avg / (1 - ρ_avg)) × FF
```
Where `ρ_avg = (ρ_ceiling + ρ_wall + ρ_floor) / 3` and `FF` is a form-factor approximation. **[ASSUMPTION: FF≈0.3 for typical office geometry (CIBSE LG7 §6.2 illustrative); runtime calc.lumen_grid_solver computes geometry-specific FF from explicit room/luminaire/task plane geometry]**. The skill emits the simplification in IR `_form_factor_approximation` field for engineer audit; runtime's geometry-specific result overrides at calc time.

Emit `illuminance_grid[]` as flat list of `{x_mm, y_mm, illuminance_lux}` per grid point.

Compute scalar summaries:
- `achieved_avg_illuminance_lux = mean(illuminance_grid[].illuminance_lux)`
- `achieved_min_illuminance_lux = min(...)`
- `achieved_max_illuminance_lux = max(...)`

### Step 7 — Compute U₀ uniformity

```
achieved_uniformity_u0 = achieved_min_illuminance_lux / achieved_avg_illuminance_lux
```

Per BS EN 12464-1 §4.4 + Table 5.3, target U₀ varies by room_type:
- Office / classroom / consulting / ward: 0.6
- Drawing office / fine assembly: 0.7
- Circulation (corridor, escape route, plantroom): 0.4
- Reception lobby / bathroom: 0.4

Emit `calculation_summary.uniformity_u0_target` + `achieved_uniformity_u0`.

### Step 8 — Compute UGR per CIE 117

Resolve observer positions:
1. Default 4 positions per [ugr-rules#default-observer-positions]:
   - `N`: (room.length_mm/2, room.width_mm - 1500, 1200), azimuth 180
   - `S`: (room.length_mm/2, 1500, 1200), azimuth 0
   - `E`: (room.length_mm - 1500, room.width_mm/2, 1200), azimuth 270
   - `W`: (1500, room.width_mm/2, 1200), azimuth 90
2. Plus engineer-supplied positions from `inputs.ugr_view_positions_override[]`

For each observer position, compute UGR per [ugr-rules#cie-117-formula-summary]:
```
UGR = 8 × log₁₀ [ (0.25 / Lb) × Σ_over_luminaires_in_FOV (L²ω / p²) ]
```

Where:
- `L` = luminance of the luminaire as seen from the observer (cd/m²)
- `ω` = solid angle subtended by the luminaire at the observer (sr)
- `p` = Guth position index from CIE 117 Annex A tables (depends on angle from line of sight)
- `Lb` = average background luminance computed from room surfaces + their illuminance

**Note on `p` symbol**: In this Step 8, `p` is the **Guth position index** (dimensionless, per CIE 117 Annex A) — distinct from the **grid spacing `p`** (in mm) used in Step 4. The CIE 117 formula's `p²` term in the denominator weights luminaires by their angular position relative to the observer's line of sight; it has nothing to do with the BS EN 12464-1 §6.2 grid resolution.

The runtime `calc.lumen_grid_solver` implements the full UGR formula with IES luminance
distribution + numerical Σ over visible luminaires + position-index lookup. Skill emits the
formula structure for engineer review.

Emit `ugr_results[]` array. Compute `max_ugr_across_view_positions = max(ugr_results[].ugr_value)`.

UGR limit from [ugr-rules#per-room-type-limits] per room.room_type. Emit
`calculation_summary.ugr_limit`.

### Step 9 — Invoke calc.lumen_grid_solver

Skill emits IR with calc inputs filled + outputs marked `tool_call_pending: true`.
Runtime detects the pending flag + calls `calc.lumen_grid_solver` with:
- room geometry (from upstream lighting-layout intent)
- luminaire positions + types
- IES file paths
- grid metadata (task_area_bounds + grid_spacing_mm)
- reflectances
- UGR observer positions

Runtime populates:
- `illuminance_grid[].illuminance_lux` per point
- `ugr_results[].ugr_value` per observer
- All scalar summaries in `calculation_summary`
- Sets `tool_call_pending: false`
- Sets `_calc_engine_version` string (e.g. "calc.lumen_grid_solver 1.0")

Skill validator (INV-09 in B.2) verifies `tool_call_pending == false` AND
`_calc_tool == "calc.lumen_grid_solver"` after runtime returns.

### Step 10 — Verify achieved-vs-target + populate non_compliance_flags

Compute compliance:
- `INV-01 check`: `achieved_min_illuminance_lux >= target × 0.7`
- `INV-02 check`: `achieved_uniformity_u0 >= uniformity_u0_target`
- `INV-03 check`: `max_ugr_across_view_positions <= ugr_limit`

For each FAIL: append non_compliance_flags entry with `severity: critical`, message
citing the specific deficit, reference to the relevant BS EN 12464-1 clause.

Set `calculation_summary.compliant = (all 3 checks PASS)`.

### Step 11 — Emit photometric_inputs.reflectances

If `inputs.reflectance_override` supplied: use it with `_source: "engineer_supplied_override"`.
Else: inherit from upstream lighting-layout `calculation_summary.assumptions[]` (look for
the reflectance assumption line); if absent, use room-type-typical defaults:
- Office / meeting / classroom / consulting: 0.7 / 0.5 / 0.2
- Industrial / warehouse: 0.5 / 0.3 / 0.2
- External / plantroom: 0.3 / 0.3 / 0.2

Set `_source` to either `"lighting-layout assumptions[N]"` (when inherited) or
`"room_type_typical_default_per_CIBSE_LG7"` (when defaulted).

### Step 12 — Emit IR + intent payload

Assemble the full IR per `schemas/photometric-analysis-ir.schema.json`. Required blocks:
drawing_type, version, mode, room, consumed_intents, photometric_inputs, calculation_summary,
illuminance_grid (when mode=full_analysis), ugr_results (when mode=full_analysis),
rationale, invariants.

Emit intent payload per `schemas/photometric-grid-intent.schema.json` as a separate
intent-out.json file. FLAT shape (no envelope wrap) per spec §5.2 + D3.B.4 fix-pass
precedent. Carry the 10 scalar fields + ies_source_summary.

### Step 13 — Populate invariants[]

Per the 9 INVs in `prompts/validator.md`:
- For each INV, evaluate the rule against the populated IR
- Emit entry with `{id, passes, severity, evidence}` where evidence ≥20 chars + ≤800 chars
  + cites specific values from this IR (not boilerplate)
- All 9 INVs MUST be present (numeric order INV-01 .. INV-09)

Examples PASS INV-01 .. INV-09 when achieved values meet targets + all metadata populated.
Examples that demonstrate failure modes (uniformity-fail, ugr-fail) carry `passes: false`
+ severity HIGH on the relevant INVs with evidence citing the actual deficit.

## Cascade contract — downstream consumers

This skill's intent payload is consumed by:
- `lighting-layout` INV-11 (per lighting-layout/prompts/validator.md post-D3) — confirms
  per-point illuminance meets BS EN 12464-1 task-area minima
- `emergency-lighting` (Wave 3) — reuses calc.lumen_grid_solver for escape-route + anti-panic
  point grids
- `daylight` (Wave 4) — reuses calc.lumen_grid_solver for daylight+electric integration

Honest disclosure: skill ships IR + cascade contract; runtime ships pixels + numbers per
[[runtime-project-boundary]].
