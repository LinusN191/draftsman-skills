# Reasoning — INT Commercial TPN MSB Earthing Schematic (TN-C-S)

> **Sprint A.1 C1 cause-fix (2026-05-25):** This folder was previously named `intl-rural-tt/` but the content (input, output, intent-out) has always been TN-C-S — never TT. The misnamed folder was renamed to `intl-rural-tncs/` to match the actual system type. A NEW genuine TT example will be authored at the freed `intl-rural-tt/` slot in Sprint C.1. The four MSB feeders F01-F04 were also incorrectly certified `pass` with `rcd_required: false` despite Zs exceeding the OCPD-only Zs_max by 2.5×-10.8×; they are now flagged `fail_needs_rcd` with mandatory MSB-level RCDs per IEC 60364-4-41 §411.4.9(b). See the dedicated `## C1 cause-fix (Sprint A.1)` section below.

> **v1.3 — db-layout intent consumption:** This example's `circuits[]` is derived from the upstream db-layout intent at `electrical/db-layout/examples/intl-commercial-tpn-msb/intent-out.json`. The earthing skill adopts the feeder list (F01-F04) verbatim and extends each feeder with CPC sizing, Zs verification, and RCD specification. Circuit IDs match the upstream 1:1.
>
> **Cross-domain note:** Although the folder name was previously `intl-rural-tt/`, the content was always TN-C-S commercial — the folder name was a lie. Sprint A.1 renamed it to `intl-rural-tncs/`. The system modelled here is a commercial TPN MSB with utility PEN bond (Ze=0.30Ω), not a rural TT dwelling.

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

## Step 3 — Earthing system classification (TN-C-S, not TT)
The paired db-layout intent describes a commercial TPN MSB. **Decision: TN-C-S** (commercial typical with utility-supplied PEN bond at the service transformer, Ze=0.30Ω). Alternative TN-S was considered but TN-C-S is the broader INT default for utility-supplied commercial buildings of this size. The folder name `intl-rural-tt/` in versions prior to Sprint A.1 was misleading — the input always declared TN-C-S; the folder was renamed to `intl-rural-tncs/` in Sprint A.1 to remove the lie.

Cross-check against `electrical/earthing/ontology/earthing-system-types.json` → TN-C-S permitted for INT, electrode optional, RCD not blanket-required.

IR emits `earthing_system: { system_type: "TN-C-S", code_clause: "IEC 60364-4-41 clause 411.4" }`.

## Step 4 — MET location
MSB cupboard, ground-floor plant room — co-located with the main switchboard for short bond runs.
- `supply_bond_type: "consumer_electrode_only"` — schema canonical value for a non-DNO, non-TN-S supply bond; used here for the INT TN-C-S scenario where the utility PEN bond is external to the installation and the schema's three-value taxonomy (`dno_pme_bond` / `consumer_electrode_only` / `tn_s_separate_pe`) maps this case to `consumer_electrode_only` as the closest non-GB, non-TN-S option.
- Main earthing conductor 70 mm² Cu sized per IEC 60364-5-54 §542.3 against the heaviest fault-path requirement (F02 240mm² line → 120mm² CPC).

## Step 5 — Electrode arrangement
TN-C-S → no installation electrode required. `electrodes: []`. (The folder name historically suggested a TT scenario with two-rod array, but the actual input has always declared TN-C-S so no electrodes are emitted.)

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

**Critical observation:** F01-F03 Zs (~0.31-0.32Ω) exceeds the OCPD-only Zs_max (≤0.046Ω) by a factor of ~7. F04 (fire-alarm, 0.466Ω) exceeds its OCPD-only Zs_max (0.183Ω) by 2.5×. With Ze=0.30Ω and Type D MCCBs (Ia=20·In) on F01-F03 plus Type C MCB on F04, the OCPD path cannot satisfy §411.4.7 disconnection on its own for any of the four feeders.

**ADS strategy (per IEC 60364-4-41 §411.4.7 + §411.4.9(b)):** ADS at each MSB feeder requires an RCD as supplement to the OCPD. The prior version's "selective coordination via downstream RCDs only" rationale was the C1 false-pass defect — §411.4.7 requires ADS at the protective device of each circuit and cannot be delegated to downstream devices. **All four MSB feeders flagged `fail_needs_rcd`** in this corrected version.

