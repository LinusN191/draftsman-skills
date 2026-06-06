# Room Types — Canonical Taxonomy

Canonical comprehensive room-type taxonomy sourced from three complementary standards: OmniClass Table 13 (Sprint X), Uniclass 2015 Table SL (Sprint Z), and OmniClass Table 11 (Sprint Z). Aligned with ISO 16739 IFC IfcSpaceTypeEnum + IfcClassificationReference.

This catalogue is the source of truth for `Room.type` values in the SkillInput contract (see `shared/schemas/core/skill-input.schema.json`). Orchestrators construct `Room.type` strings using `canonical_id` values from these files.

## Files (3-taxonomy structure)

### Schema + master index
- `room-types-schema.json` — Draft-07 per-entry metaschema with `taxonomy_source` discriminator
- `room-types.json` — master index referencing all 3 catalogues
- `fuzzy-match-reference.md` — algorithm spec for orchestrators

### OmniClass Table 13 — Spaces by Function (290 entries, Sprint X)
- `room-types/<category>.json` — 13 per-category files: space_planning / parking / facility_service / circulation / education / recreation / government / artistic / museum / library / spiritual / environmentally_controlled / healthcare
- `_source/OmniClass-Table-13-source-notes.md` — provenance

### Uniclass 2015 Table SL — comprehensive room-level (Sprint Z)
- `room-types-uniclass-sl/<category>.json` — 7 per-category files: residential / commercial / retail / hospitality / industrial / agricultural / transport
- `_source/Uniclass-2015-SL-source-notes.md` — provenance

### OmniClass Table 11 — Construction Entities (Sprint Z)
- `building-types-t11/construction-entities-by-function.json` — building-type catalogue for SL→T11 cross-reference rollup
- `_source/OmniClass-Table-11-source-notes.md` — provenance

## When to consume which taxonomy

- **Healthcare / education / circulation / facility / theatre rooms** → OmniClass T13
- **Residential / hotel / office / retail / restaurant / industrial / agricultural / warehouse rooms** → Uniclass SL
- **Building-type rollup (e.g. "this room is in a hotel building")** → OmniClass T11 via SL→T11 cross-references in `building_type_codes[]`

## How to consume

1. Validate `Room.type` value against the union of `canonical_id` keys across all relevant `room-types/*.json` and `room-types-uniclass-sl/*.json` files
2. Resolve metadata (OmniClass / Uniclass code + IFC space type + cross-references) by lookup
3. Use `common_aliases` for fuzzy-match of non-canonical strings from drawing parsers
4. Check `taxonomy_source` discriminator to determine which schema validation path applies

## Coverage — honest disclosure

- **OmniClass T13 (Sprint X):** ~290 entries; secondary mirror covers approximately 40–50% of the aspirational ~600-entry target. Future Sprint Y back-fill from canonical OCCS PDF (CSI license) will extend coverage.
- **Uniclass SL (Sprint Z):** ~270 entries across 7 categories; sourced from NBS primary mirror (v1.35 April 2026) + buildig CSV secondary mirror (v1.22). Agricultural and hospitality coverage is MEDIUM (multi-group spread; see source-notes).
- **OmniClass T11 (Sprint Z):** ~70 entries; sourced from NIBS V3 2.4.4.1 PDF (2012 DRAFT modified 2013-02-26). No machine-readable public mirror — verbatim coverage expected 40–60%.

The `_coverage_actual_pct` field in each per-category file records the actual fraction of the target achieved.

## CIBSE + NRM2 cross-references — deferred (paid source access blocker)

Sprint X + Sprint Z do NOT transcribe CIBSE LG series or NRM2. `cross_references.cibse_lg` and `cross_references.nrm2` are `null` on every entry. Future Sprint Y back-fills when paid PDFs are available.

## Sourcing discipline

Every entry MUST have `_verification_status` populated:

- `mirror_sourced` — verbatim from declared OmniClass public mirror (T13 + T11)
- `nbs_sourced` — verbatim from NBS Source primary mirror or buildig CSV secondary mirror (Uniclass SL)
- `occs_verified` — cross-checked against canonical OCCS PDF (Sprint X + Z do NOT set this; reserved for Sprint Y)
- `inferred` — synthesised from hierarchy structure with explicit `_inference_note`
- `engineering_consensus` — Uniclass-style code synthesised when NBS Source coverage is partial, citing CIBSE / ASHRAE / BS authority

Fabricating codes that do not exist in declared mirrors is a CRITICAL violation.

## OmniClass T13 edition

- **Primary authority:** NBIMS-US V3 wrapper PDF confirming May 2011 edition (https://nibs.org/...)
- **Verbatim code list:** Secondary mirror, edition 2012-05-16 (https://pdfcoffee.com/omniclass-13-2012-05-16-pdf-free.html)

See `_source/OmniClass-Table-13-source-notes.md` for full provenance detail.

## Uniclass SL edition

- **Primary mirror:** https://uniclass.thenbs.com/taxon/sl — v1.35, April 2026

See `_source/Uniclass-2015-SL-source-notes.md` for full provenance detail.

## OmniClass T11 edition

- **Primary mirror:** https://nibs.org/wp-content/uploads/2025/04/NBIMS-US_V3_2.4.4.1_OmniClass_Table_11_Construction_Entities_by_Function.pdf — 2012 DRAFT modified 2013-02-26

See `_source/OmniClass-Table-11-source-notes.md` for full provenance detail.
