# IEEE 1584 + NFPA 70E Standards-Layer Build — Design Spec

**Date:** 2026-05-17
**Status:** Approved — ready for implementation plan
**Sprint scope:** Phase A only (the two standards layers). Phase B (the `electrical/arc-flash` skill) is scoped for the next sprint.
**Pattern parent:** `shared/standards/electrical/IEC60909/` (production, 13 files; this sprint follows the same pattern at greater depth).

---

## 1. Overview & Scope

This sprint promotes two electrical standards layers from `stub` → `production` so the future `electrical/arc-flash` skill (next sprint) can consume them. The skill is out of scope for this sprint.

### 1.1 Layers built

| Layer | Path | Files | Scope |
|---|---|---|---|
| IEEE 1584:2018 | `shared/standards/electrical/IEEE1584/` | 28 | Empirical arc-flash incident energy + boundary calculations (208V – 15 kV AC) |
| NFPA 70E (Article 130 + relevant annexes) | `shared/standards/electrical/NFPA70E/` | 25 | Workplace electrical safety: arc-flash risk assessment, PPE selection, boundary definitions, AC + DC reference methods |

**Sprint total: 53 files** (15 documentation files + 38 structured-data files).

### 1.2 Methods covered (4 calculation methods + 1 lookup method)

| Method | Source | Voltage range | Source layer |
|---|---|---|---|
| IEEE 1584:2018 | IEEE 1584:2018 §§6–10 | 208V – 15 kV AC | IEEE1584 |
| IEEE 1584:2002 | IEEE 1584:2002 (Lee + Doughty/Neal) | Same | IEEE1584 (legacy compatibility) |
| Doan 2007 (DC) | NFPA 70E:2024 Annex D Section D.1 | DC up to 1000V | NFPA70E |
| Stokes & Oppenlander 1991 (DC) | NFPA 70E:2024 Annex D Section D.2 | DC up to 1000V | NFPA70E |
| NFPA 70E Table Method | NFPA 70E:2024 Table 130.7(C)(15)(a)/(b) | Any (fallback) | NFPA70E |

### 1.3 What this sprint deliberately does NOT do

- **No skill build.** The `electrical/arc-flash/` skill (prompts, IR schema, evals, examples) ships in the next sprint.
- **No new calc contract.** `shared/calculations/electrical/arc-flash-incident-energy.json` is part of the next sprint.
- **No full standard text transcription.** Only clause references + factual data + brief paraphrase.
- **No vendor-specific lookup data.** We follow IEEE/NFPA only — not ETAP, SKM, EasyPower behaviour.
- **No future-standard reservations.** DC arc-flash content lives inside NFPA 70E Annex D (where the industry references it). If IEEE 1584.2 (DC) becomes a published standard, we migrate at that point per Section 7.

---

## 2. File structure (53 files)

### 2.1 IEEE1584 — 28 files

```
shared/standards/electrical/IEEE1584/
├── README.md                              (rewrite from stub)
├── meta.json                              (stub → production)
├── terminology.md
├── amendments-summary.md                  (IEEE 1584-2002 → 2018 deltas)
├── compliance-checklist.md
├── calculation-flowchart.md               (step-by-step method walkthrough)
│
├── method-2018-600V-coefficients.json     (LV class 208V–600V: 5 electrode configs × {k1..k7})
├── method-2018-2700V-coefficients.json    (intermediate 601V–2700V)
├── method-2018-14300V-coefficients.json   (MV 2701V–15kV)
├── intermediate-voltage-interpolation.json (IEEE 1584:2018 §7.4 — interpolation between classes)
├── arc-current-formula.json               (IEEE 1584:2018 §6 — Iarc formulas per voltage class)
├── arc-current-variation-high-low.json    (§10 high/low arc-current bracketing for worst case)
├── incident-energy-formula.json           (§7.5 core IE empirical model)
├── boundary-distance-formula.json         (§8 AFB derivation: AFB = D × (E/1.2)^(1/x))
│
├── electrode-config-VCB-coefficients.json    (Vertical electrodes in Cubic Box)
├── electrode-config-VCBB-coefficients.json   (VCB with Barrier)
├── electrode-config-HCB-coefficients.json    (Horizontal Cubic Box)
├── electrode-config-VOA-coefficients.json    (Vertical Open Air)
├── electrode-config-HOA-coefficients.json    (Horizontal Open Air)
│
├── adjustment-factor-non-standard-gap.json     (§10.3)
├── adjustment-factor-non-standard-distance.json (§10.4)
├── adjustment-factor-enclosure-size.json       (§10.5)
│
├── method-2002-lee-formula.json           (Ralph Lee 1982 — pre-empirical)
├── method-2002-doughty-neal-formula.json   (IEEE 1584:2002 empirical)
│
├── voltage-classes.json                   (class breakpoints + nominal voltages)
├── gap-distance-table.json                (Annex C Table A.1 — typical gap per equipment type)
├── working-distance-defaults.json         (Annex C Table A.1 — 455mm LV / 914mm MV)
└── equipment-classification.json          (real-equipment → electrode-config mapping)
```

