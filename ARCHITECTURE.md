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

## Contribution guide

See `CONTRIBUTING.md` for how to add a new skill, update standards values,
and run the eval suite.
