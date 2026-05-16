# IEC 61439 Standard Layer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the IEC 61439 graphical-engineering standard layer covering low-voltage switchgear and controlgear assemblies across all 7 parts of the standard. 22 files in `shared/standards/electrical/IEC61439/`.

**Architecture:** Hybrid decomposition. 7 part JSONs (one per IEC 61439 part) carry per-part assembly entries with a fixed schema. 8 cross-cutting topic JSONs consolidate engineering concepts that span parts (form separations, verification methods, IP/IK, temperature rise, short-circuit withstand, internal arc, busbar derating, rated quantities). 5 narrative MDs cover non-tabular content (amendments, design-vs-manufacture split, compliance checklist, terminology, worked examples). Plus layer-level `meta.json` and `README.md`. Every assembly entry carries a `drawn_as` array referencing IEC 60617 symbol IDs (one-way pointer 61439 → 60617).

**Tech Stack:** JSON (RFC 8259), Markdown (CommonMark). No code or build scripts — layer is input-only. Validation via Python `json.load`.

**Reference:** See `docs/superpowers/specs/2026-05-15-iec61439-standard-layer-design.md` for the per-assembly schema, file organisation rationale, and decision log.

---

## File Structure

```
shared/standards/electrical/IEC61439/
├── README.md                           ← rewrite (current is stub)
├── meta.json                           ← new
│
├── part1-general.json                  ← new
├── part2-psc-assemblies.json           ← new
├── part3-dbo-assemblies.json           ← new
├── part4-acs-assemblies.json           ← new
├── part5-penda-assemblies.json         ← new
├── part6-busbar-trunking.json          ← new
├── part7-applications.json             ← new
│
├── form-separations.json               ← new
├── verification-methods.json           ← new
├── ip-ik-ratings.json                  ← new
├── temperature-rise.json               ← new
├── short-circuit-withstand.json        ← new
├── internal-arc-classification.json    ← new
├── busbar-derating.json                ← new
├── rated-quantities.json               ← new
│
├── amendments-summary.md               ← new
├── design-vs-manufacture.md            ← new
├── compliance-checklist.md             ← new
├── terminology.md                      ← new
└── worked-examples.md                  ← new
```

---

## Per-Assembly Schema (used in all part JSONs)

Every entry in `part1-general.json` through `part7-applications.json` uses this schema. All fields mandatory.

| Field | Type | Description |
|---|---|---|
| `assembly_id` | string | UPPER_SNAKE_CASE canonical id |
| `iec_ref` | string | e.g. `IEC61439-2:2020` |
| `iec_part` | integer | 1–7 |
| `iec_title` | string | Title from the standard, not paraphrased |
| `draftsman_id` | string | Same as `assembly_id` |
| `application_scope` | string | What this assembly is used for |
| `rated_quantities` | object | Keys: `Ue_V`, `Ui_V`, `Uimp_kV`, `In_A`, `Icw_kA_1s`, `Ipk_kA` — arrays of permitted standard values |
| `form_separation` | string | `1` / `2a` / `2b` / `3a` / `3b` / `4a` / `4b` or `"n/a"` |
| `ip_default` | string | Default minimum IP description |
| `ik_default` | string | Default minimum IK |
| `mandatory_characteristics` | string[] | Fields the designer MUST specify on the schedule |
| `verification_clauses` | string[] | Clauses the OEM must verify |
| `drawn_as` | string[] | IEC 60617 `symbol_id` values that render this assembly |
| `typical_components` | string[] | IEC 60617 `symbol_id` values commonly inside this assembly |
| `application_examples` | string[] | Typical use cases |
| `related_iec_60364` | string[] | Installation-side cross-refs |
| `related_bs_7671` | string[] | UK-practice cross-refs |
| `usage_notes` | string | Designer guidance |
| `related_assemblies` | string[] | Other `assembly_id` values to consider |

---

## Validation Commands (used in every task)

- JSON syntax check:
  `python3 -c "import json; json.load(open('PATH'))" && echo OK`
- Assembly schema field check (for part files):
  `python3 -c "import json; data=json.load(open('PATH')); req=['assembly_id','iec_ref','iec_part','iec_title','draftsman_id','application_scope','rated_quantities','form_separation','ip_default','ik_default','mandatory_characteristics','verification_clauses','drawn_as','typical_components','application_examples','related_iec_60364','related_bs_7671','usage_notes','related_assemblies']; missing=[(s.get('assembly_id','?'), [f for f in req if f not in s]) for s in data['assemblies'] if any(f not in s for f in req)]; print('OK' if not missing else 'MISSING:'+str(missing))"`
- IEC 60617 `drawn_as` resolution check:
  `python3 -c "import json; idx=json.load(open('shared/standards/electrical/IEC60617/symbol-index.json')); ids=set(s['symbol_id'] for s in idx['symbols']); data=json.load(open('PATH')); bad=[(a['assembly_id'],ref) for a in data['assemblies'] for ref in a.get('drawn_as',[])+a.get('typical_components',[]) if ref not in ids]; print('OK' if not bad else 'DANGLING:'+str(bad))"`

---

## Task 1: Create meta.json

**Files:**
- Create: `shared/standards/electrical/IEC61439/meta.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "IEC 61439 — Low-voltage switchgear and controlgear assemblies",
  "_version": "1.0.0",
  "_purpose": "Engineering source of truth for low-voltage assemblies (switchboards, MCCs, DBs, busduct, kiosks, application-specific). Carries the standard's tabulated rules, verification requirements, and form separations. Consumed by every DraftsMan electrical skill that produces or validates an assembly schedule, drawing, or BOM.",
  "standard": {
    "title": "Low-voltage switchgear and controlgear assemblies",
    "issuer": "International Electrotechnical Commission",
    "issuer_short": "IEC",
    "designation": "IEC 61439",
    "status": "Active",
    "database_url": "https://webstore.iec.ch/publication/series/IEC61439",
    "first_published": 2009,
    "current_edition": "2nd edition with ongoing part-by-part revisions (e.g. Part 2:2020)",
    "language_codes": ["en", "fr"],
    "national_adoptions": [
      {"code": "BS EN 61439", "country": "United Kingdom", "notes": "Direct adoption of IEC 61439"},
      {"code": "DIN EN 61439", "country": "Germany", "notes": "Direct adoption with German titles"},
      {"code": "NF EN 61439", "country": "France", "notes": "Direct adoption"},
      {"code": "AS/NZS 61439", "country": "Australia / New Zealand", "notes": "Direct adoption"},
      {"code": "IS/IEC 61439", "country": "India", "notes": "Direct adoption"}
    ],
    "supersedes": {
      "designation": "IEC 60439",
      "withdrawn": 2014,
      "note": "IEC 60439 is fully withdrawn. New designs are specified to IEC 61439. Existing assemblies built to IEC 60439 remain governed by the certificate they were issued under; this layer does not cover IEC 60439."
    }
  },
  "parts": [
    {"part": 1, "title": "General rules",                                                          "covered": true, "symbol_file": "part1-general.json"},
    {"part": 2, "title": "Power switchgear and controlgear assemblies (PSC-Assemblies)",           "covered": true, "symbol_file": "part2-psc-assemblies.json"},
    {"part": 3, "title": "Distribution boards intended to be operated by ordinary persons (DBO)",  "covered": true, "symbol_file": "part3-dbo-assemblies.json"},
    {"part": 4, "title": "Particular requirements for assemblies for construction sites (ACS)",    "covered": true, "symbol_file": "part4-acs-assemblies.json"},
    {"part": 5, "title": "Assemblies for power distribution in public networks (PENDA)",           "covered": true, "symbol_file": "part5-penda-assemblies.json"},
    {"part": 6, "title": "Busbar trunking systems (BTS)",                                          "covered": true, "symbol_file": "part6-busbar-trunking.json"},
    {"part": 7, "title": "Assemblies for specific applications (marinas, EV, safety, PV, transformer)", "covered": true, "symbol_file": "part7-applications.json"}
  ],
  "cross_cutting_topics": [
    {"file": "form-separations.json",            "scope": "Forms 1 to 4b — segregation of busbars, functional units, and outgoing terminals"},
    {"file": "verification-methods.json",        "scope": "The three permitted verification paths (test / calculation / reference design) with Annex D matrix"},
    {"file": "ip-ik-ratings.json",               "scope": "IP code (Part 1 Table 7) + IK code (BS EN 50102) + minimum IP by location"},
    {"file": "temperature-rise.json",            "scope": "Conventional limits (Table 6), Rated Diversity Factor (RDF), Annex E calculation method"},
    {"file": "short-circuit-withstand.json",     "scope": "Icw / Ipk / Icc, upstream coordination, n-factor, Annex P verification"},
    {"file": "internal-arc-classification.json", "scope": "IAC criteria A/B/C/D + accessibility types F/L/R + application boundary"},
    {"file": "busbar-derating.json",             "scope": "Current carrying capacity, adjacency derating, fault force F = K·Ipk²·s/d, neutral/PE sizing"},
    {"file": "rated-quantities.json",            "scope": "Quick-reference for all rated quantities (Ue, Ui, Uimp, In, Inc, Icw, Ipk, fn, PD)"}
  ],
  "cross_references": {
    "drawn_as_targets":     "shared/standards/electrical/IEC60617/ (symbol IDs)",
    "installation_rules":   "shared/standards/electrical/IEC60364/",
    "uk_practice":          "shared/standards/electrical/BS7671/",
    "iac_test_method":      "IEC TR 61641 — Guide for testing under conditions of arcing due to internal fault",
    "ik_standard":          "BS EN 50102 — Degrees of protection provided by enclosures for electrical equipment against external mechanical impacts (IK code)"
  }
}
```

- [ ] **Step 2: Validate JSON syntax**

Run: `python3 -c "import json; json.load(open('shared/standards/electrical/IEC61439/meta.json'))" && echo OK`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add shared/standards/electrical/IEC61439/meta.json
git commit -m "feat: IEC61439 meta.json — standard metadata and part catalogue"
```

---

## Task 2: Rewrite README.md

**Files:**
- Modify (full rewrite): `shared/standards/electrical/IEC61439/README.md`

- [ ] **Step 1: Write the new README**

````markdown
# IEC 61439 — Low-Voltage Switchgear and Controlgear Assemblies

**Standard:** IEC 61439 (multi-part)
**Status:** Active — 2nd edition with ongoing part-by-part revisions
**Scope of this layer:** All 7 parts of IEC 61439 (general, PSC, DBO, ACS, PENDA, BTS, applications) with full engineering depth and worked examples.

This layer is the engineering source of truth for low-voltage assemblies — switchboards, MCCs, distribution boards, busduct risers, kiosks, and application-specific assemblies (EV charging, marinas, PV, safety services). It complements IEC 60617 (which defines what these assemblies *look like* on a drawing): IEC 61439 defines what the actual physical assembly *must be*.

This layer is input-only. It does not produce files in `shared/symbols/electrical/`; that's IEC 60617's job. Every assembly entry carries a `drawn_as` array of IEC 60617 `symbol_id` values pointing to the visual representation.

---

## Files

| File | Purpose |
|---|---|
| `meta.json` | Standard title, edition history, part catalogue, national adoptions, relationship to withdrawn IEC 60439 |
| `part1-general.json` | Part 1 — general rules, definitions, rated quantities, constructional vs functional units |
| `part2-psc-assemblies.json` | Part 2 — power switchgear and controlgear assemblies (main switchboards, MCCs) by Form |
| `part3-dbo-assemblies.json` | Part 3 — distribution boards for ordinary persons (consumer units, sub-DBs) |
| `part4-acs-assemblies.json` | Part 4 — construction site assemblies (transportable, fixed-outdoor) |
| `part5-penda-assemblies.json` | Part 5 — public-network distribution assemblies (DNO pillars, kiosks, ground distributors) |
| `part6-busbar-trunking.json` | Part 6 — busbar trunking systems (vertical risers, horizontal mains busduct) |
| `part7-applications.json` | Part 7 — application-specific assemblies (marina/camping, EV charging, safety services, PV, transformer) |
| `form-separations.json` | Forms 1 → 4b with ASCII diagrams, applications, advantages, disadvantages |
| `verification-methods.json` | Test / calculation / reference-design — the 2014 verification trio + Annex D matrix |
| `ip-ik-ratings.json` | IP and IK codes + minimum-IP-by-location matrix |
| `temperature-rise.json` | Conventional limits, RDF, Annex E calculation |
| `short-circuit-withstand.json` | Icw / Ipk / Icc + upstream coordination + n-factor + Annex P |
| `internal-arc-classification.json` | IAC A/B/C/D + accessibility F/L/R + application boundary |
| `busbar-derating.json` | Current carrying capacity, adjacency derating, fault force calculation |
| `rated-quantities.json` | Quick-reference for all rated quantities |
| `amendments-summary.md` | Edition history and key changes affecting designers |
| `design-vs-manufacture.md` | OM / AM / MEP-designer responsibility split |
| `compliance-checklist.md` | Designer-side checklist of every mandatory characteristic |
| `terminology.md` | Critical-distinction glossary |
| `worked-examples.md` | Four worked examples covering form verification, IAC, busbar derating, Icw coordination |

---

## How skills use this layer

**Pick an assembly type (e.g. "which Form do I specify for a 1600 A main switchboard?"):**
```
load form-separations.json
find entries whose applications match the use case
pick the form with appropriate advantages
verify against rated_quantities in part2-psc-assemblies.json
```

**Validate a generated schedule:**
```
load part2-psc-assemblies.json
find the chosen assembly_id
check the schedule has every field in mandatory_characteristics
flag any missing
```

**Render the assembly on a drawing:**
```
load assembly entry
use the drawn_as array → IEC 60617 symbol_ids
runtime fetches geometry from IEC 60617 part files
```

**Cite IEC 60364 / BS 7671 installation rules:**
```
read related_iec_60364 and related_bs_7671 arrays on the assembly entry
follow the references for installation requirements
```

---

## Per-assembly schema

```json
{
  "assembly_id":               "PSC_ASSEMBLY_FORM_3B",
  "iec_ref":                   "IEC61439-2:2020",
  "iec_part":                  2,
  "iec_title":                 "Power switchgear and controlgear assemblies — Form 3b",
  "draftsman_id":              "PSC_ASSEMBLY_FORM_3B",
  "application_scope":         "...",
  "rated_quantities":          { "Ue_V": [...], "Ui_V": [...], "Uimp_kV": [...], "In_A": [...], "Icw_kA_1s": [...], "Ipk_kA": [...] },
  "form_separation":           "3b",
  "ip_default":                "IP2X (front), IP30 (enclosure)",
  "ik_default":                "IK08",
  "mandatory_characteristics": [...],
  "verification_clauses":      [...],
  "drawn_as":                  ["DB_MAIN", "DB_SUB"],
  "typical_components":        ["ACB_3P", "MCCB_3P", ...],
  "application_examples":      [...],
  "related_iec_60364":         [...],
  "related_bs_7671":           [...],
  "usage_notes":               "...",
  "related_assemblies":        [...]
}
```

See `docs/superpowers/specs/2026-05-15-iec61439-standard-layer-design.md` for the full schema definition.

---

## Scope

**In scope:** all 7 parts of IEC 61439 at full engineering depth with worked examples.

**Out of scope:**
- IEC 60439 (predecessor, withdrawn 2014).
- Manufacturer-specific catalogue data (ABB / Schneider / Siemens / Eaton). Future `shared/manufacturers/` layer.
- HV switchgear assemblies (IEC 62271).
- Power-electronic converter assemblies (IEC 61800-x).
- Functional safety of assemblies (IEC 61508 / 62061).
- Internal wiring rules below assembly level (OEM-internal).
- Generated symbol files (those come from IEC 60617).
````

- [ ] **Step 2: Commit**

```bash
git add shared/standards/electrical/IEC61439/README.md
git commit -m "docs: rewrite IEC61439 README as comprehensive layer index"
```

---

## Task 3: Create part1-general.json (Part 1 — General rules)

**Files:**
- Create: `shared/standards/electrical/IEC61439/part1-general.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "IEC 61439 Part 1 — General rules",
  "_iec_part": 1,
  "_version": "1.0.0",
  "_note": "Part 1 sets the framework for all other parts. The two assembly entries here represent the indoor/normal-service and outdoor/special-service baselines — every Part 2–7 assembly inherits from one of these.",
  "assemblies": [
    {
      "assembly_id": "ASSEMBLY_INDOOR_NORMAL_SERVICE",
      "iec_ref": "IEC61439-1:2020",
      "iec_part": 1,
      "iec_title": "LV assembly — indoor, normal service conditions",
      "draftsman_id": "ASSEMBLY_INDOOR_NORMAL_SERVICE",
      "application_scope": "Baseline LV switchgear/controlgear assembly for indoor installation under IEC 61439-1 Clause 7.1 normal service conditions: ambient -5 °C to +40 °C (24-hour average ≤ 35 °C), altitude ≤ 2000 m, relative humidity ≤ 50% at 40 °C (higher at lower temperatures), pollution degree 2 (3 for industrial). Every Part 2/3/7 assembly with no special-service overlay inherits these conditions.",
      "rated_quantities": {
        "Ue_V":      [230, 400, 690, 1000],
        "Ui_V":      [1000],
        "Uimp_kV":   [4, 6, 8, 12],
        "In_A":      [16, 32, 63, 100, 125, 160, 250, 400, 630, 800, 1250, 1600, 2000, 2500, 3200, 4000, 5000, 6300],
        "Icw_kA_1s": [10, 15, 25, 36, 50, 65, 80, 100],
        "Ipk_kA":    [17, 30, 52, 75, 105, 143, 176, 220]
      },
      "form_separation": "n/a",
      "ip_default": "IP2X minimum (Clause 8.2)",
      "ik_default": "IK05",
      "mandatory_characteristics": [
        "rated_operational_voltage_Ue",
        "rated_insulation_voltage_Ui",
        "rated_impulse_withstand_Uimp",
        "rated_current_In",
        "rated_short_time_withstand_Icw",
        "rated_peak_withstand_Ipk",
        "rated_frequency_fn",
        "ip_code",
        "ik_code",
        "ambient_temperature_range",
        "altitude",
        "pollution_degree",
        "overvoltage_category"
      ],
      "verification_clauses": [
        "10.2 strength of materials and parts",
        "10.3 degree of protection",
        "10.4 clearances and creepage distances",
        "10.5 protection against electric shock and integrity of protective circuits",
        "10.6 incorporation of switching and protective devices",
        "10.7 internal electrical circuits and connections",
        "10.8 terminals for external conductors",
        "10.9 dielectric properties",
        "10.10 temperature rise verification (Annex E)",
        "10.11 short-circuit withstand verification (Annex P)",
        "10.12 electromagnetic compatibility",
        "10.13 mechanical operation"
      ],
      "drawn_as": ["DB_GENERAL"],
      "typical_components": ["MCB_3P", "MCCB_3P", "BUSBAR_3PH", "AMMETER", "VOLTMETER"],
      "application_examples": [
        "Indoor sub-distribution board in a commercial office",
        "Indoor MCC in a temperature-controlled plant room",
        "Indoor consumer unit"
      ],
      "related_iec_60364": ["IEC60364-5-53 (Selection and erection of switchgear)", "IEC60364-6 (Verification)"],
      "related_bs_7671": ["Reg 132.12 (Equipment compatibility with the system)", "Section 537 (Isolation and switching)"],
      "usage_notes": "Use as the baseline 'no special conditions' assembly. Any deviation (outdoor, dust, vibration, high ambient) requires the SPECIAL_SERVICE_CONDITIONS variant and an OEM-agreed verification path. Designer specifies the ambient explicitly when it differs from the 35 °C 24-h average even if peak stays at 40 °C.",
      "related_assemblies": ["ASSEMBLY_OUTDOOR_SPECIAL_SERVICE", "PSC_ASSEMBLY_FORM_1", "DBO_ASSEMBLY"]
    },
    {
      "assembly_id": "ASSEMBLY_OUTDOOR_SPECIAL_SERVICE",
      "iec_ref": "IEC61439-1:2020",
      "iec_part": 1,
      "iec_title": "LV assembly — outdoor or special service conditions",
      "draftsman_id": "ASSEMBLY_OUTDOOR_SPECIAL_SERVICE",
      "application_scope": "Baseline for assemblies installed under Clause 7.2 special service conditions: outdoor installation, ambient outside -5/+40 °C, altitude > 2000 m, humidity exceeding the indoor envelope, presence of dust/corrosive atmosphere, vibration/shock above normal, exposure to fungus/insects/vermin, exposure to abnormal electrical disturbance. Used as the inherited baseline by Part 4 (ACS), Part 5 (PENDA), and outdoor-installed Part 7 applications.",
      "rated_quantities": {
        "Ue_V":      [230, 400, 690, 1000],
        "Ui_V":      [1000],
        "Uimp_kV":   [6, 8, 12],
        "In_A":      [16, 32, 63, 100, 125, 160, 250, 400, 630, 800, 1250, 1600, 2000, 2500, 3200, 4000],
        "Icw_kA_1s": [10, 15, 25, 36, 50, 65, 80, 100],
        "Ipk_kA":    [17, 30, 52, 75, 105, 143, 176, 220]
      },
      "form_separation": "n/a",
      "ip_default": "IP44 minimum (outdoor, splash-proof); IP54 in dusty/wash-down environments; IP65+ where direct water spray is foreseeable",
      "ik_default": "IK08 (outdoor, public-accessible); IK10 where vandalism is foreseeable",
      "mandatory_characteristics": [
        "rated_operational_voltage_Ue",
        "rated_insulation_voltage_Ui",
        "rated_impulse_withstand_Uimp",
        "rated_current_In",
        "rated_short_time_withstand_Icw",
        "rated_peak_withstand_Ipk",
        "rated_frequency_fn",
        "ip_code",
        "ik_code",
        "ambient_temperature_range_extended",
        "altitude_if_above_2000m",
        "solar_radiation_protection",
        "pollution_degree_special",
        "overvoltage_category_special",
        "corrosion_protection_class",
        "vibration_class_if_applicable"
      ],
      "verification_clauses": [
        "10.2 strength of materials and parts (including solar/corrosion if outdoor)",
        "10.3 degree of protection (outdoor IP and IK)",
        "10.4 clearances and creepage (pollution degree 3 typical)",
        "10.5 protection against electric shock",
        "10.6 incorporation of switching/protective devices",
        "10.7 internal electrical circuits",
        "10.8 terminals for external conductors",
        "10.9 dielectric properties (high humidity)",
        "10.10 temperature rise (solar gain Annex E.5)",
        "10.11 short-circuit withstand (Annex P)",
        "10.12 EMC",
        "10.13 mechanical operation (low-temperature operation)"
      ],
      "drawn_as": ["DB_GENERAL"],
      "typical_components": ["MCCB_3P", "ACB_3P", "BUSBAR_3PH", "SPD_TYPE1", "SPD_TYPE2"],
      "application_examples": [
        "Outdoor utility pillar (PENDA, Part 5)",
        "Construction site assembly (ACS, Part 4)",
        "Outdoor PV combiner box (Part 7-4)",
        "Outdoor EV charging station enclosure (Part 7-2)"
      ],
      "related_iec_60364": ["IEC60364-5-51 (Common rules — environmental influences)", "IEC60364-7-704 (Construction sites)", "IEC60364-7-712 (Solar PV)", "IEC60364-7-722 (EV charging)"],
      "related_bs_7671": ["Section 522 (External influences)", "Section 704 (Construction sites)", "Section 712 (Solar PV)", "Section 722 (EV charging)"],
      "usage_notes": "Specify explicit IP and IK values rather than relying on this default. Solar gain alone can add 15–25 K to internal temperature — verify temperature rise per Annex E.5. For ACS/Part 4, IK08 is mandatory; for PENDA/Part 5 in unattended public locations, IK10.",
      "related_assemblies": ["ASSEMBLY_INDOOR_NORMAL_SERVICE", "ACS_ASSEMBLY", "PENDA_KIOSK_GROUND_MOUNTED", "PENDA_KIOSK_POLE_MOUNTED"]
    }
  ]
}
```

- [ ] **Step 2: Validate JSON syntax**

Run: `python3 -c "import json; json.load(open('shared/standards/electrical/IEC61439/part1-general.json'))" && echo OK`
Expected: `OK`

- [ ] **Step 3: Verify all schema fields present**

Run: `python3 -c "import json; data=json.load(open('shared/standards/electrical/IEC61439/part1-general.json')); req=['assembly_id','iec_ref','iec_part','iec_title','draftsman_id','application_scope','rated_quantities','form_separation','ip_default','ik_default','mandatory_characteristics','verification_clauses','drawn_as','typical_components','application_examples','related_iec_60364','related_bs_7671','usage_notes','related_assemblies']; missing=[(s.get('assembly_id','?'), [f for f in req if f not in s]) for s in data['assemblies'] if any(f not in s for f in req)]; print('OK' if not missing else 'MISSING:'+str(missing))"`
Expected: `OK`

- [ ] **Step 4: Verify drawn_as references resolve in IEC 60617 symbol index**

Run:
```bash
python3 - <<'PY'
import json
idx_syms = {s['symbol_id'] for s in json.load(open('shared/standards/electrical/IEC60617/symbol-index.json'))['symbols']}
data = json.load(open('shared/standards/electrical/IEC61439/part1-general.json'))
unknown = []
for a in data['assemblies']:
    for s in a['drawn_as']:
        if s not in idx_syms:
            unknown.append((a['assembly_id'], s))
