# Reasoning — KE Nairobi Workshop Motor Starter (DOL)

## Why DOL (and not star-delta or soft-start) for 11 kW

DOL (Direct-On-Line) is the lowest-cost, lowest-component-count, lowest-failure-mode starter for a 3-phase squirrel-cage motor. The classical objections to DOL are mechanical (inrush torque shocking the driven load) and electrical (inrush current tripping upstream protection or dipping the supply). For an 11 kW workshop grinder, neither objection lands hard.

Grinders accelerate against negligible load — the abrasive wheel has very low inertia and there is no driven shaft to snap. The mechanical shock argument that motivates star-delta on large pumps and conveyors does not apply. Electrically, the 147 A inrush (~7×FLA, typical for a TEFC induction motor) lasts only ~4 s before the rotor reaches synchronous slip and current settles at 21 A FLA. With a workshop sub-DB on a robust 32 A Type D upstream MCB, the inrush sits at 4.6×In — comfortably below the Type D 10-20×In magnetic threshold per BS EN 60898-1:2019. Star-delta would add 3 contactors, a transition timer, and ~3-4× the wiring complexity, all for no measurable benefit on this grinder. The KE workshop environment also favours simplicity for field-maintenance reasons: a DOL panel can be reset and verified by an electrician with a multimeter; a star-delta panel needs an electrical engineer to trace through the transition logic.

## Overload Class 10 sizing

The overload setting is the motor FLA value (21 A), not the contactor rating (32 A) and not some derated value. The motor full-load current is the steady-state current you want the overload to permit indefinitely; the inrush is a 4 s transient handled by the overload's *class* (its time-current characteristic), not its setpoint. Class 10 tolerates locked-rotor current (7.2×Ie ≈ 151 A) for ~10 s, which comfortably accommodates the 4 s actual start. Class 20 would over-protect (slow trip on a real fault), Class 30 would be wrong (designed for high-inertia loads like centrifuges where start times exceed 10 s).

## Type D upstream selection

The engineer-declared 32 A Type D upstream is the right call for this circuit. Type B (3-5×In magnetic) would routinely nuisance-trip at 4.6×In inrush. Type C (5-10×In) sits right at the lower band edge — works most days, nuisance-trips on a hot restart or on phase imbalance. Type D (10-20×In) gives full headroom. BS EN 60898-1:2019 explicitly defines Type D as the motor / welding / DC-loaded curve for exactly this reason. KS 1700:2018 § 552 (Annex E §VIII routing to BS 7671:2018+A2:2022 § 552) covers motor switching and references the BS EN 60898 curve discipline verbatim.

## KE jurisdiction routing

KS 1700:2018 is the Kenyan adoption of the IET Wiring Regulations. Annex E §VIII establishes the explicit mechanism by which BS 7671:2018+A2:2022 clauses are adopted verbatim into the Kenyan standard. The schematic accordingly uses the form `"KS 1700:2018 § X.Y.Z (Annex E §VIII: adopts BS 7671:2018+A2:2022 § X.Y.Z verbatim)"` per Sprint 3-W2b citation discipline. Jurisdiction-agnostic standards (BS EN 60617 for symbols, BS EN 60947-4-1 for contactors, BS EN 60898-1:2019 for MCBs, BS EN 60204-1 for machinery safety) are cited directly without routing — they apply equally in any jurisdiction that has not produced a competing national standard. This is leaf-mode execution: no db-layout-rollup intent, no fault-level intent, no earthing intent available, so the upstream 32 A Type D MCB, prospective fault current, and TN-S earthing system are all engineer-declared in inputs.json and re-stated in compliance_summary.assumptions[].
