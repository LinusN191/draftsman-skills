# Sprint D3 — Lighting-Layout Depth Design Spec

**Date:** 2026-05-28
**Sprint:** D3 (last within-skill-depth sprint; the original D3 small-power depth is pushed to D4)
**Target skill:** `electrical/lighting-layout/`
**Version bump:** `v1.3.1 → v1.4.0` (additive content + new INVs; backward-compatible IR additions; existing v1.3.x consumers unaffected)
**Status:** stays `production`
**Plan output:** `docs/superpowers/plans/2026-05-28-sprint-D3-lighting-layout-depth-sprint.md` (next step, after user approves this spec)

---

## 1. Background

End-to-end test of the live lighting-layout skill (prompt: `10m × 8m open-plan office, 2.7m suspended ceiling, 500 lux to BS EN 12464-1, 4000K 6000lm LED panels recessed into 600mm grid, UK new-build BS 7671, DALI controls, drawing L-001 P1 1:50 A3`) produced a CAD output with multiple visible bugs:

- Z-pattern circuit daisy-chain (two diagonals crossing between rows)
- 4th column of luminaires sitting on the wall boundary (no edge clearance)
- No homerun arrow to the distribution board
- No luminaire schedule
- No title block, no dimensions, no scale bar
- Visibly uneven row spacing
- 12-luminaire grid where lumen-method math justifies a different count

A subsequent skill audit identified content gaps across 5 categories. The audit's Top 5 ranked fixes are addressed here, plus 3 structural issues the audit missed (circuit topology model, stub validator/reviewer prompts, intent payload extension for downstream consumers).

This sprint closes all of those gaps + re-tests the user's verbatim prompt by building it as a new canonical example.

## 2. Current state (verified against repo files)

Per file inspection:

