# `arc-flash-labelling` — Printable Arc-Flash Warning Labels (ANSI Z535.4 / ISO 7010 / BS 5499)

**Status:** `beta`
**Version:** `1.0.0`
**Drawing type:** `arc_flash_labelling_study`
**Sprint scope:** Unified Phase A (3 standards layers) + Phase B (skill)
**Reference:** `electrical/fault-level` + `electrical/cable-sizing` + `electrical/arc-flash` (proven artefact pattern)

## What this skill produces

A project-scoped labels IR with per-equipment arc-flash warning labels per regional safety standards (ANSI Z535.4 / ISO 7010 / BS 5499 — jurisdiction-aware), with all NFPA 70E §130.5(H) required content. Each label entry carries inline SVG content; PDF + PNG rendering deferred to `calc.render_label` runtime tool per WI3.

**Plus a `labels` intent** (slim downstream subset) consumed by future facility-management / digital-twin systems.

## Standards layers consumed (all production)

| Layer | Files | Role |
|---|---|---|
| `shared/standards/electrical/ANSI-Z535-4/` | 11 | US format (DANGER/WARNING/CAUTION + Pantone palette + sign-panel layout) |
| `shared/standards/electrical/ISO-7010/` | 6 | International format (W012 arc-flash hazard + colour palette) |
| `shared/standards/electrical/BS-5499/` | 4 | UK conventions (ISO 7010 + English signal-word supplementation + HSG48 framing) |
| `shared/standards/electrical/NFPA70E/` (selected) | 4 | Required content per §130.5(H) + PPE category/clothing tables |

## Jurisdictions supported

| Jurisdiction | Default format | Notes |
|---|---|---|
| US | `ansi_z535_4` | Coloured signal-word panel + Z535.4 text style |
| EU | `iso_7010` | Symbol-first + supplementary text |
| INT | `iso_7010` | Same as EU |
| GB | `bs_5499` | ISO 7010 + English signal words + HSG48 framing |

**RESTRICTED override:** When incident energy > 40 cal/cm² (above NFPA 70E Cat 4 ceiling), `restricted_format` is auto-selected REGARDLESS of jurisdiction. Distinct purple/black visual treatment + DO NOT OPERATE overlay + "Energized work prohibited" text.

## Eval coverage matrix

| Eval ID | Category | Tests |
|---|---|---|
| eval-01-us-mixed-cascade-ansi-labels | happy_path | US 480V cascade, ANSI Z535.4 |
| eval-02-restricted-equipment-distinct-format | edge_case | IE = 45 → RESTRICTED format |
| eval-03-missing-arc-flash-data-skip | validation_trap | Null IE → "Not computed" placeholder |
| eval-04-no-arc-flash-intent | missing_input | Empty labels[] + assumption log |
| eval-05-jurisdiction-gb-bs5499 | jurisdiction_switch | GB → BS-5499 auto-selected |
| eval-06-rationale-block | rationale_block | 8 sections + chat_summary |
| eval-07-svg-template-population | skill_specific | SVG content fully populated, no `{{...}}` |
| eval-08-qr-code-conditional-emission | skill_specific | URL emitted only if base_url declared |

## Tool calls awaiting runtime

| Tool name | Purpose | Status |
|---|---|---|
| `calc.render_label` | Convert SVG markup to PDF/PNG bytes | tool_call_pending_for_pdf_png until DraftsMan runtime ships |

SVG content is rendered inline by the skill (LLM-readable + LLM-writable from templates). Engineers can preview labels in any browser before the runtime tool exists.

## File structure

```
electrical/arc-flash-labelling/
├── README.md, CHANGELOG.md, skill.manifest.json, inputs.json
├── prompts/ (generator 12-step / validator 8 INV / reviewer 6 D)
├── schemas/ (labels-ir + labels-intent)
├── rules/ (4 YAMLs: jurisdiction format + signal word + content + PPE)
├── constraints/ (3 YAMLs, 9 checks: required content + colour + legibility)
├── validation/ (3 YAMLs, 9 checks: IR integrity + jurisdiction match + intent)
├── ontology/ (label-formats + signal-words)
├── docs/ (engineering-philosophy + known-limitations)
├── evals/ (runner-config + 8 evals)
├── templates/ (4 SVG: ansi-z535-4 + iso-7010 + bs-5499 + restricted)
└── examples/ (US ANSI / UK BS-5499 / INT ISO-7010 with mixed RESTRICTED)
```

Plus the new calc contract at `shared/calculations/electrical/render-label.json`.

## Known limitations

See `docs/known-limitations.md`. v1.0.0 does NOT cover:
- Physical label printing (downstream concern)
- PDF/PNG generation (deferred to `calc.render_label` runtime)
- Custom company branding (beyond placeholder support; defer to v1.1)
- Multi-language labels (English only at v1.0; v1.1)
- Old NFPA 70E:2018 format (renders to 2024 only)
- Tactile / Braille labels

## Versioning

- Minor (1.x.0): new formats (Australian AS 1319), bilingual, branding overlays
- Major (2.0.0): breaking schema OR Z535.4 / ISO 7010 revision adoption
- Patch (1.0.x): rules / templates / SVG fixes

## License

See repository root `LICENSE`.
