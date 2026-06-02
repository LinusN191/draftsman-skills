# Changelog

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
