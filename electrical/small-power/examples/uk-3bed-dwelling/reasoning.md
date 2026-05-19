# Reasoning — UK 3-bedroom 2-storey dwelling (small-power layout)

Project: `uk-3bed-dwelling-eg01`
Jurisdiction: GB (BS 7671:2018+A2:2022, 18th Edition Amendment 2)
Skill: `electrical/small-power` v1.0.0
Produced: 2026-05-19

This document is the long-form companion to the structured `rationale` block in `output.json`. The eight section titles below mirror the eight `rationale.sections[]` entries one-to-one so an auditor can move between the IR and this narrative without translation.

---

## 1. Jurisdiction + Supply

The project is a single-occupancy 2-storey dwelling in Great Britain with a notional floor area of ~100 m². Because the jurisdiction is `GB`, the applicable wiring rules are BS 7671:2018+A2:2022 (the IET 18th Edition Amendment 2, published March 2022 and effective from 28 September 2022), supplemented by the IET *On-Site Guide* (BS 7671:2018+A2:2022 OSG) for installation-level idioms such as ring final circuit composition and diversity tables.

The DNO supply is **TN-C-S** ("PME") at the cut-out: a single combined PEN conductor up to the meter, then split into separate N and PE inside the consumer unit. The declared parameters at the consumer cut-out are:

| Parameter | Declared | Source |
|---|---|---|
| Nominal voltage | 230 V (1Ø, 50 Hz) | BS 7671 §313.1.1 |
| External earth-loop impedance Ze | 0.35 Ω | DNO declaration |
| Prospective short-circuit current PSCC | 6.0 kA | DNO declaration |
| Earthing system | TN-C-S | DNO drawing |

These are *declared* values, not measured. Per BS 7671 Chapter 64 / §612 they must be verified at first energisation; the design margin assumes the declared values hold. The parent consumer unit `CU-MAIN` is a 12-way Amendment-3 metal-enclosed board (BS EN 61439-3 compliant) with a 6 kA Icu busbar — selected because the declared PSCC at the busbar equals 6.0 kA, so every protective device installed on it must have a breaking capacity ≥ 6 kA per BS 7671 §434.5.1 and BS EN 60898-1.

The split-load configuration of Amendment 3 (main switch + two RCD-protected ways) is *not* used here; every circuit is fitted with its own RCBO so that a single residual earth fault disconnects only one circuit. This is the post-Amendment-2 idiom and reflects §314.1 (division of circuits) intent.

---

## 2. Circuit Topology

Five circuits are designed:

| ID | Designation | Topology | OCPD | Cable | Rooms |
|---|---|---|---|---|---|
| C01 | Ground-floor ring | ring | 32 A RCBO B + Type A 30 mA | 2.5/1.5 mm² Cu PVC | kitchen, utility, dining, lounge, outdoor (spur) |
| C02 | First-floor ring | ring | 32 A RCBO B + Type A 30 mA | 2.5/1.5 mm² Cu PVC | bedroom-1, bedroom-2, bedroom-3 |
| C03 | Cooker outlet | dedicated radial | 32 A RCBO B + Type A 30 mA | 6 mm² T+E | kitchen |
| C04 | Immersion heater | dedicated radial | 16 A RCBO B + Type A 30 mA | 2.5 mm² T+E | utility |
| C05 | Bathroom shaver supply | dedicated radial | 6 A RCBO B + Type A 30 mA | 1.5 mm² T+E | bathroom |

**Ring topology** is the GB-idiomatic socket-network arrangement and is explicitly permitted by BS 7671 §433.1.5 (a ring final circuit may have a protective device of a rating up to 32 A when wired in 2.5 mm² copper). The IET *On-Site Guide* §8.4.4 recommends a floor-area footprint of ≤ 100 m² per 32 A ring; both rings here are well inside that envelope (ground-floor ~52 m², first-floor ~36 m²).

**Cooker on dedicated 32 A radial:** a typical 7 kW hob+oven combination (~30 A nameplate) would dominate a ring under diversity and is conventionally split off. 6 mm² T+E to a 45 A cooker-control-unit (CCU) is standard per IET OSG Table A1.

**Immersion heater on dedicated 16 A radial:** the 3 kW immersion element is a continuous load and benefits from independent disconnection at the CU. 2.5 mm² T+E to a 20 A double-pole isolation switch (FCU at the cylinder) is the conventional treatment.

**Shaver supply on dedicated 6 A radial:** the bathroom shaver supply unit (SSU) is a BS EN 61558-2-5 isolating transformer with a small primary load. A 6 A breaker provides discrimination and limits fault energy in the bathroom Part 7-701 environment.

---

## 3. Special Locations

