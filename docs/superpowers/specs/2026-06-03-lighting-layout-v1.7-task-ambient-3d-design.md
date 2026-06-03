# lighting-layout v1.7.0 — Task/Ambient Split + 3D Placement Design Spec

**Date:** 2026-06-03
**Sprint:** D5 (Wave 2 second deliverable of the lighting cluster roadmap)
**Source roadmap:** `docs/superpowers/specs/2026-05-29-lighting-cluster-roadmap.md` §4.1 + §4.2 + §5 (Wave 2)
**Parent sprint patterns:** small-power D4 (30 commits), photometric-analysis v1.0.0 (25 commits), special-locations v1.0.0 (26+3 commits)
**Target version:** lighting-layout 1.6.0 → 1.7.0 (additive minor, backwards-compatible, production stays)

---

## 1. Goal

Add task/ambient illuminance split and 3D luminaire placement to lighting-layout, closing two roadmap gaps:

- **Task/ambient split** (roadmap §4.1) — Separate task-plane illuminance from immediate surrounding (0.5m band, 0.3–0.5× task) and background (≥1/3 task, 50 lx floor) per BS EN 12464-1:2021 §4.2.2.x + Table 6. Currently the IR has a single `target_illuminance_lux` per room.
- **3D placement** (roadmap §4.2) — Add `mount_type` enum + `z_mm` + `suspension_length_mm` to luminaires. Currently luminaires are 2D-only `[id, x_mm, y_mm, zone_id, circuit_id]`. Pendant + suspended luminaires need explicit drop length for ceiling clearance + photometric calc fidelity.

Both ship in one combined sprint (decision §6.1).

## 2. Current state (v1.6.0 — what's already shipped)

- **Versioning context:** lighting-layout was bumped past v1.5.0 by the special-locations sprint (v1.5.0 added INV-12 special-locations cascade) and the photometric-analysis sprint (v1.6.0 added INV-11 photometric cascade). Roadmap's "v1.5.0 extensions" label is historical — this sprint is v1.6.0 → v1.7.0.
- **Zones:** `zones[]` exist but have no `purpose` field; all zones treated equivalently for target lookup.
- **Luminaires:** `[id, x_mm, y_mm, zone_id, circuit_id]` — 2D placement only.
- **Room:** Already has `ceiling_height_mm` + `working_plane_mm` + `hm_mm` (mounting height) at room level — 3D context exists but per-luminaire is flat.
- **calculation_summary:** Single `target_illuminance_lux` + `achieved_illuminance_lux`.
- **Standards file:** `shared/standards/lighting/BSEN12464/lux-levels.json` has BS EN 12464-1:2021 Table 5.3 transcribed (single Em per room type). Table 6 ratios + §4.2.2.x sub-clauses are NOT transcribed.
- **Examples:** 8 production examples (`office-open-plan`, `reception-lobby`, `uk-bathroom-zone-1-zone-2`, `uk-multi-entrance-classroom`, `uk-open-plan-office-10x8-dali`, `uk-part-l-fail-incandescent`, `uk-undersized-lighting-vs-target`, `warehouse-highbay`).
- **Cascades wired:** `photometric-analysis` (INV-11) + `special-locations` (INV-12) both already consumed. INV-11..12 will be preserved unchanged.

## 3. Locked decisions (recorded as the contract)

### 3.1 Scope — combined sprint
Both features (task/ambient split + 3D placement) ship in v1.7.0. Roadmap "minor bump (~2 days)" label is unrealistic; applying D4/photometric precedent the sprint is ~28-35 commits.

### 3.2 3D enforcement — conditional allOf
`mount_type` enum: `[recessed, surface, pendant, suspended, track]`. Default = `recessed`. `z_mm` + `suspension_length_mm` are REQUIRED only when `mount_type ∈ {pendant, suspended}`. Recessed/surface/track luminaires inherit `z_mm = ceiling_height_mm` by convention (no schema field needed). Backwards compatible with all 8 existing examples.

### 3.3 Task split granularity — zone-level purpose enum
`zones[].purpose: enum [task, surrounding, background, circulation]`. Default = `task` for backwards compatibility on existing zones. `zones[].em_target_lux: number ≥ 0` populated per zone (derivable from `room.target_illuminance_lux × ratio_for_purpose` or explicitly supplied).

