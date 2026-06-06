# Sprint Z — Uniclass 2015 SL + OmniClass T11 Dual-Taxonomy MEGA-SPRINT Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Author the room-level taxonomy (Uniclass 2015 Table SL) that OmniClass T13 lacks — closing the residential / hotel / office / retail / restaurant / industrial / warehouse / agricultural gaps surfaced by Sprint X coverage audit. Concurrently ship OmniClass Table 11 as the building-level cross-reference catalogue. Sprint Z runs AFTER Sprint X (already pushed `23556eb..18deb71`) and BEFORE Sprint F resumes at F.4.

**Architecture:** Dual-taxonomy mega-sprint. 18 implementer tasks across 5 phases. Net new folders: `shared/standards/spaces/room-types-uniclass-sl/` (7 per-category files) + `shared/standards/spaces/building-types-t11/` (1 file). Schema extended with `taxonomy_source` discriminator enum + conditional `omniclass_code` vs `uniclass_code` requirements. Sprint X T13 entries retroactively patched with `taxonomy_source: "OmniClass-Table-13"` for back-compat (mechanical sweep at Z.A.3). Critical constraint: implementers MUST source from declared public mirrors and flag verification status per entry; fabrication of Uniclass or OmniClass codes is a CRITICAL failure caught at Z.E.3 final review spot-check.

**Tech Stack:**
- JSON Schema Draft-07 (matches existing standards files)
- Markdown for reference docs + companion READMEs
- Python stdlib for `scripts/validate-examples.py` extension + Z.A.3 back-compat sweep + Z.D.1 cross-reference back-fill
- Existing 6-pass + 1 lint gate (Sprint X.E.1 state) — Sprint Z extends Pass 5 + Lint 5 to cover the 2 new catalogues

**Source spec:** [`docs/superpowers/specs/2026-06-06-sprint-Z-uniclass-sl-and-omniclass-t11-design.md`](../specs/2026-06-06-sprint-Z-uniclass-sl-and-omniclass-t11-design.md) (commit `d43bd08`, 291 lines).
**Pattern parent:** [`docs/superpowers/plans/2026-06-05-sprint-X-comprehensive-room-taxonomy-sprint.md`](2026-06-05-sprint-X-comprehensive-room-taxonomy-sprint.md) (Sprint X plan, 4 portions, 2838 lines, shipped 41 commits).
**Pre-existing verified standards layers (referenced for cross_references):**
- `shared/standards/lighting/BSEN12464/lux-levels.json` (27 lighting entries)
- `shared/standards/energy/ASHRAE-90-1/lpd-table-9-6-1.json` (135 LPD entries, Sprint X)
- `shared/standards/hvac/ASHRAE-62-1/ventilation-rates.json` (90 ventilation entries, Sprint X)
- `shared/standards/spaces/room-types/*.json` (290 OmniClass T13 entries across 13 categories, Sprint X)

---

## Sprint discipline (locked, mirrors Sprint X)

- Sonnet for mechanical (schema edits, per-category files once pattern stable, gate extension, back-fill scripts) per `[[feedback-no-haiku-sonnet-opus-only]]`
- Opus for judgment (source provenance, Uniclass SL pattern-setter, OmniClass T11 transcription, final integration review)
- **Two-stage Opus review after every implementer task** + fix-pass commit when HIGH/CRITICAL findings surface. Budget for ~6-10 fix-passes given the 18-task surface (Sprint X precedent: ~5 fix-passes per 21 tasks).
- **CRITICAL: Citation fidelity rule — implementers MUST cite real Uniclass NBS Source / OmniClass T11 mirror URLs + access dates.** Fabricated codes caught at Z.E.3 spot-check cause sprint FIX-FIRST verdict. `_verification_status` field must accurately reflect sourcing (`mirror_sourced` / `occs_verified` / `inferred` / `nbs_sourced` / `engineering_consensus`).
- No banned tokens: §526.2 / §433.2 / OZEV / 3rd Edition / Reg 559 / Em_room / "average room lux".
- Pre-ship **Opus 8-check verification fence** with **5% fabrication spot-check** (Z.E.3 task).
- Final cross-sprint **Opus integration review** at Z.E.3 — verdict PASS / SHIP-WITH-NOTED-CONCERNS / FIX-FIRST.
- Push deferred to user authorisation per CLAUDE.md "shared state" rule (Z.E.5 task).
- `[[feedback-no-trim-non-consequential]]` — `_note` / `_source` / `_inference_note` fields stay full-length.

### Estimated commit count: 50-60

- 18 implementer commits
- ~6-10 fix-pass commits
- 3 portion commits for this plan doc
- 1 spec commit already done (`d43bd08`)

---

## File structure

### Modified (existing files)

```
shared/standards/spaces/
├── room-types-schema.json     # Z.A.1 MODIFY — add taxonomy_source enum + uniclass_code pattern + building_type_codes + extended omniclass_code regex (^1[13]-...) + extended _verification_status enum (5 values) + allOf conditional requirements
├── room-types.json             # Z.A.2 MODIFY — master index re-architecture: declares 3 catalogues (T13 + SL + T11); per-catalogue category lists
├── README.md                   # Z.A.2 MODIFY — document 3-taxonomy approach
└── room-types/*.json (×13)     # Z.A.3 MODIFY — Sprint X back-compat sweep: add `taxonomy_source: "OmniClass-Table-13"` to all 290 existing entries

scripts/validate-examples.py    # Z.E.1 MODIFY — extend Pass 5 to validate room-types-uniclass-sl/*.json + building-types-t11/*.json; extend Lint 5 canonical membership to include SL canonical_ids
```

### Created (NEW files under `shared/standards/spaces/`)

```
shared/standards/spaces/
├── _source/
│   ├── Uniclass-2015-SL-source-notes.md    # Z.A.2 NEW
│   └── OmniClass-Table-11-source-notes.md  # Z.A.2 NEW
├── room-types-uniclass-sl/                  # NEW directory
│   ├── residential.json                     # Z.B.1 NEW; ~50-80 entries; pattern-setter
│   ├── commercial.json                      # Z.B.2 NEW; ~40 entries
│   ├── retail.json                          # Z.B.3 NEW; ~30 entries
│   ├── hospitality.json                     # Z.B.4 NEW; ~40 entries
│   ├── industrial.json                      # Z.B.5 NEW; ~50 entries
│   ├── agricultural.json                    # Z.B.6 NEW; ~20 entries
│   └── transport.json                       # Z.B.7 NEW; ~30 entries
└── building-types-t11/                      # NEW directory
    └── construction-entities-by-function.json  # Z.C.1 NEW; ~50-80 entries
```

### Created (NEW provenance spec)

```
docs/superpowers/specs/sprint-Z-source-provenance.md  # Z.A.0 NEW — Uniclass SL + T11 mirror selection + edition declarations + verification status taxonomy
```

### Memory + index (outside repo)

```
/Users/linus/.claude/projects/-Users-linus-Desktop-DraftsMan-SKills-draftsman-skills/memory/
├── sprint-Z-dual-taxonomy-shipped.md  # Z.E.2 NEW
└── MEMORY.md                           # Z.E.2 APPEND index line
```

### Modified (CHANGELOG + CLAUDE.md at repo root)

```
CHANGELOG.md   # Z.E.2 MODIFY — Sprint Z entry
CLAUDE.md      # Z.E.2 MODIFY — note 7-pass + 1 lint gate state (Sprint Z extension); 3-taxonomy room-types catalogue
```

---

## Phase Z.A — Foundation (4 tasks, ~5-7 commits)

Goal: lock the per-entry shape (Z.A.1 schema extension) + source-provenance methodology (Z.A.0) + master index re-architecture (Z.A.2) + Sprint X back-compat sweep (Z.A.3) BEFORE any new per-category transcription begins.

### Task Z.A.0: Author Sprint Z source provenance spec (Uniclass NBS + OmniClass T11 mirror survey)

**Files:**
- Create: `docs/superpowers/specs/sprint-Z-source-provenance.md`

