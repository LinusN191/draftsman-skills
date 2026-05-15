# DB Layout Skill — Engineering Philosophy

## Why this skill exists

Distribution board design is where most circuit-level errors get fixed (or missed) before site. Common failures: oversized OCPDs that won't protect the cable, undersized busbars that can't carry full diversified load, breakers whose Icn is below the prospective fault current at their terminals. This skill enforces the BS 7671 / IEC 60364 / NEC reasoning chain explicitly, and emits both the schedule (the deliverable) and the stable intent contracts other skills consume.

## What "good DB layout" looks like

A correct distribution board schedule answers eight questions in order:

1. **What board?** (consumer unit / DB / MSB / NEMA panelboard — driven by jurisdiction + role)
2. **What enclosure form?** (IEC 61439 Form 1/2a/.../4b for IEC; NEMA Type for US)
3. **What incoming supply?** (V / phases / supply rating / Ze)
4. **What busbar?** (rating ≥ Σ × diversity AND IcW ≥ Ipk)
5. **What ways used / spare?** (with multi-pole accounting)
6. **What OCPD per circuit?** (In ≤ Iz, Icn ≥ Ifault, curve appropriate to load)
7. **What RCD strategy?** (RCBO per circuit vs grouped, jurisdiction-appropriate)
8. **Does selectivity hold?** (cascade verified upstream against published table or computed)

Question 8 is the gate. A design that passes 1–7 but the upstream MCCB cascades unfavorably with a downstream MCB at fault level is unsafe.

## The standards-consumption pattern

This skill loads ONLY the standards files needed for the project's jurisdiction. The generator prompt names 21 specific JSON files; the runtime loads ~10 of those for any given board (5 always-on + 4-6 jurisdiction-gated).

- GB → BS 7671 family
- EU/INT → IEC 60364 family
- US → NFPA 70 (Articles 408, 240, 220, ocpd-coordination)
- All → IEC 60617 symbols + IEC 61439 assembly standards

## Two intents because two consumer patterns

`db-layout` (single-board) — for **panel-schedule, riser, cable-containment**. These consume one board at a time.

`db-layout-rollup` (project-wide) — for **earthing**. Earthing needs full cascade visibility — every circuit at every board — to verify CPC sizing and Zs across the installation.

Two intents = two stable contracts. Future skills get to pick whichever fits their data shape.

## Why we defer selectivity tool execution

Real selectivity is two parts:
1. Look up the manufacturer's cascade table (declarative — possible inline)
2. Compute IEC 60909 cascade fault currents (iterative — diverges if LLM-computed)

This skill always does (1) when the table covers the pair. For (2), it declares a tool-call contract (`calc.iec60909_cascade`) and marks the selectivity result `tool_call_pending: true`. The deterministic Python tool will run when the dedicated `fault-level` skill is built; until then, the engineer provides Ifault values as input.

## What this skill will NOT do

- It will not invent fault currents. If `fault-level` intent is absent AND no engineer Ifault is declared, selectivity is `tool_call_pending`, not faked.
- It will not silently downgrade OCPD ratings to fit a small cable. If `In > Iz`, the IR emits a critical flag.
- It will not paraphrase code clauses. Every cited clause is taken verbatim from the loaded standards JSON.
- It will not draw a plan-view DB location (that's stage 2).
