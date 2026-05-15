# IEC 61439 Standard Layer — Design Spec

**Date:** 2026-05-15
**Status:** Approved
**Scope:** Build the IEC 61439 graphical-engineering standard layer covering low-voltage switchgear and controlgear assemblies. The fourth standards layer after BS 7671, IEC 60364, and IEC 60617.

---

## 1. Goal

Populate `shared/standards/electrical/IEC61439/` with a machine-readable engineering catalogue so that:

1. Any DraftsMan AI skill that produces or validates assemblies (sld, db-layout, panel-schedule, riser, transformer, generator, ups, mcc-implicit, schematic) can look up what an assembly type means, what must be specified, and what IEC clause it traces to.
2. The IEC 60617 symbol layer remains visual-only; this layer carries the engineering soul behind those symbols (one-way `drawn_as` pointer from 61439 → 60617).
3. Compliance with the standard's verification requirements (type test, calculation, or comparison with reference design) is machine-checkable from skill output.

IEC 61439 is fundamentally different from IEC 60617 (which defines what symbols look like) and from IEC 60364 (which defines installation rules). IEC 61439 governs **the assembly itself** — what the physical switchboard, MCC, distribution board, busduct or kiosk must be.

---

## 2. Decisions Made

| Decision | Choice | Rationale |
|---|---|---|
| Parts covered | All 7 parts (1, 2, 3, 4, 5, 6, 7) | Building MEP scope plus utility-side (Part 5) and applications (Part 7). User wants comprehensive coverage; avoids gaps later. |
| Engineering depth | Full content with worked examples | Matches IEC 60364 / BS 7671 layer depth. Skills need actionable rules, not just code lists. |
| Cross-reference to IEC 60617 | One-way `drawn_as` pointer (61439 → 60617) | The engineering layer names its visual representation. Easy maintenance — IEC 60617 doesn't need to know about 61439. |
| File decomposition | Hybrid: part files + cross-cutting topic files | Skills load the topic file (e.g. form-separations) directly without knowing which part it lives in. Each file stays focused (~150–300 lines). |
| File count | ~22 files (2 layer + 7 part + 8 topic + 5 narrative) | Comprehensive coverage with file sizes that don't pressure AI context. |
| Manufacturer data | Excluded | Catalogue values (ABB/Schneider/Siemens/Eaton) live in datasheets, not in the standards layer. Layer carries IEC tabulated rules only. |
| IEC 60439 (predecessor) | Excluded | Withdrawn 2014. New designs use IEC 61439 only. |
| Generated outputs | None | Layer is input-only. No `shared/symbols/electrical/` generation (that's IEC 60617's job). |

---

## 3. Current State

| File | Status |
|---|---|
| `shared/standards/electrical/IEC61439/README.md` | Stub (`# IEC61439`) — must be rewritten |
| `electrical/sld/skill.manifest.json` | Already points at `shared/standards/electrical/IEC61439/` — no change required |

Everything else must be created from scratch.

---

## 4. File Set — 22 Files Total

### 4.1 Layer-level (2)

| File | Action | Content |
|---|---|---|
| `README.md` | Rewrite | Layer index — purpose, file catalogue, how skills consume it, schema overview |
| `meta.json` | New | Standard title, edition history (1st: 2009, 2nd: 2011–2014, restructure 2020+), IEC database URL, part catalogue with titles, national adoptions (BS EN 61439, DIN EN 61439, NF EN 61439, AS/NZS 61439), relationship to withdrawn IEC 60439 |

### 4.2 Part JSONs (7)

| File | IEC Part | Content |
|---|---|---|
| `part1-general.json` | Part 1 | General rules — definitions, electrical/mechanical characteristics, rated quantities (Ue, Ui, Uimp, In, Inc, Icw, Ipk, fn), interface characteristics, designated user vs original manufacturer split, conditions of use (indoor/outdoor, normal/special service) |
| `part2-psc-assemblies.json` | Part 2 | Power switchgear and controlgear assemblies (PSC-Assemblies) — main switchboards, MCCs. Form separation classes summary, application guidance, busbar systems |
| `part3-dbo-assemblies.json` | Part 3 | Distribution boards for ordinary persons (DBO) — consumer units, sub-DBs operated by laypersons. Constraints on accessibility, IP, child-safety, marking |
| `part4-acs-assemblies.json` | Part 4 | Construction site assemblies (ACS) — temporary site supplies. IK ≥ 08 impact, portability, RCD requirements, mechanical robustness |
| `part5-penda-assemblies.json` | Part 5 | Power distribution assemblies for public electricity networks (PENDA) — DNO/utility cabinets, kiosks, pillar boxes. Severe environmental, vandal, lightning impulse withstand |
| `part6-busbar-trunking.json` | Part 6 | Busbar trunking systems (BTS) — vertical risers, horizontal mains busduct. Joint design, fire stops, expansion joints, fault-current path |
| `part7-applications.json` | Part 7 | Specific applications — Part 7-1 (camping/marinas), 7-2 (EV charging stations), 7-3 (safety services), 7-4 (PV applications), 7-5 (transformer assemblies). Application-specific overlays on Part 1–3 rules |

