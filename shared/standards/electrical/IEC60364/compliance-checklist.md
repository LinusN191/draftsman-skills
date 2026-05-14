# IEC 60364 — Design Compliance Checklist

End-of-design verification checklist. Every item must be either confirmed (✓) or
documented with a reasoned justification for deviation. This checklist does not
replace engineering judgement — it ensures no category is overlooked.

---

## Section 1 — Supply and system characterisation

| # | Check | Evidence required |
|---|-------|------------------|
| 1.1 | Supply voltage, frequency, and earthing system (TN-S/TN-C-S/TT/IT) confirmed | Supply authority letter, or on-site measurement |
| 1.2 | External earth fault loop impedance Ze confirmed or conservatively assumed | DNO data sheet, or assumption with justification |
| 1.3 | Prospective short-circuit current (PSCC) at service entrance confirmed | DNO data, or calculated from Ze |
| 1.4 | Maximum demand (MD) calculated using appropriate diversity | Load schedule with diversity calculation |
| 1.5 | Supply cable and metering arrangement confirmed with DNO | Pre-application agreement or DNO design guide |

---

## Section 2 — Protection against electric shock (IEC 60364-4-41)

| # | Check | Evidence required |
|---|-------|------------------|
| 2.1 | Automatic disconnection of supply (ADS) as primary protective measure | Design basis statement |
| 2.2 | All TN system circuits satisfy Zs × Ia ≤ U0 | Circuit-by-circuit Zs calculation table |
| 2.3 | All TT system circuits satisfy Ra × IΔn ≤ 50V | Earth electrode design and RCD schedule |
| 2.4 | Earth fault loop impedance Zs calculated for every circuit (not just representative samples) | Cable sizing schedule with Zs column |
| 2.5 | Disconnection times from Table 41.1 met by all protective devices | Zs_max comparison for each device |
| 2.6 | 30mA RCDs specified for all socket outlet circuits ≤ 20A | Distribution board schedule |
| 2.7 | 30mA RCDs specified for all cables in walls at depth < 50mm | Cable route and RCD schedule |
| 2.8 | SELV/PELV voltage limits (50V AC, 120V DC) respected where ELV is used | Circuit documentation for ELV systems |
| 2.9 | Main equipotential bonding specified for all metallic services entering building | Bonding schedule (water, gas, structural steel) |
| 2.10 | Supplementary bonding specified in bathrooms and other Part 7 locations | Bonding drawing or notation on layouts |

---

## Section 3 — Overcurrent protection (IEC 60364-4-43)

| # | Check | Evidence required |
|---|-------|------------------|
| 3.1 | Fundamental Rule Ib ≤ In ≤ Iz satisfied for every circuit | Cable sizing schedule |
| 3.2 | Correction factors Ca, Cg, Ci (and Cs, Cd for buried) applied to all cable ratings | Schedule with factors applied |
| 3.3 | Cable cross-sections rounded up to next standard size after correction | Schedule with tabulated and corrected ratings |
| 3.4 | I2 ≤ 1.45 × Iz confirmed (especially for fuse-protected circuits) | Schedule annotation |
| 3.5 | All protective devices have breaking capacity ≥ PSCC at point of installation | DB schedule with device Isc and PSCC per position |
| 3.6 | Back-up protection coordination documented where devices do not individually meet PSCC | Manufacturer coordination data attached |
| 3.7 | Motor circuits have both overload and short-circuit protection specified | Motor circuit schedule |

---

## Section 4 — Cable sizing (IEC 60364-5-52)

| # | Check | Evidence required |
|---|-------|------------------|
| 4.1 | Installation method (A1–G) correctly identified for each cable route | Route description in cable schedule |
| 4.2 | Ambient temperature correction factor Ca applied (especially for tropical climates) | Ca values in schedule |
| 4.3 | Grouping factor Cg applied where cables share containment | Grouping schedule or notation |
| 4.4 | Thermal insulation factor Ci applied where cables are in or close to building insulation | Notation on cable schedule |
| 4.5 | Soil thermal resistivity and depth corrections (Cs, Cd) applied to buried cables | Soil data and buried cable schedule |
| 4.6 | Harmonic correction factor Cf applied for circuits with significant non-linear loads | Harmonic content noted for VFD/SMPS-heavy circuits |
| 4.7 | Voltage drop complies with limits (3% lighting, 5% other per Annex G) for every circuit | VD calculation for each circuit in schedule |
| 4.8 | Adiabatic check (I²t ≤ k²S²) completed for circuits where fault current is high | Fault current calculation table |
| 4.9 | CPC cross-sections comply with Table 54.3 minimum (or adiabatic calculation) | CPC sizing in cable schedule |

