# Changelog

All notable changes to the DraftsMan Skills repo are documented here. Entries follow the sprint structure.

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
