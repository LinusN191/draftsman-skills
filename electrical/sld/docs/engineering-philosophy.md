# SLD Engineering Philosophy — v1.3.0

## What SLD is

A logical-topology single-line diagram skill for LV distribution systems. Captures the cascade from utility supply through MSB to sub-DBs. Does NOT yet include drawing positions (Stage 2; deferred to v1.5.0+).

## What SLD is NOT

- Not a final-circuit schedule (db-layout owns per-board circuit detail)
- Not a renderer (no SVG/DXF/LISP output — runtime concern)
- Not a fault-current calculator (fault-level skill owns deterministic PSCC + selectivity calcs)
- Not an earthing system designer (earthing skill owns CPC + Zs + RCD)
- Not a panel-builder (db-layout owns single-board internals)

## How SLD relates to other skills

- **Consumes** `db-layout` intents (one per board in cascade) — WI4 pattern from earthing v1.3
- **Will consume** in future versions: `earthing` (Ze + supply_bond_type confirmation, SPD policy input), `fault-level` (deterministic PSCC + selectivity verification refinement) — v1.4.0+ work
- **Produces** `sld` intent for downstream skills: riser (vertical board distribution + cable routes), cable-containment (whole-installation cable schedules), maintenance docs (system overview), panel-schedule rollup

## Design principles

1. **System view, not board view.** SLD is the project-level summary that ties multiple db-layout boards into one cascade.
2. **Cascade selectivity is verified, not calculated.** Use breaker manufacturer typical curves + IEC 60898 conventions for the verdict. v1.3 doesn't add a calc tool; future v2 may.
3. **SPD assessment is rule-driven.** Per BS 7671 §443 / IEC 60364-4-44 / NEC 285 / KS 1700 §443. Lookup not math.
4. **Life-safety circuits are flagged + isolated.** Fire alarm + emergency lighting + UPS-fed essentials. Dedicated supplies; no upstream RCD per jurisdiction-specific clauses.
5. **System metrics are LLM-estimated in v1.3.** Imax_total + peak_pfc carry WI3 deferred flag until calc.sld_system_metrics ships.

## Versioning roadmap

- **v1.3.0** — this rebuild. Single-skill consumption (db-layout only). Logical topology only.
- **v1.4.0** — add earthing + fault-level intent consumption. Per-board provenance grows from N+1 → N+3 entries.
- **v1.5.0** — add drawing position layout (Stage 2). Schema gains `drawing_layout` field. Pairs with runtime renderer.
- **v2.0.0** — schema-breaking changes (e.g., consuming calc.sld_system_metrics outputs replaces the inline LLM estimates).
