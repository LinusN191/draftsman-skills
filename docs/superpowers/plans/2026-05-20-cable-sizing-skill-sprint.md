# Cable-Sizing Skill v1.0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship `electrical/cable-sizing` v1.0.0 beta — a calc skill that produces per-circuit cable selection (phase csa + CPC csa + insulation + installation method + parallel count) with binding constraint named per node, consumed by 4 downstream skills (cable-schedule + riser + cable-containment + small-power v1.1).

**Architecture:** Project-scoped cascade IR mirroring `electrical/fault-level`. Consumes `db-layout-rollup` + `fault-level` intents (multi-skill consumption, matches SLD v1.4 pattern); falls back to engineer-declared inputs. Walk-the-ladder CSA selection with `binding_constraint` + `walk_up_trail` per node. WI3 tool-call deferral on `calc.cable_ampacity` / `calc.voltage_drop` / `calc.cpc_adiabatic` (all 3 calc contracts already on disk — REUSED not created). Emits slim `cable-sizing` intent including 2 new Zs-resolution helper fields (`r1_plus_r2_milliohm_per_m_at_operating_temp` + `reactance_milliohm_per_m`) per 2026-05-20 refresh.

**Tech Stack:** JSON Schema Draft-07 + YAML 1.2 + Markdown. No new code — all artefacts are content (schemas, prompts, rules, constraints, validation YAMLs, evals, examples).

**Specs referenced:**
- Base: `docs/superpowers/specs/2026-05-16-cable-sizing-skill-design.md` (commit c47a077, 540 lines)
- Refresh: `docs/superpowers/specs/2026-05-20-cable-sizing-skill-design-refresh.md` (commit 7c67225, 175 lines)

---

## Reference table — pre-flight verifications

| Verification | Result |
|---|---|
| All 22 manifest standards paths exist on disk | PASS (verified pre-plan) |
| All 3 calc contracts exist on disk | PASS (`cable-ampacity` + `voltage-drop` + `cpc-adiabatic`) |
| 3 calc contracts currently MISSING `_consuming_skills` field | TRUE — Task 3 adds it |
| Pattern parent `fault-level` structure validated | PASS (IR schema = 159 lines, 5 examples) |
| Small-power v1.0 KE example exists for citation form reference | PASS (`electrical/small-power/examples/ke-nairobi-small-office/`) |
| Fault-level + db-layout-rollup intent schemas readable for consumed_intents typing | PASS (verified pre-plan) |
| Net file count | ~54 (50 base spec + 4 KE example files per refresh) |

---

## Phase A — Infrastructure (Tasks 1-3)

### Task 1: Skill skeleton (manifest + inputs + README + CHANGELOG)

**Model:** Sonnet (mechanical — follows fault-level v1.1 template).

**Files:**
- Create: `electrical/cable-sizing/skill.manifest.json`
- Create: `electrical/cable-sizing/inputs.json`
- Create: `electrical/cable-sizing/README.md`
- Create: `electrical/cable-sizing/CHANGELOG.md`

- [ ] **Step 1: Verify directory state**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
ls electrical/cable-sizing/ 2>/dev/null || mkdir -p electrical/cable-sizing
```

- [ ] **Step 2: Read fault-level manifest as structural reference**

```bash
cat electrical/fault-level/skill.manifest.json | head -40
```

- [ ] **Step 3: Write skill.manifest.json**

```json
{
  "skill": "cable-sizing",
  "version": "1.0.0",
  "discipline": "electrical",
  "subdiscipline": "circuit-sizing",
  "description": "Per-circuit cable selection (phase + CPC csa + insulation + installation method + parallel count) for every cable run in a project's distribution cascade per BS 7671:2018+A2:2022 App 4 + App 12 / IEC 60364-5-52 / NEC 2023 Chapter 9. Walk-the-ladder CSA selection with binding_constraint named per node. Consumes db-layout-rollup + fault-level intents; produces cable-sizing intent for cable-schedule + riser + cable-containment + small-power v1.1 consumption.",
  "status": "beta",
  "licence": "MIT",
  "inputs_path": "inputs.json",
  "inputs": [
    "jurisdiction",
    "circuits-from-intent-or-declared",
    "route-data-per-segment",
    "ambient-overlay",
    "grouping-per-segment",
    "harmonic-content-per-circuit",
    "vd-target-overrides",
    "cable-type-preferences"
  ],
  "outputs": ["cable-sizing-ir"],
  "output_schema": "electrical/cable-sizing/schemas/cable-sizing-ir.schema.json",
  "produces_intent": "cable-sizing",
  "produces_intent_schema": "electrical/cable-sizing/schemas/cable-sizing-intent.schema.json",
  "consumes_intents": ["db-layout-rollup", "fault-level"],
  "standards": [
    "shared/standards/electrical/BS7671/appendix4-cable-ratings.json",
    "shared/standards/electrical/BS7671/appendix4-cable-ratings-aluminium.json",
    "shared/standards/electrical/BS7671/appendix4-correction-factors.json",
    "shared/standards/electrical/BS7671/appendix12-voltage-drop.json",
    "shared/standards/electrical/BS7671/reg433-overcurrent-protection.json",
    "shared/standards/electrical/BS7671/reg434-fault-current.json",
    "shared/standards/electrical/BS7671/reg521-installation-methods.json",
    "shared/standards/electrical/BS7671/cable-types-fire-rated.json",
    "shared/standards/electrical/BS7671/cable-current-ratings.json",
    "shared/standards/electrical/IEC60364/part5-52-cable-ratings-copper.json",
    "shared/standards/electrical/IEC60364/part5-52-cable-ratings-aluminium.json",
    "shared/standards/electrical/IEC60364/part5-52-correction-factors.json",
    "shared/standards/electrical/IEC60364/part5-52-voltage-drop.json",
    "shared/standards/electrical/IEC60364/part5-52-installation-methods.json",
    "shared/standards/electrical/IEC60364/part4-43-overcurrent.json",
    "shared/standards/electrical/IEC60364/part5-54-earthing.json",
    "shared/standards/electrical/NFPA70/chapter9-tables.json",
    "shared/standards/electrical/NFPA70/art310-conductor-ampacity.json",
    "shared/standards/electrical/NFPA70/art240-overcurrent.json",
    "shared/standards/electrical/NFPA70/art215-feeders.json",
    "shared/standards/electrical/NFPA70/art210-branch-circuits.json",
    "shared/standards/electrical/NFPA70/ampacity-correction-factors.json"
  ],
  "ontology": [
    "electrical/cable-sizing/ontology/cable-types.json",
    "electrical/cable-sizing/ontology/installation-methods.json"
  ],
  "calculations": [
    "shared/calculations/electrical/cable-ampacity.json",
    "shared/calculations/electrical/voltage-drop.json",
    "shared/calculations/electrical/cpc-adiabatic.json"
  ]
}
```

- [ ] **Step 4: Write inputs.json**

```json
{
  "skill": "cable-sizing",
  "input_groups": [
    {
      "group": "jurisdiction",
      "fields": [
        {"name": "jurisdiction", "type": "enum", "values": ["GB", "EU", "INT", "KE", "US"], "required": true}
      ]
    },
    {
      "group": "consumed-intents",
      "fields": [
        {"name": "db_layout_rollup_intent_path", "type": "string", "required": false,
         "description": "Path to upstream db-layout-rollup intent JSON. When present, used for cascade topology + Ib + In + load_type + selectivity status per circuit. When absent, engineer must declare all circuits inline."},
        {"name": "fault_level_intent_path", "type": "string", "required": false,
         "description": "Path to upstream fault-level intent JSON. When present, used for per-node Ik\"max + Ik\"min + X/R + Z. When absent, engineer must declare per-node Ifault."}
      ]
    },
    {
      "group": "engineer-declared-fallbacks",
      "fields": [
        {"name": "circuits_declared", "type": "array", "required": false,
         "description": "Used only when db-layout-rollup intent is absent. Array of {node_id, parent_node_id, designation, load: {ib_a, in_a, phases, load_type, pf}}."},
        {"name": "t_clear_declared_per_node", "type": "object", "required": false,
         "description": "Engineer-declared OCPD clearing times per node when not provided by db-layout-rollup selectivity output. Keys = node_id, values = seconds."}
      ]
    },
    {
      "group": "route-data-per-segment",
      "fields": [
        {"name": "length_m", "type": "number", "required": true, "description": "Cable run length per cascade node (m)."},
        {"name": "installation_method", "type": "enum",
         "values": ["A1","A2","B1","B2","C","D1","D2","E","F","G","nec_conduit","nec_cable_tray","nec_direct_burial","nec_free_air"],
         "required": true},
        {"name": "ambient_c", "type": "integer", "default": 30, "description": "Ambient temperature (°C) at the cable run."},
        {"name": "grouping_count", "type": "integer", "default": 1, "description": "Number of loaded circuits in proximity (Cg derating input)."},
        {"name": "in_thermal_insulation", "type": "boolean", "default": false},
        {"name": "harmonic_content_pct", "type": "number", "default": 0, "description": "Triplen harmonic content as % of fundamental on the neutral conductor; triggers Ch derating when > 15%."},
        {"name": "terminal_temp_rating_c", "type": "integer", "default": 75, "description": "US jurisdiction only — terminal temp per NEC 110.14(C). Caps ampacity column selection."},
        {"name": "cable_type_preference", "type": "enum",
         "values": ["pvc_singles","xlpe","epr","mineral_micc","swa","fp200","cwz","thwn_2","thhn","xhhw_2"],
         "default_by_context": "pvc_singles for domestic; xlpe for commercial feeders"}
      ]
    },
    {
      "group": "design-intent-overrides",
      "fields": [
        {"name": "vd_target_overrides", "type": "object", "required": false,
         "description": "Per-circuit Vd limit override when client spec is tighter than jurisdictional default. Keys = node_id, values = limit %."}
      ]
    }
  ]
}
```

- [ ] **Step 5: Write README.md**

```markdown
# cable-sizing Skill v1.0

Per-circuit cable selection for every cable run in a project's distribution cascade. Walks the standard csa ladder from below, accepts the smallest size that simultaneously satisfies `Iz ≥ In`, cumulative `Vd ≤ limit`, and the CPC adiabatic equation. Records the binding constraint and walk-up trail per node so tender reviewers can verify every selection without rerunning the calc.

## What this skill produces

For a given project cascade + consumed intents + engineer route data, the skill emits:

- **Per-cascade-node selection:** phase_csa + cpc_csa + insulation + cable_type + parallel_count + material
- **Binding constraint name** per node (`iz_vs_in` / `vd_cumulative` / `motor_starting_vd` / `cpc_adiabatic` / `parallel_required` / `harmonic_derating`)
- **Walk-up trail** — every csa tried and the reason it was rejected
- **All 4 engineering checks** — cumulative Vd, motor-starting Vd, parallel cables, harmonic derating
- **Rationale block** — 8-section narrative + chat_summary ≤500 chars

## Architecture: multi-skill consumer

- `consumes_intents: ["db-layout-rollup", "fault-level"]` — pulls topology + Ib + In + load_type from db-layout-rollup; pulls Ik" + X/R + Z from fault-level
- `produces_intent: "cable-sizing"` — consumed by 4 downstream skills (cable-schedule + riser + cable-containment + small-power v1.1)
- Hybrid input mode: when intents are absent, engineer declares circuits + per-node fault data inline
- WI3 tool-call deferral on `calc.cable_ampacity` / `calc.voltage_drop` / `calc.cpc_adiabatic` until runtime ships them

## Jurisdictions supported

- **GB** — BS 7671:2018+A2:2022 App 4 (ampacity) + App 12 (Vd) + Reg 433 + Reg 543
- **KE** — KS 1700:2018 §313 routing to BS 7671:2018+A2:2022 (KE engineering practice)
- **INT/EU** — IEC 60364-5-52 (ampacity + Vd) + Part 5-54 (earthing)
- **US** — NEC 2023 Chapter 9 Table 9 + 310.16 + 240.4(B) + 250.122 + 220.40

## Examples

| Folder | Scenario |
|---|---|
| `examples/uk-domestic-final-circuits/` | UK 230V single-phase domestic, copper PVC, 1.5-10 mm², lighting + power radial + 32A ring. Vd binding on lighting circuits. |
| `examples/ke-nairobi-commercial-with-msb/` | KE 415V TPN KPLC TN-S, 60-200 m² Nairobi commercial office. MSB → sub-DB → final circuits cascade. KS 1700:2018 §313 routing form. |
| `examples/intl-commercial-with-feeders/` | INT 400V TPN: TX → MSB → riser → DB-L1 → final circuits. Cumulative Vd, XLPE feeders, copper. |
| `examples/us-industrial-with-motors/` | US 480V industrial: aluminium feeder + AWG sizing + 500 hp motor with starting-Vd check + parallel cables for 1200A service entrance. |

## Out of scope (v1.0)

- DC circuit sizing (PV strings, EV DCFC, battery interconnects) — future `dc-cable-sizing` sibling
- IEC 60287 thermal modelling beyond standard tables (very large buried cable groups)
- Arc-flash incident-energy boundary marking — `arc-flash` sibling
- Communications / data cables (Cat6, fibre) — different standards family
- Time-graded protection curve coordination — handled by `db-layout` + future `protection-coordination`

See `CHANGELOG.md` for version history and `docs/engineering-philosophy.md` for the walk-the-ladder rationale.
```

- [ ] **Step 6: Write CHANGELOG.md**

```markdown
# Changelog

## [1.0.0] - 2026-05-20

### Added — first ship (beta)

- **Multi-skill consumer**: consumes `db-layout-rollup` + `fault-level` intents (pattern matches SLD v1.4). Falls back to engineer-declared inputs when intents absent.
- **Project-scoped cascade IR**: mirrors `fault-level-ir` structure. Every node carries `node_id`, `parent_node_id`, `node_kind`, route data, selection, and checks.
- **Walk-the-ladder CSA selection**: each node records `binding_constraint` (from 6-token vocabulary) + `walk_up_trail[]` (every csa tried + rejection reason).
- **4 extra engineering checks**: cumulative Vd, motor-starting Vd, parallel cables, harmonic derating.
- **WI3 tool-call deferral**: `tool_call_pending: true` per cascade node until runtime ships `calc.cable_ampacity` / `calc.voltage_drop` / `calc.cpc_adiabatic`. All 3 calc contracts exist on disk (REUSED, not created).
- **Output intent (4 downstream consumers)**: `cable-schedule` (full per-circuit set) + `riser` (feeder + parent_node_id) + `cable-containment` (cable_od_mm + weight_kg_per_m + parallel_count) + `small-power v1.1` (Zs-resolution helper fields).
- **Zs-resolution helper fields per refresh 2026-05-20**: `r1_plus_r2_milliohm_per_m_at_operating_temp` + `reactance_milliohm_per_m` on every emitted circuit. Lookups from BS 7671 App 4 Tables 4F1-4F3 / IEC 60364-5-52 Table B.52.5 / NEC Chapter 9 Table 9.
- **4 jurisdictional examples**: UK domestic + KE Nairobi commercial + INT commercial with feeders + US industrial with motors.
- **3 prompts**: generator (14-step) + validator (10 INV) + reviewer (8 D).
- **9 evals**: 6 WI5 categories + 3 skill-specific (motor-starting-vd, parallel-cables, harmonic-derating).
- **5 rules + 4 constraints + 4 validation YAMLs** (12 validation checks total).
- **Calc contract consumer updates**: small-power Task 3 precedent — `_consuming_skills[]` added to `cable-ampacity.json` + `voltage-drop.json` + `cpc-adiabatic.json` to record cable-sizing as primary v1.0.0 consumer.

### Pattern parents

- `electrical/fault-level` v1.1 — project-scoped cascade IR (closest structural match)
- `electrical/earthing` v1.4 — 4-jurisdiction example pattern + KS 1700 routing convention
- `electrical/small-power` v1.0 — KE citation form precedent (KS 1700:2018 §313 leading) + WI3 deferral
- `electrical/db-layout` v1.3.1 — multi-skill intent production (produces db-layout AND db-layout-rollup)
- `electrical/sld` v1.4 — multi-skill consumption (consumes 3 intents)

