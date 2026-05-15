# IEC 60617 — Graphical Symbols for Diagrams

**Standard:** IEC 60617 (Graphical symbols for diagrams)
**Status:** Active — database edition at std.iec.ch/iec60617
**Scope of this layer:** MEP-relevant parts (2, 3, 6, 7, 8, 11). ~225 symbols.

This layer is the single source of truth for graphical symbols used by all DraftsMan electrical drafting skills. It serves two purposes simultaneously:

1. **Engineering intelligence** — every symbol has IEC clause traceability, engineering usage notes, annotation requirements, and related-symbol cross-references. Skills look up "what is this symbol?", "when do I use it?", "what fields do I annotate?".
2. **Renderer geometry** — every symbol carries an SVG path describing its shape, a bounding box, and named terminal points. The DraftsMan runtime reads geometry directly from this layer and converts it to DXF blocks at render time.

The generated symbol files under `shared/symbols/electrical/` are produced from this layer by the DraftsMan runtime. **Do not edit the generated files** — edit the source symbol entry here.

---

## Files

| File | Purpose |
|---|---|
| `meta.json` | Standard title, edition history, part catalogue, IEC reference number format |
| `part2-general.json` | Part 2 — qualifying symbols, junctions, earths, polarity markers (~25 symbols) |
| `part3-conductors.json` | Part 3 — conductors, cables, busbars, conduit, trunking (~30 symbols) |
| `part6-power.json` | Part 6 — generators, motors, transformers, batteries, UPS, PV, capacitors, inverters (~35 symbols) |
| `part7-switchgear.json` | Part 7 — MCBs, MCCBs, ACBs, contactors, fuses, RCDs, RCBOs, SPDs, ATS, contacts, pushbuttons (~70 symbols) |
| `part8-measurement.json` | Part 8 — meters, indicator lamps, alarms, transducers (~30 symbols) |
| `part11-architectural.json` | Part 11 — DBs, sockets, luminaires, switches, sensors, detectors, cable routes, EV (~36 symbols) |
| `symbol-index.json` | Flat O(1) lookup of every symbol → IEC ref + category + part file |
| `symbol-usage-guide.md` | Engineering narrative — when to use which symbol, SLD conventions, common mistakes |
| `geometry-encoding.md` | SVG path conventions, terminal naming, coordinate system, how to add a new symbol |
| `amendments-summary.md` | Edition history, transition from paper parts to online database |

---

## How skills use this layer

**Fast lookup (no geometry needed):**
```
load symbol-index.json
find entry by symbol_id
read iec_ref, category, display_name, part_file
```

**Full lookup (geometry needed for rendering):**
```
load symbol-index.json   # get part_file
load that part file
find entry by symbol_id
read geometry.path, geometry.terminals, geometry.bbox
```

**Validation use case:**
```
load part file
read annotation_fields for the symbol the user placed
verify all listed fields are populated in the drawing IR
```

---

## Per-symbol schema

Every entry in a part file:

```json
{
  "symbol_id":        "MCB_1P",
  "iec_ref":          "IEC60617-07-18-01",
  "iec_part":         7,
  "iec_description":  "Circuit-breaker, general symbol",
  "draftsman_id":     "MCB_1P",
  "category":         "protection",
  "display_name":     "1-Pole MCB",
  "geometry": {
    "grid":      100,
    "bbox":      [-50, -30, 50, 30],
    "path":      "M -50 0 L -25 0 M -25 -25 L 25 -25 L 25 25 L -25 25 Z M 25 0 L 50 0",
    "terminals": { "in": [-50, 0], "out": [50, 0] }
  },
  "variants":             ["MCB_2P", "MCB_3P", "MCB_4P"],
  "annotation_fields":    ["In_A", "curve", "Icu_kA"],
  "usage_notes":          "Used on SLDs for all final circuit MCB protection. Annotate with rated current, trip curve (B/C/D), and breaking capacity.",
  "related_symbols":      ["RCBO_1P", "MCCB_3P", "FUSE_1P"],
  "generating_shared_symbol": true
}
```

See `geometry-encoding.md` for the SVG path conventions and how to add new symbols.

---

## Coverage scope

**In scope:** Parts 2, 3, 6, 7, 8, 11 — every symbol relevant to MEP building electrical design at LV (≤ 1000V AC).

**Out of scope:**
- Parts 4, 5 — discrete passive and semiconductor components (not used at the LV building design level).
- Parts 9, 10 — telecommunications (separate discipline).
- Parts 12, 13 — logic and analogue schematic (separate future skill).
- HV symbols (HV is a separate future brainstorm).

---

## Categories used (drives `shared/symbols/electrical/` directory routing)

| Category | CAD layer | Typical symbols |
|---|---|---|
| `general` | `E-SYMB` | qualifying symbols, junctions, earths |
| `conductor` | `E-WIRE` | conductors, cables, busbars |
| `power` | `E-POWR` | generators, motors, transformers, PV |
| `protection` | `E-PROT` | MCBs, RCDs, fuses, SPDs |
| `switching` | `E-SWIT` | switches, contactors, isolators, contacts |
| `measurement` | `E-MEAS` | meters, lamps, alarms |
| `architectural` | `E-EQPM` | DBs, sockets, luminaires, sensors |
