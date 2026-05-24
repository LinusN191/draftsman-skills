# Collected External Reviews — 2026-05-22

Reviews of the draftsman-skills repo collected for aggregate remediation planning. Each review preserved verbatim with my extracted-findings summary added.

Status: collecting (1 of 10+ received).

---

## Review 1

**Source:** External reviewer (cloned repo, ran validation toolchain, functional-tested lighting-layout office example)
**Scope tested:** 1 production + 8 beta skills (lighting-layout, sld, db-layout, earthing, fault-level, cable-sizing, arc-flash, arc-flash-labelling, small-power). Predates schematic v1.0 ship.
**Date received:** 2026-05-22

### Verbatim

> I'll start by examining the repository to understand what's in it. This is a repository of MEP (Mechanical, Electrical, Plumbing) engineering skills. Let me clone it and inspect the structure, including which skills are marked beta vs production.
>
> Let me read the SKILLS_STATUS.md to understand which skills are beta vs production. Let me look at the directory structure and the scripts, plus check whether there's a test harness. There's a validation harness. Let me look at it and the production skill's manifest before running tests.
>
> The repo structure and its built-in test harness (`scripts/validate-examples.py`) are clear. Quick note before I run it: these are agent skill files (markdown + JSON schemas), not Claude-runtime skills I can register into my own loader — so "install" here means cloning the repo (done) and setting up its validation toolchain so we can actually exercise the skills. Let me install the dependencies and run the harness across everything.
>
> Structural validation passes cleanly. Let me capture the full output (passes 1 and 2 scrolled off) so I can report per-skill.
>
> All structural tests are green: **143/143** across the 9 beta + production skills (53 golden example outputs, 81 eval definitions, 9 input files). But schema-green only proves the files are well-formed, not that the engineering reasoning is right. Let me add a couple of integrity checks the harness skips, then do a real functional test on one skill.
>
> Two skills (cable-sizing, small-power) show no prompts in my check — that's likely a different manifest shape, not a missing prompt. Let me verify before flagging it.
>
> Found a real (minor) inconsistency: `cable-sizing` and `small-power` have generator/validator/reviewer prompt files on disk, but their manifests don't declare a `prompts` key — so a runtime that loads prompts via the manifest would miss them. Let me confirm the manifest shape.
>
> Confirmed — the two newest beta skills (`cable-sizing`, `small-power`) are missing `prompts`, `evals`, and `examples` declarations in their manifests even though those files exist on disk. A manifest-driven loader would silently skip them. Last check: does the cross-skill intent graph actually close (is every consumed intent produced somewhere)?
>
> Intent graph closes cleanly. Now a genuine functional check — structural validity doesn't prove the engineering is right. Let me take the production skill's office example and independently verify its golden output actually satisfies the lighting math and an eval's pass criteria. Let me independently recompute the lumen-method math rather than trust the stored numbers.
>
> Done — here's where things stand.
>
> **On "install":** I cloned the repo to my workspace and set up its validation toolchain (`jsonschema`, `pyyaml`). One honesty caveat worth stating up front: these are *agent* skill files (markdown prompts + JSON schemas designed for DraftsMan / Claude Code / generic LLM agents). I can read, execute, and test them, but I can't literally register them into my own runtime skill loader the way the built-in skills sit at `/mnt/skills`. So "installed" = cloned and runnable, not "now part of my permanent toolset."
>
> **Scope tested:** the 1 production + 8 beta skills (the 67 stubs have no prompts/schemas to test). I ran three layers of testing.
>
> **1. Structural harness (the repo's own `validate-examples.py`) — 143/143 pass, 0 failures:**
>
> | Skill | Status | Prompts | Evals | Examples | Harness |
> |---|---|---|---|---|---|
> | lighting-layout | production | g/v/r | 8 | 3 | ✓ |
> | sld | beta | g/v/r | 10 | 4 | ✓ |
> | db-layout | beta | g/v/r | 8 | 20 | ✓ |
> | earthing | beta | g/v/r | 9 | 5 | ✓ |
> | fault-level | beta | g/v/r | 9 | 6 | ✓ |
> | cable-sizing | beta | g/v/r | 9 | 4 | ✓ |
> | arc-flash | beta | g/v/r | 9 | 3 | ✓ |
> | arc-flash-labelling | beta | g/v/r | 9 | 3 | ✓ |
> | small-power | beta | g/v/r | 10 | 5 | ✓ |
>
> That covers 53 golden example outputs validated against IR schemas, 81 eval definitions, and 9 input files.
>
> **2. Integrity sweep (things the harness doesn't check):** The cross-skill intent dependency graph closes completely — every `consumes_intents` entry (e.g. sld pulling db-layout + earthing + fault-level) is produced by another skill, with no dangling references.
>
> **3. One real functional test** (because schema-green only proves the files are well-formed, not that the engineering is correct): I took the production `lighting-layout` office example and independently recomputed the lumen method. Room index came out to 1.975 (eval window 1.90–2.05 ✓), the golden output's 20-luminaire count and 603 lx achieved both clear thresholds, the back-solved UF·MF of 0.536 is a realistic office value, and the 125 lm/W efficacy clears the Part L target of 65. The engineering is sound, not just the JSON.
>
> **Two findings worth flagging:**
> - `cable-sizing` and `small-power` have generator/validator/reviewer prompts, evals, and examples *on disk*, but their `skill.manifest.json` files don't declare `prompts`, `evals`, or `examples` keys (unlike the production reference). A manifest-driven loader would silently skip those — easy fix, but real.
> - The repo's "test" harness is structural + the evals are schema-validated *definitions*, not executed assertions. So "all green" ≠ "all 9 produce correct engineering output."
>
> That last point is the obvious next step: I've functionally verified one of nine. I can run the same independent-execution test on the rest (run each generator on its input, check output against the eval assertions and standards), but that's heavy, so I'd rather do it deliberately than dump nine at once.

### Extracted findings

- **F1.1 (Important):** cable-sizing + small-power manifests missing `prompts`, `evals`, `examples` key declarations despite files existing on disk. A manifest-driven runtime loader would silently skip them. Same gap likely deserves audit across all shipped manifests. (Reviewer noted this is the issue Sprint 3-W2c Task 3 A3 audit partially addressed for the singular/plural produces_intent_schema variance — but the prompts/evals/examples declarations weren't part of that audit.)
- **F1.2 (Strategic):** Harness is structural-only — schema validation proves files are well-formed but NOT that engineering reasoning is correct. Evals are validated as definitions, not executed assertions. "All green" ≠ "produces correct output at runtime." This is the LLM-vs-golden execution harness gap Sprint 3-X was originally pencilled for. Reviewer offered to run independent functional tests on the remaining 8 skills one at a time.
- **F1.3 (Positive — sanity confirmation):** lighting-layout office example INDEPENDENTLY VERIFIED — room index 1.975 in window; 20-luminaire count + 603 lx achieved; back-solved UF·MF 0.536 realistic for office; 125 lm/W efficacy clears Part L 65 target.
- **F1.4 (Positive):** Cross-skill intent dependency graph closes cleanly (every consumes_intents resolves to a producer; no dangling references). Sprint 3-W2c Task 3 A2 confirmed this for 15 pairs; review now independently corroborates.

---

## Review 2

**Source:** External reviewer (same as Review 1, continuing the per-skill functional test series)
**Scope tested:** cable-sizing skill — golden example walked end-to-end + recomputed Vd against shipped mV/A/m table
**Date received:** 2026-05-22

### Verbatim

> Starting cable-sizing. Let me pull its examples, a representative input/output, and the eval assertions. Let me extract the golden per-circuit sizing results and the eval assertions.
>
> The selection *logic* looks right at a glance (e.g., C03 lighting radial rejected 1.0 mm² and stepped up to 1.5 mm² on voltage drop). But the absolute Vd numbers look high against my mental BS 7671 figures, so let me check the skill's own mV/A/m table and whether it sizes Vd on Ib or In before I judge it. The Vd is a deferred runtime calc contract, so the example's numbers were authored, not computed by a shipped table. Let me find the actual mV/A/m reference data and check the C03 number directly. Let me pull the actual mV/A/m values for 1.0 and 1.5 mm² from the shipped table and recompute C03 myself.
>
> Now I've found something substantive. Let me check two things: what the C03 "info" flag actually says, and whether the Iz (ampacity) path reconciles with the shipped current-ratings table.
>
> **cable-sizing — PASS on logic, but I found real issues in the worked example and data.** This one is genuinely more "beta" than fault-level was. The framework is right but the numbers and underlying tables don't fully reconcile.
>
> What's sound: the "walk-the-ladder" selection with a `binding_constraint` tag per circuit is good engineering structure, the CPC sizing cites Reg 543.1.3, the 3%-lighting / 5%-power voltage-drop limits are transcribed verified-against-source and applied as the governing rule, and the selected sizes themselves are all sensible real-world UK choices (2.5/1.5 rings on 32 A, 6 mm² cooker, 1.5 mm² lighting, 2.5 mm² immersion).
>
> Three findings worth taking seriously, all surfaced by recomputing against the skill's *own* shipped tables:
>
> 1. **The voltage-drop figures in the example don't reproduce from the shipped mV/A/m table.** C03's rationale rejects 1.0 mm² at "3.4% > 3% lighting limit" and accepts 1.5 mm² at "2.2%". But the shipped Appendix-4 table gives 1.5 mm² = 29 mV/A/m → with Ib = 4.5 A over 22 m that's **1.25%**, and 1.0 mm² works out to ~1.9%. The example's numbers run ~1.75× high. Under the canonical data, **1.0 mm² would actually pass the 3% limit** — so the headline "binding constraint = voltage drop → step up to 1.5 mm²" decision isn't justified by the skill's own table. There's likely an undocumented basis (operating-temperature correction, or sizing on In not Ib); either way it's not reproducible as written.
>
> 2. **1.0 mm² isn't in the shipped tables at all.** The mV/A/m and ratings tables start at 1.5 mm². The walk-up "attempts" 1.0 mm² — a bread-and-butter UK lighting size — but the canonical data to evaluate it isn't shipped.
>
> 3. **PVC-vs-XLPE table mismatch.** The example declares `cable_type: pvc_singles`, but the only ampacity/mV-A/m tables in the repo are the XLPE/thermosetting Table 4D2 set. Voltage drop is barely affected (it's resistance-driven), but **current ratings differ materially** — 90 °C XLPE carries more than 70 °C PVC — so applying XLPE Iz to a cable labelled PVC is potentially non-conservative. No PVC 4D1/4D5 table is shipped.
>
> Net: the live skill defers the actual Vd/ampacity math to a runtime calc tool, so these are really defects in the *golden example and shipped reference tables* — which matters because those examples are what the validation harness green-lit and what regression would anchor to. fault-level reconciled to the decimal; cable-sizing doesn't.
>
> Next up the chain is **db-layout** (consumed by sld, earthing, and the rollup that cable-sizing itself depends on), or I can do **sld** which ties the whole electrical set together. Which do you want?

### Extracted findings

- **F2.1 (Critical — engineering defect):** cable-sizing golden example C03 voltage-drop figures don't reproduce from the shipped mV/A/m table. Example says 1.0 mm² → 3.4%, 1.5 mm² → 2.2%; recomputed against shipped Appendix-4 table gives 1.0 mm² → ~1.9%, 1.5 mm² → 1.25%. Example's numbers run ~1.75× high. **The headline "binding_constraint = voltage drop → step up to 1.5 mm²" decision is NOT justified by the skill's own table.** Likely undocumented basis (operating-temperature correction, or sizing on In not Ib).
- **F2.2 (Important — data coverage):** `shared/standards/electrical/BS7671/` mV/A/m + ratings tables start at 1.5 mm². The example walks 1.0 mm² (standard UK lighting size) as a candidate, but the canonical reference data to evaluate it ISN'T SHIPPED. Either drop 1.0 mm² from the walk-up OR ship the 1.0 mm² row.
- **F2.3 (Important — engineering safety):** Example declares `cable_type: pvc_singles` but only XLPE/thermosetting Table 4D2-set tables are shipped. Current ratings differ materially (90°C XLPE > 70°C PVC); applying XLPE Iz to PVC-declared cable is **potentially non-conservative** (overstates ampacity). No PVC Table 4D1/4D5 shipped. Need PVC tables OR retag example as `cable_type: xlpe_thermosetting` to match shipped data.
- **F2.4 (Strategic — confirmation of F1.2):** Live skill defers actual Vd/ampacity math to runtime calc tool; defects above live in the golden example + shipped reference tables. Harness green-lit them because the schema validated, not because the math reproduced. Reinforces F1.2 (need LLM-vs-golden execution harness + per-decimal recomputation against shipped tables).
- **F2.5 (Positive):** Selection LOGIC is sound — walk-the-ladder + binding_constraint tag + CPC sizing per Reg 543.1.3 + 3%/5% Vd limits per BS 7671 + selected sizes are all sensible UK choices.

---

## Review 3

**Source:** External reviewer (continuing per-skill functional test series)
**Scope tested:** db-layout — UK domestic consumer-unit example walked end-to-end + diversity calc independently recomputed
**Date received:** 2026-05-22

### Verbatim

> db-layout next — it has 20 examples (the most of any skill), and it feeds sld, earthing, and the rollup cable-sizing depends on, so it's load-bearing. Let me look at its examples and a representative UK board. Let me extract all circuits' loads and the golden output's key results (diversity, way count, busbar/incomer rating). Let me verify the diversity calculation — this is the heart of a DB design, and the input gives a single blanket factor.
>
> **db-layout — PASS on layout/protection, but the diversity calc is a real weakness.** The board mechanics are correct; the demand calculation is where it falls down, and that one matters because this skill emits the rollup that downstream sizing consumes.
>
> What's correct: way schedule reconciles exactly (6 used + 6 spare on a 12-way, comfortably above the 2-spare minimum), main switch 100 A = supply, busbar 100 A, and the RCD reasoning is genuinely good — Type A justified for pulsating DC, the grouped-RCD-vs-per-circuit-RCBO cost/resilience trade-off is noted, bathroom Section 701 and the 411.3.3 socket rule are cited correctly.
>
> The problem is diversity. The golden output reports 47 A diversified, which I confirmed is just total connected load (117 A) × the blanket 0.4 factor from the input. But the actual BS 7671 / On-Site Guide method is per-load-type, and when I run it properly the demand is **≈ 89 A — nearly double (1.89×)**. The driver is the 9 kW instantaneous shower: under the OSG it gets *no* diversity (39 A, full load), but the blanket 0.4 cuts it to ~16 A, understating the single largest continuous load on the board. On a 100 A supply that's the difference between ~53 A of headroom (as reported) and ~11 A (reality).
>
> Two specific defects:
> - The skill accepts and applies a single blanket factor without applying — or even flagging — the per-circuit method that BS 7671 actually requires for domestic. It's partly GIGO (the engineer declared 0.4 in the input), but a production skill should catch that a flat factor on an instantaneous shower is non-conservative.
> - The rationale cites "Diversity factor 0.4 (domestic typical per BS 7671 Appendix 1)" — but the Appendix doesn't prescribe a blanket 0.4; it points to the per-load-type table. That's a loose/incorrect citation propping up the weak number.
>
> Because db-layout produces `db-layout-rollup`, this understatement would flow straight into the feeder/tails sizing that cable-sizing and sld pull from — so it compounds with the cable-sizing reservations from the last step.
>
> I spot-checked the domestic board; if you want I can also probe one of the 3-phase examples (e.g. `intl-commercial-tpn-msb`) specifically for phase-balancing logic, which is the other classic DB failure mode.
>
> Next integrator skill is **sld** — it consumes db-layout + earthing + fault-level, so testing it also exercises how cleanly those intents actually flow through. Want sld next, or the 3-phase db-layout balance check first?

### Extracted findings

- **F3.1 (CRITICAL — engineering defect that COMPOUNDS):** db-layout uk-domestic-consumer-unit example uses blanket diversity 0.4 → reports 47A diversified. **Correct per-load-type calc gives ≈89A (1.89× higher)**. The 9 kW instantaneous shower (which gets NO diversity per OSG) is the driver. On a 100A supply: reported 53A headroom vs reality 11A. **This understatement flows into db-layout-rollup → consumed by cable-sizing + sld** — compounds with F2.1/F2.2/F2.3 cable-sizing defects downstream.
- **F3.2 (Important — missing engineering guard):** db-layout skill accepts a single blanket diversity factor without applying OR flagging the per-circuit BS 7671 / OSG method. A production skill should detect that a flat factor on an instantaneous shower is non-conservative + flag it. Currently it's GIGO — engineer declared 0.4, skill accepted silently.
- **F3.3 (Important — incorrect citation):** Rationale cites "Diversity factor 0.4 (domestic typical per BS 7671 Appendix 1)" — but Appendix 1 is the list of referenced British Standards, NOT a diversity prescription. Diversity guidance lives in IET OSG Appendix A (the same misattribution as 3-W2c Task 2 KE-2 fix; recurring pattern). Loose citation propping up the weak number.
- **F3.4 (Test coverage gap):** Reviewer only spot-checked the domestic board. 3-phase examples (e.g. `intl-commercial-tpn-msb`) need separate probe specifically for phase-balancing logic — the other classic DB failure mode. Offer pending.
- **F3.5 (Positive):** Board mechanics correct — way schedule reconciles (6 used + 6 spare on 12-way ≥ 2-spare minimum); main switch 100A = supply; busbar 100A; RCD reasoning genuinely good (Type A for pulsating DC + grouped-RCD-vs-per-circuit-RCBO trade-off + bathroom Section 701 + 411.3.3 socket rule all correct).
- **F3.6 (Strategic compounding risk):** db-layout-rollup is consumed by cable-sizing (Review 2 already found defects) + sld (next review) + earthing + small-power. The 1.89× diversity understatement propagates into ALL downstream skills' feeder/tails/cascade sizing decisions. **Highest-leverage single fix** across the shipped skill set.

---

## Review 4

**Source:** External reviewer (continuing per-skill functional test series)
**Scope tested:** sld — the integrator skill (consumes db-layout + earthing + fault-level); intent consumption + fault-current math + phase-handling correctness
**Date received:** 2026-05-22

### Verbatim

> Now sld, the integrator. Let me look at its examples and check how it consumes the upstream intents — especially whether it re-derives phase allocation or inherits db-layout's dropped-phase gap. sld consumes upstream intents by file path. Let me verify those referenced files exist and check whether the fault-level cascade is consumed correctly. Intent files exist and expose per-node Ik. Now the core SLD test: does it actually *use* those fault levels to rate device breaking capacities at each board, pull the earthing system through, and handle phase?
>
> Strong integration result on fault current — but I need to chase one thing that looks wrong. The SLD consumes the `intl-rural-tt` earthing intent (a **TT** system), yet its output references **TN-C-S**. Let me check whether that's a genuine mismatch.
>
> Good — I was wrong about a value mismatch; the SLD is internally consistent (TN-C-S throughout, matching both its input and the intent it consumes). But that surfaced a *different* real defect: the earthing intent file lives in a folder named `intl-rural-tt` yet emits **TN-C-S**. Let me check whether that earthing example is actually a TT system mis-emitting its intent.
>
> The folder named `intl-rural-tt` is mislabeled — its input, output, and emitted intent are all **TN-C-S**, not TT. Let me confirm across all earthing examples whether a genuine TT case exists at all, since that's a meaningful coverage question.
>
> **sld — the best-integrated skill so far, and it flushed out a real upstream defect.** Three things, including a fair correction to my own hypothesis going in.
>
> **1. Intent integration is genuine and the fault-current math is exactly right.** The earthing and fault-level intent files it references actually exist on disk (not just declared paths), and it really uses them: the SLD's `peak_pfc_ka = 22.5` matches the consumed fault-level intent's TX-1 maximum (22.5 kA) to the decimal. Better still, it correctly takes the cascade *maximum* (22.5 kA at the transformer) rather than the lower declared utility figure (16 kA) when rating LV switchgear — the conservative, correct choice. The 50 kA main-switch breaking capacity yields a correct 55% headroom over the 22.5 kA prospective fault. That's textbook SLD device coordination.
>
> **2. The phase gap does NOT propagate here — and that's correct, not a pass.** I went in expecting the SLD might inherit db-layout's dropped-phase problem. It doesn't carry phase at all — but a single-line diagram *by definition* collapses three phases into one representative line; per-circuit phase allocation belongs on the panel/board schedule, not the SLD. So the SLD is behaving correctly. The takeaway is that the phase-data gap stays located in **db-layout's board output**, where it does matter, and the SLD isn't the place to recover it. Fair correction to my earlier worry.
>
> **3. It surfaced a mislabeled upstream example.** The SLD consumes `earthing/examples/intl-rural-tt/intent-out.json` — but that entire example is actually a **TN-C-S** system, not TT. Everything stays internally consistent (the SLD's TN-C-S adiabatic + 5 s clearance reasoning is correct for what it received), but the folder is misnamed. And chasing it revealed something bigger for the next skill: across all five earthing examples the coverage is **TN-C-S ×3 + TN-S ×2 — zero genuine TT**, despite one folder being named to suggest it. TT matters because it's electrically distinct: the earth-electrode loop impedance is too high for an overcurrent device to clear a fault in time, so an **RCD is mandatory for fault protection**, not just additional protection. That's a real coverage hole.
>
> So sld itself comes out strong — arguably the cleanest integration in the set. The defect it exposed belongs to **earthing**, which is conveniently next and which I've now partly pre-diagnosed: a misnamed example plus missing TT coverage. Want me to go confirm and finish off earthing?

### Extracted findings

- **F4.1 (Positive — strongest skill so far):** sld intent integration is GENUINE — references real on-disk intent files; uses consumed `fault-level` intent's per-node Ik correctly; `peak_pfc_ka = 22.5` matches TX-1 maximum to the decimal; correctly takes cascade maximum (22.5kA at transformer) over lower utility figure (16kA) for LV switchgear breaking-capacity rating; 50kA main-switch yields correct 55% headroom. **Textbook SLD device coordination.**
- **F4.2 (Reviewer self-correction — not a defect):** Initial hypothesis that sld might inherit db-layout's phase gap WAS WRONG. SLD collapses 3-phase into representative line by definition; phase allocation belongs on board schedule (db-layout's domain), not SLD. **sld is behaving correctly.** The phase-data gap stays located in db-layout's board output, not sld.
- **F4.3 (Important — mislabeled example in earthing):** `electrical/earthing/examples/intl-rural-tt/` folder name says TT system, but `input.json` + `output.json` + `intent-out.json` are ALL **TN-C-S**. Internally consistent but folder name is a lie. **Discovered via sld integration test** — would have been invisible to in-skill validation. (Note: this surfaced in 3-W2c Task 1 KE-1 area as well; recurring pattern of misleading-but-not-broken naming.)
- **F4.4 (CRITICAL — coverage hole):** Across all 5 earthing examples: TN-C-S ×3 + TN-S ×2 + **ZERO genuine TT** (despite one folder being named to suggest it). TT is **electrically distinct**: earth-electrode loop impedance too high for overcurrent device to clear fault within time; **RCD is MANDATORY for fault protection** (not just additional protection per § 415.1). The earthing skill cannot claim coverage of TT systems without an actual TT example. (Reinforces F1.2 — coverage matrix needs genuine cross-jurisdiction + cross-system-type testing.)
- **F4.5 (Strategic — integration tests catch what unit tests can't):** sld review surfaced a DEFECT IN UPSTREAM (earthing mislabel + TT coverage hole) that would have been invisible to per-skill validation. Reinforces F1.2 strategic priority: integration / cross-skill cascade testing has higher leverage than per-skill unit tests for the shipped set.
- **F4.6 (Architecture lesson):** The "phase belongs in db-layout output, not sld output" reasoning is correct AND should be documented somewhere (CLAUDE.md? ARCHITECTURE.md?) so future skills don't try to recompute it at the wrong layer. Currently implicit.

---

## Review 5

**Source:** External reviewer (continuing per-skill functional test series)
**Scope tested:** earthing — TN-C-S example end-to-end + checked whether TT logic exists despite missing TT coverage; ran conductor-sizing math against Tables 54.7/54.8
**Date received:** 2026-05-22

### Verbatim

> Now earthing. I've pre-diagnosed the TT gap; let me confirm it bites and verify the core earthing math (Zs / disconnection, conductor sizing) on a real example. Let me extract the golden conductor sizing and check it against BS 7671 Tables 54.7/54.8. The TN-C-S sizing and the RCD logic look nuanced and correct (e.g. `rcd_required = False` for fault protection in TN-C-S, with separate 30 mA additional protection applied). The critical question is whether the skill even *contains* the TT logic, given no TT example exists. Let me check the rules/prompts.
>
> **earthing — and I need to correct my own pre-diagnosis, in the skill's favour.** I expected to find that missing TT examples meant missing TT *logic*. That's wrong: the TT logic is actually present and thorough.
>
> The generator prompt handles TT extensively (24 references): it explicitly states RCD protection is **mandatory for ADS on all final circuits in TT** "because Zs alone won't trip MCBs reliably," requires a consumer earth electrode bonded to the MET, cites Reg 411.5, and works with electrode resistance Ra. The validator encodes this as a hard invariant (INV-6: "TT system — every circuit must have `rcd_required: true`") and even captures the jurisdiction nuances — the GB domestic-socket rule (411.3.3) versus the stricter Kenyan KS 1700 universal-socket-RCD deviation. The reviewer specifically checks for "missing TT requirement when the DNO declines to provide a PME earth." Honestly, the TN-C-S-vs-TT reasoning is some of the most carefully thought-through logic I've seen in this repo.
>
> On the TN-C-S example itself, the engineering checks out: `rcd_required = False` is correct for fault protection in TN-C-S (the OCPD clears via low Zs), with separate 30 mA *additional* protection still applied to the 12 circuits — that fault-protection-vs-additional-protection distinction is a subtle thing many designers get wrong, and the skill gets it right. PME main bonding correctly applies the 10 mm² minimum, and Zs = Ze + (R₁+R₂) with the Zs ≤ Zs_max compliance check is self-consistent (0.358 < 0.488 → pass).
>
> So the real finding is narrower than I forecast, but still real and arguably worse where it counts:
>
> - **Comprehensive TT logic, zero TT coverage.** The single most safety-critical branch — TT forcing `rcd_required: true` on every circuit — has no worked example and no eval exercising it. INV-6 is written but never fired against a golden case. The five examples are TN-C-S ×3 + TN-S ×2.
> - **The misnamed folder isn't just cosmetic.** `intl-rural-tt` contains TN-C-S content, and the generator prompt *itself* references "earthing example is rural TT while upstream is commercial TPN" as a handled scenario — strongly implying that folder was meant to be *the* TT demonstrator and got populated with the wrong system. The intended coverage was planned, then not delivered, and the name now masks the hole.
>
> One thing I'd want the runtime tool to confirm: the feeder CPC and main earthing conductor are both 25 mm² against 95 mm² line conductors. That's below the Table 54.7 simple value (line/2 = 50 mm²) and relies on the adiabatic route — my rough check says 25 mm² only clears adiabatically if disconnection is ≤ ~0.13 s at ~9.8 kA. Plausible with an instantaneous magnetic trip, but it's an assertion deferred to the calc tool, not a verified number.
>
> **Where we are:** of the 9 beta+production skills, I've now functionally tested fault-level (production-grade), cable-sizing (logic good, example/table defects), db-layout (mechanics good, diversity + phase-balancing gaps), sld (cleanest integration), and earthing (strong logic, TT coverage hole). Remaining: **arc-flash**, **arc-flash-labelling**, **small-power**, plus the production **lighting-layout** is already verified. Want me to keep going — arc-flash next?

### Extracted findings

- **F5.1 (Reviewer self-correction — refines F4.4):** TT LOGIC IS PRESENT AND THOROUGH in earthing skill — 24 TT references in generator.md; INV-6 in validator encodes hard rule "TT system → every circuit must have `rcd_required: true`"; jurisdiction nuances captured (GB 411.3.3 socket-only vs KS 1700 universal-socket-RCD). Reviewer flags this as "some of the most carefully thought-through logic I've seen in this repo." **Refines F4.4: the coverage gap is in EXAMPLES + EVALS, not logic.**
- **F5.2 (CRITICAL — coverage hole that bites):** Despite comprehensive TT logic, **zero TT examples + zero TT-firing evals**. INV-6 is written but never fired against a golden case. The most safety-critical branch in the entire earthing skill is unexercised. Add at minimum: 1 TT example (rural cottage on a TT system with mandatory 30mA RCD on every final circuit) + 1 eval that fires INV-6.
- **F5.3 (Important — discovery of original intent):** The misnamed `intl-rural-tt/` folder + the generator prompt's "earthing example is rural TT while upstream is commercial TPN" reference strongly imply **TT coverage was planned and not delivered**. Original folder was meant as THE TT demonstrator; got populated with TN-C-S content. Folder name now masks the missing-coverage hole.
- **F5.4 (Positive — fault-vs-additional-protection nuance handled):** TN-C-S `rcd_required = False` for fault protection (OCPD clears via low Zs) with separate 30mA *additional* protection still applied is **the correct nuanced engineering** — a distinction many designers get wrong. PME main bonding 10mm² minimum applied correctly; Zs = Ze + (R₁+R₂) compliance check (0.358 < 0.488 → pass) is self-consistent.
- **F5.5 (Deferred to runtime — adiabatic CPC sizing):** Feeder CPC + main earthing both 25mm² against 95mm² line conductors. Below Table 54.7 simple value (line/2 = 50mm²); relies on adiabatic route. Reviewer's rough check: 25mm² clears adiabatically only if disconnection ≤ ~0.13s at ~9.8kA. Plausible with instantaneous magnetic trip but DEFERRED to calc tool — not verified per-decimal. Reinforces F1.2 strategic priority (need LLM-vs-golden harness that runs the adiabatic computation).
- **F5.6 (Test-set progress so far):** 5 of 9 functionally tested: fault-level (production-grade), cable-sizing (logic good / example+table defects), db-layout (mechanics good / diversity+phase gaps), sld (cleanest integration), earthing (strong logic / TT coverage hole). Remaining: arc-flash + arc-flash-labelling + small-power.

---

## Review 6

**Source:** External reviewer (continuing per-skill functional test series)
**Scope tested:** arc-flash — UK LV example end-to-end; method-selection path; verified IEEE 1584-2018 vs Lee 1982 fallback; cross-checked DC method (Doan)
**Date received:** 2026-05-22

### Verbatim

> arc-flash now — IEEE 1584:2018 / NFPA 70E. Let me look at its examples and the UK LV case, focusing on the incident-energy method selection and PPE assignment. The input correctly reuses the 22.5 kA fault level from fault-level. Let me pull the golden output — method selected, incident energy, arc-flash boundary, and PPE category.
>
> The method selection is a red flag: it fell all the way back to **Lee 1982** for a 400 V LV node, even though IEEE 1584-2018 is valid and preferred for 208 V–15 kV. Lee is a >15 kV theoretical-max model that over-predicts at LV. Let me find *why* it fell back.
>
> Now this is the key finding. The fallback reason isn't missing input — the input *has* clearing times (0.3 s, 0.2 s). It's that **the skill's own IEEE 1584-2018 coefficients (k1–k7) are shipped as null / "pending-verification,"** so the preferred model can't run and it drops to Lee 1982. Let me check whether *any* example successfully uses IEEE 1584.
>
> **arc-flash — the weakest functional performer so far. Its headline calculation engine is non-operational.** This is the one where the beta label is generous.
>
> The finding: **every AC node in every arc-flash example falls back to Lee 1982.** Not one successfully uses IEEE 1584-2018 — the model the entire skill is nominally built around, and the correct/preferred method for 208 V–15 kV. The reason isn't missing input (the input supplies clearing times of 0.3 s and 0.2 s); it's that the skill's own shipped **IEEE 1584-2018 600 V coefficient set (k1–k7) is null / "pending-verification."** There's a `method-2018-2700V-coefficients.json` file but no verified 600 V set, so all LV work drops to Lee — and even the MV substation example falls to Lee on both nodes, so the 2700 V path isn't exercised either.
>
> Why this matters in practice: Lee 1982 is a theoretical-maximum model intended for **>15 kV**. Using it at 400 V systematically **over-predicts incident energy** and inflates PPE category. The UK example reports 9.8 cal/cm² → PPE Cat 3; the arcing current it used (19.5 kA, 0.87× bolted) is Lee-like and high for LV, where IEEE 1584-2018 would put the arcing-current ratio lower and very plausibly land the result in Cat 2. So the output isn't just deferred-and-illustrative (the numbers carry `tool_call_pending`) — the *method choice* is a real skill decision, and it's the wrong-regime model. Conservative on PPE, but conservative-wrong: it over-specs protection and can over-restrict live work based on a model that doesn't apply at that voltage.
>
> To be fair, several things are done well:
> - The fallback trail is **transparent** — each skipped method records exactly why (null coefficients), and the skill refuses to fabricate unverified coefficients. That's good engineering hygiene, the same discipline that made fault-level trustworthy.
> - **AC/DC differentiation is correct** — the PV example's DC nodes use `dc_doan` (Doan's DC arc-flash method), which is the right call since IEEE 1584 doesn't cover DC.
> - Intent consumption is right (the 22.5 kA reused from fault-level), working distance (455 mm) is standard, and the guard checks (boundary ≥ working distance, PPE consistent with E) are sensible.
>
> But net: it's a well-built scaffold around a calculation it currently can't perform at the voltages that matter. fault-level shipped verified IEC 60909 data and reconciled to the decimal; arc-flash ships null IEEE 1584 coefficients and substitutes a model from the wrong voltage regime. Functionally this is closer to a draft than a working beta.
>
> **Direct implication for the next test:** `arc-flash-labelling` consumes the arc-flash intent, so it will inherit these Lee-derived incident-energy and PPE-category numbers. The interesting question there is whether the *label* (which a worker actually relies on at the panel) faithfully reflects the method/uncertainty, or whether it launders a wrong-regime estimate into an authoritative-looking sticker. Want me to take arc-flash-labelling next?

### Extracted findings

- **F6.1 (CRITICAL — most severe finding to date):** arc-flash skill's headline calculation engine is **NON-OPERATIONAL at LV**. IEEE 1584-2018 600V coefficient set (k1-k7) shipped as null / "pending-verification". **Every AC node in every arc-flash example falls back to Lee 1982** (a >15kV theoretical-max model misapplied at 400V). The 2700V coefficient file exists but MV substation example ALSO falls to Lee on both nodes — 2700V path unexercised too. Reviewer's verdict: "closer to a draft than a working beta."
- **F6.2 (CRITICAL — conservative-WRONG):** Lee 1982 at 400V **systematically over-predicts incident energy → inflates PPE category**. UK example reports 9.8 cal/cm² → PPE Cat 3; with proper IEEE 1584-2018 at 400V would likely land Cat 2. This over-specs protection AND can over-restrict live work based on a model that doesn't apply at that voltage. Not just illustrative — the method choice is a real skill decision.
- **F6.3 (Important — data shipping gap):** Need to ship verified IEEE 1584-2018 coefficient sets for 600V (low-voltage) + verify the 2700V set. These are publicly available in IEEE 1584-2018 Tables; shipping null + falling back to Lee is the substantive gap. Parallel with F2.2 (1.0 mm² row missing from cable-sizing Appendix-4 table) — both are data-shipping holes.
- **F6.4 (Positive — engineering hygiene):** Fallback trail is **transparent** — each skipped method records exactly why (null coefficients); skill refuses to fabricate unverified coefficients. Same discipline that made fault-level trustworthy. **Don't lose this on remediation.**
- **F6.5 (Positive):** AC/DC differentiation correct (PV DC nodes use `dc_doan` since IEEE 1584 doesn't cover DC); intent consumption correct (22.5 kA reused from fault-level — matches F4.1 cascade-max pattern); working distance 455mm standard; guard checks sensible (boundary ≥ working distance; PPE consistent with E).
- **F6.6 (Setup for Review 7):** arc-flash-labelling consumes arc-flash intent → will inherit Lee-derived numbers. **Open question for next review:** does the label faithfully reflect method/uncertainty OR launder a wrong-regime estimate into an authoritative-looking panel sticker (worker-relied-on at the live panel)?
- **F6.7 (Strategic — beta status mismatch):** "beta" label on arc-flash is generous. Need to either (a) bump status DOWN to alpha/draft until coefficients ship + IEEE 1584-2018 fires on at least one example, OR (b) prioritise IEEE 1584-2018 coefficient shipping as a critical-priority fix before any runtime end-to-end test.

---

## Review 7

**Source:** External reviewer (continuing per-skill functional test series)
**Scope tested:** arc-flash-labelling — cross-skill reference resolution; label content vs upstream arc-flash output; provenance/disclaimer audit on the human-facing safety artifact
**Date received:** 2026-05-22

### Verbatim

> arc-flash-labelling, the last of the arc-flash pair. Let me check how it consumes the arc-flash intent and whether the label discloses method/uncertainty or launders the Lee estimate.
>
> Possible broken references — let me verify those consumed paths actually exist, since the arc-flash folders I saw were named differently (`uk-lv-switchgear`, `intl-mv-substation`).
>
> Confirmed — **2 of 3 labelling examples point to arc-flash intent files that don't exist.** The arc-flash folders were renamed (`intl-11kv-substation`→`intl-mv-substation`, `uk-400v-commercial`→`uk-lv-switchgear`) and the labelling `consumed_intent_path` references were never updated. Notably the 143/143 schema harness can't see this — it validates file shapes, not whether cross-skill paths resolve. Now let me check the label content itself: does it disclose the Lee method/uncertainty or present an authoritative number?
>
> Let me verify one thing before I characterize the safety implication: does the label carry *any* method/provenance or provisional marking, or does it present the number bare?
>
> **arc-flash-labelling — the riskiest skill in the set, because it's the human-facing safety output and it presents weak data with unwarranted authority.** Three findings, one of which is genuinely safety-relevant.
>
> **1. Broken cross-skill references (2 of 3).** The `consumed_intent_path` values point to arc-flash examples that don't exist — `uk-400v-commercial` and `intl-11kv-substation` were renamed to `uk-lv-switchgear` and `intl-mv-substation`, and the labelling references were never updated. Only the US example resolves. And the 143/143 schema harness can't catch this, because it validates file shapes, not whether referenced paths resolve. This is exactly the class of regression that only functional testing surfaces.
>
> **2. The label numbers have drifted from the actual arc-flash output.** The UK label states 10.5 cal/cm² @ 450 mm; the real arc-flash `uk-lv-switchgear` output says 9.8 cal/cm² @ 455 mm. Different incident energy, different working distance — because the broken link means the label example was authored independently rather than derived end-to-end. So the example is not a faithful demonstration of the pipeline it claims to represent.
>
> **3. The label launders an unverified, wrong-regime estimate into an authoritative life-safety document.** This is the serious one. The upstream incident energy is (a) Lee-1982-derived — the wrong model for 400 V, which over-predicts — and (b) flagged `tool_call_pending` upstream, meaning it was never actually computed. Yet the label carries **zero provenance**: I searched the entire output for "lee," "method," "draft," "provisional," "estimate," "unverified," "disclaimer" — all zero. It states "10.5 cal/cm², PPE Cat 3" as bare fact in formal BS 5499 / ANSI Z535.4 dress. A worker reads that at the panel and trusts it. An arc-flash label is a life-safety artifact; presenting a provisional, wrong-regime number with no method, no date, and no "draft — not for field use" marker is the wrong default. And it's structural, not just an example slip — the label schema has no field for analysis method or date, so even a correctly-computed value would ship without traceability.
>
> What's done well, to be fair: jurisdiction-aware format selection is clean and correct (UK→BS 5499, US→ANSI Z535.4, INT→ISO 7010, auto-detected), and the PPE clothing descriptions are correctly pulled from NFPA 70E Table 130.7(C)(16) with the right ATPV ratings (≥8 cal/cm² Cat 2, ≥25 Cat 3). The mechanics of label *formatting* are good; it's the *provenance and source-data integrity* that fail.
>
> Also, like earthing's TT branch, the most safety-critical override — RESTRICTED / "no PPE adequate" for IE > 40 cal/cm² — isn't exercised by any example.
>
> **Where we are now:** functionally tested 7 of 9 — fault-level (production-grade), cable-sizing (logic good, data defects), db-layout (mechanics good, diversity + phase gaps), sld (cleanest integration), earthing (strong logic, TT coverage hole), arc-flash (engine non-operational, falls to Lee), arc-flash-labelling (broken links + safety-provenance gap). Plus production lighting-layout verified at the start. Only **small-power** remains. Want me to finish the set with it, and then I can pull together an overall synthesis — which is the "discuss more" you flagged at the very beginning?

### Extracted findings

- **F7.1 (CRITICAL — safety / life-safety):** arc-flash-labelling **launders a wrong-regime, unverified estimate into an authoritative life-safety document**. Upstream incident energy is Lee-1982-derived (wrong model for 400V per F6.2) + flagged `tool_call_pending` upstream (never computed). Label carries **ZERO provenance** — grep for "lee/method/draft/provisional/estimate/unverified/disclaimer" returns all zero. Label states "10.5 cal/cm², PPE Cat 3" as bare fact in formal BS 5499 / ANSI Z535.4 dress. **A worker reads this at the panel and trusts it.** Wrong default for the riskiest skill in the set.
- **F7.2 (CRITICAL — structural):** **Label schema has no field for analysis method or date** — even a correctly-computed value would ship without traceability. This isn't fixable by example-edit alone; the schema needs a `provenance: {method, computed_at, calc_tool_version, is_provisional}` block + the renderer needs to emit "DRAFT — NOT FOR FIELD USE" marking when `is_provisional == true`.
- **F7.3 (CRITICAL — broken cross-skill refs invisible to harness):** **2 of 3 labelling examples reference arc-flash intent files that don't exist.** `uk-400v-commercial` → `uk-lv-switchgear` + `intl-11kv-substation` → `intl-mv-substation` renames not propagated to labelling's `consumed_intent_path`. **Harness can't see this** — it validates file shapes, not whether cross-skill paths resolve. Class of regression that only functional/integration testing catches. Reinforces F1.2 + F4.5.
- **F7.4 (Important — drift between intent producer + consumer):** UK label states 10.5 cal/cm² @ 450mm; upstream arc-flash output says 9.8 cal/cm² @ 455mm. Different IE + different working distance because the broken link (F7.3) meant the label example was authored independently rather than derived end-to-end. **Example is not a faithful demonstration of the pipeline it claims to represent.**
- **F7.5 (Important — coverage gap):** Like F5.2 (earthing TT), the most safety-critical override — **RESTRICTED / "no PPE adequate" for IE > 40 cal/cm²** — isn't exercised by any example. Add at minimum: 1 example with IE > 40 cal/cm² (HV substation typical) + 1 eval that fires the RESTRICTED label path.
- **F7.6 (Positive):** Jurisdiction-aware format selection clean + correct (UK → BS 5499, US → ANSI Z535.4, INT → ISO 7010, auto-detected). PPE clothing descriptions correctly pulled from NFPA 70E Table 130.7(C)(16) with right ATPV ratings (≥8 cal/cm² Cat 2, ≥25 Cat 3). **Label formatting mechanics good; provenance + source-data integrity fail.**
- **F7.7 (Strategic — riskiest skill):** Reviewer's explicit assessment: "the riskiest skill in the set, because it's the human-facing safety output and it presents weak data with unwarranted authority." **This deserves the highest remediation priority** even above F6 (arc-flash engine) because arc-flash's defect at least surfaces via fallback-trail transparency; labelling's defect is invisible to the human-in-the-loop at the panel.

---

## Review 8

**Source:** External reviewer (final per-skill test + cross-cutting synthesis)
**Scope tested:** small-power — UK + US examples; cable-sizing intent consumption resolution; socket↔circuit referential integrity; topology-by-jurisdiction. **PLUS:** synthesis of all 9 skills' findings.
**Date received:** 2026-05-22

### Verbatim — small-power

> Last one — small-power, which consumes the cable-sizing intent. Let me check the UK example (the one that consumes cable-sizing) for topology-by-jurisdiction, the circuit↔socket cross-referencing, and special-locations handling. Let me verify the two things that matter most here: whether the cable-sizing consumption is actually wired (this example's headline feature) or just authored, the socket↔circuit cross-reference integrity, and whether the US example correctly switches to radial topology.
>
> Strong results: socket↔circuit cross-referencing is **perfect** (zero dangling refs in both examples), and topology-by-jurisdiction is **correct** (UK rings + radials; US all-radial, no rings). Let me verify the headline feature — that the consumed cable-sizing path resolves (given labelling's broken links) and the Zs math is right.
>
> **small-power — PASS, and the second-strongest beta after fault-level.** It does the cross-skill integration that labelling fumbled, correctly.
>
> - **Cable-sizing consumption is properly wired.** `consumed_intents_paths.cable-sizing` resolves to a valid fixture, and the per-circuit `verified_zs_ohm` is derived from it with `tool_call_pending = False` — i.e. genuinely resolved, not deferred. That's the headline v1.1 feature working, and a direct contrast with arc-flash-labelling's broken paths.
> - **Referential integrity is perfect.** Every socket's `circuit_id` resolves to a declared circuit — zero dangling references across both the UK and US examples. Where db-layout dropped the phase field, small-power keeps its hybrid IR (circuits[] ↔ rooms[].sockets[]) fully consistent.
> - **Topology-by-jurisdiction is correct** — UK gets ring finals + dedicated radials; US gets all-radial (no rings) + dedicated radials. That's exactly the BS 1363 vs NEC distinction, and it's easy to get wrong.
> - RCD posture (Type A 30 mA per §411.3.3 on socket circuits) and the Zs values (ring ≈ 0.93 Ω, under the Type B 32 A limit) are both right.
>
> Only minor notes: the manifest still omits prompts/evals/examples declarations (shared with cable-sizing), and the special-locations branch (Section 701 bathrooms) isn't exercised in this particular example.

### Verbatim — synthesis (across all 9 skills)

> That's all 9. Here's the synthesis you flagged at the start.
>
> **Per-skill scorecard (functional, not just schema):**
>
> | Skill | Verdict | The decisive finding |
> |---|---|---|
> | fault-level | Production-grade | IEC 60909 reconciled to the decimal; correctly used dual c-factors and caught the declared-vs-calculated divergence |
> | sld | Strong | Cleanest integration; consumed fault-level peak exactly, rated switchgear correctly |
> | small-power | Strong | Cross-skill consumption wired + perfect referential integrity + correct jurisdiction topology |
> | earthing | Good logic, coverage hole | TT logic is excellent but has zero TT examples; one example misnamed |
> | lighting-layout | Verified (production) | Lumen method recomputed independently, all checks cleared |
> | db-layout | Mechanics good, two gaps | Blanket diversity understates demand ~2×; phase-balancing unimplemented + phase data dropped |
> | cable-sizing | Logic good, data defects | Example Vd numbers don't reproduce from shipped tables; 1.0 mm² missing; PVC/XLPE table mismatch |
> | arc-flash | Engine non-operational | IEEE 1584 coefficients null → every AC node falls back to wrong-regime Lee 1982 |
> | arc-flash-labelling | Riskiest | Broken intent links (2/3) + presents unverified Lee/pending estimates as authoritative life-safety labels with zero provenance |
>
> **Cross-cutting patterns worth more than any single skill:**
>
> 1. **Schema-green ≠ correct.** The repo's own harness passed 143/143, yet functional testing found a wrong-regime calculation engine, a ~2× demand understatement, dropped phase data, non-reproducible example numbers, broken cross-skill links, and a safety-provenance gap. Every one of those is invisible to schema validation. If you adopt this, the test harness needs a functional layer: resolve all cross-skill `*_path` references, and re-derive at least one number per example from the shipped tables.
>
> 2. **Two tiers of maturity hide under one "beta" label.** fault-level / sld / small-power ship *verified* data and reconcile cleanly. cable-sizing / arc-flash ship *null or unverified* reference data (mV/A/m gaps, null IEEE 1584 coefficients) and lean on fallbacks or authored example numbers. The honesty is real — the skills refuse to fabricate coefficients and flag `pending` — but the practical effect is that arc-flash can't do its core job at LV today.
>
> 3. **The most safety-critical branches are the least tested.** Earthing's TT→RCD-mandatory, arc-flash's RESTRICTED (IE > 40), labelling's provenance disclosure — the high-consequence paths are exactly the ones with no worked example. That's the inverse of where test coverage should concentrate.
>
> 4. **One genuinely safety-relevant defect**, not just a quality one: arc-flash-labelling rendering a Lee-derived, `tool_call_pending` number as a definitive BS 5499 / ANSI label with no method, date, or "draft" marker. I'd treat that as a blocker before any field use, independent of the rest.
>
> If it's useful, the natural next step is to turn this into a prioritized issue list against the repo (the manifest gaps and broken paths are quick fixes; the diversity method, IEEE 1584 coefficients, phase preservation, and label provenance are substantive). Happy to draft that, or to go deeper on any single skill.

### Extracted findings — small-power

- **F8.1 (Positive — second-strongest beta):** small-power does the cross-skill integration that labelling fumbled, correctly. Cable-sizing intent consumption properly WIRED — `consumed_intents_paths.cable-sizing` resolves; per-circuit `verified_zs_ohm` derived from it with `tool_call_pending = False`. **Headline v1.1 feature working** + direct contrast with F7.3 labelling broken paths.
- **F8.2 (Positive — referential integrity perfect):** Every socket's `circuit_id` resolves to a declared circuit. Zero dangling references across UK + US examples. Where db-layout drops the phase field, small-power keeps hybrid IR (circuits[] ↔ rooms[].sockets[]) fully consistent.
- **F8.3 (Positive — jurisdiction-aware topology):** UK gets ring finals + dedicated radials; US gets all-radial (no rings) + dedicated radials. Correct BS 1363 vs NEC distinction. Easy to get wrong; got right.
- **F8.4 (Positive):** RCD posture (Type A 30mA per §411.3.3 on socket circuits) + Zs values (ring ≈ 0.93 Ω under Type B 32A limit) both right.
- **F8.5 (Important — manifest gap recurrence):** Manifest still omits prompts/evals/examples declarations (shared with cable-sizing, per F1.1). Same gap as F1.1; needs single fix across both.
- **F8.6 (Coverage gap):** Special-locations branch (Section 701 bathrooms) not exercised in this example. Add or document explicitly.

### Extracted findings — synthesis (cross-cutting)

- **F8.7 (CRITICAL — meta-finding "schema-green ≠ correct"):** Repo's harness 143/143 PASSED yet functional testing found:
  - wrong-regime calculation engine (F6.1)
  - ~2× demand understatement (F3.1)
  - dropped phase data (db-layout, surfaced repeatedly across reviews)
  - non-reproducible example numbers (F2.1)
  - broken cross-skill links (F7.3)
  - safety-provenance gap (F7.1 + F7.2)
  
  **EVERY ONE OF THESE IS INVISIBLE TO SCHEMA VALIDATION.** Harness must add a functional layer: (a) resolve all cross-skill `*_path` references; (b) re-derive at least one number per example from shipped tables. **This is the highest-priority architectural finding across all 8 reviews.**
- **F8.8 (Strategic — two tiers under one "beta" label):** **Tier A (production-grade-as-claimed):** fault-level + sld + small-power ship verified data + reconcile cleanly. **Tier B (mislabeled as beta; actually alpha/draft):** cable-sizing + arc-flash ship null or unverified reference data; lean on fallbacks or authored example numbers. The honesty is real (refuses to fabricate; flags `pending`) but practical effect: **arc-flash can't do its core job at LV today.** Recommendation: bifurcate status labels or rename Tier B to alpha/draft.
- **F8.9 (Strategic — coverage inverted):** The MOST safety-critical branches are the LEAST tested. Earthing's TT→RCD-mandatory; arc-flash's RESTRICTED (IE > 40); labelling's provenance disclosure. **Test coverage concentration is exactly backwards** from where it should be. Future eval design should explicitly prioritize "high-consequence path" tests over "happy path" multiplication.
- **F8.10 (BLOCKER for field use):** Per reviewer's explicit assessment: "One genuinely safety-relevant defect, not just a quality one: arc-flash-labelling rendering a Lee-derived, tool_call_pending number as a definitive BS 5499 / ANSI label with no method, date, or 'draft' marker. **I'd treat that as a blocker before any field use, independent of the rest.**"
- **F8.11 (Per-skill scorecard captured):** 9 skills × verdict + decisive finding documented above in synthesis verbatim. **3 strong + 1 verified production + 2 mechanics-good-with-gaps + 1 logic-good-data-defects + 1 engine-non-operational + 1 RISKIEST.**
- **F8.12 (Recommendation):** Reviewer offers to draft prioritized issue list against the repo. Manifest gaps + broken paths = quick fixes; diversity method + IEEE 1584 coefficients + phase preservation + label provenance = substantive. **This naturally becomes the aggregate remediation plan** the user signalled in the original review-collection workflow.

---

## Review 9

**Source:** Reviewer 2 (new reviewer; appears to have runtime context — references Sprint 3-M B.1 dependency resolver, Sprint 3-N DocumentOrchestrator, matrix runner, orchestrator.py:89)
**Scope:** Manifest format compliance audit across 75 manifests (10 beta + 65 stubs); orthogonal to Reviewer 1's engineering-correctness findings
**Date received:** 2026-05-22

### Verbatim

> Skills repo audit — what needs to be fixed
> Scope: 75 manifests, of which 10 are beta+ (the ones that actually run) and 65 are stubs (no work needed yet). All issues below are in the 10 beta skills; stubs are out of scope until they're flipped to beta.
>
> **Issue 1 — Legacy consumes_intents format (8 skills, blocks DEP)**
> What's wrong: Sprint 3-M B.1 changed the dependency resolver to expect dict-shape entries with skill_id, intent_name, version_constraint. Upstream skills still ship the legacy bare-string list, causing `TypeError: string indices must be integers` on every DEP check.
>
> Current shape (broken):
> ```
> "consumes_intents": ["fault-level"]
> ```
> Required shape:
> ```
> "consumes_intents": [
>   {
>     "skill_id": "fault-level",
>     "intent_name": "fault-level",
>     "version_constraint": "^1.0"
>   }
> ]
> ```
>
> Files to fix (8):
>
> | Skill | Current consumes_intents value | Needs to become |
> |---|---|---|
> | electrical/arc-flash/skill.manifest.json | ["fault-level"] | [{skill_id:"fault-level", intent_name:"fault-level", version_constraint:"^1.0"}] |
> | electrical/arc-flash-labelling/skill.manifest.json | ["arc-flash"] | [{skill_id:"arc-flash", intent_name:"arc-flash", version_constraint:"^1.0"}] |
> | electrical/cable-sizing/skill.manifest.json | ["db-layout-rollup", "fault-level"] | Two dict entries, one per producer/intent |
> | electrical/db-layout/skill.manifest.json | ["fault-level", "lighting-layout"] | Two dict entries |
> | electrical/earthing/skill.manifest.json | ["db-layout"] | [{skill_id:"db-layout", intent_name:"db-layout-rollup", version_constraint:"^1.0"}] |
> | electrical/fault-level/skill.manifest.json | ["db-layout-rollup"] | [{skill_id:"db-layout", intent_name:"db-layout-rollup", version_constraint:"^1.0"}] |
> | electrical/sld/skill.manifest.json | ["db-layout"] | [{skill_id:"db-layout", intent_name:"db-layout", version_constraint:"^1.0"}] |
> | electrical/small-power/skill.manifest.json | ["cable-sizing"] | [{skill_id:"cable-sizing", intent_name:"cable-sizing", version_constraint:"^1.0"}] |
>
> Note on db-layout-rollup: the producer skill is db-layout, the intent emitted is db-layout-rollup. Some consumers list "db-layout-rollup" as the producer — that's wrong; the producer is "db-layout" and the intent name is "db-layout-rollup". The dict shape forces this distinction.
>
> **Issue 2 — Legacy produces_intent format (9 skills, will block consumers post-fix)**
> What's wrong: Sprint 3-M B.1 also expects each produces_intents entry to be a dict with name, version, schema_path. Upstream uses either a single bare string or a list of strings.
>
> Current shape (broken):
> ```
> "produces_intent": "earthing"
> // or
> "produces_intent": ["db-layout", "db-layout-rollup"]
> ```
> Required shape:
> ```
> "produces_intents": [
>   {
>     "name": "earthing",
>     "version": "1.0.0",
>     "schema_path": "electrical/earthing/schemas/earthing-intent.schema.json"
>   }
> ]
> ```
>
> Note the key rename: produces_intent (singular) → produces_intents (plural). The validator looks for the plural form.
>
> Files to fix (9): arc-flash, arc-flash-labelling, cable-sizing, db-layout, earthing, fault-level, lighting-layout, sld, small-power. schema_path values are mostly already declared in the manifest under produces_intent_schema (singular) or produces_intent_schemas (dict) — just need to be merged into the new dict structure.
>
> **Issue 3 — Missing chat_type declaration (9 skills, soft warning)**
> What's wrong: Only fire-alarm declares chat_type: "drawing". The other 9 beta electrical skills don't declare it explicitly. The backend's _resolve_chat_type in skills_manifest.py falls back to "drawing" by default, so this currently works — but it's brittle and will silently misroute if a manifest is moved to a different folder.
>
> Recommendation: Add explicit "chat_type": "drawing" (or "calculation" where applicable) to each of:
> arc-flash, arc-flash-labelling, cable-sizing ← probably "calculation", db-layout, earthing, fault-level ← probably "calculation", lighting-layout, sld, small-power.
>
> For Sprint 3-N, document skills will need "chat_type": "document" (or "output_format": "document" — both are accepted by the manifest validator post-3-N).
>
> **Issue 4 — Missing example input.json (1 skill, blocks GEN)**
> File: electrical/fire-alarm/examples/uk-small-office/
> What exists: brief.md, ir.json
> What's missing: input.json
>
> The matrix runner needs input.json to seed the discovery items for generation. Without it, GEN fails immediately with input.json missing.
>
> Fix: Convert the existing brief.md content into a structured input.json matching the skill's expected discovery shape (room_dims_mm, ceiling_height_mm, occupancy_category, alarm_category per the manifest). Or copy from a sibling skill's example if conventions are well-established.
>
> **Issue 5 — No document skill has outline.yaml (Sprint 3-N blocker)**
> Affects: All 6 document stubs (cable-schedule, design-statement, method-statement, om-manual, specification, tender-report) plus bq.
>
> Sprint 3-N's DocumentOrchestrator requires an outline.yaml per skill. Without it, the chat handler raises FileNotFoundError. Document skills also can't be flipped from status: stub to beta until they have:
> - outline.yaml (section list + intent reads + hints)
> - chat_type: "document" (or output_format: "document")
> - consumes_intents in dict shape pointing at producing skills
> - An examples/*/input.json for matrix runs
>
> This is the Task C.6 work that was deferred during Sprint 3-N execution. Lowest-effort path to a demoable 3-N: author documents/specification/outline.yaml with 5-8 sections and flip its status to beta. The plan's Sprint 3-N spec includes a reference outline you can copy.
>
> **Summary by effort**
>
> | Fix | Files touched | Effort | Unblocks |
> |---|---|---|---|
> | Migrate consumes_intents to dict shape | 8 manifests | ~1 hour | DEP phase for 8 skills |
> | Migrate produces_intent → produces_intents dict | 9 manifests | ~1 hour | Future consumers + 3-M B.1 strict mode |
> | Add explicit chat_type | 9 manifests | ~15 min | Routing robustness (soft fix) |
> | Add fire-alarm/examples/uk-small-office/input.json | 1 file | ~10 min | fire-alarm GEN |
> | Author 1 document outline.yaml + flip to beta | 1 skill | 2-4 hours | All of Sprint 3-N visible end-to-end |
>
> Sequence: issues 1-2 are pure mechanical conversions and should land together in a single commit. Issue 3 is cleanup. Issue 4 is independent. Issue 5 is the bigger product win — the lowest-effort path to make the whole 3-N investment visible.
>
> Once issues 1, 2, and 4 land in the submodule, the matrix should run 9/10 green on Anthropic (once the orchestrator hardcoded-Anthropic line at orchestrator.py:89 is also fixed for non-Anthropic providers like DeepSeek).

### Extracted findings

- **F9.1 (CRITICAL — blocks runtime entirely):** Sprint 3-M B.1 dependency resolver requires DICT-SHAPE `consumes_intents` entries with `{skill_id, intent_name, version_constraint}`. **All 8 consumer skills ship bare-string list.** Every DEP check fails with `TypeError: string indices must be integers`. This means **none of the 8 skills resolve their upstream dependencies at runtime today.** This is invisible to my own harness (schema validates the bare-string list against eval.schema.json fine). **Runtime is non-functional for the cross-skill cascade.**
- **F9.2 (CRITICAL — same severity, blocks future consumers):** `produces_intent` (singular bare-string OR list-of-strings) → must become `produces_intents` (plural array of dicts with `{name, version, schema_path}`). Note the KEY RENAME (singular→plural) — the validator looks for the plural form. Currently shipped values across all 9 producer skills. Schema_path values mostly already exist under legacy `produces_intent_schema` / `produces_intent_schemas` — needs MERGE into new dict form.
- **F9.3 (Important — reviewer's correction of a real conceptual error):** **PRODUCER vs INTENT distinction.** "Some consumers list `db-layout-rollup` as the producer — that's wrong; the producer is `db-layout` and the intent name is `db-layout-rollup`." This is a real conceptual error I propagated in my own Sprint 3-W2c A2 audit and the schematic v1.0 sprint (consumes_intents lists "db-layout-rollup" as if it were a producer; correctly the producer is "db-layout" emitting that intent). The dict shape forces the distinction. **Need to audit my own work for this confusion.**
- **F9.4 (Important — soft):** `chat_type` field not declared in 9 beta electrical manifests; only fire-alarm declares it. Backend `_resolve_chat_type` falls back to "drawing" — works today but brittle. Add explicit `chat_type: "drawing"` (calculation for cable-sizing + fault-level; document for Sprint 3-N docs).
- **F9.5 (Important):** `electrical/fire-alarm/examples/uk-small-office/` has brief.md + ir.json but missing `input.json` → matrix runner GEN fails immediately. Quick fix.
- **F9.6 (Strategic — Sprint 3-N blocker):** No document skill has `outline.yaml`. Sprint 3-N DocumentOrchestrator requires it (raises FileNotFoundError without it). Document skills can't flip from stub→beta until they have outline.yaml + chat_type:"document" + dict-shape consumes_intents + examples/*/input.json. **Lowest-effort path to demoable 3-N:** author documents/specification/outline.yaml + flip to beta.
- **F9.7 (Strategic):** External-system finding outside the skills repo: orchestrator.py:89 has hardcoded Anthropic provider; blocks non-Anthropic (DeepSeek) until that line is fixed. NOT in skills repo — but flagged because it gates "matrix runs 9/10 green" outcome.
- **F9.8 (Orthogonal to Reviewer 1):** Reviewer 1 = engineering correctness (numbers reproduce; logic right). Reviewer 2 = manifest contract compliance (loader can parse). **Both axes need remediation.** F9.1+F9.2 are runtime-loader blockers; F1-F8 are engineering-correctness defects. A skill could be 100% correct on one axis and 0% on the other (and is, today: small-power is engineering-strong per F8.1-F8.4 but its `consumes_intents: ["cable-sizing"]` won't load at runtime per F9.1).
- **F9.9 (Effort breakdown captured):** Issues 1+2 (consumes/produces dict migration) = 2 hours single commit. Issue 3 (chat_type) = 15 min. Issue 4 (fire-alarm input.json) = 10 min. Issue 5 (1 document outline.yaml + flip) = 2-4 hours. **Total mechanical fixes = ~4-6 hours before unblocking 9/10 matrix-green outcome.**
- **F9.10 (Architecture-level lesson):** My own Sprint 3-W2c Task 3 A3 manifest audit MISSED this — I audited for naming variance between produces_intent_schema (singular) vs produces_intent_schemas (plural array) and concluded the singular/plural variance was "semantically correct" (1 intent vs multi-intent). **But Reviewer 2 reveals the runtime expects ENTIRELY DIFFERENT FIELD NAMES** (consumes_intents must be dict array; produces_intents [plural] not produces_intent [singular]). My audit was wrong about what shape runtime actually wants. Reinforces F8.7 (need to verify against actual runtime loader, not just the static schemas in this repo).

---

## Review 10

**Source:** Reviewer 1 (returning — built proper fidelity-matched oracle that applies the skill's own formulas; recomputed every node in all 6 fault-level examples)
**Scope tested:** fault-level (full per-node recomputation across all 6 examples); RETRACTS earlier "production-grade" assessment
**Date received:** 2026-05-22

### Verbatim

> Agreed — let me build it properly. First I need to learn the skill's *actual* modelling rules (single-phase formula, superposition handling, c-factors, κ) so the oracle matches the skill's intent rather than my assumptions. Let me read the generator prompt and calc contract. The prompt gives me the exact rules: three-phase uses `c·V/(√3·Z)`; single-phase L-N uses **`c·U/(2·Z_loop)`** (divisor 2, not √3 — confirming my domestic flags were harness noise); κ = 1.02 + 0.98·exp(−3·R/X); and standby generators use ATS changeover (so utility-only at TX is *correct*, not an omission). Let me encode this faithfully and re-adjudicate every node.
>
> My oracle has two of its own bugs — the single-phase detector misclassified `uk-domestic` as 3-phase, and the label string is inverted (√3 printed as "2"). That's the iterative-fidelity problem I warned about, live. Let me fix detection and read the raw stored values for the suspect nodes so I can adjudicate exactly.
>
> Now I can adjudicate every flag precisely. The fidelity-matched oracle (with correct single-phase, c-factor, and κ rules) separates real defects from my oracle's own noise — and the result is significant.
>
> **fault-level — full per-node recomputation of all 6 examples:**
>
> | Example | Nodes | Verdict |
> |---|---|---|
> | ke-nairobi-industrial | 5/5 | ✅ Every node reconciles to <1% |
> | uk-commercial-3storey | 7/7 | ✅ Every node reconciles to <1% |
> | us-strip-mall-retail | 7/7 | ✅ Every node reconciles to <1% |
> | intl-commercial-with-genset | 5 | ❌ 3 confirmed defects |
> | us-industrial-with-motors | 5 | ❌ 1 confirmed defect (+1 oracle false positive) |
> | uk-domestic-single-source | 5 | ❌ z↔Ik unreconciled at every node |
>
> **Three confirmed, precisely-characterized defects:**
>
> 1. **`intl-genset` TX-1: physically impossible impedance.** `z_total = 0.005 Ω` is *below* the transformer's own impedance (~0.0058 Ω for 1600 kVA), and produces 48.5 kA under the skill's own formula versus the stated 22.5 kA — inconsistent by 2.15×. It contaminates MSB-1, MSB-1.BUSBAR, DB-L1 downstream, **and** flows into the SLD via the consumed intent (the "55% headroom" I praised rests on this node).
>
> 2. **Double c-factor on HV nodes (`intl-genset` and `us-motors`).** Both store `ifault_ka_max = declared_PSCC × 1.10` (17.6 = 16×1.10; 27.5 = 25×1.10) while their `z_total` was *also* derived using c=1.10. The c-factor is applied twice — once in the impedance, once on the current. The three clean examples use the declared PSCC directly without the extra ×1.10, so the declared-PSCC handling is non-deterministic across the suite.
>
> 3. **`uk-domestic-single-source`: z never reconciled.** The Ik values look intentional (1.575 = 1.5×1.05, declining downstream), but `z_total` satisfies *no* documented formula — not three-phase √3, not single-phase ÷2, not the declared-PSCC ZQ back-calc. Unlike `uk-commercial` (which back-calculated z to match its declared value), this example left z as unreconciled scaffolding.
>
> **One honest false positive:** `us-motors` MCC-1 (35 vs my 31.98) is **not** a defect — that's the induction-motor fault contribution correctly added at the MCC per IEC 60909 §4.5, which my oracle doesn't model. I'm flagging it as mine, not theirs.
>
> **The headline you need:** I called fault-level "production-grade" earlier — based on spot-checking `uk-commercial`, which is genuinely flawless. Full per-node recomputation of *every* example reveals defects in **half of them (3 of 6)**. Every one is invisible to the 143/143 schema harness, and invisible to spot-checking, because the broken examples are internally schema-valid and the *intent files faithfully carry the wrong numbers forward* (which is why my earlier "intent matches output 6/6" check passed — consistency to a wrong value is still consistency).
>
> That is the direct, concrete answer to your "100%, no single fault" goal: even the strongest skill in the repo has faults in half its examples, and you only find them by recomputing every node against the skill's own equations. The schema layer cannot see arithmetic; spot-checks miss whichever example happens to be the clean one.
>
> I now have a working, fidelity-matched fault-level oracle (two of my own bugs fixed along the way — itself a reminder that the oracle needs the same scrutiny as the skill). The natural next step toward full coverage is to harden it (add motor/UPS superposition so it stops false-positiving, plus the declared-PSCC reconciliation rule) and then build the equivalent oracles for cable-sizing (BS 7671 App 4) and earthing (Zs/adiabatic), plus the cross-cutting path-resolver and eval-assertion executor. Want me to harden the fault-level oracle to zero false positives first, or move on and stand up the cable-sizing oracle next?

### Extracted findings

- **F10.1 (RETRACTION — major):** Reviewer 1's earlier "fault-level = production-grade" verdict (F8.11 scorecard) is **RETRACTED**. Based on spot-checking only `uk-commercial-3storey`. Full per-node recomputation of all 6 examples reveals **defects in 3 of 6 (50%)**. fault-level is NOT production-grade as previously characterized.
- **F10.2 (CRITICAL — engineering + downstream contamination):** `intl-commercial-with-genset` TX-1 has `z_total = 0.005 Ω` which is **physically impossible** (below transformer's own ~0.0058 Ω for 1600 kVA). Skill's own formula on that z produces 48.5 kA vs stated 22.5 kA — **inconsistent by 2.15×**. Contaminates MSB-1, MSB-1.BUSBAR, DB-L1 downstream. **Flows into SLD via consumed intent** — sld's "55% headroom" praise from Review 4 (F4.1) was based on this contaminated number. Need to revisit F4.1 verdict.
- **F10.3 (CRITICAL — non-deterministic skill behavior):** Double c-factor application on HV nodes in `intl-genset` and `us-motors`. Both store `ifault_ka_max = declared_PSCC × 1.10` (17.6 = 16×1.10; 27.5 = 25×1.10) while `z_total` was ALSO derived using c=1.10. **C-factor applied twice — once in impedance, once on current.** The three clean examples use declared PSCC directly without the extra ×1.10. **Declared-PSCC handling is non-deterministic across the example suite.**
- **F10.4 (Important):** `uk-domestic-single-source` `z_total` satisfies **NO documented formula** (not three-phase √3, not single-phase ÷2, not declared-PSCC ZQ back-calc). Ik values look intentional (1.575 = 1.5×1.05 with downstream decline) but z is unreconciled scaffolding. `uk-commercial` back-calculated z to match its declared value; `uk-domestic` did not. Inconsistent example-authoring discipline.
- **F10.5 (CRITICAL META — "no single fault" target is much harder):** "Even the strongest skill in the repo has faults in half its examples." Invisible to 143/143 schema harness AND invisible to spot-checking because broken examples are schema-valid + intent files faithfully carry wrong numbers forward (consistency-to-a-wrong-value is still consistency). **Per-node oracle recomputation against the skill's own equations is the ONLY way to detect this class.** Reinforces F1.2 + F8.7 architectural finding at a much higher severity than previously characterized.
- **F10.6 (Oracle development meta-lesson):** Reviewer's own oracle had 2 bugs (single-phase detector misclassified uk-domestic; √3 label string inverted). **The oracle needs the same scrutiny as the skill.** Iterative-fidelity problem: building an oracle that matches the skill's intent (not the reviewer's assumptions) requires reading the generator prompt + calc contract carefully. **Implication for our remediation plan:** if we build the LLM-vs-golden harness recommended in F1.2/F8.7, we'd need to build it carefully or it'll produce false positives.
- **F10.7 (Positive — what's truly clean):** `ke-nairobi-industrial` (5/5) + `uk-commercial-3storey` (7/7) + `us-strip-mall-retail` (7/7) all reconcile to <1%. These are the genuinely production-grade examples. The skill IS capable of producing correct output; the defect is example-authoring discipline + non-deterministic declared-PSCC handling.
- **F10.8 (False positive disclosed):** `us-motors` MCC-1 (35 vs oracle's 31.98) is **NOT** a defect — induction-motor fault contribution correctly added at the MCC per IEC 60909 §4.5; reviewer's oracle doesn't yet model motor superposition. Honest disclosure builds confidence in the rest of the findings.
- **F10.9 (Roadmap — natural next steps):** Harden fault-level oracle (motor/UPS superposition + declared-PSCC reconciliation rule). Then build equivalent oracles for cable-sizing (BS 7671 App 4) and earthing (Zs/adiabatic). Plus cross-cutting path-resolver + eval-assertion executor (= the F1.2/F7.3/F8.7 architectural ask).

---

## Updated severity stack (post-Review-10)

The retraction shifts the picture significantly. fault-level was the lone "production-grade" skill claimed in Review 8 synthesis; it now joins the defect list.

**Critical updates:**
- F4.1 (sld cleanest integration; 55% headroom): downstream of F10.2 contaminated TX-1; the praise depends on a wrong number propagated via intent
- F8.11 per-skill scorecard: fault-level row must move from "production-grade" to "logic good when applied correctly; non-deterministic across examples"
- F10.5: the "schema-green ≠ correct" meta-finding (F8.7) is even more severe than previously characterized — also "spot-check-green ≠ correct"

---

## Review 11

**Source:** Reviewer 1 (continuing — built cable-sizing oracle that recomputes voltage drop + corrected ampacity per circuit against shipped BS 7671 Appendix 4 tables; all 4 cable-sizing examples)
**Scope tested:** cable-sizing (full oracle recomputation); 2 confirmed defects + 1 oracle false-positive disclosed
**Date received:** 2026-05-22

### Verbatim

> On to cable-sizing. Let me learn its exact selection rules and the shipped table structure so the oracle recomputes faithfully against BS 7671 Appendix 4. Note: `cable-current-ratings.json` is deprecated; the canonical table is `appendix4-cable-ratings.json`. Let me check whether it carries ampacity (It) columns plus the Ca/Cg correction factors, so I know what the oracle can recompute. The canonical table has both `rating_A` (ampacity) and `mVAm`, but the Ca/Cg correction factors aren't in it. Let me locate those, then build the cable-sizing oracle to recompute voltage drop and ampacity per circuit across all examples. Found the canonical `appendix4-correction-factors.json` (grouping: 2→0.8, 3→0.7, 4→0.65; ambient 30 °C→1.0). I have everything. Let me check the non-UK example input shapes, then build and run the cable-sizing oracle across all 4 examples. All examples share the `circuits_declared` schema. Let me build the cable-sizing oracle — recomputing voltage drop and corrected ampacity per circuit against the shipped BS 7671 tables — and run it.
>
> This surfaced a lot — but as with fault-level, I have to separate real defects from my oracle's own blind spots (it doesn't model ring quartering, used the single-core table for SWA cables, and compared segment vs cumulative Vd). Let me verify the two highest-value *real* candidates before reporting: the 3-phase Vd pattern and the ke MSB-1 "Iz < In" overload.
>
> cable-sizing oracle complete. Both candidates adjudicated cleanly:
>
> **(a) Confirmed real defect — three-phase voltage drop computed against the wrong voltage.** On the feeders, the stated Vd% matches `÷230` (phase voltage), not `÷400` (line voltage):
>
> - ke F02: correct 3-phase Vd = **1.00%**, stated **1.8%** (matches the ÷230 error: 1.73%)
> - ke F03: correct **0.57%**, stated **1.05%** (÷230 error: 0.99%)
>
> So every three-phase circuit's voltage-drop percentage is inflated by √3 (~73%) because it's divided by 230 V instead of 400 V. This is systematic across examples, fully reproducible, and is the generalised, now-*explained* version of the lone Vd discrepancy I first flagged on the UK lighting circuit. It over-states drop, so it's conservative-wrong — it would cause unnecessary cable upsizing and would fail a design-office QA check.
>
> **(b) That "Iz < In overload" on ke MSB-1 was my oracle's fault, not the skill's.** The cable is `xlpe_swa` on installation method E (free air), and the skill correctly used the SWA / method-E rating to get `iz_corrected = 326 A > In 315 A` — passes. My oracle wrongly used the single-core clipped-direct table, getting 282 A. I'm owning that as a false positive; the skill is right.
>
> **The two genuine findings that survive scrutiny:**
> 1. The **3-phase Vd-denominator error** above.
> 2. A **data-provenance gap**: PVC and SWA cables are sized with individually-correct values (e.g. 4 mm² PVC → 28 A), but the repo ships only XLPE single-core (4D2) tables — so those numbers can't be traced to any shipped reference, the PVC (4D1/4D5) tables aren't all present, and 1.0 mm² is still absent entirely.
>
> **Oracle artifacts I'm owning (not skill defects):** ring finals C01/C02 (my oracle lacks the ring-quartering rule, so its "overload" and 6% Vd are wrong — the skill's ring values are correct), the SWA table mix-up above, and segment-vs-cumulative Vd mismatches. And to be fair to the skill: it correctly differentiates ring vs radial, SWA vs single-core, and applies the 3%/5% limit selection properly.
>
> **Where this leaves the bigger picture.** Two oracles built, two skills with confirmed systematic defects the 143/143 schema harness couldn't see — and *both oracles also threw false positives* that needed domain-aware adjudication (superposition, single-phase, rings, SWA). That's now a doubly-confirmed law for your "100%, no single fault" goal: credible certification needs fidelity-matched oracles that encode every modelling rule, **and the oracles themselves need validating** — I've hit my own bugs in both passes.
>
> Remaining on the build plan: the **earthing** oracle (Zs = Ze + R₁+R₂, adiabatic CPC, the untested TT branch), plus two cheap cross-cutting passes that catch a *different* fault class than recomputation — a **path-resolver** (would have caught arc-flash-labelling's broken links in seconds) and an **eval-assertion executor** (would catch the empty-`invariants` / missing-`citations` assertions I noticed). Those two cross-cutting checks are low-effort and high-yield. Want me to do earthing next, or knock out the cross-cutting path-resolver + eval-executor first since they're fast and sweep all 9 skills at once?

### Extracted findings

- **F11.1 (CRITICAL — explains F2.1 root cause):** 3-phase voltage drop systematically computed against ÷230 V (phase) instead of ÷400 V (line). **Every 3-phase circuit Vd% inflated by √3 (~73%)**. Reproducible across multiple examples (ke F02: 1.00% correct / 1.8% stated; ke F03: 0.57% / 1.05%). **Generalized, now-explained version of F2.1.** Conservative-wrong → unnecessary cable upsizing + would FAIL a design-office QA check. **Single fix to formula yields multi-skill correction across cable-sizing's entire 3-phase footprint.**
- **F11.2 (Important — refines F2.2/F2.3):** Data-provenance gap. PVC + SWA cables sized with individually-correct values (e.g. 4 mm² PVC → 28 A) **but repo ships only XLPE single-core 4D2 tables**. PVC tables (4D1/4D5) not all present + 1.0 mm² still absent (same as F2.2). Sized numbers can't be traced to any shipped reference. Need to ship 4D1/4D5 + add 1.0mm² row to 4D2.
- **F11.3 (Positive — skill capabilities):** cable-sizing correctly: (a) differentiates ring vs radial topology; (b) differentiates SWA vs single-core cable construction; (c) applies 3%/5% Vd limit selection per circuit type properly. Skill capability is sound; example data + Vd formula are the defects.
- **F11.4 (Oracle false-positive disclosed — own-work honesty):** ke MSB-1 "Iz < In" was oracle's bug: oracle used single-core clipped-direct table; skill correctly used SWA method-E (iz_corrected = 326 A > 315 A In). Honest disclosure. Also: ring quartering rule + segment vs cumulative Vd are oracle gaps. **Owns 3 of own bugs alongside finding 2 real skill defects.**
- **F11.5 (META — "doubly-confirmed law" for the certification goal):** Reviewer's verbatim: "credible certification needs fidelity-matched oracles that encode every modelling rule, **and the oracles themselves need validating** — I've hit my own bugs in both passes." Reinforces F10.6 and escalates F1.2/F8.7 to a fundamental architectural requirement: any LLM-vs-golden harness needs (a) skill-specific fidelity-matching to skill's own equations, (b) own-validation discipline to prevent false positives, (c) domain-aware adjudication for cases the oracle can't model (motor superposition, ring quartering, etc.).
- **F11.6 (Roadmap continues):** Remaining oracles to build: earthing (Zs = Ze + R₁+R₂, adiabatic CPC, untested TT branch). Plus 2 cheap cross-cutting passes that catch a DIFFERENT fault class than per-skill recomputation:
  - **Path-resolver** — would catch arc-flash-labelling's broken consumed_intent_paths (F7.3) in seconds
  - **Eval-assertion executor** — would catch the empty-`invariants` / missing-`citations` assertions reviewer noticed during cable-sizing work
  Reviewer flags these as "low-effort, high-yield, sweep all 9 skills at once."

---

## Review 12

**Source:** Reviewer 1 (cross-cutting sweep #1 + #2 — path-resolver + eval-assertion executor across all 9 skills)
**Scope tested:** All 9 skills (path resolution: 111 cross-references; eval execution: every assertion against every output)
**Date received:** 2026-05-22

### Verbatim

> Proceeding with the two cross-cutting sweeps — they're fast, hit a *different* fault class than recomputation, and cover all 9 skills at once (which directly serves the 100%-coverage goal). First the path-resolver: scan every example for cross-references and check they resolve on disk. The sweep independently re-confirmed labelling's two broken links and found three more. Let me check whether the softer ones (the KS1700 annex pointer and the earthing test-fixtures) exist anywhere in the repo before characterizing them.
>
> Adjudication: the KS1700 annex pointer is a **false positive** (the file exists; my resolver mis-parsed an in-prose path — owning it). The other four are real: the two labelling `consumed_intent_path` hard breaks, plus two earthing `payload_ref`s pointing at `test-fixtures/*.json` that **don't exist anywhere** — so that earthing example can't actually run end-to-end as wired. Now the eval-assertion executor: do the evals assert on fields that actually exist in the example outputs?
>
> This is the most consequential cross-cutting result yet — but my checker is coarse (it flags `.length` pseudo-properties and grabs `.schema.json` out of `matches "X.schema.json"` strings), so I have to filter those artifacts and verify the real ones. Let me confirm the genuine pattern.
>
> All four verified, airtight. After filtering my checker's own artifacts (`.schema.json` grabbed from `matches` strings, and `.length` pseudo-properties), here's what's real — and it's the most systemic finding of the whole session.
>
> **The evals don't actually validate against the examples.** Across 8 of 9 skills, eval assertions reference output fields that are absent from every example output:
>
> - **`ir.invariants.INV-N.passes` — asserted by 5 skills (fault-level, db-layout, earthing, arc-flash, arc-flash-labelling), populated in 0 of 37 example outputs.** Not even the key is present. Every invariant assertion across those skills is unexercisable against the golden set.
> - **`ir.citations matches "^IEC 60909..."` — asserted by 3 skills, but no structured `citations` field exists** (citations live in rationale prose). Can't pass.
> - **`ir.emitted_intents` / `ir.intent_emitted`** — asserted by 3 skills, but intents live in a *separate* `intent-out.json`, not in `output.json`. Field/location mismatch.
> - **earthing** evals assert a richly-keyed rationale (`assumptions`, `constraints`, `design_methodology`, `key_decisions`, `regulatory_basis`, `risks`…) — the example outputs use `rationale.sections[]` instead. Different schema entirely.
> - **db-layout** asserts `ir.busbar.rating_a` and `ir.incoming.phase_arrangement`; outputs use `board` / `incoming_supply`, and `phase_arrangement` doesn't exist — directly tying back to the phase-drop defect I found earlier (the eval *wants* to check phase, but neither the path nor the data exists).
> - **arc-flash** asserts `ir.nodes`; the output uses `ir.cascade`.
> - **lighting-layout — the *production* reference skill — is not exempt:** its eval asserts `ir.controls.lamp_efficacy_lm_per_w`, but that field lives under `calculation_summary`, not `controls`; and `ir.flags` doesn't exist in the output.
>
> Only `sld` came back clean — and that's partly because its evals assert almost no resolvable `ir.*` paths in the first place.
>
> **Why the 143/143 harness never caught any of this:** it validates eval files against the eval schema, and output files against the IR schema — two independent shape checks. It never executes a single assertion against a single output. So the "evals" function as aspirational specs that have drifted from the actual output schemas, not as tests. The SKILLS_STATUS.md "≥5 evals, ≥3 examples" production bar is met by *counting files*, not by passing executed checks.
>
> ---
>
> **Consolidated cross-cutting scorecard (this round, all 9 skills):**
>
> | Check | Result |
> |---|---|
> | Cross-reference path resolution | 111 refs, **4 genuinely broken** (labelling ×2 hard, earthing ×2 dangling fixtures); 1 false positive (mine) |
> | Eval assertions vs example outputs | **8 of 9 skills** assert fields absent from all outputs; `invariants` empty across 5; even the production skill mismatches |
>
> **The reframed bottom line on your goal.** You asked whether we can get to "100% of all examples, no single fault." After two recompute oracles and two cross-cutting sweeps, the honest state is:
> 1. Recomputation finds real arithmetic/method faults (fault-level: 3 of 6 examples; cable-sizing: systematic 3-phase Vd error).
> 2. Path resolution finds broken cross-skill wiring (2 skills).
> 3. Eval execution finds that the test assets themselves don't run against the examples (8 of 9 skills).
>
> So "no single fault" is currently a long way off — but more importantly, **the repo's own quality gates structurally cannot detect any of these three fault classes.** Reaching your goal isn't a matter of inspecting examples; it requires building the missing test infrastructure: fidelity-matched recompute oracles per calc skill, the path-resolver in CI, and — the biggest gap — an eval executor that actually evaluates assertions against outputs *and* a reconciliation of the eval schema with the output schema so the two stop drifting.
>
> What's left on the build: the **earthing** recompute oracle is the one remaining calculation oracle (Zs = Ze + R₁+R₂, adiabatic CPC, plus the never-tested TT branch). After that, the highest-leverage move is packaging all four checkers (2 oracles + path-resolver + eval-executor) into a single runnable CI suite so this becomes repeatable rather than a one-off audit. Want earthing next, or shall I assemble what we've built into one harness and hand you the prioritized defect list?

### Extracted findings

- **F12.1 (CRITICAL — most systemic finding in entire collection):** **8 of 9 skills' evals reference output fields that are ABSENT from every example output.** Examples:
  - `ir.invariants.INV-N.passes` asserted by 5 skills (fault-level, db-layout, earthing, arc-flash, arc-flash-labelling) — **populated in 0 of 37 example outputs**. Every invariant assertion across those 5 skills is unexercisable against the golden set.
  - `ir.citations matches "..."` asserted by 3 skills — no structured `citations` field exists (citations live in rationale prose)
  - `ir.emitted_intents` / `ir.intent_emitted` asserted by 3 skills — intents live in separate `intent-out.json`, not `output.json` (field/location mismatch)
  - earthing evals assert `assumptions/constraints/design_methodology/key_decisions/regulatory_basis/risks` — examples use `rationale.sections[]` (different schema entirely)
  - db-layout asserts `ir.busbar.rating_a` + `ir.incoming.phase_arrangement` — outputs use `board` + `incoming_supply` + phase_arrangement doesn't exist
  - arc-flash asserts `ir.nodes` — output uses `ir.cascade`
  - **lighting-layout (THE PRODUCTION SKILL) is not exempt** — asserts `ir.controls.lamp_efficacy_lm_per_w` but field is under `calculation_summary`; `ir.flags` doesn't exist
  - Only `sld` came back clean (partly because it asserts almost no resolvable `ir.*` paths in the first place)
- **F12.2 (CRITICAL — STRUCTURAL ROOT CAUSE):** **The 143/143 harness validates eval files against eval schema AND output files against IR schema — TWO INDEPENDENT SHAPE CHECKS. It NEVER executes a single assertion against a single output.** "Evals" function as **aspirational specs that have drifted from actual output schemas, not as tests.** The "≥5 evals, ≥3 examples" production bar is met by COUNTING FILES, not by passing executed checks. **Every eval across the repo is dead code.**
- **F12.3 (Important):** Path-resolver sweep — 111 cross-references checked; **4 genuinely broken** (labelling ×2 from F7.3, plus 2 NEW: earthing `payload_ref`s pointing at `test-fixtures/*.json` that don't exist anywhere → earthing example can't run end-to-end as wired). 1 false positive (own KS1700 annex pointer parsing).
- **F12.4 (Direct ramification for my own work):** The 10 schematic v1.0 evals I shipped in Task 9 (eval-01 through eval-10) NEED VERIFICATION that their assertions actually match the schematic IR shape — not just that they pass eval.schema.json validation. Same for the 81 baseline evals across the 3 post-3W2a formats. **The Sprint 3-W2a/b/c eval migrations standardized SCHEMA conformance but did NOT verify assertion-vs-output match.** This is a category of debt I introduced + propagated.
- **F12.5 (Reframed certification goal):** Three fault classes found by the four checkers:
  1. **Recomputation faults** (fault-level 3 of 6; cable-sizing systematic 3-phase Vd error)
  2. **Path-resolution faults** (2 skills broken — labelling + earthing)
  3. **Eval-vs-output drift** (8 of 9 skills — most systemic)
  **Repo's own quality gates structurally cannot detect any of these three fault classes.** Reaching "100% no single fault" requires building missing test infrastructure: per-skill recompute oracles + path-resolver in CI + **eval executor that actually evaluates assertions against outputs** + reconciliation of eval schema with output schema (so they stop drifting).
- **F12.6 (Architectural recommendation for repeatable harness):** Reviewer's natural next step — package all 4 checkers (2 oracles + path-resolver + eval-executor) into a single runnable CI suite. **Highest-leverage architectural move.** Without it, all the per-skill recompute findings have to be re-run manually on each release.
- **F12.7 (Test status hygiene):** The SKILLS_STATUS.md production bar of "≥5 evals, ≥3 examples" is materially misleading — it counts files, not passing executed checks. Suggest reframing bar as "≥5 evals where every assertion executes successfully against ≥1 golden example, ≥3 examples that validate via cross-skill path-resolver."
- **F12.8 (Earthing oracle pending):** Earthing recompute oracle is the one remaining calculation oracle — Zs = Ze + R₁+R₂, adiabatic CPC, plus the never-tested TT branch (would surface F5.5 deferred adiabatic CPC question + INV-6 TT-RCD assertion that's currently dead code per F12.1).
- **F12.9 (Honesty + roadmap):** Reviewer's verbatim: "**'No single fault' is currently a long way off — but more importantly, the repo's own quality gates structurally cannot detect any of these three fault classes.**" The architectural-debt cleanup is a precondition for the 100% goal; per-skill fixes alone won't get there.

---

## Review 13

**Source:** Reviewer 1 (closing — earthing oracle + runnable `functional_audit.py` + prioritized `DEFECT_REGISTER.md`)
**Scope:** Earthing oracle (Zs reconciliation across 46 circuits in 5 examples) + harness packaging + prioritized defect register synthesis
**Date received:** 2026-05-22

### Verbatim

> Finishing both pieces. First the earthing oracle — let me confirm the exact output fields, then recompute Zs consistency and the RCD logic across all 5 examples.
>
> Major earthing finding. The `intl-rural-tt` example marks 4 circuits as `zs_compliance: "pass"` when Zs exceeds the maximum by 3–10× (0.318 vs 0.046, 0.466 vs 0.183) — meaning the overcurrent device cannot disconnect in time, yet it's labelled compliant. The other 42 circuits across the four good examples reconcile perfectly. Let me check the RCD status on those 4 to characterize it exactly.
>
> Confirmed — and this is the most serious single defect of the entire audit. The `intl-rural-tt` earthing example marks **4 circuits as `zs_compliance: "pass"` with `rcd_required: false`, while Zs exceeds Zs_max by 3–10×.** That means the overcurrent device physically cannot clear an earth fault in the required time, no RCD is flagged as a substitute, and the circuit is certified compliant anyway. The other 42 circuits across the four good examples reconcile perfectly, so earthing's Zs logic is sound *except* in the one example that's also misnamed and carries the wrong system type — three of my earlier threads converging on one broken file.
>
> Now let me assemble everything into a runnable harness and the defect register.
>
> The harness runs end-to-end. Let me confirm the CRITICAL findings landed (they sort to the top, above the `tail` window) and get the totals.
>
> Harness confirmed: 43 findings, 4 CRITICAL at the top. Now the prioritized defect register.
>
> Done — both deliverables are ready, and the last two pieces are complete.
>
> **Earthing oracle (the final calc oracle):** 42 of 46 circuits reconcile perfectly — the Zs = Ze + (R₁+R₂) logic and the pass / pass_with_rcd / fail_needs_rcd verdicts are exact across the four good examples. The exception is the critical C1 defect: `intl-rural-tt`'s 4 circuits certified `pass` with Zs 3–10× over the maximum and no RCD. That single broken example is where three earlier threads converge (misnamed folder, missing TT coverage, and now false-pass verdicts).
>
> **`functional_audit.py`** — one runnable harness consolidating all four checkers (path resolver, eval auditor, and the fault-level / cable-sizing / earthing recompute oracles). Run from the repo root, it reports **43 findings, 4 CRITICAL**, and exits non-zero — drop it into CI and it catches the broken-link and eval-drift classes in seconds. I deliberately built it to *flag for triage* rather than hard-fail, and documented its own false-positive sources (single-phase detection, motor superposition, ring quartering) in the file header, because — as this whole exercise showed — the oracle needs the same scrutiny as the skills.
>
> **`DEFECT_REGISTER.md`** — the prioritized list: 3 CRITICAL (safety), 7 HIGH (correctness, with propagation paths noted), 4 MEDIUM (test infrastructure / coverage), 3 LOW (hygiene), plus an explicit "genuinely solid — do not regress" section and a remediation order.
>
> To close the loop on the question you started with — *"can we get to 100% of all examples, no single fault?"* — the honest answer from the full audit is: not today, and the gap isn't a few bad examples. It's three fault classes (arithmetic/method, broken wiring, and evals that don't execute) that the repo's own quality gate structurally cannot see. The path to your goal isn't more manual inspection; it's the infrastructure now in `functional_audit.py`, hardened per-skill and wired into CI. The strongest skills (fault-level's clean examples, sld's integration, small-power's integrity, earthing's Zs logic) prove the underlying engineering is capable of being right — the failures are in unverified data, drifted test assets, and untested safety branches, all of which are fixable in the order the register lays out.

### Artifacts shipped (saved to repo)

- `DEFECT_REGISTER.md` saved to `docs/reviews/DEFECT_REGISTER.md` — full prioritized register
- `functional_audit.py` saved to repo root — runnable harness

### Extracted findings

- **F13.1 (CRITICAL — most serious single defect in entire audit):** `intl-rural-tt` earthing example marks **4 circuits as `zs_compliance: "pass"` with `rcd_required: false` while Zs exceeds Zs_max by 3–10×** (0.318 vs 0.046 max; 0.466 vs 0.183 max). The overcurrent device physically cannot clear earth fault in required time, no RCD as substitute, and the circuit is **CERTIFIED COMPLIANT** anyway. **A designer trusting this ships circuits with no effective fault protection.** This becomes **C1 in DEFECT_REGISTER.md**.
- **F13.2 (Convergence — three earlier threads converge on one file):** `intl-rural-tt` is simultaneously: (a) misnamed (per F4.3 — content is TN-C-S, not TT); (b) missing TT coverage (per F5.2 — should have been the TT demonstrator); (c) producing false-pass Zs verdicts (per F13.1). **One broken file caused three of the earlier findings.** Fix the example → fixes three Tier 3 items at once.
- **F13.3 (Positive — earthing Zs logic is sound):** 42 of 46 circuits across the 4 good examples reconcile perfectly. The Zs = Ze + (R₁+R₂) logic + pass / pass_with_rcd / fail_needs_rcd verdicts are exact. **The skill IS capable of correct output; the defect is in one example only.**
- **F13.4 (CRITICAL — DEFECT_REGISTER.md shipped as polished artifact):** Reviewer's final synthesis — 3 CRITICAL (C1 earthing zs false-pass; C2 labelling unverified-estimate as authoritative; C3 arc-flash LV engine non-operational) + 7 HIGH (H1 fault-level impossible-z; H2 double-c-factor; H3 z-not-reconciled; H4 cable-sizing 3-phase Vd; H5 db-layout diversity; H6 db-layout phase dropped; H7 broken cross-skill refs) + 4 MEDIUM (M1 evals don't validate against examples; M2 no genuine TT; M3 cable-sizing data provenance; M4 untested safety branches) + 3 LOW (L1 manifest declarations missing; L2 deprecated table shipped; L3 misnamed folder) + remediation order. **This becomes the canonical work-to-do reference document.**
- **F13.5 (CRITICAL — functional_audit.py shipped as runnable harness):** Reviewer ships a single end-to-end harness with 4 checkers (path resolver + eval auditor + 3 recompute oracles). 43 findings, 4 CRITICAL, exits non-zero. **Drop into CI and it catches the broken-link + eval-drift classes in seconds.** Designed to flag for triage rather than hard-fail; false-positive sources documented in header. This becomes the **infrastructure asset** the F1.2/F8.7/F12.6 architectural ask needs.
- **F13.6 (Closing answer to the certification question):** Reviewer's final word: "Not today, and the gap isn't a few bad examples. It's three fault classes that the repo's own quality gate structurally cannot see. The path to your goal isn't more manual inspection; it's the infrastructure now in `functional_audit.py`, hardened per-skill and wired into CI."
- **F13.7 (Net positive — capability proven):** "The strongest skills (fault-level's clean examples, sld's integration, small-power's integrity, earthing's Zs logic) prove the underlying engineering is capable of being right — the failures are in unverified data, drifted test assets, and untested safety branches, all of which are fixable in the order the register lays out."

---

(Reviewer 1's audit closed at Review 13. Awaiting any additional independent reviews from other reviewers.)
