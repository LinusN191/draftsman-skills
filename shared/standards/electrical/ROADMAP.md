# Electrical Standards Layer Roadmap

Last updated: 2026-05-17 (status snapshot)

Every standards layer the DraftsMan skills repo will ever reference, with current shipping status. Layers are stored at `shared/standards/electrical/<STANDARD_ID>/` and consumed by `electrical/<skill>/skill.manifest.json` via the `standards[]` array.

## Status legend

- **production** — full file set (terminology + parts/tables), referenced by a shipped skill
- **draft** — partial file set, work in progress
- **stub** — folder + README + meta.json only, no clauses transcribed
- **planned** — listed here but no folder yet

## Roadmap table

| Layer | Title | Body | Jurisdiction | Status | Dependent skills | Priority |
|---|---|---|---|---|---|---|
| BS7671 | BS 7671:2018+A3 Wiring Regulations | BSI | GB | **production** | lighting-layout, db-layout, earthing, fault-level, cable-sizing | — |
| IEC60364 | IEC 60364 LV Installations | IEC | EU/INT | **production** | db-layout, earthing, fault-level, cable-sizing | — |
| IEC60617 | IEC 60617 Graphical Symbols | IEC | INT | **production** | sld, db-layout, earthing, fault-level | — |
| IEC60909 | IEC 60909 Short-Circuit Currents | IEC | INT | **production** | fault-level, db-layout (selectivity) | — |
| IEC61439 | IEC 61439 LV Switchgear Assemblies | IEC | INT | **production** | db-layout | — |
| NFPA70 | NEC 2023 — National Electrical Code | NFPA | US | **production** | db-layout, earthing, fault-level, cable-sizing | — |
| IEEE1584 | IEEE 1584:2018 Arc Flash Incident Energy & Boundary | IEEE | US/INT | **production** | electrical/arc-flash | HIGH (shipped 2026-05-17) |
| NFPA70E | NFPA 70E Standard for Electrical Safety in the Workplace | NFPA | US | **production** | electrical/arc-flash | HIGH (shipped 2026-05-17) |
| ANSI-Z535-4 | ANSI Z535.4:2023 Product Safety Signs and Labels | ANSI/NEMA | US (de facto INT) | **production** | electrical/arc-flash-labelling | MEDIUM (shipped 2026-05-17, v1.0.0) |
| ISO-7010 | ISO 7010:2019 Graphical Symbols — Safety Signs | ISO | INT | **production** | electrical/arc-flash-labelling | MEDIUM (shipped 2026-05-17, v1.0.0) |
| BS-5499 | BS 5499:2013 Safety Signs (UK Convention) | BSI | GB | **production** | electrical/arc-flash-labelling | MEDIUM (shipped 2026-05-17, v1.0.0) |
| BSEN60947 | BS EN 60947 Low-Voltage Switchgear and Controlgear (Parts 1-7) | BSI/CEN | EU/GB | **stub** | electrical/breaker-sizing (stub), selectivity-study (stub) | MEDIUM |
| IEC60079 | IEC 60079 Explosive Atmospheres (Multi-part: 0-20) | IEC | INT | **stub** | electrical/hazardous-locations (stub) | MEDIUM |
| ERG5-5 | Engineering Recommendation G5/5 UK Harmonic Distortion Limits | ENA | GB | **stub** | electrical/power-quality-study (stub) | MEDIUM |
| IEC61000 | IEC 61000 Electromagnetic Compatibility (EMC) (Parts 3-2, 3-12, 4-30) | IEC | INT | **stub** | electrical/power-quality-study (stub) | MEDIUM |
| IEEE519 | IEEE 519 Harmonic Control in Electrical Power Systems | IEEE | US | **stub** | electrical/power-quality-study (stub) | MEDIUM |
| BSEN60831 | BS EN 60831 Shunt Capacitors for AC Power Systems LV | BSI/CEN | EU/GB | **stub** | electrical/power-factor-correction (stub) | LOW |
| IEC61921 | IEC 61921 Power Capacitors LV — Power Factor Correction | IEC | INT | **stub** | electrical/power-factor-correction (stub) | LOW |
| BSISO8528 | BS ISO 8528 Reciprocating Engine Driven AC Gensets (Parts 1-13) | ISO/BSI | INT | **stub** | electrical/generator-sizing (stub) | HIGH (Group B) |
| NFPA110 | NFPA 110 Emergency and Standby Power Systems | NFPA | US | **stub** | electrical/generator-sizing (stub), ups-sizing (stub) | HIGH (Group B) |
| NFPA111 | NFPA 111 Stored Electrical Energy Emergency and Standby Power | NFPA | US | **stub** | electrical/ups-sizing (stub), bess-sizing (stub) | MEDIUM (Group B) |
| BSEN62040 | BS EN 62040 UPS Systems (Parts 1-3) | BSI/CEN | EU/GB | **stub** | electrical/ups-sizing (stub) | MEDIUM (Group B) |
| IEEE485 | IEEE 485 Sizing Vented Lead-Acid Batteries for Stationary Applications | IEEE | US | **stub** | electrical/ups-sizing (stub), bess-sizing (stub) | MEDIUM (Group B) |
| IEC62619 | IEC 62619 Secondary Batteries — Safety of Li-Ion Batteries and Modules | IEC | INT | **stub** | electrical/bess-sizing (stub) | MEDIUM (Group B) |
| IEC60896 | IEC 60896 Stationary Lead-Acid Batteries (Parts 1-3) | IEC | INT | **stub** | electrical/bess-sizing (stub) | MEDIUM (Group B) |
| IEC62933 | IEC 62933 Electrical Energy Storage Systems | IEC | INT | **stub** | electrical/bess-sizing (stub) | HIGH (Group C) |
| NFPA855 | NFPA 855 Stationary Energy Storage Installation | NFPA | US | **stub** | electrical/bess-sizing (stub) | HIGH (Group C) |
| UL9540 | UL 9540 Energy Storage Systems & Equipment | UL | US | **stub** | electrical/bess-sizing (stub) | MEDIUM (Group C) |
| BSEN62305 | BS EN 62305 Protection Against Lightning (Parts 1-4) | BSI/CEN | EU/GB | **stub** | electrical/lightning-protection (stub) | HIGH (Group A) |
| NFPA780 | NFPA 780 Lightning Protection Systems | NFPA | US | **stub** | electrical/lightning-protection (stub) | HIGH (Group A) |
| IEC62561 | IEC 62561 Lightning Protection System Components (Parts 1-7) | IEC | INT | **stub** | electrical/lightning-protection (stub) | HIGH (Group A) |
| BSEN61643 | BS EN 61643 Surge Protective Devices (Parts 11-22) | BSI/CEN | EU/GB | **stub** | electrical/spd-selection (stub) | MEDIUM (Group A) |
| BSEN60076 | BS EN 60076 Power Transformers (Parts 1-23) | BSI/CEN | EU/GB | **stub** | electrical/transformer-sizing (stub) | MEDIUM (Group B) |
| IEEEC57 | IEEE C57 Power Transformer Standards (C57.12.00, C57.12.90, C57.12.91, etc.) | IEEE | US | **stub** | electrical/transformer-sizing (stub) | MEDIUM (Group B) |
| BSEN60034 | BS EN 60034 Rotating Electrical Machines (Parts 1-31) | BSI/CEN | EU/GB | **stub** | electrical/motor-selection (stub), vfd-selection (stub) | MEDIUM (Group B) |
| NEMA-MG1 | NEMA MG 1 Motors and Generators (US Standard) | NEMA | US | **stub** | electrical/motor-selection (stub) | MEDIUM (Group B) |
| IEC61800 | IEC 61800 Adjustable Speed Drives (Parts 1-9) | IEC | INT | **stub** | electrical/vfd-selection (stub), harmonic-mitigation (stub) | MEDIUM (Group B) |
| IEC60204-1 | IEC 60204-1 Safety of Machinery — Electrical Equipment | IEC | INT | **stub** | electrical/machinery-control (stub) | LOW (Group D) |
| IEC60287 | IEC 60287 Calculation of Cable Current Ratings (Thermal Model) | IEC | INT | **production** | cable-sizing | — |
| IEC60228 | IEC 60228 Conductors of Insulated Cables | IEC | INT | **production** | cable-sizing | — |
| IEC60502 | IEC 60502 Power Cables 1-30 kV (Parts 1-4) | IEC | INT | **production** | cable-sizing | — |
| BSEN50575 | BS EN 50575 Cables for Construction Works (CPR) | BSI/CEN | EU/GB | **production** | cable-sizing | — |
| BS7430 | BS 7430 Earthing Code of Practice (UK) | BSI | GB | **production** | earthing, fault-level | — |
| IEEE80 | IEEE 80 Safety in AC Substation Grounding | IEEE | US | **stub** | electrical/substation-earthing (stub) | LOW (Group D) |
| IEEE81 | IEEE 81 Measuring Earth Resistance and Potential Gradients | IEEE | US | **stub** | electrical/substation-earthing (stub) | LOW (Group D) |
| ENA-G99-G98 | UK ENA G99/G98 DNO Embedded Generation Connection Procedures | ENA | GB | **stub** | electrical/solar-pv (stub), embedded-gen (stub) | HIGH (Group C) |
| IEEE1547 | IEEE 1547 Interconnection and Interoperability of DER Systems | IEEE | US | **stub** | electrical/solar-pv (stub), embedded-gen (stub) | HIGH (Group C) |
| IEC61730 | IEC 61730 Photovoltaic (PV) Module Safety Qualification (Parts 1-2) | IEC | INT | **stub** | electrical/solar-pv (stub) | MEDIUM (Group C) |
| IEC62109 | IEC 62109 Safety of Photovoltaic (PV) Power Conversion Equipment (Parts 1-2) | IEC | INT | **stub** | electrical/solar-pv (stub) | MEDIUM (Group C) |
| UL1741 | UL 1741 Inverters/Converters/Controllers and Interconnected Electric Power Production Sources | UL | US | **stub** | electrical/solar-pv (stub) | MEDIUM (Group C) |
| MCS | UK Microgeneration Certification Scheme (MCS) | DCLG | GB | **stub** | electrical/solar-pv (stub) | LOW (Group C) |
| IEC61851 | IEC 61851 Electric Vehicle Conductive Charging System (Parts 1-2) | IEC | INT | **stub** | electrical/ev-charging (stub) | MEDIUM (Group B) |
| IEC62196 | IEC 62196 Plugs, Socket-Outlets, Vehicle Connectors and Vehicle Inlets (Parts 1-3) | IEC | INT | **stub** | electrical/ev-charging (stub) | MEDIUM (Group B) |
| BS5839 | BS 5839 Fire Detection and Fire Alarm Systems (Parts 1-9) | BSI | GB | **stub** | electrical/fire-alarm (stub) | MEDIUM (Group C) |
| BSEN54 | BS EN 54 Fire Detection and Fire Alarm Systems Components | BSI/CEN | EU/GB | **stub** | electrical/fire-alarm (stub) | MEDIUM (Group C) |
| NFPA72 | NFPA 72 National Fire Alarm and Signaling Code | NFPA | US | **stub** | electrical/fire-alarm (stub) | MEDIUM (Group C) |
| BS5266 | BS 5266 Emergency Lighting Code of Practice (Parts 1-2) | BSI | GB | **stub** | electrical/emergency-lighting (stub) | MEDIUM (Group C) |
| BSEN1838 | BS EN 1838 Lighting Applications — Emergency Lighting | BSI/CEN | EU/GB | **stub** | electrical/emergency-lighting (stub) | MEDIUM (Group C) |
| BSEN50131 | BS EN 50131 Alarm Systems — Intruder and Hold-Up Detection (Parts 1-7) | BSI/CEN | EU/GB | **stub** | electrical/security-system (stub) | LOW (Group C) |
| BSEN62676 | BS EN 62676 Video Surveillance / CCTV Systems (Parts 1-2) | BSI/CEN | EU/GB | **stub** | electrical/cctv-design (stub) | LOW (Group C) |
| BSEN50133 | BS EN 50133 Alarm Systems — Access Control (Parts 1-5) | BSI/CEN | EU/GB | **stub** | electrical/access-control (stub) | LOW (Group C) |
| PD6662 | PD 6662 UK Intruder Alarm Framework | BSI | GB | **stub** | electrical/security-system (stub) | LOW (Group D) |
| TIA-568 | ANSI/TIA-568 Commercial Building Telecom Cabling (568A/568B Standards) | TIA | US | **stub** | electrical/data-cabling (stub) | LOW (Group D) |
| ISO-IEC-11801 | ISO/IEC 11801 Generic Cabling (Parts 1-3) | ISO/IEC | INT | **stub** | electrical/data-cabling (stub) | LOW (Group D) |
| TIA-942 | ANSI/TIA-942 Data Center Telecom Infrastructure (Parts 1-2) | TIA | US | **stub** | electrical/data-center-cabling (stub) | LOW (Group D) |
| BSEN50173 | BS EN 50173 Generic Cabling (Parts 1-3) | BSI/CEN | EU/GB | **stub** | electrical/data-cabling (stub) | LOW (Group D) |
| HTM06-01 | HTM 06-01 Electrical Services Supply and Distribution (Healthcare) | DHSC | GB | **stub** | electrical/healthcare-electrical (stub) | LOW (Group D) |
| HTM06-02 | HTM 06-02 Electrical Safety Guidance (Healthcare) | DHSC | GB | **stub** | electrical/healthcare-electrical (stub) | LOW (Group D) |
| HTM08-03 | HTM 08-03 Bedhead Services (Healthcare) | DHSC | GB | **stub** | electrical/healthcare-bedhead (stub) | LOW (Group D) |
| PartL-2021 | UK Approved Document Part L:2021 Conservation of Fuel & Power | DCLG | GB | **stub** | electrical/energy-efficiency (stub) | MEDIUM (Group D) |
| ASHRAE-90-1 | ASHRAE 90.1 Energy Standard for Buildings (2022 Edition) | ASHRAE | US | **stub** | electrical/energy-efficiency (stub) | MEDIUM (Group D) |
| ISO50001 | ISO 50001:2018 Energy Management Systems | ISO | INT | **stub** | electrical/energy-management (stub) | LOW (Group D) |
| PartP | UK Approved Document Part P Electrical Safety in Dwellings | DCLG | GB | **stub** | electrical/domestic-installation (stub) | LOW (Group D) |
| PartM | UK Approved Document Part M Accessibility to and Use of Buildings | DCLG | GB | **stub** | electrical/accessibility-design (stub) | LOW (Group D) |
| PartB | UK Approved Document Part B Fire Safety | DCLG | GB | **stub** | electrical/fire-safety (stub) | MEDIUM (Group D) |

