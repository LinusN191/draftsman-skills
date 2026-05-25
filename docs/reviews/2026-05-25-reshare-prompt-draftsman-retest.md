# DraftsMan Re-test — Reshare Prompt for External Reviewer

**To:** the external reviewer who shipped `docs/reviews/DEFECT_REGISTER.md` + `functional_audit.py` on 2026-05-22.

**From:** the repo team after the remediation program.

**Anchor:** `git tag audit-cleared-v1.0` on `origin/main` of this repo.

---

## Context

Three days ago you ran a per-skill functional audit, eventually shipping:

- `docs/reviews/DEFECT_REGISTER.md` (3 CRITICAL safety + 7 HIGH correctness + 4 MEDIUM test-infra + 3 LOW hygiene)
- `docs/reviews/2026-05-22-functional-audit-baseline.txt` (raw baseline at commit `4e1c5ee`: 43 findings)
- `functional_audit.py` (runnable harness covering recompute oracles + cross-skill path resolver + eval-vs-output auditor)
- `docs/reviews/2026-05-22-collected-external-reviews.md` (13 reviews, 75 extracted findings F1.1–F13.7)

You also gave us 4 strategic warnings:

1. Reshare must reference a versioned anchor (we did — `audit-cleared-v1.0`)
2. Wiring `functional_audit.py` into CI is the highest-value fix (we did — `.github/workflows/functional-audit.yml`, since Sprint 0)
3. Cause-fix not symptom-paper (we used a per-sprint Sonnet verification fence to check + the audit re-runs the recompute oracles)
4. Memory doesn't carry over (this prompt + the tag + DEFECT_REGISTER pointer carry the context)

## What changed since baseline `4e1c5ee`

We ran a 5-sub-sprint remediation program (Sprint 0 → D), 21 tasks. Per-sprint detail:

- **Sprint 0** — CI wiring + manifest contract migration
  - `.github/workflows/functional-audit.yml` runs the harness on every push/PR
  - 10 skill manifests migrated to dict-shape contract (Reviewer 2 F9.1–F9.5)
  - fire-alarm/uk-small-office input.json created
- **Sprint A** — CRITICAL safety C1+C2+C3 (commits `fcd0d02` + `49bd9fc` + `f009a84`)
  - **C1:** earthing TT folder cause-fixed — `intl-rural-tt` renamed to `intl-rural-tncs` (its content was TN-C-S all along); 4 false-pass circuits now correctly flagged `fail_needs_rcd` with `rcd_required: true` per BS 7671 Reg 411.4.7 + 411.4.9(b)
  - **C2:** arc-flash-labelling provenance block added at SCHEMA level — `{method_applied, computed_at, calc_tool_version, is_provisional, provenance_note}` required; generator prepends "DRAFT — NOT FOR FIELD USE" when `is_provisional=true`
  - **C3:** **HONEST DISCLOSURE — this fix shipped the SAFETY MITIGATION, not the data transcription.** IEEE Std 1584-2018 is distributed only via the IEEE Xplore paywall. The Sprint A.3 implementer source-vetted the model SHAPE (10-coef Iarc + 13-coef IE polynomial-in-V with cross-terms) against ETAP / EasyPower / Bisson Ch. 5 references but could not transcribe verbatim coefficient values without licensed access. The standards files at `shared/standards/electrical/IEEE1584/method-2018-tables-1-3-{600V,2700V}-coefficients.json` honestly carry `_status: "pending-transcription-from-IEEE-1584-2018-tables-1-3"`. The SAFETY consequence (operator trusting a wrong-regime estimate as authoritative) is mitigated by the C2 DRAFT marker convention; the ENGINEERING accuracy gap remains a known open-source constraint requiring licensed-engineer transcription. We'd value your judgement on whether this is an acceptable resolution.
