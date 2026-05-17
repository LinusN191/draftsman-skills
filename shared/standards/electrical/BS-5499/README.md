# BS-5499 — BS 5499:Safety Signs Including Fire Safety Signs

**Status:** `production` — used by `electrical/arc-flash-labelling` for UK + GB-jurisdiction labels
**Standard body:** BSI
**Edition:** Latest (BS 5499 is a multi-part series; relevant parts updated 2002–2015)
**Layer version:** 1.0.0
**Scope:** UK safety-signage conventions. Mostly aligned with ISO 7010 (BS 5499 was harmonised with ISO 7010 in 2010) but adds UK-specific language + HSG48 framing.

## What this layer contains

| File | Purpose |
|---|---|
| README.md | This file |
| meta.json | Layer metadata |
| uk-conventions.md | UK-specific language + HSG48 framing + BS 7671 references |
| compliance-checklist.md | When a UK arc-flash label is HSG48-compliant |

Total: 4 files (light layer — mostly references ISO 7010 with UK-specific overrides).

## Related skills

- `electrical/arc-flash-labelling` (this sprint) — primary consumer for GB-jurisdiction labels

## How this differs from ISO 7010 / ANSI Z535.4

BS 5499 adopts ISO 7010 symbols + colours but adds:
- English signal-word text supplementary to symbols (Z535.4-style "DANGER" / "WARNING")
- HSG48 voluntary best-practice framing (UK arc-flash labels are recommended, not statutory)
- BS 7671:2018 cross-references for any electrical-specific language
- UK PPE language conventions (BS EN ISO 11611 PPE certification vs Z535's NFPA 70E)

For UK-jurisdiction projects, the labelling skill renders a hybrid format: ISO 7010 symbol panel + BS-5499 English signal-word + NFPA 70E content fields. This is the de facto UK convention.

## License + reuse

Standards content is © BSI. This repo stores brief paraphrase + cross-references only — never full standard text.
