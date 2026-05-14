# IEC 60364 — Prospective Short-Circuit Current (PSCC) Determination

Reference: IEC 60364-4-43:2008 Clause 434 (Short-circuit protection), IEC 60364-6:2016 Clause 61 (Initial verification), IEC 60909-0:2016 (Short-circuit currents in three-phase AC systems)

---

## Why PSCC Matters

The Prospective Short-Circuit Current (PSCC) at any point in an installation is the maximum fault current that would flow under a bolted (zero impedance) three-phase fault at that point. Every protective device — MCB, fuse, MCCB, ACB — must have a rated breaking capacity (Icu or Icn) that equals or exceeds the PSCC at its installation point.

A device that interrupts a fault current exceeding its breaking capacity will either fail to interrupt (sustained arcing, fire, explosion) or be destroyed in the attempt. Either outcome is unacceptable. PSCC determination is therefore a safety-critical calculation, not an administrative one.

Two further uses of PSCC:

1. **Adiabatic check (Clause 434.5):** The energy let-through I²t during fault clearance must not exceed the cable's thermal withstand k²S². PSCC is the input to the I²t calculation.
2. **Selectivity analysis:** Knowing the PSCC at each distribution board lets the designer set short-time delay and instantaneous trip thresholds for coordinated discrimination.

---

## The Fault Impedance Chain

At any point in a system, the PSCC is calculated from:

```
Isc = U₀ / Ztotal (single-phase to earth fault, TN system)
or
Isc = U / (√3 × Ztotal) (three-phase bolted fault)
```

Where U₀ = 230V (line-to-earth) and U = 400V (line-to-line) for standard 230/400V systems.

Ztotal is the sum of all impedances in the fault current path back to the source — the impedance chain. Every section of conductor between the source transformer and the fault point adds impedance.

```
Ztotal = Ztransformer + Zcables_to_point

For cables:
Z = R + jX  (impedance = resistance + reactance)
For small cables (≤50mm²): R >> X, so Z ≈ R (reactance negligible)
For large cables (≥70mm²): include X (typically 0.07–0.10 mΩ/m for LV cables)
```

The practical implication: PSCC decreases as you move further from the source. A main switchboard near the transformer has very high PSCC (5–50kA depending on transformer rating). A final circuit at the end of a long cable run may have a PSCC of only 500–2000A.

---

## Method 1: Measurement on Site (Initial Verification)

IEC 60364-6:2016 Clause 61.3.6 requires measurement of PSCC or earth fault loop impedance Zs during initial verification. The measured Zs gives the actual fault loop impedance at the point of test.

**Instrument:** A loop impedance tester (also called an earth loop tester or Zs meter) injects a test current into the loop and measures the resulting voltage drop to calculate impedance.

**Procedure:**
1. Set instrument to measure loop impedance (Zs)
2. Connect to the phase and earth terminals at the point under test (e.g. socket outlet)
3. Instrument measures: Zs = U₀ / test_current_injected × (correction factor)
4. Calculate PSCC from Zs: Isc = U₀ / Zs = 230 / Zs

**Limitations:**
- Measures Zs at supply voltage conditions — not the same as short-circuit Zs under low voltage during a real fault (voltage dip reduces driving voltage but also reduces impedance — effects partially cancel)
- Test current is small (typically 15–25A AC) — device under test may not be energised at rated current. For accurate results, the installation should be at normal operating temperature.
- Cannot be used to measure three-phase PSCC directly — derives from single-phase Zs
- Must be done with supply on — requires appropriate arc flash precautions

**Correcting for temperature:**
Measurements are normally taken at ambient temperature. At full load and elevated temperature, cable resistance increases: R_T = R_20 × [1 + 0.004 × (T - 20)]. The measured Zs therefore underestimates the hot Zs. IEC 60364-6 permits multiplying measured Zs by a correction factor to obtain the hot impedance — for typical UK practice this is ×1.20 for PVC cables at 70°C. Verify against the actual cable conductor temperature for critical circuits.

---

## Method 2: Calculation from Source Data

Where measurement is not yet possible (design stage, or where live testing is unsafe), PSCC is calculated by summing the impedances in the fault current path.

### Step 1 — Obtain Ze (external impedance)

