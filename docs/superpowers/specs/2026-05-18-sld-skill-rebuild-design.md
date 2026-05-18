# SLD skill rebuild (v1.3.0) + db-layout v1.2.0 — Full Cascade Design Spec

**Date:** 2026-05-18
**Skill targets:**
- `electrical/sld` v1.2.0 (legacy) → v1.3.0 (rebuild)
- `electrical/db-layout` v1.1.0 → v1.2.0 (12 new companion examples for cascade)
**Sprint type:** Paired major rebuild; biggest sprint in project history (~116 files)
**Strategic context:** Set 2026-05-18 — breadth-first build of all skills before scaling standards across more jurisdictions. SLD is the 7th electrical skill to follow the proven artefact pattern. This sprint also operationalizes WI4 cross-skill intent consumption at MULTI-BOARD scale (earthing v1.3 demonstrated single-board consumption; SLD demonstrates the full cascade pattern).

---

## 1. Why this sprint

The current `electrical/sld/` is internally inconsistent:
- Manifest claims `status: "production"` v1.2.0
- README says "Status: Stub — contributions welcome"
- Generator is a 1245-line single file (engineering substance is good but format is legacy)
- Evals: single `evals-combined.md` (NOT YAML per WI5)
- Examples: single `examples-combined.md` (NOT per-example folders)
- Schemas: EMPTY (no IR schema, no intent schema)
- rules/, constraints/, validation/: EMPTY
- Manifest is sparse: no produces_intent, no consumes_intents, no validators, no 3-prompt structure

The rebuild brings SLD into alignment with the proven artefact pattern from arc-flash + cable-sizing + fault-level + earthing v1.0-v1.3 + arc-flash-labelling. The 1245-line legacy generator is archived as engineering reference; engineering content is preserved verbatim where applicable.

Additionally, this sprint pairs with db-layout v1.2.0 which gains 12 companion examples to support SLD's full-cascade demonstration. Earthing v1.3 (shipped 2026-05-18) demonstrated single-board WI4 consumption; SLD generalizes that to multi-board cascades.

## 2. Scope

### In scope

| Category | Count | Notes |
|---|---|---|
| NEW db-layout companion examples (12 × 5 files) | 60 | UK 4 + KE 1 + INT 4 + US 3 |
| NEW SLD worked examples (4 × 5 files) | 20 | UK + KE + INT + US |
| SLD infrastructure rebuild | 24 | Manifest + inputs + README + 3 prompts + 2 schemas + 4 rules + 3 constraints + 3 validators + 2 ontology + 3 docs (incl. archived legacy generator) + CHANGELOG |
| db-layout v1.2.0 bookkeeping | 2 | Manifest + CHANGELOG |
| SLD v1.3.0 cross-cutting bookkeeping | 2 | SKILLS_STATUS row + ARCHITECTURE.md update |
| **Total** | **~108 files** | Largest sprint in project history (arc-flash-labelling was 73) |

### Out of scope (deferred to future versions)

- Consuming earthing/fault-level intents (v1.4.0+)
- Drawing layout positions (Stage 1 = logical topology only; Stage 2 in future sprint)
- New calc contracts (selectivity + SPD are validator/rule checks, not deferred tools)
- Renderer / SVG / DXF / LISP output (runtime concern)
- Mechanical/plumbing SLD equivalents (different skills)
- Multi-board consumption for cable-sizing, fault-level, arc-flash, lighting-layout (per-skill future sprints)

## 3. Architecture decisions

1. **SLD's distribution_hierarchy is a flat list with parent_board_id pointers.** Tree structure expressed as array of node objects; root marked by null parent_board_id. Easier to validate; reconstruction is downstream concern.

2. **SLD consumes ONE db-layout intent per board in the cascade.** `meta.consumed_intents[]` carries one entry per board (N+1 entries for N sub-DBs + MSB). `distribution_hierarchy[N].consumed_intent_path` per-node points at that board's intent-out.json.

3. **Cascade selectivity is a validator check (not a calc tool).** For each parent→child link, verify the upstream breaker selectively trips before downstream short-circuit fault. Reads breaker_rating + breaker_curve from upstream + downstream intent payloads. Verdict recorded in `selectivity_cascade[]`.

