# Reasoning — INT DB-UPS (UPS-Backed Critical-Loads Sub-DB)

## Site context

UPS-backed critical-loads sub-DB for the generic IEC commercial 3-storey office building. DB-UPS is the dedicated distribution downstream of a 10 kVA online double-conversion UPS unit, which itself is fed from MSB-MAIN F07 (50A MCB Type C) via a 40m utility-side feeder. The board sits on the UPS-output bus and feeds 6 critical loads: the primary server rack (6 kVA), two critical workstation rings (admin + clinical), lab benches, the BMS controller/alarm panel, and the UPS maintenance bypass loop.

The board is located in the ground-floor server/UPS room — physically co-located with both the UPS cabinet and the server rack it primarily feeds. This minimises UPS-output cabling length (≤8m to U01, 2m to U06 bypass), keeps the maintenance footprint compact, and provides a single secure room for the entire critical-power ecosystem.

The board role is `ups_backed_critical_panel` and `supply_class` is `ups_plus_essential` — a dual-classification flag that signals to downstream consumers (SLD, riser, fault-level, generator-sizing) that this distribution is BOTH UPS-backed AND essential for business continuity. In larger facilities the UPS input itself would be generator-backed, so the chain becomes utility → ATS → generator-backed essential bus → UPS → DB-UPS.

## Board Identification

DB-UPS follows the same single-board identification pattern as the rest of the IEC sub-DB family (DB-EM, DB-FA1, DB-COMMS, DB-L1, DB-P1, DB-M1): IP4X enclosure rating (indoor equipment room), single-board scope, and a role flag distinct from the others. The `ups_backed_critical_panel` role is distinct because:

- DB-UPS is on the UPS-output side — every circuit downstream of this board enjoys 30-min ride-through during a utility outage
- The cascade-coordination story is fundamentally different from a utility-fed panel: the inverter limits fault contribution to ~6.5 kA per IEC 62040-1:2017 Annex E
- Labelling discipline is stricter — every faceplate, the panel cover, and the upstream submain must clearly identify the UPS-output boundary so a maintainer never accidentally cross-bonds UPS output to utility AC during fault investigation
- The downstream skills consuming this intent must treat DB-UPS as a UPS-output distribution AND as an essential-bus distribution simultaneously