- **Sprint B** — HIGH correctness H1–H7 + Hybrid eval-vs-IR fix M1 (commits `99e1929` through `5eb2324`, 11 commits)
  - **H1–H3:** fault-level recomputes per IEC 60909 — intl-genset TX-1 z corrected (0.005→0.005577 Ω; Ik 22.5→43.49 kA); double-c-factor removed from declared-PSCC HV-1 nodes (intl-genset 17.6→16.0 kA, us-motors 27.5→25.0 kA); uk-domestic-single-source z reconciled to single-phase `Ik1 = c·U₀/(2·Z_S)` per IEC 60909 §6. Validator INV-11 added for internal-consistency reconcile within 1% tolerance with documented special cases for declared PSCC + motor superposition
  - **H4:** cable-sizing 3-phase Vd corrected from ÷230 (phase voltage) to ÷U_LL (400 V INT/EU, 415 V KE/GB) per BS 7671 App 4 + App 12. KE F02 1.8→0.96%, F03 1.05→0.55%, INT C07 1.4→0.79%. Selection preserved per spec ("keep existing CSA unless input demands re-optimization"). Validator INV-11 detects ÷230 regression
  - **H5+H6:** db-layout — per-load-type diversity per IET OSG Appendix A + BS 7671 §311.1 (shower at 1.00 factor, NOT 0.4; uk-domestic 47A→88.91A); TPN phase preservation (17 TPN examples gained `phase` per circuit + `per_phase_loading_a` + `neutral_current_a` per IEC 60364-5-52 §524.2.2). Validator INV-12 (instantaneous diversity) + INV-13 (TPN phase + unbalance) added. Citation corrected: BS 7671 Appendix 1 (informative) → IET OSG App A + §311.1
  - **H7:** 4 broken cross-skill refs repaired — labelling renamed paths fixed (uk-bs5499 + intl-iso7010), db-layout `annex_e_adoption_pathway` string restructured to avoid path-pattern false-positive, earthing test-fixtures payload_refs removed as non-load-bearing cruft
  - **M1:** all 10 IR schemas gained REQUIRED `ir.invariants[]` block (item shape `{id: "INV-NN" zero-padded, passes: bool, severity: critical|high|medium|low, evidence: 20–800 char prose}`); 10 generator prompts populate; 61 example outputs populate (13 hand-curated with 2–3 INV entries per the spec's MVP-populate guidance; 51 emit `invariants: []` empty array, schema-valid); 33+ eval assertions rewritten to point at actual IR field locations
- **Sprint C** — MEDIUM coverage + LOW hygiene (commits `153c689` through `a147ca9`)
  - **M2:** genuine TT example authored at `intl-rural-tt/` (rural off-grid cottage, Ze=200 Ω, Ra·IΔn=6.0V≤50V per IEC 60364-4-41 §411.5.3, all 4 circuits with 30 mA RCDs). INV-06 (TT → RCD mandatory) fires PASS on a real example for the first time
  - **M3:** BS 7671 Tables 4D1A + 4D5A shipped + 1.0 mm² row in 4D2A. **HONEST DISCLOSURE:** methods 4D1A 101/102/103 + 4D5A method D are estimate-only with per-entry `_TODO` and `verification_status: "pending_engineer_transcription"`. Same licensing constraint as C3 — verbatim BS 7671:2018+A2:2022 Appendix 4 values need licensed-engineer access to the published IET PDF. Methods C/A/100 + 4D5A method C are industry-cited reference values
  - **M4:** RESTRICTED arc-flash branch + non-provisional labelling examples authored (HV substation IE=48.2 cal/cm² with `ppe_category: null` per IEEE 1584-2018 §13.1 + NFPA 70E:2024 Table 130.7(C)(15)(A)(b); non-provisional BS 5499 label set with `is_provisional: false` + no DRAFT marker — demonstrates the operational field-use path). **Note:** the IE=48.2 value is engineer-authored to demonstrate RESTRICTED-branch handling, not table-computed from verified IEEE 1584-2018 coefficients (per C3 disclosure above)
  - **L1:** cable-sizing + small-power manifests gained `prompts`/`evals`/`examples` declarations
  - **L2:** deprecated `cable-current-ratings.json` `git rm`'d + 3 stale refs migrated
  - **L3:** intl-rural-tt + intl-rural-tncs both verified present with correct content
- **Sprint D pre-flight** (commit `6ecf70b`) — improved audit oracle's single-phase detection (recognizes `supply_voltage_v == 230 AND hv_side_present is False` as single-phase) + made stale TT-coverage print dynamic. Cleared 5 of 6 prior oracle false-positives without touching skill data

Per-sprint Sonnet verification fence at each sprint's ship task spot-recomputed against shipped tables/formulas to catch symptom-papering.

## Expected harness output at the tagged anchor

```bash
git checkout audit-cleared-v1.0
python3 functional_audit.py
# Expected: TOTAL FINDINGS: 1
# Single remaining: us-industrial-with-motors/MCC-1 motor-superposition
# (motor back-EMF contribution at MCC per IEC 60909 §4.5 — the audit oracle
# cannot model this per its own header disclosure)

python3 scripts/validate-examples.py
# Expected: AGGREGATE 166/166 FULL GREEN, exit 0
```

Both gates run in CI on every push/PR to main:

- `.github/workflows/functional-audit.yml`
- `.github/workflows/validate-examples.yml`

## Per-sprint evidence

Each sprint shipped its own memory file (the per-sprint commit bodies include the same content):

- `sprint-A-shipped.md` — CRITICAL safety C1+C2+C3
- `sprint-B-shipped.md` — HIGH correctness H1–H7 + M1 hybrid
- `sprint-C-shipped.md` — MEDIUM + LOW
- `remediation-program-shipped.md` — program rollup with both honest disclosures

## Like-for-like re-test request

Please:

1. Clone fresh
2. `git checkout audit-cleared-v1.0`
3. Re-run `python3 functional_audit.py`
4. Compare against your baseline (43 findings at `4e1c5ee`)
5. Spot-check any findings you flagged as "must verify the fix is structural not symptom" — the per-sprint Sonnet verification fence touched each but your eye is the gold standard

## We particularly want your judgement on these honest disclosures

### Disclosure 1 — C3 IEEE 1584-2018 coefficient transcription

Sprint A.3 shipped the SAFETY MITIGATION (DRAFT marker convention via C2 schema; transparent fallback trail) but NOT the data transcription. The standards files at `shared/standards/electrical/IEEE1584/method-2018-tables-1-3-{600V,2700V}-coefficients.json` carry `_status: "pending-transcription-from-IEEE-1584-2018-tables-1-3"` because IEEE Std 1584-2018 is distributed only via the IEEE Xplore paywall.

The C.3 RESTRICTED-branch example (`electrical/arc-flash/examples/intl-hv-restricted-substation/`) declares `method_applied: "ieee_1584_2018"` but its IE=48.2 cal/cm² value is engineer-authored to demonstrate the RESTRICTED-branch HANDLING (ppe_category=null, live-work prohibited prose) — not table-computed from verified coefficients.

**Question for you:** is the safety-mitigation-without-data-transcription path acceptable as remediation of C3, or does the open data gap warrant keeping C3 in the open-defect register until verbatim transcription happens?

### Disclosure 2 — M3 PVC table partial completion

Sprint C.2 shipped Tables 4D1A + 4D5A + the 1.0 mm² row in 4D2A. For widely-cited industry-standard methods (4D1A Method C + Method A + Method 100; 4D5A Method C), we used reference values cross-checked against industry-cited sources, flagged `verification_status: "engineer_transcription_C2"`. For rarely-cited methods (4D1A 101/102/103 + 4D5A method D), we shipped the table STRUCTURE with per-entry `_TODO` markers and `verification_status: "pending_engineer_transcription"` — same licensing constraint as C3 (the BS 7671:2018+A2:2022 Appendix 4 published PDF is distributed only via the IET).

**Question for you:** is the structure-with-TODOs-on-rare-methods approach acceptable, or should the rare methods be deleted until verified to avoid the risk of consumers relying on estimate values?

### Disclosure 3 — Sprint B.5 invariants population rate

The `ir.invariants[]` block is REQUIRED in all 10 IR schemas (M1 cause-fix), but only 13 of 64 example outputs (20%) carry populated entries with real evidence prose. 51 emit `invariants: []` (schema-valid empty array). This matches the Sprint B.5 spec's "MVP populate ~10 representative happy-paths; rest emit empty array" guidance — the runtime generator is expected to populate at generation time per the new generator-prompt step in each skill.

**Question for you:** is the MVP-populate approach acceptable, or would you recommend back-filling all 64 examples with their applicable invariants before audit closure?

### Other things to look at

- Did our IEEE 1584-2018 disclosure structure (model shape + cross-checks + pending_status flag) hold up against your independent reading? Or did we miss a public source?
- Did the db-layout per-load-type diversity match your reading of IET OSG App A (especially shower at 1.00; cooker at 10 A + 30% remainder + 5 A socket-on-unit)?
- Did the cable-sizing 3-phase Vd ÷U_LL fix introduce any regression in the SWA examples (which the audit oracle excludes per its header)?
- The remaining 1 finding (`us-industrial-with-motors/MCC-1`) — does the motor-superposition disclaimer hold, or did we miss something there?

## Single outstanding audit finding (1 of 43, all others cleared)

`fault-level/us-industrial-with-motors/MCC-1: Ik 35.0 vs recompute 31.98kA`

The audit oracle's formula `Ik = c·U/(√3·Z)` reads utility upstream only. The stored 35.0 kA includes utility (~32 kA) + induction-motor back-EMF superposition (~3 kA) at the MCC per IEC 60909 §4.5 — which the oracle's header explicitly disclaims as "motor/UPS superposition cases need manual review". The skill output is correct; the audit cannot model it.

## Out-of-scope (not in this program)

These were explicitly deferred for separate work:

- Sprint 3-N document skills (`outline.yaml` per Reviewer 2 F9.6)
- `orchestrator.py:89` hardcoded-Anthropic (lives in runtime repo, not this repo)
- Per-skill recompute oracle expansion to drawing skills (only fault-level / cable-sizing / earthing have recompute oracles)
- Eval-runtime OR-clauses + cross-array predicates (eval schema doesn't support yet; db-layout eval-03 has TODO-flagged placeholder for this)
- Schematic v1.1 polish (ANSI 49 thermal_relay + 50BF regex)
- Lighting-layout content overhaul (3 stub prompts deferred from earlier Sprint 3-W2c)
- IEEE 1584-2018 verbatim coefficient transcription (paywall — needs licensed engineer)
- M3 BS 7671 PVC table 4D1A 101/102/103 + 4D5A method D engineer verification (same constraint)

## Thank you

Your audit was load-bearing — 43 specific findings + a runnable harness made the remediation tractable. The DEFECT_REGISTER's prioritization (severity tiers + propagation paths + "genuinely solid — do not regress" section + recommended remediation order) shaped the entire sprint plan. Looking forward to the re-test report — especially on the three honest disclosures above.

— DraftsMan team
