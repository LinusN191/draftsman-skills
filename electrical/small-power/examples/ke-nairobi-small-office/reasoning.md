# Reasoning — KE Nairobi 80 m² commercial office unit (small-power layout)

Project: `ke-nairobi-office-eg01`
Jurisdiction: KE (KS 1700:2018 — The Kenyan Wiring Regulations)
Skill: `electrical/small-power` v1.0.0
Produced: 2026-05-19

This document is the long-form companion to the structured `rationale` block in `output.json`. The eight section titles below mirror the eight `rationale.sections[]` entries one-to-one so an auditor can move between the IR and this narrative without translation.

The citation convention throughout this document follows the small-power v1.0 D-3 rule for Kenyan jurisdiction work:

- Primary citations always lead with `KS 1700:2018 §X` (the year qualifier is mandatory — `KS 1700` alone is non-conformant).
- Where the Kenyan code routes to BS 7671 (i.e. the rule body adopts the BS 7671 clause text), the explicit routing form is used: `KS 1700:2018 §313 routes to BS 7671:2018+A2:2022 §313.1`. This form makes the chain auditable.
- Annotating a BS 7671 citation with a parenthetical Kenyan adoption note is **forbidden** by D-3 — the chain must be expressed as a routing call (`KS 1700:2018 §X routes to BS 7671:2018+A2:2022 §Y`), not a passive annotation.

---

## 1. Jurisdiction + Supply

The project is a tenant fit-out for an 80 m² ground-floor commercial office unit in Nairobi, Kenya. Because the jurisdiction is `KE`, the primary code is **KS 1700:2018 — The Kenyan Wiring Regulations** (published by the Kenya Bureau of Standards). KS 1700:2018 mirrors the structure of BS 7671 and explicitly routes large portions of its rule body to BS 7671 clauses; the routing must be made visible in any audit document.

The supply is a **KPLC TN-S 415V TPN+E** distribution (three-phase 400/415 V + neutral + separate dedicated protective earth conductor). Declared parameters at the parent distribution board `DB-OFFICE-01`:

| Parameter | Declared | Source |
|---|---|---|
| Nominal voltage | 415 V (3Ø, 50 Hz) line-to-line / 240 V phase-to-neutral | KS 1700:2018 §313 |
| Earthing arrangement | TN-S (separate PE) | KPLC connection drawing |
| External earth-loop impedance Ze | 0.45 Ω | KPLC declaration |
| Prospective short-circuit current PSCC | 9.0 kA | KPLC declaration |

These are **declared** values, not measured. Per KS 1700:2018 routing to BS 7671:2018+A2:2022 Chapter 64 they must be verified at first energisation. The design margin assumes the declared values hold.

