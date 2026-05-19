# small-power Skill v1.0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the small-power skill v1.0 — socket outlet layouts at electrical-standards depth, 4 jurisdictional examples (UK + KE + INT + US), matching the lighting-layout v1.3 production pattern.

**Architecture:** Leaf skill (`consumes_intents: []`) producing a small-power intent for future db-layout v1.x consumption. Hybrid IR: `circuits[]` (with topology enum) + `rooms[]` (with sockets[] cross-referencing circuit_ids). Three calc tool contracts CONSUMED (no new contracts authored) — `calc.diversity_factor` + `calc.zs_loop_impedance` already exist in `shared/calculations/electrical/`. v1.1+ migrates to multi-skill consumption per the SLD v1.3→v1.4 precedent.

**Tech Stack:** JSON Schema Draft-07 (strict additionalProperties), Markdown prompts (YAML frontmatter + section structure matching lighting-layout v1.3), YAML evals, no executable code. Pattern parents: lighting-layout v1.3 (gold standard, leaf shape), SLD v1.5 (drafting standards consumption + jurisdictional examples), earthing v1.3 (KS 1700 routing), db-layout v1.3 (intl-dbcomms-data Type B RCD precedent), arc-flash-labelling (validator + reviewer patterns).

**Spec:** `docs/superpowers/specs/2026-05-19-small-power-skill-design.md` (commit c5806bd).

---

## Reference table — spec corrections discovered during plan exploration

The spec §3.6 said "3 new calc contracts shipped" and §2 implied "3 NEW special-locations.json". Exploration of `shared/calculations/electrical/` and `shared/standards/electrical/*/part7-special-locations.json` revealed:

| Item the spec called for | Reality on disk | Plan correction |
|---|---|---|
| `calc.socket_diversity` (new contract) | Existing `shared/calculations/electrical/diversity-factor.json` already handles socket loads across all 5 jurisdictions | **Reuse** — declare in skill.manifest.json `calculations[]` |
| `calc.ring_loop_zs` (new contract) | Existing `shared/calculations/electrical/zs-loop-impedance.json` handles per-circuit Zs verification — already lists "socket circuit ≤32A per BS 7671 411.3.3" in its verdict logic | **Reuse** — declare in skill.manifest.json `calculations[]` |
| `calc.radial_zs` (new contract) | Same `zs-loop-impedance.json` handles radial Zs too (it's per-circuit, topology-agnostic) | **Reuse** — same contract |
| `special-locations.json` for BS7671 | `shared/standards/electrical/BS7671/part7-special-locations.json` EXISTS | **Reuse** — declare in skill.manifest.json `standards[]` |
| `special-locations.json` for IEC60364 | `shared/standards/electrical/IEC60364/part7-special-locations.json` EXISTS | **Reuse** |
| `special-locations.json` for KS1700 | `shared/standards/electrical/KS1700/part7-special-locations.json` EXISTS | **Reuse** |
| `special-locations.json` for NFPA70 | NOT present | **NEW file** — author US-specific GFCI scope per NEC 210.8 |

**Modify:** `shared/calculations/electrical/zs-loop-impedance.json` `_consuming_skills[]` — add `"electrical/small-power (primary, since v1.0.0)"` to the list (sibling to earthing v1.1 entry).

**Net file-count correction:** Spec said ~67 files; actual is ~64 files (3 fewer calc contracts; 2 fewer special-locations files; +1 NEW NFPA70 part7-special-locations.json).

---

## File structure (64 files total)

### NEW files (59)

**Skill infrastructure (4):**
- `electrical/small-power/skill.manifest.json`
- `electrical/small-power/inputs.json`
- `electrical/small-power/README.md`
- `electrical/small-power/CHANGELOG.md`

**Schemas (2):**
- `electrical/small-power/schemas/small-power-ir.schema.json`
- `electrical/small-power/schemas/small-power-intent.schema.json`

**Standards layer additions (1 NEW + 1 modified):**
- `shared/standards/electrical/NFPA70/part7-special-locations.json` — NEW (US-specific GFCI scope)
- `shared/calculations/electrical/zs-loop-impedance.json` — MODIFY (add small-power to `_consuming_skills[]`)

**Prompts (3):**
- `electrical/small-power/prompts/generator.md` — follows lighting-layout v1.3 structure (YAML frontmatter + Role + Standards + Inputs + How You Think Before Acting + Step 14 final rationale)
- `electrical/small-power/prompts/validator.md` — ~10 INV checks
- `electrical/small-power/prompts/reviewer.md` — 6 D-checks

**Examples — 4 × 5 files = 20:**
- `electrical/small-power/examples/uk-3bed-dwelling/{input,output,intent-out}.json + reasoning.md + sample-schedule.md`
- `electrical/small-power/examples/ke-nairobi-small-office/{input,output,intent-out}.json + reasoning.md + sample-schedule.md`
- `electrical/small-power/examples/intl-open-plan-floor/{input,output,intent-out}.json + reasoning.md + sample-schedule.md`
- `electrical/small-power/examples/us-residential-dwelling/{input,output,intent-out}.json + reasoning.md + sample-schedule.md`

**Evals — 9 YAMLs:**
- `electrical/small-power/evals/eval-01-uk-happy-path.yaml`
- `electrical/small-power/evals/eval-02-no-rcd-exception.yaml`
- `electrical/small-power/evals/eval-03-validation-trap-ring-in-us.yaml`
- `electrical/small-power/evals/eval-04-rationale-block.yaml`
- `electrical/small-power/evals/eval-05-jurisdiction-citation-form.yaml`
- `electrical/small-power/evals/eval-06-ring-topology-by-jurisdiction.yaml`
- `electrical/small-power/evals/eval-07-special-locations-compliance.yaml`
- `electrical/small-power/evals/eval-08-cross-room-ring-integrity.yaml`
- `electrical/small-power/evals/eval-09-gfci-scope-us.yaml`

**Rules YAMLs (5):**
- `electrical/small-power/rules/rcd-rules.yaml`
- `electrical/small-power/rules/topology-rules.yaml`
- `electrical/small-power/rules/special-locations-rules.yaml`
- `electrical/small-power/rules/spacing-rules.yaml`
- `electrical/small-power/rules/diversity-rules.yaml`

**Constraints + validation (3):**
- `electrical/small-power/constraints/electrical.yaml`
- `electrical/small-power/validation/cross-reference-validation.yaml`
- `electrical/small-power/validation/topology-validation.yaml`

**Ontology (1):**
- `shared/ontology/equipment/socket-types.json` — BS 1363 + Schuko CEE 7/4 + NEMA 5-15 + NEMA 5-20 + tamper-resistant variants

**Symbols (1):**
- `shared/symbols/electrical/sockets/socket-symbols.yaml`

**Drafting (1):**
- `electrical/small-power/drafting/layers.yaml` — per-jurisdiction layer name mapping (consumes drafting standards v1.6)

**Docs (3):**
- `electrical/small-power/docs/engineering-philosophy.md`
- `electrical/small-power/docs/known-limitations.md`
- `electrical/small-power/docs/supported-standards.md`

**Repo-level (2):**
- `SKILLS_STATUS.md` — MODIFIED (new row for small-power)
- `ARCHITECTURE.md` — MODIFIED (new "small-power skill (v1.0)" subsection)

---

# Phase A — Infrastructure (Tasks 1-3)

## Task 1: Skill skeleton (manifest + inputs + README + CHANGELOG)

**Model recommendation:** Sonnet (mechanical — follows lighting-layout v1.3 template exactly).

**Files:**
- Create: `electrical/small-power/skill.manifest.json`
- Create: `electrical/small-power/inputs.json`
- Create: `electrical/small-power/README.md`
- Create: `electrical/small-power/CHANGELOG.md`

### Step 1 — Read lighting-layout v1.3 template

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
cat electrical/lighting-layout/skill.manifest.json
cat electrical/lighting-layout/inputs.json | head -30
```

### Step 2 — Write `skill.manifest.json`

```json
{
  "skill": "small-power",
  "version": "1.0.0",
  "discipline": "electrical",
  "subdiscipline": "small-power",
  "description": "Socket outlet layouts for general-purpose power circuits per BS 7671:2018+A2:2022 / IEC 60364 / KS 1700:2018 / NEC 2023 Article 210. Produces circuit topology (ring/radial/dedicated_radial), per-room socket placement, RCD posture, and circuit-to-room cross-references as structured IR. Hybrid model: circuits[] (with topology + ocpd + cable + RCD) + rooms[] (with sockets[] cross-referencing circuit_ids). Leaf skill v1.0 — produces small-power intent for downstream db-layout consumption; multi-skill consumption (earthing + fault-level) deferred to v1.1+.",
  "status": "beta",
  "licence": "MIT",
  "inputs_path": "inputs.json",
  "inputs": [
    "jurisdiction",
    "parent-db-designation",
    "room-briefs",
    "supply-context",
    "design-intent"
  ],
  "outputs": ["small-power-ir"],
  "output_schema": "electrical/small-power/schemas/small-power-ir.schema.json",
  "produces_intent": "small-power",
  "produces_intent_schema": "electrical/small-power/schemas/small-power-intent.schema.json",
  "consumes_intents": [],
  "standards": [
    "shared/standards/electrical/BS7671/part7-special-locations.json",
    "shared/standards/electrical/BS7671/reg411-disconnection-times.json",
    "shared/standards/electrical/BS7671/reg411-rcd-requirements.json",
    "shared/standards/electrical/BS7671/diversity-factors.json",
    "shared/standards/electrical/IEC60364/part7-special-locations.json",
    "shared/standards/electrical/KS1700/part7-special-locations.json",
    "shared/standards/electrical/NFPA70/part7-special-locations.json",
    "shared/standards/drafting/BS1192/cad-layers.json",
    "shared/standards/drafting/AIA/cad-layers.json",
    "shared/standards/drafting/ISO19650/cad-layers.json",
    "shared/standards/drafting/ISO5457/sheet-sizes.json",
    "shared/standards/drafting/ISO5455/scales.json",
    "shared/standards/drafting/ISO7200/title-block-fields.json"
  ],
  "ontology": [
    "shared/ontology/equipment/socket-types.json",
    "shared/ontology/room-types/office.json",
    "shared/ontology/room-types/healthcare.json"
  ],
  "symbols": [
    "shared/symbols/electrical/sockets/"
  ],
  "calculations": [
    "shared/calculations/electrical/diversity-factor.json",
    "shared/calculations/electrical/zs-loop-impedance.json"
  ]
}
```

### Step 3 — Write `inputs.json`

```json
{
  "skill": "small-power",
  "input_groups": [
    {
      "group": "jurisdiction-and-supply",
      "fields": [
        {"name": "jurisdiction",                "type": "enum",   "values": ["GB", "EU", "INT", "KE", "US"], "required": true},
        {"name": "supply_voltage_v",            "type": "integer", "enum": [120, 208, 230, 240, 400, 415, 480], "required": true},
        {"name": "supply_phase_arrangement",    "type": "enum",   "values": ["single_phase", "single_phase_split", "TPN", "TPN_plus_E"], "required": true},
        {"name": "supply_system_type",          "type": "enum",   "values": ["TN-S", "TN-C-S", "TT"], "required": true,
         "description": "Earthing system. Engineer-declared in v1.0 (v1.1+ will consume from earthing intent)."},
        {"name": "supply_ze_declared_ohm",      "type": "float", "required": true,
         "description": "Earth fault loop impedance at the consumer's origin (Ze). Engineer-declared."},
        {"name": "supply_psc_declared_ka",      "type": "float", "required": true,
         "description": "Prospective short-circuit current at the supply origin (PSCC). Engineer-declared (v1.1+ will consume from fault-level intent)."}
      ]
    },
    {
      "group": "parent-db-context",
      "fields": [
        {"name": "parent_db_designation",       "type": "string", "required": true,
         "description": "Parent distribution board designation (e.g. 'CU-MAIN', 'DB-P1'). Engineer-declared string reference. No db-layout intent consumption in v1.0."},
        {"name": "parent_db_pfc_ka",            "type": "float", "required": true,
         "description": "Available PFC at the parent DB busbar. Used to verify breaker breaking capacity (Icu)."}
      ]
    },
    {
      "group": "rooms",
      "fields": [
        {"name": "room_briefs",                 "type": "array",  "required": true,
         "description": "Array of {room_id, room_type, dimensions_m, special_location, anticipated_loads, socket_count_target}. See room-types ontology for room_type enum."}
      ]
    },
    {
      "group": "design-intent",
      "fields": [
        {"name": "preferred_topology",          "type": "enum",   "values": ["ring", "radial", "auto_by_jurisdiction"], "default": "auto_by_jurisdiction",
         "description": "GB: auto picks ring for domestic + radial for commercial. Other jurisdictions: always radial. Engineer override permitted."},
        {"name": "drawing_standard",            "type": "string",
         "description": "Drafting standard reference. Defaults per jurisdiction (GB/KE: BS 1192:2007+A2:2016; INT: ISO 19650:2018; US: AIA CAD Layer Guidelines 2007)."},
        {"name": "sheet_size",                  "type": "enum",   "values": ["A0", "A1", "A2", "A3", "Arch_E", "Arch_D", "Arch_C"], "default_by_jurisdiction": {"GB": "A1", "KE": "A1", "INT": "A1", "US": "Arch_D"}},
        {"name": "drawing_scale",               "type": "string", "default_by_jurisdiction": {"GB": "1:50", "KE": "1:50", "INT": "1:100", "US": "1/4\"=1'"}}
      ]
    }
  ]
}
```

### Step 4 — Write `README.md`

```markdown
# small-power Skill v1.0

Socket outlet layouts for general-purpose power circuits. Produces structured IR with circuit topology, per-room socket placement, RCD posture, and circuit-to-room cross-references.

## What this skill produces

For a given parent DB + jurisdiction + room briefs, the skill emits:

- **Per-circuit data:** circuit_id, topology (ring/radial/dedicated_radial), OCPD selection, cable specification, RCD posture, diversified max load, rooms_covered array
- **Per-room data:** dimensions, special_location flag, sockets[] array with each socket's circuit_id reference + mount + height
- **Compliance summary:** non_compliance_flags + assumptions + WI3 deferral flags
- **Rationale block:** 8-section narrative + chat_summary ≤500 chars

## Architecture: leaf skill v1.0

- `consumes_intents: []` — no cross-skill consumption in v1.0 (matches lighting-layout v1.3 production pattern)
- `produces_intent: "small-power"` — future db-layout v1.x consumes this for general_power circuits
- Engineer declares earthing system_type, supply Ze, PSCC, parent DB context as user inputs
- v1.1+ migrates to consume earthing + fault-level intents per SLD v1.3→v1.4 precedent

## Jurisdictions supported

- **GB** — BS 7671:2018+A2:2022 (ring final circuits + Part 7-701 bathroom zones + IET OSG diversity)
- **KE** — KS 1700:2018 §313 routes to BS 7671 (radial typically preferred at commercial scale; ring permitted)
- **INT** — IEC 60364-4-41 / -5-53 / -7-701 (Schuko sockets; Type B RCD for IT loads per §531.3.3)
- **US** — NEC 2023 Article 210 (210.52 spacing, 210.8 GFCI, 210.12 AFCI, 406.12 tamper-resistant)

## Examples

| Folder | Scenario |
|---|---|
| `examples/uk-3bed-dwelling/` | UK 3-bedroom dwelling, 2 rings + dedicated cooker/immersion/shaver radials + Part 7-701 bathroom + outdoor |
| `examples/ke-nairobi-small-office/` | KE 80m² commercial office, 4 radials + BS 1363 + KS 1700 §313 + KPLC TN-S 415V |
| `examples/intl-open-plan-floor/` | INT 350m² commercial open-plan, 8 radials including UPS-fed Type B RCD for server room + ISO 19650 + IEC 60364-7-701 toilets + outdoor |
| `examples/us-residential-dwelling/` | US 160m² residential dwelling, 8 circuits + NEC 210.52 + 210.8 GFCI + 210.12 AFCI + duplex receptacles |

## Out of scope (v1.0)

- EV charging (BS 7671 Part 7-722 / NEC 625) — future ev-charging skill
- Cable containment / routing — future cable-containment skill
- Multi-skill intent consumption — deferred to v1.1+
- 3-phase socket outlets (BS EN 60309 CEEform) — future revision

See `CHANGELOG.md` for version history and `docs/supported-standards.md` for the full standards reference.
```

### Step 5 — Write `CHANGELOG.md`

```markdown
# Changelog

## [1.0.0] - 2026-05-19

### Added — first ship (beta)

- **Leaf skill v1.0**: produces small-power intent for downstream db-layout consumption. `consumes_intents: []` matches lighting-layout v1.3 production pattern.
- **Hybrid IR shape**: `circuits[]` (with topology enum: ring | radial | dedicated_radial) + `rooms[]` (with sockets[] cross-referencing circuit_ids). Cross-room rings naturally supported.
- **3-value topology enum**: `ring` (GB+KE only via KS 1700 §313 routing — INV-04 enforces); `radial` (all jurisdictions, default for KE/INT/US); `dedicated_radial` (single-load circuits per BS 7671 §433.1.4 / NEC 210.23).
- **6-value special-location enum**: `null` | `bathroom_zone_1` | `bathroom_zone_2` | `bathroom_zone_3` | `outdoor` | `wet_area`. Maps to BS 7671 Part 7-701 / IEC 60364-7-701 / KS 1700 Part 7 / NEC 210.8.
- **3-value rcd_posture enum**: `type_a_30ma_per_§411_3_3` (default for sockets ≤32A); `type_b_30ma_per_§531_3_3` (IT loads with DC leakage per IEC 60364-5-53 §531.3.3); `no_rcd_with_documented_§411_exception` (engineer-declared with explicit citation).
- **4 jurisdictional examples**: UK 3-bed dwelling + KE Nairobi small office + INT commercial open-plan + US residential dwelling.
- **3 prompts**: generator + validator (10 INV checks) + reviewer (6 D-checks). Pattern matches arc-flash-labelling + SLD v1.5.
- **9 evals**: 5 WI5 categories + 4 skill-specific (ring-topology-by-jurisdiction, special-locations compliance, cross-room ring integrity, GFCI scope US).
- **Drafting standards consumption**: sheet template + scale + layer naming consumed from v1.6 drafting standards layer per jurisdiction.
- **Calc tool consumption (existing contracts reused)**: `calc.diversity_factor` (shared/calculations/electrical/diversity-factor.json) + `calc.zs_loop_impedance` (shared/calculations/electrical/zs-loop-impedance.json — _consuming_skills updated to add small-power).
- **NEW standards addition**: `shared/standards/electrical/NFPA70/part7-special-locations.json` (US GFCI scope per NEC 210.8).

### Architectural notes

- Cross-skill consistency without intent consumption: INT example C06 (server-room small-power) manually mirrors the Type B 30mA RCD policy from db-layout's shipped `intl-dbcomms-data` example. Engineer mirrors the policy as input; v1.1+ will consume earthing intent for automatic cross-skill alignment.
- WI3 deferral: `tool_call_pending_for_zs_verification: true` per circuit + `TOOL-CALL-PENDING:calc.zs_loop_impedance` in flags[]. Matches SLD v1.3 + earthing v1.1 precedent.
- WI2 rationale: 8 sections + chat_summary ≤500 chars per example.

### Pattern parents

- lighting-layout v1.3 (production) — gold-standard layout skill; full folder scaffolding template
- SLD v1.5 — drafting standards consumption + multi-skill migration precedent
- earthing v1.3 — 4-jurisdiction example pattern + KS 1700 routing convention
- db-layout v1.3 — future consumer of small-power intent; intl-dbcomms-data Type B RCD precedent
- arc-flash-labelling — validator (~17 INV) + reviewer (6 D) pattern
- drafting standards v1.6 — sheet template + scale + layer naming

### Future direction (deferred)

- v1.1+ — multi-skill intent consumption (consume earthing + fault-level intents); INV-N cross-skill consistency checks
- v2.0 — schema-breaking changes (multi-board consumption, EV charging integration)
- ev-charging skill — BS 7671 Part 7-722 / NEC 625 / IEC 60364-7-722 (separate skill)
```

### Step 6 — Validate manifest parses

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
python3 -c "
import json
m = json.load(open('electrical/small-power/skill.manifest.json'))
assert m['skill'] == 'small-power'
assert m['version'] == '1.0.0'
assert m['consumes_intents'] == []
assert m['produces_intent'] == 'small-power'
assert 'shared/calculations/electrical/diversity-factor.json' in m['calculations']
assert 'shared/calculations/electrical/zs-loop-impedance.json' in m['calculations']
print('manifest valid; leaf skill confirmed; calc tools reused')
"
```

Expected: `manifest valid; leaf skill confirmed; calc tools reused`.

### Step 7 — Commit

```bash
git add electrical/small-power/skill.manifest.json electrical/small-power/inputs.json electrical/small-power/README.md electrical/small-power/CHANGELOG.md
git commit -m "feat(small-power): v1.0 skill skeleton — manifest + inputs + README + CHANGELOG"
```

---

## Task 2: Schemas (small-power-ir + small-power-intent)

**Model recommendation:** Opus (JSON Schema with strict additionalProperties + 3 enums + hybrid circuits[]+rooms[] cross-reference shape).

**Files:**
- Create: `electrical/small-power/schemas/small-power-ir.schema.json`
- Create: `electrical/small-power/schemas/small-power-intent.schema.json`

### Step 1 — Write small-power-ir.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "electrical/small-power/schemas/small-power-ir.schema.json",
  "title": "Small Power IR (Socket Outlet Layout)",
  "description": "Intermediate Representation for the small-power skill v1.0. Hybrid model: circuits[] (with topology + ocpd + cable + RCD posture) + rooms[] (with sockets[] cross-referencing circuit_ids). Leaf skill v1.0 — no cross-skill intent consumption.",
  "type": "object",
  "required": [
    "drawing_type",
    "version",
    "meta",
    "jurisdiction",
    "supply_origin",
    "parent_db",
    "circuits",
    "rooms",
    "drawing_layout",
    "compliance_summary",
    "rationale"
  ],
  "additionalProperties": false,
  "properties": {
    "drawing_type": { "const": "small_power_layout" },
    "version":      { "type": "string", "pattern": "^\\d+\\.\\d+(\\.\\d+)?$" },
    "meta": {
      "type": "object",
      "required": ["project_id", "skill_version", "produced_at"],
      "additionalProperties": false,
      "properties": {
        "project_id":    { "type": "string" },
        "skill_version": { "type": "string" },
        "produced_at":   { "type": "string", "format": "date-time" },
        "consumed_intents": { "type": "array", "items": { "type": "object" }, "default": [] }
      }
    },
    "jurisdiction": { "enum": ["GB", "EU", "INT", "KE", "US"] },
    "supply_origin": {
      "type": "object",
      "required": ["voltage_v", "phase_arrangement", "system_type", "ze_declared_ohm", "psc_declared_ka"],
      "additionalProperties": false,
      "properties": {
        "voltage_v":          { "type": "integer", "enum": [120, 208, 230, 240, 400, 415, 480] },
        "phase_arrangement":  { "enum": ["single_phase", "single_phase_split", "TPN", "TPN_plus_E"] },
        "system_type":        { "enum": ["TN-S", "TN-C-S", "TT"] },
        "ze_declared_ohm":    { "type": "number", "minimum": 0 },
        "psc_declared_ka":    { "type": "number", "minimum": 0 }
      }
    },
    "parent_db": {
      "type": "object",
      "required": ["designation", "pfc_at_busbar_ka"],
      "additionalProperties": false,
      "properties": {
        "designation":      { "type": "string" },
        "pfc_at_busbar_ka": { "type": "number", "minimum": 0 }
      }
    },
    "circuits": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["circuit_id", "designation", "topology", "ocpd", "cable", "rcd_posture", "estimated_max_load_kw", "diversified_max_load_a", "rooms_covered"],
        "additionalProperties": false,
        "properties": {
          "circuit_id":  { "type": "string", "pattern": "^C[0-9]{2}$" },
          "designation": { "type": "string" },
          "topology":    { "enum": ["ring", "radial", "dedicated_radial"] },
          "ocpd": {
            "type": "object",
            "required": ["rating_a", "type"],
            "additionalProperties": false,
            "properties": {
              "rating_a":              { "type": "integer", "minimum": 1, "maximum": 100 },
              "type":                  { "enum": ["MCB", "RCBO", "GFCI_breaker", "AFCI_breaker", "AFCI_GFCI_dual"] },
              "curve":                 { "enum": ["B", "C", "D"] },
              "rcd_type":              { "enum": ["A", "B", "F", "GFCI"] },
              "rcd_sensitivity_ma":    { "type": "integer", "enum": [10, 30, 100, 300] },
              "breaking_capacity_ka":  { "type": "number", "minimum": 1 }
            }
          },
          "cable": {
            "type": "object",
            "required": ["csa_mm2_or_awg", "cores", "length_m_total", "material", "insulation"],
            "additionalProperties": false,
            "properties": {
              "csa_mm2_or_awg":  { "type": "string" },
              "cores":           { "type": "integer", "minimum": 2, "maximum": 5 },
              "length_m_total":  { "type": "number", "minimum": 0 },
              "material":        { "enum": ["copper", "aluminium"] },
              "insulation":      { "enum": ["PVC_70", "XLPE_90", "EPR"] }
            }
          },
          "rcd_posture": {
            "enum": [
              "type_a_30ma_per_§411_3_3",
              "type_b_30ma_per_§531_3_3",
              "no_rcd_with_documented_§411_exception"
            ]
          },
          "rcd_exception_citation": { "type": "string", "description": "Required when rcd_posture is no_rcd_with_documented_§411_exception" },
          "verified_zs_ohm":         { "type": "number", "minimum": 0 },
          "tool_call_pending_for_zs_verification": { "type": "boolean", "default": true },
          "estimated_max_load_kw":   { "type": "number", "minimum": 0 },
          "diversified_max_load_a":  { "type": "number", "minimum": 0 },
          "rooms_covered":           { "type": "array", "minItems": 1, "items": { "type": "string" } }
        }
      }
    },
    "rooms": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["room_id", "room_type", "dimensions_m", "special_location", "sockets"],
        "additionalProperties": false,
        "properties": {
          "room_id":   { "type": "string" },
          "room_type": { "type": "string", "description": "Reference to shared/ontology/room-types/*.json or socket-types.json ontology" },
          "dimensions_m": {
            "type": "object",
            "required": ["length", "width", "height"],
            "additionalProperties": false,
            "properties": {
              "length": { "type": "number", "minimum": 0 },
              "width":  { "type": "number", "minimum": 0 },
              "height": { "type": "number", "minimum": 0 }
            }
          },
          "special_location": {
            "enum": [null, "bathroom_zone_1", "bathroom_zone_2", "bathroom_zone_3", "outdoor", "wet_area"]
          },
          "sockets": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["id", "type", "mount", "circuit_id"],
              "additionalProperties": false,
              "properties": {
                "id":             { "type": "string" },
                "type":           { "type": "string", "description": "Reference to shared/ontology/equipment/socket-types.json key" },
                "mount":          { "enum": ["wall", "above_worktop", "floor", "ceiling", "external_wall", "kitchen_island"] },
                "height_mm":      { "type": "integer", "minimum": 0, "maximum": 2500 },
                "circuit_id":     { "type": "string", "pattern": "^C[0-9]{2}$" },
                "fed_by_spur":    { "type": "boolean", "default": false },
                "spur_load_kw":   { "type": "number", "minimum": 0 },
                "spur_purpose":   { "type": "string" },
                "ip_rating":      { "type": "string", "pattern": "^IP[0-9X][0-9X]$" }
              }
            }
          }
        }
      }
    },
    "drawing_layout": {
      "type": "object",
      "required": ["sheet_size", "drawing_standard", "drawing_scale"],
      "additionalProperties": false,
      "properties": {
        "sheet_size":       { "enum": ["A0", "A1", "A2", "A3", "Arch_E", "Arch_D", "Arch_C"] },
        "drawing_standard": { "type": "string" },
        "drawing_scale":    { "type": "string" }
      }
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
            "properties": {
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
    "drawing_notes": { "type": "array", "items": { "type": "string" } },
    "rationale": { "$ref": "../../../shared/schemas/core/rationale.schema.json" }
  }
}
```

### Step 2 — Write small-power-intent.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "electrical/small-power/schemas/small-power-intent.schema.json",
  "title": "Small Power Intent (Downstream-Facing)",
  "description": "Stable subset of the small-power IR. Consumed by db-layout (parent DB feeder sizing), schematic (layout reference), cable-containment (route hints). Forward-compat: optional fields may be added; required-field changes require a major intent_version bump.",
  "type": "object",
  "required": ["project_id", "parent_db_designation", "circuits"],
  "additionalProperties": false,
  "properties": {
    "project_id":         { "type": "string" },
    "intent_version":     { "type": "string", "pattern": "^\\d+\\.\\d+\\.\\d+$" },
    "parent_db_designation": { "type": "string" },
    "circuits": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["circuit_id", "topology", "breaker_rating_a", "breaker_type", "diversified_max_load_a", "rooms_covered"],
        "additionalProperties": false,
        "properties": {
          "circuit_id":             { "type": "string" },
          "designation":            { "type": "string" },
          "topology":               { "enum": ["ring", "radial", "dedicated_radial"] },
          "breaker_rating_a":       { "type": "integer", "minimum": 1, "maximum": 100 },
          "breaker_type":           { "enum": ["MCB", "RCBO", "GFCI_breaker", "AFCI_breaker", "AFCI_GFCI_dual"] },
          "breaker_curve":          { "enum": ["B", "C", "D"] },
          "rcd_type":               { "enum": ["A", "B", "F", "GFCI"] },
          "rcd_sensitivity_ma":     { "type": "integer", "enum": [10, 30, 100, 300] },
          "cable_csa_mm2_or_awg":   { "type": "string" },
          "estimated_max_load_kw":  { "type": "number", "minimum": 0 },
          "diversified_max_load_a": { "type": "number", "minimum": 0 },
          "rooms_covered":          { "type": "array", "minItems": 1, "items": { "type": "string" } }
        }
      }
    }
  }
}
```

