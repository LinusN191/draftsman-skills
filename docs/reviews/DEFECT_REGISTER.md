# DraftsMan Skills — Functional Audit: Prioritized Defect Register

Scope: the 1 production + 8 beta skills (the 67 stubs have no testable content).
Method: functional testing beyond the repo's schema validator — independent
recomputation against each skill's own standards data, cross-reference path
resolution, and eval-assertion execution. Re-runnable via `functional_audit.py`.

**Headline:** the repo's own gate (`validate-examples.py`, 143/143 pass) checks
file *shapes* only and never executes a calculation, resolves a cross-skill path,
or runs an eval assertion. All findings below are invisible to it.

---

## CRITICAL — safety-relevant; fix before any field use

**C1. earthing / intl-rural-tt — non-compliant circuits certified as compliant.**
4 circuits report `zs_compliance: "pass"` with `rcd_required: false`, while Zs
exceeds Zs_max by 3–10× (e.g. F04: Zs 0.466 vs max 0.183). The overcurrent device
cannot disconnect an earth fault in the required time and no RCD is flagged. A
designer trusting this ships circuits with no effective fault protection.

**C2. arc-flash-labelling — unverified estimates rendered as authoritative labels.**
Incident-energy values are Lee-1982-derived (wrong voltage regime, see C3) and carry
`tool_call_pending` upstream (never computed), yet the BS 5499 / ANSI Z535.4 labels
present them as fact with **no method, date, or "draft" marker**. The label schema
has no provenance field, so this is structural, not just an example slip. An arc-flash
label is PPE-selection life-safety data.

**C3. arc-flash — core calculation engine non-operational at LV.**
IEEE 1584-2018 600 V coefficients ship as null/"pending-verification", so every AC
node in every example falls back to Lee 1982 — a >15 kV theoretical-max model that
over-predicts at 400 V and inflates PPE category. The "5-method fallback chain"
collapses to its last rung. DC nodes correctly use Doan (the one bright spot).

---

## HIGH — correctness defects that propagate downstream

**H1. fault-level / intl-commercial-with-genset — impossible impedance at TX-1.**
`z_total = 0.005 Ω` is below the transformer's own impedance (~0.0058 Ω for 1600 kVA)
and yields 48.5 kA under the skill's own formula vs the stated 22.5 kA (2.15× off).
Contaminates MSB-1, MSB-1.BUSBAR, DB-L1, **and the SLD example that consumes this
intent** (its "55% breaking-capacity headroom" rests on this node).

**H2. fault-level — double c-factor on HV nodes.**
intl-genset HV-1 = 17.6 kA = 16 × 1.10; us-motors HV-1 = 27.5 kA = 25 × 1.10. The
declared PSCC is multiplied by c=1.10 a second time after c is already embedded in z.
Three other examples handle declared PSCC correctly — non-deterministic behaviour.

**H3. fault-level / uk-domestic-single-source — z never reconciled.**
Stored z_total satisfies no documented formula (3-phase √3, single-phase ÷2, or the
declared-PSCC ZQ back-calc). The Ik values look intentional but z is unreconciled
scaffolding, unlike uk-commercial which back-calculated z correctly.

**H4. cable-sizing — three-phase voltage drop computed against phase voltage.**
3-phase Vd% is divided by 230 V instead of 400/415 V, inflating every three-phase
feeder's drop by √3 (~73%). e.g. ke F02: stated 1.8% vs correct 1.0%. Systematic.
Conservative-wrong: forces unnecessary cable upsizing; fails design-office QA.

**H5. db-layout — blanket diversity understates demand ~2× (domestic).**
A flat 0.4 factor applied to a 9 kW instantaneous shower (which gets no diversity
under BS 7671 / On-Site Guide) reports 47 A where the correct demand is ~89 A. On a
100 A supply that is the difference between 53 A and 11 A of headroom. Cited loosely
as "BS 7671 Appendix 1", which prescribes the per-load-type method, not a flat factor.

**H6. db-layout — phase allocation dropped on TPN boards.**
The input's L1/L2/L3 round-robin is discarded in the output (no phase field on any
circuit); no per-phase loading or neutral-current computation. Phase balance — the
classic 3-phase board failure mode — is unimplemented.

