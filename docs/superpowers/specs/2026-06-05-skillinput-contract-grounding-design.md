# DraftsMan SkillInput Contract Grounding — Design Spec

**Date:** 2026-06-05
**Sprint group:** F (Foundation) → W1 (Wave 1 room scope) → W2 (Wave 2+3 floor + building scope)
**Source:** Upstream brief from DraftsMan runtime team (pasted in session) + user direction to ship our own public contract
**Pattern parents:** D4 small-power sprint (30 commits, manifest evals/examples drift caught at fence) + D5 lighting-layout sprint (31 commits, 11-check fence + cascade SHA-256 byte-equality)
**Target:** Public skill-orchestration contract for draftsman-skills repo. DraftsMan-runtime is one consumer; design for arbitrary AI agents, MCP servers, future tooling.

---

## 1. Mission

Ship the **public skill-orchestration contract** that lets any orchestrator — DraftsMan runtime, a generic AI agent (Claude CLI), an MCP server, future tooling — iterate the skills in this repo without proprietary knowledge.

Today every drawing skill asks for one `room_type` + dimensions + jurisdiction and lays out one room. The skill itself doesn't carry the metadata that tells a consumer "I am a per-room skill; these inputs come from a parsed building model; here is the binding grammar." That metadata is the contract this spec ships.

## 2. Core principle reinforced

Per `[[runtime-project-boundary]]`: skills ship CONTRACTS; orchestrators own iteration + calc execution + rendering + placement. This spec adds the contract metadata that lets ANY orchestrator iterate correctly — not DraftsMan-only.

**Single-unit invariant preserved.** Every skill invoked for ONE unit; never iterates internally. The contract declares what unit (`scope`) the orchestrator must construct; the orchestrator owns the loop.

## 3. Locked decisions (from brainstorm, recorded as the contract)

### 3.1 Ship our own contract spec
DraftsMan brief = hint about their state, NOT our authority. We design for arbitrary generic runtime consumption. DraftsMan adopts our contract.

### 3.2 `project_fact_candidate` + `grounded_source` coexist
- `project_fact_candidate: boolean` (already in InputItem schema) = project-memory hint
- `grounded_source: "<binding>"` (NEW) = parsed-model auto-fill binding
- Distinct concerns; an item can be both, one, or neither.

### 3.3 4 foundation additions
1. **`shared/schemas/core/skill-input.schema.json`** (NEW) — formal SkillInput payload metaschema
2. **`shared/schemas/core/skill-manifest.schema.json`** (NEW) — manifest metaschema with `scope` + `placement_convention` enums
3. **Extension to `shared/schemas/core/inputs.schema.json`** — `grounded_source` two-tier closed-grammar validation
4. **`ORCHESTRATION.md`** at repo root — public-facing orchestration reference with pseudocode + worked example

### 3.4 `placement_convention` enum
4 values aligned with ISO 16739 IfcLocalPlacement (BIM standard):
- `room_local_mm` (default for room-scope spatial skills)
- `floor_local_mm` (floor-scope spatial skills)
- `site_local_mm` (building-scope spatial skills like earthing)
- `none_topological` (logical-only skills: SLD, schematic)

### 3.5 All 8 skills migrate (no HOLD)
User direction: declarative on our side is harmless even where DraftsMan runtime can't iterate yet. Forward-prepared for non-DraftsMan consumers.

### 3.6 fire-alarm deferred
fire-alarm v0.2.0 is a stub. Defer grounding to Wave 1.5 (separate sprint, post-ship).

### 3.7 Minor version bump per skill
Adding contract metadata is additive surface (not breaking). Minor bump signals new capability.

## 4. Contract surface — what each skill declares

### 4.1 `skill.manifest.json` additions

```json
{
  "scope": "room | floor | building",
  "placement_convention": "room_local_mm | floor_local_mm | site_local_mm | none_topological"
}
```

Both optional (backwards-compatible with un-migrated skills). VALIDATED via closed enum when present.

### 4.2 `inputs.json` per-item additions

```json
{
  "id": "room_type",
  "grounded_source": "room.type"
}
```

Closed grammar:
- **room.*** (closed list — for `scope: room` only): `room.type`, `room.area_m2`, `room.bbox.length`, `room.bbox.width`, `room.centroid.x`, `room.centroid.y`, `room.mounting_height`, `room.polygon`
- **project.*** (canonical closed list — for any scope): `project.building_type`, `project.code_basis`, `project.jurisdiction`, `project.units`, `project.ceiling_height_mm`, `project.project_id`
- **project.<custom>** (pattern fallback — `^project\\.[a-z_]+$`) — allowed but lint flags as "uses custom binding; confirm orchestrator can provide this"

### 4.3 `inputs.json` per-item drops

