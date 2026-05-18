# Inspection and Testing (KS 1700 §6)

> **Verification note:** This file is authored as a draft-from-bs7671-derivative.
> KS 1700:2018 §6 adopts BS 7671 Part 6 substantially via KS Annex E.
> The Kenyan inspection regime is enforced by the Energy and Petroleum
> Regulatory Authority (EPRA) under the Energy Act 2019. Promote
> `verification_status` once verified clause-by-clause against the
> published KS 1700:2018 PDF.

The verification regime for electrical installations under KS 1700.
Inspection and testing are not optional — every installation must be
verified before being put into service, and periodically thereafter
under the EPRA inspection regime.

---

## Kenya supply context

In Kenya the inspection-and-testing process is overlaid by statutory
EPRA enforcement:

- All inspection certificates must be **signed by an EPRA-registered
  electrical contractor**. Self-certification by the consumer or by an
  unregistered installer is invalid.
- EPRA maintains classes of contractor licensing (A-1 through C-3) — the
  contractor class must match the installation scale.
- Test instruments used must be calibrated and traceable to the Kenya
  National Bureau of Standards (KENAS-accredited calibration laboratories).
- Test results are recorded in the **KS-standard Electrical Installation
  Certificate (EIC)**, which mirrors the BS EIC shape with Kenya-specific
  header fields (KPLC Wayleave reference, EPRA contractor licence number,
  KEBS certification marks on consumer unit + protective devices).

---

## When inspection and testing applies

| Trigger | Type of verification |
|---|---|
| New installation completed | Initial Verification → Electrical Installation Certificate (KS EIC) |
| Addition or alteration | Initial Verification of new work → KS EIC or Minor Works Certificate |
| Periodic check | Periodic Inspection → Electrical Installation Condition Report (KS EICR) |
| Change of use / occupancy | Periodic Inspection often triggered by landlord/insurer |
| After fault or failure | Targeted inspection of affected circuit |

---

## KS §6 structure (mirrors BS Part 6 via Annex E)

| Chapter | Title | Content |
|---|---|---|
| §6.1 | Initial verification | First inspection + test of a new installation |
| §6.2 | Periodic inspection and testing | Subsequent inspections during the life of the installation |
| §6.3 | Certification and reporting | KS EIC, Minor Works, KS EICR |

---

## Initial Verification — KS §6.1

The sequence of tests prescribed by KS §6.1.3 must be followed in order
(adopts BS Reg 643 verbatim). Each test confirms the safety of the
previous step before proceeding.

### Inspection (visual — KS §6.1.2)

Before testing, perform visual inspection covering at minimum:
- Connection of conductors (terminations, no bare strands, correct torque)
- Identification of conductors (correct colours per KS Annex C, labelling)
- Routing of cables in safe zones
- Presence of bonding conductors (especially KS §544 main bonding)
- Equipment IP ratings appropriate to location (Kenya-specific: IP65 minimum outdoors in coastal zones)
- Presence of diagrams, danger notices, warning labels
- Provision of isolation, switching, emergency control
- Labelling of protective devices
- **Kenya-specific: KEBS certification marks present on consumer unit, MCBs/RCBOs, accessories**

### Tests — KS §6.1.3

Performed in this sequence (adopts BS Reg 643):

1. **Continuity of protective conductors** — R1 + R2 measurement, confirms CPC continuous from MET to furthest point.
2. **Continuity of ring final circuits** — end-to-end resistance of L, N, CPC of each ring.
3. **Insulation resistance** — 500V DC test (250V for SELV/PELV). Minimum 1.0 MΩ for LV; 0.5 MΩ for SELV/PELV.
4. **Protection by SELV / PELV / electrical separation** — as for insulation resistance + visual separation check.
5. **Polarity** — confirms single-pole devices in LINE conductor only.
6. **Earth electrode resistance** — required for TT systems (common in off-grid Kenyan installations). Fall-of-potential method preferred; stakeless acceptable for periodic.
7. **Earth fault loop impedance Zs** — at furthest point of every final circuit; compare to Zs_max from KS Tables 41.2/41.3.
8. **Prospective fault current Ipf** — measure PSCC + PEFC at origin; confirms switchgear breaking capacity adequate. KPLC declared PFC on the Letter of Information cross-checks against the measured value.
9. **Verification of phase sequence** — three-phase installations only.
10. **Functional testing** — RCD operation, contactors, control gear. RCD trip times: ≤ 300 ms at IΔn; ≤ 40 ms at 5×IΔn.
11. **Verification of voltage drop** — where required, measure operating voltage at the furthest point under load.

---

## Periodic Inspection — KS §6.2 (EPRA Regime)

The EPRA inspection regime is **statutory** in Kenya, unlike the IET
guidance-note recommendations under BS. The intervals are enforced by
EPRA:

### EPRA-mandated intervals

| Premises type | Maximum interval |
|---|---|
| Domestic — owner-occupied | **10 years** (EPRA regime) |
| Commercial — offices, shops | **5 years** (EPRA regime) |
| Industrial | **5 years** (EPRA regime; some hazardous occupancies tighter) |
| Schools, public buildings | **5 years** |
| Hospitals | **5 years** (more frequent in clinical areas per Ministry of Health guidance) |
| Petrol stations | **1 year** |
| Construction sites | **3 months** (matches BS practice) |

A periodic inspection certificate signed by an EPRA-registered contractor
is required at the end of each interval.

### KS EICR observation codes

KS adopts the BS coding framework:

| Code | Meaning | Action |
|---|---|---|
| **C1** | Danger present — immediate risk of injury | Make safe immediately. Notify duty holder same day. |
| **C2** | Potentially dangerous — risk could become real | Repair urgently. Installation NOT satisfactory. |
| **C3** | Improvement recommended | Not currently dangerous; repair advised. |
| **FI** | Further investigation required | Inspector unable to determine safety. |

An EICR is **UNSATISFACTORY** if any C1 or C2 observations are made.

### Common findings in Kenya practice

- C1: bare live conductors at outdoor terminations degraded by UV / humidity (coastal sites); missing covers on energised KPLC service heads.
- C2: no main bonding to water service entry (frequent in older Nairobi domestic stock); missing CPC in legacy installations; RCD failing functional test.
- C3: lack of 30mA socket RCD where KS §411.3.3 currently requires it but original design pre-dated 2018; undersized main earthing conductor by current standards.

---

## Certificates and reports — KS §6.3

### KS Electrical Installation Certificate (KS EIC)

Issued for new installations or major alterations. Contains:
- Designer's details + signature
- Constructor's (installer's) details + signature
- Inspector's details + signature
- **EPRA contractor licence number** (Kenya-specific)
- **KPLC Wayleave reference** (Kenya-specific)
- Schedule of inspections (visual checks)
- Schedule of test results (one per circuit)
- Departures from KS 1700 (if any), with engineering justification

### Minor Works Certificate

For small alterations without changing existing protective devices.
Same shape as BS Minor Works Certificate.

### KS Electrical Installation Condition Report (KS EICR)

For periodic inspection of an existing installation. Lists observations
with codes (C1, C2, C3, FI). Verdict: SATISFACTORY or UNSATISFACTORY.
Recommended date for next inspection (subject to EPRA-mandated maximum
interval above).

### Schedule of Test Results

Tabular record of test values for every circuit — adopts BS schedule
shape. Includes circuit reference, cable type/size, protective device
ratings, R1+R2, insulation resistance, polarity, Zs, RCD trip times.

---

## Test instrument requirements

A competent Kenyan electrician must have at minimum:
- Low-resistance ohmmeter (0.01 Ω resolution)
- Insulation resistance tester (250V, 500V, 1000V — Cat IV rated)
- Earth fault loop impedance tester (with no-trip mode for RCD circuits)
- RCD tester (× IΔn, × 0.5 IΔn, × 5 IΔn at 0°/180°/90°/270°)
- Earth electrode resistance tester (three-terminal method) — **critical for TT installations common in off-grid Kenya**
- Voltage indicator (two-pole, GS38 equivalent)
- Phase rotation indicator (for three-phase)

Annual calibration to KENAS-accredited laboratory required.

---

## Documentation handover

For a new Kenyan installation, the consumer must receive:
- KS Electrical Installation Certificate (KS EIC)
- Schedule of Inspections
- Schedule of Test Results
- Distribution board schedule with circuit chart
- KPLC Letter of Information (declared Ze + PFC at intake)
- Manufacturer's instructions for installed equipment
- Diagrams (single-line, layout, schematic as relevant)

A copy of the KS EIC is also filed with EPRA for installations above
defined size thresholds (typically commercial / industrial).

---

## Common errors in Kenya practice

- KS EIC issued without EPRA contractor licence number — invalid.
- KPLC Wayleave reference omitted — cannot trace supply data later.
- Test results recorded in summary only ("all PASS") — not auditable; EPRA inspection failure.
- Periodic interval slipped past the EPRA-mandated maximum — operating without valid certificate is a statutory offence.
- Equipment without KEBS certification mark installed — non-compliant; EPRA inspection failure.
- TT installations (off-grid solar) commissioned without earth electrode resistance test — fails KS §411.5.2.

---

## See also

- `KS1700/terminology.md` — EPRA + KEBS + KPLC vocabulary
- `KS1700/compliance-checklist.md` — engineer-facing §6 checklist
- `KS1700/earthing-systems-explained.md` — TN / TT verification differences
- `BS7671/inspection-and-testing.md` — parent BS Part 6 text adopted by KS Annex E
