# photometric-analysis — DraftsMan MEP Engineering Skill

**Status:** Stub — contributions welcome
**Discipline:** electrical
**Standards:** BS EN 12464-1:2021 §6.6 (UGR), CIBSE LG7, CIE 117
**Output:** JSON IR

## What this skill does
DIALux-grade photometric point-grid calculation producing UGR (glare), uniformity (Emin/Eavg), and per-point illuminance maps. Consumes lighting-layout intent + room geometry. Closes the BS EN 12464-1 §6.6 UGR + uniformity gap that the lumen-method alone cannot verify.

## What needs to be built
- [ ] skill.manifest.json — all fields complete (standards / inputs / outputs / produces_intents / consumes_intents)
- [ ] prompts/generator.md — complete engineering skill prompt
- [ ] prompts/validator.md — INV invariants
- [ ] prompts/reviewer.md — D-decision checks
- [ ] examples/ — minimum 3 worked examples (input.json, reasoning.md, output.json)
- [ ] evals/ — minimum 5 evaluation criteria (YAML; eval.schema.json v2)
- [ ] inputs.json — WI1 interview taxonomy
- [ ] schemas/<skill>-ir.schema.json + (if produces_intent) <skill>-intent.schema.json
- [ ] rules/, constraints/ — placement and engineering rules
- [ ] CHANGELOG.md

## Reference implementation
See `electrical/lighting-layout/` (production) or `electrical/db-layout/` (beta) for the complete reference shape.

## Why this stub exists
Created 2026-05-25 as a depth-extension stub during the post-remediation
within-skill-scope audit. This domain was identified as a distinct
engineering specialism (own standards, own inputs/outputs, own reviewer
expertise) that should compose with the parent skill via intent rather
than expand it. Authoring blocked pending engineer brief or sprint
resourcing.
