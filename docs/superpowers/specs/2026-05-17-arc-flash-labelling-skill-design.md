# `electrical/arc-flash-labelling` Skill v1.0.0 — Design Spec

**Date:** 2026-05-17
**Status:** Approved — ready for implementation plan
**Sprint scope:** Unified Phase A (standards layers promotion) + Phase B (skill build). Estimated ~73 files total.
**Pattern parents:** `electrical/fault-level/` + `electrical/cable-sizing/` + `electrical/arc-flash/` — same artefact shape.
**Stubs already on disk** at `electrical/arc-flash-labelling/` + `shared/standards/electrical/ANSI-Z535-4/` (commit `711ebd5`).

---

## 1. Overview & Scope

This sprint consumes the `arc-flash` intent (shipped previous sprint at `electrical/arc-flash/`) and renders printable arc-flash warning labels per ANSI Z535.4 + ISO 7010 + BS 5499 (jurisdiction-aware) plus a project-wide label index.

### 1.1 Skill identity

- Name: `electrical/arc-flash-labelling`
- Version: `1.0.0` beta
- Drawing type: `arc_flash_labelling_study`
- Discipline: electrical / subdiscipline: safety-output

### 1.2 What it produces

**Per-equipment label:**

- Signal-word header: **DANGER** (Cat 3-4) / **WARNING** (Cat 1-2) / **RESTRICTED** (IE > 40 cal/cm²)
- Equipment ID, nominal voltage, date of analysis
- Incident energy at working distance (cal/cm²)
- Arc-flash boundary distance (mm + inches)
- Limited + Restricted shock-approach boundaries
- Required PPE category + concise clothing description (NFPA 70E Table 130.7(C)(16))
- Engineering company name + qualified-person signature placeholder
- Optional QR code (project-scoped URL)

**Project-wide outputs:**

- Single-page SVG per equipment (inline LLM-produced)
- PDF per equipment (deferred to `calc.render_label` runtime tool, WI3)
- Project label-index PDF (deferred, runtime)
- Optional PNG raster per equipment (deferred, runtime)

**Plus a `labels` intent** for downstream facility-management / digital-twin consumers.

### 1.3 Sprint scope decomposition

| Phase | Content | Files |
|---|---|---|
| Phase A | Standards layers (ANSI-Z535-4 + ISO-7010 + BS-5499) | ~21 |
| Phase B | The skill at `electrical/arc-flash-labelling/` | ~30 |
| Misc | New calc contract + SVG templates + 3 worked examples | ~22 |
| **Total** | | **~73** |

### 1.4 Out of scope (deferred to v1.1+)

- Physical label printing (the skill outputs files; printing is downstream)
- Custom company branding overlays beyond placeholder support
- Multi-language labels (English only at v1.0; multilang in v1.1)
- Old NFPA 70E:2018 label format (v1.0 renders to 2024 standard)
- Tactile / Braille labels
- Australian AS 1319 format (added in v1.x if demand)

---

## 2. File Structure (~73 files)

### 2.1 Phase A — Standards layers (21 files)

```
shared/standards/electrical/ANSI-Z535-4/   (stub → production, 11 files)
├── README.md
├── meta.json
├── terminology.md
├── compliance-checklist.md
├── signal-words.json
├── colour-spec.json
├── symbol-library.json
├── panel-format.json
├── letter-height-requirements.json
├── label-content-rules.json
└── arc-flash-label-template.md

shared/standards/electrical/ISO-7010/      (NEW, 6 files)
├── README.md
├── meta.json
├── terminology.md
├── warning-signs.json
├── colour-spec.json
└── compliance-checklist.md

shared/standards/electrical/BS-5499/       (NEW, 4 files)
├── README.md
├── meta.json
├── uk-conventions.md
└── compliance-checklist.md
```

### 2.2 Phase B — The skill (~30 + 4 templates = 34 files)