print('OK' if not unknown else 'UNKNOWN:'+str(unknown))
PY
```
Expected: `OK`

- [ ] **Step 5: Commit**

```bash
git add shared/standards/electrical/IEC61439/part1-general.json
git commit -m "feat: IEC61439 part1-general.json — indoor/outdoor baseline assemblies"
```

---

## Task 4: Create part2-psc-assemblies.json (Part 2 — PSC-Assemblies, 7 Form variants)

**Files:**
- Create: `shared/standards/electrical/IEC61439/part2-psc-assemblies.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "IEC 61439 Part 2 — Power switchgear and controlgear assemblies (PSC-Assemblies)",
  "_iec_part": 2,
  "_version": "1.0.0",
  "_note": "Main switchboards and motor control centres. One assembly entry per Form code (1, 2a, 2b, 3a, 3b, 4a, 4b). Designer specifies Form on the schedule; OEM verifies. See form-separations.json for the segregation details.",
  "assemblies": [
    {
      "assembly_id": "PSC_ASSEMBLY_FORM_1",
      "iec_ref": "IEC61439-2:2020",
      "iec_part": 2,
      "iec_title": "PSC-Assembly Form 1 — no internal segregation",
      "draftsman_id": "PSC_ASSEMBLY_FORM_1",
      "application_scope": "Open-construction PSC-Assembly with no internal segregation between busbars, functional units, or outgoing terminals. Cheapest form. Acceptable only where the entire assembly is de-energised for any maintenance work and there are no operator-access requirements during operation.",
      "rated_quantities": {
        "Ue_V":      [230, 400, 690],
        "Ui_V":      [1000],
        "Uimp_kV":   [4, 6, 8],
        "In_A":      [100, 160, 250, 400, 630, 800, 1250, 1600],
        "Icw_kA_1s": [10, 15, 25, 36, 50],
        "Ipk_kA":    [17, 30, 52, 75, 105]
      },
      "form_separation": "1",
      "ip_default": "IP2X (front), IP30 (enclosure)",
      "ik_default": "IK07",
      "mandatory_characteristics": [
        "rated_operational_voltage_Ue",
        "rated_insulation_voltage_Ui",
        "rated_impulse_withstand_Uimp",
        "rated_current_In",
        "rated_short_time_withstand_Icw",
        "rated_peak_withstand_Ipk",
        "rated_frequency_fn",
        "ip_code",
        "ik_code",
        "form_separation"
      ],
      "verification_clauses": [
        "10.2 strength",
        "10.3 IP",
        "10.4 clearances/creepage",
        "10.5 electric shock protection",
        "10.10 temperature rise (Annex E)",
        "10.11 short-circuit withstand (Annex P)",
        "10.13 mechanical operation"
      ],
      "drawn_as": ["DB_GENERAL", "DB_SUB"],
      "typical_components": ["MCCB_3P", "BUSBAR_3PH"],
      "application_examples": [
        "Small industrial sub-distribution where maintenance is always with the whole board off",
        "Plant-only assemblies with no operator interface"
      ],
      "related_iec_60364": ["IEC60364-5-53 (Switchgear selection)"],
      "related_bs_7671": ["Section 537 (Isolation and switching)"],
      "usage_notes": "Avoid for any application requiring single-circuit maintenance with the rest live. Form 1 is functionally equivalent to a switchboard cabinet without internal barriers — once the door is open, all live parts are accessible.",
      "related_assemblies": ["PSC_ASSEMBLY_FORM_2A", "PSC_ASSEMBLY_FORM_2B"]
    },
    {
      "assembly_id": "PSC_ASSEMBLY_FORM_2A",
      "iec_ref": "IEC61439-2:2020",
      "iec_part": 2,
      "iec_title": "PSC-Assembly Form 2a — busbar separation, common terminations",
      "draftsman_id": "PSC_ASSEMBLY_FORM_2A",
      "application_scope": "PSC-Assembly with segregated busbar compartment; functional units share a single compartment, and outgoing-conductor terminals are not separated from the busbar.",
      "rated_quantities": {
        "Ue_V":      [230, 400, 690],
        "Ui_V":      [1000],
        "Uimp_kV":   [4, 6, 8],
        "In_A":      [100, 160, 250, 400, 630, 800, 1250, 1600, 2000],
        "Icw_kA_1s": [10, 15, 25, 36, 50, 65],
        "Ipk_kA":    [17, 30, 52, 75, 105, 143]
      },
      "form_separation": "2a",
      "ip_default": "IP2X (front), IP30 (enclosure)",
      "ik_default": "IK07",
      "mandatory_characteristics": [
        "rated_operational_voltage_Ue",
        "rated_insulation_voltage_Ui",
        "rated_impulse_withstand_Uimp",
        "rated_current_In",
        "rated_short_time_withstand_Icw",
        "rated_peak_withstand_Ipk",
        "rated_frequency_fn",
        "ip_code",
        "ik_code",
        "form_separation"
      ],
      "verification_clauses": [
        "10.2 strength",
        "10.3 IP",
        "10.4 clearances/creepage",
        "10.5 electric shock protection",
        "10.10 temperature rise",
        "10.11 short-circuit withstand",
        "10.13 mechanical operation"
      ],
      "drawn_as": ["DB_SUB", "DB_GENERAL"],
      "typical_components": ["MCCB_3P", "BUSBAR_3PH", "AMMETER", "VOLTMETER"],
      "application_examples": [
        "General industrial sub-distribution where busbar isolation matters but functional-unit segregation is not required",
        "Small commercial sub-DBs above 250A"
      ],
      "related_iec_60364": ["IEC60364-5-53"],
      "related_bs_7671": ["Section 537"],
      "usage_notes": "Form 2a is the entry-level form for installations where the busbar must remain undisturbed while a functional unit is being worked on, but the OEM does not need to separate individual functional units. Cheaper than 2b.",
      "related_assemblies": ["PSC_ASSEMBLY_FORM_1", "PSC_ASSEMBLY_FORM_2B"]
    },
    {
      "assembly_id": "PSC_ASSEMBLY_FORM_2B",
      "iec_ref": "IEC61439-2:2020",
      "iec_part": 2,
      "iec_title": "PSC-Assembly Form 2b — busbar separation, integral terminations",
      "draftsman_id": "PSC_ASSEMBLY_FORM_2B",
      "application_scope": "Form 2a plus the outgoing-conductor terminals are separated from the busbar compartment (but still in the functional-unit compartment).",
      "rated_quantities": {
        "Ue_V":      [230, 400, 690],
        "Ui_V":      [1000],
        "Uimp_kV":   [4, 6, 8],
        "In_A":      [400, 630, 800, 1250, 1600, 2000, 2500],
        "Icw_kA_1s": [25, 36, 50, 65, 80],
        "Ipk_kA":    [52, 75, 105, 143, 176]
      },
      "form_separation": "2b",
      "ip_default": "IP2X (front), IP30 (enclosure)",
      "ik_default": "IK07",
      "mandatory_characteristics": [
        "rated_operational_voltage_Ue",
        "rated_insulation_voltage_Ui",
        "rated_impulse_withstand_Uimp",
        "rated_current_In",
        "rated_short_time_withstand_Icw",
        "rated_peak_withstand_Ipk",
        "rated_frequency_fn",
        "ip_code",
        "ik_code",
        "form_separation"
      ],
      "verification_clauses": [
        "10.2 strength",
        "10.3 IP",
        "10.4 clearances/creepage",
        "10.5 electric shock protection",
        "10.10 temperature rise",
        "10.11 short-circuit withstand",
        "10.13 mechanical operation"
      ],
      "drawn_as": ["DB_MAIN", "DB_SUB"],
      "typical_components": ["MCCB_3P", "ACB_3P", "BUSBAR_3PH", "AMMETER", "VOLTMETER", "ENERGY_METER_KWH"],
      "application_examples": [
        "Commercial main switchboards up to ~1600A",
        "Light industrial main switchboards"
      ],
      "related_iec_60364": ["IEC60364-5-53"],
      "related_bs_7671": ["Section 537"],
      "usage_notes": "Form 2b is the cheapest form that lets you work on outgoing terminations without de-energising the busbar. Common default for commercial mains 400–1600A where critical-circuit independence is not required.",
      "related_assemblies": ["PSC_ASSEMBLY_FORM_2A", "PSC_ASSEMBLY_FORM_3B"]
    },
    {
      "assembly_id": "PSC_ASSEMBLY_FORM_3A",
      "iec_ref": "IEC61439-2:2020",
      "iec_part": 2,
      "iec_title": "PSC-Assembly Form 3a — busbar and functional-unit separation, common terminations",
      "draftsman_id": "PSC_ASSEMBLY_FORM_3A",
      "application_scope": "Form 2 plus segregation between functional units. Outgoing-conductor terminals are NOT separated from the busbar compartment.",
      "rated_quantities": {
        "Ue_V":      [230, 400, 690, 1000],
        "Ui_V":      [1000],
        "Uimp_kV":   [4, 6, 8, 12],
        "In_A":      [400, 630, 800, 1250, 1600, 2000, 2500, 3200],
        "Icw_kA_1s": [25, 36, 50, 65, 80, 100],
        "Ipk_kA":    [52, 75, 105, 143, 176, 220]
      },
      "form_separation": "3a",
      "ip_default": "IP2X (front), IP30 (enclosure)",
      "ik_default": "IK08",
      "mandatory_characteristics": [
        "rated_operational_voltage_Ue",
        "rated_insulation_voltage_Ui",
        "rated_impulse_withstand_Uimp",
        "rated_current_In",
        "rated_short_time_withstand_Icw",
        "rated_peak_withstand_Ipk",
        "rated_frequency_fn",
        "ip_code",
        "ik_code",
        "form_separation"
      ],
      "verification_clauses": [
        "10.2 strength",
        "10.3 IP",
        "10.4 clearances/creepage",
        "10.5 electric shock protection",
        "10.10 temperature rise",
        "10.11 short-circuit withstand",
        "10.13 mechanical operation"
      ],
      "drawn_as": ["DB_MAIN"],
      "typical_components": ["ACB_3P", "MCCB_3P", "BUSBAR_3PH", "MULTIFUNCTION_METER"],
      "application_examples": [
        "Industrial MCCs without separate-termination requirement",
        "Mid-tier commercial mains above 1600A"
      ],
      "related_iec_60364": ["IEC60364-5-53"],
      "related_bs_7671": ["Section 537"],
      "usage_notes": "Form 3a allows working on one functional unit while neighbours stay live, but the outgoing terminations remain in the busbar compartment — risky for cable work. Specify 3b instead unless cost is dominant.",
      "related_assemblies": ["PSC_ASSEMBLY_FORM_2B", "PSC_ASSEMBLY_FORM_3B"]
    },
    {
      "assembly_id": "PSC_ASSEMBLY_FORM_3B",
      "iec_ref": "IEC61439-2:2020",
      "iec_part": 2,
      "iec_title": "PSC-Assembly Form 3b — busbar and functional-unit separation, integral terminations",
      "draftsman_id": "PSC_ASSEMBLY_FORM_3B",
      "application_scope": "Form 3a plus separately-terminated outgoing conductors. Each functional unit and its outgoing terminals are in their own compartments; only the busbar runs across the assembly.",
      "rated_quantities": {
        "Ue_V":      [230, 400, 690, 1000],
        "Ui_V":      [1000],
        "Uimp_kV":   [4, 6, 8, 12],
        "In_A":      [630, 800, 1250, 1600, 2000, 2500, 3200, 4000, 5000, 6300],
        "Icw_kA_1s": [25, 36, 50, 65, 80, 100],
        "Ipk_kA":    [52, 75, 105, 143, 176, 220]
      },
      "form_separation": "3b",
      "ip_default": "IP2X (front), IP30 (enclosure)",
      "ik_default": "IK08",
      "mandatory_characteristics": [
        "rated_operational_voltage_Ue",
        "rated_insulation_voltage_Ui",
        "rated_impulse_withstand_Uimp",
        "rated_current_In",
        "rated_short_time_withstand_Icw",
        "rated_peak_withstand_Ipk",
        "rated_frequency_fn",
        "ip_code",
        "ik_code",
        "form_separation",
        "internal_arc_classification_if_applicable"
      ],
      "verification_clauses": [
        "10.2 strength",
        "10.3 IP",
        "10.4 clearances/creepage",
        "10.5 electric shock protection",
        "10.6 incorporation of switching/protective devices",
        "10.7 internal electrical circuits",
        "10.8 terminals for external conductors",
        "10.9 dielectric properties",
        "10.10 temperature rise verification (Annex E)",
        "10.11 short-circuit withstand verification (Annex P)",
        "10.13 mechanical operation"
      ],
      "drawn_as": ["DB_MAIN", "DB_SUB"],
      "typical_components": ["ACB_3P", "MCCB_3P", "BUSBAR_3PH", "CT_METERING", "MULTIFUNCTION_METER", "SPD_TYPE2"],
      "application_examples": [
        "Main LV switchboard (MSB) downstream of LV transformer",
        "Motor control centre (MCC) with segregated motor circuits",
        "Critical services switchboard with selectivity to ACB"
      ],
      "related_iec_60364": ["IEC60364-4-43 (overcurrent)", "IEC60364-5-53 (switchgear)", "IEC60364-6 (verification)"],
      "related_bs_7671": ["Reg 432 (Coordination)", "Section 537 (Isolation and switching)"],
      "usage_notes": "Default choice for commercial main LV switchboards above ~400A. Specify the requirement that incomer can be maintained with outgoers live (and vice versa) so the OEM provides a real Form 3b rather than a 3a relabelled.",
      "related_assemblies": ["PSC_ASSEMBLY_FORM_4A", "PSC_ASSEMBLY_FORM_3A"]
    },
    {
      "assembly_id": "PSC_ASSEMBLY_FORM_4A",
      "iec_ref": "IEC61439-2:2020",
      "iec_part": 2,
      "iec_title": "PSC-Assembly Form 4a — busbar, functional unit, and grouped-termination separation",
      "draftsman_id": "PSC_ASSEMBLY_FORM_4A",
      "application_scope": "Form 3b plus the outgoing-conductor terminals of EACH functional unit are separated from those of every other functional unit. Terminals belonging to the same unit may still be grouped together.",
      "rated_quantities": {
        "Ue_V":      [230, 400, 690, 1000],
        "Ui_V":      [1000],
        "Uimp_kV":   [4, 6, 8, 12],
        "In_A":      [630, 800, 1250, 1600, 2000, 2500, 3200, 4000, 5000, 6300],
        "Icw_kA_1s": [25, 36, 50, 65, 80, 100],
        "Ipk_kA":    [52, 75, 105, 143, 176, 220]
      },
      "form_separation": "4a",
      "ip_default": "IP3X (front), IP40 (enclosure)",
      "ik_default": "IK09",
      "mandatory_characteristics": [
        "rated_operational_voltage_Ue",
        "rated_insulation_voltage_Ui",
        "rated_impulse_withstand_Uimp",
        "rated_current_In",
        "rated_short_time_withstand_Icw",
        "rated_peak_withstand_Ipk",
        "rated_frequency_fn",
        "ip_code",
        "ik_code",
        "form_separation",
        "internal_arc_classification"
      ],
      "verification_clauses": [
        "10.2 strength",
        "10.3 IP",
        "10.4 clearances/creepage",
        "10.5 electric shock protection",
        "10.6 incorporation of switching/protective devices",
        "10.7 internal electrical circuits",
        "10.8 terminals for external conductors",
        "10.9 dielectric properties",
        "10.10 temperature rise verification",
        "10.11 short-circuit withstand verification",
        "10.13 mechanical operation"
      ],
      "drawn_as": ["DB_MAIN"],
      "typical_components": ["ACB_3P", "MCCB_3P", "BUSBAR_3PH", "CT_METERING", "MULTIFUNCTION_METER", "SPD_TYPE1", "SPD_TYPE2"],
      "application_examples": [
        "Hospital essential supply main switchboards",
        "Data centre main LV boards with bus-tie redundancy",
        "Refineries / petrochemical with high availability requirements"
      ],
      "related_iec_60364": ["IEC60364-4-43", "IEC60364-5-53", "IEC60364-6", "IEC60364-7-710 (Medical)"],
      "related_bs_7671": ["Section 537", "Section 710 (Medical locations)"],
      "usage_notes": "Form 4a is the standard for high-availability commercial/industrial mains. The cost premium over 3b is justified by the ability to terminate a single outgoing circuit without exposing neighbouring circuits' cables.",
      "related_assemblies": ["PSC_ASSEMBLY_FORM_3B", "PSC_ASSEMBLY_FORM_4B"]
    },
    {
      "assembly_id": "PSC_ASSEMBLY_FORM_4B",
      "iec_ref": "IEC61439-2:2020",
      "iec_part": 2,
      "iec_title": "PSC-Assembly Form 4b — busbar, functional unit, and individual-termination separation",
      "draftsman_id": "PSC_ASSEMBLY_FORM_4B",
      "application_scope": "Form 4a plus separation between INDIVIDUAL outgoing terminals — each outgoing conductor is in its own compartment. Highest cost, highest maintainability and arc-flash containment.",
      "rated_quantities": {
        "Ue_V":      [230, 400, 690, 1000],
        "Ui_V":      [1000],
        "Uimp_kV":   [4, 6, 8, 12],
        "In_A":      [800, 1250, 1600, 2000, 2500, 3200, 4000, 5000, 6300],
        "Icw_kA_1s": [36, 50, 65, 80, 100],
        "Ipk_kA":    [75, 105, 143, 176, 220]
      },
      "form_separation": "4b",
      "ip_default": "IP4X (front), IP54 (enclosure)",
      "ik_default": "IK10",
      "mandatory_characteristics": [
        "rated_operational_voltage_Ue",
        "rated_insulation_voltage_Ui",
        "rated_impulse_withstand_Uimp",
        "rated_current_In",
        "rated_short_time_withstand_Icw",
        "rated_peak_withstand_Ipk",
        "rated_frequency_fn",
        "ip_code",
        "ik_code",
        "form_separation",
        "internal_arc_classification"
      ],
      "verification_clauses": [
        "10.2 strength",
        "10.3 IP",
        "10.4 clearances/creepage",
        "10.5 electric shock protection",
        "10.6 incorporation of switching/protective devices",
        "10.7 internal electrical circuits",
        "10.8 terminals for external conductors",
        "10.9 dielectric properties",
        "10.10 temperature rise verification",
        "10.11 short-circuit withstand verification",
        "10.13 mechanical operation"
      ],
      "drawn_as": ["DB_MAIN"],
      "typical_components": ["ACB_3P", "ACB_4P", "MCCB_3P", "BUSBAR_3PH", "CT_METERING", "MULTIFUNCTION_METER", "SPD_TYPE1", "SPD_TYPE2"],
      "application_examples": [
        "Nuclear safety LV boards",
        "Critical-process petrochemical/offshore mains",
        "Major hospital theatre/ICU primary distribution",
        "Tier IV data centre mains"
      ],
      "related_iec_60364": ["IEC60364-4-43", "IEC60364-5-53", "IEC60364-6", "IEC60364-7-710"],
      "related_bs_7671": ["Section 537", "Section 710"],
      "usage_notes": "Form 4b is rare — specify only where the cost premium is justified by the regulatory/operational availability requirement. Combined with IAC classification, it provides the highest practical arc-flash and live-work protection.",
      "related_assemblies": ["PSC_ASSEMBLY_FORM_4A"]
    }
  ]
}
```

- [ ] **Step 2: Validate JSON syntax**

Run: `python3 -c "import json; json.load(open('shared/standards/electrical/IEC61439/part2-psc-assemblies.json'))" && echo OK`
Expected: `OK`

- [ ] **Step 3: Verify schema fields**

Run: `python3 -c "import json; data=json.load(open('shared/standards/electrical/IEC61439/part2-psc-assemblies.json')); req=['assembly_id','iec_ref','iec_part','iec_title','draftsman_id','application_scope','rated_quantities','form_separation','ip_default','ik_default','mandatory_characteristics','verification_clauses','drawn_as','typical_components','application_examples','related_iec_60364','related_bs_7671','usage_notes','related_assemblies']; missing=[(s.get('assembly_id','?'), [f for f in req if f not in s]) for s in data['assemblies'] if any(f not in s for f in req)]; print('OK' if not missing else 'MISSING:'+str(missing))"`
Expected: `OK`

- [ ] **Step 4: Verify drawn_as references resolve**

Run:
```bash
python3 - <<'PY'
import json
idx_syms = {s['symbol_id'] for s in json.load(open('shared/standards/electrical/IEC60617/symbol-index.json'))['symbols']}
data = json.load(open('shared/standards/electrical/IEC61439/part2-psc-assemblies.json'))
unknown = []
for a in data['assemblies']:
    for s in a['drawn_as']:
        if s not in idx_syms:
            unknown.append((a['assembly_id'], s))
