# Sprint F — Foundation: SkillInput Contract Grounding Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Land the foundation layer of the public skill-orchestration contract — `SkillInput` schema, manifest metaschema, `grounded_source` two-tier validation, `ORCHESTRATION.md`, and the extended 4-pass golden CI gate with 4 new lint sub-passes — BEFORE any per-skill migration (W1 / W2 land in later sprints).

**Architecture:** Foundation-only sprint. No skill manifests or inputs.json files in `electrical/` get touched yet (W1/W2 will). All work lands in `shared/schemas/core/` + repo root + `scripts/validate-examples.py`. The 4-pass gate becomes the contract enforcer for all subsequent migration sprints.

**Tech Stack:**
- JSON Schema Draft-07 (matches existing skill schemas)
- Markdown for reference docs + ORCHESTRATION.md
- Python stdlib for `scripts/validate-examples.py` extensions (no third-party deps per `[[runtime-project-boundary]]`)
- Existing golden CI gate (currently 3-pass; this sprint extends to 4-pass + 4 lint sub-passes)

**Source spec:** [`docs/superpowers/specs/2026-06-05-skillinput-contract-grounding-design.md`](../specs/2026-06-05-skillinput-contract-grounding-design.md) (commit `2dd01f1`).
**Pattern parent:** [`docs/superpowers/plans/2026-06-03-lighting-layout-v1.7-task-ambient-3d-sprint.md`](2026-06-03-lighting-layout-v1.7-task-ambient-3d-sprint.md) (D5 sprint that shipped 31 commits clean on 2026-06-05).
**Verified standards files referenced by Foundation deliverables:**
- `shared/standards/lighting/BSEN12464/lux-levels.json` (27 canonical room.type values; F.1 enum source)
- `shared/standards/lighting/BSEN12464/area-definitions.json` (D5 artefact; referenced for room.type taxonomy justification)

---

## Sprint discipline (locked, mirrors D4/D5)

- Sonnet for mechanical (JSON Schema authoring, harness extension, metadata edits) per `[[feedback-no-haiku-sonnet-opus-only]]`
- Opus for judgment (SkillInput reference modelling, ORCHESTRATION.md authoring, final integration review)
- **Two-stage Opus review after every implementer task** + fix-pass commit when HIGH/CRITICAL findings surface. D5 history: 0 fix-passes in clean sprint; budget for ~3-5 in Sprint F given its newer terrain.
- **No banned tokens** anywhere: §526.2 / §433.2 / OZEV / 3rd Edition / Reg 559 / Em_room / "average room lux" (inherited from D5).
- Pre-ship **Sonnet 7-check verification fence** (F.7 task) per spec §9 Sprint F pre-ship fence.
- Final cross-sprint Opus integration review (F.8 task) — PASS / SHIP-WITH-NOTED-CONCERNS / FIX-FIRST verdict.
- Push deferred to user authorisation per CLAUDE.md "shared state" rule (F.9 task).
- `[[feedback-no-trim-non-consequential]]` — raise maxLength caps if needed; do NOT trim engineering content.

### Estimated commit count: 12-15

- 10 implementer commits (F.0 through F.9)
- ~3-5 fix-pass commits
- 3 portion commits for this plan doc
- 1 spec commit already done (`2dd01f1`)

---

## File structure

### Created (NEW files in `shared/schemas/core/`)

```
shared/schemas/core/
├── skill-input.schema.json          # F.1 NEW; Draft-07 metaschema for orchestrator → skill payload
├── skill-input.reference.md         # F.1 NEW; companion reference with BIM/IFC justification
└── skill-manifest.schema.json       # F.2 NEW; Draft-07 metaschema for skill.manifest.json
```

### Created (NEW files at repo root)

```
draftsman-skills/
├── ORCHESTRATION.md                  # F.4 NEW; public-facing iteration contract for arbitrary agents
└── docs/superpowers/specs/skill-input-design-rationale.md  # F.0 NEW; engineering walk + BIM/IFC angle (input to F.1)
```

### Modified (existing files)

```
shared/schemas/core/
└── inputs.schema.json               # F.3 MODIFY; add grounded_source two-tier validation

scripts/
└── validate-examples.py             # F.5 MODIFY; extend 3-pass → 4-pass + 4 new lint sub-passes

CHANGELOG.md (or shared/CHANGELOG.md if it exists)  # F.7 MODIFY or NEW
CLAUDE.md                              # F.7 MODIFY; note 4-pass gate + foundation layer
```

### Memory + index (outside repo)

```
/Users/linus/.claude/projects/-Users-linus-Desktop-DraftsMan-SKills-draftsman-skills/memory/
├── sprint-F-foundation-shipped.md    # F.7 NEW
└── MEMORY.md                          # F.7 APPEND index line
```

---

## Phase F — Foundation (10 implementer tasks, ~12-15 commits incl. fix-passes)

Goal: land the public skill-orchestration contract layer. F.0 → F.4 author the contract surface. F.5 wires it into the gate. F.6 validates against existing state. F.7 finalises docs + memory. F.8 reviews. F.9 hands off to user for push.

### Task F.0: Author SkillInput reference rationale (design groundwork before F.1)

**Files:**
- Create: `docs/superpowers/specs/skill-input-design-rationale.md`

**Why Opus:** Design judgement; BIM/IFC justification anchoring; needs to argue WHY snake_case `room.type` enum + tagged-union by scope + per-skill placement_convention are the right shape before F.1 commits to JSON Schema.

