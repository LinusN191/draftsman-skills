# IEC 60617 Standard Layer — Design Spec

**Date:** 2026-05-14
**Status:** Approved
**Scope:** Build the IEC 60617 graphical symbols standard layer as a dual-purpose AI-intelligence and renderer-geometry source of truth.

---

## 1. Goal

Populate `shared/standards/electrical/IEC60617/` with a machine-readable symbol catalogue and narrative reference files so that:

1. Any DraftsMan AI skill can look up what a symbol means, when to use it, and what IEC clause it traces to.
2. The DraftsMan runtime can read symbol geometry directly from this layer and render it — no separate geometry store needed.
3. `shared/symbols/electrical/` symbol definition files are **generated** from this layer, making IEC 60617 the single source of truth for everything symbol-related.

IEC 60617 is the international graphical symbols standard for diagrams. It is a fundamentally different type of standard from IEC 60364 — it defines what symbols look like and mean, not engineering calculation values. The data model must reflect this.

---

## 2. Decisions Made

| Decision | Choice | Rationale |
|---|---|---|
| Purpose | Dual: AI intelligence + renderer geometry | Single source of truth — IEC 60617 layer drives both skill knowledge and symbol rendering. Avoids AI/geometry drift. |
| Coverage | Part-complete (~220 symbols) | All symbols across the 6 MEP-relevant parts. Eliminates "we need to add X" gaps later. |
| Geometry encoding | SVG path + terminals + bbox | SVG paths are universally previewable (browser, Inkscape), compact, and industry-standard. One-time SVG→DXF converter in runtime. |
| File organisation | Part files + flat index | Part files ensure completeness (nothing falls through categorisation gaps). `symbol-index.json` gives skills fast O(1) lookup without needing to know part numbers. |
| Existing `standard-symbols-reference.md` | Move to `electrical/sld/assets/` | It is SLD-skill-specific content, not a standards layer file. Superseded by the new layer. |
| Parts covered | 2, 3, 6, 7, 8, 11 | MEP-relevant parts. Parts 4 (passive components), 5 (semiconductors), 9–10 (telecom), 12–13 (logic/analogue) are out of scope for building electrical design. |
| Out of scope | IEC 60617 Parts 4, 5, 9, 10, 12, 13 | Not used in MEP building electrical design. Added in a future brainstorm if a skill needs them. |

---

## 3. Current State

Two files already exist:

| File | Status |
|---|---|
| `README.md` | Stub (`# IEC60617`) — must be rewritten |
| `standard-symbols-reference.md` | SLD-skill-specific quick-reference table — to be moved to `electrical/sld/assets/` and superseded by the new layer |

Everything else must be created from scratch.

---

## 4. File Set — 12 Files Total

### 4.1 Rewrite / migrate (2)

| File | Action |
|---|---|
| `README.md` | Rewrite as comprehensive index and layer usage guide |
| `standard-symbols-reference.md` | Move to `electrical/sld/assets/standard-symbols-reference.md`; update SLD manifest |

### 4.2 JSON — standard metadata (1)

| File | Content |
|---|---|
| `meta.json` | Standard title, IEC database URL, edition history, part catalogue with titles and scopes, relationship to national adoptions (BS EN 60617, DIN EN 60617), note on transition to online database |

### 4.3 JSON — symbol catalogues by IEC part (6)

| File | IEC Part | Approx. symbols | Content |
|---|---|---|---|
| `part2-general.json` | Part 2 | ~25 | Qualifying symbols, symbol elements: dotted enclosure boundary, shield, variability arrow, adjustability marker, test point, terminal symbol, wire junction (T and cross), wire crossing (no connection), functional grouping, screening/shielding, polarity indicators |
| `part3-conductors.json` | Part 3 | ~30 | Conductors and connections: single conductor, multicore cable, busbar, grouped conductors, conductor junction, conductor crossing, earth conductor, neutral conductor, PE conductor, PEN conductor, conductor in conduit/duct, overhead line, cable duct/trunking, armoured cable, flexible connection, shield/screen conductor |
| `part6-power.json` | Part 6 | ~35 | Generation and conversion: synchronous generator, induction generator, two-winding transformer, three-winding transformer, autotransformer, current transformer, voltage transformer, battery, battery charger, UPS, induction motor, synchronous motor, photovoltaic source, wind turbine, capacitor bank (PFC), reactor/inductor, rectifier, inverter |
| `part7-switchgear.json` | Part 7 | ~70 | Switchgear and protection: make-contact (NO), break-contact (NC), changeover contact, switch-disconnector (2P, 3P, 4P), bus section switch, isolator (2P, 3P, 4P), MCB (1P, 2P, 3P, 4P), MCCB (3P, 4P), ACB (3P, 4P), fuse (1P, 3P), fuse-switch, contactor (3P), star-delta contactor set, relay coil, thermal overload relay, motor circuit breaker, RCD/RCCB (2P, 4P), RCBO (1P, 2P), SPD (Type 1, 2, 3), ATS (2-way, 3-way), manual transfer switch, earth leakage relay, interlock contact, auxiliary contact (NO, NC), pushbutton (NO, NC), illuminated pushbutton, emergency stop, key switch, selector switch, time-delay contact (on-delay, off-delay) |
| `part8-measurement.json` | Part 8 | ~30 | Instruments and indicators: ammeter, voltmeter, wattmeter, VAR meter, power factor meter, frequency meter, energy meter (kWh), reactive energy meter (kVArh), smart/AMR meter, current transformer (metering), voltage transformer (metering), multifunction meter, lamp (indicator), lamp (luminaire general), buzzer, horn/siren, bell, audible alarm, visual alarm, LED indicator (red, green, amber) |
| `part11-architectural.json` | Part 11 | ~35 | Architectural and topographic plans: distribution board (general), main LV switchboard, consumer unit, sub-distribution board, generator panel, UPS panel, socket outlet (single, double, switched, industrial IP44, industrial IP67), socket outlet (3-phase), luminaire (general), luminaire (emergency), luminaire (recessed), exterior luminaire, switch (1-way), switch (2-way), intermediate switch, dimmer, PIR sensor, occupancy sensor, daylight sensor, smoke detector, heat detector, manual call point, junction box, cable route (general), cable route (concealed), cable route (surface trunking), cable route (overhead), cable route (underground), motor connection point, EV charging point |

