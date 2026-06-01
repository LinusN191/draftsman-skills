# Changelog

## [1.0.0] - 2026-06-01 — Initial production release (Wave 1 second deliverable)

### Added

**Phase A — Foundations (A.1–A.4)**
- **Skill scaffolding (A.1).** Production manifest with 8-entry standards stack (BS 7671
  Part 7 §701/§702/§703/§710/§715; HTM 06-01; BS EN 60601 series; BS EN 61557-8;
  BS EN 61558-2-6; BS 5266-1). `produces_intents` (special-locations-zoning v1.0.0);
  `consumes_intents` (lighting-layout v^1.5, trigger = Part 7 room_type set). 17 example
  paths registered. `_v1_limitations` explicitly declared (MRI / NEC / §722 /
  embedded-heating / INT full examples all deferred).
- **IR + intent schemas (A.2).** `schemas/special-locations-ir.schema.json` — full IR with
  zone_layout[], constraint_summary, bonding_requirements, non_compliance_flags[],
  rationale, provenance. `schemas/special-locations-zoning-intent.schema.json` — flat
  downstream payload (zones[], jurisdiction, enforcement_targets).
- **Inputs taxonomy (A.3).** `inputs.json` — 6 items: anchor_fixtures[] (required),
  room (required), water_jet_present (optional), medical_group_override (optional),
  it_system_present (optional), nhs_site (optional). Rules YAML: 5 files covering zone-
  geometry derivation, RCD requirements, SELV/IP constraints, bonding policy, medical IT.
- **Zone-derivation library (A.4).** `shared/special-locations/zone-derivation/` —
  parametric zone derivation from anchor geometry for each Part 7 section; no lookup tables.

**Phase B — Prompts (B.1–B.3)**
- **Generator prompt (B.1).** `prompts/generator.md` — multi-step zone derivation pipeline
  (anchor ingestion → zone polygon computation → constraint set assembly → bonding schedule →
  non-compliance pre-check → IR emit → intent emit).
- **Validator prompt (B.2).** `prompts/validator.md` — 10 INVs (INV-01 zone geometry
  completeness through INV-10 provenance completeness); 6 HIGH + 4 MEDIUM.
- **Reviewer prompt (B.3).** `prompts/reviewer.md` — 5 D-checks (room-type consistency;
  changing-room adjacency; medical group plausibility; ELV external hazard; bonding schedule
  completeness).

**Phase C — Examples and evals (C.1–C.3)**
- **Standalone examples (C.1).** 8 worked examples: uk-bathroom-standard-bath-and-shower,
  uk-bathroom-whirlpool-with-pump, uk-shower-room-wet-room-floor,
  uk-pool-hall-with-changing-room-adjacency, uk-sauna-with-3-zone-derivation,
  uk-medical-or-group-2-with-it-system, uk-medical-ward-group-1-bonding,
  uk-external-landscape-elv-lighting. Each carries input.json + output.json + reasoning.md.
- **Cascade examples (C.2).** 9 cascade examples across lighting-layout v1.6 / small-power
  v1.2 / db-layout v1.5 consumers. Includes KE §313 dual-citation example and violation
  demo examples (socket exclusion breach, missing isolation).
- **Evals (C.3).** ≥5 eval YAMLs: zone-geometry-completeness, rcd-blanket-enforcement,
  selv-zone-0-constraint, imd-8s-alarm-response, ipe-whirlpool-ipx5, socket-exclusion-3m,
  ke-jurisdiction-routing, bonding-schedule-integrity.

**Phase D — Cascade integration (D.1–D.3)**
- **lighting-layout v1.5 → v1.6 (D.1).** Manifest gains `consumes_intents` for
  `special-locations-zoning`; validator gains zone-aware luminaire IP check; 3 existing
  examples retrofitted.
- **small-power v1.1 → v1.2 (D.2).** Socket-outlet exclusion zone enforcement via consumed
  `special-locations-zoning` intent; isolation distance check for §702/§710.
- **db-layout v1.4 → v1.5 (D.3).** RCD allocation enforcement from zone constraints;
  §710 Group 2 medical IT distribution board recognition.

### Cascade integration summary
- Produces `special-locations-zoning` intent (v1.0.0) consumed by 3 downstream skills.
- Consumes `lighting-layout` intent (v^1.5) for upstream fixture positions.

### Honest disclosures
- INT jurisdiction worked examples deferred to v1.1 (citation routing supported in IR via
  `_clause_citation` fields; IEC 60364-7-XXX routing declared in manifest).
- MRI rooms, US NEC (Article 680/517), §722 EV charging, and embedded heating deferred.
  Full disclosure in README `_v1_limitations`.
- Zone geometry derivation is 2D plan-view; 3D envelope (ceiling Zone 1 above bath) uses
  ceiling_height_mm approximation. Engineer verification required before construction issue.

### Gates
- validate-examples.py: baseline +17 (8 standalone + 9 cascade examples added across sprint).
- functional_audit.py: 1 finding unchanged (disclosed motor-superposition oracle FP on
  fault-level/us-industrial-with-motors/MCC-1).