print('OK' if not unknown else 'UNKNOWN:'+str(unknown))
PY
```
Expected: `OK`

- [ ] **Step 5: Verify all 7 Form codes covered**

Run: `python3 -c "import json; data=json.load(open('shared/standards/electrical/IEC61439/part2-psc-assemblies.json')); forms=sorted(a['form_separation'] for a in data['assemblies']); print(forms); assert forms==['1','2a','2b','3a','3b','4a','4b'], forms; print('OK')"`
Expected: `['1', '2a', '2b', '3a', '3b', '4a', '4b']` then `OK`

- [ ] **Step 6: Commit**

```bash
git add shared/standards/electrical/IEC61439/part2-psc-assemblies.json
git commit -m "feat: IEC61439 part2-psc-assemblies.json — 7 Form variants (1, 2a, 2b, 3a, 3b, 4a, 4b)"
```

---

## Task 5: Create part3-dbo-assemblies.json (Part 3 — DBO Assemblies)

**Files:**
- Create: `shared/standards/electrical/IEC61439/part3-dbo-assemblies.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "IEC 61439 Part 3 — Distribution boards intended to be operated by ordinary persons (DBO)",
  "_iec_part": 3,
  "_version": "1.0.0",
  "_note": "Boards reachable by laypersons (consumer units, domestic/SOHO sub-DBs). Stricter accessibility and safety constraints than Part 2. Form separations rarely apply — Part 3 boards are typically single-compartment.",
  "assemblies": [
    {
      "assembly_id": "DBO_CONSUMER_UNIT",
      "iec_ref": "IEC61439-3:2012",
      "iec_part": 3,
      "iec_title": "Consumer unit / domestic distribution board",
      "draftsman_id": "DBO_CONSUMER_UNIT",
      "application_scope": "Final distribution board operated by an ordinary (non-skilled) person — domestic consumer units, small office units, apartments. Single-phase or three-phase incoming; up to ~125 A typical In. Internal-arc and finger-safe characteristics enforced; child-resistant where children may access.",
      "rated_quantities": {
        "Ue_V":      [230, 400],
        "Ui_V":      [500],
        "Uimp_kV":   [4, 6],
        "In_A":      [40, 63, 80, 100, 125],
        "Icw_kA_1s": [3, 4.5, 6, 10],
        "Ipk_kA":    [5, 8, 10, 17]
      },
      "form_separation": "n/a",
      "ip_default": "IP2XC (front, finger-safe with cover); IP30 (enclosure)",
      "ik_default": "IK07",
      "mandatory_characteristics": [
        "rated_operational_voltage_Ue",
        "rated_insulation_voltage_Ui",
        "rated_impulse_withstand_Uimp",
        "rated_current_In",
        "rated_conditional_short_circuit_current_Inc",
        "rated_frequency_fn",
        "ip_code",
        "ik_code",
        "way_count",
        "child_resistance_class_if_applicable"
      ],
      "verification_clauses": [
        "10.2 strength",
        "10.3 IP (note IP2XC finger-safe requirement)",
        "10.4 clearances/creepage",
        "10.5 electric shock protection (operator-side)",
        "10.6 incorporation of switching/protective devices",
        "10.7 internal electrical circuits",
        "10.8 terminals for external conductors",
        "10.9 dielectric properties",
        "10.10 temperature rise verification",
        "10.11 short-circuit withstand (typically Inc with upstream BS88 cut-out)",
        "10.13 mechanical operation"
      ],
      "drawn_as": ["CONSUMER_UNIT"],
      "typical_components": ["MCB_1P", "RCBO_1P", "RCD_2P", "SPD_TYPE2"],
      "application_examples": [
        "Single-family domestic consumer unit",
        "Apartment final DB",
        "Small SOHO unit"
      ],
      "related_iec_60364": ["IEC60364-4-41 (electric shock)", "IEC60364-5-53 (switchgear)"],
      "related_bs_7671": ["Reg 421.1.201 (CU enclosure material — non-combustible/metal)", "Section 537 (Isolation and switching)", "Section 314 (Division of installation)"],
      "usage_notes": "Per BS 7671 Reg 421.1.201, consumer units in domestic UK installations must be constructed of non-combustible material (metal). Specify RCBO per way rather than upstream RCD to avoid losing the whole installation on a single earth fault.",
      "related_assemblies": ["DBO_SUB_DB", "PSC_ASSEMBLY_FORM_1"]
    },
    {
      "assembly_id": "DBO_SUB_DB",
      "iec_ref": "IEC61439-3:2012",
      "iec_part": 3,
      "iec_title": "Sub-distribution board for ordinary persons",
      "draftsman_id": "DBO_SUB_DB",
      "application_scope": "Commercial / light-industrial sub-DB located in tenant/operator accessible areas (offices, retail, classrooms). Higher rating than a consumer unit but still finger-safe and operable by non-skilled persons.",
      "rated_quantities": {
        "Ue_V":      [230, 400],
        "Ui_V":      [500],
        "Uimp_kV":   [4, 6],
        "In_A":      [100, 125, 160, 250],
        "Icw_kA_1s": [6, 10, 15],
        "Ipk_kA":    [10, 17, 30]
      },
      "form_separation": "n/a",
      "ip_default": "IP2XC (front); IP30 (enclosure); IP44 if installed in dust/humid areas",
      "ik_default": "IK07",
      "mandatory_characteristics": [
        "rated_operational_voltage_Ue",
        "rated_insulation_voltage_Ui",
        "rated_impulse_withstand_Uimp",
        "rated_current_In",
        "rated_conditional_short_circuit_current_Inc",
        "rated_frequency_fn",
        "ip_code",
        "ik_code",
        "way_count"
      ],
      "verification_clauses": [
        "10.2 strength",
        "10.3 IP",
        "10.4 clearances/creepage",
        "10.5 electric shock protection",
        "10.6 incorporation of switching/protective devices",
        "10.10 temperature rise",
        "10.11 short-circuit withstand"
      ],
      "drawn_as": ["DB_SUB"],
      "typical_components": ["MCB_1P", "MCB_3P", "RCBO_1P", "RCD_4P", "SPD_TYPE2"],
      "application_examples": [
        "Floor-level sub-DB in an office building",
        "Retail tenancy DB",
        "Classroom DB in a school"
      ],
      "related_iec_60364": ["IEC60364-4-41", "IEC60364-5-53"],
      "related_bs_7671": ["Reg 411.4 (TN systems)", "Section 537"],
      "usage_notes": "Specify finger-safe IP2XC on the front face — common cause of failures is the OEM defaulting to IP2X which is finger-safe with a tool but NOT finger-safe to a child's finger.",
      "related_assemblies": ["DBO_CONSUMER_UNIT", "PSC_ASSEMBLY_FORM_2B"]
    }
  ]
}
```

- [ ] **Step 2: Validate JSON syntax**

Run: `python3 -c "import json; json.load(open('shared/standards/electrical/IEC61439/part3-dbo-assemblies.json'))" && echo OK`
Expected: `OK`

- [ ] **Step 3: Verify schema fields and drawn_as resolution**

Run:
```bash
python3 - <<'PY'
import json
req=['assembly_id','iec_ref','iec_part','iec_title','draftsman_id','application_scope','rated_quantities','form_separation','ip_default','ik_default','mandatory_characteristics','verification_clauses','drawn_as','typical_components','application_examples','related_iec_60364','related_bs_7671','usage_notes','related_assemblies']
data = json.load(open('shared/standards/electrical/IEC61439/part3-dbo-assemblies.json'))
missing = [(a.get('assembly_id','?'), [f for f in req if f not in a]) for a in data['assemblies'] if any(f not in a for f in req)]
print('SCHEMA: OK' if not missing else 'SCHEMA MISSING:'+str(missing))
idx = {s['symbol_id'] for s in json.load(open('shared/standards/electrical/IEC60617/symbol-index.json'))['symbols']}
unk = [(a['assembly_id'], s) for a in data['assemblies'] for s in a['drawn_as'] if s not in idx]
print('DRAWN_AS: OK' if not unk else 'DRAWN_AS UNKNOWN:'+str(unk))
PY
```
Expected: `SCHEMA: OK` and `DRAWN_AS: OK`

- [ ] **Step 4: Commit**

```bash
git add shared/standards/electrical/IEC61439/part3-dbo-assemblies.json
git commit -m "feat: IEC61439 part3-dbo-assemblies.json — consumer unit and sub-DB for ordinary persons"
```

---

## Task 6: Create part4-acs-assemblies.json (Part 4 — Construction Site Assemblies)

**Files:**
- Create: `shared/standards/electrical/IEC61439/part4-acs-assemblies.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "IEC 61439 Part 4 — Assemblies for construction sites (ACS)",
  "_iec_part": 4,
  "_version": "1.0.0",
  "_note": "Temporary supplies for construction, demolition, and similar mobile/transportable sites. Tight constraints on mechanical robustness (IK ≥ 08), portability, and mandatory RCD per BS 7671 Section 704 / IEC 60364-7-704.",
  "assemblies": [
    {
      "assembly_id": "ACS_TRANSPORTABLE",
      "iec_ref": "IEC61439-4:2012",
      "iec_part": 4,
      "iec_title": "Transportable construction site assembly",
      "draftsman_id": "ACS_TRANSPORTABLE",
      "application_scope": "Mobile/transportable assembly used during construction or demolition. Designed to be moved between site locations, withstand site mechanical abuse, and remain safe in wet/dusty conditions. Always RCD-protected.",
      "rated_quantities": {
        "Ue_V":      [230, 400],
        "Ui_V":      [500],
        "Uimp_kV":   [6, 8],
        "In_A":      [16, 32, 63, 100, 125, 250],
        "Icw_kA_1s": [10, 15, 25],
        "Ipk_kA":    [17, 30, 52]
      },
      "form_separation": "n/a",
      "ip_default": "IP44 minimum (Clause 8.2 of Part 4); IP55 where wash-down is foreseeable",
      "ik_default": "IK08 minimum (mandatory under Part 4)",
      "mandatory_characteristics": [
        "rated_operational_voltage_Ue",
        "rated_insulation_voltage_Ui",
        "rated_impulse_withstand_Uimp",
        "rated_current_In",
        "rated_short_time_withstand_Icw",
        "rated_peak_withstand_Ipk",
        "rated_frequency_fn",
        "ip_code",
        "ik_code_minimum_08",
        "rcd_sensitivity_IDn",
        "mass_kg_for_transportability"
      ],
      "verification_clauses": [
        "10.2 strength (extra: drop test per Part 4)",
        "10.3 IP (mandatory IP44)",
        "10.4 clearances/creepage",
        "10.5 electric shock protection",
        "10.10 temperature rise (consider sun exposure)",
        "10.11 short-circuit withstand",
        "10.13 mechanical operation (including transport)"
      ],
      "drawn_as": ["DB_GENERAL"],
      "typical_components": ["MCB_3P", "RCD_4P", "RCBO_1P", "SOCKET_INDUSTRIAL_IP44", "SOCKET_COMMANDO_32A"],
      "application_examples": [
        "Site-distribution unit (SDU) on a construction site",
        "Transportable hookup for a temporary marquee",
        "Demolition site temporary supply"
      ],
      "related_iec_60364": ["IEC60364-7-704 (Construction and demolition sites)"],
      "related_bs_7671": ["Section 704 (Construction and demolition site installations)", "Reg 704.410.3 (RCD protection)"],
      "usage_notes": "Per IEC 60364-7-704 and BS 7671 Section 704, all socket outlets ≤ 32 A on construction sites require 30 mA RCD protection (or be supplied by SELV/PELV/separation). Specify RCD type B where there are DC components (variable-speed drives, EV chargers).",
      "related_assemblies": ["ACS_FIXED", "PSC_ASSEMBLY_FORM_1"]
    },
    {
      "assembly_id": "ACS_FIXED",
      "iec_ref": "IEC61439-4:2012",
      "iec_part": 4,
      "iec_title": "Fixed construction site assembly",
      "draftsman_id": "ACS_FIXED",
      "application_scope": "Fixed (not transportable) site assembly — typically the main site incomer or a permanent floor distribution on a long-running project. Same robustness as transportable but no drop-test requirement.",
      "rated_quantities": {
        "Ue_V":      [230, 400],
        "Ui_V":      [690],
        "Uimp_kV":   [6, 8],
        "In_A":      [63, 100, 125, 250, 400, 630],
        "Icw_kA_1s": [10, 15, 25, 36],
        "Ipk_kA":    [17, 30, 52, 75]
      },
      "form_separation": "n/a",
      "ip_default": "IP44 minimum",
      "ik_default": "IK08 minimum",
      "mandatory_characteristics": [
        "rated_operational_voltage_Ue",
        "rated_insulation_voltage_Ui",
        "rated_impulse_withstand_Uimp",
        "rated_current_In",
        "rated_short_time_withstand_Icw",
        "rated_peak_withstand_Ipk",
        "rated_frequency_fn",
        "ip_code",
        "ik_code_minimum_08",
        "rcd_sensitivity_IDn"
      ],
      "verification_clauses": [
        "10.2 strength",
        "10.3 IP",
        "10.4 clearances/creepage",
        "10.5 electric shock protection",
        "10.10 temperature rise",
        "10.11 short-circuit withstand",
        "10.13 mechanical operation"
      ],
      "drawn_as": ["DB_GENERAL", "DB_MAIN"],
      "typical_components": ["MCCB_3P", "RCD_4P", "SOCKET_INDUSTRIAL_IP44", "SOCKET_COMMANDO_32A", "BUSBAR_3PH"],
      "application_examples": [
        "Site main incomer assembly",
        "Floor-level fixed DB on a major project",
        "Long-duration concert venue / event site supply"
      ],
      "related_iec_60364": ["IEC60364-7-704"],
      "related_bs_7671": ["Section 704"],
      "usage_notes": "Fixed ACS may use higher In than transportable. Still requires IP44/IK08 minimum. Periodic inspection interval per IEC 60364-6 AMD1:2023 is every 3 months for construction sites — note this on the assembly's O&M handover.",
      "related_assemblies": ["ACS_TRANSPORTABLE", "PSC_ASSEMBLY_FORM_2B"]
    }
  ]
}
```

- [ ] **Step 2: Validate**

Run:
```bash
python3 - <<'PY'
import json
req=['assembly_id','iec_ref','iec_part','iec_title','draftsman_id','application_scope','rated_quantities','form_separation','ip_default','ik_default','mandatory_characteristics','verification_clauses','drawn_as','typical_components','application_examples','related_iec_60364','related_bs_7671','usage_notes','related_assemblies']
data = json.load(open('shared/standards/electrical/IEC61439/part4-acs-assemblies.json'))
missing = [(a.get('assembly_id','?'), [f for f in req if f not in a]) for a in data['assemblies'] if any(f not in a for f in req)]
print('SCHEMA: OK' if not missing else 'SCHEMA MISSING:'+str(missing))
idx = {s['symbol_id'] for s in json.load(open('shared/standards/electrical/IEC60617/symbol-index.json'))['symbols']}
unk = [(a['assembly_id'], s) for a in data['assemblies'] for s in a['drawn_as'] if s not in idx]
print('DRAWN_AS: OK' if not unk else 'DRAWN_AS UNKNOWN:'+str(unk))
PY
```
Expected: `SCHEMA: OK` and `DRAWN_AS: OK`

- [ ] **Step 3: Commit**

```bash
git add shared/standards/electrical/IEC61439/part4-acs-assemblies.json
git commit -m "feat: IEC61439 part4-acs-assemblies.json — construction site assemblies"
```

---

## Task 7: Create part5-penda-assemblies.json (Part 5 — Public Network Distribution)

**Files:**
- Create: `shared/standards/electrical/IEC61439/part5-penda-assemblies.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "IEC 61439 Part 5 — Power distribution assemblies for public electricity networks (PENDA)",
  "_iec_part": 5,
  "_version": "1.0.0",
  "_note": "DNO / utility-side assemblies — outdoor cabinets, ground-mounted kiosks, pole-mounted distribution. Severe environmental, vandal, and lightning-impulse withstand requirements. Owned by the DNO, not the building owner — relevant to MEP design only at the supply boundary.",
  "assemblies": [
    {
      "assembly_id": "PENDA_KIOSK_GROUND_MOUNTED",
      "iec_ref": "IEC61439-5:2014",
      "iec_part": 5,
      "iec_title": "Ground-mounted distribution kiosk (PENDA)",
      "draftsman_id": "PENDA_KIOSK_GROUND_MOUNTED",
      "application_scope": "Outdoor ground-mounted DNO distribution kiosk feeding LV mains in residential or light-commercial neighbourhoods. Subject to vandalism, weather, and lightning impulse stress.",
      "rated_quantities": {
        "Ue_V":      [400, 690],
        "Ui_V":      [1000],
        "Uimp_kV":   [8, 12],
        "In_A":      [400, 630, 800, 1250, 1600, 2000, 2500],
        "Icw_kA_1s": [25, 36, 50, 65],
        "Ipk_kA":    [52, 75, 105, 143]
      },
      "form_separation": "n/a",
      "ip_default": "IP44 minimum (Part 5 Clause 8.2); IP54 where wash-down is foreseeable",
      "ik_default": "IK10 (vandal-resistant)",
      "mandatory_characteristics": [
        "rated_operational_voltage_Ue",
        "rated_insulation_voltage_Ui",
        "rated_impulse_withstand_Uimp",
        "rated_current_In",
        "rated_short_time_withstand_Icw",
        "rated_peak_withstand_Ipk",
        "rated_frequency_fn",
        "ip_code",
        "ik_code_minimum_10",
        "solar_radiation_protection_class",
        "lightning_impulse_withstand"
      ],
      "verification_clauses": [
        "10.2 strength (with vandal resistance)",
        "10.3 IP",
        "10.4 clearances/creepage (outdoor pollution degree)",
        "10.5 electric shock protection",
        "10.9 dielectric (lightning impulse)",
        "10.10 temperature rise (solar gain)",
        "10.11 short-circuit withstand",
        "10.13 mechanical operation"
      ],
      "drawn_as": ["DB_MAIN"],
      "typical_components": ["FUSE_3P", "FUSE_SWITCH", "BUSBAR_3PH", "SPD_TYPE1"],
      "application_examples": [
        "Residential street distribution pillar",
        "Light commercial area DNO kiosk",
        "DNO LV branch-line feeder cabinet"
      ],
      "related_iec_60364": ["Note: PENDA assemblies are DNO-side and not covered by IEC 60364 (which is consumer-side). They appear at the supply interface only."],
      "related_bs_7671": ["Reg 113.1 (Distributor supply interface)"],
      "usage_notes": "Outside the scope of most MEP design — relevant only at the supply boundary where the DNO's PENDA terminates and the consumer's installation begins. Cross-reference for SPD coordination — a Type 1 SPD inside the building is typically coordinated with a Type 1+2 in the upstream PENDA.",
      "related_assemblies": ["PENDA_POLE_MOUNTED", "ASSEMBLY_OUTDOOR_SPECIAL_SERVICE"]
    },
    {
      "assembly_id": "PENDA_POLE_MOUNTED",
      "iec_ref": "IEC61439-5:2014",
      "iec_part": 5,
      "iec_title": "Pole-mounted distribution assembly (PENDA)",
      "draftsman_id": "PENDA_POLE_MOUNTED",
      "application_scope": "Smaller pole-mounted PENDA used on rural LV overhead networks for service drops, single-customer breaks, or transformer-mounted incomers.",
      "rated_quantities": {
        "Ue_V":      [400],
        "Ui_V":      [690],
        "Uimp_kV":   [8],
        "In_A":      [63, 100, 160, 250],
        "Icw_kA_1s": [10, 15, 25],
        "Ipk_kA":    [17, 30, 52]
      },
      "form_separation": "n/a",
      "ip_default": "IP44 minimum",
      "ik_default": "IK08",
      "mandatory_characteristics": [
        "rated_operational_voltage_Ue",
        "rated_insulation_voltage_Ui",
        "rated_impulse_withstand_Uimp",
        "rated_current_In",
        "rated_short_time_withstand_Icw",
        "rated_peak_withstand_Ipk",
        "rated_frequency_fn",
        "ip_code",
        "ik_code",
        "solar_radiation_protection_class"
      ],
      "verification_clauses": [
        "10.2 strength",
        "10.3 IP",
        "10.4 clearances/creepage",
        "10.5 electric shock protection",
        "10.10 temperature rise",
        "10.11 short-circuit withstand",
        "10.13 mechanical operation"
      ],
      "drawn_as": ["DB_GENERAL"],
      "typical_components": ["FUSE_1P", "FUSE_3P", "SPD_TYPE1"],
      "application_examples": [
        "Rural LV service drop cabinet",
        "Pole-top single-customer break box",
        "Distribution transformer LV incomer cabinet"
      ],
      "related_iec_60364": ["Note: DNO-side equipment, outside IEC 60364 consumer-side scope"],
      "related_bs_7671": ["Reg 113.1"],
      "usage_notes": "Pole-mounted PENDA matters to MEP design only at the consumer interface — typically a service cutout fed from the PENDA. Specify the building SPD as Type 1+2 if the supply traverses overhead lines (high probability of lightning surge).",
      "related_assemblies": ["PENDA_KIOSK_GROUND_MOUNTED"]
    }
  ]
}
```

- [ ] **Step 2: Validate**

Run:
```bash
python3 - <<'PY'
import json
req=['assembly_id','iec_ref','iec_part','iec_title','draftsman_id','application_scope','rated_quantities','form_separation','ip_default','ik_default','mandatory_characteristics','verification_clauses','drawn_as','typical_components','application_examples','related_iec_60364','related_bs_7671','usage_notes','related_assemblies']
data = json.load(open('shared/standards/electrical/IEC61439/part5-penda-assemblies.json'))
missing = [(a.get('assembly_id','?'), [f for f in req if f not in a]) for a in data['assemblies'] if any(f not in a for f in req)]
print('SCHEMA: OK' if not missing else 'SCHEMA MISSING:'+str(missing))
idx = {s['symbol_id'] for s in json.load(open('shared/standards/electrical/IEC60617/symbol-index.json'))['symbols']}
unk = [(a['assembly_id'], s) for a in data['assemblies'] for s in a['drawn_as'] if s not in idx]
print('DRAWN_AS: OK' if not unk else 'DRAWN_AS UNKNOWN:'+str(unk))
PY
```
Expected: `SCHEMA: OK` and `DRAWN_AS: OK`

- [ ] **Step 3: Commit**

```bash
git add shared/standards/electrical/IEC61439/part5-penda-assemblies.json
git commit -m "feat: IEC61439 part5-penda-assemblies.json — DNO ground and pole-mounted distribution"
```

---

## Task 8: Create part6-busbar-trunking.json (Part 6 — Busbar Trunking Systems)

**Files:**
- Create: `shared/standards/electrical/IEC61439/part6-busbar-trunking.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "IEC 61439 Part 6 — Busbar trunking systems (BTS)",
  "_iec_part": 6,
  "_version": "1.0.0",
  "_note": "Prefabricated busbar trunking — used for vertical risers in tall buildings and horizontal mains in industrial halls and data centres. Joints, fire-stops, expansion joints, and fault paths are part of the BTS verification.",
  "assemblies": [
    {
      "assembly_id": "BTS_VERTICAL_RISER",
      "iec_ref": "IEC61439-6:2012",
      "iec_part": 6,
      "iec_title": "Busbar trunking — vertical riser",
      "draftsman_id": "BTS_VERTICAL_RISER",
      "application_scope": "Vertical riser BTS for tall buildings — feeds floor-level tap-off boxes from the main LV switchboard at building base. Includes fire-rated floor crossings (typically 2 h compartmentation), expansion compensation for thermal length change, and a tap-off plug-in interface at each floor.",
      "rated_quantities": {
        "Ue_V":      [400, 690],
        "Ui_V":      [1000],
        "Uimp_kV":   [8, 12],
        "In_A":      [400, 630, 800, 1250, 1600, 2000, 2500, 3200, 4000, 5000, 6300],
        "Icw_kA_1s": [25, 36, 50, 65, 80, 100],
        "Ipk_kA":    [52, 75, 105, 143, 176, 220]
      },
      "form_separation": "n/a",
      "ip_default": "IP54 (sandwich-style) or IP55 (compact aluminium)",
      "ik_default": "IK08",
      "mandatory_characteristics": [
        "rated_operational_voltage_Ue",
        "rated_insulation_voltage_Ui",
        "rated_impulse_withstand_Uimp",
        "rated_current_In",
        "rated_short_time_withstand_Icw",
        "rated_peak_withstand_Ipk",
        "rated_frequency_fn",
        "ip_code",
        "ik_code",
        "fire_resistance_at_floor_crossings",
        "expansion_compensation_length",
        "tap_off_compatibility"
      ],
      "verification_clauses": [
        "10.2 strength (including support spacing under fault force)",
        "10.3 IP",
        "10.4 clearances/creepage",
        "10.5 electric shock protection",
        "10.9 dielectric properties",
        "10.10 temperature rise (vertical convection plus solar if external)",
        "10.11 short-circuit withstand (force F = K·Ipk²·s/d on joints)",
        "10.13 mechanical operation (tap-off plug-in/out under load)"
      ],
      "drawn_as": ["BUSDUCT"],
      "typical_components": ["BUSBAR_3PH", "BUSDUCT", "FUSE_3P", "MCCB_3P"],
      "application_examples": [
        "Tall commercial office riser (typical 4000A copper or 5000A aluminium)",
        "Hospital tower vertical mains",
        "Data centre primary distribution riser"
      ],
      "related_iec_60364": ["IEC60364-5-52 (Wiring systems — busbar trunking installation)"],
      "related_bs_7671": ["Reg 521.4 (Busbar trunking systems)"],
      "usage_notes": "Specify fire compartmentation at every floor crossing (typically intumescent fire-stop kit supplied with the BTS) and expansion joints at the building expansion-joint locations. Ipk fault force on joints can exceed 50 kN — joint torquing and support spacing per the OEM's verified design.",
      "related_assemblies": ["BTS_HORIZONTAL_MAIN"]
    },
    {
      "assembly_id": "BTS_HORIZONTAL_MAIN",
      "iec_ref": "IEC61439-6:2012",
      "iec_part": 6,
      "iec_title": "Busbar trunking — horizontal mains run",
      "draftsman_id": "BTS_HORIZONTAL_MAIN",
      "application_scope": "Horizontal BTS — used in plant rooms, industrial halls, and data centres to feed multiple downstream sub-DBs or rack PDUs from a single switchboard outgoer. Tap-off boxes provide circuit drops at each load location.",
      "rated_quantities": {
        "Ue_V":      [400, 690],
        "Ui_V":      [1000],
        "Uimp_kV":   [6, 8, 12],
        "In_A":      [400, 630, 800, 1250, 1600, 2000, 2500, 3200, 4000, 5000, 6300],
        "Icw_kA_1s": [25, 36, 50, 65, 80, 100],
        "Ipk_kA":    [52, 75, 105, 143, 176, 220]
      },
      "form_separation": "n/a",
      "ip_default": "IP55 (horizontal, indoor); IP65 (overhead in wet areas)",
      "ik_default": "IK08",
      "mandatory_characteristics": [
        "rated_operational_voltage_Ue",
        "rated_insulation_voltage_Ui",
        "rated_impulse_withstand_Uimp",
        "rated_current_In",
        "rated_short_time_withstand_Icw",
        "rated_peak_withstand_Ipk",
        "rated_frequency_fn",
        "ip_code",
        "ik_code",
        "support_spacing_max",
        "tap_off_compatibility"
      ],
      "verification_clauses": [
        "10.2 strength",
        "10.3 IP",
        "10.4 clearances/creepage",
        "10.5 electric shock protection",
        "10.10 temperature rise",
        "10.11 short-circuit withstand",
        "10.13 mechanical operation"
      ],
      "drawn_as": ["BUSDUCT"],
      "typical_components": ["BUSBAR_3PH", "BUSDUCT", "MCCB_3P"],
      "application_examples": [
        "Data centre overhead busway feeding rack PDUs",
        "Industrial hall horizontal mains feeding zone DBs",
        "Plant room horizontal interlink between switchboards"
      ],
      "related_iec_60364": ["IEC60364-5-52", "IEC60364-5-54 (Earthing)"],
      "related_bs_7671": ["Reg 521.4"],
      "usage_notes": "Specify the maximum support spacing (typically 1.5 m for straight runs, less at joints). Where the BTS uses the enclosure as PE, verify Icw across the enclosure path is sufficient — this is a common failure mode in third-party verifications.",
      "related_assemblies": ["BTS_VERTICAL_RISER"]
    }
  ]
}
```

- [ ] **Step 2: Validate**

Run:
```bash
python3 - <<'PY'
import json
req=['assembly_id','iec_ref','iec_part','iec_title','draftsman_id','application_scope','rated_quantities','form_separation','ip_default','ik_default','mandatory_characteristics','verification_clauses','drawn_as','typical_components','application_examples','related_iec_60364','related_bs_7671','usage_notes','related_assemblies']
data = json.load(open('shared/standards/electrical/IEC61439/part6-busbar-trunking.json'))
missing = [(a.get('assembly_id','?'), [f for f in req if f not in a]) for a in data['assemblies'] if any(f not in a for f in req)]
print('SCHEMA: OK' if not missing else 'SCHEMA MISSING:'+str(missing))
idx = {s['symbol_id'] for s in json.load(open('shared/standards/electrical/IEC60617/symbol-index.json'))['symbols']}
unk = [(a['assembly_id'], s) for a in data['assemblies'] for s in a['drawn_as'] if s not in idx]
print('DRAWN_AS: OK' if not unk else 'DRAWN_AS UNKNOWN:'+str(unk))
PY
```
Expected: `SCHEMA: OK` and `DRAWN_AS: OK`

- [ ] **Step 3: Commit**

```bash
git add shared/standards/electrical/IEC61439/part6-busbar-trunking.json
git commit -m "feat: IEC61439 part6-busbar-trunking.json — vertical riser and horizontal mains BTS"
```

---

## Task 9: Create part7-applications.json (Part 7 — Specific Applications)

**Files:**
- Create: `shared/standards/electrical/IEC61439/part7-applications.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "IEC 61439 Part 7 — Assemblies for specific applications",
  "_iec_part": 7,
  "_version": "1.0.0",
  "_note": "Application-specific overlays on Parts 1–3. Each Part 7-x sub-part adds requirements for a particular application: camping/marinas (7-1), EV charging (7-2), safety services (7-3), PV (7-4), transformer assemblies (7-5).",
  "assemblies": [
    {
      "assembly_id": "PART7_1_MARINA_CAMPING",
      "iec_ref": "IEC61439-7-1:2014",
      "iec_part": 7,
      "iec_title": "Assembly for marinas, camping sites, market squares (Part 7-1)",
      "draftsman_id": "PART7_1_MARINA_CAMPING",
      "application_scope": "Distribution assemblies serving plug-in supplies at marinas, camping sites, market squares, charging points for caravans/boats, and similar outdoor public spaces. Mandatory RCD protection, IP44 minimum, tamper resistance.",
      "rated_quantities": {
        "Ue_V":      [230, 400],
        "Ui_V":      [500],
        "Uimp_kV":   [6, 8],
        "In_A":      [16, 32, 63, 100, 125],
        "Icw_kA_1s": [6, 10, 15],
        "Ipk_kA":    [10, 17, 30]
      },
      "form_separation": "n/a",
      "ip_default": "IP44 minimum (Clause 8 of Part 7-1)",
      "ik_default": "IK10 (vandal/impact)",
      "mandatory_characteristics": [
        "rated_operational_voltage_Ue",
        "rated_insulation_voltage_Ui",
        "rated_impulse_withstand_Uimp",
        "rated_current_In",
        "rated_short_time_withstand_Icw",
        "rated_peak_withstand_Ipk",
        "rated_frequency_fn",
        "ip_code",
        "ik_code_minimum_10",
        "rcd_sensitivity_IDn",
        "rcd_type"
      ],
      "verification_clauses": [
        "10.2 strength (vandal resistance)",
        "10.3 IP",
        "10.4 clearances/creepage",
        "10.5 electric shock protection (RCD + supplementary)",
        "10.10 temperature rise",
        "10.11 short-circuit withstand",
        "10.13 mechanical operation"
      ],
      "drawn_as": ["DB_GENERAL"],
      "typical_components": ["MCB_1P", "RCD_2P", "RCBO_1P", "SOCKET_INDUSTRIAL_IP44", "SOCKET_COMMANDO_32A"],
      "application_examples": [
        "Marina berth supply pedestal",
        "Camping pitch hookup post",
        "Market square traders' supply",
        "Caravan park bollard"
      ],
      "related_iec_60364": ["IEC60364-7-708 (Caravan parks, camping sites, marinas)", "IEC60364-7-709 (Marinas — same scope)"],
      "related_bs_7671": ["Section 708 (Caravan/camping)", "Section 709 (Marinas)"],
      "usage_notes": "30 mA RCD per outlet is the typical configuration. Specify Type A RCD as minimum; Type B where outlets serve EVSE or DC-leakage equipment (becoming common on EV-charging caravan posts).",
      "related_assemblies": ["PART7_2_EV_CHARGING", "ACS_TRANSPORTABLE"]
    },
    {
      "assembly_id": "PART7_2_EV_CHARGING",
      "iec_ref": "IEC61439-7-2:2018",
      "iec_part": 7,
      "iec_title": "Assembly for EV charging stations (Part 7-2)",
      "draftsman_id": "PART7_2_EV_CHARGING",
      "application_scope": "Assemblies forming part of an EV charging station — Mode 3 wallbox enclosure, Mode 4 DC fast charger cabinet, group-charging panel. Mandatory Type B RCD (or equivalent) where DC leakage is possible; cable rated at 100% of EVSE current per IEC 60364-7-722.",
      "rated_quantities": {
        "Ue_V":      [230, 400],
        "Ui_V":      [690],
        "Uimp_kV":   [6, 8],
        "In_A":      [16, 32, 63, 100, 125, 160, 250],
        "Icw_kA_1s": [10, 15, 25, 36],
        "Ipk_kA":    [17, 30, 52, 75]
      },
      "form_separation": "n/a",
      "ip_default": "IP44 (indoor); IP54 (outdoor); IP65 where wash-down is foreseeable",
      "ik_default": "IK08 (indoor); IK10 (outdoor public)",
      "mandatory_characteristics": [
        "rated_operational_voltage_Ue",
        "rated_insulation_voltage_Ui",
        "rated_impulse_withstand_Uimp",
        "rated_current_In",
        "rated_short_time_withstand_Icw",
        "rated_peak_withstand_Ipk",
        "rated_frequency_fn",
        "ip_code",
        "ik_code",
        "rcd_sensitivity_IDn",
        "rcd_type_must_handle_DC_leakage",
        "evse_rated_current_per_outlet",
        "cable_sized_100pct_continuous"
      ],
      "verification_clauses": [
        "10.2 strength",
        "10.3 IP",
        "10.4 clearances/creepage",
        "10.5 electric shock protection (Type B RCD)",
        "10.10 temperature rise (100% continuous duty)",
        "10.11 short-circuit withstand",
        "10.13 mechanical operation (cable retraction / connector durability)"
      ],
      "drawn_as": ["DB_GENERAL", "EV_CHARGING_POINT"],
      "typical_components": ["MCB_3P", "MCCB_3P", "RCD_4P", "RCBO_1P", "EV_CHARGING_POINT", "SPD_TYPE2"],
      "application_examples": [
        "Single Mode 3 wallbox (7.4 kW / 11 kW / 22 kW)",
        "Mode 4 DC fast-charger cabinet (50 kW / 150 kW / 350 kW)",
        "Group-charging assembly with load management"
      ],
      "related_iec_60364": ["IEC60364-7-722 (Supply of electric vehicles)", "IEC60364-4-44 AMD2:2018 (SPD requirements)"],
      "related_bs_7671": ["Section 722 (Electric vehicle charging installations)", "Reg 722.531.3.101 (Type B RCD where DC leakage)"],
      "usage_notes": "Cable to EVSE sized at 100 % of EVSE rated current — no diversity. Mandatory Type B RCD where DC leakage > 6 mA possible (Mode 3 unmanaged installations and all Mode 4). Document the load management policy if multiple chargers share a feeder.",
      "related_assemblies": ["PART7_1_MARINA_CAMPING", "PSC_ASSEMBLY_FORM_2B"]
    },
    {
      "assembly_id": "PART7_3_SAFETY_SERVICES",
      "iec_ref": "IEC61439-7-3:2018",
      "iec_part": 7,
      "iec_title": "Assembly for safety services (Part 7-3)",
      "draftsman_id": "PART7_3_SAFETY_SERVICES",
      "application_scope": "Assemblies supplying safety services (emergency lighting, fire alarm, fire pumps, smoke extraction, sprinkler pumps). Fire-integrity cabling, monitored supplies, automatic source-changeover with the safety-services generator.",
      "rated_quantities": {
        "Ue_V":      [230, 400],
        "Ui_V":      [690],
        "Uimp_kV":   [6, 8],
        "In_A":      [63, 100, 160, 250, 400, 630, 800],
        "Icw_kA_1s": [25, 36, 50],
        "Ipk_kA":    [52, 75, 105]
      },
      "form_separation": "n/a",
      "ip_default": "IP40 minimum",
      "ik_default": "IK08",
      "mandatory_characteristics": [
        "rated_operational_voltage_Ue",
        "rated_insulation_voltage_Ui",
        "rated_impulse_withstand_Uimp",
        "rated_current_In",
        "rated_short_time_withstand_Icw",
        "rated_peak_withstand_Ipk",
        "rated_frequency_fn",
        "ip_code",
        "ik_code",
        "source_changeover_method",
        "fire_integrity_class_E30_E60_E90",
        "supply_monitoring"
      ],
      "verification_clauses": [
        "10.2 strength",
        "10.3 IP",
        "10.4 clearances/creepage",
        "10.5 electric shock protection",
        "10.10 temperature rise",
        "10.11 short-circuit withstand",
        "10.13 mechanical operation (source-changeover)"
      ],
      "drawn_as": ["DB_MAIN", "DB_SUB", "PANEL_GENERATOR"],
      "typical_components": ["ACB_3P", "MCCB_3P", "ATS_2WAY", "RELAY_UNDERVOLTAGE", "BUSBAR_3PH"],
      "application_examples": [
        "Hospital essential supply changeover panel",
        "Emergency lighting central battery system supply",
        "Sprinkler/fire-pump motor control centre",
        "Smoke extraction fan supply"
      ],
      "related_iec_60364": ["IEC60364-5-56 (Safety services)", "IEC60364-7-710 (Medical)"],
      "related_bs_7671": ["Section 560 (Safety services)", "Section 710 (Medical locations)"],
      "usage_notes": "Specify the fire-integrity duration (E30/E60/E90/E120) per the project's fire strategy. Source-changeover time matters — Class 0 (no break), Class 0.15, Class 0.5, Class 15, or Class > 15 s — and must match the load tolerance.",
      "related_assemblies": ["PSC_ASSEMBLY_FORM_3B", "PSC_ASSEMBLY_FORM_4A"]
    },
    {
      "assembly_id": "PART7_4_SOLAR_PV",
      "iec_ref": "IEC61439-7-4:2022",
      "iec_part": 7,
      "iec_title": "Assembly for solar PV (Part 7-4)",
      "draftsman_id": "PART7_4_SOLAR_PV",
      "application_scope": "PV-side assemblies — string combiner box, recombiner, DC isolator cabinet, AC-side inverter output combiner. DC fault current behaviour differs from AC; arc fault protection (AFCI) required in some jurisdictions.",
      "rated_quantities": {
        "Ue_V":      [600, 1000, 1500],
        "Ui_V":      [1000, 1500],
        "Uimp_kV":   [6, 8, 12],
        "In_A":      [16, 32, 63, 100, 160, 250],
        "Icw_kA_1s": [10, 15, 25],
        "Ipk_kA":    [17, 30, 52]
      },
      "form_separation": "n/a",
      "ip_default": "IP65 (outdoor exposed); IP54 (indoor inverter room)",
      "ik_default": "IK08",
      "mandatory_characteristics": [
        "rated_operational_voltage_Ue_DC",
        "rated_insulation_voltage_Ui",
        "rated_impulse_withstand_Uimp",
        "rated_current_In",
        "rated_short_time_withstand_Icw",
        "rated_peak_withstand_Ipk",
        "rated_frequency_fn",
        "ip_code",
        "ik_code",
        "DC_isolation_method",
        "afci_provision_if_applicable",
        "spd_dc_input"
      ],
      "verification_clauses": [
        "10.2 strength",
        "10.3 IP",
        "10.4 clearances/creepage (DC arcing distances)",
        "10.5 electric shock protection",
        "10.10 temperature rise (solar gain)",
        "10.11 short-circuit withstand",
        "10.13 mechanical operation"
      ],
      "drawn_as": ["DB_GENERAL"],
      "typical_components": ["FUSE_1P", "ISOLATOR_2P", "ISOLATOR_3P", "SPD_TYPE2", "SOLAR_PV"],
      "application_examples": [
        "Rooftop PV string combiner box (DC side)",
        "Ground-mount PV recombiner cabinet",
        "Inverter AC-side combiner panel"
      ],
      "related_iec_60364": ["IEC60364-7-712 (PV installations)", "IEC60364-4-44 AMD2:2018 (SPD)"],
      "related_bs_7671": ["Section 712 (Solar PV)"],
      "usage_notes": "Specify DC-rated isolators (not AC isolators repurposed). Type 2 SPD required at the DC input to the inverter per IEC 60364-4-44 AMD2:2018. Arc fault circuit interrupters (AFCI) are mandatory in some markets (US NEC 690.11) — check jurisdiction.",
      "related_assemblies": ["PART7_2_EV_CHARGING", "ASSEMBLY_OUTDOOR_SPECIAL_SERVICE"]
    },
    {
      "assembly_id": "PART7_5_TRANSFORMER_ASSEMBLY",
      "iec_ref": "IEC61439-7-5:2022",
      "iec_part": 7,
      "iec_title": "Transformer-incorporated assembly (Part 7-5)",
      "draftsman_id": "PART7_5_TRANSFORMER_ASSEMBLY",
      "application_scope": "Assemblies that integrate a small transformer with LV switchgear — e.g. site-wide isolating transformer combined with its protection switchgear, separated-circuit medical IT panels, control-transformer panels.",
      "rated_quantities": {
        "Ue_V":      [230, 400, 690],
        "Ui_V":      [1000],
        "Uimp_kV":   [6, 8, 12],
        "In_A":      [16, 32, 63, 100, 160, 250, 400],
        "Icw_kA_1s": [10, 15, 25, 36],
        "Ipk_kA":    [17, 30, 52, 75]
      },
      "form_separation": "n/a",
      "ip_default": "IP30 (indoor); IP54 (outdoor)",
      "ik_default": "IK08",
      "mandatory_characteristics": [
        "rated_operational_voltage_Ue",
        "rated_insulation_voltage_Ui",
        "rated_impulse_withstand_Uimp",
        "rated_current_In",
        "rated_short_time_withstand_Icw",
        "rated_peak_withstand_Ipk",
        "rated_frequency_fn",
        "ip_code",
        "ik_code",
        "transformer_kVA_rating",
        "primary_secondary_voltage",
        "insulation_monitoring_if_IT"
      ],
      "verification_clauses": [
        "10.2 strength",
        "10.3 IP",
        "10.4 clearances/creepage",
        "10.5 electric shock protection",
        "10.10 temperature rise (transformer plus switchgear combined)",
        "10.11 short-circuit withstand",
        "10.13 mechanical operation"
      ],
      "drawn_as": ["DB_GENERAL", "DB_SUB"],
      "typical_components": ["TRANSFORMER_2W", "MCCB_3P", "MCB_3P", "RELAY_DIFFERENTIAL"],
      "application_examples": [
        "Medical IT separation transformer panel (Group 2 locations)",
        "Site-isolating transformer + LV switchgear combined cabinet",
        "Reduced-voltage power tools supply panel (110 V CTE)"
      ],
      "related_iec_60364": ["IEC60364-7-710 (Medical locations)", "IEC60364-4-41 (Electric shock — separation)"],
      "related_bs_7671": ["Section 710 (Medical locations)", "Reg 413.3 (Electrical separation)"],
      "usage_notes": "For medical IT applications, insulation-monitoring device (IMD) per IEC 61557-8 is mandatory and must be incorporated in the assembly. Temperature-rise verification must account for transformer losses (typically 1–2 % of rated kVA) plus switchgear losses combined.",
      "related_assemblies": ["PART7_3_SAFETY_SERVICES", "PSC_ASSEMBLY_FORM_2B"]
    }
  ]
}
```

- [ ] **Step 2: Validate**

Run:
```bash
python3 - <<'PY'
import json
req=['assembly_id','iec_ref','iec_part','iec_title','draftsman_id','application_scope','rated_quantities','form_separation','ip_default','ik_default','mandatory_characteristics','verification_clauses','drawn_as','typical_components','application_examples','related_iec_60364','related_bs_7671','usage_notes','related_assemblies']
data = json.load(open('shared/standards/electrical/IEC61439/part7-applications.json'))
missing = [(a.get('assembly_id','?'), [f for f in req if f not in a]) for a in data['assemblies'] if any(f not in a for f in req)]
print('SCHEMA: OK' if not missing else 'SCHEMA MISSING:'+str(missing))
idx = {s['symbol_id'] for s in json.load(open('shared/standards/electrical/IEC60617/symbol-index.json'))['symbols']}
unk = [(a['assembly_id'], s) for a in data['assemblies'] for s in a['drawn_as'] if s not in idx]
print('DRAWN_AS: OK' if not unk else 'DRAWN_AS UNKNOWN:'+str(unk))
print(f'Assembly count: {len(data["assemblies"])}')
PY
```
Expected: `SCHEMA: OK`, `DRAWN_AS: OK`, `Assembly count: 5`

- [ ] **Step 3: Commit**

```bash
git add shared/standards/electrical/IEC61439/part7-applications.json
git commit -m "feat: IEC61439 part7-applications.json — 5 sub-parts (marinas, EV, safety, PV, transformer)"
```

---

## Task 10: Create form-separations.json (cross-cutting topic)

**Files:**
- Create: `shared/standards/electrical/IEC61439/form-separations.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "IEC 61439 — Form Separations",
  "_iec_part": "2 (with cross-references to 3 and 4)",
  "_version": "1.0.0",
  "_note": "Form codes defined in IEC 61439-2 Annex 101. ASCII diagrams use: BUSBARS at top, FU = functional unit compartment, T = outgoing-terminal compartment, | = metallic barrier, space = same compartment.",
  "forms": [
    {
      "form_code": "1",
      "iec_ref": "IEC61439-2:2020 Annex 101",
      "title": "Form 1 — no internal segregation",
      "segregation_of": {
        "busbars_from_functional_units": false,
        "functional_units_from_each_other": false,
        "terminals_for_outgoing_conductors_separated_from_busbar": false,
        "terminals_for_outgoing_conductors_separated_from_each_other": false
      },
      "ascii_diagram": [
        "+---------------------------------+",
        "|  BUSBARS  FU  FU  FU  T  T  T   |",
        "|                                 |",
        "+---------------------------------+"
      ],
      "applications": ["Lowest-cost option where whole-board de-energising is acceptable for any maintenance"],
      "advantages": ["Cheapest", "Most compact for given rating"],
      "disadvantages": ["No live-work safety — entire board is exposed once opened"],
      "vs_neighbours": {"Form_2a": "2a adds a barrier between busbar and functional units"},
      "draftsman_id": "FORM_1",
      "drawn_as": ["DB_GENERAL"],
      "usage_notes": "Acceptable only for plant-only assemblies where maintenance is always with the whole board off."
    },
    {
      "form_code": "2a",
      "iec_ref": "IEC61439-2:2020 Annex 101",
      "title": "Form 2a — busbars segregated, functional units in common compartment, terminals not segregated from busbar",
      "segregation_of": {
        "busbars_from_functional_units": true,
        "functional_units_from_each_other": false,
        "terminals_for_outgoing_conductors_separated_from_busbar": false,
        "terminals_for_outgoing_conductors_separated_from_each_other": false
      },
      "ascii_diagram": [
        "+---------------------------------+",
        "|  BUSBARS                        |",
        "+---------------------------------+",
        "|  FU  FU  FU  T  T  T            |",
        "+---------------------------------+"
      ],
      "applications": ["Industrial sub-distribution above 250 A where busbar isolation is needed"],
      "advantages": ["Busbar can stay live while functional units are de-energised"],
      "disadvantages": ["Outgoing terminations remain at busbar potential when busbar is live"],
      "vs_neighbours": {"Form_1": "Adds busbar segregation", "Form_2b": "2b adds segregation of outgoing terminals from busbar"},
      "draftsman_id": "FORM_2A",
      "drawn_as": ["DB_SUB", "DB_GENERAL"],
      "usage_notes": "Entry-level form for installations needing busbar isolation."
    },
    {
      "form_code": "2b",
      "iec_ref": "IEC61439-2:2020 Annex 101",
      "title": "Form 2b — busbars segregated, functional units common, outgoing terminals segregated from busbar",
      "segregation_of": {
        "busbars_from_functional_units": true,
        "functional_units_from_each_other": false,
        "terminals_for_outgoing_conductors_separated_from_busbar": true,
        "terminals_for_outgoing_conductors_separated_from_each_other": false
      },
      "ascii_diagram": [
        "+---------------------------------+",
        "|  BUSBARS                        |",
        "+---------------------------------+",
        "|  FU  FU  FU                     |",
        "+----+----+----+-----------------+",
        "|  T |  T |  T |                 |",
        "+----+----+----+-----------------+"
      ],
      "applications": ["Commercial mains 400–1600 A", "Light industrial main switchboards"],
      "advantages": ["Can work on outgoing terminations without de-energising busbar"],
      "disadvantages": ["Functional units still share a compartment"],
      "vs_neighbours": {"Form_2a": "Adds terminal segregation from busbar", "Form_3a": "3a adds segregation between functional units"},
      "draftsman_id": "FORM_2B",
      "drawn_as": ["DB_MAIN", "DB_SUB"],
      "usage_notes": "Common default for commercial mains 400–1600 A where critical-circuit independence is not required."
    },
    {
      "form_code": "3a",
      "iec_ref": "IEC61439-2:2020 Annex 101",
      "title": "Form 3a — busbar and functional-unit segregation, terminals not segregated from busbar",
      "segregation_of": {
        "busbars_from_functional_units": true,
        "functional_units_from_each_other": true,
        "terminals_for_outgoing_conductors_separated_from_busbar": false,
        "terminals_for_outgoing_conductors_separated_from_each_other": false
      },
      "ascii_diagram": [
        "+---------------------------------+",
        "|  BUSBARS                        |",
        "+---------------------------------+",
        "| FU | FU | FU | FU | FU | FU |   |",
        "+----+----+----+----+----+----+---+",
        "|  T    T    T    T    T    T     |",
        "+---------------------------------+"
      ],
      "applications": ["Industrial MCCs where outgoing terminations remain in busbar compartment"],
      "advantages": ["Single functional unit can be worked on while neighbours stay live"],
      "disadvantages": ["Outgoing terminations remain risky"],
      "vs_neighbours": {"Form_2b": "Adds segregation between functional units", "Form_3b": "3b adds terminal segregation from busbar"},
      "draftsman_id": "FORM_3A",
      "drawn_as": ["DB_MAIN"],
      "usage_notes": "Industrial-only — Form 3b is preferred for new commercial designs."
    },
    {
      "form_code": "3b",
      "iec_ref": "IEC61439-2:2020 Annex 101",
      "title": "Form 3b — busbar and functional-unit segregation, terminals segregated from busbar but grouped per unit",
      "segregation_of": {
        "busbars_from_functional_units": true,
        "functional_units_from_each_other": true,
        "terminals_for_outgoing_conductors_separated_from_busbar": true,
        "terminals_for_outgoing_conductors_separated_from_each_other": false
      },
      "ascii_diagram": [
        "+---------------------------------+",
        "|  BUSBARS                        |",
        "+----+----+----+----+----+----+---+",
        "| FU | FU | FU | FU | FU | FU |   |",
        "+----+----+----+----+----+----+---+",
        "| T1 | T2 | T3 | T4 | T5 | T6 |   |",
        "+----+----+----+----+----+----+---+"
      ],
      "applications": ["Critical services main switchboards", "Industrial MCCs requiring single-circuit maintenance", "Hospital essential supply distribution"],
      "advantages": ["Single circuit maintenance with rest live", "Outgoing terminations isolated from busbar"],
      "disadvantages": ["Higher cost than Form 3a", "More floor space than Form 2"],
      "vs_neighbours": {"Form_2b": "Adds segregation between functional units (was a single bay)", "Form_3a": "Form 3a has outgoing terminals in the SAME compartment as the functional unit; 3b separates them", "Form_4a": "Form 4a separates each outgoing terminal individually rather than as a group"},
      "draftsman_id": "FORM_3B",
      "drawn_as": ["DB_MAIN", "DB_SUB"],
      "usage_notes": "Default choice for commercial main switchboards 400–4000 A. Specify explicitly on the assembly schedule — the OEM cannot infer the Form from a generic 'main switchboard' callout."
    },
    {
      "form_code": "4a",
      "iec_ref": "IEC61439-2:2020 Annex 101",
      "title": "Form 4a — busbar, functional-unit, and grouped-terminal separation",
      "segregation_of": {
        "busbars_from_functional_units": true,
        "functional_units_from_each_other": true,
        "terminals_for_outgoing_conductors_separated_from_busbar": true,
        "terminals_for_outgoing_conductors_separated_from_each_other": true,
        "individual_terminals_within_same_unit_separated": false
      },
      "ascii_diagram": [
        "+---------------------------------+",
        "|  BUSBARS                        |",
        "+----+----+----+----+----+----+---+",
        "| FU | FU | FU | FU | FU | FU |   |",
        "+----+----+----+----+----+----+---+",
        "|T1.x|T2.x|T3.x|T4.x|T5.x|T6.x|   |",
        "+----+----+----+----+----+----+---+"
      ],
      "applications": ["Hospital essential supply", "Data centre main LV boards", "High-availability industrial"],
      "advantages": ["Each functional unit's terminations isolated from neighbours'"],
      "disadvantages": ["Higher cost than 3b"],
      "vs_neighbours": {"Form_3b": "Adds terminal-group separation between units", "Form_4b": "4b adds individual-terminal separation within a unit"},
      "draftsman_id": "FORM_4A",
      "drawn_as": ["DB_MAIN"],
      "usage_notes": "Standard for high-availability commercial/industrial mains."
    },
    {
      "form_code": "4b",
      "iec_ref": "IEC61439-2:2020 Annex 101",
      "title": "Form 4b — busbar, functional-unit, and individual-terminal separation",
      "segregation_of": {
        "busbars_from_functional_units": true,
        "functional_units_from_each_other": true,
        "terminals_for_outgoing_conductors_separated_from_busbar": true,
        "terminals_for_outgoing_conductors_separated_from_each_other": true,
        "individual_terminals_within_same_unit_separated": true
      },
      "ascii_diagram": [
        "+---------------------------------+",
        "|  BUSBARS                        |",
        "+----+----+----+----+----+----+---+",
        "| FU | FU | FU | FU | FU | FU |   |",
        "+----+----+----+----+----+----+---+",
        "|T|T|T|T|T|T|T|T|T|T|T|T|T|T|T|   |",
        "+---------------------------------+"
      ],
      "applications": ["Nuclear safety LV boards", "Tier IV data centre mains", "Major hospital theatre/ICU primary distribution"],
      "advantages": ["Highest practical segregation; each outgoing terminal in own compartment"],
      "disadvantages": ["Highest cost; physically largest"],
      "vs_neighbours": {"Form_4a": "Adds separation between individual terminals within the same functional unit"},
      "draftsman_id": "FORM_4B",
      "drawn_as": ["DB_MAIN"],
      "usage_notes": "Specify only where regulatory/operational availability requirement justifies the cost premium."
    }
  ]
}
```

- [ ] **Step 2: Validate JSON syntax**

Run: `python3 -c "import json; json.load(open('shared/standards/electrical/IEC61439/form-separations.json'))" && echo OK`
Expected: `OK`

- [ ] **Step 3: Verify all 7 Forms present**

Run: `python3 -c "import json; data=json.load(open('shared/standards/electrical/IEC61439/form-separations.json')); codes=sorted(f['form_code'] for f in data['forms']); print(codes); assert codes==['1','2a','2b','3a','3b','4a','4b']; print('OK')"`
Expected: `['1', '2a', '2b', '3a', '3b', '4a', '4b']` then `OK`

- [ ] **Step 4: Commit**

```bash
git add shared/standards/electrical/IEC61439/form-separations.json
git commit -m "feat: IEC61439 form-separations.json — Forms 1, 2a, 2b, 3a, 3b, 4a, 4b with ASCII diagrams"
```

---

## Task 11: Create verification-methods.json (cross-cutting topic)

**Files:**
- Create: `shared/standards/electrical/IEC61439/verification-methods.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "IEC 61439 — Verification Methods Matrix",
  "_iec_part": "1 (referenced by all parts)",
  "_version": "1.0.0",
  "_note": "Three equivalent verification paths per IEC 61439-1 Clause 10. Annex D defines which methods are allowed for which characteristic. Designer specifies; OEM verifies.",
  "methods": [
    {
      "method_id": "TEST",
      "name": "Verification by testing",
      "iec_ref": "IEC61439-1 Clause 10",
      "description": "Physical test of a representative assembly against the standard. Performed by the original manufacturer (OM) or an accredited test laboratory.",
      "applies_to_characteristics": ["10.2 strength", "10.3 IP", "10.9 dielectric", "10.10 temperature rise", "10.11 short-circuit withstand", "10.13 mechanical operation"],
      "documentation": "Test certificate from accredited laboratory; type-test records retained by the OM.",
      "advantages": ["Most direct evidence", "Required for IP and dielectric"],
      "disadvantages": ["Costly", "Only the tested arrangement is verified — variants need cross-reference or fresh test"]
    },
    {
      "method_id": "CALC",
      "name": "Verification by calculation",
      "iec_ref": "IEC61439-1 Clause 10 + Annex E and Annex P",
      "description": "Engineering calculation per the standard's annexes. Annex E covers temperature rise (RDF, resistance, ambient correction). Annex P covers short-circuit withstand (force, thermal, mechanical stress).",
      "applies_to_characteristics": ["10.10 temperature rise (Annex E)", "10.11 short-circuit withstand (Annex P)"],
      "limits": "Permitted ONLY where an Annex method exists for the characteristic. NOT permitted for IP, dielectric, mechanical strength, or internal arc.",
      "documentation": "Calculation report referencing exact Annex method, with all assumptions, input data, and component datasheets. Must include the component derating chain.",
      "advantages": ["Cheaper than test", "Useful for tailored ratings (e.g. RDF for partly-loaded assemblies)"],
      "disadvantages": ["Limited applicability", "Requires accurate component data"]
    },
    {
      "method_id": "REFERENCE",
      "name": "Verification by comparison with reference design",
      "iec_ref": "IEC61439-1 Clause 10.5.3 + Annex D",
      "description": "Compare candidate assembly against a previously verified reference that bounds it. Bounding rules (same or larger enclosure, no worse component arrangement, busbar at least as oversized, etc.) per Annex D Table 13.",
      "applies_to_characteristics": ["10.2 strength", "10.5 electric shock protection", "10.10 temperature rise", "10.11 short-circuit withstand"],
      "limits": "Bounding rules in Annex D Table 13 must be strictly met — a single violation invalidates the comparison. NOT permitted for IP (candidate must be tested).",
      "documentation": "Reference design verification certificate from the OM + a bounding comparison report showing every Annex D criterion is satisfied.",
      "advantages": ["Cheapest", "Allows series of similar assemblies to share a single verification chain"],
      "disadvantages": ["Bounding rules are strict — small departures invalidate the comparison"]
    }
  ],
  "annex_d_matrix": {
    "_note": "Each row is a verification characteristic per IEC 61439-1 Clause 10. Methods marked 'Y' are permitted; 'N' not permitted. Note 1 columns indicate constraints.",
    "rows": [
      {"clause": "10.2",  "characteristic": "Strength of materials and parts",         "TEST": "Y", "CALC": "N", "REFERENCE": "Y"},
      {"clause": "10.3",  "characteristic": "Degree of protection (IP/IK)",            "TEST": "Y", "CALC": "N", "REFERENCE": "N"},
      {"clause": "10.4",  "characteristic": "Clearances and creepage distances",       "TEST": "Y", "CALC": "Y (per Annex F)", "REFERENCE": "Y"},
      {"clause": "10.5",  "characteristic": "Protection against electric shock",       "TEST": "Y", "CALC": "Y", "REFERENCE": "Y"},
      {"clause": "10.6",  "characteristic": "Incorporation of switching devices",       "TEST": "N", "CALC": "Y", "REFERENCE": "Y"},
      {"clause": "10.7",  "characteristic": "Internal electrical circuits",              "TEST": "Y", "CALC": "Y", "REFERENCE": "Y"},
      {"clause": "10.8",  "characteristic": "Terminals for external conductors",        "TEST": "Y", "CALC": "N", "REFERENCE": "Y"},
      {"clause": "10.9",  "characteristic": "Dielectric properties",                    "TEST": "Y", "CALC": "N", "REFERENCE": "N"},
      {"clause": "10.10", "characteristic": "Temperature rise",                          "TEST": "Y", "CALC": "Y (Annex E)", "REFERENCE": "Y"},
      {"clause": "10.11", "characteristic": "Short-circuit withstand",                  "TEST": "Y", "CALC": "Y (Annex P)", "REFERENCE": "Y"},
      {"clause": "10.12", "characteristic": "EMC",                                       "TEST": "Y", "CALC": "N", "REFERENCE": "Y"},
      {"clause": "10.13", "characteristic": "Mechanical operation",                      "TEST": "Y", "CALC": "N", "REFERENCE": "Y"}
    ]
  }
}
```

- [ ] **Step 2: Validate**

Run: `python3 -c "import json; json.load(open('shared/standards/electrical/IEC61439/verification-methods.json'))" && echo OK`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add shared/standards/electrical/IEC61439/verification-methods.json
git commit -m "feat: IEC61439 verification-methods.json — test/calc/reference trio with Annex D matrix"
```

