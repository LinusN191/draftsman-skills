# IEC 60617 — Symbol Usage Guide

This guide tells you which symbol to pick, when to use it, and what to annotate. It complements the per-symbol `usage_notes` field in the part files by covering combinations and common pitfalls that only become clear when you look at a complete drawing.

---

## Choosing the Right Symbol: Decision Trees

### Protective device on a final circuit

```
Is the circuit a socket outlet circuit or wet-area?
├─ YES → RCBO_1P / RCBO_2P (combined MCB + RCD in one device)
└─ NO  → Is the circuit a motor circuit ≤ 32A?
         ├─ YES → MCB_MOTOR (combined thermal + magnetic in one device)
         └─ NO  → MCB_1P / MCB_2P / MCB_3P / MCB_4P (per pole count)
```

### Protective device at a sub-DB incomer

```
Is the rated current ≤ 100A?
├─ YES → MCB_3P or MCB_4P (per pole count)
└─ NO  → Is the rated current ≤ 1600A?
         ├─ YES → MCCB_3P / MCCB_4P
         └─ NO  → ACB_3P / ACB_4P
```

### Protective device at a main switchboard incomer

```
Always ACB_3P or ACB_4P (≥ 800A typical).
Annotate trip unit type. Short-time delay setting must coordinate with
downstream MCCBs.
```

### Earth symbol on an SLD

```
Building main earthing terminal (MET)
├─ EARTH_GENERAL — general-purpose earth point
Sensitive equipment / data centre / hospital Group 2
├─ EARTH_CLEAN — separate clean earth (triangle shape)
Exposed-conductive-part of Class I equipment
├─ EARTH_PROTECTIVE — the PE bond
Buried electrode (rod, plate, mesh)
├─ EARTH_ELECTRODE — the physical buried electrode (triangle with arrow)
```

### Switch symbol on a plan

```
Lighting circuit control:
├─ Single location → SWITCH_1WAY
├─ Two locations (e.g. stairs) → pair of SWITCH_2WAY
├─ Three or more locations → 2× SWITCH_2WAY + 1+ SWITCH_INTERMEDIATE
├─ Dimming → SWITCH_DIMMER
Sensors (replace manual switches for energy-saving control):
├─ Movement detection → SENSOR_PIR (cheap) or SENSOR_OCCUPANCY (dual-tech)
├─ Daylight detection → SENSOR_DAYLIGHT (often combined with PIR)
```

---

## Drawing Conventions Used by DraftsMan Skills

### SLD conventions (electrical/sld)

1. **Single-line representation.** Each circuit is drawn as a single line, regardless of pole count. Pole count is annotated on the protective device symbol.
2. **Line thickness.** Busbars are drawn at heavier line weight than circuits. Use the runtime's `E-BUS` layer for busbars (4× thickness).
3. **Annotation position.** Annotations sit above the conductor (rating, CSA) or to the right of the device (circuit label).
4. **Direction.** SLDs are normally drawn with the source at the top, loads at the bottom (gravity convention).
5. **Layer mapping.** Each symbol category maps to a CAD layer — see README.md.

### Schematic conventions (electrical/schematic)

1. **Multi-line representation.** All conductors of a circuit are drawn separately (L1, L2, L3, N, PE).
2. **Reading direction.** Schematics read left-to-right (source on the left, load on the right). Control circuits below power circuits.
3. **Contact placement.** Contacts of the same device may be split across the schematic — link them by tag (e.g. K1.1, K1.2).
4. **Layer mapping.** Same category-to-layer mapping as SLDs.

### Architectural plan conventions (electrical/lighting-layout, small-power, etc.)

1. **Plan-view symbols only.** Use Part 11 symbols, not Part 7 schematic symbols, on architectural plans.
2. **Cable routes.** Use `CABLE_ROUTE_*` variants to indicate concealed/surface/overhead/underground.
3. **Scale.** Plan-view symbols are drawn at a fixed paper size regardless of drawing scale (typically 5mm at 1:50, 10mm at 1:100).
4. **Annotation.** Circuit reference labels (DB-1.1, DB-1.2 …) placed adjacent to outlets.

---

## Common Symbol Combinations

### Final socket outlet circuit (single phase, RCD-protected)

```
[CONDUCTOR_SINGLE] — [RCBO_1P] — [CABLE_ROUTE_*] — [SOCKET_DOUBLE]
```

Annotations:
- RCBO: `In_A`, `IDn_mA` (30mA), `curve` (typically B), `type` (typically A)
- Cable route: circuit ID
- Socket: type (BS1363 13A typical)

### 3-phase motor circuit (DOL start)

```
[BUSBAR_3PH] — [MCB_MOTOR or MCCB_3P]
            — [CONTACTOR_3P]
            — [RELAY_THERMAL]
            — [CONDUCTOR_3CORE]
            — [MOTOR_INDUCTION or MOTOR_CONNECTION]
```

Or use the composite `MOTOR_STARTER_DOL` instead of the three discrete devices.

Annotations:
- MCCB / MPCB: `In_A`, `Im_setting`
- Contactor: `AC3_kW` (must match motor rating)
- Thermal relay: `set_A_range` covering motor FLC
- Motor: `rating_kW`, `voltage_V`, `rpm`

### Main DB incomer with surge protection

```
[BUSBAR_3PH] — [ACB_4P]
            — [SPD_TYPE2 (parallel to earth)]
            — [BUSBAR_3PH (loads)]
```

Annotations:
- ACB: `In_A`, `Icu_kA`, `trip_unit`
- SPD: `In_kA`, `Up_kV`, `Uc_V` (typically Uc = 275V for 230/400V system)

