# DB Schedule — DB-L1, IEC Commercial 3-storey Office (Lighting)

**Project:** intl-comm-tpn-eg02
**Board:** DB-L1, IP4X enclosure, 250A TPN intake (fed from MSB-MAIN F01)
**Generated:** 2026-05-18
**Jurisdiction:** INT (IEC 60364 series + IEC 61439-3)

---

| Way | Circuit | Designation | Phase | Device | In (A) | Cable | Length (m) | RCD |
|---|---|---|---|---|---|---|---|---|
| W1 | L01 | Lighting Zone 1 — open office GF       | L1 | MCB Type C | 16 | 2.5mm² PVC      | 40 | 30mA Type A |
| W2 | L02 | Lighting Zone 2 — open office L1       | L2 | MCB Type C | 16 | 2.5mm² PVC      | 60 | 30mA Type A |
| W3 | L03 | Lighting Zone 3 — open office L2       | L3 | MCB Type C | 16 | 2.5mm² PVC      | 80 | 30mA Type A |
| W4 | L04 | Lighting — meeting rooms common        | L1 | MCB Type B | 10 | 1.5mm² PVC      | 45 | 30mA Type A |
| W5 | L05 | External lighting (parking + façade)   | L2 | MCB Type C | 20 | 4mm² SWA XLPE   | 90 | 30mA Type A |
| W6 | L06 | Emergency lighting (battery-backed)    | L3 | MCB Type B | 10 | 1.5mm² FP200    | 55 | — |
| W7 | L07 | Decorative lighting (lobby + meeting)  | L1 | MCB Type B | 10 | 1.5mm² PVC      | 35 | 30mA Type A |
| W8 | —   | Spare way reserved                      |    |            |    |                 |    |   |

---

## Notes

- Connected load ≈ 19.3 kW; design current ≈ 29A/phase — 250A intake matches upstream MSB-MAIN F01 breaker rating
- IEC 60364-4-41 Clause 411.3.3 universal 30mA Type A RCD applied on all general lighting circuits (L01-L05, L07)
- IEC 60364-5-56 Clause 560: L06 emergency lighting on dedicated circuit, NO upstream RCD, FP200 LSZH cable for 90-min survival
- Type C MCBs on L01/L02/L03/L05 handle LED driver inrush; Type B on lower-power circuits (L04, L06, L07)
- 10 kA Icn MCBs with cascade backup from upstream 250A MCCB (25 kA Icu) per IEC 60364-5-53 Clause 536.4 — verify with manufacturer cascade table
- Estimated PFC at DB-L1 ≈ 15 kA after 35m feeder impedance from 25 kA at MSB-MAIN
- Voltage drop sanity check: L03 ≈ 2.3% (80m, 16A, 2.5mm²); L05 ≈ 2.1% (90m, 20A, 4mm²) — both within 3% lighting limit
- Phase balance: L1 ≈ 6.8 kW, L2 ≈ 7.5 kW, L3 ≈ 5.0 kW — within 30% imbalance per IEC 60364-1 Clause 314
- Upstream producer: MSB-MAIN F01; peers: DB-P1, DB-M1, DB-FA1
