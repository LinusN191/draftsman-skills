# Reasoning — INT DB-GENSET-XCV (Standby-Genset Changeover Sub-DB with ATS)

## Site context

Standby-genset changeover sub-DB for the generic IEC commercial 3-storey office building. DB-GENSET-XCV is the dedicated dual-source distribution downstream of an automatic transfer switch (ATS) that selects between utility (MSB-MAIN F08, 63A MCCB Type D, 60m feeder) and an 80 kVA standby diesel genset in utility-priority mode. The ATS section sits in the ground-floor plant room (IP4X indoor) and the contactor enclosure section is co-located with the genset in an external IP54 weather-rated enclosure, with sealed wall penetration between them per IEC 60364-5-52 §522.8.3.

The board feeds 5 final circuits: G01 ATS controller (24 VDC supervisory), G02 EM lighting changeover feed to DB-EM (32A 3-phase), G03 fire alarm changeover feed to DB-FA1 (20A 3-phase), G04 UPS bypass mains backup to DB-UPS (32A 3-phase), and G05 genset day tank + cooling fan (10A mechanical-services). The 4 downstream emergency feeds (G02-G04) re-energise their respective central-battery / battery-backed sub-DBs once the genset is online, bridging the 6-10 s transfer-time gap through their own battery autonomy.

The board role is `ats_changeover_panel` and `supply_class` is `essential` — flags that signal dual-source resilience to downstream consumers (SLD, riser, fault-level, generator-sizing, earthing). This is the most operationally critical sub-DB in the IEC family because (a) it's the gateway between utility and standby genset, (b) it carries all four life-safety + critical-power emergency feeds in one panel, and (c) its design directly governs the building's behaviour during a utility outage.

## Board Identification

DB-GENSET-XCV is structurally different from the rest of the IEC sub-DB family (DB-EM, DB-FA1, DB-COMMS, DB-UPS, DB-L1, DB-P1, DB-M1) in three important ways:

1. **Split-location enclosure.** ATS controller + utility-source breaker in indoor plant room; genset-source contactor + transfer cabling in external genset enclosure. This is a deliberate siting choice — keeps the high-current genset-source contactor close to the genset to minimise tie-cable run length (and therefore tie-cable size + voltage-drop), while keeping the operator-accessible ATS controller + status panel indoors for maintenance access.

