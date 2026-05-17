# Changelog — electrical/arc-flash-labelling

All notable changes. Follows [Keep a Changelog](https://keepachangelog.com).

## [1.0.0-beta] — 2026-05-17

### Added — v1.0.0 beta (unified Phase A + B sprint)

**Phase A — standards layers shipped alongside:**
- `shared/standards/electrical/ANSI-Z535-4/` promoted stub → production (11 files)
- `shared/standards/electrical/ISO-7010/` NEW layer (6 files)
- `shared/standards/electrical/BS-5499/` NEW layer (4 files)

**Phase B — the skill:**
- 12-step generator chain (`prompts/generator.md`)
- Labels IR + slim labels intent (`schemas/`)
- 4 rules: jurisdiction-format-selection, signal-word-policy, label-content-population, ppe-clothing-description
- 3 constraints: required-content-present, colour-spec-compliance, letter-height-legibility
- 3 validation YAMLs (9 deterministic checks)
- 2 ontology files: label-formats (4 entries) + signal-words (5 entries)
- 4 SVG templates: ansi-z535-4 / iso-7010 / bs-5499 / restricted
- 8 evals (5 WI5 categories + 3 skill-specific)
- 3 worked examples (US ANSI / UK BS-5499 / INT ISO-7010)

**New calc contract:**
- `calc.render_label` at `shared/calculations/electrical/render-label.json` (SVG → PDF/PNG, deferred per WI3)

### Consumes intents
- `arc-flash` (per-equipment IE / AFB / PPE / shock-approach / label_recommended)

### Produces intent
- `labels` (per-equipment label metadata; consumed by facility-management / digital-twin systems)

### Renderings
- SVG inline (LLM-produced from template; engineers preview in browser)
- PDF / PNG / project-label-index PDF deferred to `calc.render_label` runtime tool per WI3

### Method scope
- ANSI Z535.4 (US default)
- ISO 7010 (EU/INT default)
- BS 5499 (GB default)
- RESTRICTED format (IE > 40 cal/cm² — safety override; supersedes jurisdiction)
