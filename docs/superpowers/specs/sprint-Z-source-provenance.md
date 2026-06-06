# Sprint Z Source Provenance Spec

**Date:** 2026-06-06
**Companion to:** `docs/superpowers/specs/2026-06-06-sprint-Z-uniclass-sl-and-omniclass-t11-design.md`
**Pattern parent:** `docs/superpowers/specs/sprint-X-source-provenance.md` (commit `7d797e3`)
**Sets:** citation-discipline contract for all Phase Z.B Uniclass SL per-category transcription tasks + Phase Z.C OmniClass T11 task + Phase Z.D cross-reference back-fill + Phase Z.A.3 Sprint X T13 sweep

---

## 1. Uniclass 2015 Table SL mirror selection

### Primary mirror

- **URL:** https://uniclass.thenbs.com/taxon/sl
- **Access date:** 2026-06-06
- **Edition reflected:** Uniclass 2015 Table SL Spaces/locations **v1.35, April 2026** (current at access date)
- **Coverage estimate:** Authoritative — NBS is the canonical publisher. All 16 top-level SL groups present (SL_20 / SL_25 / SL_30 / SL_32 / SL_35 / SL_40 / SL_42 / SL_45 / SL_50 / SL_55 / SL_60 / SL_70 / SL_75 / SL_80 / SL_82 / SL_90). Per-page navigation drills down to verbatim level-4 entries.
- **Code format observed:** Canonical `SL_XX_XX_XX` (group / sub-group / section / object), consistent with Uniclass 2015 spec.
- **Access mode:** Public web pages, no account required for browsing. Bulk download requires a free NBS account on https://uniclass.thenbs.com/download. CC BY-ND 4.0 licence.

### Secondary mirror (verbatim bulk code list)

- **URL:** https://raw.githubusercontent.com/buildig/uniclass-2015/main/uniclass2015/Uniclass2015_SL.csv (community CSV conversion of the NBS dataset)
- **Access date:** 2026-06-06
- **Edition reflected:** Uniclass 2015 SL **v1.22, October 2021** (latest release `202201` of the buildig repo). Lags NBS v1.35 by ~13 minor versions; per-entry codes that overlap remain verbatim-stable since Uniclass treats SL_XX_XX_XX assignments as additive.
- **Coverage estimate:** 1041 rows confirmed; CSV header `Code,Group,Sub group,Section,Object,Title,NRM`. Sampled rows confirm presence of all 7 Z target categories (sample evidence): `SL_45_10_09 Bedrooms`, `SL_20_50_72 Retail kiosks`, `SL_30_40_50 Meat processing rooms`, `SL_32_10_28 Fisheries`, `SL_80_35_13 Carriageways`, `SL_35_80_08 Bathrooms`, `SL_90_10_15 Corridors`.
- **Use:** Bulk transcription. Z.B implementers MUST cross-verify any post-2021 codes (e.g. v1.23–v1.35 additions) against the NBS primary mirror; the buildig CSV does NOT capture them.

### Tertiary mirror (revisions PDF)

- **URL:** https://www.thenbs.com.au/-/media/uk/files/pdf/uniclass/2021-04/uniclass2015_sl_v1_20_revisions.pdf
- **Access date:** 2026-06-06
- **Use:** Cross-check version-to-version diffs when an implementer suspects a code was renamed or retired between v1.20 and current.

### Target-category mapping (CRITICAL — Uniclass does NOT carve up the 7 Sprint Z target categories cleanly)

The plan's 7 target categories (residential / commercial / retail / hospitality / industrial / agricultural / transport) do NOT map 1:1 to top-level SL groups. Confirmed mapping from the primary mirror:

- **residential** → `SL_45` Residential spaces (top-level). Verified entries in `SL_45_10 Living spaces` include `SL_45_10_09 Bedrooms`, `SL_45_10_08 Bedroom-studies`, `SL_45_10_22 Domestic dining rooms`, `SL_45_10_23 Domestic kitchens`, `SL_45_10_37 Hotel rooms`, `SL_45_10_49 Living rooms`, `SL_45_10_57 Nursing home bedrooms`, `SL_45_10_78 Single-occupancy bedrooms`. 21 codes total under SL_45_10. Coverage: HIGH.
- **commercial** → `SL_20` Administrative, commercial and protective service spaces (top-level). Includes offices, legislative, judicial, protective service. Coverage: HIGH.
- **retail** → `SL_20_50` (sub-group under commercial). Verified entries include `SL_20_50_74 Retail spaces`, `SL_20_50_72 Retail kiosks`, `SL_20_50_85 Supermarket shop floors`, `SL_20_50_22 Department store shop floors`, `SL_20_50_32 Food and drink outlets`, plus salons / parlours. **NOTE: SL_45_10_37 Hotel rooms sits under RESIDENTIAL, not retail/hospitality.** Coverage: HIGH for storefront retail; offices/meeting-rooms NOT enumerated under SL_20_50 — they live elsewhere under SL_20.
- **hospitality** → NO standalone top-level group. Hotel guest rooms = `SL_45_10_37` (residential). Food/drink outlets = `SL_20_50_32` (commercial). Restaurants/bars require sub-group lookup. Coverage: MEDIUM — Z.B implementers MUST traverse multiple sub-groups, not a single SL_HOSPITALITY branch.
- **industrial** → `SL_30` Industrial spaces (top-level). Verified `SL_30_40_50 Meat processing rooms`. Coverage: HIGH.
- **agricultural** → NO standalone top-level group at SL level. Agricultural-adjacent entries appear under `SL_32` Water and land management spaces (e.g. `SL_32_10_28 Fisheries`) and possibly under SL_30 industrial. Coverage: MEDIUM — agricultural enumeration is sparser than the plan's "7 target categories" framing implies. Z.B.6 implementer MUST honestly document the gap; pure-farm taxonomy may need engineering_consensus synthesis under §7 discipline.
- **transport** → `SL_80` Transport spaces (top-level). Verified `SL_80_35_13 Carriageways`, `SL_80_50_72 Railway lines`. Coverage: HIGH for transport infrastructure rooms; vehicle interior spaces sit under `SL_82` Vehicle spaces.

### Authoritative source (paid/account, NOT default)

- **URL:** https://uniclass.thenbs.com/download
- **Status:** Free NBS account unlocks XLSX bulk download. Sprint Z does NOT require this; primary web mirror + buildig CSV cover the transcription. Future Sprint Y MAY back-fill any v1.23–v1.35 deltas using account-gated XLSX as `_verification_status: nbs_sourced` upgrades.

---

## 2. OmniClass Table 11 mirror selection

### Primary mirror

- **URL:** https://nibs.org/wp-content/uploads/2025/04/NBIMS-US_V3_2.4.4.1_OmniClass_Table_11_Construction_Entities_by_Function.pdf
- **Access date:** 2026-06-06
- **Edition reflected:** OmniClass Table 11 — Construction Entities by Function, **2012 DRAFT modified by Committee action 2013-02-26** (Pre Consensus Approved Draft status, embedded by reference into NBIMS-US V3, published 2015 by the National Institute of Building Sciences buildingSMART alliance).
- **Coverage estimate:** Authority citation only. 61-page PDF; binary stream extraction at access date returned non-text — full verbatim code transcription from this PDF alone is impractical for the Z.C implementer without manual page-by-page reading. **Use as the AUTHORITY citation; pair with the secondary mirror for code-level corroboration.**
- **Code format expected:** Canonical `11-XX XX XX XX XX` (five-level hierarchy), matching the OmniClass series convention used by Table 13 / Table 21 / Table 49.

### Secondary mirror (corroboration of NIBS wrapper)

- **URL:** https://www.scribd.com/document/468276520/NBIMS-US-V3-2-4-4-1-OmniClass-Table-11-Construction-Entities-by-Function-pdf
- **Access date:** 2026-06-06
- **Edition reflected:** Same NBIMS-US V3 2.4.4.1 wrapper (61 pages, uploaded by user "Jesus Perez" 2020). Confirms file identity matches the NIBS-hosted PDF.
- **Use:** Identity corroboration only. Scribd preview does NOT expose machine-readable code list; Z.C implementer reads the NIBS PDF directly.

