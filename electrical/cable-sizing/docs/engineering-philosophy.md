# Engineering Philosophy — cable-sizing v1.0

This document captures the engineering convictions that shape the cable-sizing skill. These are the *why* behind the algorithm and the IR shape.

## Walk-the-ladder from below, not iteratively

For each cascade node, the skill starts at the smallest csa where `Iz_tabulated × correction_factors ≥ In` and steps up the standard ladder until all 5 checks pass simultaneously: ampacity, cumulative Vd, motor-starting Vd (if motor), CPC adiabatic, and harmonic derating (if applicable).

This is intentional. Iterative refinement (binary search, mathematical optimisation) would obscure the engineering decision: a reviewer wants to see *which* check forced the size up. The walk_up_trail records every rejected csa with the failing check name — auditable in 30 seconds, not "trust the optimiser".

## binding_constraint is named per node

Every cascade node carries exactly one `binding_constraint` token from a 6-token vocabulary:

- `iz_vs_in` — ampacity drove the size (or sized at start csa with no walk-up)
- `vd_cumulative` — cumulative Vd at the leaf forced the upstream cable up
- `motor_starting_vd` — motor inrush at LRA × Ib exceeded 10% at the smaller csa
- `cpc_adiabatic` — CPC adiabatic failed at smaller phase csa, forcing phase upsize to permit larger CPC
- `parallel_required` — single-cable ladder exhausted; N parallels engaged
- `harmonic_derating` — Ch derating forced the upsize on a 3-phase 4-wire IT load

This single name encodes the *primary* engineering decision. Tender reviewers can answer "why is this cable that size?" without reading 8 sections of rationale.

## Cumulative Vd is the project-level reality

Per-segment Vd is misleading: a 4% feeder + 4% branch = 8% at the load, which violates BS 7671:2018+A2:2022 App 12. The cascade tree supports cumulative Vd naturally — each node's `vd_cumulative_pct = vd_segment_pct + parent.vd_cumulative_pct`.

This is why cable-sizing IS a project-scoped cascade skill, not a per-circuit utility. A single circuit can pass its 5% segment limit and still fail the project-level 5% at the leaf.

## CPC adiabatic can drive phase upsize

The CPC adiabatic equation `S² ≥ I²t / k²` (BS 7671 Reg 543.1.3 / IEC 60364-5-54 §543) is computed AFTER the phase csa is provisionally selected on Iz + Vd. If the resulting CPC requires upsize beyond what the smaller phase csa permits in the reduced-CPC table, the algorithm walks the phase up one ladder step and re-checks. When this happens, `binding_constraint = "cpc_adiabatic"` — phase was driven up by CPC, not by ampacity.

## Parallel cables are a last resort, with symmetry guard

When the single-cable ladder exhausts at the largest available csa (630 mm² / 1000 kcmil) and Iz still falls short of In, the skill engages parallel cables with strict symmetry: all parallels MUST match on length + csa + material + installation method (IEC 60364-5-52 §523.6 / NEC 310.10(H)). This ensures balanced current sharing.

Minimum csa per parallel: 50 mm² (IEC) or 1/0 AWG (NEC). Maximum count: 6 — above that, the engineer should redesign with bus duct rather than escalate parallels.

## Harmonic derating is an explicit trigger

When `harmonic_content_pct > 15` AND `load.phases == "three_phase_4wire"`, the skill applies a Ch derating factor (BS 7671 App 4 §5.5 / IEC 60364-5-52 Annex E §E.5 / NEC 310.15(E)) AND upsizes the neutral conductor to match phase csa when h3 > 33% (IEC) or > 50% (NEC).

This is opt-in by engineer declaration: the algorithm never invents h3 content. If the engineer fails to declare it on a UPS rectifier input or LED lighting feeder, the deficiency is on the engineer's hand-over, not the skill.

## WI3 tool-call deferral throughout

Until the runtime ships `calc.cable_ampacity` / `calc.voltage_drop` / `calc.cpc_adiabatic`, every cascade node carries `tool_call_pending: true` AND the IR carries 3 `TOOL-CALL-PENDING:calc.*` flags. The skill emits best-effort engineer estimates as placeholder values for Iz / Vd / CPC results — these are documented in non_compliance_flags as info-severity for transparency. Once the calc tools ship, the runtime re-resolves and clears the flags. Same pattern as fault-level v1.1 + earthing v1.1+ + small-power v1.0.
