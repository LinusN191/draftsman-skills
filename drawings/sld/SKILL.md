---
name: sld
description: "Design LV single line diagrams (SLDs) for building electrical distribution systems. Covers incoming supply, main switchboard, sub-distribution boards, protection coordination, and earthing arrangement. Outputs DXF-ready JSON per BS EN 60617 symbols and BS 1192 layer naming."
version: 0.1.0
discipline: electrical
standards:
  - BS EN 60617
  - BS 7671:2018
  - BS EN 61439
  - IEC 60364
output_format: json
tags:
  - drawings
  - electrical
  - distribution
status: stub — skill content to be written
---

# Single Line Diagram (SLD) Skill — DraftsMan MEP Engineering

> **Status:** This skill is a stub. Content will be developed in the next session.
> See the lighting-layout skill for the full format reference.

## Role

You are a senior electrical engineer specialising in LV distribution design
for commercial and industrial buildings.

## Standards You Apply

- BS EN 60617 — Graphical symbols for electrical diagrams
- BS 7671:2018 — IET Wiring Regulations 18th Edition
- BS EN 61439 — Low-voltage switchgear and controlgear assemblies
- IEC 60364-4-41 — Protection against electric shock
- IEC 60364-5-53 — Selection and erection of equipment — Isolation, switching, control

## Content to be written

- [ ] Inputs required (voltage levels, fault level, load list, earthing system)
- [ ] Reasoning steps (protection coordination, cable sizing, discrimination)
- [ ] Output JSON format (SLD elements, busbar, breakers, cables, annotations)
- [ ] EXAMPLES.md (3 worked examples: simple office, complex commercial, industrial)
- [ ] EVALS.md (5 evaluation criteria)
- [ ] assets/protection-coordination.md
- [ ] assets/standard-symbols.md (BS EN 60617 reference)

## Contributing

If you are a chartered electrical engineer and can contribute the content for
this skill, please see CONTRIBUTING.md and open a PR.
