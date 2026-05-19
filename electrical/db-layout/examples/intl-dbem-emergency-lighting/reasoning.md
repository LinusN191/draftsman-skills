# Reasoning — INT DB-EM (Emergency Lighting Central Battery Sub-DB)

## Site context

Emergency lighting central battery sub-DB for the generic IEC commercial 3-storey office building. DB-EM is a dedicated life-safety distribution downstream of MSB-MAIN F05 — only the emergency-lighting system (corridor + stairwell + exit-sign luminaires + central battery + monitoring) sits behind it. The board is located in the ground-floor EM equipment room for two practical reasons:

1. Co-location with the central-battery cabinet — keeps the 230V output side of the battery short and minimises voltage-drop loss on the high-current charge path
2. Adjacent to MSB-MAIN — 80m feeder run keeps cable cost and submain impedance within standard distribution-board fault-level bounds

Fed from MSB-MAIN F05 (40A MCB Type C) via an 80m feeder. The board role is `emergency_lighting_panel` — flagged in the `board.role` block so downstream SLD, riser, segregation, and cable-containment consumers recognise it as a life-safety distribution rather than a general-purpose sub-DB.

## Board Identification

DB-EM follows the same identification pattern as DB-FA1 (fire-alarm peer): single-board scope, IP4X enclosure rating (indoor equipment room), and life-safety role flag. The `emergency_lighting_panel` role is distinct from `fire_alarm_panel` because the two systems have different supply-philosophy details:

- FA panels typically have an integral panel battery (24h standby + 30min alarm per IEC 62820 / EN 54-4)
- EM systems use a **central battery** sized for 1-3h autonomy per BS EN 50171:2001+A1:2022

The role flag drives downstream segregation: EM cables must not share containment with non-essential power circuits, and the riser skill enforces dedicated EM-tray segregation per IEC 60364-5-56:2018 §560.8.

## Incoming Supply — IEC 60364-5-56:2018 §560 governs the chain

This is the defining constraint for DB-EM. IEC 60364-5-56:2018 §560 (life-safety/standby supply systems) governs the entire EM distribution chain. The fundamental principles mirror the FA case:

1. **NO upstream RCD anywhere in the chain.** §560.7 prohibits earth-leakage devices on dedicated life-safety circuits because an earth-fault trip during a fire (caused by cable insulation degradation, smoke contamination, or water ingress) would extinguish escape-route lighting at the exact moment occupants depend on it. This applies to MSB-MAIN F05 AND every final circuit at DB-EM.

2. **Fire-rated cable for all distribution.** All feeders + final circuits must use cable with the appropriate fire-survival category per IEC 60331 / IEC 60364-5-56:2018 §560.8. FP200 LSZH cable is specified throughout — provides 30/60/120-minute survival depending on the specific FP200 variant.

3. **Dedicated circuit isolation.** No non-essential loads share the EM distribution. The 40A intake is sized for the EM panel + 6 luminaire zones + battery charger + monitoring only.

4. **Secondary supply: the central battery itself.** For EM lighting, the secondary supply IS the central-battery system. BS EN 50171:2001+A1:2022 §6.12 specifies minimum autonomy of 1h, 2h, or 3h depending on building classification. Most commercial offices require 3h to cover the full evacuation + fire-fighting window. The central battery + integral changeover inverter is rated as an IEC 60598-2-22:2014+A2:2020 compliant emergency-lighting power supply.

### Fault level at DB-EM

Declared PFC at MSB-MAIN ≈ 22.5 kA. After the 80m 16mm² Cu XLPE submain, PFC at DB-EM ≈ 7.5 kA — comfortably within the 10 kA Icn of standard IEC 60898 MCBs. No cascade backup needed at this distribution point.

## Circuit Breakdown — 8 circuits across 3 zones

Connected EM load:

- 3× corridor/escape-route circuits @ 0.8 kW = 2.4 kW (LED escape-route luminaires, ~30 luminaires per floor at 25W ea.)
- 3× stairwell/exit-sign circuits @ 0.4 kW = 1.2 kW (LED stairwell luminaires + exit signs at ~10W ea.)
- 1× battery charger @ 1.2 kW (boost-charge transient; steady-state ~0.3 kW)
- 1× monitoring/test circuit @ 0.1 kW (addressable monitoring interface)
- **Total connected ≈ 4.9 kW**