### Future direction (deferred)

- v1.1 — extend intent to cable-schedule deliverable shape; tighten cross-skill consistency checks
- v1.2 — add LV switchboard busbar sizing (BS EN 61439 Annex N)
- v2.0 — DC cable sizing (PV strings + EV DCFC + battery interconnects) breaks v1.x schema
- `dc-cable-sizing` skill — IEC 62548 / NEC 690 / IEC 61851 (separate skill)
```

- [ ] **Step 7: Validate manifest parses + paths resolve**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
python3 -c "
import json, os
m = json.load(open('electrical/cable-sizing/skill.manifest.json'))
assert m['skill'] == 'cable-sizing'
assert m['version'] == '1.0.0'
assert m['consumes_intents'] == ['db-layout-rollup', 'fault-level']
assert m['produces_intent'] == 'cable-sizing'
# Verify all 22 standards paths exist
missing = [p for p in m['standards'] if not os.path.exists(p)]
assert not missing, f'missing standards: {missing}'
# Verify all 3 calc contracts exist
missing_calc = [p for p in m['calculations'] if not os.path.exists(p)]
assert not missing_calc, f'missing calc: {missing_calc}'
print('manifest valid; 22 standards + 3 calc contracts resolve')
"
python3 -c "import json; json.load(open('electrical/cable-sizing/inputs.json')); print('inputs.json valid')"
```

Expected: `manifest valid; 22 standards + 3 calc contracts resolve` + `inputs.json valid`.

- [ ] **Step 8: Commit**

```bash
git add electrical/cable-sizing/skill.manifest.json electrical/cable-sizing/inputs.json electrical/cable-sizing/README.md electrical/cable-sizing/CHANGELOG.md
git commit -m "feat(cable-sizing): v1.0 skill skeleton — manifest + inputs + README + CHANGELOG"
```

---

### Task 2: Schemas (cable-sizing-ir + cable-sizing-intent)

**Model:** Opus (JSON Schema cascade tree with strict additionalProperties + walk-up trail + Zs helper fields).

**Files:**
- Create: `electrical/cable-sizing/schemas/cable-sizing-ir.schema.json`
- Create: `electrical/cable-sizing/schemas/cable-sizing-intent.schema.json`

- [ ] **Step 1: Read fault-level IR schema as cascade-IR pattern**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
cat electrical/fault-level/schemas/fault-level-ir.schema.json
```

- [ ] **Step 2: Write cable-sizing-ir.schema.json**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "electrical/cable-sizing/schemas/cable-sizing-ir.schema.json",
  "title": "Cable-Sizing IR (per-circuit walk-the-ladder selection cascade)",
  "description": "Intermediate Representation for the cable-sizing skill v1.0. One IR per project. Carries cascade tree + per-node selection + walk_up_trail + binding_constraint + checks + rationale. Mirrors fault-level-ir cascade shape.",
  "type": "object",
  "required": [
    "drawing_type",
    "version",
    "meta",
    "jurisdiction",
    "project_supply",
    "cascade",
    "compliance_summary",
    "rationale"
  ],
  "additionalProperties": false,
  "properties": {
    "drawing_type": { "const": "cable_sizing_study" },
    "version":      { "type": "string", "pattern": "^\\d+\\.\\d+(\\.\\d+)?$" },
    "meta": {
      "type": "object",
      "required": ["project_id", "skill_version", "produced_at"],
      "additionalProperties": false,
      "properties": {
        "project_id":    { "type": "string" },
        "skill_version": { "type": "string" },
        "produced_at":   { "type": "string", "format": "date-time" },
        "consumed_intents": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["intent_type", "intent_version", "produced_by"],
            "additionalProperties": false,
            "properties": {
              "intent_type":    { "enum": ["db-layout-rollup", "fault-level"] },
              "intent_version": { "type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$" },
              "produced_by":    { "type": "string" }
            }
          }
        }
      }
    },
    "jurisdiction": { "enum": ["GB", "EU", "INT", "KE", "US"] },
    "project_supply": {
      "type": "object",
      "required": ["voltage_v", "phase_arrangement"],
      "additionalProperties": false,
      "properties": {
        "voltage_v":         { "type": "integer", "enum": [120, 208, 230, 240, 277, 400, 415, 480] },
        "phase_arrangement": { "enum": ["single_phase", "single_phase_split", "TPN", "TPN_plus_E"] },
        "system_type":       { "enum": ["TN-S", "TN-C-S", "TT", "IT"] }
      }
    },
    "cascade": {
      "type": "array",
      "minItems": 1,
      "items": { "$ref": "#/definitions/CascadeNode" }
    },
    "compliance_summary": {
      "type": "object",
      "required": ["compliant", "non_compliance_flags", "assumptions"],
      "additionalProperties": false,
      "properties": {
        "compliant":            { "type": "boolean" },
        "non_compliance_flags": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["message"],
            "additionalProperties": false,
            "properties": {
              "node_id":     { "type": "string" },
              "message":     { "type": "string" },
              "code_clause": { "type": "string" },
              "severity":    { "enum": ["critical", "warning", "info"] }
            }
          }
        },
        "assumptions": { "type": "array", "items": { "type": "string" } }
      }
    },
    "flags": { "type": "array", "items": { "type": "string" } },
    "rationale": { "$ref": "../../../shared/schemas/core/rationale.schema.json" }
  },
  "definitions": {
    "CascadeNode": {
      "type": "object",
      "required": ["node_id", "node_kind", "designation", "load", "route", "selection", "checks"],
      "additionalProperties": false,
      "properties": {
        "node_id":        { "type": "string", "pattern": "^[A-Z0-9][A-Za-z0-9._-]*$" },
        "parent_node_id": { "type": "string" },
        "node_kind":      { "enum": ["final_circuit", "feeder", "sub_feeder", "service_entrance"] },
        "designation":    { "type": "string" },
        "load": {
          "type": "object",
          "required": ["ib_a", "in_a", "phases", "load_type"],
          "additionalProperties": false,
          "properties": {
            "ib_a":      { "type": "number", "minimum": 0 },
            "in_a":      { "type": "number", "minimum": 0 },
            "phases":    { "enum": ["single", "single_split", "three_phase_3wire", "three_phase_4wire"] },
            "load_type": { "enum": ["lighting", "power_general", "power_socket", "motor", "heating", "cooker", "it_load", "ev_charging", "fixed_appliance", "mixed"] },
            "pf":        { "type": "number", "minimum": 0, "maximum": 1.0 },
            "load_class_motor": {
              "type": "object",
              "additionalProperties": false,
              "properties": {
                "rated_kw":    { "type": "number", "minimum": 0 },
                "lra_factor":  { "type": "number", "minimum": 1.0, "maximum": 10.0 },
                "design_code": { "enum": ["NEMA_B", "NEMA_C", "IEC_AA", "IEC_AB"] }
              }
            }
          }
        },
        "route": {
          "type": "object",
          "required": ["length_m", "installation_method"],
          "additionalProperties": false,
          "properties": {
            "length_m":               { "type": "number", "exclusiveMinimum": 0 },
            "installation_method":    { "enum": ["A1","A2","B1","B2","C","D1","D2","E","F","G","nec_conduit","nec_cable_tray","nec_direct_burial","nec_free_air"] },
            "ambient_c":              { "type": "integer", "minimum": -20, "maximum": 90 },
            "grouping_count":         { "type": "integer", "minimum": 1 },
            "in_thermal_insulation":  { "type": "boolean" },
            "terminal_temp_rating_c": { "type": "integer", "enum": [60, 75, 90] }
          }
        },
        "harmonic_content_pct":  { "type": "number", "minimum": 0, "maximum": 100 },
        "parent_node_ifault_ka": { "type": "number", "minimum": 0 },
        "t_clear_s":             { "type": "number", "minimum": 0 },
        "selection": {
          "type": "object",
          "required": ["phase_csa", "cpc_csa", "material", "insulation", "cable_type", "parallel_count", "binding_constraint", "walk_up_trail"],
          "additionalProperties": false,
          "properties": {
            "phase_csa": {
              "oneOf": [
                { "type": "number", "minimum": 1.0 },
                { "type": "string", "pattern": "^([0-9]+(\\.[0-9]+)?(/0)?( AWG)?|[0-9]+ kcmil)$" }
              ]
            },
            "cpc_csa": {
              "oneOf": [
                { "type": "number", "minimum": 1.0 },
                { "type": "string" }
              ]
            },
            "material":            { "enum": ["copper", "aluminium"] },
            "insulation":          { "enum": ["pvc_70", "xlpe_90", "epr_90", "mineral_micc_90", "fp200_90", "cwz_90", "thwn_2_90", "thhn_90", "xhhw_2_90"] },
            "cable_type":          { "enum": ["pvc_singles", "pvc_multicore", "xlpe_swa", "xlpe_lszh", "epr_swa", "mineral_micc", "fp200_lszh", "cwz_glass_mica", "thwn_2", "thhn", "xhhw_2"] },
            "parallel_count":      { "type": "integer", "minimum": 1, "maximum": 6 },
            "binding_constraint":  { "enum": ["iz_vs_in", "vd_cumulative", "motor_starting_vd", "cpc_adiabatic", "parallel_required", "harmonic_derating"] },
            "walk_up_trail": {
              "type": "array",
              "minItems": 1,
              "items": {
                "type": "object",
                "required": ["csa_attempted"],
                "additionalProperties": false,
                "properties": {
                  "csa_attempted":      { "oneOf": [{ "type": "number" }, { "type": "string" }] },
                  "accepted":           { "type": "boolean" },
                  "rejected_by":        { "enum": ["iz_vs_in", "vd_cumulative", "motor_starting_vd", "cpc_adiabatic", "harmonic_derating"] },
                  "iz_corrected_a":     { "type": "number", "minimum": 0 },
                  "vd_segment_pct":     { "type": "number", "minimum": 0 },
                  "vd_cumulative_pct":  { "type": "number", "minimum": 0 }
                }
              }
            }
          }
        },
        "checks": {
          "type": "object",
          "required": ["iz_corrected_a", "iz_vs_in_pass", "vd_cumulative_pct", "vd_limit_pct", "vd_pass", "cpc_adiabatic_pass", "tool_call_pending"],
          "additionalProperties": false,
          "properties": {
            "iz_corrected_a":        { "type": "number", "minimum": 0 },
            "iz_vs_in_pass":         { "type": "boolean" },
            "vd_segment_pct":        { "type": "number", "minimum": 0 },
            "vd_cumulative_pct":     { "type": "number", "minimum": 0 },
            "vd_limit_pct":          { "type": "number", "minimum": 0 },
            "vd_limit_source":       { "type": "string" },
            "vd_pass":               { "type": "boolean" },
            "cpc_adiabatic_pass":    { "type": "boolean" },
            "cpc_adiabatic_source":  { "type": "string" },
            "motor_starting_vd_pct": { "oneOf": [{ "type": "number", "minimum": 0 }, { "type": "null" }] },
            "motor_starting_vd_pass":{ "oneOf": [{ "type": "boolean" }, { "type": "null" }] },
            "harmonic_ch_applied":   { "type": "number", "minimum": 0, "maximum": 1.0 },
            "tool_call_pending":     { "type": "boolean", "default": true }
          }
        }
      }
    }
  }
}
```

- [ ] **Step 3: Write cable-sizing-intent.schema.json (with Zs helper fields per refresh)**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "electrical/cable-sizing/schemas/cable-sizing-intent.schema.json",
  "title": "Cable-Sizing Intent (Downstream-Facing)",
  "description": "Stable subset of the cable-sizing IR. Consumed by cable-schedule (tabulated deliverable), riser (parent-child rendering), cable-containment (tray/conduit fill), and small-power v1.1 (Zs resolution via table lookup). Union superset of all 4 consumers' field sets. Forward-compat: optional fields may be added; required-field changes require a major intent_version bump.",
  "type": "object",
  "required": ["project_id", "circuits"],
  "additionalProperties": false,
  "properties": {
    "project_id":     { "type": "string" },
    "intent_version": { "type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$" },
    "circuits": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": [
          "node_id",
          "designation",
          "phase_csa_mm2_or_awg",
          "cpc_csa_mm2_or_awg",
          "material",
          "insulation",
          "cable_type",
          "parallel_count",
          "length_m",
          "installation_method",
          "r1_plus_r2_milliohm_per_m_at_operating_temp",
          "reactance_milliohm_per_m"
        ],
        "additionalProperties": false,
        "properties": {
          "node_id":                                       { "type": "string", "pattern": "^[A-Z0-9][A-Za-z0-9._-]*$" },
          "parent_node_id":                                { "type": "string" },
          "designation":                                   { "type": "string" },
          "phase_csa_mm2_or_awg":                          { "type": "string" },
          "cpc_csa_mm2_or_awg":                            { "type": "string" },
          "material":                                      { "enum": ["copper", "aluminium"] },
          "insulation":                                    { "enum": ["pvc_70", "xlpe_90", "epr_90", "mineral_micc_90", "fp200_90", "cwz_90", "thwn_2_90", "thhn_90", "xhhw_2_90"] },
          "cable_type":                                    { "enum": ["pvc_singles", "pvc_multicore", "xlpe_swa", "xlpe_lszh", "epr_swa", "mineral_micc", "fp200_lszh", "cwz_glass_mica", "thwn_2", "thhn", "xhhw_2"] },
          "parallel_count":                                { "type": "integer", "minimum": 1, "maximum": 6 },
          "cable_od_mm":                                   { "type": "number", "exclusiveMinimum": 0 },
          "weight_kg_per_m":                               { "type": "number", "exclusiveMinimum": 0 },
          "length_m":                                      { "type": "number", "exclusiveMinimum": 0 },
          "installation_method":                           { "enum": ["A1","A2","B1","B2","C","D1","D2","E","F","G","nec_conduit","nec_cable_tray","nec_direct_burial","nec_free_air"] },
          "r1_plus_r2_milliohm_per_m_at_operating_temp":   { "type": "number", "exclusiveMinimum": 0, "description": "Combined phase + CPC resistance per metre at the cable's operating temperature (PVC 70°C / XLPE 90°C / NEC 90°C). Source: BS 7671 App 4 Tables 4F1-4F3 / IEC 60364-5-52 Table B.52.5 / NEC Chapter 9 Table 9." },
          "reactance_milliohm_per_m":                      { "type": "number", "minimum": 0, "description": "Cable reactance per metre. Same source tables. Negligible (<0.1 mΩ/m) for ≤16 mm²; material above 25 mm²." }
        }
      }
    }
  }
}
```

- [ ] **Step 4: Validate both schemas as Draft-07**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
python3 -c "
import json, jsonschema
for path in ['electrical/cable-sizing/schemas/cable-sizing-ir.schema.json',
             'electrical/cable-sizing/schemas/cable-sizing-intent.schema.json']:
    with open(path) as f: s = json.load(f)
    jsonschema.Draft7Validator.check_schema(s)
    print(f'{path}: valid Draft-07')

# Verify required enums
with open('electrical/cable-sizing/schemas/cable-sizing-ir.schema.json') as f: ir = json.load(f)
binding = ir['definitions']['CascadeNode']['properties']['selection']['properties']['binding_constraint']['enum']
assert binding == ['iz_vs_in', 'vd_cumulative', 'motor_starting_vd', 'cpc_adiabatic', 'parallel_required', 'harmonic_derating']
print('binding_constraint enum (6 tokens): OK')

with open('electrical/cable-sizing/schemas/cable-sizing-intent.schema.json') as f: intent = json.load(f)
req = intent['properties']['circuits']['items']['required']
assert 'r1_plus_r2_milliohm_per_m_at_operating_temp' in req
assert 'reactance_milliohm_per_m' in req
print('Zs helper fields required on intent circuits: OK')
"
```

- [ ] **Step 5: Commit**

```bash
git add electrical/cable-sizing/schemas/
git commit -m "feat(cable-sizing): IR + intent schemas — cascade tree + walk_up_trail + Zs helper fields per refresh"
```

---

### Task 3: Calc-contract consumer updates (3 files)

