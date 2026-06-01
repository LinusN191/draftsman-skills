# special-locations v1.0.0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `electrical/special-locations/` v1.0.0 production — a calc-primitive companion skill that auto-derives BS 7671:2018+A2:2022 Part 7 zones (§701/§702/§703/§710/§715) + electrical constraints from upstream architectural-extracted anchor fixtures, produces a single flat intent (`special_locations_zoning`) with a 14-value `zone_type` discriminator + 6-value `constraint_type` discriminator, and wires that intent into three downstream consumers (`lighting-layout` v1.6, `small-power` v1.2 cascade-wiring, `db-layout` v1.5) so engineers cannot ship a Part-7-affected drawing without per-zone fixture-placement verification.

**Architecture:** Calc-primitive companion (same role class as `photometric-analysis` shipped 2026-05-30). Skill emits IR + intent; does NOT produce a primary drawing. Auto-zone-derivation from `anchor_fixtures[]` input (sourced by runtime from architectural-drawing extraction; `_extraction_source` provenance carried per anchor). Single flat intent with `zone_type` discriminator means one cascade contract per consumer + additive growth for v1.1+ sections. Three consumer skills get version bumps + new cascade-INV (INV-12 / INV-12 / INV-16). Sprint shape mirrors photometric (4 phases × per-task two-stage Opus review + pre-ship Sonnet 11-check fence + final Opus integration review), expanded for triple cascade.

**Tech Stack:**
- JSON Schema Draft 2020-12 for IR + intent contracts
- YAML for evals + rules + manifests
- Markdown for prompts + README + CHANGELOG
- Python stdlib (3.10+) for the `shared/special-locations/zone-derivation/` reference library — geometry computation; no third-party deps (matches `[[runtime-project-boundary]]`)
- Existing golden CI gate (`scripts/validate-examples.py` 3-pass: IR/eval/inputs validation)
- Existing `functional_audit.py` reasoning oracle

**Source spec:** [`docs/superpowers/specs/2026-06-01-special-locations-design.md`](../specs/2026-06-01-special-locations-design.md) v1.0.1 (commit `7e4d34a`).
**Pattern parent:** [`docs/superpowers/plans/2026-05-30-photometric-analysis-sprint.md`](2026-05-30-photometric-analysis-sprint.md) (25-commit clean ship 2026-05-30).
**Verified Part 7 standards:** [`shared/standards/electrical/BS7671/part7-special-locations.json`](../../../shared/standards/electrical/BS7671/part7-special-locations.json) (verification_status: `verified-against-source`).

---

## Sprint discipline (locked, mirrors photometric)

- Sonnet for mechanical (scaffolding, schemas, manifests, eval YAML, cascade wiring) per `[[feedback-no-haiku-sonnet-opus-only]]`
- Opus for judgment (geometry library, generator/validator/reviewer prompts, all examples, retrofits, all reviews)
- **Two-stage Opus review after every implementer task** (spec-compliance + code-quality combined). Fix-pass commit when HIGH/CRITICAL findings surface. `[[sprint-D3-shipped]]` history: 10/11 D3 implementer tasks needed fix-passes — budget for ~6 fix-pass commits.
- **Cross-check every citation against `shared/standards/electrical/BS7671/part7-special-locations.json` BEFORE the implementer reads the task.** Verified-citation table is in design spec §3.2; banned-citation list also there. Same lesson from `[[sprint-D2-shipped]]` Reg 559 + photometric §714 catches — caught upstream this time.
- Pre-ship **Sonnet 11-check verification fence** (D.6 step 1)
- Final cross-sprint Opus integration review before push
- Push deferred to user authorisation per CLAUDE.md "shared state" rule
- `[[feedback-no-trim-non-consequential]]` — `invariants[].evidence` schema declares `maxLength: 1200` from v1.0 (declared upfront in A.2 task) so failure-mode INV-08 evidence doesn't trigger the photometric-style retrofit
- No-§714 / no-banned-citation discipline: any implementer commit citing a banned clause from spec §3.2 gets a CRITICAL finding in review and a mandatory fix-pass

### Estimated commit count: 23-25

- 16 implementer commits (4 + 3 + 3 + 6)
- ~6 fix-pass commits (10/11 D3 pattern)
- 1 final ship commit (D.6 + push)
- 4 portion commits for this plan doc

---

## File structure

### Created (new skill directory)

```
electrical/special-locations/
├── README.md                          # 90+ lines; standards xref table; identity + cascade contract + honest disclosures
├── CHANGELOG.md                       # [1.0.0] 2026-06-01 — production release entry
├── skill.manifest.json                # production status; 5+ standards; 1 produces_intents; 1 consumes_intents (lighting-layout); 17 examples registered
├── inputs.json                        # 7 WI1 input items per shared/schemas/core/inputs.schema.json
├── schemas/
│   ├── special-locations-ir.schema.json            # 10 top-level properties; 14-value zone_type discriminator; 6-value constraint_type discriminator; mode-conditional allOf; invariants[].evidence maxLength=1200
│   └── special-locations-zoning-intent.schema.json # FLAT shape; payload mirrors IR exportable subset
├── prompts/
│   ├── generator.md                   # ~280 lines; Step 0 cascade-prereq + 12 numbered steps
│   ├── validator.md                   # ~310 lines; 10 INVs (INV-01..INV-10) with verified-citation rule + action + rationale
│   └── reviewer.md                    # ~180 lines; 5 D-checks
├── evals/
│   ├── eval-01-anchor-zone-integrity.yaml          # INV-01 + INV-10 self-consistency
│   ├── eval-02-drift-guard.yaml                    # INV-02 audit↔flags drift
│   ├── eval-03-medical-it-required.yaml            # INV-03 (validation_trap category)
│   ├── eval-04-fixture-violation-failure.yaml      # INV-08 (compliance_failure — central engineering eval)
│   ├── eval-05-provenance-disclosure.yaml          # INV-09 (skill_specific)
│   ├── eval-06-pool-main-bonding.yaml              # INV-05 (validation_trap)
│   └── eval-07-elv-separation.yaml                 # INV-07 (skill_specific)
├── rules/
│   ├── zone-derivation-rules.yaml                  # per-section geometry rules (bath / pool / sauna / medical / ELV)
│   ├── constraint-required-by-context-rules.yaml   # INV-03..07 mapping table
│   └── provenance-disclosure-rules.yaml            # _extraction_source 3-tier enum + INV-09 thresholds
└── examples/
    ├── uk-bathroom-standard-bath-and-shower/       # 4 files: input.json + output.json + reasoning.md + intent-out.json
    ├── uk-bathroom-whirlpool-with-pump/
    ├── uk-shower-room-wet-room-floor/
    ├── uk-pool-hall-with-changing-room-adjacency/
    ├── uk-sauna-with-3-zone-derivation/
    ├── uk-medical-or-group-2-with-it-system/
    ├── uk-medical-ward-group-1-bonding/
    ├── uk-external-landscape-elv-lighting/
    ├── cascade-lighting-layout-uk-bathroom/
    ├── cascade-lighting-layout-uk-pool-hall/
    ├── cascade-lighting-layout-uk-medical-group-2/
    ├── cascade-small-power-uk-bathroom-violation/             # FAIL HIGH
    ├── cascade-small-power-uk-medical-group-2-isolation/
    ├── cascade-small-power-uk-external-elv-with-violation/    # FAIL HIGH
    ├── cascade-db-layout-uk-bathroom-rcd-enforcement/
    ├── cascade-db-layout-uk-medical-group-2-it-distribution/
    └── cascade-multi-jurisdiction-ke-bathroom-route-to-bs/    # KE jurisdiction
```

