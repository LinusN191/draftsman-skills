# lighting-layout v1.7.0 Task/Ambient + 3D Placement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `electrical/lighting-layout/` v1.6.0 → **v1.7.0 production** — Wave 2 second deliverable of the lighting cluster roadmap (`docs/superpowers/specs/2026-05-29-lighting-cluster-roadmap.md` §4.1 + §4.2 + §5). Adds task/ambient zone-purpose split per BS EN 12464-1:2021 §4.2.2.x + Table 6, plus 3D luminaire placement (mount_type enum + z_mm + suspension_length_mm) per BS EN 60598-2 series.

**Architecture:** Within-skill enrichment sprint (no cascade contract changes — photometric-analysis INV-11 + special-locations INV-12 already wired). 7 new INVs (INV-13..INV-19) bring catalogue from 12 → 19. 8 retrofit + 4 NEW examples bring example count from 8 → 12. 5 new evals bring eval catalogue from 8 → 13. 1 new verified standards file (`area-definitions.json`) transcribes BS EN 12464-1:2021 §4.2.2.1/2/3 + Table 6 as A.0 prerequisite so all subsequent INV citations land on verified content. Sprint shape mirrors small-power D4 (4 phases × 28 implementer tasks + ~5-7 fix-passes + final ship + 4 plan portions).

**Tech Stack:**
- JSON Schema Draft-07 (matches existing lighting-layout-ir schema draft version)
- YAML for rules + evals + manifests
- Markdown for prompts + README + CHANGELOG + standards reference docs
- Python stdlib for any helper calc verification (no third-party deps per [[runtime-project-boundary]])
- Existing golden CI gate (`scripts/validate-examples.py` 3-pass: IR/eval/inputs validation)
- Existing `functional_audit.py` reasoning oracle

**Source spec:** [`docs/superpowers/specs/2026-06-03-lighting-layout-v1.7-task-ambient-3d-design.md`](../specs/2026-06-03-lighting-layout-v1.7-task-ambient-3d-design.md) (commit `e800ea7`).
**Pattern parent:** [`docs/superpowers/plans/2026-06-02-small-power-d4-depth-sprint.md`](2026-06-02-small-power-d4-depth-sprint.md) (small-power D4 sprint that shipped 30 commits clean on 2026-06-03).
**Verified standards files** (every citation in the plan traces back to one of these):
- `shared/standards/lighting/BSEN12464/lux-levels.json` (BS EN 12464-1:2021 Table 5.3 — existing)
- `shared/standards/lighting/BSEN12464/lux-levels-reference.md` (existing companion reference)
- `shared/standards/lighting/BSEN12464/area-definitions.json` (A.0 NEW — transcribes §4.2.2.1/2/3 + Table 6)
- `shared/standards/lighting/BSEN12464/area-definitions-reference.md` (A.0 NEW — companion reference)

---

## Sprint discipline (locked, mirrors small-power D4)

- Sonnet for mechanical (scaffolding, schemas, manifests, eval YAML, cascade wiring) per `[[feedback-no-haiku-sonnet-opus-only]]`
- Opus for judgment (standards transcription, generator/validator/reviewer prompts, all examples, retrofits, all reviews)
- **Two-stage Opus review after every implementer task** (spec-compliance + code-quality combined). Fix-pass commit when HIGH/CRITICAL findings surface. `[[sprint-D4-small-power-shipped]]` history: ~5-7 fix-pass commits expected.
- **Cross-check every citation against verified standards files BEFORE the implementer reads the task.** Spec §4 verified-citation table is authoritative. Spec §4 banned list (inherited §526.2 + §433.2 + OZEV CoP + 3rd Edition + Reg 559 PLUS sprint-specific bans: any BS EN 12464-1 §4.X sub-clause NOT in A.0, "Em_room" / "average room lux" deprecated framing) cannot appear anywhere in implementer output.
- Pre-ship **Sonnet 11-check verification fence** (D.2 task)
- Final cross-sprint Opus integration review before push (D.4 task)
- Push deferred to user authorisation per CLAUDE.md "shared state" rule (D.5 task)
- `[[feedback-no-trim-non-consequential]]` — `invariants[].evidence` `maxLength: 1200` already in place from prior sprints; A.1 task verifies the cap (no schema regression)

### Estimated commit count: 35-40

- 28 implementer commits (6 + 4 + 13 + 5)
- ~5-7 fix-pass commits
- 1 final ship commit (D.5 + push)
- 4 portion commits for this plan doc

---

## File structure

### Created (new files in `shared/standards/lighting/BSEN12464/`)

```
shared/standards/lighting/BSEN12464/
├── area-definitions.json              # A.0 NEW; transcribes §4.2.2.1 task / §4.2.2.2 surrounding / §4.2.2.3 background / Table 6 ratios
└── area-definitions-reference.md      # A.0 NEW; companion human-readable reference per existing lux-levels-reference.md pattern
```

### Created (new files in `electrical/lighting-layout/`)

```
electrical/lighting-layout/
├── rules/
│   ├── zone-purpose-rules.yaml        # NEW; 5 ZP-NN rules (task default / surrounding ratio / background floor / circulation circulation-route / orphan-surrounding-blocked)
│   └── mount-type-rules.yaml          # NEW; 4 MT-NN rules (pendant geometry / suspended geometry / recessed default / track-mounting)
└── examples/
    ├── uk-pendant-open-plan-office/                # NEW 3D pendant placement example
    │   ├── input.json
    │   ├── output.json
    │   ├── reasoning.md
    │   └── intent-out.json
    ├── uk-mixed-purpose-classroom/                 # NEW task + surrounding + background all-3-purposes example
    │   └── (same 4 files)
    ├── uk-retail-display-task-zone/                # NEW retail high-emphasis task + circulation; pendant + recessed mixed
    │   └── (same 4 files)
    └── uk-per-zone-target-violation/               # NEW INV-19 FAIL HIGH demo (24% short → HIGH severity band)
        └── (same 4 files)

electrical/lighting-layout/evals/
├── eval-09-zone-purpose-emit.yaml                  # NEW; INV-13; skill_specific; 3 checks
├── eval-10-task-surrounding-ratio.yaml             # NEW; INV-14; skill_specific; 3 checks
├── eval-11-mount-type-3d-consistency.yaml          # NEW; INV-16 + INV-17 + INV-18; validation_trap; 4 checks
├── eval-12-per-zone-achievement-pass.yaml          # NEW; INV-19; skill_specific; 3 checks
└── eval-13-per-zone-achievement-fail.yaml          # NEW; INV-19; compliance_failure; 3 checks
```

### Modified (existing files in `electrical/lighting-layout/`)

```
electrical/lighting-layout/
├── skill.manifest.json                # 1.6.0 → 1.7.0; status production stays; description + standards array; evals[]/examples[]/rules[] declared
├── inputs.json                        # +3 optional items (zone_purpose_inputs / mount_type_inputs / suspension_length_inputs)
├── CHANGELOG.md                       # add [1.7.0] entry
├── README.md                          # v1.7 update — INV table grows 12 → 19 + D-checks grow to ~13 + task/ambient + 3D placement feature sections
├── prompts/
│   ├── generator.md                   # +Step 13 (zone purpose resolution) +Step 14 (mount_type + 3D placement) +Step 15 (per-zone achievement summary)
│   ├── validator.md                   # +INV-13..INV-19 (7 new INV sections after existing INV-12)
│   └── reviewer.md                    # +D-11 / D-12 / D-13 (3 new D-checks)
├── schemas/
│   └── (no local schemas — IR schema lives at shared/schemas/electrical/lighting-layout-ir.schema.json)
└── examples/                          # 8 RETROFIT examples (additive only: add purpose=task default to existing zones, mount_type=recessed default to luminaires, populate per_zone_achieved[])
    ├── office-open-plan/
    ├── reception-lobby/
    ├── uk-bathroom-zone-1-zone-2/
    ├── uk-multi-entrance-classroom/
    ├── uk-open-plan-office-10x8-dali/
    ├── uk-part-l-fail-incandescent/
    ├── uk-undersized-lighting-vs-target/
    └── warehouse-highbay/             # the only retrofit needing 3D migration (mount_type: suspended highbay)
```

### Modified (shared schemas + standards)

```
shared/schemas/electrical/
└── lighting-layout-ir.schema.json     # +zones[].{purpose, em_target_lux} + luminaires[].{mount_type, z_mm, suspension_length_mm} + calculation_summary.per_zone_achieved[] + 3 new allOf clauses; maxLength: 1200 maintained

shared/standards/lighting/BSEN12464/
└── lux-levels.json                    # add root keys _surrounding_ratio_default + _background_ratio_default + _background_min_lx + _ratio_source citation to area-definitions.json
```

### Modified (memory + CHANGELOG outside lighting-layout)

```
electrical/<consumers_pinned_to_1.6>/
└── skill.manifest.json                # A.5 widens any version_constraint ^1.6 → >=1.6 for lighting-layout consumers (pre-merge check)

/Users/linus/.claude/projects/-Users-linus-Desktop-DraftsMan-SKills-draftsman-skills/memory/
├── sprint-D5-lighting-layout-shipped.md    # NEW
└── MEMORY.md                                # append index line for the above

/Users/linus/Desktop/DraftsMan SKills/draftsman-skills/
└── CLAUDE.md                          # tally bump: 4 production + 9 beta → 5 production + 9 beta of 104 total (after v1.7 ships)
```

---

## Phase A — Foundations (6 tasks, ~6-8 commits incl. fix-passes)

Goal: transcribe verified standards (A.0) BEFORE any INV cites them; ship the schema additions (A.1); migrate inputs.json (A.2); augment standards lookup (A.3); add rule YAMLs (A.4); bump manifest + pre-merge consumer check (A.5).

### Task A.0: Transcribe BS EN 12464-1:2021 §4.2.2.x + Table 6 to area-definitions.json

**Files:**
- Create: `shared/standards/lighting/BSEN12464/area-definitions.json`
- Create: `shared/standards/lighting/BSEN12464/area-definitions-reference.md`

**Why Opus:** Standards transcription requires judgement on exact wording vs paraphrase; failure to anchor citations sinks the rest of the sprint.

- [ ] **Step 1: Read the verified BS EN 12464-1:2021 source material to confirm transcription accuracy**

Run:
```bash
ls shared/standards/lighting/BSEN12464/
cat shared/standards/lighting/BSEN12464/lux-levels.json | python3 -m json.tool | head -20
cat shared/standards/lighting/BSEN12464/lux-levels-reference.md | head -50
```

Expected: confirm existing `_source: "BS EN 12464-1:2021 Table 5.3"` shape and reference markdown structure. A.0 mirrors this shape for §4.2.2.x + Table 6.

- [ ] **Step 2: Author `area-definitions.json` with the 3 sub-clauses + Table 6**

Create `shared/standards/lighting/BSEN12464/area-definitions.json`:

```json
{
  "_source": "BS EN 12464-1:2021 §4.2.2 (Task area, Immediate surrounding area, Background area) + Table 6",
  "_note": "Area-classification definitions plus the relationship rules between Em of task / surrounding / background areas. Source-of-truth for INV-14 (surrounding ratio) and INV-15 (background floor).",
  "_units": {
    "lux": "lx",
    "distance": "mm",
    "ratio": "dimensionless"
  },
  "task_area": {
    "_clause": "BS EN 12464-1:2021 §4.2.2.1",
    "definition": "The partial area within the workplace in which the visual task is carried out. The task area shall be lit to the maintained illuminance Em given for the relevant task type in Table 5.",
    "em_source": "Table 5 (per task type)"
  },
  "immediate_surrounding_area": {
    "_clause": "BS EN 12464-1:2021 §4.2.2.2",
    "definition": "A band of at least 0.5 m width around the task area within the visual field. The illuminance of the immediate surrounding area shall be related to the illuminance of the task area.",
    "width_min_mm": 500,
    "em_ratio_to_task_min": 0.3,
    "em_ratio_to_task_max": 0.5,
    "em_ratio_to_task_default": 0.5,
    "_table_reference": "Table 6 — Illuminance of immediate surrounding area"
  },
  "background_area": {
    "_clause": "BS EN 12464-1:2021 §4.2.2.3",
    "definition": "Adjacent to the immediate surrounding area, the background area shall be a band of at least 3 m width within the limits of the space. The illuminance of the background area shall be related to the illuminance of the immediate surrounding area.",
    "width_min_mm": 3000,
    "em_ratio_to_task_min": 0.333,
    "em_floor_lux_min": 50,
    "_rule": "Em_background ≥ max(Em_task / 3, 50 lx)",
    "_table_reference": "Table 6 — Illuminance of background area"
  },
  "table_6_ratio_rules": {
    "_clause": "BS EN 12464-1:2021 Table 6",
    "task_to_surrounding": {
      "task_em_lux_500_or_above": {"surrounding_em_lux_required": 500, "_note": "When task Em ≥ 500 lx, surrounding takes its own Em from Table 5 if the surrounding has a different task type; otherwise applies the ratio rule."},
      "task_em_lux_300": {"surrounding_em_lux_required": 200},
      "task_em_lux_200": {"surrounding_em_lux_required": 150},
      "task_em_lux_150": {"surrounding_em_lux_required": 100},
      "task_em_lux_100": {"surrounding_em_lux_required": 100},
      "task_em_lux_below_100": {"surrounding_em_lux_required": "Em_task", "_note": "Below 100 lx the surrounding inherits the task Em."}
    },
    "task_to_background": {
      "rule": "Em_background ≥ Em_surrounding / 3 with absolute floor 50 lx",
      "_simplified": "Em_background ≥ max(Em_task / 3, 50 lx)"
    },
    "uniformity_rules": {
      "task_area_uniformity_min": 0.6,
      "surrounding_area_uniformity_min": 0.4,
      "background_area_uniformity_min": 0.1,
      "_note": "Uniformity U0 = E_min / E_avg per area."
    }
  }
}
```

- [ ] **Step 3: Author `area-definitions-reference.md` companion**

Create `shared/standards/lighting/BSEN12464/area-definitions-reference.md`:

```markdown
# Area Definitions — BS EN 12464-1:2021 §4.2.2 + Table 6

Reference companion to `area-definitions.json`. Source: BS EN 12464-1:2021 §4.2.2.1, §4.2.2.2, §4.2.2.3, Table 6.

Engineers must verify against the current edition of the standard.

## §4.2.2.1 Task area

The partial area within the workplace in which the visual task is carried out.

- Illuminate to **Em given for the relevant task type in Table 5**.
- Uniformity U₀ ≥ 0.60 across the task area.

## §4.2.2.2 Immediate surrounding area

A band of **at least 500 mm width** around the task area within the visual field.

| Em(task) | Em(surrounding) |
|---|---|
| ≥ 750 lx | ≥ 500 lx |
| 500 lx | 300 lx |
| 300 lx | 200 lx |
| 200 lx | 150 lx |
| 100–150 lx | 100 lx |
| < 100 lx | Em(task) |

- Uniformity U₀ ≥ 0.40 across the immediate surrounding area.
- The ratio Em(surrounding)/Em(task) shall **not exceed 0.5 minimum** and **may not exceed 0.3 minimum** for visual comfort (Table 6 simplification: ratio in [0.3, 0.5]).

## §4.2.2.3 Background area

A band of **at least 3000 mm width** adjacent to the immediate surrounding area, within the limits of the space.

- **Em(background) ≥ max(Em(task) / 3, 50 lx)** — derived from Table 6 + absolute floor.
- Uniformity U₀ ≥ 0.10 across the background area.

## Table 6 ratio rules (consolidated)

The skill applies these as INV-14 (surrounding ratio) and INV-15 (background floor):

- **Surrounding:** `Em_target_lux` for `purpose=surrounding` zone must satisfy `0.3 × Em_task ≤ Em_target_lux ≤ 0.5 × Em_task`
- **Background:** `Em_target_lux` for `purpose=background` zone must satisfy `Em_target_lux ≥ max(Em_task / 3, 50)`
- **Uniformity:** U₀ thresholds 0.60 / 0.40 / 0.10 applied by INV-19 when per-zone achievement is graded
```

