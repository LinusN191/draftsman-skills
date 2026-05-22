# Sprint 3-W2c — Runtime Readiness Design

**Date:** 2026-05-22
**Predecessor:** Sprint 3-W2b (Content Completion) — shipped at `915522b` with harness FULL GREEN 143/143.
**Status:** Brainstorm complete; spec for review.

---

## §1 — Locked Decisions

| # | Decision | Choice |
|---|---|---|
| D1 | Sprint scope | Engineering refinements + runtime-readiness audit. Defers Bucket C Tier-4 (needs runtime upgrades anyway) + harness M1 DRY (cosmetic refactor) until post-runtime-testing. |
| D2 | Audit coverage | All 4 audit checks: prompts (HIGH RISK), intent contracts (HIGH RISK), skill.manifest.json (MEDIUM), inputs.json taxonomy (MEDIUM). |
| D3 | Task structure | 4 tasks across 3 phases. Engineering refinements (Sonnet, mechanical) + prompts audit (Opus, judgment) + mechanical-audits-bundle (Sonnet) + ship (Opus). |
| D4 | Numeric judgment policy | For PFC + voltage-drop refinements: revise the number to the conservative engineering calculation AND add explicit `inputs` assumptions making the new figure auditable. No tool_call_pending escape hatch on these (cable-sizing skill owns deeper verification). |
| D5 | Voltage-drop reference frame | Line-line (400V) is canonical for TPN feeders. Cite both frames where contextually helpful. Apply consistently across all 4 UK files. |

---

## §2 — Scope

### Engineering refinements (13 items, from Sprint 3-W2b code reviews)

**KE bundle (5 items, from Task 2 review):**
1. **PFC numeric** — `ke-nairobi-gh-db` `incoming_supply.declared_pfc_ka: 3.0` is optimistic for 60m of 10mm² SWA Cu submain. Reviewer's calc suggests ~1.0 kA. **Fix:** revise to conservative number + add `inputs.submain_csa_mm2: 10` + `inputs.loop_z_estimate_ohm: 0.24` in the Incoming Supply decision block so the calc is auditable.
2. **KS Appendix 1 mis-citation** — `ke-nairobi-industrial-100A-tpn` `code_clause: "KS 1700:2018 Appendix 1 (route to BS 7671 via §313)"` for diversity. **Fix:** replace with `KS 1700:2018 § 311 (route to BS 7671 § 311.1) + IET OSG App A`. BS 7671 Appendix 1 is the "British Standards referenced" list, not a diversity clause.
3. **KS § 432 mis-citation** — `ke-nairobi-gh-db` `code_clause: "BS 7671 § 432"` for MCB curve selection. **Fix:** replace with `BS EN 60898-1:2019` only (curve selection lives in the device standard, not BS 7671 § 432 which is "Nature of fault current").
4. **voltage_class mislabel** — `ke-nairobi-gh-db` C03 circuit has `voltage_class: "comms_data"` but is a 240V CCTV power circuit. **Fix:** change to `voltage_class: "LV_power"`. Update Circuit Breakdown decision text if it references the old class.
5. **§ 714 floodlight RCD** — `ke-nairobi-gh-db` C01 external floodlight "No RCD" justified per `§ 411.3.3` only. **Fix:** expand the citation to also cover `BS 7671 § 714` (outdoor lighting installations); justify the no-RCD choice explicitly under § 714 (Class II luminaires + not within touch reach, or alternative § 714 compliance argument).

**UK bundle (4 items, from Task 3 review):**
1. **Voltage-drop reference frame** — UK files variously cite 230V phase or 400V line-line voltage-drop percentages. **Fix:** standardise on **400V line-line as canonical for TPN feeders**. Update every voltage-drop figure in the 4 UK files to be against 400V line-line, OR explicitly state both frames where contextually helpful (e.g. "≈ 0.83% line-line / 1.24% phase").
2. **switch-disconnector breaking_capacity_ka semantic mismatch** — IR field `main_switch.breaking_capacity_ka` is misleading for a switch-disconnector (which has Icw, not Icu). **Fix:** add a one-line clarifier in the Incoming Supply or Schedule Notes decision describing that the field carries short-time withstand (Icw) for switch-disconnector main switches. Don't change the IR field name (out of scope).
3. **§ 311 → § 311.1** — Several UK files cite `BS 7671 § 311` for diversity. **Fix:** replace with `§ 311.1` (the operative regulation; § 311 is the chapter heading).
4. **BS EN 61009-1:2012 amendment edition** — UK SDB files cite `BS EN 61009-1:2012` for RCBOs. **Fix:** update to `BS EN 61009-1:2012+A12:2014` (the in-force edition with amendments).