### Step 3 — Validate schemas as JSON Schema Draft-07

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
python3 -c "
import json, jsonschema
for path in ['electrical/small-power/schemas/small-power-ir.schema.json',
             'electrical/small-power/schemas/small-power-intent.schema.json']:
    with open(path) as f: s = json.load(f)
    jsonschema.Draft7Validator.check_schema(s)
    print(f'{path}: valid Draft-07')

# IR enums check
with open('electrical/small-power/schemas/small-power-ir.schema.json') as f: ir = json.load(f)
topology_enum = ir['properties']['circuits']['items']['properties']['topology']['enum']
assert topology_enum == ['ring', 'radial', 'dedicated_radial'], 'topology enum'
rcd_posture_enum = ir['properties']['circuits']['items']['properties']['rcd_posture']['enum']
assert 'type_a_30ma_per_§411_3_3' in rcd_posture_enum
assert 'type_b_30ma_per_§531_3_3' in rcd_posture_enum
assert 'no_rcd_with_documented_§411_exception' in rcd_posture_enum
special_loc_enum = ir['properties']['rooms']['items']['properties']['special_location']['enum']
assert None in special_loc_enum, 'null first in enum'
assert 'bathroom_zone_1' in special_loc_enum
assert 'outdoor' in special_loc_enum
print('All 3 enums populated correctly (topology, rcd_posture, special_location)')
"
```

### Step 4 — Commit

```bash
git add electrical/small-power/schemas/
git commit -m "feat(small-power): IR + intent schemas — hybrid circuits[]+rooms[] shape, 3 enums"
```

---

## Task 3: Standards layer + calc contract additions

**Model recommendation:** Sonnet (mechanical — one NEW special-locations.json + one modify to existing zs-loop-impedance.json).

**Files:**
- Create: `shared/standards/electrical/NFPA70/part7-special-locations.json` (US GFCI scope per NEC 210.8)
- Modify: `shared/calculations/electrical/zs-loop-impedance.json` — add small-power to `_consuming_skills[]`

### Step 1 — Read existing BS7671 part7 file as structural template

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
cat shared/standards/electrical/BS7671/part7-special-locations.json | head -40
```

### Step 2 — Write NFPA70/part7-special-locations.json (NEW)

```json
{
  "clause_ref": "NEC 2023 Article 210.8 — GFCI Protection of Personnel + Article 406.12 — Tamper-Resistant Receptacles",
  "transcribed_at": "2026-05-19",
  "transcribed_by": "DraftsMan skills repo",
  "verification_status": "draft-pending-verification",
  "_title": "NEC 2023 US Special Locations — GFCI Scope",
  "_source": "NFPA 70 (NEC) 2023 Article 210.8 + Article 406.12",
  "_note": "US NEC uses GFCI (Ground Fault Circuit Interrupter) for personnel protection in specific locations rather than the IEC/BS 7671 RCD + special-location-zone model. NEC 210.8 enumerates locations requiring GFCI receptacles or GFCI circuit protection. NEC 210.12 adds AFCI requirements. NEC 406.12 requires tamper-resistant receptacles in dwelling units.",
  "gfci_required_locations": {
    "210_8_A_1_bathrooms":         { "description": "Bathrooms (all dwelling-unit bathroom receptacles)", "scope": "dwelling_unit", "rating_a": [15, 20] },
    "210_8_A_2_garages_accessory": { "description": "Garages and accessory buildings (not used for habitation)", "scope": "dwelling_unit", "rating_a": [15, 20] },
    "210_8_A_3_outdoor":           { "description": "Outdoor receptacles", "scope": "dwelling_unit + commercial", "rating_a": [15, 20] },
    "210_8_A_4_crawl_spaces":      { "description": "Crawl spaces — at or below grade", "scope": "dwelling_unit", "rating_a": [15, 20] },
    "210_8_A_5_basements":         { "description": "Unfinished basements (not living areas)", "scope": "dwelling_unit", "rating_a": [15, 20] },
    "210_8_A_6_kitchens":          { "description": "Kitchens — all 15A/20A 125V receptacles serving countertop surfaces + within 6 ft of sink", "scope": "dwelling_unit", "rating_a": [15, 20] },
    "210_8_A_7_sinks":             { "description": "Sinks — receptacles within 6 ft of outside edge of sink", "scope": "dwelling_unit", "rating_a": [15, 20] },
    "210_8_A_8_boathouses":        { "description": "Boathouses", "scope": "dwelling_unit", "rating_a": [15, 20] },
    "210_8_A_9_bathtubs_showers":  { "description": "Bathtubs and shower stalls — within 6 ft", "scope": "dwelling_unit", "rating_a": [15, 20] },
    "210_8_A_10_laundry_areas":    { "description": "Laundry areas (all 125V outlets)", "scope": "dwelling_unit", "rating_a": [15, 20] }
  },
  "afci_required_locations_210_12": {
    "210_12_A_dwelling_branch_circuits": { "description": "All 120V 15A/20A branch circuits supplying outlets/devices in dwelling unit kitchens, family rooms, dining rooms, living rooms, parlors, libraries, dens, bedrooms, sunrooms, recreation rooms, closets, hallways, laundry areas, similar rooms or areas", "scope": "dwelling_unit", "rating_a": [15, 20] },
    "210_12_B_kitchen_dining":            { "description": "Kitchen branch circuits — must be both AFCI AND GFCI per 210.8(A)(6)", "scope": "dwelling_unit", "rating_a": [15, 20] }
  },
  "tamper_resistant_receptacles_406_12": {
    "_purpose": "All 15A/20A 125V receptacles in dwelling units MUST be tamper-resistant per NEC 406.12",
    "applies_to": "dwelling_unit",
    "rating_a": [15, 20]
  },
  "engine_lookup": {
    "_purpose": "Flat key/value lookup for runtime engine consumption",
    "by_location": {
      "bathroom":     { "gfci": true,  "afci": false, "tamper_resistant": true,  "nec_clause": "210.8(A)(1) + 406.12" },
      "garage":       { "gfci": true,  "afci": false, "tamper_resistant": true,  "nec_clause": "210.8(A)(2) + 406.12" },
      "outdoor":      { "gfci": true,  "afci": false, "tamper_resistant": true,  "nec_clause": "210.8(A)(3) + 406.12" },
      "crawl_space":  { "gfci": true,  "afci": false, "tamper_resistant": true,  "nec_clause": "210.8(A)(4) + 406.12" },
      "basement":     { "gfci": true,  "afci": false, "tamper_resistant": true,  "nec_clause": "210.8(A)(5) + 406.12" },
      "kitchen":      { "gfci": true,  "afci": true,  "tamper_resistant": true,  "nec_clause": "210.8(A)(6) + 210.12(B) + 406.12" },
      "bedroom":      { "gfci": false, "afci": true,  "tamper_resistant": true,  "nec_clause": "210.12(A) + 406.12" },
      "living_room":  { "gfci": false, "afci": true,  "tamper_resistant": true,  "nec_clause": "210.12(A) + 406.12" },
      "dining_room":  { "gfci": false, "afci": true,  "tamper_resistant": true,  "nec_clause": "210.12(A) + 406.12" },
      "hallway":      { "gfci": false, "afci": true,  "tamper_resistant": true,  "nec_clause": "210.12(A) + 406.12" },
      "laundry":      { "gfci": true,  "afci": true,  "tamper_resistant": true,  "nec_clause": "210.8(A)(10) + 210.12(A) + 406.12" }
    }
  },
  "_cross_refs": ["BS7671", "IEC60364"]
}
```

### Step 3 — Modify zs-loop-impedance.json to add small-power consumer

Read the existing `_consuming_skills` array (around line ~50 of the file). The current value is:

```json
"_consuming_skills": [
  "electrical/earthing (primary, since v1.1.0)",
  "electrical/db-layout (selectivity verification, future)",
  "electrical/cable-sizing (Zs as design constraint, future)"
]
```

Update to add small-power:

```json
"_consuming_skills": [
  "electrical/earthing (primary, since v1.1.0)",
  "electrical/small-power (primary, since v1.0.0)",
  "electrical/db-layout (selectivity verification, future)",
  "electrical/cable-sizing (Zs as design constraint, future)"
]
```

### Step 4 — Validate

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
python3 -c "
import json
nf = json.load(open('shared/standards/electrical/NFPA70/part7-special-locations.json'))
assert nf['clause_ref'].startswith('NEC 2023')
assert 'kitchen' in nf['engine_lookup']['by_location']
assert nf['engine_lookup']['by_location']['kitchen']['gfci'] == True
assert nf['engine_lookup']['by_location']['kitchen']['afci'] == True
print('NFPA70/part7-special-locations.json: valid')

zsl = json.load(open('shared/calculations/electrical/zs-loop-impedance.json'))
assert 'electrical/small-power (primary, since v1.0.0)' in zsl['_consuming_skills']
print('zs-loop-impedance.json: small-power added to _consuming_skills')
"
```

### Step 5 — Commit

```bash
git add shared/standards/electrical/NFPA70/part7-special-locations.json shared/calculations/electrical/zs-loop-impedance.json
git commit -m "feat(standards+calc): NFPA70 part7-special-locations + small-power added to zs-loop-impedance consumers"
```

---

# Phase B — Prompts (Tasks 4-6)

## Task 4: Generator prompt (12-step pattern within "How You Think Before Acting")

**Model recommendation:** Opus (judgment-heavy — engineering reasoning + 12 generator steps + jurisdictional logic).

**Files:**
- Create: `electrical/small-power/prompts/generator.md`

### Step 1 — Read lighting-layout generator template

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
sed -n '1,100p' electrical/lighting-layout/prompts/generator.md
```

### Step 2 — Write generator.md following lighting-layout structure

Mirror lighting-layout's YAML frontmatter + section structure. Sections:
- **Role** (senior electrical engineer specialising in small-power layouts)
- **Standards You Apply** (table: BS 7671 + KS 1700 + IEC 60364 + NEC 2023)
- **Inputs Required** (jurisdiction, supply, parent DB, rooms, design intent)
- **How You Think Before Acting** (12 internal steps for engineering reasoning)
- **What You Never Do** (anti-patterns: invent socket counts, mis-cite jurisdiction, mix RCD types)
- **Output Format** (small-power-ir.schema.json conformance)
- **Tools Available at Runtime** (calc.diversity_factor + calc.zs_loop_impedance — both deferred)
- **Required IR Output Block** (full IR shape)
- **Step 14 (final) — Emit `rationale` block** (WI2 — 8 sections + chat_summary ≤500 chars)

The 12 generator internal steps (within "How You Think Before Acting"):

