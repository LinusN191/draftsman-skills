# NFPA 70 (NEC 2023) Standard Layer — Design Spec

**Date:** 2026-05-15
**Status:** Approved
**Scope:** Build the NFPA 70 (National Electrical Code, 2023 edition) standard layer — the US-side electrical standards layer covering all 9 Chapters. Fifth electrical standards layer after BS 7671, IEC 60364, IEC 60617, and IEC 61439.

---

## 1. Goal

Populate `shared/standards/electrical/NFPA70/` with a machine-readable engineering catalogue so that:

1. Any DraftsMan AI skill targeting US/North American projects can look up NEC articles, ampacity tables, grounding rules, and load-calculation methods.
2. Skills working across jurisdictions (US + international) can surface NEC-vs-IEC divergence at design time — terminology, sizing rules, hazardous-location classification systems, AFCI/GFCI vs RCD, etc.
3. The 2023 edition is canonical; key 2020→2023 changes are captured for transition support.

NFPA 70 is fundamentally different in structure from IEC 60364 — **Articles** organised into **9 Chapters**, native imperial units (AWG, kcmil, °F, in/ft), and a distinct grounding philosophy. The data model preserves this native structure rather than forcing IEC-style decomposition.

---

## 2. Decisions Made

| Decision | Choice | Rationale |
|---|---|---|
| Edition | 2023 | Most recent published NEC; some US states still on 2017/2020 — layer notes which articles changed between 2020 and 2023. 2026 edition not yet adopted anywhere. |
| Scope | Full NEC including Chapter 8 (communications) | User chose comprehensive coverage; matches the all-parts choice taken for IEC 61439. |
| Engineering depth | Full content with worked examples | Matches IEC 60364 / IEC 61439 / BS 7671 layer depth. |
| Cross-reference to IEC 60364 | One-way pointer + `divergence_notes` field on every article | Lets a skill targeting a bi-jurisdiction project surface the conflict at the article level. Centralised divergence catalogue in `nec-vs-iec-comparison.md` for browse. |
| File decomposition | Hybrid: per-Chapter index + per-heavy-Article + cross-cutting topic | Same pattern as IEC 61439; each chapter file ≤ ~500 lines; heavy articles get their own file; cross-cutting topics (grounding, OCPD coord, hazardous classification, ampacity correction, conduit fill, wiring methods) live in dedicated files. |
| File count | 39 (2 layer + 9 chapter + 17 article + 6 topic + 5 narrative) | Comprehensive but each file stays AI-loadable. |
| Units | NEC native (AWG, kcmil, °F, in/ft) with mm² in `tables_inline` notes where useful | Preserves the standard's authoritative form; designers reading the layer read native NEC. |
| Out of scope | NFPA 70E, NFPA 72, NFPA 110/111, state amendments, UL standards, pre-1999 Division-only, other NEC editions | Each is a separate standard or layer; not duplicated. |

---

## 3. Current State

| File | Status |
|---|---|
| `shared/standards/electrical/NFPA70/README.md` | Stub (`# NFPA70`) — must be rewritten |

Everything else must be created from scratch.

---

## 4. File Set — 39 Files Total

### 4.1 Layer-level (2)

| File | Content |
|---|---|
| `README.md` | Layer index — file catalogue, how skills consume it, schema overview, NEC↔IEC mapping pointer |
| `meta.json` | Standard title, NEC edition history (2017/2020/2023), state-adoption map (US + Mexico/PH/Saudi where adopted), NFPA / ANSI / ICC relationship, 3-year cycle policy |

### 4.2 Per-Chapter index JSONs (9)

