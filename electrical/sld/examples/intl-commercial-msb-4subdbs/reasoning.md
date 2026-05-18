# Reasoning — INT Commercial MSB + 4 Sub-DBs SLD

> **v1.3 — WI4 multi-board consumption:** This example's `distribution_hierarchy[]` is derived from 5 upstream db-layout intents (one MSB + 4 sub-DBs). The SLD skill adopts each board's `db_id` + incoming-supply summary verbatim and extends the picture with cascade structure, selectivity verification, system-wide metrics, SPD assessment, and life-safety isolation accounting. Board IDs match the upstream 1:1.

## Site context

Generic IEC commercial 4-floor office with mechanical plant. The brief is intentionally jurisdiction-neutral — the SLD here is the "international" reference example and ALL citations use the IEC 60364 family directly (no BS / KS / NEC cross-contamination). Treat it as the baseline IEC commercial pattern that local-jurisdiction examples (UK BS 7671, KE KS 1700, US NEC) layer on top of.

Supply is **TN-C-S** at 400V TPN+E with declared Ze = 0.30Ω and PFC = 16kA at the service head. The 800A intake is comfortably oversized vs the modeled diversified Imax (170A) — typical for a spec building expecting tenant fit-out variation across 4 floors. 50kA Icu on the main switch (IEC 60947-2) is deeply selective vs the declared PFC.

## Why a 5-board cascade with functional separation

The dominant design driver here is **functional separation by load class** rather than per-floor distribution (which the UK 3-storey example demonstrates). Three drivers pull this design to 4 dedicated feeders:

1. **Life-safety isolation.** DB-FA1 is a dedicated fire-alarm panel fed by F04 with NO upstream RCD per IEC 60364-5-56 §560. A first-fault elsewhere in the building must not disable fire-alarm functionality. Putting fire-alarm circuits on the same feeder as lighting or small-power would either force an upstream RCD (which trips on any earth-fault anywhere downstream) or force compromise on RCD additional-protection for sockets.
2. **Mechanical inrush isolation.** DB-M1 carries 8 motor circuits (M01-M06 with motor loads, M07 ELV control, M08 mechanical control). Type D upstream breakers on the M-circuits handle locked-rotor inrush without nuisance-tripping the upstream F03 250A MCCB. Keeping mechanical on its own feeder means the inrush profile doesn't propagate to lighting or small-power feeders.
3. **Tenant / discipline fit-out.** Lighting (DB-L1) and small-power (DB-P1) carry distinct fit-out cadences — lighting design may change with tenant occupancy, sockets change with desk layouts. Independent sub-DBs simplify the fit-out works.

DB-FA1 is the **key engineering decision** at the SLD level: it appears in the IR as `board_role: "fire_alarm_panel"` (not `sub_distribution_board`) and triggers `life_safety_isolation.fire_alarm_dedicated_supply: true` in `system_metrics`.

## DB-FA1 — life-safety isolation per IEC 60364-5-56 §560

The fire-alarm distribution pattern is what makes this example distinct from a standard 3-floor topology. The rules at the SLD tier:

- **No upstream RCD on F04.** IEC 60364-5-56 §560 requires that life-safety circuits (fire-alarm being the canonical case) are not subject to upstream RCD protection — a 30mA earth-fault upstream would trip the entire DB-FA1 panel and silence fire-alarm sounders / detection. Earth-fault clearance falls back to the TN-C-S adiabatic + 5-second rule per IEC 60364-4-41 §411.3.2.2.
- **Final circuits inside DB-FA1 also `rcd_protected: false`.** This is consistent — once the life-safety panel is established, you don't reintroduce RCDs at the final-circuit tier. Each fire-alarm device (sounder, detector, MCP, beacon, repeater, FCU) is on a small 6A or 10A Type C MCB with no RCD.
- **Cable routing implications.** Although not surfaced at the SLD tier (the cable-containment skill handles this), the F04 submain typically uses fire-rated cable (FP200 / Mineral Insulated / equivalent) to maintain circuit integrity during a fire event. The SLD IR doesn't author cable types but the design intent is captured in DB-FA1's `supply_class: "essential"`.

The `fire_alarm_panel` role on DB-FA1 makes the upstream RCD prohibition visible at the IR layer, which downstream tooling (renderer, panel-schedule generator, BoQ tool) can pick up to enforce the constraint.

## F02 partial selectivity — engineering honesty

F02 (800A Type D upstream / 400A downstream main) gives a 2:1 ratio — below the 3:1 IEC 60898 typical selectivity threshold. The SLD records this honestly:

- Cascade verdict: `partial_selective` (not `selective`).
- `_note` field on the cascade entry explains: ratio is 2.0:1, remediation options are (a) downsize DB-P1 main to 315A (gives 2.5:1, still below 3:1 — partial improvement only), (b) upsize MSB feeder to 1250A (gives 3.1:1, above threshold), or (c) accept partial selectivity and rely on the manufacturer's published selectivity table for the specific MCCB pair.
- `compliance_summary.assumptions[2]` documents the F02 rationale and explicitly states it is NOT a compliance failure — the cascade verdict captures the engineering caveat without rubber-stamping or escalating to a non-compliance flag.

