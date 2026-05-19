# DraftsMan Skills — Architecture

## Three-layer model

```
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 1 — Shared Infrastructure  (shared/)                     │
│                                                                 │
│  standards/   ontology/   symbols/   calculations/              │
│  schemas/     validation/ units/     drafting/                  │
│                                                                 │
│  Owned by: standards committee / repo maintainers               │
│  Changes require: version bump + migration note                  │
└───────────────────────┬─────────────────────────────────────────┘
                        │  referenced by path in skill manifests
┌───────────────────────▼─────────────────────────────────────────┐
│  LAYER 2 — Engineering Intelligence  ([discipline]/[skill]/)    │
│                                                                 │
│  prompts/    rules/       constraints/   validation/            │
│  evals/      examples/    ontology/      schemas/               │
│  docs/       annotations/ symbols/       drafting/              │
│                                                                 │
│  skill.manifest.json — declares all inputs, outputs, refs       │
│                                                                 │
│  Owned by: discipline engineers                                  │
│  Changes require: CHANGELOG.md entry + eval re-run              │
└───────────────────────┬─────────────────────────────────────────┘
                        │  AI generates IR; runtime consumes it
┌───────────────────────▼─────────────────────────────────────────┐
│  LAYER 3 — DraftsMan Runtime  (separate repo)                   │
│                                                                 │
│  IR → DXF   IR → IFC   IR → Revit   IR → PDF   IR → Schedule   │
│                                                                 │
│  Owned by: platform team                                         │
│  This repo has no runtime code — only the intelligence layer    │
└─────────────────────────────────────────────────────────────────┘
```

## Layer ownership

### Layer 1 — Shared Infrastructure (`shared/`)

The shared layer holds all content that is reused across multiple skills
or disciplines. Nothing here is skill-specific.

| Directory | Content |
|-----------|---------|
| `standards/` | Machine-readable extracts of named standards. Each standard lives in its own versioned folder: `BS7671/`, `BSEN12464/`, `IEC60617/`, etc. Values taken from tables are annotated with clause references. |
| `ontology/` | Room types, building elements, equipment classifications. Provides a common vocabulary so all skills agree on what "open_plan_office" means. |
| `symbols/` | Symbol definitions (geometry, CAD parameters, snap points) for luminaires, switchgear, pipework fittings. Consumed by the IR renderer. |
| `calculations/` | Formula definitions and worked method descriptions. Skills reference these rather than restating the maths. |
| `schemas/` | JSON Schema files for Intermediate Representation documents. |
| `validation/` | Cross-skill validation rules (Fundamental Rule, lux minimums, etc.) that apply regardless of which skill produced the IR. |
| `units/` | SI unit definitions and imperial/AWG conversion tables. |
| `drafting/` | Layer tables, lineweight standards, titleblock templates. |

### Layer 2 — Engineering Intelligence (`[discipline]/[skill]/`)

Each skill is a self-contained directory. The `skill.manifest.json` is the
machine-readable entry point; everything else is referenced from it.

**Skill structure:**

```
[skill]/
├── skill.manifest.json       # machine-readable entry point
├── README.md                 # human summary
├── CHANGELOG.md              # version history
├── prompts/
│   ├── generator.md          # main design prompt (the "skill")
│   ├── reviewer.md           # QA / peer review prompt
│   └── validator.md          # output validation prompt
├── rules/                    # engineering rules (YAML)
├── constraints/              # hard constraints (YAML)
├── evals/                    # one YAML file per eval scenario
├── examples/
│   └── [scenario-name]/
│       ├── input.json        # structured inputs
│       ├── reasoning.md      # step-by-step working
│       └── output.json       # full IR output
├── schemas/                  # skill-specific IR schema
├── validation/               # skill-level validation rules
├── ontology/                 # skill-specific classifications
├── annotations/              # tag / label formats
├── drafting/                 # skill-specific layer overrides
├── symbols/                  # local symbol overrides
├── calculations/             # local formula overrides
└── docs/                     # engineering philosophy, limitations
```

### Layer 3 — DraftsMan Runtime (separate repository)