| File | Articles covered | Content |
|---|---|---|
| `chapter1-general.json` | 90, 100, 110 | Introduction & purpose, definitions, general electrical-installation requirements (working space, identification, dedicated electrical space) |
| `chapter2-wiring-protection.json` | 200, 285 (light articles); 210/215/220/230/240/250 → per-article files | Use of grounded conductor (200), SPD (285); pointer to per-article files for heavy content |
| `chapter3-wiring-methods.json` | 300, 312, 314, 320–399 | General wiring methods, raceways (RMC/IMC/EMT/PVC), boxes/cabinets, wireways, cable types (NM, AC, MC, MI); pointer to Art 310 |
| `chapter4-equipment.json` | 400, 402, 404, 406, 408, 410, 422, 426, 427, 440, 460, 480; 430/450 → per-article files | Flexible cords, fixture wires, switches, receptacles, panelboards (light), luminaires, appliances, fixed electric heating, AC equipment, capacitors, batteries (light) |
| `chapter5-special-occupancies.json` | 511, 513, 514, 515, 516, 518, 520, 530, 547, 590; 500-506/517 → per-article files | Repair garages, hangars, gas stations, bulk storage, spray application, assembly occupancies, theaters, agricultural buildings, temporary installations |
| `chapter6-special-equipment.json` | 600, 604, 610, 620, 630, 645, 647, 660, 665, 670, 685; 625/680/690/695 → per-article files | Signs, manufactured wiring, cranes, elevators, arc welders, IT equipment, sensitive electronics, X-ray, induction/dielectric heating, industrial machinery |
| `chapter7-special-conditions.json` | 706, 710, 712, 720, 725, 727, 728, 760, 770; 700-705 → per-article files | Energy storage, stand-alone systems, DC microgrids, low-voltage circuits, Class 1/2/3, instrumentation, fire alarm, optical fiber |
| `chapter8-communications.json` | 800, 805, 810, 820, 830, 840 | Communications systems general, radio/TV, network-powered broadband, cable TV, premises-powered broadband. NEC Ch 8 stands alone — not subject to Ch 1–4 unless specifically referenced. |
| `chapter9-tables.json` | Tables 1–10, Annexes A–H summary | Conduit fill % (Table 1), conductor properties (Table 8 — AWG, kcmil, area, resistance, reactance), conduit/tubing dimensions (Tables 4 + 5), DC resistance/reactance, AC resistance/reactance, voltage-drop multipliers. The most-consumed reference in the layer. |

### 4.3 Per-heavy-Article JSONs (17)

| File | Article | Content |
|---|---|---|
| `art210-branch-circuits.json` | 210 | Branch-circuit ratings, GFCI requirements (210.8), AFCI requirements (210.12), receptacle outlet rules (210.50–210.71), required outlets by occupancy |
| `art215-feeders.json` | 215 | Feeder load, ampacity, GFP requirement at ≥1000 A (215.10), feeder taps |
| `art220-load-calculations.json` | 220 | General load calculations: lighting (220.12), receptacle (220.14), motor (220.50), AC (220.82), dwelling/non-dwelling Standard + Optional methods |
| `art230-services.json` | 230 | Service drop/lateral, service conductor ampacity, service entrance rated equipment, service disconnect (230.70-95), max 6-handle rule, GFP at services (230.95) |
| `art240-overcurrent.json` | 240 | OCPD types, interrupting rating, conductor protection (240.4), tap rules (240.21), location, supplementary OCPDs, series ratings |
| `art250-grounding-bonding.json` | 250 | System grounding, equipment grounding, grounding electrode system (250.50–68), GEC sizing (250.66), EGC sizing (250.122 — the NEC equivalent of BS 7671 Table 54.7), bonding (250.90–106), MBJ (250.28) |
| `art310-conductor-ampacity.json` | 310 | Conductor types/markings, ampacity tables 310.16 (raceway/cable), 310.17 (free air), correction factors (310.15(B)(2)(a) ambient, 310.15(C) grouping), 75 °C/90 °C/60 °C termination rule |
| `art408-panelboards.json` | 408 | Panelboard ratings, classification (lighting/appliance vs power), max OCPD count (42-circuit rule), spacings, marking, working clearances |
| `art430-motors.json` | 430 | Motor circuit conductor sizing (430.22), motor branch-circuit short-circuit/ground-fault protection (430.52), motor overload (430.32), motor disconnect (430.102), motor controller, MCC, motor circuit examples |
| `art450-transformers.json` | 450 | Transformer overcurrent protection (450.3), primary/secondary protection rules, transformer vault, sound insulation, ventilation, askarel/dry/oil/less-flammable liquid distinctions |
| `art500-506-hazardous-locations.json` | 500-506 (bundled) | Class I/II/III, Division 1/2 vs Zone 0/1/2, group classifications (A-D for gases, E-G for dusts), seal-off requirements, intrinsically safe (Art 504), nonincendive (Art 505/506) |
| `art517-healthcare.json` | 517 | Healthcare facility wiring: patient care areas, Type 1/2/3 receptacles, X-ray (517.71+), essential electrical system (Type 1/2/3 EES per 517.30+), isolated power systems |
| `art625-ev-charging.json` | 625 | EV charging power transfer system: levels 1/2/3, conductor sizing (125% continuous), GFCI requirements, ventilation (625.52), feeder calc method (625.41+), disconnect, load management |
| `art680-pools-spas.json` | 680 | Permanently installed pools (680.20–29), storable pools (680.30+), spas/hot tubs (680.40+), fountains (680.50+), hydromassage tubs (680.70+), GFCI rules, equipotential bonding (680.26) |
| `art690-solar-pv.json` | 690 | PV system definitions, circuit sizing (125% continuous), max voltage (690.7), DC arc fault (690.11), rapid shutdown (690.12), grounding (690.41–43), source/output circuits, inverter requirements |
| `art695-fire-pumps.json` | 695 | Fire pump power source, supply continuity, fire pump controller, conductor sizing (430 + 695.6), feeder location, disconnect prohibition |
| `art700-705-emergency-standby.json` | 700, 701, 702, 705 (bundled) | Emergency systems (700), legally required standby (701), optional standby (702), interconnected sources / paralleling (705): transfer-equipment classes, transfer-time classes, scope distinctions, capacity rules |

