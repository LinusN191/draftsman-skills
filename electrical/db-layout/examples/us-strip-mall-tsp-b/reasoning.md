# Reasoning — US Strip-Mall TSP-B Tenant Sub-Panel (Suite 200 food-service retail)

## Site context

TSP-B is the tenant sub-panel serving Suite 200 of Sunset Plaza, a specialty food-service retail tenant (cheese + deli; cold-served prepared goods, no hot cooking line). Upstream is MSP-A (existing `us-strip-mall-panelboard` example). Same building service (208Y/120V 3-phase) and same 100A 2-pole tenant feeder pattern as TSP-A.

Tenant context differs significantly from TSP-A apparel:
- Heavy refrigeration motor load (2 × display reefers + 1 walk-in cooler condensing unit) → Type D curve MCBs, dedicated circuits per NEC 422.16(B)
- Prep-area receptacles → GFCI per NEC 210.8(B) prep counter
- No fitting rooms; no high-density LED track lighting

Single-board scope. Ze ≈ 0.10Ω at TSP-B.

## Step 1 — Discovery check

Single board, no cross_drawing_context. No fault-level intent. Engineer Ifault not declared → selectivity defers (tool_call_pending) per WI3.

## Step 2 — Standards files loaded (US → NFPA 70 family)

- `shared/standards/electrical/NFPA70/art408-panelboards.json`
- `shared/standards/electrical/NFPA70/art240-overcurrent.json`
- `shared/standards/electrical/NFPA70/art220-load-calculations.json`
- `shared/standards/electrical/NFPA70/ocpd-coordination.json`
- `shared/standards/electrical/IEC60617/symbol-index.json`
- `shared/standards/electrical/IEC60617/part7-switchgear.json`
- `shared/standards/electrical/IEC61439/form-separations.json` (cross-reference)
- `shared/standards/electrical/IEC61439/ip-ik-ratings.json`
- `shared/standards/electrical/IEC61439/short-circuit-withstand.json`

NEC 430 motor branch-circuit protection loaded for the refrigeration motor circuits (C03/C04/C05).

(BS 7671 and IEC 60364 NOT loaded — US jurisdiction.)

## Step 3 — Board classification

- `panelboard_nema` (US tenant sub-panel)
- NEMA Type 1 enclosure (indoor general purpose)
- Per NEC Article 408 — maximum 42 overcurrent devices per panelboard section
- Ways: 30 total (21 spare for fit-out additions like additional reefer line, ice machine, three-compartment sink dedicated heater, etc.)

## Step 4 — Incoming supply

Same as TSP-A: 208Y/120V 3-phase 4-wire 60 Hz, 100A 2-pole feeder from MSP-A. `phase_arrangement: TPN` (Y-connected 208/120 building service).

Ze 0.10Ω at TSP-B.

`supply_class: non_essential` — tenant feed.

## Step 5 — Busbar sizing

Connected load: 1.6 + 1.5 + 2.2 + 2.2 + 4.5 + 1.0 + 1.8 + 1.0 + 0.8 = 16.6 kW.

At 208V 3-phase: ~46-48A diversified at PF 0.85 (motor loads pull PF down vs LED-dominant apparel tenant).

Diversity 0.8 applied per NEC 220.61. 100A busbar matches upstream feeder OCPD per NEC 408.30/408.36 (sized to feeder rating, not diversified load).

IcW 10 kA per typical NEMA tenant sub-panel rating.

## Step 6 — Way assignment

9 circuits, all single-pole 120V branch circuits:
- C01, C02, C06, C07, C09 on 20A single-pole Type C MCBs
- C03, C04 on 20A single-pole Type D MCBs (motor inrush)
- C05 on 30A single-pole Type D MCB (walk-in cooler condensing unit motor)
- C08 on 15A single-pole Type C MCB

Total 9 ways used, 21 ways spare.

## Step 7 — OCPD per circuit

US uses NEC ampacity tables (Table 310.16):

- C01 (20A, 12 AWG Cu): NEC 310.16 → 25A ampacity → 20 ≤ 25 ✓
- C02 (20A, 12 AWG): same ✓
- C03 (20A, 12 AWG): same ✓ — Type D for compressor LRA
- C04 (20A, 12 AWG): same ✓ — Type D for compressor LRA
- C05 (30A, 10 AWG): NEC 310.16 → 35A ampacity → 30 ≤ 35 ✓ — Type D for walk-in compressor LRA (NEC 430.52 motor branch-circuit OCPD)
- C06 (20A, 12 AWG): same as C01 ✓
- C07 (20A, 12 AWG): same ✓
- C08 (15A, 14 AWG): NEC 310.16 → 20A ampacity → 15 ≤ 20 ✓
- C09 (20A, 12 AWG): same as C01 ✓

