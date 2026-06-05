# lighting-layout — DraftsMan MEP Engineering Skill

**Version:** 1.7.0
**Status:** Production (reference implementation)
**Discipline:** Electrical
**Sub-discipline:** Lighting
**Standards:** BS EN 12464-1:2021, BS 7671:2018+A2:2022, AD Part L 2021, BS 8300:2018, BS EN 1838:2013
**Output:** lighting-layout IR (JSON)

## What this skill does

Produces BS EN 12464-1:2021 compliant interior lighting layouts: luminaire
placement, circuit assignment, switching positions, and annotation data as
structured JSON IR. Checks Part L efficacy, perimeter zone controls, LLMF
conversion, IP suitability, circuit load compliance, zone-purpose hierarchy
(task / surrounding / background), and 3D luminaire placement geometry.

## Skill structure

| Folder | Contents |
|---|---|
| `prompts/` | generator.md (main skill prompt), validator.md, reviewer.md |
| `evals/` | 13 YAML evaluation criteria (eval-01..13) |
| `examples/` | 12 worked examples with input.json, reasoning.md, output.json |
| `rules/` | Placement, spacing, switching, emergency, control, zone-purpose, mount-type rules |
| `constraints/` | Geometric, electrical, maintenance constraints |
| `validation/` | Lux, spacing, emergency validation YAML |
| `ontology/` | Luminaire and switching type definitions |
| `schemas/` | lighting-layout-ir.schema.json + lighting-layout-intent.schema.json |
| `docs/` | Engineering philosophy, known limitations, supported standards |
| `assets/` | Reference tables (photometric data, standards values) |

## Features

- Lux-level compliance per BS EN 12464-1:2021 Table 5/6
- Part L 2021 efficacy gating (SBEM/notional-building limit)
- Perimeter zone dimming control (DALI/KNX mapping)
- LLMF (Light Loss Maintenance Factor) conversion, maintenance schedule awareness
- IP/voltage suitability for BS 7671:2018 Part 7 special locations
- Circuit load compliance (MCB diversity, cable rating)
- Photometric grid cascade consumer (photometric-analysis intent)
- Special-locations zoning cascade consumer (special-locations-zoning intent)
- **Task/ambient zone-purpose split** — task / surrounding / background zone
  hierarchy with ratio enforcement per §4.2.2 (Wave 2, v1.7.0)
- **3D luminaire placement** — mount_type enum, z_mm, suspension_length_mm,
  hm_mm derivation consistency (Wave 2, v1.7.0)
- Per-zone lux achievement tracking via `calc.per_zone_achieved[]` (Wave 2, v1.7.0)
- Floor plan context portability (generic `## Floor plan context` contract)

## Invariant (INV) table

| INV | Name | Severity |
|---|---|---|
| INV-1 | Maintained illuminance compliance | HIGH |
| INV-2 | Uniformity ratio (Uo) | HIGH |
| INV-3 | LLMF / maintenance factor applied | HIGH |
| INV-4 | Circuit load within rating | HIGH |
| INV-5 | Part L efficacy threshold | HIGH |
| INV-6 | Emergency luminaire coverage | HIGH |
| INV-7 | IP suitability (special locations) | HIGH |
| INV-8 | Switching zone compliance | MEDIUM |
| INV-9 | Rationale block completeness | MEDIUM |
| INV-10 | Photometric grid cascade present | HIGH |
| INV-11 | Photometric-grid lux vs design target | HIGH |
| INV-12 | Special-locations zoning cascade resolved | HIGH |
| INV-13 | Zone purpose required + valid | HIGH |
| INV-14 | Surrounding ratio compliance (≥ ⅓ task) | HIGH |
| INV-15 | Background floor (≥ ⅓ surrounding / ⅓ lowest task) | HIGH |
| INV-16 | mount_type ↔ z_mm/suspension consistency | HIGH |
| INV-17 | Ceiling clearance + working-plane floor | HIGH |
| INV-18 | hm_mm derivation consistency | MEDIUM |
| INV-19 | Per-zone achievement (graded: INFO/MEDIUM/HIGH) | HIGH |

## Reviewer D-check table

| D-check | Name | Severity |
|---|---|---|
| D-1 | Luminaire spacing-to-height ratio | MEDIUM |
| D-2 | Wall-wash spacing | MEDIUM |
| D-3 | Emergency spacing crosscheck | HIGH |
| D-4 | DALI zone/address assignment | MEDIUM |
| D-5 | UGR glare check | MEDIUM |
| D-6 | Colour rendering (Ra) | MEDIUM |
| D-7 | Photometric IES file present | HIGH |
| D-8 | Part L perimeter zone | MEDIUM |
| D-9 | Pendant/pole clearance | MEDIUM |
| D-10 | Per-zone photometric alignment | MEDIUM |
| D-11 | Suspension length sanity check | MEDIUM |
| D-12 | Background-only rooms flag | MEDIUM |
| D-13 | Task-zone density flag | LOW |

## Eval coverage matrix

| Eval | Name | Category |
|---|---|---|
| eval-01 | office-happy-path | happy_path |
| eval-02 | lux-below-minimum | compliance_failure |
| eval-03 | missing-lumen-data | edge_case |
| eval-04 | circuit-load-check | cross_validation |
| eval-05 | ceiling-grid-alignment | edge_case |
| eval-06 | part-l-efficacy | compliance_failure |
| eval-07 | initial-vs-design-lumens | skill_specific |
| eval-08 | rationale-block | skill_specific |
| eval-09 | zone-purpose-emit | skill_specific |
| eval-10 | task-surrounding-ratio | compliance_failure |
| eval-11 | mount-type-3d-consistency | skill_specific |
| eval-12 | per-zone-achievement-pass | cross_validation |
| eval-13 | per-zone-achievement-fail | compliance_failure |

All evals conform to `shared/schemas/core/eval.schema.json`.

## Verified standards files

| File | Standard | Clauses |
|---|---|---|
| `shared/standards/lighting/BSEN12464/lux-levels.json` | BS EN 12464-1:2021 | Table 5, Table 6 |
| `shared/standards/lighting/BSEN12464/area-definitions.json` | BS EN 12464-1:2021 | §4.2.2.1/2/3, Table 6 |

## Quick start

Paste a room description into DraftsMan or Claude Code with this skill active.
See `examples/office-open-plan/` for a basic worked example or
`examples/uk-pendant-open-plan-office/` for a 3D pendant placement example.

## Reference for other skill authors

This skill is the gold standard for the repo. Read `prompts/generator.md`
and `examples/office-open-plan/` before building any other skill.
