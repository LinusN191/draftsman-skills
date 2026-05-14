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
    "ze_ohm": 0.80, "supply_type": "DNO_underground", "dno_cutout_fuse_a": 100
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

---

## Example 4 — New-build office, life safety circuits, Zs check, SPD, neutral oversizing

This example demonstrates the v1.1.0 additions: life safety circuit identification,
Zs disconnection time verification, SPD risk assessment, and neutral oversizing for
harmonic loads.

### Input

```
Building: new-build 4-storey office, 3000m² GIA, England
Supply: 3-phase TN-C-S, 400V/230V, 50Hz, DNO underground (urban)
Ze at supply terminals: 0.30 Ω (confirmed by DNO letter dated [project date])
MIC: 350A (DNO connection agreement)
DNO cut-out: 100A per phase
Lightning protection system: yes (on roof) → Type 1 SPD required
New-build: yes — AD Part L 2021 sub-metering obligations apply

Load schedule:
  SDB-GF  (Ground Floor, 750m²)
    General lighting:          12kW, PF 1.00
    Socket outlets:            15kW, PF 0.90
    IT equipment (dense):      20kW, PF 0.90 (non-linear)
  SDB-L1  (Level 1, 750m²) — same profile as GF: 47kW total
  SDB-L2  (Level 2, 750m²) — same profile as GF: 47kW total
  SDB-L3  (Level 3, 750m²) — same profile as GF: 47kW total
  SDB-HVAC (Basement plant room)
    AHU (continuous):          45kW, PF 0.85, 3-phase
    VFDs (FCUs, VAVs):         30kW, PF 0.85, 3-phase (non-linear)
  SDB-ESSN (Essential services — life safety)
    Fire alarm panel:           2kVA, PF 1.00, single-phase
    Emergency lighting:         1.5kVA, PF 1.00, single-phase
    Smoke extract fans:         7.5kW, PF 0.85, 3-phase

Generator: 50kVA diesel standby — essential services bus only
Cable lengths: MSB to all SDBs via basement riser — GF 10m, L1 20m,
              L2 30m, L3 40m, HVAC 8m, ESSN 5m
All sub-mains on cable tray, method E. ESSN cables in dedicated fire-rated
conduit.
```

### Reasoning shown in chat

**Step 1 — Input validation:**

Ze = 0.30Ω confirmed by DNO letter. MIC = 350A. All loads specified.
New-build in England — AD Part L 2021 applies. Sub-metering required.
LPS present on roof → Type 1 SPD mandatory at MSB origin (Regulation 443.4).

**Step 2 — Hierarchy:**
```
DNO Supply (3-phase, 400V, TN-C-S, Ze = 0.30Ω, MIC = 350A)
  └── MSB (Main LV Switchboard, Basement Plant Room)
        ├── MAINS BUS ─────────────────────────────────────┐
        │     ├── SDB-GF   (Ground Floor — 47kW)           │
        │     ├── SDB-L1   (Level 1 — 47kW)                │
        │     ├── SDB-L2   (Level 2 — 47kW)                │
        │     ├── SDB-L3   (Level 3 — 47kW)                │
        │     └── SDB-HVAC (Plant — 75kW)                  │
        │                                                   │
        └── ESSENTIAL BUS ← ATS ← GENERATOR (50kVA) ───────┘
              └── SDB-ESSN (Life safety — 11kVA)
```

Life safety systems (fire alarm, emergency lighting, smoke extract) served
exclusively from essential bus. No general loads on SDB-ESSN.

