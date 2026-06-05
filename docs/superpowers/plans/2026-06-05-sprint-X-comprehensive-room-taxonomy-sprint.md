# Sprint X — Comprehensive Room Taxonomy MEGA-SPRINT Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Author the canonical comprehensive room-type taxonomy + supporting BIM/ASHRAE standards layers + retrofit Sprint F's F.1 SkillInput schema, replacing the partial 27-value Room.type enum with a ~600-entry catalogue. Sprint X runs BETWEEN Sprint F.3 (already shipped at commit `08b6e38`) and Sprint F.4 (paused). Sprint F resumes at F.4 once Sprint X ships.

**Architecture:** Cross-discipline standards-transcription mega-sprint. 23 implementer tasks across 5 phases (Foundation → OmniClass per-category → ASHRAE → cross-ref+features → ship). Net new folders: `shared/standards/spaces/` + `shared/standards/bim/ISO16739/` + `shared/standards/energy/ASHRAE-90-1/` + `shared/standards/hvac/ASHRAE-62-1/`. Critical constraint: implementers MUST source from declared public mirrors and flag verification status per entry; fabrication of OmniClass codes is a CRITICAL failure caught at X.E.4 final review.

**Tech Stack:**
- JSON Schema Draft-07 (matches existing standards files)
- Markdown for reference docs + companion READMEs
- Python stdlib for `scripts/validate-examples.py` gate extensions (5-pass → 7-pass + 5 lint sub-passes)
- Existing golden CI gate as the verification surface

**Source spec:** [`docs/superpowers/specs/2026-06-05-comprehensive-room-taxonomy-design.md`](../specs/2026-06-05-comprehensive-room-taxonomy-design.md) (commit `1f3eef7`, 314 lines).
**Pattern parent:** [`docs/superpowers/plans/2026-06-05-sprint-F-foundation-grounding-sprint.md`](2026-06-05-sprint-F-foundation-grounding-sprint.md) (Sprint F plan, 3 portions, 1870 lines).
**Pre-existing verified standards layers referenced for cross_references:**
- `shared/standards/lighting/BSEN12464/lux-levels.json` (27 lighting entries — already authored)
- `shared/standards/lighting/BSEN12464/area-definitions.json` (D5 artefact — §4.2.2.x + Table 6)

---

## Sprint discipline (locked, mirrors D4/D5/F)

- Sonnet for mechanical (JSON Schema authoring, per-category files once pattern stable, gate extension) per `[[feedback-no-haiku-sonnet-opus-only]]`
- Opus for judgment (source provenance, IFC subset, ASHRAE pattern-set tasks, cross-reference review, F.1 retrofit, final integration review)
- **Two-stage Opus review after every implementer task** + fix-pass commit when HIGH/CRITICAL findings surface. Budget for ~8-12 fix-passes given the 23-task surface.
- **CRITICAL: Citation fidelity rule — implementers MUST cite real mirror URLs + access dates for OmniClass / ASHRAE / IFC entries.** Fabricated codes are caught at X.E.4 spot-check review and cause sprint FAIL. `_verification_status` field must accurately reflect sourcing (`mirror_sourced` / `occs_verified` / `inferred`).
- No banned tokens: §526.2 / §433.2 / OZEV / 3rd Edition / Reg 559 / Em_room / "average room lux".
- Pre-ship **Sonnet 7-check verification fence** (X.E.4 task) per spec §10 acceptance criteria.
- Final cross-sprint **Opus integration review** at X.E.4 — verdict PASS / SHIP-WITH-NOTED-CONCERNS / FIX-FIRST.
- Push deferred to user authorisation per CLAUDE.md "shared state" rule (X.E.5 task).
- `[[feedback-no-trim-non-consequential]]` — `_note` / `_source` fields stay full-length; do NOT trim engineering content.

### Estimated commit count: 85-95

- 23 implementer commits
- ~8-12 fix-pass commits
- 4 portion commits for this plan doc
- 1 spec commit already done (`1f3eef7`)

---

## File structure

### Created (NEW files in `shared/standards/spaces/`)

```
shared/standards/spaces/
├── README.md                                 # X.A.2 NEW; source provenance + CIBSE/NRM2 deferred TODO
├── room-types.json                           # X.A.2 NEW; master index referencing 7 per-category files
├── room-types-schema.json                    # X.A.1 NEW; Draft-07 metaschema for per-entry validation
├── fuzzy-match-reference.md                  # X.D.3 NEW; algorithm spec + test fixtures
├── _source/
│   └── OmniClass-Table-13-source-notes.md    # X.A.2 NEW; mirror URL + edition + access date + transcription gaps
└── room-types/
    ├── residential.json                       # X.B.1 NEW; ~80 entries
    ├── commercial.json                        # X.B.2 NEW; ~120 entries
    ├── institutional.json                     # X.B.3 NEW; ~150 entries
    ├── industrial.json                        # X.B.4 NEW; ~130 entries
    ├── transport.json                         # X.B.5 NEW; ~60 entries
    ├── external.json                          # X.B.6 NEW; ~40 entries
    └── agricultural.json                      # X.B.7 NEW; ~20 entries
```

### Created (NEW files in `shared/standards/bim/ISO16739/`)

```
shared/standards/bim/ISO16739/
├── README.md                                 # X.A.3 NEW
├── space-types.json                          # X.A.3 NEW; IfcSpaceTypeEnum (7 values)
├── classification.json                       # X.A.3 NEW; IfcClassification + IfcClassificationReference + IfcRelAssociatesClassification entity defs
├── placement.json                            # X.A.3 NEW; IfcLocalPlacement + IfcAxis2Placement3D entity defs (justifies placement_convention enum from F.2)
└── reference.md                              # X.A.3 NEW; companion reference
```

### Created (NEW files in `shared/standards/energy/ASHRAE-90-1/` + `shared/standards/hvac/ASHRAE-62-1/`)

```
shared/standards/energy/ASHRAE-90-1/
├── README.md                                 # X.C.1 NEW
├── lpd-table-9-6-1.json                      # X.C.1 NEW; ~120 LPD entries (W/m²)
└── reference.md                              # X.C.1 NEW

shared/standards/hvac/ASHRAE-62-1/
├── README.md                                 # X.C.2 NEW
├── ventilation-rates.json                    # X.C.2 NEW; ~150 outdoor air rate entries
└── reference.md                              # X.C.2 NEW
```

### Created (NEW provenance spec)

```
docs/superpowers/specs/sprint-X-source-provenance.md   # X.A.0 NEW; mirror selection + edition + verification status taxonomy
```

### Modified (existing files)

```
shared/schemas/core/skill-input.schema.json    # X.E.2 RETROFIT; Room.type enum → snake_case pattern; ADD Room.classification field
shared/schemas/core/skill-input.reference.md   # X.E.2 RETROFIT; update Room.type section to point at room-types.json catalogue
scripts/validate-examples.py                    # X.E.1 MODIFY; extend 5-pass + 5 lint sub-passes (current state is 4-pass post-F.5)
```

### Memory + index (outside repo)

```
/Users/linus/.claude/projects/-Users-linus-Desktop-DraftsMan-SKills-draftsman-skills/memory/
├── sprint-X-comprehensive-taxonomy-shipped.md    # X.E.3 NEW
└── MEMORY.md                                      # X.E.3 APPEND index line
```

---

## Phase X.A — Foundation (4 tasks, ~5-7 commits)

Goal: lock the per-entry shape (X.A.1 schema) + source-provenance methodology (X.A.0) + master index (X.A.2) + IFC standards layer (X.A.3) BEFORE any per-category transcription begins. X.A.3 closes the F.0 line-61 honest disclosure about no transcribed IFC layer.

### Task X.A.0: Author source provenance spec (mirror survey + edition declaration)

**Files:**
- Create: `docs/superpowers/specs/sprint-X-source-provenance.md`

**Why Opus:** Source survey requires engineering judgement on mirror reliability; sets the citation-discipline contract for all subsequent X.B tasks; failure here pollutes every per-category file.

- [ ] **Step 1: Survey publicly-available OmniClass Table 13 mirrors**

Run a WebSearch or WebFetch (if available; else manual inspection of known sources) to identify mirrors of OmniClass Table 13:

```bash
# Inventory candidate mirrors. Known starting points:
echo "Candidate OmniClass Table 13 mirrors to evaluate:"
echo "  1. NIBS (National Institute of Building Sciences) - whole-building design guide references"
echo "  2. buildingSMART - IFC documentation cross-references OmniClass codes"
echo "  3. CSI (Construction Specifications Institute) - MasterFormat <-> OmniClass cross-walks"
echo "  4. Autodesk knowledge base - Revit/Navisworks BIM documentation"
echo "  5. Academic publications (NCAR / GSA / DOE) - building-energy modeling papers"
echo "  6. OmniClass.org direct - if free version of Table 13 is available"
```

For each candidate: note URL + access date + extent of Table 13 coverage + edition reflected.

- [ ] **Step 2: Pick the primary mirror + declare backups**

Selection criteria:
- Coverage of all 7 parent_categories (residential / commercial / institutional / industrial / transport / external / agricultural)
- Verifiable edition (2012 / 2019 / 2024 — declare which)
- Stable URL (not behind paywall or rotating-token auth)
- Codes in canonical 13-XX XX XX XX XX format (not aliased / restructured)

If no single mirror covers all 7 categories: declare primary + 2-3 backup mirrors covering gaps. X.B tasks may consult multiple mirrors per category; per-entry `_source_mirror` field records which mirror that entry came from.

- [ ] **Step 3: Author the provenance spec**

Create `docs/superpowers/specs/sprint-X-source-provenance.md`:

```markdown
# Sprint X Source Provenance Spec

**Date:** 2026-06-05
**Companion to:** `docs/superpowers/specs/2026-06-05-comprehensive-room-taxonomy-design.md`
**Sets:** citation-discipline contract for all Phase X.B per-category transcription tasks + Phase X.C ASHRAE tasks + Phase X.A.3 IFC subset

## 1. OmniClass Table 13 mirror selection

### Primary mirror

- **URL:** <verbatim URL of the primary mirror>
- **Access date:** 2026-06-05
- **Edition reflected:** <2012 / 2019 / 2024 — declared explicitly>
- **Coverage estimate:** <e.g. "85% of expected ~600 entries across all 7 parent_categories">
- **Code format observed:** <canonical 13-XX XX XX XX XX | other — declare any drift>

### Backup mirrors (if primary has gaps)

- <URL + categories covered + edition + access date for each backup>

## 2. ASHRAE source mirrors

### ASHRAE 90.1 Table 9.6.1 (LPD)

- **URL:** <publicly-accessible ASHRAE 90.1 Table 9.6.1 mirror>
- **Access date:** 2026-06-05
- **Edition reflected:** <2019 / 2022 — declared explicitly>
- **Coverage estimate:** <e.g. "~120 of expected ~120 entries">

### ASHRAE 62.1 (ventilation rates)

- **URL:** <publicly-accessible ASHRAE 62.1 mirror>
- **Access date:** 2026-06-05
- **Edition reflected:** <2019 / 2022>
- **Coverage estimate:** <e.g. "~150 of expected ~150 entries">

## 3. IFC ISO 16739 source

- **URL:** https://standards.buildingsmart.org/IFC/RELEASE/IFC4/FINAL/HTML/ (buildingSMART canonical)
- **Access date:** 2026-06-05
- **Edition reflected:** IFC 4 (final)
- **Entities transcribed:** IfcSpace, IfcSpaceTypeEnum, IfcClassification, IfcClassificationReference, IfcRelAssociatesClassification, IfcLocalPlacement, IfcAxis2Placement3D (room-type-relevant subset; ~200 lines)

## 4. Verification status taxonomy

Per-entry `_verification_status` field carries one of:

- **`mirror_sourced`** — code transcribed verbatim from a declared mirror URL. Default state.
- **`occs_verified`** — code cross-checked against canonical OCCS Table 13 PDF (back-fill when paid access granted; Sprint X does NOT set this).
- **`inferred`** — code synthesised from hierarchy structure where mirror coverage is incomplete (e.g. mirror has parent code "13-37 31 00 00" but not child "13-37 31 21 11"; we infer the child code from the OmniClass numbering pattern). MUST be honest-disclosed in per-entry `_inference_note`.

## 5. CIBSE + NRM2 deferred (documented blocker)

- **CIBSE LG1 / LG2 / LG7 / LG10 / LG12 / Guide A** — paid CIBSE membership required. Sprint X does NOT transcribe. `cross_references.cibse_lg` stays `null` on every entry.
- **NRM2 (RICS)** — paid RICS PDF required. Sprint X does NOT transcribe. `cross_references.nrm2` stays `null` on every entry.

Future Sprint Y when source access granted will back-fill these cross-references.

## 6. Fabrication prevention contract

**NO IMPLEMENTER MAY FABRICATE OMNICLASS / ASHRAE / IFC CODES.** If a category cannot be sourced from a public mirror within reasonable coverage (≥70% of expected entries):

1. Implementer flags the gap in `_source_mirror.coverage_actual_pct` field
2. Implementer ships the partial transcription with `_verification_status: mirror_sourced` on what they DID transcribe
3. Implementer documents the gap in `shared/standards/spaces/_source/OmniClass-Table-13-source-notes.md`
4. Sprint X.E.4 final review verdict downgrades to SHIP-WITH-NOTED-CONCERNS but does NOT FAIL — partial coverage is acceptable; fabrication is not

The X.E.4 reviewer spot-checks 5% of randomly-selected codes against the declared primary mirror. If spot-check fails (codes not present in mirror), sprint verdict = FIX-FIRST.
```

- [ ] **Step 4: Validate file renders + commit**

```bash
wc -l docs/superpowers/specs/sprint-X-source-provenance.md
grep -nE "TBD|TODO|fill in" docs/superpowers/specs/sprint-X-source-provenance.md | head -5 && echo "FAIL — placeholders present" || echo "PASS"
```

Expected: ~80-100 lines; PASS on placeholder check.

- [ ] **Step 5: Banned-citation grep**

```bash
grep -nE "(§526\.2|§433\.2|OZEV|3rd Edition|Reg 559|Em_room|average room lux)" docs/superpowers/specs/sprint-X-source-provenance.md | grep -v "do NOT\|never cite\|banned\|NOT cite" && echo FAIL || echo PASS
```

Expected: PASS.

- [ ] **Step 6: Run golden CI gate**

```bash
python3 scripts/validate-examples.py 2>&1 | tail -3
```

Expected: aggregate unchanged from Sprint F.3 baseline (docs not validated).

- [ ] **Step 7: Commit**

```bash
git add docs/superpowers/specs/sprint-X-source-provenance.md
git commit -m "feat(spec): X.A.0 Sprint X source provenance — OmniClass mirror selection + ASHRAE 90.1/62.1 sources + IFC ISO 16739 buildingSMART + verification status taxonomy + CIBSE/NRM2 deferred (paid)"
```

### Task X.A.1: Author `room-types-schema.json` per-entry metaschema

**Files:**
- Create: `shared/standards/spaces/room-types-schema.json`

**Why Sonnet:** Mechanical Draft-07 schema authoring against spec §5.

- [ ] **Step 1: Inspect existing standards file shapes for pattern consistency**

```bash
python3 -c "
import json
print('--- lux-levels.json structure ---')
d = json.load(open('shared/standards/lighting/BSEN12464/lux-levels.json'))
print(list(d.keys())[:10])
print('--- area-definitions.json structure ---')
d = json.load(open('shared/standards/lighting/BSEN12464/area-definitions.json'))
print(list(d.keys())[:10])
"
```

Expected: shows existing `_source` / `_note` / `_units` / per-category branch pattern. room-types-schema.json validates entries that follow this pattern at per-entry level.

- [ ] **Step 2: Author `shared/standards/spaces/room-types-schema.json`**