### 3.4 Standards augmentation — single Em + derived ratios
Augment `shared/standards/lighting/BSEN12464/lux-levels.json` at root with `_surrounding_ratio_default: 0.5`, `_background_ratio_default: 0.33`, `_background_min_lx: 50`, `_ratio_source` citation. Single Em per room type preserved (mirrors BS EN 12464-1:2021 Table 5.3 structure); skill computes per-purpose targets from Em × ratio.

### 3.5 Example budget — 8 retrofit + 4 NEW
Retrofit ALL 8 existing + add 4 NEW examples. Higher coverage than minimum; matches D4 footprint.

### 3.6 Citation pre-work — A.0 transcribes §4.2.2.x + Table 6
A new file `shared/standards/lighting/BSEN12464/area-definitions.json` is authored as Task A.0 transcribing BS EN 12464-1:2021 §4.2.2.1 / §4.2.2.2 / §4.2.2.3 / Table 6. ALL subsequent INV citations cross-check against this file. No INV cites a clause not transcribed in A.0 or pre-existing in `lux-levels.json`.

## 4. Verified citation table (the contract — used to grep banned tokens in plan-template)

**Permitted (will be transcribed by A.0 or already in v1.6.0 verified files):**

| Citation | Transcribed in | Used for |
|---|---|---|
| BS EN 12464-1:2021 §4.2.2.1 | A.0 (new file) | Task area definition (INV-13) |
| BS EN 12464-1:2021 §4.2.2.2 | A.0 (new file) | Surrounding area definition (INV-14) |
| BS EN 12464-1:2021 §4.2.2.3 | A.0 (new file) | Background area definition (INV-15) |
| BS EN 12464-1:2021 Table 5.3 | `lux-levels.json` (existing) | Em per room type (all INVs) |
| BS EN 12464-1:2021 Table 6 | A.0 (new file) | Ratio rules (INV-14, INV-15) |
| Part L 2021 (UK Building Regulations) | preserved from v1.6.0 | Part L efficacy (existing INVs) |
| BS EN 60598-2-x (luminaire standards) | preserved from v1.6.0 | Mount type discipline (INV-16) |

**Banned (inherited + sprint-specific):**

| Banned token | Reason |
|---|---|
| §526.2 | NOT transcribed (carry-over from special-locations + small-power D4 sprints) |
| §433.2 | NOT transcribed (same) |
| OZEV CoP | Wrong name (correct: IET CoP for EV Charging Equipment Installation 4th Edition) |
| 3rd Edition | EV CoP wrong edition |
| Reg 559 | D2.3 lift-diversity misattribution (carry-over) |
| BS EN 12464-1:2021 §4.X for any X NOT in A.0 | Not transcribed |
| "Em_room" / "average room lux" | BS EN 12464-1 deprecates this framing in favour of per-zone Em |

## 5. Schema diff — concrete

### 5.1 `shared/schemas/electrical/lighting-layout-ir.schema.json`

**Additions to `zones[].items.properties`:**
```json
{
  "purpose": {
    "type": "string",
    "enum": ["task", "surrounding", "background", "circulation"],
    "default": "task",
    "description": "BS EN 12464-1:2021 §4.2.2.x area classification."
  },
  "em_target_lux": {
    "type": "number",
    "minimum": 0,
    "description": "Per-zone maintained illuminance target. Derives from Em × ratio per purpose if not explicit."
  }
}
```

**Additions to `luminaires[].items.properties`:**
```json
{
  "mount_type": {
    "type": "string",
    "enum": ["recessed", "surface", "pendant", "suspended", "track"],
    "default": "recessed"
  },
  "z_mm": {
    "type": "integer",
    "minimum": 0,
    "description": "Height of luminaire emission plane above finished floor."
  },
  "suspension_length_mm": {
    "type": "integer",
    "minimum": 0,
    "description": "Drop length from ceiling for pendant/suspended mount."
  }
}
```

**Additions to `calculation_summary.properties`:**
```json
{
  "per_zone_achieved": {
    "type": "array",
    "items": {
      "type": "object",
      "properties": {
        "zone_id": {"type": "string"},
        "purpose": {"type": "string", "enum": ["task", "surrounding", "background", "circulation"]},
        "em_target_lux": {"type": "number", "minimum": 0},
        "em_achieved_lux": {"type": "number", "minimum": 0},
        "ratio_compliance": {"type": "string", "enum": ["pass", "fail", "marginal"]}
      },
      "required": ["zone_id", "purpose", "em_target_lux", "em_achieved_lux", "ratio_compliance"],
      "additionalProperties": false
    }
  }
}
```

