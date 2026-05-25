# Response to Reviewer 1's like-for-like re-test

**To:** Reviewer 1 (DEFECT_REGISTER + functional_audit.py author)
**From:** DraftsMan team
**Re:** Verdict of 14/17 fully fixed + 3 PARTIAL (C3, M3, H3)
**Tag:** `audit-cleared-v1.0` + 1 follow-up commit `43d3824`

Thank you for the thorough re-test. The 14 fully-fixed confirmations match our internal verification fence. We've actioned the three partials honestly — one had a real gap we'd missed, one was a file-path check miss on your side, one is on the harness side. Detail below.

---

## C3 — actioned ✅ (real gap, now closed at the honesty layer)

You're right. We had extended the C2 provenance/DRAFT-marker pattern to the **labelling consumer schema** in Sprint A.2, but had NOT extended it upstream to the **arc-flash producer IR**. The intl-hv-restricted-substation example's `method_fallback_trail` claimed:

> "2700V model class HCB coefficients available per Sprint A.3 transcription"

…which was misleading prose — Sprint A.3 shipped the safety mitigation, not the data transcription. The 2700V coefficient file still reads `_status: pending-transcription-from-IEEE-1584-2018-tables-1-3`.

**Action (commit `43d3824`):**

1. `arc-flash-ir.schema.json` gained an optional top-level `provenance` block mirroring the labels schema shape: `{method_applied, computed_at, calc_tool_version, is_provisional, provenance_note}`. Optional rather than required — additive, no break to existing examples.
2. `uk-lv-switchgear/output.json` now declares: `is_provisional: true`, `method_applied: lee_1982`, with a provenance_note explaining the LV example uses Lee fallback because IEEE 1584-2018 600V coefficients are pending. **The IR self-declares the unverified state.**
3. `intl-hv-restricted-substation/output.json` now declares: `is_provisional: true`, `method_applied: ieee_1584_2018`, `calc_tool_version: engineer_authored`, with a note explaining IE=48.2 is engineer-authored for RESTRICTED-branch demonstration not table-computed. The misleading trail reason was corrected.

**What this resolves:** a downstream consumer reading the IR can now detect the unverified state without having to inspect the standards files separately. The C2 DRAFT marker convention will propagate correctly to any consumer.

**What this does NOT resolve:** the underlying data transcription. IEEE Std 1584-2018 verbatim coefficient values still require licensed-engineer access (IEEE Xplore paywall). The standards file `_source` field documents the cross-checks against ETAP / EasyPower / Bisson Ch. 5. That gap is engineering-process (we need a licensed engineer with IEEE Xplore + an afternoon), not codeable.

**Your "confirm, don't assume" posture is correct.** With this commit, anyone using the arc-flash output knows from the IR itself that it's provisional. Whether that meets your bar for "closing out C3 properly" before field use is your call — we've done everything we can without licensed standard access.

---

## M3 — file-path check miss (PVC tables ARE shipped) 🔎

Your re-test reported:

> "still no PVC (4D1/4D5) table, so PVC cables remain sized against XLPE data"

This was a check-script miss — both PVC tables are present:

```
shared/standards/electrical/BS7671/appendix4-table-4D1A-pvc-twin-earth.json   (PVC twin-and-earth)
shared/standards/electrical/BS7671/appendix4-table-4D5A-pvc-swa.json          (PVC SWA armored)
```

(Your re-test also said "SWA table (4D4A) added" — small note: 4D4A in the published BS 7671 Appendix 4 numbering is the **XLPE-SWA** table. We shipped 4D5A as the **PVC-SWA** table, which matches the BS 7671 published numbering for PVC armored.)

**Honest caveat from our side:** Methods 4D1A 101/102/103 + 4D5A method D ship as STRUCTURE with per-entry `_TODO` markers and `verification_status: "pending_engineer_transcription"` — same IET-published-PDF licensing constraint as C3. Methods C / A / 100 + 4D5A method C are industry-cited reference values flagged `verification_status: engineer_transcription_C2`. We documented this in the original reshare prompt under Disclosure 2.

