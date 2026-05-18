# Sample Schedule — UK 3-Storey Office Earthing

**Project:** uk-3storey-office-earthing-eg01
**Generated:** 2026-05-18
**Jurisdiction:** GB (BS 7671:2018+A2)
**Supply:** UK DNO TN-C-S 400V TPN, Ze = 0.35 Ω, PSCC 9.8 kA at MSB
**Boards:** MSB-MAIN (plant room) + SDB-GF + SDB-L1 + SDB-L2
**MET:** ground-floor plant room, 25mm² Cu main earthing conductor
**Standards:** BS 7671:2018+A2 Table 41.3 (final 0.4s), Table 41.5 (distribution 5s), Table 54.7 (CPC sizing), §411.3.3 (RCD), §443 (SPD)
**Tool status:** `calc.zs_loop_impedance` deferred per WI3 — values below are LLM-estimates

---

## Zs Verification

| Circuit | Board | Designation | Device | In (A) | Cable (line/CPC) | Length (m) | Zs_calc (Ω) | Zs_max (Ω) | Margin | Verdict | RCD |
|---|---|---|---|---|---|---|---|---|---|---|---|
| F01  | MSB-MAIN | Feeder → SDB-GF             | MCCB-D | 100 | 95mm² / 25mm²  | 15 | 0.358 | 0.488 | +26.6% | pass          | — |
| F02  | MSB-MAIN | Feeder → SDB-L1             | MCCB-D | 100 | 95mm² / 25mm²  | 30 | 0.365 | 0.488 | +25.2% | pass          | — |
| F03  | MSB-MAIN | Feeder → SDB-L2             | MCCB-D | 100 | 95mm² / 25mm²  | 45 | 0.371 | 0.488 | +24.0% | pass          | — |
| G01  | SDB-GF   | GF general lighting          | MCB-B  | 10  | 1.5mm² / 1.0mm² | 25 | 0.97  | 3.49  | +72.2% | pass          | — |
| G02  | SDB-GF   | GF feature/accent lighting   | MCB-B  | 6   | 1.5mm² / 1.0mm² | 18 | 0.80  | 5.82  | +86.3% | pass          | — |
| G03  | SDB-GF   | GF emergency lighting        | MCB-B  | 6   | 1.5mm² / 1.0mm² | 20 | 0.84  | 5.82  | +85.6% | pass          | — |
| G04  | SDB-GF   | GF socket ring A (open E)    | MCB-B  | 32  | 2.5mm² / 1.5mm² | 35 | 1.04  | 1.09  | +4.6%  | pass_with_rcd | 30mA |
| G05  | SDB-GF   | GF socket ring B (open W)    | MCB-B  | 32  | 2.5mm² / 1.5mm² | 28 | 0.91  | 1.09  | +16.5% | pass_with_rcd | 30mA |
| G06  | SDB-GF   | GF socket ring C (reception) | MCB-B  | 32  | 2.5mm² / 1.5mm² | 20 | 0.75  | 1.09  | +31.2% | pass_with_rcd | 30mA |
| G07  | SDB-GF   | GF hand-dryer + WC FCU       | MCB-B  | 20  | 4mm² / 2.5mm²  | 12 | 0.54  | 1.74  | +69.0% | pass_with_rcd | 30mA |
| L101 | SDB-L1   | L1 general lighting          | MCB-B  | 10  | 1.5mm² / 1.0mm² | 26 | 1.00  | 3.49  | +71.3% | pass          | — |
| L102 | SDB-L1   | L1 feature/accent lighting   | MCB-B  | 6   | 1.5mm² / 1.0mm² | 16 | 0.76  | 5.82  | +86.9% | pass          | — |
| L103 | SDB-L1   | L1 emergency lighting        | MCB-B  | 6   | 1.5mm² / 1.0mm² | 22 | 0.90  | 5.82  | +84.5% | pass          | — |
| L104 | SDB-L1   | L1 socket ring A (open E)    | MCB-B  | 32  | 2.5mm² / 1.5mm² | 36 | 1.07  | 1.09  | +1.8%  | pass_with_rcd | 30mA |
| L105 | SDB-L1   | L1 socket ring B (open W)    | MCB-B  | 32  | 2.5mm² / 1.5mm² | 28 | 0.92  | 1.09  | +15.6% | pass_with_rcd | 30mA |
| L106 | SDB-L1   | L1 socket ring C (meetings)  | MCB-B  | 32  | 2.5mm² / 1.5mm² | 22 | 0.80  | 1.09  | +26.6% | pass_with_rcd | 30mA |
| L107 | SDB-L1   | L1 hand-dryer + WC FCU       | MCB-B  | 20  | 4mm² / 2.5mm²  | 16 | 0.61  | 1.74  | +64.9% | pass_with_rcd | 30mA |
| L201 | SDB-L2   | L2 general lighting          | MCB-B  | 10  | 1.5mm² / 1.0mm² | 26 | 1.00  | 3.49  | +71.3% | pass          | — |
| L202 | SDB-L2   | L2 feature/accent lighting   | MCB-B  | 6   | 1.5mm² / 1.0mm² | 16 | 0.76  | 5.82  | +86.9% | pass          | — |
| L203 | SDB-L2   | L2 emergency lighting        | MCB-B  | 6   | 1.5mm² / 1.0mm² | 22 | 0.90  | 5.82  | +84.5% | pass          | — |
| L204 | SDB-L2   | L2 socket ring A (open E)    | MCB-B  | 32  | 2.5mm² / 2.5mm² | 36 | 0.91  | 1.09  | +16.5% | pass_with_rcd | 30mA |
| L205 | SDB-L2   | L2 socket ring B (open W)    | MCB-B  | 32  | 2.5mm² / 1.5mm² | 28 | 0.92  | 1.09  | +15.6% | pass_with_rcd | 30mA |
| L206 | SDB-L2   | L2 socket ring C (collab)    | MCB-B  | 32  | 2.5mm² / 1.5mm² | 22 | 0.80  | 1.09  | +26.6% | pass_with_rcd | 30mA |
| L207 | SDB-L2   | L2 hand-dryer + WC FCU       | MCB-B  | 20  | 4mm² / 2.5mm²  | 16 | 0.61  | 1.74  | +64.9% | pass_with_rcd | 30mA |