---

## Build-priority groups

### Group A — Next 90 days
Blocks immediate arc-flash and lightning-protection skills:
- ✅ **IEEE1584** + **NFPA70E** (Phase A standards layers shipped 2026-05-17 — 28 files + 25 files, production v1.0.0)
- **BSEN62305** + **NFPA780** + **IEC62561** (lightning-protection design skill)
- **BSEN61643** (surge protective device selection skill)

### Group B — Next 6 months
Next batch of calculation and selection skills:
- **BSISO8528** + **NFPA110** (generator-sizing skill v1.0)
- **BSEN60076** + **IEEEC57** (transformer-sizing skill v1.0)
- **BSEN62040** + **IEEE485** + **IEC60896** (ups-sizing skill v1.0)
- **BSEN60034** + **NEMA-MG1** (motor-selection skill v1.0)
- **IEC61800** (vfd-selection + harmonic-mitigation skill v1.0)
- **IEC61851** + **IEC62196** (ev-charging-infrastructure skill v1.0)

### Group C — Next 12 months
Renewables, storage, and safety systems:
- **IEC62933** + **NFPA855** + **UL9540** (bess-sizing skill v1.0)
- **ENA-G99-G98** + **IEEE1547** + **IEC61730** + **IEC62109** + **UL1741** (solar-pv-interconnection skill v1.0)
- **BS5839** + **BSEN54** + **NFPA72** (fire-alarm-design skill v1.0)
- **BS5266** + **BSEN1838** (emergency-lighting skill v1.0)
- **BSEN50131** + **BSEN62676** + **BSEN50133** (security-system-design skill v1.0)
- **PartB** (building-regulation-fire-safety skill v1.0)