Per-skill, drop items now fully grounded by a binding. Keep genuine engineer asks.

### 4.4 Output placement

Output stays in the manifest's declared `placement_convention` frame. Orchestrator transforms to real coords per the convention's documented rule (in ORCHESTRATION.md).

## 5. Per-skill scope + placement + version table

| # | Skill | Current | `scope` | `placement_convention` | New | Sprint |
|---|---|---|---|---|---|---|
| 1 | `lighting-layout` | 1.7.0 production | `room` | `room_local_mm` | **1.8.0** | W1 |
| 2 | `small-power` | 2.0.0 production | `room` | `room_local_mm` | **2.1.0** | W1 |
| 3 | `db-layout` | 1.5.0 beta | `floor` | `floor_local_mm` | **1.6.0** | W2 |
| 4 | `arc-flash-labelling` | 1.1.0 beta | `floor` | `floor_local_mm` | **1.2.0** | W2 |
| 5 | `schematic` | 1.1.0 beta | `floor` | `none_topological` | **1.2.0** | W2 |
| 6 | `sld` | 1.6.0 beta | `building` | `none_topological` | **1.7.0** | W2 |
| 7 | `earthing` | 1.5.0 beta | `building` | `site_local_mm` | **1.6.0** | W2 |
| 8 | `fire-alarm` | 0.2.0 stub | `room` | `room_local_mm` | (post-ship) | W1.5 (deferred) |

### Per-skill drop list (W1 + W2)

| Skill | Items dropped (grounded fully covers) |
|---|---|
| lighting-layout | `room_type`, `room_length_mm`, `room_width_mm`, `jurisdiction` |
| small-power | `room_type`, `room_length_mm`, `room_width_mm`, `jurisdiction`, `building_type` |
| db-layout | `jurisdiction`, `project_id`, `building_type` |
| arc-flash-labelling | `jurisdiction`, `project_id` |
| schematic | `jurisdiction`, `project_id` |
| sld | `jurisdiction`, `project_id`, `building_type` |
| earthing | `jurisdiction`, `project_id`, `building_type` |

### Per-skill keep list (genuine engineer asks)

- Luminaire/socket/detector technical specs (lumens, wattage, IP rating, photometrics)
- `ceiling_height_mm` (engineer/project fact; not polygon-derivable)
- Controls protocols (DALI, 0-10V, switching)
- DB designations, circuit numbering
- Anchor fixtures, special-locations declarations
- Cascade source paths

## 6. Foundation deliverables in detail

### 6.1 `shared/schemas/core/skill-input.schema.json` (NEW)

Formal Draft-07 JSON Schema for orchestrator → skill payload. Tagged-union `oneOf` shape by scope:

- **RoomScopeInput**: `scope=room` + `floor` + `room` (single) + `project_facts` + `engineer_inputs`
- **FloorScopeInput**: `scope=floor` + `floor` + `rooms[]` + `project_facts` + `engineer_inputs`
- **BuildingScopeInput**: `scope=building` + `building` + `floors[]` + `project_facts` + `engineer_inputs`

Definitions:
- `Building`, `Floor`, `Room` (with `room_id`, `type`, `area_m2`, `bbox`, `polygon`, `centroid`, `mounting_height`)
- `ProjectFacts` (with `building_type`, `code_basis`, `jurisdiction`, `units` + `additionalProperties: true`)

Companion `shared/schemas/core/skill-input.reference.md` documents each field with engineering examples + BIM/IFC justification.

**Critical decision: `Room.type` is a snake_case enum** matching values in `shared/standards/lighting/BSEN12464/lux-levels.json` (`office.open_plan`, `office.private_office`, `circulation.lobby`, etc.). Orchestrators MUST normalize before passing. Fails fast if mismatched. (Risk 4 mitigation.)

### 6.2 `shared/schemas/core/skill-manifest.schema.json` (NEW)

Draft-07 metaschema for skill.manifest.json. Validates:
- Required fields: `skill`, `version` (semver pattern), `discipline`, `produces_intents`, `consumes_intents`
- Optional fields validated when present: `status` (enum: stub/beta/production), `scope` (enum: room/floor/building), `placement_convention` (4-value enum)
- `additionalProperties: true` — preserve existing manifest fields the schema doesn't yet enumerate. Lint pass catches typos (Risk 1 mitigation).

### 6.3 Extension to `shared/schemas/core/inputs.schema.json`

Add `grounded_source` to InputItem properties with **two-tier closed-grammar validation**:

```json
"grounded_source": {
  "type": "string",
  "oneOf": [
    { "enum": [
      "room.type", "room.area_m2", "room.bbox.length", "room.bbox.width",
      "room.centroid.x", "room.centroid.y", "room.mounting_height", "room.polygon",
      "project.building_type", "project.code_basis", "project.jurisdiction",
      "project.units", "project.ceiling_height_mm", "project.project_id"
    ] },
    { "pattern": "^project\\.[a-z_]+$" }
  ]
}
```