**Step 3a — Design currents:**
```
Each office floor (GF/L1/L2/L3):
  kW total = 12 + 15 + 20 = 47kW, PF mixed ≈ 0.92 (weighted average)
  Ib = 47,000 / (1.732 × 400 × 0.92) = 47,000 / 637.9 = 73.7A → 74A

SDB-HVAC:
  AHU:  Ib = 45,000 / (1.732 × 400 × 0.85) = 76.5A → 77A
  VFDs: Ib = 30,000 / 587.9 = 51.0A → 52A
  Total: 129A

SDB-ESSN:
  Fire alarm: Ib = 2000 / 230 = 8.7A → 9A
  Em. lighting: Ib = 1500 / 230 = 6.5A → 7A
  Smoke extract: Ib = 7500 / (1.732×400×0.85) = 12.8A → 13A
  Total: 29A (no diversity on life safety)
```

[ASSUMPTION: PF = 0.92 weighted average for office floors (lighting unity,
sockets/IT 0.90). Confirm from equipment schedules before tender.]

**Step 3b — Motor check (smoke extract fan):**
```
Fan FLC = 12.8A (DOL start assumed)
Starting current = 6–8 × FLC = 77–102A
MCB for smoke extract: Curve D (10–20× In) to ride DOL inrush
  In ≥ 13A → 16A Type D MCB
```

[ASSUMPTION: Smoke extract fan DOL started. Confirm starting method with
mechanical engineer — VFD or star-delta may reduce cable/device sizes.]

**Step 4 — Diversity and maximum demand:**

| Circuit | Installed Ib | Load type | Diversity | Demand |
|---|---|---|---|---|
| SDB-GF lighting | 20.9A | Lighting | 0.90 | 18.8A |
| SDB-GF sockets | 26.2A | Sockets | 0.50 | 13.1A |
| SDB-GF IT | 34.9A | IT | 0.80 | 27.9A |
| **SDB-GF total** | **74A** | | | **59.8A** |
| SDB-L1 (same) | 74A | | | 59.8A |
| SDB-L2 (same) | 74A | | | 59.8A |
| SDB-L3 (same) | 74A | | | 59.8A |
| SDB-HVAC AHU | 77A | Continuous HVAC | 1.00 | 77.0A |
| SDB-HVAC VFDs | 52A | Intermittent HVAC | 0.75 | 39.0A |
| **SDB-HVAC total** | **129A** | | | **116.0A** |
| SDB-ESSN (all) | 29A | Life safety | 1.00 | 29.0A |

MSB maximum demand = 59.8 × 4 + 116 + 29 = 384.2A
→ MSB incomer: 400A MCCB (next standard size above 384A)
→ 400A < MIC 350A? **NO — 400A > 350A MIC.**

```
[NON-COMPLIANCE RISK: Calculated maximum demand 384A exceeds MIC 350A.
Options: (1) Apply additional building diversity to confirm demand ≤ 350A
with robust justification; (2) apply for increased MIC from DNO (allow
12+ weeks); (3) reduce connected load. Do not issue for tender without
resolving against MIC limit.]
```

With building-level diversity of 0.90 applied (cross-floor diversity in a
speculative office — not all floors at peak simultaneously):
```
Revised MSB demand = 59.8 × 4 × 0.90 + 116 + 29 = 215.3 + 145 = 360.3A
```

Still marginally above 350A. Flag as [NON-COMPLIANCE RISK] and advise DNO
consultation. Provisionally select 400A MCCB for design; confirm with DNO.

**Step 5 — Protective devices:**
```
SDB-GF through SDB-L3:  Ib = 74A → 80A MCCB, Icu 16kA ✓
SDB-HVAC:              Ib = 129A → 160A MCCB, Icu 16kA ✓
SDB-ESSN:              Ib = 29A → 40A MCCB, Icu 16kA ✓ (life safety — specify
                        MCCB not MCB for robust discrimination)
MSB incomer:           400A MCCB, Icu 36kA (urban supply — specify 36kA minimum)
Generator incomer:     50kVA FLC = 72A → 80A MCCB, Icu 10kA
```

**Step 6 — Cable types:**

Office sub-mains: XLPE/SWA/LSZH (public areas and riser routes in escape
corridors — use LSZH throughout).