### 2.2 NFPA70E — 25 files

```
shared/standards/electrical/NFPA70E/
├── README.md                              (rewrite from stub)
├── meta.json                              (stub → production)
├── terminology.md
├── article-130-overview.md
├── compliance-checklist.md
│
├── section-130-2-safe-work-condition.json  (when work proceeds energized vs LOTO)
├── section-130-3-precautions.json
├── section-130-4-shock-boundaries.json     (Limited + Restricted approach definitions)
├── section-130-5-arc-flash-risk-assessment.json (9-step risk-assessment process)
├── section-130-7-ppe.json
│
├── table-130-4-C-a-AC-approach.json        (AC shock boundaries by voltage)
├── table-130-4-C-b-DC-approach.json        (DC shock boundaries)
├── table-130-5-C-likelihood.json           (likelihood of arc-flash by task)
├── table-130-5-G-equipment-table.json      (equipment + clearing-time → hazard category)
├── table-130-5-H-label-requirements.json   (where labels are mandatory)
│
├── table-130-7-C-15-a-ac-tasks.json        (AC table-method PPE category)
├── table-130-7-C-15-b-dc-tasks.json        (DC table-method PPE category)
├── table-130-7-C-15-c-ppe-categories.json  (cal/cm² → PPE 1/2/3/4 thresholds)
├── table-130-7-C-16-ppe-required-items.json (per-category clothing + equipment requirements)
│
├── annex-d-incident-energy-methods.md      (overview + cross-reference to IEEE 1584)
├── annex-d-1-doan-method.json              (DC: P_max + IE formula + enclosure adjustment)
├── annex-d-2-stokes-oppenlander-method.json (DC arc-voltage characteristic empirical)
│
├── annex-h-ppe-guidance.md                 (Annex H: PPE selection guidance)
├── annex-k-general-hazards.md              (Annex K: general hazard categories)
└── annex-l-safeguards.md                   (Annex L: typical safeguards)
```

### 2.3 Shared schemas (3 files — verify existing, create missing)

To validate the structured-data files, we need three shared schemas:

```
shared/schemas/core/
├── standards-formula.schema.json    (required: clause_ref, formula_latex, symbols[], applicable_range, units)
├── standards-table.schema.json      (required: clause_ref, title, column_definitions, rows[])
└── standards-section.schema.json    (required: clause_ref, section_title, summary, key_decisions[])
```

**First task of the implementation plan:** check each path. Any schema already on disk is reused as-is; any absent one is created. Both outcomes (existing/created) must result in all three being present + Draft-07 valid before any IEEE1584 or NFPA70E file is written.

### 2.4 Validation scripts (3 files)

```
shared/validation/standards/
├── standards-clause-check.py            (every .json carries non-empty clause_ref in expected format)
├── standards-cross-reference-check.py   (cross-file symbol + threshold consistency)
└── standards-numerical-sanity.py        (finite coefficients, monotonic ranges, worked-example round-trip ±5%)
```

