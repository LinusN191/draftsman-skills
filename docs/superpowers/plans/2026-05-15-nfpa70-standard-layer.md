# NFPA 70 (NEC 2023) Standard Layer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the NFPA 70 (NEC 2023) standard layer — 39 files in `shared/standards/electrical/NFPA70/` covering all 9 Chapters with per-article depth, NEC↔IEC divergence notes, and 7 worked examples. The US-side counterpart to the existing IEC 60364 layer.

**Architecture:** Hybrid file decomposition. 9 per-Chapter index JSONs carry general/lightweight content + pointers to heavy article files. 17 per-heavy-Article JSONs carry full depth on the most-cited MEP articles. 6 cross-cutting topic JSONs consolidate concepts that span articles (grounding, OCPD coord, hazardous-location classification, ampacity correction, conduit fill, wiring-methods-by-occupancy). 5 narrative MDs (amendments, NEC↔IEC comparison, compliance checklist, terminology, worked examples). Every article entry carries a one-way `related_iec_60364` array + `divergence_notes` field.

**Tech Stack:** JSON (RFC 8259), Markdown (CommonMark). Native NEC units (AWG, kcmil, °F, in/ft). No code or build scripts in this layer — input-only. Validation via Python `json.load`.

**Reference:** See `docs/superpowers/specs/2026-05-15-nfpa70-standard-layer-design.md` for the per-article schema, file organisation rationale, divergence catalogue, worked-examples list, and decision log.

---

## File Structure

```
shared/standards/electrical/NFPA70/
├── README.md                                ← rewrite (current is stub)
├── meta.json                                ← new
│
├── chapter1-general.json                    ← new (Arts 90, 100, 110)
├── chapter2-wiring-protection.json          ← new (Arts 200, 285; pointers to per-article)
├── chapter3-wiring-methods.json             ← new (Art 300 + raceways/cables)
├── chapter4-equipment.json                  ← new (Arts 400-490 except 430/450)
├── chapter5-special-occupancies.json        ← new (Arts 511-590 except 517)
├── chapter6-special-equipment.json          ← new (Arts 600-685 except 625/680/690/695)
├── chapter7-special-conditions.json         ← new (Arts 706-770 except 700-705)
├── chapter8-communications.json             ← new (Arts 800-840)
├── chapter9-tables.json                     ← new (Tables 1-10 + conductor properties)
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
├── art500-506-hazardous-locations.json      ← new (bundle)
├── art517-healthcare.json                   ← new
├── art625-ev-charging.json                  ← new
├── art680-pools-spas.json                   ← new
├── art690-solar-pv.json                     ← new
├── art695-fire-pumps.json                   ← new
├── art700-705-emergency-standby.json        ← new (bundle)
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

No consumer-skill manifest changes in this plan — adding NFPA70 to specific skill manifests' `standards` arrays is a follow-on PR.

---

## Per-Article JSON Schema (used by every article entry)

```json
{
  "article_id":        "ART_<num>",
  "nec_ref":           "NFPA 70:2023 Article <num>",
  "chapter":           <int 1-9>,
  "article_number":    <int>,
  "article_title":     "<string — verbatim from NEC>",
  "scope":             "<string — what this article applies to and the boundary>",
  "applies_to":        ["<tag>", "<tag>", ...],
  "key_sections": [
    {"section": "<NEC §>", "title": "<string>", "summary": "<one-sentence>"}
  ],
  "tabulated_values":  {"<table_name>": "<short description or pointer>"},
  "tables_inline":     {"<Table_id>": {"title": "<string>", "rows": [...]}},
  "common_errors":     ["<string>", ...],
  "drawn_as":          ["<IEC60617 symbol_id>", ...],
  "related_iec_60364": ["<IEC clause>", ...],
  "divergence_notes":  "<single paragraph — required; write 'None — substantively aligned' if no divergence>",
  "related_bs_7671":   [],
  "usage_notes":       "<designer guidance>",
  "related_articles":  ["ART_<num>", ...]
}
```

**Field invariant:** All 17 fields mandatory on every article entry across all 9 chapter files and 17 per-article files.

---

## Validation Commands

Every JSON-creating task runs these:

- JSON syntax: `python3 -c "import json; json.load(open('PATH'))" && echo OK`
- Per-article schema check (for any file that contains `articles` array of full entries):
  ```bash
  python3 -c "import json; data=json.load(open('PATH')); req=['article_id','nec_ref','chapter','article_number','article_title','scope','applies_to','key_sections','tabulated_values','tables_inline','common_errors','drawn_as','related_iec_60364','divergence_notes','related_bs_7671','usage_notes','related_articles']; arts=[a for a in data.get('articles',[]) if 'full_content' not in a]; missing=[(a.get('article_id','?'), [f for f in req if f not in a]) for a in arts if any(f not in a for f in req)]; print('OK' if not missing else 'MISSING:'+str(missing))"
  ```
- IEC 60617 `drawn_as` resolution:
  ```bash
  python3 - <<'PY'
  import json, sys
  idx = {s['symbol_id'] for s in json.load(open('shared/standards/electrical/IEC60617/symbol-index.json'))['symbols']}
  data = json.load(open(sys.argv[1] if len(sys.argv)>1 else 'PATH'))
  unknown = [(a.get('article_id','?'), s) for a in data.get('articles',[]) if 'full_content' not in a for s in a.get('drawn_as', []) if s not in idx]
  print('OK' if not unknown else 'UNKNOWN: '+str(unknown))
  PY
  ```

---

## Task 1: meta.json and README.md rewrite

**Files:**
- Create: `shared/standards/electrical/NFPA70/meta.json`
- Modify (full rewrite): `shared/standards/electrical/NFPA70/README.md`

- [ ] **Step 1: Write meta.json**

```json
{
  "_title": "NFPA 70 — National Electrical Code (NEC)",
  "_version": "1.0.0",
  "_purpose": "US-side electrical standards source of truth. Covers all 9 Chapters of NEC 2023 with per-article depth, NEC↔IEC divergence catalogue, and worked examples. Consumed by skills targeting US/North American projects.",
  "standard": {
    "title": "National Electrical Code",
    "issuer": "National Fire Protection Association",
    "issuer_short": "NFPA",
    "designation": "NFPA 70",
    "canonical_edition": "2023",
    "publication_cycle_years": 3,
    "publisher_url": "https://www.nfpa.org/codes-and-standards/nfpa-70-standard-development/70",
    "ansi_designation": "ANSI/NFPA 70",
    "chapters_total": 9
  },
  "edition_history": [
    {"edition": "2017", "key_changes_summary": "Energy storage Article 706 added; rapid shutdown (690.12) expanded; AFCI coverage broadened"},
    {"edition": "2020", "key_changes_summary": "GFCI receptacle requirements expanded (210.8); 215.10 GFP for feeders ≥1000 A; further EV/PV updates"},
    {"edition": "2023", "key_changes_summary": "Energy storage updates (706); EV charging refinements (625); receptacle expansion (210.8(F)); broader AFCI coverage", "status": "canonical"},
    {"edition": "2026", "key_changes_summary": "PV/storage integration; further EV updates", "status": "not yet adopted by any state as of layer build date"}
  ],
  "state_adoption_map_2026": {
    "_note": "Snapshot. Adoption is set by each state's electrical board / authority having jurisdiction; check current status before issue.",
    "edition_2023": ["AL", "AR", "CO", "DE", "FL", "ID", "IL", "IN", "IA", "KY", "LA", "MD", "MI", "MN", "NE", "NV", "NH", "NJ", "NM", "NY", "ND", "OK", "PA", "RI", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"],
    "edition_2020": ["AK", "AZ", "CT", "GA", "HI", "ME", "MS", "MO", "MT", "NC", "OH", "OR", "SC", "SD", "DC"],
    "edition_with_state_amendments": ["CA (California Electrical Code, based on NEC 2023 with state amendments)", "MA (Massachusetts Electrical Code, based on NEC 2023 with state amendments)"]
  },
  "international_adoption_notes": [
    "Mexico — NOM-001-SEDE is based on NEC structure but adapted",
    "Philippines — Philippine Electrical Code (PEC) Part 1 closely follows NEC",
    "Saudi Arabia — partial adoption in some industrial sectors; SBC 401 is local code",
    "Colombia / Costa Rica / Panama — NEC adopted with local amendments"
  ],
  "relationship_to_other_standards": {
    "NFPA_70E": "Workplace electrical safety. Separate standard; not duplicated here. Out of MEP design scope.",
    "NFPA_72":  "National Fire Alarm Code. Separate; this layer covers only Article 760 (Fire Alarm Circuits) within NEC.",
    "NFPA_110": "Emergency and Standby Power Systems. Referenced by Articles 700/701/702 but not duplicated here.",
    "NFPA_111": "Stored Electrical Energy. Referenced by Article 706 but not duplicated here.",
    "UL_67":    "Panelboards. Referenced by Article 408 — not duplicated here.",
    "UL_891":   "Switchboards. Referenced by Article 408 — not duplicated here.",
    "UL_489":   "Molded-Case Circuit Breakers. Referenced by Article 240 — not duplicated here.",
    "IEC_60364":"International electrical-installations standard. Cross-referenced from every NFPA70 article via `related_iec_60364` + `divergence_notes`. See nec-vs-iec-comparison.md for the divergence catalogue."
  },
  "out_of_scope": [
    "NFPA 70E (workplace electrical safety, PPE, arc-flash analysis)",
    "NFPA 72 (fire alarm system design beyond NEC Article 760)",
    "NFPA 110 / 111 (standby power and stored electrical energy beyond NEC 700-706)",
    "State amendments (California, Massachusetts, etc.) — future per-state layers",
    "UL equipment standards referenced by NEC",
    "Pre-1999 Class/Division-only legacy material — Article 505/506 Zone covered for new designs",
    "NEC editions 2017, 2020, 2026 — only 2023 canonical; transition notes in amendments-summary.md"
  ],
  "files": {
    "layer_level":     ["README.md", "meta.json"],
    "per_chapter":     ["chapter1-general.json", "chapter2-wiring-protection.json", "chapter3-wiring-methods.json", "chapter4-equipment.json", "chapter5-special-occupancies.json", "chapter6-special-equipment.json", "chapter7-special-conditions.json", "chapter8-communications.json", "chapter9-tables.json"],
    "per_article":     ["art210-branch-circuits.json", "art215-feeders.json", "art220-load-calculations.json", "art230-services.json", "art240-overcurrent.json", "art250-grounding-bonding.json", "art310-conductor-ampacity.json", "art408-panelboards.json", "art430-motors.json", "art450-transformers.json", "art500-506-hazardous-locations.json", "art517-healthcare.json", "art625-ev-charging.json", "art680-pools-spas.json", "art690-solar-pv.json", "art695-fire-pumps.json", "art700-705-emergency-standby.json"],
    "cross_cutting":   ["grounding-and-bonding.json", "ocpd-coordination.json", "hazardous-locations-classification.json", "ampacity-correction-factors.json", "conduit-fill.json", "wiring-methods-by-occupancy.json"],
    "narrative":       ["amendments-summary.md", "nec-vs-iec-comparison.md", "compliance-checklist.md", "terminology.md", "worked-examples.md"]
  }
}
```

- [ ] **Step 2: Rewrite README.md**

````markdown
# NFPA 70 — National Electrical Code (NEC)

**Standard:** NFPA 70 (US National Electrical Code)
**Canonical edition:** 2023
**Cycle:** 3 years (2017 → 2020 → 2023 → 2026)
**Scope of this layer:** All 9 Chapters with per-article depth and worked examples.

This layer is the US-side electrical standards source of truth. It complements:

- **IEC 60364** — international electrical-installations standard. Every NFPA article entry cross-references the equivalent IEC clause via `related_iec_60364` and flags conflicts in `divergence_notes`. See `nec-vs-iec-comparison.md` for the full divergence catalogue.
- **IEC 60617** — graphical symbols. NFPA article entries that describe specific device types reference IEC 60617 `symbol_id` values via `drawn_as`.

**Designers working bi-jurisdiction projects:** load this layer + IEC 60364 + the comparison MD. The `divergence_notes` per article surface the conflicts at the article level.

---

## Files

| File | Purpose |
|---|---|
| `meta.json` | Standard title, edition history, state-adoption map, relationship to NFPA 70E/72/110/111 |
| `chapter1-general.json` | Articles 90 (Intro), 100 (Definitions), 110 (General installation requirements) |
| `chapter2-wiring-protection.json` | Articles 200, 285 (light); pointers to 210/215/220/230/240/250 |
| `chapter3-wiring-methods.json` | Articles 300, 312, 314, 320-399 (raceways, cables, boxes); pointer to 310 |
| `chapter4-equipment.json` | Articles 400, 402, 404, 406, 408, 410, 422, 426, 427, 440, 460, 480; pointers to 430, 450 |
| `chapter5-special-occupancies.json` | Articles 511, 513, 514, 515, 516, 518, 520, 530, 547, 590; pointers to 500-506, 517 |
| `chapter6-special-equipment.json` | Articles 600, 604, 610, 620, 630, 645, 647, 660, 665, 670, 685; pointers to 625, 680, 690, 695 |
| `chapter7-special-conditions.json` | Articles 706, 710, 712, 720, 725, 727, 728, 760, 770; pointer to 700-705 |
| `chapter8-communications.json` | Articles 800, 805, 810, 820, 830, 840 (standalone chapter under NEC) |
| `chapter9-tables.json` | Tables 1-10 — conduit fill, conductor properties (AWG/kcmil area, R, X), conduit/tubing dimensions, voltage drop multipliers |
| `art210-branch-circuits.json` … `art700-705-emergency-standby.json` | 17 per-heavy-article files (210, 215, 220, 230, 240, 250, 310, 408, 430, 450, 500-506 bundle, 517, 625, 680, 690, 695, 700-705 bundle) |
| `grounding-and-bonding.json` | Unified grounding treatment across 250, 300.5, 310, 408, 450 — GEC sizing, EGC matrix, electrode types, bonding hardware |
| `ocpd-coordination.json` | Selective coordination across 240, 700.32, 701.32, 645.27, 695.6 — methods, series ratings, fuse-MCB coordination |
| `hazardous-locations-classification.json` | Unified Class/Division (US legacy) and Class/Zone (IEC-aligned) per 500-506; gas/dust group conversion; equipment selection matrix |
| `ampacity-correction-factors.json` | Ambient (310.15(B)(2)(a)), grouping (310.15(C)), termination rule (110.14(C)), demand factors (220 series) |
| `conduit-fill.json` | Chapter 9 Table 1 fill %, Table 4 raceway dimensions, Table 5 conductor dimensions, conduit-type selection matrix |
| `wiring-methods-by-occupancy.json` | Decision matrix: which raceway/cable types in which occupancies. NM/AC/MC/MI in dwellings vs commercial vs healthcare vs hazardous |
| `amendments-summary.md` | Edition history; 2020→2023 key changes |
| `nec-vs-iec-comparison.md` | Terminology, conductor sizing, earthing, OCPD, hazardous-location, EV/PV/pools/healthcare divergences |
| `compliance-checklist.md` | Designer-side checklist by project type |
| `terminology.md` | NEC↔IEC critical-distinction glossary |
| `worked-examples.md` | 7 worked examples |

---

## How skills use this layer

**Specifying to NEC for a US project:**
1. Load `chapter<n>-*.json` for general requirements.
2. For heavy articles cited in the design (e.g. 250 grounding), load the dedicated `art<num>-*.json`.
3. Copy `key_sections`, `tables_inline`, and `common_errors` into the skill's reasoning.

**Working bi-jurisdiction (US + international):**
1. Load NEC article AND its `related_iec_60364` references.
2. Read `divergence_notes` per article — surface in rationale.
3. Use the comparison MD for terminology reconciliation.

**Per-article schema invariant:** every entry across the 9 chapter files and 17 per-article files has the same 17 mandatory fields. Skills can rely on this.

---

## Per-article schema

```json
{
  "article_id":        "ART_<number>",
  "nec_ref":           "NFPA 70:2023 Article <number>",
  "chapter":           <int 1-9>,
  "article_number":    <int>,
  "article_title":     "<verbatim NEC title>",
  "scope":             "<applicability and boundary>",
  "applies_to":        ["<tag>", ...],
  "key_sections":      [{"section": "<§>", "title": "<string>", "summary": "<string>"}],
  "tabulated_values":  {"<table_name>": "<description>"},
  "tables_inline":     {"<Table_id>": {"title": "<string>", "rows": [...]}},
  "common_errors":     ["<string>", ...],
  "drawn_as":          ["<IEC60617 symbol_id>", ...],
  "related_iec_60364": ["<IEC clause>", ...],
  "divergence_notes":  "<single paragraph — required>",
  "related_bs_7671":   [],
  "usage_notes":       "<designer guidance>",
  "related_articles":  ["ART_<num>", ...]
}
```

See `docs/superpowers/specs/2026-05-15-nfpa70-standard-layer-design.md` for full field definitions.

---

## Coverage scope

**In scope:** All 9 Chapters of NEC 2023 — full coverage including Chapter 8 (communications).

**Out of scope:**
- NFPA 70E (workplace electrical safety)
- NFPA 72 (fire alarm beyond Article 760)
- NFPA 110/111 (standby/storage beyond Articles 700-706)
- State amendments (California Electrical Code, Massachusetts Electrical Code, etc.)
- UL equipment standards referenced by NEC
- Pre-1999 Class/Division-only legacy material
- NEC editions other than 2023
````

- [ ] **Step 3: Validate**

Run: `python3 -c "import json; json.load(open('shared/standards/electrical/NFPA70/meta.json'))" && echo OK`
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add shared/standards/electrical/NFPA70/meta.json shared/standards/electrical/NFPA70/README.md
git commit -m "feat: NFPA70 meta.json + rewrite README as layer index"
```

---

## Task 2: Create chapter1-general.json (Arts 90, 100, 110)

**Files:**
- Create: `shared/standards/electrical/NFPA70/chapter1-general.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "NFPA 70 Chapter 1 — General",
  "_chapter": 1,
  "_version": "1.0.0",
  "_note": "Arts 90 (Introduction), 100 (Definitions), 110 (Requirements for Electrical Installations). All small enough to live inline; no per-article files needed.",
  "articles": [
    {
      "article_id": "ART_90",
      "nec_ref": "NFPA 70:2023 Article 90",
      "chapter": 1,
      "article_number": 90,
      "article_title": "Introduction",
      "scope": "Defines the purpose, scope, arrangement and enforcement of the NEC. Sets out what the NEC covers (90.2(A)) and does not cover (90.2(B)). Establishes the AHJ (Authority Having Jurisdiction) as the enforcement authority.",
      "applies_to": ["all_installations", "scope_definition"],
      "key_sections": [
        {"section": "90.1", "title": "Purpose", "summary": "Practical safeguarding of persons and property from hazards arising from the use of electricity"},
        {"section": "90.2", "title": "Scope", "summary": "What NEC covers (and does NOT cover — utilities under their own jurisdiction, mining, ships, railway rolling stock, etc.)"},
        {"section": "90.3", "title": "Code Arrangement", "summary": "Chapters 1-4 apply generally; Chapters 5-7 supplement or modify; Chapter 8 stands alone; Chapter 9 informational"},
        {"section": "90.4", "title": "Enforcement", "summary": "AHJ has authority to interpret, grant special permission, waive specific requirements"},
        {"section": "90.5", "title": "Mandatory Rules, Permissive Rules, and Explanatory Material", "summary": "'shall' = mandatory; 'shall be permitted' = permissive; Informational Notes are not enforceable"}
      ],
      "tabulated_values": {},
      "tables_inline": {},
      "common_errors": [
        "Treating Informational Notes as enforceable — they are explanatory, not mandatory",
        "Assuming utility-owned equipment falls under NEC — Section 90.2(B)(5) excludes installations under exclusive utility control",
        "Forgetting that AHJ acceptance (90.4) is separate from NEC compliance — both are required"
      ],
      "drawn_as": [],
      "related_iec_60364": ["IEC 60364-1 Clause 11 (Scope and purpose)"],
      "divergence_notes": "NEC's AHJ concept has no direct IEC equivalent — IEC relies on national adoption and certification regimes. NEC 90.3 chapter-arrangement rule (Chapters 5-7 supplement Chapters 1-4) has no IEC analogue; IEC parts each carry independent scope.",
      "related_bs_7671": [],
      "usage_notes": "Read 90.2 first on any new project to confirm NEC applies. AHJ interpretations vary — document the AHJ name, the contact, and any project-specific waivers in the design narrative.",
      "related_articles": ["ART_100", "ART_110"]
    },
    {
      "article_id": "ART_100",
      "nec_ref": "NFPA 70:2023 Article 100",
      "chapter": 1,
      "article_number": 100,
      "article_title": "Definitions",
      "scope": "Defines terms used throughout the NEC. Definitions in Article 100 apply globally; definitions in Part II apply to circuits operating over 1000 V AC. Article-specific definitions in individual articles override Article 100 within those articles.",
      "applies_to": ["terminology", "all_installations"],
      "key_sections": [
        {"section": "100.I",  "title": "General",       "summary": "Definitions applicable to all NEC articles. Includes ampacity, branch circuit, feeder, service, grounded conductor, neutral conductor, equipment grounding conductor, etc."},
        {"section": "100.II", "title": "Over 1000 V AC, Nominal", "summary": "Definitions applicable only to circuits operating over 1000 V AC"}
      ],
      "tabulated_values": {},
      "tables_inline": {
        "key_definitions": {
          "title": "Critical NEC↔IEC terminology pairings (selected — full list in terminology.md)",
          "rows": [
            {"nec_term": "Ampacity",                       "definition": "Maximum current, in amperes, a conductor can carry continuously under conditions of use without exceeding its temperature rating", "iec_analogue": "Current-carrying capacity (Iz)"},
            {"nec_term": "Branch Circuit",                 "definition": "Circuit conductors between final OCPD and outlet(s)", "iec_analogue": "Final circuit"},
            {"nec_term": "Feeder",                         "definition": "Circuit conductors between service equipment and final branch-circuit OCPD", "iec_analogue": "Sub-main / distribution circuit"},
            {"nec_term": "Service",                        "definition": "Conductors and equipment connecting the utility supply to the wiring system", "iec_analogue": "Origin of installation / supply intake"},
            {"nec_term": "Grounded Conductor",             "definition": "System or circuit conductor intentionally grounded", "iec_analogue": "Neutral (N) in TN systems"},
            {"nec_term": "Neutral Conductor",              "definition": "Conductor connected to the neutral point of a system that is intended to carry current under normal conditions", "iec_analogue": "Neutral (N)"},
            {"nec_term": "Equipment Grounding Conductor (EGC)", "definition": "Conductive path(s) that provides a ground-fault current path and connects normally non-current-carrying metal parts of equipment together and to the system grounded conductor or to the GEC", "iec_analogue": "Circuit Protective Conductor (CPC)"},
            {"nec_term": "Grounding Electrode Conductor (GEC)", "definition": "Conductor used to connect the system grounded conductor or the equipment to a grounding electrode", "iec_analogue": "Main earthing conductor (no exact IEC term)"},
            {"nec_term": "Bonding Jumper, Main (MBJ)",     "definition": "Connection between the grounded service conductor and EGC at the service", "iec_analogue": "Main earthing terminal connection"},
            {"nec_term": "Working Space",                  "definition": "Clear space required in front of equipment likely to require examination, servicing, or maintenance while energized (110.26)", "iec_analogue": "Access and maintenance space (IEC 60364-7-729)"}
          ]
        }
      },
      "common_errors": [
        "Using NEC 'ground' interchangeably with IEC 'earth' in mixed-jurisdiction documents — confuses inspectors",
        "Mixing 'grounded conductor' (load-carrying neutral that happens to be grounded) with 'grounding electrode conductor' (carries fault current only)",
        "Treating service conductors as branch circuits — they are governed by Article 230 separately"
      ],
      "drawn_as": [],
      "related_iec_60364": ["IEC 60050 (International Electrotechnical Vocabulary)", "IEC 60364-1 Clause 3 (Definitions)"],
      "divergence_notes": "Major terminology divergence — see nec-vs-iec-comparison.md and terminology.md for the full catalogue. Most-cited: grounded conductor (NEC) ≠ neutral conductor (IEC), but NEC also uses both terms; EGC (NEC) ≈ CPC (IEC); ampacity (NEC) ≈ current-carrying capacity Iz (IEC); branch circuit (NEC) = final circuit (IEC).",
      "related_bs_7671": [],
      "usage_notes": "Every cross-jurisdiction project should include a one-page terminology key. Use NEC terms in NEC-jurisdiction documents and IEC terms in IEC-jurisdiction documents; do NOT mix.",
      "related_articles": ["ART_90", "ART_110", "ART_200", "ART_250"]
    },
    {
      "article_id": "ART_110",
      "nec_ref": "NFPA 70:2023 Article 110",
      "chapter": 1,
      "article_number": 110,
      "article_title": "Requirements for Electrical Installations",
      "scope": "General requirements for the examination and approval, installation and use, access to and spaces about electrical equipment.",
      "applies_to": ["all_installations", "workmanship", "working_clearances", "termination_temperature"],
      "key_sections": [
        {"section": "110.3",    "title": "Examination, Identification, Installation, Use, and Listing of Equipment", "summary": "Equipment must be evaluated, identified, listed where required, and installed in accordance with listing"},
        {"section": "110.10",   "title": "Circuit Impedance, Short-Circuit Current Ratings, and Other Characteristics", "summary": "OCPDs, conductors, and equipment must have short-circuit current ratings (SCCR) ≥ available fault current"},
        {"section": "110.12",   "title": "Mechanical Execution of Work", "summary": "Workmanship — neat and workmanlike installation"},
        {"section": "110.14(C)","title": "Temperature Limitations (the '60/75/90 °C rule')", "summary": "Conductor ampacity limited to the lowest temperature rating of any connected terminal — typically 60 °C or 75 °C even when conductor is 90 °C rated"},
        {"section": "110.26",   "title": "Spaces About Electrical Equipment", "summary": "Working clearances — depth (Table 110.26(A)(1)) × width (30 in min or width of equipment) × headroom (6.5 ft min) for equipment likely to be examined energised"},
        {"section": "110.34",   "title": "Working Space and Guarding (Over 1000 V)", "summary": "Increased working clearances for HV equipment"}
      ],
      "tabulated_values": {
        "working_space_depth_110_26_A_1": "see tables_inline"
      },
      "tables_inline": {
        "Table_110.26(A)(1)": {
          "title": "Working Space Depth — to Live Parts (≤ 1000 V Nominal)",
          "rows": [
            {"nominal_voltage_to_ground": "0-150 V",     "condition_1_in": 36, "condition_2_in": 36, "condition_3_in": 36},
            {"nominal_voltage_to_ground": "151-600 V",   "condition_1_in": 36, "condition_2_in": 42, "condition_3_in": 48},
            {"nominal_voltage_to_ground": "601-1000 V",  "condition_1_in": 36, "condition_2_in": 48, "condition_3_in": 60}
          ],
          "_conditions": "Condition 1: exposed live parts on one side only, no live or grounded parts on the other. Condition 2: exposed live parts on one side, grounded parts on the other. Condition 3: exposed live parts on both sides."
        }
      },
      "common_errors": [
        "Ignoring 110.14(C) — using 90 °C ampacity column when terminals are 60 °C or 75 °C rated; ampacity must be limited to the lower",
        "Specifying inadequate working clearance — Table 110.26(A)(1) is by voltage AND condition AND nominal voltage to ground (not phase-to-phase)",
        "Forgetting 110.10 SCCR coordination — equipment marked 5 kA SCCR in a 22 kA available fault location is non-compliant",
        "Confusing working space (110.26) with dedicated electrical space (110.26(E)) — both are required and have different criteria"
      ],
      "drawn_as": [],
      "related_iec_60364": ["IEC 60364-1 Clause 13 (Selection of equipment)", "IEC 60364-1 Clause 132 (Compatibility)", "IEC 60364-7-729 (Access to electrical installations and equipment)"],
      "divergence_notes": "NEC's 110.14(C) 60/75/90 °C termination rule is much more prescriptive than IEC's tabulated ratings — IEC ampacity tables (Annex B) generally assume terminations rated at the same temperature as the conductor. NEC 110.26 working space requirements are stated in feet/inches and structured by voltage-to-ground × condition; IEC 60364-7-729 uses metric and is generally less prescriptive. NEC has explicit SCCR coordination (110.10); IEC handles via Icc/Icu separately per device.",
      "related_bs_7671": [],
      "usage_notes": "110.14(C) is the most common cause of failed inspections for first-time NEC designers. Always state the termination temperature rating on the schedule (60 °C, 75 °C, 90 °C) and confirm the conductor ampacity column matches.",
      "related_articles": ["ART_240", "ART_250", "ART_310", "ART_408"]
    }
  ]
}
```

- [ ] **Step 2: Validate**

Run: `python3 -c "import json; json.load(open('shared/standards/electrical/NFPA70/chapter1-general.json'))" && echo OK`
Expected: `OK`

- [ ] **Step 3: Verify schema fields on all articles**

Run:
```bash
python3 - <<'PY'
import json
req=['article_id','nec_ref','chapter','article_number','article_title','scope','applies_to','key_sections','tabulated_values','tables_inline','common_errors','drawn_as','related_iec_60364','divergence_notes','related_bs_7671','usage_notes','related_articles']
data = json.load(open('shared/standards/electrical/NFPA70/chapter1-general.json'))
missing = [(a.get('article_id','?'), [f for f in req if f not in a]) for a in data['articles'] if any(f not in a for f in req)]
print('OK' if not missing else 'MISSING:'+str(missing))
PY
```
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add shared/standards/electrical/NFPA70/chapter1-general.json
git commit -m "feat: NFPA70 chapter1-general.json — Arts 90, 100, 110 (definitions and general reqs)"
```

---

## Task 3: Create chapter2-wiring-protection.json (Arts 200, 285 + pointers)

**Files:**
- Create: `shared/standards/electrical/NFPA70/chapter2-wiring-protection.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "NFPA 70 Chapter 2 — Wiring and Protection",
  "_chapter": 2,
  "_version": "1.0.0",
  "_note": "Heaviest chapter. Arts 200 (grounded conductor identification) and 285 (SPDs) inline. Arts 210, 215, 220, 230, 240, 250 have dedicated per-article files — only pointer entries here.",
  "articles": [
    {
      "article_id": "ART_200",
      "nec_ref": "NFPA 70:2023 Article 200",
      "chapter": 2,
      "article_number": 200,
      "article_title": "Use and Identification of Grounded Conductors",
      "scope": "Use and identification of the grounded conductor — colour coding, terminal identification, polarity at switching/protective devices.",
      "applies_to": ["grounded_conductor", "identification", "premise_wiring"],
      "key_sections": [
        {"section": "200.6", "title": "Means of Identifying Grounded Conductors", "summary": "≤6 AWG: continuous white or gray insulation, or three white stripes. >6 AWG: white at terminations only OR colour distinct + white tape/marking at every termination"},
        {"section": "200.7", "title": "Use of Insulation that is White or Gray or has Three Continuous White Stripes", "summary": "White/gray/striped insulation reserved for grounded conductor — exceptions for reidentification in cable assemblies, dimmer-controlled circuits, etc."}
      ],
      "tabulated_values": {},
      "tables_inline": {},
      "common_errors": [
        "Using white tape on a black conductor as the only identification on a high-voltage feeder — for >6 AWG only the entire termination must be re-identified; on circuits ≤6 AWG, white insulation is required (not tape)",
        "Reusing a white conductor as a hot leg in a 240 V two-wire circuit without re-identification per 200.7"
      ],
      "drawn_as": ["CONDUCTOR_NEUTRAL"],
      "related_iec_60364": ["IEC 60364-5-52 Clause 514.3 (Identification of conductors)"],
      "divergence_notes": "NEC requires white or gray for grounded conductor (200.6); IEC uses blue (BS EN 60446 / IEC 60446) for the neutral. NEC permits orange to identify the high-leg in 4-wire delta systems; IEC has no equivalent (delta neutral systems are rare in IEC jurisdictions).",
      "related_bs_7671": [],
      "usage_notes": "On US/IEC bi-jurisdiction projects, document the colour code in the design narrative — defaulting to either standard alone causes confusion at site.",
      "related_articles": ["ART_250", "ART_310"]
    },
    {
      "article_id": "ART_285",
      "nec_ref": "NFPA 70:2023 Article 242",
      "chapter": 2,
      "article_number": 242,
      "article_title": "Overvoltage Protection (formerly Art 285 SPDs, reorganised in 2020 to Art 242)",
      "scope": "Surge protective devices (SPDs) — selection, location, application, marking. SPD types and classes per UL 1449. NOTE: Article number 285 used in NEC 2017; reorganised to 242 in NEC 2020 onwards. References to 'Art 285' in older documents map to 'Art 242' under NEC 2023.",
      "applies_to": ["spd", "surge_protection", "transient_overvoltage"],
      "key_sections": [
        {"section": "242.6",   "title": "Listing", "summary": "SPDs must be listed to UL 1449"},
        {"section": "242.14",  "title": "Number Required", "summary": "Where required by AHJ or design — typically Type 1 or 2 at service entrance, Type 3 at sensitive equipment"},
        {"section": "242.16",  "title": "Location", "summary": "Type 1 ahead of service disconnect; Type 2 on load side of service; Type 3 within 30 ft of protected equipment"},
        {"section": "242.22",  "title": "Type 1, 2, 3, 4 SPDs", "summary": "Type 1 = supply-side of service disconnect; Type 2 = load-side; Type 3 = point-of-use; Type 4 = component SPDs"}
      ],
      "tabulated_values": {},
      "tables_inline": {},
      "common_errors": [
        "Installing a Type 2 SPD on the supply side of the service disconnect — only Type 1 permitted there",
        "Failing to coordinate Type 2 (8/20 µs nominal discharge) with upstream Type 1 (10/350 µs lightning impulse) — see ocpd-coordination.json for the let-through-voltage coordination",
        "Using Article 285 in design references with NEC 2020+ — the article was renumbered to 242"
      ],
      "drawn_as": ["SPD_TYPE1", "SPD_TYPE2", "SPD_TYPE3"],
      "related_iec_60364": ["IEC 60364-4-44 Clause 443 (Surge protection)"],
      "divergence_notes": "NEC SPD types (1, 2, 3, 4 per UL 1449) correspond loosely to IEC SPD types (Type 1 / 2 / 3 per IEC 61643-11) but the test waveforms differ — UL 1449 short-circuit current test vs IEC 8/20 µs and 10/350 µs impulses. NEC does not yet mandate SPDs universally (AHJ-dependent); IEC 60364-4-44 AMD2:2018 made SPDs effectively mandatory at the main DB in all new installations unless a risk analysis justifies omission.",
      "related_bs_7671": [],
      "usage_notes": "Cite Art 242 (NEC 2023) in new design documents; legacy 'Art 285' references in client/utility specs map to Art 242. Always coordinate Type 1 + Type 2 let-through voltages so Type 2 protects the panelboard's downstream equipment.",
      "related_articles": ["ART_230", "ART_240", "ART_250"]
    },
    {
      "article_number": 210,
      "article_title": "Branch Circuits",
      "scope": "Branch-circuit ratings, GFCI/AFCI requirements, receptacle outlet rules.",
      "full_content": "art210-branch-circuits.json"
    },
    {
      "article_number": 215,
      "article_title": "Feeders",
      "scope": "Feeder load, ampacity, GFP for feeders ≥1000 A.",
      "full_content": "art215-feeders.json"
    },
    {
      "article_number": 220,
      "article_title": "Branch-Circuit, Feeder, and Service Load Calculations",
      "scope": "Standard and Optional load calculation methods (220.40, 220.82).",
      "full_content": "art220-load-calculations.json"
    },
    {
      "article_number": 230,
      "article_title": "Services",
      "scope": "Service drop/lateral, service conductor ampacity, disconnect, GFP at services.",
      "full_content": "art230-services.json"
    },
    {
      "article_number": 240,
      "article_title": "Overcurrent Protection",
      "scope": "OCPD types, interrupting rating, conductor protection, tap rules, series ratings.",
      "full_content": "art240-overcurrent.json"
    },
    {
      "article_number": 250,
      "article_title": "Grounding and Bonding",
      "scope": "System and equipment grounding, grounding electrode system, GEC/EGC sizing, bonding.",
      "full_content": "art250-grounding-bonding.json"
    }
  ]
}
```

- [ ] **Step 2: Validate**

Run: `python3 -c "import json; json.load(open('shared/standards/electrical/NFPA70/chapter2-wiring-protection.json'))" && echo OK`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add shared/standards/electrical/NFPA70/chapter2-wiring-protection.json
git commit -m "feat: NFPA70 chapter2-wiring-protection.json — Arts 200, 242 inline + pointers"
```

---

## Task 4: Create chapter3-wiring-methods.json (Art 300 + raceways/cables, Art 310 pointer)