**Why Opus:** Source survey requires engineering judgement on mirror reliability; sets the citation-discipline contract for all subsequent Z.B + Z.C tasks; failure here pollutes every per-category file (lesson from Sprint X X.A.0 / X.B.1 residential discovery).

- [ ] **Step 1: Survey publicly-available Uniclass 2015 SL sources**

Run WebSearch + WebFetch (if available) to identify Uniclass SL access points:

```bash
# Inventory candidate Uniclass SL sources to evaluate:
echo "Candidate Uniclass 2015 Table SL sources:"
echo "  1. NBS Source — https://uniclass.thenbs.com/ (canonical NBS-published)"
echo "  2. Designing Buildings Wiki — designingbuildings.co.uk Uniclass coverage"
echo "  3. GOV.UK BIM Level 2 documentation (Crown Commercial Service)"
echo "  4. NBS published whitepapers and PDF guides"
echo "  5. ISO 12006-2 / ISO 19650 implementation guides referencing Uniclass"
```

For each candidate: WebFetch the URL, inspect actual SL content. Note coverage of the 7 target categories (residential / commercial / retail / hospitality / industrial / agricultural / transport).

- [ ] **Step 2: Survey publicly-available OmniClass Table 11 sources**

Same pattern as Sprint X X.A.0 for T11:

```bash
echo "Candidate OmniClass Table 11 mirrors:"
echo "  1. NIBS NBIMS-US V3 wrapper (authority citation, sparse codes)"
echo "  2. pdfcoffee.com OmniClass Table 11 mirror (verbatim codes)"
echo "  3. scribd.com OmniClass Table 11 (corroboration)"
echo "  4. Autodesk knowledge base BIM documentation"
echo "  5. CSI MasterFormat cross-walks referencing T11"
```

WebFetch the most promising URL. Note T11 top-level classes (residential / commercial / industrial / agricultural / transportation / civic / etc.) + entry coverage.

- [ ] **Step 3: Pick primary mirrors + declare backups**

Selection criteria per spec §3.4:
- Coverage of all 7 Uniclass SL target categories OR documented gap
- Coverage of all OmniClass T11 top-level classes
- Verifiable edition (Uniclass 2015 edition; OmniClass T11 latest publicly available)
- Stable URL (not behind paywall or session-token auth)
- Codes in canonical format (SL_XX_XX_XX for Uniclass; 11-XX XX XX XX XX for OmniClass T11)

If no single mirror covers everything: declare primary + backup mirrors per category.

- [ ] **Step 4: Author the provenance spec**

Create `docs/superpowers/specs/sprint-Z-source-provenance.md`:

```markdown
# Sprint Z Source Provenance Spec

**Date:** 2026-06-06
**Companion to:** `docs/superpowers/specs/2026-06-06-sprint-Z-uniclass-sl-and-omniclass-t11-design.md`
**Sets:** citation-discipline contract for all Phase Z.B Uniclass SL per-category tasks + Phase Z.C OmniClass T11 task + Phase Z.D cross-reference back-fill

## 1. Uniclass 2015 Table SL mirror selection

### Primary mirror

- **URL:** <verbatim URL of the primary Uniclass SL mirror surveyed at Step 1>
- **Access date:** 2026-06-06
- **Edition reflected:** Uniclass 2015 (post-2015 amendment — declare specific version if visible)
- **Coverage estimate:** <e.g. "85% of expected ~260 entries across 7 target categories">
- **Code format observed:** <canonical SL_XX_XX_XX | other — declare any drift>

### Backup mirrors

- <URL + categories covered + access date for each backup>

## 2. OmniClass Table 11 mirror selection

### Primary mirror

- **URL:** <verbatim URL>
- **Access date:** 2026-06-06
- **Edition reflected:** <e.g. "OmniClass Table 11 — Construction Entities by Function, 2012-05-16">
- **Coverage estimate:** <e.g. "100% of expected ~80 entries">

### Backup mirrors

- <URL + access date>

## 3. Verification status taxonomy (extended from Sprint X)

Per-entry `_verification_status` field carries one of:

- **`mirror_sourced`** — code transcribed verbatim from declared mirror URL (OmniClass entries default)
- **`nbs_sourced`** — Uniclass code transcribed verbatim from NBS Source / NBS publication
- **`occs_verified`** — OmniClass code cross-checked against canonical OCCS Table 11 PDF (future Sprint Y back-fill)
- **`inferred`** — code synthesised from hierarchy structure where mirror coverage is incomplete (MUST be honest-disclosed in `_inference_note`)
- **`engineering_consensus`** — Uniclass-style code synthesised when NBS Source coverage is partial, citing CIBSE / ASHRAE / BS engineering authority

## 4. CIBSE + NRM2 deferred (documented blocker)

- **CIBSE LG1 / LG2 / LG7 / LG10 / LG12 / Guide A** — paid CIBSE membership required. Sprint Y when access granted. `cross_references.cibse_lg` stays `null` on every Sprint Z entry.
- **NRM2 (RICS)** — paid RICS PDF required. Sprint Y. `cross_references.nrm2` stays `null` on every Sprint Z entry.

## 5. Fabrication prevention contract (inherited from Sprint X X.A.0 §6)

**NO IMPLEMENTER MAY FABRICATE UNICLASS SL OR OMNICLASS T11 CODES.** If a category cannot be sourced within reasonable coverage (≥70% of expected entries):

1. Implementer flags the gap in `_coverage_actual_pct` field
2. Implementer ships the partial transcription with `_verification_status: mirror_sourced` (OmniClass) or `nbs_sourced` (Uniclass) on what they DID transcribe
3. Implementer documents the gap in `shared/standards/spaces/_source/Uniclass-2015-SL-source-notes.md` or `OmniClass-Table-11-source-notes.md`
4. Sprint Z.E.3 final review verdict downgrades to SHIP-WITH-NOTED-CONCERNS but does NOT FAIL — partial coverage acceptable; fabrication is not

The Z.E.3 reviewer spot-checks 5% of randomly-selected codes against the declared primary mirrors. If spot-check fails (codes not present in mirror), sprint verdict = FIX-FIRST.

## 6. Sprint X T13 back-compat note

Sprint X shipped 290 OmniClass T13 entries WITHOUT a `taxonomy_source` field (the field is being added in Sprint Z). Z.A.3 mechanical sweep retroactively patches all 290 entries to add `taxonomy_source: "OmniClass-Table-13"`. This is pure additive; no Sprint X entry data changes otherwise.

## 7. Engineering consensus discipline (Uniclass-specific)

Where NBS Source is partial (residential bedrooms / hotel guest rooms / etc. may not be fully enumerated in publicly-accessible Uniclass SL), implementers may use `_verification_status: engineering_consensus` to synthesise canonical_ids that match Uniclass SL naming convention + Uniclass code format `SL_XX_XX_XX` — but each such entry MUST cite engineering authority (e.g. CIBSE LG10 §3 residential targets / BS 8233 acoustic taxonomy / Approved Document Q residential) in `_inference_note`.

This is a DIFFERENT discipline from OmniClass `inferred`: Uniclass synthesis requires engineering citation, not just hierarchy pattern.
```

- [ ] **Step 5: Validate file renders + commit**

```bash
wc -l docs/superpowers/specs/sprint-Z-source-provenance.md
grep -nE "TBD|TODO|fill in" docs/superpowers/specs/sprint-Z-source-provenance.md | head -5 && echo "FAIL — placeholders present" || echo "PASS"
```

Expected: ~80-150 lines; PASS on placeholder check.

- [ ] **Step 6: Banned-citation grep + gates**

```bash
grep -nE "(§526\.2|§433\.2|OZEV|3rd Edition|Reg 559|Em_room|average room lux)" docs/superpowers/specs/sprint-Z-source-provenance.md | grep -v "do NOT\|never cite\|banned\|NOT cite" && echo FAIL || echo PASS
python3 scripts/validate-examples.py 2>&1 | tail -3
```

Expected: PASS; aggregate 649/649 unchanged (docs not validated by gate).

- [ ] **Step 7: Commit**