- [ ] **Step 1: Read the spec sections that constrain the schema shape**

Run:
```bash
sed -n '88,150p' docs/superpowers/specs/2026-06-05-skillinput-contract-grounding-design.md
```

Expected: read §6.1 (SkillInput schema) + §6.3 (grounded_source two-tier) + §8 Risk 4 (room.type normalization). Confirm the contract surface before authoring rationale.

- [ ] **Step 2: Confirm canonical room.type values from the standards file**

Run:
```bash
python3 -c "
import json
d = json.load(open('shared/standards/lighting/BSEN12464/lux-levels.json'))
keys = []
for cat, sub in d.items():
    if cat.startswith('_'): continue
    if isinstance(sub, dict):
        for k in sub:
            if not k.startswith('_'):
                keys.append(f'{cat}.{k}')
print(f'total canonical room.type values: {len(keys)}')
for k in keys: print(' ', k)
"
```

Expected: 27 values across 6 categories (office, circulation, sanitary, industrial, healthcare, education, retail).

- [ ] **Step 3: Author the rationale doc**

Create `docs/superpowers/specs/skill-input-design-rationale.md`:

```markdown
# SkillInput Design Rationale

**Date:** 2026-06-05
**Sprint:** F (Foundation) — input to F.1 SkillInput schema authoring
**Companion to:** `shared/schemas/core/skill-input.schema.json` (authored at F.1)

## Why a tagged-union by scope

The orchestrator → skill payload changes shape by `manifest.scope`:

- `scope: room` → payload has `room` (singular, the unit being processed) + `floor` (parent context)
- `scope: floor` → payload has `floor` + `rooms[]` (all rooms in the floor for cross-room reasoning at the floor level)
- `scope: building` → payload has `building` + `floors[]` (all floors)

Tagged-union (`oneOf` with `scope` const discriminator) makes the shape self-describing. An orchestrator picks the right branch by reading the manifest's `scope` field. A skill never gets a shape it isn't designed for.

## Why `room.type` as snake_case enum

The skill's standards lookup tables (e.g. `shared/standards/lighting/BSEN12464/lux-levels.json`) use snake_case keys: `office.open_plan`, `circulation.lobby`, `industrial.warehouse_high`. If `room.type` arrives as freeform string (e.g. "Open Plan Office" or "openPlanOffice"), the lookup fails silently.

Locking `room.type` to a snake_case enum matching the 27 canonical values in `lux-levels.json` forces orchestrators to normalize BEFORE the skill runs. Schema-level fail-fast prevents silent lookup misses.

The 27 canonical values:

- **office.*** (6): open_plan, private_office, conference, reception_desk, filing_copying, archive
- **circulation.*** (4): main_corridor, link_corridor, lobby, staircase
- **sanitary.*** (2): toilet_wc, first_aid
- **industrial.*** (5): warehouse_low, warehouse_high, workshop, car_park_bays, car_park_ramp
- **healthcare.*** (3): ward_general, ward_examination, consultation
- **education.*** (4): classroom, classroom_board, laboratory, sports_hall
- **retail.*** (3): general, high_emphasis, checkout

This enum is the cross-cutting room.type taxonomy for ALL skills (not just lighting). Other skills extending the taxonomy add new keys to `lux-levels.json` first; the SkillInput enum follows.

## Why placement_convention is a separate manifest field

A skill's `scope` says what unit it processes; `placement_convention` says what coordinate frame the output uses. These are orthogonal concerns:

- A room-scope skill MAY emit in room-local mm (lighting-layout, small-power, fire-alarm) → `placement_convention: room_local_mm`
- A building-scope skill MAY emit in site-local mm (earthing) → `placement_convention: site_local_mm`
- A building-scope skill MAY emit topology-only (sld) → `placement_convention: none_topological`
- A floor-scope skill MAY emit topology-only (schematic) → `placement_convention: none_topological`

Conflating scope and placement into one field would force false equivalences (every room-scope must be spatial; every building-scope must be site-local). The 4-value placement enum + scope independence supports legitimate non-spatial outputs.

## BIM/IFC alignment (ISO 16739)

`IfcLocalPlacement` defines element positions relative to their containing space (parent-relative). The 4-value placement_convention mirrors this:

- `room_local_mm` ≈ position relative to `IfcSpace`
- `floor_local_mm` ≈ position relative to `IfcBuildingStorey`
- `site_local_mm` ≈ position relative to `IfcSite`
- `none_topological` ≈ no spatial placement; element is logical (e.g. `IfcElectricDistributionPoint` in a schematic)

This makes our outputs IFC-export-friendly when the runtime serializes to BIM. Traditional 2D CAD (world coords) is a downstream rendering concern, not a contract concern.

## Why two-tier `grounded_source` validation

The closed `room.*` enum prevents typos like `room.bbbox.length` from silently passing as "the runtime will figure it out." Strict enum closure = fail loudly at our gate, before the orchestrator ever sees the binding.

The `project.*` enum is closed for known canonical facts (jurisdiction, building_type, code_basis, units, ceiling_height_mm, project_id) BUT allows `project.<custom>` via pattern fallback for project-specific facts a particular orchestrator might track. The pattern fallback is loud — the manifest-lint pass flags every custom binding for orchestrator-confirmation.

Two-tier discipline = strict where we know the taxonomy, flagged-but-allowed where extension is legitimate.

## Reference orchestrators

This rationale informs:

1. F.1 `skill-input.schema.json` JSON Schema authoring
2. F.4 `ORCHESTRATION.md` worked example narration
3. W1 + W2 per-skill migration tasks (which manifest fields go where)
4. Future MCP-server bindings exposing draftsman-skills via tool calls
```

