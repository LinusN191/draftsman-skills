# Sprint 3-W2a — Schema Standardisation — Design Spec

**Date:** 2026-05-21
**Status:** Approved — ready for implementation plan
**Sprint target:** Formalise the eval + inputs schema conventions that emerged across recent skill work. Harmonise the 80 existing eval YAMLs to a single key-name convention without changing semantics. Extend the golden CI gate. Replace stale CLAUDE.md with a full revision.

---

## 0. Context

Sprint 3-W shipped the golden-example schema validation harness. A subsequent comprehensive audit surfaced 18 gap classes across the skills repo, spanning eval format fragmentation, missing assets, schema-vs-example drift, doc drift, and stub content. User decision 2026-05-21: split the cleanup into 3 focused sub-sprints rather than one comprehensive sprint:

- **3-W2a (this spec)** — Schema standardisation: eval + inputs schemas, harness extension, CLAUDE.md revision
- **3-W2b (later)** — Content completion: lighting-layout assets/validator/reviewer, db-layout rationale + board sub-shape, missing standards files, compliance_failure eval coverage
- **3-W2c (later)** — Quality polish: earthing intent shape fix, db-layout-rollup example, calc contract completions, shared file path resolution

3-W2a is sequenced first because the schema work unblocks the eval + content authoring in 3-W2b — those tasks need a canonical schema to validate against.

---

## 1. Scope decisions (locked via brainstorming dialogue 2026-05-21)

| Decision | Choice |
|---|---|
| Sprint packaging | Split into 3 sub-sprints; 3-W2a covers schema work only |
| Eval format strategy | Formalise emerged conventions in `eval.schema.json` — accept `input` OR `input_fixtures[]`; extend category enum from 5 to 9 (add `validation_trap`, `rationale_block`, `jurisdiction_switch`, `missing_input`) |
| inputs.json strategy | Create canonical `shared/schemas/core/inputs.schema.json` accepting all 3 emerged shapes (`items[]`, `inputs[]`, `input_groups[]`) via `oneOf`; zero file migration |
| Harness coverage | Extend `scripts/validate-examples.py` to validate `*/evals/*.yaml` + `*/inputs.json` against the new schemas; CI gate broadens |
| CLAUDE.md depth | Full revision documenting actual folder structure + sprint workflow + model rules + CI gate (~150-200 lines) |

---

## 2. Gap inventory addressed by 3-W2a (vs deferred)

### Addressed in 3-W2a

| Gap class | Count | Phase |
|---|---|---|
| Eval format fragmentation (Format C: `id`/`inputs`/`assertions`) | 23 evals | B |
| Eval format fragmentation (Format D: `eval_id`/`expected`) | 17 evals | B |
| Eval truly missing input (arc-flash-labelling/eval-08) | 1 eval | B |
| Invalid category values in eval YAMLs | 31 evals | A (schema enum extension formalises them) |
| inputs.json key inconsistency across skills | 9 files | A (canonical schema accepts all 3) |
| CLAUDE.md describes wrong structure | 1 doc | D |
| Golden harness doesn't validate evals/inputs | 1 script | C |

### Deferred to 3-W2b (Content Completion)

- lighting-layout `assets/` directory (3 missing markdown files)
- lighting-layout validator + reviewer stubs (full content authoring)
- lighting-layout manifest 6 broken refs
- db-layout 10 missing rationale blocks
- db-layout 4 board sub-shape reconciliation
- 8 new `compliance_failure` evals (one per beta skill)
- 10 missing standards files referenced in prompts

### Deferred to 3-W2c (Quality Polish)

- Earthing intent shape fix (4 missing required fields × 5 examples)
- db-layout-rollup intent example
- 10 shared calculation contract completions
- 70+ shared file unresolvable paths (filename-only references)

---

## 3. Phases

### Phase A — Schema authoring (Task 1)

**Files:**
- Modify: `shared/schemas/core/eval.schema.json`
- Create: `shared/schemas/core/inputs.schema.json`

**eval.schema.json updates:**

