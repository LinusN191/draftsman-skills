# DB Schedule — TSP-A, Suite 100 Apparel Retail Tenant

**Project:** us-stripmall-tsp-a-eg04
**Board:** TSP-A, NEMA Type 1, 100A 208Y/120V intake (fed from MSP-A 100A 2-pole breaker)
**Generated:** 2026-05-18
**Jurisdiction:** US (NFPA 70 NEC 2023)

---

| Way | Circuit | Designation                                                | Phase | Device      | In (A) | Cable        | Length (m) | GFCI         |
|-----|---------|------------------------------------------------------------|-------|-------------|--------|--------------|------------|--------------|
| W1  | C01     | Retail floor lighting (LED track + emergency egress)       | L1    | MCB Type C  | 20     | 12 AWG Cu    | 25         | —            |
| W2  | C02     | Sales floor general receptacles                            | L2    | MCB Type C  | 20     | 12 AWG Cu    | 30         | 10mA Class A |
| W3  | C03     | Sales counter dedicated receptacles                        | L3    | MCB Type C  | 20     | 12 AWG Cu    | 15         | 10mA Class A |
| W4  | C04     | Cash register / POS dedicated                              | L1    | MCB Type C  | 20     | 12 AWG Cu    | 12         | —            |
| W5  | C05     | Fitting room lighting + receptacles                        | L2    | MCB Type C  | 20     | 12 AWG Cu    | 18         | 10mA Class A |
| W6  | C06     | Stock room lighting + receptacles                          | L3    | MCB Type C  | 20     | 12 AWG Cu    | 22         | —            |
| W7  | C07     | Suite HVAC RTU control circuit                             | L1    | MCB Type C  | 15     | 14 AWG Cu    | 28         | —            |
| W8  | C08     | Suite emergency lighting circuit (life-safety)             | L2    | MCB Type C  | 20     | 12 AWG Cu    | 25         | —            |
| W9-W30 | —    | Spare ways reserved (22 ways)                              |       |             |        |              |            |              |

---

## Notes

- Connected load ≈ 9.9 kW; design current ≈ 28 A diversified across 3 phases at 208V — 100A intake matches MSP-A 100A tenant feeder breaker rating per NEC 408.30
- NEC 210.8(B) commercial GFCI applied to sales floor + sales counter + fitting room receptacles (C02, C03, C05) at 10mA Class A per UL 943
- C04 POS dedicated EXEMPT from GFCI per NEC 210.8(B) exception (dedicated electronic data-processing equipment outlet)
- C08 emergency lighting EXEMPT from GFCI per NEC 700.6 / NFPA 101 life-safety availability principle
- EGC sizing per NEC 250.122: 12 AWG Cu EGC for 20A circuits; 14 AWG Cu EGC for the 15A HVAC control circuit
- Cable ampacity per NEC Table 310.16 (THWN-2 in EMT, 30°C ambient): 12 AWG = 25A, 14 AWG = 20A — all In ≤ Iz
- 10 kA Icn MCBs with cascade backup from upstream MSP-A 200A main; cascade verification deferred to fault-level skill (tool_call_pending)
- Phase balance: ~L1 3.8 kW, L2 3.5 kW, L3 2.6 kW — within typical commercial tenant imbalance tolerance
- Upstream producer: MSP-A (`electrical/db-layout/examples/us-strip-mall-panelboard/`); peers: TSP-B, CA-P
