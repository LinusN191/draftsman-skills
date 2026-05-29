# photometric-analysis v1.0.0 Design Spec

**Date:** 2026-05-30
**Sprint:** Wave 1 of the lighting skill family roadmap (`docs/superpowers/specs/2026-05-29-lighting-cluster-roadmap.md`)
**Target skill:** `electrical/photometric-analysis/` (existing v0.1.0 stub since 2026-05-25 — extends to v1.0.0)
**Status:** stub → **production**
**Plan output:** `docs/superpowers/plans/2026-05-30-photometric-analysis-sprint.md` (next step, after user approves this spec)
**Predecessor:** Sprint D3 (lighting-layout v1.4.0) shipped 2026-05-29 — see `[[sprint-D3-shipped]]`. INV-11 placeholder added in D3 awaits the cascade contract this skill provides.
**Parallel skill:** `special-locations` v1.0 (Wave 1 second deliverable; brainstormed in a separate session).

---

## 1. Background

D3 closed the bad-CAD-output bugs in lighting-layout but the maturity audit surfaced 10 dimensions not yet covered. The cluster roadmap classified photometric verification (point-grid illuminance + uniformity U₀ + UGR) as a companion skill — its own engineering identity, own standards stack (CIBSE LG7 + BS EN 12464-1 §6.6 + CIE 117 + LM-63), shared calc primitive `calc.lumen_grid_solver` consumed by 3 downstream skills (this skill + emergency-lighting Wave 3 + daylight Wave 4).

This sprint builds the skill end-to-end + retrofits the 7 existing lighting-layout examples to consume its intent (closes INV-11 cascade gap that D3 left as a placeholder).

## 2. Architecture decisions (6 locked from brainstorming)

### 2.1 Scope tier — Full v1.0
IES files REQUIRED per luminaire type. Skill refuses computation without. No fallback to ontology UF approximation. Always DIALux-grade per CIE 117.

**Why:** the maturity audit specifically called out U₀ + UGR as gaps lumen-method alone cannot fill. Approximate output that gets mistaken for verified output is the worst-case failure mode (the bad CAD image showed exactly this class of bug).

### 2.2 IES file ingestion — filesystem path
`inputs.photometric_ies_paths[]` carries `{luminaire_type, path, _source}` per type. Matches DIALux/AGi32/Relux industry practice. Examples ship reference IES files under `shared/photometric/ies/` (engineer_typical_C2 disclosure per D2.3 pattern).

### 2.3 Grid resolution — BS EN 12464-1 §6.2 adaptive
`p = 0.2 × 5^log₁₀(d/0.2)` clamped to [50, 1000] mm where `d` = longer task-area dimension. Matches the standard's intent (denser grid in small task areas, sparser in large open spaces). INV-5 enforces formula adherence within ±50 mm tolerance.

### 2.4 UGR view positions — hybrid (CIE 117 defaults + engineer override)
Skill auto-emits 4 default observer positions per CIE 117 (one per wall facing inward at 1.2m). Engineer adds project-specific positions (workstations / control rooms / display-facing observers) via `inputs.ugr_view_positions_override[]`.

### 2.5 Output shape — flat list
`illuminance_grid[]` is a flat array of `{x_mm, y_mm, illuminance_lux}` triples. Self-describing, supports future non-rectangular task areas, easy to filter. Trade-off: ~3× larger JSON than 2D array; accepted for flexibility.

### 2.6 IES retrofit — single shared reference library
8 reference IES files at `shared/photometric/ies/` (LED_PANEL_600 + 4500 lm + 3500 lm variants + LED_DOWNLIGHT + HIGHBAY + LINEAR_LED + EMERGENCY + HALOGEN_DOWNLIGHT). All 7 existing lighting-layout examples retrofitted in Wave 1 (NOT deferred). All files flagged `verification_status: engineer_typical_C2`.

## 3. Skill identity

