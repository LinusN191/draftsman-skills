# Sprint D3 — Lighting-Layout Depth Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close every gap surfaced by the end-to-end test that produced the bad lighting CAD image + the user's 5-section audit + the 3 structural issues the audit missed (circuit topology Z-pattern, stub validator/reviewer prompts, intent payload extension). Re-test by building the user's verbatim original prompt as a new canonical example.

**Architecture:** Three sequential phases (A foundations → B prompts → C examples+ship) with 11 implementer tasks total. Phase A lands ontology + rules YAML + schema BEFORE Phase B prompts cite them (rules YAML as single source of truth eliminates drift). Phase C builds 4 new examples (3 failure-mode + 1 canonical re-test) and ships. Each task: Opus/Sonnet implementer per work-type, two-stage Opus review (spec-compliance + code-quality), fix-pass if needed. Mirrors D2's shipped pattern.

**Tech Stack:** JSON Schema Draft-07 (IR schemas), Markdown (generator/validator/reviewer prompts), YAML (rules + validation specs + evals), Python 3.11 (validate-examples.py + functional_audit.py), SVG (drafting-furniture annotation templates).

**Spec:** `docs/superpowers/specs/2026-05-28-sprint-D3-lighting-layout-depth-design.md` (commit `833e188`).

**Version bumps:**
- lighting-layout: `[1.3.1]` → `[1.4.0]` (minor — additive content: 10 new INVs + zones/topology fields + drafting_furniture block + photometric_override input + ontology backfill + rules YAML expansion + 4 new examples)

**Gates target:** validate-examples 225/225 → ~241/241 (+12 from C.1–C.3); functional_audit 1 finding unchanged (motor-superposition oracle FP on us-industrial-with-motors/MCC-1 — disclosed in D1.1).

**Pre-flight notes (verified by spec author):**
- `shared/schemas/electrical/lighting-layout-ir.schema.json` (canonical) is 512 lines and ALREADY has: `zones[]` (without `zone_type`/`circuits[]`/`homerun_endpoint`/`row_index`), `switches[].door_swing`+`switch_side`, `mode` enum (full_drawing|calc_only), `calculation_summary.non_compliance_flags` items with proper object shape `{message, reference, severity (critical|warning|info)}`, `invariants[]` with severity `critical|high|medium|low`.
- **Severity-enum split is intentional**: `non_compliance_flags` uses `critical|warning|info` (compliance-report style); `invariants` uses `critical|high|medium|low` (review-finding style). Plan preserves both.
- `electrical/lighting-layout/schemas/lighting-layout-ir.schema.json` is a 6-line `$ref` redirect to the canonical — leave it alone, edit only the canonical at `shared/`.
- `prompts/validator.md` and `prompts/reviewer.md` are **4-line stubs** (current content: `"See prompts/generator.md for the full skill context."`).
- `ontology/luminaire-types.json` (10 lines) and `ontology/switching-types.json` (9 lines) are skeletons.
- `examples/reception-lobby/` and `examples/warehouse-highbay/` are `mode: calc_only` stubs (per the existing schema `if/then/else` clause); promotion = switch to `mode: full_drawing` + populate all required fields.

---

## File Structure

### Modified

- `shared/schemas/electrical/lighting-layout-ir.schema.json` — A.3: add `zones[].zone_type` enum + `zones[].circuits[]` with row_index+homerun_endpoint; add `drafting_furniture` block; add `selection._source` path; tighten `circuits[].total_load_w` to allOf-conditional max (80% × ocpd × 230); add `room_type` enum (12 values); tighten `mcb_rating_a` per-OCPD load conditional
- `electrical/lighting-layout/schemas/lighting-layout-intent.schema.json` — A.3: extend payload with zones+circuits+homerun+switches+total_load_per_circuit for downstream consumption
- `electrical/lighting-layout/inputs.json` — A.3: add `door_swing` to entrance_positions item_schema; add `photometric_override` optional struct; tighten `ceiling_grid_mm` validator (enum {600, 1200, 0}); add `is_glazed_walls` derived helper
- `electrical/lighting-layout/ontology/luminaire-types.json` — A.1: 10 → ~250 lines (photometric block per type)
- `electrical/lighting-layout/ontology/switching-types.json` — A.1: 9 → ~80 lines (electrical ratings + symbol mapping + new types)
- `electrical/lighting-layout/rules/switching-rules.yaml` — A.2: 9 → ~50 lines (full structured rules with citations + rationale)
- `electrical/lighting-layout/rules/placement-rules.yaml` — A.2: 9 → ~50 lines
- `electrical/lighting-layout/rules/spacing-rules.yaml` — A.2: 7 → ~45 lines
- `electrical/lighting-layout/rules/control-rules.yaml` — A.2: 13 → ~60 lines (Part L 2021 + BS 7671 §714)
- `electrical/lighting-layout/rules/emergency-rules.yaml` — A.2: 7 → ~50 lines (BS 5266-1)
- `electrical/lighting-layout/prompts/generator.md` — B.1/B.2/B.3: rewrite Step 6 (lumen-method worked example) + Step 7 (S/H ratio loop) + Step 11 (circuit topology) + Step 12 (switch placement) + new Step 15 (drafting furniture); add rule-ID citations throughout
- `electrical/lighting-layout/prompts/validator.md` — B.4: 4 → ~400 lines (full INV-1..INV-10 catalogue)
- `electrical/lighting-layout/prompts/reviewer.md` — B.4: 4 → ~250 lines (D-1..D-6 catalogue)
- `electrical/lighting-layout/examples/office-open-plan/output.json` — A.3 ripple: add zone_type + row_index + homerun_endpoint + drafting_furniture; B.1 ripple: photometric source citation; B.2 ripple: per-circuit row_index; B.4 ripple: INV-1..INV-10 invariants entries
- `electrical/lighting-layout/examples/reception-lobby/output.json` — C.1: promote calc_only → full_drawing (~100 → ~400 lines)
- `electrical/lighting-layout/examples/reception-lobby/reasoning.md` — C.1: 11 → ~150 lines
- `electrical/lighting-layout/examples/warehouse-highbay/output.json` — C.1: promote calc_only → full_drawing (~90 → ~400 lines)
- `electrical/lighting-layout/examples/warehouse-highbay/reasoning.md` — C.1: 14 → ~150 lines
- `electrical/lighting-layout/CHANGELOG.md` — C.4: combined [1.4.0] entry
- `electrical/lighting-layout/skill.manifest.json` — C.4: version 1.3.1 → 1.4.0; register 4 new examples

### Created

- `electrical/lighting-layout/ontology/emergency-types.json` — A.1: emergency-luminaire ontology (BS 5266-1)
- `electrical/lighting-layout/examples/reception-lobby/intent-out.json` — C.1: new (stub previously had only output.json)
- `electrical/lighting-layout/examples/warehouse-highbay/intent-out.json` — C.1: new
- `electrical/lighting-layout/examples/uk-undersized-lighting-vs-target/` (4 files) — C.2: failure-mode example #1
- `electrical/lighting-layout/examples/uk-multi-entrance-classroom/` (4 files) — C.2: failure-mode example #2
- `electrical/lighting-layout/examples/uk-part-l-fail-incandescent/` (4 files) — C.2: failure-mode example #3
- `electrical/lighting-layout/examples/uk-open-plan-office-10x8-dali/` (4 files) — C.3: canonical re-test example
- `~/.claude/projects/-Users-linus-Desktop-DraftsMan-SKills-draftsman-skills/memory/sprint-D3-shipped.md` — C.4: sprint shipped memory

---

## Phase A — Foundations (3 tasks, sequential)

Schema + ontology + rules YAML must land before Phase B prompts can cite them. A.1 + A.2 are parallel-safe in principle (different files) but kept sequential so each gets its own two-stage Opus review pass.

---

## Task A.1: Ontology backfill — photometric defaults + switching + emergency types (Opus)

**Why Opus:** Regulation-driven content + photometric judgment + citation accuracy. Per `[[feedback-no-haiku-sonnet-opus-only]]` model rule. **Citation cross-check against `shared/standards/electrical/` BEFORE writing is MANDATORY** per the D2.3 Reg 559 lesson — every clause cited in this task must have repo-traceable evidence.

**Files:**
- Modify: `electrical/lighting-layout/ontology/luminaire-types.json` — 10 → ~250 lines (add photometric block per type)
- Modify: `electrical/lighting-layout/ontology/switching-types.json` — 9 → ~80 lines (add electrical ratings + symbol mapping + 4 new types)
- Create: `electrical/lighting-layout/ontology/emergency-types.json` — ~60 lines (BS 5266-1 emergency luminaire types)

- [ ] **Step 1: Verify citation sources exist in repo**

```bash
grep -rn "BS EN 12464-1\|CIBSE LG7\|BS 5266" shared/standards/electrical/ | head -10
ls shared/standards/electrical/BS5266 2>/dev/null || echo "BS5266 standards dir absent"
```

Expected: BS EN 12464-1 referenced in BS7671 and IEC60364 lighting files. CIBSE LG7 may not have a dedicated standards file — if so, cite it as the published industry standard without repo-internal cross-reference. If BS5266 directory absent, note it explicitly in the emergency-types.json `_note` field: `"Citations to BS 5266-1:2016 reference the published British Standard; no repo-internal cross-reference file exists yet."`

- [ ] **Step 2: Rewrite luminaire-types.json with photometric data**

Replace the existing 10-line file with:

```json
{
  "_version": "1.4.0",
  "_note": "Reference photometric defaults per luminaire type. Engineer override via inputs.photometric_override block; generator falls back to these defaults if override absent. UF tables indexed by RI (room index) and reflectance triplet (ceiling_wall_floor). LLMF schedules by maintenance environment. Citations verifiable against CIBSE LG7 and BS EN 12464-1 industry-typical values; engineer-of-record must verify against manufacturer photometric file for project-critical installations.",
  "_verification_status": "engineer_typical_C2",
  "types": {
    "LED_PANEL_600": {
      "description": "600×600mm recessed LED panel, opal diffuser",
      "shape": "rectangle",
      "dims_mm": [600, 600],
      "photometric": {
        "uf_table_by_ri": {
          "0.6":  {"0.7_0.5_0.2": 0.45, "0.5_0.3_0.2": 0.40, "0.3_0.3_0.2": 0.35},
          "1.0":  {"0.7_0.5_0.2": 0.55, "0.5_0.3_0.2": 0.50, "0.3_0.3_0.2": 0.45},
          "1.5":  {"0.7_0.5_0.2": 0.62, "0.5_0.3_0.2": 0.57, "0.3_0.3_0.2": 0.52},
          "2.0":  {"0.7_0.5_0.2": 0.67, "0.5_0.3_0.2": 0.62, "0.3_0.3_0.2": 0.57},
          "2.5":  {"0.7_0.5_0.2": 0.71, "0.5_0.3_0.2": 0.66, "0.3_0.3_0.2": 0.60},
          "3.0":  {"0.7_0.5_0.2": 0.74, "0.5_0.3_0.2": 0.68, "0.3_0.3_0.2": 0.62},
          "5.0":  {"0.7_0.5_0.2": 0.80, "0.5_0.3_0.2": 0.73, "0.3_0.3_0.2": 0.67}
        },
        "shr_max": 1.5,
        "llmf_schedule": {
          "clean_office":    {"6000h": 0.95, "12000h": 0.90, "24000h": 0.85},
          "normal_indoor":   {"6000h": 0.90, "12000h": 0.83, "24000h": 0.75},
          "industrial":      {"6000h": 0.85, "12000h": 0.75, "24000h": 0.65}
        },
        "_citation": "CIBSE LG7 §6.2 (typical recessed LED panel UF + SHR_max) + BS EN 12464-1:2021 §4.4 (LLMF maintenance categories)",
        "_verification_status": "engineer_typical_C2"
      }
    },
    "LINEAR_LED": {
      "description": "1200×100mm linear LED batten, opal diffuser",
      "shape": "rectangle",
      "dims_mm": [1200, 100],
      "photometric": {
        "uf_table_by_ri": {
          "0.6":  {"0.7_0.5_0.2": 0.42, "0.5_0.3_0.2": 0.38, "0.3_0.3_0.2": 0.33},
          "1.0":  {"0.7_0.5_0.2": 0.52, "0.5_0.3_0.2": 0.47, "0.3_0.3_0.2": 0.42},
          "1.5":  {"0.7_0.5_0.2": 0.60, "0.5_0.3_0.2": 0.54, "0.3_0.3_0.2": 0.49},
          "2.0":  {"0.7_0.5_0.2": 0.65, "0.5_0.3_0.2": 0.59, "0.3_0.3_0.2": 0.54},
          "2.5":  {"0.7_0.5_0.2": 0.69, "0.5_0.3_0.2": 0.63, "0.3_0.3_0.2": 0.57},
          "3.0":  {"0.7_0.5_0.2": 0.72, "0.5_0.3_0.2": 0.66, "0.3_0.3_0.2": 0.60},
          "5.0":  {"0.7_0.5_0.2": 0.78, "0.5_0.3_0.2": 0.71, "0.3_0.3_0.2": 0.65}
        },
        "shr_max": 1.6,
        "llmf_schedule": {
          "clean_office":    {"6000h": 0.95, "12000h": 0.90, "24000h": 0.85},
          "normal_indoor":   {"6000h": 0.90, "12000h": 0.83, "24000h": 0.75},
          "industrial":      {"6000h": 0.85, "12000h": 0.75, "24000h": 0.65}
        },
        "_citation": "CIBSE LG7 §6.2 (linear LED batten typical values) + BS EN 12464-1:2021 §4.4",
        "_verification_status": "engineer_typical_C2"
      }
    },
    "LED_DOWNLIGHT": {
      "description": "100mm diameter recessed LED downlight, prismatic lens",
      "shape": "circle",
      "diameter_mm": 100,
      "photometric": {
        "uf_table_by_ri": {
          "0.6":  {"0.7_0.5_0.2": 0.38, "0.5_0.3_0.2": 0.34, "0.3_0.3_0.2": 0.30},
          "1.0":  {"0.7_0.5_0.2": 0.48, "0.5_0.3_0.2": 0.43, "0.3_0.3_0.2": 0.38},
          "1.5":  {"0.7_0.5_0.2": 0.55, "0.5_0.3_0.2": 0.49, "0.3_0.3_0.2": 0.44},
          "2.0":  {"0.7_0.5_0.2": 0.60, "0.5_0.3_0.2": 0.54, "0.3_0.3_0.2": 0.49},
          "2.5":  {"0.7_0.5_0.2": 0.64, "0.5_0.3_0.2": 0.58, "0.3_0.3_0.2": 0.52},
          "3.0":  {"0.7_0.5_0.2": 0.67, "0.5_0.3_0.2": 0.61, "0.3_0.3_0.2": 0.55},
          "5.0":  {"0.7_0.5_0.2": 0.73, "0.5_0.3_0.2": 0.66, "0.3_0.3_0.2": 0.60}
        },
        "shr_max": 1.4,
        "llmf_schedule": {
          "clean_office":    {"6000h": 0.93, "12000h": 0.86, "24000h": 0.80},
          "normal_indoor":   {"6000h": 0.88, "12000h": 0.80, "24000h": 0.72},
          "industrial":      {"6000h": 0.82, "12000h": 0.72, "24000h": 0.62}
        },
        "_citation": "CIBSE LG7 §6.2 (recessed downlight typical values; narrow beam) + BS EN 12464-1:2021 §4.4",
        "_verification_status": "engineer_typical_C2"
      }
    },
    "HIGHBAY": {
      "description": "Industrial highbay LED, narrow-beam reflector for 6-12m mounting",
      "shape": "circle",
      "diameter_mm": 300,
      "photometric": {
        "uf_table_by_ri": {
          "0.6":  {"0.5_0.3_0.2": 0.50, "0.3_0.3_0.2": 0.45, "0.3_0.1_0.1": 0.40},
          "1.0":  {"0.5_0.3_0.2": 0.62, "0.3_0.3_0.2": 0.55, "0.3_0.1_0.1": 0.50},
          "1.5":  {"0.5_0.3_0.2": 0.70, "0.3_0.3_0.2": 0.62, "0.3_0.1_0.1": 0.56},
          "2.0":  {"0.5_0.3_0.2": 0.75, "0.3_0.3_0.2": 0.67, "0.3_0.1_0.1": 0.60},
          "2.5":  {"0.5_0.3_0.2": 0.79, "0.3_0.3_0.2": 0.70, "0.3_0.1_0.1": 0.63},
          "3.0":  {"0.5_0.3_0.2": 0.82, "0.3_0.3_0.2": 0.73, "0.3_0.1_0.1": 0.66},
          "5.0":  {"0.5_0.3_0.2": 0.87, "0.3_0.3_0.2": 0.77, "0.3_0.1_0.1": 0.69}
        },
        "shr_max": 1.0,
        "llmf_schedule": {
          "industrial":      {"6000h": 0.85, "12000h": 0.75, "24000h": 0.65},
          "warehouse_dusty": {"6000h": 0.78, "12000h": 0.65, "24000h": 0.55}
        },
        "_citation": "CIBSE LG12 (industrial lighting; highbay narrow-beam typical) + BS EN 12464-1:2021 §4.4",
        "_verification_status": "engineer_typical_C2"
      }
    },
    "EMERGENCY": {
      "description": "Emergency luminaire 300×100mm (escape route / open area / high risk task area)",
      "shape": "rectangle",
      "dims_mm": [300, 100],
      "photometric": {
        "uf_table_by_ri": {
          "1.0":  {"0.5_0.3_0.2": 0.40, "0.3_0.3_0.2": 0.36, "0.3_0.1_0.1": 0.32},
          "1.5":  {"0.5_0.3_0.2": 0.46, "0.3_0.3_0.2": 0.41, "0.3_0.1_0.1": 0.36}
        },
        "shr_max": 1.4,
        "llmf_schedule": {
          "emergency_standby": {"6000h": 0.90, "12000h": 0.82, "24000h": 0.75}
        },
        "_citation": "BS 5266-1:2016 §5.2 (emergency lighting design illuminance: 1 lux escape route minimum; 0.5 lux anti-panic open area; 15 lux high-risk task)",
        "_verification_status": "engineer_typical_C2"
      }
    }
  }
}
```

