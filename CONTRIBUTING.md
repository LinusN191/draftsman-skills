# Contributing to draftsman-skills

Thank you for contributing. This repository encodes professional MEP engineering
knowledge into skills that AI agents can use reliably. Every contribution makes
DraftsMan more accurate and more useful for engineers worldwide.

## Who should contribute

You don't need to be a developer. The most valuable contributions come from:

- **Chartered electrical engineers (CEng, MIET, MIEEE)** — standards expertise,
  calculation verification, real-world design experience
- **Mechanical engineers (CEng, MIMechE, MCIBSE)** — HVAC, plumbing, ventilation skills
- **Lighting designers (MSLL, MCIBSE)** — photometric data, control systems
- **Engineering technicians** — practical installation knowledge, common site conditions
- **Developers with engineering domain knowledge** — tooling, eval automation, JSON schema

## What we need most

1. **Corrections to existing skills** — if a standards reference is wrong, a
   calculation method is outdated, or a typical value is inaccurate, open an issue
   or submit a PR with the correction and the correct standard clause number.

2. **New skills** — see the stub files in `drawings/`, `calculations/`, and
   `documents/`. Pick a stub, write the content following SKILL_TEMPLATE.md.

3. **Worked examples** — each skill needs 3–5 examples covering different scenarios.
   Examples are the fastest way to verify a skill works correctly.

4. **Evaluation criteria** — EVALS.md files define pass/fail tests for each skill.
   Good evals prevent regressions when skills are updated.

5. **Regional standards variants** — skills currently focus on UK standards (BS 7671,
   BS EN 12464-1). Contributions covering Kenya (KEBS, Kenya Power requirements),
   South Africa (SANS), Australia (AS/NZS), and USA (NEC, NFPA) are needed.

## How to contribute

### For engineering corrections (no coding needed)

1. Open an issue describing what is wrong and what the correct value/method/reference is
2. Include the standard name, edition, and clause number
3. A maintainer will update the skill and credit you in CHANGELOG.md

### For new content or larger changes

1. Fork the repository
2. Create a branch: `git checkout -b skill/lighting-layout-v1.1`
3. Follow SKILL_TEMPLATE.md for skill structure
4. Add EXAMPLES.md with at least 2 worked examples
5. Add or update EVALS.md with pass/fail criteria
6. Open a PR with:
   - Description of what you changed and why
   - Standard references for any technical claims
   - Your professional background (optional but helps reviewers)

## Authoring evals

Every skill carries one or more eval YAML files under `evals/`. Evals are the
behavioural spec of the skill — they declare what a correct run must produce
for a specific input scenario. The runtime executes them in CI on every change.

### Eval file shape

Conforms to `shared/schemas/core/eval.schema.json`. Required fields:

```yaml
name: eval-NN-short-slug
skill: lighting-layout
description: One-line summary of what this eval verifies
category: happy_path | edge_case | compliance_failure | cross_validation | skill_specific
input:
  # maps to inputs.json item ids → answers
  room_type: open_plan_office
  room_length_mm: 10000
  # …
expected_compliance:
  # optional: declared expected compliance outcome
  lux_target_lx: 500
  compliant: true
checks:
  - assertion: ir.luminaires.length >= 17
    description: N must round UP from lumen method
    severity: critical
    standard_ref: CIBSE SLL Code for Lighting 2012
expected_flags:
  - "NON-COMPLIANCE"  # substrings expected in ir.flags
```

### Assertion grammar

Restricted on purpose so the runtime parser stays simple:

```
<jsonpath> <operator> <value>
```

Operators: `==`, `!=`, `>=`, `<=`, `>`, `<`, `contains`, `not_contains`,
`all_equal`, `matches`.

JSONPath examples:
- `ir.compliance.lux_ok`
- `ir.luminaires.length`
- `ir.luminaires[*].circuit_id` — applies the operator to every element
- `ir.rationale.sections`

Values may be: quoted strings, integers, floats, `true`, `false`.

To extend the grammar (new operator, function call, arithmetic): open an issue
first. The grammar is deliberately minimal; runtime parsers in multiple agent
environments depend on its stability.

### Coverage matrix — required for `status: production`

| Eval | Category | Required for production |
|---|---|---|
| 1 | happy_path | Yes |
| 2 | edge_case (input edge, e.g. missing data) | Yes |
| 3 | edge_case (constraint edge, e.g. grid alignment) | Yes |
| 4 | compliance_failure (must surface flag) | Yes |
| 5 | cross_validation (computed values match expected) | Yes |
| 6+ | skill_specific scenarios | Optional |

`runner-config.json` per skill declares minimum eval counts per status tier
(production ≥5, beta ≥3, draft ≥1, stub 0) and the minimum model class.

### Existing reference

See `electrical/lighting-layout/evals/` for 7 evals covering all 5 required
categories plus 2 skill-specific. `electrical/lighting-layout/evals/runner-config.json`
shows the runner-config shape.

---

## Quality standards

Every skill must meet these criteria before merging:

### Engineering accuracy
- Every number or formula must reference a specific standard clause or table
- Typical values must state their source and applicable conditions
- Assumptions must be clearly labelled with [ASSUMPTION: ...] syntax
- Non-compliance conditions must be clearly described

### Completeness
- SKILL.md must be complete (not a stub) before merging to main
- At least 2 worked examples in EXAMPLES.md
- At least 3 evaluation criteria in EVALS.md
- At least 1 reference table in assets/ if the skill uses tabulated data

### Format
- Use the frontmatter fields from SKILL_TEMPLATE.md
- Maintain consistent section headings
- Output JSON must match the schema documented in the skill

## Standards we reference

When contributing, use these primary standards as references. Always include
the edition year. Standards are updated periodically — note if your contribution
applies to a specific edition.

### Electrical (UK)
- BS 7671:2018 — IET Wiring Regulations 18th Edition (with amendments)
- BS EN 60617 — Graphical symbols for electrical diagrams
- BS EN 61439 — Low-voltage switchgear and controlgear assemblies
- BS EN 62271 — High-voltage switchgear and controlgear
- BS EN 12464-1:2021 — Light and lighting — Indoor work places
- BS EN 1838:2013 — Emergency lighting
- BS 1192:2007 / ISO 19650 — Drawing management

### Mechanical (UK)
- CIBSE Guide A — Environmental Design
- CIBSE Guide B — Heating, Ventilating, Air Conditioning and Refrigeration
- CIBSE Guide F — Energy Efficiency
- BS EN 15232 — Energy performance of buildings
- BS EN 13779 — Ventilation for non-residential buildings

### Regional standards (contributions welcome)
- Kenya: KEBS standards, Kenya Power connection requirements
- South Africa: SANS 10142, NRS 047
- Nigeria: NEC (Nigeria), SON standards
- Australia/NZ: AS/NZS 3000 (Wiring Rules), AS/NZS 1680 (Lighting)
- USA: NEC (NFPA 70), NFPA 101, IESNA Handbook

## Licensing

By contributing, you agree that your contribution is licensed under the MIT
licence. Contributions must be your own original work or properly attributed
to public domain sources (e.g. published standards tables).

Do not contribute content that reproduces copyrighted standards text verbatim.
Reference clause numbers and paraphrase; do not copy tables wholesale.

## Questions

Open an issue or start a discussion. We respond to all engineering questions.
