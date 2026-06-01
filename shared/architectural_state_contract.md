# Architectural state contract

Sprint 4-AB introduces a structured `architectural_state` JSON block
injected into every electrical skill's IR-gen prompt when the project
has a confirmed building model. Skills consume this block according to
the rules below.

## Payload shape

```json
{
  "scope": {
    "kind": "single_floor | typical_floors | all_floors_of_building | all_floors_of_project",
    "building_id": "...",
    "floor_ids": ["..."],
    "typical_signature": "..."
  },
  "building": {
    "label": "Main Tower",
    "floors_in_scope": [
      {
        "id": "...",
        "level_number": 2,
        "level_name": "L02",
        "elevation_m": 7.5,
        "ceiling_height_m": 2.7,
        "rooms": [
          {
            "id": "...",
            "name": "Open-plan office",
            "type": "office",
            "area_m2": 96.0,
            "polygon": [{"x": 0.0, "y": 0.0}],
            "ceiling_height_m": 2.7,
            "confirmed": true
          }
        ],
        "walls_count": 84,
        "doors_count": 18,
        "windows_count": 12,
        "columns_count": 6
      }
    ]
  },
  "unconfirmed_rooms_in_scope": 4
}
```

## Field semantics

- `scope.kind` — engineer's run-scope choice. `single_floor` is the
  Sprint 4-AB default; `typical_floors` / `all_floors_*` come in 4-CD.
- `scope.floor_ids` — the floors this run targets. For a single-floor
  run this is a one-element list.
- `building.label` — engineer-confirmed building name (e.g.
  "Main Tower"); use in titles, labels, and identifiers.
- `floors_in_scope[].rooms[].polygon` — closed polygon in metres,
  origin at architect's plan origin (NOT normalised). Geometry-aware
  skills use this for placement.
- `floors_in_scope[].rooms[].confirmed` — `true` iff the engineer
  has confirmed the room. Unconfirmed rooms appear in
  `unconfirmed_rooms_in_scope` count and warrant a reviewer warning
  if a generated artefact relies on them.

## Consumption taxonomy

### Geometry-aware skills

These skills lay things out IN space and consume the full payload:

- **lighting-layout** — fixture grid spacing keyed to `rooms[].polygon`
  + `ceiling_height_m`
- **earthing** — rod / mat placement against room polygons; bonding
  conductor routing along walls
- **db-layout** — distribution board placement within rooms;
  preference for `plantroom`-typed rooms
- **small-power** — receptacle positions along room perimeters
- **arc-flash-labelling** — labels placed adjacent to existing
  equipment within room polygons

Rules:
- Reject placements that fall outside any `polygon` in the floor's
  rooms list.
- When `confirmed=false`, surface a reviewer warning that the room
  geometry is unconfirmed.

### Context-only skills

These skills produce schematics or calculations and consume only the
metadata fields (`rooms[].name`, `rooms[].type`, `ceiling_height_m`):

- **sld** — single-line diagram; uses room names for circuit
  labelling but not for placement
- **cable-sizing** — uses room ceiling height for cable-tray routing
  length estimation; uses room area for diversity calculation
- **fault-level** — uses building/floor metadata for upstream
  impedance context; no geometric placement
- **arc-flash** — calculation only; uses room data for incident-energy
  context

Rules:
- Do NOT attempt to place anything geometrically.
- Use room data only as labelling/calculation context.

## Validator guidance

Validators MUST surface a finding when:

1. A geometry-aware skill places an entity whose centroid falls
   outside every `rooms[].polygon` in scope.
2. The skill consumes a room with `confirmed=false` without flagging
   the dependency in its IR's `assumptions` field.
3. `unconfirmed_rooms_in_scope > 0` and the IR doesn't acknowledge it.

## Reviewer guidance

Reviewers SHOULD comment when:

1. A geometry-aware skill ignores the polygon and uses bounding-box
   placement instead.
2. The IR doesn't reference `building.label` in titles when the
   building model is confirmed.
3. A context-only skill includes geometric placement (it shouldn't).
