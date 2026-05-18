# DB Schedule — DB-M1, IEC Commercial 3-storey Office (Mechanical/HVAC)

**Project:** intl-comm-tpn-eg02
**Board:** DB-M1, IP54 enclosure, 250A TPN intake (fed from MSB-MAIN F03)
**Generated:** 2026-05-18
**Jurisdiction:** INT (IEC 60364 series + IEC 61439-3 + IEC 60947-4-1)

---

| Way | Circuit | Designation | Phase | Device | In (A) | Cable | Length (m) | RCD |
|---|---|---|---|---|---|---|---|---|
| W1 | M01 | AHU-1 supply fan motor (3-ph 11kW)   | TPN | MCB Type D | 32 | 6mm² SY 5c   | 25 | — |
| W2 | M02 | AHU-1 extract fan motor (3-ph 7.5kW) | TPN | MCB Type D | 25 | 4mm² SY 5c   | 25 | — |
| W3 | M03 | AHU-2 supply fan motor (3-ph 11kW)   | TPN | MCB Type D | 32 | 6mm² SY 5c   | 35 | — |
| W4 | M04 | AHU-2 extract fan motor (3-ph 7.5kW) | TPN | MCB Type D | 25 | 4mm² SY 5c   | 35 | — |
| W5 | M05 | Chilled water pump (3-ph 5.5kW)      | TPN | MCB Type C | 20 | 2.5mm² SY 5c | 20 | — |
| W6 | M06 | Kitchen extract fan (3-ph 4kW)       | TPN | MCB Type C | 16 | 2.5mm² SY 5c | 45 | — |
| W7 | M07 | FCU control panel feed (BMS supply)   | L1  | MCB Type B | 16 | 2.5mm² PVC   | 30 | 30mA Type A |
| W8 | M08 | Condensate pump (single-ph 1.5kW)    | L2  | MCB Type C | 10 | 1.5mm² PVC   | 18 | 30mA Type A |
| W9-W12 | — | Spare ways                           |     |            |    |              |    |   |

---

## Notes

- Connected load ≈ 50 kW; after-diversity demand ≈ 48 kW ≈ 81A/phase — 250A intake matches upstream MSB-MAIN F03
- IP54 enclosure for plantroom dust/moisture/oil mist exposure
- M01-M06 are 3-phase motor circuits: DB-M1 MCB provides short-circuit protection only; local motor starter/VSD per IEC 60947-4-1 handles thermal overload + isolation
- Type D MCBs on AHU + extract fans (M01-M04) for DOL inrush; Type C on smaller motors (M05, M06); Type B on M07 control feed; Type C on M08 single-ph pump
- No RCD on motor circuits — IEC 60364-4-41 Clause 411.3.3 socket-RCD policy excludes fixed-equipment 3-phase motors; VSD common-mode leakage also risks nuisance trip
- 30mA Type A RCD on M07 (control panel = socket-equivalent) and M08 (accessible single-ph pump = socket-equivalent)
- 10 kA Icn MCBs with cascade backup from upstream 250A MCCB (Icu ≥ 25 kA) per IEC 60364-5-53 Clause 536.4
- Type D upstream + Type D downstream selectivity requires manufacturer cascade-table confirmation (deferred to fault-level skill)
- Estimated PFC at DB-M1 ≈ 14 kA after 45m feeder impedance from 25 kA at MSB-MAIN
- Phase balance: motors balance across TPN inherently; single-phase imbalance ≤4% — within Clause 314
- 4 spare ways for future VRF expansion or additional FCU bank circuits
- Upstream producer: MSB-MAIN F03; peers: DB-L1, DB-P1, DB-FA1
