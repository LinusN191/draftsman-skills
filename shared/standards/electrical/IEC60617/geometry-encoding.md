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
