# NFPA 70 (NEC) — Worked Examples

7 worked examples covering the highest-value design territory. Each follows
the structure: **Given inputs → NEC article path → Calculation → Decision → AHJ-acceptance note**.

---

## Example 1 — Single-family dwelling 200 A service load calc

### Inputs

- 2400 ft² dwelling, single-phase 120/240 V, 200 A service
- Cooking: 8 kW range, 1.2 kW oven (separate), 0.8 kW microwave
- Laundry: dryer 5 kW
- Water heater: 4.5 kW
- HVAC: 3.5-ton AC (24 A on 240 V), 8 kW heat strip backup

### NEC article path

- Art 220 (load calculations) — two methods available: Standard (220.40) and Optional (220.82). Choose smaller.
- Art 220.12 (general lighting load by occupancy)
- Art 220.55 (cooking equipment demand)
- Art 220.82(C) (Optional HVAC inclusion)

### Calculation — Standard Method (220.40)

| Load category | VA | Demand factor | Calc demand |
|---|---|---|---|
| General lighting (3 VA × 2400 ft²) | 7,200 | 100% on first 3,000 + 35% remainder | 3,000 + 35% × 4,200 = 4,470 |
| Two small-appliance branch circuits | 3,000 | 100% on first 3,000 + 35% remainder (combined with lighting) | (included above) |
| Laundry branch circuit | 1,500 | 100% / 35% (combined) | (included above) |
| Cooking — range 8 kW + oven 1.2 kW + microwave 0.8 kW (10 kW total) | 10,000 | Table 220.55 Note 4: 80% for total ≥3.5 kW = 8,000 | 8,000 |
| Dryer | 5,000 | 100% (≤4 units) | 5,000 |
| Water heater | 4,500 | 100% | 4,500 |
| HVAC larger of: AC (5,760 VA) or heat (8,000 VA) | 8,000 | 100% | 8,000 |
| **Total demand** | | | **29,970 VA** |

Standard method: 29,970 / 240 = 125 A → 200 A service adequate.

### Calculation — Optional Method (220.82)

| Load category | VA | Demand factor | Calc demand |
|---|---|---|---|
| General loads: lighting (7,200) + small-appl (3,000) + laundry (1,500) + range/oven/microwave (10,000) + dryer (5,000) + water heater (4,500) | 31,200 | 100% first 10 kVA + 40% remainder | 10,000 + 40% × 21,200 = 18,480 |
| HVAC (larger of AC or heat) | 8,000 | 100% | 8,000 |
| **Total demand** | | | **26,480 VA** |

Optional method: 26,480 / 240 = 110 A → smaller than Standard. Use Optional.

### Decision

Service ampacity 110 A required; 200 A service is well-sized with spare capacity.

### AHJ note

Document the calculation choice on the load calc sheet. Optional Method is
common for residential because it usually gives a lower (compliant) service
size. Pre-built dwelling forms (CEC plan check, etc.) typically accept either.

---

## Example 2 — Strip mall service & feeder design

### Inputs

- 3 retail units, each 2,000 ft²; 1 restaurant unit 3,500 ft²
- 480Y/277 V 3-phase service for lighting/HVAC; 208/120 V transformed at each tenant
- Retail: lighting 3 VA/ft² + receptacles 30 outlets × 180 VA + 5-ton AC each
- Restaurant: kitchen equipment 35 kVA + lighting 3 VA/ft² + 7.5-ton AC

### NEC article path

- Art 215 (feeders)
- Art 220.42 (general lighting demand factors for non-dwelling — Table 220.42)
- Art 220.44 (receptacle demand factor — 100% first 10 kVA, 50% remainder)
- Art 230 (services — single service for the strip mall, with sub-feeders to each tenant)
- Art 240.21 (feeder taps — relevant if any tenant > 200 A)

### Calculation per tenant — Retail (2,000 ft²)

| Load | VA | Demand factor | Calc demand |
|---|---|---|---|
| Lighting (3 × 2,000) | 6,000 | 100% non-continuous, 125% if continuous (assume continuous) | 6,000 × 1.25 = 7,500 |
| Receptacles (30 × 180) | 5,400 | 100% first 10 kVA, 50% > 10 kVA → 5,400 × 100% | 5,400 |
| AC 5-ton | ~6,000 | 100% | 6,000 |
| **Total per retail tenant** | | | **18,900 VA** |

### Calculation — Restaurant tenant