### Group D — Long-tail (build when project demand exists)
Specialized domains and low-urgency updates:
- **IEC60079** (hazardous-locations skill v1.0)
- **IEC61000** + **ERG5-5** + **IEEE519** (power-quality-harmonic-study skill v1.0)
- **BSEN60831** + **IEC61921** (power-factor-correction skill v1.0)
- **IEEE80** + **IEEE81** (substation-earthing skill v1.0)
- **IEC60204-1** (machinery-control-electrical skill v1.0)
- **TIA-568** + **ISO-IEC-11801** + **TIA-942** + **BSEN50173** (data-cabling skill v1.0)
- **HTM06-01** + **HTM06-02** + **HTM08-03** (healthcare-electrical skill v1.0)
- **PartL-2021** + **ASHRAE-90-1** (energy-efficiency-compliance skill v1.0)
- **ISO50001** (energy-management-systems skill v1.0)
- **PartP** + **PartM** (domestic-accessibility-regs skill v1.0)
- **PD6662** (intruder-alarm-framework skill v1.0)

---

## How to promote a layer from stub → draft

1. Identify all key clauses/tables in the standard's table-of-contents
2. For each major section, create a `<part>-<topic>.json` file with structured data:
   - Clause numbers and headings
   - Key definitions and parameters
   - Selection tables, formulas, and lookup values
   - Limits, thresholds, and safety margins
