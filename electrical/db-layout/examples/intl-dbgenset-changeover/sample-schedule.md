# DB Schedule — DB-GENSET-XCV, IEC Commercial 3-storey Office (Standby-Genset Changeover Sub-DB with ATS)

**Project:** intl-comm-tpn-eg02
**Board:** DB-GENSET-XCV, IP4X (ATS section, indoor plant room) + IP54 (contactor section, external genset enclosure), 63A TPN intake on ATS-output side (dual-source: utility MSB-MAIN F08 + 80 kVA standby genset via ATS per IEC 60364-5-56:2018 §552)
**Role:** ats_changeover_panel — supply_class: essential
**Generated:** 2026-05-19
**Jurisdiction:** INT (IEC 60364 series + IEC 60364-5-56:2018 §552/§551/§556/§560.7 + ISO 8528-12:1997 + IEC 60909-0:2016 §3.5/§3.5.1 + IEC 60947-2 + IEC 62040-1:2017 §5.2.4 + IEC 60364-4-41 §411.3.3 + IEEE 446-1995)

---

| Way | Circuit | Designation | Phase | Device | In (A) | Cable | Length (m) | RCD |
|---|---|---|---|---|---|---|---|---|
| G01 | W1 | ATS controller + signaling (24 VDC supervisory) | ELV control | MCB Type C |  6 | 1.5mm² LSZH Cu (3-core) |  2 | NONE (supervisory ELV_control; SMPS-derived 24 VDC per IEC 60364-5-51 §514.5) |
| G02 | W2 | EM lighting changeover feed to DB-EM            | L1+L2+L3+N  | MCB Type C | 32 | 6mm² LSZH Cu (4-core)   | 80 | NONE (life-safety per IEC 60364-5-56:2018 §560.7 — RCD would defeat dual-source resilience) |
| G03 | W3 | Fire alarm changeover feed to DB-FA1            | L1+L2+L3+N  | MCB Type C | 20 | 4mm² LSZH Cu (4-core)   | 60 | NONE (life-safety per §560.7) |
| G04 | W4 | UPS bypass mains backup to DB-UPS               | L1+L2+L3+N  | MCB Type C | 32 | 6mm² LSZH Cu (4-core)   | 40 | NONE (UPS bypass per IEC 62040-1:2017 §5.2.4 — must allow upstream fault flow) |
| G05 | W5 | Genset day tank + cooling fan                   | L1          | MCB Type C | 10 | 2.5mm² LSZH Cu (3-core) |  5 | Type A, 30 mA (§411.3.3 — exterior route + fuel handling + motor windings) |
| W6-W8 | — | Spare ways                       |             |            |    |                         |    |   |

---

## Selectivity verification

| Upstream | Downstream | Worst-case ratio | Fault level | Verdict | Source |
|---|---|---|---|---|---|
| MSB-MAIN F08 (63A MCCB Type D) → ATS → DB-GENSET-XCV main switch | 6A-32A Type C MCBs at DB-GENSET-XCV | 63:32 = ~2:1 (G02/G04) | 9.0 kA utility-mode / ~1.0 kA genset-mode subtransient Ik" (sustained Ik ~0.4 kA after AVR settles) | info — MCCB-MCB cascade with class differential | engineer_declared per MCCB-MCB manufacturer cascade chart (IEC 60898-1 + IEC 60947-2 + IEC 60364-5-53:2002 §536; dual-mode per IEC 60909-0:2016 §3.5 + §3.5.1 + IEC 60909-1:2002 Table A.1) |

---

## Notes

