# Skill-Author Bug Fix Sprint — Sprint 3-W Design Spec

**Date:** 2026-05-20
**Status:** Approved — ready for implementation plan
**Sprint target:** Clear all skill-author bugs surfaced by Sprint 3-V runtime E2E testing + ship golden-example schema validation as permanent CI gate.

---

## 0. Context

Sprint 3-V (runtime team) ran three full E2E tests against Anthropic (`claude-sonnet-4-6` generator + `claude-opus-4-7` reviewer) against the lighting-layout, db-layout, and earthing skills. The infrastructure passed cleanly (key resolution, tool dispatch, multi-turn loop, schema retry, max_tokens=16384). What blocked validator + reviewer from running was a class of skill-author bugs the LLM cannot fix in 3 retries:

| Skill | Bug class | Root cause |
|---|---|---|
| lighting-layout | `zones[].zone_id` required but Claude emits `id` | prompt-vs-schema mismatch |
| lighting-layout | `circuit_id` required on every luminaire but Claude omits | prompt-vs-schema mismatch |
| lighting-layout | `luminaire_type.initial_lumens` type mismatch | prompt-vs-schema |
| db-layout | `jurisdiction` required at top level but Claude omits | prompt-vs-schema |
| db-layout | `drawn_as_symbols[]` schema expects strings, Claude emits richer objects | schema too tight |
| db-layout | `rationale.*.summary` exceeded the 400-char cap 3× | shared schema cap too tight |
| earthing | hit credit exhaustion before completion | N/A |

A separate golden-example schema validation harness run against the full skills repo surfaced a second class of bugs the LLM never sees because the example files themselves don't satisfy the skill's schema:

| Skill | Failures | Root cause |
|---|---|---|
| db-layout | 14 examples missing required `incoming` field | schema requires OLD shape (`incoming` + `busbar` + `selectivity_results`); 14/20 examples use NEW shape (`incoming_supply` + `main_switch` + `selectivity_results` + `spare_ways`). Schema drifted behind examples. |
| db-layout | 1 example uses `severity: 'high'` | enum is `['critical', 'warning', 'info']` |
| earthing | 2 examples use `supply_bond_type` values not in enum | examples use `'tn_c_s_pen'` and `'utility_pen_bond'`; schema enum is `['dno_pme_bond', 'consumer_electrode_only', 'tn_s_separate_pe']` |

The runtime team's architectural recommendation: golden-validation belongs in skills-repo CI ("pays for itself in 5 minutes"). This sprint adopts that recommendation and pairs it with the surgical schema/example/prompt fixes the bug list requires.

---

## 1. Scope decisions (locked via brainstorming dialogue 2026-05-20)

| Decision | Choice |
|---|---|
| Sprint scope | Full Sprint 3-W — schema/example fixes **AND** prompt-vs-example fixes **AND** golden CI |
| db-layout canonical shape | NEW shape (`incoming_supply` + `main_switch` + `selectivity_results` + `spare_ways`); migrate the 6 OLD-shape examples forward |
| earthing enum direction | Migrate 2 example values to existing 3-value enum; do not extend |
| Shared rationale summary maxLength | Bump from 400 → 800 (one-line edit in `shared/schemas/core/rationale.schema.json`) |
| Golden harness packaging | `scripts/validate-examples.py` + `.github/workflows/validate-examples.yml` CI gate |

---

## 2. Phases

### Phase A — Golden harness CI (foundation)

Ships first so every subsequent fix is verified by a single command + automatically gated on PRs.

**New files:**

- `scripts/validate-examples.py` — recursive `$ref` stripping + per-skill iteration + per-example pass/fail report. Reusable script wrapping the inline harness that surfaced the original 17 failures. Returns exit code 0 on full pass, 1 on any failure, prints per-skill summary table.
- `.github/workflows/validate-examples.yml` — runs `python3 scripts/validate-examples.py` on every push + every PR to main. Fails the build on any harness FAIL.

Acceptance: green CI run against current main confirms 36/53 pass baseline; the same script will rerun after each subsequent phase to verify the failure count drops.

### Phase B — db-layout schema migration

**Schema change** (`electrical/db-layout/schemas/db-layout-ir.schema.json`):