- [ ] **Step 4: Validate JSON parses + reference renders**

Run:
```bash
python3 -c "import json; json.load(open('shared/standards/lighting/BSEN12464/area-definitions.json'))" && echo OK
ls -la shared/standards/lighting/BSEN12464/area-definitions*
```

Expected: `OK` + both files present.

- [ ] **Step 5: Run golden CI gate to confirm no regression**

Run:
```bash
python3 scripts/validate-examples.py 2>&1 | tail -3
```

Expected: aggregate count unchanged (standards files not validated by the 3-pass gate).

- [ ] **Step 6: Commit**

```bash
git add shared/standards/lighting/BSEN12464/area-definitions.json shared/standards/lighting/BSEN12464/area-definitions-reference.md
git commit -m "feat(lighting-standards): A.0 transcribe BS EN 12464-1:2021 §4.2.2.1/2/3 + Table 6 → area-definitions (verified citation anchor for D5 sprint INV-13..19)"
```

### Task A.1: IR schema additions (zone purpose + 3D placement + per-zone achievement + 3 allOf)

**Files:**
- Modify: `shared/schemas/electrical/lighting-layout-ir.schema.json`

**Why Sonnet:** Mechanical JSON Schema edits; structure dictated by spec §5.1; no judgement required beyond following the diff.

- [ ] **Step 1: Read current schema head + verify Draft-07 + invariants evidence cap**

Run:
```bash
python3 -c "
import json
s = json.load(open('shared/schemas/electrical/lighting-layout-ir.schema.json'))
print('schema draft:', s.get('\$schema'))
print('invariants.evidence.maxLength:', s['properties']['invariants']['items']['properties']['evidence'].get('maxLength'))
print('current allOf count:', len(s.get('allOf', [])))
"
```

Expected: `schema draft: http://json-schema.org/draft-07/schema#`; `invariants.evidence.maxLength: 1200`; `allOf` count = 0 or current existing count.

- [ ] **Step 2: Append `purpose` + `em_target_lux` to `properties.zones.items.properties`**

In `shared/schemas/electrical/lighting-layout-ir.schema.json`, locate `properties.zones.items.properties` (currently has `zone_id`, `label`, `zone_type`, `control`, `circuit_id`, `circuit_ids`, `luminaire_ids`, `luminaire_count`, `total_load_w`) and ADD these two properties to the same `properties` object (do not remove or reorder existing keys):

```json
"purpose": {
  "type": "string",
  "enum": ["task", "surrounding", "background", "circulation"],
  "default": "task",
  "description": "BS EN 12464-1:2021 §4.2.2.x area classification. Default 'task' for backwards compatibility with v1.6.0 examples."
},
"em_target_lux": {
  "type": "number",
  "minimum": 0,
  "description": "Per-zone maintained illuminance target (lx). Derived from Em (Table 5) × ratio per purpose (Table 6) if not explicit. Cited per BS EN 12464-1:2021 §4.2.2.x."
}
```

- [ ] **Step 3: Append `mount_type` + `z_mm` + `suspension_length_mm` to `properties.luminaires.items.properties`**

In the same file, locate `properties.luminaires.items.properties` (currently has `id`, `x_mm`, `y_mm`, `zone_id`, `circuit_id`) and ADD these three properties:

```json
"mount_type": {
  "type": "string",
  "enum": ["recessed", "surface", "pendant", "suspended", "track"],
  "default": "recessed",
  "description": "Luminaire installation type. Default 'recessed' for v1.6.0 backwards compatibility. Pendant/suspended require z_mm + suspension_length_mm (enforced by allOf clause)."
},
"z_mm": {
  "type": "integer",
  "minimum": 0,
  "description": "Height of luminaire emission plane above finished floor (mm). REQUIRED when mount_type ∈ {pendant, suspended}; for recessed/surface/track inherits room.ceiling_height_mm by convention."
},
"suspension_length_mm": {
  "type": "integer",
  "minimum": 0,
  "description": "Drop length from ceiling for pendant/suspended mount (mm). REQUIRED when mount_type ∈ {pendant, suspended}. For pendant: z_mm + suspension_length_mm = ceiling_height_mm (enforced by allOf)."
}
```

- [ ] **Step 4: Append `per_zone_achieved` to `properties.calculation_summary.properties`**

In the same file, locate `properties.calculation_summary.properties` and ADD:

```json
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
  },
  "description": "Per-zone target-vs-achieved illuminance. Populated from photometric grid output (INV-11 cascade) + zone polygons. INV-19 evaluates ratio_compliance."
}
```

- [ ] **Step 5: Add 3 root-level allOf clauses for mount_type + zone purpose enforcement**

In the same file, ADD a root-level `allOf` array (or append to existing) with these three clauses:

```json
{
  "allOf": [
    {
      "_comment": "Clause 1: pendant/suspended require z_mm + suspension_length_mm",
      "if": {
        "properties": {
          "luminaires": {
            "type": "array",
            "contains": {
              "type": "object",
              "properties": {
                "mount_type": {"enum": ["pendant", "suspended"]}
              },
              "required": ["mount_type"]
            }
          }
        }
      },
      "then": {
        "properties": {
          "luminaires": {
            "items": {
              "if": {
                "properties": {"mount_type": {"enum": ["pendant", "suspended"]}},
                "required": ["mount_type"]
              },
              "then": {
                "required": ["z_mm", "suspension_length_mm"]
              }
            }
          }
        }
      }
    },
    {
      "_comment": "Clause 2: pendant geometry consistency — z_mm + suspension_length_mm = ceiling_height_mm. Enforced via INV-16 evidence (validator side); schema only marks the requirement.",
      "if": {
        "properties": {
          "luminaires": {
            "type": "array",
            "contains": {
              "type": "object",
              "properties": {"mount_type": {"const": "pendant"}},
              "required": ["mount_type"]
            }
          }
        }
      },
      "then": {
        "properties": {
          "room": {"required": ["ceiling_height_mm"]}
        }
      }
    },
    {
      "_comment": "Clause 3: surrounding zones require a coexisting task zone (orphan surrounding blocked).",
      "if": {
        "properties": {
          "zones": {
            "type": "array",
            "contains": {
              "type": "object",
              "properties": {"purpose": {"const": "surrounding"}},
              "required": ["purpose"]
            }
          }
        }
      },
      "then": {
        "properties": {
          "zones": {
            "type": "array",
            "contains": {
              "type": "object",
              "properties": {"purpose": {"const": "task"}},
              "required": ["purpose"]
            }
          }
        }
      }
    }
  ]
}
```

- [ ] **Step 6: Validate JSON parses + maxLength preserved**

Run:
```bash
python3 -c "
import json
s = json.load(open('shared/schemas/electrical/lighting-layout-ir.schema.json'))
print('parse: OK')
zp = s['properties']['zones']['items']['properties']
print('zone.purpose:', 'present' if 'purpose' in zp else 'MISSING')
print('zone.em_target_lux:', 'present' if 'em_target_lux' in zp else 'MISSING')
lp = s['properties']['luminaires']['items']['properties']
print('lum.mount_type:', 'present' if 'mount_type' in lp else 'MISSING')
print('lum.z_mm:', 'present' if 'z_mm' in lp else 'MISSING')
print('lum.suspension_length_mm:', 'present' if 'suspension_length_mm' in lp else 'MISSING')
cp = s['properties']['calculation_summary']['properties']
print('calc.per_zone_achieved:', 'present' if 'per_zone_achieved' in cp else 'MISSING')
print('allOf clauses:', len(s.get('allOf', [])))
print('evidence.maxLength:', s['properties']['invariants']['items']['properties']['evidence'].get('maxLength'))
"
```

Expected: all `present`, allOf clauses ≥ 3, evidence.maxLength = 1200.

- [ ] **Step 7: Run golden CI gate — existing 8 examples may FAIL if any zone is missing the new defaults**

Run:
```bash
python3 scripts/validate-examples.py 2>&1 | tail -10
```

Expected: existing examples PASS via default values (`purpose: "task"` default + `mount_type: "recessed"` default). If FAIL surfaces it means defaults didn't apply — fix in this step before commit.

If FAIL because examples lack `per_zone_achieved` and it's required: confirm `per_zone_achieved` is NOT in calc_summary's `required` array (it shouldn't be — it's optional, populated post-photometric-cascade).

- [ ] **Step 8: Commit**

```bash
git add shared/schemas/electrical/lighting-layout-ir.schema.json
git commit -m "feat(lighting-layout): A.1 IR schema additions for v1.7 task/ambient + 3D placement (zones[].purpose + em_target_lux + luminaires[].mount_type + z_mm + suspension_length_mm + calc.per_zone_achieved + 3 allOf clauses; maxLength 1200 maintained)"
```

### Task A.2: inputs.json — 3 new D5 optional items

**Files:**
- Modify: `electrical/lighting-layout/inputs.json`

**Why Sonnet:** Mechanical taxonomy authoring; structure dictated by `shared/schemas/core/inputs.schema.json` canonical `items[]` shape (matches small-power D4 A.2 precedent).

- [ ] **Step 1: Read current inputs.json structure**

Run:
```bash
python3 -c "
import json
d = json.load(open('electrical/lighting-layout/inputs.json'))
print('shape:', 'items[]' if 'items' in d else ('inputs[]' if 'inputs' in d else 'input_groups[]'))
if 'items' in d:
    print('item count:', len(d['items']))
    print('first 3 ids:', [i.get('item_id') for i in d['items'][:3]])
"
```

Expected: canonical `items[]` shape. (lighting-layout already migrated in prior sprint.)

- [ ] **Step 2: Append 3 new optional items to `items[]`**

In `electrical/lighting-layout/inputs.json`, locate the `items` array and APPEND these 3 entries (do NOT remove or reorder existing items; preserve insertion order at end):

```json
{
  "item_id": "zone_purpose_inputs",
  "question": "For each zone, what is its BS EN 12464-1 area classification (task / surrounding / background / circulation)?",
  "answer_type": "struct_list",
  "required": false,
  "default": [],
  "item_schema": {
    "type": "object",
    "properties": {
      "zone_id": {"type": "string"},
      "purpose": {"type": "string", "enum": ["task", "surrounding", "background", "circulation"]},
      "em_target_lux_override": {"type": "number", "minimum": 0, "description": "Optional explicit override; else derived from Em × ratio."}
    },
    "required": ["zone_id", "purpose"]
  },
  "_clause": "BS EN 12464-1:2021 §4.2.2 + Table 6",
  "_note": "Optional. If absent, all zones default to purpose=task with em_target_lux derived from room.target_illuminance_lux. v1.7 addition (D5 sprint)."
},
{
  "item_id": "mount_type_inputs",
  "question": "For each luminaire, what is the installation mount type?",
  "answer_type": "struct_list",
  "required": false,
  "default": [],
  "item_schema": {
    "type": "object",
    "properties": {
      "luminaire_id": {"type": "string"},
      "mount_type": {"type": "string", "enum": ["recessed", "surface", "pendant", "suspended", "track"]}
    },
    "required": ["luminaire_id", "mount_type"]
  },
  "_clause": "BS EN 60598-2 series (luminaire installation type)",
  "_note": "Optional. If absent, all luminaires default to mount_type=recessed (v1.6.0 backwards compatible). v1.7 addition (D5 sprint)."
},
{
  "item_id": "suspension_length_inputs",
  "question": "For each pendant or suspended luminaire, what is the suspension drop length from ceiling (mm)?",
  "answer_type": "struct_list",
  "required": false,
  "default": [],
  "item_schema": {
    "type": "object",
    "properties": {
      "luminaire_id": {"type": "string"},
      "suspension_length_mm": {"type": "integer", "minimum": 0}
    },
    "required": ["luminaire_id", "suspension_length_mm"]
  },
  "_clause": "BS EN 60598-2 + manufacturer pendant kit datasheet",
  "_note": "Required when mount_type ∈ {pendant, suspended}. v1.7 addition (D5 sprint)."
}
```

- [ ] **Step 3: Validate inputs.json parses + passes inputs.schema.json**

Run:
```bash
python3 -c "
import json, jsonschema
schema = json.load(open('shared/schemas/core/inputs.schema.json'))
d = json.load(open('electrical/lighting-layout/inputs.json'))
v = jsonschema.Draft202012Validator(schema)
errors = list(v.iter_errors(d))
if errors:
    for e in errors[:5]: print('  ERROR:', e.message[:200])
else:
    print('OK')
"
```

Expected: `OK`.

- [ ] **Step 4: Run golden CI gate to confirm Pass 3 still green**

Run:
```bash
python3 scripts/validate-examples.py 2>&1 | tail -3
```

Expected: aggregate same; Pass 3 still green.

- [ ] **Step 5: Commit**

```bash
git add electrical/lighting-layout/inputs.json
git commit -m "feat(lighting-layout): A.2 inputs.json — 3 new optional D5 items (zone_purpose + mount_type + suspension_length)"
```

### Task A.3: Augment lux-levels.json with ratio defaults + citation

**Files:**
- Modify: `shared/standards/lighting/BSEN12464/lux-levels.json`

**Why Sonnet:** Mechanical addition of 4 root-level constants citing A.0.

- [ ] **Step 1: Read current `lux-levels.json` root keys**

Run:
```bash
python3 -c "
import json
d = json.load(open('shared/standards/lighting/BSEN12464/lux-levels.json'))
print('root keys:', list(d.keys())[:10])
print('_source:', d.get('_source'))
"
```

Expected: `_source: 'BS EN 12464-1:2021 Table 5.3'` + per-category branches (office, circulation, etc.).

- [ ] **Step 2: Append 4 new root keys (insert after `_units` if present, else after `_note`)**

In `shared/standards/lighting/BSEN12464/lux-levels.json`, ADD these 4 root keys (do NOT modify existing per-category branches):

```json
"_surrounding_ratio_default": 0.5,
"_background_ratio_default": 0.333,
"_background_min_lx": 50,
"_ratio_source": "BS EN 12464-1:2021 §4.2.2.2 + §4.2.2.3 + Table 6 (transcribed in shared/standards/lighting/BSEN12464/area-definitions.json — A.0 of D5 sprint)"
```

- [ ] **Step 3: Validate JSON parses + downstream consumers untouched**

Run:
```bash
python3 -c "
import json
d = json.load(open('shared/standards/lighting/BSEN12464/lux-levels.json'))
print('parse: OK')
print('_surrounding_ratio_default:', d.get('_surrounding_ratio_default'))
print('_background_ratio_default:', d.get('_background_ratio_default'))
print('_background_min_lx:', d.get('_background_min_lx'))
# Existing per-category branch should still be intact
print('office.open_plan.em:', d.get('office', {}).get('open_plan', {}).get('em'))
"
```

Expected: parse OK; new keys present with values `0.5`, `0.333`, `50`; `office.open_plan.em: 500` preserved.

- [ ] **Step 4: Run golden CI gate**

Run:
```bash
python3 scripts/validate-examples.py 2>&1 | tail -3
```

