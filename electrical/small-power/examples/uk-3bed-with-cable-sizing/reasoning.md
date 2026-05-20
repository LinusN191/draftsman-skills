# Reasoning — UK 3-bedroom 2-storey dwelling, v1.1 hybrid mode (small-power layout with cable-sizing intent consumed)

Project: `uk-3bed-with-cable-sizing-eg01`
Jurisdiction: GB (BS 7671:2018+A2:2022, 18th Edition Amendment 2)
Skill: `electrical/small-power` v1.1.0 (hybrid consumption mode)
Produced: 2026-05-20

This document is the long-form companion to the structured `rationale` block in `output.json`. The eight section titles below mirror the eight `rationale.sections[]` entries one-to-one so an auditor can move between the IR and this narrative without translation.

This example is the **v1.1 consumption-mode** counterpart to `electrical/small-power/examples/uk-3bed-dwelling/` (same scenario, same five circuits, same compliance posture) — the only deltas are in **§6 Diversity + Zs**, where the consumed cable-sizing intent resolves `verified_zs_ohm` per circuit and clears the `TOOL-CALL-PENDING:calc.zs_loop_impedance` flag.

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

The IR records the *total* ring length under `length_m_total` (i.e. the full ring length back to the CU, not the half-leg). In v1.1 this value also appears (under a different name `length_m`) on the consumed cable-sizing intent, where the cable-sizing skill has already computed the conductor resistance and reactance per metre at operating temperature.

All cables are copper, PVC-insulated (PVC_70), and assumed to follow Reference Method 100/101 (clipped direct under floorboards / in stud walls). The final route is delegated to the `cable-containment` skill via the intent contract.

---

## 6. Diversity + Zs

### Diversity factors

Per IET *On-Site Guide* Appendix A Table A1: socket-outlet circuits use 40% diversity on the sum of OCPD ratings, plus 5 A per socket. For this dwelling:

- **C01 ring** (kitchen + utility + dining + lounge + outdoor spur, ~19 sockets): under domestic profile the ring rarely loads more than ~16 A simultaneously (kettle + microwave coincident); `diversified_max_load_a = 16.0`.
- **C02 ring** (3 bedrooms, ~10 sockets): typical loading is a couple of phone chargers, a bedside lamp and an electric blanket; `diversified_max_load_a = 6.5`.
- **C03 cooker**: nameplate 30 A → 10 A + 30% × (30-10) + 5 A (socket on CCU) = 21 A; design value 25 A for 4 A headroom on the 32 A breaker.
- **C04 immersion**: 100% (continuous load, not diversified) → `diversified_max_load_a = 13.0` from the 3 kW nameplate.
- **C05 shaver SSU**: 0.5 kW nameplate → 2.2 A; no diversification applied.

These figures populate `intent-out.json` for `db-layout` consumption when sizing the CU feeder.

### Zs resolution (v1.1 mode — cable-sizing intent consumed)

This is a small-power **v1.1 example** demonstrating the migration target documented in `docs/superpowers/specs/2026-05-20-cable-sizing-skill-design-refresh.md §2`. The cable-sizing intent at `consumed-cable-sizing-intent.json` carries per-circuit `r1_plus_r2_milliohm_per_m_at_operating_temp` + `reactance_milliohm_per_m` + `length_m` — small-power v1.1's Step 12 uses these to resolve Zs without deferring to `calc.zs_loop_impedance`.

**Lookup mechanic.** For each small-power circuit, the lookup key is `f"{parent_db.designation}.{circuit_id}"` — here `"CU-MAIN.C01"` through `"CU-MAIN.C05"`. The cable-sizing intent's `circuits[].node_id` matches these implicit keys directly. No `cable_sizing_node_id` explicit overrides are required for this example.

**Computation.** Per circuit:

```
verified_zs_ohm = Ze + (r1_plus_r2 / 1000) × length_m + (reactance / 1000) × length_m
```

Ze comes from `supply_origin.ze_declared_ohm` (0.35 Ω for this TN-C-S installation). The `/1000` converts mΩ/m → Ω/m. Results:

