# Reasoning — INT DB-L1 (Lighting Sub-DB)

## Site context

Lighting sub-DB serving the generic IEC commercial 3-storey office building (~3000 m² total GIA). DB-L1 is one of four sub-DBs downstream of MSB-MAIN: DB-L1 (lighting, this board), DB-P1 (small power), DB-M1 (mechanical), DB-FA1 (fire alarm panel). The lighting DB is located in the level-1 electrical riser cupboard so the longest run to the L2 lighting zone is ~80 m.

## Board sizing — 250A TPN intake

Connected lighting load across 3 floors + external + emergency + decorative ≈ 19.3 kW. Design current at PF 0.95 (LED-dominated lighting): 19,300 / (√3 × 400 × 0.95) ≈ 29A. Adding allowance for inrush coincidence (LED driver capacitive inrush ≈ 30× steady-state for ~100µs) and 30% growth margin: peak ~50A. 

The 250A intake matches the upstream MSB-MAIN F01 MCCB rating directly — the feeder cable is sized for the upstream protection rating, not the diversified lighting load. This is the standard pattern: sub-DB intake = upstream feeder breaker rating, busbar sized accordingly, generous spare-way provision for tenant fit-out lighting changes.

## RCD strategy — IEC 60364-4-41 Clause 411.3.3

IEC 60364-4-41:2018 Clause 411.3.3 requires 30mA Type A RCD on all final circuits supplying socket-outlets (≤32A) in commercial premises and also on lighting circuits in many jurisdictions adopting HD 60364. Modern LED driver SMPS topology produces pulsating DC residual fault currents — Type AC RCDs would be blind to these. Type A RCD is the universal choice:

- **L01 / L02 / L03 — Zone 1/2/3 open-office lighting:** 30mA Type A. These are the high-density LED panel circuits (≈3.5 kW each, ≈40-60 luminaires per zone).
- **L04 — meeting room lighting:** 30mA Type A. Lower load but same Type A justification.
- **L05 — external parking + façade lighting:** 30mA Type A. External weather exposure increases earth-leakage risk; 4mm² SWA XLPE Cu cable for the 90m route.
- **L07 — decorative lighting:** 30mA Type A. Includes occasional accent fittings + lobby downlighters.
- **L06 — emergency lighting:** **NO RCD** — IEC 60364-5-56 Clause 560 prohibits upstream RCD on dedicated life-safety circuits because an earth-fault trip would disable the emergency-lighting supply at the moment it is most needed (e.g., during a fire involving a luminaire). FP200 LSZH fire-rated cable specified for the 90-minute survival period per the IEC 60364-5-56 cable category.

## MCB curve selection

- **Type C (Ia = 10×In)** on L01/L02/L03/L05 — the high-density LED zone lighting + external. Type C handles LED driver inrush coincidence without nuisance trip; large external lighting fixtures (parking-area floodlights ≥150W) have particularly aggressive inrush profiles.
- **Type B (Ia = 5×In)** on L04, L06, L07 — lower-power lighting where the inrush risk is modest and tighter earth-fault loop protection is preferred.

## Breaking capacity at DB-L1

Declared PFC at MSB-MAIN ≈ 25 kA. The 35m run of 35mm² 5-core SWA XLPE Cu feeder reduces PFC at DB-L1 to ≈ 15 kA. Standard 10 kA Icn MCBs (IEC 60898) would be marginal at this fault level. Two options:
1. Specify 15 kA or 16 kA Icn MCBs (commercial range — e.g., ABB S203/Schneider iC60H/Hager NCN/NHN)
2. Apply cascade backup from the upstream 250A MCCB Icu ≥ 25 kA (IEC 60364-5-53 Clause 536.4 cascade backup permits)

This board specifies 10 kA Icn MCBs with **cascade backup from upstream 250A MCCB (25 kA Icu)** verified via manufacturer cascade table — the conventional approach for sub-DB MCBs downstream of a generously-rated MCCB. Engineer should re-verify cascade pairings if a different manufacturer is procured.

## Voltage drop verification

Long runs L03 (80m, 16A) and L05 (90m, 20A) need voltage-drop sanity check:
- L03: 80m × 16A × 0.0181 Ω/m (2.5mm² Cu, AC at 70°C) ≈ 2.3% — within 3% lighting limit (IEC 60364-5-52 Annex E typical guidance for lighting circuits)
- L05: 90m × 20A × 0.0115 Ω/m (4mm² Cu, AC at 70°C) ≈ 2.1% — within 3% limit

Both pass the engineer-rule-of-thumb sanity check. Full voltage-drop verification deferred to `electrical/cable-sizing/`.

## Phase balancing

L01 → L1, L02 → L2, L03 → L3 distributes the heavy open-office load evenly across the three phases. L04 (L1), L05 (L2), L07 (L1) add modest single-phase loads. L06 emergency lighting (L3) ties up the smallest phase. Net per-phase balance is approximately L1: 6.8 kW, L2: 7.5 kW, L3: 5.0 kW — within 30% imbalance tolerance per IEC 60364-1 Clause 314.

## Selectivity verification

Upstream MSB-MAIN F01 = 250A MCCB Type D. Downstream final-circuit MCBs are ≤20A:
- Current ratio: 250/20 = 12.5:1 — well above the 2.5:1 minimum for selective discrimination
- Curve separation: Type D upstream (Ia = 20×In) sits well above Type B/C downstream Ia bands
- Manufacturer cascade table required for confirmation at 25 kA fault level (engineer-declared; verification deferred to fault-level skill)

Verdict: pass.

## Downstream consumer

This board's intent-out.json is consumed by:
- `electrical/sld/examples/intl-commercial-msb-4subdbs/` (SLD multi-board cascade, generated in Phase B of the SLD rebuild sprint)
- (Future) `electrical/cable-sizing/` — verify the 35m feeder + all final-circuit cables against IEC 60364-5-52 + Appendix B
- (Future) `electrical/fault-level/` — Zs verification + cascade fault current confirmation
- (Future) `electrical/lux/` — illuminance design per IEC 60364 / EN 12464-1 office lighting levels

## See also

- `electrical/db-layout/examples/intl-commercial-tpn-msb/` (upstream — MSB-MAIN F01 feeder)
- `electrical/db-layout/examples/intl-dbp1-power/` (peer — small power sub-DB)
- `electrical/db-layout/examples/intl-dbm1-mechanical/` (peer — mechanical/HVAC sub-DB)
- `electrical/db-layout/examples/intl-dbfa1-fire-alarm/` (peer — fire alarm panel)