---

## Task 12: Create ip-ik-ratings.json (cross-cutting topic)

**Files:**
- Create: `shared/standards/electrical/IEC61439/ip-ik-ratings.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "IEC 61439 — IP and IK Ratings",
  "_iec_part": "1 (Table 7); referenced by all parts",
  "_version": "1.0.0",
  "_note": "IP per IEC 60529, IK per IEC 62262 (formerly BS EN 50102). Default minimum IP and IK per application context shown in the minimum_per_application table below.",
  "ip_first_digit": [
    {"digit": 0, "meaning": "No protection"},
    {"digit": 1, "meaning": "Protected against solid foreign objects ≥ 50 mm (back of hand)"},
    {"digit": 2, "meaning": "Protected against solid foreign objects ≥ 12.5 mm (finger)"},
    {"digit": 3, "meaning": "Protected against solid foreign objects ≥ 2.5 mm (tool)"},
    {"digit": 4, "meaning": "Protected against solid foreign objects ≥ 1.0 mm (wire)"},
    {"digit": 5, "meaning": "Dust-protected — ingress not totally prevented but no harmful deposit"},
    {"digit": 6, "meaning": "Dust-tight — no ingress"}
  ],
  "ip_second_digit": [
    {"digit": 0, "meaning": "No protection"},
    {"digit": 1, "meaning": "Vertically dripping water"},
    {"digit": 2, "meaning": "Dripping water at 15° tilt"},
    {"digit": 3, "meaning": "Spraying water (rain)"},
    {"digit": 4, "meaning": "Splashing water from any direction"},
    {"digit": 5, "meaning": "Water jets from any direction"},
    {"digit": 6, "meaning": "Powerful water jets"},
    {"digit": 7, "meaning": "Temporary immersion to 1 m for 30 min"},
    {"digit": 8, "meaning": "Continuous immersion under conditions agreed with manufacturer"},
    {"digit": 9, "meaning": "High-pressure / high-temperature water jets (≥ 80 °C, ≥ 8 MPa)"}
  ],
  "ip_supplementary_letters": {
    "A": "Back of hand finger-safe (12.5 mm)",
    "B": "Finger finger-safe (12 mm test rod)",
    "C": "Tool finger-safe (2.5 mm)",
    "D": "Wire finger-safe (1 mm)"
  },
  "ip_supplementary_letters_meaning_notes": "Letters after the IP digits (e.g. IP2XC) provide finger-safe rating independent of the first digit. IP2XC means '≥ 12.5 mm protection plus 2.5 mm tool-finger-safe'.",
  "ik_codes": [
    {"code": "IK00", "energy_joules": "no protection", "test_mass_kg": "n/a", "drop_height_mm": "n/a"},
    {"code": "IK01", "energy_joules": 0.14, "test_mass_kg": 0.2, "drop_height_mm": 70},
    {"code": "IK02", "energy_joules": 0.2,  "test_mass_kg": 0.2, "drop_height_mm": 100},
    {"code": "IK03", "energy_joules": 0.35, "test_mass_kg": 0.2, "drop_height_mm": 175},
    {"code": "IK04", "energy_joules": 0.5,  "test_mass_kg": 0.2, "drop_height_mm": 250},
    {"code": "IK05", "energy_joules": 0.7,  "test_mass_kg": 0.2, "drop_height_mm": 350},
    {"code": "IK06", "energy_joules": 1.0,  "test_mass_kg": 0.5, "drop_height_mm": 200},
    {"code": "IK07", "energy_joules": 2.0,  "test_mass_kg": 0.5, "drop_height_mm": 400},
    {"code": "IK08", "energy_joules": 5.0,  "test_mass_kg": 1.7, "drop_height_mm": 300},
    {"code": "IK09", "energy_joules": 10.0, "test_mass_kg": 5.0, "drop_height_mm": 200},
    {"code": "IK10", "energy_joules": 20.0, "test_mass_kg": 5.0, "drop_height_mm": 400}
  ],
  "minimum_per_application": [
    {"context": "Indoor consumer unit (Part 3 DBO)",        "ip_min": "IP2XC", "ik_min": "IK07", "reference": "IEC 61439-3 Clause 8"},
    {"context": "Indoor commercial sub-DB (Part 3 DBO)",    "ip_min": "IP2XC", "ik_min": "IK07", "reference": "IEC 61439-3 Clause 8"},
    {"context": "Indoor commercial main switchboard (Part 2)", "ip_min": "IP2X", "ik_min": "IK07", "reference": "IEC 61439-2 Clause 8"},
    {"context": "Indoor MCC (Part 2)",                      "ip_min": "IP30",  "ik_min": "IK08", "reference": "IEC 61439-2 Clause 8 + project requirements"},
    {"context": "Construction site (Part 4 ACS)",           "ip_min": "IP44",  "ik_min": "IK08", "reference": "IEC 61439-4 Clause 8 (mandatory)"},
    {"context": "Outdoor DNO kiosk (Part 5 PENDA)",         "ip_min": "IP44",  "ik_min": "IK10", "reference": "IEC 61439-5 Clause 8"},
    {"context": "Outdoor EV charging post (Part 7-2)",       "ip_min": "IP54",  "ik_min": "IK10", "reference": "IEC 61439-7-2 Clause 8"},
    {"context": "Marina berth supply (Part 7-1)",           "ip_min": "IP44",  "ik_min": "IK10", "reference": "IEC 61439-7-1 Clause 8"},
    {"context": "Rooftop PV combiner (Part 7-4)",           "ip_min": "IP65",  "ik_min": "IK08", "reference": "IEC 61439-7-4 Clause 8"},
    {"context": "Vertical riser BTS (Part 6)",              "ip_min": "IP54",  "ik_min": "IK08", "reference": "IEC 61439-6 Clause 8"},
    {"context": "Bathroom-zone consumer unit",              "ip_min": "IP44 in Zone 2", "ik_min": "IK07", "reference": "IEC 60364-7-701 (location-dependent)"}
  ],
  "common_underspecifications": [
    "Specifying 'IP30' when finger-safe is required — IP30 protects against 2.5 mm objects but is NOT finger-safe; specify IP3XC or IP2XC",
    "Specifying IK07 for outdoor public locations — IK10 is the appropriate vandal-resistance rating",
    "Omitting the IK rating entirely on construction site (ACS) assemblies — IK08 is mandatory under Part 4",
    "Confusing IP65 (water jets) with IP67 (immersion) — IP67 does NOT necessarily satisfy IP65 (no dust-tightness guaranteed)"
  ]
}
```

