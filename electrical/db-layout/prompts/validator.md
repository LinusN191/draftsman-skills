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

**INV-1: Board way accounting.**
`board.ways_used + board.ways_spare == board.ways_total`.

**INV-2: Circuit-to-way mapping uniqueness.**
Every `circuits[*].way_module_id` must be unique across all circuits in this IR.

**INV-3: Busbar rating coverage.**
`busbar.rating_a >= sum(circuits[*].ocpd.rating_a) × diversity_factor` (diversity from compliance_summary.assumptions OR default 0.7).

**INV-4: OCPD-cable coordination.**
For every circuit: `cable.csa_mm2_or_awg`'s ampacity (from jurisdiction ampacity table) >= ocpd.rating_a. Validate by jurisdiction:
- GB: lookup in BS 7671 Appendix 4
- EU/INT: lookup in IEC 60364-5-52 Annex E
- US: lookup in NEC Table 310.16

**INV-5: Breaker breaking capacity.**
For every circuit: `ocpd.breaking_capacity_ka >= ifault_at_downstream_ka` (from selectivity_results OR engineer declaration). If unknown, the selectivity_results entry MUST have `tool_call_pending: true`.

**INV-6: Busbar IcW coverage.**
`busbar.icw_ka_1s >= ipk_at_busbar` (per IEC 61439 short-circuit-withstand reference).

**INV-7: Symbol references.**
Every `drawn_as_symbols[*]` must be a valid symbol_id in `shared/standards/electrical/IEC60617/symbol-index.json`.

**INV-8: RCD requirement per jurisdiction.**
- TT system (consumed from upstream): every circuit must have `rcd.required: true`.
- TN-C-S + GB + socket-outlets ≤32A in domestic: `rcd.required: true` per BS 7671 411.3.3.

**INV-9: Selectivity result completeness.**
Every upstream-downstream OCPD pair must have a corresponding `selectivity_results[]` entry. No silent omissions.

**INV-10: Rationale presence.**
`rationale` block must exist with `chat_summary` (40-500 chars) and `sections` (≥1).

**INV-11: Standards citations format.**
Every `compliance_summary.non_compliance_flags[].code_clause` entry must use canonical format:
- BS 7671: `"BS 7671:2018+A3 Reg N.N.N"` or `"BS 7671:2018+A3 Table N.N"`
- IEC 60364: `"IEC 60364-N-NN:YYYY clause N.NN.N"`
- IEC 61439: `"IEC 61439-N:YYYY clause N.NN.N"`
- NEC: `"NEC 2023 Art NNN.NN"` or `"NEC 2023 Table NNN.NN"`

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

`valid: true` requires ALL of: schema pass, all 11 invariants pass, both intent projections valid.