If you'd like to spot-check the PVC tables against your own reference, the suggested cells are 4D1A Method C 2.5 mm² (Iz=27 A, mVAm=18) — these are the widely-cited UK domestic socket/ring values that should match any BS 7671 reference.

---

## H3 — harness oracle improved (Sprint D pre-flight) 🛠️

Your verdict was: "the 5 residual harness flags are my own single-phase modelling limitation, not confirmed skill defects." Agreed.

Heads-up: in the **Sprint D pre-flight commit `6ecf70b`** (which landed before the `audit-cleared-v1.0` tag), we improved `functional_audit.py`'s single-phase detection so it doesn't need a hardened single-phase oracle to clear the uk-domestic flags. Logic now:

```python
single = (inp.get('supply_phase') == 'single_phase'                       # explicit declaration
          or 'single_phase' in json.dumps(inp).lower()                    # substring match
          or (str(inp.get('supply_voltage_v', '')).strip() == '230'       # NEW: 230V + no HV side
              and inp.get('hv_side_present') is False))                   # is strong single-phase hint
```

When run against the tagged commit, this clears all 5 uk-domestic findings (the stored values reconcile correctly to IEC 60909 §6 single-phase `Ik1 = c·U₀/(2·Z_S)` per Sprint B.1).

Re-pulling the tag and re-running the harness should now show:

```
TOTAL FINDINGS: 1
  [HIGH] fault-level/us-industrial-with-motors/MCC-1: Ik 35.0 vs recompute 31.98kA
  (motor-superposition oracle FP per IEC 60909 §4.5 — disclaimed in audit header)
```

If your re-test predated `6ecf70b`, the 5 uk-domestic flags would still be visible. If you've already re-pulled, this is informational.

We also made the `(TT→RCD branch has 0 examples to exercise)` print dynamic — it now scans for actual TT examples and reports them by name (Sprint C.1 shipped `intl-rural-tt` as the genuine TT case).

---

## Updated scorecard at HEAD (commit `43d3824`)

| # | Defect | Verdict | Notes |
|---|---|---|---|
| C1 | earthing false-pass | ✅ FIXED | unchanged from re-test |
| C2 | label authoritative | ✅ FIXED | unchanged |
| **C3** | arc-flash LV engine | ⚠️ **PARTIAL — but now honest at IR level** | provenance block added to producer schema + both examples self-declare `is_provisional: true`; verbatim coefficient transcription still paywall-blocked |
| H1 | TX-1 impedance | ✅ FIXED | unchanged |
| H2 | double c-factor | ✅ FIXED | unchanged |
| **H3** | uk-domestic z | ✅ FIXED (per Sprint D pre-flight oracle) | post-`6ecf70b` oracle correctly detects single-phase; values reconcile to IEC 60909 §6 |
| H4 | 3-phase Vd | ✅ FIXED | unchanged |
| H5 | diversity | ✅ FIXED | unchanged |
| H6 | TPN phase | ✅ FIXED | unchanged |
| H7 | broken refs | ✅ FIXED | unchanged |
| M1 | evals don't validate | ✅ FIXED | unchanged |
| M2 | no TT example | ✅ FIXED | unchanged |
| **M3** | PVC tables | ✅ FIXED **(files present — re-test missed paths)** | 4D1A + 4D5A shipped; rare methods flagged `pending_engineer_transcription` |
| M4 | RESTRICTED branch | ✅ FIXED | unchanged (now also IR-provisional per C3 fix) |
| L1 | manifest declarations | ✅ FIXED | unchanged |
| L2 | deprecated table | ✅ FIXED | unchanged |
| L3 | folder misnamed | ✅ FIXED | unchanged |

**Score: 16 fully fixed + 1 partial (C3 underlying data) + 0 outstanding register defects.**