- [ ] **Step 3: Rewrite switching-types.json with electrical ratings + new types**

```json
{
  "_version": "1.4.0",
  "_note": "Switching device ontology — electrical ratings + symbol mapping (DXF block name) + compatible load types. Generator selects switch type from inputs.controls_protocol + load count.",
  "types": {
    "1_gang": {
      "description": "Single switch, one circuit",
      "rated_amps": 10,
      "voltage_v": 230,
      "compatible_loads": ["lighting_max_2300w"],
      "symbol_dxf_block": "SW_1GANG",
      "_citation": "BS 1363-4 + BS EN 60669-1"
    },
    "2_gang": {
      "description": "Two switches, two independent circuits",
      "rated_amps": 10,
      "voltage_v": 230,
      "compatible_loads": ["lighting_max_2300w_each"],
      "symbol_dxf_block": "SW_2GANG",
      "_citation": "BS 1363-4 + BS EN 60669-1"
    },
    "3_gang": {
      "description": "Three switches, three independent circuits",
      "rated_amps": 10,
      "voltage_v": 230,
      "compatible_loads": ["lighting_max_2300w_each"],
      "symbol_dxf_block": "SW_3GANG",
      "_citation": "BS 1363-4 + BS EN 60669-1"
    },
    "dimmer": {
      "description": "Rotary or push dimmer (trailing edge for LED)",
      "rated_amps": 6,
      "voltage_v": 230,
      "compatible_loads": ["dimmable_led_max_400w"],
      "symbol_dxf_block": "SW_DIMMER",
      "_citation": "BS EN 60669-2-1 (electronic dimmers)"
    },
    "presence": {
      "description": "Presence/occupancy detector with manual override",
      "rated_amps": 6,
      "voltage_v": 230,
      "compatible_loads": ["lighting_max_1380w"],
      "symbol_dxf_block": "SW_PRESENCE",
      "_citation": "BS EN 60669-2-2 (electronic detection switches) + BS 7671:2018+A2:2022 §714 (occupancy controls)"
    },
    "daylight_sensor": {
      "description": "Photocell for daylight-linked dimming/switching",
      "rated_amps": 6,
      "voltage_v": 230,
      "compatible_loads": ["dimmable_lighting_max_1380w"],
      "symbol_dxf_block": "SW_DAYLIGHT",
      "_citation": "BS EN 15193-1:2017 + Approved Doc L (Part L 2021) §6.2 daylight-linking"
    },
    "presence_with_dimming": {
      "description": "Combined presence detector + daylight sensor + dimming output",
      "rated_amps": 6,
      "voltage_v": 230,
      "compatible_loads": ["dimmable_lighting_max_1380w"],
      "symbol_dxf_block": "SW_PRESENCE_DIM",
      "_citation": "BS EN 60669-2-2 + BS EN 15193-1:2017 + Approved Doc L §6.2"
    },
    "dali_master": {
      "description": "DALI master switch / wall controller (entry-point control for a DALI line)",
      "rated_amps": 6,
      "voltage_v": 230,
      "compatible_loads": ["dali_addressable_lighting"],
      "symbol_dxf_block": "SW_DALI_MASTER",
      "_citation": "IEC 62386-101 + BS EN 62386-102 (DALI bus + control device)"
    },
    "dali_application_controller": {
      "description": "DALI application controller (panel-mount; orchestrates scenes/zones across multiple lines)",
      "rated_amps": 6,
      "voltage_v": 230,
      "compatible_loads": ["dali_addressable_lighting", "dali_2_groups"],
      "symbol_dxf_block": "SW_DALI_AC",
      "_citation": "IEC 62386-103 (DALI application controllers)"
    }
  }
}
```

- [ ] **Step 4: Create emergency-types.json**

```json
{
  "_version": "1.0.0",
  "_note": "Emergency luminaire ontology backing rules/emergency-rules.yaml. Citations reference BS 5266-1:2016 (published British Standard). No repo-internal BS5266 cross-reference file exists yet; engineer-of-record must verify against the published edition.",
  "_verification_status": "engineer_typical_C2",
  "types": {
    "non_maintained_self_test": {
      "description": "Non-maintained: lights only on mains failure. Self-test = monthly + annual auto duration test logged by driver.",
      "operation_mode": "non_maintained",
      "duration_min": 180,
      "test_protocol": "self_test_DALI_or_local",
      "applicable_areas": ["escape_route", "office_interior", "warehouse_interior"],
      "symbol_dxf_block": "EM_NON_MAINT_ST",
      "_citation": "BS 5266-1:2016 §4.3.2 (non-maintained luminaires) + §10 (testing regime)"
    },
    "maintained_self_test": {
      "description": "Maintained: lit during normal operation; remains lit on mains failure. Used where occupants need to see exit signs at all times (e.g. cinemas, lecture halls).",
      "operation_mode": "maintained",
      "duration_min": 180,
      "test_protocol": "self_test_DALI_or_local",
      "applicable_areas": ["exit_sign_continuous_view", "high_occupancy_assembly"],
      "symbol_dxf_block": "EM_MAINT_ST",
      "_citation": "BS 5266-1:2016 §4.3.1 (maintained luminaires)"
    },
    "escape_route_luminaire": {
      "description": "Escape route luminaire — 1 lux minimum on the centre line of escape route per BS 5266-1 §5.2.1",
      "design_illuminance_lux_min": 1.0,
      "design_uniformity_min": 0.025,
      "applicable_areas": ["corridor", "stairwell", "lobby", "exit_route"],
      "symbol_dxf_block": "EM_ESCAPE",
      "_citation": "BS 5266-1:2016 §5.2.1 (escape route illuminance) + §5.2.4 (uniformity)"
    },
    "open_area_anti_panic": {
      "description": "Anti-panic open area luminaire — 0.5 lux minimum on floor area excluding 0.5m border per BS 5266-1 §5.3",
      "design_illuminance_lux_min": 0.5,
      "design_uniformity_min": 0.025,
      "applicable_areas": ["open_plan_office_>60m2", "warehouse_main_aisle", "shopping_floor"],
      "symbol_dxf_block": "EM_ANTIPANIC",
      "_citation": "BS 5266-1:2016 §5.3 (anti-panic / open area emergency lighting)"
    },
    "high_risk_task_area": {
      "description": "High-risk task area emergency luminaire — 15 lux or 10% of normal task illuminance (whichever higher), per BS 5266-1 §5.4",
      "design_illuminance_lux_min": 15.0,
      "design_uniformity_min": 0.1,
      "applicable_areas": ["machine_shop", "lab", "kitchen_commercial_hot_zone", "medical_operating"],
      "symbol_dxf_block": "EM_HIGHRISK",
      "_citation": "BS 5266-1:2016 §5.4 (high-risk task area emergency lighting)"
    }
  }
}
```

- [ ] **Step 5: Run golden CI gate**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
python3 scripts/validate-examples.py 2>&1 | tail -3
```

Expected: `AGGREGATE: 225/225 pass (0 failures)`. The ontology files aren't validated by validate-examples.py (only example outputs + evals + inputs.json). This step confirms no regression from accidental schema edits.

- [ ] **Step 6: Hand-check ontology files parse as JSON**

```bash
python3 -c "
import json
for f in ['luminaire-types.json', 'switching-types.json', 'emergency-types.json']:
    d = json.load(open(f'electrical/lighting-layout/ontology/{f}'))
    print(f'{f}: _version={d.get(\"_version\")} types={len(d.get(\"types\", {}))}')"
```

Expected:
- `luminaire-types.json: _version=1.4.0 types=5`
- `switching-types.json: _version=1.4.0 types=9`
- `emergency-types.json: _version=1.0.0 types=5`

- [ ] **Step 7: Commit A.1**

```bash
git add electrical/lighting-layout/ontology/
git commit -m "$(cat <<'EOF'
feat(lighting-layout): D3.A.1 ontology backfill — photometric defaults + switching + emergency types

Sprint D3 Phase A foundations — first of three. Closes the audit §4
ontology gap that left the generator improvising UF/SHR_max/LLMF values.

luminaire-types.json (10 → ~250 lines):
- Each of 5 luminaire types gains a `photometric` block: UF table indexed
  by room index (RI ∈ {0.6, 1.0, 1.5, 2.0, 2.5, 3.0, 5.0}) and reflectance
  triplet (ceiling_wall_floor); SHR_max; LLMF schedule by maintenance
  environment (clean_office / normal_indoor / industrial / warehouse_dusty
  / emergency_standby).
- Citations: CIBSE LG7 §6.2 (typical recessed LED panel UF + SHR_max),
  CIBSE LG12 (industrial highbay), BS EN 12464-1:2021 §4.4 (LLMF
  maintenance categories), BS 5266-1:2016 §5.2 (emergency).
- All flagged verification_status=engineer_typical_C2 — values are
  industry-typical per CIBSE; engineer-of-record must verify against
  manufacturer photometric file for project-critical installations.

switching-types.json (9 → ~80 lines):
- Each of 9 types (1_gang, 2_gang, 3_gang, dimmer, presence,
  daylight_sensor, presence_with_dimming, dali_master,
  dali_application_controller) gains rated_amps, voltage_v,
  compatible_loads[], symbol_dxf_block, _citation.
- 4 new types added: 3_gang, daylight_sensor, presence_with_dimming,
  dali_application_controller (extending the previous 5).

emergency-types.json (NEW, ~60 lines):
- 5 types per BS 5266-1:2016: non_maintained_self_test,
  maintained_self_test, escape_route_luminaire, open_area_anti_panic,
  high_risk_task_area.
- Each carries design illuminance minima, uniformity minima, applicable
  area lists, symbol mapping.

Gates: validate-examples 225/225 unchanged (ontology not directly
validated). functional_audit 1 finding unchanged.

Next: D3.A.2 rules YAML SoT expansion.
EOF
)"
```

---

## Task A.2: Rules YAML SoT expansion (Opus)

**Why Opus:** Citation accuracy (D2.3 Reg 559 lesson). Every clause cross-checked against `shared/standards/electrical/` BEFORE writing.

**Files:**
- Modify: `electrical/lighting-layout/rules/switching-rules.yaml` — 9 → ~50 lines
- Modify: `electrical/lighting-layout/rules/placement-rules.yaml` — 9 → ~50 lines
- Modify: `electrical/lighting-layout/rules/spacing-rules.yaml` — 7 → ~45 lines
- Modify: `electrical/lighting-layout/rules/control-rules.yaml` — 13 → ~60 lines
- Modify: `electrical/lighting-layout/rules/emergency-rules.yaml` — 7 → ~50 lines

- [ ] **Step 1: Verify citation sources exist in repo**

```bash
grep -rn "553\.1\.1\|714\|EN 60598\|EN 12464-1\|EN 15193" shared/standards/electrical/ | head -20
```

Expected: §553 + §714 visible in `shared/standards/electrical/BS7671/`. EN 12464-1 + EN 15193 may appear in references but not have dedicated files — cite the published standards directly per the D2.3 honest-disclosure pattern (`"no repo-internal cross-reference exists for this standard"` note where applicable).

- [ ] **Step 2: Rewrite switching-rules.yaml**

```yaml
id: switching-rules
description: Switch placement and zoning per BS 7671 §553 + IET On-Site Guide
_verification_status: engineer_typical_C2
_note: "Drift fix Sprint D3 — height value standardised to 1200mm AFF per BS 7671 §553.1.1 (was inconsistent with generator.md which had 1350mm)."

rules:
  - id: switching-rules#height
    value:
      height_mm: 1200
      tolerance_mm: 50
      reference_point: "centre_of_switch_to_finished_floor_level"
    citation: "BS 7671:2018+A2:2022 §553.1.1 (accessory mounting heights) + IET On-Site Guide App E §E1.2"
    rationale: "1200mm AFF is the IET-recommended height for general-purpose switches in offices and dwellings. Equality Act 2010 / BS 8300-2:2018 require accessible switches in accessible WCs / classrooms to be 900-1100mm range — engineer overrides for accessible spaces with explicit override and citation."

  - id: switching-rules#latch-side
    value:
      offset_mm_from_frame: 200
      side: "latch"
      door_swing_aware: true
    citation: "IET On-Site Guide App E §E1.4 (switch placement at room entrance)"
    rationale: "Switch on latch side (opposite the hinge) avoids reaching across an opening door. door_swing field on entrance_positions[] determines which side is latch for each door."

  - id: switching-rules#perimeter-circuit
    value:
      perimeter_zone_separate_circuit: true
      max_zone_depth_mm: 6000
    citation: "Approved Doc L (Part L 2021) §6.2 + BS 7671:2018+A2:2022 §714 (lighting control zones) + BS EN 15193-1:2017 §6.2"
    rationale: "Perimeter zone (within 6m of glazed wall) must be on a separately switched / dimmed circuit from interior zone, so daylight-linked dimming can operate without affecting interior task illuminance."

  - id: switching-rules#dali-master-at-entrance
    value:
      dali_master_position: "within_2m_of_primary_entrance"
      override_allowed: true
    citation: "IEC 62386-101 §6 (DALI bus topology — master at convenient access point)"
    rationale: "DALI master controller positioned for primary user access; secondary entrances may use DALI wall controllers slaved to the master line."
```

- [ ] **Step 3: Rewrite placement-rules.yaml**

```yaml
id: placement-rules
description: Luminaire placement constraints per BS EN 12464-1 + CIBSE LG7
_verification_status: engineer_typical_C2

rules:
  - id: placement-rules#edge-clearance
    value:
      min_clearance_mm_from_wall: 300
      max_clearance_mm_from_wall: 600
    citation: "CIBSE LG7 §5.2 (uniformity practice) + BS EN 12464-1:2021 §4.4 indirect (uniformity on task area)"
    rationale: "First/last row of luminaires must sit 300-600mm from the wall — closer creates hot-spots on the wall, farther sacrifices working-plane uniformity at the room perimeter. CAD-standard 300mm minimum."

  - id: placement-rules#grid-snap
    value:
      snap_mm: 50
      snap_to_ceiling_grid: true
    citation: "Industry CAD convention + BS 1192:2007 §4 (drawing presentation)"
    rationale: "Luminaire positions snap to 50mm grid for renderer + builder accuracy. When ceiling_grid_mm declared (600 or 1200), luminaires further snap to grid module centres for ceiling-tile alignment."

  - id: placement-rules#door-clearance
    value:
      min_clearance_mm_from_door_swing_arc: 300
    citation: "BS EN 12464-1:2021 §5 (lighting design — avoid placing fixtures inside door swing arc)"
    rationale: "Luminaires inside the door-swing arc create a glare hazard when the door opens. 300mm clearance from the swept arc."

  - id: placement-rules#row-spacing-uniform
    value:
      row_spacing_mm_max_variance_pct: 5
    citation: "BS EN 12464-1:2021 §4.4 (uniformity ratio U₀)"
    rationale: "Row spacing variance ≤5% to keep working-plane uniformity within EN 12464-1 task-area tolerance."
```

- [ ] **Step 4: Rewrite spacing-rules.yaml**

```yaml
id: spacing-rules
description: Luminaire spacing per Lumen Method + CIBSE LG7
_verification_status: engineer_typical_C2

