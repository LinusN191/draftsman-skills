# Sprint X — Comprehensive Room Taxonomy Design Spec

**Date:** 2026-06-05
**Sprint:** X (Comprehensive Room Taxonomy) — runs BETWEEN Sprint F.3 and F.4
**Origin:** User audit of F.1 schema (commit `c756c4e`) — 27-value Room.type enum incomplete; missing residential / healthcare specialty / industrial process / hospitality / public buildings / transport / external
**Locked decisions:** see §3
**Pattern parent:** D5 sprint A.0 area-definitions.json transcription (standards-file authoring discipline)
**Target:** Author the canonical comprehensive room-type taxonomy + supporting BIM/ASHRAE standards layers; retrofit F.1 SkillInput schema to reference the catalogue

---

## 1. Mission

Replace F.1's partial 27-value Room.type enum with the canonical comprehensive room-type taxonomy sourced from OmniClass Table 13 (BIM-aligned via publicly-available mirror), with supporting transcriptions of ASHRAE 90.1 Table 9.6.1 (lighting power density) + ASHRAE 62.1 (ventilation rates) + IFC IfcSpaceTypeEnum/IfcClassification subset. Sprint X runs BEFORE Sprint F resumes — F.1 gets retrofitted as the last step of Sprint X (X.E.2).

## 2. Origin (why mid-sprint pause)

During Sprint F execution (after F.3 shipped `08b6e38`), user audited the 27-value Room.type enum in F.1's `shared/schemas/core/skill-input.schema.json` and observed missing coverage: no residential (bedrooms / kitchens / living rooms), no healthcare specialty (operating theatres / ICU / imaging), no industrial process (plant rooms / clean rooms / server rooms), no hospitality, no public buildings, no transport, no external. User asked: "do we have a standard that defines all this; we align 100%". Decision: pause Sprint F at F.3; Sprint X authors the comprehensive taxonomy; F.1 schema gets retrofitted as Sprint X final step; Sprint F resumes at F.4.

## 3. Locked decisions (from brainstorm)

### 3.1 Coverage target
Full OmniClass Table 13 transcription (~600 entries) in one sprint. Authoritative one-shot. Single source of truth from day one.

### 3.2 Source authority
Publicly-available OmniClass Table 13 mirror (NIBS / buildingSMART / academic publications / Autodesk BIM documentation / CSI MasterFormat cross-references). Declared edition (likely 2012; most-cited). Honest disclosure: codes sourced from mirror, not OCCS canonical PDF.

### 3.3 Per-entry richness
Minimal mandatory (canonical_id + omniclass_code + parent_category + common_aliases + _verification_status) + cross_references populated where source standards exist in repo. CIBSE + NRM2 cross-refs deferred (paid source access blocker).

### 3.4 File shape
Split per parent_category + master index file. 7 per-category JSON files under `shared/standards/spaces/room-types/` + master `shared/standards/spaces/room-types.json` index.

### 3.5 F.1 retrofit mechanism
Drop the hardcoded 27-value enum in F.1's Room.type; replace with snake_case pattern `^[a-z]+(\.[a-z0-9_]+)+$`. Canonical-membership enforcement moves from schema-time to gate-time via new Lint sub-pass 5. Schema decoupled from taxonomy growth.

### 3.6 Sprint X scope (mega-sprint approved)
Feasible mega-Sprint X (~85-95 commits) — original OmniClass Table 13 + ASHRAE 90.1 + ASHRAE 62.1 + IFC standards layer + room.classification field + fuzzy-match reference. CIBSE + NRM2 deferred (paid access blocked). 2-3 sessions execution.

## 4. Folder layout

### 4.1 NEW `shared/standards/spaces/`

