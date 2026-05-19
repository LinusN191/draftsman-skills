# Reasoning — INT DB-COMMS (LV Data/Comms Distribution Sub-DB)

## Site context

LV data/comms distribution sub-DB for the generic IEC commercial 3-storey office building. DB-COMMS is a dedicated IT-infrastructure distribution downstream of MSB-MAIN F06 — only the structured-cabling ecosystem (main 24-port rack + 3 floor IDFs + PoE+ injectors + UPS bypass) sits behind it. The board is located in the ground-floor main comms room (MDF) for three practical reasons:

1. Co-location with the main 24-port managed-switch rack — keeps the 230V supply to the rack short and minimises voltage-drop loss on the highest-current circuit (C01, 16A)
2. Adjacent to MSB-MAIN — 50m feeder run keeps cable cost and submain impedance within standard distribution-board fault-level bounds
3. Central to the structured-cabling backbone — the MDF is the topology root of BS EN 50173-1:2018 generic cabling subsystem, so DB-COMMS sits adjacent to the equipment it powers

Fed from MSB-MAIN F06 (32A MCB Type C) via a 50m feeder. The board role is `comms_data_panel` — flagged in the `board.role` block so downstream SLD, riser, and cable-containment skills recognise it as an IT distribution and apply BS EN 50174-2:2018 segregation rules (typically ≥150 mm separation from unshielded LV power cables on shared trays).

## Board Identification

DB-COMMS follows the same single-board identification pattern as the rest of the IEC sub-DB family (DB-EM, DB-FA1, DB-L1, DB-P1, DB-M1): IP4X enclosure rating (indoor equipment room), single-board scope, and a role flag distinct from the others. The `comms_data_panel` role is distinct because:

- DB-COMMS is not life-safety in the IEC 60364-5-56:2018 §560 sense (no NO-RCD exemption, no fire-rated cable requirement, no central-battery requirement)
- BUT DB-COMMS is functionally essential — outage disrupts the entire office IT path (Wi-Fi, IP phones, security cameras, access control). Classified `supply_class: essential` for resilience planning purposes (e.g., generator-backed in larger facilities)
- The downstream skills consuming this intent must apply EMC/segregation rules per BS EN 50174-2:2018, not life-safety rules per §560

The role flag also drives a distinct symbol set in the SLD consumer (COMMS_RACK symbol appears on the DB-COMMS face, not on DB-EM or DB-FA1).

## Incoming Supply — IEC 60364-5-53:2002+A2:2015 §531.3.3 governs RCD selection

This is the defining design constraint for DB-COMMS. Unlike the life-safety boards (DB-EM, DB-FA1) which have NO upstream RCD per §560.7, DB-COMMS specifically REQUIRES a Type B (DC-sensitive) RCD upstream. Why:

1. **IT loads produce DC leakage.** PoE+ injectors, SMPS-fed managed switches, and UPS rectifier front-ends all rectify their AC inputs internally. Imperfect rectification + accumulated common-mode capacitance leakage means smooth (non-pulsating) DC residual currents flow back into the protective conductor. Per IEC 62423:2009, Type A and Type F RCDs are explicitly blinded by smooth DC ≥ 6 mA — they fail to disconnect under earth fault if a DC component biases the residual-current sensor toward saturation.

2. **§531.3.3 mandates Type B for such loads.** IEC 60364-5-53:2002+A2:2015 §531.3.3 introduces the explicit selection rule: where smooth DC residual currents can occur and equipment standards do not exclude such currents, Type B RCD must be used. The 2015 amendment broadened the rule to cover IT/comms equipment with PoE injectors and SMPS — a direct response to the EMC/leakage profile of modern data infrastructure.

3. **BS EN 50173 EMC accumulation.** A single PoE switch can leak 3-9 mA of DC + pulsating-DC residual current. The DB-COMMS ecosystem (24-port main rack + 3 IDF cabinets + 2 PoE+ injectors + UPS bypass) easily sums to >30 mA across the board. Type B (30 mA sensitivity) on every final circuit detects per-circuit faults; the upstream Type B (300 mA at MSB-MAIN F06) provides cumulative protection without nuisance trip from summed normal leakage.

