# DB Layout — Validator Prompt

You are validating a db-layout IR document produced by the `electrical/db-layout` skill generator.

## Input
- An IR JSON document at the user-provided path.
- Schemas at `electrical/db-layout/schemas/{db-layout-ir,db-layout-intent,db-layout-rollup-intent}.schema.json`.

## Validation procedure

### 1. Schema validation
Run JSON-schema validation against `db-layout-ir.schema.json`.
- If invalid: STOP. Emit `{"valid": false, "stage": "schema", "errors": [...]}`.

### 2. Cross-field invariants

For each item below, emit a violation if the rule fails.

**INV-01: Board way accounting.**
Applies when `board.board_kind == "main_switchboard"` (oneOf branch enforces ways accounting): `board.ways_used + board.ways_spare == board.ways_total`. When `board.board_kind == "specialty_board"`, INV-01 is not applicable (specialty boards may omit the ways triple).

The `board_kind` discriminator (Sprint 3-W2b) gates which oneOf branch is enforced by the schema — a wrong discriminator (e.g. emitting `main_switchboard` shape but declaring `board_kind: "specialty_board"`) hard-fails at schema validation before reaching the invariants stage.

**INV-02: Circuit-to-way mapping uniqueness.**
Every `circuits[*].way_module_id` must be unique across all circuits in this IR.

**INV-03: Busbar rating coverage.**
`busbar.rating_a >= sum(circuits[*].ocpd.rating_a) × diversity_factor` (diversity from compliance_summary.assumptions OR default 0.7).

**INV-04: OCPD-cable coordination.**
For every circuit: `cable.csa_mm2_or_awg`'s ampacity (from jurisdiction ampacity table) >= ocpd.rating_a. Validate by jurisdiction:
- GB: lookup in BS 7671:2018+A2:2022 Appendix 4 Tables 4D-4F
- KE: lookup in BS 7671:2018+A2:2022 Appendix 4 (KS 1700:2018 §313 routes ampacity to BS Appendix 4)
- EU/INT: lookup in IEC 60364-5-52:2009 Annex B Tables B.52.2-B.52.4
- US: lookup in NEC 2023 Article 310.16 (75°C / 90°C column per terminal rating)

**INV-05: Breaker breaking capacity.**
For every circuit: `ocpd.breaking_capacity_ka >= ifault_at_downstream_ka` (from selectivity_results OR engineer declaration). If unknown, the selectivity_results entry MUST have `tool_call_pending: true`.

**INV-06: Busbar IcW coverage.**
`busbar.icw_ka_1s >= ipk_at_busbar` (per IEC 61439 short-circuit-withstand reference).

**INV-07: Symbol references.**
Every `drawn_as_symbols[*]` must be a valid symbol_id in `shared/standards/electrical/IEC60617/symbol-index.json`.

**INV-08: RCD requirement per jurisdiction.**
- TT system (consumed from upstream): every circuit must have `rcd.required: true`.
- TN-C-S + GB + socket-outlets ≤32A in domestic: `rcd.required: true` per BS 7671 411.3.3.

**INV-09: Selectivity result completeness.**
Every upstream-downstream OCPD pair must have a corresponding `selectivity_results[]` entry. No silent omissions.

**INV-10: Rationale presence.**
`rationale` block must exist with `chat_summary` (40-500 chars) and `sections` (≥1).