1. `required` array: change from `["name", "skill", "input", "checks"]` to `["name", "skill", "checks"]`. Make `input`/`input_fixtures` mutually-optional via `oneOf` at the schema root.
2. Add `oneOf` constraint requiring exactly one of: `{required: ["input"]}` or `{required: ["input_fixtures"]}`.
3. Define `properties.input_fixtures` as `{type: array, minItems: 1, items: {type: string}}` — array of paths relative to the eval file.
4. Extend `properties.category.enum` from 5 values to 9:
   - Existing: `happy_path`, `edge_case`, `compliance_failure`, `cross_validation`, `skill_specific`
   - Add: `validation_trap`, `rationale_block`, `jurisdiction_switch`, `missing_input`

**inputs.schema.json (NEW):**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "shared/schemas/core/inputs.schema.json",
  "title": "Skill inputs.json — canonical (accepts items / inputs / input_groups conventions)",
  "type": "object",
  "required": ["skill"],
  "additionalProperties": true,
  "properties": {
    "skill":   { "type": "string" },
    "version": { "type": "string" },
    "$schema": { "type": "string" }
  },
  "oneOf": [
    { "required": ["items"], "properties": { "items": { "type": "array", "minItems": 0 } } },
    { "required": ["inputs"], "properties": { "inputs": { "type": "array", "minItems": 0 } } },
    { "required": ["input_groups"], "properties": { "input_groups": { "type": "array", "minItems": 0 } } }
  ]
}
```

The schema is intentionally permissive on the inner item shape — each skill's inputs.json may carry domain-specific fields. The contract is "use one of the 3 emerged top-level shapes"; the runtime/UI consumes the right one based on which key is present.

### Phase B — Eval migration (Tasks 2 + 3)

#### Task 2 — Format C migration (db-layout + fault-level, 23 evals)

Mechanical key rename per file. Semantics unchanged.

| Old key | New key | Notes |
|---|---|---|
| `id` | `name` | preserve value string |
| `inputs` | `input` (if data is inline) OR `input_fixtures` (if it references example files via path) | adjudicate per file |
| `assertions` | `checks` | preserve array; each check entry preserves its shape |

Per-file dispatch decision: read the existing `inputs` value. If it's inline data (a dict), rename to `input`. If it's an array of path strings or a single path string, rename to `input_fixtures` and wrap in array if needed.

Add `skill` field if missing (older Format C files may omit it; required by canonical schema).

#### Task 3 — Format D migration (arc-flash + arc-flash-labelling, 17 evals)

Mechanical key rename per file. Plus structural fix for the 1 truly-no-input eval.

| Old key | New key | Notes |
|---|---|---|
| `eval_id` | `name` | preserve value string |
| `expected` | `checks` | requires per-entry transformation if `expected` is a single dict — convert to `[{assertion, description, severity}]` form |

Plus: `arc-flash-labelling/evals/eval-08-qr-code-conditional-emission.yaml` currently has no `input`/`input_fixtures`/`inputs` field. Add `input_fixtures: ["../examples/<best-match>/output.json"]` pointing at the most appropriate existing example.

### Phase C — Harness extension (Task 4)

**File:** `scripts/validate-examples.py`

Extend the existing harness to perform 3 validation passes instead of 1:

1. **Examples pass (existing)**: validate every `*/examples/*/output.json` against the skill's IR schema
2. **Evals pass (NEW)**: load `shared/schemas/core/eval.schema.json`; validate every `*/evals/*.yaml` (except `runner-config.yaml`) against it
3. **Inputs pass (NEW)**: load `shared/schemas/core/inputs.schema.json`; validate every `*/inputs.json` against it

Each pass produces its own per-skill report block. Total line summarises all 3 passes: `examples N/M, evals N/M, inputs N/M`. Exit 0 only if ALL 3 pass; exit 1 on any failure.

Reuse the existing `strip_refs()` helper. New YAML loading via `yaml.safe_load`; jsonschema validation identical.

### Phase D — CLAUDE.md revision (Task 5)

**File:** `CLAUDE.md`

Full revision (~150-200 lines). Replaces stale content. Sections:

1. **What this repo is** — open-source MEP engineering skills for AI agents
2. **Actual skill folder structure**:
   ```
   electrical/<skill-name>/
   ├── README.md                        — skill overview
   ├── CHANGELOG.md                     — semver history
   ├── skill.manifest.json              — declares standards/calc/ontology refs + consumes_intents + produces_intent
   ├── inputs.json                      — input contract (items/inputs/input_groups per shared/schemas/core/inputs.schema.json)
   ├── schemas/
   │   ├── <skill>-ir.schema.json       — IR shape contract
   │   └── <skill>-intent.schema.json   — slim downstream intent shape
   ├── prompts/
   │   ├── generator.md                 — N-step engineering reasoning chain
   │   ├── validator.md                 — INV-N hard-fail checks
   │   └── reviewer.md                  — D-N engineering judgement checks
   ├── examples/<name>/
   │   ├── input.json
   │   ├── output.json                  — full IR
   │   ├── intent-out.json              — slim intent
   │   └── reasoning.md                 — 8-section narrative
   ├── evals/*.yaml                     — see shared/schemas/core/eval.schema.json
   ├── ontology/*.json
   ├── rules/*.yaml
   ├── constraints/*.yaml
   ├── validation/*.yaml
   └── docs/{engineering-philosophy,known-limitations}.md
   ```
3. **Sprint workflow** — every non-trivial change follows brainstorm → spec → plan → subagent-driven execution → golden CI gate. Specs live in `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`; plans live in `docs/superpowers/plans/YYYY-MM-DD-<topic>-sprint.md`.
4. **Model rules** — Sonnet for mechanical work, Opus for engineering judgement, NEVER Haiku. Sub-agent dispatches obey this.
5. **Citation form rigour per jurisdiction** — GB: `BS 7671:2018+A2:2022 §X`; KE: `KS 1700:2018 §X routes to BS 7671:2018+A2:2022 §Y` (NEVER bare BS 7671 as primary, NEVER `"adopted by KS 1700"` annotation); INT: `IEC 60364-X-XX:YYYY §Z`; US: `NEC 2023 Article X`.
6. **Cross-skill intent consumption** — leaf vs hybrid vs hard-require patterns; reference small-power v1.0→v1.1 + SLD v1.3→v1.4 + cable-sizing v1.0 as precedents.
7. **Golden CI gate** — every PR runs `python3 scripts/validate-examples.py` covering 3 passes (examples + evals + inputs). PRs cannot merge with harness FAIL.
8. **WI conventions** — WI2 rationale block (8 sections + chat_summary 40-500), WI3 tool-call deferral, WI5 eval categories.
9. **Standards to apply** — BS 7671:2018+A2:2022, BS EN 12464-1:2021, BS EN 60617, BS 1192/ISO 19650, etc.
10. **Never do** — don't ship stubs, don't skip evals, don't invent standards values, don't bypass CI.

Removes the stale `SKILL.md`/`EVALS.md`/`EXAMPLES.md` references. Doesn't include sprint-specific history (that's in memory files + `docs/superpowers/specs+plans/`).

### Phase E — Final validation + push (Task 6)

**Acceptance criteria (verified by extended harness):**

1. 53/53 examples pass IR schema validation
2. 80/80 evals pass eval.schema.json validation (after Format C + D migrations)
3. 9/9 inputs.json pass inputs.schema.json validation
4. `python3 scripts/validate-examples.py` exit 0
5. CI workflow run on the push passes

Push 5 atomic commits (one per Phase A-D + the final harness verification commit if needed) to origin/main.

Save sprint memory file at `/Users/linus/.claude/projects/-Users-linus-Desktop-DraftsMan-SKills-draftsman-skills/memory/sprint-3w2a-shipped.md`.

---

## 4. File-ops summary

| Phase | Files | Effort |
|---|---|---|
| A — Schema authoring | 1 modified (eval.schema.json), 1 new (inputs.schema.json) | 2 hr |
| B Task 2 — Format C migration | 23 eval YAMLs (db-layout + fault-level) | 2-3 hr |
| B Task 3 — Format D migration | 17 eval YAMLs (arc-flash + arc-flash-labelling) + 1 no-input fix | 2-3 hr |
| C — Harness extension | 1 modified (validate-examples.py) | 1 hr |
| D — CLAUDE.md revision | 1 modified (CLAUDE.md) | 1-2 hr |
| E — Final validation + push | 0 file changes | 30 min |

**Total: ~44 file ops; ~1.5 dev days.**

---

## 5. Risks + mitigations

| Risk | Mitigation |
|---|---|
| `eval.schema.json` `oneOf` for input/input_fixtures fails strict Draft-07 in odd ways | Test the updated schema by re-running golden harness on all 80 existing evals after Task 1 lands; any false positives surface immediately |
| Format C migration changes data shape accidentally | Each migration is mechanical key-rename only; per-file diff inspection during review; CI gate confirms semantics preserved |
| Format D `expected` → `checks` transformation drops assertion grammar | Per-file review of the assertion structure; preserve the inner `description`/`severity` keys; only rename outer wrapper |
| inputs.schema.json `oneOf` accepts garbage that breaks the runtime | Schema includes `additionalProperties: true` on common metadata fields (skill, version, $schema); strict `oneOf` on the data-shape key prevents arbitrary keys at that level. Runtime tested implicitly when CI runs against the 9 existing inputs.json files. |
| CLAUDE.md revision drifts from current practice | Cap at 200 lines; cite sprint-history specs/plans (`docs/superpowers/specs/`) for detail rather than inlining. Cross-references stay current via path stability. |
| Harness Python complexity grows | Each new pass reuses `strip_refs + jsonschema.validate` — total addition ~30 LoC. Each pass produces its own report block; per-pass exit code aggregation at the end. |
| Format E eval (arc-flash-labelling/eval-08) doesn't have an obvious matching example | Inspect available examples in `electrical/arc-flash-labelling/examples/`; pick the one that best matches the QR-code conditional-emission scenario (likely `us-ansi-label-set` if it carries a QR code field, otherwise add `input_fixtures` pointing at the closest match + a TODO note in the eval description) |

---

## 6. Out-of-scope handoffs (explicit)

| Item | Sprint | Reason |
|---|---|---|
| lighting-layout `assets/` directory | 3-W2b | Content authoring (BS EN 12464 lux targets + UF/MF tables + Part L controls) — engineering content work, not schema work |
| lighting-layout validator + reviewer (currently 4-line stubs) | 3-W2b | Substantial prompt authoring (~150 + 100 lines each); matches the pattern of the reference skill's generator |
| lighting-layout manifest 6 missing refs | 3-W2b | Each broken ref needs an ontology/standards file authored — engineering content |
| db-layout 10 missing rationale blocks | 3-W2b | Engineering reasoning authoring per example |
| db-layout 4 board sub-shape reconciliation | 3-W2b | Schema decision + per-example migration after the decision |
| 8 new `compliance_failure` evals | 3-W2b | Eval authoring with realistic engineering scenarios — one per beta skill |
| 10 missing standards files in prompts | 3-W2b | Standards-layer content authoring |
| Earthing intent shape fix | 3-W2c | Either schema relaxation OR migrate 5 example intent-out.json files |
| db-layout-rollup intent example | 3-W2c | Author one worked example of a multi-board rollup |
| 10 shared calculation contract completions | 3-W2c | Add description/outputs/formula fields per contract — math content authoring |
| 70+ shared file unresolvable paths | 3-W2c | Add a path resolution manifest OR audit prompts to add full paths |

---

## 7. Acceptance criteria

1. `shared/schemas/core/eval.schema.json` accepts `input` OR `input_fixtures[]`; category enum has 9 values
2. `shared/schemas/core/inputs.schema.json` shipped, accepts `items` / `inputs` / `input_groups` shapes via `oneOf`
3. All 80 existing eval YAMLs validate against the updated eval.schema.json (no semantics change; only Format C + D key renames applied)
4. All 9 existing inputs.json files validate against the new inputs.schema.json (no file changes needed; schema accepts current shapes)
5. `scripts/validate-examples.py` runs 3 passes (examples + evals + inputs); reports per-pass totals; exits 0 only if ALL pass
6. CLAUDE.md describes actual folder structure + brainstorm/spec/plan/subagent workflow + model rules + golden CI gate
7. Single push to origin/main containing 5 atomic commits (one per Phase A-E)

---

## 8. Approval

Approved by user 2026-05-21 via brainstorming dialogue. Five scoping decisions locked:

1. Split Sprint 3-W2 into 3 sub-sprints (3-W2a now; 3-W2b + 3-W2c to follow)
2. Eval format: formalise emerged conventions (accept input OR input_fixtures; 9-value category enum)
3. inputs.json: canonical schema accepting all 3 emerged shapes (zero file migration)
4. Golden harness: extend to validate evals + inputs.json (3 passes total)
5. CLAUDE.md: full revision documenting structure + workflow + rules

Next step: invoke `superpowers:writing-plans` to produce `docs/superpowers/plans/2026-05-21-sprint-3w2a-schema-standardisation.md`.
