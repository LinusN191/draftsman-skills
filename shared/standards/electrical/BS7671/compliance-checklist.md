# BS 7671 Compliance Checklist

End-of-design verification. Run this checklist before issuing a design
for tender or construction. Every item must have evidence — either a
calculation, a drawing reference, or a documented design decision.

---

## Part 1 — Cable sizing (every circuit)

| # | Check | Reference | Evidence |
|---|-------|-----------|----------|
| 1.1 | Design current Ib calculated with appropriate diversity | OSG App A; `diversity-factors.json` | Load schedule |
| 1.2 | Protective device In ≥ Ib | Reg 433.1.1 | Schedule |
| 1.3 | Cable tabulated rating It identified for actual installation method | App 4; `appendix4-cable-ratings.json` | Schedule |
| 1.4 | All correction factors applied (Ca, Cg, Ci, Cd) | App 4; `appendix4-correction-factors.json` | Schedule |
| 1.5 | In ≤ Iz_corrected | Reg 433.1.1 | Schedule |
| 1.6 | For fuses only: 1.6 × In ≤ 1.45 × Iz | Reg 433.1.1 | Schedule |
| 1.7 | Voltage drop ≤ 3% (lighting) or 5% (other), cumulative from origin | App 12; `appendix12-voltage-drop.json` | Cumulative Vd analysis |
| 1.8 | Adiabatic equation satisfied: S ≥ √(I²t)/k | Reg 434.5.2; `reg434-fault-current.json` | Fault current calc |

## Part 2 — Earthing and fault protection (every circuit)

| # | Check | Reference | Evidence |
|---|-------|-----------|----------|
| 2.1 | System earthing arrangement documented (TN-S / TN-C-S / TT) | Reg 312 | Design statement |
| 2.2 | Ze obtained from DNO or measured at origin | Reg 313.1 | DNO letter / test cert |
| 2.3 | Zs = Ze + (R1+R2) calculated for every circuit | Reg 411.4.5 | Schedule |
| 2.4 | Zs ≤ Zs_max from Tables 41.2/41.3 for the device type | Reg 411.3.2.2; `reg411-disconnection-times.json` | Schedule |
| 2.5 | Disconnection time check: 0.4s (final ≤32A or sockets) / 5s (distribution) | Table 41.1 | Schedule |
| 2.6 | For TT: RA × IΔn ≤ 50 V | Reg 411.5.3 | Earth electrode design |

## Part 3 — RCD protection

| # | Check | Reference | Evidence |
|---|-------|-----------|----------|
| 3.1 | 30mA RCD on all socket outlets ≤ 32A for general use | Reg 411.3.3 | Schedule |
| 3.2 | 30mA RCD on domestic lighting circuits (post AMD 2) | Reg 411.3.4 | Schedule |
| 3.3 | 30mA RCD on cables in walls at depth ≤ 50mm without protection | Reg 522.6.202 | Schedule / drawings |
| 3.4 | 30mA RCD in all bathroom circuits | Reg 701.411.3.3 | Schedule |
| 3.5 | RCD type matches load (A for electronic, B for EV/3-ph inverters) | Reg 531.3.3; `reg411-rcd-requirements.json` | Schedule |
| 3.6 | RCD selectivity coordinated (S-type upstream of instantaneous) | Reg 536.3 | Cascade diagram |

## Part 4 — Protection against overvoltage (SPD)

| # | Check | Reference | Evidence |
|---|-------|-----------|----------|
| 4.1 | SPD risk assessment performed (CRL or risk-based) | Reg 443.5; `reg443-spd.json` | Risk calculation |
| 4.2 | Type 1 SPD installed if LPS present (BS EN 62305) | Reg 443.4 | SLD |
| 4.3 | Type 2 SPD at main switchboard (default for commercial post-AMD 2) | Reg 443.4 | SLD |
| 4.4 | SPD coordinated with downstream Type 3 if installed | Reg 534.4.2 | Cascade diagram |
| 4.5 | SPD connecting leads ≤ 0.5m total | Reg 534.4.1 | Installation detail |
| 4.6 | SPD has dedicated overcurrent protection per manufacturer | Reg 534.4.7 | SLD |
| 4.7 | Up ≤ Uw of protected equipment (Cat III = 2.5 kV typical) | Table 44.4 | SPD selection sheet |

## Part 5 — Bonding and earthing arrangements

| # | Check | Reference | Evidence |
|---|-------|-----------|----------|
| 5.1 | Main earthing conductor sized per Table 54.7 | Reg 543.1.1 | Schedule |
| 5.2 | Main protective bonding conductor sized per Table 54.8 (PME) | Reg 544.1.1 | Schedule |
| 5.3 | All incoming services bonded (water, gas, oil, structural metal) | Reg 411.3.1.2 | Drawings |
| 5.4 | Supplementary equipotential bonding in bathrooms where needed | Reg 701.415.2 | Drawings |
| 5.5 | CPC sized per Reg 543 (not less than the formula or Table 54.7) | Reg 543.1.1/1.4 | Schedule |
| 5.6 | TT supplementary earth electrode designed for ≤ 100 Ω | Engineering judgement | Earth electrode calc |

## Part 6 — Inspection and testing