### 4.4 Cross-cutting topic JSONs (6)

| File | Content |
|---|---|
| `grounding-and-bonding.json` | Unified treatment of grounding across 250, 300.5, 310, 408, 450 — system grounding methods, GEC sizing, EGC sizing matrix, bonding bushings/locknuts/wedges, grounding electrode types (rod/plate/concrete-encased/ring) |
| `ocpd-coordination.json` | Selective coordination across 240, 700.32, 701.32, 645.27, 695.6 — when selectivity is required, methods, series-rated combinations, fuse-MCB coordination |
| `hazardous-locations-classification.json` | Unified Class/Division (US legacy) and Class/Zone (IEC-aligned) classification per 500-506, gas group ABCD vs IEC IIA/IIB/IIC, dust E/F/G vs IEC IIIA/IIIB/IIIC, equipment selection matrix, seal placement rules |
| `ampacity-correction-factors.json` | All correction factors collected: ambient (310.15(B)(2)(a) + Table), grouping (310.15(C) + tables), termination temperature limit rule (110.14(C)), demand factors (220 series). Worked example showing chain of corrections. |
| `conduit-fill.json` | NEC Chapter 9 Table 1 fill percentages (1 wire 53%, 2 wires 31%, ≥3 wires 40%), Table 4 raceway dimensions, Table 5 conductor dimensions, conduit/tubing-type selection matrix |
| `wiring-methods-by-occupancy.json` | Decision matrix: which raceway/cable types are permitted in which occupancies. NM (Art 334), AC (320), MC (330), MI (332), in dwellings vs commercial vs healthcare vs hazardous |

### 4.5 Narrative MDs (5)

| File | Content |
|---|---|
| `amendments-summary.md` | Edition history. Key changes 2017→2020→2023: AFCI expansion (210.12), receptacle GFCI expansion (210.8), 215.10 GFP for feeders ≥1000 A, energy storage Art 706 (2017), 625 EV updates (2020 & 2023), 690 rapid shutdown (2017+2020), 706 enhancements (2023). State-adoption status. |
| `nec-vs-iec-comparison.md` | The divergence catalogue — terminology, conductor sizing, earthing system rules, protective devices, hazardous-location classification, specific applications (EV/PV/pools/healthcare). |
| `compliance-checklist.md` | Designer-side checklist by project type: residential, commercial, industrial, healthcare, EV charging station, PV installation, ESS installation. References to AHJ acceptance, plan-review submission requirements, FM Global / IRI / utility additional reqs. |
| `terminology.md` | NEC-vs-IEC critical-distinction glossary: ground/earth, neutral/grounded conductor, AWG/kcmil/mm², kVA/horsepower, GFCI Class A vs Special-purpose, AFCI types (Branch/Feeder/Combination/Outlet), service vs feeder vs branch circuit. |
| `worked-examples.md` | 7 worked examples covering load calc (dwelling + multi-occupancy), motor circuit, hazardous-location selection, PV with 705 interconnection, EV charging with load management, healthcare emergency-vs-standby. |

