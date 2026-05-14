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

## Reference for other skill authors

This skill is the gold standard for the repo. Read prompts/generator.md
and examples/office-open-plan/ before building any other skill.
