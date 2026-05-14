# IEC 60364 Terminology

Definitions for abbreviations used throughout IEC 60364 and the machine-readable
data files in this folder. An agent reading standards data needs this glossary to
interpret variables correctly.

---

## Voltage symbols

| Symbol | Name | Typical value | Meaning |
|--------|------|---------------|---------|
| **U₀** | Nominal voltage to earth | 230 V | Nominal AC RMS voltage between any line conductor and earth (neutral). The driving voltage in fault calculations. For a 230/400V system, U₀ = 230V. |
| **U** | Nominal line-to-line voltage | 400 V (3-phase) | Nominal AC RMS voltage between any two line conductors. U = √3 × U₀. |
| **Un** | Nominal supply voltage | 230 V / 400 V | The declared system voltage — same as U₀ for single-phase reference. |
| **Uc** | Maximum continuous operating voltage (SPD) | 275 V typical | The AC RMS voltage an SPD can sustain indefinitely without operating. Must be ≥ 1.1 × U₀ (≥ 253V for 230V systems). |
| **Up** | Voltage protection level (SPD) | 1.5 kV typical | Peak voltage passed through by the SPD during a surge event. Must be ≤ Uw of the protected equipment. |
| **Uw** | Rated impulse withstand voltage | 1.5 / 2.5 / 4 / 6 kV | Peak impulse voltage a piece of equipment can survive. Defined by installation category I–IV per IEC 60664-1. |
| **Uoc** | Open-circuit voltage of test generator | — | Used in insulation resistance and earth fault loop tests during verification (Part 6). |

---

## Current symbols

| Symbol | Name | Units | Meaning |
|--------|------|-------|---------|
| **Ib** | Design current of the circuit | A | The maximum sustained current the circuit will carry under normal use, after all demand diversity is applied. Calculated by the designer. |
| **In** | Nominal rated current of the protective device | A | The rated current of the MCB, RCBO, or fuse. Standard IEC sizes: 6, 10, 16, 20, 25, 32, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630 A. |
| **Iz** | Continuous current-carrying capacity of the cable | A | The current the cable can carry indefinitely without exceeding its insulation temperature limit, **after all correction factors have been applied** (Iz = It × Ca × Cg × Ci × …). |
| **It** | Tabulated current-carrying capacity | A | The "headline" current-carrying capacity from Annex B tables, before any correction factors. Read from the appropriate table for cable type, size, and installation method. |
| **I₂** | Effective operating current of the device | A | The current at which the protective device is guaranteed to operate within the conventional time period. I₂ = 1.45 × In for MCBs (IEC 60898); I₂ = 1.6 × In for gG fuses (IEC 60269). |
| **I₁** | Conventional non-tripping current | A | The current the device must not trip at within the conventional time. I₁ = 1.13 × In for MCBs. |
| **Ia** | Instantaneous magnetic trip current | A | The current at which the MCB's magnetic element trips instantaneously. 3–5 × In for Type B, 5–10 × In for Type C, 10–20 × In for Type D (see IEC 60898). Used to determine maximum Zs. |
| **IΔn** | Rated residual operating current (RCD) | A | The earth leakage current at which an RCD is guaranteed to trip. Standard values: 6 mA, 10 mA, 30 mA, 100 mA, 300 mA, 500 mA, 1 A. |
| **IΔn0** | Rated non-operating current (RCD) | A | The current at which an RCD must NOT trip. Typically 0.5 × IΔn. |
| **Iimp** | Impulse current, 10/350 μs waveform | kA | Test current for Type 1 SPDs simulating a direct lightning flash. |
| **In (SPD)** | Nominal discharge current, 8/20 μs waveform | kA | Test current for Type 2 SPDs simulating conducted/induced surges. |
| **Isc** | Prospective short-circuit current | kA | The maximum symmetrical RMS fault current that would flow at a given point under bolted three-phase fault conditions. Devices must have breaking capacity ≥ Isc. |
| **If** | Earth fault current | A | Current flowing during a line-to-earth fault. Used in ADS verification: If = U₀ / Zs. |

---

## Impedance symbols

