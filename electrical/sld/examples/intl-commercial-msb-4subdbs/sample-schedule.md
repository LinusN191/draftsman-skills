# Board-Level SLD Schedule — INT Commercial 5-Board Cascade

Project: `intl-commercial-msb-4subdbs-eg03`  •  Jurisdiction: INT  •  System: TN-C-S 400V TPN+E  •  PFC declared 16.0kA  •  Ze 0.30Ω

| Board ID | Role                | Fed From          | Submain Cable (mm²)    | Rating (A)              | Length (m) | SPD       |
|----------|---------------------|-------------------|------------------------|-------------------------|------------|-----------|
| MSB-MAIN | Main switchboard    | Utility TN-C-S    | (utility service tail) | 800 MCCB (50kA Icu)     | 0          | Type 2 ✓  |
| DB-L1    | Sub-DB (lighting)   | MSB-MAIN F01      | 150 mm² 5-core SWA     | 250 MCCB Type D         | 35         | —         |
| DB-P1    | Sub-DB (small-pwr)  | MSB-MAIN F02      | 240 mm² 5-core SWA     | 400 MCCB Type D         | 40         | —         |
| DB-M1    | Sub-DB (mechanical) | MSB-MAIN F03      | 150 mm² 5-core SWA     | 250 MCCB Type D         | 45         | —         |
| DB-FA1   | Fire-alarm panel    | MSB-MAIN F04      | 16 mm² 5-core SWA (FR) | 63 MCB Type C (NO RCD)  | 60         | —         |

**System metrics:**

- Imax_total: **170A** (per-class diversity: lighting 0.95, power 0.85, mechanical 0.75, fire 1.0) — 21% of intake capacity, 79% headroom
- Peak PFC: **15.5kA** — comfortably inside 50kA Icu
- SPD at MSB intake: **Type 2** per IEC 60364-4-44:2007 §443
- Cascade selectivity (overall): **partially_selective** — 3 of 4 pairs selective (F01/F03 = 3.2:1, F04 = 12.7:1); F02 (2:1) partial only

**Life-safety isolation:**

- `fire_alarm_dedicated_supply`: **true** — DB-FA1 fed by F04 with NO upstream RCD per IEC 60364-5-56 §560
- `emergency_lighting_dedicated_supply`: false (local battery-pack luminaires; DB-L1 L06 sustained-supply feeder)
- `ups_essential_loads_kva`: 0

**Compliance:** ✓ Compliant. F02 partial selectivity documented in cascade `_note` + assumption — NOT a non-compliance flag. F04 fire-alarm life-safety isolation verified at the SLD tier. 6 assumptions captured (diversity structure, sub-DB-summed-load basis, F02 caveat, DB-FA1 dedicated-supply, PFC service-tail correction, emergency lighting strategy).

> _Deterministic refinement of `imax_total_a` and `peak_pfc_ka` is deferred to `calc.sld_system_metrics` per WI3. Values above are LLM estimates flagged via `tool_call_pending_for_system_metrics: true`._