- [ ] **Step 2: Validate**

Run: `python3 -c "import json; json.load(open('shared/standards/electrical/IEC61439/ip-ik-ratings.json'))" && echo OK`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add shared/standards/electrical/IEC61439/ip-ik-ratings.json
git commit -m "feat: IEC61439 ip-ik-ratings.json — IP/IK codes and per-application minima"
```

---

## Task 13: Create temperature-rise.json (cross-cutting topic)

**Files:**
- Create: `shared/standards/electrical/IEC61439/temperature-rise.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "IEC 61439 — Temperature Rise",
  "_iec_part": "1 (Annex E + Table 6); referenced by all parts",
  "_version": "1.0.0",
  "_note": "Temperature rise verification ensures that internal components do not exceed their conventional limits at rated load. Verification by test (Clause 10.10) or calculation (Annex E).",
  "conventional_temperature_rise_limits": {
    "_reference": "IEC 61439-1:2020 Table 6",
    "_ambient_assumed_C": 35,
    "_24h_average_max_ambient_C": 35,
    "_peak_ambient_C": 40,
    "rows": [
      {"item": "Terminals for external insulated conductors",       "max_rise_K": 70,  "note": "When connecting to 70 °C-insulated cable. Reduces to 55 K for 60 °C-rated cable."},
      {"item": "Bare conductors (busbars) — connections only",      "max_rise_K": 105, "note": "Where in contact only with bare conductors. Otherwise per next row."},
      {"item": "Busbars — temperature rise of metal",               "max_rise_K": 105, "note": "For copper or aluminium busbars under normal service."},
      {"item": "Manual operation handles — metal",                  "max_rise_K": 15,  "note": "Operator-touchable surface."},
      {"item": "Manual operation handles — insulating material",    "max_rise_K": 25,  "note": "Operator-touchable surface."},
      {"item": "Accessible enclosure surface — metal",              "max_rise_K": 30,  "note": "Operator-touchable surface (back-of-hand contact)."},
      {"item": "Accessible enclosure surface — insulating",         "max_rise_K": 40,  "note": "Operator-touchable surface."},
      {"item": "Built-in components (per their own data)",          "max_rise_K": null,"note": "Use the device manufacturer's rated temperature rise (e.g. 40 K for MCCB terminals at rated current)."}
    ]
  },
  "ambient_correction": {
    "_note": "If the actual ambient differs from 35 °C 24-h average, derate the rated current using factor Kt = sqrt((max_rise + 35 − actual_24h_ambient) / max_rise). For 70 K terminal rise and 45 °C ambient: Kt = sqrt((70 + 35 − 45)/70) = sqrt(60/70) = 0.926. Apply this to In.",
    "example": "Assembly rated In = 1000 A at 35 °C ambient. Installation at 45 °C ambient: derated In = 1000 × 0.926 = 926 A."
  },
  "rated_diversity_factor_RDF": {
    "_reference": "IEC 61439-1:2020 Clause 5.4 + Annex E.5",
    "_note": "Multiplier applied to In to reflect that not all functional units operate at rated current simultaneously. Specified by the designer; verified by the OEM. Default values:",
    "defaults": [
      {"outgoing_circuits_count": "2 or 3",  "RDF": 0.90},
      {"outgoing_circuits_count": "4 or 5",  "RDF": 0.80},
      {"outgoing_circuits_count": "6 to 9",  "RDF": 0.70},
      {"outgoing_circuits_count": "10 and above (incl. continuous duty)", "RDF": 0.60}
    ],
    "_caveat": "RDF does not apply to assemblies whose loads are inherently continuous (data centre, industrial process). Specify RDF = 1.0 for those."
  },
  "annex_e_calculation_overview": [
    "Step 1: Determine assembly enclosure surface area and effective heat-dissipation area.",
    "Step 2: Calculate total power dissipation = Σ (I² · R) over all functional units, multiplied by RDF.",
    "Step 3: Estimate internal temperature rise above ambient using effective dissipation area and enclosure k-factor (per Annex E.6 or test data).",
    "Step 4: Verify that no internal component sees a rise exceeding the limits in Table 6 above.",
    "Step 5: If verification fails, increase ventilation, derate In, or move to a larger enclosure."
  ],
  "solar_gain_correction": {
    "_reference": "IEC 61439-1:2020 Annex E.5 (outdoor assemblies)",
    "_note": "Outdoor enclosures absorb solar radiation; add 15–25 K to internal ambient depending on enclosure colour and orientation. Light grey/white reduces gain by ~40% vs dark colours.",
    "typical_uplift_K": {"light_colour": 15, "medium": 20, "dark": 25}
  }
}
```

- [ ] **Step 2: Validate**

Run: `python3 -c "import json; json.load(open('shared/standards/electrical/IEC61439/temperature-rise.json'))" && echo OK`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add shared/standards/electrical/IEC61439/temperature-rise.json
git commit -m "feat: IEC61439 temperature-rise.json — Annex E limits, RDF, ambient and solar correction"
```