4. **SPD assessment is a rule-based lookup.** Per BS 7671 §443 / IEC 60364-4-44 / NEC 285 / KS 1700 §443. Inputs: location type + supply type + life-safety presence. Verdict + type recorded in `system_metrics.spd_assessment`.

5. **System-wide metrics computed inline by LLM in v1.3.** `tool_call_pending_for_system_metrics: true` (WI3 deferral pattern). Refinement happens when calc.sld_system_metrics ships at runtime.

6. **Legacy 1245-line generator archived, not deleted.** Becomes `electrical/sld/docs/legacy-generator-v1.2-engineering-reference.md` for engineering content lookups.

## 4. IR schema — `electrical/sld/schemas/sld-ir.schema.json`

Full system-view IR. Key top-level fields:

```json
{
  "drawing_type": "single_line_diagram",
  "version": "1.3.0",
  "meta": {
    "project_id": "string",
    "skill_version": "sld/1.3.0",
    "produced_at": "ISO-8601",
    "consumed_intents": [
      // one entry per board in distribution_hierarchy
      { "intent_type": "db-layout", "intent_version": "1.0.0", "produced_by": "electrical/db-layout/v1.2.0" }
    ]
  },
  "jurisdiction": "GB | EU | INT | KE | US",
  "supply_origin": {
    "supplier": "string (DNO/utility name)",
    "wayleave_or_account_reference": "string",
    "system_type": "TN-S | TN-C-S | TT",
    "voltage_nominal_v": "integer (enum: 120, 208, 230, 240, 277, 400, 415, 480)",
    "voltage_arrangement": "single_phase | single_phase_split | TPN | TPN_plus_E",
    "frequency_hz": "integer (enum: 50, 60)",
    "ze_declared_ohm": "number",
    "pfc_declared_ka": "number",
    "main_switch_rating_a": "integer",
    "main_switch_breaking_capacity_ka": "number"
  },
  "distribution_hierarchy": [
    {
      "board_id": "string (e.g., MSB-MAIN)",
      "board_role": "main_switchboard | sub_distribution_board | panel | sub_panel | fire_alarm_panel | life_safety_panel | ups_distribution",
      "consumed_intent_path": "relative path to db-layout intent-out.json",
      "parent_board_id": "string | null (null = root)",
      "fed_via_circuit_id": "string | null (which upstream circuit/feeder feeds this board)",
      "location": "string",
      "enclosure_rating": "string (e.g., IP55)"
    }
  ],
  "selectivity_cascade": [
    {
      "parent_board_id": "string",
      "parent_circuit_id": "string",
      "child_board_id": "string",
      "verdict": "selective | partial_selective | non_selective",
      "verification_method": "manufacturer_table | iec_60898_typical | manual_review",
      "_note": "string (rationale or caveat)"
    }
  ],
  "system_metrics": {
    "imax_total_a": "number",
    "peak_pfc_ka": "number",
    "spd_assessment": {
      "required": "boolean",
      "spd_type": "Type 1 | Type 2 | Type 1+2 | Type 3 | not_required",
      "code_clause": "string (BS 7671:2018+A2 Reg 443 | IEC 60364-4-44 §443 | NEC 285 | KS 1700:2018 §443)",
      "location_basis": "string (urban / rural / coastal / industrial / etc.)"
    },
    "life_safety_isolation": {
      "fire_alarm_dedicated_supply": "boolean",
      "emergency_lighting_dedicated_supply": "boolean",
      "ups_essential_loads_kva": "number"
    },
    "tool_call_pending_for_system_metrics": "boolean (true in v1.3 until calc.sld_system_metrics ships)"
  },
  "compliance_summary": {
    "compliant": "boolean",
    "non_compliance_flags": "array of {message, code_clause, severity}",
    "assumptions": "array of strings"
  },
  "drawing_notes": "array of strings",
  "drawn_as_symbols": "array of IEC 60617 symbol_ids (pattern ^[A-Z][A-Z0-9_]*$)",
  "flags": "array of strings (incl. TOOL-CALL-PENDING string per WI3)",
  "rationale": "$ref → shared/schemas/core/rationale.schema.json"
}
```

## 5. Intent schema — `electrical/sld/schemas/sld-intent.schema.json`

Slim subset for downstream consumers (future: riser, cable-containment, maintenance docs, panel-schedule rollup):

