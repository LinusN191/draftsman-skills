# Changelog

All notable changes to the DraftsMan Skills repo are documented here. Entries follow the sprint structure.

---

## [Sprint F — Foundation (SkillInput Contract Grounding)] — 2026-06-06

### Added
- `shared/schemas/core/skill-input.schema.json` (F.1) + `shared/schemas/core/skill-input-reference.md` — orchestrator → skill payload metaschema with tagged-union by scope (room / floor / building); F.1 retrofit at Sprint X.E.2 replaced hardcoded 27-value Room.type enum with `snake_case` pattern (backwards-compatible; open set for catalogue members)
- `shared/schemas/core/skill-manifest.schema.json` (F.2) — manifest metaschema with `scope` + `placement_convention` enums; discipline enum extended with `commissioning` + `compliance` at F.6 fix-pass; `validation` field broadened to `oneOf[array, object]`
- `ORCHESTRATION.md` at repo root (F.4) — public-facing iteration contract for arbitrary agents; references 3-catalogue room.type taxonomy (OmniClass T13 + Uniclass SL + OmniClass T11) from Sprint X + Z
- `docs/superpowers/specs/skill-input-design-rationale.md` (F.0) — BIM/IFC + room.type enum + grounded_source rationale

### Changed
- `shared/schemas/core/inputs.schema.json` (F.3) — extended `InputItem` with `grounded_source` two-tier validation: closed enum for canonical bindings (`room.*`, `floor.*`, `building.*`, `project.*`, `mep.*`, `site.*`) + `project.<custom>` pattern for project-specific fields
- `scripts/validate-examples.py` (F.5 + F.6) — extended to **8 passes + 5 lint sub-passes**: Pass 5 manifest metaschema + Lint 1 manifest field-name typos + Lint 2 grounded_source validation + Lint 3 dropped-item orphans + Lint 4 cascade SHA-256 byte-equality (Pass 5/6/7/8 renumbering incorporates Sprint X additions)
- 92 stub manifests across electrical/mechanical/plumbing/fire-protection/coordination/documents/commissioning/compliance — added `produces_intents: []` / `consumes_intents: []` empty arrays for Pass 5 compliance (F.6 fix-pass)
- 5 `_derivation_note` strings in db-layout uk-bathroom cascade — realigned to byte-identical producer fixture strings (Lint 4 SHA-256 fix, F.6 fix-pass)
- `electrical/schematic/skill.manifest.json` — corrected discipline field from `documents` to `electrical` (F.6 fix-pass)

### Sprint Discipline
- Sprint F (Foundation) is the first of a 3-sprint group (F → W1 → W2)
- F paused at F.3 (commit `08b6e38`) for Sprint X (OmniClass T13 — 290 entries) + Sprint Z (Uniclass 2015 SL — 295 entries + OmniClass T11 — 89 entries). Both mid-sprint taxonomies shipped + pushed.
- F resumed at F.4. F.5 + F.6 closed the gate extension chapter.
- Sprint discipline held: Sonnet for mechanical tasks (schema edits, manifest fixes), Opus for judgment (design rationale, ORCHESTRATION.md engineering content); two-stage review per task; fix-pass commits per spec.

### Gates
- Sprint X baseline: 354 → Sprint X final: 649 → Sprint Z final: 1033 → Sprint F final: **1137**

### Next
- Sprint W1 — lighting-layout 1.7.0 → 1.8.0 + small-power 2.0.0 → 2.1.0 SkillInput grounding
- Sprint W2 — 5 remaining shipped skills grounded: db-layout / arc-flash-labelling / schematic / sld / earthing

---

## [Sprint Z — Uniclass SL + OmniClass T11 Dual-Taxonomy MEGA-SPRINT] — 2026-06-06

### Summary

Continuation of Sprint X's room-taxonomy programme. Sprint X shipped OmniClass T13 (290 entries) but could not cover residential, hotels, industrial, retail, agricultural, or transport room types — those live in Uniclass 2015 SL, not T13. Sprint Z fills that gap with Uniclass 2015 SL room-level entries (295 entries across 7 categories) plus OmniClass T11 building-level entries (89 entries), completing a 3-taxonomy catalogue structure.

