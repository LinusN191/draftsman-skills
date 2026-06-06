# Skill Orchestration Contract

Public-facing reference for arbitrary agents — Claude CLI, MCP servers, DraftsMan runtime, third-party agentic systems — orchestrating skills published from this repository.

This document defines the **contract between an orchestrator and a skill**: how the orchestrator constructs the per-invocation payload, how the skill declares what it needs, how grounded inputs are resolved, and how skill output is placed back into the project coordinate system.

The runtime executes; this repo ships contracts. See `[[runtime-project-boundary]]` for the boundary.

---

## 1. The contract

### What a skill declares

In `skill.manifest.json`:

```json
{
  "skill": "lighting-layout",
  "version": "1.8.0",
  "scope": "room",
  "placement_convention": "room_local_mm"
}
```

- `scope` ∈ `{room, floor, building, none}` — the unit of invocation. The orchestrator iterates per unit and invokes the skill ONCE PER UNIT.
- `placement_convention` ∈ `{room_local_mm, floor_local_mm, site_local_mm, none_topological}` — how the orchestrator interprets coordinates returned by the skill. See §5.

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

- Items with `grounded_source` are auto-filled by the orchestrator from the SkillInput payload (see §3).
- Items without `grounded_source` are engineer-provided values.

### What an orchestrator provides

A `SkillInput` payload validating against `shared/schemas/core/skill-input.schema.json`. `Room.type` MUST be a canonical_id drawn from the 3-catalogue room taxonomy at `shared/standards/spaces/` (see §8). The catalogue currently exposes **674 canonical IDs across 22 categories**.

Example:

```json
{
  "scope": "room",
  "floor": { "id": "FL-02", "level_name": "Level 2 — Outpatients" },
  "room": {
    "room_id": "R-217",
    "type": "healthcare_spaces.general_examination_spaces.exam_room",
    "area_m2": 14.4,
    "bbox": { "length": 4.8, "width": 3.0, "min_xy": [12.5, 8.0] },
    "polygon": [[12.5, 8.0], [17.3, 8.0], [17.3, 11.0], [12.5, 11.0], [12.5, 8.0]],
    "centroid": { "x": 14.9, "y": 9.5 }
  },
  "project_facts": {
    "jurisdiction": "GB",
    "building_type": "11-13 21 11",
    "code_basis": "BS 7671:2018+A2:2022",
    "units": "metric"
  },
  "engineer_inputs": {
    "ceiling_height_mm": 2800,
    "luminaire_lumens": 4000
  }
}
```

---

## 2. Iteration pseudocode

The skill is invoked ONCE PER UNIT. The orchestrator owns iteration.

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

---

## 3. Grounding bindings

`grounded_source` on an `inputs.json` item tells the orchestrator how to resolve that input from the payload.

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

---

## 4. Worked example — lighting-layout in a healthcare exam room

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

**Orchestrator constructs SkillInput per room** (canonical ID `healthcare_spaces.general_examination_spaces.exam_room` from `shared/standards/spaces/room-types/healthcare_spaces.json`, OmniClass code `13-51 11 11`, `_verification_status: mirror_sourced`):

```json
{
  "scope": "room",
  "floor": { "id": "FL-02", "level_name": "Level 2 — Outpatients", "origin_xy_mm": [0, 0] },
  "room": {
    "room_id": "R-217",
    "type": "healthcare_spaces.general_examination_spaces.exam_room",
    "area_m2": 14.4,
    "bbox": { "length": 4.8, "width": 3.0, "min_xy": [12.5, 8.0] },
    "polygon": [[12.5, 8.0], [17.3, 8.0], [17.3, 11.0], [12.5, 11.0], [12.5, 8.0]],
    "centroid": { "x": 14.9, "y": 9.5 }
  },
  "project_facts": {
    "jurisdiction": "GB",
    "building_type": "11-13 21 11",
    "code_basis": "BS 7671:2018+A2:2022",
    "units": "metric"
  },
  "engineer_inputs": {
    "ceiling_height_mm": 2800,
    "luminaire_lumens": 4000,
    "controls_protocol": "DALI"
  }
}
```

