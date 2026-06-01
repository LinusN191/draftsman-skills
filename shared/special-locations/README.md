# Shared special-locations zone-derivation library

## Purpose
Reference Python implementation of BS 7671:2018+A2:2022 Part 7 zone-polygon
derivation for `electrical/special-locations/` skill examples and unit tests.
NOT a runtime executor; the DraftsMan runtime project hosts the production
zone-derivation tool per `[[runtime-project-boundary]]`. This library exists
so skill examples + INV cross-checks have a deterministic, dependency-free
reference to compare against.

## Verification status policy
ALL zone clauses emitted by this library are routed through the verified
citation table at `shared/standards/electrical/BS7671/part7-special-locations.json`
(`verification_status: verified-against-source`) plus the spec §3.2 cross-reference
table. No Part 7 sub-clause is emitted unless it appears in that verified file.

Banned citations (would fail INV / fix-pass per spec §3.2):
`§701.32`, `§701.55`, `§702.55.1`, `§702.55.2`, `§702.32`, `§703.55`, `§703.512`,
`§703.413`, `§710.413.1.5`, `§710.314`, `§710.411.3.3`, `§715.560.4`, `§715.521`,
`§715.422`.

Cross-reference standards cited where Part 7 lacks sub-clauses:
- `BS EN 61557-8` — IMD 8 s alarm response for §710 Group 2 medical IT systems
- `BS EN 61558-2-6` — transformer short-circuit protection for §715 ELV lighting
- `HTM 06-01` — NHS medical electrical services precedence

## Constraints
- **stdlib only** — no numpy, no shapely, no third-party deps
- **Python 3.10+** — type hints + dataclasses
- Function signatures match the IR schema at
  `electrical/special-locations/schemas/special-locations-ir.schema.json`
- Polygon coordinates as `list[tuple[float, float]]` in millimetres
- Heights as `float` millimetres above floor finish level

## Module map (6 modules)

| module | scope | zones emitted |
|---|---|---|
| `common.py` | shared geometry primitives | n/a |
| `bath.py` | §701 baths + shower rooms + wet rooms | `bath_zone_0`, `bath_zone_1`, `bath_zone_2` |
| `pool.py` | §702 swimming pools + paddling pools | `pool_zone_0`, `pool_zone_1`, `pool_zone_2` |
| `sauna.py` | §703 saunas (3-zone split per verified file) | `sauna_zone_1`, `sauna_zone_2`, `sauna_zone_3` |
| `medical.py` | §710 Group 0/1/2 medical envelopes | `medical_envelope_group_{0,1,2}` |
| `elv.py` | §715 ELV lighting barrier zones | `elv_barrier_zone` |

## §703 sauna 3-zone correction
Per spec §2 and the verified standards file, §703 yields **three** zones:
- `sauna_zone_1` — small rectangular footprint around heater (high-temp; silicone-insulated cable)
- `sauna_zone_2` — sauna room polygon minus zone_1 (within sauna, away from heater; IPx4 + T125)
- `sauna_zone_3` — full sauna room footprint at height_min = 1500 mm (above 1.5 m, for accessories)

Earlier brainstorm drafts described a 2-zone split; the v1.0.1 correction realigns
the library to the verified file.

## Geometry depth (2.5D)
- Plan polygon + height_min/max + parametric cylinder
- Cylindrical zones approximated as ≥12-sided regular polygons per spec §5.2

## Polygon math limitations
- `polygon_subtract(outer, inner)` returns the outer polygon with the inner polygon
  registered as a hole-equivalent for downstream rendering; the function works
  correctly for convex outer/inner pairs (sauna_zone_2 use case). Non-convex
  subtraction is deferred to the runtime project.
- `expand_polygon_horizontally` is exact for axis-aligned rectangles (the dominant
  bath/pool use case) and an approximation otherwise.

## Unit tests
Run via stdlib `unittest`:

```bash
cd shared/special-locations
python3 -m unittest discover -s zone-derivation/tests -v
```

Each module has a dedicated test file with ≥3 test methods. Zero third-party
imports.

## When to substitute
The runtime project's executor will replace this library at production time. This
reference exists for:
- Skill example reproducibility (the `examples/<scenario>/output.json` files were
  authored to match this library's output)
- INV cross-checks in the validator prompt
- Future runtime ports / language re-implementations
