# IEC 60364 — Amendments Summary: What Changed and Practical Impact

This file summarises the key amendments across the active parts of IEC 60364. The focus is on changes that require a designer using IEC 60364 to do something differently from the previous edition — administrative or structural changes without engineering impact are omitted.

Reference: meta.json for edition/amendment dates per part.

---

## IEC 60364-4-41:2005 — AMD1:2017

### Protection against electric shock

**Change 1: Socket outlet RCD requirement tightened**

AMD1:2017 strengthened the requirement for RCD protection on socket outlet circuits. The amendment clarifies that RCD protection (≤ 30mA) is required for socket outlets intended for general use by non-skilled persons where no other protection measure is employed.

*Practical impact:* In practice this means that in most building types (domestic, commercial, public), virtually every socket outlet circuit requires a 30mA RCD. Designers who previously relied on low Zs alone to protect socket outlet circuits without RCDs should reassess. AMD1 brings the base IEC 60364 requirement much closer to existing UK (BS7671) and French (NF C 15-100) practice.

**Change 2: PELV clarifications**

AMD1 clarified the conditions under which PELV (Protective Extra-Low Voltage) systems may have earthed live parts. The amendment distinguishes more clearly between PELV applications where shock protection is from the low voltage alone versus those where the earth connection provides an additional protective function.

*Practical impact:* Designers specifying PELV for control circuits and ELV lighting should verify their system configuration against the amended Clause 414.4 requirements.

---

## IEC 60364-4-44:2007 — AMD1:2015 + AMD2:2018

### Protection against overvoltage and electromagnetic disturbances

**AMD1:2015 — SPD coordination updates**

AMD1 updated the overvoltage category definitions (Categories I–IV per IEC 60664-1) and revised SPD coordination requirements. The amendment clarified the Uc (maximum continuous operating voltage) selection criterion: Uc must be ≥ 1.1 × U₀ for the supply system voltage.

*Practical impact:* SPD selection becomes more systematic. For 230V systems: Uc ≥ 1.1 × 230 = 253V → minimum Uc = 275V (nearest standard value). Designers had previously used 275V as a rule of thumb; AMD1 provides the calculation basis.

**AMD2:2018 — Mandatory SPD installation scope significantly expanded**

This is the most significant amendment to Part 4-44. AMD2 expanded mandatory SPD installation requirements substantially. Under the original Part 4-44:2007, SPDs were required only in specific cases. AMD2 introduced a general requirement: SPDs must be installed in all new low-voltage electrical installations unless a risk analysis justifies their omission.

*Practical impact:*
- Every new building installation must now include at least Type 2 SPDs at the main distribution board by default, unless the designer can demonstrate through a documented risk assessment that the risk of overvoltage damage is acceptably low
- For buildings with lightning protection systems, Type 1 SPDs are required at the main incomer (to handle the 10/350µs impulse current)
- PV systems now explicitly require SPD protection at the DC input to the inverter
- The "unless justified otherwise" clause requires the designer to document the risk analysis if SPDs are omitted — a change from the previous "install if risk justifies it" approach

**Key SPD selection rules from AMD2:**
- Type 1 (Iimp rated): required where LPS (lightning protection system) is installed, or where installation is in a geographic area with high lightning keraunic level
- Type 2 (In rated, 8/20µs): required at main distribution board in all new installations without Type 1
- Type 3 (at point of use): supplementary protection for sensitive equipment (≤ 1.5kV Up)
- Coordination: Up of Type 2 must be ≤ Uw of the equipment being protected. Uw is defined by installation category (Category II residential equipment: Uw = 2.5kV; Category I sensitive electronics: Uw = 1.5kV)

---

## IEC 60364-5-52:2009 — AMD1:2017

### Wiring systems — current-carrying capacities

**AMD1:2017 — Updated cable rating tables and harmonic correction**

AMD1 made several significant revisions to the current-carrying capacity tables in Annex B:

1. **Revised XLPE cable ratings:** Current-carrying capacities for XLPE-insulated cables were revised in several installation methods. The revisions are modest (typically ±5%) but designers using the pre-AMD1 tables for XLPE cables in Method E (free air) and Method D (buried) should verify their sizing against the updated tables.

2. **New harmonic correction factor table (Annex E):** AMD1 added a formal table of correction factors (Cf) for harmonic current derating of cables. Where triplen harmonic currents (3rd, 9th, 15th harmonic) are present on a three-phase system, the neutral conductor carries the sum of triplen harmonics from all three phases — the neutral can carry more current than any phase conductor. This requires either a larger neutral conductor or a smaller rated current.

*Cf values for neutral current assessment:*
- Current THD < 15%: No derating required — neutral same size as phase
- Current THD 15–33%: Current-carrying capacity based on neutral heating; effective Cf reduces cable rating
- Current THD > 33%: Neutral current exceeds phase current — size cable on neutral current, consider 4th conductor larger neutral, or use 4-core cable with 1.73× phase conductor area neutral

*Practical impact:* Buildings with high IT load (data centres, office blocks, commercial kitchens with VFD-driven equipment) may have significant harmonic distortion. Ignoring Annex E can result in neutral conductor overheating. Measure or calculate THD before finalising cable sizes for three-phase distribution circuits.

3. **Method F added:** AMD1 formally added Reference Method F — single-core cables laid flat and touching on a cable tray. This fills a gap in the pre-AMD1 tables where Method E (cables in free air, not touching) gave higher ratings than conditions typically encountered in practice on cable trays.