```json
{
  "intent_type": "sld",
  "intent_version": "1.0.0",
  "produced_by_skill_version": "sld/1.3.0",
  "project_id": "string",
  "jurisdiction": "string",
  "supply_summary": {
    "system_type": "TN-S | TN-C-S | TT",
    "voltage_arrangement": "string",
    "main_switch_rating_a": "integer"
  },
  "board_count": "integer",
  "msb_board_id": "string",
  "boards": [
    { "board_id": "string", "role": "string", "consumed_db_layout_intent": "relative path | null" }
  ],
  "spd_assessment_verdict": "required_type_1_2 | required_type_2 | required_type_3 | not_required",
  "selectivity_overall_verdict": "fully_selective | partially_selective | non_selective",
  "compliant": "boolean",
  "produced_at": "ISO-8601"
}
```

## 6. 12 new db-layout companion examples

Each is a standard 5-file example. No schema changes to db-layout.

### A. UK SLD scenario (4 new — full set; no reuse of uk-domestic-cu)

| Path | Board ID | Role | Notes |
|---|---|---|---|
| `electrical/db-layout/examples/uk-commercial-msb-3storey/` | MSB-MAIN | rollup | TN-C-S 400V 400A intake; 3 feeders (F01/F02/F03) |
| `electrical/db-layout/examples/uk-commercial-sdb-gf/` | SDB-GF | single-board | 100A TPN; ~12 final circuits |
| `electrical/db-layout/examples/uk-commercial-sdb-l1/` | SDB-L1 | single-board | 100A TPN; ~12 circuits |
| `electrical/db-layout/examples/uk-commercial-sdb-l2/` | SDB-L2 | single-board | 100A TPN; ~12 circuits |

### B. KE SLD scenario (1 new — leverages existing MSP-100)

| Path | Board ID | Role | Notes |
|---|---|---|---|
| `electrical/db-layout/examples/ke-nairobi-industrial-100A-tpn/` (existing v1.1) | MSP-100 | main board (8 circuits) | Reused as-is; C08 is the only feeder to a sub-DB |
| `electrical/db-layout/examples/ke-nairobi-gh-db/` (NEW) | GH-DB | single-board | Gate-house sub-DB fed by MSP-100 C08 (60m submain); 3-4 circuits |

### C. INT SLD scenario (4 new — leverages existing INT MSB rollup)

| Path | Board ID | Role | Fed from |
|---|---|---|---|
| `electrical/db-layout/examples/intl-commercial-tpn-msb/` (existing v1.1) | MSB-MAIN | rollup, 4 feeders | — |
| `electrical/db-layout/examples/intl-dbl1-lighting/` | DB-L1 | single-board | MSB-MAIN F01 (250A) |
| `electrical/db-layout/examples/intl-dbp1-power/` | DB-P1 | single-board | MSB-MAIN F02 (400A) |
| `electrical/db-layout/examples/intl-dbm1-mechanical/` | DB-M1 | single-board | MSB-MAIN F03 (250A) |
| `electrical/db-layout/examples/intl-dbfa1-fire-alarm/` | DB-FA1 | fire_alarm_panel | MSB-MAIN F04 (63A) |

### D. US SLD scenario (3 new — leverages existing US main panel)

| Path | Board ID | Role |
|---|---|---|
| `electrical/db-layout/examples/us-strip-mall-panelboard/` (existing v1.1) | MSP-A | main service panelboard |
| `electrical/db-layout/examples/us-strip-mall-tsp-a/` | TSP-A | tenant sub-panel A (Suite 100 retail) |
| `electrical/db-layout/examples/us-strip-mall-tsp-b/` | TSP-B | tenant sub-panel B (Suite 200 retail) |
| `electrical/db-layout/examples/us-strip-mall-common-area/` | CA-P | common area + exterior lighting panel |

**Total new db-layout examples: 4 + 1 + 4 + 3 = 12 × 5 files = 60 new db-layout files.**

## 7. 4 SLD worked examples

Each lives at `electrical/sld/examples/<scenario>/` with 5 files (input.json + output.json + intent-out.json + reasoning.md + sample-schedule.md).

### Example 1 — UK 3-storey commercial office

Path: `electrical/sld/examples/uk-commercial-office-3storey/`

