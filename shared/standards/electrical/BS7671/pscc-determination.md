# Prospective Short-Circuit Current (PSCC) — Determination

How to obtain or calculate the Prospective Short-Circuit Current at any
point in an installation. PSCC governs switchgear breaking capacity
selection, cable adiabatic checks, and selectivity studies.

---

## What it is

PSCC is the maximum RMS symmetrical short-circuit current that would
flow at a specified point in the installation if a bolted (zero-impedance)
short circuit occurred at that point.

It is the **worst case** fault current. Real fault currents are typically
lower due to arc resistance, but design uses PSCC to ensure equipment
can interrupt the maximum possible fault.

PSCC determines:
- **Switchgear selection**: device's Icu ≥ PSCC at the point of installation (Reg 434.5.1)
- **Cable adiabatic check**: cable must survive PSCC for the device's clearing time (Reg 434.5.2)
- **Selectivity coordination**: PSCC at each level determines which devices can discriminate

---

## Symbols and units

| Symbol | Meaning |
|--------|---------|
| **Ipf** | Prospective fault current (general) |
| **PSCC / Isc** | Prospective Short-Circuit Current — phase-to-phase or three-phase fault |
| **PEFC** | Prospective Earth Fault Current — phase-to-earth fault |
| **Icu** | Ultimate breaking capacity of a device (kA) |
| **Ics** | Service short-circuit breaking capacity (typically 0.5 to 1.0 × Icu) |

Units: kA RMS symmetrical.

---

## Where to obtain PSCC

### Option 1 — DNO supply data

The Distribution Network Operator can provide:
- PSCC at the meter/cut-out
- Ze (external earth fault loop impedance)
- Maximum allowed import current
- Phase rotation

**How to request**: write to the DNO with site address and proposed
installation MD. Most DNOs have an online form. Typical response: 5–15
working days. Some DNOs charge a small fee.

**Typical values from DNOs (rough guide — always confirm)**:

| Supply type | Typical PSCC at cut-out |
|-------------|--------------------------|
| Domestic single-phase 100A TN-C-S | 1.0 to 6.0 kA |
| Domestic three-phase 100A | 3.0 to 12 kA |
| Small commercial 200A TN-C-S | 5.0 to 15 kA |
| Commercial 800A TN-C-S | 10 to 25 kA |
| Industrial 1600A intake | 16 to 40 kA |
| Dedicated transformer 1000 kVA | calculate from transformer data |

### Option 2 — Measure at the origin

After supply is energised, measure PSCC at the cut-out with a calibrated
loop impedance tester capable of high-current testing. This is the
ground truth — DNO calculated values are often conservative.

Limitations:
- Available only after supply is live
- Reading varies with system loading and temperature
- Test current can trip protective devices upstream if not careful

### Option 3 — Calculate from transformer data

For a dedicated transformer (consumer-owned or DNO-dedicated):

```
PSCC_transformer_secondary = Sn / (√3 × Un × Z_pu)

Where:
  Sn   = transformer rated power (kVA)
  Un   = secondary nominal voltage (kV, line-to-line)
  Z_pu = per-unit impedance (typical 4% to 6% for distribution transformers)
```

**Worked example — 1000 kVA transformer, 5% Z**:
```
PSCC = 1000 / (√3 × 0.4 × 0.05)
     = 1000 / 0.0346
     = 28,868 A
     ≈ 28.9 kA at the secondary terminals
```

This is the maximum possible — actual fault at downstream points is
reduced by the impedance of cables, busbars, and other equipment in the
fault path.

---

## Calculating PSCC at downstream points

PSCC decreases as you move away from the supply due to cable and busbar
impedance. The calculation at any point:

```
PSCC_point = U / (√3 × Z_total)        (for 3-phase fault)
PSCC_point = U0 / Z_total              (for single-phase fault — to neutral)
```

Where `Z_total` is the impedance from the supply transformer to the
fault point, including:
- Supply transformer impedance
- Service cable impedance
- Distribution cable impedance
- Busbar impedance
- Switchgear contact impedance

For simplified calculation, compute the cumulative cable impedance:

```
Z_cable = √( (R_per_m × L)² + (X_per_m × L)² )
```

Most cable manufacturer data sheets list R and X per metre. For copper
XLPE multi-core:

| Size (mm²) | R (mΩ/m) | X (mΩ/m) |
|-----------|----------|----------|
| 2.5 | 7.41 | 0.10 |
| 4 | 4.61 | 0.094 |
| 6 | 3.08 | 0.090 |
| 10 | 1.83 | 0.085 |
| 16 | 1.15 | 0.082 |
| 25 | 0.727 | 0.084 |
| 35 | 0.524 | 0.080 |
| 50 | 0.387 | 0.080 |
| 70 | 0.268 | 0.077 |
| 95 | 0.193 | 0.077 |
| 120 | 0.153 | 0.076 |
| 185 | 0.099 | 0.075 |
| 240 | 0.0754 | 0.075 |

For runs under 50m using cable ≤ 50mm², reactance is negligible and
`Z ≈ R`. For longer runs or larger cables, include X.

---

## Worked example — full chain

**Setup:**
- DNO-supplied transformer 800 kVA, 5% Z, 400V secondary, TN-C-S
- 30m of 240mm² XLPE/SWA from substation to MSB
- 40m of 70mm² XLPE/SWA from MSB to SDB-L1
- 60m of 6mm² T&E from SDB-L1 to a typical socket

**Step 1 — PSCC at transformer secondary:**
```
PSCC_tr = 800 / (√3 × 0.4 × 0.05) = 23,094 A ≈ 23.1 kA
```

**Step 2 — Add 30m of 240mm² SWA:**
```
R = 0.0754 mΩ/m × 30 = 2.262 mΩ
X = 0.075 mΩ/m × 30 = 2.250 mΩ
Z_cable = √(2.262² + 2.250²) = 3.19 mΩ

Z_tr (approximate from PSCC):  Z_tr = 230 / 23094 ≈ 10 mΩ
Z_total = 10 + 3.19 = 13.19 mΩ
PSCC_MSB = 230 / 0.01319 ≈ 17,438 A ≈ 17.4 kA
```

**Step 3 — Add 40m of 70mm² SWA:**
```
R = 0.268 × 40 = 10.72 mΩ
X = 0.077 × 40 = 3.08 mΩ
Z_cable = √(10.72² + 3.08²) = 11.15 mΩ

Z_total = 13.19 + 11.15 = 24.34 mΩ
PSCC_SDB = 230 / 0.02434 ≈ 9,449 A ≈ 9.4 kA
```

**Step 4 — Add 60m of 6mm² T&E (single-phase):**
```
R = 3.08 × 60 × 2 (both go and return) = 369.6 mΩ
X negligible at this size and length

Z_total = 24.34 + 369.6 = 393.9 mΩ
PSCC_socket = 230 / 0.394 ≈ 584 A
```

**Conclusion:**
- MSB needs switchgear rated Icu ≥ 17.4 kA → specify 25 kA breakers
- SDB-L1 needs Icu ≥ 9.4 kA → specify 10 kA breakers
- Final circuit MCB needs Icu ≥ 0.6 kA → standard 6 kA MCB more than adequate

---

## Three-phase vs single-phase faults

- Three-phase bolted fault gives the **highest current** at the supply transformer
- Single-phase phase-to-neutral fault is what is calculated for cable-end PSCC at outlets
- Phase-to-earth fault uses Zs (different impedance path through CPC) — generally lower than phase-to-neutral

**Design rule**: use the worst case for switchgear sizing — typically
the three-phase fault at the MSB and the single-phase fault at the final
circuit cable end.

---

## Common errors

1. **Using supply PSCC throughout** — leads to oversized downstream switchgear. PSCC decreases with cable run.
2. **Ignoring cable X (reactance)** — error becomes significant for cables ≥ 95mm² or runs > 50m.
3. **Using R at 20°C** — should use R at expected operating temperature (typically 70 or 90°C, ~20-25% higher than 20°C).
4. **Not including switchgear contact resistance** — adds a few mΩ in MSBs, negligible in small DBs.
5. **Confusing PSCC (phase-to-phase) with PEFC (phase-to-earth)** — they have different impedance paths and different applications.
6. **Assuming DNO PSCC without confirmation** — DNO networks change. A "5 kA" PSCC may have risen to 15 kA after upstream upgrade.

---

## PSCC software tools

For complex networks (multiple sources, parallel paths, motor contribution),
hand calculation becomes impractical. Common tools used:

- **ETAP** — industry standard for large industrial studies
- **DigSILENT PowerFactory** — distribution and transmission focused
- **Amtech ProDesign** — UK BS 7671 focused, integrates load schedule and protection coordination
- **Trimble Tas** — UK building services
- **SKM PTW** — US-focused, common in oil/gas

For most BS 7671 designs, a spreadsheet using the formulas above is sufficient.
