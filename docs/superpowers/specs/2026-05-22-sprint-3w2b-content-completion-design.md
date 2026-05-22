# Sprint 3-W2b — Content Completion Design

**Date:** 2026-05-22
**Predecessor:** Sprint 3-W2a (Schema Standardisation) — shipped at `f3960cb`, deferred 14 db-layout examples + ~18 code-review minors here.
**Status:** Brainstorm complete; spec for review.

---

## §1 — Locked Decisions

| # | Decision | Choice |
|---|---|---|
| D1 | Sprint scope | Bucket A (db-layout content) + ALL of Bucket B (silent + cosmetic cleanups). Bucket C (Tier-4 lossy) defers to Sprint 3-W2c. |
| D2 | Schema reconciliation for outlier board sub-shape | `oneOf` union with `board.board_kind` discriminator (`main_switchboard` vs `specialty_board`); each kind has its own required-fields contract. Mirrors 3-W2a's eval.schema.json + inputs.schema.json oneOf pattern. |
| D3 | Rationale authoring approach | LLM-generated per example via Opus subagent + 2-stage review (spec compliance + code quality). Matches the proven 3-W2a Task 3 + Task 5 pattern. |
| D4 | Bundling | 3 jurisdictional bundles, KE-first, then UK, then INT. Citation form stays consistent within each bundle; KE precedent established before UK/INT subagents fire. |
| D5 | Bucket B consolidation | Phase C (silent regressions) + Phase D (cosmetic minors) folded into a single Sonnet task — all mechanical edits across multiple files; splitting just adds review overhead. M1 from Task 4 (DRY refactor) deferred to 3-W2c. |

---

## §2 — Scope

### Bucket A — db-layout content (the harness blocker)

Ground truth verified 2026-05-22:

| Category | Count | Files |
|---|---|---|
| Outlier shape with rationale | 4 | `intl-dbcomms-data`, `intl-dbem-emergency-lighting`, `intl-dbgenset-changeover`, `intl-dbups-backed` |
| Outlier shape WITHOUT rationale | 10 | `intl-dbfa1-fire-alarm`, `intl-dbl1-lighting`, `intl-dbm1-mechanical`, `intl-dbp1-power`, `ke-nairobi-gh-db`, `ke-nairobi-industrial-100A-tpn`, `uk-commercial-msb-3storey`, `uk-commercial-sdb-gf`, `uk-commercial-sdb-l1`, `uk-commercial-sdb-l2` |
| Main shape (compliant, untouched) | 6 | `intl-commercial-tpn-msb`, `uk-domestic-consumer-unit`, `us-strip-mall-{common-area,panelboard,tsp-a,tsp-b}` |
| **Total** | **20** | All db-layout examples |

The 14 problem files are ALL outlier-shape. 10 of those also lack a rationale block. The two fixes (schema + rationale) are paired but independently addressable.

### Bucket B — Sprint 3-W2a code-review followups