**Gates: 649 (Sprint X final) → 1033 (Sprint Z final) (+384 new entries)**

### Mid-Sprint Discoveries (documented for transparency)

**Z.A.0 worst-case projection — T11 PDF extraction would be 40-60%:**
Initial planning assumed OmniClass Table 11 PDF might yield only partial extraction (40-60% verbatim). Actual result: `pdftotext -layout` extracted cleanly at 100% verbatim. 89 entries shipped without fabrication fallback.

**Hospitality multi-subgroup traversal (Z.B.4):**
Uniclass 2015 SL hospitality entries span 8 distinct SL sub-groups (SL_25_30, SL_25_35, SL_25_40, SL_25_45, SL_25_50, SL_25_55, SL_25_60, SL_25_65). Traversal added 46 entries across the full hospitality stack — more than any other single category.

**Structural pivot — Sprint X 7-category split → 13 T13 parents → Sprint Z dual-taxonomy:**
Sprint X had already established the T13 structural pivot (original 7-category plan → 16 actual T13 parents → 13 room-type-applicable). Sprint Z adds the second structural layer: T13 (spaces-by-function) + Uniclass SL (comprehensive room-level, all building types) + T11 (building-level cross-reference rollup). Each layer serves a distinct consumer need.

### What Shipped

#### Phase Z.A — Foundations (4 commits: Z.A.0/1/2/3 + Sprint X back-compat sweep)
- `shared/standards/spaces/room-types-uniclass-sl/` directory established
- `shared/standards/spaces/building-types-t11/` directory established
- `shared/standards/spaces/_source/Uniclass-2015-SL-source-notes.md` — provenance + mirror selection
- `shared/standards/spaces/_source/OmniClass-Table-11-source-notes.md` — provenance + edition
- `docs/superpowers/specs/sprint-Z-source-provenance.md` — mirror selection + edition declaration
- `shared/standards/spaces/room-types-schema.json` extended: `taxonomy_source` discriminator (3-value enum) + `uniclass_code` (pattern `SL_XX_XX_XX`) + `building_type_codes[]` + extended `omniclass_code` regex (accepts 11- and 13- prefixes) + extended `_verification_status` enum (5 values including `nbs_sourced` + `engineering_consensus`) + extended `parent_category` enum (13→21 values) + 2 allOf conditional requirements
- **Sprint X back-compat sweep:** all 290 Sprint X T13 entries retroactively patched with `taxonomy_source: "OmniClass-Table-13"` (commit Z.A.3; 290 entries touched, 0 content changes)

#### Phase Z.B — Uniclass 2015 SL (7 commits, 295 entries total)

| File | Uniclass SL Root | Entries | NBS / EC split |
|------|-----------------|---------|---------------|
| `residential.json` | SL_25_10 | 61 | 39 nbs + 22 engineering_consensus |
| `commercial.json` | SL_25_20 | 42 | 28 nbs + 14 engineering_consensus |
| `retail.json` | SL_25_25 | 32 | 23 nbs + 9 engineering_consensus |
| `hospitality.json` | SL_25_30..SL_25_65 (8 sub-groups) | 46 | 35 nbs + 11 engineering_consensus |
| `industrial.json` | SL_40_10..SL_40_60 | 62 | 49 nbs + 13 engineering_consensus |
| `agricultural.json` | SL_35_10..SL_35_40 | 20 | 20 nbs + 0 engineering_consensus |
| `transport.json` | SL_50_10..SL_50_40 | 32 | 23 nbs + 9 engineering_consensus |

#### Phase Z.C — OmniClass T11 (1 commit, 89 entries verbatim)
- `shared/standards/spaces/building-types-t11/construction-entities-by-function.json` — 89 entries verbatim from NIBS NBIMS-US V3 pdftotext-layout extraction (100% verbatim; Z.A.0 worst-case projection did not materialise)