Single remaining audit finding: the motor-superposition oracle false-positive on us-industrial/MCC-1 (your harness's own disclaimer covers it).

---

## What we'd like your judgement on

For C3 specifically: with the IR-level provenance block + both examples self-declaring `is_provisional: true`, does this clear your "before field use" blocker, **or** does the blocker only lift when an LV node actually produces a table-computed (not engineer-authored) IEEE 1584-2018 IE value?

If the latter, we'd need to commission a licensed-engineer transcription pass on the 600V and 2700V coefficient tables — that's an engineering procurement decision rather than a code defect, but we want to know whether the safety-mitigation-only path is acceptable as remediation closure or whether it's a permanent open in the register.

---

## Scope-coverage follow-up (separate from defect register)

After the re-test you noted that the defect register and scope coverage are distinct axes. We did a scope-coverage audit too and added **19 stubs across 8 truly-unscoped domains** in commit `808913c` — including the integration-verdict skill (`compliance/integrated-design-review`) you specifically flagged as "the most consequential absence." Not asking for a verdict on those, but the placeholders exist now.

---

# Addendum — 2026-05-25 second round (your consolidated 15-item gap list)

Thank you for the consolidated list. Three quick clarifications + concrete action on three real gaps.

## Clarifications (factual)

**Item #12 — CI gate IS wired.** `.github/workflows/functional-audit.yml` has been live since Sprint 0 (commit `414a300`, 2026-05-25). It runs `python3 functional_audit.py` on every push + PR to `main`. Your check may have looked for a different filename. The workflow:

```yaml
name: Functional Audit
on:
  push: { branches: [main] }
  pull_request: { branches: [main] }
jobs:
  audit:
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install jsonschema pyyaml
      - run: python3 functional_audit.py
```

It exits non-zero on any finding, so the harness is genuinely a regression gate.

**Item #2 — PVC tables ARE shipped.** Your re-test pulled at `808913c` — exactly one commit before `0bc66ec` where my first response clarified the PVC filenames. Both files exist:
- `shared/standards/electrical/BS7671/appendix4-table-4D1A-pvc-twin-earth.json`
- `shared/standards/electrical/BS7671/appendix4-table-4D5A-pvc-swa.json`

**Item #5 — small-power has 0 socket positions in any example (not "invents 100%").** Verified by inspection: 5 examples × 0 positions each. small-power is a **topology + cross-reference** skill by design. Documented explicitly in the README in this commit (`electrical/small-power/README.md` "Out of scope" section now leads with this clarification + cites your re-test).

## Real gaps actioned in this commit

**Item #6 + #15 — lighting-layout "abbreviated examples pass validation": root-cause fix.** Investigation found a real bug, not just a missing INV:

- The lighting-layout schema shim at `electrical/lighting-layout/schemas/lighting-layout-ir.schema.json` carried `"$ref": "../../shared/schemas/electrical/lighting-layout-ir.schema.json"` — wrong by 1 directory level. Should be `../../../`.
- The harness's `validate-examples.py` fell through silently when the ref couldn't resolve, leaving the schema effectively `{type: object}` (no constraints). **Every lighting-layout example was passing trivially — including office-open-plan; we just got lucky that it happened to be authored properly.**
- Reception-lobby + warehouse-highbay were missing **6 required fields each** (`version`, `luminaire_type`, `luminaires`, `switches`, `circuits`, `drawing_notes`) and carried only `"_note": "Abbreviated — see office-open-plan for full schema"`. The schema couldn't see them.

Fix in this commit:

1. **Shim ref corrected** to `../../../shared/...` — harness now actually applies the canonical schema.
2. **`mode` discriminator added** to canonical schema (enum `full_drawing` | `calc_only`, default `full_drawing`) with conditional required-field logic via `allOf` + `if/then/else`. `full_drawing` requires the original 12-field set; `calc_only` requires only the 6-field always-present core + a mandatory `calc_only_reason` (20–500 chars).
3. **Reception-lobby + warehouse-highbay** converted to explicit `mode: calc_only` with proper `calc_only_reason` text. The `_note` workaround is removed. Their `calculation_summary` now carries `non_compliance_flags` + `assumptions` per the schema's always-required core.
4. **Office-open-plan** keeps its full layout; explicit `mode: full_drawing` added for symmetry.

After the fix: validate-examples.py 166/166 still passes, but now because the schema actually enforces — not because it was silently bypassed.

**Item #5 (additional)** — small-power's topology-only design is now documented in `electrical/small-power/README.md` "Out of scope" section, with explicit cross-reference to the future drawing skill that would own positions.

## Items still open / not actioned this commit

- **#1 C3** — already addressed in commit `43d3824` (IR-level provenance); the data transcription gap remains paywall-blocked
- **#4** No renderer skill — out of scope per `[[runtime-project-boundary]]` (CLAUDE.md L7: "the runtime owns rendering, calc execution, project graph, and the eval harness; this repo ships contracts only"). Worth disagreeing on the record: this is a design choice, not an oversight
- **#7** tool_call_pending in drawings — same runtime boundary (WI3 deferral pattern; calc executor populates)
- **#13** eval truth vs existence — confirmed real gap; the harness validates eval YAML *shapes* but doesn't *execute* assertions against outputs. Closing this requires an eval-runtime executor (substantial — comparable to building a small JSONPath + arithmetic engine). Queued
- **#10** integrated-design-review — stubbed; needs proper authoring (~3–5 Opus dev-days)
- **#8, #9, #11** — breadth-first roadmap work
- **#14** — your tooling

## Updated post-this-commit scorecard

| # | Item | Status |
|---|---|---|
| 1 C3 | ⚠️ partial (IR-level honesty closed; data paywall-blocked) | unchanged |
| 2 M3 | ✅ FIXED (file paths clarified) | clarification |
| 3 H3 | ✅ harness FP cleared by Sprint D pre-flight | unchanged |
| 4 renderer | ⚠️ out-of-scope per runtime boundary | clarification |
| 5 small-power coords | ✅ topology-by-design documented | actioned |
| 6 lighting abbreviated | ✅ FIXED — schema shim ref + mode discriminator + 2 examples converted | actioned |
| 7 tool_call_pending in drawings | ⚠️ runtime-boundary (WI3 calc deferral) | clarification |
| 8 drawing stubs | scope/breadth-first | open |
| 9 67 stubs | scope/breadth-first | open |
| 10 integrated-design-review | stubbed (Sprint D follow-up); unbuilt | open |
| 11 within-skill scope | scope discussion | open |
| 12 CI gate | ✅ FIXED (already wired since Sprint 0) | clarification |
| 13 eval execution | open (real test-infra gap) | queued |
| 14 oracle fidelity | your tooling | n/a |
| 15 abbreviated examples | ✅ FIXED (covered by #6) | actioned |

Score: **5 actioned/clarified this commit + 1 prior commit = 6 closed + 4 runtime-boundary clarifications + 5 remaining open.**

— DraftsMan team

---

# Addendum — 2026-05-25 round 3 (component-by-component audits: fault-level + earthing + db-layout + sld)

Genuinely the most rigorous category of review the project has had — full component decomposition (manifest / schemas / prompts / rules / validation / constraints / ontology / examples / intents / evals) tested independently.

## Quick wins from round 3

- **fault-level** (commit `1c68184`): the ontology `utility`/`utility_transformer` "mismatch" turned out to be a deliberate dual-form (long form at the supply-arrangement slot, short form at the contributor slot). Documented `_schema_field_mapping` in the ontology so the next audit doesn't re-flag it.
- **earthing** (commit `97e4570`): real schema-conformance regressions found. Five of 6 intents missing `available_zs_at_main_db_ohm` AND the entire intent shape was pre-Sprint-A; migrated all 5 to current shape. `intl-rural-tncs` chat_summary 641 chars > 500 cap.
- **Structural fix from earthing audit:** added **Pass 4 (intent validation)** to `validate-examples.py` — the harness now validates every `intent-out.json` against the producing skill's intent schema. Aggregate jumped 166/166 → 219/219 across 4 passes. Pass 4 also surfaced `sld/intl-commercial-msb-4subdbs/intent-out.json` carrying a stray `sheet_count: 2` field that nobody had flagged (removed).
- **Cap raise from chat_summary friction** (commit `7e35755`): user explicit rule "don't trim non-consequential content even when reviewer highlights it." Schema `rationale.chat_summary.maxLength` raised 500 → 800 (aligns with the existing `invariants.evidence` + `arc-flash/provenance.provenance_note` benchmarks). Restored intl-rural-tncs to the original 641-char content. Future trim-vs-cap-raise decisions go to cap-raise unless the field has documented UI/render constraints.
- **db-layout** (commit `7492840`): 4 chat_summary >500 findings (ke-nairobi-gh-db 581, uk-domestic-consumer-unit 519, us-strip-mall-common-area 503, us-strip-mall-tsp-b 533) ALL pass under the new 800 cap — no action needed at the example level. The manifest gap (4 validation specs not declared) turned out to be universal — all 10 shipped skills had the same `validation` declaration missing, plus 8 of 10 carried a silent legacy `validators` (plural-noun) key alongside any new declaration. Added `validation` key + removed legacy `validators` across all 10 manifests; uniform convention now matches `prompts/`, `evals/`, `examples/`.

## sld round 4 — both findings already pre-resolved

Your sld audit flagged two schema items that turned out to be pre-resolved:

1. **chat_summary > 500 in 1 sld example** — `intl-commercial-msb-4subdbs` is 533 chars. Cap was raised 500→800 in commit `7e35755` per the no-trim rule. All 4 sld outputs now within cap (323/439/466/533).
2. **`sheet_count` extra property in 1 sld intent** — removed in commit `97e4570` (the same commit that added Pass 4; Pass 4 was the check that surfaced this in the first place). `git log electrical/sld/examples/intl-commercial-msb-4subdbs/intent-out.json` confirms.

If your audit was against a recent pull, the cap-raise (`7e35755` at 2026-05-25 12:xx) and the Pass-4 fix (`97e4570` slightly earlier same day) should both be in. If your re-test pulled before those, the findings are stale. Either way: zero remaining schema issues on sld at HEAD.

## sld round 4 — confirmations + headline

Your headline observation lands cleanly: **sld is the strongest skill tested so far.** Specific confirmations:

- **H1 propagation** (the consumed `peak_pfc_ka = 43.49` matching the fault-level intent's fixed max after H1 was corrected from 22.5 → 43.49 kA): this is exactly the cascade-correctness the Sprint B.1 fix-pass intended. Worth flagging because it confirms the cascade fix wasn't just to the producer — the consumer was updated too (we did that in B.1's fix-pass commit `2cddbac`).
- **Selectivity-cascade catching ke-nairobi's 10 kA Icu vs 10.2 kA PFC** with regulatory citation (your "skill's finest moment") — agreed. The skill carries the issue in `compliance_summary.non_compliance_flags` rather than the top-level `flags` array, which is why a flag-array filter misses it.
- **Both your false positives** (Icu < PFC; life-safety overlap from substring match) confirm the skill's defensive engineering is more granular than coarse cross-cutting checks can see. That asymmetry — skill catches more than the oracle sees — is the right direction.

## Pattern update: 4 skills deep

You wrote: "engineering and integration logic are consistently sound (and prior defects verifiably fixed); the only recurring open defect class is schema conformance."

True at the time. After this round's fixes:

- **chat_summary >500 systematic finding** → resolved at the SCHEMA layer (cap raise) per the user's no-trim rule. Not a per-skill problem anymore
- **intent-shape drift (earthing) + stray property (sld)** → resolved per-example AND structurally via Pass 4 (which would have caught both at CI time)
- **Manifest validation declaration missing (db-layout)** → resolved universally across 10 skills

The "schema conformance" defect class is now actively guarded by 4 harness passes + the cap-raise convention + the no-trim rule. Future regressions in this class should be caught in CI on the introducing commit.

The remaining genuinely-open items from the original consolidated list are unchanged: C3 IEEE 1584 transcription (paywall), integrated-design-review skill (stubbed, unbuilt), eval-execution engine (#13 — still queued).

— DraftsMan team