| Symbol | Name | Units | Meaning |
|--------|------|-------|---------|
| **Zs** | Earth fault loop impedance at the circuit | Ω | Total impedance of the complete fault loop: supply transformer → line conductor → fault point → protective conductor → MET → neutral conductor → transformer. Zs determines fault current and disconnection time. |
| **Ze** | External earth fault loop impedance | Ω | Zs measured at the origin of the installation (ahead of any consumer wiring). Obtained from the supply authority or measured on site. |
| **Zpe** | Impedance of the protective conductor | Ω | Resistance of the circuit protective conductor (CPC). Zs ≈ Ze + R1 + Rpe for simple circuits. |
| **R1** | Resistance of the line conductor | Ω | Line conductor resistance from origin to load end and back. |
| **R2 / Rpe** | Resistance of the protective conductor (CPC) | Ω | CPC resistance from origin to load end. |
| **(R1 + R2)** | Total conductor loop resistance | Ω/m | The sum of line + CPC resistance per metre, from conductor resistance tables. Used in Zs = Ze + (R1+R2) × L. |
| **Zs_max** | Maximum permissible earth fault loop impedance | Ω | Calculated as U₀ / Ia. If measured Zs exceeds this, the protective device will NOT trip within the required time. |
| **Ra** | Resistance of earth electrode and connection (TT) | Ω | For TT systems: RCD IΔn × Ra ≤ 50V is the design check. Ra is the measured electrode resistance. |
| **R** | Resistance | Ω | DC resistance of a conductor. Increases with temperature: R_T = R_20 × [1 + α × (T - 20)]. |
| **X** | Reactance | Ω | Inductive reactance. Significant in cables ≥ 50 mm² and in busbar trunking. Typically 0.07–0.10 mΩ/m for large cables. |
| **Z** | Impedance | Ω | √(R² + X²). Use Z for accurate fault calculations; for small cables R ≈ Z. |

---

## Cable parameters

| Symbol | Name | Units | Meaning |
|--------|------|-------|---------|
| **S** | Cross-sectional area of conductor | mm² | Nominal conductor area. Standard IEC sizes: 0.75, 1, 1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240, 300, 400, 500, 630 mm². |
| **θc** | Maximum conductor temperature (operating) | °C | The rated maximum conductor temperature: PVC = 70°C, XLPE/EPR = 90°C, MICC bare = 105°C, MICC with PVC sheath = 70°C. |
| **θa** | Ambient temperature | °C | The temperature of the surrounding air or soil. IEC reference values: 30°C in air, 20°C in soil. |
| **k** | Conductor k-factor (adiabatic) | — | Material constant for adiabatic cable sizing check. Depends on conductor and insulation material. See fault-current.json. |
| **It** | Tabulated current rating | A | From Annex B of IEC 60364-5-52 — the current before corrections. |
| **Iz** | Corrected current rating | A | Iz = It × Ca × Cg × Ci × Cs × Cd (all applicable correction factors applied). |
| **mV/A/m** | Voltage drop rate | mV/(A·m) | Voltage drop in millivolts per ampere of current per metre of circuit length. Used to calculate actual voltage drop: ΔU = mV/A/m × Ib × L / 1000. |

---

## Correction factors

| Symbol | Name | Description |
|--------|------|-------------|
| **Ca** | Ambient temperature factor | Corrects tabulated rating (at 30°C air / 20°C soil) to actual ambient temperature. |
| **Cg** | Grouping factor | Corrects for mutual heating when multiple cables are installed together. |
| **Ci** | Thermal insulation factor | Corrects for cables embedded in or close to thermal insulation. |
| **Cs** | Soil thermal resistivity factor | Corrects buried cable ratings for soil thermal resistivity different from reference 1.0 K·m/W. |
| **Cd** | Depth of burial factor | Corrects buried cable ratings for depth different from reference 0.7 m (direct) or 0.5 m (in duct). |
| **Cf** | Harmonic correction factor | Corrects for triplen harmonic currents in the neutral conductor of three-phase systems. |

---

## Earthing system codes

