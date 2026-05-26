# Sprint D2 — Sizing & Boards depth (design spec)

**Date:** 2026-05-26
**Sprint:** D2 (second of three within-skill-depth sprints)
**Skills touched:** `electrical/cable-sizing` (v1.0.2 → v1.1.0), `electrical/db-layout` (v1.3.3 → v1.4.0)
**Context:** Closes 3 of the 9 within-skill-depth items per `[[within-skill-depth-plan]]`. D1 (Protection & Safety) shipped 2026-05-26 per `[[sprint-D1-shipped]]`. D3 (small-power depth) follows.

---

## §1 Sprint scope

Three within-skill depth items:

| Item | Skill | Title | Model |
|---|---|---|---|
| 5 | cable-sizing | PVC/SWA edge cases — 4D1A + 4D5A consumers | Opus |
| 6 | db-layout | Board labelling (text + SVG templates) | Sonnet |
| 7 | db-layout | Diversity edge cases (lifts + EV + AC + motor groups) | Opus |

Estimated effort: ~2 dev-days. Sequenced D2.1 → D2.2 → D2.3 → D2.4 (ship). No parallel tasks.

---

## §2 Item 5 — cable-sizing PVC/SWA edge cases (D2.1)

### §2.1 Problem statement

BS 7671 Appendix 4 Tables 4D1A (PVC twin-and-earth) and 4D5A (PVC SWA) were transcribed in Sprint C.2 and ship under `shared/standards/electrical/BS7671/` with `verification_status: engineer_transcription_C2`. Zero of the 4 existing cable-sizing examples consume either table. The `table_used` field does not appear on any cascade node. cable-sizing's `cable_type` enum lacks `pvc_twin_earth` and `pvc_swa` as explicit values, so the UK domestic example (which is physically T&E in reality) incorrectly uses `pvc_singles`.

### §2.2 Schema additions

File: `electrical/cable-sizing/schemas/cable-sizing-ir.schema.json`

**Extend `cable_type` enum** (additive) — append `pvc_twin_earth` and `pvc_swa` after existing values. Keep `pvc_singles`, `xlpe_swa`, `xlpe_lszh`, `thwn_2`, `xhhw_2` unchanged.

**Add `table_used` field** on every cable-bearing cascade node:

```json
"table_used": {
  "type": "string",
  "enum": [
    "4D1A", "4D2A", "4D4A", "4D5A",
    "4E1A", "4E2A", "4E4A", "4E5A",
    "nec_310_16_60", "nec_310_16_75", "nec_310_16_90",
    "iec_60364_5_52_b1", "iec_60364_5_52_e", "iec_60364_5_52_f",
    "none"
  ],
  "description": "Reference table consulted for the ampacity walk. `none` for jurisdictions without a tabular reference. Required when installation_method is set. Cite in `_source`."
}
```

`table_used` becomes REQUIRED on cascade items where `installation_method` is set. Schema-additive for nodes without `installation_method` (transformer secondaries, busbar nodes, etc).

### §2.3 Generator step

Append a new step (or extend existing Step 5 — the implementer chooses based on flow) covering the table-selection walk:

```
For every cable-bearing cascade node:
1. Identify cable_type from inputs.cable_data + installation context
2. Identify installation_method from physical context (clipped / conduit / buried / cable tray / etc.)
3. SELECT the correct BS 7671 4D-series (or NEC equivalent) table per the compatibility matrix:
   - pvc_twin_earth → 4D1A (UK domestic methods: C, A1, 100, 101, 102, 103)
   - pvc_swa       → 4D5A (Method C clipped, Method D direct-buried)
   - pvc_singles   → 4D2A (method B1 in conduit) or 4D4A (multicore)
   - xlpe_swa      → 4E5A
   - xlpe_lszh     → 4E1A or 4E2A
   - thwn_2/xhhw_2 → nec_310_16_75 or nec_310_16_90
4. Set `table_used` to the selected table identifier
5. Set `_source` to "BS 7671:2018+A2:2022 App 4 Table {table_used} method {installation_method}"
```

### §2.4 Validator INV-12 — cable_type ↔ table_used consistency (HIGH)

For every cascade node with `cable_type` and `installation_method` set:

1. **Compatibility:** `cable_type` maps to a specific `table_used` per the matrix above. Mismatch is a HIGH violation.
2. **Method validity:** the chosen `table_used` must list `installation_method` in its `installation_methods` block.
3. **Citation:** every cable's `_source` cites the same `table_used` + `installation_method` (string-match required).
4. **Engineer-transcription disclosure:** when `table_used ∈ {4D1A, 4D5A}`, the example reasoning.md must cite the Sprint C.2 transcription disclosure (`verification_status: engineer_transcription_C2`) honestly.

### §2.5 Example coverage

**Refit** `electrical/cable-sizing/examples/uk-domestic-final-circuits/output.json`:
- Switch ring-final, lighting, cooker, and shower circuits from `pvc_singles` → `pvc_twin_earth`
- Add `table_used: "4D1A"` on each
- Update `installation_method` enum to UK-domestic-specific (C, A1, 100/101/102/103)
- Refresh `ampacity_a` values per 4D1A column reads (e.g. 2.5 mm² method C = 27 A; method 102 = 19.5 A)
- Update reasoning.md narrating the table walk + Sprint C.2 honesty disclosure

**NEW** `electrical/cable-sizing/examples/uk-rural-swa-submain/`:
- 4 files: input.json, output.json, intent-out.json, reasoning.md
- Scenario: 100 m direct-buried 4D5A PVC SWA submain from service entrance to rural outbuilding DB. Single-phase 100 A.
- Cascade: SERVICE-IN → SUBMAIN-CABLE (4D5A method D 25 mm²) → OUT-DB (100 A SP&N)
- Exercise method D explicitly (direct-buried, soil thermal resistivity 2.5 K·m/W per 4D5A notes)
- Hand-computed ampacity + voltage drop walk in reasoning.md
- Cite `verification_status: engineer_transcription_C2` disclosure in `_source`

### §2.6 D2.1 deliverables

- Schema: 2 new cable_type enum values + new table_used field
- Generator step
- INV-12
- Refit existing example (uk-domestic-final-circuits)
- New example folder (uk-rural-swa-submain)
- CHANGELOG `[1.1.0]` entry
- Manifest `version: 1.1.0` + new example registered in `examples[]`

---

## §3 Item 6 — db-layout board labelling (D2.2)

### §3.1 Problem statement

db-layout produces panel-schedule IR but ships ZERO label fields. No per-circuit label (the text that printed-and-affixed to the panel directory pocket) and no per-board headline label. A panel schedule without labels is not field-usable. BS 7671 §514, NEC §408.4(A), and IEC 60364-5-51 §514 all require legible circuit identification at the panel.

### §3.2 Schema additions

File: `electrical/db-layout/schemas/db-layout-ir.schema.json`

**Per-board** (root-level on each board entry):

```json
"label_format_standard": {
  "type": "string",
  "enum": ["BS", "NEC", "IEC"],
  "description": "Jurisdiction-bound label format. BS = BS 7671 §514 + IET OSG App B. NEC = NEC §408.4(A). IEC = IEC 60364-5-51 §514 + IEC 61439-1 §5.5.",
  "required": true
},
"board_label": {
  "type": "object",
  "required": ["text", "svg", "tool_call_pending_for_pdf_png"],
  "additionalProperties": false,
  "properties": {
    "text": {
      "type": "string",
      "minLength": 1,
      "maxLength": 120,
      "description": "Formatted per label_format_standard. Includes board designation + supply + main switch rating + dual-source warning if applicable."
    },
    "svg": {
      "type": "string",
      "minLength": 50,
      "description": "Populated SVG markup (no {{ placeholders}} remaining). LLM-writable from templates/<standard>-board-label.svg.template. Runtime-rasterisable via calc.render_label."
    },
    "tool_call_pending_for_pdf_png": {
      "type": "boolean",
      "description": "true until calc.render_label runs in the runtime; SVG content is still LLM-readable + previewable in a browser."
    }
  }
}
```

**Per-circuit** (inside `circuits[].items` or equivalent):

