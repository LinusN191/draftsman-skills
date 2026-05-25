# Known Limitations — Arc-Flash v1.0.0

What v1.0.0 does NOT cover. These are deliberate scope boundaries, not bugs.

## Out of scope (v1.0.0)

| Topic | Why not | Where it goes |
|---|---|---|
| DC > 1000V | NFPA 70E Annex D scope stops at 1000V; utility-scale PV strings at 1500V need different methods | v1.1 OR `dc-high-voltage-arc-flash` future skill |
| BESS-specific safety analysis (Li-ion thermal runaway, gas evolution) | Different physics + different standards (UL 9540A, IEC 62619, NFPA 855) | Future `bess-safety` skill |
| Arc-flash label content generation (printable PDFs/SVGs) | Document production is a separate concern from engineering analysis | Future `electrical/arc-flash-labelling` skill (stubbed at commit `711ebd5`) |
| Time-graded protection coordination | Refines t_clear precision via OCPD time-current curve interaction; complex enough for its own skill | Future `protection-coordination` skill |
| MV utility-side fault contribution beyond what fault-level handles | Multi-source fault contributions need fault-level v1.1 first | After fault-level v1.1 |
| Lee 1982 sanity-check uppper bound enforcement (auto-cap IE ≤ Lee result) | Useful safety net but complicates the fallback chain; deferred | v1.1 if engineers report unrealistic IEEE 1584:2018 results |
| Arc-resistant equipment derate (some equipment vendors publish lower IE for their arc-resistant gear) | Vendor-specific data; not standardised | Engineer-declared override per node |

## Inputs the skill cannot derive (require engineer)

These cannot come from any upstream intent and must be declared per cascade node:

- `t_clear_s` — engineer-declared with OCPD-type default fallback (rules/t-clear-defaults.yaml)
- `working_distance_mm` — defaults from Phase A working-distance-defaults.json (455mm LV, 914mm MV); engineer override per node
- `current_type` (`ac | dc`) — auto-inferred from equipment_type pattern matching; engineer override
- `electrode_config` — auto-inferred from equipment_type; engineer override per node
- `enclosure_volume_mm3` — required for §10.5 adjustment when non-standard; defaults to typical box dimensions otherwise

If any required input is missing AND no upstream intent provides it, the generator sets `method_applied: pending` for that node and emits `ARC_FLASH_PENDING` flag.

## Phase A pending-verification coefficients

Files in `shared/standards/electrical/IEEE1584/` are pending source-vetted transcription:
- 3 method-2018-tables-1-3-*V-coefficients files (10-coef Iarc + 13-coef IE polynomial-in-V per Tables 1+3)
- 3 method-2002-annex-f-*V-coefficients files (7-coef log-linear per Annex F; retained alongside for relabel correctness — see Sprint A.3 dual-track rationale in `shared/standards/electrical/IEEE1584/meta.json`)
- 5 electrode-config-*-coefficients files
- 3 adjustment-factor-*.json files
- 1 method-2002-doughty-neal-formula.json
- (Plus 5 NFPA 70E lookup tables also pending)

The skill handles this gracefully via the method fallback chain: when 2018 coefficients are null, falls through to Lee 1982 (always available) or NFPA 70E table method. When the coefficients are eventually transcribed in a future micro-sprint, the skill auto-promotes (no code changes — fallback chain re-runs at runtime).

## Forward-compatibility caveats

- The emitted `arc-flash` intent's shock-approach fields use `oneOf [number, string]` because Table 130.4(C)(a) row 1 contains `"avoid contact"` for <50V. Downstream consumers (labelling skill) must handle both.
- PPE category 0 (IE < 1.2 cal/cm²) is recorded as Cat 1 minimum per industry convention — even though NFPA 70E doesn't strictly require AR clothing below the threshold, any energized work in practice uses Cat 1 PPE.
- DC nodes always have `electrode_config: null`. The intent schema enforces this; the labelling skill should not attempt to render electrode config for DC nodes.

## Pre-existing standards-layer tech debt

The Phase A standards layers (IEEE1584 + NFPA70E) carry `clause_ref` fields per the new convention. Pre-existing electrical standards layers (BS7671, IEC60364, IEC60909, etc.) lack `clause_ref` — known cross-cutting tech debt scheduled for a future micro-sprint. The `standards-clause-check.py` validation script is scoped to IEEE1584 + NFPA70E to avoid noise from pre-existing layers.