- Top-level `required` array: drop `"incoming"`, `"busbar"`; add `"incoming_supply"`, `"main_switch"`, `"spare_ways"`. Keep `"selectivity_results"` (used by both shapes).
- Define proper `properties.incoming_supply`, `properties.main_switch`, `properties.spare_ways` blocks. The exact shape is whatever the 14 NEW-shape examples carry — read one of them (e.g., `intl-dbcomms-data/output.json`) to extract the canonical sub-shape and lift into the schema.
- Drop `properties.incoming` and `properties.busbar` from the schema (OLD shape's properties no longer needed).
- `drawn_as_symbols[]` items: relax from `{type: string, pattern: ^[A-Z][A-Z0-9_]*$}` to `{oneOf: [{type: string, pattern: ^[A-Z][A-Z0-9_]*$}, {type: object}]}` so Claude's richer object emissions are accepted.

**Example migrations — 6 OLD-shape examples**:

1. `uk-domestic-consumer-unit`
2. `us-strip-mall-common-area` (also fixes the `severity: 'high'` → `'warning'` bug found by the harness)
3. `us-strip-mall-panelboard`
4. `us-strip-mall-tsp-a`
5. `us-strip-mall-tsp-b`
6. `intl-commercial-tpn-msb`

**Migration mechanic per example:**

- Existing `incoming` block → `incoming_supply` (cable/feeder description: csa, length, system_type, declared_pscc_ka, voltage_v, etc.) + `main_switch` (the OCPD device at the incomer: type, rating_a, icu_ka, switched_poles)
- Compute `spare_ways = total_ways - len(circuits)` from existing board.total_ways config (most examples carry total_ways)
- Delete `busbar` block; rating/info either folded into `main_switch` (busbar_rating_a) or dropped if redundant with circuit ratings
- `selectivity_results` block stays as-is

**Prompt updates** (`electrical/db-layout/prompts/generator.md`):

- Add explicit "Top-level required fields you MUST emit" reminder listing `jurisdiction` alongside the other top-level required fields. Today the prompt structures the IR around board/circuits and Claude omits jurisdiction.
- Update step content describing the IR shape to reference `incoming_supply` + `main_switch` + `spare_ways` (the new canonical shape).

**Acceptance:** harness passes 20/20 db-layout examples after Phase B.

### Phase C — earthing enum fix

**Example migrations only — schema stays put:**

- `electrical/earthing/examples/uk-commercial-3storey/output.json`: `met.supply_bond_type: "tn_c_s_pen"` → `"dno_pme_bond"`. Both terms describe TN-C-S/PME at the cut-out; the canonical taxonomy uses `dno_pme_bond`.
- `electrical/earthing/examples/intl-rural-tt/output.json`: `met.supply_bond_type: "utility_pen_bond"` → `"consumer_electrode_only"`. The example's filename and engineering scenario both indicate a TT system; TT systems by definition do NOT have a utility bond, so the original value was a terminology mistake. `consumer_electrode_only` is the correct TT taxonomy.

**Acceptance:** harness passes 5/5 earthing examples after Phase C.

### Phase D — lighting-layout prompt fixes (runtime-only bugs)

**No schema or example changes** — golden harness already passes lighting-layout 3/3. The bugs are prompt-vs-runtime-output: Claude emits `id` where examples have `zone_id`, omits `circuit_id` on luminaires where examples carry it, and gets `initial_lumens` type wrong.

**Prompt updates** (`electrical/lighting-layout/prompts/generator.md`):

- Add a "Field-name precision" note explicit that `zones[]` items use `zone_id` (NOT `id`). The 3 existing examples already use `zone_id` — confirm by Read and cite the example contracts in the prompt.
- Add a sub-step in the layout step instructing that every entry in `luminaires[]` MUST carry `circuit_id` referencing the parent zone/circuit. Confirm against the examples.
- Add a type-precision note for `luminaire_type.initial_lumens`. Read the existing schema entry — if `type: integer`, the prompt should say "integer lumens, not float"; if `type: number`, the prompt should say "lumens as a number, e.g. 4200 or 4200.0 both acceptable". Whichever matches the schema, document it in the prompt.

**Acceptance:** prompt now explicitly forbids the bug patterns the runtime team observed. We can't verify the fix without rerunning Anthropic — that's a runtime-team action — but the prompt change is necessary regardless.

### Phase E — Shared rationale schema maxLength bump

**One-line schema change** (`shared/schemas/core/rationale.schema.json`):

- `definitions.Section.properties.summary.maxLength`: `400` → `800`

Affects 9 skills using the rationale `$ref` (lighting-layout + sld + db-layout + earthing + fault-level + arc-flash + arc-flash-labelling + small-power + cable-sizing). All currently-shipped examples have summaries well under 400 (we've been disciplined writing them), so no example breaks. Future Claude outputs get 2× headroom. The chat_summary cap (currently 500 chars at the top of rationale) is NOT changed — that controls the inline chat-thread summary length and 500 remains appropriate there.

**Acceptance:** harness still passes all 53 examples after the bump.

### Phase F — Re-run golden harness + push

Run `python3 scripts/validate-examples.py` against the full repo. Expected end state: **53/53 examples pass** (was 36/53 baseline).

Commit cadence: one atomic commit per phase. Push at the end of Phase F.

---

## 3. File-ops summary

| Phase | Files | Effort |
|---|---|---|
| A — Golden CI | 2 new (`scripts/validate-examples.py` + `.github/workflows/validate-examples.yml`) | 1 hr |
| B — db-layout | 8 modified (1 schema + 6 examples + 1 prompt) | 3-4 hr |
| C — earthing | 2 modified (2 examples) | 30 min |
| D — lighting-layout | 1 modified (1 prompt) | 1 hr |
| E — Shared rationale | 1 modified (1 schema) | 5 min |
| F — Validation + push | 0 | 30 min |

**Total: ~6-7 hours / 1 dev day. 12 modifications + 2 new files = 14 file ops.**

---

## 4. Out of scope (deferred)

- **LLM-vs-golden diff harness** — a harness that runs each skill's generator prompt against examples/<x>/input.json and diffs the Claude output against examples/<x>/output.json. Would systematically catch prompt-vs-schema mismatches (the class of bug Phase D guesses at). Defer to **Sprint 3-X** — it needs an LLM key budget and is independent of these surgical fixes.
- **Sprint 3-V E2E re-run** against Anthropic with these fixes applied — runtime-team action, not a skills-repo action. They'll re-run after this sprint merges.
- **`max_tokens` default in the Anthropic client** — backend territory per the runtime team's note. Not a skills-repo change.
- **Wiring the 6 unwired skills** (mechanical/plumbing/etc. that are stubs) — separate sprint (call it 3-W2) if/when the runtime team wants more skills active. Out of scope for the bug-fix sprint.

---

## 5. Risks + mitigations

| Risk | Mitigation |
|---|---|
| Phase B schema migration breaks the 6 OLD-shape examples' rationale narrative (rationale.md may reference the OLD field names) | Each example migration must also update its reasoning.md if those files reference `incoming` or `busbar` fields by name. The harness only validates output.json, so reasoning.md drift must be manually verified during the migration. |
| Phase B `drawn_as_symbols` `oneOf` relaxation accidentally accepts garbage | The `oneOf` includes the original strict string-with-pattern variant first, then a permissive object variant. Most consumers should still emit strings; the object variant is a relief valve for runtime use. |
| Phase D prompt edits introduce new mismatches | All 3 fixes are additive (explicit reminders + cross-references to existing example file paths). No example or schema content changes. Worst case: the new reminders are slightly verbose. |
| Phase E maxLength bump propagates to skills that weren't tested | Tested by re-running the harness after Phase E. All existing examples have summaries <400 chars, so no example breaks. Future Claude outputs are the only thing that changes. |
| Golden harness false positives on legitimate `$ref` chains | The harness recursively strips `$ref` to `{type: object}` before validation. This is conservative — it means the harness can't catch bugs INSIDE referenced sub-schemas (rationale, intent-out, etc.). That's acceptable for case-1 bug detection; case-2 needs the LLM diff harness in 3-X. |

---

## 6. Acceptance criteria

1. `python3 scripts/validate-examples.py` returns exit 0 (53/53 pass)
2. `.github/workflows/validate-examples.yml` CI gate runs on next PR and passes
3. db-layout schema describes the NEW shape; all 20 db-layout examples align
4. earthing supply_bond_type values match the 3-value enum across all 5 examples
5. lighting-layout generator prompt explicitly names `zone_id`, `circuit_id`, and `initial_lumens` type
6. `shared/schemas/core/rationale.schema.json` `definitions.Section.properties.summary.maxLength == 800`
7. Single push to origin/main containing 6 atomic commits (one per phase A-E plus a final F push)

---

## 7. Approval

Approved by user 2026-05-20 via brainstorming dialogue. Five scoping decisions locked:

1. Full Sprint 3-W scope (schema + example + prompt + rationale + CI)
2. db-layout NEW shape canonical (`incoming_supply` + `main_switch` + `spare_ways`); 6 OLD-shape examples migrate forward
3. earthing example migrations to existing 3-value enum
4. Shared rationale `sections[].summary` maxLength bump 400 → 800
5. Golden harness ships as script + GitHub Actions CI workflow

Next step: invoke `superpowers:writing-plans` to produce `docs/superpowers/plans/2026-05-20-skill-author-bug-fix-sprint.md`.
