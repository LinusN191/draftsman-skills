# NFPA 70 — National Electrical Code (NEC)

**Standard:** NFPA 70 (US National Electrical Code)
**Canonical edition:** 2023
**Cycle:** 3 years (2017 → 2020 → 2023 → 2026)
**Scope of this layer:** All 9 Chapters with per-article depth and worked examples.

This layer is the US-side electrical standards source of truth. It complements:

- **IEC 60364** — international electrical-installations standard. Every NFPA article entry cross-references the equivalent IEC clause via `related_iec_60364` and flags conflicts in `divergence_notes`. See `nec-vs-iec-comparison.md` for the full divergence catalogue.
- **IEC 60617** — graphical symbols. NFPA article entries that describe specific device types reference IEC 60617 `symbol_id` values via `drawn_as`.

**Designers working bi-jurisdiction projects:** load this layer + IEC 60364 + the comparison MD. The `divergence_notes` per article surface the conflicts at the article level.

---

## Files

| File | Purpose |
|---|---|
| `meta.json` | Standard title, edition history, state-adoption map, relationship to NFPA 70E/72/110/111 |
| `chapter1-general.json` | Articles 90 (Intro), 100 (Definitions), 110 (General installation requirements) |
| `chapter2-wiring-protection.json` | Articles 200, 285 (light); pointers to 210/215/220/230/240/250 |
| `chapter3-wiring-methods.json` | Articles 300, 312, 314, 320-399 (raceways, cables, boxes); pointer to 310 |
| `chapter4-equipment.json` | Articles 400, 402, 404, 406, 408, 410, 422, 426, 427, 440, 460, 480; pointers to 430, 450 |
| `chapter5-special-occupancies.json` | Articles 511, 513, 514, 515, 516, 518, 520, 530, 547, 590; pointers to 500-506, 517 |
| `chapter6-special-equipment.json` | Articles 600, 604, 610, 620, 630, 645, 647, 660, 665, 670, 685; pointers to 625, 680, 690, 695 |
| `chapter7-special-conditions.json` | Articles 706, 710, 712, 720, 725, 727, 728, 760, 770; pointer to 700-705 |
| `chapter8-communications.json` | Articles 800, 805, 810, 820, 830, 840 (standalone chapter under NEC) |
| `chapter9-tables.json` | Tables 1-10 — conduit fill, conductor properties (AWG/kcmil area, R, X), conduit/tubing dimensions, voltage drop multipliers |
| `art210-branch-circuits.json` … `art700-705-emergency-standby.json` | 17 per-heavy-article files (210, 215, 220, 230, 240, 250, 310, 408, 430, 450, 500-506 bundle, 517, 625, 680, 690, 695, 700-705 bundle) |
| `grounding-and-bonding.json` | Unified grounding treatment across 250, 300.5, 310, 408, 450 — GEC sizing, EGC matrix, electrode types, bonding hardware |
| `ocpd-coordination.json` | Selective coordination across 240, 700.32, 701.32, 645.27, 695.6 — methods, series ratings, fuse-MCB coordination |
| `hazardous-locations-classification.json` | Unified Class/Division (US legacy) and Class/Zone (IEC-aligned) per 500-506; gas/dust group conversion; equipment selection matrix |
| `ampacity-correction-factors.json` | Ambient (310.15(B)(2)(a)), grouping (310.15(C)), termination rule (110.14(C)), demand factors (220 series) |
| `conduit-fill.json` | Chapter 9 Table 1 fill %, Table 4 raceway dimensions, Table 5 conductor dimensions, conduit-type selection matrix |
| `wiring-methods-by-occupancy.json` | Decision matrix: which raceway/cable types in which occupancies. NM/AC/MC/MI in dwellings vs commercial vs healthcare vs hazardous |
| `amendments-summary.md` | Edition history; 2020→2023 key changes |
| `nec-vs-iec-comparison.md` | Terminology, conductor sizing, earthing, OCPD, hazardous-location, EV/PV/pools/healthcare divergences |
| `compliance-checklist.md` | Designer-side checklist by project type |
| `terminology.md` | NEC↔IEC critical-distinction glossary |
| `worked-examples.md` | 7 worked examples |

---

## How skills use this layer

**Specifying to NEC for a US project:**
1. Load `chapter<n>-*.json` for general requirements.
2. For heavy articles cited in the design (e.g. 250 grounding), load the dedicated `art<num>-*.json`.
3. Copy `key_sections`, `tables_inline`, and `common_errors` into the skill's reasoning.

**Working bi-jurisdiction (US + international):**
1. Load NEC article AND its `related_iec_60364` references.
2. Read `divergence_notes` per article — surface in rationale.
3. Use the comparison MD for terminology reconciliation.

**Per-article schema invariant:** every entry across the 9 chapter files and 17 per-article files has the same 17 mandatory fields. Skills can rely on this.

---

## Per-article schema

```json
{
  "article_id":        "ART_<number>",
  "nec_ref":           "NFPA 70:2023 Article <number>",
  "chapter":           <int 1-9>,
  "article_number":    <int>,
  "article_title":     "<verbatim NEC title>",
  "scope":             "<applicability and boundary>",
  "applies_to":        ["<tag>", ...],
  "key_sections":      [{"section": "<§>", "title": "<string>", "summary": "<string>"}],
  "tabulated_values":  {"<table_name>": "<description>"},
  "tables_inline":     {"<Table_id>": {"title": "<string>", "rows": [...]}},
  "common_errors":     ["<string>", ...],
  "drawn_as":          ["<IEC60617 symbol_id>", ...],
  "related_iec_60364": ["<IEC clause>", ...],
  "divergence_notes":  "<single paragraph — required>",
  "related_bs_7671":   [],
  "usage_notes":       "<designer guidance>",
  "related_articles":  ["ART_<num>", ...]
}
```

See `docs/superpowers/specs/2026-05-15-nfpa70-standard-layer-design.md` for full field definitions.

---

## Coverage scope

**In scope:** All 9 Chapters of NEC 2023 — full coverage including Chapter 8 (communications).

**Out of scope:**
- NFPA 70E (workplace electrical safety)
- NFPA 72 (fire alarm beyond Article 760)
- NFPA 110/111 (standby/storage beyond Articles 700-706)
- State amendments (California Electrical Code, Massachusetts Electrical Code, etc.)
- UL equipment standards referenced by NEC
- Pre-1999 Class/Division-only legacy material
- NEC editions other than 2023