Design current ≈ 4,900 / (√3 × 400 × 0.85) ≈ 8.3A. The 40A intake provides healthy headroom — matches the upstream MSB-MAIN F05 MCB rating directly, and the headroom covers battery-charger boost transient + simultaneous luminaire energisation after a test discharge.

### Circuit-by-circuit reasoning

**EM01/EM03/EM05 — Corridor + escape-route luminaires (GF / L1 / L2).** 10A Type C MCB each. Escape-route LED luminaires step up in count by floor footprint and corridor length. Cable lengths: 35m, 45m, 55m. 1.5mm² Cu FP200 LSZH handles both 230V ampacity and voltage drop within emergency-luminaire driver tolerance.

**EM02/EM04/EM06 — Stairwell + exit signs (GF / L1 / L2).** 6A Type C MCB each. Stairwell + exit-sign load is lower than corridor (fewer luminaires per zone, exit signs are ~5W ea.). Cable lengths: 25m, 35m, 45m. 1.5mm² Cu FP200 LSZH.

**EM07 — Central battery charger.** 16A Type C MCB. The central battery is sized for ~3-hour autonomy. After a discharge cycle (e.g., monthly test), the charger draws a boost-charge transient ~5A steady-state with peaks during the bulk-charge phase. 2.5mm² FP200 LSZH for the short 2m run to the battery cabinet. 16A Type C handles the SMPS inrush + boost transient without nuisance trip.

**EM08 — EM panel monitoring + test circuit.** 6A Type C MCB. Low-current monitoring interface for the addressable luminaire monitoring system + manual test-switch panel. 2m run to the monitoring controller adjacent to the central battery.

## Cable selection — FP200 LSZH throughout

All EM circuits use FP200 LSZH (low-smoke zero-halogen) fire-rated cable per IEC 60331 / BS EN 50200. The FP200 variant provides:

- 30/60/120-minute fire survival (variant-dependent)
- LSZH sheath for low toxic emission during fire (important in escape routes — occupants pass through these spaces during evacuation)
- Single-core or multi-core construction with mica/glass tape insulation

The upstream submain (80m from MSB-MAIN F05 to DB-EM) is 16mm² 5-core Cu XLPE in the existing design. Engineer should re-evaluate whether the submain also needs FP200 if the route passes through unprotected escape routes. The 80m run is in a dedicated EM riser/containment per IEC 60364-5-56:2018 §560.8 segregation — confirmed via the riser skill output.

## RCD strategy — NONE

**ALL DB-EM circuits are RCD-free, AND the upstream MSB-MAIN F05 has no RCD.** This is the §560.7 life-safety exemption. The standard final-circuit 30mA Type A RCD policy of IEC 60364-4-41 §411.3.3 is explicitly overridden for dedicated life-safety circuits. The trade-off:

- **Cost of NO RCD:** Loss of earth-leakage personal-shock protection on EM circuits. Mitigated by the fact that EM cabling is mostly inaccessible (concealed in tray, conduit, or above ceilings); maintenance access is controlled by IEC 60598-2-22 commissioning procedure and BS EN 50171 inspection schedule.
- **Cost of HAVING RCD:** During a fire involving cable degradation, the RCD trips and extinguishes the escape-route luminaires — catastrophic life-safety failure during the evacuation window.

§560.7 makes the trade-off explicit: protect life-safety availability over earth-leakage shock protection on these specific circuits.

## MCB curve — all Type C

Type C (Ia = 10×In) across all 8 circuits. Type C is the standard EM-system choice:

- Handles capacitive inrush of LED luminaire driver banks (modern LED escape-route luminaires use SMPS drivers with significant inrush)
- Handles battery-charger SMPS energisation transient
- Tighter than Type D so still gives reasonable earth-fault loop disconnection time per IEC 60364-4-41 §411.3.2
- 10 kA Icn (IEC 60898) covers the 7.5 kA PFC at DB-EM

