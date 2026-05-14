# Standard Symbols — LV Single Line Diagrams
# BS EN 60617 Reference for the sld skill

Reference data for the sld skill. All symbol codes map to the JSON
`symbol` field used by the ezdxf renderer.

Source: BS EN 60617:2002 Graphical Symbols for Diagrams.
Engineers must verify against the current edition of the standard.

---

## Power Source Symbols

| Symbol code | BS EN 60617 ref | Description | Typical use |
|---|---|---|---|
| `DNO_SUPPLY_3PH` | IEC 60617-11 | 3-phase utility supply terminal | Top of SLD — DNO point of supply |
| `DNO_SUPPLY_1PH` | IEC 60617-11 | Single-phase utility supply terminal | Single-phase service entry |
| `GENERATOR` | IEC 60617-10 | Synchronous generator — circle with G | Standby or prime power generator |
| `UPS_UNIT` | IEC 60617-10 | UPS block — rectangle with battery symbol | Uninterruptible power supply |
| `TRANSFORMER_2W` | IEC 60617-09 | Two-winding transformer — two circles | HV/LV transformer, isolating transformer |
| `PV_SOURCE` | IEC 60617-11 | Photovoltaic source | Solar PV array connection point |

---

## Switching and Isolation Symbols

| Symbol code | BS EN 60617 ref | Description | Typical use |
|---|---|---|---|
| `ISOLATOR_3P` | IEC 60617-07 | 3-pole switch-disconnector | Main incoming isolator, TPN isolator |
| `ISOLATOR_4P` | IEC 60617-07 | 4-pole switch-disconnector (3P+N) | Incomer where N must be switched |
| `ISOLATOR_2P` | IEC 60617-07 | 2-pole switch-disconnector | Single-phase isolation |
| `BUS_SECTION_SW` | IEC 60617-07 | Bus section switch | MSB bus section — normally open or closed |
| `ATS_2WAY` | IEC 60617-07 | Automatic transfer switch (2-position) | Mains/generator changeover |
| `CONTACTOR_3P` | IEC 60617-07 | 3-pole contactor with coil | Motor starters, remotely switched loads |

---

## Protection Device Symbols

| Symbol code | BS EN 60617 ref | Description | Standard | Typical ratings |
|---|---|---|---|---|
| `MCB_1P` | IEC 60617-07 | 1-pole miniature circuit breaker | BS EN 60898-1 | 6–63A |
| `MCB_2P` | IEC 60617-07 | 2-pole miniature circuit breaker | BS EN 60898-1 | 6–63A |
| `MCB_3P` | IEC 60617-07 | 3-pole miniature circuit breaker | BS EN 60898-1 | 6–63A |
| `MCB_4P` | IEC 60617-07 | 4-pole miniature circuit breaker (3P+N) | BS EN 60898-1 | 6–63A |
| `MCCB_3P` | IEC 60617-07 | 3-pole moulded case circuit breaker | BS EN 60947-2 | 16–630A |
| `MCCB_4P` | IEC 60617-07 | 4-pole moulded case circuit breaker | BS EN 60947-2 | 16–630A |
| `ACB_3P` | IEC 60617-07 | 3-pole air circuit breaker | BS EN 60947-2 | 630–6300A |
| `ACB_4P` | IEC 60617-07 | 4-pole air circuit breaker | BS EN 60947-2 | 630–6300A |
| `FUSE_1P` | IEC 60617-07 | Single-pole fuse | BS 88-2, BS 88-3 | Per fuse type |
| `FUSE_3P` | IEC 60617-07 | 3-pole fuse carrier/switch | BS 88-2 | HRC fuse gear |
| `RCCB_2P` | IEC 60617-07 | 2-pole residual current circuit breaker | BS EN 61008-1 | 25–100A, 30mA/100mA/300mA |
| `RCCB_4P` | IEC 60617-07 | 4-pole residual current circuit breaker | BS EN 61008-1 | 25–100A, 30/300mA |
| `RCBO_1P` | IEC 60617-07 | 1-pole RCBO (MCB + RCD combined) | BS EN 61009-1 | 6–40A, 30mA |
| `RCBO_2P` | IEC 60617-07 | 2-pole RCBO | BS EN 61009-1 | 6–40A, 30mA |
| `SPD_T1` | IEC 60617-07 | Surge protective device Type 1 | BS EN 61643-11 | At origin of installation |
| `SPD_T2` | IEC 60617-07 | Surge protective device Type 2 | BS EN 61643-11 | At sub-distribution boards |

### MCB Tripping Characteristics (BS EN 60898-1)

| Curve | Instantaneous trip range | Typical application |
|---|---|---|
| B | 3–5 × In | Resistive loads, lighting, long cable runs |
| C | 5–10 × In | General commercial, motor circuits with modest inrush |
| D | 10–20 × In | High inrush loads — transformers, large motors |

### MCCB Breaking Capacities — Standard Values

| Icu (kA) | Typical application |
|---|---|
| 10 | Low fault-level suburban/rural installations |
| 16 | Typical sub-board incomer in commercial buildings |
| 25 | MSB in medium commercial, urban |
| 36 | MSB in large commercial, DNO urban network |
| 50 | High fault-level urban or near-DNO transformer |
| 70 | Near primary substation, large industrial |

Always select Icu ≥ PSCC at the point of installation.

---

## Measurement and Metering Symbols

