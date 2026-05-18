# SLD v1.3.0 — Known Limitations

## Out of scope (deferred to future versions)

| Limitation | Future version |
|---|---|
| Drawing positions (x/y coordinates per board) — Stage 1 is logical topology only | v1.5.0 (Stage 2) |
| Consuming earthing intent (system_type confirmation, supply_bond_type, SPD policy input) | v1.4.0 |
| Consuming fault-level intent (deterministic PSCC + cascade selectivity refinement) | v1.4.0 |
| calc.sld_system_metrics tool (deterministic Imax + peak_pfc + SPD verdict refinement) | v2.0.0 |
| Generator/UPS/ATS topology (currently flagged in compliance_summary.assumptions, not modelled in IR) | v1.6.0 |
| Multi-supply scenarios (two intakes + ATS switching between them) | v1.6.0+ |
| Renderer output (SVG/DXF/LISP) | runtime concern |

## Current limitations (by design)

- **System metrics are LLM-estimated** (WI3 tool deferral flag set). Imax_total + peak_pfc accuracy is ±15-25% vs deterministic calculation.
- **Cascade selectivity verdict is engineering judgement** based on manufacturer typical curves + IEC 60898 conventions. For tight-tolerance designs, engineer should consult manufacturer selectivity tables directly.
- **SPD assessment is rule-based** (not a calc). Location-type + supply-type + life-safety-presence → verdict via jurisdiction-specific lookup. Doesn't model lightning probability or service-entry distances.
- **4 worked examples cover 4 jurisdictions** (UK + KE + INT + US). Other jurisdictions (NF C 15-100 / DIN VDE 0100 / etc.) deferred to v1.4+.

## Verification status

| Component | Status | Note |
|---|---|---|
| IR schema | production | Draft-07 JSON Schema; validates all 4 example outputs |
| Intent schema | production | Draft-07 JSON Schema; validates all 4 example intent-outs |
| Generator prompt | production | 12 steps; mirrors arc-flash / cable-sizing / fault-level / earthing pattern |
| Validator prompt | production | 10 INV checks |
| Reviewer prompt | production | 6 D-check pattern |
| Rules + constraints + validation YAMLs | production | 10 YAML files, 17+ deterministic checks total |
| 4 worked examples | production | UK + KE + INT + US, each consuming N+1 db-layout intents |
| 7 evals | production | 5 WI5 categories + 2 skill-specific |
| `calc.sld_system_metrics` runtime tool | not_shipped | Contract deferred; LLM-inline computation in v1.3 |