- [ ] **Step 4: Validate file renders + committed cleanly**

Run:
```bash
wc -l docs/superpowers/specs/skill-input-design-rationale.md
```

Expected: ~80-100 lines.

- [ ] **Step 5: Run golden CI gate (docs not validated)**

Run:
```bash
python3 scripts/validate-examples.py 2>&1 | tail -3
```

Expected: aggregate unchanged.

- [ ] **Step 6: Commit**

```bash
git add docs/superpowers/specs/skill-input-design-rationale.md
git commit -m "feat(spec): F.0 SkillInput design rationale — BIM/IFC justification + 27-value room.type enum + two-tier grounded_source discipline (input to F.1)"
```

### Task F.1: Write `skill-input.schema.json` + companion reference

**Files:**
- Create: `shared/schemas/core/skill-input.schema.json`
- Create: `shared/schemas/core/skill-input.reference.md`

**Why Sonnet:** Mechanical JSON Schema authoring against the F.0 rationale; structure is dictated by spec §6.1.

- [ ] **Step 1: Read F.0 rationale + spec §6.1 to confirm schema shape**

Run:
```bash
cat docs/superpowers/specs/skill-input-design-rationale.md | head -80
sed -n '88,140p' docs/superpowers/specs/2026-06-05-skillinput-contract-grounding-design.md
```

Expected: confirm tagged-union by scope + room.type enum + ProjectFacts.additionalProperties.

- [ ] **Step 2: Author `skill-input.schema.json`**

Create `shared/schemas/core/skill-input.schema.json`:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "draftsman-skills/skill-input.schema.json",
  "title": "SkillInput",
  "description": "Payload an orchestrator constructs per skill invocation. Tagged-union by scope (room | floor | building). See ORCHESTRATION.md for worked examples.",
  "oneOf": [
    { "$ref": "#/definitions/RoomScopeInput" },
    { "$ref": "#/definitions/FloorScopeInput" },
    { "$ref": "#/definitions/BuildingScopeInput" }
  ],
  "definitions": {
    "RoomScopeInput": {
      "type": "object",
      "required": ["scope", "floor", "room", "project_facts"],
      "properties": {
        "scope": { "const": "room" },
        "floor": { "$ref": "#/definitions/Floor" },
        "room": { "$ref": "#/definitions/Room" },
        "project_facts": { "$ref": "#/definitions/ProjectFacts" },
        "engineer_inputs": { "type": "object", "description": "Engineer-supplied items NOT covered by grounded_source bindings. Orchestrator merges engineer_inputs over grounded values." }
      },
      "additionalProperties": false
    },
    "FloorScopeInput": {
      "type": "object",
      "required": ["scope", "floor", "rooms", "project_facts"],
      "properties": {
        "scope": { "const": "floor" },
        "floor": { "$ref": "#/definitions/Floor" },
        "rooms": { "type": "array", "items": { "$ref": "#/definitions/Room" } },
        "project_facts": { "$ref": "#/definitions/ProjectFacts" },
        "engineer_inputs": { "type": "object" }
      },
      "additionalProperties": false
    },
    "BuildingScopeInput": {
      "type": "object",
      "required": ["scope", "building", "floors", "project_facts"],
      "properties": {
        "scope": { "const": "building" },
        "building": { "$ref": "#/definitions/Building" },
        "floors": { "type": "array", "items": { "$ref": "#/definitions/Floor" } },
        "project_facts": { "$ref": "#/definitions/ProjectFacts" },
        "engineer_inputs": { "type": "object" }
      },
      "additionalProperties": false
    },
    "Building": {
      "type": "object",
      "required": ["id"],
      "properties": {
        "id": { "type": "string" },
        "label": { "type": "string" }
      },
      "additionalProperties": true
    },
    "Floor": {
      "type": "object",
      "required": ["id"],
      "properties": {
        "id": { "type": "string" },
        "building_label": { "type": "string" },
        "level_name": { "type": "string" },
        "origin_xy_mm": { "type": "array", "items": { "type": "number" }, "minItems": 2, "maxItems": 2, "description": "Floor origin in site coords (mm). Used for floor_local_mm placement transform." }
      },
      "additionalProperties": true
    },
    "Room": {
      "type": "object",
      "required": ["room_id", "type", "area_m2", "bbox"],
      "properties": {
        "room_id": { "type": "string" },
        "type": {
          "type": "string",
          "enum": [
            "office.open_plan", "office.private_office", "office.conference", "office.reception_desk", "office.filing_copying", "office.archive",
            "circulation.main_corridor", "circulation.link_corridor", "circulation.lobby", "circulation.staircase",
            "sanitary.toilet_wc", "sanitary.first_aid",
            "industrial.warehouse_low", "industrial.warehouse_high", "industrial.workshop", "industrial.car_park_bays", "industrial.car_park_ramp",
            "healthcare.ward_general", "healthcare.ward_examination", "healthcare.consultation",
            "education.classroom", "education.classroom_board", "education.laboratory", "education.sports_hall",
            "retail.general", "retail.high_emphasis", "retail.checkout"
          ],
          "description": "Snake_case room type per shared/standards/lighting/BSEN12464/lux-levels.json. Orchestrators MUST normalize before passing. See skill-input-design-rationale.md for the 27-value taxonomy."
        },
        "area_m2": { "type": "number", "minimum": 0 },
        "bbox": {
          "type": "object",
          "required": ["length", "width"],
          "properties": {
            "length": { "type": "number", "minimum": 0, "description": "Room length in metres (orchestrator's drawing units; convert to mm in skill if needed)." },
            "width": { "type": "number", "minimum": 0, "description": "Room width in metres." },
            "min_xy": { "type": "array", "items": { "type": "number" }, "minItems": 2, "maxItems": 2, "description": "Bottom-left corner of bbox in floor coords (m). Used for room_local_mm placement transform." }
          },
          "additionalProperties": true
        },
        "polygon": {
          "type": "array",
          "items": { "type": "array", "items": { "type": "number" }, "minItems": 2, "maxItems": 2 },
          "description": "Room polygon vertices in floor-local coords (m). Closed polygon (last == first)."
        },
        "centroid": {
          "type": "object",
          "properties": {
            "x": { "type": "number" },
            "y": { "type": "number" }
          }
        },
        "mounting_height": { "type": "number", "minimum": 0, "description": "Working plane / mounting reference height in mm if known per-room." }
      },
      "additionalProperties": true
    },
    "ProjectFacts": {
      "type": "object",
      "properties": {
        "building_type": { "type": "string" },
        "code_basis": { "type": "string" },
        "jurisdiction": { "type": "string", "enum": ["GB", "KE", "INT", "US"], "description": "Standards jurisdiction per CLAUDE.md (GB=BS 7671 / KE=KS 1700 / INT=IEC 60364 / US=NEC)." },
        "units": { "type": "string", "enum": ["metric", "imperial"] },
        "ceiling_height_mm": { "type": "number", "minimum": 0 },
        "project_id": { "type": "string" }
      },
      "additionalProperties": true
    }
  }
}
```

- [ ] **Step 3: Author `skill-input.reference.md` companion**

Create `shared/schemas/core/skill-input.reference.md`:

```markdown
# SkillInput Reference

