# Room Types — Canonical Taxonomy

Canonical comprehensive room-type taxonomy sourced from OmniClass Table 13 (publicly-available mirror) and aligned with ISO 16739 IFC IfcSpaceTypeEnum + IfcClassificationReference.

This catalogue is the source of truth for `Room.type` values in the SkillInput contract (see `shared/schemas/core/skill-input.schema.json`). Orchestrators construct `Room.type` strings using `canonical_id` values from these files.

## Files

- `room-types-schema.json` — Draft-07 metaschema for per-entry validation
- `room-types.json` — master index referencing 7 per-category files
- `room-types/<category>.json` — per-category entries (7 files; created in Sprint X.B)
- `_source/OmniClass-Table-13-source-notes.md` — mirror URL + edition + access date + transcription gaps

## How to consume

1. Validate `Room.type` value against the union of `canonical_id` keys across all `room-types/*.json` files
2. Resolve metadata (OmniClass code + IFC space type + cross-references) by lookup
3. Use `common_aliases` for fuzzy-match of non-canonical strings from drawing parsers

## Coverage — honest disclosure

The secondary mirror used for Sprint X transcription (~250–300 entries) covers approximately **40–50% of the aspirational 600-entry target** across all 7 categories. The `entry_count_target` values in `room-types.json` are aspirational based on the expected full OmniClass Table 13 scope.

The `_coverage_actual_pct` field in each per-category file (set during Sprint X.B tasks) records the actual fraction of the target achieved from the secondary mirror.

**Future Sprint Y** back-fill from the canonical OCCS PDF (CSI license) will extend coverage toward 100% and raise per-entry `_verification_status` from `mirror_sourced` to `occs_verified`.

## CIBSE + NRM2 cross-references — deferred (paid source access blocker)

Sprint X does NOT transcribe CIBSE LG1/LG2/LG7/LG10/LG12 + Guide A or NRM2 (paid PDF sources). `cross_references.cibse_lg` and `cross_references.nrm2` are `null` on every Sprint X entry.

**Future Sprint Y will back-fill these cross-references when paid PDFs are made available to the project.**

## Sourcing discipline

Every entry MUST have `_verification_status` populated:

- `mirror_sourced` (default): verbatim from declared public mirror
- `occs_verified`: cross-checked against canonical OCCS Table 13 PDF (back-fill; Sprint X does NOT set this)
- `inferred`: synthesised from hierarchy structure with explicit `_inference_note`

Fabricating codes that do not exist in declared mirrors is a CRITICAL violation caught at Sprint X.E.4 final review spot-check.

## OmniClass edition

- **Primary authority:** NBIMS-US V3 wrapper PDF confirming May 2011 edition (https://nibs.org/...)
- **Verbatim code list:** Secondary mirror, edition 2012-05-16 (https://pdfcoffee.com/omniclass-13-2012-05-16-pdf-free.html)

See `_source/OmniClass-Table-13-source-notes.md` for full provenance detail.
