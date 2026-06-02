# small-power v2.0.0 D4 Depth Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `electrical/small-power/` v1.2.0 → **v2.0.0 production** — closes the within-skill-depth program for small-power (the last item from `[[within-skill-depth-plan]]` pushed from D3 to D4 by `[[sprint-D3-shipped]]`). Adds 5 scope items: `building_diversity` IR field mirroring verified standards file, 4 new Part-7 worked examples (pool/medical IT/EV/sauna), comprehensive ring/radial topology depth (4 new INVs), EV-charge demand coordination with Type A/B RCD rule, and INV verifying cable_sizing intent feeds into the new building-level diversity calc.

**Architecture:** Within-skill-depth sprint (no cascade contract changes — special-locations D.3 already wired the cascade). 7 new INVs (INV-13..INV-19) bring catalogue from 12 → 19. 9 new example dirs (8 NEW + 1 RETROFIT) bring example count from 6 → 15. 5 new evals bring eval catalogue from 5 → 10. Plus 2 producer-side cascade fixtures added to `electrical/special-locations/examples/` so the EV + sauna Part-7 examples have real cascade sources. Sprint shape mirrors special-locations (4 phases × 25 implementer tasks + ~5-7 fix-passes + final ship + 4 plan portions).

**Tech Stack:**
- JSON Schema Draft 2020-12 (matches existing small-power-ir schema draft version)
- YAML for rules + evals + manifests
- Markdown for prompts + README + CHANGELOG
- Python stdlib for any helper calc verification (no third-party deps per [[runtime-project-boundary]])
- Existing golden CI gate (`scripts/validate-examples.py` 3-pass: IR/eval/inputs validation)
- Existing `functional_audit.py` reasoning oracle

**Source spec:** [`docs/superpowers/specs/2026-06-02-small-power-d4-depth-design.md`](../specs/2026-06-02-small-power-d4-depth-design.md) v1.0.1 (commit `d45bf5b`).
**Pattern parent:** [`docs/superpowers/plans/2026-06-01-special-locations-sprint.md`](2026-06-01-special-locations-sprint.md) (special-locations sprint that shipped 26 + 3 housekeeping commits clean on 2026-06-02).
**Verified standards files** (every citation in the plan traces back to one of these):
- `shared/standards/electrical/BS7671/diversity-factors.json`
- `shared/standards/electrical/BS7671/part7-special-locations.json`
- `shared/standards/electrical/BS7671/reg433-overcurrent-protection.json`
- `shared/standards/electrical/BS7671/reg411-rcd-requirements.json`
- `electrical/small-power/rules/topology-rules.yaml` (anchor citation for IET OSG §8.4.4)

---

## Sprint discipline (locked, mirrors special-locations)

- Sonnet for mechanical (scaffolding, schemas, manifests, eval YAML, cascade wiring) per `[[feedback-no-haiku-sonnet-opus-only]]`
- Opus for judgment (generator/validator/reviewer prompts, all examples, retrofits, all reviews)
- **Two-stage Opus review after every implementer task** (spec-compliance + code-quality combined). Fix-pass commit when HIGH/CRITICAL findings surface. `[[sprint-D3-shipped]]` history: 10/11 D3 implementer tasks needed fix-passes — budget for ~5-7 fix-pass commits.
- **Cross-check every citation against verified standards files BEFORE the implementer reads the task.** Spec §2.3 verified-citation table is authoritative. Spec §11.1 banned list (14 inherited from special-locations + "OZEV CoP" + "3rd Edition" EV CoP + §526.2 + §433.2) cannot appear anywhere in implementer output.
- Pre-ship **Sonnet 11-check verification fence** (D.3 task)
- Final cross-sprint Opus integration review before push (D.5 task)
- Push deferred to user authorisation per CLAUDE.md "shared state" rule (D.6 task)
- `[[feedback-no-trim-non-consequential]]` — `invariants[].evidence` `maxLength: 1200` already in place from special-locations sprint; A.1 task maintains the cap (no schema regression)

### Estimated commit count: 30-35

- 25 implementer commits (5 + 4 + 10 + 6)
- ~5-7 fix-pass commits (10/11 D3 pattern)
- 1 final ship commit (D.6 + push)
- 4 portion commits for this plan doc

---

## File structure

### Created (new files in `electrical/small-power/`)

```
electrical/small-power/
├── rules/
│   ├── building-diversity-rules.yaml          # NEW; 3 profile rules (office/industrial/healthcare) + applies_after const
│   └── ev-charge-rules.yaml                   # NEW; EV-01 dedicated circuit + EV-02 no-diversity + EV-03 RCD Type A/B + EV-04 BS EN 61851-1
└── examples/
    ├── uk-pool-hall-sockets-and-isolation/                  # NEW Part-7 example #1
    │   ├── input.json
    │   ├── output.json
    │   ├── reasoning.md
    │   └── intent-out.json
    ├── uk-medical-group-2-isolation-sockets/                # NEW Part-7 example #2
    │   └── (same 4 files)
    ├── uk-ev-charge-domestic/                               # NEW Part-7 example #3
    │   └── (same 4 files)
    ├── uk-sauna-with-heater-exemption/                      # NEW Part-7 example #4
    │   └── (same 4 files)
    ├── uk-office-floor-with-building-diversity/             # NEW building_diversity demo #5
    │   └── (same 4 files)
    ├── uk-industrial-warehouse-with-building-diversity/     # NEW building_diversity demo #6
    │   └── (same 4 files)
    ├── uk-3bed-with-ring-continuity/                        # NEW topology demo #8 (INV-14 + INV-17 PASS)
    │   └── (same 4 files)
    └── uk-3bed-with-ring-continuity-VIOLATION/              # NEW topology FAIL HIGH demo #9
        └── (same 4 files)

electrical/small-power/evals/
├── eval-09-building-diversity-self-consistency.yaml         # NEW; INV-13; skill_specific; 3 checks
├── eval-10-ring-continuity.yaml                             # NEW; INV-14 + INV-15; skill_specific; 3 checks
├── eval-11-topology-ocpd-coordination.yaml                  # NEW; INV-16 + INV-17; validation_trap; 3 checks
├── eval-12-ev-rcd-type-selection.yaml                       # NEW; INV-18; validation_trap; 2 checks
└── eval-13-cable-sizing-cascade-integration.yaml            # NEW; INV-19; cross_validation; 2 checks
```

### Created (producer-side cascade fixtures in special-locations)

