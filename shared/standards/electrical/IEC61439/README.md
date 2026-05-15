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