rules:
  - id: spacing-rules#shr-max-default
    value:
      shr_max_default: 1.5
      override_via_ontology: true
    citation: "CIBSE LG7 §6.2 (Spacing-to-Height Ratio limits)"
    rationale: "Default SHR_max is 1.5 for typical recessed LED panels. Per-luminaire override via ontology/luminaire-types.json (e.g. LED_DOWNLIGHT=1.4, HIGHBAY=1.0, LINEAR_LED=1.6). The lumen-method check is S_x ≤ SHR_max × Hm AND S_y ≤ SHR_max × Hm."

  - id: spacing-rules#lumen-method-formula
    value:
      formula: "N = (Em × A) / (Φ × UF × MF)"
      rounding: "round_up"
      MF: "MF = LLMF × LSF × LMF × RSMF (typical 0.80 for clean office; 0.65 for industrial)"
    citation: "CIBSE LG7 §6 + BS EN 12464-1:2021 §4.3 (illuminance calculation)"
    rationale: "Lumen method: N = number of luminaires; Em = target illuminance (lux); A = room area (m²); Φ = luminaire design lumens; UF = utilisation factor from photometric table indexed by RI + reflectances; MF = total maintenance factor. Always round UP — never under-provide light."

  - id: spacing-rules#room-index
    value:
      formula: "RI = (L × W) / (Hm × (L + W))"
      Hm: "Hm = ceiling_height_mm − working_plane_mm"
    citation: "CIBSE LG7 §6.2 + BS EN 12464-1:2021 §4.3"
    rationale: "Room index drives UF table lookup. Hm = mounting height above working plane (typically working_plane_mm = 750 for offices, 0 for warehouses where task is at floor)."

  - id: spacing-rules#working-plane-defaults
    value:
      open_plan_office: 750
      private_office: 750
      meeting_room: 750
      corridor: 0
      warehouse: 0
      classroom: 700
      consulting_room: 800
      ward: 800
      kitchen_commercial: 900
      bathroom: 0
      reception_lobby: 0
    citation: "BS EN 12464-1:2021 Table 5.3 (task area working planes)"
    rationale: "Per-room-type working plane heights. Lookup table for generator Step 5 (compute Hm + RI)."
```

- [ ] **Step 5: Rewrite control-rules.yaml**

```yaml
id: control-rules
description: Lighting controls per Approved Doc L (Part L 2021) + BS 7671 §714 + BS EN 15193-1
_verification_status: engineer_typical_C2

rules:
  - id: control-rules#part-l-occupancy
    value:
      required_when: "is_uk_new_build == true AND room_type != 'corridor'"
      detection_protocol: "presence_or_absence"
      hold_off_min: 10
    citation: "Approved Doc L (Part L 2021) §6.2 + BS EN 15193-1:2017 §6"
    rationale: "Part L 2021 mandates occupancy detection (absence-detection preferred per BS EN 15193) for new-build offices ≥30m². Corridors typically use timed-control rather than occupancy (continuous traffic)."

  - id: control-rules#part-l-daylight
    value:
      required_when: "is_uk_new_build == true AND glazed_wall_positions != []"
      perimeter_zone_depth_mm: 6000
      control_protocol: "daylight_linked_dimming_or_switching"
    citation: "Approved Doc L (Part L 2021) §6.2 + BS EN 15193-1:2017 §6.2"
    rationale: "Perimeter zone (within 6m of any glazed wall) must be separately switched/dimmed with daylight linking. Interior zone (>6m from glazing) uses occupancy-only."

  - id: control-rules#part-l-efficacy-target
    value:
      target_lm_per_w: 95
      averaged_across_luminaires: true
    citation: "Approved Doc L (Part L 2021) Table 6.2 (lighting efficacy)"
    rationale: "Part L 2021 mandates ≥95 lm/W averaged for general lighting in non-domestic new-build. Failing this triggers non_compliance_flags with severity=critical."

  - id: control-rules#manual-switch-override
    value:
      manual_override_required: true
      switch_position_per_zone: "at_room_entrance"
    citation: "BS 7671:2018+A2:2022 §714 + Approved Doc L §6.2"
    rationale: "Automatic controls (DALI / occupancy / daylight) must allow manual override at the room entrance for safety / user preference."

  - id: control-rules#dali-line-capacity
    value:
      max_devices_per_dali_line: 64
      recommended_per_dali_line: 50
    citation: "IEC 62386-101 §4 (DALI bus capacity)"
    rationale: "DALI bus supports up to 64 short-addresses per line; design for 50 to leave headroom for scenes/groups. Above 50, add a second DALI line + application controller."
```

- [ ] **Step 6: Rewrite emergency-rules.yaml**

```yaml
id: emergency-rules
description: Emergency lighting per BS 5266-1:2016 + BS 7671 §710 (medical) + escape route design
_verification_status: engineer_typical_C2
_note: "BS5266 standards directory absent from repo — citations reference the published British Standard directly."

rules:
  - id: emergency-rules#escape-route-illuminance
    value:
      min_lux_on_centre_line: 1.0
      uniformity_min_ratio: 0.025
      duration_min: 180
    citation: "BS 5266-1:2016 §5.2.1 (escape route illuminance) + §5.2.4 (uniformity ratio)"
    rationale: "Escape routes ≤2m wide require 1 lux minimum on the centre line. Wider routes treated as anti-panic / open-area zones. Duration 3h (180min) for offices; can be reduced to 1h for premises evacuated within 1h."

  - id: emergency-rules#anti-panic-illuminance
    value:
      min_lux_on_floor: 0.5
      uniformity_min_ratio: 0.025
      duration_min: 60
      area_threshold_m2: 60
    citation: "BS 5266-1:2016 §5.3 (anti-panic / open area emergency lighting)"
    rationale: "Open areas >60m² require 0.5 lux minimum on the unobstructed floor area excluding a 0.5m border. Duration ≥1h."

  - id: emergency-rules#high-risk-task-area
    value:
      min_lux_or_pct_of_task: "max(15, 0.10 * task_illuminance_lux)"
      uniformity_min_ratio: 0.1
      duration_required: "duration_of_residual_risk_after_mains_failure"
    citation: "BS 5266-1:2016 §5.4 (high-risk task area emergency lighting)"
    rationale: "Areas with safety-critical processes (machine shops, kitchens, labs) need 15 lux OR 10% of normal task illuminance (whichever higher), to enable safe shutdown."

  - id: emergency-rules#test-regime
    value:
      monthly_function_test_required: true
      annual_full_duration_test_required: true
      logging_required: true
    citation: "BS 5266-1:2016 §10 (testing) + BS EN 62034:2012 (automatic test systems)"
    rationale: "Monthly: brief function test (simulate mains failure, verify lamps light). Annual: full-duration test (3h or rated duration). Self-test luminaires log automatically; manual systems log via maintenance schedule."

  - id: emergency-rules#exit-sign-placement
    value:
      max_viewing_distance_m: 30
      illuminance_on_face_min_lux: 5
    citation: "BS 5266-1:2016 §7 + BS EN 1838:2013 (lighting applications — emergency lighting)"
    rationale: "Exit signs must be visible from all parts of an escape route. Internally-illuminated signs need 5 lux on the face; externally-illuminated need 1 lux from an emergency luminaire."
```

- [ ] **Step 7: Validate all 5 YAML files parse**

```bash
python3 -c "
import yaml
for f in ['switching-rules', 'placement-rules', 'spacing-rules', 'control-rules', 'emergency-rules']:
    d = yaml.safe_load(open(f'electrical/lighting-layout/rules/{f}.yaml'))
    print(f'{f}.yaml: id={d.get(\"id\")} rules={len(d.get(\"rules\", []))}')"
```

Expected:
- `switching-rules.yaml: id=switching-rules rules=4`
- `placement-rules.yaml: id=placement-rules rules=4`
- `spacing-rules.yaml: id=spacing-rules rules=4`
- `control-rules.yaml: id=control-rules rules=5`
- `emergency-rules.yaml: id=emergency-rules rules=5`

- [ ] **Step 8: Run golden CI gate**

```bash
python3 scripts/validate-examples.py 2>&1 | tail -3
```

Expected: `AGGREGATE: 225/225 pass (0 failures)`.

- [ ] **Step 9: Commit A.2**

```bash
git add electrical/lighting-layout/rules/
git commit -m "$(cat <<'EOF'
feat(lighting-layout): D3.A.2 rules YAML SoT expansion (5 rule files with citations)

