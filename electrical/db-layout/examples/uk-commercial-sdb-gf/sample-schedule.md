# DB Schedule — SDB-GF, UK 3-storey Office (Ground Floor)

**Project:** uk-3storey-office-eg01
**Board:** SDB-GF, IP4X enclosure, 100A TPN intake (fed from MSB-MAIN F01)
**Generated:** 2026-05-18
**Jurisdiction:** GB (BS 7671:2018+A2)

---

| Way | Circuit | Designation | Phase | Device | In (A) | Cable | Length (m) | RCD |
|---|---|---|---|---|---|---|---|---|
| W1  | C01 | Lighting GF — open office LED panels | L1       | MCB Type B | 10 | 1.5mm² T+E | 25 | — |
| W2  | C02 | Lighting GF — meeting rooms LED      | L2       | MCB Type B | 6  | 1.5mm² T+E | 18 | — |
| W3  | C03 | Emergency lighting GF (dedicated)    | L3       | MCB Type B | 6  | 1.5mm² T+E | 20 | — |
| W4  | C04 | Sockets GF — open office RFC         | L1       | MCB Type B | 32 | 2.5mm² T+E | 35 | 30mA Type A |
| W5  | C05 | Sockets GF — meeting rooms RFC       | L2       | MCB Type B | 32 | 2.5mm² T+E | 28 | 30mA Type A |
| W6  | C06 | Sockets GF — reception RFC           | L3       | MCB Type B | 32 | 2.5mm² T+E | 20 | 30mA Type A |
| W7  | C07 | Sockets GF — kitchen radial          | L1       | MCB Type B | 20 | 2.5mm² T+E | 12 | 30mA Type A |
| W8  | C08 | Dedicated socket — printer/copier    | L2       | MCB Type B | 16 | 2.5mm² T+E | 18 | 30mA Type A |
| W9  | C09 | HVAC FCU bank GF (motor)             | TPN      | MCB Type C | 32 | 2.5mm² SY  | 22 | — |
| W10 | C10 | Cleaner sockets — corridors          | L3       | MCB Type B | 20 | 2.5mm² T+E | 30 | 30mA Type A |
| W11 | C11 | IT/data outlet ring — desks          | L1       | MCB Type B | 32 | 2.5mm² T+E | 32 | 30mA Type A |
| W12 | C12 | AV radial — meeting rooms            | L2       | MCB Type B | 20 | 2.5mm² T+E | 24 | 30mA Type A |
| W13-W16 | — | Spare ways                          |          |            |    |            |    |   |

---

## Notes

- Connected load ≈ 38 kW; after-diversity demand ≈ 28 kW (≈47A/phase)
- 100A TPN intake gives ~50% headroom — typical UK spec-office floor-DB sizing
- BS 7671:2018+A2 Reg 411.3.3 universal 30mA Type A RCD applied on all socket circuits (C04-C08, C10-C12)
- Emergency lighting C03 dedicated per §560 — no RCD upstream
- HVAC FCU C09 motor circuit: Type C curve; no socket → no Reg 411.3.3 requirement
- Estimated PFC at SDB-GF ≈ 6.0 kA after 15m feeder impedance from 9.8 kA at MSB-MAIN
- Selectivity: 100A MCCB Type D upstream (MSB-MAIN F01) selective against 32A MCBs (3.1:1 ratio + curve separation)
- Upstream producer: MSB-MAIN (F01 feeder); peers: SDB-L1, SDB-L2
