# BS 7671:2018+A2:2022 — IET Wiring Regulations (18th Edition)

Machine-readable extracts and supplementary guidance for BS 7671, for
use by DraftsMan skills and the engineers reviewing their output.

**Edition:** 18th Edition, Amendment 2 (2022). Current as of 2024.
**Publisher:** IET / BSI.

> Always verify values against the current purchased copy of the standard.
> This is a reference layer for AI agents — it is not a substitute for the
> standard itself, and it does not replace engineering judgement.

---

## Index

### Edition metadata
| File | Content |
|------|---------|
| [meta.json](meta.json) | Edition, amendments, effective dates, structure of the standard |
| [amd1-amd2-summary.md](amd1-amd2-summary.md) | What changed in each amendment, effective dates, practical impact |

### Reference and glossaries
| File | Content |
|------|---------|
| [terminology.md](terminology.md) | All abbreviations — Zs, Ze, Ib, In, Iz, k, PSCC etc. with definitions and key formulas |
| [earthing-systems-explained.md](earthing-systems-explained.md) | TN-S / TN-C-S / TT / IT explained with diagrams, when to use each |
| [protective-device-types.md](protective-device-types.md) | MCB / RCBO / RCD / HRC fuse / MCCB / ACB / AFDD selection guide |
| [cable-types-overview.md](cable-types-overview.md) | T&E / LSZH / SWA / MICC selection by application (non-fire-rated) |
| [compliance-checklist.md](compliance-checklist.md) | End-of-design verification checklist with traceable evidence |
| [pscc-determination.md](pscc-determination.md) | How to obtain or calculate PSCC at any point in the system |
| [inspection-and-testing.md](inspection-and-testing.md) | Part 6 — initial verification, periodic inspection, EICR, certificates |

### Appendix 4 — Current-carrying capacity
| File | Content | Clause |
|------|---------|--------|
| [appendix4-cable-ratings.json](appendix4-cable-ratings.json) | Copper cable ratings (Tables 4D2A, 4D2B, 4D4A) — all installation methods | App 4 |
| [appendix4-cable-ratings-aluminium.json](appendix4-cable-ratings-aluminium.json) | Aluminium cable ratings (Tables 4E2A, 4E4A) — for large submains | App 4 |
| [appendix4-correction-factors.json](appendix4-correction-factors.json) | Ambient (4B1), grouping (4C1), thermal insulation, soil, harmonic | App 4 |

### Appendix 12 — Voltage drop
| File | Content | Clause |
|------|---------|--------|
| [appendix12-voltage-drop.json](appendix12-voltage-drop.json) | Limits, formula, mV/A/m, worked examples including fail case | App 12 |

### Appendix 3 — Device characteristics
| File | Content | Clause |
|------|---------|--------|
| [appendix3-device-curves.json](appendix3-device-curves.json) | Time/current characteristics — Type B/C/D MCBs, BS 88 fuses, RCDs, selectivity | App 3 |

### Part 4 — Protection for safety
| File | Content | Clause |
|------|---------|--------|
| [reg411-disconnection-times.json](reg411-disconnection-times.json) | Tables 41.2/41.3 — Zs_max for MCBs and fuses, RCD Zs limits | Reg 411 |
| [reg411-rcd-requirements.json](reg411-rcd-requirements.json) | RCD mandatory protection, types AC/A/F/B, special locations | Reg 411.3.3, 411.3.4 |
| [reg433-overcurrent-protection.json](reg433-overcurrent-protection.json) | Fundamental Rule Ib ≤ In ≤ Iz, device characteristics, full sequence | Reg 433 |
| [reg434-fault-current.json](reg434-fault-current.json) | Adiabatic equation, k values (Tables 54.2–54.6) | Reg 434 |
| [reg443-spd.json](reg443-spd.json) | SPD Types 1/2/3, impulse withstand categories I–IV, coordination | Reg 443 |

### Part 5 — Selection and erection
| File | Content | Clause |
|------|---------|--------|
| [reg521-installation-methods.json](reg521-installation-methods.json) | Methods A1, A2, B1, B2, C, D1, D2, E, F — descriptions and selection | Reg 521 |
| [reg522-ip-ratings.json](reg522-ip-ratings.json) | IP rating selection by environment, IK impact codes | Reg 522 |

### Part 7 — Special installations / Locations
| File | Content | Clause |
|------|---------|--------|
| [part7-special-locations.json](part7-special-locations.json) | Sections 701–730 detailed — bathrooms, pools, marinas, medical, EV | Part 7 |

### Building Regulations cross-reference
| File | Content |
|------|---------|
| [part-l-controls-reference.md](part-l-controls-reference.md) | Building Regulations Part L 2021 controls and efficacy requirements |

### Specialist cable data
| File | Content |
|------|---------|
| [cable-types-fire-rated.json](cable-types-fire-rated.json) | FP200 Gold, FP400 PLUS, MICC — fire ratings, life-safety mapping |

