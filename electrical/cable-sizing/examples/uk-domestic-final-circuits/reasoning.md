# UK Domestic Final Circuits — Worked Example

## Scenario

230V single-phase domestic consumer unit feeding 4 standard final circuits:
- 2 lighting circuits (6A MCB)
- 1 kitchen ring final (32A MCB)
- 1 cooker radial (32A MCB)

All sized in PVC singles, installation method B1 (in conduit on a wall).

## Why all 4 are Iz-binding (no upsize)

Each circuit's `In` happens to match the smallest standard csa that gives sufficient Iz:
- 6A MCB → 1.5 mm² gives Iz ~15.5A (huge headroom, no Vd issue at 22m/18m)
- 32A MCB ring → 4 mm² gives Iz ~32A (just sufficient — well under 5% Vd at 30m on a ring)
- 32A MCB cooker → 6 mm² (the bigger csa is conservative for resistive heating + short run)

None of the 4 circuits trigger:
- Vd binding (lighting 3% / power 5% comfortably met)
- CPC adiabatic upsize (Ifault not declared; placeholder pass)
- Motor starting (no motors)
- Parallel cables (single-cable suffices)
- Harmonic derating (no IT loads, no VFDs)

## Tool-call deferral

Until the DraftsMan runtime ships `calc.cable_ampacity`, `calc.voltage_drop`, and
`calc.cpc_adiabatic`, every node carries `tool_call_pending: true`. The numeric values
in `checks` are senior-engineer estimates from BS 7671 App 4 tables — they will be
re-computed by the calc tools at runtime.

## What this example demonstrates

- Basic happy-path walk-up (start csa accepted on first check)
- Jurisdictional defaults (GB → BS 7671 App 12 limits)
- Per-load-type Vd limit selection (lighting vs power)
- Rationale block conformance (8 sections including "Special Checks: none triggered")
- Forward-compatible intent emission (cable_od_mm + weight_kg_per_m for downstream
  containment-fill consumers, even when those consumers aren't built yet)
