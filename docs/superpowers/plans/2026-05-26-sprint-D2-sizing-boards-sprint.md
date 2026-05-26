# Sprint D2 — Sizing & Boards depth Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close 3 within-skill depth items across cable-sizing + db-layout (PVC/SWA tables 4D1A + 4D5A consumers; per-circuit + per-board labels with BS/NEC/IEC SVG templates; diversity edge cases for lifts + EV + AC + motor groups) before pivoting to Sprint D3 (small-power depth).

**Architecture:** Three sequential implementer tasks (D2.1 → D2.2 → D2.3), each followed by Opus spec-compliance + code-quality review, then a Sonnet 8-check verification fence (D2.4) before ship. Each item follows the same 5-step pattern (schema add → generator step → validator INV → example update → CHANGELOG patch-bump). D2.2 is Sonnet (mechanical formatting + SVG template population); D2.1 + D2.3 are Opus (table-selection judgment + regulation-driven diversity factors). Strict sequential — no parallel tasks — easier to halt mid-sprint if a downstream blocker appears.

**Tech Stack:** JSON Schema Draft-07 (IR schemas), Markdown (generator/validator/reviewer prompts), YAML (validation specs + evals), Python 3.11 (validate-examples.py + functional_audit.py), SVG (label templates per arc-flash-labelling pattern).

**Spec:** `docs/superpowers/specs/2026-05-26-sprint-D2-sizing-boards-depth-design.md` (commit `c7caa28`).

**INV numbering resolved (from current validator.md counts):**
- cable-sizing: 11 existing → new is **INV-12** (cable_type ↔ table_used)
- db-layout: 13 existing → new are **INV-14** (label format) → **INV-15** (diversity basis)

**Version bumps:**
- cable-sizing: `[1.0.2]` → `[1.1.0]` (minor — new cable_type enum + table_used + INV-12 + new example)
- db-layout: `[1.3.3]` → `[1.4.0]` (minor — single bump after D2.2 + D2.3 both ship)

**Gates target:** validate-examples 225/225 (current 221 + uk-rural-swa-submain ×2 + uk-mixed-use-lifts-and-ev ×2); functional_audit 1 finding unchanged (motor-superposition oracle FP on us-industrial-with-motors/MCC-1 — disclosed in D1.1).

---

## File Structure

### Modified

- `electrical/cable-sizing/schemas/cable-sizing-ir.schema.json` — D2.1: extend `cable_type` enum (+ `pvc_twin_earth`, `pvc_swa`); add `table_used` field on cable-bearing cascade nodes
- `electrical/cable-sizing/prompts/generator.md` — D2.1: new step covering table-selection walk
- `electrical/cable-sizing/prompts/validator.md` — D2.1: add INV-12
- `electrical/cable-sizing/examples/uk-domestic-final-circuits/output.json` — D2.1: refit to `pvc_twin_earth` + `table_used: "4D1A"`
- `electrical/cable-sizing/examples/uk-domestic-final-circuits/reasoning.md` — D2.1: narrate the table walk + Sprint C.2 honesty disclosure
- `electrical/cable-sizing/CHANGELOG.md` — D2.1 entry; bump 1.0.2 → 1.1.0
- `electrical/cable-sizing/skill.manifest.json` — version sync + register new example
- `electrical/db-layout/schemas/db-layout-ir.schema.json` — D2.2: add `label_format_standard` + `board_label` + per-circuit `circuit_label`; D2.3: add per-circuit `diversity_basis` block
- `electrical/db-layout/prompts/generator.md` — D2.2: new label-population step; D2.3: extend per-load-type diversity table with 4 new rows + tighten 2 citations
- `electrical/db-layout/prompts/validator.md` — D2.2: add INV-14; D2.3: add INV-15
- `electrical/db-layout/examples/*/output.json` (20 total) — D2.2: backport labels; D2.3: backport diversity_basis on every circuit
- `electrical/db-layout/CHANGELOG.md` — combined D2.2 + D2.3 entry; bump 1.3.3 → 1.4.0
- `electrical/db-layout/skill.manifest.json` — version sync + add render-label calc + register new example

### Created

- `electrical/cable-sizing/examples/uk-rural-swa-submain/input.json` — D2.1 new example input
- `electrical/cable-sizing/examples/uk-rural-swa-submain/output.json` — D2.1 4D5A direct-buried 25 mm² submain
- `electrical/cable-sizing/examples/uk-rural-swa-submain/intent-out.json` — D2.1 new example emitted intent
- `electrical/cable-sizing/examples/uk-rural-swa-submain/reasoning.md` — D2.1 worked example narrative
- `electrical/db-layout/templates/bs-7671-circuit-label.svg.template` — D2.2 BS strip-label
- `electrical/db-layout/templates/nec-408-4-circuit-label.svg.template` — D2.2 NEC strip-label
- `electrical/db-layout/templates/iec-60364-5-51-circuit-label.svg.template` — D2.2 IEC strip-label
- `electrical/db-layout/templates/bs-7671-board-label.svg.template` — D2.2 BS board headline
- `electrical/db-layout/templates/nec-408-4-board-label.svg.template` — D2.2 NEC board headline
- `electrical/db-layout/templates/iec-60364-5-51-board-label.svg.template` — D2.2 IEC board headline
- `electrical/db-layout/examples/uk-mixed-use-lifts-and-ev/input.json` — D2.3 new example input
- `electrical/db-layout/examples/uk-mixed-use-lifts-and-ev/output.json` — D2.3 demonstrating lifts + EV + AC + motors diversity
- `electrical/db-layout/examples/uk-mixed-use-lifts-and-ev/intent-out.json` — D2.3 emitted intent
- `electrical/db-layout/examples/uk-mixed-use-lifts-and-ev/reasoning.md` — D2.3 worked example narrative
- Memory file `sprint-D2-shipped.md` at `~/.claude/projects/-Users-linus-Desktop-DraftsMan-SKills-draftsman-skills/memory/`

---

## Task D2.1: cable-sizing PVC/SWA edge cases — 4D1A + 4D5A consumers (Opus)

**Why Opus:** Table-selection engineering judgment + new worked example with hand-computed 4D5A direct-buried ampacity + voltage-drop arithmetic. Per `[[feedback-no-haiku-sonnet-opus-only]]` model selection rule.

**Files:**
- Modify: `electrical/cable-sizing/schemas/cable-sizing-ir.schema.json` — extend cable_type enum + add table_used field
- Modify: `electrical/cable-sizing/prompts/generator.md` — append new step
- Modify: `electrical/cable-sizing/prompts/validator.md` — append INV-12
- Modify: `electrical/cable-sizing/examples/uk-domestic-final-circuits/output.json` + `reasoning.md` — refit to 4D1A
- Modify: `electrical/cable-sizing/CHANGELOG.md` + `skill.manifest.json` — version sync
- Create: 4 files at `electrical/cable-sizing/examples/uk-rural-swa-submain/` — new example

- [ ] **Step 1: Read current cable-sizing IR schema**

Read `electrical/cable-sizing/schemas/cable-sizing-ir.schema.json`. Locate the `selection.cable_type` enum (currently lists: `pvc_singles`, `pvc_multicore`, `xlpe_swa`, `xlpe_lszh`, `epr_swa`, `mineral_micc`, `fp200_lszh`, `cwz_glass_mica`, `thwn_2`, `thhn`, `xhhw_2`). Locate the `route.installation_method` enum (currently lists: `A1, A2, B1, B2, C, D1, D2, E, F, G, nec_conduit, nec_cable_tray, nec_direct_burial, nec_free_air`). Note there is currently NO `table_used` field anywhere in the schema.

- [ ] **Step 2: Extend cable_type enum**

Edit `electrical/cable-sizing/schemas/cable-sizing-ir.schema.json`. Find `selection.cable_type.enum` array and append two new values (additive, no removals):

```json
"cable_type": {
  "enum": [
    "pvc_singles",
    "pvc_twin_earth",
    "pvc_multicore",
    "pvc_swa",
    "xlpe_swa",
    "xlpe_lszh",
    "epr_swa",
    "mineral_micc",
    "fp200_lszh",
    "cwz_glass_mica",
    "thwn_2",
    "thhn",
    "xhhw_2"
  ]
}
```

- [ ] **Step 3: Add table_used field on cable-bearing cascade nodes**

In the same schema file, find the `selection` object's `properties` block (sibling to `cable_type`). Add `table_used`:

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
  "description": "Reference ampacity table consulted for the cable walk. `none` for jurisdictions without a tabular reference. Required when route.installation_method is set. Cite the matching table identifier + method in the example's `_source`. Added Sprint D2.1."
}
```

Find the `selection.required` array and append `"table_used"` to it (alongside existing `phase_csa, cpc_csa, material, insulation, cable_type, parallel_count, binding_constraint, walk_up_trail`). The cable_type compatibility matrix lives in the generator step (Step 4 below); INV-12 enforces (Step 5).

- [ ] **Step 4: Append generator step to cable-sizing/prompts/generator.md**

Read `electrical/cable-sizing/prompts/generator.md`. Locate the last numbered step (search for `^### Step` and count). Append a new step at the end (before any final "Output" section):

```markdown
### Step <N>: Table selection walk (D2.1)

For every cable-bearing cascade node (i.e. every node with a `selection.cable_type` set), explicitly identify the reference ampacity table consulted. Emit the `table_used` enum value AND cite it in the `_source` field for that cable.

**cable_type → table_used compatibility matrix (BS 7671 / IEC 60364-5-52):**

| cable_type | Primary table | Methods supported |
|---|---|---|
| `pvc_twin_earth` (UK domestic T&E) | **4D1A** | C, A1 (=A), 100, 101, 102, 103 |
| `pvc_singles` (single insulated cores in conduit) | **4D2A** | B1, B2 |
| `pvc_multicore` (multicore PVC) | **4D4A** | C, E, F |
| `pvc_swa` (multicore PVC SWA armoured) | **4D5A** | C (clipped), D (direct-buried), E (cable tray) |
| `xlpe_swa` (multicore XLPE SWA armoured) | **4E5A** | C, D, E |
| `xlpe_lszh` (multicore XLPE LSZH) | **4E2A** or **4E4A** | B1, C, E, F |
| `epr_swa` | **4E5A** (EPR uses XLPE ampacity bands) | C, D, E |
| `mineral_micc` | bespoke MICC tables (not 4D-series) | engineer-declared |

**For NEC jurisdictions (US):**

| cable_type | Primary table | Methods supported |
|---|---|---|
| `thwn_2` / `thhn` (75°C insulation conduit-installed) | **nec_310_16_75** | nec_conduit |
| `xhhw_2` (90°C insulation cable-tray) | **nec_310_16_90** | nec_cable_tray, nec_free_air |
| `thwn_2` direct-buried | **nec_310_16_60** | nec_direct_burial (60°C-corrected per NEC §310.15(B)) |

**For IEC jurisdictions (INT/EU):**

| cable_type | Primary table | Methods supported |
|---|---|---|
| `pvc_singles` / `pvc_multicore` | **iec_60364_5_52_b1** (conduit) or **iec_60364_5_52_e** (cable tray) | B1, E |
| `xlpe_swa` / `xlpe_lszh` | **iec_60364_5_52_f** (free air / cable tray) | F, E |

**Set `selection.table_used`** to the table identifier from the matrix above. Set `_source` (sibling to `cable_type`) to `"BS 7671:2018+A2:2022 App 4 Table {table_used} method {installation_method}"` (or NEC/IEC equivalent for those jurisdictions).

**Honest disclosure (Sprint C.2 transcription):** Tables 4D1A + 4D5A under `shared/standards/electrical/BS7671/` carry `verification_status: engineer_transcription_C2` per the Sprint C.2 transcription pass. When the example consumes these tables, the example's `reasoning.md` MUST cite this status honestly (e.g. "Per Sprint C.2 disclosure, 4D1A values were engineer-transcribed from industry-standard references; verify against the published BS 7671:2018+A2:2022 edition before runtime use.").

**Validator INV-12 enforces** the cable_type ↔ table_used pairing + the method-compatibility check.
```

- [ ] **Step 5: Append INV-12 to cable-sizing/prompts/validator.md**

Read `electrical/cable-sizing/prompts/validator.md`. Locate the last INV (search for `^### INV-`). Append after INV-11:

```markdown

---

### INV-12: cable_type ↔ table_used consistency (D2.1)

**Severity:** HIGH

**Rule:** For every cascade node carrying `selection.cable_type` AND `route.installation_method`:

1. **Compatibility:** `cable_type` maps to a specific `table_used` value per the matrix in generator Step <N>:
   - `pvc_twin_earth` → `4D1A` (only)
   - `pvc_singles` → `4D2A` (or `4D4A` if multicore variant)
   - `pvc_multicore` → `4D4A`
   - `pvc_swa` → `4D5A` (only)
   - `xlpe_swa` → `4E5A`
   - `xlpe_lszh` → `4E2A` or `4E4A`
   - `thwn_2`/`thhn` → `nec_310_16_75` (or `nec_310_16_60` if direct-buried)
   - `xhhw_2` → `nec_310_16_90`
   - `pvc_singles`/`pvc_multicore` in IEC → `iec_60364_5_52_b1` or `iec_60364_5_52_e`
   - `xlpe_swa`/`xlpe_lszh` in IEC → `iec_60364_5_52_f`
   Mismatch (e.g. `cable_type: pvc_twin_earth` with `table_used: 4D5A`) is a HIGH violation.

2. **Method validity:** The chosen `table_used` must list `route.installation_method` in its `installation_methods` block (per the source table file under `shared/standards/electrical/BS7671/` or `shared/standards/electrical/IEC60364/` or `shared/standards/electrical/NFPA70/`). For example, `4D1A` lists `{C, A1, 100, 101, 102, 103}` — a cable claiming `table_used: 4D1A` with `installation_method: F` is invalid.

3. **Citation:** Every cable's `_source` cites the same `table_used` + `installation_method` (string-match required). Format: `"BS 7671:2018+A2:2022 App 4 Table {table_used} method {installation_method}"` (or NEC/IEC equivalent).

4. **Engineer-transcription disclosure:** When `table_used ∈ {4D1A, 4D5A}`, the example's `reasoning.md` MUST include a sentence citing the Sprint C.2 transcription disclosure (`verification_status: engineer_transcription_C2`). This is a content check on reasoning.md, not on the IR — but a HIGH violation if absent, because the runtime consumer of these examples must surface the honesty disclosure to the engineer.

**Validator action:** for each cascade node with both `cable_type` and `installation_method`, walk the compatibility matrix; check `table_used` is in the allowed set; verify method belongs to that table; verify `_source` cites the same pair; for 4D1A / 4D5A consumers, check reasoning.md contains the disclosure phrase.

**Rationale:** Tables 4D1A + 4D5A were transcribed in Sprint C.2 but have shipped without consumers for 4 days. The `table_used` field makes the chosen table audit-traceable, prevents the silent mismatch (cable physically T&E but cited against generic pvc_singles table), and forces the honest Sprint C.2 disclosure to surface on every example that consumes the engineer-transcribed tables.
```

- [ ] **Step 6: Refit uk-domestic-final-circuits to 4D1A**

Read `electrical/cable-sizing/examples/uk-domestic-final-circuits/output.json`. Identify every cascade node where `selection.cable_type == "pvc_singles"` AND the physical context is a UK domestic final circuit (ring final, radial socket, lighting, cooker, shower). These are physically twin-and-earth cables.

For each such node:

1. Change `selection.cable_type` from `"pvc_singles"` to `"pvc_twin_earth"`.
2. Add `selection.table_used: "4D1A"`.
3. Add `selection.cable_source: "BS 7671:2018+A2:2022 App 4 Table 4D1A method <installation_method>"` (or use the existing `_source` field if present; check the schema).
4. Verify `route.installation_method` is one of `{C, A1, 100, 101, 102, 103}`. If currently `B1` (singles in conduit, wrong for T&E), change to `C` (clipped direct, the canonical UK domestic T&E case).
5. Refresh `iz_corrected_a` per the 4D1A column read. Reference values for 1-loaded-pair (single-phase ring or radial):
   - 1.0 mm² method C: 15 A → derate for ambient 30°C (Ca=1.0) + grouping (Cg per Table 4C1) + thermal insulation (Ci per OSG Table 7A.2 if method 100–103)
   - 1.5 mm² method C: 19.5 A
   - 2.5 mm² method C: 27 A
   - 4 mm² method C: 36 A
   - 6 mm² method C: 46 A
   - 10 mm² method C: 63 A
   - 16 mm² method C: 85 A
   - For method 102 (stud wall with insulation on one side): 2.5 mm² = 19.5 A; 4 mm² = 26 A; 6 mm² = 32 A
6. Update each node's `walk_up_trail[*].iz_corrected_a` to match the new value.
7. Re-verify `iz_vs_in_pass` (Iz ≥ In) and `vd_pass` (cumulative Vd ≤ 5% per BS 7671 App 12). If any check now fails, document the upsizing in the walk_up_trail and re-emit the binding_constraint.

DO NOT change feeders or sub-mains in this example that are genuinely `pvc_singles` (singles in conduit are still valid for some MSB / sub-DB feeders). Only the FINAL CIRCUITS (ring/radial/lighting/cooker/shower) refit to T&E.

Update each cascade node's `invariants[]` entry (or add a new INV-12 entry at IR root level):

```json
{
  "id": "INV-12",
  "passes": true,
  "severity": "high",
  "evidence": "Cable_type pvc_twin_earth maps to table_used 4D1A per BS 7671:2018+A2:2022 App 4 + Sprint D2.1 compatibility matrix. Method C (clipped direct) and methods 100-103 (UK-domestic thermal-insulation variants) are listed in 4D1A.installation_methods. Citation in _source matches. Reasoning.md cites Sprint C.2 engineer_transcription_C2 disclosure for 4D1A."
}
```

- [ ] **Step 7: Update uk-domestic-final-circuits reasoning.md**

Read `electrical/cable-sizing/examples/uk-domestic-final-circuits/reasoning.md`. Add a new section (or extend an existing one) titled "Table selection walk":