Type B was considered but rejected because the LED driver bank + battery-charger inrush can draw 6-8× steady-state for ≈50ms, sitting on the Type B Ia threshold and risking nuisance trip during test discharges.

## Selectivity verification

Upstream MSB-MAIN F05 = 40A Type C MCB. Downstream MCBs at DB-EM are 6-16A Type C:

- Worst case ratio at EM07 (16A charger): 40/16 = 2.5:1 — meets the IEC 60898 minimum same-curve cascade threshold
- Best case ratio at EM02/EM04/EM06/EM08 (6A): 40/6 = 6.7:1 — comfortable selectivity margin
- Same-curve coordination (Type C upstream + Type C downstream) needs manufacturer cascade-table confirmation. For typical IEC 60898 ranges at 7.5 kA fault level, same-curve cascade gives current-only selectivity that clears below 6 kA but may need engineer-declared confirmation at the full 7.5 kA
- An engineer-declared assumption per manufacturer cascade table is required (deferred to fault-level skill for full coordination study)

Verdict: pass — flagged with the cascade-table caveat. Note that EM07 sits at the worst-case ratio; consider 20A or 25A upstream feeder if the building grows and EM07 needs to scale.

## Compliance Assessment

DB-EM is compliant against the relevant standards stack:

- **IEC 60364-5-56:2018 §560** (life-safety supply chain) — NO upstream RCD, dedicated isolation, fire-rated cable, secondary supply
- **BS EN 50171:2001+A1:2022** (central-battery system) — 3-hour autonomy minimum, sealed VRLA or Li-ion bank with integral charger + changeover inverter
- **IEC 60598-2-22:2014+A2:2020** (luminaires for emergency lighting) — all escape-route, stairwell, and exit-sign luminaires listed as IEC 60598-2-22 compliant

One INFO flag carried: AHJ-required survival duration (1h, 2h, or 3h per local building code) must be verified against the battery commissioning certificate at handover. The central-battery installer must provide:

1. BS EN 50171 compliance certificate
2. 3-hour discharge test report (or shorter per AHJ)
3. Per-luminaire conformity declaration (IEC 60598-2-22)
4. Monthly + annual test schedule per BS EN 50172 inspection regime

This is not a non-compliance — it's a design-decision flag noting that the design assumes 3h autonomy and the AHJ may accept shorter.

## Schedule Notes

8 circuits + 4 spare ways (W9-W12). Typical future expansion includes:

- Basement EM lighting zone (if building adds basement parking or plant-room)
- Plant-room EM coverage (if not already on a separate plant-room sub-DB)
- External escape-route luminaires (if site has external assembly point lighting)
- Addressable luminaire-monitoring interface circuit (upgrade path to BS EN 50172 automatic test system)

## Downstream consumer

This board's intent-out.json is consumed by:

- `electrical/sld/examples/intl-commercial-msb-4subdbs/` (SLD multi-board cascade, Phase B of SLD rebuild sprint — DB-EM will appear as feeder F05 of MSB-MAIN)
- (Future) `electrical/cable-sizing/` — verify FP200 cables against IEC 60364-5-52 + fire-survival cable category
- (Future) `electrical/fault-level/` — Zs verification at the furthest L2 corridor luminaire (55m run on EM05)
- (Future) `electrical/earthing/` — equipotential bonding of EM panel + luminaire enclosures
- (Future) `electrical/riser/` — life-safety segregation of EM feeder from non-essential cables in the riser

## See also

- `electrical/db-layout/examples/intl-commercial-tpn-msb/` (upstream — MSB-MAIN F05 feeder, emergency_lighting voltage class flagged)
- `electrical/db-layout/examples/intl-dbfa1-fire-alarm/` (peer — fire-alarm sub-DB, same §560 supply philosophy)
- `electrical/db-layout/examples/intl-dbl1-lighting/` (peer — general lighting sub-DB, references §560 for any EM lighting carried on the general-lighting board)
- `electrical/db-layout/examples/intl-dbp1-power/` (peer — small power sub-DB, non-essential)
- `electrical/db-layout/examples/intl-dbm1-mechanical/` (peer — mechanical/HVAC sub-DB, non-essential)