**Important (silent regressions — Task 3):**
- `electrical/arc-flash/evals/eval-05-jurisdiction-us-with-restricted.yaml:37` and `electrical/arc-flash/evals/eval-08-conservative-t-clear-default.yaml:37` — `ir.flags contains "specialised teams"` / `"Refine via protection coordination"` are free-text substring assertions against a flag-token array. Either always pass (substring incidentally present) or always fail (token-list doesn't carry recommendation text).
- ~6 occurrences of `!= null` placeholder checks in `arc-flash/eval-01/06` + `arc-flash-labelling/eval-06/07` — pass any time the schema does, so they have no signal beyond schema validation.

**Minor — Task 3 (3 items):**
- `arc-flash/eval-09-shock-approach-out-of-range.yaml:36` — `matches "^(790|840)$"` relies on numeric→string coercion. Add explicit comment about runtime assumption.
- `arc-flash-labelling/eval-08a-qr-code-emitted.yaml:20-30` — degenerate per-label coverage; add a `ir.labels[*].label_content_qr_code_url all_equal "..."` cross-cutting check.
- `arc-flash/eval-03-coefficient-fallback-trap.yaml:52,56` — `method_fallback_trail contains "skipped"` / `"applied"` substring matching lacks structural pairing semantics; tighten description.

**Minor — Task 4 (8 items, only the in-scope subset):**
- **M2 (pre-existing bug):** META-SCHEMA-INVALID branch (`scripts/validate-examples.py:105-108`) appends a failure entry but doesn't increment `total_failures`. One-line fix.
- **M3:** unused `label` variable at `scripts/validate-examples.py:173`.
- **M4:** 3× f-strings without interpolation at `scripts/validate-examples.py:283,288,293`.
- **M7:** dead `_archive/` filter at `scripts/validate-examples.py:163-165` (glob is non-recursive so the filter is a no-op).
- **DEFERRED to 3-W2c:** M1 (DRY consolidation of 3 report-formatting blocks — refactor, not bugfix); M5 (cosmetic double-blank-line drift); M6 (type-hint widening); M8 (strip_refs comment).

**Minor — Task 5 CLAUDE.md (5 items):**
- I-3 partial scaffold-only electrical folders list — either enumerate all or replace with "all other `electrical/<skill>/` folders are scaffolds".
- M-2 "across many sprints" already generic — verify no other timestamp leakage remains.
- M-3 / M-4 per-skill folder bullet omits `calculations/`, `annotations/`, `templates/` — extend with "(where applicable)" caveat.
- M-5 deferred-sprint reference is vague — replace with `[[sprint-3w-shipped]]` memory cross-ref.
- M-6 oneOf inputs-schema description duplication — tighten to one phrasing.

### Bucket C — Tier-4 lossy eval conversions (DEFERRED to 3-W2c)

Format C + D files with explicit TODO markers for canonical-grammar gaps. Out of scope here because they need eval-runtime upgrades (OR-clauses, cross-array, per-decision-presence) that the skills repo doesn't ship.

---

## §3 — Phases

### Phase A — Schema reconciliation (Task 1, Sonnet)

**File ops:** 1 schema edit + 20 example board_kind additions = 21 files.

**`electrical/db-layout/schemas/db-layout-ir.schema.json`:**
- Add `board.board_kind` property with `enum: ["main_switchboard", "specialty_board"]`.
- Add root-level `oneOf` clause:
  - `{ required: ["board.board_kind == main_switchboard"] }` → board requires `ways_total, ways_used, ways_spare` (existing required keys).
  - `{ required: ["board.board_kind == specialty_board"] }` → board requires `enclosure_rating, manufacturer_class, scope, role` (the outlier keys).
- JSON Schema Draft-07 doesn't support direct value-discriminator `oneOf`. Implementation pattern: `oneOf: [{ properties: { board: { properties: { board_kind: { const: "main_switchboard" } }, required: [..., "ways_total", "ways_used", "ways_spare"] } } }, { properties: { board: { properties: { board_kind: { const: "specialty_board" } }, required: [..., "enclosure_rating", "manufacturer_class", "scope", "role"] } } }]`.

**Example updates:**
- All 6 main-shape examples: add `"board_kind": "main_switchboard"` to the board object.
- All 14 outlier-shape examples: add `"board_kind": "specialty_board"` to the board object.

**Acceptance after Phase A:** Schema mismatch cleared on all 14 outlier-shape examples. The 4 that already had rationale (`intl-dbcomms-data`, `intl-dbem-emergency-lighting`, `intl-dbgenset-changeover`, `intl-dbups-backed`) now pass cleanly. The remaining 10 still fail on missing rationale (cleared in Phase B). Expected Pass 1: **43/53** (up from 39/53 baseline; +4 from Phase A).

### Phase B — Rationale authoring (Tasks 2-4, Opus, jurisdiction bundles)

Each task dispatches one Opus subagent with: input.json + non-rationale output.json (everything except the rationale block) + db-layout SKILL.md + db-layout/prompts/generator.md + db-layout/prompts/reviewer.md + the canonical 8-section template + per-jurisdiction citation rules.

**Canonical 8 sections** (adapt prose for specialty boards):
1. Board Classification — board_kind + role + IEC 61439-3 manufacturer class + enclosure rating
2. Incoming Supply — fed-from + supply rating + phase arrangement + Ze at origin (if applicable for specialty boards)
3. Busbar / Internal Bus Sizing — busbar rating + (for specialty boards: internal bus topology, isolators)
4. Way Assignment / Functional Scope — circuits assigned + (for specialty boards: functional loads served)
5. OCPD Selection — breaker types + ratings + (for specialty boards: specialty OCPD like fire-alarm-monitored breakers)
6. RCD / Protection Strategy — RCD posture + (for specialty boards: SPDs, EMC filters, monitoring)
7. Cable Selection — phase + CPC + (for specialty boards: cable shielding, segregation)
8. Selectivity / Compliance — verification + standard refs

**Task 2 — KE bundle (2 files):**
- `ke-nairobi-gh-db` + `ke-nairobi-industrial-100A-tpn`
- Citation form: `KS 1700:2018 § X (route to BS 7671 via §313)` for protection; `IEC 61439-3` for enclosure class
- Africa-first per [[build-strategy-breadth-first]]

**Task 3 — UK bundle (4 files):**
- `uk-commercial-msb-3storey` + `uk-commercial-sdb-gf` + `uk-commercial-sdb-l1` + `uk-commercial-sdb-l2`
- Citation form: `BS 7671:2018+A2:2022 § X` + `IEC 61439-3` + `BS EN 60898`/`BS EN 61009` for OCPDs
- Sees KE bundle as precedent

**Task 4 — INT bundle (4 files):**
- `intl-dbfa1-fire-alarm` + `intl-dbl1-lighting` + `intl-dbm1-mechanical` + `intl-dbp1-power`
- Citation form: `IEC 60364-X-XX:YYYY` + `IEC 61439-3` + specialty refs:
  - Fire alarm: `BS 5839-1:2017` (UK), `IEC 60839` (INT) — note: even INT files may reference jurisdiction-specific fire-alarm standards depending on locale
  - Lighting: `IEC 60598-2-22` (emergency lighting)
  - Mechanical: motor-protection refs
  - Power: `IEC 60364-7-7XX` for special locations as relevant
- Sees both KE + UK bundles as precedent

**Acceptance after Phase B:** Pass 1 = 53/53 (full green).

### Phase C — Bucket B cleanup (Task 5, Sonnet, bundled)

**File ops:** ~10 files touched across 3 sub-buckets.

**C-1: Silent regressions (Task 3 Important items):**
- arc-flash eval-05 + eval-08: replace each free-text-substring `ir.flags contains "<sentence>"` assertion with either:
  - (a) the closest token-array semantics (e.g. `ir.flags contains "RESTRICTED_EQUIPMENT_NEAR_LIMIT"` if such a token exists), OR
  - (b) downgrade to `severity: info` + description explicitly states "ALWAYS-PASS placeholder pending flag_messages[] field — see [[sprint-3w2a-shipped]] deferred queue".
- arc-flash/eval-01/06 + arc-flash-labelling/eval-06/07: locate the ~6 `!= null` placeholder assertions; per-occurrence triage:
  - If description has forward intent ("pending word-count operator"): downgrade to `severity: info` + tighten wording.
  - If no forward intent: delete the assertion entirely (schema already enforces presence).

**C-2: Task 3 + Task 4 minors:**
- arc-flash eval-09: add comment on numeric→string coercion assumption.
- arc-flash-labelling eval-08a: add one cross-cutting `all_equal` check on labels.
- arc-flash eval-03: tighten description on method_fallback_trail substring matching.
- `scripts/validate-examples.py`: 4 surgical edits — M2 (add `total_failures += 1` on line 105-108), M3 (remove unused `label` var line 173), M4 (drop `f` prefix on lines 283/288/293), M7 (remove dead `_archive/` filter lines 163-165).

**C-3: Task 5 CLAUDE.md doc polish:**
- 5 minor edits per the items listed in §2 Bucket B → Minor — Task 5.
- Verify no new factual errors (ground-truth check before commit).

**Acceptance:** After Phase C, all silent-regression assertions are either fixed or transparently downgraded; harness Python is cleaner (M2 closes a pre-existing bug); CLAUDE.md is fully accurate.

### Phase D — Final validation + push + memory save (Task 6, Opus)

- Run 3-pass harness: expect **53/53 + 81/81 + 9/9 = AGGREGATE 143/143 exit 0**.
- Verify by independent counts (no Format C/D leftovers, all examples have board_kind, all 10 new rationale blocks have 8 sections + chat_summary 40-500 chars).
- Push to origin/main (no --force, no --no-verify).
- Save `sprint-3w2b-shipped.md` memory file under `/Users/linus/.claude/projects/-Users-linus-Desktop-DraftsMan-SKills-draftsman-skills/memory/`.
- Update `MEMORY.md` index entry.

---

## §4 — File Operations Summary

| Phase | Files modified | Files created |
|---|---|---|
| A — Schema reconciliation | 1 schema + 20 example output.json | 0 |
| B — Rationale authoring (10 files) | 0 | 10 (added rationale blocks; or modified output.json — implementation detail) |
| C — Bucket B cleanup | ~14 (arc-flash + arc-flash-labelling evals + scripts/validate-examples.py + CLAUDE.md) | 0 |
| D — Validation + push | 0 | 1 memory file + 1 index update |
| **Total** | **~35 file ops** | |

Comparable to Sprint 3-W2a (~50 ops). 1-2 dev day budget.

---

## §5 — Risks & Mitigations

- **R1 — Rationale-authoring quality drift.** LLM may invent clause refs or diversity factors. *Mitigation:* spec compliance reviewer verifies every citation against `shared/standards/`; code quality reviewer checks engineering soundness; if a citation can't be verified, downgrade to descriptive language without false attribution.

- **R2 — Schema oneOf regression.** Adding the discriminator could reject the 6 main-shape examples if the schema is mis-authored. *Mitigation:* Task 1 explicit verification — all 20 examples must pass after schema + board_kind additions; halt if any of the 6 main fail.

- **R3 — JSON Schema Draft-07 oneOf value-discriminator limitation.** Draft-07 doesn't natively support "if value of X is Y then require Z" patterns; we use the `oneOf: [{ properties: { board: { properties: { board_kind: { const: ... } }, required: [...] } } }, ...]` pattern. *Mitigation:* Task 1 implementer verifies the pattern works by running a positive + negative test (one valid example of each kind + one cross-shape example that should fail).

- **R4 — KE specialty board categorisation.** Both KE examples are outlier-shape (verified). Confirm during Task 2 dispatch that the KE board_kind is `specialty_board` (not `main_switchboard`). *Mitigation:* Task 1 explicit ground-truth check — list which examples got which board_kind annotation before commit.

- **R5 — Silent-regression downgrade vs delete decision.** Per-assertion judgment call. *Mitigation:* Task 5 prompt makes the decision explicit (description-has-forward-intent → downgrade; no-forward-intent → delete). Document each choice in the commit message.

- **R6 — Bundle cross-pollination.** UK + INT subagents working from different inputs might produce inconsistent prose style. *Mitigation:* All 3 rationale tasks share the same 8-section template + db-layout SKILL/generator/reviewer context. Tasks dispatched sequentially (KE → UK → INT) so later bundles see earlier output as precedent.

- **R7 — CLAUDE.md polish factual drift.** Last-mile doc edits could re-introduce stale references. *Mitigation:* Task 5 prompt includes a ground-truth verification step (mirror the lesson from 3-W2a Task 5 fix).

- **R8 — Cumulative file-op count drift.** Estimated 35 ops but Phase B Opus dispatches may grow files beyond just `rationale` (e.g. fix related drift discovered during authoring). *Mitigation:* explicit scope guard — rationale authoring tasks may ONLY add the `rationale` block + adjust output.json fields that the schema validation surfaces; any other discovered drift is flagged in DONE_WITH_CONCERNS but deferred.

---

## §6 — Acceptance Criteria

1. **Harness aggregate:** `python3 scripts/validate-examples.py` exit 0.
   - Pass 1 (examples): **53/53** (full green; 14 db-layout failures cleared)
   - Pass 2 (evals): **81/81** (unchanged from 3-W2a)
   - Pass 3 (inputs.json): **9/9** (unchanged from 3-W2a)

2. **Schema correctness:**
   - All 20 db-layout examples carry `board.board_kind` (6 `main_switchboard` + 14 `specialty_board`)
   - `db-layout-ir.schema.json` oneOf enforces per-kind required fields
   - Cross-shape example (`board_kind: main_switchboard` + outlier keys) FAILS schema validation — verified by negative test

3. **Rationale completeness (10 files):**
   - Each has `rationale.chat_summary` 40-500 chars
   - Each has `rationale.sections[]` length ≥ 1 (canonical: 8 sections)
   - Section titles follow the 8-section template (adapted for specialty boards)
   - Citation form correct per jurisdiction (KE / UK / INT) — verified by spec reviewer against `shared/standards/`

4. **Bucket B closed:**
   - Zero `ir.flags contains "<full-sentence>"` style assertions remain in arc-flash family
   - All `!= null` placeholders either deleted or carry explicit "ALWAYS-PASS placeholder" wording
   - `scripts/validate-examples.py` has M2 (META-SCHEMA-INVALID counter), M3 (unused var), M4 (f-string), M7 (dead filter) all closed
   - `CLAUDE.md` polish — 5 minor items closed

5. **Memory:**
   - `sprint-3w2b-shipped.md` written
   - `MEMORY.md` index updated
   - Deferred queue moved forward (Bucket C → Sprint 3-W2c)

6. **Git:**
   - Push to origin/main without --force or --no-verify
   - 6 task commits + 2 doc commits (this spec + the upcoming plan)
   - Single session execution

---

## §7 — Out-of-Scope Handoff to Sprint 3-W2c

- **Tier-4 lossy eval conversions** (Bucket C): Format C TODO items in db-layout/eval-03 (any_one_of_must_be_true), db-layout/eval-08 + fault-level/eval-09 (cross_skill_compatibility_check), earthing/eval-04 (no_invented_values); Format D TODO items in arc-flash eval-03 (array-of-objects predicate), arc-flash eval-09 (per-node flag scoping), arc-flash-labelling eval-06 / arc-flash eval-06 (per-decision multi-field presence). All require eval-runtime upgrades to support OR-clauses / cross-array / per-decision-presence semantics.
- **Task 4 M1 (DRY refactor)**: Consolidate the 3 near-identical report-formatting blocks in `scripts/validate-examples.py` into a `format_results()` helper. Refactor — not a bugfix — so it belongs in a polish-focused sprint.
- **Task 4 M5/M6/M8**: Cosmetic + type-hint widening + strip_refs comment. Polish-only.

---

## §8 — Model Selection

Per `[[feedback-no-haiku-sonnet-opus-only]]`:
- **Sonnet** — Task 1 (mechanical schema + 20 example board_kind additions), Task 5 (mechanical Bucket B cleanup edits).
- **Opus** — Tasks 2/3/4 (judgment-heavy rationale authoring per jurisdiction), Task 6 (ship-readiness judgment + memory authoring).

Total: 6 tasks. 4 Opus + 2 Sonnet.

---

## §9 — Sprint Workflow

Standard pattern per [[sprint-3w2a-shipped]]:
1. Spec (this doc) approved by user
2. Plan authored via `superpowers:writing-plans` → `docs/superpowers/plans/2026-05-22-sprint-3w2b-content-completion-sprint.md`
3. Execute via `superpowers:subagent-driven-development`, 2-stage review per task (spec compliance → code quality), continuous execution
4. Memory save on ship; index updated; Sprint 3-W2c queued

---

## Cross-references

- [[sprint-3w-shipped]] — predecessor; surfaced the 14 db-layout failures and the Bucket B items
- [[sprint-3w2a-shipped]] — predecessor; schema standardisation, Bucket B items originate here
- [[runtime-project-boundary]] — skills repo ships contracts; runtime executes
- [[feedback-no-haiku-sonnet-opus-only]] — model rules
- [[build-strategy-breadth-first]] — Africa-first sequencing for KE bundle