These run as CI-style checks after every file commit. They are Python (already used in this repo for jsonschema validation) and depend only on standard library + `jsonschema`.

---

## 3. IEEE 1584 content scope (deep)

### 3.1 Core formula files

| File | Content | IEEE 1584:2018 clause |
|---|---|---|
| `method-2018-600V-coefficients.json` | 5 electrode configs × {k1, k2, k3, k4, k5, k6, k7} coefficients (35 numbers) for 208V–600V | §7.2 + Annex C |
| `method-2018-2700V-coefficients.json` | Same shape for 601V–2700V | §7.3 |
| `method-2018-14300V-coefficients.json` | Same shape for 2701V–15kV | §7.4 |
| `intermediate-voltage-interpolation.json` | Logarithmic interpolation rules between voltage classes (for 1000V, 4160V etc.) | §7.4.4 |
| `arc-current-formula.json` | Iarc = f(Vbf, Ibf, G) per voltage class | §6.2 / §6.3 / §6.4 |
| `arc-current-variation-high-low.json` | 0.85×Iarc / 1.0×Iarc bracketing for worst-case identification | §10.2 |
| `incident-energy-formula.json` | E = 12.552/D^x × (k1 + ... + k7×log G + ...) empirical model | §7.5 |
| `boundary-distance-formula.json` | AFB = D × (E/1.2)^(1/x) — derivation + worked example | §8 |

### 3.2 Electrode-configuration files

| File | Configuration | Default equipment |
|---|---|---|
| `electrode-config-VCB-coefficients.json` | Vertical electrodes in Cubic Box | Metal-clad MV switchgear; LV panelboards |
| `electrode-config-VCBB-coefficients.json` | VCB with Barrier | LV switchgear with insulating barrier |
| `electrode-config-HCB-coefficients.json` | Horizontal Cubic Box | Drawout breakers, racked switchgear |
| `electrode-config-VOA-coefficients.json` | Vertical Open Air | Overhead service drops, OH bus |
| `electrode-config-HOA-coefficients.json` | Horizontal Open Air | Substation bus, riser bus |

Each file declares: applicable voltage classes, default gap distance per class, default working distance per class, applicable Ibf range, equipment-classification hints.

### 3.3 Adjustment factors

| File | Adjustment | Clause |
|---|---|---|
| `adjustment-factor-non-standard-gap.json` | Correction when actual gap differs from tabulated | §10.3 |
| `adjustment-factor-non-standard-distance.json` | Working-distance correction | §10.4 |
| `adjustment-factor-enclosure-size.json` | Box-dimension correction (volume effect) | §10.5 |

### 3.4 Legacy methods (compatibility)

| File | Year | Purpose |
|---|---|---|
| `method-2002-lee-formula.json` | 1982/2002 | Ralph Lee's E = 793 × F × V × Ibf × t / D² — theoretical, pre-empirical |
| `method-2002-doughty-neal-formula.json` | 2002 | IEEE 1584:2002 empirical — for reproducing 2002–2018 era labels |

### 3.5 Supporting reference data

| File | Content |
|---|---|
| `voltage-classes.json` | Class breakpoints (208V, 240V, 480V, 600V, 1kV, 2.4kV, 4.16kV, 11kV, 12.47kV, 13.8kV, 15kV) |
| `gap-distance-table.json` | Typical conductor gap per equipment type (Annex C Table A.1) |
| `working-distance-defaults.json` | 455 mm LV / 914 mm MV per equipment type (Annex C Table A.1) |
| `equipment-classification.json` | "Square D NQ panelboard" → VCB, etc. — maps real-world equipment names to electrode-config codes |

### 3.6 Worked examples baked into each formula file

Every formula file carries a `worked_examples[]` array with `input`, `expected_output`, and `source` (e.g. "IEEE 1584:2018 Annex D Example D.1") so the future arc-flash skill has built-in test vectors.

---

## 4. NFPA 70E content scope (deep)

### 4.1 Article 130 section files

