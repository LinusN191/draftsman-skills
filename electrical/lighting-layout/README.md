# lighting-layout — DraftsMan MEP Engineering Skill

**Status:** Production (reference implementation)
**Discipline:** Electrical
**Sub-discipline:** Lighting
**Standards:** BS EN 12464-1:2021, BS 7671:2018, AD Part L 2021, BS 8300:2018
**Output:** lighting-layout IR (JSON)

## What this skill does

Produces BS EN 12464-1:2021 compliant interior lighting layouts: luminaire
placement, circuit assignment, switching positions, and annotation data as
structured JSON IR. Checks Part L efficacy, perimeter zone controls, LLMF
conversion, IP suitability, and circuit load compliance.

## Skill structure

| Folder | Contents |
|---|---|
| prompts/ | generator.md (main skill prompt), validator.md, reviewer.md |
| evals/ | 7 YAML evaluation criteria |
| examples/ | 3 worked examples with input.json, reasoning.md, output.json |
| rules/ | Placement, spacing, switching, emergency, control rules |
| constraints/ | Geometric, electrical, maintenance constraints |
| validation/ | Lux, spacing, emergency validation YAML |
| ontology/ | Luminaire and switching type definitions |
| schemas/ | lighting-layout-ir.schema.json |
| docs/ | Engineering philosophy, known limitations, supported standards |

## Quick start

Paste a room description into DraftsMan or Claude Code with this skill active.
See examples/office-open-plan/ for a complete worked example.

## Eval coverage matrix

Per the upstream-contributions spec, every `status: production` skill must
satisfy at least one eval per category below. This skill has 7/5 evals
(5 required + 2 skill-specific).

| Eval | Name | Category | Required for production |
|---|---|---|---|
| 1 | eval-01-office-happy-path | happy_path | Yes |
| 2 | eval-05-ceiling-grid-alignment | edge_case (grid present) | Yes |
| 3 | eval-03-missing-lumen-data | edge_case (missing input) | Yes |
| 4 | eval-02-lux-below-minimum | compliance_failure (lux) | Yes |
| 5 | eval-04-circuit-load-check | cross_validation | Yes |
| 6 | eval-06-part-l-efficacy | compliance_failure (Part L) | Optional |
| 7 | eval-07-initial-vs-design-lumens | skill_specific (LLMF) | Optional |

All evals conform to `shared/schemas/core/eval.schema.json`. Runner config
at `evals/runner-config.json` declares minimum status thresholds and the
model-class against which the evals are validated.

## Reference for other skill authors

This skill is the gold standard for the repo. Read prompts/generator.md
and examples/office-open-plan/ before building any other skill.