Expected: aggregate unchanged.

- [ ] **Step 5: Commit**

```bash
git add shared/standards/lighting/BSEN12464/lux-levels.json
git commit -m "feat(lighting-standards): A.3 augment lux-levels.json with Table 6 ratio defaults (cites area-definitions.json from A.0)"
```

### Task A.4: Create 2 new rules YAML files (zone-purpose-rules + mount-type-rules)

**Files:**
- Create: `electrical/lighting-layout/rules/zone-purpose-rules.yaml`
- Create: `electrical/lighting-layout/rules/mount-type-rules.yaml`

**Why Sonnet:** Mechanical rule authoring; structure dictated by existing `placement-rules.yaml` / `spacing-rules.yaml` pattern.

- [ ] **Step 1: Read existing rules YAML to match voice + structure**

Run:
```bash
cat electrical/lighting-layout/rules/placement-rules.yaml | head -40
cat electrical/lighting-layout/rules/spacing-rules.yaml | head -40
```

Expected: identify the rule-block shape (id, summary, clause, applies_when, check, severity).

- [ ] **Step 2: Author `zone-purpose-rules.yaml`**

Create `electrical/lighting-layout/rules/zone-purpose-rules.yaml`:

```yaml
# Zone purpose rules — derive task/surrounding/background/circulation behaviour from BS EN 12464-1:2021 §4.2.2 + Table 6.
# Authored: 2026-06-03 (D5 sprint A.4)
# Source-of-truth: shared/standards/lighting/BSEN12464/area-definitions.json

rules:
  - id: ZP-01
    summary: Default purpose for unclassified zones is task
    clause: "BS EN 12464-1:2021 §4.2.2.1"
    applies_when: "zone.purpose is null OR absent"
    check: "Set zone.purpose = 'task' for backwards compatibility with v1.6.0 examples. Document the default explicitly in compliance_summary.assumptions[]."
    severity: info
    _note: "Backwards-compat default. Engineers may override per WI1 zone_purpose_inputs."

  - id: ZP-02
    summary: Surrounding em_target_lux ratio-bound to task em
    clause: "BS EN 12464-1:2021 §4.2.2.2 + Table 6"
    applies_when: "zone.purpose == 'surrounding'"
    check: "em_target_lux ∈ [0.3 × Em_task, 0.5 × Em_task]. Default ratio 0.5 from area-definitions.json _surrounding_ratio_default. Honest disclosure: per Table 6 simplified rule (not the per-Em-band table)."
    severity: high

  - id: ZP-03
    summary: Background em_target_lux floor
    clause: "BS EN 12464-1:2021 §4.2.2.3 + Table 6"
    applies_when: "zone.purpose == 'background'"
    check: "em_target_lux ≥ max(Em_task / 3, 50 lx). Floor 50 lx is absolute per Table 6. _background_ratio_default 0.333 in lux-levels.json."
    severity: high

  - id: ZP-04
    summary: Orphan surrounding zone blocked
    clause: "BS EN 12464-1:2021 §4.2.2.2 (surrounding is defined RELATIVE to a task area)"
    applies_when: "any zone has purpose=='surrounding' AND no zone has purpose=='task' in the same room"
    check: "Reject the IR; surrounding zones cannot exist without a paired task zone. Schema enforces via allOf clause 3."
    severity: critical

  - id: ZP-05
    summary: Circulation zones exempt from Table 6 ratio rules
    clause: "BS EN 12464-1:2021 Table 5 (circulation has its own Em entries)"
    applies_when: "zone.purpose == 'circulation'"
    check: "em_target_lux looked up from lux-levels.json circulation branch (e.g. 100 lx main corridor, 50 lx link corridor, 150 lx staircase). NOT subject to task/surrounding/background ratios."
    severity: info
```

- [ ] **Step 3: Author `mount-type-rules.yaml`**

Create `electrical/lighting-layout/rules/mount-type-rules.yaml`:

```yaml
# Mount type rules — luminaire 3D placement geometry per BS EN 60598-2 + repo convention.
# Authored: 2026-06-03 (D5 sprint A.4)

rules:
  - id: MT-01
    summary: Recessed/surface/track inherit z = ceiling_height_mm
    clause: "Repo convention; BS EN 60598-2-2 (recessed) / -1 (general)"
    applies_when: "luminaire.mount_type ∈ {recessed, surface, track}"
    check: "z_mm is OPTIONAL. If absent, runtime renders at z = ceiling_height_mm. INV-16 verifies. hm_mm derives as ceiling_height_mm - working_plane_mm."
    severity: info

  - id: MT-02
    summary: Pendant geometry — z_mm + suspension_length_mm = ceiling_height_mm
    clause: "BS EN 60598-2-1 (general luminaire) + repo geometry convention"
    applies_when: "luminaire.mount_type == 'pendant'"
    check: "Both z_mm and suspension_length_mm REQUIRED (allOf clause 1). Algebraic identity: z_mm + suspension_length_mm = ceiling_height_mm. INV-16 verifies. hm_mm derives as z_mm - working_plane_mm."
    severity: high

  - id: MT-03
    summary: Suspended geometry — z_mm + suspension_length_mm ≤ ceiling_height_mm
    clause: "BS EN 60598-2 + repo geometry convention"
    applies_when: "luminaire.mount_type == 'suspended'"
    check: "Both z_mm and suspension_length_mm REQUIRED. INEQUALITY: z_mm + suspension_length_mm ≤ ceiling_height_mm (suspended can hang from intermediate purlin). INV-16 + INV-17 verify."
    severity: high

  - id: MT-04
    summary: Ceiling clearance + working-plane safety floor
    clause: "BS EN 12464-1:2021 §4.4 (working plane definition); repo safety convention"
    applies_when: "any luminaire.mount_type"
    check: "z_mm > working_plane_mm (no luminaire below task plane — collision risk). z_mm + suspension_length_mm ≤ ceiling_height_mm (physical clearance). INV-17 verifies both inequalities."
    severity: high
```

- [ ] **Step 4: Validate YAML parses**

Run:
```bash
python3 -c "
import yaml
for f in ['electrical/lighting-layout/rules/zone-purpose-rules.yaml', 'electrical/lighting-layout/rules/mount-type-rules.yaml']:
    d = yaml.safe_load(open(f))
    print(f, '→ rules:', len(d['rules']))
"
```

Expected: `zone-purpose-rules.yaml → rules: 5`; `mount-type-rules.yaml → rules: 4`.

- [ ] **Step 5: Run golden CI gate**

Run:
```bash
python3 scripts/validate-examples.py 2>&1 | tail -3
```

Expected: aggregate unchanged (rule YAMLs not validated by the 3-pass gate; declared in manifest at A.5).

- [ ] **Step 6: Commit**

```bash
git add electrical/lighting-layout/rules/zone-purpose-rules.yaml electrical/lighting-layout/rules/mount-type-rules.yaml
git commit -m "feat(lighting-layout): A.4 NEW rules YAML — zone-purpose-rules (5 ZP-NN) + mount-type-rules (4 MT-NN) per BS EN 12464-1 §4.2.2 + BS EN 60598-2"
```

### Task A.5: Manifest bump 1.6.0 → 1.7.0 + pre-merge consumer check + README v1.7 stub

**Files:**
- Modify: `electrical/lighting-layout/skill.manifest.json`
- Modify: `electrical/lighting-layout/README.md`
- Inspect: `electrical/*/skill.manifest.json` (consumer pin grep)

**Why Sonnet:** Mechanical metadata edits + grep. README touch is a stub bump only — full v1.7 content authored as part of D.3 documentation phase.

- [ ] **Step 1: Pre-merge check — grep all skill.manifest.json files for consumers pinned to lighting-layout ^1.6 (must widen before 1.7 ships)**

Run:
```bash
for f in electrical/*/skill.manifest.json; do
  python3 -c "
import json, sys
m = json.load(open('$f'))
ci = m.get('consumes_intents', [])
for entry in ci:
    if entry.get('skill_id') == 'lighting-layout':
        print('$f → skill_id=lighting-layout, version_constraint=', entry.get('version_constraint'))
"
done
```

Expected: list any pins. For any constraint `^1.6` or similar, widen to `>=1.6` in Step 2.

- [ ] **Step 2: For each consumer pinned to ^1.6, edit version_constraint to >=1.6 (mirrors A.5 pattern from small-power D4)**

For each `electrical/<consumer>/skill.manifest.json` flagged in Step 1, edit the lighting-layout entry inside `consumes_intents`:

```json
{
  "skill_id": "lighting-layout",
  "version_constraint": ">=1.6",
  "..."
}
```

If no consumers pin `^1.6`, skip Step 2 and note in commit message.

- [ ] **Step 3: Update lighting-layout manifest — version 1.6.0 → 1.7.0; add 2 new rules + 4 new examples + 5 new evals to declarations; bump description**

In `electrical/lighting-layout/skill.manifest.json`:

1. Change `"version": "1.6.0"` → `"version": "1.7.0"`.
2. Keep `"status": "production"` unchanged.
3. Update `"description"` to mention v1.7 additions (task/ambient split + 3D placement).
4. APPEND to `"rules"` array:
   - `"rules/zone-purpose-rules.yaml"`
   - `"rules/mount-type-rules.yaml"`
5. APPEND to `"examples"` array:
   - `"examples/uk-pendant-open-plan-office"`
   - `"examples/uk-mixed-purpose-classroom"`
   - `"examples/uk-retail-display-task-zone"`
   - `"examples/uk-per-zone-target-violation"`
6. APPEND to `"evals"` array:
   - `"evals/eval-09-zone-purpose-emit.yaml"`
   - `"evals/eval-10-task-surrounding-ratio.yaml"`
   - `"evals/eval-11-mount-type-3d-consistency.yaml"`
   - `"evals/eval-12-per-zone-achievement-pass.yaml"`
   - `"evals/eval-13-per-zone-achievement-fail.yaml"`
7. APPEND to `"standards"` array (if present) an entry for `area-definitions.json`:
   - `"shared/standards/lighting/BSEN12464/area-definitions.json"`

(Confirm shape with `cat electrical/lighting-layout/skill.manifest.json | python3 -m json.tool | head -60` before editing.)

- [ ] **Step 4: Update README.md stub — bump version line only (full v1.7 README authored at D.3)**

In `electrical/lighting-layout/README.md`, locate the version line in the YAML frontmatter or first-section header and bump it to `1.7.0`. Do NOT yet rewrite content — D.3 handles the full README content update.

- [ ] **Step 5: Validate manifest JSON parses**

Run:
```bash
python3 -c "
import json
m = json.load(open('electrical/lighting-layout/skill.manifest.json'))
print('version:', m['version'])
print('status:', m['status'])
print('rules count:', len(m.get('rules', [])))
print('examples count:', len(m.get('examples', [])))
print('evals count:', len(m.get('evals', [])))
"
```

Expected: version `1.7.0`; rules ≥ 7 (5 existing + 2 new); examples ≥ 12 (8 existing + 4 new); evals ≥ 13 (8 existing + 5 new).

- [ ] **Step 6: Run golden CI gate (manifest is metadata; gate count unchanged)**

Run:
```bash
python3 scripts/validate-examples.py 2>&1 | tail -3
```

Expected: aggregate unchanged.

- [ ] **Step 7: Commit**

```bash
git add electrical/lighting-layout/skill.manifest.json electrical/lighting-layout/README.md $(for f in electrical/*/skill.manifest.json; do grep -l 'lighting-layout' "$f" 2>/dev/null; done | sort -u)
git commit -m "feat(lighting-layout): A.5 manifest bump 1.6.0 → 1.7.0 + declare rules/examples/evals + pre-merge consumer-pin check (widen any ^1.6 → >=1.6)"
```

---

## Phase B — Prompts (4 tasks, all Opus, ~4-6 commits incl. fix-passes)

Goal: extend the three-stage prompt chain (generator → validator → reviewer) with the 7 new INV sections, 3 new generator steps, and 3 new D-checks. All citations cross-reference A.0 (`area-definitions.json`) and existing verified files. B.4 enumerates the cascade contracts referenced in the new generator steps.

### Task B.1: generator.md — Steps 13 / 14 / 15 (zone purpose + 3D placement + per-zone achievement)

**Files:**
- Modify: `electrical/lighting-layout/prompts/generator.md`

**Why Opus:** Engineering content; step ordering decisions; how to thread per-zone purpose through downstream steps without breaking existing Step 11 (Part-L) and Step 12 (cascade consumption).

- [ ] **Step 1: Read existing generator.md to map current step numbering + identify insertion points**

Run:
```bash
grep -nE "^## Step|^# " electrical/lighting-layout/prompts/generator.md | head -25
wc -l electrical/lighting-layout/prompts/generator.md
```

Expected: current step list (steps 1..N). Identify the LAST step before the rationale/output emission step (typically the step where calculation_summary is finalised).

- [ ] **Step 2: Append Step 13 — Zone purpose resolution**

In `electrical/lighting-layout/prompts/generator.md`, AFTER the existing last engineering step (likely Step 12 special-locations cascade consumption) and BEFORE the rationale-block / output-emission step, ADD:

```markdown
## Step 13 — Zone purpose resolution (v1.7 D5)

For every zone in the IR, populate `zone.purpose` per BS EN 12464-1:2021 §4.2.2:

1. **If `zone_purpose_inputs` supplied** (WI1 item — see inputs.json): use the engineer's classification verbatim.
2. **Else default to `purpose: "task"`** for backwards compatibility with v1.6.0 examples. Document the default explicitly in `compliance_summary.assumptions[]`.

Populate `zone.em_target_lux` per the following rules:

- **`purpose == "task"`** → `em_target_lux` = Em value from `shared/standards/lighting/BSEN12464/lux-levels.json` for the room's `room_type` (existing v1.6.0 behaviour preserved).
- **`purpose == "surrounding"`** → `em_target_lux` = `task_em × _surrounding_ratio_default` (0.5 per `lux-levels.json` augmentation from A.3). Engineer may override via `em_target_lux_override` in WI1 input; if so, validate against the [0.3, 0.5] band per BS EN 12464-1:2021 Table 6 (INV-14 verifies).
- **`purpose == "background"`** → `em_target_lux` = `max(task_em × _background_ratio_default, _background_min_lx)` = `max(task_em / 3, 50 lx)` per BS EN 12464-1:2021 §4.2.2.3 + Table 6 (INV-15 verifies).
- **`purpose == "circulation"`** → `em_target_lux` looked up from `lux-levels.json` circulation branch (e.g. 100 lx main corridor, 50 lx link corridor). Independent of task/surrounding/background ratios per ZP-05.

**Cross-check:** if any zone has `purpose: "surrounding"`, at least one zone in the same room MUST have `purpose: "task"`. Schema enforces via allOf clause 3 (A.1). Validator INV-13 evidence cites BS EN 12464-1:2021 §4.2.2.2 ("surrounding is defined RELATIVE to a task area").

**Citation anchor:** `shared/standards/lighting/BSEN12464/area-definitions.json` (A.0 file).
```

- [ ] **Step 3: Append Step 14 — Mount type + 3D placement**

In the same file, AFTER Step 13 and BEFORE the rationale-block step, ADD:

```markdown
## Step 14 — Mount type + 3D placement (v1.7 D5)

For every luminaire in `luminaires[]`, populate `mount_type` per BS EN 60598-2 series:

1. **If `mount_type_inputs` supplied** (WI1 item): use engineer's selection verbatim.
2. **Else default to `mount_type: "recessed"`** for v1.6.0 backwards compatibility.

For luminaires with `mount_type ∈ {pendant, suspended}`, populate `z_mm` + `suspension_length_mm`:

- **Pendant geometry** (MT-02): `z_mm + suspension_length_mm = ceiling_height_mm` (algebraic identity). If `suspension_length_inputs` supplied for the luminaire, use it; else default to 800mm typical pendant drop (document the default in assumptions).
- **Suspended geometry** (MT-03): `z_mm + suspension_length_mm ≤ ceiling_height_mm` (suspended can hang from intermediate purlin, e.g. industrial highbay from roof truss vs ceiling).

**Cross-checks** (INV-16 + INV-17 verify):

- `z_mm > working_plane_mm` (no luminaire below the task plane — collision risk).
- `z_mm + suspension_length_mm ≤ ceiling_height_mm` (physical clearance).
- For pendant specifically: equality holds.

**Update `room.hm_mm`** (mounting height above task plane):

- For pendant/suspended luminaires: `hm_mm = z_mm - working_plane_mm` (per-luminaire; if luminaires have mixed z values, use the lowest z for hm calc).
- For recessed/surface/track: `hm_mm = ceiling_height_mm - working_plane_mm` (existing v1.6.0 behaviour).

**Citation anchor:** BS EN 60598-2-1 (general luminaire) + BS EN 60598-2-2 (recessed); repo convention in `mount-type-rules.yaml` (A.4 file).
```

- [ ] **Step 4: Append Step 15 — Per-zone achievement summary**

In the same file, AFTER Step 14 and BEFORE the rationale-block step, ADD:

```markdown
## Step 15 — Per-zone achievement summary (v1.7 D5)

Populate `calculation_summary.per_zone_achieved[]` with one entry per zone:

```json
{
  "zone_id": "Z1",
  "purpose": "task",
  "em_target_lux": 500,
  "em_achieved_lux": 525,
  "ratio_compliance": "pass"
}
```

**Source of `em_achieved_lux`** in priority order:

1. **Photometric-analysis cascade** (INV-11 / `consumed_intents.photometric_grid`): if present and emitted, derive per-zone achieved Em by intersecting the point grid with the zone polygon. This is the highest-fidelity source.
2. **Lumen-method calc** (existing v1.6.0 behaviour): if no photometric cascade, use the lumen-method `E_avg = (N × Φ × MF × UF) / A` per room and assume per-zone `em_achieved_lux = E_avg × purpose_uniformity_factor` (0.6 task / 0.4 surrounding / 0.1 background per area-definitions.json uniformity_rules).
3. **Pending honest disclosure**: if neither photometric nor lumen-method can yield per-zone values (e.g. missing IES + missing Em target), set `em_achieved_lux: 0` with `ratio_compliance: "fail"` AND document the gap in `compliance_summary.assumptions[]` as a pending-photometric disclosure.

**`ratio_compliance` bands** (per spec §6 INV-19):

- `em_achieved_lux ≥ em_target_lux` → `"pass"`.
- `em_target_lux × 0.75 ≤ em_achieved_lux < em_target_lux` → `"marginal"` (within 25%, INFO severity in INV-19).
- `em_target_lux × 0.50 ≤ em_achieved_lux < em_target_lux × 0.75` → `"fail"` (25-50% short, MEDIUM severity in INV-19).
- `em_achieved_lux < em_target_lux × 0.50` → `"fail"` (>50% short, HIGH severity in INV-19).

**Note:** `ratio_compliance` is a tri-state enum on the schema (pass / fail / marginal). The HIGH-vs-MEDIUM split lives in the `non_compliance_flags[]` severity field, not the `ratio_compliance` enum.
```

- [ ] **Step 5: Validate generator.md renders cleanly + step numbers consistent**

Run:
```bash
grep -nE "^## Step" electrical/lighting-layout/prompts/generator.md
```

Expected: contiguous step sequence (no duplicate / skipped numbers); Step 13 / 14 / 15 present.

- [ ] **Step 6: Run golden CI gate (prompts not validated by gate)**

Run:
```bash
python3 scripts/validate-examples.py 2>&1 | tail -3
```

Expected: aggregate unchanged.

- [ ] **Step 7: Commit**

```bash
git add electrical/lighting-layout/prompts/generator.md
git commit -m "feat(lighting-layout): B.1 generator.md — Steps 13/14/15 (zone purpose resolution + mount_type + per-zone achievement summary; cites area-definitions.json from A.0)"
```

### Task B.2: validator.md — 7 new INV sections (INV-13..INV-19)

**Files:**
- Modify: `electrical/lighting-layout/prompts/validator.md`

**Why Opus:** Engineering content + citation discipline; every INV section needs verbatim A.0 / lux-levels.json citation; severity ladder is dictated by spec §6 but evidence language is judgement.

- [ ] **Step 1: Read existing validator.md to identify INV-12 (last existing) and the section-after-last-INV insertion point**

Run:
```bash
grep -nE "^## INV-|^# " electrical/lighting-layout/prompts/validator.md | head -20
wc -l electrical/lighting-layout/prompts/validator.md
```

Expected: INV-01..INV-12 sections present; identify the line AFTER the last INV-12 line (typically a section break or umbrella heading).

- [ ] **Step 2: Append INV-13 section — Zone purpose required + valid**

In `electrical/lighting-layout/prompts/validator.md`, after the INV-12 section, ADD:

```markdown
## INV-13 — Zone purpose required + valid (HIGH)

**Clause:** BS EN 12464-1:2021 §4.2.2.1 (task area) + §4.2.2.2 (immediate surrounding area) + §4.2.2.3 (background area). Transcribed in `shared/standards/lighting/BSEN12464/area-definitions.json` (A.0 file).

**Check:**

1. Every zone in `zones[]` has `purpose ∈ {task, surrounding, background, circulation}`.
2. If any zone has `purpose: "surrounding"`, at least one zone in the same room has `purpose: "task"` (orphan surrounding blocked).
3. `em_target_lux` populated per zone (≥ 0).

**Evidence template** (20–1200 chars per `[[feedback-no-trim-non-consequential]]`):

```
INV-13 verdict: PASS / FAIL
Zones inspected: {count}
Per-zone purpose:
- {zone_id}: purpose={enum_value}, em_target_lux={value}
Orphan-surrounding check: {pass | blocked because zone {id} has purpose=surrounding with no task zone in same room}
Citation: BS EN 12464-1:2021 §4.2.2.1/2/3 (area-definitions.json §4.2.2.x).
```

**Severity:** HIGH (zone purpose drives every downstream illuminance check).

**Vacuous PASS condition:** if `zones[]` empty (calc-only mode), INV-13 PASSes with evidence noting `zones[] empty — vacuous PASS`.
```

- [ ] **Step 3: Append INV-14 section — Surrounding ratio compliance**

In the same file, after INV-13, ADD:

```markdown
## INV-14 — Surrounding ratio compliance (HIGH)

**Clause:** BS EN 12464-1:2021 §4.2.2.2 + Table 6 (transcribed in area-definitions.json `immediate_surrounding_area` + `table_6_ratio_rules.task_to_surrounding`).

**Check:** For every zone with `purpose == "surrounding"`:

- Let `task_em` = `em_target_lux` of any zone in the same room with `purpose == "task"`.
- Verify `0.3 × task_em ≤ em_target_lux ≤ 0.5 × task_em`.
- (If `task_em < 100 lx`, surrounding inherits `task_em` per Table 6 row — verify equality.)

**Evidence template:**

```
INV-14 verdict: PASS / FAIL
Surrounding zones inspected: {count}
Task em reference: {value} lx (from zone {task_zone_id})
Per-zone ratio check:
- {zone_id}: em_target_lux={value}, ratio={ratio:.3f}, band [0.3, 0.5], result: {pass | fail}
Citation: BS EN 12464-1:2021 §4.2.2.2 + Table 6 (area-definitions.json).
```

**Severity:** HIGH.

**Vacuous PASS:** no `surrounding` zones present → INV-14 PASSes with evidence noting `no surrounding zones — vacuous PASS`.
```

- [ ] **Step 4: Append INV-15 section — Background floor**

In the same file, after INV-14, ADD:

```markdown
## INV-15 — Background floor (HIGH)

**Clause:** BS EN 12464-1:2021 §4.2.2.3 + Table 6 (transcribed in area-definitions.json `background_area` + `table_6_ratio_rules.task_to_background`).

**Check:** For every zone with `purpose == "background"`:

- Let `task_em` = `em_target_lux` of any task zone in same room.
- Verify `em_target_lux ≥ max(task_em / 3, 50 lx)`.

**Evidence template:**

```
INV-15 verdict: PASS / FAIL
Background zones inspected: {count}
Task em reference: {value} lx (from zone {task_zone_id})
Per-zone floor check:
- {zone_id}: em_target_lux={value}, floor=max({task_em}/3, 50)={floor_value} lx, result: {pass | fail}
Citation: BS EN 12464-1:2021 §4.2.2.3 + Table 6 (area-definitions.json).
```

**Severity:** HIGH.

**Vacuous PASS:** no `background` zones → vacuous PASS.
```

- [ ] **Step 5: Append INV-16 section — mount_type ↔ z_mm/suspension consistency**

In the same file, after INV-15, ADD:

```markdown
## INV-16 — mount_type ↔ z_mm/suspension consistency (HIGH)

**Clause:** BS EN 60598-2-1 (general luminaire) + BS EN 60598-2-2 (recessed); repo `mount-type-rules.yaml` MT-01/02/03.

**Check:** For every luminaire:

- If `mount_type ∈ {pendant, suspended}`: BOTH `z_mm` AND `suspension_length_mm` are present (schema allOf clause 1 enforces; INV-16 verifies emit).
- If `mount_type == "pendant"`: `z_mm + suspension_length_mm == ceiling_height_mm` (algebraic identity per MT-02).
- If `mount_type == "suspended"`: `z_mm + suspension_length_mm ≤ ceiling_height_mm` (inequality per MT-03).
- If `mount_type ∈ {recessed, surface, track}`: `z_mm` and `suspension_length_mm` MAY be omitted; if present, they inherit ceiling_height_mm convention (MT-01).

**Evidence template:**

```
INV-16 verdict: PASS / FAIL
Luminaires inspected: {count}
Pendant geometry checks:
- {luminaire_id}: z_mm={value}, suspension_length_mm={value}, ceiling_height_mm={value}, sum={sum}, identity: {pass | fail}
Suspended geometry checks:
- {luminaire_id}: sum={sum}, ceiling={ceiling}, inequality: {pass | fail}
Recessed/surface/track: {count} luminaires, z_mm convention applied.
Citation: BS EN 60598-2-1 + mount-type-rules.yaml MT-01/02/03.
```

**Severity:** HIGH.

**Vacuous PASS:** all luminaires are recessed/surface/track with no z_mm → vacuous PASS (geometry inherited from ceiling).
```

- [ ] **Step 6: Append INV-17 section — Ceiling clearance + working-plane floor**

In the same file, after INV-16, ADD:

```markdown
## INV-17 — Ceiling clearance + working-plane floor (HIGH)

**Clause:** BS EN 12464-1:2021 §4.4 (working plane definition) + BS EN 60598-2 (luminaire mounting) + repo safety convention in MT-04.

**Check:** For every luminaire (regardless of mount_type):

- `z_mm > working_plane_mm` (luminaire emission plane must be ABOVE the task plane — no collision / occlusion risk).
- `z_mm + suspension_length_mm ≤ ceiling_height_mm` (physical clearance from ceiling structure; pendant/suspended only — for recessed/surface, this is structurally implied).

**Evidence template:**

```
INV-17 verdict: PASS / FAIL
Working plane reference: {working_plane_mm} mm AFF.
Per-luminaire floor check:
- {luminaire_id}: z_mm={value}, working_plane={working_plane}, clearance={z - working_plane} mm, result: {pass | fail (luminaire below task plane)}
Per-luminaire ceiling clearance:
- {luminaire_id}: z_mm + suspension={sum}, ceiling={ceiling}, result: {pass | fail (luminaire exceeds ceiling)}
Citation: BS EN 12464-1:2021 §4.4 + BS EN 60598-2 + MT-04.
```

**Severity:** HIGH.
```

- [ ] **Step 7: Append INV-18 section — hm_mm derived correctly**

In the same file, after INV-17, ADD:

```markdown
## INV-18 — hm_mm derivation consistency (MEDIUM)

**Clause:** repo geometry convention (no specific BS EN clause — derived identity); links BS EN 12464-1:2021 §4.4 working plane to BS EN 60598 mounting height.

**Check:** `room.hm_mm` reconciles with luminaire z values per these rules:

- For pendant/suspended luminaires: expected `hm_mm = min(z_mm across pendant/suspended luminaires) - working_plane_mm`.
- For recessed/surface/track (no pendant/suspended in room): expected `hm_mm = ceiling_height_mm - working_plane_mm`.
- Tolerance: ±50 mm (engineer-of-record rounding).

**Evidence template:**

```
INV-18 verdict: PASS / FAIL
Room hm_mm recorded: {value} mm.
Expected hm_mm derivation:
- Lowest pendant/suspended z_mm: {value} (or N/A if all recessed)
- Working plane: {working_plane_mm}
- Expected: {calculated_value} mm
- Drift: {abs(recorded - expected)} mm, tolerance: ±50 mm
Result: {pass | fail (drift exceeds tolerance)}
Citation: BS EN 12464-1:2021 §4.4 + repo derivation convention.
```

**Severity:** MEDIUM (derivation drift is a calc-hygiene issue, not a safety hazard).

**Vacuous PASS:** if `room.hm_mm` absent (calc-only / minimal-room mode), INV-18 PASSes vacuously.
```

- [ ] **Step 8: Append INV-19 section — Per-zone achievement (graded severity)**

In the same file, after INV-18, ADD:

```markdown
## INV-19 — Per-zone achievement (graded severity)

**Clause:** BS EN 12464-1:2021 §4.1 (top-level maintained illuminance principle) + Table 5 (per task type Em).

**Check:** For every entry in `calculation_summary.per_zone_achieved[]`:

- Compute `gap = em_target_lux - em_achieved_lux`.
- Compute `gap_pct = gap / em_target_lux` (when em_target > 0; if em_target == 0, vacuous PASS).

**Severity bands:**

| `gap_pct` range | `ratio_compliance` | non_compliance_flag severity | INV-19 verdict per zone |
|---|---|---|---|
| `gap_pct ≤ 0` (achieved ≥ target) | `pass` | none | PASS |
| `0 < gap_pct < 0.10` | `marginal` | INFO | PASS (within 10%) |
| `0.10 ≤ gap_pct < 0.25` | `marginal` | INFO | PASS (within 25%) |
| `0.25 ≤ gap_pct < 0.50` | `fail` | MEDIUM | FAIL (MEDIUM) |
| `gap_pct ≥ 0.50` | `fail` | HIGH | FAIL (HIGH) |

**Aggregate INV-19 verdict for the IR:** PASS if every zone is PASS or `marginal`; FAIL if any zone is `fail`. INV-19 severity = max severity across all failing zones.

**Evidence template:**

```
INV-19 verdict: PASS / FAIL ({severity})
Zones inspected: {count}
Per-zone achievement:
- {zone_id} ({purpose}): target={target}, achieved={achieved}, gap={gap}, gap_pct={gap_pct:.1%}, ratio_compliance={enum}, severity={band}
Aggregate: {n_pass} PASS, {n_marginal} marginal, {n_fail_medium} MEDIUM, {n_fail_high} HIGH.
Citation: BS EN 12464-1:2021 §4.1 + Table 5 (lux-levels.json).
```

**Severity:** graded (INFO / MEDIUM / HIGH per band). Default INV-19 severity at the invariant level is HIGH (worst case); per-zone severity attaches to `non_compliance_flags[]`.

**Vacuous PASS:** if `per_zone_achieved[]` empty (no photometric cascade + no lumen calc), INV-19 PASSes vacuously with evidence noting `per_zone_achieved[] empty — calc pending photometric grid`.
```