### 4.3 Cross-cutting topic JSONs (8)

| File | Content |
|---|---|
| `form-separations.json` | Forms 1 → 4b — explicit definitions, ASCII diagrams, what's segregated, applications, advantages/disadvantages, neighbour-form comparison |
| `verification-methods.json` | The 2014 trio: test / calculation / comparison-with-reference-design. Annex D matrix mapping characteristic → permitted methods. Documentation requirements per method |
| `ip-ik-ratings.json` | IP code (Part 1 Table 7), IK code (BS EN 50102), default minimum IP per application context, IK ≥ 08 for ACS, IP requirements for outdoor PENDA, comparison with IEC 60364 location IPs |
| `temperature-rise.json` | Annex E rated diversity factor (RDF), conventional temperature rise limits (Table 6), ambient correction, busbar current carrying capacity at elevated ambient, verification approaches |
| `short-circuit-withstand.json` | Icw (rated short-time), Ipk (peak), Icc (conditional), upstream protective-device coordination, n-factor for peak ratio (Ipk = n × Icw), Annex P verification method |
| `internal-arc-classification.json` | IAC classification (IEC TR 61641 / Annex 9) — A/B/C/D protection criteria, accessibility types F/L/R, arc-flash boundary, application boundary |
| `busbar-derating.json` | Busbar current carrying capacity, current density tables, adjacency derating, ambient correction, fault-current force `F = K·Ipk²·s/d`, neutral / PE busbar sizing |
| `rated-quantities.json` | Quick-reference for Ue, Ui, Uimp, In, Inc, Icw, Ipk, fn, pollution degree (PD2 default), overvoltage category — typical LV values |

### 4.4 Narrative MDs (5)

| File | Content |
|---|---|
| `amendments-summary.md` | Edition history (1st 2009 → 2nd 2011/2014 → restructure 2020+). Key changes affecting designers: new verification trio, expanded Part 7 series, IAC formalisation |
| `design-vs-manufacture.md` | Critical responsibility split — Original Manufacturer (OM) vs Assembly Manufacturer (AM) vs MEP designer (who specifies, not builds). What's specified vs verified vs documented |
| `compliance-checklist.md` | Designer-side checklist of every mandatory characteristic to include on schedules, drawings, BOQ. Cross-references IEC 60364 installation rules and BS 7671 UK practice |
| `terminology.md` | Critical-distinction glossary — PSC-Assembly vs DBO, assembly vs constructional vs functional unit, type-tested vs verified, Form codes, accessibility (operator/maintenance/non-skilled) |
| `worked-examples.md` | 3–4 worked examples: (a) Form 3b PSC-Assembly verification chain, (b) IAC accessibility for an MCC, (c) Busbar derating for a 4000 A board at 45 °C ambient, (d) Icw coordination with upstream MCCB |

---

## 5. Per-Assembly JSON Schema (Part Files)

Every entry in `part1-general.json` through `part7-applications.json` uses this schema. All fields mandatory.

