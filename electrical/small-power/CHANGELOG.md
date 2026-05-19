# Changelog

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