3. Write `terminology.md` glossary with key terms, symbols, and cross-references
4. Update `meta.json`:
   - Set `"status": "draft"`
   - Update `"files_planned"` to `"files_present"`
5. Update this ROADMAP.md row to **draft**

---

## How to promote a layer from draft → production

1. At least one shipped skill references it via `manifest.standards[]`
2. Skill's evaluation suite passes all test cases that exercise this layer
3. All clause references have been fact-checked against the latest standard edition
4. Update `meta.json`:
   - Set `"status": "production"`
5. Update this ROADMAP.md row to **production**

---

## Standards body abbreviations

| Abbreviation | Standard Body |
|---|---|
| BSI | British Standards Institution (UK) |
| CEN | Comité Européen de Normalisation (European Committee) |
| IEC | International Electrotechnical Commission |
| IEEE | Institute of Electrical and Electronics Engineers (US/INT) |
| NFPA | National Fire Protection Association (US) |
| ENA | Electricity Networks Association (UK) |
| UL | Underwriters Laboratories (US) |
| NEMA | National Electrical Manufacturers Association (US) |
| ISO | International Organization for Standardization |
| TIA | Telecommunications Industry Association (US) |
| ASHRAE | American Society of Heating, Refrigerating and Air-Conditioning Engineers (US) |
| DCLG | Department for Communities and Local Government (UK) |
| DHSC | Department of Health and Social Care (UK) |

---

## Next steps

1. **Group A (Next 90 days):** ✅ IEEE1584 + NFPA70E shipped 2026-05-17. Proceed to BSEN62305, NFPA780, IEC62561.
2. **Parallel skill development:** Start lightning-protection skill drafts while standards layers are being transcribed
3. **Regular ROADMAP reviews:** Update status every two weeks as new layers are promoted or new skills are shipped
4. **Skill-to-standard binding:** Ensure each shipped skill's `manifest.standards[]` array references this ROADMAP correctly