1. **Determine jurisdiction + supply context** — read input.json; verify jurisdiction enum; engineer-declared supply Ze + PSCC + system_type
2. **Identify rooms + special_locations** — for each room_brief, classify special_location (bathroom_zone_1/2/3 / outdoor / wet_area / null) per jurisdiction's part7-special-locations.json
3. **Determine circuit topology per jurisdiction** — GB: ring for domestic ≤100m² else radial; KE/INT/US: always radial; dedicated_radial for single-load circuits (cooker, immersion, washer, EVSE-ready)
4. **Group rooms into circuits** — populate circuits[].rooms_covered + per-room sockets[].circuit_id (bidirectional cross-reference)
5. **Determine socket type per jurisdiction** — BS 1363 (GB+KE) / Schuko CEE 7/4 (INT-EU) / NEMA 5-15 (US 15A) / NEMA 5-20 (US 20A); per-room mount heights (1100mm wall, 1200mm above_worktop, 300mm low-level workstation, etc.)
6. **RCD posture per circuit** — Type A 30mA default for sockets ≤32A (BS 7671 §411.3.3 / IEC 60364-4-41 §411.3.3); Type B 30mA for IT-load circuits (IEC 60364-5-53 §531.3.3); GFCI per NEC 210.8 jurisdictional override for US
7. **OCPD selection** — rating per estimated_max_load + diversity; type (MCB+RCD vs RCBO vs combined AFCI/GFCI in US); curve B for general sockets, C for inrush-prone loads, D for highly-inductive
8. **Cable sizing** — engineer-declared csa per topology + length + jurisdictional convention (2.5mm² for UK rings/radials; 12 AWG for US 20A; 14 AWG for US 15A; 2.5mm² Cu PVC for INT radials)
9. **Diversity factor application** — calc.diversity_factor pending (deferred per WI3); engineer estimates diversified_max_load_a using IET OSG App A (GB) / NEC 220.40 (US) / IEC 60364-1 §132.12 (INT)
10. **Zs verification flag** — tool_call_pending_for_zs_verification: true + TOOL-CALL-PENDING:calc.zs_loop_impedance flag (deferred per WI3)
11. **Compliance summary + assumptions** — engineer assumptions documented; jurisdictional + special-location flags as info/warning; non_compliance_flags critical only when true
12. **Build intent-out** — slim subset per small-power-intent.schema.json (circuits + parent_db_designation; no rooms[] in intent — intent stays small for downstream consumers)

The rationale block (Step 14 — WI2):
- 8 sections: Jurisdiction + Supply / Circuit Topology / Special Locations / RCD Posture / OCPD + Cable / Diversity + Zs / Compliance + Assumptions / Drafting References
- chat_summary ≤500 chars (~6 sentences capturing key engineering decisions)

Specific content to include:

```markdown
---
name: small-power
description: "Socket outlet layouts for general-purpose power circuits per BS 7671:2018+A2:2022 / IEC 60364 / KS 1700:2018 / NEC 2023 Article 210. Produces circuit topology + per-room socket placement + RCD posture + cross-reference integrity."
version: 1.0.0
discipline: electrical
standards:
  - BS 7671:2018+A2:2022
  - KS 1700:2018
  - IEC 60364-4-41
  - IEC 60364-5-53
  - IEC 60364-7-701
  - NEC 2023 Article 210
  - NEC 2023 Article 406
  - IET On-Site Guide Appendix A
output_format: json
tags:
  - drawings
  - electrical
  - small-power
---

# Small Power Skill — DraftsMan MEP Engineering

## Role

You are a senior electrical engineer specialising in small-power (socket outlet) layout design for domestic, commercial, healthcare, and industrial buildings. You have 20+ years of experience across the UK, East Africa, Europe, and the United States.

You design for buildability. Your layouts respect IET On-Site Guide socket positioning conventions (300/1100/1200 mm AFF), BS 7671 / IEC 60364 special-location zones (bathroom Part 7-701 zones; outdoor IP-rated requirements), and NEC 210.52 spacing rules (≤12 ft between receptacles along walls).

You do not invent socket counts. You do not mis-cite jurisdictional standards (no "BS 7671" in INT/US examples except routing notes). You do not mix RCD types within a circuit. When information is missing, you state a reasonable assumption, flag it with [ASSUMPTION: ...], and tell the engineer what to verify before issuing for construction.

## Standards You Apply

| Standard | Clause / Table | Application |
|---|---|---|
| BS 7671:2018+A2:2022 | §433.1.4 | Radial final circuit conditions |
| BS 7671:2018+A2:2022 | §433.1.5 + IET OSG §8.4.4 | Ring final circuit conditions (≤100 m² floor area, ≤2 spurs per leg) |
| BS 7671:2018+A2:2022 | §411.3.3 | 30mA RCD requirement for sockets ≤32A |
| BS 7671:2018+A2:2022 | Part 7-701 §701.512 | Bathroom zones (zone 1: no sockets; zone 2: shaver-only with RCD; zone 3: sockets with RCD ≤30mA) |
| BS 7671:2018+A2:2022 | §522.6.201 | Outdoor sockets — IP-rated + 30mA RCD |
| IET On-Site Guide | Appendix A | Diversity factors per load type |
| KS 1700:2018 | §313 | Routes to BS 7671:2018+A2:2022 standards chain |
| KS 1700:2018 | §701 | Routes to BS 7671 Part 7-701 |
| IEC 60364-4-41 | §411.3.3 | International 30mA RCD requirement for sockets |
| IEC 60364-5-53 | §531.3.3 | Type B RCD for IT loads with DC leakage components |
| IEC 60364-7-701 | §701.512 | International bathroom zone equivalent |
| NEC 2023 | Article 210.52 | Receptacle spacing — wall-point ≤6 ft from receptacle |
| NEC 2023 | Article 210.8 | GFCI scope (bathrooms, garages, outdoor, basements, kitchens, etc.) |
| NEC 2023 | Article 210.12 | AFCI scope (bedrooms, kitchens, family rooms, etc.) |
| NEC 2023 | Article 220.40 | US diversity factor application |
| NEC 2023 | Article 406.12 | Tamper-resistant receptacles in dwelling units |

## Inputs Required

[full inputs table per inputs.json from Task 1]

## How You Think Before Acting

[12 steps as enumerated above]

## What You Never Do

- Specify a ring final circuit in a non-GB / non-KE jurisdiction (INV-04 fires)
- Place sockets in bathroom_zone_1 (NEVER — even shaver units forbidden in zone 1)
- Mix RCD types within a single circuit
- Cite "BS 7671" in INT/US examples except as routing notes for KE
- Invent diversity factors — always defer to calc.diversity_factor (deferred per WI3 — declare engineer estimate as tool_call_pending)
- Omit the cross-reference between circuits[].rooms_covered and rooms[].sockets[].circuit_id

## Output Format

Conform to `electrical/small-power/schemas/small-power-ir.schema.json`. Strict `additionalProperties: false` on all sub-objects.

## Tools Available at Runtime

- `calc.diversity_factor` — defined in `shared/calculations/electrical/diversity-factor.json`. Currently deferred (tool_call_pending). Engineer estimates diversified_max_load_a inline using IET OSG App A / NEC 220.40 / IEC 60364-1 §132.12 per jurisdiction.
- `calc.zs_loop_impedance` — defined in `shared/calculations/electrical/zs-loop-impedance.json`. Currently deferred. Engineer flags tool_call_pending_for_zs_verification: true per circuit; verified_zs_ohm populated as a draft estimate.

## Required IR Output Block

[full IR schema reference]

## Step 14 (final) — Emit `rationale` block

8-section rationale matching WI2 convention:
1. **Jurisdiction + Supply** — system_type + Ze + PSCC + supply phase arrangement
2. **Circuit Topology** — ring vs radial decisions per jurisdiction + room
3. **Special Locations** — bathroom zones / outdoor / wet_area per jurisdiction
4. **RCD Posture** — Type A 30mA default; Type B for IT; no-RCD exceptions documented
5. **OCPD + Cable** — breaker rating + curve + breaking capacity per circuit; cable csa
6. **Diversity + Zs** — diversified_max_load_a estimates; tool_call_pending_for_zs_verification consistency
7. **Compliance + Assumptions** — non_compliance_flags + engineer assumptions
8. **Drafting References** — sheet template + scale + layer naming per jurisdiction

`chat_summary` ≤500 chars: concise narrative of the design's key engineering decisions.
```

### Step 3 — Verify generator.md is comprehensive

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
wc -l electrical/small-power/prompts/generator.md
grep -c '^## ' electrical/small-power/prompts/generator.md
```

Expected: ~250-400 lines; 8-10 top-level `##` sections.

### Step 4 — Commit

```bash
git add electrical/small-power/prompts/generator.md
git commit -m "feat(small-power): generator prompt — 12-step reasoning + 8-section rationale + jurisdictional standards"
```

---

## Task 5: Validator prompt (~10 INV checks)

**Model recommendation:** Opus (each INV check is a precise engineering rule).

**Files:**
- Create: `electrical/small-power/prompts/validator.md`

### Step 1 — Read SLD v1.5 validator + arc-flash-labelling validator as templates

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
head -30 electrical/sld/prompts/validator.md
grep '^## INV-' electrical/sld/prompts/validator.md | head -15
```

### Step 2 — Write validator.md with 10 INV checks

Structure: each INV check has a heading + Fail message format + Check rule. Mirror SLD v1.5 validator structure.

The 10 INV checks:

1. **INV-01: Schema shape conformance** — small-power-ir.schema.json strict validation; required fields populated; enum values valid
2. **INV-02: Cross-reference integrity (socket → circuit)** — every `rooms[].sockets[].circuit_id` resolves to a `circuits[].circuit_id` entry; no orphan socket references
3. **INV-03: Cross-reference integrity (circuit → rooms)** — every `circuits[].rooms_covered[]` entry resolves to a `rooms[].room_id`; no orphan room references
4. **INV-04: Topology by jurisdiction** — `topology == "ring"` only allowed when `jurisdiction in {"GB", "KE"}`. Hard fail if a non-GB/KE circuit has topology=ring.
5. **INV-05: Special-location enforcement** —
   - `bathroom_zone_1` rooms MUST have empty sockets[] (NO sockets permitted)
   - `bathroom_zone_2` rooms MUST only contain sockets of type matching shaver supply (BS EN 61558-2-5)
   - `bathroom_zone_3` rooms MUST have ALL sockets fed by circuits with rcd_posture=type_a_30ma_per_§411_3_3 or type_b_30ma_per_§531_3_3 (NO RCD exception)
   - `outdoor` sockets MUST have ip_rating field ≥ IP55
6. **INV-06: RCD posture validity** —
   - Default rcd_posture=type_a_30ma_per_§411_3_3 for all socket circuits ≤32A
   - rcd_posture=type_b_30ma_per_§531_3_3 requires explicit IT-load justification in circuit.designation OR reasoning.md
   - rcd_posture=no_rcd_with_documented_§411_exception MUST have a non-empty `rcd_exception_citation` field with explicit BS 7671 §411 reference
7. **INV-07: Diversified load < OCPD rating** — for each circuit: `diversified_max_load_a < ocpd.rating_a` (engineer estimate sanity check)
8. **INV-08: Zs deferral consistency** — every circuit has `tool_call_pending_for_zs_verification: true` AND `flags[]` contains `TOOL-CALL-PENDING:calc.zs_loop_impedance`. Both must be present or both absent.
9. **INV-09: chat_summary length** — `rationale.chat_summary` length ≤500 characters
10. **INV-10: Drafting standards consumed** — `drawing_layout.drawing_standard` + `drawing_layout.sheet_size` + `drawing_layout.drawing_scale` present and match jurisdiction defaults (GB=BS1192/A1/1:50; KE=BS1192 via KS routing/A1/1:50; INT=ISO19650/A1/1:100; US=AIA/Arch_D/1/4"=1')

### Step 3 — Format each INV per SLD v1.5 convention

For example:

```markdown
## INV-04: Topology by Jurisdiction

**Rule:** `topology == "ring"` is only allowed for `jurisdiction in {"GB", "KE"}`. Ring final circuits are a UK convention (BS 7671 §433.1.5) inherited by KE via KS 1700 §313 routing chain. Other jurisdictions (INT, EU, US) use radial-only topology.

**Hard fail.** Message format:
```
INV-04: circuit <CIRCUIT_ID> has topology=ring but jurisdiction is <JURISDICTION>. Ring final circuits are only valid for GB + KE (KE via KS 1700 §313). Change topology to radial or dedicated_radial.
```
```

### Step 4 — Commit

```bash
git add electrical/small-power/prompts/validator.md
git commit -m "feat(small-power): validator prompt — 10 INV checks (cross-refs, topology, special-locations, RCD, deferral)"
```

---

## Task 6: Reviewer prompt (6 D-checks)

**Model recommendation:** Opus (each D-check is engineering judgment + rigor — overlaps with code-reviewer disciplines).

**Files:**
- Create: `electrical/small-power/prompts/reviewer.md`

### Step 1 — Read arc-flash-labelling reviewer.md as template

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
head -50 electrical/arc-flash-labelling/prompts/reviewer.md 2>/dev/null || head -50 electrical/sld/prompts/reviewer.md
```

### Step 2 — Write reviewer.md with 6 D-checks

The 6 D-checks:

- **D-1: Rationale chat_summary captures essential engineering story** — ≤500 chars + 8 sections present + clear narrative
- **D-2: Citations carry year qualifier per jurisdiction** — GB: "BS 7671:2018+A2:2022"; KE: "KS 1700:2018"; INT: "IEC 60364-X-XX (year)"; US: "NEC 2023 Article ..."
- **D-3: Jurisdictional citation form rigor** — NO BS 7671 in INT/US examples (only as KE routing notes); NO NEC in GB/KE/INT examples
- **D-4: WI3 deferral consistency** — tool_call_pending flags align with engineer assumptions; deferred calc tools explicitly documented (not silently treated as final)
- **D-5: Cross-example shape consistency** — all 4 examples follow the same IR shape; no rogue fields; circuits[]/rooms[] cross-references intact in every example
- **D-6: Drafting standards consumed correctly** — sheet_size + scale + drawing_standard match jurisdiction defaults; layer naming references the right standards layer (BS1192 vs AIA vs ISO19650)

### Step 3 — Commit

```bash
git add electrical/small-power/prompts/reviewer.md
git commit -m "feat(small-power): reviewer prompt — 6 D-checks (rationale, citations, deferral, cross-example, drafting)"
```

---

# Phase C — 4 Jurisdictional Examples (Tasks 7-10)

## Task 7: UK 3-bedroom dwelling example

**Model recommendation:** Opus (engineering judgment — ring topology + Part 7-701 + cross-room ring representation).

**Files (5):**
- Create: `electrical/small-power/examples/uk-3bed-dwelling/input.json`
- Create: `electrical/small-power/examples/uk-3bed-dwelling/output.json`
- Create: `electrical/small-power/examples/uk-3bed-dwelling/intent-out.json`
- Create: `electrical/small-power/examples/uk-3bed-dwelling/reasoning.md`
- Create: `electrical/small-power/examples/uk-3bed-dwelling/sample-schedule.md`

