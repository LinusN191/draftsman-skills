# OmniClass Table 11 — Source Notes

**Last updated:** 2026-06-06

## Source mirror (primary)

- **URL:** https://nibs.org/wp-content/uploads/2025/04/NBIMS-US_V3_2.4.4.1_OmniClass_Table_11_Construction_Entities_by_Function.pdf
- **Access date:** 2026-06-06
- **Edition reflected:** OmniClass Table 11 — Construction Entities by Function, **2012 DRAFT modified by Committee action 2013-02-26** (Pre Consensus Approved Draft status, embedded by reference into NBIMS-US V3, published 2015 by the National Institute of Building Sciences buildingSMART alliance)
- **Coverage estimate:** Authority citation only. 61-page PDF; binary stream extraction at access date returned non-text — full verbatim code transcription from this PDF alone is impractical for the Z.C implementer without manual page-by-page reading. **Use as the AUTHORITY citation; pair with the secondary mirror for code-level corroboration.**
- **Code format expected:** Canonical `11-XX XX XX XX XX` (five-level hierarchy), matching the OmniClass series convention used by Table 13 / Table 21 / Table 49.

## Source mirror (secondary — corroboration of NIBS wrapper)

- **URL:** https://www.scribd.com/document/468276520/NBIMS-US-V3-2-4-4-1-OmniClass-Table-11-Construction-Entities-by-Function-pdf
- **Access date:** 2026-06-06
- **Edition reflected:** Same NBIMS-US V3 2.4.4.1 wrapper (61 pages, uploaded by user "Jesus Perez" 2020). Confirms file identity matches the NIBS-hosted PDF.
- **Use:** Identity corroboration only. Scribd preview does NOT expose machine-readable code list; Z.C implementer reads the NIBS PDF directly.

## Source mirror (tertiary — categorical scope sketch)

- **URL:** https://biblus.accasoftware.com/en/ifc-objects-omniclass-classification/
- **Access date:** 2026-06-06
- **Use:** Confirms Table 11 root `11-00 00 00` covers "private residences, hotels, congress centres, bus stations, motorways" — i.e. residential / hospitality / civic / transport functions. Does NOT enumerate verbatim codes; categorical sanity-check only.

## Authoritative source (licensed — NOT used)

- **URL:** http://www.omniclass.org/tables.asp (CSI Construction Specifications Institute)
- **Status:** Licensed-only access via CSI Dynamic Standards. Sprint Z does NOT acquire. Future Sprint Y when CSI licence granted will back-fill `_verification_status: occs_verified` on T11 entries that round-trip against the canonical source.

## Coverage gap honest disclosure

Sprint X X.A.0 declared `pdfcoffee.com OmniClass 13 2012-05-16` as the verbatim-code secondary mirror for Table 13. **No equivalent pdfcoffee mirror exists for Table 11** at access date (2026-06-06). Web searches surface pdfcoffee Tables 13, 21, and 22 but not Table 11. Therefore:

1. The Z.C implementer's primary code source is the NIBS V3 2.4.4.1 PDF read page-by-page (Pre Consensus Approved Draft 2013-02-26 codes).
2. Verbatim code coverage is expected to be **lower than Sprint X T13 (which hit ~70–80%)**. Sprint Z plan portion 1 projects ~70 T11 entries; realistic verbatim public coverage is closer to **40–60%** because no machine-readable mirror is in the public corpus.
3. Z.C entries unable to source verbatim from NIBS PDF MUST land as `_verification_status: inferred` with `_inference_note` citing the NIBS V3 2.4.4.1 wrapper as the structural authority. **No fabrication.** No invented code numbers without an `_inference_note` declaring the parent code consulted.

## Verification status taxonomy

See `docs/superpowers/specs/sprint-Z-source-provenance.md` §3.

- `mirror_sourced` — code transcribed verbatim from the NIBS V3 2.4.4.1 PDF. **Default state for T11 entries that round-trip against the PDF.**
- `occs_verified` — cross-checked against the canonical OCCS Table 11 PDF licensed via CSI. **Sprint Z does NOT set this state.** Reserved for future Sprint Y.
- `inferred` — code synthesised from hierarchy structure where PDF coverage is incomplete (e.g. NIBS PDF shows parent `11-XX 00 00 00 00` but no readable child entries; child code synthesised from OmniClass numbering convention). MUST be honest-disclosed in per-entry `_inference_note` explaining the parent code consulted and the numbering pattern applied.

## Per-task transcription

- Z.C.1 construction-entities-by-function.json (~70 entries) — Opus

## Known transcription gaps

(populated by Z.C.1 implementer report)

## What Table 11 covers

OmniClass Table 11 classifies **whole construction entities by function** (single-family residence, hotel building, office building, warehouse, etc.) — NOT rooms within them. Room-level taxonomy for residential / hotel / etc. lives in Uniclass SL (see Z.B.*).

## Cross-reference role

Sprint Z Uniclass SL room entries reference T11 building codes via `building_type_codes[]` field. Example: `residential.bedroom_master` → `["11-11 11 11"]` (single-family residence).

## CIBSE + NRM2 deferred (paid source access blocker)

Sprint Z does NOT transcribe CIBSE LG series or NRM2. `cross_references.cibse_lg` and `cross_references.nrm2` stay `null` on every Sprint Z entry.