```bash
git add docs/superpowers/specs/sprint-Z-source-provenance.md
git commit -m "feat(spec): Z.A.0 Sprint Z source provenance — Uniclass 2015 SL mirror selection (NBS Source / designingbuildings / GOV.UK BIM) + OmniClass T11 mirror selection (NIBS / pdfcoffee / scribd) + 5-value verification status taxonomy (mirror_sourced / nbs_sourced / occs_verified / inferred / engineering_consensus) + CIBSE/NRM2 deferred + Sprint X back-compat note"
```

### Task Z.A.1: Extend room-types-schema.json with taxonomy_source discriminator

**Files:**
- Modify: `shared/standards/spaces/room-types-schema.json`

**Why Sonnet:** Mechanical JSON Schema edit; spec §5 has the exact new shape; allOf conditional requirements pattern lifted from JSON Schema Draft-07 examples.

- [ ] **Step 1: Inspect current schema state**

```bash
python3 -c "
import json
s = json.load(open('shared/standards/spaces/room-types-schema.json'))
print('current required:', s['required'])
print('current parent_category enum length:', len(s['properties']['parent_category']['enum']))
print('current omniclass_code pattern:', s['properties']['omniclass_code']['pattern'])
print('current _verification_status enum:', s['properties']['_verification_status']['enum'])
print('allOf present:', 'allOf' in s)
"
```

Expected pre-Z.A.1: required has 4 values (canonical_id, omniclass_code, parent_category, _verification_status); parent_category enum 13 values (Sprint X T13); omniclass_code pattern `^13-...`; _verification_status enum 3 values; no allOf.

- [ ] **Step 2: Apply schema extensions**

Edit `shared/standards/spaces/room-types-schema.json`. Apply these specific changes:

1. **Remove `omniclass_code` from required** (becomes conditional via allOf)
2. **Add `taxonomy_source` to required**
3. **Add new properties:**

```json
"taxonomy_source": {
  "type": "string",
  "enum": ["OmniClass-Table-13", "OmniClass-Table-11", "Uniclass-2015-SL"],
  "description": "Source taxonomy discriminator. OmniClass entries require omniclass_code; Uniclass entries require uniclass_code (enforced via allOf)."
},
"uniclass_code": {
  "type": "string",
  "pattern": "^SL_[0-9]{2}_[0-9]{2}_[0-9]{2}$",
  "description": "Uniclass 2015 Table SL 6-digit notation (SL_XX_XX_XX). Required when taxonomy_source = Uniclass-2015-SL."
},
"building_type_codes": {
  "type": "array",
  "items": {"type": "string", "pattern": "^11-[0-9]{2}( [0-9]{2}){0,4}$"},
  "description": "Optional. SL room entries reference OmniClass T11 building codes for rollup (e.g. residential.bedroom_master → [11-11 11 11] single-family residence)."
}
```

4. **Extend `omniclass_code.pattern`** from `^13-[0-9]{2}( [0-9]{2}){0,4}$` to `^1[13]-[0-9]{2}( [0-9]{2}){0,4}$` (accepts both 13- and 11- prefixes)
5. **Extend `_verification_status.enum`** from `[mirror_sourced, occs_verified, inferred]` to `[mirror_sourced, occs_verified, inferred, nbs_sourced, engineering_consensus]`
6. **Extend `parent_category.enum`** from 13 values to 21 values:

```json
"enum": [
  "space_planning_types", "parking_spaces", "facility_service_spaces",
  "circulation_spaces", "education_and_training_spaces", "recreation_spaces",
  "government_spaces", "artistic_spaces", "museum_spaces", "library_spaces",
  "spiritual_spaces", "environmentally_controlled_spaces", "healthcare_spaces",
  "residential", "commercial", "retail", "hospitality",
  "industrial", "agricultural", "transport",
  "construction_entities"
]
```

7. **Add root-level `allOf`** for conditional requirements:

```json
"allOf": [
  {
    "if": { "properties": { "taxonomy_source": { "enum": ["OmniClass-Table-13", "OmniClass-Table-11"] } } },
    "then": { "required": ["omniclass_code"] }
  },
  {
    "if": { "properties": { "taxonomy_source": { "const": "Uniclass-2015-SL" } } },
    "then": { "required": ["uniclass_code"] }
  }
]
```

- [ ] **Step 3: Validate schema + Draft-07 well-formed**

```bash
python3 -c "
import json, jsonschema
s = json.load(open('shared/standards/spaces/room-types-schema.json'))
print('parse OK')
print('required:', s['required'])
print('taxonomy_source enum:', s['properties']['taxonomy_source']['enum'])
print('uniclass_code pattern:', s['properties']['uniclass_code']['pattern'])
print('omniclass_code pattern:', s['properties']['omniclass_code']['pattern'])
print('parent_category enum length:', len(s['properties']['parent_category']['enum']))
print('_verification_status enum:', s['properties']['_verification_status']['enum'])
print('building_type_codes present:', 'building_type_codes' in s['properties'])
print('allOf clauses:', len(s.get('allOf', [])))
jsonschema.Draft7Validator.check_schema(s)
print('Draft-07 well-formed: OK')
"
```

Expected: required includes [canonical_id, taxonomy_source, parent_category, _verification_status] (NOT omniclass_code); taxonomy_source 3 enum values; both code patterns correct; parent_category 21 values; _verification_status 5 values; building_type_codes present; allOf 2 clauses; well-formed OK.

- [ ] **Step 4: Test against 8 hand-authored fixtures (covering both branches)**

```bash
python3 -c "
import json, jsonschema
schema = json.load(open('shared/standards/spaces/room-types-schema.json'))
tests = [
    ('omniclass_t13_valid', {
        'canonical_id': 'office.open_plan',
        'taxonomy_source': 'OmniClass-Table-13',
        'omniclass_code': '13-15 11 23 11',
        'parent_category': 'commercial',
        '_verification_status': 'mirror_sourced'
    }, 'PASS'),
    ('omniclass_t11_valid', {
        'canonical_id': 'construction_entities.single_family_residence',
        'taxonomy_source': 'OmniClass-Table-11',
        'omniclass_code': '11-11 11 11',
        'parent_category': 'construction_entities',
        '_verification_status': 'mirror_sourced'
    }, 'PASS'),
    ('uniclass_sl_valid', {
        'canonical_id': 'residential.bedroom_master',
        'taxonomy_source': 'Uniclass-2015-SL',
        'uniclass_code': 'SL_25_10_45',
        'parent_category': 'residential',
        '_verification_status': 'nbs_sourced'
    }, 'PASS'),
    ('uniclass_engineering_consensus', {
        'canonical_id': 'hospitality.guest_suite',
        'taxonomy_source': 'Uniclass-2015-SL',
        'uniclass_code': 'SL_25_30_15',
        'parent_category': 'hospitality',
        '_verification_status': 'engineering_consensus',
        '_inference_note': 'CIBSE LG10 §3.5 guest accommodation'
    }, 'PASS'),
    ('omniclass_missing_code', {
        'canonical_id': 'office.open_plan',
        'taxonomy_source': 'OmniClass-Table-13',
        'parent_category': 'commercial',
        '_verification_status': 'mirror_sourced'
    }, 'FAIL'),
    ('uniclass_missing_code', {
        'canonical_id': 'residential.bedroom_master',
        'taxonomy_source': 'Uniclass-2015-SL',
        'parent_category': 'residential',
        '_verification_status': 'nbs_sourced'
    }, 'FAIL'),
    ('bad_taxonomy_source', {
        'canonical_id': 'office.open_plan',
        'taxonomy_source': 'UnknownTaxonomy',
        'parent_category': 'commercial',
        '_verification_status': 'mirror_sourced'
    }, 'FAIL'),
    ('bad_uniclass_code', {
        'canonical_id': 'residential.bedroom_master',
        'taxonomy_source': 'Uniclass-2015-SL',
        'uniclass_code': 'EE_25_10_45',
        'parent_category': 'residential',
        '_verification_status': 'nbs_sourced'
    }, 'FAIL'),
]
for name, fixture, expected in tests:
    try: jsonschema.validate(fixture, schema); actual = 'PASS'
    except jsonschema.ValidationError: actual = 'FAIL'
    mark = 'OK' if actual == expected else 'WRONG'
    print(f'  {mark} {name}: expected {expected} got {actual}')
"
```