---

## 5. Per-Article JSON Schema

Every article entry (in chapter index files AND per-heavy-article files) uses this schema. All fields mandatory.

```json
{
  "article_id":        "ART_250",
  "nec_ref":           "NFPA 70:2023 Article 250",
  "chapter":           2,
  "article_number":    250,
  "article_title":     "Grounding and Bonding",
  "scope":             "Requirements for systems and equipment grounding, equipment bonding, and grounding electrode systems. Applies to all installations covered by NEC except where modified by Articles 500–517 or specific other articles.",
  "applies_to":        ["all_systems", "service_grounded", "separately_derived"],
  "key_sections": [
    {"section": "250.4",   "title": "General Requirements", "summary": "Performance-based grounding requirements (effective ground-fault current path, low impedance)"},
    {"section": "250.50",  "title": "Grounding Electrode System", "summary": "Types of grounding electrodes that must be bonded together to form the GES"},
    {"section": "250.66",  "title": "Size of AC Grounding Electrode Conductor", "summary": "GEC sizing table by largest ungrounded service conductor"},
    {"section": "250.122", "title": "Size of Equipment Grounding Conductors", "summary": "EGC sizing table — the NEC equivalent of BS 7671 Table 54.7 / IEC 60364-5-54 Table 54.1"}
  ],
  "tabulated_values": {
    "gec_sizing_table_250_66": "see tables_inline",
    "egc_sizing_table_250_122": "see tables_inline"
  },
  "tables_inline": {
    "Table_250.66": {
      "title": "Grounding Electrode Conductor for AC Systems",
      "rows": [
        {"largest_ungrounded_cu_awg": "2 or smaller", "gec_cu_awg": "8"},
        {"largest_ungrounded_cu_awg": "1 or 1/0",     "gec_cu_awg": "6"},
        {"largest_ungrounded_cu_awg": "2/0 or 3/0",   "gec_cu_awg": "4"}
      ]
    }
  },
  "common_errors": [
    "Confusing GEC (250.66) with EGC (250.122) — different sizing rules",
    "Bonding neutral to ground at sub-panels — illegal except at service or first separately-derived disconnect (250.142)",
    "Treating concrete-encased electrode (Ufer) as optional — required when present (250.50)"
  ],
  "drawn_as":          ["EARTH_GENERAL", "EARTH_ELECTRODE", "CONDUCTOR_PE"],
  "related_iec_60364": ["IEC 60364-5-54 (Earthing arrangements and protective conductors)"],
  "divergence_notes":  "NEC uses 'grounding' / 'grounded conductor' / 'equipment grounding conductor' where IEC uses 'earthing' / 'neutral' / 'CPC'. NEC EGC sizes from 250.122 by OCPD rating; IEC 60364-5-54 sizes from line-conductor CSA (Table 54.1) OR adiabatic. NEC requires concrete-encased electrode when present (250.50(A)(3)); IEC does not mandate. NEC permits TN-C only within service equipment (250.142); IEC permits TN-C throughout for cables ≥ 10 mm² Cu / 16 mm² Al.",
  "related_bs_7671":   [],
  "usage_notes":       "Most cited NEC article in MEP design. Always confirm the AHJ accepts the chosen grounding electrode arrangement before issue. Specify EGC type (insulated/bare/raceway) per 250.118 and size per 250.122 with adiabatic verification for short cable runs with high fault current.",
  "related_articles":  ["ART_200", "ART_300", "ART_310", "ART_408", "ART_450"]
}
```

### Field definitions