```
electrical/special-locations/examples/
├── cascade-small-power-uk-ev-charge-domestic/               # NEW producer fixture
│   ├── input.json
│   ├── output.json
│   ├── reasoning.md
│   └── intent-out.json
└── cascade-small-power-uk-sauna-heater-exemption/           # NEW producer fixture
    └── (same 4 files)
```

### Modified (existing files in `electrical/small-power/`)

```
electrical/small-power/
├── skill.manifest.json                # 1.2.0 → 2.0.0; status beta → production; description v2; _v2_breaking_change_note (bump-as-signaling)
├── inputs.json                        # +3 optional items (building_diversity_inputs / ring_continuity_endpoints / ev_charge_metadata)
├── CHANGELOG.md                       # add [2.0.0] entry
├── README.md                          # v2 update — INV table grows to 19 + D-checks grow to 10 + building_diversity feature section
├── prompts/
│   ├── generator.md                   # +Step 13 (building_diversity) +Step 14 (ring endpoints) +Step 15 (fcu + ev_charge_metadata)
│   ├── validator.md                   # +INV-13..INV-19 (7 new INV sections after existing INV-12)
│   └── reviewer.md                    # +D-8 / D-9 / D-10 (3 new D-checks)
├── rules/
│   ├── diversity-rules.yaml           # +DIV-05 lift table (closes lift diversity gap from D2.3)
│   └── topology-rules.yaml            # +TOP-06 (ring continuity) +TOP-07 (floor-area cross-check) +TOP-08 (OCPD-topology coord) +TOP-09 (AMD 2 FCU spur)
├── schemas/
│   ├── small-power-ir.schema.json     # +building_diversity top-level + circuits[].{ring_endpoints, fcu_spurs[], ev_charge_metadata} + 7 new INV ids + 3 new allOf clauses; cap maxLength: 1200 maintained
│   └── small-power-intent.schema.json # building_diversity field mirror at intent level
└── examples/intl-open-plan-floor/     # RETROFIT — add building_diversity office profile + INT jurisdiction routing
```

### Modified (memory + CHANGELOG outside small-power)

```
~/.claude/projects/-Users-linus-Desktop-DraftsMan-SKills-draftsman-skills/memory/
├── MEMORY.md                          # append [small-power v2.0.0 D4 shipped] line under [special-locations shipped]
└── small-power-v2.0-d4-shipped.md     # NEW; full sprint summary per [[special-locations-shipped]] pattern

CLAUDE.md                              # manifest tally bump: 13 shipped (10 beta + 3 production) → 13 shipped (9 beta + 4 production) — small-power moves beta→production; total unchanged
```

---

## Phase A — Foundations (5 tasks, Sonnet-heavy)

Phase A produces the IR schema additions + inputs.json + 2 new rules YAML files + 2 rules YAML extensions + manifest bump. Each task ships as one implementer commit; per-task two-stage Opus review may add a fix-pass commit. Phase A complete after A.5 ships green.

---

## Task A.1: IR schema additions (Sonnet)

**Why Sonnet:** Mechanical JSON Schema additions per the photometric A.3 / special-locations A.2 precedent.

**Files:**
- Modify: `shared/schemas/electrical/small-power-ir.schema.json`
- Modify: `electrical/small-power/schemas/small-power-intent.schema.json`

- [ ] **Step 1: Read current IR schema state**

```bash
python3 -c "
import json
d = json.load(open('shared/schemas/electrical/small-power-ir.schema.json'))
print('top-level properties:', sorted(d['properties'].keys()))
print('allOf clauses:', len(d.get('allOf', [])))
inv = d['properties'].get('invariants', {}).get('items', {})
print('invariants[].properties.id pattern:', inv.get('properties', {}).get('id', {}).get('pattern'))
print('invariants[].evidence maxLength:', inv.get('properties', {}).get('evidence', {}).get('maxLength'))
"
```

Expected: existing `circuits[]`, `rooms[]`, `consumed_intents`, `calculation_summary`, etc. + `invariants[].evidence.maxLength: 1200` from special-locations sprint.

- [ ] **Step 2: Add `building_diversity` top-level optional field**

Edit `shared/schemas/electrical/small-power-ir.schema.json`. Add a new property under top-level `properties` block:

```json
"building_diversity": {
  "type": "object",
  "description": "Building-level diversity per IET OSG App A — Table A1 (verified standards file). Applies AFTER per-circuit diversity (DIV-01..DIV-04). v2.0 limited to office/industrial/healthcare per verified diversity-factors.json; retail/residential/data-center deferred to v2.1.",
  "additionalProperties": false,
  "required": ["building_type", "floor_count", "design_density_w_per_m2", "future_expansion_pct", "applies_after", "applies_load_types", "building_diversified_demand_a", "_clause_citation", "_derivation_note"],
  "properties": {
    "building_type": {"type": "string", "enum": ["office", "industrial", "healthcare"]},
    "floor_count": {"type": "integer", "minimum": 1},
    "design_density_w_per_m2": {"type": "number", "minimum": 0},
    "future_expansion_pct": {"type": "number", "minimum": 0, "maximum": 100},
    "applies_after": {"const": "per_load_diversity"},
    "applies_load_types": {"type": "array", "items": {"type": "string"}, "minItems": 1},
    "building_diversified_demand_a": {"type": "number", "minimum": 0},
    "per_circuit_demand_inputs": {
      "type": "array",
      "description": "Closes INV-19 cascade integration: every circuit driving the building_diversified_demand_a must be listed here with its post-per-load-diversity current + the building factor applied.",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["circuit_id", "post_per_load_diversity_a", "building_factor_applied"],
        "properties": {
          "circuit_id": {"type": "string"},
          "post_per_load_diversity_a": {"type": "number", "minimum": 0},
          "building_factor_applied": {"type": "number", "minimum": 0, "maximum": 1}
        }
      }
    },
    "_clause_citation": {"type": "string"},
    "_derivation_note": {"type": "string", "minLength": 40, "maxLength": 800}
  }
}
```

- [ ] **Step 3: Add `circuits[].ring_endpoints` (conditional on topology=ring)**

Add under existing `circuits[].items.properties`:

```json
"ring_endpoints": {
  "type": "object",
  "description": "Required when circuits[].topology == 'ring'. Captures both endpoints + the MCB way for §526.2-style continuity verification (INV-14). Citation: IET OSG §8.4.4 (8th Edition) + BS 7671:2018+A2:2022 §526 top-level (sub-clause §526.2 not transcribed in verified file).",
  "additionalProperties": false,
  "required": ["endpoint_a_xy", "endpoint_b_xy", "mcb_way_id", "continuity_verified", "_citation"],
  "properties": {
    "endpoint_a_xy": {"type": "object", "required": ["x_mm", "y_mm"], "properties": {"x_mm": {"type": "number"}, "y_mm": {"type": "number"}}},
    "endpoint_b_xy": {"type": "object", "required": ["x_mm", "y_mm"], "properties": {"x_mm": {"type": "number"}, "y_mm": {"type": "number"}}},
    "mcb_way_id": {"type": "string", "minLength": 1},
    "continuity_verified": {"type": "boolean"},
    "_citation": {"type": "string"}
  }
}
```

