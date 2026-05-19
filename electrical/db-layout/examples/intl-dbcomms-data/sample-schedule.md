# DB Schedule — DB-COMMS, IEC Commercial 3-storey Office (LV Data/Comms Distribution)

**Project:** intl-comm-tpn-eg02
**Board:** DB-COMMS, IP4X enclosure, 32A TPN intake (fed from MSB-MAIN F06 — Type B RCD upstream per IEC 60364-5-53:2002 §531.3.3)
**Role:** comms_data_panel
**Generated:** 2026-05-19
**Jurisdiction:** INT (IEC 60364 series + IEC 60364-5-53 §531.3.3 + BS EN 50173-1/2:2018 + IEEE 802.3bt-2018)

---

| Way | Circuit | Designation | Phase | Device | In (A) | Cable | Length (m) | RCD |
|---|---|---|---|---|---|---|---|---|
| C01 | W1 | Main comms rack 24-port + PoE switch | L1 | MCB Type C | 16 | 4mm² LSZH Cu   |  5 | Type B, 30 mA (§531.3.3) |
| C02 | W2 | GF IDF cabinet + wall plates         | L2 | MCB Type C | 10 | 2.5mm² LSZH Cu | 30 | Type B, 30 mA (§531.3.3) |
| C03 | W3 | L1 IDF cabinet + wall plates         | L3 | MCB Type C | 10 | 2.5mm² LSZH Cu | 40 | Type B, 30 mA (§531.3.3) |
| C04 | W4 | L2 IDF cabinet + wall plates         | L1 | MCB Type C | 10 | 2.5mm² LSZH Cu | 50 | Type B, 30 mA (§531.3.3) |
| C05 | W5 | PoE+ AP injector (Wi-Fi mesh)        | L2 | MCB Type C |  6 | 1.5mm² LSZH Cu | 15 | Type B, 30 mA (§531.3.3) |
| C06 | W6 | PoE+ camera injector (security)      | L3 | MCB Type C |  6 | 1.5mm² LSZH Cu | 20 | Type B, 30 mA (§531.3.3) |
| C07 | W7 | UPS bypass loop feed (10 kVA)        | L1 | MCB Type C | 10 | 2.5mm² LSZH Cu |  3 | NONE (IEC 62040-1 §5.2.4) |
| W8-W10 | — | Spare ways                       |    |            |    |                |    |   |

---

## Selectivity verification

| Upstream | Downstream | Worst-case ratio | Fault level | Verdict | Source |
|---|---|---|---|---|---|
| MSB-MAIN F06 (32A MCB Type C) | DB-COMMS main switch + 6A-16A Type C MCBs | 32:16 = 2:1 (C01) | 8.0 kA | pass | engineer_declared per manufacturer cascade table (IEC 60898 same-curve, IEC 60364-5-53:2002 §536) |

---

## Notes

- **LV data/comms distribution.** IEC 60364-5-53:2002+A2:2015 §531.3.3 governs RCD selection: Type B (DC-sensitive) required for IT loads with SMPS/PoE/UPS rectifier front-ends that produce smooth DC residual currents
- **Supply class: essential.** Board role flagged as `comms_data_panel` for downstream segregation + SLD consumers; outage disrupts the entire office IT path even though not life-safety in the §560 sense
- All circuits use `voltage_class: "comms_data"` for IT-cabling segregation per BS EN 50174-2:2018 (typical ≥150 mm separation from unshielded LV power cables on shared trays)
- All cables LSZH Cu per IEC 60332-1 + IEC 60754 — low toxic emission in occupied office spaces
- Connected load ≈ 9.6 kW; design current ≈ 16.3A on 32A intake — ~2× headroom covers simultaneous boot-time inrush + UPS bypass changeover transient
- ALL Type C MCBs (Ia = 10×In) — handles SMPS inrush of comms switches + PoE+ injector cold-start + UPS rectifier energisation
- 10 kA Icn MCBs cover the ≈8.0 kA PFC at DB-COMMS (no cascade backup needed)
- **Type B RCD on every final circuit except C07.** §531.3.3 mandates Type B for IT loads with smooth-DC leakage; Type A/F would be blinded by SMPS/PoE rectifier residual currents per IEC 62423:2009
- **C07 UPS bypass is the only RCD-free circuit** — IEC 62040-1:2017 §5.2.4 design exemption; bypass paths must allow fault current to flow upstream for proper isolation
- BS EN 50173:2018 EMC accumulation: upstream 300 mA Type B at MSB-MAIN F06 provides cumulative leakage protection across the comms ecosystem (24-port main rack + 3 IDFs + 2 injectors can sum >30 mA pulsating + DC component normal leakage)
- PoE+ injectors (C05, C06) deliver IEEE 802.3bt-2018 Type 3 (30W per port) over Cat 6A structured cabling
- Selectivity: same-curve Type C → Type C cascade verified via manufacturer table (engineer-declared per IEC 60364-5-53:2002 §536). **C01 at 32:16 = 2:1 is cascade-critical** — sits at the minimum same-curve threshold; manufacturer confirmation required at 8 kA. Remaining circuits at 3.2:1 (C02-C04, C07) and 5.3:1 (C05-C06) with comfortable margin
- INFO flags: (1) Type B RCD sensitivity coordination at commissioning; (2) C01 cascade-critical verification — fault-level skill to confirm at coordination study
- Voltage drop sanity: longest L2 IDF run C04 (50m, 10A, 2.5mm² Cu) ≈ 1.4% — well within IT-equipment tolerance (typical 3% acceptable for IT distribution)
- 3 spare ways (W8-W10) for future additional IDFs, AV equipment rack, KVM/server-room sub-feed, or addressable rack-environmental monitoring (BS EN 50600-2-3)
- Upstream producer: MSB-MAIN F06; peers: DB-EM, DB-FA1, DB-L1, DB-P1, DB-M1
