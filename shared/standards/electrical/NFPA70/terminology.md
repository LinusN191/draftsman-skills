# NFPA 70 (NEC) — Terminology Glossary

NEC-vs-IEC critical-distinction glossary. Every term that has been a source of
confusion in cross-jurisdiction projects is captured here.

---

## Grounding vs Earthing

| NEC term | IEC term | Notes |
|---|---|---|
| Grounding | Earthing | Same concept. Use only one term in any single document. |
| Ground | Earth | Same |
| Grounding electrode | Earth electrode | Same |
| Grounding electrode system (GES) | Earth electrode system | Same |
| Grounding electrode conductor (GEC) | Main earthing conductor (closest analogue) | NEC sizes from largest ungrounded service conductor; IEC sizes adiabatically |
| Equipment grounding conductor (EGC) | Circuit protective conductor (CPC) | NEC sizes by OCPD rating (250.122); IEC sizes by line CSA (Table 54.1) |
| Bonding | Bonding | Same |
| Main bonding jumper (MBJ) | (no exact equivalent) | NEC has this as explicit hardware concept at service |
| System bonding jumper | Bonding jumper at SDS / first separately-derived disconnect | NEC vs IEC have similar concept different names |

## Neutral

| NEC term | IEC term | Notes |
|---|---|---|
| Grounded conductor | Neutral (N) in TN systems | NEC uses "grounded" because in TN-C-S the neutral IS grounded at the service |
| Neutral conductor | Neutral | Same — NEC distinguishes "grounded" (the bonded one) from "neutral" (carries current); sometimes the same, sometimes not |
| Multiwire branch circuit | (no exact equivalent) | NEC concept of shared neutral on multi-phase circuits — not common in IEC; IEC 60364 generally requires separate neutrals |

## Circuit roles

| NEC term | IEC term | Notes |
|---|---|---|
| Service | Origin of installation / supply intake | NEC distinguishes "service" as a legal entity (the utility connection point) |
| Feeder | Sub-main / distribution circuit | Same concept |
| Branch circuit | Final circuit | Same |
| Tap | Tap (similar) | NEC has tap rules (240.21) with explicit length limits; IEC less prescriptive |

## Conductor identification

| NEC term | IEC term | Notes |
|---|---|---|
| AWG (American Wire Gauge) | mm² | Inverse relationship: smaller AWG number = larger conductor; mm² is direct |
| kcmil (thousand circular mils) | mm² | Used for AWG-equivalents larger than 4/0 — e.g. 250 kcmil ≈ 127 mm² |
| Solid / stranded | Same | Same |
| Cu / Al | Cu / Al | Same |

## Protective devices

| NEC term | IEC term | Notes |
|---|---|---|
| OCPD (overcurrent protective device) | Overcurrent protective device | Same generic term |
| Fuse | Fuse | Same |
| Circuit breaker | Circuit breaker / MCB / MCCB | NEC doesn't distinguish MCB/MCCB by acronym — both are "circuit breaker" |
| Interrupting rating | Icu (ultimate) and Ics (service) | NEC has one rating; IEC two values per device |
| AIC | Icu (ultimate equivalent) | "Amps Interrupting Capacity" — NEC name for AIC equates to IEC's Icu |
| Frame rating | Frame size | Same |
| GFCI | RCD (functional equivalent, different trip level) | GFCI Class A = 4-6 mA; IEC general-use RCD = 30 mA |
| AFCI | (no exact equivalent in IEC 60364 base) | NEC mandates; IEC 62606 AFDD is optional |

## Receptacles / outlets

| NEC term | IEC term | Notes |
|---|---|---|
| Receptacle | Socket outlet | Same |
| Outlet | Outlet | NEC distinguishes "outlet" (a point on the wiring system) from "receptacle" (the actual device) |
| Hospital grade | (no exact term) | NEC-specific UL 498 hospital-grade receptacle |
| Tamper-resistant (TR) | (no equivalent term) | NEC mandates in dwellings; IEC sockets have inherent safety via BS 1363 shutters etc. |
| Weather-resistant (WR) | (similar via IP rating) | NEC term; IEC handles via IP per IEC 60529 |
| Listed | (Certification mark — UL/CSA/ETL) | NEC-specific "listed by NRTL" |