- [ ] **Step 4: Add `circuits[].fcu_spurs[]` (optional, for AMD 2 modelling)**

```json
"fcu_spurs": {
  "type": "array",
  "description": "AMD 2 modelling for fused connection unit spurs on ring final circuits. Each entry is one FCU. Citation: IET OSG §8.4.4 (8th Edition, AMD 2 update) + BS 7671:2018+A2:2022 §433 top-level.",
  "items": {
    "type": "object",
    "additionalProperties": false,
    "required": ["location_xy", "fcu_rating_a", "downstream_loads_w", "_citation"],
    "properties": {
      "location_xy": {"type": "object", "required": ["x_mm", "y_mm"], "properties": {"x_mm": {"type": "number"}, "y_mm": {"type": "number"}}},
      "fcu_rating_a": {"type": "integer", "enum": [3, 5, 13]},
      "downstream_loads_w": {"type": "number", "minimum": 0},
      "_citation": {"type": "string"}
    }
  }
}
```

- [ ] **Step 5: Add `circuits[].ev_charge_metadata` (conditional on load_type=ev_charge_*)**

```json
"ev_charge_metadata": {
  "type": "object",
  "description": "Required when circuits[].load_type matches ev_charge_*. Captures Reg 722.531.3.101 RCD type selection + BS EN 61851-1 charging unit standard + Mode 3/4 + IET CoP for EV (4th Ed) dedicated-circuit rule.",
  "additionalProperties": false,
  "required": ["rcd_type", "charging_unit_dc_detection_a", "mode", "charging_unit_standard", "socket_standard", "dedicated_circuit", "_citation"],
  "properties": {
    "rcd_type": {"type": "string", "enum": ["type_a", "type_b"]},
    "charging_unit_dc_detection_a": {"type": "number", "minimum": 0},
    "mode": {"type": "integer", "enum": [3, 4]},
    "charging_unit_standard": {"const": "BS EN 61851-1"},
    "socket_standard": {"type": "string", "enum": ["BS EN 62196 Type 2 Mennekes", "BS EN 62196 CCS Combo 2"]},
    "dedicated_circuit": {"const": true},
    "_citation": {"type": "string"}
  }
}
```

- [ ] **Step 6: Add 3 new allOf clauses for conditional requirements**

```json
{
  "description": "Wave 2 D4 / topology: when any circuit has topology=ring, that circuit MUST carry ring_endpoints.",
  "if": {"properties": {"circuits": {"contains": {"properties": {"topology": {"const": "ring"}}, "required": ["topology"]}}}},
  "then": {"properties": {"circuits": {"items": {"if": {"properties": {"topology": {"const": "ring"}}}, "then": {"required": ["ring_endpoints"]}}}}}
},
{
  "description": "Wave 2 D4 / EV: when any circuit's load_type matches ev_charge_*, that circuit MUST carry ev_charge_metadata.",
  "if": {"properties": {"circuits": {"contains": {"properties": {"load_type": {"pattern": "^ev_charge_"}}, "required": ["load_type"]}}}},
  "then": {"properties": {"circuits": {"items": {"if": {"properties": {"load_type": {"pattern": "^ev_charge_"}}}, "then": {"required": ["ev_charge_metadata"]}}}}}
},
{
  "description": "Wave 2 D4 / healthcare: when building_diversity.building_type == healthcare, applies_load_types MUST include healthcare_clinical_equipment per HTM 06-01.",
  "if": {"properties": {"building_diversity": {"properties": {"building_type": {"const": "healthcare"}}, "required": ["building_type"]}}},
  "then": {"properties": {"building_diversity": {"properties": {"applies_load_types": {"contains": {"const": "healthcare_clinical_equipment"}}}}}}
}
```

- [ ] **Step 7: Update intent schema (`small-power-intent.schema.json`)**

Add a permissive mirror of `building_diversity` so the intent-out can carry the cascade payload:

```json
"building_diversity": {
  "type": "object",
  "additionalProperties": true,
  "description": "v2.0 cascade payload addition. Permissive (additionalProperties: true) so consumers receive the full building-level diversity context. Semantic gating remains on the IR side."
}
```

- [ ] **Step 8: Validate both schemas parse + are Draft 2020-12 valid**

```bash
python3 -c "
import json, jsonschema
for p in ['shared/schemas/electrical/small-power-ir.schema.json',
          'electrical/small-power/schemas/small-power-intent.schema.json']:
    d = json.load(open(p))
    # Schema's own meta-validation
    jsonschema.Draft202012Validator.check_schema(d)
    print(f'{p}: OK')
    if 'building_diversity' in d.get('properties', {}):
        bd = d['properties']['building_diversity']
        print(f'  has building_diversity: required keys = {bd.get(\"required\")}')
    inv = d['properties'].get('invariants', {}).get('items', {})
    if inv:
        ml = inv.get('properties', {}).get('evidence', {}).get('maxLength')
        print(f'  invariants.evidence maxLength: {ml} (must remain 1200)')
"
```

Expected: both files OK; `maxLength: 1200` unchanged from special-locations sprint.

- [ ] **Step 9: Run gates (no regression expected — no examples yet exercise the new fields)**

```bash
python3 scripts/validate-examples.py 2>&1 | tail -3
python3 functional_audit.py 2>&1 | tail -3
```

Expected: `validate-examples 316/316 pass`, `functional_audit 1 finding` unchanged (the disclosed motor-superposition oracle FP). Existing 6 small-power examples + 1 added by special-locations D.4 = 7 examples still validate (new fields are optional).

- [ ] **Step 10: Verify no banned citations slipped into schema descriptions**

```bash
grep -nE "(§701\.32|§701\.55|§702\.55\.1|§702\.55\.2|§702\.32|§703\.55|§703\.512|§703\.413|§710\.413\.1\.5|§710\.314|§710\.411\.3\.3|§715\.560\.4|§715\.521|§715\.422|OZEV|3rd Edition|§526\.2|§433\.2)" shared/schemas/electrical/small-power-ir.schema.json electrical/small-power/schemas/small-power-intent.schema.json | grep -v "sub-clause\|not transcribed\|do NOT\|NOT verified" && echo "FAIL: banned citation in active text" || echo "PASS"
```

