# Reasoning — INT DB-FA1 (Fire Alarm Panel Sub-DB)

## Site context

Fire alarm panel sub-DB on the generic IEC commercial 3-storey office building. DB-FA1 is the smallest of the four sub-DBs downstream of MSB-MAIN — only the fire-detection system distribution sits behind it. The board is located adjacent to the building's main entrance for two practical reasons:
1. Fire-brigade access during incidents
2. FA installer/serviceman ground-level access for maintenance + commissioning

Fed from MSB-MAIN F04 (63A MCB Type C) via a 60m feeder. The board role is `fire_alarm_panel` — flagged in the `board.role` block so downstream SLD, riser, segregation, and cable-containment consumers recognise it as a life-safety distribution rather than a general-purpose sub-DB.

## Life-safety supply philosophy — IEC 60364-5-56 §560

This is the defining constraint for DB-FA1. IEC 60364-5-56:2018 §560 (life-safety/standby supply systems) governs the entire fire-alarm distribution chain. The fundamental principles:

1. **NO upstream RCD anywhere in the chain.** §560.7.2 prohibits earth-leakage devices on dedicated life-safety circuits because an earth-fault trip during a fire (caused by cable insulation degradation, water ingress from sprinklers, or smoke contamination) would disable the detection system at the exact moment it is needed. This applies to MSB-MAIN F04 AND every final circuit at DB-FA1.

2. **Fire-rated cable for all distribution.** All feeders + final circuits must use cable with the appropriate fire-survival category per IEC 60331 / IEC 60364-5-56 cable category. FP200 LSZH cable is specified throughout — provides 30/60/120-minute survival depending on the specific FP200 variant.

3. **Dedicated circuit isolation.** No other loads share the FA distribution. The 63A intake is sized for the FA panel + zone loops + sounder bank only.

4. **Secondary supply consideration.** §560.7.1 recommends a secondary supply path. For a fire-alarm system, the secondary supply is typically the integral panel battery (IEC 62820 / EN 54-4 panel power supply: 24h standby + 30min alarm minimum). For larger systems or higher-risk sites, an ATS to a generator is added. This DB schedule leaves the ATS decision as an INFO flag — engineer must verify AHJ requirements.

## Board sizing — 63A TPN intake

Connected FA load:
- FA panel power: 0.5 kW
- 3× zone loops @ 0.2 kW = 0.6 kW
- Sounder/strobe circuit: 1.5 kW (peak alarm-condition draw; quiescent ≈ 0.05 kW)
- Battery charger: 0.4 kW
- **Total connected ≈ 3.0 kW**

Design current = 3,000 / (√3 × 400 × 0.85) ≈ 5A. The 63A intake provides massive headroom but matches the upstream MSB-MAIN F04 MCB rating directly. This is the conventional pattern — the FA panel + sounder bank can briefly draw the full alarm current (~10 kVA momentary at evacuation cue), and the headroom accommodates future zone-loop expansion or interface circuits to access-control / lift-recall.

## Circuit-by-circuit reasoning

**FA01 — Fire alarm panel power supply.** 6A Type C MCB. The FA control panel itself (e.g., a Tyco/Apollo/Hochiki addressable panel) presents a switched-mode power supply load with significant capacitive inrush at first energisation. Type C handles it. 5m cable run from DB-FA1 to the panel.

**FA02/FA03/FA04 — Zone loops.** Each zone loop is a low-current addressable detection bus (typically <0.5A quiescent, ~1A in alarm with full sounder activation on the loop). 6A Type C MCB on each. Cable lengths step up by floor: 40m, 60m, 80m. The 80m run to L2 is at the practical edge for a single-loop voltage-drop budget; FA detection panels typically tolerate 8-10% loop voltage drop at the furthest detector, well above electrical-circuit norms.

**FA05 — Sounder/strobe circuit.** 10A Type C MCB. Sounder banks across all 3 floors draw the highest steady-state alarm current at DB-FA1. 2.5mm² FP200 LSZH for the 70m run handles both ampacity and voltage drop within sounder tolerance. Type C handles the inductive inrush of multiple electronic sounders energising simultaneously.

**FA06 — Battery charger / standby supply.** 6A Type C MCB. The integral panel battery charger (lead-acid or VRLA) is a constant-current load with initial charging inrush. 3m run because the battery cabinet typically sits next to the FA panel.

## Cable selection — FP200 LSZH throughout

All FA circuits use FP200 LSZH (low-smoke zero-halogen) fire-rated cable per IEC 60331 / BS EN 50200. The FP200 variant provides:
- 30/60/120-minute fire survival (variant-dependent)
- LSZH sheath for low toxic emission during fire (important in escape routes)
- Single-core or multi-core construction with mica/glass tape insulation