```
DNO TN-C-S 400V (Ze=0.35Ω, PFC=9.8kA)
  └── MSB-MAIN (400A intake)
        ├── SDB-GF (fed via MSB F01)
        ├── SDB-L1 (fed via MSB F02)
        └── SDB-L2 (fed via MSB F03)
```

4 consumed intents (one per board). Demonstrates 4-board cascade.

### Example 2 — KE Nairobi industrial light-engineering complex

Path: `electrical/sld/examples/ke-nairobi-industrial-msb-gh/`

```
KPLC TN-S 415V (Ze=0.80Ω, PFC=9.8kA — wayleave KPLC-NRB-IND-2143)
  └── MSP-100 (100A TPN)
        └── GH-DB (fed via MSP-100 C08, 60m submain)
```

2 consumed intents. Smaller cascade demonstrating scale flexibility. KS 1700 jurisdiction routing (citation form `"KS 1700:2018 §X.Y.Z"` per earthing v1.2 precedent).

### Example 3 — INT commercial TPN MSB

Path: `electrical/sld/examples/intl-commercial-msb-4subdbs/`

```
Utility TN-C-S 400V (Ze=0.30Ω, PFC=16kA)
  └── MSB-MAIN (800A intake)
        ├── DB-L1 (Lighting, fed via F01 250A)
        ├── DB-P1 (Power, fed via F02 400A)
        ├── DB-M1 (Mechanical, fed via F03 250A)
        └── DB-FA1 (Fire Alarm, fed via F04 63A — life-safety)
```

5 consumed intents. Demonstrates 5-board cascade + life-safety isolation pattern (DB-FA1 dedicated supply, no upstream RCD per IEC 60364-5-56).

### Example 4 — US strip mall with tenant sub-panels

Path: `electrical/sld/examples/us-strip-mall-msp-tenants/`

```
Utility TN-S 208Y/120V (Ze=0.10Ω, PFC=22kA)
  └── MSP-A (200A main service panelboard)
        ├── TSP-A (Suite 100 tenant)
        ├── TSP-B (Suite 200 tenant)
        └── CA-P (common area + exterior)
```

4 consumed intents. NEC convention throughout (AWG cables, NEC 250.122 EGC sizing references). Citations `"NEC 2023 Article XXX.X"`.

### Common cross-cutting in every SLD example output.json

- `meta.consumed_intents[]` with N+1 entries (one per board)
- `meta.skill_version: "sld/1.3.0"`
- Full `distribution_hierarchy[]` per cascade structure
- `selectivity_cascade[]` with N verdicts (one per parent→child link)
- `system_metrics` with imax + peak_pfc + spd_assessment + life_safety_isolation + `tool_call_pending_for_system_metrics: true`
- `rationale.sections[]` covering supply origin, hierarchy + topology, cascade selectivity, SPD assessment, life-safety isolation, compliance, assumptions (per WI2)
- `flags: ["TOOL-CALL-PENDING:sld_system_metrics — System metrics are LLM-estimates; deterministic refinement deferred per WI3."]`

## 8. SLD infrastructure rebuild (~30 files)

### Manifest (rewrite)

```json
{
  "skill": "sld",
  "version": "1.3.0",
  "discipline": "electrical",
  "subdiscipline": "distribution",
  "status": "beta",
  "description": "LV single line diagram — system-wide distribution from supply origin through MSB to sub-boards. Consumes db-layout intents for each board in the cascade. Computes Imax/PFC/SPD/life-safety system metrics. Verifies cascade selectivity.",
  "produces_intent": "sld",
  "produces_intent_schema": "electrical/sld/schemas/sld-intent.schema.json",
  "consumes_intents": ["db-layout"],
  "standards": [
    "shared/standards/electrical/BS7671/", "shared/standards/electrical/IEC60364/",
    "shared/standards/electrical/IEC61439/", "shared/standards/electrical/IEC60617/",
    "shared/standards/electrical/NFPA70/", "shared/standards/electrical/KS1700/"
  ],
  "ontology": ["board-roles.json", "distribution-types.json"],
  "rules": ["distribution-hierarchy.yaml", "device-selection.yaml", "spd-policy.yaml", "life-safety-isolation.yaml"],
  "constraints": ["selectivity-cascade.yaml", "intake-capacity.yaml", "intent-shape.yaml"],
  "validators": ["ir-integrity.yaml", "jurisdiction-routing.yaml", "tool-deferral-shape.yaml"],
  "prompts": { "generator": "...", "validator": "...", "reviewer": "..." },
  "evals": [
    "eval-01-uk-3storey-happy-path.yaml", "eval-02-ke-msp-gh-cascade.yaml",
    "eval-03-intake-undersized-trap.yaml", "eval-04-missing-spd-assessment.yaml",
    "eval-05-non-selective-cascade.yaml", "eval-06-rationale-block.yaml",
    "eval-07-multi-board-intent-consumption.yaml"
  ],
  "examples": [
    "examples/uk-commercial-office-3storey/", "examples/ke-nairobi-industrial-msb-gh/",
    "examples/intl-commercial-msb-4subdbs/", "examples/us-strip-mall-msp-tenants/"
  ]
}
```