| Load | VA | Demand factor | Calc demand |
|---|---|---|---|
| Lighting (3 × 3,500 × 1.25 cont.) | 13,125 | | 13,125 |
| Receptacles (20 × 180) | 3,600 | 100% | 3,600 |
| AC 7.5-ton | ~9,000 | 100% | 9,000 |
| Kitchen equipment (Table 220.56 demand) | 35,000 × 1.0 demand factor (≤2 units) | 35,000 |
| **Total restaurant** | | | **60,725 VA** |

### Total demand

3 × 18,900 + 60,725 = 117,425 VA. At 480Y/277 V: 117,425 / (480 × √3) ≈ 141 A. Use 200 A main with 30% spare.

### Decision

- 200 A 480Y/277 V main service
- Sub-feeders to each tenant sized per tenant load
- Coordinate tenant meters with utility

### AHJ note

Use Standard Method (220.40) — multi-occupancy strip mall, individual tenant
calc per Art 220.12-44. Receptacle demand factor (220.44) is generous for
commercial; coordinate with the demand factor early.

---

## Example 3 — Motor circuit, 50 hp 460 V 3-phase

### Inputs

- 50 hp 460 V 3-phase induction motor, Service Factor 1.15
- Locked rotor code F (3.55-3.9 kVA per hp ratio of locked rotor to full load)

### NEC article path

- Art 430.6 (full-load current from Table 430.250)
- Art 430.22 (conductor sizing)
- Art 430.32 (overload)
- Art 430.52 (branch-circuit OCPD)
- Art 430.102 (disconnect within sight)
- Art 250.122 (EGC)

### Calculation

**Step 1 — FLA from Table 430.250:** 50 hp 460 V 3-phase → 65 A FLA.

**Step 2 — Branch-circuit conductor (430.22):** 65 × 125% = 81.25 A → smallest THWN-2 conductor at 75 °C column meeting ≥81.25 A → #4 AWG Cu (ampacity 85 A).

**Step 3 — Overload (430.32):** 65 A × 115% = 74.75 A (SF 1.15). Overload set ≤74.75 A. Use NEMA size 4 starter with adjustable thermal overload set at 75 A.

**Step 4 — Branch-circuit OCPD (430.52 Table 430.52(C)(1)):**
- Inverse-time circuit breaker: 65 × 250% = 162.5 A → use 175 A breaker (next standard size up per 240.6)
- Dual-element time-delay fuse: 65 × 175% = 113.75 A → use 125 A fuse

Engineer choice (typical): 175 A inverse-time circuit breaker.

**Step 5 — Disconnect (430.102):** Disconnect within sight of motor. Use 200 A 3-pole disconnect rated for motor service.

**Step 6 — EGC (250.122 Table):** OCPD = 175 A → EGC = #6 Cu (Table 250.122).

### Decision

| Component | Size | Notes |
|---|---|---|
| Branch-circuit conductor | #4 AWG Cu THWN-2 (3-phase + #6 EGC) | At 75 °C ampacity 85 A ≥ 81.25 A required |
| Overload | NEMA 4 starter, thermal element set at 75 A | |
| Branch-circuit OCPD | 175 A inverse-time CB | Per 430.52 |
| Disconnect | 200 A 3P disconnect, within sight of motor | |
| EGC | #6 Cu | Per Table 250.122 |

### AHJ note

Submit motor schedule showing TABLE FLA used for conductor/OCPD and
NAMEPLATE FLA for overload — these are DIFFERENT values per 430.6.

---

## Example 4 — Gas station forecourt hazardous location

### Inputs

- Gasoline dispenser island, 4 dispensers, fuel-tank vents at site perimeter
- Need to classify the forecourt and size raceway/equipment

### NEC article path

- Art 514 (motor fuel dispensing)
- Art 500-503 (hazardous Class/Division) OR Art 505-506 (Class/Zone)
- Art 501.15 (seal-off requirements)

### Classification (514.3)

**Class I Locations:**

| Location | Class/Division | Class/Zone equivalent |
|---|---|---|
| Inside dispenser | Class I Div 1 | Class I Zone 0/1 |
| Within 18 in of grade, 20 ft horizontal from dispenser | Class I Div 2 | Class I Zone 2 |
| Tank vent: within 3 ft | Class I Div 1 | Zone 1 |
| Tank vent: 3-10 ft | Class I Div 2 | Zone 2 |

### Equipment selection