Life safety cables:
- Fire alarm: FP200 Gold 2C×1.5mm² (IEC 60331-1, 30 min at 830°C)
- Emergency lighting: FP200 Gold (IEC 60331-1, 60 min circuit integrity)
- Smoke extract fan: FP400 4C+CPC 2.5mm² (IEC 60331-21, 120 min at 830°C)

```
[NON-COMPLIANCE RISK: If standard XLPE cable is used for smoke extract fan,
circuit integrity cannot be guaranteed for 120 min under fire conditions.
FP400 or MICC is mandatory for this application.]
```

**Step 6d — Neutral oversizing check:**
```
Non-linear loads:
  IT equipment: 4 × 20kW = 80kW
  VFDs (HVAC): 30kW
  Total non-linear: 110kW

Total installed load: 4 × 47kW + 75kW + 11kW = 274kW
Non-linear %: 110 / 274 = 40%

40% >> 15% threshold → neutral upsized to 150% of phase conductor
on sub-mains serving IT-dense floors (SDB-GF through SDB-L3) and
SDB-HVAC.
```

[ASSUMPTION: Non-linear loading estimated at 40% of total. Neutral conductor
upsized to 150% of phase conductor (e.g. 25mm² neutral where 16mm² phase
for office sub-mains). Confirm with power quality survey before cable selection.]

**Step 7 — Breaking capacity (PSCC propagation):**
```
ρ = 0.0225 Ω·mm²/m

SDB-GF   (10m, 16mm²):  Zcable = 2×0.0225×10/16 = 0.028Ω → Ze = 0.328 → PSCC = 0.70kA
SDB-L1   (20m, 16mm²):  Zcable = 0.056Ω → Ze = 0.356 → PSCC = 0.65kA
SDB-L2   (30m, 16mm²):  Zcable = 0.084Ω → Ze = 0.384 → PSCC = 0.60kA
SDB-L3   (40m, 16mm²):  Zcable = 0.113Ω → Ze = 0.413 → PSCC = 0.56kA
SDB-HVAC  (8m, 50mm²):  Zcable = 2×0.0225×8/50 = 0.007Ω → Ze = 0.307 → PSCC = 0.75kA
SDB-ESSN  (5m, 4mm²):   Zcable = 2×0.0225×5/4  = 0.056Ω → Ze = 0.356 → PSCC = 0.65kA
```

All PSCC values << device Icu values (16kA minimum). ✓

| Board | Ze (Ω) | PSCC (kA) | Device Icu (kA) | OK? |
|---|---|---|---|---|
| MSB | 0.300 | 0.77 | 36 | ✓ |
| SDB-GF | 0.328 | 0.70 | 16 | ✓ |
| SDB-L1 | 0.356 | 0.65 | 16 | ✓ |
| SDB-L2 | 0.384 | 0.60 | 16 | ✓ |
| SDB-L3 | 0.413 | 0.56 | 16 | ✓ |
| SDB-HVAC | 0.307 | 0.75 | 16 | ✓ |
| SDB-ESSN | 0.356 | 0.65 | 16 | ✓ |

**Step 8 — Zs check (SDB-L3 socket circuit as worst case):**
```
Circuit: SDB-L3 → socket outlets, 16A Type C RCBO, 20m of 2.5mm²+1.5mm² CPC

R1 = 0.0225 × 20 / 2.5 = 0.180Ω  (phase conductor)
R2 = 0.0225 × 20 / 1.5 = 0.300Ω  (CPC)
Ze at SDB-L3 = 0.413Ω

Zs = 0.413 + 0.180 + 0.300 = 0.893Ω
Zs_max for 16A Type C MCB (0.4s, Table 41.2) = 1.44Ω

0.893Ω < 1.44Ω ✓ — 0.4s disconnection confirmed.
```

Zs check passes for the worst-case floor (SDB-L3). All other floors are
closer to the MSB and will have lower Zs values.