### 4.4 JSON — master index (1)

| File | Content |
|---|---|
| `symbol-index.json` | Flat array of all ~220 symbols from all part files. Each entry: `symbol_id`, `iec_ref`, `iec_part`, `category`, `display_name`, `part_file`. Used by skills for O(1) lookup without loading part files. |

### 4.5 MD — narrative reference (3)

| File | Content |
|---|---|
| `symbol-usage-guide.md` | Engineering narrative on when to use which symbol. SLD conventions (line thickness, annotation position, bus representation). Common symbol combinations (MCB + RCD, ATS wiring, transformer with CT and VT). Mistakes to avoid (stacking single-pole symbols, missing terminal labels, wrong Part 7 vs Part 11 symbol on wrong drawing type). |
| `geometry-encoding.md` | The coordinate system (100-unit grid, origin at symbol centre, terminals named by function). SVG path conventions used in this layer. How to read and write a `path` string for a new symbol. How to verify a symbol by pasting its path into an SVG viewer. How the runtime converts SVG paths to DXF using ezdxf. Step-by-step guide for adding a new symbol entry. |
| `amendments-summary.md` | IEC 60617 edition history. Key change: transition from paper parts to the online IEC 60617 Database (iecdatabase.iec.ch). How IEC database reference numbers map to the traditional part/clause numbering. What changed between the 1996–2002 published parts and the current online database edition. National adoption status (BS EN 60617, DIN EN 60617). |

---

## 5. Per-Symbol JSON Schema

