# EXAMPLES — lighting-layout skill

Three fully worked examples showing input → reasoning → JSON output.
Use these to verify skill behaviour and as reference for common cases.

---

## Example 1 — Open plan office, 10m × 8m

### Input

```
Room: 10m × 8m, 3.0m ceiling height
Room type: open plan office
Working plane: 0.75m AFF
Luminaire: 600×600 LED recessed panel, 4500 lm, 36W
Ceiling grid: 600mm module
Reflectances: ceiling 70%, walls 50%, floor 20% (standard)
SHR_max: 1.5 (assumed, no photometric data provided)
Entrances: 1, south wall
```

### Reasoning shown in chat

**Step 2 — Target:** Open plan office → **Em = 500 lux, UGR ≤ 19, Ra ≥ 80**
(BS EN 12464-1:2021 Table 5.3)

**Step 3 — Room Index:**
```
Hm = 3.0 − 0.75 = 2.25m
RI = (10 × 8) / (2.25 × (10 + 8)) = 80 / 40.5 = 1.98 → use 2.0
```

**Step 4 — UF:**
[ASSUMPTION: UF = 0.68 assumed for LED 600×600 panel at RI = 2.0, standard
reflectances 70/50/20. Verify against manufacturer's photometric data before tender.]

**Step 5 — MF:**
[ASSUMPTION: MF = 0.80 assumed (LLMF=0.95, LSF=1.00, LMF=0.90, RSMF=0.94).
Confirm cleaning regime and LED rated life from specification.]

**Step 6 — Fixture count:**
```
N = (500 × 80) / (4500 × 0.68 × 0.80) = 40,000 / 2,448 = 16.34 → round up to 17
```

17 luminaires does not fit a clean symmetric grid. Next clean option: **18 luminaires
in a 3 rows × 6 columns grid.**

```
E_achieved = (18 × 4500 × 0.68 × 0.80) / 80 = 44,064 / 80 = 551 lux ✓
```

**Step 7 — Spacing check (3×6 grid):**
```
X spacing (6 cols in 10,000mm): 10,000 / 6 = 1,667mm
Y spacing (3 rows in 8,000mm):  8,000 / 3  = 2,667mm
SHR check: max(1,667, 2,667) / 2,250 = 1.19 ≤ 1.5 ✓
Edge X: 1,667 / 2 = 833mm ≤ 1,687mm ✓
Edge Y: 2,667 / 2 = 1,333mm ≤ 1,687mm ✓
```

**Step 8 — Positions (snapped to 600mm grid centres):**

Grid in 10,000mm (6 cols): centres at 833, 2500, 4167, 5833, 7500, 9167mm
Snap to 600mm grid: 900, 2500, 4200, 5800, 7500, 9100mm (nearest 100mm)

Grid in 8,000mm (3 rows): centres at 1333, 4000, 6667mm
Snap: 1200, 4000, 6600mm

**Step 9 — Circuits:**
```
18 × 36W = 648W total
Max per 10A circuit = floor(1840 / 36) = 51 luminaires
All 18 on circuit L1 (648W << 1840W limit) ✓
```

**Step 10 — Switches:**
1 × 1-gang switch, south wall, controls L1.

### JSON output (abbreviated)

```json
{
  "drawing_type": "lighting_layout",
  "room": {
    "length_mm": 10000, "width_mm": 8000, "ceiling_height_mm": 3000,
    "working_plane_height_mm": 750, "effective_mounting_height_mm": 2250,
    "area_m2": 80.0, "room_index": 1.98, "space_type": "open plan office",
    "ceiling_grid_module_mm": 600
  },
  "calculation_summary": {
    "target_illuminance_lux": 500, "ugr_limit": 19, "ra_minimum": 80,
    "utilisation_factor": 0.68, "maintenance_factor": 0.80,
    "luminaires_required_lumen_method": 17, "luminaires_installed": 18,
    "grid_arrangement": "3x6",
    "achieved_illuminance_lux": 551, "uniformity_u0_estimated": 0.72,
    "compliant": true,
    "assumptions": [
      "UF = 0.68 assumed for LED 600x600 at RI=2.0. Verify against photometric data.",
      "MF = 0.80 assumed. Confirm cleaning regime and LED rated life."
    ]
  },
  "luminaire_type": {
    "symbol": "LED_PANEL_600x600", "wattage_w": 36, "lumens": 4500,
    "colour_temperature_k": 4000, "cri_ra": 80, "ip_rating": "IP20",
    "dimensions_mm": {"length": 600, "width": 600}, "shr_max": 1.5
  },
  "luminaires": [
    {"id": "L01", "x_mm": 900,  "y_mm": 1200, "circuit": "L1", "type": "general"},
    {"id": "L02", "x_mm": 2500, "y_mm": 1200, "circuit": "L1", "type": "general"},
    {"id": "L03", "x_mm": 4200, "y_mm": 1200, "circuit": "L1", "type": "general"},
    {"id": "L04", "x_mm": 5800, "y_mm": 1200, "circuit": "L1", "type": "general"},
    {"id": "L05", "x_mm": 7500, "y_mm": 1200, "circuit": "L1", "type": "general"},
    {"id": "L06", "x_mm": 9100, "y_mm": 1200, "circuit": "L1", "type": "general"},
    {"id": "L07", "x_mm": 900,  "y_mm": 4000, "circuit": "L1", "type": "general"},
    {"id": "L08", "x_mm": 2500, "y_mm": 4000, "circuit": "L1", "type": "general"},
    {"id": "L09", "x_mm": 4200, "y_mm": 4000, "circuit": "L1", "type": "general"},
    {"id": "L10", "x_mm": 5800, "y_mm": 4000, "circuit": "L1", "type": "general"},
    {"id": "L11", "x_mm": 7500, "y_mm": 4000, "circuit": "L1", "type": "general"},
    {"id": "L12", "x_mm": 9100, "y_mm": 4000, "circuit": "L1", "type": "general"},
    {"id": "L13", "x_mm": 900,  "y_mm": 6600, "circuit": "L1", "type": "general"},
    {"id": "L14", "x_mm": 2500, "y_mm": 6600, "circuit": "L1", "type": "general"},
    {"id": "L15", "x_mm": 4200, "y_mm": 6600, "circuit": "L1", "type": "general"},
    {"id": "L16", "x_mm": 5800, "y_mm": 6600, "circuit": "L1", "type": "general"},
    {"id": "L17", "x_mm": 7500, "y_mm": 6600, "circuit": "L1", "type": "general"},
    {"id": "L18", "x_mm": 9100, "y_mm": 6600, "circuit": "L1", "type": "general"}
  ],
  "circuits": [
    {
      "id": "L1", "type": "general", "mcb_rating_a": 10,
      "luminaire_ids": ["L01","L02","L03","L04","L05","L06","L07","L08","L09",
                        "L10","L11","L12","L13","L14","L15","L16","L17","L18"],
      "total_load_w": 648, "load_utilisation_pct": 35,
      "wiring_path": [[900,1200],[2500,1200],[4200,1200],[5800,1200],
                      [7500,1200],[9100,1200],[9100,4000],[7500,4000],
                      [5800,4000],[4200,4000],[2500,4000],[900,4000],
                      [900,6600],[2500,6600],[4200,6600],[5800,6600],
                      [7500,6600],[9100,6600]]
    }
  ],
  "switches": [
    {
      "id": "SW1", "x_mm": 500, "y_mm": 200, "wall": "south",
      "height_aff_mm": 1350, "controls_circuits": ["L1"],
      "gang_count": 1, "location_note": "main entrance south wall"
    }
  ]
}
```

---

## Example 2 — Warehouse, high bay, two circuits

### Input

```
Room: 30m × 20m, 8.0m ceiling height
Room type: warehouse (high rack/pick face)
Working plane: 1.0m AFF
Luminaire: LED highbay, 20,000 lm, 150W
Ceiling grid: none (industrial, open structure)
Entrances: 2, south wall (east end and west end)
```

### Key calculations (abbreviated)

```
Hm = 8.0 − 1.0 = 7.0m
RI = (30 × 20) / (7.0 × (30 + 20)) = 600 / 350 = 1.71 → use 1.75
```

[ASSUMPTION: UF = 0.65 assumed for LED highbay at RI = 1.75. High-bay
photometric data varies significantly by optic angle — verify.]

Target: 500 lux (warehouse high rack, BS EN 12464-1:2021)
MF: 0.75 (industrial, 6-month cleaning, LED)
[ASSUMPTION: MF = 0.75 (LLMF=0.92, LSF=1.00, LMF=0.87, RSMF=0.93).]

```
N = (500 × 600) / (20,000 × 0.65 × 0.75) = 300,000 / 9,750 = 30.77 → 31 fixtures
```

Clean grid: **4 rows × 8 cols = 32 fixtures**

```
E_achieved = (32 × 20,000 × 0.65 × 0.75) / 600 = 312,000 / 600 = 520 lux ✓
```

Spacing: X = 30,000/8 = 3,750mm, Y = 20,000/4 = 5,000mm
S_max = 1.5 × 7,000 = 10,500mm — both well within limit ✓

**Circuits:**
```
32 × 150W = 4,800W total
Max per 10A circuit = floor(1840 / 150) = 12 fixtures
Circuits needed = ceil(32 / 12) = 3 circuits
L1: 12 fixtures (1,800W), L2: 12 fixtures (1,800W), L3: 8 fixtures (1,200W)
```

**Switches:**
2 × 3-gang switch plates (south wall, east and west entrance positions)
Each plate controls L1, L2, L3 independently for zone dimming.

---

## Example 3 — Reception lobby, LED downlights

### Input

```
Room: 6m × 5m, 3.2m ceiling height
Room type: reception / lobby
Working plane: 0.75m AFF
Luminaire: LED downlight (recessed), 1,200 lm, 12W
Ceiling: plasterboard, no grid
Entrances: 1, north wall
```

### Key calculations (abbreviated)

Target: 300 lux (reception/lobby, BS EN 12464-1:2021)

```
Hm = 3.2 − 0.75 = 2.45m
RI = (6 × 5) / (2.45 × 11) = 30 / 26.95 = 1.11 → use 1.0
```

[ASSUMPTION: UF = 0.55 assumed for recessed downlight at RI = 1.0,
standard reflectances. Downlights have lower UF than panels — confirm
with photometric data. Narrow beam downlights may be significantly lower.]

MF = 0.80 (normal interior, LED)

```
N = (300 × 30) / (1,200 × 0.55 × 0.80) = 9,000 / 528 = 17.05 → 18 fixtures
```

Grid: **3 rows × 6 cols = 18 fixtures** (but plasterboard ceiling — positions
not constrained to grid, snap to 100mm instead)

```
E_achieved = (18 × 1,200 × 0.55 × 0.80) / 30 = 9,504 / 30 = 317 lux ✓
```

Spacing: X = 6,000/6 = 1,000mm, Y = 5,000/3 = 1,667mm
S_max = 1.5 × 2,450 = 3,675mm ✓

**Circuits:**
```
18 × 12W = 216W total — all on single circuit L1
```

**Design note for lobby:** Consider accent lighting (wall washing, artwork
lighting) as a separate circuit. UGR limit is 22 for reception — downlights
with wide beam optics are preferred over narrow spot.

[ASSUMPTION: Ceiling is flat plasterboard with no structural constraint.
Confirm there are no beams or services that would obstruct positions shown.]
