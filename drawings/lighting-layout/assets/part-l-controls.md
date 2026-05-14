# Part L Controls Reference — UK Building Regulations
# Lighting Efficacy Targets and Automatic Controls Requirements

Reference data for the lighting-layout skill, Step 9 (Part L compliance check).

Source: Approved Document L (AD L) — Conservation of Fuel and Power.
- **England:** AD Part L Volume 2 (Buildings other than dwellings), 2021 Edition
- **Wales:** AD Part L (Wales) — check current edition; follows similar principles
- **Scotland:** Building Standards Technical Handbook — Section 6 Energy
- **Northern Ireland:** Technical Booklet F2 — Conservation of Fuel and Power

**CRITICAL:** Always verify targets against the edition current at time of design.
AD Part L values are updated with each Amendment. Confirm the applicable edition
with the building control officer at the start of the project.

These values are engineering guidance only — the BRUKL compliance tool
(for England) or SAP/equivalent performs the binding compliance assessment.

---

## Lighting Efficacy Targets — England (AD Part L 2021, Table 6.1)

Minimum installed lamp luminous efficacy for general lighting circuits.
Values expressed in **circuit lumens per circuit watt** (lm/W circuit).

| Space / building type | Minimum efficacy (lm/W) | Notes |
|---|---|---|
| Office — general | 65 | Open plan, private office, meeting rooms |
| Office — display lighting | 22 | Accent, artwork, product display |
| Industrial / warehouse | 75 | General lighting on working plane |
| Retail — general | 65 | Sales floor, general illumination |
| Retail — display / high emphasis | 22 | Feature shelving, window displays |
| Education — classroom | 65 | Primary, secondary, further education |
| Healthcare — ward | 65 | General ward lighting |
| Healthcare — operating theatre / lab | 65 | Specialist clinical spaces |
| Hotel — bedrooms | 45 | Incl. decorative and feature lighting |
| Hotel — public areas, restaurants | 45 | Lobbies, dining, circulation |
| Circulation / corridors | 65 | Internal covered circulation |
| Toilets / WCs | 65 | Welfare facilities |
| Car parks — interior | 65 | Including ramps and circulation |
| External areas (controlled by AD L) | 60 | Canopies, entrances, signage |

**Efficacy calculation:**
```
lamp_efficacy (lm/W) = luminaire_design_lumens / luminaire_circuit_watts
```

Where `circuit_watts` includes the luminaire wattage AND driver/ballast losses.
If driver losses are not stated: use luminaire total wattage from the datasheet.

**If efficacy is below target:**
[NON-COMPLIANCE RISK: Lamp efficacy [X] lm/W is below AD Part L 2021 minimum
of [Y] lm/W for [space type]. Select a higher-efficacy luminaire.
Note: AD L efficacy targets increase with each revision — verify the current
target with building control before tender.]

---

## Automatic Controls Requirements — England (AD Part L 2021, Section 6)

### Offices and commercial buildings

| Space type | Occupancy control | Daylight control | Time switching | Scene control |
|---|---|---|---|---|
| Open plan office | Required — local zone | Required — perimeter zone | Alternative if daylight control present | Recommended for multi-use areas |
| Private / cellular office | Required | If adjacent to façade | Alternative to occupancy | Not required |
| Meeting / conference room | Required | If adjacent to façade | — | Recommended (present, whiteboard, general) |
| Reception / lobby | Required | If adjacent to façade | — | Not required |
| Corridor / circulation | Required or time switching | If sufficient daylighting | Alternative to occupancy | Not required |
| Toilet / WC | Required | — | Alternative to occupancy | Not required |
| Staircase | Required | — | Alternative to occupancy | Not required |
| Print room / storage | Required or time switching | — | Alternative to occupancy | Not required |

### Industrial and warehousing

| Space type | Occupancy control | Daylight control |
|---|---|---|
| Warehouse — general | Required (high-frequency recommended for high bays) | Required if rooflights present |
| Loading bay | Required | If adjacent to loading doors with natural light |
| Plant room | Required or manual local switch | Not required |

### Retail

| Space type | Requirement |
|---|---|
| Sales floor — general | Time switching at circuit level (can be BMS-controlled) |
| Sales floor — display | Manual override, time switching for overnight off |
| Staff areas, back-of-house | Occupancy sensing |
| Car parks | Occupancy sensing or time switching with minimum maintained level |

### Healthcare