The role flag drives a distinct symbol set in the SLD consumer (UPS_BLOCK symbol appears upstream of DB-UPS to show the UPS in the cascade chain) and a distinct treatment in the generator-sizing consumer (UPS-backed loads must NOT be sized into the generator startup transient — they're invisible to the generator because the UPS rides through).

## Incoming Supply — IEC 62040-1:2017 governs the UPS topology

This is the defining design constraint for DB-UPS. The 10 kVA online double-conversion UPS topology shapes everything about how this board behaves:

1. **Online double-conversion topology.** The load is ALWAYS fed from the inverter. Rectifier (utility AC → DC bus) + battery bank + inverter (DC bus → clean output AC). There is no transfer time on utility loss because the load was never on utility AC — it was always on inverter AC. This is the gold standard for critical-power topology per IEC 62040-3:2011 Class VFI-SS-111.

2. **Static bypass switch engages only on UPS internal fault or maintenance.** The bypass path is a fast-acting solid-state switch (typically <4 ms transfer) that routes the load directly from utility AC to the output bus, bypassing the inverter. It exists for two reasons: (a) safety net during an internal UPS fault, and (b) maintenance pathway so engineers can service the UPS without losing the critical loads. The bypass MUST allow upstream fault current to flow per IEC 62040-1:2017 §5.2.4 — this is why U06 is RCD-free.

3. **30-min ride-through autonomy.** Battery bank is sized for 30 minutes at full 10 kVA load — sufficient for orderly server-rack shutdown via the BMS controller and graceful workstation-session preservation. AHJ-required business-continuity duration may extend this (e.g., 60 min for hospital, 2h+ for data-centre Tier rating); verified at handover against the UPS commissioning certificate + battery discharge test report.

4. **UPS-output fault contribution ≈6.5 kA per IEC 62040-1:2017 Annex E.** Significantly lower than utility-side 22.5 kA at MSB-MAIN because the inverter's IGBT bridge limits short-circuit current to ~1.5-2× rated output. For a 10 kVA UPS at 14.4A rated, that's 22-29A continuous limit. Peak instantaneous fault current is contributed via the bypass static switch during the fault — the static switch closes as soon as the inverter senses an overload it cannot serve, dumping utility-side fault current through the bypass. This dual-regime fault behaviour is what makes UPS cascade coordination tricky.

### Fault level at DB-UPS

Declared PFC at MSB-MAIN ≈ 22.5 kA on the utility side. After the UPS, declared PFC at DB-UPS ≈ 6.5 kA on the UPS-output side per IEC 62040-1:2017 Annex E — comfortably within the 10 kA Icn of standard IEC 60898 MCBs. No cascade backup needed at the device level, BUT cascade selectivity across the UPS is a separate concern (see Selectivity Analysis below).

## Circuit Breakdown — 6 circuits across the critical-load ecosystem

Connected critical load:

- 1× server rack @ 6 kVA = 4.8 kW (assuming 0.8 PF) — 3-phase load
- 2× critical workstation rings (admin + clinical) @ 2 kW each = 4 kW — single-phase
- 1× lab benches @ 1.5 kW — single-phase
- 1× BMS controller @ 0.8 kW — single-phase supervisory
- 1× UPS bypass loop @ 0 kW continuous (path-only; carries load during maintenance)
- **Total connected ≈ 11.1 kW (≈ 13.9 kVA at 0.8 PF)**

UPS sized 10 kVA — at design intent the connected load slightly exceeds nameplate because not all loads run simultaneously at peak (server rack peaks at boot/scrub; workstations peak during occupied hours; lab benches peak intermittently). Engineer to verify peak coincident-demand profile against 10 kVA UPS capacity at design hand-off; if peak exceeds 8 kVA sustained, upsize to 15 kVA.

### Circuit-by-circuit reasoning

**U01 — Server rack 6 kVA (UPS output).** 32A Type C MCB, 6mm² 5-core Cu LSZH. The server rack contains 6-12 dual-PSU servers + 2 storage controllers + 2 PDU strips + cooling fans. Steady-state ~9A per phase; boot-time cluster inrush (all PSUs energising simultaneously after a maintenance restart) can hit 3-5× steady-state for ~200 ms. 32A Type C handles cluster inrush comfortably. 6mm² 5-core (L1+L2+L3+N+E) gives sub-0.5% voltage drop across the 8m UPS-output → DB-UPS → rack run — keeps PSU input voltage rock-solid during boost transients. Type B RCD (30 mA) per §531.3.3 — server-rack PSUs are textbook smooth-DC-leakage sources.

**U02 — Critical workstations ring (admin).** 16A Type C MCB, 2.5mm² 3-core Cu LSZH. Admin workstation ring serves 8-12 desks via 13A BS 1363 sockets on a ring topology. Steady-state ~6-8A; ring topology distributes load and reduces voltage drop across the 30m ring perimeter. 2.5mm² × 30m round-trip ≈ 60m equivalent on a ring (halved by parallel paths) — voltage drop ~1.2% at full load. Type A RCD (30 mA) per §411.3.3 — sufficient for single-phase Class 1 workstation PSUs producing pulsating-DC leakage.

**U03 — Critical workstations ring (clinical).** 16A Type C MCB, 2.5mm² 3-core Cu LSZH. Same spec as U02 but 35m route to the clinical wing. Workstations here run patient-record/PACS terminals; "critical" status earns the UPS backing so a utility outage during a clinical session doesn't lose unsaved patient data. Type A RCD identical to U02.

**U04 — Lab benches power (essential).** 10A Type C MCB, 2.5mm² 3-core Cu LSZH. Lab benches feed laboratory-grade instruments (centrifuges, microscopes, microplate readers, small heaters). Lower density than workstation rings — typically 3-4 benches with 13A sockets each. 10A handles steady-state ~4-5A with headroom for instrument inrush (centrifuge motor start). 25m route. Type A RCD (30 mA) per §411.3.3.

**U05 — BMS controller + alarm panel.** 6A Type C MCB, 1.5mm² 3-core Cu LSZH. BMS panel contains the central building-management controller + life-safety alarm interface. The 230V AC supply feeds the controller PSU; the controller itself has internal earth-leakage monitoring on its 24V DC field side. **U05 is NOT RCD-protected at DB-UPS** — the BMS is a dedicated supervisory circuit with no general-purpose sockets downstream; personal-shock protection is provided by the BMS panel's internal earth-leakage relay on the DC field side. 15m route. 6A Type C handles the small SMPS + relay-coil energisation.

**U06 — UPS bypass (maintenance loop).** 32A Type C MCB, 6mm² 5-core Cu LSZH. **U06 is the ONLY RCD-free circuit at DB-UPS by deliberate design exemption per IEC 62040-1:2017 §5.2.4.** The bypass path must allow earth-fault current to flow upstream to MSB-MAIN F07 for proper isolation. An RCD on the bypass would create a parallel earth path that could cause spurious disconnection during a downstream UPS-load earth fault — defeating the bypass-availability purpose at the exact moment maintenance redundancy is needed. 32A / 6mm² mirrors U01 so the bypass can carry full UPS-output load during maintenance changeover. Very short 2m run within the server/UPS room.

## Cable selection — LSZH Cu throughout

All DB-UPS circuits use LSZH (low-smoke zero-halogen) Cu insulated cable per IEC 60332-1 + IEC 60754-1/2. LSZH is required in the server/UPS room because:

- Low toxic emission during fire — critical in an enclosed server/UPS room where any fire would also threaten the most valuable IT assets
- Halogen-free reduces post-fire corrosion of server-rack PCBs (chloride/bromide from PVC cable fires destroys exposed PCB contacts at the exact moment the operator wants to assess salvage)
- Best practice for critical-power distribution per IEEE 446-1995

Note: DB-UPS does NOT require fire-rated (FP200/CWZ) cable like DB-EM or DB-FA1. The UPS-backed loads do not have a life-safety availability requirement during a fire — IT/server availability is not life-safety. The fire-resilience requirement only applies to dedicated escape-route lighting + fire-alarm + voice-alarm systems on dedicated boards.

The upstream submain (40m from MSB-MAIN F07 to UPS input) is 16mm² 5-core Cu XLPE — sized for 50A continuous + 22.5 kA fault carrying capacity. Standard utility-side construction.

## RCD strategy — three-tier approach

This is the design's most jurisdiction-specific decision and the reason the example exists alongside the simpler DB-EM (no RCD anywhere) and DB-COMMS (Type B everywhere) examples. DB-UPS uses **three different RCD postures across 6 circuits**:

### Tier 1 — Type B 30 mA on U01 (server rack only)

Per IEC 60364-5-53:2002+A2:2015 §531.3.3. The server rack is the only DB-UPS circuit that feeds a load classified as "IT equipment with DC leakage components" — multiple dual-PSU servers with SMPS rectifier front-ends + storage controllers + PDU strips all produce smooth DC residual currents capable of blinding Type A or Type F RCDs per IEC 62423:2009. Type B is the only DC-sensitive RCD class.

### Tier 2 — Type A 30 mA on U02, U03, U04 (general socket circuits ≤32A)

Per IEC 60364-4-41 §411.3.3. Workstation rings + lab benches feed general-purpose 13A sockets serving single-phase Class 1 equipment. The PSUs in workstation/lab equipment produce pulsating-DC leakage (half-wave-rectified) rather than smooth-DC, so Type A is sufficient — Type A is pulsating-DC sensitive but not smooth-DC sensitive. The 30 mA sensitivity provides additional protection against indirect contact + supplementary protection against direct contact per §411.3.3 for sockets ≤32A intended for general use.

Type B was considered for the workstation rings on the grounds that some modern workstation PSUs (especially data-centre-grade Platinum-rated SMPS) can produce a small smooth-DC component. The decision to stay with Type A is based on:

- §531.3.3 requires Type B only where loads are "stationary equipment that may produce smooth DC residual current" — general office workstations are mobile/replaceable and treated as standard single-phase Class 1 equipment
- Cost differential is meaningful (Type B RCBO ~5-6× Type A RCBO)
- Per-circuit smooth-DC leakage from a single workstation PSU is typically <0.5 mA, well below the 6 mA Type A blinding threshold

If the building's workstation fleet shifts toward data-centre-grade PSUs at the next refresh, this decision should be revisited.

### Tier 3 — NO RCD on U05 (BMS) and U06 (bypass)

- **U05 BMS:** Dedicated supervisory control circuit with no general-purpose sockets downstream. The BMS panel itself contains internal earth-leakage monitoring on its 24V DC field side. The 230V AC supply to the controller cabinet is treated as a dedicated supervisory circuit not subject to socket-circuit personal-shock provisions.
- **U06 UPS bypass:** IEC 62040-1:2017 §5.2.4 design exemption — bypass paths must allow upstream fault current flow for proper isolation. RCD on the bypass would create a parallel earth path and defeat the bypass-availability purpose.

## MCB curve — all Type C

Type C (Ia = 10×In) across all 6 circuits. Type C is the standard critical-power-distribution choice:

- Handles SMPS cluster inrush of the server rack at boot (dual-PSU servers energising simultaneously)
- Handles workstation cold-start inrush (PC PSU energisation at 6-8× steady-state for ~50 ms)
- Handles lab-instrument motor-start inrush (centrifuge, microplate-reader stepper)
- Handles bypass changeover transient (load step during UPS-to-utility transfer)
- Tighter than Type D so still gives reasonable earth-fault loop disconnection time per IEC 60364-4-41 §411.3.2
- 10 kA Icn (IEC 60898) covers the 6.5 kA UPS-output PFC at DB-UPS

Type B was rejected because the server-rack PSU cluster at U01 produces simultaneous SMPS inrush sitting on the Type B Ia threshold (3-5×In) — high risk of nuisance trip during scheduled-maintenance restart cycles.

## Selectivity verification — cascade-critical at U01/U06

Upstream MSB-MAIN F07 = 50A Type C MCB (utility-side). UPS sits in series between MSB-MAIN F07 and DB-UPS. Downstream MCBs at DB-UPS are 6-32A Type C:

- **Worst case at U01/U06 (32A):** 50/32 = 1.56:1 — **BELOW the 2:1 IEC 60898 same-curve cascade threshold**. Cascade-critical case. Under a downstream U01 server-rack fault on the UPS-output side, the UPS internal protection and the upstream MSB-MAIN F07 may trip simultaneously rather than selectively. The fault-clearing path becomes: (a) UPS inverter senses overload and transfers to bypass within ~4 ms, (b) bypass static switch dumps utility-side fault current (22.5 kA) through the bypass to the U01 fault, (c) U01 32A MCB clears the fault locally — BUT if MSB-MAIN F07 sees the fault current first (cascade race condition), F07 trips and takes the entire UPS offline, transferring all DB-UPS load to bypass and then to dark.
- **U02-U03 (16A):** 50/16 = 3.13:1 — above minimum threshold; manufacturer cascade table typically confirms full selectivity to 6.5 kA UPS-output PFC.
- **U04 (10A):** 50/10 = 5:1 — comfortable margin; full selectivity expected.
- **U05 (6A):** 50/6 = 8.3:1 — comfortable margin.

The U01/U06 ratio is the cascade-critical case and the reason for the second INFO flag. Same-curve Type C → Type C cascade at 1.56:1 is BELOW the documented minimum per most manufacturer tables — Schneider, ABB, Siemens, Hager all publish 2:1 as the same-curve minimum. The mitigation is one of:

1. **Manufacturer-specific coordination chart at 6.5 kA UPS-output PFC** — some manufacturers publish lower thresholds for short fault durations under inverter-limited fault sourcing. Engineer to verify against the UPS manufacturer's coordination chart at the specific 10 kVA UPS model installed.
2. **Upsize MSB-MAIN F07 to 63A** — restores 63:32 = 1.97:1 ratio (still below 2:1 but at the boundary). Better solution would be 80A → 80:32 = 2.5:1, but that requires resizing the entire utility-side feeder + the UPS input protection.
3. **Move U01 to a different curve (Type D at 32A)** — gives time-current discrimination via different magnetic-trip threshold; cascade ratio becomes effectively infinite at the magnetic-trip differential.

The example flags this as INFO (not non-compliance) and defers the resolution to the fault-level skill. The fault-level skill must:

- Verify the 6.5 kA UPS-output PFC against the manufacturer's actual short-circuit contribution chart (Annex E values are typical, not universal)
- Confirm UPS ride-through and bypass-changeover sequence under U01 fault
- Confirm cascade behaviour at both 6.5 kA (UPS-fed) and 22.5 kA (bypass-fed) fault levels

## Compliance Assessment

DB-UPS is compliant against the relevant standards stack:

- **IEC 60364 series (general LV distribution)** — basic compliance baseline
- **IEC 62040-1:2017** — UPS general requirements, §5.2.4 bypass design, Annex E fault contribution
- **IEC 60364-5-53:2002+A2:2015 §531.3.3** — Type B RCD on U01 server rack
- **IEC 60364-4-41 §411.3.3** — Type A 30 mA RCD on U02-U04 socket circuits ≤32A
- **IEEE 446-1995 (Emerald Book)** — critical-power distribution practice, labelling, siting
- **IEC 60898-1 + IEC 60364-5-53:2002 §536** — cascade selectivity verification (flagged INFO)

Two INFO flags carried:

1. **Battery autonomy verification at handover** — 30-min design intent must be confirmed against UPS commissioning certificate + battery discharge test report. AHJ-required business-continuity duration may extend per local code.

2. **Cascade ratio at U01/U06 sits below 2:1 minimum** — fault-level skill to confirm at full coordination study at 6.5 kA UPS-output PFC + 22.5 kA bypass-fed PFC + UPS ride-through behaviour.

Neither flag is a non-compliance — both are design-decision flags requiring confirmation at downstream skill invocations.

## Schedule Notes

6 circuits + 4 spare ways (W7-W10). Typical future expansion includes:

- Additional server-rack zones (compute rack, storage rack)
- Secondary BMS interface (zone-level BMS or addressable energy-monitoring sub-feed)
- Video-wall / AV-control rack (presentation system in adjacent meeting room)
- Addressable PDU / environmental-monitoring sub-feed (rack-level temp/humidity/smoke per BS EN 50600-2-3)

Placard on DB-UPS faceplate: **"UPS-OUTPUT — DO NOT BACK-FEED"** per IEEE 446-1995 critical-power labelling practice. This prevents a maintainer from accidentally cross-bonding UPS output to utility AC during fault investigation — a common cause of severe UPS damage and ride-through loss in installations without clear labelling discipline.

## Downstream consumer

This board's intent-out.json is consumed by:

- `electrical/sld/examples/intl-commercial-msb-4subdbs/` (SLD multi-board cascade — DB-UPS will appear as feeder F07 of MSB-MAIN in the Phase B multi-sheet INT rebuild, with the UPS_BLOCK symbol drawn upstream)
- (Future) `electrical/cable-sizing/` — verify 6mm² 5-core and 2.5mm² 3-core cables against IEC 60364-5-52 ampacity + voltage-drop on the UPS-output side
- (Future) `electrical/fault-level/` — **cascade-critical study at U01/U06 (50:32 = 1.56:1)** + UPS-output PFC verification at 6.5 kA + bypass-fed PFC at 22.5 kA + UPS ride-through/changeover sequence under fault
- (Future) `electrical/earthing/` — UPS-output earth bonding to building TN-S; equipotential bonding of server-rack frames per BS EN 50310:2016
- (Future) `electrical/generator-sizing/` — note that UPS-backed loads are INVISIBLE to the generator during the changeover transient (the UPS rides through); generator must be sized for the UPS input rectifier (rectifier-fed loads have a different inrush profile than direct loads)
- (Future) `electrical/riser/` — UPS-output bus segregation from utility AC on shared trays; labelling discipline at every cable break

## See also

- `electrical/db-layout/examples/intl-commercial-tpn-msb/` (upstream — MSB-MAIN F07 feeder, ups_plus_essential voltage class flagged)
- `electrical/db-layout/examples/intl-dbcomms-data/` (peer — LV data/comms sub-DB, Type B RCD throughout for IT loads, UPS bypass exemption pattern matches DB-UPS U06)
- `electrical/db-layout/examples/intl-dbem-emergency-lighting/` (peer — emergency lighting central battery sub-DB, life-safety NO-RCD philosophy, contrast with DB-UPS three-tier RCD strategy)
- `electrical/db-layout/examples/intl-dbfa1-fire-alarm/` (peer — fire-alarm sub-DB, same §560 NO-RCD philosophy as DB-EM)
- `electrical/db-layout/examples/intl-dbl1-lighting/` (peer — general lighting sub-DB)
- `electrical/db-layout/examples/intl-dbp1-power/` (peer — small power sub-DB, Type A RCD pattern matches DB-UPS U02-U04)
- `electrical/db-layout/examples/intl-dbm1-mechanical/` (peer — mechanical/HVAC sub-DB)
