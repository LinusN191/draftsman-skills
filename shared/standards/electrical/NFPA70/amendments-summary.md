# NFPA 70 (NEC) — Amendments and Edition History

NEC publishes on a 3-year cycle. The 2023 edition is canonical for this layer.
This document captures the key designer-facing changes between 2017, 2020,
and 2023, and notes state-adoption status as of 2026.

---

## Cycle and adoption pattern

NEC is the National Electrical Code published by NFPA. Each 3-year cycle:

| Year | Edition | Publication | Typical state adoption |
|---|---|---|---|
| 2017 | 14th edition | Aug 2016 | All states adopted by ~2019 (some lagging until 2020+) |
| 2020 | 15th edition | Aug 2019 | Most states adopted by 2022-23 |
| 2023 | 16th edition | Aug 2022 | Adoption staggered 2023-2026; some states still on 2017/2020 |
| 2026 | 17th edition | Aug 2025 | Not yet adopted by any state |

State adoption is by reference + state-specific amendments. The state code
takes precedence over the federal NEC where amendments exist.

---

## 2017 → 2020 → 2023 — Key designer-facing changes

### Chapter 1 (Article 110)

- **110.16 Arc-Flash Hazard Warning (2017→2020 expansion):** Field marking
  required at switchboards, switchgear, panelboards, industrial control panels,
  meter socket enclosures, motor control centres "likely to require examination,
  servicing, or maintenance while energised." 2020 added more equipment types.

### Chapter 2 (Articles 210, 215, 220, 230, 250)

- **210.8 GFCI expansion:** Every cycle since 2017 has added GFCI requirements.
  - 2017: dwelling laundry receptacles GFCI'd
  - 2020: dwelling crawl space (210.8(A)(4) now full crawl space), dishwasher (210.8(A)(11))
  - 2023: outdoor receptacles for HVAC mini-split disconnects (210.8(F))
- **210.12 AFCI expansion:**
  - 2017: dwelling kitchen + laundry circuits added
  - 2020: closet circuits added
  - 2023: minor refinements
- **215.10 Feeder GFP (NEW 2017+):** Feeders ≥1000 A, >150 V to ground,
  <600 V phase-to-phase require GFP. Expanded coverage in 2020/2023.
- **220 — Optional Method updates:** 2020 added emergency standby + battery
  storage to dwelling load calc method (220.82(C)).
- **230.85 Outside Emergency Disconnect (NEW 2020):** One- and two-family dwellings
  require outside emergency disconnect at meter or near service. Expanded
  applicability in 2023.
- **250.32 Buildings Separately Derived:** Clarified bonding rules for multi-building
  installations (2020 and 2023 refinements).
- **250.66 GEC sizing:** Table values unchanged through cycles; clarifications on
  applicability in special cases.

### Chapter 3 (Article 310)

- **310.15 Ampacity tables restructured (2014):** What was Table 310.16 etc.
  consolidated/renumbered. 2017 → 2020 → 2023 maintained structure.
- **310.15(B)(1) Ambient correction:** Values unchanged; presentation refined.
- **310.15(C)(1) Grouping:** Values unchanged.

### Chapter 4 (Articles 408, 410, 422, 440)

- **408.43 Panelboard EGC Bus:** Required, and bonding to grounded conductor
  prohibited except at service or first separately-derived disconnect.
- **410.10(F) Luminaires in Indoor Wet Locations:** 2017 clarified IP requirements
  for indoor wet locations.
- **422 Appliances:** GFCI for additional appliance categories (dishwashers,
  garbage disposals — 2017/2020 changes).

### Chapter 5 (Articles 500-506, 517)

- **517.13 Healthcare grounding:** Clarified that ALL patient care receptacles
  (not just hospital-grade) require dual grounding in Category 1/2 areas.
- **500-506:** Minor refinements to area classification criteria.

### Chapter 6 (Articles 625, 690, 695, 700)

- **625 EV Charging (massive 2020 + 2023 changes):**
  - 2020: Load management formalised (625.42), Type B RCD/EGFCI clarified, 125% continuous explicit
  - 2023: Bidirectional power transfer (V2G) provisions added
- **690 PV (2017 + 2020 + 2023 expansions):**
  - 2017: Rapid shutdown (690.12) introduced — 1-ft and 5-ft boundaries
  - 2020: Module-level rapid shutdown clarified; PV system labeling expanded
  - 2023: DC arc fault (690.11) ≥80 V refined; PV+ESS coordination strengthened
- **705 Interconnection:** 2020 added bidirectional inverter (705.12(B)) provisions.
- **706 Energy Storage Systems (NEW Article in 2017):**
  - 2017: First introduction. UL 9540 listing requirement.
  - 2020: Self-contained ESS (706.20+) detailed; NFPA 855 cross-reference
  - 2023: Refinements for residential battery storage

### Chapter 7 (Articles 700, 701, 702, 705, 706, 770)

- **700.32 / 701.32 Selective coordination:** Wording and applicability refined
  each cycle. 2023 clarified that selectivity is required across the entire
  fault current range, not just at maximum fault current.
- **712 DC Microgrids (NEW 2014):** Maintained through 2017/2020/2023; little change.
- **770 Optical Fiber:** Minor refinements.

### Chapter 8 (Articles 800-840)

- **800.100 Bonding:** Clarified that primary protector grounding is to building
  grounding electrode system (not separate ground rod) per 2017 update.
- **840 Premises-Powered Broadband:** Created/refined alongside FTTP expansion.

---

## State adoption snapshot (as of 2026-05-15)

| State | NEC base edition | State amendments |
|---|---|---|
| California (CEC 2022) | 2020 | Yes — Title 24 + California Electrical Code |
| Texas | 2020 | Some |
| New York (NY-CEC) | 2017 | Substantial |
| Florida (NEC + FBC) | 2023 | Yes |
| Illinois | 2020 | Limited |
| Massachusetts (527 CMR 12) | 2020 | Substantial |
| Washington | 2023 | Limited |
| Oregon | 2023 | Limited |
| Colorado | 2023 | Limited |
| Pennsylvania | 2023 | Limited |
| Ohio | 2017 | Substantial |

Always confirm the actual AHJ's adopted edition at project start — this layer
covers 2023 but state amendments may override.

---

## When to consult the older editions

- **Existing-building work:** The edition in force at original installation
  governs grandfather provisions. The 2023 design layer still applies to NEW
  work, but existing work may be reviewed against an older edition.
- **Retrofits and tenant improvements:** Generally must comply with the AHJ's
  currently adopted edition; consult amendments-summary above for transition
  changes.
- **Litigation / forensics:** The edition in force at the time of installation
  is what applies — confirm with AHJ records.

This layer covers ONLY the 2023 edition. For older-edition lookups, consult
NFPA's archived PDFs or the AHJ.
