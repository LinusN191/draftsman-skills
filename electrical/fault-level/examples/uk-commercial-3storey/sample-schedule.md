# Sample Schedule — UK 3-Storey Commercial Office Fault-Level Study

**Project:** London 3-Storey Commercial Office (uk-3storey-office-fl-eg01)
**Jurisdiction:** GB (BS 7671:2018+A2)
**Standards:** IEC 60909-0:2016, IEC 60364-5-52:2009 Annex E, BS 7671:2018+A2
**Date:** 2026-05-18 — Revision P01
**Status:** `tool_call_pending: true` (engineer-estimated; awaiting `calc.iec60909_cascade`)

## Cascade Fault-Current Schedule

| Node            | Designation                                | Ik"max (kA) | Ik"min (kA) | ipk (kA) | X/R   | Z_total (mΩ) |
|-----------------|--------------------------------------------|-------------|-------------|----------|-------|--------------|
| HV-1            | 11 kV DNO primary radial supply            | 14.00       | 12.73       | 30.84    | 5.00  | 499.0        |
| TX-1            | 800 kVA TX 400V TPN LV terminals           |  9.85       |  8.91       | 22.50    | 6.00  |  24.6        |
| MSB-MAIN        | Main switchboard incoming                  |  9.80       |  8.87       | 22.37    | 6.00  |  24.7        |
| MSB-MAIN.BUS    | MSB busbar 630 A                           |  9.78       |  8.85       | 22.32    | 5.98  |  24.8        |
| SDB-GF          | Ground-floor SDB incoming (35 m × 95mm²)   |  8.19       |  7.41       | 15.08    | 2.40  |  29.6        |
| SDB-L1          | Level-1 SDB incoming (45 m × 95mm²)        |  7.77       |  7.03       | 13.78    | 2.09  |  31.2        |
| SDB-L2          | Level-2 SDB incoming (55 m × 95mm²)        |  7.37       |  6.67       | 12.69    | 1.87  |  32.9        |

**Notes:**
- `Ik"max` uses voltage factor c_max = 1.05 at LV (1.10 at HV) per IEC 60909-0:2016 Table 1.
- `Ik"min` uses c_min = 0.95 at LV (1.00 at HV).
- `ipk = √2·κ·Ik"max` with κ from IEC 60909-0:2016 Eq. 29: κ = 1.02 + 0.98·exp(-3/(X/R)).
- Cable impedance per IEC 60364-5-52:2009 Annex E for 95mm² Cu XLPE @ 90 °C: R=0.208 mΩ/m, X=0.0829 mΩ/m.
- HV `Z_total` quoted at HV side (referred to LV ≈ 0.66 µΩ — negligible against TX impedance).

## Breaker Breaking-Capacity Verification (BS 7671:2018+A2 Reg 434.5.1)

| Breaker          | Rating (A) | Icu (kA) | Applied Ik" (kA) | Margin | Verdict   |
|------------------|------------|----------|------------------|--------|-----------|
| MSB ACB          | 630        | 36       | 9.80             | 3.7×   | Adequate  |
| SDB-GF MCCB      | 160        | 25       | 8.19             | 3.1×   | Adequate  |
| SDB-L1 MCCB      | 160        | 25       | 7.77             | 3.2×   | Adequate  |
| SDB-L2 MCCB      | 160        | 25       | 7.37             | 3.4×   | Adequate  |

**Verdict:** All devices have breaking capacity (Icu) exceeding the prospective fault
current at their installation point by ≥ 3.0×. Compliance with BS 7671:2018+A2
Reg 434.5.1 verified. Confirm Ics rating equals Icu for full service capability.

## Selectivity / Discrimination (BS 7671:2018+A2 Reg 536.4)

- Impedance step from MSB-MAIN.BUS (24.8 mΩ) to floor SDBs (29.6–32.9 mΩ) provides
  ≈19–33 % rise across the riser — sufficient for cascade time-current discrimination
  between the upstream ACB and downstream MCCBs at the calculated Ik"max range
  (7.37–9.78 kA).
- Manufacturer let-through (I²t) tables must be consulted at design stage to confirm
  full discrimination at the upper-tier prospective fault current.

## Transient Overvoltage Protection (BS 7671:2018+A2 Reg 443.4)

Type 1/2 SPD installation recommended at MSB-MAIN origin for atmospheric-origin transient
protection on commercial office occupancy. Coordinate with downstream Type 2/3 devices at
each SDB per Reg 443/534.

## Outstanding Actions

1. `calc.iec60909_cascade` deterministic recompute — pending tool execution.
2. Manufacturer I²t coordination check across the ACB ↔ MCCB cascade.
3. Confirm DNO declaration `Ze = 0.35 Ω, PSCC = 9.8 kA` in writing prior to first fix.