Expected: 8 OK marks (all assertions pass).

- [ ] **Step 5: Existing Sprint X entries WILL fail until Z.A.3 sweep (expected)**

```bash
python3 scripts/validate-examples.py 2>&1 | grep -E "Pass 5|^  (PASS|FAIL)" | head -20
```

Expected: Pass 5 currently reports failures for all 290 Sprint X entries because they lack `taxonomy_source`. **This is expected** — Z.A.3 sweep fixes them. Do NOT consider this a Z.A.1 failure.

- [ ] **Step 6: Banned-citation grep**

```bash
grep -nE "(§526\.2|§433\.2|OZEV|3rd Edition|Reg 559|Em_room|average room lux)" shared/standards/spaces/room-types-schema.json | grep -v "do NOT\|never cite\|banned\|NOT cite" && echo FAIL || echo PASS
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add shared/standards/spaces/room-types-schema.json
git commit -m "feat(standards): Z.A.1 extend room-types-schema with taxonomy_source discriminator (OmniClass-Table-13/11 + Uniclass-2015-SL) + uniclass_code pattern SL_XX_XX_XX + building_type_codes[] + extended omniclass_code regex (^1[13]-) + extended _verification_status enum (5 values: + nbs_sourced + engineering_consensus) + extended parent_category enum (13 → 21 values) + allOf conditional requirements"
```

### Task Z.A.2: Re-architect master index + create source-notes scaffolding

**Files:**
- Modify: `shared/standards/spaces/room-types.json` (master index)
- Modify: `shared/standards/spaces/README.md` (3-taxonomy documentation)
- Create: `shared/standards/spaces/_source/Uniclass-2015-SL-source-notes.md`
- Create: `shared/standards/spaces/_source/OmniClass-Table-11-source-notes.md`

**Why Sonnet:** Mechanical scaffolding once schema (Z.A.1) and provenance (Z.A.0) are locked.

- [ ] **Step 1: Read Z.A.0 provenance for verbatim Uniclass + T11 URLs**

```bash
cat docs/superpowers/specs/sprint-Z-source-provenance.md | head -50
```

Expected: 2 primary mirror URLs (Uniclass + T11) with edition + access date declared.

- [ ] **Step 2: Re-architect master index `shared/standards/spaces/room-types.json`**

Replace current single `categories` dict with a 3-taxonomy `taxonomies` structure:

```json
{
  "_source": "Multi-taxonomy room-type catalogue: OmniClass Table 13 (Sprint X) + Uniclass 2015 SL (Sprint Z) + OmniClass Table 11 (Sprint Z)",
  "_note": "3 complementary taxonomies. Each entry validates against room-types-schema.json with taxonomy_source discriminator. OmniClass T13 = spaces-by-function (healthcare/education/etc); Uniclass SL = comprehensive room-level (residential/hotel/office/retail/etc); OmniClass T11 = building-level cross-references.",
  "_schema": "room-types-schema.json",
  "taxonomies": {
    "OmniClass-Table-13": {
      "_source_notes": "_source/OmniClass-Table-13-source-notes.md",
      "_edition": "2012-05-16",
      "_directory": "room-types/",
      "categories": {
        "space_planning_types": {"path": "room-types/space_planning_types.json", "entry_count_target": 18, "description": "Space planning intent / BOMA area types"},
        "parking_spaces": {"path": "room-types/parking_spaces.json", "entry_count_target": 14, "description": "Interior + exterior parking"},
        "facility_service_spaces": {"path": "room-types/facility_service_spaces.json", "entry_count_target": 22, "description": "Mechanical / electrical / restrooms / risers / utility"},
        "circulation_spaces": {"path": "room-types/circulation_spaces.json", "entry_count_target": 16, "description": "Corridors / lobbies / vestibules / stairs"},
        "education_and_training_spaces": {"path": "room-types/education_and_training_spaces.json", "entry_count_target": 24, "description": "Classrooms / labs / lecture halls"},
        "recreation_spaces": {"path": "room-types/recreation_spaces.json", "entry_count_target": 18, "description": "Sports / pools / fitness"},
        "government_spaces": {"path": "room-types/government_spaces.json", "entry_count_target": 14, "description": "Courts / legislative / military"},
        "artistic_spaces": {"path": "room-types/artistic_spaces.json", "entry_count_target": 16, "description": "Theatres / galleries / studios"},
        "museum_spaces": {"path": "room-types/museum_spaces.json", "entry_count_target": 12, "description": "Galleries / collections / conservation"},
        "library_spaces": {"path": "room-types/library_spaces.json", "entry_count_target": 10, "description": "Reading rooms / stacks / archives"},
        "spiritual_spaces": {"path": "room-types/spiritual_spaces.json", "entry_count_target": 10, "description": "Worship / ceremonial / procession"},
        "environmentally_controlled_spaces": {"path": "room-types/environmentally_controlled_spaces.json", "entry_count_target": 22, "description": "Cleanrooms / data centres / archive storage"},
        "healthcare_spaces": {"path": "room-types/healthcare_spaces.json", "entry_count_target": 34, "description": "OR / ICU / imaging / pharmacy / dental"}
      }
    },
    "Uniclass-2015-SL": {
      "_source_notes": "_source/Uniclass-2015-SL-source-notes.md",
      "_edition": "Uniclass 2015",
      "_directory": "room-types-uniclass-sl/",
      "categories": {
        "residential": {"path": "room-types-uniclass-sl/residential.json", "entry_count_target": 60, "description": "Bedrooms / kitchens / dining / bathrooms / lounges / single-family + multi-family / dormitory"},
        "commercial": {"path": "room-types-uniclass-sl/commercial.json", "entry_count_target": 40, "description": "Offices / meeting rooms / receptions / banking"},
        "retail": {"path": "room-types-uniclass-sl/retail.json", "entry_count_target": 30, "description": "Shopfloor / fitting / stockroom / checkout / display"},
        "hospitality": {"path": "room-types-uniclass-sl/hospitality.json", "entry_count_target": 40, "description": "Hotel guest rooms / restaurants / kitchens / bars / function rooms"},
        "industrial": {"path": "room-types-uniclass-sl/industrial.json", "entry_count_target": 50, "description": "Manufacturing / processing / workshops / warehouse"},
        "agricultural": {"path": "room-types-uniclass-sl/agricultural.json", "entry_count_target": 20, "description": "Livestock / crops / processing"},
        "transport": {"path": "room-types-uniclass-sl/transport.json", "entry_count_target": 30, "description": "Stations / terminals / waiting / baggage"}
      }
    },
    "OmniClass-Table-11": {
      "_source_notes": "_source/OmniClass-Table-11-source-notes.md",
      "_edition": "OmniClass Table 11 — Construction Entities by Function (latest publicly-available edition; declared at Z.A.0)",
      "_directory": "building-types-t11/",
      "categories": {
        "construction_entities": {"path": "building-types-t11/construction-entities-by-function.json", "entry_count_target": 70, "description": "Whole-building types (single-family / hotel / office building / warehouse / etc.) used for cross-reference rollup"}
      }
    }
  }
}
```

- [ ] **Step 3: Update `shared/standards/spaces/README.md`**

Edit the README to document the 3-taxonomy approach. Replace the existing "Files" section (which only mentions T13) with:

```markdown
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

## CIBSE + NRM2 cross-references — deferred (paid source access blocker)

Sprint X + Sprint Z do NOT transcribe CIBSE LG series or NRM2. `cross_references.cibse_lg` and `cross_references.nrm2` are `null` on every entry. Future Sprint Y back-fills when paid PDFs are available.
```

- [ ] **Step 4: Create `shared/standards/spaces/_source/Uniclass-2015-SL-source-notes.md`**