---

## Task 14: Create short-circuit-withstand.json (cross-cutting topic)

**Files:**
- Create: `shared/standards/electrical/IEC61439/short-circuit-withstand.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "IEC 61439 — Short-Circuit Withstand",
  "_iec_part": "1 (Annex P); referenced by all parts",
  "_version": "1.0.0",
  "_note": "Three rated short-circuit characteristics. Designer specifies which applies. OEM verifies by test or Annex P calculation.",
  "rated_characteristics": [
    {
      "symbol": "Icw",
      "name": "Rated short-time withstand current",
      "unit": "kA rms (with associated time, typically 1 s or 3 s)",
      "iec_ref": "IEC 61439-1 Clause 5.3.6",
      "description": "RMS short-circuit current the assembly can carry for a stated duration without damage. Used where the upstream protective device has a delayed trip (selectivity).",
      "typical_values_1s": [10, 15, 25, 36, 50, 65, 80, 100, 150, 200],
      "specify_when": "Assembly is selectively coordinated with upstream protection AND that protection has a defined short-time delay band."
    },
    {
      "symbol": "Ipk",
      "name": "Rated peak withstand current",
      "unit": "kA peak",
      "iec_ref": "IEC 61439-1 Clause 5.3.5",
      "description": "Peak-instantaneous current the assembly must withstand. Required alongside Icw. Ratio Ipk/Icw governed by the n-factor (depends on power factor).",
      "n_factor_table": [
        {"Icw_rms_kA_range": "≤ 5",     "power_factor": 0.7,  "n_ratio_Ipk_Icw": 1.5},
        {"Icw_rms_kA_range": "5 to 10",  "power_factor": 0.5,  "n_ratio_Ipk_Icw": 1.7},
        {"Icw_rms_kA_range": "10 to 20", "power_factor": 0.3,  "n_ratio_Ipk_Icw": 2.0},
        {"Icw_rms_kA_range": "20 to 50", "power_factor": 0.25, "n_ratio_Ipk_Icw": 2.1},
        {"Icw_rms_kA_range": "> 50",     "power_factor": 0.2,  "n_ratio_Ipk_Icw": 2.2}
      ],
      "specify_when": "Always specified together with Icw."
    },
    {
      "symbol": "Icc",
      "name": "Rated conditional short-circuit current",
      "unit": "kA prospective (rms)",
      "iec_ref": "IEC 61439-1 Clause 5.3.7",
      "description": "Prospective fault current at the assembly's incoming terminals when the assembly relies on an upstream current-limiting device (fuse or current-limiting MCCB) to constrain let-through energy and peak.",
      "typical_values": [25, 36, 50, 70, 100],
      "specify_when": "Domestic consumer units (with upstream BS88 service cutout) and other DBO assemblies where Icw alone is not sufficient. Annotate the specified upstream device.",
      "linked_upstream_device_required": true
    }
  ],
  "coordination_with_upstream_protection": {
    "selectivity_rule": "For full selectivity, the upstream device's I²t let-through (at the assembly's Icw_kA × the agreed time) must be less than the assembly's Icw²·t energy capability.",
    "current_limiting_rule": "Where the assembly is rated Icc (conditional), the upstream current-limiting device must let through less than the assembly's tested let-through value at the prospective fault current."
  },
  "annex_p_calculation_overview": [
    "Step 1: Determine prospective short-circuit current at assembly incoming terminals from upstream impedance.",
    "Step 2: Compute Ipk = n × Icw (n from table above for the system power factor).",
    "Step 3: Verify electrodynamic force F = K · Ipk² · s/d on busbars and supports (K depends on geometry, s is centre-to-centre distance, d is span between supports).",
    "Step 4: Verify thermal stress I²t against busbar k²·S² (k = 226 for Cu @ 20°C → 250°C, 148 for Al).",
    "Step 5: Verify joint torquing and support spacing per the OEM's verified design.",
    "Step 6: Apply 0.95 safety margin per Clause 10.11.5.4 of IEC 61439-1."
  ],
  "common_design_errors": [
    "Specifying only Icw without Ipk — peak is needed for force verification",
    "Using Icc rating without specifying the upstream current-limiting device — Icc is meaningless without the linked device",
    "Assuming Icw = Icc — Icw is the assembly's own withstand; Icc relies on upstream limiting",
    "Failing to coordinate Icw time with upstream protective device's selectivity delay"
  ]
}
```