- **Standby-genset changeover distribution with ATS — dual-source resilience.** Utility-priority logic per IEC 60364-5-56:2018 §552: ATS rests on utility-source; on utility loss, auto-starts the 80 kVA standby genset and transfers after stability achieved; reverses on utility return + 30 s stable + 5-min cooldown
- **Transfer time: 6-10 s typical for an 80 kVA medium-genset** per ISO 8528-12:1997 Class A2 (cold-start optimised). Breakdown: 1-2 s utility-loss detection + 3-5 s engine crank-to-stable + 0.5-1 s ATS dwell + 0.5-1 s breaker close + 0.5-1 s load-step settling
- **WARNING — ATS transfer-time AHJ disclosure.** The 6-10 s design intent sits AT the NFPA 110-2022 Type 10 (≤10 s) boundary and BELOW the BS EN 50171:2001+A1:2022 §6.3 Type Z (≤0.5 s) threshold. AHJ sign-off required at commissioning. Downstream sub-DBs bridge the gap through their own autonomy:
  - DB-EM downstream of G02 — central-battery EM-CB with 3-hour autonomy bridges via internal battery; G02 re-energises charger once genset is online
  - DB-FA1 downstream of G03 — fire-alarm panel with 4-hour internal battery bridges via internal battery; G03 re-energises charger once genset is online
  - DB-UPS downstream of G04 — UPS 30-min ride-through bridges via battery; G04 re-energises UPS rectifier once genset is online (G04 is the bypass alternative to the direct-utility F07 feed)
- **Supply class: essential.** Board role flagged as `ats_changeover_panel` for downstream SLD/riser/fault-level/generator-sizing/earthing consumers; safety-services bus with dual-source resilience
- All circuits use `voltage_class` per IEC 60364-5-51 §514.5 taxonomy: G01 is `ELV_control` (24 VDC supervisory), G02-G05 are `LV_power`
- All cables LSZH Cu per IEC 60332-1 + IEC 60754 — low toxic emission in occupied plant room + genset enclosure
- Connected load ≈ 24 kW (≈ 30 kVA at 0.8 PF); genset sized 80 kVA — ~2.5× headroom for block-load step + cold-start motor inrush + 3 spare-ways future expansion
- ALL Type C MCBs on ATS-output side (Ia = 10×In) — handles SMPS cluster inrush at the four downstream sub-DB rectifier charge paths + motor inrush at G05 + block-load step on ATS transfer
- Upstream MSB-MAIN F08 = 63A MCCB Type D (Ia = 10-20×In) — Type D selected to tolerate the genset block-load transfer transient travelling upstream through the briefly-closed utility contactor during ATS transfer
- 10 kA Icn MCBs cover the 9.0 kA utility-mode declared PFC at the ATS output per IEC 60909-0:2016 §3.5 (utility-side 22.5 kA reduced by 60m × 16mm² feeder impedance)
- Genset-mode declared subtransient Ik" ~1.0 kA per IEC 60909-0:2016 §3.5.1 equivalent voltage source method on 80 kVA (In ≈ 115.5 A, Xd" ≈ 0.12 pu per IEC 60909-1:2002 Table A.1, E" ≈ 1.05 pu → Ik" ≈ 1.01 kA, peak ip ≈ 2.57 kA at κ ≈ 1.8); sustained Ik ≈ 0.4 kA (3-5× In after AVR field forcing settles ~5 s post-fault) — both modes significantly lower than utility-mode; well within 10 kA Icn
- **One-tier RCD posture — only G05 is RCD-protected:**
  - G01 (ATS controller) RCD-free — supervisory ELV_control per §514.5
  - G02 (EM lighting feed) RCD-free — safety-services emergency feed per §560.7
  - G03 (fire alarm feed) RCD-free — safety-services emergency feed per §560.7
  - G04 (UPS bypass) RCD-free — UPS bypass per IEC 62040-1:2017 §5.2.4 (must allow upstream fault flow)
  - G05 (day tank + cooling fan) Type A 30 mA per §411.3.3 — exterior-route + fuel-handling + motor-windings justify shock protection
