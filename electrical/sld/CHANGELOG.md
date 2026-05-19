# Changelog — sld

## [1.5.0] - 2026-05-19

### Added
- **Drawing layout (spatial-intent layer)**: NEW optional top-level `drawing_layout` block on SLD IR with 3 enums + sheets[] + boards{}. Skills emit functional grouping + CAD layer enum + multi-sheet split judgment; runtime renderer (separate project) consumes intent + IR + symbol library → produces SVG/DXF/PDF. NO x/y coordinates in skill output.
- **3 jurisdiction CAD layer lookup tables** in `shared/standards/drafting/` (BS1192 for GB/KE-via-routing, AIA for US, ISO19650 for INT/EU)
- **Generator Step 13** — Author drawing_layout block (post-IR, hybrid multi-sheet split rule)
- **Validator INV-12 + INV-13 + INV-14** (drawing_layout shape + jurisdictional sheet size + split logic)
- **2 new evals**: eval-09 (drawing_layout schema conformance, 8 assertions), eval-10 (multi-sheet split logic, 6 assertions)
- **INT example grown 5 → 9 boards / 1 → 2 sheets** to demonstrate multi-sheet capability (added DB-EM + DB-COMMS + DB-UPS + DB-GENSET-XCV)

### Changed
- All 4 SLD examples now ship drawing_layout (3 single-sheet: UK + KE + US; 1 multi-sheet: INT)
- INT consumed_intents count: 7 → 11 (4 new db-layout entries for the new sub-DBs)
- INT distribution_hierarchy: 5 → 9 boards; selectivity_cascade: 4 → 8 entries

### Cross-skill invariants preserved
- INV-11 (v1.4) still holds for all 4 examples — system_type cross-skill equality + peak_pfc_ka within ±0.5 kA tolerance unchanged

### Multi-sheet split rule (hybrid)
- ≤8 boards single-sheet UNLESS fire_alarm_life_safety + general_power coexist
- Life-safety coexistence forces split per BS 9999 §6.4 / IEC 60364-5-56:2018 §560 / NFPA 72 §10.6

### Backward compatibility
- v1.3 / v1.4 examples remain valid (drawing_layout is OPTIONAL in schema)

### Pattern parents
- SLD v1.4 (shipped 2026-05-18) — multi-skill consumption + INV-11
- arc-flash-labelling (shipped 2026-05-17) — jurisdiction-aware lookup tables in shared/standards/
- db-layout v1.2 — intl-dbfa1-fire-alarm structural template reused for 4 new INT sub-DBs (paired v1.3 sprint)
- [[runtime-project-boundary]] memory — drawing_layout = intent (skill), not geometry (runtime)

## [1.4.0] - 2026-05-18

### Added
- **Multi-skill intent consumption**: SLD now consumes earthing + fault-level intents in addition to db-layout (one per board). `consumes_intents`: `["db-layout"]` → `["db-layout", "earthing", "fault-level"]`
- **Generator Step 0.5 extended** with sections A/B/C/D/E for multi-skill resolution + cross-skill assumption population
- **Validator INV-11**: 5 hard fails (count, exactly-one-earthing, exactly-one-fault-level, paths resolve) + 2 warning flags (system_type equality, peak_pfc_ka ±0.5 kA tolerance)
- **New eval**: `eval-08-multi-skill-intent-consumption.yaml` (12 assertions covering structural shape + cross-file equality)

### Changed
- All 4 worked examples (UK 4-board + KE 2-board + INT 5-board + US 4-board) refreshed: `meta.consumed_intents[]` grows from N → N+2 entries (4→6, 2→4, 5→7, 4→6)
- `system_metrics.peak_pfc_ka` now sourced from fault-level intent's transformer-secondary `ifault_ka_max` (was LLM-estimated in v1.3)
- `input.json` per example gains 2 new top-level fields: `earthing_intent_path` + `fault_level_intent_path`

### Engineering consequences surfaced by multi-skill consumption
- KE example: deterministic PFC 10.22 kA exceeds MSP-100 Icu 10 kA → new non_compliance_flag with two resolution paths (uprate to 16 kA Icu OR document KPLC transformer-fuse cascade)
- INT example: dual-source (utility + 800 kVA standby genset) — bespoke genset-filtering note documented; SLD models utility-source worst case only

### Backward compatibility
- v1.3 examples remain valid (INV-11 only fires when both new input paths are declared)
- `tool_call_pending_for_system_metrics: true` preserved (only peak_pfc_ka refined; imax, SPD, life-safety isolation remain LLM-estimated until calc.sld_system_metrics ships)