**3 new `allOf` clauses on root schema:**
1. `if luminaires[].mount_type ∈ {pendant, suspended}` → require `z_mm` + `suspension_length_mm`.
2. `if luminaires[].mount_type = pendant` → require `z_mm + suspension_length_mm == ceiling_height_mm` (consistency).
3. `if any zones[].purpose = surrounding` → require at least one `zones[].purpose = task` to coexist.

### 5.2 `shared/standards/lighting/BSEN12464/lux-levels.json`

Augment root object with:
```json
{
  "_surrounding_ratio_default": 0.5,
  "_background_ratio_default": 0.33,
  "_background_min_lx": 50,
  "_ratio_source": "BS EN 12464-1:2021 §4.2.2.2 + §4.2.2.3 + Table 6"
}
```

Existing per-room-type `em` / `ugr_max` / `ra_min` values unchanged.

### 5.3 New file: `shared/standards/lighting/BSEN12464/area-definitions.json`

Transcribes BS EN 12464-1:2021 §4.2.2.1 (task area), §4.2.2.2 (immediate surrounding, 0.5m band), §4.2.2.3 (background area), Table 6 (ratio rules). Used by INV-14/15 evidence + reviewer judgement calls. Companion reference `shared/standards/lighting/BSEN12464/area-definitions-reference.md`.

## 6. New INVs (INV-13..19; 6 HIGH + 1 MEDIUM)

| # | INV | Severity | Checks | Cites |
|---|---|---|---|---|
| INV-13 | Zone purpose required + valid | HIGH | Every zone has `purpose ∈ enum`; orphan `surrounding` blocked (must coexist with `task`) | §4.2.2.1/2/3 (A.0) |
| INV-14 | Surrounding ratio compliance | HIGH | `purpose=surrounding` zones have `em_target_lux ∈ [0.3 × task_em, 0.5 × task_em]` | Table 6 (A.0) |
| INV-15 | Background floor | HIGH | `purpose=background` zones have `em_target_lux ≥ max(task_em / 3, 50 lx)` | §4.2.2.3 + Table 6 (A.0) |
| INV-16 | mount_type ↔ z_mm/suspension consistency | HIGH | pendant/suspended → both `z_mm` + `suspension_length_mm` present; pendant satisfies `z_mm + suspension_length_mm = ceiling_height_mm` | BS EN 60598-2 (existing) |
| INV-17 | Ceiling clearance | HIGH | `z_mm + suspension_length_mm ≤ ceiling_height_mm` AND `z_mm > working_plane_mm` (no luminaire below task plane) | BS EN 60598-2 (existing) |
| INV-18 | hm_mm derived correctly | MEDIUM | `room.hm_mm` reconciles with luminaire z: pendant uses `z_mm - working_plane_mm`; recessed uses `ceiling_height_mm - working_plane_mm` | derived geometry |
| INV-19 | Per-zone achievement | HIGH | `per_zone_achieved[].em_achieved_lux ≥ em_target_lux` OR `non_compliance_flag` emitted with severity matching gap (≥25% short = HIGH; 10-25% = MEDIUM; <10% = INFO marginal) | BS EN 12464-1:2021 §4.1 (top-level) |

## 7. Prompt extensions

### 7.1 generator.md — new Steps 13/14/15

- **Step 13: Zone purpose resolution** — engineer declares `purpose` per zone OR generator defaults to `task` for backwards compat; `em_target_lux` derived from Table 5 × Table 6 ratio per purpose; populate per-zone target list.
- **Step 14: Mount type + 3D placement** — pick `mount_type` from drawing/specification; populate `z_mm` + `suspension_length_mm` when pendant/suspended; cross-check ceiling clearance + working plane (INV-16/17 prep).
- **Step 15: Per-zone achievement summary** — populate `calculation_summary.per_zone_achieved[]` from photometric cascade payload (INV-11) OR mark `pending_photometric_grid` with honest disclosure.

### 7.2 validator.md — new INV sections

7 sections appended (one per INV-13..19) with verbatim A.0-transcribed citations + structured checks + evidence template (20-1200 chars maintained from `[[feedback-no-trim-non-consequential]]`).

### 7.3 reviewer.md — new D-checks (D-11/12/13)