| # | Check | Reference | Evidence |
|---|-------|-----------|----------|
| 6.1 | Inspection schedule defined (BS 7671 Reg 642) | Part 6; `inspection-and-testing.md` | Spec |
| 6.2 | Tests defined: continuity, insulation, polarity, Zs, RCD, AFDD | Reg 643 | Spec / commissioning plan |
| 6.3 | Electrical Installation Certificate (EIC) issued | Reg 644 | Project handover |
| 6.4 | Minor Works Certificate (where applicable) | Reg 644 | Project handover |
| 6.5 | Schedule of Test Results attached | Reg 644 | Project handover |

## Part 7 — Special locations (where applicable)

| # | Location | Check | Reference |
|---|----------|-------|-----------|
| 7.1 | Bathrooms | Zoning correct, IPx4/IPx5/IPx7 by zone, SELV in Zone 0/1 | Section 701; `part7-special-locations.json` |
| 7.2 | Swimming pools | Equipotential bonding to all metallic parts, IP rating by zone | Section 702 |
| 7.3 | Saunas | Heat-resistant cable, 30mA RCD | Section 703 |
| 7.4 | Construction sites | Reduced LV 110V for tools, 30mA RCD | Section 704 |
| 7.5 | Agricultural | Mechanical protection mandatory, 30mA RCD | Section 705 |
| 7.6 | Caravans/marinas | TT island, one RCD per outlet | Sections 708/709 |
| 7.7 | Medical locations | Group classification, medical IT in Group 2 | Section 710 |
| 7.8 | EV charging | Type A or B RCD, open-PEN detection on PME | Section 722 |
| 7.9 | Solar PV | DC isolation, Type B RCD if no built-in detection | Section 712 |

## Part 8 — Wiring systems

| # | Check | Reference | Evidence |
|---|-------|-----------|----------|
| 8.1 | Cable selection matches installation environment | Reg 521; `reg521-installation-methods.json` | Spec |
| 8.2 | Cable supports fire-resistant where required (Reg 521.10.202) | Reg 521.10.202 | Installation detail |
| 8.3 | Cable segregation: Cat 1 / Cat 2 / Cat 3 | Reg 528 | Cable schedule / drawings |
| 8.4 | Fire-rated cables for life safety circuits | `cable-types-fire-rated.json` | Schedule / spec |
| 8.5 | Cable bending radius ≥ manufacturer minimum (typically 6×D for SWA) | Reg 522.8.3 | Installation spec |
| 8.6 | Penetrations through fire compartments fire-stopped | Reg 527.2 | Coordination drawings |

## Part 9 — Equipment selection

| # | Check | Reference | Evidence |
|---|-------|-----------|----------|
| 9.1 | Switchgear breaking capacity ≥ PSCC at point of installation | Reg 434.5.1 | Fault current calc |
| 9.2 | Switchgear assemblies to BS EN 61439 | Reg 510 | Spec / type test cert |
| 9.3 | Form of separation specified for switchboards (Form 2 / 3b / 4) | BS EN 61439-2 | Spec |
| 9.4 | IP rating selected per environment | Reg 522.3; `reg522-ip-ratings.json` | Schedule |
| 9.5 | Isolation provisions per Reg 537 | Reg 537 | SLD / spec |

## Part 10 — Documentation

| # | Check | Reference |
|---|-------|-----------|
| 10.1 | Single line diagram | BS EN 60617 conventions |
| 10.2 | Cable schedule with all design data | BS 7671 documentation |
| 10.3 | Load schedule with diversity | OSG App A |
| 10.4 | Distribution board schedules | BS EN 61439 |
| 10.5 | Earthing and bonding drawing | BS 7671 Part 5-54 |
| 10.6 | Lighting layout with circuit assignments | Part L 2021 |
| 10.7 | Specification (NBS or similar) | Tender documentation |
| 10.8 | Construction (Design and Management) Regulations 2015 — designer's risk assessment | CDM 2015 Reg 9 |
| 10.9 | O&M manual structure defined | BSRIA BG 29 |
| 10.10 | EICR after commissioning | BS 7671 Part 6 |

---

## Sign-off

Before issuing for construction, the responsible designer must confirm:

- [ ] All checklist items above completed and evidenced
- [ ] All assumptions documented (DNO data, diversity factors, future load growth)
- [ ] All deviations from BS 7671 documented with departures declared on the EIC
- [ ] All AMD 2 (2022) requirements applied
- [ ] CDM 2015 designer's risk assessment included
- [ ] Coordination with other disciplines (HVAC, plumbing, fire) verified

---

## Common reasons designs fail compliance review

1. Voltage drop calculation done circuit-by-circuit but never aggregated — total from origin exceeds 6%
2. PME bonding not extended to all incoming services
3. EV charging without open-PEN detection on a PME supply
4. Fire-rated cable spec'd but supports/clips are plastic (Reg 521.10.202 fail)
5. SPD specified but connecting lead length not detailed (no chance of installer getting 0.5m)
6. Type AC RCD where electronic loads present
7. Domestic lighting without RCD post-AMD 2
8. Adiabatic check skipped for circuits near a transformer (high PSCC)
9. Switchgear Icu below site PSCC
10. Operating theatres without medical IT system per Reg 710
