# IEC 60364 — Low-Voltage Electrical Installations

Machine-readable extracts and supplementary guidance for IEC 60364, for
use by DraftsMan skills and the engineers reviewing their output.

**Publisher:** IEC (International Electrotechnical Commission).
**Current editions:** Multiple parts — see [meta.json](meta.json) for exact editions and amendment status.
**Reference voltage:** 230V AC (line-to-earth), 400V AC (line-to-line), 50 Hz.

> Always verify values against the current purchased copy of the standard.
> This is a reference layer for AI agents — it is not a substitute for the
> standard itself, and it does not replace engineering judgement.
> National implementations may deviate from IEC 60364. Always check the
> applicable national code for the jurisdiction of the project.

---

## Index

### Edition metadata
| File | Content |
|------|---------|
| [meta.json](meta.json) | All parts, editions, amendment dates, status, national implementations |
| [relationship-to-national-codes.md](relationship-to-national-codes.md) | How IEC 60364 maps to BS 7671 (UK), NF C 15-100 (France), DIN VDE 0100 (Germany), AS/NZS 3000, SANS 10142, NIS 197 |

### Reference and glossaries
| File | Content |
|------|---------|
| [terminology.md](terminology.md) | All abbreviations — U₀, SELV, PELV, ADS, Zs, Ze, Ia, In, Iz, k — with definitions and key formulas |
| [earthing-systems.md](earthing-systems.md) | TN-S / TN-C / TN-C-S / TT / IT explained — system descriptions, diagrams, selection guidance |
| [protective-device-types.md](protective-device-types.md) | MCB Types B/C/D, RCD types AC/A/F/B, fuses gG/aM, MCCB, ACB — selection guide |
| [cable-types-overview.md](cable-types-overview.md) | PVC / XLPE / EPR / MICC cable selection by application |
| [compliance-checklist.md](compliance-checklist.md) | End-of-design verification checklist — traceable evidence required |

### Part 4-41 — Protection against electric shock
| File | Content | Clause |
|------|---------|--------|
| [part4-41-electric-shock.json](part4-41-electric-shock.json) | ADS disconnection times (Table 41.1), Zs_max for MCBs and fuses, TT system checks, SELV/PELV voltage limits | Clauses 411–414 |

### Part 4-43 — Protection against overcurrent
| File | Content | Clause |
|------|---------|--------|
| [part4-43-overcurrent.json](part4-43-overcurrent.json) | Fundamental Rule Ib ≤ In ≤ Iz, overload and short-circuit protection, device placement | Clauses 431–435 |
| [fault-current.json](fault-current.json) | Adiabatic equation I²t ≤ k²S², k values for all conductor/insulation combinations | Clause 434.5 |

### Part 4-44 — Protection against overvoltage
| File | Content | Clause |
|------|---------|--------|
| [part4-44-overvoltage.json](part4-44-overvoltage.json) | SPD Types 1/2/3, impulse withstand categories I–IV, mandatory installation scope (AMD2:2018), coordination | Clauses 441–444 |

### Part 5-52 — Wiring systems (cable ratings)
| File | Content | Clause |
|------|---------|--------|
| [part5-52-cable-ratings-copper.json](part5-52-cable-ratings-copper.json) | Copper cable ratings (Tables B.52.4–B.52.10) — PVC 70°C and XLPE 90°C — all reference methods A1 to G | Annex B |
| [part5-52-cable-ratings-aluminium.json](part5-52-cable-ratings-aluminium.json) | Aluminium cable ratings — large submain sizes — methods C, D2, E | Annex B |
| [part5-52-correction-factors.json](part5-52-correction-factors.json) | Ambient temp (Table B.52.14), grouping (B.52.17–20), thermal insulation, soil resistivity, depth, harmonics | Annex B |
| [part5-52-voltage-drop.json](part5-52-voltage-drop.json) | Voltage drop limits (Annex G), mV/A/m for all standard copper and aluminium sizes | Annex G |
| [part5-52-installation-methods.json](part5-52-installation-methods.json) | Reference methods A1, A2, B1, B2, C, D1, D2, E, F, G — descriptions, conditions, selection | Clause 521 + Annex B |

### Part 5-54 — Earthing arrangements
| File | Content | Clause |
|------|---------|--------|
| [part5-54-earthing.json](part5-54-earthing.json) | Earthing system requirements, CPC sizing, equipotential bonding, earth electrode sizing | Clauses 541–545 |

### RCD requirements
| File | Content | Clause |
|------|---------|--------|
| [rcd-requirements.json](rcd-requirements.json) | RCD mandatory locations, types AC/A/F/B, 30mA additional protection scope, timing requirements | Clauses 411.3, 531, Part 7 |

### Part 6 — Verification
| File | Content | Clause |
|------|---------|--------|
| [part6-verification.json](part6-verification.json) | Initial verification (inspection + testing), periodic inspection, test methods and pass criteria, documentation | Part 6 |

### Part 7 — Special installations
| File | Content | Clause |
|------|---------|--------|
| [part7-special-locations.json](part7-special-locations.json) | Key sections 701 (bathrooms), 702 (pools), 703 (saunas), 704 (construction sites), 705 (agricultural), 708 (marinas), 710 (medical), 712 (PV), 714 (external lighting), 715 (ELV lighting), 722 (EV charging) | Part 7 |

---

## Coverage status