### Design data
| File | Content |
|------|---------|
| [diversity-factors.json](diversity-factors.json) | OSG Appendix A — domestic, commercial, EV, healthcare diversity |

### Legacy / deprecated
(none — `cable-current-ratings.json` was removed Sprint C.4 / L2 after being deprecated for one minor version; consumers migrated to `appendix4-cable-ratings.json` + `appendix4-correction-factors.json`.)

---

## Coverage status

| Domain | Coverage | Notes |
|--------|----------|-------|
| Cable ratings (copper) | **Complete** | All installation methods, single-core, multi-core, SWA |
| Cable ratings (aluminium) | **Complete** | Large submain sizes, methods C/D2/E |
| Correction factors | **Complete** | Temperature, grouping, insulation, soil, depth, harmonic |
| Voltage drop | **Complete** | Limits + mV/A/m for all common sizes + worked examples |
| Device time/current curves | **Complete** | Typical envelopes — manufacturer data still required for final design |
| ADS (Reg 411) | **Complete** | Tables 41.2 and 41.3 |
| RCD requirements | **Complete** | All special locations covered |
| Overcurrent (Reg 433) | **Complete** | Fundamental Rule + device characteristics |
| Fault current (Reg 434) | **Complete** | Adiabatic + k values for all material/insulation combinations |
| SPD (Reg 443) | **Complete** | Including AMD 2 expanded scope |
| Installation methods | **Complete** | All methods A1–G with design notes |
| IP ratings (Reg 522) | **Complete** | All standard ratings with minimums per location |
| Special locations (Part 7) | **Complete** | Sections 701, 702, 703, 704, 705, 708, 709, 710, 711, 712, 715, 717, 722, 730 |
| Inspection & testing (Part 6) | **Complete** | Initial verification, periodic, EICR, certificates, CDM 2015 duties |
| Fire-rated cables | **Complete** | Product-level data for FP200 / FP400 / MICC |
| Diversity factors | **Complete** | Domestic, commercial, industrial, EV |
| PSCC determination | **Complete** | Methods, worked example, common errors |
| Terminology | **Complete** | All abbreviations defined |
| Earthing systems | **Complete** | TN-S/TN-C-S/TT/IT with diagrams and selection guidance |
| Amendment history | **Complete** | AMD 1 and AMD 2 changes summarised |
| Compliance verification | **Complete** | Full end-of-design checklist |

---

## How DraftsMan skills consume this

Skills reference these files by path in their `skill.manifest.json`:

```json
"standards_refs": [
  "shared/standards/electrical/BS7671/appendix4-cable-ratings.json",
  "shared/standards/electrical/BS7671/appendix4-correction-factors.json",
  "shared/standards/electrical/BS7671/appendix12-voltage-drop.json",
  "shared/standards/electrical/BS7671/reg411-disconnection-times.json",
  "shared/standards/electrical/BS7671/reg433-overcurrent-protection.json",
  "shared/standards/electrical/BS7671/compliance-checklist.md"
]
```

The skill prompt then instructs the agent to load and use these values
rather than recalling them from training data. This ensures every skill
operates on the same authoritative numbers, and that updating a standard
value cascades to all skills automatically.

---

## File organisation

```
BS7671/
├── README.md                          ← this file
├── meta.json                          ← edition info
│
├── Reference & narrative (.md)
│   ├── terminology.md
│   ├── earthing-systems-explained.md
│   ├── protective-device-types.md
│   ├── cable-types-overview.md
│   ├── compliance-checklist.md
│   ├── amd1-amd2-summary.md
│   ├── pscc-determination.md
│   ├── inspection-and-testing.md
│   └── part-l-controls-reference.md
│
├── Machine-readable data (.json)
│   ├── appendix3-device-curves.json
│   ├── appendix4-cable-ratings.json
│   ├── appendix4-cable-ratings-aluminium.json
│   ├── appendix4-correction-factors.json
│   ├── appendix12-voltage-drop.json
│   ├── reg411-disconnection-times.json
│   ├── reg411-rcd-requirements.json
│   ├── reg433-overcurrent-protection.json
│   ├── reg434-fault-current.json
│   ├── reg443-spd.json
│   ├── reg521-installation-methods.json
│   ├── reg522-ip-ratings.json
│   ├── part7-special-locations.json
│   ├── cable-types-fire-rated.json
│   └── diversity-factors.json
```

---

## Updating these files

When a new amendment is published:

1. Update `meta.json` with the new amendment entry.
2. Update `amd1-amd2-summary.md` with a new section.
3. Identify which JSON files contain values affected by the amendment.
4. Update affected JSON files. Annotate changes with the amendment number in the `_note` field.
5. Bump the `_version` of any affected file.
6. Run the eval suite for every skill that references the changed file.
7. Update the project CHANGELOG.

Never edit values silently — every change to a standards value must
have a traceable amendment reference.
