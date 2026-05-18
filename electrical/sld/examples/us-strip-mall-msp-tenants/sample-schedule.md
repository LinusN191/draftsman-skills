# Board-Level SLD Schedule — US Strip Mall 4-Board Cascade

Project: `us-strip-mall-msp-tenants-eg04`  •  Jurisdiction: US  •  System: TN-S 208Y/120V 3φ 4-wire  •  PFC declared 22.0kA  •  Ze 0.10Ω

| Board ID | Role                    | Fed From       | Submain Cable (AWG)         | Rating (A)              | Length (m) | SPD       |
|----------|-------------------------|----------------|-----------------------------|-------------------------|------------|-----------|
| MSP-A    | Main service panelboard | US utility TN-S| (service-entrance THHN)     | 200 panelboard (25kA AIC) | 0        | Type 1+2 ✓|
| TSP-A    | Suite 100 (apparel)     | MSP-A T01      | 3/0 AWG Cu THHN (4-wire)    | 100 2-pole              | 30         | Type 2 ✓  |
| TSP-B    | Suite 200 (food-svc)    | MSP-A T02      | 3/0 AWG Cu THHN (4-wire)    | 100 2-pole              | 35         | Type 2 ✓  |
| CA-P     | Common area + exterior  | MSP-A T03      | 6 AWG Cu THHN (4-wire)      | 60 2-pole               | 50         | Type 2 ✓  |

**System metrics:**

- Imax_total: **127A** (diversity 0.85 applied) — 64% of intake capacity, 36% headroom
- Peak PFC: **21.0kA** — 16% below 25kA AIC margin (typical US commercial)
- SPD at MSP-A intake: **Type 1+2** combined assembly per NEC 2023 Article 285.23 (Type 1 service-entry) + NEC 285.24 (Type 2 at branch panels)
- Cascade selectivity (overall): **partially_selective** — T01/T02 (2:1) below 3:1 typical, T03 (3.33:1) selective. NEC 240.86 series-rated combinations acceptable for general retail (NOT mandated full coordination per NEC 620.62 / 700.27 / 517.17 scope).

**Life-safety isolation:**

- `fire_alarm_dedicated_supply`: false (24V supervised loop per NFPA 72 with battery backup)
- `emergency_lighting_dedicated_supply`: false (per-fixture battery packs per NFPA 101; CA-P C03 sustained-supply distribution)
- `ups_essential_loads_kva`: 0

**Compliance:** ✗ **CRITICAL non-compliance** — CA-P C05 fire-pump branch (60A Type D, 11kW motor) violates NEC 695.4(A) independent-source rule. Fire-pump on shared common-area panel could be disabled by a fault elsewhere on CA-P during a fire event.

**Remediation options:**

1. **Relocate C05 fire-pump to dedicated FP-1 controller** fed line-side of MSP-A main disconnect (tap-ahead-of-service-disconnect per NEC 695.3 / NEC 695.4(A)).
2. **Independent service drop** from utility for fire-pump only (separate meter + service entrance).

> **Teaching scenario:** This non-compliance is intentionally surfaced at the SLD tier to demonstrate that **multi-board compliance tensions (like NEC 695.4(A) fire-pump-on-shared-panel) only become visible when the SLD aggregates across db-layouts**. A single-board review of CA-P cannot see the rule violation — it operates at service-entry topology level.

> _Deterministic refinement of `imax_total_a` and `peak_pfc_ka` is deferred to `calc.sld_system_metrics` per WI3. Values above are LLM estimates flagged via `tool_call_pending_for_system_metrics: true`._