### Generator prompt — 12 steps

(Per Design § 5 above.)

### Validator prompt — 10 INV checks

(Per Design § 5 above.)

### Reviewer prompt — 6 D checks

(Per Design § 5 above.)

### Rules (4 YAMLs)

- `rules/distribution-hierarchy.yaml` — board_role enum + cardinality
- `rules/device-selection.yaml` — breaker type per load profile + jurisdiction
- `rules/spd-policy.yaml` — SPD lookup per jurisdiction
- `rules/life-safety-isolation.yaml` — life-safety circuit isolation per jurisdiction

### Constraints (3 YAMLs, 8 checks)

- `constraints/selectivity-cascade.yaml` (3 checks)
- `constraints/intake-capacity.yaml` (2 checks)
- `constraints/intent-shape.yaml` (3 checks)

### Validation (3 YAMLs, 9 checks)

- `validation/ir-integrity.yaml` (3 checks)
- `validation/jurisdiction-routing.yaml` (3 checks)
- `validation/tool-deferral-shape.yaml` (3 checks)

### Ontology (2 JSONs)

- `ontology/board-roles.json` — 7 role enum
- `ontology/distribution-types.json` — radial/ring/split-phase topology semantics

### Docs (3 files)

- `docs/engineering-philosophy.md` — design principles + scope boundaries
- `docs/known-limitations.md` — what v1.3 does NOT cover
- `docs/legacy-generator-v1.2-engineering-reference.md` — the archived 1245-line legacy generator

### Other infra

- `inputs.json` — full discovery questions per WI1 (project metadata, supply data, hierarchy intent, board paths)
- `README.md` — full rewrite (currently stub-flagged)
- `CHANGELOG.md` — v1.3.0 entry (Added + Changed + Notes)

## 9. Bookkeeping

