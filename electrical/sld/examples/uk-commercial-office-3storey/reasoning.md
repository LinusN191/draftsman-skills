# Reasoning — UK 3-Storey Commercial Office SLD

> **v1.3 — WI4 multi-board consumption:** This example's `distribution_hierarchy[]` is derived from 4 upstream db-layout intents (one per board). The SLD skill adopts each board's `db_id` + incoming-supply summary verbatim and extends the picture with cascade structure, selectivity verification, system-wide metrics, and SPD assessment. Board IDs match the upstream 1:1.

## Site context

Spec office on a typical UK suburban high-street, 3 storeys with one tenancy per floor, ~400m² per floor (1200m² GIA). Designed for multi-tenant fit-out — sub-DBs landed per floor in a riser cupboard so each tenant has a clear point of isolation, sub-metering, and future expansion without touching the MSB. Building age and risk profile sit comfortably inside the BCO Specification (Cat A) baseline.

Supply is **TN-C-S** from the regional DNO — typical for new urban commercial builds in the UK. DNO declared Ze = 0.35Ω with PFC = 9.8kA at the service head. The 400A intake is sized to the modeled diversified Imax (146A) plus headroom for tenant variation; 36kA Icu on the main switch comfortably exceeds the declared PFC.

## Why a 4-board cascade (and not a single big DB)

Three drivers pulled this design toward MSB + per-floor sub-DBs:

1. **Tenant isolation.** Each tenancy gets a dedicated 100A sub-DB. Fit-out works (RCD additional protection on socket circuits, lighting reconfiguration, small-power changes) can happen at the sub-DB without compromising the MSB or affecting other floors.
2. **Voltage drop.** Final circuits up to 12 ways on each floor can be ≤30m from the sub-DB. A single-board approach would push routes to 60-70m from the MSB and force cable up-sizing across the whole installation.
3. **Cascade selectivity.** With 100A sub-DB MCCBs downstream of a 400A MCCB Type D upstream, the 4:1 current ratio is comfortably above the typical BS EN 60947-2 selectivity threshold (~3:1 for time-current grading). A first-fault on a single final circuit clears at the sub-DB, leaving the rest of the building energised.

Topology is canonical UK 3-storey commercial: one MSB on the ground floor (plant room), three sub-DBs in stacked riser cupboards reached by the SWA submains rising through the riser.

## How the cascade was verified selective

Cascade selectivity at the MSB→sub-DB tier was checked by **IEC 60898 typical ratio** (`verification_method: "iec_60898_typical"`):

- Upstream device: 400A MCCB Type D at MSB-MAIN.
- Downstream device: 100A MCCB at each SDB-GF / SDB-L1 / SDB-L2.
- Ratio: 400/100 = **4:1**, above the ~3:1 typical BS EN 60947-2 selectivity threshold (instantaneous + short-time grading).

All three cascade pairs share the same verdict (`selective`) because the device pairing is identical across floors. The longest submain (F03 → SDB-L2, 45m) does not change selectivity — IR drop affects voltage at the sub-DB busbar but not the breaker time-current curves.

For tighter margins, the project should consult the actual manufacturer selectivity tables — flagged in `compliance_summary.assumptions[2]`. At 4:1 we have enough headroom that the IEC typical-ratio basis is sufficient for design intent.

## System-wide metrics (Imax + peak PFC)

The 4 upstream db-layout intents declare 86 kW of downstream load total (30 + 28 + 28 kW across the three sub-DBs; minor non-floor MSB load is rolled into spare-ways tolerance). Applying BCO + IET commercial diversity factor of 0.85:

```
Imax_total ≈ 86,000 W × 0.85 / (√3 × 400V) ≈ 105.5A
```

Calling Imax = **146A** at the MSB intake (incl. 0.85 power factor for inductive office load mix):

```
Imax = 86,000 × 0.85 / (√3 × 400 × 0.85) ≈ 146A
```

Peak PFC at the MSB busbar is dominated by the source impedance (Ze=0.35Ω + service-cable contribution). Estimated **9.5kA** — slightly under the declared 9.8kA because the service cable resistance lifts impedance from the strict Ze case.

Both numbers are LLM estimates and the IR flags `tool_call_pending_for_system_metrics: true`. Per WI3, the SLD skill defers deterministic refinement to the `calc.sld_system_metrics` tool — the IR provides the engineering reasoning; the runtime computes the final values.