Tier 1 = canonical closed enum. Tier 2 = `project.<custom>` pattern fallback (lint flags as needs-orchestrator-confirmation).

### 6.4 `ORCHESTRATION.md` at repo root (NEW)

Public-facing orchestration reference. 6 sections:

1. **The contract** — what skills declare, what orchestrators provide
2. **Iteration pseudocode** — reference loops for room/floor/building scopes
3. **Worked example** — full lighting-layout invocation: SkillInput payload → grounding → skill output → placement transform
4. **Placement transforms** — interpretation for each `placement_convention` value
5. **Engineer-input layering** — precedence order: `engineer_inputs > grounded > defaults`
6. **MCP integration hint** — how an MCP server exposing draftsman-skills structures its tool calls

## 7. Sprint structure

### Sprint F — Foundation (~10-12 commits)

| Task | Model | Description |
|---|---|---|
| F.0 | Opus | Author SkillInput reference model (BIM/IFC justification + engineering walk) |
| F.1 | Sonnet | `skill-input.schema.json` + companion reference.md |
| F.2 | Sonnet | `skill-manifest.schema.json` metaschema |
| F.3 | Sonnet | Extend `inputs.schema.json` with `grounded_source` two-tier validation |
| F.4 | Opus | `ORCHESTRATION.md` with pseudocode + worked example |
| F.5 | Sonnet | Extend `scripts/validate-examples.py` to 4-pass gate (add manifest metaschema validation + manifest-lint + grounded_source enum) |
| F.6 | Sonnet | Run 4-pass gate against 8 existing manifests; fix-pass any drift |
| F.7 | Sonnet | CHANGELOG + memory file + MEMORY.md + CLAUDE.md note |
| F.8 | Opus | Final integration review (PASS / SHIP-WITH-CONCERNS / FIX-FIRST) |
| F.9 | — | Push deferred to user authorisation |

**Acceptance:** 4-pass gate green; 8 existing manifests pass against new metaschema with 0 forced edits; ORCHESTRATION.md renders cleanly + references resolve.

### Sprint W1 — Wave 1 (lighting-layout + small-power, ~18-22 commits)

Per-skill pattern (×2 skills):
1. Manifest add `scope` + `placement_convention` + version bump
2. `inputs.json` add `grounded_source` + DROP fully-grounded items
3. Generator.md update (grounded items arrive in payload)
4. Add 1 grounded-path eval per skill (omits grounded items)
5. Regression sweep: existing examples + cascade payloads byte-identical
6. CHANGELOG entry

Cross-skill:
- W1.X.7 — Cross-skill integration review (cascade contracts preserved?)
- W1.X.8 — Memory + tally bump
- W1.X.9 — Push deferred

**Acceptance:** 4-pass gate green; existing 12 lighting-layout + 12 small-power examples still validate; new grounded-path evals pass; cascade contracts (photometric / special-locations / cable-sizing) byte-identical.

### Sprint W2 — Wave 2+3 (5 skills, ~25-30 commits)

Same per-skill pattern for db-layout + arc-flash-labelling + schematic + sld + earthing.

Wave 2 (floor-scope, 3 skills): bind `project.*` facts; no `room.*` bindings. schematic gets `none_topological`.

Wave 3 (building-scope, 2 skills): sld gets `none_topological`; earthing gets `site_local_mm`. Both declare `scope: building` even though DraftsMan runtime doesn't iterate buildings yet.

**Acceptance:** 4-pass gate green; all 7 migrated skills (2 from W1 + 5 from W2) carry `scope` + `placement_convention` + grounded bindings; ORCHESTRATION.md examples cover ≥1 skill per scope tier.

### Sprint W1.5 (deferred)
fire-alarm v0.2 → v1.0 ship + ground in one sprint. Out of scope of this brainstorm.

## 8. Risk mitigation plan (5 risks)

### Risk 1: Manifest metaschema typo slips through
- **Catch:** Manifest-lint sub-pass added to 4-pass gate (F.5). Enumerates known manifest fields; flags unknowns with suggested spelling.
- **Fires:** Every PR / pre-merge.
- **Course-correct:** Implementer fixes via Edit before commit lands.

### Risk 2: `grounded_source` open `project.*` allows unprovidable bindings
- **Catch:** Two-tier validation (F.3): closed enum + pattern fallback. Lint flags custom bindings. Grounded-path eval (W1/W2 task 4) is the runtime smoke test.
- **Fires:** Pre-commit for custom binding; grounded-path eval surfaces lookup misses.
- **Course-correct:** Pick canonical binding OR escalate "we need a new canonical project.* field" to foundation tier.