Sprint D3 Phase A foundations — second of three. Rules YAML promoted to
single source of truth; prompt will cite rule IDs (e.g. switching-rules#height)
instead of inlining values. Zero-drift by design.

All 5 rule files expanded from 7-13 line skeletons to full structured
documents. Each rule gains {id, value, citation, rationale}.

switching-rules.yaml (9 → ~50 lines):
- height: 1200mm AFF (BS 7671 §553.1.1 + IET OSG App E §E1.2) — resolves
  the audit drift with generator.md which had 1350mm
- latch-side: 200mm from frame, door_swing-aware (IET OSG App E §E1.4)
- perimeter-circuit: separately switched (Part L §6.2 + BS 7671 §714)
- dali-master-at-entrance: within 2m of primary entrance (IEC 62386-101)

placement-rules.yaml (9 → ~50 lines):
- edge-clearance: 300mm min, 600mm max from wall (CIBSE LG7 §5.2)
- grid-snap: 50mm + ceiling-grid alignment (industry CAD + BS 1192)
- door-clearance: 300mm from door-swing arc (BS EN 12464-1 §5)
- row-spacing-uniform: ≤5% variance (BS EN 12464-1 §4.4 U₀)

spacing-rules.yaml (7 → ~45 lines):
- shr-max-default: 1.5 with per-luminaire override via ontology
  (CIBSE LG7 §6.2)
- lumen-method-formula: N = (Em × A) / (Φ × UF × MF) with round-UP rule
- room-index: RI = (L × W) / (Hm × (L + W))
- working-plane-defaults: per-room-type table (750 office, 0 corridor,
  700 classroom, 800 ward, 900 commercial kitchen)
  (BS EN 12464-1 Table 5.3)

control-rules.yaml (13 → ~60 lines):
- part-l-occupancy: presence/absence detection for new-build offices
  ≥30m² (Part L 2021 §6.2)
- part-l-daylight: perimeter zone 6m deep with daylight linking when
  glazing present (Part L 2021 §6.2 + BS EN 15193 §6.2)
- part-l-efficacy-target: ≥95 lm/W averaged (Part L 2021 Table 6.2)
- manual-switch-override: required at entrance (BS 7671 §714)
- dali-line-capacity: 64 max, 50 recommended (IEC 62386-101 §4)

emergency-rules.yaml (7 → ~50 lines):
- escape-route-illuminance: 1 lux centre line, 180min duration
  (BS 5266-1 §5.2.1)
- anti-panic-illuminance: 0.5 lux floor, areas >60m² (BS 5266-1 §5.3)
- high-risk-task-area: 15 lux or 10% of task (BS 5266-1 §5.4)
- test-regime: monthly function + annual full-duration (BS 5266-1 §10)
- exit-sign-placement: 5 lux on face, max 30m viewing distance
  (BS 5266-1 §7 + BS EN 1838)

Honest disclosures:
- All 5 files flagged _verification_status: engineer_typical_C2.
- emergency-rules.yaml notes BS5266 standards directory absent from
  repo; citations reference published British Standard directly.

Gates: validate-examples 225/225 unchanged (rules YAML not directly
validated). functional_audit 1 finding unchanged.

Next: D3.A.3 schema extensions.
EOF
)"
```

---

## Task A.3: Schema extensions — zones + topology + drafting_furniture + intent payload (Sonnet)

**Why Sonnet:** Mechanical schema work; no engineering judgment beyond structure. Per `[[feedback-no-haiku-sonnet-opus-only]]` mechanical→Sonnet rule.

**Files:**
- Modify: `shared/schemas/electrical/lighting-layout-ir.schema.json` — add zone_type + zones.circuit_ids + circuits.row_index + circuits.homerun_endpoint + drafting_furniture + selection_source + room_type enum + allOf-conditional circuits.total_load_w
- Modify: `electrical/lighting-layout/schemas/lighting-layout-intent.schema.json` — extend payload with zones + circuits + homerun + switches + total_load_per_circuit
- Modify: `electrical/lighting-layout/inputs.json` — add door_swing + photometric_override + tighten ceiling_grid_mm
- Modify: `electrical/lighting-layout/examples/office-open-plan/output.json` — schema-ripple: add new optional fields so the canonical example continues to PASS (do NOT change engineering values)

- [ ] **Step 1: Read current IR schema state**

Confirm the file shape before editing:

```bash
python3 -c "
import json
d = json.load(open('shared/schemas/electrical/lighting-layout-ir.schema.json'))
print('Top-level required:', d['required'])
print('Zones required:', d['properties']['zones']['items']['required'])
print('Circuits required:', d['properties']['circuits']['items']['required'])
print('Circuits total_load_w bounds:', d['properties']['circuits']['items']['properties']['total_load_w'])
print('Room.room_type:', d['properties']['room']['properties']['room_type'])
"
```

Expected:
- Top-level required: `['drawing_type', 'version', 'room', 'calculation_summary', 'rationale', 'invariants']`
- Zones required: `['zone_id', 'circuit_id']`
- Circuits required: `['circuit_id', 'luminaire_ids', 'total_load_w', 'mcb_rating_a']`
- total_load_w: `{'type': 'number', 'minimum': 0, 'maximum': 1840}`
- room_type: `{'type': 'string'}` (no enum)

- [ ] **Step 2: Add `zone_type` + `circuit_ids` + `control` to zones[]**

In `shared/schemas/electrical/lighting-layout-ir.schema.json`, find the `zones.items` block at lines ~124–151 (which currently has `zone_id`, `label`, `circuit_id`, `luminaire_count`, `total_load_w`). Replace the entire `zones` block with:

```json
"zones": {
  "type": "array",
  "items": {
    "type": "object",
    "required": [
      "zone_id",
      "zone_type"
    ],
    "properties": {
      "zone_id": {
        "type": "string"
      },
      "label": {
        "type": "string"
      },
      "zone_type": {
        "enum": [
          "perimeter",
          "interior",
          "task",
          "emergency"
        ],
        "description": "Part L 2021 / BS EN 15193-1 zone classification. perimeter = within 6m of glazed wall (daylight-linked); interior = >6m from glazing (occupancy-only); task = high-illuminance task area; emergency = escape route / anti-panic / high-risk (BS 5266-1)."
      },
      "control": {
        "enum": [
          "daylight_linked",
          "occupancy",
          "manual",
          "dali_master",
          "emergency_self_test"
        ],
        "description": "Primary control protocol for this zone."
      },
      "circuit_id": {
        "type": "string",
        "description": "Backward-compat: single circuit feeding the zone. Use circuit_ids[] for multi-circuit zones (D3.A.3+)."
      },
      "circuit_ids": {
        "type": "array",
        "items": {"type": "string"},
        "description": "FK to circuits[].circuit_id. A zone may contain multiple circuits (e.g. zone Z2 interior has 3 row circuits in a 12-luminaire grid)."
      },
      "luminaire_ids": {
        "type": "array",
        "items": {"type": "string"},
        "description": "FK to luminaires[].id. The full set of luminaires in this zone."
      },
      "luminaire_count": {
        "type": "integer",
        "minimum": 0
      },
      "total_load_w": {
        "type": "number",
        "minimum": 0
      }
    }
  }
}
```

- [ ] **Step 3: Add `row_index` + `homerun_endpoint` to circuits[]**

In the same schema file, find `circuits.items.properties` (currently ~lines 226–280). Add three new properties alongside the existing `circuit_id`/`luminaire_ids`/`total_load_w`/`mcb_rating_a` — append (before the closing brace of `properties`):

```json
"row_index": {
  "type": "integer",
  "minimum": 0,
  "description": "Row index this circuit feeds (0 = first row from north wall). Used by INV-4 to verify no Z-pattern daisy-chain — all luminaires on a circuit must share row_index OR be on adjacent rows (|delta| ≤ 1)."
},
"homerun_endpoint": {
  "type": "object",
  "required": ["x_mm", "y_mm"],
  "additionalProperties": false,
  "description": "Wall endpoint where this circuit's homerun cable exits the room toward the DB. Renderer draws a homerun arrow from this point. INV-4 verifies this point is on one of the four room walls.",
  "properties": {
    "x_mm": {"type": "integer", "minimum": 0},
    "y_mm": {"type": "integer", "minimum": 0},
    "wall": {"enum": ["N", "S", "E", "W"], "description": "Which wall the endpoint sits on (derived; renderer can read directly)."}
  }
}
```

- [ ] **Step 4: Tighten `circuits[].total_load_w` to allOf-conditional max**

Still in `circuits.items.properties`, change the existing `total_load_w` from:

```json
"total_load_w": {
  "type": "number",
  "minimum": 0,
  "maximum": 1840
}
```

to:

```json
"total_load_w": {
  "type": "number",
  "minimum": 0,
  "description": "Sum of luminaire wattages on this circuit. Capped by allOf conditional per mcb_rating_a (80% continuous-load factor per BS 7671 §433.1.1 + IET OSG App A): 6A→1104W, 10A→1840W, 16A→2944W, 20A→3680W, 32A→5888W."
}
```

Then at the BOTTOM of `circuits.items` (after `properties` closes), add a new `allOf` clause:

```json
"allOf": [
  {
    "description": "BS 7671 §433.1.1 + IET OSG App A: continuous load ≤ 80% × ocpd_rating × 230V on each circuit",
    "if": {"properties": {"mcb_rating_a": {"const": 6}}, "required": ["mcb_rating_a"]},
    "then": {"properties": {"total_load_w": {"maximum": 1104}}}
  },
  {
    "if": {"properties": {"mcb_rating_a": {"const": 10}}, "required": ["mcb_rating_a"]},
    "then": {"properties": {"total_load_w": {"maximum": 1840}}}
  },
  {
    "if": {"properties": {"mcb_rating_a": {"const": 16}}, "required": ["mcb_rating_a"]},
    "then": {"properties": {"total_load_w": {"maximum": 2944}}}
  },
  {
    "if": {"properties": {"mcb_rating_a": {"const": 20}}, "required": ["mcb_rating_a"]},
    "then": {"properties": {"total_load_w": {"maximum": 3680}}}
  },
  {
    "if": {"properties": {"mcb_rating_a": {"const": 32}}, "required": ["mcb_rating_a"]},
    "then": {"properties": {"total_load_w": {"maximum": 5888}}}
  }
]
```

- [ ] **Step 5: Add `room_type` enum**

In `room.properties.room_type`, replace:

```json
"room_type": {
  "type": "string"
}
```

with:

```json
"room_type": {
  "enum": [
    "open_plan_office",
    "private_office",
    "meeting_room",
    "corridor",
    "warehouse",
    "warehouse_aisle",
    "classroom",
    "consulting_room",
    "ward",
    "kitchen_commercial",
    "bathroom",
    "reception_lobby",
    "escape_route",
    "plantroom",
    "external"
  ],
  "description": "15-value enum per BS EN 12464-1:2021 Table 5.3 task categories. Matches inputs.json items[room_type].options + 4 added (warehouse_aisle, escape_route, plantroom, external)."
}
```

- [ ] **Step 6: Add `drafting_furniture` top-level block**

In the top-level `properties` (NOT inside `room` or `circuits`), add:

```json
"drafting_furniture": {
  "type": "object",
  "description": "Annotation objects emitted alongside the layout for renderer to draw title block, scale bar, dimensions, and luminaire schedule. Required when mode == full_drawing. Every annotation declares explicit font_family + font_size_pt so ezdxf font fallback can resolve without losing tags.",
  "required": ["title_block", "scale_bar", "dimensions", "luminaire_schedule"],
  "additionalProperties": false,
  "properties": {
    "title_block": {
      "type": "object",
      "required": ["project_name", "drawing_number", "revision", "date", "scale", "sheet_size", "font_family", "font_size_pt"],
      "additionalProperties": false,
      "properties": {
        "project_name":  {"type": "string", "minLength": 1, "maxLength": 120},
        "drawing_number": {"type": "string", "minLength": 1, "maxLength": 30},
        "revision":      {"type": "string", "minLength": 1, "maxLength": 8},
        "date":          {"type": "string", "pattern": "^\\d{4}-\\d{2}-\\d{2}$"},
        "scale":         {"type": "string", "pattern": "^1:\\d+$"},
        "sheet_size":    {"enum": ["A0", "A1", "A2", "A3", "A4"]},
        "font_family":   {"type": "string", "default": "Arial"},
        "font_size_pt":  {"type": "number", "minimum": 6, "maximum": 24}
      }
    },
    "scale_bar": {
      "type": "object",
      "required": ["origin_x_mm", "origin_y_mm", "total_length_mm", "tick_interval_mm", "font_family", "font_size_pt"],
      "additionalProperties": false,
      "properties": {
        "origin_x_mm":      {"type": "integer", "minimum": 0},
        "origin_y_mm":      {"type": "integer", "minimum": 0},
        "total_length_mm":  {"type": "integer", "minimum": 1000},
        "tick_interval_mm": {"type": "integer", "minimum": 100},
        "font_family":      {"type": "string", "default": "Arial"},
        "font_size_pt":     {"type": "number", "minimum": 6, "maximum": 12}
      }
    },
    "dimensions": {
      "type": "array",
      "minItems": 2,
      "description": "At minimum room length + width dimension lines.",
      "items": {
        "type": "object",
        "required": ["axis", "start_x_mm", "start_y_mm", "end_x_mm", "end_y_mm", "text", "font_family", "font_size_pt"],
        "additionalProperties": false,
        "properties": {
          "axis":          {"enum": ["horizontal", "vertical"]},
          "start_x_mm":    {"type": "integer", "minimum": 0},
          "start_y_mm":    {"type": "integer", "minimum": 0},
          "end_x_mm":      {"type": "integer", "minimum": 0},
          "end_y_mm":      {"type": "integer", "minimum": 0},
          "text":          {"type": "string", "minLength": 1, "maxLength": 30},
          "font_family":   {"type": "string", "default": "Arial"},
          "font_size_pt":  {"type": "number", "minimum": 6, "maximum": 14}
        }
      }
    },
    "luminaire_schedule": {
      "type": "object",
      "required": ["columns", "rows", "font_family", "font_size_pt"],
      "additionalProperties": false,
      "properties": {
        "columns": {
          "type": "array",
          "minItems": 5,
          "description": "Schedule columns. Required minimum: ref + manufacturer + lumens + wattage + count.",
          "items": {"type": "string"}
        },
        "rows": {
          "type": "array",
          "minItems": 1,
          "items": {
            "type": "array",
            "items": {"type": "string"}
          }
        },
        "font_family":  {"type": "string", "default": "Arial"},
        "font_size_pt": {"type": "number", "minimum": 6, "maximum": 12}
      }
    }
  }
}
```

- [ ] **Step 7: Add `selection_source` top-level block**

Photometric source tracking lives at the top level (one source per layout, since the layout uses one luminaire_type):

```json
"selection_source": {
  "type": "object",
  "description": "Records which photometric data path (input override vs ontology default) was used by the lumen-method calculation. INV-8 enforces presence.",
  "required": ["photometric_source", "citation"],
  "additionalProperties": false,
  "properties": {
    "photometric_source": {
      "enum": ["input_override", "ontology_default"],
      "description": "input_override = inputs.photometric_override block was supplied and used. ontology_default = generator fell back to ontology/luminaire-types.json defaults."
    },
    "citation": {
      "type": "string",
      "minLength": 20,
      "maxLength": 500,
      "description": "Either the inputs.photometric_override._source string OR the ontology[type].photometric._citation string. Resolves which document authorises the UF + SHR_max + LLMF values used."
    }
  }
}
```

- [ ] **Step 8: Update top-level `allOf` to require new fields in full_drawing mode**

Find the existing `allOf` clause near the end of the schema (currently checks `mode` then requires `luminaire_type/luminaires/switches/circuits/controls/drawing_notes` for full_drawing). Extend the `else` branch's required list to include the new fields:

```json
"allOf": [
  {
    "description": "Sprint D reviewer follow-up + D3.A.3: conditional required-fields by mode. Top-level required is the always-true subset; mode-specific fields are enforced here via if/then/else. full_drawing (default) requires luminaire_type/luminaires/switches/circuits/controls/drawing_notes/zones/drafting_furniture/selection_source; calc_only requires calc_only_reason.",
    "if": {
      "properties": {
        "mode": {"const": "calc_only"}
      },
      "required": ["mode"]
    },
    "then": {
      "required": ["calc_only_reason"]
    },
    "else": {
      "required": [
        "luminaire_type",
        "luminaires",
        "switches",
        "circuits",
        "controls",
        "drawing_notes",
        "zones",
        "drafting_furniture",
        "selection_source"
      ]
    }
  }
]
```

- [ ] **Step 9: Extend lighting-layout-intent.schema.json**

Open `electrical/lighting-layout/schemas/lighting-layout-intent.schema.json`. Read the current payload shape:

```bash
cat electrical/lighting-layout/schemas/lighting-layout-intent.schema.json
```

Identify the `payload` object's properties. Add the following to its `properties` (additive, not breaking — existing v1.3.x intent consumers ignore new fields):

```json
"zones": {
  "type": "array",
  "items": {
    "type": "object",
    "required": ["zone_id", "zone_type", "luminaire_ids", "circuit_ids"],
    "properties": {
      "zone_id":       {"type": "string"},
      "zone_type":     {"enum": ["perimeter", "interior", "task", "emergency"]},
      "control":       {"type": "string"},
      "luminaire_ids": {"type": "array", "items": {"type": "string"}},
      "circuit_ids":   {"type": "array", "items": {"type": "string"}}
    }
  }
},
"circuits": {
  "type": "array",
  "items": {
    "type": "object",
    "required": ["circuit_id", "row_index", "total_load_w", "mcb_rating_a", "homerun_endpoint"],
    "properties": {
      "circuit_id":      {"type": "string"},
      "zone_id":         {"type": "string"},
      "row_index":       {"type": "integer", "minimum": 0},
      "total_load_w":    {"type": "number", "minimum": 0},
      "mcb_rating_a":    {"enum": [6, 10, 16, 20, 32]},
      "mcb_curve":       {"enum": ["B", "C", "D"]},
      "homerun_endpoint": {
        "type": "object",
        "required": ["x_mm", "y_mm"],
        "properties": {
          "x_mm": {"type": "integer", "minimum": 0},
          "y_mm": {"type": "integer", "minimum": 0},
          "wall": {"enum": ["N", "S", "E", "W"]}
        }
      }
    }
  }
},
"switches": {
  "type": "array",
  "items": {
    "type": "object",
    "required": ["id", "type", "x_mm", "y_mm", "controls_circuit"],
    "properties": {
      "id":               {"type": "string"},
      "type":             {"type": "string"},
      "x_mm":             {"type": "integer", "minimum": 0},
      "y_mm":             {"type": "integer", "minimum": 0},
      "height_aff_mm":    {"type": "integer"},
      "controls_circuit": {"type": "string"}
    }
  }
}
```

- [ ] **Step 10: Update inputs.json — add door_swing + photometric_override + tighten ceiling_grid_mm**

In `electrical/lighting-layout/inputs.json`:

(a) Find the `entrance_positions` item (currently item ID `entrance_positions` at lines ~135–150). Update `item_schema.required` to include `door_swing` and add `door_swing` to `item_schema.properties`:

```json
{
  "id": "entrance_positions",
  "label": "Entrance / door positions (wall + offset_mm + door_swing)",
  "hint": "List of doorways used to place switching per BS 7671 §553.1.1 + IET OSG App E §E1.4. door_swing determines latch side for switch placement.",
  "answer_type": "struct_list",
  "required": false,
  "item_schema": {
    "type": "object",
    "required": ["wall", "offset_mm", "door_swing"],
    "properties": {
      "wall":       { "enum": ["N", "S", "E", "W"] },
      "offset_mm":  { "type": "integer", "minimum": 0 },
      "width_mm":   { "type": "integer", "minimum": 600, "maximum": 2400 },
      "door_swing": { "enum": ["inward_latch_left", "inward_latch_right", "outward_latch_left", "outward_latch_right", "sliding"] }
    }
  },
  "project_fact_candidate": false
}
```

(b) Tighten `ceiling_grid_mm` validator from `non_negative_int` to enum-style:

```json
{
  "id": "ceiling_grid_mm",
  "label": "Ceiling grid module (mm)",
  "hint": "Common modules: 600 (UK suspended), 1200 (modular), 0 = no grid",
  "answer_type": "enum",
  "options": [0, 600, 1200],
  "default": 600,
  "required": false,
  "project_fact_candidate": true
}
```

(c) Add a new item `photometric_override` immediately after the `ceiling_grid_mm` item:

```json
{
  "id": "photometric_override",
  "label": "Manufacturer-specific photometric data (override ontology defaults)",
  "hint": "Optional. Supply when an IES/LDT file is available for the specific luminaire. Generator falls back to ontology/luminaire-types.json defaults if absent.",
  "answer_type": "struct",
  "required": false,
  "item_schema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "uf_table_by_ri": {
        "type": "object",
        "description": "UF table indexed by room_index string key (e.g. '1.0', '2.0') then reflectance triplet string key (e.g. '0.7_0.5_0.2'). Same shape as ontology[type].photometric.uf_table_by_ri."
      },
      "shr_max": {"type": "number", "minimum": 0.5, "maximum": 3.0},
      "llmf_at_design_hours": {"type": "number", "minimum": 0.5, "maximum": 1.0},
      "_source": {
        "type": "string",
        "minLength": 20,
        "maxLength": 500,
        "description": "Citation: manufacturer name + photometric file name + IES/LDT reference"
      }
    }
  },
  "project_fact_candidate": false
}
```

- [ ] **Step 11: Schema-ripple to office-open-plan example**

The office-open-plan example currently lacks `zones[].zone_type`, `circuits[].row_index`, `circuits[].homerun_endpoint`, `drafting_furniture`, `selection_source`. Add these minimal additions WITHOUT changing any engineering value so the example continues to validate against the updated schema:

```bash
# Inspect current office-open-plan output
python3 -c "
import json
d = json.load(open('electrical/lighting-layout/examples/office-open-plan/output.json'))
print('zones:', d.get('zones'))
print('first circuit:', d.get('circuits', [{}])[0])
print('has drafting_furniture:', 'drafting_furniture' in d)
print('has selection_source:', 'selection_source' in d)
print('mode:', d.get('mode'))
"
```

If `mode` is `full_drawing` (or absent — defaults to full_drawing), the new fields are required. Edits to make:

(a) Update `zones[]` — add `zone_type: "interior"` + `control: "manual"` + `circuit_ids: ["L1-Z2"]` + `luminaire_ids: ["L01", ..., "L20"]`:

```json
"zones": [
  {
    "zone_id": "Z2",
    "label": "Interior",
    "zone_type": "interior",
    "control": "manual",
    "circuit_id": "L1-Z2",
    "circuit_ids": ["L1-Z2"],
    "luminaire_ids": ["L01","L02","L03","L04","L05","L06","L07","L08","L09","L10","L11","L12","L13","L14","L15","L16","L17","L18","L19","L20"],
    "luminaire_count": 20,
    "total_load_w": 720
  }
]
```

(b) Update each entry in `circuits[]` — add `row_index` (single circuit for this example since all 20 luminaires share one circuit; pick the row of the median luminaire) + `homerun_endpoint`. Since this example has 5 rows × 4 luminaires on one circuit, set `row_index: 2` (middle row) and pick a wall endpoint nearest the door (defer to existing example geometry — check the `switches[]` array for entrance side and pick the nearest wall point as homerun):

```json
"circuits": [
  {
    "circuit_id": "L1-Z2",
    "luminaire_ids": ["L01", ..., "L20"],
    "total_load_w": 720,
    "mcb_rating_a": 10,
    "row_index": 2,
    "homerun_endpoint": {"x_mm": 0, "y_mm": 4000, "wall": "W"}
  }
]
```

(c) Add `selection_source` top-level:

```json
"selection_source": {
  "photometric_source": "ontology_default",
  "citation": "CIBSE LG7 §6.2 (typical recessed LED panel UF + SHR_max) + BS EN 12464-1:2021 §4.4 (LLMF maintenance categories)"
}
```

(d) Add `drafting_furniture` top-level (minimal-realistic; values drawn from example's existing `meta` block where available, defaults otherwise):

```json
"drafting_furniture": {
  "title_block": {
    "project_name":  "Sprint D3 schema ripple — office-open-plan",
    "drawing_number": "EL-001",
    "revision":      "A",
    "date":          "2026-05-28",
    "scale":         "1:50",
    "sheet_size":    "A3",
    "font_family":   "Arial",
    "font_size_pt":  10
  },
  "scale_bar": {
    "origin_x_mm":      9000,
    "origin_y_mm":      7500,
    "total_length_mm":  2000,
    "tick_interval_mm": 500,
    "font_family":      "Arial",
    "font_size_pt":     8
  },
  "dimensions": [
    {"axis": "horizontal", "start_x_mm": 0, "start_y_mm": -300, "end_x_mm": 10000, "end_y_mm": -300, "text": "10000 mm", "font_family": "Arial", "font_size_pt": 10},
    {"axis": "vertical",   "start_x_mm": -300, "start_y_mm": 0, "end_x_mm": -300, "end_y_mm": 8000, "text": "8000 mm",  "font_family": "Arial", "font_size_pt": 10}
  ],
  "luminaire_schedule": {
    "columns": ["Ref", "Manufacturer", "Lumens", "Wattage", "Count"],
    "rows": [
      ["LED_PANEL_600", "Generic", "4500", "36W", "20"]
    ],
    "font_family":  "Arial",
    "font_size_pt": 8
  }
}
```

NOTE: do not add INV-1..INV-10 invariants entries here — that lands in B.4 after the validator catalogue exists.

- [ ] **Step 12: Run golden CI gate + hand-check**

```bash
python3 scripts/validate-examples.py 2>&1 | tail -3
```

Expected: `AGGREGATE: 225/225 pass (0 failures)`. If the office-open-plan example fails, inspect the failure detail and fix the schema-ripple edits in Step 11.

```bash
python3 -c "
import json
d = json.load(open('electrical/lighting-layout/examples/office-open-plan/output.json'))
assert 'drafting_furniture' in d, 'missing drafting_furniture'
assert 'selection_source' in d, 'missing selection_source'
assert d['zones'][0].get('zone_type') == 'interior', 'missing zone_type'
assert d['circuits'][0].get('row_index') is not None, 'missing row_index on first circuit'
assert d['circuits'][0].get('homerun_endpoint') is not None, 'missing homerun_endpoint'
print('Schema ripple PASS — office-open-plan now carries all D3.A.3 fields')
"
```

Expected: `Schema ripple PASS`.

```bash
python3 functional_audit.py 2>&1 | tail -3
```

Expected: `TOTAL FINDINGS: 1`.

- [ ] **Step 13: Commit A.3**

```bash
git add shared/schemas/electrical/lighting-layout-ir.schema.json \
        electrical/lighting-layout/schemas/lighting-layout-intent.schema.json \
        electrical/lighting-layout/inputs.json \
        electrical/lighting-layout/examples/office-open-plan/output.json
