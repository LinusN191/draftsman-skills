# Reasoning — KE Nairobi Industrial TN-S

> **v1.3 — db-layout intent consumption:** This example's `circuits[]` is derived from the upstream db-layout intent at `electrical/db-layout/examples/ke-nairobi-industrial-100A-tpn/intent-out.json`. The earthing skill adopts the circuit list verbatim and extends each circuit with CPC sizing, Zs verification, and RCD specification. Circuit IDs match the upstream 1:1.

## Site context

Light engineering workshop on Enterprise Road, Nairobi Industrial Area. 1980s build, KPLC supply via dedicated 11kV/415V substation 180m down the road. Three-phase 415V/240V 4-wire 50 Hz with 100A TPN main switch.

Supply is **TN-S** — separate-Earth cable from substation transformer star point, terminated at the MET. KPLC declared Ze = 0.65Ω at 1987 commissioning; the latest measurement in 2026 shows Ze = 0.80Ω. The slow rise over 39 years is typical of older TN-S cables with progressive sheath corrosion. Design ceiling assumes 0.80Ω; further degradation triggers recalc.

## Why TN-S (not TN-C-S)

KPLC supplies a small number of legacy industrial sites on TN-S because the substation's neutral-earth bond is at the transformer star point only — there is no PEN conductor combining N and Earth at the consumer's intake. Most modern KPLC installations are TN-C-S (PME) with consumer-side N/E split, but older industrial sites in Industrial Area retain TN-S because the supply infrastructure predates PME rollout.

TN-S vs TN-C-S engineering differences exercised by this example:
- **Higher Ze.** TN-S typically 0.65-1.0Ω; TN-C-S typically 0.20-0.35Ω. This squeezes the Zs compliance margin on every circuit.
- **No PEN at intake.** Supply bond type is `tn_s_separate_pe` rather than `dno_pme_bond`. Affects the schematic symbology + supplementary bonding obligations.
- **DNO declaration uncertainty.** TN-S Ze degrades over building life; engineers should verify by measurement rather than relying on the original declaration alone.

## Why the compressor needs a 100mA RCD

C07 is a 3-phase 7.5kW reciprocating compressor with start-stop duty cycle. The high inrush demands a **Type D MCB** (Ia = 20 × In) to ride out the starting transient without nuisance tripping. The downside: Type D's higher trip multiplier requires a **lower Zs_max** to ensure the device trips in time on an earth fault:

```
For MCB_D at 25A:
  Zs_max = 230 / (20 × 25) = 0.46 Ω
```

This circuit's calculated Zs = 0.99Ω, which exceeds 0.46Ω. Without additional protection, the MCB would not trip within 5 seconds — non-compliant with KS 1700:2018 §411.4.5 (Annex E adoption of BS 7671:2018+A2 Reg 411.4.5).

The standard fix per KS 1700:2018 §411.4.5 is to add **RCD additional protection**. The 100mA RCD (rather than 30mA) is selected because:
- The compressor has a high earth leakage current at start-up (motor inrush + capacitive coupling in the SY cable)
- 30mA RCDs nuisance-trip on this duty profile
- 100mA RCD provides shock protection at fault levels without nuisance tripping during normal duty

## Why the gate-house submain needs a 30mA RCBO

C08 is a 60m run to a gate house, terminating in a small 4-way sub-DB serving sockets and lighting. The long run with 6mm² CPC pushes Zs above Type B 40A's Zs_max:

```
For MCB_B at 40A:
  Zs_max = 230 / (5 × 40) = 1.15 Ω
Calculated Zs = Ze + (R1+R2)
             ≈ 0.80 + 0.60
             ≈ 1.40 Ω
```

This exceeds 1.15Ω. Two compliance paths:

1. **Upsize the CPC to 10mm²** — R2 drops, Zs drops below 1.15Ω. Costly cable replacement.
2. **Add 30mA RCBO** — RCD additional protection achieves 0.4s disconnection on socket-final-circuit fault. Faster and cheaper.

We chose option 2. The 30mA sensitivity is required by KS 1700 §411.3.3 anyway (socket circuits ≤32A — even though this is a 40A submain, the downstream sockets behind it inherit the requirement).

## Kenya-specific RCD policy

KS 1700:2018 §411.3.3 mandates 30mA RCD on all socket circuits regardless of Zs compliance. This mirrors the BS 7671 AMD 2 (2022) socket-RCD rule but with one key difference: KS 1700 applies it from initial adoption, while BS 7671's rule was retrofit. Practically, Kenyan installations have been wired this way since 2018; UK engineers reviewing a Kenyan design should expect blanket RCD coverage on all socket circuits as standard practice.

This is why C01-C04 + C08 are all 30mA RCD-protected even when Zs alone wouldn't demand it. C05-C07 are dedicated machine circuits (no sockets) and are not RCD-protected as a matter of course.

## KS 1700 vs BS 7671

KS 1700:2018 references BS 7671 extensively. The substantive sections (411 ADS, 415 supplementary bonding, 544 main bonding, Table 41.2 Zs_max, Table 54.7 CPC sizing) are adopted **verbatim** via KS 1700 Annex E. The canonical clause-by-clause adoption map and the list of KS-specific deviations are now first-class KS1700 standards-layer artifacts — see `KS1700/annex-E-bs7671-adoption-table.json` for the adoption table and `KS1700/ks-unique-deviations.json` for the deviation index (covering items like the universal socket-RCD policy at §411.3.3 and the EV-charging routing at §722).

In v1.2, our citations use the direct form `"KS 1700:2018 §X.Y.Z"` since KS 1700 is a first-class standards layer in this repo. Where transparency helps, the Annex E adoption is noted parenthetically: `"KS 1700:2018 §411.4 (Annex E: adopts BS 7671:2018+A2 Reg 411.4 verbatim)"`. The canonical KS↔BS adoption mapping lives in `KS1700/annex-E-bs7671-adoption-table.json`; KS-specific deviations live in `KS1700/ks-unique-deviations.json`.

## Why the Zs values are LLM-estimates

`calc.zs_loop_impedance` is the new WI3-deferred tool contract introduced in this skill version (v1.1.0). The deterministic Python implementation lives in the DraftsMan runtime — it has not yet shipped. Until then, the LLM produces rough Zs estimates inline using approximate per-CSA cable resistance values.

The `zs_calc_tool_input` block at the IR root captures the complete payload the tool will consume when it ships. The runtime can replay this against `IEC60364/part5-52-cable-impedance.json` (the canonical per-CSA AC R+X table shipped 2026-05-17) without re-prompting the LLM.

Expect refinement of ±5-15% on Zs values when the tool ships. The compliance verdicts (pass / pass_with_rcd / fail_needs_rcd) should not change for this example.

## Tool deferral check

When `tool_call_pending_for_zs: true`:
- `zs_calc_tool_input` is present and well-formed (verified by validator INV-09)
- Top-level `flags` array contains `TOOL-CALL-PENDING:calc.zs_loop_impedance` disclaimer

When the runtime tool ships, both go away — `tool_call_pending_for_zs: false`, the flag is removed, and `circuits[].zs_ohm` carries tool-precision values.
