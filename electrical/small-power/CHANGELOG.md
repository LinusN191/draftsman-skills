# Changelog

## [2.0.0] - 2026-06-03 — Wave 2 first deliverable: within-skill-depth program closed; beta → production

_D4 depth sprint. Adds 5 scope items: `building_diversity` IR field mirroring verified standards (office / industrial / healthcare profiles), 4 new Part-7 worked examples (pool / medical IT / EV / sauna), comprehensive ring-topology depth (4 new INVs: ring-continuity + floor-area cross-check + OCPD-topology + AMD 2 FCU spur), EV-charge demand coordination with Type A/B RCD selection per BS 7671:2018+A2:2022 Reg 722.531.3.101, and INV-19 verifying cable-sizing cascade integration with building-level diversity._

### Changed
- `skill.manifest.json` version 1.2.0 → 2.0.0. Bump is **signalling only** — not a breaking
  change. All v2.0 schema additions are additive; all v1.x examples validate against the v2.0
  schema without modification (v1.x ring_endpoints/fcu_spurs/ev_charge_metadata are all
  `required` only under their respective `if`/`allOf` clauses). Bump signals:
  within-skill-depth program for small-power is CLOSED; small-power is architecturally
  complete and promoted to `status: production`.
- `skill.manifest.json` status `beta` → `production`.
- `skill.manifest.json` `standards[]` +5 entries: BS EN 60884-1 (socket-outlet terminals),
  BS EN 60601 series (medical electrical), BS EN 60335-2-53 (sauna appliances),
  BS EN 61851-1 (EV mode and control), BS EN 62196 (EV connector types).
- `skill.manifest.json` `calculations[]` extended: `calc.building_diversity` added (new
  shared contract wrapping `calc.diversity_factor` at building scope); `calc.ev_demand`
  added (IET OSG App A Table A1 EV demand coefficient).

### Added (IR schema — `electrical/small-power/schemas/small-power-ir.schema.json`)
- New optional top-level `building_diversity` object: `profile`
  (`office_general | industrial_warehouse | healthcare_ward`), `applied_demand_kva`,
  `demand_coefficient`, `iet_osg_table_ref` (`"IET OSG App A Table A1"`), and
  `coincidence_note` (evidence string). Mirrors verified standards at
  `shared/standards/electrical/BS7671/diversity-factors.json`.
- New conditional fields per circuit:
  - `ring_endpoints`: required when `topology = ring`; captures `socket_a_id` + `socket_b_id`
    + `continuity_r1_r2_ohm` (measured loop resistance) for ring-continuity enforcement
    (INV-14 + INV-17).
  - `fcu_spurs[]`: required when `topology = ring` AND any outlet is FCU-spurred; each entry
    carries `fcu_id`, `rating_a`, `cable_csa_mm2`, `length_m`, `bs_en_60884_ref`.
    Fuse-spurred FCU count gated per BS 7671:2018+A2:2022 §314 + IET OSG §8.4.4.
  - `ev_charge_metadata`: required when `load_type` matches `ev_charge_*`; carries
    `mode`, `connector_standard` (BS EN 62196-2/3), `min_rcd_type`
    (`type_a_per_722.531.3.101 | type_b_per_722.531.3.101`), `dedicated_circuit_per_722.4`,
    and `demand_va_per_iet_osg_table_a1`.
- Three new `allOf` enforcement clauses:
  1. `if topology = ring` → `ring_endpoints` required (guards INV-14/INV-17).
  2. `if load_type in ev_charge_*` → `ev_charge_metadata` required (guards INV-16/INV-18).
  3. `if building_diversity present` → `applied_demand_kva` ≤ `total_circuit_demand_kva`
     (arithmetic consistency; guards INV-13).

### Added (rules YAML)
- **NEW `rules/building-diversity-rules.yaml`**: 3 profile rules
  (`office_general` per IET OSG App A Table A1 0.5 coefficient /
  `industrial_warehouse` 0.7 coefficient / `healthcare_ward` 1.0 coincidence —
  BS 7671:2018+A2:2022 §311.1 diversity application). Includes `applies_after: "INV-07"`
  guard confirming total demand was computed first.
