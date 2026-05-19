# Reasoning — US Strip Mall MSP + Tenant Sub-Panels SLD

## Multi-skill consumption (v1.4)

> **v1.4 — multi-skill intent consumption:** This example consumes 3 upstream skill domains:
> - **db-layout** (4 intents — MSP-A + 3 tenant/common sub-panels) — per-board detail (board IDs, incoming-supply summaries, circuit-level data)
> - **earthing** (1 intent, system-wide) — at `electrical/earthing/examples/us-commercial-nec/intent-out.json` — NEC 2023 §250 bonding context, `system_type=TN-S` cross-check against SLD `supply_origin.system_type` (match, no INV-11 flag)
> - **fault-level** (1 intent, system-wide) — at `electrical/fault-level/examples/us-strip-mall-retail/intent-out.json` — provides deterministic `peak_pfc_ka=23.78` kA at transformer secondary per IEC 60909-0:2016 cascade; NEC 2023 §110.9 AIC verification per breaker (MSP-A 25 kA AIC at 1.05× margin against 23.8 kA PFC)
>
> `meta.consumed_intents[]` grows from 4 entries (v1.3) to 6 entries (v1.4): 4 db-layout + 1 earthing + 1 fault-level.

## Drawing layout (v1.5)

> **v1.5 — drawing layout (spatial-intent layer):**
>
> - **1 sheet** (Arch_D ANSI, AIA CAD Layer Guidelines 2007, NTS scale)
> - **layout_groups:** `main` (MSP-A) + `general_power` × 3 (TSP-A, TSP-B, CA-P)
> - **routing_intent:** all tenant subs `via_main_spine` (gear-room to in-tenant cable runs)
> - **No multi-sheet split:** 4 boards ≤ 8 threshold; no NEC 517 healthcare or NFPA 72 fire-alarm boards
>
> CAD layer names resolved at render time from `shared/standards/drafting/AIA/cad-layers.json` (US uses AIA CAD Layer Guidelines).

> **v1.3 — WI4 multi-board consumption:** This example's `distribution_hierarchy[]` is derived from 4 upstream db-layout intents (1 MSP-A + 3 sub-panels). The SLD skill adopts each board's `db_id` + incoming-supply summary verbatim and extends the picture with cascade structure, selectivity verification, system-wide metrics, SPD assessment, and surfaces multi-board compliance tensions. Board IDs match the upstream 1:1.

## Site context

US strip-mall retail building — 2 tenant suites (Suite 100 apparel + Suite 200 food-service) + common area (parking-lot lighting, signage, fire-pump, exterior). 200A 208Y/120V 3-phase 4-wire utility supply, TN-S grounding (separate neutral from utility transformer secondary). Service-entry on north exterior wall in dedicated service room with NEMA 3R MSP-A panelboard.

Declared Ze = 0.10Ω, PFC = 22kA at service entrance. AIC rating 25kA on the 200A panelboard main (UL 891 listed). Note this is a relatively tight AIC margin (22kA actual vs 25kA rated = 16% margin) — typical US commercial practice, but the sub-panel AICs need careful sizing because of the short feeder runs to the tenant panels.

## Why a 4-board cascade — tenant isolation drives the topology

Strip-mall electrical topology is standard US small-commercial:

1. **Tenant isolation for billing + fit-out.** Each retail tenant gets a dedicated 100A 2-pole feeder from MSP-A. Sub-metering happens at MSP-A breakers (electronic meters or socket-meter modules); tenant fit-out works (re-circuiting for new fixtures, kitchen equipment, etc.) happen at the tenant sub-panel without disturbing other tenants or the main service.
2. **Common-area separation.** Parking-lot lighting, exterior signage, common HVAC, fire-pump — all landlord-side loads on a dedicated CA-P sub-panel. Keeps the meter trail clean for cost allocation and CAM (common-area maintenance) chargebacks.
3. **NEC 230.71 disconnecting-means requirement.** US Code limits the number of disconnecting devices at the service-entry to 6. With 200A main + 3 tenant/common feeders that's 4 devices — comfortably inside the limit. Going to a single MSB with 8+ tenant breakers at the service-entry would require a separate switchboard configuration.

## The MSP-A upstream intent mismatch — handled honestly

**Important authoring note:** The upstream MSP-A db-layout intent at `electrical/db-layout/examples/us-strip-mall-panelboard/intent-out.json` declares `voltage_v: 240` and `phase_arrangement: "single_phase_split"` with only 4 circuits modeled. This reflects an **earlier-draft single-phase MSP authoring snapshot** that wasn't updated for the 3-phase strip-mall scenario.

The downstream sub-panels (TSP-A, TSP-B, CA-P) all model `voltage_v: 208, phase_arrangement: "TPN"` — which IS consistent with the 208Y/120V 3-phase 4-wire building service called out in the SLD task brief.