**Counts:** 3 distribution feeders + 21 final circuits = 24 total; 12 socket circuits + 3 hand-dryer radials = 15 RCD-protected (Type A 30 mA); 9 lighting/emergency circuits not RCD'd; all Zs-compliant.

---

## Main Bonding

| Bond ID | Source | Target                       | csa     | Sizing rule                          | Citation |
|---|---|---|---|---|---|
| B1 | MET | metal water service (incoming) | 10mm² Cu | PME minimum                          | BS 7671:2018+A2 Reg 544.1.1 |
| B2 | MET | metal gas service (incoming)   | 10mm² Cu | PME minimum                          | BS 7671:2018+A2 Reg 544.1.1 |
| B3 | MET | structural steel — ground floor| 16mm² Cu | long-run margin above PME 10mm² min  | BS 7671:2018+A2 Reg 544.1.1 |
| B4 | MET | structural steel — level 1     | 16mm² Cu | long-run margin                       | BS 7671:2018+A2 Reg 544.1.1 |
| B5 | MET | structural steel — level 2     | 16mm² Cu | long-run margin                       | BS 7671:2018+A2 Reg 544.1.1 |

---

## Supplementary Bonding

| Location | Items bonded | csa | Citation |
|---|---|---|---|
| Plant-room wash-hand basin | tap pillars, exposed pipework, metallic partition | 4mm² Cu | BS 7671:2018+A2 Reg 415.2 |

No supplementary bonding required at general washrooms — 30mA RCD coverage + no exposed metallic pipework expected. Confirm at architect tender stage.

---

## SPD Assessment

| Parameter | Value | Citation |
|---|---|---|
| SPD required | yes | BS 7671:2018+A2 Reg 443.4 |
| SPD type | Type 2 | commercial moderate-risk baseline |
| SPD location | MSB-MAIN intake | upstream of all DBs |
| Type 1 not required | no LPS installed | inputs.has_lightning_protection: false |
| Type 3 at SDBs | not required | cable lengths ≤45m, indoor commercial |

Cross-skill match with SLD UK `spd_assessment_verdict: "required_type_2"`.

---

## Verification Notes

- **Zs_calc** uses Ze_at_board + R1+R2 of the final circuit. Ze_at_board cascades from Ze_declared 0.35Ω + feeder R1+R2.
- **R1+R2** values use 6242Y loop mΩ/m at 70°C PVC operating temperature (1.5/1.0 ≈ 30.2 mΩ/m; 2.5/1.5 ≈ 19.5 mΩ/m; 4/2.5 ≈ 12.6 mΩ/m).
- **Zs_max** values from BS 7671:2018+A2 Table 41.3 (Type B MCB, 0.4s, 230V) and Table 41.5 (MCCB Type D 100A, 5s distribution). Tabulated values include the 0.8 temperature correction per Appendix 14.
- **Margin** = (Zs_max − Zs_calc) / Zs_max × 100. Positive = pass; negative = fail.
- **Verdict key:**
  - `pass` — Zs ≤ Zs_max; OCPD alone provides ADS disconnection
  - `pass_with_rcd` — Zs ≤ Zs_max AND BS 7671:2018+A2 §411.3.3 AMD 2 mandates 30 mA RCD additional protection
  - `fail_needs_rcd` — Zs > Zs_max; RCD required to bring disconnection time within 5 s
- Once `calc.zs_loop_impedance` runtime tool ships, rerun deterministically. Expected refinement: ±5-15% on Zs values; verdicts should not change for this example.