## Step 10 — RCD requirement check (Sprint A.1 C1 cause-fix)
- **F01-F03 (LV_power MSB feeders): 300 mA Type A time-delayed (S-type) RCD required at the MSB level.** §411.4.9(b) supplements the Type D MCCB with an RCD to clear earth-fault current in the required disconnection time. The time-delayed (S) curve preserves selectivity with downstream 30/100 mA RCDs at DB-L1/DB-P1/DB-M1.
- **F04 (fire_alarm): 30 mA Type A RCD required at the MSB feeder.** IEC 60364-5-56 §560 prioritises *availability* of life-safety services but does NOT exempt life-safety circuits from ADS. A 30 mA Type A RCD with continuity monitoring satisfies §411.4.9(b); intumescent containment and continuity monitoring preserve the safety-service availability requirement.

## Step 11 — Compliance flags
- **Not compliant as drawn — four critical non-compliance flags** raised against F01-F04 (`fail_needs_rcd`). Adding the four MSB-level RCDs (300 mA on F01-F03, 30 mA on F04) per §411.4.9(b) clears the flags.
- One TOOL-CALL-PENDING flag for `calc.zs_loop_impedance` — deterministic refinement deferred per WI3.

## Step 12 — Rationale emitted
9-section taxonomy + chat_summary, each section with decisions citing IEC 60364 clauses. See `output.json`.

## Cross-domain re-anchor summary
The folder name `intl-rural-tt/` previously suggested a rural TT dwelling scenario, but the actual content (input, output, intent-out) has always declared TN-C-S commercial. Sprint A.1 renamed the folder to `intl-rural-tncs/` so the name matches the content. The earthing skill's INT example demonstrates:

1. Consumption of a non-trivial commercial db-layout intent (TPN, four feeders, mixed voltage classes).
2. CPC sizing under the S/2 rule (S>16mm² regime) — distinct from the small-CSA Table 54.2 lookup typical of a rural TT scenario.
3. ADS strategy decisions including **mandatory RCD supplementation** under IEC 60364-4-41 §411.4.9(b) when OCPD alone cannot meet §411.4.7 disconnection time.

A genuine TT example for a rural single-family dwelling (high-Ra electrode + mandatory 30 mA RCD per §411.5 / Reg 411.5) will be authored at the freed `intl-rural-tt/` slot in **Sprint C.1**.

## C1 cause-fix (Sprint A.1)

**Defect identified by external Reviewers 1, 5, and 13 (DEFECT_REGISTER C1):**
1. The folder name `intl-rural-tt/` did not match the content (TN-C-S all along).
2. Circuits F01-F04 reported `zs_compliance: "pass"` with `rcd_required: false`, but Zs exceeded the OCPD-only Zs_max by 2.5×-10.8×. A designer trusting this would ship circuits with **no effective earth-fault protection**.

**Cause-fix applied (not symptom-papering):**
- **Folder rename.** `intl-rural-tt/` → `intl-rural-tncs/` via `git mv`. The freed name will host a genuine TT example in Sprint C.1.
- **Compliance disposition corrected per circuit.** Each of F01-F04 now reports `zs_compliance: "fail_needs_rcd"` with `rcd_required: true` and an `rcd_sensitivity_ma` aligned to IEC 60364-4-41 §411.4.9(b):
  - F01 (Zs 0.318Ω, Zs_max 0.046Ω → 6.9× over): 300 mA Type A time-delayed RCD.
  - F02 (Zs 0.312Ω, Zs_max 0.029Ω → 10.8× over): 300 mA Type A time-delayed RCD.
  - F03 (Zs 0.323Ω, Zs_max 0.046Ω → 7.0× over): 300 mA Type A time-delayed RCD.
  - F04 (Zs 0.466Ω, Zs_max 0.183Ω → 2.5× over, fire_alarm): 30 mA Type A RCD with continuity monitoring; IEC 60364-5-56 §560 availability priority does **not** waive the ADS requirement.
- **Compliance summary downgraded to `compliant: false`** with two critical `non_compliance_flags` (F01-F03 group + F04) so consumer skills (sld, fault-level, db-layout) see the unresolved fault-protection gap rather than a false-pass.
- **Standards citation form.** IEC 60364-4-41:2017 §411.4.7 (TN automatic disconnection) + §411.4.9(b) (RCD-protected supplement) cited per circuit and at the rationale section level, matching the INT citation form in CLAUDE.md.

The Zs and Zs_max values themselves were **not** recomputed — Reviewer 13's audit oracle confirmed the existing values are correct; only the compliance disposition logic was wrong.