### Created (shared library)

```
shared/special-locations/
├── README.md                          # geometry library purpose + verification status policy
└── zone-derivation/
    ├── __init__.py                    # module-level docstring + version
    ├── common.py                      # cylinder→polygon approximation (≥12 sides) + polygon union/intersection
    ├── bath.py                        # §701 zones (Zone 0 basin + Zone 1 above + Zone 2 horizontal 0.6m extension; wet-room expansion; whirlpool pump local-isolation)
    ├── pool.py                        # §702 zones (Zone 0 basin + Zone 1 above + Zone 2 horizontal 2m extension to 1.5m above water; changing-room adjacency check)
    ├── sauna.py                       # §703 3-zone (Zone 1 around heater + Zone 2 sauna body + Zone 3 above 1.5m)
    ├── medical.py                     # §710 envelope (1.5m radius cylinder around patient_position by group; Group 2 mandates IT-system constraint)
    └── elv.py                         # §715 barrier zone (cable spacing + barrier rules; transformer location)
```

### Modified (cascade consumers)

```
electrical/lighting-layout/
├── skill.manifest.json                # 1.5.0 → 1.6.0; consumes_intents[] adds special-locations entry
├── prompts/validator.md               # append INV-12 (after INV-11)
├── CHANGELOG.md                       # add [1.6.0] entry
└── examples/                          # retrofit ~5-7 Part-7-affected examples: input.json + output.json + intent-out.json

electrical/small-power/
├── skill.manifest.json                # 1.1.0 → 1.2.0; consumes_intents[] adds special-locations entry
├── prompts/validator.md               # append INV-12 (after INV-11)
├── CHANGELOG.md                       # add [1.2.0] entry — cascade-wiring scope only; D4 depth in Wave 2
└── examples/                          # retrofit ~5-7 examples

electrical/db-layout/
├── skill.manifest.json                # 1.4.0 → 1.5.0; consumes_intents[] adds special-locations entry
├── prompts/validator.md               # append INV-16 (after INV-15)
├── CHANGELOG.md                       # add [1.5.0] entry
└── examples/                          # retrofit ~3-4 examples

shared/schemas/electrical/
├── lighting-layout-ir.schema.json     # add consumed_intents.special_locations_zoning + 3rd allOf clause (1st = D3.A.3 mode; 2nd = photometric; 3rd = special-locations)
├── small-power-ir.schema.json         # add consumed_intents.special_locations_zoning + allOf clause
└── db-layout-ir.schema.json           # add consumed_intents.special_locations_zoning + allOf clause

electrical/lighting-layout/schemas/lighting-layout-intent.schema.json   # permissive consumed_intents block (D.2 photometric lesson — mirror pass)
electrical/small-power/schemas/small-power-intent.schema.json           # same shape
electrical/db-layout/schemas/db-layout-intent.schema.json               # same shape
```

### Memory artifacts

```
~/.claude/projects/-Users-linus-Desktop-DraftsMan-SKills-draftsman-skills/memory/
├── MEMORY.md                          # append [special-locations shipped] index entry (line under [photometric-analysis shipped])
└── special-locations-shipped.md       # NEW; full sprint summary per [[photometric-analysis-shipped]] pattern
```

---

## Phase A — Foundations (4 tasks, sequential)

Phase A produces the scaffolding + schemas + inputs + the shared zone-derivation library. Each task ships as one implementer commit; per-task two-stage Opus review may add a fix-pass commit. Phase A complete after A.4 ships green.

---

## Task A.1: Skill scaffolding — manifest + README + CHANGELOG (Sonnet)

**Why Sonnet:** Mechanical scaffolding (manifest + README + CHANGELOG) per the photometric A.2 precedent.