| Field | Value |
|---|---|
| name | `photometric-analysis` |
| path | `electrical/photometric-analysis/` |
| version | `0.1.0` (stub) → `1.0.0` (production) |
| status | `stub` → `production` |
| discipline | electrical |
| skill type | calc-primitive wrapper (wraps `calc.lumen_grid_solver` runtime tool) |
| chat_type | `calculation` |
| standards stack | BS EN 12464-1:2021 §4.4 + §6.2 + §6.6 + Table 5.3; ANSI/IES LM-63-2002; CIE 117; CIBSE LG7 §6 |
| consumes_intents | `lighting-layout.intent` (room + luminaires + types) |
| produces_intents | `photometric_grid.intent` (consumed by lighting-layout INV-11 + emergency-lighting + daylight) |
| runtime tool | `calc.lumen_grid_solver` (existing — contract at `shared/calculations/lighting/lumen-grid-solver.json`) |

## 4. Inputs taxonomy (`inputs.json`)

5 items:

### 4.1 `lighting_layout_intent_path` (required)
Path to upstream lighting-layout intent-out.json. Entry-point. In runtime cascade context auto-populated by manifest; in standalone context engineer-supplied.

### 4.2 `photometric_ies_paths` (required, struct_list)
Per-luminaire-type IES file paths.
- `luminaire_type` (string, must match upstream `lighting-layout.luminaire_type.symbol`)
- `path` (string, filesystem path to LM-63 file, typically `shared/photometric/ies/<type>.ies`)
- `_source` (string ≥20 chars, provenance per D2.3 pattern: manufacturer + product code + retrieval date + verification_status)

### 4.3 `ugr_view_positions_override` (optional, struct_list)
Engineer-supplied observer positions extending the 4 CIE 117 defaults.
- `label` (string, e.g. "Operator desk A1")
- `x_mm`, `y_mm`, `height_mm` (default 1200), `view_azimuth_deg`

### 4.4 `task_area_override` (optional, struct)
Override default task area (room interior minus 500 mm border) for partial-room task areas.
- `x_min_mm`, `y_min_mm`, `x_max_mm`, `y_max_mm`

### 4.5 `reflectance_override` (optional, struct)
Override room-type-typical reflectances (ceiling/wall/floor) when verified surface measurements available.

## 5. Output IR + intent payload

Two-layer output:

### 5.1 Full IR (`output.json`)
Complete photometric analysis with per-point grid + UGR results + provenance. Schema at `electrical/photometric-analysis/schemas/photometric-analysis-ir.schema.json`. Top-level required: `drawing_type`, `version`, `mode`, `room`, `consumed_intents`, `photometric_inputs`, `calculation_summary`, `illuminance_grid`, `ugr_results`, `rationale`, `invariants`.

Mode field: `full_analysis` (default — produces per-point grid + UGR) vs `screening_only` (scalar target-vs-predicted only; for early-design Part L pre-check). Mirrors lighting-layout's `mode: full_drawing | calc_only`.

Key blocks:
- `consumed_intents.lighting_layout` — upstream intent reference + version
- `photometric_inputs.ies_files[]` — per-luminaire-type IES path + provenance + parsed_summary
- `photometric_inputs.grid_metadata` — task_area_bounds, grid_spacing_mm, grid_spacing_formula citation, point_count
- `photometric_inputs.reflectances` — ceiling/wall/floor with `_source`
- `calculation_summary` — target_illuminance_lux, uniformity_u0_target, ugr_limit, achieved_avg, achieved_min, achieved_max, achieved_uniformity_u0, max_ugr_across_view_positions, compliant, non_compliance_flags[], tool_call_pending=false, `_calc_tool: "calc.lumen_grid_solver"`
- `illuminance_grid[]` — flat list per Q5 of {x_mm, y_mm, illuminance_lux} (288 entries typical for 10×8m office)
- `ugr_results[]` — per observer position: `{label, position{x,y,h}, azimuth_deg, ugr_value, _source}`