Ze is the loop impedance of the supply network, measured at the origin of the installation (ahead of the consumer's own wiring). For a building connected to the public supply:

- **From the Distribution Network Operator (DNO):** Request the declared Ze for the supply point. Typical values:
  - TN-C-S (PME) overhead low-voltage network: Ze = 0.35Ω (typical), range 0.1–0.8Ω
  - TN-S underground cable network: Ze = 0.20Ω (typical), range 0.05–0.5Ω
  - TT supply: Ze = not relevant for RCD-protected circuits — use Ra × IΔn ≤ 50V instead
- **Measured:** Loop impedance tester at the intake, before the consumer's main switch

### Step 2 — Calculate cable impedances

For each cable section from the origin to the point of interest:

```
R_conductor = ρ × L / A × correction_factor

Where:
  ρ = conductor resistivity at 20°C
      Copper: 0.01724 Ω·mm²/m  (or use: R_20 = resistivity_table from IEC 60228)
      Aluminium: 0.02826 Ω·mm²/m
  L = one-way cable length (m)  [Note: for a fault loop, include both the phase AND CPC conductors]
  A = conductor cross-section (mm²)
  correction_factor = [1 + α × (T - 20)]  where α = 0.004 for copper, 0.004 for aluminium
```

For the fault current path, sum the phase conductor resistance and the CPC resistance:
```
R_loop = R_phase + R_CPC = ρ × L × (1/A_phase + 1/A_CPC)
```

### Step 3 — Sum impedances

```
Zs = Ze + R_loop_section_1 + R_loop_section_2 + ... (adding all cable sections)
```

For cables where reactance is significant (≥70mm²), use:
```
Zs = √(R_total² + X_total²)
```
where X is typically 0.07–0.10 mΩ/m per conductor for LV power cables.

### Step 4 — Calculate PSCC

```
Isc (single-phase) = U₀ / Zs = 230 / Zs  (result in amperes)
Isc (3-phase) = U / (√3 × Zs) = 400 / (1.732 × Ztransformer_3phase)
```

### Step 5 — Verify against protective device

```
Protective device breaking capacity (Icu or Icn) ≥ Isc at the device installation point ✓
```

---

## Method 3: From Transformer Data

For a building with its own dedicated transformer (or where the supply is taken directly from an MV/LV substation), the transformer's own impedance is the dominant component of Ze.

**Transformer impedance:**
```
Zt = (uk% / 100) × (Un² / Sn)

Where:
  uk% = transformer short-circuit impedance as a percentage (nameplate value, typically 4–6%)
  Un  = transformer secondary rated voltage (V) — 400V for 3-phase LV
  Sn  = transformer rated apparent power (kVA)
```

**Three-phase bolted fault current at transformer LV terminals:**
```
Isc_3ph = Sn × 1000 / (√3 × Un × uk/100)
        = Sn(kVA) × 1000 / (√3 × 400 × uk/100)
```

**Worked example:**
```
Transformer: 500kVA, uk = 5%, 400V secondary

Isc_3ph = 500 × 1000 / (1.732 × 400 × 0.05)
        = 500000 / 34640
        = 14,433 A ≈ 14.4 kA

This is the 3-phase PSCC at the transformer LV terminals.
Main switchboard 6m from transformer on 4 × 240mm² cables per phase (in parallel):
R_cable = 0.0754 mΩ/m × 6 / 4 = 0.113 mΩ per phase (very small)
Effect is negligible — PSCC at main switchboard ≈ 14 kA

→ Specify minimum 15kA breaking capacity devices at main LV panel.
```

**Worked example — final circuit PSCC:**
```
From the example above, Ze = 0.35Ω at the consumer's origin.
Final circuit: 32A Type C MCB, 2.5mm² copper PVC cable, 30m length (one way)

R1 (2.5mm² at 70°C) = 12.1 × 1.20 / 1000 mΩ/m × 30m = 0.436Ω (one way)
R2 (1.5mm² CPC at 70°C, assumed) = 12.1/1.5 × 1.20 / 1000 × 1000 × 30/1000... 

Actually using resistivity:
R_phase = (0.01724 × 1.20 × 30) / 2.5 = 0.621 / 2.5 = 0.2484 Ω
R_CPC   = (0.01724 × 1.20 × 30) / 1.5 = 0.621 / 1.5 = 0.4140 Ω

R_loop  = 0.2484 + 0.4140 = 0.6624 Ω
Zs      = Ze + R_loop = 0.35 + 0.6624 = 1.012 Ω

Isc     = 230 / 1.012 = 227 A

ADS check (Type C, 32A): Ia = 320A → Zs_max = 0.72Ω
Measured Zs = 1.012Ω > 0.72Ω → FAIL — circuit will NOT disconnect in time.

Remedies: Increase cable size (reduce R_loop) or add 30mA RCD 
→ With 30mA RCD: disconnection independent of Zs (RCD trips at 30mA) ✓
```

---

## Method 4: PSCC from DNO or Utility Data

For supply connections to the public LV network, the DNO can provide:
- Declared Ze at the supply terminals
- Maximum and minimum PSCC values

Maximum PSCC is used for breaking capacity selection of devices.
Minimum PSCC (at light network load, maximum Ze) is used for ADS verification — you need to confirm the device will trip even under worst-case (maximum Zs) conditions.

Always design to the **minimum PSCC** for ADS compliance checks, and to the **maximum PSCC** for device breaking capacity.

---

## Maximum PSCC vs Minimum PSCC — The Two Design Cases

This distinction is critical and frequently confused:

| Design Check | Use | Reason |
|---|---|---|
| Device breaking capacity | Maximum PSCC | Device must survive the worst-case fault energy it will ever see |
| ADS compliance (Zs check) | Minimum PSCC (maximum Zs) | Device must trip even when fault current is lowest |
| Adiabatic cable check | Maximum PSCC (worst I²t) | Cable must survive the highest energy let-through |
| Selectivity study | Range of PSCCs | Need to know trip behaviour from maximum to minimum fault level |

---

## Guidance on Typical PSCC Values by System

| Supply Type | Typical PSCC Range | Notes |
|---|---|---|
| DNO urban cable supply (TN-S) | 3–15 kA at consumer intake | Urban underground network — low Ze |
| DNO suburban/rural overhead (TN-C-S) | 1–8 kA | Higher Ze on overhead lines |
| On-site generator (400kVA, uk=6%) | ~10 kA at LV terminals | Reduces rapidly with cable distance |
| UPS output (online double conversion) | 1–3× rated current | UPS limits fault current — critical for downstream device sizing |
| Solar PV inverter (grid-tied) | Varies — inverter current limited | PV contribution usually < 2× rated current |

**UPS-fed circuits deserve special attention:** A UPS output is current-limited by the UPS design. Standard MCBs with magnetic trip thresholds of 5–10× In may never reach their instantaneous trip current. These circuits require careful coordination using either a lower-In device, a dedicated UPS-rated MCB, or current-limiting fuses.