### Tertiary corroboration (categorical scope sketch)

- **URL:** https://biblus.accasoftware.com/en/ifc-objects-omniclass-classification/
- **Access date:** 2026-06-06
- **Use:** Confirms Table 11 root `11-00 00 00` covers "private residences, hotels, congress centres, bus stations, motorways" — i.e. residential / hospitality / civic / transport functions. Does NOT enumerate verbatim codes; categorical sanity-check only.
- **URL:** https://www.designingbuildings.co.uk/wiki/OmniClass — confirms Table 11 = "Construction Entities by Function"; no code enumeration.

### Coverage gap honest disclosure (CRITICAL — Sprint X pdfcoffee pattern does NOT extend to T11)

Sprint X X.A.0 declared `pdfcoffee.com OmniClass 13 2012-05-16` as the verbatim-code secondary mirror for Table 13. **No equivalent pdfcoffee mirror exists for Table 11** at access date (2026-06-06). Web searches surface pdfcoffee Tables 13, 21, and 22 but not Table 11. Therefore:

1. The Z.C implementer's primary code source is the NIBS V3 2.4.4.1 PDF read page-by-page (Pre Consensus Approved Draft 2013-02-26 codes).
2. Verbatim code coverage from the public mirror is expected to be **LOWER than Sprint X T13 (which hit ~70–80%)**. Sprint Z plan portion 1 projects ~80 T11 entries; realistic verbatim public coverage is closer to **40–60%** because no machine-readable mirror is in the public corpus.
3. Z.C entries unable to source verbatim from NIBS PDF MUST land as `_verification_status: inferred` with `_inference_note` citing the NIBS V3 2.4.4.1 wrapper as the structural authority. **No fabrication.** No invented code numbers without an `_inference_note` declaring the parent code consulted.
4. Z.E.3 reviewer spot-check 5% rule applies; failure threshold accounts for this lower realistic ceiling (see §5).

### Authoritative source (licensed, NOT used)

- **URL:** http://www.omniclass.org/tables.asp (CSI Construction Specifications Institute)
- **Status:** Licensed-only access via CSI Dynamic Standards. Sprint Z does NOT acquire. Future Sprint Y when CSI licence granted will back-fill `_verification_status: occs_verified` on T11 entries that round-trip against the canonical source.

---

## 3. Verification status taxonomy (extended from Sprint X)

Per-entry `_verification_status` field carries one of:

- **`mirror_sourced`** — code transcribed verbatim from declared mirror URL. **Default state for OmniClass T11 entries that round-trip against the NIBS V3 2.4.4.1 PDF.**
- **`nbs_sourced`** — Uniclass SL code transcribed verbatim from the NBS Source primary mirror (https://uniclass.thenbs.com/taxon/sl_XX...) or the buildig CSV secondary mirror. **Default state for Uniclass SL entries.**
- **`occs_verified`** — OmniClass code cross-checked against the canonical OCCS Table 11 PDF licensed via CSI. **Sprint Z does NOT set this state.** Reserved for future Sprint Y when CSI licence acquired.
- **`inferred`** — code synthesised from hierarchy structure where mirror coverage is incomplete (e.g. NIBS PDF shows parent `11-XX 00 00 00 00` but no readable child entries; child code synthesised from OmniClass numbering convention). MUST be honest-disclosed in per-entry `_inference_note` explaining the parent code consulted and the numbering pattern applied.
- **`engineering_consensus`** — Uniclass-style code synthesised when NBS Source coverage is partial (e.g. an agricultural sub-room genuinely absent from SL v1.35), citing CIBSE / ASHRAE / BS engineering authority. See §7 discipline.

---

## 4. CIBSE + NRM2 deferred (documented blocker)

- **CIBSE LG1 / LG2 / LG5 / LG7 / LG10 / LG12 / Guide A / Guide F / SLL Code for Lighting** — paid CIBSE membership required for digital PDF access. Sprint Z does NOT transcribe. `cross_references.cibse_lg` stays `null` on every Sprint Z entry.
- **NRM2 (RICS New Rules of Measurement 2)** — paid RICS member PDF required. Sprint Z does NOT transcribe. `cross_references.nrm2` stays `null` on every Sprint Z entry. Note: the buildig CSV header carries an `NRM` column but every sampled row showed it empty — confirms public mirrors do not carry NRM2 cross-references either.

Future Sprint Y when these source-access blockers cleared will back-fill `cross_references.cibse_lg` and `cross_references.nrm2` without breaking existing `_verification_status` values.

---

## 5. Fabrication prevention contract (inherited from Sprint X X.A.0 §6)

**NO IMPLEMENTER MAY FABRICATE UNICLASS SL OR OMNICLASS T11 CODES.** If a category cannot be sourced from the declared public mirrors within reasonable coverage (≥70% of expected entries):

1. Implementer flags the gap in `_source_mirror.coverage_actual_pct` on the parent category record.
2. Implementer ships the partial transcription with `_verification_status: nbs_sourced` (Uniclass) or `mirror_sourced` (OmniClass T11) on what they DID transcribe.
3. Implementer documents the gap in `shared/standards/spaces/_source/Uniclass-2015-SL-source-notes.md` or `OmniClass-Table-11-source-notes.md`.
4. Sprint Z.E.3 final review verdict downgrades to **SHIP-WITH-NOTED-CONCERNS** but does NOT FAIL — partial coverage is acceptable when honestly disclosed; fabrication is not.

The Z.E.3 reviewer spot-checks **5% of randomly-selected codes** against the declared primary mirrors:

- **Uniclass SL** sample → checked against https://uniclass.thenbs.com/taxon/sl_XX (each code's canonical NBS web page); fallback to buildig CSV.
- **OmniClass T11** sample → checked against the NIBS V3 2.4.4.1 PDF (page-by-page read).

If spot-check fails (codes absent from mirror, hierarchy mismatch, or invented numbers without `_inference_note`), sprint verdict = **FIX-FIRST**.

Mirror-vs-mirror discrepancies (e.g. NBS v1.35 vs buildig v1.22 disagree on a code): defer to the **later edition** (NBS v1.35) and record the discrepancy in `_inference_note`.

---

## 6. Sprint X T13 back-compat note

Sprint X shipped 290 OmniClass T13 entries WITHOUT a `taxonomy_source` field (the field is being added in Sprint Z to disambiguate T13 vs T11 vs Uniclass-SL). Z.A.3 mechanical sweep retroactively patches all 290 T13 entries to add `taxonomy_source: "OmniClass-Table-13"`. This is **pure additive**; no Sprint X entry data changes otherwise. Existing `_verification_status` values, OmniClass codes, ASHRAE cross-references, and IFC mappings remain untouched. Sprint X X.E.4 verdict carries forward.

---

## 7. Engineering consensus discipline (Uniclass-specific)

Where NBS Source coverage is genuinely partial (e.g. an agricultural sub-room or a hospitality-specific space not enumerated in Uniclass SL v1.35 because the table is biased toward UK BIM Level 2 deliverables and may not enumerate every farm or hotel-back-of-house room), implementers MAY use `_verification_status: engineering_consensus` to synthesise canonical_ids that match Uniclass SL naming convention + Uniclass code format `SL_XX_XX_XX` — but each such entry MUST cite engineering authority in `_inference_note`:

- CIBSE LG10 §3 residential lighting targets (when LG access acquired in Sprint Y)
- BS 8233 acoustic taxonomy of room types
- Approved Document Q residential security
- ASHRAE 62.1-2022 Table 6-1 occupancy categories (already in Sprint X corpus)
- IFC4 `IfcSpaceTypeEnum` (already in Sprint X corpus)

This is a DIFFERENT discipline from OmniClass `inferred`: Uniclass `engineering_consensus` requires engineering-authority citation, not just OmniClass hierarchy pattern. Implementers who cannot cite a named authority for a synthesised Uniclass code MUST flag the entry as `inferred` with `_inference_note` describing the parent NBS group consulted, or omit the entry entirely. The Z.E.3 5% spot-check applies the same fabrication-detection rule to both `inferred` and `engineering_consensus` entries.
