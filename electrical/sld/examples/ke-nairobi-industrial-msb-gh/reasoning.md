# Reasoning — KE Nairobi Industrial MSB-GH SLD

> **v1.3 — WI4 multi-board consumption:** This example consumes 2 db-layout intents — the existing MSP-100 (8 final circuits including the gate-house submain at C08) and the new gate-house GH-DB (3 final circuits fed via C08). Board IDs match the upstream 1:1. Same site as the KE earthing example, viewed through the SLD-skill lens.

## Multi-skill consumption (v1.4)

> **v1.4 — multi-skill intent consumption:** This example consumes 3 upstream skill domains:
> - **db-layout** (2 intents — MSP-100 + GH-DB) — per-board detail
> - **earthing** (1 intent, system-wide) — at `electrical/earthing/examples/ke-nairobi-industrial-tn-s/intent-out.json` — provides `system_type=TN-S` (KPLC), `supply_bond_type=tn_s_separate_pe`, `ze_declared_ohm=0.80`; cross-checked against SLD `supply_origin` via INV-11
> - **fault-level** (1 intent, system-wide) — at `electrical/fault-level/examples/ke-nairobi-industrial/intent-out.json` — provides deterministic peak_pfc_ka per IEC 60909-0:2016 cascade with motor §3.8.1 threshold check (strict-rule motor exclusion documented in fault-level reasoning). Transformer-secondary `ifault_ka_max = 10.22 kA` → SLD `system_metrics.peak_pfc_ka = 10.2` (was LLM-estimated 9.5 in v1.3)
>
> The shift from 9.5 → 10.2 kA flips the MSP-100 Icu adequacy verdict: 10kA Icu < 10.2kA peak PFC by 0.2kA. A second non_compliance_flag (Icu shortfall) is now recorded alongside the v1.3 selectivity flag. Engineering team options: uprate main switch to 16kA Icu, or document cascade protection from the KPLC 11kV/415V transformer fuse with let-through energy analysis.
>
> KS 1700:2018 §312 routes to BS 7671:2018+A2 §313.1 for short-circuit interrupting verification — Kenya direct citation form per jurisdictional policy. The same routing applies to §434.5.1 for Icu adequacy.
>
> `meta.consumed_intents[]` grows from 2 entries (v1.3) to 4 entries (v1.4): 2 db-layout + 1 earthing + 1 fault-level. INV-11 enforces the count + ordering + cross-skill field equality.

## Drawing layout (v1.5)

> **v1.5 — drawing layout (spatial-intent layer):**
>
> - **1 sheet** (A1 ISO, KS 1700:2018 §313 routing to BS 1192:2007+A2:2016, NTS scale)
> - **layout_groups:** `main` (MSP-100) + `mechanical` (GH-DB for industrial loads)
> - **routing_intent:** GH-DB `via_main_spine` (60m submain from MSP)
> - **No multi-sheet split:** 2 boards ≤ 8 threshold, no fire_alarm_life_safety boards
>
> CAD layer names resolved at render time from `shared/standards/drafting/BS1192/cad-layers.json` (Kenya jurisdiction routes through BS 1192 via KS 1700:2018 §313 chain).

## Site context

Light engineering workshop on Enterprise Road, Nairobi Industrial Area. 1980s build. KPLC supply via dedicated 11kV/415V substation 180m down the road, terminating in a 100A TPN main switch at MSP-100 in the workshop's main switchroom. The gate house at the perimeter (60m away) has its own sub-DB (`GH-DB`) for security lighting, gate-controller power, and a small comms cabinet. The 60m submain (C08 in the MSP-100 schedule) is 10mm² 4-core SWA on outdoor cable tray, transitioning to buried duct under the access road.

Supply context matches the KE earthing example:

- **System type:** TN-S (separate-Earth cable from substation transformer star point; not TN-C-S because this is older 1980s infrastructure predating KPLC PME rollout in industrial areas).
- **Ze:** 0.80Ω, measured 2026-03-12 by KPLC, degraded from original 0.65Ω at 1987 commissioning due to slow sheath corrosion on the separate-Earth cable.
- **Declared PFC:** 9.8kA at intake.
- **Main switch:** 100A TPN with shrouded busbars per BS EN 60947-3 (which KS 1700 §531 accepts via Annex E adoption pathway).

## Why a 2-board cascade

Drivers for breaking out a gate-house sub-DB rather than extending final circuits all the way:

1. **60m distance.** Direct final circuits from MSP-100 to the gate house would face severe voltage drop and clutter MSP-100's spare ways. The submain + sub-DB pattern is the canonical industrial-yard topology.
2. **Local isolation.** Gate-house security staff need a clearly labelled isolation point. The GH-DB provides that without requiring access to the main switchroom.
3. **Voltage drop.** With 10mm² SWA at 40A loading, 60m gives ~2.5% Vd on the submain — leaving ~1.5% budget for final circuits inside the gate house (well within the KS 1700 §525 ≤4% combined limit).

The cascade structure is therefore:

```
KPLC TN-S 415V intake
        |
    [Ze=0.80Ω]
        |
    MSP-100 (100A TPN, 10kA Icu)
        |
    [C08: 40A MCB Type B + 30mA Type A RCD]
        |
    [60m 10mm² 4-core SWA, outdoor tray + buried duct]
        |
    GH-DB (40A intake, single-phase 240V, 3 final circuits)
```

## The selectivity flag — engineering substance

This is the technical heart of the example. The MSP-100 → GH-DB cascade is **only partially selective**, for two independent reasons:

### Overcurrent grading

- Upstream device at C08: **40A MCB Type B**
- Downstream max at GH-DB: **16A MCB Type B** (C02 socket circuit)
- Ratio: **40 / 16 = 2.5:1**

The BS EN 60898 typical selectivity threshold for cascaded Type B MCBs is approximately 3:1. At 2.5:1 we are below that threshold — meaning a high-current short on a GH-DB final circuit could trip the upstream C08 before the local GH-DB MCB clears. Verification by manufacturer time-current curves (`verification_method: "manufacturer_table"`) might recover full selectivity in some product ranges, but the design-intent verdict at IR level is `partial_selective` with `verification_method: "manual_review"` — capturing the engineering reality rather than papering over it.

### RCD interaction

- Upstream RCD at C08: **30mA Type A** (per the MSP-100 db-layout intent)
- Downstream RCDs at GH-DB: **30mA Type A** on C02 (socket) and C03 (comms)

Cascaded 30mA-on-30mA RCDs are **non-selective by design**. RCD selectivity requires the upstream device to be a Type S (delayed-trip) at a higher sensitivity — typically Type S 100mA delayed. Without that, any earth-leakage fault on a GH-DB final circuit will trip both the local 30mA RCD AND the upstream 30mA RCD at MSP-100 C08 — taking out the entire gate-house including security lighting.

### Two compliant resolutions

The IR captures both as recommendations in `compliance_summary.non_compliance_flags[0]` and `assumptions[4]`:

1. **Upgrade upstream to 100mA Type S delayed RCD at MSP-100 C08.** RCDs become selective (Type S waits 40ms before tripping; downstream 30mA clears the fault first). Overcurrent grading still marginal at 2.5:1 — but RCD discrimination is the bigger issue and this resolves it.
2. **Remove the GH-DB 30mA RCDs** and rely on the upstream C08 30mA RCD for additional protection at sockets per KS 1700:2018 §411.3.3. This makes the cascade trivially "selective" because there is only one RCD in the chain. The downside: an earth fault on the comms-cabinet circuit (C03) trips the entire gate-house. For a small remote DB this is often acceptable.

Either path makes the cascade compliant. The current as-built design is non-compliant at the IR level (`compliant: false` with one warning flag).

## Why Type 1+2 SPD (not Type 2)

The UK 3-storey office example uses Type 2 SPD because the urban-commercial supply has very limited exposure to direct lightning strike. Nairobi industrial sites are a different threat profile:

- **Overhead KPLC distribution** for the last ~80m before the substation transformer, with limited surge protection on the KPLC side.
- **Atmospheric exposure** — Nairobi sits at ~1,800m elevation with intense electrical storms from the escarpment effect.
- **KS 1700 §443 + KS-unique deviations index** explicitly recommend combined Type 1+2 for sites with overhead supply exposure.

The Type 1+2 combined assembly is therefore a Kenya-specific design call, not a transcription of the BS 7671 baseline. This is one of the places where KS 1700 diverges from BS 7671 in practice even though the clause text is similar.

## Citation form

All citations in this example use the **direct KS 1700:2018 §X.Y.Z form** — never the inverse pattern "BS 7671 §X.Y.Z (adopted by KS 1700)". The KS 1700 standard is the primary reference for Kenya, with Annex E providing the adoption pathway when an engineer needs to verify the BS-equivalent clause text. The SLD IR does not need to surface that mapping — that's a KS1700 standards-layer concern.

