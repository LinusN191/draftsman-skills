# spd-coordination — DraftsMan MEP Engineering Skill

**Status:** Stub — contributions welcome
**Discipline:** electrical
**Standards:** BS 7671:2018+A2:2022 §443, IEC 61643-11/12, BS EN 62305-4
**Output:** JSON IR

## What this skill does
Surge protection device selection + cascade coordination per BS 7671 §443 / IEC 61643. Type 1/2/3 device selection by lightning protection level (LPL); energy let-through coordination across stages; LEMP scenarios. Interfaces with lightning-protection (LPS down-conductor terminations).

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