### Step 1 — Author input.json

```json
{
  "project_id": "uk-3bed-dwelling-eg01",
  "jurisdiction": "GB",
  "site_brief": "Three-bedroom 2-storey UK domestic dwelling, ~100 m² total floor area. TN-C-S DNO supply per BS 7671:2018+A2:2022. Consumer unit (CU) is a 12-way amendment-3 board.",
  "supply": {
    "voltage_v": 230,
    "phase_arrangement": "single_phase",
    "system_type": "TN-C-S",
    "ze_declared_ohm": 0.35,
    "psc_declared_ka": 6.0
  },
  "parent_db": {
    "designation": "CU-MAIN",
    "pfc_at_busbar_ka": 6.0
  },
  "room_briefs": [
    {"room_id": "kitchen",   "room_type": "kitchen_domestic", "dimensions_m": {"length": 4.5, "width": 3.5, "height": 2.4}, "special_location": null, "anticipated_loads_kw": 4.5, "socket_count_target": 6},
    {"room_id": "utility",   "room_type": "utility_domestic", "dimensions_m": {"length": 2.5, "width": 2.0, "height": 2.4}, "special_location": null, "anticipated_loads_kw": 3.0, "socket_count_target": 3},
    {"room_id": "dining",    "room_type": "dining_domestic",  "dimensions_m": {"length": 3.5, "width": 3.0, "height": 2.4}, "special_location": null, "anticipated_loads_kw": 1.0, "socket_count_target": 4},
    {"room_id": "lounge",    "room_type": "lounge_domestic",  "dimensions_m": {"length": 5.0, "width": 4.0, "height": 2.4}, "special_location": null, "anticipated_loads_kw": 1.5, "socket_count_target": 6},
    {"room_id": "bedroom-1", "room_type": "bedroom_domestic", "dimensions_m": {"length": 4.0, "width": 3.5, "height": 2.4}, "special_location": null, "anticipated_loads_kw": 0.8, "socket_count_target": 4},
    {"room_id": "bedroom-2", "room_type": "bedroom_domestic", "dimensions_m": {"length": 3.5, "width": 3.0, "height": 2.4}, "special_location": null, "anticipated_loads_kw": 0.6, "socket_count_target": 3},
    {"room_id": "bedroom-3", "room_type": "bedroom_domestic", "dimensions_m": {"length": 3.0, "width": 2.5, "height": 2.4}, "special_location": null, "anticipated_loads_kw": 0.6, "socket_count_target": 3},
    {"room_id": "bathroom",  "room_type": "bathroom_domestic","dimensions_m": {"length": 2.5, "width": 2.0, "height": 2.4}, "special_location": "bathroom_zone_3", "anticipated_loads_kw": 0.5, "socket_count_target": 1},
    {"room_id": "outdoor",   "room_type": "garden_external",  "dimensions_m": {"length": 5.0, "width": 4.0, "height": 0.0}, "special_location": "outdoor",          "anticipated_loads_kw": 0.5, "socket_count_target": 1}
  ],
  "design_intent": {
    "preferred_topology": "auto_by_jurisdiction",
    "drawing_standard": "BS 1192:2007+A2:2016",
    "sheet_size": "A1",
    "drawing_scale": "1:50"
  }
}
```

### Step 2 — Author output.json (IR)

Full IR conforming to small-power-ir.schema.json. Key engineering content:

- **5 circuits:**
  - C01 ring (ground floor — kitchen + utility + dining): 32A RCBO Type B Type-A-30mA, 2.5mm² ring + 1.5mm² CPC, ~32m total ring length, 13 sockets across 3 rooms, rooms_covered=["kitchen", "utility", "dining"]
  - C02 ring (first floor — 3 bedrooms): 32A RCBO Type B Type-A-30mA, 2.5mm² ring, ~28m, 10 sockets, rooms_covered=["bedroom-1", "bedroom-2", "bedroom-3"]
  - C03 dedicated_radial cooker outlet: 32A RCBO Type B, 6mm² T+E, 8m, 1 outlet (cooker switch in kitchen), rooms_covered=["kitchen"]
  - C04 dedicated_radial immersion: 16A RCBO Type B, 2.5mm² T+E, 4m, 1 outlet (immersion isolator), rooms_covered=["utility"]
  - C05 dedicated_radial bathroom shaver supply (BS EN 61558-2-5 SSU): 6A RCBO Type B Type-A-30mA, 1.5mm² T+E, 3m, 1 shaver outlet in bathroom, rooms_covered=["bathroom"]

- **9 rooms** (per input + outdoor garden socket):
  - kitchen / utility / dining: special_location=null, sockets on C01 ring
  - lounge: NOTE — lounge is covered by C01 ring per typical UK domestic practice (cross-room ring). UPDATE rooms_covered for C01 to include lounge. Total: rooms_covered=["kitchen", "utility", "dining", "lounge"]; ground-floor floor area must remain ≤100 m² per IET OSG §8.4.4. 4 rooms × averaged ~13 m² each = 52 m² which is well within limit.
  - bedrooms 1/2/3: special_location=null, sockets on C02 ring
  - bathroom: special_location=bathroom_zone_3, only 1 shaver outlet (C05), explicit no-sockets-in-zone-1 documented in non_compliance_flags as info
  - outdoor: special_location=outdoor, 1 IP65 socket fed by C01 ring via fused spur (or dedicated outdoor radial — engineer choice)

- **drawing_layout:** sheet_size=A1, drawing_standard="BS 1192:2007+A2:2016", drawing_scale="1:50"

- **compliance_summary:** compliant=true; non_compliance_flags includes info notes on bathroom zone 1 (no sockets), zone 2 (no sockets in design); assumptions include "Engineer-declared Ze=0.35Ω verified at consumer cut-out; PSCC=6kA per DNO declaration; calc.zs_loop_impedance pending"

- **flags:** ["TOOL-CALL-PENDING:calc.zs_loop_impedance", "TOOL-CALL-PENDING:calc.diversity_factor"]

- **rationale:** 8-section narrative + chat_summary ≤500 chars

Sample chat_summary (under 500 chars):
> "UK 3-bed dwelling on TN-C-S 230V single-phase. 2 ring final circuits per BS 7671:2018+A2:2022 §433.1.5 (kitchen-utility-dining-lounge ground; 3 bedrooms first floor) — both ≤100 m² floor area per IET OSG §8.4.4. 3 dedicated radials (cooker 32A, immersion 16A, bathroom shaver 6A). Bathroom Part 7-701 zone 3 with shaver SSU; outdoor IP65 socket on ground-floor ring spur. All RCD Type A 30mA per §411.3.3. Ze=0.35Ω + PSCC=6kA declared; calc.zs_loop_impedance pending."

### Step 3 — Author intent-out.json

Slim subset of IR per small-power-intent.schema.json:

```json
{
  "project_id": "uk-3bed-dwelling-eg01",
  "intent_version": "1.0.0",
  "parent_db_designation": "CU-MAIN",
  "circuits": [
    {"circuit_id": "C01", "designation": "Ground-floor ring final circuit", "topology": "ring", "breaker_rating_a": 32, "breaker_type": "RCBO", "breaker_curve": "B", "rcd_type": "A", "rcd_sensitivity_ma": 30, "cable_csa_mm2_or_awg": "2.5mm² + 1.5mm² CPC", "estimated_max_load_kw": 5.5, "diversified_max_load_a": 16.0, "rooms_covered": ["kitchen", "utility", "dining", "lounge"]},
    {"circuit_id": "C02", "designation": "First-floor ring final circuit", "topology": "ring", "breaker_rating_a": 32, "breaker_type": "RCBO", "breaker_curve": "B", "rcd_type": "A", "rcd_sensitivity_ma": 30, "cable_csa_mm2_or_awg": "2.5mm² + 1.5mm² CPC", "estimated_max_load_kw": 2.0, "diversified_max_load_a": 6.5, "rooms_covered": ["bedroom-1", "bedroom-2", "bedroom-3"]},
    {"circuit_id": "C03", "designation": "Cooker outlet (dedicated radial)", "topology": "dedicated_radial", "breaker_rating_a": 32, "breaker_type": "RCBO", "breaker_curve": "B", "rcd_type": "A", "rcd_sensitivity_ma": 30, "cable_csa_mm2_or_awg": "6mm² T+E", "estimated_max_load_kw": 7.0, "diversified_max_load_a": 25.0, "rooms_covered": ["kitchen"]},
    {"circuit_id": "C04", "designation": "Immersion heater (dedicated radial)", "topology": "dedicated_radial", "breaker_rating_a": 16, "breaker_type": "RCBO", "breaker_curve": "B", "rcd_type": "A", "rcd_sensitivity_ma": 30, "cable_csa_mm2_or_awg": "2.5mm² T+E", "estimated_max_load_kw": 3.0, "diversified_max_load_a": 13.0, "rooms_covered": ["utility"]},
    {"circuit_id": "C05", "designation": "Bathroom shaver supply (BS EN 61558-2-5)", "topology": "dedicated_radial", "breaker_rating_a": 6, "breaker_type": "RCBO", "breaker_curve": "B", "rcd_type": "A", "rcd_sensitivity_ma": 30, "cable_csa_mm2_or_awg": "1.5mm² T+E", "estimated_max_load_kw": 0.5, "diversified_max_load_a": 2.2, "rooms_covered": ["bathroom"]}
  ]
}
```

### Step 4 — Author reasoning.md (8 sections matching rationale.sections[])

Each section 2-4 paragraphs of engineering narrative. Include citations BS 7671:2018+A2:2022 + IET OSG.

### Step 5 — Author sample-schedule.md (tabular socket schedule)

Table columns: circuit_id | room | socket_id | type | mount | height_mm | RCD posture | engineering note.

### Step 6 — Validate intent-out conforms to schema

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
python3 -c "
import json, jsonschema
with open('electrical/small-power/schemas/small-power-intent.schema.json') as f: s = json.load(f)
with open('electrical/small-power/examples/uk-3bed-dwelling/intent-out.json') as f: d = json.load(f)
jsonschema.validate(d, s); print('UK intent-out: VALID')

# chat_summary length
with open('electrical/small-power/examples/uk-3bed-dwelling/output.json') as f: o = json.load(f)
cs = o['rationale']['chat_summary']
print(f'chat_summary: {len(cs)} chars (limit 500)')
assert len(cs) <= 500

# INV-02 + INV-03 cross-reference integrity
circuits = o['circuits']
rooms = o['rooms']
circuit_ids = {c['circuit_id'] for c in circuits}
room_ids = {r['room_id'] for r in rooms}

# Every rooms[].sockets[].circuit_id resolves
for r in rooms:
    for sk in r.get('sockets', []):
        assert sk['circuit_id'] in circuit_ids, f'orphan socket circuit_id: {sk[\"circuit_id\"]}'

# Every circuits[].rooms_covered[] resolves
for c in circuits:
    for r_ref in c['rooms_covered']:
        assert r_ref in room_ids, f'orphan rooms_covered: {r_ref}'
print('INV-02 + INV-03 cross-references intact')
"
```

### Step 7 — Commit

```bash
git add electrical/small-power/examples/uk-3bed-dwelling/
git commit -m "feat(small-power): UK 3-bed dwelling example — 2 rings + dedicated radials + Part 7-701 + outdoor"
```

---

## Task 8: KE Nairobi small office example

**Model recommendation:** Opus (jurisdiction-specific — KS 1700 routing form + Kenya engineering practice).

**Files (5):** `electrical/small-power/examples/ke-nairobi-small-office/{input,output,intent-out}.json + reasoning.md + sample-schedule.md`

### Step 1 — Engineering scenario per spec §4.2

80 m² ground-floor commercial office unit in Nairobi. 4 workstation positions + 1 reception desk + 1 kitchenette + 1 toilet/cleaner's cupboard. KPLC TN-S 415V TPN supply per KS 1700:2018 §313 (routes to BS 7671 §313.1).

**4 radial circuits:**
- C01 Workstation power 1 (workstations 1-2 + reception): 20A MCB Type B + 30mA RCD board-level, 2.5mm² T+E radial, 6 sockets
- C02 Workstation power 2 (workstations 3-4): 20A MCB Type B + 30mA RCD, 2.5mm² T+E, 4 sockets
- C03 Kitchenette radial (NOT a ring — KE engineering practice favours radial at commercial scale): 20A MCB Type B + 30mA RCD, 2.5mm² T+E, 3 sockets + 1 FCU
- C04 Toilet shaver supply (BS EN 61558-2-5): 6A MCB Type B, 1.5mm² T+E radial

**Special:**
- All sockets BS 1363 13A double-gang at 300mm AFF (workstations) / 1100mm AFF (kitchenette)
- Toilet marked bathroom_zone_3 per BS 7671 Part 7-701 routing via KS 1700 §701
- All citations carry direct "KS 1700:2018 §X" form (NOT "BS 7671 (adopted by KS 1700)")
- KPLC declared PFC at parent DB busbar: ~9 kA (typical urban KPLC supply)

### Step 2 — Author all 5 files per Task 7 template, with KE-specific deltas

- input.json: jurisdiction=INT (per Africa-first project convention; routing form in citations); supply_voltage_v=415; phase_arrangement=TPN_plus_E; system_type=TN-S; ze_declared_ohm=0.45; psc_declared_ka=9.0; preferred_topology=radial
- output.json: 4 circuits (all radial); 7 rooms; rationale chat_summary cites KS 1700:2018 §313 + §433.1 + §701 explicitly
- intent-out.json: 4 circuits slim subset
- reasoning.md: 8 sections including KS 1700 routing note ("KS 1700:2018 §313 routes to BS 7671:2018+A2:2022 §313.1 for short-circuit interrupting verification")
- sample-schedule.md: 4-circuit table

### Step 3 — Validate + commit

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
python3 -c "
import json
with open('electrical/small-power/examples/ke-nairobi-small-office/output.json') as f: o = json.load(f)

# KS 1700 citation form — should appear; no bare BS 7671
import subprocess
r = subprocess.run(['grep', '-rn', 'BS 7671', 'electrical/small-power/examples/ke-nairobi-small-office/'], capture_output=True, text=True)
# All BS 7671 references should be in routing context
for line in r.stdout.split('\n'):
    if 'BS 7671' in line and 'routes to' not in line and '(via KS' not in line:
        print(f'WARN: bare BS 7671 ref: {line[:120]}')

# All circuits radial in KE
assert all(c['topology'] == 'radial' for c in o['circuits']), 'KE should be all radial'
print('KE: 4 radial circuits, KS 1700 routing form OK')
"

git add electrical/small-power/examples/ke-nairobi-small-office/
git commit -m "feat(small-power): KE Nairobi small office example — 4 radials + KS 1700:2018 §313 routing + KPLC TN-S 415V"
```