Two BS 7671 special-location categories apply: **bathroom** (Part 7-701) and **outdoor** (Section 522.6).

**Bathroom (Part 7-701):** the room is classified as `bathroom_zone_3` (the area outside the 0.6 m projection of the bath/shower but inside the room boundary). BS 7671 §701.512.3 prohibits 13 A socket outlets within 3 m of the boundary of zone 1. In a typical UK family bathroom the entire room falls within that 3 m radius, so the design installs **only** the shaver supply unit (SSU) — explicitly excepted by §701.512.3 — and no general-purpose sockets. The IR records `special_location: "bathroom_zone_3"` and lists exactly one socket (`bathroom-S01`) of type `BS_EN_61558_2_5_shaver_supply_unit` on circuit C05. INV-05 (zone 1/2 must have zero sockets; zone 3 must contain only SSU/SELV) is therefore satisfied.

**Outdoor garden socket:** one IP65 weatherproof double socket is provided on the external wall, fed via a 13 A fused connection unit (FCU) spur off the ground-floor ring C01. Two BS 7671 clauses apply:
- §522.6.201 — installations subject to exposure to weather require ingress protection ≥ IPX4; IP65 exceeds this.
- §522.6.202 (additional protection) — 30 mA RCD additional protection is mandatory for outdoor socket outlets. Because C01 is an RCBO with 30 mA Type A residual protection, this is automatically satisfied.

The outdoor socket carries `fed_by_spur: true`, `ip_rating: "IP65"`, and `spur_load_kw: 1.5` (lawnmower-equivalent worst case). It is mounted 1100 mm AFFL on the external wall — a height that keeps the inlet above splash and accidental contact level.

Two info-severity flags in `compliance_summary.non_compliance_flags[]` document the bathroom zone configuration and the outdoor spur arrangement so an auditor or downstream skill (db-layout, cable-containment) sees the design intent without re-deriving it.

---

## 4. RCD Posture

Every circuit is fitted with a 30 mA Type A RCBO. The driver is BS 7671 §411.3.3 (additional protection by 30 mA RCD for socket outlets with rated current ≤ 32 A in dwellings), and the choice of **Type A** rather than Type AC reflects the post-Amendment-2 default for new domestic installations: Type A is sensitive to both AC and pulsating-DC residual currents, which covers the typical electronics found in a modern dwelling (LED drivers, EMC filters, small appliances).

No circuit requires Type B (which adds sensitivity to smooth DC residual currents). Type B is required where the equipment can introduce smooth DC into the supply — typically EV charging points (BS 7671 §722.531.3.101) or single-phase PV inverters without galvanic isolation. None of those are present in this dwelling, so the IR records `rcd_posture: "type_a_30ma_per_§411_3_3"` for all five circuits and no `rcd_exception_citation` is needed.

A frequent design question is whether the SSU circuit (C05) needs its own RCD given that the SSU itself isolates the secondary. The answer here is yes: §411.3.3 applies to all sockets in dwellings — the SSU primary connection counts — and the cost delta between an MCB and an RCBO at 6 A is negligible. The design opts for RCBO uniformity across the board.

---

## 5. OCPD + Cable

OCPD selection follows the load profile of each circuit:

- **Curve B** for every circuit: domestic loads have no significant inrush (no large motors, no transformer banks, no discharge-lamp gear). Type B trips at 3–5 × In, giving the best Zs disconnection margin per BS 7671 §411.4.5.
- **Breaking capacity ≥ 6 kA Icu**: declared PSCC at the busbar is 6 kA, so every RCBO must meet that breaking capacity per §434.5.1 and BS EN 60898-1. The selected RCBOs are 6 kA Icu products.

Cable sizing reasoning:

| Circuit | Cable | Rationale |
|---|---|---|
| C01, C02 rings | 2.5 mm² + 1.5 mm² CPC | BS 7671 Table 7.1: standard 32 A ring composition for PVC singles or T+E. |
| C03 cooker | 6 mm² T+E | 32 A radial; 6 mm² gives ~37 A current-carrying capacity in Reference Method C and adequate Zs margin to a CCU at 8 m. |
| C04 immersion | 2.5 mm² T+E | 16 A radial; 2.5 mm² is conventional for a 3 kW immersion at 4 m. |
| C05 shaver | 1.5 mm² T+E | 6 A radial at 3 m; 1.5 mm² CPC matches the live conductor. |

The IR records the *total* ring length under `length_m_total` (i.e. the full ring length back to the CU, not the half-leg). This is the value the calc.zs_loop_impedance skill will consume to compute r1+rn+r2 and Zs.

All cables are copper, PVC-insulated (PVC_70), and assumed to follow Reference Method 100/101 (clipped direct under floorboards / in stud walls). The final route is delegated to the `cable-containment` skill via the intent contract.

