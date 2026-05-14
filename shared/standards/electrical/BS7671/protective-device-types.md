# Protective Device Types

A guide to the device families used in UK low-voltage installations,
with selection guidance for typical applications.

---

## MCB — Miniature Circuit Breaker (BS EN 60898)

**Construction:** Thermal-magnetic. Thermal element for overload, magnetic element for short-circuit.

**Ratings**
- In: 6, 10, 13, 16, 20, 25, 32, 40, 50, 63, 80, 100, 125 A
- Breaking capacity (Icn): 3 kA, 4.5 kA, 6 kA, 10 kA, 15 kA, 25 kA
- Categories by instantaneous trip:
  - **Type B**: 3–5× In (default for resistive loads, general lighting, sockets)
  - **Type C**: 5–10× In (motor loads, fluorescent banks, LED with inrush, distribution circuits)
  - **Type D**: 10–20× In (transformers, X-ray, lift drives, large discharge lighting)
- Pole counts: SP, SP+N, DP, TP, TP+N, FP

**When to use**
- Final circuits in domestic and small commercial
- Lighting circuits (Type B for LED, Type C for older fluorescent banks)
- Cooker / shower circuits (Type B)
- Mechanical service circuits (Type C/D)

**When NOT to use**
- Circuits where RCD protection is required → use RCBO instead
- Fault levels above the device's Icn → use MCCB or HRC fuse
- Very large currents (> 125A) → MCCB
- Critical motor circuits with high inrush → check Type D vs soft-start

---

## RCBO — Residual Current Breaker with Overcurrent (BS EN 61009)

**Construction:** Combined MCB + RCD in one module. Provides overload, short-circuit, and earth-leakage protection.

**Ratings**
- In: same as MCB (6 to 125 A)
- IΔn: 10 mA, 30 mA, 100 mA, 300 mA
- Types: AC, A, F, B (see RCD types below)
- Same Icn ratings as MCBs

**When to use** — preferred device for modern final circuits
- All socket outlet circuits ≤ 32A (Reg 411.3.3 — mandatory 30mA RCD protection)
- Domestic lighting circuits (Reg 411.3.4 from AMD 2 — mandatory 30mA RCD)
- All circuits in bathrooms, swimming pools, saunas
- EV charging circuits (Type A or Type B per Reg 722)
- Outdoor circuits and circuits supplying mobile equipment

**Why prefer RCBO over RCD + MCB**
- Discrete protection per circuit — fault on one circuit doesn't trip others
- Smaller board footprint
- Simpler to test (one device per circuit)
- ~3× cost of MCB but justified by fault isolation and compliance

---

## RCD — Residual Current Device (BS EN 61008)

**Construction:** Earth-leakage detection only. No overcurrent protection. Always installed in series with an MCB or fuse for overcurrent.

**Ratings**
- IΔn: 10, 30, 100, 300, 500 mA, 1 A
- Types: AC, A, F, B (see RCD type selection below)
- Pole counts: DP (single phase + N), 4P (3-phase + N)
- S-type: time-delayed for selectivity (40–130 ms delay)

**When to use**
- Incoming protection at the consumer unit for groups of circuits (split-load board)
- Backup protection upstream of RCBOs (S-type for selectivity)
- Construction sites: 30mA on all socket outlets, 500mA on origin (Reg 704)

**When NOT to use**
- As the only device on a final circuit — needs overcurrent protection in series
- Where individual circuit isolation is required — RCBO per circuit is better

---

## RCD types

| Type | Detects | Use case |
|------|---------|----------|
| **AC** | Sinusoidal AC only | Legacy. Not recommended. Will fail to detect DC residual current. |
| **A** | AC + pulsating DC | Standard for modern installations. Required for electronic loads (PCs, single-phase inverters). |
| **F** | AC + pulsating DC + 1 kHz | Single-phase inverter loads (washing machines, single-phase heat pumps). |
| **B** | AC + DC + smooth DC + HF | Three-phase inverters, EV charging without built-in DC detection, three-phase solar, UPS. |

**Selection rule:** Match the RCD type to the load. Type AC RCD downstream of an EV charger will fail to detect a DC fault — illegal under Reg 722.

---

## HRC fuse — High Rupturing Capacity fuse (BS 88-3)

**Construction:** Sand-filled silver/copper element. Operates by element melting and arc extinction.

**Ratings**
- In: 6 to 1250 A common range
- Breaking capacity: typically 80 kA or 120 kA — much higher than MCBs
- Class: gG (general use), aM (motor only — provides only short-circuit protection)

**When to use**
- Submain protection where fault level exceeds MCB Icn
- Service heads (DNO supplies)
- Motor protection (in gG or aM class — aM only with overload relay)
- Where extreme reliability and minimum maintenance is required
- Industrial and utility installations

**Pros**
- Very high breaking capacity (80–120 kA standard)
- Inherently selective with downstream MCBs due to steep time-current curve
- Compact relative to MCCB
- Long service life — no mechanism to fail

