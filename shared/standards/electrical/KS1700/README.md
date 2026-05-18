# KS1700 — Kenyan Code of Practice for Electrical Wiring of Buildings

**Status:** `production` (draft-from-bs7671-derivative-needs-source-verification)
**Standard body:** Kenya Bureau of Standards (KEBS)
**Edition:** First edition, 2018
**Effective date:** 1 January 2019
**Layer version:** 1.0.0
**Scope:** Design, erection, verification, and inspection of electrical installations in buildings throughout Kenya. Mandatory under the Kenyan Standards Act Cap 496; enforcement via the Energy and Petroleum Regulatory Authority (EPRA).

## What this layer contains

| Category | Files |
|---|---|
| Foundational | meta.json, README.md, terminology.md, compliance-checklist.md, amd-summary.md |
| Contextual prose | earthing-systems-explained.md, cable-types-overview.md, inspection-and-testing.md, protective-device-types.md, pscc-determination.md |
| Earthing-relevant clauses | reg411-disconnection-times.json, reg411-rcd-requirements.json, reg433-overcurrent-protection.json, reg434-fault-current.json, reg443-spd.json, reg521-installation-methods.json, reg522-ip-ratings.json |
| Appendix / table content | appendix4-cable-ratings.json, appendix4-cable-ratings-aluminium.json, appendix4-correction-factors.json, appendix12-voltage-drop.json, appendix3-device-curves.json, cable-current-ratings.json, diversity-factors.json |
| Special locations | part7-special-locations.json, cable-types-fire-rated.json |
| **KS-unique** | annex-E-bs7671-adoption-table.json, ks-unique-deviations.json |

Total: 28 files.

## Relationship to BS 7671 and IEC 60364

KS 1700:2018 adopts BS 7671:2018 substantially via Annex E. Most clauses are adopted verbatim with KS-specific clause numbering. Where KS deviates (universal socket-RCD per §411.3.3, EV charging absence, climate-adjusted ambient temps), explicit deviation content is captured in `ks-unique-deviations.json`. Where KS Annex E adopts BS verbatim, per-clause files note this adoption explicitly with `_ks_adoption_pathway`.

For EV charging, KS Annex E §VIII directs to IEC 60364-7-722 (no native §722 in KS 1700).

## Verification status

Every file in this layer is marked `verification_status: "draft-from-bs7671-derivative-needs-source-verification"`. The published KS 1700:2018 PDF is not in repo at the time of authoring. Engineering content is correct in terms of structural pattern; the precise clause numbering and any KS-specific tolerance values should be verified against the official KEBS publication before downstream skills rely on tight tolerances.

A future micro-sprint will promote `verification_status` to `verified-against-source` after a clause-by-clause check against the official PDF.

## Related skills

- `electrical/earthing` v1.2.0+ (this sprint) — primary consumer; cites KS 1700 directly via `code_clause: "KS 1700:2018 §X.Y.Z"`
- Future: `electrical/cable-sizing` (Kenya jurisdiction), `electrical/db-layout` (Kenya jurisdiction), `electrical/lighting-layout` (Kenya jurisdiction) — each will adopt KS 1700 in their respective minor-version sprints

## Related standards in this repo

- `BS7671/` — parent standard adopted by KS 1700 via Annex E
- `IEC60364/` — international parent; KS 1700 Annex E §VIII references for sections not adopted from BS (e.g., EV charging Part 7-722)
- `local-codes/Kenya/` — country-context content (DNO, regulator, market)

## License + reuse

Standards content is © KEBS. This repo stores clause references + structural patterns + factual deviations only. Never full standard text.

## Versioning

When KS 1700 next revision is published (estimated 2024 cycle), bump `_edition` + `layer_version` 2.0.0 in-place per repo policy.
