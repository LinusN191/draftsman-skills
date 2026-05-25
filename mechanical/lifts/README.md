# lifts — DraftsMan MEP Engineering Skill

**Status:** Stub — contributions welcome
**Discipline:** mechanical
**Standards:** BS EN 81-20/-50, BS EN 81-70 (accessibility), BS EN 115 (escalators), Approved Document M, CIBSE Guide D
**Output:** JSON IR

## What this skill does
Lift and escalator specification — traffic analysis, machine-room/MRL configuration, power supply coordination and code compliance

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
Stubbed during Sprint D follow-up (2026-05-25) as part of the post-remediation scope-coverage audit. This domain was identified as **truly unscoped** (no folder anywhere in the repo) by Reviewer 1's coverage analysis, distinct from skills that are scoped-but-unbuilt elsewhere. Authoring blocked pending engineer brief or sprint resourcing.
