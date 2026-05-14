# IEC 60364 — Relationship to National Codes

IEC 60364 is the international parent standard. Countries adopt it via one of three routes:
1. **Direct adoption** — the national standard IS the IEC standard with no changes
2. **Harmonised adoption** — the national standard is based on IEC with documented national deviations
3. **Referenced adoption** — national law or regulation references IEC 60364 as the baseline

---

## United Kingdom — BS 7671 (IET Wiring Regulations)

| Aspect | IEC 60364 | BS 7671 |
|--------|-----------|---------|
| Title | Low-Voltage Electrical Installations | Requirements for Electrical Installations (18th Edition) |
| Publisher | IEC | IET / BSI |
| Numbering | Clause numbers (e.g. 411.3.3) | Regulation numbers (e.g. Reg 411.3.3) — mostly identical |
| Cable ratings | Annex B — IEC tables | Appendix 4 — derived from IEC but some values differ |
| Voltage drop | Annex G (informative) | Appendix 12 (mandatory in practice) |
| Disconnection times | Table 41.1 | Tables 41.2 and 41.3 |
| UK-specific additions | None | Part L cross-reference, AFDD provisions, BS 88 fuse data, ring final circuits, Part 1 Article 2 (UK health and safety) |
| Earthing dominant | All types | TN-C-S (PME) dominant for domestic, TN-S for larger commercial |
| Current edition | Various parts, latest AMD 2023 | BS 7671:2018+A2:2022 |

**Summary:** BS 7671 is the UK adoption of IEC 60364 with UK-specific additions. Clause numbering is largely identical. Cable rating tables differ slightly — use BS 7671 Appendix 4 for UK projects, IEC 60364-5-52 Annex B for all other IEC jurisdictions.

---

## Europe — CENELEC HD 60364 Series

CENELEC publishes HD 60364 (Harmonisation Documents) — these are the European adoptions of IEC 60364. EU member states are obliged to adopt these as their national standards.

| CENELEC HD | IEC 60364 equivalent |
|------------|----------------------|
| HD 60364-1 | IEC 60364-1 |
| HD 60364-4-41 | IEC 60364-4-41 |
| HD 60364-5-52 | IEC 60364-5-52 |
| etc. | etc. |

National deviations (A-deviations or Special National Conditions) are permitted and documented within each HD. Example French deviation: NF C 15-100 requires 30mA RCDs on ALL circuits, not just socket outlets.

---

## France — NF C 15-100