```
shared/standards/spaces/
├── README.md                                 # X.A.2 authoring; source + edition + CIBSE/NRM2 deferred TODO
├── room-types.json                           # MASTER index; declares _source + _edition + per-category file paths
├── room-types-schema.json                    # NEW Draft-07 metaschema for per-entry shape
├── fuzzy-match-reference.md                  # X.D.3 algorithm spec + test fixtures
├── _source/
│   └── OmniClass-Table-13-source-notes.md    # Mirror URL + access date + transcription gaps
└── room-types/
    ├── residential.json    # ~80 entries (single-family / multi-family / dormitory / hotel-style)
    ├── commercial.json     # ~120 entries (office / retail / banking / hospitality / restaurant)
    ├── institutional.json  # ~150 entries (healthcare / education / cultural / civic / religious)
    ├── industrial.json     # ~130 entries (manufacturing / warehouse / processing / utility)
    ├── transport.json      # ~60 entries (rail / aviation / road / marine / parking)
    ├── external.json       # ~40 entries (outdoor work / landscape / circulation)
    └── agricultural.json   # ~20 entries (livestock / crops / processing)
```

### 4.2 NEW `shared/standards/bim/ISO16739/`

```
shared/standards/bim/ISO16739/
├── README.md
├── space-types.json              # IfcSpaceTypeEnum (~7 values: PARKING/GFA/BERTHING/EXTERNAL/INTERNAL/USERDEFINED/NOTDEFINED)
├── classification.json           # IfcClassification + IfcClassificationReference + IfcRelAssociatesClassification entities
├── placement.json                # IfcLocalPlacement + IfcAxis2Placement3D (justifies placement_convention enum)
└── reference.md                  # Companion human-readable reference
```

~200 lines total transcription. Closes F.0's line-61 honest disclosure ("ISO 16739 layer would be authored following same pattern as BSEN12464").

### 4.3 NEW `shared/standards/energy/ASHRAE-90-1/` + `shared/standards/hvac/ASHRAE-62-1/`

```
shared/standards/energy/ASHRAE-90-1/
├── README.md
├── lpd-table-9-6-1.json    # ~120 space types with LPD W/m² (cited ASHRAE 90.1-2019 or latest)
└── reference.md             # Companion reference

shared/standards/hvac/ASHRAE-62-1/
├── README.md
├── ventilation-rates.json  # ~150 space types with outdoor air rates (cited ASHRAE 62.1-2019)
└── reference.md             # Companion reference
```