```json
{
  "assembly_id":        "PSC_ASSEMBLY_FORM_3B",
  "iec_ref":            "IEC61439-2:2020",
  "iec_part":           2,
  "iec_title":          "Power switchgear and controlgear assemblies — Form 3b",
  "draftsman_id":       "PSC_ASSEMBLY_FORM_3B",
  "application_scope":  "Main LV switchboards and MCCs with segregated functional units and separately-terminated outgoing busbars. Used where maintenance access on one circuit without de-energising others is required.",
  "rated_quantities": {
    "Ue_V":      [230, 400, 690, 1000],
    "Ui_V":      [1000],
    "Uimp_kV":   [4, 6, 8, 12],
    "In_A":      [630, 800, 1250, 1600, 2000, 2500, 3200, 4000, 5000, 6300],
    "Icw_kA_1s": [25, 36, 50, 65, 80, 100],
    "Ipk_kA":    [52, 75, 105, 143, 176, 220]
  },
  "form_separation":    "3b",
  "ip_default":         "IP2X (front), IP30 (enclosure)",
  "ik_default":         "IK08",
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
    "10.2 strength of materials and parts",
    "10.3 degree of protection",
    "10.4 clearances and creepage distances",
    "10.5 protection against electric shock",
    "10.6 incorporation of switching/protective devices",
    "10.7 internal electrical circuits",
    "10.8 terminals for external conductors",
    "10.9 dielectric properties",
    "10.10 temperature rise verification (Annex E)",
    "10.11 short-circuit withstand verification (Annex P)",
    "10.13 mechanical operation"
  ],
  "drawn_as":           ["DB_MAIN", "DB_SUB"],
  "typical_components": ["ACB_3P", "MCCB_3P", "BUSBAR_3PH", "CT_METERING", "MULTIFUNCTION_METER", "SPD_TYPE2"],
  "application_examples": [
    "Main LV switchboard (MSB) downstream of LV transformer",
    "Motor control centre (MCC) with segregated motor circuits",
    "Critical services switchboard with selectivity to ACB"
  ],
  "related_iec_60364":  ["IEC60364-4-43 (overcurrent)", "IEC60364-5-53 (switchgear)", "IEC60364-6 (verification)"],
  "related_bs_7671":    ["Reg 432 (Coordination)", "Section 537 (Isolation and switching)"],
  "usage_notes":        "Form 3b is the default choice for commercial main LV switchboards above ~400 A. Specify separately for incomer/outgoing-way busbars and the requirement for incomer maintenance with outgoers live.",
  "related_assemblies": ["PSC_ASSEMBLY_FORM_4A", "PSC_ASSEMBLY_FORM_2B", "DBO_ASSEMBLY"]
}
```

### Field definitions

| Field | Type | Description |
|---|---|---|
| `assembly_id` | string | UPPER_SNAKE_CASE canonical identifier used in skill IR outputs |
| `iec_ref` | string | IEC reference including part and edition year (e.g. `IEC61439-2:2020`) |
| `iec_part` | integer | IEC 61439 part number (1–7) |
| `iec_title` | string | Title from the standard, not paraphrased |
| `draftsman_id` | string | Same as `assembly_id` (explicit for generated-output clarity) |
| `application_scope` | string | What this assembly is used for, written for the designer |
| `rated_quantities` | object | Standard-defined rated values. Keys: `Ue_V`, `Ui_V`, `Uimp_kV`, `In_A`, `Icw_kA_1s`, `Ipk_kA`. Values are arrays of permitted standard values. |
| `form_separation` | string | Form code `1` / `2a` / `2b` / `3a` / `3b` / `4a` / `4b` or `n/a` |
| `ip_default` | string | Default minimum IP rating description |
| `ik_default` | string | Default minimum IK rating |
| `mandatory_characteristics` | string[] | Field names a designer MUST specify on the schedule for this assembly. Used by skill validation. |
| `verification_clauses` | string[] | Clause references the OEM must verify before commissioning |
| `drawn_as` | string[] | IEC 60617 `symbol_id` values that render this assembly graphically |
| `typical_components` | string[] | Devices commonly inside this assembly (IEC 60617 `symbol_id` references) |
| `application_examples` | string[] | Typical use cases in MEP building context |
| `related_iec_60364` | string[] | Cross-references to installation-side IEC 60364 clauses |
| `related_bs_7671` | string[] | Cross-references to UK practice (BS 7671 regulations) |
| `usage_notes` | string | Engineering guidance: when to use, gotchas, defaults |
| `related_assemblies` | string[] | Other `assembly_id` values commonly considered alongside this one |

---

## 6. Cross-Cutting Topic File Convention

Each topic file carries a common header plus a topic-specific array:

```json
{
  "_title":      "IEC 61439 — Form Separations",
  "_iec_part":   "2 (with cross-references to 3 and 4)",
  "_version":    "1.0.0",
  "_note":       "Form separations are defined in Part 2 Annex 101 and are referenced by Parts 3 and 4 where applicable. This file consolidates them for skills that need to pick a Form regardless of which assembly type.",
  "<topic_specific_array>": [ ... ]
}
```

