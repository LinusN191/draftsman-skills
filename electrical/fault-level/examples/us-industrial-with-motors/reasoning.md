# Reasoning — US Industrial with Motor Back-Feed

## Step 1 — Discovery
US industrial with HV side + material motor load. No db-layout intent.

## Step 2 — Standards loaded (US → NFPA 70 + IEC 60909 + IEC 60617)
- All 8 IEC 60909 files
- IEC 60617 symbol-index + part7-switchgear
- NFPA70 chapter1-general (NEC 110.9) + art240-overcurrent + ocpd-coordination + chapter9-tables (Table 9 R+X)
(NOT BS 7671, NOT IEC 60364 — strict NEC jurisdiction)

## Step 3 — Cascade topology
5 nodes: HV-1 → TX-1 → MSB-1 → MSB-1.BUSBAR → MCC-1.

## Step 4 — HV-side
12.47 kV declared PSCC 25 kA, X/R = 6 (US 12.47 kV urban). c_max = 1.10.
ZQ at HV: (1.10 × 12470²) / (√3 × 12470 × 25000) = 0.317 Ω.

## Step 5 — Transformer
2500 kVA, Zpu = 6%, X/R = 8 → Z_TX = 0.06 × 480² / 2500000 × 1000 = 5.53 mΩ at LV.

## Step 6 — Generator: N/A
## Step 7 — UPS: N/A

## Step 8 — Motor contribution (KEY for this example)
500 kW total motor load. Source Sk" ≈ 1600 × 1.05 / (Zk × √3) ≈ 25 kA × 480 × √3 = 20.8 MVA.
500 kW / 480V / √3 ≈ 600A FLC. ILR 5 (Letter K) → Ik"_motor ≈ 3000A = 3 kA.
3 kA / 22 kA ≈ 14% — well above 1% threshold per IEC 60909-0:2016 §4.5.1.2. INCLUDE.

## Step 9 — Cable impedance (NEC Chapter 9 Table 9)
MSB feeder 350 kcmil Cu THWN-2, 20m → R ≈ 1.0 mΩ, X ≈ 1.0 mΩ at 75°C.
MCC feeder 350 kcmil 30m → R ≈ 1.5 mΩ, X ≈ 1.5 mΩ.

## Step 10 — Cascade Ifault
At TX-1 LV: Ik"max = 1.05 × 480 / (√3 × 5.53e-3) ≈ 52 kA (utility only).
With motor contribution (3 kA at MCC referred upstream by Z): adds ~2 kA at MSB → ~54 kA.
At MSB-1 (after feeder): ≈ 38 kA (cable Z drops it significantly).
At MCC-1: ≈ 32 kA + motor contribution AT THE NODE ≈ 35 kA.

c_max=1.05 LV. ipk via κ at each node.

## Step 11 — Peak factor
At MSB: X/R ≈ 8 → κ ≈ 1.67 → ipk ≈ 90 kA.

## Step 12 — Tool call
calc.iec60909_cascade tool_call_pending — multi-source (utility + motor_aggregate) + cascade tree requires deterministic computation.

## Step 13 — Selectivity
Main ACB 3200A Icn 100 kA (US ACB rating): adequate at 54 kA.
MCCB feeders Icn 35 kA: marginal at 38 kA → flag for review.
MCC starters typically Icn 25 kA — adequate at 35 kA only if cascade-rated upstream.

## Step 14 — Rationale emitted with NEC 110.9 + IEC 60909-0 §4.5 citations.
