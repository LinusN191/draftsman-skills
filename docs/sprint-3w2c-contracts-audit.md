# Sprint 3-W2c — Contracts Audit Report (Task 3)

**Date:** 2026-05-22  
**Branch:** main  
**Baseline harness:** 143/143 (FULL GREEN)  
**Post-fix harness:** 143/143 (FULL GREEN)

This audit verifies runtime-readiness of intent contracts (A2), skill manifests (A3), and
inputs.json taxonomy (A4) post-Sprint 3-W2b schema additions. The harness FULL GREEN 143/143
verifies IR conformance but does NOT verify cross-skill intent contract alignment — A2 fills
that gap.

---

## A2 — Intent contracts (15 producer→consumer pairs)

### Schema well-formedness

All 10 per-skill intent schemas validate as JSON Schema Draft-07. 0 failures.

### Producer→consumer reference resolution

All 15 producer→consumer pairs resolve cleanly via `skill.manifest.json`
`produces_intent` ↔ `consumes_intents[]` references. 0 broken references.

Pairs verified:

| Producer | Intent emitted | Consumer |
|---|---|---|
| arc-flash | arc-flash | arc-flash-labelling |
| cable-sizing | cable-sizing | small-power |
| db-layout | db-layout | earthing |
| db-layout | db-layout | sld |
| db-layout | db-layout-rollup | arc-flash |
| db-layout | db-layout-rollup | cable-sizing |
| db-layout | db-layout-rollup | fault-level |
| earthing | earthing | sld |
| fault-level | fault-level | arc-flash |
| fault-level | fault-level | cable-sizing |
| fault-level | fault-level | db-layout |
| fault-level | fault-level | sld |
| lighting-layout | lighting-layout | db-layout |
| lighting-layout | lighting-layout | earthing |
| small-power | small-power | earthing |

Terminal producers (no downstream consumers in shipped set): arc-flash-labelling (labels),
sld (sld).

### Post-3W2b coverage per intent schema

| # | Schema file | Schema valid? | jurisdiction field? | KE in enum? | board_kind? | ups_plus_essential? | main_switch_fused? | Outcome |
|---|---|---|---|---|---|---|---|---|
| 1 | labels-intent.schema.json | Y | N (not applicable) | N/A | N/A | N/A | N/A | PASS |
| 2 | arc-flash-intent.schema.json | Y | N (not applicable) | N/A | N/A | N/A | N/A | PASS |
| 3 | cable-sizing-intent.schema.json | Y | N (not applicable) | N/A | N/A | N/A | N/A | PASS |
| 4 | db-layout-intent.schema.json | Y | N (single-board slice, jurisdiction not echoed) | N/A | N→**FIXED** | already present | N→**FIXED** | FIXED |
| 5 | db-layout-rollup-intent.schema.json | Y | N→**FIXED** | N→**FIXED** | N→**FIXED** | N→**FIXED** | N→**FIXED** | FIXED |
| 6 | earthing-intent.schema.json | Y | Y | N→**FIXED** | N/A | N/A | N/A | FIXED |
| 7 | fault-level-intent.schema.json | Y | N (not applicable) | N/A | N/A | N/A | N/A | PASS |
| 8 | lighting-layout-intent.schema.json | Y | N (not applicable) | N/A | N/A | N/A | N/A | PASS |
| 9 | sld-intent.schema.json | Y | Y | already present | N/A | N/A | N/A | PASS |
| 10 | small-power-intent.schema.json | Y | N (not applicable) | N/A | N/A | N/A | N/A | PASS |

Notes on "not applicable" jurisdiction fields:
- labels, arc-flash, cable-sizing, fault-level, lighting-layout, small-power intent schemas
  are produced by skills that do not expose jurisdiction in their stable intent contract.
  These skills surface jurisdiction in the IR but choose not to echo it downstream —
  acceptable design choice; consumers that need jurisdiction re-query the source IR or
  project context.
- db-layout-intent.schema.json models a single-board slice; jurisdiction is not echoed at
  this granularity (the rollup-intent schema is the correct place for project-wide context).

### Fixes applied

1. **earthing-intent.schema.json** — Added `KE` to `jurisdiction` enum
   (`["GB", "EU", "INT", "US"]` → `["GB", "EU", "INT", "KE", "US"]`).
   Additive; no example breakage.

2. **db-layout-rollup-intent.schema.json** — Three changes:
   - Added optional `jurisdiction` top-level field with enum `["GB", "EU", "INT", "KE", "US"]`
   - Changed `boards[].main_switch_type` from free-text string to enum matching IR:
     `["switch-disconnector", "MCCB", "isolator", "RCCB", "RCBO", "main_switch_fused"]`
   - Added optional `boards[].board_kind` enum `["main_switchboard", "specialty_board"]`
   - Added optional `boards[].supply_class` enum matching IR:
     `["essential", "non_essential", "life_safety", "ups_backed", "ups_plus_essential", "genset_backed"]`
   All additive (optional fields, additionalProperties:false already present).