**Cons**
- Single-use — must be replaced after operation
- Requires spare fuses on site
- I₂ factor of 1.6 (vs 1.45 for MCB) means more careful cable coordination
- Cannot be locked in OFF position for safe isolation

---

## MCCB — Moulded Case Circuit Breaker (BS EN 60947-2)

**Construction:** Industrial circuit breaker in a moulded case. Adjustable thermal-magnetic trip or electronic trip unit.

**Ratings**
- In: typically 16 to 3200 A (in frame sizes: 100, 160, 250, 400, 630, 800, 1250, 1600, 2500, 3200 A)
- Breaking capacity: Icu (ultimate) typically 25, 36, 50, 65, 70, 100 kA; Ics (service) typically 50–75% of Icu
- Trip units:
  - **Thermal-magnetic**: simple, fixed or adjustable trip current. Suitable for most applications.
  - **Electronic**: adjustable LSIG (Long-time, Short-time, Instantaneous, Ground fault) settings. Required for selectivity studies and motor protection.

**When to use**
- Main switchboard incomers and outgoing ways (typically 100A and above)
- Sub-distribution board incomers
- Motor protection (electronic trip with thermal model)
- Where adjustability is needed for selectivity

**Pros**
- High breaking capacity options
- Adjustable trip settings allow fine-tuning to load and selectivity needs
- Resettable after operation (unlike fuses)
- Long mechanical life with electronic trip units

**Cons**
- Larger and more expensive than MCBs
- Slower trip times than MCBs at moderate overloads (1.5–3× In)
- Settings can be wrong if not commissioned properly

---

## ACB — Air Circuit Breaker (BS EN 60947-2)

**Construction:** Open-frame breaker designed for very high currents and breaking capacities.

**Ratings**
- In: typically 630 A to 6300 A
- Icu: 50 to 150 kA
- Always equipped with electronic trip units (LSIG, sometimes plus harmonic monitoring, communications)

**When to use**
- Main incomer of large MSBs (typically > 1000A)
- Tie breakers between MSB sections
- Generator outgoing breakers
- Where automatic transfer between supplies is required

**Pros**
- Very high current and fault ratings
- Excellent selectivity capability via zone-selective interlocking (ZSI)
- Drawout (withdrawable) construction allows safe maintenance
- Communications and metering integrated

**Cons**
- Physical size large (1m wide+ for 4000A ACB)
- Cost: 10–20× equivalent MCCB
- Requires skilled commissioning
- Long lead times for spares

---

## AFDD — Arc Fault Detection Device (BS EN 62606)

**Construction:** Detects high-frequency current signatures of arc faults (loose connections, damaged insulation).

**When to use** — Reg 421.1.7 (recommended, not mandatory unless specified)
- Sleeping accommodation (hotels, hostels, care homes, dormitories)
- Locations with risk of fire from electrical sources (storage of combustibles)
- Buildings with combustible construction (timber-frame)
- Listed buildings and museums
- Residential high-rise (often specified post-Grenfell)

**Practical notes**
- Combined AFDD + RCBO device increasingly common
- Cost ~5× of equivalent MCB
- Some risk of nuisance trip with poor-quality switching loads (dimmers, fluorescent transformers)
- Future expectation: AFDD may move from "recommended" to "mandatory" for certain occupancies in future amendments

---

## Device selection decision tree

```
Final circuit?
├── YES
│   ├── Socket outlet ≤ 32A?     → RCBO (Type A or B per load) 30mA
│   ├── Domestic lighting?       → RCBO (Type AC or A) 30mA  (AMD 2 requirement)
│   ├── Other final ≤ 100A?      → MCB or RCBO depending on RCD need
│   └── Final circuit > 100A?    → MCCB
└── NO (distribution circuit)
    ├── Up to ~125A?              → MCCB (most common) or MCB if Icn sufficient
    ├── 125 to 1000A?             → MCCB (electronic trip for selectivity)
    └── Above 1000A?              → ACB
```

---

## Selectivity considerations

**Current discrimination:** Upstream device rating ≥ 1.6 × downstream rating (rule of thumb).

**Time grading:** Use S-type RCDs upstream of instantaneous RCBOs. Use MCCB with short-time delay (S-band) above MCBs.

**Energy discrimination:** Manufacturer-published I²t coordination — only achievable within one manufacturer's range.

**ZSI (Zone Selective Interlocking):** Electronic communication between upstream and downstream breakers. Downstream detects fault → signals upstream → upstream delays its trip until downstream has cleared. Achieves selectivity AND fast clearance simultaneously. Available on ACBs and high-end MCCBs.

---

## Common errors

- Using Type B MCB on circuit with inrush (LED panel arrays) — nuisance tripping
- Specifying RCD where RCBO is required — loss of one circuit causes loss of all
- Choosing MCB Icn below site PSCC — device cannot interrupt fault safely
- Forgetting Type B RCD for EV charging — non-compliant
- Mixing manufacturers in cascade and claiming selectivity — only manufacturer-tested combinations are guaranteed
- Specifying ACB where MCCB would suffice — unnecessary cost and space
- Using fuses without considering replacement strategy — site downtime when no spares
