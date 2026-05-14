# BS 7671:2018 Amendment Summary

A summary of changes introduced by AMD 1 (2020) and AMD 2 (2022). Use
this to assess existing installations and to track what's mandatory by
date.

The current published version is **BS 7671:2018+A2:2022**, effective
**28 September 2022**. New installations completed after that date must
comply with AMD 2.

---

## Amendment 1 (2020) — published March 2020, effective March 2020

A relatively small amendment. Most changes were clarifications and
errata corrections rather than new requirements.

### Key changes

| Regulation | Change |
|------------|--------|
| **421.1.7 (NEW)** | Arc Fault Detection Devices (AFDDs) — **recommended** in: sleeping accommodation; locations of risk associated with high fire load; buildings of combustible construction; locations where stored material involves risk of fire; locations with risk of fire from electric arcs. NOTE: AMD 1 made AFDD "recommended"; AMD 2 keeps it "recommended" with the same scope. AFDDs are not yet mandatory in any UK building. |
| **422.3.1** | Clarification on protection against fire — additional emphasis on cable supports not failing prematurely in fire. Foundation for AMD 1's later 521.10.202 update. |
| **521.10.202 (NEW)** | **Cable supports must not fail prematurely in fire** — affects ALL cables on escape routes, not just life safety. Plastic clips alone are non-compliant; metal saddles required. This is a frequently-missed change. |
| **559.5.1, 559.11** | Cosmetic clarifications to luminaire connection methods. |
| **Section 730 (NEW)** | Onshore units of electrical shore connections for inland navigation vessels — new specialist section. |

### Practical impact of AMD 1
- **Cable supports**: existing installations using only plastic clips along escape routes are now non-compliant. Periodic inspection should flag this.
- **AFDD**: not mandatory, but specifying for the listed scenarios is increasingly expected by insurers.

---

## Amendment 2 (2022) — published March 2022, effective September 2022

A substantial amendment. Several new mandatory requirements that the
industry is still working through.

### 1. RCD protection — expanded scope

**Reg 411.3.3 — Sockets**

Already required 30mA RCD on sockets ≤32A. AMD 2 retained this but
clarified that the exception (omitting RCD for specific labelled sockets)
must be documented through a risk assessment.

**Reg 411.3.4 — Domestic lighting (NEW)**

> "For a.c. systems in dwellings, additional protection by an RCD with a
> rated residual operating current not exceeding 30mA shall be provided
> for **a.c. final circuits supplying luminaires**."

**Impact**: All new domestic lighting circuits now require 30mA RCD
protection. Most consumer units sold post-September 2022 have RCBOs
across the board to handle this.

This was controversial during consultation — designers worried about
nuisance trips affecting safety lighting. The final wording was a
compromise.

---

### 2. SPD provision — effectively mandatory for commercial

**Reg 443.4 — substantially rewritten**

Pre-AMD 2: SPD required where "consequence of overvoltage is significant".
The wording was vague and frequently ignored.

AMD 2: SPD shall be provided "where the consequence caused by overvoltage
could result in":
- (a) serious injury or loss of human life
- (b) interruption of public services or damage to cultural heritage
- (c) interruption of commercial or industrial activity
- (d) affects a large number of co-located individuals

**Practical effect**: nearly every commercial and public building meets
at least criterion (c). SPD is now effectively the default.

For domestic, the Calculated Risk Level (CRL) per Reg 443.5 must be
performed; if CRL > 1000, SPD is mandatory.

---

### 3. EV charging — Section 722 rewritten

Major restructure of Section 722 to align with rapidly growing EV market.

**Key changes:**
- Reg 722.411.4.1 — for PME supplies, open-PEN detection device OR TT island OR continuous monitoring required. Address the chassis-energisation risk.
- Reg 722.531.3.101 — RCD requirements clarified: Type A 30mA minimum per charge point; Type B if EVSE does not have built-in 6mA DC detection.
- Reg 722.444 — clarified requirements around earthing in dedicated EV TT installations.
- Smart charging (DSRMS, V2G) addressed in informative annex.

---

### 4. Prosumer's installations — Section 712 / Part 8 introductions

**Reg 712 (Solar PV)** — significantly expanded:
- DC isolation requirements clarified
- Type B RCD required if PV inverter doesn't have integrated DC fault protection
- Maximum DC voltage to mainstream equipment limited

**Part 8 — Functional safety, energy efficiency, prosumer (NEW)** —
introductory clauses for buildings that both consume and generate energy.
Foundation for future technical sections (battery storage, energy
management systems).

---

### 5. Section 730 — Shore connections

Originally introduced in AMD 1 for inland navigation. AMD 2 expanded to
include onshore power supplies more broadly for berthed vessels.

---

### 6. Appendix 16 — Devices for protection against overvoltage

New informative appendix providing guidance on SPD selection, coordination,
and installation. Complements the regulatory text of Reg 443.

---

### 7. Appendix 17 — Energy efficiency

New informative appendix on electrical installation design for energy
efficiency. Voltage drop optimisation, harmonic management, power factor,
load management, metering. Aligns with Part L Building Regulations.

---

## What this means for existing designs

| Installation date | Standard applied | Key checks for compliance now |
|-------------------|-----------------|------------------------------|
| Before July 2008 | BS 7671:2001 (16th) | Periodic inspection often finds significant non-compliance. Major rewiring likely needed for any meaningful refurbishment. |
| 2008 – Jan 2019 | BS 7671:2008 (17th + amendments) | RCD on sockets common but not universal. Cable supports likely plastic clips throughout. |
| Jan 2019 – Mar 2020 | BS 7671:2018 base | RCD on sockets standard. PME bonding generally compliant. SPD not common. |
| Mar 2020 – Sep 2022 | BS 7671:2018 + AMD 1 | Cable supports now must be fire-resistant. AFDD recommended in specific occupancies. |
| Sep 2022 onwards | BS 7671:2018 + AMD 2 | All above PLUS: 30mA RCD on domestic lighting, SPD effectively mandatory for commercial, EV charging revised requirements. |

---

## Future direction (post-AMD 2)

The IET signals these likely areas for AMD 3 (expected 2026 or later):

- **AFDDs** may move from "recommended" to "mandatory" in sleeping accommodation
- **Battery storage** detailed technical requirements (currently scattered)
- **Vehicle-to-Grid (V2G)** technical requirements
- **EV charging** further refinement as DC charging proliferates
- **Cybersecurity** for connected electrical equipment

This is informed speculation, not committed policy.

---

## Practical tracking for designs in progress

For any project where the design started under one edition and completes
under another:

1. **Design phase**: apply the edition current at design start.
2. **Construction phase**: apply the edition current at first inspection.
3. **Certification**: apply the edition current at certificate issue date.

If the standard changes mid-project, any changes to the design or
installation must comply with the new edition. Untouched portions can
remain under the original edition (documented as a "Departure" if needed).

For ongoing periodic inspection (EICR), compliance is assessed against
the edition current at the time of the original installation, with
recommendations for improvements aligned to the current edition.
