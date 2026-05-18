# Prospective Short-Circuit Current (PSCC) — Determination Under KS 1700:2018

> **Verification note:** This file is authored as a draft-from-bs7671-derivative.
> KS 1700:2018 §312 adopts BS 7671 §313.1 substantially via KS Annex E.
> KPLC declared PFC values and the Letter of Information enquiry process
> are Kenya-specific. Promote `verification_status` once verified
> clause-by-clause against the published KS 1700:2018 PDF.

How to obtain or calculate the Prospective Short-Circuit Current at any
point in a Kenyan installation. PSCC governs switchgear breaking
capacity selection, cable adiabatic checks, and selectivity studies.

---

## Kenya supply context

In Kenya, PSCC at the intake is determined by **KPLC declared values**
rather than by engineer calculation from a known transformer. The
process for obtaining the value:

1. **Stamped Letter of Information.** When KPLC issues a service
   connection, the consumer receives a Letter of Information stamped
   with declared Ze and declared PFC at the cutout. This is the
   primary source.
2. **Enquiry to KPLC Regional Engineering office.** For non-domestic
   supplies — particularly industrial and large commercial — engineers
   should write to the KPLC Regional Engineering office quoting the
   site address and proposed MD. The office returns the declared PFC
   on letterhead. Typical response: 10–20 working days.
3. **Measurement at the origin** after supply is energised — the ground
   truth. KPLC declared values are typically conservative.

### Typical KPLC declared PFC values

| Supply type | Typical declared PFC at cutout |
|---|---|
| Single-phase domestic, rural overhead (60 A) | ~6 kA |
| Single-phase domestic, urban metro (100 A, TN-C-S) | ~9.8 kA |
| Three-phase industrial small (200 A) | ~16 kA |
| Three-phase industrial large (≥ 800 A, substation-adjacent) | ~25 kA |
| Dedicated transformer (consumer-owned) | calculate from transformer data |

These values guide initial MCB / MCCB Icn selection. Always confirm
with the KPLC-stamped Letter of Information before finalising.

---

## What PSCC is

PSCC is the maximum RMS symmetrical short-circuit current that would
flow at a specified point in the installation if a bolted (zero-impedance)
short circuit occurred at that point. It is the **worst case** fault
current — real fault currents are typically lower due to arc resistance.

PSCC determines:
- **Switchgear selection** — device's Icu ≥ PSCC at the point of installation per KS §434.5.1 (adopts BS verbatim)
- **Cable adiabatic check** — cable must survive PSCC for the device's clearing time per KS §434.5.2
- **Selectivity coordination** — PSCC at each level determines which devices can discriminate

---

## Symbols and units

| Symbol | Meaning |
|---|---|
| **Ipf** | Prospective fault current (general) |
| **PSCC / Isc** | Prospective Short-Circuit Current (phase-to-phase or three-phase) |
| **PEFC** | Prospective Earth Fault Current (phase-to-earth) |
| **Icu** | Ultimate breaking capacity of a device (kA) |
| **Ics** | Service short-circuit breaking capacity (typically 0.5 to 1.0 × Icu) |

Units: kA RMS symmetrical.

---

## Where to obtain PSCC in Kenya

### Option 1 — KPLC declared values (primary source)

- **Domestic + small commercial:** the stamped Letter of Information delivered with the supply connection contains declared Ze + PFC. Retain the original; copy it to the project file.
- **Non-domestic:** write to the KPLC Regional Engineering office (Nairobi Region, Mombasa Region, Kisumu Region, Nakuru Region, etc.) quoting site address + Wayleave reference + proposed MD. The office returns the declared PFC on letterhead.

### Option 2 — Measure at the origin

After supply is energised, measure PSCC at the cutout with a calibrated
high-current loop impedance tester. Use a KENAS-traceable calibrated
instrument.

Limitations: available only after supply is live; reading varies with
system loading + temperature; test current can trip upstream devices.

### Option 3 — Calculate from transformer data

For consumer-owned transformers (common on large industrial sites with
dedicated KPLC supply, or off-grid installations with diesel generation):

```
PSCC_transformer_secondary = Sn / (√3 × Un × Z_pu)

Where:
  Sn   = transformer rated power (kVA)
  Un   = secondary nominal voltage (kV, line-to-line; 0.415 kV for Kenya)
  Z_pu = per-unit impedance (typical 4% to 6%)
```

**Worked example — 1000 kVA transformer, 5% Z, 415V secondary**:
```
PSCC = 1000 / (√3 × 0.415 × 0.05)
     = 1000 / 0.0359
     ≈ 27.8 kA at the secondary terminals
```

This is the maximum possible; actual fault at downstream points is
reduced by cable + busbar + switchgear impedance.

---

## Calculating PSCC at downstream points

PSCC decreases as you move away from the supply due to cable + busbar
impedance:

```
PSCC_point = U / (√3 × Z_total)        (three-phase fault, U = 415 V line-to-line in Kenya)
PSCC_point = U0 / Z_total              (single-phase fault, U0 = 240 V phase-to-neutral in Kenya)
```

Where `Z_total` is the impedance from supply to fault point including
transformer impedance, service cable, distribution cable, busbar, and
switchgear contact resistance.

For simplified calculation:

```
Z_cable = √( (R_per_m × L)² + (X_per_m × L)² )
```