Equipment within the Class I Div 2 envelope must be either:
- Listed for Class I Div 2 (Group D — gasoline), OR
- Listed for Class I Zone 2 IIA (gasoline), and the equipment must be marked accordingly

Mixing Division-listed and Zone-listed equipment in the same envelope is
permitted IF the AHJ accepts the conversion matrix (see
hazardous-locations-classification.json). Best practice: pick one system
per project.

### Conduit seals (501.15)

- At the boundary where raceway exits the Class I Div 2 envelope, install a Class I Div 2 listed seal-off (e.g. EYS-style)
- Within the dispenser, additional seals at equipment entries containing arcing devices

### Decision

- Specify equipment listed for Class I Div 1 (in the dispenser) and Class I Div 2 (in the 18-in/20-ft envelope)
- Seal-off conduit fittings at boundary and at dispenser entries
- Use RMC or IMC raceway in Class I Div 1; EMT not permitted in Class I Div 1

### AHJ note

Document the classification plan on the site drawing — many AHJs require
the classification envelope to be shaded on the layout. Coordinate with
the fuel-tank installer and the tank-vent location.

---

## Example 5 — PV residential rooftop 10 kW

### Inputs

- 10 kW residential PV (32 modules at 320 W each), 8 strings of 4 modules each, 240 V single-phase grid-tie inverter
- Module Voc 40 V, Vmp 32 V, Isc 10 A, Imp 9.4 A
- Coldest expected temp at site: -10 °C (correction factor 1.10 per Table 690.7(A))
- Backfeed circuit breaker at panelboard with 200 A main breaker, 200 A busbar

### NEC article path

- Art 690.7 (max voltage)
- Art 690.8 (circuit sizing)
- Art 690.9 (OCPD)
- Art 690.11 (DC arc fault)
- Art 690.12 (rapid shutdown)
- Art 705.12(B) (interconnection at busbar — sum rule vs 120% rule)

### Calculation

**Step 1 — Maximum system voltage (690.7):**
4 modules × 40 V Voc × 1.10 (cold-temp correction) = 176 V DC per string. Well within 600 V dwelling limit.

**Step 2 — PV source circuit current (690.8):**
1 string × 10 A Isc × 125% = 12.5 A. Conductor ampacity needs ≥12.5 A × 125% = 15.625 A. Use #10 AWG PV wire (ampacity 30-40 A in free air, easily meets).

**Step 3 — PV output circuit current (690.8):**
8 strings × 12.5 A = 100 A per inverter input. Conductor sized at 100 × 125% = 125 A → #1 AWG Cu THWN-2 at 75 °C ampacity 130 A.

**Step 4 — OCPD on PV output (690.9):** ≥156% of Isc = 100 × 156% = 156 A. Round up to 175 A standard size.

**Step 5 — Inverter AC output:** 10 kW / 240 V = 41.7 A. AC output conductor at 125% × 41.7 = 52.1 A. Use #6 Cu, ampacity 65 A at 75 °C.

**Step 6 — AC OCPD (705.12 interconnection):** Inverter output breaker at 60 A (covers 52.1 A × 125% margin).

**Step 7 — 705.12 busbar interconnection rule:**
- Sum rule: 60 A inverter breaker + 200 A main breaker = 260 A > 200 A busbar. FAILS sum rule.
- 120% rule: 200 A × 120% = 240 A. 60 + 200 = 260 A > 240 A. STILL FAILS.
- Solution: Downgrade main breaker OR upgrade busbar OR use center-fed busbar configuration.
- For typical residential, this often requires a "supply-side" tap (PV breaker between meter and main panel) per 705.12(A).

**Step 8 — Rapid shutdown (690.12):**
- Conductors within 1 ft of array on roof → ≤30 V within 30 s
- Conductors > 5 ft outside array (e.g. running to inverter) → de-energized to ≤30 V within 30 s
- Module-level rapid shutdown initiator (typically MLPE microinverter or rapid-shutdown box at array)
- Marking on roof, at array boundary, at first responder location

**Step 9 — DC AFCI (690.11):**
Required because system operates ≥80 V DC. Modern inverters with integrated DC AFCI satisfy this.

### Decision

- 8 strings × 4 modules each, 176 V DC max system voltage
- DC conductors: #10 AWG PV wire (source) → #1 AWG Cu (output to inverter, 125% margin)
- AC conductor: #6 Cu (60 A breaker)
- Interconnection: supply-side tap between meter and main panel (705.12(A))
- Module-level rapid shutdown initiator
- DC AFCI per integrated inverter feature