- [ ] **Step 2: Validate**

Run: `python3 -c "import json; json.load(open('shared/standards/electrical/IEC61439/short-circuit-withstand.json'))" && echo OK`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add shared/standards/electrical/IEC61439/short-circuit-withstand.json
git commit -m "feat: IEC61439 short-circuit-withstand.json — Icw, Ipk, Icc with n-factor and Annex P"
```

---

## Task 15: Create internal-arc-classification.json (cross-cutting topic)

**Files:**
- Create: `shared/standards/electrical/IEC61439/internal-arc-classification.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "IEC 61439 — Internal Arc Classification (IAC)",
  "_iec_part": "Primary: IEC TR 61641 (IAC test method); applied via IEC 61439-2 Clauses 8.101 and 9.103; cross-referenced from Parts 3 and 5",
  "_version": "1.0.0",
  "_note": "IAC classifies an assembly's behaviour during an internal arc fault. Voluntary in many jurisdictions but increasingly mandatory for high-availability and high-arc-flash applications.",
  "iac_protection_levels": [
    {
      "code": "A",
      "name": "Person protection — restricted access (authorised personnel only)",
      "scope": "Door closed; arc cannot escape through enclosure openings rated for closed-door operation.",
      "applies_to": "Plant rooms, restricted-access industrial",
      "test_criteria": [
        "No flame or hot gas escape through door/cover",
        "Indicators (cotton flag) at 100–300 mm from accessible surfaces show no ignition",
        "Door/cover does not detach",
        "Earthing path remains continuous"
      ]
    },
    {
      "code": "B",
      "name": "Person protection — general access (laypersons)",
      "scope": "All access conditions including operator working with cover removed (where rated for operation in that state).",
      "applies_to": "Public-accessible, hospital-corridor LV boards",
      "test_criteria": [
        "All Class A criteria, plus:",
        "Specified accessible surfaces show no ignition with cover removed where applicable"
      ]
    },
    {
      "code": "C",
      "name": "Installer protection — during installation/maintenance",
      "scope": "Protection during connecting and disconnecting of conductors.",
      "applies_to": "Industrial / commercial installations where electrician works on the assembly while energised",
      "test_criteria": [
        "Worker positions assumed during installation are not ignited"
      ]
    },
    {
      "code": "D",
      "name": "Live work — arc-rated under direct intervention",
      "scope": "Highest level — protection during direct live work inside the enclosure.",
      "applies_to": "Critical national infrastructure, defense, certain process industries",
      "test_criteria": [
        "All lower-class criteria plus arc-rated viewports/PPE-compatible interface"
      ]
    }
  ],
  "accessibility_types": [
    {"code": "F", "meaning": "Front access — door/cover at the front face"},
    {"code": "L", "meaning": "Lateral (side) access"},
    {"code": "R", "meaning": "Rear access"},
    {"code": "FL", "meaning": "Front + lateral"},
    {"code": "FLR", "meaning": "All sides — typical free-standing"}
  ],
  "test_conditions": {
    "test_current": "Equal to the assembly's rated Icw",
    "test_duration_s": [0.1, 0.3, 0.5, 1.0],
    "atmosphere": "Indoor reference (per IEC TR 61641)",
    "indicators": "Black cotton flag, white cotton flag, vertical-grid indicators at standardised distances"
  },
  "specifying_iac": {
    "template": "Specify as: IAC <classification> <accessibility> Icw <kA> / <time> s. Example: IAC AB FL 50 kA / 0.5 s.",
    "designer_responsibility": [
      "Determine which protection class applies (A for restricted, B for general access, C for installer)",
      "Determine accessibility — F only is common in floor-standing wall-mounted boards; FLR for centre-of-room free-standing",
      "Match Icw test current to the assembly's expected fault level",
      "Specify the test duration aligned to upstream protection clearing time (typically 0.5 s for ACB-protected mains)"
    ]
  },
  "common_design_errors": [
    "Specifying IAC without accessibility type — the test result is meaningless without it",
    "Using a single IAC class for a multi-compartment assembly — different compartments may need different classes",
    "Mismatching IAC test duration with upstream relay setting — if upstream is set to clear in 0.3 s, an IAC at 0.5 s is over-spec but a 0.1 s IAC is under-spec"
  ]
}
```

- [ ] **Step 2: Validate**

Run: `python3 -c "import json; json.load(open('shared/standards/electrical/IEC61439/internal-arc-classification.json'))" && echo OK`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add shared/standards/electrical/IEC61439/internal-arc-classification.json
git commit -m "feat: IEC61439 internal-arc-classification.json — IAC A/B/C/D + accessibility F/L/R"
```

---

## Task 16: Create busbar-derating.json (cross-cutting topic)

**Files:**
- Create: `shared/standards/electrical/IEC61439/busbar-derating.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "IEC 61439 — Busbar Derating and Fault-Current Force",
  "_iec_part": "1 (Annex E + Annex P)",
  "_version": "1.0.0",
  "_note": "Typical current-carrying capacities and derating factors. These are indicative values per IEC 61439-1 Annex E.6 and reference designs — the OEM's verified data supersedes for any specific assembly.",
  "current_carrying_capacity_copper": {
    "_conductor": "Copper",
    "_reference_ambient_C": 35,
    "_busbar_temperature_C": 90,
    "_orientation": "Vertical, in ventilated enclosure",
    "_note": "Per single rectangular bar. Multi-bar arrangements derated for proximity per derating_for_multiple_bars below.",
    "table_A_per_csa": [
      {"csa_mm2": 100,  "width_x_thickness_mm": "20 × 5",   "rated_A": 281},
      {"csa_mm2": 150,  "width_x_thickness_mm": "30 × 5",   "rated_A": 393},
      {"csa_mm2": 200,  "width_x_thickness_mm": "40 × 5",   "rated_A": 500},
      {"csa_mm2": 250,  "width_x_thickness_mm": "50 × 5",   "rated_A": 595},
      {"csa_mm2": 400,  "width_x_thickness_mm": "80 × 5",   "rated_A": 858},
      {"csa_mm2": 500,  "width_x_thickness_mm": "100 × 5",  "rated_A": 1011},
      {"csa_mm2": 600,  "width_x_thickness_mm": "60 × 10",  "rated_A": 1110},
      {"csa_mm2": 800,  "width_x_thickness_mm": "80 × 10",  "rated_A": 1390},
      {"csa_mm2": 1000, "width_x_thickness_mm": "100 × 10", "rated_A": 1640},
      {"csa_mm2": 1600, "width_x_thickness_mm": "160 × 10", "rated_A": 2370},
      {"csa_mm2": 2000, "width_x_thickness_mm": "200 × 10", "rated_A": 2810}
    ]
  },
  "current_carrying_capacity_aluminium": {
    "_conductor": "Aluminium",
    "_factor_vs_copper": 0.78,
    "_note": "Aluminium busbar carries approximately 78% of an equal-CSA copper busbar's current at the same temperature rise."
  },
  "derating_for_ambient": {
    "_formula": "Kt = sqrt((max_rise_K + 35 − actual_ambient_C) / max_rise_K)",
    "_examples": [
      {"ambient_C": 35, "rise_K": 55, "Kt": 1.0},
      {"ambient_C": 40, "rise_K": 55, "Kt": 0.953},
      {"ambient_C": 45, "rise_K": 55, "Kt": 0.905},
      {"ambient_C": 50, "rise_K": 55, "Kt": 0.853},
      {"ambient_C": 55, "rise_K": 55, "Kt": 0.798}
    ]
  },
  "derating_for_multiple_bars_per_phase": {
    "_note": "Multiple bars per phase (parallel) experience proximity heating. Indicative derating factors:",
    "_factors": [
      {"bars_per_phase": 1, "factor": 1.00},
      {"bars_per_phase": 2, "factor": 0.85},
      {"bars_per_phase": 3, "factor": 0.78},
      {"bars_per_phase": 4, "factor": 0.72}
    ]
  },
  "fault_current_force": {
    "_formula": "F = K · Ipk² · s / d",
    "_units": "F in N/m; Ipk in kA peak; s in m (centre-to-centre between phase conductors); d in m (span between supports)",
    "_constant_K": "K depends on conductor geometry and configuration. For typical 3-phase rectangular busbar with K = 0.173 (per kA² · m / m): F[N/m] = 0.173 · Ipk² · s / d when s and d in m and Ipk in kA peak.",
    "worked_example": {
      "context": "3-phase busbar, Ipk = 100 kA peak, s = 0.15 m, d = 0.5 m",
      "calculation": "F = 0.173 × 100² × 0.15 / 0.5 = 519 N/m",
      "interpretation": "Each busbar experiences ~519 N/m of lateral force during the fault peak. Supports must withstand this; busbar deflection between supports must remain elastic."
    }
  },
  "neutral_and_pe_sizing": {
    "neutral_csa": "Min 50% of phase CSA for In ≤ 1600 A; 100% for harmonic-rich loads (THDi > 15 %). See IEC 60364-5-52 for harmonic derating.",
    "pe_csa":      "Per IEC 60364-5-54 Table 54.1: PE = S phase for S ≤ 16 mm²; PE = 16 mm² for S = 16–35 mm²; PE = S/2 for S > 35 mm². Or as agreed with adiabatic equation k²S² ≥ I²t."
  }
}
```

- [ ] **Step 2: Validate**

Run: `python3 -c "import json; json.load(open('shared/standards/electrical/IEC61439/busbar-derating.json'))" && echo OK`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add shared/standards/electrical/IEC61439/busbar-derating.json
git commit -m "feat: IEC61439 busbar-derating.json — CCC tables, derating, fault-force F=K·Ipk²·s/d"
```

---

## Task 17: Create rated-quantities.json (cross-cutting topic)

**Files:**
- Create: `shared/standards/electrical/IEC61439/rated-quantities.json`

- [ ] **Step 1: Write the file**

```json
{
  "_title": "IEC 61439 — Rated Quantities Quick Reference",
  "_iec_part": "1 (Clause 5)",
  "_version": "1.0.0",
  "_note": "All rated quantities the designer must specify on the assembly schedule. Standard-preferred values per IEC 61439-1 Clause 5.",
  "quantities": {
    "Ue": {
      "symbol": "Ue",
      "name": "Rated operational voltage",
      "unit": "V (a.c. rms) or V (d.c.)",
      "iec_ref": "IEC 61439-1 Clause 5.1",
      "definition": "Voltage between phases (a.c.) or between poles (d.c.) at which the assembly is designed to operate continuously.",
      "preferred_values_AC_V": [230, 400, 415, 480, 525, 600, 690, 1000],
      "preferred_values_DC_V": [110, 220, 440, 750, 1000, 1500],
      "typical_LV_building": "230 V (single-phase), 400 V (three-phase)"
    },
    "Ui": {
      "symbol": "Ui",
      "name": "Rated insulation voltage",
      "unit": "V rms",
      "iec_ref": "IEC 61439-1 Clause 5.2.2",
      "definition": "Voltage to which the assembly's dielectric strength is referred. Must be ≥ Ue.",
      "preferred_values_V": [500, 690, 1000],
      "typical_LV_building": "1000 V"
    },
    "Uimp": {
      "symbol": "Uimp",
      "name": "Rated impulse withstand voltage",
      "unit": "kV (1.2/50 µs impulse, peak)",
      "iec_ref": "IEC 61439-1 Clause 5.2.3",
      "definition": "Peak value of an impulse voltage that the assembly's insulation can withstand under specified conditions. Selected based on overvoltage category.",
      "preferred_values_kV": [1.5, 2.5, 4, 6, 8, 12],
      "overvoltage_category_to_Uimp_for_400V": {
        "II":  "2.5 kV (appliances and final circuits)",
        "III": "4 kV (distribution circuits within installation)",
        "IV":  "6 kV (origin of installation — meter, main switchgear)"
      },
      "typical_LV_building_for_400V_MSB": "6 kV (Cat IV)"
    },
    "In": {
      "symbol": "In",
      "name": "Rated current of the assembly",
      "unit": "A",
      "iec_ref": "IEC 61439-1 Clause 5.3.1",
      "definition": "Maximum sum of currents from incoming circuits, declared by the manufacturer. Used with RDF for verification.",
      "preferred_values_A": [16, 32, 63, 100, 125, 160, 200, 250, 400, 630, 800, 1000, 1250, 1600, 2000, 2500, 3200, 4000, 5000, 6300, 8000]
    },
    "Inc": {
      "symbol": "Inc",
      "name": "Rated current of a circuit of the assembly",
      "unit": "A",
      "iec_ref": "IEC 61439-1 Clause 5.3.2",
      "definition": "Maximum continuous current that an individual outgoing circuit can carry.",
      "preferred_values_A": [6, 10, 13, 16, 20, 25, 32, 40, 50, 63, 80, 100, 125, 160, 200, 250, 400, 630]
    },
    "Icw": {
      "symbol": "Icw",
      "name": "Rated short-time withstand current",
      "unit": "kA rms (for 1 s typical)",
      "iec_ref": "IEC 61439-1 Clause 5.3.6",
      "definition": "RMS short-circuit current the assembly can carry for a stated duration. See short-circuit-withstand.json for full treatment.",
      "preferred_values_kA": [10, 15, 25, 36, 50, 65, 80, 100]
    },
    "Ipk": {
      "symbol": "Ipk",
      "name": "Rated peak withstand current",
      "unit": "kA peak",
      "iec_ref": "IEC 61439-1 Clause 5.3.5",
      "definition": "Peak instantaneous current the assembly must withstand. Ratio Ipk/Icw via n-factor.",
      "preferred_values_kA": [17, 30, 52, 75, 105, 143, 176, 220]
    },
    "Icc": {
      "symbol": "Icc",
      "name": "Rated conditional short-circuit current",
      "unit": "kA prospective (rms)",
      "iec_ref": "IEC 61439-1 Clause 5.3.7",
      "definition": "Prospective fault current when withstand relies on an upstream current-limiting device.",
      "preferred_values_kA": [25, 36, 50, 70, 100]
    },
    "fn": {
      "symbol": "fn",
      "name": "Rated frequency",
      "unit": "Hz",
      "iec_ref": "IEC 61439-1 Clause 5.5",
      "definition": "Frequency at which the assembly is designed to operate.",
      "preferred_values_Hz": [50, 60],
      "typical": "50 Hz in Europe, Africa, most of Asia; 60 Hz in North/South America and parts of Asia"
    },
    "pollution_degree": {
      "symbol": "PD",
      "name": "Pollution degree",
      "unit": "dimensionless (1–4)",
      "iec_ref": "IEC 61439-1 Clause 5.6",
      "definition": "Severity of environmental contamination at clearances and creepages.",
      "values": {
        "1": "No pollution / dry, clean environment (sealed)",
        "2": "Normal indoor (typical office, plant room)",
        "3": "Industrial — conductive pollution may be expected (typical industrial floor)",
        "4": "Continuous conductive pollution by dust, rain — outdoor"
      },
      "typical_LV_building_indoor": "2",
      "typical_LV_outdoor": "3 (sheltered) or 4 (fully exposed)"
    },
    "overvoltage_category": {
      "symbol": "OVC",
      "name": "Overvoltage category",
      "unit": "Roman numeral (I–IV)",
      "iec_ref": "IEC 60664-1; referenced from IEC 61439-1 Clause 5.2.3",
      "definition": "Determines required Uimp based on the assembly's position in the installation.",
      "values": {
        "I":   "Equipment connected to circuits with overvoltage control (signal-only, separated by SPDs at every interface)",
        "II":  "Appliances and final circuits — fed from fixed installation",
        "III": "Distribution circuits — within the installation (DBs, mains)",
        "IV":  "Origin of the installation — meter, main intake, main switchgear, things upstream of the consumer unit"
      },
      "typical_LV_building": "IV at supply intake / MSB; III at sub-DB; II at final circuits"
    }
  }
}
```

- [ ] **Step 2: Validate**

Run: `python3 -c "import json; json.load(open('shared/standards/electrical/IEC61439/rated-quantities.json'))" && echo OK`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add shared/standards/electrical/IEC61439/rated-quantities.json
git commit -m "feat: IEC61439 rated-quantities.json — Ue, Ui, Uimp, In, Icw, Ipk, fn quick reference"
```

---

## Task 18: Create amendments-summary.md

**Files:**
- Create: `shared/standards/electrical/IEC61439/amendments-summary.md`

- [ ] **Step 1: Write the file**

````markdown
# IEC 61439 — Amendments and Edition History

IEC 61439 superseded IEC 60439 in 2009 with a fundamentally restructured approach. The standard has continued to evolve through 2nd-edition releases per part and addition of new Part 7 sub-parts.

---

## Edition history (per part)

| Part | First edition | Current edition | Major changes |
|---|---|---|---|
| 61439-1 (General) | 2009 | 2020 (3rd ed of -1) | Verification trio formalised, terminology aligned |
| 61439-2 (PSC-Assemblies) | 2009 | 2020 (2nd ed) | Forms unchanged; Annex 101 expanded |
| 61439-3 (DBO) | 2012 | 2012 (1st ed) | Defines DBO concept distinctly from PSC |
| 61439-4 (ACS) | 2012 | 2012 (1st ed) | IK ≥ 08 mandatory; RCD requirements aligned with IEC 60364-7-704 |
| 61439-5 (PENDA) | 2010 | 2014 (2nd ed) | Vandal-resistance and solar gain criteria refined |
| 61439-6 (BTS) | 2012 | 2012 (1st ed) | Replaces IEC 60439-6 |
| 61439-7-1 (Marinas/Camping) | 2014 | 2014 (1st ed) | New scope, was IEC 60439-4 (pre-2014) |
| 61439-7-2 (EV Charging) | 2018 | 2018 (1st ed) | Type B RCD requirements, mode-specific clauses |
| 61439-7-3 (Safety services) | 2018 | 2018 (1st ed) | Source-changeover classes, monitoring |
| 61439-7-4 (PV) | 2022 | 2022 (1st ed) | DC-side specifics, AFCI provisions |
| 61439-7-5 (Transformer-incorporated) | 2022 | 2022 (1st ed) | Medical IT and isolation transformer assemblies |