### Fault level at DB-COMMS

Declared PFC at MSB-MAIN ≈ 22.5 kA. After the 50m 10mm² Cu XLPE submain, PFC at DB-COMMS ≈ 8.0 kA — comfortably within the 10 kA Icn of standard IEC 60898 MCBs. No cascade backup needed at this distribution point.

## Circuit Breakdown — 7 circuits across the IT ecosystem

Connected IT load:

- 1× main comms rack @ 2.5 kW (24-port managed switch + PoE budget + dual PSU)
- 3× floor IDF cabinets @ 1.5 kW each = 4.5 kW (12-port edge switch + 24× wall plates per cabinet)
- 2× PoE+ injectors @ 0.8 kW each = 1.6 kW (Wi-Fi mesh APs + security cameras)
- 1× UPS bypass loop @ 1.0 kW
- **Total connected ≈ 9.6 kW**

Design current ≈ 9,600 / (√3 × 400 × 0.85) ≈ 16.3A. The 32A intake provides ~2× headroom — covers simultaneous boot-time inrush of all switches + PoE+ injector cold-start + UPS bypass changeover transient.

### Circuit-by-circuit reasoning

**C01 — Main comms rack 24-port + PoE switch.** 16A Type C MCB, 4mm² Cu LSZH. The 24-port managed switch (e.g. Cisco Catalyst, Aruba CX) with full PoE+ budget can boot-inrush at 4-6× steady-state for ~100 ms. Steady-state ~10A; 16A Type C handles inrush comfortably. 4mm² cable chosen for sub-1% voltage drop across the short 5m run from DB-COMMS to MDF rack — keeps PSU input voltage well within tolerance during boost transients.

**C02 / C03 / C04 — Floor IDF cabinets (GF / L1 / L2).** 10A Type C MCB each, 2.5mm² Cu LSZH. Each IDF contains a 12-port edge switch + 24× RJ45 wall-plate runs to user workstations. Cable lengths step up by floor: 30m, 40m, 50m. 2.5mm² Cu LSZH chosen for both ampacity (~16A in tray) and sub-1.5% voltage drop at the worst-case 50m L2 run.

**C05 — PoE+ AP injector (Wi-Fi mesh).** 6A Type C MCB, 1.5mm² Cu LSZH. Per IEEE 802.3bt-2018 Type 3, PoE+ delivers 30W per port at 50-57V DC over Cat 6A. A 12-port AP injector with full Type 3 budget = ~360W AC-side + rectifier inefficiency (~15%) ≈ 420W ≈ 1.8A steady-state. 6A Type C handles cold-start inrush of all 12 ports energising simultaneously. 15m cable run to the injector location near the central Wi-Fi AP cluster.

**C06 — PoE+ camera injector (security).** 6A Type C MCB, 1.5mm² Cu LSZH. Same Type 3 spec — feeds IP cameras and access-control readers. 20m cable run to the security-equipment rack adjacent to the building reception.

**C07 — UPS bypass loop feed (10 kVA).** 10A Type C MCB, 2.5mm² Cu LSZH. **This is the only RCD-free circuit at DB-COMMS** — the design exemption is deliberate per IEC 62040-1:2017 §5.2.4. The UPS bypass path must allow earth-fault current to flow upstream to MSB-MAIN protective devices for proper isolation. An RCD on the bypass would create a parallel earth path that could cause spurious disconnection during a downstream UPS-load earth fault, defeating the bypass-availability purpose. 10A Type C / 2.5mm² Cu matches the rated 10 kVA UPS bypass current. 3m short run to the UPS cabinet inside the comms room.

## Cable selection — LSZH Cu throughout

All DB-COMMS circuits use LSZH (low-smoke zero-halogen) Cu insulated cable per IEC 60332-1 + IEC 60754-1/2. LSZH is required in occupied office spaces because:

- Low toxic emission during fire — important in office tenant spaces where occupants may evacuate past the cable route
- Halogen-free reduces post-fire corrosion of comms equipment (chloride/bromide from PVC cable fires destroys exposed PCB contacts)
- Modern best practice for IT-distribution cabling — most BS EN 50173 cabling specifications mandate LSZH outer sheath as a baseline

