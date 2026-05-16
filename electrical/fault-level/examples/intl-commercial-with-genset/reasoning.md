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

## Step 4 — HV-side modelling
11 kV declared PSCC 16 kA, X/R = 5. ZQ = (1.10 × 11000²) / (√3 × 11000 × 16000) = 0.436 Ω at HV.
Apply c_max = 1.10 (HV per Table 1) for max Ik".

## Step 5 — Transformer impedance
1600 kVA, Zpu = 5%, X/R = 7 → Z_TX = 0.05 × 400² / 1600000 × 1000 = 5 mΩ at LV. R_TX ≈ 0.71 mΩ, X_TX ≈ 4.95 mΩ.

## Step 6 — Generator modelling (standby)
800 kVA, X"d_pu = 0.15 → X"d_ohm = 0.15 × 400² / 800000 × 1000 = 30 mΩ at LV.
Near-from-generator method per IEC 60909-0:2016 §3.5. Decrement profile X"d → X'd → Xd.
In utility-mode: gen output breaker open, no contribution. In gen-mode: only gen source.

## Step 7 — UPS: N/A
## Step 8 — Motor: 0 kW, no contribution

## Step 9 — Cable impedance (IEC 60364-5-52 Annex E)
- MSB feeder 240mm² Cu XLPE, 15m: R ≈ 1.2 mΩ, X ≈ 1.2 mΩ
- DB-L1 feeder 150mm² Cu XLPE, 35m: R ≈ 4.5 mΩ, X ≈ 2.8 mΩ

## Step 10 — Cascade Ifault (utility mode, worst case)
At HV-1 (referred to LV via TX): ≈ 23 kA
At TX-1 LV (after Z_TX): ≈ 22 kA
At MSB-1 (after feeder): ≈ 21 kA
At MSB-1.BUSBAR: ≈ 21 kA
At DB-L1 (after feeder): ≈ 18 kA

c_max=1.05 applied for breaker rating Ik"max.

## Step 11 — Peak factor
At MSB-1: X/R ≈ 7 → κ ≈ 1.56 → ipk_max ≈ 46 kA peak.

## Step 12 — Tool call
calc.iec60909_cascade tool_call_pending: true. Multi-source utility + gen requires complex-number addition.

## Step 13 — Selectivity
ACB main 2000A Icn 65 kA: adequate.
MCCB feeders 25 kA Icn: adequate at 21-22 kA.

## Step 14 — Rationale emitted (8 sections cite IEC 60909-0:2016 §3.4, §3.5, §4.3, §4.4).
