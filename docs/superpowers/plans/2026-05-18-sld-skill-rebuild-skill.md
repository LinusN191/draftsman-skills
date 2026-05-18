# SLD Skill Rebuild v1.3.0 + db-layout v1.2.0 — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild electrical/sld/ from legacy v1.2.0 single-prompt format to v1.3.0 full artefact pattern (matching arc-flash + cable-sizing + fault-level + earthing). Paired with db-layout v1.2.0 which gains 12 new companion examples (60 files) so every board in every SLD cascade has its own consumed db-layout intent — full WI4 multi-board cascade demonstration.

**Architecture:** SLD distribution_hierarchy is a flat list with parent_board_id pointers (root = null). Each board node carries `consumed_intent_path` pointing to its db-layout intent-out.json. meta.consumed_intents[] carries N+1 entries (one per board). Selectivity cascade verified inline (not a calc tool). SPD assessment is a rule-based jurisdiction lookup. system_metrics carries WI3 deferred-tool flag for future calc.sld_system_metrics. Legacy 1245-line generator archived as engineering reference, not deleted.

**Tech Stack:** JSON Schema draft-07 for IR + intent validation; YAML for evals, rules, constraints, validation; Markdown for prompts, reasoning, README, CHANGELOG, docs; Python 3 stdlib for cross-file validation scripts.

**Spec:** `docs/superpowers/specs/2026-05-18-sld-skill-rebuild-design.md` (456 lines, 14 sections — read this for full context)

**Pattern parents:**
- **earthing v1.3** (shipped 2026-05-18) — single-board WI4 consumption pattern; SLD generalizes to multi-board cascades
- **arc-flash-labelling** (shipped 2026-05-17) — 73-file sprint scale precedent
- **db-layout v1.1** (shipped 2026-05-18) — intent-out.json schema + per-example pattern; this sprint extends to 16 examples
- **cable-sizing + fault-level + arc-flash + earthing** — proven 12-step + INV-validator + D-reviewer + WI3 deferral pattern

**File count:** ~108 files across 28 tasks in 4 phases.

---

## Critical authoring conventions (used throughout)

### A. db-layout intent-out.json strict schema

The schema at `electrical/db-layout/schemas/db-layout-intent.schema.json` has **`additionalProperties: false`**. Only these top-level fields are allowed: `db_id`, `incoming_supply`, `circuits`, `spare_ways`. Per-circuit fields: `id`, `module_id`, `breaker_rating_a`, `breaker_curve`, `rcd_protected`, `rcd_type`, `rcd_sensitivity_ma`, `cable_csa_mm2`, `cable_csa_awg`, `cable_cores`, `voltage_class`, `downstream_load_kw`, `approximate_route_length_m`.

**Do NOT include wrapper fields** (`intent_type`, `intent_version`, `produced_by_skill_version`, `produced_at`) — those belong in the runtime envelope, not the inner payload.

Use the existing `electrical/db-layout/examples/ke-nairobi-industrial-100A-tpn/intent-out.json` as the canonical reference for the slim payload shape.

### B. db-layout IR → intent field name transformation

When extracting intent-out.json from output.json IR, apply these renames:

| IR field (output.json) | Intent field (intent-out.json) |
|---|---|
| `circuit_id` | `id` |
| `way_module_id` | `module_id` |
| `ocpd.rating_a` | `breaker_rating_a` |
| `ocpd.curve` | `breaker_curve` |
| `rcd.required` | `rcd_protected` |
| `rcd.type` | `rcd_type` |
| `rcd.sensitivity_ma` | `rcd_sensitivity_ma` |
| `cable.csa_mm2_or_awg` `"2.5mm²"` | `cable_csa_mm2: 2.5` (number) |
| `cable.csa_mm2_or_awg` `"12 AWG Cu"` | `cable_csa_awg: "12 AWG Cu"` (string) |
| `cable.cores` | `cable_cores` |
| `cable.length_m` | `approximate_route_length_m` |
| `designation` | (omitted) |

### C. SLD output.json convention

Every SLD example's `meta.consumed_intents[]` carries N+1 entries (one per board in distribution_hierarchy). Each entry:

```json
{
  "intent_type": "db-layout",
  "intent_version": "1.0.0",
  "produced_by": "electrical/db-layout/v1.2.0"
}
```

`intent_version` is the SCHEMA version (1.0.0 unchanged). `produced_by` is the producing SKILL version (1.2.0 post-sprint).

### D. Citation form per jurisdiction

| Jurisdiction | Form |
|---|---|
| GB | `"BS 7671:2018+A2 Reg X.Y.Z"` |
| EU / INT | `"IEC 60364-X-XX:YEAR Clause X.Y.Z"` |
| KE | `"KS 1700:2018 §X.Y.Z"` (NOT `"BS 7671 ... (adopted by KS 1700)"`) |
| US | `"NEC 2023 Article XXX.X"` or `"NFPA 70:2023 Article XXX.X"` |

### E. Per-example folder convention

Every example (db-layout or SLD) has 5 files:
- `input.json` — engineer-entered scenario brief
- `output.json` — full IR
- `intent-out.json` — slim intent payload (db-layout: matches strict schema; SLD: matches sld-intent.schema.json)
- `reasoning.md` — engineer narrative (50-150 lines)
- `sample-schedule.md` — printable summary table

---

## File structure

### New files (~92)

| Path pattern | Count | Purpose |
|---|---|---|
| `electrical/db-layout/examples/uk-commercial-msb-3storey/` × 5 | 5 | UK MSB-rollup |
| `electrical/db-layout/examples/uk-commercial-sdb-{gf,l1,l2}/` × 5 | 15 | UK sub-DBs |
| `electrical/db-layout/examples/ke-nairobi-gh-db/` × 5 | 5 | KE gate-house DB |
| `electrical/db-layout/examples/intl-{dbl1-lighting,dbp1-power,dbm1-mechanical,dbfa1-fire-alarm}/` × 5 | 20 | INT sub-DBs |
| `electrical/db-layout/examples/us-strip-mall-{tsp-a,tsp-b,common-area}/` × 5 | 15 | US sub-panels |
| `electrical/sld/examples/{uk-commercial-office-3storey,ke-nairobi-industrial-msb-gh,intl-commercial-msb-4subdbs,us-strip-mall-msp-tenants}/` × 5 | 20 | SLD worked examples |
| `electrical/sld/schemas/sld-ir.schema.json` | 1 | IR schema |
| `electrical/sld/schemas/sld-intent.schema.json` | 1 | Intent schema |
| `electrical/sld/prompts/validator.md` | 1 | 10 INVs |
| `electrical/sld/prompts/reviewer.md` | 1 | 6 D-checks |
| `electrical/sld/rules/{distribution-hierarchy,device-selection,spd-policy,life-safety-isolation}.yaml` | 4 | Engineering policy lookups |
| `electrical/sld/constraints/{selectivity-cascade,intake-capacity,intent-shape}.yaml` | 3 | Deterministic checks |
| `electrical/sld/validation/{ir-integrity,jurisdiction-routing,tool-deferral-shape}.yaml` | 3 | IR structural checks |
| `electrical/sld/ontology/{board-roles,distribution-types}.json` | 2 | Vocabulary |
| `electrical/sld/docs/{engineering-philosophy,known-limitations,legacy-generator-v1.2-engineering-reference}.md` | 3 | Docs + archived legacy |
| `electrical/sld/evals/eval-{01..07}-*.yaml` | 7 | 5 WI5 + 2 skill-specific |

### Modified files (~16)

| Path | What changes |
|---|---|
| `electrical/db-layout/skill.manifest.json` | Version 1.1.0 → 1.2.0; examples gain 12 entries |
| `electrical/db-layout/CHANGELOG.md` | v1.2.0 entry |
| `electrical/sld/skill.manifest.json` | Full rewrite (sparse legacy → full artefact pattern) |
| `electrical/sld/inputs.json` | Refresh per WI1 |
| `electrical/sld/README.md` | Full rewrite |
| `electrical/sld/CHANGELOG.md` | v1.3.0 entry |
| `electrical/sld/prompts/generator.md` | Move existing to `docs/legacy-generator-v1.2-engineering-reference.md`; new 12-step generator written |
| `electrical/sld/evals/evals-combined.md` | DELETE (atomized into 7 YAMLs) |
| `electrical/sld/examples/examples-combined.md` | DELETE (atomized into 4 example folders) |
| `SKILLS_STATUS.md` | sld + db-layout rows |
| `ARCHITECTURE.md` | "Cross-drawing intents" → "Worked example pattern" subsection gains SLD multi-board subsection |

---

# PHASE A — db-layout v1.2.0: 12 companion examples + bookkeeping

## Task 1 — UK commercial MSB (3-storey office) rollup example

**Files:**
- Create: `electrical/db-layout/examples/uk-commercial-msb-3storey/input.json`
- Create: `electrical/db-layout/examples/uk-commercial-msb-3storey/output.json`
- Create: `electrical/db-layout/examples/uk-commercial-msb-3storey/intent-out.json`
- Create: `electrical/db-layout/examples/uk-commercial-msb-3storey/reasoning.md`
- Create: `electrical/db-layout/examples/uk-commercial-msb-3storey/sample-schedule.md`

**Engineering scenario:** UK 3-storey commercial office, 1200m² total. TN-C-S 400V TPN supply, Ze=0.35Ω, PFC=9.8kA. Single MSB in ground-floor plant room with 400A intake. 3 feeders (F01/F02/F03) to per-floor sub-DBs (SDB-GF, SDB-L1, SDB-L2 — authored in Tasks 2-4).

- [ ] **Step 1: Create directory + input.json**

```bash
mkdir -p electrical/db-layout/examples/uk-commercial-msb-3storey
```

Write `input.json`:

```json
{
  "project_id": "uk-3storey-office-eg01",
  "board_brief": "Main switchboard (MSB-MAIN) for a 3-storey UK commercial office, 1200m² GIA. 400A intake from DNO TN-C-S supply. Three feeders to per-floor sub-DBs. Ground-floor plant room location.",
  "jurisdiction": "GB",
  "standards_stack": {
    "primary": "BS 7671:2018+A2:2022",
    "assembly_type_testing": "BS EN 61439-1:2021 Type-Tested Assembly (TTA)"
  },
  "supply": {
    "dno": "UK DNO (regional electricity board)",
    "system_type": "TN-C-S",
    "voltage": "400V/230V 3-phase 4-wire 50 Hz",
    "supply_rating_a": 400,
    "phase_arrangement": "TPN_plus_E",
    "ze_declared_ohm": 0.35,
    "pfc_declared_ka": 9.8
  },
  "board": {
    "designation": "MSB-MAIN",
    "location": "ground-floor plant room",
    "enclosure_rating": "IP4X (indoor)",
    "busbar_rating_a": 400,
    "scope": "rollup"
  },
  "feeders": [
    { "circuit_id": "F01", "designation": "Feeder to SDB-GF (ground-floor sub-DB)", "phase": "TPN", "device": "100A MCCB Type D", "cable": "35mm² SWA XLPE Cu",  "route_length_m": 15 },
    { "circuit_id": "F02", "designation": "Feeder to SDB-L1 (level-1 sub-DB)",      "phase": "TPN", "device": "100A MCCB Type D", "cable": "35mm² SWA XLPE Cu",  "route_length_m": 30 },
    { "circuit_id": "F03", "designation": "Feeder to SDB-L2 (level-2 sub-DB)",      "phase": "TPN", "device": "100A MCCB Type D", "cable": "35mm² SWA XLPE Cu",  "route_length_m": 45 }
  ]
}
```

- [ ] **Step 2: Create output.json**

Write `output.json` modelled on the structure used by `electrical/db-layout/examples/intl-commercial-tpn-msb/output.json` (rollup-scope MSB). Key fields:

```json
{
  "$schema": "../../schemas/db-layout-ir.schema.json",
  "drawing_type": "db_layout",
  "version": "1.2.0",
  "meta": {
    "project_id": "uk-3storey-office-eg01",
    "skill_version": "db-layout/1.2.0",
    "produced_at": "2026-05-18T10:00:00Z"
  },
  "jurisdiction": "GB",
  "board": {
    "db_id": "MSB-MAIN",
    "designation": "MSB-MAIN — Main switchboard, UK 3-storey office",
    "location": "ground-floor plant room",
    "enclosure_rating": "IP4X",
    "manufacturer_class": "BS EN 61439-1 Type-Tested Assembly (TTA)",
    "scope": "rollup"
  },
  "incoming_supply": {
    "voltage_v": 400,
    "phase_arrangement": "TPN_plus_E",
    "supply_rating_a": 400,
    "fed_from": "UK DNO TN-C-S 400V TPN",
    "supply_class": "non_essential",
    "declared_pfc_ka": 9.8
  },
  "main_switch": {
    "type": "MCCB",
    "rating_a": 400,
    "breaking_capacity_ka": 36,
    "fault_level_a_min": 9800
  },
  "circuits": [
    { "circuit_id": "F01", "way_module_id": "W1-W3",  "designation": "Feeder to SDB-GF",       "voltage_class": "LV_power", "downstream_load_kw": 30,   "ocpd": { "rating_a": 100, "curve": "D", "type": "MCCB", "breaking_capacity_ka": 36 }, "rcd": { "required": false }, "cable": { "csa_mm2_or_awg": "35mm²", "cores": 5, "length_m": 15 } },
    { "circuit_id": "F02", "way_module_id": "W4-W6",  "designation": "Feeder to SDB-L1",       "voltage_class": "LV_power", "downstream_load_kw": 28,   "ocpd": { "rating_a": 100, "curve": "D", "type": "MCCB", "breaking_capacity_ka": 36 }, "rcd": { "required": false }, "cable": { "csa_mm2_or_awg": "35mm²", "cores": 5, "length_m": 30 } },
    { "circuit_id": "F03", "way_module_id": "W7-W9",  "designation": "Feeder to SDB-L2",       "voltage_class": "LV_power", "downstream_load_kw": 28,   "ocpd": { "rating_a": 100, "curve": "D", "type": "MCCB", "breaking_capacity_ka": 36 }, "rcd": { "required": false }, "cable": { "csa_mm2_or_awg": "35mm²", "cores": 5, "length_m": 45 } }
  ],
  "spare_ways": 3,
  "selectivity_results": [
    { "upstream": "main_switch_400A", "downstream": "F01_F03", "verdict": "pass", "_note": "400A main MCCB selective against 100A feeder MCCBs by 4:1 ratio + breaking capacity matched (36kA)" }
  ],
  "compliance_summary": {
    "compliant": true,
    "non_compliance_flags": [],
    "assumptions": [
      "BS EN 61439-1 Type-Tested Assembly used for the MSB.",
      "DNO declared PFC of 9.8kA at intake; MCCBs selected with 36kA Icu (BS EN 60947-2).",
      "Final-circuit RCDs applied at sub-DBs (SDB-GF/L1/L2), not at MSB feeder level — preserves selectivity."
    ]
  },
  "drawing_notes": [
    "MSB-MAIN located in ground-floor plant room.",
    "Three feeders to per-floor sub-DBs (SDB-GF, SDB-L1, SDB-L2).",
    "Spare ways: 3 (W10-W12 reserved for future expansion)."
  ]
}
```

- [ ] **Step 3: Create intent-out.json (strict schema)**

```json
{
  "db_id": "MSB-MAIN",
  "incoming_supply": {
    "voltage_v": 400,
    "phase_arrangement": "TPN_plus_E",
    "supply_rating_a": 400,
    "fed_from": "UK DNO TN-C-S 400V TPN",
    "supply_class": "non_essential"
  },
  "circuits": [
    { "id": "F01", "module_id": "W1-W3", "breaker_rating_a": 100, "breaker_curve": "D", "rcd_protected": false, "cable_csa_mm2": 35, "cable_cores": 5, "voltage_class": "LV_power", "downstream_load_kw": 30, "approximate_route_length_m": 15 },
    { "id": "F02", "module_id": "W4-W6", "breaker_rating_a": 100, "breaker_curve": "D", "rcd_protected": false, "cable_csa_mm2": 35, "cable_cores": 5, "voltage_class": "LV_power", "downstream_load_kw": 28, "approximate_route_length_m": 30 },
    { "id": "F03", "module_id": "W7-W9", "breaker_rating_a": 100, "breaker_curve": "D", "rcd_protected": false, "cable_csa_mm2": 35, "cable_cores": 5, "voltage_class": "LV_power", "downstream_load_kw": 28, "approximate_route_length_m": 45 }
  ],
  "spare_ways": 3
}
```

- [ ] **Step 4: Create reasoning.md (~50 lines)**

```markdown
# Reasoning — UK 3-storey Office MSB-MAIN

## Site context

3-storey UK commercial office, 1200m² GIA total (400m² per floor). DNO TN-C-S 400V TPN supply with declared Ze=0.35Ω + PFC=9.8kA. Ground-floor plant room location for the main switchboard.

## Board sizing — 400A intake

Peak design load per floor: ~30 kVA (12kW lighting + 10kW sockets + 5kW IT + 3kW HVAC FCU). Total 3-floor load: 86 kVA at PF 0.85 = 73 kW.

Design current per phase: 86,000 / (√3 × 400 × 0.85) = ~146A.

Applying diversity factor 0.8 (commercial typical for spec offices per BS 7671 Appendix 1 + BCO guidance): ~117A. With 25% growth margin: ~146A peak.

400A TPN intake gives ~63% headroom — generous for spec office where tenant fit-out can dramatically change loads. Standard practice for commercial multi-tenant buildings.

## MCCB selection for feeders (Type D, 100A each)

Each sub-DB is sized at 100A. The feeder breakers are 100A MCCBs Type D:
- Type D curve (Ia = 20×In) handles potential inrush from downstream LED lighting transformers + UPS-fed IT loads
- 100A rating matches downstream sub-DB intake rating
- 36kA Icu breaking capacity matches DNO declared PFC + intake fault path

## Selectivity verification

Upstream 400A MCCB selectively trips against 100A feeder MCCBs:
- Current selectivity ratio: 4:1 (BS EN 60947-2 typical achieves selectivity up to 5:1)
- Time selectivity: short-time delay (STD) at 400A MCCB further enhances selectivity
- Breaking capacity: 36kA on both upstream + downstream (matched)

## Downstream consumer

This board's intent-out.json is consumed by:
- `electrical/sld/examples/uk-commercial-office-3storey/` (SLD generates the system-wide single-line diagram)
- Sub-DBs SDB-GF, SDB-L1, SDB-L2 are authored as separate db-layout examples (Tasks 2-4)
- (Future) `electrical/cable-sizing/` for feeder cable sizing verification
- (Future) `electrical/fault-level/` for cascade fault current verification

## See also

- electrical/db-layout/examples/uk-commercial-sdb-gf/ (downstream — ground floor sub-DB)
- electrical/db-layout/examples/uk-commercial-sdb-l1/ (downstream — level 1 sub-DB)
- electrical/db-layout/examples/uk-commercial-sdb-l2/ (downstream — level 2 sub-DB)
```

- [ ] **Step 5: Create sample-schedule.md (~20 lines)**

```markdown
# DB Schedule — MSB-MAIN, UK 3-storey Office

**Project:** uk-3storey-office-eg01
**Board:** MSB-MAIN, IP4X enclosure, 400A TPN intake from UK DNO
**Generated:** 2026-05-18
**Jurisdiction:** GB (BS 7671:2018+A2)

---

| Way | Circuit | Designation | Phase | Device | In (A) | Cable | Length (m) | RCD |
|---|---|---|---|---|---|---|---|---|
| W1-W3   | F01 | Feeder to SDB-GF | TPN | MCCB Type D | 100 | 35mm² SWA | 15 | n/a |
| W4-W6   | F02 | Feeder to SDB-L1 | TPN | MCCB Type D | 100 | 35mm² SWA | 30 | n/a |
| W7-W9   | F03 | Feeder to SDB-L2 | TPN | MCCB Type D | 100 | 35mm² SWA | 45 | n/a |
| W10-W12 | —   | Spare ways       |     |             |     |           |    |     |

---

## Notes

- Total design demand: 86 kVA / 73 kW / ~146A per phase peak with diversity
- 400A TPN intake provides ~63% headroom for spec-office tenant fit-out variation
- Selectivity verified: 400A main MCCB selective against 100A feeder MCCBs (4:1 ratio + STD)
- Final-circuit RCDs deferred to downstream sub-DBs (preserves MSB-level selectivity)
- Downstream consumers: SDB-GF, SDB-L1, SDB-L2 (each their own db-layout example)
```

- [ ] **Step 6: Validate JSON + schema**

```bash
python3 -c "import json; [json.load(open(f'electrical/db-layout/examples/uk-commercial-msb-3storey/{f}.json')) for f in ['input', 'output', 'intent-out']]; print('JSON OK')"
python3 -c "import json, jsonschema; s=json.load(open('electrical/db-layout/schemas/db-layout-intent.schema.json')); d=json.load(open('electrical/db-layout/examples/uk-commercial-msb-3storey/intent-out.json')); jsonschema.validate(d, s); print('intent schema OK')"
```

Expected: `JSON OK` + `intent schema OK`.

- [ ] **Step 7: Commit**

```bash
git add electrical/db-layout/examples/uk-commercial-msb-3storey/
git commit -m "$(cat <<'EOF'
feat(db-layout): NEW UK commercial MSB-MAIN (3-storey office)

Rollup-scope MSB example for the UK SLD scenario. TN-C-S 400V TPN
supply with declared Ze=0.35Ω + PFC=9.8kA. 400A intake; 3 feeders
(F01/F02/F03) to per-floor sub-DBs SDB-GF/L1/L2.

Upstream producer for electrical/sld/examples/uk-commercial-office-
3storey/. Sub-DBs authored as separate db-layout examples (Tasks 2-4).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 2 — UK SDB-GF (ground floor sub-DB)

**Files:** `electrical/db-layout/examples/uk-commercial-sdb-gf/{input,output,intent-out}.json + reasoning.md + sample-schedule.md`

**Scenario:** 100A TPN sub-DB on ground floor. ~12 final circuits: lighting (LED panels + emergency), sockets (general + dedicated), HVAC FCUs, IT/data outlets. Fed from MSB-MAIN F01.

- [ ] **Step 1: Create directory + author 5 files following the Task 1 pattern**

```bash
mkdir -p electrical/db-layout/examples/uk-commercial-sdb-gf
```

Use the same 5-file structure as Task 1. The `output.json` is single-board scope (not rollup); `db_id: "SDB-GF"`. 12 final circuits. Inputs include `fed_from: "MSB-MAIN F01"` reference. Detailed circuits:

| circuit_id | designation | rating | curve | csa_mm2 | length | rcd |
|---|---|---|---|---|---|---|
| C01 | Lighting GF — open office LED panels | 10A | B | 1.5 | 25 | 30mA Type A |
| C02 | Lighting GF — meeting rooms LED panels | 6A | B | 1.5 | 18 | 30mA Type A |
| C03 | Emergency lighting GF | 6A | B | 1.5 | 20 | n/a (dedicated supply) |
| C04 | Sockets GF — open office RFC | 32A | B | 2.5 | 35 (ring) | 30mA Type A |
| C05 | Sockets GF — meeting rooms RFC | 32A | B | 2.5 | 28 (ring) | 30mA Type A |
| C06 | Sockets GF — reception RFC | 32A | B | 2.5 | 20 (ring) | 30mA Type A |
| C07 | Sockets GF — kitchen radial | 20A | B | 2.5 | 12 | 30mA Type A |
| C08 | Dedicated socket — printer/copier | 16A | B | 2.5 | 18 | 30mA Type A |
| C09 | HVAC FCU bank GF | 32A | C | 2.5 | 22 | n/a (motor circuit) |
| C10 | Cleaner sockets — corridors | 20A | B | 2.5 | 30 | 30mA Type A |
| C11 | IT/data outlet ring — desks | 32A | B | 2.5 | 32 (ring) | 30mA Type A |
| C12 | Audio-visual radial — meeting rooms | 20A | B | 2.5 | 24 | 30mA Type A |

Apply transformation rules from "Critical authoring conventions" §B when extracting `intent-out.json` from `output.json`. The intent payload follows the strict schema.

Reasoning.md notes:
- Universal 30mA RCD on socket circuits per BS 7671:2018+A2 Reg 411.3.3
- Emergency lighting circuit C03 dedicated supply with no RCD per BS 7671 §560
- Type B MCBs on lighting + sockets; Type C on HVAC FCU motors

- [ ] **Step 2: Validate + commit**

Same validation script as Task 1 (substituting paths). Commit message:

```
feat(db-layout): NEW UK SDB-GF (ground floor sub-DB)