- **NEW `rules/ev-charge-rules.yaml`**: 4 rules — EV-01 dedicated-circuit mandate
  (BS 7671 §722.4 + BS EN 61851-1 §4.3), EV-02 no-diversity on EV circuits
  (IET OSG App A Table A1 footnote), EV-03 RCD type selection
  (Type A for Mode 2; Type B for Mode 3 with inverter DC leakage per Reg 722.531.3.101),
  EV-04 connector standard (BS EN 62196-2 Type 2 / BS EN 62196-3 CCS2 per OZEV grant
  scope — citation form: "BS EN 62196-2:2022 Table 1", NOT "OZEV CoP" which is banned).
- **`rules/topology-rules.yaml` extended**: 4 new TOP-NN entries — TOP-06 FCU-spur maximum
  count per IET OSG §8.4.4, TOP-07 ring continuity r1+r2 ceiling per IET OSG §8.4.4
  Table D, TOP-08 floor-area cross-check (≤100 m² per ring per IET OSG §8.4.4), TOP-09
  OCPD-topology enforcement (BS 7671:2018+A2:2022 §433.1 — ring fused at ≤32 A both ends).
- **`rules/diversity-rules.yaml` extended**: DIV-05 lift-demand coefficient from
  IET OSG App A Table A1 (NOT from BS 7671 Reg 559 — §433.2/§559 are banned citation
  anchors for demand figures; IET OSG App A is the verified anchor).

### Added (prompts)
- **Generator** (`prompts/generator.md`): Steps 13-15 added after existing Step 12 (Zs
  resolution). Step 13: building_diversity assembly from profile rules. Step 14:
  EV-charge metadata + RCD type determination from ev-charge-rules.yaml. Step 15:
  ring-endpoint continuity check and FCU-spur count validation.
- **Validator** (`prompts/validator.md`): INV-13 through INV-19 added (7 new checks;
  12 → 19 total):
  - INV-13 building-diversity self-consistency HIGH (demand_coefficient × circuits sum ≈ applied_demand_kva).
  - INV-14 ring-continuity structural HIGH (ring_endpoints present on every ring circuit).
  - INV-15 ring-floor-area cross-check MEDIUM (each ring ≤100 m² per IET OSG §8.4.4).
  - INV-16 EV-charge metadata completeness HIGH (ev_charge_metadata on every EV circuit).
  - INV-17 ring-endpoint value plausibility HIGH (r1+r2 ≤ IET OSG Table D ceiling for CSA).
  - INV-18 EV-RCD type selection HIGH (Mode 3 → Type B; Mode 2 → Type A per Reg 722.531.3.101).
  - INV-19 cable-sizing cascade integration MEDIUM (when cable-sizing intent consumed,
    building_diversity applied_demand_kva ≤ upstream rated_current × voltage).
- **Reviewer** (`prompts/reviewer.md`): D-8 building-diversity profile plausibility,
  D-9 EV-circuit isolation audit, D-10 Part-7 zone + EV-charge coherence. (6 → 9 D-checks.)
- **Cascade-prereq context block** in generator updated: `special-locations-zoning` trigger
  section extended to note that §703 sauna-heater exemption and §702 pool-basin isolation
  now have dedicated producer-side cascade examples (cascade-small-power-uk-ev-charge-domestic
  + cascade-small-power-uk-sauna-heater-exemption in `electrical/special-locations/examples/`).