| circuit_id | length (m) | r1+r2 (mΩ/m) | reactance (mΩ/m) | Zs_segment (Ω) | Zs total (Ω) | OCPD Zs_max (Ω) |
|---|---|---|---|---|---|---|
| C01 | 32 | 18.1 | 0.08 | 0.5818 | **0.9318** | 1.44 (32A Type-B MCB, 0.4s ADS) |
| C02 | 28 | 18.1 | 0.08 | 0.5090 | **0.8590** | 1.44 |
| C03 | 8  | 7.95 | 0.08 | 0.0642 | **0.4142** | 1.44 |
| C04 | 4  | 18.1 | 0.08 | 0.0727 | **0.4227** | 2.87 (16A Type-B MCB, 5s ADS) |
| C05 | 3  | 30.3 | 0.10 | 0.0912 | **0.4412** | 7.68 (6A Type-B MCB, 5s ADS) |

All Zs values are well within Zs_max for their OCPD per BS 7671:2018+A2:2022 Table 41.3 (Type-B MCBs at 230 V, with 0.4 s ADS for socket-outlet circuits ≤ 32 A per Reg 411.3.2.2 and 5 s for fixed-equipment circuits per Reg 411.3.2.3). The worst margin is C01 at 0.9318 Ω vs 1.44 Ω limit — still ~35% headroom — reflecting the longest ring length (32 m) at the smallest CSA permitted for a 32 A ring (2.5 mm²).

**Provenance.** The resolution is recorded in:
- `meta.consumed_intents[]` — declares the cable-sizing intent at `intent_type: "cable-sizing"`, `intent_version: "1.0.0"`, `produced_by: "electrical/cable-sizing"`
- Per-circuit `verified_zs_ohm` populated, `tool_call_pending_for_zs_verification: false`
- `TOOL-CALL-PENDING:calc.zs_loop_impedance` flag dropped from `flags[]` (compare with the v1.0 `uk-3bed-dwelling` example which retains the flag — that example demonstrates the hybrid **fallback** path)
- First entry in `compliance_summary.assumptions[]` documents the resolution formula and the v1.1 hybrid mode

**Comparison with v1.0 fallback.** The companion v1.0 example `electrical/small-power/examples/uk-3bed-dwelling/` is the same dwelling scenario **without** intent consumption. In that example, `verified_zs_ohm` is absent on every circuit, `tool_call_pending_for_zs_verification: true`, and the TOOL-CALL-PENDING flag is retained — the engineer would resolve Zs later when `calc.zs_loop_impedance` ships (WI3 deferral). v1.1 hybrid mode is **non-breaking**: small-power runs either way and the engineer never sees a downgrade in the fallback case.

The second deferred call, `TOOL-CALL-PENDING:calc.diversity_factor`, is **retained** in this example — diversity is not within the cable-sizing intent's scope and remains a separate calc-skill responsibility.

---

## 7. Compliance + Assumptions

`compliance_summary.compliant = true`. Three info-severity entries record design intent without flagging non-compliance:

1. **Bathroom zones 1+2 contain no sockets** — documented for clarity. The shaver SSU is the only socket and sits in zone 3, satisfying §701.512.3.
2. **Outdoor socket on FCU spur** — IP65 enclosure, 30 mA RCD upstream; both §522.6.201 and §522.6.202 satisfied.
3. **Zs resolved from cable-sizing intent** — v1.1 hybrid consumption replaces the v1.0 WI3 deferral; ring continuity (r1/rn/r2 measurement) still to be confirmed at install per §612.

`compliance_summary.assumptions[]` records eight engineering assumptions, with the new first entry recording the v1.1 Zs resolution mechanic:

- **Zs resolved from consumed cable-sizing intent** (formula + version recorded).
- Ze = 0.35 Ω **declared**, not measured (Chapter 64 verification required).
- PSCC = 6 kA **declared**; CU busbar and all RCBOs are 6 kA Icu.
- Ground-floor ring footprint ~52 m² (within IET OSG §8.4.4 100 m² limit).
- First-floor ring footprint ~36 m² (well within limit).
- Diversity per IET OSG Appendix A.
- Cable Reference Method 100/101 assumed; final route via cable-containment skill.
- Outdoor spur load ≤ 1.5 kW (lawnmower-equivalent).

If any declared value (Ze, PSCC) fails verification on site, the design must be re-run with measured values and `verified_zs_ohm` re-derived.

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

**Upstream intent consumed** (v1.1 delta): `meta.consumed_intents` carries one entry for `electrical/cable-sizing` v1.0.0. The presence of this intent toggles small-power into **hybrid consumption mode** (Step 12 resolves Zs from intent rather than deferring). The v1.0 leaf-skill behaviour is preserved as the **fallback** path when `consumed_intents` is empty — both paths are exercised by the example pair `uk-3bed-dwelling/` (fallback) and `uk-3bed-with-cable-sizing/` (this example).
