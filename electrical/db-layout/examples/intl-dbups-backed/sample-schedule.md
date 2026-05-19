# DB Schedule — DB-UPS, IEC Commercial 3-storey Office (UPS-Backed Critical Loads)

**Project:** intl-comm-tpn-eg02
**Board:** DB-UPS, IP4X enclosure, 50A TPN intake on UPS-output side (fed from MSB-MAIN F07 → 10 kVA online double-conversion UPS per IEC 62040-1:2017)
**Role:** ups_backed_critical_panel — supply_class: ups_plus_essential
**Generated:** 2026-05-19
**Jurisdiction:** INT (IEC 60364 series + IEC 62040-1:2017 + IEC 60364-5-53 §531.3.3 + IEC 60364-4-41 §411.3.3 + IEEE 446-1995)

---

| Way | Circuit | Designation | Phase | Device | In (A) | Cable | Length (m) | RCD |
|---|---|---|---|---|---|---|---|---|
| U01 | W1 | Server rack 6 kVA (UPS output)        | L1+L2+L3 | MCB Type C | 32 | 6mm² LSZH Cu (5-core)   |  8 | Type B, 30 mA (§531.3.3) |
| U02 | W2 | Critical workstations ring (admin)    | L1       | MCB Type C | 16 | 2.5mm² LSZH Cu          | 30 | Type A, 30 mA (§411.3.3) |
| U03 | W3 | Critical workstations ring (clinical) | L2       | MCB Type C | 16 | 2.5mm² LSZH Cu          | 35 | Type A, 30 mA (§411.3.3) |
| U04 | W4 | Lab benches power (essential)         | L3       | MCB Type C | 10 | 2.5mm² LSZH Cu          | 25 | Type A, 30 mA (§411.3.3) |
| U05 | W5 | BMS controller + alarm panel          | L1       | MCB Type C |  6 | 1.5mm² LSZH Cu          | 15 | NONE (supervisory; BMS-internal earth-leakage on DC field side) |
| U06 | W6 | UPS bypass (maintenance loop)         | L1+L2+L3 | MCB Type C | 32 | 6mm² LSZH Cu (5-core)   |  2 | NONE (IEC 62040-1:2017 §5.2.4 — bypass must allow upstream fault flow) |
| W7-W10 | — | Spare ways                       |          |            |    |                         |    |   |

---

## Selectivity verification

| Upstream | Downstream | Worst-case ratio | Fault level | Verdict | Source |
|---|---|---|---|---|---|
| MSB-MAIN F07 (50A MCB Type C) → 10 kVA UPS → DB-UPS main switch | 6A-32A Type C MCBs at DB-UPS | 50:32 = 1.56:1 (U01/U06) | 6.5 kA UPS-output / 22.5 kA bypass-fed | info — cascade-critical | engineer_declared per UPS manufacturer coordination chart (IEC 60898 same-curve, IEC 60364-5-53:2002 §536, IEC 62040-1:2017 Annex E) |

---

## Notes

- **UPS-backed critical-loads distribution.** Online double-conversion topology per IEC 62040-3:2011 Class VFI-SS-111 — load is ALWAYS fed from inverter; bypass static switch engages only on UPS internal fault or scheduled maintenance
- **30-min ride-through autonomy (design intent)** — sufficient for orderly server-rack shutdown via BMS (U05) and graceful workstation-session preservation. AHJ-required business-continuity duration must be verified against UPS commissioning certificate + battery discharge test report at handover
- **Supply class: ups_plus_essential.** Board role flagged as `ups_backed_critical_panel` for downstream SLD/riser/fault-level/generator-sizing consumers; dual-classification signals UPS-backed AND essential
- All circuits use `voltage_class: "LV_power"` for standard LV distribution treatment (no special segregation beyond LSZH cabling discipline)
- All cables LSZH Cu per IEC 60332-1 + IEC 60754 — low toxic emission in occupied server/UPS room
- Connected load ≈ 11.1 kW (≈ 13.9 kVA at 0.8 PF); UPS sized 10 kVA — engineer to verify peak coincident-demand profile at design hand-off; upsize to 15 kVA if peak exceeds 8 kVA sustained
- ALL Type C MCBs (Ia = 10×In) — handles server-rack PSU cluster inrush + workstation cold-start + lab-instrument motor-start + bypass changeover transient
- 10 kA Icn MCBs cover the ≈6.5 kA UPS-output PFC at DB-UPS per IEC 62040-1:2017 Annex E (no cascade backup needed at device level)
- **Three-tier RCD strategy:**
  - Tier 1 — Type B 30 mA on U01 (server rack): IT-load DC leakage per §531.3.3
  - Tier 2 — Type A 30 mA on U02-U04 (socket circuits ≤32A): pulsating-DC leakage per §411.3.3
  - Tier 3 — NO RCD on U05 (BMS supervisory) and U06 (UPS bypass per §5.2.4)
- **U06 UPS bypass is RCD-free by deliberate design** — IEC 62040-1:2017 §5.2.4: bypass path must allow earth-fault current to flow upstream to MSB-MAIN F07 for proper isolation; RCD would create parallel earth path and defeat bypass-availability purpose during maintenance changeover
- **U05 BMS is RCD-free** — dedicated supervisory circuit with no general-purpose sockets downstream; BMS panel contains internal earth-leakage monitoring on its 24V DC field side
- Selectivity: same-curve Type C → Type C cascade across the UPS verified via UPS manufacturer coordination chart (engineer-declared per IEC 60364-5-53:2002 §536). **U01/U06 at 50:32 = 1.56:1 is cascade-critical** — sits BELOW the 2:1 IEC 60898 same-curve minimum threshold; fault-level skill must confirm at 6.5 kA UPS-output PFC + 22.5 kA bypass-fed PFC + UPS ride-through/changeover sequence
- INFO flags: (1) battery autonomy verification at handover; (2) cascade-critical at U01/U06 — fault-level skill to confirm at coordination study
- Voltage drop sanity: server rack U01 (8m, 32A, 6mm² Cu) ≈ 0.4%; longest workstation run U03 (35m, 16A, 2.5mm² Cu ring) ≈ 1.4% — both well within IT-equipment tolerance
- 4 spare ways (W7-W10) for future additional server-rack zones, secondary BMS interface, AV-control rack, or addressable PDU/environmental-monitoring sub-feed (BS EN 50600-2-3)
- **Placard on DB-UPS faceplate: "UPS-OUTPUT — DO NOT BACK-FEED"** per IEEE 446-1995 critical-power labelling practice
- Upstream producer: MSB-MAIN F07 → 10 kVA online double-conversion UPS; peers: DB-EM, DB-FA1, DB-COMMS, DB-L1, DB-P1, DB-M1
