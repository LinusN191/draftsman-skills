# DB Schedule — MSP-100, Nairobi Industrial 100A TPN

**Project:** ke-nairobi-enterprise-light-engineering
**Board:** MSP-100, IP55 enclosure, 100A TPN intake from KPLC
**Generated:** 2026-05-18
**Jurisdiction:** KE (KS 1700:2018)

---

| Way | Circuit | Designation | Phase | Ib (A) | Device | In (A) | Cable | Length (m) | RCD |
|---|---|---|---|---|---|---|---|---|---|
| W1 | C01 | Lighting workshop                 | L1       | 5.0  | MCB Type B | 10 | 1.5mm² T+E    | 35 | n/a   |
| W2 | C02 | Lighting office mezzanine         | L2       | 3.3  | MCB Type B | 6  | 1.5mm² T+E    | 22 | n/a   |
| W3 | C03 | Socket ring main workshop         | L3       | 28.0 | MCB Type B | 32 | 2.5mm² T+E    | 28 | 30mA  |
| W4 | C04 | Socket radials office             | L1       | 13.0 | MCB Type B | 20 | 2.5mm² T+E    | 18 | 30mA  |
| W5 | C05 | Lathe 3-ph 5.5kW                  | L1+L2+L3 | 9.6  | MCB Type C | 20 | 2.5mm² SY     | 15 | n/a   |
| W6 | C06 | Pillar drill 3-ph 2.2kW           | L1+L2+L3 | 4.2  | MCB Type C | 16 | 1.5mm² SY     | 12 | n/a   |
| W7 | C07 | Compressor 3-ph 7.5kW             | L1+L2+L3 | 14.0 | MCB Type D | 25 | 4mm² SY       | 25 | 100mA |
| W8 | C08 | Submain to gate house             | L1+N+CPC | 35.0 | MCB Type B | 40 | 10mm² SWA     | 60 | 30mA  |
|    |     | **Spare ways**                    |          |      |            |    |               |    |       |
| W9 | —   | (spare) | | | | | | | |
| W10| —   | (spare) | | | | | | | |
| W11| —   | (spare) | | | | | | | |
| W12| —   | (spare) | | | | | | | |

---

## Notes

- Total design demand: ~33 kW / 46 kVA / 65A per phase (75A peak with diversity at 1.0)
- 100A TPN intake provides ~35% headroom for growth
- Selectivity verified: 100A upstream switch-fuse provides full selectivity against all MCBs
- All socket-bearing circuits (C03, C04, C08) RCD-protected per KS 1700 §411.3.3
- C07 compressor uses 100mA RCD (motor-leakage tolerant)
- Downstream consumer: `electrical/earthing/examples/ke-nairobi-industrial-tn-s/`