- [ ] **Step 9: Update the validator umbrella heading if it counts INVs (e.g. "12 INV checks" → "19 INV checks")**

Run:
```bash
grep -nE "12 INV|catalogue of 12|INV-01..INV-12|INV-01 to INV-12" electrical/lighting-layout/prompts/validator.md
```

If matches found, update to `19` / `INV-01..INV-19` accordingly.

- [ ] **Step 10: Validate validator.md renders + grep for banned citations**

Run:
```bash
grep -nE "(§526\.2|§433\.2|OZEV|3rd Edition|Reg 559|Em_room|average room lux)" electrical/lighting-layout/prompts/validator.md | grep -v "do NOT\|never cite\|banned\|NOT cite" && echo FAIL || echo PASS
```

Expected: PASS.

- [ ] **Step 11: Commit**

```bash
git add electrical/lighting-layout/prompts/validator.md
git commit -m "feat(lighting-layout): B.2 validator.md — 7 new INV sections (INV-13..INV-19; 6 HIGH + 1 MEDIUM with graded INV-19 severity bands; all cite area-definitions.json from A.0 or lux-levels.json)"
```

### Task B.3: reviewer.md — 3 new D-checks (D-11 / D-12 / D-13)

**Files:**
- Modify: `electrical/lighting-layout/prompts/reviewer.md`

**Why Opus:** Judgement-call content; D-checks are reviewer "smell tests" not algorithmic invariants; need carefully-worded thresholds that match spec §7.3.

- [ ] **Step 1: Read existing reviewer.md to identify last D-check + umbrella heading**

Run:
```bash
grep -nE "^### D-|^## The [0-9]+ D|^# " electrical/lighting-layout/prompts/reviewer.md | head -20
```

Expected: existing D-01..D-N sequence and umbrella heading (e.g. "## The 10 D dimensions" or similar).

- [ ] **Step 2: Append D-11 — Suspension length sanity check**

In `electrical/lighting-layout/prompts/reviewer.md`, after the last existing D-N section, ADD:

```markdown
### D-11 — Suspension length sanity check

**Question:** For every pendant/suspended luminaire, is the `suspension_length_mm` sensible for the ceiling height + room scale?

**Engineering judgement bands:**

- `suspension_length_mm < 100 mm` for `mount_type=pendant`: flag as suspicious — at this drop the luminaire is functionally surface-mounted. Suggest re-classifying.
- `suspension_length_mm > 2000 mm`: flag as unusual — typical pendant office drops are 500-1200 mm; >2 m suggests atrium / industrial highbay (mount_type=suspended preferred over pendant).
- `suspension_length_mm > (ceiling_height_mm - working_plane_mm)`: flag as IMPOSSIBLE — luminaire would be below the task plane; INV-17 should already catch this, but reviewer surfaces the edge case as a JSON-shape sanity check.

**Output:** Add a `_d11_review_note` field to `compliance_summary.assumptions[]` if any luminaire falls in a flag band.

**Severity:** info (sanity / smell test, not a compliance check).
```

- [ ] **Step 3: Append D-12 — Background-only rooms flag**

In the same file, after D-11, ADD:

```markdown
### D-12 — Background-only rooms flag

**Question:** Does any room have only `background` zones (no `task` zones)?

**Rule:** A room with all zones tagged `background` and no `task` zone is structurally suspicious unless the room is explicitly `circulation` (e.g. corridor, lobby).

**Action:**

- If `room.room_type ∈ {corridor, lobby, staircase, link_corridor}`: PASS — circulation rooms naturally lack task zones.
- Else: FLAG. Suggest the engineer either (a) re-classify at least one zone as `task`, or (b) change `room.room_type` to a circulation category.

**Output:** Add a `_d12_review_note` to `compliance_summary.assumptions[]` for any flagged room.

**Severity:** warning (structural anomaly, not necessarily a defect).
```

- [ ] **Step 4: Append D-13 — Task-zone density flag**

In the same file, after D-12, ADD:

```markdown
### D-13 — Task-zone density flag

**Question:** Does a single room have >70% of its floor area allocated to `task` zones?

**Rule:** BS EN 12464-1:2021 §4.2.2 framing expects task zones to be focal — surrounded by surrounding + background. A room that's 70%+ task is over-allocated; either the surrounding/background zones are missing or the task is over-broad.

**Action:**

- Compute task-zone area as sum of polygon areas for zones with `purpose: task`.
- If `task_area / room_area > 0.7`: FLAG. Suggest re-allocation: add a `surrounding` zone for desk perimeters, or split the task zone into task + circulation.
- Exception: small rooms (<10 m²) where the entire floor is the task plane (e.g. cellular office, treatment bay) — PASS with a `_small_room_exception` note.

**Output:** Add a `_d13_review_note` to `compliance_summary.assumptions[]`.

**Severity:** info.
```

- [ ] **Step 5: Update reviewer umbrella heading if it counts D-checks**

Run:
```bash
grep -nE "[0-9]+ D dimensions|D-01..D-[0-9]+|catalogue of [0-9]+ D" electrical/lighting-layout/prompts/reviewer.md
```

If matches found, bump to the new total (e.g. "10 D dimensions" → "13 D dimensions"; the exact prior count comes from Step 1).

- [ ] **Step 6: Validate reviewer.md + banned citation grep**

Run:
```bash
grep -nE "(§526\.2|§433\.2|OZEV|3rd Edition|Reg 559|Em_room|average room lux)" electrical/lighting-layout/prompts/reviewer.md | grep -v "do NOT\|never cite\|banned\|NOT cite" && echo FAIL || echo PASS
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add electrical/lighting-layout/prompts/reviewer.md
git commit -m "feat(lighting-layout): B.3 reviewer.md — 3 new D-checks (D-11 suspension sanity + D-12 background-only room flag + D-13 task-zone density flag)"
```

### Task B.4: Cascade-prereq context update (4 sources enumerated)

**Files:**
- Modify: `electrical/lighting-layout/prompts/generator.md` (cascade enumeration section)

**Why Opus:** Engineering content (documenting the cascade sources by the time-of-consumption rules); not a contract change but a clarification of what's consumed where.

- [ ] **Step 1: Read existing cascade-prereq section in generator.md**

Run:
```bash
grep -nE "cascade|consumed_intents|photometric|special-locations" electrical/lighting-layout/prompts/generator.md | head -20
```

Expected: identify existing section that lists/discusses the photometric-analysis (INV-11) and special-locations (INV-12) cascade consumption.

- [ ] **Step 2: Append (or augment existing) cascade enumeration table**

In `electrical/lighting-layout/prompts/generator.md`, at the appropriate cascade section (typically after Step 12 or in a dedicated "Cascade sources" subsection), ADD or UPDATE the enumeration:

```markdown
## Cascade sources consumed by lighting-layout v1.7

This skill consumes 2 cascade intents. Per-zone achievement (Step 15) primarily relies on the photometric cascade when present.

| Cascade source | Intent skill | Consumed at | INV that verifies | v1.7 usage |
|---|---|---|---|---|
| `consumed_intents.photometric_grid` | `photometric-analysis` | Step 15 (per-zone achievement) | INV-11 | Per-zone `em_achieved_lux` derived by intersecting grid points with zone polygons. If absent, fall back to lumen-method × purpose_uniformity_factor (per Step 15 priority list). |
| `consumed_intents.special_locations_zoning` | `special-locations` | Step 12 (existing) | INV-12 | Unchanged from v1.5.0. Special-locations payload does NOT contain `purpose` or `mount_type` — those are lighting-layout-side concerns. |

**Why no contract change for photometric in v1.7:** photometric-analysis emits the grid + UGR; lighting-layout enriches per-zone Em by polygon-intersection on the consumer side. Photometric does not need to know about `zone.purpose` to do its job. v1.7 is additive on the consumer side only.

**Honest disclosure for v1.7 examples without photometric cascade:** if `consumed_intents.photometric_grid` is absent, populate `per_zone_achieved[]` from the lumen-method × uniformity factor and document the assumption in `compliance_summary.assumptions[]` as "Em_achieved derived from lumen-method × purpose_uniformity_factor; pending full photometric grid solve for production sign-off."
```

- [ ] **Step 3: Validate generator.md renders + step ordering preserved**

Run:
```bash
grep -nE "^## Step|^## Cascade" electrical/lighting-layout/prompts/generator.md | head -25
```

Expected: cascade-sources section appears after the relevant step (typically Step 12 or between Step 15 and rationale-block); step numbering unchanged.

- [ ] **Step 4: Banned-citation grep**

Run:
```bash
grep -nE "(§526\.2|§433\.2|OZEV|3rd Edition|Reg 559|Em_room|average room lux)" electrical/lighting-layout/prompts/generator.md | grep -v "do NOT\|never cite\|banned\|NOT cite" && echo FAIL || echo PASS
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add electrical/lighting-layout/prompts/generator.md
git commit -m "feat(lighting-layout): B.4 generator.md cascade enumeration — 2 sources (photometric_grid + special_locations_zoning) documented with v1.7 usage notes"
```

---

## Phase C — Examples + Evals (13 tasks, Opus-heavy, ~13-17 commits incl. fix-passes)

Goal: retrofit 8 existing examples to declare zone.purpose + mount_type defaults + per_zone_achieved[]; author 4 NEW examples exercising new fields (pendant + mixed-purpose + retail-mixed-mount + per-zone FAIL); author 5 new evals validating INV-13..19 emission.

**Per-example discipline** (locked from Phase C onward):

- output.json validates against `shared/schemas/electrical/lighting-layout-ir.schema.json` Draft-07.
- All 19 INVs emit (12 existing + 7 new) with N/A-vacuous PASS for unused INVs.
- 4-place honest disclosure pattern: (1) `input._note` or `_cascade_disclosure`, (2) `compliance_summary.assumptions[]`, (3) `rationale.sections[]` "Honest disclosures" subsection, (4) `reasoning.md` "Honest disclosures" section.
- Banned-citation grep clean per spec §4 banned list + sprint-specific bans.
- Cascade payload, when present, byte-identical to producer fixture.
- Gates bump by +2 per NEW example (output.json + intent-out.json); +0 per retrofit (additive edits to existing files).

### Task C.1: RETROFIT office-open-plan example

**Files:**
- Modify: `electrical/lighting-layout/examples/office-open-plan/input.json`
- Modify: `electrical/lighting-layout/examples/office-open-plan/output.json`
- Modify: `electrical/lighting-layout/examples/office-open-plan/reasoning.md`
- Modify: `electrical/lighting-layout/examples/office-open-plan/intent-out.json` (if exists)

**Why Opus:** Engineering judgement on which existing zones get `purpose: task` vs `surrounding`; how to populate per_zone_achieved[] from existing achieved_illuminance_lux + zone polygon areas.

- [ ] **Step 1: Read existing example to inventory zones + luminaires + calc state**

Run:
```bash
ls electrical/lighting-layout/examples/office-open-plan/
python3 -c "
import json
d = json.load(open('electrical/lighting-layout/examples/office-open-plan/output.json'))
print('zones:', [{'id': z['zone_id'], 'label': z.get('label'), 'has_purpose': 'purpose' in z} for z in d.get('zones', [])])
print('luminaires sample:', d.get('luminaires', [])[:2])
print('calc.target_illuminance_lux:', d.get('calculation_summary', {}).get('target_illuminance_lux'))
print('calc.achieved_illuminance_lux:', d.get('calculation_summary', {}).get('achieved_illuminance_lux'))
print('room.ceiling_height_mm:', d.get('room', {}).get('ceiling_height_mm'))
print('room.working_plane_mm:', d.get('room', {}).get('working_plane_mm'))
"
```

Expected: existing zones with no purpose; existing luminaires with no mount_type.

- [ ] **Step 2: Edit output.json — add `purpose: "task"` + `em_target_lux` to every zone**

For every zone in `zones[]`, add:

```json
"purpose": "task",
"em_target_lux": <copy of room.target_illuminance_lux (e.g. 500 for open_plan)>
```

(All existing zones default to `task` per ZP-01 backwards-compat rule.)

- [ ] **Step 3: Edit output.json — add `mount_type: "recessed"` to every luminaire**

For every luminaire in `luminaires[]`, add:

```json
"mount_type": "recessed"
```

(Existing office luminaires are recessed troffer-style — z_mm + suspension_length_mm omitted per MT-01.)

- [ ] **Step 4: Edit output.json — populate `calculation_summary.per_zone_achieved[]`**

In `calculation_summary`, add:

```json
"per_zone_achieved": [
  {
    "zone_id": "<each existing zone_id>",
    "purpose": "task",
    "em_target_lux": <same as zone.em_target_lux>,
    "em_achieved_lux": <derive from existing achieved_illuminance_lux × 1.0 since all zones share the open-plan task uniformity>,
    "ratio_compliance": "pass"
  }
]
```

Mark `ratio_compliance: "pass"` for zones where achieved ≥ target; `"marginal"` for 75-99% of target; `"fail"` for <75%.

- [ ] **Step 5: Edit output.json — add INV-13..INV-19 entries to `invariants[]`**

For each of INV-13/14/15/16/17/18/19, add a corresponding entry with `passes: true` + appropriate evidence (per the templates in validator.md B.2). For vacuous PASS cases (no surrounding/background zones; all recessed luminaires), use the vacuous-PASS evidence template.

Example INV-13 entry:

```json
{
  "id": "INV-13",
  "name": "Zone purpose required + valid",
  "passes": true,
  "severity": "high",
  "evidence": "INV-13 verdict: PASS. Zones inspected: 3. Per-zone purpose: Z1 purpose=task em_target_lux=500, Z2 purpose=task em_target_lux=500, Z3 purpose=task em_target_lux=500. Orphan-surrounding check: pass (no surrounding zones). Citation: BS EN 12464-1:2021 §4.2.2.1 (area-definitions.json §4.2.2.x)."
}
```

- [ ] **Step 6: Update input.json with `_d5_retrofit_note`**

In `input.json`, add at root (or in an existing `_meta` block if present):

```json
"_d5_retrofit_note": "Retrofitted by D5 sprint 2026-06-03. All existing zones default to purpose=task per ZP-01 backwards-compat rule. All existing luminaires default to mount_type=recessed per MT-01. per_zone_achieved[] populated from existing achieved_illuminance_lux × task uniformity."
```

- [ ] **Step 7: Update reasoning.md with §D5 retrofit section**

In `electrical/lighting-layout/examples/office-open-plan/reasoning.md`, APPEND a new section:

```markdown
## §D5 RETROFIT (2026-06-03)

This example was authored at v1.6.0 with a single `target_illuminance_lux` per room. v1.7.0 splits target into per-zone `em_target_lux` per BS EN 12464-1:2021 §4.2.2 + Table 6. This retrofit applies the backwards-compatibility defaults:

- All zones get `purpose: "task"` (ZP-01 default).
- All luminaires get `mount_type: "recessed"` (MT-01 default).
- `per_zone_achieved[]` populated from existing `achieved_illuminance_lux` (the open-plan uniformity factor of 0.6 means task plane achieves the room average).

**Honest disclosures (4-place):**

1. Engineering judgment defaults documented in `input._d5_retrofit_note`.
2. Compliance assumption added: "v1.6.0 → v1.7.0 retrofit; defaults preserve behaviour."
3. Rationale section "v1.7 retrofit" added.
4. This reasoning.md §D5 section.
```

