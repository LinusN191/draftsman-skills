# `arc-flash` — Per-Node Arc-Flash Analysis (IEEE 1584 + NFPA 70E)

**Status:** `beta`
**Version:** `1.0.0`
**Drawing type:** `arc_flash_study`
**Phase:** B (Phase A standards layers shipped previous sprint)
**Reference:** `electrical/fault-level/` (production reference) + `electrical/cable-sizing/` (sibling beta — proven artefact pattern)

## What this skill produces

A project-scoped arc-flash IR with per-node:

- Incident energy (cal/cm²) at working distance
- Arc-flash boundary distance (where E = 1.2 cal/cm²)
- Limited + Restricted shock-approach boundaries (NFPA 70E §130.4 — bundled because every label needs them)
- PPE category 1–4 (NFPA 70E Table 130.7(C)(15)(c)) + engineer override
- `label_recommended` boolean per NFPA 70E §130.5(H)
- `method_applied` tag + `method_fallback_trail[]` showing every method tried

**Plus an `arc-flash` intent** (slim downstream subset) emitted alongside — consumed by future `electrical/arc-flash-labelling` skill (stub committed 2026-05-17 at `electrical/arc-flash-labelling/`).

## Five methods + fallback chain

| Method | Source | Bias | When used |
|---|---|---|---|
| `ieee_1584_2018` | IEEE 1584:2018 §§6-10 + Annex C | Most realistic | Preferred for AC; requires transcribed coefficients |
| `ieee_1584_2002` | IEEE 1584:2002 (Doughty/Neal) | Slightly conservative vs 2018 | Legacy compatibility + fallback |
| `lee_1982` | Lee 1982 IEEE-IAS paper | **Significantly conservative (2-5× higher IE)** | Always-available fallback |
| `nfpa_70e_table` | NFPA 70E Table 130.7(C)(15)(a)/(b) | **Most conservative** | Equipment-class lookup, no IE computed |
| `doan_dc` | NFPA 70E Annex D §D.1+D.2 | Realistic for DC | DC nodes only (current_type=dc) |

For each AC node: 2018 → 2002 → Lee 1982 → NFPA 70E table → pending. Every node records the full trail.

## Jurisdictions supported

| Jurisdiction | Regulatory framing | Label policy |
|---|---|---|
| GB | HSG48 + IET CoP (voluntary best practice) | Recommended but not statutory |
| EU / INT | IEEE 1584 (de facto international standard) | Best practice |
| US | NFPA 70E §130.5(H) (mandatory under OSHA) | Required for switchgear / panelboards / MCCs ≥240V |

## Voltage range

208V – 15 kV AC + DC up to 1000V.

## Cross-drawing intent contract

| Direction | Intent | Purpose |
|---|---|---|
| Produces | `arc-flash` | Per-node IE/AFB/PPE/shock-approach → consumed by future arc-flash-labelling skill |
| Consumes | `fault-level` | Per-node Ibf + ipk + X/R for arc-current calc |
| Consumes | `db-layout-rollup` | Equipment type + OCPD type + voltage for inference |

## File structure

```
electrical/arc-flash/
├── README.md
├── CHANGELOG.md
├── skill.manifest.json
├── inputs.json
├── prompts/        (generator 14-step / validator 10 INV / reviewer 8 D)
├── schemas/        (IR + intent)
├── rules/          (5 YAMLs)
├── constraints/    (4 YAMLs)
├── validation/     (4 YAMLs, 12 checks)
├── ontology/       (method-types + current-types)
├── docs/           (engineering-philosophy + known-limitations)
├── evals/          (runner-config + 9 evals)
└── examples/       (UK LV / INT MV / US PV+DCFC)
```

Plus the new calc contract at `shared/calculations/electrical/arc-flash-incident-energy.json` (shipped this sprint).

## Eval coverage matrix

| Eval ID | Category | Tests |
|---|---|---|
| eval-01-uk-lv-switchboard-happy-path | happy_path | 400V UK commercial cascade, baseline |
| eval-02-mv-cascade-with-drawout | edge_case | 11kV + 400V cascade, HCB + VCB |
| eval-03-coefficient-fallback-trap | validation_trap | 2018 coefficients null → Lee 1982 fallback |
| eval-04-missing-fault-data | missing_input | No Ifault → method_applied: pending |
| eval-05-jurisdiction-us-with-restricted | jurisdiction_switch | IE > 40 → RESTRICTED |
| eval-06-rationale-block | rationale_block | 8 sections + chat_summary |
| eval-07-dc-pv-string | skill_specific | DC node with doan_dc method |
| eval-08-conservative-t-clear-default | skill_specific | No ocpd_type → 2.0s default + warning |
| eval-09-shock-approach-out-of-range | skill_specific | 47 kV → SHOCK_APPROACH_BEYOND_TABLE_RANGE |

All 6 WI5 categories + 3 skill-specific.

## Phase A dependencies (already shipped)

- `shared/standards/electrical/IEEE1584/` (28 files, production)
- `shared/standards/electrical/NFPA70E/` (25 files, production)
- `shared/schemas/core/standards-{formula,table,section}.schema.json` (3 schemas)
- `shared/validation/standards/*.py` (3 validation scripts)

## Tool calls awaiting runtime

| Tool name | Purpose |
|---|---|
| `calc.arc_flash_incident_energy` | IEEE 1584 / Lee / NFPA 70E / Doan fallback chain. Contract at `shared/calculations/electrical/arc-flash-incident-energy.json`. Status: tool_call_pending until runtime ships. |

## Pending-verification coefficients

17 IEEE 1584 coefficient files in the Phase A standards layer carry null values (pending transcription from a paid copy). The skill handles this gracefully via the method fallback chain — when 2018 coefficients are null, auto-demotes to Lee 1982 or NFPA 70E table method.

When the coefficients are eventually transcribed (a future micro-sprint), the skill auto-promotes from `lee_1982` to `ieee_1584_2018` with no code changes.

## Known limitations

See `docs/known-limitations.md`. v1.0.0 does NOT cover:
- DC > 1000V (utility-scale PV 1500V systems) → v1.1
- BESS-specific safety analysis → separate `bess-safety` skill
- Arc-flash label content generation → separate `electrical/arc-flash-labelling` skill (stubbed)
- Time-graded protection coordination → separate `protection-coordination` skill (refines t_clear)
- MV utility-side fault contribution beyond fault-level

## Versioning

- Minor bumps (1.x.0): new jurisdictions, new evals, DC > 1000V support
- Major bump (2.0.0): breaking IR schema change OR IEEE 1584:2028 adoption
- Patch bumps (1.0.x): rules/constraints/validation fixes

## License

See repository root `LICENSE`.