### 5.2 Intent payload (`intent-out.json`) — flat shape per B.4 fix-pass precedent
Namespaced `photometric_grid.*` per roadmap §2.3. Carries scalar summary fields downstream consumers need:
- `achieved_avg_illuminance_lux`, `achieved_min_illuminance_lux`, `achieved_uniformity_u0`
- `ugr_max`, `ugr_target`
- `uniformity_target`, `target_illuminance_lux`, `task_area_compliant`
- `grid_point_count`
- `ies_source_summary.{all_verified, verification_status_lowest}`

Schema at `electrical/photometric-analysis/schemas/photometric-grid-intent.schema.json`.

## 6. Validator INV catalogue (9 INVs in `prompts/validator.md`)

| ID | Severity | Rule | Catches |
|---|---|---|---|
| INV-1 | HIGH | `achieved_min_illuminance_lux ≥ target_illuminance_lux × 0.7` per BS EN 12464-1 Table 5.3 | Cold corners (lumen-method passes avg but min-point fails standard) |
| INV-2 | HIGH | `achieved_uniformity_u0 ≥ uniformity_u0_target` (default 0.6 office task, 0.4 circulation per Table 5.3) | Spotty distribution (avg passes, min/avg ratio doesn't) |
| INV-3 | HIGH | `max_ugr_across_view_positions ≤ ugr_limit` per BS EN 12464-1 Table 5.3 | Glare hot-spots avg-only calc misses |
| INV-4 | HIGH | Every `luminaire_type.symbol` in upstream lighting-layout MUST have matching `photometric_inputs.ies_files[]` entry | Missing IES files — Full v1.0 refuses approximate |
| INV-5 | HIGH | `grid_spacing_mm` matches BS EN 12464-1 §6.2 adaptive formula ±50 mm tolerance | Wrong-resolution grid |
| INV-6 | HIGH | `illuminance_grid[].length == grid_metadata.point_count` AND every point inside `task_area_bounds` AND no duplicate (x_mm, y_mm) | Grid shape inconsistency |
| INV-7 | MEDIUM | `ugr_results[]` carries ≥4 entries with `_source: cie_117_default` plus any engineer overrides | Missing default UGR observers |
| INV-8 | MEDIUM | Every `ies_files[]._source` ≥20 chars AND `verification_status` enum match | Missing provenance (D2.3 honest-disclosure pattern) |
| INV-9 | HIGH | `tool_call_pending == false` AND `_calc_tool == "calc.lumen_grid_solver"` | Phantom IRs never invoked runtime calc |

Cross-skill consequence: INV-1, INV-2, INV-3 failures cascade upstream to lighting-layout INV-11.

## 7. Reviewer D-checks (5 in `prompts/reviewer.md`)

| ID | Check | Trigger |
|---|---|---|
| D-1 | Achieved-avg-vs-target headroom reasonable (5–30% range, not over-provisioned) | always |
| D-2 | IES file age + manufacturer plausibility per `_source` provenance | when `verification_status: engineer_typical_C2` |
| D-3 | UGR-vs-task-type fit per BS EN 12464-1 Table 5.3 (e.g. drawing office ≤16 vs general office ≤19) | when `room_type ∈ {drawing_office, technical_drawing, fine_assembly, precision_work}` |
| D-4 | Reflectance values vs room_type typical (flag deviations >0.1 without explanation) | when `reflectance_override` supplied |
| D-5 | Task-area placement vs luminaire-coverage envelope (flag gaps in coverage) | when `task_area_override` supplied |

## 8. Shared IES library

New shared resource at `shared/photometric/ies/`. Mirrors `shared/calculations/`, `shared/standards/`, `shared/symbols/` shape.

### 8.1 Folder structure
```
shared/photometric/
├── README.md                          # provenance + verification_status policy
├── ies/
│   ├── LED_PANEL_600.ies              # 6000 lm variant (used by uk-open-plan-office-10x8-dali)
│   ├── LED_PANEL_600-4500lm.ies       # used by office-open-plan + uk-multi-entrance-classroom
│   ├── LED_PANEL_600-3500lm.ies       # used by uk-undersized-lighting-vs-target
│   ├── LED_DOWNLIGHT.ies              # used by reception-lobby
│   ├── HIGHBAY.ies                    # used by warehouse-highbay
│   ├── LINEAR_LED.ies                 # reference (not used in current examples)
│   ├── EMERGENCY.ies                  # used by warehouse-highbay Z3
│   └── HALOGEN_DOWNLIGHT.ies          # used by uk-part-l-fail-incandescent
└── ies-provenance.json                # machine-readable per-file provenance
```

### 8.2 Provenance file
`ies-provenance.json` — machine-readable schema-validated provenance. INV-8 reads this to verify each example's `_source` string traces to a known reference.

### 8.3 Honest disclosure policy
ALL files flagged `verification_status: engineer_typical_C2` per D2.3 pattern. README documents substitution policy: engineer-of-record MUST substitute project-specific IES files before final design freeze. NOT project-deliverable.

### 8.4 Future extensibility
- daylight (Wave 4) adds `shared/photometric/sky-models/` (CIE Standard Overcast Sky files)
- emergency-lighting (Wave 3) reuses `EMERGENCY.ies` + adds maintained-luminaire variants
- Pattern extends cleanly across 6+ skills

## 9. Examples (3 minimum per CLAUDE.md skill standards)

### 9.1 `uk-open-plan-office-10x8-dali-photometric/` (happy path verification)
Consumes D3 canonical lighting-layout example. Demonstrates standard cascade. All 9 INVs PASS. Achieved avg ~545 lux (target 500), U₀ ~0.62, max UGR ~18.4. 238-point grid.

### 9.2 `uk-office-uniformity-fail-perimeter-cold-spots/` (INV-1 + INV-2 FAIL demo)
Synthetic 10×8m office, 16 LED_PANEL_600 in 4×4 grid CLUSTERED in central 6×5m (instead of even 4×5). Achieved avg ~582 lux (lumen-method-style PASS) BUT achieved_min ~210 lux at corners (INV-1 FAIL), U₀ ~0.36 (INV-2 FAIL). Proves photometric catches what lumen-method INV-1 cannot.

### 9.3 `uk-drawing-office-strict-ugr/` (INV-3 + D-3 FAIL demo)
12×9m drawing office, 24 LED_PANEL_600 in 4×6 grid, target 750 lux, UGR limit 16 (per BS EN 12464-1 Table 5.3 row 5.34). max_ugr ~17.8 > 16 (INV-3 FAIL). D-3 reviewer fires per room_type stricter UGR.

## 10. lighting-layout INV-11 cascade integration

The binding glue between this skill and Wave-0 D3 lighting-layout.

### 10.1 lighting-layout manifest gains `consumes_intents[]`
```json
"consumes_intents": [{
  "name": "photometric_grid",
  "producer_skill": "photometric-analysis",
  "version_pin": ">=1.0.0",
  "trigger": "mode == 'full_drawing'",
  "consumed_fields": [
    "achieved_avg_illuminance_lux", "achieved_min_illuminance_lux",
    "achieved_uniformity_u0", "ugr_max", "task_area_compliant"
  ]
}]
```

### 10.2 lighting-layout IR gains `consumed_intents.photometric_grid` block
Schema extension in `shared/schemas/electrical/lighting-layout-ir.schema.json`. Required when `mode == full_drawing` (allOf clause extends D3.A.3 mode-conditional).

### 10.3 lighting-layout INV-11 rewritten (D3 placeholder → real rule)
`electrical/lighting-layout/prompts/validator.md` INV-11:
- Severity HIGH when mode == full_drawing; N/A when calc_only
- Rule (4 sub-checks):
  1. `consumed_intents.photometric_grid` present (cascade triggered + resolved)
  2. `consumed_intents.photometric_grid.payload.task_area_compliant == true` (photometric INV-1+2+3 all PASS upstream)
  3. `consumed_intents.photometric_grid.payload.achieved_avg_illuminance_lux >= calculation_summary.target_illuminance_lux` (photometric confirms lighting-layout target is met)
  4. Flag cascading: if `consumed_intents.photometric_grid.payload.non_compliance_flags[]` is non-empty, lighting-layout's own `calculation_summary.non_compliance_flags[]` MUST include each flag (with provenance attribution to `photometric-analysis`). No silent suppression.

### 10.4 Retrofit of 7 existing lighting-layout examples
All 7 examples retrofitted in Wave 1 sprint:
- input.json gains `photometric_ies_paths[]` per the table below
- output.json + intent-out.json gain `consumed_intents.photometric_grid` block
- INV-11 evidence rewritten from D3 placeholder to cite actual photometric payload

| lighting-layout example | luminaire_type | IES file |
|---|---|---|
| office-open-plan | LED_PANEL_600 (4500 lm) | LED_PANEL_600-4500lm.ies |
| reception-lobby | LED_DOWNLIGHT | LED_DOWNLIGHT.ies |
| warehouse-highbay | HIGHBAY + EMERGENCY | HIGHBAY.ies + EMERGENCY.ies |
| uk-undersized-lighting-vs-target | LED_PANEL_600 (3500 lm) | LED_PANEL_600-3500lm.ies |
| uk-multi-entrance-classroom | LED_PANEL_600 (4500 lm) | LED_PANEL_600-4500lm.ies |
| uk-part-l-fail-incandescent | HALOGEN_DOWNLIGHT | HALOGEN_DOWNLIGHT.ies |
| uk-open-plan-office-10x8-dali | LED_PANEL_600 (6000 lm) | LED_PANEL_600.ies |

## 11. Files modified + created

### Modified
- `electrical/photometric-analysis/skill.manifest.json` — stub → production
- `electrical/photometric-analysis/README.md` — stub content → real skill body
- `electrical/lighting-layout/skill.manifest.json` — add `consumes_intents[]`
- `electrical/lighting-layout/prompts/validator.md` — INV-11 placeholder → real rule
- `shared/schemas/electrical/lighting-layout-ir.schema.json` — add `consumed_intents` block + extend `allOf` for full_drawing
- `electrical/lighting-layout/examples/<7 examples>/input.json` — add `photometric_ies_paths[]`
- `electrical/lighting-layout/examples/<7 examples>/output.json` — add `consumed_intents.photometric_grid` + rewrite INV-11 evidence
- `electrical/lighting-layout/examples/<7 examples>/intent-out.json` — add `consumed_intents.photometric_grid`

### Created
- `electrical/photometric-analysis/inputs.json` — 5 items
- `electrical/photometric-analysis/schemas/photometric-analysis-ir.schema.json`
- `electrical/photometric-analysis/schemas/photometric-grid-intent.schema.json`
- `electrical/photometric-analysis/prompts/generator.md` (~600 lines)
- `electrical/photometric-analysis/prompts/validator.md` (~350 lines — 9 INVs)
- `electrical/photometric-analysis/prompts/reviewer.md` (~200 lines — 5 D-checks)
- `electrical/photometric-analysis/rules/*.yaml` — grid-spacing-rules, ugr-rules, ies-provenance-rules (per A.2 pattern)
- `electrical/photometric-analysis/ontology/*.json` — minimal (mostly inherits from lighting-layout ontology)
- `electrical/photometric-analysis/CHANGELOG.md`
- `electrical/photometric-analysis/examples/<3 examples>/{input,output,intent-out}.json + reasoning.md` (3 × 4 = 12 files)
- `electrical/photometric-analysis/examples/cascade-<lighting-layout-example-name>/{input,output,intent-out}.json + reasoning.md` × 7 — one photometric-analysis run cascading from each existing lighting-layout example. Directory names mirror the upstream example exactly with `cascade-` prefix (e.g. `cascade-office-open-plan/`, `cascade-warehouse-highbay/`, ..., `cascade-uk-open-plan-office-10x8-dali/`)
- `electrical/photometric-analysis/evals/eval-NN-*.yaml` (≥5 per CLAUDE.md)
- `shared/photometric/README.md`
- `shared/photometric/ies/<8 files>.ies` (~80 KB total)
- `shared/photometric/ies-provenance.json`
- `shared/schemas/core/photometric-provenance.schema.json` (validates ies-provenance.json)

## 12. Gate targets

- `validate-examples.py`: `236 → ~257` (+21 — computed below):
  - **+6** from 3 new photometric-analysis examples × 2 validated files each (Pass 1 output.json + Pass 4 intent-out.json)
  - **+14** from 7 cascade retrofit examples × 2 validated files each
  - **+1** from new photometric-analysis `inputs.json` (Pass 3)
  - input.json + reasoning.md per example not directly validated; IES files + README not validated
  - Exact final number set by implementer; the +21 is a planning estimate
- `functional_audit.py`: `1 finding unchanged` (disclosed motor-superposition oracle FP on `fault-level/us-industrial-with-motors/MCC-1`, disclosed in Sprint D1.1)

## 13. Out of scope (deferred to v2.0 or other skills)

- **Non-rectangular task areas** (L-shaped offices, atriums with cutouts) — flat-list output supports this structurally but v1.0 examples + INV checks assume rectangular task area
- **Climate-based daylight contribution** to point-grid — daylight skill Wave 4 owns this; v1.0 is electric-light-only point-grid
- **CCT mixing / colour-rendering point-grid** — single CCT per luminaire assumed; mixed-CCT layouts deferred
- **Manufacturer-IES URL ingestion** — v1.0 filesystem path only; v2.0 may extend to URL fetch
- **3D mounting variation** (different ceiling heights per zone) — v1.0 assumes single mounting height per luminaire_type
- **Outdoor / facade photometric** — `external-lighting` skill (separate)
- **Emergency-specific point grid (escape route ≥1 lux centre line, anti-panic ≥0.5 lux floor)** — emergency-lighting skill Wave 3 (reuses this skill's calc primitive)
- **Daylight + electric integration for LENI** — daylight + energy-leni skills Waves 4
- **Live calc execution** — runtime owns `calc.lumen_grid_solver` per `[[runtime-project-boundary]]`; skill emits IR with `tool_call_pending: false` only after runtime invocation

## 14. Process lessons applied from D2.3 + D3

- Every clause citation cross-checked against `shared/standards/electrical/` BEFORE plan ships (Reg 559 + §714 lessons)
- Two-stage Opus review per task — implementer + spec compliance + code quality + fix-pass if needed
- Pre-ship Sonnet verification fence — catches drift per-task reviewers miss
- `verification_status: engineer_typical_C2` honest-disclosure pattern applied to ALL shared IES files
- Schema additions are additive — existing v1.3.x lighting-layout consumers ignore new fields gracefully

## 15. Cross-references

- Cluster roadmap: `docs/superpowers/specs/2026-05-29-lighting-cluster-roadmap.md` §3.1 + §5 Wave 1 + §6
- Sprint D3 shipped: `[[sprint-D3-shipped]]`
- Within-skill depth plan: `[[within-skill-depth-plan]]`
- Build strategy: `[[build-strategy-breadth-first]]`
- Model selection: `[[feedback-no-haiku-sonnet-opus-only]]`
- No-trim policy: `[[feedback-no-trim-non-consequential]]`
- Runtime boundary: `[[runtime-project-boundary]]`
- Calc contract: `shared/calculations/lighting/lumen-grid-solver.json` (existing stub — expanded by this sprint)
- Pattern parent: `electrical/cable-sizing/` (calc-primitive skill shape) + `electrical/lighting-layout/` (downstream consumer shape)
