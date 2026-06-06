# Sprint Z — Uniclass 2015 SL (room-level) + OmniClass Table 11 (building-level) Design Spec

**Date:** 2026-06-06
**Sprint:** Z — Companion to Sprint X (just shipped: 290 OmniClass T13 entries across 13 spaces-by-function categories)
**Origin:** Sprint X coverage audit surfaced that ~60-70% of the most common building types (residential / hotels / offices / retail / restaurants / industrial / warehouses / agricultural) are NOT covered by OmniClass T13. Mid-design discovery that **OmniClass T11 is BUILDING-LEVEL not room-level**, so the originally-proposed T11-only Sprint Z would not solve the gap. Pivoted to dual-taxonomy: Uniclass 2015 SL (room-level) + OmniClass T11 (building-level cross-references).
**Pattern parent:** Sprint X structure (`docs/superpowers/specs/2026-06-05-comprehensive-room-taxonomy-design.md` + `docs/superpowers/plans/2026-06-05-sprint-X-comprehensive-room-taxonomy-sprint.md`)
**Target:** ~50-60 commits authoring the room-level taxonomy that closes the residential / hotel / office / retail / restaurant / industrial / warehouse / agricultural gaps in our SkillInput contract.

---

## 1. Mission

Author the **room-level** taxonomy that OmniClass T13 lacks, using **Uniclass 2015 Table SL (Spaces & Locations)** — the UK NBS-published comprehensive room-type catalogue used by NRM2 + BS 1192 + ISO 19650 projects. Concurrently transcribe **OmniClass Table 11 (Construction Entities by Function)** as the building-level cross-reference layer so consumers can model "this room is in a hotel building" via SL→T11 relations.

After Sprint Z, the public skill-orchestration contract carries 3 complementary taxonomies:

| Taxonomy | Coverage | Scope |
|---|---|---|
| OmniClass Table 13 (Sprint X) | Healthcare / education / circulation / facility services / theatres / etc. | 290 entries / 13 categories |
| **Uniclass 2015 Table SL (Sprint Z)** | **Residential / hotel / office / retail / restaurant / industrial / warehouse / agricultural rooms** | **~260 entries / 7 categories (target)** |
| **OmniClass Table 11 (Sprint Z)** | **Building-level cross-references** | **~50-80 building-type entries** |

## 2. Mid-design discovery (why T11 alone insufficient)

User-prompted pre-design WebSearch confirmed via OmniClass authoritative sources:

> "Table 11 focuses on construction entities by function" (i.e. whole buildings)
> "Table 13 classifies Spaces by Function which are basic units of the built environment delineated by physical or abstract boundaries"

T11 codes resolve to entities like "single-family residential construction" or "hotel building" — NOT to rooms within them. The T11-only Sprint Z proposed in the original brief would have failed to surface room-level entries like bedroom / kitchen / hotel guest room / office.private / shopfloor — exactly the gap Sprint X audit identified.

**Decision:** dual-taxonomy approach. Uniclass SL provides the room-level catalogue; T11 provides the building-level cross-reference. Combined with the T13 catalogue from Sprint X, all 3 form the comprehensive SkillInput Room.type catalogue.

## 3. Locked decisions (from brainstorm)

### 3.1 Two new taxonomies in one schema
Schema gains `taxonomy_source` enum discriminator (3 values: `OmniClass-Table-13` / `OmniClass-Table-11` / `Uniclass-2015-SL`). Each entry declares its taxonomy source.

### 3.2 Uniclass SL scope
Transcribe 7 categories matching the 7 missing types from Sprint X audit:
- `residential` (~50-80 entries)
- `commercial` (~40 entries — offices / meeting rooms / receptions)
- `retail` (~30 entries — shopfloor / fitting / stockroom)
- `hospitality` (~40 entries — guest rooms / restaurants / kitchens / bars)
- `industrial` (~50 entries — manufacturing / processing / workshops)
- `agricultural` (~20 entries — livestock / crops / processing)
- `transport` (~30 entries — stations / terminals / waiting rooms)

Skip categories already covered by T13 (institutional / educational / healthcare / governmental / religious / artistic).

### 3.3 OmniClass T11 scope
Single per-class file `building-types-t11/construction-entities-by-function.json` with ~50-80 building-type entries spanning all T11 top-level classes (used for cross-reference rollup from SL rooms).

