# Reasoning — UK Domestic Single-Source Cascade

## Step 1 — Discovery
No `cross_drawing_context` (no db-layout intent). Engineer-declared cascade (5 nodes).

## Step 2 — Standards loaded (GB)
IEC 60909 always-on (8 files) + IEC 60617 (2 files) + BS 7671 reg434 + pscc-determination + appendix4-cable-ratings.

## Step 3 — Cascade topology
5 nodes: TX → CU-G (incoming) → CU-G.BUSBAR → 2 final circuits (C01 lighting, C03 sockets ring).

## Step 4 — HV-side
N/A — no HV present.

## Sprint B H3 correction (May 2026 — read before Step 5)

Following Sprint B H3 remediation, the cascade anchor was reframed. Previously this example derived `Z_TX` from the supplied `lv_source.z_percent = 4.0` and then walked downstream — but the resulting `z_total` values at each node satisfied no documented IEC 60909 formula, with cascade `Ik` and `z_total` simply not reconciling.

The corrected approach anchors on the DNO-declared PSCC at CU-G (the service head), which is the binding boundary per BS 7671:2018+A2:2022 Reg 313.1.1:

- **CU-G anchored:** declared PSCC `1.5 kA` → `Z_CU-G = c · U₀ / (2 · Ik) = 1.05 · 230 / (2 · 1500) = 0.0805 Ω` per IEC 60909-0:2016 §6 single-phase TN L-N formula.
- **TX-1 back-derived upstream:** the 5 m of 25 mm² Cu PVC service cable contributes `|Z_cable| = √(0.004² + 0.0005²) ≈ 0.00403 Ω`, so `Z_TX-1 = Z_CU-G − Z_cable = 0.0805 − 0.00403 = 0.07647 Ω`.
- **`lv_source.z_percent` now informational only:** the 4% transformer impedance hint is retained as a sanity check but does NOT drive the cascade — the DNO declaration is authoritative per Reg 313.1.

All five nodes now reconcile to `Ik = c · U₀ / (2 · Z)` within the 1% INV-11 tolerance (single-phase TN, c_max = 1.05 LV per IEC 60909-0:2016 Table 1).

## Step 5 — Transformer + service-head impedances (post-H3 derivation)
500 kVA TX, supplied `Zpu = 4%` is informational (sanity-check) — the binding anchor is the DNO-declared 1.5 kA at CU-G per BS 7671 Reg 313.1.1.
- `Z_CU-G = c · U₀ / (2 · Ik_declared) = 1.05 · 230 / (2 · 1500) = 0.0805 Ω` per IEC 60909-0:2016 §6.
- `|Z_service_cable| = √(0.004² + 0.0005²) ≈ 0.00403 Ω` (5 m of 25 mm² Cu PVC).
- `Z_TX-1 = Z_CU-G − |Z_service_cable| = 0.0805 − 0.00403 = 0.07647 Ω` (back-derived upstream).
- X/R = 5 (engineer value, IEC 60909-2 typical for 500 kVA distribution TX).

## Step 6 — Generator: N/A
## Step 7 — UPS: N/A
## Step 8 — Motor: N/A (0 kW)

## Step 9 — Cable impedance (BS 7671 App 4)
- CU incoming feeder: 25mm² Cu, 5m → R ≈ 4 mΩ, X ≈ 0.5 mΩ → |Z| ≈ 4.03 mΩ
- C01 lighting: 1.5mm² Cu, 18m → R ≈ 220 mΩ, X ≈ 4 mΩ → |Z| ≈ 220.0 mΩ
- C03 ring: 2.5mm² Cu, 38m → R ≈ 281 mΩ, X ≈ 9 mΩ → |Z| ≈ 281.1 mΩ (ring approximated as radial worst-case; tight ring would halve cable R per BS 7671 App 15)

## Step 10 — Cascade Ifault (post-H3 reconciliation)

Single-phase TN L-N formula `Ik = c · U₀ / (2 · Z)` applied at every node (c_max = 1.05 LV per IEC 60909-0:2016 Table 1, U₀ = 230 V):

| Node           | z_total (Ω) | Ik"max (kA) | Basis                                                |
|----------------|-------------|-------------|------------------------------------------------------|
| TX-1           | 0.07647     | 1.579       | Back-derived upstream of CU-G                        |
| CU-G           | 0.0805      | 1.500       | DNO declaration anchor (Reg 313.1.1) — binding       |
| CU-G.BUSBAR    | 0.0810      | 1.491       | CU-G + negligible busbar trunk increment             |
| CU-G.C01       | 0.3010      | 0.401       | Busbar z + 220.0 mΩ 1.5 mm² lighting cable           |
| CU-G.C03       | 0.3621      | 0.334       | Busbar z + 281.1 mΩ 2.5 mm² ring (radial worst-case) |

C01 and C03 values were the most defective at the pre-H3 baseline (stored at 0.85 and 0.79 kA respectively, dramatically inconsistent with the physical cable impedance); they are now driven by the cable z and reconcile within 1%.

## Step 11 — Peak factor
LV cable-dominated: X/R range 0.4-5 across cascade → κ ≈ 1.02-1.59. ipk values stored: TX-1 3.48 kA, CU-G 2.79 kA, CU-G.BUSBAR 2.77 kA, C01 0.58 kA, C03 0.48 kA (each `≈ κ · √2 · Ik"max` for that node's X/R per IEC 60909-0:2016 Eq 29).

## Step 12 — Tool call
DNO PSCC engineer-declared at CU-G (BS 7671 Reg 313.1.1 binding) and cable impedances tabulated. Engineer-input fallback used; calc.iec60909_cascade would refine. Emit tool_call_pending: true.

## Step 13 — Selectivity
- DNO service fuse 100A (BS 1361 Type II, Icn 33 kA) at TX-1 (1.579 kA cascade): adequate (≥20× margin).
- CU main switch (100A, 6 kA rating) at CU-G (1.500 kA): well within rating.
- Final circuit MCBs (6 kA Icn) at C01 (0.401 kA): adequate (15× margin). C03 ring on Type B 32A MCB 6 kA Icn at 0.334 kA: adequate.

## Step 14 — Rationale block emitted (see output.json — 8 sections cite IEC 60909-0:2016 §6 + Table 1 + BS 7671:2018+A2:2022 Reg 313.1.1 + App 4 Table 4D5/4F).