| File | Change |
|---|---|
| `electrical/db-layout/skill.manifest.json` | Version 1.1.0 → 1.2.0; `examples` array gains 12 new entries |
| `electrical/db-layout/CHANGELOG.md` | v1.2.0 entry covering 12 new companion examples |
| `electrical/sld/skill.manifest.json` | Full rewrite (per §8) |
| `electrical/sld/CHANGELOG.md` | v1.3.0 entry (rebuild) |
| `electrical/sld/README.md` | Full rewrite |
| `SKILLS_STATUS.md` | sld row v1.2.0 → v1.3.0 (production → beta during rebuild → production after eval-09); db-layout row v1.1.0 → v1.2.0 |
| `ARCHITECTURE.md` | Cross-drawing intents §"Worked example pattern" subsection gains SLD multi-board sub-section (generalization of earthing's single-board pattern) |

## 10. Sequencing

Single unified sprint with ~30 tasks (subagent-driven-development model). Recommended task order:

**Phase A — db-layout v1.2 cascade examples (Tasks 1-13)**
1. UK: 4 db-layout examples (Tasks 1-4)
2. KE: 1 db-layout example (Task 5)
3. INT: 4 db-layout examples (Tasks 6-9)
4. US: 3 db-layout examples (Tasks 10-12)
5. db-layout v1.2.0 manifest + CHANGELOG (Task 13)

**Phase B — SLD infrastructure (Tasks 14-20)**
14. Archive legacy generator + rewrite README
15. SLD manifest + inputs.json
16. SLD schemas (IR + intent)
17. SLD generator prompt (12 steps)
18. SLD validator prompt (10 INVs) + reviewer prompt (6 Ds)
19. SLD rules + constraints + validation YAMLs (10 files)
20. SLD ontology + docs (5 files)

**Phase C — SLD worked examples (Tasks 21-24)**
21. UK 3-storey office SLD example (5 files)
22. KE Nairobi industrial MSP-GH SLD example (5 files)
23. INT commercial MSB 4-subDBs SLD example (5 files)
24. US strip mall MSP-tenants SLD example (5 files)

**Phase D — Evals + final integration (Tasks 25-30)**
25. Evals 1-3 (happy_path × 2 + validation_trap)
26. Evals 4-5 (validation_trap + edge_case)
27. Evals 6-7 (rationale_block + skill_specific WI4)
28. SLD CHANGELOG + SKILLS_STATUS rows + ARCHITECTURE.md
29. Cross-cutting validation script + spec compliance review
30. Final code review + push

## 11. Acceptance criteria

- [ ] 12 new db-layout companion examples exist, each with 5 files (input/output/intent-out/reasoning/sample-schedule)
- [ ] Each new db-layout intent-out.json validates against `db-layout-intent.schema.json`
- [ ] db-layout v1.2.0 manifest + CHANGELOG updated
- [ ] SLD legacy generator archived at `docs/legacy-generator-v1.2-engineering-reference.md`
- [ ] SLD v1.3.0 manifest rewrite with full produces_intent + consumes_intents + 3 prompts + 4 rules + 3 constraints + 3 validators + 7 evals + 4 examples
- [ ] SLD IR + intent schemas exist + validate the 4 worked examples
- [ ] 4 SLD example output.json files each carry meta.consumed_intents[] with N+1 entries (one per board)
- [ ] Every SLD distribution_hierarchy node has a consumed_intent_path that resolves to a real file
- [ ] selectivity_cascade[] populated for every parent→child link in each example
- [ ] system_metrics.spd_assessment present + jurisdiction-appropriate
- [ ] tool_call_pending_for_system_metrics flag + TOOL-CALL-PENDING in flags[]
- [ ] 7 evals + corresponding YAML files
- [ ] SKILLS_STATUS rows updated for both skills
- [ ] ARCHITECTURE.md gains SLD multi-board subsection
- [ ] Final code review verdict APPROVE

## 12. Risks + mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| 116-file sprint is largest in project history; coordination complexity | Medium | Subagent-driven-development with ~30 tasks; per-phase batching; final review catches cross-task drift |
| 12 new db-layout examples + 4 SLD examples need consistent supply context | Medium | Per-jurisdiction sub-batches (UK/KE/INT/US) keep supply context grouped; engineering parameters propagate within each batch |
| INT MSB-MAIN existing rollup-scope assumes 4 specific feeders (F01-F04); new sub-DBs must align with those feeders' breaker ratings + cable CSAs | Low | Implementer reads existing INT intent-out.json before authoring sub-DBs; eval-07 catches misalignment |
| Cascade selectivity is engineering judgement, not pure calculation; LLM may hallucinate verdicts | Medium | INV-7 enforces cascade size = N-1; reviewer D3 cross-checks verdicts against manufacturer typical curves; selectivity_cascade entries carry verification_method to flag manual_review cases |
| Legacy generator content drift — moving to docs/ may break links | Low | Archive path documented in README + CHANGELOG; old prompts/generator.md path absent triggers new generator routing |

## 13. Out-of-scope clarification (for plan agent)

Do NOT introduce:
- Drawing layout positions (Stage 2 — separate sprint)
- New calc contracts (no calc.sld_system_metrics implementation; only contract deferral via WI3 pattern)
- Schema changes to db-layout (db-layout intent schema unchanged; only new examples)
- Consumption of earthing/fault-level intents (future v1.4+)
- Renderer code (runtime concern)
- Other skills' refresh to consume sld intent (separate per-skill sprints)

## 14. Pattern parents

- **earthing v1.3** (shipped 2026-05-18) — single-board WI4 consumption; SLD generalizes to multi-board cascades
- **arc-flash-labelling** (shipped 2026-05-17) — multi-standards-layer + 73-file sprint scale precedent
- **db-layout v1.1** (shipped 2026-05-18) — intent-out.json schema + 4-example pattern (extended to 16 examples this sprint)
- **cable-sizing + fault-level + arc-flash + earthing** — proven 12-step generator + INV-validator + D-reviewer + per-example folder + WI3 tool deferral pattern
