# Earthing Skill — Engineering Philosophy

## Why this skill exists

Earthing design is the single largest source of electrical safety failures in real buildings. Most CAD packages let designers draw an earthing schematic without ever asking whether the disconnection time will actually be met. This skill enforces the BS 7671 / IEC 60364 / NEC reasoning chain *before* the IR is emitted.

## What "good earthing design" looks like

A correct earthing schematic answers six questions in order:

1. **What earthing system applies?** (TN-C-S / TT / TN-S — driven by DNO declaration, not designer preference)
2. **Where is the MET?** (single point, accessible, labelled)
3. **What electrodes — if any — are needed?** (TT: always; TN-C-S: optional but recommended ≤200Ω; NEC: always supplemental)
4. **What bonding is required?** (every extraneous-conductive-part to the MET)
5. **What CPC for every circuit?** (table method OR adiabatic OR NEC 250.122)
6. **Does Zs meet the disconnection time?** (Ze + R1 + R2 ≤ Zs_max for that protective device)

Question 6 is the gate. A design that passes 1–5 but fails 6 is not a design.

## The standards-consumption pattern

This skill's generator prompt names specific JSON files from `shared/standards/` rather than the standards as a body of work. The runtime loads only what the jurisdiction requires:

- GB project → load BS 7671 files
- EU/INT project → load IEC 60364 files
- US project → load NFPA 70 (NEC) files
- All projects → load IEC 60617 symbol files

This selective consumption is what makes the skill viable at production scale — the LLM never sees the 70%+ of standards content irrelevant to the current job.

## Why we defer iterative calculations

Earth electrode resistance (Ra) is a function of soil resistivity, electrode geometry, and arrangement. Iterative calculations are not the LLM's strength — small arithmetic errors compound. This skill declares a tool-call contract (`calc.electrode_resistance`) and marks the result `tool_call_pending: true`. The deterministic Python tool will run when the WI3 runtime lands; until then, the engineer provides Ra as input and the skill validates it against the target.

## What this skill will NOT do

- It will not invent soil resistivity values. If the engineer hasn't provided one, the skill emits a compliance flag asking for it.
- It will not paraphrase code clauses. Every cited clause is taken verbatim from the loaded standards JSON.
- It will not silently switch jurisdictions. The first input is `jurisdiction` and the skill refuses to proceed without it.
- It will not draw a plan-view earthing layout in stage 1. That ships in stage 2.