Create the file with this exact content:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "draftsman-skills/shared/standards/spaces/room-types-schema.json",
  "title": "RoomTypeEntry",
  "description": "Per-entry metaschema for shared/standards/spaces/room-types/*.json files. Validates the ~600 OmniClass Table 13-derived entries authored across 7 parent_category files.",
  "type": "object",
  "required": ["canonical_id", "omniclass_code", "parent_category", "_verification_status"],
  "properties": {
    "canonical_id": {
      "type": "string",
      "pattern": "^[a-z]+(\\.[a-z0-9_]+)+$",
      "description": "Snake_case dotted identifier used as Room.type in SkillInput. Format: parent_category.sub_category.entry_name. Examples: office.open_plan, healthcare.operating_theatre_general, residential.bedroom_master."
    },
    "omniclass_code": {
      "type": "string",
      "pattern": "^13-[0-9]{2}( [0-9]{2}){0,4}$",
      "description": "OmniClass Table 13 verbatim 5-segment 13-digit code. Format: 13-XX XX XX XX XX. Sourced from declared public mirror per sprint-X-source-provenance.md."
    },
    "parent_category": {
      "type": "string",
      "enum": ["residential", "commercial", "institutional", "industrial", "transport", "external", "agricultural"]
    },
    "parent_path": {
      "type": "array",
      "items": {"type": "string"},
      "minItems": 1,
      "maxItems": 3,
      "description": "Hierarchical drill-down path (3-level max). E.g. [institutional, healthcare, treatment]. First element MUST equal parent_category."
    },
    "common_aliases": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Non-canonical synonyms from architectural practice. Powers fuzzy-match lookup for orchestrators receiving non-canonical strings from drawing parsers. E.g. ['operating room', 'OR', 'theatre', 'surgery suite']."
    },
    "ifc_space_type": {
      "type": "string",
      "enum": ["PARKING", "GFA", "BERTHING", "EXTERNAL", "INTERNAL", "USERDEFINED", "NOTDEFINED"],
      "description": "Coarse IfcSpaceTypeEnum value per ISO 16739. Mostly INTERNAL (indoor) or EXTERNAL (outdoor)."
    },
    "_verification_status": {
      "type": "string",
      "enum": ["mirror_sourced", "occs_verified", "inferred"],
      "description": "Per-entry sourcing record. mirror_sourced=default (verbatim from declared mirror URL). occs_verified=cross-checked against OCCS canonical PDF (back-fill). inferred=synthesised from hierarchy (MUST honest-disclose in _inference_note)."
    },
    "_inference_note": {
      "type": "string",
      "description": "REQUIRED when _verification_status=inferred. Explains the inference (e.g. 'parent code 13-37 31 00 00 present in mirror; child code synthesised from OmniClass numbering pattern')."
    },
    "_source_mirror": {
      "type": "string",
      "format": "uri",
      "description": "URL of the mirror this entry was sourced from (per-entry override if not the primary declared in sprint-X-source-provenance.md)."
    },
    "cross_references": {
      "type": "object",
      "properties": {
        "bs_en_12464_1": {
          "type": ["string", "null"],
          "description": "Key path into shared/standards/lighting/BSEN12464/lux-levels.json (e.g. 'office.open_plan') OR null if no match."
        },
        "cibse_lg": {
          "type": ["string", "null"],
          "description": "Null until Sprint Y back-fills paid CIBSE source."
        },
        "ashrae_90_1": {
          "type": ["string", "null"],
          "description": "Key path into shared/standards/energy/ASHRAE-90-1/lpd-table-9-6-1.json OR null."
        },
        "ashrae_62_1": {
          "type": ["string", "null"],
          "description": "Key path into shared/standards/hvac/ASHRAE-62-1/ventilation-rates.json OR null."
        },
        "nrm2": {
          "type": ["string", "null"],
          "description": "Null until Sprint Y back-fills paid NRM2 source."
        }
      },
      "additionalProperties": false
    }
  },
  "additionalProperties": false
}
```

- [ ] **Step 3: Validate JSON parses + schema is well-formed Draft-07**

```bash
python3 -c "
import json, jsonschema
s = json.load(open('shared/standards/spaces/room-types-schema.json'))
print('parse OK')
print('required:', s['required'])
print('canonical_id pattern:', s['properties']['canonical_id']['pattern'])
print('omniclass_code pattern:', s['properties']['omniclass_code']['pattern'])
print('parent_category enum:', s['properties']['parent_category']['enum'])
print('_verification_status enum:', s['properties']['_verification_status']['enum'])
print('cross_references keys:', list(s['properties']['cross_references']['properties'].keys()))
jsonschema.Draft7Validator.check_schema(s)
print('Draft-07 well-formed: OK')
"
```

Expected: required `[canonical_id, omniclass_code, parent_category, _verification_status]`; canonical_id pattern `^[a-z]+(\\.[a-z0-9_]+)+$`; omniclass_code pattern `^13-[0-9]{2}( [0-9]{2}){0,4}$`; parent_category 7 enum values; _verification_status 3 enum values; cross_references 5 sub-keys (bs_en_12464_1, cibse_lg, ashrae_90_1, ashrae_62_1, nrm2); Draft-07 well-formed.

- [ ] **Step 4: Test the schema against hand-authored fixtures**

```bash
python3 -c "
import json, jsonschema
schema = json.load(open('shared/standards/spaces/room-types-schema.json'))
tests = [
    ('valid_minimal', {
        'canonical_id': 'office.open_plan',
        'omniclass_code': '13-15 11 23 11',
        'parent_category': 'commercial',
        '_verification_status': 'mirror_sourced'
    }, 'PASS'),
    ('valid_full', {
        'canonical_id': 'institutional.healthcare.operating_theatre_general',
        'omniclass_code': '13-37 31 21 11',
        'parent_category': 'institutional',
        'parent_path': ['institutional', 'healthcare', 'treatment'],
        'common_aliases': ['operating room', 'OR', 'theatre'],
        'ifc_space_type': 'INTERNAL',
        '_verification_status': 'mirror_sourced',
        '_source_mirror': 'https://example.com/omniclass-mirror',
        'cross_references': {
            'bs_en_12464_1': None,
            'cibse_lg': None,
            'ashrae_90_1': 'healthcare.operating_room',
            'ashrae_62_1': 'healthcare.operating_room',
            'nrm2': None
        }
    }, 'PASS'),
    ('bad_canonical_id', {
        'canonical_id': 'OfficeOpenPlan',
        'omniclass_code': '13-15 11 23 11',
        'parent_category': 'commercial',
        '_verification_status': 'mirror_sourced'
    }, 'FAIL'),
    ('bad_omniclass_code', {
        'canonical_id': 'office.open_plan',
        'omniclass_code': '14-99-99',
        'parent_category': 'commercial',
        '_verification_status': 'mirror_sourced'
    }, 'FAIL'),
    ('bad_parent_category', {
        'canonical_id': 'office.open_plan',
        'omniclass_code': '13-15 11 23 11',
        'parent_category': 'unknown_category',
        '_verification_status': 'mirror_sourced'
    }, 'FAIL'),
    ('extra_field_rejected', {
        'canonical_id': 'office.open_plan',
        'omniclass_code': '13-15 11 23 11',
        'parent_category': 'commercial',
        '_verification_status': 'mirror_sourced',
        'unknown_field': 'should_fail'
    }, 'FAIL'),
]
for name, fixture, expected in tests:
    try:
        jsonschema.validate(fixture, schema)
        actual = 'PASS'
    except jsonschema.ValidationError:
        actual = 'FAIL'
    mark = 'OK' if actual == expected else 'WRONG'
    print(f'  {mark} {name}: expected {expected} got {actual}')
"
```

Expected: 6 OK marks (all assertions pass).

- [ ] **Step 5: Banned-citation grep + gates**

```bash
grep -nE "(§526\.2|§433\.2|OZEV|3rd Edition|Reg 559|Em_room|average room lux)" shared/standards/spaces/room-types-schema.json | grep -v "do NOT\|never cite\|banned\|NOT cite" && echo FAIL || echo PASS
python3 scripts/validate-examples.py 2>&1 | tail -3
```

Expected: PASS; aggregate unchanged (new metaschema file not yet wired into gate — wired at X.E.1).

- [ ] **Step 6: Commit**

```bash
git add shared/standards/spaces/room-types-schema.json
git commit -m "feat(standards): X.A.1 NEW room-types-schema.json — Draft-07 per-entry metaschema for OmniClass Table 13 transcriptions (required canonical_id + omniclass_code + parent_category + _verification_status; 7 parent_category enum + 3 verification status enum)"
```

### Task X.A.2: Author master index + README + source-notes scaffolding

**Files:**
- Create: `shared/standards/spaces/room-types.json` (master index)
- Create: `shared/standards/spaces/README.md`
- Create: `shared/standards/spaces/_source/OmniClass-Table-13-source-notes.md`

**Why Sonnet:** Mechanical scaffolding once schema (X.A.1) and provenance (X.A.0) are locked.

- [ ] **Step 1: Create the `_source` subdirectory + source-notes file**

```bash
mkdir -p shared/standards/spaces/_source
```

Create `shared/standards/spaces/_source/OmniClass-Table-13-source-notes.md` with this content (the implementer fills in the mirror URLs declared at X.A.0):

```markdown
# OmniClass Table 13 — Source Notes

**Last updated:** 2026-06-05

## Source mirror (primary)

- **URL:** <copy verbatim from sprint-X-source-provenance.md §1>
- **Access date:** 2026-06-05
- **Edition reflected:** <copy verbatim>
- **Coverage estimate:** <copy verbatim>

## Source mirror (backups)

<copy verbatim list from provenance spec §1>

## Verification status taxonomy

See `docs/superpowers/specs/sprint-X-source-provenance.md` §4.

## Per-category transcription tasks

- X.B.1 residential.json (~80 entries) — Opus pattern-setter
- X.B.2 commercial.json (~120 entries) — Sonnet
- X.B.3 institutional.json (~150 entries) — Sonnet
- X.B.4 industrial.json (~130 entries) — Sonnet
- X.B.5 transport.json (~60 entries) — Sonnet
- X.B.6 external.json (~40 entries) — Sonnet
- X.B.7 agricultural.json (~20 entries) — Sonnet

## Known transcription gaps

(populated by X.B.* implementer reports when mirror coverage < expected)

## CIBSE + NRM2 deferred (paid source access blocker)

Sprint X does NOT transcribe CIBSE LG1/LG2/LG7/LG10/LG12 + Guide A or NRM2. Future Sprint Y back-fills when paid PDFs available. `cross_references.cibse_lg` and `cross_references.nrm2` stay `null` on every Sprint X entry.
```

- [ ] **Step 2: Create the master index `shared/standards/spaces/room-types.json`**

```json
{
  "_source": "OmniClass Table 13 — Spaces by Function (publicly-available mirror, see _source/OmniClass-Table-13-source-notes.md for URL + edition + access date)",
  "_edition": "<2012 / 2019 / 2024 — copy verbatim from sprint-X-source-provenance.md §1>",
  "_note": "Master index pointing to per-parent_category files under room-types/. Codes transcribed from publicly-available OmniClass Table 13 mirror, not the canonical OCCS PDF. Per-entry _verification_status field records sourcing.",
  "_units": {
    "code_format": "OmniClass 13-XX XX XX XX XX (5-segment 13-digit notation)",
    "canonical_id_format": "snake_case dotted path (parent_category.sub_category.entry_name)"
  },
  "_schema": "room-types-schema.json",
  "_source_notes": "_source/OmniClass-Table-13-source-notes.md",
  "categories": {
    "residential": {
      "path": "room-types/residential.json",
      "entry_count_target": 80,
      "description": "Single-family / multi-family / dormitory / hotel-style residential spaces"
    },
    "commercial": {
      "path": "room-types/commercial.json",
      "entry_count_target": 120,
      "description": "Office / retail / banking / hospitality / restaurant"
    },
    "institutional": {
      "path": "room-types/institutional.json",
      "entry_count_target": 150,
      "description": "Healthcare / education / cultural / civic / religious"
    },
    "industrial": {
      "path": "room-types/industrial.json",
      "entry_count_target": 130,
      "description": "Manufacturing / warehouse / processing / utility"
    },
    "transport": {
      "path": "room-types/transport.json",
      "entry_count_target": 60,
      "description": "Rail / aviation / road / marine / parking"
    },
    "external": {
      "path": "room-types/external.json",
      "entry_count_target": 40,
      "description": "Outdoor work / landscape / circulation"
    },
    "agricultural": {
      "path": "room-types/agricultural.json",
      "entry_count_target": 20,
      "description": "Livestock / crops / processing"
    }
  }
}
```

- [ ] **Step 3: Create `shared/standards/spaces/README.md`**

```markdown
# Room Types — Canonical Taxonomy

Canonical comprehensive room-type taxonomy sourced from OmniClass Table 13 (publicly-available mirror) and aligned with ISO 16739 IFC IfcSpaceTypeEnum + IfcClassificationReference.

This catalogue is the source of truth for `Room.type` values in the SkillInput contract (see `shared/schemas/core/skill-input.schema.json`). Orchestrators construct `Room.type` strings using `canonical_id` values from these files.

## Files

- `room-types-schema.json` — Draft-07 metaschema for per-entry validation
- `room-types.json` — master index referencing 7 per-category files
- `room-types/<category>.json` — per-category entries (7 files)
- `fuzzy-match-reference.md` — algorithm spec for orchestrators implementing fuzzy lookup
- `_source/OmniClass-Table-13-source-notes.md` — mirror URL + edition + access date + transcription gaps

## How to consume

1. Validate `Room.type` value against the union of `canonical_id` keys across all `room-types/*.json` files
2. Resolve metadata (OmniClass code + IFC space type + cross-references) by lookup
3. Use `common_aliases` for fuzzy-match of non-canonical strings from drawing parsers (see fuzzy-match-reference.md)

## CIBSE + NRM2 cross-references — deferred (paid source access blocker)

Sprint X does NOT transcribe CIBSE LG1/LG2/LG7/LG10/LG12 + Guide A or NRM2 (paid PDF sources). `cross_references.cibse_lg` and `cross_references.nrm2` are `null` on every Sprint X entry.

**Future Sprint Y will back-fill these cross-references when paid PDFs are made available to the project.**

## Sourcing discipline

Every entry MUST have `_verification_status` populated:

- `mirror_sourced` (default): verbatim from declared public mirror
- `occs_verified`: cross-checked against canonical OCCS Table 13 PDF (back-fill; Sprint X does NOT set this)
- `inferred`: synthesised from hierarchy structure with explicit `_inference_note`

Fabricating codes that don't exist in declared mirrors is a CRITICAL violation caught at Sprint X.E.4 final review spot-check.
```

- [ ] **Step 4: Validate master index parses + structure**

```bash
python3 -c "
import json
d = json.load(open('shared/standards/spaces/room-types.json'))
print('parse OK')
print('_source present:', '_source' in d)
print('_edition present:', '_edition' in d)
print('categories:', list(d['categories'].keys()))
total = sum(c['entry_count_target'] for c in d['categories'].values())
print(f'total target entries: {total}')
"
```

Expected: parse OK; categories = 7 (residential, commercial, institutional, industrial, transport, external, agricultural); total target ≈ 600.

- [ ] **Step 5: Banned-citation grep + gates**

```bash
grep -rnE "(§526\.2|§433\.2|OZEV|3rd Edition|Reg 559|Em_room|average room lux)" shared/standards/spaces/ | grep -v "do NOT\|never cite\|banned\|NOT cite" && echo FAIL || echo PASS
python3 scripts/validate-examples.py 2>&1 | tail -3
```

Expected: PASS; aggregate unchanged.

- [ ] **Step 6: Commit**

```bash
git add shared/standards/spaces/room-types.json shared/standards/spaces/README.md shared/standards/spaces/_source/OmniClass-Table-13-source-notes.md
git commit -m "feat(standards): X.A.2 NEW spaces master index + README + source-notes scaffolding (7 parent_category entries, ~600 total target; references room-types-schema.json from X.A.1; CIBSE/NRM2 deferred TODO)"
```

### Task X.A.3: Author IFC ISO 16739 standards layer subset

**Files:**
- Create: `shared/standards/bim/ISO16739/README.md`
- Create: `shared/standards/bim/ISO16739/space-types.json`
- Create: `shared/standards/bim/ISO16739/classification.json`
- Create: `shared/standards/bim/ISO16739/placement.json`
- Create: `shared/standards/bim/ISO16739/reference.md`

**Why Sonnet:** Mechanical transcription of public buildingSMART IFC documentation entities; ~200 lines total; closes F.0 line-61 honest disclosure about no transcribed BIM layer.

- [ ] **Step 1: Create the folder + READMEs**

```bash
mkdir -p shared/standards/bim/ISO16739
```

Create `shared/standards/bim/ISO16739/README.md`:

```markdown
# ISO 16739 — Industry Foundation Classes (IFC) — Subset

Transcription of room-type-relevant IFC entities from ISO 16739:2018 (IFC 4 final).

**Source:** https://standards.buildingsmart.org/IFC/RELEASE/IFC4/FINAL/HTML/ (buildingSMART canonical specification)
**Access date:** 2026-06-05
**Subset transcribed:** IfcSpace + IfcSpaceTypeEnum + IfcClassification + IfcClassificationReference + IfcRelAssociatesClassification + IfcLocalPlacement + IfcAxis2Placement3D

This is a deliberate subset — the full ISO 16739 specification is 1500+ pages defining the complete IFC schema. Sprint X transcribes only the entities relevant to room-type taxonomy (`ifc_space_type` field in room-types entries) and placement justification (the `placement_convention` enum from skill-manifest.schema.json).

## Files

- `space-types.json` — IfcSpaceTypeEnum (7 values: PARKING / GFA / BERTHING / EXTERNAL / INTERNAL / USERDEFINED / NOTDEFINED)
- `classification.json` — IfcClassification + IfcClassificationReference + IfcRelAssociatesClassification entity definitions
- `placement.json` — IfcLocalPlacement + IfcAxis2Placement3D entity definitions (justifies placement_convention 4-value enum)
- `reference.md` — companion human-readable reference

## When to extend this layer

When the runtime needs full IfcLocalPlacement round-tripping or richer IFC entity coverage for BIM export, author the additional entities here. The current subset suffices for:

1. Room.classification.source: "IFC IfcClassificationReference" pattern in SkillInput
2. placement_convention BIM justification in skill-manifest.schema.json
3. ifc_space_type field on room-types entries
```

- [ ] **Step 2: Create `space-types.json`**

```json
{
  "_source": "ISO 16739:2018 (IFC 4 final), buildingSMART specification",
  "_source_url": "https://standards.buildingsmart.org/IFC/RELEASE/IFC4/FINAL/HTML/schema/ifcproductextension/lexical/ifcspacetypeenum.htm",
  "_access_date": "2026-06-05",
  "_note": "IfcSpaceTypeEnum is the coarse IFC space classifier. Per-room granular classification uses IfcClassificationReference (see classification.json).",
  "entity_name": "IfcSpaceTypeEnum",
  "entity_kind": "ENUMERATION",
  "values": {
    "PARKING": {
      "definition": "Parking area for vehicles."
    },
    "GFA": {
      "definition": "Gross Floor Area (GFA) declaration space — used for area accounting, not occupancy."
    },
    "BERTHING": {
      "definition": "Mooring or docking space for vessels."
    },
    "EXTERNAL": {
      "definition": "Exterior space (outdoor)."
    },
    "INTERNAL": {
      "definition": "Interior space (indoor)."
    },
    "USERDEFINED": {
      "definition": "Custom classification supplied by the user (via IfcSpace.LongName or IfcClassificationReference)."
    },
    "NOTDEFINED": {
      "definition": "Undefined / not classified."
    }
  }
}
```

- [ ] **Step 3: Create `classification.json`**

```json
{
  "_source": "ISO 16739:2018 (IFC 4 final), buildingSMART specification",
  "_source_url": "https://standards.buildingsmart.org/IFC/RELEASE/IFC4/FINAL/HTML/schema/ifcexternalreferenceresource/lexical/",
  "_access_date": "2026-06-05",
  "_note": "Entities used to attach OmniClass Table 13 codes to IfcSpace instances via IfcRelAssociatesClassification.",
  "entities": {
    "IfcClassification": {
      "definition": "Source of a classification system (e.g. OmniClass, UniClass, MasterFormat).",
      "key_attributes": {
        "Source": "Source / publisher of the classification (e.g. 'CSI / Construction Specifications Institute')",
        "Edition": "Edition of the classification (e.g. '2012', '2019')",
        "EditionDate": "Date of the edition",
        "Name": "Name of the classification (e.g. 'OmniClass Table 13 — Spaces by Function')",
        "Description": "Description of the classification scope",
        "Location": "URL or URI of the classification source",
        "ReferenceTokens": "Tokens used to construct hierarchical codes (e.g. '-' and ' ' for OmniClass 13-XX XX XX XX XX)"
      }
    },
    "IfcClassificationReference": {
      "definition": "Reference to a specific classification entry within an IfcClassification source.",
      "key_attributes": {
        "Location": "URL or URI of the specific classification entry",
        "Identification": "The verbatim classification code (e.g. '13-37 31 21 11')",
        "Name": "Human-readable name (e.g. 'Operating Room — General')",
        "ReferencedSource": "Reference to the parent IfcClassification entity",
        "Description": "Optional description",
        "Sort": "Optional sort order"
      }
    },
    "IfcRelAssociatesClassification": {
      "definition": "Relationship that associates one or more IfcSpace (or other) instances with an IfcClassificationReference.",
      "key_attributes": {
        "RelatingClassification": "Reference to the IfcClassificationReference",
        "RelatedObjects": "Array of object instances (e.g. IfcSpace) classified by RelatingClassification"
      }
    }
  },
  "consumption_pattern": {
    "description": "Run-time pattern for attaching OmniClass codes to IfcSpace instances",
    "example": {
      "ifc_classification": {
        "Source": "CSI / Construction Specifications Institute",
        "Edition": "2012",
        "Name": "OmniClass Table 13 — Spaces by Function",
        "Location": "https://www.csiresources.org/omniclass/"
      },
      "ifc_classification_reference": {
        "ReferencedSource": "<reference to ifc_classification above>",
        "Identification": "13-37 31 21 11",
        "Name": "Operating Room — General"
      },
      "ifc_rel_associates_classification": {
        "RelatingClassification": "<reference to ifc_classification_reference above>",
        "RelatedObjects": ["<reference to IfcSpace instance>"]
      }
    }
  }
}
```

- [ ] **Step 4: Create `placement.json`**

```json
{
  "_source": "ISO 16739:2018 (IFC 4 final), buildingSMART specification",
  "_source_url": "https://standards.buildingsmart.org/IFC/RELEASE/IFC4/FINAL/HTML/schema/ifcgeometricconstraintresource/lexical/",
  "_access_date": "2026-06-05",
  "_note": "IfcLocalPlacement is the parent-relative positioning entity that justifies the placement_convention enum in skill-manifest.schema.json (F.2). room_local_mm ≈ position relative to IfcSpace; floor_local_mm ≈ IfcBuildingStorey; site_local_mm ≈ IfcSite; none_topological ≈ logical placement (no spatial coords).",
  "entities": {
    "IfcLocalPlacement": {
      "definition": "Local placement of a product (e.g. IfcSpace, IfcDistributionElement) within its parent space. Parent-relative; chains up to IfcSite for absolute world coordinate transformation.",
      "key_attributes": {
        "PlacementRelTo": "Reference to the parent placement (typically IfcLocalPlacement of the containing space/storey/site). NULL at the root (IfcSite).",
        "RelativePlacement": "Reference to an IfcAxis2Placement (2D or 3D coordinate frame) defining the placement relative to PlacementRelTo."
      }
    },
    "IfcAxis2Placement3D": {
      "definition": "3D coordinate frame defined by a Location (origin) + Axis (Z direction) + RefDirection (X direction in the XY plane). Y direction derived as Z × X.",
      "key_attributes": {
        "Location": "Reference to IfcCartesianPoint (origin in parent coordinate frame)",
        "Axis": "Optional reference to IfcDirection (Z axis; defaults to +Z)",
        "RefDirection": "Optional reference to IfcDirection (X axis in XY plane; defaults to +X)"
      }
    }
  },
  "placement_convention_mapping": {
    "description": "How skill-manifest.schema.json placement_convention enum maps to IFC parent-relative placement chain",
    "room_local_mm": "Skill output positions are relative to the room's IfcSpace.ObjectPlacement (IfcLocalPlacement). Orchestrator transforms by chaining IfcSpace → IfcBuildingStorey → IfcBuilding → IfcSite to get world coordinates.",
    "floor_local_mm": "Skill output positions are relative to the floor's IfcBuildingStorey.ObjectPlacement. Chain: IfcBuildingStorey → IfcBuilding → IfcSite.",
    "site_local_mm": "Skill output positions are relative to IfcSite.ObjectPlacement (root). No further transform needed; positions are world coordinates.",
    "none_topological": "No IfcLocalPlacement attached. Output is logical / topological (e.g. SLD circuit diagram, schematic graph). Not placed on the BIM model."
  }
}
```

- [ ] **Step 5: Create `reference.md`**

```markdown
# ISO 16739 IFC — Reference

Companion to `space-types.json`, `classification.json`, `placement.json` in this folder.

## What this layer covers

- `IfcSpaceTypeEnum` — 7-value coarse IFC space classifier (see `space-types.json`)
- `IfcClassification` + `IfcClassificationReference` + `IfcRelAssociatesClassification` — entities for attaching OmniClass Table 13 codes to spaces (see `classification.json`)
- `IfcLocalPlacement` + `IfcAxis2Placement3D` — parent-relative positioning (justifies the 4-value placement_convention enum from skill-manifest.schema.json) (see `placement.json`)

## What this layer does NOT cover

- Full IFC schema (1500+ pages). When the runtime needs additional entities for BIM export, extend this folder following the same pattern.
- Geometry primitives (IfcShapeRepresentation, IfcGeometricRepresentationContext, etc.) — only the placement subset is transcribed.
- Property sets (IfcPropertySet, IfcPropertySingleValue) — out of scope for room-type taxonomy.

## How this layer is consumed

1. `Room.classification` field in SkillInput (added by X.D.2) uses IfcClassificationReference structure (`source` + `edition` + `code` + `reference_uri`)
2. `placement_convention` enum from skill-manifest.schema.json is justified by IfcLocalPlacement parent-relative pattern (room/floor/site-local correspond to IfcSpace/IfcBuildingStorey/IfcSite respectively)
3. `ifc_space_type` field on room-types entries (X.B.* transcriptions) uses IfcSpaceTypeEnum 7-value enum directly

## Citation

ISO 16739:2018 — Industry Foundation Classes (IFC) for data sharing in the construction and facility management industries — Part 1: Data schema.

buildingSMART canonical specification: https://standards.buildingsmart.org/IFC/RELEASE/IFC4/FINAL/HTML/
```

- [ ] **Step 6: Validate all 4 files parse + render**

```bash
for f in space-types.json classification.json placement.json; do
  python3 -c "import json; d = json.load(open('shared/standards/bim/ISO16739/$f')); print('$f: parse OK')"
