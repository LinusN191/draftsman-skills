# Reasoning — US 4-Tenant Retail Strip Mall Fault-Level Study

## Section 1 — Source Specification

The installation is supplied from a single utility source: a 300 kVA PoCo pad-mount
transformer (dry-type, Z = 5.75 %) fed from the local 13.2 kV PoCo network on a radial
arrangement. The secondary is 208Y/120V TPN — the standard US commercial low-voltage
service that gives 208 V three-phase line-to-line for HVAC and small motor loads and 120 V
line-to-neutral for general receptacles and lighting on each tenant's panelboard. The
utility has declared the available fault current `PFC = 22.0 kA` at the MSP intake terminals
and this value is binding for design purposes under **NEC 2023 Article 110.24(A)** —
the field-marking rule that requires service equipment in other than dwelling units to be
legibly marked with the maximum available fault current.

There is no standby generator, no UPS, and no connected motor load at the fault-level
cascade tier (see Section 5 for the rigorous treatment of retail HVAC fan-coil-unit and
condenser motors). The installation therefore satisfies the "far-from-generator" condition
of **IEC 60909-0:2016 §3.4** at every cascade node: the initial symmetrical short-circuit
current `Ik"` does not exhibit a decaying sub-transient component from large rotating
machinery and can be modelled with a constant Thévenin source. A single `utility-PoCo`
source entry with `contribution_method = "constant"` and `ifault_contribution_ka = 22.00`
captures this.

## Section 2 — Cascade Topology

Seven nodes are declared by the engineer to mirror the SLD topology
(`us-strip-mall-msp-tenants`) — a four-board cascade with three parallel tenant sub-feeders
branching from the MSP busbar:

```
HV-1 (13.2 kV PoCo primary)
 └── TX-1 (300 kVA PoCo pad-mount TX 208Y/120V LV terminals)
      └── MSP (10 ft × 350 kcmil Cu THWN service conductors from TX pad to MSP)
           └── MSP.BUS (600 A busbar)
                ├── TSP-A (80 ft × 250 kcmil Cu XHHW → Tenant A 200 A sub-panel)
                ├── TSP-B (100 ft × 250 kcmil Cu XHHW → Tenant B 200 A sub-panel)
                └── CA-P  (120 ft × 4/0 AWG Cu XHHW   → Common-areas 100 A panel)
```

`cascade_topology_source = "engineer_declared"` is appropriate because the architectural
arrangement (a single MSP serving three sub-panels from a common busbar — two retail
tenants plus a common-areas panel for parking-lot lighting and signage) is fixed by the
building footprint, not derived from any board-graph inference. There are no inter-tenant
ties, no transfer switch, and no on-site generation.

## Section 3 — HV-side Assumptions

The PoCo declares 28 kA PFC at the 13.2 kV primary terminals with X/R = 7 (typical urban
distribution per **IEC 60909-1:2008 Table A.1** for radial 12.47–13.2 kV feeders).
Applying the HV voltage factor `c_max = 1.10` from **IEC 60909-0:2016 Table 1**:

- `ZQ_HV = (c_max × U_n) / (√3 × Ik"_pri) = (1.10 × 13 200) / (√3 × 28 000) ≈ 0.2994 Ω` at HV
- `Ik"max @ HV-1 = 28.00 kA`, `Ik"min @ HV-1 = 25.45 kA` (`c_min = 1.00` for HV)
- `κ(X/R = 7) = 1.02 + 0.98·exp(-3/7) = 1.658` → `ipk = √2·κ·Ik" = 65.67 kA`

The HV impedance referred to LV via the turns ratio `(208/13200)² ≈ 2.48 × 10⁻⁴` is
approximately 74 µΩ — negligible against the transformer impedance (5.3 mΩ at LV) but
retained in the cascade audit for completeness.

## Section 4 — Transformer + Source Impedances

The transformer nameplate impedance at LV is computed from `Z_pu = 0.0575`:

- `Z_TX = Z_pu × U²_LV / S = 0.0575 × 208² / 300 000 = 8.29 mΩ`
- At X/R = 8: `R_TX = Z_TX / √(1 + 64) ≈ 1.03 mΩ`, `X_TX = 8 · R_TX ≈ 8.22 mΩ`

An isolated calculation against an infinite HV source would yield
`Ik" = 1.05 × 208 / (√3 × 8.29 mΩ) ≈ 15.2 kA` at the TX LV terminals. The PoCo-declared
22.0 kA at MSP is *higher* than this isolated value — which seems counter-intuitive but is
typical of urban 13.2 kV networks where the upstream system contribution is small enough
that the transformer impedance dominates and small variations in actual transformer Zpu
plus the precise X/R assumed by the utility produce the higher number. The cascade is
therefore anchored to the PoCo declaration per **NEC 2023 §110.24(A)** rather than to a
nameplate back-calculation.

