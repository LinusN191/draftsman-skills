# DB Schedule — GH-DB, Nairobi Industrial Workshop (Gate House)

**Project:** ke-nairobi-enterprise-light-engineering
**Board:** GH-DB, IP54 enclosure, 40A single-phase intake (fed from MSP-100 C08, 60m submain)
**Generated:** 2026-05-18
**Jurisdiction:** KE (KS 1700:2018)

---

| Way | Circuit | Designation | Phase | Device | In (A) | Cable | Length (m) | RCD |
|---|---|---|---|---|---|---|---|---|
| W1 | C01 | Gate-house lighting (external floodlights + internal) | L | MCB Type B | 10 | 1.5mm² T+E | 8 | — |
| W2 | C02 | Gate-house sockets (general)                          | L | MCB Type B | 16 | 2.5mm² T+E | 6 | 30mA Type A |
| W3 | C03 | Comms outlet (CCTV camera + intercom)                | L | MCB Type B | 6  | 1.5mm² T+E | 5 | 30mA Type A |
| W4 | —   | Spare way reserved                                    |   |            |    |            |    |   |

---

## Notes

- Connected load ≈ 2.3 kW; design current ≈ 10A — 40A intake gives ~75% headroom (matches upstream MSP-100 C08 breaker)
- Single-phase 240V supply chosen to simplify isolation and minimise neutral imbalance at the upstream MSP-100
- KS 1700:2018 §411.3.3 universal socket-RCD: 30mA Type A on C02 and C03 (CCTV outlet treated as a socket-equivalent)
- C01 lighting not RCD-protected (fixed-equipment exemption; Class II IP65 floodlight luminaires)
- Series 30mA RCD pair (upstream MSP-100 C08 + downstream C02/C03) — pair is NOT selective per KS §314, accepted because the upstream C08 feeder serves only the gate house
- Estimated PFC at GH-DB ≈ 3.0 kA after 60m submain impedance from 9.8 kA at MSP-100; 6 kA Icn MCBs provide 100% headroom
- KS Annex E adopts BS EN 61439-3 (Distribution Board) and BS Table 41.2 (max-disconnection-time) verbatim — used here as the assembly + earth-fault loop reference
- Upstream producer: MSP-100 C08 (existing KE example); no downstream consumers