Expected: `PASS`.

- [ ] **Step 11: Commit A.1**

```bash
git add shared/schemas/electrical/small-power-ir.schema.json \
        electrical/small-power/schemas/small-power-intent.schema.json
git commit -m "$(cat <<'EOF'
feat(small-power): A.1 IR schema additions for D4 depth (v2.0 prep)

First task of small-power v2.0.0 D4 depth sprint. Phase A foundations —
first of five.

IR schema additions (shared/schemas/electrical/small-power-ir.schema.json):
- NEW building_diversity top-level optional field (office/industrial/
  healthcare profile + floor_count + density + expansion + applies_after
  const + applies_load_types[] + per_circuit_demand_inputs[] for INV-19
  cascade integration + _clause_citation + _derivation_note 40-800 char)
- NEW circuits[].ring_endpoints (conditional on topology=ring) —
  endpoint_a_xy + endpoint_b_xy + mcb_way_id + continuity_verified;
  citation IET OSG §8.4.4 + BS 7671 §526 top-level (§526.2 not
  transcribed in verified file per spec §2.3 citation hygiene catch)
- NEW circuits[].fcu_spurs[] optional — fcu_rating_a in {3,5,13} +
  downstream_loads_w; citation IET OSG §8.4.4 (AMD 2 update) +
  BS 7671 §433 top-level
- NEW circuits[].ev_charge_metadata (conditional on load_type=ev_charge_*)
  — rcd_type type_a|type_b + charging_unit_dc_detection_a + mode 3|4 +
  charging_unit_standard BS EN 61851-1 + socket_standard BS EN 62196 +
  dedicated_circuit const true; citation Reg 722.531.3.101 + IET CoP
  for EV (4th Ed)
- 3 NEW allOf clauses: topology=ring → ring_endpoints required;
  load_type=ev_charge_* → ev_charge_metadata required; building_type=
  healthcare → applies_load_types contains healthcare_clinical_equipment
  per HTM 06-01
- additionalProperties: false maintained at every object level
- invariants[].evidence maxLength: 1200 maintained (from special-locations
  sprint, per [[feedback-no-trim-non-consequential]])

Intent schema mirror (electrical/small-power/schemas/small-power-intent.
schema.json):
- building_diversity permissive sub-object (additionalProperties: true)
  so cascade payload passes Pass-4 validation; semantic gating on IR
  side

Gates: validate-examples 316/316 unchanged (new fields optional;
existing 7 examples still validate). functional_audit 1 finding unchanged.
Zero banned citations.

Next: A.2 inputs.json additions.
EOF
)"
```

---

## Task A.2: inputs.json additions (Sonnet)

**Why Sonnet:** Mechanical YAML-shaped JSON additions per the special-locations A.3 precedent.

**Files:**
- Modify: `electrical/small-power/inputs.json`

- [ ] **Step 1: Read current inputs.json shape**

```bash
python3 -c "
import json
d = json.load(open('electrical/small-power/inputs.json'))
print(f'current items count: {len(d[\"items\"])}')
print(f'ids: {[i[\"id\"] for i in d[\"items\"]]}')
"
```

- [ ] **Step 2: Append 3 new optional items**

Add to the `items[]` array (append; do not replace existing):

```json
{
  "id": "building_diversity_inputs",
  "name": "Building-level diversity context",
  "description": "OPTIONAL — engineer-supplied building taxonomy that drives the building_diversity IR field (INV-13). Falls back to verified standards-file values when overrides absent. Per IET On-Site Guide 8th Edition Appendix A — Table A1.",
  "type": "object",
  "required": false,
  "_validation_hint": "{building_type ∈ ['office','industrial','healthcare'], floor_count: int ≥1, design_density_w_per_m2_override?: number, future_expansion_pct_override?: number ∈ [0,100]}. v2.0 limited to 3 building types per verified diversity-factors.json; retail/residential/data-center/hospitality deferred to v2.1."
},
{
  "id": "ring_continuity_endpoints",
  "name": "Ring final circuit continuity endpoints",
  "description": "OPTIONAL — per-ring endpoint coordinates and MCB way id so the validator can verify both ends of every ring final circuit land at the same MCB way per IET OSG §8.4.4 (INV-14).",
  "type": "array",
  "required": false,
  "_validation_hint": "Each entry: {circuit_id, endpoint_a_xy: {x_mm, y_mm}, endpoint_b_xy: {x_mm, y_mm}, mcb_way_id: string}. When circuits[].topology == 'ring' and this input is supplied, INV-14 verifies the cross-reference; when absent, INV-14 emits 'skipped — input not supplied' and passes vacuously (engineer-of-record must verify manually)."
},
{
  "id": "ev_charge_metadata",
  "name": "EV charge circuit metadata",
  "description": "OPTIONAL — per-EV-circuit Reg 722.531.3.101 RCD type + BS EN 61851-1 charging unit standard + Mode 3/4 cabling per IET Code of Practice for EV Charging Equipment Installation (4th Ed). Drives INV-18 (RCD Type A/B selection).",
  "type": "array",
  "required": false,
  "_validation_hint": "Each entry: {circuit_id, rcd_type: 'type_a'|'type_b', charging_unit_dc_detection_a: number (0 or 6 typical), mode: 3|4, charging_unit_standard: 'BS EN 61851-1', socket_standard ∈ ['BS EN 62196 Type 2 Mennekes','BS EN 62196 CCS Combo 2']}. Type A is default per Reg 722.531.3.101; Type B required when charging_unit_dc_detection_a < 6 (no built-in 6mA DC detection)."
}
```

- [ ] **Step 3: Validate inputs.json against inputs metaschema**

```bash
python3 -c "
import json, jsonschema
schema = json.load(open('shared/schemas/core/inputs.schema.json'))
inputs = json.load(open('electrical/small-power/inputs.json'))
jsonschema.validate(instance=inputs, schema=schema)
print(f'OK; total items: {len(inputs[\"items\"])}')
new_ids = ['building_diversity_inputs', 'ring_continuity_endpoints', 'ev_charge_metadata']
for nid in new_ids:
    found = any(i['id'] == nid for i in inputs['items'])
    print(f'  {nid}: {\"present\" if found else \"MISSING\"}')
"
```

Expected: OK + all 3 new ids present.

- [ ] **Step 4: Verify no banned citations**

```bash
grep -nE "(§701\.32|§701\.55|§702\.55\.1|§702\.55\.2|§702\.32|§703\.55|§703\.512|§703\.413|§710\.413\.1\.5|§710\.314|§710\.411\.3\.3|§715\.560\.4|§715\.521|§715\.422|OZEV|3rd Edition|§526\.2|§433\.2)" electrical/small-power/inputs.json && echo "FAIL" || echo "PASS"
```

