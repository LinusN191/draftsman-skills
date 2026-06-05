# OmniClass Table 13 — Source Notes

**Last updated:** 2026-06-05

## Source mirror (primary)

- **URL:** https://nibs.org/wp-content/uploads/2025/04/NBIMS-US_V3_2.4.4.3_Omniclass_Table_13_Spaces_by_Function.pdf
- **Access date:** 2026-06-05
- **Edition reflected:** OmniClass Table 13 — Spaces by Function, May 2011 (incorporated by reference into NBIMS-US V3, published 2015 by the National Institute of Building Sciences buildingSMART alliance)
- **Coverage estimate:** Authoritative wrapper PDF — confirms scope, normative references (ISO 12006-2, ISO TR 14177), and bibliography, but the embedded May 2011 table is referenced by inclusion rather than re-typeset in full. Use as the **authority citation** for code legitimacy; pair with the secondary mirror below for the verbatim code list.
- **Code format observed:** Canonical `13-XX XX XX XX XX` (five-level hierarchy), consistent with the published May 2011 edition.

## Source mirror (secondary — verbatim code list)

- **URL:** https://pdfcoffee.com/omniclass-13-2012-05-16-pdf-free.html
- **Access date:** 2026-06-05
- **Edition reflected:** OmniClass Table 13 — Spaces by Function, **2012-05-16** (next minor revision after May 2011; National Standard status)
- **Coverage estimate:** ~250–300 code entries across all parent categories; covers ~50% of the aspirational ~600-entry target in room-types.json. Gaps are concentrated in deepest level-5 entries (13-XX XX XX XX XX) within Healthcare (13-51) and Environmentally Controlled (13-49).
- **Parent categories confirmed present:** 13-11 Space Planning Types, 13-13 Void Areas, 13-15 Wall Spaces, 13-17 Encroachment Spaces, 13-21 Parking Spaces, 13-23 Facility Service Spaces, 13-25 Circulation Spaces, 13-31 Education and Training Spaces, 13-33 Recreation Spaces, 13-35 Government Spaces, 13-37 Artistic Spaces, 13-41 Museum Spaces, 13-45 Library Spaces, 13-47 Spiritual Spaces, 13-49 Environmentally Controlled Spaces, 13-51 Healthcare Spaces.

## Source mirror (backup — corroboration only)

- **URL:** https://www.scribd.com/document/958191411/13-OmniClass
- **Access date:** 2026-06-05
- **Edition reflected:** OmniClass Table 13, 2012-05-16 edition (same as secondary mirror)
- **Use:** Spot-check the secondary mirror's level-5 codes if any individual code reads suspect.

## Authoritative source (paid — NOT used in Sprint X)

- **URL:** http://www.omniclass.org/tables.asp (CSI Construction Specifications Institute)
- **Status:** Licensed-only access via CSI Dynamic Standards. Sprint X does NOT acquire. Future Sprint Y when CSI license granted will back-fill `_verification_status: occs_verified` on entries that round-trip against this canonical source.

## Coverage disclosure

The secondary mirror (~250–300 entries) provides approximately **40–50% of the aspirational ~600-entry target** in `room-types.json`. The per-category `entry_count_target` fields in `room-types.json` are aspirational targets based on the expected full OmniClass Table 13 scope. The `_coverage_actual_pct` field in each per-category file records the fraction of that target actually transcribed from the secondary mirror.

Future Sprint Y back-fill from the canonical OCCS PDF (CSI license) will:
1. Raise `_verification_status` from `mirror_sourced` to `occs_verified` on all confirmed entries
2. Add missing level-5 entries (primarily Healthcare + Environmentally Controlled parent categories)
3. Set `_coverage_actual_pct` to 100% where applicable

## Verification status taxonomy

See `docs/superpowers/specs/sprint-X-source-provenance.md` §4 for full definitions.

- `mirror_sourced` — verbatim from declared secondary mirror URL (default for Sprint X)
- `occs_verified` — cross-checked against canonical OCCS PDF (Sprint X does NOT set this)
- `inferred` — synthesised from hierarchy structure; MUST include `_inference_note`

## Per-category transcription tasks

- X.B.1 residential.json (~80 entries target) — Opus pattern-setter
- X.B.2 commercial.json (~120 entries target) — Sonnet
- X.B.3 institutional.json (~150 entries target) — Sonnet
- X.B.4 industrial.json (~130 entries target) — Sonnet
- X.B.5 transport.json (~60 entries target) — Sonnet
- X.B.6 external.json (~40 entries target) — Sonnet
- X.B.7 agricultural.json (~20 entries target) — Sonnet

## Known transcription gaps

(populated by X.B.* implementer reports when mirror coverage < target; currently empty pending X.B task execution)

## CIBSE + NRM2 deferred (paid source access blocker)

Sprint X does NOT transcribe CIBSE LG1/LG2/LG7/LG10/LG12 + Guide A or NRM2. Future Sprint Y back-fills when paid PDFs available. `cross_references.cibse_lg` and `cross_references.nrm2` remain `null` on every Sprint X entry.
