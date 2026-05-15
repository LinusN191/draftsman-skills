# IEC 61439 — Terminology Glossary

Critical distinctions used throughout the standard. Get these wrong and the assembly schedule becomes meaningless.

---

## Assembly-level terms

**Assembly** — A combination of one or more low-voltage switching devices together with associated control, measuring, signalling, protective, regulating equipment, with all the internal electrical and mechanical interconnections and structural parts. Per IEC 61439-1 Clause 3.1.1. NOT "switchboard" or "panel" — those are colloquial.

**PSC-Assembly (Power Switchgear and Controlgear Assembly)** — IEC 61439-2 scope. Main switchboards, MCCs. Operated by skilled or instructed persons. Includes Form separations 1–4b.

**DBO (Distribution Board for Ordinary persons)** — IEC 61439-3 scope. Consumer units and sub-DBs operated by laypersons. Stricter accessibility and finger-safety than PSC.

**ACS (Assembly for Construction Sites)** — IEC 61439-4 scope. Mandatory IP44/IK08. Mandatory RCD on socket outlets.

**PENDA (Power Distribution Assembly for Public Electricity Networks)** — IEC 61439-5 scope. DNO-side. Mandatory IK10 typical.

**BTS (Busbar Trunking System)** — IEC 61439-6 scope. Prefabricated busbar including its joints, fire-stops, expansion joints, and tap-off boxes.

---

## Internal-structure terms

**Functional unit** — A part of an assembly comprising all the electrical and mechanical elements that contribute to a defined function (e.g. an outgoing-way comprising MCCB + cable terminations).

**Compartment** — A section of an assembly enclosed except where it joins other compartments. Form codes describe which functional units / busbars / terminals occupy distinct compartments.

**Section** — A vertical or horizontal subdivision of the assembly comprising one or more bays/columns. Multiple sections make up an assembly. Distinct from "compartment".

**Bay** — A vertical column within a section, typically housing one or more functional units arranged vertically.

---

## Role terms

**Original manufacturer (OM)** — The organisation that has carried out the original design and the associated verification of an assembly in accordance with the relevant assembly standard. Owns the verified design. Per IEC 61439-1 Clause 3.10.1.

**Assembly manufacturer (AM)** — The organisation taking responsibility for the completed assembly. May or may not be the OM. Per IEC 61439-1 Clause 3.10.2.

**Designer** — Per IEC 61439, the designer is NOT a defined role inside the OM/AM split. The designer (MEP / consultant) is the user who specifies the assembly. The standard refers to "user requirements" in the Annex C interface characteristics.

---

## Verification terms

**Type-tested / TTA (older)** — Pre-2014 IEC 60439 term. Means "the design has been physically tested". Replaced by "design verification" in IEC 61439.

**Design verification** — The new umbrella term covering test, calculation, and comparison-with-reference-design.

**Routine verification** — Tests carried out on every assembly that leaves the AM. NOT the same as design verification. Includes insulation test, dielectric, functional, and earth continuity per Clause 11.

**Conditions of normal service** — Indoor, -5 to +40 °C ambient (35 °C 24-h average), altitude ≤ 2000 m, humidity ≤ 50% at 40 °C, pollution degree 2.

**Special service conditions** — Outdoor, or any deviation from normal-service. Triggers higher Uimp, larger creepages, IP44+, IK08+, solar-gain correction.

---

## Electrical-rating terms

**Rated current of the assembly (In)** — Total maximum continuous current the assembly handles at its incoming terminals. Verified at Ue, fn, RDF.

**Rated current of a circuit (Inc)** — Maximum continuous current for a single circuit within the assembly.

**Rated Diversity Factor (RDF)** — Multiplier applied to the sum of outgoing-circuit ratings to give the simultaneous load the assembly is verified for. Defaults from 1.0 (continuous) to 0.6 (10+ circuits with no continuous load) per Annex E.5.

**Short-circuit current quantities** — see `short-circuit-withstand.json`.

---

## Protection terms

**IP code** — Two digits + supplementary letter: solid-object protection, water protection, finger-safe code. Per IEC 60529.

**IK code** — IK00–IK10, impact energy in joules. Per IEC 62262 (was BS EN 50102).

**IAC (Internal Arc Classification)** — Per IEC TR 61641. A/B/C/D person/installer/live-work protection class + accessibility F/L/R + Icw test current and time. Format: "IAC AB FL 50 kA / 0.5 s".

**RCD type** — AC (sinusoidal AC residual), A (AC + pulsating DC), F (A + composite multi-frequency), B (A/F + smooth DC > 6 mA). Selection drives compatibility with VFDs, EVSEs, PV inverters.

**SPD type** — Type 1 (Iimp, 10/350 µs lightning impulse), Type 2 (In, 8/20 µs nominal), Type 3 (point-of-use, low let-through Up).

---

## Form-separation terms

**Segregation** — Metallic barrier between two named parts of the assembly. Form codes describe which segregations exist.

**Common compartment** — Compartment containing more than one type of named part (e.g. functional units sharing a single space).

**Cable termination** — The point where an external conductor joins the assembly's internal wiring. Form 2b+ separate these from the busbar; Form 4a+ separate them between functional units; Form 4b separates them between individual terminals.

---

## What's NOT in this glossary

- **Switchboard / panel / DB / consumer unit** — colloquial terms. Use "assembly per IEC 61439-x" in technical documents.
- **TTA / PTTA** — pre-2014 IEC 60439 terms. Do NOT use for new designs. The IEC 61439 equivalent is "design-verified".
- **Manufacturer-specific terms** — refer to OEM documentation.