| Code | System | Description |
|------|--------|-------------|
| **TN** | Terra-Neutral | Supply earth is taken from the transformer neutral. Includes TN-S, TN-C, TN-C-S. |
| **TN-S** | Separate Neutral and Earth | Neutral (N) and protective earth (PE) are separate throughout. Lowest interference risk. |
| **TN-C** | Combined N and PE | Single PEN conductor carries both neutral current and protective earth. Not permitted for new consumer installations. |
| **TN-C-S** | Combined then Separate (PME) | PEN conductor in the supply network, split to N and PE at the consumer's main earthing terminal. Dominant in UK, common across Africa and Asia. |
| **TT** | Terra-Terra | Supply neutral is earthed at the transformer; consumer has separate independent earth electrode. Common in rural areas, older networks. |
| **IT** | Isolated Terra | Supply neutral is isolated from earth (or impedance-earthed). First fault does not cause disconnection. Used in medical locations (Group 2), offshore, some industrial processes. |
| **PME** | Protective Multiple Earthing | UK/IEC term for the TN-C-S arrangement where the PEN conductor is earthed at multiple points. |
| **MET / MEB** | Main Earthing Terminal / Main Equipotential Bonding | The central connection point inside the installation where PE, bonding conductors, and earth electrode are connected. |
| **CPC** | Circuit Protective Conductor | The green-yellow conductor within a wiring system. Connects exposed-conductive-parts to the MET. Same as "earth wire" colloquially. |
| **ECP** | Exposed Conductive Part | Metal parts of equipment that can become live if insulation fails. Must be connected to CPC. |
| **ECP** | Extraneous Conductive Part | Metal parts not part of the electrical installation but which could introduce an earth potential. Must be connected to MET via bonding. |

---

## Protection system abbreviations

| Abbreviation | Full name | Meaning |
|-------------|-----------|---------|
| **SELV** | Separated Extra-Low Voltage | AC ≤ 50V, DC ≤ 120V. Circuit separated from earth and from other circuits. No shock risk from direct or indirect contact. |
| **PELV** | Protective Extra-Low Voltage | AC ≤ 50V, DC ≤ 120V. Like SELV but one point or the enclosure IS earthed. Mainly used where earthing is needed for functional reasons. |
| **FELV** | Functional Extra-Low Voltage | AC or DC at ELV for functional (not safety) reasons. Must meet shock protection requirements of the higher-voltage supply feeding it. Not a protective measure. |
| **ADS** | Automatic Disconnection of Supply | The primary protective measure — a device automatically disconnects the supply within a specified time when an earth fault occurs. |
| **RCD / RCCB** | Residual Current Device / Residual Current Circuit Breaker | Detects leakage current to earth (neutral-live imbalance). Trips at IΔn (typically 30 mA). |
| **RCBO** | Residual Current Circuit Breaker with Overcurrent protection | Combined MCB + RCD in a single device. |
| **MCB** | Miniature Circuit Breaker | Overload and short-circuit protection in final circuits. Types B, C, D per IEC 60898. |
| **MCCB** | Moulded Case Circuit Breaker | Larger capacity version of MCB, adjustable trip settings. Used for submains. |
| **HBC / HRC** | High Breaking Capacity / High Rupturing Capacity fuse | Cartridge fuse with high fault interrupting capacity. gG type for general use, aM for motor protection. |
| **ACB** | Air Circuit Breaker | Large capacity breaker (typically > 800A) with electronic trip units. LSIG adjustable settings. |
| **SPD** | Surge Protective Device | Limits transient overvoltages. Type 1 (lightning), Type 2 (induced surges), Type 3 (point of use). |
| **AFDD** | Arc Fault Detection Device | Detects arcing faults from cable damage or loose connections. Required in some applications per AMD2:2018 proposals. |
| **LPS** | Lightning Protection System | External lightning protection (air terminals, down conductors, earth termination) per IEC 62305. |
| **IPDS** | Isolated Power Distribution System | IT system used in medical locations Group 2. Insulation monitoring device (IMD) alerts on first fault. |

---

## Key formula reference

```
Fundamental Rule (Overcurrent, Clause 433):
  Ib ≤ In ≤ Iz                 — Device current must sit between design current and cable capacity

ADS check — TN system (Clause 411.4):
  Zs × Ia ≤ U₀               — Earth fault loop impedance × instantaneous trip current ≤ supply voltage

ADS check — TT system (Clause 411.5):
  Ra × IΔn ≤ 50V              — Electrode resistance × RCD trip current ≤ 50V (contact voltage limit)

Voltage drop (Annex G):
  ΔU = (mV/A/m × Ib × L) / 1000   — Drop in volts across a circuit of length L at design current Ib

Adiabatic check (Clause 434.5):
  I²t ≤ k²S²                  — Energy let-through ≤ conductor thermal withstand
  or: S ≥ √(I²t) / k          — Minimum conductor cross-section to withstand fault energy

Corrected cable rating:
  Iz = It × Ca × Cg × Ci × Cs × Cd   — Apply all applicable factors to tabulated value
```