2. **Dual-source feed.** Every other sub-DB has a single upstream source (utility-fed). DB-GENSET-XCV has TWO upstream sources (utility + genset) selected by the ATS — a fundamentally different distribution topology that must be reflected in the SLD (dual incoming feeders drawn into the ATS_BLOCK symbol), in the riser (genset-side cable run distinct from utility-side), in the fault-level skill (dual-mode PFC), and in the generator-sizing skill (the entire board is the genset's connected load).

3. **Distinct role flag.** `ats_changeover_panel` is a one-of-a-kind role flag in the IEC family — no other sub-DB carries it. Downstream consumers (especially SLD) recognise this flag and draw the ATS_BLOCK + GENSET_BLOCK symbols upstream of the board on the SLD; without the flag, they would default to the standard single-source MAIN_SWITCH presentation.

The board placard reads: **"DUAL-SOURCE — UTILITY/GENSET ATS — DO NOT BACK-FEED"** per IEEE 446-1995 critical-power labelling practice + IEC 60364-5-56:2018 §552 dual-source warning requirement. This prevents a maintainer from accidentally back-feeding the utility from the genset (or vice versa) during maintenance — a catastrophic mistake that can damage the genset alternator, trip the upstream utility breakers, and back-feed energised conductors onto an "isolated" utility section during a utility-side fault investigation.

## Incoming Supply — IEC 60364-5-56:2018 §552 governs the ATS

This is the defining design constraint for DB-GENSET-XCV. The ATS and its control logic shape everything about how this board behaves.

### Utility-priority logic

Per IEC 60364-5-56:2018 §552:

1. **Default state: ATS rests on utility-source.** Utility contactor closed; genset contactor open; genset stopped. All 5 circuits energised from MSB-MAIN F08.

2. **Utility-loss detection.** ATS controller monitors utility voltage (3-phase + neutral) for undervoltage (<85% nominal), phase-loss, frequency deviation (>±5%), or reverse-rotation. Trigger detection time typically 1-2 s to avoid nuisance transfers on brief voltage sags.

3. **Genset start signal.** ATS sends start signal to genset controller via a dedicated dry-contact relay on G01's 24 VDC supervisory loop. Genset engine cranks; warms up; alternator excites; voltage + frequency stabilise.

4. **Genset stability gate.** ATS waits for genset stable signal (≥95% nominal voltage AND ≥98% nominal frequency for ≥3 s) before initiating transfer. Prevents transferring to an unstable genset that could collapse under load.

5. **Transfer sequence.** Utility contactor opens → ATS dwells (typical 0.5-1 s break-before-make) → genset contactor closes → load transfers to genset. All 4 poles (L1+L2+L3+N) switch together.

6. **Utility return.** When utility voltage + frequency return to nominal AND remain stable for ≥30 s (longer hysteresis than the loss-detection gate, to confirm utility is genuinely back rather than briefly recovered), reverse transfer initiates: open genset contactor → dwell → close utility contactor → load on utility. Genset receives stop signal but runs unloaded for 5-min cooldown per ISO 8528-12:1997 §5.5 before final stop (prevents thermal shock to the diesel engine's turbocharger and cylinder head).

### Transfer time — the critical design disclosure

**Transfer time 6-10 s typical for an 80 kVA medium-genset.** Breakdown:

- 1-2 s utility-loss detection (debounce against brief sags)
- 3-5 s engine crank-to-stable (cold-start + warm-up + alternator excitation + AVR settling)
- 0.5-1 s ATS break-before-make dwell
- 0.5-1 s genset contactor close + mechanical settling
- 0.5-1 s load-step settling on genset (block-load step from zero to full)

ISO 8528-12:1997 classifies this as **Class A1 (≤1 s) NOT achievable without a no-break or short-break system** (e.g., flywheel UPS, rotary UPS, fuel-cell ride-through). A standard reciprocating-engine standby genset operates in Class B (>15 s tolerable for some loads) or Class A2 (1-15 s with optimised warm-up). The 6-10 s design intent sits in **Class A2 with cold-start optimisation** (block heater on, AVR pre-energised, engine maintenance-cycled).

This is the most safety-critical fact about this board and the reason the example carries a **WARNING-severity** compliance flag (not info). Two cross-jurisdictional benchmarks govern the AHJ sign-off:

- **NFPA 110-2022 Type 10:** US-aligned facilities require ≤10 s transfer for life-safety branch loads. The 6-10 s design intent sits AT the boundary — passing AHJ acceptance requires commissioning test confirming consistent ≤10 s under cold-start conditions, not just warm-engine conditions.
- **BS EN 50171:2001+A1:2022 §6.3:** EU central-battery emergency-lighting standard classifies transfer times as Type Z (≤0.5 s, only achievable with central-battery EM systems or self-contained luminaires) or Type N (≤15 s, acceptable for genset transfer). The 6-10 s genset-only transfer is INSUFFICIENT for Type Z and ACCEPTABLE for Type N — DB-EM downstream of G02 must be a Type N central-battery system OR self-contained luminaires bridge the gap.

The mitigation in this design is layered:

1. **G02 EM lighting feed to DB-EM** — DB-EM is itself a central-battery EM system with 3-hour autonomy (per the peer dbem example). DB-EM rides through the 6-10 s genset transfer entirely on battery; G02 simply re-energises the EM-CB charger + central inverter once the genset is online. EM luminaires never see the transfer event.
2. **G03 fire alarm feed to DB-FA1** — DB-FA1 carries its own internal battery autonomy (4-hour minimum per BS 5839-1:2017 §25.3 typical specification). DB-FA1 rides through the transfer on internal battery; G03 re-energises the panel charger once the genset is online.
3. **G04 UPS bypass mains backup to DB-UPS** — DB-UPS sits behind a 10 kVA online double-conversion UPS with 30-min ride-through. The UPS never sees the transfer event because its load is always on inverter; G04 simply re-energises the UPS rectifier charge path once the genset is online. (Note: G04 is the BYPASS path; the primary UPS-input feed is from MSB-MAIN F07, but G04 provides a genset-backed bypass mains alternative for maintenance/redundancy scenarios.)

### Dual-mode fault contribution

**Utility-mode declared PFC: 9.0 kA at the ATS output** — derived from upstream MSB-MAIN F08 declared 22.5 kA, reduced by the 60m × 16mm² Cu XLPE feeder impedance (R+jX ≈ 0.27 Ω) per IEC 60909-0:2016 §3.5. Comfortably within the 10 kA Icn of standard IEC 60898 Type C MCBs.

**Genset-mode declared PFC: ~4.0 kA at the ATS output** — derived from genset subtransient impedance per IEC 60909-0:2016 §3.5.1 equivalent voltage source method:

```
Ik" = c × Un / (√3 × Xd")
    = c × 400 / (√3 × Xd" × Un / S_n)
    = 1.05 × 400 / (√3 × 0.12 × 400 × 400 / 80000)
    ≈ 1.05 × 80000 / (√3 × 0.12 × 400)
    ≈ 4000 A  (with Xd" ≈ 0.12 pu typical 4-pole synchronous)
```

Significantly lower than utility-mode. The fault-level skill must verify BOTH regimes against the manufacturer cascade table — neither alone is sufficient because cascade behaviour during the transfer event itself (when the ATS is briefly in dwell with no source) is a third regime that requires time-domain modelling per IEC 60909-1:2002.

## Circuit Breakdown — 5 circuits across the dual-source ecosystem

Connected load:

- 1× G01 ATS controller @ 0.5 kW (24 VDC supervisory; SMPS-fed)
- 1× G02 EM lighting feed @ 6.0 kW (central-battery EM-CB charger + inverter standby load)
- 1× G03 fire alarm feed @ 4.0 kW (fire-alarm panel + voice-alarm amps + battery charger)
- 1× G04 UPS bypass feed @ 12.0 kW (UPS rectifier rated load + bypass path losses)
- 1× G05 day tank + cooling fan @ 1.5 kW (fuel pump motor + exterior cooling fan)
- **Total connected ≈ 24 kW (≈ 30 kVA at 0.8 PF)**

Genset sized 80 kVA — significantly oversized for the 30 kVA connected. The oversize is driven by:

- **Block-load step capability.** ISO 8528-5:2018 performance class G3 requires the genset to accept a 100% block-load step (the worst-case scenario: ATS closes onto a fully energised set of downstream sub-DB chargers + UPS rectifier + EM-CB rectifier all drawing inrush simultaneously). 80 kVA gives ~2.5× headroom on the steady-state 30 kVA + room for the transient peak.
- **Cold-start motor inrush.** G05 cooling fan + day tank pump motors produce ~5-7× steady-state inrush during the ATS transfer event — adds ~5-10 kVA transient to the 80 kVA genset.
- **Future expansion margin.** 3 spare ways (W6-W8) on DB-GENSET-XCV signal capacity for future safety-services growth; the genset is also sized with this in mind.

### Circuit-by-circuit reasoning

**G01 — ATS controller + signaling (24 VDC supervisory).** 6A Type C MCB, 1.5mm² 3-core LSZH Cu. The ATS controller cabinet houses the microprocessor-based control + the SMPS that derives 24 VDC from the 230 VAC supply + the genset start/stop relays + the status-LED panel. Steady-state load ~0.3 kW + small inrush at energisation. Type C handles the SMPS inrush. **G01 is on the `ELV_control` voltage class** (not `LV_power`) because the dominant downstream loads are 24 VDC supervisory — distinguishes this circuit from the LV_power feeds for downstream skills (especially riser + cable-containment, where ELV_control is segregated per IEC 60364-5-52 §528.1). **G01 is NOT RCD-protected** — dedicated supervisory control circuit with no general-purpose sockets downstream; same exemption principle as DB-UPS U05 BMS controller.

**G02 — EM lighting changeover feed to DB-EM.** 32A Type C MCB, 6mm² 4-core LSZH Cu over 80m. The longest run on this board — 80m from DB-GENSET-XCV through the riser to DB-EM in the ground-floor plant room. 32A sized for the DB-EM intake (24 kVA central-battery EM-CB unit + small overhead). 6mm² × 80m round-trip ≈ 1.8% voltage drop at full load — within the 5% IEC 60364-5-52 limit. **G02 is NOT RCD-protected** per IEC 60364-5-56:2018 §560.7 — safety-services emergency feeds must allow upstream fault current to flow for proper isolation; an RCD would defeat the dual-source resilience purpose.

**G03 — Fire alarm changeover feed to DB-FA1.** 20A Type C MCB, 4mm² 4-core LSZH Cu over 60m. Sized for the DB-FA1 intake (fire-alarm panel + voice-alarm amps + 4-hour battery charger). 4mm² × 60m gives 1.5% voltage drop. **G03 is NOT RCD-protected** per §560.7 (same reasoning as G02). Cable type may be upgraded to fire-resistant (FP200 Gold equivalent per BS 6387 CWZ) downstream of DB-FA1 — but the DB-GENSET-XCV → DB-FA1 trunk is standard LSZH because it's the supply-side path, not the fire-alarm circuit itself.

**G04 — UPS bypass mains backup to DB-UPS.** 32A Type C MCB, 6mm² 4-core LSZH Cu over 40m. Sized for the DB-UPS bypass intake (10 kVA UPS rectifier rated load + bypass-path losses + future-capacity headroom). 6mm² × 40m gives 0.9% voltage drop. **G04 is NOT RCD-protected** per IEC 62040-1:2017 §5.2.4 — UPS bypass paths must allow upstream fault flow for proper isolation. **Note on topology:** G04 provides a genset-backed bypass mains alternative to the primary UPS-input feed (which comes from MSB-MAIN F07 directly per the peer dbups example). During a utility outage, the genset re-energises G04, which provides the UPS rectifier with a genset-sourced supply once the UPS internal switchover from battery to mains is required (i.e., after the 30-min ride-through if the utility outage extends beyond battery autonomy). This is a defence-in-depth topology — the UPS battery is the primary ride-through; the genset is the long-duration backstop.

**G05 — Genset day tank + cooling fan.** 10A Type C MCB, 2.5mm² 3-core LSZH Cu over 5m. Two small mechanical-services loads in the external genset enclosure:

- **Day tank fuel pump** — small 1-phase motor that transfers diesel from the bulk fuel tank to the genset day tank when the day-tank level switch closes. Operates intermittently (a few minutes every hour during sustained genset run).
- **Cooling fan** — small 1-phase fan motor that draws air through the radiator when the engine coolant temperature exceeds threshold. Operates only during sustained genset run, not during the brief weekly exercise cycle.

**G05 IS RCD-protected — Type A 30 mA per IEC 60364-4-41 §411.3.3.** This is the only RCD-protected circuit on the board. Three factors justify it:

1. **Exterior route.** Cabling runs into the external genset enclosure where exposure to moisture, vermin, and mechanical damage is higher than indoor cable trays.
2. **Fuel handling.** The day-tank pump moves diesel — any earth fault in the motor windings or the pump terminal box creates an ignition risk near flammable liquid; an RCD provides the fastest possible disconnection.
3. **Motor windings.** Both motors are Class 1 single-phase types with full earth bonding of the motor frame; Type A handles the pulsating-DC leakage characteristic of small Class 1 SMPS-controlled motor circuits.

Type A (not Type B) is sufficient because there is no DC-coupled load downstream — both motors are direct-on-line 1-phase Class 1, producing pulsating-DC rather than smooth-DC residual currents.

## Cable selection — LSZH Cu throughout

All DB-GENSET-XCV circuits use LSZH (low-smoke zero-halogen) Cu insulated cable per IEC 60332-1 + IEC 60754-1/2. LSZH is required because:

- The plant room is an occupied space accessed regularly by maintenance staff — low toxic emission during fire is essential
- The genset enclosure houses fuel + hot engine surfaces + electrical components; halogen-free reduces post-fire corrosion of nearby control equipment (chloride/bromide from PVC cable fires destroys exposed PCB contacts and contactor coils)
- Best practice for ATS-fed safety-services distribution per IEEE 446-1995

Note: DB-GENSET-XCV feeders themselves do NOT require fire-rated (FP200/CWZ) cable, because they are the SUPPLY paths to the downstream safety-services sub-DBs, not the life-safety circuits themselves. The fire-resilience requirement (BS 6387 CWZ / IEC 60331) only applies to the dedicated escape-route lighting + fire-alarm + voice-alarm circuits downstream of DB-EM and DB-FA1. The upstream feeds from a fully-functional ATS-backed essential bus are governed by general LV distribution rules (IEC 60364-5-52), not by the life-safety cable-fire-resilience rules.

The upstream submain (60m from MSB-MAIN F08 to ATS utility-source input) is 16mm² 4-core Cu XLPE — sized for 63A continuous + 22.5 kA fault carrying capacity. The genset-side tie cable (genset → ATS genset-source input) is 25mm² 4-core Cu XLPE — sized for the genset full-load current (80 kVA / (√3 × 400V) = 116A nominal, but 25mm² rather than 16mm² is selected to handle (a) the block-load step transient + (b) the genset's actual 95-100% rated point under steady-state running + (c) the 4-pole transfer requirement that the cable carry phase + neutral conductors of equal cross-section).

## RCD strategy — one-circuit-only RCD posture

Unlike DB-UPS (three-tier RCD strategy across 6 circuits), DB-GENSET-XCV uses a **single-tier RCD posture: only G05 is RCD-protected**. All other circuits are RCD-FREE by deliberate design exemption:

- **G01 (ATS controller):** Supervisory ELV_control circuit — IEC 60364-5-51 §514.5 exemption pattern
- **G02 (EM lighting feed):** Safety-services emergency feed — IEC 60364-5-56:2018 §560.7 NO-RCD requirement
- **G03 (fire alarm feed):** Safety-services emergency feed — §560.7 NO-RCD requirement
- **G04 (UPS bypass):** UPS bypass path — IEC 62040-1:2017 §5.2.4 fault-flow requirement
- **G05 (day tank + cooling fan):** Mechanical-services with exterior route + fuel handling — IEC 60364-4-41 §411.3.3 Type A 30 mA REQUIRED

This is the **dual-source-board equivalent** of the "no RCD on life-safety feeds" doctrine: an RCD on G02/G03/G04 would defeat the entire purpose of building dual-source resilience, because under a downstream fault the RCD would trip at 30 mA before the upstream MCCB/MCB could discriminate at the 16-32A overcurrent level — losing the emergency feed at the worst possible moment. The fault-clearance path on a dual-source life-safety feed must run end-to-end through MCB/MCCB devices that can be coordinated against the dual-mode source impedances.

G05 is the exception because (a) it is not a life-safety feed (it's a mechanical-services circuit that serves the genset's own auxiliaries, not a downstream safety-services sub-DB), and (b) the exterior route + fuel-handling + motor-windings combination demands the highest available shock-protection class. Loss of G05 during a fault is acceptable — the genset will simply run without active cooling for a few minutes (engine ECU manages thermal trip) and the day-tank will drain to the low-level cutout before requiring intervention.

## MCB curve — all Type C on ATS-output side; Type D upstream

**ATS-output (G01-G05): all Type C MCBs (Ia = 10×In).** Type C handles:

- SMPS inrush at G01 (ATS controller 24 VDC SMPS)
- EM-CB rectifier inrush at G02 (DB-EM central-battery charger energising)
- Fire-alarm-panel SMPS + voice-alarm-amp inrush at G03 (DB-FA1 panel chargers + amplifier rail caps)
- UPS rectifier inrush at G04 (DB-UPS rectifier charge path energising — significant transient as the rectifier capacitor bank charges)
- Motor inrush at G05 (day-tank pump + cooling-fan motor starts)
- Block-load step at the genset closing event (all downstream loads energising simultaneously when ATS transfers to genset)

Type B was rejected because the simultaneous downstream chargers + UPS rectifier produce SMPS cluster inrush sitting on the Type B Ia threshold (3-5×In) — high risk of nuisance trip during ATS transfer. Type D was rejected on the ATS-output side because the higher magnetic threshold (10-20×In) would not give acceptable earth-fault loop disconnection time on the downstream sub-DB feeders.

**Upstream MSB-MAIN F08: 63A MCCB Type D.** Type D selected for the 60m utility-side feeder run because:

- The 60m feeder + 32A downstream loads + ATS transfer-event transient combine to produce a brief overcurrent on the feeder during transfer (genset block-load step travels back upstream through the closed utility contactor for the ~1 ms before the ATS opens utility). Type D's higher magnetic threshold (10-20×In) tolerates this transient where Type C (5-10×In) would risk nuisance trip.
- MCCB (not MCB) selected because the feeder current (63A continuous) is at the upper edge of IEC 60898 MCB practical sizing; IEC 60947-2 MCCBs give higher continuous-rating reliability + better fault-clearing performance for medium-current feeders + adjustable trip settings if commissioning reveals a need to retune.

## Selectivity verification — MCCB-upstream-of-MCB cascade at G02/G04

Upstream MSB-MAIN F08 = 63A MCCB Type D (utility-side). ATS sits in series between MSB-MAIN F08 and DB-GENSET-XCV. Downstream MCBs at DB-GENSET-XCV are 6-32A Type C:

- **Worst case at G02/G04 (32A):** 63/32 = ~2:1 — AT the IEC 60898 same-curve cascade threshold. BUT benefits from MCCB-class cross-discrimination: Type D upstream (magnetic 10-20×In = 630-1260A trip threshold) vs Type C downstream (magnetic 5-10×In = 160-320A trip threshold) gives a clear magnetic-trip differential. IEC 60947-2 cascade tables typically grant time-current selectivity at ratios ≥1.5:1 across MCCB-MCB pairs.
- **G03 (20A):** 63/20 = 3.15:1 — comfortable margin; full selectivity expected.
- **G05 (10A):** 63/10 = 6.3:1 — comfortable margin.
- **G01 (6A):** 63/6 = 10.5:1 — comfortable margin.

The G02/G04 ratio is the cascade-critical case and the reason for the INFO selectivity flag. Same-curve C-to-C at ~2:1 is at the documented minimum; MCCB-to-MCB at ~2:1 with class differential is acceptable per typical manufacturer tables but engineer-declared (not standard-guaranteed). The mitigation is:

1. **Manufacturer-specific MCCB-MCB cascade chart at 9.0 kA utility-mode + ~4.0 kA genset-mode.** Engineer to verify against the actual MCCB + MCB types installed.
2. **Time-domain transfer analysis.** During the 6-10 s transfer window, the ATS is briefly in dwell (no source) — cascade behaviour cannot be analysed in steady-state alone; fault-level skill must model the transfer sequence per IEC 60909-1:2002.

The example flags this as INFO (not non-compliance) and defers the resolution to the fault-level skill. The fault-level skill must:

- Verify the 9.0 kA utility-mode PFC against the upstream MSB-MAIN F08 declared 22.5 kA + 60m feeder impedance
- Verify the ~4.0 kA genset-mode PFC against the 80 kVA genset Xd" ≈ 0.12 pu equivalent voltage source method per IEC 60909-0:2016 §3.5.1
- Confirm cascade behaviour at BOTH regimes + during the ATS transfer dwell window
- Confirm the MCCB-MCB cascade table grants time-current selectivity at 63:32 = 2:1 with Type D upstream / Type C downstream

## Compliance Assessment

DB-GENSET-XCV is compliant against the relevant standards stack:

- **IEC 60364 series** (general LV distribution baseline)
- **IEC 60364-5-56:2018 §552** (ATS + automatic transfer switching + dual-source) — governs the ATS design, 4-pole transfer, neutral switching, mechanical/electrical interlock
- **IEC 60364-5-56:2018 §551** (LV generating sets) — governs the genset installation (earthing, neutral bonding in genset-mode, exhaust + ventilation, fuel-handling)
- **IEC 60364-5-56:2018 §556** (safety services general) — governs the classification of EM lighting + fire alarm + UPS bypass as safety services with dual-source resilience requirements
- **IEC 60364-5-56:2018 §560.7** (NO RCD on safety-services emergency feeds) — governs the RCD-free status of G02/G03/G04
- **IEC 60364-4-41 §411.3.3** (30 mA RCD on socket circuits ≤32A for additional protection) — applied to G05 mechanical-services
- **IEC 62040-1:2017 §5.2.4** (UPS bypass — fault-current flow requirement) — applied to G04 bypass RCD exemption
- **ISO 8528-12:1997** (genset emergency power supply to safety services) — governs the genset selection + transfer-time classification + cooldown sequence
- **NFPA 110-2022 Type 10** (US-aligned ≤10 s transfer requirement) — cross-jurisdictional benchmark for the transfer-time AHJ disclosure
- **BS EN 50171:2001+A1:2022 §6.3** (central-battery EM transfer time) — cross-jurisdictional benchmark, requires central-battery DB-EM downstream to bridge the gap
- **IEC 60909-0:2016 §3.5 + §3.5.1** (dual-mode fault-current calculation) — governs the utility-mode + genset-mode PFC declarations
- **IEC 60947-2** (MCCB cascade with MCB downstream) — governs the cascade selectivity flag at G02/G04
- **IEC 61439-3:2012** (distribution-board assembly) — governs the panel construction + verification + type-testing

**ONE WARNING flag carried:**

1. **ATS transfer time (6-10 s) AHJ disclosure** — sits AT the NFPA 110-2022 Type 10 (≤10 s) boundary and BELOW the BS EN 50171:2001+A1:2022 §6.3 Type Z (≤0.5 s) threshold. Sign-off required at commissioning against the strictest applicable benchmark. Downstream DB-EM (central-battery) + DB-FA1 (internal battery) + DB-UPS (UPS battery) all bridge the gap through their own autonomy — but the design depends on ALL three of those downstream sub-DBs being correctly specified and commissioned. If the downstream EM-CB unit specification changes (e.g., spec downgrade to self-contained luminaires only), the transfer-time analysis must be re-verified.

The flag is WARNING severity (not info) because it is a hard sign-off gate at commissioning, not a future check. The skill ships the disclosure UPFRONT so the design engineer cannot miss it.

## Schedule Notes

5 circuits + 3 spare ways (W6-W8). Typical future expansion includes:

- Additional safety-services feed: CCTV control panel, security alarm system, addressable-access-control hub (all are "essential" but not life-safety — would land on a 16-20A feed with no RCD per the same §560.7 doctrine)
- Genset block heater (cold-climate retrofit) — exterior-route mechanical-services circuit similar to G05, RCD-protected
- Genset-room utility lighting + maintenance socket — small 6A feed with Type A 30 mA RCD per §411.3.3

Placard on DB-GENSET-XCV faceplate: **"DUAL-SOURCE — UTILITY/GENSET ATS — DO NOT BACK-FEED"** per IEEE 446-1995 critical-power labelling practice + IEC 60364-5-56:2018 §552 dual-source warning requirement.

## Downstream consumer

This board's intent-out.json is consumed by:

- `electrical/sld/examples/intl-commercial-msb-4subdbs/` (SLD multi-board cascade — DB-GENSET-XCV will appear as feeder F08 of MSB-MAIN in the Phase B multi-sheet INT rebuild, with the ATS_BLOCK + GENSET_BLOCK symbols drawn upstream)
- (Future) `electrical/cable-sizing/` — verify 6mm² 4-core, 4mm² 4-core, 2.5mm² 3-core, 1.5mm² 3-core cables against IEC 60364-5-52 ampacity + voltage-drop on the ATS-output side; verify upstream 16mm² 4-core utility feeder + 25mm² 4-core genset-side tie
- (Future) `electrical/fault-level/` — **DUAL-MODE cascade study REQUIRED at G02/G04 (63:32 = ~2:1)** + 9.0 kA utility-mode PFC + ~4.0 kA genset-mode PFC + ATS transfer-dwell time-domain analysis per IEC 60909-1:2002
- (Future) `electrical/earthing/` — verify TN-S bonding on utility side AND genset-side neutral-earth bonding contact at ATS per IEC 60364-5-56:2018 §552; equipotential bonding of genset frame + day-tank + fuel-system per BS 7430:2011
- (Future) `electrical/generator-sizing/` — **the ENTIRE DB-GENSET-XCV connected load (≈30 kVA continuous + transient peaks) is the genset's primary sizing input** + block-load step capability + cold-start transfer-time validation per ISO 8528-5:2018 G3 + ISO 8528-12:1997 Class A2
- (Future) `electrical/riser/` — ATS-fed essential bus segregation from utility AC on shared trays; labelling discipline at every cable break (especially through-floor risers); genset-side tie cable separately routed from utility-side feeder

## See also

- `electrical/db-layout/examples/intl-commercial-tpn-msb/` (upstream — MSB-MAIN F08 feeder; the feeder block where DB-GENSET-XCV is the F08 destination, distinct from F07 = DB-UPS direct-utility feed)
- `electrical/db-layout/examples/intl-dbem-emergency-lighting/` (peer — emergency lighting central-battery sub-DB; G02 here re-energises that DB's charger after the 6-10 s genset transfer; the central-battery 3-hour autonomy bridges the gap)
- `electrical/db-layout/examples/intl-dbfa1-fire-alarm/` (peer — fire-alarm sub-DB; G03 here re-energises that DB's panel after the genset transfer; the 4-hour internal battery bridges the gap)
- `electrical/db-layout/examples/intl-dbups-backed/` (peer — UPS-backed critical-loads sub-DB; G04 here is the genset-backed bypass alternative to the direct-utility feed; UPS 30-min ride-through bridges the gap)
- `electrical/db-layout/examples/intl-dbcomms-data/` (peer — LV data/comms sub-DB; not directly fed from DB-GENSET-XCV in this design but would be a candidate for a future safety-services-classed feed on a spare way)
- `electrical/db-layout/examples/intl-dbl1-lighting/` (peer — general lighting sub-DB; not fed from DB-GENSET-XCV — general lighting is non-essential)
- `electrical/db-layout/examples/intl-dbp1-power/` (peer — small power sub-DB; not fed from DB-GENSET-XCV — general small power is non-essential)
- `electrical/db-layout/examples/intl-dbm1-mechanical/` (peer — mechanical/HVAC sub-DB; not fed from DB-GENSET-XCV in this design but would be a candidate for a future essential-mechanical feed if the design is upgraded to genset-back the HVAC for tropical-climate continuity)
