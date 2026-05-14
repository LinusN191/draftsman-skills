# IEC 60364 — Cable Types: Selection by Application and Environment

Reference: IEC 60364-5-52:2009+AMD1:2017, Clause 521 (Types of wiring systems), IEC 60228:2004 (Conductors), IEC 60227 (PVC cables), IEC 60245 (Rubber cables), IEC 60702 (MICC), IEC 60332 (Fire tests)

---

## Cable Selection Principles

A cable must simultaneously satisfy five independent requirements. Failure to consider any one of them is a design error:

1. **Current rating** — The cable must carry the design current Ib without exceeding its maximum conductor temperature. This is an insulation life and fire prevention requirement, not just a convenience.
2. **Voltage drop** — The cable must deliver adequate voltage at the load terminals under full-load conditions. IEC 60364-5-52 Annex G recommends 3% for lighting, 5% for other uses (informative limits — verify national requirement).
3. **Fault withstand** — The cable's conductors and insulation must survive the energy let-through from the protective device clearing a fault. Verified by the adiabatic equation: I²t ≤ k²S² (Clause 434.5).
4. **Mechanical protection** — The cable must resist the physical hazards of its installed environment: crushing, rodent attack, UV, chemical exposure, tension, and impact.
5. **Fire performance** — The cable must not propagate a fire in its installed location, and where circuit integrity during a fire is required, the cable must maintain function for the required duration.

No cable type scores best on all five. The selection is always a compromise optimised for the dominant constraints of the application.

---

## PVC Insulated Cables (70°C)

**Standards:** IEC 60227 series (fixed wiring); IEC 60228 for conductors.

PVC (polyvinyl chloride) is the most widely used cable insulation worldwide. It is inexpensive, chemically resistant to most oils and weak acids, easily terminated, and mechanically robust in normal installations. The maximum continuous conductor temperature is 70°C, which sets the current-carrying capacity from the Annex B tables.

**Strengths:**
- Low cost — 60–70% cheaper than XLPE for the same cross-section
- Wide temperature range for storage and installation (−5°C to +60°C) — does not crack when installed in cold weather in the way that some compounds do
- Excellent oil and weak acid resistance — suitable for industrial environments
- Self-extinguishing in normal fire tests (IEC 60332-1)
- Easily repaired and re-terminated in the field

**Limitations:**
- Maximum continuous temperature 70°C — requires larger cross-section than XLPE for the same current
- Releases hydrogen chloride (HCl) gas when burned — corrosive and toxic fumes, visibility-impairing smoke. Not suitable for locations where people cannot escape quickly (occupied buildings, public areas) unless LSZH is specified instead
- Softens above 70°C — cannot be used on or near hot surfaces (steam pipes, flue ducts)
- Cold becomes brittle below −5°C — do not install at low temperature without warming
- PVC plasticiser migrates over decades — old PVC cables become brittle. Expect 30–40 year service life in normal conditions

**Typical applications:**
- Domestic and commercial wiring in conduit, trunking, or clipped to surfaces
- Distribution boards and switchgear wiring
- Industrial fixed wiring where smoke hazard is acceptable
- Underground power cables (PVC outer sheath with XLPE insulation is common for HV cables)

---

## XLPE Insulated Cables (90°C)

**Standards:** IEC 60502 (power cables with XLPE or EPR insulation, 1kV to 30kV); IEC 60227/60245 for flexible versions.

XLPE (cross-linked polyethylene) achieves higher operating temperatures than standard PVC by chemically cross-linking the polyethylene polymer chains. This prevents softening and flow at elevated temperatures. The maximum continuous conductor temperature is 90°C, giving approximately 25–30% higher current-carrying capacity than the same cable with PVC insulation.

**Strengths:**
- Higher current rating than PVC at the same cross-section — allows one or two cable size reductions for the same current
- Maximum temperature 90°C continuous; 130°C short-circuit withstand
- Better thermal stability at high load — smaller cross-section for the same current in a constrained route
- Better electrical characteristics for high-voltage applications (lower dielectric loss)
- More fire-resistant than PVC at higher temperatures

**Limitations:**
- More expensive than PVC (typically 20–30% premium for LV cables)
- XLPE outer sheath is not inherently flexible — less suitable for flexible connections than rubber
- Some XLPE compounds are more susceptible to water treeing at high voltage (mitigated by tree-retardant XLPE — TR-XLPE)
- Smoke and toxic gas hazard similar to PVC unless LSZH outer sheath is added

**Typical applications:**
- Final circuit cables and distribution cables where current density is critical
- Underground service cables and distribution mains (often XLPE insulation with PVC or PE outer sheath)
- Industrial submain cables where weight saving matters
- All cable types in hot ambient environments (plant rooms, boiler rooms) where 90°C rating is needed to avoid over-sizing

