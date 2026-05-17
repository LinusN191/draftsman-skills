# ANSI-Z535-4 — ANSI Z535.4:2023 Product Safety Signs and Labels

**Status:** `production` — sign-format spec for arc-flash labels
**Standard body:** ANSI / NEMA
**Edition:** 2023 (current)
**Layer version:** 1.0.0
**Scope:** Format, colour, symbol, panel-layout, and content requirements for product safety signs + labels. The canonical sign-format spec referenced by NFPA 70E §130.5(H) for arc-flash labels.

## What this layer contains

| Category | Files |
|---|---|
| Signal words | signal-words.json (DANGER / WARNING / CAUTION / NOTICE + colours + triggers) |
| Colour spec | colour-spec.json (Pantone / CMYK / RGB / hex per safety colour) |
| Symbol library | symbol-library.json (arc-flash, electric shock, hazard alert, PPE symbols) |
| Panel format | panel-format.json (signal-word + message + symbol panel layout rules) |
| Letter height | letter-height-requirements.json (legibility per working distance) |
| Label content | label-content-rules.json (NFPA 70E §130.5(H) field requirements + ordering) |
| Arc-flash template | arc-flash-label-template.md (canonical Z535.4 + NFPA 70E layout in prose) |

Total: 11 files in this layer.

## Related skills

- `electrical/arc-flash-labelling` (planned v1.0.0 — this sprint) — primary consumer

## License + reuse

Standards content is © ANSI/NEMA. This repo stores clause references + factual colour codes (Pantone refs are facts, not copyrighted expression) + brief paraphrase. Never full standard text.

## Versioning

When ANSI Z535.4:2028 (estimated revision cycle) is published, bump `edition` + `layer_version` 2.0.0 in-place per repo policy.