```markdown
# Uniclass 2015 Table SL — Source Notes

**Last updated:** 2026-06-06

## Source mirror (primary)

- **URL:** <copy verbatim from sprint-Z-source-provenance.md §1>
- **Access date:** 2026-06-06
- **Edition reflected:** Uniclass 2015 (post-2015 amendments — declare specific version)
- **Coverage estimate:** <copy verbatim>

## Source mirror (backups)

<copy verbatim list from provenance spec §1>

## Verification status taxonomy

See `docs/superpowers/specs/sprint-Z-source-provenance.md` §3.

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

Where NBS Source is partial, `_verification_status: engineering_consensus` allowed with mandatory `_inference_note` citing CIBSE / ASHRAE / BS engineering authority. See provenance §7.

## CIBSE + NRM2 deferred (paid source access blocker)

Sprint Z does NOT transcribe CIBSE LG series or NRM2. `cross_references.cibse_lg` and `cross_references.nrm2` stay `null` on every Sprint Z entry.
```

- [ ] **Step 5: Create `shared/standards/spaces/_source/OmniClass-Table-11-source-notes.md`**

Same shape as Sprint X T13 source-notes but for T11:

```markdown
# OmniClass Table 11 — Source Notes

**Last updated:** 2026-06-06

## Source mirror (primary)

- **URL:** <copy verbatim from sprint-Z-source-provenance.md §2>
- **Access date:** 2026-06-06
- **Edition reflected:** <copy verbatim>
- **Coverage estimate:** <copy verbatim>

## Source mirror (backups)

<copy verbatim list>

## Per-task transcription

- Z.C.1 construction-entities-by-function.json (~70 entries) — Opus

## Known transcription gaps

(populated by Z.C.1 implementer report)

## What Table 11 covers

OmniClass Table 11 classifies **whole construction entities by function** (single-family residence, hotel building, office building, warehouse, etc.) — NOT rooms within them. Room-level taxonomy for residential / hotel / etc. lives in Uniclass SL (see Z.B.*).

## Cross-reference role

Sprint Z Uniclass SL room entries reference T11 building codes via `building_type_codes[]` field. Example: `residential.bedroom_master` → `["11-11 11 11"]` (single-family residence).
```

- [ ] **Step 6: Validate master index parses + 3 taxonomies declared**

```bash
python3 -c "
import json
d = json.load(open('shared/standards/spaces/room-types.json'))
print('parse OK')
print('taxonomies:', list(d['taxonomies'].keys()))
for tname, tdata in d['taxonomies'].items():
    cats = tdata['categories']
    total = sum(c['entry_count_target'] for c in cats.values())
    print(f'  {tname}: {len(cats)} categories, total target {total}')
"
```

Expected: 3 taxonomies; T13 13 categories ~230 target; SL 7 categories ~270 target; T11 1 category 70 target.

- [ ] **Step 7: Banned-citation grep + gates**

```bash
grep -rnE "(§526\.2|§433\.2|OZEV|3rd Edition|Reg 559|Em_room|average room lux)" shared/standards/spaces/ | grep -v "do NOT\|never cite\|banned\|NOT cite" && echo FAIL || echo PASS
python3 scripts/validate-examples.py 2>&1 | tail -3
```

Expected: PASS; aggregate may show Pass 5 failures on Sprint X entries (expected pre-Z.A.3 sweep).

- [ ] **Step 8: Commit**

```bash
git add shared/standards/spaces/room-types.json shared/standards/spaces/README.md shared/standards/spaces/_source/Uniclass-2015-SL-source-notes.md shared/standards/spaces/_source/OmniClass-Table-11-source-notes.md
git commit -m "feat(standards): Z.A.2 re-architect master index for 3-taxonomy structure (OmniClass T13 + Uniclass SL + OmniClass T11) + create Uniclass + T11 source-notes scaffolding + update README 3-taxonomy docs"
```

### Task Z.A.3: Sprint X T13 back-compat sweep (add taxonomy_source to all 290 entries)

**Files:**
- Modify: `shared/standards/spaces/room-types/*.json` (all 13 Sprint X category files)

**Why Sonnet:** Mechanical scripted sweep. Pure additive (adds 1 field; changes nothing else). Critical: must not regress any Sprint X entry data.

- [ ] **Step 1: Inspect Sprint X entry shape pre-sweep**

```bash
python3 -c "
import json, glob
for f in sorted(glob.glob('shared/standards/spaces/room-types/*.json'))[:2]:
    d = json.load(open(f))
    if d.get('entries'):
        first = d['entries'][0]
        print(f'{f.split(chr(47))[-1]}: first entry has taxonomy_source = {first.get(\"taxonomy_source\", \"MISSING\")}')
"
```

Expected: `MISSING` (Sprint X shipped without the field).

- [ ] **Step 2: Author the sweep script and run it**

Run this Python one-liner (script does NOT go in repo — one-off):

```bash
python3 -c "
import json, glob
total = 0
for f in sorted(glob.glob('shared/standards/spaces/room-types/*.json')):
    d = json.load(open(f))
    if 'entries' not in d: continue
    for entry in d['entries']:
        if 'taxonomy_source' not in entry:
            entry['taxonomy_source'] = 'OmniClass-Table-13'
            total += 1
    json.dump(d, open(f, 'w'), indent=2, ensure_ascii=False)
print(f'Patched: {total} entries')
"
```

Expected: ~290 entries patched.

- [ ] **Step 3: Verify all 290 entries now have taxonomy_source**

```bash
python3 -c "
import json, glob
total = 0
missing = 0
for f in sorted(glob.glob('shared/standards/spaces/room-types/*.json')):
    d = json.load(open(f))
    for e in d.get('entries', []):
        total += 1
        if 'taxonomy_source' not in e: missing += 1
print(f'Total entries: {total}; missing taxonomy_source: {missing}')
"
```

Expected: total 290; missing 0.

- [ ] **Step 4: Re-run gate to confirm Pass 5 green**

```bash
python3 scripts/validate-examples.py 2>&1 | grep -A 5 "Pass 5" | head -10
```

Expected: `Pass 5: PASS — all room-types entries validate` (no longer failing).

- [ ] **Step 5: Confirm no entry data regressed (spot-check 5 random)**

```bash
python3 -c "
import json, glob, random
random.seed(42)
all_entries = []
for f in sorted(glob.glob('shared/standards/spaces/room-types/*.json')):
    d = json.load(open(f))
    all_entries.extend(d.get('entries', []))
sample = random.sample(all_entries, 5)
for e in sample:
    print(f'  {e[\"canonical_id\"]}: omniclass_code={e[\"omniclass_code\"]}, taxonomy_source={e[\"taxonomy_source\"]}')
"
```

Expected: 5 entries showing original `omniclass_code` (unchanged) + new `taxonomy_source: OmniClass-Table-13`.

- [ ] **Step 6: Aggregate gate green**

```bash
python3 scripts/validate-examples.py 2>&1 | tail -3
```

Expected: 649/649 PASS (Sprint X baseline restored).

- [ ] **Step 7: Commit**

```bash
git add shared/standards/spaces/room-types/
git commit -m "fix(standards): Z.A.3 Sprint X back-compat sweep — add taxonomy_source: OmniClass-Table-13 to all 290 Sprint X entries across 13 T13 category files (pure additive; no entry data regression; restores Pass 5 to PASS after Z.A.1 schema requirement addition)"
```

---

## Phase Z.B — Uniclass 2015 SL per-category transcription (7 tasks, ~25-30 commits)

Goal: transcribe ~270 Uniclass SL entries from declared NBS Source / mirror across 7 per-category files covering the building types T13 lacks. Z.B.1 (residential) is Opus to establish per-entry authoring pattern; Z.B.2-7 are Sonnet once pattern stable.

### Per-task discipline (locked from Z.A.0)

Every Z.B.* task follows this acceptance gate:

1. Implementer consults primary Uniclass SL mirror declared in `sprint-Z-source-provenance.md` §1
2. Each entry gets `taxonomy_source: "Uniclass-2015-SL"` + `uniclass_code` matching pattern `^SL_[0-9]{2}_[0-9]{2}_[0-9]{2}$` verbatim from mirror
3. Each entry's `_verification_status` ∈ `{nbs_sourced, engineering_consensus, inferred}` per Z.A.0 §3
4. **NO FABRICATION** of Uniclass codes — ship verified entries only; document gaps in source-notes
5. Per-entry validates against extended `room-types-schema.json`
6. Banned-citation grep clean
7. `cross_references.*` populated for matching ASHRAE 90.1 / 62.1 / BS EN 12464-1 entries at Z.D.1 (Z.B leaves null)
8. `building_type_codes[]` populated at Z.D.1 (Z.B leaves absent or empty)

### Task Z.B.1: Author residential.json (~60 entries) — Opus pattern-setter

**Files:**
- Create: `shared/standards/spaces/room-types-uniclass-sl/residential.json`

**Why Opus:** First Uniclass SL transcription sets the per-entry authoring pattern for Z.B.2-7; engineering judgement on canonical_id naming for residential rooms (no precedent in T13 spaces-by-function); engineering consensus discipline (residential bedrooms / kitchens may not all be NBS-source-verbatim).

- [ ] **Step 1: Read prerequisites**

```bash
cat docs/superpowers/specs/sprint-Z-source-provenance.md | head -60
cat shared/standards/spaces/room-types-schema.json | python3 -m json.tool | head -80
cat shared/standards/spaces/_source/Uniclass-2015-SL-source-notes.md
```

- [ ] **Step 2: WebFetch the declared Uniclass SL primary mirror**

WebFetch the URL declared at Z.A.0. Extract all residential SL entries (codes matching `SL_25_XX_XX` pattern — Uniclass SL_25 is the typical residential prefix; verify against mirror).

Typical residential coverage:
- **Single-family dwelling rooms:** bedroom_master / bedroom_secondary / bedroom_guest / kitchen / dining / living_room / family_room / bathroom_master / bathroom_secondary / en_suite / powder_room / study / utility / laundry / pantry / hallway / staircase / cloakroom / garage_attached / basement / attic / conservatory / porch / balcony / patio / deck / boot_room / mud_room / snug / games_room / media_room
- **Multi-family / apartment:** studio / one_bedroom / two_bedroom / three_bedroom / penthouse / lobby_residential / corridor_residential / bin_store / bicycle_store / communal_lounge / communal_laundry
- **Dormitory / student housing:** bedroom_single / bedroom_shared / bathroom_shared / kitchen_shared / lounge_communal / study_room
- **Sheltered / care home:** care_room / shared_lounge / activity_room / staff_office

- [ ] **Step 3: Author the file**

Create `shared/standards/spaces/room-types-uniclass-sl/residential.json`:

```json
{
  "_source": "Uniclass 2015 Table SL — Residential rooms (verbatim from primary NBS Source mirror declared in sprint-Z-source-provenance.md §1)",
  "_source_url": "<verbatim primary mirror URL>",
  "_access_date": "2026-06-06",
  "_parent_category": "residential",
  "_taxonomy_source": "Uniclass-2015-SL",
  "_entry_count": <actual count from mirror>,
  "_entry_count_target": 60,
  "_coverage_actual_pct": <100 × actual / 60>,
  "_note": "Per-entry _verification_status records sourcing (nbs_sourced / engineering_consensus / inferred). cross_references.cibse_lg + nrm2 stay null per Sprint Z deferral. building_type_codes populated at Z.D.1 cross-reference back-fill.",
  "entries": [
    {
      "canonical_id": "residential.single_family.bedroom_master",
      "taxonomy_source": "Uniclass-2015-SL",
      "uniclass_code": "<verbatim from mirror, e.g. SL_25_10_15>",
      "parent_category": "residential",
      "parent_path": ["residential", "single_family", "bedrooms"],
      "common_aliases": ["master bedroom", "primary bedroom", "main bedroom", "master suite"],
      "ifc_space_type": "INTERNAL",
      "_verification_status": "nbs_sourced",
      "cross_references": {
        "bs_en_12464_1": null,
        "cibse_lg": null,
        "ashrae_90_1": null,
        "ashrae_62_1": null,
        "nrm2": null
      }
    }
  ]
}
```

For each canonical_id transcribed: use actual Uniclass code verbatim from mirror. For canonical_ids the mirror doesn't cover but engineering authority cites (e.g. CIBSE LG10 §3 lists "snug" as common UK residential room): use `_verification_status: engineering_consensus` with `_inference_note` citing the authority + invented `uniclass_code` synthesised from the SL_25 prefix pattern (per Z.A.0 §7 engineering consensus discipline — Uniclass synthesis allowed when NBS partial AND engineering citation present).

- [ ] **Step 4: Validate against extended schema**

```bash
python3 -c "
import json, jsonschema
schema = json.load(open('shared/standards/spaces/room-types-schema.json'))
d = json.load(open('shared/standards/spaces/room-types-uniclass-sl/residential.json'))
print(f'entries: {len(d[\"entries\"])}/{d[\"_entry_count_target\"]} ({d[\"_coverage_actual_pct\"]}%)')
ns = sum(1 for e in d['entries'] if e['_verification_status'] == 'nbs_sourced')
ec = sum(1 for e in d['entries'] if e['_verification_status'] == 'engineering_consensus')
inf = sum(1 for e in d['entries'] if e['_verification_status'] == 'inferred')
print(f'nbs_sourced: {ns}, engineering_consensus: {ec}, inferred: {inf}')
errors = 0
for entry in d['entries']:
    try: jsonschema.validate(entry, schema)
    except jsonschema.ValidationError as e:
        errors += 1
        print(f'  {entry.get(\"canonical_id\", \"?\")}: FAIL {e.message[:120]}')
if errors == 0: print('All entries PASS schema validation')
ids = [e['canonical_id'] for e in d['entries']]
print(f'duplicates: {set(i for i in ids if ids.count(i) > 1) or \"none\"}')
"
```

Expected: 0 schema errors; mix of nbs_sourced + engineering_consensus declared.

- [ ] **Step 5: Banned-citation grep**

```bash
grep -nE "(§526\.2|§433\.2|OZEV|3rd Edition|Reg 559|Em_room|average room lux)" shared/standards/spaces/room-types-uniclass-sl/residential.json | grep -v "do NOT\|never cite\|banned\|NOT cite" && echo BANNED_FAIL || echo BANNED_PASS
```

- [ ] **Step 6: Gate**

```bash
python3 scripts/validate-examples.py 2>&1 | tail -3
```

Expected: 649 + N entries (where N = actual residential count).

- [ ] **Step 7: Commit**

```bash
git add shared/standards/spaces/room-types-uniclass-sl/residential.json
git commit -m "feat(standards): Z.B.1 NEW residential.json — Uniclass 2015 SL residential rooms (single-family + multi-family + dormitory + sheltered care; sets per-entry authoring pattern for Z.B.2-7; mix of nbs_sourced + engineering_consensus per Z.A.0 §7 discipline)"
```

### Task Z.B.2: Author commercial.json (~40 entries) — Sonnet

**Files:**
- Create: `shared/standards/spaces/room-types-uniclass-sl/commercial.json`

**Why Sonnet:** Per-entry pattern set by Z.B.1; commercial offices have well-established Uniclass coverage.

- [ ] **Step 1: Read Z.B.1 as template**

```bash
python3 -m json.tool shared/standards/spaces/room-types-uniclass-sl/residential.json | head -40
```

- [ ] **Step 2: WebFetch Uniclass SL commercial section + author commercial.json**

Set `_parent_category: "commercial"`, `_entry_count_target: 40`. Typical coverage:
- Office types: open_plan_office / private_office / executive_office / shared_office / hot_desking / quiet_room / phone_booth / focus_pod / collaboration_space
- Meeting rooms: small / medium / large / boardroom / videoconference / training_room
- Support: reception / waiting / mail_room / printing / archive / filing / break_room
- Banking: banking_hall / atm_lobby / vault / safe_deposit / bank_office / advisor_room