Expected: `PASS`.

- [ ] **Step 5: Run gates**

```bash
python3 scripts/validate-examples.py 2>&1 | tail -3
```

Expected: validate-examples 316/316 unchanged (inputs.json change picked up by Pass 3 but content-wise this is just adding optional items so existing examples still pass).

- [ ] **Step 6: Commit A.2**

```bash
git add electrical/small-power/inputs.json
git commit -m "feat(small-power): A.2 inputs.json — 3 new optional D4 items (building_diversity_inputs + ring_continuity_endpoints + ev_charge_metadata)"
```

---

## Task A.3: NEW rules YAML files (Sonnet)

**Why Sonnet:** Mechanical YAML authoring per the special-locations A.3 precedent.

**Files:**
- Create: `electrical/small-power/rules/building-diversity-rules.yaml`
- Create: `electrical/small-power/rules/ev-charge-rules.yaml`

- [ ] **Step 1: Write `building-diversity-rules.yaml` (3 building-type profile rules)**

```yaml
# Building-level diversity factors per IET On-Site Guide 8th Edition Appendix A — Table A1
# Applied AFTER per-circuit diversity (DIV-01..DIV-04 in diversity-rules.yaml)
# v2.0 limited to office/industrial/healthcare per verified diversity-factors.json
# retail/residential/data-center/hospitality deferred to v2.1
#
# Consumed by validator (INV-13 building_diversity self-consistency)
# Source of truth: shared/standards/electrical/BS7671/diversity-factors.json

rules:
  - id: BLD-01
    jurisdiction: [GB, KE]
    standard_reference: "IET On-Site Guide 8th Edition Appendix A — Table A1 (office) + diversity-factors.json"
    rule_text: >
      Office building diversity profile: applies_load_types =
      [office_small_power_workstation, office_lighting, office_hvac_vav,
      office_lift_single, office_lift_two, office_lift_three_or_more].
      design_density range 65-100 W/m²; future_expansion_pct default 25%.
      Apply per-circuit DIV-NN factors first, then sum the diversified currents
      and apply the building-level factor for the building's lift count.
      Formula: building_diversified_demand_a = Σ(circuit_post_per_load_diversity_a × building_factor)
    applies_to: building_diversity
    enforcement: hard_fail

  - id: BLD-02
    jurisdiction: [GB, KE]
    standard_reference: "IET On-Site Guide 8th Edition Appendix A — Table A1 (industrial) + diversity-factors.json"
    rule_text: >
      Industrial building diversity profile: applies_load_types =
      [industrial_motor_groups, industrial_process_loads, industrial_lighting,
      industrial_compressors, industrial_welding_resistive].
      design_density range 80-150 W/m² (varies widely by industry).
      future_expansion_pct default 30% (industrial change rate higher than office).
      Apply per-circuit DIV-NN factors first; for motor groups use 100% largest +
      50% remainder per IET OSG App A.
    applies_to: building_diversity
    enforcement: hard_fail

  - id: BLD-03
    jurisdiction: [GB, KE]
    standard_reference: "HTM 06-01 + IET On-Site Guide 8th Edition Appendix A — Table A1 (healthcare)"
    rule_text: >
      Healthcare building diversity profile: applies_load_types MUST include
      healthcare_clinical_equipment (enforced by IR schema allOf clause).
      Also typically includes: healthcare_general_lighting, healthcare_hvac,
      healthcare_lift_essential_emergency, healthcare_uninterruptible_supply.
      design_density range 100-150 W/m². future_expansion_pct default 20%
      (healthcare load growth driven by clinical-tech roadmap, often planned).
      Apply per-circuit DIV-NN factors first; HTM 06-01 takes precedence
      over IET OSG for clinical-area diversity.
    applies_to: building_diversity
    enforcement: hard_fail

  - id: BLD-04
    jurisdiction: [GB, KE, INT]
    standard_reference: "applies_after computation-order discipline"
    rule_text: >
      building_diversity.applies_after MUST equal "per_load_diversity" (const).
      This documents the computation order: per-circuit diversity (DIV-01..04)
      runs FIRST at each circuit; then the building-level factor multiplies
      the sum of per-circuit demanded currents. Reversing the order produces
      wrong answers (building factor would be applied to undiversified loads).
    applies_to: building_diversity
    enforcement: hard_fail

  - id: BLD-05
    jurisdiction: [GB, KE]
    standard_reference: "IET Guidance Note 1 §4 (blocks / commercial diversity context)"
    rule_text: >
      Per-circuit demand traceability: every circuit contributing to
      building_diversified_demand_a MUST appear in per_circuit_demand_inputs[]
      with its post-per-load-diversity current AND the building factor applied.
      This is the structural ingredient of INV-19 (cable-sizing cascade
      integration): the cable_sizing.payload.circuits[] must contain matching
      entries so the cascade is traceable end-to-end.
    applies_to: building_diversity
    enforcement: hard_fail
```

- [ ] **Step 2: Write `ev-charge-rules.yaml` (4 EV-NN rules)**