**Step 9 — Protection coordination:**
```
MSB 400A MCCB (S-delay 100ms) → SDB MCCBs (Instantaneous)
Ratio: 400A / 80A = 5.0 >> 1.6 ✓ — current discrimination adequate

ESSN MCCB 40A → internal MCBs at 16A
Ratio: 40A / 16A = 2.5 > 1.6 ✓ — current discrimination adequate
```

**Step 11 — Life safety circuits:**
```
Fire alarm (BS 5839-1):
  Source: SDB-ESSN (essential bus) → FAP (Fire Alarm Panel)
  Cable: FP200 Gold 2C×1.5mm², IEC 60331-1, 30 min circuit integrity
  Diversity: 1.00 (no diversity on life safety)

Emergency lighting (BS 5266-1):
  Source: SDB-ESSN (essential bus) → CEB (Central Emergency Battery) or
  distributed self-contained fittings
  Cable: FP200 Gold 2C×1.5mm², IEC 60331-1, 60 min circuit integrity

Smoke extract fans (BS 9999 / BS EN 12101-3):
  Source: SDB-ESSN (essential bus) → dedicated MCB per fan
  Cable: FP400 4C+CPC×2.5mm², IEC 60331-21, 120 min circuit integrity
  Starting method: DOL, Curve D MCB 16A
  No other loads on this circuit.
```

All life safety circuits confirmed segregated in dedicated fire-rated conduit
separate from general cable containment.

**Step 13 — Generator:**
```
Essential loads (on generator):
  Fire alarm panel:     2kVA
  Emergency lighting:   1.5kVA
  Smoke extract fans:   7.5kW / PF 0.85 = 8.8kVA
  Total essential:     12.3kVA

Generator: 50kVA diesel — 12.3kVA essential load = 25% loading → adequate ✓
Generator FLC: 50,000 / (1.732 × 400) = 72.2A → 80A MCCB incomer

Non-essential circuits shed on generator: SDB-GF, SDB-L1, SDB-L2, SDB-L3,
SDB-HVAC.

ATS: 2-way, AMF, ≤15s transfer time
Interlocking: electrical + mechanical — Regulation 551.7 applies
```

[ASSUMPTION: Generator PSCC = 3 × 72.2A = 217A = 0.22kA. MCCB Icu 10kA >>
0.22kA. Confirm sub-transient reactance from manufacturer.]

**Step 14 — SPD assessment:**
```
Risk factors present:
  ✓ LPS on building → Type 1 SPD mandatory at MSB origin
  ✓ New-build commercial building
  ✓ IT loads present (sensitive)

SPD specification:
  MSB: Type 1 + Type 2 combined SPD (BS EN 61643-11)
  Each SDB: Type 2 SPD
  Server room (if present): Type 3 at distribution sockets

Type 1/Type 2 coordination: 10m cable separation between MSB Type 1 and
SDB Type 2 SPDs in riser. If riser < 10m, fit coordination inductor.
```

[ASSUMPTION: Formal lightning risk assessment (BS EN 62305-2) not yet
completed. SPD type selections above are preliminary. Confirm with lightning
protection specialist before procurement.]

**Step 15 — Earthing and sub-metering:**
```
Earthing system: TN-C-S (PME)
Main bonding conductor: supply cable assumed 95mm² → 16mm² Cu per Table 54.8
Bonding connections: gas, water, structural steel at MSB MET
TN-C-S restrictions: no PME earth for EV chargers in accessible areas
  (Regulation 312.2.3) — note on drawing if EV charging specified later

AD Part L 2021 sub-metering obligations:
  MSB:      Landlord main meter (all building) — mandatory
  HVAC:     SDB-HVAC sub-meter (AHU + VFDs > 50kWh/day) — mandatory
  IT/floors: Sub-meters on each SDB-GF through SDB-L3 (IT loads > 50kWh/day)
             — mandatory
  Emergency: SDB-ESSN — not required (< 50kWh/day)

BREEAM Ene04: if targeted, AMR meters with 30-min logging on all sub-meters.
```