| File | Content | Section |
|---|---|---|
| `section-130-2-safe-work-condition.json` | When energized work is permitted; LOTO triggers; permit thresholds | §130.2 |
| `section-130-3-precautions.json` | General precautions near live parts | §130.3 |
| `section-130-4-shock-boundaries.json` | Limited Approach + Restricted Approach definitions | §130.4 |
| `section-130-5-arc-flash-risk-assessment.json` | 9-step risk assessment process | §130.5 |
| `section-130-7-ppe.json` | PPE general requirements + selection rules | §130.7 |

### 4.2 Critical tables (lookup data)

| File | Content | Source |
|---|---|---|
| `table-130-4-C-a-AC-approach.json` | AC shock boundaries by voltage class | Table 130.4(C)(a) |
| `table-130-4-C-b-DC-approach.json` | DC shock boundaries | Table 130.4(C)(b) |
| `table-130-5-C-likelihood.json` | Likelihood of arc-flash by task | Table 130.5(C) |
| `table-130-5-G-equipment-table.json` | Equipment + clearing-time bins → hazard category | Table 130.5(G) |
| `table-130-5-H-label-requirements.json` | Where arc-flash labels are mandatory | Table 130.5(H) |
| `table-130-7-C-15-a-ac-tasks.json` | AC equipment + task → PPE category (table method) | Table 130.7(C)(15)(a) |
| `table-130-7-C-15-b-dc-tasks.json` | DC equipment + task → PPE category | Table 130.7(C)(15)(b) |
| `table-130-7-C-15-c-ppe-categories.json` | cal/cm² thresholds for PPE 1/2/3/4 | Table 130.7(C)(15)(c) |
| `table-130-7-C-16-ppe-required-items.json` | Required clothing + equipment per category | Table 130.7(C)(16) |

PPE-category thresholds (must match exactly):

- **Category 1:** 1.2 – 4 cal/cm² (4 cal AR clothing minimum)
- **Category 2:** 4 – 8 cal/cm² (8 cal AR clothing)
- **Category 3:** 8 – 25 cal/cm² (25 cal AR suit + hood)
- **Category 4:** 25 – 40 cal/cm² (40 cal AR suit + hood)
- **>40 cal/cm²:** Restricted — energized work only by specialised teams per facility risk assessment

### 4.3 Annex D — Incident Energy Calculation Methods (DC focus)

| File | Method | Year | Source |
|---|---|---|---|
| `annex-d-incident-energy-methods.md` | Overview + cross-reference to IEEE 1584 | — | NFPA 70E Annex D |
| `annex-d-1-doan-method.json` | DC: Pmax = Varc × Iarc; IE = Pmax × tarc × 10⁴ / (4π × D²); 1.5× enclosure factor | 2007 | Annex D §D.1 + Doan IEEE-IAS 2007 |
| `annex-d-2-stokes-oppenlander-method.json` | DC arc-voltage: V_arc = (20 + 0.534 × G) × Iarc^0.12 | 1991 | Annex D §D.2 + Stokes & Oppenlander 1991 |

### 4.4 Other annexes (reference)

| File | Content |
|---|---|
| `annex-h-ppe-guidance.md` | NFPA 70E Annex H: PPE selection guidance beyond bare requirements |
| `annex-k-general-hazards.md` | Annex K: general categories of electrical hazards |
| `annex-l-safeguards.md` | Annex L: typical safeguards applied to electrical equipment |

### 4.5 Documentation files

`README.md`, `meta.json`, `terminology.md`, `article-130-overview.md`, `compliance-checklist.md`.

---

## 5. Validation strategy

Standards layers don't have generator/validator/reviewer prompts. Validation is self-consistency + cross-reference integrity, encoded as scripts committed alongside the layers.

### 5.1 JSON Schema validation per file

Every `.json` file must validate against one of three shared schemas:

| File type | Schema | Required fields |
|---|---|---|
| Formula files | `shared/schemas/core/standards-formula.schema.json` | `clause_ref`, `formula_latex`, `symbols[]`, `applicable_range`, `units` |
| Table files | `shared/schemas/core/standards-table.schema.json` | `clause_ref`, `title`, `column_definitions`, `rows[]` |
| Section files | `shared/schemas/core/standards-section.schema.json` | `clause_ref`, `section_title`, `summary`, `key_decisions[]` |

### 5.2 Clause-reference integrity

Every file MUST include `clause_ref` in format `<standard ID> <year>:<section/table>`.

The validation script `shared/validation/standards/standards-clause-check.py` (introduced in §2.4) grep-walks every file and confirms `clause_ref` is non-empty + matches the expected format.

### 5.3 Cross-reference integrity between files

Encoded in `shared/validation/standards/standards-cross-reference-check.py` — verifies:

- Every coefficient file's electrode-config references exist in `electrode-configurations.json` (implicit — derived from individual `electrode-config-*-coefficients.json`)
- `incident-energy-formula.json` symbol references resolve in `arc-current-formula.json`
- `annex-d-1-doan-method.json` arc-voltage symbol resolves in `annex-d-2-stokes-oppenlander-method.json`
- PPE-category thresholds in `table-130-7-C-15-c-ppe-categories.json` match the boundary derivation 1.2 cal/cm² used by IEEE 1584

### 5.4 Numerical sanity checks

`shared/validation/standards/standards-numerical-sanity.py` — verifies:

- Every coefficient is finite (no NaN / null / infinity)
- Every applicable-range is monotonic (`min < max`)
- PPE-category thresholds monotonic (1.2 < 4 < 8 < 25 < 40)
- Worked-example outputs match formula outputs within ±5% (LLM-readable round-trip test)

### 5.5 Worked-example reproducibility

Every formula file carries `worked_examples[]` with:

```json
{
  "input": {"voltage_v": 480, "ibf_a": 25000, "gap_mm": 32, "distance_mm": 455, "tarc_s": 0.2},
  "expected_output": {"iarc_a": 21500, "incident_energy_cal_per_cm2": 6.4, "afb_mm": 1280},
  "source": "IEEE 1584:2018 Annex D Example D.1"
}
```

The numerical-sanity script runs every formula against every worked example and reports drift.

### 5.6 What we do NOT validate

- LLM-style "engineering rationale" — skill's concern, not the layer's
- Conformance to specific arc-flash software vendors
- User-safety claims — these are reference data, not safety advice

---

## 6. How Phase B (the future arc-flash skill) will consume these layers

Forward-looking — documents the consumption contract so file layout is correct *now* for the skill that ships *next sprint*.

### 6.1 Manifest references the skill will declare

When `electrical/arc-flash/skill.manifest.json` is built next sprint, it will reference ~36 specific standards file paths from `IEEE1584/` and `NFPA70E/` (plus the new `calc.arc_flash_incident_energy` contract). This is the consumption-pattern proof we use for every other skill.

### 6.2 The new calc contract (next sprint, not this one)

`shared/calculations/electrical/arc-flash-incident-energy.json` — defines `calc.arc_flash_incident_energy` with inputs:

```
method: ieee1584_2018 | ieee1584_2002 | dc_doan | dc_stokes_oppenlander | nfpa70e_table
voltage_v, bolted_fault_current_a, gap_mm, working_distance_mm, arcing_time_s,
electrode_config, enclosure_size_mm3
```

Outputs:

```
arcing_current_a, incident_energy_cal_per_cm2, arc_flash_boundary_mm,
applied_method, voltage_class_used
```

### 6.3 Per-node arc-flash IR shape (preview)

Each cascade node in the skill's IR will carry an `arc_flash` block with `method_applied`, `voltage_class`, `electrode_config`, `incident_energy_cal_per_cm2`, `arc_flash_boundary_mm`, `working_distance_mm`, `ppe_category`, `ppe_category_source`, `label_recommended`, `label_required_per`, `engineer_override`, `tool_call_pending`.

### 6.4 Cross-skill contracts