**Model:** Sonnet (mechanical — surgical edits to existing files).

**Files:**
- Modify: `shared/calculations/electrical/cable-ampacity.json` — add `_consuming_skills`
- Modify: `shared/calculations/electrical/voltage-drop.json` — add `_consuming_skills`
- Modify: `shared/calculations/electrical/cpc-adiabatic.json` — add `_consuming_skills`

- [ ] **Step 1: Read each calc contract to find insertion point**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
for f in cable-ampacity voltage-drop cpc-adiabatic; do
  python3 -c "
import json
d = json.load(open('shared/calculations/electrical/${f}.json'))
print('${f}: existing top-level keys:', list(d.keys()))
print('  _consuming_skills present:', '_consuming_skills' in d)
"
done
```

- [ ] **Step 2: Add `_consuming_skills` field to each calc contract**

For each of the 3 files, use Edit (NOT Write — preserve existing content) to add the field. The exact insertion sits after `implementation_note` (or whatever last existing top-level metadata field precedes `inputs`).

For `shared/calculations/electrical/cable-ampacity.json`, add after the last top-level metadata field:
```json
  "_consuming_skills": [
    "electrical/cable-sizing (primary, since v1.0.0)"
  ],
```

For `shared/calculations/electrical/voltage-drop.json`, same pattern:
```json
  "_consuming_skills": [
    "electrical/cable-sizing (primary, since v1.0.0)"
  ],
```

For `shared/calculations/electrical/cpc-adiabatic.json`, same pattern:
```json
  "_consuming_skills": [
    "electrical/cable-sizing (primary, since v1.0.0)"
  ],
```

Use Read first on each file to find the correct insertion line, then Edit to insert. The line must be valid JSON (correct comma placement).

- [ ] **Step 3: Validate**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
python3 -c "
import json
for f in ['cable-ampacity', 'voltage-drop', 'cpc-adiabatic']:
    d = json.load(open(f'shared/calculations/electrical/{f}.json'))
    assert 'electrical/cable-sizing (primary, since v1.0.0)' in d['_consuming_skills'], f'{f}: cable-sizing missing'
    print(f'{f}: cable-sizing consumer recorded')
"
```

Expected: 3 lines `<name>: cable-sizing consumer recorded`.

- [ ] **Step 4: Commit**

```bash
git add shared/calculations/electrical/cable-ampacity.json shared/calculations/electrical/voltage-drop.json shared/calculations/electrical/cpc-adiabatic.json
git commit -m "feat(calc): record cable-sizing v1.0 as primary consumer on 3 calc contracts (cable-ampacity + voltage-drop + cpc-adiabatic)"
```

---

## Phase B — Prompts (Tasks 4-6)

### Task 4: Generator prompt — 14-step chain

**Model:** Opus (engineering reasoning + 14 steps + jurisdictional citation logic).

**Files:**
- Create: `electrical/cable-sizing/prompts/generator.md`

- [ ] **Step 1: Read fault-level generator as cascade-skill template**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
cat electrical/fault-level/prompts/generator.md
```

- [ ] **Step 2: Write generator.md with YAML frontmatter + 14 numbered steps + 8-section rationale block**

The prompt file must include:

**Frontmatter:**
```yaml
---
name: cable-sizing
description: "Per-circuit cable selection for every cable run in a project's distribution cascade. Walks the standard csa ladder; names the binding constraint per node; records walk-up trail."
version: 1.0.0
discipline: electrical
standards:
  - BS 7671:2018+A2:2022 (App 4 ampacity + App 12 voltage drop + Reg 433 + Reg 543)
  - IEC 60364-5-52:2009 (ampacity + voltage drop + installation methods)
  - IEC 60364-5-54:2011 (earthing + CPC)
  - KS 1700:2018 §313 (routes to BS 7671)
  - NEC 2023 Chapter 9 Table 9 (impedance) + Article 310.16 (ampacity) + 240.4(B) (next size up) + 250.122 (CPC)
  - NEMA MG-1 (motor LRA) + IEC 60034-1
output_format: json
tags:
  - calculations
  - electrical
  - cable-sizing
---
```

**Section 1: Role** — Senior electrical engineer specialising in cable selection per BS 7671 / IEC / NEC. 20+ years across UK + East Africa + Europe + US. Walks the standard csa ladder transparently. Names the binding constraint. Never invents Iz or Vd values — always cites a table.

**Section 2: Standards You Apply** — full table from spec §11 (22 standards files referenced)

**Section 3: Inputs Required** — from `electrical/cable-sizing/inputs.json` (4 input groups: jurisdiction + consumed-intents + engineer-declared-fallbacks + route-data-per-segment + design-intent-overrides)

**Section 4: How You Think Before Acting** — 14 steps from spec §7.1:

1. **Ingest db-layout-rollup intent** → extract circuit list, parent topology, Ib, In, load_type. Record in `meta.consumed_intents[]`. If absent, use `circuits_declared` engineer fallback.
2. **Ingest fault-level intent** → extract per-node Ik"max + Ik"min + t_clear. Record in `meta.consumed_intents[]`. If absent, use `t_clear_declared_per_node` engineer fallback.
3. **Determine jurisdiction** → load applicable Vd limits + ampacity table family + correction factor stack.
4. **Build cascade tree** (node_id paths) — service entrance → feeder → sub-feeder → final circuit. node_id pattern `[A-Z0-9][A-Za-z0-9._-]*` (e.g., `MSB-1.F03.DB-L1.C07`).
5. **Engineer-declared route overlay** → length_m, installation_method, ambient_c, grouping_count, harmonic_content_pct per node.
6. **Per node (root → leaves)**: determine starting csa from In (smallest where Iz_tabulated × selected_correction_factors ≥ In; for US, then cap by terminal_temp_rating per NEC 110.14(C)).
7. **Walk-up loop**: `calc.cable_ampacity` → check Iz vs In. If fails, advance to next ladder size.
8. **`calc.voltage_drop`** → compute vd_segment_pct → add parent's cumulative → check vs limit. If fails, walk up.
9. **`calc.cpc_adiabatic`** with parent_ifault + t_clear → check CPC sizing. If fails, upsize phase (CPC adiabatic binding).
10. **Motor check**: if `load.load_type == "motor"`, compute vd_starting_pct at LRA × Ib_motor. Check ≤ 10% (warning, not error).
11. **Parallel cables**: if ladder exhausted at single-cable scope, engage parallel rule (N × Iz ≥ In, each parallel ≥ 50 mm² per IEC 60364-5-52 §523.6 / ≥ 1/0 AWG per NEC 310.10(H)(1), symmetric routes).
12. **Cable physical data lookup**: emit `cable_od_mm` + `weight_kg_per_m` from `shared/standards/electrical/<juris>/cable-types-overview.md` or `NFPA70/chapter9-tables.json`. **AND** emit `r1_plus_r2_milliohm_per_m_at_operating_temp` + `reactance_milliohm_per_m` from `BS 7671 App 4 Tables 4F1-4F3` / `IEC 60364-5-52 Table B.52.5` / `NEC Chapter 9 Table 9` at the cable's operating temp (PVC 70°C / XLPE/EPR/MICC/NEC-90°C).
13. **Record selection** + `binding_constraint` + `walk_up_trail` per node.
14. **Emit `cable-sizing` intent** (slim downstream subset, union superset of 4 consumers' field sets) alongside the full IR.

**Section 5: What You Never Do** —
- Invent Iz, Vd, or impedance values — always cite a table
- Skip cumulative Vd (per-segment is misleading: 4% + 4% = 8% at load)
- Mix material within a parallel set (all parallels must be identical csa + material + insulation + length)
- Apply Type B RCD reasoning here (that's small-power's domain — cable-sizing produces the data small-power v1.1 consumes)
- Cite BS 7671 in INT or US examples except as a comparative reference
- Use the forbidden `"adopted by KS 1700"` annotation form in KE example (use explicit routing form `KS 1700:2018 §X routes to BS 7671:2018+A2:2022 §Y`)
- Omit `tool_call_pending: true` until runtime ships the 3 calc tools

**Section 6: Output Format** — Conform strictly to `electrical/cable-sizing/schemas/cable-sizing-ir.schema.json`. `additionalProperties: false` on all sub-objects. Emit the intent simultaneously.

**Section 7: Tools Available at Runtime** —
- `calc.cable_ampacity` — `shared/calculations/electrical/cable-ampacity.json` — currently deferred (tool_call_pending). Engineer estimates Iz inline using App 4 / IEC tables / NEC ampacity tables until tool ships.
- `calc.voltage_drop` — `shared/calculations/electrical/voltage-drop.json` — deferred.
- `calc.cpc_adiabatic` — `shared/calculations/electrical/cpc-adiabatic.json` — deferred.
All 3 referenced from manifest.calculations[].

**Section 8: Required IR Output Block** — point at the schema; show one full cascade-node example.

**Section 9: Step 14 (final) — Emit `rationale` block (WI2)** — 8-section structure:
1. Project Supply + Jurisdiction
2. Cascade Tree + Topology
3. Walk-the-Ladder Approach + Binding Constraints
4. Cumulative Voltage Drop
5. CPC Adiabatic Sizing
6. Motor Starting + Parallel Cables + Harmonic Derating (only sections used)
7. Compliance + Assumptions + Tool-Call Pending
8. Cross-Skill Contract — emitted cable-sizing intent + 4 downstream consumers

`chat_summary` ≤ 500 chars: concise narrative of the project, dominant binding constraint(s), and any deferred verifications.

- [ ] **Step 3: Verify generator.md structure**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
wc -l electrical/cable-sizing/prompts/generator.md
grep -c '^## ' electrical/cable-sizing/prompts/generator.md
grep -cE '^### Step ([0-9]+) — ' electrical/cable-sizing/prompts/generator.md
```

Expected: ~300-450 lines, 8-9 `## ` H2 sections, 14 `### Step N — ` step headings.

- [ ] **Step 4: Commit**

```bash
git add electrical/cable-sizing/prompts/generator.md
git commit -m "feat(cable-sizing): generator prompt — 14-step chain + 8-section rationale + jurisdictional standards"
```

---

### Task 5: Validator prompt — 10 INV invariants

**Model:** Opus (each INV check is a precise engineering rule).

**Files:**
- Create: `electrical/cable-sizing/prompts/validator.md`

- [ ] **Step 1: Read SLD v1.5 validator as INV-format template**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
head -100 electrical/sld/prompts/validator.md
```

- [ ] **Step 2: Write validator.md with 10 INV checks**

YAML frontmatter same shape as Task 4. Then 10 INV sections per spec §7.2. Each INV has `## INV-NN: <Title>` heading + **Rule:** paragraph + **Severity:** Hard fail / Warning + **Fail message format:** code block.

The 10 INV checks (verbatim from spec §7.2):

1. **INV-01: node_id format** — Every cascade node has a valid `node_id` matching pattern `^[A-Z0-9][A-Za-z0-9._-]*$` (board.feeder.circuit). Hard fail.
2. **INV-02: parent_node_id resolves** — Every non-root cascade node has `parent_node_id` resolvable to another node in `cascade[]`. Hard fail.
3. **INV-03: csa on ladder** — Every `selection.phase_csa` is on the standard ladder for the jurisdiction (IEC mm² ladder `[1.0, 1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240, 300, 400, 500, 630]` for GB/EU/INT/KE; AWG ladder `["14", "12", "10", "8", "6", "4", "3", "2", "1", "1/0", "2/0", "3/0", "4/0", "250", "300", "350", "400", "500", "600", "750", "1000"]` for US). Hard fail.
4. **INV-04: Iz ≥ In** — Every `checks.iz_corrected_a ≥ load.in_a`. Hard fail.
5. **INV-05: Cumulative Vd ≤ limit** — Every `checks.vd_cumulative_pct ≤ checks.vd_limit_pct` for its load type per jurisdiction (GB App 12: 3% lighting / 5% power; INT IEC 60364-5-52 §G: 3% lighting / 5% power; US NEC 215.2(A)(1) IN 2: feeder-only 3% / feeder+branch 5%). Hard fail.
6. **INV-06: CPC adiabatic** — `checks.cpc_adiabatic_pass == true` OR `selection.binding_constraint == "cpc_adiabatic"` (the phase has been upsized to permit larger CPC). Hard fail otherwise.
7. **INV-07: Motor checks present** — Motor nodes (`load.load_type == "motor"`) have `checks.motor_starting_vd_pct` populated; non-motor nodes have it null. Hard fail on absent value for motor; warning on inconsistency for non-motor.
8. **INV-08: Parallel cable rules** — Parallel nodes (`selection.parallel_count ≥ 2`) have each parallel ≥ 50 mm² (IEC) or ≥ 1/0 AWG (NEC). Hard fail.
9. **INV-09: Tool-call consistency** — Every node carries `checks.tool_call_pending == true` OR all 3 calc tool outputs are populated (`iz_corrected_a`, `vd_cumulative_pct`, `cpc_adiabatic_pass`). Hard fail on mixed state.
10. **INV-10: Emitted intent conforms** — Emitted `cable-sizing` intent matches `cable-sizing-intent.schema.json` AND contains every final-circuit cascade node AND every circuit carries the 2 Zs-resolution helper fields (`r1_plus_r2_milliohm_per_m_at_operating_temp` + `reactance_milliohm_per_m`). Hard fail.

For each INV, show a concrete fail message:
```
INV-04: node <node_id> has iz_corrected=<X>A but in=<Y>A. Iz must be ≥ In per BS 7671:2018+A2:2022 Reg 433.1 / IEC 60364-4-43 §433.1 / NEC 2023 Article 240.4(B). Walk up the ladder one csa.
```

End with a `valid: true` gate paragraph: "valid: true requires INV-01 through INV-10 all pass (no hard fails)."

- [ ] **Step 3: Verify validator.md structure**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
wc -l electrical/cable-sizing/prompts/validator.md
grep -c '^## INV-' electrical/cable-sizing/prompts/validator.md
```

Expected: ~200-300 lines, 10 `## INV-` sections.

- [ ] **Step 4: Commit**

```bash
git add electrical/cable-sizing/prompts/validator.md
git commit -m "feat(cable-sizing): validator prompt — 10 INV checks (cascade integrity + csa ladder + Iz/Vd/CPC + parallel + intent shape)"
```

---

### Task 6: Reviewer prompt — 8 D dimensions

**Model:** Opus (each D is an engineering judgment dimension).

**Files:**
- Create: `electrical/cable-sizing/prompts/reviewer.md`

- [ ] **Step 1: Read arc-flash-labelling reviewer.md as D-check template**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
cat electrical/arc-flash-labelling/prompts/reviewer.md
```

- [ ] **Step 2: Write reviewer.md with 8 D dimensions**

YAML frontmatter same shape. Then 8 D sections per spec §7.3 with `### D-N — <Title>` + **Question:** + **Look for:** + **Flag when:** format.

The 8 D dimensions:

1. **D-1 — Sources cited per rule** — Every Vd limit cites BS 7671 App 12 / IEC 60364-5-52 §G / NEC 215.2(A). Every Iz value cites App 4 / Table B.52 / Chapter 9 Table 9.
2. **D-2 — Walk-up trail is auditable** — Each rejected csa in `walk_up_trail[]` names the failing check (`rejected_by` field populated).
3. **D-3 — Binding constraint matches walk-up trail** — `selection.binding_constraint` equals the `rejected_by` reason at the last walk-up step before the accepted csa.
4. **D-4 — Cumulative Vd math sums up parent chain** — Spot-check 2 random leaves: leaf `vd_cumulative_pct == sum(parent_chain.vd_segment_pct + this.vd_segment_pct)`. Tolerance ±0.05%.
5. **D-5 — CPC sizing cites correct standard** — GB cites Table 54.7 (BS 7671) + Reg 543.1.3; INT cites IEC 60364-5-54; US cites NEC 250.122.
6. **D-6 — Parallel cables symmetry** — Where `parallel_count ≥ 2`, all parallels match on length + csa + material + installation method (identical impedance → balanced current sharing).
7. **D-7 — Harmonic derating applied where required** — If any node has `harmonic_content_pct > 15` AND `load.phases == "three_phase_4wire"`, `checks.harmonic_ch_applied < 1.0` AND `selection.binding_constraint` references `harmonic_derating` where appropriate. Reference: BS 7671 App 4 §5.5 / IEC 60364-5-52 Annex E §E.5 / NEC 310.15(E).
8. **D-8 — Rationale block** — 8 sections present + `chat_summary` ≤ 500 chars + WI2-conformant.

