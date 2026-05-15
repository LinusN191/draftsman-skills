# Earthing Skill — Known Limitations (Stage 1)

This is the stage 1 (schematic) release. The following are known limitations that will be resolved in later stages.

## Stage 1 scope

- **Output:** schematic IR only
- **Systems supported:** TN-C-S, TT (≈85% of designs)
- **Jurisdictions:** GB, EU, INT, US
- **Calculations:** inline lookup-style only; iterative calcs deferred via `tool_call_pending`

## What is OUT of scope

### IT systems
IT systems (hospitals Group 2, certain industrial) require an Insulation Monitoring Device and have different disconnection rules. Not supported in stage 1. Engineers working on Group 2 medical locations should not use this skill yet.

### Plan-view earthing layout
Stage 1 emits the schematic only. The plan-view layer (which physically locates the MET, electrode runs, ring conductor route, bonding routes) ships in stage 2. The schematic IR will be consumed by the plan-view skill when it exists.

### Declaration-only stage
A lightweight "no-design" mode that emits a compliance declaration referencing an existing earthing design (for tender response, M&E coordination) is deferred to stage 3.

### Earth-fault current calculations
Prospective earth-fault current (Ief) is needed for selectivity and breaking capacity decisions. Not calculated in stage 1 — engineer provides Ze and the skill calculates Zs.

### Lightning protection bonding
BS EN 62305 lightning protection bonding interfaces with the earthing system but is its own skill scope. Stage 1 marks lightning-protection bonds as `bonded_via: "structural"` and defers the design.

### EV charger earthing
Open-PEN protection (BS 7671 Section 722, IET Code of Practice for EV) requires specific measures beyond standard PME treatment. Stage 1 emits a compliance flag if an EV circuit is detected but does not design the open-PEN mitigation.

### Generator-fed earthing
Standby generators have specific earthing requirements (BS 7671 Chapter 55, NEC 250.30). Not supported in stage 1.

## What may produce false positives in evals

- **D6 (Zs margin):** if the engineer provides exact measured Ze (rather than declared), the design may pass with very small margins that the reviewer flags as "low headroom". This is correct engineering judgement, not a bug.
- **INV-3 (bonding completeness):** the skill cannot detect un-declared extraneous-conductive-parts. Garbage-in-garbage-out applies.

## Tool calls awaiting runtime

| Tool name | Purpose | Status |
|---|---|---|
| `calc.electrode_resistance` | Compute Ra from soil resistivity + electrode geometry | tool_call_pending |
| `calc.adiabatic_cpc` | Compute CPC CSA via adiabatic equation for fault energy let-through | tool_call_pending |

When WI3 runtime tools land, the generator prompt's calculation steps will be updated to invoke them instead of accepting engineer input.
