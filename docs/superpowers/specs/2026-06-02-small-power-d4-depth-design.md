# small-power v2.0.0 D4 Depth — Design Spec (Wave 2 First Deliverable)

**Date:** 2026-06-02
**Spec author:** brainstorm session via `superpowers:brainstorming`
**Cluster context:** Wave 2 first deliverable. Closes the within-skill-depth program for small-power that was pushed from D3 to D4 by `[[sprint-D3-shipped]]` (lighting-layout depth shipped in original D3 slot).
**Predecessor:** [2026-06-01-special-locations-design.md](2026-06-01-special-locations-design.md) (Wave 1 second deliverable; cascade-wired special-locations into small-power v1.2.0 + 1 Part-7 example).
**Target skill path:** `electrical/small-power/`
**Target version:** v1.2.0 → **v2.0.0 production**.

---

## 1. Identity & architecture

D4 is the **within-skill-depth sprint** that closes the small-power depth roadmap from `[[within-skill-depth-plan]]`. Special-locations sprint cascade-wired small-power's INV-12 but did NOT add D4 engineering content. D4 adds 5 depth items: `building_diversity` IR field, 4 new Part-7 worked examples, comprehensive ring/radial topology depth, EV-charge demand coordination with Type A/B RCD rule, and cascade integration verification.

| Attribute | Value |
|---|---|
| Path | `electrical/small-power/` |
| Version | 1.2.0 → **2.0.0** (major bump — see §3.1) |
| Status | beta → **production** (D4 closes within-skill-depth program; small-power is architecturally complete) |
| Discipline | Electrical |
| Sprint shape | 4 phases × **25 implementer tasks** (smaller than special-locations 26 commits) |
| INV catalogue | 12 → **19** (7 new INVs: INV-13..INV-19) |
| Eval catalogue | 5 → **10** (5 new YAMLs covering INV-13/14/15/16/17/18/19) |
| Example catalogue | 6 → **15** (8 NEW + 1 RETROFIT) |
| Producer-side cascade fixtures added to special-locations | 2 (`cascade-small-power-uk-ev-charge-domestic` + `cascade-small-power-uk-sauna-heater-exemption`) |

**Why this sprint:**
- Closes `[[within-skill-depth-plan]]` original D3/D4 small-power depth (items 8 + 9: special-locations examples + area-level diversity)
- Adds 3 more items (topology comprehensive + EV depth + cable-sizing cascade integration) per this brainstorm
- Ships small-power as a fully-realised **v2.0 production skill**
- Validates the special-locations cascade end-to-end through 4 new consumer-side Part-7 examples

**Standards stack:**
- BS 7671:2018+A2:2022 (electrical primary; §433/§522/§526/§701/§702/§703/§710/§722)
- IET On-Site Guide 8th Edition Appendix A (diversity) + Appendix H (ring final / radial topology)
- IET Code of Practice for EV Charging Equipment Installation **4th Edition** (NOT 3rd Edition — citation hygiene catch at brainstorm)
- IET Guidance Note 1 Section 4 (blocks / commercial diversity)
- BS EN 61851-1 (EV charging equipment) + BS EN 62196 (EV plug/socket Type 2 Mennekes / CCS Combo 2)
- HTM 06-01 (NHS healthcare medical IT system)
- KS 1700:2018 §313 (Kenya jurisdiction route to BS 7671)

---

## 2. Scope (locked)

### v2.0 included scope items (5)

| # | Item | Key citation | Source decision |
|---|---|---|---|
| 1 | `building_diversity` IR field — office/industrial/healthcare profiles mirroring `diversity-factors.json` | IET OSG App A — Table A1 + IET Guidance Note 1 §4 | Brainstorm Q on richness, locked at "Mirror standards" |
| 2 | 4 new Part-7 worked examples: pool (§702) + medical Group 2 (§710 IT) + EV (§722) + sauna (§703) | Part-7 verified citations | Brainstorm Q on Part-7 count, locked at "Hybrid + 4" |
| 3 | Topology comprehensive: ring continuity (IET OSG §8.4.4 + §526 top-level) + floor-area cross-check + OCPD-topology coordination + AMD 2 FCU spur modelling | IET OSG §8.4.4 (8th Edition) + BS 7671 §433 top-level + §526 top-level + AMD 2 corrigenda | Brainstorm Q on topology depth, locked at "Comprehensive". Plan-writing stage caught that BS 7671 sub-clauses §526.2 and §433.2 are NOT transcribed in the verified standards file — anchor citation is IET OSG §8.4.4 (which IS verified and already used by 4 existing TOP-NN rules). |
| 4 | EV demand + RCD Type A/B selection per Reg 722.531.3.101 | Reg 722.531.3.101 + IET CoP for EV (4th Ed) | Brainstorm Q on EV depth, locked at "Demand + RCD" |
| 5 | INV verifying cable_sizing intent feeds into building-level diversity calc | Skill-internal cross-skill integration | Brainstorm Q on cable-sizing cascade, locked at "Full integration INV" |