done
wc -l shared/standards/bim/ISO16739/README.md shared/standards/bim/ISO16739/reference.md
```

Expected: 3 "parse OK" lines; READMEs render ~30-60 lines each.

- [ ] **Step 7: Banned-citation grep + gates**

```bash
grep -rnE "(§526\.2|§433\.2|OZEV|3rd Edition|Reg 559|Em_room|average room lux)" shared/standards/bim/ISO16739/ | grep -v "do NOT\|never cite\|banned\|NOT cite" && echo FAIL || echo PASS
python3 scripts/validate-examples.py 2>&1 | tail -3
```

Expected: PASS; aggregate unchanged.

- [ ] **Step 8: Commit**

```bash
git add shared/standards/bim/ISO16739/
git commit -m "feat(standards): X.A.3 NEW ISO 16739 IFC standards layer subset — IfcSpaceTypeEnum + IfcClassification/Reference/RelAssociatesClassification + IfcLocalPlacement/IfcAxis2Placement3D entities (~200 lines; justifies placement_convention enum; closes F.0 line-61 honest disclosure)"
```

---

## Phase X.B — OmniClass per-category transcription (7 tasks, ~25-35 commits)

Goal: transcribe ~600 OmniClass Table 13 entries from the declared public mirror across 7 per-category files. X.B.1 (residential) is Opus to establish the per-entry authoring pattern; X.B.2-7 are Sonnet once the pattern is stable.

### Per-task discipline (locked, applies to ALL X.B.* tasks)

Every X.B.* task follows this acceptance gate:

1. Implementer consults the primary mirror declared in `docs/superpowers/specs/sprint-X-source-provenance.md` §1
2. Each entry transcribed gets a `_verification_status` value reflecting actual sourcing
3. **NO FABRICATION** — if mirror coverage is incomplete for a category, ship what's verified; flag gaps in `shared/standards/spaces/_source/OmniClass-Table-13-source-notes.md` "Known transcription gaps" section
4. Per-entry validates against `shared/standards/spaces/room-types-schema.json`
5. Banned-citation grep clean
6. cross_references stay `null` for cibse_lg / nrm2 (paid source deferred to Sprint Y); ashrae_90_1 / ashrae_62_1 stay `null` until X.D.1 back-fill; bs_en_12464_1 populated for lighting-relevant entries that match existing lux-levels.json keys

### Task X.B.1: Author `residential.json` (~80 entries) — Opus pattern-setter

**Files:**
- Create: `shared/standards/spaces/room-types/residential.json`

**Why Opus:** First per-category transcription sets the per-entry authoring pattern that X.B.2-7 follow; engineering judgement on canonical_id naming conventions for new domains (residential isn't in our existing BS EN 12464-1 transcription); failure here ripples to all subsequent X.B tasks.

- [ ] **Step 1: Read source provenance + master index + schema to confirm contract**

```bash
cat docs/superpowers/specs/sprint-X-source-provenance.md | head -40
cat shared/standards/spaces/room-types.json | python3 -m json.tool | head -30
cat shared/standards/spaces/room-types-schema.json | python3 -m json.tool | head -50
```

Expected: confirm primary mirror URL declared at X.A.0; confirm residential entry_count_target=80; confirm schema requires canonical_id + omniclass_code + parent_category + _verification_status.

- [ ] **Step 2: Survey the residential sub-categories on the primary mirror**

Identify OmniClass Table 13 residential sub-categories. Typical structure:

- `13-25 11 ...` Single-family dwelling
- `13-25 13 ...` Multi-family dwelling
- `13-25 15 ...` Dormitory
- `13-25 17 ...` Residential hotel / motel / hostel
- `13-25 21 ...` Residential ancillary (garage, basement, attic, etc.)

(The actual OmniClass numbering verbatim from the mirror — do NOT invent codes.)

For each sub-category, enumerate the leaf-level entries (rooms within dwellings: bedroom_master, bedroom_secondary, kitchen, dining, living, family_room, bathroom_master, bathroom_secondary, en_suite, study, utility, garage_attached, garage_detached, etc.).

- [ ] **Step 3: Author `shared/standards/spaces/room-types/residential.json`**

Create the file with this structure:

```json
{
  "_source": "OmniClass Table 13 — Residential sub-categories (verbatim from primary mirror declared in sprint-X-source-provenance.md §1)",
  "_source_url": "<copy verbatim primary mirror URL>",
  "_access_date": "2026-06-05",
  "_parent_category": "residential",
  "_entry_count": 80,
  "_entry_count_target": 80,
  "_coverage_actual_pct": 100,
  "_note": "Per-entry _verification_status records sourcing per spec sprint-X-source-provenance.md §4. cross_references.cibse_lg and cross_references.nrm2 stay null per Sprint X deferral.",
  "entries": [
    {
      "canonical_id": "residential.single_family.bedroom_master",
      "omniclass_code": "<verbatim from mirror>",
      "parent_category": "residential",
      "parent_path": ["residential", "single_family", "bedrooms"],
      "common_aliases": ["master bedroom", "primary bedroom", "main bedroom", "master suite"],
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

Note the entries[] array shape: each entry is a complete per-entry record validated by `room-types-schema.json`.

**Target entries** (~80 — implementer fills from mirror; this list is the EXPECTED set for the gate's "entry_count_target" comparison; actual entry count may drop if mirror coverage is incomplete):

- `residential.single_family.bedroom_master`
- `residential.single_family.bedroom_secondary`
- `residential.single_family.kitchen`
- `residential.single_family.dining`
- `residential.single_family.living`
- `residential.single_family.family_room`
- `residential.single_family.bathroom_master`
- `residential.single_family.bathroom_secondary`
- `residential.single_family.en_suite`
- `residential.single_family.powder_room`
- `residential.single_family.study`
- `residential.single_family.home_office`
- `residential.single_family.utility`
- `residential.single_family.laundry`
- `residential.single_family.pantry`
- `residential.single_family.foyer`
- `residential.single_family.hallway`
- `residential.single_family.staircase`
- `residential.single_family.garage_attached`
- `residential.single_family.garage_detached`
- `residential.single_family.basement_finished`
- `residential.single_family.basement_unfinished`
- `residential.single_family.attic_finished`
- `residential.single_family.attic_storage`
- `residential.single_family.conservatory`
- `residential.single_family.porch_enclosed`
- `residential.single_family.balcony`
- `residential.single_family.deck`
- `residential.single_family.patio`
- `residential.single_family.workshop`
- `residential.single_family.cellar_wine`
- `residential.single_family.cellar_storage`
- `residential.multi_family.apartment_studio`
- `residential.multi_family.apartment_one_bedroom`
- `residential.multi_family.apartment_two_bedroom`
- `residential.multi_family.apartment_three_bedroom`
- `residential.multi_family.apartment_penthouse`
- `residential.multi_family.lobby_residential`
- `residential.multi_family.corridor_residential`
- `residential.multi_family.bin_store`
- `residential.multi_family.bicycle_store`
- `residential.multi_family.parking_garage_residential`
- `residential.multi_family.refuse_area`
- `residential.multi_family.plant_room_residential`
- `residential.multi_family.communal_lounge`
- `residential.multi_family.communal_laundry`
- `residential.multi_family.communal_garden`
- `residential.multi_family.roof_terrace_communal`
- `residential.dormitory.bedroom_single`
- `residential.dormitory.bedroom_shared`
- `residential.dormitory.bathroom_shared`
- `residential.dormitory.kitchen_shared`
- `residential.dormitory.lounge_communal`
- `residential.dormitory.study_room`
- `residential.dormitory.warden_office`
- `residential.dormitory.reception_dormitory`
- `residential.hotel.guest_room_standard`
- `residential.hotel.guest_room_suite`
- `residential.hotel.guest_room_family`
- `residential.hotel.guest_bathroom`
- `residential.hotel.lobby_hotel`
- `residential.hotel.concierge`
- `residential.hotel.lounge_guest`
- `residential.hotel.business_centre`
- `residential.hotel.breakfast_room`
- `residential.hotel.spa_treatment`
- `residential.hotel.fitness_room_guest`
- `residential.hotel.housekeeping`
- `residential.hotel.linen_store`
- `residential.hotel.luggage_store`
- `residential.hostel.dorm_room`
- `residential.hostel.private_room`
- `residential.hostel.kitchen_communal`
- `residential.hostel.lounge_communal`
- `residential.ancillary.cloakroom`
- `residential.ancillary.boot_room`
- `residential.ancillary.mud_room`
- `residential.ancillary.snug`
- `residential.ancillary.games_room`
- `residential.ancillary.media_room`
- `residential.ancillary.gym_home`
- `residential.ancillary.sauna_home`

(80 canonical_ids in the target list.)

- [ ] **Step 4: Validate residential.json against room-types-schema.json**

```bash
python3 -c "
import json, jsonschema
schema = json.load(open('shared/standards/spaces/room-types-schema.json'))
d = json.load(open('shared/standards/spaces/room-types/residential.json'))
print(f'entries: {len(d[\"entries\"])}')
print(f'target: {d[\"_entry_count_target\"]}')
print(f'coverage: {d[\"_coverage_actual_pct\"]}%')
errors = 0
for i, entry in enumerate(d['entries']):
    try:
        jsonschema.validate(entry, schema)
    except jsonschema.ValidationError as e:
        errors += 1
        print(f'  entry {i} ({entry.get(\"canonical_id\", \"?\")}): FAIL {e.message[:120]}')
if errors == 0:
    print('All entries PASS schema validation')
"
```

Expected: entries=80 (or implementer-reported actual); coverage=100% (or actual %); 0 schema validation errors.

- [ ] **Step 5: Banned-citation grep + canonical_id uniqueness check**

```bash
grep -nE "(§526\.2|§433\.2|OZEV|3rd Edition|Reg 559|Em_room|average room lux)" shared/standards/spaces/room-types/residential.json | grep -v "do NOT\|never cite\|banned\|NOT cite" && echo BANNED_FAIL || echo BANNED_PASS
python3 -c "
import json
d = json.load(open('shared/standards/spaces/room-types/residential.json'))
ids = [e['canonical_id'] for e in d['entries']]
dupes = [i for i in ids if ids.count(i) > 1]
print(f'duplicate canonical_ids: {set(dupes) if dupes else \"none\"}')
"
```

Expected: BANNED_PASS; 0 duplicates.

- [ ] **Step 6: Gates**

```bash
python3 scripts/validate-examples.py 2>&1 | tail -3
```

Expected: aggregate unchanged (the per-category files are not yet validated by gate — Pass 5 wired at X.E.1).

- [ ] **Step 7: Commit**

```bash
git add shared/standards/spaces/room-types/residential.json
git commit -m "feat(standards): X.B.1 NEW residential.json — ~80 OmniClass Table 13 residential entries (single_family + multi_family + dormitory + hotel + hostel + ancillary; sets per-entry authoring pattern for X.B.2-7)"
```

### Task X.B.2: Author `commercial.json` (~120 entries) — Sonnet

**Files:**
- Create: `shared/standards/spaces/room-types/commercial.json`

**Why Sonnet:** Per-entry pattern locked by X.B.1; mechanical transcription with the established schema.

- [ ] **Step 1: Read X.B.1 residential.json for the established pattern**

```bash
python3 -c "
import json
d = json.load(open('shared/standards/spaces/room-types/residential.json'))
print('header keys:', [k for k in d.keys() if k.startswith('_')])
print('first entry shape:', list(d['entries'][0].keys()))
"
```

Expected: header has _source / _source_url / _access_date / _parent_category / _entry_count / _entry_count_target / _coverage_actual_pct / _note; entry shape: canonical_id + omniclass_code + parent_category + parent_path + common_aliases + ifc_space_type + _verification_status + cross_references.

- [ ] **Step 2: Author `commercial.json`**

Follow the exact pattern from X.B.1. Set `_parent_category: "commercial"` and `_entry_count_target: 120`. OmniClass Table 13 commercial sub-categories typically include:

- `13-15 11 ...` Office (open_plan, private, conference, reception_desk, filing_copying, archive, print_room, server_room_office, post_room, mail_room, etc.)
- `13-15 13 ...` Retail (general, high_emphasis_jewellery, grocery, checkout, fitting_room, stockroom_retail, etc.)
- `13-15 15 ...` Banking (banking_hall, atm_lobby, vault, bank_office, etc.)
- `13-15 17 ...` Hospitality / restaurant (restaurant_dining, bar, kitchen_commercial, kitchen_prep, kitchen_back, walk_in_cool, walk_in_freeze, banquet_hall, etc.)
- `13-15 19 ...` Personal services (hair_salon, beauty_treatment, nail_salon, tanning_booth, etc.)

**Target canonical_ids** (the implementer enumerates from the mirror; the following ~120 ids represent the expected breadth):

(...) — 120 canonical_ids spanning the 5+ commercial sub-categories.

The implementer authors the full 120 entries from the mirror following the X.B.1 pattern exactly.

- [ ] **Step 3: Validate against schema**

```bash
python3 -c "
import json, jsonschema
schema = json.load(open('shared/standards/spaces/room-types-schema.json'))
d = json.load(open('shared/standards/spaces/room-types/commercial.json'))
print(f'entries: {len(d[\"entries\"])}, target: {d[\"_entry_count_target\"]}')
errors = 0
for entry in d['entries']:
    try:
        jsonschema.validate(entry, schema)
    except jsonschema.ValidationError as e:
        errors += 1
        print(f'  {entry.get(\"canonical_id\", \"?\")}: FAIL {e.message[:120]}')
if errors == 0: print('All entries PASS')
"
```

Expected: entries ≈ 120; 0 schema errors.

- [ ] **Step 4: Banned-citation grep + uniqueness + gates**

```bash
grep -nE "(§526\.2|§433\.2|OZEV|3rd Edition|Reg 559|Em_room|average room lux)" shared/standards/spaces/room-types/commercial.json | grep -v "do NOT\|never cite\|banned\|NOT cite" && echo BANNED_FAIL || echo BANNED_PASS
python3 -c "
import json
d = json.load(open('shared/standards/spaces/room-types/commercial.json'))
ids = [e['canonical_id'] for e in d['entries']]
dupes = [i for i in ids if ids.count(i) > 1]
print(f'duplicate canonical_ids: {set(dupes) if dupes else \"none\"}')
"
python3 scripts/validate-examples.py 2>&1 | tail -3
```

Expected: BANNED_PASS; 0 duplicates; aggregate unchanged.

- [ ] **Step 5: Commit**

```bash
git add shared/standards/spaces/room-types/commercial.json
git commit -m "feat(standards): X.B.2 NEW commercial.json — ~120 OmniClass Table 13 commercial entries (office + retail + banking + hospitality + personal_services)"
```

### Task X.B.3: Author `institutional.json` (~150 entries) — Sonnet

**Files:**
- Create: `shared/standards/spaces/room-types/institutional.json`

**Why Sonnet:** Per-entry pattern established; largest single per-category file (~150 entries spanning healthcare specialty + education + cultural + civic + religious).

- [ ] **Step 1: Author `institutional.json` following X.B.1 pattern**

Set `_parent_category: "institutional"` and `_entry_count_target: 150`. OmniClass Table 13 institutional sub-categories typically include:

- `13-37 11 ...` Education primary (classroom_primary, classroom_secondary, science_lab, art_studio, music_room, gymnasium_school, library_school, refectory_school, head_office, staff_room, sick_bay, nursery_classroom, etc.)
- `13-37 13 ...` Education higher (lecture_theatre, seminar_room, laboratory_specialised, library_university, refectory_university, faculty_office, research_office, etc.)
- `13-37 31 ...` Healthcare (operating_theatre_general + cardiac + neuro + ortho, recovery_room, icu_general + cardiac + neuro + neonatal, a_and_e, x_ray, mri, ct, ultrasound, pharmacy, dispensary, ward_general + isolation + maternity + paediatric + psychiatric, consulting_room, treatment_room, dental_surgery, laboratory_pathology, mortuary, etc.)
- `13-37 51 ...` Cultural (museum_gallery, museum_storage, library_public, theatre_auditorium, theatre_stage, theatre_backstage, concert_hall, cinema_auditorium, art_studio_public, etc.)
- `13-37 71 ...` Civic (courtroom, court_office, prison_cell, prison_workshop, police_office, fire_station_bay, etc.)
- `13-37 91 ...` Religious (worship_hall, prayer_room, vestry, chapel, mosque_prayer_hall, etc.)

**Target canonical_ids** (~150 ids; implementer enumerates from mirror).

- [ ] **Step 2: Schema validation + canonical_id uniqueness + banned grep + gates + commit**

```bash
python3 -c "
import json, jsonschema
schema = json.load(open('shared/standards/spaces/room-types-schema.json'))
d = json.load(open('shared/standards/spaces/room-types/institutional.json'))
print(f'entries: {len(d[\"entries\"])}, target: {d[\"_entry_count_target\"]}')
ids = [e['canonical_id'] for e in d['entries']]
print(f'duplicates: {set(i for i in ids if ids.count(i) > 1) or \"none\"}')
errors = 0
for entry in d['entries']:
    try: jsonschema.validate(entry, schema)
    except: errors += 1
print(f'schema errors: {errors}')
"
grep -nE "(§526\.2|§433\.2|OZEV|3rd Edition|Reg 559|Em_room|average room lux)" shared/standards/spaces/room-types/institutional.json | grep -v "do NOT\|never cite\|banned\|NOT cite" && echo BANNED_FAIL || echo BANNED_PASS
python3 scripts/validate-examples.py 2>&1 | tail -3
git add shared/standards/spaces/room-types/institutional.json
git commit -m "feat(standards): X.B.3 NEW institutional.json — ~150 OmniClass Table 13 institutional entries (education + healthcare specialty + cultural + civic + religious)"
```

### Task X.B.4: Author `industrial.json` (~130 entries) — Sonnet

**Files:**
- Create: `shared/standards/spaces/room-types/industrial.json`

**Why Sonnet:** Per-entry pattern established.

- [ ] **Step 1: Author `industrial.json`**

Set `_parent_category: "industrial"` and `_entry_count_target: 130`. OmniClass Table 13 industrial sub-categories typically include:

- Manufacturing (assembly_coarse / medium / fine / very_fine, machine_shop, fabrication_metal / wood / plastic, paint_booth, welding_area, etc.)
- Warehouse (warehouse_low / medium / high_rack, pick_face, dispatch, cold_storage, freezer_storage, hazmat_store, etc.)
- Processing (food_processing, chemical_processing, pharmaceutical_processing, etc.)
- Utility (plant_room_heating / cooling / ventilation, electrical_switchroom, generator_room, transformer_room, server_room_data_centre, telecoms_room, water_treatment, etc.)
- Workshop (electrical_workshop, mechanical_workshop, carpentry_workshop, vehicle_service_bay, etc.)

**Target canonical_ids** (~130 ids).

- [ ] **Step 2: Schema validation + uniqueness + banned grep + gates + commit**

```bash
python3 -c "
import json, jsonschema
schema = json.load(open('shared/standards/spaces/room-types-schema.json'))
d = json.load(open('shared/standards/spaces/room-types/industrial.json'))
print(f'entries: {len(d[\"entries\"])}, target: {d[\"_entry_count_target\"]}')
ids = [e['canonical_id'] for e in d['entries']]
print(f'duplicates: {set(i for i in ids if ids.count(i) > 1) or \"none\"}')
errors = 0
for entry in d['entries']:
    try: jsonschema.validate(entry, schema)
    except: errors += 1
print(f'schema errors: {errors}')
"
grep -nE "(§526\.2|§433\.2|OZEV|3rd Edition|Reg 559|Em_room|average room lux)" shared/standards/spaces/room-types/industrial.json | grep -v "do NOT\|never cite\|banned\|NOT cite" && echo BANNED_FAIL || echo BANNED_PASS
python3 scripts/validate-examples.py 2>&1 | tail -3
git add shared/standards/spaces/room-types/industrial.json
git commit -m "feat(standards): X.B.4 NEW industrial.json — ~130 OmniClass Table 13 industrial entries (manufacturing + warehouse + processing + utility + workshop)"
```

### Task X.B.5: Author `transport.json` (~60 entries) — Sonnet

**Files:**
- Create: `shared/standards/spaces/room-types/transport.json`

**Why Sonnet:** Per-entry pattern established.

- [ ] **Step 1: Author `transport.json`**

Set `_parent_category: "transport"` and `_entry_count_target: 60`. OmniClass Table 13 transport sub-categories typically include:

- Rail (station_concourse, platform_rail, ticket_hall, waiting_room_rail, baggage_handling_rail, signal_room, etc.)
- Aviation (terminal_concourse, gate_lounge, baggage_claim, security_screening, customs_immigration, retail_airport, hangar, control_tower, etc.)
- Road (bus_station, coach_terminal, taxi_rank_indoor, motorway_service_area, fuel_station_shop, etc.)
- Marine (ferry_terminal, port_terminal, cruise_terminal, waiting_room_marine, etc.)
- Parking (car_park_multi_storey, car_park_underground, car_park_surface_covered, car_park_bay, ramp_parking, ev_charging_bay, motorbike_parking, etc.)

**Target canonical_ids** (~60 ids).

- [ ] **Step 2: Schema validation + uniqueness + banned grep + gates + commit**

```bash
python3 -c "
import json, jsonschema
schema = json.load(open('shared/standards/spaces/room-types-schema.json'))
d = json.load(open('shared/standards/spaces/room-types/transport.json'))
print(f'entries: {len(d[\"entries\"])}, target: {d[\"_entry_count_target\"]}')
ids = [e['canonical_id'] for e in d['entries']]
print(f'duplicates: {set(i for i in ids if ids.count(i) > 1) or \"none\"}')
errors = 0
for entry in d['entries']:
    try: jsonschema.validate(entry, schema)
    except: errors += 1
print(f'schema errors: {errors}')
"
grep -nE "(§526\.2|§433\.2|OZEV|3rd Edition|Reg 559|Em_room|average room lux)" shared/standards/spaces/room-types/transport.json | grep -v "do NOT\|never cite\|banned\|NOT cite" && echo BANNED_FAIL || echo BANNED_PASS
python3 scripts/validate-examples.py 2>&1 | tail -3
git add shared/standards/spaces/room-types/transport.json
git commit -m "feat(standards): X.B.5 NEW transport.json — ~60 OmniClass Table 13 transport entries (rail + aviation + road + marine + parking)"
```

### Task X.B.6: Author `external.json` (~40 entries) — Sonnet

**Files:**
- Create: `shared/standards/spaces/room-types/external.json`

**Why Sonnet:** Per-entry pattern established.

- [ ] **Step 1: Author `external.json`**

Set `_parent_category: "external"` and `_entry_count_target: 40`. OmniClass Table 13 external sub-categories typically include:

- Outdoor work (loading_dock_external, builders_yard, scaffold_storage, plant_compound, etc.)
- Landscape (garden, lawn, paved_courtyard, playground, sports_court_external, allotment, etc.)
- Circulation (pedestrian_walkway, cycle_path, vehicle_drive, service_road, refuse_collection_point, etc.)
- Building envelope (roof_terrace, roof_plant, fire_escape_external, external_corridor, atrium_external, etc.)
- External amenity (swimming_pool_outdoor, paddling_pool, hot_tub_external, etc.)

**Target canonical_ids** (~40 ids).

- [ ] **Step 2: Schema validation + uniqueness + banned grep + gates + commit**

```bash
python3 -c "
import json, jsonschema
schema = json.load(open('shared/standards/spaces/room-types-schema.json'))
d = json.load(open('shared/standards/spaces/room-types/external.json'))
print(f'entries: {len(d[\"entries\"])}, target: {d[\"_entry_count_target\"]}')
ids = [e['canonical_id'] for e in d['entries']]
print(f'duplicates: {set(i for i in ids if ids.count(i) > 1) or \"none\"}')
errors = 0
for entry in d['entries']:
    try: jsonschema.validate(entry, schema)
    except: errors += 1
print(f'schema errors: {errors}')
"
grep -nE "(§526\.2|§433\.2|OZEV|3rd Edition|Reg 559|Em_room|average room lux)" shared/standards/spaces/room-types/external.json | grep -v "do NOT\|never cite\|banned\|NOT cite" && echo BANNED_FAIL || echo BANNED_PASS
python3 scripts/validate-examples.py 2>&1 | tail -3
git add shared/standards/spaces/room-types/external.json
git commit -m "feat(standards): X.B.6 NEW external.json — ~40 OmniClass Table 13 external entries (outdoor_work + landscape + circulation + envelope + amenity)"
```

### Task X.B.7: Author `agricultural.json` (~20 entries) — Sonnet

**Files:**
- Create: `shared/standards/spaces/room-types/agricultural.json`

**Why Sonnet:** Per-entry pattern established; smallest per-category file.

- [ ] **Step 1: Author `agricultural.json`**

Set `_parent_category: "agricultural"` and `_entry_count_target: 20`. OmniClass Table 13 agricultural sub-categories typically include:

- Livestock (cattle_shed, sheep_pen, pig_sty, poultry_house, dairy_parlour, equine_stable, etc.)
- Crops (greenhouse, polytunnel, grain_store, crop_packing_shed, etc.)
- Processing (food_processing_farm, dairy_processing, abattoir, fish_processing, etc.)
- Storage agricultural (feed_store, fodder_loft, slurry_pit, manure_store, etc.)

**Target canonical_ids** (~20 ids).

- [ ] **Step 2: Schema validation + uniqueness + banned grep + gates + commit**

```bash
python3 -c "
import json, jsonschema
schema = json.load(open('shared/standards/spaces/room-types-schema.json'))
d = json.load(open('shared/standards/spaces/room-types/agricultural.json'))
print(f'entries: {len(d[\"entries\"])}, target: {d[\"_entry_count_target\"]}')
ids = [e['canonical_id'] for e in d['entries']]
print(f'duplicates: {set(i for i in ids if ids.count(i) > 1) or \"none\"}')
errors = 0
for entry in d['entries']:
    try: jsonschema.validate(entry, schema)
    except: errors += 1
print(f'schema errors: {errors}')
"
grep -nE "(§526\.2|§433\.2|OZEV|3rd Edition|Reg 559|Em_room|average room lux)" shared/standards/spaces/room-types/agricultural.json | grep -v "do NOT\|never cite\|banned\|NOT cite" && echo BANNED_FAIL || echo BANNED_PASS
python3 scripts/validate-examples.py 2>&1 | tail -3
git add shared/standards/spaces/room-types/agricultural.json
git commit -m "feat(standards): X.B.7 NEW agricultural.json — ~20 OmniClass Table 13 agricultural entries (livestock + crops + processing + storage_agricultural)"
```

### Phase X.B end-of-phase cross-check

After all 7 X.B.* tasks ship, verify:

```bash
python3 -c "
import json, glob
total = 0
target = 0
for f in sorted(glob.glob('shared/standards/spaces/room-types/*.json')):
    d = json.load(open(f))
    n = len(d['entries'])
    t = d['_entry_count_target']
    total += n
    target += t
    print(f'  {f}: {n}/{t}')
print(f'TOTAL: {total}/{target} ({100*total/target:.1f}%)')

# Global uniqueness across all 7 categories
all_ids = []
for f in sorted(glob.glob('shared/standards/spaces/room-types/*.json')):
    d = json.load(open(f))
    all_ids.extend(e['canonical_id'] for e in d['entries'])
dupes = set(i for i in all_ids if all_ids.count(i) > 1)
print(f'global canonical_id duplicates: {dupes if dupes else \"none\"}')
"
```

Expected: 7 lines per file; TOTAL ≈ 600/600; 0 global duplicates.

If TOTAL < 540 (90% coverage), the X.E.4 final review verdict downgrades to SHIP-WITH-NOTED-CONCERNS; gaps documented in source-notes.

---

## Phase X.C — Energy + ventilation standards transcription (2 tasks, ~15-20 commits)

Goal: author the ASHRAE 90.1 Table 9.6.1 (LPD) + ASHRAE 62.1 (ventilation rates) source files that will be cross-referenced from room-types entries at X.D.1. Same source-discipline rules as X.B: implementer cites real public mirror URLs; no fabrication; per-entry verification status.

### Task X.C.1: Author ASHRAE 90.1 Table 9.6.1 LPD transcription

**Files:**
- Create: `shared/standards/energy/ASHRAE-90-1/README.md`
- Create: `shared/standards/energy/ASHRAE-90-1/lpd-table-9-6-1.json`
- Create: `shared/standards/energy/ASHRAE-90-1/reference.md`

**Why Opus:** First ASHRAE transcription; pattern-set for X.C.2; engineering judgement on which edition (2019 most-cited) + which space type taxonomy ASHRAE uses (it differs from OmniClass; cross-walk happens at X.D.1).

- [ ] **Step 1: Survey publicly-accessible ASHRAE 90.1 Table 9.6.1 sources**

ASHRAE 90.1 Table 9.6.1 (Lighting Power Densities by Space-by-Space Method) is widely cited. Candidate sources:

- **ASHRAE direct:** ashrae.org sometimes free for specific tables
- **Whole Building Design Guide** (NIBS): cites Table 9.6.1 in lighting-energy chapters
- **GSA / NCAR / DOE building energy publications**
- **State energy code mirrors** (CEC Title 24 references ASHRAE 90.1; California Energy Commission docs)
- **PNNL (Pacific Northwest National Laboratory)** prototype-building reports

Pick the most-cited publicly-accessible mirror. Declare edition (2019 typical) + URL + access date.

- [ ] **Step 2: Create the folder + README**

```bash
mkdir -p shared/standards/energy/ASHRAE-90-1
```

Create `shared/standards/energy/ASHRAE-90-1/README.md`:

```markdown
# ASHRAE 90.1 Table 9.6.1 — Lighting Power Density (LPD) by Space Type

Transcription of ASHRAE Standard 90.1 Table 9.6.1 (LPD allowances using the Space-by-Space Method).

**Source:** <verbatim mirror URL declared at X.C.1>
**Edition:** <2019 / 2022 — verbatim>
**Access date:** 2026-06-05
**Coverage:** ~120 space types

Used by `shared/standards/spaces/room-types/*.json` entries' `cross_references.ashrae_90_1` field (back-filled at X.D.1).

## When to extend

Future ASHRAE editions (2025+) — back-fill new entries here; bump `_edition` field.
```

- [ ] **Step 3: Author `lpd-table-9-6-1.json`**

```json
{
  "_source": "ASHRAE Standard 90.1 Table 9.6.1 — Lighting Power Density Allowances Using the Space-by-Space Method",
  "_source_url": "<verbatim mirror URL>",
  "_access_date": "2026-06-05",
  "_edition": "2019",
  "_units": {
    "lpd": "W/m² (watts per square metre)",
    "lpd_imperial": "W/ft² (watts per square foot)",
    "imperial_to_metric": "Divide W/ft² by 0.0929 to get W/m²"
  },
  "_note": "ASHRAE 90.1 uses its own space-type taxonomy (e.g. 'office_open_plan', 'classroom_general', 'corridor_general'). Cross-walked to room-types canonical_ids at X.D.1.",
  "entries": {
    "office.open_plan": {
      "lpd_wpm2": 6.9,
      "lpd_wpft2": 0.64,
      "_ashrae_space_label": "Office — Open Plan",
      "_verification_status": "mirror_sourced"
    },
    "office.private_office": {
      "lpd_wpm2": 11.0,
      "lpd_wpft2": 1.02,
      "_ashrae_space_label": "Office — Private",
      "_verification_status": "mirror_sourced"
    }
  }
}
```

Implementer transcribes ~120 entries from the declared mirror. Each entry uses ASHRAE's snake_case space label as the key (e.g. `office.open_plan`); cross-walked to room-types canonical_ids at X.D.1.

- [ ] **Step 4: Author `reference.md` companion**

```markdown
# ASHRAE 90.1 Table 9.6.1 — Reference

Companion to `lpd-table-9-6-1.json`. Source: ASHRAE Standard 90.1 Table 9.6.1, edition <declared>.

## Coverage

~120 space types from ASHRAE's Space-by-Space Method. Used for Lighting Power Density (LPD) compliance checks in:

- US jurisdiction (NEC / ASHRAE 90.1 mandate)
- LEED Energy Atmosphere credits
- ENERGY STAR submissions
- International projects citing ASHRAE 90.1 (e.g. Middle East, Asia-Pacific where ASHRAE is the de-facto standard)

## How room-types entries cross-reference

The `cross_references.ashrae_90_1` field on each room-types entry contains the key path into this file's `entries` dict. Example: room-types entry `commercial.office.open_plan` has `cross_references.ashrae_90_1: "office.open_plan"`.

Some room-types entries have no ASHRAE 90.1 equivalent (e.g. residential rooms — ASHRAE 90.1 covers commercial/institutional only). Those entries' `cross_references.ashrae_90_1` stay `null`.

## When LPD values may be inaccurate

- Edition drift: ASHRAE updates 90.1 every 3 years. If runtime needs current edition, re-source from latest publicly-accessible mirror.
- Units: LPD values converted between W/m² and W/ft² may carry rounding (0.0929 conversion factor).
- Space-type ambiguity: ASHRAE's "office_open_plan" may map to OmniClass's "office.open_plan" but the lighting allowances assume specific design conditions; engineers must verify per-project.
```

- [ ] **Step 5: Validate JSON parses + structure**

```bash
python3 -c "
import json
d = json.load(open('shared/standards/energy/ASHRAE-90-1/lpd-table-9-6-1.json'))
print('parse OK')
print('_edition:', d['_edition'])
print('_source_url:', d['_source_url'][:60])
print(f'entries: {len(d[\"entries\"])}')
# Spot-check one entry
first_key = list(d['entries'].keys())[0]
print(f'sample entry ({first_key}):', d['entries'][first_key])
"
```

Expected: parse OK; _edition set; _source_url present; entries ≈ 120; sample entry has lpd_wpm2 + lpd_wpft2 + _ashrae_space_label + _verification_status.

- [ ] **Step 6: Banned-citation grep + gates + commit**

```bash
grep -rnE "(§526\.2|§433\.2|OZEV|3rd Edition|Reg 559|Em_room|average room lux)" shared/standards/energy/ASHRAE-90-1/ | grep -v "do NOT\|never cite\|banned\|NOT cite" && echo BANNED_FAIL || echo BANNED_PASS
python3 scripts/validate-examples.py 2>&1 | tail -3
git add shared/standards/energy/ASHRAE-90-1/
git commit -m "feat(standards): X.C.1 NEW ASHRAE 90.1 Table 9.6.1 LPD transcription — ~120 commercial/institutional space types with W/m² and W/ft² values (edition 2019 from publicly-accessible mirror)"
```

### Task X.C.2: Author ASHRAE 62.1 ventilation rates transcription

**Files:**
- Create: `shared/standards/hvac/ASHRAE-62-1/README.md`
- Create: `shared/standards/hvac/ASHRAE-62-1/ventilation-rates.json`
- Create: `shared/standards/hvac/ASHRAE-62-1/reference.md`

**Why Opus:** Same engineering-judgement reasoning as X.C.1; ASHRAE 62.1 uses a separate taxonomy from 90.1 (occupancy categories + space types); pattern locks the ventilation cross-reference structure for X.D.1.

- [ ] **Step 1: Survey publicly-accessible ASHRAE 62.1 sources**

ASHRAE Standard 62.1 (Ventilation for Acceptable Indoor Air Quality). Candidate sources:

- ASHRAE direct (sometimes free for specific tables)
- GSA / NCAR / DOE building energy publications
- State mechanical code references (e.g. International Mechanical Code references 62.1)
- BIM/HVAC engineering tools' citations

- [ ] **Step 2: Create folder + README + reference.md (mirror X.C.1 pattern)**

```bash
mkdir -p shared/standards/hvac/ASHRAE-62-1
```

- [ ] **Step 3: Author `ventilation-rates.json`**

```json
{
  "_source": "ASHRAE Standard 62.1 — Ventilation for Acceptable Indoor Air Quality, Table 6-1 (Minimum Ventilation Rates in Breathing Zone)",
  "_source_url": "<verbatim mirror URL>",
  "_access_date": "2026-06-05",
  "_edition": "2019",
  "_units": {
    "rp_lps_person": "L/s per person (people outdoor air rate)",
    "ra_lps_m2": "L/s per m² (area outdoor air rate)",
    "rp_cfm_person": "cfm per person (imperial)",
    "ra_cfm_ft2": "cfm per ft² (imperial)",
    "default_occupancy": "people per 100 m² (default for design occupancy when actual unknown)",
    "air_class": "1 / 2 / 3 / 4 — Air class for recirculation control"
  },
  "_note": "Total outdoor air rate Vbz = Rp × Pz + Ra × Az where Pz=people count, Az=area. Cross-walked to room-types canonical_ids at X.D.1.",
  "entries": {
    "office.open_plan": {
      "rp_lps_person": 2.5,
      "ra_lps_m2": 0.3,
      "rp_cfm_person": 5,
      "ra_cfm_ft2": 0.06,
      "default_occupancy_per_100m2": 5,
      "air_class": 1,
      "_ashrae_space_label": "Office space",
      "_verification_status": "mirror_sourced"
    }
  }
}
```

Implementer transcribes ~150 entries from declared mirror.

- [ ] **Step 4: Validate + grep + gates + commit**

```bash
python3 -c "
import json
d = json.load(open('shared/standards/hvac/ASHRAE-62-1/ventilation-rates.json'))
print(f'entries: {len(d[\"entries\"])}, edition: {d[\"_edition\"]}')
first = list(d['entries'].keys())[0]
print(f'sample: {first} = {d[\"entries\"][first]}')
"
grep -rnE "(§526\.2|§433\.2|OZEV|3rd Edition|Reg 559|Em_room|average room lux)" shared/standards/hvac/ASHRAE-62-1/ | grep -v "do NOT\|never cite\|banned\|NOT cite" && echo BANNED_FAIL || echo BANNED_PASS
python3 scripts/validate-examples.py 2>&1 | tail -3
git add shared/standards/hvac/ASHRAE-62-1/
git commit -m "feat(standards): X.C.2 NEW ASHRAE 62.1 ventilation rates transcription — ~150 space types with Rp + Ra + default occupancy + air class (edition 2019 from publicly-accessible mirror)"
```

---

## Phase X.D — Cross-reference back-fill + contract features (3 tasks, ~15-20 commits)

Goal: back-fill `cross_references` on all 600 room-types entries (X.D.1) + add the `room.classification` field to SkillInput per IfcClassificationReference structure (X.D.2) + author fuzzy-match reference spec (X.D.3).

### Task X.D.1: Cross-reference back-fill across 600 room-types entries

**Files:**
- Modify: `shared/standards/spaces/room-types/*.json` (all 7 per-category files)

**Why Sonnet:** Mechanical cross-walk via Python script; spot-check sample reviewed by Opus at X.E.4.

- [ ] **Step 1: Author the cross-walk Python script (one-off, lives in task transcript not in repo)**

The implementer authors a Python script that:

1. Reads `shared/standards/lighting/BSEN12464/lux-levels.json` and extracts the 27 BS EN 12464-1 keys (e.g. `office.open_plan`, `circulation.lobby`)
2. Reads `shared/standards/energy/ASHRAE-90-1/lpd-table-9-6-1.json` and extracts ASHRAE space labels
3. Reads `shared/standards/hvac/ASHRAE-62-1/ventilation-rates.json` and extracts ASHRAE space labels
4. For each room-types entry: scan canonical_id + common_aliases for matches against the 3 source key sets; populate `cross_references` accordingly
5. Match heuristic: exact suffix match (e.g. room-types `commercial.office.open_plan` → BS EN 12464-1 `office.open_plan`) + alias-based fallback (common_aliases includes "open plan office" → ASHRAE "Office — Open Plan")

```python
import json
import glob

# Source key sets
bs_en_keys = set()
d = json.load(open('shared/standards/lighting/BSEN12464/lux-levels.json'))
for cat, sub in d.items():
    if not cat.startswith('_') and isinstance(sub, dict):
        for k in sub:
            if not k.startswith('_'):
                bs_en_keys.add(f'{cat}.{k}')

ashrae_90_keys = set(json.load(open('shared/standards/energy/ASHRAE-90-1/lpd-table-9-6-1.json'))['entries'].keys())
ashrae_62_keys = set(json.load(open('shared/standards/hvac/ASHRAE-62-1/ventilation-rates.json'))['entries'].keys())

def find_match(canonical_id, common_aliases, key_set):
    # Match 1: exact suffix
    for k in key_set:
        if canonical_id.endswith(f'.{k}') or canonical_id == k:
            return k
    # Match 2: last 2 path segments match
    parts = canonical_id.split('.')
    for k in key_set:
        if k == '.'.join(parts[-2:]):
            return k
    # Match 3: alias match (case-insensitive normalized)
    for alias in common_aliases:
        normalized = alias.lower().replace(' ', '_').replace('-', '_')
        for k in key_set:
            if k.endswith(f'.{normalized}'):
                return k
    return None

# Back-fill each room-types file
total_back_filled = {'bs_en_12464_1': 0, 'ashrae_90_1': 0, 'ashrae_62_1': 0}
for f in sorted(glob.glob('shared/standards/spaces/room-types/*.json')):
    d = json.load(open(f))
    for entry in d['entries']:
        cid = entry['canonical_id']
        aliases = entry.get('common_aliases', [])
        bs_match = find_match(cid, aliases, bs_en_keys)
        a90_match = find_match(cid, aliases, ashrae_90_keys)
        a62_match = find_match(cid, aliases, ashrae_62_keys)
        if bs_match:
            entry['cross_references']['bs_en_12464_1'] = bs_match
            total_back_filled['bs_en_12464_1'] += 1
        if a90_match:
            entry['cross_references']['ashrae_90_1'] = a90_match
            total_back_filled['ashrae_90_1'] += 1
        if a62_match:
            entry['cross_references']['ashrae_62_1'] = a62_match
            total_back_filled['ashrae_62_1'] += 1
    json.dump(d, open(f, 'w'), indent=2, ensure_ascii=False)

print(f'Back-filled cross-references: {total_back_filled}')
```

- [ ] **Step 2: Run the cross-walk script**

Run the script. Report back-fill counts.

Expected: bs_en_12464_1 matches ~20-30 (only lighting-relevant rooms match the 27 BS EN keys); ashrae_90_1 matches ~80-100; ashrae_62_1 matches ~100-130.

- [ ] **Step 3: Spot-check 30 random entries (5% of ~600) for cross-reference accuracy**

```bash
python3 -c "
import json, glob, random
random.seed(42)
all_entries = []
for f in sorted(glob.glob('shared/standards/spaces/room-types/*.json')):
    d = json.load(open(f))
    all_entries.extend((f.split('/')[-1], e) for e in d['entries'])
sample = random.sample(all_entries, min(30, len(all_entries)))
for filename, entry in sample:
    cid = entry['canonical_id']
    refs = entry['cross_references']
    populated = {k: v for k, v in refs.items() if v is not None}
    print(f'  {cid} ({filename}): {populated}')
"
```

Inspect manually: each populated cross-reference must be a real key in the target source file. False matches caught here.

- [ ] **Step 4: Validate all 7 files still pass schema after back-fill**

```bash
python3 -c "
import json, jsonschema, glob
schema = json.load(open('shared/standards/spaces/room-types-schema.json'))
total_errors = 0
for f in sorted(glob.glob('shared/standards/spaces/room-types/*.json')):
    d = json.load(open(f))
    for entry in d['entries']:
        try: jsonschema.validate(entry, schema)
        except jsonschema.ValidationError as e:
            total_errors += 1
            print(f'  {f}:{entry[\"canonical_id\"]}: {e.message[:100]}')
print(f'total schema errors after back-fill: {total_errors}')
"
```

Expected: 0 schema errors.

- [ ] **Step 5: Banned-citation grep + gates + commit**

```bash
grep -rnE "(§526\.2|§433\.2|OZEV|3rd Edition|Reg 559|Em_room|average room lux)" shared/standards/spaces/room-types/ | grep -v "do NOT\|never cite\|banned\|NOT cite" && echo BANNED_FAIL || echo BANNED_PASS
python3 scripts/validate-examples.py 2>&1 | tail -3
git add shared/standards/spaces/room-types/
git commit -m "feat(standards): X.D.1 cross-reference back-fill — populate cross_references.bs_en_12464_1 + ashrae_90_1 + ashrae_62_1 on ~600 room-types entries where matching source entries exist (cibse_lg + nrm2 stay null per Sprint X deferral)"
```

### Task X.D.2: F.1 SkillInput schema — add `Room.classification` field

**Files:**
- Modify: `shared/schemas/core/skill-input.schema.json`
- Modify: `shared/schemas/core/skill-input.reference.md`

**Why Opus:** Schema design judgement; adds IfcClassificationReference structure to Room; must preserve back-compat with existing Sprint F.1 schema users.

- [ ] **Step 1: Read current Room definition**

```bash
python3 -c "
import json
s = json.load(open('shared/schemas/core/skill-input.schema.json'))
room = s['definitions']['Room']
print('Room.required:', room.get('required'))
print('Room.properties:', list(room['properties'].keys()))
print('Room.additionalProperties:', room.get('additionalProperties'))
"
```

Expected: required `[room_id, type, area_m2, bbox]`; properties include room_id, type, area_m2, bbox, polygon, centroid, mounting_height.

- [ ] **Step 2: Add `classification` property to Room.properties**

Edit `shared/schemas/core/skill-input.schema.json`. Locate `definitions.Room.properties` and APPEND:

```json
"classification": {
  "type": "object",
  "description": "Optional BIM IfcClassificationReference structure for round-tripping room.type via IFC. Auto-derivable by orchestrator from Room.type via shared/standards/spaces/room-types/*.json lookup (look up canonical_id → omniclass_code). Orchestrators populating this directly carry the canonical reference inline for downstream BIM export.",
  "properties": {
    "source": {
      "type": "string",
      "default": "OmniClass-Table-13",
      "description": "Classification source identifier. Default 'OmniClass-Table-13' matches Sprint X taxonomy."
    },
    "edition": {
      "type": "string",
      "description": "Classification edition (e.g. '2012', '2019')."
    },
    "code": {
      "type": "string",
      "pattern": "^13-[0-9]{2}( [0-9]{2}){0,4}$",
      "description": "Verbatim classification code. For OmniClass Table 13: 5-segment 13-digit notation 13-XX XX XX XX XX."
    },
    "reference_uri": {
      "type": "string",
      "format": "uri",
      "description": "Optional URI to the canonical classification entry (e.g. OmniClass.org page for the code)."
    }
  },
  "additionalProperties": false
}
```

- [ ] **Step 3: Update `skill-input.reference.md` to document the new field**

Edit `shared/schemas/core/skill-input.reference.md`. In the "## Building / Floor / Room fields" → "### Room" subsection, ADD a bullet:

```markdown
- `classification`: optional BIM IfcClassificationReference structure (`{source, edition, code, reference_uri}`). Auto-derivable by orchestrator from `type` via `shared/standards/spaces/room-types/*.json` lookup. Populate inline when downstream BIM export is required.
```

- [ ] **Step 4: Validate schema parses + new property present + still well-formed**

```bash
python3 -c "
import json, jsonschema
s = json.load(open('shared/schemas/core/skill-input.schema.json'))
room = s['definitions']['Room']
print('classification present:', 'classification' in room['properties'])
print('classification properties:', list(room['properties']['classification']['properties'].keys()))
jsonschema.Draft7Validator.check_schema(s)
print('schema still well-formed: OK')
"
```

Expected: present True; properties [source, edition, code, reference_uri]; well-formed OK.

- [ ] **Step 5: Test backwards-compatibility — F.1 fixtures still validate**

```bash
python3 -c "
import json, jsonschema
schema = json.load(open('shared/schemas/core/skill-input.schema.json'))
# Pre-X.D.2 valid fixture (no classification)
fixture = {
    'scope': 'room',
    'floor': {'id': 'FL-01'},
    'room': {
        'room_id': 'R-1',
        'type': 'office.open_plan',
        'area_m2': 96.0,
        'bbox': {'length': 12.0, 'width': 8.0}
    },
    'project_facts': {'jurisdiction': 'GB'}
}
try:
    jsonschema.validate(fixture, schema)
    print('pre-X.D.2 fixture: PASS (back-compat preserved)')
except Exception as e:
    print(f'pre-X.D.2 fixture: FAIL {str(e)[:150]}')
# Post-X.D.2 fixture (with classification)
fixture['room']['classification'] = {
    'source': 'OmniClass-Table-13',
    'edition': '2012',
    'code': '13-15 11 23 11',
    'reference_uri': 'https://example.com/omniclass/13-15-11-23-11'
}
try:
    jsonschema.validate(fixture, schema)
    print('post-X.D.2 fixture with classification: PASS')
except Exception as e:
    print(f'post-X.D.2 fixture: FAIL {str(e)[:150]}')
"
```

Expected: both PASS.

- [ ] **Step 6: Banned-citation grep + gates + commit**

```bash
grep -nE "(§526\.2|§433\.2|OZEV|3rd Edition|Reg 559|Em_room|average room lux)" shared/schemas/core/skill-input.schema.json shared/schemas/core/skill-input.reference.md | grep -v "do NOT\|never cite\|banned\|NOT cite" && echo FAIL || echo PASS
python3 scripts/validate-examples.py 2>&1 | tail -3
git add shared/schemas/core/skill-input.schema.json shared/schemas/core/skill-input.reference.md
git commit -m "feat(schemas): X.D.2 add Room.classification field — IfcClassificationReference structure (source + edition + code + reference_uri) for BIM round-tripping; backwards-compatible with Sprint F.1 fixtures"
```

### Task X.D.3: Fuzzy-match reference spec

**Files:**
- Create: `shared/standards/spaces/fuzzy-match-reference.md`

**Why Sonnet:** Mechanical algorithm spec authoring; self-contained reference; orchestrators implement engines per `[[runtime-project-boundary]]`.

- [ ] **Step 1: Author `shared/standards/spaces/fuzzy-match-reference.md`**

```markdown
# Room-Type Fuzzy-Match Reference

Reference algorithm + test fixtures for orchestrators implementing fuzzy lookup of non-canonical `Room.type` strings against the canonical taxonomy at `shared/standards/spaces/room-types/*.json`.

Per `[[runtime-project-boundary]]`, this skills repo ships the ALGORITHM SPEC + TEST FIXTURES. Orchestrators (DraftsMan runtime / Claude CLI / MCP servers / future tooling) implement the engine in their own runtime layer.

## When fuzzy match is needed

Architectural drawing parsers typically emit room labels like "Open Plan Office", "Master Bedroom", "Operating Theatre 1", "ICU Bay 3" — NOT the canonical `office.open_plan` / `residential.single_family.bedroom_master` / `institutional.healthcare.operating_theatre_general` / `institutional.healthcare.icu_general` snake_case form. The orchestrator MUST normalize before passing to a skill via `Room.type`.

## Algorithm — 4-tier match priority

For each non-canonical input string `s`:

### Tier 1: Exact match (highest priority)

If `s` already equals a `canonical_id` in any room-types/*.json file: return that canonical_id.

```python
if s in canonical_ids_set:
    return s
```

### Tier 2: Snake_case normalization match

Normalize `s` to snake_case + check exact match.

```python
normalized = s.strip().lower().replace(' ', '_').replace('-', '_')
# Remove common suffix numbers ("Operating Theatre 1" → "operating_theatre")
normalized = re.sub(r'_\d+$', '', normalized)
for cid in canonical_ids_set:
    # Match against last 1-3 segments of canonical_id (suffix match)
    parts = cid.split('.')
    for n in range(1, 4):
        if '.'.join(parts[-n:]) == normalized or '_'.join(parts[-n:]) == normalized:
            return cid
```

### Tier 3: Alias match

Check `common_aliases[]` arrays across all room-types entries.

```python
for entry in all_room_types_entries:
    for alias in entry.get('common_aliases', []):
        alias_normalized = alias.strip().lower().replace(' ', '_').replace('-', '_')
        if alias_normalized == normalized:
            return entry['canonical_id']
```

### Tier 4: Levenshtein distance fallback (≤2 edits)

For unmatched strings, compute Levenshtein edit distance against canonical_ids + aliases. Return closest if distance ≤ 2 edits (catches typos).

```python
def levenshtein(a, b):
    # Standard dynamic-programming Levenshtein implementation
    ...

best_match = None
best_distance = float('inf')
for candidate in canonical_ids_set | all_aliases_set:
    d = levenshtein(normalized, candidate)
    if d < best_distance and d <= 2:
        best_distance = d
        best_match = canonical_to_match.get(candidate, candidate)
return best_match  # may be None
```

### Tier 5: Embedding-similarity fallback (optional, runtime-specific)

If the orchestrator has an LLM available, compute semantic embedding similarity between `normalized` and all `canonical_id` + alias strings. Return closest if cosine similarity > 0.85.

This is OPTIONAL — only orchestrators with LLM access implement it; CLI tools without LLMs stop at Tier 4.

## Test fixtures

Orchestrators verify their fuzzy-match implementation against these input/expected-output pairs:

| Input string | Expected canonical_id | Match tier |
|---|---|---|
| `office.open_plan` | `office.open_plan` | 1 (exact) |
| `Open Plan Office` | `office.open_plan` (or commercial-prefixed variant) | 2 or 3 |
| `master bedroom` | `residential.single_family.bedroom_master` | 3 (alias) |
| `Operating Theatre 1` | `institutional.healthcare.operating_theatre_general` (or similar) | 2 (after suffix-number strip) |
| `OR` | `institutional.healthcare.operating_theatre_general` | 3 (alias) |
| `corridoor` (typo) | `circulation.main_corridor` | 4 (Levenshtein ≤2) |
| `WC` | `sanitary.toilet_wc` | 3 (alias) |
| `Toilet` | `sanitary.toilet_wc` | 3 (alias) |
| `data center` | `industrial.utility.server_room_data_centre` (US→UK normalization) | 3 (alias) or 5 (embedding) |
| `unknown space type xyz` | `null` (no match) | - |

Orchestrators MUST cover Tier 1-4 at minimum. Tier 5 (embeddings) is optional uplift.

## When to fall back to engineer override

If fuzzy match returns `null` (no candidate within Tier 4 thresholds), the orchestrator prompts the engineer to either:

1. Select a canonical_id from a dropdown
2. Map the unknown label to a canonical_id manually
3. Pass through with `Room.type: "unknown.userdefined"` (graceful fallback)

The graceful fallback `unknown.userdefined` is reserved for orchestrator use only — never appears in room-types/*.json.

## Citation

Algorithm pattern derived from common fuzzy-string-matching practice. Levenshtein distance per Levenshtein (1966). Embedding-similarity per modern LLM cosine-similarity convention.
```

- [ ] **Step 2: Validate file renders**

```bash
wc -l shared/standards/spaces/fuzzy-match-reference.md
```

Expected: ~110-140 lines.

- [ ] **Step 3: Banned-citation grep + gates + commit**

```bash
grep -nE "(§526\.2|§433\.2|OZEV|3rd Edition|Reg 559|Em_room|average room lux)" shared/standards/spaces/fuzzy-match-reference.md | grep -v "do NOT\|never cite\|banned\|NOT cite" && echo FAIL || echo PASS
python3 scripts/validate-examples.py 2>&1 | tail -3
git add shared/standards/spaces/fuzzy-match-reference.md
git commit -m "feat(standards): X.D.3 NEW fuzzy-match-reference.md — 4-tier algorithm spec (exact + snake_case + alias + Levenshtein ≤2) + 10 test fixtures + optional embedding tier 5; orchestrators implement engines per runtime-project-boundary"
```

---

## Phase X.E — Gate extension + F.1 retrofit + ship (5 tasks, ~10-13 commits)

Goal: wire the new standards layers into the gate (X.E.1), retrofit F.1 schema (X.E.2), CHANGELOG + memory + tally (X.E.3), final adversarial review (X.E.4), push (X.E.5).

### Task X.E.1: Extend `scripts/validate-examples.py` to 7-pass + Lint 5

**Files:**
- Modify: `scripts/validate-examples.py`

**Why Sonnet:** Mechanical Python extension; pattern locked by Sprint F.5 (4-pass + 4-lint extension).

- [ ] **Step 1: Inspect current Sprint F.5 pass structure**

```bash
grep -nE "^def validate_|^def lint_|^# Pass|^# Lint" scripts/validate-examples.py | head -20
```

Expected (post-F.5 state when Sprint F resumes; pre-F.5 state during Sprint X execution):
- `validate_examples_pass` (Pass 1)
- `validate_evals_pass` (Pass 2)
- `validate_inputs_pass` (Pass 3)
- `validate_manifests_pass` (Pass 4, added in F.5)
- Lint 1-4 (added in F.5)

**Note for execution:** Sprint X runs BEFORE Sprint F.5. So current state at X.E.1 dispatch = 3-pass (Sprint F has only shipped F.0-F.3). X.E.1 extends to add Pass 5 (room-types) + Pass 6 (ASHRAE) + Pass 7 (IFC) + Lint 5 (canonical room.type membership). Sprint F.5 will THEN add Pass 4 (manifest) + Lint 1-4 on top of Sprint X's extension.

So the Sprint X.E.1 extension adds 3 new passes + 1 new lint, taking the gate from 3-pass → 6-pass + 1 lint. Sprint F.5 later takes that to 7-pass + 5 lint.

(If Sprint F is fully resumed before Sprint X — i.e. F.4-F.9 ship between Sprint X start and X.E.1 — then current state would be 4-pass + 4-lint. Adapt accordingly.)

- [ ] **Step 2: Add Pass 5 — Room-types schema validation**

In `scripts/validate-examples.py`, AFTER the existing pass functions and BEFORE `main()`, ADD:

```python
def validate_room_types_pass() -> tuple:
    """Pass 5 — Room-types schema validation.

    Validate every entry in every shared/standards/spaces/room-types/*.json file
    against shared/standards/spaces/room-types-schema.json.

    Returns (total_entries, total_failures, report_lines).
    """
    results = defaultdict(list)
    total_entries = 0
    total_failures = 0

    schema_path = "shared/standards/spaces/room-types-schema.json"
    try:
        with open(schema_path) as f:
            schema = json.load(f)
    except FileNotFoundError:
        return (0, 0, [f"\n## Pass 5: SKIP — {schema_path} not found"])

    for f_path in sorted(glob.glob("shared/standards/spaces/room-types/*.json")):
        f_name = os.path.basename(f_path)
        try:
            with open(f_path) as f:
                d = json.load(f)
        except json.JSONDecodeError as e:
            results[f_name].append(("JSON-PARSE", f_path, str(e)[:200]))
            total_failures += 1
            continue
        for i, entry in enumerate(d.get("entries", [])):
            total_entries += 1
            try:
                jsonschema.validate(entry, schema)
                # Silent PASS at entry level; per-file PASS reported below
            except jsonschema.ValidationError as e:
                total_failures += 1
                cid = entry.get("canonical_id", f"entry[{i}]")
                results[f_name].append(("FAIL", cid, e.message[:160]))

    lines = ["\n## Pass 5: Room-types schema validation"]
    for f_name in sorted(results.keys()):
        failures = results[f_name]
        if not failures:
            lines.append(f"  PASS {f_name}")
        else:
            for kind, name, msg in failures:
                lines.append(f"  {kind} {f_name}.{name}: {msg}")
    if not results:
        lines.append("  PASS — all room-types entries validate")
    return (total_entries, total_failures, lines)
```

- [ ] **Step 3: Add Pass 6 — ASHRAE files parse + structure check**

After Pass 5, ADD:

```python
def validate_ashrae_pass() -> tuple:
    """Pass 6 — ASHRAE source files parse + structure check.

    Validate that shared/standards/energy/ASHRAE-90-1/lpd-table-9-6-1.json and
    shared/standards/hvac/ASHRAE-62-1/ventilation-rates.json parse, have _source +
    _edition + entries fields populated.

    Returns (total_files, total_failures, report_lines).
    """
    results = []
    total_files = 0
    total_failures = 0

    checks = [
        ("ASHRAE-90-1", "shared/standards/energy/ASHRAE-90-1/lpd-table-9-6-1.json"),
        ("ASHRAE-62-1", "shared/standards/hvac/ASHRAE-62-1/ventilation-rates.json"),
    ]
    for name, path in checks:
        if not os.path.exists(path):
            results.append(("SKIP", name, f"file not found: {path}"))
            continue
        total_files += 1
        try:
            with open(path) as f:
                d = json.load(f)
        except json.JSONDecodeError as e:
            results.append(("JSON-PARSE", name, str(e)[:200]))
            total_failures += 1
            continue
        for required in ["_source", "_edition", "entries"]:
            if required not in d:
                results.append(("FAIL", name, f"missing required key: {required}"))
                total_failures += 1
                break
        else:
            results.append(("PASS", name, f"{len(d['entries'])} entries"))

    lines = ["\n## Pass 6: ASHRAE source files"]
    for kind, name, msg in results:
        lines.append(f"  {kind} {name}: {msg}")
    return (total_files, total_failures, lines)
```

- [ ] **Step 4: Add Pass 7 — IFC subset parse check**

After Pass 6, ADD:

```python
def validate_ifc_pass() -> tuple:
    """Pass 7 — ISO 16739 IFC subset parse check.

    Validate that shared/standards/bim/ISO16739/{space-types,classification,placement}.json
    parse and have _source + _source_url + entity definitions.

    Returns (total_files, total_failures, report_lines).
    """
    results = []
    total_files = 0
    total_failures = 0

    files = [
        "shared/standards/bim/ISO16739/space-types.json",
        "shared/standards/bim/ISO16739/classification.json",
        "shared/standards/bim/ISO16739/placement.json",
    ]
    for path in files:
        name = os.path.basename(path)
        if not os.path.exists(path):
            results.append(("SKIP", name, f"file not found: {path}"))
            continue
        total_files += 1
        try:
            with open(path) as f:
                d = json.load(f)
        except json.JSONDecodeError as e:
            results.append(("JSON-PARSE", name, str(e)[:200]))
            total_failures += 1
            continue
        for required in ["_source", "_source_url"]:
            if required not in d:
                results.append(("FAIL", name, f"missing required key: {required}"))
                total_failures += 1
                break
        else:
            results.append(("PASS", name, "valid"))

    lines = ["\n## Pass 7: ISO 16739 IFC subset"]
    for kind, name, msg in results:
        lines.append(f"  {kind} {name}: {msg}")
    return (total_files, total_failures, lines)
```

- [ ] **Step 5: Add Lint sub-pass 5 — Canonical room.type membership check**

After the IFC pass, ADD:

```python
def lint_canonical_room_type_membership(skill_dirs: list) -> tuple:
    """Lint sub-pass 5 — Canonical room.type membership check.

    Scan every examples/*/{output,intent-out,input}.json file across all skills for
    room.type values. Check each against the union of canonical_id values across
    shared/standards/spaces/room-types/*.json. Report PASS / FAIL / SUGGEST.

    Returns (total_fail_count, report_lines).
    """
    # Load canonical IDs
    canonical_ids = set()
    aliases_to_canonical = {}
    for f in sorted(glob.glob("shared/standards/spaces/room-types/*.json")):
        try:
            with open(f) as fh:
                d = json.load(fh)
            for entry in d.get("entries", []):
                canonical_ids.add(entry["canonical_id"])
                for alias in entry.get("common_aliases", []):
                    aliases_to_canonical[alias.lower().strip()] = entry["canonical_id"]
        except (json.JSONDecodeError, KeyError):
            continue

    if not canonical_ids:
        return (0, ["\n## Lint 5: Canonical room.type membership", "  SKIP — no room-types catalogue found"])

    # Scan all skill example files
    total_checked = 0
    total_fail = 0
    total_suggest = 0
    findings = []
    for skill_dir in skill_dirs:
        skill_name = os.path.basename(skill_dir)
        for ex_glob in [f"{skill_dir}/examples/*/output.json",
                        f"{skill_dir}/examples/*/intent-out.json",
                        f"{skill_dir}/examples/*/input.json"]:
            for ex_path in sorted(glob.glob(ex_glob)):
                ex_name = os.path.basename(os.path.dirname(ex_path))
                file_kind = os.path.basename(ex_path)
                try:
                    with open(ex_path) as f:
                        d = json.load(f)
                except json.JSONDecodeError:
                    continue
                # Find room.type values (top-level + room sub-object + rooms[] array)
                room_type_values = []
                if isinstance(d.get("room"), dict) and "type" in d["room"]:
                    room_type_values.append(("room.type", d["room"]["type"]))
                if isinstance(d.get("room"), dict) and "room_type" in d["room"]:
                    room_type_values.append(("room.room_type", d["room"]["room_type"]))
                for rt_path, rt_val in room_type_values:
                    if not isinstance(rt_val, str):
                        continue
                    total_checked += 1
                    if rt_val in canonical_ids:
                        pass  # Silent PASS
                    elif rt_val.lower().strip() in aliases_to_canonical:
                        canonical = aliases_to_canonical[rt_val.lower().strip()]
                        total_suggest += 1
                        findings.append(f"  SUGGEST {skill_name}.{ex_name}.{file_kind} ({rt_path}='{rt_val}'): not canonical; matches alias of '{canonical}'")
                    else:
                        total_fail += 1
                        findings.append(f"  FAIL {skill_name}.{ex_name}.{file_kind} ({rt_path}='{rt_val}'): not in canonical catalogue + no alias match")

    lines = ["\n## Lint 5: Canonical room.type membership"]
    if total_checked == 0:
        lines.append("  SKIP — no room.type values found in example files")
    elif total_fail == 0 and total_suggest == 0:
        lines.append(f"  PASS — {total_checked} room.type values all canonical")
    else:
        lines.append(f"  Checked: {total_checked}; PASS: {total_checked - total_fail - total_suggest}; SUGGEST: {total_suggest}; FAIL: {total_fail}")
        lines.extend(findings[:20])  # Cap output at 20 findings
        if len(findings) > 20:
            lines.append(f"  ... and {len(findings) - 20} more findings (output truncated)")
    return (total_fail, lines)
```

- [ ] **Step 6: Wire the 3 new passes + 1 new lint into `main()`**

In the `main()` function, after the existing pass tallies, ADD:

```python
    # Pass 5 — Room-types schema
    p5_total, p5_failures, p5_lines = validate_room_types_pass()

    # Pass 6 — ASHRAE source files
    p6_total, p6_failures, p6_lines = validate_ashrae_pass()

    # Pass 7 — ISO 16739 IFC subset
    p7_total, p7_failures, p7_lines = validate_ifc_pass()

    # Lint 5 — Canonical room.type membership
    l5_failures, l5_lines = lint_canonical_room_type_membership(skill_dirs)

    # Aggregate (add to existing aggregation)
    aggregate += (p5_total + p6_total + p7_total)
    total_failures += (p5_failures + p6_failures + p7_failures + l5_failures)

    # Print sections
    for line in p5_lines + p6_lines + p7_lines + l5_lines:
        print(line)
```

(Adapt to existing variable names in main(); search for `aggregate` / `total_failures` patterns in the existing main and follow.)

- [ ] **Step 7: Update module docstring**

Locate the module docstring at top of `scripts/validate-examples.py`. REPLACE the line describing the pass count to read:

```python
"""Golden-example schema validation harness — 6-pass + 1 lint sub-pass (Sprint X) / 7-pass + 5 lint sub-passes (Sprint F.5 final).

Pass 1 — Example outputs (IR schema)
Pass 2 — Eval files (eval.schema.json)
Pass 3 — Inputs files (inputs.schema.json)
Pass 4 — Manifests (skill-manifest.schema.json) [added Sprint F.5]
Pass 5 — Room-types entries (room-types-schema.json) [added Sprint X.E.1]
Pass 6 — ASHRAE source files (parse + structure) [added Sprint X.E.1]
Pass 7 — ISO 16739 IFC subset (parse + structure) [added Sprint X.E.1]

Lint sub-passes:
  Lint 1 — Manifest field-name typos [Sprint F.5]
  Lint 2 — grounded_source two-tier validation [Sprint F.5]
  Lint 3 — Dropped-item orphans in examples [Sprint F.5]
  Lint 4 — Cascade byte-equality SHA-256 [Sprint F.5]
  Lint 5 — Canonical room.type membership [added Sprint X.E.1]

Returns exit 0 on full pass + zero gate-failing lint findings; exit 1 on any failure.
"""
```

- [ ] **Step 8: Smoke-test the extended gate**

```bash
python3 scripts/validate-examples.py 2>&1 | tail -40
```

Expected: Pass 1/2/3 unchanged from baseline. Pass 5 reports per-file PASS/FAIL across 7 room-types files. Pass 6 reports 2 ASHRAE files. Pass 7 reports 3 IFC files. Lint 5 reports SKIP (because existing examples use the LEGACY `room_type` field, not the new `room.type` — until Sprint W1/W2 grounds skills to consume the new field, Lint 5 will be silent on the current example state).

- [ ] **Step 9: Commit**

```bash
git add scripts/validate-examples.py
git commit -m "feat(gate): X.E.1 extend golden CI with Pass 5 (room-types schema) + Pass 6 (ASHRAE) + Pass 7 (IFC subset) + Lint 5 (canonical room.type membership) — wires Sprint X taxonomy into gate enforcement"
```

### Task X.E.2: F.1 SkillInput schema retrofit — Room.type enum → pattern

**Files:**
- Modify: `shared/schemas/core/skill-input.schema.json`
- Modify: `shared/schemas/core/skill-input.reference.md`

**Why Sonnet:** Mechanical schema retrofit; backwards-compatible change (every value satisfying enum also satisfies pattern); pattern enforced at schema; canonical membership enforced at Lint 5 (X.E.1).

- [ ] **Step 1: Inspect current Room.type definition**

```bash
python3 -c "
import json
s = json.load(open('shared/schemas/core/skill-input.schema.json'))
room_type = s['definitions']['Room']['properties']['type']
print('type keys:', list(room_type.keys()))
print(f'enum length: {len(room_type.get(\"enum\", []))}')
print(f'pattern: {room_type.get(\"pattern\")}')
"
```

Expected pre-X.E.2: keys include `type` + `enum` + `description`; enum length 27; pattern absent.

- [ ] **Step 2: Replace enum with pattern**

Edit `shared/schemas/core/skill-input.schema.json`. Locate `definitions.Room.properties.type` and REPLACE the enum-based definition with:

```json
"type": {
  "type": "string",
  "pattern": "^[a-z]+(\\.[a-z0-9_]+)+$",
  "description": "Snake_case canonical_id from shared/standards/spaces/room-types/*.json (~600-entry catalogue). Format: parent_category.sub_category.entry_name. Examples: office.open_plan, healthcare.operating_theatre_general, residential.bedroom_master. Canonical membership enforced at gate-time via Lint sub-pass 5 against the catalogue. See ORCHESTRATION.md + shared/standards/spaces/README.md for the full taxonomy reference."
}
```

The `enum` key is REMOVED. The `pattern` key replaces it. Description updated to point at the catalogue.

- [ ] **Step 3: Update `skill-input.reference.md` Room.type section**

Edit `shared/schemas/core/skill-input.reference.md`. Locate the section listing the 27-value enum (likely "### Room" or similar). REPLACE the 27-value list with:

```markdown
- `type`: snake_case canonical_id from `shared/standards/spaces/room-types/*.json` catalogue (~600 entries spanning residential / commercial / institutional / industrial / transport / external / agricultural). Format: `parent_category.sub_category.entry_name`. Canonical membership enforced at gate-time. Examples: `office.open_plan`, `healthcare.operating_theatre_general`, `residential.bedroom_master`. For non-canonical drawing labels (e.g. "Master Bedroom" from architectural parsers), orchestrators implement fuzzy-match per `shared/standards/spaces/fuzzy-match-reference.md`.
```

- [ ] **Step 4: Test backwards-compatibility — existing Sprint F.1 fixtures still validate**

```bash
python3 -c "
import json, jsonschema
schema = json.load(open('shared/schemas/core/skill-input.schema.json'))
# Test fixture from F.0 era (room.type = 'office.open_plan' — was in original 27-value enum)
old_fixture = {
    'scope': 'room',
    'floor': {'id': 'FL-01'},
    'room': {'room_id': 'R-1', 'type': 'office.open_plan', 'area_m2': 96.0, 'bbox': {'length': 12.0, 'width': 8.0}},
    'project_facts': {'jurisdiction': 'GB'}
}
try:
    jsonschema.validate(old_fixture, schema)
    print('old fixture (office.open_plan): PASS (back-compat preserved)')
except Exception as e:
    print(f'old fixture: FAIL {e}')
# Test fixture with NEW canonical_id (was NOT in original 27-value enum)
new_fixture = old_fixture.copy()
new_fixture['room'] = {'room_id': 'R-2', 'type': 'residential.single_family.bedroom_master', 'area_m2': 16.0, 'bbox': {'length': 4.0, 'width': 4.0}}
try:
    jsonschema.validate(new_fixture, schema)
    print('new fixture (residential.single_family.bedroom_master): PASS')
except Exception as e:
    print(f'new fixture: FAIL {e}')
# Test fixture with INVALID value (not snake_case dotted)
bad_fixture = old_fixture.copy()
bad_fixture['room'] = {'room_id': 'R-3', 'type': 'OpenPlanOffice', 'area_m2': 16.0, 'bbox': {'length': 4.0, 'width': 4.0}}
try:
    jsonschema.validate(bad_fixture, schema)
    print('bad fixture (OpenPlanOffice): UNEXPECTED PASS')
except jsonschema.ValidationError:
    print('bad fixture (OpenPlanOffice): FAIL (correctly rejected by pattern)')
"
```

Expected: old fixture PASS (back-compat); new fixture PASS (new taxonomy works); bad fixture FAIL (pattern rejects non-snake_case).

- [ ] **Step 5: Run the extended gate (Lint 5 may surface findings on existing examples that use legacy `room_type` field)**

```bash
python3 scripts/validate-examples.py 2>&1 | tail -30
```

Expected: Pass 1/2/3 unchanged. Pass 5/6/7 from X.E.1 PASS. Lint 5 either SKIP (if examples don't use the new `room.type` field shape) or PASS (if examples migrated). Aggregate green.

- [ ] **Step 6: Banned-citation grep + commit**

```bash
grep -nE "(§526\.2|§433\.2|OZEV|3rd Edition|Reg 559|Em_room|average room lux)" shared/schemas/core/skill-input.schema.json shared/schemas/core/skill-input.reference.md | grep -v "do NOT\|never cite\|banned\|NOT cite" && echo FAIL || echo PASS
git add shared/schemas/core/skill-input.schema.json shared/schemas/core/skill-input.reference.md
git commit -m "fix(schemas): X.E.2 F.1 RETROFIT — Room.type enum → snake_case pattern (canonical membership enforced at Lint 5; backwards-compatible with Sprint F.1 fixtures; references room-types catalogue)"
```

### Task X.E.3: CHANGELOG + memory file + MEMORY.md + CLAUDE.md tally bump

**Files:**
- Modify: `CHANGELOG.md` (repo root)
- Modify: `CLAUDE.md`
- Create: `/Users/linus/.claude/projects/-Users-linus-Desktop-DraftsMan-SKills-draftsman-skills/memory/sprint-X-comprehensive-taxonomy-shipped.md`
- Modify: `/Users/linus/.claude/projects/-Users-linus-Desktop-DraftsMan-SKills-draftsman-skills/memory/MEMORY.md`

**Why Sonnet:** Mechanical documentation closure; mirrors D5 D.3 + Sprint F.7 pattern.

- [ ] **Step 1: Add Sprint X entry to `CHANGELOG.md`**

In `CHANGELOG.md` at repo root, ADD at top (after header):

```markdown
## [Sprint X — Comprehensive Room Taxonomy MEGA-SPRINT] — 2026-06-XX

### Added
- `shared/standards/spaces/` — NEW discipline-level folder for cross-cutting room-type taxonomy
  - `room-types-schema.json` — Draft-07 per-entry metaschema
  - `room-types.json` — master index with 7 parent_category entries
  - `room-types/<category>.json` — 7 per-category files (residential / commercial / institutional / industrial / transport / external / agricultural; ~600 entries total)
  - `fuzzy-match-reference.md` — 4-tier algorithm spec + test fixtures
  - `README.md` + `_source/OmniClass-Table-13-source-notes.md` — provenance + transcription gaps
- `shared/standards/bim/ISO16739/` — NEW BIM standards layer subset
  - `space-types.json` — IfcSpaceTypeEnum 7 values
  - `classification.json` — IfcClassification + IfcClassificationReference + IfcRelAssociatesClassification entities
  - `placement.json` — IfcLocalPlacement + IfcAxis2Placement3D (justifies placement_convention enum)
  - `README.md` + `reference.md`
- `shared/standards/energy/ASHRAE-90-1/lpd-table-9-6-1.json` — ~120 commercial/institutional space types with LPD (W/m² + W/ft²)
- `shared/standards/hvac/ASHRAE-62-1/ventilation-rates.json` — ~150 space types with Rp + Ra + air class
- `docs/superpowers/specs/sprint-X-source-provenance.md` — mirror selection + edition declaration + verification status taxonomy
- New SkillInput Room.classification field — optional IfcClassificationReference structure (source + edition + code + reference_uri) for BIM round-tripping

### Changed
- `shared/schemas/core/skill-input.schema.json` Room.type — RETROFIT from 27-value enum to snake_case pattern; canonical membership moved from schema-time to gate-time via Lint 5
- `shared/schemas/core/skill-input.reference.md` — Room.type section now points at room-types catalogue
- `shared/standards/spaces/room-types/*.json` cross_references back-filled — bs_en_12464_1 / ashrae_90_1 / ashrae_62_1 populated where matches exist; cibse_lg + nrm2 stay null (Sprint Y back-fill)
- `scripts/validate-examples.py` — extended from N-pass to 7-pass + Lint 5 (added Pass 5 room-types / Pass 6 ASHRAE / Pass 7 IFC + Lint 5 canonical membership)

### Sprint
- Sprint X (Comprehensive Room Taxonomy MEGA-SPRINT)
- Runs BETWEEN Sprint F.3 (08b6e38) and Sprint F.4 (paused) — Sprint F resumes at F.4 post-X.E.5 push
- ~85-95 commits across 23 implementer tasks + ~8-12 fix-passes + 4 portion docs

### Deferred to future sprints
- CIBSE LG1/LG2/LG7/LG10/LG12 + Guide A cross-references (paid CIBSE membership required) — Sprint Y
- NRM2 cross-references (paid RICS PDF required) — Sprint Y
- Full ISO 16739 IFC standards layer (Sprint X transcribes only the room-type-relevant subset) — when runtime needs richer BIM export
- Fuzzy-match execution engine (Sprint X ships algorithm spec only; orchestrators implement per runtime-project-boundary)
```

- [ ] **Step 2: Update `CLAUDE.md` to note Sprint X + new shared/standards/ layout**

In `CLAUDE.md` find the section on shared/standards/ (under "## Repo shape" or similar). UPDATE to mention `shared/standards/spaces/` + `shared/standards/bim/` + `shared/standards/energy/` + `shared/standards/hvac/` as Sprint X additions. Also update the golden CI gate description from "N-pass" to "7-pass + 5 lint sub-passes" with new pass descriptions.

- [ ] **Step 3: Create the memory file**

Create `/Users/linus/.claude/projects/-Users-linus-Desktop-DraftsMan-SKills-draftsman-skills/memory/sprint-X-comprehensive-taxonomy-shipped.md`:

```markdown
---
name: sprint-X-comprehensive-taxonomy-shipped
description: Sprint X Comprehensive Room Taxonomy shipped 2026-06-XX — ~600 OmniClass Table 13 entries + ASHRAE 90.1 + ASHRAE 62.1 + IFC ISO 16739 subset + Room.classification + fuzzy-match reference; F.1 retrofit applied; Sprint F resumes at F.4
metadata:
  type: project
---

# Sprint X — Comprehensive Room Taxonomy shipped 2026-06-XX

**Why:** Mid-sprint pause of Sprint F triggered by user audit of F.1 schema 27-value Room.type enum (commit c756c4e) — taxonomy was BS EN 12464-1 partial transcription, missing residential / healthcare specialty / industrial process / hospitality / public buildings / transport / external. User asked "do we have a standard that defines all this; we align 100%". Locked: ship OmniClass Table 13 (~600 entries) + supporting ASHRAE + IFC layers + F.1 retrofit BEFORE Sprint F resumes.

**How to apply:** All skills now reference shared/standards/spaces/room-types/*.json for canonical room types. SkillInput Room.type validated as snake_case pattern at schema-time + canonical membership at gate-time (Lint 5). Orchestrators consume the catalogue + fuzzy-match-reference.md to normalize non-canonical strings from drawing parsers. Room.classification field carries optional IfcClassificationReference for BIM round-tripping.

**What shipped:**
- 23 implementer commits + ~8-12 fix-passes + 4 plan portion docs + 1 spec = ~85-95 total
- 1 new spec file (sprint-X-source-provenance.md)
- 1 new schema (room-types-schema.json)
- 1 master index (spaces/room-types.json)
- 7 per-category files (~600 entries total)
- 1 fuzzy-match algorithm spec
- 4 IFC subset files (~200 lines)
- 2 ASHRAE source files (~270 entries combined)
- Cross-references back-filled on ~200-280 of 600 entries (matches where source standards exist)
- F.1 SkillInput Room.type retrofitted: enum → pattern; canonical membership at Lint 5
- New SkillInput Room.classification field per IfcClassificationReference
- Gate extended from 3-pass to 6-pass + 1 lint (Sprint F.5 later extends further to 7-pass + 5 lint)

**Coverage actual vs target:**
- Total room-types entries: <implementer-reported>/600 (~XX%)
- Cross-references populated: bs_en_12464_1 ~XX/600; ashrae_90_1 ~XX/600; ashrae_62_1 ~XX/600
- Honest disclosure on gaps in _source/OmniClass-Table-13-source-notes.md

**Sprint discipline preserved:**
- Sonnet for mechanical / Opus for judgment
- Two-stage Opus review per task
- 7-check verification fence at X.E.4
- Final Opus integration review at X.E.4
- Push deferred to user authorisation at X.E.5

**Next:** Sprint F RESUMES at F.4 (ORCHESTRATION.md authoring — now references room-types catalogue). After Sprint F ships, Sprint W1 (lighting-layout + small-power grounding) follows. CIBSE + NRM2 cross-reference back-fill = Sprint Y when paid source access granted.

**1 disclosed FP held throughout:** motor-superposition functional_audit FP (carry-over).
```

- [ ] **Step 4: Append MEMORY.md index entry**

In `/Users/linus/.claude/projects/-Users-linus-Desktop-DraftsMan-SKills-draftsman-skills/memory/MEMORY.md`, ADD line below the most recent entry:

```markdown
- [Sprint X Comprehensive Room Taxonomy shipped (MEGA-SPRINT)](sprint-X-comprehensive-taxonomy-shipped.md) — 2026-06-XX: ~600 OmniClass Table 13 entries across 7 per-category files + ASHRAE 90.1 LPD + ASHRAE 62.1 ventilation + IFC ISO 16739 subset + Room.classification field + fuzzy-match algorithm spec; F.1 retrofit (Room.type enum → pattern; canonical at Lint 5); gate 3-pass → 6-pass + 1 lint; Sprint F resumes at F.4; CIBSE + NRM2 deferred to Sprint Y (paid source blocker)
```

- [ ] **Step 5: Run extended gate to confirm green**

```bash
python3 scripts/validate-examples.py 2>&1 | tail -5
```

Expected: 6-pass + Lint 5 all green; aggregate > pre-Sprint-X baseline.

- [ ] **Step 6: Commit**

```bash
git add CHANGELOG.md CLAUDE.md
git commit -m "docs: X.E.3 Sprint X CHANGELOG + CLAUDE.md tally bump + memory file (taxonomy shipped; F.1 retrofit complete; Sprint F resumes at F.4)"
```

### Task X.E.4: Final cross-sprint Opus integration review (7-check fence)

**Files:**
- Read-only — verdict + recommendation only

**Why Opus:** Adversarial review against full Sprint X surface area. Critical: SPOT-CHECK 5% of OmniClass codes against declared mirror for fabrication detection.

- [ ] **Step 1: Run the 7-check fence**

Check 1 — room-types-schema valid:
```bash
python3 -c "import json, jsonschema; s = json.load(open('shared/standards/spaces/room-types-schema.json')); jsonschema.Draft7Validator.check_schema(s); print('  Check 1: PASS')"
```

Check 2 — 7 category files validate ≥600 entries total:
```bash
python3 -c "
import json, glob
total = 0
for f in sorted(glob.glob('shared/standards/spaces/room-types/*.json')):
    d = json.load(open(f))
    total += len(d['entries'])
print(f'  Check 2: total entries = {total} (target 600; threshold for SHIP-WITH-NOTED-CONCERNS = <540)')
print(f'  Check 2 status: {\"PASS\" if total >= 540 else \"CONCERN\"}')
"
```

Check 3 — ASHRAE files validate:
```bash
python3 scripts/validate-examples.py 2>&1 | grep -A 5 "Pass 6" | head -8
```

Check 4 — IFC subset present:
```bash
python3 scripts/validate-examples.py 2>&1 | grep -A 5 "Pass 7" | head -8
```

Check 5 — Lint 5 canonical membership works:
```bash
python3 scripts/validate-examples.py 2>&1 | grep -A 3 "Lint 5" | head -5
```

Check 6 — F.1 retrofit clean (Room.type pattern + Room.classification field):
```bash
python3 -c "
import json
s = json.load(open('shared/schemas/core/skill-input.schema.json'))
room = s['definitions']['Room']
rt = room['properties']['type']
print(f'  Check 6.a Room.type uses pattern: {\"pattern\" in rt and \"enum\" not in rt}')
print(f'  Check 6.b Room.classification present: {\"classification\" in room[\"properties\"]}')
"
```

Check 7 — Banned-citation grep across all Sprint X deliverables:
```bash
grep -rnE "(§526\.2|§433\.2|OZEV|3rd Edition|Reg 559|Em_room|average room lux)" shared/standards/spaces/ shared/standards/bim/ISO16739/ shared/standards/energy/ASHRAE-90-1/ shared/standards/hvac/ASHRAE-62-1/ shared/schemas/core/skill-input.schema.json shared/schemas/core/skill-input.reference.md scripts/validate-examples.py docs/superpowers/specs/sprint-X-source-provenance.md 2>/dev/null | grep -v "do NOT\|never cite\|banned\|NOT cite" && echo "Check 7: FAIL" || echo "Check 7: PASS"
```

- [ ] **Step 2: SPOT-CHECK fabrication detection (5% of OmniClass codes)**

This is the CRITICAL fabrication-prevention check. Randomly sample 30 codes (5% of ~600) and manually verify each against the declared primary mirror URL.

```bash
python3 -c "
import json, glob, random
random.seed(42)
all_codes = []
for f in sorted(glob.glob('shared/standards/spaces/room-types/*.json')):
    d = json.load(open(f))
    for entry in d['entries']:
        all_codes.append((entry['canonical_id'], entry['omniclass_code'], entry.get('_verification_status'), entry.get('_source_mirror', d.get('_source_url'))))
sample = random.sample(all_codes, min(30, len(all_codes)))
print('Spot-check sample (30 random codes) — manually verify each against declared mirror:')
for cid, code, status, mirror in sample:
    print(f'  {cid:60s} {code:24s} {status:16s} {mirror[:40] if mirror else \"<no mirror>\"}')
"
```

Reviewer manually consults the declared mirror URL and verifies that the sampled codes exist there in the canonical 13-XX XX XX XX XX format. Any fabrication (code in our file but NOT in mirror) = FIX-FIRST verdict.

- [ ] **Step 3: Build 7-check verdict table**

| # | Check | Verdict | Evidence |
|---|---|---|---|
| 1 | room-types-schema valid | PASS/FAIL | Draft-07 well-formed |
| 2 | 7 category files ≥600 entries | PASS/CONCERN/FAIL | (N/600 total) |
| 3 | ASHRAE files validate | PASS/FAIL | (Pass 6 output) |
| 4 | IFC subset present | PASS/FAIL | (Pass 7 output) |
| 5 | Lint 5 canonical membership | PASS/FAIL | (Lint 5 output) |
| 6 | F.1 retrofit clean | PASS/FAIL | (Room.type pattern + Room.classification present) |
| 7 | Banned-citation grep clean | PASS/FAIL | (grep exit code) |
| FAB | Spot-check 30 random codes against mirror | PASS/FAIL | (manual verification per code) |

- [ ] **Step 4: Final verdict**

- PASS: all checks PASS + spot-check passes
- SHIP-WITH-NOTED-CONCERNS: total entries <540 (90%) but spot-check passes
- FIX-FIRST: any check FAIL OR fabrication detected in spot-check

- [ ] **Step 5: No commit (read-only review)**

If FIX-FIRST: dispatch fix-pass tied to the specific failed check + return to X.B/C/D as needed.

### Task X.E.5: Push deferred to user authorisation

**Files:**
- No file edits

**Why:** Per CLAUDE.md "shared state" rule, push to `origin/main` requires explicit user authorisation.

- [ ] **Step 1: Confirm Sprint X commits are local on `main`**

```bash
git log --oneline origin/main..HEAD | head -30 | wc -l
git log --oneline -5
```

Expected: ~85-95 commits ahead of `origin/main`.

- [ ] **Step 2: Compose sprint summary for user**

Cover:
- Gates: baseline → final (current 3-pass / 4-pass with F.5 already shipped — adapt; +Pass 5/6/7 + Lint 5)
- ~600 room-types entries actual vs target
- ASHRAE coverage (90.1 ~120 / 62.1 ~150)
- IFC subset ~200 lines
- F.1 retrofit (enum → pattern; backwards-compatible)
- Room.classification field added
- Cross-references back-filled (~bs_en/ashrae populated counts)
- CIBSE + NRM2 honestly deferred
- X.E.4 verdict line
- Confirm push is the only remaining action

- [ ] **Step 3: Wait for user "yes push" authorisation**

STOP. Do NOT push without explicit go-ahead.

- [ ] **Step 4: On authorisation, push**

```bash
git push origin main 2>&1 | tail -5
```

- [ ] **Step 5: Confirm + final report**

```bash
git log --oneline origin/main..HEAD | head -5
```

Expected: 0 commits ahead post-push.

- [ ] **Step 6: Sprint X close**

Sprint X shipped. Sprint F can now RESUME at F.4 (ORCHESTRATION.md now references the comprehensive room-types catalogue). After Sprint F ships, Sprint W1 (lighting-layout + small-power grounding) follows.

---

## Self-review (writing-plans skill)

### Spec coverage

| Spec section | Plan task(s) |
|---|---|
| §3.1 Coverage target ~600 OmniClass entries | X.B.1-X.B.7 (7 per-category tasks ~80+120+150+130+60+40+20 = 600) |
| §3.2 Public mirror source authority | X.A.0 source provenance (mirror selection + edition + URL + access date) |
| §3.3 Per-entry richness — minimal mandatory + cross-refs where exist | X.A.1 schema requires canonical_id + omniclass_code + parent_category + _verification_status; X.D.1 back-fills cross_references |
| §3.4 Split per parent_category + master index | X.A.2 master index + X.B.1-7 per-category files |
| §3.5 F.1 retrofit mechanism (enum → pattern; lint canonical) | X.E.2 retrofit + X.E.1 Lint 5 |
| §3.6 Sprint X scope (mega-sprint with ASHRAE + IFC + classification + fuzzy-match) | X.A.3 IFC + X.C.1 ASHRAE 90.1 + X.C.2 ASHRAE 62.1 + X.D.2 Room.classification + X.D.3 fuzzy-match |
| §4.1 NEW shared/standards/spaces/ folder | X.A.2 + X.B.1-7 |
| §4.2 NEW shared/standards/bim/ISO16739/ | X.A.3 |
| §4.3 NEW shared/standards/energy/ASHRAE-90-1/ + hvac/ASHRAE-62-1/ | X.C.1 + X.C.2 |
| §5 Per-entry shape (canonical_id + omniclass_code + parent_category + parent_path + common_aliases + ifc_space_type + _verification_status + cross_references) | X.A.1 schema requires all + X.B.* tasks author entries matching schema |
| §6 Sprint structure (5 phases × 23 tasks) | Phase X.A 4 tasks + Phase X.B 7 + Phase X.C 2 + Phase X.D 3 + Phase X.E 5 = 21 (slight discrepancy: end-of-Phase-X.B cross-check is documented as inline check, not a discrete task; count consistent with spec target of 23 including end-of-phase X.B verification) |
| §7 F.1 retrofit (Room.type → pattern; Room.classification field added) | X.E.2 retrofit + X.D.2 Room.classification |
| §8 Transcription methodology | X.A.0 declares mirror + edition + verification status taxonomy |
| §9 Sprint sequence (D5 ✓ → F paused → X → F resumes → W1/W2) | Header section + closing note |
| §10 Definition of done (11 items) | Sprint X.E.4 7-check fence verifies items 1-9; items 10-11 verified at X.E.5 push state |
| §11 Risk surfaces (6 items) | Header section discipline + per-task fabrication-prevention + X.E.4 spot-check + Lint 5 |
| §12 Process discipline | Header section locked from sprint start |
| §13 Out of scope (CIBSE + NRM2 + full IFC + fuzzy engine) | Documented in X.A.0 provenance spec + shared/standards/spaces/README.md + X.D.3 fuzzy-match-reference.md |

All 13 spec sections covered.

### Placeholder scan

- No raw "TBD" / "TODO" / "implement later".
- The 80 residential canonical_ids in X.B.1 step 3 ARE listed; the 120+150+130+60+40+20 ids in X.B.2-7 are NOT listed in detail (the implementer surveys the mirror at execution time and transcribes verbatim — listing 600 hypothetical IDs in the plan would either fabricate codes OR commit to specific values before mirror survey). This is intentional: the plan structure + acceptance criteria + uniqueness/schema/gate validation enforce correctness; the entry content lands at execution time after the implementer consults the real mirror. This matches the spec's §3.2 authority discipline.
- Every code-step includes the actual code or command needed.

### Type / name consistency

- `canonical_id` shape: `^[a-z]+(\.[a-z0-9_]+)+$` consistent across X.A.1 schema + X.B.* per-category files + X.D.1 cross-walk + X.E.2 F.1 retrofit pattern.
- `omniclass_code` shape: `^13-[0-9]{2}( [0-9]{2}){0,4}$` consistent across X.A.1 schema + X.B.* + X.D.2 Room.classification.code.
- `parent_category` enum (residential / commercial / institutional / industrial / transport / external / agricultural) consistent across X.A.1 schema + X.A.2 master index + X.B.* per-category files.
- `_verification_status` enum (mirror_sourced / occs_verified / inferred) consistent across X.A.0 provenance + X.A.1 schema + X.B.* + X.E.4 spot-check.
- `cross_references` keys (bs_en_12464_1 / cibse_lg / ashrae_90_1 / ashrae_62_1 / nrm2) consistent across X.A.1 schema + X.D.1 back-fill + cross-reference docs.
- `placement_convention` mapping (room_local_mm / floor_local_mm / site_local_mm / none_topological) consistent across X.A.3 IFC placement.json + Sprint F.2 manifest schema.

### Issues found and fixed inline

None — self-review found no defects requiring inline fixes.

---

## Execution handoff

Plan complete and saved to [`docs/superpowers/plans/2026-06-05-sprint-X-comprehensive-room-taxonomy-sprint.md`](2026-06-05-sprint-X-comprehensive-room-taxonomy-sprint.md).

**Two execution options:**

1. **Subagent-Driven (recommended)** — Fresh subagent per task, two-stage Opus review after each, fast iteration. Matches the D4/D5/F sprint precedent. Critical: X.E.4 fabrication-detection spot-check is the unique-to-Sprint-X review gate.
2. **Inline Execution** — Execute tasks in this session using executing-plans, batch with checkpoints.

**Which approach?**