| Symbol code | BS EN 60617 ref | Description | Typical use |
|---|---|---|---|
| `CT` | IEC 60617-08 | Current transformer — circle with slash | Metering and protection CTs at incomers |
| `VT` | IEC 60617-08 | Voltage transformer | Voltage measurement on HV/LV boundary |
| `KWH_METER` | IEC 60617-08 | kWh energy meter — circle with E or kWh | Landlord/tenant metering points |
| `SMART_METER` | IEC 60617-08 | Smart/AMR energy meter | Advanced metering infrastructure |
| `AMMETER` | IEC 60617-08 | Ammeter — circle with A | Panel-mounted ammeter on incomers |
| `VOLTMETER` | IEC 60617-08 | Voltmeter — circle with V | Panel-mounted voltmeter |
| `PF_METER` | IEC 60617-08 | Power factor meter | PFC panel instrumentation |

### CT Ratios — Common Values for Commercial Buildings

| CT ratio | Suitable incoming current range |
|---|---|
| 100/5A | Up to 100A incoming |
| 200/5A | 100–200A incoming |
| 400/5A | 200–400A incoming |
| 630/5A | 400–630A incoming |
| 1000/5A | 630A–1000A incoming |

CT class: Class 1 or Class 0.5 for revenue metering. Class 5P or 10P for protection.

---

## Earthing and Bonding Symbols

| Symbol code | BS EN 60617 ref | Description | Typical use |
|---|---|---|---|
| `EARTH_TERMINAL` | IEC 60617-02 | Earth terminal (protective earth) — three bars | Main earthing terminal, circuit earth points |
| `EARTH_ELECTRODE` | IEC 60617-02 | Earth electrode — below-ground bar | TT systems, supplementary electrodes |
| `PEN_TERMINAL` | IEC 60617-02 | PEN conductor terminal | TN-C-S split point at consumer's MET |
| `BONDING_CLAMP` | IEC 60617-02 | Protective bonding connection | Main equipotential bonding to gas/water |

### Earthing Systems (BS 7671:2018 Section 312)

| System | Description | PEN split point | Typical UK application |
|---|---|---|---|
| TN-C-S (PME) | PEN conductor in DNO network, split at consumer | Consumer's main earthing terminal (MET) | Most UK commercial supplies |
| TN-S | Separate PE and N throughout — PE from DNO earth | DNO cable sheath or earth conductor | Older UK supplies, some industrial |
| TT | Consumer provides own earth electrode | N from DNO, earth from electrode | Rural, temporary, EV charging |

---

## Generator and UPS Notation

| Field | Description |
|---|---|
| `generator.rating_kva` | Rated output kVA |
| `generator.fuel_type` | diesel / gas / HVO |
| `generator.amf` | true if Auto Mains Failure panel fitted |
| `generator.essential_bus_id` | Board ID fed from generator essential bus |
| `generator.non_essential_bus_id` | Board ID load-shed on generator |
| `ups.rating_kva` | UPS kVA rating |
| `ups.autonomy_min` | Battery autonomy at full load in minutes |
| `ups.topology` | online_double_conversion / line_interactive |
| `ups.bypass` | true if static/manual bypass fitted |

### ATS Interlocking Note

The ATS must prevent simultaneous connection of mains and generator supplies
unless the panel is specifically designed for synchronised paralleling.
Regulation 551.7 (BS 7671:2018) applies to generators operating in parallel
with the public supply.

---

## Board Type Codes

| Board type code | Description |
|---|---|
| `main_lv_switchboard` | Main LV Distribution Board (MLVDB / MSB) — building intake |
| `sub_distribution_board` | Sub-distribution board (SDB) — floor or zone level |
| `final_distribution_board` | Final DB (FDB / consumer unit) — final circuit level |
| `generator_panel` | Generator interface / ATS panel |
| `ups_panel` | UPS output distribution panel |
| `pfc_panel` | Power factor correction panel |
| `tenant_board` | Tenant metering and isolation board |
| `emergency_board` | Essential services / emergency board |

---

## Standard Cable Conductor Sizes (BS EN 60228)

Copper conductor cross-sections (mm²) used in UK LV installations:

| Size group | Sizes (mm²) | Typical application |
|---|---|---|
| Final circuits | 1.0, 1.5, 2.5, 4.0, 6.0 | Lighting, socket outlets, small power |
| Sub-mains (small) | 10, 16, 25, 35, 50 | Small SDBs, single-phase sub-mains |
| Sub-mains (medium) | 70, 95, 120, 150 | Medium SDBs, 3-phase sub-mains |
| Mains (large) | 185, 240, 300 | MSB incomers, large sub-mains |
| Parallel mains | 2 × 150, 2 × 240, 2 × 300 | When single cable > 300mm² impractical |

Aluminium conductors used above 95mm² in some applications — note in JSON
`conductor_material: "aluminium"` and verify jointing requirements.

---

## Installation Method Codes (Table 4A2, BS 7671:2018)

| Method | Description | CCC reference table |
|---|---|---|
| A1 | Insulated conductors in conduit in thermally insulating wall | 4D1A |
| A2 | Multi-core cable in conduit in thermally insulating wall | 4D2A |
| B1 | Insulated conductors in conduit on wall | 4D1A |
| B2 | Multi-core cable in conduit on wall, or in trunking | 4D2A |
| C | Single or multi-core cable clipped direct to surface | 4D2A |
| D1 | Multi-core cable in duct in ground | 4D4A |
| D2 | Multi-core cable direct in ground | 4D4A |
| E | Multi-core cable in free air, on cable tray | 4D2A |
| F | Single-core cables touching in free air on tray | 4D2A |
| G | Single-core cables spaced in free air | 4D2A |

---

*Source: BS EN 60617:2002, BS 7671:2018 (18th Edition), BS EN 61439-1 & -2.
Always verify against current editions. Symbol rendering in ezdxf is defined
in the renderer module — see assets/renderer-symbols/ for DXF block definitions.*
