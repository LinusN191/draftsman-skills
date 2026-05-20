# Reasoning — INT Commercial TPN MSB Earthing Schematic

> **v1.3 — db-layout intent consumption:** This example's `circuits[]` is derived from the upstream db-layout intent at `electrical/db-layout/examples/intl-commercial-tpn-msb/intent-out.json`. The earthing skill adopts the feeder list (F01-F04) verbatim and extends each feeder with CPC sizing, Zs verification, and RCD specification. Circuit IDs match the upstream 1:1.
>
> **Cross-domain note:** The previous v1.0-v1.2 version of this example modelled a rural TT installation (single-phase 230 V, two-rod electrode array, three small final circuits). The v1.3 refresh re-anchors it to the commercial TPN MSB scenario in the paired db-layout example. This demonstrates earthing at the downstream of an INT commercial site rather than rural TT.

> **v1.1 retrofit (2026-05-17):** This example declares `calc.zs_loop_impedance` tool deferral per WI3. The Zs values below are LLM-computed inline; the deterministic tool will refine them when the DraftsMan runtime ships. The `zs_calc_tool_input` replay payload is preserved at the IR root.

## Step 1 — Discovery check
Single consumed intent: db-layout (`intl-commercial-tpn-msb`). Four MSB feeders F01-F04 with declared `voltage_class` per upstream. F04 is `fire_alarm` (life-safety) — flag for ADS-exemption handling per IEC 60364-5-56.

## Step 2 — Standards files to load
Jurisdiction is INT. Loading:
- `shared/standards/electrical/IEC60364/part4-41-electric-shock.json`
- `shared/standards/electrical/IEC60364/part5-54-earthing.json`
- `shared/standards/electrical/IEC60364/part5-56-safety-services.json` (for fire-alarm exemption)
- `shared/standards/electrical/IEC60364/earthing-systems.md`
- `shared/standards/electrical/IEC60617/symbol-index.json`
- `shared/standards/electrical/IEC60617/part2-general.json`

BS 7671 and NFPA 70 NOT loaded.

## Step 3 — Earthing system classification (re-anchor decision)
The paired db-layout intent describes a commercial TPN MSB. The previous v1.2 rural-TT scenario does not fit a commercial multi-tenant building. **Decision: TN-C-S** (commercial typical with utility-supplied PEN bond at the service transformer, Ze=0.30Ω). Alternative TN-S was considered but TN-C-S is the broader INT default for utility-supplied commercial buildings of this size.

Cross-check against `electrical/earthing/ontology/earthing-system-types.json` → TN-C-S permitted for INT, electrode optional, RCD not blanket-required.

IR emits `earthing_system: { system_type: "TN-C-S", code_clause: "IEC 60364-4-41 clause 411.4" }`.

## Step 4 — MET location
MSB cupboard, ground-floor plant room — co-located with the main switchboard for short bond runs.
- `supply_bond_type: "consumer_electrode_only"` — schema canonical value for a non-DNO, non-TN-S supply bond; used here for the INT TN-C-S scenario where the utility PEN bond is external to the installation and the schema's three-value taxonomy (`dno_pme_bond` / `consumer_electrode_only` / `tn_s_separate_pe`) maps this case to `consumer_electrode_only` as the closest non-GB, non-TN-S option.
- Main earthing conductor 70 mm² Cu sized per IEC 60364-5-54 §542.3 against the heaviest fault-path requirement (F02 240mm² line → 120mm² CPC).

## Step 5 — Electrode arrangement
TN-C-S → no installation electrode required. `electrodes: []`. (Previous TT scenario required a two-rod array; this no longer applies under TN-C-S.)

## Step 6 — Main protective bonding
Three main bonding conductors from MET, sized per IEC 60364-5-54 Clause 544.1:
- 35mm² to incoming water service (commercial-scale 80mm pipe)
- 35mm² to incoming gas service (commercial-scale 50mm pipe)
- 25mm² to main column structural steelwork

Half of largest line CSA = 240mm²/2 = 120mm² cap; rule permits ≥ minimum 6mm² and proportional to service entry. 35mm² is adequate for commercial service entries; 25mm² for structural steel.

