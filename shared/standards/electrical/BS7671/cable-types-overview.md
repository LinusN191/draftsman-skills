# Cable Types Under BS 7671

A reference for selecting the right cable construction for the
application. For fire-rated cables specifically, see
`cable-types-fire-rated.json`.

---

## Naming conventions

UK cables typically reference:
- **Conductor material**: copper (default), aluminium (for very large submains)
- **Insulation type**: PVC (70°C), XLPE (90°C), EPR (90°C), LSZH (low smoke variants)
- **Construction**: single-core, multi-core, flat (T&E), armoured (SWA)
- **Sheath material**: PVC, LSZH, polyethylene
- **Voltage rating**: 300/500V (household), 600/1000V (industrial)

---

## Standard cable types

### T&E — Twin and Earth (BS 6004)

The default UK domestic and small commercial cable.

```
   ┌─────────────────────────┐
   │  ┌──────┐    ┌──────┐   │  Outer PVC sheath
   │  │ Cu L │    │ Cu N │   │  Solid copper conductors (1.5 to 16mm²)
   │  └──────┘    └──────┘   │  PVC insulation 70°C
   │       Cu CPC (bare)     │  Bare CPC — must be sleeved with green/yellow at terminations
   └─────────────────────────┘
```

- **Sizes**: 1.0 to 16mm² (above 16mm² → switch to multi-core LSZH or SWA)
- **CPC**: reduced size — 1.0/1.0, 1.5/1.0, 2.5/1.5, 4/1.5, 6/2.5, 10/4, 16/6 mm² (line/CPC pairs)
- **Use**: Domestic final circuits, small commercial behind plasterboard
- **Don't use**: Where mechanical protection is needed (use SWA), in escape routes (use LSZH), where IP rating > IP2X required (in conduit)

### Single-core LSZH (BS 6231 / BS 7211)

Single insulated conductors used in conduit, trunking, or for connections within DBs and switchgear.

- **Use**: Conduit and trunking wiring, control panel internals
- **Colours**: brown (L1), black (L2), grey (L3), blue (N), green/yellow (CPC), brown for SP
- **Sizes**: 1.0 to 240mm²
- **LSZH variants** preferred for public/commercial buildings (low smoke, zero halogen — reduces toxic fumes in fire)

### Multi-core LSZH (BS 7211 / BS EN 50525)

Twin, three-core, four-core, five-core flexible or rigid cable with LSZH sheath.

- **Use**: Surface containment in commercial spaces, distribution feeds to fixed equipment, escape routes
- **Sizes**: 1.5 to 300mm²
- **Versions**:
  - 3 core (3L) or 4 core (3L+N) for three-phase power
  - 5 core (3L+N+PE) where separate CPC required
  - Flexible (H07RN-F equivalent) for portable equipment

### Steel Wire Armoured — SWA (BS 5467 / BS 6724)

Armoured cable for mechanical protection, underground burial, and EMI immunity.

```
   Outer PVC or LSZH sheath
   ▼
   ┌──────────────────────────┐
   │  ╱╱╱╱╱╱╱ steel wires ╱╱╱ │  Single layer of galvanised steel wires
   │  ┌───┐  ┌───┐  ┌───┐    │  Insulated cores (3, 4, or 5)
   │  │L1 │  │L2 │  │L3 │    │  Bedding (PVC or LSZH)
   │  └───┘  └───┘  └───┘    │
   └──────────────────────────┘
```

- **Versions**:
  - BS 5467 — 600/1000V — most common for fixed power
  - BS 6724 — LSZH equivalent of BS 5467
- **Sizes**: 1.5 to 630mm²
- **Use**: Underground submains, plant rooms, external power, anywhere mechanical protection or EMI shielding needed
- **Armour as CPC**: For TN systems, the armour can serve as the CPC when earthed at both ends (Reg 543.2.6) — saves a dedicated CPC conductor

### MICC — Mineral Insulated Copper-Clad (BS EN 60702)

Inorganic insulation between copper conductors and a copper outer sheath.

- **Use**: Highest-risk fire safety applications, chemical plants, listed buildings, deep tunnels
- **Sizes**: 1.0 to 240mm²
- **Versions**: Light Duty (500V) and Heavy Duty (750V)
- **Pros**: Survives 950°C for 3 hours (BS 6387 CWZ rating). Indefinite service life.
- **Cons**: Specialist termination (seal pots). Brittle if over-bent. Highest cost (6–10× standard cable).

### Flexible cords (H05/H07 series)

For appliances, portable equipment, and pendants.

- **H05VV-F**: 300/500V, PVC, indoor light use (table lamps, small appliances)
- **H07RN-F**: 450/750V, rubber, heavy duty (outdoor extensions, industrial portables)
- **H05Z1Z1-F**: LSZH flexible — public buildings, schools, hospitals