#### Phase Z.D — Cross-Reference Back-Fill (1 commit)
- 124 `bs_en_12464_1` + 265 `ashrae_90_1` + 211 `ashrae_62_1` cross-refs populated on SL entries
- 44 `bs_en_12464_1` + 87 `ashrae_90_1` + 78 `ashrae_62_1` cross-refs populated on T11 entries
- `building_type_codes[]` populated on all SL room entries (SL → T11 cross-reference rollup; heuristic SL.parent_category → T11.parent_path[1] mapping)

#### Phase Z.E — Gate Extension + Ship
- `scripts/validate-examples.py` Pass 5 + Lint 5 extended to cover 21 category files across 3 taxonomies (T13 13 files + SL 7 files + T11 1 file)
- CHANGELOG + CLAUDE.md + memory file

### Sprint Z Totals

| Metric | Value |
|--------|-------|
| New entries (SL) | 295 across 7 categories |
| New entries (T11) | 89 building-level |
| Sprint X back-compat patches | 290 |
| Cross-refs back-filled (SL) | 600 (124 + 265 + 211) |
| Cross-refs back-filled (T11) | 209 (44 + 87 + 78) |
| Gate files covered by Pass 5 | 21 (was 13) |
| Gates before Sprint Z | 649 |
| Gates after Sprint Z | 1033 |
| Net new gate entries | +384 |

### Deferred

- **Sprint Y (paid source blocker):** CIBSE LG series + NRM2 cross-references
- **Future sprint:** Remaining Uniclass SL coverage (~700 entries beyond the 7 shipped categories)

### Next

Sprint F resumes at F.4 (ORCHESTRATION.md authoring — now references 3-taxonomy room-types catalogue).

---

## [Sprint X] — 2026-06-06 — Comprehensive Room Taxonomy (MEGA-SPRINT)

### Summary

Mid-sprint pause of Sprint F (after F.3 ship `08b6e38`) triggered by user audit of F.1's 27-value `Room.type` enum — partial BS EN 12464-1 transcription missing residential, healthcare specialty, industrial process, hospitality, public buildings, transport, and external categories. User locked: ship OmniClass Table 13 publicly-available mirror + ASHRAE 90.1 + ASHRAE 62.1 + IFC subset + F.1 retrofit BEFORE Sprint F resumes.

**Gates: 354 → 649 (+295)**

### Mid-Sprint Pivots (documented for transparency)

**Original plan:** 600 OmniClass entries across 7 user-described categories (residential / commercial / institutional / industrial / transport / external / agricultural).

**Discovery #1 — OmniClass T13 has no residential:**  
Residential space types live in OmniClass Table 11 (Construction Entities by Function), not T13 (Spaces by Function). 7-category plan invalidated. Recovery commit `f297cca` re-architected to **16 actual T13 parents**.

**Discovery #2 — Public mirror has ~290 entries (not 600):**  
The OCCS publicly-accessible content covers ~250–300 entries. The full 600-entry canonical PDF is a paid source (OCCS). Recovery commit `91ffbaa` scoped to **13 room-type-applicable parents** (dropped Void Areas, Wall Spaces, Encroachment Spaces — construction elements, not occupancy/function space types).

**Final delivery:** 290 entries across 13 T13 categories (~250 `mirror_sourced` + ~40 `inferred` with mandatory `_inference_note` citing engineering authorities).

### What Shipped

#### Phase X.A — Foundations
- `shared/standards/spaces/room-types/` directory established
- `shared/standards/spaces/room-types/_source/OmniClass-Table-13-source-notes.md` — honest disclosure of mirror coverage vs canonical PDF gap
- `shared/standards/spaces/room-types/fuzzy-match-reference.md` — 4-tier fuzzy-match algorithm (exact → normalised → alias map → embedding tier 5 optional) + 10 test fixtures
- `shared/standards/spaces/room-types/index.json` — master catalogue index with entry counts per category

#### Phase X.B — OmniClass T13 Room Type Files (13 files, 290 entries total)