Companion to `skill-input.schema.json`. Each field explained with engineering context.

## Tagged-union by scope

The payload shape changes by `manifest.scope`:

- **`scope: room`** → orchestrator passes ONE room (the unit being processed) + parent floor context + project facts
- **`scope: floor`** → orchestrator passes ONE floor + ALL rooms in that floor (skill reasons across rooms within the floor) + project facts
- **`scope: building`** → orchestrator passes ONE building + ALL floors + project facts

The `scope` field is the `oneOf` discriminator. Schema validation fails if shape doesn't match scope.

## Building / Floor / Room fields

### Building
- `id`: unique building identifier (e.g. "BLD-001")
- `label`: human-readable name (e.g. "Office Block A")

### Floor
- `id`: unique floor identifier (e.g. "FL-01" or "L1")
- `building_label`: parent building label
- `level_name`: human-readable level (e.g. "Ground Floor", "Mezzanine")
- `origin_xy_mm`: floor origin in site coordinates (mm) — used for `floor_local_mm` placement transforms

### Room
- `room_id`: unique room identifier within the floor
- `type`: snake_case room type from the 27-value enum (see rationale doc)
- `area_m2`: net internal area in square metres
- `bbox`: bounding box with `length` + `width` (m) + optional `min_xy` (bottom-left corner in floor coords)
- `polygon`: closed polygon vertices in floor-local metres
- `centroid`: room centroid {x, y} in floor-local metres
- `mounting_height`: working-plane/mounting reference in mm if known per-room

## ProjectFacts

Canonical project-level facts (closed list) + `additionalProperties: true` for project-specific custom facts that an orchestrator may track:

- `building_type`: e.g. "commercial_office", "warehouse", "residential_dwelling"
- `code_basis`: e.g. "BS 7671:2018+A2:2022", "NEC 2023", "IEC 60364"
- `jurisdiction`: closed enum (GB / KE / INT / US) per CLAUDE.md
- `units`: closed enum (metric / imperial)
- `ceiling_height_mm`: project-default ceiling height (mm)
- `project_id`: project identifier

Custom facts via `additionalProperties: true` (e.g. `project.client_name`, `project.briefing_meeting_date`) — orchestrator declares them when constructing SkillInput; manifest-side `grounded_source: "project.<custom>"` references them.

## engineer_inputs

Items NOT covered by `grounded_source` bindings. The orchestrator collects these from the engineer (UI / form / CLI prompt) and passes them to the skill alongside grounded values.

Precedence order at invocation:
1. `engineer_inputs.<id>` (highest priority — explicit override)
2. Grounded value from SkillInput (resolved by `grounded_source` binding)
3. Default value from `inputs.json` (lowest priority)

## BIM/IFC alignment

This shape mirrors ISO 16739 IfcLocalPlacement parent-relative positioning:
- `Building` ≈ `IfcBuilding`
- `Floor` ≈ `IfcBuildingStorey`
- `Room` ≈ `IfcSpace`

