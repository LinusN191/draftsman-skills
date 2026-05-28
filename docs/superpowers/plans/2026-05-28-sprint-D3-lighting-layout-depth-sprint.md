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