| File | T13 Code | Entries |
|------|----------|---------|
| `space_planning_types.json` | 13-11 | 5 |
| `parking_spaces.json` | 13-21 | 9 |
| `facility_service_spaces.json` | 13-23 | 51 |
| `circulation_spaces.json` | 13-25 | 25 |
| `education_and_training_spaces.json` | 13-31 | 23 |
| `recreation_spaces.json` | 13-33 | 18 |
| `government_spaces.json` | 13-35 | 21 |
| `artistic_spaces.json` | 13-37 | 32 |
| `museum_spaces.json` | 13-41 | 12 |
| `library_spaces.json` | 13-45 | 10 |
| `spiritual_spaces.json` | 13-47 | 25 |
| `environmentally_controlled_spaces.json` | 13-49 | 25 |
| `healthcare_spaces.json` | 13-51 | 34 |

#### Phase X.C — ASHRAE Standards Files
- `shared/standards/spaces/ashrae/ashrae-90.1-table-9.5.2.1-lpd.json` — 135 LPD entries verbatim from ashrae.org Addendum ba (formerly Table 9.6.1)
- `shared/standards/spaces/ashrae/ashrae-62.1-table-6-1-ventilation.json` — 90 ventilation entries verbatim from ASHRAE 62.1 Table 6-1

#### Phase X.D — IFC ISO 16739 Subset
- `shared/standards/spaces/ifc/` (5 files): `IfcSpaceTypeEnum.json`, `IfcClassification.json`, `IfcLocalPlacement.json`, `IfcRelDefinesByProperties.json`, `README.md`
- Closes F.0 gap (line 61: IFC entity reference undefined)

#### Phase X.E — F.1 Retrofit + Cross-References + Gate Extension
- **F.1 SkillInput retrofit:** `Room.type` enum (27 discrete values) → `snake_case` pattern; backwards-compatible — all existing examples still validate
- **New `Room.classification` field:** optional `IfcClassificationReference` structure (`source`, `edition`, `code`, `reference_uri`) added to SkillInput for BIM round-tripping
- **424 cross-references back-filled** across 290 room-type entries:
  - 81 × BS EN 12464-1 maintained illuminance / UGR references
  - 210 × ASHRAE 90.1 LPD cross-references
  - 133 × ASHRAE 62.1 ventilation cross-references
- **Gate extension:** `validate-examples.py` extended from 3-pass to **6-pass + 1 lint sub-pass**:
  - Pass 4: ASHRAE 90.1 LPD file schema validation
  - Pass 5: ASHRAE 62.1 ventilation file schema validation
  - Pass 6: IFC subset file schema validation
  - Lint 1: room-type snake_case pattern conformance
  - Sprint F.5 will extend further to 7-pass + 5 lint

### Coverage vs Original Target

| Metric | Target | Actual | Notes |
|--------|--------|--------|-------|
| Total entries | 600 | 290 (48%) | Paid-source gap; OCCS canonical PDF deferred to Sprint Y |
| T13 categories | 7 (user-described) | 13 (actual T13 parents) | Residential (T11) deferred to Sprint Z |
| Source type | — | ~250 mirror_sourced + ~40 inferred | Inferred entries carry `_inference_note` |
| ASHRAE 90.1 LPD | — | 135 verbatim | From ashrae.org Addendum ba |
| ASHRAE 62.1 ventilation | — | 90 verbatim | From Table 6-1 |
| IFC entities | — | 4 entity files + README | Closes F.0 line-61 gap |
| Cross-references | — | 424 back-filled | BS EN 12464-1 + ASHRAE 90.1/62.1 |

### Deferred

- **Sprint Y (paid source blocker):** CIBSE LG1/LG2/LG7/LG10/LG12, CIBSE Guide A, NRM2, OmniClass canonical OCCS PDF spot-check
- **Sprint Z:** OmniClass Table 11 (Construction Entities by Function) — residential coverage

### Next

Sprint F resumes at F.4 (ORCHESTRATION.md authoring — now references room-types catalogue). After Sprint F ships, Sprint W1 (lighting-layout + small-power grounding) follows.