---

## Key changes that affect designers

### 2009–2014 — From IEC 60439 to IEC 61439

The withdrawal of IEC 60439 (all parts withdrawn 2014) and replacement by IEC 61439 introduced three changes that designers must internalise:

1. **Verification by test, calculation, or comparison with reference design.** IEC 60439 required type-test certificates; IEC 61439 accepts three equivalent paths. This dramatically lowers the cost of producing verified-to-standard assemblies for low-volume specials.

2. **Original Manufacturer (OM) vs Assembly Manufacturer (AM) responsibility split.** Formerly any "tested" assembly was simply tested by the supplier. IEC 61439 makes explicit that the OM provides the verified design (with type tests, calculations, or reference design certificates); the AM builds individual units within the OM's verified envelope. Many UK panel-builders are AMs licensed by an OM such as ABB or Schneider.

3. **Rated Diversity Factor (RDF).** Replaces the old assumption that all functional units operate at full rating simultaneously. Designer specifies the RDF (or accepts the OEM's default), and the OEM verifies temperature rise under that condition rather than 100% load.

### 2018 — Part 7-2 EV charging

The introduction of Part 7-2 reflects the rapid build-out of EV infrastructure. Two requirements affect MEP design:

- **Type B RCD (or equivalent DC-leakage protection).** Required where DC leakage > 6 mA is possible. Standard for Mode 4 fast chargers; required for unmanaged Mode 3 unless the EVSE itself has Type A + 6 mA DC.
- **Cable rated at 100% of EVSE rated current.** No diversity factor applies to the cable to the EVSE. A 32 A EVSE requires a 32 A continuous-rated cable regardless of load management.

### 2020 — Part 1 third edition

The 2020 third edition of Part 1 introduced no fundamental rule changes but consolidated 11 years of amendments. Practical impact:

- Annex E (temperature rise calculation) is more usable for design engineers without OEM-specific data.
- Annex P (short-circuit verification) clarifies the calculation path for non-standard assemblies.
- The terminology around assembly types (PSC vs DBO vs ACS vs PENDA) is rigorously distinguished.

### 2022 — Parts 7-4 (PV) and 7-5 (Transformer-incorporated)

These two new Part 7 sub-parts reflect modern application needs:

- **Part 7-4 (PV).** Codifies the DC-side requirements (1500 V Ue, DC-rated isolators, SPD at DC input). Some jurisdictions (US NEC 690) require AFCI in addition.
- **Part 7-5 (Transformer-incorporated).** Used heavily in medical Group 2 IT panels and in 110 V CTE reduced-voltage power tools supply.

---

## Withdrawn IEC 60439 — what to do with existing equipment

Assemblies installed under IEC 60439 before 2014 remain valid for their service life. They were verified to a different (test-only) standard and cannot be retro-claimed as IEC 61439-compliant.

For new designs: never reference IEC 60439. For extensions or modifications to existing IEC 60439 boards: extend per the original verification chain, document the boundaries, and consider whether a partial replacement to IEC 61439 is more cost-effective than continuing to verify against a withdrawn standard.

---

## National adoption status

| National code | Country | Relationship to IEC 61439 |
|---|---|---|
| BS EN 61439   | United Kingdom | Direct CENELEC adoption |
| DIN EN 61439  | Germany | Direct adoption |
| NF EN 61439   | France | Direct adoption |
| SS-EN 61439   | Sweden | Direct adoption |
| AS/NZS 61439  | Australia / New Zealand | Direct adoption with limited national variants |
| IS/IEC 61439  | India | Direct adoption |
| GB/T 7251     | China | Substantially aligned, with national variations on form codes |
| UL 891 / UL 67 | United States | Different standards family — NOT aligned with IEC 61439 |

A skill targeting a region with direct adoption can cite the national designation in the drawing legend alongside the IEC reference — both are correct.
````

- [ ] **Step 2: Commit**

```bash
git add shared/standards/electrical/IEC61439/amendments-summary.md
git commit -m "docs: IEC61439 amendments summary — edition history and key changes"
```

---

## Task 19: Create design-vs-manufacture.md

**Files:**
- Create: `shared/standards/electrical/IEC61439/design-vs-manufacture.md`

- [ ] **Step 1: Write the file**

````markdown
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
````

- [ ] **Step 2: Commit**

```bash
git add shared/standards/electrical/IEC61439/design-vs-manufacture.md
git commit -m "docs: IEC61439 design-vs-manufacture — OM/AM/designer responsibility split"
```

---

## Task 20: Create compliance-checklist.md

**Files:**
- Create: `shared/standards/electrical/IEC61439/compliance-checklist.md`

- [ ] **Step 1: Write the file**

````markdown
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
````

- [ ] **Step 2: Commit**

```bash
git add shared/standards/electrical/IEC61439/compliance-checklist.md
git commit -m "docs: IEC61439 compliance checklist — designer-side schedule fields per part"
```

---

## Task 21: Create terminology.md

**Files:**
- Create: `shared/standards/electrical/IEC61439/terminology.md`

- [ ] **Step 1: Write the file**

````markdown
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
````

- [ ] **Step 2: Commit**

```bash
git add shared/standards/electrical/IEC61439/terminology.md
git commit -m "docs: IEC61439 terminology — critical-distinction glossary"
```

---

## Task 22: Create worked-examples.md

**Files:**
- Create: `shared/standards/electrical/IEC61439/worked-examples.md`

- [ ] **Step 1: Write the file**

````markdown
# IEC 61439 — Worked Examples

Four worked examples illustrating how designers apply IEC 61439. Each example walks the schedule entry → verification chain → handover documentation.

---

## Example 1 — Form 3b PSC-Assembly verification chain

**Project:** 8-storey commercial office. Main LV switchboard fed from a 1250 kVA, 11 kV / 415 V transformer.

### Step 1 — Designer specifies

| Field | Value | Source |
|---|---|---|
| Assembly designation | MSB-01 per IEC 61439-2:2020 | designer |
| Form | 3b | designer choice (single-circuit maintenance with rest live) |
| Ue | 400 V (3φ + N + PE) | DNO supply |
| Ui | 1000 V | per Part 1 |
| Uimp | 6 kV (overvoltage category IV) | designer (MSB is OVC IV) |
| In | 2500 A | designer's load schedule |
| Icw / time | 50 kA / 1 s | calculated from transformer Z = 6 %, Sn = 1250 kVA: Isc = 1250 × 1000 / (√3 × 415 × 0.06) = 29 kA. Designer rounds up to standard 50 kA / 1 s. |
| Ipk | 105 kA peak | from Icw via n-factor at PF 0.25 → n = 2.1 → Ipk = 2.1 × 50 = 105 kA |
| fn | 50 Hz | UK |
| IP / IK | IP2X (front) / IP30 (enclosure) / IK08 | indoor plant room |
| IAC | AB FL 50 kA / 0.5 s | designer (occupied building, front + lateral access) |
| RDF | 0.85 | designer's diversity assessment |

### Step 2 — OEM verification path

OEM (Schneider, Prisma iPM) presents:
- Type-test certificate for the Prisma iPM Form 3b at 50 kA / 1 s, 2500 A.
- IAC test certificate at 50 kA / 0.5 s.
- Annex E temperature-rise calculation showing the specific outgoer mix passes at RDF 0.85.
- Annex D bounding comparison showing this build (2500 A, 50 kA, RDF 0.85, IAC AB FL) falls within the verified envelope.

### Step 3 — AM build

Licensed UK panel-builder constructs the assembly using Prisma iPM verified design. Provides routine-verification test records (insulation, polarity, functional) at handover.

### Step 4 — Handover documentation pack

- OEM verification declaration (signed by Schneider)
- Annex E calculation report (Schneider)
- Annex D bounding comparison (Schneider)
- Type-test certificate summary (Schneider)
- IAC test certificate (Schneider)
- As-built single line, GA, terminal schedule (AM)
- Routine test records (AM)
- BSRIA BG 29 O&M (AM, building O&M consultant)

---

## Example 2 — IAC accessibility for an MCC

**Project:** Industrial MCC for a sewage treatment plant. Maintenance personnel are skilled. The MCC sits in a dedicated electrical room.

### Designer's IAC decision

| Question | Answer | Implication |
|---|---|---|
| Is the room accessible to the public? | No | Class A acceptable (skilled persons only) |
| What direction can the OEM access? | Front only (back is against a wall) | Accessibility type F |
| What is the prospective fault current? | 36 kA | Icw test current = 36 kA |
| What is the upstream protection clearing time? | ACB with short-time delay 0.3 s | IAC test duration ≥ 0.3 s, round to 0.5 s |

**Result:** Specify IAC AF 36 kA / 0.5 s.

### What this means in practice

The OEM verifies that during a 36 kA fault for up to 0.5 s, with the door closed:
- No flame or hot gas escapes through the door
- No ignition occurs at the front of the MCC
- The door does not detach
- Earthing remains continuous

If the room were occupied by ordinary persons during operation (a public-accessible substation room), Class B would be required. If access were possible from sides or rear, accessibility would be FL, FR, or FLR.

---

## Example 3 — Busbar derating for a 4000 A board at 45 °C ambient

**Project:** Data centre MSB rated 4000 A at standard 35 °C 24-h average ambient. Installation in a plant room where ambient runs at 45 °C 24-h average.

### Step 1 — Ambient correction factor

From `temperature-rise.json` ambient correction formula with max rise 55 K for busbars:
```
Kt = sqrt((55 + 35 − 45) / 55)
   = sqrt(45 / 55)
   = sqrt(0.818)
   = 0.905
```

### Step 2 — Derated In

Derated In = 4000 × 0.905 = **3620 A** at 45 °C ambient.

### Step 3 — Designer's options

Option A: Accept derating. Specify In = 4000 A on the assembly but apply a 3620 A operational limit in the BMS. Cheap; constrains future load growth.

Option B: Specify In = 4400 A at 45 °C ambient. OEM upsizes the busbar to compensate. Higher cost; preserves headroom.

Option C: Improve ambient (ventilation / cooling) so 35 °C 24-h average is achieved. Capex on HVAC; preserves the standard rating.

### Step 4 — Verification documentation

Whichever option is chosen, the OEM provides an Annex E calculation showing the busbar's temperature rise at the design ambient remains ≤ 55 K above ambient (90 °C absolute peak). If Option B is chosen, the OEM may need a reference-design certificate covering 4400 A or a fresh test.

---

## Example 4 — Icw coordination with upstream MCCB

**Project:** Sub-DB on the 8th floor of the office building from Example 1. Fed from the main switchboard at the building base via 50 m of 3-phase busduct.

### Step 1 — Fault current at sub-DB

From PSCC calculation chain (per IEC 60364-4-43): the fault current at the 8th-floor sub-DB drops to **18 kA prospective** due to busduct impedance.

### Step 2 — Designer's selectivity strategy

Upstream MCCB at the MSB end of the busduct is set with short-time delay (STD) 0.2 s and a magnetic instantaneous threshold at 30 kA (above the 18 kA prospective at the sub-DB).

Sub-DB MCCB at the 8th floor must clear faults at 18 kA without waiting for the upstream STD.

### Step 3 — Sub-DB Icw specification

Designer specifies sub-DB Icw = 18 kA / 0.2 s (matching the upstream STD time). This guarantees the sub-DB withstands 18 kA for the duration that selectivity requires.

If the sub-DB used a fuse-protected feeder instead, Icc would apply: the designer would specify Icc 18 kA conditional on the upstream BS88 cut-out, and the OEM's verification would document the fuse's let-through.

### Step 4 — Common error to avoid

A naive specification of "Icw = 18 kA / 1 s" would force the OEM to verify the sub-DB at 18 kA for a full second. This is more expensive than necessary (because the upstream STD is only 0.2 s) and may push the assembly into a larger frame size. Specify Icw matched to the actual selectivity delay.

---

## Cross-references across these examples

| Topic | Used in Example | Layer file |
|---|---|---|
| Form 3b | Example 1 | `form-separations.json` (FORM_3B), `part2-psc-assemblies.json` (PSC_ASSEMBLY_FORM_3B) |
| IAC classification | Example 2 | `internal-arc-classification.json` |
| Busbar derating | Example 3 | `busbar-derating.json`, `temperature-rise.json` |
| Icw coordination | Example 4 | `short-circuit-withstand.json` |
| n-factor for Ipk | Example 1 | `short-circuit-withstand.json` (rated_characteristics.Ipk.n_factor_table) |
| RDF | Example 1 | `temperature-rise.json` (rated_diversity_factor_RDF) |
| Annex E verification | Examples 1 & 3 | `verification-methods.json` (CALC method), `temperature-rise.json` |
| Annex D bounding | Example 1 | `verification-methods.json` (REFERENCE method) |
````

- [ ] **Step 2: Commit**

```bash
git add shared/standards/electrical/IEC61439/worked-examples.md
git commit -m "docs: IEC61439 worked examples — Form 3b, IAC, busbar derating, Icw coordination"
```

---

## Task 23: Final verification

**Files:**
- Verify: full `shared/standards/electrical/IEC61439/` directory

- [ ] **Step 1: Verify all 22 files are present**

Run:
```bash
ls -1 shared/standards/electrical/IEC61439/
```
Expected (alphabetical):
```
README.md
amendments-summary.md
busbar-derating.json
compliance-checklist.md
design-vs-manufacture.md
form-separations.json
internal-arc-classification.json
ip-ik-ratings.json
meta.json
part1-general.json
part2-psc-assemblies.json
part3-dbo-assemblies.json
part4-acs-assemblies.json
part5-penda-assemblies.json
part6-busbar-trunking.json
part7-applications.json
rated-quantities.json
short-circuit-withstand.json
temperature-rise.json
terminology.md
verification-methods.json
worked-examples.md
```
(Count = 22 files)

- [ ] **Step 2: Verify all JSON files parse**

Run:
```bash
for f in shared/standards/electrical/IEC61439/*.json; do
  python3 -c "import json; json.load(open('$f'))" && echo "$f OK" || echo "$f FAIL"
done
```
Expected: every line ends with `OK`.

- [ ] **Step 3: Verify all part files conform to assembly schema**

Run:
```bash
python3 - <<'PY'
import json, glob
req=['assembly_id','iec_ref','iec_part','iec_title','draftsman_id','application_scope','rated_quantities','form_separation','ip_default','ik_default','mandatory_characteristics','verification_clauses','drawn_as','typical_components','application_examples','related_iec_60364','related_bs_7671','usage_notes','related_assemblies']
bad = []
for f in sorted(glob.glob('shared/standards/electrical/IEC61439/part*.json')):
    data = json.load(open(f))
    for a in data['assemblies']:
        missing = [x for x in req if x not in a]
        if missing:
            bad.append((f, a.get('assembly_id','?'), missing))
print('OK' if not bad else 'BAD:'+str(bad))
PY
```
Expected: `OK`

- [ ] **Step 4: Verify every drawn_as reference resolves in IEC 60617 symbol index**

Run:
```bash
python3 - <<'PY'
import json, glob
idx = {s['symbol_id'] for s in json.load(open('shared/standards/electrical/IEC60617/symbol-index.json'))['symbols']}
unknown = []
for f in sorted(glob.glob('shared/standards/electrical/IEC61439/part*.json')):
    data = json.load(open(f))
    for a in data['assemblies']:
        for s in a['drawn_as']:
            if s not in idx:
                unknown.append((f.split('/')[-1], a['assembly_id'], s))
# Also check form-separations.json
fs = json.load(open('shared/standards/electrical/IEC61439/form-separations.json'))
for form in fs['forms']:
    for s in form.get('drawn_as', []):
        if s not in idx:
            unknown.append(('form-separations.json', form['form_code'], s))
print('OK' if not unknown else 'UNKNOWN:'+str(unknown))
PY
```
Expected: `OK`

- [ ] **Step 5: Verify total assembly count**

Run:
```bash
python3 - <<'PY'
import json, glob
total = 0
for f in sorted(glob.glob('shared/standards/electrical/IEC61439/part*.json')):
    data = json.load(open(f))
    n = len(data['assemblies'])
    total += n
    print(f'{f.split("/")[-1]}: {n} assemblies')
print(f'TOTAL: {total}')
PY
```
Expected:
```
part1-general.json: 2 assemblies
part2-psc-assemblies.json: 7 assemblies
part3-dbo-assemblies.json: 2 assemblies
part4-acs-assemblies.json: 2 assemblies
part5-penda-assemblies.json: 2 assemblies
part6-busbar-trunking.json: 2 assemblies
part7-applications.json: 5 assemblies
TOTAL: 22
```

- [ ] **Step 6: Verify form-separations.json covers all 7 Forms**

Run: `python3 -c "import json; data=json.load(open('shared/standards/electrical/IEC61439/form-separations.json')); codes=sorted(f['form_code'] for f in data['forms']); assert codes==['1','2a','2b','3a','3b','4a','4b']; print('OK')"`
Expected: `OK`

- [ ] **Step 7: Final layer-level summary commit (optional — only if uncommitted changes remain)**

Run:
```bash
git status --short
```

If any files remain uncommitted, run:
```bash
git add shared/standards/electrical/IEC61439/
git commit -m "feat: IEC61439 standard layer v1.0.0 complete — 22 files covering 7 parts"
```

- [ ] **Step 8: Verify the final git log**

Run:
```bash
git log --oneline -25
```

Expected (most recent first, after the spec commit `de8958e`):
- (optional final commit)
- docs: IEC61439 worked examples
- docs: IEC61439 terminology
- docs: IEC61439 compliance checklist
- docs: IEC61439 design-vs-manufacture
- docs: IEC61439 amendments summary
- feat: IEC61439 rated-quantities.json
- feat: IEC61439 busbar-derating.json
- feat: IEC61439 internal-arc-classification.json
- feat: IEC61439 short-circuit-withstand.json
- feat: IEC61439 temperature-rise.json
- feat: IEC61439 ip-ik-ratings.json
- feat: IEC61439 verification-methods.json
- feat: IEC61439 form-separations.json
- feat: IEC61439 part7-applications.json
- feat: IEC61439 part6-busbar-trunking.json
- feat: IEC61439 part5-penda-assemblies.json
- feat: IEC61439 part4-acs-assemblies.json
- feat: IEC61439 part3-dbo-assemblies.json
- feat: IEC61439 part2-psc-assemblies.json
- feat: IEC61439 part1-general.json
- docs: rewrite IEC61439 README
- feat: IEC61439 meta.json
- docs: IEC 61439 standard layer design spec (de8958e)

---

## Plan Summary

| Task | File(s) | Assembly count | Commits |
|---|---|---|---|
| 1 | `meta.json` | — | 1 |
| 2 | `README.md` rewrite | — | 1 |
| 3 | `part1-general.json` | 2 | 1 |
| 4 | `part2-psc-assemblies.json` | 7 (all Forms) | 1 |
| 5 | `part3-dbo-assemblies.json` | 2 | 1 |
| 6 | `part4-acs-assemblies.json` | 2 | 1 |
| 7 | `part5-penda-assemblies.json` | 2 | 1 |
| 8 | `part6-busbar-trunking.json` | 2 | 1 |
| 9 | `part7-applications.json` | 5 | 1 |
| 10 | `form-separations.json` | (7 Form entries) | 1 |
| 11 | `verification-methods.json` | — | 1 |
| 12 | `ip-ik-ratings.json` | — | 1 |
| 13 | `temperature-rise.json` | — | 1 |
| 14 | `short-circuit-withstand.json` | — | 1 |
| 15 | `internal-arc-classification.json` | — | 1 |
| 16 | `busbar-derating.json` | — | 1 |
| 17 | `rated-quantities.json` | — | 1 |
| 18 | `amendments-summary.md` | — | 1 |
| 19 | `design-vs-manufacture.md` | — | 1 |
| 20 | `compliance-checklist.md` | — | 1 |
| 21 | `terminology.md` | — | 1 |
| 22 | `worked-examples.md` | — | 1 |
| 23 | Final verification | — | 0–1 |
| **Total** | **22 new/rewritten files** | **22 part-file assembly entries** | **22–23** |