Note: DB-COMMS does NOT require fire-rated (FP200/CWZ) cable like DB-EM and DB-FA1. The IT system does not have a life-safety availability requirement during a fire — occupant evacuation does not depend on the network remaining online. The fire-resilience requirement only applies to dedicated escape-route lighting + fire-alarm + voice-alarm systems.

The upstream submain (50m from MSB-MAIN F06 to DB-COMMS) is 10mm² 5-core Cu XLPE — standard non-essential submain construction. EMC/segregation per BS EN 50174-2:2018 is handled at the containment level (riser skill output), not at the cable level.

## RCD strategy — Type B on every circuit except C07

This is the design's most jurisdiction-specific decision and the reason the example exists. **6 of 7 circuits use 30 mA Type B RCD**:

- **Type B selection driver:** §531.3.3 of IEC 60364-5-53:2002+A2:2015. All comms loads have SMPS/PoE/UPS rectifier front-ends that produce smooth DC residual currents capable of blinding Type A or Type F RCDs. Type B is the only DC-sensitive RCD class per IEC 62423:2009.
- **30 mA sensitivity:** Standard IEC 60364-4-41 §411.3.3 final-circuit personal-shock protection. Coordinated with upstream 300 mA Type B at MSB-MAIN F06 for cumulative leakage discrimination.
- **C07 UPS bypass exemption:** IEC 62040-1:2017 §5.2.4 — bypass paths must allow upstream fault current flow for proper isolation. Engineer must verify at commissioning that the UPS cabinet itself provides equivalent personal-shock protection on its output side (typically via internal earth-leakage relay on the inverter section).

Cost analysis worth noting: Type B RCDs are ~3-4× the cost of Type A, and Type B RCBOs ~5-6× the cost of an MCB-only unit. The design accepts this cost premium because:

1. Functional necessity — Type A would silently fail under IT-load DC leakage
2. Standards compliance — §531.3.3 makes Type B mandatory, not optional
3. Future-proofing — even if today's switches happened to use AC-leakage-only PSUs, the next refresh cycle will introduce PoE++/Type 4 (90W per port) which guarantees DC leakage. Designing in Type B now avoids a costly retrofit.

## MCB curve — all Type C

Type C (Ia = 10×In) across all 7 circuits. Type C is the standard IT-distribution choice:

- Handles SMPS inrush of managed switches + edge switches (typical 4-6× steady-state for 100 ms)
- Handles PoE+ injector cold-start (all ports energising simultaneously at boot time)
- Handles UPS rectifier energisation transient + bypass changeover step
- Tighter than Type D so still gives reasonable earth-fault loop disconnection time per IEC 60364-4-41 §411.3.2
- 10 kA Icn (IEC 60898) covers the 8.0 kA PFC at DB-COMMS

Type B was considered but rejected because the multi-PSU dual-power-supply main rack at C01 produces simultaneous SMPS inrush that sits on the Type B Ia threshold (3-5×In) and risks nuisance trip during scheduled overnight reboots.

## Selectivity verification

Upstream MSB-MAIN F06 = 32A Type C MCB. Downstream MCBs at DB-COMMS are 6-16A Type C:

- **Worst case at C01 (16A main rack):** 32/16 = 2:1 — sits at the IEC 60898 minimum same-curve cascade threshold. Manufacturer cascade table must explicitly confirm selectivity at 8 kA fault level.
- **C02-C04, C07 (10A):** 32/10 = 3.2:1 — above minimum threshold; manufacturer cascade table typically confirms full selectivity to 8 kA.
- **C05-C06 (6A):** 32/6 = 5.3:1 — comfortable margin; full selectivity to 8 kA expected.

The C01 ratio is the cascade-critical case and the reason for the second INFO flag. Same-curve Type C → Type C cascade at 2:1 is the documented minimum per most manufacturer tables (Schneider, ABB, Siemens, Hager all publish similar thresholds). At 8 kA fault level it typically holds but requires explicit manufacturer-table confirmation — engineer-declared in the IR with a `tool_call_pending` flag for the fault-level skill to resolve at coordination-study time.