```json
"circuit_label": {
  "type": "object",
  "required": ["text", "svg", "tool_call_pending_for_pdf_png"],
  "additionalProperties": false,
  "properties": {
    "text": {
      "type": "string",
      "minLength": 1,
      "maxLength": 80,
      "description": "Formatted per board.label_format_standard. ≤80 chars to fit strip-label width."
    },
    "svg": {"type": "string", "minLength": 50},
    "tool_call_pending_for_pdf_png": {"type": "boolean"}
  }
}
```

### §3.3 NEW templates directory

Create `electrical/db-layout/templates/` with 6 files:

| File | Standard | Width × Height |
|---|---|---|
| `bs-7671-circuit-label.svg.template` | BS 7671 §514 + IET OSG App B | 50 × 12 mm |
| `nec-408-4-circuit-label.svg.template` | NEC §408.4(A) | 50 × 12 mm |
| `iec-60364-5-51-circuit-label.svg.template` | IEC 60364-5-51 §514 / IEC 61439-1 §5.5 | 50 × 12 mm |
| `bs-7671-board-label.svg.template` | BS 7671 §514.13 | 100 × 60 mm |
| `nec-408-4-board-label.svg.template` | NEC §408.4 | 100 × 60 mm |
| `iec-60364-5-51-board-label.svg.template` | IEC 60364-5-51 §514 | 100 × 60 mm |

Templates use `{{placeholder}}` syntax matching `electrical/arc-flash-labelling/templates/` pattern. Examples of placeholders per jurisdiction:

- **BS**: `{{way}}`, `{{description}}`, `{{phase}}`, `{{ocpd_type}}`, `{{ocpd_rating_a}}`, `{{cable_type}}`, `{{cable_csa_mm2}}`, `{{rcd_if_any}}`
- **NEC**: `{{circuit_number}}`, `{{description}}`, `{{load_served}}`, `{{ocpd_rating_a}}`
- **IEC**: `{{id}}`, `{{function}}`, `{{in_a}}`, `{{csa_mm2}}`

### §3.4 Generator step

Append a new step:

```
For every board:
1. Determine label_format_standard from jurisdiction:
   - GB / KE → "BS" (KE adopts BS 7671 via Annex E)
   - US → "NEC"
   - INT / EU → "IEC"
2. Populate board_label.text per the per-jurisdiction format string:
   - BS: "<board_designation> | <voltage_v> V <phase_arrangement> | Main Switch <main_switch_rating_a> A | <dual_supply_warning_if_applicable>"
   - NEC: "<board_designation> — <voltage_v>V <phase> — Main: <main_switch_rating_a>A — <warning>"
   - IEC: "<id> | U=<voltage_v> V | I_n=<main_switch_rating_a> A | <warning>"
3. Read the matching templates/<standard>-board-label.svg.template; populate placeholders; emit as board_label.svg
4. Set board_label.tool_call_pending_for_pdf_png = true
5. For each circuit in this board:
   - Populate circuit_label.text per jurisdictional format:
     * BS: "<way> | <description> | <phase> | <ocpd_type> <ocpd_rating_a> A | <cable_csa_mm2>mm² <cable_type> | <rcd_if_any>"
     * NEC: "<circuit_number> — <description> — <load_served> — <ocpd_rating_a>A"
     * IEC: "<id> | <function> | <in_a> A | <csa_mm2> mm²"
   - Read templates/<standard>-circuit-label.svg.template; populate; emit as circuit_label.svg
   - Set tool_call_pending_for_pdf_png = true
```

### §3.5 Validator INV-14 — Label format compliance (HIGH)

For every board:

1. `label_format_standard ∈ {"BS", "NEC", "IEC"}` and matches jurisdiction expectation (GB/KE → BS, US → NEC, INT/EU → IEC; non-match is INFO not HIGH — engineer may override).
2. `board_label.text` non-empty, ≤120 chars.
3. `board_label.svg` contains populated content (no `{{` placeholder remnants remaining).

For every circuit in the board:

4. `circuit_label.text` non-empty, ≤80 chars.
5. `circuit_label.text` matches the format-pattern regex for `label_format_standard`:
   - BS: `^\d+\s*\|\s*.+\s*\|\s*(L1|L2|L3|N|L1L2|L1L2L3)\s*\|\s*.+$`
   - NEC: `^\d+\s+—\s+.+\s+—\s+.+\s+—\s+\d+A$`
   - IEC: `^[A-Z0-9.-]+\s*\|\s*.+\s*\|\s*\d+(\.\d+)?\s*A\s*\|\s*\d+(\.\d+)?\s*mm²$`
