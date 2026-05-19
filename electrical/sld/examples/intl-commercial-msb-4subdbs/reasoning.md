# Reasoning — INT Commercial MSB + 4 Sub-DBs SLD

## Drawing layout (v1.5 — MULTI-SHEET demonstration fixture)

> **v1.5 — drawing layout with multi-sheet split:** This example is the canonical multi-sheet demonstration. The cascade grew from 5 boards (v1.4) to 9 boards (v1.5) by adding 4 sub-DBs (DB-EM + DB-COMMS + DB-UPS + DB-GENSET-XCV) as MSB-MAIN children via F05-F08.
>
> **Multi-sheet split triggers (both fire):**
> 1. **Hard count rule:** 9 boards > 8 threshold
> 2. **Functional isolation rule:** `fire_alarm_life_safety` (DB-FA1) coexists with `general_power` (DB-P1) and `lighting` (DB-L1) — life-safety isolation per BS 9999 §6.4 / IEC 60364-5-56:2018 §560 / NFPA 72 §10.6 mandates separate sheets
>
> **Sheet 1 — General power + mechanical (4 boards):**
> - MSB-MAIN (main, ground-floor plant room) — tree_layer 0
> - DB-L1 (lighting, via_main_spine)
> - DB-P1 (general_power, via_main_spine)
> - DB-M1 (mechanical, via_main_spine)
>
> **Sheet 2 — Life-safety + comms + emergency (5 boards):**
> - DB-FA1 (fire_alarm_life_safety, dedicated riser)
> - DB-EM (emergency_power, EM lighting central battery — BS EN 50171 3hr backup)
> - DB-UPS (emergency_power, 10 kVA UPS-backed critical loads, 30-min ride-through)
> - DB-COMMS (comms, MDF — Type B RCD upstream per IEC 60364-5-53:2002+A2:2015 §531.3.3 / BS EN 50173)
> - DB-GENSET-XCV (emergency_power, ATS standby genset — IEC 60364-5-56:2018 §552 utility-priority)
>
> Both sheets: A1 ISO, ISO 19650:2018 + BS 1192:2007+A2:2016 generic INT, NTS scale.
>
> **Cross-skill values preserved from v1.4:** `supply_origin.system_type=TN-C-S` (matches earthing intent, INV-11 check 6), `system_metrics.peak_pfc_ka=22.5 kA` (sourced from fault-level intent TX-1 transformer-secondary `ifault_ka_max`, INV-11 check 7 within ±0.5 kA tolerance) — INV-11 cross-skill checks still pass after the cascade grew from 5 to 9 boards. Peak PFC is a property of the utility supply, NOT of the cascade structure, so adding sub-DBs downstream does not shift it.
>
> **`meta.consumed_intents[]` grew 7 → 11:** 4 new db-layout intents (v1.3.0) added BEFORE the earthing + fault-level entries to preserve the v1.4 ordering rule (all db-layout first, then earthing, then fault-level). INV-11 cross-skill check on consumed_intents count + ordering still passes.
>
> **F05-F08 brief-authoritative caveat:** The 4 new feeders are asserted by `distribution_hierarchy_brief` and are NOT yet present in the upstream MSB intent at v1.3.0 (which carries F01-F04 only). The brief is authoritative at this growth-example tier; a v1.6 refresh of the MSB db-layout intent will reconcile by adding F05-F08 to the MSB panel schedule. Each new sub-DB's `incoming_supply.fed_from` documents its expected MSB feeder, so the downstream reconciliation is mechanical.

> **v1.3 — WI4 multi-board consumption:** This example's `distribution_hierarchy[]` is derived from 5 upstream db-layout intents (one MSB + 4 sub-DBs). The SLD skill adopts each board's `db_id` + incoming-supply summary verbatim and extends the picture with cascade structure, selectivity verification, system-wide metrics, SPD assessment, and life-safety isolation accounting. Board IDs match the upstream 1:1.

## Multi-skill consumption (v1.4)

> **v1.4 — multi-skill intent consumption:** This example consumes 3 upstream skill domains:
> - **db-layout** (5 intents — MSB + 4 sub-DBs) — per-board detail
> - **earthing** (1 intent, system-wide) — at `electrical/earthing/examples/intl-rural-tt/intent-out.json` (re-anchored to commercial TPN MSB in earthing v1.3 — folder name preserves history, content reflects TN-C-S commercial scope) — provides `system_type=TN-C-S`, `supply_bond_type=utility_pen_bond`, `ze_declared_ohm=0.30`; cross-checked against SLD `supply_origin` via INV-11
> - **fault-level** (1 intent, system-wide) — at `electrical/fault-level/examples/intl-commercial-with-genset/intent-out.json` — provides deterministic peak_pfc_ka at transformer secondary per IEC 60909-0:2016 cascade. Transformer-secondary `ifault_ka_max = 22.5 kA` → SLD `system_metrics.peak_pfc_ka = 22.5` (was LLM-estimated 15.5 in v1.3)
>
> **Genset-source filtering (bespoke v1.4 handling):** The fault-level intent models a 1600 kVA utility + 800 kVA standby genset (`source_summary.type == "mixed"`). SLD's `distribution_hierarchy` does NOT include genset topology — that is a fault-level domain concern, not an SLD one. SLD's `system_metrics.peak_pfc_ka` is sourced from the **utility-source worst-case** PFC at transformer secondary (worst case for breaker rating verification per IEC 60909-0:2016 §3.5). Engineers consulting this SLD MUST cross-reference the fault-level skill's full IR for genset-mode settings — particularly for protection coordination during genset-only operation when Ik" can be substantially LOWER, potentially falling below selectivity thresholds that hold under utility-source conditions.
>
> The PFC shift 15.5 → 22.5 kA does NOT trigger a non_compliance_flag: the 800A main switch has 50 kA Icu (IEC 60947-2), so 55% headroom remains. The downstream sub-DB Icu ratings (each 10–16 kA typical for MCCB at this scale) have not been re-verified against the cascade-reduced PFC in this v1.4 refresh — that step is part of the deferred WI3 sld_system_metrics tool.
>
> `meta.consumed_intents[]` grows from 5 entries (v1.3) to 7 entries (v1.4): 5 db-layout + 1 earthing + 1 fault-level. INV-11 enforces the count + ordering + cross-skill field equality (`supply_origin.system_type == earthing.system_type`, `system_metrics.peak_pfc_ka ≈ fault-level TX-1 ifault_ka_max` within ±0.5 kA tolerance).

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
