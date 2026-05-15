# Earthing Schematic — Validator Prompt

You are validating an earthing schematic IR document produced by the `electrical/earthing` skill generator.

## Input
- An IR JSON document at the user-provided path.
- The canonical schema at `electrical/earthing/schemas/earthing-ir.schema.json`.
- The intent schema at `electrical/earthing/schemas/earthing-intent.schema.json`.

## Validation procedure

### 1. Schema validation
Run JSON-schema validation against `earthing-ir.schema.json`.
- If invalid: STOP. Emit `{"valid": false, "stage": "schema", "errors": [...]}`.

### 2. Cross-field invariants

For each item below, emit a violation if the rule fails.

**INV-1: MET reference integrity.**
Every `circuits[*].cpc.terminated_at_met_id` must equal `met.id`.

**INV-2: Electrode jurisdiction-system match.**

| jurisdiction | earthing_system | electrodes required |
|---|---|---|
| GB | TN-C-S | ≥0 (PME — DNO provides earth) |
| GB | TT | ≥1 |
| EU/INT | TN-C-S | ≥0 |
| EU/INT | TT | ≥1 |
| US | TN-S (NEC default) | ≥2 supplemental electrodes per NEC 250.53(A)(2) unless one rod meets ≤25Ω |

**INV-3: Bonding completeness.**
If `extraneous_parts` (from inputs.json) lists any item, every item must appear in `main_bonding.conductors[]` OR be marked `bonded_via: "structural"` in the rationale.

**INV-4: CPC sizing method per jurisdiction.**

| jurisdiction | allowed cpc_sizing_method values |
|---|---|
| GB | `bs7671_table_54.7`, `bs7671_adiabatic_54.1` |
| EU/INT | `iec60364_table_54.2`, `iec60364_adiabatic_543.1.2` |
| US | `nec_table_250.122` |

**INV-5: Zs check arithmetic.**
For every circuit: `zs_calculated_ohm == ze_ohm + r1_ohm + r2_ohm` (within 0.001Ω rounding). And `zs_calculated_ohm ≤ zs_max_ohm`.

**INV-6: RCD requirement.**
- TT system: every circuit must have `rcd_required: true`.
- TN-C-S + GB + circuit serving socket-outlets ≤32A in domestic: `rcd_required: true` per BS 7671 Reg 411.3.3.

**INV-7: Symbol references.**
Every `drawn_as_symbols[*].symbol_id` must exist in `shared/standards/electrical/IEC60617/symbol-index.json`.

**INV-8: Rationale presence.**
`rationale` block must exist at root and contain `chat_summary`, all 8 taxonomy keys, and `decisions` array with ≥3 entries.

**INV-9: Standards citations.**
Every `compliance_summary.clauses_cited[]` entry must use exact clause format:
- BS 7671: `"BS 7671:2018+A3 Reg N.N.N"` or `"BS 7671:2018+A3 Table N.N"`
- IEC 60364: `"IEC 60364-N-NN:YYYY clause N.NN.N"`
- NEC: `"NEC 2023 Art NNN.NN"` or `"NEC 2023 Table NNN.NN"`

### 3. Intent extraction validation

Project the IR down to the intent shape declared by `earthing-intent.schema.json`. Validate against that schema. The intent must contain the stable subset: `jurisdiction, earthing_system, met_location, available_zs_at_main_db_ohm, electrode_target_met, circuits`.

## Output

Emit a single JSON object:

```json
{
  "valid": true | false,
  "stage": "schema" | "invariants" | "intent" | "passed",
  "errors": [
    {"code": "INV-N", "path": "$.circuits[2].cpc", "message": "..."}
  ],
  "warnings": [...]
}
```

`valid: true` requires ALL of: schema pass, all 9 invariants pass, intent extraction valid.