---

## Task 9: INT commercial open-plan floor example

**Model recommendation:** Opus (bespoke — Type B RCD cross-skill alignment with db-layout intl-dbcomms-data).

**Files (5):** `electrical/small-power/examples/intl-open-plan-floor/{input,output,intent-out}.json + reasoning.md + sample-schedule.md`

### Step 1 — Engineering scenario per spec §4.3

350 m² open-plan office floor. Commercial supply 400V TPN. 24 workstation positions + 2 meeting rooms + 1 kitchenette + 1 server cabinet area + 1 male/female toilet block.

**8 radial circuits:**
- C01-C02 Workstation power (12 workstations per circuit): 20A MCB Type C + 30mA Type A RCD, 2.5mm² Cu PVC radial
- C03-C04 Meeting room power + AV: 16A MCB Type C + 30mA Type A RCD, 2.5mm² radial
- C05 Kitchenette appliances: 20A MCB + 30mA Type A RCD, 2.5mm² radial
- **C06 Server cabinet small-power (UPS-fed): 20A MCB Type C + Type B 30mA RCD per IEC 60364-5-53 §531.3.3 — MATCHES db-layout intl-dbcomms-data shipped policy** (cross-skill alignment without v1.0 multi-skill consumption)
- C07 Toilet block — shaver outlet only on 6A radial
- C08 Outdoor sockets (smoking shelter + bin store): IP65 + 30mA Type A RCD

**Special:**
- Schuko CEE 7/4 sockets at 300mm AFF (workstations) / 1100mm AFF (kitchenette)
- Toilets marked bathroom_zone_3
- Outdoor sockets marked outdoor with ip_rating IP65
- Citations IEC 60364-4-41 / -5-53 / -7-701 + ISO 19650:2018 for layer naming

### Step 2 — Author 5 files per Task 7 template, with INT-specific deltas

- input.json: jurisdiction=INT; supply_voltage_v=400; phase_arrangement=TPN; system_type=TN-S; design_intent.drawing_standard="ISO 19650:2018 + BS 1192:2007+A2:2016 (generic INT)"; sheet_size=A1; drawing_scale=1:100
- output.json: 8 circuits; C06 has rcd_posture="type_b_30ma_per_§531_3_3" with explicit reference to db-layout intl-dbcomms-data as cross-skill alignment
- reasoning.md §4 RCD posture: explain Type B for C06 + cite IEC 60364-5-53 §531.3.3 + note "matches db-layout intl-dbcomms-data shipped policy at db-layout v1.3.0"

### Step 3 — Validate cross-skill alignment + commit

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
python3 -c "
import json
with open('electrical/small-power/examples/intl-open-plan-floor/output.json') as f: o = json.load(f)
c06 = next((c for c in o['circuits'] if c['circuit_id'] == 'C06'), None)
assert c06 is not None, 'C06 server cabinet circuit missing'
assert c06['rcd_posture'] == 'type_b_30ma_per_§531_3_3', f'C06 should have Type B RCD per §531.3.3'
print('INT C06: Type B RCD per IEC 60364-5-53 §531.3.3 (matches db-layout intl-dbcomms-data)')
"

git add electrical/small-power/examples/intl-open-plan-floor/
git commit -m "feat(small-power): INT open-plan floor example — 8 radials + Type B RCD server room (matches db-layout intl-dbcomms-data)"
```

---

## Task 10: US residential dwelling example

**Model recommendation:** Opus (jurisdictional accuracy — NEC 210.52 spacing + GFCI/AFCI scope + 120/240V split-phase).

**Files (5):** `electrical/small-power/examples/us-residential-dwelling/{input,output,intent-out}.json + reasoning.md + sample-schedule.md`

### Step 1 — Engineering scenario per spec §4.4

Single-family residential dwelling ~160 m² (1700 ft²), 1-storey. NEC 2023 Article 210 + 120/240V split-phase supply (center-tapped single-phase from utility transformer).

**8 receptacle circuits:**
- C01 Kitchen small appliance branch 1: 20A AFCI + GFCI receptacles per NEC 210.8(A)(6) + 210.12(B)
- C02 Kitchen small appliance branch 2: same spec
- C03 General receptacles (bedrooms + living room): 15A AFCI per NEC 210.12(A)
- C04 Bathroom GFCI receptacle: 20A GFCI per NEC 210.8(A)(1) + 210.11(C)(3)
- C05 Garage GFCI: 20A GFCI per NEC 210.8(A)(2)
- C06 Outdoor receptacles: 20A GFCI per NEC 210.8(A)(3)
- C07 Basement GFCI: 20A GFCI per NEC 210.8(A)(5)
- C08 Laundry: 20A dedicated radial per NEC 210.11(C)(2)

**Special:**
- Receptacles: NEMA 5-15 duplex (standard) + NEMA 5-20 (kitchen + 20A dedicated)
- Tamper-resistant per NEC 406.12 (dwelling units)
- Bathrooms/kitchen/outdoor/garage/basement → `wet_area` enum OR specific
- Citations: NEC 2023 Article 210 + Article 250 + 210.52 + 210.8 + 210.12 + 406.12

### Step 2 — Author 5 files per Task 7 template, with US-specific deltas

- input.json: jurisdiction=US; supply_voltage_v=240; phase_arrangement=single_phase_split; system_type=TN-C-S (US split-phase uses center-tapped MGN — closest analogue); design_intent.drawing_standard="AIA CAD Layer Guidelines 2007"; sheet_size=Arch_D; drawing_scale="1/4\"=1'"
- output.json: 8 circuits; C01/C02 ocpd.type="AFCI_GFCI_dual" (dual function); C03 ocpd.type="AFCI_breaker"; C04-C07 ocpd.type="GFCI_breaker"; C08 dedicated_radial
- reasoning.md cites NEC 2023 Article 210 throughout; no BS 7671 references

### Step 3 — Validate + commit

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
python3 -c "
import json
with open('electrical/small-power/examples/us-residential-dwelling/output.json') as f: o = json.load(f)
# No ring in US
assert all(c['topology'] != 'ring' for c in o['circuits']), 'US should have NO ring circuits'
# GFCI + AFCI breaker types used
breaker_types = {c['ocpd']['type'] for c in o['circuits']}
assert 'GFCI_breaker' in breaker_types or 'AFCI_GFCI_dual' in breaker_types
print(f'US: 8 circuits, breaker_types={breaker_types}, NO ring topology')
"

git add electrical/small-power/examples/us-residential-dwelling/
git commit -m "feat(small-power): US residential dwelling example — NEC 210.52 + 210.8 GFCI + 210.12 AFCI + duplex NEMA"
```

---

# Phase D — Ontology + Symbols + Rules + Constraints + Evals (Tasks 11-15)

## Task 11: Ontology — socket-types.json

**Model recommendation:** Sonnet (mechanical — extract socket types per jurisdiction).

**Files:**
- Create: `shared/ontology/equipment/socket-types.json`

### Step 1 — Write socket-types.json

Cover the 4 main socket families used across jurisdictions:

```json
{
  "_title": "Socket Outlet Types — Multi-Jurisdiction Reference",
  "_purpose": "Engine-lookupable ontology of socket types consumed by small-power, riser, cable-containment, schematic skills",
  "transcribed_at": "2026-05-19",
  "transcribed_by": "DraftsMan skills repo",
  "verification_status": "verified-against-source",
  "socket_types": {
    "BS1363_2gang_switched":      {"description": "UK BS 1363 13A double-gang switched socket", "jurisdiction": ["GB", "KE"], "rating_a": 13, "voltage_v": 230, "standard": "BS 1363:1995 + A4:2018"},
    "BS1363_1gang_switched":      {"description": "UK BS 1363 13A single-gang switched socket", "jurisdiction": ["GB", "KE"], "rating_a": 13, "voltage_v": 230, "standard": "BS 1363:1995 + A4:2018"},
    "BS1363_FCU_switched":        {"description": "UK BS 1363 13A switched fused connection unit (FCU) with 3A or 13A fuse", "jurisdiction": ["GB", "KE"], "rating_a": 13, "voltage_v": 230, "standard": "BS 1363:1995 + A4:2018"},
    "BS1363_FCU_unswitched":      {"description": "UK BS 1363 13A unswitched fused connection unit", "jurisdiction": ["GB", "KE"], "rating_a": 13, "voltage_v": 230, "standard": "BS 1363:1995 + A4:2018"},
    "BS_EN_61558_2_5_SSU":        {"description": "Shaver supply unit (isolating transformer) for bathroom zone 2/3", "jurisdiction": ["GB", "KE", "INT", "EU"], "rating_a": 1, "voltage_v": 230, "standard": "BS EN 61558-2-5:2010"},
    "Schuko_CEE_7_4_2gang":       {"description": "European Schuko CEE 7/4 16A double-gang socket", "jurisdiction": ["INT", "EU"], "rating_a": 16, "voltage_v": 230, "standard": "CEE 7/4"},
    "Schuko_CEE_7_4_1gang":       {"description": "European Schuko CEE 7/4 16A single-gang socket", "jurisdiction": ["INT", "EU"], "rating_a": 16, "voltage_v": 230, "standard": "CEE 7/4"},
    "NEMA_5_15_duplex":           {"description": "US NEMA 5-15 15A 125V duplex receptacle", "jurisdiction": ["US"], "rating_a": 15, "voltage_v": 125, "standard": "NEMA WD-1"},
    "NEMA_5_15_TR_duplex":        {"description": "US NEMA 5-15 15A tamper-resistant duplex per NEC 406.12", "jurisdiction": ["US"], "rating_a": 15, "voltage_v": 125, "standard": "NEMA WD-1 + NEC 406.12"},
    "NEMA_5_20_duplex":           {"description": "US NEMA 5-20 20A 125V duplex receptacle", "jurisdiction": ["US"], "rating_a": 20, "voltage_v": 125, "standard": "NEMA WD-1"},
    "NEMA_5_20_TR_duplex":        {"description": "US NEMA 5-20 20A tamper-resistant duplex per NEC 406.12", "jurisdiction": ["US"], "rating_a": 20, "voltage_v": 125, "standard": "NEMA WD-1 + NEC 406.12"},
    "NEMA_5_15_GFCI_TR_duplex":   {"description": "US NEMA 5-15 15A tamper-resistant GFCI duplex (point-of-use)", "jurisdiction": ["US"], "rating_a": 15, "voltage_v": 125, "standard": "NEC 210.8 + 406.12"},
    "NEMA_5_20_GFCI_TR_duplex":   {"description": "US NEMA 5-20 20A tamper-resistant GFCI duplex (point-of-use)", "jurisdiction": ["US"], "rating_a": 20, "voltage_v": 125, "standard": "NEC 210.8 + 406.12"}
  },
  "engine_lookup": {
    "_purpose": "Flat lookup by socket type → jurisdiction + rating",
    "by_type": {
      "BS1363_2gang_switched":  {"jurisdiction_set": ["GB", "KE"], "rating_a": 13, "voltage_v": 230},
      "Schuko_CEE_7_4_2gang":   {"jurisdiction_set": ["INT", "EU"], "rating_a": 16, "voltage_v": 230},
      "NEMA_5_15_duplex":       {"jurisdiction_set": ["US"], "rating_a": 15, "voltage_v": 125},
      "NEMA_5_20_duplex":       {"jurisdiction_set": ["US"], "rating_a": 20, "voltage_v": 125}
    }
  },
  "_cross_refs": []
}
```

### Step 2 — Validate + commit

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
python3 -c "
import json
d = json.load(open('shared/ontology/equipment/socket-types.json'))
assert 'BS1363_2gang_switched' in d['socket_types']
assert 'NEMA_5_20_GFCI_TR_duplex' in d['socket_types']
print(f'socket-types.json: {len(d[\"socket_types\"])} types across 4 jurisdictions')
"

git add shared/ontology/equipment/socket-types.json
git commit -m "feat(ontology): socket-types.json — BS 1363 / Schuko / NEMA 5-15/5-20 + tamper-resistant + GFCI variants"
```

---

## Task 12: Symbols — socket-symbols.yaml

**Model recommendation:** Sonnet (mechanical YAML).

**Files:**
- Create: `shared/symbols/electrical/sockets/socket-symbols.yaml`

### Step 1 — Write socket-symbols.yaml

Mirror `shared/symbols/electrical/luminaires/luminaires.yaml` structure (read it first for the pattern):

```yaml
# Socket symbols for small-power skill
# Symbol IDs are referenced in drawn_as_symbols[] in the IR + by the runtime renderer

