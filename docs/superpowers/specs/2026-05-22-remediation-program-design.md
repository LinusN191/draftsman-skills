# Remediation Program — Aggregate Audit Fix Design

**Date:** 2026-05-22
**Predecessor:** External audit by 2 reviewers (13 reviews collected, baseline captured at commit `4e1c5ee`); 43 functional findings + 5 Reviewer-2 manifest-contract items
**Status:** Brainstorm complete; spec for review.

---

## §1 — Locked Decisions

| # | Decision | Choice |
|---|---|---|
| D1 | Sprint shape | 5 sub-sprints (Sprint 0 → D) sequenced per DEFECT_REGISTER recommended order; matches 3-W2a/b/c precedent |
| D2 | CI gate sequencing | functional_audit.py wired into CI as Sprint 0 prerequisite (BEFORE any fixes); CI red from day 1 trending green to baseline-0 |
| D3 | Eval-vs-IR (M1) reconciliation | Hybrid: extend IR schemas to add `ir.invariants: {INV-N: {passes, evidence}}` (load-bearing) + rewrite assertions for citations/emitted_intents to existing fields (where they semantically belong) |
| D4 | Schematic v1.0 retrofit | YES — retrofit alongside the 9 baseline skills for canonical consistency |
| D5 | Manifest contract migration timing | Sprint 0 parallel workstream alongside CI wiring (both infrastructure prerequisites unblock everything downstream) |
| D6 | Verification fence | Per-sprint Sonnet subagent re-runs `functional_audit.py` + `validate-examples.py` + spot-recomputes 1 example from affected skill BEFORE sprint's commit lands; catches symptom-papering per Reviewer's #3 warning |

---

## §2 — Program Goal

Clear the 43 findings from `functional_audit.py` + Reviewer 2's 5 contract-migration items + wire the harness into CI as the canonical gate, then tag a versioned commit and reshare to Reviewer 1 for like-for-like re-audit ("DraftsMan re-test").

**Reviewer's 4 strategic warnings explicitly addressed:**
1. **Like-for-like re-test** → Sprint D tags `audit-cleared-v1.0` at the final commit; reshare prompt references the tag
2. **CI gating highest-value** → Sprint 0 prerequisite (functional_audit.py in CI BEFORE any fix)
3. **Cause-fixing not symptom-papering** → per-sprint verification fence + cause-fix-explicit task prompts (e.g. C1 cause-fix is "rename folder + author genuine TT example", not "flip compliance flag")
4. **Memory doesn't carry over** → Sprint D explicit reshare prompt with tag + DEFECT_REGISTER pointer + per-sprint memory file links

---

## §3 — Sprint Breakdown (5 sprints, 18 tasks)

### Sprint 0 — Infrastructure prerequisites (2 tasks, ~1 dev-day)

| Task | Workstream | Model | Outcome |
|---|---|---|---|
| 0.1 | CI wiring | Sonnet | `.github/workflows/functional-audit.yml` runs harness on push/PR to main; baseline 43 findings visible in CI; FP-disclosure header documents known false-positive sources |
| 0.2 | Manifest contract migration | Sonnet | 10 skills' consumes_intents → dict shape per Reviewer 2 Issue 1; 10 skills' produces_intent → produces_intents plural dict per Issue 2; producer/intent confusion fixed (db-layout PRODUCES "db-layout-rollup" intent, not vice-versa); chat_type added to 9 skills per Issue 3; fire-alarm/examples/uk-small-office/input.json added per Issue 4 |

**Gate:** CI workflow live + harness baseline 43 findings + dict-shape manifests pass dependency resolver + validate-examples.py 162/162 held.

### Sprint A — CRITICAL safety (4 tasks, ~1.5 dev-days)

