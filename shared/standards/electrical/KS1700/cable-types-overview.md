# Cable Types Under KS 1700:2018

> **Verification note:** This file is authored as a draft-from-bs7671-derivative.
> KS 1700:2018 §521 + Annex H adopt the BS 7671 / IEC 60364 cable-type
> framework substantially via KS Annex E, with Kenya-specific equipment
> certification requirements layered on top. Promote `verification_status`
> once verified clause-by-clause against the published KS 1700:2018 PDF.

A reference for selecting the right cable construction for the Kenyan
application. Cable types are governed by KS 1700 §521 (installation
methods) and KS Annex H (Kenya-specific cable types and KEBS-certified
equipment).

---

## Kenya supply context

In Kenya, cable selection is shaped by three factors that differ from
generic BS practice:

1. **KEBS certification mark is required by law.** Any cable sold or
   installed in Kenya must carry the Kenya Bureau of Standards (KEBS)
   certification mark. Imported cables must obtain the KEBS Import
   Standardisation Mark (ISM) at port of entry.
2. **Climate zones drive insulation choices.** Coastal humidity (Mombasa,
   Kilifi, Lamu) and arid northern heat (Marsabit, Garissa) push
   outdoor cable specifications toward XLPE/SWA or UV-stable LSZH.
3. **KPLC infrastructure standards.** Service connections from the KPLC
   network use KPLC-approved cable types only — typically aluminium ABC
   (Aerial Bundled Cable) for overhead and aluminium XLPE/SWA for buried
   service entries.

---

## Naming conventions

Kenyan installations reference:
- **Conductor material**: copper (default for consumer installations), aluminium (KPLC service cables + large submains)
- **Insulation type**: PVC (70°C), XLPE (90°C), EPR (90°C), LSZH variants
- **Construction**: single-core, multi-core, flat (T+E), armoured (SWA)
- **Sheath material**: PVC, LSZH, polyethylene
- **Voltage rating**: 300/500V (household), 600/1000V (industrial)

---

## Standard cable types in Kenya practice

### T+E — Twin and Earth (KS §521)

The default Kenyan domestic and light commercial cable, sold widely by
KEBS-certified local manufacturers (East African Cables, Metsec).

- **Sizes**: 1.0 to 16mm² (above 16mm² switch to multi-core LSZH or SWA)
- **CPC**: reduced size pairs — 1.0/1.0, 1.5/1.0, 2.5/1.5, 4/1.5, 6/2.5, 10/4, 16/6 mm²
- **Use**: Domestic final circuits, small commercial behind plasterboard
- **Don't use**: Where mechanical protection is needed (use SWA), in escape routes (use LSZH), outdoor without conduit, in coastal salt-air environments without sheath rating

### SY 4-core (KS §521)

SY (steel braid screened control flex) is widely used in Kenyan machine
tool circuits, industrial workshops, and CNC installations.

- **Use**: Industrial machine tool circuits per KS §521, control cabling between drive and motor on workshop equipment
- **Construction**: PVC-insulated cores + braid screen + transparent PVC outer
- **Sizes**: 0.75 to 6mm²
- **Note**: SY braid is for screening, NOT for mechanical protection or as a CPC.

### Steel Wire Armoured — SWA (KS §521)

The Kenyan industrial workhorse for fixed power, plant rooms, and
buried services.

- **Use**: Underground submains, plant rooms, external power, buried KPLC service cables, industrial submains across Industrial Area Nairobi / Athi River / Mombasa industrial zones
- **Sizes**: 1.5 to 630mm²
- **Armour as CPC**: For TN systems, the armour serves as the CPC when earthed at both ends (KS §543.2.6 adopts BS Reg 543.2.6 verbatim) — saves a dedicated CPC conductor
- **Coastal note**: Mombasa / Kilifi installations use LSZH-sheathed SWA in preference to PVC due to UV + salt-air degradation of standard PVC sheath

### Single-core LSZH (KS §521)

Single insulated conductors used in conduit, trunking, or for DB and
switchgear internals.

- **Use**: Conduit/trunking wiring, control panel internals
- **Colours per KS Annex C**: brown (L1), black (L2), grey (L3), blue (N), green/yellow (CPC) — matches BS 7671 harmonised colours
- **Sizes**: 1.0 to 240mm²

### Multi-core LSZH (KS §521)

- **Use**: Surface containment in commercial spaces (Westlands offices, Upper Hill towers), distribution feeds to fixed equipment, escape routes
- **Sizes**: 1.5 to 300mm²

### FP200 / Mineral Insulated (KS §527 — adopts BS verbatim)

Fire-rated cables for life-safety circuits — emergency lighting, fire
alarm, sprinkler pumps.

