# Changelog — electrical/arc-flash

All notable changes to the arc-flash skill. Follows [Keep a Changelog](https://keepachangelog.com).

## [1.0.0-beta] — 2026-05-17

### Added — v1.0.0 beta (Phase B)
- 14-step generator chain (`prompts/generator.md`) — IEEE 1584:2018 + IEEE 1584:2002 + Lee 1982 + NFPA 70E table method + Doan/Stokes & Oppenlander for DC
- Project-scoped cascade IR (`schemas/arc-flash-ir.schema.json`) with method-fallback-trail per node
- Slim downstream `arc-flash` intent (`schemas/arc-flash-intent.schema.json`) — consumed by future `electrical/arc-flash-labelling` skill
- 5 rules: method-fallback-chain, electrode-config-inference, t-clear-defaults, ppe-category-mapping, label-required-equipment
- 4 constraints: incident-energy-finite, boundary-distance-physical, ppe-category-monotonic, method-fallback-consistency
- 4 validation YAMLs (12 deterministic checks)
- 2 ontology files: method-types (5 methods + pending), current-types (ac/dc with applicable methods)
- 9 evals (6 WI5 categories + 3 skill-specific)
- 3 worked examples: UK LV switchgear / INT MV substation / US PV+DCFC

### Phase A dependencies (already shipped)
- `shared/standards/electrical/IEEE1584/` (28 files, production)
- `shared/standards/electrical/NFPA70E/` (25 files, production)
- `shared/schemas/core/standards-{formula,table,section}.schema.json`
- `shared/validation/standards/*.py` (3 validation scripts)

### Tool calls awaiting runtime (WI3 deferral)
- `calc.arc_flash_incident_energy` (contract: `shared/calculations/electrical/arc-flash-incident-energy.json` — shipped this sprint)

### Consumes intents
- `fault-level` (per-node Ibf + ipk + X/R)
- `db-layout-rollup` (per-board equipment_type + ocpd_type + voltage)
- Engineer-declared fallback when intents absent

### Produces intent
- `arc-flash` — per-node IE + AFB + PPE + shock-approach + label_recommended; consumed by future `electrical/arc-flash-labelling` skill (stub committed 2026-05-17 at `electrical/arc-flash-labelling/`)

### Known limitations
- DC > 1000V not supported (utility PV 1500V systems deferred to v1.1)
- 17 IEEE 1584 coefficient files in Phase A standards layer are pending-verification; skill falls back gracefully to Lee 1982 or NFPA 70E table method until coefficients are transcribed
- Arc-flash label content generation is a separate future skill (arc-flash-labelling)
- Time-graded protection coordination is a separate future skill (refines t_clear precision)
