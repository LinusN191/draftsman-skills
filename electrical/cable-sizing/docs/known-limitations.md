# Known Limitations — Cable Sizing v1.0.0

What v1.0.0 does NOT cover. These are deliberate scope boundaries, not bugs.

## Out of scope (v1.0.0)

| Topic | Why not | Where it goes |
|---|---|---|
| DC circuit sizing (PV strings, EV DCFC, battery interconnects) | Different standards family (IEC 62548, NEC Art 690/706); different fault-current behaviour | Future `dc-cable-sizing` sibling skill |
| Arc-flash incident-energy + boundary marking | IEEE 1584 / NFPA 70E method is orthogonal to ampacity; different audience | Future `arc-flash` sibling skill |
| IEC 60287 advanced thermal modelling for buried groups | v1.0.0 uses the standard tables (BS 7671 App 4 / IEC 60364-5-52 Annex E / NEC Ch 9); buried-group thermal modelling is for utility-scale work | Either ship a separate `cable-thermal` calc tool or accept that very large buried groups need a specialist |
| Communications + data cables (Cat6, fibre) | TIA-568 / ISO/IEC 11801 — completely different standards family | `electrical/data-telecom` (separate skill) |
| Time-graded protection coordination | OCPD curve coordination — runs on top of fault-level data, not cable sizing | `electrical/db-layout` v1.1 + future `protection-coordination` |
| Cable joint / termination resistance | Specialist topic; rarely changes the csa selection | Out of scope indefinitely |
| Underground buried direct-vs-duct thermal interaction | Uses standard installation method D1/D2 ratings only | Specialist thermal study if very large |

## Inputs the skill cannot derive (require engineer)

These cannot come from any upstream intent and must be declared per segment:

- `length_m` — physical cable run length
- `installation_method` (A1-G / NEC categories)
- `ambient_c` if non-default
- `grouping_count` if non-1
- `in_thermal_insulation` if true
- `harmonic_content_pct` for IT / VFD / LED-heavy loads
- `terminal_temp_rating_c` for US jurisdiction (60/75/90°C)
- `locked_rotor_multiplier` per motor (NEMA class B/C, IEC class AA/AB)

If any are missing for a node, the generator sets `tool_call_pending: true` on that node
and emits an assumption — it never invents a number.

## Forward-compatibility caveats

- The emitted `cable-sizing` intent's `circuits[].phase_csa` / `cpc_csa` use `oneOf [number, string]` to accommodate IEC mm² (number) + NEC AWG (string like "1/0"). Downstream consumers must handle both.
- `cable_od_mm` and `weight_kg_per_m` are looked up at intent-emission time from `shared/standards/electrical/<juris>/cable-types-overview.md` / `chapter9-tables.json`. If a non-standard cable type is selected, these may be `null` and the consumer must look up.