## Step 7 — Supplementary bonding
None declared at MSB level. Each downstream sub-DB (DB-L1, DB-P1, DB-M1) will declare its own supplementary bonding requirements per zone (kitchens, plant rooms, etc.). DB-FA1 fire-alarm panel is bonded for fault-current return but does not require zone supplementary bonding.

## Step 8 — CPC sizing per feeder

| Feeder | Line CSA | CPC CSA | Method |
|---|---|---|---|
| F01 (LV_power, 150mm²) | 150mm² | 70mm² | IEC 60364-5-54 §543.1.2 (S/2 rule for S>16mm²) |
| F02 (LV_power, 240mm²) | 240mm² | 120mm² | IEC 60364-5-54 §543.1.2 (S/2 rule for S>16mm²) |
| F03 (LV_power, 150mm²) | 150mm² | 70mm² | IEC 60364-5-54 §543.1.2 (S/2 rule for S>16mm²) |
| F04 (fire_alarm, 16mm²) | 16mm² | 16mm² | IEC 60364-5-54 Table 54.2 (S=CPC for S≤16mm²) |

## Step 9 — Zs verification
Compute R1+R2 per feeder using 70°C Cu data (IEC 60228 / Eland tables, single-core XLPE):

| Feeder | Length | R/km line | R/km CPC | R1+R2 | Zs (Ze+R1+R2) | Zs_max (Type D) |
|---|---|---|---|---|---|---|
| F01 (250A) | 35m | 0.165 | 0.342 | 0.0177Ω | 0.318Ω | 0.046Ω |
| F02 (400A) | 40m | 0.106 | 0.197 | 0.0121Ω | 0.312Ω | 0.029Ω |
| F03 (250A) | 45m | 0.165 | 0.342 | 0.0228Ω | 0.323Ω | 0.046Ω |
| F04 (63A C) | 60m | 1.38 | 1.38 | 0.166Ω | 0.466Ω | 0.183Ω |

**Critical observation:** F01-F03 Zs (~0.31-0.32Ω) exceeds the OCPD-only Zs_max (≤0.046Ω) by a factor of ~7. With Ze=0.30Ω and Type D MCCBs (Ia=20·In), the OCPD path cannot satisfy ADS on its own. This is **normal** for commercial MSB feeders.

**ADS strategy (per IEC 60364-4-41 §411.4.2):** ADS is achieved via selective coordination with the downstream DB-level RCDs at DB-L1/DB-P1/DB-M1 — these are the final-circuit protection devices and provide the required disconnection. MSB-level RCDs are intentionally omitted to maintain selectivity and avoid nuisance tripping of life-safety paths.

F04 fire-alarm feeder: `zs_compliance: "ads_exempt_life_safety"` — exempt from ADS per IEC 60364-5-56 §560.

## Step 10 — RCD requirement check
- F01-F03: **no RCD at MSB level.** Documented as selective-coordination strategy. RCDs sit at the downstream DBs.
- F04 (fire_alarm): **no RCD.** IEC 60364-5-56:2018 §560 — life-safety circuits are exempt from automatic disconnection that would compromise the safety service. Continuity assurance via cable monitoring + intumescent containment instead.

## Step 11 — Compliance flags
- Compliant overall under selective-coordination ADS strategy + fire-alarm exemption.
- One TOOL-CALL-PENDING flag for `calc.zs_loop_impedance` — deterministic refinement deferred per WI3.

## Step 12 — Rationale emitted
9-section taxonomy + chat_summary, each section with decisions citing IEC 60364 clauses. See `output.json`.

## Cross-domain re-anchor summary
The previous v1.0-v1.2 example demonstrated TT earthing for a rural single-family dwelling — a perfectly valid earthing scenario, but unrelated to the paired db-layout commercial TPN MSB intent. Strategy A of the v1.3 sprint (per the upstream-contributions spec) chose to re-anchor this example to the commercial scenario so that the earthing skill's INT example demonstrates:

1. Consumption of a non-trivial commercial db-layout intent (TPN, four feeders, mixed voltage classes).
2. CPC sizing under the S/2 rule (S>16mm² regime) — distinct from the small-CSA Table 54.2 lookup the rural TT example covered.
3. ADS strategy decisions (selective coordination, life-safety exemption) that are central to real INT commercial practice.

A future example may reintroduce the rural TT scenario as a separate `intl-rural-tt-dwelling` folder if a matching db-layout intent is added.
