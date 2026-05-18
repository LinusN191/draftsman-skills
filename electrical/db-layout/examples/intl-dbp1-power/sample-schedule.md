# DB Schedule — DB-P1, IEC Commercial 3-storey Office (Small Power)

**Project:** intl-comm-tpn-eg02
**Board:** DB-P1, IP4X enclosure, 400A TPN intake (fed from MSB-MAIN F02)
**Generated:** 2026-05-18
**Jurisdiction:** INT (IEC 60364 series + IEC 61439-3)

---

| Way | Circuit | Designation | Phase | Device | In (A) | Cable | Length (m) | RCD |
|---|---|---|---|---|---|---|---|---|
| W1  | P01 | Socket ring main GF — open office    | L1 | MCB Type B | 32 | 2.5mm² PVC |  50 (ring) | 30mA Type A |
| W2  | P02 | Socket ring main L1 — open office    | L2 | MCB Type B | 32 | 2.5mm² PVC |  75 (ring) | 30mA Type A |
| W3  | P03 | Socket ring main L2 — open office    | L3 | MCB Type B | 32 | 2.5mm² PVC |  95 (ring) | 30mA Type A |
| W4  | P04 | Socket radials GF — meeting rooms    | L1 | MCB Type B | 20 | 2.5mm² PVC |  30        | 30mA Type A |
| W5  | P05 | Socket radials L1 — meeting rooms    | L2 | MCB Type B | 20 | 2.5mm² PVC |  55        | 30mA Type A |
| W6  | P06 | Dedicated outlets — photocopier      | L3 | MCB Type B | 16 | 2.5mm² PVC |  25        | 30mA Type A |
| W7  | P07 | Kitchen socket radial                 | L1 | MCB Type B | 20 | 2.5mm² PVC |  35        | 30mA Type A |
| W8  | P08 | IT/data ring main — desks GF         | L2 | MCB Type B | 32 | 2.5mm² PVC |  60 (ring) | 30mA Type A |
| W9  | P09 | IT/data ring main — desks L1         | L3 | MCB Type B | 32 | 2.5mm² PVC |  80 (ring) | 30mA Type A |
| W10 | P10 | IT/data ring main — desks L2         | L1 | MCB Type B | 32 | 2.5mm² PVC | 100 (ring) | 30mA Type A |
| W11 | P11 | AV outlets — meeting rooms           | L2 | MCB Type B | 20 | 2.5mm² PVC |  50        | 30mA Type A |
| W12 | P12 | Cleaner sockets — corridors          | L3 | MCB Type B | 20 | 2.5mm² PVC |  40        | 30mA Type A |
| W13-W18 | — | Spare ways                       |    |            |    |            |            |   |

---

## Notes

- Connected load ≈ 47 kW; after-diversity (DF ≈ 0.6) ≈ 28 kW ≈ 47A/phase — 400A intake matches upstream MSB-MAIN F02
- IEC 60364-4-41 Clause 411.3.3 universal 30mA Type A RCD on every circuit (mandatory commercial socket RCD policy)
- IT/data ring mains (P08-P10) carry SMPS loads; Type A needed for pulsating DC residual current detection
- P07 kitchen socket additionally satisfies IEC 60364-7-701 (water-proximity zone)
- Ring-circuit voltage drop: longest ring P10 at 100m gives ~2.8% drop including feeder — within 4% socket-circuit guidance
- All Type B MCBs (no motor circuits, no LED-driver inrush)
- 10 kA Icn MCBs with cascade backup from upstream 400A MCCB (Icu ≥ 36 kA) per IEC 60364-5-53 Clause 536.4
- Estimated PFC at DB-P1 ≈ 18 kA after 40m feeder impedance from 25 kA at MSB-MAIN
- Phase balance: L1 ≈ 16.5 kW, L2 ≈ 16.5 kW, L3 ≈ 14.5 kW — 4% imbalance (well within Clause 314)
- 6 spare ways for tenant fit-out churn (extra rings, server outlets, EV charge points, future printer rooms)
- Upstream producer: MSB-MAIN F02; peers: DB-L1, DB-M1, DB-FA1
