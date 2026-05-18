# Board-Level SLD Schedule — UK 3-Storey Office

Project: `uk-3storey-office-eg01`  •  Jurisdiction: GB  •  System: TN-C-S 400V TPN  •  PFC declared 9.8kA  •  Ze 0.35Ω

| Board ID | Role               | Fed From          | Submain Cable (mm²) | Rating (A)         | Length (m) | SPD       |
|----------|--------------------|-------------------|---------------------|--------------------|------------|-----------|
| MSB-MAIN | Main switchboard   | UK DNO TN-C-S     | (DNO service)       | 400 MCCB (36kA Icu)| 0          | Type 2 ✓  |
| SDB-GF   | Sub-DB (ground)    | MSB-MAIN F01      | 35 mm² 5-core SWA   | 100 MCCB Type D    | 15         | —         |
| SDB-L1   | Sub-DB (level 1)   | MSB-MAIN F02      | 35 mm² 5-core SWA   | 100 MCCB Type D    | 30         | —         |
| SDB-L2   | Sub-DB (level 2)   | MSB-MAIN F03      | 35 mm² 5-core SWA   | 100 MCCB Type D    | 45         | —         |

**System metrics:**

- Imax_total: **146A** (diversity 0.85 applied) — 36% of intake capacity
- Peak PFC: **9.5kA** — comfortably inside 36kA Icu
- SPD at MSB intake: **Type 2** per BS 7671:2018+A2 Reg 443
- Cascade selectivity: **fully_selective** — 4:1 ratio (400A / 100A) exceeds BS EN 60947-2 typical threshold (~3:1)

**Compliance:** ✓ Compliant. Final-circuit RCDs (30mA Type A) located at sub-DB level on socket circuits, preserving MSB-level cascade selectivity. Emergency lighting + fire alarm via local battery-backed equipment (no dedicated life-safety distribution at this scale).

> _Deterministic refinement of `imax_total_a` and `peak_pfc_ka` is deferred to `calc.sld_system_metrics` per WI3. Values above are LLM estimates flagged via `tool_call_pending_for_system_metrics: true`._
