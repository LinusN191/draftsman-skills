# IEC 61439 — Designer's Compliance Checklist

This checklist enumerates every characteristic an MEP designer must specify on the assembly schedule for an IEC 61439 assembly. A skill that generates a schedule must populate every applicable item before issuing for tender.

---

## Universal items (every assembly, every part)

- [ ] **Assembly designation** — include the IEC 61439 part number and edition year (e.g. "MSB-01 per IEC 61439-2:2020")
- [ ] **Rated operational voltage Ue** — V a.c. or V d.c. with phases
- [ ] **Rated insulation voltage Ui** — V rms, ≥ Ue
- [ ] **Rated impulse withstand voltage Uimp** — kV per overvoltage category
- [ ] **Rated current In** — A
- [ ] **Rated short-time withstand current Icw** — kA rms with associated time (typical 1 s)
- [ ] **Rated peak withstand current Ipk** — kA peak; ratio Ipk/Icw via n-factor
- [ ] **Rated frequency fn** — Hz (50 or 60)
- [ ] **IP code** — first and second digit per IEC 60529; include supplementary letter if finger-safe required
- [ ] **IK code** — IK00–IK10 per IEC 62262
- [ ] **Pollution degree** — 1–4
- [ ] **Overvoltage category** — I–IV
- [ ] **Service condition** — indoor/outdoor, normal/special
- [ ] **Ambient temperature** — state explicitly if 24-h average exceeds 35 °C or peak exceeds 40 °C
- [ ] **Altitude** — if above 2000 m

---

## Part 2 PSC-Assemblies (main switchboards, MCCs) — additional items

- [ ] **Form separation** — 1, 2a, 2b, 3a, 3b, 4a, 4b
- [ ] **Internal arc classification (IAC)** — class + accessibility + Icw test current + time (e.g. "IAC AB FL 50 kA / 0.5 s") — if specified
- [ ] **Rated diversity factor (RDF)** — state explicitly if not the standard default; common values 0.6–1.0
- [ ] **Busbar material** — copper or aluminium; copper preferred where space-constrained
- [ ] **Incomer arrangement** — single/dual/N+1, with bus-section switch if applicable
- [ ] **Source-changeover scheme** — manual / automatic; class of changeover time (0 / 0.15 / 0.5 / 15 / > 15 s)
- [ ] **Maintenance access requirement** — confirm which functional units can be worked on with rest live (drives form selection)

---

## Part 3 DBO (consumer units, sub-DBs operable by laypersons) — additional items

- [ ] **Way count** — number of outgoing single-pole equivalents
- [ ] **Incoming protection** — main switch rating or main RCD type
- [ ] **Per-circuit protection device** — MCB, RCBO, etc., per circuit
- [ ] **Enclosure material** — for UK domestic per BS 7671 Reg 421.1.201, non-combustible / metal
- [ ] **Child-resistance class** — if installed in family environment
- [ ] **Rated conditional short-circuit Icc** — with stated upstream device (typically BS88 cut-out)

---

## Part 4 ACS (construction sites) — additional items

- [ ] **IP44 minimum confirmed** — mandatory under Part 4 Clause 8
- [ ] **IK08 minimum confirmed** — mandatory under Part 4 Clause 8
- [ ] **30 mA RCD on socket outlets ≤ 32 A** — confirmed per IEC 60364-7-704 / BS 7671 Section 704
- [ ] **RCD type** — Type A minimum; Type B where DC leakage possible (variable-speed drives, EV chargers on site)
- [ ] **Transportability class** — fixed or transportable; drop-test required for transportable
- [ ] **Periodic inspection interval** — every 3 months for construction sites

---

## Part 5 PENDA (DNO kiosks) — additional items (mostly DNO-side)

- [ ] **IK10 confirmed** — vandal-resistance
- [ ] **Solar radiation protection class** — light grey / white reduces internal temperature rise
- [ ] **Lightning impulse withstand** — confirmed for the supply network's overvoltage class

---

## Part 6 BTS (busbar trunking) — additional items

- [ ] **Fire compartmentation at floor crossings** — fire-stop kit per OEM verification (typically 2 h)
- [ ] **Expansion joints** — at building expansion joints and at 30 m intervals on long horizontal runs
- [ ] **Support spacing** — max 1.5 m for straight runs; less at joints
- [ ] **PE path through enclosure** — verify Icw across enclosure if used as PE
- [ ] **Tap-off compatibility** — confirmed compatible with planned distribution boxes

---

## Part 7-1 (camping / marinas) — additional items

- [ ] **30 mA RCD per outlet** — confirmed
- [ ] **IK10 vandal resistance** — confirmed
- [ ] **Tamper-resistant socket layout** — child-safe / non-aligned-prong design

---

## Part 7-2 (EV charging) — additional items

- [ ] **RCD type B** — confirmed where DC leakage > 6 mA possible (all Mode 4; unmanaged Mode 3)
- [ ] **Cable to EVSE rated 100% of EVSE In** — no diversity at cable level
- [ ] **Load management** — documented if multiple chargers share a feeder
- [ ] **SPD at AC input** — Type 2 minimum
- [ ] **PEN broken-conductor protection** — for PME/TN-C-S installations (BS 7671 Reg 722.411.4.1)

---

## Part 7-3 (safety services) — additional items

- [ ] **Source-changeover class** — Class 0 / 0.15 / 0.5 / 15 / > 15 s matched to load tolerance
- [ ] **Fire-integrity class** — E30 / E60 / E90 / E120 of supply cabling
- [ ] **Supply monitoring** — annunciation of supply loss to BMS / front face
- [ ] **Battery / generator backup test schedule** — documented in O&M

---

## Part 7-4 (PV) — additional items

- [ ] **DC-rated isolators specified** — NOT repurposed AC isolators
- [ ] **DC SPD specified** — Type 2 minimum at inverter DC input per IEC 60364-4-44 AMD2
- [ ] **AFCI** — confirmed if mandated by jurisdiction (e.g. US NEC 690.11)
- [ ] **String overcurrent protection** — if string count requires it (typically ≥ 3 strings per inverter MPPT)

---

## Part 7-5 (transformer-incorporated) — additional items

- [ ] **Transformer kVA / primary V / secondary V** — specified
- [ ] **Insulation monitoring device** — confirmed for medical IT (Group 2 locations)
- [ ] **Combined temperature rise verification** — transformer + switchgear losses

---

## Cross-reference items

- [ ] **IEC 60364 installation requirements** — cited on schedule (e.g. IEC 60364-4-43 overcurrent, IEC 60364-7-704 construction sites)
- [ ] **BS 7671 (UK projects)** — relevant regulation references cited
- [ ] **National adoption code** — BS EN 61439, DIN EN 61439, etc. — cited alongside the IEC reference

---

## Documentation handover

- [ ] **OEM type-test / calculation / reference-design certificate** — received and filed
- [ ] **As-built drawings** — received (single-line, general arrangement, terminal schedule)
- [ ] **Verification declaration** — signed by OEM
- [ ] **Functional test records** — insulation, polarity, RCD, switching
- [ ] **O&M manual** — BSRIA BG 29 format or equivalent
- [ ] **Spares list** — received
