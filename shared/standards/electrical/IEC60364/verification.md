# IEC 60364-6 — Verification: Initial Verification and Periodic Inspection

Reference: IEC 60364-6:2016+AMD1:2023

---

## Purpose and Scope

IEC 60364-6 establishes the requirements for verifying that a completed electrical installation satisfies the requirements of IEC 60364 before it is put into service (initial verification), and for confirming through periodic inspection that an installation in service continues to meet those requirements.

Verification is not the same as commissioning. Commissioning confirms that equipment operates as intended. Verification confirms that the installation is safe — that it would not cause injury or damage under foreseeable fault conditions.

Every new installation, extension, or alteration must undergo initial verification before being energised and put into service. The verifying engineer must be a competent person with knowledge of the installation and access to the design documentation.

---

## Initial Verification — Sequence

IEC 60364-6 Clause 61.1 requires inspection to precede testing. This is a mandatory sequence — it is not acceptable to test first and inspect after. The reason is that testing an installation with obvious visible defects wastes time and may create dangerous conditions.

### Phase 1: Inspection (before testing, before energising)

Visual inspection verifies that the installation as built conforms to the design and to the general requirements of IEC 60364. The inspection is carried out with the installation de-energised.

**Inspection items include:**

- Correct identification and labelling of all circuits — circuit schedule must match the installation
- Protection against electric shock — correct IP rating, no live parts exposed, correct clearances
- Prevention of mutual detrimental influence — electrical separation from other services (gas, water), correct segregation of circuits by voltage class
- Selection of conductors — cable types, cross-sections, and insulation appropriate for the circuits as installed
- Switching and isolation — isolating means present for all equipment, emergency switching accessible
- Connection devices — all terminations visible, accessible, properly made, no mechanical damage
- Protection against thermal effects — cables not in contact with thermal insulation unless rated for it, no cables overloaded by proximity to heat sources
- Protective conductors — CPCs present and correctly sized throughout, all earthing connections made
- Earthing arrangements — main earthing terminal present, earthing electrode connection made and labelled, all bonding conductors in place
- Correct devices — MCBs, fuses, RCDs of the specified ratings installed as designed
- Documentation — circuit charts, single-line diagrams, warning notices present

### Phase 2: Testing (after inspection passes)

Testing is conducted in the following sequence. Each test must pass before proceeding to the next — a failed test must be investigated and corrected before the sequence continues.

**Test 1: Continuity of protective conductors (CPCs) — Clause 61.3.3**

Verifies that every circuit has a continuous, low-impedance protective conductor from the load end back to the Main Earthing Terminal (MET).

- Method: Low-resistance ohmmeter (short circuit the line and protective conductor at the distribution board, then measure resistance at each outlet — the reading is R1+R2 for that circuit)
- Pass criterion: Measured (R1+R2) consistent with design value. No open circuit. Typically <1Ω for final circuits; lower for large circuits.
- Purpose: Confirms CPCs are not broken, connected to the wrong terminal, or omitted

**Test 2: Continuity of ring final circuit conductors (where applicable) — Clause 61.3.4**

For ring circuits only. Verifies that all three conductors (line, neutral, CPC) form complete rings.

- Method: Sequential end-to-end resistance tests with conductors crossed
- Pass criterion: Consistent readings indicating complete rings without joins or spurs that interrupt the ring

**Test 3: Insulation resistance — Clause 61.3.5**

Verifies that the insulation between conductors and between conductors and earth has not been damaged by the installation process.

- Test voltage: 500V DC for circuits up to 500V (standard LV installations)
- Pass criterion: ≥ 1 MΩ between each live conductor and earth (with line and neutral joined together); ≥ 1 MΩ between line and neutral
- Precautions: Disconnect all equipment that contains capacitors, surge protection devices, or voltage-sensitive electronics before testing — these will fail at 500V DC and may be damaged. Disconnect dimmers and ELV transformers. Test with circuits in the disconnected state at the final accessories.
- Note: Very long cables have capacitance that requires the meter to be held for 60 seconds to stabilise the reading. Readings that continue to rise are normal for long cables.

**Test 4: Polarity — Clause 61.3.8**

Verifies that line conductors are connected to line terminals, neutrals to neutral terminals, and that no single-pole switching device has been inserted in the neutral conductor of a circuit.

- Method: Continuity tester with circuit energised or from the distribution board before energising
- Pass criterion: Correct polarity at all outlets; line switches switch line only

**Test 5: Earth electrode resistance (where applicable) — Clause 61.3.7**

For TT systems and where a separate earth electrode is installed: verifies that the earth electrode resistance Ra meets the design requirement.

- Method: Three-electrode fall-of-potential test (independent current and potential electrodes spaced at 10m intervals)
- Pass criterion: For TT systems with 30mA RCD: Ra ≤ 1667Ω (since Ra × 0.030 ≤ 50V). In practice, ≤ 200Ω is recommended as a practical target for soil with normal conductivity.
- Alternative: For safety check only, a two-electrode test (clamp test) can be used on installed electrode systems