6. `circuit_label.svg` populated (no placeholder remnants).
7. `tool_call_pending_for_pdf_png` set (true until runtime renders).

### §3.6 Manifest

Add `shared/calculations/electrical/render-label.json` to `electrical/db-layout/skill.manifest.json` `calculations[]` array.

### §3.7 Example coverage

Backport `label_format_standard` + `board_label` + `circuit_label` across all 20 existing db-layout example outputs. Use Sonnet for the mechanical population per the model-selection rule. Each example's reasoning.md gets a short "Labels" section noting the jurisdictional format applied.

### §3.8 D2.2 deliverables

- Schema: 3 new field blocks
- 6 NEW template files
- Generator step
- INV-14
- 20 example backports
- Manifest update (calculations[] + version)
- CHANGELOG `[1.4.0]` entry (combined with D2.3)

---

## §4 Item 7 — db-layout diversity edge cases (D2.3)

### §4.1 Problem statement

db-layout's per-load-type diversity table (Sprint B M1 work, in generator.md) currently covers water heaters, showers, sockets (100% + 40%), and motors (100% + 50%). Missing: lifts (Reg 559), EV charging (Reg 722 + OZEV CoP), AC units (single + grouped per CIBSE TM50). The schema also doesn't surface the `diversity_basis` per circuit — the factor is computed but the audit trail (which clause was applied, why) is not first-class. Sprint B INV-12 catches the instantaneous-load misapplication but doesn't enforce per-circuit basis citation.

### §4.2 Schema additions

File: `electrical/db-layout/schemas/db-layout-ir.schema.json`

Extend `circuits[].items` with:

```json
"diversity_basis": {
  "type": "object",
  "required": ["load_type", "factor_applied", "method", "citation"],
  "additionalProperties": false,
  "properties": {
    "load_type": {
      "type": "string",
      "enum": [
        "instantaneous_water_heater", "shower", "storage_water_heater",
        "socket_general", "motor_single", "motor_group",
        "lift", "ev_charger", "ac_single", "ac_group",
        "lighting_continuous", "fixed_resistive", "other_declared"
      ]
    },
    "factor_applied": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0,
      "description": "Diversity factor 0.0–1.00. 1.00 means no diversity."
    },
    "method": {
      "type": "string",
      "enum": [
        "no_diversity",
        "largest_plus_remainder_pct",
        "table_factor",
        "engineer_declared"
      ]
    },
    "method_params": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "largest_pct": {"type": "number", "minimum": 0, "maximum": 100},
        "remainder_pct": {"type": "number", "minimum": 0, "maximum": 100}
      },
      "description": "Required when method == 'largest_plus_remainder_pct' (e.g. sockets: 100/40; motors: 100/50; AC grouped: 100/75)."
    },
    "citation": {
      "type": "string",
      "minLength": 20,
      "maxLength": 300,
      "description": "Names the clause (Reg / § / Table / OSG / CoP / TM). INV-15 enforces a recognisable clause marker."
    }
  }
}
```

`diversity_basis` is REQUIRED on every circuit. Schema-additive for boards that pre-date this field — examples backport the field; no breaking change to v1.3 consumers as long as they're updated to read the new field.

### §4.3 Generator step extension

Extend the existing per-load-type table with 4 new rows + tighten 2 existing citations:

| Load type | Factor / method | Citation |
|---|---|---|
| Instantaneous water heater | 1.00 | BS 7671:2018+A2:2022 § 311.1 + IET OSG App A |
| Shower (≥7.2 kW instantaneous) | 1.00 | BS 7671:2018+A2:2022 § 311.1 |
| Storage water heater | 1.00 | IET OSG App A (continuous load) |
| Standard socket-outlet | 100% largest + 40% remainder | IET OSG App A |
| **Lift / lift motor** | **1.00** | **BS 7671:2018+A2:2022 Reg 559 + IET WR9 + EN 81-20:2020** |
| **EV charging point** | **1.00** | **BS 7671:2018+A2:2022 Reg 722 + OZEV CoP for EV Charging Equipment Installation §4.3 + IET CoP for EVCI 4th ed. §8.5** |
| **AC unit — single** | **1.00** | **CIBSE TM50:2014 §4.2 + BS 7671 Reg 552** |
| **AC group (multi-split)** | **100% largest + 75% remainder** | **CIBSE TM50:2014 Table 4.3** |
| Motor — single (tighten citation) | 1.00 | BS 7671:2018+A2:2022 Reg 552.1.1 |
| Motor group (tighten citation) | 100% largest + 50% remainder | BS 7671:2018+A2:2022 Reg 552 + IET OSG App A motor section |
| Lighting (continuous) | 1.00 | IET OSG App A |
| Fixed resistive (e.g. immersion heater bank) | 1.00 | IET OSG App A |

**Generator instructs the LLM to populate `diversity_basis` on every circuit** with the matching row's factor, method, params, and citation.

### §4.4 Validator INV-15 — Diversity basis cited per circuit (HIGH)

For every circuit on every board:

1. `diversity_basis` present with `load_type` ∈ enum, `factor_applied` ∈ [0.0, 1.0], `method` ∈ enum.
2. `citation` ≥ 20 chars AND contains at least one recognisable clause marker: `Reg`, `§`, `Table`, `OSG`, `CoP`, `TM`.
3. If `load_type ∈ {lift, ev_charger}` then `factor_applied == 1.00` (regulation-mandated; INV catches misapplication).
4. If `method == "largest_plus_remainder_pct"` then `method_params.largest_pct` AND `method_params.remainder_pct` are present and sum within [100, 200] (sockets 140 / motors 150 / AC grouped 175 — defensible range).

### §4.5 Example coverage

**Refit** `electrical/db-layout/examples/intl-commercial-tpn-msb/` (or whichever existing example has the most diverse load mix — implementer picks at plan time): populate `diversity_basis` on every circuit.

**NEW** `electrical/db-layout/examples/uk-mixed-use-lifts-and-ev/`:
- 4 files: input.json, output.json, intent-out.json, reasoning.md
- Scenario: UK mixed-use building DB serving 1 lift + 4 EV chargers (7 kW each) + 2 AC units (single + grouped pair) + general sockets + lighting
- ~8–10 circuits exercising 5 of the 12 diversity load-types
- Demonstrates: lift 1.00 / EV 1.00 / AC single 1.00 / AC group 100+75 / motor group 100+50 / sockets 100+40 / lighting 1.00
- reasoning.md narrates the diversity walk + cites all 5 clauses
- **Schema dependency:** must ALSO carry `label_format_standard: "BS"` + `board_label` + `circuit_label` on every circuit, since D2.2 made those fields required. Author the labels using the BS templates created in D2.2.

### §4.6 Backport scope to other 19 examples

All 19 other existing db-layout example outputs gain `diversity_basis` on every circuit. This is mechanical (the load type is implicit in the existing circuit description) — Sonnet sub-dispatch within D2.3 if Opus considers it within scope, else a small Sonnet follow-up at the end of D2.3.

### §4.7 D2.3 deliverables

- Schema: diversity_basis block
- Generator step extension (4 new rows + tighter citations)
- INV-15
- Refit 1 example + NEW uk-mixed-use-lifts-and-ev
- 19 existing examples backport diversity_basis on every circuit
- CHANGELOG `[1.4.0]` entry (combined with D2.2)

### §4.8 Explicitly deferred to Sprint D3 (item 9)

Building-level area diversity (`building_diversity: {building_type: office|retail|industrial, factor: 0.75|0.85|0.90, applied_after: per_load_diversity}` at IR root) belongs in small-power v1.2 per the within-skill-depth-plan. NOT in scope for D2.

---

## §5 Sprint workflow + ship gates (D2.4)

### §5.1 Task sequencing

Strict sequential, no parallel:

```
D2.1 cable-sizing PVC/SWA (Opus)
  ↳ spec compliance review (Opus)
  ↳ code quality review (Opus)
  ↳ fix-pass if FIX-NEXT items
D2.2 db-layout labelling (Sonnet)
  ↳ spec compliance review (Opus)
  ↳ code quality review (Opus)
  ↳ fix-pass if FIX-NEXT items
D2.3 db-layout diversity (Opus)
  ↳ spec compliance review (Opus)
  ↳ code quality review (Opus)
  ↳ fix-pass if FIX-NEXT items
D2.4 ship (Opus orchestrator + Sonnet 8-check fence + memory + push)
```

Two-stage review per task (matching D1 cadence). BLOCKING issues halt; FIX-NEXT applied inline before next task starts.

### §5.2 INV numbering (resolved at plan-writing time per Sprint B.5 fix-pass-2 convention)

- cable-sizing currently ends at INV-11 → new is **INV-12** (cable_type ↔ table_used)
- db-layout currently ends at INV-13 → new are **INV-14** (label format) → **INV-15** (diversity basis cited)

Zero-padded throughout (INV-12 not INV-1+something).

### §5.3 Version bumps

- cable-sizing 1.0.2 → **1.1.0** (minor: new cable_type enum values + INV-12 + new example + table_used field)
- db-layout 1.3.3 → **1.4.0** (minor: combined D2.2 + D2.3 — single bump after both ship)

Manifest updates:
- cable-sizing manifest registers `uk-rural-swa-submain` in `examples[]` array
- db-layout manifest registers `uk-mixed-use-lifts-and-ev` in `examples[]` + adds `shared/calculations/electrical/render-label.json` to `calculations[]`

### §5.4 Gates at ship

- `python3 scripts/validate-examples.py`: AGGREGATE **225/225** (current 221 + uk-rural-swa-submain ×2 + uk-mixed-use-lifts-and-ev ×2 = +4 [each new example adds 1 output.json Pass 1 + 1 intent-out.json Pass 4])
- `python3 functional_audit.py`: 1 finding unchanged (the disclosed motor-superposition oracle FP from D1.1)
- If oracle gains new checks for `table_used` reconciliation during D2.1 (out of scope unless implementer flags as necessary), document in CHANGELOG

### §5.5 Sonnet 8-check fence (D2.4)

Mirrors D1.5 fence shape:

| Check | What |
|---|---|
| 1 | Gates: validate-examples 225/225 + functional_audit 1 finding |
| 2 | D2.1 hand-check uk-rural-swa-submain: 4D5A direct-buried 25 mm² ampacity reconciles to BS 7671 4D5A Method D column; INV-12 entry in invariants[] |
| 3 | D2.1 hand-check uk-domestic-final-circuits refit: ring-final + lighting now use `pvc_twin_earth` + `table_used: 4D1A`; reasoning.md cites Sprint C.2 disclosure |
| 4 | D2.2 hand-check `uk-domestic-consumer-unit` (canonical BS db-layout example): `label_format_standard: "BS"`; every circuit has `circuit_label.text` matching BS regex; every board has `board_label.svg` populated (no `{{` remnants); INV-14 entry in invariants[] |
| 5 | D2.2 templates/ directory present with 6 files; arc-flash-labelling pattern matched |
| 6 | D2.3 hand-check uk-mixed-use-lifts-and-ev: every circuit has `diversity_basis` with valid citation; lift + EV circuits have `factor_applied: 1.00`; INV-15 entry |
| 7 | D2.3 backport: 19 other db-layout examples carry `diversity_basis` on every circuit |
| 8 | Version + CHANGELOG sync: cable-sizing 1.1.0 / db-layout 1.4.0 (manifest tops match CHANGELOG tops) |

If ANY check fails → HALT + re-dispatch the failing implementer with detail.

### §5.6 Memory + push

After fence PASS:
1. Write `~/.claude/projects/.../memory/sprint-D2-shipped.md`
2. Update `~/.claude/projects/.../memory/MEMORY.md` index
3. `git push origin main`

---

## §6 Honest disclosures preserved

Per the established Sprint C3 + `[[feedback-no-trim-non-consequential]]` pattern, the following disclosures MUST appear in CHANGELOG + relevant reasoning.md sections:

1. **4D1A + 4D5A tables** carry `verification_status: engineer_transcription_C2`. Both uk-domestic-final-circuits (refit) and uk-rural-swa-submain (new) must cite this in `_source` and reasoning.md.
2. **OZEV CoP** is industry guidance, not statutory. Reg 722 IS statutory and references OZEV. The new example reasoning.md must distinguish.
3. **CIBSE TM50 Table 4.3** grouped-AC factor (100% + 75%): cite the table number explicitly so the engineer can verify against the CIBSE publication.
4. **IEC 60364-5-51 §514** + **IEC 61439-1 §5.5** are the IEC label standards; cited in the IEC label template and INV-14 evidence.
5. **NEC §408.4(A)** is the canonical NEC label clause; cited in the NEC label template and INV-14 evidence.

---

## §7 Risks + mitigations

| Risk | Mitigation |
|---|---|
| R1 | 4D1A refit changes ampacity values from `pvc_singles` reads to `pvc_twin_earth` reads; downstream cable-sizing intent consumers (small-power v1.1+) may see different ampacity values → cascade re-runs needed. Mitigation: cable-sizing intent is consumed-from for Zs values, not ampacity — ampacity stays internal. Verify in D2.1 implementer task. |
| R2 | SVG template authoring risk: 6 templates × jurisdictional formatting nuance. Mitigation: model after arc-flash-labelling's existing 4 templates; reuse the `{{placeholder}}` convention; Sonnet model is appropriate per the mechanical-formatting rule. |
| R3 | 20-example backport in D2.2 (label) + 19-example backport in D2.3 (diversity) is significant. Mitigation: Sonnet sub-dispatch within each task; each example is identical-shape mechanical edit; functional_audit oracle catches anything missed. |
| R4 | Diversity INV-15 Rule 4 (largest+remainder sum range [100, 200]) might be too tight if engineer-declared edge case exceeds it. Mitigation: the 100–200 range covers all documented industry methods (sockets 140 / motors 150 / AC grouped 175). If an engineer needs >200, they use `method: engineer_declared` which bypasses Rule 4. |
| R5 | INV-14 Rule 5 regex per jurisdiction may false-positive on edge cases (e.g. board with non-numeric way IDs). Mitigation: the regex matches the format the generator emits; engineer-override paths use `method: engineer_declared` (similar to R4). |

---

## §8 Out of scope for D2

- Building-level area diversity (D3 item 9)
- small-power special-locations design depth (D3 item 8)
- Any cable-sizing tables beyond 4D1A + 4D5A (4D2A/4D4A reads already work via existing logic; full transcription validation deferred)
- Any new jurisdictions beyond GB/KE/INT/US
- SVG-to-PDF rasterisation (deferred to runtime per `[[runtime-project-boundary]]`)
- Oracle-side recompute updates for `table_used` (deferred unless required to validate D2.1 outputs)

---

## §9 Commits expected (D2)

```
docs: Sprint D2 (Sizing & Boards depth) design spec
docs: Sprint D2 implementation plan
feat(cable-sizing): D2.1 PVC/SWA tables 4D1A + 4D5A consumers
fix(cable-sizing): D2.1 fix-pass — <any FIX-NEXT items>
feat(db-layout): D2.2 board + circuit labels (BS/NEC/IEC) + 6 SVG templates
fix(db-layout): D2.2 fix-pass — <any FIX-NEXT items>
feat(db-layout): D2.3 diversity edge cases — lifts + EV + AC + motors + INV-15
fix(db-layout): D2.3 fix-pass — <any FIX-NEXT items>
fix(sprint-D2): verification-fence cleanup — <if needed>
```

Estimated 8–10 commits total. After push, write sprint-D2-shipped memory.

---

## §10 Cross-references

- `[[within-skill-depth-plan]]` (the 3-sprint roadmap; D2 is the second sprint)
- `[[sprint-D1-shipped]]` (D1 ship pattern; D2 mirrors)
- `[[feedback-no-haiku-sonnet-opus-only]]` (model selection enforced)
- `[[feedback-no-trim-non-consequential]]` (honest disclosures preserved over style trims)
- `[[runtime-project-boundary]]` (calc executors + SVG rasterisation live in runtime, not skills)
- `electrical/arc-flash-labelling/templates/` (canonical SVG template pattern)
- `shared/calculations/electrical/render-label.json` (calc contract reused)