```
electrical/arc-flash-labelling/
├── README.md
├── CHANGELOG.md
├── skill.manifest.json
├── inputs.json
│
├── prompts/
│   ├── generator.md          (12-step chain)
│   ├── validator.md          (8 INV invariants)
│   └── reviewer.md           (6 D dimensions)
│
├── schemas/
│   ├── labels-ir.schema.json
│   └── labels-intent.schema.json
│
├── rules/
│   ├── jurisdiction-format-selection.yaml
│   ├── signal-word-policy.yaml
│   ├── label-content-population.yaml
│   └── ppe-clothing-description.yaml
│
├── constraints/
│   ├── required-content-present.yaml
│   ├── colour-spec-compliance.yaml
│   └── letter-height-legibility.yaml
│
├── validation/
│   ├── ir-integrity.yaml
│   ├── jurisdiction-format-match.yaml
│   └── intent-shape.yaml
│
├── ontology/
│   ├── label-formats.json
│   └── signal-words.json
│
├── docs/
│   ├── engineering-philosophy.md
│   └── known-limitations.md
│
├── evals/
│   ├── runner-config.json
│   └── eval-01 … eval-08.yaml
│
├── templates/                (4 SVG templates)
│   ├── ansi-z535-4-label.svg.template
│   ├── iso-7010-label.svg.template
│   ├── bs-5499-label.svg.template
│   └── restricted-label.svg.template
│
└── examples/                  (3 × 5 files = 15)
    ├── us-ansi-label-set/
    │   ├── input.json
    │   ├── output.json
    │   ├── intent-out.json
    │   ├── sample-svg/MSB-1.svg
    │   └── reasoning.md
    ├── uk-bs5499-label-set/
    │   └── (same 5-file shape)
    └── intl-iso7010-label-set/
        └── (same 5-file shape)
```

### 2.3 New calc contract

```
shared/calculations/electrical/render-label.json
```

### 2.4 Total file inventory

| Group | Files |
|---|---|
| Phase A — ANSI-Z535-4 | 11 |
| Phase A — ISO-7010 | 6 |
| Phase A — BS-5499 | 4 |
| Phase B — root | 4 |
| Phase B — prompts | 3 |
| Phase B — schemas | 2 |
| Phase B — rules + constraints + validation | 10 |
| Phase B — ontology | 2 |
| Phase B — docs | 2 |
| Phase B — evals (1 runner-config + 8 evals) | 9 |
| Phase B — SVG templates | 4 |
| Phase B — examples (3 × 5) | 15 |
| New calc contract | 1 |
| **Total** | **73** |

---

## 3. Standards Layer Content (Phase A)

### 3.1 ANSI-Z535-4 — canonical US format

| File | Content |
|---|---|
| `signal-words.json` | DANGER / WARNING / CAUTION / NOTICE with Pantone colour codes, severity definitions, trigger conditions |
| `colour-spec.json` | Pantone refs + CMYK/RGB/hex equivalents for safety colours + distinct RESTRICTED colour |
| `symbol-library.json` | Arc-flash symbol, electric shock symbol, general hazard alert, PPE-required symbol |
| `panel-format.json` | Sign-panel layout (signal-word + message + symbol panels); minimum dimensions |
| `letter-height-requirements.json` | Z535.4 Annex B legibility table — letter height per working distance |
| `label-content-rules.json` | NFPA 70E §130.5(H) required + optional fields with ordering convention |
| `arc-flash-label-template.md` | Canonical Z535.4 + NFPA 70E label layout described in prose |

### 3.2 ISO-7010 — international format

| File | Content |
|---|---|
| `warning-signs.json` | W-series signs; W012 = arc-flash hazard symbol (yellow triangle + black border + black lightning) |
| `colour-spec.json` | ISO 7010 colour palette: Warning Yellow / Mandatory Blue / Prohibition Red / Safe Green |

### 3.3 BS-5499 — UK conventions

| File | Content |
|---|---|
| `uk-conventions.md` | UK-specific language + HSG48 framing + BS 7671 references + voluntary best-practice notes |
| `compliance-checklist.md` | When a UK label is HSG48-compliant |

---

## 4. Data Flow

### 4.1 Inputs

**Consumed from upstream intent (preferred):**

| Source intent | Fields used |
|---|---|
| `arc-flash` | All 11 required + 4 optional per-node fields (designation, equipment_type, voltage_v, IE, AFB, working_distance_mm, 3 shock-approach distances, ppe_category, method_applied, label_recommended, label_required_per, produced_at) |

**Engineer overlay (project-scoped):**

- `jurisdiction` → drives format selection
- `company_name` + `qualified_person_signature` → appear on every label
- `qr_code_base_url` → optional; labels carry `<base_url>/<node_id>`
- `label_size_mm` → default 100 × 75 mm
- `format_override_per_node` → optional dict for hybrid facilities
- `branding_overlay` → optional company logo SVG path

### 4.2 IR shape

Project-scoped collection of per-equipment labels. Each label entry carries:

- `node_id`, `designation`
- `format_applied` (ansi_z535_4 / iso_7010 / bs_5499 / restricted_format)
- `signal_word` (DANGER / WARNING / RESTRICTED / NOTICE)
- `label_content` (all required + optional fields formatted for display)
- `rendering` block: `label_size_mm`, `svg_template_used`, `svg_content` (inline), `tool_call_pending_for_pdf_png`