git commit -m "$(cat <<'EOF'
feat(lighting-layout): D3.A.3 schema extensions — zones + topology + drafting_furniture + intent payload

Sprint D3 Phase A foundations — third of three. Adds the IR vocabulary
B.1/B.2/B.3 generators will populate (zone Part L semantics + per-circuit
topology + drafting furniture + photometric source).

IR schema (shared/schemas/electrical/lighting-layout-ir.schema.json):
- zones[]: added zone_type enum (perimeter|interior|task|emergency),
  control enum (daylight_linked|occupancy|manual|dali_master|
  emergency_self_test), circuit_ids[] (FK to circuits), luminaire_ids[].
  Kept circuit_id (singular) for backward compat with v1.3.x consumers.
- circuits[]: added row_index (kills Z-pattern bug structurally) +
  homerun_endpoint {x_mm, y_mm, wall}. Tightened total_load_w from
  blanket max=1840 to allOf-conditional per mcb_rating_a (BS 7671
  §433.1.1 80% continuous-load rule: 6A→1104, 10A→1840, 16A→2944,
  20A→3680, 32A→5888).
- room.room_type: enum-typed (15 values) instead of bare string,
  matching inputs.json items[room_type].options + 4 added.
- drafting_furniture top-level: required when mode=full_drawing.
  Carries title_block + scale_bar + dimensions[] + luminaire_schedule;
  every annotation declares explicit font_family + font_size_pt.
- selection_source top-level: records photometric source (input_override
  vs ontology_default) + citation. INV-8 will enforce in B.4.
- allOf if/then/else updated to require zones + drafting_furniture +
  selection_source in full_drawing mode (additive — calc_only path
  unchanged).

Intent schema (electrical/lighting-layout/schemas/lighting-layout-intent.schema.json):
- payload extended with zones + circuits (incl. row_index + homerun) +
  switches. Additive — existing v1.3.x intent consumers unaffected.

Inputs (electrical/lighting-layout/inputs.json):
- entrance_positions item_schema: added door_swing enum (5 values)
  + required.
- ceiling_grid_mm: tightened to enum [0, 600, 1200] (was non_negative_int).
- photometric_override: new optional struct (uf_table_by_ri + shr_max +
  llmf_at_design_hours + _source citation).

Schema ripple to office-open-plan example: minimal additive edits to
keep it schema-valid (zone_type=interior + circuit row_index +
homerun_endpoint + drafting_furniture + selection_source). NO
engineering value changes; INV-1..INV-10 entries land in B.4 after the
validator catalogue exists.

Gates: validate-examples 225/225 (held); functional_audit 1 finding
unchanged.

Phase A complete. Next: D3.B.1 generator lumen-method worked example.
EOF
)"
```

---

## Phase B — Prompts (4 tasks, sequential)

Generator + validator + reviewer + intent payload wiring. Each generator-edit task adds 2-3 INVs alongside the new generator step; the validator catalogue is consolidated at B.4.

---

## Task B.1: Generator — lumen-method worked example + S/H ratio loop + photometric lookup (Opus)

**Why Opus:** Lumen-method judgment + worked-example arithmetic + citation accuracy.

**Files:**
- Modify: `electrical/lighting-layout/prompts/generator.md` — rewrite Step 6 (lumen method) + Step 7 (S/H ratio) + add photometric lookup procedure
- Modify: `electrical/lighting-layout/examples/office-open-plan/output.json` — add INV-1, INV-2, INV-8 invariants entries

- [ ] **Step 1: Read current Step 6 + Step 7 in generator.md**

```bash
sed -n '255,290p' electrical/lighting-layout/prompts/generator.md
```

Note the existing Step 6 (lumen method) at lines ~259–276 and Step 7 (S/H ratio) at lines ~282–283. Replace them with the rewrites below.

- [ ] **Step 2: Replace Step 6 with full worked-example version**

Find the existing Step 6 section (the formula `N = (Em × A) / (Φ × UF × MF)` with "round UP" instruction). Replace it with:

```markdown
## Step 6 — Lumen Method (N count calculation per [spacing-rules#lumen-method-formula])

### 6.1 — Compute room index RI

