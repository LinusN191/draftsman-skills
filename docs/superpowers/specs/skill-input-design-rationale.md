# SkillInput Design Rationale

**Date:** 2026-06-05
**Sprint:** F (Foundation) — input to F.1 SkillInput schema authoring
**Companion to:** `shared/schemas/core/skill-input.schema.json` (authored at F.1)

## Why a tagged-union by scope

The orchestrator → skill payload changes shape by `manifest.scope`:

- `scope: room` → payload has `room` (singular, the unit being processed) + `floor` (parent context)
- `scope: floor` → payload has `floor` + `rooms[]` (all rooms in the floor for cross-room reasoning at the floor level)
- `scope: building` → payload has `building` + `floors[]` (all floors)

Tagged-union (`oneOf` with `scope` const discriminator) makes the shape self-describing. An orchestrator picks the right branch by reading the manifest's `scope` field. A skill never receives a shape it isn't designed for, and an orchestrator authoring mistake fails at the schema gate rather than mid-prompt.

The alternative — a single flat shape with optional fields for every scope — was rejected because it forces every consumer skill to defensively check `if (input.rooms) {…} else if (input.room) {…}` at every entry point. Tagged-union pushes that branching into the schema where it belongs.

## Why `room.type` as snake_case enum

Each skill's standards lookup tables (e.g. `shared/standards/lighting/BSEN12464/lux-levels.json`) use snake_case keys: `office.open_plan`, `circulation.lobby`, `industrial.warehouse_high`. If `room.type` arrives as freeform string (e.g. "Open Plan Office" or "openPlanOffice"), the lookup fails silently — the skill falls back to a default lux target and the orchestrator never learns the binding was wrong.

Locking `room.type` to a snake_case enum matching the 27 canonical values in `lux-levels.json` forces orchestrators to normalize BEFORE the skill runs. Schema-level fail-fast prevents silent lookup misses.

The 27 canonical values (verified against `shared/standards/lighting/BSEN12464/lux-levels.json`):

- **office.*** (6): `open_plan`, `private_office`, `conference`, `reception_desk`, `filing_copying`, `archive`
- **circulation.*** (4): `main_corridor`, `link_corridor`, `lobby`, `staircase`
- **sanitary.*** (2): `toilet_wc`, `first_aid`
- **industrial.*** (5): `warehouse_low`, `warehouse_high`, `workshop`, `car_park_bays`, `car_park_ramp`
- **healthcare.*** (3): `ward_general`, `ward_examination`, `consultation`
- **education.*** (4): `classroom`, `classroom_board`, `laboratory`, `sports_hall`
- **retail.*** (3): `general`, `high_emphasis`, `checkout`

This enum is the cross-cutting room.type taxonomy for ALL skills (not just lighting). Other skills extending the taxonomy add new keys to `lux-levels.json` first; the SkillInput enum follows. Single source of truth = no enum drift across the contract surface.

Per BS EN 12464-1:2021 Tables 6.1–6.43, the 27 values cover the room categories where indoor work area lighting requirements are explicitly tabulated. Specialist room types not in this list (e.g. theatres, cleanrooms, server halls) are intentionally out-of-scope for v1.0 of the contract — the lint pass rejects them rather than silently treating them as generic office. Extension is a deliberate governance step, not an accidental override.

## Why `placement_convention` is separate from `scope`

A skill's `scope` declares what unit it processes; `placement_convention` declares what coordinate frame the output uses. These are orthogonal concerns:

- A room-scope skill MAY emit in room-local mm (lighting-layout, small-power, fire-alarm) → `placement_convention: room_local_mm`
- A building-scope skill MAY emit in site-local mm (earthing electrode network) → `placement_convention: site_local_mm`
- A building-scope skill MAY emit topology-only (sld) → `placement_convention: none_topological`
- A floor-scope skill MAY emit topology-only (schematic) → `placement_convention: none_topological`

Conflating scope and placement into one field would force false equivalences (every room-scope must be spatial; every building-scope must be site-local). The 4-value placement enum + scope independence supports legitimate non-spatial outputs (schematics, single-line diagrams, schedules).

## BIM/IFC alignment (ISO 16739)

`IfcLocalPlacement` (per ISO 16739, the public IFC standard) defines element positions relative to their containing spatial parent. The 4-value `placement_convention` mirrors this parent-relative convention:

- `room_local_mm` ≈ position relative to `IfcSpace`
- `floor_local_mm` ≈ position relative to `IfcBuildingStorey`
- `site_local_mm` ≈ position relative to `IfcSite`
- `none_topological` ≈ no spatial placement; element is logical (e.g. an `IfcElectricDistributionPoint` in a single-line diagram)

This makes our outputs IFC-export-friendly when the runtime serializes to BIM. Traditional 2D CAD (world coords) is a downstream rendering concern handled by the runtime, not a contract concern. The skills repo never emits world coordinates directly — parent-relative placement is the IR convention.

Note: we do not yet ship a transcribed IFC standards layer. The ISO 16739 reference is by public standard name only. When/if the runtime needs full IfcLocalPlacement round-tripping, an `shared/standards/bim/ISO16739/` layer would be authored following the same pattern as `shared/standards/lighting/BSEN12464/`.

## Why two-tier `grounded_source` validation

The closed `room.*` enum (e.g. `room.length_mm`, `room.width_mm`, `room.ceiling_height_mm`, `room.type`) prevents typos like `room.bbbox.length` from silently passing as "the runtime will figure it out." Strict enum closure = fail loudly at the gate, before the orchestrator ever wires the binding.

The `project.*` enum is closed for known canonical facts (`jurisdiction`, `building_type`, `code_basis`, `units`, `ceiling_height_mm`, `project_id`) BUT allows `project.<custom>` via a pattern fallback (`^project\\.[a-z_][a-z0-9_]*$`) for project-specific facts a particular orchestrator might track (e.g. `project.acoustic_class`, `project.fire_strategy_ref`). The pattern fallback is loud — the manifest-lint pass flags every custom binding for orchestrator-confirmation in the lint report.

Two-tier discipline = strict where we know the taxonomy, flagged-but-allowed where extension is legitimate. The orchestrator stays accountable for custom bindings; the contract stays open enough to accommodate real projects without forcing every new fact through a contract amendment.

## Reference orchestrators

This rationale informs the following downstream artefacts:

1. F.1 `shared/schemas/core/skill-input.schema.json` — JSON Schema authoring (tagged-union shape, room.type enum, ProjectFacts additionalProperties pattern)
2. F.4 `shared/schemas/core/ORCHESTRATION.md` — worked example narration showing how an orchestrator constructs SkillInput per scope
3. W1 / W2 per-skill migration tasks — decisions about which manifest fields carry `scope`, `placement_convention`, and `grounded_source` bindings
4. Future MCP-server bindings exposing draftsman-skills via tool calls — the tagged-union surfaces directly as the tool's input schema, so MCP-consuming agents inherit the same fail-fast discipline at the protocol boundary, not at runtime

Any future change to the SkillInput shape (new scope value, new placement_convention entry, new room.type category) must update this rationale first, then F.1, then per-skill migrations. Rationale-before-schema-before-migration is the contract change order.