The upstream feeder (60m from MSB-MAIN F04 to DB-FA1) is 16mm² 5-core SWA XLPE Cu in the existing design — engineer should re-evaluate whether the feeder also needs FP200 if the route passes through unprotected escape routes. This is a fire-strategy interface point: depends on the building's compartment-segregation strategy.

## RCD strategy — NONE

**ALL DB-FA1 circuits are RCD-free, AND the upstream MSB-MAIN F04 has no RCD.** This is the §560.7.2 life-safety exemption. The standard final-circuit 30mA Type A RCD policy of IEC 60364-4-41 Clause 411.3.3 is explicitly overridden for dedicated life-safety circuits. The trade-off:

- **Cost of NO RCD:** Loss of earth-leakage personal-shock protection on FA circuits. Mitigated by the fact that FA cabling is mostly inaccessible (concealed in tray, conduit, or behind plant); maintenance/installer access is controlled by IEC 62820 commissioning procedure.
- **Cost of HAVING RCD:** During a fire involving cable degradation, the RCD trips and disables the entire detection + sounder system — catastrophic life-safety failure.

§560 makes the trade-off explicit: protect life-safety availability over earth-leakage shock protection on these specific circuits.

## MCB curve — all Type C

Type C (Ia = 10×In) across all 6 circuits. Type C is the standard FA-system choice:
- Handles capacitive inrush of the FA panel SMPS, zone-loop driver, and sounder bank energisation
- Tighter than Type D so still gives reasonable earth-fault loop disconnection time
- 10 kA Icn (IEC 60898) covers the 9 kA PFC at DB-FA1

Type B was considered but rejected because the panel SMPS + sounder bank energisation can draw 5-6× steady-state for ≈50ms, sitting on the Type B Ia threshold and risking nuisance trip.

## Breaking capacity at DB-FA1

Declared PFC at MSB-MAIN ≈ 25 kA. After the 60m 16mm² SWA feeder, PFC at DB-FA1 ≈ 9 kA — within the 10 kA Icn of standard IEC 60898 MCBs. No cascade backup needed at this point. (Compare to the larger DB-L1/DB-P1/DB-M1 sub-DBs which require cascade backup from the upstream MCCB.)

## Selectivity verification

Upstream MSB-MAIN F04 = 63A MCB Type C. Downstream MCBs at DB-FA1 are ≤10A Type C:
- Current ratio: 63/10 = 6.3:1 — above the 2.5:1 selectivity minimum
- Same-curve coordination (Type C upstream + Type C downstream) needs manufacturer cascade-table confirmation. For typical IEC 60898 ranges, same-curve cascade gives current-only selectivity which usually clears below 6 kA but may not be guaranteed at the full 9 kA fault level
- An engineer-declared assumption per manufacturer cascade table is required (deferred to fault-level skill)

Verdict: pass — flagged with the cascade-table caveat.

## Spare ways

2 spare ways (W7-W8). Typical future expansion includes:
- Additional sounder-strobe circuit for atrium / large-volume spaces requiring extra acoustic coverage
- Interface circuit to access-control system (door-release on fire)
- Interface circuit to lift system (lift-recall on fire)
- Voice-alarm system feed (where the building upgrades from sounder-only to BS EN 54-16 voice alarm)

## ATS recommendation — INFO flag

The compliance_summary carries an INFO flag noting that §560.7.1 recommends a secondary supply for life-safety loads. The current design relies on the integral FA panel battery for backup (typical 24h + 30min). For higher-risk sites or AHJ-mandated secondary supply, an ATS to the building generator or to a dedicated FA standby UPS should be considered. This is not a non-compliance — it's a design-decision flag.

## Downstream consumer

This board's intent-out.json is consumed by:
- `electrical/sld/examples/intl-commercial-msb-4subdbs/` (SLD multi-board cascade, Phase B of SLD rebuild sprint)
- (Future) `electrical/cable-sizing/` — verify FP200 cables against IEC 60364-5-52 + fire-survival cable category
- (Future) `electrical/fault-level/` — Zs verification at the furthest detector terminus (80m loop on L2)
- (Future) `electrical/earthing/` — equipotential bonding of FA panel + sounder enclosures
- (Future) `electrical/riser/` — life-safety segregation of FA feeder from non-essential cables in the riser

## See also

- `electrical/db-layout/examples/intl-commercial-tpn-msb/` (upstream — MSB-MAIN F04 feeder, fire_alarm voltage class flagged)
- `electrical/db-layout/examples/intl-dbl1-lighting/` (peer — lighting sub-DB, also references §560 for the emergency-lighting circuit)
- `electrical/db-layout/examples/intl-dbp1-power/` (peer — small power sub-DB)
- `electrical/db-layout/examples/intl-dbm1-mechanical/` (peer — mechanical/HVAC sub-DB)