The SLD adopts the **building-service voltage from the project brief (208Y/120V 3-phase)** since that's the canonical strip-mall scenario and matches the sub-panel intents. The MSP-A upstream voltage mismatch is recorded honestly in `compliance_summary.assumptions[1]` and flagged for db-layout follow-up — the SLD does NOT silently engineer-correct the upstream intent.

This is the pattern the SLD skill should use when upstream intents have authoring discontinuities: **adopt the most consistent representation (here: sub-panel + brief alignment on 208Y/120V), document the mismatch in assumptions, and flag the upstream for re-authoring** — rather than either propagating the mismatch silently or rewriting the upstream as a side-effect.

## Cascade selectivity — NEC scope is narrower than IEC

This is where US practice diverges from IEC. NEC does **NOT mandate full selective coordination for general commercial sub-panels** — selective coordination is required only for specific applications:

- **NEC 620.62** — elevator feeders
- **NEC 700.27 / 701.27** — emergency systems
- **NEC 517.17** — healthcare critical-branch + life-safety branch
- **NEC 645.27** — information technology equipment rooms (Article 645)

For a general retail strip-mall, partial selectivity at the MSP→TSP tier is acceptable as long as:

1. The series-rated AIC combination is listed per **NEC 240.86** (i.e., the manufacturer publishes a series-rating table showing the upstream + downstream pair has been tested together to the upstream's AIC rating).
2. The downstream branch protection still operates correctly during fault clearing.

In this example:

- **T01 (MSP-A 200A → TSP-A 100A) = 2:1 ratio** → partial_selective with verification_method `manual_review`. Below 3:1 typical IEC selectivity threshold, but acceptable for general retail per NEC 240.86 series-rated combinations.
- **T02 (MSP-A 200A → TSP-B 100A) = 2:1 ratio** → partial_selective. Same rationale. Note TSP-B has food-service kitchen equipment on Type D curves (C03/C04 cooking appliances, C05 walk-in cooler) — the D-curve inrush handling is local to TSP-B and doesn't affect MSP-A cascade.
- **T03 (MSP-A 200A → CA-P 60A) = 3.33:1 ratio** → selective with verification_method `iec_60898_typical`. Above the 3:1 threshold; common-area panel cleanly discriminates from MSP-A main.

Overall verdict: `partially_selective` (2 of 3 cascade pairs partial).

## The deliberate NEC 695.4(A) teaching scenario — CRITICAL flag

The CA-P common-area sub-panel carries a **fire-pump branch circuit** on C05 (60A Type D, 11.0 kW motor). This is intentionally **non-compliant** per NEC 695.4(A):

> **NEC 695.4(A)** — "The power supply to electric motor-driven fire pump(s) shall be from a fire-pump-rated tap ahead of the service-disconnecting means or from an independent source..."

A fire-pump on a shared common-area panel violates this rule because:

1. A fault on **any other CA-P circuit** (parking-lot lighting C01, signage C02, common HVAC C04, common-area cleaning sockets, etc.) could trip the upstream T03 60A feeder at MSP-A, **disabling the fire-pump during a fire event**.
2. Even ground-faults on the parking-lot photocell control circuits would propagate to T03 in the absence of proper fault clearance hierarchy.

**The SLD surfaces this honestly as a CRITICAL non_compliance_flag at the IR tier.** This is the key teaching point of this example: **multi-board compliance tensions only become visible when the SLD aggregates across db-layouts** — a single-board db-layout review of CA-P cannot see the fire-pump-on-shared-panel violation because the rule operates at the multi-board / service-entry topology level.

Remediation options surfaced in the flag message:

- **Option 1 (preferred):** Relocate the C05 fire-pump branch to a dedicated **FP-1 fire-pump controller** fed directly from MSP-A line-side (ahead of the MSP-A main disconnect). This creates a true tap-ahead-of-service-disconnect configuration per NEC 695.4(A).
- **Option 2:** Provide an **independent service drop** from the utility for the fire-pump (a separate meter + service entrance). More expensive but cleaner for sites with high-rise / multi-building scope.

The `compliance_summary.compliant: false` propagates to the intent-out.json's `compliant: false` — downstream consumers (BoQ tooling, design-review checklists, AHJ submittal packages) can pick up the flag and route to remediation.

## System-wide metrics (Imax + peak PFC)

The 3 sub-panel intents declare actual final-circuit loads:

```
TSP-A (Suite 100 apparel):     1.8+1.5+1.2+1.0+1.2+1.4+1.0+0.8         =  9.9 kW
TSP-B (Suite 200 food-svc):    1.6+1.5+2.2+2.2+4.5+1.0+1.8+1.0+0.8     = 16.6 kW
CA-P (common area):            3.5+1.8+1.2+1.5+11.0+0.6                = 19.6 kW
Total raw:                                                              = 46.1 kW
```

The MSP-A upstream rollup (4 circuits = 17 kW) is the earlier-draft snapshot mentioned above; not used as the authoritative basis.

Diversity 0.85 applied across the sub-panel summed loads (general retail commercial diversity):

```
Imax_total = 46.1 × 0.85 / (√3 × 208 × 0.85) ≈ 127A
```

Peak PFC at MSP-A busbar: declared 22 kA minus service-entrance impedance → ~21 kA. Sub-panel PFCs are lower at the feeder tier:

- TSP-A / TSP-B at ~30-40m feeder run → ~15-18 kA (within 22 kA AIC rating)
- CA-P at ~50-60m feeder run → ~12-14 kA (within 10 kA AIC; the feeder run helps here)

Both Imax and peak PFC are LLM estimates and the IR flags `tool_call_pending_for_system_metrics: true` — per WI3 the deterministic refinement is deferred to `calc.sld_system_metrics`.

## SPD assessment — Type 1+2 per NEC 285

US commercial SPD policy per NEC 2023 Article 285:

- **Type 1 at service-entry (NEC 285.23).** Installed ahead of the main disconnect at MSP-A — handles direct-strike via the utility service drop. 10/350 µs waveform protection. Suitable for strip-mall with potential rooftop exposure (signage, HVAC condensers).
- **Type 2 at branch panels (NEC 285.24).** Installed inside TSP-A, TSP-B, CA-P enclosures — handles residual transient surges after the Type 1 has clamped the main strike. 8/20 µs waveform protection.

Combined Type 1+2 assembly at MSP-A is the standard installation pattern at this scale (single device with both ratings, listed UL 1449). Separate Type 1 + Type 2 devices give finer control but add installation complexity — not justified for a 200A retail strip mall.

## WI4 multi-board consumption pattern (4 intents)

This example demonstrates the SLD consuming N+1 db-layout intents = **1 MSP + 3 sub-panels = 4 intents total**:

1. `electrical/db-layout/examples/us-strip-mall-panelboard/intent-out.json` (MSP-A; voltage mismatch flagged)
2. `electrical/db-layout/examples/us-strip-mall-tsp-a/intent-out.json` (TSP-A Suite 100, 8 circuits)
3. `electrical/db-layout/examples/us-strip-mall-tsp-b/intent-out.json` (TSP-B Suite 200, 9 circuits)
4. `electrical/db-layout/examples/us-strip-mall-common-area/intent-out.json` (CA-P, 6 circuits including fire-pump)

`meta.consumed_intents[]` records all 4 consumptions. AWG cable sizes in the upstream intents are NOT authored by the SLD — cable sizing remains the cable-sizing skill's responsibility per the runtime-project boundary; the SLD records the cable_csa_awg fields verbatim where surfaced in sample-schedule.md.

## What would change if the brief were different

- **Resolve the NEC 695.4(A) flag (preferred).** Remove C05 fire-pump from CA-P; add a 5th board `FP-1` fire-pump controller fed line-side of MSP-A main. Cascade gains an entry (utility → FP-1 ahead of MSP-A). `compliant: true`. Board count → 5.
- **MSP-A re-authored as proper 3-phase.** Update upstream db-layout intent to 208Y/120V 3-phase with the 3 actual T01/T02/T03 tenant feeders. SLD assumption[1] (the voltage mismatch note) becomes obsolete and is removed.
- **Add elevator.** Strip mall with 2 floors triggers elevator service. NEC 620.62 mandates selective coordination on the elevator feeder — requires manufacturer selectivity-table verification (not just IEC 60898 typical). Cascade verification_method on the elevator feeder becomes `manufacturer_table`.
- **Tenant adds restaurant with grease-load.** TSP-B C05 walk-in cooler scales up; new circuit for grease-trap booster heater + Type 2 hood exhaust + Type K cooktop. TSP-B sub-panel approaches its 100A feeder limit — may need TSP-B upsize to 125A 2-pole at MSP-A.
- **TT supply (not used in US).** US service is universally TN derived from utility transformer secondary; TT is not a US system type. Mentioned for IEC cross-reference only.

## Citation form — NEC only

All citations in `output.json` use **NEC 2023** form: e.g., `"NEC 2023 Article 250.24"`, `"NEC 2023 Article 695.4(A)"`. NFPA references (NFPA 72 fire-alarm, NFPA 101 life-safety) appear only in narrative `assumptions` text where required for context — never in `code_clause` fields. NO BS 7671, NO KS 1700, NO IEC 60364 references in the IR — this is the US example.

The verification script in Step 24.2 confirms zero `BS 7671` / `KS 1700` mentions in the IR — citation discipline is part of what makes this the reference US example.