**Files:**
- Create: `electrical/special-locations/skill.manifest.json`
- Create: `electrical/special-locations/README.md`
- Create: `electrical/special-locations/CHANGELOG.md`
- Create: `electrical/special-locations/` directory (with empty subdirs ready for A.2/A.3/A.4 contents)

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p electrical/special-locations/{schemas,prompts,evals,rules,examples}
mkdir -p shared/special-locations/zone-derivation
```

- [ ] **Step 2: Write `skill.manifest.json`**

```json
{
  "id": "special-locations",
  "name": "Special Locations (BS 7671 Part 7)",
  "version": "1.0.0",
  "status": "production",
  "discipline": "electrical",
  "subdiscipline": "compliance",
  "description": "Auto-derives BS 7671:2018+A2:2022 Part 7 zoning + electrical constraints from upstream architectural-extracted anchor fixtures. Covers §701 (baths/showers), §702 (swimming pools), §703 (saunas), §710 (medical Groups 0/1/2 + IT system), §715 (extra-low voltage lighting). Calc-primitive companion skill: emits intent + IR; does NOT produce a primary drawing. Three downstream cascade consumers (lighting-layout v1.6, small-power v1.2, db-layout v1.5) enforce per-zone fixture-placement compliance.",
  "standards": [
    {"id": "BS 7671:2018+A2:2022", "scope": "Part 7 §701 + §702 + §703 + §710 + §715", "ref": "shared/standards/electrical/BS7671/part7-special-locations.json"},
    {"id": "IEC 60364-7-XXX", "scope": "INT jurisdiction parallel parts (citation routing only at v1.0; full INT examples deferred to v1.1)"},
    {"id": "KS 1700:2018", "scope": "KE jurisdiction §313 route to BS 7671 Part 7"},
    {"id": "HTM 06-01", "scope": "NHS technical memorandum — medical electrical services; takes precedence in NHS sites for §710 safety service categories"},
    {"id": "BS EN 60601 series", "scope": "Medical electrical equipment safety (cross-reference for §710)"},
    {"id": "BS EN 61557-8", "scope": "Insulation Monitoring Devices (IMD) for medical IT systems — 8 s alarm response time"},
    {"id": "BS EN 61558-2-6", "scope": "Transformer short-circuit protection for §715 ELV lighting"},
    {"id": "BS 5266-1", "scope": "Emergency lighting in medical locations (cross-reference)"}
  ],
  "produces_intents": [
    {"intent_name": "special-locations-zoning", "version": "1.0.0", "schema_ref": "schemas/special-locations-zoning-intent.schema.json"}
  ],
  "consumes_intents": [
    {"skill_id": "lighting-layout", "intent_name": "lighting-layout", "version_constraint": "^1.5", "trigger": "room.room_type IN ['bathroom', 'shower_room', 'swimming_pool_hall', 'sauna', 'medical_group_0_area', 'medical_group_1_ward', 'medical_group_2_theatre', 'external_landscape']", "consumed_fields": ["luminaires", "switches", "sockets", "room"]}
  ],
  "examples": [
    "examples/uk-bathroom-standard-bath-and-shower",
    "examples/uk-bathroom-whirlpool-with-pump",
    "examples/uk-shower-room-wet-room-floor",
    "examples/uk-pool-hall-with-changing-room-adjacency",
    "examples/uk-sauna-with-3-zone-derivation",
    "examples/uk-medical-or-group-2-with-it-system",
    "examples/uk-medical-ward-group-1-bonding",
    "examples/uk-external-landscape-elv-lighting",
    "examples/cascade-lighting-layout-uk-bathroom",
    "examples/cascade-lighting-layout-uk-pool-hall",
    "examples/cascade-lighting-layout-uk-medical-group-2",
    "examples/cascade-small-power-uk-bathroom-violation",
    "examples/cascade-small-power-uk-medical-group-2-isolation",
    "examples/cascade-small-power-uk-external-elv-with-violation",
    "examples/cascade-db-layout-uk-bathroom-rcd-enforcement",
    "examples/cascade-db-layout-uk-medical-group-2-it-distribution",
    "examples/cascade-multi-jurisdiction-ke-bathroom-route-to-bs"
  ],
  "prompts": {
    "generator": "prompts/generator.md",
    "validator": "prompts/validator.md",
    "reviewer": "prompts/reviewer.md"
  },
  "ontology": [],
  "_ontology_note": "v1.0 has no ontology library — zone derivation is parametric from anchor geometry, not lookup-table-based. Future v1.1+ may add a fixture-IP-classification ontology if engineer demand surfaces.",
  "_v1_limitations": [
    "MRI rooms NOT in scope (IEC 60601-1 + Faraday cage specs different stack — separate sibling skill when first MRI project)",
    "US NEC parallel NOT in scope (Article 680 / 517 — separate sibling skill electrical/special-locations-us/ when first US project)",
    "§722 EV charging NOT in scope (intersects with EV-Charge skill; defer until that skill matures)",
    "Embedded heating (former §753) NOT in scope (no §753 in BS 7671:2018+A2:2022; v1.1 candidate via §415 + §522 routing)",
    "INT jurisdiction worked examples NOT in scope at v1.0 (citation routing supported via _clause_citation; full examples in v1.1)"
  ]
}
```

- [ ] **Step 3: Write `README.md`** — Minimum 90 lines, real engineering body (not stub). Cover: identity + scope + cascade contract + inputs + outputs + 10 INVs + 5 D-checks + standards cross-reference table + honest disclosures + why this skill exists.

The README should mirror photometric-analysis's shape but be specific to special-locations. Standards cross-reference table must use verified-only citations per spec §3.2.

Include this exact standards cross-reference table:

```markdown
## Standards cross-reference

| Citation | Section | Used for |
|---|---|---|
| BS 7671:2018+A2:2022 §701 | §701 | Generic bathroom/shower-room scope |
| BS 7671:2018+A2:2022 §701.411.3.3 | §701 | 30 mA RCD blanket (INV-04) |
| BS 7671:2018+A2:2022 §701.414.4.5 | §701 | SELV ≤12 V in Zone 0 |
| BS 7671:2018+A2:2022 §701.415.2 | §701 | Supplementary equipotential bonding |
| BS 7671:2018+A2:2022 §701.512.2 | §701 | IPx5 where water jets used (drives whirlpool IPx5 — INV-06) |
| BS 7671:2018+A2:2022 §701.512.3 | §701 | Socket outlet ≥3 m from Zone 1 boundary |
| BS 7671:2018+A2:2022 §702 | §702 | Generic swimming-pool scope |
| BS 7671:2018+A2:2022 §702.415.1 | §702 | Main equipotential bonding (INV-05; NOT §702.55.1) |
| BS 7671:2018+A2:2022 §702.415.2 | §702 | Pool supplementary bonding |
| BS 7671:2018+A2:2022 §702.55.4 | §702 | Zone 2 changing-room overlap (D-2) |
| BS 7671:2018+A2:2022 §703 | §703 | Generic sauna scope (3-zone split) |
| BS 7671:2018+A2:2022 §703.411.3.3 | §703 | RCD blanket (heater exempt) |
| BS 7671:2018+A2:2022 §710 | §710 | Generic medical scope (Groups 0/1/2) |
| BS 7671:2018+A2:2022 §715 | §715 | Generic ELV lighting scope |
| HTM 06-01 | cross-ref | NHS technical memorandum (medical safety service categories — §710) |
| BS EN 60601 series | cross-ref | Medical equipment safety |
| BS EN 61557-8 | cross-ref | IMD spec — 8 s alarm response (§710 Group 2 — INV-03) |
| BS EN 61558-2-6 | cross-ref | ELV transformer short-circuit protection (§715 — INV-07) |
| BS 5266-1 | cross-ref | Emergency lighting in medical locations |
| BS 5489-1 | cross-ref | External area lighting (not Part 7; routes via §522 IP) |
```

Add explicit "Banned citations — do NOT use" footer listing the 14 invented sub-clauses from spec §3.2 banned-list.

- [ ] **Step 4: Write `CHANGELOG.md`** — Single `[1.0.0] - 2026-06-01 — Initial production release` entry. Body lists Phase A/B/C/D scope; mirrors photometric CHANGELOG shape.

- [ ] **Step 5: Run gates (A.1 should not regress baseline)**

```bash
python3 scripts/validate-examples.py 2>&1 | tail -3
python3 functional_audit.py 2>&1 | tail -3
```

Expected: baseline unchanged (skill has no examples yet — manifest registered but examples not built).

- [ ] **Step 6: Commit A.1**

```bash
git add electrical/special-locations/skill.manifest.json electrical/special-locations/README.md electrical/special-locations/CHANGELOG.md
git commit -m "$(cat <<'EOF'
feat(special-locations): A.1 skill scaffolding — manifest + README + CHANGELOG (v0.0.0 → v1.0.0 production)