### Scope corrections from `[[within-skill-depth-plan]]` (auditable)

The original D3/D4 small-power-depth roadmap entry listed 2 items (8 + 9). This brainstorm expanded scope to 5 items + applied citation-hygiene corrections caught at brainstorm:

| Original plan | Reality | Resolution |
|---|---|---|
| Item 8: "EV charging (§722 Type B RCD + OZEV)" | §722 RCD is Type A default + Type B conditional (per Reg 722.531.3.101 verified file). OZEV CoP was caught as a misname in D2.3 — actual name is **IET CoP for EV Charging Equipment Installation (4th Ed)** | Item 4 uses correct Reg 722.531.3.101 + IET CoP 4th Ed citations. No-diversity per CoP. |
| Item 9: "building_diversity floor_factor (office 0.75 / retail 0.85 / industrial 0.90)" | The floor_factor values in original plan NOT in verified file. Standards file has richer office/industrial/healthcare profiles with density + expansion + applies_load_types | Item 1 mirrors verified standards file (3 profiles only). Retail / residential / data-center / hospitality deferred to v2.1 once standards-file entries land. |
| Brainstorm args: "PVC/SWA tables 4D1A + 4D5A" | Cable-sizing D2.1 (May 2026) already shipped these in `appendix4-table-4D1A-pvc-twin-earth.json` + `appendix4-table-4D5A-pvc-swa.json`. Small-power CONSUMES cable-sizing, not duplicates. | Dropped from D4 scope. cable-sizing handles the cable rating; small-power handles the socket/circuit layer above. |
| Brainstorm args: "Cable derating per §433 + §523 (Ca/Cg/Ci grouping)" | Cable-sizing already enforces Ib ≤ In ≤ Iz per Reg 433 + correction factors per Appendix 4. | Dropped from D4 scope. |
| Brainstorm args: "IET CoP for EV 3rd edition" | Verified file says **4th Edition** | Spec uses 4th Ed throughout. |

### Verified citation table (v2.0 — every clause the skill will cite)

Cross-checked against verified standards files (`verification_status: verified-against-source`). **No other sub-clause citations beyond this list are valid** — fall back to top-level section + named cross-reference for any unverified path.