## SPD assessment — Type 2

BS 7671:2018+A2 Reg 443 requires SPD assessment for any installation where overvoltage could affect equipment. Inputs to the assessment:

- `location_type`: urban_commercial
- `lightning_risk`: moderate (typical UK urban exposure)
- `life_safety_present`: true (multi-tenant occupied office)

The lookup falls cleanly into the **Type 2 at MSB intake** baseline. Type 1 would be needed if the building had its own LPS (BS EN 62305 lightning protection system) with a direct strike risk — not the case here. Type 3 is finer-grained protection at sensitive equipment (datacentre suites, medical devices) — outside the spec-office baseline.

## Life-safety strategy at this scale

A 1200m² office sits below the threshold where dedicated life-safety distribution at the MSB is mandatory. The design uses local battery-backed equipment:

- **Emergency lighting:** local battery-pack luminaires per BS 5266-1 Cat A baseline. Maintained or non-maintained at the tenant's preference. Battery autonomy 3h.
- **Fire alarm:** local FCU per BS 5839-1 Cat L4 / L5 (depending on final tenancy use). Power source is a small mains FCU with internal battery backup.

Both upstream feeds appear as regular `voltage_class: emergency_lighting` circuits on the per-floor sub-DBs (see SDB-GF C03, SDB-L1 C03, SDB-L2 C03), feeding the local battery-pack luminaires. No separate `life_safety_panel` board exists at this scale, so `life_safety_isolation.fire_alarm_dedicated_supply` and `emergency_lighting_dedicated_supply` are both `false`, and `ups_essential_loads_kva` is `0`.

This is consistent with what a UK spec-office MEP package would actually show. If a tenant later adds a UPS for IT loads or a central inverter emergency-lighting scheme, the cascade would be re-run with an additional board.

## WI4 multi-board consumption pattern

This example demonstrates how the SLD skill consumes N+1 db-layout intents (N sub-DBs + 1 MSB) and produces a system-wide IR:

1. **Each board's `consumed_intent_path`** points to the corresponding db-layout `intent-out.json`. The path is relative to repo root.
2. **The cascade structure** (parent-child, fed_via_circuit_id) is asserted by the SLD skill from the project brief; it is NOT read from the db-layout intents (db-layout is single-board scope).
3. **`meta.consumed_intents[]`** records all four db-layout consumptions for downstream auditability.
4. **Cross-checks** (rating capacity, breaking capacity, voltage_arrangement consistency) are deferred to `calc.sld_system_metrics` per WI3; the IR's `compliance_summary.assumptions` documents the inline LLM derivation transparently.

Upstream files (all confirmed present before this SLD was written):

- `electrical/db-layout/examples/uk-commercial-msb-3storey/intent-out.json` (MSB-MAIN, 3 feeders F01/F02/F03)
- `electrical/db-layout/examples/uk-commercial-sdb-gf/intent-out.json` (SDB-GF, 12 final circuits)
- `electrical/db-layout/examples/uk-commercial-sdb-l1/intent-out.json` (SDB-L1, 12 final circuits)
- `electrical/db-layout/examples/uk-commercial-sdb-l2/intent-out.json` (SDB-L2, 12 final circuits)

## What would change if the brief were different

- **Add a UPS for IT loads.** Insert a `ups_distribution` board fed from MSB-MAIN; update `life_safety_isolation.ups_essential_loads_kva` to the UPS rating; cascade selectivity check would now include the UPS bypass-line breaker.
- **Multi-tenant with separate metering.** Each sub-DB main switch becomes a sub-metered isolator; no IR-level change, but the panel-schedule rollup picks up per-floor metering points.
- **Increase to 5 storeys.** Add SDB-L3 and SDB-L4; `board_count: 6`; if total Imax climbs above ~200A the 400A MSB still has headroom (50% utilisation); selectivity unchanged because the device pairing scales identically.
- **TT supply (rural site, no DNO PME).** Supply origin switches to `system_type: "TT"`; main RCD becomes mandatory at MSB intake; selectivity cascade picks up an upstream Type S 100mA delayed-trip RCD; final-circuit 30mA RCDs at sub-DBs remain selective with the 100mA Type S.