```yaml
# EV charge installation rules per BS 7671:2018+A2:2022 §722 + IET Code of Practice
# for EV Charging Equipment Installation (4th Ed)
# Consumed by validator (INV-18 RCD Type A/B selection)
#
# IMPORTANT: D4 scope is intentionally narrow — RCD type + dedicated circuit + diversity
# Open-PEN protection (§722.411.4.1), Mode 3/4 cable sizing, and smart charging are
# DEFERRED to the dedicated EV-Charge skill (currently stub per CLAUDE.md)

rules:
  - id: EV-01
    jurisdiction: [GB, KE]
    standard_reference: "BS 7671:2018+A2:2022 §722 (top-level) + IET Code of Practice for EV Charging Equipment Installation (4th Ed)"
    rule_text: >
      Every EV charge circuit MUST be a dedicated circuit — no shared loads
      with sockets, lighting, fixed equipment, or other distribution circuits.
      Enforced at IR via circuits[].ev_charge_metadata.dedicated_circuit ==
      true (const). This is the central engineering rule that distinguishes
      EV charging from other small-power loads.
    applies_to: circuits
    enforcement: hard_fail

  - id: EV-02
    jurisdiction: [GB, KE]
    standard_reference: "IET Code of Practice for EV Charging Equipment Installation (4th Ed)"
    rule_text: >
      EV charge demand: NO diversity applied. Each charge point contributes
      100% of its rated current to the building_diversified_demand calculation.
      Rationale: EV charging is a contracted-load-bearing service; assuming
      partial occupancy at sizing-time risks the supply tripping when fleet
      usage spikes. Engineer can document load-management-based diversity
      separately if smart-charging control is part of the design, but the
      default at sizing-time is no diversity.
    applies_to: circuits
    enforcement: warning

  - id: EV-03
    jurisdiction: [GB, KE]
    standard_reference: "BS 7671:2018+A2:2022 §722.531.3.101 (verified)"
    rule_text: >
      RCD type selection rule: Type A 30 mA per charge point is the DEFAULT
      per §722.531.3.101. Type B is REQUIRED when the charging unit does not
      have built-in 6 mA DC residual current detection. The IR
      circuits[].ev_charge_metadata.charging_unit_dc_detection_a field captures
      the manufacturer's declared detection threshold; INV-18 enforces:
        rcd_type=type_a iff charging_unit_dc_detection_a ≥ 6;
        rcd_type=type_b iff charging_unit_dc_detection_a <  6.
      Type A on a unit without 6 mA DC detection is a HIGH safety failure
      (DC fault current can blind a Type A RCD; only Type B detects DC).
    applies_to: circuits
    enforcement: hard_fail

  - id: EV-04
    jurisdiction: [GB, KE]
    standard_reference: "BS EN 61851-1 + BS EN 62196 (verified in part7-special-locations.json)"
    rule_text: >
      Charging unit standard MUST be BS EN 61851-1 (const enforced at IR
      schema). Socket/plug MUST be BS EN 62196 Type 2 'Mennekes' for AC
      Mode 3 OR CCS Combo 2 for DC Mode 4. The mode field enforces the
      typical Mode 3 (AC up to 22 kW 32A 3-ph) vs Mode 4 (DC rapid 50-350
      kW) distinction; Mode 1 (AC unattended via standard socket) and
      Mode 2 (AC with in-cable controlbox) are DEPRECATED in §722 and NOT
      permitted at D4 v2.0 ship.
    applies_to: circuits
    enforcement: hard_fail
```

- [ ] **Step 3: Validate both rules YAMLs parse**

```bash
python3 -c "
import yaml, glob
for p in sorted(glob.glob('electrical/small-power/rules/*.yaml')):
    d = yaml.safe_load(open(p))
    rules = d.get('rules', [])
    new_files = ['building-diversity-rules.yaml', 'ev-charge-rules.yaml']
    is_new = any(p.endswith(f) for f in new_files)
    print(f'{p}: OK ({len(rules)} rules){\" NEW\" if is_new else \"\"}')"
```

Expected: 7 rules files OK (5 existing + 2 new); building-diversity has 5 rules; ev-charge has 4 rules.

- [ ] **Step 4: Verify no banned citations**

```bash
grep -nE "(§701\.32|§701\.55|§702\.55\.1|§702\.55\.2|§702\.32|§703\.55|§703\.512|§703\.413|§710\.413\.1\.5|§710\.314|§710\.411\.3\.3|§715\.560\.4|§715\.521|§715\.422|OZEV|3rd Edition|§526\.2|§433\.2)" electrical/small-power/rules/building-diversity-rules.yaml electrical/small-power/rules/ev-charge-rules.yaml | grep -v "do NOT\|never cite\|sub-clause\|not transcribed" && echo "FAIL" || echo "PASS"
```

Expected: `PASS`.

- [ ] **Step 5: Run gates**

```bash
python3 scripts/validate-examples.py 2>&1 | tail -3
```

Expected: 316/316 unchanged (rules YAML not validated by golden CI; consumed by skill prompt + reasoning).

- [ ] **Step 6: Commit A.3**

```bash
git add electrical/small-power/rules/building-diversity-rules.yaml \
        electrical/small-power/rules/ev-charge-rules.yaml
git commit -m "feat(small-power): A.3 NEW rules YAML — building-diversity-rules (5 BLD-NN) + ev-charge-rules (4 EV-NN)"
```

---

## Task A.4: rules YAML extensions (Sonnet)

**Why Sonnet:** Append-only extensions to 2 existing rules files.

**Files:**
- Modify: `electrical/small-power/rules/topology-rules.yaml` (append TOP-06..TOP-09)
- Modify: `electrical/small-power/rules/diversity-rules.yaml` (append DIV-05 lift table)

- [ ] **Step 1: Append TOP-06..TOP-09 to `topology-rules.yaml`**

After existing TOP-05:

```yaml
  - id: TOP-06
    jurisdiction: [GB, KE]
    standard_reference: "IET On-Site Guide §8.4.4 (8th Edition) + BS 7671:2018+A2:2022 §526 (top-level)"
    rule_text: >
      Ring final circuit continuity: when circuits[].topology == 'ring',
      both endpoints of the ring (endpoint_a_xy and endpoint_b_xy) MUST land
      at the same MCB way (mcb_way_id). A ring that lands at two different
      ways is structurally broken — the supply is then two radials sharing
      conductors, NOT a ring final, and the Zs / cable thermal protection
      assumptions for ring topology no longer apply.
      INV-14 enforces. Note: BS 7671 sub-clause §526.2 is not transcribed in
      the verified standards file; the anchor citation is IET OSG §8.4.4
      (which IS verified and already used by TOP-01..TOP-05 above).
    applies_to: circuits
    enforcement: hard_fail

  - id: TOP-07
    jurisdiction: [GB, KE, INT]
    standard_reference: "IET On-Site Guide §8.4.4 (8th Edition)"
    rule_text: >
      Per-circuit floor-area cross-check: circuit.floor_area_m2 (the
      engineer-declared floor area served) MUST equal Σ(rooms_covered[].
      floor_area_m2) (the sum of rooms the circuit actually feeds, derived
      from circuit.rooms_covered). Drift between the two suggests one of:
        (a) the engineer declared an area without listing the rooms,
        (b) the rooms_covered list is stale (room added/removed in iteration),
        (c) a typo in either field.
      INV-15 enforces. Tolerance: ±5% (rounding in m² conversions).
    applies_to: circuits
    enforcement: hard_fail

  - id: TOP-08
    jurisdiction: [GB, KE]
    standard_reference: "BS 7671:2018+A2:2022 §433.1.1 + IET On-Site Guide §8.4.4"
    rule_text: >
      OCPD-topology coordination: the chosen MCB rating MUST be coordinated
      with the topology and conductor csa:
        - topology=ring          → MCB ≤ 32 A
        - topology=radial AND cable_csa_mm2=2.5 → MCB ≤ 20 A
        - topology=radial AND cable_csa_mm2=4   → MCB ≤ 32 A
        - topology=dedicated_radial → MCB sized by connected load per §433.1.1
      A 32 A MCB on a 2.5 mm² radial would breach Iz before tripping under
      sustained 20-32 A; the cable overheats. INV-16 enforces.
    applies_to: circuits
    enforcement: hard_fail

  - id: TOP-09
    jurisdiction: [GB, KE]
    standard_reference: "IET On-Site Guide §8.4.4 (8th Edition, AMD 2 update) + BS 7671:2018+A2:2022 §433 (top-level)"
    rule_text: >
      Fused connection unit (FCU) spur modelling: when circuits[].fcu_spurs[]
      is populated, every entry MUST have fcu_rating_a ∈ {3, 5, 13} AND
      downstream_loads_w ≤ (fcu_rating_a × 230 V) — the FCU is the
      load's OCPD and must not be over-loaded. AMD 2 corrigenda clarified
      the 13 A FCU + ring final rules — the FCU is the spur's protection,
      not the ring MCB. INV-17 enforces (MEDIUM severity; an over-loaded
      FCU is a design defect but not a structural compliance breach because
      the FCU would still trip under fault — the breach is engineering
      best-practice).
      Note: BS 7671 sub-clause §433.2 is not transcribed in the verified
      standards file; the anchor citation is IET OSG §8.4.4 AMD 2.
    applies_to: circuits
    enforcement: warning
```

