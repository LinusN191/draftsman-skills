# DB Schedule — MSB-MAIN, UK 3-storey Office

**Project:** uk-3storey-office-eg01
**Board:** MSB-MAIN, IP4X enclosure, 400A TPN intake from UK DNO
**Generated:** 2026-05-18
**Jurisdiction:** GB (BS 7671:2018+A2)

---

| Way | Circuit | Designation | Phase | Device | In (A) | Cable | Length (m) | RCD |
|---|---|---|---|---|---|---|---|---|
| W1-W3   | F01 | Feeder to SDB-GF | TPN | MCCB Type D | 100 | 35mm² SWA | 15 | n/a |
| W4-W6   | F02 | Feeder to SDB-L1 | TPN | MCCB Type D | 100 | 35mm² SWA | 30 | n/a |
| W7-W9   | F03 | Feeder to SDB-L2 | TPN | MCCB Type D | 100 | 35mm² SWA | 45 | n/a |
| W10-W12 | —   | Spare ways       |     |             |     |           |    |     |

---

## Notes

- Total design demand: 86 kVA / 73 kW / ~146A per phase peak with diversity
- 400A TPN intake provides ~63% headroom for spec-office tenant fit-out variation
- Selectivity verified: 400A main MCCB selective against 100A feeder MCCBs (4:1 ratio + STD)
- Final-circuit RCDs deferred to downstream sub-DBs (preserves MSB-level selectivity)
- Downstream consumers: SDB-GF, SDB-L1, SDB-L2 (each their own db-layout example)