### 6.1 Form separations schema (`form-separations.json`)

```json
{
  "form_code":        "3b",
  "iec_ref":          "IEC61439-2:2020 Annex 101",
  "title":            "Form 3b — Separation of busbars, separation of functional units, separately-terminated outgoing conductors",
  "segregation_of": {
    "busbars_from_functional_units":             true,
    "functional_units_from_each_other":          true,
    "terminals_for_outgoing_conductors_separated": true,
    "terminals_in_same_compartment_as_functional_unit": false
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
  "applications":   ["Critical services main switchboards", "Industrial MCCs requiring single-circuit maintenance", "Hospital essential supply distribution"],
  "advantages":     ["Single circuit maintenance with rest live", "Outgoing terminations isolated from busbar"],
  "disadvantages":  ["Higher cost than Form 3a", "More floor space than Form 2"],
  "vs_neighbours": {
    "Form_2b":  "Adds separation between functional units (was a single bay)",
    "Form_3a":  "Form 3a has outgoing terminals in the SAME compartment as the functional unit; 3b separates them",
    "Form_4a":  "Form 4a separates each outgoing terminal individually rather than as a group"
  },
  "draftsman_id":   "FORM_3B",
  "drawn_as":       ["DB_MAIN", "DB_SUB"],
  "usage_notes":    "Default choice for commercial main switchboards 400–4000 A. Specify explicitly on the assembly schedule — the OEM cannot infer the Form from a generic 'main switchboard' callout."
}
```

ASCII diagram convention: `BUSBARS` row at the top, `FU` = functional-unit compartment, `T` = outgoing-terminal compartment, `|` indicates a metallic barrier, space indicates no separation. All 7 Form codes (`1`, `2a`, `2b`, `3a`, `3b`, `4a`, `4b`) get their own entry.

### 6.2 Verification methods schema (`verification-methods.json`)

```json
{
  "methods": [
    {
      "method_id":         "TEST",
      "name":              "Verification by testing",
      "iec_ref":           "IEC61439-1 Clause 10",
      "description":       "Physical test of a representative assembly against the standard.",
      "applies_to_characteristics": ["10.2", "10.3", "10.10", "10.11", "10.13"],
      "documentation":     "Test certificate from accredited laboratory; type-test records"
    },
    {
      "method_id":         "CALC",
      "name":              "Verification by calculation",
      "iec_ref":           "IEC61439-1 Clause 10 + Annex E/P",
      "description":       "Engineering calculation per the standard's annexes (Annex E temperature rise; Annex P short-circuit).",
      "applies_to_characteristics": ["10.10 (Annex E)", "10.11 (Annex P)"],
      "limits":            "Permitted only where Annex method exists. NOT permitted for IP, dielectric, or arc.",
      "documentation":     "Calculation report referencing exact annex method, with assumptions and component data"
    },
    {
      "method_id":         "REFERENCE",
      "name":              "Verification by comparison with reference design",
      "iec_ref":           "IEC61439-1 Clause 10.5.3 + Annex D",
      "description":       "Compare candidate against a previously verified reference that bounds it (same/larger enclosure, no worse component arrangement, busbar at least as oversized).",
      "applies_to_characteristics": ["10.2", "10.5", "10.10", "10.11"],
      "limits":            "Bounding rules in Annex D must be strictly met. NOT permitted for IP without test of the candidate.",
      "documentation":     "Reference design verification certificate + bounding comparison report"
    }
  ],
  "annex_d_matrix": "Each characteristic 10.2..10.13 with permitted methods."
}
```

### 6.3 Other topic files

| File | Top-level array | Notes |
|---|---|---|
| `ip-ik-ratings.json` | `ip_codes` (IP00..IP69K) + `ik_codes` (IK00..IK10) | Each entry has first/second digit meaning, test conditions, minimum-IP-by-location matrix |
| `temperature-rise.json` | `temperature_rise_limits` (Table 6 entries) + `rated_diversity_factors` + `annex_e_calculation_steps` | Conventional limits per component class |
| `short-circuit-withstand.json` | `withstand_characteristics` (Icw / Ipk / Icc) + `coordination_rules` + `n_factor_table` | n-factor table for converting Icw to Ipk |
| `internal-arc-classification.json` | `iac_criteria` (A/B/C/D) + `accessibility_types` (F/L/R) + `application_boundary_rules` | When IAC applies and what classification to specify |
| `busbar-derating.json` | `current_carrying_capacity` + `derating_factors` + `force_calculation` | Force `F = K·Ipk²·s/d` with K table |
| `rated-quantities.json` | `quantities` object keyed by symbol (Ue, Ui, Uimp, In, …) | Each entry has unit, definition, typical LV values, standard-defined preferred values |