| Citation | Verified in file | Used for |
|---|---|---|
| `BS 7671:2018+A2:2022 §433.1.1` | `reg433-overcurrent-protection.json` | Ib ≤ In ≤ Iz fundamental rule (referenced by INV-16; cable-sizing enforces) |
| `IET On-Site Guide §8.4.4 (8th Edition)` | `electrical/small-power/rules/topology-rules.yaml` (4 existing TOP-NN rules already cite it) | **Anchor citation for ring/radial topology** — covers INV-14 ring continuity + INV-17 FCU spur modelling (AMD 2). Brainstorm caught BS 7671 sub-clauses §526.2 + §433.2 are NOT transcribed in verified file; IET OSG §8.4.4 IS verified and is the proper anchor. |
| `BS 7671:2018+A2:2022 §526` (top-level only) | (general connections section) | Top-level cross-reference for connection requirements; sub-clauses NOT verified |
| `BS 7671:2018+A2:2022 §701.411.3.3` | `part7-special-locations.json` | Bathroom 30 mA RCD (cascade from special-locations) |
| `BS 7671:2018+A2:2022 §702.415.1` | `part7-special-locations.json` | Pool main equipotential bonding (cascade demonstrated in example #1) |
| `BS 7671:2018+A2:2022 §702.415.2` | `part7-special-locations.json` | Pool supplementary bonding |
| `BS 7671:2018+A2:2022 §703.411.3.3` | `part7-special-locations.json` | Sauna RCD-with-heater-exemption (example #4 + cascade) |
| `BS 7671:2018+A2:2022 §710` (top-level) | `part7-special-locations.json` | Medical IT system + supplementary bonding (cascade demonstrated in example #2) |
| `BS 7671:2018+A2:2022 §722.411.4.1` | `part7-special-locations.json` | Open-PEN protection (OUT of D4 scope; for reference only) |
| `BS 7671:2018+A2:2022 §722.531.3.101` | `part7-special-locations.json` | EV RCD Type A default; Type B if charging unit lacks 6mA DC detection (INV-18) |
| `IET On-Site Guide 8th Edition Appendix A — Table A1` | `diversity-factors.json` | Per-load diversity + office_lift_single/two/three_or_more lift diversity table (DIV-05) |
| `IET On-Site Guide 8th Edition §8.4.4` | (standards-file cross-reference) | Ring final circuit rules (TOP-06..09) |
| `IET Code of Practice for EV Charging Equipment Installation (4th Ed)` | `diversity-factors.json` `_reference` field | EV no-diversity rule (EV-02) |
| `IET Guidance Note 1 §4` | `diversity-factors.json` `_reference` field | Blocks / commercial diversity context |
| `BS EN 61851-1` | `part7-special-locations.json` | EV charging unit standard |
| `BS EN 62196` | `part7-special-locations.json` | EV plug/socket Type 2 Mennekes / CCS Combo 2 |
| `HTM 06-01` | `diversity-factors.json` `_reference` field | NHS healthcare site precedence |
| `KS 1700:2018 §313` | `diversity-factors.json` (DIV-03 referenced) | KE jurisdiction route to BS 7671 |

**Banned citations (would fail INV / fix-pass):** none specific to D4 — D4 inherits the 14-banned-clause list from `[[2026-06-01-special-locations-design.md]]` §3.2 (banned sub-clauses §701.32, §701.55, §702.55.1, §702.55.2, §702.32, §703.55, §703.512, §703.413, §710.413.1.5, §710.314, §710.411.3.3, §715.560.4, §715.521, §715.422). Plus per the citation hygiene catches above: **"OZEV CoP"** name and **"3rd Edition"** EV CoP version are banned (correct names are IET CoP for EV Charging Equipment Installation, 4th Ed).

### v2.1 deferrals (declared, not built)

| Item | Trigger to build |
|---|---|
| `building_diversity` retail / residential / data-center / hospitality profiles | When standards-file entries land for these building types |
| §722.411.4.1 open-PEN protection (4-option enum) — OUT of D4 EV scope per item 4 lock | Dedicated EV-Charge skill ships; earthing skill v1.x adds open-PEN rules |
| Mode 3 / Mode 4 cable-sizing routing | Dedicated EV-Charge skill |
| Per-circuit cable derating (Ca/Cg/Ci grouping factors) | Cable-sizing already handles; no duplication in small-power |

---

## 3. Architecture decisions (locked at brainstorm)

| Decision | Choice | Rationale |
|---|---|---|
| Sprint scope | 5 focused items (no PVC/SWA / no cable derating duplication) | Avoid duplicating cable-sizing's domain |
| building_diversity richness | Mirror verified standards file (office/industrial/healthcare) | No invented values; v2.1 extends |
| Part-7 example count | 4 (pool + medical IT + EV + sauna) | Hybrid Q answer; covers 4 distinct Part-7 sections |
| Topology depth | Comprehensive (continuity + floor-area + OCPD-topology + AMD 2 FCU) | Most thorough; 4 new INVs |
| EV depth | Demand + RCD Type A/B (NOT open-PEN, NOT Mode 3/4) | Belongs in small-power's domain; dedicated EV-Charge skill handles the rest |
| Cable-sizing cascade | Full INV-19 verifying cable_sizing.payload feeds building_diversity calc | Most integrative |
| Version bump | 1.2.0 → 2.0.0 (additive changes; bump-as-signaling not bump-as-breakage) | Mark "small-power architecturally complete" |
| Status promotion | beta → production | D4 closes the depth program for small-power |

### 3.1 Why a 2.0 (not 1.3) major bump

Strictly by semver, D4's changes are additive (new optional `building_diversity` IR field + 7 new INVs with `additionalProperties: false` discipline maintained). Existing 6 examples will still validate. Cable-sizing's `consumes_intents.version_constraint` is `^1.0` (cable-sizing consumes small-power... actually wait — small-power consumes cable-sizing, so cable-sizing's `consumes_intents` does NOT reference small-power).

**Pre-merge check at writing-plans stage:** grep all `electrical/*/skill.manifest.json` files for any `consumes_intents.skill_id: "small-power"` entry with `version_constraint: "^1.x"` — if any exists, that consumer's version_constraint needs updating to `>=1.0` (or `^1 || ^2`) before D4 ships. Confirm zero consumer-side breakage before the version bump lands.

The bump is **signaling**: small-power has closed within-skill-depth program and is now production-ready architecturally complete. The "1.x → 2.x" boundary makes that visible in the version vector + the manifest `status: production` field.

---

## 4. Input model additions

### 4.1 `inputs.json` additions (3 new items, all optional)

| Item id | Type | Required | Purpose |
|---|---|---|---|
| `building_diversity_inputs` | object | optional | Engineer-supplied building taxonomy: `{building_type, floor_count, design_density_w_per_m2_override?, future_expansion_pct_override?}`. Defaults to verified standards-file values when overrides absent. |
| `ring_continuity_endpoints` | array | optional | Per-ring `{circuit_id, endpoint_a_xy, endpoint_b_xy, mcb_way_id}` for ring continuity verification per IET OSG §8.4.4 (INV-14) |
| `ev_charge_metadata` | array | optional | Per-EV-circuit `{circuit_id, rcd_type, charging_unit_dc_detection_a, mode (3 or 4), charging_unit_standard}` for INV-18 |

All 3 are optional. When absent, the validator emits `"INV-N skipped — input not supplied (engineer must verify manually)"` and the INV passes vacuously. Engineer-of-record bears responsibility per CLAUDE.md honest-disclosure discipline.

---

## 5. IR additions

### 5.1 New top-level field `building_diversity` (optional)

```yaml
building_diversity:
  building_type: enum(office | industrial | healthcare)              # v2.0 limited to verified standards file
  floor_count: int
  design_density_w_per_m2: number                                    # must be within standards range or flagged
  future_expansion_pct: number                                       # defaults to standards-file value
  applies_after: const "per_load_diversity"
  applies_load_types: [string]                                       # filtered to standards-file enum per building_type
  building_diversified_demand_a: number                              # computed output
  per_circuit_demand_inputs:                                         # closes INV-19 cascade integration
    - {circuit_id, post_per_load_diversity_a, building_factor_applied}
  _clause_citation: "IET On-Site Guide 8th Edition Appendix A — Table A1 + diversity-factors.json"
  _derivation_note: string (minLength: 40, maxLength: 800)
```

### 5.2 Per-circuit additions (conditional on topology/load_type)

**`circuits[].ring_endpoints`** (required when `circuits[].topology == "ring"`):

```yaml
ring_endpoints:
  endpoint_a_xy: {x_mm, y_mm}
  endpoint_b_xy: {x_mm, y_mm}
  mcb_way_id: string
  continuity_verified: boolean
  _citation: "IET On-Site Guide §8.4.4 (8th Edition) + BS 7671:2018+A2:2022 §526 (top-level)"
```

**`circuits[].fcu_spurs[]`** (optional; for AMD 2 modelling):

```yaml
fcu_spurs[]:
  - location_xy: {x_mm, y_mm}
    fcu_rating_a: enum(3 | 5 | 13)
    downstream_loads_w: number
    _citation: "IET On-Site Guide §8.4.4 (8th Edition, AMD 2 update) + BS 7671:2018+A2:2022 §433 (top-level)"
```

**`circuits[].ev_charge_metadata`** (required when `circuits[].load_type` matches `ev_charge_*`):

```yaml
ev_charge_metadata:
  rcd_type: enum(type_a | type_b)
  charging_unit_dc_detection_a: number                               # 0 or 6 typical
  mode: enum(3 | 4)
  charging_unit_standard: const "BS EN 61851-1"
  socket_standard: enum("BS EN 62196 Type 2 Mennekes" | "BS EN 62196 CCS Combo 2")
  dedicated_circuit: const true
  _citation: "BS 7671:2018+A2:2022 §722.531.3.101 + IET CoP for EV (4th Ed)"
```

### 5.3 7 new INV ids appended to `invariants[]`

| ID | Severity | Rule | Citation |
|---|---|---|---|
| INV-13 | HIGH | `building_diversity` self-consistency (density within standards range; floor_count × per_circuit_demand × building_factor matches building_diversified_demand_a; applies_load_types filtered to building_type) | IET OSG App A |
| INV-14 | HIGH | Ring continuity: when topology=ring, both endpoints MUST land at same `mcb_way_id`; `continuity_verified == true` | IET OSG §8.4.4 + BS 7671 §526 (top-level) |
| INV-15 | HIGH | Per-circuit floor-area cross-check: `circuit.floor_area_m2` = Σ(rooms_covered[].floor_area_m2) | BS 7671 §433 + IET OSG §8.4.4 |
| INV-16 | HIGH | OCPD-topology coordination: ring → MCB ≤32A; 2.5mm² radial → ≤20A; 4mm² radial → ≤32A | BS 7671 §433.1.1 + IET OSG §8.4.4 |
| INV-17 | MEDIUM | AMD 2 FCU spur modelling: every fcu_spurs[] entry has fcu_rating_a in {3,5,13} + downstream_loads ≤ (fcu_rating × 230V) | IET OSG §8.4.4 + BS 7671 §433 (top-level) |
| INV-18 | HIGH | EV RCD Type selection: `rcd_type=type_a` when `charging_unit_dc_detection_a ≥ 6`; `rcd_type=type_b` otherwise | Reg 722.531.3.101 |
| INV-19 | MEDIUM | Cable-sizing cascade ↔ building_diversity integration: every circuit in `building_diversity.per_circuit_demand_inputs[]` has a matching entry in consumed `cable_sizing.payload.circuits[]`; demand values reconcile within 5% tolerance | Skill-internal cross-skill integration |

**Total INVs after D4: 19** (existing 12 + 7 new). Heavier on HIGH than MEDIUM (5 HIGH + 2 MEDIUM in new additions); matches small-power's existing high-safety-criticality posture.

### 5.4 IR schema validation discipline

- `additionalProperties: false` maintained at every object level
- `invariants[].evidence.maxLength: 1200` already in place from special-locations sprint
- New conditional `allOf` clauses:
  - When `circuits[].topology == "ring"` → `ring_endpoints` required
  - When `circuits[].load_type matches "ev_charge_*"` → `ev_charge_metadata` required
  - When `building_diversity.building_type == "healthcare"` → `applies_load_types` MUST include `healthcare_clinical_equipment` (per HTM 06-01)

---

## 6. Cascade contract (D4 EXERCISES; does not change wiring)

D4 does NOT change cascade wiring. Special-locations D.3 already wired:
- `electrical/small-power/skill.manifest.json` `consumes_intents[]` (cable-sizing + special-locations)
- `shared/schemas/electrical/small-power-ir.schema.json` `consumed_intents` block + Part-7 trigger allOf clause
- `electrical/small-power/prompts/validator.md` INV-12 (special-locations cascade)

D4 EXERCISES the cascade through 4 new Part-7 consumer examples. Cascade payload re-use pattern from special-locations D.4:

| New D4 consumer example | Consumes producer-side cascade |
|---|---|
| `uk-pool-hall-sockets-and-isolation` | `electrical/special-locations/examples/cascade-lighting-layout-uk-pool-hall/intent-out.json` (anchor-driven engineering equivalence; honest disclosure documented) |
| `uk-medical-group-2-isolation-sockets` | `electrical/special-locations/examples/cascade-small-power-uk-medical-group-2-isolation/intent-out.json` (real small-power-specific producer fixture from C.2; closes integrity loop) |
| `uk-ev-charge-domestic` | NEW producer-side fixture in `electrical/special-locations/examples/cascade-small-power-uk-ev-charge-domestic/` (4 files added in D.1 of D4 sprint) |
| `uk-sauna-with-heater-exemption` | NEW producer-side fixture in `electrical/special-locations/examples/cascade-small-power-uk-sauna-heater-exemption/` (4 files added in D.1 of D4 sprint) |

---

## 7. Reviewer D-checks (3 new)

D4 adds 3 new reviewer D-checks beyond the existing reviewer.md catalogue:

**D-8 — `building_diversity` density outside-band warning** | when `design_density_w_per_m2` is supplied but sits outside the standards-file `[low, high]` range, flag for engineer verification (not a hard fail because the engineer may have project-specific data; honest disclosure required).

**D-9 — EV Type A vs Type B borderline** | when `charging_unit_dc_detection_a == 6` exactly (right on the threshold), flag for engineer confirmation that the manufacturer datasheet actually meets the 6 mA threshold under test (vs theoretical spec).

**D-10 — Ring vs radial topology choice on edge floor area** | when `circuit.floor_area_m2` is in the range [95, 100] m² (right at the IET OSG §8.4.4 ring 100 m² ceiling), flag for engineer to confirm topology choice — ring is technically permitted up to 100 m² but radial gives more headroom for future spur additions.

Total D-checks after D4: existing 7 + 3 new = **10 D-checks**.

---

## 8. Examples taxonomy (9 example dirs total)

### 8.1 8 NEW + 1 RETROFIT

| # | Example name | Type | Purpose |
|---|---|---|---|
| 1 | `uk-pool-hall-sockets-and-isolation` | NEW | INV-12 PASS; §702.415.1 pool main bonding cascade + 30 mA RCD per §702.415.2 |
| 2 | `uk-medical-group-2-isolation-sockets` | NEW | INV-12 PASS; medical IT panel cascade + supplementary bonding terminal |
| 3 | `uk-ev-charge-domestic` | NEW | INV-12 PASS + INV-18 PASS; Reg 722 dedicated circuit + Type A RCD with 6 mA DC detection + no-diversity per IET CoP 4th Ed |
| 4 | `uk-sauna-with-heater-exemption` | NEW | INV-12 PASS; §703.411.3.3 RCD-blanket-with-heater-exemption + sauna 3-zone fixture cross-check |
| 5 | `uk-office-floor-with-building-diversity` | NEW | INV-13 PASS; office profile + floor_count 5 + 75 W/m² density + 25% expansion |
| 6 | `uk-industrial-warehouse-with-building-diversity` | NEW | INV-13 PASS; industrial profile + lower density + higher diversity factor |
| 7 | `intl-open-plan-floor` | RETROFIT | Add office building_diversity profile to existing example; demonstrates retrofit pattern + INT jurisdiction routing |
| 8 | `uk-3bed-with-ring-continuity` | NEW | INV-14 PASS + INV-17 PASS (AMD 2 FCU spur modelling) |
| 9 | `uk-3bed-with-ring-continuity-VIOLATION` | NEW (FAIL HIGH demo) | Ring endpoints land at different MCB ways → INV-14 FAIL HIGH + INV-16 OCPD-topology mismatch |

### 8.2 Plus 2 producer-side cascade fixtures added to special-locations

| # | Special-locations cascade dir | Purpose |
|---|---|---|
| 10 | `cascade-small-power-uk-ev-charge-domestic` (4 files) | Producer-side cascade source for D4 example #3 |
| 11 | `cascade-small-power-uk-sauna-heater-exemption` (4 files) | Producer-side cascade source for D4 example #4 |

**Total new example-related files:** 9 × 4 + 2 × 4 = **44 files** added in D4 sprint.

### 8.3 Failure-mode + jurisdiction coverage

- **2 failure-mode demonstrations** — #9 ring continuity violation (INV-14 + INV-16 FAIL HIGH) + reuse of existing FAIL fixtures via cascade
- **Jurisdiction coverage** — GB primary (8 examples) + INT (#7 retrofit, INT jurisdiction routing); KE deferred to v2.1 per breadth-first build strategy

---

## 9. Evals (5 new YAMLs)

| File | Category | INVs covered | Checks |
|---|---|---|---|
| `eval-09-building-diversity-self-consistency.yaml` | `skill_specific` | INV-13 | 3 (building_type in enum; density within range; computed demand matches output) |
| `eval-10-ring-continuity.yaml` | `skill_specific` | INV-14 + INV-15 | 3 (both endpoints same mcb_way; floor_area cross-check; continuity_verified=true) |
| `eval-11-topology-ocpd-coordination.yaml` | `validation_trap` | INV-16 + INV-17 | 3 (ring→≤32A MCB; 2.5mm² radial→≤20A; FCU spur fcu_rating_a in {3,5,13}) |
| `eval-12-ev-rcd-type-selection.yaml` | `validation_trap` | INV-18 | 2 (type_a when dc_detection ≥6; type_b otherwise; standard_ref Reg 722.531.3.101) |
| `eval-13-cable-sizing-cascade-integration.yaml` | `cross_validation` | INV-19 | 2 (every circuit in building_diversity has matching cable_sizing payload entry; demand reconciles within 5%) |

**Categories from canonical 9-value enum** per CLAUDE.md. Severity mapping: HIGH→critical, MEDIUM→warning.

**Eval coverage post-D4:** 10 evals covering 10 of 19 INVs. Uncovered INVs (INV-01..INV-12 + 1 of the new 7) are the existing-INV-not-yet-covered set from earlier sprints. Per CLAUDE.md ≥5 minimum, coverage is well above floor.

---

## 10. Sprint shape — 4 phases × 25 implementer tasks

### Phase A — Foundations (5 tasks)
- **A.1** IR schema additions: `building_diversity` top-level field + `circuits[].ring_endpoints` + `circuits[].fcu_spurs[]` + `circuits[].ev_charge_metadata` + 7 new INV ids + `additionalProperties: false` discipline + 3 new allOf clauses + version bump 1.2.0 → 2.0.0 — **Sonnet**
- **A.2** inputs.json additions (3 new optional items) — **Sonnet**
- **A.3** rules YAML: NEW `building-diversity-rules.yaml` (3 profiles) + NEW `ev-charge-rules.yaml` (EV-01..EV-04) — **Sonnet**
- **A.4** rules YAML extensions: `topology-rules.yaml` adds TOP-06..09 + `diversity-rules.yaml` adds DIV-05 lift table — **Sonnet**
- **A.5** manifest bump 1.2.0 → 2.0.0 + status beta → production + README v2 update + `_v2_breaking_change_note` (explains bump-as-signaling) — **Sonnet**

### Phase B — Prompts (4 tasks, all Opus)
- **B.1** generator.md adds Step 13 (resolve building_diversity from inputs/standards) + Step 14 (verify ring endpoints) + Step 15 (emit fcu_spurs + ev_charge_metadata when applicable) — **Opus**
- **B.2** validator.md adds INV-13..INV-19 (7 new INV sections per canonical template) — **Opus**
- **B.3** reviewer.md adds D-8/D-9/D-10 — **Opus**
- **B.4** Cascade-prereq context updates for the 2 NEW producer-side cascade fixtures (cross-skill cascade discipline) — **Opus**

### Phase C — Examples + evals (10 tasks)
- **C.1–C.4** 4 Part-7 examples (pool / medical IT / EV / sauna) — **Opus**
- **C.5–C.6** 2 building_diversity examples (office + industrial) — **Opus**
- **C.7** Retrofit `intl-open-plan-floor` for building_diversity + honest disclosure — **Opus**
- **C.8–C.9** 2 ring continuity examples (PASS + FAIL HIGH demo) — **Opus**
- **C.10** 5 new evals YAML (eval-09..eval-13) — **Sonnet**

### Phase D — Ship (6 tasks)
- **D.1** 2 new producer-side cascade fixtures in special-locations/examples/ (4 files each) — **Opus**
- **D.2** Honest disclosure sweep (engineer-of-record substitutes, synthetic fixture warnings, no-banned-citation grep) — **Sonnet**
- **D.3** Sonnet 11-check verification fence (per special-locations D.6 pattern)
- **D.4** CHANGELOG (v2.0.0 entry) + memory file + MEMORY.md index entry — **Sonnet**
- **D.5** Final cross-sprint Opus integration review
- **D.6** Push deferred to user authorisation

**Total: 25 implementer tasks** = 5 (A) + 4 (B) + 10 (C) + 6 (D). Plus ~5-7 fix-pass commits expected per `[[sprint-D3-shipped]]` history. Estimated **~30-32 commits total** for the sprint.

### Sprint discipline (locked, mirrors special-locations)

- Sonnet for mechanical (scaffolding, schemas, manifests, eval YAML, cascade wiring) per `[[feedback-no-haiku-sonnet-opus-only]]`
- Opus for judgment (generator/validator/reviewer prompts, all examples, retrofits, all reviews)
- Two-stage Opus review after every implementer task — fix-pass commit when HIGH/CRITICAL findings surface
- Per-task two-stage Opus review + fix-pass commits
- Cross-check plan-template citations against `shared/standards/electrical/BS7671/` BEFORE implementer copies them (already applied at brainstorm in §2 verified citation table)
- Pre-ship Sonnet 11-check verification fence
- Final cross-sprint Opus integration review before push
- Push deferred to user authorisation per CLAUDE.md "shared state" rule
- `[[feedback-no-trim-non-consequential]]` discipline maintained (evidence maxLength 1200 already in place from special-locations sprint)

### Estimated commit count
25 implementer commits + ~5-7 fix-pass commits + 1 ship commit + 4 portion commits for this plan = **~35 commits**.

---

## 11. Honest disclosures

### 11.1 Standards citation discipline

- All citations verified per §2 table. No invented values.
- **§722 RCD type**: spec uses Reg 722.531.3.101 (Type A default; Type B conditional) per verified file. Earlier brainstorm args had "Type B required" oversimplification — corrected.
- **IET CoP for EV**: 4th Edition per verified file. NOT 3rd Edition.
- **OZEV CoP**: banned name. Actual name is "IET Code of Practice for EV Charging Equipment Installation" (4th Ed).
- **Lift diversity**: IET OSG App A — Table A1 office_lift_single/two/three_or_more, NOT Reg 559 (D2.3 catch).
- **building_diversity floor_factor numbers (office 0.75 / retail 0.85 / industrial 0.90)** from original within-skill-depth-plan: NOT verified in standards file. D4 uses density + future_expansion_pct from verified file instead.

### 11.2 Cross-skill cascade disclosures

- 4 new Part-7 small-power examples consume producer-side cascade fixtures from special-locations. 2 of the cascade fixtures (`cascade-small-power-uk-ev-charge-domestic` + `cascade-small-power-uk-sauna-heater-exemption`) are AUTHORED as part of D4 sprint (D.1) — disclosed in their honest disclosures.
- Pool example (#1) consumes `cascade-lighting-layout-uk-pool-hall/intent-out.json` (anchor-driven engineering equivalence). Disclosed in input + assumptions + rationale + reasoning.md. Engineer-of-record substitutes project-specific small-power-pool cascade in future per the same pattern D.4 special-locations established.

### 11.3 building_diversity coverage limitations

- v2.0 covers 3 building_type values (office / industrial / healthcare) per verified standards file
- Retail / residential / data-center / hospitality deferred to v2.1
- design_density_w_per_m2 must be within standards-file range OR flagged via D-8 reviewer flag

### 11.4 OUT of scope (explicit boundaries)

- Cable rating tables (4D1A + 4D5A) — cable-sizing's domain
- Cable derating (Ca/Cg/Ci) — cable-sizing's domain
- Voltage drop (Appendix 12) — cable-sizing's domain
- §722.411.4.1 open-PEN protection — dedicated EV-Charge skill + earthing skill v1.x
- Mode 3 / Mode 4 cable-sizing routing — dedicated EV-Charge skill
- MRI room electrical — separate sibling skill (per special-locations spec §13)

---

## 12. v2.1+ deferrals (declared)

| Item | Trigger to build |
|---|---|
| building_diversity retail / residential / data-center / hospitality profiles | When standards-file entries land + verified |
| Full lighting-controls cascade integration (DALI scene scheduling impact on small-power loads) | Wave 3 lighting-controls skill ships |
| Full EV-Charge skill (open-PEN + Mode 3/4 + smart charging + load management) | Dedicated EV-Charge skill (currently stub) |
| INT jurisdiction full Part-7 examples (IEC 60364-7-XXX routing for §702/§710/§722) | When first INT project requirement lands |

---

## 13. Cross-references

- Spec predecessors:
  - `2026-06-01-special-locations-design.md` (Wave 1 second deliverable; cascade wiring + 1 small-power Part-7 example)
  - `2026-05-30-photometric-analysis-design.md` (Wave 1 first deliverable; cascade pattern parent)
- Cluster roadmap: `2026-05-29-lighting-cluster-roadmap.md` Wave 2
- Standards files (all `verification_status: verified-against-source`):
  - `shared/standards/electrical/BS7671/diversity-factors.json`
  - `shared/standards/electrical/BS7671/part7-special-locations.json`
  - `shared/standards/electrical/BS7671/reg433-overcurrent-protection.json`
  - `shared/standards/electrical/BS7671/reg411-rcd-requirements.json` (for §722 RCD type cross-reference)
- Memory cross-refs:
  - `[[within-skill-depth-plan]]` — D3/D4 original scope (items 8 + 9)
  - `[[sprint-D2-shipped]]` — Reg 559 + OZEV CoP misname catches
  - `[[sprint-D3-shipped]]` — small-power D3 push to D4
  - `[[photometric-analysis-shipped]]` — Wave 1 first; cascade pattern parent
  - `[[special-locations-shipped]]` — Wave 1 second; cascade wiring + 1 Part-7 example
  - `[[feedback-no-haiku-sonnet-opus-only]]`
  - `[[feedback-no-trim-non-consequential]]`
  - `[[build-strategy-breadth-first]]`
  - `[[runtime-project-boundary]]`

---

## 14. Next action

After user approval of this spec:

1. Invoke `superpowers:writing-plans` to produce `docs/superpowers/plans/2026-06-02-small-power-d4-depth-sprint.md`.
2. Plan portions 1-4 committed sequentially (matches special-locations + photometric portion-by-portion pattern).
3. Sprint execution via `superpowers:subagent-driven-development` — 25 implementer tasks across 4 phases.

Estimated commit count: 30-35 (per `[[sprint-D3-shipped]]` 10/11 fix-pass pattern). Estimated wall-clock: comparable to special-locations (~one focused session).

After ship: Wave 2 first deliverable complete. **Wave 2 second deliverable** = `lighting-layout v1.6.x extensions` (task/ambient luminaire split + 3D placement). Then Wave 3 = `emergency-lighting + lighting-controls` parallel. Then Wave 4 = `daylight → energy-leni` sequential.