**INT bundle (4 items, from Task 4 review):**
1. **DB-P1 pre-existing IEC 60364-7-701 mis-citation** — `compliance_summary.assumptions[*]` references `IEC 60364-7-701 series (water proximity)` for a commercial kitchen socket. **Fix:** update the pre-existing assumption text to remove the wrong special-location citation (kitchen is NOT a Part 7-701 bathroom); justify the kitchen RCD requirement directly under § 411.3.3 universal socket-circuit policy.
2. **§ 560.7 sub-clause precision** — DB-FA1 cites `IEC 60364-5-56 § 560.7` for no-RCD justification. **Fix:** tighten to specific sub-clauses where verifiable: `§ 560.7.1` for safety service independence; `§ 560.7.2` for protection coordination. If sub-clause precision can't be confirmed, leave as `§ 560.7` and add a note "(sub-clause precision pending verification)".
3. **Decision text DRY across 4 files** — "Engineer-declared per manufacturer cascade table" decision block appears identically in DB-FA1/L1/M1/P1 selectivity_results sections. **Fix:** vary the wording per file by adding the file-specific cascade ratio (e.g. "6.3:1 same-curve cascade" for DB-FA1; "12.5:1 MCCB+MCB cross-curve" for DB-L1).
4. **DB-P1 P10 voltage drop numeric** — Claims "≈3.7%" at full load on 100m ring; reviewer's IEC mv/A/m calc suggests 5-6% on a centre-loaded ring. **Fix:** revise the figure to the conservative calculation AND add `inputs.ring_length_m: 100` + `inputs.assumed_load_distribution: "centre-loaded"` + `inputs.iec_mv_per_a_per_m: 18` in the Circuit Breakdown decision block. Keep tool_call_pending flag on the cable-sizing-skill handoff.

### Runtime-readiness audit (4 checks)

