# ISO-7010 — ISO 7010:2019 Graphical Symbols — Safety Signs

**Status:** `production` — used by `electrical/arc-flash-labelling` for international + EU safety labels
**Standard body:** ISO
**Edition:** 2019 (current)
**Layer version:** 1.0.0
**Scope:** Standardised graphical symbols for safety signs. Used internationally as the canonical warning-symbol set; the W-series symbols are referenced by NFPA 70E and similar standards as the visual hazard glyph.

## What this layer contains

| Category | Files |
|---|---|
| Warning signs | warning-signs.json (W-series — W012 is arc-flash hazard) |
| Colour spec | colour-spec.json (yellow / black / red / blue / green safety palette) |
| Terminology | terminology.md (sign-shape conventions, colour meanings) |
| Compliance | compliance-checklist.md |

Total: 6 files in this layer.

## Related skills

- `electrical/arc-flash-labelling` (this sprint) — primary consumer for EU + INT label rendering

## How this differs from ANSI Z535.4

| Aspect | ANSI Z535.4 (US) | ISO 7010 (INT / EU) |
|---|---|---|
| Signal-word panel | Coloured background + uppercase signal word | No signal-word panel; visual hierarchy via symbol shape |
| Hazard symbol | Inside coloured banner | Standalone, dominant; yellow triangle + black border + black symbol |
| Colour scheme | Red/Orange/Yellow/Blue/Green | Yellow (warning) / Red (prohibition) / Blue (mandatory) / Green (safe) |
| Text language | English (typically); language-flexible | Symbol-first; text optional + language-flexible |

The skill renders different visual layouts per format; ISO 7010 leans more icon-driven, ANSI Z535.4 more text-driven.

## License + reuse

Standards content is © ISO. This repo stores symbol IDs + colour codes + brief paraphrase. Full standard text is never reproduced.