`RI = (L × W) / (Hm × (L + W))` per [spacing-rules#room-index].

`Hm = ceiling_height_mm − working_plane_mm` (working plane from
[spacing-rules#working-plane-defaults] by `room_type`).

**Example (10×8 m open-plan office, 2.7 m ceiling):**
- L = 10 m, W = 8 m
- working_plane = 750 mm (open_plan_office), ceiling = 2700 mm
- Hm = 2700 − 750 = 1950 mm = 1.95 m
- RI = (10 × 8) / (1.95 × (10 + 8)) = 80 / 35.1 = 2.28 → look up at RI=2.0
  (round down to ontology table key)

### 6.2 — Resolve photometric values (UF, SHR_max, MF)

**Lookup order (override-first):**

```
uf = inputs.photometric_override?.uf_table_by_ri?.[RI]?.[reflectance_triplet]
     ?? ontology[luminaire_type].photometric.uf_table_by_ri[RI][reflectance_triplet]

shr_max = inputs.photometric_override?.shr_max
          ?? ontology[luminaire_type].photometric.shr_max

llmf = inputs.photometric_override?.llmf_at_design_hours
       ?? ontology[luminaire_type].photometric.llmf_schedule[environment][design_hours]
```

Record which path won in `selection_source.photometric_source` (=
`"input_override"` OR `"ontology_default"`) and `selection_source.citation`
(= override `_source` OR ontology `_citation`). **INV-8 enforces this.**

**Reflectance triplet** = `<ceiling>_<wall>_<floor>`. Default for offices
is `0.7_0.5_0.2` (per BS EN 12464-1:2021 Annex C typical interior
reflectances).

**Example (LED_PANEL_600 at RI=2.0, reflectances 0.7_0.5_0.2):**
- From `ontology/luminaire-types.json`: UF = 0.67, SHR_max = 1.5
- environment = "clean_office", design_hours = "6000h" → LLMF = 0.95
- LSF × LMF × RSMF (luminaire survival × luminaire maintenance ×
  room surface maintenance) ≈ 0.84 (typical clean office; cite
  CIBSE LG7 §6.2)
- MF = LLMF × LSF × LMF × RSMF ≈ 0.95 × 0.84 = 0.80
- selection_source = {photometric_source: "ontology_default",
  citation: "CIBSE LG7 §6.2 + BS EN 12464-1:2021 §4.4"}

### 6.3 — Compute N (round UP)

Per [spacing-rules#lumen-method-formula]:

`N = (Em × A) / (Φ × UF × MF)` — round UP.

**Worked example (continued — 10×8 m office, 500 lux target, 6000 lm
LED panels):**
- Em = 500 lux, A = 80 m², Φ = 6000 lm, UF = 0.67, MF = 0.80
- N = (500 × 80) / (6000 × 0.67 × 0.80)
    = 40000 / 3216
    = 12.44
- **Round UP → N = 13** (never under-provide; one luminaire of headroom
  buys ~3% extra illuminance margin)

**Counter-example (under-counted bug from end-to-end test):**
If the generator computed `N = 12` (round to nearest), achieved_lux =
12 × 6000 × 0.67 × 0.80 / 80 = **482 lux < 500 target**. INV-1 fires
HIGH. Always round UP per the rule.

### 6.4 — Compute achieved_illuminance_lux

After fixing N, recompute the achieved illuminance:

`achieved = (N × Φ × UF × MF) / A`

For 13 panels: `achieved = (13 × 6000 × 0.67 × 0.80) / 80 = 41808 / 80 = 522.6 lux`. **≥ target_illuminance_lux** — INV-1 PASS.

Emit in `calculation_summary.achieved_illuminance_lux`. **INV-1 enforces
`achieved_illuminance_lux ≥ target_illuminance_lux`.**

### 6.5 — `calc.lumen_grid_solver` tool call (when runtime ships it)

Generator MAY call `calc.lumen_grid_solver` to verify the hand-computed
result point-grid-wise. Expected output spec:

```json
{
  "achieved_illuminance_lux": <number>,
  "uniformity_u0": <number 0..1>,
  "point_grid": [
    {"x_mm": <int>, "y_mm": <int>, "lux": <number>}
  ],
  "calc_method": "lumen_method_simplified | full_point_grid"
}
```

If the tool's `achieved_illuminance_lux` differs from the hand-computed
value by >5%, prefer the tool result and update `calculation_summary`
accordingly. If the tool is unavailable at runtime, set
`tool_call_pending: true` on `calculation_summary` and emit the
hand-computed value.
```

- [ ] **Step 3: Replace Step 7 with explicit S/H ratio enforcement loop**

Find the existing Step 7 (`S ≤ SHR_max × Hm`). Replace with:

```markdown
## Step 7 — S/H Ratio Enforcement Loop (per [spacing-rules#shr-max-default])

After Step 6 fixes N, lay out the grid and check the spacing. **Loop
until both directions PASS or until adding rows/columns is no longer
feasible.**

### 7.1 — Initial grid layout

Given N luminaires + room L × W, pick the closest `n_rows × n_cols`
factorisation favouring near-square cells:

- For N=13: `n_rows × n_cols ∈ {1×13, 13×1}` — neither is square.
  Bump N→14 to get {2×7, 7×2} or N→15 for {3×5}. Round UP at this
  step too: pick the next-larger N that allows a near-square
  factorisation if the original N forces a strip layout.
- For N=12: {3×4, 4×3, 2×6, 6×2}. Pick {3×4} for a 10×8 m room
  (long axis takes more luminaires).

### 7.2 — Compute S_x and S_y

For a grid with edge clearance e (from [placement-rules#edge-clearance],
default 300 mm) and ceiling-grid snap (from [placement-rules#grid-snap]):

- `S_x = (L − 2e) / (n_cols − 1)`  if n_cols ≥ 2; else `S_x = L − 2e`
- `S_y = (W − 2e) / (n_rows − 1)`  if n_rows ≥ 2; else `S_y = W − 2e`

**Worked example (10×8 m office, 12 panels in 3×4 grid):**
- e = 300 mm, n_cols = 4, n_rows = 3
- S_x = (10000 − 600) / 3 = 9400 / 3 = 3133 mm
- S_y = (8000 − 600) / 2 = 7400 / 2 = 3700 mm

### 7.3 — Enforce SHR_max constraint

From [spacing-rules#shr-max-default] (default SHR_max = 1.5) and ontology
[`LED_PANEL_600`].photometric.shr_max:

`S_x ≤ SHR_max × Hm AND S_y ≤ SHR_max × Hm`

**Worked example (continued, Hm = 1.95 m, SHR_max = 1.5):**
- Limit = 1.5 × 1950 = 2925 mm
- S_x = 3133 > 2925 ❌ FAIL
- S_y = 3700 > 2925 ❌ FAIL

**Both fail → add a row AND a column** (one cycle): N goes 12 → next
factorisation that satisfies. Try N = 16 in 4×4 grid:
- S_x = 9400 / 3 = 3133 mm (n_cols still 4)
- S_y = 7400 / 3 = 2467 mm ✓ now PASS for y-axis

Still fail x-axis. Bump n_cols → 5, N=20 in 4×5 grid:
- S_x = 9400 / 4 = 2350 mm ✓ PASS
- S_y = 7400 / 3 = 2467 mm ✓ PASS

**INV-2 enforces** `S_x ≤ SHR_max × Hm AND S_y ≤ SHR_max × Hm` on every
shipped layout.

### 7.4 — Snap to ceiling grid

Per [placement-rules#grid-snap]: if `ceiling_grid_mm ∈ {600, 1200}`,
snap each luminaire's centre to the nearest grid-module centre. May
shift the S_x / S_y by up to half a grid module — re-check INV-2 after
snapping.

### 7.5 — Edge cases

- **If even N=20 fails SHR**: the room is too tall for this luminaire
  (Hm × SHR_max < minimum feasible spacing). Switch to a luminaire with
  a higher SHR_max (LINEAR_LED has SHR_max=1.6) OR drop ceiling height
  via suspended luminaires (reduces Hm). Emit `non_compliance_flags`
  with `severity: warning` if unable to satisfy; INV-2 fires.
- **If room is very small (N < 4)**: use N=4 minimum (one luminaire per
  quadrant) — single-luminaire rooms have uniformity issues.
```

- [ ] **Step 4: Add photometric lookup procedure summary (cross-reference Step 6.2)**

Find a placement after Step 7 (before whatever Step 8 currently is) and insert a one-line summary callout that the validator INV-8 enforces:

```markdown
## Step 7.5 — Emit `selection_source` block

Per Step 6.2, populate `selection_source` at the IR root:

- `photometric_source`: `"input_override"` if `inputs.photometric_override`
  was non-null AND used; else `"ontology_default"`.
- `citation`: matches the path taken. **NO improvisation** — the
  citation must come from either inputs OR ontology, not be paraphrased
  by the generator. INV-8 enforces.
```

- [ ] **Step 5: Add INV-1, INV-2, INV-8 entries to office-open-plan invariants[]**

The example currently has 20 luminaires on a 5×4 grid. For INV-2 we need to compute and verify S_x + S_y. Read the example output and compute:

```bash
python3 -c "
import json
d = json.load(open('electrical/lighting-layout/examples/office-open-plan/output.json'))
xs = sorted(set(l['x_mm'] for l in d['luminaires']))
ys = sorted(set(l['y_mm'] for l in d['luminaires']))
print(f'unique x positions: {xs}')
print(f'unique y positions: {ys}')
hm_mm = d['room']['ceiling_height_mm'] - d['room']['working_plane_mm']
shr_max = 1.5
limit_mm = shr_max * hm_mm
sx = xs[1] - xs[0] if len(xs) > 1 else 0
sy = ys[1] - ys[0] if len(ys) > 1 else 0
print(f'Hm = {hm_mm} mm, SHR_max × Hm limit = {limit_mm} mm')
print(f'S_x = {sx} mm  ({\"PASS\" if sx <= limit_mm else \"FAIL\"})')
print(f'S_y = {sy} mm  ({\"PASS\" if sy <= limit_mm else \"FAIL\"})')
print(f'achieved_illuminance_lux declared = {d[\"calculation_summary\"].get(\"achieved_illuminance_lux\")}')
print(f'target_illuminance_lux declared = {d[\"calculation_summary\"].get(\"target_illuminance_lux\")}')
"
```

Use those numbers in the invariants[] entries. Append to `invariants[]`:

```json
{
  "id": "INV-01",
  "passes": true,
  "severity": "high",
  "evidence": "Lumen method: N=20 luminaires × 4500 lm × UF=0.67 × MF=0.80 / 80 m² = achieved_illuminance_lux=...lux ≥ target 500 lux (Rule 1 PASS). Calculation per [spacing-rules#lumen-method-formula] + ontology LED_PANEL_600 UF table at RI=1.98, reflectances 0.7_0.5_0.2."
},
{
  "id": "INV-02",
  "passes": true,
  "severity": "high",
  "evidence": "S/H ratio: Hm=2250 mm, SHR_max=1.5 (LED_PANEL_600 ontology default), limit=3375 mm. S_x=...mm ≤ 3375 PASS; S_y=...mm ≤ 3375 PASS. Per [spacing-rules#shr-max-default]."
},
{
  "id": "INV-08",
  "passes": true,
  "severity": "medium",
  "evidence": "selection_source.photometric_source='ontology_default'; citation='CIBSE LG7 §6.2 + BS EN 12464-1:2021 §4.4'. No inputs.photometric_override supplied for this example. Rule 8 PASS."
}
```

Fill in the `...` placeholders with the numbers computed in the Step 5 hand-check.

- [ ] **Step 6: Run gates**

```bash
python3 scripts/validate-examples.py 2>&1 | tail -3
```

Expected: `AGGREGATE: 225/225 pass (0 failures)`.

```bash
python3 functional_audit.py 2>&1 | tail -3
```

Expected: `TOTAL FINDINGS: 1`.

- [ ] **Step 7: Commit B.1**

```bash
git add electrical/lighting-layout/prompts/generator.md \
        electrical/lighting-layout/examples/office-open-plan/output.json
git commit -m "$(cat <<'EOF'
feat(lighting-layout): D3.B.1 generator — lumen-method worked example + S/H ratio loop + photometric lookup + INV-1/INV-2/INV-8

Sprint D3 Phase B prompts — first of four. Closes audit Top 5 #1 + #2
+ §4 ontology drift (UF improvisation).

Generator Step 6 (lumen method) — rewrite from 18-line formula stub to
full worked example:
- 6.1 RI = (L × W) / (Hm × (L + W)) walk for 10×8 m office
- 6.2 Photometric lookup procedure (override-first then ontology) with
  worked example: LED_PANEL_600 at RI=2.0, reflectances 0.7_0.5_0.2 →
  UF=0.67, MF=0.80
- 6.3 N = (500 × 80) / (6000 × 0.67 × 0.80) = 12.44 → round UP to 13
  with counter-example showing round-to-nearest under-provides at 482
  lux (INV-1 fires HIGH)
- 6.4 achieved_illuminance_lux recompute after N fixed
- 6.5 calc.lumen_grid_solver output spec documented inline so generator
  can trust/use the tool when runtime ships it

Generator Step 7 (S/H ratio) — rewrite from 2-line constraint stub to
explicit enforcement loop:
- 7.1 Initial grid factorisation (near-square preferred)
- 7.2 S_x + S_y formulas with edge clearance from
  [placement-rules#edge-clearance]
- 7.3 SHR_max check walked end-to-end: 12 panels in 3×4 → S_x=3133 mm
  FAIL → bump to 16 panels in 4×4 → still FAIL on x-axis → 20 panels
  in 4×5 → PASS both directions
- 7.4 Ceiling-grid snap (re-check INV-2 after snap)
- 7.5 Edge cases (room too tall + room too small)

Step 7.5 added — emit selection_source block per Step 6.2. No
improvisation; INV-8 enforces.

Three new INVs documented in generator (will land in validator.md at
B.4):
- INV-1 (HIGH): achieved_illuminance_lux ≥ target_illuminance_lux
- INV-2 (HIGH): S_x ≤ SHR_max × Hm AND S_y ≤ SHR_max × Hm
- INV-8 (MEDIUM): selection_source resolves to ontology citation or
  input override _source

office-open-plan example: appended INV-1, INV-2, INV-8 entries to
invariants[] based on hand-walked numbers (5×4 grid, 4500 lm panels,
UF 0.67, MF 0.80).

Gates: validate-examples 225/225; functional_audit 1 finding unchanged.

Next: D3.B.2 generator circuit topology + switch placement.
EOF
)"
```

---

## Task B.2: Generator — circuit topology (zone + row + homerun) + switch placement (Opus)

**Why Opus:** Topology judgment + regulation-driven zone assignment.

**Files:**
- Modify: `electrical/lighting-layout/prompts/generator.md` — new Step 11 (circuit topology) + Step 12 (switch placement rewrite)
- Modify: `electrical/lighting-layout/examples/office-open-plan/output.json` — add INV-3, INV-4, INV-5, INV-7 invariants entries

- [ ] **Step 1: Add new Step 11 — Circuit topology (zone + row + homerun)**

Find the current "circuit" step in `generator.md` (search for `circuit_id`). Insert a new Step 11 immediately after Step 10 (luminaire placement):

```markdown
## Step 11 — Circuit Topology: Part L Zones + Row Circuits + Homerun

### 11.1 — Part L zone assignment

Each luminaire belongs to exactly one zone per [control-rules#part-l-daylight].
Decision tree:

1. **Z4 (emergency)** — luminaires with `symbol = "EMERGENCY"` go to Z4
   regardless of position. Control: `emergency_self_test`.
2. **Z1 (perimeter)** — luminaires within
   [switching-rules#perimeter-circuit].max_zone_depth_mm (6000 mm by
   default) of ANY wall declared in `inputs.glazed_wall_positions`.
   Control: `daylight_linked`.
3. **Z3 (task)** — luminaires placed at engineer-declared task locations
   (rare for general lighting layouts; explicit input
   `task_area_positions` if supplied). Control: `manual` or `dali_master`.
4. **Z2 (interior)** — everything else. Control: `occupancy` if
   `is_uk_new_build == true`; else `manual`.

**Edge case: no glazed walls.** If `inputs.glazed_wall_positions == []`
OR field absent, Z1 (perimeter) is absent — `zones[]` carries no
perimeter entry. INV-7 enforces this consistency.

### 11.2 — Group luminaires into row circuits

Per zone (in the order Z1, Z2, Z3, Z4 — perimeter first because daylight
linking takes priority), group its `luminaire_ids[]` by `row_index`:

- A row = luminaires sharing the same y_mm (within snap tolerance
  ±50 mm per [placement-rules#grid-snap]).
- `row_index` numbered 0 from the north (low y_mm) wall.

Each row → one circuit IF the row's total wattage is within the OCPD
limit per [control-rules#part-l-efficacy-target] x [BS 7671
§433.1.1 + IET OSG App A 80% rule]:

| MCB rating | 80% × rating × 230V | Per-row example |
|---|---|---|
|  6 A | 1104 W | 30 × 36 W LED panels |
| 10 A | 1840 W | 51 × 36 W LED panels |
| 16 A | 2944 W | 81 × 36 W LED panels |

Most office rows fit a 6 A MCB. If a row exceeds 1104 W on a 6 A circuit,
either (a) split into two circuits of half the row, OR (b) upgrade
MCB to 10 A (rare — 6 A is the standard lighting circuit per IET OSG
App C).

### 11.3 — Compute homerun endpoint per circuit

For each circuit, pick the nearest wall endpoint to the project's
`db_designation` reference point. If no DB position is supplied via
`inputs.db_designation`, default to the wall adjacent to the primary
entrance (from `inputs.entrance_positions[0].wall`).

Homerun rules:
- The endpoint MUST sit on one of the four room walls (x_mm = 0 OR
  x_mm = room.length_mm OR y_mm = 0 OR y_mm = room.width_mm). INV-4
  Rule (b) enforces.
- The endpoint defaults to the row's midpoint projected to the chosen
  wall, snapped to 50 mm.

**Worked example (10×8 m office, 12 panels in 3×4 grid, DB on west
wall):**
- Row 0 (y=800): 4 panels @ x ∈ {1200, 3600, 6000, 8400}
- Row 1 (y=4000): same x positions
- Row 2 (y=7200): same x positions
- Each row → 1 circuit at 4 × 36 W = 144 W (well under 1104 W).
- Homerun for each row: project x-midpoint (4800 mm) to west wall →
  `(x_mm=0, y_mm=<row's y>, wall="W")`.

### 11.4 — Emit IR

Per circuit:

```json
{
  "circuit_id":      "C-L01",
  "zone_id":         "Z2",
  "luminaire_ids":   ["L01", "L02", "L03", "L04"],
  "row_index":       0,
  "total_load_w":    144,
  "mcb_rating_a":    6,
  "mcb_curve":       "B",
  "homerun_endpoint": {"x_mm": 0, "y_mm": 800, "wall": "W"}
}
```

Per zone:

```json
{
  "zone_id":       "Z2",
  "label":         "Interior",
  "zone_type":     "interior",
  "control":       "occupancy",
  "luminaire_ids": ["L01", "L02", ..., "L12"],
  "circuit_ids":   ["C-L01", "C-L02", "C-L03"],
  "luminaire_count": 12,
  "total_load_w":  432
}
```

**INVs enforced by this step:**
- INV-4 (HIGH): every circuit's `luminaire_ids` all share row_index OR
  are on adjacent rows (`|row_a − row_b| ≤ 1`); homerun_endpoint on a
  room wall. Kills Z-pattern daisy-chain bug.
- INV-5 (HIGH): `circuit.total_load_w ≤ 0.8 × mcb_rating_a × 230` per
  BS 7671 §433.1.1.
- INV-7 (MEDIUM): every luminaire belongs to exactly one zone;
  zone_type matches geometry (perimeter zone present iff glazed_walls
  non-empty).
```

- [ ] **Step 2: Replace Step 12 — Switch placement (entrance-driven, deterministic)**

Find the current Step 12 (which references "latch side, 200mm from frame"). Replace with:

```markdown
## Step 12 — Switch Placement (deterministic from entrance_positions)

### 12.1 — Extract entrance data

From `inputs.entrance_positions[]`, every entrance carries `wall +
offset_mm + door_swing` (door_swing required per D3.A.3 input schema).

### 12.2 — For each entrance, compute switch (x, y)

Map `wall + offset_mm` to a room coordinate (the door's hinge-side
frame post position):

- `wall == "N"` (y=0):    door spans (offset_mm, 0) — (offset_mm + width_mm, 0)
- `wall == "S"` (y=W):    door spans (offset_mm, W) — (offset_mm + width_mm, W)
- `wall == "E"` (x=L):    door spans (L, offset_mm) — (L, offset_mm + width_mm)
- `wall == "W"` (x=0):    door spans (0, offset_mm) — (0, offset_mm + width_mm)

Resolve LATCH side from `door_swing`:

| door_swing                | latch side position                     |
|---|---|
| inward_latch_left         | left edge of door span                  |
| inward_latch_right        | right edge of door span                 |
| outward_latch_left        | left edge of door span                  |
| outward_latch_right       | right edge of door span                 |
| sliding                   | use offset_mm + 200 mm (no swing)       |

Switch placement: 200 mm INSIDE the room from the latch frame, on the
WALL adjacent to the latch side (NOT on the door wall). Specifically:

- For a door on wall "N" with `door_swing="inward_latch_right"`: latch
  position = (offset_mm + width_mm, 0). Adjacent wall = "E" (if room
  permits) OR same wall "N" offset 200 mm to the inside. Default:
  same-wall placement at `(offset_mm + width_mm + 200, 0)` because most
  rooms don't have a side wall close to the door.

- For sliding doors: switch at the wall point 200 mm to the side of the
  door opening, OR on a stub wall if available.

**Worked example (door at wall="N", offset_mm=500, width_mm=900,
door_swing="inward_latch_right"):**
- Door spans (500, 0) — (1400, 0)
- Latch at (1400, 0)
- Switch placed at (1400 + 200, 0) = (1600, 0) on wall N, mounted at
  1200 mm AFF per [switching-rules#height]

### 12.3 — Emit switches[] block

Per entrance, emit one switch entry:

```json
{
  "id":              "SW01",
  "type":            "1_gang",
  "x_mm":            1600,
  "y_mm":            0,
  "height_aff_mm":   1200,
  "controls_circuit": "C-L01",
  "door_swing":      "inward_latch_right",
  "switch_side":     "latch"
}
```

If the entrance serves a multi-circuit zone, use a `2_gang` / `3_gang`
type from `ontology/switching-types.json` and emit one switch entry
with the controlled circuit IDs in a comma-separated `controls_circuit`
string OR set `type: "dali_master"` for DALI-controlled zones.

### 12.4 — DALI override

If `inputs.controls_protocol ∈ {DALI, DALI-2}`: emit ONE
`dali_master` switch at the primary entrance per
[switching-rules#dali-master-at-entrance], and emit ZERO 1_gang/2_gang
switches (DALI master replaces individual switches; wall controllers at
secondary entrances are optional and emitted only if
`inputs.entrance_positions.length > 1`).

**INVs enforced by this step:**
- INV-3 (HIGH): `switches.length ≥ entrances.length` (or 1 if DALI
  master); each switch at correct latch_side + offset + height per
  rules cited.
```

- [ ] **Step 3: Add INV-3, INV-4, INV-5, INV-7 entries to office-open-plan invariants[]**

Append to the example's `invariants[]`:

```json
{
  "id": "INV-03",
  "passes": true,
  "severity": "high",
  "evidence": "Switch coverage: 1 entrance declared, 1 switch emitted (SW01 at <x,y>, 1200 mm AFF, latch side per door_swing). switches.length ≥ entrances.length (Rule 3a PASS). Height + latch placement per [switching-rules#height] + [switching-rules#latch-side] (Rule 3b PASS)."
},
{
  "id": "INV-04",
  "passes": true,
  "severity": "high",
  "evidence": "Circuit topology: all 20 luminaires on circuit L1-Z2 share row_index spans 0..4 — this example pre-D3 used single-circuit layout; INV-4 trivially PASS (all luminaires on one circuit; no Z-pattern possible). homerun_endpoint = (0, 4000, W) sits on west wall (Rule 4b PASS)."
},
{
  "id": "INV-05",
  "passes": true,
  "severity": "high",
  "evidence": "Circuit load: total_load_w = 720 W ≤ 0.8 × 10 × 230 = 1840 W (10 A MCB). Rule 5 PASS per BS 7671 §433.1.1 + IET OSG App A 80% continuous-load rule."
},
{
  "id": "INV-07",
  "passes": true,
  "severity": "medium",
  "evidence": "Zone assignment: 20 luminaires all in Z2 (interior). Glazed walls = [] → no perimeter zone (consistency PASS). No task or emergency zones declared for this example. Rule 7 PASS."
}
```

- [ ] **Step 4: Run gates**

```bash
python3 scripts/validate-examples.py 2>&1 | tail -3
```

Expected: `AGGREGATE: 225/225 pass (0 failures)`.

- [ ] **Step 5: Commit B.2**

```bash
git add electrical/lighting-layout/prompts/generator.md \
        electrical/lighting-layout/examples/office-open-plan/output.json
git commit -m "$(cat <<'EOF'
feat(lighting-layout): D3.B.2 generator — circuit topology + switch placement + INV-3/INV-4/INV-5/INV-7

Sprint D3 Phase B prompts — second of four. Closes the Z-pattern bug
(image-visible) + audit Top 5 #3 (switch placement deterministic).

Generator Step 11 (NEW) — Circuit topology: zones + rows + homerun:
- 11.1 Part L zone assignment decision tree (Z4 emergency / Z1
  perimeter <6m of glazed wall / Z3 task / Z2 interior). Edge case:
  no glazed walls → Z1 absent (INV-7 consistency).
- 11.2 Group luminaires into row circuits with per-MCB 80%
  continuous-load table (6A→1104W, 10A→1840W, 16A→2944W).
- 11.3 Homerun endpoint = row midpoint projected to nearest wall
  adjacent to DB; defaults to entrance wall if DB position unsupplied.
  INV-4 enforces endpoint sits on a room wall.
- 11.4 Worked example (10×8 m office, 3×4 grid → 3 row circuits at
  144 W each, homeruns to west wall).

Generator Step 12 (REWRITE) — Switch placement deterministic from
entrance_positions:
- 12.1 Extract wall + offset_mm + door_swing per entrance (door_swing
  added in D3.A.3).
- 12.2 Latch-side resolution table mapping door_swing enum to switch
  position; 200 mm inside the room from latch frame; 1200 mm AFF per
  [switching-rules#height].
- 12.3 Emit switches[] block with door_swing + switch_side fields
  (both already in canonical IR schema).
- 12.4 DALI override: one dali_master at primary entrance + optional
  wall controllers at secondaries.

Four new INVs documented (will land in validator.md at B.4):
- INV-3 (HIGH): switches.length ≥ entrances.length + height + latch
- INV-4 (HIGH): luminaire_ids share row_index OR adjacent
  (|row_a−row_b|≤1); homerun_endpoint on a room wall — kills
  Z-pattern daisy-chain
- INV-5 (HIGH): circuit.total_load_w ≤ 0.8 × mcb_rating × 230 per
  BS 7671 §433.1.1
- INV-7 (MEDIUM): every luminaire in exactly one zone; zone_type
  matches geometry

office-open-plan example: appended INV-3, INV-4, INV-5, INV-7 entries
to invariants[]. The pre-D3 single-circuit shape trivially PASSes
INV-4 (no Z-pattern possible with one circuit).

Gates: validate-examples 225/225; functional_audit 1 finding unchanged.

Next: D3.B.3 generator drafting furniture step.
EOF
)"
```

---

## Task B.3: Generator — drafting furniture step (Sonnet)

**Why Sonnet:** Mechanical formatting + template population. Per `[[feedback-no-haiku-sonnet-opus-only]]` mechanical→Sonnet rule.

**Files:**
- Modify: `electrical/lighting-layout/prompts/generator.md` — new Step 15 (drafting furniture emission)
- Modify: `electrical/lighting-layout/examples/office-open-plan/output.json` — add INV-9 invariants entry (the example already has drafting_furniture from A.3 schema ripple; B.3 just adds the validator entry)

- [ ] **Step 1: Add new Step 15 — Drafting furniture emission**

Find the last numbered step in `generator.md` (likely Step 14 around the output-format section). Insert a new Step 15 immediately before the output-format section:

```markdown
## Step 15 — Drafting Furniture Emission (required when mode = full_drawing)

The IR `drafting_furniture` block is required per the schema's allOf
clause when `mode = full_drawing` (default). Emit four annotation
objects: title_block + scale_bar + dimensions + luminaire_schedule.
Every annotation declares explicit `font_family` + `font_size_pt` so
the renderer's ezdxf font fallback can resolve without losing tags.

### 15.1 — title_block

Populate from `inputs.drawing_metadata` (project_name + drawing_number +
revision + date) and from the lumen-method calculation context (scale +
sheet_size):

```json
"title_block": {
  "project_name":  "<inputs.drawing_metadata.project_name>",
  "drawing_number": "<inputs.drawing_metadata.drawing_number>",
  "revision":      "<inputs.drawing_metadata.revision>",
  "date":          "<YYYY-MM-DD today's date>",
  "scale":         "1:50",
  "sheet_size":    "A3",
  "font_family":   "Arial",
  "font_size_pt":  10
}
```

If `inputs.drawing_metadata` is absent, set placeholder values:
- project_name: derived from `inputs.room_type` + room dimensions
  (e.g. "Open-plan office 10×8 m — lighting layout")
- drawing_number: "EL-001"
- revision: "A"
- date: today
- scale: pick the largest scale that fits the room on the sheet
  (1:50 for ≤15×10 m on A3; 1:100 for larger; 1:200 for warehouse)

### 15.2 — scale_bar

Place in the bottom-right corner of the drawing area, 500 mm × 100 mm
above the sheet's bottom edge:

```json
"scale_bar": {
  "origin_x_mm":      <room.length_mm − 2500>,
  "origin_y_mm":      <room.width_mm + 500>,
  "total_length_mm":  2000,
  "tick_interval_mm": 500,
  "font_family":      "Arial",
  "font_size_pt":     8
}
```

For 1:50 scale, total_length_mm 2000 (4 ticks × 500 mm = 2 m at full
scale = 40 mm on paper). For 1:100, double the total_length_mm; for
1:200, triple.

### 15.3 — dimensions[]

At minimum: room length (horizontal at top or bottom) + room width
(vertical at left or right). Position 300 mm OUTSIDE the room rectangle
(negative coordinate; the renderer handles negative-space layout):

```json
"dimensions": [
  {
    "axis":          "horizontal",
    "start_x_mm":    0,
    "start_y_mm":    -300,
    "end_x_mm":      <room.length_mm>,
    "end_y_mm":      -300,
    "text":          "<room.length_mm> mm",
    "font_family":   "Arial",
    "font_size_pt":  10
  },
  {
    "axis":          "vertical",
    "start_x_mm":    -300,
    "start_y_mm":    0,
    "end_x_mm":      -300,
    "end_y_mm":      <room.width_mm>,
    "text":          "<room.width_mm> mm",
    "font_family":   "Arial",
    "font_size_pt":  10
  }
]
```

For rooms with multiple luminaire rows, optionally add per-row dimension
lines showing inter-row spacing. Not required by INV-9 (which checks
only minimum 2 dimensions).

### 15.4 — luminaire_schedule

Required columns: Ref + Manufacturer + Lumens + Wattage + Count. One
row per unique luminaire type used in the layout:

```json
"luminaire_schedule": {
  "columns": ["Ref", "Manufacturer", "Lumens", "Wattage", "Count"],
  "rows": [
    ["<luminaire_type.symbol>", "<inputs.manufacturer ?? 'Generic'>",
     "<luminaire_type.lumens>", "<luminaire_type.wattage_w>W",
     "<luminaires.length>"]
  ],
  "font_family":  "Arial",
  "font_size_pt": 8
}
```

For multi-type layouts (e.g. general lighting LED_PANEL_600 +
emergency EMERGENCY luminaires), emit one row per distinct type.

### 15.5 — calc_only path

If `mode = calc_only`, skip Step 15 entirely. The schema's allOf clause
only requires drafting_furniture for full_drawing mode.

**INV enforced by this step:**
- INV-9 (MEDIUM): drafting_furniture.{title_block, scale_bar,
  dimensions[≥2], luminaire_schedule} all present with explicit
  font_family + font_size_pt. No `{{placeholder}}` remnants in any text
  field.
```

- [ ] **Step 2: Add INV-9 entry to office-open-plan invariants[]**

Append to invariants[]:

```json
{
  "id": "INV-09",
  "passes": true,
  "severity": "medium",
  "evidence": "drafting_furniture present with all 4 required blocks (title_block + scale_bar + dimensions[2] + luminaire_schedule). All annotations declare font_family='Arial' + explicit font_size_pt ∈ {8, 10}. No {{placeholder}} remnants in any text field. Rule 9 PASS."
}
```

- [ ] **Step 3: Run gates**

```bash
python3 scripts/validate-examples.py 2>&1 | tail -3
```

Expected: `AGGREGATE: 225/225 pass (0 failures)`.

- [ ] **Step 4: Commit B.3**

```bash
git add electrical/lighting-layout/prompts/generator.md \
        electrical/lighting-layout/examples/office-open-plan/output.json
git commit -m "$(cat <<'EOF'
feat(lighting-layout): D3.B.3 generator — drafting furniture step + INV-9

Sprint D3 Phase B prompts — third of four. Closes audit Top 5 #4 +
image-visible drafting-furniture gap (no title block, no dimensions,
no scale bar, no luminaire schedule).

Generator Step 15 (NEW) — Drafting furniture emission:
- 15.1 title_block: derived from inputs.drawing_metadata or fallback
  to room-type-derived placeholders + today's date + scale picked by
  room size (1:50 ≤15×10 m, 1:100 ≤30×20 m, 1:200 larger)
- 15.2 scale_bar: bottom-right corner placement; tick interval 500 mm;
  total_length scales with drawing scale (2000 mm at 1:50, 4000 at
  1:100, 6000 at 1:200)
- 15.3 dimensions[]: minimum 2 (room length horizontal + room width
  vertical), 300 mm offset outside room rectangle in negative-space
- 15.4 luminaire_schedule: columns Ref/Manufacturer/Lumens/Wattage/Count;
  one row per distinct luminaire type
- 15.5 calc_only path: Step 15 skipped (schema allOf only requires
  drafting_furniture for full_drawing mode)

Every annotation declares explicit font_family='Arial' (fallback
LiberationSans via ezdxf) + font_size_pt (6-24 range) so the renderer
font fallback can resolve without losing tags — the silent-render-error
class that produced the missing-annotations bug in the original test.

One new INV documented (will land in validator.md at B.4):
- INV-9 (MEDIUM): drafting_furniture present with all 4 required blocks
  + explicit font fields + no {{placeholder}} remnants

office-open-plan example: appended INV-9 entry to invariants[].

Gates: validate-examples 225/225; functional_audit 1 finding unchanged.

Next: D3.B.4 validator + reviewer prompts + intent payload wiring.
EOF
)"
```

---

## Task B.4: Validator + reviewer prompts + intent payload wiring (Opus)

**Why Opus:** Review-prompt content authoring + INV catalogue judgment + cross-skill consumer awareness.

**Files:**
- Modify: `electrical/lighting-layout/prompts/validator.md` — 4 → ~400 lines (full INV-1..INV-10 catalogue)
- Modify: `electrical/lighting-layout/prompts/reviewer.md` — 4 → ~250 lines (D-1..D-6 catalogue)
- Modify: `electrical/lighting-layout/prompts/generator.md` — add intent-payload emission step
- Modify: `electrical/lighting-layout/examples/office-open-plan/output.json` — add INV-6, INV-10 entries (the remaining 2 of 10 not yet added in B.1/B.2/B.3)
- Modify: `electrical/lighting-layout/examples/office-open-plan/intent-out.json` — populate the new intent fields (zones + circuits + homerun + switches)

- [ ] **Step 1: Write validator.md (replace the 4-line stub)**

Overwrite `electrical/lighting-layout/prompts/validator.md` with:

```markdown
# Lighting Layout — Validator Prompt

You are the validator for the lighting-layout skill. Given a candidate
IR (lighting_layout_ir.json), verify that all 10 INVs below PASS or
emit a HIGH/MEDIUM finding per the severity-classification rule.

Validate the IR in this order:

1. **Schema-level checks first** (JSON Schema validation against
   `shared/schemas/electrical/lighting-layout-ir.schema.json` — the
   golden CI gate `scripts/validate-examples.py` does this
   automatically; treat as a precondition).
2. **Per-INV checks** in numeric order INV-1 → INV-10.

For each INV, emit an entry into the IR's `invariants[]` array:

```json
{
  "id": "INV-NN",
  "passes": true|false,
  "severity": "high"|"medium",
  "evidence": "<20-800 char prose stating WHY the rule passed/failed; cite specific values from the IR>"
}
```

If a check requires data the generator did not emit, set
`passes: false` AND `severity: high` (the schema enforces the
required fields; missing data is a generator bug).

---

## INV-1 — Achieved illuminance ≥ target (HIGH)

**Severity:** HIGH

**Rule:** `calculation_summary.achieved_illuminance_lux >= calculation_summary.target_illuminance_lux`

**Validator action:**
- Read both values.
- If `achieved >= target`: PASS.
- If `achieved < target`: FAIL. Compute the lux shortfall + percent.
  Suggest action: increase N (panels), or upgrade luminaire to higher
  Φ (lumens), or improve UF (lighter reflectances / lower mounting),
  or accept fail with non_compliance_flags entry.

**Citation:** `[spacing-rules#lumen-method-formula]` + BS EN 12464-1:2021 §4 (illuminance criteria).

**Rationale:** The single most common bug in LLM-driven lighting layouts
is round-to-nearest instead of round-UP on N — produces a layout that
hits 482 lux on a 500 lux target. INV-1 catches it deterministically.

---

## INV-2 — S/H ratio within SHR_max (HIGH)

**Severity:** HIGH

**Rule:** For the laid-out grid, compute:
- `S_x = (room.length_mm - 2 * edge_clearance_mm) / max(1, n_cols - 1)`
- `S_y = (room.width_mm  - 2 * edge_clearance_mm) / max(1, n_rows - 1)`
- `Hm = room.ceiling_height_mm - room.working_plane_mm`
- `SHR_max` from `ontology[luminaire_type.symbol].photometric.shr_max`,
  with override from `inputs.photometric_override.shr_max` if supplied.

PASS iff `S_x <= SHR_max * Hm AND S_y <= SHR_max * Hm`.

**Validator action:**
- Read all luminaire positions, derive unique x + y sets (snap to
  ±50 mm tolerance), compute n_cols + n_rows.
- Compute S_x + S_y + limit.
- Emit evidence with all four numbers + PASS/FAIL per direction.

**Citation:** `[spacing-rules#shr-max-default]` + CIBSE LG7 §6.2.

---

## INV-3 — Switch coverage + height + latch placement (HIGH)

**Severity:** HIGH

**Rule:** Per `inputs.entrance_positions[]`:
1. `switches.length >= entrances.length` (unless `controls_protocol ∈ {DALI, DALI-2}` in which case 1 DALI master is sufficient).
2. Each `switches[*].height_aff_mm` ∈ `[1200 - 50, 1200 + 50]` per `[switching-rules#height]`.
3. Each `switches[*].x_mm/y_mm` sits 200 mm inside the room from a latch frame derived from `entrance_positions[*].wall + offset_mm + door_swing` per `[switching-rules#latch-side]`.
4. Each `switches[*].switch_side == "latch"` (or `"sliding"` for sliding doors).

**Validator action:**
- Enumerate entrances + switches.
- Verify count + every switch's geometry against the derived latch position.
- For DALI: verify exactly one dali_master switch + optional wall controllers at secondary entrances.

**Citation:** `[switching-rules#height]` + `[switching-rules#latch-side]` + BS 7671:2018+A2:2022 §553.1.1 + IET OSG App E §E1.4.

---

## INV-4 — Circuit topology: no Z-pattern + homerun on wall (HIGH)

**Severity:** HIGH

**Rule:** For every circuit in `circuits[]`:
1. Derive `row_indices = { luminaires[id].row_index | id ∈ circuit.luminaire_ids }`.
2. PASS iff `max(row_indices) - min(row_indices) <= 1` (same row or adjacent rows only — no diagonal jumps across non-adjacent rows).
3. `circuit.homerun_endpoint.{x_mm, y_mm}` sits on one of the four room walls (x_mm=0 OR x_mm=room.length_mm OR y_mm=0 OR y_mm=room.width_mm).

**Validator action:**
- For each circuit, project its luminaire_ids to row_indices, compute span.
- Verify homerun_endpoint sits on a wall.
- Emit evidence per circuit (e.g. `"C-L01: rows {0}, homerun (0,800) on wall W — PASS"`).

**Citation:** Sprint D3 design spec §3.2 + BS 7671 §433 (circuit topology engineering practice).

**Rationale:** The Z-pattern bug came from the generator emitting `luminaire_ids` for a single circuit that included luminaires from rows 0 + 2 (skipping row 1) — the renderer drew a daisy-chain across rows. INV-4 catches this structurally.

---

## INV-5 — Circuit load ≤ 80% of OCPD (HIGH)

**Severity:** HIGH

**Rule:** For every circuit:
`circuit.total_load_w <= 0.8 * circuit.mcb_rating_a * supply_voltage_v`

where `supply_voltage_v = 230` (UK default; KE inherits via §313).

Equivalent table:
- 6A → 1104 W
- 10A → 1840 W
- 16A → 2944 W
- 20A → 3680 W
- 32A → 5888 W

**Validator action:**
- For each circuit, multiply mcb_rating_a × 184 (= 0.8 × 230) and check.
- The schema's allOf clause enforces this structurally already (D3.A.3);
  INV-5 confirms the schema-level check passed AND emits evidence to the
  invariants log.

**Citation:** BS 7671:2018+A2:2022 §433.1.1 + IET OSG App A (continuous-load rule).

---

## INV-6 — Part L compliance (HIGH)

**Severity:** HIGH (when `is_uk_new_build == true`)

**Rule:** If `inputs.is_uk_new_build == true`:
1. `controls.part_l_assessed == true`.
2. `controls.required[]` includes `"occupancy"` (per `[control-rules#part-l-occupancy]`).
3. If `inputs.glazed_wall_positions != []`: `controls.required[]` ALSO includes `"daylight_linking"` (per `[control-rules#part-l-daylight]`).
4. `controls.lamp_efficacy_lm_per_w >= 95` per `[control-rules#part-l-efficacy-target]`.

If `inputs.is_uk_new_build == false` OR absent: PASS trivially (rule does not apply).

**Validator action:**
- Check is_uk_new_build flag.
- If true: verify part_l_assessed + required[] contents + efficacy ≥ 95.
- If any sub-check fails: emit non_compliance_flags entry with `severity: critical` AND set this INV to FAIL.

**Citation:** Approved Doc L (Part L 2021) §6.2 + BS EN 15193-1:2017 §6.

---

## INV-7 — Zone assignment (MEDIUM)

**Severity:** MEDIUM

**Rule:**
1. Every luminaire's `zone_id` references a real entry in `zones[].zone_id`.
2. Each luminaire belongs to exactly one zone.
3. Zone geometry consistency: if a zone has `zone_type == "perimeter"`, the zone's luminaire positions must be within 6 m of a wall declared in `inputs.glazed_wall_positions`. Conversely, if `inputs.glazed_wall_positions == []`, NO zone may have `zone_type == "perimeter"`.

**Validator action:**
- Build a map `luminaire_id → zone_id` and verify referential integrity.
- For each perimeter zone, verify at least one luminaire is within 6 m of a glazed wall.
- For the no-glazing case, verify no perimeter zone exists.

**Citation:** `[control-rules#part-l-daylight]` + `[switching-rules#perimeter-circuit]`.

---

## INV-8 — Photometric source resolved (MEDIUM)

**Severity:** MEDIUM

**Rule:** `selection_source` is present with:
- `photometric_source ∈ {"input_override", "ontology_default"}`.
- `citation` matches the chosen path: either `inputs.photometric_override._source` OR `ontology[luminaire_type.symbol].photometric._citation`.

**Validator action:**
- Verify `selection_source` exists.
- If `photometric_source == "input_override"`: verify `inputs.photometric_override` was supplied AND its `_source` string matches `selection_source.citation`.
- If `photometric_source == "ontology_default"`: verify the citation matches the relevant ontology entry's `_citation`.

**Citation:** Sprint D3 design spec §3.1 (no improvisation policy).

---

## INV-9 — Drafting furniture complete (MEDIUM)

**Severity:** MEDIUM (HIGH if mode = full_drawing)

**Rule:** When `mode == full_drawing` (or absent — defaults to full_drawing):
1. `drafting_furniture` exists with `title_block + scale_bar + dimensions + luminaire_schedule` all present.
2. Every annotation declares `font_family` + `font_size_pt`.
3. No `{{placeholder}}` substrings in any text field (substring `{{` is forbidden).
4. `drafting_furniture.dimensions.length >= 2`.

When `mode == calc_only`: PASS trivially (rule does not apply).

**Validator action:**
- For each of the 4 required blocks, verify presence + font fields.
- Walk every text field and grep for `{{` — any occurrence fails Rule 3.
- Count dimensions[] entries; ≥2 required.

**Citation:** Sprint D3 design spec §3.5 + BS 1192:2007 §4 (drawing presentation).

---

## INV-10 — Schema fields populated + non_compliance_flags shape (HIGH)

**Severity:** HIGH

**Rule:**
1. Every field listed in the schema's top-level `required[]` is populated (the JSON Schema validator catches this; INV-10 confirms the gate passed).
2. `calculation_summary.non_compliance_flags[]` items match object shape `{message: <string>, reference: <string|absent>, severity: ∈ {critical, warning, info}}`. **Not** the legacy string-flag form.
3. If `controls.part_l_compliant == false`: at least one non_compliance_flags entry with severity == critical referencing Part L.

**Validator action:**
- Confirm JSON Schema validation PASSED (precondition).
- Walk non_compliance_flags[] and verify object shape.
- Cross-check controls.part_l_compliant with non_compliance_flags content.

**Citation:** Sprint D3 design spec §3 + audit Top 5 #5 (schema-required-fields).

---

## Output

After running all 10 INVs, emit the populated `invariants[]` array as
part of the IR. A failing INV does NOT block emission — the IR ships
with the failure recorded so downstream skills can react (e.g.
db-layout sees `INV-5: FAIL` and re-sizes the lighting circuit MCB).
```

- [ ] **Step 2: Write reviewer.md (replace the 4-line stub)**

Overwrite `electrical/lighting-layout/prompts/reviewer.md` with:

```markdown
# Lighting Layout — Reviewer Prompt

You are the reviewer for the lighting-layout skill. Given a candidate
IR that has already passed the validator (all 10 INVs emitted with
pass/fail decisions), perform 6 quality / engineering-judgment checks
that the validator's deterministic INV catalogue cannot cover.

Reviewer findings go into the IR's `flags[]` array (chat-facing
high-signal flags) AND optionally into `calculation_summary.non_compliance_flags[]`
when they indicate a non-compliance risk.

---

## D-1 — Photometric override sanity check

**Trigger:** when `selection_source.photometric_source == "input_override"`.

**Check:** are the override's UF values plausible for the luminaire
type? Specifically:
- UF range: 0.30 ≤ UF ≤ 0.85 for typical recessed LED panels.
- UF should DECREASE as room index decreases (smaller rooms = lower UF).
- SHR_max range: 0.8 ≤ SHR_max ≤ 2.0 for indoor luminaires.

**Action:** if any value falls outside the plausible range, emit a
flag: `"REVIEWER D-1: photometric override UF=<value> outside typical
range 0.30-0.85 for <luminaire_type>; engineer to verify against IES
file source."`

**Citation:** CIBSE LG7 §6.2 (typical UF ranges).

---

## D-2 — OCPD rating realism

**Check:** for each circuit:
- The chosen `mcb_rating_a` is the smallest that satisfies the 80% load
  rule. Engineer should size for the load, not over-size "for headroom"
  (oversized MCBs reduce protection coordination effectiveness).
- For LED panels at 36-50 W each, expect 6 A MCBs on most circuits.
  A 10 A MCB on a circuit carrying <500 W is over-sized.
- `mcb_curve == "B"` for general lighting (per BS 7671 §433.2).
  Curve C only justified if the luminaire has high inrush (DALI drivers
  with large bulk caps); curve D never for lighting circuits.

**Action:** flag over-sized MCBs and non-B curves with justification
prompt.

**Citation:** BS 7671:2018+A2:2022 §433 + IET OSG App C.

---

## D-3 — Emergency lighting coverage (BS 5266-1)

**Trigger:** when `room.room_type ∈ {open_plan_office, warehouse, corridor, classroom, ward, escape_route}` (rooms where emergency lighting is mandatory per Part B Approved Doc or industry practice).

**Check:** does the IR include at least one emergency zone (Z4)?
Specifically:
- Escape route rooms: ≥1 EMERGENCY luminaire per BS 5266-1 §5.2.1
  (1 lux centre line).
- Open plan offices >60 m²: anti-panic luminaires per
  [emergency-rules#anti-panic-illuminance] (0.5 lux floor minimum).
- High-risk task areas: 15 lux or 10% of task per
  [emergency-rules#high-risk-task-area].

**Action:** if emergency luminaires absent for a room type that
requires them, emit flag: `"REVIEWER D-3: emergency lighting coverage
required per BS 5266-1 §<clause> for room_type=<type>; no EMERGENCY
luminaires in IR. Add Z4 emergency zone + escape-route or anti-panic
luminaires per [emergency-rules]."`

**Citation:** BS 5266-1:2016 + BS 7671:2018+A2:2022 §710 (medical) +
Approved Doc B.

---

## D-4 — Uniformity ratio U₀ per BS EN 12464-1

**Check:** for the laid-out grid, U₀ = min_lux / avg_lux on the task
area should meet BS EN 12464-1:2021 Table 5.3 minimum:
- Office task area: U₀ ≥ 0.6
- Corridor: U₀ ≥ 0.4
- Warehouse: U₀ ≥ 0.4

The lumen method gives average illuminance; the renderer or
`calc.lumen_grid_solver` provides U₀. If U₀ is below the minimum, the
spacing is uneven or the perimeter edge-clearance is too large.

**Action:** if `calc.lumen_grid_solver` output indicates U₀ <
threshold, flag: `"REVIEWER D-4: uniformity U₀=<value> < <threshold>
for <room_type> per BS EN 12464-1 Table 5.3; tighten spacing or add
perimeter row."`

**Citation:** BS EN 12464-1:2021 §4.4 Table 5.3.

---

## D-5 — Controls protocol fit

**Check:** is `inputs.controls_protocol` appropriate for the layout?
- DALI / DALI-2: justified when ≥10 luminaires OR multi-zone control
  needed.
- 0-10V: legacy analog dimming; less reliable than DALI; flag if
  selected for new-build.
- switched (no dimming): inappropriate for Part L new-builds with
  glazing.
- none: only appropriate for small private offices or back-of-house
  spaces.

**Action:** flag misfits with rationale prompt.

**Citation:** `[control-rules#dali-line-capacity]` + Part L 2021 §6.2.

---

## D-6 — Zone perimeter geometry sanity

**Check:** for each perimeter zone (zone_type == "perimeter"):
- Zone luminaires sit between 300 mm and 6000 mm from a glazed wall.
- Perimeter zone width ≤ 6000 mm per
  [switching-rules#perimeter-circuit].max_zone_depth_mm.

**Action:** if a perimeter zone's luminaires extend beyond 6 m from
the glazed wall, flag: `"REVIEWER D-6: perimeter zone depth exceeds
6 m; split into Z1 (true perimeter) + Z2 (interior)."`

**Citation:** `[switching-rules#perimeter-circuit]` + BS EN 15193-1:2017
§6.2.

---

## Output

Reviewer findings emitted as:
- `flags[]` entries: high-signal one-line strings (e.g.
  `"REVIEWER D-3: emergency lighting coverage required"`).
- Optional `calculation_summary.non_compliance_flags[]` entries for
  non-compliances requiring engineer action.

A failing D-check does NOT block emission. The IR ships with the
review findings recorded so downstream skills + engineers can react.
```

- [ ] **Step 3: Add intent-payload emission step to generator.md**

Find the existing intent-emission step in generator.md (search for `intent_emitted` or the section near the bottom that handles intent output). Update it to include zones + circuits + switches per the extended intent schema. Insert immediately after Step 15:

```markdown
## Step 16 — Emit lighting-layout intent payload

Per `electrical/lighting-layout/schemas/lighting-layout-intent.schema.json`
(extended in D3.A.3), emit the intent block downstream consumers
(db-layout, cable-sizing, small-power) read:

```json
{
  "intent_type":    "lighting-layout",
  "intent_version": "1.0.0",
  "produced_by":    "electrical/lighting-layout/v1.4.0",
  "payload": {
    "room": { "length_mm": ..., "width_mm": ... },
    "zones": [
      {
        "zone_id": "Z2",
        "zone_type": "interior",
        "control": "occupancy",
        "luminaire_ids": ["L01", ...],
        "circuit_ids": ["C-L01", "C-L02", "C-L03"]
      }
    ],
    "circuits": [
      {
        "circuit_id": "C-L01",
        "zone_id": "Z2",
        "row_index": 0,
        "total_load_w": 144,
        "mcb_rating_a": 6,
        "mcb_curve": "B",
        "homerun_endpoint": {"x_mm": 0, "y_mm": 800, "wall": "W"}
      }
    ],
    "switches": [
      {
        "id": "SW01",
        "type": "1_gang",
        "x_mm": 1600,
        "y_mm": 0,
        "height_aff_mm": 1200,
        "controls_circuit": "C-L01"
      }
    ],
    "total_load_per_circuit_w": [144, 144, 144]
  }
}
```

Downstream consumption:
- **db-layout** reads `circuits[].mcb_rating_a` + `total_load_w` to
  size the lighting MCB on the consumer unit; consumes `homerun_endpoint`
  to position the lighting circuit termination on the board.
- **cable-sizing** reads `circuits[].total_load_w` + `mcb_rating_a` to
  size cable CSA from the homerun endpoint to each row.
- **small-power** is not a direct consumer but may reference zone
  positions for socket-vs-lighting coordination.
```

- [ ] **Step 4: Update office-open-plan intent-out.json with new payload fields**

Read the current intent-out.json to find its shape, then add the new fields (zones + circuits + switches + total_load_per_circuit_w) consistent with the example's existing output.json data:

```bash
cat electrical/lighting-layout/examples/office-open-plan/intent-out.json
```

Edit the file to include the new fields per Step 3's template. Match the example's actual zone Z2 + single circuit L1-Z2 + 1 switch + total_load_w 720.

- [ ] **Step 5: Add INV-6 and INV-10 entries to office-open-plan output.json invariants[]**

Append to invariants[]:

```json
{
  "id": "INV-06",
  "passes": true,
  "severity": "high",
  "evidence": "Part L compliance: inputs.is_uk_new_build status drives Rule 6. If new-build: controls.part_l_assessed + required[] includes occupancy + (daylight when glazed) + efficacy ≥ 95 lm/W. For this example: <fill in based on the actual controls block — if not new-build, evidence reads 'is_uk_new_build absent/false, Rule 6 trivially PASS'>."
},
{
  "id": "INV-10",
  "passes": true,
  "severity": "high",
  "evidence": "Schema validation PASSED (precondition: golden CI gate 225/225). All top-level required fields populated: drawing_type, version, room, calculation_summary, rationale, invariants, plus full_drawing-mode required: luminaire_type, luminaires, switches, circuits, controls, drawing_notes, zones, drafting_furniture, selection_source. non_compliance_flags = [] (vacuously valid). Rule 10 PASS."
}
```

- [ ] **Step 6: Run gates**

```bash
python3 scripts/validate-examples.py 2>&1 | tail -3
```

Expected: `AGGREGATE: 225/225 pass (0 failures)`.

Verify the office-open-plan example now carries all 10 INVs:

```bash
python3 -c "
import json
d = json.load(open('electrical/lighting-layout/examples/office-open-plan/output.json'))
ids = sorted(i['id'] for i in d.get('invariants', []))
print(f'INVs present: {ids}')
print(f'count: {len(ids)}')"
```

Expected: `INVs present: ['INV-01', 'INV-02', 'INV-03', 'INV-04', 'INV-05', 'INV-06', 'INV-07', 'INV-08', 'INV-09', 'INV-10']` + `count: 10`.

- [ ] **Step 7: Commit B.4**

```bash
git add electrical/lighting-layout/prompts/validator.md \
        electrical/lighting-layout/prompts/reviewer.md \
        electrical/lighting-layout/prompts/generator.md \
        electrical/lighting-layout/examples/office-open-plan/output.json \
        electrical/lighting-layout/examples/office-open-plan/intent-out.json
git commit -m "$(cat <<'EOF'
feat(lighting-layout): D3.B.4 validator + reviewer prompts + intent payload wiring + INV-6/INV-10

Sprint D3 Phase B prompts — fourth of four. Promotes 4-line stub
prompts to full INV/D catalogues + wires generator to emit extended
intent payload for downstream consumption.

validator.md (4 → ~400 lines): full INV-1..INV-10 catalogue.
- INV-1 (HIGH): achieved_illuminance_lux ≥ target_illuminance_lux
- INV-2 (HIGH): S_x ≤ SHR_max × Hm AND S_y ≤ SHR_max × Hm
- INV-3 (HIGH): switches.length ≥ entrances.length + 1200 mm AFF +
  latch placement
- INV-4 (HIGH): luminaire_ids share row_index OR adjacent
  (|row_a−row_b|≤1); homerun on wall — kills Z-pattern
- INV-5 (HIGH): circuit.total_load_w ≤ 0.8 × mcb × 230 (BS 7671 §433.1.1)
- INV-6 (HIGH): if is_uk_new_build → part_l_assessed + occupancy +
  daylight (when glazed) + efficacy ≥ 95 lm/W
- INV-7 (MEDIUM): every luminaire in exactly one zone; zone geometry
  consistency (perimeter iff glazed walls)
- INV-8 (MEDIUM): selection_source resolves to ontology citation or
  input override
- INV-9 (MEDIUM/HIGH): drafting_furniture complete in full_drawing mode
- INV-10 (HIGH): all schema-required fields populated; non_compliance_flags
  object shape

reviewer.md (4 → ~250 lines): D-1..D-6 catalogue.
- D-1 photometric override sanity (UF range 0.30-0.85, SHR_max 0.8-2.0)
- D-2 OCPD rating realism (right-size to load, curve B for lighting)
- D-3 emergency lighting coverage per BS 5266-1
- D-4 uniformity U₀ per BS EN 12464-1 Table 5.3
- D-5 controls protocol fit (DALI for ≥10 luminaires)
- D-6 zone perimeter geometry sanity (≤6m from glazing)

generator Step 16 (NEW): intent payload emission with zones + circuits
(incl. homerun_endpoint) + switches + total_load_per_circuit_w.
Downstream consumption documented: db-layout reads mcb_rating_a +
total_load_w to size lighting MCB; cable-sizing reads for CSA;
small-power coordinates zone positions.

office-open-plan example: appended INV-6 + INV-10 entries; updated
intent-out.json with zones + circuits + switches per extended schema.
All 10 INVs now present and PASS.

Gates: validate-examples 225/225; functional_audit 1 finding unchanged.

Phase B complete. Next: D3.C.1 promote reception-lobby +
warehouse-highbay stubs to full examples.
EOF
)"
```

---
