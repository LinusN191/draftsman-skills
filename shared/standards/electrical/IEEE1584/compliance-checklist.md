# IEEE 1584 — Compliance Checklist

A study satisfies IEEE 1584:2018 when ALL of the following are demonstrated.

## 1. Method choice documented
- [ ] The applicable method is declared: `ieee1584_2018` for new work, `ieee1584_2002` only for legacy reproduction.
- [ ] Voltage class is explicitly identified (600V / 2700V / 14300V).
- [ ] Electrode configuration is declared (VCB / VCBB / HCB / VOA / HOA).

## 2. Inputs sourced + cited
- [ ] Bolted fault current `I_bf` from a documented short-circuit study (IEC 60909 or equivalent).
- [ ] Working distance `D` declared per equipment type — using IEEE 1584:2018 Annex C defaults (455 mm LV / 914 mm MV) unless engineer documents otherwise.
- [ ] Gap distance `G` per equipment type from Annex C, or measured.
- [ ] Arcing time `t_arc` from upstream OCPD time-current curve at the predicted `I_arc` (not at `I_bf`).
- [ ] Box dimensions documented if non-standard (triggers §10.5 adjustment).

## 3. Worst-case scenario evaluated
- [ ] Arc-current variation (high/low bracket per §10.2) computed; the case producing **higher** incident energy is reported.
- [ ] Sensitivity to OCPD clearing time documented if multiple devices can clear the fault (selectivity question).

## 4. Output completeness
- [ ] Incident energy at the working distance: `E` in cal/cm².
- [ ] Arc-flash boundary distance: `AFB` (where E = 1.2 cal/cm²).
- [ ] PPE category from NFPA 70E Table 130.7(C)(15)(c).
- [ ] All units explicit (no unitless numbers in the report).

## 5. Documentation per IEEE 1584:2018 Annex F
- [ ] Date of analysis.
- [ ] Engineer responsible.
- [ ] All inputs and assumptions.
- [ ] Software / method used (skill version + calc tool version when DraftsMan runtime ships).
- [ ] Equipment to which the analysis applies.

## 6. Label requirements (cross-reference NFPA 70E §130.5(H))
- [ ] Arc-flash hazard label posted at each equipment where labels are required (switchgear, panelboards, MCCs, etc.).
- [ ] Label content: nominal voltage, incident energy at working distance, arc-flash boundary, required PPE category, date of analysis.