---

## IEC 60364-5-52:2009 — AMD2:2023

### Wiring systems — further table revisions and EV wiring

AMD2:2023 made further updates to Annex B cable rating tables, particularly for XLPE cables, and introduced explicit requirements for wiring systems serving EV charging points.

**EV charging wiring requirement (new in AMD2):**
The supply cable to an EV charging point must be sized at 100% of the EVSE rated current — no diversity is applied at the cable level. Load management systems may reduce the actual current drawn, but the cable must be rated for the maximum the EVSE can draw.

*Practical impact:* A 32A Mode 3 wall box requires a cable rated at 32A continuous, regardless of any demand management. This is more conservative than applying a 0.5 or 0.75 diversity factor, as would be common practice for general socket outlet circuits.

---

## IEC 60364-5-54:2011 — AMD1:2021

### Earthing arrangements

**AMD1:2021 — Earth electrode sizing and soil resistivity guidance**

AMD1 updated the guidance on earth electrode sizing and introduced more systematic guidance on soil thermal resistivity for buried electrode systems. For copper earth electrodes, the minimum sizes were reviewed. For combined PEN conductors in TN-C systems, AMD1 added explicit minimum sizes.

*Practical impact:* The fundamental Table 54.1 (minimum PE cross-section vs. line conductor cross-section) is unchanged. The amendment primarily affects specialist earthing design for large installations with independent earth electrode systems, and TN-C system upgrades.

---

## IEC 60364-6:2016 — AMD1:2023

### Verification — periodic inspection intervals and EV charging tests

**AMD1:2023 — Periodic inspection guidance formalised**

AMD1:2023 added formal guidance on periodic inspection intervals (previously absent from the standard — intervals were entirely at national discretion). The intervals introduced in AMD1 align broadly with European practice and provide a reference for countries without nationally mandated intervals.

**EV charging point verification added:**
AMD1 explicitly includes requirements for verifying EV charging point installations, including:
- Verification that RCD type is appropriate (Type A minimum; Type B where DC leakage possible)
- Confirmation of cable sizing compliant with 100% continuous current requirement
- Confirmation of load management system settings and monitoring

*Practical impact:* Inspectors and verifiers now have an explicit IEC basis for including EV-specific checks in their initial verification test sequence.

---

## IEC 60364-7-701:2019 (Third Edition)

### Rooms containing a bath or shower

**Third edition replaces second edition (2006)**

The 2019 third edition was a significant revision. Key changes:

1. **Zone geometry simplified:** The previous second edition used a complex three-dimensional zone definition that was difficult to apply in practice. The third edition simplified the zone boundaries, particularly for shower cubicles and walk-in showers without a tray.

2. **Outside-zones area defined more clearly:** The third edition clarifies that outside the defined zones (but still within the same room), standard socket outlets are permitted subject to RCD protection.

3. **Supplementary bonding review:** The third edition updated the supplementary bonding requirements, recognising that in many modern bathrooms all metalwork is accessible and bonded through the building's main bonding system. Where the prospective touch voltage in the absence of supplementary bonding can be shown to be within safe limits, AMD1 permits dispensing with supplementary bonding.

*Practical impact:* The simplified zone geometry in the 2019 edition makes it easier to apply zone restrictions correctly. Designers should update their zone diagrams from the 2006 edition zones to the 2019 zones — the boundaries have changed.

---

## IEC 60364-7-722:2018 (Second Edition)

### Supply of electric vehicles

**Second edition substantially expands EV charging requirements**

The first edition of Part 7-722 (published 2011) was brief. The 2018 second edition reflects the rapid development of EV charging technology and grid-interactive vehicle systems.

Key additions in 2018 edition:
1. Modes 1–4 formally defined with specific requirements for each
2. Type B RCD requirement introduced for circuits where DC leakage possible
3. Load management systems formally recognised and requirements for documenting managed current set
4. Cable sizing rule clarified: 100% of rated EVSE current (no diversity at cable level)
5. PME/TN-C-S earthing risk addressed — measures required to mitigate broken PEN risk
6. V2G (Vehicle-to-Grid) provisions anticipated — amendment in preparation as of 2024

*Practical impact:* EV charging design moved from an afterthought (a single paragraph in pre-2018 practice) to a standalone design discipline requiring specific RCD type selection, cable sizing methodology, load management documentation, and earthing risk assessment. Any EV charging installation designed to IEC 60364 must now follow Part 7-722 in full.

---

## Summary: Amendments With Greatest Design Impact

| Amendment | Part | Impact Level | Designer Action |
|---|---|---|---|
| AMD2:2018 | 4-44 | **High** | SPD required in all new installations by default; document risk analysis if omitting |
| AMD1:2017 | 4-41 | **High** | 30mA RCD on socket outlet circuits is now unambiguously required in base IEC 60364 |
| 2018 edition | 7-722 | **High** | EV charging now a full discipline — Type B RCD, 100% cable sizing, load management documentation |
| AMD1:2017 | 5-52 | **Medium** | Annex E harmonic derating applies to circuits with >15% THD; Method F added |
| 2019 edition | 7-701 | **Medium** | Zone geometry updated — review existing design templates for bathroom zones |
| AMD2:2023 | 5-52 | **Low** | Table revisions for XLPE; EV wiring rule formalised (already covered by Part 7-722) |
| AMD1:2023 | 6 | **Low** | Periodic inspection intervals formalised; EV verification added |