The runtime is not in this repository. Its sole contract with Layer 2 is
the IR schema. Any agent or tool that can produce a valid IR document
can be used as a generator — Claude, GPT-4, a deterministic Python script,
or a human filling in a form.

## Intermediate Representation (IR)

The IR is a structured JSON document produced by the AI and consumed by the
renderer. It contains all the information needed to produce a drawing or
document without any further inference.

**Principles:**
- IR is output, not input. Agents read prompts and examples; they write IR.
- IR is validated against a JSON Schema before the renderer processes it.
- IR is human-readable. An engineer must be able to audit it without tooling.
- IR never contains rendered geometry — only logical design data.

**Example IR top-level structure (lighting-layout):**

```json
{
  "meta":       { "skill": "lighting-layout", "version": "1.2.0", ... },
  "room":       { "type": "open_plan_office", "length_m": 10, ... },
  "luminaires": [ { "id": "L01", "symbol": "LED_PANEL_600", "x_m": 1.5, ... } ],
  "circuits":   [ { "id": "L1-Z1", "luminaire_ids": ["L01","L02",...], ... } ],
  "switches":   [ { "id": "SW01", "type": "two_gang_plate", ... } ],
  "zone":       { "id": "Z1", "type": "general", "lux_achieved": 512 },
  "compliance": { "lux_ok": true, "part_l_ok": true, "ugr_ok": true },
  "flags":      [ "[ASSUMPTION: MF=0.80 — cleaning regime not confirmed]" ]
}
```

## Standards versioning

Each standard occupies its own folder named after the edition year or
publication number. When a new edition is released, a new folder is added
and the old folder is retained:

```
shared/standards/electrical/
├── BS7671/          # BS 7671:2018 + AMD 2 (2022)
├── IEC60364/        # IEC 60364 series
├── IEC60617/        # IEC 60617 graphical symbols
├── IEC61439/        # switchgear assemblies
├── NFPA70/          # NEC 2023
└── local-codes/
    ├── Kenya/       # KEBS / ERC regulations
    ├── Nigeria/     # SON / NERC regulations
    └── SouthAfrica/ # SANS 10142-1
```

Skills declare which standards package they use in `skill.manifest.json`:

```json
"standards_refs": [
  "shared/standards/electrical/BS7671",
  "shared/standards/lighting/BSEN12464"
]
```

To produce a regional variant, swap the standards package. The engineering
logic in the prompts and rules does not change; only the values change.

## Regional adaptation

The same skill can target multiple jurisdictions by pointing at different
standards packages. The AI is instructed via the manifest and prompt to
load the correct values at runtime.

| Region | Electrical standard | Lighting standard |
|--------|--------------------|--------------------|
| UK / England & Wales | BS 7671:2018 AMD 2 | BS EN 12464-1:2021 |
| USA / Canada | NFPA 70 (NEC) 2023 | IESNA / IES |
| Kenya | KEBS EAS 62 / ERC | BS EN 12464-1 |
| Nigeria | SON NIS 436 / NERC | BS EN 12464-1 |
| South Africa | SANS 10142-1:2020 | SANS 10114-1 |

## Discipline structure

```
draftsman-skills/
├── shared/                   # Layer 1 — shared infrastructure
├── electrical/               # LV power, lighting, ELV systems
├── mechanical/               # HVAC, ductwork, refrigeration
├── plumbing/                 # cold/hot water, drainage, stormwater
├── fire-protection/          # sprinklers, hydrants, detection
├── calculations/             # calculation skills (multi-discipline)
├── documents/                # documents and reports
└── coordination/             # BIM, clash detection, combined services
```

## Skill manifest schema

Every skill must have a `skill.manifest.json` at its root. Required fields:

```json
{
  "skill":              "string — kebab-case skill identifier",
  "version":            "string — semver",
  "discipline":         "string",
  "subdiscipline":      "string",
  "status":             "stub | draft | beta | production",
  "licence":            "string — SPDX expression",
  "inputs":             ["array of named input fields"],
  "outputs":            ["array of output type identifiers"],
  "output_schema":      "path to JSON Schema relative to repo root",
  "standards_refs":     ["paths to shared/standards/ entries used"],
  "shared_refs":        ["paths to other shared/ content used"],
  "compatible_runtimes":["list of compatible runtime identifiers"],
  "prompt_path":        "path to prompts/generator.md",
  "eval_paths":         ["paths to evals/*.yaml"],
  "example_paths":      ["paths to examples/*/"]
}
```

## Cross-drawing intents

A real project has multiple chats — earthing, DB, lighting, small-power,
cable-containment — and engineering decisions on one drawing affect others.
The earthing chat's Zs verification needs breaker ratings from the DB chat.
The cable-containment chat needs cable counts from DB / lighting / small-power.

To make this composable, skills declare their cross-drawing data flow on the
manifest:

```json
{
  "produces_intent":         "lighting-layout",
  "produces_intent_schema":  "electrical/lighting-layout/schemas/lighting-layout-intent.schema.json",
  "consumes_intents":        ["db-layout", "lighting-layout", "small-power"]
}
```

### Intent payload vs full IR

The **full IR** carries everything the runtime needs to render a drawing
(positions, drawing notes, layers, presentation). The **intent payload**
is a stable, smaller subset published for downstream skills.

| | Full IR | Intent payload |
|---|---|---|
| Audience | runtime renderer | sibling skills |
| Size | thousands of lines | dozens to hundreds |
| Stability contract | per skill version | per intent_version (independent semver) |
| Forward-compat | minor IR changes can break renderer | only major intent bumps may remove required fields |

### Envelope schema

Every intent payload is wrapped at runtime in
`shared/schemas/core/intent.schema.json`:

```json
{
  "intent_type":   "lighting-layout",
  "intent_version":"1.0.0",
  "produced_by":   { "skill": "lighting-layout", "skill_version": "1.3.0", "chat_id": "..." },
  "produced_at":   "2026-05-15T11:34:00Z",
  "payload":       { /* conforms to <skill>-intent.schema.json */ }
}
```

### Producer rules

- A skill produces **one** intent type only. Name it the same as the skill id.
- Author the per-skill intent schema at `<skill>/schemas/<skill>-intent.schema.json`.
- Reference it from the manifest's `produces_intent_schema` field.
- Forward-compat: add optional fields freely; remove or rename required
  fields only with a major `intent_version` bump.

### Consumer rules

When a skill declares `consumes_intents: [...]`, the runtime pre-fetches the
latest intent for each declared producer from the project's other chats and
injects them as additional context in the user message under
`cross_drawing_context`:

```json
{
  "cross_drawing_context": {
    "db-layout":       { /* db-layout intent envelope */ },
    "lighting-layout": [ /* per chat */ ],
    "small-power":     [ /* per chat */ ]
  }
}
```