EGC sizing per NEC 250.122: 12 AWG Cu EGC for 20A circuits, 10 AWG Cu EGC for the 30A walk-in cooler, 14 AWG Cu EGC for the 15A HVAC control.

Icn 10 kA exceeds typical fault current at the tenant sub-panel.

## Step 8 — Motor protection (NEC 430)

Refrigeration motor circuits handled per NEC 430:

- **C03/C04 display reefers (~2.2 kW each ≈ 10.6 A FLA at 208V):** 20A Type D MCB protects against LRA (typically 6× FLA = 64 A for ~100 ms during compressor start). Type D Ia ≈ 10-20× In = 200-400A — handles LRA without nuisance trip while still operating fast at fault levels per NEC 430.52 Table.
- **C05 walk-in cooler condensing unit (~4.5 kW ≈ 21.6 A FLA):** 30A Type D MCB. LRA ≈ 130 A. Same Type D rationale.

Cord-and-plug-connected reefer equipment is UL-listed; the panelboard breaker is the branch-circuit OCPD per NEC 422.16(B).

## Step 9 — GFCI assignment (NEC 210.8(B) commercial)

NEC 2023 Article 210.8(B) requires GFCI on:

- **C02 counter + customer area receptacles:** GFCI 10mA Class A per NEC 210.8(B)(8) — counter receptacles in commercial occupancy + customer-accessible.
- **C07 prep-area receptacles + small appliance branch:** GFCI 10mA Class A per NEC 210.8(B)(7) — receptacles serving prep counter and within 6 ft of food-prep sink.
- **C06 POS dedicated:** EXEMPT per NEC 210.8(B) exception — dedicated electronic data-processing outlet not readily accessible. Verify at fit-out.
- **C03/C04/C05 refrigeration:** Dedicated hardline / cord-and-plug commercial refrigeration equipment per NEC 422.16(B) — feeder-side GFEP at the cooler controller (where required by NEC 426/427 for de-icing heaters), but NOT panelboard receptacle GFCI. Verify with refrigeration equipment vendor.
- **C01 sales floor lighting:** No GFCI required (lighting load).
- **C08 HVAC control:** No GFCI required (motor / control circuit).
- **C09 emergency lighting:** NO GFCI per **NEC 700.6** — life-safety availability principle (an earth-fault trip would disable egress illumination at the moment of greatest need).

AFCI per NEC 210.12 applies to dwelling-unit branch circuits — **not** this retail fit-out.

## Step 10 — Cable selection

THWN-2 copper in EMT conduit. NEC Table 310.16 at 30°C ambient. `cable_csa_awg` (string) used per US jurisdiction.

10 AWG for the walk-in cooler dedicated (12m route — short, voltage drop negligible).

## Step 11 — DB face schematic

Symbols emitted: `BUSBAR`, `MAIN_SWITCH` (100A 2-pole main), `MCB` (×9, including Type D variants), `GFCI` (on C02 + C07 breaker positions), `EARTH_GENERAL`.

## Step 12 — Selectivity verification

No fault-level intent. Engineer Ifault not declared → all 9 cascade pairs (MSP-A → C01..C09) emit `tool_call_pending: true` per WI3.

Top-level flags include `TOOL-CALL-PENDING`.

When fault-level skill ships, the cascade pairing will verify upstream MSP-A 100A feeder OCPD against TSP-B branch-circuit MCBs (especially the 30A walk-in cooler) at the cascade fault level. Note: motor circuit cascade selectivity also depends on the Type D curve's higher Ia band — verify with manufacturer cascade table.

## Step 13 — Compliance flags

- **INFO:** GFCI scope per NEC 210.8(B) — verify with AHJ at tenant fit-out commissioning, especially the 6 ft proximity rule to any prep sink for C07.
- None critical.

## Rationale block

9-section taxonomy with NEC 2023 citations ONLY (no BS 7671, no IEC 60364).

## Downstream consumer

TSP-B's intent-out.json is consumed by:
- `electrical/sld/examples/us-strip-mall-msp-tenants/` (4-board cascade SLD: MSP-A → TSP-A + TSP-B + CA-P)
- (Future) `electrical/cable-sizing/` — verify NEC 310.16 against the 30A walk-in cooler + 20A motor circuits including motor-circuit conductor 125% sizing rules
- (Future) `electrical/fault-level/` — NEC 110.9 / 430.52 motor-branch cascade fault verification

## See also

- `electrical/db-layout/examples/us-strip-mall-panelboard/` (upstream — MSP-A landlord service panel)
- `electrical/db-layout/examples/us-strip-mall-tsp-a/` (peer — Suite 100 apparel retail tenant sub-panel)
- `electrical/db-layout/examples/us-strip-mall-common-area/` (peer — CA-P common-area panel)
