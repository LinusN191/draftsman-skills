# cable-sizing Skill v1.0

Per-circuit cable selection for every cable run in a project's distribution cascade. Walks the standard csa ladder from below, accepts the smallest size that simultaneously satisfies `Iz ≥ In`, cumulative `Vd ≤ limit`, and the CPC adiabatic equation. Records the binding constraint and walk-up trail per node so tender reviewers can verify every selection without rerunning the calc.

## What this skill produces

For a given project cascade + consumed intents + engineer route data, the skill emits:

- **Per-cascade-node selection:** phase_csa + cpc_csa + insulation + cable_type + parallel_count + material
- **Binding constraint name** per node (`iz_vs_in` / `vd_cumulative` / `motor_starting_vd` / `cpc_adiabatic` / `parallel_required` / `harmonic_derating`)
- **Walk-up trail** — every csa tried and the reason it was rejected
- **All 4 engineering checks** — cumulative Vd, motor-starting Vd, parallel cables, harmonic derating
- **Rationale block** — 8-section narrative + chat_summary ≤500 chars

## Architecture: multi-skill consumer

- `consumes_intents: ["db-layout-rollup", "fault-level"]` — pulls topology + Ib + In + load_type from db-layout-rollup; pulls Ik" + X/R + Z from fault-level
- `produces_intent: "cable-sizing"` — consumed by 4 downstream skills (cable-schedule + riser + cable-containment + small-power v1.1)
- Hybrid input mode: when intents are absent, engineer declares circuits + per-node fault data inline
- WI3 tool-call deferral on `calc.cable_ampacity` / `calc.voltage_drop` / `calc.cpc_adiabatic` until runtime ships them

## Jurisdictions supported

- **GB** — BS 7671:2018+A2:2022 App 4 (ampacity) + App 12 (Vd) + Reg 433 + Reg 543
- **KE** — KS 1700:2018 §313 routing to BS 7671:2018+A2:2022 (KE engineering practice)
- **INT/EU** — IEC 60364-5-52 (ampacity + Vd) + Part 5-54 (earthing)
- **US** — NEC 2023 Chapter 9 Table 9 + 310.16 + 240.4(B) + 250.122 + 220.40

## Examples

| Folder | Scenario |
|---|---|
| `examples/uk-domestic-final-circuits/` | UK 230V single-phase domestic, copper PVC, 1.5-10 mm², lighting + power radial + 32A ring. Vd binding on lighting circuits. |
| `examples/ke-nairobi-commercial-with-msb/` | KE 415V TPN KPLC TN-S, 60-200 m² Nairobi commercial office. MSB → sub-DB → final circuits cascade. KS 1700:2018 §313 routing form. |
| `examples/intl-commercial-with-feeders/` | INT 400V TPN: TX → MSB → riser → DB-L1 → final circuits. Cumulative Vd, XLPE feeders, copper. |
| `examples/us-industrial-with-motors/` | US 480V industrial: aluminium feeder + AWG sizing + 500 hp motor with starting-Vd check + parallel cables for 1200A service entrance. |

## Out of scope (v1.0)

- DC circuit sizing (PV strings, EV DCFC, battery interconnects) — future `dc-cable-sizing` sibling
- IEC 60287 thermal modelling beyond standard tables (very large buried cable groups)
- Arc-flash incident-energy boundary marking — `arc-flash` sibling
- Communications / data cables (Cat6, fibre) — different standards family
- Time-graded protection curve coordination — handled by `db-layout` + future `protection-coordination`

See `CHANGELOG.md` for version history and `docs/engineering-philosophy.md` for the walk-the-ladder rationale.