| Task | Workstream | Model | Outcome |
|---|---|---|---|
| A.1 | **C1 earthing TT cause-fix** | Opus | Rename `intl-rural-tt/` → `intl-rural-tncs/` (matches TN-C-S content); fix 4 false-pass circuits' zs_compliance; **author genuine TT example at `intl-rural-tt/` (rural cottage with mandatory 30mA RCD per Reg 411.5); INV-6 fires against this new golden case**; update sld consumer reference if needed |
| A.2 | **C2 label provenance schema-level fix** | Opus | Add `provenance: {method, computed_at, calc_tool_version, is_provisional}` block to arc-flash-labelling IR schema; renderer emits "DRAFT — NOT FOR FIELD USE" when `is_provisional == true`; 3 label examples updated to populate provenance from upstream arc-flash intent |
| A.3 | **C3 IEEE 1584-2018 coefficients ship** | Opus | Transcribe + verify IEEE 1584-2018 600V coefficient set from publicly available IEEE Std 1584-2018 Tables; verify 2700V set; at least one arc-flash example demonstrably uses IEEE 1584-2018 method (NOT Lee fallback); add eval asserting `method_applied == "ieee_1584_2018"` for a 400V example |
| A.4 | Sprint A ship | Opus | functional_audit.py: 4 CRITICAL → 0; validate-examples.py: 162/162 held; commit + push; sprint-A-shipped memory |

### Sprint B — HIGH correctness + Hybrid eval-vs-IR fix (6 tasks, ~2 dev-days)

| Task | Workstream | Model | Outcome |
|---|---|---|---|
| B.1 | **fault-level H1+H2+H3** | Opus | intl-genset TX-1 z fixed (recompute from 1600 kVA transformer impedance); double-c-factor fixed on intl-genset HV-1 + us-motors HV-1; uk-domestic z reconciled to documented formula; validator INV added: `Ik = c·U/(div·Z)` internal-consistency check |
| B.2 | **cable-sizing H4 single formula fix** | Sonnet | 3-phase Vd divisor changed from 230V phase to 400/415V line-line in generator; affected examples recomputed (ke F02, ke F03, intl RISER.L3.C07); validator INV detects ÷230 anomaly on 3-phase |
| B.3 | **db-layout H5+H6** | Opus | Per-load-type diversity per IET OSG Appendix A (replace blanket 0.4 in uk-domestic); validator INV flags blanket factor on instantaneous loads; wrong citation fixed (BS 7671 App 1 → IET OSG App A + § 311.1); **phase preservation in TPN board outputs** (carry L1/L2/L3 round-robin from input; compute per-phase loading + neutral current) |
| B.4 | **H7 cross-skill broken refs** | Sonnet | arc-flash-labelling 2 consumed_intent_path fixes (uk-400v-commercial → uk-lv-switchgear; intl-11kv-substation → intl-mv-substation); earthing uk-dwelling-tn-cs 2 payload_ref fixes (author missing fixture files if load-bearing OR remove cruft refs — choice documented in commit) |
| B.5 | **M1 Hybrid eval-vs-IR fix (all 10 skills + schematic retrofit)** | Opus | Extend 10 IR schemas with `ir.invariants: {INV-<N>: {passes, evidence}}`; extend 10 generator prompts to populate; update all 61+ examples to carry populated invariants; rewrite eval assertions for `ir.citations` / `ir.emitted_intents` / `ir.intent_emitted` / `ir.controls.lamp_efficacy_lm_per_w` / `ir.nodes` / `ir.busbar` / `ir.incoming` / `ir.flags` → reference where these fields actually live (rationale prose, intent-out.json, calculation_summary, etc.); schematic v1.0 retrofitted alongside |
| B.6 | Sprint B ship | Opus | functional_audit.py: 7 HIGH → 0 + M1 4 MEDIUM (eval-vs-output) → 0; validate-examples.py: 162/162 held; commit + push; sprint-B-shipped memory |

### Sprint C — MEDIUM coverage + LOW hygiene (5 tasks, ~1 dev-day)

