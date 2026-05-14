# DraftsMan Skills — Claude Code Context

## What this repo is
Open source MEP engineering skills for AI agents. Each skill teaches Claude
to reason like a senior building services engineer before producing output.

## Skill structure (follow exactly)
Every skill folder must contain:
- SKILL.md — the skill (YAML frontmatter + engineering content)
- EVALS.md — 5 evaluation criteria with pass/fail tests
- EXAMPLES.md — 3 worked examples with full inputs and reasoning
- assets/ — reference tables (standards values, photometric data, etc.)

## Format reference
The lighting-layout skill is the gold standard. Read it completely before
writing any other skill. Every other skill must match its depth and structure.

## Build order
Work through these in order. Complete each fully before starting the next.
One skill = SKILL.md + EVALS.md + EXAMPLES.md + at least 1 asset file.

### Drawings (8 skills)
- [x] lighting-layout — COMPLETE (reference implementation)
- [ ] sld — single line diagrams, BS EN 60617, BS 7671:2018
- [ ] db-layout — distribution board design, BS 7671:2018
- [ ] cable-containment — tray/trunking/conduit routing
- [ ] riser — LV riser diagrams, floor by floor
- [ ] schematic — schematic diagrams, BS EN 60617
- [ ] small-power — socket outlet layouts, BS 7671:2018
- [ ] earthing — earthing layouts, BS 7671:2018 Part 5-54

### Calculations (7 skills)
- [ ] cable-sizing — BS 7671:2018 Appendix 4, deterministic Python
- [ ] lux — room cavity ratio method, CIBSE SLL
- [ ] load-schedule — diversity factors, maximum demand
- [ ] voltage-drop — BS 7671:2018 Appendix 4
- [ ] generator-sizing — kVA sizing, load shedding
- [ ] fault-level — short circuit, basic IEC 60909
- [ ] power-factor — capacitor sizing, BS EN 60831

### Documents (7 skills)
- [ ] tender-report — BS 7671, CDM 2015, CIBSE refs
- [ ] bq — NRM2 measurement rules for electrical
- [ ] method-statement — CDM 2015, sequence of works
- [ ] cable-schedule — tabulated format, BS 7671
- [ ] specification — NBS format, clause structure
- [ ] om-manual — structure and content per BSRIA BG 29
- [ ] design-statement — planning requirements, Part L

## Standards to apply
- BS 7671:2018 (18th Edition) — primary electrical standard
- BS EN 12464-1:2021 — lighting
- BS EN 60617 — electrical symbols
- BS 1192 / ISO 19650 — drawing management
- BS EN 61439 — switchgear assemblies
- CIBSE Guides A, B, F, SLL
- CDM Regulations 2015
- NRM2 — measurement rules for BQs

## Git commit format
feat: [skill-name] skill v1.0.0
chore: [description]
fix: [skill-name] [what was fixed]

## Never do
- Never write a stub — every skill must be complete before committing
- Never skip EVALS.md — 5 evals minimum per skill
- Never skip EXAMPLES.md — 3 examples minimum per skill
- Never invent standards values — reference the clause number