Single-board sub-DB example fed from MSB-MAIN F01. 12 final circuits
(lighting + sockets + HVAC + IT). All socket circuits 30mA RCD per
BS 7671:2018+A2 §411.3.3. Emergency lighting C03 dedicated supply
per §560.

Upstream producer for SLD UK 3-storey office cascade.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

---

## Task 3 — UK SDB-L1 (level 1 sub-DB)

**Files:** `electrical/db-layout/examples/uk-commercial-sdb-l1/{input,output,intent-out}.json + reasoning.md + sample-schedule.md`

**Scenario:** Same shape as SDB-GF but for level 1. 100A TPN. ~12 final circuits with slight load variation (no reception → no kitchen). Fed from MSB-MAIN F02 (30m route).

- [ ] **Step 1: Author 5 files following Task 2 pattern**

Same circuit list as SDB-GF but adapted for L1:
- C01-C02 lighting (open office + breakout)
- C03 emergency lighting
- C04-C06 socket ring mains (open office, meeting rooms, breakout)
- C07 socket radial — printer corner
- C08-C09 dedicated outlets
- C10 HVAC FCU bank L1
- C11 IT/data outlets
- C12 AV outlets

Apply transformation rules + validate + commit with appropriate message ("L1 sub-DB").

---

## Task 4 — UK SDB-L2 (level 2 sub-DB)

**Files:** `electrical/db-layout/examples/uk-commercial-sdb-l2/{input,output,intent-out}.json + reasoning.md + sample-schedule.md`

**Scenario:** Same shape as L1 but for level 2. 100A TPN. Fed from MSB-MAIN F03 (45m route — longest run; Zs verification at L2 socket circuits will be tightest in the SLD cascade analysis).

- [ ] **Step 1: Author 5 files following Task 3 pattern**

Validate + commit with appropriate message ("L2 sub-DB; 45m feeder route").

---

## Task 5 — KE Nairobi gate-house sub-DB (GH-DB)

**Files:** `electrical/db-layout/examples/ke-nairobi-gh-db/{input,output,intent-out}.json + reasoning.md + sample-schedule.md`

