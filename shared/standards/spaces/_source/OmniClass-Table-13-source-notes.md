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

## Phase X re-architecture (2026-06-05)

**Pivot:** Phase X originally planned a 7-category planner split (residential / commercial / institutional / industrial / transport / external / agricultural). Task X.B.1 (residential pattern-setter) discovered via WebFetch of all three declared mirrors that **OmniClass Table 13 does NOT publish a residential parent category**. T13 is *Spaces by Function*; residential dwelling spaces (bedrooms, kitchens, dining rooms, living rooms, hotel/dormitory) are absent from every T13 mirror surveyed.

**Root cause:** OmniClass partitions the discipline space across multiple tables. Residential entities live under **Table 11 — Construction Entities by Function** (single-family residence, multi-family residence, hotel, dormitory) rather than under T13. The original 7-category planner conflated Table-11 entity-types with Table-13 space-functions.

**Resolution:** Phase X re-scopes to the **16 actual OmniClass T13 level-2 parent categories** verified verbatim in the secondary mirror (and corroborated by the NIBS NBIMS-US V3 §2.4.4.3 wrapper). Residential is **deferred to a future Sprint Z** that surveys OmniClass Table 11 sources.

**Failed task:** `shared/standards/spaces/room-types/residential.json` was deleted at re-architecture time. Its 0-coverage record is preserved in commit history.

## 16 verified T13 parent_category names (re-architecture target)

Verbatim parent titles confirmed via WebFetch of the declared secondary mirror (`https://pdfcoffee.com/omniclass-13-2012-05-16-pdf-free.html`) on 2026-06-05, paired with the snake_case canonical used in the `room-types-schema.json` enum:

| OmniClass code | Verbatim title | Snake_case `parent_category` |
| --- | --- | --- |
| 13-11 | Space Planning Types | `space_planning_types` |
| 13-13 | Void Areas | `void_areas` |
| 13-15 | Wall Spaces | `wall_spaces` |
| 13-17 | Encroachment Spaces | `encroachment_spaces` |
| 13-21 | Parking Spaces | `parking_spaces` |
| 13-23 | Facility Service Spaces | `facility_service_spaces` |
| 13-25 | Circulation Spaces | `circulation_spaces` |
| 13-31 | Education and Training Spaces | `education_and_training_spaces` |
| 13-33 | Recreation Spaces | `recreation_spaces` |
| 13-35 | Government Spaces | `government_spaces` |
| 13-37 | Artistic Spaces | `artistic_spaces` |
| 13-41 | Museum Spaces | `museum_spaces` |
| 13-45 | Library Spaces | `library_spaces` |
| 13-47 | Spiritual Spaces | `spiritual_spaces` |
| 13-49 | Environmentally Controlled Spaces | `environmentally_controlled_spaces` |
| 13-51 | Healthcare Spaces | `healthcare_spaces` |

## Per-category transcription tasks (16-task re-plan)

Original 7-task X.B.* plan is superseded. Re-planned task list runs one task per actual T13 parent:

- X.B.1 space_planning_types.json (~18 entries target) — Opus pattern-setter
- X.B.2 void_areas.json (~8 entries target) — Sonnet
- X.B.3 wall_spaces.json (~6 entries target) — Sonnet
- X.B.4 encroachment_spaces.json (~6 entries target) — Sonnet
- X.B.5 parking_spaces.json (~14 entries target) — Sonnet
- X.B.6 facility_service_spaces.json (~22 entries target) — Sonnet
- X.B.7 circulation_spaces.json (~16 entries target) — Sonnet
- X.B.8 education_and_training_spaces.json (~24 entries target) — Sonnet
- X.B.9 recreation_spaces.json (~18 entries target) — Sonnet
- X.B.10 government_spaces.json (~14 entries target) — Sonnet
- X.B.11 artistic_spaces.json (~16 entries target) — Sonnet
- X.B.12 museum_spaces.json (~12 entries target) — Sonnet
- X.B.13 library_spaces.json (~10 entries target) — Sonnet
- X.B.14 spiritual_spaces.json (~10 entries target) — Sonnet
- X.B.15 environmentally_controlled_spaces.json (~22 entries target) — Sonnet
- X.B.16 healthcare_spaces.json (~34 entries target) — Sonnet (largest category — depth focus)

Aspirational total: ~250 entries (mirror-realistic, down from the original 600-entry 7-category aspirational total which depended on a residential category that does not exist in T13).

## Residential — deferred to future Sprint Z

Residential dwelling spaces are out-of-scope for Phase X. A future sprint will:

1. Survey OmniClass **Table 11 — Construction Entities by Function** sources for residential building entity types (single-family, multi-family, hotel, dormitory).
2. Decide whether residential *spaces* (as opposed to *entities*) belong in a new table-11-derived schema, a Uniclass 2015 Table SL (Spaces/Locations) bridge, or a hybrid.
3. Re-introduce a residential entry-set under whichever schema route is chosen, without polluting the T13-only `room-types/` directory.

## Known transcription gaps

(populated by X.B.* implementer reports when mirror coverage < target; currently empty pending X.B task execution)

## CIBSE + NRM2 deferred (paid source access blocker)

Sprint X does NOT transcribe CIBSE LG1/LG2/LG7/LG10/LG12 + Guide A or NRM2. Future Sprint Y back-fills when paid PDFs available. `cross_references.cibse_lg` and `cross_references.nrm2` remain `null` on every Sprint X entry.