First task of special-locations v1.0 sprint. Phase A foundations —
first of four. Wave 1 second deliverable of the lighting skill family
roadmap (parallel with photometric-analysis shipped 2026-05-30).

Identity:
- Path: electrical/special-locations/
- Version: 1.0.0 production (NEW skill, no prior stub)
- Role: calc-primitive companion (same class as photometric-analysis)
- Discipline: electrical / compliance subdiscipline

Standards: 8 entries covering BS 7671 Part 7 §701/§702/§703/§710/§715
+ HTM 06-01 NHS technical memorandum + BS EN 60601/61557-8/61558-2-6
+ BS 5266-1 — all verified against shared/standards/electrical/BS7671/
part7-special-locations.json (verification_status: verified-against-source).

Intent declarations:
- produces: special-locations-zoning v1.0.0
- consumes: lighting-layout v^1.5 (when room.type ∈ Part-7 set)

17 examples registered (8 standalone + 9 cascade per spec §9).

_v1_limitations explicitly declared: MRI / NEC / §722 / embedded-heating /
INT full examples all deferred. Honest disclosure end-to-end.

README ≥90 lines with full standards cross-reference table (verified
citations only) + banned-citations footer (14 invented sub-clauses
caught at spec §3.2 brainstorm).

Next: A.2 IR + intent schemas.
EOF
)"
```

---

## Task A.2: IR + intent schemas (Sonnet)

**Why Sonnet:** Mechanical schema authoring per the photometric A.3 precedent. Discriminator branches + mode-conditional `allOf` are structural — no engineering judgment needed.

**Files:**
- Create: `electrical/special-locations/schemas/special-locations-ir.schema.json`
- Create: `electrical/special-locations/schemas/special-locations-zoning-intent.schema.json`

- [ ] **Step 1: Read the spec §5 + §6 sections to ground in shape**

```bash
sed -n '/^## 5\. IR shape/,/^## 6\. Produced intent/p' docs/superpowers/specs/2026-06-01-special-locations-design.md | head -200
sed -n '/^## 6\. Produced intent/,/^## 7\. Validator/p' docs/superpowers/specs/2026-06-01-special-locations-design.md | head -100
```

- [ ] **Step 2: Write `special-locations-ir.schema.json`**

Top-level shape: 10 properties (`drawing_type`, `version`, `mode`, `jurisdiction`, `room`, `anchor_fixtures`, `zones`, `electrical_constraints`, `existing_fixtures_audit`, `calculation_summary`) plus `invariants[]` and `rationale`. 8 required at top-level (everything except `electrical_constraints` and `existing_fixtures_audit` which are mode-conditional).

`invariants[].evidence` declares `maxLength: 1200` upfront per `[[feedback-no-trim-non-consequential]]` — avoids the photometric D.2 retrofit.

`additionalProperties: false` on every object block. Banned per CLAUDE.md to omit.

`zone_type` discriminator (14 values) at `zones[].properties.zone_type.enum`:

```json
["bath_zone_0", "bath_zone_1", "bath_zone_2",
 "pool_zone_0", "pool_zone_1", "pool_zone_2",
 "sauna_zone_1", "sauna_zone_2", "sauna_zone_3",
 "medical_envelope_group_0", "medical_envelope_group_1", "medical_envelope_group_2",
 "elv_barrier_zone"]
```

Wait — that's 13 values. The spec §5.2 says 14. Counting: 3 bath + 3 pool + 3 sauna + 3 medical + 1 elv = 13. The spec heading says 14 but the enum body shows 13. **Implementer note for A.2:** confirm count is 13 (3+3+3+3+1) before writing the schema; reach back to the spec §5.2 header math if discrepancy persists.

`constraint_type` discriminator (6 values) at `electrical_constraints[].properties.constraint_type.enum`:

```json
["medical_it_system", "supplementary_equipotential_bonding",
 "pool_main_equipotential_bonding", "whirlpool_pump_circuit",
 "rcd_blanket_by_room", "elv_separation"]