- [ ] **Step 2: Append DIV-05 to `diversity-rules.yaml` (lift table)**

After existing DIV-04 (assuming the existing file ends with DIV-04 per the inspection earlier):

```yaml
  - id: DIV-05
    jurisdiction: [GB, KE]
    standard_reference: "IET On-Site Guide 8th Edition Appendix A — Table A1 (lifts) + diversity-factors.json"
    rule_text: >
      Lift diversity factors (verified standards-file values):
        - office_lift_single:        100%  (no diversity; single lift runs full duty)
        - office_lift_two:            80%  (two-lift parallel; one always available)
        - office_lift_three_or_more:  70%  (three-or-more parallel; group control)
      Applied at the building-level for the office building_diversity profile.
      Cited via IET OSG App A, NOT Reg 559 (Reg 559 is a banned misattribution
      caught in D2.3 fix-pass — Reg 559 is luminaires-in-shops, NOT lift
      diversity). The verified diversity-factors.json carries the office_lift_*
      keys with these percentages.
    applies_to: building_diversity
    enforcement: info
```

- [ ] **Step 3: Validate both rules YAMLs parse + counts increased**

```bash
python3 -c "
import yaml
top = yaml.safe_load(open('electrical/small-power/rules/topology-rules.yaml'))
top_rules = top.get('rules', [])
print(f'topology-rules.yaml: {len(top_rules)} rules')
top_ids = [r['id'] for r in top_rules]
for nid in ['TOP-06', 'TOP-07', 'TOP-08', 'TOP-09']:
    print(f'  {nid}: {\"present\" if nid in top_ids else \"MISSING\"}')

div = yaml.safe_load(open('electrical/small-power/rules/diversity-rules.yaml'))
div_rules = div.get('rules', [])
print(f'diversity-rules.yaml: {len(div_rules)} rules')
div_ids = [r['id'] for r in div_rules]
print(f'  DIV-05: {\"present\" if \"DIV-05\" in div_ids else \"MISSING\"}')
"
```

Expected: topology has 9 rules (TOP-01..TOP-09), diversity has 5 rules (DIV-01..DIV-05).

- [ ] **Step 4: Verify no banned citations**

```bash
grep -nE "(§701\.32|§701\.55|§702\.55\.1|§702\.55\.2|§702\.32|§703\.55|§703\.512|§703\.413|§710\.413\.1\.5|§710\.314|§710\.411\.3\.3|§715\.560\.4|§715\.521|§715\.422|OZEV|3rd Edition|§526\.2|§433\.2|Reg 559)" electrical/small-power/rules/topology-rules.yaml electrical/small-power/rules/diversity-rules.yaml | grep -v "do NOT\|never cite\|sub-clause\|not transcribed\|banned misattribution" && echo "FAIL" || echo "PASS"
```

Expected: `PASS`. (The "Reg 559" mention in DIV-05 is inside the "banned misattribution" disclosure prose; grep filter excludes it.)

- [ ] **Step 5: Run gates + commit A.4**

```bash
python3 scripts/validate-examples.py 2>&1 | tail -3
git add electrical/small-power/rules/topology-rules.yaml \
        electrical/small-power/rules/diversity-rules.yaml
git commit -m "feat(small-power): A.4 rules YAML extensions — TOP-06..TOP-09 (4 topology depth rules) + DIV-05 (lift table)"
```

---

## Task A.5: Manifest bump + README v2 + pre-merge consumer check (Sonnet)

**Why Sonnet:** Mechanical manifest + README edit + grep-based consumer scan.

**Files:**
- Modify: `electrical/small-power/skill.manifest.json`
- Modify: `electrical/small-power/README.md`

- [ ] **Step 1: CRITICAL pre-merge check — grep for v1.x consumers of small-power**

Before bumping the version, confirm no other skill's `consumes_intents` is pinned to `^1.x` for small-power. The 2.0 bump would break their constraint matching.

```bash
python3 -c "
import json, glob
hits = []
for p in sorted(glob.glob('electrical/*/skill.manifest.json')):
    m = json.load(open(p))
    for c in m.get('consumes_intents', []):
        if c.get('skill_id') == 'small-power':
            hits.append((p, c.get('version_constraint')))
if hits:
    print('Consumers of small-power found:')
    for p, vc in hits:
        print(f'  {p}: version_constraint={vc}')
else:
    print('Zero consumers of small-power found — version bump 1.x → 2.0 is safe (no downstream constraint to update).')
"
```

Expected outcome: zero consumers (small-power is at the bottom of the distribution cascade; nothing consumes its intent). If ANY consumer found with `^1.x` pin, STOP and report — that consumer must update first.

- [ ] **Step 2: Bump manifest version + status**

In `electrical/small-power/skill.manifest.json`:
- Change `"version": "1.2.0"` → `"version": "2.0.0"`
- Change `"status": "beta"` → `"status": "production"`
- Append a `"_v2_breaking_change_note"` field at top-level (after `status`):

