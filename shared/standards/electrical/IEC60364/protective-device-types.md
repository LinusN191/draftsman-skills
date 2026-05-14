# IEC 60364 — Protective Device Types

Selection guide for overcurrent and residual-current protective devices.
References IEC 60898 (MCBs), IEC 60269 (fuses), IEC 60947-2 (MCCBs/ACBs),
IEC 61008/61009 (RCCBs/RCBOs).

---

## Miniature Circuit Breakers (MCBs) — IEC 60898

MCBs provide both overload and short-circuit protection in one device.
They have two trip mechanisms: thermal (bimetallic strip, overload) and magnetic (solenoid, short-circuit).

### Trip characteristic types

| Type | Instantaneous trip | Use case |
|------|--------------------|----------|
| **B** | 3×–5× In | Resistive loads, lighting, general socket outlets — minimal inrush |
| **C** | 5×–10× In | Inductive loads, fluorescent/LED banks, small motors, transformers |
| **D** | 10×–20× In | Very high inrush — transformer primary, motor-generator sets, welding |
| **K** | 8×–12× In | Motor protective characteristic — similar to D but with specific motor overload curve |
| **Z** | 2×–3× In | Semiconductor protection, very sensitive circuits |

**Which type to use:**
- Lighting and socket circuits — **Type B** (standard)
- Motor starters (DOL, star-delta) — **Type C** (or D for direct-on-line heavy motors)
- Transformer primary circuits — **Type C** or **Type D** depending on inrush
- EV charging — **Type C** (EV chargers have significant charging current step-change)

### Standard ratings
IEC current ratings: 6, 10, 13, 16, 20, 25, 32, 40, 50, 63, 80, 100, 125 A

### Breaking capacity
| Rating | Typical application |
|--------|---------------------|
| 3 kA | Domestic only, low PSCC confirmed |
| 6 kA | Standard domestic/commercial |
| 10 kA | Commercial and industrial — recommended as minimum |
| 16 kA | Near main switchboards in commercial |
| 25 kA+ | Industrial near transformers — use MCCB or HRC fuse above this |

**Never assume 6 kA is adequate without checking the PSCC at the point of installation.**

---

## Residual Current Circuit Breakers (RCCBs) and RCBOs — IEC 61008/61009

RCDs trip on the difference between line and neutral current — the imbalance indicates current is returning via earth (a person, a fault path).

### RCD types by waveform detection

| Type | Detects | Use |
|------|---------|-----|
| **AC** | Sinusoidal AC only | Resistive-only loads — NOT suitable for electronic equipment |
| **A** | AC + pulsating DC | Standard for modern installations — handles SMPSs, single-phase EVs, LED drivers |
| **F** | AC + pulsating DC + composite frequencies | Single-phase VFDs, washing machine inverter motors |
| **B** | AC + DC + high frequency | Three-phase EV charging, three-phase VFDs |
| **S** | Time-delayed version of any of above | Selectivity — upstream of 30mA RCDs, prevents losing whole building on single fault |

**Selection rule:**
- Default for all general circuits → **Type A**
- Single-phase VFD circuits → **Type F**
- Three-phase EV chargers → **Type B** (or Type A + 6mA DC monitor)
- Upstream of 30mA RCDs → **Type S (delayed), 100–300mA**
- Never use **Type AC** for circuits with any electronic equipment

### Standard IΔn ratings

| IΔn | Application |
|-----|-------------|
| 6 mA | DC fault monitor for EV circuits |
| 10 mA | Swimming pool Zone 1, special applications |
| **30 mA** | **All socket outlets, cables in walls, bathrooms, additional protection** |
| 100 mA | Fire protection only — not personal protection |
| 300 mA | Fire protection, upstream selectivity with 30mA downstream |
| 500 mA | Industrial, large leakage installations (many VFDs) |

### RCBO — Combined RCD + MCB
An RCBO (IEC 61009) provides both residual current AND overcurrent protection in a single device.
- **Advantage:** One device per circuit — simpler, less panel space
- **Disadvantage:** More expensive, failure affects one circuit (loss of protection + overcurrent)
- **Use:** Final circuit protection in consumer units/distribution boards where individual circuit RCD is required

---

## HRC (High Rupturing Capacity) Fuses — IEC 60269

Cartridge fuses with high breaking capacity (typically 80–120 kA). The fuse element melts under overload or fault, interrupting the circuit.

### gG type — General purpose (general current-limiting)

| Feature | Detail |
|---------|--------|
| Standard | IEC 60269-1 (general), IEC 60269-3 (distribution) |
| Type code | **gG** — general, full-range (handles both overload AND short-circuit) |
| I2 factor | 1.6 × In |
| Breaking capacity | 80–120 kA (typical) |
| Advantage over MCB | Much lower let-through energy (I²t) at high fault levels — better cable protection |
| Disadvantage | Fuse replacement required after operation — cannot be reset |
| Use | Submains, distribution boards, motor circuits (overload relay provides overload protection) |