---

## Section 5 — Overvoltage protection (IEC 60364-4-44)

| # | Check | Evidence required |
|---|-------|------------------|
| 5.1 | Risk assessment or default assumption for SPD requirement completed | Risk assessment note or reference to AMD2:2018 default |
| 5.2 | SPD type, IΔn, Uc, Up specified at main distribution board | DB schedule / spec |
| 5.3 | SPD type, rating specified at every sub-distribution board | SDB schedules |
| 5.4 | SPD connection lead length minimised (≤ 0.5m total live+earth) | Installation detail drawing |
| 5.5 | SPD coordination between Type 1 and Type 2 confirmed (10m cable or decoupling inductor) | SDB single line diagram |
| 5.6 | Point-of-use (Type 3) SPDs specified for Category I equipment locations | Equipment schedule |
| 5.7 | EV charging circuits include appropriate SPDs | EV circuit design |
| 5.8 | PV systems include SPDs on both DC and AC sides | PV system design documentation |

---

## Section 6 — RCD schedule

| # | Check | Evidence required |
|---|-------|------------------|
| 6.1 | RCD type (AC/A/F/B) correct for load type | DB schedule with type notation |
| 6.2 | Type S (time-delayed) RCDs specified upstream of instantaneous 30mA RCDs | DB single line diagram showing selectivity |
| 6.3 | All TT system circuits have RCD protection | DB schedule |
| 6.4 | EV charging circuits have Type A (minimum) or Type B RCDs | EV circuit specification |
| 6.5 | Bathroom circuits have 30mA RCD protection | DB schedule |
| 6.6 | Construction site circuits have 30mA RCDs on all outlets ≤ 32A | Temporary supply design |
| 6.7 | Total leakage current per RCD circuit estimated (< IΔn/3) | Load schedule annotation |

---

## Section 7 — Distribution boards and switchgear

| # | Check | Evidence required |
|---|-------|------------------|
| 7.1 | Distribution boards comply with IEC 61439 | Specification clause |
| 7.2 | Busbar rated for maximum demand current | DB design sheet |
| 7.3 | Outgoing ways rated for each circuit | DB schedule |
| 7.4 | Spare ways provided (minimum 25%) | DB schedule |
| 7.5 | IP rating appropriate for location | DB specification |
| 7.6 | Incoming isolator or MCCB correctly rated | DB schedule |
| 7.7 | Main incomer protected against fault current at installation point | Fault level check |
| 7.8 | Circuit labelling specified | Specification or drawing note |

---

## Section 8 — Special locations (Part 7)

| # | Check | Evidence |
|---|-------|---------|
| 8.1 | Bathrooms — zones defined, IP ratings confirmed, bonding specified | Drawing annotation + spec |
| 8.2 | Kitchens — zones noted, minimum IP above/below worktop applied | Drawing annotation |
| 8.3 | Any swimming pool — Section 702 zones applied | Pool drawing |
| 8.4 | EV charging — Section 722 requirements (RCD type, socket type, load management) | EV spec |
| 8.5 | External lighting — Section 714 (RCD, IP65 minimum, isolation) | External lighting spec |
| 8.6 | Any medical location — Section 710 group classification documented | Medical brief confirmation |
| 8.7 | Any construction site supply — Section 704 applied | Temp supply design |

---

## Section 9 — Documentation and verification

| # | Check | Evidence |
|---|-------|---------|
| 9.1 | Cable schedule complete and traceable to circuit diagrams | Cable schedule document |
| 9.2 | Distribution board schedules complete for all boards | DB schedule documents |
| 9.3 | Single line diagram complete from service entrance to all final circuits | SLD drawing |
| 9.4 | Earthing and bonding drawing produced | E&B drawing |
| 9.5 | Cable routing drawings or schedules produced | Cable route drawings |
| 9.6 | Specification written referencing applicable IEC standards | Specification document |
| 9.7 | Verification (test) requirements specified for contractor | Spec clause or commissioning brief |
| 9.8 | Electrical Installation Certificate template provided or referenced | Spec clause |

---

## Sign-off declaration

> I confirm that I have reviewed the design against this checklist. All items are either:
> (a) confirmed compliant with IEC 60364 and the applicable national code, or
> (b) documented with a justified deviation where departure from the standard is taken.
>
> This checklist does not replace the full engineering calculations, drawings, and
> specifications that constitute the complete design. Refer to those documents for evidence.

**Designer:** _____________________________
**Date:** _________________________________
**Project:** _______________________________