### Added (examples — 8 NEW + 1 RETROFIT; total 6 → 15)
- **`uk-pool-hall-sockets-and-isolation/`** (NEW Part-7 #1): BS 7671 §702 pool-hall.
  Consumed special-locations-zoning intent (pool_basin anchor). Zone 2 RCD Type A 30 mA;
  isolation transformer for underwater luminaires per §702.55.4. INV-12 cascade + INV-14
  ring-topology both exercised.
- **`uk-medical-group-2-isolation-sockets/`** (NEW Part-7 #2): BS 7671 §710 Group 2 medical.
  IT system declared; BS EN 60601-1 socket-outlets (3-pin Schuko with isolation marking);
  IMD 8-second alarm; INV-12 cascade (medical-group zone). No-diversity coincidence (1.0)
  per healthcare_ward profile.
- **`uk-ev-charge-domestic/`** (NEW Part-7 #3): Domestic garage EV install. Mode 3 wallbox,
  BS EN 62196-2 Type 2, dedicated 32 A radial per §722.4, RCD Type B per Reg 722.531.3.101;
  INV-16 + INV-18 exercised. Producer-side cascade fixture:
  `special-locations/examples/cascade-small-power-uk-ev-charge-domestic/`.
- **`uk-sauna-with-heater-exemption/`** (NEW Part-7 #4): BS 7671 §703 sauna. Heater circuit
  exempt from RCD per §703.410.3.6 (appliance-integral thermal protection cited per
  BS EN 60335-2-53 §22.106); socket exclusion zones enforced; INV-12 cascade. Producer-side
  cascade fixture: `special-locations/examples/cascade-small-power-uk-sauna-heater-exemption/`.
- **`uk-office-floor-with-building-diversity/`** (NEW diversity demo #1): Open-plan office,
  building_diversity profile `office_general`, demand_coefficient 0.5, IET OSG App A Table A1.
  INV-13 exercised. Cable-sizing intent consumed (INV-19 demonstrated PASS).
- **`uk-industrial-warehouse-with-building-diversity/`** (NEW diversity demo #2): Industrial
  warehouse, profile `industrial_warehouse`, coefficient 0.7. Includes fork-lift charge point
  (EV-charge_generic, Mode 2, Type A RCD). INV-13 + INV-16 + INV-18 exercised.
- **`uk-3bed-with-ring-continuity/`** (NEW topology demo): UK 3-bed dwelling, ring sockets.
  `ring_endpoints` populated per circuit with continuity_r1_r2_ohm values from IET OSG
  Table D. FCU spur count within limit. INV-14 + INV-17 PASS. Demonstrates positive case.
- **`uk-3bed-with-ring-continuity-violation/`** (NEW topology FAIL HIGH demo): Same scenario
  but ring_endpoints.continuity_r1_r2_ohm exceeds IET OSG Table D ceiling for 2.5 mm²;
  INV-17 fires FAIL HIGH. Demonstrates negative case.
- **RETROFIT `uk-bathroom-shaver-and-zone2-sockets/`**: `ring_endpoints` added to ring
  circuit with honest engineering-judgement defaults (measured values pending commissioning);
  `_retrofit_note` field added per v2.0 retrofit pattern.

### Added (evals — 5 new; total 5 → 10)
- `eval-09-building-diversity-self-consistency.yaml` (skill_specific; 3 checks; INV-13).
- `eval-10-ring-continuity-passes.yaml` (skill_specific; 3 checks; INV-14 + INV-17 PASS case).
- `eval-11-ring-continuity-fails.yaml` (skill_specific; 2 checks; INV-17 FAIL case detection).
- `eval-12-ev-charge-rcd-type-determination.yaml` (skill_specific; 3 checks; INV-16 + INV-18).
- `eval-13-cable-sizing-cascade-integration.yaml` (skill_specific; 2 checks; INV-19).

### Added (producer-side cascade fixtures in special-locations)
- `electrical/special-locations/examples/cascade-small-power-uk-ev-charge-domestic/`
  (4 files): Producer source for small-power EV example; §702/§722 zone intersection.
  Closes C.3 consumer integrity loop.
- `electrical/special-locations/examples/cascade-small-power-uk-sauna-heater-exemption/`
  (4 files): Producer source for small-power sauna example; §703 zone derivation with
  heater-exemption annotation. Closes C.4 consumer integrity loop.

### Honest disclosures
- `building_diversity` v2.1 deferrals: healthcare_ward lift-demand coincidence (IET OSG App A
  Table A1 row 6) + mixed-use cross-profile blending deferred.
- 2.0 bump-as-signaling rationale: no v1.x consumer was pinned to `^1.x` at bump time
  (A.5 pre-merge check confirmed; earthing manifest widened to `>=1.0`).
- All ring-endpoint continuity values on retrofitted v1.x examples carry
  `_retrofit_note: "engineering-judgement defaults — measured values to be substituted at commissioning"`.

### Citation hygiene (per spec §11.1 + D4 brainstorm §11 banned list)
- Banned anchors confirmed absent: `§526.2` (connection resistance — not a demand figure),
  `§433.2` (overload protection — not a demand figure), `OZEV CoP 3rd Edition`,
  `OZEV CoP 4th Edition` (internal policy docs — not normative; replaced by BS EN 62196 + §722).
- All EV citations trace to: BS 7671:2018+A2:2022 §722 + IET OSG App A Table A1 + BS EN 61851-1
  + BS EN 62196-2/3.
- All lift-demand citations trace to IET OSG App A Table A1 (NOT Reg 559).

### Gates
- `validate-examples.py`: 316 → 341 (+25); all 3 passes GREEN.
- `functional_audit.py`: 1 finding unchanged (disclosed motor-superposition oracle FP on
  fault-level/us-industrial-with-motors/MCC-1).

## [1.2.0] - 2026-06-02 — Wave 1: special-locations cascade contract + Floor plan context portability

_Two parallel-shipped deliverables merged into a single version entry. The Wave 1 special-locations cascade contract (the main deliverable) is documented first; the Floor plan context portability changes (originally landed as PR #2 / commit 013861b) are appended below._


### Changed
- `skill.manifest.json` version 1.1.0 → 1.2.0 (additive; backward-compatible IR additions).
- `consumes_intents[]` extended with `special-locations-zoning` cascade entry.
  Trigger: WI3 `room_context.room_type` matches the Part-7 set OR any
  `outlets[].room_id` resolves to a Part-7 room. Joins `cable-sizing-results`
  as the second downstream-cascade consumer for this skill.

### Added (IR schema — `electrical/small-power/schemas/small-power-ir.schema.json`)
- New `allOf` clause: when `flags[]` contains `part7_zone_present`,
  `consumed_intents.special_locations_zoning` MUST be populated. Structural
  enforcement; semantic content enforced by INV-12.
- `consumed_intents.special_locations_zoning` sub-object with `intent_version`
  + `source_path` + `payload` mirroring the FLAT shape of the special-locations
  zoning intent.

### Added (validator)
- **INV-12 — Special-locations zoning cascade resolved (HIGH)**. 4 sub-checks:
  (1) cascade structural presence; (2) payload counts reconcile;
  (3) socket-by-zone gating per `payload.zones[].prohibited_fixture_types` +
  zone polygon containment per `outlets[].position_xyz_mm`; (4) negative
  coverage of non-applicable Part-7 sub-rules (medical IT / pool main bonding /
  sauna heater exemption).
- IR `invariants[].evidence` cap left at 800 chars for this skill; INV-12
  evidence engineered to fit the cap in the cascade examples shipped.

### Added (examples)
- **NEW `examples/uk-bathroom-shaver-and-zone2-sockets/`**: UK 2700 × 2100 mm
  bathroom; BS EN 61558-2-5 shaver supply unit at 1400 mm AFFL + Zone 2
  mirror-side proximity outlet. Consumed-intent walked the shaver socket
  against `prohibited_fixture_types` (sees it is BS EN 61558-2-5, not
  `socket_230v` — passes Zone 2 gating). Shared bathroom fixture with
  `lighting-layout/uk-bathroom-zone-1-zone-2` and
  `db-layout/uk-bathroom-rcd-distribution`.

### Scope note
- This release wires the cascade contract end-to-end; deeper small-power
  depth (multi-circuit RCD discrimination, BS 1363-A vs BS EN 60309-2
  vehicle-charging selection inside the cascade) is deferred to Wave 2.
- Cascade is read-only for the small-power consumer: payload inlined for
  reproducibility on golden examples; runtime resolves `source_path`
  at execution time.
### Floor plan context portability (PR #2)

### Changed
- Replaced previous Sprint 4-AB `architectural_state` section in
  `prompts/{generator,reviewer,validator}.md` with the generic
  `## Floor plan context` contract. Prompt is now portable across AI
  runtimes that inject room-list markdown under that heading.
- Inlined the contract per-file; deleted the previous
  `shared/architectural_state_contract.md` dependency.

### Added (IR schema — `schemas/small-power-ir.schema.json`)
- NEW optional top-level `floor_plan_context_consumed: boolean`
  (default `false`). IR sets `true` when the prompt context included
  a `## Floor plan context` block.

## [next-patch] - 2026-05-25 — M1 hybrid eval-vs-IR fix

### Added
- `invariants[]` field added to the IR root (required). Each entry is
  `{id: "INV-NN", passes: bool, severity: critical|high|medium|low, evidence: 20-800c prose}`.
- Generator prompt gained a step instructing it to populate `invariants[]` per
  validator-INV that applies to the current example.

### Changed
- Eval assertions reconciled to actual IR field locations. Where evals
  referenced runtime-fan-out fields (`ir.emitted_intents`, `ir.intent_emitted`,
  `ir.citations` at root), assertions now point at the equivalent IR field
  (rationale section summaries / decisions[*].code_clause / sibling IR root
  fields). `ir.invariants.INV-NN.passes` rewritten as
  `ir.invariants[?(@.id=="INV-NN")].passes` to match the new array shape.

### Rationale
Sprint B Task B.5 — closes M1 (functional_audit MEDIUM eval-vs-output drift).
Evals were aspirational specs that had drifted from the IR schemas; this
change makes the validator-INV evidence visible to the runtime eval harness
and fixes the dangling-path findings without weakening the engineering
contract.

## [1.1.0] - 2026-05-20

### Added — cable-sizing intent consumer migration (hybrid mode)

- **Multi-skill consumption**: `consumes_intents: ["cable-sizing"]` (was `[]`). Hybrid posture — when cable-sizing intent is provided in runtime inputs, every circuit's `verified_zs_ohm` is resolved from `Ze + (r1_plus_r2 / 1000) × length + (reactance / 1000) × length`; when intent is absent, v1.0 deferral behaviour holds (no breaking change).
- **Schema (additive, non-breaking)**: typed `meta.consumed_intents.items` (matches SLD v1.4 shape — required `intent_type` + `intent_version` + `produced_by`); new optional `cable_sizing_node_id` field per circuit (explicit override for the implicit `f"{parent_db.designation}.{circuit_id}"` composition).
- **Generator**: 12 → 13 numbered steps (new Step 12 inserted: "Resolve Zs from cable-sizing intent"); existing rationale step renumbered.
- **Validator**: 10 → 11 INV checks (new INV-11: cable-sizing intent lookup integrity — hard fail when intent consumed but a circuit's lookup fails).
- **Reviewer**: 6 → 7 D-checks (new D-7: Zs resolution provenance audit — flags mixed states where some circuits resolved and others deferred).
- **New worked example**: `examples/uk-3bed-with-cable-sizing/` (5 files: input.json + consumed-cable-sizing-intent.json + output.json + intent-out.json + reasoning.md). Mirrors the v1.0 `uk-3bed-dwelling` scenario but in v1.1 consumption mode with resolved Zs per circuit.
- **New eval**: `eval-10-cable-sizing-intent-consumed.yaml` (skill_specific category) — 6 checks covering v1.1 consumption behaviour.

### Unchanged from v1.0 (additive sprint — no breaking changes)

- All 4 existing v1.0 examples (`uk-3bed-dwelling`, `ke-nairobi-small-office`, `intl-open-plan-floor`, `us-residential-dwelling`) — now demonstrate v1.1 hybrid fallback behaviour when no intent is consumed
- All 9 existing v1.0 evals (eval-01 through eval-09)
- 5 rules + 3 constraints + 3 validation YAMLs
- Ontology (`shared/ontology/equipment/socket-types.json`) + symbols (`shared/symbols/electrical/sockets/`)
- Manifest `standards[]`, `ontology[]`, `calculations[]` arrays (no path changes)

### Pattern parents

- SLD v1.3 → v1.4 (leaf → multi-skill consumer) — closest structural precedent
- cable-sizing v1.0 refresh §2 (forward-compat contract this sprint fulfils)
- lighting-layout v1.3 (flexible-inputs pattern)

## [1.0.0] - 2026-05-19

### Added — first ship (beta)

- **Leaf skill v1.0**: produces small-power intent for downstream db-layout consumption. `consumes_intents: []` matches lighting-layout v1.3 production pattern.
- **Hybrid IR shape**: `circuits[]` (with topology enum: ring | radial | dedicated_radial) + `rooms[]` (with sockets[] cross-referencing circuit_ids). Cross-room rings naturally supported.
- **3-value topology enum**: `ring` (GB+KE only via KS 1700 §313 routing — INV-04 enforces); `radial` (all jurisdictions, default for KE/INT/US); `dedicated_radial` (single-load circuits per BS 7671 §433.1.4 / NEC 210.23).
- **6-value special-location enum**: `null` | `bathroom_zone_1` | `bathroom_zone_2` | `bathroom_zone_3` | `outdoor` | `wet_area`. Maps to BS 7671 Part 7-701 / IEC 60364-7-701 / KS 1700 Part 7 / NEC 210.8.
- **3-value rcd_posture enum**: `type_a_30ma_per_§411_3_3` (default for sockets ≤32A); `type_b_30ma_per_§531_3_3` (IT loads with DC leakage per IEC 60364-5-53 §531.3.3); `no_rcd_with_documented_§411_exception` (engineer-declared with explicit citation).
- **4 jurisdictional examples**: UK 3-bed dwelling + KE Nairobi small office + INT commercial open-plan + US residential dwelling.
- **3 prompts**: generator + validator (10 INV checks) + reviewer (6 D-checks). Pattern matches arc-flash-labelling + SLD v1.5.
- **9 evals**: 5 WI5 categories + 4 skill-specific (ring-topology-by-jurisdiction, special-locations compliance, cross-room ring integrity, GFCI scope US).
- **Drafting standards consumption**: sheet template + scale + layer naming consumed from v1.6 drafting standards layer per jurisdiction.
- **Calc tool consumption (existing contracts reused)**: `calc.diversity_factor` (shared/calculations/electrical/diversity-factor.json) + `calc.zs_loop_impedance` (shared/calculations/electrical/zs-loop-impedance.json — _consuming_skills updated to add small-power).
- **NEW standards addition**: `shared/standards/electrical/NFPA70/part7-special-locations.json` (US GFCI scope per NEC 210.8).

### Architectural notes

- Cross-skill consistency without intent consumption: INT example C06 (server-room small-power) manually mirrors the Type B 30mA RCD policy from db-layout's shipped `intl-dbcomms-data` example. Engineer mirrors the policy as input; v1.1+ will consume earthing intent for automatic cross-skill alignment.
- WI3 deferral: `tool_call_pending_for_zs_verification: true` per circuit + `TOOL-CALL-PENDING:calc.zs_loop_impedance` in flags[]. Matches SLD v1.3 + earthing v1.1 precedent.
- WI2 rationale: 8 sections + chat_summary ≤500 chars per example.

### Pattern parents

- lighting-layout v1.3 (production) — gold-standard layout skill; full folder scaffolding template
- SLD v1.5 — drafting standards consumption + multi-skill migration precedent
- earthing v1.4 — 4-jurisdiction example pattern + KS 1700 routing convention
- db-layout v1.3 — future consumer of small-power intent; intl-dbcomms-data Type B RCD precedent
- arc-flash-labelling — validator (~17 INV) + reviewer (6 D) pattern
- drafting standards v1.6 — sheet template + scale + layer naming

### Future direction (deferred)

- v1.1+ — multi-skill intent consumption (consume earthing + fault-level intents); INV-N cross-skill consistency checks
- v2.0 — schema-breaking changes (multi-board consumption, EV charging integration)
- ev-charging skill — BS 7671 Part 7-722 / NEC 625 / IEC 60364-7-722 (separate skill)