Plus `project_label_index` summary table + `compliance_summary` + WI2-style 8-section `rationale`.

### 4.3 Output intent — `labels`

Slim downstream subset (5-6 fields per node) for facility-management consumers: `node_id`, `format_applied`, `signal_word`, `ppe_category`, `label_size_mm`, optional `qr_code_url`.

### 4.4 Renderings — WI3 deferred

| Format | How produced |
|---|---|
| **SVG** | Inline by the skill (LLM-readable + LLM-writable from Jinja-style template) |
| **PDF** | `calc.render_label` runtime tool (WI3 — tool_call_pending until runtime ships) |
| **PNG** | Same — deferred |
| **Project label-index PDF** | Deferred — runtime bundles per-equipment PDFs |

### 4.5 New calc contract — `calc.render_label`

File: `shared/calculations/electrical/render-label.json`

Defines:
- Inputs: `svg_content`, `format` (pdf / png), `size_mm`, `dpi`
- Outputs: `rendered_bytes`, `format_actual`, `byte_count`

---

## 5. Label Content Rules

### 5.1 Format selection (`rules/jurisdiction-format-selection.yaml`)

| Jurisdiction | Default format |
|---|---|
| US | ansi_z535_4 |
| EU | iso_7010 |
| INT | iso_7010 |
| GB | bs_5499 |

**Override priority:** RESTRICTED (IE > 40) > engineer_per_node > jurisdiction_default.

The RESTRICTED override is safety-critical and supersedes all other selections regardless of regional convention.

### 5.2 Signal-word policy (`rules/signal-word-policy.yaml`)

| Trigger | Signal word | Rationale |
|---|---|---|
| PPE Cat 1 or 2 | WARNING | "Could result in injury" per Z535.4 severity |
| PPE Cat 3 or 4 | DANGER | "Imminent hazard / serious injury risk" |
| IE > 40 cal/cm² | RESTRICTED | Above NFPA 70E Cat 4 ceiling — energized work prohibited |
| `label_recommended == false` | NONE | Skip (e.g., single-family residential exemption) |

Signal-word colour is looked up from the applicable format's `colour-spec.json`.

### 5.3 Content population (`rules/label-content-population.yaml`)

Maps each arc-flash intent field → label content field with formatting rules:

| Arc-flash field | Label content | Formatting |
|---|---|---|
| `designation` | header sub-line | uppercase; max 60 chars |
| `voltage_v` | nominal_voltage | "{V} V {phases}-phase" |
| `incident_energy_cal_per_cm2` | incident_energy_at_working_distance | "{IE} cal/cm² @ {D}mm" or "Not computed — see analysis" if null |
| `arc_flash_boundary_mm` | arc_flash_boundary | "{mm} mm ({inches} in)" — both units |
| 3 shock-approach distances | shock_approach | same dual-unit format; "avoid contact" verbatim where applicable |
| `ppe_category` | ppe_category | "Category {N}" or "Specialised PPE Required" for RESTRICTED |
| (lookup) | ppe_clothing_description | from `rules/ppe-clothing-description.yaml` |
| `produced_at` | analysis_date | YYYY-MM-DD |
| (project metadata) | engineer, qr_code_url, company | from overlay |

### 5.4 PPE clothing descriptions (`rules/ppe-clothing-description.yaml`)

Concise text per NFPA 70E Table 130.7(C)(16), capped at 200 characters per label:

| Category | Description |
|---|---|
| 1 | AR shirt+trousers OR coverall (ATPV ≥4 cal/cm²); face shield + balaclava; safety glasses; hard hat; leather gloves |
| 2 | AR shirt+trousers OR coverall (ATPV ≥8 cal/cm²); AR hood; safety glasses; hard hat; rubber+leather gloves |
| 3 | AR suit + AR hood (ATPV ≥25 cal/cm²); AR gloves; hard hat; safety glasses |
| 4 | AR suit + AR hood (ATPV ≥40 cal/cm²); AR gloves; hard hat; safety glasses |
| RESTRICTED | Energized work prohibited. De-energise and LOTO before work. Specialised assessment required — contact facility safety engineering. |

Engineer override permitted; recorded as `ppe_description_source = engineer_override`.

### 5.5 RESTRICTED label format

When `signal_word == RESTRICTED`:
- Distinct **purple/black header** (not red/orange/yellow)
- PPE-category line replaced with RESTRICTED clothing description
- Bold "DO NOT OPERATE" overlay OR strike-through on equipment-label area
- Other content (IE, AFB, shock-approach) retained so reviewers see the rationale