**H7. Broken cross-skill references.**
arc-flash-labelling: 2 `consumed_intent_path`s point to renamed arc-flash folders
(`uk-400v-commercial`, `intl-11kv-substation`) that no longer exist. earthing
uk-dwelling-tn-cs: 2 `payload_ref`s point to `test-fixtures/*.json` that exist
nowhere. These examples cannot run end-to-end as wired.

---

## MEDIUM — test-infrastructure & coverage gaps

**M1. Evals do not validate against examples (8 of 9 skills).**
Eval assertions reference output fields absent from every example: `ir.invariants.*`
(5 skills, 0/37 outputs populate it), `ir.citations` (3 skills, no structured field),
`ir.emitted_intents` / `ir.nodes` (field/location mismatches), and even the production
skill (`ir.controls.lamp_efficacy_lm_per_w` actually lives under `calculation_summary`;
`ir.flags` absent). The evals are aspirational specs that have drifted from the output
schemas. "≥5 evals" is met by counting files, not passing executed checks.

**M2. earthing — no genuine TT example; safest branch untested.**
TT logic is thorough in the prompts (RCD mandatory per Reg 411.5) but the example
named `intl-rural-tt` actually contains TN-C-S data. TT→RCD-mandatory is never
exercised — and the same broken example produced C1.

**M3. cable-sizing — data provenance gaps.**
PVC and SWA cables are sized from values not present in the shipped XLPE-only (4D2)
tables; the PVC 4D1/4D5 tables are absent; 1.0 mm² (a standard UK lighting size) is
absent entirely. Numbers may be individually correct but are untraceable to shipped data.

**M4. Untested safety-critical branches.**
arc-flash RESTRICTED (IE > 40 cal/cm², "no PPE adequate") and the label provenance
path have no worked example. High-consequence branches have the least coverage.

---

## LOW — hygiene

- **L1.** cable-sizing and small-power manifests omit `prompts` / `evals` / `examples`
  declarations though the files exist — a manifest-driven loader silently skips them.
- **L2.** `shared/.../BS7671/cable-current-ratings.json` is marked DEPRECATED but ships.
- **L3.** Example folder `intl-rural-tt` is misnamed for its TN-C-S content (see M2).

---

## What is genuinely solid (do not regress)

- **fault-level**: 3 of 6 examples reconcile to <1% (ke-nairobi, uk-commercial,
  us-strip-mall); IEC 60909 c-factor (1.10 HV / 1.05 LV) and κ handling correct where
  reconciled; declared-vs-calculated divergence handled transparently.
- **earthing**: 42 of 46 circuits' Zs logic is exact, with correct pass /
  pass_with_rcd / fail_needs_rcd verdicts; TT *logic* is well-specified.
- **sld**: cleanest integration; correctly takes the cascade *maximum* fault for
  switchgear rating (the consumed number is wrong only because of H1 upstream).
- **small-power**: perfect socket→circuit referential integrity; correct
  ring-vs-radial topology by jurisdiction; cable-sizing intent consumption wired.
- **lighting-layout**: lumen-method output independently verified correct.
- **db-layout**: way schedule, busbar, OCPD and RCD-type reasoning are correct.

---

## Recommended remediation order

1. **C1–C3** immediately (safety). For C3, transcribe & verify the IEEE 1584-2018
   600 V coefficient set, or hard-block label generation while energy is `pending`.
2. **H1–H4** — fix the broken example data and the 3-phase Vd denominator; add an
   internal-consistency invariant (Ik = c·U/(div·Z)) that runs in CI.
3. **H7 + M1** — wire `functional_audit.py` into CI (it catches H7 and M1 in seconds)
   and reconcile the eval schema with the output schema so they stop drifting.
4. **M2–M4, L1–L3** — add a real TT example + RESTRICTED arc-flash example; ship the
   PVC/1.0 mm² tables; fix manifests and the folder name.

## Harness limitations (be honest about the tool)

The recompute oracles flag for human triage, not hard-fail. Known false-positive
sources requiring manual adjudication: single-phase detection (uk-domestic flags are
partly this), induction-motor and UPS fault superposition (us-motors MCC node), ring
quartering and SWA tables (cable-sizing), and declared-binding-value anchoring. A
production oracle must encode these rules; the oracle itself needs the same scrutiny
as the skills (two of my own bugs surfaced during this audit).
