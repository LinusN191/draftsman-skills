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
