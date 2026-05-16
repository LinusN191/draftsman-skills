# Fault-Level Skill — Engineering Philosophy

## Why this skill exists

Prospective short-circuit current (Ik") is the foundation of switchgear sizing, cable adiabatic protection, and selectivity coordination. Get Ik" wrong and breakers will explode on fault, cables will burn through, and selectivity coordination becomes meaningless. This skill enforces the IEC 60909-0:2016 reasoning chain explicitly.

## What "good fault-level analysis" looks like

A correct fault-level study answers seven questions in order:

1. **What sources?** Utility / generator / UPS / motors — each contributes differently
2. **What's the cascade topology?** Tree of impedances from each source to each fault
3. **What voltage factor c?** 1.05 for Ik"max (breaker rating); 0.95 for Ik"min (protection)
4. **Near or far from generator?** Apply subtransient decrement for NG; constant for FG
5. **What κ at each node?** Peak factor from R/X — drives busbar Ipk withstand
6. **What's Ik" at every protective device?** Compare against device Icn
7. **Does selectivity hold?** Each upstream-downstream pair adequately rated

Question 6 is the gate. A study that passes 1-5 but the 100A MCCB has Icn 10kA at a node where Ik" = 25kA is **unsafe**.

## The standards-consumption pattern

This skill loads jurisdiction-specific files. The generator prompt names 21 specific JSON/md files; runtime loads ~12-15 for any given project.

- All jurisdictions → IEC 60909 family (8 files) + IEC 60617 symbols (2 files)
- GB → BS 7671 fault-current + cable-ratings (3 files)
- EU/INT → IEC 60364 fault-current + cable-ratings (4 files)
- US → NEC Chapter 1, 240, Chapter 9 Table 9 (4 files)

## Two emitted artefacts: IR + intent

`fault-level-ir.schema.json` — full audit trail (every cascade node + selectivity implication + rationale)

`fault-level-intent.schema.json` — slim downstream subset (just the Ifault numbers per node). Consumed by:
- `db-layout` v1.0.0+ — resolves selectivity `tool_call_pending` entries
- `earthing` v1.1+ (future) — cross-validates Ze + R1 + R2 against board Ifault
- `cable-sizing` (Tier 1 Item 3) — adiabatic check at every cable
- `generator-sizing` (future) — Iek for generator dimensioning

## Why we defer the math

IEC 60909-0 calculation involves:
- Complex-number arithmetic (R + jX) at every node
- Iterative cascade impedance addition
- Multi-source superposition (utility + gen + UPS + motors)
- Peak factor κ from X/R (transcendental function)
- Near-generator decrement factor μ (tabulated curves)

LLM inline math diverges from validated Python by >30% in representative cases. This skill **NEVER** inline-computes. It assembles inputs, dispatches `calc.iec60909_cascade` (per WI3 + the calc contract shipped Item 1), interprets results, and emits the rationale.

## What this skill will NOT do

- It will not invent fault currents. If `calc.iec60909_cascade` hasn't run AND no engineer-input fallback is given, emit `tool_call_pending: true` per WI3.
- It will not invent source impedances. If no Zpu nameplate is given, use IEC 60909-2 typical default + a flag in compliance_summary.
- It will not paraphrase IEC 60909-0 clauses. Cite verbatim ("IEC 60909-0:2016 §3.7 Table 1").
- It will not do arc-flash (separate skill scope per NFPA 70E / IEEE 1584).
- It will not do time-graded protection coordination (separate skill scope per IEC 60255).
