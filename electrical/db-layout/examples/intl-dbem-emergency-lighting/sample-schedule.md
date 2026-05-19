# DB Schedule — DB-EM, IEC Commercial 3-storey Office (Emergency Lighting Central Battery)

**Project:** intl-comm-tpn-eg02
**Board:** DB-EM, IP4X enclosure, 40A TPN intake (fed from MSB-MAIN F05 — NO upstream RCD per §560.7)
**Role:** emergency_lighting_panel
**Generated:** 2026-05-19
**Jurisdiction:** INT (IEC 60364 series + IEC 60364-5-56:2018 §560 + BS EN 50171 + IEC 60598-2-22)

---

| Way | Circuit | Designation | Phase | Device | In (A) | Cable | Length (m) | RCD |
|---|---|---|---|---|---|---|---|---|
| EM01 | W1 | GF corridor + escape route luminaires | L1 | MCB Type C | 10 | 1.5mm² FP200 LSZH | 35 | NONE (§560.7) |
| EM02 | W2 | GF stairwell + exit signs            | L2 | MCB Type C |  6 | 1.5mm² FP200 LSZH | 25 | NONE (§560.7) |
| EM03 | W3 | L1 corridor + escape route           | L3 | MCB Type C | 10 | 1.5mm² FP200 LSZH | 45 | NONE (§560.7) |
| EM04 | W4 | L1 stairwell + exit signs            | L1 | MCB Type C |  6 | 1.5mm² FP200 LSZH | 35 | NONE (§560.7) |
| EM05 | W5 | L2 corridor + escape route           | L2 | MCB Type C | 10 | 1.5mm² FP200 LSZH | 55 | NONE (§560.7) |
| EM06 | W6 | L2 stairwell + exit signs            | L3 | MCB Type C |  6 | 1.5mm² FP200 LSZH | 45 | NONE (§560.7) |
| EM07 | W7 | EM panel battery charger             | L1 | MCB Type C | 16 | 2.5mm² FP200 LSZH |  2 | NONE (§560.7) |
| EM08 | W8 | EM panel monitoring + test circuit   | L2 | MCB Type C |  6 | 1.5mm² FP200 LSZH |  2 | NONE (§560.7) |
| W9-W12 | — | Spare ways                         |    |            |    |                    |    |   |

---

## Selectivity verification

| Upstream | Downstream | Worst-case ratio | Fault level | Verdict | Source |
|---|---|---|---|---|---|
| MSB-MAIN F05 (40A MCB Type C) | DB-EM main switch + 6A-16A Type C MCBs | 40:16 = 2.5:1 (EM07) | 7.5 kA | pass | engineer_declared per manufacturer cascade table (IEC 60898 same-curve) |

---

## Notes

- **Life-safety distribution.** IEC 60364-5-56:2018 §560 governs the entire EM chain: NO upstream RCD, NO final-circuit RCD, all EM cables fire-rated, dedicated circuit isolation
- **Supply class: essential.** Board role flagged as `emergency_lighting_panel` for downstream segregation + SLD consumers
- All circuits use `voltage_class: "emergency_lighting"` for segregation
- All cables FP200 LSZH per IEC 60331 / BS EN 50200 — 30/60/120-min fire survival depending on variant
- Connected load ≈ 4.9 kW; 40A intake matches upstream MSB-MAIN F05 breaker; headroom covers battery-charger boost transient + simultaneous luminaire energisation after test discharge
- ALL Type C MCBs (Ia = 10×In) — handles LED driver bank inrush + battery-charger SMPS energisation
- 10 kA Icn MCBs cover the ≈7.5 kA PFC at DB-EM (no cascade backup needed)
- Selectivity: same-curve Type C → Type C cascade verified via manufacturer table (engineer-declared per IEC 60364-5-53 §536). EM07 16A charger is the worst-case 2.5:1 ratio; remaining circuits at 4:1+ comfortable margin
- INFO flag (BS EN 50171 §6.12 + IEC 60598-2-22 §22.6): AHJ-required survival duration (1h / 2h / 3h per local building code) to be verified against the battery commissioning certificate at handover
- Central battery rated 3-hour autonomy minimum per BS EN 50171:2001+A1:2022; installer to provide compliance certificate + 3-hour discharge test report
- Luminaires throughout conform to IEC 60598-2-22:2014+A2:2020 (escape-route + stairwell + exit-sign luminaires fed at 230V from central battery via fire-rated cable)
- Voltage drop sanity: longest corridor zone EM05 (55m, 10A, 1.5mm² Cu) ≈ 3.5% — within emergency-luminaire driver tolerance (typical 6-8% acceptable)
- 4 spare ways (W9-W12) for future basement EM zone, plant-room EM, external escape-route luminaires, or addressable luminaire-monitoring interface
- Upstream producer: MSB-MAIN F05; peers: DB-FA1, DB-L1, DB-P1, DB-M1