| Space type | Requirement |
|---|---|
| Ward — general | Occupancy or BMS time switching; night lighting separate circuit |
| Circulation | Occupancy sensing or time switching |
| Examination / clinical | Manual with override; occupancy sensing if space is intermittently used |

---

## Perimeter Zone Definitions (Daylighting Zones)

A daylit zone is defined as the area of a room that can receive sufficient natural light
to reduce the artificial lighting load. AD Part L and CIBSE guidance define this zone
based on glazing area and orientation.

**Simplified rule for preliminary design:**

| Zone type | Depth from glazed wall | Trigger |
|---|---|---|
| Primary daylit zone | Up to 1× glazing head height from wall | Where glazing head ≥ 2.0m AFF |
| Secondary daylit zone | 1×–2× glazing head height from wall | Where glazing head ≥ 2.0m AFF |
| Skill default (no glazing data) | 2000mm from glazed wall | Use when head height unknown |

For a typical commercial window with head height 2.4m:
- Primary zone: 0–2400mm from glazed wall
- Secondary zone: 2400–4800mm from glazed wall

**For rigorous assessment:** Use the CIBSE Daylight Calculation Tool or
Radiance/EnergyPlus simulation to define the actual daylit zone boundary.

**Circuit requirements for daylit zones:**
- Each daylit zone requires its own separately controllable circuit
- Daylight sensor controls perimeter circuit(s) independently
- Interior circuit(s) controlled by occupancy sensor or time switching
- Sensor setpoint: maintain target lux at sensor position (typically 500 lux
  for offices) — sensor dims artificial light as daylight increases

---

## Occupancy Sensor Selection Guide

| Sensor type | Technology | Suitable spaces | Range |
|---|---|---|---|
| PIR (Passive Infrared) | Heat + motion detection | Small to medium rooms | Up to 8m diameter |
| High-Frequency (HF/Microwave) | Doppler motion | Open plan, warehouses | Up to 20m diameter |
| Dual-technology | PIR + HF combined | High-security, corridors | Per manufacturer |
| Ultrasonic | Sound vibration | Partitioned spaces | Up to 10m |

**For high-bay warehouses (>6m mounting height):** Use HF sensors rated for long range.
**For open plan offices:** Use networked sensors for zone-level dimming and occupancy mapping.
**Time delay after last detection:** Minimum 5 minutes before switch-off (to avoid
false switch-off interruptions).

---

## Photoelectric (Daylight) Sensor Selection Guide

| Parameter | Typical specification |
|---|---|
| Control type | Dimming (continuous) or switching (stepped) |
| Mounting | Ceiling-mounted looking down towards work plane; or external |
| Calibration | Set to maintain 500 lux (office) or target lux at work plane |
| Dead band | ±10% of setpoint to prevent hunting |
| Protocol | DALI-2, 0-10V, or volt-free contact depending on circuit protocol |
| Response time | 30–60 seconds minimum (filters out transient shading effects) |

---

## DALI System Sizing Reference

| Parameter | Limit | Notes |
|---|---|---|
| Devices per DALI bus | 64 | Each driver/ballast = 1 device |
| DALI buses per controller | Varies | Typically 4–16 buses per central controller |
| Groups per bus | 16 | Logical groupings for scene control |
| Scenes per group | 16 | Recall via wall controller or BMS |
| Max cable length | 300m | Use DALI-grade twisted pair; avoid parallel with power cables |

For large open-plan offices (>64 drivers): use multiple DALI buses with a central
DALI controller or Building Management System (BMS) gateway.

---

## Part L Compliance Checklist

Use this checklist at Step 9d to populate `controls.part_l_notes`:

- [ ] Lamp efficacy ≥ minimum target for space type (AD L Table 6.1)
- [ ] Luminaire wattage confirmed (including driver/ballast losses)
- [ ] Occupancy control specified for all applicable spaces
- [ ] Daylight control specified for all perimeter zones with adequate glazing
- [ ] Perimeter zone circuit separated from interior zone circuit
- [ ] Photoelectric sensor type and protocol confirmed
- [ ] Time switching confirmed for spaces not covered by occupancy sensing
- [ ] Scene control specified for conference/meeting rooms (recommended)
- [ ] All controls equipment wiring coordinated with circuit design
- [ ] Building control officer consulted on AD L interpretation for this project

---

*Source: HM Government, Approved Document L — Conservation of Fuel and Power,
Volume 2: Buildings other than dwellings (2021 Edition, England).
Always verify against the edition current at the time of building notice submission.
BRUKL compliance tool and NCM methodology are the binding compliance pathway —
these tables provide preliminary design guidance only.*