Encoded in `templates/restricted-label.svg.template`.

### 5.6 Constraints — 3 YAMLs, 9 checks

| File | Key checks |
|---|---|
| `required-content-present.yaml` | All 8 NFPA 70E §130.5(H) required fields populated; RESTRICTED uses RESTRICTED text not "Category null"; label-size ≥ Z535.4 minimum |
| `colour-spec-compliance.yaml` | Signal-word colour matches format standard; RESTRICTED uses sanctioned distinct colour; all SVG colours from sanctioned palette |
| `letter-height-legibility.yaml` | Signal-word height ≥ legibility table for working distance; body text ≥ 3mm; equipment-ID is bold + dedicated panel |

---

## 6. Prompts

### 6.1 Generator — 12-step chain

1. Ingest arc-flash intent → extract per-node label data
2. Determine jurisdiction (from project metadata or arc-flash IR)
3. Apply project-metadata overlay (company_name, qualified_person, qr_code_base_url, label_size_mm)
4. Filter to nodes where `label_recommended == true`
5. Select label format per `rules/jurisdiction-format-selection.yaml` (RESTRICTED overrides for IE > 40)
6. Select signal_word per `rules/signal-word-policy.yaml`
7. Populate `label_content` per `rules/label-content-population.yaml` (dual-unit formatting, QR URL construction)
8. Lookup PPE clothing description per `rules/ppe-clothing-description.yaml` (engineer override allowed)
9. Inline-render SVG by populating the template at `templates/<format>-label.svg.template`
10. Declare `tool_call_pending_for_pdf_png: true` (calc.render_label deferred per WI3)
11. Build project-label-index summary table
12. Run all 3 constraint files → emit non_compliance_flags[]. Emit `labels` intent. Assemble 8-section rationale.

### 6.2 Validator — 8 INV invariants

| INV | Statement |
|---|---|
| INV-01 | Valid node_id pattern; parent_node_id resolves |
| INV-02 | format_applied from controlled vocabulary (4 values) |
| INV-03 | signal_word from controlled vocabulary (5 values) |
| INV-04 | PPE Cat ↔ signal_word mapping consistent (1-2→WARNING, 3-4→DANGER, IE>40→RESTRICTED) |
| INV-05 | All NFPA 70E §130.5(H) required content fields populated per label |
| INV-06 | `rendering.svg_content` non-empty AND contains expected template markers |
| INV-07 | `tool_call_pending_for_pdf_png` consistent (boolean) |
| INV-08 | Emitted labels intent validates against schema AND 1-to-1 with IR labels[] |

### 6.3 Reviewer — 6 D dimensions

| D | Dimension |
|---|---|
| D1 | Standards citations specific per label (Z535.4 + NFPA 70E §130.5(H) clauses) |
| D2 | Signal-word policy applied correctly per node |
| D3 | RESTRICTED handling distinct (purple/black + Cat-line suppressed + "Energized work prohibited") |
| D4 | Content completeness — spot-check 3 nodes; all §130.5(H) fields have real values |
| D5 | Jurisdictional format match (GB → BS-5499; US → ANSI; etc.); mixed only with explicit override |
| D6 | Rationale: 8 sections + chat_summary ≤ 1200 chars + every decision cites rule + clause |

### 6.4 Generator hard rules

```
- Never invent label content fields not in arc-flash intent
- Never set format_applied outside controlled vocabulary
- Never set signal_word outside controlled vocabulary
- Never skip a node with label_recommended == true
- RESTRICTED format always uses distinct visual treatment
- SVG output must be valid XML (escape & < > " in dynamic content)
- QR URL omitted if qr_code_base_url not declared (never fake URLs)
```

---

## 7. Evals + Worked Examples

### 7.1 Eval coverage (8 evals)

| Eval ID | Category | What it tests |
|---|---|---|
| eval-01-us-mixed-cascade-ansi-labels | happy_path | US 480V cascade, ANSI Z535.4 auto-selected, mixed Cat 1-3 |
| eval-02-restricted-equipment-distinct-format | edge_case | IE = 45 → RESTRICTED format; distinct visual; suppressed Cat line |
| eval-03-missing-arc-flash-data-skip | validation_trap | Some IE values null → "Not computed" placeholder; no fabrication |
| eval-04-no-arc-flash-intent | missing_input | No upstream intent → tool_call_pending; empty labels[] |
| eval-05-jurisdiction-gb-bs5499 | jurisdiction_switch | GB → BS-5499 auto-selected; HSG48 framing in rationale |
| eval-06-rationale-block | rationale_block | 8 sections + chat_summary + citations |
| eval-07-svg-template-population | skill_specific | SVG content non-empty + template markers populated (no `{{...}}` left) |
| eval-08-qr-code-conditional-emission | skill_specific | qr_code_base_url declared → all labels have URLs; absent → none |

