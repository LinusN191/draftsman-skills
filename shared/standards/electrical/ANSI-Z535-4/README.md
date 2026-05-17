# ANSI-Z535-4 — Product Safety Signs and Labels

**Status:** `stub` — folder placeholder, no clauses transcribed yet
**Standard body:** ANSI / NEMA
**Edition:** ANSI Z535.4:2023 (current)
**Scope:** Format, colour, symbol, and content requirements for safety signs and labels affixed to products + equipment. The canonical sign-format spec referenced by NFPA 70E §130.5(H) for arc-flash labels.
**Jurisdiction:** US (de facto international for industrial safety labels)
**Cost-to-acquire:** ~$100-200 USD from ANSI

## Related skills (will consume this layer)

- `electrical/arc-flash-labelling` (planned — stub) — primary consumer; renders arc-flash labels per Z535.4 format

## What this folder will contain (TODO when promoted stub → production)

- `meta.json` (present — minimal frontmatter)
- `README.md` (this file)
- `terminology.md` — definitions (signal word, panel, symbol, hazard severity level)
- `signal-words.json` — DANGER / WARNING / CAUTION / NOTICE definitions + colour codes
- `colour-spec.json` — safety colours (red, orange, yellow, green) + Pantone references
- `symbol-library.json` — standardised hazard symbols (electric shock, arc-flash, hot surface, etc.)
- `panel-format.json` — sign-panel layout (signal-word panel, message panel, symbol panel)
- `letter-height-requirements.json` — minimum legibility distances per text size
- `label-content-rules.json` — required content + ordering on a label
- `compliance-checklist.md` — when a label satisfies Z535.4

## Priority for next build cycle

- [ ] Critical (top 5 next-to-build): false
- [ ] Dependent skill is currently stub: true (arc-flash-labelling)
- [ ] Dependent skill is currently beta needing v1.1: false

Status: build when `electrical/arc-flash-labelling/` enters active development (~next-next sprint after arc-flash + clause_ref retrofit).

## License + reuse note

Standards content is copyright of ANSI/NEMA. This repo will store clause references + brief paraphrase only — never full standard text. Safety colours (red/orange/yellow/green Pantone codes) are factual; reproduced for interoperation.
