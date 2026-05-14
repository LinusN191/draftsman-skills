# EXAMPLES — sld skill

Three fully worked examples showing input → reasoning → JSON output.
Use these to verify skill behaviour and as reference for common cases.

---

## Example 1 — Small commercial office, MSB + 3 SDBs

### Input

```
Building: 3-storey spec office, 1200m² GIA
Supply: 3-phase TN-C-S, 400V/230V, 50Hz, DNO underground
Ze at supply terminals: 0.35 Ω (confirmed by DNO)
PSCC at supply: 230 / 0.35 = 657 A = 0.66 kA
DNO cutout fuse: 100A per phase

Load schedule:
  SDB-GF  (Ground Floor, 400m²): 30 kVA, PF 0.85, 3-phase
            — 12kW lighting, 10kW sockets, 5kW IT, 3kW HVAC FCUs
  SDB-L1  (Level 1, 400m²):      28 kVA, PF 0.85, 3-phase
            — 11kW lighting, 9kW sockets, 5kW IT, 3kW HVAC FCUs
  SDB-L2  (Level 2, 400m²):      28 kVA, PF 0.85, 3-phase
            — 11kW lighting, 9kW sockets, 5kW IT, 3kW HVAC FCUs

Cable lengths (MSB to each SDB): GF 15m, L1 30m, L2 45m
All cables on cable tray in riser — installation method E
Generator: none
Metering: 1 × landlord kWh meter at MSB
```

### Reasoning shown in chat

**Step 2 — Hierarchy:**
```
DNO Supply (3-phase, 400V, TN-C-S, Ze = 0.35 Ω)
  └── MSB (Main LV Switchboard, Ground Floor Plant Room)
        ├── SDB-GF  (Ground Floor, 400m²)
        ├── SDB-L1  (Level 1, 400m²)
        └── SDB-L2  (Level 2, 400m²)
```

**Step 3 — Design currents (Ib):**
```
SDB-GF:  Ib = 30,000 / (1.732 × 400 × 0.85) = 30,000 / 587.9 = 51.0A → 52A
SDB-L1:  Ib = 28,000 / 587.9 = 47.6A → 48A
SDB-L2:  Ib = 28,000 / 587.9 = 47.6A → 48A
```

[ASSUMPTION: PF = 0.85 for all loads. Confirm with mechanical engineer for
FCU loads and equipment schedules for IT.]

**Step 4 — Diversity and maximum demand at MSB:**

| Circuit | Installed load | Load type | Diversity | Demand current |
|---|---|---|---|---|
| SDB-GF lighting | 12kW = 23.5A | Lighting | 0.90 | 21.2A |
| SDB-GF sockets | 10kW = 19.6A | Sockets | 0.50 | 9.8A |
| SDB-GF IT | 5kW = 9.8A | IT | 0.80 | 7.8A |
| SDB-GF HVAC FCUs | 3kW = 5.9A | Intermittent HVAC | 0.75 | 4.4A |
| **SDB-GF total** | **51.0A** | | | **43.2A** |
| SDB-L1 (same profile) | 47.6A | | | 40.3A |
| SDB-L2 (same profile) | 47.6A | | | 40.3A |

