# DB Schedule — DB-FA1, IEC Commercial 3-storey Office (Fire Alarm Panel)

**Project:** intl-comm-tpn-eg02
**Board:** DB-FA1, IP4X enclosure, 63A TPN intake (fed from MSB-MAIN F04 — NO upstream RCD per §560)
**Role:** fire_alarm_panel
**Generated:** 2026-05-18
**Jurisdiction:** INT (IEC 60364 series + IEC 60364-5-56 §560 + IEC 62820)

---

| Way | Circuit | Designation | Phase | Device | In (A) | Cable | Length (m) | RCD |
|---|---|---|---|---|---|---|---|---|
| FA01 | W1 | Fire alarm panel power supply         | L1 | MCB Type C |  6 | 1.5mm² FP200 LSZH |  5 | NONE (§560) |
| FA02 | W2 | Zone loop 1 (GF detectors)            | L2 | MCB Type C |  6 | 1.5mm² FP200 LSZH | 40 | NONE (§560) |
| FA03 | W3 | Zone loop 2 (L1 detectors)            | L3 | MCB Type C |  6 | 1.5mm² FP200 LSZH | 60 | NONE (§560) |
| FA04 | W4 | Zone loop 3 (L2 detectors)            | L1 | MCB Type C |  6 | 1.5mm² FP200 LSZH | 80 | NONE (§560) |
| FA05 | W5 | Sounder/strobe circuit (all floors)   | L2 | MCB Type C | 10 | 2.5mm² FP200 LSZH | 70 | NONE (§560) |
| FA06 | W6 | Battery charger / standby supply      | L3 | MCB Type C |  6 | 1.5mm² FP200 LSZH |  3 | NONE (§560) |
| W7-W8 | — | Spare ways                           |    |            |    |                    |    |   |

---

## Notes

- **Life-safety distribution.** IEC 60364-5-56:2018 §560 governs the entire FA chain: NO upstream RCD, NO final-circuit RCD, all FA cables fire-rated, dedicated circuit isolation
- **Supply class: essential.** Board role flagged as `fire_alarm_panel` for downstream segregation + SLD consumers
- All circuits use `voltage_class: "fire_alarm"` for segregation
- All cables FP200 LSZH per IEC 60331 / BS EN 50200 — 30/60/120-min fire survival depending on variant
- Connected load ≈ 3 kW; 63A intake matches upstream MSB-MAIN F04 breaker; massive headroom accommodates sounder alarm-condition peak + future expansion
- ALL Type C MCBs (Ia = 10×In) — handles FA panel SMPS + sounder bank inrush
- 10 kA Icn MCBs cover the ≈9 kA PFC at DB-FA1 (no cascade backup needed)
- Selectivity: same-curve Type C → Type C cascade verified via manufacturer table (engineer-declared per IEC 60364-5-53 Clause 536)
- INFO flag (§560.7.1): consider ATS to a secondary supply if AHJ standby duration exceeds the integral panel battery (typical 24h standby + 30min alarm)
- Voltage drop sanity: longest zone loop FA04 (80m, 6A, 1.5mm² Cu) ≈ 1.5% — well within FA panel loop tolerance
- 2 spare ways for future atrium sounders, access-control interface, lift-recall interface, or voice-alarm upgrade (EN 54-16)
- Upstream producer: MSB-MAIN F04; peers: DB-L1, DB-P1, DB-M1