---

## 6. Diversity + Zs

**Diversity:** the IR records both `estimated_max_load_kw` (sum of nameplate loads on the circuit) and `diversified_max_load_a` (after applying IET *On-Site Guide* Appendix A factors).

For the cooker:
- Nameplate: 7 kW hob+oven ≈ 30 A at 230 V.
- Diversity formula (IET OSG Appendix A): 10 A + 30% × (30-10) + 5 A for the socket on the CCU = 10 + 6 + 5 = **21 A**.
- Design value 25 A → comfortably within 32 A breaker, with margin for the small CCU socket.

For the rings, domestic usage profile rarely loads more than ~16 A on a ground-floor ring (kettle + microwave coincident) or ~6.5 A on a first-floor ring (a couple of phone chargers, a bedside lamp and an electric blanket). These diversified figures are the ones the `db-layout` skill should consume when sizing the consumer-unit feeder.

**Zs verification:** the loop impedance Zs = Ze + (r1 + r2) for radials, or Zs = Ze + (r1·r2)/(r1+r2) for the parallel legs of a ring (with both legs continuous), and must satisfy the §411.4.5 disconnection time tables (Type B 32 A, 0.4 s → Zs ≤ 1.37 Ω with 18th-Edition Cmin = 0.95).

The small-power skill v1.0 does **not** compute Zs itself — it is delegated to the `calc.zs_loop_impedance` skill per WI3 (the deferred-tool-call work item in the spec). Every circuit therefore carries `tool_call_pending_for_zs_verification: true`, and the IR-level `flags[]` array contains the string `TOOL-CALL-PENDING:calc.zs_loop_impedance` so the orchestrator knows to invoke the calc skill before drawing or before sign-off. INV-08 (Zs deferral consistency) is satisfied: every circuit's flag matches the top-level flag.

A second deferred call, `TOOL-CALL-PENDING:calc.diversity_factor`, allows the runtime to re-derive the diversified currents with a more rigorous formula (e.g. IEC 60364-1 Annex B if requested) and update `diversified_max_load_a` in place.

---

## 7. Compliance + Assumptions

`compliance_summary.compliant = true`. Three info-severity entries record design intent without flagging non-compliance:

1. **Bathroom zones 1+2 contain no sockets** — documented for clarity. The shaver SSU is the only socket and sits in zone 3, satisfying §701.512.3.
2. **Outdoor socket on FCU spur** — IP65 enclosure, 30 mA RCD upstream; both §522.6.201 and §522.6.202 satisfied.
3. **Zs deferred to calc** — per WI3 the loop-impedance check is a downstream calc-skill responsibility.

`compliance_summary.assumptions[]` records seven engineering assumptions:

- Ze = 0.35 Ω **declared**, not measured (Chapter 64 verification required).
- PSCC = 6 kA **declared**; CU busbar and all RCBOs are 6 kA Icu.
- Ground-floor ring footprint ~52 m² (within IET OSG §8.4.4 100 m² limit).
- First-floor ring footprint ~36 m² (well within limit).
- Diversity per IET OSG Appendix A.
- Cable Reference Method 100/101 assumed; final route via cable-containment skill.
- Outdoor spur load ≤ 1.5 kW (lawnmower-equivalent).

If any declared value (Ze, PSCC) fails verification on site, the design must be re-run with measured values and Zs re-checked.

---

## 8. Drafting References

The drawing intent is a single A1 sheet at 1:50 metric scale, suitable for both floor plans, a CU schedule and notes on one drawing. Layer naming follows **BS 1192:2007+A2:2016** (Discipline-Element-Modifier convention):

- `E-POW-OUTLET-G` — ground-floor power outlets
- `E-POW-OUTLET-1` — first-floor power outlets
- `E-POW-CIRCUIT-G` / `E-POW-CIRCUIT-1` — circuit identification
- `E-POW-ZONE-BATH` — bathroom Part 7-701 zone overlay

Drawing notes annotate:

1. Standard socket types (BS 1363 double 13A switched) and mounting heights (450 mm AFFL general / 1150 mm above worktop / 1100 mm external).
2. Bathroom Part 7-701 zone overlay and the SSU-only restriction.
3. Outdoor IP65 FCU spur arrangement.
4. The BS 1192 layer scheme used.

Downstream skills consuming this IR:

- **`db-layout`** consumes `intent-out.json` to size the CU feeder (sum of `diversified_max_load_a` weighted by ring vs radial diversity).
- **`cable-containment`** consumes the same intent to plan routes from the CU to each room.
- **`schematic`** consumes the intent to draw the single-line of the consumer unit.

No upstream intent is consumed (`meta.consumed_intents: []`) because small-power is a leaf skill in v1.0.