```

Mode-conditional `allOf` (2 clauses):

```json
{
  "allOf": [
    {
      "description": "Mode-conditional fixture audit + constraint requirement: full_analysis requires both; screening_only relaxes to zones-only.",
      "if": {"properties": {"mode": {"const": "screening_only"}}, "required": ["mode"]},
      "then": {"not": {"required": ["existing_fixtures_audit"]}},
      "else": {"required": ["existing_fixtures_audit", "electrical_constraints"]}
    },
    {
      "description": "§710 Group 2 medical envelope mandates a sibling medical_it_system constraint per BS 7671:2018 §710 + BS EN 61557-8 (IMD 8 s alarm response). Enforced declaratively at schema level.",
      "if": {
        "properties": {
          "zones": {"contains": {"properties": {"zone_type": {"const": "medical_envelope_group_2"}}, "required": ["zone_type"]}}
        }
      },
      "then": {
        "properties": {
          "electrical_constraints": {"contains": {"properties": {"constraint_type": {"const": "medical_it_system"}}, "required": ["constraint_type"]}}
        }
      }
    }
  ]
}
```

`zones[]` items full property set per spec §5.2 — copy verbatim from spec; populate `_clause_citation` description with allowed-citations note from spec §3.2.

`electrical_constraints[]` items use a `oneOf` array branching on `constraint_type` so each constraint type carries its own required-field contract per spec §5.3 (medical_it_system fields differ from rcd_blanket_by_room fields etc.).

`existing_fixtures_audit[]` items per spec §5.4.
`calculation_summary` per spec §5.5.
`invariants[]` per shared invariants pattern (id + passes + severity + evidence with `maxLength: 1200`).
`rationale` per `shared/schemas/core/rationale.schema.json` `$ref`.

- [ ] **Step 3: Write `special-locations-zoning-intent.schema.json`**

FLAT shape (no envelope wrap) per photometric A.3 precedent. Top-level: `intent_version`, `skill`, `consumed_lighting_layout_intent` (path string or null), `special_locations_zoning` (object).

`special_locations_zoning.properties`: 10 fields per spec §6 — `zones` (full IR zone shape — `$ref` to ir-schema), `electrical_constraints` (full IR constraint shape — `$ref`), `compliant`, `zone_count`, `constraint_count`, `violation_count_critical`, `violation_count_high`, `non_compliance_flags`, `anchor_source_summary`.

All 10 required.

`additionalProperties: false` at every object level.

- [ ] **Step 4: Validate both schemas parse**

```bash
python3 -c "
import json, jsonschema
for p in ['electrical/special-locations/schemas/special-locations-ir.schema.json',
          'electrical/special-locations/schemas/special-locations-zoning-intent.schema.json']:
    d = json.load(open(p))
    jsonschema.Draft202012Validator.check_schema(d)
    props = d.get('properties', {})
    print(f'{p}: parses + valid Draft 2020-12; {len(props)} top-level properties')
"
```

Expected: 2 lines, both parsing clean, IR has 10+ top-level properties, intent has 4 top-level.

- [ ] **Step 5: Run gates (no regression expected — no examples yet)**

```bash
python3 scripts/validate-examples.py 2>&1 | tail -3
```

Expected: baseline unchanged.

- [ ] **Step 6: Commit A.2**

```bash
git add electrical/special-locations/schemas/
git commit -m "$(cat <<'EOF'
feat(special-locations): A.2 IR + intent payload schemas

Second task of special-locations v1.0 sprint. Phase A foundations —
second of four.

IR schema (electrical/special-locations/schemas/special-locations-ir.schema.json):
- 10 top-level properties (drawing_type, version, mode, jurisdiction,
  room, anchor_fixtures, zones, electrical_constraints,
  existing_fixtures_audit, calculation_summary) + invariants[] + rationale
- 8 required at top level (electrical_constraints + existing_fixtures_audit
  mode-conditional via allOf)
- 14-value zone_type discriminator (3 bath + 3 pool + 3 sauna + 3 medical
  + 1 ELV); discriminator-conditional required fields per spec §5.2
- 6-value constraint_type discriminator with oneOf branches per type
  (medical_it_system imd_alarm_response_time_s_max: 8 per BS EN 61557-8;
  pool_main_equipotential_bonding conductor_csa_min_mm2: 10 per §702.415.1;
  whirlpool_pump_circuit ip_rating_min: IPx5 per §701.512.2;
  rcd_blanket_by_room rcd_rating_ma: 30 per §701.411.3.3 + §703.411.3.3
  with sauna_heater_excluded flag; supplementary_equipotential_bonding
  conductor csa per §701.415.2; elv_separation transformer_short_circuit_
  protected per BS EN 61558-2-6)
- 2 allOf clauses: mode-conditional + §710 Group 2 → medical_it_system
  structural enforcement
- additionalProperties: false at every object level
- invariants[].evidence maxLength: 1200 declared upfront per
  [[feedback-no-trim-non-consequential]] (avoids photometric D.2-style
  retrofit)
- Only verified citations from spec §3.2 referenced in property
  descriptions

Intent schema (special-locations-zoning-intent.schema.json):
- FLAT shape (no envelope wrap) per photometric A.3 precedent
- 4 top-level + 10 payload fields all required
- Payload zones/electrical_constraints $ref IR schema
- additionalProperties: false throughout

Gates: validate-examples baseline unchanged (no examples yet).