Each entry uses `parent_category: "commercial"`, `ifc_space_type: "INTERNAL"`.

- [ ] **Step 3: Validate + uniqueness + grep + gate + commit**

```bash
python3 -c "
import json, jsonschema
schema = json.load(open('shared/standards/spaces/room-types-schema.json'))
d = json.load(open('shared/standards/spaces/room-types-uniclass-sl/commercial.json'))
print(f'entries: {len(d[\"entries\"])}/{d[\"_entry_count_target\"]} ({d[\"_coverage_actual_pct\"]}%)')
errors = 0
for entry in d['entries']:
    try: jsonschema.validate(entry, schema)
    except: errors += 1
print(f'schema errors: {errors}')
ids = [e['canonical_id'] for e in d['entries']]
print(f'duplicates: {set(i for i in ids if ids.count(i) > 1) or \"none\"}')
"
grep -nE "(§526\.2|§433\.2|OZEV|3rd Edition|Reg 559|Em_room|average room lux)" shared/standards/spaces/room-types-uniclass-sl/commercial.json | grep -v "do NOT\|never cite\|banned\|NOT cite" && echo BANNED_FAIL || echo BANNED_PASS
python3 scripts/validate-examples.py 2>&1 | tail -3
git add shared/standards/spaces/room-types-uniclass-sl/commercial.json
git commit -m "feat(standards): Z.B.2 NEW commercial.json — Uniclass 2015 SL commercial rooms (office types + meeting rooms + support + banking)"
```

### Task Z.B.3: Author retail.json (~30 entries) — Sonnet

**Files:**
- Create: `shared/standards/spaces/room-types-uniclass-sl/retail.json`

**Why Sonnet:** Pattern stable.

- [ ] **Step 1: Author retail.json**

Set `_parent_category: "retail"`, `_entry_count_target: 30`. Typical coverage:
- Sales floor types: general_shopfloor / department_store_floor / showroom / boutique
- Specialty: jewellery_display / electronics_display / fashion_floor / grocery_aisle
- Service points: checkout / customer_service_desk / returns_counter / click_and_collect
- Support: fitting_room / stockroom_retail / loading_back_of_house / staff_room_retail / manager_office_retail
- Outdoor / circulation retail: covered_arcade / pedestrianised_street_retail / market_stall

- [ ] **Step 2: Validate + grep + gate + commit**

```bash
python3 -c "
import json, jsonschema
schema = json.load(open('shared/standards/spaces/room-types-schema.json'))
d = json.load(open('shared/standards/spaces/room-types-uniclass-sl/retail.json'))
print(f'entries: {len(d[\"entries\"])}/{d[\"_entry_count_target\"]} ({d[\"_coverage_actual_pct\"]}%)')
errors = 0
for entry in d['entries']:
    try: jsonschema.validate(entry, schema)
    except: errors += 1
print(f'schema errors: {errors}')
ids = [e['canonical_id'] for e in d['entries']]
print(f'duplicates: {set(i for i in ids if ids.count(i) > 1) or \"none\"}')
"
grep -nE "(§526\.2|§433\.2|OZEV|3rd Edition|Reg 559|Em_room|average room lux)" shared/standards/spaces/room-types-uniclass-sl/retail.json | grep -v "do NOT\|never cite\|banned\|NOT cite" && echo BANNED_FAIL || echo BANNED_PASS
python3 scripts/validate-examples.py 2>&1 | tail -3
git add shared/standards/spaces/room-types-uniclass-sl/retail.json
git commit -m "feat(standards): Z.B.3 NEW retail.json — Uniclass 2015 SL retail rooms (sales floor types + specialty + service points + support)"
```

### Task Z.B.4: Author hospitality.json (~40 entries) — Sonnet

**Files:**
- Create: `shared/standards/spaces/room-types-uniclass-sl/hospitality.json`

- [ ] **Step 1: Author hospitality.json**

Set `_parent_category: "hospitality"`, `_entry_count_target: 40`. Typical coverage:
- Hotel guest accommodation: guest_room_standard / guest_room_suite / guest_room_family / guest_room_accessible / penthouse_suite / guest_bathroom / guest_powder_room
- Hotel public areas: lobby_hotel / concierge_desk / business_centre / lounge_guest / breakfast_room / fitness_room_guest / spa_treatment
- Hotel back-of-house: housekeeping / linen_store / luggage_store / staff_canteen_hotel / banqueting_kitchen / dishwash_area
- Restaurant / dining: restaurant_dining / fine_dining / casual_dining / cafe_seating / coffee_bar
- Bar / drinks: cocktail_bar / pub_bar / wine_bar / outdoor_terrace_drinks
- Function: banquet_hall / wedding_function / conference_room / breakout_room

Hotel guest_room entries use `ifc_space_type: "INTERNAL"`; outdoor terrace uses `EXTERNAL`.

- [ ] **Step 2: Validate + grep + gate + commit (mirrors Z.B.3 pattern; substitute file path)**

```bash
git add shared/standards/spaces/room-types-uniclass-sl/hospitality.json
git commit -m "feat(standards): Z.B.4 NEW hospitality.json — Uniclass 2015 SL hospitality rooms (hotel guest accommodation + public areas + back-of-house + restaurant + bar + function)"
```

### Task Z.B.5: Author industrial.json (~50 entries) — Sonnet

**Files:**
- Create: `shared/standards/spaces/room-types-uniclass-sl/industrial.json`

- [ ] **Step 1: Author industrial.json**

Set `_parent_category: "industrial"`, `_entry_count_target: 50`. Typical coverage:
- Manufacturing: assembly_line / fabrication_metal / fabrication_wood / fabrication_plastic / paint_booth / welding_bay / machine_shop / press_room
- Processing: food_processing / chemical_processing / pharmaceutical_processing / petroleum_processing
- Warehouse: warehouse_low_rack / warehouse_high_rack / warehouse_pick_face / cold_storage / freezer_storage / hazmat_storage / bonded_warehouse / dispatch_area / goods_inwards
- Workshop: electrical_workshop / mechanical_workshop / carpentry_workshop / vehicle_service_bay / fitter_workshop
- Industrial support: tool_crib / safety_office / quality_control_office / industrial_canteen / industrial_changing_room
- Outdoor industrial: yard_storage / scaffold_compound / plant_compound

- [ ] **Step 2: Validate + grep + gate + commit**

```bash
git add shared/standards/spaces/room-types-uniclass-sl/industrial.json
git commit -m "feat(standards): Z.B.5 NEW industrial.json — Uniclass 2015 SL industrial rooms (manufacturing + processing + warehouse + workshop + support + outdoor)"
```

### Task Z.B.6: Author agricultural.json (~20 entries) — Sonnet

**Files:**
- Create: `shared/standards/spaces/room-types-uniclass-sl/agricultural.json`

- [ ] **Step 1: Author agricultural.json**

Set `_parent_category: "agricultural"`, `_entry_count_target: 20`. Typical coverage:
- Livestock: cattle_shed / sheep_pen / pig_sty / poultry_house / dairy_parlour / equine_stable / milking_parlour
- Crops: greenhouse / polytunnel / grain_store / crop_packing_shed / drying_room
- Processing on-farm: dairy_processing / abattoir / fish_processing / cheese_aging / cidery_press_room / brewery
- Storage agricultural: feed_store / fodder_loft / slurry_pit / manure_store / silo

`ifc_space_type` typically `INTERNAL`; outdoor pens use `EXTERNAL`.

- [ ] **Step 2: Validate + grep + gate + commit**

```bash
git add shared/standards/spaces/room-types-uniclass-sl/agricultural.json
git commit -m "feat(standards): Z.B.6 NEW agricultural.json — Uniclass 2015 SL agricultural rooms (livestock + crops + processing + storage)"
```

### Task Z.B.7: Author transport.json (~30 entries) — Sonnet

**Files:**
- Create: `shared/standards/spaces/room-types-uniclass-sl/transport.json`

- [ ] **Step 1: Author transport.json**