**Scenario:** Small gate-house sub-DB fed by MSP-100 C08 (existing KE example's 40A submain to gate house, 60m route). KS 1700 jurisdiction. 3-4 final circuits: lighting + sockets + comms outlet.

- [ ] **Step 1: Create directory + author 5 files**

```bash
mkdir -p electrical/db-layout/examples/ke-nairobi-gh-db
```

Input scenario:
- KE jurisdiction
- Fed from KPLC TN-S supply (via MSP-100 C08)
- 60m submain from main switchroom
- Gate-house sub-DB: 4 final circuits
- KS 1700:2018 §411.3.3 universal socket-RCD applies

Circuits (4 total):
| circuit_id | designation | rating | curve | csa | length | rcd |
|---|---|---|---|---|---|---|
| C01 | Gate-house lighting (external floodlights + internal) | 10A | B | 1.5mm² | 8m | n/a (lighting) |
| C02 | Gate-house sockets (general) | 16A | B | 2.5mm² | 6m | 30mA Type A (KS §411.3.3) |
| C03 | Comms outlet (CCTV camera supply + intercom) | 6A | B | 1.5mm² | 5m | 30mA Type A |
| C04 | Spare way reserved | — | — | — | — | — |

Citations in `reasoning.md` use form `"KS 1700:2018 §411.3.3"` (NOT BS 7671 annotation form). KS Annex E adoption of BS Table 41.2 mentioned briefly.

- [ ] **Step 2: Validate + commit**

Commit message:
```
feat(db-layout): NEW KE gate-house DB (downstream of MSP-100 C08)

Small gate-house sub-DB on KPLC TN-S supply, fed via 60m submain from
MSP-100 C08 (existing KE example). 4 ways total: 3 final circuits +
1 spare. KS 1700:2018 §411.3.3 universal socket-RCD applied to C02
+ C03. Citations in direct KS 1700 form (no annotation).

Upstream producer for the KE Nairobi SLD example.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

---

## Task 6 — INT DB-L1 (lighting sub-DB, downstream of MSB-MAIN F01)

**Files:** `electrical/db-layout/examples/intl-dbl1-lighting/{input,output,intent-out}.json + reasoning.md + sample-schedule.md`

**Scenario:** Generic IEC commercial lighting sub-DB. Fed from existing `intl-commercial-tpn-msb/` MSB-MAIN F01 (250A MCCB Type D, 150mm² cable). 250A intake at DB-L1. 8-10 final lighting circuits.

- [ ] **Step 1: Read upstream INT MSB to align**

```bash
cat electrical/db-layout/examples/intl-commercial-tpn-msb/intent-out.json | python3 -c "import json, sys; d=json.load(sys.stdin); print('F01:', [c for c in d['circuits'] if c['id']=='F01'])"
```

Note F01: 250A Type D, 150mm² cable, 35m route, LV_power.

- [ ] **Step 2: Author 5 files for DB-L1**

Input scenario:
- INT jurisdiction (IEC 60364, generic — no Kenya cues)
- Fed from MSB-MAIN F01 (existing INT MSB example)
- DB-L1 location: ground-floor lighting riser
- 250A TPN intake
- 8 lighting final circuits (commercial building lighting: LED panels by zone)

Circuits:
| id | designation | rating | curve | csa_mm2 | length | rcd |
|---|---|---|---|---|---|---|
| L01 | Lighting Zone 1 (open office GF) | 16A | C | 2.5 | 40m | 30mA Type A |
| L02 | Lighting Zone 2 (open office L1) | 16A | C | 2.5 | 60m | 30mA Type A |
| L03 | Lighting Zone 3 (open office L2) | 16A | C | 2.5 | 80m | 30mA Type A |
| L04 | Lighting — meeting rooms common | 10A | B | 1.5 | 45m | 30mA Type A |
| L05 | External lighting (parking + façade) | 20A | C | 4 | 90m | 30mA Type A |
| L06 | Emergency lighting (battery-backed) | 10A | B | 1.5 | 55m | n/a |
| L07 | Decorative lighting (lobby + meeting rooms) | 10A | B | 1.5 | 35m | 30mA Type A |
| L08 | Spare | — | — | — | — | — |

Apply transformation rules. Citations: `"IEC 60364-X-XX Clause X.Y.Z"` form.

- [ ] **Step 3: Validate + commit**

```
feat(db-layout): NEW INT DB-L1 (commercial lighting sub-DB, fed via MSB-MAIN F01)

Lighting sub-DB downstream of existing intl-commercial-tpn-msb F01.
250A TPN intake. 8 final circuits covering open-office lighting,
common-area lighting, external lighting, emergency lighting. IEC
60364 generic citation form.

Upstream producer for the INT commercial SLD example (DB-L1 board).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

---

## Task 7 — INT DB-P1 (small-power sub-DB, downstream of MSB-MAIN F02)

**Files:** `electrical/db-layout/examples/intl-dbp1-power/{input,output,intent-out}.json + reasoning.md + sample-schedule.md`

**Scenario:** Generic IEC commercial small-power sub-DB. Fed from MSB-MAIN F02 (400A MCCB Type D, 240mm² cable). 400A intake at DB-P1. ~12 final socket + small-power circuits.

- [ ] **Step 1: Author 5 files (pattern follows Task 6)**

Circuits cover: socket ring mains (open offices per zone), dedicated outlets (kitchen/copier/AV), IT/data ring mains. ~12 circuits at 32A Type B + a few 20A radials.

Citations: IEC 60364 form. Apply transformation rules. Validate. Commit.

---

## Task 8 — INT DB-M1 (mechanical sub-DB, downstream of MSB-MAIN F03)

**Files:** `electrical/db-layout/examples/intl-dbm1-mechanical/{input,output,intent-out}.json + reasoning.md + sample-schedule.md`

**Scenario:** Generic IEC commercial mechanical/HVAC sub-DB. Fed from MSB-MAIN F03 (250A MCCB Type D, 150mm² cable). 250A intake at DB-M1. 6-8 mechanical circuits.

- [ ] **Step 1: Author 5 files**

Circuits cover: AHU motors (Type D MCBs for inrush), chilled-water pumps, BMS-controlled FCUs, kitchen extract fan, condensate pump. Mix of Type C + Type D curves.

Validate + commit.

---

## Task 9 — INT DB-FA1 (fire alarm panel, downstream of MSB-MAIN F04)

**Files:** `electrical/db-layout/examples/intl-dbfa1-fire-alarm/{input,output,intent-out}.json + reasoning.md + sample-schedule.md`

**Scenario:** Fire alarm panel. Fed from MSB-MAIN F04 (63A MCB Type C). NO upstream RCD (life-safety exemption per IEC 60364-5-56 §560). 63A intake; small circuit count (panel power + zone loops). `voltage_class: "fire_alarm"` for all circuits.

- [ ] **Step 1: Author 5 files**

Key engineering point — `board.role: "fire_alarm_panel"`; all circuits use `voltage_class: "fire_alarm"`. No RCDs (life-safety exemption). Reasoning.md emphasises §560 routing.

Validate + commit.

---

## Task 10 — US strip mall tenant sub-panel A (TSP-A, Suite 100 retail)

**Files:** `electrical/db-layout/examples/us-strip-mall-tsp-a/{input,output,intent-out}.json + reasoning.md + sample-schedule.md`

**Scenario:** Tenant sub-panel for Suite 100 (retail occupancy). Fed from MSP-A (existing US strip mall example). 100A 208Y/120V intake at TSP-A. NEC convention throughout (AWG cables). 8-10 final circuits.

- [ ] **Step 1: Author 5 files**

Circuits cover: retail floor lighting (LED track + emergency), sales counter outlets, HVAC RTU control, dedicated freezer/cooler (motors), point-of-sale dedicated. NEC 250.122 EGC sizing references.

Apply transformation rules — US cables use `cable_csa_awg: "12 AWG Cu"` etc. Citations: `"NEC 2023 Article XXX.X"` form.

Validate + commit.

---

## Task 11 — US strip mall tenant sub-panel B (TSP-B, Suite 200 retail)

**Files:** `electrical/db-layout/examples/us-strip-mall-tsp-b/{input,output,intent-out}.json + reasoning.md + sample-schedule.md`

**Scenario:** Same shape as TSP-A but for Suite 200 (different retail tenant — slight load variation). 100A 208Y/120V intake.

- [ ] **Step 1: Author 5 files (pattern follows Task 10)**

Slightly different load mix (e.g., no freezer; food-service tenant with display refrigeration instead). Same NEC conventions.

Validate + commit.

---

## Task 12 — US strip mall common-area panel (CA-P)

**Files:** `electrical/db-layout/examples/us-strip-mall-common-area/{input,output,intent-out}.json + reasoning.md + sample-schedule.md`

**Scenario:** Common-area + exterior lighting panel. Fed from MSP-A. 60A 208Y/120V intake (smaller than tenants). 5-6 circuits: parking lot lighting, façade lighting, common-area HVAC, fire pump controller (life-safety).

- [ ] **Step 1: Author 5 files**

NEC convention throughout. Fire pump controller circuit per NEC Article 695 — appropriate cable + dedicated supply considerations.

Validate + commit.

---

## Task 13 — db-layout v1.2.0 bookkeeping (manifest + CHANGELOG + SKILLS_STATUS)

**Files:**
- Modify: `electrical/db-layout/skill.manifest.json`
- Modify: `electrical/db-layout/CHANGELOG.md`
- Modify: `SKILLS_STATUS.md` (db-layout row only — SLD row update in later task)

- [ ] **Step 1: Bump db-layout manifest**

Use Edit on `electrical/db-layout/skill.manifest.json`:
- Version `"1.1.0"` → `"1.2.0"`
- In `examples` array, append 12 new entries:

```
"electrical/db-layout/examples/uk-commercial-msb-3storey/",
"electrical/db-layout/examples/uk-commercial-sdb-gf/",
"electrical/db-layout/examples/uk-commercial-sdb-l1/",
"electrical/db-layout/examples/uk-commercial-sdb-l2/",
"electrical/db-layout/examples/ke-nairobi-gh-db/",
"electrical/db-layout/examples/intl-dbl1-lighting/",
"electrical/db-layout/examples/intl-dbp1-power/",
"electrical/db-layout/examples/intl-dbm1-mechanical/",
"electrical/db-layout/examples/intl-dbfa1-fire-alarm/",
"electrical/db-layout/examples/us-strip-mall-tsp-a/",
"electrical/db-layout/examples/us-strip-mall-tsp-b/",
"electrical/db-layout/examples/us-strip-mall-common-area/"
```

Total examples after: 4 (existing) + 12 (new) = 16.

- [ ] **Step 2: db-layout CHANGELOG v1.2.0 entry**

Use Edit on `electrical/db-layout/CHANGELOG.md`. Insert IMMEDIATELY BEFORE the existing `## [1.1.0]` entry:

```markdown
## [1.2.0] - 2026-05-18

### Added
- **12 new cascade-supporting examples** to enable full WI4 multi-board intent consumption in SLD v1.3.0:
  - UK: 4 new (MSB-rollup + 3 sub-DBs SDB-GF/L1/L2)
  - KE: 1 new (gate-house DB downstream of MSP-100 C08)
  - INT: 4 new (DB-L1 lighting + DB-P1 power + DB-M1 mechanical + DB-FA1 fire alarm; all downstream of existing intl-commercial-tpn-msb F01-F04)
  - US: 3 new (TSP-A + TSP-B tenant sub-panels + CA-P common area; all downstream of existing us-strip-mall-panelboard)

### Notes
- All new examples follow the 5-file pattern (input + output + intent-out + reasoning + sample-schedule) established in v1.1.
- intent-out.json strict schema validation enforced (additionalProperties: false; no wrapper fields).
- Downstream consumer: SLD v1.3.0 (paired sprint).

```

- [ ] **Step 3: SKILLS_STATUS db-layout row**

Use Edit on `SKILLS_STATUS.md`. Find the existing db-layout row + replace with:

```
| db-layout | `electrical/db-layout` | **beta** | BS 7671:2018, IEC 60364, IEC 61439, NFPA 70 (NEC 2023), KS 1700:2018, IEC 60617 | 8/3 ✓ | v1.2.0 — 12 new cascade-supporting examples for SLD v1.3.0 (paired sprint). 16 worked examples total covering UK/KE/INT/US jurisdictions at MSB-rollup + single-board sub-DB scopes. |
```

- [ ] **Step 4: Validate**

```bash
python3 -c "import json; d=json.load(open('electrical/db-layout/skill.manifest.json')); assert d['version']=='1.2.0'; assert len(d['examples'])==16; print('OK 16 examples')"
grep "^| db-layout" SKILLS_STATUS.md | head -1
```

Expected: `OK 16 examples`; row contains "v1.2.0".

- [ ] **Step 5: Commit**

```bash
git add electrical/db-layout/skill.manifest.json electrical/db-layout/CHANGELOG.md SKILLS_STATUS.md
git commit -m "$(cat <<'EOF'
chore(db-layout): v1.1.0 → v1.2.0 — manifest + CHANGELOG + SKILLS_STATUS

Version bump. 12 new examples registered in manifest examples array
(now 16 total). CHANGELOG v1.2.0 entry documents the cascade-supporting
examples per jurisdiction. SKILLS_STATUS row bumped to v1.2.0.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

# PHASE B — SLD infrastructure rebuild (Tasks 14-20)

## Task 14 — Archive legacy generator + initialize SLD docs structure

**Files:**
- Create: `electrical/sld/docs/legacy-generator-v1.2-engineering-reference.md` (moved from prompts/generator.md)
- Create: `electrical/sld/docs/engineering-philosophy.md`
- Create: `electrical/sld/docs/known-limitations.md`
- Delete: `electrical/sld/evals/evals-combined.md`
- Delete: `electrical/sld/examples/examples-combined.md`

- [ ] **Step 1: Archive the legacy generator**

```bash
mkdir -p electrical/sld/docs
git mv electrical/sld/prompts/generator.md electrical/sld/docs/legacy-generator-v1.2-engineering-reference.md
```

Then edit the archived file's H1 to add the archive note. Use Edit to find the existing first line (likely `# generator — sld skill` or similar) and replace with:

```markdown
# Legacy SLD Generator v1.2 — Engineering Reference (Archived)

> **Status:** ARCHIVED. This is the original single-file generator from SLD v1.2.0 (1245 lines). It has been replaced by the 12-step generator at `electrical/sld/prompts/generator.md` (v1.3.0) and the per-prompt artefact pattern.
>
> **Why kept:** Engineering substance below is good (deep coverage of distribution hierarchy, design currents, diversity, breaker sizing, cable selection, breaking capacity, Zs, selectivity, RCD, life safety, switchgear, gen/UPS/ATS, SPD per BS 7671 §443, earthing/bonding/metering). Useful as engineering reference + when authoring new SLD examples.
>
> **What's different from v1.3.0:**
> - v1.3.0 generator follows 12-step pattern (matches other skills); legacy is 15-step + idiosyncratic
> - v1.3.0 consumes db-layout intents per board (WI4); legacy required all data inline in inputs
> - v1.3.0 emits a rationale block (WI2); legacy didn't
> - v1.3.0 uses WI3 tool-call deferral for system_metrics; legacy computed everything inline
> - v1.3.0 has separate validator + reviewer prompts; legacy bundled everything into one generator

---

[ORIGINAL LEGACY CONTENT BELOW]

```

- [ ] **Step 2: Create engineering-philosophy.md**

```markdown
# SLD Engineering Philosophy — v1.3.0

## What SLD is

A logical-topology single-line diagram skill for LV distribution systems. Captures the cascade from utility supply through MSB to sub-DBs. Does NOT yet include drawing positions (Stage 2; deferred to v1.5.0+).

## What SLD is NOT

- Not a final-circuit schedule (db-layout owns per-board circuit detail)
- Not a renderer (no SVG/DXF/LISP output — runtime concern)
- Not a fault-current calculator (fault-level skill owns deterministic PSCC + selectivity calcs)
- Not an earthing system designer (earthing skill owns CPC + Zs + RCD)
- Not a panel-builder (db-layout owns single-board internals)

## How SLD relates to other skills

- **Consumes** `db-layout` intents (one per board in cascade) — WI4 pattern from earthing v1.3
- **Will consume** in future versions: `earthing` (Ze + supply_bond_type confirmation, SPD policy input), `fault-level` (deterministic PSCC + selectivity verification refinement) — v1.4.0+ work
- **Produces** `sld` intent for downstream skills: riser (vertical board distribution + cable routes), cable-containment (whole-installation cable schedules), maintenance docs (system overview), panel-schedule rollup

## Design principles

1. **System view, not board view.** SLD is the project-level summary that ties multiple db-layout boards into one cascade.
2. **Cascade selectivity is verified, not calculated.** Use breaker manufacturer typical curves + IEC 60898 conventions for the verdict. v1.3 doesn't add a calc tool; future v2 may.
3. **SPD assessment is rule-driven.** Per BS 7671 §443 / IEC 60364-4-44 / NEC 285 / KS 1700 §443. Lookup not math.
4. **Life-safety circuits are flagged + isolated.** Fire alarm + emergency lighting + UPS-fed essentials. Dedicated supplies; no upstream RCD per jurisdiction-specific clauses.
5. **System metrics are LLM-estimated in v1.3.** Imax_total + peak_pfc carry WI3 deferred flag until calc.sld_system_metrics ships.

## Versioning roadmap

- **v1.3.0** — this rebuild. Single-skill consumption (db-layout only). Logical topology only.
- **v1.4.0** — add earthing + fault-level intent consumption. Per-board provenance grows from N+1 → N+3 entries.
- **v1.5.0** — add drawing position layout (Stage 2). Schema gains `drawing_layout` field. Pairs with runtime renderer.
- **v2.0.0** — schema-breaking changes (e.g., consuming calc.sld_system_metrics outputs replaces the inline LLM estimates).
```

- [ ] **Step 3: Create known-limitations.md**

```markdown
# SLD v1.3.0 — Known Limitations

## Out of scope (deferred to future versions)

| Limitation | Future version |
|---|---|
| Drawing positions (x/y coordinates per board) — Stage 1 is logical topology only | v1.5.0 (Stage 2) |
| Consuming earthing intent (system_type confirmation, supply_bond_type, SPD policy input) | v1.4.0 |
| Consuming fault-level intent (deterministic PSCC + cascade selectivity refinement) | v1.4.0 |
| calc.sld_system_metrics tool (deterministic Imax + peak_pfc + SPD verdict refinement) | v2.0.0 |
| Generator/UPS/ATS topology (currently flagged in compliance_summary.assumptions, not modelled in IR) | v1.6.0 |
| Multi-supply scenarios (two intakes + ATS switching between them) | v1.6.0+ |
| Renderer output (SVG/DXF/LISP) | runtime concern |

## Current limitations (by design)

- **System metrics are LLM-estimated** (WI3 tool deferral flag set). Imax_total + peak_pfc accuracy is ±15-25% vs deterministic calculation.
- **Cascade selectivity verdict is engineering judgement** based on manufacturer typical curves + IEC 60898 conventions. For tight-tolerance designs, engineer should consult manufacturer selectivity tables directly.
- **SPD assessment is rule-based** (not a calc). Location-type + supply-type + life-safety-presence → verdict via jurisdiction-specific lookup. Doesn't model lightning probability or service-entry distances.
- **4 worked examples cover 4 jurisdictions** (UK + KE + INT + US). Other jurisdictions (NF C 15-100 / DIN VDE 0100 / etc.) deferred to v1.4+.

## Verification status

| Component | Status | Note |
|---|---|---|
| IR schema | production | Draft-07 JSON Schema; validates all 4 example outputs |
| Intent schema | production | Draft-07 JSON Schema; validates all 4 example intent-outs |
| Generator prompt | production | 12 steps; mirrors arc-flash / cable-sizing / fault-level / earthing pattern |
| Validator prompt | production | 10 INV checks |
| Reviewer prompt | production | 6 D-check pattern |
| Rules + constraints + validation YAMLs | production | 10 YAML files, 17+ deterministic checks total |
| 4 worked examples | production | UK + KE + INT + US, each consuming N+1 db-layout intents |
| 7 evals | production | 5 WI5 categories + 2 skill-specific |
| `calc.sld_system_metrics` runtime tool | not_shipped | Contract deferred; LLM-inline computation in v1.3 |
```

- [ ] **Step 4: Delete legacy combined files**

```bash
git rm electrical/sld/evals/evals-combined.md
git rm electrical/sld/examples/examples-combined.md
```

- [ ] **Step 5: Commit**

```bash
git add electrical/sld/docs/
git commit -m "$(cat <<'EOF'
docs(sld): archive legacy 1245-line generator + init docs/

Moves electrical/sld/prompts/generator.md (legacy v1.2 monolithic
prompt) to electrical/sld/docs/legacy-generator-v1.2-engineering-
reference.md with archive note documenting the v1.3 differences.

Creates docs/engineering-philosophy.md (design principles + skill
relationships + versioning roadmap) and docs/known-limitations.md
(out-of-scope items + verification status + 4-jurisdiction coverage).

Deletes legacy evals-combined.md + examples-combined.md (their
content gets atomized into per-eval YAMLs + per-example folders
in subsequent tasks).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 15 — SLD IR + intent schemas

**Files:**
- Create: `electrical/sld/schemas/sld-ir.schema.json`
- Create: `electrical/sld/schemas/sld-intent.schema.json`

- [ ] **Step 1: Create directory + IR schema**

```bash
mkdir -p electrical/sld/schemas
```

Write `sld-ir.schema.json` per spec §4. Full JSON Schema Draft-07 with required top-level fields: drawing_type (const "single_line_diagram"), version, meta (with consumed_intents array), jurisdiction (enum GB/EU/INT/KE/US), supply_origin, distribution_hierarchy (array of board nodes), selectivity_cascade, system_metrics, compliance_summary, drawn_as_symbols, flags, tool_call_pending_for_system_metrics, rationale ($ref to shared rationale schema).

Per-board node required fields: board_id, board_role (enum from ontology), consumed_intent_path. Optional: parent_board_id, fed_via_circuit_id, location, enclosure_rating.

Per-selectivity-cascade-entry required fields: parent_board_id, parent_circuit_id, child_board_id, verdict (enum), verification_method.

Per-system_metrics required fields: imax_total_a, peak_pfc_ka, spd_assessment, life_safety_isolation, tool_call_pending_for_system_metrics.

`spd_assessment` required: required (boolean), spd_type, code_clause, location_basis.

- [ ] **Step 2: Validate IR schema**

```bash
python3 -c "import json; json.load(open('electrical/sld/schemas/sld-ir.schema.json')); print('IR schema parses')"
```

Expected: `IR schema parses`.

- [ ] **Step 3: Create intent schema**

Write `sld-intent.schema.json` per spec §5. Strict mode (`additionalProperties: false`). Required top-level: intent_type (const "sld"), intent_version, produced_by_skill_version, project_id, jurisdiction, supply_summary, board_count, msb_board_id, boards (array of {board_id, role, consumed_db_layout_intent}), spd_assessment_verdict, selectivity_overall_verdict, compliant, produced_at.

- [ ] **Step 4: Validate intent schema**

```bash
python3 -c "import json; json.load(open('electrical/sld/schemas/sld-intent.schema.json')); print('intent schema parses')"
```

- [ ] **Step 5: Commit**

```bash
git add electrical/sld/schemas/
git commit -m "$(cat <<'EOF'
feat(sld): IR + intent schemas (v1.3.0)

sld-ir.schema.json: full system-view IR. Required top-level fields
cover distribution_hierarchy (flat list with parent_board_id pointers),
selectivity_cascade, system_metrics with WI3 deferral flag, supply_
origin, jurisdiction enum, meta with N+1 consumed_intents entries.

sld-intent.schema.json: slim subset for downstream consumers (riser,
cable-containment, maintenance docs). additionalProperties:false
strict mode like db-layout.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 16 — SLD manifest + inputs.json (full rewrite)

**Files:**
- Modify: `electrical/sld/skill.manifest.json` (full rewrite)
- Modify: `electrical/sld/inputs.json` (refresh)

- [ ] **Step 1: Rewrite manifest**

Replace `electrical/sld/skill.manifest.json` content entirely with full structure per spec §8. Version `1.3.0`, status `beta`, produces_intent `"sld"`, consumes_intents `["db-layout"]`, 6 standards layers referenced, ontology + rules + constraints + validators arrays populated, 3 prompts (generator/validator/reviewer), 7 evals, 4 examples.

Use the precedent at `electrical/earthing/skill.manifest.json` as the structural template; adapt for SLD.

- [ ] **Step 2: Refresh inputs.json**

Refresh per WI1 schema. Required input items: jurisdiction, project_id, supply_brief (DNO/utility data), distribution_hierarchy_brief (list of boards with optional consumed_intent_path), system_metrics_assumptions.

Use `electrical/earthing/inputs.json` as structural template.

- [ ] **Step 3: Validate**

```bash
python3 -c "import json; d=json.load(open('electrical/sld/skill.manifest.json')); assert d['version']=='1.3.0'; assert d['produces_intent']=='sld'; assert 'db-layout' in d['consumes_intents']; print('manifest OK')"
python3 -c "import json; json.load(open('electrical/sld/inputs.json')); print('inputs OK')"
```

Expected: `manifest OK` + `inputs OK`.

- [ ] **Step 4: Commit**

```bash
git add electrical/sld/skill.manifest.json electrical/sld/inputs.json
git commit -m "$(cat <<'EOF'
feat(sld): manifest v1.3.0 + inputs.json refresh

Full manifest rewrite from sparse v1.2.0 legacy form to v1.3.0 full
artefact pattern: produces_intent="sld", consumes_intents=["db-layout"],
3 prompts (generator/validator/reviewer), 4 rules + 3 constraints +
3 validators (YAML), 2 ontology JSONs, 7 evals, 4 examples,
6 standards layers referenced.

inputs.json refreshed per WI1 — jurisdiction + project_id +
supply_brief + distribution_hierarchy_brief + system_metrics_
assumptions discovery items.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 17 — SLD generator prompt (12-step pattern)

**Files:**
- Create: `electrical/sld/prompts/generator.md` (NEW file — replaces archived legacy)

- [ ] **Step 1: Write generator.md with 12 steps**

Use `electrical/earthing/prompts/generator.md` as structural template (it's the most recent and has the v1.3 Step 0.5 WI4 consumption pattern).

12 steps per spec § 5:
- Step 0: Read input.json + identify jurisdiction; route to standards layer
- Step 0.5: Resolve upstream intents (multi-board: each distribution_hierarchy node has a consumed_intent_path — read all N+1 db-layout intent-out.json files)
- Step 1: Determine supply origin (DNO/utility, system_type, Ze, PFC, voltage_arrangement) from input.json
- Step 2: Build distribution_hierarchy tree (root MSB + sub-DB nodes with parent_board_id + fed_via_circuit_id pointers)
- Step 3: Compute Imax_total at MSB (sum of board demands × diversity factor where applicable)
- Step 4: Compute peak_pfc_ka at MSB busbar (inline LLM estimate; tool_call_pending_for_system_metrics flag)
- Step 5: Verify intake capacity (main_switch_rating_a ≥ Imax_total; fail with flag if not)
- Step 6: Cascade selectivity check (one verdict per parent→child link in selectivity_cascade[])
- Step 7: SPD assessment per jurisdiction lookup
- Step 8: Life-safety isolation check (fire alarm + emergency lighting + UPS-essential boards)
- Step 9: Drawing notes + symbol roll-up (IEC 60617 symbol_ids)
- Step 10: Compliance summary + assumptions
- Step 11: Build intent-out (slim subset per intent schema)
- Step 12: Rationale block (WI2 — 8 sections + chat_summary ≤500 chars)

Include explicit text for the WI4 multi-board consumption: "When `input.distribution_hierarchy_brief[]` declares multiple boards, each with a `consumed_intent_path`, read EACH path and adopt the upstream `circuits[]` + breaker_rating + breaker_curve + voltage_class + route_length verbatim per board."

Include WI3 tool deferral instructions: "Set `system_metrics.tool_call_pending_for_system_metrics: true` and append to top-level `flags[]`: `'TOOL-CALL-PENDING:sld_system_metrics — System metrics are LLM-estimates; deterministic refinement deferred per WI3.'`"

Include jurisdiction citation form table:
- GB: `BS 7671:2018+A2 Reg X.Y.Z`
- EU/INT: `IEC 60364-X-XX:YEAR Clause X.Y.Z`
- KE: `KS 1700:2018 §X.Y.Z` (banned: `BS 7671 ... (adopted by KS 1700)` annotation)
- US: `NEC 2023 Article XXX.X`

- [ ] **Step 2: Validate generator prompt**

```bash
grep -c "^## Step" electrical/sld/prompts/generator.md
grep -c "consumed_intent_path" electrical/sld/prompts/generator.md
grep -c "tool_call_pending_for_system_metrics" electrical/sld/prompts/generator.md
```

Expected: Step count ≥12; consumed_intent_path ≥2; tool_call_pending_for_system_metrics ≥1.

- [ ] **Step 3: Commit**

```bash
git add electrical/sld/prompts/generator.md
git commit -m "$(cat <<'EOF'
feat(sld): generator prompt (v1.3.0) — 12-step pattern

Replaces archived 1245-line legacy generator with 12-step pattern
matching arc-flash + cable-sizing + fault-level + earthing.

Includes: WI4 multi-board intent consumption (Step 0.5), WI3 tool
deferral for system_metrics (Step 4-5), WI2 rationale block (Step 12),
jurisdiction-specific citation form table, cascade selectivity (Step 6),
SPD assessment per jurisdiction lookup (Step 7), life-safety isolation
(Step 8).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 18 — SLD validator + reviewer prompts

**Files:**
- Create: `electrical/sld/prompts/validator.md` (10 INV checks)
- Create: `electrical/sld/prompts/reviewer.md` (6 D-check pattern)

- [ ] **Step 1: Write validator.md with 10 INVs**

Use `electrical/earthing/prompts/validator.md` as template. SLD 10 INVs per spec §5:

| INV | Check |
|---|---|
| INV-1 | distribution_hierarchy[0] has parent_board_id == null (single root) |
| INV-2 | All non-root nodes have parent_board_id pointing to an existing node |
| INV-3 | All boards have consumed_intent_path pointing to a real file |
| INV-4 | meta.consumed_intents[] length matches distribution_hierarchy[] length |
| INV-5 | system_metrics.imax_total_a ≤ supply_origin.main_switch_rating_a |
| INV-6 | system_metrics.peak_pfc_ka ≤ supply_origin.main_switch_breaking_capacity_ka |
| INV-7 | selectivity_cascade[] has exactly N-1 entries for N boards (one per parent→child link) |
| INV-8 | SPD assessment present + jurisdiction-appropriate code_clause |
| INV-9 | Tool deferral shape: tool_call_pending_for_system_metrics true ↔ TOOL-CALL-PENDING flag in flags[] |
| INV-10 | Jurisdiction routing: KE citations start with "KS 1700:"; UK with "BS 7671:"; US with "NEC 2023" or "NFPA 70:"; INT with "IEC 60364" |

Each INV documented with:
- The check (what condition must hold)
- The IR field path(s) involved
- Severity (all CRITICAL for v1.3)
- Failure message template

- [ ] **Step 2: Write reviewer.md with 6 D-checks**

Use `electrical/earthing/prompts/reviewer.md` as template. SLD 6 D-checks per spec §5:

| D | Domain |
|---|---|
| D1 — Design intent | Does hierarchy match brief? Right number of boards? Correct roles? |
| D2 — Data lineage | Every consumed_intent_path resolves; meta.consumed_intents covers all boards |
| D3 — Discipline integrity | Selectivity verdict realistic? SPD requirement appropriate to location/jurisdiction? |
| D4 — Documentation | Rationale block complete (8 sections); chat_summary ≤ 500 chars |
| D5 — Diversity / aggregation | Imax_total correctly aggregates board demands with diversity? |
| D6 — Deferred tools | tool_call_pending_for_system_metrics flag set + replay payload captured? |

- [ ] **Step 3: Validate**

```bash
grep -c "^## INV-" electrical/sld/prompts/validator.md
grep -c "^## D" electrical/sld/prompts/reviewer.md
```

Expected: INV count == 10; D count == 6.

- [ ] **Step 4: Commit**

```bash
git add electrical/sld/prompts/validator.md electrical/sld/prompts/reviewer.md
git commit -m "$(cat <<'EOF'
feat(sld): validator + reviewer prompts (v1.3.0)

validator.md: 10 INV checks (cascade structure + selectivity + SPD +
intake capacity + tool deferral + jurisdiction routing).
reviewer.md: 6 D-checks (design intent + data lineage + discipline
integrity + documentation + diversity + deferred tools).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 19 — SLD rules + constraints + validation YAMLs (10 files)

**Files:**
- Create: `electrical/sld/rules/distribution-hierarchy.yaml`
- Create: `electrical/sld/rules/device-selection.yaml`
- Create: `electrical/sld/rules/spd-policy.yaml`
- Create: `electrical/sld/rules/life-safety-isolation.yaml`
- Create: `electrical/sld/constraints/selectivity-cascade.yaml`
- Create: `electrical/sld/constraints/intake-capacity.yaml`
- Create: `electrical/sld/constraints/intent-shape.yaml`
- Create: `electrical/sld/validation/ir-integrity.yaml`
- Create: `electrical/sld/validation/jurisdiction-routing.yaml`
- Create: `electrical/sld/validation/tool-deferral-shape.yaml`

- [ ] **Step 1: Create rules directory + 4 rule YAMLs**

```bash
mkdir -p electrical/sld/rules electrical/sld/constraints electrical/sld/validation
```

Use `electrical/earthing/rules/` siblings as structural templates. Each rule YAML has:

```yaml
name: <rule-name>
applies_to: electrical/sld
description: <one-line description>

rules:
  - id: <rule-id>
    when: <condition>
    then: <required action>
    rationale: <engineering justification>
    code_clause: <BS/IEC/NEC/KS reference>
```

Per-file content:

**`distribution-hierarchy.yaml`** — 6 rules covering:
- Single root (one node with parent_board_id == null)
- All non-root nodes have parent in same array
- board_role enum values (main_switchboard / sub_distribution_board / panel / sub_panel / fire_alarm_panel / life_safety_panel / ups_distribution)
- Fire_alarm_panel nodes have parent's fed_via_circuit voltage_class == "fire_alarm"
- UPS_distribution nodes are conceptually downstream of main supply but supply isolated downstream loads
- Sub-board cardinality (no recursive parent-child loops)

**`device-selection.yaml`** — 4 rules covering:
- MCCB selection per breaker rating ranges (≥100A typically MCCB; ≤63A typically MCB)
- Type curve per load profile (Type B general; Type C motor/transformer; Type D high-inrush motor)
- Breaking capacity per fault level (≥ declared PFC at board busbar)
- AIC ratings for US jurisdictions (NEC convention)

**`spd-policy.yaml`** — 4 rules per jurisdiction:
- GB: BS 7671 §443 → Type 2 default for indoor; Type 1+2 where lightning risk; Type 3 final-circuit
- EU/INT: IEC 60364-4-44 → similar tiering
- KE: KS 1700 §443 (adopts BS) → Type 1+2 typical for KPLC supplies + atmospheric overvoltage risk
- US: NEC 285 → Type 1 service-entry; Type 2 branch panel; SPD required for residential per NEC 230.67 (2020+)

**`life-safety-isolation.yaml`** — 4 rules:
- Fire alarm circuits: BS 7671 §560.7 / IEC 60364-5-56 §560 — dedicated supply, no upstream RCD, monitored cabling
- Emergency lighting: BS 5266 / IEC 60364-5-56 §560.9 — dedicated supply or battery-backed luminaires
- UPS-fed essential loads: dedicated supply downstream of UPS output
- Life-safety isolation in mixed boards: physical separation OR dedicated breakers with no RCD upstream

- [ ] **Step 2: Create 3 constraint YAMLs (8 checks total)**

`constraints/selectivity-cascade.yaml` (3 checks):
- Every parent→child link in distribution_hierarchy has a corresponding entry in selectivity_cascade
- selectivity_cascade entries have verdict from valid enum (selective | partial_selective | non_selective)
- non_selective verdicts have a `_note` field with rationale OR a compliance_summary.assumption

`constraints/intake-capacity.yaml` (2 checks):
- supply_origin.main_switch_rating_a ≥ system_metrics.imax_total_a
- supply_origin.main_switch_breaking_capacity_ka ≥ system_metrics.peak_pfc_ka

`constraints/intent-shape.yaml` (3 checks):
- intent-out.board_count matches IR.distribution_hierarchy.length
- intent-out.msb_board_id matches the IR root node's board_id
- intent-out.boards[] has one entry per IR.distribution_hierarchy[] entry

- [ ] **Step 3: Create 3 validation YAMLs (9 checks total)**

`validation/ir-integrity.yaml` (3 checks): root node + parent pointer integrity per spec §8
`validation/jurisdiction-routing.yaml` (3 checks): citation form per jurisdiction per spec §8 / INV-10
`validation/tool-deferral-shape.yaml` (3 checks): INV-9 enforcement (tool_call_pending_for_system_metrics + TOOL-CALL-PENDING string pair consistency)

- [ ] **Step 4: Validate all 10 YAMLs**

```bash
python3 <<'PY'
import yaml, os
for d in ['rules', 'constraints', 'validation']:
    for f in os.listdir(f'electrical/sld/{d}'):
        if f.endswith('.yaml'):
            yaml.safe_load(open(f'electrical/sld/{d}/{f}'))
            print(f'{d}/{f}: OK')
PY
```

Expected: 10 OK lines.

- [ ] **Step 5: Commit**

```bash
git add electrical/sld/rules/ electrical/sld/constraints/ electrical/sld/validation/
git commit -m "$(cat <<'EOF'
feat(sld): rules + constraints + validation YAMLs (10 files)

4 rules: distribution-hierarchy, device-selection, spd-policy,
life-safety-isolation. 3 constraints: selectivity-cascade (3 checks),
intake-capacity (2 checks), intent-shape (3 checks). 3 validation:
ir-integrity (3 checks), jurisdiction-routing (3 checks), tool-
deferral-shape (3 checks).

Total: 17 deterministic checks across the SLD skill.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 20 — SLD ontology + README rewrite

**Files:**
- Create: `electrical/sld/ontology/board-roles.json`
- Create: `electrical/sld/ontology/distribution-types.json`
- Modify: `electrical/sld/README.md` (full rewrite from stub)

- [ ] **Step 1: Create ontology directory + 2 JSON files**

```bash
mkdir -p electrical/sld/ontology
```

`board-roles.json` — 7-entry enum with definitions:

```json
{
  "board_roles": [
    { "id": "main_switchboard",        "label": "Main Switchboard (MSB)", "description": "Top-level board fed directly from the utility intake. Distributes to sub-DBs.", "typical_intake_a_range": [100, 4000] },
    { "id": "sub_distribution_board",  "label": "Sub-Distribution Board (SDB)", "description": "Intermediate board fed from MSB or another upstream board. Distributes to final circuits or further sub-boards.", "typical_intake_a_range": [40, 400] },
    { "id": "panel",                   "label": "Panel (US convention)", "description": "US/NEC equivalent of sub-distribution board. Single-board scope; serves final circuits in a defined area.", "typical_intake_a_range": [60, 400] },
    { "id": "sub_panel",               "label": "Sub-Panel (US convention)", "description": "US/NEC equivalent of a downstream sub-DB. Fed from a main panel; serves tenant or zone loads.", "typical_intake_a_range": [40, 200] },
    { "id": "fire_alarm_panel",        "label": "Fire Alarm Panel", "description": "Dedicated life-safety panel. No upstream RCD (per IEC 60364-5-56 §560 / BS 7671 §560). voltage_class: fire_alarm.", "typical_intake_a_range": [16, 100] },
    { "id": "life_safety_panel",       "label": "Life-Safety Panel (emergency lighting / fire pump / smoke control)", "description": "Dedicated panel for emergency lighting, fire pump, or smoke control. Dedicated supply per BS 7671 §560 / IEC 60364-5-56 / NEC 695/700.", "typical_intake_a_range": [16, 200] },
    { "id": "ups_distribution",        "label": "UPS Distribution Panel", "description": "Downstream of UPS output. Serves uninterruptible loads (typically IT / process / data). May have dedicated grounding.", "typical_intake_a_range": [16, 400] }
  ]
}
```

`distribution-types.json` — topology semantics:

```json
{
  "distribution_types": [
    { "id": "radial",         "label": "Radial",                  "description": "Each board fed from one upstream feeder. No alternative path.", "common_jurisdictions": ["GB", "EU", "INT", "US"] },
    { "id": "ring",           "label": "Ring",                    "description": "Boards connected in a closed loop; each board fed from two directions.", "common_jurisdictions": ["GB (legacy)"] },
    { "id": "split_phase",    "label": "Split-Phase (US 120/240V)", "description": "US residential / small commercial convention. Single-phase supply with center tap providing 120V to neutral or 240V phase-to-phase.", "common_jurisdictions": ["US"] },
    { "id": "tpn",            "label": "Three-Phase Plus Neutral (TPN)", "description": "3-phase + N. Most common commercial/industrial supply globally. TN-S, TN-C-S, TT, IT subtypes per earthing system.", "common_jurisdictions": ["GB", "EU", "INT", "KE"] },
    { "id": "tpn_plus_e",     "label": "Three-Phase Plus Neutral + Separate Earth (TPN+E)", "description": "TPN with separate Earth conductor at intake. TN-S subtype.", "common_jurisdictions": ["GB (older)", "KE (older)"] }
  ]
}
```

- [ ] **Step 2: Rewrite README.md**

Replace stub README with full content following the structure of `electrical/earthing/README.md`. Cover: skill purpose, status, standards layers consumed, jurisdiction support, eval coverage matrix, tool calls awaiting runtime, file structure, known limitations, versioning, license.

- [ ] **Step 3: Validate**

```bash
python3 -c "import json; [json.load(open(f'electrical/sld/ontology/{f}.json')) for f in ['board-roles', 'distribution-types']]; print('ontology OK')"
wc -l electrical/sld/README.md
```

Expected: `ontology OK`; README ≥40 lines (substantial, not stub).

- [ ] **Step 4: Commit**

```bash
git add electrical/sld/ontology/ electrical/sld/README.md
git commit -m "$(cat <<'EOF'
feat(sld): ontology (2 JSONs) + README rewrite

board-roles.json: 7-entry enum (main_switchboard, sub_distribution_
board, panel, sub_panel, fire_alarm_panel, life_safety_panel, ups_
distribution).

distribution-types.json: 5 topology entries (radial, ring, split_phase,
tpn, tpn_plus_e).

README.md: full rewrite from stub. Covers skill purpose, jurisdiction
support, eval coverage matrix, file structure, known limitations.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

# PHASE C — SLD worked examples (Tasks 21-24)

## Task 21 — UK 3-storey office SLD example

**Files:** `electrical/sld/examples/uk-commercial-office-3storey/{input,output,intent-out}.json + reasoning.md + sample-schedule.md`

**Scenario:** Spec §7 Example 1. 4-board cascade (MSB-MAIN → SDB-GF / SDB-L1 / SDB-L2).

**Consumes 4 db-layout intents** (produced in Tasks 1-4 of this sprint).

- [ ] **Step 1: Create directory + 5 files**

```bash
mkdir -p electrical/sld/examples/uk-commercial-office-3storey
```

Author 5 files. Key fields:

**input.json:**
```json
{
  "project_id": "uk-3storey-office-eg01",
  "site_brief": "3-storey UK commercial office, 1200m² GIA. TN-C-S 400V TPN supply.",
  "jurisdiction": "GB",
  "supply_brief": {
    "supplier": "UK DNO",
    "system_type": "TN-C-S",
    "voltage_nominal_v": 400,
    "voltage_arrangement": "TPN_plus_E",
    "frequency_hz": 50,
    "ze_declared_ohm": 0.35,
    "pfc_declared_ka": 9.8,
    "main_switch_rating_a": 400,
    "main_switch_breaking_capacity_ka": 36
  },
  "distribution_hierarchy_brief": [
    { "board_id": "MSB-MAIN", "board_role": "main_switchboard",        "consumed_intent_path": "electrical/db-layout/examples/uk-commercial-msb-3storey/intent-out.json", "parent_board_id": null, "fed_via_circuit_id": null,    "location": "ground-floor plant room" },
    { "board_id": "SDB-GF",   "board_role": "sub_distribution_board",  "consumed_intent_path": "electrical/db-layout/examples/uk-commercial-sdb-gf/intent-out.json",     "parent_board_id": "MSB-MAIN", "fed_via_circuit_id": "F01", "location": "ground-floor riser cupboard" },
    { "board_id": "SDB-L1",   "board_role": "sub_distribution_board",  "consumed_intent_path": "electrical/db-layout/examples/uk-commercial-sdb-l1/intent-out.json",     "parent_board_id": "MSB-MAIN", "fed_via_circuit_id": "F02", "location": "level-1 riser cupboard" },
    { "board_id": "SDB-L2",   "board_role": "sub_distribution_board",  "consumed_intent_path": "electrical/db-layout/examples/uk-commercial-sdb-l2/intent-out.json",     "parent_board_id": "MSB-MAIN", "fed_via_circuit_id": "F03", "location": "level-2 riser cupboard" }
  ],
  "spd_assessment_inputs": {
    "location_type": "urban_commercial",
    "lightning_risk": "moderate",
    "life_safety_present": true
  }
}
```

**output.json:** Full IR with:
- `meta.consumed_intents` = 4 entries (one per board)
- `meta.skill_version` = "sld/1.3.0"
- `jurisdiction` = "GB"
- `supply_origin` per input + main switch fields
- `distribution_hierarchy` = 4 nodes matching input
- `selectivity_cascade` = 3 entries (MSB→SDB-GF, MSB→SDB-L1, MSB→SDB-L2 each "selective")
- `system_metrics` with imax_total=146A, peak_pfc=9.8kA, spd_assessment={required: true, spd_type: "Type 2", code_clause: "BS 7671:2018+A2 Reg 443", location_basis: "urban commercial with moderate lightning risk"}
- `system_metrics.tool_call_pending_for_system_metrics` = true
- `flags` includes TOOL-CALL-PENDING string
- `compliance_summary.compliant` = true
- `rationale` block with 8 sections per WI2
- Citations all in `BS 7671:2018+A2 ...` form

**intent-out.json:** Slim subset per intent schema. 4-board list. spd_assessment_verdict="required_type_2"; selectivity_overall_verdict="fully_selective"; compliant=true.

**reasoning.md:** Engineer narrative covering site context, board sizing, cascade selectivity, SPD assessment, life-safety isolation, consumption pattern (4 db-layout intents).

**sample-schedule.md:** Board-level summary table (4 rows: MSB + 3 SDBs).

- [ ] **Step 2: Validate cross-file consistency**

```bash
python3 <<'PY'
import json
e = json.load(open('electrical/sld/examples/uk-commercial-office-3storey/output.json'))
assert e['jurisdiction'] == 'GB'
assert len(e['distribution_hierarchy']) == 4
assert len(e['meta']['consumed_intents']) == 4
assert len(e['selectivity_cascade']) == 3
assert e['system_metrics']['tool_call_pending_for_system_metrics'] is True
roots = [n for n in e['distribution_hierarchy'] if n.get('parent_board_id') is None]
assert len(roots) == 1, 'Single root expected'
for n in e['distribution_hierarchy']:
    if n.get('parent_board_id'):
        assert n['parent_board_id'] in {x['board_id'] for x in e['distribution_hierarchy']}, f"orphan parent ref {n['parent_board_id']}"
import os
for n in e['distribution_hierarchy']:
    assert os.path.exists(n['consumed_intent_path']), f"missing intent {n['consumed_intent_path']}"
print('UK SLD: OK — 4 boards, 3 cascade verdicts, all consumed_intent_paths resolve')
PY
```

Expected: `UK SLD: OK ...`.

- [ ] **Step 3: Commit**

```bash
git add electrical/sld/examples/uk-commercial-office-3storey/
git commit -m "$(cat <<'EOF'
feat(sld): UK 3-storey office worked example

4-board cascade: MSB-MAIN → SDB-GF / SDB-L1 / SDB-L2. Consumes 4
db-layout intents (one per board). BS 7671:2018+A2 jurisdiction.
SPD Type 2 required per Reg 443. tool_call_pending_for_system_metrics
true per WI3 deferral.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 22 — KE Nairobi industrial MSB-GH SLD example

**Files:** `electrical/sld/examples/ke-nairobi-industrial-msb-gh/{input,output,intent-out}.json + reasoning.md + sample-schedule.md`

**Scenario:** Spec §7 Example 2. 2-board cascade (MSP-100 → GH-DB). KS 1700 jurisdiction.

**Consumes 2 db-layout intents:** existing `ke-nairobi-industrial-100A-tpn` (MSP-100) + new `ke-nairobi-gh-db` (GH-DB).

- [ ] **Step 1: Create directory + 5 files**

Same pattern as Task 21 but smaller cascade (2 boards). Key differences:
- `jurisdiction: "KE"`
- Citations in KE form: `KS 1700:2018 §X.Y.Z` (NO `BS 7671 ... (adopted by KS 1700)` annotation)
- `supply_origin`: KPLC TN-S 415V, Ze=0.80Ω, PFC=9.8kA, wayleave_or_account_reference="KPLC-NRB-IND-2143"
- `distribution_hierarchy`: 2 nodes (MSP-100 root + GH-DB child via C08)
- `selectivity_cascade`: 1 entry (MSP-100 C08 → GH-DB)
- `system_metrics.spd_assessment`: Type 1+2 required (KPLC industrial site + KS Annex G coastal/highland adjustment)
- `meta.consumed_intents`: 2 entries
- Reasoning.md emphasises KS 1700 deviations (§411.3.3 socket-RCD applied at GH-DB) + cross-domain consumption demonstration

- [ ] **Step 2: Validate + commit**

Same validation script as Task 21 (paths adjusted). Commit message:
```
feat(sld): KE Nairobi industrial MSB-GH worked example

2-board cascade (MSP-100 → GH-DB via 60m C08 submain). Consumes
existing KE MSP-100 intent + new gate-house DB intent. KS 1700:2018
jurisdiction with direct citation form (no BS-annotation pattern).
SPD Type 1+2 required per KS §443. KS 1700 §411.3.3 universal
socket-RCD applied at GH-DB.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

---

## Task 23 — INT commercial MSB + 4 sub-DBs SLD example

**Files:** `electrical/sld/examples/intl-commercial-msb-4subdbs/{input,output,intent-out}.json + reasoning.md + sample-schedule.md`

**Scenario:** Spec §7 Example 3. 5-board cascade (MSB-MAIN → DB-L1 + DB-P1 + DB-M1 + DB-FA1).

**Consumes 5 db-layout intents:** existing `intl-commercial-tpn-msb` (MSB-MAIN) + 4 new (intl-dbl1-lighting + intl-dbp1-power + intl-dbm1-mechanical + intl-dbfa1-fire-alarm).

- [ ] **Step 1: Create directory + 5 files**

5-board cascade. Key engineering points to document:
- DB-FA1 fire-alarm has `board_role: "fire_alarm_panel"`; no upstream RCD (life-safety exemption)
- DB-FA1's `fed_via_circuit_id: "F04"` consumes the existing INT MSB's F04 feeder (fire_alarm voltage class)
- selectivity_cascade has 4 entries (MSB → each sub-DB)
- For DB-FA1 link: verdict may be `partial_selective` due to no RCD upstream; rationale documents life-safety isolation per IEC 60364-5-56 §560
- Citations: generic IEC 60364 form (`IEC 60364-X-XX:YEAR Clause X.Y.Z`)

- [ ] **Step 2: Validate + commit**

Same validation pattern as Task 21 (5 boards instead of 4). Commit message:
```
feat(sld): INT commercial MSB + 4 sub-DBs worked example

5-board cascade: MSB-MAIN → DB-L1 (lighting) + DB-P1 (small-power) +
DB-M1 (mechanical) + DB-FA1 (fire alarm — life-safety, no upstream
RCD per IEC 60364-5-56 §560). Consumes 5 db-layout intents (1
existing INT MSB rollup + 4 new sub-DBs). Generic IEC 60364
citation form (no Kenya cues — this is the international example).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

---

## Task 24 — US strip mall MSP + tenant sub-panels SLD example

**Files:** `electrical/sld/examples/us-strip-mall-msp-tenants/{input,output,intent-out}.json + reasoning.md + sample-schedule.md`

**Scenario:** Spec §7 Example 4. 4-board cascade (MSP-A → TSP-A + TSP-B + CA-P).

**Consumes 4 db-layout intents:** existing `us-strip-mall-panelboard` (MSP-A) + 3 new (us-strip-mall-tsp-a + tsp-b + common-area).

- [ ] **Step 1: Create directory + 5 files**

US conventions throughout:
- `voltage_nominal_v: 208`
- `voltage_arrangement: "TPN"` (Y-connected 208V/120V)
- Citations: `NEC 2023 Article XXX.X`
- AWG cable references in reasoning.md (no SI in citations)
- SPD: NEC 285 Type 1 at service entrance + Type 2 at branch panels
- `system_metrics.spd_assessment.code_clause`: `"NEC 2023 Article 285"`

- [ ] **Step 2: Validate + commit**

Commit:
```
feat(sld): US strip mall MSP + tenant sub-panels worked example

4-board cascade: MSP-A → TSP-A + TSP-B + CA-P. Consumes 4 db-layout
intents (1 existing US main panelboard + 3 new sub-panels). NEC 2023
citation form. SPD Type 1 service-entry + Type 2 branch per NEC 285.
AWG cables throughout.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

---

# PHASE D — Evals + bookkeeping + final review (Tasks 25-28)

## Task 25 — 7 eval YAMLs

**Files:**
- Create: `electrical/sld/evals/eval-01-uk-3storey-happy-path.yaml`
- Create: `electrical/sld/evals/eval-02-ke-msp-gh-cascade.yaml`
- Create: `electrical/sld/evals/eval-03-intake-undersized-trap.yaml`
- Create: `electrical/sld/evals/eval-04-missing-spd-assessment.yaml`
- Create: `electrical/sld/evals/eval-05-non-selective-cascade.yaml`
- Create: `electrical/sld/evals/eval-06-rationale-block.yaml`
- Create: `electrical/sld/evals/eval-07-multi-board-intent-consumption.yaml`

- [ ] **Step 1: Create eval-01 (UK happy path)**

Use `electrical/earthing/evals/eval-09-db-layout-intent-consumption.yaml` as YAML template. Adapt for SLD UK example. 8-10 assertions covering: jurisdiction GB; 4 boards in distribution_hierarchy; 4 entries in meta.consumed_intents; 3 selectivity_cascade verdicts; SPD Type 2 required; tool deferral flag set + TOOL-CALL-PENDING string in flags.

- [ ] **Step 2: Create eval-02 (KE happy path with KS 1700 citations)**

Adapt for KE. 8-10 assertions: jurisdiction KE; 2 boards; KS 1700 citation form for ALL `code_clause` fields; SPD Type 1+2 required; consumed_intents references KE MSP-100 + GH-DB.

- [ ] **Step 3: Create eval-03 (validation_trap: intake undersized)**

Trap test — assert that when supply_origin.main_switch_rating_a < system_metrics.imax_total_a, IR carries an INV-5 non-compliance flag with severity critical. Input fixture has main_switch=200A but imax=320A.

- [ ] **Step 4: Create eval-04 (validation_trap: missing SPD)**

Trap test — assert that an IR with `system_metrics.spd_assessment` absent fails INV-8 validation. Input fixture has SPD-relevant location but generator omitted the assessment.

- [ ] **Step 5: Create eval-05 (edge_case: non_selective cascade)**

Edge case — parent breaker not selective against child (e.g., 100A MCCB feeding 80A MCB at ratio < 1.25:1). Assert IR has selectivity_cascade entry with verdict `non_selective` + rationale note in compliance_summary.assumptions.

- [ ] **Step 6: Create eval-06 (WI2 rationale block coverage)**

Standard WI2 coverage test — assert rationale.sections.length ≥ 8 (or ≥ 6 in v1.3, with versioning); chat_summary length ≤ 500; rationale present in all 4 SLD examples.

- [ ] **Step 7: Create eval-07 (skill_specific: multi-board consumption)**

Core skill-specific test:
- All 4 SLD examples have consumed_intent_path in input.json's distribution_hierarchy_brief entries
- All 4 examples have meta.consumed_intents.length == distribution_hierarchy.length
- Every consumed_intent_path resolves to an existing file
- Field alignment: for each board, board_role matches the role declared in the consumed db-layout intent (where applicable)

- [ ] **Step 8: Validate all 7 evals + commit**

```bash
python3 <<'PY'
import yaml, os
for f in sorted(os.listdir('electrical/sld/evals')):
    if f.endswith('.yaml'):
        d = yaml.safe_load(open(f'electrical/sld/evals/{f}'))
        assert d.get('name', '').startswith('eval-'), f
        print(f'{f}: OK ({len(d.get("checks", []))} checks)')
PY
```

Expected: 7 OK lines.

Commit:
```
feat(sld): 7 evals (5 WI5 categories + 2 skill-specific)

eval-01 UK happy path; eval-02 KE happy path + KS 1700 citation;
eval-03 intake undersized trap; eval-04 missing SPD trap; eval-05
non-selective cascade edge case; eval-06 WI2 rationale block; eval-07
skill-specific multi-board WI4 consumption.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

---

## Task 26 — SLD v1.3 bookkeeping (CHANGELOG + SKILLS_STATUS + ARCHITECTURE.md)

**Files:**
- Modify: `electrical/sld/CHANGELOG.md`
- Modify: `SKILLS_STATUS.md` (sld row)
- Modify: `ARCHITECTURE.md`

- [ ] **Step 1: SLD CHANGELOG v1.3.0 entry**

Use Edit. Find existing top (likely `## [1.2.0]` legacy). Insert IMMEDIATELY BEFORE:

```markdown
## [1.3.0] - 2026-05-18

### Added
- **Full rebuild to artefact pattern.** Manifest grows from sparse legacy form to full v1.3 structure (produces_intent, consumes_intents, 3 prompts, 4 rules, 3 constraints, 3 validators, 2 ontology, 7 evals, 4 examples).
- **IR schema** (`sld-ir.schema.json`) — first-time SLD has a formal IR schema. Required fields: distribution_hierarchy (flat list with parent_board_id pointers), selectivity_cascade, system_metrics, supply_origin, jurisdiction (enum GB/EU/INT/KE/US), meta.consumed_intents.
- **Intent schema** (`sld-intent.schema.json`) — slim downstream-consumable subset.
- **12-step generator prompt** replacing legacy 1245-line monolith. Mirrors arc-flash + cable-sizing + fault-level + earthing pattern. Includes Step 0.5 multi-board WI4 consumption.
- **10 INV validator + 6 D reviewer** prompts.
- **17 deterministic checks** across 4 rules + 3 constraints + 3 validation YAMLs.
- **4 worked examples** (UK 3-storey office, KE Nairobi industrial, INT commercial MSB+4subDBs, US strip mall MSP+tenants).
- **7 evals** (5 WI5 categories + 2 skill-specific WI4 consumption).
- **2 ontology JSONs** (board-roles with 7 roles + distribution-types with 5 topologies).

### Changed
- **Legacy 1245-line generator archived** at `electrical/sld/docs/legacy-generator-v1.2-engineering-reference.md`. Engineering content preserved as reference; replaced by 12-step generator at `prompts/generator.md`.
- **inputs.json refreshed** per WI1 — discovery questions include consumed_intent_path per board.
- **README.md fully rewritten** (was stub-flagged).
- **db-layout dependency** — consumes_intents now actively populated (was declared but unused in legacy v1.2).

### Removed
- `electrical/sld/evals/evals-combined.md` (atomized into 7 per-eval YAMLs)
- `electrical/sld/examples/examples-combined.md` (atomized into 4 example folders)

### Notes
- **Paired with db-layout v1.2.0** which adds 12 new companion examples (60 files) supporting full cascade WI4 consumption.
- **WI3 tool deferral** for system_metrics: `calc.sld_system_metrics` not yet runtime-shipped; system_metrics values are LLM-estimates with disclaimer in flags.
- **No schema changes to db-layout** — db-layout intent shape unchanged.
- **Future v1.4.0** will add earthing + fault-level intent consumption.
- **Future v1.5.0** will add drawing position layout (Stage 2).
```

- [ ] **Step 2: SKILLS_STATUS sld row**

Replace the existing sld row with:

```
| sld | `electrical/sld` | **beta** | BS 7671:2018, IEC 60364, IEC 61439, NFPA 70 (NEC 2023), KS 1700:2018, IEC 60617 | 7/3 ✓ | v1.3.0 — full rebuild from legacy 1245-line generator into proven artefact pattern. 4 worked examples (UK + KE + INT + US) each consuming N+1 db-layout intents (WI4 multi-board cascade). Legacy archived as engineering reference. system_metrics deferred to calc.sld_system_metrics per WI3. |
```

- [ ] **Step 3: ARCHITECTURE.md update**

Find the "Cross-drawing intents" → "Worked example pattern" subsection added in earthing v1.3. Append the SLD multi-board generalization:

```markdown
### SLD multi-board generalization (since 2026-05-18, sld v1.3.0)

The `electrical/sld` skill (v1.3+) generalizes the WI4 pattern from single-board (earthing v1.3 consuming one db-layout intent) to multi-board cascade (one db-layout intent per board in the distribution hierarchy).

| Field | Single-board pattern (earthing v1.3) | Multi-board pattern (sld v1.3) |
|---|---|---|
| `meta.consumed_intents[]` length | 1 entry | N+1 entries (one per board) |
| `consumed_intent_path` location | input.json root | distribution_hierarchy[].consumed_intent_path |
| Cross-file alignment | circuits[] subset of upstream | board_id matches upstream db_id |

Generalization template:
- Each downstream consumer reads ALL upstream intent paths
- Each consumer aggregates upstream data into a system-level view + adds its own discipline-specific fields
- Provenance records (meta.consumed_intents) capture every upstream consumed

Future skills (cable-containment, riser, panel-schedule rollup) follow this generalized multi-board pattern.
```

- [ ] **Step 4: Commit**

```bash
git add electrical/sld/CHANGELOG.md SKILLS_STATUS.md ARCHITECTURE.md
git commit -m "$(cat <<'EOF'
docs(sld): v1.3.0 CHANGELOG + SKILLS_STATUS + ARCHITECTURE.md

SLD CHANGELOG v1.3.0 entry with Added + Changed + Removed + Notes.
SKILLS_STATUS sld row bumped v1.2.0 (legacy) → v1.3.0 (rebuild);
evals 0 → 7/3.

ARCHITECTURE.md Cross-drawing intents §Worked example pattern gains
SLD multi-board generalization subsection — extends earthing v1.3's
single-board WI4 to N+1 entries per cascade.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 27 — Cross-cutting validation

**Files:** none (validation script run only)

- [ ] **Step 1: Run cross-cutting validation across all sprint deliverables**

```bash
python3 <<'PY'
import json, yaml, os, sys

# 1. All 12 new db-layout examples + 1 reused = 16 examples in db-layout
db_dir = 'electrical/db-layout/examples'
db_examples = sorted(os.listdir(db_dir))
print(f'db-layout examples: {len(db_examples)} (target: 16)')

# 2. Every db-layout example has 5 files
for e in db_examples:
    files = sorted(os.listdir(f'{db_dir}/{e}'))
    expected = {'input.json', 'output.json', 'intent-out.json', 'reasoning.md', 'sample-schedule.md'}
    missing = expected - set(files)
    if missing:
        print(f'  {e}: MISSING {missing}')

# 3. All db-layout intent-out.json validate against schema
schema = json.load(open('electrical/db-layout/schemas/db-layout-intent.schema.json'))
import jsonschema
for e in db_examples:
    d = json.load(open(f'{db_dir}/{e}/intent-out.json'))
    try:
        jsonschema.validate(d, schema)
        print(f'  {e}: intent schema OK')
    except Exception as ex:
        print(f'  {e}: FAIL — {ex}')

# 4. All 4 SLD examples exist with 5 files each
sld_dir = 'electrical/sld/examples'
sld_examples = sorted(os.listdir(sld_dir))
print(f'\nSLD examples: {len(sld_examples)} (target: 4)')

# 5. All SLD output.json validate against SLD IR schema (basic shape check)
sld_schema = json.load(open('electrical/sld/schemas/sld-ir.schema.json'))
for e in sld_examples:
    d = json.load(open(f'{sld_dir}/{e}/output.json'))
    assert 'meta' in d and 'distribution_hierarchy' in d and 'selectivity_cascade' in d
    n_boards = len(d['distribution_hierarchy'])
    n_consumed = len(d['meta'].get('consumed_intents', []))
    n_cascade = len(d['selectivity_cascade'])
    print(f'  {e}: boards={n_boards}, consumed={n_consumed}, cascade={n_cascade}')
    assert n_consumed == n_boards, f'{e}: consumed/board mismatch'
    assert n_cascade == n_boards - 1, f'{e}: cascade entry count wrong'

# 6. All SLD evals load
evals = sorted(os.listdir('electrical/sld/evals'))
print(f'\nSLD evals: {len(evals)} (target: 7 YAMLs)')
for f in evals:
    if f.endswith('.yaml'):
        yaml.safe_load(open(f'electrical/sld/evals/{f}'))

# 7. Manifests
sld_manifest = json.load(open('electrical/sld/skill.manifest.json'))
assert sld_manifest['version'] == '1.3.0'
assert sld_manifest['produces_intent'] == 'sld'
assert 'db-layout' in sld_manifest['consumes_intents']
assert len(sld_manifest['evals']) == 7
assert len(sld_manifest['examples']) == 4
print(f'\nsld manifest: v{sld_manifest["version"]}; 7 evals; 4 examples OK')

db_manifest = json.load(open('electrical/db-layout/skill.manifest.json'))
assert db_manifest['version'] == '1.2.0'
assert len(db_manifest['examples']) == 16
print(f'db-layout manifest: v{db_manifest["version"]}; 16 examples OK')

# 8. Legacy archived
assert os.path.exists('electrical/sld/docs/legacy-generator-v1.2-engineering-reference.md'), 'legacy not archived'
assert not os.path.exists('electrical/sld/evals/evals-combined.md'), 'legacy evals-combined still present'
assert not os.path.exists('electrical/sld/examples/examples-combined.md'), 'legacy examples-combined still present'
print('\nLegacy archived + combined-md files removed: OK')

print('\nALL CROSS-CUTTING CHECKS PASS')
PY
```

Expected: All OK lines + `ALL CROSS-CUTTING CHECKS PASS`. If any FAIL, fix the underlying file before proceeding.

- [ ] **Step 2: No commit needed** (validation only)

---

## Task 28 — Final code review + push

**Files:** none (review + push)

- [ ] **Step 1: Dispatch code-reviewer agent**

Use the Agent tool with `subagent_type: code-reviewer`:

Description: `Final review SLD v1.3.0 + db-layout v1.2.0 paired sprint`

Prompt:
```
Review the full diff for the SLD rebuild + db-layout v1.2 paired sprint.

Spec: docs/superpowers/specs/2026-05-18-sld-skill-rebuild-design.md
Plan: docs/superpowers/plans/2026-05-18-sld-skill-rebuild-skill.md

Sprint range: commits from start of this sprint (after b894f3b = spec commit) to HEAD (~28 commits).

Run the cross-cutting validation script from Task 27 + report results.

Verify:
1. db-layout has 16 examples (12 new + 4 existing), each with 5 files
2. All db-layout intent-out.json files validate against db-layout-intent.schema.json strict mode
3. SLD has 4 worked examples, each with 5 files + meta.consumed_intents N+1 entries
4. SLD distribution_hierarchy: single root (parent_board_id null) + all child pointers resolve
5. SLD selectivity_cascade: N-1 entries for N boards
6. SLD tool_call_pending_for_system_metrics + TOOL-CALL-PENDING flag pair consistent
7. Legacy archived at docs/legacy-generator-v1.2-engineering-reference.md; combined-md files deleted
8. Manifests: sld v1.3.0 + 7 evals + 4 examples; db-layout v1.2.0 + 16 examples
9. SKILLS_STATUS + CHANGELOG + ARCHITECTURE.md all updated
10. KE example citations all use "KS 1700:" form (no "(adopted by KS 1700)" annotation)
11. US example citations use "NEC 2023 Article" form
12. INT example uses generic IEC 60364 (no Kenya cues)

Report CRITICAL / IMPORTANT / MEDIUM / LOW findings. Under 700 words.
```

- [ ] **Step 2: Fix any review findings**

If CRITICAL or IMPORTANT issues: fix with Edit + commit as `fix(sld): final-review issues — <summary>`. Re-dispatch reviewer until APPROVE.

- [ ] **Step 3: Push to origin/main**

```bash
git push origin main
```

- [ ] **Step 4: Verify push + summary**

```bash
git log --oneline b894f3b..HEAD | head -30
echo ""
echo "Sprint summary:"
echo "- SLD v1.2.0 (legacy) → v1.3.0 (full artefact pattern rebuild)"
echo "- db-layout v1.1.0 → v1.2.0 (12 new cascade-supporting examples)"
echo "- ~108 files; ~28 commits"
echo "- Biggest sprint in project history"
```

Print final summary with file count + commit count + what shipped.

---

## Self-review

**Spec coverage:**
- §1 Why → Plan header + Task 14 archive
- §2 Scope → Task list covers all 108 deliverables
- §3 Architecture decisions → Tasks 14-20 implement
- §4 IR schema → Task 15
- §5 Intent schema → Task 15
- §6 12 new db-layout examples → Tasks 1-12 (one per example) + Task 13 manifest
- §7 4 SLD worked examples → Tasks 21-24 (one per example)
- §8 SLD infrastructure → Tasks 14-20
- §9 Bookkeeping → Task 13 (db-layout) + Task 26 (sld)
- §10 Sequencing → Plan task order matches spec phases
- §11 Acceptance criteria → Task 27 validation script covers
- §12 Risks → addressed across tasks
- §13 Out-of-scope → respected
- §14 Pattern parents → referenced in plan header

**Placeholder scan:** No TBD/TODO patterns in plan steps. Tasks 6-12 (single-paragraph format for repeated db-layout patterns) reference Task 1's full template explicitly — that's standard "use Task X's pattern" guidance rather than a placeholder.

**Type consistency:**
- `consumed_intent_path` (string, in distribution_hierarchy node) — consistent across Tasks 15, 17, 21-24
- `meta.consumed_intents[]` (array with N+1 entries) — consistent across all 4 SLD examples
- intent_version 1.0.0 + produced_by "electrical/db-layout/v1.2.0" — consistent
- 10 INV identifiers (INV-1 through INV-10) — consistent in Task 18 + spec §5
- 6 D identifiers (D1 through D6) — consistent

Plan is internally consistent. Tasks 6-12 use the "follow Task 5's pattern" shorthand where engineering content varies but file structure is identical — acceptable for a 108-file sprint where inlining every example's full content would balloon the plan beyond manageable size.

The plan totals 28 tasks. Effective task density: ~4 files per task average (with peaks at Tasks 1-12 db-layout authoring = 5 files per task, and lows at Tasks 14-20 SLD infrastructure = 1-3 files per task).