```json
"_v2_breaking_change_note": "v2.0.0 is a major bump as SIGNALING (NOT breakage). All v2.0 IR additions are additive: new building_diversity top-level field is OPTIONAL; new circuits[].ring_endpoints / fcu_spurs / ev_charge_metadata are conditional on existing fields (topology=ring / load_type=ev_charge_*). All 6 v1.x examples still validate against v2.0 schema. The bump signals: within-skill-depth program for small-power is CLOSED; small-power is now architecturally complete and PRODUCTION status. Pre-merge check at A.5 confirmed zero consumers of small-power were pinned to ^1.x at the time of the bump."
```

- [ ] **Step 3: Update standards entries (add 4 D4-specific cross-references)**

In the `standards[]` array, append:

```
"IET On-Site Guide 8th Edition Appendix A — Table A1 (building diversity + lift table)",
"IET On-Site Guide 8th Edition §8.4.4 (ring final + radial topology, including AMD 2 FCU spur update)",
"IET Code of Practice for EV Charging Equipment Installation (4th Ed)",
"BS EN 61851-1 (EV charging equipment) + BS EN 62196 (EV plug/socket — Type 2 Mennekes / CCS Combo 2)",
"HTM 06-01 (NHS healthcare medical electrical — taken with §710 for medical-IT cascade integration)"
```

(Append; do not remove existing standards entries.)

- [ ] **Step 4: Update `README.md` v2 highlights**

Append a new section at the top of the README body (after the existing identity block, before the existing INV table):

```markdown
## v2.0.0 highlights (Wave 2 first deliverable, 2026-06-02)

D4 closes the within-skill-depth program for small-power. Promoted from
beta to **production**. Bump 1.2.0 → 2.0.0 is bump-as-signaling, not
bump-as-breakage (see manifest `_v2_breaking_change_note`).

### What's new in v2.0
- NEW top-level optional `building_diversity` IR field mirroring verified
  diversity-factors.json office/industrial/healthcare profiles (BLD-01..05)
- NEW 4 Part-7 worked examples: pool (§702.415.1) + medical Group 2 (§710 IT)
  + EV charging (§722) + sauna (§703.411.3.3)
- NEW 4 topology depth rules: TOP-06 ring continuity + TOP-07 floor-area
  cross-check + TOP-08 OCPD-topology coordination + TOP-09 AMD 2 FCU spur
- NEW EV-charge demand coordination: RCD Type A/B selection per
  Reg 722.531.3.101 + no-diversity per IET CoP for EV (4th Ed) +
  dedicated-circuit rule + BS EN 61851-1 + BS EN 62196
- NEW INV-13..INV-19 (7 new INVs); catalogue now 19 total
- NEW D-8 / D-9 / D-10 reviewer judgment checks
- INV-19 verifies cable-sizing cascade integration with building_diversity

### Verified citation discipline (per spec §2.3)
All citations trace to verified standards files. Banned at the spec stage:
§526.2 + §433.2 (not transcribed in verified BS 7671 file — IET OSG §8.4.4
is the anchor) + OZEV CoP (correct name is IET CoP for EV Charging
Equipment Installation) + 3rd Edition EV CoP (correct is 4th Ed).
```

- [ ] **Step 5: Validate manifest still parses + verify v2.0 markers**

```bash
python3 -c "
import json
m = json.load(open('electrical/small-power/skill.manifest.json'))
print(f'version: {m[\"version\"]}; status: {m[\"status\"]}')
print(f'_v2_breaking_change_note present: {\"_v2_breaking_change_note\" in m}')
print(f'standards count: {len(m[\"standards\"])} (expected ≥ previous + 5)')
"
```

Expected: version 2.0.0; status production; note present; standards count grew by 5.

- [ ] **Step 6: Verify no banned citations in manifest or README**

```bash
grep -nE "(§701\.32|§701\.55|§702\.55\.1|§702\.55\.2|§702\.32|§703\.55|§703\.512|§703\.413|§710\.413\.1\.5|§710\.314|§710\.411\.3\.3|§715\.560\.4|§715\.521|§715\.422|OZEV|3rd Edition|§526\.2|§433\.2)" electrical/small-power/skill.manifest.json electrical/small-power/README.md | grep -v "Banned\|do NOT\|never cite\|sub-clause\|not transcribed\|banned at the spec stage" && echo "FAIL" || echo "PASS"
```

Expected: `PASS`. (Banned-citation mentions in the v2.0 highlights "verified citation discipline" disclosure are inside the documented banned-list context.)

- [ ] **Step 7: Run gates + commit A.5**

```bash
python3 scripts/validate-examples.py 2>&1 | tail -3
python3 functional_audit.py 2>&1 | tail -3
git add electrical/small-power/skill.manifest.json electrical/small-power/README.md
git commit -m "$(cat <<'EOF'
feat(small-power): A.5 manifest bump 1.2.0 → 2.0.0 + status beta → production + README v2

Fifth and final task of Phase A foundations. Phase A complete after this.

Manifest changes:
- version 1.2.0 → 2.0.0 (bump-as-signaling; small-power architecturally
  complete post-D4)
- status beta → production (closes within-skill-depth program)
- NEW _v2_breaking_change_note field documenting that all changes are
  additive (new building_diversity is OPTIONAL; new circuits[]
  sub-blocks are conditional on existing fields). v1.x examples still
  validate against v2.0 schema.
- standards[] grows by 5 entries (IET OSG App A + §8.4.4 + IET CoP for
  EV 4th Ed + BS EN 61851-1 + BS EN 62196 + HTM 06-01)

Pre-merge consumer check: grep of all electrical/*/skill.manifest.json
files for consumes_intents.skill_id=='small-power' returned ZERO hits.
Version bump from 1.x to 2.0 is safe — no consumer constraint to update.

README v2 highlights section added:
- 4 Part-7 worked examples preview
- 4 topology depth rules preview
- EV-charge coordination preview
- INV-13..INV-19 + D-8/D-9/D-10 preview
- Verified citation discipline disclosure (banned: §526.2, §433.2, OZEV,
  3rd Edition EV CoP per spec §2.3)

Gates: validate-examples 316/316 unchanged; functional_audit 1 finding
unchanged. Zero banned citations.

Phase A complete (A.1 IR schema + A.2 inputs.json + A.3 new rules YAML
+ A.4 rules extensions + A.5 manifest + README). Next: Phase B prompts.
EOF
)"
```

---

[Phase B + C + D continue in subsequent plan portions — committed sequentially per the special-locations precedent. Phase B covers the 4 prompt tasks (generator + validator + reviewer + cascade-prereq update); Phase C covers the 8 new + 1 retrofit examples + 5 evals; Phase D covers the 2 new producer-side cascade fixtures + Sonnet 11-check fence + 3 CHANGELOGs + memory + final integration review + push-deferred-to-user.]