**A1 — Prompts audit (HIGH RISK)**
- Scope: every skill's `prompts/generator.md` + `prompts/validator.md` + `prompts/reviewer.md` (or whichever exist per skill). 9 skills × up to 3 files each = up to 27 files.
- 5-row drift check per prompt file:
  1. Mentions `board_kind` discriminator? (specifically for db-layout's generator/validator/reviewer)
  2. Covers all 5 jurisdiction enum values including `KE`? (every skill)
  3. Covers `ups_plus_essential` supply_class? (db-layout + skills that consume db-layout intents)
  4. Uses `main_switch_fused` canonical enum (NOT `switch-fuse`)? (db-layout + sld + fault-level downstream consumers)
  5. Citation form aligns with the post-3W2b 4-jurisdiction convention (GB / KE / INT / US)?
- For each drift item found: FIX in place with surgical edits OR document explicitly if out of scope.
- Output: `docs/sprint-3w2c-prompts-audit.md` summary + per-prompt edits committed.

**A2 — Cross-skill intent contracts (HIGH RISK)**
- Producer-consumer pairs to cross-check:
  - **db-layout-rollup** intent (producer: db-layout; consumers: sld, earthing)
  - **fault-level** intent (producer: fault-level; consumers: arc-flash, sld)
  - **cable-sizing** intent (producer: cable-sizing; consumers: small-power, db-layout)
  - **earthing** intent (producer: earthing; consumers: small-power, sld)
  - **arc-flash** intent (producer: arc-flash; consumer: arc-flash-labelling)
  - **small-power** intent (producer: small-power; consumer: db-layout-rollup downstream if applicable)
- For each pair: load both schemas (`shared/schemas/intents/*.schema.json` + per-skill consumer reference), structurally diff. Mismatches → FIX if non-cascading; DEFER if fix triggers example failures.
- Output: section in `docs/sprint-3w2c-contracts-audit.md` for each pair (PASS / N issues fixed / DEFERRED with reason).

**A3 — skill.manifest.json consistency (MEDIUM RISK)**
- Scope: 9 `electrical/*/skill.manifest.json` files.
- Per-manifest checks:
  - Required keys present (skill_id, version semver, produces_intent, consumes_intents[], calc_tools_required[])
  - Version aligns with CHANGELOG.md latest entry
  - produces_intent + consumes_intents[] reference real intent names that exist in `shared/schemas/intents/`
  - calc_tools_required[] reference real calc tools under `shared/calculations/`
- Output: section in `docs/sprint-3w2c-contracts-audit.md` (9 manifests × PASS / N issues fixed).

**A4 — inputs.json item taxonomy resolution (MEDIUM RISK)**
- Scope: 5 skills using `items[]` shape (db-layout, earthing, fault-level, lighting-layout, sld). Skip the 2 `inputs[]` skills (arc-flash family) and the 2 `input_groups[]` skills (cable-sizing, small-power) — their item shape isn't InputItem-validated.
- Per-skill checks:
  - depends_on graph: every depended-on id exists in the same inputs.json items[] array
  - enum option coverage: every option in enum[] appears as the answer for that item in at least one example
  - required item coverage: every item marked `required: true` has a non-null answer in at least one example
- Output: section in `docs/sprint-3w2c-contracts-audit.md` (5 skills × PASS / N issues fixed / DEFERRED).

### Out of scope (kept deferred)

- **Bucket C — Tier-4 lossy eval conversions**: Format C TODO items in db-layout/eval-03, db-layout/eval-08, fault-level/eval-09, earthing/eval-04. Format D TODO items in arc-flash eval-03, arc-flash eval-09, arc-flash-labelling eval-06, arc-flash eval-06. All require eval-runtime upgrades (OR-clauses, cross-array predicates, per-decision-presence) that don't exist yet. Revisit AFTER end-to-end runtime testing surfaces what's actually needed.
- **Harness M1 — DRY consolidation of 3 report-formatting blocks**. Refactor, not bugfix. Not blocking runtime testing.
- **Harness M5/M6/M8**: cosmetic double-blank-line drift; type-hint widening to Python 3.11 syntax; strip_refs over-approximation comment.
- **Deeper prompt content overhaul** beyond the 5-row drift check.
- **Intent contract reconciliation** that would cascade into example failures.

---

## §3 — Phases & Tasks

### Phase A — Engineering refinements (Task 1, Sonnet)

**Why Sonnet:** 13 surgical text + JSON edits with explicit per-occurrence rules. No engineering judgment beyond the locked-decision policies (D4 numeric, D5 voltage-drop frame).

**Files modified:** ~10 example output.json files across `electrical/db-layout/examples/`.

**Steps (high-level):**
1. KE bundle — apply 5 fixes to `ke-nairobi-gh-db` (4 items) + `ke-nairobi-industrial-100A-tpn` (1 item)
2. UK bundle — apply 4 fixes across 4 `uk-commercial-*` files
3. INT bundle — apply 4 fixes to `intl-dbp1-power` + `intl-dbfa1-fire-alarm` + the 4 INT files (decision text DRY)
4. Cross-check: grep for OLD citation/value strings to confirm replacements complete
5. Validate harness still 143/143
6. Commit with per-occurrence documentation in commit body

**Acceptance:** all 13 items closed; harness still 143/143; rationale schemas validate.

### Phase B — Runtime-readiness audit (Tasks 2 & 3)

**Task 2 — Prompts audit + fixes (Opus, judgment)**

**Why Opus:** Prompt files are PROSE not schema. Determining "does this prompt drive the LLM toward post-3W2b shapes" requires reading the prose carefully and making judgment calls about adequacy. Mechanical pattern-matching insufficient.

**Steps:**
1. Inventory all prompt files across 9 skills
2. For each prompt file: apply the 5-row drift check
3. For each drift found: FIX in place if surgical OR document if deeper rewrite needed
4. Author `docs/sprint-3w2c-prompts-audit.md` summary (per-skill rows + drift count + fix-vs-defer outcome)
5. Validate harness still 143/143 (prompt edits shouldn't affect harness, but verify)
6. Commit

**Acceptance:** every prompt verified or documented; audit report committed; zero HIGH-RISK drift items unfixed.

**Task 3 — Intent contracts + manifests + inputs.json (Sonnet, mechanical)**

**Why Sonnet:** A2 + A3 + A4 are mechanical schema/JSON diffs with deterministic comparison rules.

**Steps:**
1. A2 intent contracts — load each producer/consumer schema pair; structural diff; report PASS or fixes
2. A3 manifests — validate 9 skill.manifest.json files for required keys + version semver + reference resolution
3. A4 inputs.json taxonomy — for 5 items[]-shape skills: walk depends_on graphs + verify enum coverage + verify required-item coverage
4. Author `docs/sprint-3w2c-contracts-audit.md` (3 sections: A2 + A3 + A4)
5. Apply surgical fixes for non-cascading mismatches; defer cascading ones with explicit reason
6. Validate harness still 143/143
7. Commit

**Acceptance:** every audit category has PASS or "N issues fixed"; report committed; zero unresolved HIGH-RISK mismatches; harness still 143/143.

### Phase C — Final validation + push + memory save (Task 4, Opus)

**Why Opus:** Ship-readiness judgment + memory file authoring requires faithful summary + accurate deferred-queue documentation.

**Steps:**
1. Run 3-pass harness; expect 143/143 exit 0
2. Walk the 4 audit reports; confirm zero unfixed HIGH-RISK items
3. Push to origin/main
4. Save `sprint-3w2c-shipped.md` memory file (mirror sprint-3w2b-shipped.md shape)
5. Update MEMORY.md index
6. Update CLAUDE.md if any audit found material conventions to document (don't add scope creep)
7. Report to user: ready for runtime end-to-end testing

---

## §4 — File Operations Summary

| Phase | Files modified | Files created |
|---|---|---|
| A — Engineering refinements (13 items) | ~10 example output.json files | 0 |
| B Task 2 — Prompts audit | up to 27 prompt files (many likely PASS) | 1 (`docs/sprint-3w2c-prompts-audit.md`) |
| B Task 3 — Contracts audit | up to 9 manifests + ~6 intent schemas + 5 inputs.json | 1 (`docs/sprint-3w2c-contracts-audit.md`) |
| C — Ship | 0-1 (CLAUDE.md if needed) | 1 memory file + 1 index update |
| **Total estimated** | **~30-50 file ops** | **2 audit reports + 1 memory file** |

Comparable to 3-W2b (~50 ops). 1-2 dev day budget.

---

## §5 — Risks & Mitigations

- **R1 — Prompts audit surfaces a large fix queue.** *Mitigation:* if any single skill needs > 30 min of prompt rewriting, defer the deeper refresh to a follow-up sprint and document the gap in the audit report. Don't expand the sprint silently.

- **R2 — Intent contract mismatches require cascading schema changes.** *Mitigation:* Task 3 categorises every mismatch by severity. Non-cascading edits ship; cascading edits defer to a dedicated "intent contract reconciliation" sprint.

- **R3 — Numeric refinement reversibility.** Changing PFC 9.8→1.0 kA or P10 voltage drop 3.7%→6% could ripple into downstream selectivity_results / compliance_summary fields. *Mitigation:* Task 1 grep per file for old numeric values BEFORE replacing; commit body documents the cascade explicitly.

- **R4 — Inputs.json depends_on cycle or orphan.** *Mitigation:* Task 3 reports unfixable items as audit-report entries; surfaces to runtime testing phase for the runtime adapter to handle.

- **R5 — Audit findings cascade into scope creep.** *Mitigation:* per-audit report has explicit FIXED vs DEFERRED columns; deferred items added to memory file's known-follow-up section.

- **R6 — Runtime-readiness is necessary but not sufficient.** Audit can't see LLM emission quality, runtime adapter assumptions, calc tool integration. *Mitigation:* Task 4 commit message explicitly says "audit confirms contracts and prompts align; runtime testing may surface execution-layer issues not visible here."

- **R7 — Bucket C Tier-4 + harness polish truly deferred — not silently lost.** *Mitigation:* `sprint-3w2c-shipped.md` memory file MUST list both as explicit follow-ups for a post-runtime-testing sprint.

---

## §6 — Acceptance Criteria

1. **Harness FULL GREEN held:** `python3 scripts/validate-examples.py` exit 0 with Pass 1 53/53 + Pass 2 81/81 + Pass 3 9/9 = AGGREGATE 143/143.

2. **All 13 engineering refinements applied:**
   - 6 citation-precision fixes (grep confirms old citations gone, new ones present)
   - 2 data fixes (voltage_class C03 + IEC 60364-7-701 assumption text)
   - 2 numeric judgments documented with explicit inputs assumptions
   - 2 doc clarifications consistent across affected files
   - 1 citation expansion (§ 714 floodlight)

3. **Audit A1 (prompts) outcome:** `docs/sprint-3w2c-prompts-audit.md` exists; per-skill PASS or "N drift items fixed"; zero HIGH-RISK drift unfixed.

4. **Audit A2 (intent contracts) outcome:** every producer-consumer pair has PASS or "N mismatches fixed"; zero unresolved HIGH-RISK mismatches.

5. **Audit A3 (manifests) outcome:** all 9 `skill.manifest.json` files valid + version-consistent.

6. **Audit A4 (inputs.json taxonomy) outcome:** all 5 items[]-shape inputs.json files have clean depends_on graphs.

7. **Documentation:**
   - `sprint-3w2c-shipped.md` memory file written with deferred-follow-up section
   - `MEMORY.md` index updated
   - Skills repo declared "runtime-ready" — user can proceed to Claude + DraftsMan runtime end-to-end test

8. **Push:** committed cleanly to origin/main without `--force` or `--no-verify`. 4 task commits + 2 doc commits (spec + plan) = 6 commits pushed.

---

## §7 — Out-of-Scope Handoff

After 3-W2c ships and runtime testing surfaces real needs, a future sprint (3-W2d or post-runtime-test cycle) addresses:

- **Bucket C — Tier-4 lossy eval conversions** (require eval-runtime grammar upgrades for OR-clauses / cross-array predicates / per-decision-presence)
- **Harness M1** — DRY consolidation of 3 report-formatting blocks (refactor)
- **Harness M5/M6/M8** — cosmetic + type-hint widening + strip_refs comment
- **Deeper prompt content overhaul** for any skill where the 5-row drift check surfaced beyond-scope rewrites
- **Intent contract reconciliation** for any cascading mismatches deferred from Task 3
- **inputs.json depends_on cycle/orphan fixes** that the runtime adapter can't paper over
- **Engineering content refinements** that runtime testing reveals (e.g. LLM emits a shape that no example covered)

---

## §8 — Model Selection

Per `[[feedback-no-haiku-sonnet-opus-only]]`:
- **Sonnet** — Task 1 (mechanical refinements), Task 3 (mechanical schema audits)
- **Opus** — Task 2 (prompts audit needs content judgment), Task 4 (ship judgment + memory authoring)

Total: 4 tasks. 2 Opus + 2 Sonnet.

---

## §9 — Sprint Workflow

Standard pattern per [[sprint-3w2a-shipped]] / [[sprint-3w2b-shipped]]:
1. Spec (this doc) approved by user
2. Plan authored via `superpowers:writing-plans` → `docs/superpowers/plans/2026-05-22-sprint-3w2c-runtime-readiness-sprint.md`
3. Execute via `superpowers:subagent-driven-development`, 2-stage review per task, continuous execution
4. Memory save on ship; index updated; runtime end-to-end testing follows

---

## Cross-references

- [[sprint-3w-shipped]] — original schema-fragmentation backlog
- [[sprint-3w2a-shipped]] — schema standardisation
- [[sprint-3w2b-shipped]] — content completion; harness FULL GREEN achieved
- [[runtime-project-boundary]] — skills repo ships contracts; runtime executes
- [[feedback-no-haiku-sonnet-opus-only]] — model rules
- [[build-strategy-breadth-first]] — back to breadth-first skill build after runtime testing validates
