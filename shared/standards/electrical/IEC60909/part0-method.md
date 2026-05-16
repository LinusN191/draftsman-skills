# IEC 60909-0:2016 — Calculation Method (Step-by-Step)

This file is the canonical reference for the calculation steps the `electrical/fault-level` generator prompt walks every IR through. The math itself runs in the `calc.iec60909_cascade` runtime tool (per the WI3 deferral pattern); this document tells engineers what the tool does.

## Inputs (preconditions)

Before applying the method, the engineer/skill must know:

1. **Fault location:** every node in the cascade tree where Ik" is needed
2. **Source(s):** utility transformer rating + Zpu OR generator(s) + X"d profile OR UPS rated current + bypass path OR running motor load (for motor back-feed)
3. **Cascade path:** series chain of impedances from each source to each fault point — typically:
   - HV primary (network impedance ZQ if HV supply present)
   - Transformer (Zk referred to LV)
   - LV mains cable (R + jX per length, csa, insulation)
   - Sub-DB feeder cable
   - Final-circuit cable
4. **Voltage factor c:** 1.05 for Ik"max (breaker rating); 0.95 for Ik"min (protection setting)

## Step 1 — Classify the system

**Near-from-generator (NG)** or **Far-from-generator (FG)?**

- If ΣP_synchronous_generation > 5% of source Sk" at the fault → NG method (apply subtransient → transient → steady-state decrement)
- Otherwise FG method (Ik = Ib = Ik", constant source)

Building-services projects fed from public DNO grid are almost always FG. Standby-generator projects switch to NG when on gen.

## Step 2 — Compute source impedance ZQ

For a utility supply with known Sk" at primary substation:
- `ZQ = c × U²_n / Sk"` (positive sequence)
- `XQ ≈ ZQ × X/R_ratio / √(1 + (X/R)²)`
- `RQ ≈ ZQ / √(1 + (X/R)²)`

For a transformer LV-side calculation (typical building services):
- `Zk_TX_ohm = (Zpu_percent / 100) × U²_LV[V] / S_TX[VA]`
- Equivalent with kVA notation: `Zk_TX_ohm = (Zpu_percent / 100) × U²_LV[V] / (S_TX_kVA × 1000)`
- Or in kV/MVA convention: `Zk_TX_ohm = (Zpu_percent / 100) × U²_LV[kV] / S_TX[MVA]` × 1000 *(returns mΩ; divide by 1000 for Ω)*
- Worked: 500 kVA, 4% Zpu, 230V → Z = 0.04 × 230² / (500 × 1000) = 4.23 mΩ
- Split Zk into R + jX using transformer X/R (typical 5-10 for distribution transformers)

For a generator (near-from-generator):
- `X"d_ohm = (X"d_pu) × U²_LV / S_gen_kVA` for the subtransient period (Ik")
- `X'd_ohm = (X'd_pu) × U²_LV / S_gen_kVA` for the transient period (Ib at ~100 ms)
- `Xd_ohm = (Xd_pu) × U²_LV / S_gen_kVA` for the steady-state period

## Step 3 — Build series impedance to each fault point

Walk the cascade tree from source to fault, summing R + jX of each link:

| Link | R contribution | X contribution |
|---|---|---|
| Source (utility OR gen) | RQ + R_TX | XQ + X_TX |
| Main feeder cable | r × L_main | x × L_main |
| Sub-DB feeder cable | r × L_sub | x × L_sub |
| Final circuit cable | r × L_final | x × L_final |

Where:
- `r` = cable resistance per metre (Ω/m) at conductor operating temperature
- `x` = cable reactance per metre (Ω/m)
- `L` = one-way length in metres

Get r + x from:
- **GB:** BS 7671 Appendix 4 Tables 4D5 (R), Table 4F (X)
- **EU/INT:** IEC 60364-5-52 Annex E
- **US:** NEC 2023 Chapter 9 Table 9 (ac resistance + reactance)

## Step 4 — Compute Ik" at each node

For a three-phase symmetrical fault:
```
Ik" = c × Un / (√3 × |Z_total|)
```

Where `|Z_total| = √(R_total² + X_total²)`.

For maximum (breaker rating check): `c = c_max = 1.05` (LV)
For minimum (ADS check):           `c = c_min = 0.95` (LV)

## Step 5 — Compute peak current ipk

```
ipk = κ × √2 × Ik"
```

Where κ (kappa) is the peak factor per IEC 60865-1:
```
κ = 1.02 + 0.98 × exp(-3 R/X)
```

| X/R ratio | κ | Interpretation |
|---|---|---|
| 0.5 | 1.02 + 0.98 × exp(-6) ≈ 1.022 | Highly resistive — small peak |
| 1 | 1.02 + 0.98 × exp(-3) ≈ 1.069 | Moderate |
| 5 | 1.02 + 0.98 × exp(-0.6) ≈ 1.557 | Industrial typical |
| 10 | 1.02 + 0.98 × exp(-0.3) ≈ 1.747 | Large transformer |
| 30+ | 1.02 + 0.98 × exp(-0.1) ≈ 1.907 | Generator/large MV — close to maximum 2.0 |

See `peak-factor-kappa.json` for the table.

## Step 6 — For near-from-generator: apply decrement

If the fault is supplied by a synchronous generator (standby genset on a transfer scheme):

- **First cycle (subtransient):** Use X"d → compute Ik"
- **Breaking-current time tmin (≈ 30-90 ms for MCCB/ACB):** Apply decrement factor μ:
  - `Ib_NG = μ × Ik"`
  - `μ` from IEC 60909-0 §3.5 Table 4 (function of Ik"_gen / In_gen and tmin)
  - Typical μ ≈ 0.75-0.85 for tmin ≈ 90 ms
- **Steady state:** `Ik = λ × In_gen` where λ from Table 5 (function of X"d, X'd, Xd)

For far-from-generator: skip this step. Ik = Ib = Ik".

## Step 7 — Multi-source superposition

When utility + generator + UPS + motors contribute simultaneously (data centre topology, ATS in parallel-paths mode):

```
Ik"_total = Σ Ik"_source_i
```

Each source contributes its own Ik" via its source path to the fault. Sum the complex values:
```
I_total_complex = Σ (c × Un / (√3 × Z_path_i))
|Ik"_total| = |I_total_complex|
```

For most building services: utility OR generator (transfer scheme = one source at a time). For data centres: utility + UPS + sometimes static gen → multi-source applies.

## Step 8 — Output

Emit at each cascade node:

```json
{
  "node_id": "MSB-1.F01.DB-L1",
  "ifault_ka_max": 23.4,
  "ifault_ka_min": 21.1,
  "ipk_ka": 35.7,
  "x_over_r_at_node": 4.2,
  "z_total_ohm": 0.024
}
```

## What does NOT happen here

- DC arc-flash calculation (separate IEEE 1584 method)
- Lightning surge analysis (BS EN 62305 / NFPA 780)
- Sub-cycle dynamic simulation (EMT-level — beyond IEC 60909 scope)
- Time-graded protection curves (separate protection-coordination scope)
