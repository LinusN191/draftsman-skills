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
