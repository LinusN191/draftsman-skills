# Known Limitations — cable-sizing v1.0

This document inventories what v1.0 does NOT cover, with the rationale for each deferral and the future-skill or roadmap item that will address it.

## DC scope deferred

v1.0 covers AC cable sizing only. DC sizing for PV strings, EV DCFC charge points, and battery interconnects requires different equations (single-conductor Vd, different fault analysis, no power-factor) and different standards (IEC 62548 for PV, NEC 690 for US PV, IEC 61851 for EV).

**Roadmap:** future `dc-cable-sizing` sibling skill. v2.0 of cable-sizing reserved for the DC extension OR a breaking IR schema change.

## IEC 60287 advanced thermal modelling deferred

v1.0 uses standard ampacity tables (BS 7671 App 4 / IEC 60364-5-52 Annex B / NEC Chapter 9) which encapsulate the thermal model. Very large buried cable groups (>3 circuits in same trench, soil thermal resistivity ≠ 1.0 K·m/W, non-standard depth) need IEC 60287 first-principles calculation.

**Roadmap:** v1.x or a sibling skill once a real engineering need surfaces.

## Arc-flash incident-energy boundary marking deferred

Arc-flash is conceptually adjacent (both consume fault-level intent) but distinct in math (IEEE 1584:2018 / NFPA 70E:2024). The `arc-flash` skill is already shipped (v1.0 beta) as a separate skill consuming the same fault-level intent.

**Status:** see `electrical/arc-flash/` and `electrical/arc-flash-labelling/`.

## Communications + data cables (Cat6, fibre) excluded

Cat5e/Cat6/Cat6a/Cat7 + multi-mode fibre + OPGW are a different standards family (BS EN 50173 / TIA-568 / ISO/IEC 11801) with different metrics (insertion loss, return loss, NEXT, polarisation mode dispersion) — not Iz/Vd/adiabatic.

**Roadmap:** future `data-telecom-cabling` skill. Not in current pipeline.

## Time-graded protection curve coordination deferred

OCPD selectivity (time-current curve coordination, Type 1/2/3 selectivity per IEC 60947-2) is handled upstream by `db-layout` which emits `selectivity_pending` flags in its rollup intent. cable-sizing consumes the resulting `t_clear` per node from db-layout-rollup; it does NOT run the curve-coordination math itself.

**Roadmap:** future `protection-coordination` skill or extension of `db-layout`.

## v1.0 single-stage only

The skill produces one IR per project in a single pass. v1.1+ may introduce iterative passes (e.g., re-resolve after engineer overrides one circuit, propagate cumulative-Vd cascade effects upstream). For v1.0 the engineer reruns the skill end-to-end.
