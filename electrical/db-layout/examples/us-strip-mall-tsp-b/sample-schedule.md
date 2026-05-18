# DB Schedule — TSP-B, Suite 200 Food-Service Retail Tenant

**Project:** us-stripmall-tsp-b-eg05
**Board:** TSP-B, NEMA Type 1, 100A 208Y/120V intake (fed from MSP-A 100A 2-pole breaker)
**Generated:** 2026-05-18
**Jurisdiction:** US (NFPA 70 NEC 2023)

---

| Way | Circuit | Designation                                                | Phase | Device      | In (A) | Cable        | Length (m) | GFCI         |
|-----|---------|------------------------------------------------------------|-------|-------------|--------|--------------|------------|--------------|
| W1  | C01     | Sales floor lighting (LED)                                 | L1    | MCB Type C  | 20     | 12 AWG Cu    | 30         | —            |
| W2  | C02     | Counter + customer area receptacles                        | L2    | MCB Type C  | 20     | 12 AWG Cu    | 25         | 10mA Class A |
| W3  | C03     | Display refrigeration unit 1 dedicated (motor)             | L3    | MCB Type D  | 20     | 12 AWG Cu    | 18         | —            |
| W4  | C04     | Display refrigeration unit 2 dedicated (motor)             | L1    | MCB Type D  | 20     | 12 AWG Cu    | 18         | —            |
| W5  | C05     | Walk-in cooler condensing unit (motor)                     | L2    | MCB Type D  | 30     | 10 AWG Cu    | 12         | —            |
| W6  | C06     | POS register dedicated                                     | L3    | MCB Type C  | 20     | 12 AWG Cu    | 15         | —            |
| W7  | C07     | Prep area receptacles + small appliance branch             | L1    | MCB Type C  | 20     | 12 AWG Cu    | 20         | 10mA Class A |
| W8  | C08     | Suite HVAC RTU control circuit                             | L2    | MCB Type C  | 15     | 14 AWG Cu    | 28         | —            |
| W9  | C09     | Suite emergency lighting circuit (life-safety)             | L3    | MCB Type C  | 20     | 12 AWG Cu    | 25         | —            |
| W10-W30 | —   | Spare ways reserved (21 ways)                              |       |             |        |              |            |              |

---

## Notes

- Connected load ≈ 16.6 kW; design current ≈ 48 A diversified across 3 phases at 208V — 100A intake matches MSP-A 100A tenant feeder breaker rating per NEC 408.30
- Type D MCBs on motor refrigeration circuits (C03 + C04 display reefers, C05 walk-in cooler) per NEC 430.52 motor branch-circuit OCPD — accommodate compressor LRA inrush
- NEC 210.8(B) commercial GFCI applied to counter + customer (C02) + prep area receptacles (C07) at 10mA Class A per UL 943
- C06 POS dedicated EXEMPT from GFCI per NEC 210.8(B) exception
- C03/C04/C05 refrigeration motor circuits dedicated per NEC 422.16(B); feeder-side GFEP at cooler controller if NEC 426/427 de-icing heaters present (verify with refrigeration vendor)
- C09 emergency lighting EXEMPT from GFCI per NEC 700.6 / NFPA 101 life-safety availability
- EGC sizing per NEC 250.122: 12 AWG / 10 AWG / 14 AWG matching circuit OCPD ratings
- Cable ampacity per NEC Table 310.16 (THWN-2 in EMT, 30°C ambient): 14 AWG = 20A, 12 AWG = 25A, 10 AWG = 35A — all In ≤ Iz
- Motor branch conductor sizing per NEC 430.22 (125% FLA) verified for cord-and-plug cooler equipment via vendor UL listing
- 10 kA Icn MCBs with cascade backup from upstream MSP-A 200A main; cascade verification deferred to fault-level skill (tool_call_pending)
- Phase balance: roughly even across L1/L2/L3 (~5.5 kW each) with the 4.5 kW walk-in cooler on L2 — within commercial imbalance tolerance
- Upstream producer: MSP-A (`electrical/db-layout/examples/us-strip-mall-panelboard/`); peers: TSP-A, CA-P
