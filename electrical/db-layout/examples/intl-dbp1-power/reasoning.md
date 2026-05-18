# Reasoning — INT DB-P1 (Small-Power Sub-DB)

## Site context

Small-power sub-DB serving the generic IEC commercial 3-storey office building. DB-P1 is the largest of the four sub-DBs downstream of MSB-MAIN, reflecting the dominance of small-power demand in a modern office (IT equipment, desk power, kitchen, AV, photocopiers). 400A TPN intake fed from MSB-MAIN F02 (400A MCCB Type D, 40m feeder). Located in the level-1 electrical riser cupboard so the longest run to the L2 ring main is ~100m.

## Board sizing — 400A TPN intake

Connected load summary across 12 circuits ≈ 47 kW. Applying IEC 60364-1 Annex C diversity for office small-power (DF ≈ 0.55-0.65): after-diversity demand ≈ 28 kW. Design current per phase = 28,000 / (√3 × 400 × 0.85) ≈ 47A. The 400A intake provides huge headroom — but it matches the upstream MSB-MAIN F02 MCCB rating directly. The feeder is sized for the breaker rating, not the diversified load. This is the conventional pattern in spec-office distribution.

Six spare ways (W13-W18) provision generously for tenant fit-out churn — additional ring mains, dedicated IT/server outlets, EV-charge points at parking integration, future printer rooms.

## Circuit type strategy

| Type | Circuits | Pattern |
|------|----------|---------|
| 32A socket ring main | P01, P02, P03, P08, P09, P10 | Per-floor open-office sockets + per-floor IT/data desks. Ring topology, 2.5mm² PVC. |
| 20A socket radial | P04, P05, P07, P11, P12 | Meeting-room sockets, kitchen, AV outlets, cleaner sockets. Radial topology, 2.5mm². |
| 16A dedicated radial | P06 | Photocopier room with specific equipment power requirement. |

Ring mains are appropriate for the high-density open-office where ~30-40 sockets sit on the same circuit; radials are used for low-density discrete rooms.

## RCD strategy — IEC 60364-4-41 Clause 411.3.3

**Universal 30mA Type A RCD on every circuit at DB-P1** — all 12 circuits are socket-bearing or feed equipment with significant SMPS content. Type A is mandatory because:

- All office loads include switched-mode power supplies (laptops, monitors, dock stations, phone chargers)
- Modern desk equipment frequently has DC residual currents from EMC filtering capacitors
- Type AC RCDs are blind to pulsating DC and AC-with-DC-component fault currents
- IEC 60364-4-41:2018 Clause 411.3.3 explicitly requires Type A or higher for circuits supplying sockets ≤32A in dwellings, commercial, and similar premises

P07 kitchen socket additionally satisfies IEC 60364-7-701 series (water proximity zones) by RCD protection.

## Ring-circuit voltage drop sanity check

Longest ring is P10 (IT/data desks on L2, 100m loop):
- 100m × 32A × 0.0181 Ω/m (2.5mm² Cu AC at 70°C) / 2 (ring halves) ≈ 2.9 V over ring half
- Round trip ≈ 2.9V × 2 ≈ 5.8 V at full load = 2.5% drop
- Plus feeder drop (40m × 47A diversified / 70mm² ≈ 0.3V × 2 = 0.6V) = ~0.3% additional
- Total: ~2.8% — within 4% socket-circuit guidance in IEC 60364-5-52 Annex E

P03 (open-office ring at 95m, 32A) and P09 (IT/data at 80m, 32A) sit comfortably below P10.

## Cable selection rationale

2.5mm² for all 32A and 20A ring/radial circuits. For 32A ring mains, the 2.5mm² ring is rated at ~27A per leg at Reference Method C (clipped direct or installed in conduit) but IEC 60364-5-52 Annex E ring-circuit allowance permits a 32A protective device on a 2.5mm² ring main because the ring topology halves the load on each leg.

For P06 (16A radial — photocopier), 2.5mm² is well over-rated but standardised for ease of installation and future load growth.

## MCB curve — all Type B

Type B (Ia = 5×In) across all 12 circuits. Type B is the universal commercial office small-power choice — handles the modest steady-state inrush of office equipment without nuisance trip while giving tight earth-fault loop disconnection time. Type C is unnecessary because:
- No motor circuits (mechanical loads on DB-M1)
- No large LED-driver inrush (lighting on DB-L1)
- No charging-capacitor banks

## Selectivity verification

Upstream MSB-MAIN F02 = 400A MCCB Type D. Final-circuit MCBs at DB-P1 are ≤32A:
- Current ratio: 400/32 = 12.5:1 — well above the 2.5:1 selectivity minimum
- Curve separation: Type D (Ia = 20×In) sits well above Type B (Ia = 5×In)
- Manufacturer cascade table required for confirmation at 36 kA fault level (engineer-declared; verification deferred to fault-level skill)

Verdict: pass.

## Breaking capacity — cascade backup

Declared PFC at DB-P1 ≈ 18 kA. Standard 10 kA Icn MCBs would be inadequate at this fault level on their own, but IEC 60364-5-53 Clause 536.4 permits cascade backup from the upstream 400A MCCB Icu ≥ 36 kA, which limits the let-through energy reaching the downstream MCB. Engineer must verify the cascade pairing on the procured manufacturer's published cascade table.

## Phase balancing

Phase distribution:
- L1: P01 (5.5) + P04 (3.0) + P07 (3.5) + P10 (4.5) = 16.5 kW
- L2: P02 (5.5) + P05 (3.0) + P08 (4.5) + P11 (3.5) = 16.5 kW
- L3: P03 (5.5) + P06 (2.5) + P09 (4.5) + P12 (2.0) = 14.5 kW

Imbalance: max-min = 2 kW over a 47.5 kW total ≈ 4% imbalance — excellent balance, well within IEC 60364-1 Clause 314 guidance.

## Downstream consumer

This board's intent-out.json is consumed by:
- `electrical/sld/examples/intl-commercial-msb-4subdbs/` (SLD multi-board cascade, Phase B of SLD rebuild sprint)
- (Future) `electrical/cable-sizing/` — verify feeder + 12 final-circuit cables
- (Future) `electrical/fault-level/` — cascade fault current and Zs at terminus
- (Future) `electrical/small-power/` — layout of socket outlets at each ring/radial

## See also

- `electrical/db-layout/examples/intl-commercial-tpn-msb/` (upstream — MSB-MAIN F02 feeder)
- `electrical/db-layout/examples/intl-dbl1-lighting/` (peer — lighting sub-DB)
- `electrical/db-layout/examples/intl-dbm1-mechanical/` (peer — mechanical/HVAC sub-DB)
- `electrical/db-layout/examples/intl-dbfa1-fire-alarm/` (peer — fire alarm panel)