This is the pattern the SLD skill should use throughout: **the IR records engineering caveats with traceable rationale, and uses non_compliance_flags only when a clear code violation exists (e.g., the KE example's 30mA-on-30mA RCD non-selectivity which violates KS 1700 §411.3.3 universal socket-RCD interpretation).**

## System-wide metrics (Imax + peak PFC)

The 4 upstream sub-DB intents declare actual final-circuit loads:

```
DB-L1 (lighting):    3.5+3.5+3.5+1.8+4.0+1.5+1.5  = 19.3 kW
DB-P1 (small-power): 5.5+5.5+5.5+3.0+3.0+2.5+3.5+4.5+4.5+4.5+3.5+2.0 = 47.5 kW
DB-M1 (mechanical):  11.0+7.5+11.0+7.5+5.5+4.0+2.0+1.5 = 50.0 kW
DB-FA1 (fire alarm): 0.5+0.2+0.2+0.2+1.5+0.4 = 3.0 kW
Total raw:                                       119.8 kW
```

Note that the **MSB upstream rollup F-feeders** (F01=80, F02=150, F03=100, F04=12 → 342 kW total) are oversized vs the actual sub-DB summed loads. This is normal: the MSB feeder rollup includes rated headroom for spare-way fit-out + future expansion. The SLD uses the **sub-DB summed loads as the authoritative basis** for Imax (more honest — captures the design-day load rather than the worst-case feeder rating).

Diversity is applied per load class (different mixes have different coincidence behaviours):

```
Lighting     19.3 × 0.95 = 18.3 kW  (high coincidence — most lighting on simultaneously)
Small-power  47.5 × 0.85 = 40.4 kW  (typical commercial diversity)
Mechanical   50.0 × 0.75 = 37.5 kW  (lower coincidence — not all motors at peak simultaneously)
Fire-alarm    3.0 × 1.00 =  3.0 kW  (always full draw — life-safety standby)
Total diverse                  99.2 kW

Imax_total = 99,200 / (√3 × 400 × 0.85) ≈ 168A → rounded to 170A
```

Peak PFC at MSB busbar: declared 16kA at the service head, minus ~0.05Ω service-tail impedance → ~15.5kA. Both values are LLM estimates and the IR flags `tool_call_pending_for_system_metrics: true` — per WI3 the deterministic refinement is deferred to `calc.sld_system_metrics`.

## SPD assessment — Type 2

IEC 60364-4-44 §443 SPD assessment inputs:

- `location_type`: commercial
- `lightning_risk`: moderate (typical urban / suburban exposure)
- `life_safety_present`: true (DB-FA1 + occupied tenancies)

The lookup is Type 2 at MSB intake. Type 1+2 would be triggered if the building had its own LPS (IEC 62305 lightning protection system) — not the case in this baseline brief. Type 3 (fine-grained at sensitive equipment) is outside the SLD scope and would be specified per discipline.

## WI4 multi-board consumption pattern (5 intents)

This example demonstrates the SLD consuming N+1 db-layout intents = **1 MSB + 4 sub-DBs = 5 intents total**:

1. `electrical/db-layout/examples/intl-commercial-tpn-msb/intent-out.json` (MSB-MAIN with F01-F04)
2. `electrical/db-layout/examples/intl-dbl1-lighting/intent-out.json` (DB-L1, 7 circuits)
3. `electrical/db-layout/examples/intl-dbp1-power/intent-out.json` (DB-P1, 12 circuits)
4. `electrical/db-layout/examples/intl-dbm1-mechanical/intent-out.json` (DB-M1, 8 circuits)
5. `electrical/db-layout/examples/intl-dbfa1-fire-alarm/intent-out.json` (DB-FA1, 6 circuits)

`meta.consumed_intents[]` records all 5 consumptions for downstream auditability. The cascade structure (parent-child, fed_via_circuit_id) is asserted by the SLD skill from the project brief; it is NOT read from the db-layout intents (db-layout is single-board scope).

## What would change if the brief were different

- **Add a UPS for IT loads.** Insert a `ups_distribution` board fed from MSB-MAIN; update `life_safety_isolation.ups_essential_loads_kva` to the UPS rating; cascade selectivity check would include the UPS bypass-line breaker. SLD board count → 6.
- **Add a central inverter emergency-lighting board.** Insert an `emergency_lighting_panel` role board fed from MSB-MAIN with NO upstream RCD (similar life-safety pattern to DB-FA1); `emergency_lighting_dedicated_supply` flips to true; DB-L1 L06 sustained-supply circuit becomes redundant.
- **Add site LPS (IEC 62305).** SPD assessment escalates to Type 1+2 combined at MSB intake. SPD policy lookup re-runs.
- **Generator backup.** Insert an automatic-transfer-switch (ATS) board between utility supply and MSB-MAIN; SLD supply_origin now records two sources (utility + generator) with the ATS as the supply-origin node. Life-safety loads (DB-FA1, central emergency lighting if present) get dedicated essential-side feeders from the ATS.
- **TT supply (rural site without DNO PME).** Supply origin switches to `system_type: "TT"`; main RCD becomes mandatory at MSB intake; but DB-FA1 still bypasses the main RCD per IEC 60364-5-56 §560 — the fire-alarm feeder is wired directly to the MSB busbar upstream of the main RCD, or a dedicated transformer creates a separate earthing reference for life-safety. This complicates the cascade and would require a manual_review on F04.

## Citation form — IEC only

All citations in `output.json` use the **IEC 60364** form (with year + section): e.g., `"IEC 60364-4-41:2005 §411.4"`, `"IEC 60364-5-56:2009 §560"`. NO BS 7671, NO KS 1700, NO NEC references — this is the international / generic example. The IEC 60898 (MCB) and IEC 60947-2 (MCCB) component standards are referenced where selectivity is discussed.

The verification script in Step 23.2 confirms zero `KS 1700` mentions in the IR — citation discipline is part of what makes this the reference INT example.