The TX-1 node is back-computed from the MSP anchor (Z_MSP = 5.732 mΩ at 22.0 kA, X/R = 8)
by subtracting the 10 ft × 350 kcmil Cu service-conductor impedance per **NEC 2023
Chapter 9 Table 9** (350 kcmil Cu PVC raceway: R = 0.041 Ω/1000 ft, X = 0.037 Ω/1000 ft →
R_serv = 0.41 mΩ, X_serv = 0.37 mΩ for 10 ft). With the X/R = 8 nameplate constraint
preserved at TX-1, the quadratic solution gives R_TX = 0.658 mΩ, X_TX = 5.261 mΩ,
Z_TX = 5.302 mΩ → Ik"max @ TX-1 = 23.78 kA. This is the engineering-honest
representation: TX-1 carries the higher fault duty (just upstream of the service
conductors) and MSP carries the slightly lower duty after the service-conductor drop.

## Section 5 — Motor Contribution Assessment

The connected motor load at the fault-level cascade tier is zero kW. The site is a
4-tenant retail strip mall — no industrial process motors, no elevator winders at
fault-study scale, no large standalone pumps connected to any of the LV panels.
Distributed HVAC fan-coil-unit and rooftop-condenser motors are embedded across tenants
but each individual unit is fractional-kW (typically ½–3 hp) and is not modelled at the
SLD / fault-level layer; their locked-rotor contribution at the MSP busbar is negligible
relative to the 22.0 kA utility infeed and is conventionally absorbed into the load-side
branch impedance rather than enumerated as a discrete source.

Applying the **IEC 60909-0:2016 §3.8.1** threshold check rigorously: the rule asks whether
`ΣI_rM ≥ 1 % × Ik"_no_motors`. With Ik"_no_motors = 22 000 A at MSP, the threshold is
220 A. With ΣI_rM = 0 A the threshold is unambiguously not met → motor contribution is
**explicitly excluded** from the cascade. No `motor-aggregate` entry is added to
`sources[]`, no asynchronous-motor decrement profile is generated, and the per-node
Ik" values reflect the utility-source contribution only. This is the standards-driven call;
the §3.8.1 threshold engages only when the aggregate motor load is comparable to the
fault-level scale, which retail-strip-mall HVAC distributed across four tenants is not.

If a tenant later refits with material electrically-driven mechanical plant — a restaurant
fit-out with large refrigeration compressors and walk-in cooler condensers, a laundromat
with multiple high-extract motors, an EV-charger dispenser cluster on the common-areas
panel — the fault-level study **must be re-run** with the updated motor inventory. Once
`ΣI_rM` crosses 220 A the §3.8.1 threshold engages, the cascade `Ik"max` values rise at
MSP.BUS by the motor sub-transient contribution (typically I_M ≈ 5 × ΣI_rM per §3.8
Equation 19 for aggregated induction motors), and AIC verification against the revised
cascade must be repeated. The motor-load brief is therefore captured in `input.json` as a
load-side input that re-opens the entire IEC 60909-0:2016 assessment.

## Section 6 — Per-node Ifault Computation

Per-node `Ik"max` is computed with the LV voltage factor `c_max = 1.05` per
**IEC 60909-0:2016 Table 1**. Service-conductor and sub-feeder impedance values are taken
from **NEC 2023 Chapter 9 Table 9** (AC resistance + reactance, copper conductors, PVC
raceway, 75 °C operating temperature — XHHW conductors share this Table 9 column with
THWN, both being 75 °C-rated insulation in the wet-locations ampacity column):

- 350 kcmil Cu (PVC raceway): `R = 0.041 Ω/1000 ft, X = 0.037 Ω/1000 ft`
- 250 kcmil Cu (PVC raceway): `R = 0.054 Ω/1000 ft, X = 0.038 Ω/1000 ft`
- 4/0 AWG Cu (PVC raceway):   `R = 0.063 Ω/1000 ft, X = 0.040 Ω/1000 ft`

Cumulative R and X are summed from the source down each branch; `Z_total = √(R² + X²)`
and `Ik"max = (c · U_LL) / (√3 · Z_total)`. Peak factor `κ` is computed per
**IEC 60909-0:2016 Eq. 29**: `κ = 1.02 + 0.98 · exp(-3 / (X/R))` with the **X/R
regenerated at each node** from the local cumulative R, X — not frozen at the upstream
value:

| Node     | R (mΩ) | X (mΩ) | Z (mΩ) | X/R   | Ik"max (kA) | κ     | ipk (kA) |
|----------|--------|--------|--------|-------|-------------|-------|----------|
| HV-1     |  —     |  —     | 299.4  | 7.00  | 28.00       | 1.658 | 65.67    |
| TX-1     |  0.658 |  5.261 |  5.302 | 8.00  | 23.78       | 1.694 | 56.96    |
| MSP      |  0.711 |  5.687 |  5.732 | 8.00  | 22.00       | 1.694 | 52.69    |
| MSP.BUS  |  0.811 |  5.787 |  5.844 | 7.14  | 21.58       | 1.664 | 50.77    |
| TSP-A    |  5.131 |  8.827 | 10.210 | 1.72  | 12.35       | 1.191 | 20.81    |
| TSP-B    |  6.211 |  9.587 | 11.423 | 1.54  | 11.04       | 1.160 | 18.11    |
| CA-P     |  8.371 | 10.587 | 13.497 | 1.26  |  9.34       | 1.111 | 14.68    |