The skill auto-resolves `room_type` and `jurisdiction` via `grounded_source`; the engineer supplies the rest via `engineer_inputs`.

**Skill emits output (room-local mm per `placement_convention: room_local_mm`):**

```json
{
  "drawing_type": "lighting-layout",
  "version": "1.8.0",
  "room": { "length_mm": 4800, "width_mm": 3000, "ceiling_height_mm": 2800 },
  "luminaires": [
    { "id": "L1", "x_mm": 1200, "y_mm": 750, "mount_type": "recessed" },
    { "id": "L2", "x_mm": 3600, "y_mm": 750, "mount_type": "recessed" },
    { "id": "L3", "x_mm": 1200, "y_mm": 2250, "mount_type": "recessed" },
    { "id": "L4", "x_mm": 3600, "y_mm": 2250, "mount_type": "recessed" }
  ]
}
```

**Orchestrator transforms to floor-local metres** (using §5 `room_local_mm` rule):

```python
real_x_m = room.bbox.min_xy[0] + (lum.x_mm / 1000.0)
real_y_m = room.bbox.min_xy[1] + (lum.y_mm / 1000.0)
# L1: real_x = 12.5 + 1.2 = 13.7 m; real_y = 8.0 + 0.75 = 8.75 m
```

---

## 5. Placement transforms

| `placement_convention` | Transform rule |
|---|---|
| `room_local_mm` | `real_xy_m = room.bbox.min_xy + (skill_output.x_mm / 1000, skill_output.y_mm / 1000)` |
| `floor_local_mm` | `real_xy_m = floor.origin_xy_mm/1000 + (skill_output.x_mm/1000, skill_output.y_mm/1000)` |
| `site_local_mm` | `real_xy_m = site.origin_xy_mm/1000 + (skill_output.x_mm/1000, skill_output.y_mm/1000)` |
| `none_topological` | No spatial transform. Render as topology graph (e.g. SLD circuit diagram). |

The 4-value enum mirrors `IfcLocalPlacement` semantics in ISO 16739 (IFC 4 final). The chosen convention determines which `IfcLocalPlacement.PlacementRelTo` parent the skill output binds to — room, floor, or site — when the runtime exports to IFC. The topological case maps to `IfcRelConnectsElements` rather than spatial placement. Full IFC entity reference at `shared/standards/bim/ISO16739/` (Sprint X).

---

## 6. Engineer-input layering

When the orchestrator resolves a value for an `inputs.json` item, it MUST follow this precedence (highest → lowest):

1. `engineer_inputs.<id>` — explicit override (orchestrator-collected from engineer or session)
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

Engineer overrides always win — the engineer is the system of record for design decisions; grounding is convenience scaffolding, not authority.

---

## 7. MCP integration hint

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
4. Resolves grounded bindings (§3)
5. Invokes the skill (typically via LLM prompt chain)
6. Returns the skill's IR output to the calling agent, ready for the orchestrator's placement transform (§5)

This makes draftsman-skills first-class MCP-discoverable tools for any MCP-aware agent.

---

## 8. Room.type catalogue

`Room.type` MUST be a canonical_id drawn from the 3-catalogue room taxonomy at `shared/standards/spaces/`. Validation pattern is snake_case (enforced at schema level); canonical membership is enforced at gate-time via the `validate-examples.py` Lint 5 check.

### Three catalogues

| Catalogue | Path | Entries | Categories | Sprint |
|---|---|---|---|---|
| OmniClass Table 13 — Spaces by Function | `shared/standards/spaces/room-types/*.json` | 290 | 13 | X |
| Uniclass 2015 Table SL — comprehensive room-level | `shared/standards/spaces/room-types-uniclass-sl/*.json` | 295 | 7 | Z |
| OmniClass Table 11 — Construction Entities (building-level) | `shared/standards/spaces/building-types-t11/construction-entities-by-function.json` | 89 | (cross-reference target) | Z |

**Total: 674 canonical IDs across 22 categories.**