### Key JSON fields (abbreviated)

```json
{
  "supply": {
    "voltage_ll_v": 400, "voltage_ln_v": 230, "phases": 3,
    "earthing_system": "TN-C-S", "ze_ohm": 0.30,
    "pscc_ka_at_supply": 0.77, "mic_a": 350,
    "dno_cutout_fuse_a": 100, "overhead_supply": false,
    "g99_required": false
  },
  "boards": [
    {
      "id": "MSB", "type": "main_lv_switchboard", "form_of_separation": "Form3b",
      "busbar_rating_a": 500, "busbar_icw_ka": 36,
      "incomer": {
        "device": "MCCB", "rating_a": 400, "breaking_capacity_ka": 36,
        "poles": 4, "symbol": "MCCB_4P"
      },
      "spd": true, "spd_type": "T1",
      "metering": [
        {"type": "CT", "ratio": "630/5A", "class": "1", "purpose": "revenue"},
        {"type": "KWH_METER", "label": "LL01 — Landlord Main Meter"}
      ],
      "earthing": {
        "main_earth_terminal": true, "earth_conductor_mm2": 35,
        "bonding_connections": ["gas", "water", "structural_steel"]
      },
      "pscc_ka": 0.77, "total_installed_load_kva": 274.0,
      "maximum_demand_kva": 223.8, "overall_diversity_factor": 0.82
    },
    {
      "id": "SDB-ESSN", "type": "emergency_board",
      "label": "ESSENTIAL SERVICES BOARD", "level": 2,
      "life_safety": true, "life_safety_source": "essential_bus",
      "form_of_separation": "Form2b",
      "incomer": {
        "device": "MCCB", "rating_a": 40, "breaking_capacity_ka": 16,
        "poles": 4, "symbol": "MCCB_4P"
      },
      "spd": false,
      "pscc_ka": 0.65, "zs_ohm": null, "zs_compliant": true
    }
  ],
  "connections": [
    {
      "id": "C-ESSN-FA", "label": "Fire Alarm Circuit",
      "conductors": "2C+CPC", "conductor_size_mm2": 1.5,
      "neutral_size_mm2": 1.5, "cpc_size_mm2": 1.0,
      "cable_type": "FP200", "lszh": false,
      "fire_rated": true, "fire_rating_minutes": 30,
      "armoured": false, "installation_method": "B1"
    },
    {
      "id": "C-ESSN-SE", "label": "Smoke Extract Fan Circuit",
      "conductors": "4C+CPC", "conductor_size_mm2": 2.5,
      "neutral_size_mm2": 2.5, "cpc_size_mm2": 1.5,
      "cable_type": "FP400", "lszh": false,
      "fire_rated": true, "fire_rating_minutes": 120,
      "armoured": false, "installation_method": "B1"
    },
    {
      "id": "C-L3", "label": "MSB to SDB-L3",
      "conductors": "4C+CPC", "conductor_size_mm2": 16,
      "neutral_size_mm2": 25,
      "cpc_size_mm2": 10,
      "cable_type": "XLPE-SWA-LSZH", "lszh": true,
      "fire_rated": false, "armoured": true,
      "installation_method": "E", "length_m": 40,
      "design_current_a": 74.0, "ccc_a": 87,
      "r1_ohm": 0.056, "r2_ohm": 0.099,
      "zs_ohm": 0.413, "pscc_at_far_end_ka": 0.56
    }
  ],
  "life_safety_circuits": [
    {
      "system": "fire_alarm", "standard": "BS 5839-1:2017",
      "board_id": "SDB-ESSN", "cable_type": "FP200",
      "fire_rating_minutes": 30, "power_source": "essential_bus",
      "circuit_integrity_standard": "IEC 60331-1"
    },
    {
      "system": "emergency_lighting", "standard": "BS 5266-1:2016",
      "board_id": "SDB-ESSN", "cable_type": "FP200",
      "fire_rating_minutes": 60, "power_source": "essential_bus",
      "circuit_integrity_standard": "IEC 60331-1"
    },
    {
      "system": "smoke_extract", "standard": "BS EN 12101-3",
      "board_id": "SDB-ESSN", "cable_type": "FP400",
      "fire_rating_minutes": 120, "power_source": "essential_bus",
      "circuit_integrity_standard": "IEC 60331-21"
    }
  ],
  "spd_assessment": {
    "risk_assessment_completed": false,
    "lps_on_building": true,
    "overhead_supply": false,
    "sensitive_loads_present": true,
    "spd_required": true,
    "spd_type_at_origin": "T1",
    "t1_t2_coordination_method": "10m_cable_separation",
    "notes": [
      "LPS present — Type 1 SPD mandatory at MSB per BS EN 61643-11 / Reg 443.4",
      "Formal risk assessment per BS EN 62305-2 required before procurement"
    ]
  },
  "load_shedding": {
    "enabled": true,
    "essential_boards": ["SDB-ESSN"],
    "non_essential_boards": ["SDB-GF","SDB-L1","SDB-L2","SDB-L3","SDB-HVAC"],
    "essential_load_kva": 12.3,
    "transfer_time_s": 15
  },
  "metering_schedule": [
    {"id": "M01", "board_id": "MSB",      "label": "Landlord main meter",
     "type": "KWH_METER", "class": "1", "part_l_required": true, "breeam_ene04": true},
    {"id": "M02", "board_id": "SDB-HVAC", "label": "HVAC plant sub-meter",
     "type": "KWH_METER", "class": "1", "part_l_required": true, "breeam_ene04": true},
    {"id": "M03", "board_id": "SDB-GF",   "label": "GF office sub-meter",
     "type": "KWH_METER", "class": "1", "part_l_required": true, "breeam_ene04": true},
    {"id": "M04", "board_id": "SDB-L1",   "label": "L1 office sub-meter",
     "type": "KWH_METER", "class": "1", "part_l_required": true, "breeam_ene04": true},
    {"id": "M05", "board_id": "SDB-L2",   "label": "L2 office sub-meter",
     "type": "KWH_METER", "class": "1", "part_l_required": true, "breeam_ene04": true},
    {"id": "M06", "board_id": "SDB-L3",   "label": "L3 office sub-meter",
     "type": "KWH_METER", "class": "1", "part_l_required": true, "breeam_ene04": true}
  ],
  "calculation_summary": {
    "total_installed_load_kva": 274.0, "maximum_demand_kva": 223.8,
    "overall_diversity_factor": 0.82, "incoming_device_rating_a": 400,
    "supply_pscc_ka": 0.77, "earthing_system": "TN-C-S",
    "rcd_protected_ways": 16,
    "life_safety_circuits_count": 3,
    "zs_check_compliant": true,
    "breaking_capacity_compliant": true,
    "selectivity_confirmed": true,
    "spd_required": true,
    "harmonic_loading_pct": 40.0, "neutral_oversized": true,
    "g99_required": false,
    "compliant": false,
    "non_compliance_flags": [
      "Maximum demand 384A (pre building diversity) exceeds MIC 350A — confirm with DNO before tender",
      "SPD formal risk assessment (BS EN 62305-2) not completed — Type 1 selection is preliminary"
    ],
    "assumptions": [
      "PF = 0.92 weighted for office floors — confirm from equipment schedules",
      "Building-level diversity 0.90 applied to bring demand to 360A — confirm with client",
      "Non-linear loading ~40% of total — neutral oversized; confirm with power quality survey",
      "Generator PSCC = 3×FLC = 0.22kA — confirm sub-transient reactance from manufacturer",
      "Smoke extract DOL start assumed — confirm starting method with mechanical engineer"
    ]
  }
}
```