**Common gG ratings:** 2, 4, 6, 10, 13, 16, 20, 25, 32, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630 A

### aM type — Motor circuit (partial range)

| Feature | Detail |
|---------|--------|
| Type code | **aM** — motor, partial range (short-circuit protection ONLY — no overload) |
| Purpose | Protects against short-circuit — overload relay/thermal trip provides overload protection |
| Must be used with | Overload relay (motor starter contactor + overload relay) |
| Advantage | Withstands motor starting current without blowing — designed for high inrush |
| Never use alone | Without overload protection, a motor running at 120% current will burn out without tripping the aM fuse |

### BS 88 type (UK) — Compatible with gG

BS 88 fuses (used in UK installations to BS 7671) are compatible with IEC 60269 gG type. The trip characteristics and let-through energy are similar. For UK projects, refer to BS 7671/appendix3-device-curves.json for BS 88 specific data.

---

## Moulded Case Circuit Breakers (MCCBs) — IEC 60947-2

Larger capacity than MCBs, with adjustable trip settings and higher breaking capacity.

| Feature | Detail |
|---------|--------|
| Current range | 16 A to 1600 A (typical) |
| Breaking capacity | 16–200 kA |
| Trip settings | Fixed (non-adjustable) in smaller sizes; adjustable in larger — thermal, magnetic, or electronic trip |
| Electronic trip unit | Full LSIG adjustability (Long-time, Short-time, Instantaneous, Ground fault) |
| Selectivity | Electronic MCCBs with short-time delay (S-band) can achieve selectivity with downstream MCBs |
| Standards | IEC 60947-2 |
| Use | Main incomer to sub-distribution boards, large motor feeders, bus section breakers |

### MCCB LSIG settings (electronic trip units)

| Setting | Function |
|---------|----------|
| **L** (Long-time) | Overload protection — equivalent to thermal trip. Set to FLC or cable rating. |
| **S** (Short-time) | Intentional time delay for selectivity — allows downstream devices to clear the fault first |
| **I** (Instantaneous) | High-speed magnetic trip for very high fault currents (typically > 8–12× In) |
| **G** (Ground fault) | Earth fault protection — not widely used outside USA |

---

## Air Circuit Breakers (ACBs) — IEC 60947-2

Largest category of circuit breakers for main switchboard incoming and bus section duties.

| Feature | Detail |
|---------|--------|
| Current range | 800 A to 6300 A |
| Breaking capacity | Up to 150 kA |
| Trip unit | Always electronic — full LSIG adjustable |
| Zone Selective Interlocking (ZSI) | Communication between cascaded ACBs — downstream sees fault, signals upstream to delay, ensuring only the device nearest the fault trips |
| Drawout or fixed | Both variants available — drawout allows replacement under live conditions |
| Standards | IEC 60947-2 |
| Use | Main switchboard incomers, bus section breakers, large generator changeover |

---

## Surge Protective Devices (SPDs)

See `part4-44-overvoltage.json` for full SPD selection guide.

| Type | Function |
|------|---------|
| Type 1 | Lightning discharge current — at service entrance, where LPS present |
| Type 2 | Induced surges — at every distribution board |
| Type 3 | Point-of-use protection — at sensitive equipment |
| Type 1+2 | Combination at main board |

---

## Device selection matrix

| Application | Device type |
|------------|-------------|
| Lighting final circuit, 16A | 16A Type B MCB + 30mA Type A RCBO |
| Socket outlet ring/radial, 32A | 32A Type B MCB + 30mA Type A RCBO |
| Motor DOL, 7.5kW | 16A Type C MCB + overload relay OR Type D MCB |
| Submain to SDB, 100A | 100A MCCB (TM or electronic) |
| Incomer MDB, 400A | 400A MCCB electronic, or 400A ACB |
| Generator incomer, 800A+ | ACB with ATS interlocks |
| EV charger circuit, 32A single-phase | 32A Type C MCB + 30mA Type A RCBO |
| EV charger, 32A three-phase | 32A 3-pole Type C MCB + 30mA Type B RCD |
| Transformer primary | Type D MCB or gG fuse sized for inrush |
| Submain with high PSCC | 100A+ gG fuses for better I²t let-through |

---

## Common errors to avoid

1. **Type AC RCDs on electronic load circuits** — Type AC cannot detect DC residual current from switch-mode power supplies. Use Type A minimum.
2. **No S-type upstream RCD** — Installing 30mA RCDs downstream of a 300mA instant-trip RCD loses selectivity. The 300mA will trip on a 30mA fault.
3. **MCB breaking capacity not checked** — 6kA MCBs fail catastrophically when PSCC at installation is 10+ kA. Check PSCC, specify 10kA MCBs in commercial buildings.
4. **Type B MCB on motor circuits** — Motor inrush trips Type B. Use Type C or D.
5. **gG fuse on motor without overload relay** — gG fuses do not provide overload protection adequately for motor circuits. Always add a thermal or electronic overload relay.