| Aspect | IEC 60364 | NF C 15-100 |
|--------|-----------|-------------|
| Publisher | IEC | UTE (Union Technique de l'Electricité) |
| Earthing dominant | All types | **TT — all residential installations in France use TT** |
| RCD requirements | 30mA for socket outlets | **30mA RCDs on every circuit including lighting — more restrictive** |
| Socket outlet types | Not specified | Specific French socket types (type E) with earth pin |
| Cable colour coding | Brown/Black/Grey, Blue, Green-Yellow | Same (post-2004 harmonised) |
| Key difference | — | France mandates TT earthing for all domestic, requiring RCDs on all circuits |

---

## Germany — DIN VDE 0100

| Aspect | IEC 60364 | DIN VDE 0100 |
|--------|-----------|--------------|
| Publisher | IEC | VDE (Verband der Elektrotechnik) |
| Based on | — | IEC 60364 + CENELEC HD 60364 |
| Earthing dominant | All types | TN-C-S dominant for residential supply; TN-S preferred within buildings |
| Protective devices | MCBs per IEC 60898 | Same + specific requirements for VDE-certified products |
| Key areas of added detail | — | More prescriptive installation practices, VDE product certification requirements |

---

## Australia/New Zealand — AS/NZS 3000 (Wiring Rules)

| Aspect | IEC 60364 | AS/NZS 3000 |
|--------|-----------|-------------|
| Publisher | IEC | Standards Australia / Standards New Zealand |
| Nominal voltage | 230V AC | **230V AC (240V in some areas by tolerance)** |
| Earthing dominant | All types | **MEN (Multiple Earthed Neutral)** — effectively TN-C-S |
| Socket outlets | Not specified | Australian flat-pin socket (AS 3112) |
| RCDs | 30mA for sockets | **30mA mandatory for most circuits** (more aggressive than IEC) |
| Cable ratings | IEC Annex B | Own tables — based on IEC but with Australian ambient adjustments |
| Key difference | — | MEN requires neutral earthed at every switchboard — all metalwork connected to neutral/earth. No floating neutral permitted. |

---

## South Africa — SANS 10142-1

| Aspect | IEC 60364 | SANS 10142-1 |
|--------|-----------|--------------|
| Publisher | IEC | SABS (South African Bureau of Standards) |
| Nominal voltage | 230V AC | 230V AC (previously 220V, harmonised ~2007) |
| Earthing | All types | TN-C-S (MEN) dominant in urban areas; TT in rural areas |
| Earthing note | — | "Combined earth neutral" (CEN) = TN-C-S |
| Consumer protection | — | CoC (Certificate of Compliance) required — registered electrician only |
| Socket outlets | — | SABS 164-2 (round pin, 16A) — unique South African type |
| Key reference | — | SANS 10142-1:2020 — closely aligned with IEC 60364 but with South African-specific content |

---

## Nigeria — NIS 197 / NESIS

| Aspect | IEC 60364 | Nigeria |
|--------|-----------|---------|
| Primary standard | IEC 60364 | **IEC 60364** adopted by SON (Standards Organisation of Nigeria) as **NIS 197** |
| Regulatory framework | — | NESIS (Nigerian Electricity Supply and Installation Standards Regulations) under EPSRA 2005 |
| Regulator | — | NERC (Nigerian Electricity Regulatory Commission) |
| Nominal voltage | 230V AC | 230V AC / 415V 3-phase, 50Hz |
| Earthing | All types | TN-C-S urban (via DISCO supply); TT rural |
| Ambient temperature | 30°C reference | **35–40°C design ambient** — apply Ca correction always |
| Socket outlets | — | BS 1363 (UK-style 13A flat pin) dominant in existing stock, transitioning to IEC standard |
| Key local codes | — | See `local-codes/Nigeria/README.md` for full local deviation detail |
| Certification | — | Licensed electrical contractors required; installation certificates mandatory |

---

## Kenya — KEBS EAS 61 / KS IEC Standards

| Aspect | IEC 60364 | Kenya |
|--------|-----------|-------|
| Primary standard | IEC 60364 | KEBS (Kenya Bureau of Standards) adopts IEC 60364 series as KS IEC standards |
| Regulator | — | ERC (Energy and Petroleum Regulatory Authority) |
| Nominal voltage | 230V AC | 240V AC (single phase), 415V 3-phase — note Kenya uses 240V nominal |
| Earthing | All types | TN-C-S urban (KPLC supply); TT rural |
| Ambient temperature | 30°C reference | 30–35°C typical (varies by altitude — Nairobi at 1800m is cooler) |
| Key consideration | — | High lightning activity — SPDs mandatory in practice. Altitude corrections may be needed above 2000m (lower air density affects some equipment ratings) |

---

## IEC 60364 vs. NFPA 70 (National Electrical Code, USA)

The USA uses NFPA 70 (NEC), not IEC 60364. They are fundamentally different standards.

| Aspect | IEC 60364 | NFPA 70 NEC |
|--------|-----------|-------------|
| Voltage | 230V/400V, 50Hz | 120/240V single-phase or 120/208V 3-phase, 60Hz |
| Earthing | TN-S/TN-C-S/TT/IT | Grounded neutral (TN-C-S equivalent), called "grounding" |
| Cable sizing | mm² cross-sections, Annex B tables | AWG / kcmil wire gauge, NEC Table 310 |
| Conduit sizing | mm metric | Imperial (EMT, IMC, rigid conduit — inches) |
| Device standards | IEC 60898 MCBs | UL 489 circuit breakers — different trip characteristics |
| Wire colours | Brown/Black/Grey, Blue, Green-Yellow | Black/Red (phase), White (neutral), Green/Bare (ground) |
| **Not interchangeable** | Do NOT mix IEC 60364 design practices with NEC installations | |

---

## How to use this information

**For a project in a specific country:**
1. Identify the primary applicable national standard from the table above
2. Use IEC 60364 data files as the base calculation data
3. Apply any national deviations noted (e.g. Nigeria ambient temperature, France TT earthing)
4. Cross-reference the `local-codes/[Country]/README.md` for project-specific guidance
5. Verify any critical values against the current purchased copy of the national standard

**Data file equivalence:**
- `part5-52-cable-ratings-copper.json` (IEC) ≈ `BS7671/appendix4-cable-ratings.json` (UK) with some numerical differences
- `part4-41-electric-shock.json` (IEC) ≈ `BS7671/reg411-disconnection-times.json` (UK) — mostly identical
- Voltage drop limits (IEC Annex G) = same as BS 7671 Appendix 12 in practice
