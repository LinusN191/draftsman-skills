# Schematic Skill

**Status:** beta (v1.0.0)
**Discipline:** electrical → schematic_diagrams
**Standards:** BS EN 60617, BS EN 61082, IEC 60255, IEC 61850, NEC 2023, IEEE Std 315

## What this skill produces

Schematic control + protection diagrams as structured IR. One schematic = one IR document. Two categories:

- **Control schematics**: motor starter circuits (DOL / star-delta / VSD), contactor logic, sequence of operations, generator/UPS changeover
- **Protection schematics**: IDMT overcurrent, differential (87T / 87B), restricted earth fault (87N), motor protection (49/50/51/86), busbar protection

## Cross-skill integration (hybrid consumer)

When upstream intents are available:
- `db-layout-rollup` — upstream OCPD context (breaker type + rating + curve)
- `fault-level` — PFC at protected node + protection coordination
- `earthing` — system type + CPC return paths + earth-fault loop impedance

When intents absent (leaf-mode), engineer provides equivalent context via inputs.json.

## Jurisdictions covered

GB (BS 7671:2018+A2:2022), KE (KS 1700:2018 + BS 7671 routing), INT (IEC 60364-X-XX), US (NEC 2023 / NFPA 70).

## Outputs

- `schematic-ir.schema.json` — structured IR
- `schematic-intent.schema.json` — terminal intent for downstream consumption

## Examples

See `examples/` — 8 canonical examples spanning control + protection across all 4 jurisdictions.
