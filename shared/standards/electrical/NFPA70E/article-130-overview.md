# NFPA 70E:2024 — Article 130 Overview

Article 130 is the central framework for work on or near energized electrical equipment. It addresses when and how to work safely on live systems, defining mandatory boundaries, assessment processes, and PPE selection pathways. Article 130 assumes workers are qualified (trained and authorized) and establishes the hierarchy: de-energize when possible, apply boundaries and controls when energized work is required.

## §130.1 General

Defines the scope and applicability of Article 130: it applies to all employees working on or near energized electrical systems. The section establishes that work authorization and hazard assessment are prerequisites. Key decision point: Is the work location within an Energized Electrical Work Area (EEWA), or is it outside equipment but near energized parts?

## §130.2 Electrically Safe Work Condition (ESWC)

Specifies when electrical equipment must be de-energized and brought to an ESWC before work. An ESWC means all parts are de-energized, isolated, and verified to be safe. Per §130.2(A), equipment must be de-energized unless de-energizing would create an additional hazard (e.g., shutdown of critical life-safety loads). When ESWC is mandated:
- Lockout/tagout (LOTO) procedures per §110.43 are required
- Verification that de-energization is complete per §110.44
- Only qualified persons may perform LOTO

When energized work is justified under §130.2(A), an Energized Work Permit (EWP) per §130.5(F) must be issued and signed.

## §130.3 Precautions Against Electrical Hazard

Establishes general precautions for all work near energized parts, whether de-energized work or energized work. Key precautions:
- All energized electrical equipment must be treated as live until verified otherwise
- Insulated tools, insulating mats, and rubber gloves must be used when required
- A second qualified person (observer or safety watch) should be present
- No metallic jewelry, watches, or loose clothing that could bridge across energized parts
- Barricades and signs must prevent unqualified persons from entering the work area

These precautions apply across Article 130 and support both shock risk control and arc-flash protection.

## §130.4 Shock Risk Assessment and Shock Approach Boundaries

Addresses the hazard of electrical shock when a person makes contact with an energized part. The section establishes two approach boundaries:

**§130.4(C)(a) AC Shock Approach Boundaries:**
- Limited Approach Boundary (LAB): typically 10 feet from energized parts (>50 V AC)
- Restricted Approach Boundary (RAB): typically 3–4 feet depending on voltage (requires specialized PPE and qualifications)
- Prohibited Approach Boundary (PAB): actual contact with the conductor (work only permitted with full LOTO and verification)

**§130.4(C)(b) DC Shock Approach Boundaries:**
- LAB: 3 feet from energized parts (>50 V DC)
- RAB: 1 foot
- PAB: actual contact

Boundaries are specified in Table 130.4(C)(a) and Table 130.4(C)(b), indexed by voltage. Shock risk assessment is independent of arc-flash risk and must be performed separately; a location may have no arc-flash hazard but still require shock precautions.

## §130.5 Arc Flash Risk Assessment

The mandatory process to determine whether an arc-flash hazard exists and, if so, to assign the required PPE category. §130.5 is the longest and most complex section, driving every arc-flash label and every energized work permit.

**§130.5(A) – §130.5(B): Hazard Identification and Likelihood Assessment**
- Determine whether the equipment and task could plausibly produce an arc-flash event
- Use Table 130.5(C) to determine likelihood: "likely" (probable) or "possible" (lower probability)
- If no arc-flash hazard is credible, no arc-flash PPE is required (but shock PPE may still be needed)

**§130.5(E) – §130.5(G): Incident Energy Determination — Two Pathways**

Pathway 1: Calculation (IEEE 1584 or NFPA 70E Annex D)
- Compute incident energy from short-circuit fault current, device clearing time, and distance
- Compare against ATPV (Arc Thermal Performance Value) of candidate PPE
- Select PPE category from Table 130.7(C)(15)(c) based on incident energy result

Pathway 2: Equipment Table Method (§130.5(G))
- Use Table 130.5(G), which pre-assigns typical incident energies and PPE categories for common equipment types and voltage levels
- Faster, requires no calculation; acceptable per the standard when likelihood from §130.5(C) is "possible" (not "likely")

**§130.5(H) – Labeling**
- Every piece of equipment where an arc-flash hazard exists must bear an arc-flash label
- Label must display the estimated incident energy (in cal/cm²) and the required PPE category
- Labels are affixed per Table 130.5(H) requirements; re-labeling is required if system changes

**§130.5(F) – Energized Work Permit (EWP)**
- When energized work is performed, a written EWP must be completed and signed by a qualified supervisor
- EWP documents: date, time, equipment, hazard analysis, PPE category, rescue procedures, hot-work justification
- EWP is retained per §130.5(F)(1)

## §130.7 Personal Protective Equipment (PPE)

Specifies the selection, use, and maintenance of arc-rated PPE. §130.7 is organized by task type and energy level.

**§130.7(C)(15)(a) – AC Tasks and Predicted Incident Energy**
- Table 130.7(C)(15)(a) lists common AC tasks (e.g., arc-flash boundary assessment, maintenance on transformers, switchgear operation) and pre-assigned PPE categories
- Allows quick selection without detailed incident-energy calculation if the task matches an entry
- Categories range from 1 (≤ 2 cal/cm²) to 4 (> 8 cal/cm²)

**§130.7(C)(15)(b) – DC Tasks and Predicted Incident Energy**
- Table 130.7(C)(15)(b) addresses DC systems, which have different arc characteristics and typically lower clearing times
- Provides task-based PPE selection for DC circuits and batteries

**§130.7(C)(15)(c) – PPE Categories by Incident Energy**
- Table 130.7(C)(15)(c) correlates incident energy (in cal/cm²) to PPE category
- Used when incident energy has been calculated
- Categories 1–4 define minimum garment ATPV and required clothing ensemble

**§130.7(C)(16) – Required Clothing and Equipment per Category**
- Table 130.7(C)(16) specifies the garment combination required for each PPE category
- Example, Category 2: FR shirt, FR pants, arc-rated hood (ATPV ≥ 4), hard hat, face shield, safety glasses, hearing protection, leather gloves, leather shoes
- All items must be arc-rated and match the assigned category

**§130.7(E) – Care and Maintenance**
- AR clothing must be inspected before each use
- Damaged or contaminated AR garments must be retired
- Laundering must use approved AR-compatible detergents to preserve ATPV

## §130.8 Other Protective Equipment

Covers auxiliary protection beyond PPE clothing:
- Insulating blankets and arc-rated face shields
- Insulating gloves and mats
- Insulated tools and test equipment
- Hot sticks and overhead line tools

§130.8 ensures that the full toolkit of electrical safety equipment is deployed when working on or near energized systems.

## Cross-Cutting Relationships

- **§130.2 ↔ §130.5:** If §130.2 allows energized work (cannot be de-energized), then §130.5 assessment is mandatory
- **§130.4 ↔ §130.5:** Both must be assessed independently; shock and arc-flash controls are not equivalent
- **§130.5 ↔ §130.7:** Incident energy result (§130.5) feeds directly into PPE selection (§130.7)
- **§130.3 precautions apply to all work:** General precautions (tools, training, observers) underpin all Article 130 work

## Related Standards Referenced in Article 130

- NFPA 79 — Electrical Standard for Industrial Machinery
- IEEE 1584 — Guide for Performing Arc-Flash Hazard Calculations
- NFPA 70E Annex D — Alternative Incident Energy Calculation Methods (Doan, Stokes–Oppenlander)
- Table cross-references to NFPA 70 (National Electrical Code) for voltage definitions and equipment classifications