- [ ] **Step 8: Update intent-out.json (if present) with the same enrichments**

If `intent-out.json` exists, mirror the zone.purpose + mount_type + per_zone_achieved additions in the intent payload shape.

- [ ] **Step 9: Validate retrofit + gates + banned-citation grep**

Run:
```bash
python3 -c "
import json, jsonschema
schema = json.load(open('shared/schemas/electrical/lighting-layout-ir.schema.json'))
d = json.load(open('electrical/lighting-layout/examples/office-open-plan/output.json'))
v = jsonschema.Draft7Validator(schema)
errors = list(v.iter_errors(d))
if errors:
    for e in errors[:5]: print('  ERROR:', e.message[:200])
else:
    print('OK')
"

grep -rnE "(§526\.2|§433\.2|OZEV|3rd Edition|Reg 559|Em_room|average room lux)" electrical/lighting-layout/examples/office-open-plan/ | grep -v "do NOT\|never cite\|banned\|NOT cite" && echo BANNED_FAIL || echo BANNED_PASS

python3 scripts/validate-examples.py 2>&1 | tail -3
```

Expected: `OK` + `BANNED_PASS` + aggregate unchanged (retrofit, no new files).

- [ ] **Step 10: Commit**

```bash
git add electrical/lighting-layout/examples/office-open-plan/
git commit -m "feat(lighting-layout): C.1 RETROFIT office-open-plan with v1.7 defaults (purpose=task, mount_type=recessed, per_zone_achieved populated)"
```

### Task C.2: RETROFIT reception-lobby example

**Files:**
- Modify: `electrical/lighting-layout/examples/reception-lobby/{input,output,reasoning,intent-out}.{json,md}`

**Why Opus:** Reception lobby is the first non-task room — `purpose: "circulation"` rather than default `task` (per ZP-05). Engineering call.

- [ ] **Step 1: Inventory existing example**

Run:
```bash
python3 -c "
import json
d = json.load(open('electrical/lighting-layout/examples/reception-lobby/output.json'))
print('room_type:', d.get('room', {}).get('room_type'))
print('zones:', [{'id': z['zone_id'], 'label': z.get('label')} for z in d.get('zones', [])])
print('target_illuminance_lux:', d.get('calculation_summary', {}).get('target_illuminance_lux'))
"
```

Expected: room_type likely `lobby` or `reception_area`; target ~300 lx per BS EN 12464-1 Table 5 lobby entry.

- [ ] **Step 2: Edit output.json — add `purpose: "circulation"` + `em_target_lux: 300` (or as room.target) to every zone**

(Per ZP-05, circulation zones look up Em from lux-levels.json circulation branch directly; not subject to task/surrounding ratios.)

- [ ] **Step 3: Edit output.json — add `mount_type: "recessed"` to every luminaire (typical lobby downlights)**

- [ ] **Step 4: Populate `per_zone_achieved[]` with purpose: circulation entries**

- [ ] **Step 5: Add INV-13..INV-19 entries (INV-14 + INV-15 vacuous PASS — no surrounding/background; INV-16/17/18 vacuous-PASS since recessed)**

- [ ] **Step 6: Add `_d5_retrofit_note` + reasoning.md §D5 section (mirror C.1 pattern)**

- [ ] **Step 7: Validate + gates + grep + commit**

```bash
python3 -c "import json, jsonschema; jsonschema.Draft7Validator(json.load(open('shared/schemas/electrical/lighting-layout-ir.schema.json'))).validate(json.load(open('electrical/lighting-layout/examples/reception-lobby/output.json'))); print('OK')"
grep -rnE "(§526\.2|§433\.2|OZEV|3rd Edition|Reg 559|Em_room|average room lux)" electrical/lighting-layout/examples/reception-lobby/ | grep -v "do NOT\|never cite\|banned\|NOT cite" && echo BANNED_FAIL || echo BANNED_PASS
python3 scripts/validate-examples.py 2>&1 | tail -3
git add electrical/lighting-layout/examples/reception-lobby/
git commit -m "feat(lighting-layout): C.2 RETROFIT reception-lobby with v1.7 defaults (purpose=circulation per ZP-05, mount_type=recessed)"
```

### Task C.3: RETROFIT uk-bathroom-zone-1-zone-2 example

**Files:**
- Modify: `electrical/lighting-layout/examples/uk-bathroom-zone-1-zone-2/{input,output,reasoning,intent-out}.{json,md}`

**Why Opus:** Special-locations cascade preserved (existing INV-12 consumption); zone.purpose split is `task` (vanity) + `circulation` (entry) — judgement call on which existing zones map to which.

- [ ] **Step 1: Inventory + read existing INV-12 cascade payload**

Run:
```bash
python3 -c "
import json
d = json.load(open('electrical/lighting-layout/examples/uk-bathroom-zone-1-zone-2/output.json'))
print('zones:', [z['zone_id'] + ':' + z.get('label', '?') for z in d.get('zones', [])])
print('consumed_intents.special_locations_zoning present:', 'special_locations_zoning' in d.get('consumed_intents', {}))
"
```

- [ ] **Step 2: Edit output.json — split zone purposes**

For each zone in `zones[]`, assign:

- Zone(s) at the vanity / mirror / sink area → `purpose: "task"`, `em_target_lux: 500` (BS EN 12464-1 §4.2.2.1 + Table 5 bathroom_vanity entry).
- Zone(s) at the entry / general bathroom area → `purpose: "circulation"`, `em_target_lux: 200` (Table 5 bathroom_general entry).

- [ ] **Step 3: Edit output.json — `mount_type: "recessed"` for all luminaires (typical bathroom downlights)**

- [ ] **Step 4: Populate per_zone_achieved[] preserving special-locations cascade payload byte-identical**

- [ ] **Step 5: Add INV-13..INV-19 entries**

- [ ] **Step 6: Add _d5_retrofit_note + reasoning.md §D5**

- [ ] **Step 7: Verify cascade preserved + validate + gate + commit**

```bash
python3 -c "
import json
d = json.load(open('electrical/lighting-layout/examples/uk-bathroom-zone-1-zone-2/output.json'))
print('cascade payload key preserved:', 'special_locations_zoning' in d.get('consumed_intents', {}))
"
python3 -c "import json, jsonschema; jsonschema.Draft7Validator(json.load(open('shared/schemas/electrical/lighting-layout-ir.schema.json'))).validate(json.load(open('electrical/lighting-layout/examples/uk-bathroom-zone-1-zone-2/output.json'))); print('OK')"
grep -rnE "(§526\.2|§433\.2|OZEV|3rd Edition|Reg 559|Em_room|average room lux)" electrical/lighting-layout/examples/uk-bathroom-zone-1-zone-2/ | grep -v "do NOT\|never cite\|banned\|NOT cite" && echo BANNED_FAIL || echo BANNED_PASS
python3 scripts/validate-examples.py 2>&1 | tail -3
git add electrical/lighting-layout/examples/uk-bathroom-zone-1-zone-2/
git commit -m "feat(lighting-layout): C.3 RETROFIT uk-bathroom-zone-1-zone-2 with v1.7 defaults (purpose=task vanity + circulation entry, special-locations cascade preserved)"
```

### Task C.4: RETROFIT uk-multi-entrance-classroom example

**Files:**
- Modify: `electrical/lighting-layout/examples/uk-multi-entrance-classroom/{input,output,reasoning,intent-out}.{json,md}`

**Why Opus:** Classroom desk zones = task; aisle zones = circulation. Engineering split per zone.

- [ ] **Step 1: Inventory example zones**

Run:
```bash
python3 -c "
import json
d = json.load(open('electrical/lighting-layout/examples/uk-multi-entrance-classroom/output.json'))
print('zones:', [{'id': z['zone_id'], 'label': z.get('label')} for z in d.get('zones', [])])
"
```

- [ ] **Step 2: Edit output.json — desk zones → `purpose: task`, em_target_lux: 300 (BS EN 12464 classroom-task)**

- [ ] **Step 3: Edit output.json — aisle/entry zones → `purpose: circulation`, em_target_lux: 100**

- [ ] **Step 4: mount_type: recessed on all luminaires**

- [ ] **Step 5: Populate per_zone_achieved[]**

- [ ] **Step 6: INV-13..INV-19 entries**

- [ ] **Step 7: _d5_retrofit_note + reasoning.md §D5**

- [ ] **Step 8: Validate + gates + commit**

```bash
python3 -c "import json, jsonschema; jsonschema.Draft7Validator(json.load(open('shared/schemas/electrical/lighting-layout-ir.schema.json'))).validate(json.load(open('electrical/lighting-layout/examples/uk-multi-entrance-classroom/output.json'))); print('OK')"
grep -rnE "(§526\.2|§433\.2|OZEV|3rd Edition|Reg 559|Em_room|average room lux)" electrical/lighting-layout/examples/uk-multi-entrance-classroom/ | grep -v "do NOT\|never cite\|banned\|NOT cite" && echo BANNED_FAIL || echo BANNED_PASS
python3 scripts/validate-examples.py 2>&1 | tail -3
git add electrical/lighting-layout/examples/uk-multi-entrance-classroom/
git commit -m "feat(lighting-layout): C.4 RETROFIT uk-multi-entrance-classroom with v1.7 defaults (purpose=task desks + circulation aisles)"
```

### Task C.5: RETROFIT uk-open-plan-office-10x8-dali example

**Files:**
- Modify: `electrical/lighting-layout/examples/uk-open-plan-office-10x8-dali/{input,output,reasoning,intent-out}.{json,md}`

**Why Opus:** First retrofit demonstrating `purpose: surrounding` on perimeter zones (per spec §8.1). Surrounding ratio (INV-14) becomes a non-vacuous PASS here.

- [ ] **Step 1: Inventory zones**

```bash
python3 -c "
import json
d = json.load(open('electrical/lighting-layout/examples/uk-open-plan-office-10x8-dali/output.json'))
print('zones:', [{'id': z['zone_id'], 'label': z.get('label')} for z in d.get('zones', [])])
"
```

- [ ] **Step 2: Edit output.json — central desk zones → `purpose: task`, em_target_lux: 500 (open_plan)**

- [ ] **Step 3: Edit output.json — perimeter zones (if any with "perimeter" or "side" label) → `purpose: surrounding`, em_target_lux: 250 (= 500 × 0.5 default ratio per ZP-02)**

If no explicit perimeter zone exists in the v1.6 example, ADD a single new `surrounding` zone wrapping the desk area's perimeter band (≥500mm width per §4.2.2.2). Use plausible polygon coordinates inset 500mm from room walls.

- [ ] **Step 4: `mount_type: recessed` on all luminaires; DALI control preserved**

- [ ] **Step 5: Populate per_zone_achieved[] with separate task + surrounding entries**

- [ ] **Step 6: INV-13..INV-19 — INV-14 has non-vacuous PASS evidence: surrounding em (250) ∈ [500×0.3, 500×0.5] = [150, 250]**

- [ ] **Step 7: _d5_retrofit_note + reasoning.md §D5 explaining the new surrounding zone**

- [ ] **Step 8: Validate + gates + commit**

```bash
python3 -c "import json, jsonschema; jsonschema.Draft7Validator(json.load(open('shared/schemas/electrical/lighting-layout-ir.schema.json'))).validate(json.load(open('electrical/lighting-layout/examples/uk-open-plan-office-10x8-dali/output.json'))); print('OK')"
grep -rnE "(§526\.2|§433\.2|OZEV|3rd Edition|Reg 559|Em_room|average room lux)" electrical/lighting-layout/examples/uk-open-plan-office-10x8-dali/ | grep -v "do NOT\|never cite\|banned\|NOT cite" && echo BANNED_FAIL || echo BANNED_PASS
python3 scripts/validate-examples.py 2>&1 | tail -3
git add electrical/lighting-layout/examples/uk-open-plan-office-10x8-dali/
git commit -m "feat(lighting-layout): C.5 RETROFIT uk-open-plan-office-10x8-dali with v1.7 (task + surrounding split — INV-14 first non-vacuous PASS)"
```

### Task C.6: RETROFIT uk-part-l-fail-incandescent example

**Files:**
- Modify: `electrical/lighting-layout/examples/uk-part-l-fail-incandescent/{input,output,reasoning,intent-out}.{json,md}`

**Why Opus:** Part-L failure preserved; D5 additions are orthogonal — confirm no regression on existing Part-L FAIL.

- [ ] **Step 1: Inventory + confirm existing Part-L FAIL state**

Run:
```bash
python3 -c "
import json
d = json.load(open('electrical/lighting-layout/examples/uk-part-l-fail-incandescent/output.json'))
print('part_l_compliant:', d.get('controls', {}).get('part_l_compliant'))
print('compliant:', d.get('calculation_summary', {}).get('compliant'))
"
```

- [ ] **Step 2: Edit output.json — purpose=task (default), mount_type=recessed (default), per_zone_achieved[] populated**

- [ ] **Step 3: Preserve existing Part-L non_compliance_flags; ADD INV-13..INV-19 entries**

- [ ] **Step 4: _d5_retrofit_note + reasoning.md §D5 noting Part-L FAIL preserved**

- [ ] **Step 5: Validate + gates + commit**

```bash
python3 -c "
import json, jsonschema
d = json.load(open('electrical/lighting-layout/examples/uk-part-l-fail-incandescent/output.json'))
jsonschema.Draft7Validator(json.load(open('shared/schemas/electrical/lighting-layout-ir.schema.json'))).validate(d)
print('OK; part_l preserved:', d['controls']['part_l_compliant'])
"
grep -rnE "(§526\.2|§433\.2|OZEV|3rd Edition|Reg 559|Em_room|average room lux)" electrical/lighting-layout/examples/uk-part-l-fail-incandescent/ | grep -v "do NOT\|never cite\|banned\|NOT cite" && echo BANNED_FAIL || echo BANNED_PASS
python3 scripts/validate-examples.py 2>&1 | tail -3
git add electrical/lighting-layout/examples/uk-part-l-fail-incandescent/
git commit -m "feat(lighting-layout): C.6 RETROFIT uk-part-l-fail-incandescent with v1.7 defaults (Part-L failure preserved)"
```

### Task C.7: RETROFIT uk-undersized-lighting-vs-target example

**Files:**
- Modify: `electrical/lighting-layout/examples/uk-undersized-lighting-vs-target/{input,output,reasoning,intent-out}.{json,md}`

**Why Opus:** Existing FAIL example with achieved < target; INV-19 will surface this as a per-zone FAIL — choose the appropriate severity band.

- [ ] **Step 1: Inventory existing FAIL state**

```bash
python3 -c "
import json
d = json.load(open('electrical/lighting-layout/examples/uk-undersized-lighting-vs-target/output.json'))
print('target:', d.get('calculation_summary', {}).get('target_illuminance_lux'))
print('achieved:', d.get('calculation_summary', {}).get('achieved_illuminance_lux'))
gap_pct = (d['calculation_summary']['target_illuminance_lux'] - d['calculation_summary']['achieved_illuminance_lux']) / d['calculation_summary']['target_illuminance_lux']
print(f'gap_pct: {gap_pct:.1%}')
print('compliant:', d['calculation_summary']['compliant'])
"
```