**INV-11: Standards citations format.**
Every `compliance_summary.non_compliance_flags[].code_clause` entry must use canonical format:
- BS 7671 (GB): `"BS 7671:2018+A2:2022 Reg N.N.N"` or `"BS 7671:2018+A2:2022 Table N.N"`
- KS 1700 (KE): `"KS 1700:2018 §N.N.N"` direct form — Annex E §VIII may be cited as a routing-note suffix (e.g. `"KS 1700:2018 §X.Y.Z (Annex E: adopts BS 7671:2018+A2 Reg X.Y.Z verbatim)"`). The banned trailing annotation `"BS 7671 ... (adopted by KS 1700)"` is forbidden — flag as INV-11 fail if encountered.
- IEC 60364 (EU/INT): `"IEC 60364-N-NN:YYYY Clause N.NN.N"`
- IEC 61439 (all IEC jurisdictions): `"IEC 61439-N:YYYY Clause N.NN.N"`
- NEC (US): `"NEC 2023 Art NNN.NN"` or `"NEC 2023 Table NNN.NN"` or `"NFPA 70:2023 Article NNN.NN"`

Cross-contamination ban: `KS 1700` must not appear when `jurisdiction != "KE"`. `BS 7671` must not appear as a primary citation when `jurisdiction != "GB"` AND `jurisdiction != "KE"` (KE only via the routing-note form above).

**INV-12: Diversity factor — instantaneous loads must use 1.00.**
For any circuit whose `designation` or load metadata indicates an
instantaneous load (e.g. `instantaneous_shower`, `instantaneous_water_heater`,
or shower / instant heater designations with `downstream_load_kw ≥ 7.2`),
the diversity factor applied to its demand contribution MUST be 1.00 (not
a blanket lower factor). Per BS 7671:2018+A2:2022 § 311.1 + IET OSG
Appendix A.

Validator action: if a circuit is an instantaneous load AND the board-level
diversity assumption recorded in `compliance_summary.assumptions[]` applies
a sub-1.00 factor uniformly across all circuits (including instantaneous),
FLAG INV-12. The fix is to record per-load-type diversity, not a blanket
factor, and explicitly call out the 1.00 factor on instantaneous loads.

Rationale: instantaneous heating loads are inherently full-rated when
energised — no statistical diversity applies. H5 defect class.

**INV-13: Phase preservation on TPN boards.**
For boards where `incoming_supply.phase_arrangement ∈ {"TPN", "TPN_plus_E"}`,
every circuit in `circuits[]` MUST carry `phase ∈ {"L1", "L2", "L3"}` or a
3-phase span value (`"L1+L2+L3"` for 3-phase loads). ELV / SELV / PELV
control circuits that intrinsically don't see phase current MAY omit
`phase` with an explanatory `drawing_notes[]` entry.

The board IR MUST include:
- `per_phase_loading_a`: object with `L1`, `L2`, `L3` numbers (A)
- `neutral_current_a`: number (A), worst-case unbalanced neutral per IEC
  60364-5-52 § 524.2.2.

Validator actions:
- If board is TPN AND any non-ELV circuit lacks `phase`, FLAG INV-13.
- If `per_phase_loading_a` is absent on a TPN board, FLAG INV-13.
- If `neutral_current_a` is absent on a TPN board with non-zero loads,
  FLAG INV-13.
- Sanity-check `I_N ∈ [0, max(IL1, IL2, IL3)]`. If outside the range,
  FLAG INV-13 — the unbalance formula was applied incorrectly.

**Validator action (additional, PHASE_UNBALANCE regression-detection):**
Compute `unbalance_pct = neutral_current_a / max(per_phase_loading_a.L1,
per_phase_loading_a.L2, per_phase_loading_a.L3) × 100`. If `unbalance_pct
> 30` AND no entry in `compliance_summary.non_compliance_flags[]` has
`code == "PHASE_UNBALANCE_HIGH"`, FLAG INV-13. This guarantees the
PHASE_UNBALANCE_HIGH rule (declared in `prompts/generator.md` Step 6) is
emitted whenever the board crosses the 30% unbalance threshold — closes
the regression-detection gap from the B.3 fix-pass.

Rationale: phase balance is the classic 3-phase board failure mode; H6
defect class. Per IEC 60364-5-52 § 524.2.2 the neutral current depends on
per-phase unbalance.

---

**INV-14: Label format compliance (D2.2).**

**Severity:** HIGH

**Rule:** For every board:

1. **label_format_standard present + jurisdictional alignment.** `label_format_standard ∈ {"BS", "NEC", "IEC"}`. Expected mapping: GB/KE → BS, US → NEC, INT/EU → IEC. Mismatch emits an INFO (not HIGH) — engineer may override for multi-jurisdiction projects.

2. **board_label populated.** `board_label.text` non-empty, ≤120 chars, AND contains NO `{{` placeholder remnants. `board_label.svg` ≥50 chars AND contains NO `{{` placeholder remnants (substring `"{{"` is forbidden in either field — indicates the template was not populated).

3. **board_label.text matches the format-pattern regex for label_format_standard:**
   - BS regex: `^[\w.-]+\s*\|\s*\d+\s*V\s+\S+\s*\|\s*Main\s+Switch\s+\d+\s*A\s*\|\s*\S.*\S\s*$`
   - NEC regex: `^[\w.-]+\s*—\s*\d+V\s+\S+\s*\d+-wire\s*—\s*Main:\s*\d+A\s+\S+\s*—\s*\S.*\S\s*$`
   - IEC regex: `^[\w.-]+\s*\|\s*U=\d+\s*V\s+\S+\s*\|\s*I_n=\d+\s*A\s*\|\s*\S.*\S\s*$`

   The terminal `\s*\S.*\S\s*$` clause (instead of `.*$`) requires at least one
   non-whitespace token in the warning slot, so a board_label whose 4th field
   is pure whitespace OR an unfilled `{{...}}` placeholder string is rejected.

For every circuit on every board:

4. **circuit_label populated.** `circuit_label.text` non-empty, ≤120 chars, AND contains NO `{{` placeholder remnants. `circuit_label.svg` ≥50 chars AND contains NO `{{` placeholder remnants. The 120-char cap accommodates two-line strip-label layouts (real panel directories routinely wrap onto a second line for NEC dedicated/life-safety circuits whose designation already spans the strip).

5. **circuit_label.text matches the format-pattern regex:**
   - BS: `^[\w.]+\s*\|\s*\S.*\S\s*\|\s*(L1|L2|L3|N|L1N|L1L2|L1L2N|L1L2L3|L1L2L3N)\s*\|\s*\S.*\S\s*\|\s*\S.*\S\s*\|\s*\S.*\S\s*$`
   - NEC: `^[\d,\-]+\s+—\s+\S.*\S\s+—\s+\S.*\S\s+—\s+\d+A$`
   - IEC: `^[\w.]+\s*\|\s*\S.*\S\s*\|\s*\d+(\.\d+)?\s*A\s*\|\s*\d+(\.\d+)?\s*mm²(\s+\S.*\S)?\s*$`

   **Variations accepted by the loosened regexes:**
   - BS: RCBOs whose rating is carried in the device-name token (e.g.
     `RCBO B6 30mA`) — the 4th field no longer requires a literal `\d+A`
     anywhere; any non-empty token passes. The phase token list now also
     accepts `L1N`, `L1L2N`, and `L1L2L3N` (TPN-with-N variants).
   - NEC: multi-pole circuit numbering like `1,3,5` or `2-4-6` is accepted in
     the leading id slot (previously only a single integer).
   - IEC: an optional trailing cable-type suffix after the csa (e.g.
     `2.5 mm² 5C`, `2.5 mm² Cu/PVC`) is accepted.

   Every field still requires at least one non-whitespace character, so a
   string of pure whitespace fails Rule 5. A literal `{{designation}}`
   placeholder fails Rule 4 (the `{{`-substring guard).

6. **tool_call_pending_for_pdf_png set.** Both `board_label.tool_call_pending_for_pdf_png` and every `circuit_label.tool_call_pending_for_pdf_png` are present and boolean. Typically `true` (LLM-emitted SVG before runtime rasterisation); `false` only after runtime renders PDF/PNG.

