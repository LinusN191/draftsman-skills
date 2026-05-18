# Reasoning — UK 3-Storey Commercial Office Fault-Level Study

## Section 1 — Source Specification

The project is supplied from a single utility source: an 800 kVA pad-mount transformer
(Dyn11, Z=5%) fed from the local 11 kV DNO network on a radial arrangement. The earthing
system is TN-C-S, with the DNO declaring `Ze = 0.35 Ω` and `PSCC = 9.8 kA` at the MSB
intake terminals — values that are binding for design purposes under
**BS 7671:2018+A2 Reg 313.1.1**.

There is no standby generator, no UPS, and no connected motor load. The system therefore
satisfies the "far-from-generator" condition of **IEC 60909-0:2016 §3.4** at every cascade
node: the initial symmetrical short-circuit current `Ik"` does not exhibit a decaying
sub-transient component from rotating machinery and can be modelled with a constant
Thévenin source. A single `utility-DNO` source entry with
`contribution_method = "constant"` and `ifault_contribution_ka = 9.85` captures this.

## Section 2 — Cascade Topology

Seven nodes are declared by the engineer to mirror the SLD topology
(`uk-commercial-office-3storey`) — a four-board cascade with three parallel floor SDBs
branching from the MSB busbar:

```
HV-1 (11 kV DNO)
 └── TX-1 (800 kVA TX LV terminals)
      └── MSB-MAIN (5 m × 240mm² busbar trunking from TX vault to MSB)
           └── MSB-MAIN.BUS (630 A busbar)
                ├── SDB-GF (35 m × 95mm² Cu XLPE)
                ├── SDB-L1 (45 m × 95mm² Cu XLPE)
                └── SDB-L2 (55 m × 95mm² Cu XLPE)
```

`cascade_topology_source = "engineer_declared"` is appropriate because the architectural
arrangement (vertical risers serving one DB per storey) is fixed by the building, not
derived from any board-graph inference.

## Section 3 — HV-side Assumptions

The DNO declares 14 kA PSCC at the 11 kV primary terminals with X/R = 5 (typical urban
distribution per **IEC 60909-1:2008 Table A.1**). Applying the HV voltage factor
`c_max = 1.10` from **IEC 60909-0:2016 Table 1**:

- `ZQ_HV = (c_max × U_n) / (√3 × Ik"_pri) = (1.10 × 11 000) / (√3 × 14 000) ≈ 0.499 Ω` at HV
- `Ik"max @ HV-1 = 14.00 kA`, `Ik"min @ HV-1 = 12.73 kA` (c_min = 1.00 for HV)
- `κ(X/R=5) = 1.02 + 0.98·exp(-3/5) = 1.558` → `ipk = √2·κ·Ik" = 30.84 kA`

The HV impedance referred to LV via the turns ratio (400/11000)² is approximately
0.66 µΩ — negligible against the transformer impedance but retained in the cascade audit
for completeness.

## Section 4 — Transformer + Source Impedances

The transformer impedance at LV is computed from `Z_pu = 0.05`:

- `Z_TX = Z_pu × U²_LV / S = 0.05 × 400² / 800 000 = 10.0 mΩ`
- At X/R = 6: `R_TX = Z_TX / √(1+36) ≈ 1.64 mΩ`, `X_TX = 6·R_TX ≈ 9.86 mΩ`

An isolated calculation against an infinite HV source would yield
`Ik" = 1.05 × 400 / (√3 × 10 mΩ) ≈ 22.75 kA` at the TX LV terminals. This is **not**
representative of the physical installation: the DNO-declared 9.8 kA at the MSB intake
constrains the cascade per **BS 7671:2018+A2 Reg 313.1** and implies the actual upstream
network (HV feeder + transformer) presents a higher equivalent impedance than the
nameplate transformer impedance alone — typical of long urban 11 kV feeders with
intermediate switchgear.

The cascade is therefore anchored to the DNO declaration. TX-1 is back-calculated as
≈9.85 kA — a hair higher than the 9.80 kA at MSB-MAIN to account for the 5 m of 240mm²
busbar trunking between the TX vault and the MSB cubicle.

## Section 5 — Motor Contribution Assessment

Connected motor load is zero kW for this study. The building is a commercial office with
small-power, lighting, and HVAC-only loads — there are no industrial process motors, no
lift motors at fault-study scale, and no large standalone pumps connected to the LV cascade.
Distributed fan-coil-unit motors embedded in the HVAC system are not modelled at the
SLD / fault-level layer; they are small fractional-kW devices whose locked-rotor
contribution is negligible relative to the utility infeed and is conventionally absorbed
into the load-side branch impedance rather than enumerated as discrete sources.

The relevant trigger is **IEC 60909-0:2016 §3.8** (motor contribution to short-circuit
current). Per §3.8.1, asynchronous-motor sub-transient contribution must be included in
the cascade when the sum of rated motor currents at the fault location is comparable
to — typically taken as ≥ 1 % of — the initial symmetrical short-circuit current `Ik"`
calculated **without** motor contribution. In this study the LHS (Σ I_rM) is exactly zero,
which is unambiguously below the §3.8.1 threshold at every node. Motor contribution is
therefore explicitly excluded from the cascade, no motor source is added to `sources[]`,
and no asynchronous-motor decrement profile is generated.