Also include a **D-3-citation-rigour** sub-check (matches small-power D-3 pattern):
- GB jurisdiction → primary citation `BS 7671:2018+A2:2022 §X`
- KE jurisdiction → primary citation `KS 1700:2018 §X` (NEVER bare BS 7671 except in explicit routing form `KS 1700:2018 §X routes to BS 7671:2018+A2:2022 §Y`)
- INT/EU → `IEC 60364-X-XX:YYYY §Z`
- US → `NEC 2023 Article X`
- FORBIDDEN: `"adopted by KS 1700"` annotation form anywhere
- FORBIDDEN: NEC citation as primary in GB/KE/INT examples

- [ ] **Step 3: Verify reviewer.md**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
wc -l electrical/cable-sizing/prompts/reviewer.md
grep -cE '^### D-[0-9]+' electrical/cable-sizing/prompts/reviewer.md
```

Expected: ~100-180 lines, 8 `### D-N` sections.

- [ ] **Step 4: Commit**

```bash
git add electrical/cable-sizing/prompts/reviewer.md
git commit -m "feat(cable-sizing): reviewer prompt — 8 D dimensions (sources + audit trail + Vd math + CPC + parallel + harmonic + rationale + citation rigour)"
```

---

## Phase C — 4 Jurisdictional Examples (Tasks 7-10)

Each example folder contains 4 files: `input.json` + `output.json` (full IR) + `intent-out.json` + `reasoning.md`. Total 16 files across 4 tasks.

For ALL examples:
- `output.json` must validate against `cable-sizing-ir.schema.json`
- `intent-out.json` must validate against `cable-sizing-intent.schema.json`
- `intent-out.json` MUST carry `r1_plus_r2_milliohm_per_m_at_operating_temp` + `reactance_milliohm_per_m` on every circuit
- `reasoning.md` has 8 sections matching the rationale block titles
- `chat_summary` 40-500 chars (rationale schema enforces)

### Task 7: UK domestic final circuits example

**Model:** Opus (engineering judgment).

**Files (4):**
- Create: `electrical/cable-sizing/examples/uk-domestic-final-circuits/input.json`
- Create: `electrical/cable-sizing/examples/uk-domestic-final-circuits/output.json`
- Create: `electrical/cable-sizing/examples/uk-domestic-final-circuits/intent-out.json`
- Create: `electrical/cable-sizing/examples/uk-domestic-final-circuits/reasoning.md`

- [ ] **Step 1: Engineering scenario**

UK 230V single-phase domestic dwelling, ~100 m². TN-C-S DNO supply, Ze=0.35Ω, declared PFC=6kA. Consumer unit `CU-MAIN`. 5 cable runs:

| node_id | designation | load_type | Ib (A) | In (A) | length (m) | install_method | expected csa |
|---|---|---|---|---|---|---|---|
| `CU-MAIN.C01` | Ground-floor ring final | power_general | 24.0 | 32 | 32 (ring) | B1 | 2.5 mm² (ring) |
| `CU-MAIN.C02` | First-floor ring final | power_general | 18.0 | 32 | 28 (ring) | B1 | 2.5 mm² (ring) |
| `CU-MAIN.C03` | Lighting upstairs | lighting | 4.5 | 6 | 22 | A1 | 1.5 mm² — **Vd binding** |
| `CU-MAIN.C04` | Cooker dedicated radial | cooker | 22.0 | 32 | 8 | C | 6 mm² |
| `CU-MAIN.C05` | Immersion heater | heating | 12.0 | 16 | 4 | C | 2.5 mm² |

Expected binding constraints: C01 + C02 + C04 + C05 = `iz_vs_in`; C03 = `vd_cumulative` (long radial lighting circuit forces walk-up from 1.0 to 1.5 mm²).

- [ ] **Step 2: Author input.json**

```json
{
  "project_id": "uk-domestic-eg01",
  "jurisdiction": "GB",
  "site_brief": "UK 3-bedroom dwelling on TN-C-S 230V single-phase supply. Cable sizing for 5 final circuits from CU-MAIN. Engineer declares cascade inline (no db-layout-rollup intent consumed in this demonstration); engineer declares per-node t_clear from RCBO time-current curves (0.4s ADS).",
  "supply": {
    "voltage_v": 230,
    "phase_arrangement": "single_phase",
    "system_type": "TN-C-S"
  },
  "circuits_declared": [
    {"node_id": "CU-MAIN.C01", "parent_node_id": "CU-MAIN", "node_kind": "final_circuit", "designation": "Ground-floor ring final", "load": {"ib_a": 24.0, "in_a": 32, "phases": "single", "load_type": "power_general", "pf": 1.0}, "route": {"length_m": 32, "installation_method": "B1", "ambient_c": 30, "grouping_count": 2}, "parent_node_ifault_ka": 6.0, "t_clear_s": 0.4},
    {"node_id": "CU-MAIN.C02", "parent_node_id": "CU-MAIN", "node_kind": "final_circuit", "designation": "First-floor ring final", "load": {"ib_a": 18.0, "in_a": 32, "phases": "single", "load_type": "power_general", "pf": 1.0}, "route": {"length_m": 28, "installation_method": "B1", "ambient_c": 30, "grouping_count": 1}, "parent_node_ifault_ka": 6.0, "t_clear_s": 0.4},
    {"node_id": "CU-MAIN.C03", "parent_node_id": "CU-MAIN", "node_kind": "final_circuit", "designation": "Lighting upstairs radial", "load": {"ib_a": 4.5, "in_a": 6, "phases": "single", "load_type": "lighting", "pf": 1.0}, "route": {"length_m": 22, "installation_method": "A1", "ambient_c": 30, "grouping_count": 1}, "parent_node_ifault_ka": 6.0, "t_clear_s": 0.4},
    {"node_id": "CU-MAIN.C04", "parent_node_id": "CU-MAIN", "node_kind": "final_circuit", "designation": "Cooker dedicated radial", "load": {"ib_a": 22.0, "in_a": 32, "phases": "single", "load_type": "cooker", "pf": 1.0}, "route": {"length_m": 8, "installation_method": "C", "ambient_c": 30, "grouping_count": 1}, "parent_node_ifault_ka": 6.0, "t_clear_s": 0.4},
    {"node_id": "CU-MAIN.C05", "parent_node_id": "CU-MAIN", "node_kind": "final_circuit", "designation": "Immersion heater dedicated radial", "load": {"ib_a": 12.0, "in_a": 16, "phases": "single", "load_type": "heating", "pf": 1.0}, "route": {"length_m": 4, "installation_method": "C", "ambient_c": 30, "grouping_count": 1}, "parent_node_ifault_ka": 6.0, "t_clear_s": 0.4}
  ],
  "design_intent": {
    "cable_type_preference": "pvc_singles"
  }
}
```

- [ ] **Step 3: Author output.json (full IR)**

Build IR with:
- `drawing_type: "cable_sizing_study"`, `version: "1.0.0"`
- `meta: {project_id: "uk-domestic-eg01", skill_version: "1.0.0", produced_at: "2026-05-20T00:00:00Z", consumed_intents: []}`
- `jurisdiction: "GB"`, `project_supply: {voltage_v: 230, phase_arrangement: "single_phase", system_type: "TN-C-S"}`
- `cascade[]`: 5 entries (one per circuit declared)
- `compliance_summary: {compliant: true, non_compliance_flags: [{node_id: "CU-MAIN.C03", message: "Vd binding constraint on lighting radial — 22m run forces csa walk-up from 1.0 to 1.5 mm²", code_clause: "BS 7671:2018+A2:2022 App 12 §G", severity: "info"}], assumptions: ["Engineer declared Ze=0.35Ω verified at consumer cut-out", "PSCC=6kA per DNO declaration"]}`
- `flags: ["TOOL-CALL-PENDING:calc.cable_ampacity", "TOOL-CALL-PENDING:calc.voltage_drop", "TOOL-CALL-PENDING:calc.cpc_adiabatic"]`
- `rationale: {chat_summary, sections: [...]}`

Each cascade node MUST carry:
- selection: phase_csa, cpc_csa, material=copper, insulation=pvc_70, cable_type=pvc_singles, parallel_count=1, binding_constraint, walk_up_trail
- checks: iz_corrected_a, iz_vs_in_pass=true, vd_segment_pct, vd_cumulative_pct, vd_limit_pct=3.0 (lighting) or 5.0 (power), vd_pass=true, cpc_adiabatic_pass=true, motor_starting_vd_pct=null, tool_call_pending=true

**C03 (lighting Vd binding) walk_up_trail** must show:
```json
[
  {"csa_attempted": 1.0, "accepted": false, "rejected_by": "vd_cumulative", "iz_corrected_a": 11.5, "vd_segment_pct": 3.4, "vd_cumulative_pct": 3.4},
  {"csa_attempted": 1.5, "accepted": true, "iz_corrected_a": 14.5, "vd_segment_pct": 2.2, "vd_cumulative_pct": 2.2}
]
```

**chat_summary template (≤500 chars):** "UK 230V single-phase domestic dwelling, TN-C-S, Ze=0.35Ω, PSCC=6kA. 5 final circuits sized per BS 7671:2018+A2:2022 App 4 + App 12: 2× 2.5 mm² rings + 1.5 mm² upstairs lighting (vd_cumulative binding at 22m radial per App 12) + 6 mm² cooker + 2.5 mm² immersion. All copper PVC singles. CPC sized per Table 54.7 — adiabatic passes. calc.cable_ampacity + calc.voltage_drop + calc.cpc_adiabatic deferred per WI3."

**8 rationale sections** (titles exact):
1. Project Supply + Jurisdiction
2. Cascade Tree + Topology
3. Walk-the-Ladder Approach + Binding Constraints
4. Cumulative Voltage Drop
5. CPC Adiabatic Sizing
6. Motor Starting + Parallel Cables + Harmonic Derating
7. Compliance + Assumptions + Tool-Call Pending
8. Cross-Skill Contract

Each section.summary ≤ 400 chars (rationale schema enforces).

- [ ] **Step 4: Author intent-out.json**

```json
{
  "project_id": "uk-domestic-eg01",
  "intent_version": "1.0.0",
  "circuits": [
    {"node_id": "CU-MAIN.C01", "parent_node_id": "CU-MAIN", "designation": "Ground-floor ring final", "phase_csa_mm2_or_awg": "2.5 mm²", "cpc_csa_mm2_or_awg": "1.5 mm²", "material": "copper", "insulation": "pvc_70", "cable_type": "pvc_singles", "parallel_count": 1, "cable_od_mm": 8.4, "weight_kg_per_m": 0.18, "length_m": 32, "installation_method": "B1", "r1_plus_r2_milliohm_per_m_at_operating_temp": 18.1, "reactance_milliohm_per_m": 0.08},
    {"node_id": "CU-MAIN.C02", "parent_node_id": "CU-MAIN", "designation": "First-floor ring final", "phase_csa_mm2_or_awg": "2.5 mm²", "cpc_csa_mm2_or_awg": "1.5 mm²", "material": "copper", "insulation": "pvc_70", "cable_type": "pvc_singles", "parallel_count": 1, "cable_od_mm": 8.4, "weight_kg_per_m": 0.18, "length_m": 28, "installation_method": "B1", "r1_plus_r2_milliohm_per_m_at_operating_temp": 18.1, "reactance_milliohm_per_m": 0.08},
    {"node_id": "CU-MAIN.C03", "parent_node_id": "CU-MAIN", "designation": "Lighting upstairs radial", "phase_csa_mm2_or_awg": "1.5 mm²", "cpc_csa_mm2_or_awg": "1.0 mm²", "material": "copper", "insulation": "pvc_70", "cable_type": "pvc_singles", "parallel_count": 1, "cable_od_mm": 7.2, "weight_kg_per_m": 0.13, "length_m": 22, "installation_method": "A1", "r1_plus_r2_milliohm_per_m_at_operating_temp": 30.3, "reactance_milliohm_per_m": 0.10},
    {"node_id": "CU-MAIN.C04", "parent_node_id": "CU-MAIN", "designation": "Cooker dedicated radial", "phase_csa_mm2_or_awg": "6 mm²", "cpc_csa_mm2_or_awg": "2.5 mm²", "material": "copper", "insulation": "pvc_70", "cable_type": "pvc_singles", "parallel_count": 1, "cable_od_mm": 10.6, "weight_kg_per_m": 0.34, "length_m": 8, "installation_method": "C", "r1_plus_r2_milliohm_per_m_at_operating_temp": 7.95, "reactance_milliohm_per_m": 0.08},
    {"node_id": "CU-MAIN.C05", "parent_node_id": "CU-MAIN", "designation": "Immersion heater dedicated radial", "phase_csa_mm2_or_awg": "2.5 mm²", "cpc_csa_mm2_or_awg": "1.5 mm²", "material": "copper", "insulation": "pvc_70", "cable_type": "pvc_singles", "parallel_count": 1, "cable_od_mm": 8.4, "weight_kg_per_m": 0.18, "length_m": 4, "installation_method": "C", "r1_plus_r2_milliohm_per_m_at_operating_temp": 18.1, "reactance_milliohm_per_m": 0.08}
  ]
}
```

- [ ] **Step 5: Author reasoning.md (8 sections matching rationale.sections)**

Each section 2-4 paragraphs of engineering narrative. Cite BS 7671:2018+A2:2022 App 4 Tables (ampacity), App 12 §G (Vd), Reg 433.1 (Iz ≥ In), Reg 543.1.3 (CPC adiabatic), Table 54.7 (CPC minimum). ~120-200 lines total.

- [ ] **Step 6: Validate**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
python3 -c "
import json, jsonschema, os
ir_schema = json.load(open('electrical/cable-sizing/schemas/cable-sizing-ir.schema.json'))
intent_schema = json.load(open('electrical/cable-sizing/schemas/cable-sizing-intent.schema.json'))
output = json.load(open('electrical/cable-sizing/examples/uk-domestic-final-circuits/output.json'))
intent = json.load(open('electrical/cable-sizing/examples/uk-domestic-final-circuits/intent-out.json'))

base = 'electrical/cable-sizing/schemas/'
resolver = jsonschema.RefResolver(base_uri='file://' + os.path.abspath(base) + '/', referrer=ir_schema)
jsonschema.validate(output, ir_schema, resolver=resolver); print('UK output IR: VALID')
jsonschema.validate(intent, intent_schema); print('UK intent: VALID')

# chat_summary 40-500
cs = output['rationale']['chat_summary']
assert 40 <= len(cs) <= 500, f'chat_summary {len(cs)} out of range'
print(f'chat_summary: {len(cs)} chars')

# 8 sections
assert len(output['rationale']['sections']) == 8
print('8 rationale sections OK')

# Every cascade node has tool_call_pending
for n in output['cascade']:
    assert n['checks']['tool_call_pending'] == True
print('INV-09 OK (all nodes tool_call_pending)')

# Every intent circuit has Zs helpers
for c in intent['circuits']:
    assert 'r1_plus_r2_milliohm_per_m_at_operating_temp' in c
    assert 'reactance_milliohm_per_m' in c
print('INV-10 OK (intent Zs helper fields present)')