| Field | Type | Description |
|---|---|---|
| `article_id` | string | UPPER_SNAKE_CASE; pattern `ART_<number>` (e.g. `ART_250`, `ART_500_506` for bundles) |
| `nec_ref` | string | Full reference: `NFPA 70:<edition> Article <num>` |
| `chapter` | integer | NEC Chapter (1–9) |
| `article_number` | integer | NEC Article number |
| `article_title` | string | Title from the standard, not paraphrased |
| `scope` | string | What this article applies to and the boundary with other articles |
| `applies_to` | string[] | Functional applicability tags used by skills to filter |
| `key_sections` | array | The 3–8 most-cited sections within this article with `{section, title, summary}` |
| `tabulated_values` | object | Names of inline tables (pointer index for skills) |
| `tables_inline` | object | Full tabulated data — rows in NEC's native units (AWG, kcmil, in, ft, °F) |
| `common_errors` | string[] | 3–5 mistakes the AI must learn to avoid; derived from real CMP reports and inspection data |
| `drawn_as` | string[] | IEC 60617 `symbol_id` values that render this article's typical devices |
| `related_iec_60364` | string[] | IEC clauses on the same topic |
| `divergence_notes` | string | Single paragraph flagging where NEC and IEC disagree. **Required** — write `"None — substantively aligned with IEC equivalent"` if truly no divergence |
| `related_bs_7671` | string[] | Always empty for NEC entries (different jurisdiction family) |
| `usage_notes` | string | Designer guidance: AHJ considerations, defaults, gotchas |
| `related_articles` | string[] | Other NEC articles to load alongside this one |

### Per-Chapter index file shape

Chapter files use the same `{_title, _version, ...}` header, then carry an `articles` array. For articles big enough to need their own file, the chapter file's entry is a short pointer:

```json
{
  "article_number": 250,
  "article_title":  "Grounding and Bonding",
  "scope":          "...short summary...",
  "full_content":   "art250-grounding-bonding.json"
}
```

For articles small enough to live inline, the chapter file holds the full per-article schema entry directly.

### Cross-cutting topic file convention

Same common header `{_title, _nec_chapter, _version, _note}` plus topic-specific structure. The 6 topic files do NOT use the article schema — each has its own shape fitted to the topic (correction-factor tables, classification matrices, etc.).

---

## 6. NEC↔IEC Divergence Catalogue (`nec-vs-iec-comparison.md`)

The most-cited NEC↔IEC differences MEP designers stumble on. Single most-consumed file by skills working across jurisdictions.

### Terminology (the silent breakers)

| NEC | IEC | Why it matters |
|---|---|---|
| Grounding | Earthing | Same concept, different word — never use both in one drawing/spec |
| Grounded conductor | Neutral | NEC uses "grounded" because in TN-C-S the neutral IS grounded at the service |
| Equipment grounding conductor (EGC) | Circuit protective conductor (CPC) | Sizing rules differ |
| GFCI (Class A, 6 mA) | RCD (typically 30 mA general use) | GFCI Class A is more sensitive than IEC general RCD |
| AFCI | (no exact equivalent in IEC 60364 base) | NEC mandates AFCI on many circuits; IEC base does not |
| AWG / kcmil | mm² | AWG decreases as size increases; mm² is direct |
| Branch circuit | Final circuit | Same idea |
| Feeder | Sub-main / distribution circuit | NEC keeps "feeder" as a distinct legal category |
| Service | DNO/utility supply intake | NEC has detailed service rules; IEC less prescriptive |

### Conductor / cable sizing

- NEC sizes EGC by OCPD rating (250.122 table); IEC sizes CPC by line-conductor CSA (Table 54.1) or adiabatic.
- NEC's 75 °C / 90 °C / 60 °C termination rule (110.14(C)) limits ampacity to the termination's temperature rating, not the conductor's.
- NEC ampacity tables (310.16/.17) use AWG with imperial reference methods; IEC Annex B uses mm² with named reference methods (A1, B1, C, etc.).

### Earthing systems