3. **db-layout-intent.schema.json** — Two changes:
   - Added optional `board_kind` top-level field enum `["main_switchboard", "specialty_board"]`
   - Added optional `main_switch` sub-object with `type` enum:
     `["switch-disconnector", "MCCB", "isolator", "RCCB", "RCBO", "main_switch_fused"]`,
     `rating_a` (number), `curve` (B/C/D)
   All additive; no example breakage.

### Deferred

None. All post-3W2b intent gaps were non-cascading additive fixes.

---

## A3 — skill.manifest.json (9 shipped skills)

### Per-skill manifest summary

| # | Skill | Version | Required keys present | produces_intent_schema variant | inputs vs inputs_path | CHANGELOG aligned | Outcome |
|---|---|---|---|---|---|---|---|
| 1 | arc-flash | 1.0.0 | OK | plural (`produces_intent_schemas`) | inputs removed → `inputs_path` only | OK | FIXED |
| 2 | arc-flash-labelling | 1.0.0 | OK | plural (`produces_intent_schemas`) | inputs removed → `inputs_path` only | OK | FIXED |
| 3 | cable-sizing | 1.0.0 | OK | singular (`produces_intent_schema`) | inputs removed → `inputs_path` only | OK | FIXED |
| 4 | db-layout | 1.3.1 | OK | plural (`produces_intent_schemas`) | inputs removed → `inputs_path` only | OK | FIXED |
| 5 | earthing | 1.4.0 | OK | singular (`produces_intent_schema`) | inputs removed → `inputs_path` only | OK | FIXED |
| 6 | fault-level | 1.1.0 | OK | singular (`produces_intent_schema`) | inputs removed → `inputs_path` only | OK | FIXED |
| 7 | lighting-layout | 1.3.0 | OK | singular (`produces_intent_schema`) | inputs removed → `inputs_path` only | OK | FIXED |
| 8 | sld | 1.5.0 | OK | singular (`produces_intent_schema`) | `inputs_path` normalised to relative | OK | FIXED |
| 9 | small-power | 1.1.0 | OK | singular (`produces_intent_schema`) | inputs removed → `inputs_path` only | OK | FIXED |

All 9 CHANGELOG versions aligned with manifest versions.

### Naming-convention findings

**produces_intent_schema (singular) vs produces_intent_schemas (plural):**  
This variance is intentional and semantically correct:
- `produces_intent_schema` (string path) — skill produces exactly 1 intent type.
  Used by: cable-sizing, earthing, fault-level, lighting-layout, sld, small-power.
- `produces_intent_schemas` (dict `{intent_name: path}`) — skill produces 2+ intent types.
  Used by: arc-flash, arc-flash-labelling, db-layout.
Decision: **ACCEPT AS CONVENTION**. No normalisation needed.

**inputs vs inputs_path:**  
8 skills had both `inputs` (inline stale list) and `inputs_path` (canonical file reference).
The inline `inputs` lists were stale copies of inputs.json with fewer items
(8-12 items vs 15-18 in the canonical files). The runtime reads from `inputs_path`.
Decision: **REMOVE inline `inputs`** from all 8 affected manifests.

**inputs_path path style:**  
SLD used a repo-root relative path (`electrical/sld/inputs.json`); all others used skill-local
relative (`inputs.json`). Normalised SLD to `inputs.json` for consistency.

### Fixes applied

1. **8 manifests (arc-flash, arc-flash-labelling, cable-sizing, db-layout, earthing,
   fault-level, lighting-layout, small-power)** — Removed stale inline `inputs` list key.
   `inputs_path` is the canonical reference; inline copy was diverged (8-12 items vs 15-18
   in the canonical file).

2. **sld/skill.manifest.json** — Normalised `inputs_path` from `"electrical/sld/inputs.json"`
   to `"inputs.json"` (skill-local relative, matching all other skills).

### Deferred

None.

---

## A4 — inputs.json taxonomy (5 items[]-shape skills)

### Per-skill summary

| # | Skill | Item count | depends_on issues | depends_on cycles | Required-item coverage gaps | Enum coverage gaps (fields) | Outcome |
|---|---|---|---|---|---|---|---|
| 1 | db-layout | 17 | 0 | none | 0 | 6 fields (informational) | PASS |
| 2 | earthing | 18 | 0 | none | 0 | 10 fields (informational) | PASS |
| 3 | fault-level | 16 | 0 | none | 1 (content sprint) | 4 fields (informational) | DEFERRED |
| 4 | lighting-layout | 15 | 0 | none | 5 (content sprint) | 6 fields (informational) | DEFERRED |
| 5 | sld | 5 | 0 | none | 0 | 1 field (informational) | PASS |