Every symbol entry in a part file uses this exact schema. All fields are mandatory — no optional fields.

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
    "path":      "M -50 0 L -20 0 M 20 0 L 50 0 M -20 -25 L -20 25 L 20 25 L 20 -25 Z M -20 0 L 20 0",
    "terminals": { "in": [-50, 0], "out": [50, 0] }
  },
  "variants":             ["MCB_2P", "MCB_3P", "MCB_4P"],
  "annotation_fields":    ["In_A", "curve", "Icu_kA"],
  "usage_notes":          "Used on SLDs for all final circuit MCB protection. Annotate with rated current, trip curve (B/C/D), and breaking capacity. For multi-pole, use the matching variant.",
  "related_symbols":      ["RCBO_1P", "MCCB_3P", "FUSE_1P"],
  "generating_shared_symbol": true
}
```

**Field definitions:**

| Field | Type | Description |
|---|---|---|
| `symbol_id` | string | DraftsMan canonical identifier — kebab-free, UPPER_SNAKE. Used in all skill IR outputs. |
| `iec_ref` | string | IEC 60617 database reference number. Format: `IEC60617-PP-XX-YY` where PP = part number. |
| `iec_part` | integer | IEC 60617 part number (2, 3, 6, 7, 8, or 11). |
| `iec_description` | string | Exact description from the IEC 60617 standard/database — not paraphrased. |
| `draftsman_id` | string | Same as `symbol_id` — explicit field for generated output clarity. |
| `category` | string | Functional category for `shared/symbols/electrical/` directory routing. One of: `general`, `conductor`, `power`, `protection`, `switching`, `measurement`, `architectural`. |
| `display_name` | string | Human-readable name shown in tool UIs and drawing legends. |
| `geometry.grid` | integer | Coordinate system grid size. Always 100. All coordinates in range ±50 on each axis. |
| `geometry.bbox` | [x1,y1,x2,y2] | Bounding box in grid units. |
| `geometry.path` | string | SVG path `d` attribute string. Origin at symbol centre. Terminals must lie on the bbox boundary. |
| `geometry.terminals` | object | Named terminal points as [x, y] in grid coordinates. Terminal names are functional (e.g. `in`/`out`, `A`/`B`, `line`/`load`, `coil_plus`/`coil_minus`). |
| `variants` | string[] | Other `symbol_id` values that are variants of this symbol (different pole count, NO/NC flip, etc.). |
| `annotation_fields` | string[] | Fields that must be annotated on this symbol in a drawing. Used by skill validation. |
| `usage_notes` | string | Engineering guidance: when to use this symbol, how to annotate it, common errors. |
| `related_symbols` | string[] | Symbols typically used together with this one. Used by skills for cross-referencing. |
| `generating_shared_symbol` | boolean | `true` = runtime generates a file in `shared/symbols/electrical/`. `false` for pure qualifying/modifier symbols. |

---

## 6. `symbol-index.json` Schema

```json
{
  "_title":           "IEC 60617 — Master Symbol Index",
  "_version":         "1.0.0",
  "_generated_from":  ["part2-general.json", "part3-conductors.json", "part6-power.json",
                       "part7-switchgear.json", "part8-measurement.json", "part11-architectural.json"],
  "_note": "Flat lookup for skills. Hand-maintained in sync with the six part files — not auto-generated by a script. When a new symbol is added to a part file, add the corresponding index entry here. Load this file for symbol_id → IEC ref + category + part file mapping. Load the part file when geometry or usage notes are needed.",
  "symbols": [
    {
      "symbol_id":    "MCB_1P",
      "iec_ref":      "IEC60617-07-18-01",
      "iec_part":     7,
      "category":     "protection",
      "display_name": "1-Pole MCB",
      "part_file":    "part7-switchgear.json"
    }
  ]
}
```

---

## 7. Generated Output — `shared/symbols/electrical/`

Symbols with `generating_shared_symbol: true` produce files under `shared/symbols/electrical/[category]/[symbol_id].json`. The runtime generator copies geometry from the IEC 60617 entry and adds CAD-specific fields:

```json
{
  "symbol_id":     "MCB_1P",
  "source":        "shared/standards/electrical/IEC60617/part7-switchgear.json",
  "iec_ref":       "IEC60617-07-18-01",
  "category":      "protection",
  "display_name":  "1-Pole MCB",
  "geometry":      { "...copied from IEC60617 entry..." },
  "cad": {
    "default_layer":  "E-PROT",
    "default_colour": 1,
    "lineweight":     25,
    "block_name":     "MCB-1P"
  },
  "annotation_fields": ["In_A", "curve", "Icu_kA"],
  "tag_format":    "CB{index:02d}"
}
```

The generator script lives in the DraftsMan runtime repo — it is not part of this standards layer. The standards layer is input-only.

**CAD layer assignments by category:**

| Category | CAD layer |
|---|---|
| `protection` | `E-PROT` |
| `switching` | `E-SWIT` |
| `power` | `E-POWR` |
| `conductor` | `E-WIRE` |
| `measurement` | `E-MEAS` |
| `architectural` | `E-EQPM` |
| `general` | `E-SYMB` |

---

## 8. SLD Manifest Migration

The SLD skill's `standards` field is updated from pointing at the old single file to the whole IEC 60617 layer folder:

**Before:**
```json
"standards": [
  "shared/standards/electrical/BS7671/",
  "shared/standards/electrical/IEC61439/",
  "shared/standards/electrical/IEC60617/standard-symbols-reference.md"
]
```

**After:**
```json
"standards": [
  "shared/standards/electrical/BS7671/",
  "shared/standards/electrical/IEC61439/",
  "shared/standards/electrical/IEC60617/"
]
```

`standard-symbols-reference.md` is moved to `electrical/sld/assets/standard-symbols-reference.md` as a legacy quick-reference. It is not deleted — the SLD skill may still reference it in its prompt until the new layer is fully integrated.

---

## 9. File Tree (final state)

```
IEC60617/
├── README.md                    ← rewrite
├── meta.json                    ← new
├── symbol-index.json            ← new
│
├── part2-general.json           ← new (~25 symbols)
├── part3-conductors.json        ← new (~30 symbols)
├── part6-power.json             ← new (~35 symbols)
├── part7-switchgear.json        ← new (~70 symbols)
├── part8-measurement.json       ← new (~30 symbols)
├── part11-architectural.json    ← new (~35 symbols)
│
├── symbol-usage-guide.md        ← new
├── geometry-encoding.md         ← new
└── amendments-summary.md        ← new

standard-symbols-reference.md   ← MOVED to electrical/sld/assets/
```

---

## 10. Out of Scope

- IEC 60617 Parts 4, 5, 9, 10, 12, 13 — passive components, semiconductors, telecom, logic, analogue. Added when a skill needs them.
- DXF block definitions — geometry is in SVG path format in this layer; the DXF block generation is the runtime's responsibility.
- Symbol colours / line weights in the standards layer — those are renderer concerns and live only in the generated `shared/symbols/electrical/` files.
- HV symbols — IEC 60617 covers HV as well as LV; this layer covers LV building electrical only. HV symbols are a future brainstorm.
- Schematic skills beyond SLD — the schematic skill will consume this layer directly once it is built.