# C03 is the Vd binding
c03 = next(n for n in output['cascade'] if n['node_id'] == 'CU-MAIN.C03')
assert c03['selection']['binding_constraint'] == 'vd_cumulative'
assert len(c03['selection']['walk_up_trail']) >= 2
print('C03 lighting Vd binding: OK')
"
```

- [ ] **Step 7: Commit**

```bash
git add electrical/cable-sizing/examples/uk-domestic-final-circuits/
git commit -m "feat(cable-sizing): UK domestic example — 5 final circuits, vd_cumulative binding on lighting radial, copper PVC"
```

---

### Task 8: KE Nairobi commercial example (NEW per refresh)

**Model:** Opus (KE engineering practice + KS 1700:2018 §313 routing form).

**Files (4):**
- Create: `electrical/cable-sizing/examples/ke-nairobi-commercial-with-msb/input.json`
- Create: `electrical/cable-sizing/examples/ke-nairobi-commercial-with-msb/output.json`
- Create: `electrical/cable-sizing/examples/ke-nairobi-commercial-with-msb/intent-out.json`
- Create: `electrical/cable-sizing/examples/ke-nairobi-commercial-with-msb/reasoning.md`

- [ ] **Step 1: Engineering scenario per refresh §3.1**

KE 415V TPN+E KPLC TN-S supply, Ze≈0.45Ω, declared PFC at MSB busbar≈9kA, 60-200 m² Nairobi commercial office.

**Cascade (6 nodes):**

| node_id | designation | node_kind | load_type | Ib (A) | In (A) | length (m) | install | csa expected |
|---|---|---|---|---|---|---|---|---|
| `MSB-1` | Main switchboard incoming | service_entrance | mixed | 250 | 315 | 12 | E | 95 mm² (Cu XLPE) |
| `MSB-1.F01` | Feeder to DB-L1 | feeder | lighting | 30 | 40 | 22 | E | 10 mm² |
| `MSB-1.F02` | Feeder to DB-P1 | sub_feeder | power_general | 65 | 80 | 35 | E | 25 mm² (cumulative-Vd binding) |
| `MSB-1.F03` | Feeder to DB-M1 (HVAC) | feeder | motor | 45 | 63 | 18 | E | 16 mm² |
| `MSB-1.F02.C03` | Remote socket final | final_circuit | power_general | 18 | 20 | 45 | B1 | 4 mm² (Vd binding) |
| `MSB-1.F03.C01` | Chiller pump 7.5 kW | final_circuit | motor | 14.5 | 32 | 18 | C | 6 mm² + motor-starting Vd check |

Expected binding constraints:
- MSB-1, F01, F03 = `iz_vs_in`
- F02 = `vd_cumulative` (sub-feeder Vd already 1.8% — downstream branches will compound)
- F02.C03 = `vd_cumulative` (1.8% feeder + 3.2% branch = 5.0% at limit)
- F03.C01 = `motor_starting_vd` consideration but resolves at 6 mm² with VFD acknowledged as out-of-scope

- [ ] **Step 2: Author input.json**

```json
{
  "project_id": "ke-nairobi-commercial-eg01",
  "jurisdiction": "KE",
  "site_brief": "60-200 m² Nairobi commercial office tenant fit-out. 415V TPN+E KPLC TN-S supply per KS 1700:2018 §313 (routes to BS 7671:2018+A2:2022 §313.1 for short-circuit verification). MSB-1 (315A) → 3 sub-DB feeders (DB-L1 lighting + DB-P1 small-power + DB-M1 HVAC) → final circuits. Cumulative-Vd binding expected on remote small-power circuit and HVAC chiller pump 7.5 kW motor.",
  "supply": {
    "voltage_v": 415,
    "phase_arrangement": "TPN_plus_E",
    "system_type": "TN-S"
  },
  "circuits_declared": [
    {"node_id": "MSB-1", "node_kind": "service_entrance", "designation": "Main switchboard incoming", "load": {"ib_a": 250, "in_a": 315, "phases": "three_phase_4wire", "load_type": "mixed", "pf": 0.92}, "route": {"length_m": 12, "installation_method": "E", "ambient_c": 32, "grouping_count": 1}, "parent_node_ifault_ka": 9.0, "t_clear_s": 0.4},
    {"node_id": "MSB-1.F01", "parent_node_id": "MSB-1", "node_kind": "feeder", "designation": "Feeder to DB-L1 (lighting)", "load": {"ib_a": 30, "in_a": 40, "phases": "three_phase_4wire", "load_type": "lighting", "pf": 0.95}, "route": {"length_m": 22, "installation_method": "E", "ambient_c": 32, "grouping_count": 1}, "parent_node_ifault_ka": 9.0, "t_clear_s": 0.4},
    {"node_id": "MSB-1.F02", "parent_node_id": "MSB-1", "node_kind": "sub_feeder", "designation": "Sub-feeder to DB-P1 (small-power)", "load": {"ib_a": 65, "in_a": 80, "phases": "three_phase_4wire", "load_type": "power_general", "pf": 0.92}, "route": {"length_m": 35, "installation_method": "E", "ambient_c": 32, "grouping_count": 1}, "parent_node_ifault_ka": 9.0, "t_clear_s": 0.4},
    {"node_id": "MSB-1.F03", "parent_node_id": "MSB-1", "node_kind": "feeder", "designation": "Feeder to DB-M1 (HVAC)", "load": {"ib_a": 45, "in_a": 63, "phases": "three_phase_4wire", "load_type": "motor", "pf": 0.85}, "route": {"length_m": 18, "installation_method": "E", "ambient_c": 32, "grouping_count": 1}, "parent_node_ifault_ka": 9.0, "t_clear_s": 0.4},
    {"node_id": "MSB-1.F02.C03", "parent_node_id": "MSB-1.F02", "node_kind": "final_circuit", "designation": "Remote small-power final circuit", "load": {"ib_a": 18, "in_a": 20, "phases": "single", "load_type": "power_general", "pf": 1.0}, "route": {"length_m": 45, "installation_method": "B1", "ambient_c": 30, "grouping_count": 2}, "parent_node_ifault_ka": 7.5, "t_clear_s": 0.4},
    {"node_id": "MSB-1.F03.C01", "parent_node_id": "MSB-1.F03", "node_kind": "final_circuit", "designation": "Chiller pump 7.5 kW DOL", "load": {"ib_a": 14.5, "in_a": 32, "phases": "three_phase_3wire", "load_type": "motor", "pf": 0.85, "load_class_motor": {"rated_kw": 7.5, "lra_factor": 6.5, "design_code": "IEC_AB"}}, "route": {"length_m": 18, "installation_method": "C", "ambient_c": 32, "grouping_count": 1}, "parent_node_ifault_ka": 8.2, "t_clear_s": 0.2}
  ],
  "design_intent": {
    "cable_type_preference": "xlpe"
  }
}
```

- [ ] **Step 3: Author output.json (full IR)**

Build full IR. ALL citations lead with `KS 1700:2018 §X` form; routing notes use explicit `KS 1700:2018 §X routes to BS 7671:2018+A2:2022 §Y` form. NEVER bare `BS 7671 §X` as primary citation. NEVER `"adopted by KS 1700"` annotation form.

Per spec §6.1 KE Vd limits (via KS 1700:2018 §313 routing to BS 7671 App 12): 3% lighting / 5% power.

F02 sub-feeder must be sized to leave headroom for F02.C03 cumulative (Vd at F02 ≤ 1.8% → C03 budget = 3.2%). C03 walk_up_trail shows 2.5 mm² rejected by cumulative Vd (1.8% + 4.0% = 5.8%), 4 mm² accepted (1.8% + 3.2% = 5.0% — at limit).

F03.C01 motor: `checks.motor_starting_vd_pct` = `vd_running × LRA_factor = 1.2% × 6.5 = 7.8%` → passes 10% limit. Documented in reasoning.md §6.

**chat_summary template (≤500 chars):** "Kenya 415V TPN+E commercial office (60-200 m²), KPLC TN-S, Ze=0.45Ω, PSCC=9kA. 6-node cascade per KS 1700:2018 §313 routes to BS 7671:2018+A2:2022 App 4 + App 12. MSB-1 95 mm² Cu XLPE; F01 lighting feeder 10 mm² (iz_vs_in); F02 power sub-feeder 25 mm² (vd_cumulative binding); F03 HVAC feeder 16 mm²; F02.C03 remote final 4 mm² (vd_cumulative); F03.C01 chiller pump 6 mm² motor-starting Vd 7.8%. 3 calc tools pending."

- [ ] **Step 4: Author intent-out.json**

6 circuits matching the cascade. All required intent fields populated including Zs helpers. KE example circuit_ids match the IR's node_ids (use the full hierarchical form e.g., `MSB-1.F02.C03`).

- [ ] **Step 5: Author reasoning.md (8 sections)**

Lead with `KS 1700:2018 §X` citations throughout. Where routing to BS 7671 is explicit, use the routing form `KS 1700:2018 §X routes to BS 7671:2018+A2:2022 §Y`. NEVER use forbidden annotation form `"adopted by KS 1700"`.

~150-250 lines.

- [ ] **Step 6: Validate (including KS 1700 citation audit)**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
python3 -c "
import json, jsonschema, os
ir_schema = json.load(open('electrical/cable-sizing/schemas/cable-sizing-ir.schema.json'))
intent_schema = json.load(open('electrical/cable-sizing/schemas/cable-sizing-intent.schema.json'))
output = json.load(open('electrical/cable-sizing/examples/ke-nairobi-commercial-with-msb/output.json'))
intent = json.load(open('electrical/cable-sizing/examples/ke-nairobi-commercial-with-msb/intent-out.json'))

base = 'electrical/cable-sizing/schemas/'
resolver = jsonschema.RefResolver(base_uri='file://' + os.path.abspath(base) + '/', referrer=ir_schema)
jsonschema.validate(output, ir_schema, resolver=resolver); print('KE output IR: VALID')
jsonschema.validate(intent, intent_schema); print('KE intent: VALID')

assert output['jurisdiction'] == 'KE'

# KS 1700 citation audit
content = json.dumps(output) + open('electrical/cable-sizing/examples/ke-nairobi-commercial-with-msb/reasoning.md').read()
assert 'adopted by KS 1700' not in content, 'FORBIDDEN annotation form'
assert 'KS 1700:2018' in output['rationale']['chat_summary'], 'chat_summary must reference KS 1700:2018'
print('KS 1700 citation form: OK')

# F02 binding = vd_cumulative
f02 = next(n for n in output['cascade'] if n['node_id'] == 'MSB-1.F02')
print(f'F02 binding: {f02[\"selection\"][\"binding_constraint\"]}')

# F03.C01 motor check
c01 = next(n for n in output['cascade'] if n['node_id'] == 'MSB-1.F03.C01')
assert c01['load']['load_type'] == 'motor'
assert c01['checks']['motor_starting_vd_pct'] is not None
print(f'F03.C01 motor_starting_vd: {c01[\"checks\"][\"motor_starting_vd_pct\"]}%')
"
```

- [ ] **Step 7: Commit**

```bash
git add electrical/cable-sizing/examples/ke-nairobi-commercial-with-msb/
git commit -m "feat(cable-sizing): KE Nairobi commercial example — MSB cascade + vd_cumulative + motor-starting + KS 1700:2018 §313 routing"
```

---

### Task 9: INT commercial with feeders example

**Model:** Opus.

**Files (4):**
- Create: `electrical/cable-sizing/examples/intl-commercial-with-feeders/input.json`
- Create: `electrical/cable-sizing/examples/intl-commercial-with-feeders/output.json`
- Create: `electrical/cable-sizing/examples/intl-commercial-with-feeders/intent-out.json`
- Create: `electrical/cable-sizing/examples/intl-commercial-with-feeders/reasoning.md`

- [ ] **Step 1: Engineering scenario**

INT 400V TPN, 3-storey commercial building. TX → MSB → riser → DB-L1 (level 3) → final circuits cascade. ~7 cable runs. XLPE copper feeders + PVC final circuits. Cumulative-Vd binding on the deepest final circuit. Primary citations: IEC 60364-4-41 (overcurrent) + IEC 60364-5-52 (cable sizing) + IEC 60364-5-54 (CPC).

**Cascade (7 nodes):**

| node_id | designation | node_kind | Ib (A) | In (A) | length (m) | install | csa expected |
|---|---|---|---|---|---|---|---|
| `TX-1` | TX secondary (1000 kVA) → MSB | service_entrance | 1450 | 1600 | 8 | F | 2 × 500 mm² parallel (Cu XLPE) |
| `MSB-1.F-RISER` | Riser feeder MSB → riser DB | feeder | 320 | 400 | 25 (riser) | E | 185 mm² (Cu XLPE) |
| `RISER.L1` | Level 1 sub-DB | sub_feeder | 80 | 100 | 8 (tap-off) | E | 35 mm² |
| `RISER.L2` | Level 2 sub-DB | sub_feeder | 110 | 125 | 8 | E | 50 mm² |
| `RISER.L3` | Level 3 sub-DB | sub_feeder | 130 | 160 | 8 | E | 70 mm² (cumulative-Vd binding) |
| `RISER.L3.C04` | Long L3 final circuit | final_circuit | 16 | 20 | 38 | B1 | 4 mm² (Vd binding — riser already 1.5%) |
| `RISER.L3.C07` | L3 IT load 3-phase 4W (server rack) | final_circuit | 24 | 32 | 18 | B1 | 6 mm² + 4 mm² N upsized due to 30% h3 |

C07 demonstrates harmonic_content_pct=30 + 3-phase 4-wire → Ch derating + neutral sizing rule.

- [ ] **Step 2-5: Author input + output + intent-out + reasoning files**

Per Task 7 template, with INT-specific deltas:
- `jurisdiction: "INT"`, `voltage_v: 400`, `phase_arrangement: "TPN_plus_E"`
- All primary citations lead with `IEC 60364-X-XX:YYYY §Z` form
- NEVER cite BS 7671 (acceptable: BS EN 60529 device standard, BS EN 12464-1 — not LV code)
- NEVER cite NEC
- TX-1 demonstrates parallel_count=2 (2× 500 mm² for 1450A — single 630 mm² insufficient)
- RISER.L3.C07 has `harmonic_content_pct: 30` and demonstrates Ch derating (Ch=0.86 per IEC 60364-5-52 Annex E §E.5)

**chat_summary template (≤500 chars):** "INT 400V TPN+E commercial 3-storey building. TX 1000 kVA secondary → MSB → riser → 3 floors of sub-DBs per IEC 60364-5-52:2009 §G + Annex E. 7-node cascade. TX-1: 2 × 500 mm² parallel Cu XLPE (iz_vs_in). Riser 185 mm² (iz_vs_in). L3 sub-feeder 70 mm² (vd_cumulative). Long L3 final 4 mm² (vd_cumulative — riser 1.5% + branch 3.5%). L3 IT rack 6 mm² with 30% h3 Ch derating + 4 mm² neutral upsized per Annex E.5. 3 calc tools pending."

- [ ] **Step 6: Validate**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
python3 -c "
import json, jsonschema, os
ir_schema = json.load(open('electrical/cable-sizing/schemas/cable-sizing-ir.schema.json'))
intent_schema = json.load(open('electrical/cable-sizing/schemas/cable-sizing-intent.schema.json'))
output = json.load(open('electrical/cable-sizing/examples/intl-commercial-with-feeders/output.json'))
intent = json.load(open('electrical/cable-sizing/examples/intl-commercial-with-feeders/intent-out.json'))

base = 'electrical/cable-sizing/schemas/'
resolver = jsonschema.RefResolver(base_uri='file://' + os.path.abspath(base) + '/', referrer=ir_schema)
jsonschema.validate(output, ir_schema, resolver=resolver); print('INT output IR: VALID')
jsonschema.validate(intent, intent_schema); print('INT intent: VALID')

assert output['jurisdiction'] == 'INT'

# No NEC or BS 7671 primary citations in chat_summary
cs = output['rationale']['chat_summary']
assert 'NEC' not in cs and 'BS 7671' not in cs.replace('BS EN', '')

# Parallel cables demonstrated (TX-1)
tx = next(n for n in output['cascade'] if n['node_id'] == 'TX-1')
assert tx['selection']['parallel_count'] >= 2
assert tx['selection']['binding_constraint'] == 'parallel_required' or tx['selection']['parallel_count'] == 2
print('TX-1 parallel_count =', tx['selection']['parallel_count'])

