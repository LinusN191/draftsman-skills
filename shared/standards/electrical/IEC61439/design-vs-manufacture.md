# IEC 61439 — Design vs Manufacture Responsibility Split

This is the single most-confused topic for designers using IEC 61439. The 2nd edition (2009 onward) made explicit a three-way responsibility split that pre-2014 IEC 60439 left implicit. Understanding who does what is essential for writing a coherent assembly schedule and reading the resulting documentation handover.

---

## The three roles

### Original Manufacturer (OM)

**What they do:** Design and verify the assembly to IEC 61439. Hold the verification chain — type-test certificates from accredited laboratories, calculation reports per Annex E/P, reference design certificates, and the bounding rules that govern variants.

**Examples:** ABB SMissline, Schneider Prisma iPM, Siemens Sivacon S8, Eaton xEnergy. The "OEM" is typically a major switchgear maker who owns the verified design and the right to license it to assembly manufacturers.

**Key deliverables to the designer/AM:**
- Type-test certificates (for the tested arrangement)
- Calculation reports (where Annex E or Annex P is invoked)
- Reference design verification + Annex D bounding rules (for variants within the verified envelope)
- Construction drawings / arrangement drawings
- Verification declaration

### Assembly Manufacturer (AM)

**What they do:** Build individual assemblies under the OM's verified design. May be the same legal entity as the OM (large OEMs run their own panel-build factories) or a licensed third-party panel-builder ("panel-shop").

**Examples:** A UK panel-building company licensed by Schneider to assemble Prisma iPM boards. The AM cuts metal, lays out functional units, fits devices, wires, terminates, and ships — but does NOT redesign or re-verify.

**Key responsibilities:**
- Build strictly within the OM's verified envelope (no substitutions of un-verified devices, no enlargements beyond bounding rules)
- Maintain build records traceable to the OM's verified design
- Provide as-built drawings, test records (insulation, polarity, functional), and the verification declaration linked to the OM's certificate
- Hand over the O&M pack (BSRIA BG 29 or equivalent) at commissioning

### MEP Designer (you / the skill)

**What they do:** Specify the assembly on schedules, drawings, BOQ. Do NOT design or build — that's the OM/AM's job.

**Key responsibilities:**
- Pick the right assembly type (Part 2 PSC, Part 3 DBO, Part 4 ACS, Part 7-x application)
- Pick the right Form separation (1, 2a, 2b, 3a, 3b, 4a, 4b)
- Specify rated quantities (Ue, Ui, Uimp, In, Icw, Ipk, fn)
- Specify environmental class (IP, IK, ambient, pollution degree, overvoltage category)
- Specify special features (IAC class + accessibility, RDF, source-changeover class for Part 7-3, RCD type for Part 7-2)
- Specify cross-references (IEC 60364 installation rules, BS 7671 UK practice if applicable)
- Cite the IEC 61439 part number and Form on the schedule

**Common mistake:** the designer specifying which OEM to use is acceptable on a tender. The designer specifying construction details (sheet thickness, paint type, busbar geometry) is NOT — that's the OM's verified design.

---

## What goes on the assembly schedule

Per IEC 61439-1 Clause 6, the designer's schedule must include:

| Field | Mandatory? | Example |
|---|---|---|
| Assembly designation | Yes | "MSB-01: Main LV switchboard, Form 3b PSC per IEC 61439-2:2020" |
| Rated voltage Ue | Yes | "400 V (3-phase) + N + PE" |
| Rated insulation voltage Ui | Yes | "1000 V" |
| Rated impulse withstand Uimp | Yes | "6 kV (overvoltage category IV)" |
| Rated current In | Yes | "2500 A" |
| Rated short-time withstand Icw / time | Yes | "50 kA / 1 s" |
| Rated peak withstand Ipk | Yes | "105 kA peak" |
| Rated frequency fn | Yes | "50 Hz" |
| IP code | Yes | "IP2X (front) / IP30 (enclosure)" |
| IK code | Yes | "IK08" |
| Form separation | Yes | "Form 3b" |
| Internal arc classification | If applicable | "IAC AB FL 50 kA / 0.5 s" |
| Ambient temperature | If outside 35 °C 24-h | "45 °C 24-h average" |
| Altitude | If above 2000 m | "n/a" |
| Pollution degree | Yes | "2 (indoor)" |
| Service condition | Yes if special | "Indoor, normal service" |
| Rated Diversity Factor | Yes if non-default | "RDF = 0.7" |

---

## What comes back from the OEM at handover

| Document | Provided by | Purpose |
|---|---|---|
| Type-test certificate (or summary) | OM | Demonstrates compliance with IEC 61439-x |
| Calculation report (Annex E / P) | OM | Where calculation verification used |
| Reference design certificate | OM | Where reference comparison used |
| Annex D bounding comparison | OM/AM | Documents that this build falls within the verified envelope |
| As-built drawings | AM | Single-line, general arrangement, terminal schedule |
| Verification declaration | OM/AM | The OEM's formal "this assembly complies with IEC 61439-x" |
| Functional test records | AM | Polarity, insulation, RCD trip, switching operation |
| O&M manual (BSRIA BG 29) | AM | Installation, operation, maintenance |
| Spares list | AM | Recommended hold quantities |

---

## Documentation flow on a project

```
Designer's spec  →  OEM (OM) verified design  →  AM build  →  As-built drawings + verification reports  →  Handover pack  →  BSRIA BG 29 O&M
       ↑                                                            ↓
       └──── Cross-references: IEC 60364 (installation), BS 7671 (UK practice) ────┘
```

The flow is linear in principle. In practice the designer iterates with the OM during tender (confirming RDF, IAC, Form fitness) before issuing the final spec to the AM.