| File | Lines | State |
|---|---|---|
| `prompts/generator.md` | 910 | Substantial but with content gaps per audit |
| `prompts/validator.md` | 4 | **STUB** — "See prompts/generator.md" |
| `prompts/reviewer.md` | 4 | **STUB** — "See prompts/generator.md" |
| `inputs.json` | 170 | Substantial; discovery gaps per audit §1 |
| `schemas/lighting-layout-ir.schema.json` | 6 | `$ref` redirect to `shared/schemas/electrical/lighting-layout-ir.schema.json` |
| `shared/schemas/electrical/lighting-layout-ir.schema.json` | 512 | Canonical IR schema |
| `schemas/lighting-layout-intent.schema.json` | 63 | Thin — doesn't carry circuit topology or homerun |
| `ontology/luminaire-types.json` | 10 | Shape + dims only; **no photometric data** |
| `ontology/switching-types.json` | 9 | 4 types; no electrical ratings, no symbol mapping |
| `rules/switching-rules.yaml` | 9 | Skeleton; says `1200mm AFF` (drift with prompt's 1350mm) |
| `rules/placement-rules.yaml` | 9 | Skeleton; not referenced from prompt |
| `rules/spacing-rules.yaml` | 7 | Skeleton |
| `rules/control-rules.yaml` | 13 | Skeleton |
| `rules/emergency-rules.yaml` | 7 | Skeleton; no backing ontology |
| `examples/office-open-plan/output.json` | 367 | Full example (canonical) |
| `examples/reception-lobby/output.json` | 104 | **Abbreviated stub** |
| `examples/warehouse-highbay/output.json` | 89 | **Abbreviated stub** |
| `examples/*/intent-out.json` | — | Only office-open-plan has one |
| `evals/eval-*.yaml` | 8 evals | All schema-pass; no example exercises the failure mode (lux below minimum, missing lumen data, etc.) |

## 3. Architecture decisions (5 locked)

### 3.1 Photometric data — hybrid

`ontology/luminaire-types.json` carries reference UF / SHR_max / LLMF defaults per luminaire type. `inputs.json` gains an optional `photometric_override` block where engineers can supply a manufacturer-specific IES/LDT-derived set. Generator lookup order:

```
uf = inputs.photometric_override?.uf_table?.[RI]?.[refs]
     ?? ontology[luminaire_type].photometric.uf_table[RI][refs]
shr_max = inputs.photometric_override?.shr_max
          ?? ontology[luminaire_type].photometric.shr_max
llmf = inputs.photometric_override?.llmf_at_design_hours
       ?? ontology[luminaire_type].photometric.llmf_schedule[environment][design_hours]
```

IR records which path won in `selection._source` (string citing either ontology citation or input override `_source`).

**Rationale:** rapid iteration works without IES files (ontology defaults); manufacturer-specific projects supply override; INV-8 enforces source resolution (no improvisation).

### 3.2 Circuit topology — hybrid zones + rows + homerun

IR `lighting_layout-ir.schema.json` gains `zones[]` block (Part L semantics):

```json
"zones": [{
  "zone_id": "Z1",
  "zone_type": "perimeter",  // perimeter | interior | task | emergency
  "control": "daylight_linked",  // daylight_linked | occupancy | manual | dali_master
  "luminaire_ids": ["L01", "L02", "L03", "L04"],
  "circuits": [{
    "circuit_id": "C-L01",
    "row_index": 1,
    "luminaire_ids": ["L01", "L02", "L03", "L04"],
    "homerun_endpoint": {"x_mm": 200, "y_mm": 0},
    "total_load_w": 240,
    "ocpd_rating_a": 6
  }]
}]
```

**Rationale:** zones surface Part L grouping for downstream `db-layout` consumption; per-zone `circuits[].row_index` + `luminaire_ids` kills the Z-pattern bug structurally (INV-4 enforces same-row-or-adjacent); `homerun_endpoint` makes the renderer draw a real arrow to the DB; `total_load_w` + `ocpd_rating_a` let the validator catch overloaded circuits (INV-5).

### 3.3 Rules YAML as single source of truth

All 5 `rules/*.yaml` files expand from 7-13 line skeletons to full structured documents:

```yaml
id: switching-rules
description: Switch placement and zoning per BS 7671 §553 + IET OSG
rules:
  - id: switching-rules#height
    value: {height_mm: 1200, tolerance_mm: 50}
    citation: "BS 7671:2018+A2:2022 §553.1.1 + IET OSG App E §E1.2"
    rationale: "Industry-standard reach height for adults..."
  - id: switching-rules#latch-side
    value: {offset_mm_from_frame: 200, side: "latch", door_swing_aware: true}
    citation: "IET OSG App E §E1.4"
    rationale: "Switch on latch side avoids reaching across door swing..."
```

Generator prompt cites rule IDs instead of inlining values:

```markdown
Step 12: Place switch per rule [switching-rules#latch-side] at the offset
declared in [switching-rules#height]. Resolve door_swing from inputs.entrance_positions[].
```

**Rationale:** zero-drift by design; one place to change a rule; rules become runtime-consumable (validator can parse YAML and verify generator output against the same values).

### 3.4 End-to-end re-test gate — canonical example

New example `examples/uk-open-plan-office-10x8-dali/` built from the user's verbatim original prompt:

- `input.json`: 10×8m, 2.7m ceiling, 500 lux, 4000K, 6000 lm LED panels, 600mm grid, DALI, no glazing, drawing L-001 rev P1, A3 1:50, UK new-build
- `output.json`: full IR with 12 luminaires (3 rows × 4) in 3 zones (Z1 perimeter daylight-linked / Z2 interior occupancy / Z3 emergency self-test); 3 row circuits each with homerun to a chosen wall endpoint; DALI master switch at the entrance; full drafting furniture; all 10 INVs PASS
- `reasoning.md`: full lumen-method walk with concrete numbers — `N = (500 × 80) / (6000 × 0.67 × 0.80) = 12.4 → 12`; S/H ratio computation; circuit topology rationale; switch placement derivation; photometric source (ontology LED_PANEL_600 defaults)
- `intent-out.json`: full intent payload exercising the new zone+topology fields

**Rationale:** doubles as the canonical few-shot example future generators copy from; serves as the spec-level re-test of the user's failing prompt. Live runtime re-run stays out of scope per `[[runtime-project-boundary]]`.

### 3.5 Drafting furniture scope — lighting-layout-only

D3 ships title block + scale bar + dimensions + luminaire schedule as annotation objects inside the lighting-layout IR. Each annotation carries explicit `font_family` (Arial, fallback LiberationSans) + `font_size_pt` so the renderer's ezdxf font fallback doesn't lose tags.

Cross-skill drafting-standards harmonisation (BS 1192 + ISO 19650 + AIA + ISO 5457 + ISO 5455 layer naming) stays deferred per the existing `[[drafting-standards-deferred-sprint]]` memory. That sprint runs after the depth program completes and generalises the pattern across all drawing skills.

## 4. Phase + task breakdown (11 implementer tasks)

### Phase A — Foundations (3 tasks, sequential)

Schema + ontology + rules YAML must land before prompts can cite them.

**A.1 — Ontology backfill (Opus, ~4 hr)**

- `ontology/luminaire-types.json` (10 → ~250 lines): add `photometric` block per type (UF table indexed by RI + reflectance triplets; SHR_max; LLMF schedule by environment; `_citation` to CIBSE LG7 + BS EN 12464-1)
- `ontology/switching-types.json` (9 → ~80 lines): add electrical ratings (rated_amps, voltage), symbol mapping (DXF block name), compatible-load-types per type. Expand types: add `dali_master`, `dali_application_controller`, `daylight_sensor`, `presence_with_dimming`
- `ontology/emergency-types.json` (NEW, ~60 lines): emergency-luminaire ontology backing `rules/emergency-rules.yaml` (self-test, non-maintained, maintained, escape route, open area, high-risk task area per BS 5266-1)

**Why Opus**: regulation-driven content + photometric judgment + citation accuracy. Citation cross-check against `shared/standards/electrical/` mandatory (Reg 559 lesson from D2.3).

**A.2 — Rules YAML SoT expansion (Opus, ~3 hr)**

All 5 `rules/*.yaml` files expanded from skeleton to full structured documents. Each rule entry gains `{id, value, citation, rationale}`. Specifically resolve drift:

- `switching-rules#height` = 1200mm AFF (per BS 7671 §553.1.1; correct value, override the prompt's 1350mm)
- `placement-rules#edge_clearance` = 300mm (per BS EN 12464-1 §4.4 indirect; cite CIBSE LG7)
- `placement-rules#grid_snap` = 50mm (industry CAD convention)
- `spacing-rules#shr_max_default` = 1.5 (per CIBSE LG7; per-luminaire override via ontology)
- `control-rules`: occupancy + daylight zone requirements per Part L 2021 + BS 7671 §714

**Why Opus**: citation accuracy. Every clause cross-checked against `shared/standards/electrical/` BEFORE writing.

**A.3 — Schema extensions (Sonnet, ~3 hr)**

- `shared/schemas/electrical/lighting-layout-ir.schema.json`: add `zones[]` (per §3.2 above); add `drafting_furniture` block (title_block + scale_bar + dimensions[] + luminaire_schedule with explicit font fields); add `selection._source` field; tighten `non_compliance_flags` items to `{message, reference, severity}` objects with `additionalProperties: false`; promote `controls.part_l_assessed` to required when `is_uk_new_build == true`; add `room_type` enum (12 values: open_plan_office, cellular_office, meeting, reception, lobby, corridor, warehouse_highbay, warehouse_aisle, escape_route, bathroom, plantroom, external)
- `electrical/lighting-layout/schemas/lighting-layout-intent.schema.json` (63 → ~180 lines): extend intent payload with zones + circuits + homerun + switch positions + total_load_per_circuit for `db-layout` / `small-power` / `cable-sizing` to consume
- `inputs.json`: add `door_swing` field to `entrance_positions` (enum: `inward_latch_left | inward_latch_right | outward_latch_left | outward_latch_right | sliding`); add `lumen_type` enum (`initial | design`) required when `luminaire_lumens` supplied; add `photometric_override` optional block; tighten `controls_protocol` default per `is_uk_new_build`; add `ceiling_grid_mm` validator (enum {600, 1200} or `null`)

**Why Sonnet**: mechanical schema work; no judgment beyond structure.

### Phase B — Prompts (4 tasks, sequential)

Generator + validator + reviewer + intent payload.

**B.1 — Generator: lumen-method + S/H ratio + photometric lookup (Opus, ~4 hr)**

- Step 6 rewrite: full worked example with concrete numbers (`N = (Em × A) / (Φ × UF × MF)` walked end-to-end). Document `calc.lumen_grid_solver` output spec inline so generator can trust it
- Step 7 rewrite: explicit S/H ratio enforcement loop — compute S_x, S_y, check `≤ SHR_max × Hm`, add row/column and recalculate if exceeded. Worked example showing a fail → add column → pass cycle
- Photometric lookup procedure: override-first-then-ontology per §3.1
- Cite `spacing-rules#shr_max_default` instead of inlining 1.5
- INV-1 (HIGH): `achieved_illuminance_lux ≥ target_illuminance_lux`
- INV-2 (HIGH): `S_x ≤ SHR_max × Hm` AND `S_y ≤ SHR_max × Hm`
- INV-8 (MEDIUM): `selection._source` resolves to ontology citation or input override `_source` (no improvisation)

**Why Opus**: lumen-method judgment, worked-example arithmetic, citation accuracy.

**B.2 — Generator: circuit topology + switch placement (Opus, ~4 hr)**

- New step: Part L zone assignment (Z1 perimeter daylight-linked within 3m of glazing / Z2 interior occupancy / Z3 task / Z4 emergency). **If the room has no glazed walls** (`is_glazed_walls == false` or `entrance_positions` carries no glazed surface), Z1 perimeter is absent and the IR emits `zones[]` without a perimeter entry — INV-7 enforces consistency (perimeter zone present iff glazing exists)
- Per zone, group luminaires into rows; per row, compute `total_load_w` and verify `≤ 0.8 × ocpd_rating_a × supply_voltage_v` (e.g. `0.8 × 6A × 230V = 1104W` per 6A MCB circuit)
- Homerun: choose nearest wall endpoint to the DB; emit `homerun_endpoint {x_mm, y_mm}` per circuit
- Switch placement rewrite: extract `entrance_positions[]` from inputs; for each entrance compute switch (x, y) from `wall + offset_mm + door_swing`; emit switch on latch side per `switching-rules#latch-side` + `#height`
- INV-3 (HIGH): `switches.length ≥ entrances.length` AND each switch at correct latch_side + offset + height per rule cites
- INV-4 (HIGH): every circuit's `luminaire_ids` all sit on the same `row_index` OR adjacent rows (defined as `|row_index_a - row_index_b| ≤ 1`); no diagonal jumps across non-adjacent rows
- INV-5 (HIGH): `circuit.total_load_w ≤ 0.8 × ocpd_rating_a × supply_voltage_v` (the 80% continuous-load factor per BS 7671:2018+A2:2022 §433.1.1 + IET OSG App A continuous-load rule)
- INV-7 (MEDIUM): every luminaire belongs to exactly one zone; zone_type matches geometry (perimeter zone = within 3m of glazed wall)

**Why Opus**: topology judgment, regulation-driven zone assignment.

**B.3 — Generator: drafting furniture step (Sonnet, ~3 hr)**

- New step emitting `drafting_furniture.title_block` (project name + drawing number + revision + date + scale + sheet size — all from inputs), `scale_bar` (CAD-standard with tick marks), `dimensions[]` (room length + width as dimension lines with text), `luminaire_schedule` (table per luminaire type: ref + manufacturer + lumens + wattage + count)
- Every annotation object carries explicit `font_family` (Arial fallback LiberationSans) + `font_size_pt`
- INV-9 (MEDIUM): `drafting_furniture.{title_block, scale_bar, dimensions, luminaire_schedule}` all present with explicit font fields

**Why Sonnet**: mechanical formatting + template population.

**B.4 — Validator + reviewer prompts + intent payload wiring (Opus, ~4 hr)**

- `prompts/validator.md` (4 → ~400 lines): write full INV catalogue (10 INVs from §5 below) with rule citations, validator-action instructions, rationale paragraphs (D2-style)
- `prompts/reviewer.md` (4 → ~250 lines): D-check catalogue (D-1 photometric override sanity; D-2 OCPD rating realism; D-3 emergency lighting coverage if Part 7 §710 applies; D-4 BS EN 12464-1 task area uniformity; D-5 controls protocol fit; D-6 zone perimeter geometry)
- Wire generator to emit `intent` block populated per the new intent schema (zones + circuits + homerun + switches + total_load_per_circuit)
- INV-6 (HIGH): if `is_uk_new_build == true`: `controls.part_l_assessed == true` AND `controls.required` includes occupancy AND daylight where applicable
- INV-10 (HIGH): every schema-required field populated; `non_compliance_flags` items match object shape `{message, reference, severity}`

**Why Opus**: review-prompt content authoring + INV catalogue judgment.

### Phase C — Examples + Ship (4 tasks, sequential)

**C.1 — Promote 2 stub examples (Opus, ~3 hr)**

- `examples/reception-lobby/` (~100 → ~400 lines): full IR matching office-open-plan depth, complete reasoning.md, intent-out.json. Realistic reception scenario: 8×5m lobby, 300 lux target (BS EN 12464-1), recessed downlights on grid, 2 entrances, separate emergency lighting zone
- `examples/warehouse-highbay/` (~100 → ~400 lines): 30×20m warehouse, 200 lux aisles + 300 lux task, HIGHBAY luminaires at 8m mounting height, multi-row circuits, emergency egress lighting per BS 5266-1
- Use ontology defaults for photometric (no override). Add INV-1..INV-10 invariants entries

**Why Opus**: engineering judgment to produce realistic lobby + warehouse photometric scenarios.

**C.2 — 3 new failure-mode examples (Opus, ~4 hr)**

- `examples/uk-undersized-lighting-vs-target/`: 8×6m office sized to 12 panels when math demands 15 → `achieved_lux 380 < target 500`, INV-1 FAIL, `non_compliance_flags[]` populated with proper object shape, `part_l_assessed: false`. Tests eval-02
- `examples/uk-multi-entrance-classroom/`: 10×8m classroom with 3 entrances → 3 switches each on latch side, INV-3 verifies coverage; demonstrates door_swing-aware placement
- `examples/uk-part-l-fail-incandescent/`: legacy office with halogen downlights → efficacy fails Part L 2021, `controls.part_l_assessed: true`, `controls.part_l_compliant: false`, `non_compliance_flags` with `severity: high`. Tests eval-06

**Why Opus**: hand-walked failure-mode arithmetic + regulation citations.

**C.3 — Canonical re-test example `uk-open-plan-office-10x8-dali` (Opus, ~3 hr)**

- User's verbatim original prompt as `inputs.items[]`: 10×8m, 2.7m ceiling, 500 lux, 4000K, 6000 lm LED panels, 600mm grid, DALI, no glazing, drawing L-001 P1, A3 1:50, UK new-build
- Full IR: 12 luminaires (3×4 grid). **Note**: user's prompt says "no glazed walls" so Z1 perimeter is absent — zones reduce to Z2 interior (all 12 luminaires) + Z3 emergency (self-test luminaires per BS 5266-1 if escape route applies). 3 row circuits each with homerun to a chosen wall endpoint; DALI master switch at entrance; full drafting furniture; all 10 INVs PASS (INV-7 explicitly verifies "perimeter absent because no glazing" path)
- reasoning.md: full lumen-method walk (`N = (500 × 80) / (6000 × 0.67 × 0.80) = 12.4 → 12`), S/H ratio computation, circuit topology rationale, switch placement derivation, photometric source (ontology LED_PANEL_600 defaults)
- intent-out.json: full intent payload exercising new zone+topology fields

**Why Opus**: full canonical example for the re-test gate.

**C.4 — Sprint D3 ship (Opus orchestrator + Sonnet 12-check fence, ~3 hr)**

- 12-check verification fence (3 checks per phase + 2 cross-cutting + 1 canonical re-test):
  - Per-phase A: schema validation, ontology field presence, rules cross-references resolve
  - Per-phase B: prompt content match plan, intent emission verified, INV catalogue complete
  - Per-phase C: 6 examples gate-pass (3 promoted/new + 3 failure-mode), canonical example all INVs PASS
  - Cross-cutting: 1200mm AFF drift gone everywhere; no `{{` placeholders in any drafting-furniture SVG
  - Canonical: `uk-open-plan-office-10x8-dali` matches user's prompt verbatim + all 10 INVs PASS
- Combined CHANGELOG `[1.4.0]` entry covering A + B + C
- Manifest bump `1.3.1 → 1.4.0` + register 4 new examples in `examples[]`
- `sprint-D3-shipped.md` memory file + MEMORY.md index entry

**Why Opus orchestrator + Sonnet fence**: same pattern as D2.4. Sonnet fence cheap + deterministic; Opus orchestrator handles edge cases.

## 5. INV catalogue (final — 10 INVs)

All INVs live in `prompts/validator.md` (which is currently a 4-line stub):

| ID | Severity | Rule | Caught failure mode |
|---|---|---|---|
| INV-1 | HIGH | `achieved_illuminance_lux ≥ target_illuminance_lux` | Under-lit room (audit Top 5 #1) |
| INV-2 | HIGH | `S_x ≤ SHR_max × Hm` AND `S_y ≤ SHR_max × Hm` | Uneven spacing (audit Top 5 #2; image bug) |
| INV-3 | HIGH | `switches.length ≥ entrances.length` AND each switch at `latch_side + 200mm + 1200mm AFF` per `switching-rules#height + #latch-side` | Switch under fixture (audit Top 5 #3; image bug) |
| INV-4 | HIGH | Every circuit's `luminaire_ids` all sit on the same `row_index` OR adjacent rows; no diagonal jumps across non-adjacent rows | Z-pattern daisy-chain (image bug; audit missed) |
| INV-5 | HIGH | `circuit.total_load_w ≤ 0.8 × ocpd_rating_a × supply_voltage_v` | Overloaded lighting circuit |
| INV-6 | HIGH | If `is_uk_new_build == true`: `controls.part_l_assessed == true` AND `controls.required` includes occupancy AND daylight where applicable | Silent Part L 2021 miss |
| INV-7 | MEDIUM | Every luminaire belongs to exactly one zone; zone_type matches room geometry (perimeter zone = within 3m of glazed wall) | Zone misassignment |
| INV-8 | MEDIUM | `selection._source` resolves to either `inputs.photometric_override._source` or `ontology[type].photometric._citation` (no improvisation) | Fabricated photometric values |
| INV-9 | MEDIUM | `drafting_furniture.{title_block, scale_bar, dimensions, luminaire_schedule}` all present with explicit `font_family` + `font_size_pt` | Missing title block / unreadable annotations (audit Top 5 #4; image bug) |
| INV-10 | HIGH | Every schema-required field populated; `non_compliance_flags` items match object shape `{message, reference, severity}` | Schema drift (audit Top 5 #5) |

Plus 6 D-checks in `prompts/reviewer.md`:

| ID | Check |
|---|---|
| D-1 | Photometric override sanity — UF values plausible for luminaire type |
| D-2 | OCPD rating realism — matches load + cable + protection coordination |
| D-3 | Emergency lighting coverage — BS 5266-1 escape route requirements per Part 7 §710 if applicable |
| D-4 | BS EN 12464-1 task area uniformity (U₀ ≥ 0.6 for office task plane) |
| D-5 | Controls protocol fit — DALI for >20 luminaires, simple switch for <10, etc |
| D-6 | Zone perimeter geometry — perimeter zone width ≤ 6m and adjacent to glazed wall |

## 6. Files modified + created

### Modified

```
electrical/lighting-layout/CHANGELOG.md
electrical/lighting-layout/inputs.json
electrical/lighting-layout/ontology/luminaire-types.json
electrical/lighting-layout/ontology/switching-types.json
electrical/lighting-layout/prompts/generator.md
electrical/lighting-layout/prompts/reviewer.md
electrical/lighting-layout/prompts/validator.md
electrical/lighting-layout/rules/control-rules.yaml
electrical/lighting-layout/rules/emergency-rules.yaml
electrical/lighting-layout/rules/placement-rules.yaml
electrical/lighting-layout/rules/spacing-rules.yaml
electrical/lighting-layout/rules/switching-rules.yaml
electrical/lighting-layout/schemas/lighting-layout-intent.schema.json
electrical/lighting-layout/skill.manifest.json
electrical/lighting-layout/examples/reception-lobby/output.json
electrical/lighting-layout/examples/reception-lobby/reasoning.md
electrical/lighting-layout/examples/warehouse-highbay/output.json
electrical/lighting-layout/examples/warehouse-highbay/reasoning.md
shared/schemas/electrical/lighting-layout-ir.schema.json
```

### Created

```
electrical/lighting-layout/ontology/emergency-types.json
electrical/lighting-layout/examples/reception-lobby/intent-out.json
electrical/lighting-layout/examples/warehouse-highbay/intent-out.json
electrical/lighting-layout/examples/uk-undersized-lighting-vs-target/{input,output,intent-out}.json + reasoning.md
electrical/lighting-layout/examples/uk-multi-entrance-classroom/{input,output,intent-out}.json + reasoning.md
electrical/lighting-layout/examples/uk-part-l-fail-incandescent/{input,output,intent-out}.json + reasoning.md
electrical/lighting-layout/examples/uk-open-plan-office-10x8-dali/{input,output,intent-out}.json + reasoning.md
~/.claude/projects/-Users-linus-Desktop-DraftsMan-SKills-draftsman-skills/memory/sprint-D3-shipped.md
```

## 7. Gate targets

- **`validate-examples.py`**: `225 → ~241` (exact number set by C.1–C.3 implementer)
  - C.1 promotes 2 stub examples: +4 file validations (each gains intent-out.json + reasoning.md upgrade)
  - C.2 adds 3 failure-mode examples: +6 file validations (2 per example)
  - C.3 adds canonical 10×8m DALI example: +2 file validations
  - Net: +12 lighting-layout validations; some re-baselining likely once Phase A schema changes ripple through the office-open-plan example output

- **`functional_audit.py`**: holds at `1 finding` (disclosed motor-superposition oracle FP on `fault-level/us-industrial-with-motors/MCC-1`)

## 8. Out of scope (deferred)

- **Cross-skill drafting-standards harmonisation** (BS 1192 + ISO 19650 + AIA + ISO 5457 + ISO 5455 layer naming) — stays deferred per `[[drafting-standards-deferred-sprint]]`. D3 ships lighting-layout-only drafting furniture; the cross-skill sprint later generalises the pattern across all drawing skills.
- **Live runtime re-run** of the user's original prompt — out of scope for the contracts repo; the canonical example serves as the spec-level re-test. Live verification happens in the runtime project per `[[runtime-project-boundary]]`.
- **Other skills' stub validator/reviewer prompts** — the user noted "most of the validator and reviewer prompts being stubs" is a cross-skill issue. D3 fixes lighting-layout's two stubs only; the cross-skill audit + remediation is its own future sprint after D4.

## 9. Process lessons applied from D2.3

The D2.3 review caught a CRITICAL Reg 559 misattribution that the plan template itself had carried in. The lesson applied here:

- **Cross-check every clause citation against `shared/standards/electrical/` BEFORE writing it into the plan template.** Specifically: Phase A.1 (ontology citations) and A.2 (rules YAML citations) implementers MUST verify every clause against the repo's own standards data before emitting. Two-stage Opus review (spec-compliance + code-quality) per task remains mandatory.
- **No fabricated standards references.** If a citation cannot be verified, use `engineer_declared` + an explicit "no pinpoint clause" honest disclosure per `[[feedback-no-trim-non-consequential]]`.

## 10. Expected commit log

```
docs:                  Sprint D3 (lighting-layout depth) design spec
docs:                  Sprint D3 implementation plan
feat(lighting-layout): D3.A.1 ontology backfill — photometric defaults + switching + emergency types
feat(lighting-layout): D3.A.2 rules YAML SoT expansion (5 rule files with citations)
feat(lighting-layout): D3.A.3 schema extensions — zones + topology + drafting_furniture + intent payload
fix(lighting-layout):  D3.A.N fix-pass (one per A.1/A.2/A.3 review iff review surfaces issues — D2 precedent: per-task not per-phase)
feat(lighting-layout): D3.B.1 generator — lumen-method worked example + S/H ratio loop + photometric lookup + INV-1/INV-2/INV-8
feat(lighting-layout): D3.B.2 generator — circuit topology + switch placement + INV-3/INV-4/INV-5/INV-7
feat(lighting-layout): D3.B.3 generator — drafting furniture step + INV-9
feat(lighting-layout): D3.B.4 validator + reviewer prompts + intent payload wiring + INV-6/INV-10
fix(lighting-layout):  D3.B.N fix-pass (one per B.1/B.2/B.3/B.4 review iff review surfaces issues)
feat(lighting-layout): D3.C.1 promote reception-lobby + warehouse-highbay to full examples
feat(lighting-layout): D3.C.2 3 failure-mode examples (undersized + multi-entrance + part-l-fail)
feat(lighting-layout): D3.C.3 canonical uk-open-plan-office-10x8-dali (user's verbatim re-test)
feat(lighting-layout): D3.C.4 sprint ship — manifest 1.3.1→1.4.0 + combined CHANGELOG + memory
```

13–16 commits expected (depending on fix-passes per review round, mirroring D2's 8-commit shape scaled to 11 implementer tasks).

## 11. Cross-references

- Sprint D2 shipped memory: `~/.claude/projects/-Users-linus-Desktop-DraftsMan-SKills-draftsman-skills/memory/sprint-D2-shipped.md`
- Sprint D1 design spec (pattern parent): `docs/superpowers/specs/2026-05-25-sprint-D1-protection-safety-depth-design.md`
- Sprint D2 design spec (immediate predecessor): `docs/superpowers/specs/2026-05-26-sprint-D2-sizing-boards-depth-design.md`
- Within-skill depth plan: `~/.claude/projects/.../memory/within-skill-depth-plan.md`
- Model selection rule: `~/.claude/projects/.../memory/feedback-no-haiku-sonnet-opus-only.md`
- No-trim policy: `~/.claude/projects/.../memory/feedback-no-trim-non-consequential.md`
- Runtime boundary: `~/.claude/projects/.../memory/runtime-project-boundary.md`
- Drafting standards deferred: `~/.claude/projects/.../memory/drafting-standards-deferred-sprint.md`
- Canonical SVG template pattern (D2.2): `electrical/db-layout/templates/`
- Pattern parent for INV catalogues: `electrical/db-layout/prompts/validator.md` (post-D2.3)