| Domain | Coverage | Notes |
|--------|----------|-------|
| Cable ratings (copper) | **Complete** | Methods A1, A2, B1, B2, C, D1, D2, E, F, G — PVC and XLPE |
| Cable ratings (aluminium) | **Complete** | Large submain sizes, methods C, D2, E |
| Correction factors | **Complete** | Temperature, grouping, insulation, soil, depth, harmonic |
| Voltage drop | **Complete** | Limits + mV/A/m for all common conductor sizes |
| ADS / Electric shock (Part 4-41) | **Complete** | TN/TT/IT, all voltage levels, Zs_max tables |
| RCD requirements | **Complete** | All mandatory locations, types, timing |
| Overcurrent protection (Part 4-43) | **Complete** | Fundamental Rule, device characteristics |
| Fault current / adiabatic | **Complete** | k values for all material/insulation combinations |
| Overvoltage / SPD (Part 4-44) | **Complete** | Including AMD2:2018 mandatory scope |
| Installation methods (Part 5-52) | **Complete** | All reference methods A1–G |
| Earthing arrangements (Part 5-54) | **Complete** | TN/TT/IT, CPC sizing, bonding |
| Special locations (Part 7) | **Complete** | Key sections 701, 702, 703, 704, 705, 708, 710, 712, 714, 715, 722 |
| Verification (Part 6) | **Complete** | Initial and periodic |
| Terminology | **Complete** | All abbreviations and formulas |
| National code mapping | **Complete** | BS 7671, NF C 15-100, AS/NZS 3000, SANS 10142, NIS 197 |
| Compliance checklist | **Complete** | Full end-of-design checklist |

---

## Relationship to BS 7671

BS 7671 (IET Wiring Regulations, UK 18th Edition) is the UK national implementation of IEC 60364.
The table below maps equivalent clauses:

| IEC 60364 clause | BS 7671 equivalent |
|------------------|--------------------|
| Part 4-41 (electric shock) | Part 4, Chapter 41 |
| Table 41.1 (disconnection times) | Tables 41.2 and 41.3 |
| Annex B (cable ratings) | Appendix 4 |
| Annex G (voltage drop) | Appendix 12 |
| Clause 434.5 (adiabatic) | Regulation 434.5.2 |
| Part 4-44 (SPD) | Regulation 443 |
| Part 5-52 (wiring systems) | Regulation 521–526 |
| Part 5-54 (earthing) | Part 5, Chapter 54 |
| Part 6 (verification) | Part 6 |
| Part 7 sections | Part 7 sections |

Key differences from BS 7671:
1. **Clause numbering** — IEC 60364 uses part/clause structure; BS 7671 uses regulation numbers
2. **Some cable ratings differ** — BS 7671 Appendix 4 values were adopted from older CENELEC tables and differ slightly from current IEC 60364-5-52:2009+AMD1 values in some rows
3. **UK-specific additions** — BS 7671 includes BS 88 HBC fuse data, BS 1362 domestic fuses, AFDD provisions, Part L cross-reference
4. **Ring final circuits** — Specific to BS 7671 / UK practice; IEC 60364 does not address them
5. **Earthing** — BS 7671 explicitly addresses PME; IEC 60364 uses the generic TN-C-S description

---

## How DraftsMan skills consume this

Skills reference these files by path in their `skill.manifest.json`:

```json
"standards_refs": [
  "shared/standards/electrical/IEC60364/part5-52-cable-ratings-copper.json",
  "shared/standards/electrical/IEC60364/part5-52-correction-factors.json",
  "shared/standards/electrical/IEC60364/part5-52-voltage-drop.json",
  "shared/standards/electrical/IEC60364/part4-41-electric-shock.json",
  "shared/standards/electrical/IEC60364/part4-43-overcurrent.json",
  "shared/standards/electrical/IEC60364/compliance-checklist.md"
]
```

When a project is in a BS 7671 jurisdiction (UK), use the `BS7671/` folder.
When a project is in any other IEC-aligned jurisdiction (Nigeria, Kenya, South Africa, etc.),
use `IEC60364/` as the base and cross-reference the appropriate `local-codes/` folder.

---

## File organisation

```
IEC60364/
├── README.md                              ← this file
├── meta.json                              ← all parts, editions, amendments
│
├── Reference & narrative (.md)
│   ├── terminology.md
│   ├── earthing-systems.md
│   ├── protective-device-types.md
│   ├── cable-types-overview.md
│   ├── compliance-checklist.md
│   └── relationship-to-national-codes.md
│
└── Machine-readable data (.json)
    ├── part4-41-electric-shock.json
    ├── part4-43-overcurrent.json
    ├── part4-44-overvoltage.json
    ├── fault-current.json
    ├── rcd-requirements.json
    ├── part5-52-cable-ratings-copper.json
    ├── part5-52-cable-ratings-aluminium.json
    ├── part5-52-correction-factors.json
    ├── part5-52-voltage-drop.json
    ├── part5-52-installation-methods.json
    ├── part5-54-earthing.json
    ├── part6-verification.json
    └── part7-special-locations.json
```

---

## Updating these files

When a new amendment or edition is published:

1. Update `meta.json` with the new entry.
2. Identify which JSON files contain values affected by the amendment.
3. Update affected files — annotate changes with amendment number in the `_note` field.
4. Bump `_version` in any affected file.
5. Check `relationship-to-national-codes.md` — national implementations may or may not adopt the change.
6. Run the eval suite for every skill that references the changed file.
7. Update the coverage status table in this README.

Never edit values silently — every change to a standards value must have a traceable amendment reference.