### 3.4 Source authority (per Sprint X X.A.0 precedent)
- **Uniclass SL primary:** publicly accessible via NBS Source (https://uniclass.thenbs.com/) — main NBS-published canonical
- **Uniclass SL secondary:** designingbuildings.co.uk Uniclass coverage / GOV.UK BIM Level 2 documentation
- **OmniClass T11:** same pdfcoffee / scribd mirror pattern as Sprint X X.A.0 (verbatim-only)

Implementers cite real mirror URLs + access dates. Fabrication-prevention contract carried over from Sprint X.

### 3.5 Cross-references
SL room entries get optional `building_type_codes: ["11-XX XX XX XX", ...]` listing the OmniClass T11 codes for buildings that typically contain the room. Example: `residential.bedroom_master` → `["11-11 11 11" single-family detached, "11-11 13" multi-family apartment]`.

T13 entries from Sprint X are NOT retroactively given this field (keeps Sprint X cohesive).

### 3.6 Schema-level discriminator
`omniclass_code` becomes optional (only required when `taxonomy_source ∈ {OmniClass-Table-13, OmniClass-Table-11}`). New field `uniclass_code` (pattern `^SL_[0-9]{2}_[0-9]{2}_[0-9]{2}$`) required when `taxonomy_source = Uniclass-2015-SL`.

## 4. Folder layout

### 4.1 Modified (existing)

```
shared/standards/spaces/
├── room-types-schema.json     # MODIFY: add taxonomy_source discriminator + uniclass_code + building_type_codes
├── room-types.json             # MODIFY: master index references all 3 catalogues
├── README.md                   # MODIFY: document 3-taxonomy approach
└── _source/
    ├── OmniClass-Table-13-source-notes.md  # unchanged (Sprint X)
    ├── Uniclass-2015-SL-source-notes.md    # NEW: Sprint Z mirror provenance
    └── OmniClass-Table-11-source-notes.md  # NEW: Sprint Z mirror provenance
```

### 4.2 NEW (Sprint Z)

```
shared/standards/spaces/
├── room-types-uniclass-sl/
│   ├── residential.json
│   ├── commercial.json
│   ├── retail.json
│   ├── hospitality.json
│   ├── industrial.json
│   ├── agricultural.json
│   └── transport.json
└── building-types-t11/
    └── construction-entities-by-function.json
```

## 5. Per-entry shape (extended room-types-schema.json)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "RoomTypeEntry",
  "required": ["canonical_id", "taxonomy_source", "parent_category", "_verification_status"],
  "properties": {
    "canonical_id": {
      "type": "string",
      "pattern": "^[a-z][a-z0-9_]*(\\.[a-z0-9_]+)+$"
    },
    "taxonomy_source": {
      "type": "string",
      "enum": ["OmniClass-Table-13", "OmniClass-Table-11", "Uniclass-2015-SL"]
    },
    "omniclass_code": {
      "type": "string",
      "pattern": "^1[13]-[0-9]{2}( [0-9]{2}){0,4}$",
      "description": "Required when taxonomy_source ∈ {OmniClass-Table-13, OmniClass-Table-11}. Pattern accepts both 13- and 11- prefixes."
    },
    "uniclass_code": {
      "type": "string",
      "pattern": "^SL_[0-9]{2}_[0-9]{2}_[0-9]{2}$",
      "description": "Required when taxonomy_source = Uniclass-2015-SL. Uniclass 2015 SL 6-digit notation."
    },
    "parent_category": {
      "type": "string",
      "enum": [
        "space_planning_types", "parking_spaces", "facility_service_spaces",
        "circulation_spaces", "education_and_training_spaces", "recreation_spaces",
        "government_spaces", "artistic_spaces", "museum_spaces", "library_spaces",
        "spiritual_spaces", "environmentally_controlled_spaces", "healthcare_spaces",
        "residential", "commercial", "retail", "hospitality",
        "industrial", "agricultural", "transport",
        "construction_entities"
      ]
    },
    "parent_path": { "type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": 3 },
    "common_aliases": { "type": "array", "items": {"type": "string"} },
    "ifc_space_type": {
      "type": "string",
      "enum": ["PARKING", "GFA", "BERTHING", "EXTERNAL", "INTERNAL", "USERDEFINED", "NOTDEFINED"]
    },
    "building_type_codes": {
      "type": "array",
      "items": {"type": "string", "pattern": "^11-[0-9]{2}( [0-9]{2}){0,4}$"},
      "description": "Optional. SL rooms reference T11 building codes for rollup."
    },
    "_verification_status": {
      "type": "string",
      "enum": ["mirror_sourced", "occs_verified", "inferred", "nbs_sourced", "engineering_consensus"]
    },
    "_inference_note": { "type": "string" },
    "_source_mirror": { "type": "string", "format": "uri" },
    "cross_references": {
      "type": "object",
      "properties": {
        "bs_en_12464_1": { "type": ["string", "null"] },
        "cibse_lg": { "type": ["string", "null"] },
        "ashrae_90_1": { "type": ["string", "null"] },
        "ashrae_62_1": { "type": ["string", "null"] },
        "nrm2": { "type": ["string", "null"] }
      },
      "additionalProperties": false
    }
  },
  "additionalProperties": false,
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
}
```

### 5.1 Sprint X T13 back-compat
Existing 290 Sprint X entries must be retroactively patched to add `taxonomy_source: "OmniClass-Table-13"`. This is a mechanical sweep (1 commit). Their `parent_category` values stay unchanged.

## 6. Sprint structure (5 phases, ~18 implementer tasks)

### Phase Z.A — Foundation (4 tasks, ~5-7 commits)

| Task | Model | Deliverable |
|---|---|---|
| Z.A.0 | Opus | `docs/superpowers/specs/sprint-Z-source-provenance.md` — Uniclass SL + T11 mirror selection + edition declarations + verification status taxonomy |
| Z.A.1 | Sonnet | Schema extension: `room-types-schema.json` adds `taxonomy_source` + `uniclass_code` + `building_type_codes` + allOf conditional requirements |
| Z.A.2 | Sonnet | Master index `room-types.json` re-architecture: declares 3 catalogues (T13 + SL + T11); per-catalogue category lists |
| Z.A.3 | Sonnet | Sprint X T13 back-compat sweep: add `taxonomy_source: "OmniClass-Table-13"` to all 290 existing entries; mechanical script |

### Phase Z.B — Uniclass SL per-category transcription (7 tasks, ~25-30 commits)

| Task | Model | File | Target Entries |
|---|---|---|---|
| Z.B.1 | Opus | `residential.json` (pattern-setter) | ~50-80 |
| Z.B.2 | Sonnet | `commercial.json` | ~40 |
| Z.B.3 | Sonnet | `retail.json` | ~30 |
| Z.B.4 | Sonnet | `hospitality.json` | ~40 |
| Z.B.5 | Sonnet | `industrial.json` | ~50 |
| Z.B.6 | Sonnet | `agricultural.json` | ~20 |
| Z.B.7 | Sonnet | `transport.json` | ~30 |

### Phase Z.C — OmniClass T11 building types (1 task, ~3-5 commits)

| Task | Model | Deliverable |
|---|---|---|
| Z.C.1 | Opus | `construction-entities-by-function.json` — ~50-80 building-type entries verbatim from T11 mirror; spans all top-level T11 classes |

### Phase Z.D — Cross-references + ASHRAE/BS EN back-fill (1 task, ~3-5 commits)

| Task | Model | Deliverable |
|---|---|---|
| Z.D.1 | Sonnet | Back-fill `cross_references` on all new SL + T11 entries (BS EN 12464-1 / ASHRAE 90.1 / ASHRAE 62.1); populate `building_type_codes[]` on SL room entries with their typical-containing T11 building types |

### Phase Z.E — Gate extension + ship (5 tasks, ~10-12 commits)

| Task | Model | Deliverable |
|---|---|---|
| Z.E.1 | Sonnet | Extend `scripts/validate-examples.py` Pass 5 to validate both new catalogues (room-types-uniclass-sl/*.json + building-types-t11/*.json); update Lint 5 canonical membership to include SL canonical_ids |
| Z.E.2 | Sonnet | CHANGELOG entry + memory file `sprint-Z-dual-taxonomy-shipped.md` + MEMORY.md index + CLAUDE.md tally bump |
| Z.E.3 | Opus | Final 8-check fence + 5% fabrication spot-check (SL codes against NBS Uniclass mirror; T11 codes against pdfcoffee mirror) |
| Z.E.4 | Sonnet | (Conditional) Fix-pass per Z.E.3 verdict |
| Z.E.5 | — | Push deferred to user authorisation |

## 7. Cost estimate

- 18 implementer commits + ~5-8 fix-passes + 4 portion/spec commits = **~50-60 total**
- 2-3 sessions of execution (similar to Sprint X mega-sprint scale)

## 8. Definition of done

1. Schema extended with `taxonomy_source` discriminator; conditional requirements for `omniclass_code` vs `uniclass_code`
2. All 290 Sprint X entries retroactively carry `taxonomy_source: "OmniClass-Table-13"` (back-compat sweep)
3. 7 Uniclass SL per-category files shipped (~260 entries total target)
4. 1 OmniClass T11 building-types file shipped (~50-80 entries)
5. SL → T11 cross-references populated where applicable
6. cross_references back-filled on SL + T11 entries (BS EN 12464-1 / ASHRAE 90.1 / ASHRAE 62.1; cibse_lg + nrm2 stay null per Sprint X discipline)
7. Gate extended to validate both new catalogues; Lint 5 canonical membership extended to include SL canonical_ids
8. CHANGELOG + memory + tally bumped
9. Final 8-check fence + 5% fabrication spot-check PASS
10. Push deferred to user authorisation

## 9. Risk surfaces

1. **Uniclass SL public mirror coverage** — NBS Source is canonical but may be partial-access or require account. Fallback: designingbuildings.co.uk Uniclass coverage + GOV.UK BIM Level 2 documentation. If coverage <70% in a category, ship partial + honest disclosure (Sprint X precedent).
2. **OmniClass T11 mirror coverage** — same risk as T13. pdfcoffee + scribd mirrors confirmed for T13; assume similar exists for T11; verify at Z.A.0.
3. **Schema dual-taxonomy complexity** — conditional `allOf` requirements for `omniclass_code` vs `uniclass_code` add Lint 5 complexity. Mitigation: test fixtures cover both branches.
4. **Existing Sprint X entries back-compat** — Z.A.3 sweep MUST not regress any of 290 entries. Mitigation: pure additive (add taxonomy_source field, change nothing else).
5. **Sprint Z total size** — at 50-60 commits this is larger than originally pitched. Mitigation: 5-phase split allows multi-session execution; each phase ships discrete value.
6. **Uniclass SL code format drift** — Uniclass 2015 vs Uniclass 2 vs older editions may use different code patterns. Lock to Uniclass 2015 SL at Z.A.0 provenance; document edition.

## 10. Process discipline (locked)

- Sonnet for mechanical / Opus for judgment (per `[[feedback-no-haiku-sonnet-opus-only]]`)
- Two-stage Opus review per task + fix-pass commits (Sprint X/D4/D5 precedent)
- Citation hygiene: every entry cites Uniclass SL or OmniClass T11 verbatim from declared mirror
- Banned tokens inherited: §526.2 / §433.2 / OZEV / 3rd Edition / Reg 559 / Em_room / "average room lux"
- No-trim per `[[feedback-no-trim-non-consequential]]`
- 8-check verification fence + 5% fabrication spot-check at Z.E.3
- Push deferred to user authorisation per CLAUDE.md shared-state rule

## 11. Out of scope (deferred)

- **CIBSE LG10 (residential)** + CIBSE LG7 (offices) + CIBSE LG1 (industrial) + Guide A + NRM2 — paid CIBSE/RICS membership required. Sprint Y when access granted.
- **OmniClass T13 newer editions (2019, 2024)** that may add kitchens / offices to T13 — investigated and deferred; current Sprint X 2012-05-16 transcription stands.
- **Full Uniclass coverage** — Sprint Z transcribes only the 7 missing-from-T13 categories. Comprehensive Uniclass SL coverage (~1000 entries) deferred to future Sprint when needed.
- **F.1 retrofit further changes** — Room.type pattern already supports SL canonical_ids (snake_case dotted format). No additional F.1 work needed.

## 12. Sprint sequence (post-Z)

```
Sprint X ✓ pushed (290 T13 room types; pushed 23556eb..18deb71)
       ↓
Sprint Z (this) — Uniclass SL + T11 dual taxonomy (~50-60 commits)
       ↓
Sprint F RESUMES at F.4 — ORCHESTRATION.md now references all 3 catalogues (T13 + SL + T11)
       ├── F.4 ORCHESTRATION.md
       ├── F.5 4-pass gate + 4 lint sub-passes
       ├── F.6 8 existing manifests validation
       ├── F.7 7-check fence
       ├── F.8 Final integration review
       └── F.9 Push
       ↓
Sprint W1 (lighting-layout + small-power grounding)
       ↓
Sprint W2 (5 remaining skills grounding)
```