- **4-pole transfer ATS** (L1+L2+L3+N switched together) per IEC 60364-5-56:2018 §552 — genset operates as separately derived TN-S system in genset-mode with separate neutral-earth bonding contact; prevents parallel-neutral fault paths to utility transformer
- **Split-location enclosure:** ATS controller + utility-source breaker in IP4X indoor plant room; genset-source contactor + transfer cabling in IP54 external genset enclosure; sealed wall penetration per IEC 60364-5-52 §522.8.3
- Selectivity: MCCB-upstream-of-MCB cascade at G02/G04 (63:32 = ~2:1) — AT IEC 60898 same-curve minimum BUT benefits from MCCB-class cross-discrimination per IEC 60947-2 (Type D magnetic 10-20×In vs Type C 5-10×In). **Fault-level skill must verify at BOTH 9.0 kA utility-mode and ~1.0 kA genset-mode subtransient Ik" (sustained Ik ~0.4 kA after AVR settles) + time-domain ATS transfer-dwell analysis per IEC 60909-1:2002**
- INFO flag: cascade verification at G02/G04 — MCCB-MCB manufacturer chart confirmation required at full coordination study
- Voltage drop sanity: G02 EM lighting feed (80m, 32A, 6mm² Cu) ≈ 1.8% — within 5% IEC 60364-5-52 limit; G03 fire alarm feed (60m, 20A, 4mm² Cu) ≈ 1.5%; G04 UPS bypass (40m, 32A, 6mm² Cu) ≈ 0.9%; G01/G05 negligible
- 3 spare ways (W6-W8) for future safety-services feeds (CCTV/security/access-control), genset block heater (cold-climate retrofit), or genset-room utility lighting/maintenance socket
- **Placard on DB-GENSET-XCV faceplate: "DUAL-SOURCE — UTILITY/GENSET ATS — DO NOT BACK-FEED"** per IEEE 446-1995 critical-power labelling practice + IEC 60364-5-56:2018 §552 dual-source warning requirement
- Upstream producer: MSB-MAIN F08 (63A MCCB Type D, 60m feeder) AND 80 kVA standby genset via 4-pole ATS; peers: DB-EM (G02 destination), DB-FA1 (G03 destination), DB-UPS (G04 destination — bypass alternative); other peers: DB-COMMS, DB-L1, DB-P1, DB-M1

---

## ATS transfer-time AHJ disclosure (governing standard cross-reference)

| Benchmark | Limit | Verdict | Mitigation |
|---|---|---|---|
| **NFPA 110-2022 Type 10** (US-aligned life-safety branch) | ≤10 s | AT BOUNDARY — passes if commissioning test confirms ≤10 s under cold-start | Engine block heater + AVR pre-energisation + monthly exercise cycle |
| **BS EN 50171:2001+A1:2022 §6.3 Type Z** (EU central-battery EM transfer) | ≤0.5 s | DOES NOT MEET — requires Type Z bridging | Downstream DB-EM is central-battery EM-CB (3-hour autonomy) — bridges the gap |
| **BS EN 50171:2001+A1:2022 §6.3 Type N** (EU central-battery EM acceptable transfer) | ≤15 s | MEETS — 6-10 s well within Type N | Downstream DB-EM Type N classification acceptable |
| **ISO 8528-12:1997 Class A1** (no-break safety-services) | ≤1 s | DOES NOT MEET — requires no-break system (flywheel/rotary UPS) | Not applicable — design relies on central-battery + UPS ride-through, not no-break |
| **ISO 8528-12:1997 Class A2** (short-break safety-services) | 1-15 s | MEETS — 6-10 s within Class A2 | Cold-start optimisation (block heater + AVR pre-energisation) confirmed at commissioning |
| **IEC 60364-5-56:2018 §556+§551** (general safety services + LV generating sets) | Engineer-declared per AHJ | MEETS — engineer-declared 6-10 s + AHJ sign-off | Commissioning test report + battery-bridging documentation |

**Sign-off required before energisation:** UPS commissioning certificate + EM-CB battery discharge test report + fire-alarm panel battery discharge test report + ATS transfer-time test report (cold-start + warm-start scenarios) + AHJ acceptance against the strictest applicable benchmark above.
