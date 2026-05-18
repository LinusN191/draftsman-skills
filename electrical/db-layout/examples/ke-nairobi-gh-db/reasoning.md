# Reasoning — KE Nairobi Gate-House Sub-DB (GH-DB)

## Site context

Gate-house perimeter cabin for the Nairobi industrial light-engineering workshop. Small cabin (~6m²) housing one security guard at any time, supporting external floodlights, a single-bay sockets outlet, and a CCTV/intercom comms outlet. The cabin sits ~60m from the main switchroom; the supply is taken as a submain off MSP-100 C08 (the existing KE main switchboard example), not as a separate KPLC intake — KPLC site wayleave is a single intake at the main building.

## Board sizing — single-phase 40A intake

Connected load: 0.6 kW (lighting) + 1.5 kW (sockets) + 0.2 kW (CCTV/intercom) ≈ 2.3 kW. Design current = 2,300 / 240 ≈ 10A. After applying KS 1700 Annex C diversity (gate-house = full demand, no diversification): ~10A. 40A intake leaves ~75% headroom — generous, but matches the upstream MSP-100 C08 breaker rating directly so the submain conductor is sized once for the full breaker rating.

Single-phase 240V intake selected because:
- Total gate-house load is small (<3 kW), well within single-phase capacity
- Single-phase simplifies isolation (one switch-disconnector vs three-pole)
- Minimises neutral imbalance contribution at MSP-100 (gate house is on one phase only)
- Easier diagnostic when only L1 is involved at the gate house

## RCD strategy — KS 1700:2018 §411.3.3

KS 1700:2018 §411.3.3 (KE adoption of BS 7671 universal-socket-RCD principle) requires 30mA Type A RCD on all socket-bearing final circuits. Applied here:

- **C02 — sockets:** 30mA Type A RCD. Type A handles pulsating DC residual currents from any switched-mode electronics a guard might plug in (phone charger, kettle controller, fan).
- **C03 — CCTV/intercom comms outlet:** 30mA Type A RCD. While not a 13A socket per the strict reading, the comms outlet supplies SMPS-fed CCTV camera + intercom — earth-leakage exposure is meaningful and a 30mA RCD adds protection at trivial cost.
- **C01 — lighting:** No RCD. KS 1700 §411.3.3 socket-exemption applies only to socket circuits; lighting is fixed-equipment and RCD is not mandatory. (External floodlight luminaires use IP65 fittings with Class II construction, so additional RCD risk is low.)

## Upstream RCD coordination — series 30mA pair

The upstream MSP-100 C08 (40A MCB Type B with 30mA Type A RCD) is in series with the downstream C02 and C03 30mA Type A RCDs at GH-DB. **This pairing is not selectively coordinated** — series 30mA RCDs are time-coincident and an earth fault on C02 will trip both the local and upstream RCD per KS 1700 §314. Engineering decision: accept the non-selective pair because the entire upstream C08 feeder serves only the gate house — there is no other downstream load that needs to remain energised when GH-DB trips on an earth fault. A staged selectivity arrangement (100mA Type S upstream + 30mA Type A downstream) is the alternative and noted in `selectivity_results.verdict = "pass_with_rcd_caution"`.

## MCB curve selection

All circuits use Type B (Ia = 5×In) — appropriate for resistive/light-electronic loads (LED floodlights, small office sockets, low-power CCTV SMPS). No motor circuits at the gate house, so Type C/D are not justified.

## Breaking capacity at gate house

Declared PFC at MSP-100 = 9.8 kA. Submain impedance over 60m of 10mm² 4-core SWA PVC Cu is approximately:
- R (60m × 0.00183 Ω/m at 70°C) ≈ 0.11 Ω per phase loop = ~0.22 Ω L-N loop
- Available PFC at GH-DB ≈ 240 / 0.22 ≈ 1.1 kA (worst case, L-N fault at termination)

Allowing for arc impedance reduction in upstream cable: practical PFC at GH-DB ≈ 3.0 kA. 6 kA Icn MCBs (BS EN 60898 economy range) provide 100% headroom — comfortable margin for a domestic-style sub-DB.

## Standards routing — KS 1700:2018 + KS Annex E

This example uses native KS citation form (`KS 1700:2018 §411.3.3`) rather than the legacy "BS 7671 ... (adopted by KS 1700)" annotation. KS 1700:2018 Annex E adopts the BS Table 41.2 maximum-disconnection-time table verbatim and the BS EN 61439-3 distribution-board assembly standard verbatim. Engineers reading this output should treat KS 1700 as the primary reference, with BS table content reachable via the Annex E adoption.

## Downstream consumer

This board's intent-out.json is consumed by:
- `electrical/sld/examples/ke-nairobi-industrial-msb-gh/` (SLD multi-board cascade, generated in Phase B of the SLD rebuild sprint)
- (Future) `electrical/cable-sizing/` — verify the 60m submain + 3 final-circuit cables against KS 1700 / BS 7671 Appendix 4
- (Future) `electrical/fault-level/` — Zs verification at each final-circuit terminus, including the long submain feeder
- (Future) `electrical/earthing/` — site earthing arrangement and gate-house equipotential bonding

## See also

- `electrical/db-layout/examples/ke-nairobi-industrial-100A-tpn/` (upstream — MSP-100 main switchboard, C08 is the submain feeder to GH-DB)
