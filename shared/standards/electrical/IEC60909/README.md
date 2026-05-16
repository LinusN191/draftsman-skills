# IEC 60909 — Short-Circuit Currents in Three-Phase AC Systems

**Status:** v1.0.0 beta
**Released:** 2026-05-16
**Primary consumer:** `electrical/fault-level` skill v1.0.0

## Standard

IEC 60909-0:2016 — Calculation of currents. The international reference for prospective short-circuit current calculation. Used by:
- Switchgear breaking-capacity (IEC 60947, IEC 60898) verification
- Cable adiabatic protection (IEC 60364-4-43, BS 7671 Reg 434)
- Selectivity coordination (IEC 60364-5-53, BS 7671 Reg 536)

## What this layer covers

- Fundamental method (§3): Ik" symmetrical initial short-circuit current, voltage factor c
- Peak current (§4.3): ipk via κ factor per IEC 60865-1
- Source impedance modelling: utility / transformer / generator / UPS / motor (§4.2 - §4.5)
- Near-generator decrement (§3.5)
- Far-from-generator constant-source (§3.4)
- Multi-source superposition (§3.6)

## What this layer does NOT cover

- IEEE 1584 arc-flash (separate `arc-flash` skill scope)
- Time-graded protection coordination (separate `protection-coordination` skill scope)
- DC fault analysis (PV strings, battery storage — separate skill)
- HV transformer differential protection (out of building-services scope)

## Loaded by

- `electrical/fault-level/skill.manifest.json` (primary)
- `electrical/db-layout/skill.manifest.json` (cross-reference for cascade context)
- Other skills consuming `fault-level` intent: earthing, cable-sizing, generator-sizing

## Files

| File | Purpose |
|---|---|
| `part0-fundamentals.json` | Core definitions: Ik", c-factor, near/far-from-generator classification |
| `part0-method.md` | Step-by-step IEC 60909-0 calculation method |
| `peak-factor-kappa.json` | κ peak factor formula + table by X/R ratio |
| `voltage-factor-c.json` | c=1.05 (Ik"max) and c=0.95 (Ik"min) selection rules |
| `source-impedances.json` | Unified source-impedance reference (utility/TX/gen/UPS/motor) |
| `transformer-zpu-table.json` | Typical Zpu values by transformer kVA |
| `generator-subtransient-tables.json` | X"d, X'd, Xd by machine type and rating |
| `motor-contribution-rules.json` | IEC 60909-0 §4.5 induction motor short-circuit contribution |
| `compliance-checklist.md` | Verification checklist for fault-level study deliverables |
| `terminology.md` | Glossary aligning IEC 60909 terms with BS 7671 / NEC equivalents |
| `amendments-summary.md` | Notes on IEC 60909-0:2016 amendments + national derivations |
