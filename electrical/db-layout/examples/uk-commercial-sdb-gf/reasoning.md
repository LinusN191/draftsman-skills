# Reasoning — UK 3-storey Office SDB-GF (Ground Floor Sub-DB)

## Site context

Ground-floor sub-DB on the UK 3-storey commercial office. ~400m² floor plate housing reception, open-plan workspace, meeting rooms, kitchen/breakout, and a small printer corner. Fed from MSB-MAIN F01 (100A MCCB Type D) via 15m run of 35mm² 5-core SWA XLPE Cu — the shortest of the three feeder runs (SDB-GF, SDB-L1, SDB-L2).

## Board sizing — 100A TPN intake

Connected load summary (12 final circuits): ~38 kW total connected; ~28 kW after diversity (DF ≈ 0.75 per BS 7671 Appendix 1 typical commercial office). Design current per phase ≈ 28,000 / (√3 × 400 × 0.85) ≈ 47A — well below the 100A intake. Headroom suits open spec-office tenant variation.

100A TPN sub-DB is the standard UK commercial floor-DB rating for ~400m² spec-office plates.

## RCD strategy — BS 7671:2018+A2 Reg 411.3.3

Universal 30mA Type A RCDs applied on all socket-bearing circuits per Reg 411.3.3 (AMD 2). Type A specified because modern office equipment (LED drivers, IT switching supplies, EV-trickle desk chargers) produces pulsating DC residual fault currents that Type AC cannot detect:

- C04 / C05 / C06 — socket ring final circuits (office, meeting rooms, reception)
- C07 — kitchen socket radial (water/heat proximity — additional reason for 30mA)
- C08 — dedicated printer socket
- C10 — corridor cleaner sockets
- C11 — IT/data desk ring
- C12 — AV outlet radial

Lighting circuits C01, C02 are NOT RCD-protected (Reg 411.3.3 socket-exemption applies only to circuits supplying sockets ≤32A). C09 HVAC FCU is a fixed motor circuit — no socket, no Reg 411.3.3 RCD requirement; Type C MCB handles inrush.

## Emergency lighting C03 — dedicated supply

C03 emergency lighting is a dedicated circuit per BS 7671:2018+A2 §560. NOT RCD-protected, NOT downstream-RCD-fed via shared RCBO bank — life-safety availability takes priority over earth-leakage trip risk. Voltage class `emergency_lighting` in the intent payload signals to downstream consumers (riser, schematic, life-safety segregation rules) that this circuit is segregated.

## MCB curve selection

- Type B (Ia = 5×In) on lighting + sockets — standard final-circuit selection, matches BS 7671 §433 + §434 for resistive/light-electronic loads
- Type C (Ia = 10×In) on HVAC FCU C09 — handles fan motor starting inrush (≈6×FLC for ≈100ms)
- 10 kA Icn breaking capacity across all MCBs (BS EN 60898) — adequate for ≈6 kA PFC estimate at SDB-GF after 15m feeder impedance

## Selectivity verification

Upstream protection at MSB-MAIN F01 is a 100A MCCB Type D. Final-circuit MCBs at SDB-GF are ≤32A:
- Current ratio: 100A / 32A = 3.1:1 (BS EN 60947-2 cascade tables typically achieve selectivity to 2.5:1 for MCCB-vs-MCB pairings with Type D upstream)
- Type D upstream curve (Ia = 20×In) sits well above Type B/C downstream Ia bands, so transient inrush at the sub-DB does not trip the upstream
- Manufacturer cascade table verification deferred to fault-level cascade analysis (future SLD example)

## Downstream consumer

This board's intent-out.json is consumed by:
- `electrical/sld/examples/uk-commercial-office-3storey/` (multi-board cascade)
- (Future) `electrical/cable-sizing/` — verify each final-circuit cable against BS 7671 Appendix 4
- (Future) `electrical/fault-level/` — Zs verification at each final-circuit terminus
- (Future) `electrical/earthing/` — TN-C-S earthing arrangement at sub-DB level

## See also

- electrical/db-layout/examples/uk-commercial-msb-3storey/ (upstream — MSB-MAIN feeder F01)
- electrical/db-layout/examples/uk-commercial-sdb-l1/ (peer — level 1 sub-DB)
- electrical/db-layout/examples/uk-commercial-sdb-l2/ (peer — level 2 sub-DB)
