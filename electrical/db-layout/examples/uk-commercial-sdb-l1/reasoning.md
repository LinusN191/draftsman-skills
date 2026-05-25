# Reasoning — UK 3-storey Office SDB-L1 (Level 1 Sub-DB)

## Site context

Level-1 sub-DB on the UK 3-storey commercial office. ~400m² floor plate housing open-plan workspace, meeting rooms, breakout area, printer corner, and small comms cabinet. No reception or kitchen (those are ground-floor only). Fed from MSB-MAIN F02 (100A MCCB Type D) via 30m run of 35mm² 5-core SWA XLPE Cu — the mid-length feeder run.

## Board sizing — 100A TPN intake

Connected load summary (12 final circuits): ~37 kW total connected; ~27 kW after diversity (DF ≈ 0.75 per CIBSE Guide F + BCO Guidance for typical commercial spec-office at the board-aggregate level — distinct from the per-circuit / per-load-type diversity that BS 7671:2018+A2:2022 § 311.1 + IET OSG Appendix A would prescribe on individual instantaneous loads). Design current per phase ≈ 27,000 / (√3 × 400 × 0.85) ≈ 46A — well below the 100A intake. Matches SDB-GF sizing convention for consistency across floors.

## Circuit allocation — differences vs SDB-GF

- L1 has no reception / no kitchen — those circuits replaced by breakout area sockets (C06) and printer-corner radial (C07)
- C09 dedicated UPS feed to L1 comms cabinet (small ~2 kW cabinet supporting floor-level data switches)
- C10 HVAC FCU bank — moves to W10 (Type C motor circuit), with the freed W08/W09 ways used for dedicated A/V rack + comms cabinet sockets

Identical RCD strategy + breaker curves to SDB-GF.

## RCD strategy — BS 7671:2018+A2 Reg 411.3.3

Universal 30mA Type A RCDs applied on all socket-bearing circuits per Reg 411.3.3 (AMD 2):

- C04 / C05 / C06 — socket ring final circuits (office, meeting rooms, breakout)
- C07 — printer corner socket radial
- C08 — dedicated A/V rack socket
- C09 — dedicated UPS feed socket (UPS itself handles continuous power; RCD protects the supply tail)
- C11 — IT/data desk ring
- C12 — AV outlet radial

Lighting C01, C02 not RCD-protected. Emergency lighting C03 dedicated supply per §560. HVAC FCU C10 motor circuit — Type C MCB, no socket → no Reg 411.3.3 requirement.

## MCB curve selection

Same as SDB-GF: Type B on lighting + sockets (BS 7671 §433/§434); Type C on HVAC FCU motor circuit (handles fan motor inrush); 10 kA Icn breaking capacity across all MCBs.

Estimated PFC at SDB-L1 ≈ 4.5 kA after 30m feeder impedance from 9.8 kA at MSB-MAIN — still within 10 kA MCB rating with comfortable margin.

## Selectivity verification

Upstream protection at MSB-MAIN F02 is a 100A MCCB Type D. Final-circuit MCBs at SDB-L1 are ≤32A:
- Current ratio: 100A / 32A = 3.1:1
- Type D upstream curve sits well above Type B/C downstream Ia bands
- Manufacturer cascade table verification deferred to fault-level cascade analysis (future SLD example)

## Voltage drop consideration

30m feeder run + ~36m furthest final circuit (C04) gives ~66m total cable run from MSB-MAIN to furthest socket. Voltage drop at full design current must stay ≤5% per BS 7671 Reg 525 — verification deferred to cable-sizing skill (future invocation).

## Downstream consumer

This board's intent-out.json is consumed by:
- `electrical/sld/examples/uk-commercial-office-3storey/` (multi-board cascade)
- (Future) `electrical/cable-sizing/` — verify each final-circuit cable against BS 7671 Appendix 4
- (Future) `electrical/fault-level/` — Zs verification at each final-circuit terminus
- (Future) `electrical/earthing/` — TN-C-S earthing arrangement at sub-DB level

## See also

- electrical/db-layout/examples/uk-commercial-msb-3storey/ (upstream — MSB-MAIN feeder F02)
- electrical/db-layout/examples/uk-commercial-sdb-gf/ (peer — ground floor sub-DB)
- electrical/db-layout/examples/uk-commercial-sdb-l2/ (peer — level 2 sub-DB)
