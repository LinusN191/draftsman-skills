# Sample Schedule — Kenya Nairobi Industrial Workshop Fault-Level Study

**Project:** Nairobi Industrial Workshop (ke-nairobi-industrial-fl-eg01)
**Jurisdiction:** INT (KS 1700:2018 jurisdictional layer; routes to BS 7671:2018+A2 for the short-circuit chain)
**Standards:** KS 1700:2018, IEC 60909-0:2016, IEC 60909-1:2008, IEC 60364-5-52:2009 Annex E
**Date:** 2026-05-18 — Revision P01
**Status:** `tool_call_pending: true` (engineer-estimated; awaiting `calc.iec60909_cascade`)

## Cascade Fault-Current Schedule

| Node            | Designation                                       | Ik"max (kA) | Ik"min (kA) | ipk (kA) | X/R   | Z_total (mΩ) |
|-----------------|---------------------------------------------------|-------------|-------------|----------|-------|--------------|
| HV-1            | 11 kV KPLC primary radial supply                  | 13.00       | 11.82       | 28.64    | 5.00  | 537.4        |
| TX-1            | 500 kVA KPLC TX 415 V TPN LV terminals            | 10.22       |  9.24       | 22.51    | 5.00  |  24.6        |
| MSP-100         | Main switch-panel 100 A incoming (3 m × 70mm²)    |  9.80       |  8.87       | 20.76    | 4.18  |  25.7        |
| MSP-100.BUS     | MSP busbar 100 A                                  |  9.78       |  8.85       | 20.66    | 4.13  |  25.9        |
| GH-DB           | Glasshouse/workshop DB incoming (60 m × 95mm²)    |  7.24       |  6.55       | 11.98    | 1.60  |  34.8        |

**Notes:**
- `Ik"max` uses voltage factor c_max = 1.05 at LV (1.10 at HV) per IEC 60909-0:2016 Table 1.
- `Ik"min` uses c_min = 0.95 at LV (1.00 at HV).
- `ipk = √2·κ·Ik"max` with κ from IEC 60909-0:2016 Eq. 29: κ = 1.02 + 0.98·exp(-3/(X/R)).
- Service cable per IEC 60364-5-52:2009 Annex E for 70mm² Cu XLPE @ 90 °C: R = 0.337 mΩ/m, X = 0.0875 mΩ/m.
- Submain cable per IEC 60364-5-52:2009 Annex E for 95mm² Cu XLPE @ 90 °C: R = 0.208 mΩ/m, X = 0.0829 mΩ/m.
- HV `Z_total` quoted at HV side (referred to LV ≈ 0.76 µΩ — negligible against TX impedance).

## Motor Contribution — §3.8.1 Threshold Check

| Quantity                                         | Value      |
|--------------------------------------------------|------------|
| Lathe                                            | 11 kW      |
| Pillar drill                                     |  4 kW      |
| Air compressor                                   | 22 kW      |
| **ΣP_motor**                                     | **37 kW**  |
| ΣI_rM (η = 0.85, cos φ = 0.85, 415 V)            |  71 A      |
| Threshold = 1 % × 9 800 A (IEC 60909-0:2016 §3.8.1) |  98 A      |
| Threshold met?                                   | **NO**     |
| **Motor contribution to cascade**                | **EXCLUDED** |

## Breaker Breaking-Capacity Verification (KS 1700:2018 §434.5 → BS 7671:2018+A2 §434.5.1)

| Breaker          | Rating (A) | Icu (kA) | Applied Ik" (kA) | Margin | Verdict          |
|------------------|------------|----------|------------------|--------|------------------|
| MSP-100 MCCB     | 100        | 25       | 9.80             | 2.6×   | Adequate         |
| GH-DB MCCB       |  63        | 10       | 7.24             | 1.38×  | Adequate (marginal — recommend Icu 15 kA upgrade) |

**Verdict:** Both devices have breaking capacity (Icu) exceeding the prospective fault
current at their installation point. GH-DB headroom is marginal at 1.38× and flagged for
upgrade to Icu 15 kA. Compliance with KS 1700:2018 §434.5 (routes to BS 7671:2018+A2
§434.5.1) verified. Confirm Ics ≥ 75 % Icu for full service capability.

## Selectivity / Discrimination (KS 1700:2018 §536.4 → BS 7671:2018+A2 §536.4)

- Impedance step from MSP-100.BUS (25.9 mΩ) to GH-DB (34.8 mΩ) provides ≈34 % rise across
  the 60 m submain — sufficient for cascade time-current discrimination between the
  upstream MSP MCCB and downstream GH-DB MCCB at the calculated Ik"max range
  (7.24–9.78 kA).
- Manufacturer let-through (I²t) tables must be consulted at design stage to confirm
  full discrimination at the upper-tier prospective fault current.

## Transient Overvoltage Protection (KS 1700:2018 §443.4 → BS 7671:2018+A2 §443.4)

Type 1/2 SPD installation recommended at MSP-100 origin for atmospheric-origin transient
protection. Nairobi sits on the Rift escarpment with an elevated keraunic level
(40–80 thunder-days/year, AQ2 classification). Coordinate with a downstream Type 2/3 SPD
at GH-DB per KS 1700:2018 §443 + §534.

## Outstanding Actions

1. `calc.iec60909_cascade` deterministic recompute — pending tool execution.
2. Manufacturer I²t coordination check across the MSP MCCB ↔ GH-DB MCCB cascade.
3. Confirm KPLC declaration `Ze = 0.80 Ω, PSCC = 9.8 kA` in writing prior to first fix.
4. Re-run §3.8.1 motor-contribution threshold check if workshop motor inventory expands
   (compressor upgrade, additional CNC plant, fire-pump driver added). Threshold engages
   once `ΣI_rM ≥ 98 A`.