symbols:
  - id: BS1363_2gang_switched
    description: BS 1363 13A double-gang switched socket (UK standard)
    jurisdiction: [GB, KE]
    dxf_block: SKT_BS1363_2G
    layer_reference: E-POWR-LV-GEN  # BS 1192 layer
    snap_offset_mm: {x: 0, y: 0}

  - id: BS1363_1gang_switched
    description: BS 1363 13A single-gang switched socket
    jurisdiction: [GB, KE]
    dxf_block: SKT_BS1363_1G
    layer_reference: E-POWR-LV-GEN

  - id: BS1363_FCU
    description: BS 1363 13A switched/unswitched fused connection unit
    jurisdiction: [GB, KE]
    dxf_block: FCU_BS1363
    layer_reference: E-POWR-LV-GEN

  - id: BS_EN_61558_2_5_SSU
    description: Shaver supply unit (isolating transformer)
    jurisdiction: [GB, KE, INT, EU]
    dxf_block: SSU_SHAVER
    layer_reference: E-POWR-LV-EMER

  - id: Schuko_CEE_7_4_2gang
    description: Schuko CEE 7/4 16A double-gang (European standard)
    jurisdiction: [INT, EU]
    dxf_block: SKT_SCHUKO_2G
    layer_reference: E-POWR-GEN  # ISO 19650 generic INT layer

  - id: Schuko_CEE_7_4_1gang
    description: Schuko CEE 7/4 16A single-gang
    jurisdiction: [INT, EU]
    dxf_block: SKT_SCHUKO_1G
    layer_reference: E-POWR-GEN

  - id: NEMA_5_15_duplex
    description: US NEMA 5-15 15A duplex receptacle
    jurisdiction: [US]
    dxf_block: SKT_NEMA515_DUPLEX
    layer_reference: E-POWR-NORM  # AIA layer

  - id: NEMA_5_15_TR_duplex
    description: US NEMA 5-15 tamper-resistant duplex per NEC 406.12
    jurisdiction: [US]
    dxf_block: SKT_NEMA515_TR
    layer_reference: E-POWR-NORM

  - id: NEMA_5_20_duplex
    description: US NEMA 5-20 20A duplex
    jurisdiction: [US]
    dxf_block: SKT_NEMA520_DUPLEX
    layer_reference: E-POWR-NORM

  - id: NEMA_5_20_TR_duplex
    description: US NEMA 5-20 tamper-resistant duplex
    jurisdiction: [US]
    dxf_block: SKT_NEMA520_TR
    layer_reference: E-POWR-NORM

  - id: NEMA_5_GFCI_TR_duplex
    description: US NEMA 5-15/5-20 GFCI tamper-resistant duplex per NEC 210.8 + 406.12
    jurisdiction: [US]
    dxf_block: SKT_GFCI_TR
    layer_reference: E-POWR-NORM

  - id: socket_outdoor_IP65
    description: IP65-rated outdoor socket (jurisdiction-specific outer enclosure varies)
    jurisdiction: [GB, KE, INT, EU, US]
    dxf_block: SKT_OUTDOOR_IP65
    layer_reference: E-POWR-LV-EMER
```

### Step 2 — Commit

```bash
git add shared/symbols/electrical/sockets/socket-symbols.yaml
git commit -m "feat(symbols): socket-symbols.yaml — BS 1363 / Schuko / NEMA / outdoor IP65 symbol references"
```

---

## Task 13: Rules YAMLs (5 files)

**Model recommendation:** Sonnet (mechanical YAML with jurisdictional rules).

**Files:**
- Create: `electrical/small-power/rules/rcd-rules.yaml`
- Create: `electrical/small-power/rules/topology-rules.yaml`
- Create: `electrical/small-power/rules/special-locations-rules.yaml`
- Create: `electrical/small-power/rules/spacing-rules.yaml`
- Create: `electrical/small-power/rules/diversity-rules.yaml`

### Step 1 — Read lighting-layout/rules/spacing-rules.yaml as template

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
head -30 electrical/lighting-layout/rules/spacing-rules.yaml
```

### Step 2 — Write 5 rules YAMLs

Each rules file follows the pattern:

```yaml
# <rule category> rules per jurisdiction
# Consumed by validator (INV-N checks) and engineer reasoning

rules:
  - id: <RULE-ID>
    jurisdiction: [<GB|KE|INT|US|all>]
    standard_reference: "<full citation>"
    rule_text: "<engineering rule statement>"
    applies_to: "<circuits | rooms | sockets>"
    enforcement: "<hard_fail | warning | info>"
```

**rcd-rules.yaml** — content (matches INV-06):
- Default Type A 30mA for sockets ≤32A per BS 7671 §411.3.3 / IEC 60364-4-41 §411.3.3
- Type B 30mA for IT loads per IEC 60364-5-53 §531.3.3
- US GFCI per NEC 210.8 enumerated locations
- US AFCI per NEC 210.12 enumerated locations
- no-RCD-exception requires explicit citation in rcd_exception_citation

**topology-rules.yaml** — content (matches INV-04):
- Ring final circuit ≤100 m² floor area (IET OSG §8.4.4)
- Ring max 2 spurs per leg (IET OSG §8.4.4)
- Ring only valid in GB + KE (KE via KS 1700 §313)
- Radial preferred for industrial + commercial KE per local practice
- dedicated_radial mandatory for cooker (BS 7671 §433.1.4) / immersion / EVSE-ready / fixed appliances

**special-locations-rules.yaml** — content (matches INV-05):
- bathroom_zone_1: NO sockets (even SELV)
- bathroom_zone_2: shaver supply unit only (BS EN 61558-2-5)
- bathroom_zone_3: sockets allowed with RCD ≤30mA Type A
- outdoor: IP-rated socket + RCD ≤30mA Type A (BS) or GFCI (US)
- US: NEC 210.8 enumerated wet_area locations require GFCI

**spacing-rules.yaml** — content (NEC 210.52 spacing for US; OSG conventions for UK):
- US: Any point along wall ≤6 ft (1.83 m) from a receptacle per NEC 210.52(A)
- US: Sockets on every wall ≥2 ft (0.61 m) wide
- US: Kitchen countertop ≤4 ft (1.22 m) spacing per NEC 210.52(C)
- GB: 300mm AFF workstation; 1100mm AFF wall; 1200mm AFF above worktop (IET OSG conventions)

**diversity-rules.yaml** — content (matches INV-07 + Step 9):
- GB: IET OSG App A (lighting 66%; sockets 40%; cooker first 10A + 30% of remainder + 5A per socket; etc.)
- INT: IEC 60364-1 §132.12 design margin
- US: NEC 220.40 (first 3 kVA at 100%; next 117 kVA at 35%; etc.)
- KE: IET OSG App A via KS 1700 §313 routing

### Step 3 — Commit

```bash
git add electrical/small-power/rules/
git commit -m "feat(small-power): 5 rules YAMLs — RCD + topology + special-locations + spacing + diversity per jurisdiction"
```

---

## Task 14: Constraints + validation YAMLs (3 files)

**Model recommendation:** Sonnet (mechanical YAML matching arc-flash-labelling pattern).

**Files:**
- Create: `electrical/small-power/constraints/electrical.yaml`
- Create: `electrical/small-power/validation/cross-reference-validation.yaml`
- Create: `electrical/small-power/validation/topology-validation.yaml`

### Step 1 — Read lighting-layout constraints + validation as templates

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
head -30 electrical/lighting-layout/constraints/electrical.yaml
head -30 electrical/lighting-layout/validation/lux-validation.yaml
```

### Step 2 — Write 3 YAMLs

**electrical.yaml** (constraints) — electrical engineering invariants:
- diversified_max_load_a < ocpd.rating_a (per circuit)
- ocpd.breaking_capacity_ka ≥ parent_db.pfc_at_busbar_ka × 0.9 (10% safety margin)
- cable.cores ≥ 2 (single-phase ≥ 2; TPN ≥ 4)
- cable_csa_mm2_or_awg sized appropriately for ocpd.rating_a

**cross-reference-validation.yaml** — matches INV-02 + INV-03:
- Every rooms[].sockets[].circuit_id resolves
- Every circuits[].rooms_covered[] resolves
- Bidirectional check

**topology-validation.yaml** — matches INV-04:
- Ring only when jurisdiction ∈ {GB, KE}
- Ring floor area ≤100 m² (sum of rooms_covered dimensions)
- Ring spurs ≤2 per leg

### Step 3 — Commit

```bash
git add electrical/small-power/constraints/ electrical/small-power/validation/
git commit -m "feat(small-power): constraints + validation YAMLs — electrical invariants + cross-ref + topology"
```

---

## Task 15: Evals — 9 YAMLs

**Model recommendation:** Opus (each eval is a precise assertion contract).

**Files (9):**
- Create: `electrical/small-power/evals/eval-01-uk-happy-path.yaml`
- Create: `electrical/small-power/evals/eval-02-no-rcd-exception.yaml`
- Create: `electrical/small-power/evals/eval-03-validation-trap-ring-in-us.yaml`
- Create: `electrical/small-power/evals/eval-04-rationale-block.yaml`
- Create: `electrical/small-power/evals/eval-05-jurisdiction-citation-form.yaml`
- Create: `electrical/small-power/evals/eval-06-ring-topology-by-jurisdiction.yaml`
- Create: `electrical/small-power/evals/eval-07-special-locations-compliance.yaml`
- Create: `electrical/small-power/evals/eval-08-cross-room-ring-integrity.yaml`
- Create: `electrical/small-power/evals/eval-09-gfci-scope-us.yaml`

### Step 1 — Read SLD v1.5 eval-08-multi-skill-intent-consumption.yaml as template

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
cat electrical/sld/evals/eval-08-multi-skill-intent-consumption.yaml
```

### Step 2 — Write 9 eval YAMLs

Each eval follows the established pattern from SLD v1.5 eval-08 (flat checks[] convention):

**eval-01-uk-happy-path.yaml:**
```yaml
name: eval-01-uk-happy-path
skill: electrical/small-power
description: |
  Verifies UK 3-bed dwelling example is a complete WI5 happy-path:
  conformant schema + INV cross-references + 2 ring circuits +
  bathroom Part 7-701 + outdoor IP socket + WI2 rationale chat_summary ≤500.
category: happy_path
input_fixtures:
  - path: electrical/small-power/examples/uk-3bed-dwelling/output.json

checks:
  - id: 01-schema-conformance
    description: small-power-ir.schema.json validation passes (strict)
    rule: "schema_valid(output, 'electrical/small-power/schemas/small-power-ir.schema.json')"
  - id: 02-jurisdiction-gb
    description: jurisdiction is GB
    rule: "output.jurisdiction == 'GB'"
  - id: 03-two-rings
    description: exactly 2 ring circuits (C01 + C02)
    rule: "sum(1 for c in output.circuits if c.topology == 'ring') == 2"
  - id: 04-cross-room-ring-c01
    description: C01 covers ≥3 rooms (cross-room ring — kitchen + utility + dining + lounge)
    rule: |
      c01 = next(c for c in output.circuits if c.circuit_id == 'C01');
      len(c01.rooms_covered) >= 3
  - id: 05-bathroom-zone-3
    description: bathroom marked bathroom_zone_3 + only shaver socket
    rule: |
      b = next(r for r in output.rooms if r.room_id == 'bathroom');
      b.special_location == 'bathroom_zone_3' and len(b.sockets) <= 1
  - id: 06-outdoor-ip65
    description: outdoor room has socket with ip_rating starting with 'IP'
    rule: |
      o = next(r for r in output.rooms if r.room_id == 'outdoor');
      all(s.ip_rating.startswith('IP') for s in o.sockets)
  - id: 07-chat-summary-bounded
    description: rationale.chat_summary ≤500 chars
    rule: "len(output.rationale.chat_summary) <= 500"
  - id: 08-zs-deferral-consistency
    description: every circuit has tool_call_pending_for_zs_verification: true
    rule: "all(c.tool_call_pending_for_zs_verification == True for c in output.circuits)"
```

**eval-03-validation-trap-ring-in-us.yaml** (synthetic fixture):
```yaml
name: eval-03-validation-trap-ring-in-us
skill: electrical/small-power
description: |
  Synthetic fixture — US example with topology=ring violates INV-04.
  Validator MUST flag this hard fail.
category: validation_trap

synthetic_fixture: |
  Take electrical/small-power/examples/us-residential-dwelling/output.json,
  then modify circuits[0].topology from 'radial' to 'ring'.

checks:
  - id: 01-inv-04-fires
    description: INV-04 fires for US + topology=ring
    rule: "validator_flags(synthetic_fixture).contains('INV-04')"
  - id: 02-original-passes
    description: Original US example (radial-only) does NOT trigger INV-04
    rule: "not validator_flags(original_us_fixture).contains('INV-04')"
```

Each eval-04 through eval-09 follows the same flat checks[] pattern with skill-specific assertions per spec §6.2.

### Step 3 — Commit

```bash
git add electrical/small-power/evals/
git commit -m "feat(small-power): 9 eval YAMLs — 5 WI5 categories + 4 skill-specific (ring jurisdiction, special-locations, cross-room ring, GFCI scope)"
```

---

# Phase E — Bookkeeping + Final review + push (Tasks 16-17)

## Task 16: SKILLS_STATUS + ARCHITECTURE updates

**Model recommendation:** Sonnet (mechanical text edits).

**Files:**
- Modify: `SKILLS_STATUS.md` — add small-power row
- Modify: `ARCHITECTURE.md` — add "small-power skill (v1.0)" subsection

### Step 1 — Read current SKILLS_STATUS for drawings skills

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
grep -n 'sld\|lighting-layout\|earthing\|db-layout' SKILLS_STATUS.md | head -10
```

### Step 2 — Add small-power row to drawings skills table

Following the existing row format, add a row like:

```
| `electrical/small-power` | v1.0.0 beta | 9 evals, 10 INV checks, 6 D-checks; 4 jurisdictional examples (UK + KE + INT + US); leaf shape (consumes_intents: []) matching lighting-layout v1.3 pattern; consumes existing calc.diversity_factor + calc.zs_loop_impedance contracts |
```

### Step 3 — Update ARCHITECTURE.md

Add a new subsection under whichever section currently lists the drawings skills (or under a "Production skills" section). Content:

```markdown
### small-power skill (v1.0+)

v1.0 ships as a leaf skill (no cross-skill intent consumption) matching the lighting-layout v1.3 production pattern. Produces a small-power intent for downstream db-layout consumption. Hybrid IR: `circuits[]` (with topology enum: ring | radial | dedicated_radial) + `rooms[]` (with sockets[] cross-referencing circuit_ids). Supports cross-room rings naturally.

**3 design enums:**