### Risk 3: Stale dropped items in example input.json files
- **Catch:** Example-deprecation lint added to gate (F.5). Scans example input.json files for fields removed from inputs.json.
- **Fires:** Per-skill regression sweep (W1.X.5 / W2.X.5); per-commit for drop changes.
- **Course-correct:** Remove stale fields OR convert to `engineer_inputs` overrides.

### Risk 4: Generator prompt drift on `room.type` value normalization
- **Catch:** F.1 SkillInput schema declares `room.type` snake_case enum matching standards file. Generator prompt explicitly states orchestrator MUST normalize. Grounded-path eval (W1.{A,B}.4) exercises lookup.
- **Fires:** F.1 schema authoring (orchestrators learn constraint); W1.{A,B}.4 eval surfaces lookup miss.
- **Course-correct:** Update normalization layer OR widen enum with explicit standards citation.

### Risk 5: Cascade contract drift
- **Catch:** Cascade-byte-equality lint (SHA-256, F.5) added to gate. Per-sprint cross-skill integration review (W1.X.7 / W2.X.7).
- **Fires:** Per-commit during W1/W2 for cascade-touching edits; pre-ship integration review.
- **Course-correct:** Revert cascade-breaking edit; refactor to leave cascade payload untouched.

## 9. Cross-cutting safety net

### Sprint F pre-ship fence (7 checks)
1. SkillInput schema validates ≥1 fixture per scope tier
2. Manifest metaschema validates 8 existing manifests with 0 forced edits
3. inputs.schema.json grounded_source two-tier validation works (closed enum + pattern fallback)
4. ORCHESTRATION.md renders cleanly + references resolve
5. 4-pass gate green (was 3-pass)
6. Manifest lint = 0 unknown-field flags on existing manifests
7. Banned-citation grep clean

### Sprint W1 / W2 pre-ship fence (11 checks per skill, applied per skill at end of Wave)
1. Banned-citation grep clean
2. Existing examples still validate
3. New grounded-path eval passes
4. Cascade payloads byte-identical
5. CHANGELOG accurate
6. Manifest scope + placement_convention match §5 table
7. Generator prompt no longer asks for grounded items
8. inputs.json validates against extended metaschema
9. Dropped items not orphaned in example input.json files
10. Honest disclosure 4-place pattern (where retrofit applies)
11. Aggregate gate green

### Final Opus adversarial review per sprint
PASS / SHIP-WITH-NOTED-CONCERNS / FIX-FIRST verdict gate. Same pattern as D4 D.5 + D5 D.4.

## 10. Cost estimate

| Sprint | Commits | Token cost (per D4/D5 precedent) |
|---|---|---|
| F (Foundation) | 10-12 | ~50k subagent + main |
| W1 (lighting + small-power) | 18-22 | ~100k subagent + main |
| W2 (5 skills: db-layout + arc-flash + schematic + sld + earthing) | 25-30 | ~150k subagent + main |
| **Total** | **~55-65 commits** | **~300k tokens across 3 sessions** |

## 11. Process discipline (locked from sprint start)

- **Sonnet for mechanical**, Opus for judgment per `[[feedback-no-haiku-sonnet-opus-only]]`
- **Two-stage Opus review** per task + fix-pass commits (D4/D5 precedent)
- **Citation hygiene:** all standards citations cross-checked against `shared/standards/` verified files BEFORE plan ships
- **Banned tokens:** §526.2, §433.2, OZEV, 3rd Edition, Reg 559, Em_room, "average room lux" (inherited)
- **No-trim** per `[[feedback-no-trim-non-consequential]]`: evidence stays full-length
- **Pre-ship verification fence** per sprint
- **Final Opus integration review** per sprint
- **Push deferred to user authorisation** per CLAUDE.md shared-state rule
- **Honest disclosure** for any case where existing example deviates from canonical pattern

## 12. Definition of done

After F + W1 + W2:

- 7 of 8 production+beta skills carry `scope` + `placement_convention` + grounded bindings (fire-alarm rejoins post-ship)
- 4-pass golden CI gate green (was 3-pass)
- `SkillInput`, manifest metaschema, `grounded_source` two-tier validation all metaschema-validated
- `ORCHESTRATION.md` published at repo root; reads as public-facing iteration contract for arbitrary agents
- DraftsMan runtime activation: grounded path "just works" without further coordination
- Non-DraftsMan agent activation: Claude CLI / MCP / future tooling can read contract end-to-end without proprietary knowledge
- 1 disclosed FP held throughout (motor-superposition carry-over from remediation program)
- All 3 sprints pushed to `origin/main` only after user authorisation