# Harmonic derating on L3.C07
c07 = next(n for n in output['cascade'] if n['node_id'] == 'RISER.L3.C07')
assert c07['harmonic_content_pct'] >= 15
assert c07['checks'].get('harmonic_ch_applied', 1.0) < 1.0
print('L3.C07 harmonic_ch_applied:', c07['checks']['harmonic_ch_applied'])
"
```

- [ ] **Step 7: Commit**

```bash
git add electrical/cable-sizing/examples/intl-commercial-with-feeders/
git commit -m "feat(cable-sizing): INT commercial example — 7-node TX → MSB → riser cascade, parallel cables, harmonic derating, vd_cumulative binding"
```

---

### Task 10: US industrial with motors example

**Model:** Opus.

**Files (4):**
- Create: `electrical/cable-sizing/examples/us-industrial-with-motors/input.json`
- Create: `electrical/cable-sizing/examples/us-industrial-with-motors/output.json`
- Create: `electrical/cable-sizing/examples/us-industrial-with-motors/intent-out.json`
- Create: `electrical/cable-sizing/examples/us-industrial-with-motors/reasoning.md`

- [ ] **Step 1: Engineering scenario**

US 480V 3-phase industrial facility. 1200A service entrance + 500 hp motor + aluminium feeder demonstrating AWG sizing + terminal-temp cap + parallel cables.

**Cascade (5 nodes):**

| node_id | designation | node_kind | Ib (A) | In (A) | length (m) | install | csa expected |
|---|---|---|---|---|---|---|---|
| `SERVICE.1200A` | 1200A service entrance | service_entrance | 950 | 1200 | 3 | E | 4 × 350 kcmil parallel Cu THWN-2 |
| `MCC-1.F01` | Feeder to MCC-1 | feeder | 320 | 400 | 30 | nec_cable_tray | 600 kcmil Al XHHW-2 |
| `MCC-1.M01` | 500 hp motor M01 | final_circuit | 590 | 700 | 25 | nec_conduit | 2 × 350 kcmil parallel Cu THWN-2 + motor-starting Vd |
| `MCC-1.M02` | 200 hp pump M02 | final_circuit | 240 | 300 | 18 | nec_conduit | 350 kcmil Cu THWN-2 |
| `MCC-1.F02.B01` | Receptacle branch | final_circuit | 16 | 20 | 22 | nec_conduit | 12 AWG Cu THWN-2 |

Demonstrations:
- AWG + kcmil sizing per NEC Chapter 9 Table 9 + Article 310.16
- Aluminium feeder (MCC-1.F01) — 600 kcmil Al ≈ same ampacity as 350 kcmil Cu at 90°C (terminal cap 75°C)
- Terminal-temperature cap per NEC 110.14(C) (caps ampacity column at 75°C)
- Parallel cables at SERVICE.1200A and MCC-1.M01 (NEC 310.10(H)(1) minimum 1/0 AWG)
- Motor-starting Vd check on MCC-1.M01: vd_running × LRA_factor (NEMA Design B = 6.0)
- Primary citations: NEC 2023 Article 240.4(B) + 250.122 + 215.2(A)(1) + 220.40 + 310.16 + 110.14(C)

- [ ] **Step 2-5: Author input + output + intent-out + reasoning**

Per Task 7 template, with US-specific deltas:
- `jurisdiction: "US"`, `voltage_v: 480`, `phase_arrangement: "TPN"` (3-phase 480V industrial; not split-phase)
- ALL primary citations lead with `NEC 2023 Article X` form
- NEVER cite BS 7671 or IEC 60364 as primary
- `csa` fields use AWG/kcmil strings (e.g., "350 kcmil", "12 AWG", "1/0 AWG")
- `material: "aluminium"` on MCC-1.F01 (with appropriate density-correction Iz)
- `insulation: "thwn_2_90"` or `"xhhw_2_90"` (NEC-specific)
- `installation_method: "nec_cable_tray"` or `"nec_conduit"`
- terminal_temp_rating_c: 75 per NEC 110.14(C)
- Motor M01: `load.load_class_motor: {rated_kw: 373 (500 hp ≈ 373 kW), lra_factor: 6.0, design_code: "NEMA_B"}`. motor_starting_vd_pct ≈ 8.5% (within 10% limit)

**chat_summary template (≤500 chars):** "US 480V 3-phase industrial facility per NEC 2023 Article 240.4(B) + 250.122 + 220.40. 5-node cascade. Service entrance 1200A: 4 × 350 kcmil parallel Cu THWN-2 (parallel_required, NEC 310.10(H)(1) ≥1/0 AWG). MCC-1 feeder 600 kcmil Al XHHW-2 (iz_vs_in capped by 75°C terminal per NEC 110.14(C)). M01 500 hp 2 × 350 kcmil parallel + motor-starting Vd 8.5% (NEMA B LRA=6). M02 350 kcmil. B01 12 AWG receptacle. 3 calc tools pending."

- [ ] **Step 6: Validate**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
python3 -c "
import json, jsonschema, os
ir_schema = json.load(open('electrical/cable-sizing/schemas/cable-sizing-ir.schema.json'))
intent_schema = json.load(open('electrical/cable-sizing/schemas/cable-sizing-intent.schema.json'))
output = json.load(open('electrical/cable-sizing/examples/us-industrial-with-motors/output.json'))
intent = json.load(open('electrical/cable-sizing/examples/us-industrial-with-motors/intent-out.json'))

base = 'electrical/cable-sizing/schemas/'
resolver = jsonschema.RefResolver(base_uri='file://' + os.path.abspath(base) + '/', referrer=ir_schema)
jsonschema.validate(output, ir_schema, resolver=resolver); print('US output IR: VALID')
jsonschema.validate(intent, intent_schema); print('US intent: VALID')

assert output['jurisdiction'] == 'US'

# No BS 7671 or IEC 60364 primary citations
cs = output['rationale']['chat_summary']
assert 'BS 7671' not in cs and 'IEC 60364' not in cs

# Parallel demonstrated
service = next(n for n in output['cascade'] if n['node_id'] == 'SERVICE.1200A')
assert service['selection']['parallel_count'] >= 2
print(f'SERVICE.1200A parallel: {service[\"selection\"][\"parallel_count\"]}')

# Aluminium feeder
mcc_feeder = next(n for n in output['cascade'] if n['node_id'] == 'MCC-1.F01')
assert mcc_feeder['selection']['material'] == 'aluminium'
print(f'MCC-1.F01 material: {mcc_feeder[\"selection\"][\"material\"]}')

# Motor M01
m01 = next(n for n in output['cascade'] if n['node_id'] == 'MCC-1.M01')
assert m01['load']['load_type'] == 'motor'
assert m01['checks']['motor_starting_vd_pct'] is not None
print(f'M01 motor-starting Vd: {m01[\"checks\"][\"motor_starting_vd_pct\"]}%')
"
```

- [ ] **Step 7: Commit**

```bash
git add electrical/cable-sizing/examples/us-industrial-with-motors/
git commit -m "feat(cable-sizing): US industrial example — 1200A parallel + aluminium feeder + 500 hp motor + AWG/kcmil sizing per NEC 2023"
```

---

## Phase D — Ontology + Rules + Constraints + Validation + Evals (Tasks 11-15)

### Task 11: Ontology (cable-types + installation-methods)

**Model:** Sonnet (mechanical lookup tables).

**Files (2):**
- Create: `electrical/cable-sizing/ontology/cable-types.json`
- Create: `electrical/cable-sizing/ontology/installation-methods.json`

- [ ] **Step 1: Write cable-types.json**

```json
{
  "_title": "Cable Types — Multi-Jurisdiction Reference",
  "_purpose": "Engine-lookupable ontology of cable types consumed by cable-sizing, cable-schedule, riser, cable-containment skills",
  "transcribed_at": "2026-05-20",
  "transcribed_by": "DraftsMan skills repo",
  "verification_status": "verified-against-source",
  "cable_types": {
    "pvc_singles":     {"description": "PVC insulated singles drawn into conduit/trunking", "jurisdiction": ["GB","KE","INT","EU"], "operating_temp_c": 70, "insulation_standard": "BS 6004 / IEC 60227", "max_csa_mm2": 400},
    "pvc_multicore":   {"description": "PVC insulated multicore cable (T+E / NYM)", "jurisdiction": ["GB","KE","INT","EU"], "operating_temp_c": 70, "insulation_standard": "BS 6004 / IEC 60227"},
    "xlpe_swa":        {"description": "XLPE insulated steel-wire-armoured cable", "jurisdiction": ["GB","KE","INT","EU"], "operating_temp_c": 90, "insulation_standard": "BS 5467 / IEC 60502-1"},
    "xlpe_lszh":       {"description": "XLPE insulated LSZH cable", "jurisdiction": ["GB","KE","INT","EU"], "operating_temp_c": 90, "insulation_standard": "BS 7211 / IEC 60332-1"},
    "epr_swa":         {"description": "EPR insulated steel-wire-armoured cable (offshore/marine grade)", "jurisdiction": ["GB","KE","INT","EU"], "operating_temp_c": 90, "insulation_standard": "BS 6883 / IEC 60092-353"},
    "mineral_micc":    {"description": "Mineral-insulated copper-covered cable (Pyro)", "jurisdiction": ["GB","KE","INT","EU"], "operating_temp_c": 90, "insulation_standard": "BS EN 60702"},
    "fp200_lszh":      {"description": "Fire-rated 2-hour cable (FP200 family)", "jurisdiction": ["GB","KE"], "operating_temp_c": 90, "insulation_standard": "BS EN 50200"},
    "cwz_glass_mica":  {"description": "Fire-rated 3-hour CWZ-class cable", "jurisdiction": ["GB","KE"], "operating_temp_c": 90, "insulation_standard": "BS 6387"},
    "thwn_2":          {"description": "Thermoplastic heat-resistant water-resistant, 90°C wet/dry", "jurisdiction": ["US"], "operating_temp_c": 90, "insulation_standard": "UL 83"},
    "thhn":            {"description": "Thermoplastic heat-resistant nylon, 90°C dry / 75°C wet", "jurisdiction": ["US"], "operating_temp_c": 90, "insulation_standard": "UL 83"},
    "xhhw_2":          {"description": "Cross-linked polyethylene high heat resistant water resistant, 90°C wet/dry", "jurisdiction": ["US"], "operating_temp_c": 90, "insulation_standard": "UL 44"}
  },
  "engine_lookup": {
    "_purpose": "Flat lookup by cable_type → operating_temp + jurisdiction set",
    "by_type": {
      "pvc_singles":   {"operating_temp_c": 70, "jurisdiction_set": ["GB","KE","INT","EU"]},
      "xlpe_swa":      {"operating_temp_c": 90, "jurisdiction_set": ["GB","KE","INT","EU"]},
      "thwn_2":        {"operating_temp_c": 90, "jurisdiction_set": ["US"]},
      "xhhw_2":        {"operating_temp_c": 90, "jurisdiction_set": ["US"]}
    }
  },
  "_cross_refs": []
}
```

- [ ] **Step 2: Write installation-methods.json**

```json
{
  "_title": "Cable Installation Methods — Multi-Jurisdiction Reference",
  "_purpose": "Engine-lookupable ontology of installation methods consumed by cable-sizing for ampacity table column selection",
  "transcribed_at": "2026-05-20",
  "transcribed_by": "DraftsMan skills repo",
  "verification_status": "verified-against-source",
  "installation_methods": {
    "A1": {"description": "Insulated conductors in conduit in thermally insulated wall", "jurisdiction": ["GB","KE","INT","EU"], "standard": "BS 7671:2018+A2:2022 Reg 521 / IEC 60364-5-52 §521"},
    "A2": {"description": "Multicore cable in conduit in thermally insulated wall", "jurisdiction": ["GB","KE","INT","EU"], "standard": "BS 7671:2018+A2:2022 Reg 521"},
    "B1": {"description": "Insulated conductors in conduit on a wall", "jurisdiction": ["GB","KE","INT","EU"], "standard": "BS 7671:2018+A2:2022 Reg 521"},
    "B2": {"description": "Multicore cable in conduit on a wall", "jurisdiction": ["GB","KE","INT","EU"], "standard": "BS 7671:2018+A2:2022 Reg 521"},
    "C":  {"description": "Single layer multicore cables clipped direct to a wall", "jurisdiction": ["GB","KE","INT","EU"], "standard": "BS 7671:2018+A2:2022 Reg 521"},
    "D1": {"description": "Multicore cable in conduit, buried in the ground", "jurisdiction": ["GB","KE","INT","EU"], "standard": "BS 7671:2018+A2:2022 Reg 521"},
    "D2": {"description": "Multicore cable buried direct in the ground", "jurisdiction": ["GB","KE","INT","EU"], "standard": "BS 7671:2018+A2:2022 Reg 521"},
    "E":  {"description": "Multicore cable in free air (on cable tray or perforated tray)", "jurisdiction": ["GB","KE","INT","EU"], "standard": "BS 7671:2018+A2:2022 Reg 521"},
    "F":  {"description": "Single-core cables in free air (touching)", "jurisdiction": ["GB","KE","INT","EU"], "standard": "BS 7671:2018+A2:2022 Reg 521"},
    "G":  {"description": "Single-core cables in free air (spaced)", "jurisdiction": ["GB","KE","INT","EU"], "standard": "BS 7671:2018+A2:2022 Reg 521"},
    "nec_conduit":         {"description": "Conductors in conduit (raceway)", "jurisdiction": ["US"], "standard": "NEC 2023 Article 310.16 + Chapter 9 Table 1"},
    "nec_cable_tray":      {"description": "Cables in cable tray", "jurisdiction": ["US"], "standard": "NEC 2023 Article 392"},
    "nec_direct_burial":   {"description": "Direct-buried cable (Type USE / UF)", "jurisdiction": ["US"], "standard": "NEC 2023 Article 340 + 339"},
    "nec_free_air":        {"description": "Conductors in free air (single conductors, exposed)", "jurisdiction": ["US"], "standard": "NEC 2023 Article 310.17"}
  },
  "engine_lookup": {
    "_purpose": "Method → ampacity-table-column lookup by jurisdiction",
    "by_method": {
      "B1": {"bs7671_app4_column": "Table 4D1A method B1", "iec_table": "Table B.52.4 method B1"},
      "C":  {"bs7671_app4_column": "Table 4D2A method C",  "iec_table": "Table B.52.4 method C"},
      "E":  {"bs7671_app4_column": "Table 4D1A method E",  "iec_table": "Table B.52.4 method E"},
      "nec_conduit":    {"nec_table": "Table 310.16 raceway"},
      "nec_cable_tray": {"nec_table": "Article 392 free-air ampacity"}
    }
  },
  "_cross_refs": []
}
```

- [ ] **Step 3: Validate + commit**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
python3 -c "
import json
ct = json.load(open('electrical/cable-sizing/ontology/cable-types.json'))
im = json.load(open('electrical/cable-sizing/ontology/installation-methods.json'))
assert len(ct['cable_types']) >= 10
assert len(im['installation_methods']) == 14  # 10 IEC + 4 NEC
print(f'cable-types: {len(ct[\"cable_types\"])} types; installation-methods: {len(im[\"installation_methods\"])} methods')
"
git add electrical/cable-sizing/ontology/
git commit -m "feat(cable-sizing): ontology — cable-types (11 entries) + installation-methods (10 IEC + 4 NEC)"
```

---

### Task 12: Rules (5 YAMLs)

**Model:** Sonnet.

**Files (5):**
- Create: `electrical/cable-sizing/rules/csa-selection-walk-up.yaml`
- Create: `electrical/cable-sizing/rules/voltage-drop-targets.yaml`
- Create: `electrical/cable-sizing/rules/correction-factor-stack.yaml`
- Create: `electrical/cable-sizing/rules/parallel-cables-threshold.yaml`
- Create: `electrical/cable-sizing/rules/harmonic-derating-trigger.yaml`

- [ ] **Step 1: Read fault-level rules/peak-factor-kappa.yaml as YAML structure template**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
cat electrical/fault-level/rules/peak-factor-kappa.yaml
```

- [ ] **Step 2: Write all 5 rules YAMLs**