T13 categories (room-level by function): space_planning / parking / facility_service / circulation / education / recreation / government / artistic / museum / library / spiritual / environmentally_controlled / healthcare.

SL categories (room-level by occupancy): residential / commercial / retail / hospitality / industrial / agricultural / transport.

T11 (building-level only): used via cross-reference rollup; NOT a direct `Room.type` source.

### When to consume which taxonomy

- **Healthcare / education / circulation / facility / theatre rooms** → OmniClass T13.
- **Residential / hotel / office / retail / restaurant / industrial / agricultural / warehouse rooms** → Uniclass SL.
- **Building-type rollup** (e.g. "this room is in a hotel building") → OmniClass T11 via SL→T11 cross-references in the SL entry's `building_type_codes[]`.

### Cross-references per entry

Every entry exposes a `cross_references` object with these keys (any may be `null` if not applicable):

- `bs_en_12464_1` — BS EN 12464-1:2021 lighting class binding (consumed by lighting-layout, photometric-analysis)
- `ashrae_90_1` — ASHRAE Standard 90.1 building-energy lookup
- `ashrae_62_1` — ASHRAE Standard 62.1 ventilation lookup
- `cibse_lg` — CIBSE Lighting Guide tag (DEFERRED to Sprint Y; paid source)
- `nrm2` — RICS NRM2 measurement rule (DEFERRED to Sprint Y; paid source)

SL entries additionally carry `building_type_codes[]` (list of OmniClass T11 codes) for building rollup.

### Entry provenance

Each entry has a `_verification_status` discriminator:

- `mirror_sourced` — verbatim from the upstream mirror (highest authority).
- `engineering_consensus` — synthesised via engineering discipline citing recognised standards (NHS HTM / HBN / ASHRAE / BS / Approved Documents). The `_inference_note` field discloses the citation chain.
- `inferred` — pattern-extended from the upstream mirror's hierarchical numbering; `_inference_note` discloses the inference path and engineering corroboration; Sprint Y `occs_verified` back-fill will confirm.

The worked example in §4 uses `healthcare_spaces.general_examination_spaces.exam_room` (`mirror_sourced`, OmniClass 13-51 11 11). Compare against `healthcare_spaces.operating_theatre` (`inferred` — disclosed lineage to NHS HTM 03-01 + HBN 26 + ASHRAE 170-2021).

### Fuzzy match for drawing-parser strings

Architectural drawing parsers emit room labels in human language ("Master Bedroom", "OR-3", "Open Plan"). Orchestrators normalise to canonical IDs via the fuzzy-match algorithm spec at `shared/standards/spaces/fuzzy-match-reference.md` (Sprint X). The spec ships algorithm + test fixtures only; orchestrators implement the engine in their own runtime layer.

The fuzzy matcher uses `common_aliases[]` on each entry as primary signal, with hierarchical fallback to parent canonical IDs when sub-type disambiguation fails.

### IFC space-type binding

Every entry carries `ifc_space_type` ∈ `IfcSpaceTypeEnum` (7 values from ISO 16739: PARKING / GFA / BERTHING / EXTERNAL / INTERNAL / USERDEFINED / NOTDEFINED). This binding feeds IFC export at the runtime layer. Full enum + entity reference at `shared/standards/bim/ISO16739/space-types.json`.

---

## References

- `shared/schemas/core/skill-input.schema.json` — SkillInput payload metaschema
- `shared/schemas/core/skill-manifest.schema.json` — manifest metaschema (declares `scope` + `placement_convention`)
- `shared/schemas/core/inputs.schema.json` — inputs metaschema (extended with `grounded_source`)
- `shared/standards/spaces/README.md` — 3-catalogue taxonomy overview
- `shared/standards/spaces/fuzzy-match-reference.md` — fuzzy-match algorithm spec + fixtures
- `shared/standards/bim/ISO16739/README.md` — IFC entity subset reference
- `docs/superpowers/specs/2026-06-05-skillinput-contract-grounding-design.md` — full design spec
- `docs/superpowers/specs/skill-input-design-rationale.md` — BIM/IFC + taxonomy justification