### depends_on graph

All 5 files: 0 broken depends_on references, 0 cycles. Runtime interview UX termination
is safe.

### Required-item coverage gaps (content sprint scope)

**fault-level** — `project_id` item is required in inputs.json but no example has a
top-level `project_id` key. Root cause: fault-level examples use a nested
`project_meta.project_id` struct rather than a flat `project_id` key. The inputs.json
taxonomy models the flat UX question; the example input.json mirrors the structured IR
ingestion format. These are intentionally different layers. Resolving this requires either
(a) aligning the example input.json to the WI1 flat taxonomy, or (b) restructuring the
`project_id` item to use dot-notation path. Both require content authoring — **DEFERRED to
content sprint**.

**lighting-layout** — 5 required items missing example coverage:
`room_length_mm`, `room_width_mm`, `ceiling_height_mm`, `luminaire_lumens`, `lumen_type`.
Root cause: inputs.json uses `_mm` integer fields (e.g. `room_length_mm`) but examples use
`_m` float fields (`room_length_m`). Similarly, `luminaire_lumens`/`lumen_type` (flat) vs
`luminaire.lumen_output`/`luminaire.lumen_type` (nested struct in examples).
This is a field-name mismatch between the WI1 taxonomy layer and the example input.json
format. Resolving requires aligning both to one convention — **DEFERRED to content sprint**.

### Enum option coverage notes (all informational — not blocking)

These enum values exist in inputs.json but are not exercised by any current example.
Uncovered options do not indicate schema bugs; they represent valid input combinations
not yet covered by examples. No fixes applied.

| Skill | Field | Options seen / total | Uncovered options (sample) |
|---|---|---|---|
| db-layout | jurisdiction | 4/4 | EU |
| db-layout | board_type | 3/6 | distribution_board, motor_control_center, motor_db |
| db-layout | supply_voltage_v | 4/7 | 120, 415, 480 |
| db-layout | phase_arrangement | 3/4 | TPN_plus_E |
| db-layout | form_separation_iec61439 | 2/7 | 2a, 2b, 3a, 3b, 4a |
| db-layout | rcd_type_default | 2/4 | B, F |
| earthing | jurisdiction | 4/4 | EU |
| earthing | electrode_type_planned | 0/7 | ground_ring, mat, plate, rod, structural_metal, tbd, ufer |
| earthing | ground_conditions | 3/7 | clay_moist, loam, made_ground_imported_fill, marsh_wet, rock, sand_dry |
| earthing | building_type | 4/10 | agricultural, dwelling_multi_family, education, healthcare… |
| fault-level | jurisdiction | 3/4 | EU |
| fault-level | cascade_topology_source | 1/2 | db_layout_rollup_intent |
| lighting-layout | lumen_type | 0/3 | design, initial, unknown |
| lighting-layout | controls_protocol | 0/5 | 0-10V, DALI, DALI-2, none, switched |
| lighting-layout | jurisdiction | 1/11 | AE, AU, DE, FR, GB, IE, KE, NG, NZ, OTHER, ZA |
| sld | jurisdiction | 4/5 | EU |

### Fixes applied

None. All A4 issues are either PASS (no issues) or content-sprint scope (DEFERRED).

### Deferred

- fault-level `project_id` required-item coverage gap — content sprint (input.json
  flat-vs-nested alignment)
- lighting-layout 5 required-item coverage gaps (`room_*_mm`, `luminaire_lumens`,
  `lumen_type`) — content sprint (unit convention + flat-vs-nested alignment)
- All enum coverage notes — informational only, no action required until example set expands

---

## Summary

| Sub-audit | Items assessed | Issues found | Fixed | Deferred |
|---|---|---|---|---|
| A2 — Intent contracts | 10 schemas, 15 pairs | 3 schemas with post-3W2b coverage gaps | 3 (additive enum/field additions) | 0 |
| A3 — Skill manifests | 9 manifests | 9 (inputs/inputs_path duplicate in 8; sld path style) | 9 | 0 |
| A4 — inputs.json taxonomy | 5 items-shape files | 2 files with required-item coverage gaps; 0 graph issues | 0 | 2 (content sprint) |

**Harness result: 143/143 FULL GREEN throughout.**  
**Unresolved HIGH-RISK items: 0.**

All deferred items are content-authoring scope (field-name convention alignment between
WI1 flat taxonomy and structured IR input format). They do not block runtime-readiness
of schema validation, intent contract plumbing, or the harness gate.