Each file uses this structure:
```yaml
# <rule category> rules for cable-sizing per jurisdiction
# Consumed by generator (Step N) + validator (INV-NN)

rules:
  - id: <RULE-ID>
    jurisdiction: [<GB|KE|INT|US|all>]
    standard_reference: "<full citation>"
    rule_text: "<engineering rule statement>"
    applies_to: "<cascade_node|circuit>"
    enforcement: "<algorithm_step|hard_fail|warning|info>"
```

**csa-selection-walk-up.yaml — 6 rules:**
- WALK-01: Start csa = smallest where Iz_tabulated × correction_factors ≥ In (all)
- WALK-02: Walk-up condition = any of {iz_vs_in, vd_cumulative, motor_starting_vd, cpc_adiabatic, harmonic_derating} fails (all)
- WALK-03: Accept condition = all 5 checks pass at current csa (all)
- WALK-04: binding_constraint = the rejection reason at csa_one_below_selected (all)
- WALK-05: NEC terminal-temp cap after Ca × Cg correction per NEC 110.14(C) (US)
- WALK-06: Standard mm² ladder = [1.0, 1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240, 300, 400, 500, 630] (GB/EU/INT/KE); AWG/kcmil ladder per NEC Chapter 9 Table 8 (US)

**voltage-drop-targets.yaml — 6 rules:**
- VD-01: GB lighting limit 3% per BS 7671:2018+A2:2022 App 12 (GB)
- VD-02: GB power limit 5% per BS 7671:2018+A2:2022 App 12 (GB)
- VD-03: KE limits route to GB per KS 1700:2018 §313 routes to BS 7671:2018+A2:2022 App 12 (KE)
- VD-04: INT/EU 3% lighting / 5% power per IEC 60364-5-52:2009 §G (INT, EU)
- VD-05: US feeder-only 3% / feeder+branch 5% per NEC 2023 Article 215.2(A)(1) Informational Note 2 (US)
- VD-06: vd_target_overrides[node_id] takes precedence when client spec is tighter (all)

**correction-factor-stack.yaml — 5 rules:**
- CF-01: Stack order = Ca × Cg × Ci × Ch (all)
- CF-02: Ca per ambient temp per BS 7671 App 4 §4 / IEC 60364-5-52 §B.52 (GB, KE, INT, EU)
- CF-03: Cg per grouping count per BS 7671 App 4 Table 4C / IEC 60364-5-52 Table B.52.17 (GB, KE, INT, EU)
- CF-04: Ci = 0.5 when in_thermal_insulation == true per BS 7671 App 4 §4 (GB, KE, INT, EU)
- CF-05: US correction = Ca × Cg per NEC 2023 Article 310.15(B)(1) + (B)(3)(a) (US)

**parallel-cables-threshold.yaml — 4 rules:**
- PAR-01: Engage parallel when single-cable ladder exhausted at largest csa with Iz < In (all)
- PAR-02: Minimum csa per parallel = 50 mm² per IEC 60364-5-52 §523.6 (GB, KE, INT, EU)
- PAR-03: Minimum csa per parallel = 1/0 AWG per NEC 2023 Article 310.10(H)(1) (US)
- PAR-04: All parallels MUST match on length + csa + material + installation (symmetric impedances) (all)

**harmonic-derating-trigger.yaml — 5 rules:**
- HARM-01: Trigger when harmonic_content_pct > 15 AND load.phases == "three_phase_4wire" (all)
- HARM-02: Ch lookup GB per BS 7671:2018+A2:2022 App 4 §5.5 Table 4Ab (GB)
- HARM-03: Ch lookup INT per IEC 60364-5-52:2009 Annex E §E.5 (INT, EU)
- HARM-04: Neutral upsized to phase when h3 > 33% per BS 7671 Reg 523.6.3 / IEC 60364-5-52 §523.6.3 (GB, KE, INT, EU)
- HARM-05: Ch lookup US per NEC 2023 Article 310.15(E); neutral upsized when h3 > 50% per NEC 220.61(C)(2) (US)

- [ ] **Step 3: Validate + commit**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
python3 -c "
import yaml, glob
files = sorted(glob.glob('electrical/cable-sizing/rules/*.yaml'))
assert len(files) == 5
total = 0
for f in files:
    d = yaml.safe_load(open(f))
    n = len(d['rules'])
    total += n
    print(f'{f}: {n} rules')
print(f'Total: {total} rules')
"
git add electrical/cable-sizing/rules/
git commit -m "feat(cable-sizing): 5 rules YAMLs — walk-up + Vd targets + correction stack + parallel + harmonic"
```

---

### Task 13: Constraints (4 YAMLs)

**Model:** Sonnet.

**Files (4):**
- Create: `electrical/cable-sizing/constraints/iz-vs-in-vs-ib.yaml`
- Create: `electrical/cable-sizing/constraints/vd-cumulative-limit.yaml`
- Create: `electrical/cable-sizing/constraints/cpc-adiabatic-passes.yaml`
- Create: `electrical/cable-sizing/constraints/motor-starting-vd-limit.yaml`

- [ ] **Step 1: Write all 4 constraint YAMLs**

Each follows:
```yaml
# <constraint name> for cable-sizing IR
# Hard checks (or warnings) enforced by validator

constraints:
  - id: <ID>
    description: <plain English>
    rule: <expression>
    enforcement: <hard_fail|warning>
    matches_inv: <INV-NN>
    standards: ["<citation>"]
```

**iz-vs-in-vs-ib.yaml:**
- IZ-01: `for each node: node.load.ib_a ≤ node.load.in_a ≤ node.checks.iz_corrected_a` — hard_fail — INV-04 — BS 7671:2018+A2:2022 Reg 433.1 / IEC 60364-4-43 §433.1 / NEC 2023 Article 240.4(B)

**vd-cumulative-limit.yaml:**
- VDC-01: `for each node: node.checks.vd_cumulative_pct ≤ node.checks.vd_limit_pct` — hard_fail — INV-05 — BS 7671:2018+A2:2022 App 12 / IEC 60364-5-52:2009 §G / NEC 2023 Article 215.2(A)(1) IN 2
- VDC-02: `for each leaf node: vd_cumulative_pct == sum(parent_chain.vd_segment_pct) within ±0.05% tolerance` — hard_fail — math integrity

**cpc-adiabatic-passes.yaml:**
- CPC-01: `for each node: node.checks.cpc_adiabatic_pass == true` OR `node.selection.binding_constraint == "cpc_adiabatic"` (phase upsized) — hard_fail — INV-06 — BS 7671:2018+A2:2022 Reg 543.1.3 / IEC 60364-5-54 §543 / NEC 2023 Article 250.122
- CPC-02: `S = sqrt(I²t) / k` formula reference — informational — IEC 60364-5-54 §543.1.2

**motor-starting-vd-limit.yaml:**
- MS-01: `for each motor node: node.checks.motor_starting_vd_pct ≤ 10.0` — warning (engineer may resolve with VFD/soft-start) — INV-07 — BS 7671:2018+A2:2022 §525.1 + Table 4Ab note 5 / IEC 60364-5-52 §525.1 / NEC 2023 Article 430.6(A)(1) + NEMA MG-1
- MS-02: `for each motor node: load_class_motor.lra_factor populated when load_type == motor` — hard_fail — INV-07

- [ ] **Step 2: Validate + commit**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
python3 -c "
import yaml, glob
files = sorted(glob.glob('electrical/cable-sizing/constraints/*.yaml'))
assert len(files) == 4
total = 0
for f in files:
    d = yaml.safe_load(open(f))
    n = len(d['constraints'])
    total += n
    print(f'{f}: {n} constraints')
print(f'Total: {total} constraints')
"
git add electrical/cable-sizing/constraints/
git commit -m "feat(cable-sizing): 4 constraints YAMLs — iz vs in vs ib + cumulative Vd + CPC adiabatic + motor-starting Vd"
```

---

### Task 14: Validation (4 YAMLs, 12 checks)

**Model:** Sonnet.

**Files (4):**
- Create: `electrical/cable-sizing/validation/cascade-tree-integrity.yaml`
- Create: `electrical/cable-sizing/validation/csa-on-standard-ladder.yaml`
- Create: `electrical/cable-sizing/validation/tool-call-resolved.yaml`
- Create: `electrical/cable-sizing/validation/intent-shape.yaml`

- [ ] **Step 1: Write all 4 validation YAMLs**

Pattern (each entry):
```yaml
validations:
  - id: <ID>
    description: <plain English>
    rule: <expression>
    enforcement: <hard_fail|warning>
    matches_inv: <INV-NN>
    fail_message: <template>
```

**cascade-tree-integrity.yaml — 4 checks:**
- TREE-01: All node_ids unique
- TREE-02: Every non-root node parent_node_id resolves
- TREE-03: No cycles (parent_node_id never points to a descendant)
- TREE-04: Exactly one or more root nodes (no parent_node_id field)

**csa-on-standard-ladder.yaml — 4 checks:**
- LAD-01: Every selection.phase_csa on IEC mm² ladder for GB/EU/INT/KE jurisdictions
- LAD-02: Every selection.cpc_csa on IEC mm² ladder for GB/EU/INT/KE
- LAD-03: Every selection.phase_csa on AWG/kcmil ladder for US
- LAD-04: parallel_count is integer in [1, 6] inclusive

**tool-call-resolved.yaml — 1 check:**
- TC-01: All nodes have checks.tool_call_pending == true OR all 3 calc outputs populated (iz_corrected_a, vd_cumulative_pct, cpc_adiabatic_pass). Hard fail on mixed state. — INV-09

**intent-shape.yaml — 3 checks (extended per refresh §2):**
- INT-01: Emitted intent validates against cable-sizing-intent.schema.json
- INT-02: Every final-circuit cascade node appears in intent.circuits[]
- INT-03: Every intent.circuits[] entry has `r1_plus_r2_milliohm_per_m_at_operating_temp` AND `reactance_milliohm_per_m` populated (per refresh §1.4 — required on every circuit, populated from standards tables based on selected csa + insulation + material) — INV-10

- [ ] **Step 2: Validate + commit**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
python3 -c "
import yaml, glob
files = sorted(glob.glob('electrical/cable-sizing/validation/*.yaml'))
assert len(files) == 4
total = 0
for f in files:
    d = yaml.safe_load(open(f))
    n = len(d['validations'])
    total += n
    print(f'{f}: {n} checks')
print(f'Total: {total} checks (target 12)')
assert total == 12, f'expected 12, got {total}'
"
git add electrical/cable-sizing/validation/
git commit -m "feat(cable-sizing): 4 validation YAMLs (12 checks) — cascade tree + csa ladder + tool-call + intent shape with Zs helpers"
```

---

### Task 15: 9 eval YAMLs + runner-config

**Model:** Opus (each eval is a precise assertion contract).

**Files (10):**
- Create: `electrical/cable-sizing/evals/runner-config.yaml`
- Create: `electrical/cable-sizing/evals/eval-01-uk-domestic-happy-path.yaml`
- Create: `electrical/cable-sizing/evals/eval-02-tpn-commercial-cumulative-vd.yaml`
- Create: `electrical/cable-sizing/evals/eval-03-undersized-cable-trap.yaml`
- Create: `electrical/cable-sizing/evals/eval-04-missing-route-data.yaml`
- Create: `electrical/cable-sizing/evals/eval-05-jurisdiction-us-with-awg.yaml`
- Create: `electrical/cable-sizing/evals/eval-06-rationale-block.yaml`
- Create: `electrical/cable-sizing/evals/eval-07-motor-starting-vd.yaml`
- Create: `electrical/cable-sizing/evals/eval-08-parallel-cables.yaml`
- Create: `electrical/cable-sizing/evals/eval-09-harmonic-derating-data-centre.yaml`

- [ ] **Step 1: Read SLD v1.5 eval template**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
cat electrical/sld/evals/eval-08-multi-skill-intent-consumption.yaml
```

- [ ] **Step 2: Write runner-config.yaml**

```yaml
skill: electrical/cable-sizing
schema_paths:
  ir: electrical/cable-sizing/schemas/cable-sizing-ir.schema.json
  intent: electrical/cable-sizing/schemas/cable-sizing-intent.schema.json
eval_order:
  - eval-01-uk-domestic-happy-path
  - eval-02-tpn-commercial-cumulative-vd
  - eval-03-undersized-cable-trap
  - eval-04-missing-route-data
  - eval-05-jurisdiction-us-with-awg
  - eval-06-rationale-block
  - eval-07-motor-starting-vd
  - eval-08-parallel-cables
  - eval-09-harmonic-derating-data-centre
required_categories:
  - happy_path
  - edge_case
  - validation_trap
  - missing_input
  - jurisdiction_switch
  - rationale_block
  - skill_specific
```

- [ ] **Step 3: Write 9 eval YAMLs (SLD v1.5 pattern: assertion + severity + description, flat checks[])**

Each eval shape:
```yaml
name: eval-NN-<slug>
skill: electrical/cable-sizing
description: |
  <what fixture tests, what assertion contract>
category: <happy_path|edge_case|validation_trap|missing_input|jurisdiction_switch|rationale_block|skill_specific>
input_fixtures:
  - ../examples/<example-folder>/output.json

checks:
  - assertion: "<expression that evaluates to bool>"
    description: <plain English>
    severity: <critical|warning|info>
```

Per spec §9:

**eval-01-uk-domestic-happy-path** (happy_path) — UK 5-circuit cascade, all schema-valid, all INV pass, C03 binding=vd_cumulative, all tool_call_pending=true.

**eval-02-tpn-commercial-cumulative-vd** (edge_case) — INT 7-node cascade, cumulative-Vd binding at deep leaf, RISER.L3.C04 cumulative_vd_pct ≤ 5.0% strictly.

**eval-03-undersized-cable-trap** (validation_trap) — Synthetic fixture: take uk-domestic output.json, modify CU-MAIN.C03.selection.phase_csa from 1.5 to 1.0 (revert to undersized). Validator MUST flag INV-05 (vd_cumulative).

**eval-04-missing-route-data** (missing_input) — Synthetic fixture: drop route.length_m from one node. Validator MUST tag tool_call_pending=true and produce non_compliance_flags with severity=info.

**eval-05-jurisdiction-us-with-awg** (jurisdiction_switch) — US 5-node cascade, all csa strings match AWG/kcmil ladder, aluminium feeder demonstrates material switch, no BS 7671 or IEC 60364 primary citations.

**eval-06-rationale-block** (rationale_block) — All 4 example outputs validate: 8 sections in exact order, all section.summary ≤ 400 chars, chat_summary 40-500 chars.

**eval-07-motor-starting-vd** (skill_specific) — KE F03.C01 + US M01 both: load_type=motor, motor_starting_vd_pct populated, motor_starting_vd_pass=true (within 10% limit).

**eval-08-parallel-cables** (skill_specific) — INT TX-1 + US SERVICE.1200A + US MCC-1.M01 all: parallel_count ≥ 2, each parallel ≥ 50 mm² (IEC) or ≥ 1/0 AWG (US).

**eval-09-harmonic-derating-data-centre** (skill_specific) — INT RISER.L3.C07: harmonic_content_pct ≥ 15, load.phases = three_phase_4wire, harmonic_ch_applied < 1.0.

