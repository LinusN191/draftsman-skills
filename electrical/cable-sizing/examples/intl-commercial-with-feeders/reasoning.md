# INT Commercial Cascade with Feeders — Worked Example

## Scenario

INT 400V TPN cascade — 4 nodes deep:
- `MSB-1` — service entrance 2000A
- `MSB-1.F03` — 65m riser feeder up to Level 3
- `MSB-1.F03.DB-L1` — DB incoming 63A sub-feeder
- `MSB-1.F03.DB-L1.C07` — long-run 48m lighting circuit

Both upstream intents present (`db-layout-rollup` + `fault-level`).

## Why C07 is vd_cumulative-binding

Each upstream segment contributes a fraction of the Vd budget:
- `MSB-1`: 0.4% (12m at 1450A, 630 mm²)
- `MSB-1.F03`: 1.4% segment, **1.8% cumulative**
- `MSB-1.F03.DB-L1`: 0.3% segment, **2.1% cumulative**

By the time we get to C07, only 0.9% of the 3% lighting limit is left for the 48m final
circuit. At 1.5 mm² the segment alone is 2.2% (4.3% cumulative — fail). At 2.5 mm² it's
1.3% (3.4% cumulative — still fail). At 4 mm² it's 0.8% (2.9% cumulative — pass).

`binding_constraint == "vd_cumulative"`, `walk_up_trail` shows all three steps.

## Why the upstream feeders are Iz-binding (not Vd)

The feeders are heavily sized for Iz headroom (Ib well under In, In well under Iz tabulated),
so Vd is comfortably small. The Vd budget gets consumed where Ib/L is highest relative to
csa — typically the final circuit.

## Forward-compat for downstream consumers

The emitted intent carries `cable_od_mm` + `weight_kg_per_m` per circuit so that the future
`cable-containment` skill can compute tray fill without needing to re-look-up the cable
type. The `parent_node_id` chain lets `riser` reconstruct floor-by-floor cable routing
exactly.

## tool_call_pending status

All 4 nodes carry `tool_call_pending: true`. The `vd_segment_pct` values shown are
senior-engineer estimates from IEC 60364-5-52 Annex G mV/A/m tables — runtime tool will
re-compute. The cumulative math is correct regardless (cumulative is just the sum).
