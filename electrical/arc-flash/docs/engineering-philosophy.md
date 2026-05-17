# Engineering Philosophy — Arc-Flash

This skill encodes a senior-engineer mental model for arc-flash analysis rather than just running calc formulas. The model:

## 1. Method fallback, not method blindness

When IEEE 1584:2018 empirical coefficients aren't available for a (voltage_class, electrode_config) pair, the skill doesn't return null — it falls through a chain: 2018 → 2002 → Lee 1982 → NFPA 70E table method → pending. Every node records the full trail so an engineer reading the IR can see exactly which methods were tried and why.

This matches what NFPA 70E §130.5 actually requires: "if you can't do an incident-energy analysis, use the table method." Falling back gracefully gives the engineer useful output (a conservative upper bound) instead of a blank screen.

## 2. Conservatism is acceptable; silence isn't

Lee 1982 typically produces 2-5× higher IE than IEEE 1584:2018 (Lee treats the arc as a black-body radiator with spherical dispersion — real arcs are far less efficient). NFPA 70E table method is even more conservative. The skill emits **info-severity flags** when these fallbacks fire (`LEE_1982_FALLBACK_USED`, `NFPA70E_TABLE_METHOD_USED`) so the engineer sees that the answer is conservative and knows the action to un-block it: transcribe IEEE 1584:2018 coefficients.

## 3. Shock-approach distances belong on every arc-flash label

Engineers sometimes ship arc-flash labels with only the thermal boundary. NFPA 70E §130.5(H) actually requires both: thermal (arc-flash) + shock (limited + restricted approach). The skill bundles them — every node carries both, sourced from Table 130.4(C)(a) (AC) or (b) (DC). The future labelling skill doesn't have to compute shock-approach separately.

## 4. DC is different physics; treat it differently

DC arcs sustain at lower voltages, have different arc-voltage characteristics, and aren't covered by IEEE 1584 (which is AC-only). The skill routes DC nodes through Doan + Stokes & Oppenlander (NFPA 70E Annex D §D.1 + §D.2). DC nodes get `electrode_config: null` (the IEEE 1584 electrode-config concept doesn't apply), and shock-approach comes from Table 130.4(C)(b), not (a).

A unified cascade tree with `current_type: ac | dc` per node — instead of two separate trees — keeps the parent-child relationships clean (a PV string is a child of its inverter; the inverter is AC, the string is DC, both live in the same cascade).

## 5. t_clear is the dominant uncertainty

Incident energy is approximately linear in arcing time. A 0.1s vs 0.3s clearing time is a 3× IE difference. The skill's t_clear handling reflects this: engineer-declared (most authoritative) > OCPD-type default (reasonable) > conservative 2.0s (worst case). When the 2.0s default fires, an explicit warning flag tells the engineer to refine via protection coordination.

## 6. Defer math to deterministic tools

The empirical IE formula, the log-log interpolation between voltage classes, the adjustment factors for non-standard gap/distance/enclosure — all LLM-unreliable. We push them to `calc.arc_flash_incident_energy` per the WI3 pattern. Until the DraftsMan runtime ships, every node carries `tool_call_pending: true` + senior-engineer estimates as placeholders.

## 7. Engineer judgement stays at the prompt layer

What lives in the prompt: method fallback policy, electrode-config inference, t_clear defaults, label-required rules, PPE override policy. What lives in calc tools: the actual formulas + table lookups. Split deliberately — same separation as fault-level / cable-sizing.

## 8. Forward-compatible intent contract for the labelling skill

The `arc-flash` intent is designed as a superset of what the future `electrical/arc-flash-labelling` skill will consume. When that skill ships, it conforms to this contract — not the other way round. We've stubbed `electrical/arc-flash-labelling/` (commit `711ebd5`) so the roadmap shows the dependency.

## 9. Hard rules over soft guidance

Things the generator MUST never do (invent IEEE 1584 coefficients, set method_applied outside vocabulary, emit negative IE/AFB, skip the method_fallback_trail). These live as `hard_rules:` in the generator prompt, not as suggestions. The validator enforces them mechanically.