### 7.2 Worked examples

#### Example 1: `us-ansi-label-set/` (5 files)

Consumes the existing arc-flash intent from `electrical/arc-flash/examples/us-pv-with-dcfc/intent-out.json` (5 nodes: 3 AC + 2 DC). Produces ANSI Z535.4 labels for the 4 nodes with `label_recommended: true`; skips PV-string node.

Files: `input.json`, `output.json`, `intent-out.json`, `sample-svg/MSB-1.svg`, `reasoning.md`.

#### Example 2: `uk-bs5499-label-set/` (5 files)

UK 400V commercial. 2 nodes: MSB-1 (Cat 3 DANGER) + DB-L1 (Cat 2 WARNING). BS-5499 + ISO-7010 W012 hybrid layout.

#### Example 3: `intl-iso7010-label-set/` (5 files)

INT 11kV substation with one RESTRICTED node (IE = 47 cal/cm²). 3 nodes covering all 3 signal words.

### 7.3 Reference SVG quality

Each example includes one full SVG rendering that validates as XML, uses sanctioned colour codes, and renders at typical label-stock size (75 × 100 mm). Engineers can preview these directly in any browser.

---

## 8. Cross-Skill Contracts + Manifest

### 8.1 Manifest references

14 specific standards files (10 new + 4 reused from Phase A NFPA70E) + 1 new calc contract. Zero new IEEE 1584 references — this skill is rendering, not analysis.

### 8.2 Cross-skill intent contracts

| Direction | Intent | Purpose |
|---|---|---|
| Consumes | `arc-flash` | Per-node IE / AFB / PPE / shock-approach / equipment_type / label_recommended |
| Produces | `labels` | Per-equipment label metadata for facility-management / digital-twin consumers |

### 8.3 Phase A pending-verification dependency

The arc-flash intent it consumes may carry IE values from `method_applied: lee_1982` (Phase A IEEE 1584 coefficients pending-verification). The labelling skill renders whatever IE value the intent provides — when coefficients are transcribed and arc-flash auto-promotes to `ieee1584_2018`, the labels regenerate with the new (typically lower) IE values, potentially shifting some equipment from Cat 3 → Cat 2 or similar.

### 8.4 Versioning policy

- Minor (1.x.0): new formats (Australian AS 1319), bilingual, branding overlays
- Major (2.0.0): breaking schema OR Z535.4 / ISO 7010 revision adoption
- Patch (1.0.x): rules / templates / SVG fixes

### 8.5 Sprint dependencies

| Dependency | Status |
|---|---|
| `electrical/arc-flash` v1.0.0 (consumed intent) | ✅ Shipped 2026-05-17 |
| Phase A NFPA70E layer (4 files referenced) | ✅ Production |
| `shared/standards/electrical/ANSI-Z535-4/` | Stubbed → promoted this sprint |
| `shared/standards/electrical/ISO-7010/` | NEW this sprint |
| `shared/standards/electrical/BS-5499/` | NEW this sprint |

### 8.6 Sprint sequence after this ships

| Sprint | Content | Status |
|---|---|---|
| ✅ Prior + Phase A + Phase B + clause_ref retrofit | All foundation work | Shipped |
| 🔄 **This sprint** | **arc-flash-labelling + ANSI Z535.4 + ISO 7010 + BS 5499** | In design |
| Next | `electrical/earthing` v1.1 — TN-S + Zs table | Queued |
| Then | `electrical/db-layout` v1.1 — DC distribution + Type B RCD | Queued |
| Then | `electrical/voltage-drop` (or fold into cable-sizing) | Queued |
| Then | `electrical/sld` v1.2 — eval split | Queued |

---

## 9. Approval

All 8 design sections approved by user 2026-05-17. Ready for implementation plan.

**Sprint scope summary:** 73 files (21 Phase A standards + 30 Phase B skill + 4 SVG templates + 15 example files + 1 calc contract + 2 stub-folder bootstraps already on disk). Uses the proven artefact pattern (`earthing` / `db-layout` / `fault-level` / `cable-sizing` / `arc-flash`).

Next step: invoke `superpowers:writing-plans` to produce `docs/superpowers/plans/2026-05-17-arc-flash-labelling-skill.md`.
