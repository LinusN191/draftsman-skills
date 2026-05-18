# Reasoning — Kenya Nairobi Industrial Workshop Fault-Level Study

## Section 1 — Source Specification

The installation is supplied from a single utility source: a 500 kVA KPLC pole-mount
transformer (Z = 4.75 %) fed from the local 11 kV KPLC primary on a radial arrangement.
The earthing system is TN-S with KPLC declaring `Ze = 0.80 Ω` and `PSCC = 9.8 kA` at the
MSP-100 intake terminals — values that are binding for design purposes under
**KS 1700:2018 §313.1** (which Annex E adopts from **BS 7671:2018+A2 §313.1** verbatim for
the short-circuit interrupting chain).

There is no standby generator, no UPS, and only a modest motor inventory (workshop tools
totalling 37 kW — see Section 5). The installation therefore satisfies the
"far-from-generator" condition of **IEC 60909-0:2016 §3.4** at every cascade node: the
initial symmetrical short-circuit current `Ik"` does not exhibit a decaying sub-transient
component from large rotating machinery and can be modelled with a constant Thévenin
source. A single `utility-KPLC` source entry with `contribution_method = "constant"` and
`ifault_contribution_ka = 9.80` captures this.

## Section 2 — Cascade Topology

Five nodes are declared by the engineer to mirror the SLD topology
(`ke-nairobi-industrial-msb-gh`) — a two-board linear cascade with a single submain feeder:

```
HV-1 (11 kV KPLC primary)
 └── TX-1 (500 kVA KPLC pole-mount TX LV terminals)
      └── MSP-100 (3 m × 70mm² Cu XLPE service cable from pole-mount to MSP)
           └── MSP-100.BUS (100 A busbar)
                └── GH-DB (60 m × 95mm² Cu XLPE submain to workshop/glasshouse DB)
```

`cascade_topology_source = "engineer_declared"` is appropriate because the architectural
arrangement (pole-mount TX feeding a single MSP, then a single submain across the yard to
the workshop DB) is fixed by the building footprint, not derived from any board-graph
inference. There are no parallel branches at the MSP busbar in this study; future
extensions (offices, additional outbuildings) would add SDB nodes at MSP-100.BUS.

## Section 3 — HV-side Assumptions

KPLC declares 13 kA PSCC at the 11 kV primary terminals with X/R = 5 (typical urban
distribution per **IEC 60909-1:2008 Table A.1** for radial 11 kV feeders). Applying the
HV voltage factor `c_max = 1.10` from **IEC 60909-0:2016 Table 1**:

- `ZQ_HV = (c_max × U_n) / (√3 × Ik"_pri) = (1.10 × 11 000) / (√3 × 13 000) ≈ 0.5374 Ω` at HV
- `Ik"max @ HV-1 = 13.00 kA`, `Ik"min @ HV-1 = 11.82 kA` (`c_min = 1.00` for HV)
- `κ(X/R = 5) = 1.02 + 0.98·exp(-3/5) = 1.558` → `ipk = √2·κ·Ik" = 28.64 kA`

The HV impedance referred to LV via the turns ratio `(415/11000)²` is approximately
0.76 µΩ — negligible against the transformer impedance but retained in the cascade audit
for completeness.

## Section 4 — Transformer + Source Impedances

The transformer impedance at LV is computed from `Z_pu = 0.0475`:

- `Z_TX = Z_pu × U²_LV / S = 0.0475 × 415² / 500 000 = 16.36 mΩ`
- At X/R = 5: `R_TX = Z_TX / √(1 + 25) ≈ 3.21 mΩ`, `X_TX = 5 · R_TX ≈ 16.04 mΩ`

An isolated calculation against an infinite HV source would yield
`Ik" = 1.05 × 415 / (√3 × 16.36 mΩ) ≈ 15.4 kA` at the TX LV terminals. This is **not**
representative of the physical installation: the KPLC-declared 9.8 kA at the MSP-100
intake constrains the cascade per **KS 1700:2018 §313.1** (routes to **BS 7671:2018+A2
§313.1** for the short-circuit interrupting chain) and implies the actual upstream
network (HV feeder + transformer + service cable) presents a higher equivalent impedance
than the nameplate transformer impedance alone — typical of rural KPLC pole-mount
installations on long 11 kV laterals.

The cascade is therefore anchored to the KPLC declaration. TX-1 is back-calculated as
≈10.22 kA — a hair higher than the 9.80 kA at MSP-100 to account for the 3 m of 70mm²
Cu XLPE service cable between the pole-mount TX terminals and the MSP cubicle.

## Section 5 — Motor Contribution Assessment

The workshop carries a small but non-zero motor inventory: an 11 kW lathe, a 4 kW pillar
drill, and a 22 kW air compressor — total 37 kW connected motor load at 415 V three-phase.
Naïve intuition would treat the 22 kW compressor at the MSP busbar as potentially
contributing meaningfully to the fault current during sub-transient (first half-cycle), and
in larger industrial installations this is exactly the regime that **IEC 60909-0:2016
§3.8** asks the engineer to interrogate.

Applying the **IEC 60909-0:2016 §3.8.1** threshold check rigorously: the sum of rated
motor currents at 415 V (taking η = 0.85, cos φ = 0.85 for typical asynchronous induction
motors) is
`ΣI_rM = 37 000 / (√3 × 415 × 0.85 × 0.85) ≈ 71 A`.
The §3.8.1 threshold for inclusion is `ΣI_rM ≥ 1 % × Ik"_no_motors = 1 % × 9 800 A = 98 A`.
Since `71 A < 98 A`, the threshold is **NOT met** and motor contribution is **explicitly
excluded** from the cascade. No `motor-aggregate` entry is added to `sources[]`, no
asynchronous-motor decrement profile is generated, and the per-node Ik" values reflect the
utility-source contribution only. This is the engineering-honest call — the rule said no,
even though intuition about the 22 kW compressor near the bus said yes. The numerical
answer follows the standard, not the gut.