See `docs/superpowers/specs/skill-input-design-rationale.md` for the full BIM/IFC justification.
```

- [ ] **Step 4: Validate JSON parses + reference renders**

Run:
```bash
python3 -c "
import json
s = json.load(open('shared/schemas/core/skill-input.schema.json'))
print('parse OK; oneOf branches:', len(s.get('oneOf', [])))
print('definitions:', sorted(s.get('definitions', {}).keys()))
print('Room.type enum length:', len(s['definitions']['Room']['properties']['type']['enum']))
"
wc -l shared/schemas/core/skill-input.reference.md
```

Expected: `parse OK; oneOf branches: 3`; definitions include Building, Floor, Room, ProjectFacts, RoomScopeInput, FloorScopeInput, BuildingScopeInput; `Room.type enum length: 27`; reference ~80 lines.

- [ ] **Step 5: Run golden CI gate (still 3-pass at this point; new file not yet wired in)**

Run:
```bash
python3 scripts/validate-examples.py 2>&1 | tail -3
```

Expected: aggregate unchanged (354/354 from end of D5).

- [ ] **Step 6: Commit**

```bash
git add shared/schemas/core/skill-input.schema.json shared/schemas/core/skill-input.reference.md
git commit -m "feat(schemas): F.1 NEW skill-input.schema.json + reference — tagged-union by scope with 27-value room.type enum (per skill-input-design-rationale F.0)"
```

### Task F.2: Write `skill-manifest.schema.json` metaschema

**Files:**
- Create: `shared/schemas/core/skill-manifest.schema.json`

**Why Sonnet:** Mechanical JSON Schema authoring; structure dictated by spec §6.2.

- [ ] **Step 1: Inspect existing manifest field set across 8 skills**

Run:
```bash
python3 -c "
import json
fields = set()
for skill in ['lighting-layout', 'small-power', 'fire-alarm', 'db-layout', 'arc-flash-labelling', 'schematic', 'sld', 'earthing']:
    try:
        m = json.load(open(f'electrical/{skill}/skill.manifest.json'))
        fields.update(m.keys())
    except FileNotFoundError:
        print(f'  $skill: manifest not found')
print('union of fields across 8 manifests:')
for f in sorted(fields): print(' ', f)
"
```

Expected: list of ~20-25 manifest fields (skill, version, discipline, subdiscipline, chat_type, description, status, licence, inputs_path, outputs, output_schema, produces_intents, produces_intent_schema, consumes_intents, standards, ontology, symbols, calculations, prompts, evals, examples, validation, rules, constraints).

- [ ] **Step 2: Author `skill-manifest.schema.json`**

Create `shared/schemas/core/skill-manifest.schema.json`:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "draftsman-skills/skill-manifest.schema.json",
  "title": "SkillManifest",
  "description": "Metaschema for skill.manifest.json. Required core fields + optional scope/placement_convention enums. additionalProperties: true preserves existing manifest fields not yet enumerated; manifest-lint sub-pass flags unknowns.",
  "type": "object",
  "required": ["skill", "version", "discipline", "produces_intents", "consumes_intents"],
  "properties": {
    "skill": { "type": "string", "description": "Skill identifier (matches directory name, e.g. 'lighting-layout')." },
    "version": { "type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$", "description": "Semantic version (major.minor.patch)." },
    "discipline": { "type": "string", "enum": ["electrical", "mechanical", "plumbing", "fire-protection", "coordination", "documents"] },
    "subdiscipline": { "type": "string" },
    "chat_type": { "type": "string", "description": "Skill's chat archetype (e.g. 'drawing-skill', 'calc-skill', 'document-skill')." },
    "description": { "type": "string", "minLength": 10 },
    "status": { "type": "string", "enum": ["stub", "beta", "production"] },
    "scope": {
      "type": "string",
      "enum": ["room", "floor", "building"],
      "description": "Iteration unit. Orchestrator constructs ONE SkillInput per unit per invocation. Optional for back-compat with un-migrated skills; legacy path activates when absent."
    },
    "placement_convention": {
      "type": "string",
      "enum": ["room_local_mm", "floor_local_mm", "site_local_mm", "none_topological"],
      "description": "Coordinate frame for emitted positions. ISO 16739 IfcLocalPlacement-aligned. Optional for back-compat."
    },
    "licence": { "type": "string" },
    "inputs_path": { "type": "string" },
    "outputs": { "type": "array" },
    "output_schema": { "type": "string" },
    "produces_intents": { "type": "array" },
    "produces_intent_schema": { "type": "string" },
    "consumes_intents": { "type": "array" },
    "standards": { "type": "array" },
    "ontology": { "type": "array" },
    "symbols": { "type": "array" },
    "calculations": { "type": "array" },
    "prompts": { "type": "object" },
    "evals": { "type": "array" },
    "examples": { "type": "array" },
    "validation": { "type": "object" },
    "rules": { "type": "array" },
    "constraints": { "type": "array" }
  },
  "additionalProperties": true
}
```

- [ ] **Step 3: Validate parses + enums correct**

Run:
```bash
python3 -c "
import json
s = json.load(open('shared/schemas/core/skill-manifest.schema.json'))
print('parse OK')
print('required:', s.get('required'))
print('scope enum:', s['properties']['scope']['enum'])
print('placement_convention enum:', s['properties']['placement_convention']['enum'])
print('status enum:', s['properties']['status']['enum'])
print('discipline enum:', s['properties']['discipline']['enum'])
print('additionalProperties:', s.get('additionalProperties'))
"
```

Expected: required `[skill, version, discipline, produces_intents, consumes_intents]`; scope enum `[room, floor, building]`; placement_convention enum 4 values; status enum 3 values; additionalProperties True.

- [ ] **Step 4: Gates**

Run:
```bash
python3 scripts/validate-examples.py 2>&1 | tail -3
```

Expected: aggregate unchanged (metaschema not yet wired into the gate).