### CT-VT metering chain

```
Power conductor: [BUSBAR_3PH] — [CT_METERING (×3)] — [BUSBAR_3PH]
Voltage tap:     [BUSBAR_3PH] — [VT_METERING (×3)] — [MULTIFUNCTION_METER]
Current input:                 [CT_METERING] — [MULTIFUNCTION_METER]
```

Annotations:
- CT: `ratio` (e.g. 400/5), `class` 0.5
- VT: `ratio` 11000/110 (HV) or 400/110 (LV)
- Meter: functions list

### Generator + utility ATS

```
[Utility supply] — [ACB_4P (utility incomer)] —┐
                                                ├─ [ATS_2WAY] — [DB_MAIN]
[GENERATOR_SYNC] — [ACB_4P (genset incomer)] —┘
```

Annotations:
- ATS: `rated_A`, `transfer_time_s`
- Genset: `rating_kVA`, `voltage_V`, `pf`

---

## Mistakes to Avoid

### Mistake 1: Stacking 1-pole symbols for a 3-phase circuit

Do not draw three `MCB_1P` symbols side by side to represent a 3-pole MCB. Use `MCB_3P`. Three separate 1-pole devices have separate operating mechanisms and do not give simultaneous interruption — they are not equivalent.

### Mistake 2: Confusing isolator and switch-disconnector

`ISOLATOR_*` cannot break load current — it is a visible-break device only, operated off-load. `SWITCH_DISCONNECTOR_*` can break load current and is suitable for normal switching duty. A circuit's main switch is almost always a switch-disconnector, not a plain isolator.

### Mistake 3: Missing terminal labels on detailed schematics

On Part 7 contact symbols, label the terminals (e.g. 13/14 for NO, 11/12 for NC, A1/A2 for coil). The skill validation will flag missing terminal labels on schematic outputs.

### Mistake 4: Wrong category symbol on the wrong drawing type

`MCB_1P` (Part 7) is for SLDs and schematics. `SOCKET_SWITCHED_DOUBLE` (Part 11) is for architectural plans. Don't put `SOCKET_SWITCHED_DOUBLE` on an SLD — represent the outlet on the SLD as a generic load with a circuit annotation; show the socket on the plan.

### Mistake 5: Confusing PE/N/PEN

- `CONDUCTOR_PE` — separate PE only (TN-S, downstream of MET).
- `CONDUCTOR_N` — separate N only (TN-S).
- `CONDUCTOR_PEN` — combined (TN-C, only upstream of MET; in IEC 60364 terms only in the supply side of a TN-C-S installation).
- Once PEN has been separated into PE and N, never recombine them downstream.

### Mistake 6: Drawing both an RCD and an RCBO on the same circuit

`RCBO_1P` is a combined MCB + RCD. Don't pair it with a separate `RCD_2P` upstream — they will trip together and lose discrimination. The pairing only makes sense if the upstream RCD is selective (type S) and the RCBO is general type.

### Mistake 7: Forgetting the SPD earth lead

Every SPD needs an explicit earth connection. The SPD symbols have an `earth` terminal — draw the path from the SPD body to the local earth bar. Don't leave it floating.

---

## When Two Symbols Are Almost the Same

| Pair | Distinction |
|---|---|
| `TRANSFORMER_2W` (Part 6) vs `VT_METERING` (Part 8) | TRANSFORMER_2W is a power transformer (kVA scale); VT_METERING is a small measuring VT (VA scale) used with a meter. |
| `TRANSFORMER_CURRENT` (Part 6) vs `CT_METERING` (Part 8) | Same geometry; the metering form has a defined accuracy class. Use the metering form when the CT feeds a revenue meter. |
| `LUMINAIRE_GENERAL` (Part 8) vs `LUMINAIRE_ARCH` (Part 11) | Part 8 is the schematic-side symbol (on a control schematic, a wiring diagram). Part 11 is the architectural plan-view symbol. |
| `JUNCTION_BOX_CONDUCTOR` (Part 3) vs `JUNCTION_BOX` (Part 11) | Part 3 is the schematic in-line junction. Part 11 is the plan-view junction box. |
| `MOTOR_INDUCTION` (Part 6) vs `MOTOR_CONNECTION` (Part 11) | Part 6 is the schematic motor (with circle, label MA). Part 11 is the plan-view motor connection point. |
| `SWITCH_1P` (Part 7) vs `SWITCH_1WAY` (Part 11) | Part 7 is the schematic single-pole switch. Part 11 is the plan-view 1-way wall switch (circle). |

When in doubt: schematic drawings use Part 7 / Part 8 symbols; architectural floor plans use Part 11 symbols; cable section views use Part 3 symbols.

---

## Annotation Quick Reference

Every device on an SLD or schematic should be annotated with the fields listed in its `annotation_fields` array. Common patterns:

| Device type | Required annotations |
|---|---|
| MCB / MCCB / ACB | In_A, curve (B/C/D), Icu_kA |
| Fuse | In_A, fuse type (gG, aM, gF, BS88) |
| RCD / RCBO | In_A, IDn_mA, type (AC, A, F, B) |
| Contactor | AC3_kW, coil voltage |
| Transformer | kVA, primary V, secondary V, vector group, uk% |
| Motor | kW, voltage, rpm |
| Cable | csa_mm² (e.g. 4mm²), insulation (e.g. XLPE/SWA), length |
| SPD | type (1/2/3), In_kA or Iimp_kA, Up_kV, Uc_V |

The skill validation routines load each part file and check the drawing IR for the listed annotation fields. Missing fields generate a warning in the skill output.
