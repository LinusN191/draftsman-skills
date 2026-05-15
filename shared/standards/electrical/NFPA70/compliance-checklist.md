# NFPA 70 (NEC 2023) — Designer Compliance Checklist

Project-type-organised checklist of NEC compliance items every MEP designer
must verify before AHJ submission.

---

## Universal items (every project)

- [ ] Confirm AHJ's adopted NEC edition (2017 / 2020 / 2023 / state-specific)
- [ ] Confirm state and local amendments
- [ ] Available fault current at each service / panelboard documented (110.10, 110.24)
- [ ] Working clearances (110.26) on all panel layouts
- [ ] Termination temperature rating (60/75/90 °C) stated on each conductor schedule
- [ ] Arc-flash hazard warning labels (110.16) on equipment likely to require energised work

---

## Residential (single-family dwelling)

- [ ] Service entrance ≥100 A (typical 200 A); calc per Art 220 (Standard 220.40 OR Optional 220.82)
- [ ] Outside emergency disconnect at meter or near service (230.85 — NEC 2020+)
- [ ] Service disconnect within ≤2 m of building entrance or at the meter
- [ ] Grounding electrode system per 250.50 — all present electrodes bonded (including Ufer if present)
- [ ] AFCI per 210.12 — kitchens, bedrooms, living, dining, family, closets, hallways, laundry
- [ ] GFCI per 210.8 — bathrooms, kitchens, dishwasher, laundry, garage, outdoor, basements, crawl space, near sinks
- [ ] TR (tamper-resistant) receptacles per 406.12 — all 15/20 A 125 V dwelling outlets
- [ ] Receptacle spacing per 210.52(A) — wall-space rule (no point > 6 ft from outlet)
- [ ] Two small-appliance kitchen circuits (20 A dedicated)
- [ ] Dedicated 20 A laundry circuit; dedicated 20 A bathroom receptacle circuit

---

## Commercial occupancies

