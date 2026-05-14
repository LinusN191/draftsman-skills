# BS 7671 Terminology

Definitions for the abbreviations used throughout BS 7671 and the JSON
data files in this folder. An agent reading the standards data needs
this glossary to interpret variables correctly.

---

## Voltage symbols

| Symbol | Name | Typical value | Meaning |
|--------|------|---------------|---------|
| **U₀** | Nominal voltage to earth | 230 V (UK) | RMS voltage between live conductor and earth at the supply origin. Used as the driving voltage in fault calculations. |
| **U** | Nominal line-to-line voltage | 400 V (3-phase) | RMS voltage between any two line conductors. |
| **Un** | Nominal supply voltage | 230 V / 400 V | The declared system voltage. |
| **Uc** | Maximum continuous operating voltage | 275 V typical | The RMS voltage an SPD can sustain continuously without operating. Must be ≥ 1.1 × U₀. |
| **Up** | Voltage protection level | 1.5 kV typical | The peak voltage an SPD allows to pass through to downstream equipment during a surge. Must be ≤ Uw of protected equipment. |
| **Uw** | Rated impulse withstand voltage | 1.5 / 2.5 / 4 / 6 kV | The peak impulse voltage a piece of equipment can survive without damage. Categorised I to IV (see `reg443-spd.json`). |
| **Uoc** | Open-circuit voltage of test source | 250 V (insulation test) | Used in insulation resistance measurement per Part 6. |

---

## Current symbols

| Symbol | Name | Units | Meaning |
|--------|------|-------|---------|
| **Ib** | Design current of the circuit | A | The maximum sustained current the circuit will carry under normal use, after diversity is applied. Calculated by the designer. |
| **In** | Nominal current of the protective device | A | The rated current of the MCB, fuse, RCBO. Standard sizes: 6, 10, 16, 20, 25, 32, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250 A. |
| **Iz** | Continuous current-carrying capacity | A | The current the cable can carry indefinitely without exceeding its insulation temperature limit, AFTER all correction factors are applied. |
| **It** | Tabulated current-carrying capacity | A | The "headline" current from Appendix 4 tables, before correction factors. |
| **I₂** | Operating current of the device | A | The current at which the protective device is guaranteed to operate within conventional time. I₂ = 1.45 × In for MCBs (BS EN 60898); 1.6 × In for HRC fuses (BS 88). |
| **I₁** | Non-tripping current | A | The current the device must NOT trip at within conventional time. 1.13 × In for MCBs. |
| **Ia** | Instantaneous magnetic trip current | A | The fault current at which the MCB's magnetic trip operates without intentional delay. 5×In for Type B, 10×In for Type C, 20×In for Type D. |
| **IΔn** | Rated residual operating current | A | The earth fault current at which an RCD is guaranteed to trip. Standard sizes: 0.01, 0.03, 0.1, 0.3, 0.5, 1.0 A. |
| **Iimp** | Impulse current (10/350 μs) | kA | Test current for Type 1 SPDs simulating direct lightning. |
| **In (SPD)** | Nominal discharge current (8/20 μs) | kA | Test current for Type 2/3 SPDs simulating induced surges. |
| **PSCC / Ipf** | Prospective short-circuit current | kA | The maximum RMS symmetrical fault current that would flow at a given point in the installation. |
| **PEFC** | Prospective earth fault current | kA | The maximum RMS earth fault current at a given point. PEFC ≤ PSCC. |

---

## Impedance symbols

| Symbol | Name | Units | Meaning |
|--------|------|-------|---------|
| **Zs** | Earth fault loop impedance at the circuit | Ω | Total impedance of the loop: supply transformer → line conductor → fault → CPC → MET → transformer neutral. Determines fault current and disconnection time. |
| **Ze** | External earth fault loop impedance | Ω | Zs measured at the origin of the installation (before any consumer wiring). Provided by the DNO or measured during installation. |
| **Zdb** | Earth loop impedance at the distribution board | Ω | Zs at the DB feeding the circuit — used as a starting point for downstream calculations. |
| **R1** | Resistance of the line conductor | Ω | Line conductor resistance of the circuit, end-to-end. |
| **R2** | Resistance of the CPC | Ω | Circuit Protective Conductor resistance, end-to-end. |
| **R1 + R2** | Total circuit conductor resistance | Ω | Used in Zs = Ze + (R1+R2). For a 2.5/1.5 T&E cable: R1+R2 ≈ 19.5 mΩ/m. |
| **Zs_max** | Maximum permissible Zs | Ω | Look-up value from Tables 41.2 / 41.3. If measured Zs > Zs_max, the device will NOT trip in the required time. |
| **R** | Resistance | Ω | DC resistance of a conductor. Increases with temperature. |
| **X** | Reactance | Ω | Inductive reactance. Significant in cables ≥ 50mm² and at high frequencies. |
| **Z** | Impedance | Ω | √(R² + X²). Used in AC fault calculations. |