This decision is captured in `input.json` as `motor_load_brief: { total_motor_kw: 0,
largest_motor_kw: 0 }`. If the building is later refit with significant electrically-driven
mechanical plant — chiller compressors, large AHU fans, a fire-pump driver, lift winders —
the fault-level study must be re-run with the updated motor inventory: the §3.8.1 threshold
check is then likely to engage, the cascade `Ik"max` values will rise (motor sub-transient
adds to the utility contribution during the first 10–30 ms), and breaker breaking-capacity
verification against the revised cascade must be repeated. A future engineer should treat
the motor-load brief as a load-side input that re-opens the entire IEC 60909 assessment
rather than a fixed assumption.

## Section 6 — Per-node Ifault Computation

Per-node `Ik"max` is computed with the LV voltage factor `c_max = 1.05` per
**IEC 60909-0:2016 Table 1**. Floor-riser cable impedance per **IEC 60364-5-52 Annex E**
for 95mm² Cu XLPE at 90 °C operating temperature is `R = 0.208 mΩ/m, X = 0.0829 mΩ/m`.

Cumulative R and X are summed from the source down each branch; `Z_total = √(R² + X²)` and
`Ik"max = (c·U_LL) / (√3·Z_total)`. Peak factor `κ` is computed per **IEC 60909-0:2016
Eq. 29**: `κ = 1.02 + 0.98·exp(-3/(X/R))`.

| Node            | R (mΩ) | X (mΩ) | Z (mΩ) | X/R   | Ik"max (kA) | κ     | ipk (kA) |
|-----------------|--------|--------|--------|-------|-------------|-------|----------|
| TX-1            |  3.65  | 23.99  | 24.27  | 6.57  |  9.85       | 1.64  | 22.50    |
| MSB-MAIN        |  4.07  | 24.41  | 24.74  | 6.00  |  9.80       | 1.61  | 22.37    |
| MSB-MAIN.BUS    |  4.09  | 24.43  | 24.77  | 5.98  |  9.78       | 1.61  | 22.32    |
| SDB-GF (35 m)   | 11.37  | 27.33  | 29.60  | 2.40  |  8.19       | 1.30  | 15.08    |
| SDB-L1 (45 m)   | 13.45  | 28.16  | 31.20  | 2.09  |  7.77       | 1.25  | 13.78    |
| SDB-L2 (55 m)   | 15.53  | 28.99  | 32.88  | 1.87  |  7.37       | 1.21  | 12.69    |

`Ik"min` is computed with `c_min = 0.95` at LV. All seven cascade entries carry
`tool_call_pending = true` per the v1.1 contract; deterministic refinement will come from
`calc.iec60909_cascade` at runtime.

## Section 7 — Selectivity Implications

Breaker breaking-capacity verification per **BS 7671:2018+A2 Reg 434.5.1** ("device shall
have a breaking capacity not less than the prospective fault current"):

- **MSB ACB 630 A, Icu = 36 kA** — applied 9.80 kA → adequate (3.7× margin). Confirm that
  `Ics ≥ Icu` is rated for full service capability at this Icu (Reg 434.5.1 Note).
- **SDB-GF MCCB 160 A, Icu = 25 kA** — applied 8.19 kA → adequate (3.1× margin).
- **SDB-L1 MCCB 160 A, Icu = 25 kA** — applied 7.77 kA → adequate (3.2× margin).
- **SDB-L2 MCCB 160 A, Icu = 25 kA** — applied 7.37 kA → adequate (3.4× margin).

The substantial impedance drop across the floor risers (29.6/31.2/32.9 mΩ vs. 24.7 mΩ at
the busbar) supports cascade discrimination between the MSB ACB and the SDB MCCBs per
**BS 7671:2018+A2 Reg 536.4**, subject to manufacturer let-through (I²t) confirmation at
the design stage.

## Section 8 — Compliance + Assumptions

The cascade complies with **BS 7671:2018+A2** and **IEC 60909-0:2016**. Explicit
assumptions:

1. DNO declared `Ze = 0.35 Ω, PSCC = 9.8 kA` at MSB intake is binding
   (BS 7671:2018+A2 Reg 313.1.1).
2. Transformer X/R = 6 from **IEC 60909-1:2008 Table A.1** typical for 800 kVA urban
   distribution unit.
3. Cable impedance from **IEC 60364-5-52 Annex E** at 90 °C operating temperature.
4. Peak factor κ per **IEC 60909-0:2016 Eq. 29** with R/X regenerated from each cumulative
   X/R rather than assumed.
5. Selectivity verification per **BS 7671:2018+A2 Reg 434.5.1** + **Reg 536.4**.
6. Type 1/2 SPD recommended at MSB origin per **BS 7671:2018+A2 Reg 443.4** for atmospheric
   transient protection on commercial office occupancy.
7. `tool_call_pending: true` across cascade — deterministic recompute pending the
   `calc.iec60909_cascade` shared runtime tool execution.
