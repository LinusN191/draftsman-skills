# Inspection and Testing (BS 7671 Part 6)

The verification regime for electrical installations under BS 7671.
Inspection and testing are not optional — every installation must be
verified before being put into service, and periodically thereafter.

---

## When inspection and testing applies

| Trigger | Type of verification |
|---------|---------------------|
| New installation completed | Initial Verification → Electrical Installation Certificate (EIC) |
| Addition or alteration | Initial Verification of new work → EIC or Minor Works Certificate |
| Periodic check | Periodic Inspection → Electrical Installation Condition Report (EICR) |
| Change of use / occupancy | Periodic Inspection often triggered by landlord/insurer |
| After fault or failure | Targeted inspection of affected circuit |

---

## Part 6 structure

| Chapter | Title | Content |
|---------|-------|---------|
| 64 | Initial verification | First inspection and test of a new installation |
| 65 | Periodic inspection and testing | Subsequent inspections during the life of an installation |
| 66 | Certification and reporting | Document formats — EIC, Minor Works, EICR |

---

## Initial Verification — Chapter 64

The sequence of tests prescribed by Reg 643 must be followed in order.
Each test confirms the safety of the previous step before proceeding.

### Inspection (visual — Reg 642)

Before testing, perform visual inspection covering at minimum:
- Connection of conductors (terminations, no bare strands, correct torque)
- Identification of conductors (correct colours, labelling)
- Routing of cables in safe zones
- Selection of conductors for current-carrying capacity
- Connection of single-pole devices in line conductor only
- Correct connection of accessories and equipment
- Presence and condition of bonding conductors
- Presence and correct location of fire barriers and seals
- Erection methods (cable supports, mechanical protection)
- Equipment IP ratings appropriate to location
- Presence of diagrams, danger notices, warning labels
- Provision of isolation, switching, and emergency control
- Presence of energy-efficient features (Appendix 17)
- Labelling of protective devices

### Tests — Reg 643

Performed in this sequence:

**1. Continuity of protective conductors (Reg 643.2)**

Test: R1 + R2 measurement using a low-resistance ohmmeter.
Confirms the CPC is electrically continuous from MET to the furthest point of each circuit.

**2. Continuity of ring final circuit conductors (Reg 643.2.3)**

Test: end-to-end resistance of L, N, and CPC of each ring.
Confirms the ring is intact (no break that would convert it to a radial).

**3. Insulation resistance (Reg 643.3)**

Test: 500V DC test (250V for SELV/PELV), measure insulation resistance.
Required values:
- SELV / PELV: ≥ 0.5 MΩ
- LV up to 500V: ≥ 1.0 MΩ
- LV above 500V: ≥ 1.0 MΩ

Measure between:
- All line conductors connected together → earth
- All line conductors → neutral
- Each line → each other line (for three-phase)

**4. Protection by SELV / PELV / electrical separation (Reg 643.4)**

Test: as for insulation resistance, plus visual verification of separation.

**5. Polarity (Reg 643.6)**

Test: confirms single-pole switches and protective devices are in the LINE conductor, not the NEUTRAL.

**6. Earth electrode resistance (Reg 643.7)**

Test: required for TT systems and any installation with a supplementary earth electrode.
- Three-terminal "fall of potential" method (preferred for new electrodes)
- Stakeless / clamp method (acceptable for periodic testing where rod is already installed)
- Compare RA against required value: RA × IΔn ≤ 50V

**7. Earth fault loop impedance Zs (Reg 643.7.3)**

Test: at the furthest point of every final circuit.
Confirms Zs ≤ Zs_max from Tables 41.2/41.3.

Must be measured, not calculated — site conditions differ from design assumptions.

**8. Prospective fault current Ipf (Reg 643.7.2)**

Test: measure PSCC and PEFC at the origin of the installation.
Confirms switchgear breaking capacity is adequate.

**9. Verification of phase sequence (Reg 643.8)**

Test: three-phase installations only. Confirms correct rotation (L1, L2, L3 in order).

**10. Functional testing (Reg 643.10)**

Test: RCD operation, contactors, control gear, interlocks. Confirm correct operation.

For RCDs:
- IΔn trip time: ≤ 300 ms (general) or ≤ 40 ms (additional protection 30mA)
- 5 × IΔn trip time: ≤ 40 ms
- Test using calibrated RCD tester at appropriate test currents

**11. Verification of voltage drop (Reg 643.11)**

Where required: measure operating voltage at the furthest point of each circuit under load.
Compare against the design calculation.

---

## Periodic Inspection — Chapter 65

Existing installations are inspected to confirm continued safety. The
output is an EICR with observations classified by code.

### Recommended intervals

| Premises type | Maximum interval |
|---------------|------------------|
| Domestic — owner-occupied | 10 years |
| Domestic — rented (England) | 5 years (statutory under Electrical Safety Standards Regs 2020) |
| Commercial — offices, shops | 5 years |
| Industrial | 3 years |
| Schools, public buildings | 5 years |
| Hospitals | 5 years (more frequent in clinical areas per HTM 06-01) |
| Construction sites | 3 months |
| Caravans (touring) | 1 year (or each tenancy) |
| Petrol stations | 1 year |
| Theatres, cinemas | 3 years |
| Swimming pools | 1 year |
| Marinas | 1 year |