### Pattern parents
- earthing v1.3 (shipped 2026-05-18) — single-board WI4 single-skill consumption
- SLD v1.3 (shipped 2026-05-18) — multi-board WI4 single-skill consumption
- This sprint: multi-board + multi-skill WI4 consumption

## [1.3.0] - 2026-05-18

### Added
- **Full rebuild to artefact pattern.** Manifest grows from sparse legacy form to full v1.3 structure: produces_intent + consumes_intents + 3 prompts + 4 rules + 3 constraints + 3 validators + 2 ontology + 7 evals + 4 examples + 6 standards layers.
- **IR schema** (`sld-ir.schema.json`) — first-time SLD has a formal IR schema. Required fields: distribution_hierarchy (flat list with parent_board_id pointers), selectivity_cascade, system_metrics, supply_origin, jurisdiction (enum GB/EU/INT/KE/US), meta.consumed_intents.
- **Intent schema** (`sld-intent.schema.json`) — slim downstream-consumable subset; strict additionalProperties:false; pinned intent_type const "sld".
- **12-step generator prompt** (~535 lines) replacing legacy 1245-line monolith. Mirrors arc-flash + cable-sizing + fault-level + earthing pattern. Includes Step 0.5 multi-board WI4 consumption.
- **Validator prompt** with 10 INV checks; **reviewer prompt** with 6 D-checks.
- **17 deterministic checks** across 4 rules + 3 constraints + 3 validation YAMLs.
- **4 worked examples**: UK 3-storey office (4-board cascade) + KE Nairobi industrial MSB-GH (2-board, KS 1700 jurisdiction) + INT commercial MSB + 4 sub-DBs (5-board, fire-alarm life-safety) + US strip mall MSP + tenants (4-board, NEC + AWG).
- **7 evals**: 5 WI5 categories (happy_path × 2, validation_trap × 2, edge_case) + 2 skill-specific (rationale_block + multi-board WI4 consumption).
- **2 ontology JSONs**: board-roles (7 roles) + distribution-types (5 topologies).
- **3 docs**: engineering-philosophy.md + known-limitations.md + legacy-generator-v1.2-engineering-reference.md (archived 1245-line legacy generator).

### Changed
- **Legacy 1245-line generator archived** at `electrical/sld/docs/legacy-generator-v1.2-engineering-reference.md`. Engineering content preserved as reference; replaced by 12-step generator at `prompts/generator.md`.
- **inputs.json refreshed** per WI1 — discovery questions include consumed_intent_path per board.
- **README.md fully rewritten** (was stub-flagged).
- **db-layout dependency** — consumes_intents now actively populated (was declared but unused in legacy v1.2).
- **Status:** production → beta during rebuild; can promote back to production after eval runs in DraftsMan runtime.

### Removed
- `electrical/sld/evals/evals-combined.md` (atomized into 7 per-eval YAMLs)
- `electrical/sld/examples/examples-combined.md` (atomized into 4 example folders)

### Notes
- **Paired with db-layout v1.2.0** which adds 12 new companion examples (60 files) supporting full cascade WI4 consumption.
- **WI3 tool deferral** for system_metrics: `calc.sld_system_metrics` not yet runtime-shipped; system_metrics values are LLM-estimates with disclaimer in flags.
- **No schema changes to db-layout** — db-layout intent shape unchanged.
- **Future v1.4.0** will add earthing + fault-level intent consumption (memory queue: sld-deferred-followups).
- **Future v1.5.0** will add drawing position layout (Stage 2).
- **US example** carries deliberate NEC 695.4(A) teaching flag (fire pump on common-area panel) — `compliant: false` at IR level demonstrates how SLD records multi-board compliance tensions.

## v1.2.0 (current)
- Add `inputs.json` carrying full discovery taxonomy (18 items including supply source, earthing, PSCC, transformer/generator/UPS, distribution-board struct_list, Form/IAC, SPD strategy)
- Add `inputs_path: "inputs.json"` to manifest pointing at the new taxonomy
- Bare-string `inputs: [...]` array retained for back-compat; will be removed in v2.0.0
- Conforms to new `shared/schemas/core/inputs.schema.json` metaschema (upstream Work Item 1)

## v1.1.0
- Zs disconnection time check (Tables 41.2/41.3)
- Protection coordination and selectivity
- Life safety circuits (FP200/FP400, essential bus)
- Cable type selection (LSZH, fire-rated)
- Neutral oversizing for harmonic loads
- Motor load starting current
- Switchgear Form of separation (BS EN 61439-1)
- ACB electronic trip unit settings
- SPD risk assessment (Reg 443.4)
- Part L sub-metering obligations
- G99/G98 regulatory submissions

## v1.0.0
- Initial production release