A `consumes_intents` skill **must handle the case where one or more intents
are absent** (empty project, sibling chat hasn't completed yet). Generate a
flag in `rationale.sections[].decisions` indicating the gap, e.g.
`"no db-layout chat in this project; cable demand from explicit entry only"`.

### Current intent producers

| Skill | Produces | Status |
|---|---|---|
| lighting-layout | `lighting-layout` | schema authored, manifest declared |
| db-layout       | `db-layout`       | schema authored, manifest declared (skill itself still a stub) |

### Planned intent producers (when those skills are authored)

| Skill | Produces | Consumes |
|---|---|---|
| small-power      | `small-power`      | `db-layout` |
| earthing         | `earthing`         | `db-layout`, `lighting-layout`, `small-power` |
| cable-containment| `cable-containment`| `db-layout`, `lighting-layout`, `small-power`, `earthing` |

The runtime cannot validate `consumes_intents` references until the matching
producer schemas exist. Adding a new `consumes_intents` entry referencing a
not-yet-authored producer is fine — the runtime treats the missing producer
as an absent intent and the consumer skill flags the gap per its prompt.

### Worked example pattern (since 2026-05-18)

The `electrical/earthing` skill (v1.3+) consumes `db-layout` intents in all 4 worked examples. Each pair demonstrates the WI4 contract:

| Downstream (earthing) | Upstream (db-layout) | Pattern |
|---|---|---|
| KE Nairobi industrial TN-S | KE Nairobi industrial 100A TPN | Same scenario; full circuit alignment (C01-C08); built in paired v1.3 sprint |
| UK dwelling TN-C-S | UK domestic consumer unit | Domestic pairing; 6-circuit alignment (C01-C06) |
| INT commercial earthing | INT commercial TPN MSB | Cross-domain pairing (previously rural TT consumer + commercial TPN producer; v1.3 re-anchored to commercial MSB scenario); 4-feeder alignment (F01-F04) |
| US commercial NEC | US strip mall panelboard | NEC commercial pairing; 4-circuit alignment (C01-C04) with AWG cable conventions |

The pattern is generalizable: any consumer skill that declares `consumes_intents` populates `meta.consumed_intents[]` + carries `consumed_intent_path` in input.json + aligns its derived fields to the upstream intent.

Future consumers (cable-sizing, fault-level, arc-flash) will follow this pattern when their respective minor-version sprints add db-layout intent consumption.

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

### SLD multi-skill intent consumption (v1.4+)

SLD v1.4 generalizes the WI4 cross-drawing intent pattern from single-skill (v1.3 db-layout only) to multi-skill: each SLD example now consumes 3 upstream skill domains.

| Source skill | Count per SLD example | Content consumed |
|---|---|---|
| db-layout | N entries (one per board) | per-board OCPD + cable + load + supply_origin |
| earthing | 1 entry (system-wide) | system_type, ze_declared_ohm, supply_bond_type |
| fault-level | 1 entry (system-wide) | peak_pfc_ka at transformer secondary |

**Length invariant:** `meta.consumed_intents.length == distribution_hierarchy.length + 2`

**Cross-skill consistency (INV-11):**
- SLD `supply_origin.system_type` MUST equal earthing intent's top-level `system_type` field
- SLD `system_metrics.peak_pfc_ka` MUST be within ±0.5 kA of fault-level intent's `fault_currents[]` entry where `node_kind == "transformer_secondary"` → `ifault_ka_max`

**Engineering benefit:** `peak_pfc_ka` was an LLM inline estimate in v1.3. In v1.4 it sources from deterministic IEC 60909-0:2016 cascade computation (via fault-level intent). This is the first concrete demonstration of multi-skill provenance feeding engineering precision — sometimes flipping compliance verdicts (e.g., KE example's 10.22 kA deterministic PFC vs 10 kA Icu).

**Backward compatibility:** v1.3 examples remain valid. INV-11 only fires when both `earthing_intent_path` AND `fault_level_intent_path` are declared in input.

**Pattern parents:** earthing v1.3 (single-board WI4 single-skill); SLD v1.3 (multi-board WI4 single-skill); this sprint = multi-board + multi-skill.

### Drawing layout (v1.5+)

SLD v1.5 adds the spatial-intent layer to the SLD IR — engineering layout judgment that the runtime renderer consumes to produce drawings. **Skills emit intent; runtime computes geometry.** See [[runtime-project-boundary]].

**Schema:** OPTIONAL top-level `drawing_layout` block with 3 enums:

| Enum | Values | Purpose |
|---|---|---|
| `layout_group` | main, general_power, lighting, mechanical, fire_alarm_life_safety, emergency_power, comms, other | Functional grouping → CAD layer assignment |
| `routing_intent` | via_main_spine, via_dedicated_riser, via_shared_tray, direct_from_msb, via_genset_changeover | How the feeder reaches each board |
| `sheet_size` | A0, A1, A2, A3, Arch_E, Arch_D, Arch_C | Jurisdictional drawing-sheet template |

**CAD layer naming via jurisdiction-aware lookup tables** (`shared/standards/drafting/<jurisdiction>/cad-layers.json`):

| Jurisdiction | Lookup table |
|---|---|
| GB | `BS1192/cad-layers.json` (BS 1192:2007+A2:2016) |
| KE | `BS1192/cad-layers.json` (KS 1700:2018 §313 routes to BS 1192) |
| US | `AIA/cad-layers.json` (AIA CAD Layer Guidelines 2007) |
| INT / EU | `ISO19650/cad-layers.json` (ISO 19650:2018 + BS 1192 generic) |

**Multi-sheet split rule (hybrid):** ≤8 boards single-sheet UNLESS `fire_alarm_life_safety` + `general_power` boards coexist (life-safety isolation per BS 9999 §6.4 / IEC 60364-5-56:2018 §560 / NFPA 72 §10.6 → mandatory split).

**Skill / runtime boundary preserved:** v1.5 does NOT produce x/y coordinates. Runtime renderer in the separate project takes intent + IR + symbol library → SVG/DXF/PDF.

**Validator INV-12 + INV-13 + INV-14** enforce schema conformance + jurisdictional sheet sizes + split logic. Backward-compatible: v1.3 / v1.4 examples without drawing_layout skip these checks entirely.

### Drafting standards layer (v1.6+)

v1.6 expanded `shared/standards/drafting/` from 3 minimal cad-layers.json files (8-entry enum each, shipped in SLD v1.5) to a full 10-standard layer at electrical-standards depth (mirrors `shared/standards/electrical/BS7671/` pattern). Skills emit drafting-standard references (e.g., `drawing_standard: "BS 1192:2007+A2:2016"`); runtime renderer and future skills query the lookup tables. No executable code in this repo per [[runtime-project-boundary]].

**10 standards covered:**

| Standard | Folder | Primary use |
|---|---|---|
| BS 1192:2007+A2:2016 | `BS1192/` | UK information management + layer naming + file naming + revision conventions |
| ISO 19650:2018 (Parts 1-5) | `ISO19650/` | International CDE workflows + security + federated information management |
| AIA CAD Layer Guidelines 2007 | `AIA/` | US layer naming + status codes + discipline designators |
| ISO 5457:1999/A1:2010 | `ISO5457/` | Sheet sizes A0-A4 + drawing area + title block region |
| ISO 5455:1979 | `ISO5455/` | Standard scales + use guidance per discipline |
| ISO 7200:2004 | `ISO7200/` | Title block data fields (mandatory + optional) |
| ISO 128 (multi-part) | `ISO128/` | Line widths + line types |
| ISO 129-1:2018 | `ISO129/` | Dimensioning rules + tolerances + symbols |
| ISO 9431:1990 | `ISO9431/` | Drawing fold procedures |
| BS 5536:1978 | `BS5536/` | UK reading of ISO 128 line conventions |

**Top-level discovery file:** `shared/standards/drafting/meta.json` indexes all 10 standards + maps 5 jurisdictions (GB/KE/US/INT/EU) to primary standards.

**Engine-lookupable convention:** Each data JSON ships `{clause_ref, transcribed_at, transcribed_by, verification_status, _title, _source, _note, _cross_refs, <primary_key>: {...}, engine_lookup: {...}}` shape consistent with `shared/standards/electrical/BS7671/` files. The `engine_lookup` wrapper provides a flat key/value form for runtime engine consumption.

**Verification status enum (per file):**
- `verified-against-source` — author confirmed values against the purchased standard
- `draft-pending-verification` — drafted from secondary source; engineer review needed
- `draft-from-secondary-needs-second-source-pair` — single secondary source only; second-source check pending

**Cross-references:** Each meta.json declares a `_cross_refs[]` array (one-direction only — referenced-from, not referenced-to) to neighbouring standards.

**Skill / runtime boundary preserved:** drafting standards are contract data only. Renderer + lookups live in the separate runtime project per [[runtime-project-boundary]].

**Pattern parent:** `shared/standards/electrical/BS7671/` (17 JSONs + 10 markdowns).

### small-power skill (v1.0+)

v1.0 ships as a leaf skill (no cross-skill intent consumption) matching the lighting-layout v1.3 production pattern. Produces a small-power intent for downstream db-layout consumption. Hybrid IR: `circuits[]` (with topology enum: ring | radial | dedicated_radial) + `rooms[]` (with sockets[] cross-referencing circuit_ids). Supports cross-room rings naturally (e.g., UK ground-floor ring covering kitchen + utility + dining + lounge).

**3 design enums:**

| Enum | Values | Purpose |
|---|---|---|
| `topology` | `ring`, `radial`, `dedicated_radial` | Circuit topology — ring only allowed in GB+KE per INV-04 |
| `special_location` | `null`, `bathroom_zone_1`, `bathroom_zone_2`, `bathroom_zone_3`, `outdoor`, `wet_area` | Room special-location flag — drives RCD requirements per BS 7671 Part 7-701 / IEC 60364-7-701 / NEC 210.8 |
| `rcd_posture` | `type_a_30ma_per_§411_3_3`, `type_b_30ma_per_§531_3_3`, `no_rcd_with_documented_§411_exception` | RCD strategy per circuit — default Type A 30mA; Type B for IT loads with DC leakage components per IEC 60364-5-53 §531.3.3; explicit-citation exception for documented edge cases |

**Calc tool consumption (existing contracts reused — NOT created):**

- `calc.diversity_factor` — shared/calculations/electrical/diversity-factor.json (handles all 5 jurisdictions: IET OSG App A / NEC 220.40 / IEC 60364-1 §132.12)
- `calc.zs_loop_impedance` — shared/calculations/electrical/zs-loop-impedance.json (ring + radial Zs verification; small-power added to _consuming_skills[] in Task 3)

WI3 deferral: every circuit carries `tool_call_pending_for_zs_verification: true` + the IR-level `flags[]` contains `TOOL-CALL-PENDING:calc.zs_loop_impedance`. Matches SLD v1.3 + earthing v1.1 precedent.

**Standards consumption:**

- BS 7671:2018+A2:2022 Part 7-701, §411.3.3, §433.1.5 (existing)
- IEC 60364-4-41:2017, -5-53:2002+A2:2015, -7-701:2019 (existing)
- KS 1700:2018 §313 routing + §701 (existing)
- NEC 2023 Article 210 (NEW — small-power adds shared/standards/electrical/NFPA70/part7-special-locations.json with NEC 210.8 GFCI scope + 210.12 AFCI scope + 406.12 tamper-resistant)
- Drafting standards v1.6 layer (sheet template + scale + layer naming per jurisdiction: BS 1192 for GB/KE; ISO 19650 for INT; AIA CAD Layer Guidelines for US)

**Cross-skill alignment (v1.0 leaf shape):**

INT example C06 (server-room small-power) manually mirrors the Type B 30mA RCD policy from db-layout's shipped `intl-dbcomms-data` example. Engineer mirrors the policy as input rather than consuming via intent (v1.0 ships as leaf). v1.1+ will migrate to consume earthing + fault-level intents for automatic cross-skill alignment, per SLD v1.3→v1.4 precedent.

**4 jurisdictional examples:**

| Folder | Scenario | Topology | Special note |
|---|---|---|---|
| `uk-3bed-dwelling/` | 3-bed dwelling, ~100 m² | 2 rings + 3 dedicated radials | Bathroom Part 7-701 zone 3, outdoor IP65 |
| `ke-nairobi-small-office/` | 80 m² Nairobi office | 4 radials (no ring — KE commercial practice) | KS 1700:2018 §313 + §701 routing; KPLC TN-S 415V |
| `intl-open-plan-floor/` | 350 m² commercial floor | 8 radials | C06 server-room Type B 30mA RCD per IEC 60364-5-53:2002+A2:2015 §531.3.3 (matches db-layout intl-dbcomms-data) |
| `us-residential-dwelling/` | ~160 m² single-family | 8 branch circuits | NEC 210.8 GFCI + 210.12 AFCI + 406.12 tamper-resistant + 120/240V split-phase |

**Deferred to v1.1+:** multi-skill intent consumption (consume earthing + fault-level intents); INV-N cross-skill consistency checks. **Deferred to ev-charging skill:** BS 7671 Part 7-722 / NEC 625 EV charging circuits.

## Contribution guide

See `CONTRIBUTING.md` for how to add a new skill, update standards values,
and run the eval suite.