- NEC permits TN-C only within the service equipment (250.142); after the service disconnect, neutral and EGC must be separate.
- IEC permits TN-C throughout an installation for cables ≥ 10 mm² Cu / 16 mm² Al.
- NEC requires concrete-encased electrode ("Ufer") at every new building where present (250.50(A)(3)); IEC treats as optional.

### Protective devices

- NEC interrupting rating ≈ IEC Icu (ultimate). NEC interrupting rating does not include the Ics (service) concept.
- Series-rated combinations are common under NEC (240.86); IEC permits cascading but treats it more cautiously.
- AFCI types: Branch/Feeder (legacy), Combination (2008+), Outlet, System Combination.

### Hazardous locations

- NEC Class/Division (legacy US system) — Class I/II/III × Division 1/2.
- NEC Class/Zone (Article 505 — IEC-aligned, 1996+) — Class I × Zone 0/1/2.
- IEC 60079 uses Zone 0/1/2 (gas) and Zone 20/21/22 (dust) but not Class as prefix.
- Equipment marked for Division and Zone are not freely interchangeable.

### Specific applications

- EV: NEC 625 vs IEC 60364-7-722. NEC explicit on conductor sizing at 125% continuous (625.40); IEC requires 100% continuous per cable.
- PV: NEC 690 vs IEC 60364-7-712. NEC mandates rapid shutdown (690.12); IEC does not (yet — IEC TS 60364-8-2 emerging). NEC mandates DC arc fault detection (690.11); IEC silent.
- Pools/spas: NEC 680 vs IEC 60364-7-702. NEC has 5-foot rule for receptacles; IEC has zone-based geometry.
- Healthcare: NEC 517 vs IEC 60364-7-710. Different system classification — NEC Type 1/2/3 EES vs IEC Group 0/1/2 + safety/critical/general categories.

---

## 7. Worked Examples (`worked-examples.md`)

| # | Example | Articles invoked | What it demonstrates |
|---|---|---|---|
| 1 | Single-family dwelling 200 A service load calc | 220.82 (optional) + 220.40 (standard) | Both 220 methods side-by-side; how to choose; common rounding pitfalls |
| 2 | Strip-mall service & feeder design | 215, 220.40 (multi-occupancy), 230 | Multi-tenant load calc; main vs sub-feeder sizing; shared service rules |
| 3 | Motor circuit — 50 hp 460 V 3-phase | 430.6, 430.22, 430.32, 430.52, 430.102 | Full conductor + OCPD + overload + disconnect chain; using Table 430.250 FLA |
| 4 | Hazardous-location selection — gas station forecourt | 514, 500-506 | Class I Div 1 vs Zone 1 equipment selection; seal placement; conduit type |
| 5 | PV residential rooftop — 10 kW system | 690 + 705 + 215 | Module/inverter/PV-source-circuit sizing; rapid shutdown placement; interconnection at load side vs supply side per 705.12 |
| 6 | EV charging — 5-station commercial bay | 625 + 220 + 240 | 125% continuous sizing; load management per 625.42; feeder OCPD coordination |
| 7 | Emergency vs legally-required-standby — hospital | 517 + 700 + 701 | Three-bus split (life-safety / critical / equipment); transfer-equipment classes; selectivity across 700.32 / 701.32 |

Each example: **Given inputs → NEC article path → Calculation → Decision → AHJ-acceptance note**.

---

## 8. Cross-references

### Out (this layer references)
- IEC 60364 — every per-article `related_iec_60364` array + `divergence_notes` field, plus the comparison MD
- IEC 60617 — `drawn_as` on article entries with specific device types
- Other NFPA standards (70E, 72, 110, 111) — referenced by name in `usage_notes` but not duplicated

### In (anticipated consumers; no changes to those skills here)
- `electrical/sld` — when US-project support lands
- `electrical/db-layout`, `panel-schedule`, `load-schedule` — US load-calc methods (220.40, 220.82)
- `electrical/earthing` — Art 250 grounding electrode rules
- `electrical/solar-pv` — Art 690 + 705
- `electrical/ev-charging` (future) — Art 625
- `electrical/hvac-power` — Art 440 + 430
- A future `documents/specification-us` skill — NEC compliance assertions on tender specs

