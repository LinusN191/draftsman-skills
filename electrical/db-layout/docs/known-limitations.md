# DB Layout Skill — Known Limitations (Stage 1)

This is the stage 1 (schedule + face schematic + selectivity) release. Known limitations resolved in later stages.

## Stage 1 scope

- **Output:** single-board IR (schedule + face one-line schematic + selectivity_results)
- **Project-level rollup:** db-layout-rollup intent emitted alongside per-board IRs
- **Systems supported:** AC LV distribution (consumer units, DBs, MSBs, panelboards, MCCs)
- **Jurisdictions:** GB, EU, INT, US
- **Selectivity:** cascade table lookup inline; IEC 60909 calc deferred via tool_call_pending

## What is OUT of scope

### DC distribution
PV strings, EV chargepoints, battery storage DC sides. Stage 1 v1.0.0 lists these as AC circuits only. Full DC distribution (combiners, isolators per NEC 690) deferred to v1.1.0.

### Plan-view DB location drawing
Stage 1 emits the schedule + face schematic only. The plan-view layer (physically locating the board in the building, cable routes to/from) ships in stage 2.

### Live IEC 60909 calculation
Prospective fault current at each cascade level requires iterative calculation. Not done inline. The selectivity_results entries declare `tool_call_pending: true` until the dedicated `fault-level` skill ships.

### Motor control center internal compartments
Stage 1 emits the MCC as a single entry with summarized motor circuits. Detailed compartment-by-compartment I/O (terminal labels, control wiring) is its own skill scope.

### Arc-flash hazard analysis
NFPA 70E / IEEE 1584 arc-flash incident energy calculation is its own specialty. Not included.

### Generator + UPS distribution coordination
Standby generator transfer schemes (NEC 250.30 / BS 7671 Chapter 55) and UPS-fed circuits get special handling not in stage 1.

### Voltage drop verification
Voltage drop per circuit is a separate validation (cable-sizing skill scope). This skill does not run the V-drop check.

## What may produce false positives in evals

- **D6 (Cable + OCPD coordination):** if the engineer provides explicit cable temperature class and installation method, the verdict may differ from the default-corrected ampacity. Reviewer should accept engineer-provided derating.
- **INV-09 (Selectivity result completeness):** the skill cannot detect undeclared cascade pairs. If two circuits share an upstream OCPD that wasn't declared, the cascade entry is missing.

## Tool calls awaiting runtime

| Tool name | Purpose | Status |
|---|---|---|
| `calc.iec60909_cascade` | Compute prospective fault current at each cascade level | tool_call_pending (until fault-level skill) |
| `calc.diversity_factor` | Apply diversity factor from standards to mains sizing | tool_call_pending |

When WI3 runtime tools land + `fault-level` skill ships, selectivity_results entries with source = "tool_call_pending" will be re-emitted as `source: "iec_60909_calc"` with computed selective_to_fault_ka values.