Next: A.3 inputs.json + 3 rules YAML files.
EOF
)"
```

---

## Task A.3: inputs.json + 3 rules YAML files (Sonnet)

**Why Sonnet:** Mechanical YAML/JSON authoring per the photometric A.4 precedent.

**Files:**
- Create: `electrical/special-locations/inputs.json`
- Create: `electrical/special-locations/rules/zone-derivation-rules.yaml`
- Create: `electrical/special-locations/rules/constraint-required-by-context-rules.yaml`
- Create: `electrical/special-locations/rules/provenance-disclosure-rules.yaml`

- [ ] **Step 1: Write `inputs.json` — 7 items per spec §4**

Top-level: `{"skill_id": "special-locations", "items": [...]}`. Each item has `{id, name, description, type, required, _validation_hint}`.

The 7 items per spec §4.1–4.7:

```json
{
  "skill_id": "special-locations",
  "items": [
    {
      "id": "anchor_fixtures",
      "name": "Anchor fixtures (extracted from architectural drawing)",
      "description": "List of anchor fixtures (bath, shower, pool, sauna heater, medical patient bed, ELV luminaire) sourced from the runtime's architectural-drawing extraction. Each carries _extraction_source provenance per spec §4.1.",
      "type": "array",
      "required": true,
      "_validation_hint": "Each entry: {type ∈ 6-value enum, id, position {x_mm, y_mm, z_floor_mm}, dimensions, shape_kind, conditional sub-fields per type (bath_kind / medical_group / shower_head_height_mm / whirlpool_pump_position), _extraction_source ∈ 3-tier enum, _provenance_note ≥40 chars}"
    },
    {"id": "room", "name": "Room context", "description": "Room polygon + ceiling height + room_type from 9-value enum + floor_finish + is_external + is_wet_room + optional ambient_temperature_c (drives ELV de-rating per D-5).", "type": "object", "required": true, "_validation_hint": "room_type ∈ {bathroom, shower_room, swimming_pool_hall, sauna, medical_group_0_area, medical_group_1_ward, medical_group_2_theatre, external_landscape, other}; room_polygon_mm ≥3 vertices"},
    {"id": "jurisdiction", "name": "Jurisdiction", "description": "GB / KE / INT — drives _clause_citation routing per spec §4.3.", "type": "string", "required": true, "_validation_hint": "enum: ['GB', 'KE', 'INT']"},
    {"id": "existing_fixtures", "name": "Existing fixtures for cross-check", "description": "OPTIONAL — engineer-supplied existing fixtures for cross-check when consumed lighting-layout intent is not yet available (early-design pre-check). Each entry: {type, position, ip_rating, voltage_v, is_rcd_protected, source_skill?, source_skill_intent_path?}. Skill iterates against derived zones → INV-08 violations.", "type": "array", "required": false, "_validation_hint": "Used when mode == full_analysis AND no consumed lighting-layout intent. Skip when consumed intent is present (intent is more recent authoritative source)."},
    {"id": "zone_polygon_override", "name": "Zone polygon overrides", "description": "OPTIONAL — engineer overrides derived zone polygons for irregular geometry (corner baths, L-shaped pools). Each entry: {zone_id, replacement_polygon_mm, _reason ≥40 char prose}. Original derivation preserved with _overridden_by_engineer: true flag.", "type": "array", "required": false},
    {"id": "medical_it_system_override", "name": "Medical IT system commissioning data", "description": "OPTIONAL — for §710 Group 2 rooms when engineer has commissioned IT system data ahead of compliance check. Fields: {isolating_transformer_va, insulation_monitoring_device_present, imd_alarm_response_time_s_observed (8 s typical per BS EN 61557-8), supplementary_bonding_verified, supplementary_bonding_resistance_ohm_observed (≤ 0.2 Ω per §710), safety_service_category (1/2/3 per HTM 06-01)}.", "type": "object", "required": false},
    {"id": "ies_lookup_paths", "name": "IES file paths for ELV §715 cross-check", "description": "OPTIONAL — for ELV §715 luminaire-IP cross-check via consumed lighting-layout intent. Mirrors photometric-analysis IES handling: each path may be a project-specific IES OR a synthetic_reference_C3 fallback from shared/photometric/ies/<type>.ies.", "type": "array", "required": false}
  ]
}
```

- [ ] **Step 2: Write `rules/zone-derivation-rules.yaml`**

Per-section geometry derivation rules with verified citations. Each rule: `{id, value, citation, rationale}`.

Cover: bath Zone 0/1/2 geometry per §701 (no sub-clause for the geometry itself in verified file — use generic §701); pool Zone 0/1/2 per §702 with 2 m horizontal + 1.5 m above water; sauna 3-zone split per §703 (Zone 1 small footprint around heater + Zone 2 sauna room minus Zone 1 + Zone 3 above 1.5 m AFF); medical envelope 1.5 m radius cylinder around patient_position per §710 (cylinder approximation noted per rule); ELV barrier zone per §715 (cable spacing + barrier).

Wet-room expansion: rule keyed `bath_zone_1_wet_room_expansion` with citation `BS 7671:2018 §701 + IET GN7 wet-room commentary` and rationale explaining no §701 sub-clause exists for this — generic §701 + IET GN7 cross-ref applies.

Total ≥12 rules. Banned citations from spec §3.2 must NOT appear.

- [ ] **Step 3: Write `rules/constraint-required-by-context-rules.yaml`**

The INV-03..INV-07 mapping table in rule form. 5+ rules:
- `medical_group_2_requires_it_system` — INV-03; citation `BS 7671:2018 §710 + BS EN 61557-8`
- `bathroom_requires_rcd_blanket` — INV-04 part A; citation `§701.411.3.3`
- `sauna_requires_rcd_blanket_with_heater_exemption` — INV-04 part B; citation `§703.411.3.3`
- `pool_requires_main_bonding` — INV-05; citation `§702.415.1` (NOT §702.55.1)
- `whirlpool_requires_pump_circuit` — INV-06; citation `§701 + §701.512.2`
- `elv_requires_separation` — INV-07; citation `§715 + BS EN 61558-2-6`

- [ ] **Step 4: Write `rules/provenance-disclosure-rules.yaml`**

`_extraction_source` 3-tier enum + per-tier rule:
- `tier_a_architectural_extraction` — strongest; no manual review needed; _provenance_note ≥40 chars
- `tier_b_engineer_manual_entry` — medium; should be cross-checked against architectural drawing during review
- `tier_c_inferred_from_room_type` — weakest; INV-09 MEDIUM + D-1 reviewer flag when this tier drives safety-critical zones (medical_envelope_group_2 / pool_zone_0 / bath_zone_0)

- [ ] **Step 5: Validate inputs.json + rules YAMLs**

```bash
python3 -c "
import json, jsonschema, yaml
# inputs.json validation
inputs_schema = json.load(open('shared/schemas/core/inputs.schema.json'))
inputs = json.load(open('electrical/special-locations/inputs.json'))
jsonschema.validate(instance=inputs, schema=inputs_schema)
print(f'inputs.json: OK ({len(inputs[\"items\"])} items)')

# rules YAML parse
import glob
for p in sorted(glob.glob('electrical/special-locations/rules/*.yaml')):
    d = yaml.safe_load(open(p))
    rules = d.get('rules', [])
    print(f'{p}: OK ({len(rules)} rules)')
