# IEC 60617 Standard Layer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the IEC 60617 graphical symbols standard layer as a dual-purpose AI-intelligence + renderer-geometry source of truth. 12 files in `shared/standards/electrical/IEC60617/` covering ~225 symbols across 6 IEC parts, plus migration of the legacy `standard-symbols-reference.md`.

**Architecture:** Six part-files (one per IEC 60617 part) each containing a JSON array of full symbol entries with SVG path geometry. A flat `symbol-index.json` provides O(1) lookup. Three narrative MD files document usage, geometry conventions, and amendments. `meta.json` records the standard's title, edition history, and part catalogue.

**Tech Stack:** JSON (RFC 8259), Markdown (CommonMark), SVG path syntax (W3C SVG 1.1 path `d` grammar). No code or build scripts in this layer — it is input-only. Validation via Python `json.load`.

**Reference:** See `docs/superpowers/specs/2026-05-14-iec60617-standard-layer-design.md` for the per-symbol schema, file organisation rationale, and decision log.

---

## File Structure

```
shared/standards/electrical/IEC60617/
├── README.md                    ← rewrite (was a stub)
├── meta.json                    ← new
├── symbol-index.json            ← new
├── part2-general.json           ← new (~25 symbols)
├── part3-conductors.json        ← new (~30 symbols)
├── part6-power.json             ← new (~35 symbols)
├── part7-switchgear.json        ← new (~70 symbols)
├── part8-measurement.json       ← new (~30 symbols)
├── part11-architectural.json    ← new (~36 symbols)
├── symbol-usage-guide.md        ← new
├── geometry-encoding.md         ← new
└── amendments-summary.md        ← new

electrical/sld/assets/
└── standard-symbols-reference.md  ← MOVED from IEC60617/ folder

electrical/sld/skill.manifest.json  ← UPDATED standards array
```

---

## SVG Path Conventions (apply to every symbol entry)

- **Grid:** 100 units, origin at symbol centre. SVG Y increases downward.
- **Coordinate range:** `[-50, +50]` on both axes.
- **Terminals:** Must lie on the bbox boundary, typically at `±50` on the relevant axis.
- **Symbol body:** Confined to `±30` from centre for most symbols, leaving room for terminal stubs.
- **Path commands used:** `M` (moveto), `L` (lineto), `A` (elliptical arc), `Z` (closepath). No `Q`/`C` Béziers unless a curve is essential.
- **Circle path template (centre `cx,cy`, radius `r`):**
  `M cx+r cy A r r 0 1 0 cx-r cy A r r 0 1 0 cx+r cy Z`
- **Rectangle template (corners `x1,y1` to `x2,y2`):**
  `M x1 y1 L x2 y1 L x2 y2 L x1 y2 Z`

---

## Validation Commands (used in every task)

- JSON syntax check:
  `python3 -c "import json; json.load(open('PATH'))" && echo OK`
- Symbol count (for part files):
  `python3 -c "import json; print(len(json.load(open('PATH'))['symbols']))"`
- Schema field check (for a part file):
  `python3 -c "import json; data=json.load(open('PATH')); req=['symbol_id','iec_ref','iec_part','iec_description','draftsman_id','category','display_name','geometry','variants','annotation_fields','usage_notes','related_symbols','generating_shared_symbol']; missing=[(s['symbol_id'] if 'symbol_id' in s else '?', [f for f in req if f not in s]) for s in data['symbols'] if any(f not in s for f in req)]; print('OK' if not missing else 'MISSING:'+str(missing))"`

---

## Task 1: Migrate standard-symbols-reference.md and update SLD manifest

**Files:**
- Move: `shared/standards/electrical/IEC60617/standard-symbols-reference.md` → `electrical/sld/assets/standard-symbols-reference.md`
- Modify: `electrical/sld/skill.manifest.json`

- [ ] **Step 1: Move the legacy file**

Run:
```bash
mkdir -p "electrical/sld/assets"
git mv "shared/standards/electrical/IEC60617/standard-symbols-reference.md" "electrical/sld/assets/standard-symbols-reference.md"
```

- [ ] **Step 2: Update the SLD manifest standards array**

Replace the third entry in `standards` (the path to `standard-symbols-reference.md`) with the folder path. The full updated file:

```json
{
  "skill": "sld",
  "version": "1.1.0",
  "discipline": "electrical",
  "subdiscipline": "distribution",
  "description": "LV single line diagrams from supply intake through MSB to sub-boards. Calculates maximum demand, sizes protective devices, checks PSCC/Zs, identifies life safety circuits, assesses SPD requirements.",
  "status": "production",
  "licence": "MIT",
  "inputs": ["supply-data", "load-schedule", "distribution-hierarchy", "earthing-system", "cable-lengths"],
  "outputs": ["sld-ir"],
  "output_schema": "shared/schemas/electrical/sld-ir.schema.json",
  "standards": [
    "shared/standards/electrical/BS7671/",
    "shared/standards/electrical/IEC61439/",
    "shared/standards/electrical/IEC60617/"
  ],
  "compatible_runtimes": ["DraftsMan >= 1.0", "Claude Code", "OpenClaw"],
  "changelog": "electrical/sld/CHANGELOG.md"
}
```

- [ ] **Step 3: Validate the manifest**

Run: `python3 -c "import json; json.load(open('electrical/sld/skill.manifest.json'))" && echo OK`
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add electrical/sld/skill.manifest.json electrical/sld/assets/standard-symbols-reference.md shared/standards/electrical/IEC60617/standard-symbols-reference.md
git commit -m "refactor: move IEC60617 symbol reference into SLD assets

The standard-symbols-reference.md is SLD-skill-specific quick-reference content,
not a standards layer file. Move it under electrical/sld/assets/ and point the
SLD manifest at the full IEC60617/ folder for the new layer."
```

---

## Task 2: Create meta.json

**Files:**
- Create: `shared/standards/electrical/IEC60617/meta.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "IEC 60617 — Graphical symbols for diagrams",
  "_version": "1.0.0",
  "_purpose": "Single source of truth for the graphical-symbols standard used by all DraftsMan electrical drafting skills (SLD, schematic, panel layout, riser, etc.). Combines IEC clause-level metadata, engineering usage guidance, and SVG-path geometry. Generated symbols in shared/symbols/electrical/ are produced from this layer by the DraftsMan runtime.",
  "standard": {
    "title": "Graphical symbols for diagrams",
    "issuer": "International Electrotechnical Commission",
    "issuer_short": "IEC",
    "designation": "IEC 60617",
    "status": "Active — database edition",
    "database_url": "https://std.iec.ch/iec60617",
    "first_published": 1983,
    "current_edition": "Database edition (continuously updated since 2002)",
    "language_codes": ["en", "fr"],
    "national_adoptions": [
      {"code": "BS EN 60617", "country": "United Kingdom", "notes": "Direct adoption of IEC 60617"},
      {"code": "DIN EN 60617", "country": "Germany", "notes": "Direct adoption with German titles"},
      {"code": "NF EN 60617", "country": "France", "notes": "Direct adoption"},
      {"code": "SS-EN 60617", "country": "Sweden", "notes": "Direct adoption"},
      {"code": "IS/IEC 60617", "country": "India", "notes": "Direct adoption"}
    ]
  },
  "parts": [
    {"part": 2,  "title": "Symbol elements, qualifying symbols and other symbols having general application", "covered": true,  "symbol_file": "part2-general.json"},
    {"part": 3,  "title": "Conductors and connecting devices",                                                "covered": true,  "symbol_file": "part3-conductors.json"},
    {"part": 4,  "title": "Basic passive components",                                                         "covered": false, "reason_out_of_scope": "Resistors, capacitors, inductors at component level — not relevant for MEP building electrical design above component schematics"},
    {"part": 5,  "title": "Semiconductors and electron tubes",                                                "covered": false, "reason_out_of_scope": "Discrete semiconductor symbols — not used in LV building electrical diagrams"},
    {"part": 6,  "title": "Production and conversion of electrical energy",                                   "covered": true,  "symbol_file": "part6-power.json"},
    {"part": 7,  "title": "Switchgear, controlgear and protective devices",                                   "covered": true,  "symbol_file": "part7-switchgear.json"},
    {"part": 8,  "title": "Measuring instruments, lamps and signalling devices",                              "covered": true,  "symbol_file": "part8-measurement.json"},
    {"part": 9,  "title": "Telecommunications: switching and peripheral equipment",                           "covered": false, "reason_out_of_scope": "Telecom — separate discipline"},
    {"part": 10, "title": "Telecommunications: transmission",                                                 "covered": false, "reason_out_of_scope": "Telecom — separate discipline"},
    {"part": 11, "title": "Architectural and topographical installation plans and diagrams",                  "covered": true,  "symbol_file": "part11-architectural.json"},
    {"part": 12, "title": "Binary logic elements",                                                            "covered": false, "reason_out_of_scope": "Logic schematic — covered by IEC 60617-12 future skill"},
    {"part": 13, "title": "Analogue elements",                                                                "covered": false, "reason_out_of_scope": "Analogue schematic — out of scope for building electrical"}
  ],
  "iec_reference_format": {
    "pattern": "IEC60617-PP-XX-YY",
    "fields": {
      "PP": "Part number (zero-padded to 2 digits)",
      "XX": "Section number within the part",
      "YY": "Symbol number within the section"
    },
    "example": "IEC60617-07-18-01 — Part 7, Section 18 (circuit-breakers), symbol 01 (general)"
  },
  "transition_note": "IEC 60617 was published as 13 paper parts between 1996 and 2002. In 2002 it transitioned to a continuously-updated online database at iecdatabase.iec.ch (now std.iec.ch/iec60617). Reference numbers from the printed parts remain valid; new symbols added since 2002 carry database-only references with the same PP-XX-YY format."
}
```

- [ ] **Step 2: Validate**

Run: `python3 -c "import json; json.load(open('shared/standards/electrical/IEC60617/meta.json'))" && echo OK`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add shared/standards/electrical/IEC60617/meta.json
git commit -m "feat: IEC60617 meta.json — standard metadata and part catalogue"
```

---

## Task 3: Rewrite README.md

**Files:**
- Modify (full rewrite): `shared/standards/electrical/IEC60617/README.md`

- [ ] **Step 1: Write the new README**

````markdown
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
````

- [ ] **Step 2: Commit**

```bash
git add shared/standards/electrical/IEC60617/README.md
git commit -m "docs: rewrite IEC60617 README as comprehensive layer index"
```

---

## Task 4: Create geometry-encoding.md

**Files:**
- Create: `shared/standards/electrical/IEC60617/geometry-encoding.md`

- [ ] **Step 1: Write the file**

````markdown
# IEC 60617 — Geometry Encoding

This document specifies the SVG-path geometry conventions used throughout the IEC 60617 layer. Every symbol entry in every part file follows these rules.

---

## Coordinate System

- **Grid size:** 100 units, declared as `geometry.grid: 100` in every entry.
- **Origin:** symbol centre is at `(0, 0)`.
- **Range:** all coordinates in `[-50, +50]` on each axis.
- **Y axis:** Y increases downward (SVG convention). A point at `y = -50` is at the top of the symbol; `y = +50` is at the bottom.
- **Symbol body:** keep within `±30` of centre so terminal stubs at `±50` have room.

```
              y = -50  (top)
                  |
                  |
   x = -50 ───── (0,0) ───── x = +50
       (left)     |          (right)
                  |
              y = +50  (bottom)
```

---

## Bounding Box

`geometry.bbox` is `[x_min, y_min, x_max, y_max]`. Two rules:

1. Every drawn pixel of the symbol body falls inside the bbox.
2. Every named terminal falls on the bbox boundary.

The bbox is used by the runtime for symbol placement, collision detection, and DXF block extents.

---

## Terminals

Terminals are named connection points. Stored as an object keyed by functional name:

```json
"terminals": {
  "in":  [-50, 0],
  "out": [ 50, 0]
}
```

Terminal naming convention (use the most specific name that applies):

| Functional role | Preferred name | Notes |
|---|---|---|
| Single in/out flow | `in`, `out` | Most protective devices, switches, fuses |
| Multi-phase | `L1`, `L2`, `L3`, `N`, `PE` | 3-phase devices |
| Multi-phase input/output | `L1_in`, `L1_out`, `L2_in` … | 3-phase devices with distinct line and load |
| Generic two-terminal | `A`, `B` | Symmetric devices (resistor, capacitor) |
| Power vs control | `power_in`, `power_out`, `coil_plus`, `coil_minus` | Contactors, relays |
| Earth | `line` | Earth symbols have one connection point — the line above the bars |
| Multiple identical | `t1`, `t2`, … | Last-resort numeric naming |

A purely qualifying symbol (overlay decoration like a variability arrow) has `"terminals": {}`.

---

## SVG Path Grammar

The `path` string is the value of an SVG `<path d="…">` attribute. Commands used in this layer:

| Command | Meaning | Example |
|---|---|---|
| `M x y` | Move-to (start a new sub-path) | `M -50 0` |
| `L x y` | Line-to | `L 50 0` |
| `A rx ry x-axis-rotation large-arc-flag sweep-flag x y` | Elliptical arc to | `A 20 20 0 1 0 -20 0` |
| `Z` | Close sub-path (line back to last `M`) | `Z` |

We avoid `H`, `V`, `C`, `S`, `Q`, `T`, lowercase relative commands, and Bézier curves unless absolutely necessary. The reason: explicit `M` + `L` with absolute coordinates is easier to read and validate by hand.

### Circle template

A full circle centred at `(cx, cy)` with radius `r`:

```
M cx+r cy A r r 0 1 0 cx-r cy A r r 0 1 0 cx+r cy Z
```

Example — circle radius 20 at origin:
`M 20 0 A 20 20 0 1 0 -20 0 A 20 20 0 1 0 20 0 Z`

### Rectangle template

A rectangle from `(x1, y1)` to `(x2, y2)`:

```
M x1 y1 L x2 y1 L x2 y2 L x1 y2 Z
```

Example — rectangle from (-25, -25) to (25, 25):
`M -25 -25 L 25 -25 L 25 25 L -25 25 Z`

### Connecting leads

Most symbols have leads connecting terminals to the symbol body. Pattern:

```
M -50 0 L -25 0    ← left lead from terminal at (-50,0) to body edge at (-25,0)
[…body path…]
M 25 0 L 50 0      ← right lead from body edge at (25,0) to terminal at (50,0)
```

Sub-paths are separated by additional `M` commands. The path string for a complete symbol with leads, a rectangular body, and an internal horizontal line is therefore a single string with multiple `M` segments:

```
M -50 0 L -25 0 M -25 -25 L 25 -25 L 25 25 L -25 25 Z M -25 0 L 25 0 M 25 0 L 50 0
```

---

## Previewing a Symbol

To verify a path renders correctly, paste it into any SVG viewer. Quick HTML wrapper:

```html
<svg width="200" height="200" viewBox="-50 -50 100 100" xmlns="http://www.w3.org/2000/svg">
  <path d="PASTE_PATH_HERE" stroke="black" fill="none" stroke-width="2"/>
</svg>
```

Open in a browser. Stroke `black`, no fill, stroke-width 2 is the convention. Filled shapes (battery plates, junction dots) use `fill="black"` and are noted in the entry's `usage_notes`.

---

## Runtime Conversion to DXF

The DraftsMan runtime converts these SVG paths to DXF blocks via `ezdxf`. The mapping:

| SVG | DXF entity |
|---|---|
| `M x1 y1 L x2 y2` | `LINE` from `(x1, y1)` to `(x2, y2)` |
| Closed sub-path of `L` commands | `LWPOLYLINE` (closed flag set) |
| `A rx ry 0 _ _ x y` (rx == ry) | `ARC` |
| Closed circle (two `A` halves) | `CIRCLE` |

The runtime scales the 100-unit grid to project units (typically 1 grid unit = 1 mm in millimetre projects, or 1 grid unit = 1 inch ÷ 25.4 in imperial projects).

---

## Adding a New Symbol

When a skill needs a symbol that isn't in this layer:

1. **Confirm it's a real IEC 60617 symbol.** Look it up at std.iec.ch/iec60617 or in a national adoption (BS EN 60617). If it isn't an IEC symbol, it doesn't belong in this layer — extend with a custom symbol file in `shared/symbols/electrical/` and document the deviation.
2. **Determine the part.** Parts 2, 3, 6, 7, 8, 11 are covered here. If the symbol is in an out-of-scope part, raise a brainstorm.
3. **Choose a `symbol_id`.** UPPER_SNAKE_CASE. For variants of an existing symbol, follow the existing pattern (e.g. `MCB_3P` → `MCB_4P`).
4. **Write the geometry.** Stay within `±50` on each axis. Place terminals on the bbox boundary. Preview the path in a browser before committing.
5. **Add the entry to the relevant part file.** All schema fields are mandatory.
6. **Add a matching row to `symbol-index.json`.** The index is hand-maintained — it is not auto-generated by a script.
7. **Cross-reference.** Update `related_symbols` on this symbol and add this `symbol_id` to the `variants` array of its parent symbol if applicable.

---

## Common Geometry Patterns

| Shape | Sample path | Used by |
|---|---|---|
| Horizontal line with terminals | `M -50 0 L 50 0` | Conductor, busbar, simple wire |
| Boxed device | `M -50 0 L -25 0 M -25 -25 L 25 -25 L 25 25 L -25 25 Z M 25 0 L 50 0` | MCB, MCCB, fuse |
| Circle device | `M -50 0 L -25 0 M 25 0 A 25 25 0 1 0 -25 0 A 25 25 0 1 0 25 0 Z M 25 0 L 50 0` | Motor, generator, meter |
| Two-circle (transformer) | `M -50 0 L -35 0 M 5 0 A 20 20 0 1 0 -35 0 A 20 20 0 1 0 5 0 Z M 35 0 A 20 20 0 1 0 -5 0 A 20 20 0 1 0 35 0 Z M 35 0 L 50 0` | Transformer 2W |
| Earth bars | `M 0 -50 L 0 0 M -25 0 L 25 0 M -15 10 L 15 10 M -8 20 L 8 20` | Earth, PE |
| Triangle (delta) | `M 0 -25 L 25 25 L -25 25 Z` | Delta winding |
| Diamond | `M 0 -25 L 25 0 L 0 25 L -25 0 Z` | SPD, surge arrester |

````

- [ ] **Step 2: Commit**

```bash
git add shared/standards/electrical/IEC60617/geometry-encoding.md
git commit -m "docs: IEC60617 geometry encoding — SVG path conventions and terminal naming"
```

---

## Task 5: Create amendments-summary.md

**Files:**
- Create: `shared/standards/electrical/IEC60617/amendments-summary.md`

- [ ] **Step 1: Write the file**

````markdown
# IEC 60617 — Amendments and Edition History

IEC 60617 has a different revision pattern from most IEC standards. It was originally published as a series of thirteen paper parts between 1983 and 2002, then migrated to a continuously-updated online database. This document summarises that history and what it means for symbol references in this layer.

---

## Phase 1 — Paper Parts (1983–2002)

The standard was issued in thirteen parts, each independently versioned:

| Part | Title | Last paper edition |
|---|---|---|
| 1 | Introduction (now withdrawn — content folded into Part 2) | 1985 |
| 2 | Symbol elements, qualifying symbols and other general symbols | 1996 |
| 3 | Conductors and connecting devices | 1996 |
| 4 | Basic passive components | 1996 |
| 5 | Semiconductors and electron tubes | 1996 |
| 6 | Production and conversion of electrical energy | 1996 |
| 7 | Switchgear, controlgear and protective devices | 1996 |
| 8 | Measuring instruments, lamps and signalling devices | 1996 |
| 9 | Telecommunications: switching and peripheral equipment | 1996 |
| 10 | Telecommunications: transmission | 1995 |
| 11 | Architectural and topographical installation plans | 1996 |
| 12 | Binary logic elements | 1997 |
| 13 | Analogue elements | 1997 |

During this period, an IEC reference number `IEC 60617-7, fig. 18-01` identified Part 7, section 18, symbol 01.

---

## Phase 2 — Database Edition (2002 onward)

In 2002, IEC migrated IEC 60617 from paper parts to a continuously-updated online database. The database is hosted at:

- Original URL: https://std.iec.ch/iec60617 (active)
- Earlier alias: https://www.graphical-symbols.info

Effects of the transition:

1. **No more periodic full-part revisions.** Individual symbols are added, deprecated, or revised as needed. The database carries a single live version rather than per-part edition numbers.
2. **Reference number format preserved.** A 2024-vintage symbol still references its parent part and section, in the form `IEC60617-PP-XX-YY`. New symbols added since 2002 use the same scheme.
3. **Withdrawal of paper parts.** The paper parts are no longer printed but remain the conceptual structure of the database. Part 1 has been folded into Part 2 and is no longer separately referenced.
4. **National adoptions track the database.** BS EN 60617, DIN EN 60617, NF EN 60617 etc. are adoptions of the database content. National standards bodies issue periodic snapshots of the database under their own designations.

This layer uses the database reference format throughout: `IEC60617-PP-XX-YY`.

---

## Notable Symbol Additions Since 2002

The transition to the database has enabled IEC to add symbols for technologies that did not exist in the 1996 paper editions. Of relevance to this layer:

| Symbol | Approximate added | Reason |
|---|---|---|
| Photovoltaic source (Part 6) | ~2005 | Rise of grid-tied PV installations |
| Wind turbine (Part 6) | ~2006 | Distributed generation |
| LED indicator (Part 8) | ~2010 | Replacement of incandescent indicator lamps |
| EV charging point (Part 11) | ~2018 | EV infrastructure on building plans |
| Battery storage (Part 6, distinct from UPS battery) | ~2020 | Behind-the-meter storage |
| Smart/AMR meter (Part 8) | ~2012 | Distinct symbol from analogue meter |
| SPD Type 1, 2, 3 distinctions (Part 7) | ~2010 | Coordination with IEC 61643-11 SPD classification |

---

## What This Means for Designers Using This Layer

1. **Quote the database reference.** When citing a symbol in design documentation, use the `IEC60617-PP-XX-YY` format from the `iec_ref` field, not the legacy paper-part `fig.` numbering.
2. **National differences are stylistic.** BS EN 60617 and DIN EN 60617 use the same reference numbers as the IEC database. Drawing-style preferences (e.g. North American IEEE/ANSI Y32.2 alternatives) are out of scope for this layer.
3. **Symbol shape stability.** Symbol geometry in this layer is stable across the database revisions — IEC has not historically changed the shape of an established symbol. New symbols use new reference numbers rather than overwriting old ones.
4. **Deprecated symbols.** Where the database flags a symbol as deprecated, this layer either omits it or marks it with `"status": "deprecated"` in a future revision (no deprecated symbols are present in v1.0.0).

---

## National Adoption Status (For Reference Only)

| National code | Country | Relationship to IEC 60617 |
|---|---|---|
| BS EN 60617 | United Kingdom | Direct adoption (CENELEC EN) |
| DIN EN 60617 | Germany | Direct adoption with German titles |
| NF EN 60617 | France | Direct adoption |
| SS-EN 60617 | Sweden | Direct adoption |
| NEN-EN-IEC 60617 | Netherlands | Direct adoption |
| IS/IEC 60617 | India | Direct adoption |
| AS/NZS IEC 60617 | Australia / New Zealand | Direct adoption (limited parts) |
| GB/T 4728 | China | Substantially aligned but with national variations |
| IEEE Std 315 / ANSI Y32.2 | United States | **Different standard** — not aligned with IEC 60617. Out of scope for this layer. |

A skill targeting a region listed above as "direct adoption" can cite the national designation in its drawing legend in addition to the IEC reference — both are correct.
````

- [ ] **Step 2: Commit**

```bash
git add shared/standards/electrical/IEC60617/amendments-summary.md
git commit -m "docs: IEC60617 amendments summary — paper-to-database transition history"
```

---

## Task 6: Create part2-general.json (~25 symbols)

**Files:**
- Create: `shared/standards/electrical/IEC60617/part2-general.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "IEC 60617 Part 2 — Symbol elements, qualifying symbols and other symbols having general application",
  "_iec_part": 2,
  "_version": "1.0.0",
  "_note": "Qualifying symbols (overlays, modifiers) have generating_shared_symbol=false because they are rendered on top of other symbols by the runtime rather than standing alone. Connection points (junctions, terminals) and earth symbols have generating_shared_symbol=true.",
  "symbols": [
    {
      "symbol_id": "JUNCTION_T",
      "iec_ref": "IEC60617-02-02-02",
      "iec_part": 2,
      "iec_description": "Junction of conductors (T)",
      "draftsman_id": "JUNCTION_T",
      "category": "general",
      "display_name": "T-junction (connected)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -50, 50, 5],
        "path": "M -50 0 L 50 0 M 0 0 L 0 -50 M 5 0 A 5 5 0 1 0 -5 0 A 5 5 0 1 0 5 0 Z",
        "terminals": {"h_left": [-50, 0], "h_right": [50, 0], "stem": [0, -50]}
      },
      "variants": ["JUNCTION_CROSS"],
      "annotation_fields": [],
      "usage_notes": "Use at three-way connections where conductors meet. The filled dot is mandatory — absence of the dot indicates wires cross without connecting (use WIRE_CROSSING for that case).",
      "related_symbols": ["JUNCTION_CROSS", "WIRE_CROSSING"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "JUNCTION_CROSS",
      "iec_ref": "IEC60617-02-02-03",
      "iec_part": 2,
      "iec_description": "Junction of conductors (4-way)",
      "draftsman_id": "JUNCTION_CROSS",
      "category": "general",
      "display_name": "Cross junction (connected)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -50, 50, 50],
        "path": "M -50 0 L 50 0 M 0 -50 L 0 50 M 5 0 A 5 5 0 1 0 -5 0 A 5 5 0 1 0 5 0 Z",
        "terminals": {"left": [-50, 0], "right": [50, 0], "top": [0, -50], "bottom": [0, 50]}
      },
      "variants": ["JUNCTION_T"],
      "annotation_fields": [],
      "usage_notes": "Use at four-way connections where conductors meet. Convention varies: many drafting offices avoid the 4-way cross with dot and prefer two staggered T-junctions for clarity. The dot is mandatory if used.",
      "related_symbols": ["JUNCTION_T", "WIRE_CROSSING"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "WIRE_CROSSING",
      "iec_ref": "IEC60617-02-02-01",
      "iec_part": 2,
      "iec_description": "Crossing of conductors without electrical connection",
      "draftsman_id": "WIRE_CROSSING",
      "category": "general",
      "display_name": "Wire crossing (no connection)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -50, 50, 50],
        "path": "M -50 0 L 50 0 M 0 -50 L 0 50",
        "terminals": {"left": [-50, 0], "right": [50, 0], "top": [0, -50], "bottom": [0, 50]}
      },
      "variants": [],
      "annotation_fields": [],
      "usage_notes": "Plain crossing without a dot. Absence of the junction dot signals no electrical connection. Some drafting offices add a small arc (hop) over one conductor for extra clarity — IEC permits both.",
      "related_symbols": ["JUNCTION_T", "JUNCTION_CROSS"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "TERMINAL_SYMBOL",
      "iec_ref": "IEC60617-02-09-02",
      "iec_part": 2,
      "iec_description": "Terminal",
      "draftsman_id": "TERMINAL_SYMBOL",
      "category": "general",
      "display_name": "Terminal",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -5, 5, 5],
        "path": "M -50 0 L -5 0 M 5 0 A 5 5 0 1 0 -5 0 A 5 5 0 1 0 5 0 Z",
        "terminals": {"connect": [-50, 0]}
      },
      "variants": [],
      "annotation_fields": ["tag"],
      "usage_notes": "Marks a physical terminal on a piece of equipment (a screw terminal, a busbar lug). Annotate with the terminal tag (e.g. T1, L1, COM).",
      "related_symbols": ["JUNCTION_T"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "TEST_POINT",
      "iec_ref": "IEC60617-02-09-04",
      "iec_part": 2,
      "iec_description": "Test point",
      "draftsman_id": "TEST_POINT",
      "category": "general",
      "display_name": "Test point",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -30, 50, 5],
        "path": "M -50 0 L 50 0 M 0 -30 L 0 -5 M -8 -15 L 0 -5 L 8 -15",
        "terminals": {"left": [-50, 0], "right": [50, 0]}
      },
      "variants": [],
      "annotation_fields": ["tp_id"],
      "usage_notes": "Use to mark an accessible test point on a circuit. Common at the line side of MCBs for Zs verification.",
      "related_symbols": [],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "VARIABILITY_ARROW",
      "iec_ref": "IEC60617-02-04-01",
      "iec_part": 2,
      "iec_description": "Inherent variability — arrow",
      "draftsman_id": "VARIABILITY_ARROW",
      "category": "general",
      "display_name": "Variability arrow (qualifying)",
      "geometry": {
        "grid": 100,
        "bbox": [-30, -30, 30, 30],
        "path": "M -30 30 L 30 -30 M 15 -30 L 30 -30 L 30 -15",
        "terminals": {}
      },
      "variants": ["ADJUSTABILITY_MARKER"],
      "annotation_fields": [],
      "usage_notes": "Overlay symbol indicating the parent device's value varies inherently with operating conditions (e.g. thermistor). Drawn diagonally across the parent symbol.",
      "related_symbols": ["ADJUSTABILITY_MARKER"],
      "generating_shared_symbol": false
    },
    {
      "symbol_id": "ADJUSTABILITY_MARKER",
      "iec_ref": "IEC60617-02-04-02",
      "iec_part": 2,
      "iec_description": "Adjustability — arrow with perpendicular bar",
      "draftsman_id": "ADJUSTABILITY_MARKER",
      "category": "general",
      "display_name": "Adjustability marker (qualifying)",
      "geometry": {
        "grid": 100,
        "bbox": [-25, -25, 25, 25],
        "path": "M -25 25 L 25 -25 M 10 -25 L 25 -25 L 25 -10 M -5 5 L 5 -5",
        "terminals": {}
      },
      "variants": ["VARIABILITY_ARROW"],
      "annotation_fields": [],
      "usage_notes": "Overlay symbol indicating the parent device is user-adjustable (e.g. variable resistor, adjustable trip MCCB). The perpendicular cross-bar distinguishes from inherent variability.",
      "related_symbols": ["VARIABILITY_ARROW"],
      "generating_shared_symbol": false
    },
    {
      "symbol_id": "POLARITY_PLUS",
      "iec_ref": "IEC60617-02-05-01",
      "iec_part": 2,
      "iec_description": "Positive polarity",
      "draftsman_id": "POLARITY_PLUS",
      "category": "general",
      "display_name": "Positive polarity (+)",
      "geometry": {
        "grid": 100,
        "bbox": [-15, -15, 15, 15],
        "path": "M 0 -15 L 0 15 M -15 0 L 15 0",
        "terminals": {}
      },
      "variants": ["POLARITY_MINUS"],
      "annotation_fields": [],
      "usage_notes": "Label symbol for DC positive polarity. Place adjacent to the terminal it marks.",
      "related_symbols": ["POLARITY_MINUS", "BATTERY"],
      "generating_shared_symbol": false
    },
    {
      "symbol_id": "POLARITY_MINUS",
      "iec_ref": "IEC60617-02-05-02",
      "iec_part": 2,
      "iec_description": "Negative polarity",
      "draftsman_id": "POLARITY_MINUS",
      "category": "general",
      "display_name": "Negative polarity (-)",
      "geometry": {
        "grid": 100,
        "bbox": [-15, -5, 15, 5],
        "path": "M -15 0 L 15 0",
        "terminals": {}
      },
      "variants": ["POLARITY_PLUS"],
      "annotation_fields": [],
      "usage_notes": "Label symbol for DC negative polarity. Place adjacent to the terminal it marks.",
      "related_symbols": ["POLARITY_PLUS", "BATTERY"],
      "generating_shared_symbol": false
    },
    {
      "symbol_id": "FUNCTIONAL_GROUP",
      "iec_ref": "IEC60617-02-07-01",
      "iec_part": 2,
      "iec_description": "Functional grouping — dashed boundary",
      "draftsman_id": "FUNCTIONAL_GROUP",
      "category": "general",
      "display_name": "Functional grouping (dashed)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -50, 50, 50],
        "path": "M -50 -50 L 50 -50 L 50 50 L -50 50 Z",
        "terminals": {}
      },
      "variants": ["ENCLOSURE_DOTTED"],
      "annotation_fields": ["group_label"],
      "usage_notes": "Dashed rectangular boundary around a set of related symbols (e.g. all components inside one enclosure, a functional unit such as a star-delta starter). The runtime renders with dashed line style.",
      "related_symbols": ["ENCLOSURE_DOTTED"],
      "generating_shared_symbol": false
    },
    {
      "symbol_id": "ENCLOSURE_DOTTED",
      "iec_ref": "IEC60617-02-07-02",
      "iec_part": 2,
      "iec_description": "Enclosure boundary — dotted",
      "draftsman_id": "ENCLOSURE_DOTTED",
      "category": "general",
      "display_name": "Enclosure boundary (dotted)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -50, 50, 50],
        "path": "M -50 -50 L 50 -50 L 50 50 L -50 50 Z",
        "terminals": {}
      },
      "variants": ["FUNCTIONAL_GROUP"],
      "annotation_fields": ["enclosure_label", "IP_rating"],
      "usage_notes": "Dotted rectangular boundary around a physical enclosure (e.g. all components inside a panel cabinet). Distinct from FUNCTIONAL_GROUP — that is dashed and indicates a functional unit, this is dotted and indicates a physical container.",
      "related_symbols": ["FUNCTIONAL_GROUP"],
      "generating_shared_symbol": false
    },
    {
      "symbol_id": "SHIELD_SYMBOL",
      "iec_ref": "IEC60617-02-06-01",
      "iec_part": 2,
      "iec_description": "Shielding (general)",
      "draftsman_id": "SHIELD_SYMBOL",
      "category": "general",
      "display_name": "Shield / screen (qualifying)",
      "geometry": {
        "grid": 100,
        "bbox": [-40, -30, 40, 30],
        "path": "M -20 -30 L -40 -30 L -40 30 L -20 30 M 20 -30 L 40 -30 L 40 30 L 20 30",
        "terminals": {}
      },
      "variants": ["SCREEN_CONDUCTOR"],
      "annotation_fields": [],
      "usage_notes": "Overlay symbol indicating the parent component is electrostatically shielded. Drawn as two open bracket shapes flanking the parent.",
      "related_symbols": ["SCREEN_CONDUCTOR"],
      "generating_shared_symbol": false
    },
    {
      "symbol_id": "SCREEN_CONDUCTOR",
      "iec_ref": "IEC60617-02-06-02",
      "iec_part": 2,
      "iec_description": "Screened conductor",
      "draftsman_id": "SCREEN_CONDUCTOR",
      "category": "general",
      "display_name": "Screened conductor",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -8, 50, 8],
        "path": "M -50 0 L 50 0 M -30 -8 L -30 8 M -10 -8 L -10 8 M 10 -8 L 10 8 M 30 -8 L 30 8",
        "terminals": {"start": [-50, 0], "end": [50, 0]}
      },
      "variants": [],
      "annotation_fields": [],
      "usage_notes": "Conductor with electrostatic screen. Tick marks along the length indicate the screen wrap. Use for instrument cables, control cables in noisy environments.",
      "related_symbols": ["CONDUCTOR_SINGLE", "SHIELD_SYMBOL", "CONDUCTOR_COAX"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "EARTH_GENERAL",
      "iec_ref": "IEC60617-02-15-01",
      "iec_part": 2,
      "iec_description": "Earth (general)",
      "draftsman_id": "EARTH_GENERAL",
      "category": "general",
      "display_name": "Earth (general)",
      "geometry": {
        "grid": 100,
        "bbox": [-25, -50, 25, 25],
        "path": "M 0 -50 L 0 0 M -25 0 L 25 0 M -15 10 L 15 10 M -8 20 L 8 20",
        "terminals": {"line": [0, -50]}
      },
      "variants": ["EARTH_PROTECTIVE", "EARTH_CLEAN", "EARTH_CHASSIS"],
      "annotation_fields": [],
      "usage_notes": "General-purpose earth symbol. Three horizontal bars decreasing in length. Use where the earth nature is unspecified or for the building's main earthing terminal.",
      "related_symbols": ["EARTH_PROTECTIVE", "EARTH_CLEAN", "EARTH_CHASSIS", "EARTH_ELECTRODE"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "EARTH_PROTECTIVE",
      "iec_ref": "IEC60617-02-15-02",
      "iec_part": 2,
      "iec_description": "Protective earth (PE)",
      "draftsman_id": "EARTH_PROTECTIVE",
      "category": "general",
      "display_name": "Protective earth (PE)",
      "geometry": {
        "grid": 100,
        "bbox": [-25, -50, 25, 25],
        "path": "M 0 -50 L 0 -5 M -25 -5 L 25 -5 M -15 5 L 15 5 M -8 15 L 8 15 M -20 -25 A 20 20 0 1 0 20 -25 A 20 20 0 1 0 -20 -25 Z",
        "terminals": {"line": [0, -50]}
      },
      "variants": ["EARTH_GENERAL", "EARTH_CLEAN", "EARTH_CHASSIS"],
      "annotation_fields": [],
      "usage_notes": "Protective earth — earth used for shock protection (the CPC system). The enclosing circle distinguishes from EARTH_GENERAL. Required at all Class I equipment exposed-conductive-parts.",
      "related_symbols": ["EARTH_GENERAL", "EARTH_ELECTRODE", "CONDUCTOR_PE"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "EARTH_CLEAN",
      "iec_ref": "IEC60617-02-15-04",
      "iec_part": 2,
      "iec_description": "Noiseless (clean) earth",
      "draftsman_id": "EARTH_CLEAN",
      "category": "general",
      "display_name": "Clean / noiseless earth",
      "geometry": {
        "grid": 100,
        "bbox": [-25, -50, 25, 25],
        "path": "M 0 -50 L 0 0 M -25 0 L 25 0 L 0 25 Z",
        "terminals": {"line": [0, -50]}
      },
      "variants": ["EARTH_GENERAL", "EARTH_PROTECTIVE", "EARTH_CHASSIS"],
      "annotation_fields": [],
      "usage_notes": "Clean earth — a separate low-noise earth used for sensitive electronic equipment (data centres, hospital electromedical Group 2). Triangle shape distinguishes from PE. Do not connect to PE except at one defined point.",
      "related_symbols": ["EARTH_GENERAL", "EARTH_PROTECTIVE"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "EARTH_CHASSIS",
      "iec_ref": "IEC60617-02-15-03",
      "iec_part": 2,
      "iec_description": "Chassis (frame) earth",
      "draftsman_id": "EARTH_CHASSIS",
      "category": "general",
      "display_name": "Chassis earth",
      "geometry": {
        "grid": 100,
        "bbox": [-25, -50, 25, 15],
        "path": "M 0 -50 L 0 0 M -20 0 L 20 0 M -20 0 L -25 15 M -10 0 L -10 15 M 0 0 L 0 15 M 10 0 L 10 15 M 20 0 L 25 15",
        "terminals": {"line": [0, -50]}
      },
      "variants": ["EARTH_GENERAL", "EARTH_PROTECTIVE"],
      "annotation_fields": [],
      "usage_notes": "Chassis or frame earth — bond to equipment frame, not necessarily connected to the electrical earth network. Used for equipotential bonding within an enclosure.",
      "related_symbols": ["EARTH_GENERAL", "EARTH_PROTECTIVE"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "NOT_CONNECTED",
      "iec_ref": "IEC60617-02-09-01",
      "iec_part": 2,
      "iec_description": "Terminal not connected",
      "draftsman_id": "NOT_CONNECTED",
      "category": "general",
      "display_name": "Not connected (X marker)",
      "geometry": {
        "grid": 100,
        "bbox": [-10, -10, 10, 10],
        "path": "M -10 -10 L 10 10 M -10 10 L 10 -10",
        "terminals": {}
      },
      "variants": [],
      "annotation_fields": [],
      "usage_notes": "X-mark placed at the end of a conductor or on a terminal to indicate it is intentionally not connected (e.g. a spare contact on a relay).",
      "related_symbols": ["TERMINAL_SYMBOL"],
      "generating_shared_symbol": false
    },
    {
      "symbol_id": "COMMON_RETURN",
      "iec_ref": "IEC60617-02-13-01",
      "iec_part": 2,
      "iec_description": "Common return / bus",
      "draftsman_id": "COMMON_RETURN",
      "category": "general",
      "display_name": "Common return bus",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -3, 50, 3],
        "path": "M -50 0 L 50 0",
        "terminals": {"start": [-50, 0], "end": [50, 0]}
      },
      "variants": ["BUSBAR"],
      "annotation_fields": ["bus_id"],
      "usage_notes": "Thick horizontal line representing a common return or shared bus. Distinct from BUSBAR — this is the schematic single-line representation of any shared connection point. Annotate with the bus identifier.",
      "related_symbols": ["BUSBAR", "BUSBAR_3PH"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "SIGNAL_LEVEL",
      "iec_ref": "IEC60617-02-13-04",
      "iec_part": 2,
      "iec_description": "Signal level / arrow",
      "draftsman_id": "SIGNAL_LEVEL",
      "category": "general",
      "display_name": "Signal level indicator",
      "geometry": {
        "grid": 100,
        "bbox": [-15, -15, 15, 15],
        "path": "M -15 -15 L 0 0 L -15 15 M 0 -15 L 15 0 L 0 15",
        "terminals": {}
      },
      "variants": [],
      "annotation_fields": ["level"],
      "usage_notes": "Qualifying symbol indicating a signal at a defined level (e.g. logic high, control signal). Used in control schematics. Annotate with the level value.",
      "related_symbols": [],
      "generating_shared_symbol": false
    },
    {
      "symbol_id": "FILTER_GENERAL",
      "iec_ref": "IEC60617-02-12-01",
      "iec_part": 2,
      "iec_description": "Filter (general)",
      "draftsman_id": "FILTER_GENERAL",
      "category": "general",
      "display_name": "Filter (general)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -20, 50, 20],
        "path": "M -50 0 L -20 0 M -20 -20 L 20 -20 L 20 20 L -20 20 Z M -20 -20 L 20 20 M -20 20 L 20 -20 M 20 0 L 50 0",
        "terminals": {"in": [-50, 0], "out": [50, 0]}
      },
      "variants": [],
      "annotation_fields": ["filter_type", "cutoff_Hz"],
      "usage_notes": "Generic filter symbol — a rectangle with internal X. Annotate type (LPF/HPF/BPF/notch) and cut-off frequency. Used for harmonic filters, EMC filters in LV distribution.",
      "related_symbols": [],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "COAX_CONNECTOR",
      "iec_ref": "IEC60617-02-09-05",
      "iec_part": 2,
      "iec_description": "Coaxial connection point",
      "draftsman_id": "COAX_CONNECTOR",
      "category": "general",
      "display_name": "Coaxial connector",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -12, 12, 12],
        "path": "M -50 0 L -12 0 M 12 0 A 12 12 0 1 0 -12 0 A 12 12 0 1 0 12 0 Z M 3 0 A 3 3 0 1 0 -3 0 A 3 3 0 1 0 3 0 Z",
        "terminals": {"signal": [-50, 0]}
      },
      "variants": [],
      "annotation_fields": ["conn_type"],
      "usage_notes": "Coaxial connector face — outer ring is shield, inner dot is signal core. Annotate connector type (BNC, N, F, SMA). Rare in MEP building but appears on instrument distribution.",
      "related_symbols": ["CONDUCTOR_COAX"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "OPTIONAL_PATH",
      "iec_ref": "IEC60617-02-13-02",
      "iec_part": 2,
      "iec_description": "Optional / alternative path",
      "draftsman_id": "OPTIONAL_PATH",
      "category": "general",
      "display_name": "Optional path (dashed line)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -3, 50, 3],
        "path": "M -50 0 L 50 0",
        "terminals": {"start": [-50, 0], "end": [50, 0]}
      },
      "variants": [],
      "annotation_fields": ["condition"],
      "usage_notes": "Dashed line representing an optional or alternative circuit path (e.g. spare circuit, future connection). Runtime renders with dashed line style.",
      "related_symbols": ["CONDUCTOR_SINGLE"],
      "generating_shared_symbol": false
    },
    {
      "symbol_id": "DELAY_SYMBOL",
      "iec_ref": "IEC60617-02-12-03",
      "iec_part": 2,
      "iec_description": "Delay (general)",
      "draftsman_id": "DELAY_SYMBOL",
      "category": "general",
      "display_name": "Delay element (qualifying)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -15, 50, 15],
        "path": "M -50 0 L -20 0 M -20 -15 L 20 -15 L 20 15 L -20 15 Z M -10 0 L 10 0 M 20 0 L 50 0",
        "terminals": {"in": [-50, 0], "out": [50, 0]}
      },
      "variants": [],
      "annotation_fields": ["delay_s"],
      "usage_notes": "Qualifying symbol for a delay element. The arrow inside indicates direction of signal flow with a time delay. Annotate the delay duration.",
      "related_symbols": ["CONTACT_ON_DELAY", "CONTACT_OFF_DELAY"],
      "generating_shared_symbol": false
    },
    {
      "symbol_id": "FAULT_INDICATOR",
      "iec_ref": "IEC60617-02-12-05",
      "iec_part": 2,
      "iec_description": "Fault / failure indication",
      "draftsman_id": "FAULT_INDICATOR",
      "category": "general",
      "display_name": "Fault indicator (qualifying)",
      "geometry": {
        "grid": 100,
        "bbox": [-20, -20, 20, 20],
        "path": "M -15 -15 L 15 15 M -15 15 L 15 -15 M 20 0 A 20 20 0 1 0 -20 0 A 20 20 0 1 0 20 0 Z",
        "terminals": {}
      },
      "variants": [],
      "annotation_fields": [],
      "usage_notes": "Circle with internal X — overlay symbol indicating fault detection or fault state. Used on relay logic and protection schematics.",
      "related_symbols": ["RELAY_GENERAL"],
      "generating_shared_symbol": false
    }
  ]
}
```

- [ ] **Step 2: Validate JSON syntax**

Run: `python3 -c "import json; json.load(open('shared/standards/electrical/IEC60617/part2-general.json'))" && echo OK`
Expected: `OK`

- [ ] **Step 3: Verify symbol count**

Run: `python3 -c "import json; print(len(json.load(open('shared/standards/electrical/IEC60617/part2-general.json'))['symbols']))"`
Expected: `25`

- [ ] **Step 4: Verify all schema fields present**

Run: `python3 -c "import json; data=json.load(open('shared/standards/electrical/IEC60617/part2-general.json')); req=['symbol_id','iec_ref','iec_part','iec_description','draftsman_id','category','display_name','geometry','variants','annotation_fields','usage_notes','related_symbols','generating_shared_symbol']; missing=[(s.get('symbol_id','?'), [f for f in req if f not in s]) for s in data['symbols'] if any(f not in s for f in req)]; print('OK' if not missing else 'MISSING:'+str(missing))"`
Expected: `OK`

- [ ] **Step 5: Commit**

```bash
git add shared/standards/electrical/IEC60617/part2-general.json
git commit -m "feat: IEC60617 part2-general.json — 25 qualifying and general symbols"
```

---

## Task 7: Create part3-conductors.json (~30 symbols)

**Files:**
- Create: `shared/standards/electrical/IEC60617/part3-conductors.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "IEC 60617 Part 3 — Conductors and connecting devices",
  "_iec_part": 3,
  "_version": "1.0.0",
  "symbols": [
    {
      "symbol_id": "CONDUCTOR_SINGLE",
      "iec_ref": "IEC60617-03-01-01",
      "iec_part": 3,
      "iec_description": "Conductor (line, group of lines, cable)",
      "draftsman_id": "CONDUCTOR_SINGLE",
      "category": "conductor",
      "display_name": "Single conductor",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -2, 50, 2],
        "path": "M -50 0 L 50 0",
        "terminals": {"start": [-50, 0], "end": [50, 0]}
      },
      "variants": ["CONDUCTOR_2CORE", "CONDUCTOR_3CORE", "CONDUCTOR_4CORE", "CONDUCTOR_NCORE"],
      "annotation_fields": ["csa_mm2", "insulation", "tag"],
      "usage_notes": "The fundamental conductor symbol. On SLDs, a single line represents the whole circuit (line + neutral + CPC). On schematics, one line per conductor. Annotate with CSA and insulation type.",
      "related_symbols": ["BUSBAR", "CONDUCTOR_NEUTRAL", "CONDUCTOR_PE"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "CONDUCTOR_2CORE",
      "iec_ref": "IEC60617-03-01-02",
      "iec_part": 3,
      "iec_description": "Two conductors",
      "draftsman_id": "CONDUCTOR_2CORE",
      "category": "conductor",
      "display_name": "2-core cable",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -5, 50, 5],
        "path": "M -50 -3 L 50 -3 M -50 3 L 50 3",
        "terminals": {"start_1": [-50, -3], "start_2": [-50, 3], "end_1": [50, -3], "end_2": [50, 3]}
      },
      "variants": ["CONDUCTOR_SINGLE", "CONDUCTOR_3CORE", "CONDUCTOR_4CORE"],
      "annotation_fields": ["csa_mm2", "insulation", "tag"],
      "usage_notes": "Two parallel lines for a 2-core cable (e.g. L+N, or twin twisted pair).",
      "related_symbols": ["CONDUCTOR_3CORE", "CONDUCTOR_4CORE"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "CONDUCTOR_3CORE",
      "iec_ref": "IEC60617-03-01-03",
      "iec_part": 3,
      "iec_description": "Three conductors",
      "draftsman_id": "CONDUCTOR_3CORE",
      "category": "conductor",
      "display_name": "3-core cable",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -8, 50, 8],
        "path": "M -50 -6 L 50 -6 M -50 0 L 50 0 M -50 6 L 50 6",
        "terminals": {"start": [-50, 0], "end": [50, 0]}
      },
      "variants": ["CONDUCTOR_2CORE", "CONDUCTOR_4CORE"],
      "annotation_fields": ["csa_mm2", "insulation", "tag"],
      "usage_notes": "Three parallel lines for a 3-core cable (L1+L2+L3, or L+N+CPC).",
      "related_symbols": ["CONDUCTOR_2CORE", "CONDUCTOR_4CORE"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "CONDUCTOR_4CORE",
      "iec_ref": "IEC60617-03-01-04",
      "iec_part": 3,
      "iec_description": "Four conductors",
      "draftsman_id": "CONDUCTOR_4CORE",
      "category": "conductor",
      "display_name": "4-core cable",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -12, 50, 12],
        "path": "M -50 -9 L 50 -9 M -50 -3 L 50 -3 M -50 3 L 50 3 M -50 9 L 50 9",
        "terminals": {"start": [-50, 0], "end": [50, 0]}
      },
      "variants": ["CONDUCTOR_3CORE", "CONDUCTOR_NCORE"],
      "annotation_fields": ["csa_mm2", "insulation", "tag"],
      "usage_notes": "Four parallel lines for a 4-core cable (L1+L2+L3+N, or L1+L2+L3+CPC).",
      "related_symbols": ["CONDUCTOR_3CORE", "CONDUCTOR_NCORE"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "CONDUCTOR_NCORE",
      "iec_ref": "IEC60617-03-01-05",
      "iec_part": 3,
      "iec_description": "Conductors with slash and count (n)",
      "draftsman_id": "CONDUCTOR_NCORE",
      "category": "conductor",
      "display_name": "Multi-core cable (n-core)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -20, 50, 20],
        "path": "M -50 0 L 50 0 M -10 -20 L 10 20",
        "terminals": {"start": [-50, 0], "end": [50, 0]}
      },
      "variants": ["CONDUCTOR_2CORE", "CONDUCTOR_3CORE", "CONDUCTOR_4CORE"],
      "annotation_fields": ["core_count", "csa_mm2", "insulation", "tag"],
      "usage_notes": "Compact representation when core count is high (e.g. 5-core, 7-core, 19-core). Single line with diagonal slash; annotate count above the slash. Use for control multi-core, screened instrumentation cables.",
      "related_symbols": ["CONDUCTOR_4CORE"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "BUSBAR",
      "iec_ref": "IEC60617-03-02-01",
      "iec_part": 3,
      "iec_description": "Busbar",
      "draftsman_id": "BUSBAR",
      "category": "conductor",
      "display_name": "Busbar (single)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -4, 50, 4],
        "path": "M -50 0 L 50 0",
        "terminals": {"start": [-50, 0], "end": [50, 0]}
      },
      "variants": ["BUSBAR_3PH", "BUSDUCT"],
      "annotation_fields": ["bus_id", "rated_A", "material"],
      "usage_notes": "Heavy horizontal line. Rendered at thick lineweight to distinguish from a normal conductor. Use for the main bus of a switchboard or distribution board.",
      "related_symbols": ["BUSBAR_3PH", "COMMON_RETURN", "BUSDUCT"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "BUSBAR_3PH",
      "iec_ref": "IEC60617-03-02-02",
      "iec_part": 3,
      "iec_description": "Three-phase busbar",
      "draftsman_id": "BUSBAR_3PH",
      "category": "conductor",
      "display_name": "3-phase busbar",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -12, 50, 12],
        "path": "M -50 -8 L 50 -8 M -50 0 L 50 0 M -50 8 L 50 8",
        "terminals": {"L1": [-50, -8], "L2": [-50, 0], "L3": [-50, 8], "L1_end": [50, -8], "L2_end": [50, 0], "L3_end": [50, 8]}
      },
      "variants": ["BUSBAR", "BUSDUCT"],
      "annotation_fields": ["bus_id", "rated_A", "material"],
      "usage_notes": "Three parallel heavy lines representing L1, L2, L3 in a 3-phase busbar arrangement. Add CONDUCTOR_NEUTRAL and CONDUCTOR_PE separately if a 4-wire or 5-wire system.",
      "related_symbols": ["BUSBAR", "CONDUCTOR_NEUTRAL", "CONDUCTOR_PE"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "CONDUCTOR_IN_CONDUIT",
      "iec_ref": "IEC60617-03-03-01",
      "iec_part": 3,
      "iec_description": "Conductor enclosed in conduit",
      "draftsman_id": "CONDUCTOR_IN_CONDUIT",
      "category": "conductor",
      "display_name": "Conductor in conduit",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -15, 50, 15],
        "path": "M -50 0 L 50 0 M 15 0 A 15 15 0 1 0 -15 0 A 15 15 0 1 0 15 0 Z",
        "terminals": {"start": [-50, 0], "end": [50, 0]}
      },
      "variants": ["CONDUCTOR_IN_DUCT", "CONDUIT"],
      "annotation_fields": ["conduit_dia_mm", "csa_mm2"],
      "usage_notes": "Indicates the conductor is enclosed in a conduit run. Annotate conduit diameter. The circle is a section view of the conduit.",
      "related_symbols": ["CONDUIT", "CONDUCTOR_IN_DUCT"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "CONDUCTOR_IN_DUCT",
      "iec_ref": "IEC60617-03-03-02",
      "iec_part": 3,
      "iec_description": "Conductor in duct or trunking",
      "draftsman_id": "CONDUCTOR_IN_DUCT",
      "category": "conductor",
      "display_name": "Conductor in duct/trunking",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -10, 50, 10],
        "path": "M -50 0 L 50 0 M -20 -10 L 20 -10 L 20 10 L -20 10 Z",
        "terminals": {"start": [-50, 0], "end": [50, 0]}
      },
      "variants": ["TRUNKING", "CABLE_DUCT"],
      "annotation_fields": ["duct_size", "csa_mm2"],
      "usage_notes": "Indicates conductor in a duct, trunking, or wireway. Rectangle is a section view.",
      "related_symbols": ["TRUNKING", "CABLE_DUCT"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "CONDUCTOR_GROUPED",
      "iec_ref": "IEC60617-03-01-06",
      "iec_part": 3,
      "iec_description": "Grouped conductors",
      "draftsman_id": "CONDUCTOR_GROUPED",
      "category": "conductor",
      "display_name": "Grouped conductors",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -10, 50, 10],
        "path": "M -50 -6 L 50 -6 M -50 0 L 50 0 M -50 6 L 50 6 M 0 -10 A 10 10 0 0 1 0 10",
        "terminals": {"start": [-50, 0], "end": [50, 0]}
      },
      "variants": ["CONDUCTOR_3CORE", "CONDUCTOR_4CORE"],
      "annotation_fields": ["core_count", "csa_mm2"],
      "usage_notes": "Multiple conductors bundled together (e.g. clipped together but not in a common sheath). Arc indicates grouping. Use where derating factor for grouping applies.",
      "related_symbols": ["CONDUCTOR_3CORE", "CONDUCTOR_4CORE"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "CONDUCTOR_ARMOURED",
      "iec_ref": "IEC60617-03-01-07",
      "iec_part": 3,
      "iec_description": "Armoured cable",
      "draftsman_id": "CONDUCTOR_ARMOURED",
      "category": "conductor",
      "display_name": "Armoured cable (SWA)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -8, 50, 8],
        "path": "M -50 0 L 50 0 M -25 -8 L -25 8 M -15 -8 L -15 8 M -5 -8 L -5 8 M 5 -8 L 5 8 M 15 -8 L 15 8 M 25 -8 L 25 8",
        "terminals": {"start": [-50, 0], "end": [50, 0]}
      },
      "variants": ["CONDUCTOR_SINGLE"],
      "annotation_fields": ["core_count", "csa_mm2", "armour_type"],
      "usage_notes": "Conductor with steel wire (SWA) or aluminium wire (AWA) armour. Tick marks indicate the armour layer. Common for underground, outdoor, and industrial cabling. Armour is bonded to PE at both ends.",
      "related_symbols": ["CONDUCTOR_SINGLE", "CONDUCTOR_UNDERGROUND"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "CONDUCTOR_OVERHEAD",
      "iec_ref": "IEC60617-03-03-04",
      "iec_part": 3,
      "iec_description": "Overhead line",
      "draftsman_id": "CONDUCTOR_OVERHEAD",
      "category": "conductor",
      "display_name": "Overhead line",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -20, 50, 5],
        "path": "M -50 0 L 50 0 M -20 0 L -20 -15 M -25 -15 L -15 -15 M 20 0 L 20 -15 M 15 -15 L 25 -15",
        "terminals": {"start": [-50, 0], "end": [50, 0]}
      },
      "variants": ["CONDUCTOR_UNDERGROUND", "CONDUCTOR_SINGLE"],
      "annotation_fields": ["csa_mm2", "pole_spacing"],
      "usage_notes": "Conductor strung overhead on poles or pylons. The cross-bars represent insulator supports. Use for service drop from DNO overhead network, site overhead distribution.",
      "related_symbols": ["CONDUCTOR_UNDERGROUND", "CONDUCTOR_SINGLE"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "CONDUCTOR_UNDERGROUND",
      "iec_ref": "IEC60617-03-03-05",
      "iec_part": 3,
      "iec_description": "Underground line",
      "draftsman_id": "CONDUCTOR_UNDERGROUND",
      "category": "conductor",
      "display_name": "Underground cable",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -3, 50, 15],
        "path": "M -50 0 L 50 0 M -25 0 L -25 12 M 0 0 L 0 12 M 25 0 L 25 12",
        "terminals": {"start": [-50, 0], "end": [50, 0]}
      },
      "variants": ["CONDUCTOR_OVERHEAD", "CONDUCTOR_ARMOURED"],
      "annotation_fields": ["csa_mm2", "depth_mm"],
      "usage_notes": "Conductor laid underground. Vertical ticks represent earth/buried marker. Use for service feed from utility, site distribution mains, EV charging supply runs.",
      "related_symbols": ["CONDUCTOR_OVERHEAD", "CONDUCTOR_ARMOURED"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "CONDUCTOR_FLEXIBLE",
      "iec_ref": "IEC60617-03-01-08",
      "iec_part": 3,
      "iec_description": "Flexible connection",
      "draftsman_id": "CONDUCTOR_FLEXIBLE",
      "category": "conductor",
      "display_name": "Flexible connection",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -10, 50, 10],
        "path": "M -50 0 L -40 0 L -30 -8 L -20 8 L -10 -8 L 0 8 L 10 -8 L 20 8 L 30 -8 L 40 0 L 50 0",
        "terminals": {"start": [-50, 0], "end": [50, 0]}
      },
      "variants": ["CONDUCTOR_SINGLE"],
      "annotation_fields": ["csa_mm2", "length_m"],
      "usage_notes": "Wavy/zigzag line representing a flexible cable connection (e.g. between a fixed wiring system and a vibrating/moving piece of equipment such as a motor on a slide rail, or a robot arm).",
      "related_symbols": ["CONDUCTOR_SINGLE"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "CONDUCTOR_EARTH",
      "iec_ref": "IEC60617-03-01-09",
      "iec_part": 3,
      "iec_description": "Earth conductor",
      "draftsman_id": "CONDUCTOR_EARTH",
      "category": "conductor",
      "display_name": "Earth conductor",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -10, 50, 10],
        "path": "M -50 0 L 50 0 M -10 -10 L 10 10 M 10 -10 L -10 10",
        "terminals": {"start": [-50, 0], "end": [50, 0]}
      },
      "variants": ["CONDUCTOR_PE", "CONDUCTOR_PEN", "CONDUCTOR_NEUTRAL"],
      "annotation_fields": ["csa_mm2", "colour"],
      "usage_notes": "Earth conductor — generic. For protective earth specifically, prefer CONDUCTOR_PE. For the combined PEN, use CONDUCTOR_PEN.",
      "related_symbols": ["CONDUCTOR_PE", "CONDUCTOR_PEN", "EARTH_GENERAL"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "CONDUCTOR_NEUTRAL",
      "iec_ref": "IEC60617-03-01-10",
      "iec_part": 3,
      "iec_description": "Neutral conductor",
      "draftsman_id": "CONDUCTOR_NEUTRAL",
      "category": "conductor",
      "display_name": "Neutral conductor",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -10, 50, 10],
        "path": "M -50 0 L 50 0 M -10 -10 L -10 10 L 10 -10 L 10 10",
        "terminals": {"start": [-50, 0], "end": [50, 0]}
      },
      "variants": ["CONDUCTOR_EARTH", "CONDUCTOR_PE", "CONDUCTOR_PEN"],
      "annotation_fields": ["csa_mm2", "colour"],
      "usage_notes": "Neutral conductor. The 'N' shape marker distinguishes from earth and live conductors. Colour code: blue (IEC). Annotate CSA; in harmonic-rich circuits the neutral may need oversizing.",
      "related_symbols": ["CONDUCTOR_PE", "CONDUCTOR_PEN", "CONDUCTOR_SINGLE"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "CONDUCTOR_PE",
      "iec_ref": "IEC60617-03-01-11",
      "iec_part": 3,
      "iec_description": "Protective earth conductor",
      "draftsman_id": "CONDUCTOR_PE",
      "category": "conductor",
      "display_name": "PE conductor",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -10, 50, 10],
        "path": "M -50 0 L 50 0 M -10 -10 L 10 10 M 10 -10 L -10 10 M -15 5 L -15 -5 M 15 5 L 15 -5",
        "terminals": {"start": [-50, 0], "end": [50, 0]}
      },
      "variants": ["CONDUCTOR_EARTH", "CONDUCTOR_PEN", "CONDUCTOR_NEUTRAL"],
      "annotation_fields": ["csa_mm2", "colour"],
      "usage_notes": "Protective earth (CPC) conductor. Colour code: green/yellow. Minimum size determined by IEC 60364-5-54 Table 54.1 vs line conductor.",
      "related_symbols": ["EARTH_PROTECTIVE", "CONDUCTOR_PEN", "CONDUCTOR_NEUTRAL"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "CONDUCTOR_PEN",
      "iec_ref": "IEC60617-03-01-12",
      "iec_part": 3,
      "iec_description": "PEN conductor (combined protective and neutral)",
      "draftsman_id": "CONDUCTOR_PEN",
      "category": "conductor",
      "display_name": "PEN conductor",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -10, 50, 10],
        "path": "M -50 0 L 50 0 M -10 -10 L -10 10 L 10 -10 L 10 10 M -20 5 L -20 -5 M 20 5 L 20 -5",
        "terminals": {"start": [-50, 0], "end": [50, 0]}
      },
      "variants": ["CONDUCTOR_EARTH", "CONDUCTOR_PE", "CONDUCTOR_NEUTRAL"],
      "annotation_fields": ["csa_mm2", "colour"],
      "usage_notes": "Combined PEN conductor (used in TN-C systems and TN-C-S supply side). Combines functions of N and PE. Once separated downstream, must not be re-combined. Minimum CSA 10mm² Cu or 16mm² Al.",
      "related_symbols": ["CONDUCTOR_PE", "CONDUCTOR_NEUTRAL"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "CONDUCTOR_DRAIN",
      "iec_ref": "IEC60617-03-01-13",
      "iec_part": 3,
      "iec_description": "Drain wire (for screen)",
      "draftsman_id": "CONDUCTOR_DRAIN",
      "category": "conductor",
      "display_name": "Drain wire",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -3, 50, 8],
        "path": "M -50 0 L 50 0 M -50 6 L 50 6",
        "terminals": {"signal": [-50, 0], "drain": [-50, 6], "signal_end": [50, 0], "drain_end": [50, 6]}
      },
      "variants": ["SCREEN_CONDUCTOR"],
      "annotation_fields": ["csa_mm2"],
      "usage_notes": "Drain wire associated with a screened cable — bonded to screen at one end (typically the source). Used on instrumentation cables.",
      "related_symbols": ["SCREEN_CONDUCTOR", "CONDUCTOR_COAX"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "CONDUCTOR_COAX",
      "iec_ref": "IEC60617-03-01-14",
      "iec_part": 3,
      "iec_description": "Coaxial cable",
      "draftsman_id": "CONDUCTOR_COAX",
      "category": "conductor",
      "display_name": "Coaxial cable",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -15, 50, 15],
        "path": "M -50 0 L 50 0 M 15 0 A 15 15 0 1 0 -15 0 A 15 15 0 1 0 15 0 Z M 5 0 A 5 5 0 1 0 -5 0 A 5 5 0 1 0 5 0 Z",
        "terminals": {"start": [-50, 0], "end": [50, 0]}
      },
      "variants": ["SCREEN_CONDUCTOR"],
      "annotation_fields": ["impedance_ohm", "csa_mm2"],
      "usage_notes": "Coaxial cable — inner conductor inside grounded outer conductor. Annotate characteristic impedance (50Ω or 75Ω). Used for HF and RF signal runs.",
      "related_symbols": ["COAX_CONNECTOR", "SCREEN_CONDUCTOR"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "CONDUCTOR_MINERAL",
      "iec_ref": "IEC60617-03-01-15",
      "iec_part": 3,
      "iec_description": "Mineral insulated cable (MICC)",
      "draftsman_id": "CONDUCTOR_MINERAL",
      "category": "conductor",
      "display_name": "Mineral insulated cable",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -6, 50, 6],
        "path": "M -50 0 L 50 0 M -50 -4 L 50 -4 M -50 4 L 50 4",
        "terminals": {"start": [-50, 0], "end": [50, 0]}
      },
      "variants": ["CONDUCTOR_SINGLE"],
      "annotation_fields": ["core_count", "csa_mm2"],
      "usage_notes": "Mineral insulated (MgO) copper sheathed cable (MICC). Used for fire-integrity circuits — fire alarm, emergency lighting, smoke extraction.",
      "related_symbols": ["CONDUCTOR_SINGLE"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "CABLE_DUCT",
      "iec_ref": "IEC60617-03-04-01",
      "iec_part": 3,
      "iec_description": "Cable duct",
      "draftsman_id": "CABLE_DUCT",
      "category": "conductor",
      "display_name": "Cable duct",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -15, 50, 15],
        "path": "M -50 -15 L 50 -15 L 50 15 L -50 15 Z M -50 -5 L 50 -5 M -50 5 L 50 5",
        "terminals": {"left": [-50, 0], "right": [50, 0]}
      },
      "variants": ["TRUNKING", "BUSDUCT"],
      "annotation_fields": ["size", "material"],
      "usage_notes": "A closed cable duct (e.g. underground concrete duct, ceiling void duct). Closed rectangle with internal section lines. Distinct from open-top trunking.",
      "related_symbols": ["TRUNKING", "CABLE_LADDER"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "TRUNKING",
      "iec_ref": "IEC60617-03-04-02",
      "iec_part": 3,
      "iec_description": "Cable trunking",
      "draftsman_id": "TRUNKING",
      "category": "conductor",
      "display_name": "Cable trunking",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -15, 50, 15],
        "path": "M -50 15 L -50 -15 L 50 -15 L 50 15",
        "terminals": {"left": [-50, 0], "right": [50, 0]}
      },
      "variants": ["CABLE_DUCT", "BUSDUCT"],
      "annotation_fields": ["size", "material"],
      "usage_notes": "Open-top cable trunking (with removable lid). Three-sided rectangle. Distinct from closed cable duct.",
      "related_symbols": ["CABLE_DUCT", "CABLE_LADDER"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "CONDUIT",
      "iec_ref": "IEC60617-03-04-03",
      "iec_part": 3,
      "iec_description": "Conduit",
      "draftsman_id": "CONDUIT",
      "category": "conductor",
      "display_name": "Conduit",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -10, 50, 10],
        "path": "M -50 -8 L 50 -8 M -50 8 L 50 8",
        "terminals": {"start": [-50, 0], "end": [50, 0]}
      },
      "variants": ["CONDUCTOR_IN_CONDUIT"],
      "annotation_fields": ["diameter_mm", "material"],
      "usage_notes": "Conduit shown in section as two parallel lines. Use for conduit runs in containment drawings. Annotate diameter and material (steel, PVC, flexible).",
      "related_symbols": ["CONDUCTOR_IN_CONDUIT"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "CABLE_LADDER",
      "iec_ref": "IEC60617-03-04-04",
      "iec_part": 3,
      "iec_description": "Cable ladder",
      "draftsman_id": "CABLE_LADDER",
      "category": "conductor",
      "display_name": "Cable ladder",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -12, 50, 12],
        "path": "M -50 -10 L 50 -10 M -50 10 L 50 10 M -40 -10 L -40 10 M -20 -10 L -20 10 M 0 -10 L 0 10 M 20 -10 L 20 10 M 40 -10 L 40 10",
        "terminals": {"start": [-50, 0], "end": [50, 0]}
      },
      "variants": ["CABLE_DUCT", "TRUNKING"],
      "annotation_fields": ["width_mm", "material"],
      "usage_notes": "Cable ladder — two side rails with cross rungs at regular intervals. Used for heavy cable runs in plant rooms, utility risers.",
      "related_symbols": ["CABLE_DUCT", "TRUNKING"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "BUSDUCT",
      "iec_ref": "IEC60617-03-04-05",
      "iec_part": 3,
      "iec_description": "Busbar trunking (busduct)",
      "draftsman_id": "BUSDUCT",
      "category": "conductor",
      "display_name": "Busbar trunking / busduct",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -12, 50, 12],
        "path": "M -50 -12 L 50 -12 L 50 12 L -50 12 Z M -50 -4 L 50 -4 M -50 4 L 50 4",
        "terminals": {"start": [-50, 0], "end": [50, 0]}
      },
      "variants": ["BUSBAR", "BUSBAR_3PH"],
      "annotation_fields": ["rated_A", "manufacturer", "length_m"],
      "usage_notes": "Prefabricated busbar trunking system. Use for high-current vertical risers and horizontal mains distribution. Annotate rated current and manufacturer/range.",
      "related_symbols": ["BUSBAR", "BUSBAR_3PH"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "JUNCTION_BOX_CONDUCTOR",
      "iec_ref": "IEC60617-03-05-01",
      "iec_part": 3,
      "iec_description": "Junction box in conductor run",
      "draftsman_id": "JUNCTION_BOX_CONDUCTOR",
      "category": "conductor",
      "display_name": "Conductor junction box",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -15, 50, 15],
        "path": "M -50 0 L -15 0 M -15 -15 L 15 -15 L 15 15 L -15 15 Z M 15 0 L 50 0",
        "terminals": {"in": [-50, 0], "out": [50, 0]}
      },
      "variants": ["JUNCTION_BOX"],
      "annotation_fields": ["box_id", "IP_rating"],
      "usage_notes": "Junction box inserted in a conductor run for splicing or branching. Distinct from JUNCTION_BOX (Part 11) which is the architectural-plan symbol.",
      "related_symbols": ["JUNCTION_BOX", "CABLE_SPLICE"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "CABLE_END_SEAL",
      "iec_ref": "IEC60617-03-05-02",
      "iec_part": 3,
      "iec_description": "Cable end seal / termination",
      "draftsman_id": "CABLE_END_SEAL",
      "category": "conductor",
      "display_name": "Cable end seal",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -10, 5, 10],
        "path": "M -50 0 L 0 0 M -20 -10 L 0 0 L -20 10",
        "terminals": {"cable": [-50, 0]}
      },
      "variants": [],
      "annotation_fields": ["seal_type"],
      "usage_notes": "End seal on an MICC or other moisture-sensitive cable. Triangle/arrowhead indicates the sealed termination. Required at every MICC entry into a gland or terminal.",
      "related_symbols": ["CONDUCTOR_MINERAL"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "CONDUCTOR_LAPPED",
      "iec_ref": "IEC60617-03-01-16",
      "iec_part": 3,
      "iec_description": "Lapped / braided conductors",
      "draftsman_id": "CONDUCTOR_LAPPED",
      "category": "conductor",
      "display_name": "Lapped conductors",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -8, 50, 8],
        "path": "M -50 0 L 50 0 M -30 -6 L -15 6 M -15 -6 L 0 6 M 0 -6 L 15 6 M 15 -6 L 30 6",
        "terminals": {"start": [-50, 0], "end": [50, 0]}
      },
      "variants": ["CONDUCTOR_SINGLE"],
      "annotation_fields": ["csa_mm2"],
      "usage_notes": "Lapped or braided conductor — multi-strand braid used for high-current flexible connections, equipotential bonding straps, lightning down-conductors.",
      "related_symbols": ["CONDUCTOR_FLEXIBLE"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "CABLE_SPLICE",
      "iec_ref": "IEC60617-03-05-03",
      "iec_part": 3,
      "iec_description": "Cable splice",
      "draftsman_id": "CABLE_SPLICE",
      "category": "conductor",
      "display_name": "Cable splice joint",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -15, 50, 15],
        "path": "M -50 0 L -15 0 M -15 0 L 0 -15 L 15 0 L 0 15 Z M 15 0 L 50 0",
        "terminals": {"in": [-50, 0], "out": [50, 0]}
      },
      "variants": ["JUNCTION_BOX_CONDUCTOR"],
      "annotation_fields": ["splice_type"],
      "usage_notes": "In-line cable splice — a diamond shape where two conductor lengths are jointed. Used for cable repairs or extension joints on underground/site cabling.",
      "related_symbols": ["JUNCTION_BOX_CONDUCTOR"],
      "generating_shared_symbol": true
    }
  ]
}
```

- [ ] **Step 2: Validate JSON syntax**

Run: `python3 -c "import json; json.load(open('shared/standards/electrical/IEC60617/part3-conductors.json'))" && echo OK`
Expected: `OK`

- [ ] **Step 3: Verify symbol count**

Run: `python3 -c "import json; print(len(json.load(open('shared/standards/electrical/IEC60617/part3-conductors.json'))['symbols']))"`
Expected: `30`

- [ ] **Step 4: Verify all schema fields present**

Run: `python3 -c "import json; data=json.load(open('shared/standards/electrical/IEC60617/part3-conductors.json')); req=['symbol_id','iec_ref','iec_part','iec_description','draftsman_id','category','display_name','geometry','variants','annotation_fields','usage_notes','related_symbols','generating_shared_symbol']; missing=[(s.get('symbol_id','?'), [f for f in req if f not in s]) for s in data['symbols'] if any(f not in s for f in req)]; print('OK' if not missing else 'MISSING:'+str(missing))"`
Expected: `OK`

- [ ] **Step 5: Commit**

```bash
git add shared/standards/electrical/IEC60617/part3-conductors.json
git commit -m "feat: IEC60617 part3-conductors.json — 30 conductor and cable symbols"
```

---

## Task 8: Create part6-power.json (~35 symbols)

**Files:**
- Create: `shared/standards/electrical/IEC60617/part6-power.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "IEC 60617 Part 6 — Production and conversion of electrical energy",
  "_iec_part": 6,
  "_version": "1.0.0",
  "symbols": [
    {
      "symbol_id": "GENERATOR_GENERAL",
      "iec_ref": "IEC60617-06-04-01",
      "iec_part": 6,
      "iec_description": "Generator (general)",
      "draftsman_id": "GENERATOR_GENERAL",
      "category": "power",
      "display_name": "Generator (general)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -30, 50, 30],
        "path": "M -50 0 L -30 0 M 30 0 A 30 30 0 1 0 -30 0 A 30 30 0 1 0 30 0 Z M 30 0 L 50 0",
        "terminals": {"out_pos": [50, 0], "out_neg": [-50, 0]}
      },
      "variants": ["GENERATOR_SYNC", "GENERATOR_INDUCTION"],
      "annotation_fields": ["rating_kVA", "voltage_V", "label"],
      "usage_notes": "Generic generator — circle with internal 'G' (label annotation). Use when type is unspecified or for diesel/gas standby gensets at the schematic level.",
      "related_symbols": ["GENERATOR_SYNC", "GENERATOR_INDUCTION", "MOTOR_GENERAL"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "GENERATOR_SYNC",
      "iec_ref": "IEC60617-06-04-02",
      "iec_part": 6,
      "iec_description": "Synchronous generator",
      "draftsman_id": "GENERATOR_SYNC",
      "category": "power",
      "display_name": "Synchronous generator",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -30, 50, 30],
        "path": "M -50 0 L -30 0 M 30 0 A 30 30 0 1 0 -30 0 A 30 30 0 1 0 30 0 Z M 30 0 L 50 0",
        "terminals": {"out_pos": [50, 0], "out_neg": [-50, 0]}
      },
      "variants": ["GENERATOR_GENERAL", "GENERATOR_INDUCTION"],
      "annotation_fields": ["rating_kVA", "voltage_V", "pf", "label_GS"],
      "usage_notes": "Synchronous generator — circle annotated 'GS'. Standard for diesel gensets, gas turbines, hydro generators. Excitation system separate.",
      "related_symbols": ["GENERATOR_GENERAL", "MOTOR_SYNC"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "GENERATOR_INDUCTION",
      "iec_ref": "IEC60617-06-04-03",
      "iec_part": 6,
      "iec_description": "Induction (asynchronous) generator",
      "draftsman_id": "GENERATOR_INDUCTION",
      "category": "power",
      "display_name": "Induction generator",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -30, 50, 30],
        "path": "M -50 0 L -30 0 M 30 0 A 30 30 0 1 0 -30 0 A 30 30 0 1 0 30 0 Z M 30 0 L 50 0",
        "terminals": {"out_pos": [50, 0], "out_neg": [-50, 0]}
      },
      "variants": ["GENERATOR_GENERAL", "GENERATOR_SYNC"],
      "annotation_fields": ["rating_kVA", "voltage_V", "label_GA"],
      "usage_notes": "Induction generator — circle annotated 'GA' (asynchronous). Common in small wind turbines, some micro-hydro. Requires grid reactive power for excitation.",
      "related_symbols": ["GENERATOR_GENERAL", "MOTOR_INDUCTION", "WIND_TURBINE"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "MOTOR_GENERAL",
      "iec_ref": "IEC60617-06-05-01",
      "iec_part": 6,
      "iec_description": "Motor (general)",
      "draftsman_id": "MOTOR_GENERAL",
      "category": "power",
      "display_name": "Motor (general)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -30, 50, 30],
        "path": "M -50 0 L -30 0 M 30 0 A 30 30 0 1 0 -30 0 A 30 30 0 1 0 30 0 Z M 30 0 L 50 0",
        "terminals": {"in_a": [-50, 0], "in_b": [50, 0]}
      },
      "variants": ["MOTOR_INDUCTION", "MOTOR_SYNC", "MOTOR_DC"],
      "annotation_fields": ["rating_kW", "voltage_V", "rpm", "label_M"],
      "usage_notes": "Generic motor — circle annotated 'M'. Use when type is unspecified at the SLD level. Distinguish synchronous (MS), asynchronous (MA), DC (MC).",
      "related_symbols": ["MOTOR_INDUCTION", "MOTOR_SYNC", "MOTOR_DC", "GENERATOR_GENERAL"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "MOTOR_INDUCTION",
      "iec_ref": "IEC60617-06-05-02",
      "iec_part": 6,
      "iec_description": "Induction (asynchronous) motor",
      "draftsman_id": "MOTOR_INDUCTION",
      "category": "power",
      "display_name": "Induction motor",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -30, 50, 30],
        "path": "M -50 0 L -30 0 M 30 0 A 30 30 0 1 0 -30 0 A 30 30 0 1 0 30 0 Z M 30 0 L 50 0",
        "terminals": {"L1": [-50, 0], "L2": [50, 0]}
      },
      "variants": ["MOTOR_GENERAL", "MOTOR_SYNC", "MOTOR_DC"],
      "annotation_fields": ["rating_kW", "voltage_V", "rpm", "starting_kVA", "label_MA"],
      "usage_notes": "Induction (asynchronous) motor — circle annotated 'MA' or '3~M'. Most common motor type for HVAC fans, pumps, conveyors. Annotate kW, starting kVA for SLD coordination.",
      "related_symbols": ["MOTOR_GENERAL", "MOTOR_STARTER_DOL", "VFD"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "MOTOR_SYNC",
      "iec_ref": "IEC60617-06-05-03",
      "iec_part": 6,
      "iec_description": "Synchronous motor",
      "draftsman_id": "MOTOR_SYNC",
      "category": "power",
      "display_name": "Synchronous motor",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -30, 50, 30],
        "path": "M -50 0 L -30 0 M 30 0 A 30 30 0 1 0 -30 0 A 30 30 0 1 0 30 0 Z M 30 0 L 50 0",
        "terminals": {"L1": [-50, 0], "L2": [50, 0]}
      },
      "variants": ["MOTOR_INDUCTION", "MOTOR_GENERAL"],
      "annotation_fields": ["rating_kW", "voltage_V", "rpm", "label_MS"],
      "usage_notes": "Synchronous motor — circle annotated 'MS'. Used in large compressors, mills. Can provide leading PF.",
      "related_symbols": ["MOTOR_INDUCTION", "GENERATOR_SYNC"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "MOTOR_DC",
      "iec_ref": "IEC60617-06-05-04",
      "iec_part": 6,
      "iec_description": "Direct current motor",
      "draftsman_id": "MOTOR_DC",
      "category": "power",
      "display_name": "DC motor",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -30, 50, 30],
        "path": "M -50 0 L -30 0 M 30 0 A 30 30 0 1 0 -30 0 A 30 30 0 1 0 30 0 Z M 30 0 L 50 0",
        "terminals": {"pos": [-50, 0], "neg": [50, 0]}
      },
      "variants": ["MOTOR_GENERAL", "MOTOR_INDUCTION"],
      "annotation_fields": ["rating_kW", "voltage_V_DC", "rpm", "label_MC"],
      "usage_notes": "DC motor — circle annotated 'MC' (continuous). Used in some lifts, EV drives. Less common in modern installations.",
      "related_symbols": ["MOTOR_GENERAL", "RECTIFIER"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "TRANSFORMER_2W",
      "iec_ref": "IEC60617-06-09-01",
      "iec_part": 6,
      "iec_description": "Two-winding transformer (single-line)",
      "draftsman_id": "TRANSFORMER_2W",
      "category": "power",
      "display_name": "Two-winding transformer",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -20, 50, 20],
        "path": "M -50 0 L -35 0 M 5 0 A 20 20 0 1 0 -35 0 A 20 20 0 1 0 5 0 Z M 35 0 A 20 20 0 1 0 -5 0 A 20 20 0 1 0 35 0 Z M 35 0 L 50 0",
        "terminals": {"primary": [-50, 0], "secondary": [50, 0]}
      },
      "variants": ["TRANSFORMER_3W", "TRANSFORMER_AUTO", "TRANSFORMER_1PH", "TRANSFORMER_3PH"],
      "annotation_fields": ["rating_kVA", "primary_V", "secondary_V", "vector_group", "uk_pct"],
      "usage_notes": "Two-winding transformer — two touching circles. Annotate kVA, primary and secondary voltages, vector group (e.g. Dyn11), uk% for fault calculations.",
      "related_symbols": ["TRANSFORMER_3W", "TRANSFORMER_AUTO", "TRANSFORMER_CURRENT", "TRANSFORMER_VOLTAGE"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "TRANSFORMER_3W",
      "iec_ref": "IEC60617-06-09-02",
      "iec_part": 6,
      "iec_description": "Three-winding transformer (single-line)",
      "draftsman_id": "TRANSFORMER_3W",
      "category": "power",
      "display_name": "Three-winding transformer",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -40, 50, 30],
        "path": "M -40 0 A 15 15 0 1 0 -10 0 A 15 15 0 1 0 -40 0 Z M 10 0 A 15 15 0 1 0 40 0 A 15 15 0 1 0 10 0 Z M -15 -25 A 15 15 0 1 0 15 -25 A 15 15 0 1 0 -15 -25 Z M -50 0 L -40 0 M 40 0 L 50 0 M 0 -40 L 0 -25",
        "terminals": {"primary": [-50, 0], "secondary": [50, 0], "tertiary": [0, -40]}
      },
      "variants": ["TRANSFORMER_2W", "TRANSFORMER_AUTO"],
      "annotation_fields": ["rating_kVA", "primary_V", "secondary_V", "tertiary_V", "vector_group"],
      "usage_notes": "Three-winding transformer — three interconnected circles. Used for HV/MV/LV step-down with a tertiary winding (e.g. for delta stabiliser or auxiliary supply).",
      "related_symbols": ["TRANSFORMER_2W"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "TRANSFORMER_AUTO",
      "iec_ref": "IEC60617-06-09-03",
      "iec_part": 6,
      "iec_description": "Autotransformer (single-line)",
      "draftsman_id": "TRANSFORMER_AUTO",
      "category": "power",
      "display_name": "Autotransformer",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -25, 50, 25],
        "path": "M -50 0 L -25 0 M 25 0 A 25 25 0 1 0 -25 0 A 25 25 0 1 0 25 0 Z M 25 0 L 50 0 M 0 0 L 0 -25 L 30 -25",
        "terminals": {"primary": [-50, 0], "secondary": [50, 0], "tap": [30, -25]}
      },
      "variants": ["TRANSFORMER_2W"],
      "annotation_fields": ["rating_kVA", "primary_V", "secondary_V", "tap_V"],
      "usage_notes": "Autotransformer — single circle with tap. Common for voltage step-up/down where galvanic isolation is not required (e.g. motor starting, distribution voltage matching). Annotate tap voltage.",
      "related_symbols": ["TRANSFORMER_2W"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "TRANSFORMER_CURRENT",
      "iec_ref": "IEC60617-06-09-05",
      "iec_part": 6,
      "iec_description": "Current transformer",
      "draftsman_id": "TRANSFORMER_CURRENT",
      "category": "power",
      "display_name": "Current transformer (CT)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -25, 50, 25],
        "path": "M -50 0 L 50 0 M 0 25 A 25 25 0 1 0 0 -25 M 0 -25 A 8 8 0 1 0 -16 -25 M -16 -25 L -16 25 M 0 25 A 8 8 0 1 0 -16 25",
        "terminals": {"primary_in": [-50, 0], "primary_out": [50, 0], "sec_S1": [-16, -25], "sec_S2": [-16, 25]}
      },
      "variants": ["TRANSFORMER_VOLTAGE", "CT_METERING"],
      "annotation_fields": ["ratio", "burden_VA", "class", "accuracy"],
      "usage_notes": "CT — primary conductor passes through the core, secondary winding feeds metering or protection. Annotate ratio (e.g. 800/5), class (P, PR, PX for protection; 0.2, 0.5 for metering), burden VA.",
      "related_symbols": ["TRANSFORMER_VOLTAGE", "AMMETER", "CT_METERING"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "TRANSFORMER_VOLTAGE",
      "iec_ref": "IEC60617-06-09-06",
      "iec_part": 6,
      "iec_description": "Voltage transformer",
      "draftsman_id": "TRANSFORMER_VOLTAGE",
      "category": "power",
      "display_name": "Voltage transformer (VT)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -30, 50, 30],
        "path": "M -50 0 L -25 0 M 5 0 A 20 20 0 1 0 -25 0 A 20 20 0 1 0 5 0 Z M 25 0 A 20 20 0 1 0 -5 0 A 20 20 0 1 0 25 0 Z M 25 0 L 50 0",
        "terminals": {"hv_a": [-50, 0], "hv_b": [50, 0], "lv_a": [-15, -20], "lv_b": [15, -20]}
      },
      "variants": ["TRANSFORMER_CURRENT", "VT_METERING"],
      "annotation_fields": ["ratio", "burden_VA", "class"],
      "usage_notes": "VT (PT) — steps high voltage down for metering and protection. Annotate ratio (e.g. 11000/110), class, burden. Two circles like a power transformer but smaller.",
      "related_symbols": ["TRANSFORMER_CURRENT", "VOLTMETER", "VT_METERING"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "TRANSFORMER_1PH",
      "iec_ref": "IEC60617-06-09-04",
      "iec_part": 6,
      "iec_description": "Single-phase transformer",
      "draftsman_id": "TRANSFORMER_1PH",
      "category": "power",
      "display_name": "1-phase transformer",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -25, 50, 25],
        "path": "M -50 -10 L -35 -10 M -50 10 L -35 10 M -15 -10 A 20 20 0 1 0 -15 10 A 20 20 0 1 0 -15 -10 Z M 15 -10 A 20 20 0 1 0 15 10 A 20 20 0 1 0 15 -10 Z M 35 -10 L 50 -10 M 35 10 L 50 10",
        "terminals": {"prim_a": [-50, -10], "prim_b": [-50, 10], "sec_a": [50, -10], "sec_b": [50, 10]}
      },
      "variants": ["TRANSFORMER_2W", "TRANSFORMER_3PH"],
      "annotation_fields": ["rating_kVA", "primary_V", "secondary_V"],
      "usage_notes": "Single-phase transformer with explicit two-terminal primary and secondary. Use when phase distinction is important (e.g. control transformers).",
      "related_symbols": ["TRANSFORMER_2W", "TRANSFORMER_3PH"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "TRANSFORMER_3PH",
      "iec_ref": "IEC60617-06-09-07",
      "iec_part": 6,
      "iec_description": "Three-phase transformer (detailed)",
      "draftsman_id": "TRANSFORMER_3PH",
      "category": "power",
      "display_name": "3-phase transformer",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -30, 50, 30],
        "path": "M -50 -15 L -35 -15 M -50 0 L -35 0 M -50 15 L -35 15 M -15 -15 A 20 20 0 1 0 -15 5 A 20 20 0 1 0 -15 -15 Z M 15 -15 A 20 20 0 1 0 15 5 A 20 20 0 1 0 15 -15 Z M 35 -15 L 50 -15 M 35 0 L 50 0 M 35 15 L 50 15",
        "terminals": {"L1_prim": [-50, -15], "L2_prim": [-50, 0], "L3_prim": [-50, 15], "L1_sec": [50, -15], "L2_sec": [50, 0], "L3_sec": [50, 15]}
      },
      "variants": ["TRANSFORMER_2W", "TRANSFORMER_1PH"],
      "annotation_fields": ["rating_kVA", "primary_V", "secondary_V", "vector_group", "uk_pct"],
      "usage_notes": "Three-phase transformer with all phase terminals shown. Use on detailed schematics where phase routing matters; the single-line TRANSFORMER_2W is preferred on SLDs.",
      "related_symbols": ["TRANSFORMER_2W", "TRANSFORMER_1PH"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "BATTERY",
      "iec_ref": "IEC60617-06-15-01",
      "iec_part": 6,
      "iec_description": "Battery (cell or accumulator)",
      "draftsman_id": "BATTERY",
      "category": "power",
      "display_name": "Battery",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -15, 50, 15],
        "path": "M -50 0 L -10 0 M -10 -15 L -10 15 M 0 -8 L 0 8 M 10 -15 L 10 15 M 20 -8 L 20 8 M 20 0 L 50 0",
        "terminals": {"pos": [50, 0], "neg": [-50, 0]}
      },
      "variants": [],
      "annotation_fields": ["capacity_Ah", "voltage_V", "chemistry"],
      "usage_notes": "Battery — long plate (positive) and short plate (negative) alternating. Two cells shown here. Annotate capacity (Ah), nominal voltage, chemistry (lead-acid, Li-ion, NiMH).",
      "related_symbols": ["BATTERY_CHARGER", "UPS", "POLARITY_PLUS", "POLARITY_MINUS"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "BATTERY_CHARGER",
      "iec_ref": "IEC60617-06-15-02",
      "iec_part": 6,
      "iec_description": "Battery charger / rectifier-charger",
      "draftsman_id": "BATTERY_CHARGER",
      "category": "power",
      "display_name": "Battery charger",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -20, 50, 20],
        "path": "M -50 0 L -25 0 M -25 -20 L 25 -20 L 25 20 L -25 20 Z M 25 0 L 50 0 M -15 -10 L 15 10 M -15 10 L -10 10 M 15 -10 L 10 -10",
        "terminals": {"ac_in": [-50, 0], "dc_out": [50, 0]}
      },
      "variants": ["RECTIFIER"],
      "annotation_fields": ["rating_kW", "input_V_AC", "output_V_DC"],
      "usage_notes": "Battery charger — rectangle with diagonal indicating AC→DC. Annotate ratings. Distinct from generic RECTIFIER by inclusion of charge management.",
      "related_symbols": ["BATTERY", "RECTIFIER", "UPS"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "UPS",
      "iec_ref": "IEC60617-06-15-04",
      "iec_part": 6,
      "iec_description": "Uninterruptible power supply",
      "draftsman_id": "UPS",
      "category": "power",
      "display_name": "UPS",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -25, 50, 25],
        "path": "M -50 0 L -30 0 M -30 -25 L 30 -25 L 30 25 L -30 25 Z M 30 0 L 50 0 M -15 -10 L 15 10 M -15 10 L -10 10 M 15 -10 L 10 -10",
        "terminals": {"ac_in": [-50, 0], "ac_out": [50, 0]}
      },
      "variants": ["BATTERY_CHARGER"],
      "annotation_fields": ["rating_kVA", "autonomy_min", "topology"],
      "usage_notes": "UPS — rectangle annotated 'UPS'. Common annotation: kVA rating, autonomy (minutes), topology (online double-conversion, line-interactive). Distinct from BATTERY_CHARGER — UPS includes inverter and bypass.",
      "related_symbols": ["BATTERY", "BATTERY_CHARGER", "INVERTER"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "SOLAR_PV",
      "iec_ref": "IEC60617-06-16-01",
      "iec_part": 6,
      "iec_description": "Photovoltaic cell / module",
      "draftsman_id": "SOLAR_PV",
      "category": "power",
      "display_name": "Photovoltaic source",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -30, 50, 30],
        "path": "M -50 0 L -20 0 M -20 -20 L 20 -20 L 20 20 L -20 20 Z M -20 -20 L 20 20 M 20 0 L 50 0 M -10 -30 L -5 -25 M 0 -30 L 5 -25 M 10 -30 L 15 -25",
        "terminals": {"pos": [50, 0], "neg": [-50, 0]}
      },
      "variants": [],
      "annotation_fields": ["rating_kWp", "voltage_V_DC", "module_count"],
      "usage_notes": "PV source — rectangle with diagonal (indicating a diode/cell-like behaviour) plus arrows indicating incident sunlight. Annotate peak rating (kWp).",
      "related_symbols": ["INVERTER", "BATTERY"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "WIND_TURBINE",
      "iec_ref": "IEC60617-06-16-02",
      "iec_part": 6,
      "iec_description": "Wind-powered generator",
      "draftsman_id": "WIND_TURBINE",
      "category": "power",
      "display_name": "Wind turbine",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -30, 50, 30],
        "path": "M -50 0 L -30 0 M 30 0 A 30 30 0 1 0 -30 0 A 30 30 0 1 0 30 0 Z M 30 0 L 50 0 M 0 -25 L 0 25 M -25 0 L 0 0 L 22 -12",
        "terminals": {"out_a": [-50, 0], "out_b": [50, 0]}
      },
      "variants": ["GENERATOR_INDUCTION"],
      "annotation_fields": ["rating_kW", "voltage_V", "rotor_dia_m"],
      "usage_notes": "Wind turbine — generator circle with three-blade indicator. Annotate rated kW. Internal generator may be induction or synchronous (refer to cross-referenced symbol).",
      "related_symbols": ["GENERATOR_INDUCTION", "GENERATOR_SYNC", "INVERTER"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "CAPACITOR",
      "iec_ref": "IEC60617-06-04-04",
      "iec_part": 6,
      "iec_description": "Capacitor (general)",
      "draftsman_id": "CAPACITOR",
      "category": "power",
      "display_name": "Capacitor",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -15, 50, 15],
        "path": "M -50 0 L -5 0 M -5 -15 L -5 15 M 5 -15 L 5 15 M 5 0 L 50 0",
        "terminals": {"a": [-50, 0], "b": [50, 0]}
      },
      "variants": ["CAPACITOR_BANK"],
      "annotation_fields": ["capacitance_uF", "voltage_V"],
      "usage_notes": "Single capacitor — two parallel plates. Annotate capacitance and rated voltage.",
      "related_symbols": ["CAPACITOR_BANK", "REACTOR_INDUCTOR"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "CAPACITOR_BANK",
      "iec_ref": "IEC60617-06-06-01",
      "iec_part": 6,
      "iec_description": "Capacitor bank (PFC)",
      "draftsman_id": "CAPACITOR_BANK",
      "category": "power",
      "display_name": "Capacitor bank (PFC)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -20, 50, 20],
        "path": "M -50 0 L -25 0 M -25 -20 L 25 -20 L 25 20 L -25 20 Z M -10 -10 L -10 10 M 0 -10 L 0 10 M 10 -10 L 10 10 M -5 -10 L -5 10 M 5 -10 L 5 10 M 25 0 L 50 0",
        "terminals": {"L": [-50, 0], "out": [50, 0]}
      },
      "variants": ["CAPACITOR"],
      "annotation_fields": ["rating_kVAr", "voltage_V", "stages"],
      "usage_notes": "Power factor correction capacitor bank — rectangle with multiple capacitor plate marks. Annotate kVAr rating and number of stages. Distinct from a single CAPACITOR.",
      "related_symbols": ["CAPACITOR", "REACTOR_INDUCTOR"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "REACTOR_INDUCTOR",
      "iec_ref": "IEC60617-06-04-05",
      "iec_part": 6,
      "iec_description": "Inductor / reactor",
      "draftsman_id": "REACTOR_INDUCTOR",
      "category": "power",
      "display_name": "Reactor / inductor",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -15, 50, 15],
        "path": "M -50 0 L -25 0 M -25 0 A 7 7 0 1 0 -11 0 M -11 0 A 7 7 0 1 0 3 0 M 3 0 A 7 7 0 1 0 17 0 M 17 0 A 7 7 0 1 0 25 0 M 25 0 L 50 0",
        "terminals": {"a": [-50, 0], "b": [50, 0]}
      },
      "variants": [],
      "annotation_fields": ["inductance_mH", "current_A"],
      "usage_notes": "Reactor / inductor — series of half-circles representing the coil. Used for harmonic filters, motor starting reactors, transformer neutral grounding.",
      "related_symbols": ["CAPACITOR", "FILTER_GENERAL"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "RECTIFIER",
      "iec_ref": "IEC60617-06-12-01",
      "iec_part": 6,
      "iec_description": "Rectifier (general)",
      "draftsman_id": "RECTIFIER",
      "category": "power",
      "display_name": "Rectifier (AC→DC)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -20, 50, 20],
        "path": "M -50 0 L -20 0 M -20 -20 L 20 -20 L 20 20 L -20 20 Z M -15 0 L 15 0 M -15 -10 L -10 0 L -15 10 M 15 -10 L 10 0 L 15 10 M 20 0 L 50 0",
        "terminals": {"ac_in": [-50, 0], "dc_out": [50, 0]}
      },
      "variants": ["CONVERTER_AC_DC", "BATTERY_CHARGER"],
      "annotation_fields": ["rating_kW", "input_V_AC", "output_V_DC"],
      "usage_notes": "Rectifier — rectangle with internal AC/DC indication. Generic AC to DC conversion device. Use CONVERTER_AC_DC for a more specific labelling.",
      "related_symbols": ["INVERTER", "CONVERTER_AC_DC", "BATTERY_CHARGER"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "INVERTER",
      "iec_ref": "IEC60617-06-12-02",
      "iec_part": 6,
      "iec_description": "Inverter (general)",
      "draftsman_id": "INVERTER",
      "category": "power",
      "display_name": "Inverter (DC→AC)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -20, 50, 20],
        "path": "M -50 0 L -20 0 M -20 -20 L 20 -20 L 20 20 L -20 20 Z M -15 -10 L -10 -10 M -15 10 L -10 10 M 10 -10 L 15 -10 L 15 10 L 10 10 M -10 0 Q 0 -8 5 0 Q 10 8 15 0 M 20 0 L 50 0",
        "terminals": {"dc_in": [-50, 0], "ac_out": [50, 0]}
      },
      "variants": ["CONVERTER_DC_AC"],
      "annotation_fields": ["rating_kW", "input_V_DC", "output_V_AC", "phase_count"],
      "usage_notes": "Inverter — DC to AC conversion. Rectangle with DC and AC indicators. Used in PV systems, UPS, VFD output stages.",
      "related_symbols": ["RECTIFIER", "SOLAR_PV", "UPS", "VFD"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "CONVERTER_DC_DC",
      "iec_ref": "IEC60617-06-12-03",
      "iec_part": 6,
      "iec_description": "DC/DC converter",
      "draftsman_id": "CONVERTER_DC_DC",
      "category": "power",
      "display_name": "DC/DC converter",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -20, 50, 20],
        "path": "M -50 0 L -20 0 M -20 -20 L 20 -20 L 20 20 L -20 20 Z M -15 -5 L -10 -5 L -10 5 L -15 5 M 10 -5 L 15 -5 L 15 5 L 10 5 M 20 0 L 50 0",
        "terminals": {"in": [-50, 0], "out": [50, 0]}
      },
      "variants": [],
      "annotation_fields": ["input_V_DC", "output_V_DC", "rating_W"],
      "usage_notes": "DC to DC converter (e.g. PV string optimisers, telecom power). Rectangle with DC marks both sides.",
      "related_symbols": ["CONVERTER_AC_DC", "CONVERTER_DC_AC"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "CONVERTER_AC_DC",
      "iec_ref": "IEC60617-06-12-04",
      "iec_part": 6,
      "iec_description": "AC/DC converter",
      "draftsman_id": "CONVERTER_AC_DC",
      "category": "power",
      "display_name": "AC/DC converter",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -20, 50, 20],
        "path": "M -50 0 L -20 0 M -20 -20 L 20 -20 L 20 20 L -20 20 Z M -15 -5 Q -10 -10 -5 -5 Q 0 0 -5 5 M 10 -5 L 15 -5 L 15 5 L 10 5 M 20 0 L 50 0",
        "terminals": {"ac_in": [-50, 0], "dc_out": [50, 0]}
      },
      "variants": ["RECTIFIER"],
      "annotation_fields": ["input_V_AC", "output_V_DC", "rating_W"],
      "usage_notes": "AC to DC converter — same function as RECTIFIER but the converter label form preferred in modern installations.",
      "related_symbols": ["RECTIFIER", "CONVERTER_DC_AC"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "CONVERTER_DC_AC",
      "iec_ref": "IEC60617-06-12-05",
      "iec_part": 6,
      "iec_description": "DC/AC converter (inverter)",
      "draftsman_id": "CONVERTER_DC_AC",
      "category": "power",
      "display_name": "DC/AC converter",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -20, 50, 20],
        "path": "M -50 0 L -20 0 M -20 -20 L 20 -20 L 20 20 L -20 20 Z M -15 -5 L -10 -5 L -10 5 L -15 5 M 5 0 Q 10 -8 15 0 M 20 0 L 50 0",
        "terminals": {"dc_in": [-50, 0], "ac_out": [50, 0]}
      },
      "variants": ["INVERTER"],
      "annotation_fields": ["input_V_DC", "output_V_AC", "rating_W"],
      "usage_notes": "DC to AC converter — same function as INVERTER but the converter label form. Use as preferred in PV/battery storage SLDs.",
      "related_symbols": ["INVERTER", "CONVERTER_AC_DC"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "RESISTOR",
      "iec_ref": "IEC60617-06-04-06",
      "iec_part": 6,
      "iec_description": "Resistor (general)",
      "draftsman_id": "RESISTOR",
      "category": "power",
      "display_name": "Resistor",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -10, 50, 10],
        "path": "M -50 0 L -20 0 M -20 -10 L 20 -10 L 20 10 L -20 10 Z M 20 0 L 50 0",
        "terminals": {"a": [-50, 0], "b": [50, 0]}
      },
      "variants": [],
      "annotation_fields": ["resistance_ohm", "power_W"],
      "usage_notes": "IEC resistor symbol — rectangle. Used for neutral earthing resistors (NER), dummy loads, snubber resistors. Annotate Ω and power rating.",
      "related_symbols": ["REACTOR_INDUCTOR", "CAPACITOR"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "EARTH_ELECTRODE",
      "iec_ref": "IEC60617-06-15-06",
      "iec_part": 6,
      "iec_description": "Earth electrode",
      "draftsman_id": "EARTH_ELECTRODE",
      "category": "power",
      "display_name": "Earth electrode",
      "geometry": {
        "grid": 100,
        "bbox": [-25, -50, 25, 25],
        "path": "M 0 -50 L 0 0 M -20 0 L 20 0 L 0 25 Z M -15 -10 L 0 -25 L 15 -10",
        "terminals": {"line": [0, -50]}
      },
      "variants": ["EARTH_GENERAL", "EARTH_PROTECTIVE"],
      "annotation_fields": ["electrode_type", "Ra_ohm"],
      "usage_notes": "Earth electrode (rod, plate, mesh) — triangle with downward arrow representing the buried electrode. Annotate measured/designed resistance Ra. Distinct from EARTH_GENERAL which is the symbolic earth terminal.",
      "related_symbols": ["EARTH_GENERAL", "EARTH_PROTECTIVE"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "FUEL_CELL",
      "iec_ref": "IEC60617-06-16-03",
      "iec_part": 6,
      "iec_description": "Fuel cell",
      "draftsman_id": "FUEL_CELL",
      "category": "power",
      "display_name": "Fuel cell",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -20, 50, 20],
        "path": "M -50 0 L -25 0 M -25 -20 L 25 -20 L 25 20 L -25 20 Z M 25 0 L 50 0 M -10 -10 L 10 -10 M -10 0 L 10 0 M -10 10 L 10 10",
        "terminals": {"pos": [50, 0], "neg": [-50, 0]}
      },
      "variants": ["BATTERY", "SOLAR_PV"],
      "annotation_fields": ["rating_kW", "voltage_V_DC", "fuel"],
      "usage_notes": "Fuel cell — rectangle with stack-cell indication. Annotate rated power, output voltage, fuel type (hydrogen, methanol).",
      "related_symbols": ["BATTERY", "INVERTER"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "STABILIZER",
      "iec_ref": "IEC60617-06-12-06",
      "iec_part": 6,
      "iec_description": "Voltage stabiliser",
      "draftsman_id": "STABILIZER",
      "category": "power",
      "display_name": "Voltage stabiliser",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -20, 50, 20],
        "path": "M -50 0 L -25 0 M -25 -20 L 25 -20 L 25 20 L -25 20 Z M 25 0 L 50 0 M -10 -10 L -10 0 L 10 0 L 10 10",
        "terminals": {"in": [-50, 0], "out": [50, 0]}
      },
      "variants": [],
      "annotation_fields": ["rating_kVA", "input_V_range", "output_V"],
      "usage_notes": "Voltage stabiliser / AVR — rectangle with internal step pattern indicating voltage regulation. Used where supply voltage fluctuates outside equipment tolerance.",
      "related_symbols": ["TRANSFORMER_AUTO", "UPS"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "FREQUENCY_CONVERTER",
      "iec_ref": "IEC60617-06-12-07",
      "iec_part": 6,
      "iec_description": "Frequency converter (static)",
      "draftsman_id": "FREQUENCY_CONVERTER",
      "category": "power",
      "display_name": "Frequency converter",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -20, 50, 20],
        "path": "M -50 0 L -25 0 M -25 -20 L 25 -20 L 25 20 L -25 20 Z M 25 0 L 50 0 M -15 0 L -10 0 L -10 -8 L -5 -8 M -5 0 Q 0 -8 5 0 M 5 0 L 10 0 L 10 -8 L 15 -8",
        "terminals": {"in": [-50, 0], "out": [50, 0]}
      },
      "variants": ["VFD"],
      "annotation_fields": ["input_Hz", "output_Hz", "rating_kVA"],
      "usage_notes": "Frequency converter — between two AC systems of different frequencies (e.g. 50Hz to 60Hz for marine shore power, 50Hz to 400Hz for aerospace test). Annotate both frequencies.",
      "related_symbols": ["VFD", "INVERTER"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "SOFT_STARTER",
      "iec_ref": "IEC60617-06-12-09",
      "iec_part": 6,
      "iec_description": "Soft starter (motor)",
      "draftsman_id": "SOFT_STARTER",
      "category": "power",
      "display_name": "Soft starter",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -20, 50, 20],
        "path": "M -50 0 L -25 0 M -25 -20 L 25 -20 L 25 20 L -25 20 Z M 25 0 L 50 0 M -15 10 L -5 -10 L 15 -10",
        "terminals": {"L_in": [-50, 0], "M_out": [50, 0]}
      },
      "variants": ["VFD", "MOTOR_STARTER_DOL"],
      "annotation_fields": ["rating_kW", "ramp_time_s"],
      "usage_notes": "Soft starter — controls motor inrush current by ramping voltage. Annotate motor rating and ramp time. Cheaper than VFD but no speed control.",
      "related_symbols": ["VFD", "MOTOR_STARTER_DOL", "MOTOR_INDUCTION"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "VFD",
      "iec_ref": "IEC60617-06-12-08",
      "iec_part": 6,
      "iec_description": "Variable frequency drive",
      "draftsman_id": "VFD",
      "category": "power",
      "display_name": "Variable frequency drive (VFD)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -20, 50, 20],
        "path": "M -50 0 L -25 0 M -25 -20 L 25 -20 L 25 20 L -25 20 Z M 25 0 L 50 0 M -15 -10 L -10 -10 L -10 0 L -5 0 M 0 0 Q 5 -8 10 0 M 10 -5 L 15 -10",
        "terminals": {"L_in": [-50, 0], "M_out": [50, 0]}
      },
      "variants": ["FREQUENCY_CONVERTER", "SOFT_STARTER"],
      "annotation_fields": ["rating_kW", "output_Hz_range"],
      "usage_notes": "VFD / variable speed drive — controls motor speed by varying frequency. Standard for HVAC fans, pumps, energy efficiency retrofits. Annotate motor rating and speed range.",
      "related_symbols": ["MOTOR_INDUCTION", "INVERTER", "MOTOR_STARTER_VFD", "SOFT_STARTER"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "TRANSFORMER_PEC",
      "iec_ref": "IEC60617-06-09-08",
      "iec_part": 6,
      "iec_description": "Transformer with primary earth clamp / point",
      "draftsman_id": "TRANSFORMER_PEC",
      "category": "power",
      "display_name": "Transformer with earth point",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -25, 50, 30],
        "path": "M -50 0 L -35 0 M 5 0 A 20 20 0 1 0 -35 0 A 20 20 0 1 0 5 0 Z M 35 0 A 20 20 0 1 0 -5 0 A 20 20 0 1 0 35 0 Z M 35 0 L 50 0 M 0 0 L 0 25 M -10 25 L 10 25 M -5 30 L 5 30",
        "terminals": {"primary": [-50, 0], "secondary": [50, 0], "earth": [0, 30]}
      },
      "variants": ["TRANSFORMER_2W"],
      "annotation_fields": ["rating_kVA", "primary_V", "secondary_V", "earth_method"],
      "usage_notes": "Two-winding transformer with explicit earth point (typically star-point earth on the secondary). Annotate the earthing method (solid, resistor, reactor).",
      "related_symbols": ["TRANSFORMER_2W", "EARTH_GENERAL"],
      "generating_shared_symbol": true
    }
  ]
}
```

- [ ] **Step 2: Validate JSON syntax**

Run: `python3 -c "import json; json.load(open('shared/standards/electrical/IEC60617/part6-power.json'))" && echo OK`
Expected: `OK`

- [ ] **Step 3: Verify symbol count**

Run: `python3 -c "import json; print(len(json.load(open('shared/standards/electrical/IEC60617/part6-power.json'))['symbols']))"`
Expected: `35`

- [ ] **Step 4: Verify all schema fields present**

Run: `python3 -c "import json; data=json.load(open('shared/standards/electrical/IEC60617/part6-power.json')); req=['symbol_id','iec_ref','iec_part','iec_description','draftsman_id','category','display_name','geometry','variants','annotation_fields','usage_notes','related_symbols','generating_shared_symbol']; missing=[(s.get('symbol_id','?'), [f for f in req if f not in s]) for s in data['symbols'] if any(f not in s for f in req)]; print('OK' if not missing else 'MISSING:'+str(missing))"`
Expected: `OK`

- [ ] **Step 5: Commit**

```bash
git add shared/standards/electrical/IEC60617/part6-power.json
git commit -m "feat: IEC60617 part6-power.json — 35 generation and conversion symbols"
```

---

## Task 9: Create part7-switchgear.json (~70 symbols — largest file)

**Files:**
- Create: `shared/standards/electrical/IEC60617/part7-switchgear.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "IEC 60617 Part 7 — Switchgear, controlgear and protective devices",
  "_iec_part": 7,
  "_version": "1.0.0",
  "symbols": [
    {
      "symbol_id": "CONTACT_NO",
      "iec_ref": "IEC60617-07-01-01",
      "iec_part": 7,
      "iec_description": "Make contact (normally open)",
      "draftsman_id": "CONTACT_NO",
      "category": "switching",
      "display_name": "Make contact (NO)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -20, 50, 20],
        "path": "M -50 0 L -15 0 M -15 0 L 12 -18 M 15 -20 L 15 20 M 15 0 L 50 0",
        "terminals": {"in": [-50, 0], "out": [50, 0]}
      },
      "variants": ["CONTACT_NC", "CONTACT_CHANGEOVER"],
      "annotation_fields": ["tag"],
      "usage_notes": "Make contact — normally open. Closes when operated. The moving contact (diagonal blade) and fixed contact (vertical bar) are shown in the open position.",
      "related_symbols": ["CONTACT_NC", "CONTACT_CHANGEOVER", "CONTACT_AUX_NO"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "CONTACT_NC",
      "iec_ref": "IEC60617-07-01-02",
      "iec_part": 7,
      "iec_description": "Break contact (normally closed)",
      "draftsman_id": "CONTACT_NC",
      "category": "switching",
      "display_name": "Break contact (NC)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -20, 50, 20],
        "path": "M -50 0 L -15 0 M -15 -20 L -15 20 M -15 0 L 15 0 M 15 -20 L 15 20 M 15 0 L 50 0 M -20 -15 L 20 15",
        "terminals": {"in": [-50, 0], "out": [50, 0]}
      },
      "variants": ["CONTACT_NO", "CONTACT_CHANGEOVER"],
      "annotation_fields": ["tag"],
      "usage_notes": "Break contact — normally closed. Opens when operated. Shown in the closed position with a diagonal stroke indicating NC behaviour.",
      "related_symbols": ["CONTACT_NO", "CONTACT_CHANGEOVER", "CONTACT_AUX_NC"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "CONTACT_CHANGEOVER",
      "iec_ref": "IEC60617-07-01-03",
      "iec_part": 7,
      "iec_description": "Changeover contact (SPDT)",
      "draftsman_id": "CONTACT_CHANGEOVER",
      "category": "switching",
      "display_name": "Changeover contact (CO)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -25, 50, 25],
        "path": "M -50 0 L -15 0 M -15 0 L 12 -22 M 15 -25 L 15 -15 M 15 15 L 15 25 M 15 -20 L 50 -20 M 15 20 L 50 20",
        "terminals": {"common": [-50, 0], "no": [50, -20], "nc": [50, 20]}
      },
      "variants": ["CONTACT_NO", "CONTACT_NC"],
      "annotation_fields": ["tag"],
      "usage_notes": "Single-pole double-throw contact. Common terminal switches between NO and NC. Used in selector circuits, indication, control logic.",
      "related_symbols": ["CONTACT_NO", "CONTACT_NC"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "SWITCH_GENERAL",
      "iec_ref": "IEC60617-07-02-01",
      "iec_part": 7,
      "iec_description": "Switch (general)",
      "draftsman_id": "SWITCH_GENERAL",
      "category": "switching",
      "display_name": "Switch (general)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -20, 50, 20],
        "path": "M -50 0 L -15 0 M -15 0 L 12 -18 M 15 0 L 50 0",
        "terminals": {"in": [-50, 0], "out": [50, 0]}
      },
      "variants": ["SWITCH_DISCONNECTOR_2P", "ISOLATOR_2P", "SWITCH_1P"],
      "annotation_fields": ["rated_A", "tag"],
      "usage_notes": "Generic switch — single-pole single-throw. Use when device specifics are not yet determined. For an isolating switch, prefer SWITCH_ISOLATING.",
      "related_symbols": ["SWITCH_DISCONNECTOR_2P", "ISOLATOR_2P", "SWITCH_ISOLATING"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "SWITCH_1P",
      "iec_ref": "IEC60617-07-02-02",
      "iec_part": 7,
      "iec_description": "Single-pole switch",
      "draftsman_id": "SWITCH_1P",
      "category": "switching",
      "display_name": "Single-pole switch",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -20, 50, 20],
        "path": "M -50 0 L -15 0 M -15 0 L 12 -18 M 15 0 L 50 0",
        "terminals": {"in": [-50, 0], "out": [50, 0]}
      },
      "variants": ["SWITCH_GENERAL"],
      "annotation_fields": ["rated_A", "tag"],
      "usage_notes": "Single-pole switch — most basic mechanical switch.",
      "related_symbols": ["SWITCH_GENERAL", "SWITCH_DISCONNECTOR_2P"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "SWITCH_DISCONNECTOR_2P",
      "iec_ref": "IEC60617-07-13-01",
      "iec_part": 7,
      "iec_description": "Switch-disconnector, 2-pole",
      "draftsman_id": "SWITCH_DISCONNECTOR_2P",
      "category": "switching",
      "display_name": "2-pole switch-disconnector",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -25, 50, 25],
        "path": "M -50 -10 L -15 -10 M -15 -10 L 12 -28 M 15 -10 L 50 -10 M -50 10 L -15 10 M -15 10 L 12 -8 M 15 10 L 50 10 M -15 -25 L -15 25",
        "terminals": {"L1_in": [-50, -10], "L2_in": [-50, 10], "L1_out": [50, -10], "L2_out": [50, 10]}
      },
      "variants": ["SWITCH_DISCONNECTOR_3P", "SWITCH_DISCONNECTOR_4P", "ISOLATOR_2P"],
      "annotation_fields": ["rated_A", "Icw_kA", "tag"],
      "usage_notes": "2-pole switch-disconnector (load break and isolation). Used as main isolator on single-phase distribution boards. Distinct from ISOLATOR_2P — switch-disconnector can break load current, plain isolator cannot.",
      "related_symbols": ["SWITCH_DISCONNECTOR_3P", "ISOLATOR_2P", "DISCONNECTOR_GENERAL"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "SWITCH_DISCONNECTOR_3P",
      "iec_ref": "IEC60617-07-13-02",
      "iec_part": 7,
      "iec_description": "Switch-disconnector, 3-pole",
      "draftsman_id": "SWITCH_DISCONNECTOR_3P",
      "category": "switching",
      "display_name": "3-pole switch-disconnector",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -30, 50, 30],
        "path": "M -50 -15 L -15 -15 M -15 -15 L 12 -33 M 15 -15 L 50 -15 M -50 0 L -15 0 M -15 0 L 12 -18 M 15 0 L 50 0 M -50 15 L -15 15 M -15 15 L 12 -3 M 15 15 L 50 15 M -15 -30 L -15 30",
        "terminals": {"L1_in": [-50, -15], "L2_in": [-50, 0], "L3_in": [-50, 15], "L1_out": [50, -15], "L2_out": [50, 0], "L3_out": [50, 15]}
      },
      "variants": ["SWITCH_DISCONNECTOR_2P", "SWITCH_DISCONNECTOR_4P"],
      "annotation_fields": ["rated_A", "Icw_kA", "tag"],
      "usage_notes": "3-pole switch-disconnector. Used as the main isolator on 3-phase distribution boards. Mechanically linked operation.",
      "related_symbols": ["SWITCH_DISCONNECTOR_4P", "ISOLATOR_3P"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "SWITCH_DISCONNECTOR_4P",
      "iec_ref": "IEC60617-07-13-03",
      "iec_part": 7,
      "iec_description": "Switch-disconnector, 4-pole",
      "draftsman_id": "SWITCH_DISCONNECTOR_4P",
      "category": "switching",
      "display_name": "4-pole switch-disconnector",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -30, 50, 30],
        "path": "M -50 -20 L -15 -20 M -15 -20 L 12 -38 M 15 -20 L 50 -20 M -50 -7 L -15 -7 M -15 -7 L 12 -25 M 15 -7 L 50 -7 M -50 7 L -15 7 M -15 7 L 12 -11 M 15 7 L 50 7 M -50 20 L -15 20 M -15 20 L 12 2 M 15 20 L 50 20 M -15 -30 L -15 30",
        "terminals": {"L1_in": [-50, -20], "L2_in": [-50, -7], "L3_in": [-50, 7], "N_in": [-50, 20], "L1_out": [50, -20], "L2_out": [50, -7], "L3_out": [50, 7], "N_out": [50, 20]}
      },
      "variants": ["SWITCH_DISCONNECTOR_3P"],
      "annotation_fields": ["rated_A", "Icw_kA", "tag"],
      "usage_notes": "4-pole switch-disconnector — switches L1, L2, L3 and N. Used where switched neutral is required (IT systems, generator/utility transfer).",
      "related_symbols": ["SWITCH_DISCONNECTOR_3P", "ISOLATOR_4P"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "BUS_SECTION_SWITCH",
      "iec_ref": "IEC60617-07-13-08",
      "iec_part": 7,
      "iec_description": "Bus section switch",
      "draftsman_id": "BUS_SECTION_SWITCH",
      "category": "switching",
      "display_name": "Bus section switch",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -25, 50, 25],
        "path": "M -50 -15 L -15 -15 M -15 -15 L 12 -33 M 15 -15 L 50 -15 M -50 0 L -15 0 M -15 0 L 12 -18 M 15 0 L 50 0 M -50 15 L -15 15 M -15 15 L 12 -3 M 15 15 L 50 15",
        "terminals": {"L1_a": [-50, -15], "L2_a": [-50, 0], "L3_a": [-50, 15], "L1_b": [50, -15], "L2_b": [50, 0], "L3_b": [50, 15]}
      },
      "variants": ["SWITCH_DISCONNECTOR_3P"],
      "annotation_fields": ["rated_A", "Icw_kA", "tag"],
      "usage_notes": "Bus section switch — connects two halves of a split busbar. Used in main switchboards with dual incomers for source-changeover / N+1 topology.",
      "related_symbols": ["SWITCH_DISCONNECTOR_3P", "ATS_2WAY"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "ISOLATOR_2P",
      "iec_ref": "IEC60617-07-14-01",
      "iec_part": 7,
      "iec_description": "Isolator (disconnector), 2-pole",
      "draftsman_id": "ISOLATOR_2P",
      "category": "switching",
      "display_name": "2-pole isolator",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -25, 50, 25],
        "path": "M -50 -10 L -15 -10 M -15 -10 L 12 -28 M 15 -10 L 50 -10 M -50 10 L -15 10 M -15 10 L 12 -8 M 15 10 L 50 10 M -15 -25 L -15 25 M -25 -22 L -5 -22",
        "terminals": {"L1_in": [-50, -10], "N_in": [-50, 10], "L1_out": [50, -10], "N_out": [50, 10]}
      },
      "variants": ["ISOLATOR_3P", "ISOLATOR_4P", "SWITCH_DISCONNECTOR_2P"],
      "annotation_fields": ["rated_A", "tag"],
      "usage_notes": "2-pole isolator (no load break). For visible isolation only — must be operated off-load. Horizontal bar across the top indicates isolator (no quick-break mechanism).",
      "related_symbols": ["SWITCH_DISCONNECTOR_2P", "DISCONNECTOR_GENERAL"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "ISOLATOR_3P",
      "iec_ref": "IEC60617-07-14-02",
      "iec_part": 7,
      "iec_description": "Isolator (disconnector), 3-pole",
      "draftsman_id": "ISOLATOR_3P",
      "category": "switching",
      "display_name": "3-pole isolator",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -30, 50, 30],
        "path": "M -50 -15 L -15 -15 M -15 -15 L 12 -33 M 15 -15 L 50 -15 M -50 0 L -15 0 M -15 0 L 12 -18 M 15 0 L 50 0 M -50 15 L -15 15 M -15 15 L 12 -3 M 15 15 L 50 15 M -15 -30 L -15 30 M -25 -27 L -5 -27",
        "terminals": {"L1_in": [-50, -15], "L2_in": [-50, 0], "L3_in": [-50, 15], "L1_out": [50, -15], "L2_out": [50, 0], "L3_out": [50, 15]}
      },
      "variants": ["ISOLATOR_2P", "ISOLATOR_4P"],
      "annotation_fields": ["rated_A", "tag"],
      "usage_notes": "3-pole isolator for 3-phase circuits. Off-load only.",
      "related_symbols": ["ISOLATOR_4P", "SWITCH_DISCONNECTOR_3P"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "ISOLATOR_4P",
      "iec_ref": "IEC60617-07-14-03",
      "iec_part": 7,
      "iec_description": "Isolator (disconnector), 4-pole",
      "draftsman_id": "ISOLATOR_4P",
      "category": "switching",
      "display_name": "4-pole isolator",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -30, 50, 30],
        "path": "M -50 -20 L -15 -20 M -15 -20 L 12 -38 M 15 -20 L 50 -20 M -50 -7 L -15 -7 M -15 -7 L 12 -25 M 15 -7 L 50 -7 M -50 7 L -15 7 M -15 7 L 12 -11 M 15 7 L 50 7 M -50 20 L -15 20 M -15 20 L 12 2 M 15 20 L 50 20 M -15 -30 L -15 30 M -25 -27 L -5 -27",
        "terminals": {"L1_in": [-50, -20], "L2_in": [-50, -7], "L3_in": [-50, 7], "N_in": [-50, 20], "L1_out": [50, -20], "L2_out": [50, -7], "L3_out": [50, 7], "N_out": [50, 20]}
      },
      "variants": ["ISOLATOR_3P"],
      "annotation_fields": ["rated_A", "tag"],
      "usage_notes": "4-pole isolator. Off-load only.",
      "related_symbols": ["ISOLATOR_3P", "SWITCH_DISCONNECTOR_4P"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "MCB_1P",
      "iec_ref": "IEC60617-07-18-01",
      "iec_part": 7,
      "iec_description": "Circuit-breaker, general symbol — 1-pole",
      "draftsman_id": "MCB_1P",
      "category": "protection",
      "display_name": "1-Pole MCB",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -25, 50, 25],
        "path": "M -50 0 L -20 0 M -20 -25 L 20 -25 L 20 25 L -20 25 Z M -20 0 L 20 0 M 20 0 L 50 0",
        "terminals": {"in": [-50, 0], "out": [50, 0]}
      },
      "variants": ["MCB_2P", "MCB_3P", "MCB_4P"],
      "annotation_fields": ["In_A", "curve", "Icu_kA"],
      "usage_notes": "1-pole miniature circuit breaker for final circuits. Annotate rated current (In), trip curve (B/C/D), and breaking capacity (Icu). Standard final-circuit protective device.",
      "related_symbols": ["RCBO_1P", "MCCB_3P", "FUSE_1P", "MCB_2P"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "MCB_2P",
      "iec_ref": "IEC60617-07-18-02",
      "iec_part": 7,
      "iec_description": "Circuit-breaker — 2-pole",
      "draftsman_id": "MCB_2P",
      "category": "protection",
      "display_name": "2-Pole MCB",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -30, 50, 30],
        "path": "M -50 -10 L -20 -10 M -20 -30 L 20 -30 L 20 30 L -20 30 Z M -20 -10 L 20 -10 M 20 -10 L 50 -10 M -50 10 L -20 10 M -20 10 L 20 10 M 20 10 L 50 10",
        "terminals": {"L_in": [-50, -10], "N_in": [-50, 10], "L_out": [50, -10], "N_out": [50, 10]}
      },
      "variants": ["MCB_1P", "MCB_3P", "MCB_4P"],
      "annotation_fields": ["In_A", "curve", "Icu_kA"],
      "usage_notes": "2-pole MCB — breaks both line and neutral simultaneously. Required for IT systems, some EV charge points. Mechanically linked operation.",
      "related_symbols": ["MCB_1P", "MCB_3P"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "MCB_3P",
      "iec_ref": "IEC60617-07-18-03",
      "iec_part": 7,
      "iec_description": "Circuit-breaker — 3-pole",
      "draftsman_id": "MCB_3P",
      "category": "protection",
      "display_name": "3-Pole MCB",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -30, 50, 30],
        "path": "M -50 -15 L -20 -15 M -20 -30 L 20 -30 L 20 30 L -20 30 Z M -20 -15 L 20 -15 M 20 -15 L 50 -15 M -50 0 L -20 0 M -20 0 L 20 0 M 20 0 L 50 0 M -50 15 L -20 15 M -20 15 L 20 15 M 20 15 L 50 15",
        "terminals": {"L1_in": [-50, -15], "L2_in": [-50, 0], "L3_in": [-50, 15], "L1_out": [50, -15], "L2_out": [50, 0], "L3_out": [50, 15]}
      },
      "variants": ["MCB_1P", "MCB_2P", "MCB_4P"],
      "annotation_fields": ["In_A", "curve", "Icu_kA"],
      "usage_notes": "3-pole MCB for 3-phase final circuits. Mechanically linked operation.",
      "related_symbols": ["MCB_4P", "MCCB_3P"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "MCB_4P",
      "iec_ref": "IEC60617-07-18-04",
      "iec_part": 7,
      "iec_description": "Circuit-breaker — 4-pole",
      "draftsman_id": "MCB_4P",
      "category": "protection",
      "display_name": "4-Pole MCB",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -30, 50, 30],
        "path": "M -50 -20 L -20 -20 M -20 -30 L 20 -30 L 20 30 L -20 30 Z M -20 -20 L 20 -20 M 20 -20 L 50 -20 M -50 -7 L -20 -7 M -20 -7 L 20 -7 M 20 -7 L 50 -7 M -50 7 L -20 7 M -20 7 L 20 7 M 20 7 L 50 7 M -50 20 L -20 20 M -20 20 L 20 20 M 20 20 L 50 20",
        "terminals": {"L1_in": [-50, -20], "L2_in": [-50, -7], "L3_in": [-50, 7], "N_in": [-50, 20], "L1_out": [50, -20], "L2_out": [50, -7], "L3_out": [50, 7], "N_out": [50, 20]}
      },
      "variants": ["MCB_3P"],
      "annotation_fields": ["In_A", "curve", "Icu_kA"],
      "usage_notes": "4-pole MCB — breaks L1, L2, L3 and N. Used where switched neutral is required (IT systems, source changeover circuits).",
      "related_symbols": ["MCB_3P", "MCCB_4P"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "MCCB_3P",
      "iec_ref": "IEC60617-07-18-11",
      "iec_part": 7,
      "iec_description": "Moulded case circuit breaker — 3-pole",
      "draftsman_id": "MCCB_3P",
      "category": "protection",
      "display_name": "3-Pole MCCB",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -30, 50, 30],
        "path": "M -50 -15 L -25 -15 M -25 -30 L 25 -30 L 25 30 L -25 30 Z M -25 -15 L 25 -15 M 25 -15 L 50 -15 M -50 0 L -25 0 M -25 0 L 25 0 M 25 0 L 50 0 M -50 15 L -25 15 M -25 15 L 25 15 M 25 15 L 50 15 M -15 -10 L 15 -10",
        "terminals": {"L1_in": [-50, -15], "L2_in": [-50, 0], "L3_in": [-50, 15], "L1_out": [50, -15], "L2_out": [50, 0], "L3_out": [50, 15]}
      },
      "variants": ["MCCB_4P", "MCB_3P", "ACB_3P"],
      "annotation_fields": ["In_A", "Ir_setting", "Im_setting", "Icu_kA"],
      "usage_notes": "Moulded case circuit breaker — typically 100A to 1600A. Adjustable thermal (Ir) and magnetic (Im) trip settings. Annotate trip unit type (thermal-magnetic or electronic).",
      "related_symbols": ["MCCB_4P", "ACB_3P", "MCB_3P"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "MCCB_4P",
      "iec_ref": "IEC60617-07-18-12",
      "iec_part": 7,
      "iec_description": "Moulded case circuit breaker — 4-pole",
      "draftsman_id": "MCCB_4P",
      "category": "protection",
      "display_name": "4-Pole MCCB",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -30, 50, 30],
        "path": "M -50 -20 L -25 -20 M -25 -30 L 25 -30 L 25 30 L -25 30 Z M -25 -20 L 25 -20 M 25 -20 L 50 -20 M -50 -7 L -25 -7 M -25 -7 L 25 -7 M 25 -7 L 50 -7 M -50 7 L -25 7 M -25 7 L 25 7 M 25 7 L 50 7 M -50 20 L -25 20 M -25 20 L 25 20 M 25 20 L 50 20 M -15 -10 L 15 -10",
        "terminals": {"L1_in": [-50, -20], "L2_in": [-50, -7], "L3_in": [-50, 7], "N_in": [-50, 20], "L1_out": [50, -20], "L2_out": [50, -7], "L3_out": [50, 7], "N_out": [50, 20]}
      },
      "variants": ["MCCB_3P"],
      "annotation_fields": ["In_A", "Ir_setting", "Im_setting", "Icu_kA"],
      "usage_notes": "4-pole MCCB — for circuits requiring switched neutral or 4-pole isolation (TN-S with neutral isolation, generator/utility transfer).",
      "related_symbols": ["MCCB_3P", "ACB_4P"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "ACB_3P",
      "iec_ref": "IEC60617-07-18-21",
      "iec_part": 7,
      "iec_description": "Air circuit breaker — 3-pole",
      "draftsman_id": "ACB_3P",
      "category": "protection",
      "display_name": "3-Pole ACB",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -30, 50, 30],
        "path": "M -50 -15 L -25 -15 M -25 -30 L 25 -30 L 25 30 L -25 30 Z M -25 -15 L 25 -15 M 25 -15 L 50 -15 M -50 0 L -25 0 M -25 0 L 25 0 M 25 0 L 50 0 M -50 15 L -25 15 M -25 15 L 25 15 M 25 15 L 50 15 M -15 -10 L 15 -10 M -15 -5 L 15 -5",
        "terminals": {"L1_in": [-50, -15], "L2_in": [-50, 0], "L3_in": [-50, 15], "L1_out": [50, -15], "L2_out": [50, 0], "L3_out": [50, 15]}
      },
      "variants": ["ACB_4P", "MCCB_3P"],
      "annotation_fields": ["In_A", "Icu_kA", "trip_unit"],
      "usage_notes": "Air circuit breaker — typically 800A and above, used as the incomer on main LV switchboards. Drawn similarly to MCCB but with a double internal bar to distinguish. Annotate trip unit type and short-time delay settings.",
      "related_symbols": ["ACB_4P", "MCCB_3P"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "ACB_4P",
      "iec_ref": "IEC60617-07-18-22",
      "iec_part": 7,
      "iec_description": "Air circuit breaker — 4-pole",
      "draftsman_id": "ACB_4P",
      "category": "protection",
      "display_name": "4-Pole ACB",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -30, 50, 30],
        "path": "M -50 -20 L -25 -20 M -25 -30 L 25 -30 L 25 30 L -25 30 Z M -25 -20 L 25 -20 M 25 -20 L 50 -20 M -50 -7 L -25 -7 M -25 -7 L 25 -7 M 25 -7 L 50 -7 M -50 7 L -25 7 M -25 7 L 25 7 M 25 7 L 50 7 M -50 20 L -25 20 M -25 20 L 25 20 M 25 20 L 50 20 M -15 -10 L 15 -10 M -15 -5 L 15 -5",
        "terminals": {"L1_in": [-50, -20], "L2_in": [-50, -7], "L3_in": [-50, 7], "N_in": [-50, 20], "L1_out": [50, -20], "L2_out": [50, -7], "L3_out": [50, 7], "N_out": [50, 20]}
      },
      "variants": ["ACB_3P"],
      "annotation_fields": ["In_A", "Icu_kA", "trip_unit"],
      "usage_notes": "4-pole ACB — incomer with switched neutral. Common on main LV boards with multiple supply sources.",
      "related_symbols": ["ACB_3P", "MCCB_4P"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "FUSE_1P",
      "iec_ref": "IEC60617-07-21-01",
      "iec_part": 7,
      "iec_description": "Fuse — 1-pole",
      "draftsman_id": "FUSE_1P",
      "category": "protection",
      "display_name": "1-Pole fuse",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -15, 50, 15],
        "path": "M -50 0 L -20 0 M -20 -10 L 20 -10 L 20 10 L -20 10 Z M 20 0 L 50 0",
        "terminals": {"in": [-50, 0], "out": [50, 0]}
      },
      "variants": ["FUSE_3P", "FUSE_SWITCH"],
      "annotation_fields": ["In_A", "fuse_type"],
      "usage_notes": "1-pole fuse — rectangle with leads. Annotate fuse rating and type (gG general purpose, aM motor circuit, gF fast-acting, BS88 etc.). Common at the supply intake (BS88 cut-out) and on final circuits where MCBs are not used.",
      "related_symbols": ["FUSE_3P", "FUSE_SWITCH", "MCB_1P"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "FUSE_3P",
      "iec_ref": "IEC60617-07-21-02",
      "iec_part": 7,
      "iec_description": "Fuse — 3-pole",
      "draftsman_id": "FUSE_3P",
      "category": "protection",
      "display_name": "3-Pole fuses",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -25, 50, 25],
        "path": "M -50 -15 L -20 -15 M -20 -25 L 20 -25 L 20 -5 L -20 -5 Z M 20 -15 L 50 -15 M -50 0 L -20 0 M -20 -10 L 20 -10 M 20 0 L 50 0 M -50 15 L -20 15 M -20 5 L 20 5 L 20 25 L -20 25 Z M 20 15 L 50 15",
        "terminals": {"L1_in": [-50, -15], "L2_in": [-50, 0], "L3_in": [-50, 15], "L1_out": [50, -15], "L2_out": [50, 0], "L3_out": [50, 15]}
      },
      "variants": ["FUSE_1P", "FUSE_SWITCH"],
      "annotation_fields": ["In_A", "fuse_type"],
      "usage_notes": "Three single-pole fuses in a 3-phase circuit, drawn aligned. Use for fused supply intake or as backup protection.",
      "related_symbols": ["FUSE_1P", "FUSE_SWITCH"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "FUSE_SWITCH",
      "iec_ref": "IEC60617-07-21-04",
      "iec_part": 7,
      "iec_description": "Fuse-switch (switch-fuse)",
      "draftsman_id": "FUSE_SWITCH",
      "category": "protection",
      "display_name": "Fuse-switch / switch-fuse",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -20, 50, 20],
        "path": "M -50 0 L -25 0 M -25 0 L -2 -18 M 0 -10 L 30 -10 L 30 10 L 0 10 Z M 30 0 L 50 0",
        "terminals": {"in": [-50, 0], "out": [50, 0]}
      },
      "variants": ["FUSE_1P", "SWITCH_DISCONNECTOR_2P"],
      "annotation_fields": ["In_A", "fuse_type", "rated_A_switch"],
      "usage_notes": "Combined fuse and switch — switch breaks load, fuse provides backup protection. Common as a main isolator on industrial DBs. Annotate fuse and switch ratings.",
      "related_symbols": ["FUSE_1P", "SWITCH_DISCONNECTOR_2P"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "CONTACTOR_3P",
      "iec_ref": "IEC60617-07-19-01",
      "iec_part": 7,
      "iec_description": "Contactor — 3-pole",
      "draftsman_id": "CONTACTOR_3P",
      "category": "switching",
      "display_name": "3-Pole contactor",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -30, 50, 30],
        "path": "M -50 -15 L -15 -15 M -15 -15 L 12 -33 M 15 -15 L 50 -15 M -50 0 L -15 0 M -15 0 L 12 -18 M 15 0 L 50 0 M -50 15 L -15 15 M -15 15 L 12 -3 M 15 15 L 50 15 M -15 -30 L -15 30 M -20 -28 A 5 5 0 1 0 -10 -28 A 5 5 0 1 0 -20 -28 Z",
        "terminals": {"L1_in": [-50, -15], "L2_in": [-50, 0], "L3_in": [-50, 15], "L1_out": [50, -15], "L2_out": [50, 0], "L3_out": [50, 15]}
      },
      "variants": ["CONTACTOR_STAR_DELTA", "CONTACTOR_GENERAL", "RELAY_COIL"],
      "annotation_fields": ["AC_rating_A", "AC3_kW", "tag"],
      "usage_notes": "3-pole contactor for motor control. Coil shown separately. Small circle at top indicates the automatic-return spring. Annotate AC3 rating (motor switching).",
      "related_symbols": ["CONTACTOR_STAR_DELTA", "RELAY_COIL", "MOTOR_STARTER_DOL", "RELAY_THERMAL"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "CONTACTOR_STAR_DELTA",
      "iec_ref": "IEC60617-07-19-02",
      "iec_part": 7,
      "iec_description": "Star-delta contactor set",
      "draftsman_id": "CONTACTOR_STAR_DELTA",
      "category": "switching",
      "display_name": "Star-delta contactor set",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -30, 50, 30],
        "path": "M -50 -15 L -30 -15 M -30 -15 L -10 -28 M -30 -15 L -30 15 M -10 -15 L 10 -28 M -10 -15 L -10 15 M 10 -15 L 30 -28 M 10 -15 L 10 15 M -30 15 L -10 0 M -10 15 L 10 0 M 10 15 L 30 0 M -30 0 L 50 0",
        "terminals": {"L_in": [-50, -15], "M_out": [50, 0]}
      },
      "variants": ["CONTACTOR_3P", "MOTOR_STARTER_SD"],
      "annotation_fields": ["AC_rating_A", "rated_kW"],
      "usage_notes": "Three contactors arranged for star-delta motor starting (main, star, delta). Drawn as a single composite symbol. See MOTOR_STARTER_SD for the complete starter symbol.",
      "related_symbols": ["CONTACTOR_3P", "MOTOR_STARTER_SD"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "RELAY_COIL",
      "iec_ref": "IEC60617-07-15-01",
      "iec_part": 7,
      "iec_description": "Relay coil (operating coil)",
      "draftsman_id": "RELAY_COIL",
      "category": "switching",
      "display_name": "Relay coil",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -15, 50, 15],
        "path": "M -50 0 L -20 0 M -20 -15 L 20 -15 L 20 15 L -20 15 Z M 20 0 L 50 0 M -10 -15 L -10 15",
        "terminals": {"a1": [-50, 0], "a2": [50, 0]}
      },
      "variants": ["RELAY_THERMAL", "RELAY_GENERAL"],
      "annotation_fields": ["coil_V", "tag"],
      "usage_notes": "Relay / contactor coil — rectangle with vertical bar. Annotate coil voltage (e.g. 230V AC, 24V DC) and tag. Pairs with contacts elsewhere on the schematic.",
      "related_symbols": ["CONTACTOR_3P", "RELAY_THERMAL", "CONTACT_NO", "CONTACT_NC"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "RELAY_THERMAL",
      "iec_ref": "IEC60617-07-15-02",
      "iec_part": 7,
      "iec_description": "Thermal overload relay",
      "draftsman_id": "RELAY_THERMAL",
      "category": "protection",
      "display_name": "Thermal overload relay",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -30, 50, 30],
        "path": "M -50 -15 L -25 -15 M -25 -30 L 25 -30 L 25 30 L -25 30 Z M -25 -15 L 25 -15 M 25 -15 L 50 -15 M -50 0 L -25 0 M -25 0 L 25 0 M 25 0 L 50 0 M -50 15 L -25 15 M -25 15 L 25 15 M 25 15 L 50 15 M -10 -10 L 10 -10 L -10 10 L 10 10",
        "terminals": {"L1_in": [-50, -15], "L2_in": [-50, 0], "L3_in": [-50, 15], "L1_out": [50, -15], "L2_out": [50, 0], "L3_out": [50, 15]}
      },
      "variants": ["MCB_MOTOR"],
      "annotation_fields": ["set_A_range", "trip_class"],
      "usage_notes": "Thermal overload relay — installed in series with contactor for motor protection. Zigzag indicates thermal bimetal element. Annotate set current range and trip class (10, 20, 30).",
      "related_symbols": ["CONTACTOR_3P", "MCB_MOTOR", "MOTOR_STARTER_DOL"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "MCB_MOTOR",
      "iec_ref": "IEC60617-07-18-13",
      "iec_part": 7,
      "iec_description": "Motor protection circuit breaker (MPCB)",
      "draftsman_id": "MCB_MOTOR",
      "category": "protection",
      "display_name": "Motor circuit breaker (MPCB)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -30, 50, 30],
        "path": "M -50 -15 L -25 -15 M -25 -30 L 25 -30 L 25 30 L -25 30 Z M -25 -15 L 25 -15 M 25 -15 L 50 -15 M -50 0 L -25 0 M -25 0 L 25 0 M 25 0 L 50 0 M -50 15 L -25 15 M -25 15 L 25 15 M 25 15 L 50 15 M -10 -25 L 10 -25 M -15 -10 L 15 10",
        "terminals": {"L1_in": [-50, -15], "L2_in": [-50, 0], "L3_in": [-50, 15], "L1_out": [50, -15], "L2_out": [50, 0], "L3_out": [50, 15]}
      },
      "variants": ["MCCB_3P", "RELAY_THERMAL"],
      "annotation_fields": ["In_A", "set_A", "Icu_kA"],
      "usage_notes": "Motor protection circuit breaker — combines short-circuit (magnetic) and overload (thermal) protection in one device. Standard final-circuit motor protection up to ~32A. Annotate set current.",
      "related_symbols": ["RELAY_THERMAL", "CONTACTOR_3P", "MOTOR_STARTER_DOL"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "RCD_2P",
      "iec_ref": "IEC60617-07-22-01",
      "iec_part": 7,
      "iec_description": "Residual current device (RCD/RCCB) — 2-pole",
      "draftsman_id": "RCD_2P",
      "category": "protection",
      "display_name": "2-Pole RCD (RCCB)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -30, 50, 30],
        "path": "M -50 -10 L -20 -10 M -20 -30 L 20 -30 L 20 30 L -20 30 Z M -20 -10 L 20 -10 M 20 -10 L 50 -10 M -50 10 L -20 10 M -20 10 L 20 10 M 20 10 L 50 10 M -10 -20 L 10 -20 M 0 0 A 8 8 0 1 0 0 16 A 8 8 0 1 0 0 0",
        "terminals": {"L_in": [-50, -10], "N_in": [-50, 10], "L_out": [50, -10], "N_out": [50, 10]}
      },
      "variants": ["RCD_4P", "RCBO_1P", "RCBO_2P"],
      "annotation_fields": ["In_A", "IDn_mA", "type"],
      "usage_notes": "2-pole RCD — no overload protection (must be paired with an MCB upstream). Internal toroid symbol (figure-of-eight). Annotate sensitivity (30mA standard for socket outlets) and type (AC, A, F, B).",
      "related_symbols": ["RCBO_1P", "RCD_4P", "RELAY_EARTH_LEAKAGE"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "RCD_4P",
      "iec_ref": "IEC60617-07-22-02",
      "iec_part": 7,
      "iec_description": "Residual current device (RCD/RCCB) — 4-pole",
      "draftsman_id": "RCD_4P",
      "category": "protection",
      "display_name": "4-Pole RCD (RCCB)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -30, 50, 30],
        "path": "M -50 -20 L -20 -20 M -20 -30 L 20 -30 L 20 30 L -20 30 Z M -20 -20 L 20 -20 M 20 -20 L 50 -20 M -50 -7 L -20 -7 M -20 -7 L 20 -7 M 20 -7 L 50 -7 M -50 7 L -20 7 M -20 7 L 20 7 M 20 7 L 50 7 M -50 20 L -20 20 M -20 20 L 20 20 M 20 20 L 50 20 M 0 -10 A 6 6 0 1 0 0 2 A 6 6 0 1 0 0 -10",
        "terminals": {"L1_in": [-50, -20], "L2_in": [-50, -7], "L3_in": [-50, 7], "N_in": [-50, 20], "L1_out": [50, -20], "L2_out": [50, -7], "L3_out": [50, 7], "N_out": [50, 20]}
      },
      "variants": ["RCD_2P"],
      "annotation_fields": ["In_A", "IDn_mA", "type"],
      "usage_notes": "4-pole RCD for 3-phase + N circuits. Required for 3-phase final circuits with shock protection (workshops, kitchens, EV chargers).",
      "related_symbols": ["RCD_2P", "RCBO_2P"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "RCBO_1P",
      "iec_ref": "IEC60617-07-22-11",
      "iec_part": 7,
      "iec_description": "Residual current circuit-breaker with overcurrent protection — 1P+N",
      "draftsman_id": "RCBO_1P",
      "category": "protection",
      "display_name": "1-Pole RCBO",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -30, 50, 30],
        "path": "M -50 -10 L -20 -10 M -20 -30 L 20 -30 L 20 30 L -20 30 Z M -20 -10 L 20 -10 M 20 -10 L 50 -10 M -50 10 L -20 10 M -20 10 L 20 10 M 20 10 L 50 10 M 0 -22 A 6 6 0 1 0 0 -10 A 6 6 0 1 0 0 -22 M -10 0 L 10 20",
        "terminals": {"L_in": [-50, -10], "N_in": [-50, 10], "L_out": [50, -10], "N_out": [50, 10]}
      },
      "variants": ["RCBO_2P", "MCB_1P", "RCD_2P"],
      "annotation_fields": ["In_A", "IDn_mA", "curve", "type"],
      "usage_notes": "Combined MCB + RCD in a single device — 1P+N width. Standard for final circuits requiring both overcurrent and earth fault protection (UK domestic since 18th Edition).",
      "related_symbols": ["MCB_1P", "RCD_2P", "RCBO_2P"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "RCBO_2P",
      "iec_ref": "IEC60617-07-22-12",
      "iec_part": 7,
      "iec_description": "Residual current circuit-breaker with overcurrent — 2P",
      "draftsman_id": "RCBO_2P",
      "category": "protection",
      "display_name": "2-Pole RCBO",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -30, 50, 30],
        "path": "M -50 -10 L -20 -10 M -20 -30 L 20 -30 L 20 30 L -20 30 Z M -20 -10 L 20 -10 M 20 -10 L 50 -10 M -50 10 L -20 10 M -20 10 L 20 10 M 20 10 L 50 10 M 0 -22 A 6 6 0 1 0 0 -10 A 6 6 0 1 0 0 -22 M -10 0 L 10 20 M -10 22 L 10 22",
        "terminals": {"L_in": [-50, -10], "N_in": [-50, 10], "L_out": [50, -10], "N_out": [50, 10]}
      },
      "variants": ["RCBO_1P"],
      "annotation_fields": ["In_A", "IDn_mA", "curve", "type"],
      "usage_notes": "2-pole RCBO — switches both L and N. Required for IT systems and some EV circuits.",
      "related_symbols": ["RCBO_1P", "RCD_2P"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "SPD_TYPE1",
      "iec_ref": "IEC60617-07-25-01",
      "iec_part": 7,
      "iec_description": "Surge protective device — Type 1 (Iimp)",
      "draftsman_id": "SPD_TYPE1",
      "category": "protection",
      "display_name": "SPD Type 1",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -25, 50, 25],
        "path": "M -50 0 L 0 0 M 0 -25 L 25 0 L 0 25 L -25 0 Z M 0 25 L 0 50",
        "terminals": {"line": [-50, 0], "earth": [0, 50]}
      },
      "variants": ["SPD_TYPE2", "SPD_TYPE3"],
      "annotation_fields": ["Iimp_kA", "Up_kV", "Uc_V"],
      "usage_notes": "Type 1 SPD — diamond shape with earth lead. Tests using lightning impulse (10/350μs). Required where LPS is installed or for buildings in high lightning exposure. Annotate Iimp, Up, Uc.",
      "related_symbols": ["SPD_TYPE2", "SPD_TYPE3", "EARTH_GENERAL"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "SPD_TYPE2",
      "iec_ref": "IEC60617-07-25-02",
      "iec_part": 7,
      "iec_description": "Surge protective device — Type 2 (In)",
      "draftsman_id": "SPD_TYPE2",
      "category": "protection",
      "display_name": "SPD Type 2",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -25, 50, 25],
        "path": "M -50 0 L 0 0 M 0 -20 L 20 0 L 0 20 L -20 0 Z M 0 20 L 0 50",
        "terminals": {"line": [-50, 0], "earth": [0, 50]}
      },
      "variants": ["SPD_TYPE1", "SPD_TYPE3"],
      "annotation_fields": ["In_kA", "Up_kV", "Uc_V"],
      "usage_notes": "Type 2 SPD — smaller diamond. Tests using 8/20μs nominal. Required at main DB in all new installations (IEC 60364-4-44 AMD2:2018). Annotate In, Up, Uc.",
      "related_symbols": ["SPD_TYPE1", "SPD_TYPE3"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "SPD_TYPE3",
      "iec_ref": "IEC60617-07-25-03",
      "iec_part": 7,
      "iec_description": "Surge protective device — Type 3 (point-of-use)",
      "draftsman_id": "SPD_TYPE3",
      "category": "protection",
      "display_name": "SPD Type 3",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -20, 50, 25],
        "path": "M -50 0 L 0 0 M 0 -15 L 15 0 L 0 15 L -15 0 Z M 0 15 L 0 50",
        "terminals": {"line": [-50, 0], "earth": [0, 50]}
      },
      "variants": ["SPD_TYPE1", "SPD_TYPE2"],
      "annotation_fields": ["Up_kV", "Uc_V"],
      "usage_notes": "Type 3 SPD — point-of-use protection for sensitive equipment. Lowest let-through voltage (Up ≤ 1.5kV typically). Annotate Up.",
      "related_symbols": ["SPD_TYPE1", "SPD_TYPE2"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "ATS_2WAY",
      "iec_ref": "IEC60617-07-26-01",
      "iec_part": 7,
      "iec_description": "Automatic transfer switch — 2-way",
      "draftsman_id": "ATS_2WAY",
      "category": "switching",
      "display_name": "ATS (2-way)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -30, 50, 30],
        "path": "M -50 -20 L -20 -20 M -20 -30 L 20 -30 L 20 30 L -20 30 Z M -20 -20 L 0 0 M -20 20 L 0 0 M 20 0 L 50 0 M -10 -10 L 10 -10 M -50 20 L -20 20",
        "terminals": {"source_A": [-50, -20], "source_B": [-50, 20], "load": [50, 0]}
      },
      "variants": ["ATS_3WAY", "TRANSFER_SWITCH_MANUAL", "BUS_SECTION_SWITCH"],
      "annotation_fields": ["rated_A", "transfer_time_s"],
      "usage_notes": "Automatic transfer switch — selects between two power sources (typically utility and generator). Two inputs, one output. Annotate rated current and transfer time. Internal logic controls source selection.",
      "related_symbols": ["ATS_3WAY", "TRANSFER_SWITCH_MANUAL"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "ATS_3WAY",
      "iec_ref": "IEC60617-07-26-02",
      "iec_part": 7,
      "iec_description": "Automatic transfer switch — 3-way",
      "draftsman_id": "ATS_3WAY",
      "category": "switching",
      "display_name": "ATS (3-way)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -30, 50, 30],
        "path": "M -50 -20 L -20 -20 M -20 -30 L 20 -30 L 20 30 L -20 30 Z M -20 -20 L 0 0 M -20 0 L 0 0 M -20 20 L 0 0 M 20 0 L 50 0 M -50 0 L -20 0 M -50 20 L -20 20",
        "terminals": {"source_A": [-50, -20], "source_B": [-50, 0], "source_C": [-50, 20], "load": [50, 0]}
      },
      "variants": ["ATS_2WAY"],
      "annotation_fields": ["rated_A", "transfer_time_s"],
      "usage_notes": "Three-way ATS — selects between three sources (e.g. utility, generator, UPS). Used in critical applications (data centres, hospitals).",
      "related_symbols": ["ATS_2WAY", "TRANSFER_SWITCH_MANUAL"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "TRANSFER_SWITCH_MANUAL",
      "iec_ref": "IEC60617-07-26-03",
      "iec_part": 7,
      "iec_description": "Manual transfer switch",
      "draftsman_id": "TRANSFER_SWITCH_MANUAL",
      "category": "switching",
      "display_name": "Manual transfer switch",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -25, 50, 25],
        "path": "M -50 -15 L -20 -15 M -20 -15 L 0 0 M 0 0 L 30 -15 M 0 0 L 30 15 M -50 15 L -20 15 M -20 15 L 0 0 M 30 -15 L 50 -15 M 30 15 L 50 15",
        "terminals": {"source_A": [-50, -15], "source_B": [-50, 15], "load_A": [50, -15], "load_B": [50, 15]}
      },
      "variants": ["ATS_2WAY"],
      "annotation_fields": ["rated_A"],
      "usage_notes": "Manual transfer switch / changeover switch — operator selects source. Used for small installations or as bypass for an ATS.",
      "related_symbols": ["ATS_2WAY", "ATS_3WAY"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "RELAY_EARTH_LEAKAGE",
      "iec_ref": "IEC60617-07-22-03",
      "iec_part": 7,
      "iec_description": "Earth leakage relay (sensing only)",
      "draftsman_id": "RELAY_EARTH_LEAKAGE",
      "category": "protection",
      "display_name": "Earth leakage relay",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -25, 50, 25],
        "path": "M -50 0 L -20 0 M -20 -20 L 20 -20 L 20 20 L -20 20 Z M 20 0 L 50 0 M 0 0 A 8 8 0 1 0 0 16 A 8 8 0 1 0 0 0 M 0 -10 L 0 -25",
        "terminals": {"L": [-50, 0], "out": [50, 0], "trip_signal": [0, -25]}
      },
      "variants": ["RCD_4P"],
      "annotation_fields": ["IDn_mA", "trip_output"],
      "usage_notes": "Earth leakage relay — sensing only, must be paired with a separate switching device (contactor or shunt-trip MCCB). Used on larger circuits where a single RCCB rating is not available.",
      "related_symbols": ["RCD_4P", "CONTACTOR_3P"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "CONTACT_INTERLOCK",
      "iec_ref": "IEC60617-07-08-02",
      "iec_part": 7,
      "iec_description": "Interlocked contacts",
      "draftsman_id": "CONTACT_INTERLOCK",
      "category": "switching",
      "display_name": "Interlock contact",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -25, 50, 25],
        "path": "M -50 -10 L -15 -10 M -15 -10 L 12 -28 M 15 -10 L 50 -10 M -50 10 L -15 10 M -15 10 L 12 -8 M 15 10 L 50 10 M 0 -15 L 0 15",
        "terminals": {"line1_in": [-50, -10], "line1_out": [50, -10], "line2_in": [-50, 10], "line2_out": [50, 10]}
      },
      "variants": ["CONTACT_NO", "CONTACT_AUX_NO"],
      "annotation_fields": ["tag"],
      "usage_notes": "Mechanically interlocked pair of contacts — both cannot be closed simultaneously. Vertical line indicates the interlock. Used between source ATS contactors (utility/generator) to prevent paralleling.",
      "related_symbols": ["CONTACT_NO", "ATS_2WAY"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "CONTACT_AUX_NO",
      "iec_ref": "IEC60617-07-08-03",
      "iec_part": 7,
      "iec_description": "Auxiliary contact — NO",
      "draftsman_id": "CONTACT_AUX_NO",
      "category": "switching",
      "display_name": "Auxiliary contact (NO)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -20, 50, 20],
        "path": "M -50 0 L -15 0 M -15 0 L 12 -18 M 15 0 L 50 0 M -25 -15 L -10 -15",
        "terminals": {"in": [-50, 0], "out": [50, 0]}
      },
      "variants": ["CONTACT_NO", "CONTACT_AUX_NC"],
      "annotation_fields": ["tag", "parent_device"],
      "usage_notes": "Auxiliary contact — derived from a power contactor or breaker. NO state. Used for control logic, indication. Annotate the parent device tag.",
      "related_symbols": ["CONTACT_NO", "CONTACTOR_3P", "MCCB_3P"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "CONTACT_AUX_NC",
      "iec_ref": "IEC60617-07-08-04",
      "iec_part": 7,
      "iec_description": "Auxiliary contact — NC",
      "draftsman_id": "CONTACT_AUX_NC",
      "category": "switching",
      "display_name": "Auxiliary contact (NC)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -20, 50, 20],
        "path": "M -50 0 L -15 0 M -15 -20 L -15 20 M -15 0 L 15 0 M 15 -20 L 15 20 M 15 0 L 50 0 M -20 -15 L 20 15 M -25 -15 L -10 -15",
        "terminals": {"in": [-50, 0], "out": [50, 0]}
      },
      "variants": ["CONTACT_NC", "CONTACT_AUX_NO"],
      "annotation_fields": ["tag", "parent_device"],
      "usage_notes": "Auxiliary contact, NC state. Often used for fault/trip signalling from a breaker.",
      "related_symbols": ["CONTACT_NC", "CONTACTOR_3P"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "PUSHBUTTON_NO",
      "iec_ref": "IEC60617-07-07-01",
      "iec_part": 7,
      "iec_description": "Push-button — make contact",
      "draftsman_id": "PUSHBUTTON_NO",
      "category": "switching",
      "display_name": "Pushbutton (NO)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -25, 50, 25],
        "path": "M -50 0 L -15 0 M -15 -15 L 15 -15 M -15 0 L 15 0 M 15 -15 L 15 15 M 15 0 L 50 0 M 0 -15 L 0 -25",
        "terminals": {"in": [-50, 0], "out": [50, 0]}
      },
      "variants": ["PUSHBUTTON_NC", "PUSHBUTTON_ILLUMINATED", "EMERGENCY_STOP"],
      "annotation_fields": ["function"],
      "usage_notes": "Push-to-make pushbutton — momentary NO contact. Vertical line indicates the plunger. Used for start, reset, accept commands.",
      "related_symbols": ["PUSHBUTTON_NC", "CONTACT_NO", "EMERGENCY_STOP"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "PUSHBUTTON_NC",
      "iec_ref": "IEC60617-07-07-02",
      "iec_part": 7,
      "iec_description": "Push-button — break contact",
      "draftsman_id": "PUSHBUTTON_NC",
      "category": "switching",
      "display_name": "Pushbutton (NC)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -25, 50, 25],
        "path": "M -50 0 L -15 0 M -15 -15 L -15 15 M -15 0 L 15 0 M 15 -15 L 15 15 M 15 0 L 50 0 M -20 -15 L 20 15 M 0 15 L 0 25",
        "terminals": {"in": [-50, 0], "out": [50, 0]}
      },
      "variants": ["PUSHBUTTON_NO", "EMERGENCY_STOP"],
      "annotation_fields": ["function"],
      "usage_notes": "Push-to-break pushbutton — momentary NC contact. Used for stop, cancel commands.",
      "related_symbols": ["PUSHBUTTON_NO", "EMERGENCY_STOP"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "PUSHBUTTON_ILLUMINATED",
      "iec_ref": "IEC60617-07-07-03",
      "iec_part": 7,
      "iec_description": "Illuminated push-button",
      "draftsman_id": "PUSHBUTTON_ILLUMINATED",
      "category": "switching",
      "display_name": "Illuminated pushbutton",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -25, 50, 25],
        "path": "M -50 0 L -15 0 M -15 -15 L 15 -15 M -15 0 L 15 0 M 15 -15 L 15 15 M 15 0 L 50 0 M 0 -15 L 0 -25 M -20 -8 L 20 -8 M -15 -3 L -5 -8 M 5 -3 L 15 -8",
        "terminals": {"in": [-50, 0], "out": [50, 0], "lamp_a": [-15, 20], "lamp_b": [15, 20]}
      },
      "variants": ["PUSHBUTTON_NO"],
      "annotation_fields": ["function", "lamp_colour"],
      "usage_notes": "Pushbutton with integral lamp — combines a contact and an indicator. Annotate lamp colour and function.",
      "related_symbols": ["PUSHBUTTON_NO", "INDICATOR_LAMP"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "EMERGENCY_STOP",
      "iec_ref": "IEC60617-07-07-04",
      "iec_part": 7,
      "iec_description": "Emergency stop button (mushroom head)",
      "draftsman_id": "EMERGENCY_STOP",
      "category": "switching",
      "display_name": "Emergency stop",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -25, 50, 25],
        "path": "M -50 0 L -15 0 M -15 -15 L -15 15 M -15 0 L 15 0 M 15 -15 L 15 15 M 15 0 L 50 0 M -20 -15 L 20 15 M 20 -25 A 20 20 0 1 0 -20 -25 A 20 20 0 1 0 20 -25 Z",
        "terminals": {"in": [-50, 0], "out": [50, 0]}
      },
      "variants": ["PUSHBUTTON_NC"],
      "annotation_fields": ["function"],
      "usage_notes": "Emergency stop — NC contact with mushroom-head latching pushbutton. Drawn with a circle above the contact symbol. Required at machinery to ISO 13850.",
      "related_symbols": ["PUSHBUTTON_NC"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "KEY_SWITCH",
      "iec_ref": "IEC60617-07-07-06",
      "iec_part": 7,
      "iec_description": "Key-operated switch",
      "draftsman_id": "KEY_SWITCH",
      "category": "switching",
      "display_name": "Key switch",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -25, 50, 25],
        "path": "M -50 0 L -15 0 M -15 0 L 12 -18 M 15 0 L 50 0 M 0 -25 L 0 -10 M -5 -22 A 5 5 0 1 0 5 -22 A 5 5 0 1 0 -5 -22 Z",
        "terminals": {"in": [-50, 0], "out": [50, 0]}
      },
      "variants": ["SELECTOR_SWITCH_2POS", "SWITCH_1P"],
      "annotation_fields": ["function"],
      "usage_notes": "Key-operated switch — switch with a key symbol on top. Used for secure or critical operations (e.g. lift maintenance, hospital theatre changeover).",
      "related_symbols": ["SELECTOR_SWITCH_2POS", "SWITCH_1P"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "SELECTOR_SWITCH_2POS",
      "iec_ref": "IEC60617-07-07-07",
      "iec_part": 7,
      "iec_description": "Selector switch — 2-position",
      "draftsman_id": "SELECTOR_SWITCH_2POS",
      "category": "switching",
      "display_name": "Selector switch (2-position)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -25, 50, 25],
        "path": "M -50 -10 L -15 -10 M -15 -10 L 0 0 M -50 10 L -15 10 M -15 10 L 0 0 M 0 0 L 15 -10 M 0 0 L 15 10 M 15 -10 L 50 -10 M 15 10 L 50 10",
        "terminals": {"in_a": [-50, -10], "in_b": [-50, 10], "out_a": [50, -10], "out_b": [50, 10]}
      },
      "variants": ["SELECTOR_SWITCH_3POS", "CONTACT_CHANGEOVER"],
      "annotation_fields": ["positions", "function"],
      "usage_notes": "Two-position rotary selector. Common for hand/off, manual/auto.",
      "related_symbols": ["SELECTOR_SWITCH_3POS", "KEY_SWITCH"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "SELECTOR_SWITCH_3POS",
      "iec_ref": "IEC60617-07-07-08",
      "iec_part": 7,
      "iec_description": "Selector switch — 3-position",
      "draftsman_id": "SELECTOR_SWITCH_3POS",
      "category": "switching",
      "display_name": "Selector switch (3-position)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -25, 50, 25],
        "path": "M -50 -15 L -15 -15 M -15 -15 L 0 0 M -50 0 L -15 0 M -15 0 L 0 0 M -50 15 L -15 15 M -15 15 L 0 0 M 0 0 L 15 -15 M 0 0 L 15 0 M 0 0 L 15 15 M 15 -15 L 50 -15 M 15 0 L 50 0 M 15 15 L 50 15",
        "terminals": {"in_a": [-50, -15], "in_b": [-50, 0], "in_c": [-50, 15], "out_a": [50, -15], "out_b": [50, 0], "out_c": [50, 15]}
      },
      "variants": ["SELECTOR_SWITCH_2POS"],
      "annotation_fields": ["positions", "function"],
      "usage_notes": "Three-position rotary selector. Common for hand/off/auto, forward/off/reverse.",
      "related_symbols": ["SELECTOR_SWITCH_2POS"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "CONTACT_ON_DELAY",
      "iec_ref": "IEC60617-07-09-01",
      "iec_part": 7,
      "iec_description": "Time-delay contact, on-delay (delayed when closing)",
      "draftsman_id": "CONTACT_ON_DELAY",
      "category": "switching",
      "display_name": "Time-delay contact (on-delay)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -25, 50, 25],
        "path": "M -50 0 L -15 0 M -15 0 L 12 -18 M 15 -20 L 15 20 M 15 0 L 50 0 M -25 -20 L -25 -10 A 10 10 0 0 0 -15 0",
        "terminals": {"in": [-50, 0], "out": [50, 0]}
      },
      "variants": ["CONTACT_OFF_DELAY", "DELAY_SYMBOL", "CONTACT_NO"],
      "annotation_fields": ["delay_s"],
      "usage_notes": "On-delay contact — delays closing after operation. Curve symbol indicates the timing function. Annotate delay duration.",
      "related_symbols": ["CONTACT_OFF_DELAY", "DELAY_SYMBOL"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "CONTACT_OFF_DELAY",
      "iec_ref": "IEC60617-07-09-02",
      "iec_part": 7,
      "iec_description": "Time-delay contact, off-delay (delayed when opening)",
      "draftsman_id": "CONTACT_OFF_DELAY",
      "category": "switching",
      "display_name": "Time-delay contact (off-delay)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -25, 50, 25],
        "path": "M -50 0 L -15 0 M -15 0 L 12 -18 M 15 -20 L 15 20 M 15 0 L 50 0 M 25 -20 L 25 -10 A 10 10 0 0 1 15 0",
        "terminals": {"in": [-50, 0], "out": [50, 0]}
      },
      "variants": ["CONTACT_ON_DELAY"],
      "annotation_fields": ["delay_s"],
      "usage_notes": "Off-delay contact — delays opening after de-energising. Mirror curve symbol. Annotate delay duration.",
      "related_symbols": ["CONTACT_ON_DELAY", "DELAY_SYMBOL"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "DISCONNECT_HANDLE",
      "iec_ref": "IEC60617-07-13-09",
      "iec_part": 7,
      "iec_description": "Disconnect handle (manual operating mechanism)",
      "draftsman_id": "DISCONNECT_HANDLE",
      "category": "switching",
      "display_name": "Manual disconnect handle",
      "geometry": {
        "grid": 100,
        "bbox": [-25, -25, 25, 25],
        "path": "M 0 -25 L 0 25 M -15 0 L 15 0",
        "terminals": {}
      },
      "variants": [],
      "annotation_fields": [],
      "usage_notes": "Qualifying overlay indicating a switching device has a manual external handle. Often combined with SWITCH_DISCONNECTOR or ISOLATOR.",
      "related_symbols": ["SWITCH_DISCONNECTOR_3P", "ISOLATOR_3P"],
      "generating_shared_symbol": false
    },
    {
      "symbol_id": "LIMITER_CURRENT",
      "iec_ref": "IEC60617-07-21-05",
      "iec_part": 7,
      "iec_description": "Current limiter",
      "draftsman_id": "LIMITER_CURRENT",
      "category": "protection",
      "display_name": "Current limiter",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -15, 50, 15],
        "path": "M -50 0 L -20 0 M -20 -10 L 20 -10 L 20 10 L -20 10 Z M 20 0 L 50 0 M -10 -10 L -10 10 M 10 -10 L 10 10",
        "terminals": {"in": [-50, 0], "out": [50, 0]}
      },
      "variants": ["FUSE_1P"],
      "annotation_fields": ["limit_A", "let_through_A"],
      "usage_notes": "Current-limiting device — fuse-like rectangle with internal bars. Used to reduce let-through energy at high PSCC.",
      "related_symbols": ["FUSE_1P", "MCCB_3P"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "LIMITER_VOLTAGE",
      "iec_ref": "IEC60617-07-25-04",
      "iec_part": 7,
      "iec_description": "Voltage limiter",
      "draftsman_id": "LIMITER_VOLTAGE",
      "category": "protection",
      "display_name": "Voltage limiter",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -25, 50, 25],
        "path": "M -50 0 L 0 0 M 0 -15 L 15 0 L 0 15 L -15 0 Z M 0 15 L 0 25 L 20 25",
        "terminals": {"line": [-50, 0], "earth": [20, 25]}
      },
      "variants": ["SPD_TYPE2", "SPD_TYPE3"],
      "annotation_fields": ["Uc_V", "Up_kV"],
      "usage_notes": "Voltage limiter — diamond with earth lead. Generic form for an MOV or gas discharge tube. SPD_TYPE2 is the formal IEC type-classified form.",
      "related_symbols": ["SPD_TYPE2", "SPD_TYPE3"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "RELAY_OVERCURRENT",
      "iec_ref": "IEC60617-07-15-04",
      "iec_part": 7,
      "iec_description": "Overcurrent relay",
      "draftsman_id": "RELAY_OVERCURRENT",
      "category": "protection",
      "display_name": "Overcurrent relay",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -15, 50, 15],
        "path": "M -50 0 L -20 0 M -20 -15 L 20 -15 L 20 15 L -20 15 Z M 20 0 L 50 0 M -10 -10 L 10 10 M -10 0 L 10 0",
        "terminals": {"in": [-50, 0], "out": [50, 0]}
      },
      "variants": ["RELAY_GENERAL", "RELAY_THERMAL"],
      "annotation_fields": ["pickup_A", "time_s"],
      "usage_notes": "Overcurrent protection relay — rectangle with internal indication. Used on MV switchgear, large MCCBs with separate trip units.",
      "related_symbols": ["RELAY_GENERAL", "MCCB_3P"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "RELAY_UNDERVOLTAGE",
      "iec_ref": "IEC60617-07-15-05",
      "iec_part": 7,
      "iec_description": "Undervoltage relay",
      "draftsman_id": "RELAY_UNDERVOLTAGE",
      "category": "protection",
      "display_name": "Undervoltage relay",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -15, 50, 15],
        "path": "M -50 0 L -20 0 M -20 -15 L 20 -15 L 20 15 L -20 15 Z M 20 0 L 50 0 M -10 -8 L -5 -8 M -8 -8 L -8 8 M 5 -8 L 10 -8 M 8 -8 L 8 8",
        "terminals": {"in": [-50, 0], "out": [50, 0]}
      },
      "variants": ["RELAY_GENERAL"],
      "annotation_fields": ["pickup_V", "time_s"],
      "usage_notes": "Undervoltage relay — used for automatic disconnection on supply loss (e.g. generator changeover trigger, motor undervoltage trip).",
      "related_symbols": ["RELAY_GENERAL"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "RELAY_DIFFERENTIAL",
      "iec_ref": "IEC60617-07-15-06",
      "iec_part": 7,
      "iec_description": "Differential relay",
      "draftsman_id": "RELAY_DIFFERENTIAL",
      "category": "protection",
      "display_name": "Differential relay",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -20, 50, 20],
        "path": "M -50 -10 L -20 -10 M -20 -20 L 20 -20 L 20 20 L -20 20 Z M 20 -10 L 50 -10 M -50 10 L -20 10 M 20 10 L 50 10 M -10 -5 L 10 5 M 10 -5 L -10 5",
        "terminals": {"in_a": [-50, -10], "in_b": [-50, 10], "out_a": [50, -10], "out_b": [50, 10]}
      },
      "variants": ["RELAY_GENERAL"],
      "annotation_fields": ["bias", "pickup_A"],
      "usage_notes": "Differential protection relay — compares current in two CTs (in/out). Used for transformer differential, busbar protection.",
      "related_symbols": ["RELAY_GENERAL", "TRANSFORMER_CURRENT"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "MOTOR_STARTER_DOL",
      "iec_ref": "IEC60617-07-19-03",
      "iec_part": 7,
      "iec_description": "Direct-on-line motor starter",
      "draftsman_id": "MOTOR_STARTER_DOL",
      "category": "switching",
      "display_name": "DOL motor starter",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -30, 50, 30],
        "path": "M -50 0 L -30 0 M -30 -25 L 30 -25 L 30 25 L -30 25 Z M 30 0 L 50 0 M -20 -10 L -10 10 M -5 -10 L 5 10 M 10 -10 L 20 10 M -15 15 L 15 15",
        "terminals": {"L_in": [-50, 0], "M_out": [50, 0]}
      },
      "variants": ["MOTOR_STARTER_SD", "MOTOR_STARTER_VFD", "SOFT_STARTER"],
      "annotation_fields": ["rated_kW", "tag"],
      "usage_notes": "Direct-on-line motor starter — composite symbol for contactor + overload relay. Annotate motor rating. Simplest motor control; high inrush current.",
      "related_symbols": ["CONTACTOR_3P", "RELAY_THERMAL", "MOTOR_INDUCTION"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "MOTOR_STARTER_SD",
      "iec_ref": "IEC60617-07-19-04",
      "iec_part": 7,
      "iec_description": "Star-delta motor starter",
      "draftsman_id": "MOTOR_STARTER_SD",
      "category": "switching",
      "display_name": "Star-delta motor starter",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -30, 50, 30],
        "path": "M -50 0 L -30 0 M -30 -25 L 30 -25 L 30 25 L -30 25 Z M 30 0 L 50 0 M -15 -10 L 15 10 M -15 0 L 15 -10 L 15 10 Z M -10 15 L 10 15",
        "terminals": {"L_in": [-50, 0], "M_out": [50, 0]}
      },
      "variants": ["MOTOR_STARTER_DOL", "CONTACTOR_STAR_DELTA"],
      "annotation_fields": ["rated_kW", "transition_time_s"],
      "usage_notes": "Star-delta starter for reduced-inrush motor starting. Suitable for motors > 7.5 kW where DOL inrush is too high. Annotate transition time.",
      "related_symbols": ["MOTOR_STARTER_DOL", "CONTACTOR_STAR_DELTA"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "MOTOR_STARTER_VFD",
      "iec_ref": "IEC60617-07-19-05",
      "iec_part": 7,
      "iec_description": "VFD motor starter",
      "draftsman_id": "MOTOR_STARTER_VFD",
      "category": "switching",
      "display_name": "VFD motor starter",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -30, 50, 30],
        "path": "M -50 0 L -30 0 M -30 -25 L 30 -25 L 30 25 L -30 25 Z M 30 0 L 50 0 M -15 -10 L -10 -10 L -10 0 L -5 0 M 0 0 Q 5 -8 10 0 M 10 -5 L 15 -10",
        "terminals": {"L_in": [-50, 0], "M_out": [50, 0]}
      },
      "variants": ["VFD", "MOTOR_STARTER_DOL"],
      "annotation_fields": ["rated_kW", "speed_range_Hz"],
      "usage_notes": "VFD-based motor starter — soft starting plus variable speed. Standard for HVAC fans, pumps. Annotate speed range.",
      "related_symbols": ["VFD", "MOTOR_STARTER_SD"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "SWITCH_PRESSURE",
      "iec_ref": "IEC60617-07-03-01",
      "iec_part": 7,
      "iec_description": "Pressure-operated switch",
      "draftsman_id": "SWITCH_PRESSURE",
      "category": "switching",
      "display_name": "Pressure switch",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -25, 50, 25],
        "path": "M -50 0 L -15 0 M -15 0 L 12 -18 M 15 0 L 50 0 M 0 -25 L 0 -15 M -8 -20 A 8 8 0 0 0 8 -20",
        "terminals": {"in": [-50, 0], "out": [50, 0]}
      },
      "variants": ["SWITCH_TEMPERATURE", "SWITCH_FLOAT", "SWITCH_LEVEL"],
      "annotation_fields": ["setpoint_bar"],
      "usage_notes": "Pressure-operated switch — dome symbol above the contact represents the pressure sensor. Annotate setpoint.",
      "related_symbols": ["SWITCH_TEMPERATURE", "SWITCH_FLOAT"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "SWITCH_TEMPERATURE",
      "iec_ref": "IEC60617-07-03-02",
      "iec_part": 7,
      "iec_description": "Temperature-operated switch (thermostat)",
      "draftsman_id": "SWITCH_TEMPERATURE",
      "category": "switching",
      "display_name": "Temperature switch (thermostat)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -25, 50, 25],
        "path": "M -50 0 L -15 0 M -15 0 L 12 -18 M 15 0 L 50 0 M 0 -25 L 0 -15 M -5 -25 L -5 -18 L 5 -18 L 5 -25",
        "terminals": {"in": [-50, 0], "out": [50, 0]}
      },
      "variants": ["SWITCH_PRESSURE"],
      "annotation_fields": ["setpoint_C"],
      "usage_notes": "Thermostat — rectangle symbol above the contact represents the temperature sensor. Used for HVAC controls, motor temperature trip.",
      "related_symbols": ["SWITCH_PRESSURE"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "SWITCH_FLOAT",
      "iec_ref": "IEC60617-07-03-03",
      "iec_part": 7,
      "iec_description": "Float (liquid level) switch",
      "draftsman_id": "SWITCH_FLOAT",
      "category": "switching",
      "display_name": "Float switch",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -25, 50, 25],
        "path": "M -50 0 L -15 0 M -15 0 L 12 -18 M 15 0 L 50 0 M 0 -25 L 0 -15 M -10 -25 L 10 -25",
        "terminals": {"in": [-50, 0], "out": [50, 0]}
      },
      "variants": ["SWITCH_LEVEL"],
      "annotation_fields": ["level_position"],
      "usage_notes": "Float switch — bar symbol above the contact represents the float. Used in sump pumps, water tanks.",
      "related_symbols": ["SWITCH_LEVEL"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "SWITCH_LEVEL",
      "iec_ref": "IEC60617-07-03-04",
      "iec_part": 7,
      "iec_description": "Level switch (general)",
      "draftsman_id": "SWITCH_LEVEL",
      "category": "switching",
      "display_name": "Level switch",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -25, 50, 25],
        "path": "M -50 0 L -15 0 M -15 0 L 12 -18 M 15 0 L 50 0 M 0 -25 L 0 -15 M -8 -25 L 8 -25 M -8 -20 L 8 -20",
        "terminals": {"in": [-50, 0], "out": [50, 0]}
      },
      "variants": ["SWITCH_FLOAT"],
      "annotation_fields": ["level_position"],
      "usage_notes": "Level switch — generic (capacitive, ultrasonic, conductive). Distinct from FLOAT which is the mechanical/buoyancy form.",
      "related_symbols": ["SWITCH_FLOAT"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "CIRCUIT_BREAKER_GENERAL",
      "iec_ref": "IEC60617-07-18-00",
      "iec_part": 7,
      "iec_description": "Circuit-breaker (general)",
      "draftsman_id": "CIRCUIT_BREAKER_GENERAL",
      "category": "protection",
      "display_name": "Circuit-breaker (general)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -25, 50, 25],
        "path": "M -50 0 L -20 0 M -20 -25 L 20 -25 L 20 25 L -20 25 Z M -20 0 L 20 0 M 20 0 L 50 0",
        "terminals": {"in": [-50, 0], "out": [50, 0]}
      },
      "variants": ["MCB_1P", "MCCB_3P", "ACB_3P"],
      "annotation_fields": ["In_A", "Icu_kA"],
      "usage_notes": "Generic circuit-breaker box. Use only when device class (MCB/MCCB/ACB) is not yet decided. Otherwise prefer the specific class symbol.",
      "related_symbols": ["MCB_1P", "MCCB_3P", "ACB_3P"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "DISCONNECTOR_GENERAL",
      "iec_ref": "IEC60617-07-14-00",
      "iec_part": 7,
      "iec_description": "Disconnector (general)",
      "draftsman_id": "DISCONNECTOR_GENERAL",
      "category": "switching",
      "display_name": "Disconnector (general)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -20, 50, 20],
        "path": "M -50 0 L -15 0 M -15 0 L 12 -18 M 15 0 L 50 0 M -25 -15 L -5 -15",
        "terminals": {"in": [-50, 0], "out": [50, 0]}
      },
      "variants": ["ISOLATOR_2P", "ISOLATOR_3P", "ISOLATOR_4P"],
      "annotation_fields": ["rated_A"],
      "usage_notes": "Generic single-pole disconnector. Used when pole count is not yet fixed. Horizontal bar indicates 'no load' (isolator) operation.",
      "related_symbols": ["ISOLATOR_2P", "ISOLATOR_3P"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "CONTACTOR_GENERAL",
      "iec_ref": "IEC60617-07-19-00",
      "iec_part": 7,
      "iec_description": "Contactor (general)",
      "draftsman_id": "CONTACTOR_GENERAL",
      "category": "switching",
      "display_name": "Contactor (general)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -25, 50, 25],
        "path": "M -50 0 L -15 0 M -15 0 L 12 -18 M 15 0 L 50 0 M -20 -22 A 5 5 0 1 0 -10 -22 A 5 5 0 1 0 -20 -22 Z",
        "terminals": {"in": [-50, 0], "out": [50, 0]}
      },
      "variants": ["CONTACTOR_3P"],
      "annotation_fields": ["AC_rating_A", "tag"],
      "usage_notes": "Generic single-pole contactor. The small circle indicates the spring-return / power-operated behaviour (distinct from a manual switch).",
      "related_symbols": ["CONTACTOR_3P", "RELAY_COIL"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "RELAY_GENERAL",
      "iec_ref": "IEC60617-07-15-00",
      "iec_part": 7,
      "iec_description": "Relay (general)",
      "draftsman_id": "RELAY_GENERAL",
      "category": "switching",
      "display_name": "Relay (general)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -15, 50, 15],
        "path": "M -50 0 L -20 0 M -20 -15 L 20 -15 L 20 15 L -20 15 Z M 20 0 L 50 0",
        "terminals": {"in": [-50, 0], "out": [50, 0]}
      },
      "variants": ["RELAY_COIL", "RELAY_OVERCURRENT", "RELAY_THERMAL"],
      "annotation_fields": ["function", "tag"],
      "usage_notes": "Generic relay symbol — rectangle without specific function marking. Annotate function (overcurrent, undervoltage, etc.).",
      "related_symbols": ["RELAY_COIL", "RELAY_OVERCURRENT"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "SWITCH_ISOLATING",
      "iec_ref": "IEC60617-07-02-03",
      "iec_part": 7,
      "iec_description": "Switch suitable for isolation",
      "draftsman_id": "SWITCH_ISOLATING",
      "category": "switching",
      "display_name": "Isolating switch",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -20, 50, 20],
        "path": "M -50 0 L -15 0 M -15 0 L 12 -18 M 15 0 L 50 0 M -25 -15 L 25 -15",
        "terminals": {"in": [-50, 0], "out": [50, 0]}
      },
      "variants": ["SWITCH_GENERAL", "ISOLATOR_2P"],
      "annotation_fields": ["rated_A"],
      "usage_notes": "Switch certified for isolation duty (e.g. MAINS marked). Long horizontal bar over the contact indicates the isolation rating. Used as functional switch + isolator.",
      "related_symbols": ["SWITCH_GENERAL", "ISOLATOR_2P"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "LINK_REMOVABLE",
      "iec_ref": "IEC60617-07-04-01",
      "iec_part": 7,
      "iec_description": "Removable link / bolted link",
      "draftsman_id": "LINK_REMOVABLE",
      "category": "switching",
      "display_name": "Removable link",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -10, 50, 10],
        "path": "M -50 0 L -15 0 M -15 0 L 15 0 M 15 0 L 50 0 M -15 -10 A 5 5 0 1 0 -15 0 M 15 -10 A 5 5 0 1 0 15 0",
        "terminals": {"a": [-50, 0], "b": [50, 0]}
      },
      "variants": [],
      "annotation_fields": [],
      "usage_notes": "Bolted/removable link — a non-switching connection that can be unbolted for maintenance. Two terminals connected by a bar with knobs. Used on PE-N links in TN-C-S systems.",
      "related_symbols": ["DISCONNECTOR_GENERAL"],
      "generating_shared_symbol": true
    }
  ]
}
```

- [ ] **Step 2: Validate JSON syntax**

Run: `python3 -c "import json; json.load(open('shared/standards/electrical/IEC60617/part7-switchgear.json'))" && echo OK`
Expected: `OK`

- [ ] **Step 3: Verify symbol count**

Run: `python3 -c "import json; print(len(json.load(open('shared/standards/electrical/IEC60617/part7-switchgear.json'))['symbols']))"`
Expected: `70`

- [ ] **Step 4: Verify all schema fields present**

Run: `python3 -c "import json; data=json.load(open('shared/standards/electrical/IEC60617/part7-switchgear.json')); req=['symbol_id','iec_ref','iec_part','iec_description','draftsman_id','category','display_name','geometry','variants','annotation_fields','usage_notes','related_symbols','generating_shared_symbol']; missing=[(s.get('symbol_id','?'), [f for f in req if f not in s]) for s in data['symbols'] if any(f not in s for f in req)]; print('OK' if not missing else 'MISSING:'+str(missing))"`
Expected: `OK`

- [ ] **Step 5: Commit**

```bash
git add shared/standards/electrical/IEC60617/part7-switchgear.json
git commit -m "feat: IEC60617 part7-switchgear.json — 70 switchgear and protection symbols"
```

---

## Task 10: Create part8-measurement.json (~30 symbols)

**Files:**
- Create: `shared/standards/electrical/IEC60617/part8-measurement.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "IEC 60617 Part 8 — Measuring instruments, lamps and signalling devices",
  "_iec_part": 8,
  "_version": "1.0.0",
  "symbols": [
    {
      "symbol_id": "AMMETER",
      "iec_ref": "IEC60617-08-01-01",
      "iec_part": 8,
      "iec_description": "Ammeter",
      "draftsman_id": "AMMETER",
      "category": "measurement",
      "display_name": "Ammeter",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -30, 50, 30],
        "path": "M -50 0 L -30 0 M 30 0 A 30 30 0 1 0 -30 0 A 30 30 0 1 0 30 0 Z M 30 0 L 50 0",
        "terminals": {"in": [-50, 0], "out": [50, 0]}
      },
      "variants": ["VOLTMETER", "WATTMETER"],
      "annotation_fields": ["range_A", "class", "label_A"],
      "usage_notes": "Ammeter — circle labelled 'A'. Annotate full-scale range and class. Used at outgoing circuit metering, motor control centres. Wired through CT for currents above 10A.",
      "related_symbols": ["VOLTMETER", "TRANSFORMER_CURRENT"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "VOLTMETER",
      "iec_ref": "IEC60617-08-01-02",
      "iec_part": 8,
      "iec_description": "Voltmeter",
      "draftsman_id": "VOLTMETER",
      "category": "measurement",
      "display_name": "Voltmeter",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -30, 50, 30],
        "path": "M -50 0 L -30 0 M 30 0 A 30 30 0 1 0 -30 0 A 30 30 0 1 0 30 0 Z M 30 0 L 50 0",
        "terminals": {"in": [-50, 0], "out": [50, 0]}
      },
      "variants": ["AMMETER", "WATTMETER"],
      "annotation_fields": ["range_V", "class", "label_V"],
      "usage_notes": "Voltmeter — circle labelled 'V'. Connected line-to-line or line-to-neutral.",
      "related_symbols": ["AMMETER", "TRANSFORMER_VOLTAGE"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "WATTMETER",
      "iec_ref": "IEC60617-08-01-03",
      "iec_part": 8,
      "iec_description": "Wattmeter",
      "draftsman_id": "WATTMETER",
      "category": "measurement",
      "display_name": "Wattmeter",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -30, 50, 30],
        "path": "M -50 0 L -30 0 M 30 0 A 30 30 0 1 0 -30 0 A 30 30 0 1 0 30 0 Z M 30 0 L 50 0",
        "terminals": {"in": [-50, 0], "out": [50, 0]}
      },
      "variants": ["VAR_METER", "AMMETER", "VOLTMETER"],
      "annotation_fields": ["range_W", "class", "label_W"],
      "usage_notes": "Wattmeter — circle labelled 'W'. Measures active power; requires both current and voltage inputs.",
      "related_symbols": ["VAR_METER", "ENERGY_METER_KWH"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "VAR_METER",
      "iec_ref": "IEC60617-08-01-04",
      "iec_part": 8,
      "iec_description": "Var-meter (reactive power)",
      "draftsman_id": "VAR_METER",
      "category": "measurement",
      "display_name": "VAR meter",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -30, 50, 30],
        "path": "M -50 0 L -30 0 M 30 0 A 30 30 0 1 0 -30 0 A 30 30 0 1 0 30 0 Z M 30 0 L 50 0",
        "terminals": {"in": [-50, 0], "out": [50, 0]}
      },
      "variants": ["WATTMETER", "POWER_FACTOR_METER"],
      "annotation_fields": ["range_VAr", "class", "label_VAr"],
      "usage_notes": "Reactive power meter — circle labelled 'var'. Used at PFC installations to verify reactive load.",
      "related_symbols": ["WATTMETER", "POWER_FACTOR_METER", "CAPACITOR_BANK"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "POWER_FACTOR_METER",
      "iec_ref": "IEC60617-08-01-05",
      "iec_part": 8,
      "iec_description": "Power factor meter",
      "draftsman_id": "POWER_FACTOR_METER",
      "category": "measurement",
      "display_name": "Power factor meter",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -30, 50, 30],
        "path": "M -50 0 L -30 0 M 30 0 A 30 30 0 1 0 -30 0 A 30 30 0 1 0 30 0 Z M 30 0 L 50 0",
        "terminals": {"in": [-50, 0], "out": [50, 0]}
      },
      "variants": ["VAR_METER"],
      "annotation_fields": ["range", "class", "label_cosphi"],
      "usage_notes": "Power factor meter — circle labelled 'cos φ' or 'PF'. Used at PFC, large motor circuits.",
      "related_symbols": ["VAR_METER", "WATTMETER"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "FREQUENCY_METER",
      "iec_ref": "IEC60617-08-01-06",
      "iec_part": 8,
      "iec_description": "Frequency meter",
      "draftsman_id": "FREQUENCY_METER",
      "category": "measurement",
      "display_name": "Frequency meter",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -30, 50, 30],
        "path": "M -50 0 L -30 0 M 30 0 A 30 30 0 1 0 -30 0 A 30 30 0 1 0 30 0 Z M 30 0 L 50 0",
        "terminals": {"in": [-50, 0], "out": [50, 0]}
      },
      "variants": [],
      "annotation_fields": ["range_Hz", "class", "label_Hz"],
      "usage_notes": "Frequency meter — circle labelled 'Hz'. Used at generator synchronising panels.",
      "related_symbols": ["VOLTMETER"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "ENERGY_METER_KWH",
      "iec_ref": "IEC60617-08-02-01",
      "iec_part": 8,
      "iec_description": "Energy meter (kWh)",
      "draftsman_id": "ENERGY_METER_KWH",
      "category": "measurement",
      "display_name": "Energy meter (kWh)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -25, 50, 25],
        "path": "M -50 0 L -25 0 M -25 -20 L 25 -20 L 25 20 L -25 20 Z M 25 0 L 50 0 M -10 -8 L 10 -8 M -10 0 L 10 0 M -10 8 L 10 8",
        "terminals": {"in": [-50, 0], "out": [50, 0]}
      },
      "variants": ["ENERGY_METER_KVARH", "SMART_METER"],
      "annotation_fields": ["rating_A", "ratio_CT", "label_kWh"],
      "usage_notes": "Active energy meter (kWh) — rectangle with internal register marks. Annotate kWh and CT ratio if used. Required at every billing point.",
      "related_symbols": ["ENERGY_METER_KVARH", "SMART_METER", "WATTMETER"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "ENERGY_METER_KVARH",
      "iec_ref": "IEC60617-08-02-02",
      "iec_part": 8,
      "iec_description": "Reactive energy meter (kVArh)",
      "draftsman_id": "ENERGY_METER_KVARH",
      "category": "measurement",
      "display_name": "Reactive energy meter (kVArh)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -25, 50, 25],
        "path": "M -50 0 L -25 0 M -25 -20 L 25 -20 L 25 20 L -25 20 Z M 25 0 L 50 0 M -10 -8 L 10 -8 M -10 0 L 10 0 M -10 8 L 10 8 M -15 -15 L -10 -15",
        "terminals": {"in": [-50, 0], "out": [50, 0]}
      },
      "variants": ["ENERGY_METER_KWH"],
      "annotation_fields": ["rating_A", "ratio_CT", "label_kVArh"],
      "usage_notes": "Reactive energy meter — used at billing points where the utility charges for reactive consumption (typically commercial/industrial above a kVA threshold).",
      "related_symbols": ["ENERGY_METER_KWH", "VAR_METER"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "SMART_METER",
      "iec_ref": "IEC60617-08-02-03",
      "iec_part": 8,
      "iec_description": "Smart / AMR energy meter",
      "draftsman_id": "SMART_METER",
      "category": "measurement",
      "display_name": "Smart meter (AMR)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -25, 50, 25],
        "path": "M -50 0 L -25 0 M -25 -20 L 25 -20 L 25 20 L -25 20 Z M 25 0 L 50 0 M -10 -8 L 10 -8 M -10 0 L 10 0 M -10 8 L 10 8 M 20 -25 L 30 -15 M 25 -25 L 35 -15",
        "terminals": {"in": [-50, 0], "out": [50, 0], "comms": [25, -25]}
      },
      "variants": ["ENERGY_METER_KWH", "MULTIFUNCTION_METER"],
      "annotation_fields": ["rating_A", "comms_protocol"],
      "usage_notes": "Smart meter / automatic meter reader — energy meter with comms link (antenna marks). Annotate comms protocol (Modbus, BACnet, M-Bus, RF).",
      "related_symbols": ["ENERGY_METER_KWH", "MULTIFUNCTION_METER"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "CT_METERING",
      "iec_ref": "IEC60617-08-03-01",
      "iec_part": 8,
      "iec_description": "Current transformer for metering",
      "draftsman_id": "CT_METERING",
      "category": "measurement",
      "display_name": "CT (metering class)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -25, 50, 25],
        "path": "M -50 0 L 50 0 M 0 25 A 25 25 0 1 0 0 -25 M 0 -25 A 8 8 0 1 0 -16 -25 M -16 -25 L -16 25 M 0 25 A 8 8 0 1 0 -16 25",
        "terminals": {"primary_in": [-50, 0], "primary_out": [50, 0], "S1": [-16, -25], "S2": [-16, 25]}
      },
      "variants": ["TRANSFORMER_CURRENT", "VT_METERING"],
      "annotation_fields": ["ratio", "class", "burden_VA"],
      "usage_notes": "Metering-class CT — same form as TRANSFORMER_CURRENT but with metering accuracy class (0.2, 0.5). Used for revenue metering and instrumentation.",
      "related_symbols": ["TRANSFORMER_CURRENT", "AMMETER", "ENERGY_METER_KWH"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "VT_METERING",
      "iec_ref": "IEC60617-08-03-02",
      "iec_part": 8,
      "iec_description": "Voltage transformer for metering",
      "draftsman_id": "VT_METERING",
      "category": "measurement",
      "display_name": "VT (metering class)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -30, 50, 30],
        "path": "M -50 0 L -25 0 M 5 0 A 20 20 0 1 0 -25 0 A 20 20 0 1 0 5 0 Z M 25 0 A 20 20 0 1 0 -5 0 A 20 20 0 1 0 25 0 Z M 25 0 L 50 0 M -15 -20 L 15 -20",
        "terminals": {"hv_a": [-50, 0], "hv_b": [50, 0], "lv_a": [-15, -20], "lv_b": [15, -20]}
      },
      "variants": ["TRANSFORMER_VOLTAGE", "CT_METERING"],
      "annotation_fields": ["ratio", "class", "burden_VA"],
      "usage_notes": "Metering-class VT — same form as TRANSFORMER_VOLTAGE with measurement accuracy class. Used in revenue metering chains.",
      "related_symbols": ["TRANSFORMER_VOLTAGE", "VOLTMETER"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "MULTIFUNCTION_METER",
      "iec_ref": "IEC60617-08-02-04",
      "iec_part": 8,
      "iec_description": "Multifunction metering device",
      "draftsman_id": "MULTIFUNCTION_METER",
      "category": "measurement",
      "display_name": "Multifunction meter",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -25, 50, 25],
        "path": "M -50 0 L -25 0 M -25 -20 L 25 -20 L 25 20 L -25 20 Z M 25 0 L 50 0 M -15 -10 L 15 -10 M -15 0 L 15 0 M -15 10 L 15 10",
        "terminals": {"in": [-50, 0], "out": [50, 0], "comms": [25, -25]}
      },
      "variants": ["SMART_METER", "ENERGY_METER_KWH"],
      "annotation_fields": ["rating_A", "functions", "comms_protocol"],
      "usage_notes": "Multifunction meter — V, I, kW, kVAr, kWh, PF, frequency in one device. Common at MSB incomer for power quality monitoring.",
      "related_symbols": ["SMART_METER", "ENERGY_METER_KWH", "POWER_ANALYSER"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "INDICATOR_LAMP",
      "iec_ref": "IEC60617-08-04-01",
      "iec_part": 8,
      "iec_description": "Lamp (indicator)",
      "draftsman_id": "INDICATOR_LAMP",
      "category": "measurement",
      "display_name": "Indicator lamp",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -20, 50, 20],
        "path": "M -50 0 L -15 0 M 15 0 A 15 15 0 1 0 -15 0 A 15 15 0 1 0 15 0 Z M 15 0 L 50 0 M -10 -10 L 10 10 M 10 -10 L -10 10",
        "terminals": {"a": [-50, 0], "b": [50, 0]}
      },
      "variants": ["INDICATOR_LAMP_R", "INDICATOR_LAMP_G", "INDICATOR_LAMP_A", "LED_INDICATOR"],
      "annotation_fields": ["voltage_V", "colour", "function"],
      "usage_notes": "Indicator lamp — circle with internal X. Used to signal supply present, equipment status. Annotate voltage and colour. Colour-specific variants below.",
      "related_symbols": ["INDICATOR_LAMP_R", "INDICATOR_LAMP_G", "PUSHBUTTON_ILLUMINATED"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "INDICATOR_LAMP_R",
      "iec_ref": "IEC60617-08-04-02",
      "iec_part": 8,
      "iec_description": "Red indicator lamp",
      "draftsman_id": "INDICATOR_LAMP_R",
      "category": "measurement",
      "display_name": "Indicator lamp (red)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -20, 50, 20],
        "path": "M -50 0 L -15 0 M 15 0 A 15 15 0 1 0 -15 0 A 15 15 0 1 0 15 0 Z M 15 0 L 50 0 M -10 -10 L 10 10 M 10 -10 L -10 10",
        "terminals": {"a": [-50, 0], "b": [50, 0]}
      },
      "variants": ["INDICATOR_LAMP", "INDICATOR_LAMP_G", "INDICATOR_LAMP_A"],
      "annotation_fields": ["voltage_V", "function", "label_R"],
      "usage_notes": "Red indicator lamp — convention: trip/fault/danger. Annotate function (e.g. 'CB tripped', 'Fault').",
      "related_symbols": ["INDICATOR_LAMP_G", "INDICATOR_LAMP_A"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "INDICATOR_LAMP_G",
      "iec_ref": "IEC60617-08-04-03",
      "iec_part": 8,
      "iec_description": "Green indicator lamp",
      "draftsman_id": "INDICATOR_LAMP_G",
      "category": "measurement",
      "display_name": "Indicator lamp (green)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -20, 50, 20],
        "path": "M -50 0 L -15 0 M 15 0 A 15 15 0 1 0 -15 0 A 15 15 0 1 0 15 0 Z M 15 0 L 50 0 M -10 -10 L 10 10 M 10 -10 L -10 10",
        "terminals": {"a": [-50, 0], "b": [50, 0]}
      },
      "variants": ["INDICATOR_LAMP", "INDICATOR_LAMP_R", "INDICATOR_LAMP_A"],
      "annotation_fields": ["voltage_V", "function", "label_G"],
      "usage_notes": "Green indicator lamp — convention: ready/normal/safe. Annotate function (e.g. 'Ready', 'Running').",
      "related_symbols": ["INDICATOR_LAMP_R", "INDICATOR_LAMP_A"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "INDICATOR_LAMP_A",
      "iec_ref": "IEC60617-08-04-04",
      "iec_part": 8,
      "iec_description": "Amber / yellow indicator lamp",
      "draftsman_id": "INDICATOR_LAMP_A",
      "category": "measurement",
      "display_name": "Indicator lamp (amber)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -20, 50, 20],
        "path": "M -50 0 L -15 0 M 15 0 A 15 15 0 1 0 -15 0 A 15 15 0 1 0 15 0 Z M 15 0 L 50 0 M -10 -10 L 10 10 M 10 -10 L -10 10",
        "terminals": {"a": [-50, 0], "b": [50, 0]}
      },
      "variants": ["INDICATOR_LAMP_R", "INDICATOR_LAMP_G"],
      "annotation_fields": ["voltage_V", "function", "label_A"],
      "usage_notes": "Amber/yellow indicator lamp — convention: warning/caution/maintenance. Annotate function.",
      "related_symbols": ["INDICATOR_LAMP_R", "INDICATOR_LAMP_G"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "LED_INDICATOR",
      "iec_ref": "IEC60617-08-04-05",
      "iec_part": 8,
      "iec_description": "Light-emitting diode (LED) indicator",
      "draftsman_id": "LED_INDICATOR",
      "category": "measurement",
      "display_name": "LED indicator",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -20, 50, 20],
        "path": "M -50 0 L -15 0 M 15 0 A 15 15 0 1 0 -15 0 A 15 15 0 1 0 15 0 Z M 15 0 L 50 0 M -10 -10 L 10 10 M 10 -10 L -10 10 M 18 -15 L 25 -22 M 22 -22 L 25 -22 L 25 -19",
        "terminals": {"anode": [-50, 0], "cathode": [50, 0]}
      },
      "variants": ["INDICATOR_LAMP"],
      "annotation_fields": ["voltage_V", "colour"],
      "usage_notes": "LED indicator — like INDICATOR_LAMP with two angled arrows indicating light emission. Replacement for incandescent indicator lamps in modern installations.",
      "related_symbols": ["INDICATOR_LAMP"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "BUZZER",
      "iec_ref": "IEC60617-08-05-01",
      "iec_part": 8,
      "iec_description": "Buzzer",
      "draftsman_id": "BUZZER",
      "category": "measurement",
      "display_name": "Buzzer",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -20, 50, 20],
        "path": "M -50 0 L -20 0 M -20 -20 A 20 20 0 0 1 20 -20 L 20 20 A 20 20 0 0 1 -20 20 Z M 20 0 L 50 0",
        "terminals": {"a": [-50, 0], "b": [50, 0]}
      },
      "variants": ["HORN", "BELL", "ALARM_AUDIBLE"],
      "annotation_fields": ["voltage_V", "dB"],
      "usage_notes": "Buzzer — semicircle outline. Used for low-volume audible signalling (panel alarms, doorbells). Distinct from HORN (louder).",
      "related_symbols": ["HORN", "BELL"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "HORN",
      "iec_ref": "IEC60617-08-05-02",
      "iec_part": 8,
      "iec_description": "Horn / siren",
      "draftsman_id": "HORN",
      "category": "measurement",
      "display_name": "Horn / siren",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -20, 50, 20],
        "path": "M -50 0 L -20 0 M -20 -15 L 0 -15 L 25 -5 L 25 5 L 0 15 L -20 15 Z M 25 0 L 50 0",
        "terminals": {"a": [-50, 0], "b": [50, 0]}
      },
      "variants": ["BUZZER", "BELL", "ALARM_AUDIBLE"],
      "annotation_fields": ["voltage_V", "dB"],
      "usage_notes": "Horn / siren — trumpet-shaped outline. Used for high-volume audible signalling (fire alarm sounders, evacuation).",
      "related_symbols": ["BUZZER", "BELL", "ALARM_AUDIBLE"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "BELL",
      "iec_ref": "IEC60617-08-05-03",
      "iec_part": 8,
      "iec_description": "Bell",
      "draftsman_id": "BELL",
      "category": "measurement",
      "display_name": "Bell",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -25, 50, 20],
        "path": "M -50 0 L -20 0 M -20 0 A 20 20 0 0 1 20 0 L 20 5 L -20 5 Z M 20 0 L 50 0 M 0 -25 L 0 -20",
        "terminals": {"a": [-50, 0], "b": [50, 0]}
      },
      "variants": ["BUZZER", "HORN"],
      "annotation_fields": ["voltage_V", "dB"],
      "usage_notes": "Bell — semicircle (bell-shape) outline. Used for traditional alarm bells. Less common in modern installations than horns.",
      "related_symbols": ["BUZZER", "HORN"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "ALARM_AUDIBLE",
      "iec_ref": "IEC60617-08-05-04",
      "iec_part": 8,
      "iec_description": "Audible alarm (general)",
      "draftsman_id": "ALARM_AUDIBLE",
      "category": "measurement",
      "display_name": "Audible alarm",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -20, 50, 20],
        "path": "M -50 0 L -20 0 M -20 -15 L 0 -15 L 25 -5 L 25 5 L 0 15 L -20 15 Z M 25 0 L 50 0 M 30 -10 L 35 -15 M 30 0 L 40 0 M 30 10 L 35 15",
        "terminals": {"a": [-50, 0], "b": [50, 0]}
      },
      "variants": ["HORN", "BUZZER", "BELL"],
      "annotation_fields": ["voltage_V", "dB"],
      "usage_notes": "Generic audible alarm — horn with sound-wave indicator. Use when device type is not yet specified.",
      "related_symbols": ["HORN", "ALARM_VISUAL"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "ALARM_VISUAL",
      "iec_ref": "IEC60617-08-05-05",
      "iec_part": 8,
      "iec_description": "Visual alarm (strobe / xenon flasher)",
      "draftsman_id": "ALARM_VISUAL",
      "category": "measurement",
      "display_name": "Visual alarm (strobe)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -20, 50, 25],
        "path": "M -50 0 L -15 0 M 15 0 A 15 15 0 1 0 -15 0 A 15 15 0 1 0 15 0 Z M 15 0 L 50 0 M 0 -25 L -10 -10 L 10 -5 L 0 10 L 5 5",
        "terminals": {"a": [-50, 0], "b": [50, 0]}
      },
      "variants": ["INDICATOR_LAMP"],
      "annotation_fields": ["voltage_V", "candela", "colour"],
      "usage_notes": "Strobe / visual alarm — lamp circle with lightning-bolt indicator. Used in fire alarm and emergency systems. Annotate candela rating per EN 54-23.",
      "related_symbols": ["INDICATOR_LAMP", "ALARM_AUDIBLE"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "LUMINAIRE_GENERAL",
      "iec_ref": "IEC60617-08-04-10",
      "iec_part": 8,
      "iec_description": "Luminaire (general)",
      "draftsman_id": "LUMINAIRE_GENERAL",
      "category": "measurement",
      "display_name": "Luminaire (general)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -25, 50, 25],
        "path": "M -50 0 L -20 0 M 20 0 A 20 20 0 1 0 -20 0 A 20 20 0 1 0 20 0 Z M 20 0 L 50 0 M -14 -14 L 14 14 M 14 -14 L -14 14",
        "terminals": {"a": [-50, 0], "b": [50, 0]}
      },
      "variants": ["LUMINAIRE_ARCH", "LUMINAIRE_EMERGENCY"],
      "annotation_fields": ["voltage_V", "wattage_W"],
      "usage_notes": "Luminaire — circle with internal X. The schematic-side luminaire symbol. For architectural-plan luminaire, see LUMINAIRE_ARCH (Part 11).",
      "related_symbols": ["LUMINAIRE_ARCH", "INDICATOR_LAMP"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "OSCILLOSCOPE",
      "iec_ref": "IEC60617-08-06-01",
      "iec_part": 8,
      "iec_description": "Oscilloscope",
      "draftsman_id": "OSCILLOSCOPE",
      "category": "measurement",
      "display_name": "Oscilloscope",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -30, 50, 30],
        "path": "M -50 0 L -30 0 M 30 0 A 30 30 0 1 0 -30 0 A 30 30 0 1 0 30 0 Z M 30 0 L 50 0 M -20 5 Q -10 -15 0 5 Q 10 25 20 -5",
        "terminals": {"signal": [-50, 0], "trig": [50, 0]}
      },
      "variants": ["POWER_ANALYSER", "RECORDER"],
      "annotation_fields": ["bandwidth_MHz", "label"],
      "usage_notes": "Oscilloscope — circle with sine-wave trace. Used on test equipment racks, calibration benches. Rare in MEP building electrical.",
      "related_symbols": ["POWER_ANALYSER"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "POWER_ANALYSER",
      "iec_ref": "IEC60617-08-06-02",
      "iec_part": 8,
      "iec_description": "Power quality analyser",
      "draftsman_id": "POWER_ANALYSER",
      "category": "measurement",
      "display_name": "Power quality analyser",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -25, 50, 25],
        "path": "M -50 0 L -25 0 M -25 -20 L 25 -20 L 25 20 L -25 20 Z M 25 0 L 50 0 M -15 -5 L -5 5 L 5 -10 L 15 0 M -15 10 L 15 10",
        "terminals": {"in": [-50, 0], "out": [50, 0], "comms": [25, -25]}
      },
      "variants": ["MULTIFUNCTION_METER", "OSCILLOSCOPE", "RECORDER"],
      "annotation_fields": ["functions", "comms_protocol"],
      "usage_notes": "Power quality analyser — rectangle with waveform indicator. Measures harmonics, transients, flicker. Used at incomer of critical loads.",
      "related_symbols": ["MULTIFUNCTION_METER", "RECORDER"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "SIGNAL_GENERATOR",
      "iec_ref": "IEC60617-08-06-03",
      "iec_part": 8,
      "iec_description": "Signal generator (test)",
      "draftsman_id": "SIGNAL_GENERATOR",
      "category": "measurement",
      "display_name": "Signal generator",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -30, 50, 30],
        "path": "M -50 0 L -30 0 M 30 0 A 30 30 0 1 0 -30 0 A 30 30 0 1 0 30 0 Z M 30 0 L 50 0 M -15 0 Q -8 -10 0 0 Q 8 10 15 0",
        "terminals": {"out": [50, 0], "ref": [-50, 0]}
      },
      "variants": ["OSCILLOSCOPE"],
      "annotation_fields": ["frequency_Hz", "amplitude_V"],
      "usage_notes": "Signal generator for test bench / calibration. Circle with sine-wave indicator. Out of normal MEP scope but included for completeness on test panels.",
      "related_symbols": ["OSCILLOSCOPE"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "TRANSDUCER_CURRENT",
      "iec_ref": "IEC60617-08-07-01",
      "iec_part": 8,
      "iec_description": "Current transducer (4-20mA output)",
      "draftsman_id": "TRANSDUCER_CURRENT",
      "category": "measurement",
      "display_name": "Current transducer",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -20, 50, 25],
        "path": "M -50 0 L -20 0 M -20 -15 L 20 -15 L 20 15 L -20 15 Z M 20 0 L 50 0 M 0 15 L 0 25 M -5 5 L 5 5 M -10 -5 L 10 -5",
        "terminals": {"in": [-50, 0], "out": [50, 0], "signal": [0, 25]}
      },
      "variants": ["TRANSDUCER_VOLTAGE", "CT_METERING"],
      "annotation_fields": ["input_A", "output_signal"],
      "usage_notes": "Current transducer — converts AC current to a 4-20mA or 0-10V signal for BMS or PLC. Annotate input range and output signal type.",
      "related_symbols": ["TRANSDUCER_VOLTAGE", "CT_METERING"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "TRANSDUCER_VOLTAGE",
      "iec_ref": "IEC60617-08-07-02",
      "iec_part": 8,
      "iec_description": "Voltage transducer (4-20mA output)",
      "draftsman_id": "TRANSDUCER_VOLTAGE",
      "category": "measurement",
      "display_name": "Voltage transducer",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -20, 50, 25],
        "path": "M -50 0 L -20 0 M -20 -15 L 20 -15 L 20 15 L -20 15 Z M 20 0 L 50 0 M 0 15 L 0 25 M -10 -5 L 10 -5 M -5 5 L 5 5 M -5 -8 L -5 -2 M 5 -8 L 5 -2",
        "terminals": {"in": [-50, 0], "out": [50, 0], "signal": [0, 25]}
      },
      "variants": ["TRANSDUCER_CURRENT"],
      "annotation_fields": ["input_V", "output_signal"],
      "usage_notes": "Voltage transducer — AC voltage to analogue signal converter. Used for BMS feedback.",
      "related_symbols": ["TRANSDUCER_CURRENT", "VT_METERING"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "RECORDER",
      "iec_ref": "IEC60617-08-06-04",
      "iec_part": 8,
      "iec_description": "Recorder (chart / data)",
      "draftsman_id": "RECORDER",
      "category": "measurement",
      "display_name": "Recorder",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -25, 50, 25],
        "path": "M -50 0 L -25 0 M -25 -20 L 25 -20 L 25 20 L -25 20 Z M 25 0 L 50 0 M -15 5 L -5 -10 L 5 5 L 15 -5",
        "terminals": {"in": [-50, 0], "out": [50, 0]}
      },
      "variants": ["POWER_ANALYSER"],
      "annotation_fields": ["channels", "memory_days"],
      "usage_notes": "Recorder — rectangle with waveform indicator. Used for long-term load profile recording, generator test data.",
      "related_symbols": ["POWER_ANALYSER"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "TOTALISER",
      "iec_ref": "IEC60617-08-02-05",
      "iec_part": 8,
      "iec_description": "Totaliser / integrator",
      "draftsman_id": "TOTALISER",
      "category": "measurement",
      "display_name": "Totaliser",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -25, 50, 25],
        "path": "M -50 0 L -25 0 M -25 -20 L 25 -20 L 25 20 L -25 20 Z M 25 0 L 50 0 M -10 -8 L 10 -8 M -10 0 L 10 0 M -10 8 L 10 8 M -15 -15 L 15 -15",
        "terminals": {"in": [-50, 0], "out": [50, 0]}
      },
      "variants": ["ENERGY_METER_KWH"],
      "annotation_fields": ["quantity", "units"],
      "usage_notes": "Totaliser — generic integrating counter (e.g. running hours meter, kWh totaliser). Distinct from ENERGY_METER_KWH which has the explicit kWh function.",
      "related_symbols": ["ENERGY_METER_KWH"],
      "generating_shared_symbol": true
    }
  ]
}
```

- [ ] **Step 2: Validate JSON syntax**

Run: `python3 -c "import json; json.load(open('shared/standards/electrical/IEC60617/part8-measurement.json'))" && echo OK`
Expected: `OK`

- [ ] **Step 3: Verify symbol count**

Run: `python3 -c "import json; print(len(json.load(open('shared/standards/electrical/IEC60617/part8-measurement.json'))['symbols']))"`
Expected: `30`

- [ ] **Step 4: Verify all schema fields present**

Run: `python3 -c "import json; data=json.load(open('shared/standards/electrical/IEC60617/part8-measurement.json')); req=['symbol_id','iec_ref','iec_part','iec_description','draftsman_id','category','display_name','geometry','variants','annotation_fields','usage_notes','related_symbols','generating_shared_symbol']; missing=[(s.get('symbol_id','?'), [f for f in req if f not in s]) for s in data['symbols'] if any(f not in s for f in req)]; print('OK' if not missing else 'MISSING:'+str(missing))"`
Expected: `OK`

- [ ] **Step 5: Commit**

```bash
git add shared/standards/electrical/IEC60617/part8-measurement.json
git commit -m "feat: IEC60617 part8-measurement.json — 30 measurement and signalling symbols"
```

---

## Task 11: Create part11-architectural.json (~36 symbols)

**Files:**
- Create: `shared/standards/electrical/IEC60617/part11-architectural.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "IEC 60617 Part 11 — Architectural and topographical installation plans and diagrams",
  "_iec_part": 11,
  "_version": "1.0.0",
  "_note": "Part 11 symbols are plan-view (top-down) representations used on architectural floor plans, not schematic line-diagrams. Terminals are notional (cable entry points) rather than electrical schematic terminals.",
  "symbols": [
    {
      "symbol_id": "DB_GENERAL",
      "iec_ref": "IEC60617-11-04-01",
      "iec_part": 11,
      "iec_description": "Distribution board (general)",
      "draftsman_id": "DB_GENERAL",
      "category": "architectural",
      "display_name": "Distribution board (general)",
      "geometry": {
        "grid": 100,
        "bbox": [-30, -20, 30, 20],
        "path": "M -30 -20 L 30 -20 L 30 20 L -30 20 Z M -30 0 L 30 0",
        "terminals": {"cable_entry": [0, 20]}
      },
      "variants": ["DB_MAIN", "DB_SUB", "CONSUMER_UNIT"],
      "annotation_fields": ["board_id", "rated_A", "ip_rating"],
      "usage_notes": "Generic distribution board — rectangle with horizontal divider line. Annotate board ID and rating.",
      "related_symbols": ["DB_MAIN", "DB_SUB", "CONSUMER_UNIT"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "DB_MAIN",
      "iec_ref": "IEC60617-11-04-02",
      "iec_part": 11,
      "iec_description": "Main distribution board / main switchboard",
      "draftsman_id": "DB_MAIN",
      "category": "architectural",
      "display_name": "Main LV switchboard (MSB)",
      "geometry": {
        "grid": 100,
        "bbox": [-40, -25, 40, 25],
        "path": "M -40 -25 L 40 -25 L 40 25 L -40 25 Z M -40 0 L 40 0 M -40 -12 L 40 -12 M -40 12 L 40 12",
        "terminals": {"incoming": [-40, 0], "outgoing_1": [40, -12], "outgoing_2": [40, 0], "outgoing_3": [40, 12]}
      },
      "variants": ["DB_GENERAL", "DB_SUB"],
      "annotation_fields": ["board_id", "rated_A", "Icw_kA", "form_separation"],
      "usage_notes": "Main LV switchboard — larger rectangle with multiple horizontal dividers indicating busbar and panel sections. Annotate form separation (Form 2/3/4 to IEC 61439-2).",
      "related_symbols": ["DB_GENERAL", "DB_SUB", "ACB_3P"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "CONSUMER_UNIT",
      "iec_ref": "IEC60617-11-04-03",
      "iec_part": 11,
      "iec_description": "Consumer unit / domestic distribution board",
      "draftsman_id": "CONSUMER_UNIT",
      "category": "architectural",
      "display_name": "Consumer unit",
      "geometry": {
        "grid": 100,
        "bbox": [-25, -15, 25, 15],
        "path": "M -25 -15 L 25 -15 L 25 15 L -25 15 Z M -25 0 L 25 0",
        "terminals": {"incoming": [-25, 0], "outgoing": [25, 0]}
      },
      "variants": ["DB_GENERAL"],
      "annotation_fields": ["board_id", "way_count"],
      "usage_notes": "Domestic consumer unit (smaller DB form). Annotate number of ways and main switch rating. Compliant with BS EN 61439-3.",
      "related_symbols": ["DB_GENERAL", "RCBO_1P"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "DB_SUB",
      "iec_ref": "IEC60617-11-04-04",
      "iec_part": 11,
      "iec_description": "Sub-distribution board",
      "draftsman_id": "DB_SUB",
      "category": "architectural",
      "display_name": "Sub-distribution board (SDB)",
      "geometry": {
        "grid": 100,
        "bbox": [-30, -20, 30, 20],
        "path": "M -30 -20 L 30 -20 L 30 20 L -30 20 Z M -30 0 L 30 0 M -25 -10 L 25 -10",
        "terminals": {"incoming": [-30, 0], "outgoing": [30, 0]}
      },
      "variants": ["DB_MAIN", "DB_GENERAL"],
      "annotation_fields": ["board_id", "rated_A"],
      "usage_notes": "Sub-distribution board — fed from MSB or another SDB. Distinct from main board by smaller size and single internal divider.",
      "related_symbols": ["DB_MAIN", "DB_GENERAL"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "PANEL_GENERATOR",
      "iec_ref": "IEC60617-11-04-05",
      "iec_part": 11,
      "iec_description": "Generator control panel",
      "draftsman_id": "PANEL_GENERATOR",
      "category": "architectural",
      "display_name": "Generator control panel",
      "geometry": {
        "grid": 100,
        "bbox": [-30, -20, 30, 20],
        "path": "M -30 -20 L 30 -20 L 30 20 L -30 20 Z M -10 -10 L 10 -10 L 10 10 L -10 10 Z M -15 -5 L -5 -5 M 5 -5 L 15 -5",
        "terminals": {"incoming": [-30, 0], "outgoing": [30, 0]}
      },
      "variants": ["DB_MAIN", "PANEL_UPS"],
      "annotation_fields": ["board_id", "rating_kVA"],
      "usage_notes": "Generator control panel — rectangle with internal circle/box indicating generator association. Annotate generator rating.",
      "related_symbols": ["DB_MAIN", "GENERATOR_GENERAL", "ATS_2WAY"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "PANEL_UPS",
      "iec_ref": "IEC60617-11-04-06",
      "iec_part": 11,
      "iec_description": "UPS control panel",
      "draftsman_id": "PANEL_UPS",
      "category": "architectural",
      "display_name": "UPS panel",
      "geometry": {
        "grid": 100,
        "bbox": [-30, -20, 30, 20],
        "path": "M -30 -20 L 30 -20 L 30 20 L -30 20 Z M -15 -10 L 15 -10 L 15 10 L -15 10 Z M -10 0 L 10 0",
        "terminals": {"incoming": [-30, 0], "outgoing": [30, 0]}
      },
      "variants": ["PANEL_GENERATOR", "DB_MAIN"],
      "annotation_fields": ["board_id", "rating_kVA", "autonomy_min"],
      "usage_notes": "UPS panel — rectangle with internal box indicating UPS association.",
      "related_symbols": ["UPS", "DB_MAIN"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "SOCKET_SINGLE",
      "iec_ref": "IEC60617-11-15-01",
      "iec_part": 11,
      "iec_description": "Single socket outlet",
      "draftsman_id": "SOCKET_SINGLE",
      "category": "architectural",
      "display_name": "Single socket outlet",
      "geometry": {
        "grid": 100,
        "bbox": [-20, -20, 20, 20],
        "path": "M 20 0 A 20 20 0 1 0 -20 0 L 20 0 Z M 0 -5 L 0 5 M -8 0 L 8 0",
        "terminals": {"supply": [0, 20]}
      },
      "variants": ["SOCKET_DOUBLE", "SOCKET_SWITCHED_SINGLE", "SOCKET_INDUSTRIAL_IP44", "SOCKET_3PHASE"],
      "annotation_fields": ["rated_A", "type"],
      "usage_notes": "Plan-view single socket outlet — half-circle facing the wall. Two parallel marks indicate the L+N pins. Annotate rated current and type (e.g. 13A BS1363, 16A Schuko).",
      "related_symbols": ["SOCKET_DOUBLE", "SOCKET_SWITCHED_SINGLE"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "SOCKET_DOUBLE",
      "iec_ref": "IEC60617-11-15-02",
      "iec_part": 11,
      "iec_description": "Double socket outlet",
      "draftsman_id": "SOCKET_DOUBLE",
      "category": "architectural",
      "display_name": "Double socket outlet",
      "geometry": {
        "grid": 100,
        "bbox": [-30, -20, 30, 20],
        "path": "M 30 0 A 30 30 0 1 0 -30 0 L 30 0 Z M -15 -5 L -15 5 M -8 -5 L -8 5 M 8 -5 L 8 5 M 15 -5 L 15 5",
        "terminals": {"supply": [0, 20]}
      },
      "variants": ["SOCKET_SINGLE", "SOCKET_SWITCHED_DOUBLE"],
      "annotation_fields": ["rated_A", "type"],
      "usage_notes": "Plan-view double socket outlet — wider half-circle with two pairs of pin marks.",
      "related_symbols": ["SOCKET_SINGLE", "SOCKET_SWITCHED_DOUBLE"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "SOCKET_SWITCHED_SINGLE",
      "iec_ref": "IEC60617-11-15-03",
      "iec_part": 11,
      "iec_description": "Switched single socket outlet",
      "draftsman_id": "SOCKET_SWITCHED_SINGLE",
      "category": "architectural",
      "display_name": "Switched single socket",
      "geometry": {
        "grid": 100,
        "bbox": [-20, -25, 20, 20],
        "path": "M 20 0 A 20 20 0 1 0 -20 0 L 20 0 Z M 0 -5 L 0 5 M -8 0 L 8 0 M 0 -25 L 0 -15 M -5 -20 L 5 -25",
        "terminals": {"supply": [0, 20]}
      },
      "variants": ["SOCKET_SINGLE"],
      "annotation_fields": ["rated_A", "type"],
      "usage_notes": "Switched single socket — like SOCKET_SINGLE with an additional switch marker above. Standard for UK installations.",
      "related_symbols": ["SOCKET_SINGLE", "SWITCH_1WAY"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "SOCKET_SWITCHED_DOUBLE",
      "iec_ref": "IEC60617-11-15-04",
      "iec_part": 11,
      "iec_description": "Switched double socket outlet",
      "draftsman_id": "SOCKET_SWITCHED_DOUBLE",
      "category": "architectural",
      "display_name": "Switched double socket",
      "geometry": {
        "grid": 100,
        "bbox": [-30, -25, 30, 20],
        "path": "M 30 0 A 30 30 0 1 0 -30 0 L 30 0 Z M -15 -5 L -15 5 M -8 -5 L -8 5 M 8 -5 L 8 5 M 15 -5 L 15 5 M -10 -25 L -10 -15 M -15 -20 L -5 -25 M 10 -25 L 10 -15 M 5 -20 L 15 -25",
        "terminals": {"supply": [0, 20]}
      },
      "variants": ["SOCKET_DOUBLE", "SOCKET_SWITCHED_SINGLE"],
      "annotation_fields": ["rated_A", "type"],
      "usage_notes": "Switched double socket — most common UK domestic / commercial socket. Two switches above the outlets.",
      "related_symbols": ["SOCKET_DOUBLE", "SOCKET_SWITCHED_SINGLE"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "SOCKET_INDUSTRIAL_IP44",
      "iec_ref": "IEC60617-11-15-05",
      "iec_part": 11,
      "iec_description": "Industrial socket outlet — IP44",
      "draftsman_id": "SOCKET_INDUSTRIAL_IP44",
      "category": "architectural",
      "display_name": "Industrial socket (IP44, 16A)",
      "geometry": {
        "grid": 100,
        "bbox": [-25, -25, 25, 20],
        "path": "M 25 0 A 25 25 0 1 0 -25 0 L 25 0 Z M 0 -10 L 0 0 M -10 -5 L 10 -5 M -20 -20 L 20 -20",
        "terminals": {"supply": [0, 20]}
      },
      "variants": ["SOCKET_INDUSTRIAL_IP67", "SOCKET_3PHASE"],
      "annotation_fields": ["rated_A", "voltage_V", "phase_count"],
      "usage_notes": "Industrial CEE/Commando socket — IP44 splash-proof, 16A or 32A. Bar across the top indicates IP rating. Used in industrial environments, workshops.",
      "related_symbols": ["SOCKET_INDUSTRIAL_IP67", "SOCKET_3PHASE"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "SOCKET_INDUSTRIAL_IP67",
      "iec_ref": "IEC60617-11-15-06",
      "iec_part": 11,
      "iec_description": "Industrial socket outlet — IP67",
      "draftsman_id": "SOCKET_INDUSTRIAL_IP67",
      "category": "architectural",
      "display_name": "Industrial socket (IP67, 16A)",
      "geometry": {
        "grid": 100,
        "bbox": [-25, -30, 25, 20],
        "path": "M 25 0 A 25 25 0 1 0 -25 0 L 25 0 Z M 0 -10 L 0 0 M -10 -5 L 10 -5 M -20 -20 L 20 -20 M -20 -25 L 20 -25",
        "terminals": {"supply": [0, 20]}
      },
      "variants": ["SOCKET_INDUSTRIAL_IP44"],
      "annotation_fields": ["rated_A", "voltage_V", "phase_count"],
      "usage_notes": "Industrial CEE/Commando socket — IP67 immersion-proof. Double-bar over the top indicates higher IP. For wet/exterior locations.",
      "related_symbols": ["SOCKET_INDUSTRIAL_IP44"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "SOCKET_3PHASE",
      "iec_ref": "IEC60617-11-15-07",
      "iec_part": 11,
      "iec_description": "Three-phase socket outlet",
      "draftsman_id": "SOCKET_3PHASE",
      "category": "architectural",
      "display_name": "3-phase socket outlet",
      "geometry": {
        "grid": 100,
        "bbox": [-25, -25, 25, 20],
        "path": "M 25 0 A 25 25 0 1 0 -25 0 L 25 0 Z M 0 -10 L 0 0 M -12 -5 L -8 -5 M -2 -5 L 2 -5 M 8 -5 L 12 -5 M -15 -20 L 15 -20",
        "terminals": {"supply": [0, 20]}
      },
      "variants": ["SOCKET_INDUSTRIAL_IP44", "SOCKET_COMMANDO_32A"],
      "annotation_fields": ["rated_A", "voltage_V"],
      "usage_notes": "3-phase industrial socket — three pin marks indicating L1/L2/L3 plus N and PE. Annotate 16A, 32A, or 63A rating.",
      "related_symbols": ["SOCKET_INDUSTRIAL_IP44", "SOCKET_COMMANDO_32A"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "SOCKET_COMMANDO_32A",
      "iec_ref": "IEC60617-11-15-08",
      "iec_part": 11,
      "iec_description": "32A industrial Commando socket",
      "draftsman_id": "SOCKET_COMMANDO_32A",
      "category": "architectural",
      "display_name": "Commando socket (32A)",
      "geometry": {
        "grid": 100,
        "bbox": [-30, -25, 30, 20],
        "path": "M 30 0 A 30 30 0 1 0 -30 0 L 30 0 Z M 0 -10 L 0 0 M -15 -5 L -10 -5 M -3 -5 L 3 -5 M 10 -5 L 15 -5 M -20 -20 L 20 -20",
        "terminals": {"supply": [0, 20]}
      },
      "variants": ["SOCKET_3PHASE", "SOCKET_INDUSTRIAL_IP44"],
      "annotation_fields": ["rated_A", "voltage_V"],
      "usage_notes": "32A 3-phase + N + PE Commando socket (IEC 60309). Larger than 16A version. Standard for site/workshop power.",
      "related_symbols": ["SOCKET_3PHASE"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "LUMINAIRE_ARCH",
      "iec_ref": "IEC60617-11-09-01",
      "iec_part": 11,
      "iec_description": "Luminaire (architectural plan)",
      "draftsman_id": "LUMINAIRE_ARCH",
      "category": "architectural",
      "display_name": "Luminaire (general, plan)",
      "geometry": {
        "grid": 100,
        "bbox": [-25, -25, 25, 25],
        "path": "M 25 0 A 25 25 0 1 0 -25 0 A 25 25 0 1 0 25 0 Z M 0 -25 L 0 25 M -25 0 L 25 0",
        "terminals": {"supply": [25, 0]}
      },
      "variants": ["LUMINAIRE_EMERGENCY", "LUMINAIRE_RECESSED", "LUMINAIRE_EXTERIOR", "LUMINAIRE_GENERAL"],
      "annotation_fields": ["lamp_type", "wattage_W", "lumen_output"],
      "usage_notes": "Architectural-plan luminaire — circle with internal cross. Annotate lamp type (LED, T5, etc.) and rating. The DraftsMan lighting-layout skill uses this as its primary luminaire symbol.",
      "related_symbols": ["LUMINAIRE_EMERGENCY", "LUMINAIRE_RECESSED", "LUMINAIRE_GENERAL"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "LUMINAIRE_EMERGENCY",
      "iec_ref": "IEC60617-11-09-02",
      "iec_part": 11,
      "iec_description": "Emergency luminaire",
      "draftsman_id": "LUMINAIRE_EMERGENCY",
      "category": "architectural",
      "display_name": "Emergency luminaire",
      "geometry": {
        "grid": 100,
        "bbox": [-25, -25, 25, 25],
        "path": "M 25 0 A 25 25 0 1 0 -25 0 A 25 25 0 1 0 25 0 Z M 0 -25 L 0 25 M -25 0 L 25 0 M -10 -10 L 10 -10 L 10 10 L -10 10 Z",
        "terminals": {"supply": [25, 0]}
      },
      "variants": ["LUMINAIRE_ARCH"],
      "annotation_fields": ["lamp_type", "wattage_W", "duration_min"],
      "usage_notes": "Emergency luminaire — luminaire symbol with internal square indicating self-contained battery pack. Annotate duration (1h, 3h per BS EN 50172).",
      "related_symbols": ["LUMINAIRE_ARCH", "BATTERY"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "LUMINAIRE_RECESSED",
      "iec_ref": "IEC60617-11-09-03",
      "iec_part": 11,
      "iec_description": "Recessed luminaire",
      "draftsman_id": "LUMINAIRE_RECESSED",
      "category": "architectural",
      "display_name": "Recessed luminaire",
      "geometry": {
        "grid": 100,
        "bbox": [-25, -25, 25, 25],
        "path": "M -25 -25 L 25 -25 L 25 25 L -25 25 Z M 0 -25 L 0 25 M -25 0 L 25 0",
        "terminals": {"supply": [25, 0]}
      },
      "variants": ["LUMINAIRE_ARCH"],
      "annotation_fields": ["lamp_type", "wattage_W", "size_mm"],
      "usage_notes": "Recessed luminaire — square outline with internal cross. Common for office ceiling panels (e.g. 600×600 LED).",
      "related_symbols": ["LUMINAIRE_ARCH"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "LUMINAIRE_EXTERIOR",
      "iec_ref": "IEC60617-11-09-04",
      "iec_part": 11,
      "iec_description": "Exterior luminaire",
      "draftsman_id": "LUMINAIRE_EXTERIOR",
      "category": "architectural",
      "display_name": "External luminaire",
      "geometry": {
        "grid": 100,
        "bbox": [-25, -25, 25, 25],
        "path": "M 25 0 A 25 25 0 1 0 -25 0 A 25 25 0 1 0 25 0 Z M 0 -25 L 0 25 M -25 0 L 25 0 M -32 -32 L -25 -25 M 25 25 L 32 32 M -32 32 L -25 25 M 25 -25 L 32 -32",
        "terminals": {"supply": [25, 0]}
      },
      "variants": ["LUMINAIRE_ARCH"],
      "annotation_fields": ["lamp_type", "wattage_W", "ip_rating"],
      "usage_notes": "Exterior luminaire — luminaire symbol with four light-ray marks. Annotate IP rating (IP44 minimum for outdoor).",
      "related_symbols": ["LUMINAIRE_ARCH"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "SWITCH_1WAY",
      "iec_ref": "IEC60617-11-12-01",
      "iec_part": 11,
      "iec_description": "1-way switch",
      "draftsman_id": "SWITCH_1WAY",
      "category": "architectural",
      "display_name": "1-way switch",
      "geometry": {
        "grid": 100,
        "bbox": [-15, -15, 15, 15],
        "path": "M 15 0 A 15 15 0 1 0 -15 0 A 15 15 0 1 0 15 0 Z M 0 0 L 10 -10",
        "terminals": {"supply": [-15, 0], "load": [15, 0]}
      },
      "variants": ["SWITCH_2WAY", "SWITCH_INTERMEDIATE", "SWITCH_DIMMER"],
      "annotation_fields": ["rated_A", "tag"],
      "usage_notes": "Single-pole one-way switch — circle with internal switch blade. Most common wall switch for lighting circuits.",
      "related_symbols": ["SWITCH_2WAY", "SWITCH_INTERMEDIATE"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "SWITCH_2WAY",
      "iec_ref": "IEC60617-11-12-02",
      "iec_part": 11,
      "iec_description": "2-way switch (SPDT)",
      "draftsman_id": "SWITCH_2WAY",
      "category": "architectural",
      "display_name": "2-way switch",
      "geometry": {
        "grid": 100,
        "bbox": [-15, -15, 15, 15],
        "path": "M 15 0 A 15 15 0 1 0 -15 0 A 15 15 0 1 0 15 0 Z M 0 0 L 10 -10 M 0 0 L 10 10",
        "terminals": {"common": [-15, 0], "way_a": [15, -10], "way_b": [15, 10]}
      },
      "variants": ["SWITCH_1WAY", "SWITCH_INTERMEDIATE"],
      "annotation_fields": ["rated_A", "tag"],
      "usage_notes": "2-way (SPDT) switch — used in pairs to control a lighting circuit from two locations (e.g. top and bottom of stairs).",
      "related_symbols": ["SWITCH_1WAY", "SWITCH_INTERMEDIATE"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "SWITCH_INTERMEDIATE",
      "iec_ref": "IEC60617-11-12-03",
      "iec_part": 11,
      "iec_description": "Intermediate switch (DPDT)",
      "draftsman_id": "SWITCH_INTERMEDIATE",
      "category": "architectural",
      "display_name": "Intermediate switch",
      "geometry": {
        "grid": 100,
        "bbox": [-15, -15, 15, 15],
        "path": "M 15 0 A 15 15 0 1 0 -15 0 A 15 15 0 1 0 15 0 Z M 0 -10 L 10 -10 M 0 10 L 10 10 M -10 -10 L 0 0 M -10 10 L 0 0",
        "terminals": {"l_a": [-15, -10], "l_b": [-15, 10], "r_a": [15, -10], "r_b": [15, 10]}
      },
      "variants": ["SWITCH_1WAY", "SWITCH_2WAY"],
      "annotation_fields": ["rated_A", "tag"],
      "usage_notes": "Intermediate switch — placed between two 2-way switches for three or more switching points (e.g. long corridor with switches at both ends and middle).",
      "related_symbols": ["SWITCH_2WAY"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "SWITCH_DIMMER",
      "iec_ref": "IEC60617-11-12-04",
      "iec_part": 11,
      "iec_description": "Dimmer switch",
      "draftsman_id": "SWITCH_DIMMER",
      "category": "architectural",
      "display_name": "Dimmer switch",
      "geometry": {
        "grid": 100,
        "bbox": [-15, -20, 15, 15],
        "path": "M 15 0 A 15 15 0 1 0 -15 0 A 15 15 0 1 0 15 0 Z M 0 0 L 10 -10 M -5 -20 L 5 -10",
        "terminals": {"supply": [-15, 0], "load": [15, 0]}
      },
      "variants": ["SWITCH_1WAY"],
      "annotation_fields": ["rated_W", "dim_type"],
      "usage_notes": "Dimmer switch — 1-way switch with diagonal arrow indicating variable output. Annotate dim type (trailing-edge, leading-edge, DALI).",
      "related_symbols": ["SWITCH_1WAY", "VARIABILITY_ARROW"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "SENSOR_PIR",
      "iec_ref": "IEC60617-11-13-01",
      "iec_part": 11,
      "iec_description": "PIR occupancy sensor",
      "draftsman_id": "SENSOR_PIR",
      "category": "architectural",
      "display_name": "PIR sensor",
      "geometry": {
        "grid": 100,
        "bbox": [-20, -25, 20, 20],
        "path": "M 20 0 A 20 20 0 1 0 -20 0 A 20 20 0 1 0 20 0 Z M -15 -10 L 15 -10 L 10 -5 L 15 0 L 10 5 L 15 10 L -15 10 Z",
        "terminals": {"supply": [0, 20]}
      },
      "variants": ["SENSOR_OCCUPANCY", "SENSOR_DAYLIGHT"],
      "annotation_fields": ["detection_range_m", "function"],
      "usage_notes": "Passive infrared occupancy sensor — circle with zigzag indicating PIR detection field. Used for energy-saving lighting control.",
      "related_symbols": ["SENSOR_OCCUPANCY", "SENSOR_DAYLIGHT"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "SENSOR_OCCUPANCY",
      "iec_ref": "IEC60617-11-13-02",
      "iec_part": 11,
      "iec_description": "Occupancy sensor (general)",
      "draftsman_id": "SENSOR_OCCUPANCY",
      "category": "architectural",
      "display_name": "Occupancy sensor",
      "geometry": {
        "grid": 100,
        "bbox": [-20, -25, 20, 20],
        "path": "M 20 0 A 20 20 0 1 0 -20 0 A 20 20 0 1 0 20 0 Z M -10 0 A 10 10 0 1 0 10 0 A 10 10 0 1 0 -10 0 Z",
        "terminals": {"supply": [0, 20]}
      },
      "variants": ["SENSOR_PIR", "SENSOR_DAYLIGHT"],
      "annotation_fields": ["sensor_type", "detection_range_m"],
      "usage_notes": "Generic occupancy sensor — circle with inner circle. Use when sensor type is not PIR-specific (e.g. ultrasonic, dual-tech). PIR-specific = SENSOR_PIR.",
      "related_symbols": ["SENSOR_PIR"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "SENSOR_DAYLIGHT",
      "iec_ref": "IEC60617-11-13-03",
      "iec_part": 11,
      "iec_description": "Daylight / photocell sensor",
      "draftsman_id": "SENSOR_DAYLIGHT",
      "category": "architectural",
      "display_name": "Daylight sensor / photocell",
      "geometry": {
        "grid": 100,
        "bbox": [-20, -25, 20, 20],
        "path": "M 20 0 A 20 20 0 1 0 -20 0 A 20 20 0 1 0 20 0 Z M -10 -10 L 10 10 M -8 0 A 8 8 0 1 0 8 0 A 8 8 0 1 0 -8 0 Z",
        "terminals": {"supply": [0, 20]}
      },
      "variants": ["SENSOR_OCCUPANCY", "SENSOR_PIR"],
      "annotation_fields": ["setpoint_lux"],
      "usage_notes": "Daylight sensor — circle with sun-like marks. Used for automatic lighting control based on ambient light. Required for Part L compliance in many regions.",
      "related_symbols": ["SENSOR_OCCUPANCY"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "DETECTOR_SMOKE",
      "iec_ref": "IEC60617-11-14-01",
      "iec_part": 11,
      "iec_description": "Smoke detector",
      "draftsman_id": "DETECTOR_SMOKE",
      "category": "architectural",
      "display_name": "Smoke detector",
      "geometry": {
        "grid": 100,
        "bbox": [-20, -20, 20, 20],
        "path": "M 20 0 A 20 20 0 1 0 -20 0 A 20 20 0 1 0 20 0 Z M 0 -5 L 0 5 M -10 -8 L 10 8 M 10 -8 L -10 8 M -5 -2 L 5 2",
        "terminals": {"loop_a": [-20, 0], "loop_b": [20, 0]}
      },
      "variants": ["DETECTOR_HEAT", "CALL_POINT_MANUAL"],
      "annotation_fields": ["detector_type", "loop_address"],
      "usage_notes": "Smoke detector — circle with internal S / cross marker. Annotate detector type (ionisation, optical, multi-sensor) and loop address.",
      "related_symbols": ["DETECTOR_HEAT", "CALL_POINT_MANUAL"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "DETECTOR_HEAT",
      "iec_ref": "IEC60617-11-14-02",
      "iec_part": 11,
      "iec_description": "Heat detector",
      "draftsman_id": "DETECTOR_HEAT",
      "category": "architectural",
      "display_name": "Heat detector",
      "geometry": {
        "grid": 100,
        "bbox": [-20, -20, 20, 20],
        "path": "M 20 0 A 20 20 0 1 0 -20 0 A 20 20 0 1 0 20 0 Z M -8 -8 L 8 -8 L 8 8 L -8 8 Z M 0 -8 L 0 8",
        "terminals": {"loop_a": [-20, 0], "loop_b": [20, 0]}
      },
      "variants": ["DETECTOR_SMOKE"],
      "annotation_fields": ["detector_type", "loop_address"],
      "usage_notes": "Heat detector — circle with internal square. Annotate type (fixed temperature, rate-of-rise). Used in kitchens, plant rooms where smoke detector would false-alarm.",
      "related_symbols": ["DETECTOR_SMOKE"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "CALL_POINT_MANUAL",
      "iec_ref": "IEC60617-11-14-03",
      "iec_part": 11,
      "iec_description": "Manual call point (fire alarm)",
      "draftsman_id": "CALL_POINT_MANUAL",
      "category": "architectural",
      "display_name": "Manual call point (MCP)",
      "geometry": {
        "grid": 100,
        "bbox": [-20, -20, 20, 20],
        "path": "M -15 -15 L 15 -15 L 15 15 L -15 15 Z M -10 -10 L 10 10 M 10 -10 L -10 10",
        "terminals": {"loop_a": [-20, 0], "loop_b": [20, 0]}
      },
      "variants": ["DETECTOR_SMOKE"],
      "annotation_fields": ["loop_address"],
      "usage_notes": "Manual call point — square with internal X. EN 54-11 break-glass type. Required on escape routes.",
      "related_symbols": ["DETECTOR_SMOKE"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "JUNCTION_BOX",
      "iec_ref": "IEC60617-11-05-01",
      "iec_part": 11,
      "iec_description": "Junction box (architectural plan)",
      "draftsman_id": "JUNCTION_BOX",
      "category": "architectural",
      "display_name": "Junction box (plan)",
      "geometry": {
        "grid": 100,
        "bbox": [-15, -15, 15, 15],
        "path": "M -15 -15 L 15 -15 L 15 15 L -15 15 Z M -8 0 L 8 0 M 0 -8 L 0 8",
        "terminals": {"cable_entry": [0, 15]}
      },
      "variants": ["JUNCTION_BOX_CONDUCTOR"],
      "annotation_fields": ["box_id", "ip_rating"],
      "usage_notes": "Architectural junction box — square with internal cross. Annotate box ID and IP rating. The plan-view equivalent of the schematic JUNCTION_BOX_CONDUCTOR.",
      "related_symbols": ["JUNCTION_BOX_CONDUCTOR"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "CABLE_ROUTE_GENERAL",
      "iec_ref": "IEC60617-11-06-01",
      "iec_part": 11,
      "iec_description": "Cable route (general)",
      "draftsman_id": "CABLE_ROUTE_GENERAL",
      "category": "architectural",
      "display_name": "Cable route (general)",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -3, 50, 3],
        "path": "M -50 0 L 50 0",
        "terminals": {"start": [-50, 0], "end": [50, 0]}
      },
      "variants": ["CABLE_ROUTE_CONCEALED", "CABLE_ROUTE_SURFACE", "CABLE_ROUTE_OVERHEAD", "CABLE_ROUTE_UNDERGROUND"],
      "annotation_fields": ["circuit_id", "csa_mm2"],
      "usage_notes": "Generic cable route on a plan — solid line. Use when route method is not specified or for simplicity.",
      "related_symbols": ["CABLE_ROUTE_CONCEALED", "CABLE_ROUTE_SURFACE", "CONDUCTOR_SINGLE"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "CABLE_ROUTE_CONCEALED",
      "iec_ref": "IEC60617-11-06-02",
      "iec_part": 11,
      "iec_description": "Cable route (concealed in wall/ceiling)",
      "draftsman_id": "CABLE_ROUTE_CONCEALED",
      "category": "architectural",
      "display_name": "Concealed cable route",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -3, 50, 3],
        "path": "M -50 0 L 50 0",
        "terminals": {"start": [-50, 0], "end": [50, 0]}
      },
      "variants": ["CABLE_ROUTE_SURFACE", "CABLE_ROUTE_GENERAL"],
      "annotation_fields": ["circuit_id"],
      "usage_notes": "Cable route concealed in wall/ceiling (chased, in conduit). Rendered as dashed line.",
      "related_symbols": ["CABLE_ROUTE_GENERAL", "CABLE_ROUTE_SURFACE"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "CABLE_ROUTE_SURFACE",
      "iec_ref": "IEC60617-11-06-03",
      "iec_part": 11,
      "iec_description": "Cable route (surface trunking)",
      "draftsman_id": "CABLE_ROUTE_SURFACE",
      "category": "architectural",
      "display_name": "Surface trunking route",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -5, 50, 5],
        "path": "M -50 -3 L 50 -3 M -50 3 L 50 3",
        "terminals": {"start": [-50, 0], "end": [50, 0]}
      },
      "variants": ["CABLE_ROUTE_CONCEALED", "TRUNKING"],
      "annotation_fields": ["circuit_id", "trunking_size"],
      "usage_notes": "Surface-mounted trunking route — drawn as two parallel solid lines.",
      "related_symbols": ["TRUNKING", "CABLE_ROUTE_CONCEALED"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "CABLE_ROUTE_OVERHEAD",
      "iec_ref": "IEC60617-11-06-04",
      "iec_part": 11,
      "iec_description": "Cable route (overhead)",
      "draftsman_id": "CABLE_ROUTE_OVERHEAD",
      "category": "architectural",
      "display_name": "Overhead cable route",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -10, 50, 5],
        "path": "M -50 0 L 50 0 M -25 0 L -25 -10 M 25 0 L 25 -10",
        "terminals": {"start": [-50, 0], "end": [50, 0]}
      },
      "variants": ["CABLE_ROUTE_UNDERGROUND", "CONDUCTOR_OVERHEAD"],
      "annotation_fields": ["circuit_id"],
      "usage_notes": "Overhead cable route — line with vertical pole markers. Used for site/external runs.",
      "related_symbols": ["CONDUCTOR_OVERHEAD"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "CABLE_ROUTE_UNDERGROUND",
      "iec_ref": "IEC60617-11-06-05",
      "iec_part": 11,
      "iec_description": "Cable route (underground)",
      "draftsman_id": "CABLE_ROUTE_UNDERGROUND",
      "category": "architectural",
      "display_name": "Underground cable route",
      "geometry": {
        "grid": 100,
        "bbox": [-50, -3, 50, 12],
        "path": "M -50 0 L 50 0 M -25 0 L -25 10 M 25 0 L 25 10",
        "terminals": {"start": [-50, 0], "end": [50, 0]}
      },
      "variants": ["CABLE_ROUTE_OVERHEAD", "CONDUCTOR_UNDERGROUND"],
      "annotation_fields": ["circuit_id", "depth_mm"],
      "usage_notes": "Underground / buried cable route — line with downward markers indicating buried position. Annotate burial depth.",
      "related_symbols": ["CONDUCTOR_UNDERGROUND"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "MOTOR_CONNECTION",
      "iec_ref": "IEC60617-11-08-01",
      "iec_part": 11,
      "iec_description": "Motor connection point (architectural)",
      "draftsman_id": "MOTOR_CONNECTION",
      "category": "architectural",
      "display_name": "Motor connection point",
      "geometry": {
        "grid": 100,
        "bbox": [-20, -25, 20, 20],
        "path": "M 20 0 A 20 20 0 1 0 -20 0 A 20 20 0 1 0 20 0 Z M -8 -8 L 8 -8 M -8 8 L 8 8 M 0 -8 L 0 8",
        "terminals": {"supply": [0, 20]}
      },
      "variants": ["MOTOR_GENERAL", "EV_CHARGING_POINT"],
      "annotation_fields": ["motor_id", "rating_kW"],
      "usage_notes": "Plan-view motor connection — circle with internal 'M' marking (drawn as cross-hair). Used to mark where a motor connects to the fixed wiring (e.g. AHU fan, pump set).",
      "related_symbols": ["MOTOR_INDUCTION", "MOTOR_GENERAL"],
      "generating_shared_symbol": true
    },
    {
      "symbol_id": "EV_CHARGING_POINT",
      "iec_ref": "IEC60617-11-15-10",
      "iec_part": 11,
      "iec_description": "Electric vehicle charging point",
      "draftsman_id": "EV_CHARGING_POINT",
      "category": "architectural",
      "display_name": "EV charging point",
      "geometry": {
        "grid": 100,
        "bbox": [-20, -25, 20, 20],
        "path": "M 20 0 A 20 20 0 1 0 -20 0 A 20 20 0 1 0 20 0 Z M -10 -8 L 10 -8 M -10 -3 L 10 -3 M -3 3 L 3 3 M -3 8 L 3 8 M -10 -8 L -10 -3 M 10 -8 L 10 -3",
        "terminals": {"supply": [0, 20]}
      },
      "variants": ["SOCKET_3PHASE", "MOTOR_CONNECTION"],
      "annotation_fields": ["rated_A", "mode", "rated_kW"],
      "usage_notes": "EV charging point — circle with charging plug indicator. Annotate Mode (1-4 per IEC 61851), rated current and kW. Required cable sizing = 100% of EVSE rated current (no diversity).",
      "related_symbols": ["SOCKET_3PHASE"],
      "generating_shared_symbol": true
    }
  ]
}
```

- [ ] **Step 2: Validate JSON syntax**

Run: `python3 -c "import json; json.load(open('shared/standards/electrical/IEC60617/part11-architectural.json'))" && echo OK`
Expected: `OK`

- [ ] **Step 3: Verify symbol count**

Run: `python3 -c "import json; print(len(json.load(open('shared/standards/electrical/IEC60617/part11-architectural.json'))['symbols']))"`
Expected: `36`

- [ ] **Step 4: Verify all schema fields present**

Run: `python3 -c "import json; data=json.load(open('shared/standards/electrical/IEC60617/part11-architectural.json')); req=['symbol_id','iec_ref','iec_part','iec_description','draftsman_id','category','display_name','geometry','variants','annotation_fields','usage_notes','related_symbols','generating_shared_symbol']; missing=[(s.get('symbol_id','?'), [f for f in req if f not in s]) for s in data['symbols'] if any(f not in s for f in req)]; print('OK' if not missing else 'MISSING:'+str(missing))"`
Expected: `OK`

- [ ] **Step 5: Commit**

```bash
git add shared/standards/electrical/IEC60617/part11-architectural.json
git commit -m "feat: IEC60617 part11-architectural.json — 36 architectural plan symbols"
```

---

## Task 12: Create symbol-index.json (flat O(1) lookup of all 226 symbols)

**Files:**
- Create: `shared/standards/electrical/IEC60617/symbol-index.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "IEC 60617 — Master Symbol Index",
  "_version": "1.0.0",
  "_generated_from": ["part2-general.json", "part3-conductors.json", "part6-power.json", "part7-switchgear.json", "part8-measurement.json", "part11-architectural.json"],
  "_note": "Flat lookup of every symbol in the layer. Hand-maintained in sync with the six part files — not auto-generated by a script. When a new symbol is added to a part file, add the corresponding index entry here. Load this file for symbol_id → IEC ref + category + part file mapping. Load the part file when geometry or usage notes are needed.",
  "symbols": [
    {"symbol_id": "JUNCTION_T", "iec_ref": "IEC60617-02-02-02", "iec_part": 2, "category": "general", "display_name": "T-junction (connected)", "part_file": "part2-general.json"},
    {"symbol_id": "JUNCTION_CROSS", "iec_ref": "IEC60617-02-02-03", "iec_part": 2, "category": "general", "display_name": "Cross junction (connected)", "part_file": "part2-general.json"},
    {"symbol_id": "WIRE_CROSSING", "iec_ref": "IEC60617-02-02-01", "iec_part": 2, "category": "general", "display_name": "Wire crossing (no connection)", "part_file": "part2-general.json"},
    {"symbol_id": "TERMINAL_SYMBOL", "iec_ref": "IEC60617-02-09-02", "iec_part": 2, "category": "general", "display_name": "Terminal", "part_file": "part2-general.json"},
    {"symbol_id": "TEST_POINT", "iec_ref": "IEC60617-02-09-04", "iec_part": 2, "category": "general", "display_name": "Test point", "part_file": "part2-general.json"},
    {"symbol_id": "VARIABILITY_ARROW", "iec_ref": "IEC60617-02-04-01", "iec_part": 2, "category": "general", "display_name": "Variability arrow (qualifying)", "part_file": "part2-general.json"},
    {"symbol_id": "ADJUSTABILITY_MARKER", "iec_ref": "IEC60617-02-04-02", "iec_part": 2, "category": "general", "display_name": "Adjustability marker (qualifying)", "part_file": "part2-general.json"},
    {"symbol_id": "POLARITY_PLUS", "iec_ref": "IEC60617-02-05-01", "iec_part": 2, "category": "general", "display_name": "Positive polarity (+)", "part_file": "part2-general.json"},
    {"symbol_id": "POLARITY_MINUS", "iec_ref": "IEC60617-02-05-02", "iec_part": 2, "category": "general", "display_name": "Negative polarity (-)", "part_file": "part2-general.json"},
    {"symbol_id": "FUNCTIONAL_GROUP", "iec_ref": "IEC60617-02-07-01", "iec_part": 2, "category": "general", "display_name": "Functional grouping (dashed)", "part_file": "part2-general.json"},
    {"symbol_id": "ENCLOSURE_DOTTED", "iec_ref": "IEC60617-02-07-02", "iec_part": 2, "category": "general", "display_name": "Enclosure boundary (dotted)", "part_file": "part2-general.json"},
    {"symbol_id": "SHIELD_SYMBOL", "iec_ref": "IEC60617-02-06-01", "iec_part": 2, "category": "general", "display_name": "Shield / screen (qualifying)", "part_file": "part2-general.json"},
    {"symbol_id": "SCREEN_CONDUCTOR", "iec_ref": "IEC60617-02-06-02", "iec_part": 2, "category": "general", "display_name": "Screened conductor", "part_file": "part2-general.json"},
    {"symbol_id": "EARTH_GENERAL", "iec_ref": "IEC60617-02-15-01", "iec_part": 2, "category": "general", "display_name": "Earth (general)", "part_file": "part2-general.json"},
    {"symbol_id": "EARTH_PROTECTIVE", "iec_ref": "IEC60617-02-15-02", "iec_part": 2, "category": "general", "display_name": "Protective earth (PE)", "part_file": "part2-general.json"},
    {"symbol_id": "EARTH_CLEAN", "iec_ref": "IEC60617-02-15-04", "iec_part": 2, "category": "general", "display_name": "Clean / noiseless earth", "part_file": "part2-general.json"},
    {"symbol_id": "EARTH_CHASSIS", "iec_ref": "IEC60617-02-15-03", "iec_part": 2, "category": "general", "display_name": "Chassis earth", "part_file": "part2-general.json"},
    {"symbol_id": "NOT_CONNECTED", "iec_ref": "IEC60617-02-09-01", "iec_part": 2, "category": "general", "display_name": "Not connected (X marker)", "part_file": "part2-general.json"},
    {"symbol_id": "COMMON_RETURN", "iec_ref": "IEC60617-02-13-01", "iec_part": 2, "category": "general", "display_name": "Common return bus", "part_file": "part2-general.json"},
    {"symbol_id": "SIGNAL_LEVEL", "iec_ref": "IEC60617-02-13-04", "iec_part": 2, "category": "general", "display_name": "Signal level indicator", "part_file": "part2-general.json"},
    {"symbol_id": "FILTER_GENERAL", "iec_ref": "IEC60617-02-12-01", "iec_part": 2, "category": "general", "display_name": "Filter (general)", "part_file": "part2-general.json"},
    {"symbol_id": "COAX_CONNECTOR", "iec_ref": "IEC60617-02-09-05", "iec_part": 2, "category": "general", "display_name": "Coaxial connector", "part_file": "part2-general.json"},
    {"symbol_id": "OPTIONAL_PATH", "iec_ref": "IEC60617-02-13-02", "iec_part": 2, "category": "general", "display_name": "Optional path (dashed line)", "part_file": "part2-general.json"},
    {"symbol_id": "DELAY_SYMBOL", "iec_ref": "IEC60617-02-12-03", "iec_part": 2, "category": "general", "display_name": "Delay element (qualifying)", "part_file": "part2-general.json"},
    {"symbol_id": "FAULT_INDICATOR", "iec_ref": "IEC60617-02-12-05", "iec_part": 2, "category": "general", "display_name": "Fault indicator (qualifying)", "part_file": "part2-general.json"},

    {"symbol_id": "CONDUCTOR_SINGLE", "iec_ref": "IEC60617-03-01-01", "iec_part": 3, "category": "conductor", "display_name": "Single conductor", "part_file": "part3-conductors.json"},
    {"symbol_id": "CONDUCTOR_2CORE", "iec_ref": "IEC60617-03-01-02", "iec_part": 3, "category": "conductor", "display_name": "2-core cable", "part_file": "part3-conductors.json"},
    {"symbol_id": "CONDUCTOR_3CORE", "iec_ref": "IEC60617-03-01-03", "iec_part": 3, "category": "conductor", "display_name": "3-core cable", "part_file": "part3-conductors.json"},
    {"symbol_id": "CONDUCTOR_4CORE", "iec_ref": "IEC60617-03-01-04", "iec_part": 3, "category": "conductor", "display_name": "4-core cable", "part_file": "part3-conductors.json"},
    {"symbol_id": "CONDUCTOR_NCORE", "iec_ref": "IEC60617-03-01-05", "iec_part": 3, "category": "conductor", "display_name": "Multi-core cable (n-core)", "part_file": "part3-conductors.json"},
    {"symbol_id": "BUSBAR", "iec_ref": "IEC60617-03-02-01", "iec_part": 3, "category": "conductor", "display_name": "Busbar (single)", "part_file": "part3-conductors.json"},
    {"symbol_id": "BUSBAR_3PH", "iec_ref": "IEC60617-03-02-02", "iec_part": 3, "category": "conductor", "display_name": "3-phase busbar", "part_file": "part3-conductors.json"},
    {"symbol_id": "CONDUCTOR_IN_CONDUIT", "iec_ref": "IEC60617-03-03-01", "iec_part": 3, "category": "conductor", "display_name": "Conductor in conduit", "part_file": "part3-conductors.json"},
    {"symbol_id": "CONDUCTOR_IN_DUCT", "iec_ref": "IEC60617-03-03-02", "iec_part": 3, "category": "conductor", "display_name": "Conductor in duct/trunking", "part_file": "part3-conductors.json"},
    {"symbol_id": "CONDUCTOR_GROUPED", "iec_ref": "IEC60617-03-01-06", "iec_part": 3, "category": "conductor", "display_name": "Grouped conductors", "part_file": "part3-conductors.json"},
    {"symbol_id": "CONDUCTOR_ARMOURED", "iec_ref": "IEC60617-03-01-07", "iec_part": 3, "category": "conductor", "display_name": "Armoured cable (SWA)", "part_file": "part3-conductors.json"},
    {"symbol_id": "CONDUCTOR_OVERHEAD", "iec_ref": "IEC60617-03-03-04", "iec_part": 3, "category": "conductor", "display_name": "Overhead line", "part_file": "part3-conductors.json"},
    {"symbol_id": "CONDUCTOR_UNDERGROUND", "iec_ref": "IEC60617-03-03-05", "iec_part": 3, "category": "conductor", "display_name": "Underground cable", "part_file": "part3-conductors.json"},
    {"symbol_id": "CONDUCTOR_FLEXIBLE", "iec_ref": "IEC60617-03-01-08", "iec_part": 3, "category": "conductor", "display_name": "Flexible connection", "part_file": "part3-conductors.json"},
    {"symbol_id": "CONDUCTOR_EARTH", "iec_ref": "IEC60617-03-01-09", "iec_part": 3, "category": "conductor", "display_name": "Earth conductor", "part_file": "part3-conductors.json"},
    {"symbol_id": "CONDUCTOR_NEUTRAL", "iec_ref": "IEC60617-03-01-10", "iec_part": 3, "category": "conductor", "display_name": "Neutral conductor", "part_file": "part3-conductors.json"},
    {"symbol_id": "CONDUCTOR_PE", "iec_ref": "IEC60617-03-01-11", "iec_part": 3, "category": "conductor", "display_name": "PE conductor", "part_file": "part3-conductors.json"},
    {"symbol_id": "CONDUCTOR_PEN", "iec_ref": "IEC60617-03-01-12", "iec_part": 3, "category": "conductor", "display_name": "PEN conductor", "part_file": "part3-conductors.json"},
    {"symbol_id": "CONDUCTOR_DRAIN", "iec_ref": "IEC60617-03-01-13", "iec_part": 3, "category": "conductor", "display_name": "Drain wire", "part_file": "part3-conductors.json"},
    {"symbol_id": "CONDUCTOR_COAX", "iec_ref": "IEC60617-03-01-14", "iec_part": 3, "category": "conductor", "display_name": "Coaxial cable", "part_file": "part3-conductors.json"},
    {"symbol_id": "CONDUCTOR_MINERAL", "iec_ref": "IEC60617-03-01-15", "iec_part": 3, "category": "conductor", "display_name": "Mineral insulated cable", "part_file": "part3-conductors.json"},
    {"symbol_id": "CABLE_DUCT", "iec_ref": "IEC60617-03-04-01", "iec_part": 3, "category": "conductor", "display_name": "Cable duct", "part_file": "part3-conductors.json"},
    {"symbol_id": "TRUNKING", "iec_ref": "IEC60617-03-04-02", "iec_part": 3, "category": "conductor", "display_name": "Cable trunking", "part_file": "part3-conductors.json"},
    {"symbol_id": "CONDUIT", "iec_ref": "IEC60617-03-04-03", "iec_part": 3, "category": "conductor", "display_name": "Conduit", "part_file": "part3-conductors.json"},
    {"symbol_id": "CABLE_LADDER", "iec_ref": "IEC60617-03-04-04", "iec_part": 3, "category": "conductor", "display_name": "Cable ladder", "part_file": "part3-conductors.json"},
    {"symbol_id": "BUSDUCT", "iec_ref": "IEC60617-03-04-05", "iec_part": 3, "category": "conductor", "display_name": "Busbar trunking / busduct", "part_file": "part3-conductors.json"},
    {"symbol_id": "JUNCTION_BOX_CONDUCTOR", "iec_ref": "IEC60617-03-05-01", "iec_part": 3, "category": "conductor", "display_name": "Conductor junction box", "part_file": "part3-conductors.json"},
    {"symbol_id": "CABLE_END_SEAL", "iec_ref": "IEC60617-03-05-02", "iec_part": 3, "category": "conductor", "display_name": "Cable end seal", "part_file": "part3-conductors.json"},
    {"symbol_id": "CONDUCTOR_LAPPED", "iec_ref": "IEC60617-03-01-16", "iec_part": 3, "category": "conductor", "display_name": "Lapped conductors", "part_file": "part3-conductors.json"},
    {"symbol_id": "CABLE_SPLICE", "iec_ref": "IEC60617-03-05-03", "iec_part": 3, "category": "conductor", "display_name": "Cable splice joint", "part_file": "part3-conductors.json"},

    {"symbol_id": "GENERATOR_GENERAL", "iec_ref": "IEC60617-06-04-01", "iec_part": 6, "category": "power", "display_name": "Generator (general)", "part_file": "part6-power.json"},
    {"symbol_id": "GENERATOR_SYNC", "iec_ref": "IEC60617-06-04-02", "iec_part": 6, "category": "power", "display_name": "Synchronous generator", "part_file": "part6-power.json"},
    {"symbol_id": "GENERATOR_INDUCTION", "iec_ref": "IEC60617-06-04-03", "iec_part": 6, "category": "power", "display_name": "Induction generator", "part_file": "part6-power.json"},
    {"symbol_id": "MOTOR_GENERAL", "iec_ref": "IEC60617-06-05-01", "iec_part": 6, "category": "power", "display_name": "Motor (general)", "part_file": "part6-power.json"},
    {"symbol_id": "MOTOR_INDUCTION", "iec_ref": "IEC60617-06-05-02", "iec_part": 6, "category": "power", "display_name": "Induction motor", "part_file": "part6-power.json"},
    {"symbol_id": "MOTOR_SYNC", "iec_ref": "IEC60617-06-05-03", "iec_part": 6, "category": "power", "display_name": "Synchronous motor", "part_file": "part6-power.json"},
    {"symbol_id": "MOTOR_DC", "iec_ref": "IEC60617-06-05-04", "iec_part": 6, "category": "power", "display_name": "DC motor", "part_file": "part6-power.json"},
    {"symbol_id": "TRANSFORMER_2W", "iec_ref": "IEC60617-06-09-01", "iec_part": 6, "category": "power", "display_name": "Two-winding transformer", "part_file": "part6-power.json"},
    {"symbol_id": "TRANSFORMER_3W", "iec_ref": "IEC60617-06-09-02", "iec_part": 6, "category": "power", "display_name": "Three-winding transformer", "part_file": "part6-power.json"},
    {"symbol_id": "TRANSFORMER_AUTO", "iec_ref": "IEC60617-06-09-03", "iec_part": 6, "category": "power", "display_name": "Autotransformer", "part_file": "part6-power.json"},
    {"symbol_id": "TRANSFORMER_CURRENT", "iec_ref": "IEC60617-06-09-05", "iec_part": 6, "category": "power", "display_name": "Current transformer (CT)", "part_file": "part6-power.json"},
    {"symbol_id": "TRANSFORMER_VOLTAGE", "iec_ref": "IEC60617-06-09-06", "iec_part": 6, "category": "power", "display_name": "Voltage transformer (VT)", "part_file": "part6-power.json"},
    {"symbol_id": "TRANSFORMER_1PH", "iec_ref": "IEC60617-06-09-04", "iec_part": 6, "category": "power", "display_name": "1-phase transformer", "part_file": "part6-power.json"},
    {"symbol_id": "TRANSFORMER_3PH", "iec_ref": "IEC60617-06-09-07", "iec_part": 6, "category": "power", "display_name": "3-phase transformer", "part_file": "part6-power.json"},
    {"symbol_id": "BATTERY", "iec_ref": "IEC60617-06-15-01", "iec_part": 6, "category": "power", "display_name": "Battery", "part_file": "part6-power.json"},
    {"symbol_id": "BATTERY_CHARGER", "iec_ref": "IEC60617-06-15-02", "iec_part": 6, "category": "power", "display_name": "Battery charger", "part_file": "part6-power.json"},
    {"symbol_id": "UPS", "iec_ref": "IEC60617-06-15-04", "iec_part": 6, "category": "power", "display_name": "UPS", "part_file": "part6-power.json"},
    {"symbol_id": "SOLAR_PV", "iec_ref": "IEC60617-06-16-01", "iec_part": 6, "category": "power", "display_name": "Photovoltaic source", "part_file": "part6-power.json"},
    {"symbol_id": "WIND_TURBINE", "iec_ref": "IEC60617-06-16-02", "iec_part": 6, "category": "power", "display_name": "Wind turbine", "part_file": "part6-power.json"},
    {"symbol_id": "CAPACITOR", "iec_ref": "IEC60617-06-04-04", "iec_part": 6, "category": "power", "display_name": "Capacitor", "part_file": "part6-power.json"},
    {"symbol_id": "CAPACITOR_BANK", "iec_ref": "IEC60617-06-06-01", "iec_part": 6, "category": "power", "display_name": "Capacitor bank (PFC)", "part_file": "part6-power.json"},
    {"symbol_id": "REACTOR_INDUCTOR", "iec_ref": "IEC60617-06-04-05", "iec_part": 6, "category": "power", "display_name": "Reactor / inductor", "part_file": "part6-power.json"},
    {"symbol_id": "RECTIFIER", "iec_ref": "IEC60617-06-12-01", "iec_part": 6, "category": "power", "display_name": "Rectifier (AC→DC)", "part_file": "part6-power.json"},
    {"symbol_id": "INVERTER", "iec_ref": "IEC60617-06-12-02", "iec_part": 6, "category": "power", "display_name": "Inverter (DC→AC)", "part_file": "part6-power.json"},
    {"symbol_id": "CONVERTER_DC_DC", "iec_ref": "IEC60617-06-12-03", "iec_part": 6, "category": "power", "display_name": "DC/DC converter", "part_file": "part6-power.json"},
    {"symbol_id": "CONVERTER_AC_DC", "iec_ref": "IEC60617-06-12-04", "iec_part": 6, "category": "power", "display_name": "AC/DC converter", "part_file": "part6-power.json"},
    {"symbol_id": "CONVERTER_DC_AC", "iec_ref": "IEC60617-06-12-05", "iec_part": 6, "category": "power", "display_name": "DC/AC converter", "part_file": "part6-power.json"},
    {"symbol_id": "RESISTOR", "iec_ref": "IEC60617-06-04-06", "iec_part": 6, "category": "power", "display_name": "Resistor", "part_file": "part6-power.json"},
    {"symbol_id": "EARTH_ELECTRODE", "iec_ref": "IEC60617-06-15-06", "iec_part": 6, "category": "power", "display_name": "Earth electrode", "part_file": "part6-power.json"},
    {"symbol_id": "FUEL_CELL", "iec_ref": "IEC60617-06-16-03", "iec_part": 6, "category": "power", "display_name": "Fuel cell", "part_file": "part6-power.json"},
    {"symbol_id": "STABILIZER", "iec_ref": "IEC60617-06-12-06", "iec_part": 6, "category": "power", "display_name": "Voltage stabiliser", "part_file": "part6-power.json"},
    {"symbol_id": "FREQUENCY_CONVERTER", "iec_ref": "IEC60617-06-12-07", "iec_part": 6, "category": "power", "display_name": "Frequency converter", "part_file": "part6-power.json"},
    {"symbol_id": "SOFT_STARTER", "iec_ref": "IEC60617-06-12-09", "iec_part": 6, "category": "power", "display_name": "Soft starter", "part_file": "part6-power.json"},
    {"symbol_id": "VFD", "iec_ref": "IEC60617-06-12-08", "iec_part": 6, "category": "power", "display_name": "Variable frequency drive (VFD)", "part_file": "part6-power.json"},
    {"symbol_id": "TRANSFORMER_PEC", "iec_ref": "IEC60617-06-09-08", "iec_part": 6, "category": "power", "display_name": "Transformer with earth point", "part_file": "part6-power.json"},

    {"symbol_id": "CONTACT_NO", "iec_ref": "IEC60617-07-01-01", "iec_part": 7, "category": "switching", "display_name": "Make contact (NO)", "part_file": "part7-switchgear.json"},
    {"symbol_id": "CONTACT_NC", "iec_ref": "IEC60617-07-01-02", "iec_part": 7, "category": "switching", "display_name": "Break contact (NC)", "part_file": "part7-switchgear.json"},
    {"symbol_id": "CONTACT_CHANGEOVER", "iec_ref": "IEC60617-07-01-03", "iec_part": 7, "category": "switching", "display_name": "Changeover contact (CO)", "part_file": "part7-switchgear.json"},
    {"symbol_id": "SWITCH_GENERAL", "iec_ref": "IEC60617-07-02-01", "iec_part": 7, "category": "switching", "display_name": "Switch (general)", "part_file": "part7-switchgear.json"},
    {"symbol_id": "SWITCH_1P", "iec_ref": "IEC60617-07-02-02", "iec_part": 7, "category": "switching", "display_name": "Single-pole switch", "part_file": "part7-switchgear.json"},
    {"symbol_id": "SWITCH_DISCONNECTOR_2P", "iec_ref": "IEC60617-07-13-01", "iec_part": 7, "category": "switching", "display_name": "2-pole switch-disconnector", "part_file": "part7-switchgear.json"},
    {"symbol_id": "SWITCH_DISCONNECTOR_3P", "iec_ref": "IEC60617-07-13-02", "iec_part": 7, "category": "switching", "display_name": "3-pole switch-disconnector", "part_file": "part7-switchgear.json"},
    {"symbol_id": "SWITCH_DISCONNECTOR_4P", "iec_ref": "IEC60617-07-13-03", "iec_part": 7, "category": "switching", "display_name": "4-pole switch-disconnector", "part_file": "part7-switchgear.json"},
    {"symbol_id": "BUS_SECTION_SWITCH", "iec_ref": "IEC60617-07-13-08", "iec_part": 7, "category": "switching", "display_name": "Bus section switch", "part_file": "part7-switchgear.json"},
    {"symbol_id": "ISOLATOR_2P", "iec_ref": "IEC60617-07-14-01", "iec_part": 7, "category": "switching", "display_name": "2-pole isolator", "part_file": "part7-switchgear.json"},
    {"symbol_id": "ISOLATOR_3P", "iec_ref": "IEC60617-07-14-02", "iec_part": 7, "category": "switching", "display_name": "3-pole isolator", "part_file": "part7-switchgear.json"},
    {"symbol_id": "ISOLATOR_4P", "iec_ref": "IEC60617-07-14-03", "iec_part": 7, "category": "switching", "display_name": "4-pole isolator", "part_file": "part7-switchgear.json"},
    {"symbol_id": "MCB_1P", "iec_ref": "IEC60617-07-18-01", "iec_part": 7, "category": "protection", "display_name": "1-Pole MCB", "part_file": "part7-switchgear.json"},
    {"symbol_id": "MCB_2P", "iec_ref": "IEC60617-07-18-02", "iec_part": 7, "category": "protection", "display_name": "2-Pole MCB", "part_file": "part7-switchgear.json"},
    {"symbol_id": "MCB_3P", "iec_ref": "IEC60617-07-18-03", "iec_part": 7, "category": "protection", "display_name": "3-Pole MCB", "part_file": "part7-switchgear.json"},
    {"symbol_id": "MCB_4P", "iec_ref": "IEC60617-07-18-04", "iec_part": 7, "category": "protection", "display_name": "4-Pole MCB", "part_file": "part7-switchgear.json"},
    {"symbol_id": "MCCB_3P", "iec_ref": "IEC60617-07-18-11", "iec_part": 7, "category": "protection", "display_name": "3-Pole MCCB", "part_file": "part7-switchgear.json"},
    {"symbol_id": "MCCB_4P", "iec_ref": "IEC60617-07-18-12", "iec_part": 7, "category": "protection", "display_name": "4-Pole MCCB", "part_file": "part7-switchgear.json"},
    {"symbol_id": "ACB_3P", "iec_ref": "IEC60617-07-18-21", "iec_part": 7, "category": "protection", "display_name": "3-Pole ACB", "part_file": "part7-switchgear.json"},
    {"symbol_id": "ACB_4P", "iec_ref": "IEC60617-07-18-22", "iec_part": 7, "category": "protection", "display_name": "4-Pole ACB", "part_file": "part7-switchgear.json"},
    {"symbol_id": "FUSE_1P", "iec_ref": "IEC60617-07-21-01", "iec_part": 7, "category": "protection", "display_name": "1-Pole fuse", "part_file": "part7-switchgear.json"},
    {"symbol_id": "FUSE_3P", "iec_ref": "IEC60617-07-21-02", "iec_part": 7, "category": "protection", "display_name": "3-Pole fuses", "part_file": "part7-switchgear.json"},
    {"symbol_id": "FUSE_SWITCH", "iec_ref": "IEC60617-07-21-04", "iec_part": 7, "category": "protection", "display_name": "Fuse-switch / switch-fuse", "part_file": "part7-switchgear.json"},
    {"symbol_id": "CONTACTOR_3P", "iec_ref": "IEC60617-07-19-01", "iec_part": 7, "category": "switching", "display_name": "3-Pole contactor", "part_file": "part7-switchgear.json"},
    {"symbol_id": "CONTACTOR_STAR_DELTA", "iec_ref": "IEC60617-07-19-02", "iec_part": 7, "category": "switching", "display_name": "Star-delta contactor set", "part_file": "part7-switchgear.json"},
    {"symbol_id": "RELAY_COIL", "iec_ref": "IEC60617-07-15-01", "iec_part": 7, "category": "switching", "display_name": "Relay coil", "part_file": "part7-switchgear.json"},
    {"symbol_id": "RELAY_THERMAL", "iec_ref": "IEC60617-07-15-02", "iec_part": 7, "category": "protection", "display_name": "Thermal overload relay", "part_file": "part7-switchgear.json"},
    {"symbol_id": "MCB_MOTOR", "iec_ref": "IEC60617-07-18-13", "iec_part": 7, "category": "protection", "display_name": "Motor circuit breaker (MPCB)", "part_file": "part7-switchgear.json"},
    {"symbol_id": "RCD_2P", "iec_ref": "IEC60617-07-22-01", "iec_part": 7, "category": "protection", "display_name": "2-Pole RCD (RCCB)", "part_file": "part7-switchgear.json"},
    {"symbol_id": "RCD_4P", "iec_ref": "IEC60617-07-22-02", "iec_part": 7, "category": "protection", "display_name": "4-Pole RCD (RCCB)", "part_file": "part7-switchgear.json"},
    {"symbol_id": "RCBO_1P", "iec_ref": "IEC60617-07-22-11", "iec_part": 7, "category": "protection", "display_name": "1-Pole RCBO", "part_file": "part7-switchgear.json"},
    {"symbol_id": "RCBO_2P", "iec_ref": "IEC60617-07-22-12", "iec_part": 7, "category": "protection", "display_name": "2-Pole RCBO", "part_file": "part7-switchgear.json"},
    {"symbol_id": "SPD_TYPE1", "iec_ref": "IEC60617-07-25-01", "iec_part": 7, "category": "protection", "display_name": "SPD Type 1", "part_file": "part7-switchgear.json"},
    {"symbol_id": "SPD_TYPE2", "iec_ref": "IEC60617-07-25-02", "iec_part": 7, "category": "protection", "display_name": "SPD Type 2", "part_file": "part7-switchgear.json"},
    {"symbol_id": "SPD_TYPE3", "iec_ref": "IEC60617-07-25-03", "iec_part": 7, "category": "protection", "display_name": "SPD Type 3", "part_file": "part7-switchgear.json"},
    {"symbol_id": "ATS_2WAY", "iec_ref": "IEC60617-07-26-01", "iec_part": 7, "category": "switching", "display_name": "ATS (2-way)", "part_file": "part7-switchgear.json"},
    {"symbol_id": "ATS_3WAY", "iec_ref": "IEC60617-07-26-02", "iec_part": 7, "category": "switching", "display_name": "ATS (3-way)", "part_file": "part7-switchgear.json"},
    {"symbol_id": "TRANSFER_SWITCH_MANUAL", "iec_ref": "IEC60617-07-26-03", "iec_part": 7, "category": "switching", "display_name": "Manual transfer switch", "part_file": "part7-switchgear.json"},
    {"symbol_id": "RELAY_EARTH_LEAKAGE", "iec_ref": "IEC60617-07-22-03", "iec_part": 7, "category": "protection", "display_name": "Earth leakage relay", "part_file": "part7-switchgear.json"},
    {"symbol_id": "CONTACT_INTERLOCK", "iec_ref": "IEC60617-07-08-02", "iec_part": 7, "category": "switching", "display_name": "Interlock contact", "part_file": "part7-switchgear.json"},
    {"symbol_id": "CONTACT_AUX_NO", "iec_ref": "IEC60617-07-08-03", "iec_part": 7, "category": "switching", "display_name": "Auxiliary contact (NO)", "part_file": "part7-switchgear.json"},
    {"symbol_id": "CONTACT_AUX_NC", "iec_ref": "IEC60617-07-08-04", "iec_part": 7, "category": "switching", "display_name": "Auxiliary contact (NC)", "part_file": "part7-switchgear.json"},
    {"symbol_id": "PUSHBUTTON_NO", "iec_ref": "IEC60617-07-07-01", "iec_part": 7, "category": "switching", "display_name": "Pushbutton (NO)", "part_file": "part7-switchgear.json"},
    {"symbol_id": "PUSHBUTTON_NC", "iec_ref": "IEC60617-07-07-02", "iec_part": 7, "category": "switching", "display_name": "Pushbutton (NC)", "part_file": "part7-switchgear.json"},
    {"symbol_id": "PUSHBUTTON_ILLUMINATED", "iec_ref": "IEC60617-07-07-03", "iec_part": 7, "category": "switching", "display_name": "Illuminated pushbutton", "part_file": "part7-switchgear.json"},
    {"symbol_id": "EMERGENCY_STOP", "iec_ref": "IEC60617-07-07-04", "iec_part": 7, "category": "switching", "display_name": "Emergency stop", "part_file": "part7-switchgear.json"},
    {"symbol_id": "KEY_SWITCH", "iec_ref": "IEC60617-07-07-06", "iec_part": 7, "category": "switching", "display_name": "Key switch", "part_file": "part7-switchgear.json"},
    {"symbol_id": "SELECTOR_SWITCH_2POS", "iec_ref": "IEC60617-07-07-07", "iec_part": 7, "category": "switching", "display_name": "Selector switch (2-position)", "part_file": "part7-switchgear.json"},
    {"symbol_id": "SELECTOR_SWITCH_3POS", "iec_ref": "IEC60617-07-07-08", "iec_part": 7, "category": "switching", "display_name": "Selector switch (3-position)", "part_file": "part7-switchgear.json"},
    {"symbol_id": "CONTACT_ON_DELAY", "iec_ref": "IEC60617-07-09-01", "iec_part": 7, "category": "switching", "display_name": "Time-delay contact (on-delay)", "part_file": "part7-switchgear.json"},
    {"symbol_id": "CONTACT_OFF_DELAY", "iec_ref": "IEC60617-07-09-02", "iec_part": 7, "category": "switching", "display_name": "Time-delay contact (off-delay)", "part_file": "part7-switchgear.json"},
    {"symbol_id": "DISCONNECT_HANDLE", "iec_ref": "IEC60617-07-13-09", "iec_part": 7, "category": "switching", "display_name": "Manual disconnect handle", "part_file": "part7-switchgear.json"},
    {"symbol_id": "LIMITER_CURRENT", "iec_ref": "IEC60617-07-21-05", "iec_part": 7, "category": "protection", "display_name": "Current limiter", "part_file": "part7-switchgear.json"},
    {"symbol_id": "LIMITER_VOLTAGE", "iec_ref": "IEC60617-07-25-04", "iec_part": 7, "category": "protection", "display_name": "Voltage limiter", "part_file": "part7-switchgear.json"},
    {"symbol_id": "RELAY_OVERCURRENT", "iec_ref": "IEC60617-07-15-04", "iec_part": 7, "category": "protection", "display_name": "Overcurrent relay", "part_file": "part7-switchgear.json"},
    {"symbol_id": "RELAY_UNDERVOLTAGE", "iec_ref": "IEC60617-07-15-05", "iec_part": 7, "category": "protection", "display_name": "Undervoltage relay", "part_file": "part7-switchgear.json"},
    {"symbol_id": "RELAY_DIFFERENTIAL", "iec_ref": "IEC60617-07-15-06", "iec_part": 7, "category": "protection", "display_name": "Differential relay", "part_file": "part7-switchgear.json"},
    {"symbol_id": "MOTOR_STARTER_DOL", "iec_ref": "IEC60617-07-19-03", "iec_part": 7, "category": "switching", "display_name": "DOL motor starter", "part_file": "part7-switchgear.json"},
    {"symbol_id": "MOTOR_STARTER_SD", "iec_ref": "IEC60617-07-19-04", "iec_part": 7, "category": "switching", "display_name": "Star-delta motor starter", "part_file": "part7-switchgear.json"},
    {"symbol_id": "MOTOR_STARTER_VFD", "iec_ref": "IEC60617-07-19-05", "iec_part": 7, "category": "switching", "display_name": "VFD motor starter", "part_file": "part7-switchgear.json"},
    {"symbol_id": "SWITCH_PRESSURE", "iec_ref": "IEC60617-07-03-01", "iec_part": 7, "category": "switching", "display_name": "Pressure switch", "part_file": "part7-switchgear.json"},
    {"symbol_id": "SWITCH_TEMPERATURE", "iec_ref": "IEC60617-07-03-02", "iec_part": 7, "category": "switching", "display_name": "Temperature switch (thermostat)", "part_file": "part7-switchgear.json"},
    {"symbol_id": "SWITCH_FLOAT", "iec_ref": "IEC60617-07-03-03", "iec_part": 7, "category": "switching", "display_name": "Float switch", "part_file": "part7-switchgear.json"},
    {"symbol_id": "SWITCH_LEVEL", "iec_ref": "IEC60617-07-03-04", "iec_part": 7, "category": "switching", "display_name": "Level switch", "part_file": "part7-switchgear.json"},
    {"symbol_id": "CIRCUIT_BREAKER_GENERAL", "iec_ref": "IEC60617-07-18-00", "iec_part": 7, "category": "protection", "display_name": "Circuit-breaker (general)", "part_file": "part7-switchgear.json"},
    {"symbol_id": "DISCONNECTOR_GENERAL", "iec_ref": "IEC60617-07-14-00", "iec_part": 7, "category": "switching", "display_name": "Disconnector (general)", "part_file": "part7-switchgear.json"},
    {"symbol_id": "CONTACTOR_GENERAL", "iec_ref": "IEC60617-07-19-00", "iec_part": 7, "category": "switching", "display_name": "Contactor (general)", "part_file": "part7-switchgear.json"},
    {"symbol_id": "RELAY_GENERAL", "iec_ref": "IEC60617-07-15-00", "iec_part": 7, "category": "switching", "display_name": "Relay (general)", "part_file": "part7-switchgear.json"},
    {"symbol_id": "SWITCH_ISOLATING", "iec_ref": "IEC60617-07-02-03", "iec_part": 7, "category": "switching", "display_name": "Isolating switch", "part_file": "part7-switchgear.json"},
    {"symbol_id": "LINK_REMOVABLE", "iec_ref": "IEC60617-07-04-01", "iec_part": 7, "category": "switching", "display_name": "Removable link", "part_file": "part7-switchgear.json"},

    {"symbol_id": "AMMETER", "iec_ref": "IEC60617-08-01-01", "iec_part": 8, "category": "measurement", "display_name": "Ammeter", "part_file": "part8-measurement.json"},
    {"symbol_id": "VOLTMETER", "iec_ref": "IEC60617-08-01-02", "iec_part": 8, "category": "measurement", "display_name": "Voltmeter", "part_file": "part8-measurement.json"},
    {"symbol_id": "WATTMETER", "iec_ref": "IEC60617-08-01-03", "iec_part": 8, "category": "measurement", "display_name": "Wattmeter", "part_file": "part8-measurement.json"},
    {"symbol_id": "VAR_METER", "iec_ref": "IEC60617-08-01-04", "iec_part": 8, "category": "measurement", "display_name": "VAR meter", "part_file": "part8-measurement.json"},
    {"symbol_id": "POWER_FACTOR_METER", "iec_ref": "IEC60617-08-01-05", "iec_part": 8, "category": "measurement", "display_name": "Power factor meter", "part_file": "part8-measurement.json"},
    {"symbol_id": "FREQUENCY_METER", "iec_ref": "IEC60617-08-01-06", "iec_part": 8, "category": "measurement", "display_name": "Frequency meter", "part_file": "part8-measurement.json"},
    {"symbol_id": "ENERGY_METER_KWH", "iec_ref": "IEC60617-08-02-01", "iec_part": 8, "category": "measurement", "display_name": "Energy meter (kWh)", "part_file": "part8-measurement.json"},
    {"symbol_id": "ENERGY_METER_KVARH", "iec_ref": "IEC60617-08-02-02", "iec_part": 8, "category": "measurement", "display_name": "Reactive energy meter (kVArh)", "part_file": "part8-measurement.json"},
    {"symbol_id": "SMART_METER", "iec_ref": "IEC60617-08-02-03", "iec_part": 8, "category": "measurement", "display_name": "Smart meter (AMR)", "part_file": "part8-measurement.json"},
    {"symbol_id": "CT_METERING", "iec_ref": "IEC60617-08-03-01", "iec_part": 8, "category": "measurement", "display_name": "CT (metering class)", "part_file": "part8-measurement.json"},
    {"symbol_id": "VT_METERING", "iec_ref": "IEC60617-08-03-02", "iec_part": 8, "category": "measurement", "display_name": "VT (metering class)", "part_file": "part8-measurement.json"},
    {"symbol_id": "MULTIFUNCTION_METER", "iec_ref": "IEC60617-08-02-04", "iec_part": 8, "category": "measurement", "display_name": "Multifunction meter", "part_file": "part8-measurement.json"},
    {"symbol_id": "INDICATOR_LAMP", "iec_ref": "IEC60617-08-04-01", "iec_part": 8, "category": "measurement", "display_name": "Indicator lamp", "part_file": "part8-measurement.json"},
    {"symbol_id": "INDICATOR_LAMP_R", "iec_ref": "IEC60617-08-04-02", "iec_part": 8, "category": "measurement", "display_name": "Indicator lamp (red)", "part_file": "part8-measurement.json"},
    {"symbol_id": "INDICATOR_LAMP_G", "iec_ref": "IEC60617-08-04-03", "iec_part": 8, "category": "measurement", "display_name": "Indicator lamp (green)", "part_file": "part8-measurement.json"},
    {"symbol_id": "INDICATOR_LAMP_A", "iec_ref": "IEC60617-08-04-04", "iec_part": 8, "category": "measurement", "display_name": "Indicator lamp (amber)", "part_file": "part8-measurement.json"},
    {"symbol_id": "LED_INDICATOR", "iec_ref": "IEC60617-08-04-05", "iec_part": 8, "category": "measurement", "display_name": "LED indicator", "part_file": "part8-measurement.json"},
    {"symbol_id": "BUZZER", "iec_ref": "IEC60617-08-05-01", "iec_part": 8, "category": "measurement", "display_name": "Buzzer", "part_file": "part8-measurement.json"},
    {"symbol_id": "HORN", "iec_ref": "IEC60617-08-05-02", "iec_part": 8, "category": "measurement", "display_name": "Horn / siren", "part_file": "part8-measurement.json"},
    {"symbol_id": "BELL", "iec_ref": "IEC60617-08-05-03", "iec_part": 8, "category": "measurement", "display_name": "Bell", "part_file": "part8-measurement.json"},
    {"symbol_id": "ALARM_AUDIBLE", "iec_ref": "IEC60617-08-05-04", "iec_part": 8, "category": "measurement", "display_name": "Audible alarm", "part_file": "part8-measurement.json"},
    {"symbol_id": "ALARM_VISUAL", "iec_ref": "IEC60617-08-05-05", "iec_part": 8, "category": "measurement", "display_name": "Visual alarm (strobe)", "part_file": "part8-measurement.json"},
    {"symbol_id": "LUMINAIRE_GENERAL", "iec_ref": "IEC60617-08-04-10", "iec_part": 8, "category": "measurement", "display_name": "Luminaire (general)", "part_file": "part8-measurement.json"},
    {"symbol_id": "OSCILLOSCOPE", "iec_ref": "IEC60617-08-06-01", "iec_part": 8, "category": "measurement", "display_name": "Oscilloscope", "part_file": "part8-measurement.json"},
    {"symbol_id": "POWER_ANALYSER", "iec_ref": "IEC60617-08-06-02", "iec_part": 8, "category": "measurement", "display_name": "Power quality analyser", "part_file": "part8-measurement.json"},
    {"symbol_id": "SIGNAL_GENERATOR", "iec_ref": "IEC60617-08-06-03", "iec_part": 8, "category": "measurement", "display_name": "Signal generator", "part_file": "part8-measurement.json"},
    {"symbol_id": "TRANSDUCER_CURRENT", "iec_ref": "IEC60617-08-07-01", "iec_part": 8, "category": "measurement", "display_name": "Current transducer", "part_file": "part8-measurement.json"},
    {"symbol_id": "TRANSDUCER_VOLTAGE", "iec_ref": "IEC60617-08-07-02", "iec_part": 8, "category": "measurement", "display_name": "Voltage transducer", "part_file": "part8-measurement.json"},
    {"symbol_id": "RECORDER", "iec_ref": "IEC60617-08-06-04", "iec_part": 8, "category": "measurement", "display_name": "Recorder", "part_file": "part8-measurement.json"},
    {"symbol_id": "TOTALISER", "iec_ref": "IEC60617-08-02-05", "iec_part": 8, "category": "measurement", "display_name": "Totaliser", "part_file": "part8-measurement.json"},

    {"symbol_id": "DB_GENERAL", "iec_ref": "IEC60617-11-04-01", "iec_part": 11, "category": "architectural", "display_name": "Distribution board (general)", "part_file": "part11-architectural.json"},
    {"symbol_id": "DB_MAIN", "iec_ref": "IEC60617-11-04-02", "iec_part": 11, "category": "architectural", "display_name": "Main LV switchboard (MSB)", "part_file": "part11-architectural.json"},
    {"symbol_id": "CONSUMER_UNIT", "iec_ref": "IEC60617-11-04-03", "iec_part": 11, "category": "architectural", "display_name": "Consumer unit", "part_file": "part11-architectural.json"},
    {"symbol_id": "DB_SUB", "iec_ref": "IEC60617-11-04-04", "iec_part": 11, "category": "architectural", "display_name": "Sub-distribution board (SDB)", "part_file": "part11-architectural.json"},
    {"symbol_id": "PANEL_GENERATOR", "iec_ref": "IEC60617-11-04-05", "iec_part": 11, "category": "architectural", "display_name": "Generator control panel", "part_file": "part11-architectural.json"},
    {"symbol_id": "PANEL_UPS", "iec_ref": "IEC60617-11-04-06", "iec_part": 11, "category": "architectural", "display_name": "UPS panel", "part_file": "part11-architectural.json"},
    {"symbol_id": "SOCKET_SINGLE", "iec_ref": "IEC60617-11-15-01", "iec_part": 11, "category": "architectural", "display_name": "Single socket outlet", "part_file": "part11-architectural.json"},
    {"symbol_id": "SOCKET_DOUBLE", "iec_ref": "IEC60617-11-15-02", "iec_part": 11, "category": "architectural", "display_name": "Double socket outlet", "part_file": "part11-architectural.json"},
    {"symbol_id": "SOCKET_SWITCHED_SINGLE", "iec_ref": "IEC60617-11-15-03", "iec_part": 11, "category": "architectural", "display_name": "Switched single socket", "part_file": "part11-architectural.json"},
    {"symbol_id": "SOCKET_SWITCHED_DOUBLE", "iec_ref": "IEC60617-11-15-04", "iec_part": 11, "category": "architectural", "display_name": "Switched double socket", "part_file": "part11-architectural.json"},
    {"symbol_id": "SOCKET_INDUSTRIAL_IP44", "iec_ref": "IEC60617-11-15-05", "iec_part": 11, "category": "architectural", "display_name": "Industrial socket (IP44, 16A)", "part_file": "part11-architectural.json"},
    {"symbol_id": "SOCKET_INDUSTRIAL_IP67", "iec_ref": "IEC60617-11-15-06", "iec_part": 11, "category": "architectural", "display_name": "Industrial socket (IP67, 16A)", "part_file": "part11-architectural.json"},
    {"symbol_id": "SOCKET_3PHASE", "iec_ref": "IEC60617-11-15-07", "iec_part": 11, "category": "architectural", "display_name": "3-phase socket outlet", "part_file": "part11-architectural.json"},
    {"symbol_id": "SOCKET_COMMANDO_32A", "iec_ref": "IEC60617-11-15-08", "iec_part": 11, "category": "architectural", "display_name": "Commando socket (32A)", "part_file": "part11-architectural.json"},
    {"symbol_id": "LUMINAIRE_ARCH", "iec_ref": "IEC60617-11-09-01", "iec_part": 11, "category": "architectural", "display_name": "Luminaire (general, plan)", "part_file": "part11-architectural.json"},
    {"symbol_id": "LUMINAIRE_EMERGENCY", "iec_ref": "IEC60617-11-09-02", "iec_part": 11, "category": "architectural", "display_name": "Emergency luminaire", "part_file": "part11-architectural.json"},
    {"symbol_id": "LUMINAIRE_RECESSED", "iec_ref": "IEC60617-11-09-03", "iec_part": 11, "category": "architectural", "display_name": "Recessed luminaire", "part_file": "part11-architectural.json"},
    {"symbol_id": "LUMINAIRE_EXTERIOR", "iec_ref": "IEC60617-11-09-04", "iec_part": 11, "category": "architectural", "display_name": "External luminaire", "part_file": "part11-architectural.json"},
    {"symbol_id": "SWITCH_1WAY", "iec_ref": "IEC60617-11-12-01", "iec_part": 11, "category": "architectural", "display_name": "1-way switch", "part_file": "part11-architectural.json"},
    {"symbol_id": "SWITCH_2WAY", "iec_ref": "IEC60617-11-12-02", "iec_part": 11, "category": "architectural", "display_name": "2-way switch", "part_file": "part11-architectural.json"},
    {"symbol_id": "SWITCH_INTERMEDIATE", "iec_ref": "IEC60617-11-12-03", "iec_part": 11, "category": "architectural", "display_name": "Intermediate switch", "part_file": "part11-architectural.json"},
    {"symbol_id": "SWITCH_DIMMER", "iec_ref": "IEC60617-11-12-04", "iec_part": 11, "category": "architectural", "display_name": "Dimmer switch", "part_file": "part11-architectural.json"},
    {"symbol_id": "SENSOR_PIR", "iec_ref": "IEC60617-11-13-01", "iec_part": 11, "category": "architectural", "display_name": "PIR sensor", "part_file": "part11-architectural.json"},
    {"symbol_id": "SENSOR_OCCUPANCY", "iec_ref": "IEC60617-11-13-02", "iec_part": 11, "category": "architectural", "display_name": "Occupancy sensor", "part_file": "part11-architectural.json"},
    {"symbol_id": "SENSOR_DAYLIGHT", "iec_ref": "IEC60617-11-13-03", "iec_part": 11, "category": "architectural", "display_name": "Daylight sensor / photocell", "part_file": "part11-architectural.json"},
    {"symbol_id": "DETECTOR_SMOKE", "iec_ref": "IEC60617-11-14-01", "iec_part": 11, "category": "architectural", "display_name": "Smoke detector", "part_file": "part11-architectural.json"},
    {"symbol_id": "DETECTOR_HEAT", "iec_ref": "IEC60617-11-14-02", "iec_part": 11, "category": "architectural", "display_name": "Heat detector", "part_file": "part11-architectural.json"},
    {"symbol_id": "CALL_POINT_MANUAL", "iec_ref": "IEC60617-11-14-03", "iec_part": 11, "category": "architectural", "display_name": "Manual call point (MCP)", "part_file": "part11-architectural.json"},
    {"symbol_id": "JUNCTION_BOX", "iec_ref": "IEC60617-11-05-01", "iec_part": 11, "category": "architectural", "display_name": "Junction box (plan)", "part_file": "part11-architectural.json"},
    {"symbol_id": "CABLE_ROUTE_GENERAL", "iec_ref": "IEC60617-11-06-01", "iec_part": 11, "category": "architectural", "display_name": "Cable route (general)", "part_file": "part11-architectural.json"},
    {"symbol_id": "CABLE_ROUTE_CONCEALED", "iec_ref": "IEC60617-11-06-02", "iec_part": 11, "category": "architectural", "display_name": "Concealed cable route", "part_file": "part11-architectural.json"},
    {"symbol_id": "CABLE_ROUTE_SURFACE", "iec_ref": "IEC60617-11-06-03", "iec_part": 11, "category": "architectural", "display_name": "Surface trunking route", "part_file": "part11-architectural.json"},
    {"symbol_id": "CABLE_ROUTE_OVERHEAD", "iec_ref": "IEC60617-11-06-04", "iec_part": 11, "category": "architectural", "display_name": "Overhead cable route", "part_file": "part11-architectural.json"},
    {"symbol_id": "CABLE_ROUTE_UNDERGROUND", "iec_ref": "IEC60617-11-06-05", "iec_part": 11, "category": "architectural", "display_name": "Underground cable route", "part_file": "part11-architectural.json"},
    {"symbol_id": "MOTOR_CONNECTION", "iec_ref": "IEC60617-11-08-01", "iec_part": 11, "category": "architectural", "display_name": "Motor connection point", "part_file": "part11-architectural.json"},
    {"symbol_id": "EV_CHARGING_POINT", "iec_ref": "IEC60617-11-15-10", "iec_part": 11, "category": "architectural", "display_name": "EV charging point", "part_file": "part11-architectural.json"}
  ]
}
```

- [ ] **Step 2: Validate JSON syntax**

Run: `python3 -c "import json; json.load(open('shared/standards/electrical/IEC60617/symbol-index.json'))" && echo OK`
Expected: `OK`

- [ ] **Step 3: Verify symbol count matches sum of part files**

Run:
```bash
python3 - <<'PY'
import json
idx = json.load(open('shared/standards/electrical/IEC60617/symbol-index.json'))
n_idx = len(idx['symbols'])
parts = ['part2-general.json', 'part3-conductors.json', 'part6-power.json', 'part7-switchgear.json', 'part8-measurement.json', 'part11-architectural.json']
n_parts = sum(len(json.load(open('shared/standards/electrical/IEC60617/' + p))['symbols']) for p in parts)
print(f'index: {n_idx}, part files total: {n_parts}', 'OK' if n_idx == n_parts == 226 else 'MISMATCH')
PY
```
Expected: `index: 226, part files total: 226 OK`

- [ ] **Step 4: Verify every index symbol exists in its declared part file**

Run:
```bash
python3 - <<'PY'
import json
idx = json.load(open('shared/standards/electrical/IEC60617/symbol-index.json'))
errs = []
for entry in idx['symbols']:
    pf = json.load(open('shared/standards/electrical/IEC60617/' + entry['part_file']))
    if not any(s['symbol_id'] == entry['symbol_id'] for s in pf['symbols']):
        errs.append(entry['symbol_id'])
print('OK' if not errs else 'NOT_FOUND:' + str(errs))
PY
```
Expected: `OK`

- [ ] **Step 5: Commit**

```bash
git add shared/standards/electrical/IEC60617/symbol-index.json
git commit -m "feat: IEC60617 symbol-index.json — flat lookup of all 226 symbols"
```

---

## Task 13: Create symbol-usage-guide.md

**Files:**
- Create: `shared/standards/electrical/IEC60617/symbol-usage-guide.md`

- [ ] **Step 1: Write the file**

````markdown
# IEC 60617 — Symbol Usage Guide

This guide tells you which symbol to pick, when to use it, and what to annotate. It complements the per-symbol `usage_notes` field in the part files by covering combinations and common pitfalls that only become clear when you look at a complete drawing.

---

## Choosing the Right Symbol: Decision Trees

### Protective device on a final circuit

```
Is the circuit a socket outlet circuit or wet-area?
├─ YES → RCBO_1P / RCBO_2P (combined MCB + RCD in one device)
└─ NO  → Is the circuit a motor circuit ≤ 32A?
         ├─ YES → MCB_MOTOR (combined thermal + magnetic in one device)
         └─ NO  → MCB_1P / MCB_2P / MCB_3P / MCB_4P (per pole count)
```

### Protective device at a sub-DB incomer

```
Is the rated current ≤ 100A?
├─ YES → MCB_3P or MCB_4P (per pole count)
└─ NO  → Is the rated current ≤ 1600A?
         ├─ YES → MCCB_3P / MCCB_4P
         └─ NO  → ACB_3P / ACB_4P
```

### Protective device at a main switchboard incomer

```
Always ACB_3P or ACB_4P (≥ 800A typical).
Annotate trip unit type. Short-time delay setting must coordinate with
downstream MCCBs.
```

### Earth symbol on an SLD

```
Building main earthing terminal (MET)
├─ EARTH_GENERAL — general-purpose earth point
Sensitive equipment / data centre / hospital Group 2
├─ EARTH_CLEAN — separate clean earth (triangle shape)
Exposed-conductive-part of Class I equipment
├─ EARTH_PROTECTIVE — the PE bond
Buried electrode (rod, plate, mesh)
├─ EARTH_ELECTRODE — the physical buried electrode (triangle with arrow)
```

### Switch symbol on a plan

```
Lighting circuit control:
├─ Single location → SWITCH_1WAY
├─ Two locations (e.g. stairs) → pair of SWITCH_2WAY
├─ Three or more locations → 2× SWITCH_2WAY + 1+ SWITCH_INTERMEDIATE
├─ Dimming → SWITCH_DIMMER
Sensors (replace manual switches for energy-saving control):
├─ Movement detection → SENSOR_PIR (cheap) or SENSOR_OCCUPANCY (dual-tech)
├─ Daylight detection → SENSOR_DAYLIGHT (often combined with PIR)
```

---

## Drawing Conventions Used by DraftsMan Skills

### SLD conventions (electrical/sld)

1. **Single-line representation.** Each circuit is drawn as a single line, regardless of pole count. Pole count is annotated on the protective device symbol.
2. **Line thickness.** Busbars are drawn at heavier line weight than circuits. Use the runtime's `E-BUS` layer for busbars (4× thickness).
3. **Annotation position.** Annotations sit above the conductor (rating, CSA) or to the right of the device (circuit label).
4. **Direction.** SLDs are normally drawn with the source at the top, loads at the bottom (gravity convention).
5. **Layer mapping.** Each symbol category maps to a CAD layer — see README.md.

### Schematic conventions (electrical/schematic)

1. **Multi-line representation.** All conductors of a circuit are drawn separately (L1, L2, L3, N, PE).
2. **Reading direction.** Schematics read left-to-right (source on the left, load on the right). Control circuits below power circuits.
3. **Contact placement.** Contacts of the same device may be split across the schematic — link them by tag (e.g. K1.1, K1.2).
4. **Layer mapping.** Same category-to-layer mapping as SLDs.

### Architectural plan conventions (electrical/lighting-layout, small-power, etc.)

1. **Plan-view symbols only.** Use Part 11 symbols, not Part 7 schematic symbols, on architectural plans.
2. **Cable routes.** Use `CABLE_ROUTE_*` variants to indicate concealed/surface/overhead/underground.
3. **Scale.** Plan-view symbols are drawn at a fixed paper size regardless of drawing scale (typically 5mm at 1:50, 10mm at 1:100).
4. **Annotation.** Circuit reference labels (DB-1.1, DB-1.2 …) placed adjacent to outlets.

---

## Common Symbol Combinations

### Final socket outlet circuit (single phase, RCD-protected)

```
[CONDUCTOR_SINGLE] — [RCBO_1P] — [CABLE_ROUTE_*] — [SOCKET_DOUBLE]
```

Annotations:
- RCBO: `In_A`, `IDn_mA` (30mA), `curve` (typically B), `type` (typically A)
- Cable route: circuit ID
- Socket: type (BS1363 13A typical)

### 3-phase motor circuit (DOL start)

```
[BUSBAR_3PH] — [MCB_MOTOR or MCCB_3P]
            — [CONTACTOR_3P]
            — [RELAY_THERMAL]
            — [CONDUCTOR_3CORE]
            — [MOTOR_INDUCTION or MOTOR_CONNECTION]
```

Or use the composite `MOTOR_STARTER_DOL` instead of the three discrete devices.

Annotations:
- MCCB / MPCB: `In_A`, `Im_setting`
- Contactor: `AC3_kW` (must match motor rating)
- Thermal relay: `set_A_range` covering motor FLC
- Motor: `rating_kW`, `voltage_V`, `rpm`

### Main DB incomer with surge protection

```
[BUSBAR_3PH] — [ACB_4P]
            — [SPD_TYPE2 (parallel to earth)]
            — [BUSBAR_3PH (loads)]
```

Annotations:
- ACB: `In_A`, `Icu_kA`, `trip_unit`
- SPD: `In_kA`, `Up_kV`, `Uc_V` (typically Uc = 275V for 230/400V system)

### CT-VT metering chain

```
Power conductor: [BUSBAR_3PH] — [CT_METERING (×3)] — [BUSBAR_3PH]
Voltage tap:     [BUSBAR_3PH] — [VT_METERING (×3)] — [MULTIFUNCTION_METER]
Current input:                 [CT_METERING] — [MULTIFUNCTION_METER]
```

Annotations:
- CT: `ratio` (e.g. 400/5), `class` 0.5
- VT: `ratio` 11000/110 (HV) or 400/110 (LV)
- Meter: functions list

### Generator + utility ATS

```
[Utility supply] — [ACB_4P (utility incomer)] —┐
                                                ├─ [ATS_2WAY] — [DB_MAIN]
[GENERATOR_SYNC] — [ACB_4P (genset incomer)] —┘
```

Annotations:
- ATS: `rated_A`, `transfer_time_s`
- Genset: `rating_kVA`, `voltage_V`, `pf`

---

## Mistakes to Avoid

### Mistake 1: Stacking 1-pole symbols for a 3-phase circuit

Do not draw three `MCB_1P` symbols side by side to represent a 3-pole MCB. Use `MCB_3P`. Three separate 1-pole devices have separate operating mechanisms and do not give simultaneous interruption — they are not equivalent.

### Mistake 2: Confusing isolator and switch-disconnector

`ISOLATOR_*` cannot break load current — it is a visible-break device only, operated off-load. `SWITCH_DISCONNECTOR_*` can break load current and is suitable for normal switching duty. A circuit's main switch is almost always a switch-disconnector, not a plain isolator.

### Mistake 3: Missing terminal labels on detailed schematics

On Part 7 contact symbols, label the terminals (e.g. 13/14 for NO, 11/12 for NC, A1/A2 for coil). The skill validation will flag missing terminal labels on schematic outputs.

### Mistake 4: Wrong category symbol on the wrong drawing type

`MCB_1P` (Part 7) is for SLDs and schematics. `SOCKET_SWITCHED_DOUBLE` (Part 11) is for architectural plans. Don't put `SOCKET_SWITCHED_DOUBLE` on an SLD — represent the outlet on the SLD as a generic load with a circuit annotation; show the socket on the plan.

### Mistake 5: Confusing PE/N/PEN

- `CONDUCTOR_PE` — separate PE only (TN-S, downstream of MET).
- `CONDUCTOR_N` — separate N only (TN-S).
- `CONDUCTOR_PEN` — combined (TN-C, only upstream of MET; in IEC 60364 terms only in the supply side of a TN-C-S installation).
- Once PEN has been separated into PE and N, never recombine them downstream.

### Mistake 6: Drawing both an RCD and an RCBO on the same circuit

`RCBO_1P` is a combined MCB + RCD. Don't pair it with a separate `RCD_2P` upstream — they will trip together and lose discrimination. The pairing only makes sense if the upstream RCD is selective (type S) and the RCBO is general type.

### Mistake 7: Forgetting the SPD earth lead

Every SPD needs an explicit earth connection. The SPD symbols have an `earth` terminal — draw the path from the SPD body to the local earth bar. Don't leave it floating.

---

## When Two Symbols Are Almost the Same

| Pair | Distinction |
|---|---|
| `TRANSFORMER_2W` (Part 6) vs `VT_METERING` (Part 8) | TRANSFORMER_2W is a power transformer (kVA scale); VT_METERING is a small measuring VT (VA scale) used with a meter. |
| `TRANSFORMER_CURRENT` (Part 6) vs `CT_METERING` (Part 8) | Same geometry; the metering form has a defined accuracy class. Use the metering form when the CT feeds a revenue meter. |
| `LUMINAIRE_GENERAL` (Part 8) vs `LUMINAIRE_ARCH` (Part 11) | Part 8 is the schematic-side symbol (on a control schematic, a wiring diagram). Part 11 is the architectural plan-view symbol. |
| `JUNCTION_BOX_CONDUCTOR` (Part 3) vs `JUNCTION_BOX` (Part 11) | Part 3 is the schematic in-line junction. Part 11 is the plan-view junction box. |
| `MOTOR_INDUCTION` (Part 6) vs `MOTOR_CONNECTION` (Part 11) | Part 6 is the schematic motor (with circle, label MA). Part 11 is the plan-view motor connection point. |
| `SWITCH_1P` (Part 7) vs `SWITCH_1WAY` (Part 11) | Part 7 is the schematic single-pole switch. Part 11 is the plan-view 1-way wall switch (circle). |

When in doubt: schematic drawings use Part 7 / Part 8 symbols; architectural floor plans use Part 11 symbols; cable section views use Part 3 symbols.

---

## Annotation Quick Reference

Every device on an SLD or schematic should be annotated with the fields listed in its `annotation_fields` array. Common patterns:

| Device type | Required annotations |
|---|---|
| MCB / MCCB / ACB | In_A, curve (B/C/D), Icu_kA |
| Fuse | In_A, fuse type (gG, aM, gF, BS88) |
| RCD / RCBO | In_A, IDn_mA, type (AC, A, F, B) |
| Contactor | AC3_kW, coil voltage |
| Transformer | kVA, primary V, secondary V, vector group, uk% |
| Motor | kW, voltage, rpm |
| Cable | csa_mm² (e.g. 4mm²), insulation (e.g. XLPE/SWA), length |
| SPD | type (1/2/3), In_kA or Iimp_kA, Up_kV, Uc_V |

The skill validation routines load each part file and check the drawing IR for the listed annotation fields. Missing fields generate a warning in the skill output.
````

- [ ] **Step 2: Commit**

```bash
git add shared/standards/electrical/IEC60617/symbol-usage-guide.md
git commit -m "docs: IEC60617 symbol usage guide — decision trees, conventions, common pitfalls"
```

---

## Task 14: Final verification and layer-level commit

**Files:**
- Verify: full `shared/standards/electrical/IEC60617/` directory

- [ ] **Step 1: Verify all 12 files are present**

Run:
```bash
ls -la shared/standards/electrical/IEC60617/
```
Expected: 12 files —
- README.md
- meta.json
- symbol-index.json
- part2-general.json
- part3-conductors.json
- part6-power.json
- part7-switchgear.json
- part8-measurement.json
- part11-architectural.json
- symbol-usage-guide.md
- geometry-encoding.md
- amendments-summary.md

- [ ] **Step 2: Verify all JSON files are valid**

Run:
```bash
for f in shared/standards/electrical/IEC60617/*.json; do
  python3 -c "import json; json.load(open('$f'))" && echo "$f OK" || echo "$f FAIL"
done
```
Expected: every line ends with `OK`.

- [ ] **Step 3: Verify total symbol count is 226**

Run:
```bash
python3 - <<'PY'
import json, glob
total = 0
for f in sorted(glob.glob('shared/standards/electrical/IEC60617/part*.json')):
    d = json.load(open(f))
    n = len(d['symbols'])
    total += n
    print(f'{f}: {n}')
print(f'TOTAL: {total}')
PY
```
Expected:
```
…/part11-architectural.json: 36
…/part2-general.json: 25
…/part3-conductors.json: 30
…/part6-power.json: 35
…/part7-switchgear.json: 70
…/part8-measurement.json: 30
TOTAL: 226
```

- [ ] **Step 4: Verify symbol-index.json is consistent with part files**

Run:
```bash
python3 - <<'PY'
import json, glob
idx = json.load(open('shared/standards/electrical/IEC60617/symbol-index.json'))
idx_ids = sorted(s['symbol_id'] for s in idx['symbols'])
part_ids = []
for f in sorted(glob.glob('shared/standards/electrical/IEC60617/part*.json')):
    d = json.load(open(f))
    part_ids.extend(s['symbol_id'] for s in d['symbols'])
part_ids = sorted(part_ids)
missing_from_index = set(part_ids) - set(idx_ids)
missing_from_parts = set(idx_ids) - set(part_ids)
print('OK' if not missing_from_index and not missing_from_parts else f'MISMATCH: missing from index {missing_from_index}, missing from parts {missing_from_parts}')
PY
```
Expected: `OK`

- [ ] **Step 5: Verify SLD manifest no longer references the moved file**

Run:
```bash
grep -c "standard-symbols-reference.md" electrical/sld/skill.manifest.json
```
Expected: `0`

- [ ] **Step 6: Verify the moved file is in its new location**

Run:
```bash
test -f electrical/sld/assets/standard-symbols-reference.md && echo OK || echo MISSING
test ! -f shared/standards/electrical/IEC60617/standard-symbols-reference.md && echo OK || echo "STILL EXISTS"
```
Expected: both lines `OK`.

- [ ] **Step 7: Final layer-level summary commit (optional — only if uncommitted changes remain)**

Run:
```bash
git status --short
```

If any files remain uncommitted, run:
```bash
git add shared/standards/electrical/IEC60617/
git commit -m "feat: IEC60617 standard layer v1.0.0 complete — 226 symbols across 6 IEC parts"
```

- [ ] **Step 8: Verify the final git log shows the planned commits**

Run:
```bash
git log --oneline -20
```

Expected to include (in order, most-recent first):
- (optional final commit)
- docs: IEC60617 symbol usage guide
- feat: IEC60617 symbol-index.json
- feat: IEC60617 part11-architectural.json
- feat: IEC60617 part8-measurement.json
- feat: IEC60617 part7-switchgear.json
- feat: IEC60617 part6-power.json
- feat: IEC60617 part3-conductors.json
- feat: IEC60617 part2-general.json
- docs: IEC60617 amendments summary
- docs: IEC60617 geometry encoding
- docs: rewrite IEC60617 README
- feat: IEC60617 meta.json
- refactor: move IEC60617 symbol reference into SLD assets

---

## Plan Summary

| Task | File(s) | Symbol count | Commits |
|---|---|---|---|
| 1 | Move `standard-symbols-reference.md` + update SLD manifest | — | 1 |
| 2 | `meta.json` | — | 1 |
| 3 | `README.md` rewrite | — | 1 |
| 4 | `geometry-encoding.md` | — | 1 |
| 5 | `amendments-summary.md` | — | 1 |
| 6 | `part2-general.json` | 25 | 1 |
| 7 | `part3-conductors.json` | 30 | 1 |
| 8 | `part6-power.json` | 35 | 1 |
| 9 | `part7-switchgear.json` | 70 | 1 |
| 10 | `part8-measurement.json` | 30 | 1 |
| 11 | `part11-architectural.json` | 36 | 1 |
| 12 | `symbol-index.json` | (226 entries) | 1 |
| 13 | `symbol-usage-guide.md` | — | 1 |
| 14 | Final verification | — | 0–1 |
| **Total** | **12 new files + 1 manifest update + 1 file move** | **226** | **13–14** |
