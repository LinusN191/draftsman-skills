# NFPA 70E Annex K — General Electrical Hazards

NFPA 70E:2024 Annex K provides foundational context for the categories of electrical hazards that NFPA 70E addresses. Understanding hazard categorization and control hierarchy is central to all work on or near electrical equipment.

## Categories of electrical hazard

Electrical work exposes individuals to four primary hazard classes:

### Electric shock (electrocution)

- Contact with energized conductors at voltage sufficient to cause cardiac arrhythmia, muscle paralysis, or respiratory failure
- Severity depends on current magnitude, duration, and path through body
- Thresholds per IEC 60479 and NFPA 70E §110.2:
  - AC 50–100 mA: Ventricular fibrillation
  - AC 1–5 mA: Perception and involuntary muscle contraction
  - DC: Generally higher tolerance due to different physiological response
- Fatal outcomes possible above ~100 mA for 100 ms exposure

### Arc-flash / thermal burn

- Radiant heat from an electrical arc (ionized air channel between conductors)
- Temperature at arc column: 19,000 K (comparable to surface of sun)
- Incident energy (cal/cm²) quantifies thermal energy reaching worker at a specific working distance
- Primary protection: distance, insulating barriers, and arc-rated PPE per incident energy

### Arc-blast / pressure wave

- Explosive expansion of ionized air and vaporized conductor material
- Shock wave pressure can cause physical trauma (hearing loss, lung injury, flying object impact)
- Secondary injury risk: worker blown back into energized equipment or structural hazards
- More severe at higher voltages and higher short-circuit capacities

### Electrical burn (contact burns)

- Direct contact with energized surfaces or secondary arcs
- Skin burns from RF heating where contact resistance is high
- Typically lower incident energy than arc-flash flash-over burns, but localized and severe

## The hazard control hierarchy

NFPA 70E establishes a priority order for hazard control, aligned with industrial safety practice:

### Tier 1: Elimination

Remove the hazard entirely:
- De-energize equipment before work (preferred method)
- Substitute with lower-voltage or non-electrical equipment
- Permanently disconnect hazardous equipment from service

**Effort:** Usually highest initial effort, but eliminates risk entirely.

### Tier 2: Substitution

Replace hazardous equipment with safer alternative:
- Swap high-impedance equipment (arc-resistant switchgear) for conventional switchgear
- Use insulating tools rated for working voltage
- Install electronic monitoring to reduce live-work frequency

**Effort:** Moderate; requires capital investment but reduces long-term exposure.

### Tier 3: Engineering controls

Isolate workers from the hazard through design:
- Insulating barriers and enclosures
- Automatic shut-off devices (arc-flash relay protection, ground-fault protection)
- Working distance maximization (long-reach test equipment, remote monitoring)
- Voltage reduction (working on LV side of transformer rather than HV)

**Effort:** Varies; typically implemented at design and installation phase.

### Tier 4: Administrative controls

Reduce exposure through work practice and process:
- Lockout/tagout procedures to ensure equipment remains de-energized
- Limiting work scope (maintenance windows, restricted access)
- Hazard awareness training
- Two-person rule for high-risk tasks
- Work permits and sign-off protocols

**Effort:** Lower capital cost; depends on worker compliance and enforcement.

### Tier 5: PPE (Last resort)

Protect worker if hazard cannot be eliminated or controlled:
- Arc-rated clothing and face protection
- Rubber insulating gloves and sleeves
- Hard hats and hearing protection
- Safety glasses and face shields
- **Critical caveat:** PPE only mitigates consequence, not the hazard itself. Do not rely on PPE when elimination/substitution/engineering controls are feasible.

**Effort:** Relatively low capital cost, but ongoing inspection, replacement, and training required.

### Selection principle

When planning electrical work:

1. **First, ask:** Can this task be done with equipment de-energized? (Elimination)
2. **If no:** Can we install barriers or remote monitoring? (Engineering controls)
3. **If impractical:** Can we limit exposure time or use two-person teams? (Administrative)
4. **Only then:** Issue appropriate PPE and ensure worker training (PPE)

Effective programs use a combination of all five tiers.

## The Heinrich pyramid for electrical incidents

Heinrich's occupational safety pyramid (1931, extended by later research) estimates:

- **1 fatality** (typically electrical shock or severe arc-flash)
- **29 serious injuries** (non-fatal arc-flash burns, non-fatal shock)
- **300 minor injuries** (small shocks, minor burns, eye flash from arc)
- **1000 near-misses** (momentary contact, alarm signals, equipment damage)

Application to electrical work:

- Near-miss investigation is as critical as incident investigation; it identifies control gaps before fatalities occur
- Every minor incident should trigger a review of hazard controls
- Absence of reported incidents does NOT indicate absence of hazard; active monitoring and auditing required

## Standard electrical hazards by equipment type

### Switchgear and circuit breakers

Hazards:
- Arc-flash during fault clearing
- Shock from energized bus or component parts
- Mechanical hazard from operating mechanisms

Controls:
- Use arc-resistant switchgear where risk is high (Tier 3)
- Lockout/tagout before maintenance (Tier 4)
- Arc-rated gloves and face shield for diagnostics (Tier 5)

### Transformers

Hazards:
- High-voltage primary winding (shock, arc-flash)
- High-amperage secondary (arc-flash, thermal burn)
- Insulation failure over time

Controls:
- Ensure primary is de-energized before secondary work
- Use insulating tools on secondary if live testing required
- Thermal imaging to identify hotspots (Tier 3)

### Motors and driven equipment

Hazards:
- Stored mechanical energy (rotating shafts, compressed springs, gravity loads)
- Electrical hazard (shock, arc-flash) during maintenance
- Unexpected startup due to automatic restart circuits

Controls:
- Lockout mechanical moving parts in addition to electrical de-energization
- Verify motor has fully coasted to stop before touching
- Label automatic-start circuits clearly (Tier 4)

### Batteries and DC systems

Hazards:
- High short-circuit current capacity despite "low voltage" (often 48–600V DC)
- Explosive arc-flash in confined spaces (battery rooms)
- Chemical hazards from battery electrolyte or gas venting

Controls:
- Use insulated tools and wear arc-rated PPE (DC incident energy often exceeds AC at same voltage)
- Ensure adequate ventilation if hydrogen/oxygen gas present
- Plan escape routes before entry to confined spaces (Tier 4)

### Photovoltaic (PV) systems

Hazards:
- String voltage can remain high even when main disconnect is open (series-connected cells)
- Back-feed through PV during sunlight (difficult to fully de-energize)
- DC arc-flash hazard (high temperature, long duration arc in DC systems)

Controls:
- Install additional dedicated DC disconnect switches upstream of inverter
- Use infrared thermography to locate open-circuit or shaded modules (Tier 3)
- Work on DC portions only during night hours or with string covered (Tier 4)
- Wear full DC arc-rated PPE for high-voltage string work (Tier 5)

## Risk assessment framework

Before starting any electrical work:

1. **Identify the hazard type:** Shock, arc-flash, arc-blast, thermal burn, or combination
2. **Estimate severity:** Refer to thresholds (incident energy for arc, voltage class for shock)
3. **Determine control tier:** Apply hierarchy from elimination to PPE
4. **Verify compliance:** Ensure all selected controls meet relevant NFPA 70E article requirements
5. **Train and document:** Ensure workers understand task-specific hazards and assigned controls

**Reference:** NFPA 70E:2024 Article 110 (General) and Annex K.