**Test 6: Earth fault loop impedance (Zs) — Clause 61.3.9**

Verifies that the earth fault loop impedance at the end of each circuit is low enough that the protective device will disconnect within the required time.

- Method: Loop impedance tester at socket outlets, at lighting points (with fittings removed or via test terminals), and at the distribution board's incoming terminals (to measure Ze)
- Pass criterion: Measured Zs (corrected to operating temperature where appropriate) ≤ Zs_max for the protective device type and rating at that point. See part4-41-electric-shock.json for Zs_max tables.
- Temperature correction: Multiply measured Zs by 1.20 for PVC cables (measurement at 20°C ambient, rated at 70°C operating) or by 1.28 for XLPE (90°C operating)
- Critical point: IEC 60364-6 AMD1:2023 permits use of measured Ze plus calculated (R1+R2) from the continuity test as an alternative to direct Zs measurement at every point.

**Test 7: RCD operation — Clause 61.3.10**

Verifies that each RCD (RCCB, RCBO) trips within the required time at IΔn.

- Test equipment: RCD tester applying calibrated residual current through the protected circuit
- Tests required:
  - At 0.5 × IΔn: RCD must NOT trip (non-operating current test)
  - At IΔn: RCD must trip within 300ms (general type) or 40ms (socket outlet RCDs)
  - At 5 × IΔn: RCD must trip within 40ms (general) or 15ms (socket outlet)
  - For S-type (selective): At IΔn, minimum 130ms non-trip, maximum 500ms trip
- Test polarity: Test at 0° and 180° phase angle (positive and negative half-cycle) for detection of waveform sensitivity
- Press test button: Manually test each RCD using its built-in test button at the start of testing — if the button test fails, the RCD is faulty and must be replaced before proceeding

**Test 8: Prospective Short-Circuit Current (PSCC) — Clause 61.3.6**

Measurement or calculation of PSCC at the origin of the installation and at main distribution boards.

- Method: PSCC tester (measures the calculated fault current from the measured loop impedance) or calculate from Ze and transformer data
- Purpose: Confirm that all devices have adequate breaking capacity for the actual PSCC
- Pass criterion: All device Icu/Icn ratings ≥ PSCC at the device installation point

---

## Documentation Requirements

IEC 60364-6 Clause 61.4 requires that test results be recorded and that a verification report be issued to the client on completion.

The verification report must include:
- Description of the installation
- Date of verification
- Details of the extent and limits of the installation verified
- All test results with instrument serial numbers and calibration dates
- Confirmation of compliance or list of departures from IEC 60364
- Signature of the responsible qualified person

Circuit schedules, single-line diagrams, and operating/maintenance instructions are handed over to the client as part of the verification documentation package.

---

## Periodic Inspection

IEC 60364-6 AMD1:2023 introduces guidance on periodic inspection intervals. An existing installation should be re-inspected periodically to confirm it remains safe.

Recommended intervals (guidance — not mandatory under IEC 60364, but many national codes mandate specific intervals):

| Installation Type | Recommended Interval |
|---|---|
| Domestic premises | Every 10 years or on change of occupancy |
| Commercial / office | Every 5 years |
| Industrial premises | Every 3 years |
| Catering establishments | Every 1 year |
| Swimming pools | Every year |
| Agricultural premises | Every 3 years |
| Construction site (temporary) | Every 3 months |
| Medical Group 2 locations | Every year |
| Caravan parks, marinas | Every year |

Periodic inspection follows the same sequence as initial verification (inspect then test). However, the full test sequence may be abbreviated by agreement with the building owner — continuity of CPCs and RCD testing are the most critical tests to repeat. Insulation resistance testing is conducted on any circuit where there is evidence of degradation.

---

## Common Failures at Verification

Understanding why installations fail verification is essential for producing compliant designs:

**Most frequent reasons for failing Zs tests:**
- Incorrect CPC size or CPC missing entirely
- Long cable runs without increasing CPC cross-section
- Using SWA armour as CPC without verifying its impedance at the far end
- Connections not made at intermediate junction boxes

**Most frequent reasons for failing insulation resistance tests:**
- PVC insulation nicked during installation or draw-in
- Moisture ingress at outdoor or concealed terminations
- SPDs and electronic ballasts left connected during test (not an installation fault — operator error)
- Insulation displacement in over-tightened terminals

**Most frequent reasons for RCD failures:**
- Neutral cross-connections between circuits (leakage current not balanced through RCD)
- RCD faulty on delivery (always test before installation)
- S-type and general-type RCDs wired in series without selectivity — S-type trips first on nuisance grounds

**Most frequent reasons for polarity failures:**
- Line and neutral transposed at socket outlets by inexperienced installers
- Single-pole switches in neutral rather than line
- L and N reversed at distribution board feeding sub-panel