"
```

Expected: 4 lines OK.

- [ ] **Step 6: Verify no banned citations present**

```bash
grep -nE "(§701\.32|§701\.55|§702\.55\.1|§702\.55\.2|§702\.32|§703\.55|§703\.512|§703\.413|§710\.413|§710\.314|§710\.411|§715\.560|§715\.521|§715\.422)" electrical/special-locations/rules/ electrical/special-locations/inputs.json && echo "FAIL: banned citations found" || echo "PASS: no banned citations"
```

Expected: `PASS: no banned citations`.

- [ ] **Step 7: Run gates**

```bash
python3 scripts/validate-examples.py 2>&1 | tail -3
```

Expected: validate-examples bumps by 1 (Pass 3 now finds + validates the new inputs.json).

- [ ] **Step 8: Commit A.3**

```bash
git add electrical/special-locations/inputs.json electrical/special-locations/rules/
git commit -m "$(cat <<'EOF'
feat(special-locations): A.3 inputs.json + 3 rules YAML files

Third task of special-locations v1.0 sprint. Phase A foundations —
third of four.

inputs.json (7 WI1 items per spec §4):
- anchor_fixtures (required) — extracted from architectural drawing by
  runtime; 6-value type enum + conditional sub-fields + 3-tier
  _extraction_source provenance
- room (required) — 9-value room_type enum + polygon + ceiling +
  is_wet_room + ambient_temperature_c
- jurisdiction (required) — GB / KE / INT
- existing_fixtures (optional) — engineer cross-check fallback
- zone_polygon_override (optional) — irregular geometry overrides
- medical_it_system_override (optional) — commissioned IT system data
  including imd_alarm_response_time_s_observed (8 s typical per
  BS EN 61557-8)
- ies_lookup_paths (optional) — ELV §715 cross-check IES

Rules YAML (3 files):
- zone-derivation-rules.yaml — bath / pool / sauna 3-zone / medical
  envelope / ELV barrier geometry rules with verified citations only
- constraint-required-by-context-rules.yaml — INV-03..07 mapping
  (medical_it / RCD bathroom + sauna-with-heater-exemption / pool
  bonding §702.415.1 / whirlpool §701.512.2 / ELV §715 +
  BS EN 61558-2-6)
- provenance-disclosure-rules.yaml — 3-tier _extraction_source policy

Zero banned citations (§701.32, §701.55, §702.55.1, §702.55.2,
§702.32, §703.55, §703.512, §703.413, §710.413.1.5, §710.314,
§710.411.3.3, §715.560.4, §715.521, §715.422 all absent — verified
by grep).

Gates: validate-examples +1 (Pass 3 picks up inputs.json).

Next: A.4 shared zone-derivation library.
EOF
)"
```

---

## Task A.4: Shared zone-derivation library (Opus)

**Why Opus:** Geometry math + per-section engineering nuance (sauna 3-zone footprint split, medical envelope cylinder approximation, pool changing-room overlap detection, wet-room expansion logic). This is engineering judgment territory, not mechanical.

**Files:**
- Create: `shared/special-locations/README.md`
- Create: `shared/special-locations/zone-derivation/__init__.py`
- Create: `shared/special-locations/zone-derivation/common.py`
- Create: `shared/special-locations/zone-derivation/bath.py`
- Create: `shared/special-locations/zone-derivation/pool.py`
- Create: `shared/special-locations/zone-derivation/sauna.py`
- Create: `shared/special-locations/zone-derivation/medical.py`
- Create: `shared/special-locations/zone-derivation/elv.py`
- Create: 6 test files under `shared/special-locations/zone-derivation/tests/` (one per module + common)

- [ ] **Step 1: Write `shared/special-locations/README.md`**

Same shape as `shared/photometric/README.md` — purpose + verification policy + per-module summary + when to substitute.

State explicitly: this Python library is the REFERENCE implementation; the runtime project hosts the executor; this repo ships the contract + reference per `[[runtime-project-boundary]]`.

- [ ] **Step 2: Write `zone-derivation/__init__.py`**

```python
"""Zone derivation library for special-locations skill.

Computes BS 7671:2018+A2:2022 Part 7 zone polygons + height bounds from
anchor fixtures. Reference implementation; runtime project hosts the
executor.

Verified against shared/standards/electrical/BS7671/part7-special-locations.json
(verification_status: verified-against-source).
"""

__version__ = "1.0.0"
__all__ = ["bath", "pool", "sauna", "medical", "elv", "common"]

from . import common, bath, pool, sauna, medical, elv
```

- [ ] **Step 3: Write `common.py` — cylinder-to-polygon + polygon operations**

Stdlib-only. Functions:
- `cylinder_to_polygon(center_xy, radius_mm, sides=12)` → returns ≥12-sided regular polygon as `[(x,y), ...]`
- `rectangular_zone(center_xy, length_mm, width_mm, rotation_deg=0)` → 4-vertex polygon
- `expand_polygon_horizontally(polygon, distance_mm)` → Minkowski sum approximation (for §702 2 m extension and §701 0.6 m Zone 2)
- `polygon_intersects(poly1, poly2)` → boolean (Shapely-free; ray-casting or SAT)
- `polygon_subtract(outer, inner)` → polygon difference (for sauna_zone_2 = sauna_room − sauna_zone_1)

- [ ] **Step 4: Write `bath.py`**

Per §701 verified body:
- `bath_zone_0(bath_anchor)` → rectangular polygon = basin footprint; height_min=0, height_max=basin_top_z; IPx7
- `bath_zone_1(bath_anchor, room_ceiling_mm, is_wet_room=False)` → polygon = above_zone_0; height_min=basin_top_z, height_max=max(2250, shower_head_height_mm); IPx4; when is_wet_room=True, polygon expands to full room floor
- `bath_zone_2(bath_anchor, room_polygon)` → polygon = expand_polygon_horizontally(zone_1, 600); IPx4; height_min=0, height_max=2250
- `whirlpool_pump_position_default(bath_anchor)` → defaults to bath edge midpoint; flag `_assumption_default_placement: true`

All clause citations on output zones: `BS 7671:2018 §701` (top-level only — no sub-clause for geometry in verified file).

- [ ] **Step 5: Write `pool.py`**

Per §702:
- `pool_zone_0(pool_anchor)` → basin interior polygon; height_min=0, height_max=water_surface_z
- `pool_zone_1(pool_anchor, water_surface_z)` → vertical column above zone_0; height_min=water_surface_z, height_max=water_surface_z + 2500
- `pool_zone_2(pool_anchor)` → expand_polygon_horizontally(zone_0, 2000); IPx4; height_min=0, height_max=water_surface_z + 1500
- `check_changing_room_overlap(pool_zone_2_polygon, adjacent_room_polygon, barrier_distance_mm=200)` → returns bool for D-2 reviewer flag

Clauses: `§702` generic + `§702.415.1` main bonding + `§702.55.4` changing-room.

- [ ] **Step 6: Write `sauna.py` — 3 zones per verified file**

```python
def sauna_zone_1(heater_anchor):
    """§703 Zone 1 — around the heater (high temperature zone).
    Small rectangular footprint, typically 500mm around heater anchor.
    Cables must be silicone insulated (170°C ambient) per verified file.
    """
    # Returns polygon, height_min=0, height_max=ceiling, ip_rating=IPx4

