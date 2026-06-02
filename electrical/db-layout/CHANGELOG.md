# Changelog — db-layout

## [1.5.0] - 2026-06-02 — Wave 1: special-locations cascade contract + Floor plan context portability

_Two parallel-shipped deliverables merged into a single version entry. The Wave 1 special-locations cascade contract (the main deliverable) is documented first; the Floor plan context portability changes (originally landed as PR #2 / commit 013861b) are appended below._


### Changed
- `skill.manifest.json` version 1.4.0 → 1.5.0 (additive; backward-compatible
  IR additions).
- `consumes_intents[]` extended with `special-locations-zoning` cascade entry.
  Trigger: any room served by this board (derived from upstream
  lighting-layout `room_adjacency_graph` or WI3 `room_context`) matches
  the Part-7 set (bathroom, shower_room, swimming_pool_hall, sauna,
  medical_group_0_area, medical_group_1_ward, medical_group_2_theatre,
  external_landscape).

### Added (IR schema — `electrical/db-layout/schemas/db-layout-ir.schema.json`)
- New `allOf` clause: when `flags[]` contains the sentinel
  `part7_zone_present`, `consumed_intents.special_locations_zoning` MUST be
  populated. Sentinel-pattern enforcement (different from lighting-layout
  which uses `rooms[].room_type` directly); chosen because db-layout's room
  model is implicit-via-circuits rather than explicit-rooms-list.
- `consumed_intents.special_locations_zoning` sub-object: `intent_version` +
  `source_path` + `payload` via `$ref` to the special-locations zoning intent
  schema.
- **Schema cap raise**: `invariants[].evidence.maxLength` 800 → 1200 to
  accommodate INV-16 cascade evidence (cascade source path + 4 sub-checks
  + circuits walked + 4 distribution sub-rules with negative coverage).
  Style-only cap raise per [[feedback-no-trim-non-consequential]]; existing
  21 example INV evidence blocks all already fit 800. Matches the
  lighting-layout shared-schema cap.

### Added (validator)
- **INV-16 — Special-locations distribution cascade resolved (CRITICAL)**.
  4 sub-checks:
  (1) cascade structural presence + `payload.compliant: true`;
  (2) `payload.zone_count` + `payload.constraint_count` reconcile with
      array lengths;
  (3) each circuit serving a Part-7 room verified to gain RCD protection
      per `payload.electrical_constraints[].rcd_rating_ma`;
  (4) negative-coverage for the 4 distribution sub-rules — only the rule
      that applies to the room class fires (e.g. § 701 bathroom →
      rcd_blanket only; no medical IT panel, no pool main bonding, no
      board-side supplementary bonding terminal).
- Reviewer prompt extended with cascade-discipline checks.

### Added (examples)
- **NEW `examples/uk-bathroom-rcd-distribution/`**: UK first-floor consumer
  unit DB-FF1; 230 V single_phase 60 A switch-disconnector, Form 1 IP2X
  10-way Hager-style. Scope-cut to the 2 bathroom-serving circuits
  (C-B1 lighting RCBO 6 A + C-B2 shaver/shower-pump RCBO 16 A); 7 other
  first-floor circuits flagged as deferred. Per-circuit RCBO topology
  chosen over grouped main RCD per BS 7671 § 314.1 (avoidance of unwanted
  disconnection). `flags[]` includes `part7_zone_present` sentinel;
  triggers the allOf clause non-vacuously. Shared bathroom fixture with
  `lighting-layout/uk-bathroom-zone-1-zone-2` and
  `small-power/uk-bathroom-shaver-and-zone2-sockets`.

### Honest disclosures preserved
- Cascade is read-only for the distribution consumer: payload inlined on
  this golden example for reproducibility; runtime resolves `source_path`
  fresh.
- The new example is a deliberate scope-cut (2 of ~9 actual first-floor
  circuits) so the Part-7 cascade can be exercised in isolation; the cut
  is recorded as an INFO flag on `compliance_summary.non_compliance_flags[]`.
### Floor plan context portability (PR #2)

### Changed
- Replaced previous Sprint 4-AB `architectural_state` section in
  `prompts/{generator,reviewer,validator}.md` with the generic
  `## Floor plan context` contract. Prompt is now portable across AI
  runtimes that inject room-list markdown under that heading.
- Inlined the contract per-file; deleted the previous
  `shared/architectural_state_contract.md` dependency.

### Added (IR schema — `schemas/db-layout-ir.schema.json`)
- NEW optional top-level `floor_plan_context_consumed: boolean`
  (default `false`). IR sets `true` when the prompt context included
  a `## Floor plan context` block.

## [1.4.0] - 2026-05-26 — Sprint D2.2 + D2.3 (labels + diversity edge cases)

### Added (Sprint D2.2 — labels)
- **label_format_standard at root**: enum BS|NEC|IEC; jurisdiction-mapped
  GB/KE→BS, US→NEC, INT/EU→IEC; engineer override permitted.
- **board_label at root**: text (≤120c, formatted per std) + svg
  (populated from templates/) + tool_call_pending_for_pdf_png.
- **circuit_label per circuit**: text (≤80c) + svg + tool_call_pending.
  Required on every circuits[].items entry.
- **NEW templates/ directory** with 6 .svg.template files mirroring the
  arc-flash-labelling pattern: BS / NEC / IEC × circuit / board.
- **Validator INV-14: Label format compliance** (HIGH, 6 rules).
- Generator prompt step covering label_format_standard derivation +
  per-jurisdiction text format + svg template population.
- shared/calculations/electrical/render-label.json added to manifest
  calculations[] (reuses arc-flash-labelling's calc contract).

### Added (Sprint D2.3 — diversity edge cases)
- **diversity_basis per circuit**: required object on every circuit
  with load_type (13-enum) + factor_applied [0.0, 1.0] + method enum +
  optional method_params + citation (≥20c with clause marker).
- **Generator prompt per-load-type table extended** with 4 new rows:
  lift (EN 81-20:2020 §5.10 + BS 7671 Section 552, factor 1.00),
  ev_charger (Reg 722 + IET CoP for EVCI 4th Ed §8.5, factor 1.00),
  ac_single (Section 552 by analogy, factor 1.00), ac_group (engineer-
  declared 100% largest + 75% remainder by analogy to Reg 552). Motor +
  socket existing rows tightened with explicit Reg 552.1.1 / OSG App
  A motor section citations.
- **Validator INV-15: Diversity basis cited per circuit** (HIGH, 4
  rules — presence + range + citation marker + lift/EV factor==1.00
  hard rules + method_params sum range [100, 200]).

### Examples
- **D2.2 backport**: 20 existing examples gained label_format_standard
  + board_label + per-circuit circuit_label. No IE/load/OCPD value
  changes; labels derived from existing content.
- **D2.3 backport**: 20 existing examples gained diversity_basis on
  every circuit, inferring load_type from designation.
- **NEW example uk-mixed-use-lifts-and-ev**: demonstrates 5 new
  diversity rows in one mixed-use SDB (lift + 4 EV chargers + AC
  single + AC group + sockets + lighting). Total demand 62.115 kW
  on 200 A TPN main.

### Honest disclosures
- IET Code of Practice for EV Charging Equipment Installation (4th Ed)
  is INDUSTRY GUIDANCE, not statutory. BS 7671 Reg 722 IS statutory and
  the IET CoP is the industry-standard reference for Reg 722 compliance.
  Both citations appear in every EV circuit's diversity_basis.citation.
- Multi-split AC group 100% largest + 75% remainder rule is engineering
  practice with no single authoritative pinpoint clause in published UK
  guidance — closest anchor is BS 7671 Section 552 motor diversity by
  analogy. Citation flags this inline; engineer-of-record must validate.
- BS 7671 has NO dedicated lift regulation. Lift safety envelope comes
  from EN 81-20:2020 §5.10 + the motor-circuit aspect from BS 7671
  Section 552. (Sprint D2.3 originally cited a non-existent Reg 559;
  D2.3 fix-pass corrected this across all 5 lift-touched locations.)
- Templates/ directory deferred SVG-to-PDF rasterisation to runtime
  per [[runtime-project-boundary]]; tool_call_pending_for_pdf_png=true
  on every label entry.

### Schema migration impact
- circuit_label, diversity_basis, board_label become required after
  1.4.0. v1.3 IR consumers reading 1.4.0 outputs without awareness of
  these fields are unaffected (additive); consumers that DO consume
  them must be aware of the schema bump.

## [1.3.3] - 2026-05-25

### Added
- **D1.0 (Sprint D1 prerequisite):** `main_switch.breaking_capacity_ka` +
  outgoing-circuit `breaker_breaking_capacity_ka` declared in the intent
  schema (now required). Field already existed in the output IR; the
  intent was the missing piece. Enables downstream fault-level Sprint D1
  hybrid-consumer breaking-capacity verdict (D1.1).
- Backported the field across all 20 example intent-out.json files
  by reading from each example's corresponding output.json main_switch
  + per-circuit ocpd block.

## [1.3.2] - 2026-05-25

### Added (Sprint B M1 hybrid eval-vs-IR fix)
- `invariants[]` field added to the IR root (required). Each entry is
  `{id: "INV-NN", passes: bool, severity: critical|high|medium|low, evidence: 20-800c prose}`.
- Generator prompt gained a step instructing it to populate `invariants[]` per
  validator-INV that applies to the current example.

### Changed (Sprint B M1 hybrid eval-vs-IR fix)
- Eval assertions reconciled to actual IR field locations. Where evals
  referenced runtime-fan-out fields (`ir.emitted_intents`, `ir.intent_emitted`,
  `ir.citations` at root), assertions now point at the equivalent IR field
  (rationale section summaries / decisions[*].code_clause / sibling IR root
  fields). `ir.invariants.INV-NN.passes` rewritten as
  `ir.invariants[?(@.id=="INV-NN")].passes` to match the new array shape.

### Sprint B M1 rationale
Sprint B Task B.5 — closes M1 (functional_audit MEDIUM eval-vs-output drift).
Evals were aspirational specs that had drifted from the IR schemas; this
change makes the validator-INV evidence visible to the runtime eval harness
and fixes the dangling-path findings without weakening the engineering
contract. (Originally tracked as [next-patch]; promoted into [1.3.2]
during Sprint D1 verification fence because both M1 and H5/H6 shipped
together on 2026-05-25 as Sprint B remediation.)

### Fixed
- **H5**: blanket 0.4 diversity factor was applied to instantaneous loads
  (9 kW shower). Per BS 7671:2018+A2:2022 § 311.1 + IET OSG Appendix A,
  instantaneous loads get NO diversity. uk-domestic-consumer-unit recomputed
  with per-load-type table (shower at 1.00, cooker at 10 A + 30% remainder,
  lighting at 0.66, sockets at 100% largest + 40% remainder). Citation
  corrected: BS 7671 Appendix 1 (informative) → IET OSG Appendix A + § 311.1.
  Reported demand changed from 47 A (wrong) to 88.91 A (correct) on the
  100 A supply — headroom collapses from 53 A to ~11 A, now flagged as
  marginal.
- **H6**: phase allocation was dropped on TPN board outputs; per-phase
  loading and neutral current were not computed. All 17 TPN example outputs
  now carry `phase` per circuit (preserved from input.json where declared,
  else L1/L2/L3 round-robin), `per_phase_loading_a` per board, and
  `neutral_current_a` computed from the IEC 60364-5-52 § 524.2.2 worst-case
  unbalance formula.

### Added
- Generator prompt (Step 5): per-load-type diversity table (IET OSG App A)
  with explicit 1.00-factor call-out for instantaneous loads, plus phase
  preservation rule for TPN boards (phase field per circuit +
  per_phase_loading_a + neutral_current_a + unbalance flag guidance).
- Validator **INV-12** (diversity on instantaneous loads, HIGH).
- Validator **INV-13** (phase preservation + per-phase loading + neutral
  current on TPN boards, HIGH).
- Schema: optional `phase` (circuit, enum incl. L1/L2/L3 + 3-phase span
  forms), `per_phase_loading_a` + `neutral_current_a` (top-level board) —
  additive, doesn't break existing examples.

### TPN examples updated (17)
intl-commercial-tpn-msb, intl-dbcomms-data, intl-dbem-emergency-lighting,
intl-dbfa1-fire-alarm, intl-dbgenset-changeover, intl-dbl1-lighting,
intl-dbm1-mechanical, intl-dbp1-power, intl-dbups-backed,
ke-nairobi-industrial-100A-tpn, uk-commercial-msb-3storey,
uk-commercial-sdb-gf, uk-commercial-sdb-l1, uk-commercial-sdb-l2,
us-strip-mall-common-area, us-strip-mall-tsp-a, us-strip-mall-tsp-b.

## [1.3.1] - 2026-05-19

### Fixed
- **intl-dbgenset-changeover example**: Genset-mode Ik" precision corrected. Previous text conflated sustained Ik (3-5× In after AVR field forcing settles, ~5 s post-fault) with subtransient Ik" (within first cycle). Per IEC 60909-0:2016 §3.5.1 equivalent voltage source method, an 80 kVA, 400 V TPN, salient-pole synchronous genset with Xd" = 0.12 pu, E" = 1.05 pu yields subtransient Ik" ≈ 1.0 kA (peak ip ≈ 2.5 kA, κ ≈ 1.8). Sustained Ik ≈ 0.4 kA. The earlier "~3.5-4.5 kA" figure was sustained Ik mistakenly labelled as subtransient Ik".

### Unchanged
- No schema changes
- No new examples
- intent-out.json contracts unchanged (db-layout intent shape has no Ik"/PFC fields)
- SLD v1.5 INT example consuming this db-layout intent is unaffected (consumes intent shape, not prose)

### Why this patch
Per SLD v1.5 final code-review MEDIUM-2 deferred fix (commit 432050a-review). Deferred to v1.6 sprint per user direction 2026-05-19.

## [1.3.0] - 2026-05-19

### Added
- 4 new INT db-layout examples (pair with SLD v1.5 multi-sheet INT growth):
  - `intl-dbem-emergency-lighting` — EM lighting central battery per IEC 60364-5-56:2018 §560.7 + BS EN 50171:2001+A1:2022 + IEC 60598-2-22:2014+A2:2020. 8 circuits, 40A intake, NO upstream RCD (life-safety exemption)
  - `intl-dbcomms-data` — LV data/comms with Type B RCD per IEC 60364-5-53:2002+A2:2015 §531.3.3 + BS EN 50173:2018 EMC + IEEE 802.3bt-2018 PoE+. 7 circuits, 32A intake
  - `intl-dbups-backed` — 10 kVA online UPS critical loads per IEC 62040-1:2017 + IEEE 446-1995. 6 circuits, 50A intake, three-tier RCD strategy (Type B on IT / Type A on workstations / bypass RCD-free)
  - `intl-dbgenset-changeover` — ATS + 80 kVA standby genset per IEC 60364-5-56:2018 §552 + ISO 8528-12:1997 + NFPA 110-2022 + BS EN 50171:2001+A1:2022 §6.3. 5 circuits, 63A intake, utility-priority mode, dual-mode PFC (utility 9 kA + genset 4 kA)

### Changed
- Examples count: 16 → 20 (5 INT examples now: MSB + 8 sub-DBs total — 4 existing + 4 new)

### Why this sprint
Pairs with SLD v1.5 drawing-layout sprint. SLD INT example grows 5→9 boards to demonstrate multi-sheet split logic (life-safety isolation per BS 9999 §6.4 / IEC 60364-5-56:2018 §560 / NFPA 72 §10.6).

### Pattern parent
- db-layout v1.2 (shipped 2026-05-18) — `intl-dbfa1-fire-alarm` structural template reused for the 4 new examples

## [1.2.0] - 2026-05-18

### Added
- **12 new cascade-supporting examples** to enable full WI4 multi-board intent consumption in SLD v1.3.0:
  - UK: 4 new (MSB-rollup + 3 sub-DBs SDB-GF/L1/L2)
  - KE: 1 new (gate-house DB downstream of MSP-100 C08)
  - INT: 4 new (DB-L1 lighting + DB-P1 power + DB-M1 mechanical + DB-FA1 fire alarm; all downstream of existing intl-commercial-tpn-msb F01-F04)
  - US: 3 new (TSP-A + TSP-B tenant sub-panels + CA-P common area; all downstream of existing us-strip-mall-panelboard)

### Notes
- All new examples follow the 5-file pattern (input + output + intent-out + reasoning + sample-schedule) established in v1.1.
- intent-out.json strict schema validation enforced (additionalProperties: false; no wrapper fields).
- Downstream consumer: SLD v1.3.0 (paired sprint).

## [1.1.0] - 2026-05-18

### Added
- **NEW KE Nairobi industrial 100A TPN example** (`examples/ke-nairobi-industrial-100A-tpn/`) — 5 files: input.json, output.json, intent-out.json, reasoning.md, sample-schedule.md. 8 circuits matching the KE earthing example 1:1 for cross-skill consumption demonstration.
- **intent-out.json backfill for existing 3 examples** — uk-domestic-consumer-unit, intl-commercial-tpn-msb, us-strip-mall-panelboard. Brings all 4 db-layout examples to feature parity with arc-flash + arc-flash-labelling + earthing pattern.

### Notes
- intent-out.json schema field names differ from output.json IR field names (id vs circuit_id, breaker_rating_a vs ocpd.rating_a, etc.). The intent contract is at `electrical/db-layout/schemas/db-layout-intent.schema.json`.
- Downstream consumer: `electrical/earthing` v1.3 (paired sprint, shipped 2026-05-18).

## v1.0.0 (current — Stage 1: Schedule + Schematic + Selectivity)

First production-grade version. Stage 1 of a two-stage plan:
- **Stage 1 (this release):** DB schedule + DB face one-line schematic + cascade selectivity verification. Covers single-board IR + project-wide rollup intent across GB / EU/INT / US jurisdictions.
- **Stage 2 (planned):** Plan-view DB location drawing + DC distribution (PV, EV chargepoints).

### Features
- 13-step reasoning chain in `prompts/generator.md` that explicitly names 19 standards files to load (consumption-pattern proof)
- Jurisdiction-gated standards loading: BS 7671 (GB) / IEC 60364 (EU/INT) / NFPA 70 (US) + IEC 61439 + IEC 60617 always
- Single-board IR schema with `selectivity_results[]` and `tool_call_pending` flag per WI3 (live IEC 60909 cascade deferred to `fault-level` skill)
- TWO stable intent contracts:
  - `db-layout` (single-board) — for panel-schedule, riser, cable-containment
  - `db-layout-rollup` (project-wide) — for earthing (payload shape verified verbatim against earthing example expectations)
- Cross-drawing intent consumption: `fault-level` (when available) for live Ifault numbers; engineer-input fault currents accepted as fallback with `tool_call_pending`
- Rationale block per WI2 (9 mandatory sections)
- 8 evals covering all 6 WI5 categories + 2 skill-specific (selectivity_cascade, intent_rollup_shape)
- 3 worked examples (UK / INT / US) demonstrating jurisdiction switch + intent shape compatibility

### Standards consumed (explicit file paths — not folders)
- `shared/standards/electrical/IEC60617/symbol-index.json` (always)
- `shared/standards/electrical/IEC60617/part7-switchgear.json` (always)
- `shared/standards/electrical/IEC61439/form-separations.json` (always)
- `shared/standards/electrical/IEC61439/ip-ik-ratings.json` (always)
- `shared/standards/electrical/IEC61439/short-circuit-withstand.json` (always)
- `shared/standards/electrical/BS7671/reg433-overcurrent-protection.json` (GB)
- `shared/standards/electrical/BS7671/reg434-fault-current.json` (GB)
- `shared/standards/electrical/BS7671/reg443-spd.json` (GB)
- `shared/standards/electrical/BS7671/reg411-rcd-requirements.json` (GB)
- `shared/standards/electrical/BS7671/appendix3-device-curves.json` (GB)
- `shared/standards/electrical/BS7671/diversity-factors.json` (GB)
- `shared/standards/electrical/IEC60364/part4-43-overcurrent.json` (EU/INT)
- `shared/standards/electrical/IEC60364/part4-44-overvoltage.json` (EU/INT)
- `shared/standards/electrical/IEC60364/rcd-requirements.json` (EU/INT)
- `shared/standards/electrical/IEC60364/device-curves.json` (EU/INT)
- `shared/standards/electrical/IEC60364/diversity-factors.json` (EU/INT)
- `shared/standards/electrical/IEC60364/fault-current.json` (EU/INT)
- `shared/standards/electrical/NFPA70/art408-panelboards.json` (US)
- `shared/standards/electrical/NFPA70/art240-overcurrent.json` (US)
- `shared/standards/electrical/NFPA70/art220-load-calculations.json` (US)
- `shared/standards/electrical/NFPA70/ocpd-coordination.json` (US)

### Tool calls awaiting runtime (WI3)
- `calc.iec60909_cascade` — compute prospective fault current at each level. Status: tool_call_pending; deferred until dedicated `fault-level` skill ships.
- `calc.diversity_factor` — apply diversity factor from standard for main sizing. Status: tool_call_pending.

### Status
- `status: beta` — production-grade artefact set with two known runtime dependencies (selectivity tool, diversity tool). IR includes `tool_call_pending: true` markers where the deterministic calc has not yet been wired.
- Promotes to `production` when: 8/8 evals pass against a production model AND `fault-level` skill exists for live IEC 60909 cascade execution.