Specific clauses invoked:

- `KS 1700:2018 §411.4` — TN-S system definition (Annex E adoption of BS 7671 411.4)
- `KS 1700:2018 §411.3.3` — universal socket-RCD requirement (KS-unique tightening of BS 7671 411.3.3)
- `KS 1700:2018 §433.1.1` — main-switch capacity rule
- `KS 1700:2018 §443` — SPD selection policy
- `KS 1700:2018 §525` — voltage-drop limit ≤4% combined
- `KS 1700:2018 §531` — equipment marking acceptance
- `KS 1700:2018 §536` — selectivity / discrimination

## System metrics — how the numbers were derived

MSP-100 db-layout intent declares 8 circuits totalling 33.2 kW downstream load (1.2 + 0.8 + 5.0 + 3.0 + 5.5 + 2.2 + 7.5 + 8.0 kW). Applying mixed-industrial diversity factor 0.75:

```
Imax_total ≈ 33,200 W × 0.75 / (√3 × 415V × 0.85 PF)
           ≈ 24,900 / 611
           ≈ 41A
```

At MSP-100 busbar Imax is 41A vs 100A intake — 41% utilisation, 59% headroom. Plenty of room for tenant growth.

Peak PFC at MSP-100 busbar is taken as **9.5kA** (slightly under the declared 9.8kA accounting for the short service-tail impedance). The MSP-100 main-switch Icu of 10kA is within ~5% margin — tight by UK standards but consistent with typical Kenyan industrial practice. If KPLC ever upgrades the substation transformer the PFC could climb; flagged in compliance_summary for future re-evaluation.

At GH-DB after 60m of 10mm² 4-core SWA the PFC drops dramatically:

```
R_loop ≈ 2 × 60m × 0.00183 Ω/m ≈ 0.22Ω (4-core SWA, copper, 70°C)
Plus Ze of 0.80Ω (carried through the TN-S CPC).
At single-phase 240V: PFC ≈ 240 / 1.02 ≈ 235A — well within 6kA Icu typical for the GH-DB main switch.
```

Wait — that's the earth fault current, not the prospective short-circuit current. For 3-phase short across the 4-core SWA, PFC at GH-DB would be in the 3-4 kA range, which is what the rationale section says. Either way, GH-DB equipment is comfortable.

Per WI3, all of these are LLM derivations flagged with `tool_call_pending_for_system_metrics: true`. The deterministic refinement is deferred to `calc.sld_system_metrics`.

## WI4 multi-board consumption — comparison to UK example

The UK example consumes 4 db-layout intents (1 MSB + 3 sub-DBs) and produces a fully-selective, compliant SLD. This KE example consumes 2 intents (1 MSB + 1 sub-DB) and produces a partial-selective, non-compliant SLD with two recommended resolutions. Both demonstrate the same WI4 consumption pattern; the engineering verdict differs because the device pairing in this real-world brief has a genuine discrimination problem.

This is a feature, not a bug — the worked examples show what a senior engineer would actually flag rather than pretending every cascade lands cleanly selective.

Upstream files (confirmed present before this SLD was written):

- `electrical/db-layout/examples/ke-nairobi-industrial-100A-tpn/intent-out.json` (MSP-100, 8 final circuits including C08 submain)
- `electrical/db-layout/examples/ke-nairobi-gh-db/intent-out.json` (GH-DB, 3 final circuits, NEW from this sprint Task 5)

## What would change if the brief were different

- **TN-C-S (modern KPLC industrial estate).** Ze drops to ~0.3-0.4Ω; PFC climbs to ~15kA; main-switch Icu needs to rise to 16kA. SPD selection unchanged (still Type 1+2 because of overhead exposure).
- **Add a workshop UPS for CNC controllers.** Insert a `ups_distribution` board fed from MSP-100; cascade selectivity check now includes the UPS bypass-line breaker; life_safety_isolation.ups_essential_loads_kva captures the rating.
- **Upgrade gate-house intake to 60A 3-phase.** GH-DB role becomes a small TPN sub-DB; cascade ratio improves if C08 is uprated to 63A; the RCD-on-RCD problem still requires resolution unless upstream goes Type S.
- **Remove gate house from project scope.** SLD collapses to single-board (just MSP-100) and degenerates to a single db-layout consumption — which is the trivial degenerate case of the WI4 pattern.