| Direction | Intent | Purpose |
|---|---|---|
| Consumes | `fault-level` | Per-node Ik" + ipk + X/R + t_clear for arc-current calc |
| Consumes | `db-layout-rollup` | Equipment type + working-distance + electrode-config hint |
| Produces | `arc-flash` | Per-node IE/AFB/PPE → consumed by future `arc-flash-labelling` skill |

### 6.5 Why this section is in this sprint's spec

Documenting the consumption contract now ensures the standards-layer files are designed with the right field names and right granularity to satisfy the skill. Avoids the pattern-divergence trap we caught mid-build on cable-sizing.

---

## 7. Versioning + maintenance policy

### 7.1 Edition tracking

Both standards revise on cycles: IEEE 1584 ~10-year (next likely 2028); NFPA 70E 3-year (2024 → 2027 → 2030).

**Strategy: edition-pinned content, single source of truth per standard.**

Each layer's `meta.json` carries `edition` (the standard's edition) + `layer_version` (this layer's transcription version).

When a new edition is released, **Option A — in-place update:** the existing folder's content is updated + `edition` bumped + `amendments-summary.md` documents deltas. The consuming arc-flash skill bumps to its v2.0.0.

(Rejected: side-by-side editions — `IEEE1584-2018/` + `IEEE1584-2028/`. Doubles maintenance. Legacy compatibility is already handled via dedicated `method-<year>-*.json` files within the current folder.)

### 7.2 Layer versioning

| Bump | Trigger |
|---|---|
| `layer_version` 1.0.x | Bug fixes — typo in coefficient, mis-cited clause |
| `layer_version` 1.x.0 | Non-breaking additions — new worked example, new annex transcription |
| `layer_version` 2.0.0 | Adoption of a new edition of the source standard |

### 7.3 Audit-trail metadata

Every file's frontmatter carries:

```json
{
  "clause_ref": "IEEE 1584:2018 §7.2 + Annex C Table A.1",
  "transcribed_at": "2026-05-17",
  "transcribed_by": "DraftsMan skills repo",
  "verification_status": "verified-against-source | pending-verification"
}
```

### 7.4 Maintenance triggers

| Trigger | Response | SLA |
|---|---|---|
| New edition released by IEEE/NFPA | Plan layer-update sprint; bump `layer_version` 2.0.0 + `edition` | 6 months |
| Errata published | Patch + push; bump `layer_version` 1.0.x | 1 month |
| Consuming skill finds missing clause | Open `layer-extension` issue; ship in next `layer_version` minor bump | 2 weeks |
| Coefficient mistake discovered | Critical bug: patch + push immediately; log in `amendments-summary.md` | Same-day |

### 7.5 License + reuse

Standards content is © IEEE and NFPA respectively. This repo only stores:

- Clause/section/table references
- Numeric coefficients + thresholds (factual data, not copyrighted expression)
- Brief paraphrase sufficient for an LLM to reason about compliance
- Cross-references between clauses

We do NOT store: full standard text, annex prose verbatim, figures from the standards.

Every `meta.json` carries an explicit `license_note` field.

### 7.6 Future-standard migration: if IEEE 1584.2 (DC arc-flash) is published

For now, DC arc-flash content lives in `NFPA70E/annex-d-*` (where industry references it).

If IEEE PC2 publishes IEEE 1584.2 as a formal DC standard:

1. Create `shared/standards/electrical/IEEE1584-2/` as a new stub
2. Migrate DC content from `NFPA70E/annex-d-*` to the new layer
3. Bump both `NFPA70E/layer_version` (content removed → 2.0.0) and `electrical/arc-flash` skill version (consumes a different layer set → 2.0.0)
4. Cross-reference the migration in both layers' `amendments-summary.md`

---

## 8. Approval

All 7 design sections approved by user (2026-05-17). Ready for implementation plan.

Next step: invoke `superpowers:writing-plans` to produce `docs/superpowers/plans/2026-05-17-arc-flash-standards-layer.md`.

Sprint scope summary: **53 standards files (28 IEEE1584 + 25 NFPA70E) + 3 shared core schemas + 3 validation scripts = 59 files**.