Set `_parent_category: "transport"`, `_entry_count_target: 30`. Typical coverage:
- Rail: station_concourse / platform_rail / ticket_hall / waiting_room_rail / baggage_handling_rail / signal_room / station_office
- Aviation: terminal_concourse / gate_lounge / baggage_claim / security_screening / customs_immigration / retail_airport / hangar / control_tower / departures_lounge
- Road: bus_station / coach_terminal / taxi_rank_indoor / motorway_service_area / fuel_station_shop / car_rental_desk
- Marine: ferry_terminal / port_terminal / cruise_terminal / waiting_room_marine / boarding_pier

`ifc_space_type` mostly `INTERNAL`; piers/platforms may be `EXTERNAL` or `BERTHING` per IfcSpaceTypeEnum.

- [ ] **Step 2: Validate + grep + gate + commit**

```bash
git add shared/standards/spaces/room-types-uniclass-sl/transport.json
git commit -m "feat(standards): Z.B.7 NEW transport.json — Uniclass 2015 SL transport rooms (rail + aviation + road + marine)"
```

### Phase Z.B end-of-phase cross-check

After all 7 Z.B.* tasks ship:

```bash
python3 -c "
import json, glob
total = 0
target = 0
for f in sorted(glob.glob('shared/standards/spaces/room-types-uniclass-sl/*.json')):
    d = json.load(open(f))
    n = len(d['entries'])
    t = d['_entry_count_target']
    total += n
    target += t
    print(f'  {f.split(chr(47))[-1]}: {n}/{t} ({100*n/t:.0f}%)')
print(f'TOTAL Uniclass SL: {total}/{target} ({100*total/target:.1f}%)')
# Global canonical_id uniqueness across BOTH T13 and SL catalogues
all_ids = []
for f in sorted(glob.glob('shared/standards/spaces/room-types/*.json') + glob.glob('shared/standards/spaces/room-types-uniclass-sl/*.json')):
    d = json.load(open(f))
    all_ids.extend(e['canonical_id'] for e in d.get('entries', []))
dupes = set(i for i in all_ids if all_ids.count(i) > 1)
print(f'global canonical_id duplicates across T13+SL: {dupes if dupes else \"none\"}')
"
```

Expected: 7 lines (one per category); TOTAL ~210-270 (target 270; expect 70-100% coverage); 0 global duplicates.

If TOTAL < 220 (≈80% coverage), Z.E.3 final review verdict downgrades to SHIP-WITH-NOTED-CONCERNS; gaps documented in source-notes.

---

## Phase Z.C — OmniClass T11 building types (1 task, ~3-5 commits)

Goal: transcribe ~70 OmniClass T11 building-type entries from declared mirror. Provides the cross-reference targets for SL room `building_type_codes[]` field (back-filled at Z.D.1).

### Task Z.C.1: Author construction-entities-by-function.json — Opus

**Files:**
- Create: `shared/standards/spaces/building-types-t11/construction-entities-by-function.json`

**Why Opus:** OmniClass T11 is a different taxonomy from T13 (building-level not room-level); needs careful pattern setup; ~70 entries spanning all top-level T11 classes.

- [ ] **Step 1: Read Z.A.0 T11 provenance + Z.A.2 master index target**

```bash
grep -A 5 "OmniClass Table 11" docs/superpowers/specs/sprint-Z-source-provenance.md | head -20
python3 -c "import json; d = json.load(open('shared/standards/spaces/room-types.json')); print(d['taxonomies']['OmniClass-Table-11']['categories']['construction_entities'])"
```

- [ ] **Step 2: WebFetch T11 mirror; extract all top-level + level-3 child entries**

T11 top-level classes (per Sprint Z source survey expectations — verify against mirror):
- 11-11 Residential entities
- 11-13 Commercial entities (offices / banking / retail)
- 11-15 Industrial entities (manufacturing / process / warehouse)
- 11-16 Mixed-use entities
- 11-17 Transportation entities (rail / aviation / road / marine)
- 11-21 Educational entities
- 11-23 Recreation entities
- 11-25 Healthcare entities
- 11-31 Civic / government entities
- 11-33 Religious entities
- 11-35 Cultural entities (museums / theatres)
- 11-37 Agricultural entities

Per parent class: enumerate the level-3 entries the mirror exposes. For residential: single_family_detached / single_family_attached / multi_family_low_rise / multi_family_high_rise / mobile_home / dormitory / hotel / motel. For commercial: office_low_rise / office_high_rise / retail_strip_mall / shopping_centre / restaurant / bank / convention_centre. Etc.

- [ ] **Step 3: Author the file**

Create `shared/standards/spaces/building-types-t11/construction-entities-by-function.json`:

```json
{
  "_source": "OmniClass Table 11 — Construction Entities by Function (verbatim from primary mirror declared in sprint-Z-source-provenance.md §2)",
  "_source_url": "<verbatim>",
  "_access_date": "2026-06-06",
  "_parent_category": "construction_entities",
  "_taxonomy_source": "OmniClass-Table-11",
  "_entry_count": <actual>,
  "_entry_count_target": 70,
  "_coverage_actual_pct": <100 × actual / 70>,
  "_note": "Building-level taxonomy. Used for cross-reference rollup from Uniclass SL room entries via building_type_codes[]. Per-entry _verification_status records sourcing.",
  "entries": [
    {
      "canonical_id": "construction_entities.residential.single_family_detached",
      "taxonomy_source": "OmniClass-Table-11",
      "omniclass_code": "<verbatim from mirror, e.g. 11-11 11 11>",
      "parent_category": "construction_entities",
      "parent_path": ["construction_entities", "residential"],
      "common_aliases": ["single-family home", "detached house", "free-standing residence"],
      "ifc_space_type": "INTERNAL",
      "_verification_status": "mirror_sourced",
      "cross_references": {
        "bs_en_12464_1": null,
        "cibse_lg": null,
        "ashrae_90_1": null,
        "ashrae_62_1": null,
        "nrm2": null
      }
    }
  ]
}
```

- [ ] **Step 4: Validate against schema + uniqueness**

```bash
python3 -c "
import json, jsonschema
schema = json.load(open('shared/standards/spaces/room-types-schema.json'))
d = json.load(open('shared/standards/spaces/building-types-t11/construction-entities-by-function.json'))
print(f'entries: {len(d[\"entries\"])}/{d[\"_entry_count_target\"]} ({d[\"_coverage_actual_pct\"]}%)')
ms = sum(1 for e in d['entries'] if e['_verification_status'] == 'mirror_sourced')
inf = sum(1 for e in d['entries'] if e['_verification_status'] == 'inferred')
print(f'mirror_sourced: {ms}, inferred: {inf}')
errors = 0
for entry in d['entries']:
    try: jsonschema.validate(entry, schema)
    except jsonschema.ValidationError as e:
        errors += 1
        print(f'  {entry.get(\"canonical_id\", \"?\")}: FAIL {e.message[:120]}')
if errors == 0: print('All entries PASS')
ids = [e['canonical_id'] for e in d['entries']]
print(f'duplicates: {set(i for i in ids if ids.count(i) > 1) or \"none\"}')
"
```

Expected: 0 schema errors; entries close to 70.

- [ ] **Step 5: Banned-citation grep + gate + commit**

```bash
grep -nE "(§526\.2|§433\.2|OZEV|3rd Edition|Reg 559|Em_room|average room lux)" shared/standards/spaces/building-types-t11/construction-entities-by-function.json | grep -v "do NOT\|never cite\|banned\|NOT cite" && echo BANNED_FAIL || echo BANNED_PASS
python3 scripts/validate-examples.py 2>&1 | tail -3
git add shared/standards/spaces/building-types-t11/construction-entities-by-function.json
git commit -m "feat(standards): Z.C.1 NEW construction-entities-by-function.json — OmniClass T11 building-level taxonomy (~70 entries across residential + commercial + industrial + mixed_use + transportation + educational + recreation + healthcare + civic + religious + cultural + agricultural top-level classes; cross-reference targets for Uniclass SL room building_type_codes)"
```

---