## Voltage / current / power

| NEC term | IEC term | Notes |
|---|---|---|
| Volts (V) | Volts (V) | Same — values differ between NEC 60 Hz US and IEC 50 Hz international |
| Amperes (A) | Amperes (A) | Same |
| VA (volt-amperes) | VA | NEC uses VA frequently in load calc; IEC uses kVA more often |
| Horsepower (hp) | kW | NEC uses hp for motors (especially with Table 430.250 FLA); IEC uses kW |
| RLA (rated-load current) for AC compressors | Rated current | NEC-specific construct for Art 440 (hermetic compressors) |
| Power factor (PF) | Power factor / cos φ | Same |

## Wiring methods

| NEC term | IEC term | Notes |
|---|---|---|
| Raceway | Conduit / cable trunking / tray system | NEC umbrella term covers conduit/trunking/cable tray etc. |
| Conduit | Conduit | Same |
| Cable tray | Cable tray | Same |
| Wireway | Cable trunking with internal access | NEC-specific (NEC Art 376/378) |
| NM (Nonmetallic-Sheathed Cable, Romex) | (no exact equivalent in common use) | NEC dwelling cable; IEC typically uses singles in conduit/trunking |
| AC (Armored Cable) | (similar to armoured cable) | NEC AC has internal bonding strip; IEC armoured cable uses SWA |
| MC (Metal-Clad Cable) | (closest: SWA + LSZH cable) | NEC MC has separate EGC inside |
| MI (Mineral-Insulated) | MICC (Mineral Insulated Copper-Clad) | Same |
| EMT (Electrical Metallic Tubing) | (closest: light gauge steel conduit) | NEC-specific |
| RMC (Rigid Metal Conduit) | Heavy gauge steel conduit | Same idea |
| IMC (Intermediate Metal Conduit) | (between EMT and RMC) | NEC-specific intermediate weight |
| PVC | uPVC conduit | Same |
| FMC (Flexible Metal Conduit) | Flexible steel conduit | Same |
| LFMC (Liquidtight Flexible Metal Conduit) | Flexible steel conduit with thermoplastic cover | Same |
| LFNC | Liquidtight flexible nonmetallic conduit | Same |

## Special locations and systems

| NEC term | IEC term | Notes |
|---|---|---|
| Hazardous (Classified) location | Hazardous area | Same concept |
| Class I / II / III | (IEC uses category zones only) | NEC has both Division and Zone systems |
| Division 1 / 2 | Zone 0 / 1 / 2 (gas), Zone 20 / 21 / 22 (dust) | See hazardous-locations-classification.json for conversion |
| Group A/B/C/D (gases) | IIA / IIB / IIC | NEC Groups A and B map to IEC IIC |
| Group E/F/G (dusts) | IIIA / IIIB / IIIC | Approximate equivalence |
| Wet location | Damp/wet location | Same |
| Damp location | Damp location | Same |
| Healthcare patient care space Category 1-4 | Group 0/1/2 medical locations | Different classification details |
| Type 1 / 2 / 3 Essential Electrical System | Essential power supply (similar) | NEC has three-branch Type 1; IEC has equivalent grouped power supplies |

## Project roles

| NEC term | IEC term | Notes |
|---|---|---|
| AHJ (Authority Having Jurisdiction) | Approving authority / building control | NEC's AHJ is the enforcement authority — varies by state/locality |
| Electrical inspector | Inspector | Same |
| Listed (by an NRTL) | Certified (by a national mark — CE, UKCA, etc.) | Different regimes |
| Identified (per its listing) | Suitable for the application | Same concept |

---

## When in doubt

If you must use BOTH NEC and IEC terms in a document:
1. Define each term explicitly at first use
2. Pick one as primary throughout and put the other in parentheses
3. Note in the design narrative which standard is the authoritative reference

The single biggest source of cross-jurisdiction confusion is grounding vs
earthing. Always pick one and stick with it.