[ASSUMPTION: Diversity factors applied as: lighting 0.90, sockets 0.50,
IT 0.80, HVAC FCUs 0.75. Confirm with client's load schedule before tender.]

MSB total maximum demand = 43.2 + 40.3 + 40.3 = 123.8A → use 125A for device
selection.

**Step 5 — Protective devices:**

SDB incomer MCCBs:
```
SDB-GF:  Ib = 52A → select 63A MCCB (next standard size above 52A) ✓
SDB-L1:  Ib = 48A → select 63A MCCB ✓
SDB-L2:  Ib = 48A → select 63A MCCB ✓
```

MSB incomer MCCB:
```
Ib_MSB = 125A → select 160A MCCB (next standard size above 125A) ✓
DNO cutout fuse 100A per phase — NOTE: 160A MCCB is downstream of 100A
cutout. Cutout provides upstream discrimination. Confirm with DNO.
```

Breaking capacity check: all MCCBs need Icu ≥ 0.66kA — minimum standard
MCCB Icu of 10kA is far in excess. No issue.

**Step 6 — Cables:**
```
MSB to SDB-GF:  Ib = 52A, L = 15m, method E (tray)
  → 16mm² 4C+CPC Cu XLPE/SWA/PVC  (CCC = 87A from Table 4D4A method E) ✓
  Vd = 52 × 15 × 2.4mv/A/m / 1000 = 1.87V = 0.47% ✓ (≤5%)

MSB to SDB-L1:  Ib = 48A, L = 30m, method E
  → 16mm² 4C+CPC (CCC = 87A) ✓
  Vd = 48 × 30 × 2.4 / 1000 = 3.46V = 0.86% ✓

MSB to SDB-L2:  Ib = 48A, L = 45m, method E
  → 16mm² 4C+CPC (CCC = 87A) ✓
  Vd = 48 × 45 × 2.4 / 1000 = 5.18V = 1.30% ✓
```

[ASSUMPTION: mV/A/m = 2.4 for 16mm² Cu at 70°C, method E. Confirm from
BS 7671:2018 Table 4D2B or cable manufacturer's data.]

**Step 7 — RCD requirements:**
Socket circuits at each SDB will require 30mA RCBOs per Regulation 411.3.3.
Note on SLD: "All socket outlet circuits ≤ 32A to have 30mA RCD protection."
IT circuit: fixed connection — RCD recommended but not mandatory.

**Step 8 — PSCC at each SDB:**
```
ρ = 0.0225 Ω·mm²/m  (copper at 70°C)

SDB-GF:  Zcable = (2 × 0.0225 × 15) / 16 = 0.042Ω
          Ze_SDB-GF = 0.35 + 0.042 = 0.392Ω → PSCC = 230/0.392 = 587A = 0.59kA
SDB-L1:  Zcable = (2 × 0.0225 × 30) / 16 = 0.084Ω
          Ze_SDB-L1 = 0.35 + 0.084 = 0.434Ω → PSCC = 230/0.434 = 530A = 0.53kA
SDB-L2:  Zcable = (2 × 0.0225 × 45) / 16 = 0.127Ω
          Ze_SDB-L2 = 0.35 + 0.127 = 0.477Ω → PSCC = 230/0.477 = 482A = 0.48kA
```

All PSCC values well below minimum MCCB Icu of 10kA. ✓

**Step 10 — Earthing:**
TN-C-S system. Main bonding at MSB MET to gas, water, and structural steel.
Main bonding conductors: minimum 10mm² copper (Table 54.8, BS 7671:2018).
Earth conductor from MET to building earth: 16mm² Cu (Table 54.7).

### JSON output (abbreviated)

```json
{
  "drawing_type": "single_line_diagram",
  "supply": {
    "voltage_ll_v": 400, "voltage_ln_v": 230, "phases": 3,
    "earthing_system": "TN-C-S", "pscc_ka_at_supply": 0.66,
    "ze_ohm": 0.35, "supply_type": "DNO_underground", "cutout_fuse_a": 100
  },
  "boards": [
    {
      "id": "MSB", "type": "main_lv_switchboard",
      "label": "MAIN LV SWITCHBOARD", "level": 1,
      "busbar_rating_a": 200,
      "incomer": {"device": "MCCB", "rating_a": 160, "breaking_capacity_ka": 10,
                  "poles": 4, "standard": "BS EN 60947-2", "symbol": "MCCB_4P"},
      "metering": [{"type": "CT", "ratio": "200/5A", "class": "1"},
                   {"type": "KWH_METER", "label": "LL01 — Landlord Main Meter"}],
      "earthing": {"main_earth_terminal": true, "earth_conductor_mm2": 16,
                   "bonding_connections": ["gas", "water", "structural_steel"]},
      "outgoing_ways": [
        {"way_id": "MSB-W01", "label": "SDB-GF — Ground Floor",
         "device": "MCCB", "rating_a": 63, "breaking_capacity_ka": 10, "poles": 4,
         "rcd": false, "to_board_id": "SDB-GF",
         "design_current_a": 52.0, "installed_load_kva": 30.0,
         "maximum_demand_kva": 25.4, "diversity_factor": 0.85, "cable_ref": "C01"},
        {"way_id": "MSB-W02", "label": "SDB-L1 — Level 1",
         "device": "MCCB", "rating_a": 63, "breaking_capacity_ka": 10, "poles": 4,
         "rcd": false, "to_board_id": "SDB-L1",
         "design_current_a": 48.0, "installed_load_kva": 28.0,
         "maximum_demand_kva": 23.7, "diversity_factor": 0.85, "cable_ref": "C02"},
        {"way_id": "MSB-W03", "label": "SDB-L2 — Level 2",
         "device": "MCCB", "rating_a": 63, "breaking_capacity_ka": 10, "poles": 4,
         "rcd": false, "to_board_id": "SDB-L2",
         "design_current_a": 48.0, "installed_load_kva": 28.0,
         "maximum_demand_kva": 23.7, "diversity_factor": 0.85, "cable_ref": "C03"}
      ],
      "pscc_ka": 0.66, "total_installed_load_kva": 86.0,
      "maximum_demand_kva": 72.8, "overall_diversity_factor": 0.85
    },
    {
      "id": "SDB-GF", "type": "sub_distribution_board", "label": "SDB — GROUND FLOOR",
      "level": 2, "parent_id": "MSB", "location": "Ground Floor Comms Room",
      "busbar_rating_a": 100,
      "incomer": {"device": "MCCB", "rating_a": 63, "breaking_capacity_ka": 10,
                  "poles": 4, "standard": "BS EN 60947-2", "symbol": "MCCB_4P"},
      "outgoing_ways": [
        {"way_id": "SDB-GF-W01", "label": "Lighting — GF",
         "device": "MCB", "rating_a": 10, "poles": 1, "rcd": false, "cable_ref": null},
        {"way_id": "SDB-GF-W02", "label": "Sockets — GF",
         "device": "RCBO", "rating_a": 16, "poles": 1,
         "rcd": true, "rcd_sensitivity_ma": 30, "cable_ref": null},
        {"way_id": "SDB-GF-W03", "label": "IT outlets — GF",
         "device": "RCBO", "rating_a": 16, "poles": 1,
         "rcd": true, "rcd_sensitivity_ma": 30, "cable_ref": null}
      ],
      "pscc_ka": 0.59, "total_installed_load_kva": 30.0, "maximum_demand_kva": 25.4
    }
  ],
  "connections": [
    {"id": "C01", "from_board_id": "MSB", "from_way_id": "MSB-W01", "to_board_id": "SDB-GF",
     "conductors": "4C+CPC", "conductor_size_mm2": 16, "cpc_size_mm2": 10,
     "conductor_material": "copper", "insulation": "XLPE", "armour": "SWA",
     "installation_method": "E", "length_m": 15,
     "design_current_a": 52.0, "ccc_a": 87,
     "voltage_drop_mv_per_am": 2.4, "voltage_drop_v": 1.87,
     "voltage_drop_pct": 0.47, "pscc_at_far_end_ka": 0.59},
    {"id": "C02", "from_board_id": "MSB", "from_way_id": "MSB-W02", "to_board_id": "SDB-L1",
     "conductors": "4C+CPC", "conductor_size_mm2": 16, "cpc_size_mm2": 10,
     "conductor_material": "copper", "insulation": "XLPE", "armour": "SWA",
     "installation_method": "E", "length_m": 30,
     "design_current_a": 48.0, "ccc_a": 87,
     "voltage_drop_v": 3.46, "voltage_drop_pct": 0.86, "pscc_at_far_end_ka": 0.53},
    {"id": "C03", "from_board_id": "MSB", "from_way_id": "MSB-W03", "to_board_id": "SDB-L2",
     "conductors": "4C+CPC", "conductor_size_mm2": 16, "cpc_size_mm2": 10,
     "conductor_material": "copper", "insulation": "XLPE", "armour": "SWA",
     "installation_method": "E", "length_m": 45,
     "design_current_a": 48.0, "ccc_a": 87,
     "voltage_drop_v": 5.18, "voltage_drop_pct": 1.30, "pscc_at_far_end_ka": 0.48}
  ],
  "earthing": {
    "system": "TN-C-S", "main_earthing_terminal_board": "MSB",
    "earth_conductor_size_mm2": 16, "main_bonding_conductor_mm2": 10,
    "bonding_connections": ["gas installation pipework", "water installation pipework",
                            "structural steel"],
    "earth_electrode": false
  },
  "schematic": {
    "layout_direction": "top_down", "supply_x_col": 0,
    "board_positions": [
      {"board_id": "MSB",    "x_col": 0,  "y_level": 1},
      {"board_id": "SDB-GF", "x_col": -2, "y_level": 2},
      {"board_id": "SDB-L1", "x_col": 0,  "y_level": 2},
      {"board_id": "SDB-L2", "x_col": 2,  "y_level": 2}
    ]
  },
  "calculation_summary": {
    "total_installed_load_kva": 86.0, "maximum_demand_kva": 72.8,
    "overall_diversity_factor": 0.85, "incoming_mccb_rating_a": 160,
    "supply_pscc_ka": 0.66, "earthing_system": "TN-C-S",
    "rcd_protected_ways": 6, "compliant": true,
    "assumptions": [
      "PF = 0.85 assumed for all loads — confirm with equipment schedules",
      "Diversity: lighting 0.90, sockets 0.50, IT 0.80, FCUs 0.75 — confirm with client",
      "mV/A/m = 2.4 for 16mm² Cu method E — confirm from BS 7671:2018 Table 4D2B"
    ]
  }
}
```

---

## Example 2 — Medium commercial building with standby generator

### Input

```
Building: 5-storey office and retail, mixed-use, 4000m² GIA
Supply: 3-phase TN-C-S, 400V/230V, Ze = 0.25 Ω from DNO
PSCC at supply: 230 / 0.25 = 920A = 0.92kA

Load schedule (at MSB):
  SDB-RETAIL  (Ground Floor retail): 60kVA, PF 0.90, 3-phase
  SDB-OFFICE  (Floors 1–4, open plan): 80kVA, PF 0.85, 3-phase
  SDB-HVAC    (Plant room): 90kVA continuous HVAC, PF 0.85, 3-phase
  SDB-LIFT    (2 × 15kW lifts): 30kVA, PF 0.85, 3-phase
  SDB-ESSN    (Essential services — escape lighting, fire alarm, security): 5kVA

Generator: 125kVA diesel standby — essential services only (SDB-ESSN, smoke
           extract fan, server room UPS)
Cable lengths: MSB to each SDB — 10m (all in basement plant room)
```

### Key reasoning (abbreviated)

**Step 2 — Hierarchy:**
```
DNO Supply (Ze = 0.25 Ω)
  └── MSB (with ATS)
        ├── MAINS BUS ──────────────────────────────────────────┐
        │     ├── SDB-RETAIL  (60kVA)                           │
        │     ├── SDB-OFFICE  (80kVA)                           │
        │     ├── SDB-HVAC    (90kVA)                           │
        │     └── SDB-LIFT    (30kVA)                           │
        │                                                        │
        └── ESSENTIAL BUS  ← ATS ← GENERATOR (125kVA diesel) ──┘
              └── SDB-ESSN  (5kVA)
```

ATS interlocks mains and generator supplies — cannot parallel.
(BS 7671:2018 Regulation 551.7)

**Step 3 & 4 — Design currents and maximum demand:**

```
SDB-RETAIL: Ib = 60,000 / (1.732×400×0.90) = 60,000/623.5 = 96.2A → 97A
             Max demand: 50kW lighting @ 0.90 + 10kW sockets @ 0.50 = 77A
SDB-OFFICE: Ib = 80,000 / (1.732×400×0.85) = 80,000/587.9 = 136.1A → 137A
             Max demand with diversity = 109A
SDB-HVAC:   Ib = 90,000 / 587.9 = 153.1A → 154A
             Continuous HVAC: diversity = 1.00. Max demand = 154A
SDB-LIFT:   Ib = 30,000 / 587.9 = 51.0A → 52A
             2 lifts: Lift 1 @ 1.00 (26A), Lift 2 @ 0.50 (13A) = 39A
SDB-ESSN:   Ib = 5,000 / 587.9 = 8.5A → 9A (no diversity on essential services)
```

MSB total maximum demand = 77 + 109 + 154 + 39 + 9 = 388A → select 400A MCCB

[ASSUMPTION: Diversity factors — lighting 0.90, sockets 0.50, office loads 0.80.
HVAC continuous plant rated at 1.00 diversity per CIBSE Guide B. Confirm before
tender.]

**Step 5 — Protective devices:**
```
SDB-RETAIL incomer:  97A → 100A MCCB, Icu ≥ 10kA ✓
SDB-OFFICE incomer: 137A → 160A MCCB, Icu ≥ 10kA ✓
SDB-HVAC incomer:   154A → 160A MCCB, Icu ≥ 10kA ✓
SDB-LIFT incomer:    52A →  63A MCCB, Icu ≥ 10kA ✓
SDB-ESSN incomer:     9A →  16A MCB, Icu ≥ 3kA ✓
MSB incomer:         388A → 400A MCCB, Icu ≥ 25kA (PSCC = 0.92kA — minimum
                     standard MCCB 10kA Icu far exceeds, but specify 25kA for
                     urban supply resilience) ✓
```

**Step 9 — Generator and ATS:**
```
Generator rating: 125kVA
Generator full load current: 125,000 / (1.732 × 400) = 180.5A
Generator incomer MCCB at MSB essential bus: 200A MCCB

Essential bus feeds: SDB-ESSN (5kVA), smoke extract fans (included in HVAC
allocation), server room UPS input (flagged for client confirmation)

ATS: 2-way automatic transfer switch between mains and generator
Interlocking: electrical and mechanical — mains and generator MCCBs cannot
close simultaneously.

Generator PSCC estimate: 3 × 180.5 = 542A = 0.54kA
[ASSUMPTION: Generator PSCC estimated as 3× FLC. Obtain sub-transient
reactance data from generator manufacturer for accurate value.]
```

**Step 8 — PSCC at boards (cable 10m, 35mm² XLPE 4C+CPC):**
```
Zcable = (2 × 0.0225 × 10) / 35 = 0.013Ω per board
Ze_SDB = 0.25 + 0.013 = 0.263Ω → PSCC = 230/0.263 = 875A = 0.875kA
```

All device Icu of 10kA far exceeds 0.875kA. ✓

**Generator:**
```json
"generator": {
  "rating_kva": 125,
  "fuel_type": "diesel",
  "amf": true,
  "full_load_current_a": 181,
  "incomer_mccb_rating_a": 200,
  "incomer_breaking_capacity_ka": 10,
  "pscc_ka_estimate": 0.54,
  "essential_bus_boards": ["SDB-ESSN"],
  "non_essential_bus_boards": ["SDB-RETAIL", "SDB-OFFICE", "SDB-HVAC", "SDB-LIFT"],
  "ats_type": "ATS_2WAY",
  "interlocking_note": "Mains and generator MCCBs electrically interlocked — cannot parallel. Regulation 551.7, BS 7671:2018."
}
```

---

## Example 3 — Retail unit, single-phase service, sub-metered tenants

### Input

```
Building: small retail parade, 3 units sharing a single-phase service
Supply: single-phase TN-C-S, 230V, 50Hz
Ze at supply terminals: 0.80 Ω (confirmed by DNO)
PSCC at supply: 230 / 0.80 = 288A = 0.29kA
DNO cutout: 100A

Loads:
  Unit A: 5kW total (lighting, sockets, refrigeration), PF 0.90, single-phase
  Unit B: 8kW total (lighting, sockets, catering prep), PF 0.85, single-phase
  Unit C: 6kW total (lighting, sockets), PF 0.90, single-phase

Metering: individual kWh meters per unit at landlord board (LB)
```

### Key reasoning (abbreviated)

**Step 2 — Hierarchy:**
```
DNO Supply (single-phase, 230V, Ze = 0.80Ω)
  └── LB (Landlord Board with 3 tenant meters)
        ├── DB-A  (Unit A)
        ├── DB-B  (Unit B)
        └── DB-C  (Unit C)
```

**Step 3 — Design currents:**
```
DB-A: Ib = (5000) / (230 × 0.90) = 5000 / 207 = 24.2A → 25A
DB-B: Ib = (8000) / (230 × 0.85) = 8000 / 195.5 = 40.9A → 41A
DB-C: Ib = (6000) / (230 × 0.90) = 6000 / 207 = 29.0A → 30A
```

**Step 4 — Maximum demand:**

| Circuit | Ib | Diversity | Demand |
|---|---|---|---|
| Unit A — lighting + sockets + refrigeration | 25A | 0.70 | 17.5A |
| Unit B — lighting + catering | 41A | 0.75 | 30.8A |
| Unit C — lighting + sockets | 30A | 0.70 | 21.0A |
| **LB total** | **96A** | | **69.3A** |

[ASSUMPTION: Diversity 0.70–0.75 for small retail. Catering equipment
higher at 0.75 (CIBSE Guide B4). Confirm before tender.]

LB incoming protective device: 69.3A → 80A MCB (BS EN 60898-1)
NOTE: DNO cutout is 100A. LB 80A MCB is downstream — correct discrimination.

**Step 5 — Board incomers:**
```
DB-A: 25A → 32A MCB (BS EN 60898-1, Type C for motor/catering loads) ✓
DB-B: 41A → 50A MCB (Type C) ✓
DB-C: 30A → 32A MCB (Type C) ✓
LB incoming: 69.3A → 80A MCB ✓
```

Breaking capacity: PSCC = 0.29kA = 290A.
Standard MCB minimum Icu = 1.5kA (BS EN 60898-1 Table 3) >> 290A. ✓
No concern on breaking capacity for single-phase service with high Ze.

**Step 7 — RCD:**
All socket outlets at each unit require 30mA RCBO protection.
Refrigeration and catering equipment: fixed connection — RCD not mandatory but
recommended for equipment protection.

**Step 8 — PSCC at unit boards (cables 5m, 6mm² from LB to DBs):**
```
Zcable = (2 × 0.0225 × 5) / 6 = 0.0375Ω
Ze_unit = 0.80 + 0.0375 = 0.8375Ω → PSCC = 230/0.8375 = 275A = 0.28kA
```

MCB minimum Icu of 1.5kA >> 0.28kA. ✓

**Metering note:**
One kWh sub-meter per tenant at LB. Meters wired so landlord can read all from
the single LB location. Smart meters (AMR) recommended for remote reading.

### Key JSON fields (abbreviated)

```json
{
  "supply": {
    "voltage_ll_v": 230, "voltage_ln_v": 230, "phases": 1,
    "earthing_system": "TN-C-S", "pscc_ka_at_supply": 0.29,
    "ze_ohm": 0.80, "supply_type": "DNO_underground", "cutout_fuse_a": 100
  },
  "boards": [
    {
      "id": "LB", "type": "main_lv_switchboard",
      "label": "LANDLORD BOARD", "level": 1, "phases": 1,
      "busbar_rating_a": 100,
      "incomer": {"device": "MCB", "rating_a": 80, "breaking_capacity_ka": 3,
                  "poles": 2, "standard": "BS EN 60898-1", "symbol": "MCB_2P"},
      "metering": [
        {"type": "KWH_METER", "label": "M-A — Unit A tenant meter"},
        {"type": "KWH_METER", "label": "M-B — Unit B tenant meter"},
        {"type": "KWH_METER", "label": "M-C — Unit C tenant meter"}
      ],
      "outgoing_ways": [
        {"way_id": "LB-W01", "label": "DB-A — Unit A",
         "device": "MCB", "rating_a": 32, "breaking_capacity_ka": 3, "poles": 2,
         "rcd": false, "to_board_id": "DB-A",
         "design_current_a": 25.0, "maximum_demand_kva": 4.0, "cable_ref": "C01"},
        {"way_id": "LB-W02", "label": "DB-B — Unit B",
         "device": "MCB", "rating_a": 50, "breaking_capacity_ka": 3, "poles": 2,
         "rcd": false, "to_board_id": "DB-B",
         "design_current_a": 41.0, "maximum_demand_kva": 7.1, "cable_ref": "C02"},
        {"way_id": "LB-W03", "label": "DB-C — Unit C",
         "device": "MCB", "rating_a": 32, "breaking_capacity_ka": 3, "poles": 2,
         "rcd": false, "to_board_id": "DB-C",
         "design_current_a": 30.0, "maximum_demand_kva": 4.8, "cable_ref": "C03"}
      ],
      "pscc_ka": 0.29, "total_installed_load_kva": 19.0,
      "maximum_demand_kva": 16.0, "overall_diversity_factor": 0.72
    }
  ],
  "calculation_summary": {
    "total_installed_load_kva": 19.0, "maximum_demand_kva": 16.0,
    "overall_diversity_factor": 0.72, "incoming_mccb_rating_a": 80,
    "supply_pscc_ka": 0.29, "earthing_system": "TN-C-S",
    "rcd_protected_ways": 9,
    "assumptions": [
      "PF = 0.85–0.90 assumed per load type — confirm with equipment schedules",
      "Diversity 0.70–0.75 for small retail units — confirm with client",
      "Single-phase supply assumed for all tenant units"
    ]
  }
}
```