- **D-11**: Suspension length judgement — pendant drop sensible for ceiling + room scale (flag drops >2m or <100mm as edge cases)
- **D-12**: Background-only rooms — flag rooms with only `background` zones (no `task` zones) as suspicious unless explicitly `circulation`
- **D-13**: Task-zone density — flag rooms where >70% of floor is `task` purpose (typically overdense; surrounding/background expected)

## 8. Examples (8 retrofit + 4 NEW = 12 total)

### 8.1 Retrofit (8 — additive, default values preserve behaviour)

| Example | Edits |
|---|---|
| office-open-plan | `purpose: task` on existing zones; `mount_type: recessed`; populate `per_zone_achieved[]` |
| reception-lobby | `purpose: circulation`; `mount_type: recessed` |
| uk-bathroom-zone-1-zone-2 | `purpose: task` (vanity) + `circulation` (entry); recessed; cascade to special-locations preserved |
| uk-multi-entrance-classroom | `purpose: task` (desks) + `circulation` (aisles); recessed |
| uk-open-plan-office-10x8-dali | `purpose: task` on desk zones + `surrounding` on perimeter; recessed; DALI preserved |
| uk-part-l-fail-incandescent | `purpose: task`; recessed; Part-L failure preserved |
| uk-undersized-lighting-vs-target | `purpose: task`; recessed; existing FAIL preserved + add per-zone INV-19 surface |
| warehouse-highbay | `purpose: task` (pick face) + `circulation` (aisles); `mount_type: suspended` (highbay pendant) — first 3D-placement retrofit; suspension_length_mm derived from existing hm_mm |

### 8.2 NEW (4)

1. **`uk-pendant-open-plan-office`** — 12×8m, ceiling 3500mm, pendant LEDs with 800mm suspension (z_mm=2700, working_plane=750, hm=1950). Exercises INV-16/17/18 PASS. `mount_type: pendant`.
2. **`uk-mixed-purpose-classroom`** — task zones (student desks Em=300lx) + surrounding zone (teacher desk + side band Em=200lx = 0.66×task → INV-14 PASS within ratio) + background (back wall display = 100lx = 1/3×task → INV-15 PASS); recessed.
3. **`uk-retail-display-task-zone`** — high-emphasis goods Em=1000lx task zone + general circulation Em=300lx; pendant accent + recessed downlights mixed; exercises mount_type heterogeneity.
4. **`uk-per-zone-target-violation`** **FAIL HIGH** — task zone with em_target=500lx but `per_zone_achieved.em_achieved=380lx` (24% short); INV-19 fires HIGH; `non_compliance_flag` HIGH; `compliant=false` by design.

## 9. Evals (5 new YAML)

| Eval | Skill check | Severity |
|---|---|---|
| `eval-XX-zone-purpose-emit.yaml` | INV-13 PASS across retrofits + NEW#2 | warning |
| `eval-XX-task-surrounding-ratio.yaml` | INV-14 ratio compliance on NEW#2 + NEW#3 | warning |
| `eval-XX-mount-type-3d-consistency.yaml` | INV-16/17/18 on NEW#1 + warehouse-highbay retrofit | warning |
| `eval-XX-per-zone-achievement-pass.yaml` | INV-19 PASS on retrofits + NEW#1/2/3 | info |
| `eval-XX-per-zone-achievement-fail.yaml` | INV-19 FAIL HIGH on NEW#4 | critical |

## 10. Cascade impact

**photometric-analysis cascade (INV-11)** — unchanged. Photometric consumes luminaire positions + room geometry for point-grid solving; doesn't consume `zone.purpose`. Per-zone achieved values are computed by lighting-layout from the photometric grid output + zone polygons (lighting-layout-side enrichment).

**special-locations cascade (INV-12)** — unchanged. Special-locations consumes room geometry + zone polygons; doesn't consume `purpose` or `mount_type`.

**Downstream consumers** — schema additions are additive; no consumer-side `version_constraint` changes needed. A.5 pre-merge check confirms no consumer pins `lighting-layout ^1.6` that would break on v1.7.

## 11. Sprint structure