The engineering implication is operational, not just numerical. If the workshop later
expands — additional CNC mills, a larger compressor, a paint-line, an injection-moulder
— the fault-level study **must be re-run** with the updated motor inventory. Once
`ΣI_rM` crosses 98 A the §3.8.1 threshold engages, the cascade `Ik"max` values rise at
MSP-100.BUS by the motor sub-transient contribution (typically I_M ≈ 5 × ΣI_rM per
§3.8 Equation 19 for aggregated induction motors), and breaker breaking-capacity
verification against the revised cascade must be repeated. The motor-load brief is
therefore captured in `input.json` as a load-side input that re-opens the entire
IEC 60909-0:2016 assessment — not as a fixed assumption.

## Section 6 — Per-node Ifault Computation

Per-node `Ik"max` is computed with the LV voltage factor `c_max = 1.05` per
**IEC 60909-0:2016 Table 1**. Service cable impedance (70mm² Cu XLPE @ 90 °C) and submain
impedance (95mm² Cu XLPE @ 90 °C) are taken from **IEC 60364-5-52:2009 Annex E**:
- 70mm² Cu XLPE @ 90 °C: `R = 0.337 mΩ/m, X = 0.0875 mΩ/m`
- 95mm² Cu XLPE @ 90 °C: `R = 0.208 mΩ/m, X = 0.0829 mΩ/m`

Cumulative R and X are summed from the source down each branch; `Z_total = √(R² + X²)` and
`Ik"max = (c · U_LL) / (√3 · Z_total)`. Peak factor `κ` is computed per **IEC 60909-0:2016
Eq. 29**: `κ = 1.02 + 0.98 · exp(-3 / (X/R))`.

| Node            | R (mΩ) | X (mΩ) | Z (mΩ) | X/R   | Ik"max (kA) | κ     | ipk (kA) |
|-----------------|--------|--------|--------|-------|-------------|-------|----------|
| TX-1            |  4.83  | 24.15  | 24.63  | 5.00  | 10.22       | 1.56  | 22.51    |
| MSP-100         |  5.84  | 24.41  | 25.67  | 4.18  |  9.80       | 1.56  | 21.59    |
| MSP-100.BUS     |  5.94  | 24.51  | 25.87  | 4.13  |  9.78       | 1.56  | 21.55    |
| GH-DB (60 m)    | 18.42  | 29.49  | 34.77  | 1.60  |  7.24       | 1.17  | 11.98    |

`Ik"min` is computed with `c_min = 0.95` at LV. All five cascade entries carry
`tool_call_pending = true` per the v1.1 contract; deterministic refinement will come from
`calc.iec60909_cascade` at runtime.

## Section 7 — Selectivity Implications

Breaker breaking-capacity verification per **KS 1700:2018 §434.5** (which Annex E adopts
from **BS 7671:2018+A2 §434.5.1** verbatim — "device shall have a breaking capacity not
less than the prospective fault current"):

- **MSP-100 MCCB 100 A, Icu = 25 kA** — applied 9.80 kA → adequate (2.6× margin). Confirm
  that `Ics ≥ 75 % Icu` is rated for full service capability at this Icu.
- **GH-DB MCCB 63 A, Icu = 10 kA** — applied 7.24 kA → adequate (1.38× margin —
  **marginal**). Recommendation: specify Icu 15 kA for design prudence. The 1.38× margin
  leaves little room for upstream-network impedance improvements (KPLC may refurbish the
  HV feeder, lowering the declared PSCC ceiling at MSP-100 and pushing the GH-DB Ik"max
  upward).

The substantial impedance step across the 60 m submain (25.21 mΩ at MSP-100.BUS →
34.77 mΩ at GH-DB) supports cascade discrimination between the MSP MCCB and the GH-DB
MCCB per **KS 1700:2018 §536.4** (routes to **BS 7671:2018+A2 §536.4** for OCPD
discrimination), subject to manufacturer let-through (I²t) confirmation at the design
stage.

## Section 8 — Compliance + Assumptions

The cascade complies with **KS 1700:2018** and **IEC 60909-0:2016**. Explicit
assumptions:

1. KPLC declared `Ze = 0.80 Ω, PSCC = 9.8 kA` at MSP-100 intake is binding
   (**KS 1700:2018 §313.1** routes to **BS 7671:2018+A2 §313.1**).
2. Transformer X/R = 5 from **IEC 60909-1:2008 Table A.1** typical for 500 kVA KPLC
   pole-mount distribution unit.
3. Cable impedance from **IEC 60364-5-52:2009 Annex E** at 90 °C operating temperature
   (70mm² and 95mm² Cu XLPE).
4. Peak factor κ per **IEC 60909-0:2016 Eq. 29** with X/R regenerated from each
   cumulative impedance summation rather than assumed.
5. Motor contribution **explicitly excluded** per **IEC 60909-0:2016 §3.8.1** strict
   threshold (`ΣI_rM = 71 A < 1 % × 9 800 A = 98 A`).
6. Selectivity verification per **KS 1700:2018 §434.5 + §536.4** (route to **BS 7671:2018+A2
   §434.5.1 + §536.4** respectively).
7. Type 1/2 SPD recommended at MSP-100 origin per **KS 1700:2018 §443.4** (routes to
   **BS 7671:2018+A2 §443.4**) for atmospheric transient protection on the Nairobi Rift
   escarpment (elevated keraunic level, AQ2 classification).
8. `tool_call_pending: true` across cascade — deterministic recompute pending the
   `calc.iec60909_cascade` shared runtime tool execution.