### AHJ note

Submit single-line diagram showing all DC and AC circuits with OCPD ratings,
conductor sizes, and the rapid-shutdown plan. Most jurisdictions require
plan check before installation.

---

## Example 6 — EV charging, 5-station commercial bay

### Inputs

- 5 × 32 A Level 2 EVSE (J1772), 7.7 kW each, 240 V single-phase
- All on a shared feeder with load management; want to minimize feeder size

### NEC article path

- Art 625.41 (branch-circuit conductor sizing)
- Art 625.42 (rating + load management)
- Art 215 (feeder sizing)
- Art 240 (OCPD)

### Calculation

**Without load management (worst case — all 5 EVSEs at max simultaneously):**

5 × 32 A × 125% (continuous) = 200 A on the feeder.

**With load management (625.42(A)(2)):**

Suppose load management limits the feeder to 100 A maximum (managing power distribution among connected vehicles).

- Feeder ampacity ≥ 100 A × 125% = 125 A
- Each EVSE branch circuit: 32 A × 125% = 40 A conductor (use #8 Cu THWN-2 at 75 °C ampacity 50 A)
- Each EVSE OCPD: 40 A
- Feeder conductor: 125 A → #1 Cu THWN-2 (75 °C 130 A)
- Feeder OCPD: 125 A

### Documentation requirements

- Load management scheme documented on the design narrative
- Compliance with 625.42(A)(2): "An automatic load management system ... that is listed for the purpose..."
- Identification at the feeder: "EV charging load management to 100 A maximum"

### Decision

- 5 × 40 A 1-pole branch circuits, #8 Cu each
- Feeder 125 A, #1 Cu, with documented load management to 100 A
- 200 A feeder is over-sized without load management; 125 A with — major cost savings

### AHJ note

Load management is the most common path for multi-EVSE installations. Submit
the load management documentation explicitly — the AHJ will verify that
without it, the feeder would need to be 200 A.

---

## Example 7 — Hospital essential electrical system

### Inputs

- 200-bed hospital, mixed Category 1 (ICU, OR) + Category 2 (patient rooms) areas
- Required: Type 1 EES per Art 517.30 — three branches (Life Safety, Critical, Equipment)
- On-site standby generator + utility service

### NEC article path

- Art 517.30 (Type 1 EES — three branches)
- Art 517.31 (Type 1 distribution and wiring)
- Art 700 (Emergency System — Life Safety Branch)
- Art 700.27 / 700.32 (selective coordination)

### Architecture

**Type 1 EES three branches** (all on the EES bus, all transfer-switched):

| Branch | Loads | Restoration time |
|---|---|---|
| Life Safety Branch | Emergency egress lighting, fire alarm, exit signs, medical gas alarms | ≤10 s |
| Critical Branch | Patient-care receptacles in Category 1/2 spaces, isolated power systems, certain HVAC | ≤10 s |
| Equipment Branch | Equipment essential to facility operation (sterilization, refrigeration of pharma, etc.) | ≤10 s (or up to 60 s for some Equipment Branch loads) |

### Source transfer

- Two independent sources: utility (Primary) + on-site generator (Alternate)
- Generator sized to carry ALL three branches simultaneously
- Three transfer switches (one per branch) — typically located close to the EES bus
- Generator start ≤10 s; generator capable of sustained operation ≥1.5 hours minimum (per 517.30(C)(3))

### Selective coordination (700.32 / 701.32)

- OCPDs on Type 1 EES branches must selectively coordinate with all upstream OCPDs in the full available fault-current range
- Engagement of a coordination study with the OCPD manufacturer at design stage

### Wiring (517.31, 700.10)

- Critical Branch wiring INDEPENDENT of normal-source wiring (separate raceway, separate distribution)
- Life Safety Branch wiring also independent — most prescriptive
- Equipment Branch may share raceways with Critical Branch under certain conditions (517.31(A))

### Decision

- Three separate EES distribution panels (Life Safety, Critical, Equipment)
- Three independent transfer switches per 517.31(C)
- Generator sized for all three branches simultaneously
- Coordination study verifying selective coordination per 700.32

### AHJ note

Coordinate with NFPA 99 (Health Care Facilities Code) and the AHJ's hospital
review process. Most state health departments have additional requirements
beyond NEC + NFPA 99.

---

These 7 worked examples cover the highest-value NEC design territory.
For additional examples on specific articles, see the per-article JSON
files' `usage_notes` and `common_errors` fields.