---

## [Sprint D5] — 2026-06-05 — lighting-layout v1.7.0 (Wave 2 second deliverable)

lighting-layout v1.6.0→v1.7.0 production; task/ambient zone-purpose split + 3D pendant placement; 7 new INVs (INV-13..19); 8 retrofit + 4 NEW examples; 5 new evals; 1 new verified standards file (area-definitions.json); manifest 1.6.0→1.7.0; gates 341→354 (+13); 11/11 D.2 fence PASS clean; Wave 2 closes.

---

## [Sprint D4] — 2026-06-03 — small-power v2.0.0 (Wave 2 first deliverable)

small-power v1.2.0 beta→v2.0.0 production; closes within-skill-depth program for small-power; 7 new INVs (INV-13..INV-19; 5 HIGH + 2 MEDIUM) + 5 new evals (10 total) + 8 NEW + 1 RETROFIT examples; building_diversity (IET OSG App A Table A1) + ring-topology depth (IET OSG §8.4.4) + EV-charge (BS EN 61851-1 + BS EN 62196 + §722); gates 312→341 (+29).

---

## [Wave 1 — Sprint Special-Locations] — 2026-06-02 — special-locations v1.0.0

Cross-cutting Part-7 zoning skill (§701 bathrooms + §702 pools + §703 saunas + §710 medical + §715 ELV); 16 implementer tasks across 4 phases; 6 Python zone-derivation modules + 75 unit tests; 8 standalone + 9 cascade examples; 3 consumer skills wired (lighting-layout v1.5→v1.6 + small-power v1.1→v1.2 + db-layout v1.4→v1.5); gates 262→312 (+50).

---

## [Wave 1 — Sprint Photometric-Analysis] — 2026-05-30 — photometric-analysis v1.0.0

v0.1.0 stub→v1.0.0 production; calc-primitive wrapper of calc.lumen_grid_solver per BS EN 12464-1; 8 synthetic IES files; 7 lighting-layout examples retrofitted; lighting-layout v1.4→v1.5 with INV-11 cascade activated; gates 236→262 (+26).

---

## [Sprint D3] — 2026-05-29 — lighting-layout v1.4.0

Z-pattern topology + stub prompt fixes + intent payload extension; 10 new INVs + 4 new examples; gates 236/236 held.

---

## [Sprint D2] — 2026-05-27 — cable-sizing v1.1.0 + db-layout v1.4.0

D2.1 PVC/SWA correction tables + D2.2 BS/NEC/IEC label templates + D2.3 diversity for lifts/EV/AC/motors; gates 225/225. D2.3 fix-pass corrected CRITICAL Reg 559 misattribution.

---

## [Sprint D1] — 2026-05-26 — fault-level v1.2.0 + arc-flash v1.1.0

Breaking-capacity verdict + motor/UPS superposition + Park's decrement curves; NFPA 70E §130.5(A) equipment-condition; gates 221/221.

---

## [Remediation Program A–C] — 2026-05-22–25

43-finding external audit → 1 finding (motor-superposition oracle FP); 17/17 DEFECT_REGISTER buckets resolved; tagged audit-cleared-v1.0; harness 163→166→221.

---

## [Sprint 3-W2] — 2026-05-22 — Schema Standardisation + Content Completion

eval.schema.json v2 + new inputs.schema.json + 3-pass golden CI gate + CLAUDE.md ground-truth rewrite; db-layout board_kind discriminator + 10 specialty-board rationale blocks; harness FULL GREEN 143/143.

---

## [Sprint 3-W] — 2026-05-21 — Golden CI Gate Live

skill-author bug fix; golden CI gate live; db-layout NEW shape + earthing enum + lighting-layout prompt; 39/53 harness pass.

---

## Earlier Sprints

See memory files under `/Users/linus/.claude/projects/-Users-linus-Desktop-DraftsMan-SKills-draftsman-skills/memory/` for full history of sprints 3-W, D1–D5, Wave 1, and earlier milestones.
