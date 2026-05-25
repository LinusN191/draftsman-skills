# Reasoning — UK 3-storey Office SDB-L2 (Level 2 Sub-DB)

## Site context

Level-2 sub-DB on the UK 3-storey commercial office. ~400m² floor plate — identical layout to Level 1 (open-plan workspace, meeting rooms, breakout area, printer corner, comms cabinet). Fed from MSB-MAIN F03 (100A MCCB Type D) via **45m run** of 35mm² 5-core SWA XLPE Cu — the longest feeder run in the cascade. This length drives the tightest Zs verification in any future SLD cascade analysis.

## Board sizing — 100A TPN intake

Connected load summary (12 final circuits): ~37 kW total connected; ~27 kW after diversity (DF ≈ 0.75 per CIBSE Guide F + BCO Guidance for typical commercial spec-office at the board-aggregate level — distinct from per-circuit / per-load-type diversity prescribed by BS 7671:2018+A2:2022 § 311.1 + IET OSG Appendix A on individual instantaneous loads). Design current per phase ≈ 46A — well below 100A. Matches SDB-L1 sizing convention for consistency across upper floors.

## Why this DB is the cascade bottleneck

The 45m feeder run is 50% longer than F02 (30m) and 3× the length of F01 (15m). Three consequences:

1. **PFC drop** — Estimated PFC at SDB-L2 ≈ 3.5 kA (down from 9.8 kA at MSB-MAIN intake) due to 45m of 35mm² SWA series impedance. Still well within the 10 kA Icn of all final-circuit MCBs, but the margin is tightest here.

2. **Zs tightness** — Earth-fault loop impedance at the furthest final-circuit terminus (C04, 36m of 2.5mm² T+E from SDB-L2) accumulates ~45m + ~36m = 81m of conductor impedance from the MSB-MAIN intake. Compliance with BS 7671 Table 41.3 (Zs ≤ 1.37Ω for 32A Type B in TN system, 0.4s disconnection) needs verification once cable impedances are known.

3. **Voltage drop** — At full design current the voltage drop along ~81m of conductor must stay ≤5% per BS 7671 Reg 525. With 30mA RCD protection downstream, ADS via RCD reduces Zs urgency for life safety, but Zs compliance remains required.

These checks are flagged in `compliance_summary.assumptions` and deferred to the cable-sizing + fault-level skills (future SLD cascade invocation).

## Circuit allocation

Identical to SDB-L1 (open office + breakout + meeting rooms layout). 12 final circuits + 4 spare ways. Same RCD strategy, same MCB curves, same load profile.

## RCD strategy — BS 7671:2018+A2 Reg 411.3.3

Universal 30mA Type A RCDs on all socket-bearing circuits (C04-C09, C11, C12). Lighting C01/C02 not RCD-protected. Emergency lighting C03 dedicated supply per §560. HVAC FCU C10 fixed motor circuit — no socket → no Reg 411.3.3 requirement.

The 30mA RCD layer here also provides additional protection against indirect contact in case Zs at long-runs exceeds Table 41.3 — RCD operates well before MCB on earth fault per Reg 411.4.5.

## MCB curve selection

Same as SDB-L1: Type B on lighting + sockets (BS 7671 §433/§434); Type C on HVAC FCU motor circuit; 10 kA Icn breaking capacity across all MCBs (adequate for 3.5 kA estimated PFC + 65% margin).

## Selectivity verification

Upstream protection at MSB-MAIN F03 is 100A MCCB Type D. Final-circuit MCBs at SDB-L2 are ≤32A:
- Current ratio: 3.1:1
- Type D upstream curve (Ia = 20×In) sits well above Type B/C downstream Ia bands
- Manufacturer cascade table verification deferred to fault-level cascade analysis

## Downstream consumer

This board's intent-out.json is consumed by:
- `electrical/sld/examples/uk-commercial-office-3storey/` (multi-board cascade — L2 is the bottleneck branch)
- (Future) `electrical/cable-sizing/` — verify each final-circuit cable, voltage drop at 45m feeder + 36m final
- (Future) `electrical/fault-level/` — Zs verification at each final-circuit terminus
- (Future) `electrical/earthing/` — TN-C-S earthing at L2 sub-DB level

## See also

- electrical/db-layout/examples/uk-commercial-msb-3storey/ (upstream — MSB-MAIN feeder F03)
- electrical/db-layout/examples/uk-commercial-sdb-gf/ (peer — ground floor sub-DB)
- electrical/db-layout/examples/uk-commercial-sdb-l1/ (peer — level 1 sub-DB)