- [ ] **Step 5: Commit**

```bash
git add shared/schemas/core/skill-manifest.schema.json
git commit -m "feat(schemas): F.2 NEW skill-manifest.schema.json metaschema — scope + placement_convention enums + 4-pass-gate-ready (additionalProperties true; lint pass flags unknown fields at F.5)"
```

### Task F.3: Extend `inputs.schema.json` with `grounded_source` two-tier validation

**Files:**
- Modify: `shared/schemas/core/inputs.schema.json`

**Why Sonnet:** Mechanical addition of one field; structure dictated by spec §6.3.

- [ ] **Step 1: Inspect current inputs.schema.json InputItem fields**

Run:
```bash
python3 -c "
import json
s = json.load(open('shared/schemas/core/inputs.schema.json'))
item = s['definitions'].get('InputItem', {})
print('InputItem additionalProperties:', item.get('additionalProperties'))
print('properties:', list(item.get('properties', {}).keys()))
"
```

Expected: `additionalProperties: false`; properties include id, label, hint, answer_type, options, default, required, validator, depends_on, project_fact_candidate, item_schema.

- [ ] **Step 2: Add `grounded_source` property to InputItem.properties**

Edit `shared/schemas/core/inputs.schema.json`. Locate `definitions.InputItem.properties` and APPEND (preserve all existing properties):

```json
"grounded_source": {
  "description": "Closed-grammar binding to a SkillInput field. Orchestrator auto-fills this item from the parsed model. Two-tier validation: closed enum for canonical room.* + project.* bindings; pattern fallback for project.<custom> bindings (manifest-lint flags those for orchestrator-confirmation).",
  "oneOf": [
    {
      "type": "string",
      "enum": [
        "room.type",
        "room.area_m2",
        "room.bbox.length",
        "room.bbox.width",
        "room.centroid.x",
        "room.centroid.y",
        "room.mounting_height",
        "room.polygon",
        "project.building_type",
        "project.code_basis",
        "project.jurisdiction",
        "project.units",
        "project.ceiling_height_mm",
        "project.project_id"
      ]
    },
    {
      "type": "string",
      "pattern": "^project\\.[a-z_]+$"
    }
  ]
}
```

- [ ] **Step 3: Validate parses + new property present**

Run:
```bash
python3 -c "
import json
s = json.load(open('shared/schemas/core/inputs.schema.json'))
item = s['definitions']['InputItem']
print('grounded_source present:', 'grounded_source' in item['properties'])
gs = item['properties'].get('grounded_source', {})
print('oneOf branches:', len(gs.get('oneOf', [])))
print('tier 1 enum length:', len(gs['oneOf'][0].get('enum', [])))
print('tier 2 pattern:', gs['oneOf'][1].get('pattern'))
"
```

Expected: `grounded_source present: True`; oneOf 2 branches; tier 1 enum 14 values; tier 2 pattern `^project\\.[a-z_]+$`.

- [ ] **Step 4: Run golden CI gate Pass 3 (existing inputs.json files must still pass)**

Run:
```bash
python3 scripts/validate-examples.py 2>&1 | tail -3
```

Expected: aggregate unchanged. Pass 3 still green (existing inputs.json files don't use `grounded_source` yet so the new optional field doesn't trigger).

- [ ] **Step 5: Commit**

```bash
git add shared/schemas/core/inputs.schema.json
git commit -m "feat(schemas): F.3 extend inputs.schema.json with grounded_source two-tier validation (closed enum for room.* + canonical project.* + pattern fallback for project.<custom>)"
```

### Task F.4: Write `ORCHESTRATION.md`

**Files:**
- Create: `ORCHESTRATION.md` (at repo root)

**Why Opus:** Authoring a public-facing contract reference; needs to read for non-DraftsMan agents (Claude CLI, MCP servers, future tooling); engineering content with worked example.

- [ ] **Step 1: Inspect a representative skill (lighting-layout v1.7.0) for the worked example shape**

Run:
```bash
python3 -c "
import json
m = json.load(open('electrical/lighting-layout/skill.manifest.json'))
print('version:', m['version'])
print('produces_intents:', m.get('produces_intents', []))
print('consumes_intents skill_ids:', [c.get('skill_id') for c in m.get('consumes_intents', [])])
i = json.load(open('electrical/lighting-layout/inputs.json'))
items = i.get('items', i.get('inputs', []))
print('input items (id/required):')
for x in items[:15]:
    print(f'  - {x.get(\"id\")}: required={x.get(\"required\", False)}')
"
```

Expected: see current lighting-layout inputs to author a grounded version in the worked example.

- [ ] **Step 2: Author `ORCHESTRATION.md`**

Create `ORCHESTRATION.md` at repo root:

```markdown
# Skill Orchestration Contract

> Public-facing contract for any orchestrator consuming `draftsman-skills`. DraftsMan-runtime is one consumer; this contract is designed for arbitrary AI agents, MCP servers, CLI tools, and future tooling.

This document explains how to:

1. Read a skill's `manifest.json` to discover its `scope` and `placement_convention`
2. Construct the `SkillInput` payload per `shared/schemas/core/skill-input.schema.json`
3. Resolve `grounded_source` bindings from the parsed building model
4. Merge engineer inputs over grounded values with the correct precedence
5. Invoke the skill once per unit (no iteration inside the skill)
6. Transform skill outputs from local coords to real coords via `placement_convention`
7. (Optional) Expose the skill as an MCP tool

## 1. The contract

### What skills declare

In `skill.manifest.json`:

```json
{
  "skill": "lighting-layout",
  "version": "1.8.0",
  "scope": "room",
  "placement_convention": "room_local_mm",
  "...": "..."
}
```

In `inputs.json`:

```json
{
  "items": [
    { "id": "room_type", "grounded_source": "room.type" },
    { "id": "ceiling_height_mm", "answer_type": "int", "required": true },
    { "id": "luminaire_lumens", "answer_type": "int", "required": true }
  ]
}
```

### What orchestrators provide

A `SkillInput` payload validating against `shared/schemas/core/skill-input.schema.json`:

```json
{
  "scope": "room",
  "floor": { "id": "FL-01", "level_name": "Ground Floor" },
  "room": {
    "room_id": "R-101",
    "type": "office.open_plan",
    "area_m2": 96.0,
    "bbox": { "length": 12.0, "width": 8.0, "min_xy": [0, 0] },
    "polygon": [[0,0], [12,0], [12,8], [0,8], [0,0]],
    "centroid": { "x": 6.0, "y": 4.0 }
  },
  "project_facts": {
    "jurisdiction": "GB",
    "building_type": "commercial_office",
    "code_basis": "BS 7671:2018+A2:2022",
    "units": "metric"
  },
  "engineer_inputs": {
    "ceiling_height_mm": 3500,
    "luminaire_lumens": 5000
  }
}
```

## 2. Iteration pseudocode

The skill is invoked ONCE PER UNIT. The orchestrator owns iteration:

### Room-scope iteration

```python
for floor in building.floors:
    for room in floor.rooms:
        payload = {
            "scope": "room",
            "floor": floor_to_dict(floor),
            "room": room_to_dict(room),
            "project_facts": project_facts,
            "engineer_inputs": collect_engineer_inputs(skill)
        }
        grounded_payload = apply_grounded_bindings(skill.inputs_json, payload)
        skill_output = invoke_skill(skill, grounded_payload)
        place_output(skill_output, room.polygon, skill.placement_convention)
```

### Floor-scope iteration

```python
for floor in building.floors:
    payload = {
        "scope": "floor",
        "floor": floor_to_dict(floor),
        "rooms": [room_to_dict(r) for r in floor.rooms],
        "project_facts": project_facts,
        "engineer_inputs": collect_engineer_inputs(skill)
    }
    skill_output = invoke_skill(skill, apply_grounded_bindings(skill.inputs_json, payload))
    place_output(skill_output, floor, skill.placement_convention)
```

### Building-scope iteration

```python
payload = {
    "scope": "building",
    "building": building_to_dict(building),
    "floors": [floor_to_dict(f) for f in building.floors],
    "project_facts": project_facts,
    "engineer_inputs": collect_engineer_inputs(skill)
}
skill_output = invoke_skill(skill, apply_grounded_bindings(skill.inputs_json, payload))
place_output(skill_output, building, skill.placement_convention)
```

## 3. Grounding bindings

`grounded_source` on an `inputs.json` item tells the orchestrator how to resolve that input from the payload:

| Binding | Resolves to |
|---|---|
| `room.type` | `payload.room.type` (room-scope only) |
| `room.area_m2` | `payload.room.area_m2` |
| `room.bbox.length` | `payload.room.bbox.length` |
| `room.bbox.width` | `payload.room.bbox.width` |
| `room.centroid.x` | `payload.room.centroid.x` |
| `room.centroid.y` | `payload.room.centroid.y` |
| `room.mounting_height` | `payload.room.mounting_height` |
| `room.polygon` | `payload.room.polygon` |
| `project.building_type` | `payload.project_facts.building_type` |
| `project.jurisdiction` | `payload.project_facts.jurisdiction` |
| `project.code_basis` | `payload.project_facts.code_basis` |
| `project.units` | `payload.project_facts.units` |
| `project.ceiling_height_mm` | `payload.project_facts.ceiling_height_mm` |
| `project.project_id` | `payload.project_facts.project_id` |
| `project.<custom>` | `payload.project_facts.<custom>` (orchestrator MUST track) |

### Precedence order (highest → lowest)

1. `engineer_inputs.<id>` — explicit override (orchestrator-collected from engineer)
2. Grounded value from SkillInput (resolved via `grounded_source`)
3. Default value from `inputs.json` (lowest priority)

Pseudocode:

```python
def resolve_input(item, payload):
    if item["id"] in payload.get("engineer_inputs", {}):
        return payload["engineer_inputs"][item["id"]]
    if "grounded_source" in item:
        return resolve_binding(item["grounded_source"], payload)
    return item.get("default")