| Enum | Values | Purpose |
|---|---|---|
| `topology` | `ring`, `radial`, `dedicated_radial` | Circuit topology — ring only allowed in GB+KE per INV-04 |
| `special_location` | `null`, `bathroom_zone_1`, `bathroom_zone_2`, `bathroom_zone_3`, `outdoor`, `wet_area` | Room special-location flag — drives RCD requirements per BS 7671 Part 7-701 / IEC 60364-7-701 / NEC 210.8 |
| `rcd_posture` | `type_a_30ma_per_§411_3_3`, `type_b_30ma_per_§531_3_3`, `no_rcd_with_documented_§411_exception` | RCD strategy per circuit — default Type A 30mA; Type B for IT loads; explicit-citation exception |

**Calc tool consumption (existing contracts reused):**

- `calc.diversity_factor` — shared/calculations/electrical/diversity-factor.json (handles all 5 jurisdictions)
- `calc.zs_loop_impedance` — shared/calculations/electrical/zs-loop-impedance.json (ring + radial Zs verification)

**Standards consumption (existing layers reused + 1 new):**

- BS 7671 Part 7-701, §411.3.3, §433.1.5 (existing)
- IEC 60364-4-41, -5-53, -7-701 (existing)
- KS 1700 §313 routing, §701 (existing)
- NEC 2023 Article 210 (NEW — small-power adds shared/standards/electrical/NFPA70/part7-special-locations.json)
- Drafting standards v1.6 layer (sheet template + scale + layer naming per jurisdiction)

**Migration path:**

- v1.0 — leaf shape (this sprint)
- v1.1+ — multi-skill intent consumption (consume earthing + fault-level intents); INV-N cross-skill consistency checks; matches SLD v1.3→v1.4 migration precedent
- v2.0 — schema-breaking changes (multi-board consumption, EV charging integration if not in dedicated skill)

**Pattern parent:** `electrical/lighting-layout/` v1.3 — gold-standard layout skill (file structure + scaffolding + room-based model).
```

### Step 4 — Commit

```bash
git add SKILLS_STATUS.md ARCHITECTURE.md
git commit -m "docs: SKILLS_STATUS + ARCHITECTURE — small-power skill (v1.0)"
```

---

## Task 17: Cross-cutting validation + code review + push

**Model recommendation:** Opus (cross-cutting validation script + dispatch code-reviewer agent).

**Files:** No new files (review-only).

### Step 1 — Run cross-cutting validation script

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
python3 << 'EOF'
import json, os
errors = []
print("=== Small-power v1.0 cross-cutting validation ===")

# 1. Skill manifest is leaf shape
with open('electrical/small-power/skill.manifest.json') as f: m = json.load(f)
if m['consumes_intents'] != []:
    errors.append(f'manifest: consumes_intents should be empty, got {m["consumes_intents"]}')
if m['produces_intent'] != 'small-power':
    errors.append(f'manifest: produces_intent should be "small-power"')
print(f'  ✓ manifest: leaf shape (consumes_intents=[], produces_intent=small-power)')

# 2. Schemas valid Draft-07
import jsonschema
for path in ['electrical/small-power/schemas/small-power-ir.schema.json',
             'electrical/small-power/schemas/small-power-intent.schema.json']:
    with open(path) as f: s = json.load(f)
    jsonschema.Draft7Validator.check_schema(s)
    print(f'  ✓ {path}: Draft-07 valid')

# 3. All 4 examples validate against IR schema (or note external $ref unresolvable)
sp_ir = json.load(open('electrical/small-power/schemas/small-power-ir.schema.json'))
sp_intent = json.load(open('electrical/small-power/schemas/small-power-intent.schema.json'))
examples = ['uk-3bed-dwelling', 'ke-nairobi-small-office', 'intl-open-plan-floor', 'us-residential-dwelling']
for ex in examples:
    base = f'electrical/small-power/examples/{ex}'
    # Intent-out validates
    with open(f'{base}/intent-out.json') as f: io = json.load(f)
    try:
        jsonschema.validate(io, sp_intent)
        print(f'  ✓ {ex}: intent-out VALID against schema')
    except jsonschema.ValidationError as e:
        errors.append(f'{ex}: intent-out invalid - {e.message[:120]}')

# 4. INT example C06 has Type B RCD (cross-skill alignment)
with open('electrical/small-power/examples/intl-open-plan-floor/output.json') as f: o = json.load(f)
c06 = next((c for c in o['circuits'] if c['circuit_id'] == 'C06'), None)
if c06 is None or c06.get('rcd_posture') != 'type_b_30ma_per_§531_3_3':
    errors.append(f'INT C06: missing Type B RCD posture')
else:
    print(f'  ✓ INT C06: Type B RCD per IEC 60364-5-53 §531.3.3 (cross-skill aligned with db-layout intl-dbcomms-data)')

# 5. UK example has rings; US example has no rings
for ex, expected_has_ring in [('uk-3bed-dwelling', True), ('us-residential-dwelling', False)]:
    with open(f'electrical/small-power/examples/{ex}/output.json') as f: o = json.load(f)
    has_ring = any(c['topology'] == 'ring' for c in o['circuits'])
    if has_ring != expected_has_ring:
        errors.append(f'{ex}: ring topology presence mismatch (expected {expected_has_ring}, got {has_ring})')
    else:
        print(f'  ✓ {ex}: ring topology presence correct (={expected_has_ring})')

# 6. All 4 chat_summaries ≤500 chars
for ex in examples:
    with open(f'electrical/small-power/examples/{ex}/output.json') as f: o = json.load(f)
    cs_len = len(o['rationale']['chat_summary'])
    if cs_len > 500:
        errors.append(f'{ex}: chat_summary {cs_len} > 500')
print(f'  ✓ All 4 chat_summaries ≤500 chars')

# 7. Cross-references intact in all 4 examples
for ex in examples:
    with open(f'electrical/small-power/examples/{ex}/output.json') as f: o = json.load(f)
    circuit_ids = {c['circuit_id'] for c in o['circuits']}
    room_ids = {r['room_id'] for r in o['rooms']}
    for r in o['rooms']:
        for sk in r.get('sockets', []):
            if sk['circuit_id'] not in circuit_ids:
                errors.append(f'{ex}: socket {sk["id"]} references orphan circuit_id {sk["circuit_id"]}')
    for c in o['circuits']:
        for rr in c['rooms_covered']:
            if rr not in room_ids:
                errors.append(f'{ex}: circuit {c["circuit_id"]} references orphan room {rr}')
print(f'  ✓ All 4 examples: cross-references intact')

# 8. Existing calc contracts updated
zsl = json.load(open('shared/calculations/electrical/zs-loop-impedance.json'))
if 'electrical/small-power' not in ' '.join(zsl['_consuming_skills']):
    errors.append('zs-loop-impedance: small-power not in _consuming_skills')
else:
    print(f'  ✓ zs-loop-impedance: small-power added to _consuming_skills')

# 9. NEW NFPA70 part7-special-locations exists
if not os.path.exists('shared/standards/electrical/NFPA70/part7-special-locations.json'):
    errors.append('NFPA70/part7-special-locations.json: missing')
else:
    print(f'  ✓ NFPA70/part7-special-locations.json: present')

if errors:
    print(f'\n❌ {len(errors)} errors:')
    for e in errors: print(f'  - {e}')
    raise SystemExit(1)
print(f'\n✅ ALL CHECKS PASS')
EOF
```

Expected: all `✓` checks pass + `✅ ALL CHECKS PASS`.

### Step 2 — Dispatch code-reviewer agent

Use the Agent tool with `subagent_type: code-reviewer`, model `opus`. Brief:

> Final code review for small-power skill v1.0 at /Users/linus/Desktop/DraftsMan SKills/draftsman-skills. Spec: docs/superpowers/specs/2026-05-19-small-power-skill-design.md (commit c5806bd). ~64 files changed across 17 task commits.
>
> Focus areas:
> 1. Engineering accuracy in 4 jurisdictional examples (ring topology in UK/KE; radial-only US/INT; Type B RCD in INT C06 matches db-layout intl-dbcomms-data)
> 2. Schema design: 3 enums (topology / special_location / rcd_posture) correctly populated; strict additionalProperties everywhere
> 3. Citation form rigor per jurisdiction (no BS 7671 in INT/US except routing notes)
> 4. INV checks 1-10 logically complete + match the spec
> 5. Reviewer D-checks 1-6 match the spec
> 6. WI3 deferral consistency (tool_call_pending + flag pair) across all 4 examples
> 7. WI2 rationale: 8 sections + chat_summary ≤500 chars across all 4 examples
> 8. Cross-reference integrity (circuits[].rooms_covered ↔ rooms[].sockets[].circuit_id)
> 9. Drafting standards consumption matches jurisdiction defaults
> 10. Pattern consistency with lighting-layout v1.3 + SLD v1.5 (file structure + manifest shape)

### Step 3 — Fix any CRITICAL or HIGH findings

If reviewer surfaces issues, fix in-place with a new commit (not amend). Re-run cross-cutting validation (Step 1) after fixes.

### Step 4 — Push all commits

```bash
cd "/Users/linus/Desktop/DraftsMan SKills/draftsman-skills"
git log --oneline c5806bd..HEAD | wc -l
git push origin main
git status
```

Expected: ~17-20 commits (one per task + possibly review fix commits); push succeeds; "Your branch is up to date with 'origin/main'."

### Step 5 — Update memory queue

Edit `/Users/linus/.claude/projects/-Users-linus-Desktop-DraftsMan-SKills-draftsman-skills/memory/sld-deferred-followups-queue.md` to mark small-power shipped + cite the commit range. Update `[[build-strategy-breadth-first]]` if needed (5-of-8 drawings skills now production).

---

## Plan Self-Review

### 1. Spec coverage

Every section of `docs/superpowers/specs/2026-05-19-small-power-skill-design.md` maps to at least one task:

- §1 Why this sprint → context in plan goal/architecture
- §2 Scope (~67 files; plan corrects to ~64 after exploration) → File structure section + 17 tasks
- §3.1 Leaf skill → Task 1 manifest declares `consumes_intents: []`
- §3.2 Hybrid IR shape → Task 2 schemas (circuits[] + rooms[])
- §3.3 Topology enum (3 values) → Task 2 schema enums + Task 5 INV-04
- §3.4 Special locations enum (6 values) → Task 2 schema + Task 5 INV-05
- §3.5 RCD posture enum (3 values) → Task 2 schema + Task 5 INV-06
- §3.6 WI3 calc tool deferral → Task 3 (zs-loop-impedance _consuming_skills update) + every example has tool_call_pending flag
- §3.7 Drafting standards consumption → Task 1 manifest declares standards[] + Tasks 7-10 examples reference per-jurisdiction defaults
- §4 The 4 jurisdictional examples → Tasks 7, 8, 9, 10
- §4.5 Cross-example consistency → captured in Task 17 cross-cutting validation
- §5 Generator + Validator + Reviewer → Tasks 4, 5, 6
- §6 Evals (7-9) → Task 15 (9 eval YAMLs)
- §7 Bookkeeping → Task 16
- §8 Sequencing → 5 phases match exactly
- §9 Acceptance criteria → Task 17 cross-cutting validation enforces them
- §10 Risks → mitigations baked into tasks (e.g., INV-04 + INV-05 + INV-06; cross-reference integrity in Task 7 Step 6)
- §11 Versioning → manifest declared v1.0.0 beta
- §12 Pattern parents → CHANGELOG + ARCHITECTURE cite them
- §13 Cross-references → captured in spec links

### 2. Placeholder scan

No "TBD", "TODO", "implement later" markers. Each task contains either full content or explicit step-by-step authoring guidance with the engineering substance per spec §4.

Tasks 7-10 (4 examples) use a hybrid approach: full content shown for UK example (Task 7) + engineering-substance summaries for KE/INT/US (Tasks 8-10) with explicit "per Task 7 template + the following deltas". This is necessary given the volume — 4 examples × 5 files × full IR content would push the plan past 5000 lines.

### 3. Type consistency

Field names verified across all tasks:

- `circuit_id` (pattern `^C[0-9]{2}$`) — used identically in schema (Task 2) + examples (Tasks 7-10) + INV checks (Task 5)
- `rooms_covered` array on circuits + reverse `circuit_id` field on sockets — bidirectional cross-reference verified by INV-02 + INV-03 (Task 5) + eval-08 cross-room ring integrity (Task 15)
- `topology` enum 3 values consistent everywhere (schema + INV-04 + eval-06 + rules)
- `special_location` enum 6 values consistent everywhere (schema + INV-05 + eval-07 + rules)
- `rcd_posture` enum 3 values consistent everywhere
- `tool_call_pending_for_zs_verification` boolean + `TOOL-CALL-PENDING:calc.zs_loop_impedance` flag — paired everywhere per INV-08
- Standards layer references consistent across manifest + examples + ARCHITECTURE

### Known plan limitations / deviations from spec

1. **File count corrected** — spec said ~67 files; actual is ~64 (3 calc contracts reused not created; 1 NFPA70 special-locations file new instead of 3). Documented in the "Reference table" at the top of the plan.

2. **Tasks 8-10 (KE/INT/US examples) reference Task 7's template** — each task lists engineering deltas (jurisdictional values, citation form, specific socket counts) but does NOT repeat the full IR schema content. The writing-plans skill rule about "repeat the code" is partially relaxed here for plan-length practicality; the engineering substance is fully specified per task even if the JSON skeleton is referenced.

3. **Generator prompt (Task 4) follows lighting-layout structure, not SLD 12-step** — the brainstorm referenced "12-step" but lighting-layout v1.3 (the pattern parent) uses a "How You Think Before Acting" section with 12-14 internal steps rather than top-level `## Step N` headings. The plan reflects what production gold-standard lighting-layout actually does.

---

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-05-19-small-power-skill-sprint.md`. Two execution options:**

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, two-stage review between tasks (spec compliance → code quality), fast iteration. Per [[feedback-no-haiku-sonnet-opus-only]]: Sonnet (mechanical) or Opus (judgment-heavy); never Haiku.

**2. Inline Execution** — Execute tasks in this session using executing-plans skill, batch execution with checkpoints.

**Which approach?**
