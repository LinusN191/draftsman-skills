# Reasoning — INT Commercial TPN with Standby Genset

## Step 1 — Discovery
Single MSB project with HV side present. Standby generator declared.

## Step 2 — Standards loaded (INT → IEC 60364 family + IEC 60909 + IEC 60617)
- All 8 IEC 60909 files
- IEC60617 symbol-index + part7-switchgear
- IEC60364 fault-current + pscc-determination + part5-52-cable-ratings-copper + part5-52-cable-ratings-aluminium
(NOT BS 7671, NOT NFPA 70)

## Step 3 — Cascade topology
5 nodes: HV-1 → TX-1 → MSB-1 → MSB-1.BUSBAR → DB-L1.

## Sprint B H1+H2 correction (May 2026 — read before Steps 4-10)

Following Sprint B remediation, two defects in this example's cascade were corrected:

- **H1 (TX-1 sub-impedance).** Previously stored `z_total = 0.005 Ω` was below the transformer's own LV-referred impedance — physically impossible. Recomputed per IEC 60909-0:2016 §3.3: `z_total = ZQ_LV + Z_TX_LV = 0.000577 + 0.005 = 0.005577 Ω`. Ik_max at TX-1 LV terminals refreshed from prior placeholder to `Ik = 1.05 · 400 / (√3 · 0.005577) ≈ 43.49 kA`.
- **H2 (HV-1 double-c-factor).** Declared utility PSCC `16 kA` was being multiplied by `c = 1.10` a second time, producing `17.6 kA`. Per IEC 60909-0:2016 §3.3.2 the declared PSCC IS already c-corrected by the utility — `ZQ` is back-calculated FROM it, not the other way around. HV-1 now stores `Ik = 16.0 kA` exactly, with `ZQ_HV = c · U_HV / (√3 · Ik_declared) = 1.10 · 11kV / (√3 · 16 kA) = 0.4366 Ω`.

Downstream nodes (MSB-1, MSB-1.BUSBAR, DB-L1) were re-cascaded against the corrected TX-1 z. All Ik values quoted in Steps 4-13 below reflect the corrected cascade.

## Step 4 — HV-side modelling
11 kV declared PSCC 16 kA, X/R = 5. Declared PSCC is already c-corrected by the utility per IEC 60909-0:2016 §3.3.2 — back-calculate `ZQ_HV = c · U_HV / (√3 · Ik_declared) = 1.10 · 11000 / (√3 · 16000) = 0.4366 Ω` (do NOT re-multiply Ik by c). HV-1 stores `Ik = 16.0 kA` exact.

## Step 5 — Transformer impedance
1600 kVA, Zpu = 5%, X/R = 7.
- `ZQ_LV = ZQ_HV × (U_LV / U_HV)² = 0.4366 × (400 / 11000)² = 0.000577 Ω` (HV source impedance referred to LV via the transformer ratio squared).
- `Z_TX_LV = u_k × U_LV² / S_tx = 0.05 × 400² / 1.6 MVA = 0.005 Ω`.
- `z_total_TX = ZQ_LV + Z_TX_LV = 0.005577 Ω` per IEC 60909-0:2016 §3.3 series-sum at LV terminals.
- `Ik_max_TX = 1.05 · 400 / (√3 · 0.005577) ≈ 43.49 kA` per Table 1 (c_max = 1.05 LV).

## Step 6 — Generator modelling (standby)
800 kVA, X"d_pu = 0.15 → X"d_ohm = 0.15 × 400² / 800000 × 1000 = 30 mΩ at LV.
Near-from-generator method per IEC 60909-0:2016 §3.5. Decrement profile X"d → X'd → Xd.
In utility-mode: gen output breaker open, no contribution. In gen-mode: only gen source.

## Step 7 — UPS: N/A
## Step 8 — Motor: 0 kW, no contribution

## Step 9 — Cable impedance (IEC 60364-5-52 Annex E)
- MSB feeder 240mm² Cu XLPE, 15m: R ≈ 1.2 mΩ, X ≈ 1.2 mΩ → |Z| = √(R² + X²) ≈ 1.697 mΩ
- DB-L1 feeder 150mm² Cu XLPE, 35m: R ≈ 4.5 mΩ, X ≈ 2.8 mΩ → |Z| ≈ 5.300 mΩ

## Step 10 — Cascade Ifault (utility mode, worst case)

Series-sum of upstream `z_total` + cable magnitude at each node, then `Ik = c · U / (√3 · Z)` per IEC 60909-0:2016 §4.3 (c_max = 1.05 LV):

| Node             | z_total (Ω)  | Ik"max (kA) | Basis                                       |
|------------------|--------------|-------------|---------------------------------------------|
| HV-1             | 0.4366 (HV)  | 16.00       | Declared PSCC; ZQ back-calculated per §3.3.2 |
| TX-1             | 0.005577     | 43.49       | ZQ_LV + Z_TX_LV per §3.3                    |
| MSB-1            | 0.007274     | 33.34       | TX-1 z + 1.697 mΩ MSB feeder                |
| MSB-1.BUSBAR     | 0.007280     | 33.31       | MSB-1 + 0.006 mΩ busbar trunk increment     |
| DB-L1            | 0.01258      | 19.27       | Busbar z + 5.300 mΩ DB-L1 feeder            |

All five nodes reconcile to `Ik = c · U / (√3 · Z)` within the 1% INV-11 tolerance.

## Step 11 — Peak factor
Per IEC 60909-0:2016 Eq 29, `κ = 1.02 + 0.98 · exp(-3 · R/X)` per node. ipk values stored: HV-1 35.27 kA, TX-1 102.0 kA, MSB-1 76.12 kA, MSB-1.BUSBAR 76.05 kA, DB-L1 40.42 kA (each `≈ κ · √2 · Ik"max` for that node's X/R).

## Step 12 — Tool call
calc.iec60909_cascade tool_call_pending: true. Multi-source utility + gen requires complex-number addition.

## Step 13 — Selectivity
- ACB main 2000A Icn 65 kA at MSB-1 (33.34 kA cascade): adequate (1.95× margin).
- MCCB DB-L1 250A Icn 25 kA at DB-L1 (19.27 kA cascade): adequate (1.30× margin — verify Ics ≥ Icu at full rating per IEC 60947-2).

## Step 14 — Rationale emitted (8 sections cite IEC 60909-0:2016 §3.3, §3.3.2, §3.4, §3.5, §4.3, §4.4, §6 + Table 1).