```

## 4. Worked example — lighting-layout

**Skill manifest (`electrical/lighting-layout/skill.manifest.json`):**

```json
{
  "skill": "lighting-layout",
  "version": "1.8.0",
  "scope": "room",
  "placement_convention": "room_local_mm"
}
```

**Skill inputs (`electrical/lighting-layout/inputs.json`, excerpt):**

```json
{
  "items": [
    { "id": "room_type", "grounded_source": "room.type" },
    { "id": "jurisdiction", "grounded_source": "project.jurisdiction" },
    { "id": "ceiling_height_mm", "answer_type": "int", "required": true },
    { "id": "luminaire_lumens", "answer_type": "int", "required": true },
    { "id": "controls_protocol", "answer_type": "enum", "options": ["DALI", "0-10V", "switching"] }
  ]
}
```

**Orchestrator constructs SkillInput per room:**

```json
{
  "scope": "room",
  "floor": { "id": "FL-01", "level_name": "Ground Floor", "origin_xy_mm": [0, 0] },
  "room": {
    "room_id": "R-101",
    "type": "office.open_plan",
    "area_m2": 96.0,
    "bbox": { "length": 12.0, "width": 8.0, "min_xy": [2.5, 1.0] },
    "polygon": [[2.5, 1.0], [14.5, 1.0], [14.5, 9.0], [2.5, 9.0], [2.5, 1.0]],
    "centroid": { "x": 8.5, "y": 5.0 }
  },
  "project_facts": {
    "jurisdiction": "GB",
    "building_type": "commercial_office",
    "code_basis": "BS 7671:2018+A2:2022",
    "units": "metric"
  },
  "engineer_inputs": {
    "ceiling_height_mm": 3500,
    "luminaire_lumens": 5000,
    "controls_protocol": "DALI"
  }
}
```

**Skill emits output (room-local mm):**

```json
{
  "drawing_type": "lighting-layout",
  "version": "1.8.0",
  "room": { "length_mm": 12000, "width_mm": 8000, "ceiling_height_mm": 3500 },
  "luminaires": [
    { "id": "L1", "x_mm": 2000, "y_mm": 2000, "mount_type": "recessed" },
    { "id": "L2", "x_mm": 4000, "y_mm": 2000, "mount_type": "recessed" },
    "..."
  ]
}
```

**Orchestrator transforms to real coords (placement_convention=room_local_mm):**

```python
real_x_m = room.bbox.min_xy[0] + (lum.x_mm / 1000.0)
real_y_m = room.bbox.min_xy[1] + (lum.y_mm / 1000.0)
# L1: real_x = 2.5 + 2.0 = 4.5 m; real_y = 1.0 + 2.0 = 3.0 m (floor coords)
```

## 5. Placement transforms

| `placement_convention` | Transform rule |
|---|---|
| `room_local_mm` | `real_xy_m = room.bbox.min_xy + (skill_output.x_mm / 1000, skill_output.y_mm / 1000)` |
| `floor_local_mm` | `real_xy_m = floor.origin_xy_mm/1000 + (skill_output.x_mm/1000, skill_output.y_mm/1000)` |
| `site_local_mm` | `real_xy_m = site.origin_xy_mm/1000 + (skill_output.x_mm/1000, skill_output.y_mm/1000)` |
| `none_topological` | No spatial transform. Render as topology graph (e.g. SLD circuit diagram). |

## 6. MCP integration hint

To expose a skill as an MCP tool, the server wraps the skill's interface as:

```typescript
{
  name: "draftsman_skill_<skill_name>",
  description: "<from skill.manifest.json.description>",
  inputSchema: SkillInputSchema  // shared/schemas/core/skill-input.schema.json
}
```

The MCP server's tool handler:
1. Receives a `SkillInput` payload from the calling agent
2. Validates against `skill-input.schema.json`
3. Looks up the skill's manifest + inputs.json
4. Resolves grounded bindings
5. Invokes the skill (typically via LLM prompt chain)
6. Returns the skill's IR output to the calling agent

This makes draftsman-skills first-class MCP-discoverable tools for Claude / any MCP-aware agent.

## 7. Back-compat

Skills WITHOUT `scope` + `placement_convention` declared in manifest run on the legacy path: orchestrator treats them as opaque single-invocation skills with no auto-grounding. This is the v1.7 default behaviour.

Skills WITH `scope` + `placement_convention` + `grounded_source` use the contract path: orchestrator iterates per unit, auto-fills bindings, transforms outputs.

The 4-pass gate at `scripts/validate-examples.py` validates both paths. Migrated skills must include at least one grounded-path eval (omits grounded items from engineer_inputs) per Sprint W1/W2 acceptance criteria.

## References

- `shared/schemas/core/skill-input.schema.json` — payload metaschema
- `shared/schemas/core/skill-manifest.schema.json` — manifest metaschema
- `shared/schemas/core/inputs.schema.json` — extended with `grounded_source`
- `docs/superpowers/specs/2026-06-05-skillinput-contract-grounding-design.md` — full design spec
- `docs/superpowers/specs/skill-input-design-rationale.md` — BIM/IFC + room.type enum justification
```

- [ ] **Step 3: Validate file renders + internal refs resolve**

Run:
```bash
wc -l ORCHESTRATION.md
grep -nE "shared/schemas/core/|docs/superpowers/" ORCHESTRATION.md | head -10
```

Expected: ~240-280 lines; 5+ references to shared/schemas/core/ + spec files.

- [ ] **Step 4: Banned-citation grep**

Run:
```bash
grep -nE "(§526\.2|§433\.2|OZEV|3rd Edition|Reg 559|Em_room|average room lux)" ORCHESTRATION.md | grep -v "do NOT\|never cite\|banned\|NOT cite" && echo FAIL || echo PASS
```

Expected: PASS.

- [ ] **Step 5: Gates**

Run:
```bash
python3 scripts/validate-examples.py 2>&1 | tail -3
```

Expected: aggregate unchanged.

- [ ] **Step 6: Commit**

```bash
git add ORCHESTRATION.md
git commit -m "feat(docs): F.4 ORCHESTRATION.md — public-facing skill orchestration contract for arbitrary agents (DraftsMan / Claude CLI / MCP servers / future tooling)"
```

---