KS 1700:2018 §313 routes explicitly to BS 7671:2018+A2:2022 §313.1 for the short-circuit verification rule (the consumer's installed protective device must have a breaking capacity at least equal to the prospective short-circuit current at that point). Because PSCC = 9.0 kA at the busbar, every MCB installed on `DB-OFFICE-01` must therefore have an Icu ≥ 9 kA. The selected products are 9 kA Icu MCBs sourced from the BS EN 60898-1 product range — the routing chain `KS 1700:2018 §434 → BS 7671:2018+A2:2022 §434.5.1 → IEC 60898-1` is the auditable basis.

---

## 2. Circuit Topology

Four final circuits are designed, **all radial** (no ring final circuits):

| ID | Designation | Topology | OCPD | Cable | Rooms |
|---|---|---|---|---|---|
| C01 | Workstations 1-2 + reception | radial | 20 A MCB B + Type A 30 mA | 2.5 mm² T+E | workstation-1, workstation-2, reception |
| C02 | Workstations 3-4 | radial | 20 A MCB B + Type A 30 mA | 2.5 mm² T+E | workstation-3, workstation-4 |
| C03 | Kitchenette + fridge FCU | radial | 20 A MCB B + Type A 30 mA | 2.5 mm² T+E | kitchenette |
| C04 | Toilet shaver supply | dedicated_radial | 6 A MCB B + Type A 30 mA | 1.5 mm² T+E | toilet |

**Why radial, not ring?** KS 1700:2018 §433 routes to BS 7671:2018+A2:2022 §433.1.5, and that clause permits ring final circuits in KE jurisdiction (this is also reflected in the small-power v1.0 invariant INV-04, which lists `{GB, KE}` as the ring-allowed jurisdictions). However, common KE commercial engineering practice for a tenant fit-out at this scale favours radial-only topology for three reasons:

1. **Selectivity at the parent DB.** With dedicated radials each having their own MCB, a fault on any one circuit isolates a discrete group of sockets, simplifying fault-finding in a commercial tenant context where multiple users share the space.
2. **Test burden at handover.** Ring continuity testing (r1, rn, r2 + the open-end test) adds installation and verification effort; a radial only needs R1+R2 + Zs at the furthest point.
3. **Future flexibility.** When a tenant churns and a new workstation block is added, extending a radial is operationally simpler than re-validating ring continuity on a partially modified circuit.

The design intent in `input.json` is therefore explicit: `"preferred_topology": "radial"`. The IR records every circuit as `radial` or `dedicated_radial`; INV-04 (ring restricted to GB/KE jurisdictions) is satisfied trivially because no ring exists.

**Why a dedicated radial for the SSU (C04)?** The bathroom/toilet shaver supply unit is an isolating transformer per BS EN 61558-2-5; routing it on a dedicated 6 A MCB radial gives discrimination and limits the fault energy that can be delivered into a Part 7-701 zone. The cable is 1.5 mm² T+E — adequate for the SSU primary current (~0.4 A) and meeting the smallest CPC size required for a 6 A circuit.

---

## 3. Special Locations

The only special-location room in this fit-out is the **toilet**, classified as `bathroom_zone_3`. KS 1700:2018 §701 routes to BS 7671:2018+A2:2022 Part 7-701 (locations containing a bath or shower). Although the brief calls the room a "toilet/cleaner's cupboard" (not a bathroom in the strict sense), the wash-hand basin and possible cleaner's slop-sink mean the Part 7-701 zoning rules apply by analogy — and by convention KE M&E engineers apply the same zone treatment to commercial WCs as to domestic bathrooms when classifying socket locations.

§701.512.3 prohibits general-purpose 13 A socket outlets within 3 m of the zone 1 boundary. Because the room is only 2.0 × 1.5 m and falls entirely within that 3 m radius, the design installs **only** a BS EN 61558-2-5 shaver supply unit (`toilet-S01`) — explicitly excepted by §701.512.3. No general-purpose sockets are placed in the toilet.

INV-05 (special-location compliance: `bathroom_zone_1` / `bathroom_zone_2` must have zero sockets; `bathroom_zone_3` must contain only SSU/SELV outlets) is satisfied: the room has one socket and it is the SSU.

The SSU is mounted at 1400 mm AFFL on a non-condensing surface, well above splash level and clear of the zone 1 / zone 2 boundary. No outdoor sockets are required in this fit-out — the unit is internal-only.

A single info-severity flag in `compliance_summary.non_compliance_flags[]` records the bathroom zone configuration so the downstream `db-layout` and `cable-containment` skills see the design intent without re-deriving it.

---

## 4. RCD Posture

Every circuit uses **30 mA Type A** residual-current protection. The implementation is board-level RCD protection upstream of the MCBs at `DB-OFFICE-01` (rather than per-circuit RCBOs), which is the typical KE commercial idiom on small TPN distribution boards.

KS 1700:2018 §411.3.3 routes to BS 7671:2018+A2:2022 §411.3.3 for the additional-protection-by-RCD rule on socket outlets with rated current ≤ 32 A. The IR records `rcd_posture: "type_a_30ma_per_§411_3_3"` on every circuit.

**Why Type A, not Type AC?** Type A is sensitive to both AC and pulsating-DC residual currents and is the modern default for installations with electronics — office equipment (laptop PSUs, monitor EMI filters, LED drivers, small kitchen appliances) frequently injects pulsating-DC into the protective conductor. KS 1700:2018 routing to BS 7671:2018+A2:2022 §411.3.3 + IET On-Site Guide §5.3 makes Type A the post-Amendment-2 default for general-purpose socket circuits. Type AC is not recommended for new installations.

**Why not Type B?** Type B adds sensitivity to *smooth* DC residual currents and is required where the equipment downstream can introduce smooth DC into the supply — typically EV charge points (BS 7671:2018+A2:2022 §722.531.3.101) or transformerless single-phase PV inverters. Neither applies to this office fit-out, so Type B is not required and no `rcd_exception_citation` is documented.

The 6 A SSU circuit (C04) is itself an isolating transformer that breaks the protective conductor path to its secondary — but §411.3.3 still applies to the SSU **primary** connection (it is a "socket outlet" under BS 7671's definition), so the C04 MCB still sits under the 30 mA Type A RCD coverage. No exception is sought.

---

## 5. OCPD + Cable

OCPD selection follows the load profile of each circuit:

- **Curve B** for every circuit: office loads have no significant inrush (no large motors, no transformer banks, no discharge-lamp gear). Type B trips at 3-5 × In, giving the cleanest Zs disconnection margin per KS 1700:2018 §411.4.5 routing.
- **Breaking capacity ≥ 9 kA Icu**: declared PSCC at the busbar is 9 kA, so every MCB must meet that breaking capacity per the routing chain `KS 1700:2018 §434 → BS 7671:2018+A2:2022 §434.5.1 → IEC 60898-1`. The selected MCBs are 9 kA Icu products.

Cable sizing reasoning:

| Circuit | Cable | Rationale |
|---|---|---|
| C01 | 2.5 mm² T+E, ~18 m | 20 A radial covering 3 rooms; 2.5 mm² gives ~27 A current-carrying capacity in Reference Method 100/101 and adequate Zs margin at ~18 m total run. |
| C02 | 2.5 mm² T+E, ~14 m | 20 A radial covering 2 rooms; identical sizing logic to C01 at shorter length. |
| C03 | 2.5 mm² T+E, ~10 m | 20 A radial for kitchenette; 2.5 mm² covers worst-case coincident kettle+microwave+fridge ~8 A diversified within 20 A budget. |
| C04 | 1.5 mm² T+E, ~6 m | 6 A radial for SSU; 1.5 mm² is the minimum standard CSA and matches CPC sizing. |

All cables are copper, PVC-insulated (`PVC_70`), and assumed to follow Reference Method 100/101 (concealed in stud walls and ceiling void). The final route is delegated to the `cable-containment` skill via the intent contract.

The kitchenette FCU is recorded as a `switched_connection_unit_13A_BS_EN_60669` rather than a general 13 A socket — this is the correct treatment for a fixed-feed appliance (under-counter fridge): a switched fused connection unit gives local isolation and a 13 A BS 1362 fuse in the FCU sub-protects the fridge flex.

---

## 6. Diversity + Zs

**Diversity:** the IR records both `estimated_max_load_kw` (nameplate sum) and `diversified_max_load_a` (after applying diversity per KS 1700:2018 routing to BS 7671 + IET OSG Appendix A):

| Circuit | Nameplate (kW) | Diversified (A) | Logic |
|---|---|---|---|
| C01 | 1.8 | 5.5 | 3 rooms × 2 workstations + reception desk; assume only 60% concurrent active at 150 W per position + reception at 800 W coincident peak. |
| C02 | 1.0 | 3.5 | 2 rooms × 2 workstations; 50% concurrent at 150 W per position + minor task lighting. |
| C03 | 2.0 | 8.0 | Kitchenette: kettle 2 kW + microwave 0.8 kW + fridge 0.2 kW; assume kettle + microwave never coincident; worst-case ~1.8 kW at single-phase 240 V = 7.5 A; rounded to 8 A. |
| C04 | 0.1 | 0.4 | SSU primary current at typical 100 W secondary load. |

The downstream `db-layout` skill should consume the `diversified_max_load_a` values from `intent-out.json` to size the DB feeder.

**Zs verification** is deferred to the `calc.zs_loop_impedance` skill per work-item WI3 (the deferred-tool-call pattern in the small-power v1.0 spec). Every circuit therefore carries `tool_call_pending_for_zs_verification: true`, and the IR-level `flags[]` array contains `TOOL-CALL-PENDING:calc.zs_loop_impedance`. INV-08 (Zs deferral consistency) is satisfied: every circuit's pending flag aligns with the top-level flag.

The Zs ceiling per KS 1700:2018 §411.4.5 routing to BS 7671:2018+A2:2022 Table 41.3 for a 20 A Type B MCB with 0.4 s disconnection time, with the BS 7671 Cmin = 0.95 correction factor, is approximately:

```
Zs(max) ≤ (Cmin × U0) / (5 × In) = (0.95 × 240) / (5 × 20) = 2.28 Ω
```

For C04 at 6 A Type B: `Zs(max) ≤ (0.95 × 240) / (5 × 6) = 7.6 Ω`. The declared Ze of 0.45 Ω leaves ample margin for the (R1+R2) cable contribution at the radial lengths quoted — but the calc skill confirms the precise figure.

A second deferred tool call, `TOOL-CALL-PENDING:calc.diversity_factor`, lets the runtime re-derive `diversified_max_load_a` with a more rigorous method (e.g. IEC 60364-1 Annex B) if requested.

---

## 7. Compliance + Assumptions

`compliance_summary.compliant = true`. Three info-severity entries record design intent without flagging non-compliance:

1. **Toilet bathroom_zone_3 — SSU only.** Documented for clarity. KS 1700:2018 §701 routes to BS 7671:2018+A2:2022 Part 7-701; only the BS EN 61558-2-5 SSU is installed in the toilet, satisfying §701.512.3.
2. **Radial-only topology.** Although KS 1700:2018 §433 routes to BS 7671:2018+A2:2022 §433.1.5 permitting ring finals in KE, this design uses radials throughout per commercial engineering practice. Documented for downstream skills.
3. **Zs deferred to calc.** Per WI3, the loop-impedance check is the responsibility of the `calc.zs_loop_impedance` skill.

`compliance_summary.assumptions[]` records seven engineering assumptions:

- KPLC-declared Ze = 0.45 Ω at the DB earth terminal; not yet site-measured.
- KPLC-declared PSCC = 9.0 kA at DB-OFFICE-01 busbar; all MCBs selected with Icu ≥ 9 kA via the KS 1700:2018 §434 routing chain.
- All four circuits configured radial; ring finals permitted but not used at this scale.
- Diversity factors per KS 1700:2018 routing + IET OSG Appendix A.
- Toilet bathroom_zone_3 carries only the shaver SSU.
- Cable Reference Method 100/101 assumed; final route via `cable-containment` skill.
- Drafting follows BS 1192:2007+A2:2016 as the de facto KE design-industry convention; a future Kenyan drafting-standards layer will revisit (see the build-strategy memo on deferred standards sprints).

If any declared value (Ze, PSCC) fails verification on site, the design must be re-run with measured values and the Zs check repeated.

---

## 8. Drafting References

The drawing intent is a single A1 sheet at 1:50 metric scale, suitable for the 80 m² ground-floor plan plus a panel schedule and notes block. Layer naming follows **BS 1192:2007+A2:2016** (Discipline-Element-Modifier convention):

- `E-POW-OUTLET-GF` — ground-floor power outlets
- `E-POW-CIRCUIT-GF` — circuit identification annotations
- `E-POW-ZONE-BATH` — toilet Part 7-701 zone overlay
- `E-POW-DB-GF` — DB-OFFICE-01 schedule block

BS 1192:2007+A2:2016 is used here as the *de facto* convention for layered electrical drawings in the Kenyan design industry — most KE consulting practices have adopted UK CAD standards through training and professional history. The future Kenyan drafting-standards layer (see deferred-sprint memo `drafting-standards-deferred-sprint` of 2026-05-19) will revisit whether KS-equivalent drafting standards should be applied in place of (or in routing-from) BS 1192.

Drawing notes annotate:

1. Standard socket types (BS 1363 double 13 A switched, 300 mm AFFL for low-mount under-desk).
2. Kitchenette worktop sockets at 1100 mm AFFL with fridge FCU at 300 mm AFFL.
3. Toilet bathroom_zone_3 overlay with SSU-only annotation.
4. The BS 1192 layer scheme.

Downstream skills consuming this IR:

- **`db-layout`** consumes `intent-out.json` to size the DB-OFFICE-01 feeder and add the 4 final circuits to the board schedule (sum of `diversified_max_load_a` weighted by phase loading; here single-phase 240 V per circuit because the design assigns each radial to one phase of the TPN supply — phase balance to be confirmed by `db-layout`).
- **`cable-containment`** consumes the same intent to plan routes from `DB-OFFICE-01` to each room.
- **`schematic`** consumes the intent to draw the single-line schematic of the parent DB.

No upstream intent is consumed (`meta.consumed_intents: []`) because small-power is a leaf skill in v1.0.
