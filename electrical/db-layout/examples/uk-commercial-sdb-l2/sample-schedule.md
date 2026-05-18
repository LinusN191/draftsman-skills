# DB Schedule — SDB-L2, UK 3-storey Office (Level 2)

**Project:** uk-3storey-office-eg01
**Board:** SDB-L2, IP4X enclosure, 100A TPN intake (fed from MSB-MAIN F03 — 45m, longest cascade run)
**Generated:** 2026-05-18
**Jurisdiction:** GB (BS 7671:2018+A2)

---

| Way | Circuit | Designation | Phase | Device | In (A) | Cable | Length (m) | RCD |
|---|---|---|---|---|---|---|---|---|
| W1  | C01 | Lighting L2 — open office LED panels | L1       | MCB Type B | 10 | 1.5mm² T+E | 26 | — |
| W2  | C02 | Lighting L2 — breakout area LED      | L2       | MCB Type B | 6  | 1.5mm² T+E | 16 | — |
| W3  | C03 | Emergency lighting L2 (dedicated)    | L3       | MCB Type B | 6  | 1.5mm² T+E | 22 | — |
| W4  | C04 | Sockets L2 — open office RFC         | L1       | MCB Type B | 32 | 2.5mm² T+E | 36 | 30mA Type A |
| W5  | C05 | Sockets L2 — meeting rooms RFC       | L2       | MCB Type B | 32 | 2.5mm² T+E | 28 | 30mA Type A |
| W6  | C06 | Sockets L2 — breakout area RFC       | L3       | MCB Type B | 32 | 2.5mm² T+E | 22 | 30mA Type A |
| W7  | C07 | Sockets L2 — printer corner radial   | L1       | MCB Type B | 20 | 2.5mm² T+E | 16 | 30mA Type A |
| W8  | C08 | Dedicated socket — A/V rack          | L2       | MCB Type B | 16 | 2.5mm² T+E | 14 | 30mA Type A |
| W9  | C09 | Dedicated socket — comms UPS feed    | L3       | MCB Type B | 16 | 2.5mm² T+E | 10 | 30mA Type A |
| W10 | C10 | HVAC FCU bank L2 (motor)             | TPN      | MCB Type C | 32 | 2.5mm² SY  | 24 | — |
| W11 | C11 | IT/data outlet ring — desks          | L1       | MCB Type B | 32 | 2.5mm² T+E | 34 | 30mA Type A |
| W12 | C12 | AV radial — meeting rooms            | L2       | MCB Type B | 20 | 2.5mm² T+E | 25 | 30mA Type A |
| W13-W16 | — | Spare ways                          |          |            |    |            |    |   |

---

## Notes

- Connected load ≈ 37 kW; after-diversity demand ≈ 27 kW (≈46A/phase)
- 100A TPN intake gives ~54% headroom — typical UK spec-office floor-DB sizing
- BS 7671:2018+A2 Reg 411.3.3 universal 30mA Type A RCD applied on all socket circuits (C04-C09, C11, C12)
- Emergency lighting C03 dedicated per §560 — no RCD upstream
- HVAC FCU C10 motor circuit: Type C curve; no socket → no Reg 411.3.3 requirement
- **45m feeder is the longest in the cascade** — Zs + voltage drop verification will be tightest at L2 socket terminals (deferred to cable-sizing + fault-level)
- Estimated PFC at SDB-L2 ≈ 3.5 kA after 45m feeder impedance from 9.8 kA at MSB-MAIN (still 65% margin under 10 kA Icn)
- Selectivity: 100A MCCB Type D upstream (MSB-MAIN F03) selective against 32A MCBs (3.1:1 ratio + curve separation)
- Total cable run MSB→furthest socket on C04 ≈ 81m — flagged as the cascade bottleneck
- Upstream producer: MSB-MAIN (F03 feeder); peers: SDB-GF, SDB-L1
