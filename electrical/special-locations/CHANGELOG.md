# Changelog

## [1.0.1] - 2026-06-03 — Wave 2 producer-side cascade fixtures for small-power D4

_Patch: 2 additional producer-side cascade fixtures added to `examples/` to close
consumer-side integrity loops for small-power v2.0.0 (D4 depth sprint). No schema changes,
no prompt changes, no IR changes. All existing examples and evals unaffected._

### Added (examples)
- **`cascade-small-power-uk-ev-charge-domestic/`** (4 files: input.json, output.json,
  reasoning.md, intent-out.json): Producer source for the small-power
  `uk-ev-charge-domestic` example. Derives §702/§722 zone intersection for a domestic
  garage containing an EV charging point; confirms socket-exclusion zone boundaries and
  the absence of any §702 prohibition on EV dedicated circuits. `_cascaded_from` field
  set to `"electrical/special-locations/examples/cascade-small-power-uk-ev-charge-domestic"`.
  Closes small-power C.3 consumer integrity loop.
- **`cascade-small-power-uk-sauna-heater-exemption/`** (4 files: input.json, output.json,
  reasoning.md, intent-out.json): Producer source for the small-power
  `uk-sauna-with-heater-exemption` example. Derives §703 three-zone layout; annotates
  heater-exemption trigger from `appliance_thermal_protection: true` per
  BS EN 60335-2-53 §22.106; confirms socket-outlet exclusion outside Zone 3. Closes
  small-power C.4 consumer integrity loop.

### Unchanged
- All 8 standalone examples from v1.0.0 unchanged.
- All 9 v1.0.0 cascade examples unchanged (5 pre-existing special-locations cascade
  examples + the 4 consumer-skill cascade fixtures shipped with Wave 1).
- All 8 evals unchanged; gates held at +17 (the 2 new examples are producer-side cascade
  fixtures, not standalone examples that drive the gate counter independently).
- No schema changes; no prompt changes; no manifest breaking changes.
  `skill.manifest.json` minor internal annotation added noting 2 additional example paths.

### Relation to small-power v2.0.0
Both fixtures are required for the small-power v2.0.0 D4 sprint end-to-end cascade
contract validation. The special-locations v1.0.1 patch was dispatched within the D4
sprint as sub-task D.1 to ensure the cascade contract was closed before the
small-power CHANGELOGs were written. See `[[sprint-D4-small-power-shipped]]` memory for
the full sprint record.

## [1.0.0] - 2026-06-01 — Initial production release (Wave 1 second deliverable)

### Added
- **Skill scaffolding.** Production manifest (corrected shape — `skill` + `chat_type` +
  `licence` + `inputs_path` + `outputs` + `output_schema` + `produces_intent_schema`;
  aligns to photometric-analysis sibling convention). Standards array of 8 strings
  (BS 7671 Part 7 §701/§702/§703/§710/§715; HTM 06-01; BS EN 60601 series; BS EN 61557-8;
  BS EN 61558-2-6; BS 5266-1). `produces_intents` (special-locations-zoning v1.0.0,
  `name` + `schema_path` fields per photometric convention); `consumes_intents`
  (lighting-layout v^1.5, cascade DSL trigger + consumed_fields). 17 example paths
  registered. `_v1_limitations` explicitly declared (MRI / NEC / §722 /
  embedded-heating / INT full examples all deferred). Empty subdirs ready for A.2/A.3/A.4:
  `schemas/`, `prompts/`, `evals/`, `examples/`, `rules/`.
- **IR + intent schemas.** `schemas/special-locations-ir.schema.json` — full IR with
  zone_layout[], constraint_summary, bonding_requirements, non_compliance_flags[],
  rationale, provenance. `schemas/special-locations-zoning-intent.schema.json` — flat
  downstream payload (zones[], jurisdiction, enforcement_targets).
- **Inputs taxonomy.** `inputs.json` — 6 items: anchor_fixtures[] (required),
  room (required), water_jet_present (optional), medical_group_override (optional),
  it_system_present (optional), nhs_site (optional). Rules YAML: 5 files covering zone-
  geometry derivation, RCD requirements, SELV/IP constraints, bonding policy, medical IT.
- **Zone-derivation library.** `shared/special-locations/zone-derivation/` — parametric
  zone derivation from anchor geometry for each Part 7 section; no lookup tables.
- **Generator prompt.** `prompts/generator.md` — multi-step zone derivation pipeline
  (anchor ingestion → zone polygon computation → constraint set assembly → bonding schedule →
  non-compliance pre-check → IR emit → intent emit).
- **Validator prompt.** `prompts/validator.md` — 10 INVs (INV-01 zone geometry
  completeness through INV-10 provenance completeness); 6 HIGH + 4 MEDIUM.
- **Reviewer prompt.** `prompts/reviewer.md` — 5 D-checks (room-type consistency;
  changing-room adjacency; medical group plausibility; ELV external hazard; bonding schedule
  completeness).
- **Standalone examples (8).** uk-bathroom-standard-bath-and-shower,
  uk-bathroom-whirlpool-with-pump, uk-shower-room-wet-room-floor,
  uk-pool-hall-with-changing-room-adjacency, uk-sauna-with-3-zone-derivation,
  uk-medical-or-group-2-with-it-system, uk-medical-ward-group-1-bonding,
  uk-external-landscape-elv-lighting. Each carries input.json + output.json + reasoning.md.
- **Cascade examples (9).** 9 cascade examples across lighting-layout v1.6 / small-power
  v1.2 / db-layout v1.5 consumers. Includes KE §313 dual-citation example and violation
  demo examples (socket exclusion breach, missing isolation).
- **Evals (8 YAMLs).** zone-geometry-completeness, rcd-blanket-enforcement,
  selv-zone-0-constraint, imd-8s-alarm-response, ipx5-whirlpool-pump,
  socket-exclusion-3m, ke-jurisdiction-routing, bonding-schedule-integrity.

### Cascade integration with downstream skills
- lighting-layout v1.5 → v1.6: manifest gains `consumes_intents` for
  `special-locations-zoning`; validator gains zone-aware luminaire IP check; 3 existing
  examples retrofitted.
- small-power v1.1 → v1.2: socket-outlet exclusion zone enforcement via consumed
  `special-locations-zoning` intent; isolation distance check for §702/§710.
- db-layout v1.4 → v1.5: RCD allocation enforcement from zone constraints; §710 Group 2
  medical IT distribution board recognition.

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
