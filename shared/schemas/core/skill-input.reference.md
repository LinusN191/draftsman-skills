# SkillInput Reference

Companion to `skill-input.schema.json`. Each field explained with engineering context.

## Tagged-union by scope

The payload shape changes by `manifest.scope`:

- **`scope: room`** — orchestrator passes ONE room (the unit being processed) + parent floor context + project facts
- **`scope: floor`** — orchestrator passes ONE floor + ALL rooms in that floor (skill reasons across rooms within the floor) + project facts
- **`scope: building`** — orchestrator passes ONE building + ALL floors + project facts

The `scope` field is the `oneOf` discriminator. Schema validation fails if shape does not match scope.

## Building / Floor / Room fields

### Building

- `id`: unique building identifier (e.g. "BLD-001")
- `label`: human-readable name (e.g. "Office Block A")

`additionalProperties: true` — orchestrators may attach custom building-level metadata.

### Floor

- `id`: unique floor identifier (e.g. "FL-01" or "L1")
- `building_label`: parent building label
- `level_name`: human-readable level (e.g. "Ground Floor", "Mezzanine")
- `origin_xy_mm`: floor origin in site coordinates (mm) — used for `floor_local_mm` placement transforms

`additionalProperties: true` — orchestrators may attach storey-level metadata (e.g. `floor_to_floor_mm`).

### Room

- `room_id`: unique room identifier within the floor
- `type`: snake_case room type from the 27-value enum (see taxonomy below)
- `area_m2`: net internal area in square metres
- `bbox`: bounding box with `length` + `width` (m) + optional `min_xy` (bottom-left corner in floor-local coords in m)
- `polygon`: closed polygon vertices in floor-local metres (last vertex == first vertex)
- `centroid`: room centroid `{x, y}` in floor-local metres
- `mounting_height`: working-plane or mounting reference height in mm if known per-room
- `classification`: optional BIM `IfcClassificationReference` structure for BIM round-tripping. Auto-derivable by the orchestrator from `Room.type` via the canonical room-types catalogue lookup (`shared/standards/spaces/room-types/*.json` — match `canonical_id` and read `omniclass_code`). When supplied directly, the inline reference is carried through to IFC export. Sub-fields:
  - `source`: classification source identifier (default `"OmniClass-Table-13"` matching Sprint X taxonomy)
  - `edition`: classification edition (e.g. `"2012"`, `"2019"`)
  - `code`: verbatim classification code; for OmniClass Table 13 the 5-segment 13-digit notation `13-XX XX XX XX XX` (regex-validated)
  - `reference_uri`: optional URI to the canonical classification entry (e.g. OmniClass.org page for the code)

`additionalProperties: true` — skills may attach extra room metadata (e.g. `reflectance_ceiling`, `maintenance_factor`).

## Room.type — 27-value taxonomy

Sourced from `shared/standards/lighting/BSEN12464/lux-levels.json`. Orchestrators MUST normalize free-text room names to these values before invoking a skill.

| Category | Values |
|---|---|
| `office` | `open_plan`, `private_office`, `conference`, `reception_desk`, `filing_copying`, `archive` |
| `circulation` | `main_corridor`, `link_corridor`, `lobby`, `staircase` |
| `sanitary` | `toilet_wc`, `first_aid` |
| `industrial` | `warehouse_low`, `warehouse_high`, `workshop`, `car_park_bays`, `car_park_ramp` |
| `healthcare` | `ward_general`, `ward_examination`, `consultation` |
| `education` | `classroom`, `classroom_board`, `laboratory`, `sports_hall` |
| `retail` | `general`, `high_emphasis`, `checkout` |

Pass as `category.subcategory` (e.g. `"office.open_plan"`, `"industrial.warehouse_high"`).

## ProjectFacts

Canonical project-level facts (closed enum fields) + `additionalProperties: true` for project-specific custom facts that an orchestrator may track:

- `building_type`: e.g. `"commercial_office"`, `"warehouse"`, `"residential_dwelling"`
- `code_basis`: e.g. `"BS 7671:2018+A2:2022"`, `"NEC 2023"`, `"IEC 60364"`
- `jurisdiction`: closed enum (`GB` / `KE` / `INT` / `US`) per CLAUDE.md
- `units`: closed enum (`metric` / `imperial`)
- `ceiling_height_mm`: project-default ceiling height (mm); per-room override via `Room.mounting_height`
- `project_id`: project identifier

Custom facts via `additionalProperties: true` (e.g. `client_name`, `briefing_meeting_date`) — orchestrator declares them when constructing SkillInput; manifest-side `grounded_source: "project_facts.<custom>"` references them.

## engineer_inputs

Items NOT covered by `grounded_source` bindings. The orchestrator collects these from the engineer (UI / form / CLI prompt) and passes them alongside grounded values.

Precedence order at invocation:
1. `engineer_inputs.<id>` (highest — explicit engineer override)
2. Grounded value resolved from SkillInput via `grounded_source` binding
3. Default value declared in `inputs.json` (lowest priority)

## BIM/IFC alignment

This shape mirrors ISO 16739 `IfcLocalPlacement` parent-relative positioning:

- `Building` corresponds to `IfcBuilding`
- `Floor` corresponds to `IfcBuildingStorey`
- `Room` corresponds to `IfcSpace`

See `docs/superpowers/specs/skill-input-design-rationale.md` for the full BIM/IFC justification and orchestration worked examples.