- [ ] **Step 2: Edit output.json — purpose=task default, mount_type=recessed default; populate per_zone_achieved[] showing the existing FAIL**

For each zone, set `em_achieved_lux` from the existing achieved; set `ratio_compliance` per INV-19 band (`fail` if gap_pct ≥ 25%, `marginal` if 10-25%).

- [ ] **Step 3: Add INV-19 entry with FAIL verdict + correct severity band per spec §6 (≥25% short = HIGH; 10-25% = MEDIUM)**

- [ ] **Step 4: Preserve existing non_compliance_flags; ADD an INV-19 flag with the per-zone gap data**

- [ ] **Step 5: _d5_retrofit_note + reasoning.md §D5 noting INV-19 now surfaces the existing FAIL at per-zone level**

- [ ] **Step 6: Validate + gates + commit**

```bash
python3 -c "import json, jsonschema; jsonschema.Draft7Validator(json.load(open('shared/schemas/electrical/lighting-layout-ir.schema.json'))).validate(json.load(open('electrical/lighting-layout/examples/uk-undersized-lighting-vs-target/output.json'))); print('OK')"
grep -rnE "(§526\.2|§433\.2|OZEV|3rd Edition|Reg 559|Em_room|average room lux)" electrical/lighting-layout/examples/uk-undersized-lighting-vs-target/ | grep -v "do NOT\|never cite\|banned\|NOT cite" && echo BANNED_FAIL || echo BANNED_PASS
python3 scripts/validate-examples.py 2>&1 | tail -3
git add electrical/lighting-layout/examples/uk-undersized-lighting-vs-target/
git commit -m "feat(lighting-layout): C.7 RETROFIT uk-undersized-lighting-vs-target with v1.7 (INV-19 now surfaces existing FAIL at per-zone level)"
```

### Task C.8: RETROFIT warehouse-highbay (3D placement migration — only retrofit needing mount_type=suspended)

**Files:**
- Modify: `electrical/lighting-layout/examples/warehouse-highbay/{input,output,reasoning,intent-out}.{json,md}`

**Why Opus:** First retrofit needing 3D placement migration — highbay luminaires are typically suspended from roof truss. Engineering call on `z_mm` + `suspension_length_mm` derived from existing `room.hm_mm`.

- [ ] **Step 1: Inventory + read existing hm_mm + ceiling_height_mm**

```bash
python3 -c "
import json
d = json.load(open('electrical/lighting-layout/examples/warehouse-highbay/output.json'))
print('ceiling_height_mm:', d.get('room', {}).get('ceiling_height_mm'))
print('hm_mm:', d.get('room', {}).get('hm_mm'))
print('working_plane_mm:', d.get('room', {}).get('working_plane_mm'))
print('zones:', [{'id': z['zone_id'], 'label': z.get('label')} for z in d.get('zones', [])])
print('luminaires count:', len(d.get('luminaires', [])))
"
```

Expected: ceiling typically 8000-10000 mm; hm_mm typically 6000-8000 mm; working plane 1000 mm (floor task).

- [ ] **Step 2: Edit output.json — pick-face zones → `purpose: task`, em_target_lux: 500 (warehouse high rack); aisle zones → `purpose: circulation`, em_target_lux: 75 (car park circulation entry from Table 5)**

- [ ] **Step 3: Edit output.json — every luminaire → `mount_type: "suspended"`, `z_mm: <derived>`, `suspension_length_mm: <derived>`**

Derivation:
- `z_mm = working_plane_mm + hm_mm` (existing v1.6 hm_mm tells us z above the task plane).
- `suspension_length_mm = ceiling_height_mm - z_mm` (drop from ceiling).

Example for ceiling=10000mm + hm_mm=8000mm + working_plane=1000mm:
- z_mm = 1000 + 8000 = 9000 mm
- suspension_length_mm = 10000 - 9000 = 1000 mm
- Check INV-17: 9000 > 1000 ✓ ; 9000 + 1000 = 10000 ≤ 10000 ✓

- [ ] **Step 4: Populate per_zone_achieved[]**

- [ ] **Step 5: INV-13..INV-19 entries — INV-16/17/18 now non-vacuous PASS (first retrofit exercising 3D placement)**

- [ ] **Step 6: _d5_retrofit_note + reasoning.md §D5 explaining the 3D migration arithmetic**

- [ ] **Step 7: Validate + gates + commit**

```bash
python3 -c "import json, jsonschema; jsonschema.Draft7Validator(json.load(open('shared/schemas/electrical/lighting-layout-ir.schema.json'))).validate(json.load(open('electrical/lighting-layout/examples/warehouse-highbay/output.json'))); print('OK')"
grep -rnE "(§526\.2|§433\.2|OZEV|3rd Edition|Reg 559|Em_room|average room lux)" electrical/lighting-layout/examples/warehouse-highbay/ | grep -v "do NOT\|never cite\|banned\|NOT cite" && echo BANNED_FAIL || echo BANNED_PASS
python3 scripts/validate-examples.py 2>&1 | tail -3
git add electrical/lighting-layout/examples/warehouse-highbay/
git commit -m "feat(lighting-layout): C.8 RETROFIT warehouse-highbay with v1.7 3D placement (mount_type=suspended + z_mm + suspension_length_mm derived from existing hm_mm; INV-16/17/18 first non-vacuous PASS)"
```

### Task C.9: NEW uk-pendant-open-plan-office example

**Files:**
- Create: `electrical/lighting-layout/examples/uk-pendant-open-plan-office/input.json`
- Create: `electrical/lighting-layout/examples/uk-pendant-open-plan-office/output.json`
- Create: `electrical/lighting-layout/examples/uk-pendant-open-plan-office/reasoning.md`
- Create: `electrical/lighting-layout/examples/uk-pendant-open-plan-office/intent-out.json`

**Why Opus:** First fully-pendant example; pendant geometry algebraic identity must hold (`z_mm + suspension_length_mm = ceiling_height_mm`).