**Phase A — Foundations (6 tasks, mix Opus + Sonnet)**
- A.0 *(Opus)* — Transcribe §4.2.2.x + Table 6 → `area-definitions.json` + reference markdown.
- A.1 *(Sonnet)* — IR schema additions: zones[].purpose + em_target_lux + luminaires[].mount_type + z_mm + suspension_length_mm + per_zone_achieved[] + 3 allOf clauses. Verify `invariants[].evidence.maxLength: 1200`.
- A.2 *(Sonnet)* — `inputs.json` D5 additions: zone purpose + mount_type + suspension_length item taxonomies.
- A.3 *(Sonnet)* — `lux-levels.json` augmentation: ratio defaults + citation.
- A.4 *(Sonnet)* — Rules YAML: `zone-purpose-rules.yaml` (5 ZP-NN) + `mount-type-rules.yaml` (4 MT-NN).
- A.5 *(Sonnet)* — Manifest bump 1.6.0 → 1.7.0 + pre-merge consumer check.

**Phase B — Prompts (4 tasks, all Opus)**
- B.1 — `generator.md`: Steps 13/14/15.
- B.2 — `validator.md`: 7 new INV sections.
- B.3 — `reviewer.md`: 3 new D-checks (D-11/12/13).
- B.4 — Cascade-prereq enumeration.

**Phase C — Examples + Evals (13 tasks)**
- C.1-C.8 *(Opus)* — 8 retrofits.
- C.9 *(Opus)* — NEW uk-pendant-open-plan-office.
- C.10 *(Opus)* — NEW uk-mixed-purpose-classroom.
- C.11 *(Opus)* — NEW uk-retail-display-task-zone.
- C.12 *(Opus)* — NEW uk-per-zone-target-violation FAIL HIGH.
- C.13 *(Sonnet)* — 5 new evals YAML.

**Phase D — Ship (5 tasks)**
- D.1 *(Sonnet)* — Honest disclosure 4-place sweep across 12 examples.
- D.2 *(Sonnet)* — 11-check verification fence.
- D.3 *(Sonnet)* — 2 CHANGELOGs + memory file + MEMORY.md + CLAUDE.md tally bump.
- D.4 *(Opus)* — Final cross-sprint integration review.
- D.5 — Push deferred to user authorization.

**Estimated commits:** ~28 implementer + ~5-7 fix-passes + 5 spec/plan/portion commits = **~40 commits**

## 12. Risk surfaces (acknowledged at brainstorm)

1. **Photometric cascade INV-11** may need a light touch if `per_zone_achieved[]` requires zone polygon access that photometric doesn't currently surface — flag at B.4; dispatch fix-pass if so.
2. **warehouse-highbay retrofit** is the only existing example needing 3D placement migration (mount_type: suspended) — non-trivial. Budget extra time for that C task.
3. **NEW#2 mixed-purpose-classroom** exercises all 3 zone purposes (task + surrounding + background) in one room — most complex single example; needs careful per-zone ratio math.

## 13. Process discipline (locked from day one)

- **Citation hygiene:** every BS EN 12464-1 sub-clause in every plan-template cross-checked against `shared/standards/lighting/BSEN12464/` BEFORE plan ships. A.0 transcription anchors this.
- **No-trim discipline** per `[[feedback-no-trim-non-consequential]]`: evidence/decision content stays full-length; raise maxLength caps if needed, do NOT trim engineering content.
- **No Haiku** per `[[feedback-no-haiku-sonnet-opus-only]]`: Sonnet for mechanical / Opus for judgment.
- **Per-task two-stage Opus review** + fix-pass commits (D2/D3/D4 precedent: 5-10 fix-pass commits expected).
- **Pre-ship Sonnet 11-check fence** at D.2.
- **Final cross-sprint Opus integration review** at D.4 with adversarial verdict.
- **Push deferred to user authorization** per CLAUDE.md shared-state rule.
- **Honest disclosure 4-place pattern** held across all 12 examples.

## 14. Definition of done

- 12 examples pass IR schema (Pass 1).
- 5 new evals pass eval.schema.json (Pass 2).
- inputs.json passes inputs.schema.json (Pass 3).
- All 19 INVs (existing 12 + new 7) emit on every D5 example with N/A-vacuous PASS for unused INVs.
- Manifest v1.7.0 + status production + evals[]/examples[]/rules[] declared.
- 2 CHANGELOGs (lighting-layout + lux-levels-standards entry note).
- Memory file `sprint-D5-lighting-layout-shipped.md` saved + MEMORY.md index updated.
- CLAUDE.md tally bumped.
- 1 disclosed FP held (motor-superposition oracle) — no new FPs introduced.
- Golden CI gate aggregate green.
- Final integration review verdict: SHIP or SHIP-WITH-NOTED-CONCERNS (not FIX-FIRST).
- Push to `origin/main` only after user authorization.