```markdown
## Table selection walk (Sprint D2.1)

UK domestic final circuits use flat twin-and-earth (T&E) cable —
70°C PVC insulated, two-core plus reduced-section CPC, copper,
unarmoured. Per the BS 7671:2018+A2:2022 Appendix 4 walk-the-ladder
convention, the canonical ampacity table for T&E is **Table 4D1A**.

This example refits the prior `pvc_singles` declaration (which would
direct the engineer to Table 4D2A — singles in conduit, the wrong
construction) to `pvc_twin_earth` + `table_used: 4D1A`, with
`installation_method: C` (clipped direct to non-metallic surface,
the canonical UK domestic surface-clipped case).

Ampacity column reads per 4D1A method C (one twin-pair loaded):
- 1.5 mm² → 19.5 A (lighting circuit, In ≤ 6 A → ample headroom)
- 2.5 mm² → 27 A (ring final In = 32 A; ring shares load across two
  legs so the 27 A per-leg capacity supports 32 A circuit current
  per BS 7671 Reg 433.1.5 ring-final rule)
- 4 mm² → 36 A (radial socket In ≤ 32 A → ample headroom)
- 6 mm² → 46 A (cooker In ≤ 45 A → headroom 1 A; check vd)
- 10 mm² → 63 A (shower In ≤ 45 A → ample headroom)

**Honest disclosure (Sprint C.2 transcription).** Table 4D1A under
`shared/standards/electrical/BS7671/appendix4-table-4D1A-pvc-twin-earth.json`
carries `verification_status: engineer_transcription_C2`. The
ampacity values cited above were engineer-transcribed from
industry-standard references during the Sprint C.2 remediation pass;
the engineer-of-record MUST verify against the published BS
7671:2018+A2:2022 edition before runtime use. INV-12 Rule 4
enforces this disclosure on every example consuming 4D1A.
```

- [ ] **Step 8: Create new example uk-rural-swa-submain — input.json**

Create directory `electrical/cable-sizing/examples/uk-rural-swa-submain/`. Write `input.json`:

```json
{
  "$schema": "../../inputs.json",
  "skill": "cable-sizing",
  "example_id": "uk-rural-swa-submain",
  "jurisdiction": "GB",
  "items": [
    {
      "id": "I-1",
      "category": "site_brief",
      "label": "Site description",
      "value": "Rural property, UK. 100 A single-phase 230 V supply at the main service entrance head. Standalone outbuilding 100 m from the main dwelling requires its own 100 A sub-distribution board (SDB). The submain runs direct-buried (0.6 m depth, undisturbed soil, thermal resistivity 2.5 K·m/W per BS 7671 App 4 §2.4) from the main service to the outbuilding SDB. This study sizes the SWA submain per BS 7671:2018+A2:2022 Appendix 4 Table 4D5A."
    },
    {
      "id": "I-2",
      "category": "cable",
      "label": "Cable specification",
      "value": {
        "cable_type": "pvc_swa",
        "material": "copper",
        "insulation": "pvc_70",
        "armouring": "steel_wire",
        "cores": 2,
        "phase_arrangement": "single_phase"
      }
    },
    {
      "id": "I-3",
      "category": "route",
      "label": "Route data",
      "value": {
        "length_m": 100,
        "installation_method": "D1",
        "ambient_c": 15,
        "soil_thermal_resistivity_k_m_w": 2.5,
        "burial_depth_m": 0.6,
        "grouping_count": 1
      }
    },
    {
      "id": "I-4",
      "category": "load",
      "label": "Sub-DB load",
      "value": {
        "in_a": 100,
        "ib_a": 80,
        "phases": "single",
        "pf": 0.9
      }
    },
    {
      "id": "I-5",
      "category": "method_preference",
      "label": "Calculation method",
      "value": "BS 7671:2018+A2:2022 Appendix 4 Table 4D5A Method D (direct-buried, two-core PVC SWA, copper). Voltage drop per Appendix 12. Adiabatic CPC check per Reg 543.1.3 using the SWA armour as CPC per Reg 543.2.5."
    }
  ]
}
```

- [ ] **Step 9: Create uk-rural-swa-submain output.json**

Write `electrical/cable-sizing/examples/uk-rural-swa-submain/output.json`. Hand-compute the ampacity walk:

**Ampacity walk per BS 7671:2018+A2:2022 Table 4D5A method D, 2-core SWA copper, direct-buried, soil 2.5 K·m/W:**

| csa | Iz_base (A) | Ca (ambient 15°C ÷ 20°C ref) | Cg (single) | Ci (none for buried) | Iz_corrected (A) |
|---|---|---|---|---|---|
| 16 mm² | 87 | 1.07 | 1.00 | 1.00 | 93.1 |
| **25 mm² | 112** | 1.07 | 1.00 | 1.00 | **119.8** |
| 35 mm² | 135 | 1.07 | 1.00 | 1.00 | 144.5 |

Per BS 7671 App 4 Table 4B2 (Ca for ambient ≠ 20°C reference for buried cables PVC), at 15°C the factor is ~1.07. For 100 A In on 25 mm² Iz=120 A, headroom is 19 A (16% margin). Walk-up trail:

- 16 mm² (Iz 93 A) — REJECTED: Iz < In (93 < 100).
- 25 mm² (Iz 120 A) — ACCEPTED: Iz ≥ In; check vd next.

**Voltage drop per BS 7671 App 12, Table 4D5A mVAm column:**

For 25 mm² 2-core PVC SWA single-phase, the mVAm value from 4D5A is **1.8 mV/A/m**.

```
Vd = (mVAm × L × Ib) / 1000
   = (1.8 × 100 × 80) / 1000
   = 14.4 V
Vd_pct = (14.4 / 230) × 100 = 6.26%
```

6.26% > 3% (per BS 7671 App 12 §6.4 power circuits limit) → REJECTED on voltage drop. Walk up to 35 mm²:

For 35 mm² 2-core PVC SWA single-phase, the mVAm value from 4D5A is **1.25 mV/A/m**.

```
Vd = (1.25 × 100 × 80) / 1000 = 10.0 V
Vd_pct = (10.0 / 230) × 100 = 4.35%
```

4.35% > 3% → still REJECTED on power-circuit limit. Walk up to 50 mm²:

For 50 mm² 2-core PVC SWA single-phase, the mVAm value from 4D5A is **0.93 mV/A/m**.

```
Vd = (0.93 × 100 × 80) / 1000 = 7.44 V
Vd_pct = (7.44 / 230) × 100 = 3.23%
```

3.23% still > 3%. Walk up to 70 mm²:

For 70 mm² 2-core PVC SWA single-phase, the mVAm value from 4D5A is **0.63 mV/A/m**.

```
Vd = (0.63 × 100 × 80) / 1000 = 5.04 V
Vd_pct = (5.04 / 230) × 100 = 2.19%
```

2.19% ≤ 3% → ACCEPTED on voltage drop. Iz at 70 mm² (Iz_base 195 A × Ca 1.07 = 208.7 A) ≫ In 100 A — ample ampacity headroom; binding_constraint = `vd_cumulative`.

**CPC adiabatic check per Reg 543.1.3 / Table 54.7:** The SWA armour acts as CPC per Reg 543.2.5. For 70 mm² 2-core SWA the steel wire armour has a CSA roughly equivalent to 35–50 mm² copper for adiabatic purposes (per BS 7671 Table 54.7 + manufacturer data). With t_clear ≈ 0.4 s and Ik upstream ≈ 6 kA, adiabatic check: k=46 for steel armour, S_cpc_min = √(I²t)/k = √(6000² × 0.4)/46 = √(14.4M)/46 = 3795/46 = 82.5 mm² required — but the steel armour CSA on 70 mm² 2-core SWA is ~50 mm² steel which equates to ~22 mm² copper-equivalent. **CPC adiabatic FAILS** with armour-only CPC. Add a separate 25 mm² copper CPC per Reg 543.2.5 alternative — single-CPC route. Re-check: 25 mm² Cu CPC, k=143 for Cu/PVC, S_cpc_min = 3795/143 = 26.5 mm² → 25 mm² is JUST short; upsize CPC to 35 mm² Cu (k×S = 143×35 = 5005 A ≥ √(6000²×0.4) = 3795 ✓).

The output.json:

```json
{
  "$schema": "../../schemas/cable-sizing-ir.schema.json",
  "drawing_type": "cable_sizing_cascade",
  "version": "1.1.0",
  "meta": {
    "project_id": "uk-rural-swa-submain",
    "skill_version": "cable-sizing/1.1.0",
    "produced_at": "2026-05-26T10:00:00Z",
    "consumed_intents": []
  },
  "jurisdiction": "GB",
  "project_supply": {
    "voltage_v": 230,
    "phase_arrangement": "single_phase",
    "system_type": "TN-S"
  },
  "cascade": [
    {
      "node_id": "SERVICE-IN",
      "parent_node_id": null,
      "node_kind": "service_entrance",
      "designation": "Main service entrance — 100 A SP&N",
      "load": {"ib_a": 80, "in_a": 100, "phases": "single", "load_type": "submain_feeder", "pf": 0.9}
    },
    {
      "node_id": "SUBMAIN-CABLE",
      "parent_node_id": "SERVICE-IN",
      "node_kind": "submain_cable",
      "designation": "100 m direct-buried PVC SWA submain to outbuilding SDB",
      "load": {"ib_a": 80, "in_a": 100, "phases": "single", "load_type": "submain_feeder", "pf": 0.9},
      "route": {
        "length_m": 100,
        "installation_method": "D1",
        "ambient_c": 15,
        "soil_thermal_resistivity_k_m_w": 2.5,
        "burial_depth_m": 0.6,
        "grouping_count": 1
      },
      "parent_node_ifault_ka": 6.0,
      "t_clear_s": 0.4,
      "selection": {
        "phase_csa": 70,
        "cpc_csa": 35,
        "cpc_provision": "separate_copper_cpc_per_reg_543_2_5",
        "material": "copper",
        "insulation": "pvc_70",
        "cable_type": "pvc_swa",
        "table_used": "4D5A",
        "_source": "BS 7671:2018+A2:2022 App 4 Table 4D5A method D",
        "parallel_count": 1,
        "binding_constraint": "vd_cumulative",
        "walk_up_trail": [
          {"csa_attempted": 16, "accepted": false, "iz_corrected_a": 93.1, "reject_reason": "Iz 93.1 < In 100"},
          {"csa_attempted": 25, "accepted": false, "iz_corrected_a": 119.8, "vd_segment_pct": 6.26, "vd_cumulative_pct": 6.26, "reject_reason": "Vd 6.26% > 3% power-circuit limit"},
          {"csa_attempted": 35, "accepted": false, "iz_corrected_a": 144.5, "vd_segment_pct": 4.35, "vd_cumulative_pct": 4.35, "reject_reason": "Vd 4.35% > 3% power-circuit limit"},
          {"csa_attempted": 50, "accepted": false, "iz_corrected_a": 181.5, "vd_segment_pct": 3.23, "vd_cumulative_pct": 3.23, "reject_reason": "Vd 3.23% > 3% power-circuit limit"},
          {"csa_attempted": 70, "accepted": true, "iz_corrected_a": 208.7, "vd_segment_pct": 2.19, "vd_cumulative_pct": 2.19}
        ]
      },
      "checks": {
        "iz_corrected_a": 208.7,
        "iz_vs_in_pass": true,
        "vd_segment_pct": 2.19,
        "vd_cumulative_pct": 2.19,
        "vd_limit_pct": 3.0,
        "vd_limit_source": "BS 7671:2018+A2:2022 App 12 §6.4 power circuits 3%",
        "vd_pass": true,
        "cpc_adiabatic_pass": true,
        "cpc_adiabatic_source": "BS 7671:2018+A2:2022 Reg 543.1.3 + Reg 543.2.5 (SWA armour insufficient as CPC; separate 35 mm² Cu CPC routed per Reg 543.2.5 alternative). Adiabatic k×S = 143 × 35 = 5005 ≥ √(I²t) = √(6000² × 0.4) = 3795. PASS.",
        "motor_starting_vd_pct": null,
        "motor_starting_vd_pass": null,
        "tool_call_pending": true
      }
    },
    {
      "node_id": "OUT-DB",
      "parent_node_id": "SUBMAIN-CABLE",
      "node_kind": "sub_distribution_board",
      "designation": "Outbuilding SDB — 100 A SP&N",
      "load": {"ib_a": 80, "in_a": 100, "phases": "single", "load_type": "sub_distribution", "pf": 0.9}
    }
  ],
  "compliance_summary": {
    "compliant": true,
    "non_compliance_flags": []
  },
  "flags": [],
  "rationale": {
    "chat_summary": "100 m direct-buried PVC SWA submain from 100 A service entrance to rural outbuilding SDB. Per BS 7671:2018+A2:2022 App 4 Table 4D5A method D (direct-buried, soil 2.5 K·m/W, ambient 15°C). Walk-up: 16/25/35/50 mm² all rejected on vd limit (3% power-circuit per App 12 §6.4); 70 mm² accepted at vd 2.19%. SWA armour insufficient as CPC for 6 kA × 0.4 s adiabatic — separate 35 mm² Cu CPC required per Reg 543.2.5 alternative.",
    "sections": [
      {"title": "Why 4D5A method D", "summary": "Multicore PVC SWA cable, 2-core single-phase, direct-buried 0.6 m depth in undisturbed soil — method D is the canonical BS 7671 App 4 reference per Table 4D5A's installation_methods block."},
      {"title": "Walk-up rationale", "summary": "Iz acceptance at 25 mm² (120 A ≥ 100 A In) but vd 6.26% fails the App 12 §6.4 power-circuit 3% limit. Walked up through 35/50/70 mm²; binding_constraint is vd_cumulative, not iz_vs_in."},
      {"title": "CPC alternative per Reg 543.2.5", "summary": "SWA armour CSA on 70 mm² 2-core ≈ 50 mm² steel (k=46) — adiabatic 46 × 50 = 2300 < 3795 required (6 kA × 0.4 s). Per Reg 543.2.5, a separate copper CPC may be routed. Selected 35 mm² Cu CPC (k=143 × 35 = 5005 ≥ 3795). PASS."},
      {"title": "Sprint C.2 transcription honesty disclosure", "summary": "Table 4D5A values used in this example were engineer-transcribed during Sprint C.2 from industry-standard references; the source file carries verification_status: engineer_transcription_C2. Engineer-of-record MUST verify against the published BS 7671:2018+A2:2022 edition before runtime use. INV-12 Rule 4 enforces this disclosure."}
    ]
  },
  "invariants": [
    {
      "id": "INV-12",
      "passes": true,
      "severity": "high",
      "evidence": "cable_type pvc_swa maps to table_used 4D5A per BS 7671:2018+A2:2022 App 4 + Sprint D2.1 compatibility matrix (Rule 1 PASS). Method D (direct-buried) is listed in 4D5A.installation_methods alongside method C (Rule 2 PASS). _source string 'BS 7671:2018+A2:2022 App 4 Table 4D5A method D' matches the (cable_type, installation_method) pair (Rule 3 PASS). reasoning.md cites the Sprint C.2 engineer_transcription_C2 disclosure (Rule 4 PASS)."
    }
  ]
}
```

- [ ] **Step 10: Create uk-rural-swa-submain intent-out.json**

Write `electrical/cable-sizing/examples/uk-rural-swa-submain/intent-out.json`. Read the existing intent shape from a sibling example (e.g. `electrical/cable-sizing/examples/uk-domestic-final-circuits/intent-out.json`) to learn the canonical shape, then mirror it. Typical shape:

```json
{
  "$schema": "../../schemas/cable-sizing-intent.schema.json",
  "intent_type": "cable-sizing",
  "intent_version": "1.0.0",
  "produced_by": "electrical/cable-sizing/v1.1.0",
  "payload": {
    "project_id": "uk-rural-swa-submain",
    "jurisdiction": "GB",
    "cables": [
      {
        "node_id": "SUBMAIN-CABLE",
        "phase_csa_mm2": 70,
        "cpc_csa_mm2": 35,
        "cable_type": "pvc_swa",
        "table_used": "4D5A",
        "iz_corrected_a": 208.7,
        "vd_cumulative_pct": 2.19,
        "binding_constraint": "vd_cumulative"
      }
    ]
  }
}
```

If the intent schema's exact shape differs from this template (e.g. uses `cables[*].selection` instead of flat fields), match the actual schema. Verify by reading `electrical/cable-sizing/schemas/cable-sizing-intent.schema.json` first.

- [ ] **Step 11: Create uk-rural-swa-submain reasoning.md**

Write `electrical/cable-sizing/examples/uk-rural-swa-submain/reasoning.md` (~150 lines). Structure:

```markdown
# uk-rural-swa-submain — Reasoning

100 m direct-buried PVC SWA submain feeding a 100 A SP&N outbuilding
SDB from a rural property's main service entrance. Per BS
7671:2018+A2:2022 Appendix 4 Table 4D5A method D.

## Site brief

Rural property, single-phase 230 V supply at main service entrance.
Standalone outbuilding 100 m from the dwelling requires its own SDB
(workshop / studio / outbuilding scenario). Cable runs direct-buried
at 0.6 m depth, undisturbed soil (thermal resistivity 2.5 K·m/W per
BS 7671 App 4 §2.4 default).

## Why table 4D5A method D

Multicore PVC SWA cable, 2-core single-phase, copper. Per BS 7671
App 4 Table 4D5A `installation_methods` block:
- Method C: clipped direct to non-metallic surface or on cable tray
- **Method D: direct buried in ground (0.5–0.7 m, soil 2.5 K·m/W)**

Method D matches the install context exactly.

## Walk-up walk

**Iz acceptance test (Reg 433.1.1):** Iz_corrected ≥ In = 100 A.

[Insert table with 16/25/35/50/70 mm² walk per Step 9's hand-computed
values, plus brief rejection rationale per row]

**Voltage drop test (App 12 §6.4 power 3% limit):**

The 100 m run drives the vd binding-constraint. mVAm reads from 4D5A:

- 25 mm²: 1.8 mV/A/m → 6.26% (FAIL)
- 35 mm²: 1.25 mV/A/m → 4.35% (FAIL)
- 50 mm²: 0.93 mV/A/m → 3.23% (FAIL)
- **70 mm²: 0.63 mV/A/m → 2.19% (PASS)**

Selected: **70 mm² 2-core PVC SWA**, binding_constraint = vd_cumulative.

## CPC alternative per Reg 543.2.5

SWA armour CSA on a 70 mm² 2-core cable ≈ 50 mm² steel. Adiabatic
check (k=46 for steel armour per BS 7671 Table 54.7):

```
k × S = 46 × 50 = 2300
Required = √(I²t) = √(6000² × 0.4) = √14,400,000 = 3795 A·s^0.5
2300 < 3795 → adiabatic FAILS with armour-only CPC
```

Per Reg 543.2.5, a separate copper CPC may be routed alongside the
SWA cable. Selected 35 mm² Cu CPC:

```
k × S = 143 × 35 = 5005 ≥ 3795 ✓ PASS
```

Total cable + CPC: 70 mm² 2-core PVC SWA + 35 mm² separate Cu CPC.

## Sprint C.2 honesty disclosure

Table 4D5A under
`shared/standards/electrical/BS7671/appendix4-table-4D5A-pvc-swa.json`
carries `verification_status: engineer_transcription_C2`. The mVAm
and ampacity values cited in this worked example were
engineer-transcribed from industry-standard references during the
Sprint C.2 remediation pass. The engineer-of-record MUST verify
against the published BS 7671:2018+A2:2022 edition before runtime
use.

INV-12 Rule 4 enforces this disclosure on every example consuming
4D5A. See `electrical/cable-sizing/prompts/validator.md` INV-12.

## Operational summary

| Field | Value |
|---|---|
| cable_type | pvc_swa |
| table_used | 4D5A |
| installation_method | D1 (direct-buried) |
| phase_csa | 70 mm² |
| cpc_csa | 35 mm² (separate copper CPC per Reg 543.2.5) |
| iz_corrected | 208.7 A |
| In | 100 A |
| vd_cumulative | 2.19% |
| vd_limit | 3.0% |
| binding_constraint | vd_cumulative |
```

- [ ] **Step 12: Update CHANGELOG**

Edit `electrical/cable-sizing/CHANGELOG.md`. Add a new top entry:

```markdown
## [1.1.0] - 2026-05-26 — Sprint D2.1 PVC/SWA edge cases (4D1A + 4D5A consumers)

### Added
- **cable_type enum** extended with `pvc_twin_earth` and `pvc_swa`
  (additive; existing 11 values unchanged).
- **`table_used` field** on every cable-bearing cascade node; enum
  references BS 7671 4D-series, NEC 310.16 columns, IEC 60364-5-52
  tables. Required when `route.installation_method` is set.
- **Validator INV-12: cable_type ↔ table_used consistency** (HIGH).
  Asserts the compatibility matrix (pvc_twin_earth → 4D1A only,
  pvc_swa → 4D5A only, etc.), method validity (the method must be
  listed in the table's installation_methods block), citation
  consistency in `_source`, and the engineer-transcription disclosure
  on examples consuming 4D1A or 4D5A.

### Generator prompt
- New step (table-selection walk) added at end of flow with the full
  cable_type → table_used compatibility matrix for BS 7671 / NEC /
  IEC jurisdictions.

### Examples
- **Refit** `uk-domestic-final-circuits/`: final circuits (ring,
  lighting, cooker, shower) switched from `pvc_singles` (incorrect
  — these are physically T&E) to `pvc_twin_earth` + `table_used:
  "4D1A"` + `installation_method: C`. Ampacity values refreshed
  per 4D1A column reads. reasoning.md narrates the table walk + the
  Sprint C.2 engineer_transcription_C2 honesty disclosure.
- **NEW example** `uk-rural-swa-submain/`: 100 m direct-buried PVC
  SWA submain feeding a 100 A SP&N outbuilding SDB. Exercises Table
  4D5A method D (direct-buried, soil 2.5 K·m/W). Walk-up rejected
  16/25/35/50 mm² on vd 3% power-circuit limit; selected 70 mm² at
  vd 2.19%. CPC alternative per Reg 543.2.5 — separate 35 mm² Cu
  CPC (SWA armour insufficient for 6 kA × 0.4 s adiabatic).

### Honest disclosure
- Tables 4D1A + 4D5A under `shared/standards/electrical/BS7671/`
  carry `verification_status: engineer_transcription_C2` per the
  Sprint C.2 remediation pass. Every example consuming these tables
  MUST cite this status in reasoning.md (INV-12 Rule 4 enforces).
```

- [ ] **Step 13: Update cable-sizing skill.manifest.json**

Edit `electrical/cable-sizing/skill.manifest.json`:
1. Bump `"version": "1.0.2"` → `"version": "1.1.0"`.
2. Register the new example in `examples[]`:

```json
"examples": [
  "electrical/cable-sizing/examples/uk-domestic-final-circuits/",
  "electrical/cable-sizing/examples/ke-nairobi-commercial-with-msb/",
  "electrical/cable-sizing/examples/intl-commercial-with-feeders/",
  "electrical/cable-sizing/examples/us-industrial-with-motors/",
  "electrical/cable-sizing/examples/uk-rural-swa-submain/"
]
```

- [ ] **Step 14: Run gates + hand-check INV-12**

```bash
python3 scripts/validate-examples.py 2>&1 | tail -5
python3 functional_audit.py 2>&1 | tail -5

python3 -c "
import json
# uk-rural-swa-submain hand-check
d = json.load(open('electrical/cable-sizing/examples/uk-rural-swa-submain/output.json'))
for n in d['cascade']:
    sel = n.get('selection', {})
    if sel:
        print(f'{n[\"node_id\"]}:')
        print(f'  cable_type: {sel.get(\"cable_type\")}')
        print(f'  table_used: {sel.get(\"table_used\")}')
        print(f'  _source: {sel.get(\"_source\")}')
        print(f'  binding: {sel.get(\"binding_constraint\")}')
print()
inv12 = next((i for i in d.get('invariants', []) if i['id'] == 'INV-12'), None)
print(f'INV-12 entry: {inv12 is not None}')

# uk-domestic-final-circuits refit hand-check
d2 = json.load(open('electrical/cable-sizing/examples/uk-domestic-final-circuits/output.json'))
for n in d2['cascade']:
    sel = n.get('selection', {})
    if sel.get('cable_type') == 'pvc_twin_earth':
        print(f'{n[\"node_id\"]} refit: cable_type={sel[\"cable_type\"]}, table_used={sel.get(\"table_used\")}')
"
```

Expected output:
- validate-examples: AGGREGATE 223/223 pass (was 221, +2 from uk-rural-swa-submain output.json + intent-out.json)
- functional_audit: 1 finding unchanged
- uk-rural-swa-submain SUBMAIN-CABLE node: cable_type=pvc_swa, table_used=4D5A, _source matches, binding=vd_cumulative, INV-12 entry True
- uk-domestic-final-circuits refit: final circuit nodes show cable_type=pvc_twin_earth, table_used=4D1A

- [ ] **Step 15: Commit D2.1**

```bash
git add electrical/cable-sizing/
git commit -m "$(cat <<'EOF'
feat(cable-sizing): D2.1 PVC/SWA tables 4D1A + 4D5A consumers

Sprint D2 Item 5: extends cable_type enum with pvc_twin_earth + pvc_swa;
adds table_used field referencing BS 7671 4D-series + NEC 310.16 + IEC
60364-5-52 tables; new INV-12 enforces the cable_type ↔ table_used
compatibility matrix + method validity + citation + honest-disclosure.

Schema (cable-sizing-ir.schema.json):
- cable_type enum: +pvc_twin_earth, +pvc_swa (additive)
- selection.table_used: required when route.installation_method is set;
  enum covers BS 7671 (4D1A/4D2A/4D4A/4D5A/4E1A/4E2A/4E4A/4E5A),
  NEC (310.16 60/75/90°C columns), IEC 60364-5-52 (B1/E/F), and `none`
  for jurisdictions without a tabular reference.

Generator prompt: new step (table-selection walk) with the full
cable_type → table_used compatibility matrix per jurisdiction; cites
Sprint C.2 engineer_transcription_C2 disclosure requirement for 4D1A
+ 4D5A consumers.

Validator: INV-12 added (HIGH) — asserts:
1. cable_type ↔ table_used pair valid per the matrix
2. installation_method listed in the table's installation_methods
3. _source cites the (table_used, method) pair (string-match)
4. reasoning.md cites the Sprint C.2 disclosure for 4D1A/4D5A examples

Examples:
- Refit uk-domestic-final-circuits: final circuits (ring/lighting/
  cooker/shower) switched from incorrect pvc_singles to pvc_twin_earth
  + table_used: 4D1A + method C. Ampacity values refreshed per 4D1A
  column reads. reasoning.md adds table-walk section + C.2 disclosure.
- NEW example uk-rural-swa-submain: 100 m direct-buried PVC SWA
  submain to outbuilding SDB. Method D, soil 2.5 K·m/W. Walk-up
  rejected 16/25/35/50 mm² on 3% vd limit; selected 70 mm² at vd
  2.19%. CPC alternative per Reg 543.2.5 — separate 35 mm² Cu CPC
  (SWA armour insufficient for 6 kA × 0.4 s adiabatic).

Honest disclosure preserved: 4D1A + 4D5A engineer_transcription_C2
status surfaced in CHANGELOG, generator prompt, INV-12 Rule 4, and
both example reasoning.md files.

CHANGELOG [1.1.0] entry added (minor bump — new feature). Manifest
bumped 1.0.2 → 1.1.0.

validate-examples.py: 223/223 across 4 passes (+2 new example files).
functional_audit.py: 1 finding unchanged.

Sprint D2 Item 5 closed. Next: D2.2 db-layout board labelling.
EOF
)"
```

---

## Task D2.2: db-layout board + circuit labels (Sonnet)

**Why Sonnet:** Mechanical formatting per BS 7671 §514 / NEC §408.4(A) / IEC 60364-5-51 §514 + SVG template population. No engineering judgment beyond the per-jurisdiction format string. 20-example backport is the bulk of the work. Per model-selection rule for mechanical work.

**Files:**
- Modify: `electrical/db-layout/schemas/db-layout-ir.schema.json` — add label_format_standard + board_label + per-circuit circuit_label
- Modify: `electrical/db-layout/prompts/generator.md` — new label-population step
- Modify: `electrical/db-layout/prompts/validator.md` — add INV-14
- Create: `electrical/db-layout/templates/` directory with 6 .svg.template files
- Modify: 20 × `electrical/db-layout/examples/*/output.json` — backport labels
- Modify: `electrical/db-layout/skill.manifest.json` — add render-label to calculations[]
- CHANGELOG entry deferred — combined with D2.3 into single [1.4.0] bump

- [ ] **Step 1: Read current db-layout IR schema**

Read `electrical/db-layout/schemas/db-layout-ir.schema.json`. Locate:
- The root `properties` block. Note no `label_format_standard` and no `board_label` exist.
- The `board` property block (`board.properties` = `db_id, designation, location, enclosure_form_iec61439, ip_rating, ways_total, ways_used, ways_spare, board_kind`).
- The `circuits.items.properties` block (= `circuit_id, way_module_id, designation, voltage_class, downstream_load_kw, phase, ocpd, rcd, cable`). Note no `circuit_label`.

- [ ] **Step 2: Add `label_format_standard` and `board_label` at root**

Edit `electrical/db-layout/schemas/db-layout-ir.schema.json`. Find the root `properties` block (sibling to `drawing_type`, `meta`, etc.). Add two new fields:

```json
"label_format_standard": {
  "type": "string",
  "enum": ["BS", "NEC", "IEC"],
  "description": "Jurisdiction-bound label format. BS = BS 7671:2018+A2:2022 §514 + IET OSG Appendix B. NEC = NEC §408.4(A). IEC = IEC 60364-5-51 §514 + IEC 61439-1 §5.5. Maps from jurisdiction: GB/KE → BS; US → NEC; INT/EU → IEC. Engineer override permitted (INV-14 Rule 1 emits INFO not HIGH). Added Sprint D2.2."
},
"board_label": {
  "type": "object",
  "required": ["text", "svg", "tool_call_pending_for_pdf_png"],
  "additionalProperties": false,
  "description": "Per-board headline label per BS 7671 §514.13 / NEC §408.4 / IEC 60364-5-51 §514. Affixed to the panel face for field identification. SVG content is LLM-writable from templates/<standard>-board-label.svg.template; PDF/PNG rasterisation deferred to runtime via shared/calculations/electrical/render-label.json. Added Sprint D2.2.",
  "properties": {
    "text": {
      "type": "string",
      "minLength": 1,
      "maxLength": 120,
      "description": "Formatted per label_format_standard. Includes board designation + supply voltage + main switch rating + dual-source warning if applicable."
    },
    "svg": {
      "type": "string",
      "minLength": 50,
      "description": "Populated SVG markup (no {{placeholder}} remnants). LLM-readable; runtime-rasterisable via calc.render_label."
    },
    "tool_call_pending_for_pdf_png": {
      "type": "boolean",
      "description": "true until calc.render_label runs in the DraftsMan runtime. SVG content is browser-previewable inline."
    }
  }
}
```

Add `"label_format_standard"` and `"board_label"` to the root `required` array (sibling to existing required fields like `drawing_type`, `meta`, `jurisdiction`, `board`, `incoming_supply`, `main_switch`, `spare_ways`, `circuits`, `selectivity_results`, `compliance_summary`, `rationale`, `invariants`).

- [ ] **Step 3: Add `circuit_label` to circuits.items.properties**

In the same schema file, find the `circuits.items.properties` block. Add a sibling to existing properties (`circuit_id`, `way_module_id`, `designation`, ...):

```json
"circuit_label": {
  "type": "object",
  "required": ["text", "svg", "tool_call_pending_for_pdf_png"],
  "additionalProperties": false,
  "description": "Per-circuit strip-label per BS 7671 §514 / NEC §408.4(A) / IEC 60364-5-51 §514. Affixed to the directory pocket inside the panel door. Added Sprint D2.2.",
  "properties": {
    "text": {
      "type": "string",
      "minLength": 1,
      "maxLength": 80,
      "description": "Formatted per board.label_format_standard. ≤80 chars to fit strip-label width."
    },
    "svg": {"type": "string", "minLength": 50, "description": "Populated SVG markup (no {{placeholder}} remnants)."},
    "tool_call_pending_for_pdf_png": {"type": "boolean", "description": "true until calc.render_label runs."}
  }
}
```

Add `"circuit_label"` to `circuits.items.required` (alongside existing `circuit_id, way_module_id, designation, ocpd`).

- [ ] **Step 4: Create `electrical/db-layout/templates/` directory + 6 SVG templates**

Create the directory `electrical/db-layout/templates/`. Reference the canonical pattern at `electrical/arc-flash-labelling/templates/bs-5499-label.svg.template` (uses `{{placeholder}}` syntax + viewBox + Arial). Create 6 templates:

**`templates/bs-7671-circuit-label.svg.template`** (50 × 12 mm strip-label, BS format):

```xml
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg" width="50mm" height="12mm" viewBox="0 0 50 12" version="1.1">
  <title>Circuit label per BS 7671:2018+A2:2022 §514 — Way {{way}}</title>
  <desc>Per-circuit strip-label for UK installation per BS 7671 §514 + IET OSG App B.</desc>
  <rect x="0" y="0" width="50" height="12" fill="#FFFFFF" stroke="#000000" stroke-width="0.2"/>
  <text x="2" y="3.5" font-family="Arial, sans-serif" font-size="2.5" font-weight="bold" fill="#000000">{{way}}</text>
  <text x="6" y="3.5" font-family="Arial, sans-serif" font-size="2.5" fill="#000000">{{description}}</text>
  <text x="2" y="7" font-family="Arial, sans-serif" font-size="2" fill="#000000">{{phase}} | {{ocpd_type}} {{ocpd_rating_a}}A | {{cable_csa_mm2}}mm² {{cable_type}}</text>
  <text x="2" y="10.5" font-family="Arial, sans-serif" font-size="2" fill="#000000">{{rcd_if_any}}</text>
</svg>
```

**`templates/nec-408-4-circuit-label.svg.template`** (50 × 12 mm strip-label, NEC format):

```xml
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg" width="50mm" height="12mm" viewBox="0 0 50 12" version="1.1">
  <title>Circuit label per NEC §408.4(A) — Circuit {{circuit_number}}</title>
  <desc>Per-circuit strip-label for US installation per NEC 2023 §408.4(A).</desc>
  <rect x="0" y="0" width="50" height="12" fill="#FFFFFF" stroke="#000000" stroke-width="0.2"/>
  <text x="2" y="3.5" font-family="Arial, sans-serif" font-size="2.5" font-weight="bold" fill="#000000">#{{circuit_number}}</text>
  <text x="8" y="3.5" font-family="Arial, sans-serif" font-size="2.5" fill="#000000">{{description}}</text>
  <text x="2" y="7" font-family="Arial, sans-serif" font-size="2" fill="#000000">{{load_served}}</text>
  <text x="2" y="10.5" font-family="Arial, sans-serif" font-size="2" fill="#000000">OCPD: {{ocpd_rating_a}}A</text>
</svg>
```

**`templates/iec-60364-5-51-circuit-label.svg.template`** (50 × 12 mm strip-label, IEC format):

```xml
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg" width="50mm" height="12mm" viewBox="0 0 50 12" version="1.1">
  <title>Circuit label per IEC 60364-5-51 §514 / IEC 61439-1 §5.5 — {{id}}</title>
  <desc>Per-circuit strip-label for IEC-jurisdiction installation.</desc>
  <rect x="0" y="0" width="50" height="12" fill="#FFFFFF" stroke="#000000" stroke-width="0.2"/>
  <text x="2" y="3.5" font-family="Arial, sans-serif" font-size="2.5" font-weight="bold" fill="#000000">{{id}}</text>
  <text x="8" y="3.5" font-family="Arial, sans-serif" font-size="2.5" fill="#000000">{{function}}</text>
  <text x="2" y="7" font-family="Arial, sans-serif" font-size="2" fill="#000000">I_n: {{in_a}} A</text>
  <text x="2" y="10.5" font-family="Arial, sans-serif" font-size="2" fill="#000000">CSA: {{csa_mm2}} mm²</text>
</svg>
```