## 5. Per-entry shape (room-types-schema.json)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "RoomTypeEntry",
  "required": ["canonical_id", "omniclass_code", "parent_category", "_verification_status"],
  "properties": {
    "canonical_id": {
      "type": "string",
      "pattern": "^[a-z]+(\\.[a-z0-9_]+)+$",
      "description": "Snake_case dotted identifier used as Room.type in SkillInput. E.g. office.open_plan, healthcare.operating_theatre_general, residential.bedroom_master."
    },
    "omniclass_code": {
      "type": "string",
      "pattern": "^13-[0-9]{2}( [0-9]{2}){0,4}$",
      "description": "OmniClass Table 13 verbatim code (5-segment 13-digit notation). E.g. 13-37 31 21 11."
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
      "description": "Hierarchical drill-down path (3-level max). E.g. [institutional, healthcare, treatment]."
    },
    "common_aliases": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Non-canonical synonyms for fuzzy lookup. E.g. ['operating room', 'OR', 'theatre', 'surgery suite']."
    },
    "ifc_space_type": {
      "type": "string",
      "enum": ["PARKING", "GFA", "BERTHING", "EXTERNAL", "INTERNAL", "USERDEFINED", "NOTDEFINED"],
      "description": "Coarse IfcSpaceTypeEnum value (mostly INTERNAL or EXTERNAL)."
    },
    "_verification_status": {
      "type": "string",
      "enum": ["mirror_sourced", "occs_verified", "inferred"]
    },
    "cross_references": {
      "type": "object",
      "properties": {
        "bs_en_12464_1": {"type": ["string", "null"]},
        "cibse_lg": {"type": ["string", "null"]},
        "ashrae_90_1": {"type": ["string", "null"]},
        "ashrae_62_1": {"type": ["string", "null"]},
        "nrm2": {"type": ["string", "null"]}
      },
      "additionalProperties": false
    }
  },
  "additionalProperties": false
}
```

## 6. Sprint structure (5 phases, 23 implementer tasks)

### Phase X.A — Foundation (4 tasks, ~5-7 commits)

| Task | Model | Deliverable |
|---|---|---|
| X.A.0 | Opus | `docs/superpowers/specs/sprint-X-source-provenance.md` — declares mirrors + editions + verification status taxonomy; documents CIBSE/NRM2 deferred TODO |
| X.A.1 | Sonnet | `shared/standards/spaces/room-types-schema.json` per-entry metaschema |
| X.A.2 | Sonnet | `room-types.json` master index + `README.md` + `_source/OmniClass-Table-13-source-notes.md` |
| X.A.3 | Sonnet | `shared/standards/bim/ISO16739/` — 4 files (space-types + classification + placement + reference.md), ~200 lines total |

### Phase X.B — OmniClass per-category transcription (7 tasks, ~25-35 commits)

| Task | Model | File | ~Entries |
|---|---|---|---|
| X.B.1 | Opus | `room-types/residential.json` | 80 |
| X.B.2 | Sonnet | `room-types/commercial.json` | 120 |
| X.B.3 | Sonnet | `room-types/institutional.json` | 150 |
| X.B.4 | Sonnet | `room-types/industrial.json` | 130 |
| X.B.5 | Sonnet | `room-types/transport.json` | 60 |
| X.B.6 | Sonnet | `room-types/external.json` | 40 |
| X.B.7 | Sonnet | `room-types/agricultural.json` | 20 |

X.B.1 is Opus to set the per-category pattern; X.B.2-7 are Sonnet once pattern stable.

### Phase X.C — Energy + ventilation standards transcription (2 tasks, ~15-20 commits)

| Task | Model | Deliverable |
|---|---|---|
| X.C.1 | Opus | `shared/standards/energy/ASHRAE-90-1/lpd-table-9-6-1.json` + reference.md — ~120 space types with LPD W/m² (cite ASHRAE 90.1-2019 or latest publicly-accessible) |
| X.C.2 | Opus | `shared/standards/hvac/ASHRAE-62-1/ventilation-rates.json` + reference.md — ~150 space types with outdoor air rates (cite ASHRAE 62.1-2019 or latest) |

### Phase X.D — Cross-reference back-fill + new contract features (3 tasks, ~15-20 commits)

| Task | Model | Deliverable |
|---|---|---|
| X.D.1 | Sonnet | Back-fill `cross_references` on all ~600 room-types entries. Mechanical cross-walk: scan ASHRAE 90.1 + ASHRAE 62.1 + BS EN 12464-1 + IFC entries for matching canonical_id; populate cross_references where matched; null where not. Sample 10% spot-check by Opus reviewer. |
| X.D.2 | Opus | F.1 SkillInput schema extension — add `room.classification` field per BIM IfcClassificationReference structure: `{source, edition, code, reference_uri}`. Update `skill-input.reference.md` to document the new optional field. |
| X.D.3 | Sonnet | `shared/standards/spaces/fuzzy-match-reference.md` — algorithm spec (exact → alias → snake_case → Levenshtein ≤2 → embedding fallback) + worked examples + test fixtures. Self-contained reference; orchestrators implement engines per `[[runtime-project-boundary]]`. |

### Phase X.E — Gate extension + F.1 retrofit + ship (5 tasks, ~10-13 commits)

| Task | Model | Deliverable |
|---|---|---|
| X.E.1 | Sonnet | Extend `scripts/validate-examples.py` with Pass 5 (room-types-schema validation × 7 category files) + Pass 6 (ASHRAE files) + Pass 7 (IFC subset) + Lint sub-pass 5 (canonical room.type membership across all `examples/*/output.json` + intent-out.json + input.json files; FAIL on non-canonical; SUGGEST on alias-match) |
| X.E.2 | Sonnet | **F.1 RETROFIT** — `skill-input.schema.json` Room.type changes from 27-value enum to snake_case pattern; reference.md updated to point at room-types.json catalogue |
| X.E.3 | Sonnet | CHANGELOG entry per repo root + memory file `sprint-X-comprehensive-taxonomy-shipped.md` + MEMORY.md index + CLAUDE.md note (Sprint X shipped + F.1 retrofit complete) |
| X.E.4 | Opus | Final cross-sprint integration review — 7-check fence: (1) room-types-schema valid, (2) 7 category files validate ≥600 total, (3) ASHRAE files validate, (4) IFC subset present, (5) Lint 5 canonical membership works, (6) F.1 retrofit clean, (7) banned-citation grep clean |
| X.E.5 | — | Push deferred to user authorisation |

## 7. F.1 retrofit (X.E.2 — the critical schema change)

### Before X.E.2

```json
"type": {
  "type": "string",
  "enum": [
    "office.open_plan", "office.private_office", ... 27 values
  ]
}
```

### After X.E.2

```json
"type": {
  "type": "string",
  "pattern": "^[a-z]+(\\.[a-z0-9_]+)+$",
  "description": "Snake_case canonical_id from shared/standards/spaces/room-types/*.json. Canonical membership enforced at gate-time via Lint sub-pass 5 against the ~600-entry catalogue. Examples: office.open_plan, healthcare.operating_theatre_general, residential.bedroom_master. See ORCHESTRATION.md for full taxonomy reference."
}
```

Backwards-compatible: every value that satisfied the 27-value enum also satisfies the pattern. Existing fixtures untouched.

### `room.classification` addition (X.D.2)

```json
"classification": {
  "type": "object",
  "description": "Optional BIM IfcClassificationReference structure for round-tripping room.type via IFC. Auto-derivable from room.type via shared/standards/spaces/room-types/*.json lookup; orchestrators populating this directly carry the canonical reference inline.",
  "properties": {
    "source": {"type": "string", "default": "OmniClass-Table-13"},
    "edition": {"type": "string"},
    "code": {"type": "string", "pattern": "^13-[0-9]{2}( [0-9]{2}){0,4}$"},
    "reference_uri": {"type": "string", "format": "uri"}
  },
  "additionalProperties": false
}
```

## 8. Transcription methodology (X.A.0 deliverable)

1. **Public mirror selection** — implementer surveys publicly-available OmniClass Table 13 mirrors (NIBS, buildingSMART, academic publications, Autodesk BIM docs, CSI MasterFormat cross-references). Selected mirror declared in `_source_mirror` field with URL + access-date.
2. **Edition declaration** — OmniClass had editions 2006/2012/2019/2024. Mirror typically reflects 2012 (most-cited). Declared in `_edition`.
3. **Code format verification** — OmniClass uses `13-XX XX XX XX XX` 5-segment notation. Codes that don't match flagged as `_verification_status: inferred`.
4. **Missing-entry handling** — where the mirror gap exceeds 10% in a category, X.A.0 documents the gap; that category's entry count drops; future sprint back-fills from OCCS PDF.
5. **canonical_id derivation** — snake_case slug of `parent_category.sub_category.entry_name`. Disambiguated where collisions occur.
6. **alias collection** — common aliases from architectural practice for fuzzy-match support.
7. **Hierarchical depth** — OmniClass Table 13 has up to 5 levels; we flatten to 3-level `parent_path` array for orchestrator simplicity.

## 9. Sprint sequence

```
[Sprint D5 lighting-layout v1.7.0 SHIPPED] ✓ pushed
       ↓
[Sprint F Foundation PAUSED at F.3]
       ├── F.0 ✓ design rationale 8c59304
       ├── F.1 ✓ skill-input.schema c756c4e (27-value enum LOCKED → retrofitted at X.E.2)
       ├── F.2 ✓ skill-manifest.schema f97084b
       └── F.3 ✓ inputs.schema grounded_source 08b6e38
       ↓
[Sprint X — Comprehensive Room Taxonomy MEGA-SPRINT]  ← we are here, brainstorm done
       ├── X.A — Foundation (4 tasks)
       ├── X.B — OmniClass 7 categories (7 tasks)
       ├── X.C — ASHRAE 90.1 + 62.1 (2 tasks)
       ├── X.D — Cross-ref back-fill + room.classification + fuzzy-match (3 tasks)
       └── X.E — Gate ext + F.1 retrofit + ship (5 tasks)
       ↓
[Sprint F RESUMES at F.4 — ORCHESTRATION.md now references room-types.json]
       ↓
[Sprint W1 — lighting-layout + small-power grounding]
       ↓
[Sprint W2 — db-layout + arc-flash + schematic + sld + earthing grounding]
```

## 10. Definition of done

1. `shared/standards/spaces/room-types.json` master index + 7 per-category files with ≥600 entries total
2. `shared/standards/spaces/room-types-schema.json` Draft-07 metaschema; every entry validates
3. `shared/standards/bim/ISO16739/` subset transcribed (IfcSpaceTypeEnum + IfcClassification + IfcLocalPlacement + ~3 more entities; ~200 lines)
4. `shared/standards/energy/ASHRAE-90-1/lpd-table-9-6-1.json` with ≥100 entries
5. `shared/standards/hvac/ASHRAE-62-1/ventilation-rates.json` with ≥120 entries
6. `cross_references` populated on every room-types entry where matching ASHRAE/BS EN 12464-1/IFC entry exists
7. `shared/standards/spaces/fuzzy-match-reference.md` algorithm spec + test fixtures
8. F.1 SkillInput schema retrofitted (X.E.2): Room.type pattern-validated; Room.classification field added per IfcClassificationReference
9. 5-pass + 5-lint golden CI gate green (Pass 5/6/7 added by X.E.1)
10. CIBSE + NRM2 honestly documented as TODO in `shared/standards/spaces/README.md`
11. Push deferred to user authorisation

## 11. Risk surfaces

1. **OmniClass mirror coverage gaps** — mirror may be incomplete for some entries. Mitigation: `_verification_status: inferred` flag + per-entry honest disclosure; gap-by-category documented in X.A.0 source-notes.
2. **ASHRAE edition drift** — 2019 vs 2022 vs 2025. Mitigation: declare edition in `_source` field; choose latest publicly-accessible (likely 2019).
3. **Cross-reference accuracy** — mechanical cross-walk via Python script may misalign canonical_ids with ASHRAE space types. Mitigation: X.D.1 review pass spot-checks 10% sample.
4. **IFC subset completeness** — ISO 16739 is 1500+ pages; we transcribe only the room-type-relevant entities. Mitigation: X.A.3 documents the boundary explicitly; future sprint extends if needed.
5. **F.1 schema retrofit cascade impact** — changing Room.type from enum to pattern is technically a schema change. Mitigation: backwards-compatible (any value that satisfied enum also satisfies pattern); existing fixtures still validate.
6. **Sprint size vs context window** — 85-95 commits across 23 tasks may saturate single-session context. Mitigation: 4-portion plan (foundation / OmniClass / standards / cross-ref+retrofit+ship); per-portion execution if needed.

## 12. Process discipline (locked)

- Sonnet for mechanical / Opus for judgment per `[[feedback-no-haiku-sonnet-opus-only]]`
- Two-stage Opus review + fix-pass per task (D4/D5 precedent)
- Citation hygiene: every entry cites OmniClass Table 13 verbatim; ASHRAE entries cite ASHRAE 90.1-XXXX / 62.1-XXXX edition; IFC entries cite ISO 16739 entity names
- Banned tokens inherited: §526.2, §433.2, OZEV, 3rd Edition, Reg 559, Em_room, "average room lux"
- No-trim per `[[feedback-no-trim-non-consequential]]`: evidence stays full-length
- 7-check verification fence at X.E.4
- Final cross-sprint Opus integration review at X.E.4 with PASS / SHIP-WITH-NOTED-CONCERNS / FIX-FIRST verdict
- Push deferred to user authorisation per CLAUDE.md shared-state rule at X.E.5

## 13. Out of scope (deferred to future sprints)

- **CIBSE LG1/LG2/LG7/LG10/LG12 + Guide A transcription** — paid CIBSE membership required for canonical PDFs. Sprint Y when access granted.
- **NRM2/NRM3 transcription** — paid RICS PDF required. Sprint Y when access granted.
- **Full IFC standards layer** — Sprint X transcribes only the room-type-relevant entities (IfcSpace, IfcClassification, IfcLocalPlacement). Full ISO 16739 layer awaits runtime IFC export needs.
- **Fuzzy-match execution engine** — Sprint X ships algorithm spec only; runtime project implements per `[[runtime-project-boundary]]`.
- **SkillInput room.classification cascade integration** — Sprint X adds the field; W1/W2 don't consume it yet. Future sprint (post-W2) wires classification through orchestration layer.