---

## EPR (Ethylene Propylene Rubber) Cables (90°C)

**Standard:** IEC 60245 (rubber-insulated cables), IEC 60502-1 for power cables with EPR.

EPR is an elastomeric rubber-based insulation that achieves 90°C continuous rating. Unlike XLPE, EPR remains flexible at low temperatures and resists ozone cracking, making it the preferred insulation for outdoor and marine applications.

**Strengths:**
- Excellent flexibility — remains pliable in cold conditions down to −40°C
- Excellent ozone resistance — does not crack in outdoor or coastal environments
- Good chemical resistance — suitable for chemical process plant
- 90°C continuous rating with good short-circuit withstand
- Better mechanical impact resistance than XLPE

**Limitations:**
- More expensive than XLPE
- Not as easily terminated as PVC or XLPE — requires specialist rubber cable glands
- Higher moisture absorption than XLPE — not ideal for buried applications unless PE outer sheathed

**Typical applications:**
- Marine and offshore (coastal power distribution, marine vessels, offshore platforms)
- Railway rolling stock and trackside equipment
- Mining and tunnel installations
- Outdoor flexible power cables (generators, temporary supplies)
- Nuclear and hazardous area installations where EPR's fire behaviour is superior

---

## LSZH / LS0H (Low Smoke Zero Halogen) Cables

**Standards:** IEC 60332-3 (fire propagation), IEC 61034 (smoke density), IEC 60754-1 (halogen content), IEC 60754-2 (acidity/corrosivity).

LSZH cables use a halogen-free flame-retardant compound (typically thermoplastic polyolefin — TPO or HFFR compound) instead of PVC. When burned, they produce minimal smoke and no halogen acid gases. In a fire, HCl from PVC corrodes electronics and building fabric; LSZH compounds produce CO₂ and water — far less corrosive and less toxic.

**Strengths:**
- Very low smoke emission in fire — IEC 61034 minimum 60% light transmittance
- No halogen acid gas — no corrosion of electronics or building structure during or after a fire
- Mandatory in many applications: occupied buildings, data centres, transportation, public infrastructure
- Self-extinguishing; IEC 60332-3 flame retardant for bunch wiring

**Limitations:**
- Significantly more expensive than PVC: 30–80% premium depending on grade
- Less mechanically robust than PVC — more easily damaged during installation
- Older LSZH compounds were stiffer at low temperatures — modern grades are much improved
- Minimum installation temperature: −5°C (check with manufacturer for cold-climate installation)
- Some grades have lower chemical resistance than PVC — check compatibility with installation environment

**Typical applications:**
- All internal wiring in public buildings, offices, retail, schools, hospitals where smoke hazard is unacceptable
- Data centres and IT rooms — LSZH mandatory to protect equipment from HCl damage
- Railways, metro, and underground stations — critical occupant safety
- Marine passenger vessels — IMO requirements mandate LSZH in accommodation spaces
- Residential multi-occupancy buildings — increasingly mandatory in European and African building codes

**Design note:** Specifying LSZH is not always sufficient. Check whether IEC 60332-3 (bunch fire propagation) is required — a LSZH cable installed as a single cable on a surface (Method C) may not need 60332-3; the same cable type installed in a large bundle in a riser does.

---

## SWA (Steel Wire Armoured) Cables

**Standards:** IEC 60502-1 (LV power cables with metallic armouring), IEC 60228 (conductors).

SWA cables have an inner PVC or XLPE insulation, a bedding layer, a layer of helically applied steel wires (the armour), and an outer PVC or LSZH sheath. The steel armour provides mechanical protection against crushing, rodent attack, and physical damage. SWA cables are the standard for underground direct-buried power cables, outdoor above-ground routes subject to mechanical risk, and industrial installations where cables must survive accidental mechanical contact.

**Strengths:**
- Excellent mechanical protection — armour survives light vehicular run-over, pick-and-shovel accidental contact
- Steel armour can be used as the circuit protective conductor (CPC) in TN systems — eliminates a separate earth conductor in underground installations
- Long service life when properly buried — 40+ years for PVC/SWA/PVC
- Wide range of sizes — 1.5mm² to 630mm² copper, 25mm² to 630mm² aluminium
- Available with LSZH outer sheath (SWA/LSF) for installations where fire performance is required

**Limitations:**
- Heavier and less flexible than unarmoured cables — routing in tight spaces requires care
- Steel armour must be correctly earthed at both ends for single-core cables; at one end only for multi-core (to avoid circulating eddy currents in single-core SWA)
- Steel armour is a parallel earth path — its impedance contributes to the circuit's Zs value
- Aluminium wire armour (AWA) is used for single-core large cables to avoid magnetic eddy current losses