---

## 9. Out of Scope

- **NFPA 70E (Workplace Electrical Safety)** — separate standard; out of MEP design scope.
- **NFPA 72 (National Fire Alarm Code)** — separate standard; this layer covers only NEC Article 760 (fire alarm circuits within NEC).
- **NFPA 110 (Standby Power)** and **NFPA 111 (Stored Electrical Energy)** — referenced by Articles 700/701/702 but not duplicated.
- **State amendments** — California Electrical Code, Massachusetts Electrical Code, etc. — future per-state layers.
- **UL standards** — UL 67, UL 891, UL 489, etc. — referenced by NEC but not duplicated.
- **NEC 2017 / 2020 / 2026 editions** — only 2023 canonical. Amendments-summary captures 2020→2023 transition.
- **Pre-1999 Hazardous-location Division-only system** — covered alongside Article 505 (Zone) for new designs; legacy Division-only material is summary-level only.
- **Generated symbol files / IR schemas** — layer is input-only.

---

## 10. File Tree (final state)

```
NFPA70/
├── README.md                                ← rewrite
├── meta.json                                ← new
│
├── chapter1-general.json                    ← new (Arts 90, 100, 110)
├── chapter2-wiring-protection.json          ← new (Arts 200, 285)
├── chapter3-wiring-methods.json             ← new (Art 300 + raceways/cables)
├── chapter4-equipment.json                  ← new (Arts 400, 402, 404, 406, 410, 422, 426, 427, 440, 460, 480)
├── chapter5-special-occupancies.json        ← new (Arts 511-590 except 517)
├── chapter6-special-equipment.json          ← new (Arts 600-685 except 625, 680, 690, 695)
├── chapter7-special-conditions.json         ← new (Arts 706-770 except 700-705)
├── chapter8-communications.json             ← new (Arts 800-840)
├── chapter9-tables.json                     ← new (Tables 1-10, conductor properties, conduit dimensions)
│
├── art210-branch-circuits.json              ← new
├── art215-feeders.json                      ← new
├── art220-load-calculations.json            ← new
├── art230-services.json                     ← new
├── art240-overcurrent.json                  ← new
├── art250-grounding-bonding.json            ← new
├── art310-conductor-ampacity.json           ← new
├── art408-panelboards.json                  ← new
├── art430-motors.json                       ← new
├── art450-transformers.json                 ← new
├── art500-506-hazardous-locations.json      ← new
├── art517-healthcare.json                   ← new
├── art625-ev-charging.json                  ← new
├── art680-pools-spas.json                   ← new
├── art690-solar-pv.json                     ← new
├── art695-fire-pumps.json                   ← new
├── art700-705-emergency-standby.json        ← new
│
├── grounding-and-bonding.json               ← new
├── ocpd-coordination.json                   ← new
├── hazardous-locations-classification.json  ← new
├── ampacity-correction-factors.json         ← new
├── conduit-fill.json                        ← new
├── wiring-methods-by-occupancy.json         ← new
│
├── amendments-summary.md                    ← new
├── nec-vs-iec-comparison.md                 ← new
├── compliance-checklist.md                  ← new
├── terminology.md                           ← new
└── worked-examples.md                       ← new
```

**Total: 39 files** (2 layer + 9 chapter + 17 article + 6 topic + 5 narrative).

---

## 11. Layer Success Criteria

1. Any consuming skill can answer "what's the NEC equivalent of IEC 60364-7-722 EV charging?" by loading `art625-ev-charging.json` and reading `related_iec_60364` + `divergence_notes`.
2. Every article entry across all 9 chapter files and 17 per-article files has the 17 mandatory schema fields.
3. Chapter 9 tables (`chapter9-tables.json`) carry the full conductor-properties + conduit-fill data so skills doing ampacity / conduit-fill computations resolve without external lookups.
4. `nec-vs-iec-comparison.md` is concise enough (≤ 500 lines) to be loaded inline by any cross-jurisdiction skill prompt without dominating the context window.
5. Each JSON file ≤ ~500 lines; the heavy article files (250, 310, 690) ≤ ~700 lines.
