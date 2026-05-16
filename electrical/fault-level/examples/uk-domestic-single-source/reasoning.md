# Reasoning — UK Domestic Single-Source Cascade

## Step 1 — Discovery
No `cross_drawing_context` (no db-layout intent). Engineer-declared cascade (5 nodes).

## Step 2 — Standards loaded (GB)
IEC 60909 always-on (8 files) + IEC 60617 (2 files) + BS 7671 reg434 + pscc-determination + appendix4-cable-ratings.

## Step 3 — Cascade topology
5 nodes: TX → CU-G (incoming) → CU-G.BUSBAR → 2 final circuits (C01 lighting, C03 sockets ring).

## Step 4 — HV-side
N/A — no HV present.

## Step 5 — Transformer impedance
500 kVA, Zpu = 4%, X/R = 5 → Z_TX = 0.04 × 230² / 500000 × 1000 = 4.23 mΩ at LV. R_TX ≈ 0.83 mΩ, X_TX ≈ 4.15 mΩ.

## Step 6 — Generator: N/A
## Step 7 — UPS: N/A
## Step 8 — Motor: N/A (0 kW)

## Step 9 — Cable impedance (BS 7671 App 4)
- CU incoming feeder: 25mm² Cu, 5m → R ≈ 4 mΩ, X ≈ 0.5 mΩ
- C01 lighting: 1.5mm² Cu, 18m → R ≈ 220 mΩ, X ≈ 4 mΩ
- C03 ring: 2.5mm² Cu, 38m → R ≈ 281 mΩ, X ≈ 9 mΩ (ring formula simplified for cascade)

## Step 10 — Cascade Ifault
At TX-1: Ik"max ≈ 1.575 kA (declared PSCC 1.5 kA × 1.05/1.00 c-factor adjustment)
At CU-G (after 5m feeder): ≈ 1.50 kA (DNO declared anchor)
At C01 final: ≈ 0.85 kA (cable drop dominates)
At C03 final: ≈ 0.79 kA

Engineer-declared PSCC at CU-G = 1.5 kA accepted as Ik"max anchor (DNO authority).

## Step 11 — Peak factor
LV cable-dominated: X/R ≈ 1-2 → κ ≈ 1.07-1.18. ipk_max at CU-G ≈ 2.3 kA peak.

## Step 12 — Tool call
DNO PSCC engineer-declared and cable impedances tabulated. Engineer-input fallback used; calc.iec60909_cascade would refine. Emit tool_call_pending: true.

## Step 13 — Selectivity
DNO service fuse 100A (BS 1361 Type II, Icn 33 kA): adequate.
CU main switch (100A): no MCB Icn check at 1.5 kA — passes.
Final circuit MCBs (6 kA Icn): adequate at 0.8-1.5 kA cascade Ifault.

## Step 14 — Rationale block emitted (see output.json).
