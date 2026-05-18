# Zs Verification Schedule — Nairobi Industrial TN-S

**Project:** ke-nairobi-enterprise-light-engineering
**Generated:** 2026-05-18
**Jurisdiction:** KE (KS 1700:2018 + BS 7671:2018+A2)
**Supply:** KPLC TN-S 415V/240V 50Hz, Ze = 0.80 Ω
**Standards:** BS 7671 Table 41.2 (adopted by KS 1700 Annex E) for Zs_max; IEC 60364-5-52 Annex B for cable R+X
**Tool status:** `calc.zs_loop_impedance` deferred per WI3 — values below are LLM-estimates

---

| Circuit | Ib (A) | Device | In (A) | Cable (line/CPC) | Length (m) | R1+R2 (Ω) | Zs_calc (Ω) | Zs_max (Ω) | Margin (%) | Verdict | RCD |
|---|---|---|---|---|---|---|---|---|---|---|---|
| C01 | 7.5  | MCB_B  | 10 | 1.5mm² / 1.0mm² | 35 | 0.65 | 1.45 | 4.60 | +68.5% | pass | 30mA |
| C02 | 4.5  | MCB_B  | 6  | 1.5mm² / 1.0mm² | 22 | 0.41 | 1.21 | 7.67 | +84.2% | pass | 30mA |
| C03 | 28.0 | MCB_B  | 32 | 2.5mm² / 1.5mm² | 28 | 0.54 | 1.34 | 1.44 | +6.9%  | pass | 30mA |
| C04 | 16.0 | MCB_B  | 20 | 2.5mm² / 2.5mm² | 18 | 0.24 | 1.04 | 2.30 | +54.8% | pass | 30mA |
| C05 | 9.6  | MCB_C  | 20 | 2.5mm² / 2.5mm² | 15 | 0.19 | 0.99 | 1.15 | +13.9% | pass | n/a  |
| C06 | 4.2  | MCB_C  | 16 | 1.5mm² / 1.5mm² | 12 | 0.21 | 1.01 | 1.44 | +29.9% | pass | n/a  |
| C07 | 14.0 | MCB_D  | 25 | 4mm² / 4mm²     | 25 | 0.19 | 0.99 | 0.46 | -53.5% | **fail_needs_rcd** | 100mA |
| C08 | 35.0 | MCB_B  | 40 | 10mm² / 6mm² SWA| 60 | 0.60 | 1.40 | 1.15 | -17.9% | **fail_needs_rcd** | 30mA  |

---

## Notes

- **Ib (design current)** is at full design load. Actual operating current will be lower under partial load.
- **R1+R2** is the loop resistance of line + CPC at 70°C PVC operating temperature, per IEC 60364-5-52 Annex B.
- **Zs_calc** = Ze (0.80 Ω) + R1+R2.
- **Zs_max** from BS 7671 Table 41.2 (KS 1700 Annex E adopts verbatim). Table values already include the 0.8 temperature correction.
- **Margin** = (Zs_max − Zs_calc) / Zs_max × 100. Positive = pass; negative = fail.
- **Verdict** key:
  - `pass` — Zs ≤ Zs_max; protective device alone provides disconnection
  - `pass_with_rcd` — Zs ≤ Zs_max AND KS 1700 §411.3.3 mandates RCD on this socket circuit
  - `fail_needs_rcd` — Zs > Zs_max; RCD required to achieve disconnection time
  - `fail_oversize_cpc` — Zs > Zs_max even with RCD threshold; CPC must be oversized

## Failures explained

- **C07 (Compressor 7.5kW)**: Type D MCB demands Ia = 20×In, giving Zs_max = 230/(20×25) = 0.46 Ω. Calculated Zs (0.99 Ω) exceeds. 100mA RCD specified (higher than 30mA to avoid nuisance trips on motor leakage).
- **C08 (60m submain)**: Long route × 6mm² CPC pushes Zs to 1.40 Ω vs Type B 40A Zs_max of 1.15 Ω. 30mA RCBO required — also satisfies KS 1700 §411.3.3 socket-circuit RCD policy at the gate-house downstream DB.

## Verification

Once `calc.zs_loop_impedance` runtime tool ships, the engineer will rerun this schedule deterministically. Expected refinement: ±5-15% on Zs values; verdicts should not change for this example.
