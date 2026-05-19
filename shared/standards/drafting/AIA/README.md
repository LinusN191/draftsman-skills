# AIA CAD Layer Guidelines 2007 — Drafting Standards Layer

US CAD layer-naming standard. Part of the National CAD Standard (NCS) Version 5.

## Files in this folder

| File | Purpose |
|---|---|
| `meta.json` | Publication metadata, edition, scope |
| `layer-naming.json` | Discipline-MajorGroup-MinorGroup-Modifier-Status layer naming convention |
| `status-codes.json` | Single-character status (N/E/D/F/R/X) |
| `discipline-designators.json` | 16 discipline single-character codes |
| `major-group-codes.json` | Electrical major group set (focus); other disciplines listed |
| `cad-layers.json` | Skills-layer abstract `layout_group` → AIA concrete CAD layer code mapping (consumed by SLD v1.5+ US examples) |

## Scope notes

- **Electrical** discipline major groups populated exhaustively (POWR, LITE, COMM, FIRE, SOUN, VIDE, SECU, AUTO, NURS, TVAN, GROU, INST)
- **Other disciplines** (A/S/M/P) list common values only — full taxonomy deferred to per-discipline skill consumption sprints

## Applies to jurisdictions

- **US** — primary standard