| Task | Workstream | Model | Outcome |
|---|---|---|---|
| C.1 | **M2 genuine TT example** | Opus | (cause-fix completion of C1) — rural cottage TT system at `intl-rural-tt/`: high Ra electrode, mandatory 30mA RCD on every final circuit, Reg 411.5 citations, INV-6 fires; ≥1 eval that fires INV-6 against this golden case |
| C.2 | **M3 ship PVC + 1.0mm² tables** | Sonnet | BS 7671 Appendix 4 Table 4D1A (PVC twin-and-earth) + Table 4D5A (PVC SWA) data shipped; 1.0 mm² row added to existing 4D2 table; any example misusing XLPE data for PVC cable re-tagged |
| C.3 | **M4 untested safety branches** | Opus | arc-flash RESTRICTED >40 cal/cm² example added (HV substation typical; "no PPE adequate" path); label provenance disclosure example added (correctly-computed value with full provenance metadata + non-provisional renderer output) |
| C.4 | **L1+L2+L3 hygiene** | Sonnet | cable-sizing + small-power manifests gain prompts/evals/examples declarations; deprecated cable-current-ratings.json removed; folder rename L3 verified completed in A.1 |
| C.5 | Sprint C ship | Opus | functional_audit.py: aggregate 0 findings exit 0; validate-examples.py: 162/162 (or higher with new examples); commit + push; sprint-C-shipped memory |

### Sprint D — Tag + push + memory + reshare (1 task, ~30 min)

| Task | Workstream | Model | Outcome |
|---|---|---|---|
| D.1 | **Program closing ship** | Opus | functional_audit.py exit 0 + validate-examples.py exit 0; `git tag audit-cleared-v1.0`; `git push origin main --tags`; author `remediation-program-shipped.md` memory + MEMORY.md index update; author "DraftsMan re-test" reshare prompt (tag + DEFECT_REGISTER pointer + expected harness output + per-sprint memory links); report final state |

---

## §4 — Verification Fence (every sprint)

Each sprint's final ship task includes a verification fence — a Sonnet subagent that BEFORE commit:

1. Runs `python3 functional_audit.py` and reports the delta from the prior sprint's finding count
2. Runs `python3 scripts/validate-examples.py` and confirms 162/162 (or current baseline)
3. Spot-recomputes 1 example from a skill touched in the sprint against the skill's shipped tables/formulas — flags symptom-papering (e.g. if cable-sizing 3-phase Vd was "fixed" by hardcoding numbers, recomputation would catch the mismatch with shipped mV/A/m table)
4. Confirms no regression to schematic v1.0 baseline (162/162 AGGREGATE; preserves the 10-skill set's harness state)

This addresses Reviewer's #3 warning directly. Verification subagents are Sonnet (cheap) — ~15 min per sprint × 5 sprints = ~75 min added.

---

## §5 — Risks & Mitigations

(Full list per Section 3 of brainstorm; reproduced here for completeness.)

- **R1 — Symptom-papering instead of cause-fixing.** Verification fence per sprint + task prompts explicitly state cause vs symptom.
- **R2 — IR-schema additions break existing examples.** Schema addition additive (`ir.invariants` optional initially); examples updated in same task.
- **R3 — Cross-skill cascade: H1 fault-level fix flows downstream.** B.1 grep-cascades the fix; B.6 verification reruns audit.
- **R4 — Manifest contract migration breaks schema harness.** Task 0.2 includes post-migration `validate-examples.py` check; updates eval.schema.json if needed.
- **R5 — IEEE 1584-2018 coefficient transcription accuracy.** A.3 reviewer verifies against PUBLIC IEEE source; spot-recomputes IE for 1 node to confirm direction (IEEE-2018 < Lee at LV).
- **R6 — Verification fence subagent adds cost.** Accept ~75 min cost; Sonnet-cheap; non-negotiable per Reviewer warning #3.
- **R7 — Schematic v1.0 regression during B.5 retrofit.** B.5 explicit AGGREGATE 162/162 check after retrofit; halt + fix if drops.
- **R8 — Like-for-like re-test commit-anchor drift.** Sprint D tags `audit-cleared-v1.0`; reshare prompt references THAT tag.
- **R9 — Test-fixture orphan files in earthing.** B.4 prompt explicit: author missing fixtures if load-bearing OR remove if cruft; document choice in commit.
- **R10 — Memory + reshare prompt drift.** D.1 reshare prompt includes tag + DEFECT_REGISTER pointer + expected harness output (0 findings) + per-sprint memory file links.

---

## §6 — Acceptance Criteria

1. `python3 functional_audit.py` → 0 findings exit 0
2. `python3 scripts/validate-examples.py` → AGGREGATE 162/162+ exit 0
3. CI workflow `.github/workflows/functional-audit.yml` runs on every push + PR; PRs must pass before merge
4. All 10 skill manifests on dict-shape contract per Reviewer 2 spec
5. All 10 IR schemas carry `ir.invariants` block; all 61+ examples populate it
6. No symptom-papering verified per verification fence
7. CRITICAL safety (C1+C2+C3) completely remediated
8. HIGH correctness (H1-H7) all 7 cleared; validator INVs added
9. MEDIUM coverage (M1-M4) all 4 cleared; eval-vs-IR drift = 0 across 10 skills
10. LOW hygiene (L1-L3) all 3 cleared
11. Tagged commit `audit-cleared-v1.0` pushed
12. `remediation-program-shipped.md` memory + MEMORY.md updated; "DraftsMan re-test" reshare prompt drafted

---

## §7 — Out-of-Scope Handoff

- Sprint 3-N document skills (`outline.yaml` per Reviewer 2 Issue 5) — separate program; document skills need their own brainstorm
- External: `orchestrator.py:89` hardcoded Anthropic — lives in runtime repo, not skills repo (Reviewer 2 Issue 7)
- Per-skill recompute oracle expansion to drawing skills (geometry/topology vs arithmetic) — future work
- Eval-runtime upgrades for OR-clauses / cross-array predicates / per-decision-presence (Bucket C from 3-W2c deferred queue)
- Schematic v1.1 polish items (ANSI 49 thermal_relay enum + 50BF regex; ~200-symbol library expansion; HV protection beyond busbar)
- Lighting-layout content overhaul (3 stub prompts deferred from 3-W2c)

---

## §8 — Model Selection

Per `[[feedback-no-haiku-sonnet-opus-only]]`:
- **Sonnet (6 tasks):** 0.1 (CI wiring), 0.2 (manifest migration), B.2 (cable-sizing formula fix), B.4 (broken refs), C.2 (PVC tables), C.4 (hygiene)
- **Opus (12 tasks):** A.1 (TT cause-fix), A.2 (provenance schema), A.3 (IEEE coefficients), A.4 (Sprint A ship), B.1 (fault-level), B.3 (db-layout), B.5 (Hybrid IR extension), B.6 (Sprint B ship), C.1 (TT example), C.3 (safety branches), C.5 (Sprint C ship), D.1 (program close)
- **Per-sprint verification fence:** Sonnet sub-dispatch from within each Opus ship task (A.4, B.6, C.5, D.1) — not counted as separate tasks; 4 fence runs total

Total: 18 tasks = 6 Sonnet + 12 Opus. Estimated 5-6 dev-days end-to-end.

---

## §9 — Program Workflow

Standard pattern per [[sprint-3w2a-shipped]] / [[sprint-3w2b-shipped]] / [[sprint-3w2c-shipped]]:
1. Spec (this doc) approved by user
2. Plan authored via `superpowers:writing-plans` → `docs/superpowers/plans/2026-05-22-remediation-program-sprint.md`
3. Execute via `superpowers:subagent-driven-development`, 2-stage review per task + verification-fence per sprint, continuous execution
4. Each sprint = its own memory file (sprint-A/B/C/D-shipped.md); D.1 also writes program-level summary
5. Final tag `audit-cleared-v1.0` + reshare prompt for reviewer re-audit

---

## Cross-references

- `docs/reviews/DEFECT_REGISTER.md` — canonical defect register (3 CRIT + 7 HIGH + 4 MED + 3 LOW)
- `docs/reviews/2026-05-22-collected-external-reviews.md` — 13 reviews verbatim + F1.x-F13.x findings
- `docs/reviews/2026-05-22-functional-audit-baseline.txt` — captured 43-finding baseline at commit `4e1c5ee`
- `functional_audit.py` — canonical re-test instrument
- [[runtime-project-boundary]] — skills repo ships contracts; runtime executes
- [[feedback-no-haiku-sonnet-opus-only]] — model rules
- [[build-strategy-breadth-first]] — schematic v1.0 (10th skill) preserves harness 162/162 throughout
- [[sprint-3w2a-shipped]] / [[sprint-3w2b-shipped]] / [[sprint-3w2c-shipped]] — proven multi-sub-sprint pattern (3 sub-sprints → this is 5)