**Typical applications:**
- Underground direct-buried cables (from substation to distribution point, from distribution board to remote buildings)
- Outdoor exposed routes (rooftop, external walls, equipment yard)
- Industrial plant (mechanical risk areas, areas with forklift traffic)
- Distribution cables in Africa and developing countries where cable theft is a risk (SWA is harder to strip and less attractive to thieves than unarmoured cable)

**Earthing SWA armouring correctly:**
The steel wire armour must be earthed at both cable termination points using an SWA gland with earth tag. Failure to earth the armour leaves it at a hazardous floating potential. For single-core SWA cables ≥95mm² carrying significant AC current, the armour must be earthed at one end only per phase (or a cross-bonded scheme used) to prevent circulating currents. Consult the cable manufacturer for large single-core SWA installations.

---

## MICC (Mineral Insulated Copper Clad) Cables

**Standards:** IEC 60702-1 (mineral insulated cables), IEC 60702-2 (terminations).

MICC cables consist of copper conductors (solid, annealed) surrounded by compressed magnesium oxide powder insulation within a copper outer sheath. There are no organic materials whatsoever. This makes MICC the most fire-resistant cable type available — it remains functional at temperatures up to 950°C for extended periods and does not contribute to fire load.

**Strengths:**
- Fire integrity maintained up to 950°C — circuit continues to function during and after severe structural fire. Essential for fire alarm, emergency lighting, sprinkler pump, and smoke extraction circuits.
- No organic materials — zero fire load, zero smoke, zero toxic emissions from the cable itself
- Extremely long service life — 50+ years with no degradation in normal environments
- Small overall diameter for conductor cross-section
- Suitable for use in explosive atmospheres (hazardous areas — Ex i, Ex e, Ex d)
- Can be operated continuously at 105°C (bare) or 70°C (PVC-oversheathed)

**Limitations:**
- Very high cost — 4–8× the cost of PVC cable of equivalent size
- Magnesium oxide is hygroscopic — cable ends must be sealed immediately on termination. Moisture ingress destroys the insulation resistance. Storage requirements are strict.
- Specialist terminations required — MICC pot terminations with compound seals. Not field-repairable without termination kits.
- Very low flexibility — tight bending radii are not achievable. Route planning must be done before laying.
- Difficult to reroute or extend without skilled labour

**Typical applications:**
- Fire alarm circuits where circuit integrity during fire is mandatory (IEC 60332-3 Category C or E maintained circuit)
- Emergency lighting circuits in buildings with mandatory escape route maintenance
- Smoke extraction fan power supplies
- Sprinkler pump power supplies in buildings where these must function during fire
- High-temperature industrial processes (furnaces, kilns, autoclaves)
- Nuclear power stations and hazardous area installations

**Design note:** For most fire-integrity applications, specifying MICC implies accepting a significant cost premium. Alternative fire-rated cables (armoured cables with fire-rated insulation compounds, FP200 type in UK — but see BS7671 layer for UK-specific fire-rated cables) may meet the fire integrity requirement at lower cost. Check the required fire-integrity standard: E30, E60, E90 (circuit functional for 30/60/90 minutes in the relevant fire test) and verify which cable type achieves it.

---

## Summary: Selection Guide

| Cable Type | Max Temp | Mechanical | Smoke/Fire | Cost | Primary Use |
|-----------|----------|-----------|------------|------|-------------|
| PVC 70°C | 70°C | Good | Poor — HCl | Lowest | General building wiring, conduit, trunking |
| XLPE 90°C | 90°C | Good | Poor — HCl | Low+ | Higher-density sizing, underground mains |
| EPR 90°C | 90°C | Excellent | Moderate | Medium | Marine, outdoor, cold-climate flexible |
| LSZH 70°C | 70°C | Moderate | Excellent — no halogen | High | Occupied buildings, data centres, transport |
| SWA PVC/XLPE | 70/90°C | Excellent | Poor (PVC sheath) | Medium | Underground, outdoor, mechanical risk |
| SWA LSZH | 70/90°C | Excellent | Excellent | High | Underground in occupied buildings |
| MICC | 105°C | Excellent | None — no organics | Very High | Fire-integrity circuits, life-safety systems |

When specifying cables for a project, the specification should always state:
1. Conductor material (copper or aluminium)
2. Insulation type (PVC 70°C, XLPE 90°C, EPR 90°C, LSZH)
3. Armouring (SWA, AWA, unarmoured)
4. Outer sheath (PVC, LSZH, PE for underground)
5. Minimum installation method and rating basis (IEC 60364-5-52 reference method)
6. Fire performance requirements if applicable (IEC 60332, IEC 61034, IEC 60754 class)