- [ ] Load calc per Art 220 — Standard method 220.40 (Optional 220.84 multi-family doesn't apply here)
- [ ] Service ≥ calculated demand; conductor sizing 125% continuous + 100% non-continuous (215.2)
- [ ] GFP at service ≥1000 A (230.95) — performance test required
- [ ] Selective coordination on emergency / legally req'd standby circuits (700.32 / 701.32)
- [ ] Wiring methods per occupancy table (in wiring-methods-by-occupancy.json)
- [ ] Working clearances (110.26) — confirm 36 in for 480 V or less; 42 in for ≤600 V with energised parts both sides
- [ ] Bathroom GFCI (210.8(B)(1)); kitchen GFCI (210.8(B)(2)); rooftop GFCI (210.8(B)(3))

---

## Industrial / manufacturing

- [ ] Industrial machinery (Art 670 + NFPA 79) — SCCR ≥ available fault current
- [ ] Motor circuits sized per 430.22 (125% × Table 430.250 FLA)
- [ ] Motor OCPD per 430.52 (typical 250% inverse-time CB, 175% dual-element time-delay fuse)
- [ ] Motor disconnect within sight (430.102) — visible from controller AND motor
- [ ] Hazardous locations classified per 500-506 (Division) or 505-506 (Zone)
- [ ] Equipment listed for the Class/Division (or Class/Zone) at every location
- [ ] Conduit seals at hazardous-to-non-hazardous boundary (501.15 et al.)
- [ ] Stationary battery / ESS per Art 480 + Art 706 (UL 9540 listing)

---

## Healthcare

- [ ] Patient care space categories (1-4) marked on drawings (517.2)
- [ ] Dual EGC paths in Category 1 + 2 patient care (517.13)
- [ ] Type 1 EES (hospital) — three branches: Life Safety, Critical, Equipment (517.30+)
- [ ] Generator start ≤10 s, sized for all Type 1 EES loads (517.30 + Art 700)
- [ ] Isolated power systems with LIM at wet locations (ORs, etc.) (517.160)
- [ ] Hospital-grade receptacles (UL 498 hospital grade) in patient-care spaces
- [ ] Anesthetizing locations — if applicable, classify and select equipment (517.60)

---

## EV charging installations (Art 625)

- [ ] Branch circuit ≥125% of EVSE input current (625.41(B))
- [ ] OCPD ≥125% of EVSE input current ≤ branch circuit ampacity
- [ ] GFCI (Class A or EGFCI) — integral to listed EVSE; external for receptacle-type
- [ ] Disconnect within sight (625.43) for EVSE >60 A or >150 V to ground
- [ ] Load management documented for multi-EVSE feeders (625.42(A)(2))
- [ ] Ventilation per 625.52 (rarely needed for modern Li-ion vehicles but rule still applies)

---

## PV installations (Art 690 + 705)

- [ ] Max voltage per 690.7 (600 V dwelling, 1000/1500 V non-dwelling) with cold-temp Voc adjustment
- [ ] OCPD ≥156% of module Isc (125% × 125% per 690.9)
- [ ] DC AFCI on PV source circuits ≥80 V DC (690.11)
- [ ] Rapid shutdown on rooftop PV (690.12) — markings + initiation device location
- [ ] Interconnection per 705.12 — sum rule, 120% rule, or center-fed rule documented
- [ ] PV system GES bonded with AC GES (250.50 + 690.47)
- [ ] System labelling: PV system, rapid shutdown, AC/DC junction boxes, etc. (690.4(D), 690.13(B))

---

## Fire pumps (Art 695)

- [ ] Reliable power source (utility OR on-site generator) (695.3)
- [ ] No disconnect on fire pump supply (except listed controller's) (695.4)
- [ ] Voltage drop ≤15% at motor start, ≤5% at run (695.7)
- [ ] Conductor ampacity ≥125% fire pump motor + accessories (695.6)
- [ ] Coordinate with NFPA 20 (Fire Pumps) standard
- [ ] Listed fire pump controller (NFPA 20-listed)

---

## Energy storage systems (Art 706)

- [ ] ESS listed per UL 9540 (706.4)
- [ ] ESS components listed per UL 9540A (thermal runaway test) for batteries
- [ ] Disconnect within sight or lockable remote (706.7)
- [ ] Location compliance with NFPA 855 separation rules
- [ ] If PV-coupled: rapid shutdown coverage per 690.12

---

## Hazardous locations (Art 500-506)

- [ ] Classification documented (Class/Division OR Class/Zone)
- [ ] Material groups identified (A/B/C/D gas; E/F/G dust; or IIA/IIB/IIC, IIIA/IIIB/IIIC)
- [ ] Equipment listing matches Class/Division/Group (or Zone/Group)
- [ ] Temperature class (T1-T6) ≤ material auto-ignition temperature
- [ ] Conduit seals at boundary (501.15) + at appropriate equipment entries
- [ ] Intrinsically safe loop calculation if Art 504 applied (entity parameters Voc/Isc/Pi/Po/Ci/Li)
- [ ] Maintenance work permit / hot work permit procedures coordinated with operations

---

## At AHJ submission

- [ ] Complete drawing set (one-line, panel schedules, layouts, details)
- [ ] Calculations (load, fault current, voltage drop, conduit fill, ampacity)
- [ ] Equipment specifications including SCCR
- [ ] AHJ-specific submission forms (varies by jurisdiction)
- [ ] Coordination study (where required by 700.32 / 701.32 / 645.27 / 695.6)
- [ ] Listing letters for listed equipment that AHJ requires
- [ ] Engineer of record signature + seal as required

---

## Field marking (commissioning)

- [ ] Available fault current at each panelboard (110.24)
- [ ] Date of fault current marking (110.24(B))
- [ ] Arc-flash hazard warning (110.16)
- [ ] PV system markings per 690.4(D) + 690.13(B) + 705.10
- [ ] Rapid shutdown markings per 690.12(C)
- [ ] Hospital essential electrical system identification (517.30(E))
- [ ] Power-source identification at stand-alone systems (710.10)
- [ ] ESS disconnect marking (706.7(E))
