# Uniclass 2015 Table SL — Source Notes

**Last updated:** 2026-06-06

## Source mirror (primary)

- **URL:** https://uniclass.thenbs.com/taxon/sl
- **Access date:** 2026-06-06
- **Edition reflected:** Uniclass 2015 Table SL Spaces/locations **v1.35, April 2026** (current at access date)
- **Coverage estimate:** Authoritative — NBS is the canonical publisher. All 16 top-level SL groups present (SL_20 / SL_25 / SL_30 / SL_32 / SL_35 / SL_40 / SL_42 / SL_45 / SL_50 / SL_55 / SL_60 / SL_70 / SL_75 / SL_80 / SL_82 / SL_90). Per-page navigation drills down to verbatim level-4 entries.
- **Code format observed:** Canonical `SL_XX_XX_XX` (group / sub-group / section / object), consistent with Uniclass 2015 spec.
- **Access mode:** Public web pages, no account required for browsing. Bulk download requires a free NBS account on https://uniclass.thenbs.com/download. CC BY-ND 4.0 licence.

## Source mirror (secondary — verbatim bulk code list)

- **URL:** https://raw.githubusercontent.com/buildig/uniclass-2015/main/uniclass2015/Uniclass2015_SL.csv (community CSV conversion of the NBS dataset)
- **Access date:** 2026-06-06
- **Edition reflected:** Uniclass 2015 SL **v1.22, October 2021** (latest release `202201` of the buildig repo). Lags NBS v1.35 by ~13 minor versions; per-entry codes that overlap remain verbatim-stable since Uniclass treats SL_XX_XX_XX assignments as additive.
- **Coverage estimate:** 1041 rows confirmed; CSV header `Code,Group,Sub group,Section,Object,Title,NRM`. Sampled rows confirm presence of all 7 Sprint Z target categories: `SL_45_10_09 Bedrooms`, `SL_20_50_72 Retail kiosks`, `SL_30_40_50 Meat processing rooms`, `SL_32_10_28 Fisheries`, `SL_80_35_13 Carriageways`, `SL_35_80_08 Bathrooms`, `SL_90_10_15 Corridors`.
- **Use:** Bulk transcription. Z.B implementers MUST cross-verify any post-2021 codes (e.g. v1.23–v1.35 additions) against the NBS primary mirror; the buildig CSV does NOT capture them.

## Source mirror (tertiary — revision diffs)

- **URL:** https://www.thenbs.com.au/-/media/uk/files/pdf/uniclass/2021-04/uniclass2015_sl_v1_20_revisions.pdf
- **Access date:** 2026-06-06
- **Use:** Cross-check version-to-version diffs when an implementer suspects a code was renamed or retired between v1.20 and current.

## Authoritative source (paid/account — NOT default)

- **URL:** https://uniclass.thenbs.com/download
- **Status:** Free NBS account unlocks XLSX bulk download. Sprint Z does NOT require this; primary web mirror + buildig CSV cover the transcription. Future Sprint Y MAY back-fill any v1.23–v1.35 deltas using account-gated XLSX as `_verification_status: nbs_sourced` upgrades.

## Target-category mapping (CRITICAL — Uniclass does NOT carve up the 7 Sprint Z target categories cleanly)

The plan's 7 target categories (residential / commercial / retail / hospitality / industrial / agricultural / transport) do NOT map 1:1 to top-level SL groups. Confirmed mapping from the primary mirror:

- **residential** → `SL_45` Residential spaces (top-level). Verified entries in `SL_45_10 Living spaces` include `SL_45_10_09 Bedrooms`, `SL_45_10_08 Bedroom-studies`, `SL_45_10_22 Domestic dining rooms`, `SL_45_10_23 Domestic kitchens`, `SL_45_10_37 Hotel rooms`, `SL_45_10_49 Living rooms`, `SL_45_10_57 Nursing home bedrooms`, `SL_45_10_78 Single-occupancy bedrooms`. 21 codes total under SL_45_10. Coverage: HIGH.
- **commercial** → `SL_20` Administrative, commercial and protective service spaces (top-level). Includes offices, legislative, judicial, protective service. Coverage: HIGH.
- **retail** → `SL_20_50` (sub-group under commercial). Verified entries include `SL_20_50_74 Retail spaces`, `SL_20_50_72 Retail kiosks`, `SL_20_50_85 Supermarket shop floors`, `SL_20_50_22 Department store shop floors`, `SL_20_50_32 Food and drink outlets`, plus salons / parlours. **NOTE: SL_45_10_37 Hotel rooms sits under RESIDENTIAL, not retail/hospitality.** Coverage: HIGH for storefront retail; offices/meeting-rooms NOT enumerated under SL_20_50 — they live elsewhere under SL_20.
- **hospitality** → NO standalone top-level group. Hotel guest rooms = `SL_45_10_37` (residential). Food/drink outlets = `SL_20_50_32` (commercial). Restaurants/bars require sub-group lookup. Coverage: MEDIUM — Z.B implementers MUST traverse multiple sub-groups, not a single SL_HOSPITALITY branch.
- **industrial** → `SL_30` Industrial spaces (top-level). Verified `SL_30_40_50 Meat processing rooms`. Coverage: HIGH.
- **agricultural** → NO standalone top-level group at SL level. Agricultural-adjacent entries appear under `SL_32` Water and land management spaces (e.g. `SL_32_10_28 Fisheries`) and possibly under SL_30 industrial. Coverage: MEDIUM — agricultural enumeration is sparser than the plan's "7 target categories" framing implies. Z.B.6 implementer MUST honestly document the gap; pure-farm taxonomy may need `engineering_consensus` synthesis with mandatory `_inference_note` citing CIBSE / ASHRAE / BS engineering authority.
- **transport** → `SL_80` Transport spaces (top-level). Verified `SL_80_35_13 Carriageways`, `SL_80_50_72 Railway lines`. Coverage: HIGH for transport infrastructure rooms; vehicle interior spaces sit under `SL_82` Vehicle spaces.

## Verification status taxonomy

See `docs/superpowers/specs/sprint-Z-source-provenance.md` §3.

- `nbs_sourced` — code transcribed verbatim from NBS Source primary mirror or buildig CSV secondary mirror. **Default state for Sprint Z Uniclass SL entries.**
- `occs_verified` — NOT applicable to Uniclass SL (OCCS covers OmniClass only). Reserved for future cross-checks if NBS provides a canonical verification mechanism.
- `inferred` — synthesised from hierarchy structure; MUST include `_inference_note`
- `engineering_consensus` — Uniclass-style code synthesised when NBS Source coverage is partial, citing CIBSE / ASHRAE / BS engineering authority

## Per-category transcription tasks

- Z.B.1 residential.json (~60 entries) — Opus pattern-setter
- Z.B.2 commercial.json (~40 entries) — Sonnet
- Z.B.3 retail.json (~30 entries) — Sonnet
- Z.B.4 hospitality.json (~40 entries) — Sonnet
- Z.B.5 industrial.json (~50 entries) — Sonnet
- Z.B.6 agricultural.json (~20 entries) — Sonnet
- Z.B.7 transport.json (~30 entries) — Sonnet

## Known transcription gaps

(populated by Z.B.* implementer reports when NBS Source coverage < expected)

## Engineering consensus path

Where NBS Source is partial, `_verification_status: engineering_consensus` allowed with mandatory `_inference_note` citing CIBSE / ASHRAE / BS engineering authority. See `docs/superpowers/specs/sprint-Z-source-provenance.md` §7.

## CIBSE + NRM2 deferred (paid source access blocker)

Sprint Z does NOT transcribe CIBSE LG series or NRM2. `cross_references.cibse_lg` and `cross_references.nrm2` stay `null` on every Sprint Z entry. Note: the buildig CSV header carries an `NRM` column but every sampled row showed it empty — confirms public mirrors do not carry NRM2 cross-references.