def sauna_zone_2(heater_anchor, sauna_room_polygon):
    """§703 Zone 2 — within the sauna room, away from heater.
    Computed as sauna_room_polygon - sauna_zone_1.
    Light fittings: IPx4 minimum, T-rated to 125°C.
    """

def sauna_zone_3(sauna_room_polygon, ceiling_height_mm):
    """§703 Zone 3 — higher level (above 1.5m for accessories).
    Returns sauna_room_polygon at height_min=1500, height_max=ceiling.
    """
```

Each function emits `_clause_citation: "BS 7671:2018 §703"` (top-level only). RCD note: heater circuit exempt per §703.411.3.3.

- [ ] **Step 7: Write `medical.py`**

```python
def medical_envelope(patient_position, medical_group, ceiling_height_mm):
    """§710 medical envelope.
    1.5m radius cylinder around patient_position, height_min=0,
    height_max=2500 (per typical patient envelope above bed).
    Returns zone_type per group: medical_envelope_group_0/1/2.

    Group 2 triggers MANDATORY sibling medical_it_system constraint
    (enforced at IR allOf level, INV-03 at validator level).

    Citation: BS 7671:2018 §710 + BS EN 61557-8 (IMD 8s alarm response)
    + HTM 06-01 (NHS precedence; safety service categories).
    """
```

- [ ] **Step 8: Write `elv.py`**

```python
def elv_barrier_zone(elv_anchor, lv_cable_spacing_mm_min=100):
    """§715 ELV barrier zone.
    Polygon spanning cable spacing requirements from elv_anchor.
    Returns zone with barrier_required: True, label_required: True,
    transformer_short_circuit_protected: True.

    Citation: BS 7671:2018 §715 + BS EN 61558-2-6 (transformer
    short-circuit protection).
    """
```

- [ ] **Step 9: Write unit tests under `zone-derivation/tests/`**

Each module gets a test file. Use Python `unittest` (stdlib). Test:
- `test_common.py` — cylinder polygon has ≥12 sides; expand_polygon_horizontally roundtrips on simple rectangle; polygon_intersects on overlapping vs disjoint
- `test_bath.py` — Zone 0/1/2 dimensions match a hand-calculated 1700×700 bath at default ceiling 2400mm; wet-room expansion fills room
- `test_pool.py` — 5m×10m pool yields 5m+2m+2m wide Zone 2; changing-room overlap detection passes when 200mm gap, fails when 100mm gap
- `test_sauna.py` — 3-zone split sums to sauna room polygon; Zone 1 < Zone 2 area; Zone 3 starts at 1500mm
- `test_medical.py` — Group 2 envelope is 12-sided polygon, radius ≥1500mm
- `test_elv.py` — barrier zone has barrier_required=True

- [ ] **Step 10: Run tests**

```bash
cd shared/special-locations && python3 -m unittest discover -s zone-derivation/tests -v 2>&1 | tail -10
cd ../..
```

Expected: all tests pass; no third-party deps required.

- [ ] **Step 11: Run gates (no regression — library not in golden CI path)**

```bash
python3 scripts/validate-examples.py 2>&1 | tail -3
```

Expected: unchanged from A.3 baseline (geometry library is reference, not validated by golden CI directly).

- [ ] **Step 12: Commit A.4**

```bash
git add shared/special-locations/
git commit -m "$(cat <<'EOF'
feat(shared/special-locations): A.4 zone-derivation reference library + unit tests

Fourth task of special-locations v1.0 sprint. Phase A foundations —
fourth of four. Phase A complete after this task.

Reference Python stdlib library implementing BS 7671:2018+A2:2022
Part 7 zone derivation from anchor fixtures. Runtime project hosts
the executor; this repo ships the contract + reference per
[[runtime-project-boundary]].

shared/special-locations/zone-derivation/:
- common.py — cylinder→polygon approximation (≥12 sides) +
  expand_polygon_horizontally (Minkowski sum) + polygon ops
- bath.py — §701 Zone 0 basin + Zone 1 above (with wet-room
  expansion) + Zone 2 0.6m horizontal extension; whirlpool pump
  default placement
- pool.py — §702 Zone 0 basin + Zone 1 above + Zone 2 2m horizontal
  to 1.5m above water; §702.55.4 changing-room overlap check
- sauna.py — §703 3-ZONE split per verified file: Zone 1 around
  heater high-temp + Zone 2 sauna body (= room - Zone 1) + Zone 3
  above 1.5m for accessories
- medical.py — §710 1.5m radius cylinder around patient_position
  per group; Group 2 mandates IT-system sibling
- elv.py — §715 barrier zone with BS EN 61558-2-6 transformer
  protection

6 module unit-test files under tests/ — all pass via stdlib unittest;
no third-party deps.

All clause citations verified against shared/standards/electrical/
BS7671/part7-special-locations.json. Banned citations grep-checked
absent. Generic top-level §701/§702/§703/§710/§715 citations used
where no verified sub-clause exists.

Gates: validate-examples unchanged (library not in golden CI path).

Phase A complete. Next: Phase B — prompts (B.1 generator + B.2
validator + B.3 reviewer).
EOF
)"
```

---

[Phase B + C + D continue in subsequent plan portions — committed sequentially per the photometric-analysis precedent. Phase B covers the 3 prompt tasks (generator + validator + reviewer); Phase C covers the 8 standalone + 9 cascade examples + 7 evals; Phase D covers the 3 cascade-integration retrofits + the sprint ship with Sonnet 11-check fence + memory + push.]