---

## 7. Design-vs-Manufacture Responsibility Split (Narrative)

This is the single most-confused topic for designers. The narrative MD covers it explicitly:

- **Original Manufacturer (OM):** Designs and verifies the assembly against IEC 61439. Holds the type-test records, calculation reports, and reference design certificates. Provides verified designs to Assembly Manufacturers.
- **Assembly Manufacturer (AM):** Builds individual units under the OM's verified design. May be the same legal entity as the OM, or a licensed third-party panel builder.
- **MEP designer (you):** Specifies the assembly on schedules, drawings, BOQ. Does not verify and does not manufacture.

**What the MEP designer specifies** (on the schedule):
assembly designation, In, Icw, Ipk, Ue, Ui, Uimp, fn, IP, IK, form, IAC if applicable, ambient, service conditions, accessibility class.

**What the OEM verifies and provides on handover:**
test certificates, calculation reports, reference design certificates, type-test records, instructions for installation/operation/maintenance.

**Documentation flow:** designer's spec → OEM's verified design → as-built drawings + verification reports → handover pack → BSRIA BG 29 O&M manual.

---

## 8. Cross-references

### Out (this layer references)
- IEC 60617 symbol IDs (`drawn_as` array on every assembly entry)
- IEC 60364 clauses (`related_iec_60364` on assembly entries; `compliance-checklist.md` cites installation rules)
- BS 7671 regulations (`related_bs_7671` on assembly entries; `compliance-checklist.md` cites UK practice)
- IEC TR 61641 (referenced from `internal-arc-classification.json`)
- BS EN 50102 (IK rating standard, referenced from `ip-ik-ratings.json`)

### In (anticipated consumers, no changes required to those skills here)
- `electrical/sld` — form separations, busbar ratings, fault levels at assembly busbar
- `electrical/db-layout` — form separations, IP, busbar config, ratings
- `electrical/panel-schedule` — form, ratings, BOM, IAC
- `electrical/riser` — Part 6 busbar trunking systems
- `electrical/transformer` / `generator` / `ups` / `hvac-power` / `solar-pv` — Part 2 PSC-Assembly rules
- `electrical/schematic` — assembly internal-circuit conventions

The SLD manifest already references `shared/standards/electrical/IEC61439/` so no manifest changes are required.

---

## 9. Out of Scope

- **IEC 60439 (predecessor, withdrawn 2014).** New designs use IEC 61439 only.
- **Manufacturer-specific catalogue data.** ABB / Schneider / Siemens / Eaton ranges live in datasheets, not in the standards layer. A future `shared/manufacturers/` layer is the right home if it becomes needed.
- **HV switchgear assemblies (IEC 62271).** HV is a separate standard family and out of MEP building LV scope.
- **Power-electronic converter assemblies (IEC 61800-x).** Drive enclosures are governed by IEC 61800; cross-reference only.
- **Functional safety of assemblies (IEC 61508 / 62061).** Protective relaying dependability referenced but not specified here.
- **Internal wiring rules below assembly level.** Component-to-component wiring inside an assembly is OEM-internal; designers do not specify it.
- **Generated symbol files.** Layer is input-only. Does not produce `shared/symbols/electrical/` entries.

---

## 10. File Tree (final state)

```
IEC61439/
├── README.md                           ← rewrite
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

## 11. Layer Success Criteria

1. Any consuming skill (sld, db-layout, panel-schedule, riser, etc.) can answer "what Form do I specify?" by loading `form-separations.json` alone.
2. Every assembly entry across all 7 part files has a `drawn_as` array that resolves to existing IEC 60617 `symbol_id` values (no dangling references).
3. The compliance checklist enumerates every characteristic an MEP designer must specify, so a schedule generated by a skill cannot omit a mandatory field.
4. Each file is ≤ ~300 lines so AI consumers load them without context pressure.