### Mineral / fire-rated cables

See `cable-types-fire-rated.json` for product-level detail on FP200 Gold, FP400 PLUS, and MICC for life safety.

---

## Insulation comparison

| Insulation | Max operating temp | Smoke/Halogen | Typical use |
|------------|--------------------|---------------|-------------|
| **PVC (thermoplastic)** | 70°C | High smoke, halogen present | Domestic T&E, general purpose |
| **XLPE (thermosetting)** | 90°C | Moderate smoke if XLPE-sheathed | Power distribution, submains |
| **EPR (thermosetting)** | 90°C | Moderate smoke | Industrial control |
| **LSZH** | 70 or 90°C | Low smoke, zero halogen | Public buildings, schools, hospitals, retail |
| **MICC (mineral)** | 250°C+ | Zero — copper sheath | Critical life safety |

**90°C ratings give ~15% higher current capacity than 70°C** for the same conductor size. XLPE preferred for submains where every kVA matters.

---

## Conductor material

### Copper (default)
- Higher conductivity (lower resistance per mm²)
- Easier to terminate
- Used for nearly all final circuits and most submains

### Aluminium
- Approximately 2/3 the conductivity of copper — needs ~1.6× the cross-section for the same rating
- Significantly cheaper for very large cables (typically > 70mm²)
- Common in DNO supply cables, some industrial submains
- Termination requires antioxidant grease and bimetallic lugs to prevent galvanic corrosion
- For BS 7671 ratings: see `appendix4-cable-ratings-aluminium.json`

---

## Cable selection by application

| Application | Recommended cable |
|-------------|------------------|
| Domestic lighting and sockets | T&E (BS 6004) |
| Domestic shower / cooker | T&E sized for load |
| Commercial office final circuits | T&E in trunking, OR multi-core LSZH |
| Commercial lighting in suspended ceiling | T&E or LSZH multi-core, clipped |
| Risers (commercial) | LSZH multi-core on cable tray, OR SWA if mechanical risk |
| Plant rooms | SWA clipped direct |
| External above ground | SWA clipped or on cable tray |
| External buried (submain to outbuilding) | SWA direct buried, depth ≥ 0.7m, with marker tile |
| EV charging supply | LSZH or SWA — depends on route |
| Fire alarm | FP200 Gold (BS 5839-1 standard grade), FP200 PLUS (enhanced) |
| Emergency lighting wiring | FP200 Gold typically |
| Sprinkler pump supply | FP400 PLUS or MICC, 120 min rated |
| Operating theatre (medical IT) | Special LSZH or PVC, separate IT-M circuit |
| Hazardous area (Zone 1/2) | Per DSEAR — typically SWA with Ex glands, intrinsically safe certified |

---

## Voltage and frequency ratings

| Rating | Use |
|--------|-----|
| **300/500V** | Domestic, light commercial. T&E, LSZH multi-core. |
| **450/750V** | Heavy-duty flexible cords, control circuits. |
| **600/1000V** | Fixed power distribution, SWA. Standard for most commercial and industrial. |
| **3.6/6kV upwards** | Medium voltage cables — outside scope of BS 7671 (BS 6622 etc.). |

UK supply is 50 Hz. For 60 Hz installations (US/Caribbean), de-rate inductive losses slightly above 95mm².

---

## Voltage drop quick reference (per mV/A/m)

For commonly used sizes — see `appendix12-voltage-drop.json` for full table.

| Size | Two-core (single-phase) mV/A/m | Three-core (three-phase) mV/A/m |
|------|--------------------------------|---------------------------------|
| 1.5  | 29   | 25   |
| 2.5  | 18   | 15   |
| 4    | 11   | 9.5  |
| 6    | 7.3  | 6.4  |
| 10   | 4.4  | 3.8  |
| 16   | 2.8  | 2.4  |
| 25   | 1.75 | 1.50 |
| 35   | 1.25 | 1.10 |
| 50   | 0.93 | 0.80 |
| 70   | 0.63 | 0.55 |
| 95   | 0.47 | 0.41 |
| 120  | 0.37 | 0.32 |

---

## Common errors

- T&E specified outside its mechanical protection zone (e.g. surface in plant room) — should be SWA or in conduit
- PVC cable used in escape routes — LSZH should be specified
- Aluminium terminated with copper lugs without bimetallic preparation — galvanic corrosion
- 70°C cable specified in environment > 30°C without derating — overheating
- SWA armour relied upon as CPC without proper earthing at both ends
- Fire-rated cable mixed with standard cable in same tray — standard cable melts in fire and damages fire-rated cable
- Insufficient cable bending radius (minimum 6× cable diameter for SWA, 4× for T&E) — conductor damage