**Files:**
- Create: `shared/standards/electrical/NFPA70/chapter3-wiring-methods.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "NFPA 70 Chapter 3 — Wiring Methods and Materials",
  "_chapter": 3,
  "_version": "1.0.0",
  "_note": "Wiring methods (raceways, cables, boxes). Art 310 (conductor ampacity) has dedicated file; raceway/cable type articles consolidated here.",
  "articles": [
    {
      "article_id": "ART_300",
      "nec_ref": "NFPA 70:2023 Article 300",
      "chapter": 3,
      "article_number": 300,
      "article_title": "General Requirements for Wiring Methods and Materials",
      "scope": "General requirements for all wiring methods covered in Chapter 3 — conductor support, protection from physical damage, conductors in same raceway, securing, bushings, raceways exposed to weather.",
      "applies_to": ["all_wiring_methods", "raceways", "cables"],
      "key_sections": [
        {"section": "300.3",  "title": "Conductors", "summary": "Single conductors must be installed within recognized wiring methods; conductors of same circuit must be grouped in same raceway/cable"},
        {"section": "300.4",  "title": "Protection Against Physical Damage", "summary": "Bored holes ≥1¼ in from wood face; nail plates where <1¼ in; conduit/cable protection in metal-stud framing"},
        {"section": "300.5",  "title": "Underground Installations", "summary": "Min cover depths per Table 300.5; warning ribbon; separation from non-electrical underground structures"},
        {"section": "300.11", "title": "Securing and Supporting", "summary": "Raceways and cables securely fastened — typical spacings in respective raceway/cable articles"},
        {"section": "300.13(B)","title": "Continuity at Splices and Terminations", "summary": "Grounded (neutral) conductor of a multiwire branch circuit shall not depend on device connections for continuity"},
        {"section": "300.21", "title": "Spread of Fire or Products of Combustion", "summary": "Fire-stopping at floor/wall penetrations to maintain fire-resistance rating"}
      ],
      "tabulated_values": {
        "underground_cover_300_5": "see tables_inline"
      },
      "tables_inline": {
        "Table_300.5_Minimum_Cover_Direct_Bury": {
          "title": "Minimum Cover Requirements for Direct-Buried Cables and Raceways (typical residential rows)",
          "rows": [
            {"location": "All locations not specified below",                          "direct_bury_in": 24, "rmc_imc_in": 6,  "nonmetallic_raceway_in": 18},
            {"location": "In trench below 2-in concrete or equivalent",                "direct_bury_in": 18, "rmc_imc_in": 6,  "nonmetallic_raceway_in": 12},
            {"location": "Under residential driveway",                                 "direct_bury_in": 18, "rmc_imc_in": 18, "nonmetallic_raceway_in": 18},
            {"location": "In or under building",                                       "direct_bury_in": "n/a", "rmc_imc_in": 0, "nonmetallic_raceway_in": "in raceway"}
          ]
        }
      },
      "common_errors": [
        "Routing line and neutral of the same circuit in separate raceways — induces heating and impedance imbalance, prohibited by 300.3(B) except specific permitted cases",
        "Bored holes too close to wood face — 300.4(A)(1) requires ≥1¼ in; missing the rule is a common framing rough-in violation",
        "Underground cover below the 300.5 minimum — most often on residential service laterals where contractors aim for ease over compliance"
      ],
      "drawn_as": ["CONDUIT", "CABLE_TRAY", "CABLE_DUCT", "CONDUCTOR_UNDERGROUND"],
      "related_iec_60364": ["IEC 60364-5-52 (Wiring systems)", "IEC 60364-5-52 Clause 521 (Types of wiring systems)"],
      "divergence_notes": "NEC 300.3(B) prohibition of single-conductor circuits in separate raceways is much more explicit than IEC 60364-5-52. NEC underground cover (Table 300.5) is in inches by location class; IEC 60364-5-52 specifies metric burial depths generically with national-adoption variation. NEC firestop requirement (300.21) is performance-based; IEC defers to local building code.",
      "related_bs_7671": [],
      "usage_notes": "Always check Table 300.5 first on outdoor projects — burial depth is by raceway type AND location class.",
      "related_articles": ["ART_310", "ART_312", "ART_314", "ART_250"]
    },
    {
      "article_id": "ART_310",
      "nec_ref": "NFPA 70:2023 Article 310 (pointer)",
      "chapter": 3,
      "article_number": 310,
      "article_title": "Conductors for General Wiring",
      "scope": "Conductor materials, insulation, ampacity tables (310.16, 310.17), correction factors (ambient, grouping), termination temperature limits. The heaviest article in Chapter 3.",
      "applies_to": ["pointer"],
      "key_sections": [],
      "tabulated_values": {},
      "tables_inline": {},
      "common_errors": [],
      "drawn_as": [],
      "related_iec_60364": [],
      "divergence_notes": "See art310-conductor-ampacity.json for full content.",
      "related_bs_7671": [],
      "usage_notes": "Full content lives in art310-conductor-ampacity.json — load that file when ampacity / correction-factor data is needed.",
      "related_articles": [],
      "full_content": "art310-conductor-ampacity.json"
    },
    {
      "article_id": "ART_312_314",
      "nec_ref": "NFPA 70:2023 Articles 312 (Cabinets) + 314 (Boxes)",
      "chapter": 3,
      "article_number": 314,
      "article_title": "Outlet, Device, Pull, and Junction Boxes; Conduit Bodies",
      "scope": "Box sizing (314.16 fill calculation), pull box sizing (314.28), conduit body dimensions, cabinet/cutout box installation (Art 312). Bundled here because Art 312 and 314 are short and tightly related.",
      "applies_to": ["boxes", "cabinets", "fill_calculation", "pull_box_sizing"],
      "key_sections": [
        {"section": "312.5",   "title": "Cabinets, Cutout Boxes — Conductors Entering", "summary": "Cable assemblies and conduits must be securely fastened to the cabinet/cutout box; insulating bushings on metal raceway >4 AWG"},
        {"section": "314.16",  "title": "Number of Conductors in Outlet, Device, and Junction Boxes", "summary": "Box fill calculation — count conductors entering box + device fill + clamp fill + support fitting fill + grounding-conductor fill; sum × volume allowance per conductor size must be ≤ box's listed volume"},
        {"section": "314.28",  "title": "Pull and Junction Boxes — Straight and Angle/U Pulls", "summary": "Straight pull: 8 × largest raceway trade size. Angle/U pull: 6 × largest raceway + sum of other raceways entering same wall."}
      ],
      "tabulated_values": {
        "box_volume_per_conductor_314_16_B": "see tables_inline"
      },
      "tables_inline": {
        "Table_314.16(B)_Box_Volume_Allowance_per_Conductor": {
          "title": "Volume Allowance Required per Conductor (Free Space)",
          "rows": [
            {"conductor_size_awg": 18, "volume_in3": 1.50},
            {"conductor_size_awg": 16, "volume_in3": 1.75},
            {"conductor_size_awg": 14, "volume_in3": 2.00},
            {"conductor_size_awg": 12, "volume_in3": 2.25},
            {"conductor_size_awg": 10, "volume_in3": 2.50},
            {"conductor_size_awg": 8,  "volume_in3": 3.00},
            {"conductor_size_awg": 6,  "volume_in3": 5.00}
          ]
        }
      },
      "common_errors": [
        "Forgetting the device fill (each yoke = 2 × volume allowance for largest conductor connected to that device) when computing 314.16",
        "Forgetting the clamp/support fill (1 × volume allowance for largest conductor) when boxes have internal clamps",
        "Pull-box sizing failing 314.28 — 8× rule for straight pulls is per the LARGEST raceway, not the average"
      ],
      "drawn_as": ["JUNCTION_BOX"],
      "related_iec_60364": ["IEC 60670 (Boxes and enclosures for electrical accessories)"],
      "divergence_notes": "NEC fill calc is volumetric (in³ per conductor); IEC fill is by % cross-section (similar to NEC raceway fill in Chapter 9 Table 1 but applied to boxes). NEC 314.28 pull-box sizing has no IEC equivalent — IEC defers to manufacturer sizing.",
      "related_bs_7671": [],
      "usage_notes": "Box fill (314.16) is a frequent inspection failure. Use a fill calculator and always carry the count on the schedule.",
      "related_articles": ["ART_300", "ART_310", "ART_408"]
    },
    {
      "article_id": "ART_320_399_raceways_cables",
      "nec_ref": "NFPA 70:2023 Articles 320-399 (Raceway and Cable Types)",
      "chapter": 3,
      "article_number": 320,
      "article_title": "Raceway and Cable Type Bundle (320 AC, 330 MC, 332 MI, 334 NM, 342 IMC, 344 RMC, 348 FMC, 350 LFMC, 352 PVC, 356 LFNC, 358 EMT)",
      "scope": "All recognized raceway and cable types. Each has its own Article in NEC; this bundle entry summarises the most-used types for MEP design. The decision matrix lives in wiring-methods-by-occupancy.json.",
      "applies_to": ["raceway_types", "cable_types", "method_selection"],
      "key_sections": [
        {"section": "320", "title": "Armored Cable (AC)", "summary": "Metal-clad cable with flexible metal armor; bonded grounding strip required for EGC continuity"},
        {"section": "330", "title": "Metal-Clad Cable (MC)", "summary": "Smooth or corrugated tube; separate EGC inside the cable assembly"},
        {"section": "332", "title": "Mineral-Insulated, Metal-Sheathed Cable (MI)", "summary": "Magnesium oxide insulation, copper sheath; fire-rated; used for emergency circuits"},
        {"section": "334", "title": "Nonmetallic-Sheathed Cable (NM)", "summary": "Common residential cable (Romex); restricted to dwellings and limited commercial under specific conditions"},
        {"section": "342", "title": "Intermediate Metal Conduit (IMC)", "summary": "Galvanized steel, threaded; permitted in all atmospheric conditions"},
        {"section": "344", "title": "Rigid Metal Conduit (RMC)", "summary": "Heaviest steel raceway; permitted everywhere"},
        {"section": "348", "title": "Flexible Metal Conduit (FMC)", "summary": "Continuous helical metal strip; used for short runs to vibrating equipment; bonding rules per 250.118"},
        {"section": "350", "title": "Liquidtight Flexible Metal Conduit (LFMC)", "summary": "FMC with PVC sheath; outdoor / wet locations"},
        {"section": "352", "title": "Rigid Polyvinyl Chloride Conduit (PVC)", "summary": "Schedule 40/80; underground common"},
        {"section": "356", "title": "Liquidtight Flexible Nonmetallic Conduit (LFNC)", "summary": "Nonmetallic equivalent of LFMC; chemical-resistant"},
        {"section": "358", "title": "Electrical Metallic Tubing (EMT)", "summary": "Thin-wall steel; not threaded; setscrew/compression fittings; not permitted underground or in certain hazardous locations"}
      ],
      "tabulated_values": {},
      "tables_inline": {},
      "common_errors": [
        "Using NM cable in commercial occupancies other than those explicitly permitted by 334.10 — very restricted",
        "Using EMT underground — prohibited by 358.10(C) except specific cases",
        "Using FMC as the EGC on circuits over the length/size limits of 250.118(5) — must run a separate EGC"
      ],
      "drawn_as": ["CONDUIT", "CABLE_DUCT", "CABLE_TRAY"],
      "related_iec_60364": ["IEC 60364-5-52 Tables of installation methods (Table A.52.3)"],
      "divergence_notes": "NEC has separate articles per raceway/cable type (320-399 series); IEC consolidates into installation methods (A1/A2/B1/B2/C/D/E/F) in Annex A of 60364-5-52. NEC's NM cable (Romex) has no IEC equivalent in common use — IEC typically uses singles in conduit/trunking or armoured multicore.",
      "related_bs_7671": [],
      "usage_notes": "See wiring-methods-by-occupancy.json for the decision matrix — which raceway/cable types are permitted in which occupancies.",
      "related_articles": ["ART_300", "ART_310", "ART_250"]
    }
  ]
}
```

- [ ] **Step 2: Validate**