These are recommendations from IET Guidance Note 3 — not regulations
except where specifically cited (e.g. domestic rented in England).

### EICR observation codes

| Code | Meaning | Action |
|------|---------|--------|
| **C1** | Danger present — immediate risk of injury | Make safe immediately (isolate circuit). Notify duty holder same day. |
| **C2** | Potentially dangerous — risk could become real | Repair urgently. Installation NOT satisfactory. |
| **C3** | Improvement recommended | Not currently dangerous but doesn't meet current standard. Repair advised. |
| **FI** | Further investigation required | Inspector unable to determine safety; investigate further. |

An EICR is recorded **"UNSATISFACTORY"** if any C1 or C2 observations
are made. C3 alone does not render the report unsatisfactory.

### Common EICR findings

- C1: bare live conductors, missing covers on energised equipment, broken accessories with exposed terminals
- C2: no main bonding to gas/water, missing CPC in old wiring, RCD failing functional test, broken cable insulation
- C3: lack of RCD where currently required but original design pre-dated requirement, undersized main earthing conductor by current standards, old consumer unit with insufficient ways

---

## Certificates and reports — Chapter 66

### Electrical Installation Certificate (EIC)

Issued for new installations or major alterations. Contains:
- Designer's details and signature
- Constructor's (installer's) details and signature
- Inspector's details and signature
- Schedule of inspections (visual checks)
- Schedule of test results (one per circuit)
- Departures from BS 7671 (if any), with engineering justification

The EIC certifies that the installation:
- Complies with BS 7671 (or, where it doesn't, the departures are documented)
- Has been inspected and tested in accordance with Part 6
- Is safe to put into service

### Minor Works Certificate

For small alterations (typically additions to existing circuits without changing the existing protective devices):
- One certificate per circuit altered
- Includes the schedule of test results for the affected circuit only
- Cannot be used for additional final circuits or new distribution boards

### Electrical Installation Condition Report (EICR)

For periodic inspection of an existing installation:
- Lists observations with codes (C1, C2, C3, FI)
- Verdict: SATISFACTORY or UNSATISFACTORY
- Recommended date for next inspection
- Tests recorded (typically a sample — not necessarily 100% as for initial verification)

### Schedule of Test Results

Tabular record of test values for every circuit:
- Circuit reference and description
- Cable type and size
- Protective device type, rating, breaking capacity
- R1 + R2 (Ω)
- Insulation resistance L-L, L-N, L-PE (MΩ)
- Polarity confirmed (✓)
- Zs (Ω)
- RCD trip time at IΔn and 5×IΔn (ms)

---

## Test instrument requirements

A competent electrician must have at minimum:
- **Low-resistance ohmmeter** for R1+R2 and ring continuity (0.01 Ω resolution)
- **Insulation resistance tester** (250V, 500V, 1000V — Cat IV rated)
- **Earth fault loop impedance tester** (with no-trip mode for RCD circuits)
- **RCD tester** (× IΔn, × 0.5 IΔn, × 5 IΔn at 0°, 180°, 90°, 270°)
- **Earth electrode resistance tester** (three-terminal method)
- **Voltage indicator** (per GS38, two-pole)
- **Phase rotation indicator** (for three-phase)

Multi-function testers combine all of the above. Annual calibration required.

---

## Documentation handover

For a new installation, the consumer must receive:
- Electrical Installation Certificate (EIC)
- Schedule of Inspections
- Schedule of Test Results
- Distribution board schedule with circuit chart
- Operating instructions for control gear / protective devices
- Manufacturer's instructions for installed equipment
- Diagrams (single-line, layout, schematic as relevant)

For HMOs and rented domestic, copies must be provided to:
- Landlord (statutory under Electrical Safety Standards Regs 2020)
- Tenant (within 28 days of inspection)
- Local authority on request

---

## Departures from BS 7671

If a design or installation departs from BS 7671 (e.g. using an
alternative non-standard method), the EIC must record:
- The specific regulation departed from
- The reason for the departure
- The alternative method used
- The engineer's justification that an equivalent level of safety is achieved

Departures are not breaches — they are documented engineering decisions.
The designer takes professional responsibility for the alternative.

---

## Common issues with documentation

- EIC issued without schedule of test results attached — invalid
- Test results recorded in summary only ("all PASS") — not auditable
- Departures not documented — non-compliance becomes liability
- EICR coded too leniently (C3 where C2 is appropriate) — inspector liable
- EICR coded too harshly (C1 for code 3 issues) — unnecessary remedial cost
- No next inspection date — owner has no prompt for re-inspection
- Missing distribution board labels — circuits cannot be safely isolated

---

## CDM 2015 designer's duties

Under the Construction (Design and Management) Regulations 2015, the
designer of an electrical installation has specific duties:

- Eliminate foreseeable risks during construction, use, maintenance, and demolition (so far as reasonably practicable)
- Reduce risks that cannot be eliminated
- Provide information about residual risks (in the construction phase plan and the health and safety file)

For electrical work, this typically means:
- Designing for safe access during installation and maintenance
- Specifying live-working avoidance through isolation provisions
- Designing for safe testing (test points, accessible terminals)
- Specifying earthing/bonding such that future modifications don't compromise safety

The CDM file is part of the project handover. Electrical drawings, schedules, and the EIC form part of it.