---

## Cable parameters

| Symbol | Name | Units | Meaning |
|--------|------|-------|---------|
| **S** | Conductor cross-sectional area | mm² | The "cable size" — 1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240, 300 mm². |
| **mV/A/m** | Voltage drop coefficient | mV per A per m | Tabulated value used to calculate voltage drop. Already includes both go and return conductors. |
| **k** | Cable adiabatic constant | A·s½/mm² | Material/insulation constant used in S ≥ √(I²t)/k. 115 for copper/PVC, 143 for copper/XLPE. |
| **tp** | Maximum conductor temperature | °C | 70°C for PVC, 90°C for XLPE/EPR. The temperature the conductor can run at continuously. |

---

## Correction factor symbols

| Symbol | Name | Meaning |
|--------|------|---------|
| **Ca** | Ambient temperature correction | Reduces Iz when ambient temperature > 30°C (in air) or > 20°C (in ground). |
| **Cg** | Grouping correction | Reduces Iz when multiple circuits share the same containment. |
| **Ci** | Thermal insulation correction | Reduces Iz when cable is in or near thermal insulation. |
| **Cd** | Depth of burial correction | Adjusts Iz for buried cables at non-reference depth. |
| **Cs** | Soil thermal resistivity correction | Adjusts Iz for buried cables in non-standard soil. |

**Application:** Iz_corrected = It × Ca × Cg × Ci × Cd × Cs

---

## System earthing classifications

| Code | Name | Description |
|------|------|-------------|
| **TN-S** | Terra-Neutral Separate | Separate neutral and earth from the supply transformer. Earth conductor is dedicated. |
| **TN-C** | Terra-Neutral Combined | Combined neutral-earth (PEN) throughout. Not permitted in consumer installations. |
| **TN-C-S** | Combined then Separate | PEN from transformer to consumer's intake, then separated into N and PE. Most common UK supply (PME — Protective Multiple Earthing). |
| **TT** | Terra-Terra | Independent earth electrodes at supply and consumer. Common in rural areas. |
| **IT** | Isolated-Terra | Live parts isolated from earth, or earthed via high impedance. Used in healthcare, marine, mining. |

See `earthing-systems-explained.md` for full detail.

---

## Other abbreviations

| Code | Expansion |
|------|-----------|
| **ADS** | Automatic Disconnection of Supply |
| **AFDD** | Arc Fault Detection Device |
| **CDM** | Construction (Design and Management) Regulations 2015 |
| **CPC** | Circuit Protective Conductor — the earth wire of a circuit |
| **DB** | Distribution Board |
| **DNO** | Distribution Network Operator (electricity supply company) |
| **EICR** | Electrical Installation Condition Report |
| **EPR** | Ethylene Propylene Rubber (thermosetting insulation) |
| **FLC** | Full Load Current |
| **HRC** | High Rupturing Capacity (fuse) |
| **LSZH / LSF** | Low Smoke Zero Halogen / Low Smoke and Fumes |
| **MCB** | Miniature Circuit Breaker (BS EN 60898) |
| **MCCB** | Moulded Case Circuit Breaker (BS EN 60947-2) |
| **MD** | Maximum Demand |
| **MET** | Main Earthing Terminal |
| **MICC** | Mineral Insulated Copper-Clad (cable) |
| **MSB** | Main Switchboard |
| **OSG** | On-Site Guide (IET publication) |
| **PE** | Protective Earth |
| **PEN** | Combined Protective and Neutral conductor |
| **PME** | Protective Multiple Earthing (TN-C-S) |
| **RCBO** | Residual Current Breaker with Overcurrent protection |
| **RCD** | Residual Current Device |
| **SDB** | Sub-Distribution Board |
| **SPD** | Surge Protective Device |
| **SWA** | Steel Wire Armoured (cable) |
| **T&E** | Twin and Earth (BS 6004 flat cable) |
| **THD** | Total Harmonic Distortion |
| **UPS** | Uninterruptible Power Supply |
| **VFD** | Variable Frequency Drive |
| **XLPE** | Cross-Linked Polyethylene (thermosetting insulation) |
| **ZSI** | Zone Selective Interlocking |

---

## Key formulas at a glance

| Formula | Use |
|---------|-----|
| `Zs = Ze + (R1 + R2)` | Earth fault loop impedance at end of circuit |
| `Vd = (mVAm × Ib × L) / 1000` | Voltage drop (single-phase) |
| `Ib ≤ In ≤ Iz` | Fundamental Rule of cable sizing |
| `I2 ≤ 1.45 × Iz` | Overload coordination check |
| `S ≥ √(I²t) / k` | Adiabatic equation — cable survives fault |
| `Iz_corrected = It × Ca × Cg × Ci × Cd` | Apply all correction factors |
| `MF = LLMF × LSF × LMF × RSMF` | Lighting maintenance factor (CIBSE) |