- **Use**: Fire alarm circuits (KS §527 mandates fire-rated cabling for survival-mode circuits)
- **Common products in Kenya**: FP200 Gold (BS 5839-1 standard grade), FP400 (enhanced), MICC for the highest-criticality circuits
- **Sourcing**: imported via KEBS-certified distributors; not domestically manufactured

### Flexible cords (H05/H07 series)

For appliances, portable equipment, and pendants.

- **H05VV-F**: 300/500V, PVC, indoor light use
- **H07RN-F**: 450/750V, rubber, heavy duty (outdoor extensions, industrial portables in workshops)

### Aluminium ABC (Aerial Bundled Cable)

KPLC standard for overhead LV service cables.

- **Use**: KPLC overhead service entries — installed by KPLC, terminated at the consumer cutout.
- **Note**: ABC is KPLC infrastructure; consumer-side cable types begin at the cutout.

---

## Insulation comparison

| Insulation | Max operating temp | Smoke/Halogen | Kenya typical use |
|---|---|---|---|
| **PVC** | 70°C | High smoke, halogen present | Domestic T+E |
| **XLPE** | 90°C | Moderate smoke | Submains, KPLC service cables |
| **LSZH** | 70 or 90°C | Low smoke, zero halogen | Commercial buildings, schools, hospitals |
| **MICC** | 250°C+ | Zero (copper sheath) | Critical life safety |

90°C ratings give ~15% higher current capacity than 70°C for the same
conductor size. XLPE preferred for submains where every kVA matters.

---

## Conductor material

### Copper (default for consumer installations)

- Higher conductivity (lower resistance per mm²)
- Used for nearly all consumer-side final circuits + most submains in Kenya
- East African Cables and Metsec are the dominant KEBS-certified local manufacturers

### Aluminium

- ~2/3 the conductivity of copper — needs ~1.6× the cross-section for the same rating
- Significantly cheaper for very large cables (typically > 70mm²)
- Common in KPLC supply cables and some industrial submains
- Termination requires antioxidant grease + bimetallic lugs to prevent galvanic corrosion (especially relevant in coastal humidity)
- For KS Annex E adopts BS Appendix 4 verbatim — see `appendix4-cable-ratings-aluminium.json`

---

## Cable selection by Kenya application

| Application | Recommended cable |
|---|---|
| Domestic lighting + sockets (Nairobi suburb) | T+E (KEBS-certified) |
| Commercial office final circuits | T+E in trunking, OR multi-core LSZH |
| Risers in commercial towers (Upper Hill, Westlands) | LSZH multi-core on cable tray |
| Industrial plant rooms | SWA clipped direct |
| External above ground (coastal — Mombasa) | LSZH-sheathed SWA (UV + salt resistance) |
| External buried submain | SWA direct buried, depth ≥ 0.7m, with marker tile |
| Off-grid solar PV (Marsabit, Turkana) | UV-stable XLPE/SWA for DC strings |
| Fire alarm | FP200 Gold (BS 5839-1 standard grade) |
| Emergency lighting | FP200 Gold |
| Sprinkler pump supply | FP400 PLUS or MICC, 120 min rated |
| Hospital operating theatre (medical IT) | Special LSZH per KS §710 |

---

## Voltage drop quick reference

KS Annex E adopts BS Appendix 12 verbatim. See
`appendix12-voltage-drop.json` for the full table. The Kenya nominal
supply is 240V single-phase / 415V three-phase, 50 Hz with ±6% EPRA
tolerance — voltage drop budgets should account for this tolerance
range, not just nominal.

---

## Common errors in Kenya practice

- T+E specified outside its mechanical protection zone (e.g. surface in plant room) — should be SWA or in conduit
- PVC cable specified in coastal installations — UV + salt degrade PVC sheath in 5–8 years; specify LSZH or polyethylene
- Aluminium terminated with copper lugs without bimetallic preparation — galvanic corrosion accelerated by coastal humidity
- 70°C cable specified outdoor in arid northern Kenya (Marsabit, Garissa, ambient ≥ 40°C) without derating — overheating + premature failure
- Cable without KEBS certification mark used on site — non-compliant, EPRA inspection failure
- SWA armour relied upon as CPC without proper earthing at both ends per KS §543.2.6
- Fire-rated cable mixed with standard cable in same tray — standard cable melts in fire and damages fire-rated cable

---

## See also

- `KS1700/terminology.md` — KEBS + KPLC vocabulary
- `KS1700/compliance-checklist.md` — equipment certification checklist
- `KS1700/earthing-systems-explained.md` — earthing system per supply type
- `BS7671/cable-types-overview.md` — parent BS text adopted by KS Annex E
- `KS1700/appendix4-cable-ratings.json` — current ratings (adopted from BS verbatim)
