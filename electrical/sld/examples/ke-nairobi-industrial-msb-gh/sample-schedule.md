# Board-Level SLD Schedule — KE Nairobi Industrial MSB-GH

Project: `ke-nairobi-enterprise-light-engineering-msb-gh`  •  Jurisdiction: KE  •  System: TN-S 415V/240V TPN  •  PFC declared 9.8kA  •  Ze 0.80Ω

| Board ID | Role               | Fed From            | Submain Cable          | Rating (A)               | Length (m) | SPD          |
|----------|--------------------|---------------------|------------------------|--------------------------|------------|--------------|
| MSP-100  | Main switchboard   | KPLC TN-S 415V      | (KPLC service tail)    | 100 TPN (10kA Icu)       | 0          | Type 1+2 ✓   |
| GH-DB    | Sub-DB (gate house)| MSP-100 C08         | 10 mm² 4-core SWA      | 40 MCB Type B + 30mA RCD | 60         | —            |

**System metrics:**

- Imax_total: **41A** (diversity 0.75 applied) — 41% of intake capacity
- Peak PFC at MSP-100: **9.5kA** (≈ 5% margin below 10kA Icu)
- Peak PFC at GH-DB (post-submain): **~3.5kA** (comfortable for 6kA Icu typical GH-DB equipment)
- SPD at MSP-100 intake: **Type 1+2 combined** per KS 1700:2018 §443 (overhead-supply lightning exposure)
- Cascade selectivity: **partially_selective** — see flag below

**Compliance:** ⚠ Non-compliant pending resolution of the MSP-100 C08 → GH-DB selectivity flag.

> **Selectivity issue.** Overcurrent ratio 40A/16A = 2.5:1 is below the 3:1 BS EN 60898 typical threshold. RCDs (30mA upstream + 30mA downstream) are non-selective by design — both trip on any downstream earth fault.
>
> **Recommended resolutions** (either suffices):
>
> 1. Upgrade upstream to **100mA Type S delayed RCD** at MSP-100 C08. RCDs become selective; overcurrent grading still marginal but the bigger issue (earth-fault discrimination) is resolved.
> 2. Remove the **30mA RCDs at GH-DB** and rely on upstream additional protection at C08 per KS 1700:2018 §411.3.3. Cascade trivially "selective" because only one RCD remains.

> _Deterministic refinement of `imax_total_a` and `peak_pfc_ka` is deferred to `calc.sld_system_metrics` per WI3. Values above are LLM estimates flagged via `tool_call_pending_for_system_metrics: true`._