Run: `python3 -c "import json; json.load(open('shared/standards/electrical/NFPA70/chapter3-wiring-methods.json'))" && echo OK`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add shared/standards/electrical/NFPA70/chapter3-wiring-methods.json
git commit -m "feat: NFPA70 chapter3-wiring-methods.json — Arts 300, 312/314, 320-399 bundle"
```

---

## Task 5: Create chapter4-equipment.json (light Ch 4 articles, pointers to 408/430/450)

**Files:**
- Create: `shared/standards/electrical/NFPA70/chapter4-equipment.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "NFPA 70 Chapter 4 — Equipment for General Use",
  "_chapter": 4,
  "_version": "1.0.0",
  "_note": "Light Ch 4 articles inline. Arts 408 (panelboards), 430 (motors), 450 (transformers) have dedicated per-article files — pointers only.",
  "articles": [
    {
      "article_id": "ART_400",
      "nec_ref": "NFPA 70:2023 Article 400",
      "chapter": 4,
      "article_number": 400,
      "article_title": "Flexible Cords and Flexible Cables",
      "scope": "Flexible cord types (Table 400.4), uses permitted (400.10), uses NOT permitted (400.12 — common violation source).",
      "applies_to": ["flexible_cords", "portable_equipment", "pendant_drops"],
      "key_sections": [
        {"section": "400.10", "title": "Uses Permitted", "summary": "Pendants, fixtures, portable equipment, elevator cables, hoist/crane, prevention of transmission of noise/vibration, removable equipment, identified appliances"},
        {"section": "400.12", "title": "Uses Not Permitted", "summary": "Substitute for fixed wiring, run through walls/floors/ceilings/doors, attached to building surfaces, concealed, in raceways (with limited exceptions)"}
      ],
      "tabulated_values": {},
      "tables_inline": {},
      "common_errors": ["Using SO/SJOOW flexible cord as fixed wiring — prohibited by 400.12(1) and frequent inspection failure"],
      "drawn_as": [],
      "related_iec_60364": ["IEC 60364-5-52 Clause 521.9 (Flexible cables)"],
      "divergence_notes": "NEC restricts flexible cord use much more tightly than IEC; IEC permits flexible cables in fixed wiring with conditions.",
      "related_bs_7671": [],
      "usage_notes": "Read 400.12 first. If the application doesn't match 400.10 exactly, it's prohibited.",
      "related_articles": ["ART_410", "ART_422"]
    },
    {
      "article_id": "ART_404",
      "nec_ref": "NFPA 70:2023 Article 404",
      "chapter": 4,
      "article_number": 404,
      "article_title": "Switches",
      "scope": "Snap switches, dimmers, transfer switches (≤1000 V) — installation, position, ratings, identification.",
      "applies_to": ["switches", "dimmers", "transfer_switches"],
      "key_sections": [
        {"section": "404.2(C)", "title": "Switches Controlling Lighting Loads", "summary": "Grounded conductor (neutral) required at switch box for control devices needing one (most occupancy sensors, dimmers); exceptions for switch loops in existing dwellings"},
        {"section": "404.9",   "title": "Provisions for General-Use Snap Switches", "summary": "Switches mounted in metal boxes must be effectively grounded"},
        {"section": "404.14",  "title": "Rating and Use of Snap Switches", "summary": "Switch ratings — AC general-use (40A 277V), AC-DC general-use, motor circuit (Type V), heater"}
      ],
      "tabulated_values": {},
      "tables_inline": {},
      "common_errors": ["Routing a switch loop without the neutral conductor in new construction — 404.2(C) requires neutral at virtually every switch box"],
      "drawn_as": ["SWITCH_1WAY", "SWITCH_2WAY", "DIMMER_SWITCH"],
      "related_iec_60364": ["IEC 60364-5-53 (Switchgear and controlgear)"],
      "divergence_notes": "NEC 404.2(C) neutral-at-switch-box rule (added in 2011) has no IEC equivalent; IEC does not require neutral at every switch.",
      "related_bs_7671": [],
      "usage_notes": "Specify neutral at every switch box on new-construction drawings unless one of the four exceptions in 404.2(C) clearly applies.",
      "related_articles": ["ART_406", "ART_410"]
    },
    {
      "article_id": "ART_406",
      "nec_ref": "NFPA 70:2023 Article 406",
      "chapter": 4,
      "article_number": 406,
      "article_title": "Receptacles, Cord Connectors, and Attachment Plugs",
      "scope": "Receptacle ratings, types (15A/20A/30A/50A configurations per NEMA WD-6), GFCI/AFCI compliance via the receptacle, tamper-resistant (TR) requirements (406.12), weather-resistant (WR) (406.9), countertop placement.",
      "applies_to": ["receptacles", "outlets", "tamper_resistance", "weather_resistance"],
      "key_sections": [
        {"section": "406.4",  "title": "General Installation Requirements", "summary": "Mounting, ratings, identification"},
        {"section": "406.9",  "title": "Receptacles in Damp or Wet Locations", "summary": "Damp = listed for damp/wet; wet = listed for wet + cover that maintains weatherproof when plug inserted (in-use cover)"},
        {"section": "406.12", "title": "Tamper-Resistant Receptacles (TR)", "summary": "All 125 V and 250 V, 15A/20A receptacles in dwelling units, child care, preschool, classroom, waiting rooms, hotels, dormitories MUST be tamper-resistant"}
      ],
      "tabulated_values": {},
      "tables_inline": {},
      "common_errors": ["Specifying standard (non-TR) receptacles in dwelling units — 406.12 requires TR in every receptacle outlet"],
      "drawn_as": ["SOCKET_OUTLET_DUPLEX", "SOCKET_OUTLET_GFCI"],
      "related_iec_60364": ["IEC 60364-5-53 Clause 553 (Plugs and socket-outlets)"],
      "divergence_notes": "NEC TR receptacle requirement (406.12) has no IEC equivalent; IEC relies on socket-design standards (BS 1363 shutters, Schuko safety, etc.) and does not have a separate 'tamper-resistant' classification.",
      "related_bs_7671": [],
      "usage_notes": "Default to TR on all dwelling-unit outlets; default to WR + in-use cover for any outdoor receptacle.",
      "related_articles": ["ART_210", "ART_404", "ART_680"]
    },
    {
      "article_id": "ART_410",
      "nec_ref": "NFPA 70:2023 Article 410",
      "chapter": 4,
      "article_number": 410,
      "article_title": "Luminaires, Lampholders, and Lamps",
      "scope": "Luminaire installation — locations (wet/damp), in clothes closets (410.16), above bathtubs (410.10(D)), recessed (410.110-130), poles (410.30).",
      "applies_to": ["luminaires", "clothes_closets", "bathtub_zones", "recessed_fixtures", "lighting_poles"],
      "key_sections": [
        {"section": "410.10(D)","title": "Luminaires in Bathtub and Shower Areas", "summary": "No luminaire within 3 ft horizontal and 8 ft vertical of bathtub rim/shower stall threshold unless wet-listed"},
        {"section": "410.16",   "title": "Luminaires in Clothes Closets", "summary": "Permitted types/locations — surface fluorescent/LED on wall or ceiling outside storage volume OK; incandescent prohibited within storage zone"},
        {"section": "410.110+", "title": "Recessed Luminaires (Part XII)", "summary": "Type IC for direct contact with insulation; Type non-IC requires 3-in clearance from insulation; thermal protection per UL 1598"}
      ],
      "tabulated_values": {},
      "tables_inline": {},
      "common_errors": ["Specifying non-IC recessed luminaires in insulated ceiling — fire hazard; use IC-rated for direct contact"],
      "drawn_as": ["LUMINAIRE_CEILING", "LUMINAIRE_RECESSED", "LUMINAIRE_WALL"],
      "related_iec_60364": ["IEC 60364-7-701 (Bath and shower locations)"],
      "divergence_notes": "NEC bathtub zone (3 ft × 8 ft per 410.10(D)) differs from IEC 60364-7-701 zones (Zone 0, 1, 2 with specific dimensions and IP requirements). NEC has no explicit IPX rating in the bath zone — relies on 'damp' / 'wet' listing.",
      "related_bs_7671": [],
      "usage_notes": "On bath/shower designs, default to wet-listed luminaires in the 3-ft × 8-ft envelope.",
      "related_articles": ["ART_404", "ART_680"]
    },
    {
      "article_id": "ART_422",
      "nec_ref": "NFPA 70:2023 Article 422",
      "chapter": 4,
      "article_number": 422,
      "article_title": "Appliances",
      "scope": "Fastened-in-place and cord-connected appliances — branch-circuit sizing (422.10), disconnect (422.30+), GFCI for specific appliances (422.5: vending machines, drinking fountains, dishwashers, etc.).",
      "applies_to": ["appliances", "branch_circuit_sizing", "disconnect"],
      "key_sections": [
        {"section": "422.5",  "title": "GFCI Protection for Personnel", "summary": "Listed appliances requiring GFCI (per their listing) — vending machines, drinking fountains, dishwashers, etc."},
        {"section": "422.10", "title": "Branch-Circuit Rating", "summary": "Individual branch circuit ≥ 125% of nameplate for continuous-duty appliance; ≥ 100% for non-continuous"},
        {"section": "422.30", "title": "Disconnecting Means — General", "summary": "Each appliance must have a disconnect"}
      ],
      "tabulated_values": {},
      "tables_inline": {},
      "common_errors": ["Sizing appliance circuit at 100% of nameplate when appliance is continuous-duty — must be 125% per 422.10(A)(1)"],
      "drawn_as": [],
      "related_iec_60364": ["IEC 60364-5-55 (Other equipment)"],
      "divergence_notes": "NEC 125% continuous-duty multiplier is explicit and prescriptive; IEC handles via cable derating + circuit-rated-In selection.",
      "related_bs_7671": [],
      "usage_notes": "Always confirm continuous-duty vs non-continuous before sizing the branch circuit.",
      "related_articles": ["ART_210", "ART_440"]
    },
    {
      "article_id": "ART_440",
      "nec_ref": "NFPA 70:2023 Article 440",
      "chapter": 4,
      "article_number": 440,
      "article_title": "Air-Conditioning and Refrigerating Equipment",
      "scope": "Hermetic refrigerant motor-compressor branch circuits — rated-load current (RLA), short-circuit ground-fault protection, conductor sizing (440.32-33), disconnect within sight (440.14).",
      "applies_to": ["ac_equipment", "refrigeration", "compressors"],
      "key_sections": [
        {"section": "440.14", "title": "Location of Disconnect", "summary": "Disconnect within sight from and readily accessible to the AC equipment"},
        {"section": "440.22", "title": "Application and Selection of Short-Circuit Ground-Fault Protection", "summary": "OCPD selection — up to 175% of RLA + branch-circuit selection current (BCSC); 225% if 175% trips on start"},
        {"section": "440.32", "title": "Single Motor-Compressor", "summary": "Conductor ampacity ≥ 125% of RLA or branch-circuit selection current (whichever is greater)"}
      ],
      "tabulated_values": {},
      "tables_inline": {},
      "common_errors": ["Using full-load amps (FLA) from a generic motor table for a hermetic compressor — Art 440 requires RLA from the equipment nameplate"],
      "drawn_as": ["AC_OUTDOOR_UNIT"],
      "related_iec_60364": ["IEC 60364-5-55 Clause 559 (Luminaires and lighting installations) — peripheral relevance only"],
      "divergence_notes": "Art 440 is NEC-specific: the 'hermetic refrigerant motor-compressor' construct and the RLA/BCSC dual-rating system have no IEC equivalent; IEC sizes via standard motor-circuit rules (similar to NEC Art 430).",
      "related_bs_7671": [],
      "usage_notes": "Always size from nameplate RLA, not generic FLA. Confirm disconnect is within sight (most common AC inspection failure).",
      "related_articles": ["ART_430", "ART_210"]
    },
    {
      "article_id": "ART_480",
      "nec_ref": "NFPA 70:2023 Article 480",
      "chapter": 4,
      "article_number": 480,
      "article_title": "Stationary Standby Batteries",
      "scope": "Storage batteries (lead-acid, alkaline, lithium-ion) for stationary applications — battery rooms, ventilation, disconnect, charging.",
      "applies_to": ["batteries", "ups_batteries", "ess_subset"],
      "key_sections": [
        {"section": "480.6", "title": "Battery Locations", "summary": "Ventilation per 480.10, working space, racks, spill containment for flooded lead-acid"},
        {"section": "480.7", "title": "Direct-Current Disconnect", "summary": "DC disconnect required; lockable in OFF position"}
      ],
      "tabulated_values": {},
      "tables_inline": {},
      "common_errors": ["Treating Art 480 as the only battery rule for ESS — for ESS systems ≥1 kWh, Art 706 (Energy Storage Systems) applies in addition"],
      "drawn_as": ["BATTERY", "UPS"],
      "related_iec_60364": ["IEC 60364-5-55 (Other equipment)", "IEC 62485-2 (Battery safety)"],
      "divergence_notes": "Art 480 covers stationary lead-acid + alkaline + Li-ion; Art 706 (Energy Storage Systems) layered on top for ESS. IEC handles via IEC 62485-2 (separate standard) referenced from IEC 60364.",
      "related_bs_7671": [],
      "usage_notes": "For ESS designs, read 480 + 706 together. UPS systems generally fall under 480 alone.",
      "related_articles": ["ART_700", "ART_701", "ART_702"]
    },
    {
      "article_number": 408,
      "article_title": "Switchboards, Switchgear, and Panelboards",
      "scope": "Panelboard ratings, classification, 42-circuit rule, spacings, working clearances.",
      "full_content": "art408-panelboards.json"
    },
    {
      "article_number": 430,
      "article_title": "Motors, Motor Circuits, and Controllers",
      "scope": "Motor circuit conductor sizing, OCPD, overload, disconnect, MCC.",
      "full_content": "art430-motors.json"
    },
    {
      "article_number": 450,
      "article_title": "Transformers and Transformer Vaults",
      "scope": "Transformer overcurrent protection, primary/secondary, vault, ventilation.",
      "full_content": "art450-transformers.json"
    }
  ]
}
```

- [ ] **Step 2: Validate and commit**

Run: `python3 -c "import json; json.load(open('shared/standards/electrical/NFPA70/chapter4-equipment.json'))" && echo OK`

```bash
git add shared/standards/electrical/NFPA70/chapter4-equipment.json
git commit -m "feat: NFPA70 chapter4-equipment.json — light Ch 4 articles + pointers"
```

---

## Task 6: Create chapter5-special-occupancies.json (light Ch 5 articles, pointers to 500-506 and 517)

**Files:**
- Create: `shared/standards/electrical/NFPA70/chapter5-special-occupancies.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "NFPA 70 Chapter 5 — Special Occupancies",
  "_chapter": 5,
  "_version": "1.0.0",
  "_note": "Light Ch 5 articles inline. Arts 500-506 (hazardous locations) and 517 (healthcare) have dedicated per-article files.",
  "articles": [
    {
      "article_id": "ART_511",
      "nec_ref": "NFPA 70:2023 Article 511",
      "chapter": 5,
      "article_number": 511,
      "article_title": "Commercial Garages, Repair and Storage",
      "scope": "Repair garages where flammable liquids/gases are dispensed or transferred. Classified locations depend on whether the garage is major repair (Class I Div 2 within 18 in of floor) or minor repair (unclassified).",
      "applies_to": ["repair_garages", "automotive", "hazardous_classification"],
      "key_sections": [
        {"section": "511.3", "title": "Area Classification", "summary": "Major repair: Class I Div 2 within 18 in of floor in service/repair areas. Minor repair: unclassified unless flammable fuel-dispensing or fuel-tank repair"},
        {"section": "511.7", "title": "Wiring and Equipment Above Class I Locations", "summary": "Above 18 in: ordinary location wiring acceptable; below 18 in: hazardous-location wiring per Art 501"}
      ],
      "tabulated_values": {},
      "tables_inline": {},
      "common_errors": ["Treating an EV-repair garage as unclassified — EV battery rooms may warrant Class I Div 2 around electrolyte vent points"],
      "drawn_as": [],
      "related_iec_60364": ["IEC 60079 series (Hazardous areas)"],
      "divergence_notes": "Art 511 + 500-506 use Class/Division (legacy US) and Class/Zone (Art 505); IEC uses Zone classification only. See hazardous-locations-classification.json for the conversion matrix.",
      "related_bs_7671": [],
      "usage_notes": "Always confirm the AHJ's expected classification — many jurisdictions adopt stricter local interpretations.",
      "related_articles": ["ART_500_506", "ART_514"]
    },
    {
      "article_id": "ART_513",
      "nec_ref": "NFPA 70:2023 Article 513",
      "chapter": 5,
      "article_number": 513,
      "article_title": "Aircraft Hangars",
      "scope": "Hangars for aircraft maintenance/storage. Floor + 18 in classified Class I Div 2; 5 ft horizontal from aircraft Class I Div 2; full hangar Class I Div 2 above grade up to specific limits.",
      "applies_to": ["aviation", "hangars", "hazardous_classification"],
      "key_sections": [
        {"section": "513.3", "title": "Classification of Locations", "summary": "Floor + 18 in: Class I Div 2 throughout. Within 5 ft of aircraft: Class I Div 2. Above 18 in but within the hangar volume: generally unclassified"}
      ],
      "tabulated_values": {},
      "tables_inline": {},
      "common_errors": ["Failing to classify the wing-tip envelope when defueling — aircraft fuel ops temporarily extend the classified zone"],
      "drawn_as": [],
      "related_iec_60364": ["IEC 60079 series"],
      "divergence_notes": "Art 513 is highly application-specific; IEC handles via 60079-10-1 area classification with no aviation-specific guide.",
      "related_bs_7671": [],
      "usage_notes": "Coordinate with the hangar's fire-protection layout (foam suppression, fuel-handling SOPs).",
      "related_articles": ["ART_500_506"]
    },
    {
      "article_id": "ART_514",
      "nec_ref": "NFPA 70:2023 Article 514",
      "chapter": 5,
      "article_number": 514,
      "article_title": "Motor Fuel Dispensing Facilities",
      "scope": "Gas stations, EV-fast-charging-with-fuel-dispensing combo sites. Defines classified zones around dispensers (Class I Div 1 inside dispenser; Class I Div 2 within 18 in of grade × 20 ft horizontal).",
      "applies_to": ["gas_stations", "fuel_dispensing", "hazardous_classification"],
      "key_sections": [
        {"section": "514.3", "title": "Class I Locations", "summary": "Dispenser internal: Div 1. Within 18 in of grade × 20 ft horizontal radius: Div 2. Tank vents: Div 1 within 3 ft × Div 2 to 10 ft"},
        {"section": "514.9", "title": "Seal-off requirements", "summary": "Conduit seals at boundary of classified location"}
      ],
      "tabulated_values": {},
      "tables_inline": {},
      "common_errors": ["Missing the 20-ft horizontal envelope around dispensers — frequent inspection failure"],
      "drawn_as": [],
      "related_iec_60364": ["IEC 60079-10-1 (Gas hazardous areas classification)"],
      "divergence_notes": "Art 514 dimensions (18 in, 20 ft, 3 ft, 10 ft) are NEC-specific; IEC uses similar zonal envelopes but in metric and via the API RP 500 / IEC 60079-10-1 source-based classification method.",
      "related_bs_7671": [],
      "usage_notes": "On a project that combines fuel dispensing + EV fast-charging, verify the EV equipment is sited OUTSIDE the Class I Div 2 envelope.",
      "related_articles": ["ART_500_506", "ART_625"]
    },
    {
      "article_id": "ART_518",
      "nec_ref": "NFPA 70:2023 Article 518",
      "chapter": 5,
      "article_number": 518,
      "article_title": "Assembly Occupancies",
      "scope": "Spaces accommodating ≥100 persons (auditoriums, theatres, churches, conference centres). Wiring method restrictions, emergency-circuit independence.",
      "applies_to": ["assembly_occupancies", "auditoriums", "wiring_method_restrictions"],
      "key_sections": [
        {"section": "518.4", "title": "Wiring Methods", "summary": "Metal-clad wiring (RMC/IMC/EMT/MC/AC) typical; NM cable prohibited in occupancies of >100 persons (exception: dwelling-style portions)"}
      ],
      "tabulated_values": {},
      "tables_inline": {},
      "common_errors": ["Specifying NM cable in assembly occupancy floor — prohibited"],
      "drawn_as": [],
      "related_iec_60364": [],
      "divergence_notes": "NEC restricts NM cable in assembly occupancies; IEC has no NM-cable equivalent (uses singles in conduit/trunking by default).",
      "related_bs_7671": [],
      "usage_notes": "Confirm occupancy load classification with the building code (IBC) before selecting wiring methods.",
      "related_articles": ["ART_300", "ART_700"]
    },
    {
      "article_id": "ART_547",
      "nec_ref": "NFPA 70:2023 Article 547",
      "chapter": 5,
      "article_number": 547,
      "article_title": "Agricultural Buildings",
      "scope": "Buildings housing livestock or storing/handling materials creating dust/corrosive/moisture issues. Equipotential bonding (547.10), site-specific wiring methods.",
      "applies_to": ["agricultural", "livestock", "equipotential_bonding"],
      "key_sections": [
        {"section": "547.10", "title": "Equipotential Planes and Bonding of Equipotential Planes", "summary": "Equipotential plane required in animal-confinement areas — bonded to building grounding electrode system"}
      ],
      "tabulated_values": {},
      "tables_inline": {},
      "common_errors": ["Omitting the equipotential plane in dairy/swine facilities — animals are sensitive to step voltages from stray currents"],
      "drawn_as": [],
      "related_iec_60364": ["IEC 60364-7-705 (Agricultural and horticultural premises)"],
      "divergence_notes": "NEC's equipotential plane requirement (547.10) and IEC 60364-7-705 supplementary bonding rules cover similar ground but with different mandatory thresholds.",
      "related_bs_7671": [],
      "usage_notes": "Always include the equipotential plane on agricultural building designs.",
      "related_articles": ["ART_250"]
    },
    {
      "article_id": "ART_590",
      "nec_ref": "NFPA 70:2023 Article 590",
      "chapter": 5,
      "article_number": 590,
      "article_title": "Temporary Installations",
      "scope": "Temporary wiring for construction, decorations, holidays. GFCI required on construction site receptacles (590.6).",
      "applies_to": ["temporary_wiring", "construction_sites", "decorative_lighting"],
      "key_sections": [
        {"section": "590.6", "title": "Ground-Fault Protection for Personnel (Construction Sites)", "summary": "All 125 V/15-, 20-, 30-A receptacles on construction sites require GFCI protection (Class A) for personnel"}
      ],
      "tabulated_values": {},
      "tables_inline": {},
      "common_errors": ["Using non-GFCI 'plug strips' on construction sites — prohibited; every receptacle must be GFCI-protected"],
      "drawn_as": [],
      "related_iec_60364": ["IEC 60364-7-704 (Construction and demolition site installations)"],
      "divergence_notes": "NEC 590.6 GFCI requirement is functionally equivalent to IEC 60364-7-704 30 mA RCD requirement, but NEC requires Class A GFCI (4-6 mA trip) which is more sensitive than IEC general-use 30 mA RCD.",
      "related_bs_7671": [],
      "usage_notes": "Default to GFCI on all construction site receptacles regardless of voltage.",
      "related_articles": ["ART_210", "ART_250"]
    },
    {
      "article_number": 500,
      "article_title": "Hazardous (Classified) Locations — Bundle (Arts 500, 501, 502, 503, 504, 505, 506)",
      "scope": "Class I/II/III, Division 1/2, Zone 0/1/2 classification systems and equipment requirements.",
      "full_content": "art500-506-hazardous-locations.json"
    },
    {
      "article_number": 517,
      "article_title": "Health Care Facilities",
      "scope": "Patient care areas, Type 1/2/3 EES, isolated power systems, X-ray.",
      "full_content": "art517-healthcare.json"
    }
  ]
}
```

- [ ] **Step 2: Validate and commit**

```bash
python3 -c "import json; json.load(open('shared/standards/electrical/NFPA70/chapter5-special-occupancies.json'))" && echo OK
git add shared/standards/electrical/NFPA70/chapter5-special-occupancies.json
git commit -m "feat: NFPA70 chapter5-special-occupancies.json — Arts 511, 513, 514, 518, 547, 590 + pointers"
```

---

## Task 7: Create chapter6-special-equipment.json (light Ch 6 articles, pointers to 625/680/690/695)

**Files:**
- Create: `shared/standards/electrical/NFPA70/chapter6-special-equipment.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "NFPA 70 Chapter 6 — Special Equipment",
  "_chapter": 6,
  "_version": "1.0.0",
  "_note": "Light Ch 6 articles inline. Arts 625 (EV), 680 (pools), 690 (PV), 695 (fire pumps) have dedicated per-article files.",
  "articles": [
    {
      "article_id": "ART_600",
      "nec_ref": "NFPA 70:2023 Article 600",
      "chapter": 6,
      "article_number": 600,
      "article_title": "Electric Signs and Outline Lighting",
      "scope": "Electric signs (fixed and portable), outline lighting (including neon and skeleton tubing). Branch circuit dedicated (600.5(A)); GFCI for portable signs (600.10(C)); secondary wiring (600.32 — neon).",
      "applies_to": ["electric_signs", "neon", "outline_lighting"],
      "key_sections": [
        {"section": "600.5", "title": "Branch Circuits", "summary": "Each commercial occupancy accessible to pedestrians and at least 20 A dedicated sign circuit"},
        {"section": "600.7", "title": "Grounding and Bonding", "summary": "Sign and metal equipment must be grounded; bonding for neon/skeleton tubing through GTO cable"}
      ],
      "tabulated_values": {},
      "tables_inline": {},
      "common_errors": ["Forgetting the 20 A dedicated sign branch circuit at each commercial occupancy entry"],
      "drawn_as": [],
      "related_iec_60364": [],
      "divergence_notes": "Art 600 is NEC-specific. IEC has no equivalent dedicated article — sign wiring handled via standard wiring methods + IEC 60598 for luminaires.",
      "related_bs_7671": [],
      "usage_notes": "Default to a dedicated 20 A circuit per occupancy front for sign use.",
      "related_articles": []
    },
    {
      "article_id": "ART_620",
      "nec_ref": "NFPA 70:2023 Article 620",
      "chapter": 6,
      "article_number": 620,
      "article_title": "Elevators, Dumbwaiters, Escalators, Moving Walks, Platform Lifts, and Stairway Chairlifts",
      "scope": "Elevator/escalator branch circuits, disconnect (620.51), feeder, GFCI for machine room receptacles (620.85), MoR (machine room) circuits.",
      "applies_to": ["elevators", "escalators", "lifts"],
      "key_sections": [
        {"section": "620.22", "title": "Branch Circuits for Other than Elevator Power", "summary": "Car lighting, car receptacles, machine room lighting and receptacles all on separate branch circuits (not on the elevator power circuit)"},
        {"section": "620.51", "title": "Disconnecting Means", "summary": "Disconnect for each elevator within sight of the controller; lockable; identified"},
        {"section": "620.85", "title": "Ground-Fault Circuit-Interrupter Protection for Personnel", "summary": "GFCI required for 125 V, 15- and 20-A receptacles in elevator pits, machine rooms, escalator wellways"}
      ],
      "tabulated_values": {},
      "tables_inline": {},
      "common_errors": ["Putting car lighting on the elevator power feeder — must be a separate branch circuit per 620.22"],
      "drawn_as": ["MOTOR"],
      "related_iec_60364": ["IEC 60364-7-708 (Caravan parks, camping sites and similar locations) — peripheral", "EN 81 series (Elevators) — primary reference outside NEC"],
      "divergence_notes": "NEC Art 620 is comprehensive for elevators; IEC defers to EN 81 series (lift equipment) for most elevator-specific rules.",
      "related_bs_7671": [],
      "usage_notes": "Coordinate with the elevator vendor's submittal — vendor specifies the controller's exact feeder and branch-circuit needs.",
      "related_articles": ["ART_430"]
    },
    {
      "article_id": "ART_645",
      "nec_ref": "NFPA 70:2023 Article 645",
      "chapter": 6,
      "article_number": 645,
      "article_title": "Information Technology Equipment",
      "scope": "IT rooms (data centres, server rooms, telecomm equipment rooms) meeting 645.4 conditions can use the optional rules of Art 645 — special wiring methods (under-floor wiring, abandoned cable), special disconnect requirements, optional zone-protection.",
      "applies_to": ["data_centres", "server_rooms", "it_equipment_rooms"],
      "key_sections": [
        {"section": "645.4", "title": "Special Requirements for Information Technology Equipment Room", "summary": "All five conditions must be met to use Art 645 (disconnecting means at exits, fire suppression, room construction, etc.)"},
        {"section": "645.10","title": "Disconnecting Means", "summary": "Disconnect at each principal exit to shut down IT equipment power and HVAC simultaneously (the 'EPO' button)"}
      ],
      "tabulated_values": {},
      "tables_inline": {},
      "common_errors": ["Trying to use Art 645 optional rules without meeting all five 645.4 conditions — invalidates the entire article's permissions"],
      "drawn_as": [],
      "related_iec_60364": ["IEC 60364-7-740 (data centres) — partial coverage"],
      "divergence_notes": "Art 645's 'opt-in' approach is unique to NEC — meet the conditions and gain permission to use optional wiring methods. IEC handles data-centre power through TIA-942 and dedicated IEC 60364-7-740 (partial scope).",
      "related_bs_7671": [],
      "usage_notes": "Document the five 645.4 conditions explicitly on the design narrative if claiming Art 645 permissions.",
      "related_articles": ["ART_725", "ART_770"]
    },
    {
      "article_id": "ART_670",
      "nec_ref": "NFPA 70:2023 Article 670",
      "chapter": 6,
      "article_number": 670,
      "article_title": "Industrial Machinery",
      "scope": "Industrial machines per NFPA 79 (Electrical Standard for Industrial Machinery). Disconnect, nameplate, SCCR, supply conductors.",
      "applies_to": ["industrial_machinery", "manufacturing_equipment"],
      "key_sections": [
        {"section": "670.4", "title": "Nameplate Data", "summary": "Industrial machine nameplate must include: supply voltage, FLA, SCCR, max OCPD ahead of machine, etc."},
        {"section": "670.5", "title": "Short-Circuit Current Rating", "summary": "Machine SCCR must equal or exceed available fault current at point of supply"}
      ],
      "tabulated_values": {},
      "tables_inline": {},
      "common_errors": ["Specifying a machine with SCCR < available fault current — common failure on retrofits"],
      "drawn_as": [],
      "related_iec_60364": ["IEC 60204-1 (Safety of machinery — Electrical equipment of machines) — primary IEC reference for industrial machinery"],
      "divergence_notes": "Art 670 + NFPA 79 ≈ IEC 60204-1; conceptually aligned but specific values and certifications differ.",
      "related_bs_7671": [],
      "usage_notes": "Cross-reference NFPA 79 for machine-internal wiring; NEC 670 covers the supply side.",
      "related_articles": ["ART_430", "ART_409"]
    },
    {
      "article_number": 625,
      "article_title": "Electric Vehicle Power Transfer System",
      "scope": "EV charging — Levels 1/2/3, 125% continuous sizing, GFCI, ventilation, load management.",
      "full_content": "art625-ev-charging.json"
    },
    {
      "article_number": 680,
      "article_title": "Swimming Pools, Fountains, and Similar Installations",
      "scope": "Pools, spas, hot tubs, fountains — GFCI rules, equipotential bonding, receptacle clearances.",
      "full_content": "art680-pools-spas.json"
    },
    {
      "article_number": 690,
      "article_title": "Solar Photovoltaic (PV) Systems",
      "scope": "PV system definitions, circuit sizing, max voltage, DC arc fault, rapid shutdown, grounding.",
      "full_content": "art690-solar-pv.json"
    },
    {
      "article_number": 695,
      "article_title": "Fire Pumps",
      "scope": "Fire pump power source, supply continuity, controller, conductor sizing, disconnect prohibition.",
      "full_content": "art695-fire-pumps.json"
    }
  ]
}
```

- [ ] **Step 2: Validate and commit**

```bash
python3 -c "import json; json.load(open('shared/standards/electrical/NFPA70/chapter6-special-equipment.json'))" && echo OK
git add shared/standards/electrical/NFPA70/chapter6-special-equipment.json
git commit -m "feat: NFPA70 chapter6-special-equipment.json — light Ch 6 articles + pointers"
```

---

## Task 8: Create chapter7-special-conditions.json (Arts 706/710/712/725/727/728/760/770 + pointer to 700-705)

**Files:**
- Create: `shared/standards/electrical/NFPA70/chapter7-special-conditions.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "NFPA 70 Chapter 7 — Special Conditions",
  "_chapter": 7,
  "_version": "1.0.0",
  "_note": "Emergency/standby/interconnect (Arts 700-705) bundled in art700-705-emergency-standby.json. Other Ch 7 articles inline.",
  "articles": [
    {
      "article_id": "ART_706",
      "nec_ref": "NFPA 70:2023 Article 706",
      "chapter": 7,
      "article_number": 706,
      "article_title": "Energy Storage Systems (ESS)",
      "scope": "Stationary ESS — batteries (Li-ion, lead-acid, flow), capacitors. Listing per UL 9540 (706.4), disconnect (706.7), location (residential garage, utility closet limits), interconnection with PV and grid (705).",
      "applies_to": ["energy_storage", "battery_ess", "li_ion_ess", "residential_storage", "commercial_storage"],
      "key_sections": [
        {"section": "706.4",  "title": "Listing", "summary": "ESS must be listed per UL 9540 (System) and components per UL 9540A (Thermal runaway test)"},
        {"section": "706.7",  "title": "Disconnecting Means", "summary": "Disconnect within sight or remote with lockout-tagout; identified for service personnel; first responder readability"},
        {"section": "706.10", "title": "Qualified Personnel", "summary": "Installation by qualified persons; commissioning per manufacturer"},
        {"section": "706.20", "title": "Self-Contained Energy Storage System", "summary": "Listed self-contained ESS — installation, ventilation, location restrictions"}
      ],
      "tabulated_values": {},
      "tables_inline": {},
      "common_errors": [
        "Treating an ESS as just an Art 480 battery installation — 706 layered requirements apply, including UL 9540 listing",
        "Installing residential Li-ion ESS in an attached garage without complying with NFPA 855 separation rules (referenced from 706)"
      ],
      "drawn_as": ["BATTERY", "ESS_BATTERY"],
      "related_iec_60364": ["IEC 60364-8-2 (Prosumer's electrical installations)", "IEC 62933 series (Electrical energy storage systems)"],
      "divergence_notes": "Art 706 (since NEC 2017) consolidates ESS-specific rules; IEC handles via IEC 62933 (technical) + IEC 60364-8-2 (installation). UL 9540 listing is NEC-mandated; IEC equivalent is IEC 62933-5-2. NFPA 855 (Stationary Energy Storage Systems) is the companion installation standard referenced from Art 706; IEC equivalent IEC 62933-5-1.",
      "related_bs_7671": [],
      "usage_notes": "For PV+ESS, read Art 690 + 705 + 706 together. ESS rapid shutdown handled via 690.12 when PV-coupled.",
      "related_articles": ["ART_480", "ART_690", "ART_705"]
    },
    {
      "article_id": "ART_710",
      "nec_ref": "NFPA 70:2023 Article 710",
      "chapter": 7,
      "article_number": 710,
      "article_title": "Stand-Alone Systems",
      "scope": "Off-grid power systems — PV-only, wind-only, gen-only, or hybrid where no utility connection exists. Voltage limits, backup load sizing, identification of power sources.",
      "applies_to": ["off_grid", "stand_alone_pv", "remote_systems"],
      "key_sections": [
        {"section": "710.10", "title": "Identification of Power Sources", "summary": "Permanent plaque at service equipment identifying all power sources"},
        {"section": "710.15", "title": "General", "summary": "Backup load may be lower than original-utility load; sized per actual standalone capacity"}
      ],
      "tabulated_values": {},
      "tables_inline": {},
      "common_errors": ["Sizing stand-alone system to original utility load instead of actual standalone autonomy needs"],
      "drawn_as": [],
      "related_iec_60364": ["IEC 60364-8-2 (Prosumer's electrical installations) — partial coverage"],
      "divergence_notes": "Art 710 is NEC-specific to stand-alone (no utility) systems. IEC 60364-8-2 covers prosumer (with-grid) systems more thoroughly; standalone is via national supplements.",
      "related_bs_7671": [],
      "usage_notes": "Document the stand-alone capacity vs total load on the design narrative; cite NEC 710 for the source identification plaque requirement.",
      "related_articles": ["ART_690", "ART_705", "ART_706"]
    },
    {
      "article_id": "ART_712",
      "nec_ref": "NFPA 70:2023 Article 712",
      "chapter": 7,
      "article_number": 712,
      "article_title": "Direct Current Microgrids",
      "scope": "DC microgrids — distribution at DC voltage levels, bus voltages, interconnection with AC system, DC OCPDs.",
      "applies_to": ["dc_microgrid", "data_centre_dc", "telecom_dc"],
      "key_sections": [
        {"section": "712.10", "title": "Voltage", "summary": "DC microgrid bus voltage classifications: ≤60 V (ELV), 60-1500 V"}
      ],
      "tabulated_values": {},
      "tables_inline": {},
      "common_errors": ["Using AC-rated OCPDs in a DC microgrid — DC has no zero-crossing; OCPDs must be DC-rated"],
      "drawn_as": [],
      "related_iec_60364": ["IEC 60364-8-2 (Prosumer's electrical installations) — partial"],
      "divergence_notes": "Art 712 is NEC-specific. IEC handles DC distribution via IEC 60364-5-52 with DC-specific Annex content; full DC microgrid standardisation is emerging (IEC 60364-8-3 in development).",
      "related_bs_7671": [],
      "usage_notes": "DC microgrid design is still emerging; coordinate with the equipment vendor's DC-rated component list.",
      "related_articles": ["ART_690", "ART_706"]
    },
    {
      "article_id": "ART_725",
      "nec_ref": "NFPA 70:2023 Article 725",
      "chapter": 7,
      "article_number": 725,
      "article_title": "Class 1, Class 2, and Class 3 Remote-Control, Signaling, and Power-Limited Circuits",
      "scope": "Low-voltage / power-limited circuits — Class 1 (≤30 V, 1000 VA limited), Class 2 (60 V, 100 VA), Class 3 (similar voltage, lower energy). Wiring methods, separation from other circuits.",
      "applies_to": ["control_circuits", "low_voltage", "signaling"],
      "key_sections": [
        {"section": "725.41", "title": "Power Sources for Class 2 and Class 3 Circuits", "summary": "Listed Class 2 / 3 transformer or power supply per UL 1310"},
        {"section": "725.143","title": "Conductors of Different Circuits in Same Cable, Cable Tray, Enclosure, or Raceway", "summary": "Class 2/3 circuits cannot share with Class 1, power, or lighting circuits except with permitted separation"}
      ],
      "tabulated_values": {},
      "tables_inline": {},
      "common_errors": ["Mixing Class 2 control wiring with power circuits in the same raceway — prohibited"],
      "drawn_as": [],
      "related_iec_60364": ["IEC 60364-4-41 Clause 414 (PELV/SELV systems)"],
      "divergence_notes": "NEC Class 2/3 ≈ IEC SELV/PELV but with different voltage/energy limits and listing regimes.",
      "related_bs_7671": [],
      "usage_notes": "Specify the Class on every low-voltage circuit on the schedule.",
      "related_articles": ["ART_645", "ART_760"]
    },
    {
      "article_id": "ART_760",
      "nec_ref": "NFPA 70:2023 Article 760",
      "chapter": 7,
      "article_number": 760,
      "article_title": "Fire Alarm Systems",
      "scope": "Fire alarm circuits — Non-power-limited (NPLFA) and Power-limited (PLFA) systems. Wiring methods, conductor sizing, separation from other circuits, cable listing (FPLP, FPL, FPLR).",
      "applies_to": ["fire_alarm", "life_safety_circuits"],
      "key_sections": [
        {"section": "760.41",  "title": "Power Sources for Power-Limited Fire Alarm Circuits", "summary": "Listed PLFA transformer or power supply"},
        {"section": "760.139", "title": "Listing and Marking of PLFA Cables", "summary": "FPLP (plenum), FPLR (riser), FPL (general)"}
      ],
      "tabulated_values": {},
      "tables_inline": {},
      "common_errors": ["Using non-fire-rated cable on plenum-rated fire alarm circuit — FPLP required in air-handling spaces"],
      "drawn_as": ["FIRE_ALARM_DEVICE"],
      "related_iec_60364": ["IEC 60364-5-56 (Safety services)"],
      "divergence_notes": "Art 760 is the NEC-specific fire alarm wiring standard; NFPA 72 (National Fire Alarm Code) is the companion device-and-system standard. IEC covers fire alarm wiring via 60364-5-56 + national supplements.",
      "related_bs_7671": [],
      "usage_notes": "Coordinate with the project's NFPA 72 fire alarm design. Cable type (FPLP/FPLR/FPL) by installation location.",
      "related_articles": ["ART_725", "ART_770"]
    },
    {
      "article_id": "ART_770",
      "nec_ref": "NFPA 70:2023 Article 770",
      "chapter": 7,
      "article_number": 770,
      "article_title": "Optical Fiber Cables",
      "scope": "Optical fiber cable installation — conductive vs non-conductive cable types, abandoned cable removal, raceway and routing rules.",
      "applies_to": ["fiber_optic", "data_cabling"],
      "key_sections": [
        {"section": "770.179", "title": "Listing and Marking of Optical Fiber Cables", "summary": "OFNP (plenum), OFNR (riser), OFNG (general), OFN (general restricted)"}
      ],
      "tabulated_values": {},
      "tables_inline": {},
      "common_errors": ["Leaving abandoned fiber in place after retrofit — 770.25 requires removal"],
      "drawn_as": [],
      "related_iec_60364": [],
      "divergence_notes": "Art 770 (optical fiber) has no direct IEC 60364 analogue; IEC defers to ISO/IEC 11801 (premises cabling).",
      "related_bs_7671": [],
      "usage_notes": "Coordinate with the structured cabling design (ISO/IEC 11801).",
      "related_articles": ["ART_800"]
    },
    {
      "article_number": 700,
      "article_title": "Emergency Systems / Legally Required Standby / Optional Standby / Interconnect (Bundle 700, 701, 702, 705)",
      "scope": "Emergency systems, legally required standby, optional standby, interconnected power production sources.",
      "full_content": "art700-705-emergency-standby.json"
    }
  ]
}
```

- [ ] **Step 2: Validate and commit**

```bash
python3 -c "import json; json.load(open('shared/standards/electrical/NFPA70/chapter7-special-conditions.json'))" && echo OK
git add shared/standards/electrical/NFPA70/chapter7-special-conditions.json
git commit -m "feat: NFPA70 chapter7-special-conditions.json — Arts 706, 710, 712, 725, 760, 770 + 700-705 pointer"
```

---

## Task 9: Create chapter8-communications.json (Arts 800-840)

**Files:**
- Create: `shared/standards/electrical/NFPA70/chapter8-communications.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "NFPA 70 Chapter 8 — Communications Systems",
  "_chapter": 8,
  "_version": "1.0.0",
  "_note": "Chapter 8 STANDS ALONE per NEC 90.3 — not subject to Chapters 1-4 unless specifically referenced. Articles 800 (general), 805 (network-powered broadband), 810 (radio/TV), 820 (cable TV), 830 (premises-powered broadband), 840 (premises-powered broadband over POE).",
  "articles": [
    {
      "article_id": "ART_800",
      "nec_ref": "NFPA 70:2023 Article 800",
      "chapter": 8,
      "article_number": 800,
      "article_title": "General Requirements for Communications Systems",
      "scope": "General installation requirements for ALL Chapter 8 communications systems — telephone, intercom, network, audio. Wiring/cable listing, separation from power circuits (800.133), bonding of primary protector (800.100).",
      "applies_to": ["communications_general", "telephone", "intercom", "data"],
      "key_sections": [
        {"section": "800.100", "title": "Cable and Primary Protector Bonding and Grounding", "summary": "Primary protector grounded to building grounding electrode via #14 AWG (or larger) grounding conductor; bonded to power grounding system"},
        {"section": "800.133", "title": "Installation of Communications Wires, Cables, and Equipment", "summary": "Separation from power and Class 1 circuits — communications cables generally must be separated by 2 in from power conductors of >300 V unless one is in conduit"},
        {"section": "800.179", "title": "Listing and Marking of Communications Wires and Cables", "summary": "CMP (plenum), CMR (riser), CMG (general), CM (general restricted)"}
      ],
      "tabulated_values": {},
      "tables_inline": {},
      "common_errors": [
        "Failing to bond the primary protector to the building grounding electrode (800.100) — common during retrofits",
        "Mixing communications cables and power circuits in shared raceways without 2-in separation (800.133)"
      ],
      "drawn_as": [],
      "related_iec_60364": [],
      "divergence_notes": "NEC Chapter 8 stands alone (90.3); IEC handles communications via separate standards (ISO/IEC 11801, EN 50173). The 'primary protector' concept (800.100) is NEC-specific — bonding telecom protector to the building grounding electrode.",
      "related_bs_7671": [],
      "usage_notes": "Chapter 8 cross-references back to Chapter 1-4 are explicit (e.g., 800.100 references Art 250). Otherwise Chapter 8 stands alone.",
      "related_articles": ["ART_805", "ART_820", "ART_830", "ART_770"]
    },
    {
      "article_id": "ART_805",
      "nec_ref": "NFPA 70:2023 Article 805",
      "chapter": 8,
      "article_number": 805,
      "article_title": "Communications Circuits (Telephone, etc.)",
      "scope": "Telephone-circuit-specific requirements — primary protectors, listing of communications equipment, premises wiring.",
      "applies_to": ["telephone", "voice_circuits"],
      "key_sections": [
        {"section": "805.50", "title": "Circuit Loading", "summary": "Primary protector required where communications circuit exposed to lightning or accidental contact with power circuits >300 V"}
      ],
      "tabulated_values": {},
      "tables_inline": {},
      "common_errors": ["Omitting primary protector on aerial communications cable — required by 805.50"],
      "drawn_as": [],
      "related_iec_60364": [],
      "divergence_notes": "NEC Art 805 telephone-specific rules; IEC defers to national telecoms regulation.",
      "related_bs_7671": [],
      "usage_notes": "Read 805 + 800 together for the full picture.",
      "related_articles": ["ART_800"]
    },
    {
      "article_id": "ART_810",
      "nec_ref": "NFPA 70:2023 Article 810",
      "chapter": 8,
      "article_number": 810,
      "article_title": "Radio and Television Equipment",
      "scope": "Antenna systems (transmitting and receiving) — antenna lead-in cables, masts, antenna discharge units, grounding.",
      "applies_to": ["radio", "tv_antenna", "satellite_dish"],
      "key_sections": [
        {"section": "810.20", "title": "Antenna Discharge Units", "summary": "Antenna discharge unit (lightning arrester) on receiving antenna lead-ins"},
        {"section": "810.21", "title": "Grounding Conductors — Receiving Stations", "summary": "Antenna mast and antenna discharge unit grounded to building grounding electrode"}
      ],
      "tabulated_values": {},
      "tables_inline": {},
      "common_errors": ["Omitting antenna discharge unit on rooftop receiving antenna — required by 810.20"],
      "drawn_as": [],
      "related_iec_60364": [],
      "divergence_notes": "Art 810 antenna grounding ≈ IEC 62305-3 (Lightning protection) external systems. NEC requires antenna discharge unit grounding for receiving antennas; IEC handles via SPD coordination.",
      "related_bs_7671": [],
      "usage_notes": "Always coordinate antenna grounding with the building lightning-protection system if present.",
      "related_articles": ["ART_800", "ART_820"]
    },
    {
      "article_id": "ART_820",
      "nec_ref": "NFPA 70:2023 Article 820",
      "chapter": 8,
      "article_number": 820,
      "article_title": "Community Antenna Television and Radio Distribution Systems (CATV)",
      "scope": "Cable television and coaxial distribution — same primary-protector / separation / bonding regime as Art 800.",
      "applies_to": ["catv", "coaxial_cable_tv"],
      "key_sections": [
        {"section": "820.100", "title": "Cable and Primary Protector Bonding and Grounding", "summary": "Coaxial cable shield bonded/grounded at building entrance via #14 AWG conductor"}
      ],
      "tabulated_values": {},
      "tables_inline": {},
      "common_errors": ["Failing to ground the cable TV shield at building entrance"],
      "drawn_as": [],
      "related_iec_60364": [],
      "divergence_notes": "NEC Art 820 CATV-specific; IEC handles via ISO/IEC 11801 and national CATV regulations.",
      "related_bs_7671": [],
      "usage_notes": "Coordinate with the cable provider's drop installation.",
      "related_articles": ["ART_800"]
    },
    {
      "article_id": "ART_830",
      "nec_ref": "NFPA 70:2023 Article 830",
      "chapter": 8,
      "article_number": 830,
      "article_title": "Network-Powered Broadband Communications Systems",
      "scope": "Network-powered broadband (power from the central office over the broadband line) — primary protector requirements, separation, cable types (BMR, BLP/BLR/BL).",
      "applies_to": ["network_powered_broadband", "fttp"],
      "key_sections": [
        {"section": "830.100","title": "Primary Protector Grounding and Bonding", "summary": "Primary protector grounded same as Art 800"},
        {"section": "830.179","title": "Listing of Equipment, Wires, Cables, and Devices", "summary": "Cable types BMR, BLP, BLR, BL by application"}
      ],
      "tabulated_values": {},
      "tables_inline": {},
      "common_errors": [],
      "drawn_as": [],
      "related_iec_60364": [],
      "divergence_notes": "NEC Art 830 covers network-powered broadband (rare topology); IEC has no direct equivalent.",
      "related_bs_7671": [],
      "usage_notes": "Read in conjunction with the provider's drop equipment spec.",
      "related_articles": ["ART_800", "ART_840"]
    },
    {
      "article_id": "ART_840",
      "nec_ref": "NFPA 70:2023 Article 840",
      "chapter": 8,
      "article_number": 840,
      "article_title": "Premises-Powered Broadband Communications Systems",
      "scope": "Premises-powered broadband (the customer powers the ONT/router locally) — Power over Ethernet (PoE) at the network interface, battery backup considerations.",
      "applies_to": ["premises_powered_broadband", "poe", "fttp_premises"],
      "key_sections": [
        {"section": "840.160", "title": "Powering Circuits", "summary": "Premises power source for the broadband terminal — typically PoE (Class 2/3 power-limited)"}
      ],
      "tabulated_values": {},
      "tables_inline": {},
      "common_errors": [],
      "drawn_as": [],
      "related_iec_60364": [],
      "divergence_notes": "NEC Art 840 covers premises-powered broadband + PoE specifics; IEC handles via IEC 60364-4-41 PELV and IEC 60950 / IEC 62368 for ONT/router equipment.",
      "related_bs_7671": [],
      "usage_notes": "On fiber-to-the-premises (FTTP) installations, this is the primary article — read with 770 (optical fiber).",
      "related_articles": ["ART_770", "ART_800", "ART_725"]
    }
  ]
}
```

- [ ] **Step 2: Validate and commit**

```bash
python3 -c "import json; json.load(open('shared/standards/electrical/NFPA70/chapter8-communications.json'))" && echo OK
git add shared/standards/electrical/NFPA70/chapter8-communications.json
git commit -m "feat: NFPA70 chapter8-communications.json — Arts 800, 805, 810, 820, 830, 840"
```

---

## Task 10: Create chapter9-tables.json (Tables 1-10, conductor properties, conduit dimensions)

**Files:**
- Create: `shared/standards/electrical/NFPA70/chapter9-tables.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "NFPA 70 Chapter 9 — Tables",
  "_chapter": 9,
  "_version": "1.0.0",
  "_note": "Chapter 9 is INFORMATIONAL — tables of conductor properties, conduit fill, conduit/tubing dimensions, voltage drop multipliers, AC resistance/reactance. The most-consumed reference in the layer. NOT structured as articles; structured as tables.",
  "tables": {
    "Table_1_Percent_of_Cross_Section_for_Conductors_in_Conduit_or_Tubing": {
      "title": "Maximum Conductor Fill Percentage",
      "_source": "NFPA 70:2023 Chapter 9 Table 1",
      "rows": [
        {"number_of_conductors": 1,        "fill_percent": 53},
        {"number_of_conductors": 2,        "fill_percent": 31},
        {"number_of_conductors": "over 2", "fill_percent": 40}
      ],
      "_note": "Apply to total cross-sectional area of conductors and apply to the internal area of the raceway from Table 4."
    },
    "Table_4_Dimensions_and_Percent_Area_of_Conduit_and_Tubing": {
      "title": "Conduit/Tubing Internal Cross-Sectional Area (selected sizes)",
      "_source": "NFPA 70:2023 Chapter 9 Table 4 (selected — full table covers all standard sizes)",
      "rows": [
        {"trade_size_in": "1/2",  "rmc_total_area_in2": 0.314, "rmc_2_wire_area_in2": 0.097, "rmc_over_2_area_in2": 0.125, "emt_total_area_in2": 0.304, "emt_over_2_area_in2": 0.122},
        {"trade_size_in": "3/4",  "rmc_total_area_in2": 0.549, "rmc_2_wire_area_in2": 0.170, "rmc_over_2_area_in2": 0.220, "emt_total_area_in2": 0.533, "emt_over_2_area_in2": 0.213},
        {"trade_size_in": "1",    "rmc_total_area_in2": 0.887, "rmc_2_wire_area_in2": 0.275, "rmc_over_2_area_in2": 0.355, "emt_total_area_in2": 0.864, "emt_over_2_area_in2": 0.346},
        {"trade_size_in": "1 1/4","rmc_total_area_in2": 1.526, "rmc_2_wire_area_in2": 0.473, "rmc_over_2_area_in2": 0.610, "emt_total_area_in2": 1.496, "emt_over_2_area_in2": 0.598},
        {"trade_size_in": "1 1/2","rmc_total_area_in2": 2.071, "rmc_2_wire_area_in2": 0.642, "rmc_over_2_area_in2": 0.829, "emt_total_area_in2": 2.036, "emt_over_2_area_in2": 0.814},
        {"trade_size_in": "2",    "rmc_total_area_in2": 3.408, "rmc_2_wire_area_in2": 1.056, "rmc_over_2_area_in2": 1.363, "emt_total_area_in2": 3.356, "emt_over_2_area_in2": 1.342},
        {"trade_size_in": "2 1/2","rmc_total_area_in2": 4.866, "rmc_2_wire_area_in2": 1.508, "rmc_over_2_area_in2": 1.946, "emt_total_area_in2": 5.858, "emt_over_2_area_in2": 2.343},
        {"trade_size_in": "3",    "rmc_total_area_in2": 7.499, "rmc_2_wire_area_in2": 2.325, "rmc_over_2_area_in2": 3.000, "emt_total_area_in2": 8.846, "emt_over_2_area_in2": 3.538},
        {"trade_size_in": "4",    "rmc_total_area_in2":12.882, "rmc_2_wire_area_in2": 3.993, "rmc_over_2_area_in2": 5.153, "emt_total_area_in2":15.518, "emt_over_2_area_in2": 6.207}
      ]
    },
    "Table_5_Dimensions_of_Insulated_Conductors_and_Fixture_Wires": {
      "title": "Conductor External Cross-Sectional Area (THWN/THHN, selected)",
      "_source": "NFPA 70:2023 Chapter 9 Table 5 (selected)",
      "rows": [
        {"size_awg_kcmil": 14,   "thhn_thwn_area_in2": 0.0097},
        {"size_awg_kcmil": 12,   "thhn_thwn_area_in2": 0.0133},
        {"size_awg_kcmil": 10,   "thhn_thwn_area_in2": 0.0211},
        {"size_awg_kcmil": 8,    "thhn_thwn_area_in2": 0.0366},
        {"size_awg_kcmil": 6,    "thhn_thwn_area_in2": 0.0507},
        {"size_awg_kcmil": 4,    "thhn_thwn_area_in2": 0.0824},
        {"size_awg_kcmil": 3,    "thhn_thwn_area_in2": 0.0973},
        {"size_awg_kcmil": 2,    "thhn_thwn_area_in2": 0.1158},
        {"size_awg_kcmil": 1,    "thhn_thwn_area_in2": 0.1562},
        {"size_awg_kcmil": "1/0","thhn_thwn_area_in2": 0.1855},
        {"size_awg_kcmil": "2/0","thhn_thwn_area_in2": 0.2223},
        {"size_awg_kcmil": "3/0","thhn_thwn_area_in2": 0.2679},
        {"size_awg_kcmil": "4/0","thhn_thwn_area_in2": 0.3237},
        {"size_awg_kcmil": 250,  "thhn_thwn_area_in2": 0.3970},
        {"size_awg_kcmil": 300,  "thhn_thwn_area_in2": 0.4608},
        {"size_awg_kcmil": 350,  "thhn_thwn_area_in2": 0.5242},
        {"size_awg_kcmil": 400,  "thhn_thwn_area_in2": 0.5863},
        {"size_awg_kcmil": 500,  "thhn_thwn_area_in2": 0.7073}
      ]
    },
    "Table_8_Conductor_Properties": {
      "title": "Conductor Properties (Cu, stranded class B, uncoated)",
      "_source": "NFPA 70:2023 Chapter 9 Table 8",
      "rows": [
        {"size_awg_kcmil": 18,    "stranding_qty": 7,  "area_kcmil": 1.62,    "cu_ohms_per_kft_dc_75c": 7.95,  "cu_diameter_in": 0.046},
        {"size_awg_kcmil": 16,    "stranding_qty": 7,  "area_kcmil": 2.58,    "cu_ohms_per_kft_dc_75c": 4.99,  "cu_diameter_in": 0.058},
        {"size_awg_kcmil": 14,    "stranding_qty": 7,  "area_kcmil": 4.11,    "cu_ohms_per_kft_dc_75c": 3.14,  "cu_diameter_in": 0.073},
        {"size_awg_kcmil": 12,    "stranding_qty": 7,  "area_kcmil": 6.53,    "cu_ohms_per_kft_dc_75c": 1.98,  "cu_diameter_in": 0.092},
        {"size_awg_kcmil": 10,    "stranding_qty": 7,  "area_kcmil": 10.38,   "cu_ohms_per_kft_dc_75c": 1.24,  "cu_diameter_in": 0.116},
        {"size_awg_kcmil": 8,     "stranding_qty": 7,  "area_kcmil": 16.51,   "cu_ohms_per_kft_dc_75c": 0.778, "cu_diameter_in": 0.146},
        {"size_awg_kcmil": 6,     "stranding_qty": 7,  "area_kcmil": 26.24,   "cu_ohms_per_kft_dc_75c": 0.491, "cu_diameter_in": 0.184},
        {"size_awg_kcmil": 4,     "stranding_qty": 7,  "area_kcmil": 41.74,   "cu_ohms_per_kft_dc_75c": 0.308, "cu_diameter_in": 0.232},
        {"size_awg_kcmil": 3,     "stranding_qty": 7,  "area_kcmil": 52.62,   "cu_ohms_per_kft_dc_75c": 0.245, "cu_diameter_in": 0.260},
        {"size_awg_kcmil": 2,     "stranding_qty": 7,  "area_kcmil": 66.36,   "cu_ohms_per_kft_dc_75c": 0.194, "cu_diameter_in": 0.292},
        {"size_awg_kcmil": 1,     "stranding_qty": 19, "area_kcmil": 83.69,   "cu_ohms_per_kft_dc_75c": 0.154, "cu_diameter_in": 0.332},
        {"size_awg_kcmil": "1/0", "stranding_qty": 19, "area_kcmil": 105.6,   "cu_ohms_per_kft_dc_75c": 0.122, "cu_diameter_in": 0.373},
        {"size_awg_kcmil": "2/0", "stranding_qty": 19, "area_kcmil": 133.1,   "cu_ohms_per_kft_dc_75c": 0.0967,"cu_diameter_in": 0.419},
        {"size_awg_kcmil": "3/0", "stranding_qty": 19, "area_kcmil": 167.8,   "cu_ohms_per_kft_dc_75c": 0.0766,"cu_diameter_in": 0.470},
        {"size_awg_kcmil": "4/0", "stranding_qty": 19, "area_kcmil": 211.6,   "cu_ohms_per_kft_dc_75c": 0.0608,"cu_diameter_in": 0.528},
        {"size_awg_kcmil": 250,   "stranding_qty": 37, "area_kcmil": 250.0,   "cu_ohms_per_kft_dc_75c": 0.0515,"cu_diameter_in": 0.575},
        {"size_awg_kcmil": 350,   "stranding_qty": 37, "area_kcmil": 350.0,   "cu_ohms_per_kft_dc_75c": 0.0367,"cu_diameter_in": 0.681},
        {"size_awg_kcmil": 500,   "stranding_qty": 37, "area_kcmil": 500.0,   "cu_ohms_per_kft_dc_75c": 0.0258,"cu_diameter_in": 0.813},
        {"size_awg_kcmil": 750,   "stranding_qty": 61, "area_kcmil": 750.0,   "cu_ohms_per_kft_dc_75c": 0.0172,"cu_diameter_in": 0.998},
        {"size_awg_kcmil": 1000,  "stranding_qty": 61, "area_kcmil": 1000.0,  "cu_ohms_per_kft_dc_75c": 0.0129,"cu_diameter_in": 1.152}
      ]
    },
    "Table_9_Alternating_Current_Resistance_and_Reactance_for_600V_Cables": {
      "title": "AC Resistance and Reactance — 600 V, 3-phase, 60 Hz, 75 °C (selected, ohms/1000 ft)",
      "_source": "NFPA 70:2023 Chapter 9 Table 9",
      "_note": "Use for voltage-drop calculations. Combines effective Z = R cos θ + X sin θ for a given power factor.",
      "rows": [
        {"size_awg_kcmil": 14, "cu_pvc_resistance": 3.1, "cu_pvc_reactance": 0.058, "cu_steel_resistance": 3.1, "cu_steel_reactance": 0.073},
        {"size_awg_kcmil": 12, "cu_pvc_resistance": 2.0, "cu_pvc_reactance": 0.054, "cu_steel_resistance": 2.0, "cu_steel_reactance": 0.068},
        {"size_awg_kcmil": 10, "cu_pvc_resistance": 1.2, "cu_pvc_reactance": 0.050, "cu_steel_resistance": 1.2, "cu_steel_reactance": 0.063},
        {"size_awg_kcmil": 8,  "cu_pvc_resistance": 0.78,"cu_pvc_reactance": 0.052, "cu_steel_resistance": 0.78,"cu_steel_reactance": 0.065},
        {"size_awg_kcmil": 6,  "cu_pvc_resistance": 0.49,"cu_pvc_reactance": 0.051, "cu_steel_resistance": 0.49,"cu_steel_reactance": 0.064},
        {"size_awg_kcmil": 4,  "cu_pvc_resistance": 0.31,"cu_pvc_reactance": 0.048, "cu_steel_resistance": 0.31,"cu_steel_reactance": 0.060},
        {"size_awg_kcmil": 2,  "cu_pvc_resistance": 0.19,"cu_pvc_reactance": 0.045, "cu_steel_resistance": 0.20,"cu_steel_reactance": 0.057},
        {"size_awg_kcmil": "1/0","cu_pvc_resistance": 0.12,"cu_pvc_reactance": 0.044,"cu_steel_resistance":0.12,"cu_steel_reactance": 0.055},
        {"size_awg_kcmil": "4/0","cu_pvc_resistance": 0.063,"cu_pvc_reactance":0.041,"cu_steel_resistance":0.067,"cu_steel_reactance": 0.051},
        {"size_awg_kcmil": 250, "cu_pvc_resistance":0.052,"cu_pvc_reactance":0.041,"cu_steel_resistance":0.057,"cu_steel_reactance":0.052},
        {"size_awg_kcmil": 500, "cu_pvc_resistance":0.029,"cu_pvc_reactance":0.039,"cu_steel_resistance":0.032,"cu_steel_reactance":0.048}
      ]
    }
  },
  "_consuming_skills": "Skills computing ampacity, conduit fill, or voltage drop on US projects load this file alongside the relevant per-article file. Reference: art310-conductor-ampacity.json (ampacity tables 310.16/.17), conduit-fill.json (full fill calc procedure), ampacity-correction-factors.json (correction chain)."
}
```

- [ ] **Step 2: Validate and commit**

```bash
python3 -c "import json; json.load(open('shared/standards/electrical/NFPA70/chapter9-tables.json'))" && echo OK
git add shared/standards/electrical/NFPA70/chapter9-tables.json
git commit -m "feat: NFPA70 chapter9-tables.json — Tables 1, 4, 5, 8, 9 (fill, dimensions, conductor properties, AC Z)"
```

---

## Task 11: Create art210-branch-circuits.json

**Files:**
- Create: `shared/standards/electrical/NFPA70/art210-branch-circuits.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "NFPA 70 Article 210 — Branch Circuits",
  "_version": "1.0.0",
  "articles": [
    {
      "article_id": "ART_210",
      "nec_ref": "NFPA 70:2023 Article 210",
      "chapter": 2,
      "article_number": 210,
      "article_title": "Branch Circuits",
      "scope": "Branch-circuit ratings, GFCI and AFCI protection, required outlet locations, ground-fault protection of equipment, multi-wire branch circuits.",
      "applies_to": ["branch_circuits", "gfci", "afci", "receptacles", "dwelling_units"],
      "key_sections": [
        {"section": "210.3",   "title": "Rating", "summary": "Branch-circuit ratings limited to 15, 20, 30, 40, 50 A and certain higher per individual branch circuits"},
        {"section": "210.4",   "title": "Multiwire Branch Circuits", "summary": "Common identified disconnect at origin; neutral shall not depend on device connections; identification of grouped conductors"},
        {"section": "210.8",   "title": "Ground-Fault Circuit-Interrupter (GFCI) Protection for Personnel", "summary": "Required at: dwelling bathrooms, kitchens, garages, outdoor, basements, laundries, near pools (680); commercial bathrooms, rooftops, kitchen receptacles, dishwashers, etc. — expanded each cycle"},
        {"section": "210.12",  "title": "Arc-Fault Circuit-Interrupter (AFCI) Protection", "summary": "Required at: dwelling unit kitchens, dining, family, living, bedrooms, parlors, libraries, dens, sunrooms, recreation, closets, hallways — virtually all 120 V, 15- and 20-A circuits in dwellings"},
        {"section": "210.19",  "title": "Conductors — Minimum Ampacity and Size", "summary": "Branch-circuit conductors sized per 210.19(A) and (B). For continuous loads, 125% of continuous load + 100% of non-continuous"},
        {"section": "210.20",  "title": "Overcurrent Protection", "summary": "Rating ≥ continuous × 125% + non-continuous × 100%"},
        {"section": "210.52",  "title": "Dwelling Unit Receptacle Outlets — Required Locations", "summary": "Wall space spacing rule (no point > 6 ft from receptacle along wall), small appliance circuits (20A, ≥2 for kitchen), laundry (20A dedicated), bathroom (20A dedicated)"}
      ],
      "tabulated_values": {
        "gfci_required_locations_210_8": "see tables_inline",
        "afci_required_locations_210_12": "see tables_inline"
      },
      "tables_inline": {
        "GFCI_Required_Locations_210.8": {
          "title": "GFCI Protection Required (selected dwelling and commercial)",
          "rows": [
            {"location": "Dwelling bathrooms",                    "section": "210.8(A)(1)"},
            {"location": "Dwelling garages, carports",            "section": "210.8(A)(2)"},
            {"location": "Dwelling outdoors",                     "section": "210.8(A)(3)"},
            {"location": "Dwelling crawl space, basement",        "section": "210.8(A)(4)(5)"},
            {"location": "Dwelling kitchen receptacles",          "section": "210.8(A)(6)"},
            {"location": "Dwelling sinks (within 6 ft)",          "section": "210.8(A)(7)"},
            {"location": "Dwelling laundry, dishwasher",          "section": "210.8(A)(10)(11)"},
            {"location": "Commercial bathrooms",                  "section": "210.8(B)(1)"},
            {"location": "Commercial kitchens",                   "section": "210.8(B)(2)"},
            {"location": "Commercial rooftops",                   "section": "210.8(B)(3)"},
            {"location": "Commercial outdoors",                   "section": "210.8(B)(4)"},
            {"location": "Sinks (commercial, within 6 ft)",       "section": "210.8(B)(5)"},
            {"location": "Garages, accessory buildings",          "section": "210.8(B)(6)"},
            {"location": "Crawl spaces",                          "section": "210.8(B)(8)"}
          ]
        },
        "AFCI_Required_Locations_210.12": {
          "title": "AFCI Protection Required (Dwelling Units, NEC 2023)",
          "rows": [
            {"area": "Kitchens"},
            {"area": "Family rooms / dens / parlors / libraries / sunrooms / recreation rooms / closets / hallways / laundry"},
            {"area": "Bedrooms"},
            {"area": "Dining rooms"},
            {"area": "Living rooms"}
          ],
          "_note": "Applies to all 120 V, 15- and 20-A branch circuits supplying receptacles, lighting, and other outlets in these areas. Combination-type AFCI required (CAFCI per UL 1699)."
        }
      },
      "common_errors": [
        "Missing GFCI in dwelling laundry (added in NEC 2017, often missed in older designs)",
        "Missing AFCI in dwelling closet circuits (added in NEC 2014)",
        "Treating commercial bathroom as GFCI-exempt — required since NEC 2014",
        "Sizing branch-circuit conductors for the non-continuous portion only — must include 125% for continuous load"
      ],
      "drawn_as": ["SOCKET_OUTLET_DUPLEX", "SOCKET_OUTLET_GFCI", "MCB_1P"],
      "related_iec_60364": ["IEC 60364-4-41 (Protection against electric shock)", "IEC 60364-4-41 Clause 411 (Protection by automatic disconnection)"],
      "divergence_notes": "NEC GFCI (Class A, 4-6 mA trip) is more sensitive than IEC general-use RCD (30 mA); NEC GFCI covers personnel protection, IEC RCD covers both shock and fire. NEC AFCI (combination type per UL 1699) has no IEC equivalent in 60364 base — IEC 62606 (AFDD) is the analogue but is optional in IEC 60364 unless adopted nationally. NEC 210.52 dwelling outlet spacing has no IEC equivalent; IEC defers to national supplements.",
      "related_bs_7671": [],
      "usage_notes": "210.8 and 210.12 are the most-cited GFCI/AFCI references — load them on any dwelling-unit project. Note: 210.8 expanded substantially in 2020 and 2023 — review the changes when transitioning from older NEC editions.",
      "related_articles": ["ART_240", "ART_250", "ART_406", "ART_680"]
    }
  ]
}
```

- [ ] **Step 2: Validate and commit**

```bash
python3 -c "import json; json.load(open('shared/standards/electrical/NFPA70/art210-branch-circuits.json'))" && echo OK
git add shared/standards/electrical/NFPA70/art210-branch-circuits.json
git commit -m "feat: NFPA70 art210-branch-circuits.json — GFCI/AFCI requirements, outlet spacing"
```

---

## Task 12: Create art215-feeders.json

**Files:**
- Create: `shared/standards/electrical/NFPA70/art215-feeders.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "NFPA 70 Article 215 — Feeders",
  "_version": "1.0.0",
  "articles": [
    {
      "article_id": "ART_215",
      "nec_ref": "NFPA 70:2023 Article 215",
      "chapter": 2,
      "article_number": 215,
      "article_title": "Feeders",
      "scope": "Conductors between service equipment and final branch-circuit OCPD. Feeder ampacity, OCPD sizing, ground-fault protection for feeders ≥1000 A (215.10), voltage drop guidance (informational, not enforceable).",
      "applies_to": ["feeders", "subfeeders", "voltage_drop_informational"],
      "key_sections": [
        {"section": "215.2", "title": "Minimum Rating and Size", "summary": "Feeder rated ≥ continuous load × 125% + non-continuous load × 100%; matches branch-circuit sizing rule"},
        {"section": "215.3", "title": "Overcurrent Protection", "summary": "OCPD rating ≥ minimum required ampacity (215.2)"},
        {"section": "215.10","title": "Ground-Fault Protection of Equipment (GFP)", "summary": "Required for feeders rated ≥1000 A, more than 150 V to ground, less than 600 V phase-to-phase. Maximum setting 1200 A. Exceptions for continuous industrial process and fire pumps (Art 695)"},
        {"section": "215.12","title": "Identification for Feeders", "summary": "Where the premises has feeders supplied from more than one nominal voltage system, each ungrounded conductor must be identified by phase or line and system"}
      ],
      "tabulated_values": {},
      "tables_inline": {},
      "common_errors": [
        "Sizing feeder for non-continuous load only — must include 125% continuous-load multiplier",
        "Missing GFP at feeders ≥1000 A (215.10) — frequent inspection failure on commercial mains retrofits"
      ],
      "drawn_as": ["MCCB_3P"],
      "related_iec_60364": ["IEC 60364-4-43 (Protection against overcurrent)", "IEC 60364-5-52 (Wiring systems — ampacity)"],
      "divergence_notes": "NEC 215.2 explicit 125% continuous + 100% non-continuous rule is more prescriptive than IEC — IEC handles via Iz ampacity tables + diversity factors. NEC 215.10 GFP at ≥1000 A has no direct IEC equivalent — IEC requires RCD per IEC 60364-4-41 but trips below GFP set point.",
      "related_bs_7671": [],
      "usage_notes": "Voltage-drop guidance in 215.2(A)(1) Informational Note No. 2 (3% feeders, 5% combined) is NOT enforceable — design intent only.",
      "related_articles": ["ART_220", "ART_230", "ART_240", "ART_250"]
    }
  ]
}
```

- [ ] **Step 2: Validate and commit**

```bash
python3 -c "import json; json.load(open('shared/standards/electrical/NFPA70/art215-feeders.json'))" && echo OK
git add shared/standards/electrical/NFPA70/art215-feeders.json
git commit -m "feat: NFPA70 art215-feeders.json — feeder ampacity, OCPD, GFP at ≥1000A"
```

---

## Task 13: Create art220-load-calculations.json

**Files:**
- Create: `shared/standards/electrical/NFPA70/art220-load-calculations.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "NFPA 70 Article 220 — Branch-Circuit, Feeder, and Service Load Calculations",
  "_version": "1.0.0",
  "articles": [
    {
      "article_id": "ART_220",
      "nec_ref": "NFPA 70:2023 Article 220",
      "chapter": 2,
      "article_number": 220,
      "article_title": "Branch-Circuit, Feeder, and Service Load Calculations",
      "scope": "Load calculation methods — Standard (220.40) and Optional (220.82 dwelling / 220.84 multi-family / 220.86 office / 220.87 existing). Lighting load (220.12), receptacle load (220.14), motor load (220.50), AC load (220.82(C)).",
      "applies_to": ["load_calculation", "service_sizing", "feeder_sizing", "dwelling", "commercial"],
      "key_sections": [
        {"section": "220.12", "title": "Lighting Load for Listed Occupancies", "summary": "VA/ft² by occupancy from Table 220.12 (dwelling 3 VA/ft², office 3.5, school 3, store 3, hospital 2, etc.)"},
        {"section": "220.14", "title": "Other Loads — All Occupancies", "summary": "Receptacle outlets: each commercial receptacle = 180 VA; dwelling small-appliance 1500 VA per circuit"},
        {"section": "220.40", "title": "General — Computation of Loads (Standard Method)", "summary": "Sum of all loads applied to feeder; demand factors per Table 220.42 (dwellings), 220.44 (receptacles in non-dwelling), 220.54 (electric dryers), 220.55 (cooking equipment)"},
        {"section": "220.82", "title": "Dwelling Unit — Optional Calculation", "summary": "Alternative dwelling calc: 100% of first 10 kVA + 40% of remainder for general loads; HVAC at 100% or AC at 100% (whichever is larger)"},
        {"section": "220.83", "title": "Existing Dwelling Unit", "summary": "Optional calc for adding load to existing service — based on 80% of existing actual demand load"},
        {"section": "220.84", "title": "Multifamily Dwelling — Optional", "summary": "Demand factor table from 220.84(C) — applies to # units in the multifamily"},
        {"section": "220.86", "title": "Schools — Optional", "summary": "School-specific demand factors"},
        {"section": "220.87", "title": "Determining Existing Loads", "summary": "Use of recorded peak demand from utility for existing building"}
      ],
      "tabulated_values": {
        "lighting_load_va_per_ft2_220_12": "see tables_inline",
        "dwelling_demand_factors_220_42": "see tables_inline",
        "dryer_demand_220_54": "see tables_inline"
      },
      "tables_inline": {
        "Table_220.12_General_Lighting_Loads_by_Occupancy": {
          "title": "Unit Loads for General Lighting (VA per ft²)",
          "rows": [
            {"occupancy": "Armories, auditoriums",          "va_per_ft2": 1},
            {"occupancy": "Banks, offices",                  "va_per_ft2": 3.5},
            {"occupancy": "Barber shops, beauty parlors",    "va_per_ft2": 3},
            {"occupancy": "Churches",                        "va_per_ft2": 1},
            {"occupancy": "Clubs",                           "va_per_ft2": 2},
            {"occupancy": "Court rooms",                     "va_per_ft2": 2},
            {"occupancy": "Dwelling units (incl. lighting, small-appliance 1500VA × 2 + laundry 1500VA included in 220.42)", "va_per_ft2": 3},
            {"occupancy": "Garages — commercial (storage)",  "va_per_ft2": 0.5},
            {"occupancy": "Hospitals",                       "va_per_ft2": 2},
            {"occupancy": "Hotels, motels (no provisions for cooking)", "va_per_ft2": 2},
            {"occupancy": "Industrial commercial loft buildings", "va_per_ft2": 2},
            {"occupancy": "Lodge rooms",                      "va_per_ft2": 1.5},
            {"occupancy": "Offices",                          "va_per_ft2": 3.5},
            {"occupancy": "Restaurants",                      "va_per_ft2": 2},
            {"occupancy": "Schools",                          "va_per_ft2": 3},
            {"occupancy": "Stores",                           "va_per_ft2": 3},
            {"occupancy": "Warehouses (storage)",             "va_per_ft2": 0.25}
          ]
        },
        "Table_220.42_Demand_Factors_for_General_Lighting_Dwelling": {
          "title": "Demand Factor — Dwelling Unit General Lighting",
          "rows": [
            {"portion_va": "First 3000 VA", "demand_factor_pct": 100},
            {"portion_va": "3001-120,000 VA", "demand_factor_pct": 35},
            {"portion_va": "Remainder (over 120,000)", "demand_factor_pct": 25}
          ]
        },
        "Table_220.54_Demand_Factors_for_Household_Electric_Clothes_Dryers": {
          "title": "Electric Clothes Dryer Demand (Dwelling)",
          "rows": [
            {"number_of_dryers": "1-4", "demand_pct_of_5kva_per_dryer": 100},
            {"number_of_dryers": "5",   "demand_pct_of_5kva_per_dryer": 85},
            {"number_of_dryers": "10",  "demand_pct_of_5kva_per_dryer": 50},
            {"number_of_dryers": "20",  "demand_pct_of_5kva_per_dryer": 35},
            {"number_of_dryers": "≥30", "demand_pct_of_5kva_per_dryer": 25}
          ]
        }
      },
      "common_errors": [
        "Computing dwelling load with 220.40 (Standard) when 220.82 (Optional) gives a smaller, code-compliant answer — choose the lower of the two valid methods",
        "Forgetting the two small-appliance circuits (1500 VA each) + laundry circuit (1500 VA) when computing dwelling lighting load",
        "Using 220.82 Optional without including the HVAC 100% (or AC 100%, whichever is larger) per 220.82(C)",
        "Applying 220.12 lighting density to a kitchen — kitchen lighting comes through the dwelling load (220.42 + small-appliance)"
      ],
      "drawn_as": [],
      "related_iec_60364": ["IEC 60364-1 Annex Z (Method for assessment of maximum demand)"],
      "divergence_notes": "NEC 220 has TWO permitted load calc methods per project type (Standard 220.40 and Optional 220.82+) — the designer picks the lower; IEC has no parallel structured method, instead relying on diversity factors per circuit type. NEC 220.12 by-occupancy lighting load density (VA/ft²) is unique to NEC; IEC sizes from actual specified lighting + diversity.",
      "related_bs_7671": [],
      "usage_notes": "Always compute BOTH the Standard (220.40) and Optional (220.82+) for dwelling projects and use the smaller. Document which method was used in the design narrative.",
      "related_articles": ["ART_215", "ART_230", "ART_310", "ART_440"]
    }
  ]
}
```

- [ ] **Step 2: Validate and commit**

```bash
python3 -c "import json; json.load(open('shared/standards/electrical/NFPA70/art220-load-calculations.json'))" && echo OK
git add shared/standards/electrical/NFPA70/art220-load-calculations.json
git commit -m "feat: NFPA70 art220-load-calculations.json — Standard (220.40) and Optional (220.82+) methods"
```

---

## Task 14: Create art230-services.json

**Files:**
- Create: `shared/standards/electrical/NFPA70/art230-services.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "NFPA 70 Article 230 — Services",
  "_version": "1.0.0",
  "articles": [
    {
      "article_id": "ART_230",
      "nec_ref": "NFPA 70:2023 Article 230",
      "chapter": 2,
      "article_number": 230,
      "article_title": "Services",
      "scope": "Service conductors, equipment, and connections — overhead service drops, underground service laterals, service entrance conductors, service equipment, service disconnect (6-handle rule), GFP at services ≥1000 A (230.95).",
      "applies_to": ["services", "service_entrance", "service_disconnect", "gfp"],
      "key_sections": [
        {"section": "230.2",  "title": "Number of Services", "summary": "One service per building; multiple services permitted for special conditions (capacity, voltage, classification of supply)"},
        {"section": "230.40", "title": "Number of Service-Entrance Conductor Sets", "summary": "One set per service drop/lateral; multiple sets only with specific conditions"},
        {"section": "230.42", "title": "Minimum Size and Rating of Service-Entrance Conductors", "summary": "Sized for the calculated load per Art 220 with 125% continuous; minimum #8 AWG copper or #6 AWG aluminium"},
        {"section": "230.70", "title": "Service Disconnecting Means — General", "summary": "Service disconnect at readily accessible location, outdoors or near point of entrance"},
        {"section": "230.71", "title": "Number of Disconnects", "summary": "Maximum 6 service disconnects per service (the 6-handle rule); 2020+ requires that the 6 disconnects be grouped with a single connecting strap"},
        {"section": "230.85", "title": "Emergency Disconnects (NEW in NEC 2020/2023)", "summary": "Outside emergency disconnect required for one- and two-family dwellings, located readily accessible to first responders, marked accordingly"},
        {"section": "230.95", "title": "Ground-Fault Protection of Equipment (GFP at Service)", "summary": "GFP required for service disconnect rated ≥1000 A, more than 150 V to ground, less than 600 V phase-to-phase. Setting ≤1200 A; performance test required after installation"}
      ],
      "tabulated_values": {
        "minimum_service_size_230_42": "see tables_inline"
      },
      "tables_inline": {
        "Min_Service_Conductor_Size": {
          "title": "Minimum Service-Entrance Conductor Size (NEC 230.42)",
          "rows": [
            {"copper_awg": "8",   "aluminium_awg": "6",   "applies_to": "Minimum allowed regardless of calculated load"},
            {"copper_awg": "6",   "aluminium_awg": "4",   "applies_to": "Calculated load up to 50 A"},
            {"copper_awg": "4",   "aluminium_awg": "2",   "applies_to": "Calculated load 51-70 A"}
          ],
          "_note": "Above 70 A, size per Table 310.16 ampacity for the service-entrance temperature column (typically 75 °C for stripped insulation termination)"
        }
      },
      "common_errors": [
        "Specifying 7 service disconnects — 230.71 limits to 6",
        "Missing the outside emergency disconnect for new one- and two-family dwellings (added in NEC 2020) — readily accessible to first responders",
        "Missing GFP at services ≥1000 A (230.95) on a new commercial main service",
        "Forgetting the GFP performance test (230.95(C)) — required after installation"
      ],
      "drawn_as": ["ACB_3P", "MCCB_3P", "ENERGY_METER"],
      "related_iec_60364": ["IEC 60364-1 Clause 14 (Origin of installation)", "IEC 60364-5-53 (Switchgear)"],
      "divergence_notes": "NEC's 'service' is a distinct legal/contractual concept (utility/customer boundary); IEC uses 'origin of installation'. NEC 230.71 6-handle rule has no IEC equivalent. NEC 230.85 outside emergency disconnect (2020+) is NEC-specific. NEC GFP at services (230.95) is functionally similar to IEC residual-current monitoring at the main DB but NEC has explicit setpoint (≤1200 A) and performance-test requirement.",
      "related_bs_7671": [],
      "usage_notes": "For new dwellings in NEC 2020+ jurisdictions, ALWAYS show the outside emergency disconnect on the drawing. Confirm the AHJ has adopted the 2020 or 2023 edition (some still on 2017).",
      "related_articles": ["ART_215", "ART_220", "ART_240", "ART_250", "ART_310"]
    }
  ]
}
```

- [ ] **Step 2: Validate and commit**

```bash
python3 -c "import json; json.load(open('shared/standards/electrical/NFPA70/art230-services.json'))" && echo OK
git add shared/standards/electrical/NFPA70/art230-services.json
git commit -m "feat: NFPA70 art230-services.json — service conductors, 6-handle rule, GFP, emergency disconnect"
```

---

## Task 15: Create art240-overcurrent.json

**Files:**
- Create: `shared/standards/electrical/NFPA70/art240-overcurrent.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "NFPA 70 Article 240 — Overcurrent Protection",
  "_version": "1.0.0",
  "articles": [
    {
      "article_id": "ART_240",
      "nec_ref": "NFPA 70:2023 Article 240",
      "chapter": 2,
      "article_number": 240,
      "article_title": "Overcurrent Protection",
      "scope": "Overcurrent protection requirements for conductors and equipment — OCPD types, ratings, interrupting rating, conductor protection at 240.4, tap rules (240.21), location, series ratings, selective coordination (240.12).",
      "applies_to": ["overcurrent_protection", "fuses", "circuit_breakers", "tap_rules", "selective_coordination"],
      "key_sections": [
        {"section": "240.4",   "title": "Protection of Conductors", "summary": "Conductors protected at their ampacity (per Table 310.16 with 110.14(C) termination temp limit). 'Next higher size rule' (240.4(B)): standard OCPD just above conductor ampacity permitted if conductor ampacity is not a standard size and load ≤ conductor ampacity"},
        {"section": "240.6",   "title": "Standard Ampere Ratings", "summary": "Standard fuse and breaker ratings: 15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100, 110, 125, 150, 175, 200, 225, 250, 300, 350, 400, 450, 500, 600, 700, 800, 1000, 1200, 1600, 2000, 2500, 3000, 4000, 5000, 6000 A"},
        {"section": "240.12",  "title": "Electrical System Coordination", "summary": "Where coordination is required by 700.32, 701.32, 645.27, 695.6 — selective coordination across all OCPDs"},
        {"section": "240.21",  "title": "Location in Circuit (Tap Rules)", "summary": "10-foot tap (240.21(B)(1)), 25-foot tap (240.21(B)(2)), outside feeder tap (240.21(B)(5)), transformer secondary tap (240.21(C)) — common in commercial design"},
        {"section": "240.86",  "title": "Series Ratings", "summary": "Series-rated combinations permitted under specific conditions — tested combinations marked on the equipment"},
        {"section": "240.87",  "title": "Arc Energy Reduction", "summary": "Required for circuit breakers rated ≥1200 A — methods include zone-selective interlocking, differential relaying, energy-reducing maintenance switching, or instantaneous trip with adjustable settings"}
      ],
      "tabulated_values": {
        "standard_ratings_240_6": "see tables_inline"
      },
      "tables_inline": {
        "Standard_Ampere_Ratings_240.6": {
          "title": "Standard Fuse and Circuit Breaker Ratings (A)",
          "rows": [
            {"low": 15, "high": 50,  "values": "15, 20, 25, 30, 35, 40, 45, 50"},
            {"low": 60, "high": 100, "values": "60, 70, 80, 90, 100"},
            {"low": 110,"high": 200, "values": "110, 125, 150, 175, 200"},
            {"low": 225,"high": 600, "values": "225, 250, 300, 350, 400, 450, 500, 600"},
            {"low": 700,"high": 1200,"values": "700, 800, 1000, 1200"},
            {"low": 1600,"high": 6000,"values": "1600, 2000, 2500, 3000, 4000, 5000, 6000"}
          ]
        },
        "Tap_Rules_240.21": {
          "title": "Feeder Tap Conductor Rules (selected)",
          "rows": [
            {"tap_rule": "10-foot (240.21(B)(1))", "max_length_ft": 10,  "tap_ampacity_min": "1/10 of feeder OCPD rating"},
            {"tap_rule": "25-foot (240.21(B)(2))", "max_length_ft": 25,  "tap_ampacity_min": "1/3 of feeder OCPD rating"},
            {"tap_rule": "Outside feeder (240.21(B)(5))", "max_length_ft": "unlimited", "tap_ampacity_min": "no length limit if outside building"},
            {"tap_rule": "Transformer secondary (240.21(C))", "max_length_ft": "varies",  "tap_ampacity_min": "per 240.21(C)(2-6) based on tap length and primary protection"}
          ]
        }
      },
      "common_errors": [
        "Using 240.4(B) next-higher-size rule on continuous-duty circuits — only permitted for circuits where conductor ampacity is not a standard size AND load ≤ conductor ampacity",
        "Violating 10-ft or 25-ft tap rules by ignoring physical raceway length",
        "Treating series-rated combinations (240.86) as interchangeable — only the specific marked combinations are permitted; the equipment manufacturer's listing controls",
        "Missing arc-energy reduction (240.87) on circuit breakers ≥1200 A — added in NEC 2014, expanded in 2020 and 2023"
      ],
      "drawn_as": ["MCB_1P", "MCB_3P", "MCCB_3P", "ACB_3P", "FUSE_1P"],
      "related_iec_60364": ["IEC 60364-4-43 (Protection against overcurrent)", "IEC 60364-5-53 Clause 533 (Devices for protection against overcurrent)"],
      "divergence_notes": "NEC's 'standard ratings' (240.6) are imperial-A values; IEC has its own preferred-value series. NEC 240.21 tap rules (10-ft, 25-ft, outside, transformer-secondary) have no direct IEC equivalent — IEC handles via Iz/Z calculations for protection effectiveness at the tap end. NEC 240.86 series ratings are common; IEC permits cascading (IEC 60364-4-43 Annex D) but more cautious. NEC 240.87 arc-energy reduction (≥1200 A) has no IEC equivalent.",
      "related_bs_7671": [],
      "usage_notes": "Tap rules (240.21) are the #1 source of inspection failures on commercial feeder designs — always document tap length and conductor ampacity on the schedule.",
      "related_articles": ["ART_210", "ART_215", "ART_310", "ART_408", "ART_695", "ART_700"]
    }
  ]
}
```

- [ ] **Step 2: Validate and commit**

```bash
python3 -c "import json; json.load(open('shared/standards/electrical/NFPA70/art240-overcurrent.json'))" && echo OK
git add shared/standards/electrical/NFPA70/art240-overcurrent.json
git commit -m "feat: NFPA70 art240-overcurrent.json — OCPD ratings, tap rules, series ratings, arc energy reduction"
```

---

## Task 16: Create art250-grounding-bonding.json

**Files:**
- Create: `shared/standards/electrical/NFPA70/art250-grounding-bonding.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "NFPA 70 Article 250 — Grounding and Bonding",
  "_version": "1.0.0",
  "articles": [
    {
      "article_id": "ART_250",
      "nec_ref": "NFPA 70:2023 Article 250",
      "chapter": 2,
      "article_number": 250,
      "article_title": "Grounding and Bonding",
      "scope": "System grounding, equipment grounding, grounding electrode system (GES), bonding. The most cross-jurisdiction-divergent NEC article — NEC uses 'grounding' terminology where IEC uses 'earthing'.",
      "applies_to": ["all_systems", "service_grounded", "separately_derived", "gec", "egc", "bonding"],
      "key_sections": [
        {"section": "250.4",   "title": "General Requirements for Grounding and Bonding", "summary": "Performance-based: effective ground-fault current path with low impedance; bonding of equipment, structural metal, piping systems"},
        {"section": "250.20",  "title": "AC Systems to Be Grounded", "summary": "Systems supplying premises wiring under 1000 V to be grounded if any of: (1) phase-to-ground < 150 V, (2) star-connected 4-wire, (3) delta with one phase grounded"},
        {"section": "250.28",  "title": "Main Bonding Jumper (MBJ)", "summary": "Connection between grounded service conductor and EGC at service. Sized per 250.28(D)"},
        {"section": "250.30",  "title": "Grounding Separately Derived Alternating-Current Systems", "summary": "SDS (transformer secondary, generator output, etc.) grounded at the first system disconnect; system bonding jumper required"},
        {"section": "250.50",  "title": "Grounding Electrode System", "summary": "All electrode types present at the building must be bonded together: metal underground water pipe (≥10 ft), concrete-encased electrode (Ufer), ground ring, rod/pipe/plate, structural metal"},
        {"section": "250.52",  "title": "Grounding Electrodes", "summary": "Permitted types and specifications"},
        {"section": "250.66",  "title": "Size of Alternating-Current Grounding Electrode Conductor (GEC)", "summary": "GEC sized by largest ungrounded service conductor via Table 250.66"},
        {"section": "250.118", "title": "Types of Equipment Grounding Conductors (EGC)", "summary": "Permitted EGC types: copper wire, aluminium wire, RMC, IMC, EMT (qualified), flexible metal conduit (qualified by length and size), etc."},
        {"section": "250.122", "title": "Size of Equipment Grounding Conductors", "summary": "EGC sized by upstream OCPD rating via Table 250.122 — the NEC equivalent of BS 7671 Table 54.7 / IEC 60364-5-54 Table 54.1"},
        {"section": "250.142", "title": "Use of Grounded Circuit Conductor for Grounding Equipment", "summary": "TN-C concept permitted ONLY within service equipment (and on the supply side of the service disconnect). After service disconnect, neutral and EGC must be separate (the NEC's 'no TN-C downstream' rule)"}
      ],
      "tabulated_values": {
        "gec_sizing_table_250_66": "see tables_inline",
        "egc_sizing_table_250_122": "see tables_inline"
      },
      "tables_inline": {
        "Table_250.66_GEC_for_AC_Systems": {
          "title": "Grounding Electrode Conductor for AC Systems",
          "rows": [
            {"largest_ungrounded_cu_awg": "2 or smaller",          "gec_cu_awg": "8"},
            {"largest_ungrounded_cu_awg": "1 or 1/0",              "gec_cu_awg": "6"},
            {"largest_ungrounded_cu_awg": "2/0 or 3/0",            "gec_cu_awg": "4"},
            {"largest_ungrounded_cu_awg": "over 3/0 to 350 kcmil", "gec_cu_awg": "2"},
            {"largest_ungrounded_cu_awg": "over 350 to 600 kcmil", "gec_cu_awg": "1/0"},
            {"largest_ungrounded_cu_awg": "over 600 to 1100 kcmil","gec_cu_awg": "2/0"},
            {"largest_ungrounded_cu_awg": "over 1100 kcmil",       "gec_cu_awg": "3/0"}
          ]
        },
        "Table_250.122_EGC_for_Equipment_Grounding": {
          "title": "Minimum Size Equipment Grounding Conductors for Grounding Raceway and Equipment",
          "rows": [
            {"ocpd_rating_a": 15,   "cu_egc_awg": "14",  "al_egc_awg": "12"},
            {"ocpd_rating_a": 20,   "cu_egc_awg": "12",  "al_egc_awg": "10"},
            {"ocpd_rating_a": 30,   "cu_egc_awg": "10",  "al_egc_awg": "8"},
            {"ocpd_rating_a": 40,   "cu_egc_awg": "10",  "al_egc_awg": "8"},
            {"ocpd_rating_a": 60,   "cu_egc_awg": "10",  "al_egc_awg": "8"},
            {"ocpd_rating_a": 100,  "cu_egc_awg": "8",   "al_egc_awg": "6"},
            {"ocpd_rating_a": 200,  "cu_egc_awg": "6",   "al_egc_awg": "4"},
            {"ocpd_rating_a": 300,  "cu_egc_awg": "4",   "al_egc_awg": "2"},
            {"ocpd_rating_a": 400,  "cu_egc_awg": "3",   "al_egc_awg": "1"},
            {"ocpd_rating_a": 500,  "cu_egc_awg": "2",   "al_egc_awg": "1/0"},
            {"ocpd_rating_a": 600,  "cu_egc_awg": "1",   "al_egc_awg": "2/0"},
            {"ocpd_rating_a": 800,  "cu_egc_awg": "1/0", "al_egc_awg": "3/0"},
            {"ocpd_rating_a": 1000, "cu_egc_awg": "2/0", "al_egc_awg": "4/0"},
            {"ocpd_rating_a": 1200, "cu_egc_awg": "3/0", "al_egc_awg": "250 kcmil"},
            {"ocpd_rating_a": 1600, "cu_egc_awg": "4/0", "al_egc_awg": "350 kcmil"},
            {"ocpd_rating_a": 2000, "cu_egc_awg": "250 kcmil", "al_egc_awg": "400 kcmil"},
            {"ocpd_rating_a": 2500, "cu_egc_awg": "350 kcmil", "al_egc_awg": "600 kcmil"},
            {"ocpd_rating_a": 3000, "cu_egc_awg": "400 kcmil", "al_egc_awg": "600 kcmil"},
            {"ocpd_rating_a": 4000, "cu_egc_awg": "500 kcmil", "al_egc_awg": "750 kcmil"},
            {"ocpd_rating_a": 5000, "cu_egc_awg": "700 kcmil", "al_egc_awg": "1200 kcmil"},
            {"ocpd_rating_a": 6000, "cu_egc_awg": "800 kcmil", "al_egc_awg": "1200 kcmil"}
          ]
        }
      },
      "common_errors": [
        "Confusing GEC (250.66, sized by ungrounded conductor) with EGC (250.122, sized by OCPD rating) — DIFFERENT sizing rules",
        "Sizing EGC from breaker rating alone instead of larger of: 250.122 table OR adiabatic check per 250.122(B) for parallel/upsized conductors",
        "Bonding neutral to ground at sub-panels — illegal except at service or first disconnect of separately derived system (250.142)",
        "Treating concrete-encased electrode (Ufer) as optional — required when present per 250.50(A)(3)",
        "Failing to bond ALL present electrodes (250.50) — water pipe + Ufer + ground rod + ring + structural steel all must be bonded together"
      ],
      "drawn_as": ["EARTH_GENERAL", "EARTH_ELECTRODE", "CONDUCTOR_PE"],
      "related_iec_60364": ["IEC 60364-5-54 (Earthing arrangements and protective conductors)", "IEC 60364-5-54 Table 54.1 (CPC sizing)", "IEC 60364-5-54 Clause 541 (Earthing arrangements)"],
      "divergence_notes": "NEC uses 'grounding' / 'grounded conductor' / 'EGC' where IEC uses 'earthing' / 'neutral' / 'CPC'. NEC EGC sizes from 250.122 by OCPD rating; IEC 60364-5-54 sizes from line-conductor CSA (Table 54.1) OR adiabatic — same circuit yields different EGC/CPC under the two codes. NEC requires concrete-encased electrode (Ufer) when present (250.50(A)(3)); IEC does not mandate. NEC permits TN-C only within service equipment (250.142); IEC permits TN-C throughout for cables ≥10 mm² Cu / 16 mm² Al. NEC GEC sizing (250.66 — by ungrounded conductor) has no IEC analogue — IEC sizes main earthing conductor adiabatically. See nec-vs-iec-comparison.md and grounding-and-bonding.json for the full divergence catalogue.",
      "related_bs_7671": [],
      "usage_notes": "The most cited NEC article in MEP design. Always confirm AHJ acceptance of the grounding electrode arrangement before issue. Specify EGC type (insulated/bare/raceway) per 250.118 and size per 250.122 with adiabatic verification (250.122(B)) for short cable runs with high fault current. For separately-derived systems, the system bonding jumper at the SDS replaces the MBJ function — see 250.30.",
      "related_articles": ["ART_200", "ART_300", "ART_310", "ART_408", "ART_450"]
    }
  ]
}
```

- [ ] **Step 2: Validate and commit**

```bash
python3 -c "import json; json.load(open('shared/standards/electrical/NFPA70/art250-grounding-bonding.json'))" && echo OK
git add shared/standards/electrical/NFPA70/art250-grounding-bonding.json
git commit -m "feat: NFPA70 art250-grounding-bonding.json — GEC, EGC, GES, MBJ, divergence with IEC 60364-5-54"
```

---

## Task 17: Create art310-conductor-ampacity.json

**Files:**
- Create: `shared/standards/electrical/NFPA70/art310-conductor-ampacity.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "NFPA 70 Article 310 — Conductors for General Wiring",
  "_version": "1.0.0",
  "articles": [
    {
      "article_id": "ART_310",
      "nec_ref": "NFPA 70:2023 Article 310",
      "chapter": 3,
      "article_number": 310,
      "article_title": "Conductors for General Wiring",
      "scope": "Conductor types and markings, ampacity tables (310.16 raceway/cable, 310.17 free air), correction factors for ambient (Table 310.15(B)(1)) and grouping (Table 310.15(C)(1)), 60/75/90 °C termination temperature limit from 110.14(C).",
      "applies_to": ["conductors", "ampacity", "ambient_correction", "grouping_correction", "termination_temperature_limit"],
      "key_sections": [
        {"section": "310.6",   "title": "Conductor Construction and Applications", "summary": "Common conductor types: THWN-2/THHN (90 °C dry, 75 °C wet), XHHW-2 (90 °C dry/wet), USE-2 (90 °C, underground service), RHH/RHW (rubber). Use the lowest-rated termination temp limits ampacity"},
        {"section": "310.15",  "title": "Ampacities for Conductors Rated 0-2000 V", "summary": "General ampacity rules; correction factors for ambient temperature (310.15(B)(1)) and number of current-carrying conductors (310.15(C)(1))"},
        {"section": "310.16",  "title": "Ampacity Table — Conductors in Raceway, Cable, or Earth (≤3 current-carrying)", "summary": "Primary ampacity table for raceway/cable installations"},
        {"section": "310.17",  "title": "Ampacity Table — Free Air", "summary": "Single insulated conductors in free air; higher ampacity than raceway"}
      ],
      "tabulated_values": {
        "ampacity_table_310_16": "see tables_inline",
        "ambient_temp_correction_310_15_B_1": "see tables_inline",
        "grouping_correction_310_15_C_1": "see tables_inline"
      },
      "tables_inline": {
        "Table_310.16_Ampacity_Raceway_Cable_Cu": {
          "title": "Ampacity (A) — Copper, ≤3 Current-Carrying Conductors in Raceway/Cable, 30 °C Ambient",
          "rows": [
            {"size_awg_kcmil": 14,    "tw_60c": 15,  "thw_75c": 20,  "thhn_thwn_90c": 25},
            {"size_awg_kcmil": 12,    "tw_60c": 20,  "thw_75c": 25,  "thhn_thwn_90c": 30},
            {"size_awg_kcmil": 10,    "tw_60c": 30,  "thw_75c": 35,  "thhn_thwn_90c": 40},
            {"size_awg_kcmil": 8,     "tw_60c": 40,  "thw_75c": 50,  "thhn_thwn_90c": 55},
            {"size_awg_kcmil": 6,     "tw_60c": 55,  "thw_75c": 65,  "thhn_thwn_90c": 75},
            {"size_awg_kcmil": 4,     "tw_60c": 70,  "thw_75c": 85,  "thhn_thwn_90c": 95},
            {"size_awg_kcmil": 3,     "tw_60c": 85,  "thw_75c": 100, "thhn_thwn_90c": 115},
            {"size_awg_kcmil": 2,     "tw_60c": 95,  "thw_75c": 115, "thhn_thwn_90c": 130},
            {"size_awg_kcmil": 1,     "tw_60c": 110, "thw_75c": 130, "thhn_thwn_90c": 145},
            {"size_awg_kcmil": "1/0", "tw_60c": 125, "thw_75c": 150, "thhn_thwn_90c": 170},
            {"size_awg_kcmil": "2/0", "tw_60c": 145, "thw_75c": 175, "thhn_thwn_90c": 195},
            {"size_awg_kcmil": "3/0", "tw_60c": 165, "thw_75c": 200, "thhn_thwn_90c": 225},
            {"size_awg_kcmil": "4/0", "tw_60c": 195, "thw_75c": 230, "thhn_thwn_90c": 260},
            {"size_awg_kcmil": 250,   "tw_60c": 215, "thw_75c": 255, "thhn_thwn_90c": 290},
            {"size_awg_kcmil": 300,   "tw_60c": 240, "thw_75c": 285, "thhn_thwn_90c": 320},
            {"size_awg_kcmil": 350,   "tw_60c": 260, "thw_75c": 310, "thhn_thwn_90c": 350},
            {"size_awg_kcmil": 400,   "tw_60c": 280, "thw_75c": 335, "thhn_thwn_90c": 380},
            {"size_awg_kcmil": 500,   "tw_60c": 320, "thw_75c": 380, "thhn_thwn_90c": 430},
            {"size_awg_kcmil": 600,   "tw_60c": 350, "thw_75c": 420, "thhn_thwn_90c": 475},
            {"size_awg_kcmil": 750,   "tw_60c": 400, "thw_75c": 475, "thhn_thwn_90c": 535},
            {"size_awg_kcmil": 1000,  "tw_60c": 455, "thw_75c": 545, "thhn_thwn_90c": 615}
          ]
        },
        "Table_310.15(B)(1)_Ambient_Temperature_Correction": {
          "title": "Ambient Temperature Correction Factors (apply to ampacity tables based on 30 °C ambient)",
          "rows": [
            {"ambient_temp_c": "≤10",   "60c_factor": 1.29, "75c_factor": 1.20, "90c_factor": 1.15},
            {"ambient_temp_c": "11-15", "60c_factor": 1.22, "75c_factor": 1.15, "90c_factor": 1.12},
            {"ambient_temp_c": "16-20", "60c_factor": 1.15, "75c_factor": 1.11, "90c_factor": 1.08},
            {"ambient_temp_c": "21-25", "60c_factor": 1.08, "75c_factor": 1.05, "90c_factor": 1.04},
            {"ambient_temp_c": "26-30", "60c_factor": 1.00, "75c_factor": 1.00, "90c_factor": 1.00},
            {"ambient_temp_c": "31-35", "60c_factor": 0.91, "75c_factor": 0.94, "90c_factor": 0.96},
            {"ambient_temp_c": "36-40", "60c_factor": 0.82, "75c_factor": 0.88, "90c_factor": 0.91},
            {"ambient_temp_c": "41-45", "60c_factor": 0.71, "75c_factor": 0.82, "90c_factor": 0.87},
            {"ambient_temp_c": "46-50", "60c_factor": 0.58, "75c_factor": 0.75, "90c_factor": 0.82},
            {"ambient_temp_c": "51-55", "60c_factor": 0.41, "75c_factor": 0.67, "90c_factor": 0.76},
            {"ambient_temp_c": "56-60", "60c_factor": "—", "75c_factor": 0.58, "90c_factor": 0.71},
            {"ambient_temp_c": "61-70", "60c_factor": "—", "75c_factor": 0.33, "90c_factor": 0.58},
            {"ambient_temp_c": "71-80", "60c_factor": "—", "75c_factor": "—", "90c_factor": 0.41}
          ]
        },
        "Table_310.15(C)(1)_Adjustment_for_More_Than_3_Conductors": {
          "title": "Adjustment Factors for More Than Three Current-Carrying Conductors",
          "rows": [
            {"num_current_carrying": "4-6",   "percent_ampacity": 80},
            {"num_current_carrying": "7-9",   "percent_ampacity": 70},
            {"num_current_carrying": "10-20", "percent_ampacity": 50},
            {"num_current_carrying": "21-30", "percent_ampacity": 45},
            {"num_current_carrying": "31-40", "percent_ampacity": 40},
            {"num_current_carrying": "≥41",   "percent_ampacity": 35}
          ]
        }
      },
      "common_errors": [
        "Using the 90 °C ampacity column when terminations are 75 °C rated — must use the 75 °C column per 110.14(C)",
        "Forgetting to apply both ambient correction AND grouping adjustment when both conditions exist — they multiply (not add)",
        "Treating neutral conductors as non-current-carrying for the grouping count — neutrals carrying unbalanced current count; in linear loads of single-phase 3-wire or 3-phase 4-wire, neutral typically does NOT count; in non-linear (harmonic) loads, neutral DOES count per 310.15(E)",
        "Sizing the conductor based on ampacity after correction but forgetting 110.14(C) termination limit ends up REDUCING the answer further"
      ],
      "drawn_as": [],
      "related_iec_60364": ["IEC 60364-5-52 (Wiring systems — current-carrying capacity)", "IEC 60364-5-52 Annex B (Ampacity tables)"],
      "divergence_notes": "NEC ampacity tables use AWG/kcmil with three temperature-rating columns (60/75/90 °C); IEC Annex B uses mm² and named insulation types (PVC/XLPE/EPR) with reference installation methods (A1/A2/B1/B2/C/D/E/F). NEC's 110.14(C) termination temperature limit has no IEC equivalent — IEC ampacity tables assume terminations are rated to match conductor. NEC ambient correction is per Table 310.15(B)(1); IEC Annex B Tables B.52.14 / B.52.15. NEC grouping adjustment per Table 310.15(C)(1) (4-6: 80%, 7-9: 70%, etc.); IEC has similar but slightly different multipliers in Annex B.",
      "related_bs_7671": [],
      "usage_notes": "Always state on the schedule: (1) conductor type (THHN/THWN-2/XHHW-2), (2) termination temperature rating (60/75/90 °C), (3) ambient temperature, (4) number of current-carrying conductors. Without these four, ampacity is ambiguous.",
      "related_articles": ["ART_110", "ART_220", "ART_240", "ART_300"]
    }
  ]
}
```

- [ ] **Step 2: Validate and commit**

```bash
python3 -c "import json; json.load(open('shared/standards/electrical/NFPA70/art310-conductor-ampacity.json'))" && echo OK
git add shared/standards/electrical/NFPA70/art310-conductor-ampacity.json
git commit -m "feat: NFPA70 art310-conductor-ampacity.json — Table 310.16, ambient + grouping correction"
```

---

## Task 18: Create art408-panelboards.json

**Files:**
- Create: `shared/standards/electrical/NFPA70/art408-panelboards.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "NFPA 70 Article 408 — Switchboards, Switchgear, and Panelboards",
  "_version": "1.0.0",
  "articles": [
    {
      "article_id": "ART_408",
      "nec_ref": "NFPA 70:2023 Article 408",
      "chapter": 4,
      "article_number": 408,
      "article_title": "Switchboards, Switchgear, and Panelboards",
      "scope": "Switchboards, switchgear (rated up to 6000 V — Class IIIA), and panelboards (≤1000 V, typically ≤600 V). Classifications, ratings, OCPD count limits, working clearances (cross-ref 110.26).",
      "applies_to": ["switchboards", "switchgear", "panelboards", "lighting_panelboard", "power_panelboard"],
      "key_sections": [
        {"section": "408.4",  "title": "Field Identification Required", "summary": "Panelboards/switchboards marked with: max OCPD ahead, SCCR, voltage rating, manufacturer, equipment description, available fault current"},
        {"section": "408.30", "title": "General — Panelboards", "summary": "Panelboard rating ≥ minimum feeder rating; rated for short-circuit current available"},
        {"section": "408.36", "title": "Overcurrent Protection — Panelboards", "summary": "Panelboard with OCPDs sums ≥ panelboard rating: each panelboard requires individual OCPD protection on the feeder ahead, sized ≤ panelboard rating. (Maximum 42 OCPDs rule was removed in NEC 2008 — modern panelboards are rated by ampere/voltage, not by OCPD count)"},
        {"section": "408.41", "title": "Grounded Conductor Terminations", "summary": "Each grounded (neutral) conductor terminated in an individual terminal that is not also used for another conductor"}
      ],
      "tabulated_values": {},
      "tables_inline": {},
      "common_errors": [
        "Sharing a neutral termination among multiple branch circuits — 408.41 requires individual termination per neutral",
        "Specifying a 42-circuit panelboard limit in modern designs — that rule was removed in NEC 2008; the limit is by panelboard rating, not OCPD count",
        "Failing to mark available fault current at the panelboard (408.4(C)) — required for any equipment expected to be replaced/serviced",
        "Treating switchgear and switchboards as interchangeable — 'switchgear' (per NEMA SG-3) is metal-enclosed, drawout-rated, generally higher SCCR; 'switchboard' is less stringent"
      ],
      "drawn_as": ["PANELBOARD", "SWITCHBOARD", "MCC"],
      "related_iec_60364": ["IEC 60364-5-53 (Switchgear)", "IEC 61439-1/2/3 (Low-voltage switchgear assemblies — see existing IEC61439/ layer)"],
      "divergence_notes": "NEC 408 + UL 67 (panelboards) + UL 891 (switchboards) ≈ IEC 61439 series — see existing IEC61439/ layer for the comprehensive IEC treatment of assemblies. NEC's 'panelboard vs switchboard vs switchgear' classification is distinct from IEC's PSC-Assembly/DBO-Assembly classification. NEC 408.4(C) field-marking of available fault current is more prescriptive than IEC equivalent.",
      "related_bs_7671": [],
      "usage_notes": "Cross-reference the existing IEC61439/ layer when working bi-jurisdiction projects — `divergence_notes` in art500-506-hazardous-locations.json and art250-grounding-bonding.json reference IEC 61439 indirectly through specific assembly types.",
      "related_articles": ["ART_110", "ART_240", "ART_250", "ART_312_314"]
    }
  ]
}
```

- [ ] **Step 2: Validate and commit**

```bash
python3 -c "import json; json.load(open('shared/standards/electrical/NFPA70/art408-panelboards.json'))" && echo OK
git add shared/standards/electrical/NFPA70/art408-panelboards.json
git commit -m "feat: NFPA70 art408-panelboards.json — panelboard/switchboard ratings, marking, IEC 61439 link"
```

---

## Task 19: Create art430-motors.json

**Files:**
- Create: `shared/standards/electrical/NFPA70/art430-motors.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "NFPA 70 Article 430 — Motors, Motor Circuits, and Controllers",
  "_version": "1.0.0",
  "articles": [
    {
      "article_id": "ART_430",
      "nec_ref": "NFPA 70:2023 Article 430",
      "chapter": 4,
      "article_number": 430,
      "article_title": "Motors, Motor Circuits, and Controllers",
      "scope": "Motor branch-circuit conductor sizing (430.22, 430.24), motor short-circuit/ground-fault protection (430.52), motor overload (430.32), motor controller (430.81), motor disconnect (430.102), motor control centres (430.94+).",
      "applies_to": ["motors", "single_motor", "multiple_motors", "motor_controllers", "mcc"],
      "key_sections": [
        {"section": "430.6",   "title": "Ampacity and Motor Rating Determination", "summary": "Use Tables 430.247 / 430.248 / 430.250 / 430.251 (full-load currents) for single-motor branch circuits; use nameplate for thermal overload"},
        {"section": "430.22",  "title": "Single Motor — Conductors", "summary": "Branch-circuit conductors ≥ 125% × motor FLA from Table 430.250 (3-phase) or 430.248 (single-phase)"},
        {"section": "430.24",  "title": "Several Motors or Motors plus Other Loads", "summary": "Conductors ≥ 125% × largest motor FLA + 100% × other motors' FLA + 100% × non-motor loads"},
        {"section": "430.32",  "title": "Continuous-Duty Motors — Overload Protection", "summary": "Overload sized at 115% to 125% of motor nameplate FLA (Service Factor and motor type dependent)"},
        {"section": "430.52",  "title": "Motor Branch-Circuit Short-Circuit and Ground-Fault Protection", "summary": "OCPD sized by Table 430.52(C)(1) percentage: typical 250% inverse-time breaker / 300% non-time-delay fuse / 175% dual-element time-delay fuse / 800% instantaneous-trip breaker (all of motor FLA from Table 430.250)"},
        {"section": "430.102", "title": "Disconnecting Means", "summary": "Disconnect within sight of the controller AND within sight of the motor (or lockable disconnect within sight of controller meets both)"}
      ],
      "tabulated_values": {
        "full_load_3phase_motors_430_250": "see tables_inline",
        "branch_circuit_protection_percentage_430_52": "see tables_inline"
      },
      "tables_inline": {
        "Table_430.250_Full_Load_Current_3-phase_AC_Motors": {
          "title": "Full-Load Current (A) — Three-Phase AC Motors at 460 V (selected)",
          "_note": "For sizing branch-circuit conductors and OCPDs. Always use TABLE FLA (not nameplate FLA) for these calculations.",
          "rows": [
            {"hp": 1,    "fla_460v": 2.1},
            {"hp": 2,    "fla_460v": 3.4},
            {"hp": 3,    "fla_460v": 4.8},
            {"hp": 5,    "fla_460v": 7.6},
            {"hp": 7.5,  "fla_460v": 11},
            {"hp": 10,   "fla_460v": 14},
            {"hp": 15,   "fla_460v": 21},
            {"hp": 20,   "fla_460v": 27},
            {"hp": 25,   "fla_460v": 34},
            {"hp": 30,   "fla_460v": 40},
            {"hp": 40,   "fla_460v": 52},
            {"hp": 50,   "fla_460v": 65},
            {"hp": 60,   "fla_460v": 77},
            {"hp": 75,   "fla_460v": 96},
            {"hp": 100,  "fla_460v": 124},
            {"hp": 125,  "fla_460v": 156},
            {"hp": 150,  "fla_460v": 180},
            {"hp": 200,  "fla_460v": 240}
          ]
        },
        "Table_430.52(C)(1)_Branch_Circuit_OCPD_Percentage": {
          "title": "Maximum Branch-Circuit OCPD as % of Motor FLA",
          "rows": [
            {"motor_type": "Single-phase / Polyphase squirrel-cage / Synchronous", "nontime_delay_fuse_pct": 300, "dual_element_fuse_pct": 175, "instantaneous_breaker_pct": 800, "inverse_time_breaker_pct": 250},
            {"motor_type": "Wound-rotor",                                         "nontime_delay_fuse_pct": 150, "dual_element_fuse_pct": 150, "instantaneous_breaker_pct": 800, "inverse_time_breaker_pct": 150},
            {"motor_type": "Direct current",                                      "nontime_delay_fuse_pct": 150, "dual_element_fuse_pct": 150, "instantaneous_breaker_pct": 250, "inverse_time_breaker_pct": 150}
          ]
        }
      },
      "common_errors": [
        "Using nameplate FLA for branch-circuit conductor sizing — must use Table 430.250 FLA (430.6(A)(1))",
        "Using Table 430.250 FLA for overload sizing — must use nameplate FLA (430.6(A)(2))",
        "Sizing OCPD at 100% of motor FLA — motor must be sized at 250% (inverse-time breaker) or 175% (dual-element fuse) to handle starting inrush",
        "Disconnect not within sight of motor — 430.102(B) violation. 'Within sight' = visible from one location to the other AND ≤50 ft apart"
      ],
      "drawn_as": ["MOTOR", "MOTOR_STARTER", "MOTOR_DISCONNECT"],
      "related_iec_60364": ["IEC 60364-5-55 Clause 559.5 (Motors)", "IEC 60204-1 (Safety of machinery — electrical equipment of machines)"],
      "divergence_notes": "NEC Art 430 uses horsepower-based FLA tables (430.247-251) and a percentage-based OCPD sizing rule (430.52). IEC sizes motors per actual rated current with diversity factors and protective-device coordination per IEC 60364-5-53. NEC's 'within sight' disconnect rule (430.102) has no IEC equivalent — IEC requires accessible local isolation but does not specify sightline.",
      "related_bs_7671": [],
      "usage_notes": "Always cite TABLE FLA when sizing conductors/OCPDs and NAMEPLATE FLA when sizing overloads. Confusing the two is the #1 motor-circuit inspection failure.",
      "related_articles": ["ART_240", "ART_310", "ART_440", "ART_670"]
    }
  ]
}
```

- [ ] **Step 2: Validate and commit**

```bash
python3 -c "import json; json.load(open('shared/standards/electrical/NFPA70/art430-motors.json'))" && echo OK
git add shared/standards/electrical/NFPA70/art430-motors.json
git commit -m "feat: NFPA70 art430-motors.json — motor circuit sizing, OCPD, overload, disconnect"
```

---

## Task 20: Create art450-transformers.json

**Files:**
- Create: `shared/standards/electrical/NFPA70/art450-transformers.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "NFPA 70 Article 450 — Transformers and Transformer Vaults",
  "_version": "1.0.0",
  "articles": [
    {
      "article_id": "ART_450",
      "nec_ref": "NFPA 70:2023 Article 450",
      "chapter": 4,
      "article_number": 450,
      "article_title": "Transformers and Transformer Vaults",
      "scope": "Transformer installation, overcurrent protection, primary and secondary connections, vault construction. Transformer classifications: dry-type, oil-insulated, less-flammable-liquid (FR3 etc.), askarel (legacy/banned).",
      "applies_to": ["transformers", "dry_type", "oil_filled", "transformer_vault", "primary_protection", "secondary_protection"],
      "key_sections": [
        {"section": "450.3", "title": "Overcurrent Protection", "summary": "Primary OCPD per Table 450.3(A) (>1000 V) or 450.3(B) (≤1000 V). Secondary OCPD often required to size feeder conductors per 240.21(C)"},
        {"section": "450.4", "title": "Autotransformer Protection", "summary": "Autotransformer OCPD sized differently from isolation transformer; based on input current rating"},
        {"section": "450.9", "title": "Ventilation", "summary": "Ventilation requirements for transformers; clearances per manufacturer + Code"},
        {"section": "450.21","title": "Dry-Type Transformer Installation (Indoor)", "summary": "≤112.5 kVA: any location. >112.5 kVA: 1-hour fire-resistant separation from combustibles (3-ft clearance from combustible building material if not in fire-rated room)"},
        {"section": "450.43","title": "Less-Flammable Liquid-Insulated Transformer Installation (Indoor)", "summary": "Indoor installation permitted with conditions: containment, ventilation, automatic fire suppression"},
        {"section": "450.46","title": "Liquid-Insulated Transformer Installation (Indoor)", "summary": "Mineral-oil-insulated transformer indoor only in approved vault per Part III"}
      ],
      "tabulated_values": {
        "primary_ocpd_lt_1000v_450_3_B": "see tables_inline"
      },
      "tables_inline": {
        "Table_450.3(B)_Primary_OCPD_for_Transformers_Rated_Up_to_1000_V": {
          "title": "Maximum Primary OCPD for Transformer ≤1000 V (% of primary rated current)",
          "_note": "Where only primary protection is provided (no secondary OCPD)",
          "rows": [
            {"primary_amps": "≥ 9", "primary_ocpd_max_pct": 125},
            {"primary_amps": "2-9", "primary_ocpd_max_pct": 167},
            {"primary_amps": "< 2", "primary_ocpd_max_pct": 300}
          ]
        }
      },
      "common_errors": [
        "Failing to provide secondary OCPD when feeder is sized per the secondary load — required for tap rule compliance per 240.21(C)",
        "Installing dry-type transformer >112.5 kVA in unrated room with combustibles — 450.21 violation",
        "Treating an autotransformer like an isolation transformer for OCPD sizing — 450.4 specifies different rules",
        "Specifying mineral-oil transformer indoor without a vault per Part III — only less-flammable-liquid (FR3, K-class, midel) is permitted indoor without vault"
      ],
      "drawn_as": ["TRANSFORMER_2W", "TRANSFORMER_3W"],
      "related_iec_60364": ["IEC 60364-5-55 (Other equipment) — limited treatment", "IEC 60076 series (Power transformers — primary reference)"],
      "divergence_notes": "NEC Art 450 handles installation; IEC defers to IEC 60076 (power transformer equipment) and 60364-5-55 (installation, limited). NEC's primary OCPD sizing rule (Table 450.3(B), 125% / 167% / 300% of primary current) has no direct IEC equivalent — IEC sizes based on Iz of the primary cable + transformer Icc.",
      "related_bs_7671": [],
      "usage_notes": "Confirm transformer type (dry / less-flammable-liquid / oil) early — determines whether vault is required.",
      "related_articles": ["ART_240", "ART_310", "ART_408"]
    }
  ]
}
```

- [ ] **Step 2: Validate and commit**

```bash
python3 -c "import json; json.load(open('shared/standards/electrical/NFPA70/art450-transformers.json'))" && echo OK
git add shared/standards/electrical/NFPA70/art450-transformers.json
git commit -m "feat: NFPA70 art450-transformers.json — primary/secondary OCPD, vault, indoor installation rules"
```

---

## Task 21: Create art500-506-hazardous-locations.json (bundle)

**Files:**
- Create: `shared/standards/electrical/NFPA70/art500-506-hazardous-locations.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "NFPA 70 Articles 500-506 — Hazardous (Classified) Locations",
  "_version": "1.0.0",
  "_note": "Bundle covering the Division system (legacy US — Arts 500-503) and the Zone system (IEC-aligned — Arts 505-506).",
  "articles": [
    {
      "article_id": "ART_500_506",
      "nec_ref": "NFPA 70:2023 Articles 500, 501, 502, 503, 504, 505, 506",
      "chapter": 5,
      "article_number": 500,
      "article_title": "Hazardous (Classified) Locations — Classes I, II, III (Division and Zone)",
      "scope": "Classification of locations where flammable gases (Class I), combustible dusts (Class II), or ignitible fibers/flyings (Class III) are present. TWO classification systems: Division system (NEC legacy — Class × Division 1/2 × Group A-G) and Zone system (IEC-aligned — Class I × Zone 0/1/2). Article 504 covers intrinsically safe (IS) systems.",
      "applies_to": ["hazardous_locations", "class_division", "class_zone", "intrinsically_safe", "explosionproof", "purge_pressurize"],
      "key_sections": [
        {"section": "500.5", "title": "Classifications of Locations", "summary": "Class I (gas/vapor): Division 1 (ignitible concentrations exist under normal conditions) and Division 2 (likely only under abnormal conditions). Class II (dust): Division 1/2 by similar logic. Class III (fibers): Division 1/2."},
        {"section": "500.6", "title": "Material Groups (Gas/Dust Groups)", "summary": "Class I Groups A-D (Group A: acetylene; B: hydrogen; C: ethylene; D: propane/gasoline). Class II Groups E-G (E: metal dust; F: carbon dust; G: combustible dust like grain). IEC IIA/IIB/IIC equivalents for gases, IIIA/IIIB/IIIC for dusts"},
        {"section": "500.8", "title": "Equipment Marking and Selection", "summary": "Equipment marked for the Class/Division/Group it's listed for. Equipment listed for Zone is generally accepted in Division locations of equivalent severity (with limits)"},
        {"section": "501",   "title": "Class I Locations (Gas/Vapor)", "summary": "Wiring methods, sealing, equipment for Class I"},
        {"section": "502",   "title": "Class II Locations (Combustible Dust)", "summary": "Wiring methods and equipment for Class II — dust-ignitionproof or dust-tight"},
        {"section": "503",   "title": "Class III Locations (Ignitible Fibers/Flyings)", "summary": "Generally less restrictive than I/II — covers textile mills, grain processing"},
        {"section": "504",   "title": "Intrinsically Safe Systems", "summary": "IS apparatus and associated apparatus per UL 913 / UL 60079-11. Loop calculation for entity parameters (Voc, Isc, Ca, La, Pi, Po, Ci, Li)"},
        {"section": "505",   "title": "Class I, Zone 0, 1, and 2 Locations (IEC-aligned)", "summary": "Alternative to 501. Zone 0 (continuously present), Zone 1 (occasionally), Zone 2 (only under abnormal conditions). IIA/IIB/IIC gas grouping"},
        {"section": "506",   "title": "Zone 20, 21, and 22 Locations (Combustible Dust)", "summary": "IEC-aligned dust classification. Zone 20 (dust cloud continuously), 21 (occasionally), 22 (abnormal only). IIIA/IIIB/IIIC dust grouping"}
      ],
      "tabulated_values": {
        "class_division_zone_mapping": "see tables_inline + see hazardous-locations-classification.json for full matrix"
      },
      "tables_inline": {
        "Class_vs_Division_vs_Zone_Quick_Reference": {
          "title": "Class/Division ↔ Class/Zone equivalence (severity-based)",
          "rows": [
            {"class_division": "Class I Division 1", "class_zone": "Class I Zone 0 + Zone 1 combined", "severity_note": "Division 1 is more severe than Zone 1 alone (Division 1 ≈ Zone 0 + 1)"},
            {"class_division": "Class I Division 2", "class_zone": "Class I Zone 2",                 "severity_note": "Direct equivalence"},
            {"class_division": "Class II Division 1","class_zone": "Zone 20 + Zone 21 combined",   "severity_note": ""},
            {"class_division": "Class II Division 2","class_zone": "Zone 22",                       "severity_note": ""}
          ]
        },
        "Gas_Group_Mapping_NEC_vs_IEC": {
          "title": "Gas Group Equivalence",
          "rows": [
            {"nec_group": "A (acetylene)", "iec_group": "IIC", "_note": "NEC Group A is more specific than IEC IIC; IIC covers acetylene + hydrogen + similar"},
            {"nec_group": "B (hydrogen)",   "iec_group": "IIC", "_note": "Group B equipment can typically be used in IIC locations and vice versa with caveats"},
            {"nec_group": "C (ethylene)",   "iec_group": "IIB", "_note": "Direct equivalence"},
            {"nec_group": "D (propane, gasoline)", "iec_group": "IIA", "_note": "Direct equivalence"}
          ]
        }
      },
      "common_errors": [
        "Mixing Division-marked equipment and Zone-marked equipment in the same location without confirming the conversion matrix",
        "Treating Class II Group G (grain dust) and Class II Group F (carbon dust) interchangeably — they have different ignition characteristics",
        "Omitting conduit seals where the boundary crosses from classified to unclassified — common 501.15 violation",
        "Using non-IS equipment in a Class I Div 1 location where the original design assumed an IS loop — IS calculation invalidated by component substitution"
      ],
      "drawn_as": ["EXPLOSION_PROOF_LUMINAIRE", "EXPLOSION_PROOF_RECEPTACLE"],
      "related_iec_60364": ["IEC 60079 series (Hazardous areas)", "IEC 60079-10-1 (Gas hazardous areas classification)", "IEC 60079-10-2 (Dust hazardous areas classification)", "IEC 60079-11 (Intrinsic safety)"],
      "divergence_notes": "NEC uses two parallel classification systems — Division (legacy US, Arts 500-503) and Zone (IEC-aligned, Arts 505-506). IEC 60079 uses Zone only. NEC Group A/B/C/D (gas) and E/F/G (dust) map approximately to IEC IIA/IIB/IIC and IIIA/IIIB/IIIC but with material-specific differences. See hazardous-locations-classification.json for the comprehensive conversion matrix.",
      "related_bs_7671": [],
      "usage_notes": "On a new design, ask the AHJ early which classification system is preferred — many jurisdictions accept either, but mixing systems within one project is problematic.",
      "related_articles": ["ART_511", "ART_513", "ART_514"]
    }
  ]
}
```

- [ ] **Step 2: Validate and commit**

```bash
python3 -c "import json; json.load(open('shared/standards/electrical/NFPA70/art500-506-hazardous-locations.json'))" && echo OK
git add shared/standards/electrical/NFPA70/art500-506-hazardous-locations.json
git commit -m "feat: NFPA70 art500-506-hazardous-locations.json — Division (Arts 500-503) + Zone (Arts 505-506) bundle"
```

---

## Task 22: Create art517-healthcare.json

**Files:**
- Create: `shared/standards/electrical/NFPA70/art517-healthcare.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "NFPA 70 Article 517 — Health Care Facilities",
  "_version": "1.0.0",
  "articles": [
    {
      "article_id": "ART_517",
      "nec_ref": "NFPA 70:2023 Article 517",
      "chapter": 5,
      "article_number": 517,
      "article_title": "Health Care Facilities",
      "scope": "Healthcare facility electrical systems — patient care spaces (Categories 1-4 per 517.2), Type 1/2/3 essential electrical systems (EES), isolated power systems, X-ray, anesthetizing locations (517.60+).",
      "applies_to": ["healthcare", "hospitals", "outpatient", "patient_care_spaces", "essential_electrical_system", "isolated_power"],
      "key_sections": [
        {"section": "517.2",   "title": "Definitions — Patient Care Space Categories", "summary": "Category 1 (critical care): includes operating, ICU, etc. Category 2 (general care): includes patient rooms, exam rooms. Category 3 (basic care). Category 4 (support areas — corridors, lobbies). Determines receptacle type, EES requirement, redundancy"},
        {"section": "517.13",  "title": "Grounding of Receptacles and Fixed Electrical Equipment in Patient Care Spaces", "summary": "Two equipment grounding paths: (1) EGC in raceway, (2) insulated copper EGC bonded to grounding terminal of receptacle. Both required for Category 1 and 2"},
        {"section": "517.30",  "title": "Sources of Power (Type 1 EES)", "summary": "Type 1 hospital EES: two independent sources of power (utility + on-site generator). Generator must start within 10 s and provide power for ≥1.5 hours minimum. Required for Category 1 + 2 patient care"},
        {"section": "517.31",  "title": "Emergency System (Type 1 EES — Branches)", "summary": "Type 1 EES has THREE branches: (1) Life Safety Branch, (2) Critical Branch, (3) Equipment System. All three on the same EES bus + transfer scheme"},
        {"section": "517.41",  "title": "Sources of Power (Type 2 EES)", "summary": "Type 2 EES: two independent sources but with reduced scope. For nursing homes (Type 2 generally) and outpatient (Type 3 reduced further)"},
        {"section": "517.60",  "title": "Anesthetizing Locations", "summary": "Definitions, grounding requirements for hazardous (Class I Div 1 flammable anesthetic — RARE in modern practice with non-flammable gases) and other anesthetizing locations"},
        {"section": "517.160", "title": "Isolated Power Systems (IT Systems)", "summary": "Required in wet locations (e.g. ORs) where line-isolation is critical. Includes Line Isolation Monitor (LIM) per IEC 61557-9 / NEC 517.160"}
      ],
      "tabulated_values": {},
      "tables_inline": {
        "Patient_Care_Space_Categories_Quick_Reference": {
          "title": "Healthcare Patient Care Space Categories (NEC 2023 — 517.2)",
          "rows": [
            {"category": 1, "description": "Critical Care Space",    "typical_areas": "Operating rooms, ICUs, cath labs, NICU, ER trauma, recovery"},
            {"category": 2, "description": "General Care Space",     "typical_areas": "Patient rooms, exam rooms, treatment rooms"},
            {"category": 3, "description": "Basic Care Space",       "typical_areas": "Outpatient procedure rooms in lower-risk facilities"},
            {"category": 4, "description": "Support Spaces",         "typical_areas": "Corridors, lobbies, common areas, offices"}
          ]
        }
      },
      "common_errors": [
        "Missing the second equipment-grounding path (insulated EGC) in patient care spaces (517.13) — RACEWAY alone is insufficient",
        "Treating a Type 1 EES as a single circuit — Type 1 requires THREE branches (Life Safety, Critical, Equipment) all sourced from the EES bus",
        "Specifying Type 1 EES for an outpatient facility — Type 1 is for Category 1 patient care; outpatient surgery centers typically Type 2 or 3 depending on procedure scope",
        "Omitting isolated power systems in wet locations like ORs — required by 517.160 and the FGI guidelines"
      ],
      "drawn_as": ["RECEPTACLE_HOSPITAL_GRADE", "ATS"],
      "related_iec_60364": ["IEC 60364-7-710 (Medical locations)"],
      "divergence_notes": "NEC Art 517 uses Categories 1-4 + Type 1/2/3 EES classification; IEC 60364-7-710 uses Group 0/1/2 + 'safety' / 'critical' / 'general' service categories. Patient-care space classification differs in detail though the philosophy is similar. NEC Type 1 EES three-branch structure (Life Safety / Critical / Equipment) has direct IEC equivalent in 60364-7-710 essential power supply but with different grouping. NEC's isolated power system requirements (517.160) align with IEC 60364-7-710 medical IT but specifics differ — NEC mandates Line Isolation Monitor (LIM) hardware per UL 1022, IEC mandates IMD per IEC 61557-8.",
      "related_bs_7671": [],
      "usage_notes": "Coordinate with FGI Guidelines for Design and Construction of Hospitals (referenced from Art 517) and NFPA 99 (Health Care Facilities Code) — the latter is the companion standard.",
      "related_articles": ["ART_700", "ART_701", "ART_250"]
    }
  ]
}
```

- [ ] **Step 2: Validate and commit**

```bash
python3 -c "import json; json.load(open('shared/standards/electrical/NFPA70/art517-healthcare.json'))" && echo OK
git add shared/standards/electrical/NFPA70/art517-healthcare.json
git commit -m "feat: NFPA70 art517-healthcare.json — patient care categories, Type 1/2/3 EES, isolated power"
```

---

## Task 23: Create art625-ev-charging.json

**Files:**
- Create: `shared/standards/electrical/NFPA70/art625-ev-charging.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "NFPA 70 Article 625 — Electric Vehicle Power Transfer System",
  "_version": "1.0.0",
  "articles": [
    {
      "article_id": "ART_625",
      "nec_ref": "NFPA 70:2023 Article 625",
      "chapter": 6,
      "article_number": 625,
      "article_title": "Electric Vehicle Power Transfer System",
      "scope": "Conductive and inductive EV charging — Levels 1 (120 V), 2 (208/240 V), 3 (DC fast charging). Conductor sizing at 125% continuous (625.40), GFCI for personnel (625.54), ventilation (625.52), disconnect, load management (625.42).",
      "applies_to": ["ev_charging", "evse", "dc_fast_charging", "wireless_ev_charging", "load_management"],
      "key_sections": [
        {"section": "625.40", "title": "Electric Vehicle Branch Circuit", "summary": "Branch circuit dedicated to EVSE; conductors sized at 125% of EVSE rated input current (continuous load assumption per 625.41(B))"},
        {"section": "625.41", "title": "Overcurrent Protection", "summary": "OCPD rated ≥ EVSE rated input current; cannot exceed conductor ampacity"},
        {"section": "625.42", "title": "Rating", "summary": "EVSE rating shall not exceed branch circuit rating. Load management systems permitted per 625.42(A)(2) — multiple EVSEs sharing a feeder with controlled total load"},
        {"section": "625.43", "title": "Disconnecting Means", "summary": "Disconnect for EVSE rated >60 A or >150 V to ground; lockable in OFF position"},
        {"section": "625.46", "title": "Loss of Primary Source", "summary": "EVSE shall automatically disconnect from premises when primary source is lost"},
        {"section": "625.52", "title": "Ventilation", "summary": "Indoor charging area ventilation required for Level 2 charging of vehicles that vent hydrogen during charging (rare in modern Li-ion vehicles, but rule still applies)"},
        {"section": "625.54", "title": "Personnel Protection System (GFCI)", "summary": "EVSE shall include integral GFCI ≤20 mA Class A AND/OR equipment ground-fault circuit protection (EGFCI). For circuits supplying single-phase Level 2 EVSE, the LISTED EVSE provides the GFCI internally — external GFCI breaker required ONLY for receptacle-type EVSE connections"}
      ],
      "tabulated_values": {},
      "tables_inline": {
        "EV_Charging_Levels": {
          "title": "EV Charging Level Classification (typical, not from Article 625)",
          "rows": [
            {"level": "Level 1", "voltage": "120 V AC", "typical_current": "12-16 A", "typical_kw": "1.4-1.9 kW", "connector": "SAE J1772"},
            {"level": "Level 2", "voltage": "208-240 V AC", "typical_current": "16-80 A", "typical_kw": "3-19 kW", "connector": "SAE J1772 (NACS / Tesla also)"},
            {"level": "Level 3 / DCFC", "voltage": "200-1000 V DC", "typical_current": "100-500 A", "typical_kw": "50-350 kW", "connector": "CCS Type 1, CHAdeMO, NACS/Tesla, GB/T"}
          ]
        }
      },
      "common_errors": [
        "Sizing the EVSE branch circuit at 100% of EVSE rating — 625.41(B) requires 125% continuous (matches 215.2 feeder rule)",
        "Omitting load management documentation on multi-EVSE feeders — required by 625.42(A)(2)",
        "Installing an external GFCI breaker on a hard-wired listed Level 2 EVSE — redundant and may cause nuisance trips; listed EVSE provides GFCI internally",
        "Treating Level 3 DCFC as a normal EV charger — it requires utility-scale interconnection coordination (often >150 kW)"
      ],
      "drawn_as": ["EV_CHARGER"],
      "related_iec_60364": ["IEC 60364-7-722 (Supply of electric vehicles)"],
      "divergence_notes": "NEC 625.40 cable sizing at 125% of EVSE input current vs IEC 60364-7-722 cable sizing at 100% continuous of EVSE rating with no diversity — same end value for most charger ratings, different framing. NEC mandates GFCI (Class A or EGFCI) per 625.54; IEC mandates Type B RCD where DC leakage > 6 mA possible (functional equivalent — both detect DC fault currents). NEC has no PEN broken-conductor protection requirement; IEC 60364-7-722 requires it for PME/TN-C-S installations. NEC permits separable receptacle EVSE; IEC permits both fixed-cord and separable.",
      "related_bs_7671": [],
      "usage_notes": "Document the load management scheme explicitly when multiple EVSEs share a feeder. Default to 125% continuous (matches NEC 215.2 / 220 conventions). For DC fast chargers, coordinate with the utility early — most require formal interconnection study.",
      "related_articles": ["ART_210", "ART_215", "ART_220", "ART_240"]
    }
  ]
}
```

- [ ] **Step 2: Validate and commit**

```bash
python3 -c "import json; json.load(open('shared/standards/electrical/NFPA70/art625-ev-charging.json'))" && echo OK
git add shared/standards/electrical/NFPA70/art625-ev-charging.json
git commit -m "feat: NFPA70 art625-ev-charging.json — EV charging levels, 125% continuous, GFCI, load management"
```

---

## Task 24: Create art680-pools-spas.json

**Files:**
- Create: `shared/standards/electrical/NFPA70/art680-pools-spas.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "NFPA 70 Article 680 — Swimming Pools, Fountains, and Similar Installations",
  "_version": "1.0.0",
  "articles": [
    {
      "article_id": "ART_680",
      "nec_ref": "NFPA 70:2023 Article 680",
      "chapter": 6,
      "article_number": 680,
      "article_title": "Swimming Pools, Fountains, and Similar Installations",
      "scope": "Permanently installed pools (Part II — 680.20+), storable pools (Part III — 680.30+), spas/hot tubs (Part IV — 680.40+), fountains (Part V — 680.50+), hydromassage bathtubs (Part VII — 680.70+). GFCI rules, equipotential bonding (680.26), receptacle clearances (5 ft / 10 ft / 20 ft rules), underwater lighting.",
      "applies_to": ["pools", "spas", "hot_tubs", "fountains", "hydromassage", "equipotential_bonding", "wet_locations"],
      "key_sections": [
        {"section": "680.21", "title": "Motors — Permanently Installed Pools", "summary": "Pool pump motor branch circuits: GFCI protection (680.21(C)) for single-phase 120-240 V"},
        {"section": "680.22", "title": "Area Lighting, Receptacles, and Equipment", "summary": "Receptacle outlets: at least one within 6-20 ft of pool wall (681.22(A)), all 125 V 15/20 A receptacles within 20 ft of pool wall GFCI-protected, NO receptacles within 5 ft of inside wall of pool except low-voltage installations"},
        {"section": "680.26", "title": "Equipotential Bonding", "summary": "Equipotential bonding grid required at all permanently installed pools — connects: pool reinforcing steel, deck steel/copper grid, metal pool fittings, pool water (via conductive surface or intentional grid), pumps, lights, fences within 5 ft, etc. #8 AWG solid copper minimum, 4500 lb tensile strength"},
        {"section": "680.42", "title": "Spas and Hot Tubs (Outdoor)", "summary": "GFCI for all 125 V receptacles within 10 ft of inside walls of spa/hot tub. Indoor spas: same rules + interior wiring per Part IV"},
        {"section": "680.50", "title": "Fountains — General", "summary": "Fountains include decorative pools, water displays, etc. Conductive metal parts equipotentially bonded; underwater lighting limited to specific listings"},
        {"section": "680.74", "title": "Hydromassage Bathtub — Bonding", "summary": "Hydromassage bathtub: all metal piping/parts and motor frame bonded together with #8 AWG solid copper"}
      ],
      "tabulated_values": {},
      "tables_inline": {
        "Pool_Receptacle_Distance_Rules_680.22": {
          "title": "Receptacle Distances from Pool Inside Wall",
          "rows": [
            {"distance_from_pool": "Within 5 ft",       "rule": "No general-purpose receptacle (low-voltage equipment receptacle exception)"},
            {"distance_from_pool": "6-20 ft",            "rule": "At least one general-purpose receptacle required. GFCI-protected"},
            {"distance_from_pool": "Beyond 20 ft",       "rule": "Receptacles permitted; GFCI required for those serving pool equipment"}
          ]
        }
      },
      "common_errors": [
        "Omitting the equipotential bonding grid (680.26) — most frequent pool inspection failure",
        "Specifying a receptacle within 5 ft of pool inside wall — prohibited (except low-voltage)",
        "Treating an outdoor hot tub like a regular outdoor receptacle — 680.42 GFCI distance is 10 ft, not the dwelling-outdoor 6 ft",
        "Using #10 AWG for equipotential bonding — 680.26 requires #8 AWG solid copper"
      ],
      "drawn_as": ["GFCI_RECEPTACLE", "POOL_LIGHT"],
      "related_iec_60364": ["IEC 60364-7-702 (Swimming pools and fountains)"],
      "divergence_notes": "NEC 680.22 uses imperial distance rules (5 ft / 6-20 ft / 20 ft / 10 ft for spas). IEC 60364-7-702 uses zone classification (Zone 0 = pool water + 0.3 m around, Zone 1 = 2 m horizontal from pool edge, Zone 2 = 1.5 m beyond Zone 1) with different rules per zone. NEC equipotential bonding grid (680.26) ≈ IEC 60364-7-702 supplementary bonding but NEC is more prescriptive on grid construction (#8 AWG solid Cu).",
      "related_bs_7671": [],
      "usage_notes": "Coordinate with the pool contractor's bonding plan and the local AHJ — equipotential bonding is THE pool electrical safety requirement.",
      "related_articles": ["ART_210", "ART_240", "ART_250"]
    }
  ]
}
```

- [ ] **Step 2: Validate and commit**

```bash
python3 -c "import json; json.load(open('shared/standards/electrical/NFPA70/art680-pools-spas.json'))" && echo OK
git add shared/standards/electrical/NFPA70/art680-pools-spas.json
git commit -m "feat: NFPA70 art680-pools-spas.json — pool/spa receptacle distances, equipotential bonding"
```

---

## Task 25: Create art690-solar-pv.json

**Files:**
- Create: `shared/standards/electrical/NFPA70/art690-solar-pv.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "NFPA 70 Article 690 — Solar Photovoltaic (PV) Systems",
  "_version": "1.0.0",
  "articles": [
    {
      "article_id": "ART_690",
      "nec_ref": "NFPA 70:2023 Article 690",
      "chapter": 6,
      "article_number": 690,
      "article_title": "Solar Photovoltaic (PV) Systems",
      "scope": "PV systems definitions and requirements — circuit sizing at 125% continuous (690.8), maximum voltage (690.7), DC arc-fault circuit interrupter — DC AFCI (690.11), rapid shutdown (690.12), grounding (690.41-43), source-circuit and output-circuit sizing.",
      "applies_to": ["solar_pv", "photovoltaic", "rapid_shutdown", "dc_arc_fault", "module_strings", "inverters", "interconnection"],
      "key_sections": [
        {"section": "690.7",  "title": "Maximum Voltage", "summary": "Maximum PV source-circuit voltage: 600 V for dwelling, 1000 V for non-dwelling, 1500 V for non-dwelling where 1500 V-rated. Determined by adjusted module open-circuit voltage at lowest expected temperature"},
        {"section": "690.8",  "title": "Circuit Sizing and Current", "summary": "PV source circuit current = max module Isc × 125%. PV output circuit current = sum of PV source circuit currents. Conductor ampacity = 125% × calculated current"},
        {"section": "690.9",  "title": "Overcurrent Protection", "summary": "OCPD rating ≥ 156% of module Isc (125% module × 125% continuous). Inverter output OCPD per 690.9(B)"},
        {"section": "690.11", "title": "Arc-Fault Circuit Protection (DC)", "summary": "PV source circuits operating at ≥80 V DC require listed DC arc-fault circuit interrupter (DC AFCI). Typically integrated in modern PV inverters or string combiners"},
        {"section": "690.12", "title": "Rapid Shutdown of PV Systems on Buildings", "summary": "PV array on building — rapid shutdown system shutting down conductors to ≤30 V within 30 s of initiation. Required at: 1 ft of array on rooftop and 5 ft outside array boundary. Initiation by service disconnect or first-responder switch"},
        {"section": "690.41", "title": "System Grounding", "summary": "PV systems may be ungrounded, functionally grounded (one conductor referenced to ground through impedance), or solidly grounded. Most modern systems are functionally grounded (transformerless inverters)"},
        {"section": "690.47", "title": "Grounding Electrode System", "summary": "DC grounding electrode permitted; if AC and DC systems share grounding electrode, the GEC must be sized per the larger of: AC GEC (250.66) or DC GEC (250.166)"},
        {"section": "690.64", "title": "Point of Interconnection (cross-ref 705)", "summary": "Connection of PV inverter output to premises wiring per Art 705"}
      ],
      "tabulated_values": {},
      "tables_inline": {
        "PV_Voltage_Limits_690.7": {
          "title": "Maximum PV Source-Circuit Voltage",
          "rows": [
            {"installation_type": "Dwelling — one-/two-family + multifamily",  "max_voltage_dc": "600 V"},
            {"installation_type": "Non-dwelling (commercial, industrial)",       "max_voltage_dc": "1000 V (or 1500 V if equipment listed for 1500 V)"}
          ]
        },
        "Rapid_Shutdown_Initiation_Markings_690.12": {
          "title": "Rapid Shutdown System — Required Field Marking",
          "rows": [
            {"marking_type": "Initiation device label",     "wording": "Solar PV System Equipped With Rapid Shutdown"},
            {"marking_type": "Initiation device location",  "wording": "At service disconnect, OR within sight of service disconnect, OR location of first responder operation"}
          ]
        }
      },
      "common_errors": [
        "Missing the 125% × 125% cascading multiplier (156% of module Isc) for OCPD sizing per 690.9 — frequent error",
        "Failing to adjust maximum voltage for lowest expected temperature — 690.7 requires Voc adjustment, typically increasing the calc voltage by ~10-15% above STC",
        "Omitting rapid shutdown on rooftop residential PV (690.12) — added in NEC 2014, expanded in 2017 and 2020",
        "Treating an ungrounded PV system as needing an AC EGC only — also requires the functional grounding reference",
        "Sizing inverter output OCPD at 100% of inverter output current — must be ≥125% × inverter max output (690.9(B))"
      ],
      "drawn_as": ["PV_MODULE", "PV_INVERTER", "PV_DISCONNECT"],
      "related_iec_60364": ["IEC 60364-7-712 (Solar photovoltaic power supply systems)"],
      "divergence_notes": "NEC 690 is more prescriptive than IEC 60364-7-712. NEC requires DC AFCI (690.11) at ≥80 V DC; IEC has no equivalent (DC AFD coverage emerging in IEC 60947). NEC mandates rapid shutdown on rooftop PV (690.12); IEC has no equivalent. NEC 125%-of-125% (156%) OCPD sizing rule is unique to NEC; IEC sizes per Iz × design current with no cascading multiplier. NEC permits 1500 V DC in non-dwelling installations; IEC 60364-7-712 typically limited to 1500 V via national supplements.",
      "related_bs_7671": [],
      "usage_notes": "PV designs on US projects must show: (1) string sizing computation with cold-temp Voc, (2) OCPD coordination at 156% Isc, (3) rapid shutdown schematic for rooftop installations, (4) interconnection per 705 (often the most-revised page during AHJ review).",
      "related_articles": ["ART_240", "ART_250", "ART_310", "ART_705", "ART_706"]
    }
  ]
}
```

- [ ] **Step 2: Validate and commit**

```bash
python3 -c "import json; json.load(open('shared/standards/electrical/NFPA70/art690-solar-pv.json'))" && echo OK
git add shared/standards/electrical/NFPA70/art690-solar-pv.json
git commit -m "feat: NFPA70 art690-solar-pv.json — PV voltage, 125%×125% sizing, DC AFCI, rapid shutdown"
```

---

## Task 26: Create art695-fire-pumps.json

**Files:**
- Create: `shared/standards/electrical/NFPA70/art695-fire-pumps.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "NFPA 70 Article 695 — Fire Pumps",
  "_version": "1.0.0",
  "articles": [
    {
      "article_id": "ART_695",
      "nec_ref": "NFPA 70:2023 Article 695",
      "chapter": 6,
      "article_number": 695,
      "article_title": "Fire Pumps",
      "scope": "Fire pump installation — power source (695.3), supply continuity, fire pump controller (695.7), conductor sizing (695.6), feeder location (695.6(B)), disconnect prohibition on the supply line (695.4).",
      "applies_to": ["fire_pumps", "life_safety_pumping", "diesel_pump", "electric_pump"],
      "key_sections": [
        {"section": "695.3", "title": "Power Source(s) for Electric Motor-Driven Fire Pumps", "summary": "Power source either: (1) reliable utility service, (2) reliable on-site source (generator), (3) combination. 'Reliable' is the AHJ's call but generally means continuous availability"},
        {"section": "695.4", "title": "Continuity of Power", "summary": "Fire pump supply conductors shall be direct from the source of power to the fire pump controller (or a tap from the supply to non-fire-pump loads must not be subject to disconnection by any fire-related event)"},
        {"section": "695.5", "title": "Transformers", "summary": "Where a transformer feeds a fire pump, the transformer is to be sized at 125% of pump motor + 100% of associated equipment"},
        {"section": "695.6", "title": "Power Wiring", "summary": "Conductor ampacity ≥ 125% of fire pump motor + accessories. Single-conductor wiring methods may be used (not in raceway with non-fire-pump conductors)"},
        {"section": "695.7", "title": "Voltage Drop", "summary": "Voltage at fire pump controller terminals: shall not drop more than 15% below normal during motor starting; shall not drop more than 5% below 100% of normal during motor running"},
        {"section": "695.10","title": "Listed Equipment", "summary": "Listed fire pump controller (NFPA 20-listed) and associated equipment"}
      ],
      "tabulated_values": {},
      "tables_inline": {},
      "common_errors": [
        "Installing a disconnect on the fire pump supply line (other than the listed fire pump controller's disconnect) — prohibited by 695.4(B)(1)",
        "Routing fire pump supply through normal panelboards or feeders subject to opening on a fire-floor signal — 695.4(B) requires the supply path to remain energised even on fire",
        "Specifying voltage drop > 15% at motor start or > 5% at run — fire pump may stall or trip",
        "Using a non-listed (non-NFPA 20) controller — NEC 695.10 requires listed equipment"
      ],
      "drawn_as": ["FIRE_PUMP", "FIRE_PUMP_CONTROLLER"],
      "related_iec_60364": ["IEC 60364-5-56 (Safety services) — life safety power"],
      "divergence_notes": "Fire pump rules are NFPA-system-specific (NFPA 20 + NEC 695). IEC handles life-safety pumps via 60364-5-56 + national fire codes. NEC voltage-drop limits at fire pump (15% start, 5% run) are explicit; IEC defers to system-design coordination.",
      "related_bs_7671": [],
      "usage_notes": "Coordinate with the fire-protection engineer (NFPA 20 lead). Fire pump electrical and mechanical systems are tightly integrated — single-source design responsibility ideal.",
      "related_articles": ["ART_230", "ART_240", "ART_430", "ART_700"]
    }
  ]
}
```

- [ ] **Step 2: Validate and commit**

```bash
python3 -c "import json; json.load(open('shared/standards/electrical/NFPA70/art695-fire-pumps.json'))" && echo OK
git add shared/standards/electrical/NFPA70/art695-fire-pumps.json
git commit -m "feat: NFPA70 art695-fire-pumps.json — fire pump supply continuity, voltage drop, disconnect prohibition"
```

---

## Task 27: Create art700-705-emergency-standby.json (bundle 700, 701, 702, 705)

**Files:**
- Create: `shared/standards/electrical/NFPA70/art700-705-emergency-standby.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "NFPA 70 Articles 700-705 — Emergency Systems, Legally Required Standby, Optional Standby, Interconnected Sources",
  "_version": "1.0.0",
  "_note": "Bundle of four closely-related articles. Each addresses a different service-continuity tier — Art 700 (life safety, ≤10 s restoration), Art 701 (legally required, ≤60 s), Art 702 (optional, owner-elected), Art 705 (interconnection of multiple sources).",
  "articles": [
    {
      "article_id": "ART_700_705",
      "nec_ref": "NFPA 70:2023 Articles 700, 701, 702, 705",
      "chapter": 7,
      "article_number": 700,
      "article_title": "Emergency Systems / Legally Required Standby / Optional Standby / Interconnected Power Production Sources",
      "scope": "Article 700: emergency systems essential for safety to human life (egress lighting, fire alarm, refrigeration of critical med, etc.) — restoration ≤10 s. Article 701: legally required standby (HVAC for life safety, sewage, communications, industrial process) — restoration ≤60 s. Article 702: optional standby (owner-elected — comfort, computer protection). Article 705: interconnection of multiple sources (PV, wind, generator, utility).",
      "applies_to": ["emergency", "legally_required_standby", "optional_standby", "transfer_equipment", "selective_coordination", "interconnection"],
      "key_sections": [
        {"section": "700.4",   "title": "Capacity", "summary": "Sized to carry all emergency loads simultaneously"},
        {"section": "700.10",  "title": "Wiring, Emergency System", "summary": "Independent wiring from emergency source to emergency loads; SEPARATE from normal-source wiring"},
        {"section": "700.12",  "title": "General Requirements (Sources of Power)", "summary": "Emergency power source options: storage battery, generator set, uninterruptible power supply (UPS), separate utility service, fuel cell"},
        {"section": "700.27",  "title": "Coordination — Emergency", "summary": "Emergency system OCPDs shall be selectively coordinated with all supply-side OCPDs (overcurrent that would otherwise open emergency circuits)"},
        {"section": "700.32",  "title": "Selective Coordination — Emergency System (alt clause #)", "summary": "Same as 700.27 — selective coordination requirement"},
        {"section": "701.4",   "title": "Capacity — Legally Required", "summary": "Capacity for all legally required standby loads simultaneously"},
        {"section": "701.10",  "title": "Wiring, Legally Required Standby", "summary": "Per Art 215 / 220 — no special separation requirement (unlike Art 700)"},
        {"section": "701.32",  "title": "Selective Coordination — Legally Required Standby", "summary": "Same selectivity rule as 700.32 applied to legally required standby"},
        {"section": "702.4",   "title": "Capacity and Rating — Optional Standby", "summary": "Sized per the loads it serves — no NEC-mandated capacity minimum"},
        {"section": "702.5",   "title": "Transfer Equipment", "summary": "Transfer equipment listed for the intended purpose (UL 1008 for ATS / manual transfer switches)"},
        {"section": "705.6",   "title": "Equipment Disconnect", "summary": "Disconnecting means for each power source; lockable, identified"},
        {"section": "705.12",  "title": "Load-Side Source Connections", "summary": "PV/wind/generator interconnection at load side of service disconnect — busbar/feeder ampacity rules (120% rule, sum rule). Most common interconnection method for residential PV"}
      ],
      "tabulated_values": {},
      "tables_inline": {
        "Emergency_vs_Standby_Comparison": {
          "title": "Article 700 / 701 / 702 — Required Restoration Times and Scope",
          "rows": [
            {"article": 700, "name": "Emergency Systems",                "scope": "Life safety: egress lighting, fire alarm, fire-pump backup, healthcare critical branch, mass transit", "max_restoration_s": 10},
            {"article": 701, "name": "Legally Required Standby",         "scope": "Communications, industrial process, sewage, HVAC for life safety", "max_restoration_s": 60},
            {"article": 702, "name": "Optional Standby",                  "scope": "Owner-elected: comfort, computer protection, retail HVAC", "max_restoration_s": "Not specified"}
          ]
        },
        "Load_Side_Interconnection_Rules_705.12": {
          "title": "PV/Wind Interconnection at Load Side — Busbar Ampacity Rules",
          "rows": [
            {"rule": "Sum rule",            "description": "Inverter output OCPD + main breaker rating ≤ 100% of busbar ampacity"},
            {"rule": "120% rule",            "description": "If sum > 100%: inverter output OCPD ≤ (busbar ampacity × 120% − main breaker rating). I.e., main breaker downgrade or busbar upgrade needed"},
            {"rule": "Center-fed rule",      "description": "For PV inverter breaker on opposite end from main breaker, allow up to 120% rule without main breaker downgrade"},
            {"rule": "Sum 100% rule",        "description": "Sum of all overcurrent devices supplying busbar ≤ 100% of busbar ampacity (the conservative rule)"}
          ]
        }
      },
      "common_errors": [
        "Mixing Art 700 emergency circuits with normal-source circuits in shared wiring — Art 700.10 requires independent wiring",
        "Failing selective coordination requirement (700.32, 701.32) — common on retrofit of small commercial buildings adding fire pump",
        "Misapplying 705.12 — assuming the 120% busbar rule applies when actually the sum rule applies (busbar is the limiting factor)",
        "Treating Art 702 as having no NEC requirements — capacity sizing per 702.4 and transfer equipment listing per 702.5 still apply"
      ],
      "drawn_as": ["ATS", "GENERATOR_SET", "UPS"],
      "related_iec_60364": ["IEC 60364-5-56 (Safety services)", "IEC 60364-8-2 (Prosumer's electrical installations) — for interconnection rules"],
      "divergence_notes": "NEC Articles 700/701/702 distinguish emergency vs legally-required-standby vs optional-standby with explicit restoration times (10 s / 60 s / not specified); IEC 60364-5-56 has 'safety services' (corresponds roughly to NEC 700) and 'standby services' (corresponds to NEC 701/702 combined) with different restoration classifications (Class 0 = no break, 0.15 s, 0.5 s, 15 s, > 15 s). NEC 705.12 interconnection rules (sum / 120% / center-fed) are very prescriptive; IEC 60364-8-2 has equivalent requirements but less geometrically specific. Selective coordination requirement (700.32 / 701.32) is more explicit in NEC; IEC handles via IEC 60364-5-53 device coordination tables.",
      "related_bs_7671": [],
      "usage_notes": "Always identify which article applies (700 vs 701 vs 702) based on what the loads ARE — emergency systems are by code authority (life safety), legally required by other AHJ/code mandate, optional by owner. Document selective coordination on critical fire-pump and life-safety circuits — frequent inspection failure.",
      "related_articles": ["ART_215", "ART_230", "ART_240", "ART_517", "ART_690", "ART_695", "ART_706"]
    }
  ]
}
```

- [ ] **Step 2: Validate and commit**

```bash
python3 -c "import json; json.load(open('shared/standards/electrical/NFPA70/art700-705-emergency-standby.json'))" && echo OK
git add shared/standards/electrical/NFPA70/art700-705-emergency-standby.json
git commit -m "feat: NFPA70 art700-705-emergency-standby.json — emergency/standby/optional + 705 interconnection"
```

---

## Task 28: Create grounding-and-bonding.json (cross-cutting)

**Files:**
- Create: `shared/standards/electrical/NFPA70/grounding-and-bonding.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "NFPA 70 — Grounding and Bonding (cross-cutting)",
  "_version": "1.0.0",
  "_note": "Unified treatment of grounding across NEC. Primary source is Article 250; references from 300, 310, 408, 450. Use this file when looking up grounding rules independently of a specific Article.",
  "grounding_concepts": [
    {
      "concept": "System Grounding",
      "definition": "Intentional connection of one conductor of the electrical system to the grounding electrode system at one point.",
      "nec_section": "250.20-26",
      "examples": ["Grounded conductor of 120/240 V single-phase service is bonded to GES at service via MBJ", "Grounded conductor of 480Y/277 V wye service grounded similarly"]
    },
    {
      "concept": "Equipment Grounding",
      "definition": "Conductive paths providing low-impedance return for ground-fault current. Bonds all normally non-current-carrying metal parts together and back to the grounded conductor at the source.",
      "nec_section": "250.118 (acceptable types), 250.122 (sizing)",
      "examples": ["EGC (insulated or bare copper)", "Metal raceway acting as EGC", "Cable assembly's EGC conductor (e.g. NM cable green/bare)"]
    },
    {
      "concept": "Grounding Electrode System (GES)",
      "definition": "All grounding electrodes present at the building, bonded together to form a single grounding reference.",
      "nec_section": "250.50",
      "required_electrodes_when_present": [
        "Metal underground water pipe (≥10 ft, in direct contact with earth)",
        "Concrete-encased electrode (Ufer) — ≥20 ft of bare/zinc-galvanized rebar, ≥1/2 in dia, in concrete in direct contact with earth",
        "Ground ring — bare copper conductor ≥2 AWG, ≥20 ft, ≥30 in below grade",
        "Rod/Pipe/Plate electrode (250.52(A)(5)) — typical 5/8 in dia × 8 ft Cu-clad steel rod, ≥8 ft in earth",
        "Structural metal frame — if present and qualifying"
      ]
    },
    {
      "concept": "Main Bonding Jumper (MBJ)",
      "definition": "Connection between grounded service conductor (neutral) and equipment grounding terminal at the service equipment.",
      "nec_section": "250.28",
      "sizing": "Per 250.28(D)(1): ≥ size of GEC required by Table 250.66, OR per 250.28(D)(2) if largest ungrounded conductor > 1100 kcmil (12.5% rule)"
    },
    {
      "concept": "Bonding Jumper, Supply-Side",
      "definition": "Connection between the grounded conductor and equipment grounding system on the supply side of the service disconnect.",
      "nec_section": "250.30(A)(1) — for separately derived systems",
      "_note": "Functionally identical to MBJ but applied to SDS (transformer secondary, generator output, etc.)"
    },
    {
      "concept": "Equipment Grounding Conductor (EGC)",
      "definition": "Conductor that provides the low-impedance fault current path back to the source. Required on every circuit.",
      "nec_section": "250.118, 250.122",
      "sizing": "Per Table 250.122 (by OCPD rating) OR adiabatic (250.122(B)) for special conditions (e.g. parallel conductors)",
      "vs_iec_cpc": "The NEC EGC is the analogue of IEC CPC. Sizing differs: NEC sizes by OCPD rating; IEC sizes by line conductor CSA (Table 54.1) or adiabatic."
    },
    {
      "concept": "Grounding Electrode Conductor (GEC)",
      "definition": "Conductor that connects the grounded service conductor (or system source) to the grounding electrode system.",
      "nec_section": "250.66",
      "sizing": "Per Table 250.66 (by largest ungrounded service conductor)",
      "vs_iec": "No exact IEC analogue — IEC sizes 'main earthing conductor' adiabatically or per local supplement."
    }
  ],
  "egc_sizing_matrix_summary": {
    "_source": "NEC Table 250.122 (full table in art250-grounding-bonding.json)",
    "_rule_of_thumb": "EGC at least the next size up from the OCPD rating in conductor terms. For copper EGC, rough rule: OCPD ≤ 60A → 10 AWG; 60-200A → larger copper EGC needed.",
    "_adiabatic_when": "Use 250.122(B) adiabatic check when fault current × clearing time > what Table 250.122 EGC can safely carry. Common on parallel circuits with high SCCR."
  },
  "common_grounding_errors": [
    "Confusing GEC (sized by ungrounded conductor) with EGC (sized by OCPD)",
    "Bonding neutral to ground at sub-panel — illegal except at service or first SDS disconnect (250.142)",
    "Omitting Ufer when present — 250.50(A)(3) mandates bonding all present electrodes",
    "Forgetting MBJ at service — without it, the grounded conductor is just a neutral, not a grounded one",
    "Treating the metal raceway as EGC on circuits where 250.118(5) FMC length/size limits apply — must run separate wire EGC"
  ],
  "iec_60364_cross_reference": {
    "concept_mapping": [
      {"nec": "System grounding (250.20-26)", "iec": "Earthing arrangement classification (IEC 60364-1 Clause 312 — TN-S, TN-C, TN-C-S, TT, IT)"},
      {"nec": "Equipment grounding (250.118 EGC)", "iec": "CPC (IEC 60364-5-54 Clause 543)"},
      {"nec": "Grounding electrode system (250.50)", "iec": "Earth electrode (IEC 60364-5-54 Clause 542)"},
      {"nec": "MBJ (250.28)", "iec": "Main earthing terminal connection (IEC 60364-5-54 Clause 542.4)"},
      {"nec": "GEC (250.66)", "iec": "Main earthing conductor / protective bonding conductor (IEC 60364-5-54 Clause 543)"}
    ]
  }
}
```

- [ ] **Step 2: Validate and commit**

```bash
python3 -c "import json; json.load(open('shared/standards/electrical/NFPA70/grounding-and-bonding.json'))" && echo OK
git add shared/standards/electrical/NFPA70/grounding-and-bonding.json
git commit -m "feat: NFPA70 grounding-and-bonding.json — cross-cutting grounding concepts + IEC mapping"
```

---

## Task 29: Create ocpd-coordination.json (cross-cutting)

**Files:**
- Create: `shared/standards/electrical/NFPA70/ocpd-coordination.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "NFPA 70 — OCPD Selective Coordination (cross-cutting)",
  "_version": "1.0.0",
  "_note": "Selective coordination requirements across NEC — 240.12, 700.32 (emergency), 701.32 (legally required), 645.27 (IT room), 695.6 (fire pump).",
  "selective_coordination_definition": "OCPDs are 'selectively coordinated' when only the OCPD nearest the fault opens to clear the fault — all upstream OCPDs remain closed.",
  "where_required": [
    {
      "nec_article_section": "700.32",
      "title": "Emergency Systems",
      "scope": "Selective coordination required between emergency-system OCPDs and supply-side OCPDs for the full range of available fault currents",
      "rationale": "An emergency-circuit fault must not open an upstream OCPD that would also de-energise non-emergency circuits — but more importantly, must not de-energise OTHER emergency loads"
    },
    {
      "nec_article_section": "701.32",
      "title": "Legally Required Standby Systems",
      "scope": "Same selectivity rule as 700.32, applied to legally required standby",
      "rationale": "Same logic as emergency, applied at 60 s restoration tier"
    },
    {
      "nec_article_section": "645.27",
      "title": "Information Technology Equipment Rooms",
      "scope": "Selective coordination of OCPDs supplying IT room critical loads",
      "rationale": "Single circuit fault must not cascade to take down the entire IT room"
    },
    {
      "nec_article_section": "695.6",
      "title": "Fire Pumps",
      "scope": "OCPDs supplying the fire pump shall be selectively coordinated such that an OCPD downstream of the fire pump controller does NOT open ahead of the fire pump controller",
      "rationale": "Fire pump must run during a fire even if part of the building distribution is faulted"
    }
  ],
  "methods": [
    {
      "method": "Time-current curve comparison",
      "description": "Plot the time-current characteristics of upstream and downstream OCPDs on the same log-log graph; selective coordination achieved if the downstream curve is entirely BELOW the upstream curve (lower time and current) for ALL fault currents up to the maximum available",
      "engineering_caveat": "Selective coordination through the full range of fault currents is hard — modern PV-rich systems can require very large frame circuit breakers upstream to maintain selectivity at high fault levels"
    },
    {
      "method": "Series-rated OCPDs",
      "description": "Listed combinations of fuses + circuit breakers tested together (240.86) — the upstream device's interrupting rating extends to the downstream device. NOT the same as selective coordination — series ratings allow the downstream device to clear faults exceeding its own interrupting rating but upstream device may also open",
      "engineering_caveat": "Series ratings do NOT necessarily provide selective coordination — confirm with manufacturer's published combinations"
    },
    {
      "method": "Zone-Selective Interlocking (ZSI)",
      "description": "Communication between OCPDs — downstream OCPD signals 'I have this fault' to upstream, restraining the upstream from tripping until the downstream attempts to clear",
      "engineering_caveat": "Requires compatible circuit breakers with ZSI capability (typically electronic trip units)"
    }
  ],
  "fuse_circuit_breaker_compatibility": {
    "rule": "Fuse-to-fuse selectivity easier than CB-to-CB at high fault currents. CB-to-CB selectivity at low/medium fault currents managed by time-delay settings; at high fault currents both may trip via instantaneous element unless ZSI",
    "typical_recommendation": "Selective coordination required by NEC 700.32 or 695.6 — engage a coordination study with the OCPD manufacturer at design stage; do not assume off-the-shelf devices will coordinate"
  },
  "common_errors": [
    "Specifying 'selective coordination required' on the drawings without doing the coordination study — the schedule must show the OCPDs that achieve selectivity",
    "Treating series-rated combinations as selective — series ratings are about interrupting capability, not selectivity",
    "Ignoring instantaneous trip on circuit breakers — at fault currents above the instantaneous threshold, all CBs in series may trip together"
  ],
  "iec_60364_cross_reference": "IEC 60364-4-43 Annex D provides cascading rules ≈ NEC series ratings. IEC has no explicit 'selective coordination' mandate for safety services equivalent to NEC 700.32 / 701.32 — IEC handles via system design coordination guidance."
}
```

- [ ] **Step 2: Validate and commit**

```bash
python3 -c "import json; json.load(open('shared/standards/electrical/NFPA70/ocpd-coordination.json'))" && echo OK
git add shared/standards/electrical/NFPA70/ocpd-coordination.json
git commit -m "feat: NFPA70 ocpd-coordination.json — selective coordination + series ratings + ZSI"
```

---

## Task 30: Create hazardous-locations-classification.json (cross-cutting)

**Files:**
- Create: `shared/standards/electrical/NFPA70/hazardous-locations-classification.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "NFPA 70 — Hazardous Locations: Class/Division and Class/Zone Classification",
  "_version": "1.0.0",
  "_note": "Unified treatment of the two parallel classification systems used in NEC — Division (legacy, Arts 500-503) and Zone (IEC-aligned, Arts 505-506). Plus equipment selection matrix and seal placement rules.",
  "classification_systems": [
    {
      "name": "Class/Division (NEC legacy)",
      "scope": "Arts 500-503. Class I (gas/vapor) × Division 1 (normal-condition ignitible concentration) / Division 2 (only abnormal). Class II (dust) × Division 1 / 2. Class III (ignitible fibers/flyings) × Division 1 / 2.",
      "gas_groups": {
        "A": "Acetylene",
        "B": "Hydrogen, ammonia (≤25% acetylene-equivalent)",
        "C": "Ethylene, hydrogen sulfide, propylene oxide",
        "D": "Propane, gasoline, methane, butane, ethanol, acetone, benzene, MEK"
      },
      "dust_groups": {
        "E": "Metal dust (aluminum, magnesium)",
        "F": "Coal dust, coke dust, carbon black",
        "G": "Grain dust, flour, plastic dust, wood dust"
      }
    },
    {
      "name": "Class/Zone (IEC-aligned)",
      "scope": "Arts 505-506. Class I × Zone 0 (continuously present), Zone 1 (occasionally), Zone 2 (only abnormal). Zone 20/21/22 for dust.",
      "gas_groups": {
        "IIA": "≈ NEC Group D (propane, methane, gasoline)",
        "IIB": "≈ NEC Group C (ethylene)",
        "IIC": "≈ NEC Groups A and B combined (acetylene, hydrogen)"
      },
      "dust_groups": {
        "IIIA": "Combustible flyings",
        "IIIB": "Non-conductive combustible dust",
        "IIIC": "Conductive combustible dust"
      }
    }
  ],
  "severity_equivalence_matrix": [
    {"nec_division": "Class I Div 1",  "iec_zone": "Class I Zone 0 + Zone 1 combined",  "severity_note": "Division 1 covers both 'continuously present' AND 'occasionally present' — broader than Zone 1 alone"},
    {"nec_division": "Class I Div 2",  "iec_zone": "Class I Zone 2",                    "severity_note": "Direct equivalence"},
    {"nec_division": "Class II Div 1", "iec_zone": "Zone 20 + Zone 21 combined",        "severity_note": "Similar broadening"},
    {"nec_division": "Class II Div 2", "iec_zone": "Zone 22",                            "severity_note": "Direct equivalence"}
  ],
  "equipment_marking_examples": [
    {"system": "Class/Division", "example": "Class I, Div 1, Group D, T4", "interpretation": "Suitable for Class I (gases) Div 1 (continuous/occasional), Group D (propane/gasoline), T4 (max surface temp 135 °C)"},
    {"system": "Class/Zone",     "example": "Class I, Zone 1, IIA T3",      "interpretation": "Class I Zone 1 (occasional), Group IIA, T3 (max surface temp 200 °C)"},
    {"system": "IEC",            "example": "II 2 G Ex db IIB+H2 T4 Gb",   "interpretation": "Group II equipment, Category 2 (Zone 1), G (gas), explosion proof, IIB + hydrogen, T4 (135 °C), EPL Gb (high level protection)"}
  ],
  "protection_techniques_class_division": [
    {"technique": "Explosionproof", "marking": "XP",      "applicability": "Class I Div 1, Class I Div 2"},
    {"technique": "Intrinsically safe", "marking": "IS",  "applicability": "Class I Div 1 (uA), Class I Div 2"},
    {"technique": "Nonincendive", "marking": "NIC",       "applicability": "Class I Div 2"},
    {"technique": "Purged/Pressurized", "marking": "Type X/Y/Z", "applicability": "Class I Div 1 (Type X), Div 2 (Type Z)"},
    {"technique": "Hermetically sealed", "marking": "—",  "applicability": "Class I Div 2 only"},
    {"technique": "Oil immersion", "marking": "—",        "applicability": "Class I Div 2 only"}
  ],
  "protection_techniques_class_zone": [
    {"technique": "Flameproof (Ex d)",          "iec_marking": "Ex d", "applicability": "Zone 1, Zone 2"},
    {"technique": "Increased safety (Ex e)",     "iec_marking": "Ex e", "applicability": "Zone 1, Zone 2"},
    {"technique": "Pressurized (Ex p)",          "iec_marking": "Ex p", "applicability": "Zone 1 (px), Zone 2 (py, pz)"},
    {"technique": "Intrinsic safety (Ex ia/ib)", "iec_marking": "Ex ia (Zone 0), Ex ib (Zone 1)", "applicability": "Ex ia = Zone 0; Ex ib = Zone 1"},
    {"technique": "Encapsulation (Ex m)",        "iec_marking": "Ex m", "applicability": "Zone 1 (ma, mb), Zone 2 (mc)"},
    {"technique": "Non-sparking (Ex nA)",        "iec_marking": "Ex nA","applicability": "Zone 2 only"}
  ],
  "seal_placement_rules": {
    "rule_summary": "Conduit seal required at the boundary between hazardous and non-hazardous locations, and at certain equipment entries inside the hazardous location",
    "nec_section": "501.15 (Class I), 502.15 (Class II), 505.16 (Class I Zone)",
    "boundary_seal": "Required where raceway leaves a hazardous location and enters a non-hazardous location",
    "equipment_seal": "Required at conduit entries to: (1) Class I Div 1 enclosures containing arcing/sparking devices, (2) Class I Div 1 enclosures with internal volume > 100 in³",
    "conductor_seal_compound": "Listed sealing compound; cannot use the EGC continuity through the seal — bond around with external bonding jumper"
  },
  "temperature_class_table": {
    "_source": "NEC 500.8(D) / 505.9(D) — equipment maximum surface temperature codes",
    "rows": [
      {"t_class": "T1", "max_surface_c": 450, "max_surface_f": 842},
      {"t_class": "T2", "max_surface_c": 300, "max_surface_f": 572},
      {"t_class": "T2A","max_surface_c": 280, "max_surface_f": 536},
      {"t_class": "T2B","max_surface_c": 260, "max_surface_f": 500},
      {"t_class": "T2C","max_surface_c": 230, "max_surface_f": 446},
      {"t_class": "T2D","max_surface_c": 215, "max_surface_f": 419},
      {"t_class": "T3", "max_surface_c": 200, "max_surface_f": 392},
      {"t_class": "T3A","max_surface_c": 180, "max_surface_f": 356},
      {"t_class": "T3B","max_surface_c": 165, "max_surface_f": 329},
      {"t_class": "T3C","max_surface_c": 160, "max_surface_f": 320},
      {"t_class": "T4", "max_surface_c": 135, "max_surface_f": 275},
      {"t_class": "T4A","max_surface_c": 120, "max_surface_f": 248},
      {"t_class": "T5", "max_surface_c": 100, "max_surface_f": 212},
      {"t_class": "T6", "max_surface_c":  85, "max_surface_f": 185}
    ]
  },
  "common_errors": [
    "Mixing Division-marked and Zone-marked equipment in the same location — confirm equipment listing covers both or use one system throughout",
    "Specifying T1 equipment in a hazardous location where the gas autoignition is 200 °C — must specify T3 or lower (lower number = lower surface temp = safer)",
    "Omitting the boundary seal — frequent inspection failure on retrofits where existing raceway crosses a newly classified boundary",
    "Treating gas Group IIC (acetylene + hydrogen) as covered by Group D (propane) equipment — IIC requires different equipment construction"
  ],
  "_consuming_skills": "Skills designing for industrial / chemical / fuel-dispensing facilities load this file alongside art500-506-hazardous-locations.json."
}
```

- [ ] **Step 2: Validate and commit**

```bash
python3 -c "import json; json.load(open('shared/standards/electrical/NFPA70/hazardous-locations-classification.json'))" && echo OK
git add shared/standards/electrical/NFPA70/hazardous-locations-classification.json
git commit -m "feat: NFPA70 hazardous-locations-classification.json — Division/Zone matrix + equipment selection"
```

---

## Task 31: Create ampacity-correction-factors.json (cross-cutting)

**Files:**
- Create: `shared/standards/electrical/NFPA70/ampacity-correction-factors.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "NFPA 70 — Ampacity Correction Factor Chain (cross-cutting)",
  "_version": "1.0.0",
  "_note": "Conductor ampacity corrections come from multiple sources — Table 310.16 base ampacity × Table 310.15(B)(1) ambient × Table 310.15(C)(1) grouping × 110.14(C) termination temperature limit. This file unifies the chain with a worked example.",
  "correction_chain": [
    {
      "step": 1,
      "source": "Table 310.16",
      "input": "AWG conductor size + temperature rating (60/75/90 °C)",
      "output": "Base ampacity at 30 °C ambient, ≤3 current-carrying conductors",
      "_note": "Use the column matching the conductor INSULATION temperature rating (not termination rating)"
    },
    {
      "step": 2,
      "source": "Table 310.15(B)(1)",
      "input": "Actual ambient temperature (°C)",
      "output": "Ambient correction factor (multiplier)",
      "formula": "Base ampacity × ambient correction factor"
    },
    {
      "step": 3,
      "source": "Table 310.15(C)(1)",
      "input": "Number of current-carrying conductors in raceway/cable",
      "output": "Grouping adjustment factor (% multiplier)",
      "formula": "(Base × ambient) × grouping factor",
      "_note": "Neutral conductors carrying harmonic content count as current-carrying per 310.15(E)"
    },
    {
      "step": 4,
      "source": "110.14(C) Termination Temperature Limit",
      "input": "Termination temperature rating (60 / 75 / 90 °C)",
      "output": "FINAL ampacity = min(corrected ampacity, ampacity from the lower temperature column)",
      "_note": "If terminations are 75 °C but conductor is 90 °C, the conductor's corrected ampacity is limited to the 75 °C column value (uncorrected from Table 310.16)"
    }
  ],
  "worked_example_full_chain": {
    "scenario": "Determine the ampacity of #2 AWG Cu THHN conductor in a raceway with 5 current-carrying conductors, 45 °C ambient, terminated at 75 °C rated lugs.",
    "step_1_base_ampacity": {
      "table": "310.16",
      "column": "90 °C (THHN insulation)",
      "size_awg": 2,
      "base_a": 130
    },
    "step_2_ambient": {
      "table": "310.15(B)(1)",
      "ambient_c": 45,
      "factor_90c": 0.87,
      "ampacity_after_ambient_a": "130 × 0.87 = 113.1"
    },
    "step_3_grouping": {
      "table": "310.15(C)(1)",
      "num_current_carrying": "5 (range 4-6)",
      "factor_pct": 80,
      "ampacity_after_grouping_a": "113.1 × 0.80 = 90.5"
    },
    "step_4_termination_check": {
      "rule": "110.14(C) — limit to ampacity from the termination temperature column",
      "termination_rating": "75 °C",
      "table_310_16_75c_size_2": 115,
      "termination_limit_a": "115 (uncorrected)",
      "_note": "Termination limit is BEFORE ambient/grouping correction — apply the corrections to the termination-column value AS WELL, then compare"
    },
    "step_4b_full_check": {
      "alternate_calc_at_75c": {
        "base_75c_size_2": 115,
        "ambient_correction_75c_factor": 0.82,
        "grouping_correction": 0.80,
        "result_a": "115 × 0.82 × 0.80 = 75.4"
      },
      "step_5_final": {
        "min_of": ["step 3 result: 90.5 A (from 90 °C column corrected)", "step 4b result: 75.4 A (from 75 °C column corrected)"],
        "final_ampacity_a": 75.4,
        "_note": "The termination temperature column dominates — the 90 °C conductor's higher base ampacity is wasted because terminations are 75 °C rated"
      }
    },
    "design_decision_with_this_ampacity": "75.4 A available. If circuit's design current is, say, 60 A, this works. If 80 A, oversize the conductor or upgrade terminations to 90 °C rated"
  },
  "common_errors": [
    "Skipping the 110.14(C) termination check — using just the corrected 90 °C column value when terminations are 75 °C",
    "Applying ambient OR grouping but not both — they multiply",
    "Counting neutral conductors as non-current-carrying in non-linear loads (computers, VFDs, LEDs) — 310.15(E) requires counting them in harmonic-rich loads",
    "Using the wrong correction-factor column — the column corresponds to the CONDUCTOR insulation temp, not the termination temp"
  ],
  "iec_60364_cross_reference": "IEC 60364-5-52 Annex B has corresponding ambient correction (Annex B Tables B.52.14, B.52.15) and grouping correction (Annex B Tables B.52.17). Methodology is similar but values differ slightly — and IEC has no 110.14(C)-style termination temperature limit (IEC tables assume terminations match conductor)."
}
```

- [ ] **Step 2: Validate and commit**

```bash
python3 -c "import json; json.load(open('shared/standards/electrical/NFPA70/ampacity-correction-factors.json'))" && echo OK
git add shared/standards/electrical/NFPA70/ampacity-correction-factors.json
git commit -m "feat: NFPA70 ampacity-correction-factors.json — 4-step correction chain + worked example"
```

---

## Task 32: Create conduit-fill.json (cross-cutting)

**Files:**
- Create: `shared/standards/electrical/NFPA70/conduit-fill.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "NFPA 70 — Conduit Fill (cross-cutting)",
  "_version": "1.0.0",
  "_note": "Conduit fill calculation procedure using Chapter 9 Table 1 (% allowed) + Table 4 (raceway dimensions) + Table 5 (conductor dimensions). Inline tables here are reference; full data lives in chapter9-tables.json.",
  "calculation_procedure": [
    {
      "step": 1,
      "action": "Identify the conductor types and counts to be installed",
      "data_needed": "Wire type (THHN, THWN-2, XHHW-2, etc.) + AWG/kcmil size + quantity"
    },
    {
      "step": 2,
      "action": "Look up each conductor's external area",
      "data_needed": "Chapter 9 Table 5 — gives external area in² per conductor by insulation type and size",
      "_note": "External area, NOT copper cross-section (kcmil) — external area includes the insulation"
    },
    {
      "step": 3,
      "action": "Sum total conductor area",
      "formula": "Σ (count × area_per_conductor)"
    },
    {
      "step": 4,
      "action": "Determine allowed conduit fill percentage from Table 1",
      "rule": "1 conductor: 53%; 2 conductors: 31%; 3 or more conductors: 40%",
      "_note": "≥3 conductors = 40% is the most common case in commercial work"
    },
    {
      "step": 5,
      "action": "Look up raceway internal area from Table 4",
      "data_needed": "Raceway type (RMC, IMC, EMT, PVC) + trade size",
      "output": "Total internal area (in²) at 100%; allowable area at 31%/40%/53% pre-computed in Table 4"
    },
    {
      "step": 6,
      "action": "Compare",
      "rule": "Total conductor area ≤ raceway allowable area at the appropriate % fill"
    }
  ],
  "worked_example": {
    "scenario": "Run 9 conductors of #6 AWG THHN through an EMT raceway. Determine minimum trade size.",
    "step_1_conductors": "9 × #6 AWG THHN",
    "step_2_conductor_area": "Table 5: #6 THHN external area = 0.0507 in²",
    "step_3_total_area": "9 × 0.0507 = 0.4563 in²",
    "step_4_fill_percent": "≥3 conductors → 40% allowed",
    "step_5_emt_minimum": {
      "trade_size_check_options": [
        {"trade_size_in": "1",     "emt_40pct_area_in2": 0.346, "passes": false},
        {"trade_size_in": "1 1/4", "emt_40pct_area_in2": 0.598, "passes": true}
      ],
      "minimum_emt": "1 1/4 inch EMT"
    },
    "_note": "If 1 inch EMT is preferred for space reasons, reduce to 8 conductors max (8 × 0.0507 = 0.406 in² > 0.346 → still over). 1-inch EMT max with #6 THHN is 6 conductors (6 × 0.0507 = 0.304 < 0.346 ✓)"
  },
  "special_cases": [
    {
      "case": "Same conductor type, different sizes",
      "procedure": "Sum each size's area separately, then sum all"
    },
    {
      "case": "Different conductor types",
      "procedure": "Same — each conductor's area from Table 5 column for its type"
    },
    {
      "case": "Conductors with internal grounding conductor (NM cable, MC cable)",
      "procedure": "Use the cable's total external diameter, not individual conductor sums (cables are treated as a unit)"
    },
    {
      "case": "Communications cables in same conduit as power",
      "procedure": "Generally prohibited per 800.133 (≥2 in separation required); when permitted (e.g. fiber), apply fill calc to ALL cables in the raceway"
    }
  ],
  "common_errors": [
    "Using copper kcmil area instead of external area (with insulation) — frequent error",
    "Using 53% (1-conductor) fill % for a single piece of wire in a raceway with planned future expansion — once future conductors added, 40% rule applies",
    "Forgetting to include the EGC as a counted conductor for fill — EGC contributes to total area",
    "Mixing fill % for different conductors — the entire raceway is single-fill-percent based on the highest conductor count"
  ],
  "iec_60364_cross_reference": "IEC 60364-5-52 conduit/trunking fill handled by Annex B in some national supplements (e.g. BS 7671 Appendix 4 + Appendix 6 trunking fill); the IEC base does not have a comprehensive fill table comparable to NEC Chapter 9 Table 1 + 4 + 5. NEC's approach is more codified."
}
```

- [ ] **Step 2: Validate and commit**

```bash
python3 -c "import json; json.load(open('shared/standards/electrical/NFPA70/conduit-fill.json'))" && echo OK
git add shared/standards/electrical/NFPA70/conduit-fill.json
git commit -m "feat: NFPA70 conduit-fill.json — fill calculation procedure + worked example"
```

---

## Task 33: Create wiring-methods-by-occupancy.json (cross-cutting)

**Files:**
- Create: `shared/standards/electrical/NFPA70/wiring-methods-by-occupancy.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "NFPA 70 — Wiring Methods by Occupancy (decision matrix)",
  "_version": "1.0.0",
  "_note": "Which raceway/cable types are permitted in which occupancies. Synthesized from NEC Arts 300-399 (raceway/cable type articles) + Arts 511-590 (special occupancy restrictions) + Arts 500-506 (hazardous locations).",
  "matrix": [
    {
      "wiring_method": "Nonmetallic Sheathed Cable (NM, Romex)",
      "nec_article": 334,
      "permitted_occupancies": ["one- and two-family dwellings", "multifamily dwellings (Type V construction)", "other structures permitted by 334.10"],
      "prohibited_occupancies": ["Type I-IV construction in commercial occupancies", "wet locations", "embedded in concrete", "hazardous locations (most)", "as service-entrance cable", "exposed in dropped/suspended ceilings of commercial occupancies"],
      "key_restrictions": "Cannot be exposed in dropped ceilings — must be in protective raceway above suspended ceiling tiles in commercial occupancies"
    },
    {
      "wiring_method": "Armored Cable (AC)",
      "nec_article": 320,
      "permitted_occupancies": ["Most occupancies (dry locations, exposed or concealed)", "Returns to dwellings since NEC 2017 update"],
      "prohibited_occupancies": ["Wet locations", "Direct embedded in concrete", "Hazardous locations"],
      "key_restrictions": "AC cable has a bonding strip for EGC; must terminate properly to maintain EGC continuity. Not suitable for wet locations."
    },
    {
      "wiring_method": "Metal-Clad Cable (MC)",
      "nec_article": 330,
      "permitted_occupancies": ["All occupancies — including healthcare patient care (with restrictions per 517)", "Wet locations if listed for wet location"],
      "prohibited_occupancies": ["Hazardous locations except where listed"],
      "key_restrictions": "Most versatile cable type. MC with separate EGC permitted in patient care areas (517.13)."
    },
    {
      "wiring_method": "Mineral-Insulated Cable (MI)",
      "nec_article": 332,
      "permitted_occupancies": ["All occupancies", "Hazardous locations", "Fire-rated emergency circuits (life safety, fire pump supply)"],
      "prohibited_occupancies": [],
      "key_restrictions": "Most fire-resistant cable type. Highest cost; specialized terminations."
    },
    {
      "wiring_method": "Rigid Metal Conduit (RMC)",
      "nec_article": 344,
      "permitted_occupancies": ["All occupancies", "Hazardous locations (with proper sealing per 501.15+)", "Direct buried", "Embedded in concrete"],
      "prohibited_occupancies": [],
      "key_restrictions": "Most universally accepted raceway. Heaviest steel; threaded connections."
    },
    {
      "wiring_method": "Intermediate Metal Conduit (IMC)",
      "nec_article": 342,
      "permitted_occupancies": ["Same as RMC — all occupancies, hazardous locations, direct burial, embedded"],
      "prohibited_occupancies": [],
      "key_restrictions": "Lighter than RMC but same approval scope; preferred for cost-sensitive overhead/wall work"
    },
    {
      "wiring_method": "Electrical Metallic Tubing (EMT)",
      "nec_article": 358,
      "permitted_occupancies": ["Most occupancies (dry locations primarily)", "Concealed in walls", "Above ceilings (commercial)"],
      "prohibited_occupancies": ["Direct buried", "Embedded in concrete in contact with earth", "Class I Div 1 hazardous locations", "Severe corrosive environments (without supplementary protection)"],
      "key_restrictions": "Thin-wall, not threaded. Compression or setscrew fittings only. Most common commercial raceway."
    },
    {
      "wiring_method": "Flexible Metal Conduit (FMC)",
      "nec_article": 348,
      "permitted_occupancies": ["Short runs (typically ≤6 ft) to vibrating equipment (motors, transformers)"],
      "prohibited_occupancies": ["Used as EGC where length > 6 ft or size > certain limits per 250.118(5)", "Wet locations (use LFMC instead)"],
      "key_restrictions": "Limited as EGC. Must be installed with separate EGC wire on long runs."
    },
    {
      "wiring_method": "Liquidtight Flexible Metal Conduit (LFMC)",
      "nec_article": 350,
      "permitted_occupancies": ["Outdoor connections to vibrating equipment", "Wet locations"],
      "prohibited_occupancies": [],
      "key_restrictions": "FMC + PVC sheath for outdoor / wet use"
    },
    {
      "wiring_method": "Rigid Polyvinyl Chloride Conduit (PVC) — Schedule 40/80",
      "nec_article": 352,
      "permitted_occupancies": ["Direct buried (Schedule 40 or 80)", "Concealed in walls", "Wet locations", "Sunlight-exposed (Schedule 80 only — Schedule 40 may degrade)"],
      "prohibited_occupancies": ["Hazardous locations except as permitted in 514.8 (gas stations) and similar", "Concealed in walls of dwellings if expanding into ambient temperature variation causing telegraphic movement (rare concern)"],
      "key_restrictions": "Most common underground raceway. Schedule 80 needed for direct mechanical hits/sun exposure"
    }
  ],
  "occupancy_specific_restrictions": [
    {"occupancy": "Healthcare patient care space (Category 1, 2)", "permitted": "AC, MC with insulated EGC, RMC, IMC, EMT, MI", "_note": "All require dual EGC paths per 517.13"},
    {"occupancy": "Class I Div 1 hazardous", "permitted": "RMC, IMC, listed flexible methods (LFMC type, listed Class I) with proper seals", "_note": "EMT prohibited"},
    {"occupancy": "Class I Div 2 hazardous", "permitted": "Above + EMT with listed fittings", "_note": ""},
    {"occupancy": "Assembly occupancy (>100 persons)", "permitted": "Metal raceways (RMC, IMC, EMT), MC, AC", "_note": "NM cable prohibited (518.4)"},
    {"occupancy": "Wet locations", "permitted": "RMC, IMC, PVC, LFMC, LFNC, MC listed for wet, MI", "_note": "EMT generally permitted with listed fittings; NM cable prohibited"},
    {"occupancy": "Dwelling units", "permitted": "All including NM cable (most common)", "_note": ""}
  ],
  "common_errors": [
    "Using NM cable in commercial-occupancy ceilings — must use AC, MC, or in raceway",
    "Using EMT below grade — prohibited; use RMC, IMC, or PVC for direct burial",
    "Using FMC longer than 6 ft as EGC — must install separate EGC wire OR use a wiring method with continuous EGC",
    "Using Schedule 40 PVC in sunlight-exposed locations — degrades; use Schedule 80"
  ],
  "_consuming_skills": "The sld, db-layout, panel-schedule, riser, and small-power skills should load this file when generating wiring specifications for US projects."
}
```

- [ ] **Step 2: Validate and commit**

```bash
python3 -c "import json; json.load(open('shared/standards/electrical/NFPA70/wiring-methods-by-occupancy.json'))" && echo OK
git add shared/standards/electrical/NFPA70/wiring-methods-by-occupancy.json
git commit -m "feat: NFPA70 wiring-methods-by-occupancy.json — decision matrix raceway/cable by occupancy"
```

---

## Task 34: Create amendments-summary.md

**Files:**
- Create: `shared/standards/electrical/NFPA70/amendments-summary.md`

- [ ] **Step 1: Write the file**

````markdown
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
````

- [ ] **Step 2: Commit**

```bash
git add shared/standards/electrical/NFPA70/amendments-summary.md
git commit -m "docs: NFPA70 amendments summary — 2017/2020/2023 changes + state adoption"
```

---

## Task 35: Create nec-vs-iec-comparison.md

**Files:**
- Create: `shared/standards/electrical/NFPA70/nec-vs-iec-comparison.md`

- [ ] **Step 1: Write the file**

````markdown
# NFPA 70 (NEC) ↔ IEC 60364 — Divergence Catalogue

The single most-consumed cross-jurisdiction reference. Skills working across
US/Europe/international project teams load this MD to surface differences at
design time.

---

## 1. Terminology — the silent breakers

| NEC | IEC | Why it matters |
|---|---|---|
| **Grounding** | **Earthing** | Same concept, different word. Never mix in a single drawing/spec. |
| **Grounded conductor** | **Neutral** | NEC's "grounded" because in TN-C-S the neutral IS grounded at the service |
| **Equipment grounding conductor (EGC)** | **Circuit protective conductor (CPC)** | Sizing rules differ — see Section 4 below |
| **Grounding electrode conductor (GEC)** | (no exact term; closest: main earthing conductor) | Different sizing rule |
| **Main bonding jumper (MBJ)** | Main earthing terminal connection | NEC has explicit hardware concept |
| **GFCI** Class A (4-6 mA trip) | **RCD** (typically 30 mA general use) | GFCI more sensitive than IEC RCD — different protection scope |
| **AFCI** | (no exact equivalent in IEC 60364 base) | NEC mandates; IEC 62606 (AFDD) is optional in IEC base |
| **AWG / kcmil** | **mm²** | AWG decreases as size increases; mm² is direct |
| **Branch circuit** | **Final circuit** | Same idea |
| **Feeder** | **Sub-main / distribution circuit** | NEC keeps "feeder" as distinct legal category |
| **Service** | **DNO/utility supply intake** | NEC has detailed service rules; IEC less prescriptive |
| **Ampacity** | **Current-carrying capacity (Iz)** | Same |
| **Disconnecting means** | **Isolating switch** | Same |
| **Hospital grade** | (no exact term) | NEC-specific receptacle classification (UL 498) |

---

## 2. Earthing systems

| Topic | NEC | IEC |
|---|---|---|
| TN-C permissible scope | ONLY within service equipment (250.142). After the service disconnect, neutral and EGC must be separate. | TN-C permitted throughout an installation for cables ≥10 mm² Cu / 16 mm² Al. |
| Required electrodes (250.50 / 542) | Concrete-encased electrode (Ufer) REQUIRED when present at new buildings (250.50(A)(3)). All present electrodes must be bonded together. | Concrete-encased optional. Specific electrodes mandated by national supplement. |
| Earthing system declarations | NEC does not classify systems as "TN-S / TN-C-S / TT / IT" — uses prescriptive rules (250.20 mandates grounding for certain system configurations) | IEC classifies explicitly per IEC 60364-1 Clause 312 |

---

## 3. Voltage and equipment ratings

| Topic | NEC | IEC |
|---|---|---|
| Nominal voltage (residential) | 120 V single-phase (split 240/120) | 230 V single-phase |
| Nominal voltage (3-phase commercial) | 208Y/120 V, 480Y/277 V (US wye); 240V delta common | 400Y/230 V (Europe), 415Y/240 V (UK) |
| Frequency | 60 Hz | 50 Hz |
| Working clearance (NEC 110.26) | Tabulated in ft/in by voltage × condition (1/2/3) | IEC 60364-7-729 less prescriptive — metric, fewer condition tiers |
| Termination temperature rule | NEC 110.14(C) limits conductor ampacity to terminal temperature rating | No equivalent — IEC ampacity tables (Annex B) assume terminations rated to conductor |

---

## 4. Conductor / cable sizing — the largest divergence area

| Topic | NEC | IEC |
|---|---|---|
| Conductor identification | AWG (decreasing number = larger) + kcmil (large) | mm² (direct) |
| Ampacity tables | Table 310.16 (raceway/cable), 310.17 (free air); columns by temperature rating (60/75/90 °C) | Annex B (60364-5-52); rows by installation method (A1/A2/B1/B2/C/D/E/F) and insulation type (PVC/XLPE/EPR) |
| Ambient correction | Table 310.15(B)(1) — by ambient temp × conductor temp rating | Annex B Tables B.52.14, B.52.15 |
| Grouping correction | Table 310.15(C)(1) — 4-6: 80%, 7-9: 70%, etc. | Annex B Table B.52.17 |
| EGC / CPC sizing | NEC Table 250.122 — by OCPD rating | IEC Table 54.1 — by line-conductor CSA, OR adiabatic |
| GEC sizing | NEC Table 250.66 — by largest ungrounded service conductor | No exact analogue — main earthing conductor sized adiabatically or per local supplement |

### EGC vs CPC — same circuit, different sizes

**Example:** Branch circuit on a 100 A OCPD with #4 AWG (~21 mm²) phase conductors.

- **NEC EGC (250.122):** #8 AWG (~8 mm²) — sized from the 100 A OCPD rating.
- **IEC CPC (Table 54.1):** For S = 21 mm² (>16 mm²), CPC = S/2 = ~10 mm².

The IEC CPC is larger than the NEC EGC on this example. The reverse can be true on circuits with high OCPD rating relative to phase conductor.

---

## 5. Protective devices

| Topic | NEC | IEC |
|---|---|---|
| OCPD interrupting rating | "Interrupting rating" (AIC) — single value | Icu (ultimate) and Ics (service) — two values per device |
| Series ratings | Permitted (240.86) under tested combinations | Cascading permitted (IEC 60364-4-43 Annex D) but more cautious |
| AFCI | Mandatory (210.12) — combination AFCI (UL 1699) | Optional in IEC 60364 base; IEC 62606 AFDD emerging |
| GFCI | Class A 4-6 mA (UL 943) — personnel protection | RCD 30 mA general use (IEC 61008/61009) — broader scope |
| SPD (NEC 242 / IEC 60364-4-44) | UL 1449 types 1, 2, 3, 4 | IEC 61643-11 types 1, 2, 3 |

---

## 6. Hazardous locations

| Topic | NEC | IEC |
|---|---|---|
| Classification system | Two parallel: Division (Arts 500-503, legacy US) and Zone (Arts 505-506, IEC-aligned) | Zone only (IEC 60079) |
| Gas groups | A (acetylene), B (hydrogen), C (ethylene), D (propane/methane) | IIA, IIB, IIC (with IIC most severe — covers acetylene + hydrogen) |
| Dust groups | E (metal), F (carbon), G (grain) | IIIA, IIIB, IIIC |

Equipment certified for NEC Division and IEC Zone are not freely interchangeable.
See `hazardous-locations-classification.json` for the full conversion matrix.

---

## 7. Specific applications

### EV charging

| Aspect | NEC 625 | IEC 60364-7-722 |
|---|---|---|
| Cable sizing | 125% of EVSE input current (625.41(B)) | 100% of EVSE rated current — no diversity |
| GFCI / DC leakage protection | Class A or EGFCI (625.54) integral to EVSE | Type B RCD where DC leakage > 6 mA |
| PME / TN-C-S broken-PEN protection | Not explicitly addressed | Required (IEC 60364-7-722 + national supplements) |

### PV

| Aspect | NEC 690 | IEC 60364-7-712 |
|---|---|---|
| Max voltage | 600 V dwelling, 1000 V or 1500 V non-dwelling | Typically 1500 V per national supplements |
| DC arc fault | Mandatory ≥80 V DC (690.11) | No equivalent (DC AFD emerging in IEC 60947) |
| Rapid shutdown | Mandatory on rooftop PV (690.12) | No equivalent in IEC base |
| OCPD sizing | 125% × 125% (156% of module Isc) | Iz × design current — no cascading multiplier |

### Healthcare

| Aspect | NEC 517 | IEC 60364-7-710 |
|---|---|---|
| Patient care classification | Categories 1-4 | Group 0/1/2 + safety/critical/general categories |
| Essential Electrical System | Type 1 (three branches: Life Safety / Critical / Equipment), Type 2, Type 3 | Equivalent essential power supply via 60364-7-710 |
| Isolated power | LIM (Line Isolation Monitor) per UL 1022 | IMD (Insulation Monitoring Device) per IEC 61557-8 |

### Pools / spas

| Aspect | NEC 680 | IEC 60364-7-702 |
|---|---|---|
| Receptacle clearances | Imperial (5 ft / 6-20 ft / 20 ft for pools; 10 ft for spas) | Zone-based (Zone 0, 1, 2) with metric envelopes |
| Equipotential bonding | Mandatory grid, #8 AWG solid Cu, includes pool steel + deck + fittings (680.26) | Supplementary bonding required — less prescriptive on grid construction |

---

## 8. Working clearances (110.26 vs IEC 60364-7-729)

| Voltage to ground | NEC 110.26(A)(1) — Condition 1 (live one side, no live other) | IEC 60364-7-729 |
|---|---|---|
| 0–150 V | 36 in (~915 mm) | ~700 mm typical (national variations) |
| 151–600 V | 36 in | ~700 mm |
| 601–1000 V | 36 in | 1000 mm |

NEC requires width ≥30 in OR equipment width; headroom ≥6.5 ft. IEC less prescriptive.

---

## 9. Receptacle outlet rules

| Topic | NEC | IEC |
|---|---|---|
| Spacing rule (dwelling) | "No point along wall > 6 ft from outlet" (210.52(A)) | No NEC-like rule — national supplements vary |
| Tamper-resistant requirement | Mandatory in dwelling units (406.12) | No equivalent (relies on socket design — BS 1363 shutters, Schuko, etc.) |
| Outdoor weather resistance | Listed for damp/wet + in-use cover where wet (406.9) | IP rating per IEC 60529 |
| GFCI receptacle | Class A (4-6 mA) per UL 943 | Local-RCD (30 mA general) per IEC 61008 |

---

## 10. The bottom line for designers

**On a US-only project:** Use NEC consistently. Do not introduce IEC terminology.

**On a project in an IEC jurisdiction:** Use IEC 60364 + the relevant national
supplement (BS 7671 UK, AS/NZS 3000 Australia, etc.).

**On a project with both US and IEC elements** (e.g. US-owned factory in
Europe, multinational data centre, US navy facility abroad):
- Set the primary jurisdiction in the design brief.
- Document the terminology choice (one OR the other).
- Cross-reference both standards on items with significant divergence (grounding,
  conductor sizing, hazardous locations, healthcare, EV/PV).
- Engage the AHJ early — they decide which standard applies and which deviations
  are acceptable.

This MD covers the most-cited differences. For the full divergence per article,
each NEC article's `divergence_notes` field in the per-article JSON files
captures the specific divergence at that article level.
````

- [ ] **Step 2: Commit**

```bash
git add shared/standards/electrical/NFPA70/nec-vs-iec-comparison.md
git commit -m "docs: NFPA70 nec-vs-iec-comparison — terminology, sizing, devices, applications divergence"
```

---

## Task 36: Create compliance-checklist.md

**Files:**
- Create: `shared/standards/electrical/NFPA70/compliance-checklist.md`

- [ ] **Step 1: Write the file**

````markdown
# NFPA 70 (NEC 2023) — Designer Compliance Checklist

Project-type-organised checklist of NEC compliance items every MEP designer
must verify before AHJ submission.

---

## Universal items (every project)

- [ ] Confirm AHJ's adopted NEC edition (2017 / 2020 / 2023 / state-specific)
- [ ] Confirm state and local amendments
- [ ] Available fault current at each service / panelboard documented (110.10, 110.24)
- [ ] Working clearances (110.26) on all panel layouts
- [ ] Termination temperature rating (60/75/90 °C) stated on each conductor schedule
- [ ] Arc-flash hazard warning labels (110.16) on equipment likely to require energised work

---

## Residential (single-family dwelling)

- [ ] Service entrance ≥100 A (typical 200 A); calc per Art 220 (Standard 220.40 OR Optional 220.82)
- [ ] Outside emergency disconnect at meter or near service (230.85 — NEC 2020+)
- [ ] Service disconnect within ≤2 m of building entrance or at the meter
- [ ] Grounding electrode system per 250.50 — all present electrodes bonded (including Ufer if present)
- [ ] AFCI per 210.12 — kitchens, bedrooms, living, dining, family, closets, hallways, laundry
- [ ] GFCI per 210.8 — bathrooms, kitchens, dishwasher, laundry, garage, outdoor, basements, crawl space, near sinks
- [ ] TR (tamper-resistant) receptacles per 406.12 — all 15/20 A 125 V dwelling outlets
- [ ] Receptacle spacing per 210.52(A) — wall-space rule (no point > 6 ft from outlet)
- [ ] Two small-appliance kitchen circuits (20 A dedicated)
- [ ] Dedicated 20 A laundry circuit; dedicated 20 A bathroom receptacle circuit

---

## Commercial occupancies

- [ ] Load calc per Art 220 — Standard method 220.40 (Optional 220.84 multi-family doesn't apply here)
- [ ] Service ≥ calculated demand; conductor sizing 125% continuous + 100% non-continuous (215.2)
- [ ] GFP at service ≥1000 A (230.95) — performance test required
- [ ] Selective coordination on emergency / legally req'd standby circuits (700.32 / 701.32)
- [ ] Wiring methods per occupancy table (in wiring-methods-by-occupancy.json)
- [ ] Working clearances (110.26) — confirm 36 in for 480 V or less; 42 in for ≤600 V with energised parts both sides
- [ ] Bathroom GFCI (210.8(B)(1)); kitchen GFCI (210.8(B)(2)); rooftop GFCI (210.8(B)(3))

---

## Industrial / manufacturing

- [ ] Industrial machinery (Art 670 + NFPA 79) — SCCR ≥ available fault current
- [ ] Motor circuits sized per 430.22 (125% × Table 430.250 FLA)
- [ ] Motor OCPD per 430.52 (typical 250% inverse-time CB, 175% dual-element time-delay fuse)
- [ ] Motor disconnect within sight (430.102) — visible from controller AND motor
- [ ] Hazardous locations classified per 500-506 (Division) or 505-506 (Zone)
- [ ] Equipment listed for the Class/Division (or Class/Zone) at every location
- [ ] Conduit seals at hazardous-to-non-hazardous boundary (501.15 et al.)
- [ ] Stationary battery / ESS per Art 480 + Art 706 (UL 9540 listing)

---

## Healthcare

- [ ] Patient care space categories (1-4) marked on drawings (517.2)
- [ ] Dual EGC paths in Category 1 + 2 patient care (517.13)
- [ ] Type 1 EES (hospital) — three branches: Life Safety, Critical, Equipment (517.30+)
- [ ] Generator start ≤10 s, sized for all Type 1 EES loads (517.30 + Art 700)
- [ ] Isolated power systems with LIM at wet locations (ORs, etc.) (517.160)
- [ ] Hospital-grade receptacles (UL 498 hospital grade) in patient-care spaces
- [ ] Anesthetizing locations — if applicable, classify and select equipment (517.60)

---

## EV charging installations (Art 625)

- [ ] Branch circuit ≥125% of EVSE input current (625.41(B))
- [ ] OCPD ≥125% of EVSE input current ≤ branch circuit ampacity
- [ ] GFCI (Class A or EGFCI) — integral to listed EVSE; external for receptacle-type
- [ ] Disconnect within sight (625.43) for EVSE >60 A or >150 V to ground
- [ ] Load management documented for multi-EVSE feeders (625.42(A)(2))
- [ ] Ventilation per 625.52 (rarely needed for modern Li-ion vehicles but rule still applies)

---

## PV installations (Art 690 + 705)

- [ ] Max voltage per 690.7 (600 V dwelling, 1000/1500 V non-dwelling) with cold-temp Voc adjustment
- [ ] OCPD ≥156% of module Isc (125% × 125% per 690.9)
- [ ] DC AFCI on PV source circuits ≥80 V DC (690.11)
- [ ] Rapid shutdown on rooftop PV (690.12) — markings + initiation device location
- [ ] Interconnection per 705.12 — sum rule, 120% rule, or center-fed rule documented
- [ ] PV system GES bonded with AC GES (250.50 + 690.47)
- [ ] System labelling: PV system, rapid shutdown, AC/DC junction boxes, etc. (690.4(D), 690.13(B))

---

## Fire pumps (Art 695)

- [ ] Reliable power source (utility OR on-site generator) (695.3)
- [ ] No disconnect on fire pump supply (except listed controller's) (695.4)
- [ ] Voltage drop ≤15% at motor start, ≤5% at run (695.7)
- [ ] Conductor ampacity ≥125% fire pump motor + accessories (695.6)
- [ ] Coordinate with NFPA 20 (Fire Pumps) standard
- [ ] Listed fire pump controller (NFPA 20-listed)

---

## Energy storage systems (Art 706)

- [ ] ESS listed per UL 9540 (706.4)
- [ ] ESS components listed per UL 9540A (thermal runaway test) for batteries
- [ ] Disconnect within sight or lockable remote (706.7)
- [ ] Location compliance with NFPA 855 separation rules
- [ ] If PV-coupled: rapid shutdown coverage per 690.12

---

## Hazardous locations (Art 500-506)

- [ ] Classification documented (Class/Division OR Class/Zone)
- [ ] Material groups identified (A/B/C/D gas; E/F/G dust; or IIA/IIB/IIC, IIIA/IIIB/IIIC)
- [ ] Equipment listing matches Class/Division/Group (or Zone/Group)
- [ ] Temperature class (T1-T6) ≤ material auto-ignition temperature
- [ ] Conduit seals at boundary (501.15) + at appropriate equipment entries
- [ ] Intrinsically safe loop calculation if Art 504 applied (entity parameters Voc/Isc/Pi/Po/Ci/Li)
- [ ] Maintenance work permit / hot work permit procedures coordinated with operations

---

## At AHJ submission

- [ ] Complete drawing set (one-line, panel schedules, layouts, details)
- [ ] Calculations (load, fault current, voltage drop, conduit fill, ampacity)
- [ ] Equipment specifications including SCCR
- [ ] AHJ-specific submission forms (varies by jurisdiction)
- [ ] Coordination study (where required by 700.32 / 701.32 / 645.27 / 695.6)
- [ ] Listing letters for listed equipment that AHJ requires
- [ ] Engineer of record signature + seal as required

---

## Field marking (commissioning)

- [ ] Available fault current at each panelboard (110.24)
- [ ] Date of fault current marking (110.24(B))
- [ ] Arc-flash hazard warning (110.16)
- [ ] PV system markings per 690.4(D) + 690.13(B) + 705.10
- [ ] Rapid shutdown markings per 690.12(C)
- [ ] Hospital essential electrical system identification (517.30(E))
- [ ] Power-source identification at stand-alone systems (710.10)
- [ ] ESS disconnect marking (706.7(E))
````

- [ ] **Step 2: Commit**

```bash
git add shared/standards/electrical/NFPA70/compliance-checklist.md
git commit -m "docs: NFPA70 compliance checklist — designer-side reqs by project type"
```

---

## Task 37: Create terminology.md

**Files:**
- Create: `shared/standards/electrical/NFPA70/terminology.md`

- [ ] **Step 1: Write the file**

````markdown
# NFPA 70 (NEC) — Terminology Glossary

NEC-vs-IEC critical-distinction glossary. Every term that has been a source of
confusion in cross-jurisdiction projects is captured here.

---

## Grounding vs Earthing

| NEC term | IEC term | Notes |
|---|---|---|
| Grounding | Earthing | Same concept. Use only one term in any single document. |
| Ground | Earth | Same |
| Grounding electrode | Earth electrode | Same |
| Grounding electrode system (GES) | Earth electrode system | Same |
| Grounding electrode conductor (GEC) | Main earthing conductor (closest analogue) | NEC sizes from largest ungrounded service conductor; IEC sizes adiabatically |
| Equipment grounding conductor (EGC) | Circuit protective conductor (CPC) | NEC sizes by OCPD rating (250.122); IEC sizes by line CSA (Table 54.1) |
| Bonding | Bonding | Same |
| Main bonding jumper (MBJ) | (no exact equivalent) | NEC has this as explicit hardware concept at service |
| System bonding jumper | Bonding jumper at SDS / first separately-derived disconnect | NEC vs IEC have similar concept different names |

## Neutral

| NEC term | IEC term | Notes |
|---|---|---|
| Grounded conductor | Neutral (N) in TN systems | NEC uses "grounded" because in TN-C-S the neutral IS grounded at the service |
| Neutral conductor | Neutral | Same — NEC distinguishes "grounded" (the bonded one) from "neutral" (carries current); sometimes the same, sometimes not |
| Multiwire branch circuit | (no exact equivalent) | NEC concept of shared neutral on multi-phase circuits — not common in IEC; IEC 60364 generally requires separate neutrals |

## Circuit roles

| NEC term | IEC term | Notes |
|---|---|---|
| Service | Origin of installation / supply intake | NEC distinguishes "service" as a legal entity (the utility connection point) |
| Feeder | Sub-main / distribution circuit | Same concept |
| Branch circuit | Final circuit | Same |
| Tap | Tap (similar) | NEC has tap rules (240.21) with explicit length limits; IEC less prescriptive |

## Conductor identification

| NEC term | IEC term | Notes |
|---|---|---|
| AWG (American Wire Gauge) | mm² | Inverse relationship: smaller AWG number = larger conductor; mm² is direct |
| kcmil (thousand circular mils) | mm² | Used for AWG-equivalents larger than 4/0 — e.g. 250 kcmil ≈ 127 mm² |
| Solid / stranded | Same | Same |
| Cu / Al | Cu / Al | Same |

## Protective devices

| NEC term | IEC term | Notes |
|---|---|---|
| OCPD (overcurrent protective device) | Overcurrent protective device | Same generic term |
| Fuse | Fuse | Same |
| Circuit breaker | Circuit breaker / MCB / MCCB | NEC doesn't distinguish MCB/MCCB by acronym — both are "circuit breaker" |
| Interrupting rating | Icu (ultimate) and Ics (service) | NEC has one rating; IEC two values per device |
| AIC | Icu (ultimate equivalent) | "Amps Interrupting Capacity" — NEC name for AIC equates to IEC's Icu |
| Frame rating | Frame size | Same |
| GFCI | RCD (functional equivalent, different trip level) | GFCI Class A = 4-6 mA; IEC general-use RCD = 30 mA |
| AFCI | (no exact equivalent in IEC 60364 base) | NEC mandates; IEC 62606 AFDD is optional |

## Receptacles / outlets

| NEC term | IEC term | Notes |
|---|---|---|
| Receptacle | Socket outlet | Same |
| Outlet | Outlet | NEC distinguishes "outlet" (a point on the wiring system) from "receptacle" (the actual device) |
| Hospital grade | (no exact term) | NEC-specific UL 498 hospital-grade receptacle |
| Tamper-resistant (TR) | (no equivalent term) | NEC mandates in dwellings; IEC sockets have inherent safety via BS 1363 shutters etc. |
| Weather-resistant (WR) | (similar via IP rating) | NEC term; IEC handles via IP per IEC 60529 |
| Listed | (Certification mark — UL/CSA/ETL) | NEC-specific "listed by NRTL" |

## Voltage / current / power

| NEC term | IEC term | Notes |
|---|---|---|
| Volts (V) | Volts (V) | Same — values differ between NEC 60 Hz US and IEC 50 Hz international |
| Amperes (A) | Amperes (A) | Same |
| VA (volt-amperes) | VA | NEC uses VA frequently in load calc; IEC uses kVA more often |
| Horsepower (hp) | kW | NEC uses hp for motors (especially with Table 430.250 FLA); IEC uses kW |
| RLA (rated-load current) for AC compressors | Rated current | NEC-specific construct for Art 440 (hermetic compressors) |
| Power factor (PF) | Power factor / cos φ | Same |

## Wiring methods

| NEC term | IEC term | Notes |
|---|---|---|
| Raceway | Conduit / cable trunking / tray system | NEC umbrella term covers conduit/trunking/cable tray etc. |
| Conduit | Conduit | Same |
| Cable tray | Cable tray | Same |
| Wireway | Cable trunking with internal access | NEC-specific (NEC Art 376/378) |
| NM (Nonmetallic-Sheathed Cable, Romex) | (no exact equivalent in common use) | NEC dwelling cable; IEC typically uses singles in conduit/trunking |
| AC (Armored Cable) | (similar to armoured cable) | NEC AC has internal bonding strip; IEC armoured cable uses SWA |
| MC (Metal-Clad Cable) | (closest: SWA + LSZH cable) | NEC MC has separate EGC inside |
| MI (Mineral-Insulated) | MICC (Mineral Insulated Copper-Clad) | Same |
| EMT (Electrical Metallic Tubing) | (closest: light gauge steel conduit) | NEC-specific |
| RMC (Rigid Metal Conduit) | Heavy gauge steel conduit | Same idea |
| IMC (Intermediate Metal Conduit) | (between EMT and RMC) | NEC-specific intermediate weight |
| PVC | uPVC conduit | Same |
| FMC (Flexible Metal Conduit) | Flexible steel conduit | Same |
| LFMC (Liquidtight Flexible Metal Conduit) | Flexible steel conduit with thermoplastic cover | Same |
| LFNC | Liquidtight flexible nonmetallic conduit | Same |

## Special locations and systems

| NEC term | IEC term | Notes |
|---|---|---|
| Hazardous (Classified) location | Hazardous area | Same concept |
| Class I / II / III | (IEC uses category zones only) | NEC has both Division and Zone systems |
| Division 1 / 2 | Zone 0 / 1 / 2 (gas), Zone 20 / 21 / 22 (dust) | See hazardous-locations-classification.json for conversion |
| Group A/B/C/D (gases) | IIA / IIB / IIC | NEC Groups A and B map to IEC IIC |
| Group E/F/G (dusts) | IIIA / IIIB / IIIC | Approximate equivalence |
| Wet location | Damp/wet location | Same |
| Damp location | Damp location | Same |
| Healthcare patient care space Category 1-4 | Group 0/1/2 medical locations | Different classification details |
| Type 1 / 2 / 3 Essential Electrical System | Essential power supply (similar) | NEC has three-branch Type 1; IEC has equivalent grouped power supplies |

## Project roles

| NEC term | IEC term | Notes |
|---|---|---|
| AHJ (Authority Having Jurisdiction) | Approving authority / building control | NEC's AHJ is the enforcement authority — varies by state/locality |
| Electrical inspector | Inspector | Same |
| Listed (by an NRTL) | Certified (by a national mark — CE, UKCA, etc.) | Different regimes |
| Identified (per its listing) | Suitable for the application | Same concept |

---

## When in doubt

If you must use BOTH NEC and IEC terms in a document:
1. Define each term explicitly at first use
2. Pick one as primary throughout and put the other in parentheses
3. Note in the design narrative which standard is the authoritative reference

The single biggest source of cross-jurisdiction confusion is grounding vs
earthing. Always pick one and stick with it.
````

- [ ] **Step 2: Commit**

```bash
git add shared/standards/electrical/NFPA70/terminology.md
git commit -m "docs: NFPA70 terminology — comprehensive NEC↔IEC glossary"
```

---

## Task 38: Create worked-examples.md

**Files:**
- Create: `shared/standards/electrical/NFPA70/worked-examples.md`

- [ ] **Step 1: Write the file**

````markdown
# NFPA 70 (NEC) — Worked Examples

7 worked examples covering the highest-value design territory. Each follows
the structure: **Given inputs → NEC article path → Calculation → Decision → AHJ-acceptance note**.

---

## Example 1 — Single-family dwelling 200 A service load calc

### Inputs

- 2400 ft² dwelling, single-phase 120/240 V, 200 A service
- Cooking: 8 kW range, 1.2 kW oven (separate), 0.8 kW microwave
- Laundry: dryer 5 kW
- Water heater: 4.5 kW
- HVAC: 3.5-ton AC (24 A on 240 V), 8 kW heat strip backup

### NEC article path

- Art 220 (load calculations) — two methods available: Standard (220.40) and Optional (220.82). Choose smaller.
- Art 220.12 (general lighting load by occupancy)
- Art 220.55 (cooking equipment demand)
- Art 220.82(C) (Optional HVAC inclusion)

### Calculation — Standard Method (220.40)

| Load category | VA | Demand factor | Calc demand |
|---|---|---|---|
| General lighting (3 VA × 2400 ft²) | 7,200 | 100% on first 3,000 + 35% remainder | 3,000 + 35% × 4,200 = 4,470 |
| Two small-appliance branch circuits | 3,000 | 100% on first 3,000 + 35% remainder (combined with lighting) | (included above) |
| Laundry branch circuit | 1,500 | 100% / 35% (combined) | (included above) |
| Cooking — range 8 kW + oven 1.2 kW + microwave 0.8 kW (10 kW total) | 10,000 | Table 220.55 Note 4: 80% for total ≥3.5 kW = 8,000 | 8,000 |
| Dryer | 5,000 | 100% (≤4 units) | 5,000 |
| Water heater | 4,500 | 100% | 4,500 |
| HVAC larger of: AC (5,760 VA) or heat (8,000 VA) | 8,000 | 100% | 8,000 |
| **Total demand** | | | **29,970 VA** |

Standard method: 29,970 / 240 = 125 A → 200 A service adequate.

### Calculation — Optional Method (220.82)

| Load category | VA | Demand factor | Calc demand |
|---|---|---|---|
| General loads: lighting (7,200) + small-appl (3,000) + laundry (1,500) + range/oven/microwave (10,000) + dryer (5,000) + water heater (4,500) | 31,200 | 100% first 10 kVA + 40% remainder | 10,000 + 40% × 21,200 = 18,480 |
| HVAC (larger of AC or heat) | 8,000 | 100% | 8,000 |
| **Total demand** | | | **26,480 VA** |

Optional method: 26,480 / 240 = 110 A → smaller than Standard. Use Optional.

### Decision

Service ampacity 110 A required; 200 A service is well-sized with spare capacity.

### AHJ note

Document the calculation choice on the load calc sheet. Optional Method is
common for residential because it usually gives a lower (compliant) service
size. Pre-built dwelling forms (CEC plan check, etc.) typically accept either.

---

## Example 2 — Strip mall service & feeder design

### Inputs

- 3 retail units, each 2,000 ft²; 1 restaurant unit 3,500 ft²
- 480Y/277 V 3-phase service for lighting/HVAC; 208/120 V transformed at each tenant
- Retail: lighting 3 VA/ft² + receptacles 30 outlets × 180 VA + 5-ton AC each
- Restaurant: kitchen equipment 35 kVA + lighting 3 VA/ft² + 7.5-ton AC

### NEC article path

- Art 215 (feeders)
- Art 220.42 (general lighting demand factors for non-dwelling — Table 220.42)
- Art 220.44 (receptacle demand factor — 100% first 10 kVA, 50% remainder)
- Art 230 (services — single service for the strip mall, with sub-feeders to each tenant)
- Art 240.21 (feeder taps — relevant if any tenant > 200 A)

### Calculation per tenant — Retail (2,000 ft²)

| Load | VA | Demand factor | Calc demand |
|---|---|---|---|
| Lighting (3 × 2,000) | 6,000 | 100% non-continuous, 125% if continuous (assume continuous) | 6,000 × 1.25 = 7,500 |
| Receptacles (30 × 180) | 5,400 | 100% first 10 kVA, 50% > 10 kVA → 5,400 × 100% | 5,400 |
| AC 5-ton | ~6,000 | 100% | 6,000 |
| **Total per retail tenant** | | | **18,900 VA** |

### Calculation — Restaurant tenant

| Load | VA | Demand factor | Calc demand |
|---|---|---|---|
| Lighting (3 × 3,500 × 1.25 cont.) | 13,125 | | 13,125 |
| Receptacles (20 × 180) | 3,600 | 100% | 3,600 |
| AC 7.5-ton | ~9,000 | 100% | 9,000 |
| Kitchen equipment (Table 220.56 demand) | 35,000 × 1.0 demand factor (≤2 units) | 35,000 |
| **Total restaurant** | | | **60,725 VA** |

### Total demand

3 × 18,900 + 60,725 = 117,425 VA. At 480Y/277 V: 117,425 / (480 × √3) ≈ 141 A. Use 200 A main with 30% spare.

### Decision

- 200 A 480Y/277 V main service
- Sub-feeders to each tenant sized per tenant load
- Coordinate tenant meters with utility

### AHJ note

Use Standard Method (220.40) — multi-occupancy strip mall, individual tenant
calc per Art 220.12-44. Receptacle demand factor (220.44) is generous for
commercial; coordinate with the demand factor early.

---

## Example 3 — Motor circuit, 50 hp 460 V 3-phase

### Inputs

- 50 hp 460 V 3-phase induction motor, Service Factor 1.15
- Locked rotor code F (3.55-3.9 kVA per hp ratio of locked rotor to full load)

### NEC article path

- Art 430.6 (full-load current from Table 430.250)
- Art 430.22 (conductor sizing)
- Art 430.32 (overload)
- Art 430.52 (branch-circuit OCPD)
- Art 430.102 (disconnect within sight)
- Art 250.122 (EGC)

### Calculation

**Step 1 — FLA from Table 430.250:** 50 hp 460 V 3-phase → 65 A FLA.

**Step 2 — Branch-circuit conductor (430.22):** 65 × 125% = 81.25 A → smallest THWN-2 conductor at 75 °C column meeting ≥81.25 A → #4 AWG Cu (ampacity 85 A).

**Step 3 — Overload (430.32):** 65 A × 115% = 74.75 A (SF 1.15). Overload set ≤74.75 A. Use NEMA size 4 starter with adjustable thermal overload set at 75 A.

**Step 4 — Branch-circuit OCPD (430.52 Table 430.52(C)(1)):**
- Inverse-time circuit breaker: 65 × 250% = 162.5 A → use 175 A breaker (next standard size up per 240.6)
- Dual-element time-delay fuse: 65 × 175% = 113.75 A → use 125 A fuse

Engineer choice (typical): 175 A inverse-time circuit breaker.

**Step 5 — Disconnect (430.102):** Disconnect within sight of motor. Use 200 A 3-pole disconnect rated for motor service.

**Step 6 — EGC (250.122 Table):** OCPD = 175 A → EGC = #6 Cu (Table 250.122).

### Decision

| Component | Size | Notes |
|---|---|---|
| Branch-circuit conductor | #4 AWG Cu THWN-2 (3-phase + #6 EGC) | At 75 °C ampacity 85 A ≥ 81.25 A required |
| Overload | NEMA 4 starter, thermal element set at 75 A | |
| Branch-circuit OCPD | 175 A inverse-time CB | Per 430.52 |
| Disconnect | 200 A 3P disconnect, within sight of motor | |
| EGC | #6 Cu | Per Table 250.122 |

### AHJ note

Submit motor schedule showing TABLE FLA used for conductor/OCPD and
NAMEPLATE FLA for overload — these are DIFFERENT values per 430.6.

---

## Example 4 — Gas station forecourt hazardous location

### Inputs

- Gasoline dispenser island, 4 dispensers, fuel-tank vents at site perimeter
- Need to classify the forecourt and size raceway/equipment

### NEC article path

- Art 514 (motor fuel dispensing)
- Art 500-503 (hazardous Class/Division) OR Art 505-506 (Class/Zone)
- Art 501.15 (seal-off requirements)

### Classification (514.3)

**Class I Locations:**

| Location | Class/Division | Class/Zone equivalent |
|---|---|---|
| Inside dispenser | Class I Div 1 | Class I Zone 0/1 |
| Within 18 in of grade, 20 ft horizontal from dispenser | Class I Div 2 | Class I Zone 2 |
| Tank vent: within 3 ft | Class I Div 1 | Zone 1 |
| Tank vent: 3-10 ft | Class I Div 2 | Zone 2 |

### Equipment selection

Equipment within the Class I Div 2 envelope must be either:
- Listed for Class I Div 2 (Group D — gasoline), OR
- Listed for Class I Zone 2 IIA (gasoline), and the equipment must be marked accordingly

Mixing Division-listed and Zone-listed equipment in the same envelope is
permitted IF the AHJ accepts the conversion matrix (see
hazardous-locations-classification.json). Best practice: pick one system
per project.

### Conduit seals (501.15)

- At the boundary where raceway exits the Class I Div 2 envelope, install a Class I Div 2 listed seal-off (e.g. EYS-style)
- Within the dispenser, additional seals at equipment entries containing arcing devices

### Decision

- Specify equipment listed for Class I Div 1 (in the dispenser) and Class I Div 2 (in the 18-in/20-ft envelope)
- Seal-off conduit fittings at boundary and at dispenser entries
- Use RMC or IMC raceway in Class I Div 1; EMT not permitted in Class I Div 1

### AHJ note

Document the classification plan on the site drawing — many AHJs require
the classification envelope to be shaded on the layout. Coordinate with
the fuel-tank installer and the tank-vent location.

---

## Example 5 — PV residential rooftop 10 kW

### Inputs

- 10 kW residential PV (32 modules at 320 W each), 8 strings of 4 modules each, 240 V single-phase grid-tie inverter
- Module Voc 40 V, Vmp 32 V, Isc 10 A, Imp 9.4 A
- Coldest expected temp at site: -10 °C (correction factor 1.10 per Table 690.7(A))
- Backfeed circuit breaker at panelboard with 200 A main breaker, 200 A busbar

### NEC article path

- Art 690.7 (max voltage)
- Art 690.8 (circuit sizing)
- Art 690.9 (OCPD)
- Art 690.11 (DC arc fault)
- Art 690.12 (rapid shutdown)
- Art 705.12(B) (interconnection at busbar — sum rule vs 120% rule)

### Calculation

**Step 1 — Maximum system voltage (690.7):**
4 modules × 40 V Voc × 1.10 (cold-temp correction) = 176 V DC per string. Well within 600 V dwelling limit.

**Step 2 — PV source circuit current (690.8):**
1 string × 10 A Isc × 125% = 12.5 A. Conductor ampacity needs ≥12.5 A × 125% = 15.625 A. Use #10 AWG PV wire (ampacity 30-40 A in free air, easily meets).

**Step 3 — PV output circuit current (690.8):**
8 strings × 12.5 A = 100 A per inverter input. Conductor sized at 100 × 125% = 125 A → #1 AWG Cu THWN-2 at 75 °C ampacity 130 A.

**Step 4 — OCPD on PV output (690.9):** ≥156% of Isc = 100 × 156% = 156 A. Round up to 175 A standard size.

**Step 5 — Inverter AC output:** 10 kW / 240 V = 41.7 A. AC output conductor at 125% × 41.7 = 52.1 A. Use #6 Cu, ampacity 65 A at 75 °C.

**Step 6 — AC OCPD (705.12 interconnection):** Inverter output breaker at 60 A (covers 52.1 A × 125% margin).

**Step 7 — 705.12 busbar interconnection rule:**
- Sum rule: 60 A inverter breaker + 200 A main breaker = 260 A > 200 A busbar. FAILS sum rule.
- 120% rule: 200 A × 120% = 240 A. 60 + 200 = 260 A > 240 A. STILL FAILS.
- Solution: Downgrade main breaker OR upgrade busbar OR use center-fed busbar configuration.
- For typical residential, this often requires a "supply-side" tap (PV breaker between meter and main panel) per 705.12(A).

**Step 8 — Rapid shutdown (690.12):**
- Conductors within 1 ft of array on roof → ≤30 V within 30 s
- Conductors > 5 ft outside array (e.g. running to inverter) → de-energized to ≤30 V within 30 s
- Module-level rapid shutdown initiator (typically MLPE microinverter or rapid-shutdown box at array)
- Marking on roof, at array boundary, at first responder location

**Step 9 — DC AFCI (690.11):**
Required because system operates ≥80 V DC. Modern inverters with integrated DC AFCI satisfy this.

### Decision

- 8 strings × 4 modules each, 176 V DC max system voltage
- DC conductors: #10 AWG PV wire (source) → #1 AWG Cu (output to inverter, 125% margin)
- AC conductor: #6 Cu (60 A breaker)
- Interconnection: supply-side tap between meter and main panel (705.12(A))
- Module-level rapid shutdown initiator
- DC AFCI per integrated inverter feature

### AHJ note

Submit single-line diagram showing all DC and AC circuits with OCPD ratings,
conductor sizes, and the rapid-shutdown plan. Most jurisdictions require
plan check before installation.

---

## Example 6 — EV charging, 5-station commercial bay

### Inputs

- 5 × 32 A Level 2 EVSE (J1772), 7.7 kW each, 240 V single-phase
- All on a shared feeder with load management; want to minimize feeder size

### NEC article path

- Art 625.41 (branch-circuit conductor sizing)
- Art 625.42 (rating + load management)
- Art 215 (feeder sizing)
- Art 240 (OCPD)

### Calculation

**Without load management (worst case — all 5 EVSEs at max simultaneously):**

5 × 32 A × 125% (continuous) = 200 A on the feeder.

**With load management (625.42(A)(2)):**

Suppose load management limits the feeder to 100 A maximum (managing power distribution among connected vehicles).

- Feeder ampacity ≥ 100 A × 125% = 125 A
- Each EVSE branch circuit: 32 A × 125% = 40 A conductor (use #8 Cu THWN-2 at 75 °C ampacity 50 A)
- Each EVSE OCPD: 40 A
- Feeder conductor: 125 A → #1 Cu THWN-2 (75 °C 130 A)
- Feeder OCPD: 125 A

### Documentation requirements

- Load management scheme documented on the design narrative
- Compliance with 625.42(A)(2): "An automatic load management system ... that is listed for the purpose..."
- Identification at the feeder: "EV charging load management to 100 A maximum"

### Decision

- 5 × 40 A 1-pole branch circuits, #8 Cu each
- Feeder 125 A, #1 Cu, with documented load management to 100 A
- 200 A feeder is over-sized without load management; 125 A with — major cost savings

### AHJ note

Load management is the most common path for multi-EVSE installations. Submit
the load management documentation explicitly — the AHJ will verify that
without it, the feeder would need to be 200 A.

---

## Example 7 — Hospital essential electrical system

### Inputs

- 200-bed hospital, mixed Category 1 (ICU, OR) + Category 2 (patient rooms) areas
- Required: Type 1 EES per Art 517.30 — three branches (Life Safety, Critical, Equipment)
- On-site standby generator + utility service

### NEC article path

- Art 517.30 (Type 1 EES — three branches)
- Art 517.31 (Type 1 distribution and wiring)
- Art 700 (Emergency System — Life Safety Branch)
- Art 700.27 / 700.32 (selective coordination)

### Architecture

**Type 1 EES three branches** (all on the EES bus, all transfer-switched):

| Branch | Loads | Restoration time |
|---|---|---|
| Life Safety Branch | Emergency egress lighting, fire alarm, exit signs, medical gas alarms | ≤10 s |
| Critical Branch | Patient-care receptacles in Category 1/2 spaces, isolated power systems, certain HVAC | ≤10 s |
| Equipment Branch | Equipment essential to facility operation (sterilization, refrigeration of pharma, etc.) | ≤10 s (or up to 60 s for some Equipment Branch loads) |

### Source transfer

- Two independent sources: utility (Primary) + on-site generator (Alternate)
- Generator sized to carry ALL three branches simultaneously
- Three transfer switches (one per branch) — typically located close to the EES bus
- Generator start ≤10 s; generator capable of sustained operation ≥1.5 hours minimum (per 517.30(C)(3))

### Selective coordination (700.32 / 701.32)

- OCPDs on Type 1 EES branches must selectively coordinate with all upstream OCPDs in the full available fault-current range
- Engagement of a coordination study with the OCPD manufacturer at design stage

### Wiring (517.31, 700.10)

- Critical Branch wiring INDEPENDENT of normal-source wiring (separate raceway, separate distribution)
- Life Safety Branch wiring also independent — most prescriptive
- Equipment Branch may share raceways with Critical Branch under certain conditions (517.31(A))

### Decision

- Three separate EES distribution panels (Life Safety, Critical, Equipment)
- Three independent transfer switches per 517.31(C)
- Generator sized for all three branches simultaneously
- Coordination study verifying selective coordination per 700.32

### AHJ note

Coordinate with NFPA 99 (Health Care Facilities Code) and the AHJ's hospital
review process. Most state health departments have additional requirements
beyond NEC + NFPA 99.

---

These 7 worked examples cover the highest-value NEC design territory.
For additional examples on specific articles, see the per-article JSON
files' `usage_notes` and `common_errors` fields.
````

- [ ] **Step 2: Commit**

```bash
git add shared/standards/electrical/NFPA70/worked-examples.md
git commit -m "docs: NFPA70 worked examples — 7 scenarios (dwelling, strip mall, motor, haz loc, PV, EV, hospital)"
```

---

## Task 39: Final verification

**Files:**
- Verify: full `shared/standards/electrical/NFPA70/` directory

- [ ] **Step 1: Verify all 39 files present**

Run:
```bash
ls -1 shared/standards/electrical/NFPA70/ | wc -l
ls -1 shared/standards/electrical/NFPA70/
```
Expected: count = 39; list contains README.md, meta.json, 9 chapter*.json, 17 art*.json, 6 cross-cutting *.json (grounding-and-bonding, ocpd-coordination, hazardous-locations-classification, ampacity-correction-factors, conduit-fill, wiring-methods-by-occupancy), 5 *.md (amendments-summary, nec-vs-iec-comparison, compliance-checklist, terminology, worked-examples).

- [ ] **Step 2: Verify all JSON files parse**

Run:
```bash
for f in shared/standards/electrical/NFPA70/*.json; do
  python3 -c "import json; json.load(open('$f'))" && echo "$f OK" || echo "$f FAIL"
done
```
Expected: every line ends `OK`.

- [ ] **Step 3: Verify per-article schema compliance**

Article-shaped files = the 9 chapter JSONs + 17 article JSONs. Each contains an `articles` array with the 17 mandatory fields per entry.

Run:
```bash
python3 - <<'PY'
import json, glob
req=['article_id','nec_ref','chapter','article_number','article_title','scope','applies_to','key_sections','tabulated_values','tables_inline','common_errors','drawn_as','related_iec_60364','divergence_notes','related_bs_7671','usage_notes','related_articles']
article_files = []
for pattern in ['shared/standards/electrical/NFPA70/chapter*.json', 'shared/standards/electrical/NFPA70/art*.json']:
    article_files.extend(sorted(glob.glob(pattern)))
bad = []
for f in article_files:
    data = json.load(open(f))
    if 'articles' not in data:
        bad.append((f, 'no `articles` array'))
        continue
    for a in data['articles']:
        if 'full_content' in a:
            continue  # pointer entry, not full schema
        missing = [x for x in req if x not in a]
        if missing:
            bad.append((f, a.get('article_id','?'), missing))
print('OK' if not bad else 'BAD:'+str(bad[:10]))
PY
```
Expected: `OK`

- [ ] **Step 4: Verify every related_iec_60364 + divergence_notes field is populated**

Run:
```bash
python3 - <<'PY'
import json, glob
empty_divergence = []
empty_iec = []
for f in sorted(glob.glob('shared/standards/electrical/NFPA70/chapter*.json')) + sorted(glob.glob('shared/standards/electrical/NFPA70/art*.json')):
    data = json.load(open(f))
    for a in data.get('articles', []):
        if 'full_content' in a:
            continue
        if not a.get('divergence_notes'):
            empty_divergence.append((f.split('/')[-1], a.get('article_id','?')))
        if not isinstance(a.get('related_iec_60364'), list):
            empty_iec.append((f.split('/')[-1], a.get('article_id','?')))
print(f'Empty divergence_notes: {len(empty_divergence)} (should be 0)')
print(f'Missing related_iec_60364: {len(empty_iec)} (should be 0)')
if empty_divergence: print('First few:', empty_divergence[:5])
if empty_iec: print('First few:', empty_iec[:5])
PY
```
Expected: `Empty divergence_notes: 0`, `Missing related_iec_60364: 0`.

- [ ] **Step 5: Verify related_bs_7671 always empty for NEC entries**

Run:
```bash
python3 - <<'PY'
import json, glob
nonempty = []
for f in sorted(glob.glob('shared/standards/electrical/NFPA70/chapter*.json')) + sorted(glob.glob('shared/standards/electrical/NFPA70/art*.json')):
    data = json.load(open(f))
    for a in data.get('articles', []):
        if 'full_content' in a:
            continue
        if a.get('related_bs_7671') and len(a['related_bs_7671']) > 0:
            nonempty.append((f.split('/')[-1], a.get('article_id','?'), a['related_bs_7671']))
print(f'Articles with non-empty related_bs_7671: {len(nonempty)} (must be 0 per spec)')
if nonempty: print(nonempty[:5])
PY
```
Expected: `0`.

- [ ] **Step 6: Verify file count and category breakdown**

Run:
```bash
python3 - <<'PY'
import os, glob
files = sorted(os.listdir('shared/standards/electrical/NFPA70'))
counts = {'layer': 0, 'chapter': 0, 'article': 0, 'topic': 0, 'narrative': 0}
for f in files:
    if f in ['README.md', 'meta.json']: counts['layer'] += 1
    elif f.startswith('chapter'): counts['chapter'] += 1
    elif f.startswith('art'): counts['article'] += 1
    elif f.endswith('.md'): counts['narrative'] += 1
    else: counts['topic'] += 1
print(f'Layer: {counts["layer"]} (expected 2)')
print(f'Chapter: {counts["chapter"]} (expected 9)')
print(f'Article: {counts["article"]} (expected 17)')
print(f'Topic: {counts["topic"]} (expected 6)')
print(f'Narrative: {counts["narrative"]} (expected 5)')
print(f'TOTAL: {sum(counts.values())} (expected 39)')
PY
```
Expected: 2 + 9 + 17 + 6 + 5 = 39.

- [ ] **Step 7: Final layer-level summary commit (optional — only if uncommitted changes remain)**

```bash
git status --short
```

If uncommitted changes remain:
```bash
git add shared/standards/electrical/NFPA70/
git commit -m "feat: NFPA70 (NEC 2023) standard layer v1.0.0 complete — 39 files covering all 9 chapters"
```

- [ ] **Step 8: Verify final git log**

```bash
git log --oneline -42
```

Expected entries (most recent first, after spec commit `53bf6ea`):
- (optional final commit)
- docs: NFPA70 worked examples
- docs: NFPA70 terminology
- docs: NFPA70 compliance checklist
- docs: NFPA70 nec-vs-iec-comparison
- docs: NFPA70 amendments summary
- feat: NFPA70 wiring-methods-by-occupancy.json
- feat: NFPA70 conduit-fill.json
- feat: NFPA70 ampacity-correction-factors.json
- feat: NFPA70 hazardous-locations-classification.json
- feat: NFPA70 ocpd-coordination.json
- feat: NFPA70 grounding-and-bonding.json
- feat: NFPA70 art700-705-emergency-standby.json
- feat: NFPA70 art695-fire-pumps.json
- feat: NFPA70 art690-solar-pv.json
- feat: NFPA70 art680-pools-spas.json
- feat: NFPA70 art625-ev-charging.json
- feat: NFPA70 art517-healthcare.json
- feat: NFPA70 art500-506-hazardous-locations.json
- feat: NFPA70 art450-transformers.json
- feat: NFPA70 art430-motors.json
- feat: NFPA70 art408-panelboards.json
- feat: NFPA70 art310-conductor-ampacity.json
- feat: NFPA70 art250-grounding-bonding.json
- feat: NFPA70 art240-overcurrent.json
- feat: NFPA70 art230-services.json
- feat: NFPA70 art220-load-calculations.json
- feat: NFPA70 art215-feeders.json
- feat: NFPA70 art210-branch-circuits.json
- feat: NFPA70 chapter9-tables.json
- feat: NFPA70 chapter8-communications.json
- feat: NFPA70 chapter7-special-conditions.json
- feat: NFPA70 chapter6-special-equipment.json
- feat: NFPA70 chapter5-special-occupancies.json
- feat: NFPA70 chapter4-equipment.json
- feat: NFPA70 chapter3-wiring-methods.json
- feat: NFPA70 chapter2-wiring-protection.json
- feat: NFPA70 chapter1-general.json
- feat: NFPA70 meta.json + rewrite README as layer index
- docs: NFPA 70 (NEC 2023) standard layer design spec (53bf6ea)

---

## Plan Summary

| Group | Files | Tasks | Commits |
|---|---|---|---|
| Layer-level | 2 (README, meta.json) | 1 | 1 (combined) |
| Per-Chapter index | 9 | 9 | 9 |
| Per-heavy-Article | 17 | 17 | 17 |
| Cross-cutting topic | 6 | 6 | 6 |
| Narrative MDs | 5 | 5 | 5 |
| Final verification | — | 1 | 0–1 |
| **Total** | **39 files** | **39 tasks** | **38–39 commits** |