**Validator action:** for each board, check label_format_standard + board_label fields per Rules 1–3; for each circuit, check circuit_label per Rules 4–5; verify all SVG fields contain no `{{` substring; verify all tool_call_pending flags are present.

**Rationale:** Panel-schedule IR is not field-usable without circuit labels (BS 7671 §514 / NEC §408.4(A) / IEC 60364-5-51 §514 all require legible identification at the panel). Labels are the field-engineer's only documentation pulled directly from the panel directory pocket; their format must be jurisdiction-correct + machine-checkable so the runtime can rasterise them onto adhesive label stock. The D2.2 fix-pass loosened the original regexes to accept legitimate variations engineers encounter in practice — RCBO labels with the rating embedded in the device name, multi-pole circuit numbering (`1,3,5` or `2-4-6`), TPN-with-N phase tokens (`L1N`, `L1L2N`, `L1L2L3N`), and IEC cable-type suffixes after the csa (`2.5 mm² 5C`) — while keeping the placeholder / pure-whitespace failure modes blocked by Rules 2 + 4.

---

**INV-15: Diversity basis cited per circuit (D2.3).**

**Severity:** HIGH

**Rule:** For every circuit on every board:

1. **diversity_basis present + valid enum values.** Every circuit has `diversity_basis` with `load_type ∈` the 13-value enum, `factor_applied ∈ [0.0, 1.0]`, `method ∈ {no_diversity, largest_plus_remainder_pct, table_factor, engineer_declared}`.

2. **Citation includes a recognisable clause marker.** `diversity_basis.citation` is ≥20 chars AND contains at least one of: `Reg`, `§`, `Table`, `OSG`, `CoP`, `TM`. Pure prose without a clause marker is a HIGH violation.

3. **Regulation-driven hard rules.** If `load_type == "lift"`, then `factor_applied == 1.00` AND `method == "no_diversity"` (per EN 81-20:2020 §5.10 + BS 7671 Section 552 motors). If `load_type == "ev_charger"`, then `factor_applied == 1.00` AND `method == "no_diversity"` (per BS 7671 Reg 722 + IET CoP for EVCI 4th Ed §8.5). Mismatch (e.g. an EV circuit with factor 0.5) is a HIGH violation — these regulations forbid diversity on these loads.

4. **method_params consistency.** If `method == "largest_plus_remainder_pct"`, then `method_params.largest_pct` AND `method_params.remainder_pct` must be present, both ∈ [0, 100], AND their sum ∈ [100, 200]. Documented industry sums: sockets 100+40=140; motor group 100+50=150; AC group 100+75=175. Engineer-declared edge cases outside [100, 200] must use `method: "engineer_declared"` (which bypasses Rule 4).

**Validator action:** for each circuit, check diversity_basis presence; assert factor_applied in range; verify citation contains a clause marker; for load_type ∈ {lift, ev_charger}, assert factor_applied == 1.00; for method == largest_plus_remainder_pct, assert sum of pct in [100, 200].

**Rationale:** Sprint B INV-12 caught the instantaneous-load misapplication (blanket 0.4 factor on a shower load) but did not enforce per-circuit basis citation. The Sprint D2.3 audit trail closes the gap: every circuit now declares (a) which load-type it falls under, (b) what factor applies, (c) what regulation/standard authorises it. A downstream reviewer (TCS / panel-builder / building-control) can verify each circuit independently without inferring from designation prose.

## INV-16 — Special-locations distribution cascade resolved (HIGH)

**Severity:** HIGH when `flags[]` contains `"part7_zone_present"` (i.e. any room served by this board matches the Part-7 set); N/A otherwise.