Cable R and X per metre values for copper XLPE multi-core (KS Annex E
adopts BS Appendix 4 verbatim):

| Size (mm²) | R (mΩ/m) | X (mΩ/m) |
|---|---|---|
| 2.5 | 7.41 | 0.10 |
| 4 | 4.61 | 0.094 |
| 6 | 3.08 | 0.090 |
| 10 | 1.83 | 0.085 |
| 16 | 1.15 | 0.082 |
| 25 | 0.727 | 0.084 |
| 50 | 0.387 | 0.080 |
| 95 | 0.193 | 0.077 |
| 240 | 0.0754 | 0.075 |

For runs under 50 m using cable ≤ 50 mm², reactance is negligible and
`Z ≈ R`. For longer runs or larger cables, include X.

---

## Worked example — Kenyan commercial installation

**Setup:**
- KPLC dedicated transformer 800 kVA, 5% Z, 415V secondary, TN-C-S
- 30 m of 240 mm² XLPE/SWA from KPLC substation to MSB
- 40 m of 70 mm² XLPE/SWA from MSB to SDB-L1
- 60 m of 6 mm² T+E from SDB-L1 to a typical socket

**Step 1 — PSCC at transformer secondary:**
```
PSCC_tr = 800 / (√3 × 0.415 × 0.05) ≈ 22.3 kA
```

**Step 2 — Add 30 m of 240 mm² SWA:**
```
R = 0.0754 mΩ/m × 30 = 2.26 mΩ
X = 0.075 mΩ/m × 30 = 2.25 mΩ
Z_cable = √(2.26² + 2.25²) ≈ 3.19 mΩ

Z_tr (approximate from PSCC):  Z_tr = 240 / 22300 ≈ 10.76 mΩ
Z_total = 10.76 + 3.19 = 13.95 mΩ
PSCC_MSB ≈ 240 / 0.01395 ≈ 17.2 kA
```

**Step 3 — Add 40 m of 70 mm² SWA:**
```
R = 0.268 × 40 = 10.72 mΩ
X = 0.077 × 40 =  3.08 mΩ
Z_cable = √(10.72² + 3.08²) ≈ 11.15 mΩ

Z_total = 13.95 + 11.15 = 25.10 mΩ
PSCC_SDB ≈ 240 / 0.02510 ≈ 9.56 kA
```

**Step 4 — Add 60 m of 6 mm² T+E (single-phase, go + return):**
```
R = 3.08 × 60 × 2 = 369.6 mΩ
X negligible at this size + length

Z_total = 25.10 + 369.6 = 394.7 mΩ
PSCC_socket ≈ 240 / 0.3947 ≈ 608 A
```

**Conclusion:**
- MSB switchgear needs Icu ≥ 17.2 kA → specify 25 kA breakers
- SDB-L1 needs Icu ≥ 9.6 kA → specify 10 kA breakers
- Final-circuit MCB needs Icu ≥ 0.6 kA → standard 6 kA MCB is more than adequate

---

## Three-phase vs single-phase faults

- Three-phase bolted fault gives the **highest current** at the supply transformer.
- Single-phase phase-to-neutral fault is what is calculated for cable-end PSCC at outlets.
- Phase-to-earth fault uses Zs (different impedance path through CPC) — generally lower than phase-to-neutral.

**Design rule:** use the worst case for switchgear sizing — three-phase
fault at the MSB, single-phase fault at the final circuit cable end.

---

## Common errors in Kenya practice

1. **Using KPLC declared PFC throughout the installation** — leads to oversized downstream switchgear. PSCC decreases with cable run.
2. **Specifying Icn without checking the KPLC Letter of Information** — device may be undersized; will not interrupt fault safely.
3. **Ignoring cable X (reactance)** — significant for cables ≥ 95 mm² or runs > 50 m.
4. **Using R at 20°C** — should use R at expected operating temperature (70 or 90°C, ~20–25% higher).
5. **Confusing PSCC with PEFC** — different impedance paths, different applications.
6. **Assuming PFC unchanged after KPLC network upgrade** — declared PFC can rise materially after KPLC adds capacity. Re-confirm at major refurbishments.
7. **Off-grid installations with diesel generator only** — generator subtransient impedance gives lower PSCC than KPLC equivalent. Treat the generator like a small consumer-owned transformer.

---

## PSCC software tools

For complex networks (multiple sources, parallel paths, motor contribution),
hand calculation becomes impractical. Tools used in Kenya practice:

- **ETAP** — used by large industrial / utility consultancies in Kenya
- **DigSILENT PowerFactory** — KPLC + KETRACO network studies
- **Amtech ProDesign** — BS 7671 / KS 1700 focused, integrates load schedule + protection coordination
- **EcoStruxure Power Design** (Schneider) — common with KEBS-certified Schneider switchgear

For most KS 1700 designs a spreadsheet using the formulas above is sufficient.

---

## See also

- `KS1700/terminology.md` — KPLC + Wayleave + EPRA vocabulary
- `KS1700/compliance-checklist.md` — §312 + §434 PSCC checklist items
- `KS1700/protective-device-types.md` — Icn vs PSCC selection
- `KS1700/earthing-systems-explained.md` — Ze + PEFC (related but distinct from PSCC)
- `BS7671/pscc-determination.md` — parent BS text adopted by KS Annex E