Example concrete shape for eval-01:
```yaml
name: eval-01-uk-domestic-happy-path
skill: electrical/cable-sizing
description: |
  WI5 happy-path coverage for the UK domestic example. Verifies a complete,
  spec-conformant IR: schema validates, all 10 INV pass, 5 cascade nodes,
  C03 lighting Vd-cumulative binding, every node tool_call_pending: true.
category: happy_path
input_fixtures:
  - ../examples/uk-domestic-final-circuits/output.json

checks:
  - assertion: "schema_valid(output, 'electrical/cable-sizing/schemas/cable-sizing-ir.schema.json')"
    description: cable-sizing-ir.schema.json strict validation passes
    severity: critical

  - assertion: "output.jurisdiction == 'GB'"
    description: UK example carries jurisdiction == 'GB'
    severity: critical

  - assertion: "len(output.cascade) == 5"
    description: Five cascade nodes in UK domestic example
    severity: critical

  - assertion: "next(n for n in output.cascade if n.node_id == 'CU-MAIN.C03').selection.binding_constraint == 'vd_cumulative'"
    description: C03 lighting circuit binds on vd_cumulative
    severity: critical
    matches_inv: INV-05

  - assertion: "all(n.checks.tool_call_pending == True for n in output.cascade)"
    description: Every cascade node has tool_call_pending true (WI3 deferral)
    severity: critical
    matches_inv: INV-09

  - assertion: "all(n.checks.iz_corrected_a >= n.load.in_a for n in output.cascade)"
    description: Iz ≥ In for every node (INV-04)
    severity: critical
    matches_inv: INV-04

  - assertion: "all(n.checks.vd_cumulative_pct <= n.checks.vd_limit_pct for n in output.cascade)"
    description: Cumulative Vd ≤ limit for every node (INV-05)
    severity: critical
    matches_inv: INV-05

  - assertion: "40 <= len(output.rationale.chat_summary) <= 500"
    description: chat_summary 40-500 chars (WI2 + rationale schema)
    severity: critical

  - assertion: "len(output.rationale.sections) == 8"
    description: 8 rationale sections
    severity: critical
```

The other 8 evals follow the same flat checks[] pattern. Each must have at least 3 critical checks.

- [ ] **Step 4: Validate**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
python3 -c "
import yaml, glob
files = sorted(glob.glob('electrical/cable-sizing/evals/eval-*.yaml'))
assert len(files) == 9, f'expected 9 evals, got {len(files)}'
for f in files:
    d = yaml.safe_load(open(f))
    assert d['skill'] == 'electrical/cable-sizing'
    assert d['category'] in {'happy_path','edge_case','validation_trap','missing_input','jurisdiction_switch','rationale_block','skill_specific'}
    assert len(d['checks']) >= 3
    for fixture in d['input_fixtures']:
        import os
        resolved = os.path.normpath(os.path.join('electrical/cable-sizing/evals', fixture))
        assert os.path.exists(resolved), f'{f}: missing fixture {resolved}'
    print(f'{f}: {d[\"category\"]}, {len(d[\"checks\"])} checks')
print('All 9 evals validate')
"
```

- [ ] **Step 5: Commit**

```bash
git add electrical/cable-sizing/evals/
git commit -m "feat(cable-sizing): 9 eval YAMLs + runner-config — 6 WI5 categories + 3 skill-specific (motor + parallel + harmonic)"
```

---

## Phase E — Docs + Bookkeeping + Final review + Push (Tasks 16-17)

### Task 16: Docs + SKILLS_STATUS + ARCHITECTURE

**Model:** Sonnet (mechanical content edits).

**Files (4):**
- Create: `electrical/cable-sizing/docs/engineering-philosophy.md`
- Create: `electrical/cable-sizing/docs/known-limitations.md`
- Modify: `SKILLS_STATUS.md` — small-power row already updated; modify cable-sizing row + bump beta count
- Modify: `ARCHITECTURE.md` — add `### cable-sizing skill (v1.0+)` subsection

- [ ] **Step 1: Write docs/engineering-philosophy.md**

~80-120 line markdown explaining:
- Why walk-the-ladder from below (not iterative): transparency for tender reviewers
- Why binding_constraint is named per node (auditable single decision)
- Why cumulative Vd is the project-level reality (per-segment is misleading)
- Why CPC adiabatic can drive phase upsize (sometimes the binding constraint)
- Why parallel cables are last-resort (symmetric impedance requirement is fragile)
- Why harmonic derating is an explicit trigger (engineer must declare h3 content)

- [ ] **Step 2: Write docs/known-limitations.md**

~60-100 lines per spec §13:
- DC scope deferred to dc-cable-sizing sibling
- IEC 60287 advanced thermal modelling deferred (uses standard tables only)
- Communications/data cables deferred (different standards family)
- Arc-flash incident-energy boundary marking deferred to arc-flash sibling
- Time-graded protection curve coordination deferred to db-layout + future protection-coordination

- [ ] **Step 3: Modify SKILLS_STATUS.md**

Read SKILLS_STATUS.md to find:
- The current `cable-sizing` row (currently shows `stub` or earlier state)
- Current beta count line near line 177

Update the cable-sizing row to:
```
| cable-sizing | `electrical/cable-sizing` | **beta** | BS 7671:2018+A2:2022 App 4 + App 12, IEC 60364-5-52 + -5-54 + -4-43, KS 1700:2018 §313, NEC 2023 Chapter 9 + Art 310/240/250/220/215/210, NEMA MG-1 | 9/4 ✓ | v1.0.0 beta — Project-scoped cascade IR (mirrors fault-level). Multi-skill consumer (db-layout-rollup + fault-level intents). Walk-the-ladder CSA with binding_constraint per node + walk_up_trail. 4 extra checks (cumulative Vd + motor-starting + parallel + harmonic). 14-step generator + 10 INV + 8 D. 4 jurisdictional examples (UK + KE + INT + US). Produces cable-sizing intent for 4 consumers (cable-schedule + riser + cable-containment + small-power v1.1). Intent carries `r1_plus_r2_milliohm_per_m_at_operating_temp` + `reactance_milliohm_per_m` for Zs-resolution. 3 calc contracts reused (cable-ampacity + voltage-drop + cpc-adiabatic — all updated with `_consuming_skills`). |
```

Bump beta count from 8 to 9 (cable-sizing added). Add cable-sizing to the beta summary list line.

- [ ] **Step 4: Modify ARCHITECTURE.md**

Find the insertion point (after the small-power v1.0+ subsection — that pattern was established Task 16 of the small-power sprint). Add `### cable-sizing skill (v1.0+)` subsection covering:

- Project-scoped cascade IR shape mirroring fault-level
- Multi-skill consumption pattern (db-layout-rollup + fault-level)
- Walk-the-ladder selection with binding_constraint vocabulary (6 tokens)
- 4 extra engineering checks
- 4 jurisdictional examples
- 4 downstream consumers + 2 Zs-resolution helper fields on intent
- WI3 tool-call deferral for the 3 calc contracts
- Versioning policy (minor/major/patch bump rules)

- [ ] **Step 5: Validate + commit**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
grep -n 'cable-sizing' SKILLS_STATUS.md | head -3
grep -n 'cable-sizing skill' ARCHITECTURE.md
git add electrical/cable-sizing/docs/ SKILLS_STATUS.md ARCHITECTURE.md
git commit -m "docs: cable-sizing v1.0.0 beta — engineering-philosophy + known-limitations + SKILLS_STATUS row + ARCHITECTURE subsection"
```

---

### Task 17: Cross-cutting validation + final code review + push

**Model:** Opus (judgment call on what passes for v1.0 ship).

This task runs the same gate as small-power Task 17. It does NOT make new content — only validates, reviews, and pushes.

- [ ] **Step 1: Cross-cutting validation pass**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"

# 1.1 — Every example IR + intent validates
python3 << 'PY'
import json, jsonschema, os
ir_schema = json.load(open('electrical/cable-sizing/schemas/cable-sizing-ir.schema.json'))
intent_schema = json.load(open('electrical/cable-sizing/schemas/cable-sizing-intent.schema.json'))
base = 'electrical/cable-sizing/schemas/'
resolver = jsonschema.RefResolver(base_uri='file://' + os.path.abspath(base) + '/', referrer=ir_schema)

examples = ['uk-domestic-final-circuits', 'ke-nairobi-commercial-with-msb', 'intl-commercial-with-feeders', 'us-industrial-with-motors']
for ex in examples:
    out = json.load(open(f'electrical/cable-sizing/examples/{ex}/output.json'))
    intent = json.load(open(f'electrical/cable-sizing/examples/{ex}/intent-out.json'))
    jsonschema.validate(out, ir_schema, resolver=resolver); print(f'  {ex} output.json: VALID')
    jsonschema.validate(intent, intent_schema); print(f'  {ex} intent-out.json: VALID')
PY

# 1.2 — Manifest paths all resolve
python3 -c "
import json, os
m = json.load(open('electrical/cable-sizing/skill.manifest.json'))
for k in ['standards', 'ontology', 'calculations']:
    for p in m.get(k, []):
        assert os.path.exists(p), f'MISSING: {p}'
print('All manifest paths resolve')
"

# 1.3 — chat_summary length per example
python3 -c "
import json
for ex in ['uk-domestic-final-circuits','ke-nairobi-commercial-with-msb','intl-commercial-with-feeders','us-industrial-with-motors']:
    o = json.load(open(f'electrical/cable-sizing/examples/{ex}/output.json'))
    cs = o['rationale']['chat_summary']
    print(f'  {ex}: chat_summary {len(cs)} chars')
    assert 40 <= len(cs) <= 500
"

# 1.4 — Every example circuit has Zs helpers
python3 -c "
import json
for ex in ['uk-domestic-final-circuits','ke-nairobi-commercial-with-msb','intl-commercial-with-feeders','us-industrial-with-motors']:
    i = json.load(open(f'electrical/cable-sizing/examples/{ex}/intent-out.json'))
    for c in i['circuits']:
        assert 'r1_plus_r2_milliohm_per_m_at_operating_temp' in c, f'{ex} {c[\"node_id\"]} missing R1+R2'
        assert 'reactance_milliohm_per_m' in c, f'{ex} {c[\"node_id\"]} missing reactance'
    print(f'  {ex}: all circuits have Zs helpers')
"

# 1.5 — KE citation form audit
python3 -c "
content = ''
for p in ['electrical/cable-sizing/examples/ke-nairobi-commercial-with-msb/output.json','electrical/cable-sizing/examples/ke-nairobi-commercial-with-msb/reasoning.md']:
    content += open(p).read()
assert 'adopted by KS 1700' not in content, 'FORBIDDEN annotation form'
print('KE citation form OK (no \"adopted by KS 1700\")')
"

# 1.6 — Eval input_fixtures all resolve
python3 -c "
import yaml, glob, os
for f in sorted(glob.glob('electrical/cable-sizing/evals/eval-*.yaml')):
    d = yaml.safe_load(open(f))
    for fixture in d['input_fixtures']:
        resolved = os.path.normpath(os.path.join('electrical/cable-sizing/evals', fixture))
        assert os.path.exists(resolved), f'{f}: missing {resolved}'
print('All eval fixtures resolve')
"

# 1.7 — Calc contracts list cable-sizing as consumer
python3 -c "
import json
for f in ['cable-ampacity','voltage-drop','cpc-adiabatic']:
    d = json.load(open(f'shared/calculations/electrical/{f}.json'))
    assert 'electrical/cable-sizing (primary, since v1.0.0)' in d.get('_consuming_skills', []), f'{f}: cable-sizing missing'
print('All 3 calc contracts list cable-sizing as consumer')
"

# 1.8 — File count
find electrical/cable-sizing -type f | wc -l
```

- [ ] **Step 2: Dispatch code-review subagent (optional but recommended)**

If using subagent-driven-development, dispatch a code-reviewer subagent against the entire `electrical/cable-sizing/` folder. The reviewer should flag any CRITICAL/HIGH issues. Address before push.

- [ ] **Step 3: Final commit count check + push**

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
git log --oneline 7c67225..HEAD | wc -l
git status
git log --oneline 7c67225..HEAD | head -30
```

Expected: 17-22 commits (one per task plus per-task fixes).

If everything passes:
```bash
git push origin main
```

If push fails or any CRITICAL/HIGH found, STOP and report.

- [ ] **Step 4: Save sprint memory**

After successful push, write `/Users/linus/.claude/projects/-Users-linus-Desktop-DraftsMan-SKills-draftsman-skills/memory/cable-sizing-shipped.md` with the same shape as `small-power-shipped.md`:

```markdown
---
name: cable-sizing-shipped
description: cable-sizing v1.0.0 beta shipped 2026-05-20 — most-consumed calc tool in repo, multi-skill consumer, 4 jurisdictional examples + Zs helper fields
metadata:
  type: project
---

**✅ SHIPPED 2026-05-20 — cable-sizing v1.0.0 beta**

Most-consumed calc tool in the repo. Multi-skill consumer (db-layout-rollup + fault-level). Produces cable-sizing intent feeding cable-schedule + riser + cable-containment + small-power v1.1.

## Architecture captured
- Project-scoped cascade IR mirroring fault-level
- Walk-the-ladder CSA selection with binding_constraint (6-token enum) + walk_up_trail per node
- 4 extra engineering checks: cumulative Vd / motor-starting / parallel cables / harmonic derating
- WI3 tool-call deferral for calc.cable_ampacity + calc.voltage_drop + calc.cpc_adiabatic (all 3 contracts REUSED)
- 2 Zs-resolution helper fields on intent (r1_plus_r2_milliohm_per_m_at_operating_temp + reactance_milliohm_per_m) — small-power v1.1 migration target

## Stats
- ~54 files in electrical/cable-sizing/
- 4 jurisdictional examples (UK domestic + KE Nairobi + INT commercial + US industrial)
- 9 evals + 5 rules + 4 constraints + 4 validation (12 checks) + 2 ontology files
- 14-step generator + 10 INV + 8 D

## How to apply
- Future small-power v1.1 sprint: consume cable-sizing intent; replace TOOL-CALL-PENDING:calc.zs_loop_impedance with resolved verified_zs_ohm using r1_plus_r2 + reactance × length
- Future cable-schedule skill: consume cable-sizing intent's full per-circuit set
- Future riser skill: consume feeder-level + parent_node_id
- Future cable-containment skill: consume cable_od_mm + weight_kg_per_m + parallel_count
- Pattern parent for next calc skill: cable-sizing v1.0 (cascade IR + walk-up trail)

## Cross-references
- [[small-power-shipped]] — v1.1 migration target consumer
- [[runtime-project-boundary]] — 3 calc contracts shipped here; runtime executes
- [[feedback-no-haiku-sonnet-opus-only]] — followed throughout sprint
- [[build-strategy-breadth-first]] — closes Item 3 of Tier 1 sequence
```

Then update `MEMORY.md` index with a 1-line entry for the new memory file.

```bash
git add /Users/linus/.claude/projects/-Users-linus-Desktop-DraftsMan-SKills-draftsman-skills/memory/cable-sizing-shipped.md
# MEMORY.md is also in same dir — add it too
```

(Note: memory files are personal scope, not in the repo — no commit needed; Write tool persists them.)

---

## Self-review checklist (run after writing this plan)

- [x] **Spec coverage:** Every section of base spec + refresh spec has a task implementing it.
  - Base §1-§3 (Overview/Scope/Files) → Task 1
  - Base §4 IR + §4.3 intent → Task 2 + refresh §1 deltas merged
  - Base §5 CSA algorithm → Tasks 4 + 7-10 (encoded in generator + demonstrated in examples)
  - Base §6 Extra checks → Tasks 7-10 + rules + constraints
  - Base §7 Prompts → Tasks 4-6
  - Base §8 Rules + Constraints + Validation → Tasks 12-14
  - Base §9 Evals → Task 15
  - Base §10 Examples + refresh §3 KE → Tasks 7-10
  - Base §11 Manifest → Task 1
  - Base §12 Cross-skill contracts + refresh §2 → Tasks 1 (manifest) + 2 (intent schema)
  - Base §13 Known limitations + §14 Versioning → Task 16
  - Refresh §1 Zs helper fields → Tasks 2 + 7-10
- [x] **Placeholder scan:** No "TBD"/"TODO"/"add validation"/"similar to". Concrete content for every step.
- [x] **Type consistency:** `binding_constraint` enum identical in schema (Task 2) + walk-up trail (Tasks 7-10) + INV-N references (Task 5) + rules (Task 12). `r1_plus_r2_milliohm_per_m_at_operating_temp` field name spelled identically in: intent schema (Task 2), all 4 example intent-out.json (Tasks 7-10), validation/intent-shape (Task 14), eval-09 (Task 15), refresh spec §1, and CHANGELOG (Task 1).

---

**Plan complete and saved to `docs/superpowers/plans/2026-05-20-cable-sizing-skill-sprint.md`.**

Two execution options:

1. **Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, two-stage review (spec compliance → code quality) after each, continuous execution. Matches the proven pattern from small-power sprint.

2. **Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints for user review.

Which approach?
