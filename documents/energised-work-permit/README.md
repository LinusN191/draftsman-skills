# energised-work-permit — DraftsMan MEP Engineering Skill

**Status:** Stub — contributions welcome
**Discipline:** documents
**Standards:** IEEE Std 1584-2018 §6, NFPA 70E:2024 §130.2 + §130.5, HSE EAW Regulations 1989
**Output:** JSON IR

## What this skill does
Energised-electrical-work permit (live-work risk assessment) per IEEE 1584 §6 + NFPA 70E. Consumes arc-flash intent (incident energy, PPE category, AFB, restricted/limited approach). Outputs the HSE permit document with controls, justification, and supervisor sign-off blocks.

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