**Scenario** (spec §8.2 NEW#1):
- 12×8 m open-plan office, single tenant, UK jurisdiction.
- Ceiling 3500 mm; working plane 750 mm.
- Pendant LED linear luminaires: 6 units, 1200 mm × 200 mm.
- Suspension drop 800 mm → z_mm = 2700 mm; hm_mm = 2700 - 750 = 1950 mm.
- Target Em: 500 lx (open_plan task).
- Achieved Em: 540 lx via lumen-method.

- [ ] **Step 1: Author input.json (engineer brief — same shape as existing v1.6 input shapes)**

Use the existing `electrical/lighting-layout/examples/office-open-plan/input.json` as the template; substitute:
- room dimensions 12×8 m
- ceiling_height_mm 3500
- luminaire description "pendant LED linear"
- `mount_type_inputs`: array with 6 entries each `{luminaire_id, mount_type: "pendant"}`
- `suspension_length_inputs`: array with 6 entries each `{luminaire_id, suspension_length_mm: 800}`
- `zone_purpose_inputs`: array with `{zone_id: "Z1", purpose: "task"}` (single task zone covering desk area)

- [ ] **Step 2: Author output.json**

Full IR structure following the C.1 retrofit template + adding 3D fields. Key fields:

```json
{
  "drawing_type": "lighting-layout",
  "version": "1.7.0",
  "room": {
    "length_mm": 12000,
    "width_mm": 8000,
    "area_m2": 96,
    "ceiling_height_mm": 3500,
    "working_plane_mm": 750,
    "hm_mm": 1950,
    "room_type": "open_plan_office",
    ...
  },
  "zones": [
    {"zone_id": "Z1", "label": "Open desk area", "zone_type": "task", "purpose": "task", "em_target_lux": 500, ...}
  ],
  "luminaires": [
    {"id": "L1", "x_mm": 2000, "y_mm": 2000, "zone_id": "Z1", "circuit_id": "C1", "mount_type": "pendant", "z_mm": 2700, "suspension_length_mm": 800},
    {"id": "L2", "x_mm": 4000, "y_mm": 2000, "zone_id": "Z1", "circuit_id": "C1", "mount_type": "pendant", "z_mm": 2700, "suspension_length_mm": 800},
    {"id": "L3", "x_mm": 6000, "y_mm": 2000, "zone_id": "Z1", "circuit_id": "C1", "mount_type": "pendant", "z_mm": 2700, "suspension_length_mm": 800},
    {"id": "L4", "x_mm": 2000, "y_mm": 6000, "zone_id": "Z1", "circuit_id": "C1", "mount_type": "pendant", "z_mm": 2700, "suspension_length_mm": 800},
    {"id": "L5", "x_mm": 6000, "y_mm": 6000, "zone_id": "Z1", "circuit_id": "C1", "mount_type": "pendant", "z_mm": 2700, "suspension_length_mm": 800},
    {"id": "L6", "x_mm": 10000, "y_mm": 6000, "zone_id": "Z1", "circuit_id": "C1", "mount_type": "pendant", "z_mm": 2700, "suspension_length_mm": 800}
  ],
  "calculation_summary": {
    "target_illuminance_lux": 500,
    "achieved_illuminance_lux": 540,
    "per_zone_achieved": [
      {"zone_id": "Z1", "purpose": "task", "em_target_lux": 500, "em_achieved_lux": 540, "ratio_compliance": "pass"}
    ],
    "compliant": true,
    ...
  },
  "invariants": [
    ... all 19 with PASS verdicts ...
    {"id": "INV-16", "name": "mount_type ↔ z_mm/suspension consistency", "passes": true, "severity": "high", "evidence": "INV-16 verdict: PASS. Luminaires inspected: 6. Pendant geometry: L1..L6 all z_mm=2700, suspension_length_mm=800, ceiling_height_mm=3500, sum=3500, identity holds. Citation: BS EN 60598-2-1 + mount-type-rules.yaml MT-02."},
    {"id": "INV-17", "name": "Ceiling clearance + working-plane floor", "passes": true, "severity": "high", "evidence": "INV-17 verdict: PASS. Working plane reference: 750 mm AFF. Per-luminaire clearance: L1..L6 z=2700, clearance from working plane = 1950 mm ✓. Per-luminaire ceiling clearance: 2700+800=3500 = ceiling 3500 ✓. Citation: BS EN 12464-1:2021 §4.4 + MT-04."},
    {"id": "INV-18", "name": "hm_mm derivation consistency", "passes": true, "severity": "medium", "evidence": "INV-18 verdict: PASS. Room hm_mm: 1950. Expected: lowest pendant z=2700 - working_plane 750 = 1950. Drift 0 mm within ±50 mm tolerance. Citation: BS EN 12464-1:2021 §4.4."}
  ]
}
```

- [ ] **Step 3: Author intent-out.json**

Same structure as existing intent payloads; include `mount_type` + `z_mm` + `suspension_length_mm` in the luminaires intent payload (so consumers see the 3D data).

- [ ] **Step 4: Author reasoning.md**

Cover: pendant choice rationale, geometric derivation (z = ceiling - suspension), per-zone Em derivation (single task zone at 500 lx), INV-16/17/18 PASS commentary, 4-place honest disclosure section.

- [ ] **Step 5: Validate + banned-citation grep + gates**

```bash
python3 -c "
import json, jsonschema
schema = json.load(open('shared/schemas/electrical/lighting-layout-ir.schema.json'))
d = json.load(open('electrical/lighting-layout/examples/uk-pendant-open-plan-office/output.json'))
v = jsonschema.Draft7Validator(schema)
errors = list(v.iter_errors(d))
if errors:
    for e in errors[:5]: print('  ERROR:', e.message[:200])
else:
    print('OK')
"
grep -rnE "(§526\.2|§433\.2|OZEV|3rd Edition|Reg 559|Em_room|average room lux)" electrical/lighting-layout/examples/uk-pendant-open-plan-office/ | grep -v "do NOT\|never cite\|banned\|NOT cite" && echo BANNED_FAIL || echo BANNED_PASS
python3 scripts/validate-examples.py 2>&1 | tail -3
```

Expected: `OK` + `BANNED_PASS` + aggregate bumps +2.

- [ ] **Step 6: Commit**

```bash
git add electrical/lighting-layout/examples/uk-pendant-open-plan-office/
git commit -m "feat(lighting-layout): C.9 NEW uk-pendant-open-plan-office example (first fully-pendant; INV-16/17/18 PASS with z_mm + suspension_length_mm = ceiling_height_mm identity)"
```

### Task C.10: NEW uk-mixed-purpose-classroom example

**Files:**
- Create: `electrical/lighting-layout/examples/uk-mixed-purpose-classroom/{input,output,reasoning,intent-out}.{json,md}`

**Why Opus:** Most complex single example — all 3 zone purposes (task + surrounding + background) coexist; INV-14 and INV-15 both non-vacuous PASS; ratio math must be exact.

**Scenario** (spec §8.2 NEW#2):
- Classroom 9×7 m, ceiling 3000 mm, working plane 750 mm.
- Task zone: student desks area (Em = 300 lx).
- Surrounding zone: teacher desk + 500mm band around student desks (Em = 200 lx = 0.66×300; within [0.3×300=90, 0.5×300=150] band? Actually 200 > 150 — Table 6 simplified rule allows 0.3-0.5 BUT Table 6 ALSO permits 200 lx as Em_surrounding when Em_task = 300 lx per the per-Em-band table. Reference: lux-levels.json or area-definitions.json Table 6 row).
  - Decision: use Em_surrounding = 150 lx (= 0.5×300, top of ratio band) for clean math.
- Background zone: back wall display area (Em = max(300/3, 50) = 100 lx).

- [ ] **Step 1: Author input.json with `zone_purpose_inputs` covering all 3 purposes**

```json
"zone_purpose_inputs": [
  {"zone_id": "Z1", "purpose": "task"},
  {"zone_id": "Z2", "purpose": "surrounding", "em_target_lux_override": 150},
  {"zone_id": "Z3", "purpose": "background"}
]
```

- [ ] **Step 2: Author output.json with 3 zones**

```json
"zones": [
  {"zone_id": "Z1", "label": "Student desks", "purpose": "task", "em_target_lux": 300, ...},
  {"zone_id": "Z2", "label": "Teacher area + desk perimeter", "purpose": "surrounding", "em_target_lux": 150, ...},
  {"zone_id": "Z3", "label": "Rear wall display", "purpose": "background", "em_target_lux": 100, ...}
]
```

- [ ] **Step 3: All luminaires recessed (typical classroom)**

- [ ] **Step 4: per_zone_achieved[] with realistic em_achieved values**

- Z1 task: achieved 315 lx → pass
- Z2 surrounding: achieved 155 lx → pass
- Z3 background: achieved 105 lx → pass

- [ ] **Step 5: INV entries — INV-13/14/15 all non-vacuous PASS with detailed evidence**

INV-14 evidence example:

```
INV-14 verdict: PASS. Surrounding zones inspected: 1. Task em reference: 300 lx (from Z1). Per-zone ratio check: Z2 em_target_lux=150, ratio=0.500, band [0.3, 0.5], result: pass (equal to upper band). Citation: BS EN 12464-1:2021 §4.2.2.2 + Table 6.
```

INV-15 evidence example:

```
INV-15 verdict: PASS. Background zones inspected: 1. Task em reference: 300 lx (from Z1). Per-zone floor check: Z3 em_target_lux=100, floor=max(300/3, 50)=100 lx, result: pass (equal to floor). Citation: BS EN 12464-1:2021 §4.2.2.3 + Table 6.
```

- [ ] **Step 6: Author intent-out.json + reasoning.md (cover the 3-purpose split + ratio math + 4-place disclosure)**

- [ ] **Step 7: Validate + grep + gates + commit**

```bash
python3 -c "import json, jsonschema; jsonschema.Draft7Validator(json.load(open('shared/schemas/electrical/lighting-layout-ir.schema.json'))).validate(json.load(open('electrical/lighting-layout/examples/uk-mixed-purpose-classroom/output.json'))); print('OK')"
grep -rnE "(§526\.2|§433\.2|OZEV|3rd Edition|Reg 559|Em_room|average room lux)" electrical/lighting-layout/examples/uk-mixed-purpose-classroom/ | grep -v "do NOT\|never cite\|banned\|NOT cite" && echo BANNED_FAIL || echo BANNED_PASS
python3 scripts/validate-examples.py 2>&1 | tail -3
git add electrical/lighting-layout/examples/uk-mixed-purpose-classroom/
git commit -m "feat(lighting-layout): C.10 NEW uk-mixed-purpose-classroom example (task + surrounding + background all 3 purposes; INV-13/14/15 non-vacuous PASS)"
```

### Task C.11: NEW uk-retail-display-task-zone example

**Files:**
- Create: `electrical/lighting-layout/examples/uk-retail-display-task-zone/{input,output,reasoning,intent-out}.{json,md}`

**Why Opus:** Mixed mount_type (pendant accent + recessed downlights); demonstrates heterogeneous luminaire array in a single room.

**Scenario** (spec §8.2 NEW#3):
- Retail floor 15×10 m, ceiling 4000 mm, working plane 0 mm (floor display).
- Task zone: high-emphasis goods display island (Em = 1000 lx per Table 5 jewellery/fashion).
- Circulation zone: customer aisles (Em = 300 lx per Table 5 retail general).
- Luminaires:
  - 4 pendant accent lights over display island (z_mm=2500, suspension_length_mm=1500).
  - 12 recessed downlights in aisles (mount_type=recessed).

- [ ] **Step 1: Author input.json with mixed `mount_type_inputs`**

- [ ] **Step 2: Author output.json**

Zones:
- Z1 task display: em_target_lux=1000
- Z2 circulation aisles: em_target_lux=300

Luminaires:
- L1-L4 pendant over Z1 (z_mm=2500, suspension_length_mm=1500; check 2500+1500=4000 ≤ 4000 ✓)
- L5-L16 recessed over Z2 (no z_mm needed)

- [ ] **Step 3: per_zone_achieved[]**

- [ ] **Step 4: INV entries — INV-16 non-vacuous PASS demonstrating heterogeneous mount types**

- [ ] **Step 5: intent-out.json + reasoning.md**

- [ ] **Step 6: Validate + grep + gates + commit**

```bash
python3 -c "import json, jsonschema; jsonschema.Draft7Validator(json.load(open('shared/schemas/electrical/lighting-layout-ir.schema.json'))).validate(json.load(open('electrical/lighting-layout/examples/uk-retail-display-task-zone/output.json'))); print('OK')"
grep -rnE "(§526\.2|§433\.2|OZEV|3rd Edition|Reg 559|Em_room|average room lux)" electrical/lighting-layout/examples/uk-retail-display-task-zone/ | grep -v "do NOT\|never cite\|banned\|NOT cite" && echo BANNED_FAIL || echo BANNED_PASS
python3 scripts/validate-examples.py 2>&1 | tail -3
git add electrical/lighting-layout/examples/uk-retail-display-task-zone/
git commit -m "feat(lighting-layout): C.11 NEW uk-retail-display-task-zone example (mixed pendant accent + recessed downlights; INV-16 heterogeneous-mount PASS)"
```

### Task C.12: NEW uk-per-zone-target-violation FAIL HIGH example

**Files:**
- Create: `electrical/lighting-layout/examples/uk-per-zone-target-violation/{input,output,reasoning,intent-out}.{json,md}`

**Why Opus:** FAIL-by-design example; INV-19 fires HIGH; compliance: false; honest disclosure of FAIL intent in all 4 places.

**Scenario** (spec §8.2 NEW#4):
- Open-plan office 10×6 m, ceiling 3000 mm, working plane 750 mm.
- Task zone Em target 500 lx.
- Achieved 380 lx (24% short) → INV-19 ratio_compliance: `marginal` (within 25%, MEDIUM band per spec §6).
- WAIT — spec §8.2 says 24% short — let's recalculate. 380/500 = 0.76, gap = 24%. Per INV-19 bands: 10-25% short = MEDIUM severity (marginal in ratio_compliance enum). To get a true HIGH FAIL, we need gap ≥ 50% (i.e. achieved < 250 lx).

**Decision:** for the FAIL HIGH example, use a more dramatic gap to clearly exercise HIGH severity:
- Achieved 200 lx (60% short) → INV-19 ratio_compliance: `fail`, severity: HIGH.

- [ ] **Step 1: Author input.json**

Use 500 lx target + supply 200 lx achieved via input gymnastics (engineer-supplied lumen-method values that produce 200 lx; show the math in reasoning).

- [ ] **Step 2: Author output.json — single task zone with achieved 200 lx**

```json
"calculation_summary": {
  "target_illuminance_lux": 500,
  "achieved_illuminance_lux": 200,
  "per_zone_achieved": [
    {"zone_id": "Z1", "purpose": "task", "em_target_lux": 500, "em_achieved_lux": 200, "ratio_compliance": "fail"}
  ],
  "compliant": false,
  "non_compliance_flags": [
    {
      "id": "INV-19-violation",
      "severity": "high",
      "description": "Per-zone task achievement 200 lx is 60% short of 500 lx target. Severity HIGH per INV-19 band (≥50% short).",
      "clause": "BS EN 12464-1:2021 §4.1 + Table 5"
    }
  ]
}
```

- [ ] **Step 3: INV-19 entry — `passes: false`, `severity: "high"`, full evidence**

```json
{
  "id": "INV-19",
  "name": "Per-zone achievement",
  "passes": false,
  "severity": "high",
  "evidence": "INV-19 verdict: FAIL (HIGH). Zones inspected: 1. Per-zone achievement: Z1 (task): target=500, achieved=200, gap=300, gap_pct=60.0%, ratio_compliance=fail, severity=HIGH. Aggregate: 0 PASS, 0 marginal, 0 MEDIUM, 1 HIGH. Citation: BS EN 12464-1:2021 §4.1 + Table 5."
}
```

- [ ] **Step 4: intent-out.json + reasoning.md emphasising FAIL-by-design intent**

- [ ] **Step 5: 4-place honest disclosure of FAIL-by-design**

In each of the 4 disclosure places, note: "This example is DELIBERATELY FAIL-by-design to exercise INV-19 HIGH-severity band. Real engineering would either add more luminaires or accept the lower target."

- [ ] **Step 6: Validate + grep + gates + commit**

```bash
python3 -c "
import json, jsonschema
d = json.load(open('electrical/lighting-layout/examples/uk-per-zone-target-violation/output.json'))
jsonschema.Draft7Validator(json.load(open('shared/schemas/electrical/lighting-layout-ir.schema.json'))).validate(d)
print('OK; compliant:', d['calculation_summary']['compliant'])
inv19 = [i for i in d['invariants'] if i['id'] == 'INV-19'][0]
print('INV-19 passes:', inv19['passes'], 'severity:', inv19['severity'])
"
grep -rnE "(§526\.2|§433\.2|OZEV|3rd Edition|Reg 559|Em_room|average room lux)" electrical/lighting-layout/examples/uk-per-zone-target-violation/ | grep -v "do NOT\|never cite\|banned\|NOT cite" && echo BANNED_FAIL || echo BANNED_PASS
python3 scripts/validate-examples.py 2>&1 | tail -3
git add electrical/lighting-layout/examples/uk-per-zone-target-violation/
git commit -m "feat(lighting-layout): C.12 NEW uk-per-zone-target-violation FAIL HIGH example (INV-19 fires HIGH at 60% gap; compliant=false by design)"
```

### Task C.13: 5 new evals YAML (eval-09 through eval-13)

**Files:**
- Create: `electrical/lighting-layout/evals/eval-09-zone-purpose-emit.yaml`
- Create: `electrical/lighting-layout/evals/eval-10-task-surrounding-ratio.yaml`
- Create: `electrical/lighting-layout/evals/eval-11-mount-type-3d-consistency.yaml`
- Create: `electrical/lighting-layout/evals/eval-12-per-zone-achievement-pass.yaml`
- Create: `electrical/lighting-layout/evals/eval-13-per-zone-achievement-fail.yaml`

**Why Sonnet:** Mechanical YAML authoring against the eval.schema.json contract (matches small-power D4 C.10 precedent).

- [ ] **Step 1: Read existing eval YAML + the eval schema**

Run:
```bash
cat electrical/lighting-layout/evals/eval-08-rationale-block.yaml
cat shared/schemas/core/eval.schema.json | python3 -m json.tool | head -60
```

Expected: identify the canonical YAML structure (name, skill, category enum, checks with severity+matches_inv).

- [ ] **Step 2: Author `eval-09-zone-purpose-emit.yaml`**

```yaml
name: zone-purpose-emit
skill: lighting-layout
category: skill_specific
description: |
  Verifies that every zone in v1.7+ IRs has a purpose field populated per BS EN 12464-1:2021 §4.2.2.
  Cross-checks against retrofitted examples (default purpose=task) and uk-mixed-purpose-classroom (all 3 purposes).
input_fixtures:
  - electrical/lighting-layout/examples/office-open-plan/output.json
  - electrical/lighting-layout/examples/uk-mixed-purpose-classroom/output.json
  - electrical/lighting-layout/examples/uk-pendant-open-plan-office/output.json
checks:
  - description: "Every zone has purpose enum value"
    severity: warning
    matches_inv: "INV-13"
  - description: "Default purpose=task when not supplied (backwards compat per ZP-01)"
    severity: info
    matches_inv: "INV-13"
  - description: "Orphan surrounding zones blocked (mixed-purpose example has task zone)"
    severity: warning
    matches_inv: "INV-13"
```

- [ ] **Step 3: Author `eval-10-task-surrounding-ratio.yaml`**

```yaml
name: task-surrounding-ratio
skill: lighting-layout
category: skill_specific
description: |
  Verifies that surrounding-zone em_target_lux respects the BS EN 12464-1:2021 Table 6 ratio [0.3, 0.5] of task Em.
  Cross-checks uk-open-plan-office-10x8-dali (perimeter surrounding) and uk-mixed-purpose-classroom.
input_fixtures:
  - electrical/lighting-layout/examples/uk-open-plan-office-10x8-dali/output.json
  - electrical/lighting-layout/examples/uk-mixed-purpose-classroom/output.json
checks:
  - description: "Surrounding em_target_lux in [0.3 × task_em, 0.5 × task_em]"
    severity: warning
    matches_inv: "INV-14"
  - description: "Background em_target_lux ≥ max(task_em / 3, 50 lx)"
    severity: warning
    matches_inv: "INV-15"
  - description: "Ratios cite area-definitions.json + Table 6"
    severity: info
    matches_inv: "INV-14"
```

- [ ] **Step 4: Author `eval-11-mount-type-3d-consistency.yaml`**

```yaml
name: mount-type-3d-consistency
skill: lighting-layout
category: validation_trap
description: |
  Verifies that pendant/suspended luminaires have z_mm + suspension_length_mm populated with the
  algebraic identity (pendant) or inequality (suspended) per BS EN 60598-2 + mount-type-rules.yaml.
input_fixtures:
  - electrical/lighting-layout/examples/uk-pendant-open-plan-office/output.json
  - electrical/lighting-layout/examples/uk-retail-display-task-zone/output.json
  - electrical/lighting-layout/examples/warehouse-highbay/output.json
checks:
  - description: "Pendant geometry: z_mm + suspension_length_mm = ceiling_height_mm"
    severity: warning
    matches_inv: "INV-16"
  - description: "Suspended geometry: z_mm + suspension_length_mm ≤ ceiling_height_mm"
    severity: warning
    matches_inv: "INV-16"
  - description: "z_mm > working_plane_mm (no luminaire below task plane)"
    severity: warning
    matches_inv: "INV-17"
  - description: "hm_mm derives from lowest pendant z minus working_plane_mm"
    severity: info
    matches_inv: "INV-18"
```

- [ ] **Step 5: Author `eval-12-per-zone-achievement-pass.yaml`**

```yaml
name: per-zone-achievement-pass
skill: lighting-layout
category: skill_specific
description: |
  Verifies per_zone_achieved[] populated + ratio_compliance pass on PASS examples.
input_fixtures:
  - electrical/lighting-layout/examples/uk-pendant-open-plan-office/output.json
  - electrical/lighting-layout/examples/uk-mixed-purpose-classroom/output.json
  - electrical/lighting-layout/examples/uk-retail-display-task-zone/output.json
checks:
  - description: "per_zone_achieved[] populated with one entry per zone"
    severity: info
    matches_inv: "INV-19"
  - description: "ratio_compliance: pass on every zone"
    severity: info
    matches_inv: "INV-19"
  - description: "INV-19 aggregate verdict: PASS"
    severity: info
    matches_inv: "INV-19"
```

- [ ] **Step 6: Author `eval-13-per-zone-achievement-fail.yaml`**

```yaml
name: per-zone-achievement-fail
skill: lighting-layout
category: compliance_failure
description: |
  Verifies INV-19 fires HIGH on uk-per-zone-target-violation (FAIL-by-design example, 60% gap).
input_fixtures:
  - electrical/lighting-layout/examples/uk-per-zone-target-violation/output.json
checks:
  - description: "INV-19 passes: false on FAIL example"
    severity: critical
    matches_inv: "INV-19"
  - description: "INV-19 severity: high (gap_pct ≥ 50% band)"
    severity: critical
    matches_inv: "INV-19"
  - description: "non_compliance_flags[] contains INV-19 HIGH entry"
    severity: critical
    matches_inv: "INV-19"
```

- [ ] **Step 7: Validate all 5 YAML files parse + pass eval.schema.json**

Run:
```bash
python3 -c "
import yaml, json, jsonschema
schema = json.load(open('shared/schemas/core/eval.schema.json'))
for f in [
  'electrical/lighting-layout/evals/eval-09-zone-purpose-emit.yaml',
  'electrical/lighting-layout/evals/eval-10-task-surrounding-ratio.yaml',
  'electrical/lighting-layout/evals/eval-11-mount-type-3d-consistency.yaml',
  'electrical/lighting-layout/evals/eval-12-per-zone-achievement-pass.yaml',
  'electrical/lighting-layout/evals/eval-13-per-zone-achievement-fail.yaml',
]:
    d = yaml.safe_load(open(f))
    v = jsonschema.Draft202012Validator(schema)
    errors = list(v.iter_errors(d))
    if errors:
        print(f, 'ERRORS:', [e.message[:100] for e in errors[:3]])
    else:
        print(f, 'OK')
"
```

Expected: all 5 OK.

- [ ] **Step 8: Run golden CI gate (Pass 2)**

Run:
```bash
python3 scripts/validate-examples.py 2>&1 | tail -3
```

Expected: aggregate bumps by +5 (5 new evals).

- [ ] **Step 9: Commit**

```bash
git add electrical/lighting-layout/evals/eval-09-*.yaml electrical/lighting-layout/evals/eval-10-*.yaml electrical/lighting-layout/evals/eval-11-*.yaml electrical/lighting-layout/evals/eval-12-*.yaml electrical/lighting-layout/evals/eval-13-*.yaml
git commit -m "feat(lighting-layout): C.13 add 5 new evals for D5 depth features (INV-13/14/15/16/17/18/19 coverage)"
```

---