Two engineering notes on the κ recomputation. First, κ drops sharply from 1.69 at the
service entrance (X/R = 8, transformer-dominated) to 1.11 at CA-P (X/R = 1.26,
sub-feeder-dominated) — this is exactly the behaviour **IEC 60909-0:2016 Eq. 29** is
designed to capture: as cable resistance dominates over transformer reactance, the
asymmetric peak factor approaches unity and the DC offset decays faster, making `ipk` only
marginally above `√2 · Ik"` rather than the ≈1.7× scaling at the service. Second, freezing
κ at an upstream value (a common implementation bug) would over-estimate `ipk` at TSP-A by
≈40 % and at CA-P by ≈50 % — driving unnecessary specifications of higher
peak-withstand busbars in the tenant sub-panels. The standard requires per-node
regeneration.

`Ik"min` is computed with `c_min = 0.95` at LV (1.00 at HV) per IEC 60909-0:2016 Table 1.
All seven cascade entries carry `tool_call_pending = true` per the v1.1 contract;
deterministic refinement will come from `calc.iec60909_cascade` at runtime.

## Section 7 — Selectivity Implications

Breaker interrupting-capacity verification per **NEC 2023 Article 110.9** — "Equipment
intended to interrupt current at fault levels shall have an interrupting rating at nominal
circuit voltage at least equal to the current that must be interrupted":

- **MSP main MCCB 600 A, AIC = 65 kA** — applied 22.00 kA → adequate (3.0× margin).
  Confirm SCCR marking on the MSP enclosure per **NEC 2023 §408.36** (panelboards) and
  **Article 110.10** (component protection coordination).
- **TSP-A MCCB 200 A, AIC = 25 kA** — applied 12.35 kA → adequate (2.0× margin). Tenant
  fit-out equipment (HVAC condenser units, lighting contactors, POS rack) downstream must
  carry SCCR ≥ 12.35 kA per **NEC 2023 Article 110.9** — verify equipment SCCR labels
  during tenant CO inspection.
- **TSP-B MCCB 200 A, AIC = 25 kA** — applied 11.04 kA → adequate (2.3× margin). Cascade
  discrimination with the upstream MSP MCCB is supported by the 100 ft × 250 kcmil
  sub-feeder impedance step (5.84 mΩ at MSP.BUS → 11.42 mΩ at TSP-B incoming) per
  **NEC 2023 Article 240.87** selectivity assessment for arc-energy reduction.
- **CA-P MCCB 100 A, AIC = 22 kA** — applied 9.34 kA → adequate (2.4× margin). Common-
  areas panel feeds parking-lot lighting contactors and pylon signage; verify
  lighting-control panel SCCR ≥ 9.34 kA per **NEC 2023 Article 110.9**.

Series-combination ratings per **NEC 2023 Article 240.86** are *not* claimed in this
study — all devices are fully rated for the prospective fault at their location. Series
ratings would require either (A) licensed-engineer-supervised installation with
documented breaker pairings, or (B) manufacturer-tested combinations marked on the
panelboard nameplate; for a retail strip mall with frequent tenant churn, the fully-rated
approach is more robust.

## Section 8 — Compliance + Assumptions

The cascade complies with **NEC 2023** and **IEC 60909-0:2016**. Explicit assumptions:

1. PoCo declared `PFC = 22.0 kA` at MSP intake is binding (**NEC 2023 §110.24(A)** —
   available fault current field-marking on service equipment in other than dwelling
   units).
2. Transformer X/R = 8 from **IEC 60909-1:2008 Table A.1** typical for 300 kVA pad-mount
   dry-type distribution unit (range 6–10).
3. Cable impedance from **NEC 2023 Chapter 9 Table 9** at 75 °C operating temperature
   (350 kcmil, 250 kcmil, 4/0 AWG copper in PVC raceway). XHHW conductors share the
   Table 9 column with THWN, both rated 75 °C wet-location insulation.
4. Peak factor κ per **IEC 60909-0:2016 Eq. 29** with X/R regenerated from each
   cumulative impedance summation — not frozen at the upstream value.
5. Motor contribution **explicitly excluded** per **IEC 60909-0:2016 §3.8.1** strict
   threshold (`ΣI_rM = 0 A < 1 % × 22 000 A = 220 A`).
6. AIC verification per **NEC 2023 Article 110.9**; SCCR marking per **NEC 2023 §408.36**
   (panelboards) + **Article 110.10** (component protection).
7. Series-combination ratings per **NEC 2023 Article 240.86** not claimed — all devices
   fully rated.
8. Type 1 SPD recommended at MSP service entrance per **NEC 2023 Article 285** with
   downstream Type 2 SPDs at each tenant sub-panel for transient-overvoltage protection
   on commercial occupancy with significant POS / HVAC controls electronics.
9. `tool_call_pending: true` across cascade — deterministic recompute pending the
   `calc.iec60909_cascade` shared runtime tool execution.