**`templates/bs-7671-board-label.svg.template`** (100 × 60 mm board headline, BS format):

```xml
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100mm" height="60mm" viewBox="0 0 100 60" version="1.1">
  <title>Board headline label per BS 7671:2018+A2:2022 §514.13 — {{board_designation}}</title>
  <desc>Board headline label for UK installation per BS 7671 §514.13.</desc>
  <rect x="0" y="0" width="100" height="60" fill="#FFFFFF" stroke="#000000" stroke-width="0.5"/>
  <rect x="0" y="0" width="100" height="14" fill="#003478" stroke="#000000" stroke-width="0.5"/>
  <text x="50" y="9" font-family="Arial, sans-serif" font-size="6" font-weight="bold" fill="#FFFFFF" text-anchor="middle">{{board_designation}}</text>
  <text x="4" y="22" font-family="Arial, sans-serif" font-size="3.5" font-weight="bold" fill="#000000">Supply:</text>
  <text x="20" y="22" font-family="Arial, sans-serif" font-size="3.5" fill="#000000">{{voltage_v}} V {{phase_arrangement}} {{system_type}}</text>
  <text x="4" y="29" font-family="Arial, sans-serif" font-size="3.5" font-weight="bold" fill="#000000">Main Switch:</text>
  <text x="28" y="29" font-family="Arial, sans-serif" font-size="3.5" fill="#000000">{{main_switch_rating_a}} A {{main_switch_type}}</text>
  <text x="4" y="36" font-family="Arial, sans-serif" font-size="3.5" font-weight="bold" fill="#000000">Ways:</text>
  <text x="16" y="36" font-family="Arial, sans-serif" font-size="3.5" fill="#000000">{{ways_used}} / {{ways_total}}</text>
  <text x="4" y="46" font-family="Arial, sans-serif" font-size="3" fill="#CC0000" font-weight="bold">{{dual_supply_warning_if_applicable}}</text>
  <text x="4" y="56" font-family="Arial, sans-serif" font-size="2.5" fill="#000000">Per BS 7671:2018+A2:2022 §514.13</text>
</svg>
```

**`templates/nec-408-4-board-label.svg.template`** (100 × 60 mm board headline, NEC format):

```xml
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100mm" height="60mm" viewBox="0 0 100 60" version="1.1">
  <title>Board headline label per NEC 2023 §408.4 — {{board_designation}}</title>
  <desc>Board headline label for US installation per NEC §408.4.</desc>
  <rect x="0" y="0" width="100" height="60" fill="#FFFFFF" stroke="#000000" stroke-width="0.5"/>
  <rect x="0" y="0" width="100" height="14" fill="#B22234" stroke="#000000" stroke-width="0.5"/>
  <text x="50" y="9" font-family="Arial, sans-serif" font-size="6" font-weight="bold" fill="#FFFFFF" text-anchor="middle">{{board_designation}}</text>
  <text x="4" y="22" font-family="Arial, sans-serif" font-size="3.5" font-weight="bold" fill="#000000">Supply:</text>
  <text x="20" y="22" font-family="Arial, sans-serif" font-size="3.5" fill="#000000">{{voltage_v}}V {{phase}} {{wire_count}}-wire</text>
  <text x="4" y="29" font-family="Arial, sans-serif" font-size="3.5" font-weight="bold" fill="#000000">Main:</text>
  <text x="14" y="29" font-family="Arial, sans-serif" font-size="3.5" fill="#000000">{{main_switch_rating_a}}A {{main_switch_type}}</text>
  <text x="4" y="36" font-family="Arial, sans-serif" font-size="3.5" font-weight="bold" fill="#000000">Spaces:</text>
  <text x="20" y="36" font-family="Arial, sans-serif" font-size="3.5" fill="#000000">{{ways_used}} of {{ways_total}}</text>
  <text x="4" y="46" font-family="Arial, sans-serif" font-size="3" fill="#CC0000" font-weight="bold">{{dual_supply_warning_if_applicable}}</text>
  <text x="4" y="56" font-family="Arial, sans-serif" font-size="2.5" fill="#000000">Per NEC 2023 §408.4(A)</text>
</svg>
```

**`templates/iec-60364-5-51-board-label.svg.template`** (100 × 60 mm board headline, IEC format):

```xml
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100mm" height="60mm" viewBox="0 0 100 60" version="1.1">
  <title>Board headline label per IEC 60364-5-51 §514 / IEC 61439-1 §5.5 — {{board_designation}}</title>
  <desc>Board headline label for IEC-jurisdiction installation.</desc>
  <rect x="0" y="0" width="100" height="60" fill="#FFFFFF" stroke="#000000" stroke-width="0.5"/>
  <rect x="0" y="0" width="100" height="14" fill="#003399" stroke="#000000" stroke-width="0.5"/>
  <text x="50" y="9" font-family="Arial, sans-serif" font-size="6" font-weight="bold" fill="#FFFFFF" text-anchor="middle">{{board_designation}}</text>
  <text x="4" y="22" font-family="Arial, sans-serif" font-size="3.5" font-weight="bold" fill="#000000">U:</text>
  <text x="10" y="22" font-family="Arial, sans-serif" font-size="3.5" fill="#000000">{{voltage_v}} V {{phase_arrangement}}</text>
  <text x="4" y="29" font-family="Arial, sans-serif" font-size="3.5" font-weight="bold" fill="#000000">I_n:</text>
  <text x="10" y="29" font-family="Arial, sans-serif" font-size="3.5" fill="#000000">{{main_switch_rating_a}} A</text>
  <text x="4" y="36" font-family="Arial, sans-serif" font-size="3.5" font-weight="bold" fill="#000000">Modules:</text>
  <text x="22" y="36" font-family="Arial, sans-serif" font-size="3.5" fill="#000000">{{ways_used}} / {{ways_total}}</text>
  <text x="4" y="46" font-family="Arial, sans-serif" font-size="3" fill="#CC0000" font-weight="bold">{{dual_supply_warning_if_applicable}}</text>
  <text x="4" y="56" font-family="Arial, sans-serif" font-size="2.5" fill="#000000">Per IEC 60364-5-51:2020 §514 + IEC 61439-1 §5.5</text>
</svg>
```

- [ ] **Step 5: Append generator step to db-layout/prompts/generator.md**

Read `electrical/db-layout/prompts/generator.md`. Locate the last numbered step. Append:

```markdown
### Step <N>: Board + circuit labelling per BS 7671 §514 / NEC §408.4 / IEC 60364-5-51 §514 (D2.2)

For every board, populate the headline label + every circuit's strip-label.

**Step 5.1 — Determine label_format_standard from jurisdiction:**

| Jurisdiction | label_format_standard | Clause |
|---|---|---|
| GB | BS | BS 7671:2018+A2:2022 §514 + IET OSG App B |
| KE | BS | KS 1700 §313 routes to BS 7671 §514 |
| US | NEC | NEC 2023 §408.4(A) |
| INT / EU | IEC | IEC 60364-5-51:2020 §514 + IEC 61439-1 §5.5 |

Engineer override permitted (e.g. multi-jurisdiction project picking
one format); INV-14 Rule 1 emits INFO not HIGH for jurisdictional
mismatch.

**Step 5.2 — Populate board_label.text per label_format_standard:**

- **BS:**
  ```
  <board.db_id> | <incoming_supply.voltage_v> V <incoming_supply.phase_arrangement> | Main Switch <main_switch.rating_a> A | <dual_supply_warning_if_applicable>
  ```
  Example: `DB-L1 | 230 V TPN | Main Switch 100 A | —`
  Dual-supply warning: `CAUTION: More than one source of supply (genset)` when the board is fed by a transfer scheme.

- **NEC:**
  ```
  <board.db_id> — <incoming_supply.voltage_v>V <phase> <wire_count>-wire — Main: <main_switch.rating_a>A <main_switch.type> — <warning>
  ```
  Example: `MSP — 208V 3-phase 4-wire — Main: 200A MCB — —`

- **IEC:**
  ```
  <board.db_id> | U=<incoming_supply.voltage_v> V <phase_arrangement> | I_n=<main_switch.rating_a> A | <warning>
  ```
  Example: `MSB-1 | U=400 V TPN | I_n=630 A | —`

**Step 5.3 — Populate board_label.svg:**

Read `electrical/db-layout/templates/<standard-lowercased>-board-label.svg.template` (e.g. `bs-7671-board-label.svg.template`). Substitute every `{{placeholder}}`:

- `{{board_designation}}` ← `board.db_id` (or `board.designation` if more descriptive)
- `{{voltage_v}}` ← `incoming_supply.voltage_v`
- `{{phase_arrangement}}` ← `incoming_supply.phase_arrangement`
- `{{system_type}}` ← `incoming_supply.system_type` (TN-S, TN-C-S, etc.)
- `{{main_switch_rating_a}}` ← `main_switch.rating_a`
- `{{main_switch_type}}` ← `main_switch.type`
- `{{ways_used}}` ← `board.ways_used`
- `{{ways_total}}` ← `board.ways_total`
- `{{dual_supply_warning_if_applicable}}` ← `"CAUTION: More than one source of supply"` if dual-source, else empty string `""`

For NEC template, also derive:
- `{{phase}}` ← `"single-phase"` / `"3-phase"` from `incoming_supply.phase_arrangement`
- `{{wire_count}}` ← `2`/`3`/`4` from phase arrangement + neutral presence

Emit the populated SVG as `board_label.svg`. Set `board_label.tool_call_pending_for_pdf_png: true`.

**Step 5.4 — Populate every circuits[*].circuit_label:**

For each circuit:

- **BS circuit_label.text** format:
  ```
  <circuit_id> | <designation> | <phase> | <ocpd.type> <ocpd.rating_a>A | <cable.csa_mm2_or_awg> <cable_type_short> | <rcd_if_any>
  ```
  Example: `C01 | Ground floor lighting | L1 | MCB 6A | 1.5mm² T&E | RCD 30mA Type A`
  Where:
  - `<phase>` ← `circuits[*].phase` (L1/L2/L3/N/L1L2/L1L2L3 for TPN multi-phase circuits)
  - `<ocpd.type> <ocpd.rating_a>A` ← e.g. `MCB 6A`, `MCCB 100A`, `RCBO 32A`
  - `<cable_type_short>` ← short-name e.g. `T&E` for pvc_twin_earth, `SWA` for pvc_swa, `singles` for pvc_singles
  - `<rcd_if_any>` ← `RCD <type> <sensitivity_ma>mA` if `circuits[*].rcd.required == true`; else `—`

- **NEC circuit_label.text** format:
  ```
  <circuit_id_number> — <designation> — <load_served> — <ocpd.rating_a>A
  ```
  Example: `12 — Receptacles East — General use — 20A`

- **IEC circuit_label.text** format:
  ```
  <circuit_id> | <function> | <ocpd.rating_a> A | <cable.csa_mm2> mm²
  ```
  Example: `Q1.1 | Lighting bank A | 16 A | 1.5 mm²`

For each circuit, read `templates/<standard-lowercased>-circuit-label.svg.template` and substitute placeholders. Set `tool_call_pending_for_pdf_png: true`.

**Step 5.5 — Set board.label_format_standard at root.**

**Output rule:** every board MUST have `label_format_standard` + `board_label`; every circuit MUST have `circuit_label`. INV-14 enforces.
```

- [ ] **Step 6: Append INV-14 to db-layout/prompts/validator.md**

Read `electrical/db-layout/prompts/validator.md`. Append after INV-13:

```markdown

---

**INV-14: Label format compliance (D2.2).**

**Severity:** HIGH

**Rule:** For every board:

1. **label_format_standard present + jurisdictional alignment.** `label_format_standard ∈ {"BS", "NEC", "IEC"}`. Expected mapping: GB/KE → BS, US → NEC, INT/EU → IEC. Mismatch emits an INFO (not HIGH) — engineer may override for multi-jurisdiction projects.

2. **board_label populated.** `board_label.text` non-empty, ≤120 chars. `board_label.svg` ≥50 chars AND contains NO `{{` placeholder remnants (substring `"{{"` is forbidden — indicates the template was not populated).

3. **board_label.text matches the format-pattern regex for label_format_standard:**
   - BS regex: `^[\w.-]+\s*\|\s*\d+\s*V\s+\S+\s*\|\s*Main\s+Switch\s+\d+\s*A\s*\|.*$`
   - NEC regex: `^[\w.-]+\s*—\s*\d+V\s+\S+\s*\d+-wire\s*—\s*Main:\s*\d+A\s+\S+\s*—.*$`
   - IEC regex: `^[\w.-]+\s*\|\s*U=\d+\s*V\s+\S+\s*\|\s*I_n=\d+\s*A\s*\|.*$`

For every circuit on every board:

4. **circuit_label populated.** `circuit_label.text` non-empty, ≤80 chars. `circuit_label.svg` ≥50 chars AND contains NO `{{` placeholder remnants.

5. **circuit_label.text matches the format-pattern regex:**
   - BS: `^[\w.]+\s*\|\s*.+\s*\|\s*(L1|L2|L3|N|L1L2|L1L2L3)\s*\|.*\d+A.*\|.*mm².*\|.+$`
   - NEC: `^\d+\s+—\s+.+\s+—\s+.+\s+—\s+\d+A$`
   - IEC: `^[\w.]+\s*\|\s*.+\s*\|\s*\d+(\.\d+)?\s*A\s*\|\s*\d+(\.\d+)?\s*mm²$`

6. **tool_call_pending_for_pdf_png set.** Both `board_label.tool_call_pending_for_pdf_png` and every `circuit_label.tool_call_pending_for_pdf_png` are present and boolean. Typically `true` (LLM-emitted SVG before runtime rasterisation); `false` only after runtime renders PDF/PNG.

**Validator action:** for each board, check label_format_standard + board_label fields per Rules 1–3; for each circuit, check circuit_label per Rules 4–5; verify all SVG fields contain no `{{` substring; verify all tool_call_pending flags are present.

**Rationale:** Panel-schedule IR is not field-usable without circuit labels (BS 7671 §514 / NEC §408.4(A) / IEC 60364-5-51 §514 all require legible identification at the panel). Labels are the field-engineer's only documentation pulled directly from the panel directory pocket; their format must be jurisdiction-correct + machine-checkable so the runtime can rasterise them onto adhesive label stock.
```

- [ ] **Step 7: Update db-layout/skill.manifest.json — add render-label calc**

Edit `electrical/db-layout/skill.manifest.json`. Find the `calculations[]` array. Append `"shared/calculations/electrical/render-label.json"` to it (reuses the same calc contract arc-flash-labelling uses).

DO NOT bump version yet — version bump is combined with D2.3 (deferred until D2.3 close).

- [ ] **Step 8: Backport labels to 20 existing examples**

For each of the 20 db-layout examples:

```
electrical/db-layout/examples/intl-commercial-tpn-msb/
electrical/db-layout/examples/intl-dbcomms-data/
electrical/db-layout/examples/intl-dbem-emergency-lighting/
electrical/db-layout/examples/intl-dbfa1-fire-alarm/
electrical/db-layout/examples/intl-dbgenset-changeover/
electrical/db-layout/examples/intl-dbl1-lighting/
electrical/db-layout/examples/intl-dbm1-mechanical/
electrical/db-layout/examples/intl-dbp1-power/
electrical/db-layout/examples/intl-dbups-backed/
electrical/db-layout/examples/ke-nairobi-gh-db/
electrical/db-layout/examples/ke-nairobi-industrial-100A-tpn/
electrical/db-layout/examples/uk-commercial-msb-3storey/
electrical/db-layout/examples/uk-commercial-sdb-gf/
electrical/db-layout/examples/uk-commercial-sdb-l1/
electrical/db-layout/examples/uk-commercial-sdb-l2/
electrical/db-layout/examples/uk-domestic-consumer-unit/
electrical/db-layout/examples/us-strip-mall-common-area/
electrical/db-layout/examples/us-strip-mall-panelboard/
electrical/db-layout/examples/us-strip-mall-tsp-a/
electrical/db-layout/examples/us-strip-mall-tsp-b/
```

For each example's `output.json`:

1. Add `label_format_standard` at root (derived from `jurisdiction`):
   - `"GB"` or `"KE"` → `"label_format_standard": "BS"`
   - `"US"` → `"label_format_standard": "NEC"`
   - `"INT"` → `"label_format_standard": "IEC"`

2. Add `board_label` at root. Populate `text` per the format string in Step 5.2; populate `svg` by reading the matching template and substituting placeholders. Set `tool_call_pending_for_pdf_png: true`.

3. For every circuit in `circuits[]`, add `circuit_label`. Populate text + svg + tool_call_pending per Step 5.4.

4. Add INV-14 entry to `invariants[]`:

```json
{
  "id": "INV-14",
  "passes": true,
  "severity": "high",
  "evidence": "label_format_standard=<std> matches jurisdiction <jur> (Rule 1 PASS). board_label.text formatted per <std> regex (Rule 2 PASS); svg populated from templates/<std-lower>-board-label.svg.template with all {{placeholders}} substituted (Rule 3 PASS). All <N> circuits carry circuit_label.text matching the <std> regex; circuit_label.svg populated from templates/<std-lower>-circuit-label.svg.template (Rules 4–5 PASS). tool_call_pending_for_pdf_png=true on board + every circuit (Rule 6 PASS)."
}
```

NO IE / load / OCPD value changes during this backport. Labels are derived-from-existing-content; the rest of the IR is untouched.

- [ ] **Step 9: Run gates + hand-check INV-14**

```bash
python3 scripts/validate-examples.py 2>&1 | tail -5

python3 -c "
import json, re
# Pick uk-domestic-consumer-unit as canonical BS check
d = json.load(open('electrical/db-layout/examples/uk-domestic-consumer-unit/output.json'))
print(f'label_format_standard: {d.get(\"label_format_standard\")}')
bl = d.get('board_label', {})
print(f'board_label.text: {bl.get(\"text\", \"\")[:80]}')
print(f'board_label.svg has no {{{{: {\"{{\" not in bl.get(\"svg\", \"\")}')
print(f'tool_call_pending: {bl.get(\"tool_call_pending_for_pdf_png\")}')
print()
print(f'circuit_label coverage:')
for c in d.get('circuits', [])[:3]:
    cl = c.get('circuit_label', {})
    print(f'  {c[\"circuit_id\"]}: text={cl.get(\"text\", \"\")[:60]}, svg_no_placeholder={\"{{\" not in cl.get(\"svg\", \"\")}')
print()
inv14 = next((i for i in d.get('invariants', []) if i['id'] == 'INV-14'), None)
print(f'INV-14 entry: {inv14 is not None}')
"
```

Expected output:
- validate-examples: 223/223 (no new examples added in D2.2; 221 baseline + 2 from D2.1 uk-rural-swa-submain)
- uk-domestic-consumer-unit: label_format_standard=BS; board_label.text starts with `CU-MAIN |` or similar; svg has no `{{`; tool_call_pending=true
- First 3 circuits have circuit_label.text matching BS regex; svg populated
- INV-14 entry present

DO NOT update CHANGELOG yet — combined with D2.3 in a single 1.4.0 bump.

- [ ] **Step 10: Commit D2.2**

```bash
git add electrical/db-layout/
git commit -m "$(cat <<'EOF'
feat(db-layout): D2.2 board + circuit labels (BS/NEC/IEC) + 6 SVG templates

Sprint D2 Item 6: panel-schedule IR gains per-circuit + per-board labels
per BS 7671:2018+A2:2022 §514 / NEC 2023 §408.4(A) / IEC 60364-5-51:2020
§514. Without these, the schedule was not field-usable.

Schema (db-layout-ir.schema.json):
- label_format_standard at root: enum BS|NEC|IEC; jurisdiction-mapped
  GB/KE→BS, US→NEC, INT/EU→IEC; engineer override permitted.
- board_label at root: text (≤120c, formatted per std) + svg
  (populated from templates/) + tool_call_pending_for_pdf_png. Required.
- circuit_label per circuit: text (≤80c) + svg + tool_call_pending.
  Required on every circuits[].items entry.

NEW templates/ directory with 6 .svg.template files (mirrors the canonical
arc-flash-labelling pattern):
- bs-7671-{circuit,board}-label.svg.template (UK navy banner)
- nec-408-4-{circuit,board}-label.svg.template (US red banner)
- iec-60364-5-51-{circuit,board}-label.svg.template (EU blue banner)
All use {{placeholder}} syntax substituted at generation time.

Generator prompt: new step covering label_format_standard derivation +
text format per jurisdiction + svg template population for board headline
+ per-circuit strip-labels. Format strings:
- BS:  '<id> | <V> V <ph> | Main Switch <In> A | <warning>'
- NEC: '<id> — <V>V <ph> <n>-wire — Main: <In>A <type> — <warning>'
- IEC: '<id> | U=<V> V <ph> | I_n=<In> A | <warning>'

Validator INV-14 added (HIGH, 6 rules): label_format_standard presence +
jurisdictional alignment (INFO for mismatch); board_label/circuit_label
text length + regex match per std; svg populated (no {{ remnants);
tool_call_pending_for_pdf_png set on every label entry.

Manifest: shared/calculations/electrical/render-label.json added to
calculations[] (reuses arc-flash-labelling's calc contract — runtime PDF/PNG
rasterisation deferred per [[runtime-project-boundary]]).

Examples: 20 existing example outputs backported with label_format_standard
+ board_label + per-circuit circuit_label. NO IE/load/OCPD changes — labels
derived from existing content; rest of IR untouched. Each example gains
an INV-14 invariants[] entry.

Version bump deferred to D2.3 — single 1.4.0 bump after diversity edge
cases ship.

validate-examples.py: 223/223 across 4 passes (no new example files in
D2.2; 221 baseline + 2 from D2.1).
functional_audit.py: 1 finding unchanged.

Sprint D2 Item 6 closed. Next: D2.3 diversity edge cases.
EOF
)"
```

---

## Task D2.3: db-layout diversity edge cases — lifts + EV + AC + motor groups (Opus)

**Why Opus:** Engineering judgment on regulation-driven diversity factors (BS 7671 Reg 559 lifts; Reg 722 + OZEV CoP for EV — both 1.00 no-diversity by regulation; CIBSE TM50 grouped-AC 100+75; Reg 552 motor groups). Plus a new worked example with 5 distinct load-types in one mixed-use building. Per model-selection rule for engineering work.

**Files:**
- Modify: `electrical/db-layout/schemas/db-layout-ir.schema.json` — add diversity_basis to circuits.items
- Modify: `electrical/db-layout/prompts/generator.md` — extend per-load-type diversity table (4 new rows + tighten 2)
- Modify: `electrical/db-layout/prompts/validator.md` — add INV-15
- Modify: 20 × `electrical/db-layout/examples/*/output.json` — backport diversity_basis
- Modify: `electrical/db-layout/CHANGELOG.md` — combined [1.4.0] entry (D2.2 + D2.3)
- Modify: `electrical/db-layout/skill.manifest.json` — version 1.3.3 → 1.4.0 + register new example
- Create: 4 files at `electrical/db-layout/examples/uk-mixed-use-lifts-and-ev/`

- [ ] **Step 1: Read current db-layout IR schema (post-D2.2 state)**

Read `electrical/db-layout/schemas/db-layout-ir.schema.json`. Locate `circuits.items.properties` — currently has `circuit_id, way_module_id, designation, voltage_class, downstream_load_kw, phase, ocpd, rcd, cable, circuit_label` (last added by D2.2).

Note: there is currently NO `diversity_basis` field. Diversity is computed at board-level only — this surfaces it per-circuit so the audit trail is explicit.

- [ ] **Step 2: Add `diversity_basis` to circuits.items.properties**

Edit `electrical/db-layout/schemas/db-layout-ir.schema.json`. Find `circuits.items.properties`. Add sibling to `circuit_label`:

```json
"diversity_basis": {
  "type": "object",
  "required": ["load_type", "factor_applied", "method", "citation"],
  "additionalProperties": false,
  "description": "Per-circuit diversity factor + the regulation/standard that authorises it. Surfaces the audit trail of which clause was applied so a downstream reviewer can verify without inferring from designation alone. Added Sprint D2.3.",
  "properties": {
    "load_type": {
      "type": "string",
      "enum": [
        "instantaneous_water_heater",
        "shower",
        "storage_water_heater",
        "socket_general",
        "motor_single",
        "motor_group",
        "lift",
        "ev_charger",
        "ac_single",
        "ac_group",
        "lighting_continuous",
        "fixed_resistive",
        "other_declared"
      ]
    },
    "factor_applied": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0,
      "description": "Diversity factor 0.0–1.00. 1.00 means no diversity (load takes full demand)."
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
      "description": "Required when method == 'largest_plus_remainder_pct'. Sockets: 100/40; motor group: 100/50; AC group: 100/75.",
      "properties": {
        "largest_pct": {"type": "number", "minimum": 0, "maximum": 100},
        "remainder_pct": {"type": "number", "minimum": 0, "maximum": 100}
      }
    },
    "citation": {
      "type": "string",
      "minLength": 20,
      "maxLength": 300,
      "description": "Names the clause (Reg / § / Table / OSG / CoP / TM). INV-15 enforces presence of a recognisable clause marker."
    }
  }
}
```

Add `"diversity_basis"` to `circuits.items.required`.

- [ ] **Step 3: Extend generator step in db-layout/prompts/generator.md**

Read `electrical/db-layout/prompts/generator.md`. Locate the existing per-load-type diversity table (search for `diversity` — Sprint B added the initial table). Replace the existing table with the extended version:

```markdown
**Per-load-type diversity table (BS 7671 + IET OSG App A + sector
standards):**

| Load type | Factor / method | Method params | Citation |
|---|---|---|---|
| Instantaneous water heater | 1.00 | — | BS 7671:2018+A2:2022 § 311.1 + IET OSG App A |
| Shower (≥7.2 kW instantaneous) | 1.00 | — | BS 7671:2018+A2:2022 § 311.1 |
| Storage water heater | 1.00 | — | IET OSG App A (continuous load) |
| Standard socket-outlet | 100% largest + 40% remainder | {largest:100, remainder:40} | IET OSG App A |
| **Lift / lift motor** | **1.00** | — | **BS 7671:2018+A2:2022 Reg 559 + IET Wiring Matters WR9 + EN 81-20:2020 §5.10** |
| **EV charging point** | **1.00** | — | **BS 7671:2018+A2:2022 Reg 722 + OZEV CoP for EV Charging Equipment Installation §4.3 + IET CoP for EVCI 4th ed. §8.5** |
| **AC unit — single** | **1.00** | — | **CIBSE TM50:2014 §4.2 + BS 7671:2018+A2:2022 Reg 552** |
| **AC group (multi-split)** | **100% largest + 75% remainder** | {largest:100, remainder:75} | **CIBSE TM50:2014 Table 4.3** |
| Motor — single (tighten citation) | 1.00 | — | BS 7671:2018+A2:2022 Reg 552.1.1 |
| Motor group (tighten citation) | 100% largest + 50% remainder | {largest:100, remainder:50} | BS 7671:2018+A2:2022 Reg 552 + IET OSG App A motor section |
| Lighting (continuous) | 1.00 | — | IET OSG App A |
| Fixed resistive (e.g. immersion heater bank) | 1.00 | — | IET OSG App A |

**For every circuit**, populate `circuits[*].diversity_basis`:

```json
"diversity_basis": {
  "load_type": "<one of enum>",
  "factor_applied": <0.0-1.0>,
  "method": "<no_diversity | largest_plus_remainder_pct | table_factor | engineer_declared>",
  "method_params": {<largest_pct, remainder_pct> if method=largest_plus_remainder_pct},
  "citation": "<≥20 char clause reference>"
}
```

**Critical regulation-driven cases (cite the regulation directly):**

- **Lifts: factor = 1.00.** Per BS 7671 Reg 559 + IET WR9. Lift
  motors have starting transients 3–5× running current — applying
  any diversity downstream understates the cable + protective device
  requirement.

- **EV chargers: factor = 1.00.** Per BS 7671 Reg 722 + the OZEV
  Code of Practice for EV Charging Equipment Installation (industry
  guidance referenced by Reg 722) + IET CoP for EVCI 4th ed. EV
  charging is treated as continuous load at full demand — no
  diversity per the OZEV CoP §4.3.

- **AC grouped: 100% largest + 75% remainder.** Per CIBSE TM50:2014
  Table 4.3. Multi-split AC installations may apply this factor
  because simultaneous full-load operation of N units is rare under
  typical building thermal load profiles. SINGLE AC unit gets no
  diversity.

**Honest disclosure (OZEV industry-guidance status):** The OZEV Code
of Practice for EV Charging Equipment Installation is INDUSTRY
GUIDANCE, not statutory law. However, BS 7671 Reg 722 IS statutory
and references the OZEV CoP. Examples consuming this row MUST
distinguish the two in reasoning.md (Reg 722 statutory + OZEV CoP
industry guidance).

**Honest disclosure (CIBSE TM50 paywall):** CIBSE TM50:2014 is
behind the CIBSE publication paywall. Cite the table number
explicitly (TM50:2014 Table 4.3) so the engineer-of-record can
verify against the published edition.

**Validator INV-15 enforces** diversity_basis presence + factor
range + citation marker + the lift/EV factor=1.00 hard rules.
```

- [ ] **Step 4: Append INV-15 to db-layout/prompts/validator.md**

Read `electrical/db-layout/prompts/validator.md`. Append after INV-14:

```markdown

---

**INV-15: Diversity basis cited per circuit (D2.3).**

**Severity:** HIGH

**Rule:** For every circuit on every board:

1. **diversity_basis present + valid enum values.** Every circuit has `diversity_basis` with `load_type ∈` the 13-value enum, `factor_applied ∈ [0.0, 1.0]`, `method ∈ {no_diversity, largest_plus_remainder_pct, table_factor, engineer_declared}`.

2. **Citation includes a recognisable clause marker.** `diversity_basis.citation` is ≥20 chars AND contains at least one of: `Reg`, `§`, `Table`, `OSG`, `CoP`, `TM`. Pure prose without a clause marker is a HIGH violation.

3. **Regulation-driven hard rules.** If `load_type == "lift"`, then `factor_applied == 1.00` AND `method == "no_diversity"` (per BS 7671 Reg 559 + WR9). If `load_type == "ev_charger"`, then `factor_applied == 1.00` AND `method == "no_diversity"` (per BS 7671 Reg 722 + OZEV CoP §4.3). Mismatch (e.g. an EV circuit with factor 0.5) is a HIGH violation — these regulations forbid diversity on these loads.

4. **method_params consistency.** If `method == "largest_plus_remainder_pct"`, then `method_params.largest_pct` AND `method_params.remainder_pct` must be present, both ∈ [0, 100], AND their sum ∈ [100, 200]. Documented industry sums: sockets 100+40=140; motor group 100+50=150; AC group 100+75=175. Engineer-declared edge cases outside [100, 200] must use `method: "engineer_declared"` (which bypasses Rule 4).

**Validator action:** for each circuit, check diversity_basis presence; assert factor_applied in range; verify citation contains a clause marker; for load_type ∈ {lift, ev_charger}, assert factor_applied == 1.00; for method == largest_plus_remainder_pct, assert sum of pct in [100, 200].

**Rationale:** Sprint B INV-12 caught the instantaneous-load misapplication (blanket 0.4 factor on a shower load) but did not enforce per-circuit basis citation. The Sprint D2.3 audit trail closes the gap: every circuit now declares (a) which load-type it falls under, (b) what factor applies, (c) what regulation/standard authorises it. A downstream reviewer (TCS / panel-builder / building-control) can verify each circuit independently without inferring from designation prose.
```

- [ ] **Step 5: Create uk-mixed-use-lifts-and-ev — input.json**

Create directory `electrical/db-layout/examples/uk-mixed-use-lifts-and-ev/`. Write `input.json`:

```json
{
  "$schema": "../../inputs.json",
  "skill": "db-layout",
  "example_id": "uk-mixed-use-lifts-and-ev",
  "jurisdiction": "GB",
  "items": [
    {
      "id": "I-1",
      "category": "site_brief",
      "label": "Site description",
      "value": "UK mixed-use building — 4-storey commercial ground + residential upper. Sub-distribution board serves the ground-floor commercial common areas: 1 passenger lift (BS EN 81-20:2020), 4 × 7 kW EV charge points (residential parking — Mode 3 Type 2 per BS 7671 Reg 722 + OZEV CoP), 2 × split AC units (single + grouped multi-split pair), general sockets, and lighting. Per BS 7671:2018+A2:2022 § 311.1 per-load-type diversity table (NOT blanket factor)."
    },
    {
      "id": "I-2",
      "category": "board",
      "label": "Board specification",
      "value": {
        "db_id": "SDB-COMMON",
        "designation": "Ground-floor common-area sub-distribution board",
        "location": "GF plant room",
        "enclosure_form_iec61439": "form_2b",
        "ip_rating": "IP4X",
        "ways_total": 12,
        "board_kind": "general_distribution"
      }
    },
    {
      "id": "I-3",
      "category": "incoming_supply",
      "label": "Incoming supply",
      "value": {
        "voltage_v": 400,
        "phase_arrangement": "TPN",
        "system_type": "TN-S",
        "declared_pfc_ka": 16,
        "main_switch_rating_a": 200
      }
    },
    {
      "id": "I-4",
      "category": "circuits",
      "label": "Load schedule",
      "value": [
        {"id": "C01", "designation": "Lift motor + lift controller (BS EN 81-20)", "load_kw": 11, "load_type": "lift", "phase": "L1L2L3"},
        {"id": "C02", "designation": "EV charge point #1 (7 kW Mode 3)", "load_kw": 7.36, "load_type": "ev_charger", "phase": "L1"},
        {"id": "C03", "designation": "EV charge point #2 (7 kW Mode 3)", "load_kw": 7.36, "load_type": "ev_charger", "phase": "L2"},
        {"id": "C04", "designation": "EV charge point #3 (7 kW Mode 3)", "load_kw": 7.36, "load_type": "ev_charger", "phase": "L3"},
        {"id": "C05", "designation": "EV charge point #4 (7 kW Mode 3)", "load_kw": 7.36, "load_type": "ev_charger", "phase": "L1"},
        {"id": "C06", "designation": "AC unit — single split (5 kW)", "load_kw": 5, "load_type": "ac_single", "phase": "L2"},
        {"id": "C07", "designation": "AC multi-split bank — 4 units × 3.5 kW each", "load_kw": 14, "load_type": "ac_group", "phase": "L1L2L3", "items_in_group": 4, "largest_item_kw": 3.5},
        {"id": "C08", "designation": "Common-area lighting (continuous)", "load_kw": 2, "load_type": "lighting_continuous", "phase": "L3"},
        {"id": "C09", "designation": "General sockets — 6 circuits", "load_kw": 6, "load_type": "socket_general", "phase": "L1", "items_in_group": 6, "largest_item_kw": 1.5}
      ]
    }
  ]
}
```

- [ ] **Step 6: Create uk-mixed-use-lifts-and-ev — output.json**

Write `electrical/db-layout/examples/uk-mixed-use-lifts-and-ev/output.json`. Hand-compute the per-circuit diversity walk + the board-level demand sum:

**Per-circuit diversity walk:**

| Circuit | load_kw | load_type | factor | method | demand_kw |
|---|---|---|---|---|---|
| C01 lift | 11 | lift | 1.00 | no_diversity | 11.00 |
| C02 EV | 7.36 | ev_charger | 1.00 | no_diversity | 7.36 |
| C03 EV | 7.36 | ev_charger | 1.00 | no_diversity | 7.36 |
| C04 EV | 7.36 | ev_charger | 1.00 | no_diversity | 7.36 |
| C05 EV | 7.36 | ev_charger | 1.00 | no_diversity | 7.36 |
| C06 AC single | 5 | ac_single | 1.00 | no_diversity | 5.00 |
| C07 AC group | 14 (= 4 × 3.5) | ac_group | (3.5 + 0.75 × 10.5)/14 = 0.81 | largest_plus_remainder_pct {100,75} | 3.5 + 7.875 = 11.375 |
| C08 lighting | 2 | lighting_continuous | 1.00 | no_diversity | 2.00 |
| C09 sockets | 6 (= 6 × ~1.5, largest 1.5) | socket_general | (1.5 + 0.4 × 4.5)/6 = 0.55 | largest_plus_remainder_pct {100,40} | 1.5 + 1.8 = 3.30 |

**Total board demand = 11.00 + 7.36×4 + 5.00 + 11.375 + 2.00 + 3.30 = 62.115 kW**

At 400 V TPN: I = 62115 / (√3 × 400 × 0.9) = 99.7 A balanced. Per-phase load varies (EV circuits each on a different phase by design) — phase L1: C02 + C05 + C09 ≈ 7.36 + 7.36 + 1.5 (single largest socket on L1) = ~16.2 kW. L2: C03 + C06 = 7.36 + 5 = ~12.4 kW. L3: C04 + C08 = 7.36 + 2 = ~9.4 kW. Plus 3-phase circuits (C01 lift + C07 AC group) split across all three phases. Per-phase loading reasonably balanced for a 200 A TPN main.

Output.json:

```json
{
  "$schema": "../../schemas/db-layout-ir.schema.json",
  "drawing_type": "db_layout_schedule_and_schematic",
  "version": "1.4.0",
  "meta": {
    "project_id": "uk-mixed-use-lifts-and-ev",
    "skill_version": "db-layout/1.4.0",
    "produced_at": "2026-05-26T11:00:00Z",
    "consumed_intents": []
  },
  "jurisdiction": "GB",
  "label_format_standard": "BS",
  "board": {
    "db_id": "SDB-COMMON",
    "designation": "Ground-floor common-area sub-distribution board",
    "location": "GF plant room",
    "enclosure_form_iec61439": "form_2b",
    "ip_rating": "IP4X",
    "ways_total": 12,
    "ways_used": 9,
    "ways_spare": 3,
    "board_kind": "general_distribution"
  },
  "board_label": {
    "text": "SDB-COMMON | 400 V TPN | Main Switch 200 A | —",
    "svg": "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"100mm\" height=\"60mm\" viewBox=\"0 0 100 60\" version=\"1.1\"><title>Board headline label per BS 7671:2018+A2:2022 §514.13 — SDB-COMMON</title><rect x=\"0\" y=\"0\" width=\"100\" height=\"60\" fill=\"#FFFFFF\" stroke=\"#000000\" stroke-width=\"0.5\"/><rect x=\"0\" y=\"0\" width=\"100\" height=\"14\" fill=\"#003478\"/><text x=\"50\" y=\"9\" font-family=\"Arial\" font-size=\"6\" font-weight=\"bold\" fill=\"#FFFFFF\" text-anchor=\"middle\">SDB-COMMON</text><text x=\"4\" y=\"22\" font-family=\"Arial\" font-size=\"3.5\" font-weight=\"bold\" fill=\"#000000\">Supply:</text><text x=\"20\" y=\"22\" font-family=\"Arial\" font-size=\"3.5\" fill=\"#000000\">400 V TPN TN-S</text><text x=\"4\" y=\"29\" font-family=\"Arial\" font-size=\"3.5\" font-weight=\"bold\" fill=\"#000000\">Main Switch:</text><text x=\"28\" y=\"29\" font-family=\"Arial\" font-size=\"3.5\" fill=\"#000000\">200 A MCCB</text><text x=\"4\" y=\"36\" font-family=\"Arial\" font-size=\"3.5\" font-weight=\"bold\" fill=\"#000000\">Ways:</text><text x=\"16\" y=\"36\" font-family=\"Arial\" font-size=\"3.5\" fill=\"#000000\">9 / 12</text><text x=\"4\" y=\"56\" font-family=\"Arial\" font-size=\"2.5\" fill=\"#000000\">Per BS 7671:2018+A2:2022 §514.13</text></svg>",
    "tool_call_pending_for_pdf_png": true
  },
  "incoming_supply": {
    "voltage_v": 400,
    "phase_arrangement": "TPN",
    "system_type": "TN-S",
    "declared_pfc_ka": 16
  },
  "main_switch": {
    "type": "MCCB",
    "rating_a": 200,
    "curve": "B",
    "breaking_capacity_ka": 36
  },
  "spare_ways": 3,
  "circuits": [
    {
      "circuit_id": "C01",
      "way_module_id": "W1",
      "designation": "Lift motor + lift controller (BS EN 81-20)",
      "voltage_class": "LV_power",
      "downstream_load_kw": 11,
      "phase": "L1L2L3",
      "ocpd": {"type": "MCCB", "rating_a": 32, "curve": "D", "breaking_capacity_ka": 36},
      "rcd": {"required": true, "type": "B", "sensitivity_ma": 300},
      "cable": {"csa_mm2_or_awg": "10mm²", "cores": 5, "length_m": 22},
      "circuit_label": {
        "text": "C01 | Lift motor + controller | L1L2L3 | MCCB 32A | 10mm² T&E | RCD 300mA Type B",
        "svg": "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"50mm\" height=\"12mm\" viewBox=\"0 0 50 12\"><rect x=\"0\" y=\"0\" width=\"50\" height=\"12\" fill=\"#FFFFFF\" stroke=\"#000000\" stroke-width=\"0.2\"/><text x=\"2\" y=\"3.5\" font-family=\"Arial\" font-size=\"2.5\" font-weight=\"bold\">C01</text><text x=\"6\" y=\"3.5\" font-family=\"Arial\" font-size=\"2.5\">Lift motor + controller</text><text x=\"2\" y=\"7\" font-family=\"Arial\" font-size=\"2\">L1L2L3 | MCCB 32A | 10mm² T&amp;E</text><text x=\"2\" y=\"10.5\" font-family=\"Arial\" font-size=\"2\">RCD 300mA Type B</text></svg>",
        "tool_call_pending_for_pdf_png": true
      },
      "diversity_basis": {
        "load_type": "lift",
        "factor_applied": 1.00,
        "method": "no_diversity",
        "citation": "BS 7671:2018+A2:2022 Reg 559 + IET WR9 + EN 81-20:2020 §5.10 — lift motors take full demand, no diversity"
      }
    },
    {
      "circuit_id": "C02",
      "way_module_id": "W2",
      "designation": "EV charge point #1 (7 kW Mode 3 Type 2)",
      "voltage_class": "LV_power",
      "downstream_load_kw": 7.36,
      "phase": "L1",
      "ocpd": {"type": "MCB", "rating_a": 32, "curve": "C", "breaking_capacity_ka": 6},
      "rcd": {"required": true, "type": "B", "sensitivity_ma": 30},
      "cable": {"csa_mm2_or_awg": "6mm²", "cores": 3, "length_m": 28},
      "circuit_label": {
        "text": "C02 | EV CP#1 7kW Mode 3 | L1 | MCB 32A | 6mm² T&E | RCD 30mA Type B",
        "svg": "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"50mm\" height=\"12mm\" viewBox=\"0 0 50 12\"><rect width=\"50\" height=\"12\" fill=\"#FFFFFF\" stroke=\"#000000\" stroke-width=\"0.2\"/><text x=\"2\" y=\"3.5\" font-family=\"Arial\" font-size=\"2.5\" font-weight=\"bold\">C02</text><text x=\"6\" y=\"3.5\" font-family=\"Arial\" font-size=\"2.5\">EV CP#1 7kW Mode 3</text><text x=\"2\" y=\"7\" font-family=\"Arial\" font-size=\"2\">L1 | MCB 32A | 6mm² T&amp;E</text><text x=\"2\" y=\"10.5\" font-family=\"Arial\" font-size=\"2\">RCD 30mA Type B</text></svg>",
        "tool_call_pending_for_pdf_png": true
      },
      "diversity_basis": {
        "load_type": "ev_charger",
        "factor_applied": 1.00,
        "method": "no_diversity",
        "citation": "BS 7671:2018+A2:2022 Reg 722 + OZEV CoP §4.3 + IET CoP for EVCI 4th ed. §8.5 — EV charging treated as continuous load at full demand, no diversity"
      }
    },
    {
      "circuit_id": "C03",
      "way_module_id": "W3",
      "designation": "EV charge point #2 (7 kW Mode 3 Type 2)",
      "voltage_class": "LV_power",
      "downstream_load_kw": 7.36,
      "phase": "L2",
      "ocpd": {"type": "MCB", "rating_a": 32, "curve": "C", "breaking_capacity_ka": 6},
      "rcd": {"required": true, "type": "B", "sensitivity_ma": 30},
      "cable": {"csa_mm2_or_awg": "6mm²", "cores": 3, "length_m": 30},
      "circuit_label": {
        "text": "C03 | EV CP#2 7kW Mode 3 | L2 | MCB 32A | 6mm² T&E | RCD 30mA Type B",
        "svg": "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"50mm\" height=\"12mm\" viewBox=\"0 0 50 12\"><rect width=\"50\" height=\"12\" fill=\"#FFFFFF\" stroke=\"#000000\" stroke-width=\"0.2\"/><text x=\"2\" y=\"3.5\" font-family=\"Arial\" font-size=\"2.5\" font-weight=\"bold\">C03</text><text x=\"6\" y=\"3.5\" font-family=\"Arial\" font-size=\"2.5\">EV CP#2 7kW Mode 3</text><text x=\"2\" y=\"7\" font-family=\"Arial\" font-size=\"2\">L2 | MCB 32A | 6mm² T&amp;E</text><text x=\"2\" y=\"10.5\" font-family=\"Arial\" font-size=\"2\">RCD 30mA Type B</text></svg>",
        "tool_call_pending_for_pdf_png": true
      },
      "diversity_basis": {
        "load_type": "ev_charger",
        "factor_applied": 1.00,
        "method": "no_diversity",
        "citation": "BS 7671:2018+A2:2022 Reg 722 + OZEV CoP §4.3 + IET CoP for EVCI 4th ed. §8.5"
      }
    },
    {
      "circuit_id": "C04",
      "way_module_id": "W4",
      "designation": "EV charge point #3 (7 kW Mode 3 Type 2)",
      "voltage_class": "LV_power",
      "downstream_load_kw": 7.36,
      "phase": "L3",
      "ocpd": {"type": "MCB", "rating_a": 32, "curve": "C", "breaking_capacity_ka": 6},
      "rcd": {"required": true, "type": "B", "sensitivity_ma": 30},
      "cable": {"csa_mm2_or_awg": "6mm²", "cores": 3, "length_m": 32},
      "circuit_label": {
        "text": "C04 | EV CP#3 7kW Mode 3 | L3 | MCB 32A | 6mm² T&E | RCD 30mA Type B",
        "svg": "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"50mm\" height=\"12mm\" viewBox=\"0 0 50 12\"><rect width=\"50\" height=\"12\" fill=\"#FFFFFF\" stroke=\"#000000\" stroke-width=\"0.2\"/><text x=\"2\" y=\"3.5\" font-family=\"Arial\" font-size=\"2.5\" font-weight=\"bold\">C04</text><text x=\"6\" y=\"3.5\" font-family=\"Arial\" font-size=\"2.5\">EV CP#3 7kW Mode 3</text><text x=\"2\" y=\"7\" font-family=\"Arial\" font-size=\"2\">L3 | MCB 32A | 6mm² T&amp;E</text><text x=\"2\" y=\"10.5\" font-family=\"Arial\" font-size=\"2\">RCD 30mA Type B</text></svg>",
        "tool_call_pending_for_pdf_png": true
      },
      "diversity_basis": {
        "load_type": "ev_charger",
        "factor_applied": 1.00,
        "method": "no_diversity",
        "citation": "BS 7671:2018+A2:2022 Reg 722 + OZEV CoP §4.3 + IET CoP for EVCI 4th ed. §8.5"
      }
    },
    {
      "circuit_id": "C05",
      "way_module_id": "W5",
      "designation": "EV charge point #4 (7 kW Mode 3 Type 2)",
      "voltage_class": "LV_power",
      "downstream_load_kw": 7.36,
      "phase": "L1",
      "ocpd": {"type": "MCB", "rating_a": 32, "curve": "C", "breaking_capacity_ka": 6},
      "rcd": {"required": true, "type": "B", "sensitivity_ma": 30},
      "cable": {"csa_mm2_or_awg": "6mm²", "cores": 3, "length_m": 26},
      "circuit_label": {
        "text": "C05 | EV CP#4 7kW Mode 3 | L1 | MCB 32A | 6mm² T&E | RCD 30mA Type B",
        "svg": "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"50mm\" height=\"12mm\" viewBox=\"0 0 50 12\"><rect width=\"50\" height=\"12\" fill=\"#FFFFFF\" stroke=\"#000000\" stroke-width=\"0.2\"/><text x=\"2\" y=\"3.5\" font-family=\"Arial\" font-size=\"2.5\" font-weight=\"bold\">C05</text><text x=\"6\" y=\"3.5\" font-family=\"Arial\" font-size=\"2.5\">EV CP#4 7kW Mode 3</text><text x=\"2\" y=\"7\" font-family=\"Arial\" font-size=\"2\">L1 | MCB 32A | 6mm² T&amp;E</text><text x=\"2\" y=\"10.5\" font-family=\"Arial\" font-size=\"2\">RCD 30mA Type B</text></svg>",
        "tool_call_pending_for_pdf_png": true
      },
      "diversity_basis": {
        "load_type": "ev_charger",
        "factor_applied": 1.00,
        "method": "no_diversity",
        "citation": "BS 7671:2018+A2:2022 Reg 722 + OZEV CoP §4.3 + IET CoP for EVCI 4th ed. §8.5"
      }
    },
    {
      "circuit_id": "C06",
      "way_module_id": "W6",
      "designation": "AC unit — single split (5 kW)",
      "voltage_class": "LV_power",
      "downstream_load_kw": 5,
      "phase": "L2",
      "ocpd": {"type": "MCB", "rating_a": 25, "curve": "C", "breaking_capacity_ka": 6},
      "rcd": {"required": true, "type": "A", "sensitivity_ma": 30},
      "cable": {"csa_mm2_or_awg": "4mm²", "cores": 3, "length_m": 18},
      "circuit_label": {
        "text": "C06 | AC single split 5kW | L2 | MCB 25A | 4mm² T&E | RCD 30mA Type A",
        "svg": "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"50mm\" height=\"12mm\" viewBox=\"0 0 50 12\"><rect width=\"50\" height=\"12\" fill=\"#FFFFFF\" stroke=\"#000000\" stroke-width=\"0.2\"/><text x=\"2\" y=\"3.5\" font-family=\"Arial\" font-size=\"2.5\" font-weight=\"bold\">C06</text><text x=\"6\" y=\"3.5\" font-family=\"Arial\" font-size=\"2.5\">AC single split 5kW</text><text x=\"2\" y=\"7\" font-family=\"Arial\" font-size=\"2\">L2 | MCB 25A | 4mm² T&amp;E</text><text x=\"2\" y=\"10.5\" font-family=\"Arial\" font-size=\"2\">RCD 30mA Type A</text></svg>",
        "tool_call_pending_for_pdf_png": true
      },
      "diversity_basis": {
        "load_type": "ac_single",
        "factor_applied": 1.00,
        "method": "no_diversity",
        "citation": "CIBSE TM50:2014 §4.2 + BS 7671:2018+A2:2022 Reg 552 — single AC unit at full demand"
      }
    },
    {
      "circuit_id": "C07",
      "way_module_id": "W7",
      "designation": "AC multi-split bank — 4 units × 3.5 kW each",
      "voltage_class": "LV_power",
      "downstream_load_kw": 14,
      "phase": "L1L2L3",
      "ocpd": {"type": "MCCB", "rating_a": 40, "curve": "D", "breaking_capacity_ka": 36},
      "rcd": {"required": true, "type": "A", "sensitivity_ma": 30},
      "cable": {"csa_mm2_or_awg": "10mm²", "cores": 5, "length_m": 25},
      "circuit_label": {
        "text": "C07 | AC multi-split 4×3.5kW | L1L2L3 | MCCB 40A | 10mm² T&E | RCD 30mA Type A",
        "svg": "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"50mm\" height=\"12mm\" viewBox=\"0 0 50 12\"><rect width=\"50\" height=\"12\" fill=\"#FFFFFF\" stroke=\"#000000\" stroke-width=\"0.2\"/><text x=\"2\" y=\"3.5\" font-family=\"Arial\" font-size=\"2.5\" font-weight=\"bold\">C07</text><text x=\"6\" y=\"3.5\" font-family=\"Arial\" font-size=\"2.5\">AC multi-split 4x3.5kW</text><text x=\"2\" y=\"7\" font-family=\"Arial\" font-size=\"2\">L1L2L3 | MCCB 40A | 10mm² T&amp;E</text><text x=\"2\" y=\"10.5\" font-family=\"Arial\" font-size=\"2\">RCD 30mA Type A</text></svg>",
        "tool_call_pending_for_pdf_png": true
      },
      "diversity_basis": {
        "load_type": "ac_group",
        "factor_applied": 0.81,
        "method": "largest_plus_remainder_pct",
        "method_params": {"largest_pct": 100, "remainder_pct": 75},
        "citation": "CIBSE TM50:2014 Table 4.3 — multi-split AC group: 100% largest + 75% remainder. 4 × 3.5 kW: 3.5 + 0.75×10.5 = 11.375 kW → factor = 11.375/14 = 0.81. Cite TM50 paywall-published table."
      }
    },
    {
      "circuit_id": "C08",
      "way_module_id": "W8",
      "designation": "Common-area lighting (continuous)",
      "voltage_class": "LV_power",
      "downstream_load_kw": 2,
      "phase": "L3",
      "ocpd": {"type": "MCB", "rating_a": 10, "curve": "B", "breaking_capacity_ka": 6},
      "rcd": {"required": true, "type": "A", "sensitivity_ma": 30},
      "cable": {"csa_mm2_or_awg": "1.5mm²", "cores": 3, "length_m": 35},
      "circuit_label": {
        "text": "C08 | Common-area lighting | L3 | MCB 10A | 1.5mm² T&E | RCD 30mA Type A",
        "svg": "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"50mm\" height=\"12mm\" viewBox=\"0 0 50 12\"><rect width=\"50\" height=\"12\" fill=\"#FFFFFF\" stroke=\"#000000\" stroke-width=\"0.2\"/><text x=\"2\" y=\"3.5\" font-family=\"Arial\" font-size=\"2.5\" font-weight=\"bold\">C08</text><text x=\"6\" y=\"3.5\" font-family=\"Arial\" font-size=\"2.5\">Common-area lighting</text><text x=\"2\" y=\"7\" font-family=\"Arial\" font-size=\"2\">L3 | MCB 10A | 1.5mm² T&amp;E</text><text x=\"2\" y=\"10.5\" font-family=\"Arial\" font-size=\"2\">RCD 30mA Type A</text></svg>",
        "tool_call_pending_for_pdf_png": true
      },
      "diversity_basis": {
        "load_type": "lighting_continuous",
        "factor_applied": 1.00,
        "method": "no_diversity",
        "citation": "IET OSG App A — continuous lighting load, no diversity"
      }
    },
    {
      "circuit_id": "C09",
      "way_module_id": "W9",
      "designation": "General sockets — 6 outlets",
      "voltage_class": "LV_power",
      "downstream_load_kw": 6,
      "phase": "L1",
      "ocpd": {"type": "MCB", "rating_a": 32, "curve": "B", "breaking_capacity_ka": 6},
      "rcd": {"required": true, "type": "A", "sensitivity_ma": 30},
      "cable": {"csa_mm2_or_awg": "2.5mm²", "cores": 3, "length_m": 40},
      "circuit_label": {
        "text": "C09 | General sockets 6× | L1 | MCB 32A | 2.5mm² T&E | RCD 30mA Type A",
        "svg": "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"50mm\" height=\"12mm\" viewBox=\"0 0 50 12\"><rect width=\"50\" height=\"12\" fill=\"#FFFFFF\" stroke=\"#000000\" stroke-width=\"0.2\"/><text x=\"2\" y=\"3.5\" font-family=\"Arial\" font-size=\"2.5\" font-weight=\"bold\">C09</text><text x=\"6\" y=\"3.5\" font-family=\"Arial\" font-size=\"2.5\">General sockets 6x</text><text x=\"2\" y=\"7\" font-family=\"Arial\" font-size=\"2\">L1 | MCB 32A | 2.5mm² T&amp;E</text><text x=\"2\" y=\"10.5\" font-family=\"Arial\" font-size=\"2\">RCD 30mA Type A</text></svg>",
        "tool_call_pending_for_pdf_png": true
      },
      "diversity_basis": {
        "load_type": "socket_general",
        "factor_applied": 0.55,
        "method": "largest_plus_remainder_pct",
        "method_params": {"largest_pct": 100, "remainder_pct": 40},
        "citation": "IET OSG App A — socket-outlets: 100% largest + 40% remainder. 6 × 1.5 kW: 1.5 + 0.4×4.5 = 3.3 kW → factor = 3.3/6 = 0.55."
      }
    }
  ],
  "selectivity_results": [],
  "compliance_summary": {
    "compliant": true,
    "non_compliance_flags": []
  },
  "flags": [],
  "rationale": {
    "chat_summary": "UK mixed-use SDB feeding 1 lift + 4 EV chargers + AC (single + grouped 4-unit multi-split) + lighting + general sockets. Per-circuit diversity_basis populated for all 9 circuits demonstrating 5 distinct load types: lift (Reg 559, 1.00), EV (Reg 722 + OZEV CoP, 1.00), AC single (TM50 §4.2, 1.00), AC group (TM50 Table 4.3, 100+75), sockets (OSG App A, 100+40), lighting (OSG App A, 1.00). Total demand = 62.115 kW = 99.7 A on 200 A TPN main (~50% headroom).",
    "sections": [
      {"title": "Why these load types", "summary": "Example chosen to demonstrate all 4 new diversity rows added in Sprint D2.3 (lifts + EV + AC single + AC group) plus tightened motor + socket citations. Mixed-use ground-floor common-area board is realistic UK scenario where all 5 load types coexist."},
      {"title": "Lift diversity (Reg 559 + WR9)", "summary": "C01 lift: factor 1.00. BS 7671 Reg 559 + IET WR9 + EN 81-20:2020 §5.10. Lift motors take full demand because starting transients (3-5× running current) plus emergency/fire-mode duty cycle preclude diversity. Type B RCD required for VFD-driven lift motors per Reg 559.5."},
      {"title": "EV diversity (Reg 722 + OZEV CoP)", "summary": "C02-C05 EV: factor 1.00 each. BS 7671 Reg 722 (statutory) references the OZEV CoP for EV Charging Equipment Installation (industry guidance). Per OZEV CoP §4.3, EV charging is treated as continuous load at full demand — no diversity. IET CoP for EVCI 4th ed. §8.5 concurs. Type B RCD required per Reg 722.531.3.101 (DC fault current detection)."},
      {"title": "AC diversity (TM50 §4.2 vs Table 4.3)", "summary": "C06 AC single: factor 1.00 (no diversity — single compressor at full demand). C07 AC multi-split group of 4 × 3.5 kW: factor 0.81 via CIBSE TM50:2014 Table 4.3 (100% largest + 75% remainder). Multi-split installations may apply this factor because simultaneous full-load operation under typical building thermal load profiles is rare. CIBSE TM50:2014 is paywalled — engineer-of-record must verify against the published edition."},
      {"title": "OZEV CoP industry-guidance status (honest disclosure)", "summary": "The OZEV Code of Practice for EV Charging Equipment Installation is INDUSTRY GUIDANCE, not statutory law. However, BS 7671 Reg 722 IS statutory and references the OZEV CoP. Both citations appear in every EV circuit's diversity_basis.citation field per the [[feedback-no-trim-non-consequential]] honest-disclosure rule."},
      {"title": "CIBSE TM50 paywall (honest disclosure)", "summary": "CIBSE TM50:2014 Table 4.3 is behind the CIBSE publication paywall. The diversity_basis.citation on C07 cites the table number explicitly so the engineer-of-record can verify against the published edition. INV-15 Rule 2 (citation contains a recognisable clause marker) enforces this disclosure on every TM-cited circuit."},
      {"title": "Board-level demand", "summary": "Sum of per-circuit demands: lift 11.0 + EV 4 × 7.36 + AC single 5.0 + AC group 11.375 + lighting 2.0 + sockets 3.30 = 62.115 kW. At 400 V TPN 0.9 pf: I = 99.7 A balanced on 200 A main — 50% headroom. Per-phase loading reasonably balanced (EV phases rotated by design)."}
    ]
  },
  "invariants": [
    {
      "id": "INV-12",
      "passes": true,
      "severity": "high",
      "evidence": "Diversity factor for shower-equivalent loads on this board: N/A (no instantaneous loads present). For the loads that ARE present, per-load-type factors applied per generator step; no blanket factor used. INV-12 Sprint B M1 rule (instantaneous loads must use 1.00) not triggered because no instantaneous-load circuits exist on this SDB."
    },
    {
      "id": "INV-14",
      "passes": true,
      "severity": "high",
      "evidence": "label_format_standard=BS matches jurisdiction=GB (Rule 1 PASS). board_label.text 'SDB-COMMON | 400 V TPN | Main Switch 200 A | —' matches BS regex (Rule 2-3 PASS). All 9 circuit_label entries populated with text + svg per BS template; no {{placeholders}} remain in any svg (Rules 4-5 PASS). tool_call_pending_for_pdf_png=true on board_label + all 9 circuits (Rule 6 PASS)."
    },
    {
      "id": "INV-15",
      "passes": true,
      "severity": "high",
      "evidence": "All 9 circuits carry diversity_basis. load_types: lift (×1), ev_charger (×4), ac_single (×1), ac_group (×1), lighting_continuous (×1), socket_general (×1) — all valid enum (Rule 1 PASS). Citations all ≥20 chars with clause markers (Reg, §, OSG, CoP, TM, Table) (Rule 2 PASS). Lift + 4 EV all factor=1.00 per regulation (Rule 3 PASS). C07 AC group method_params {largest:100, remainder:75} sums 175 ∈ [100,200]; C09 sockets {100,40} sums 140 ∈ [100,200] (Rule 4 PASS)."
    }
  ]
}
```

- [ ] **Step 7: Create uk-mixed-use-lifts-and-ev intent-out.json**

Write `electrical/db-layout/examples/uk-mixed-use-lifts-and-ev/intent-out.json`. Read the canonical intent shape from a sibling example (e.g. `electrical/db-layout/examples/uk-domestic-consumer-unit/intent-out.json`) to learn the shape. Typical shape (db-layout-intent — db-layout-rollup):

```json
{
  "$schema": "../../schemas/db-layout-intent.schema.json",
  "intent_type": "db-layout-rollup",
  "intent_version": "1.0.0",
  "produced_by": "electrical/db-layout/v1.4.0",
  "payload": {
    "boards": [
      {
        "db_id": "SDB-COMMON",
        "fed_from": null,
        "main_switch": {"type": "MCCB", "rating_a": 200, "breaking_capacity_ka": 36, "curve": "B"},
        "circuits": [
          {"id": "C01", "module_id": "W1", "designation": "Lift motor + controller", "downstream_load_kw": 11, "ocpd": {"rating_a": 32, "curve": "D", "type": "MCCB", "breaker_breaking_capacity_ka": 36}, "diversity_basis": {"load_type": "lift", "factor_applied": 1.00}},
          {"id": "C02", "module_id": "W2", "designation": "EV CP#1", "downstream_load_kw": 7.36, "ocpd": {"rating_a": 32, "curve": "C", "type": "MCB", "breaker_breaking_capacity_ka": 6}, "diversity_basis": {"load_type": "ev_charger", "factor_applied": 1.00}},
          {"id": "C03", "module_id": "W3", "designation": "EV CP#2", "downstream_load_kw": 7.36, "ocpd": {"rating_a": 32, "curve": "C", "type": "MCB", "breaker_breaking_capacity_ka": 6}, "diversity_basis": {"load_type": "ev_charger", "factor_applied": 1.00}},
          {"id": "C04", "module_id": "W4", "designation": "EV CP#3", "downstream_load_kw": 7.36, "ocpd": {"rating_a": 32, "curve": "C", "type": "MCB", "breaker_breaking_capacity_ka": 6}, "diversity_basis": {"load_type": "ev_charger", "factor_applied": 1.00}},
          {"id": "C05", "module_id": "W5", "designation": "EV CP#4", "downstream_load_kw": 7.36, "ocpd": {"rating_a": 32, "curve": "C", "type": "MCB", "breaker_breaking_capacity_ka": 6}, "diversity_basis": {"load_type": "ev_charger", "factor_applied": 1.00}},
          {"id": "C06", "module_id": "W6", "designation": "AC single split", "downstream_load_kw": 5, "ocpd": {"rating_a": 25, "curve": "C", "type": "MCB", "breaker_breaking_capacity_ka": 6}, "diversity_basis": {"load_type": "ac_single", "factor_applied": 1.00}},
          {"id": "C07", "module_id": "W7", "designation": "AC multi-split", "downstream_load_kw": 14, "ocpd": {"rating_a": 40, "curve": "D", "type": "MCCB", "breaker_breaking_capacity_ka": 36}, "diversity_basis": {"load_type": "ac_group", "factor_applied": 0.81}},
          {"id": "C08", "module_id": "W8", "designation": "Common lighting", "downstream_load_kw": 2, "ocpd": {"rating_a": 10, "curve": "B", "type": "MCB", "breaker_breaking_capacity_ka": 6}, "diversity_basis": {"load_type": "lighting_continuous", "factor_applied": 1.00}},
          {"id": "C09", "module_id": "W9", "designation": "General sockets", "downstream_load_kw": 6, "ocpd": {"rating_a": 32, "curve": "B", "type": "MCB", "breaker_breaking_capacity_ka": 6}, "diversity_basis": {"load_type": "socket_general", "factor_applied": 0.55}}
        ]
      }
    ]
  }
}
```

If the actual db-layout-intent schema requires different field shapes (e.g. `breaker_rating_a` flat instead of nested `ocpd`), match the actual schema by reading `electrical/db-layout/schemas/db-layout-intent.schema.json` first. Diversity_basis on intent is OPTIONAL (additive) — if the intent schema doesn't yet declare it, append a permissive object property.

- [ ] **Step 8: Create uk-mixed-use-lifts-and-ev reasoning.md**

Write `electrical/db-layout/examples/uk-mixed-use-lifts-and-ev/reasoning.md` (~200 lines) covering the 7 rationale.sections of the output.json plus a closing "Operational summary" table. Cover:
1. Why these load types (demonstrating 5 distinct diversity rows)
2. Lift diversity (Reg 559 + WR9)
3. EV diversity (Reg 722 + OZEV CoP)
4. AC diversity (TM50 §4.2 single vs Table 4.3 grouped)
5. Motor citation tightening (Reg 552.1.1)
6. Honest disclosure — OZEV CoP industry-guidance status
7. Honest disclosure — CIBSE TM50 paywall
8. Board-level demand summary table

- [ ] **Step 9: Backport diversity_basis to 20 existing examples**

For each of the 20 existing db-layout example outputs (the same list as Step 8 of D2.2), add `diversity_basis` on every circuit. Use the per-load-type table from Step 3.

For each circuit, infer the `load_type` from the existing `designation` field:
- "Lighting" or "lighting" → `lighting_continuous`, factor 1.00, citation `"IET OSG App A — continuous lighting load, no diversity"`
- "Socket" or "ring" or "radial" → `socket_general`, factor 0.55 (approximate for a typical socket bank — engineer-overrideable), method `largest_plus_remainder_pct` {100, 40}, citation `"IET OSG App A — socket-outlets: 100% largest + 40% remainder"`
- "Cooker" or "oven" → `other_declared`, factor 0.6 (10A + 30% remainder per OSG App A cooker table), method `engineer_declared`, citation `"BS 7671:2018+A2:2022 § 311.1 + IET OSG App A — cooker: 10A + 30% remainder of demand above 10A"`
- "Shower" or "instantaneous water heater" → `shower` or `instantaneous_water_heater`, factor 1.00, citation `"BS 7671:2018+A2:2022 § 311.1 — instantaneous loads take full demand"`
- "Storage heater" → `storage_water_heater`, factor 1.00, citation `"IET OSG App A — storage heater continuous load"`
- "Motor" (single) → `motor_single`, factor 1.00, citation `"BS 7671:2018+A2:2022 Reg 552.1.1"`
- "MCC" or "Motor Control Centre" or multiple motors → `motor_group`, factor varies (compute 100% largest + 50% remainder), method `largest_plus_remainder_pct` {100, 50}, citation `"BS 7671:2018+A2:2022 Reg 552 + IET OSG App A motor section"`
- "Fire alarm" or "emergency lighting" → `fixed_resistive`, factor 1.00, citation `"IET OSG App A — fixed continuous-duty load"`
- "Comms" or "Data" or "UPS" → `fixed_resistive`, factor 1.00, citation `"IET OSG App A — continuous-duty load"`
- Anything else → `other_declared`, factor 1.00, method `engineer_declared`, citation `"BS 7671:2018+A2:2022 § 311.1 — engineer-declared single-load circuit"`

Add an INV-15 entry to each example's `invariants[]`:

```json
{
  "id": "INV-15",
  "passes": true,
  "severity": "high",
  "evidence": "All <N> circuits carry diversity_basis with valid load_type enum + factor_applied in [0.0, 1.0] (Rule 1 PASS). All citations ≥20 chars with recognisable clause markers (Reg/§/OSG/Table/CoP/TM) (Rule 2 PASS). No lift or ev_charger circuits on this board (Rule 3 N/A). Method_params present where method='largest_plus_remainder_pct' (Rule 4 PASS)."
}
```

- [ ] **Step 10: Update db-layout CHANGELOG (combined 1.4.0 entry covering D2.2 + D2.3)**

Edit `electrical/db-layout/CHANGELOG.md`. Add a new top entry:

```markdown
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
  lift (Reg 559 + WR9 + EN 81-20, factor 1.00), ev_charger (Reg 722 +
  OZEV CoP §4.3, factor 1.00), ac_single (TM50 §4.2, factor 1.00),
  ac_group (TM50 Table 4.3, 100% largest + 75% remainder). Motor +
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
- OZEV CoP for EV Charging Equipment Installation is INDUSTRY GUIDANCE,
  not statutory. BS 7671 Reg 722 IS statutory and references OZEV.
  Both citations appear in every EV circuit's diversity_basis.citation.
- CIBSE TM50:2014 is behind the CIBSE publication paywall. Table 4.3
  cited explicitly so engineer-of-record can verify.
- Templates/ directory deferred SVG-to-PDF rasterisation to runtime
  per [[runtime-project-boundary]]; tool_call_pending_for_pdf_png=true
  on every label entry.

### Schema migration impact
- circuit_label, diversity_basis, board_label become required after
  1.4.0. v1.3 IR consumers reading 1.4.0 outputs without awareness of
  these fields are unaffected (additive); consumers that DO consume
  them must be aware of the schema bump.
```

- [ ] **Step 11: Update db-layout manifest**

Edit `electrical/db-layout/skill.manifest.json`:
1. Bump `"version": "1.3.3"` → `"version": "1.4.0"`.
2. Register the new example in `examples[]`:

```json
"examples": [
  "electrical/db-layout/examples/intl-commercial-tpn-msb/",
  ... existing 19 entries ...
  "electrical/db-layout/examples/uk-mixed-use-lifts-and-ev/"
]
```

- [ ] **Step 12: Run gates + hand-check INV-15**

```bash
python3 scripts/validate-examples.py 2>&1 | tail -5
python3 functional_audit.py 2>&1 | tail -5

python3 -c "
import json
# uk-mixed-use-lifts-and-ev hand-check
d = json.load(open('electrical/db-layout/examples/uk-mixed-use-lifts-and-ev/output.json'))
print('Circuits with diversity_basis:')
for c in d['circuits']:
    db = c.get('diversity_basis', {})
    print(f'  {c[\"circuit_id\"]} ({db.get(\"load_type\")}): factor={db.get(\"factor_applied\")}, citation_chars={len(db.get(\"citation\", \"\"))}')

# Verify lift + EV factor=1.00 rule
lifts_and_evs = [c for c in d['circuits'] if c['diversity_basis']['load_type'] in ('lift', 'ev_charger')]
print(f'\\nLift + EV circuits: {len(lifts_and_evs)}')
for c in lifts_and_evs:
    assert c['diversity_basis']['factor_applied'] == 1.00, f'{c[\"circuit_id\"]} has factor != 1.00'
print('All lift + EV factor=1.00: PASS')

inv15 = next((i for i in d['invariants'] if i['id'] == 'INV-15'), None)
print(f'\\nINV-15 entry: {inv15 is not None}, passes={inv15[\"passes\"] if inv15 else None}')
"
```

Expected output:
- validate-examples: 225/225 (was 223 after D2.1 + D2.2; +2 from uk-mixed-use-lifts-and-ev output + intent-out)
- functional_audit: 1 finding unchanged
- All 9 circuits in new example have diversity_basis with citations
- Lift + 4 EV all factor=1.00
- INV-15 entry present

- [ ] **Step 13: Commit D2.3**

```bash
git add electrical/db-layout/
git commit -m "$(cat <<'EOF'
feat(db-layout): D2.3 diversity edge cases — lifts + EV + AC + motors + INV-15

Sprint D2 Item 7: per-circuit diversity_basis block surfaces the audit
trail of which regulation/standard authorises each circuit's diversity
factor. Extends Sprint B M1's per-load-type table with 4 new rows for
lifts (Reg 559), EV charging (Reg 722 + OZEV CoP), AC single (TM50
§4.2), and AC grouped (TM50 Table 4.3, 100+75).

Schema (db-layout-ir.schema.json):
- circuits.items.diversity_basis: required object with load_type (13-enum
  including lift, ev_charger, ac_single, ac_group, motor_group), factor
  in [0.0, 1.0], method enum, optional method_params {largest_pct,
  remainder_pct}, citation ≥20 chars with clause marker.

Generator prompt: per-load-type table extended with 4 new rows + 2
tightened citations (motor_single → Reg 552.1.1; motor_group → Reg 552 +
IET OSG App A motor section). Explicit no-diversity rules for lifts
(Reg 559 + WR9 + EN 81-20 §5.10) and EV chargers (Reg 722 + OZEV CoP
§4.3 + IET CoP for EVCI 4th ed. §8.5). AC grouped factor 100+75 per
CIBSE TM50:2014 Table 4.3.

Validator INV-15 added (HIGH, 4 rules):
1. diversity_basis present + valid enum values + factor in range
2. Citation contains clause marker (Reg/§/Table/OSG/CoP/TM)
3. Lift + EV hard rules: factor_applied == 1.00 always
4. method_params sum ∈ [100, 200] when method=largest_plus_remainder_pct
   (sockets 140 / motor group 150 / AC group 175)

Examples:
- Backport diversity_basis across 20 existing examples; load_type
  inferred from designation.
- NEW example uk-mixed-use-lifts-and-ev: 9 circuits across 5 distinct
  diversity rows in one mixed-use SDB. Total demand 62.115 kW on 200A
  TPN main (~50% headroom).

Honest disclosures preserved per [[feedback-no-trim-non-consequential]]:
- OZEV CoP is industry guidance, not statutory. BS 7671 Reg 722 IS
  statutory and references OZEV. Both cited in every EV circuit.
- CIBSE TM50:2014 paywall: table number cited explicitly.

Combined CHANGELOG [1.4.0] entry covers Sprint D2.2 (labels) + D2.3
(diversity). Manifest bumped 1.3.3 → 1.4.0. New example registered.

validate-examples.py: 225/225 across 4 passes (+2 from new example).
functional_audit.py: 1 finding unchanged.

Sprint D2 Items 6 + 7 closed. Next: D2.4 ship.
EOF
)"
```

---

## Task D2.4: Sprint D2 ship (Opus orchestrator + Sonnet verification fence)

**Files:**
- Create: `~/.claude/projects/-Users-linus-Desktop-DraftsMan-SKills-draftsman-skills/memory/sprint-D2-shipped.md`
- Modify: `~/.claude/projects/-Users-linus-Desktop-DraftsMan-SKills-draftsman-skills/memory/MEMORY.md`

- [ ] **Step 1: Dispatch Sonnet verification fence**

Use the Agent tool with `subagent_type: general-purpose` and `model: sonnet`. Prompt:

```
You are the Sprint D2 verification fence — Sonnet sub-dispatch before
the D2 ship. Confirm all 3 items shipped correctly.

Work from /Users/linus/Desktop/DraftsMan SKills/draftsman-skills

Run these checks IN ORDER and report PASS/FAIL per check:

Check 1 — Gates: validate-examples.py 225/225 + functional_audit.py 1 finding

Check 2 — D2.1 hand-check uk-rural-swa-submain:
  - SUBMAIN-CABLE cascade node has selection.cable_type=pvc_swa
  - selection.table_used=4D5A
  - selection.binding_constraint=vd_cumulative (vd 2.19% at 70 mm²)
  - _source cites BS 7671:2018+A2:2022 App 4 Table 4D5A method D
  - INV-12 entry in invariants[]
  - reasoning.md cites Sprint C.2 engineer_transcription_C2 disclosure

Check 3 — D2.1 hand-check uk-domestic-final-circuits refit:
  - Final circuit cascade nodes (ring/lighting/cooker/shower) have
    selection.cable_type=pvc_twin_earth
  - selection.table_used=4D1A
  - route.installation_method ∈ {C, A1, 100, 101, 102, 103}
  - reasoning.md narrates the 4D1A table walk + Sprint C.2 disclosure

Check 4 — D2.2 hand-check uk-domestic-consumer-unit (canonical BS):
  - label_format_standard=BS at root
  - board_label.text matches BS regex: starts with db_id, ' | ', voltage_v, ' V ', phase, ' | Main Switch ', rating, ' A | '
  - board_label.svg ≥50 chars AND contains no '{{' substring
  - All circuits have circuit_label.text matching BS regex (way | description | phase | OCPD | cable | RCD)
  - All circuit_label.svg populated (no '{{' remnants)
  - INV-14 entry in invariants[]

Check 5 — D2.2 templates/ directory:
  - electrical/db-layout/templates/ exists with 6 files:
    bs-7671-circuit-label.svg.template, nec-408-4-circuit-label.svg.template,
    iec-60364-5-51-circuit-label.svg.template, bs-7671-board-label.svg.template,
    nec-408-4-board-label.svg.template, iec-60364-5-51-board-label.svg.template
  - Each template contains {{placeholder}} substitution points
  - manifest calculations[] includes shared/calculations/electrical/render-label.json

Check 6 — D2.3 hand-check uk-mixed-use-lifts-and-ev:
  - 9 circuits, all with diversity_basis (load_type + factor + method + citation)
  - Lift circuit (C01) factor_applied = 1.00
  - All 4 EV circuits (C02-C05) factor_applied = 1.00
  - AC group (C07) method=largest_plus_remainder_pct with params {100, 75}
  - All citations ≥20 chars and contain Reg/§/Table/OSG/CoP/TM
  - INV-15 entry in invariants[]

Check 7 — D2.3 backport: 20 other db-layout examples have diversity_basis on every circuit, each with INV-15 entry.

Check 8 — Version + CHANGELOG sync:
  - cable-sizing: manifest 1.1.0, CHANGELOG top [1.1.0]
  - db-layout: manifest 1.4.0, CHANGELOG top [1.4.0]
  - No db-layout [next-patch] header (cleaned in D1.5)

If ANY check fails, STOP. Re-dispatch the failing-item implementer with the failure detail before proceeding.

Report format:
PASS/FAIL | Check N | <detail>
Final verdict: SHIP | HALT
Summary: 2-3 sentences.
```

- [ ] **Step 2: Read fence report; halt + redispatch on FAIL**

If any check FAILS: redispatch the corresponding D2.1/D2.2/D2.3 implementer with the failure detail; do NOT proceed.

- [ ] **Step 3: Write `sprint-D2-shipped.md` memory file**

Write to `/Users/linus/.claude/projects/-Users-linus-Desktop-DraftsMan-SKills-draftsman-skills/memory/sprint-D2-shipped.md`:

```markdown
---
name: sprint-D2-shipped
description: Sprint D2 (Sizing & Boards depth) shipped 2026-05-26 — 3 within-skill depth items across cable-sizing + db-layout. cable-sizing v1.0.2→v1.1.0 (PVC/SWA tables 4D1A + 4D5A consumers + INV-12 + new uk-rural-swa-submain example); db-layout v1.3.3→v1.4.0 (board+circuit labels per BS/NEC/IEC + 6 SVG templates + INV-14, diversity edge cases lifts+EV+AC+motors + INV-15 + new uk-mixed-use-lifts-and-ev example). validate-examples 225/225; functional_audit 1 finding unchanged. D3 (small-power depth) next.
metadata:
  type: project
---

Sprint D2 (Sizing & Boards depth) shipped 2026-05-26. Second of three
within-skill-depth sprints per [[within-skill-depth-plan]]. Three
sequential Opus/Sonnet implementer tasks (D2.1 → D2.2 → D2.3) + Sonnet
8-check verification fence at ship.

## Items shipped

**D2.1 — cable-sizing PVC/SWA edge cases (Opus, v1.0.2 → v1.1.0)**
- Schema: cable_type enum extended with pvc_twin_earth + pvc_swa;
  new table_used field referencing BS 7671 4D-series + NEC + IEC tables
- Generator step: full cable_type → table_used compatibility matrix
- INV-12 (HIGH): cable_type ↔ table_used consistency + method validity
  + citation + Sprint C.2 honest-disclosure enforcement
- Refit uk-domestic-final-circuits: final circuits switched from
  incorrect pvc_singles to pvc_twin_earth + table_used 4D1A + method C
- NEW example uk-rural-swa-submain: 100 m direct-buried PVC SWA submain
  exercising Table 4D5A method D; walk-up to 70 mm² (binding_constraint
  = vd_cumulative); CPC alternative per Reg 543.2.5
- Honest disclosure: 4D1A + 4D5A engineer_transcription_C2 status
  surfaced in CHANGELOG + INV-12 + both example reasoning.md files

**D2.2 — db-layout board + circuit labels (Sonnet, partial 1.3.3 → 1.4.0)**
- Schema: label_format_standard (BS|NEC|IEC) + board_label + per-circuit
  circuit_label, all required after 1.4.0
- NEW templates/ directory with 6 .svg.template files (BS/NEC/IEC ×
  circuit/board), mirroring arc-flash-labelling pattern
- Generator step: per-jurisdiction text format + SVG template population
- INV-14 (HIGH, 6 rules): label_format_standard presence + jurisdictional
  alignment + text length + regex match per std + svg populated (no
  {{remnants) + tool_call_pending_for_pdf_png set
- Backport: 20 existing examples gain labels; no IE/load/OCPD changes
- Manifest: render-label calc registered

**D2.3 — db-layout diversity edge cases (Opus, full 1.3.3 → 1.4.0)**
- Schema: circuits.items.diversity_basis (load_type 13-enum +
  factor_applied [0.0,1.0] + method enum + optional method_params +
  citation), required on every circuit
- Generator step: per-load-type table extended with 4 new rows:
  - Lift: factor 1.00 (Reg 559 + WR9 + EN 81-20 §5.10)
  - EV charger: factor 1.00 (Reg 722 + OZEV CoP §4.3 + IET CoP EVCI)
  - AC single: factor 1.00 (TM50 §4.2)
  - AC group: 100% largest + 75% remainder (TM50 Table 4.3)
  Plus tightened motor_single (Reg 552.1.1) + motor_group (Reg 552 +
  OSG App A) citations.
- INV-15 (HIGH, 4 rules): presence + citation marker + lift/EV
  factor=1.00 hard rules + method_params sum range
- Backport: 20 existing examples gain diversity_basis on every circuit
- NEW example uk-mixed-use-lifts-and-ev: 9 circuits across 5 distinct
  diversity rows (lift + 4 EV + AC single + AC group + sockets +
  lighting). Total demand 62.115 kW on 200 A TPN main.
- Combined CHANGELOG [1.4.0] entry covers D2.2 + D2.3

## Gates final state

- validate-examples.py: AGGREGATE 225/225 across 4 passes (+4 over D1
  baseline 221: uk-rural-swa-submain ×2 + uk-mixed-use-lifts-and-ev ×2)
- functional_audit.py: 1 finding unchanged (motor-superposition oracle
  FP on us-industrial-with-motors/MCC-1; disclosed in D1.1 + D1.2 via
  ik3_basis enum + superposition_contribution_ka explicit block)

## Honest disclosures preserved

- **Sprint C.2 4D1A + 4D5A engineer_transcription_C2 status** surfaced
  in cable-sizing CHANGELOG, INV-12 Rule 4, generator prompt, and both
  example reasoning.md files.
- **OZEV CoP industry-guidance status** (not statutory law, but BS 7671
  Reg 722 IS statutory and references it) cited in every EV circuit's
  diversity_basis.citation + reasoning.md.
- **CIBSE TM50:2014 paywall**: Table 4.3 cited explicitly so the
  engineer-of-record can verify against the published edition.
- **SVG-to-PDF rasterisation deferred to runtime** per
  [[runtime-project-boundary]]; tool_call_pending_for_pdf_png=true on
  every label entry.

## Commits shipped (Sprint D2 chronological)

```
docs: Sprint D2 (Sizing & Boards depth) design spec
docs: Sprint D2 implementation plan
feat(cable-sizing): D2.1 PVC/SWA tables 4D1A + 4D5A consumers
feat(db-layout): D2.2 board + circuit labels (BS/NEC/IEC) + 6 SVG templates
feat(db-layout): D2.3 diversity edge cases — lifts + EV + AC + motors + INV-15
```

Plus any FIX-NEXT commits from the two-stage Opus review per task.

## Next

Per [[within-skill-depth-plan]]: Sprint D3 (small-power depth) closes
the final 2 within-skill items:
- Item 8: small-power special-locations design depth (swimming pool §702,
  medical Group 2 §710, EV charging §722 — 3 new examples; Opus)
- Item 9: small-power area-level diversity (building_diversity at IR
  root: office 0.75 / retail 0.85 / industrial 0.90 per CIBSE TM50 +
  IET OSG App A)
~2 Opus dev-days. After D3 ships, the within-skill depth program is
complete and the build pivots to breadth-first across the 92 stubs
per [[build-strategy-breadth-first]].

Related: [[within-skill-depth-plan]], [[sprint-D1-shipped]],
[[build-strategy-breadth-first]], [[feedback-no-trim-non-consequential]],
[[runtime-project-boundary]].
```

- [ ] **Step 4: Append memory index entry**

Edit `/Users/linus/.claude/projects/-Users-linus-Desktop-DraftsMan-SKills-draftsman-skills/memory/MEMORY.md`. After the existing `[Sprint D1 shipped]` line, append:

```markdown
- [Sprint D2 shipped (Sizing & Boards depth)](sprint-D2-shipped.md) — 2026-05-26: 3 depth items (D2.1 cable-sizing PVC/SWA 4D1A+4D5A consumers + new uk-rural-swa-submain example + INV-12; D2.2 db-layout BS/NEC/IEC labels + 6 SVG templates + INV-14; D2.3 db-layout diversity edge cases lifts+EV+AC+motors + new uk-mixed-use-lifts-and-ev example + INV-15); cable-sizing v1.1.0 + db-layout v1.4.0; gates 225/225 + 1 disclosed oracle FP; Sprint D3 (small-power depth) next
```

- [ ] **Step 5: Push commits**

```bash
git status  # verify working tree clean (all D2 commits committed)
git log --oneline c7caa28..HEAD  # spec was c7caa28; verify the D2 commits ahead
git push origin main
```

Expected: `~9–13 commits pushed` (plan + 3 implementer + 0-3 fix-passes + fence cleanup if needed). Verify by reading the push output.

- [ ] **Step 6: Sprint D2 done**

Sprint D2 is shipped. Two within-skill depth items remain (Sprint D3,
small-power). After D3 ships, the depth program is complete and the
build pivots breadth-first.

---

## Cross-references

- Sprint D2 design spec: `docs/superpowers/specs/2026-05-26-sprint-D2-sizing-boards-depth-design.md` (commit `c7caa28`)
- Sprint D1 plan (template for this plan): `docs/superpowers/plans/2026-05-25-sprint-D1-protection-safety-sprint.md`
- Sprint D1 shipped memory: `~/.claude/projects/.../memory/sprint-D1-shipped.md`
- Within-skill depth plan: `~/.claude/projects/.../memory/within-skill-depth-plan.md`
- Model selection rule: `~/.claude/projects/.../memory/feedback-no-haiku-sonnet-opus-only.md`
- No-trim policy: `~/.claude/projects/.../memory/feedback-no-trim-non-consequential.md`
- Runtime boundary: `~/.claude/projects/.../memory/runtime-project-boundary.md`
- SVG template canonical pattern: `electrical/arc-flash-labelling/templates/`
- Reused calc contract: `shared/calculations/electrical/render-label.json`