If the building grows and C01 ever needs to scale to 20A or 25A, the cascade ratio collapses below 2:1 and either:
- MSB-MAIN F06 must be upsized to 40A, OR
- C01 must move to a different curve (Type D at 16A would give time-current discrimination via different magnetic-trip threshold)

This sizing margin is flagged in the rationale.

## Compliance Assessment

DB-COMMS is compliant against the relevant standards stack:

- **IEC 60364 series (general LV distribution)** — basic compliance baseline
- **IEC 60364-5-53:2002+A2:2015 §531.3.3** — Type B RCD selection rule satisfied
- **BS EN 50173-1:2018 + BS EN 50173-2:2018** — structured cabling subsystem topology + EMC compliance via segregated containment (handled by riser/cable-containment skills downstream)
- **IEEE 802.3bt-2018** — PoE+ Type 3 power budget compliance for injectors
- **IEC 62040-1:2017 §5.2.4** — UPS bypass design (C07 RCD exemption)
- **IEC 60898-1 + IEC 60364-5-53:2002 §536** — cascade selectivity verification

Two INFO flags carried:

1. **Type B RCD sensitivity coordination** — engineer to verify at commissioning that the cumulative DC leakage across the comms ecosystem stays below 300 mA at the upstream RCD threshold. If routine leakage approaches 300 mA, consider segregating PoE+ injectors onto a separate downstream Type B RCD at higher sensitivity tier.

2. **Cascade ratio at C01 sits at minimum threshold** — manufacturer cascade table confirmation required at full 8 kA fault level. Defer to fault-level skill for full coordination study at engineering hand-off.

Neither flag is a non-compliance — both are design-decision flags requiring confirmation at downstream skill invocations.

## Schedule Notes

7 circuits + 3 spare ways (W8-W10). Typical future expansion includes:

- Additional floor IDF cabinets (if building adds a basement comms zone or external annex)
- AV equipment rack (boardroom AV switching + projection + display wall)
- KVM / server-room sub-feed (if the office adds an on-prem compute rack)
- Addressable rack-environmental monitoring (temperature, humidity, smoke per BS EN 50600-2-3)

## Downstream consumer

This board's intent-out.json is consumed by:

- `electrical/sld/examples/intl-commercial-msb-4subdbs/` (SLD multi-board cascade — DB-COMMS will appear as feeder F06 of MSB-MAIN in the Phase B multi-sheet INT rebuild)
- (Future) `electrical/cable-sizing/` — verify 4mm² and 2.5mm² cables against IEC 60364-5-52 ampacity + voltage-drop
- (Future) `electrical/fault-level/` — Zs verification at the furthest L2 IDF cabinet (50m run on C04) + cascade-ratio confirmation at C01 (2:1 minimum threshold case)
- (Future) `electrical/earthing/` — equipotential bonding of comms-rack frames + structured-cabling earth bus per BS EN 50310:2016
- (Future) `electrical/riser/` — IT-cabling segregation from LV power cables per BS EN 50174-2:2018
- (Future) `electrical/cable-containment/` — dedicated comms-tray sized for Cat 6A backbone + AC-side power feeders, with segregation distance enforced

## See also

- `electrical/db-layout/examples/intl-commercial-tpn-msb/` (upstream — MSB-MAIN F06 feeder, comms_data voltage class flagged)
- `electrical/db-layout/examples/intl-dbem-emergency-lighting/` (peer — emergency lighting central battery sub-DB, life-safety NO-RCD philosophy)
- `electrical/db-layout/examples/intl-dbfa1-fire-alarm/` (peer — fire-alarm sub-DB, same §560 NO-RCD philosophy as DB-EM)
- `electrical/db-layout/examples/intl-dbl1-lighting/` (peer — general lighting sub-DB)
- `electrical/db-layout/examples/intl-dbp1-power/` (peer — small power sub-DB, Type A RCD for general 13A sockets)
- `electrical/db-layout/examples/intl-dbm1-mechanical/` (peer — mechanical/HVAC sub-DB)