**Rule (4 sub-checks):**
1. `consumed_intents.special_locations_zoning` is present (cascade triggered + resolved).
2. `consumed_intents.special_locations_zoning.payload.compliant == true` (special-locations' own INVs all PASS upstream).
3. Thin sanity cross-check: walk `circuits[]`; for each circuit serving a Part-7 room (identifiable via `designation` reference or `consumed_intents.special_locations_zoning.payload.electrical_constraints[]` matching the circuit's downstream zone), verify:
   - 30 mA RCD present (`rcd.required: true` AND `rcd.sensitivity_ma == 30`) if `electrical_constraints[]` includes `rcd_blanket_by_room` for that zone (per BS 7671:2018+A2:2022 §701.411.3.3 + §703.411.3.3)
   - Circuit routed via Medical IT panel if `electrical_constraints[]` includes `medical_it_system` for that zone (per BS 7671:2018+A2:2022 §710 + BS EN 61557-8 + HTM 06-01)
   - Supplementary bonding terminal modelled at the board if `supplementary_equipotential_bonding` constraint present for any served zone (per BS 7671:2018+A2:2022 §710 + §701.415.2)
   - Main equipotential bond ≥10 mm² at the ME terminal if `pool_main_equipotential_bonding` constraint present for any served zone (per BS 7671:2018+A2:2022 §702.415.1)
4. Flag cascading: every `payload.non_compliance_flags[]` entry MUST appear in `compliance_summary.non_compliance_flags[]` with `_cascaded_from: "special-locations"` attribution. No silent suppression.

When `flags[]` does not contain `"part7_zone_present"`: trivially PASS (cascade not triggered).

**Validator action:**
- Check `flags[]` for `"part7_zone_present"`. If absent: INV-16 N/A — trivially PASS.
- If present and `consumed_intents.special_locations_zoning` is absent: INV-16 FAIL HIGH.
- Read `consumed_intents.special_locations_zoning.payload`. Verify `compliant == true`. If false: INV-16 FAIL HIGH; cascade flags + add INV-16's own evidence.
- Walk `circuits[]` for Part-7-serving circuits: evaluate 4 distribution sub-rules per above. Any violation: INV-16 FAIL HIGH.
- Walk `payload.non_compliance_flags[]`. For each: verify same flag exists in `compliance_summary.non_compliance_flags[]` with `_cascaded_from: "special-locations"`. If any flag missing: INV-16 FAIL HIGH.

**Citation:** Cluster roadmap §6.7 cascade contract + special-locations INV-08 upstream + spec `2026-06-01-special-locations-design.md` §10.3.

**Rationale:** Boards and OCPDs are not zoning artefacts — they are the upstream supply chain. INV-16 binds db-layout to the special-locations spatial-compliance layer at the circuit-supply level: every circuit serving a Part-7 room MUST carry the right protection topology (30 mA RCD for bathroom/sauna; Medical IT for Group 2 OR; main equipotential bond for pools). Without this binding, a board could ship with an inadequate protection scheme and no engineer review would catch it.

---

### 3. Intent extraction validation

Project the IR down to:
1. `db-layout` single-board intent shape (validate against `db-layout-intent.schema.json`)
2. The board's contribution to the project-rollup intent (validate against `db-layout-rollup-intent.schema.json`)

## Output

Emit a single JSON object:

```json
{
  "valid": true | false,
  "stage": "schema" | "invariants" | "intent" | "passed",
  "errors": [
    {"code": "INV-N", "path": "$.circuits[2]", "message": "..."}
  ],
  "warnings": [...]
}
```

`valid: true` requires ALL of: schema pass, all 16 invariants pass (INV-01 → INV-16), both intent projections valid.

## Floor plan context

When the prompt context includes a `## Floor plan context` markdown
block, the validator MUST surface a finding for any of:

1. IR places an entity in a room not listed in the block.
2. The block flagged unconfirmed rooms AND the IR's `assumptions`
   array does not mention the unconfirmed rooms when those rooms were
   consumed.
3. IR's `building_label` field (if present) does not match the
   building label in the block.
4. IR omits `floor_plan_context_consumed: true` when the block was
   present.

Findings should cite the room name and the block location so the
reviewer can correlate.
