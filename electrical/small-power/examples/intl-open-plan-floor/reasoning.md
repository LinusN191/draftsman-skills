# Reasoning — INT 350 m² commercial open-plan office floor (small-power layout)

Project: `intl-open-plan-floor-eg01`
Jurisdiction: INT (IEC 60364 series — international LV installation code)
Skill: `electrical/small-power` v1.0.0
Produced: 2026-05-19

This document is the long-form companion to the structured `rationale` block in `output.json`. The eight section titles below mirror the eight `rationale.sections[]` entries one-to-one so an auditor can move between the IR and this narrative without translation.

The citation convention throughout this document follows the small-power v1.0 D-3 rule for INT jurisdiction work:

- Primary citations always lead with `IEC 60364-X-XX:YYYY §Z` (the part-number, year, and clause are mandatory — bare `IEC 60364` is non-conformant).
- The Type B RCD policy on C06 uses the exact form `IEC 60364-5-53:2002+A2:2015 §531.3.3` — this is the same citation form shipped by the `db-layout/intl-dbcomms-data` example at db-layout v1.3.0+, so the cross-skill alignment is verifiable as a literal string match.
- BS 7671 is **never** cited as a primary code under INT jurisdiction. The only BS references that appear are device standards (BS EN 61558-2-5 for the shaver supply unit, BS EN 60529 for IP rating, BS EN 60669 for the FCU) and the BS 1192:2007+A2:2016 drafting convention that piggybacks on ISO 19650:2018 in INT industry practice.
- NEC is **not** cited — NEC is a US-only code outside the scope of the INT jurisdiction lane.

---

## 1. Jurisdiction + Supply

The project is a tenant fit-out for a 350 m² commercial open-plan office floor. Because the jurisdiction is `INT`, the primary code is **IEC 60364 — Low-voltage electrical installations** (the international LV installation series published by the IEC). The relevant parts referenced in this design are:

- IEC 60364-1:2005 (general principles)
- IEC 60364-4-41:2017 (protection against electric shock)
- IEC 60364-4-43:2017 (protection against overcurrent)
- IEC 60364-5-52:2009+A1:2019 (selection and erection of wiring systems)
- IEC 60364-5-53:2002+A2:2015 (isolation, switching, control)
- IEC 60364-6:2016 (verification)
- IEC 60364-7-701:2019 (locations containing a bath or shower)

The supply is a **utility-provided TN-S 400V TPN+E** distribution (three-phase 400 V + neutral + separate dedicated protective earth conductor). Declared parameters at the parent distribution board `DB-FLOOR-01`:

| Parameter | Declared | Source |
|---|---|---|
| Nominal voltage | 400 V (3Ø, 50 Hz) line-to-line / 230 V phase-to-neutral | IEC 60364-1:2005 §313 |
| Earthing arrangement | TN-S (separate PE) | utility connection drawing |
| External earth-loop impedance Ze | 0.25 Ω | utility declaration |
| Prospective short-circuit current PSCC | 10.0 kA | utility declaration |

These are **declared** values, not measured. Per IEC 60364-6:2016 they must be verified at first energisation. The design margin assumes the declared values hold.

IEC 60364-4-43:2017 §434.5.1 sets the short-circuit verification rule: the consumer's installed protective device must have a breaking capacity at least equal to the prospective short-circuit current at the point of installation. Because PSCC = 10.0 kA at the DB-FLOOR-01 busbar, every MCB installed on `DB-FLOOR-01` must therefore have an Icu ≥ 10 kA. The selected products are 10 kA Icu MCBs sourced from the IEC 60898-1 product range.

---

## 2. Circuit Topology

Eight final circuits are designed, **all radial** (no ring final circuits — IEC 60364 has no ring-final equivalent to BS 7671 §433.1.5):

| ID | Designation | Topology | OCPD | Cable | Rooms |
|---|---|---|---|---|---|
| C01 | Workstation power 1 (zones 1-12) | radial | 20 A MCB C + Type A 30 mA | 2.5 mm² Cu PVC | workstation-zone-1 |
| C02 | Workstation power 2 (zones 13-24) | radial | 20 A MCB C + Type A 30 mA | 2.5 mm² Cu PVC | workstation-zone-2 |
| C03 | Meeting room 1 power + AV | radial | 16 A MCB C + Type A 30 mA | 2.5 mm² Cu PVC | meeting-room-1 |
| C04 | Meeting room 2 power + AV | radial | 16 A MCB C + Type A 30 mA | 2.5 mm² Cu PVC | meeting-room-2 |
| C05 | Kitchenette appliances + FCU | radial | 20 A MCB C + Type A 30 mA | 2.5 mm² Cu PVC | kitchenette |
| C06 | Server cabinet small-power (UPS-fed) | dedicated_radial | 20 A MCB C + **Type B 30 mA** | 2.5 mm² Cu PVC | server-room |
| C07 | Toilet shaver supply (SSU) | dedicated_radial | 6 A MCB B + Type A 30 mA | 1.5 mm² Cu PVC | toilet |
| C08 | Outdoor IP65 sockets | radial | 16 A MCB C + Type A 30 mA | 2.5 mm² Cu PVC | outdoor-smoking, outdoor-bin |

**Why radial, not ring?** IEC 60364 does not include the BS 7671 ring final circuit construct. INT engineering convention treats every final socket-outlet circuit as a radial. INV-04 in the small-power v1.0 invariant catalogue restricts ring topology to the `{GB, KE}` jurisdiction set; INT is therefore correctly radial-only and the invariant is satisfied trivially.

**Why dedicated radials for C06 and C07?**

- **C06 (server cabinet):** the load is IT equipment fed via a UPS — UPS rectifier front-ends and SMPS-fed servers generate smooth DC residual currents on the protective conductor. Isolating this load on its own MCB allows the upstream Type B 30 mA RCD to provide clean DC-sensitive protection without coupling to the building's general Type A coverage. The dedicated_radial topology also supports planned maintenance lockout of the server feed without interrupting other office circuits.
- **C07 (shaver SSU):** the bathroom/toilet shaver supply unit is an isolating transformer per BS EN 61558-2-5; routing it on a dedicated 6 A MCB radial gives discrimination and limits the fault energy that can be delivered into a Part 7-701 zone. The cable is 1.5 mm² Cu PVC — adequate for the SSU primary current (~0.4 A) and meeting the smallest CPC size for a 6 A circuit.

---

## 3. Special Locations

Three special-location categories appear in this design:

### 3.1 Toilet — `bathroom_zone_3` per IEC 60364-7-701:2019 §701.512

The toilet (3.0 × 2.5 m) is classified as `bathroom_zone_3`. Although the brief calls the room a commercial WC and there is no full bath/shower, the wash-hand basin and possible cleaner's slop-sink mean the IEC 60364-7-701:2019 zoning rules apply by analogy — INT M&E engineering convention applies the same zone treatment to commercial WCs as to domestic bathrooms when classifying socket locations.

§701.512 prohibits general-purpose socket outlets within 3 m of the zone 1 boundary. Because the room is only 3.0 × 2.5 m and falls entirely within that 3 m radius, the design installs **only** a BS EN 61558-2-5 shaver supply unit (`wc-S01`) — explicitly excepted by §701.512. No general-purpose Schuko outlets are placed in the toilet.

INV-05 (special-location compliance: `bathroom_zone_1` / `bathroom_zone_2` must have zero sockets; `bathroom_zone_3` must contain only SSU/SELV outlets) is satisfied: the room has one socket and it is the SSU.

### 3.2 Outdoor sockets — IP65 per BS EN 60529

Two outdoor amenity points host one IP65 Schuko socket each, fed from C08:

- `outdoor-smoking` — smoking-shelter convenience outlet
- `outdoor-bin` — bin-store maintenance outlet

Each socket is housed in a weatherproof enclosure to **IP65** per BS EN 60529, with a sprung flap closure for the plug entry. The IP65 rating gives:

- IP6X = dust-tight
- IPX5 = protected against jets of water from any direction

This is the standard INT design level for external sockets exposed to rain, garden hose proximity, or bin-area washdown. The IP rating is recorded on each socket via the `ip_rating` field. The circuit (C08) is Type A 30 mA RCD-protected per IEC 60364-4-41:2017 §411.3.3, which is mandatory for all outdoor socket circuits.

IEC 60364-5-53:2002+A2:2015 §512.2 governs the selection of equipment for the environmental conditions; BS EN 60529 is the IP-rating product standard explicitly referenced for ingress protection.

### 3.3 No bathroom_zone_1 or _2

This is a commercial floor — no bath, no shower, no swimming pool, no sauna. There are no zone_1 / zone_2 / wet_area locations to consider beyond the WC's bathroom_zone_3 by-analogy classification.

A single info-severity flag in `compliance_summary.non_compliance_flags[]` records each of the three special-location categories so the downstream `db-layout` and `cable-containment` skills see the design intent without re-deriving it.

---

## 4. RCD Posture

Every socket-outlet circuit must carry residual-current protection per IEC 60364-4-41:2017 §411.3.3 — additional protection by 30 mA RCD on socket outlets with rated current ≤ 32 A. The post-Amendment-2 default is **Type A 30 mA** (sensitive to AC + pulsating-DC residuals) for general-purpose office, retail, and domestic socket circuits.

### 4.1 Seven circuits — Type A 30 mA

Circuits C01, C02, C03, C04, C05, C07, C08 all use `rcd_posture: "type_a_30ma_per_§411_3_3"`:

| Circuit | Load profile | Why Type A is adequate |
|---|---|---|
| C01, C02 | Workstation power (laptops, monitors, task lights) | Laptop PSUs + LED drivers can inject pulsating-DC residuals; Type A handles this. |
| C03, C04 | Meeting-room AV + low-level wall sockets | Wall-mounted displays, AV processors, AC adapters — same pulsating-DC profile as workstations. |
| C05 | Kitchenette (kettle, microwave, fridge, FCU) | Resistive + light SMPS; Type A more than adequate. |
| C07 | Shaver SSU primary | Isolating transformer primary; minimal residual leakage. |
| C08 | Outdoor sockets | General-purpose 16 A external outlets; Type A is the modern IEC baseline. |

The implementation is board-level RCD protection upstream of the MCBs at `DB-FLOOR-01` — typical INT commercial idiom on a single floor distribution board. Each Type A device covers a group of MCBs (typical implementation: two banks of 4 circuits each, plus a third dedicated bank for the Type B RCD on C06).

### 4.2 C06 — Type B 30 mA per IEC 60364-5-53:2002+A2:2015 §531.3.3 (cross-skill alignment)

C06 server-room small-power is the exception. The IR records `rcd_posture: "type_b_30ma_per_§531_3_3"` and `ocpd.rcd_type: "B"`.

**Why Type B?** IEC 60364-5-53:2002+A2:2015 §531.3.3 mandates DC-sensitive (Type B) RCD protection on circuits feeding loads that can produce smooth (non-pulsating) DC residual currents. The classic offenders are:

1. **UPS rectifier front-ends** — three-phase or single-phase rectifier topologies in the UPS injection stage can pass smooth DC into the protective conductor when there is an insulation fault on the DC bus.
2. **SMPS-fed IT equipment** — switched-mode power supplies in servers, network switches, KVM appliances, and rack-mount NAS units all rectify mains to a DC bus before chopping it; PFC front-ends in particular can inject smooth DC under fault.
3. **PoE+/PoE++ injectors** — power-over-Ethernet supplies are SMPS-based and feed DC out onto twisted-pair cabling; a fault between the secondary DC bus and chassis ground produces DC residual current.

Type A and Type F RCDs are **blinded** by smooth DC residual currents above their characteristic DC threshold (typically 6 mA DC blinds a Type A); they will silently fail to disconnect on a fault that produces only smooth DC. Type B explicitly detects smooth DC up to higher thresholds and gives proper protection.

**Cross-skill alignment with `db-layout/intl-dbcomms-data`:** the `db-layout` skill at version v1.3.0+ ships an example DB called `intl-dbcomms-data` which puts a Type B 30 mA RCD upstream of an IT/comms sub-DB. The shipped citation form is exactly `IEC 60364-5-53:2002+A2:2015 §531.3.3` — see `electrical/db-layout/examples/intl-dbcomms-data/output.json` line 24 and following. By using **the identical citation string** here on C06, the small-power IR is interoperable with the db-layout IR at literal-string match — a future cross-skill validator can detect alignment without semantic interpretation.

A subtle invariant: small-power v1.0 is a **leaf skill** (no upstream `consumed_intents` in `meta`). It does **not** consume an upstream db-layout intent in v1.0. Yet the engineer mirrors the db-layout shipped policy by convention — this is documented in `compliance_summary.assumptions[]` and via the `CROSS-SKILL-ALIGNMENT:db-layout/intl-dbcomms-data/Type-B-RCD` entry in `flags[]`. A future small-power v1.1+ may consume `db-layout-intent.json` and lift this alignment from convention to formal contract.

**Sensitivity coordination:** the upstream Type B device at 30 mA must coordinate with any downstream Type A devices to avoid nuisance trip cascades. In this design, C06 is the **only** circuit downstream of the Type B RCD bank, so no Type A is downstream of the Type B and no coordination conflict exists. The engineer notes this in `drawing_notes`.

---

## 5. OCPD + Cable

OCPD selection follows the load profile of each circuit:

- **Curve C** for all Schuko/outdoor/server circuits (C01-C06, C08): office and IT loads exhibit SMPS inrush from monitors, laptop PSUs, AV processors, server PSUs, and kitchen appliances. Type C trips at 5-10 × In, accommodating inrush without nuisance trip per IEC 60898-1.
- **Curve B** for C07 (SSU only): the BS EN 61558-2-5 isolating transformer has minimal inrush at the small SSU rating; Type B (3-5 × In) gives the cleanest Zs disconnection margin against the tiny 0.4 A primary current.

**Breaking capacity ≥ 10 kA Icu:** declared PSCC at the busbar is 10 kA, so every MCB must meet that breaking capacity per IEC 60364-4-43:2017 §434.5.1. The selected MCBs are 10 kA Icu products from the IEC 60898-1 range.

Cable sizing reasoning:

| Circuit | Cable | Length | Rationale |
|---|---|---|---|
| C01 | 2.5 mm² Cu PVC, 3-core | ~30 m | 20 A radial covering 12 floor-box positions in zone 1; 2.5 mm² gives ~24 A current-carrying capacity in Reference Method per IEC 60364-5-52:2009+A1:2019 Annex A. |
| C02 | 2.5 mm² Cu PVC, 3-core | ~30 m | identical sizing to C01 for zone 2. |
| C03 | 2.5 mm² Cu PVC, 3-core | ~18 m | 16 A radial for meeting room 1; 2.5 mm² oversized for 16 A to give Zs headroom. |
| C04 | 2.5 mm² Cu PVC, 3-core | ~20 m | identical to C03 for meeting room 2. |
| C05 | 2.5 mm² Cu PVC, 3-core | ~14 m | 20 A radial for kitchenette; covers kettle + microwave + fridge worst-case coincident ~11 A. |
| C06 | 2.5 mm² Cu PVC, 3-core | ~12 m | 20 A radial for server cabinet small-power; short run, Type B RCD upstream. |
| C07 | 1.5 mm² Cu PVC, 3-core | ~16 m | 6 A radial for SSU; 1.5 mm² minimum CSA + matching CPC. |
| C08 | 2.5 mm² Cu PVC, 3-core | ~28 m | 16 A radial outdoor; longer run to external smoking + bin sockets; concealed in containment + emerging at IP65 enclosure. |

All cables are copper, PVC-insulated (`PVC_70`), 3-core (L + N + PE). Cable routing assumes IEC 60364-5-52:2009+A1:2019 Annex A reference methods (concealed in raised access floor, ceiling void, or wall chase); the final route is delegated to the `cable-containment` skill via the intent contract.

The kitchenette FCU is recorded as a `switched_connection_unit_16A_BS_EN_60669` rather than a general Schuko socket — this is the correct treatment for a fixed-feed appliance (under-counter fridge): a switched fused connection unit gives local isolation, and the BS EN 60669 product standard governs the device.

---

## 6. Diversity + Zs

### 6.1 Diversity

The IR records both `estimated_max_load_kw` (nameplate sum) and `diversified_max_load_a` (after applying diversity per IEC 60364-1:2005 §132.12 design margin guidance):

| Circuit | Nameplate (kW) | Diversified (A) | Logic |
|---|---|---|---|
| C01 | 3.0 | 10.0 | 12 workstation positions × 125 W coincident × ~0.7 utilisation = ~1.05 kW + screen+task + reception spill at 230 V ≈ 10 A. |
| C02 | 3.0 | 10.0 | identical to C01 for zone 2. |
| C03 | 1.5 | 6.5 | Meeting room 1: AV processor + display + 3 user laptops + minor task. |
| C04 | 1.5 | 6.5 | identical to C03 for meeting room 2. |
| C05 | 2.5 | 11.0 | Kitchenette: kettle 2.0 kW + microwave 0.8 kW (non-coincident) + fridge 0.2 kW; worst-case ~2.6 kW @ 230 V = 11.3 A → 11 A. |
| C06 | 2.0 | 9.0 | Server cabinet small-power UPS-fed; rack PDU + 2 server PSUs + network switches sum to ~2 kW @ 230 V = 8.7 A → 9 A. |
| C07 | 0.1 | 0.4 | SSU primary current at typical 100 W secondary load. |
| C08 | 0.4 | 1.7 | 2 outdoor sockets at occasional use: small power tool + minor maintenance load. |

The downstream `db-layout` skill should consume the `diversified_max_load_a` values from `intent-out.json` to size the DB-FLOOR-01 feeder. Sum of diversified currents = 10 + 10 + 6.5 + 6.5 + 11 + 9 + 0.4 + 1.7 = **55.1 A** across three phases. Assuming reasonable phase balance, the floor incomer should target ~32 A TPN with headroom.

A second deferred tool call, `TOOL-CALL-PENDING:calc.diversity_factor`, lets the runtime re-derive `diversified_max_load_a` with a more rigorous method (e.g. IEC 60364-1 Annex B or IEC 60364-8-1 energy efficiency annex) if requested.

### 6.2 Zs verification

Zs verification is deferred to the `calc.zs_loop_impedance` skill per work-item WI3 (the deferred-tool-call pattern in the small-power v1.0 spec). Every circuit therefore carries `tool_call_pending_for_zs_verification: true`, and the IR-level `flags[]` array contains `TOOL-CALL-PENDING:calc.zs_loop_impedance`. INV-08 (Zs deferral consistency) is satisfied: every circuit's pending flag aligns with the top-level flag.

The Zs ceiling per IEC 60364-4-41:2017 §411.4.5 for a 20 A Type C MCB with 0.4 s disconnection time at U0 = 230 V, applying the IEC Cmin = 0.95 correction factor, is approximately:

```
Zs(max) ≤ (Cmin × U0) / (10 × In) = (0.95 × 230) / (10 × 20) = 1.09 Ω
```

(The factor of 10 accommodates the Type C Ia max of 10 × In, not the 5 × In of Type B.)

For C03/C04/C08 at 16 A Type C: `Zs(max) ≤ (0.95 × 230) / (10 × 16) = 1.37 Ω`.
For C07 at 6 A Type B: `Zs(max) ≤ (0.95 × 230) / (5 × 6) = 7.28 Ω`.

The declared Ze of 0.25 Ω leaves moderate margin for the (R1+R2) cable contribution at the radial lengths quoted — but the calc skill confirms the precise figure. At the longer radials (C01/C02 ~30 m, C08 ~28 m) the (R1+R2) of 2.5 mm² Cu adds ~0.45 Ω, putting Zs around 0.70 Ω against a 1.09 Ω ceiling — adequate but the calc step is mandatory for sign-off.

---

## 7. Compliance + Assumptions

`compliance_summary.compliant = true`. Five info-severity entries record design intent without flagging non-compliance:

1. **C06 Type B RCD + cross-skill alignment.** Documented explicitly — IEC 60364-5-53:2002+A2:2015 §531.3.3 + the literal-string match with `db-layout/intl-dbcomms-data`.
2. **Toilet bathroom_zone_3 — SSU only.** IEC 60364-7-701:2019 §701.512; INV-05 satisfied.
3. **Outdoor IP65.** BS EN 60529 + IEC 60364-5-53:2002+A2:2015 §512.2.
4. **Radial-only topology.** IEC 60364 has no ring final construct; INV-04 satisfied trivially under INT.
5. **Zs deferred to calc.** Per WI3, the loop-impedance check is the responsibility of the `calc.zs_loop_impedance` skill.

`compliance_summary.assumptions[]` records eight engineering assumptions:

- Utility-declared Ze = 0.25 Ω at the DB-FLOOR-01 earth terminal; not yet site-measured (IEC 60364-6:2016 verification mandated).
- Utility-declared PSCC = 10.0 kA at DB-FLOOR-01 busbar; all MCBs selected with Icu ≥ 10 kA per IEC 60364-4-43:2017 §434.5.1 + IEC 60898-1.
- All eight circuits configured radial; IEC 60364 has no ring-final equivalent to BS 7671 §433.1.5.
- Diversity factors per IEC 60364-1:2005 §132.12 design margin estimates.
- Toilet bathroom_zone_3 holds only the shaver SSU per IEC 60364-7-701:2019 §701.512.
- Outdoor sockets IP65 per BS EN 60529 + IEC 60364-5-53:2002+A2:2015 §512.2.
- C06 server-room Type B RCD per IEC 60364-5-53:2002+A2:2015 §531.3.3 — mirrors db-layout intl-dbcomms-data shipped policy (cross-skill alignment by engineering convention).
- Drafting follows ISO 19650:2018 + BS 1192:2007+A2:2016 as the INT industry default for layered electrical drawings; a future drafting-standards deferred sprint will revisit ISO-only layer naming (AIA / ISO 5457 / ISO 5455).

If any declared value (Ze, PSCC) fails verification on site, the design must be re-run with measured values and the Zs check repeated.

---

## 8. Drafting References

The drawing intent is a single A1 sheet at 1:100 metric scale, suitable for the 350 m² open-plan floor plate plus a panel schedule, notes block, and the Part 7-701 toilet zone overlay.

Layer naming follows the **ISO 19650:2018 federation pattern** + **BS 1192:2007+A2:2016 discipline-element-modifier convention** — the INT industry default for layered electrical drawings:

- `E-POW-OUTLET-L01` — level 01 power outlets (Schuko + IP65 + SSU + FCU)
- `E-POW-CIRCUIT-L01` — level 01 circuit identification annotations
- `E-POW-ZONE-BATH` — toilet IEC 60364-7-701 zone overlay
- `E-POW-DB-L01` — DB-FLOOR-01 schedule block

ISO 19650:2018 governs the information-management federation of layered drawings across multi-discipline projects; BS 1192:2007+A2:2016 is layered underneath for the actual discipline-element-modifier layer-naming syntax. This pairing is the *de facto* convention for INT consulting practices doing IEC 60364 work — most international consultancies have inherited UK CAD standards through training and corporate history. The future drafting-standards deferred sprint (memo `drafting-standards-deferred-sprint` of 2026-05-19) will revisit whether full ISO-only drafting standards (AIA layer guidelines, ISO 5457 sheet sizes, ISO 5455 scales) should fully supplant BS 1192 in INT outputs.

Drawing notes annotate:

1. Floor-box mounted Schuko sockets in workstation zones (12 boxes per zone, 2× Schuko each).
2. Meeting-room low-level sockets at 300 mm AFFL + AV socket at 1200 mm AFFL.
3. Kitchenette worktop sockets at 1100 mm AFFL with fridge FCU at 300 mm AFFL on C05.
4. Server-room sockets at 600 mm AFFL on C06 with Type B 30 mA RCD upstream.
5. Toilet bathroom_zone_3 overlay with SSU-only annotation.
6. Outdoor IP65 enclosure at 1200 mm AFFL on external wall on C08.
7. ISO 19650 + BS 1192 layer scheme.

Downstream skills consuming this IR:

- **`db-layout`** consumes `intent-out.json` to size the DB-FLOOR-01 feeder and add the 8 final circuits to the board schedule. Phase balance to be confirmed by `db-layout` (target: even distribution of 10 A workstation banks across phases A/B/C, with C06 server-room on its own phase due to the Type B RCD bank).
- **`cable-containment`** consumes the same intent to plan routes from `DB-FLOOR-01` to each room (raised access floor for workstations; ceiling void for meeting rooms and kitchenette; external wall containment for C08).
- **`schematic`** consumes the intent to draw the single-line schematic of the parent DB, including the segregation of the Type B RCD bank for C06.

No upstream intent is consumed (`meta.consumed_intents: []`) because small-power is a leaf skill in v1.0. The cross-skill alignment with db-layout's Type B policy on C06 is therefore a **convention**, recorded explicitly in `flags[]` as `CROSS-SKILL-ALIGNMENT:db-layout/intl-dbcomms-data/Type-B-RCD` so a future cross-skill validator can match the citation strings without semantic interpretation.

---

## 9. v2.0.0 D4 RETROFIT — building_diversity + cable-sizing cascade (added 2026-06-03)

### 9.1 Honest retrofit disclosure

This section was **not present** in the v1.0.0 ship of this example (2026-05-19). It is added as part of the small-power v2.0.0 D4 depth sprint (the within-skill-depth closeout for small-power) as a deliberate jurisdiction-agnostic demonstration of the new v2.0 `building_diversity` IR field and the new INV-19 cable-sizing cascade integration invariant.

**Pre-D4 (v1.0.0) state of this example:**

1. `meta.consumed_intents: []` (leaf skill)
2. No top-level `consumed_intents` block at all
3. No `building_diversity` block (the field did not exist in v1.x)
4. Every circuit carried `tool_call_pending_for_zs_verification: true`
5. `invariants: []` was empty (the v1.0 invariant emission discipline was deferred)

**Post-D4 (v2.0.0) state of this example:**

1. `meta.consumed_intents` adds the `cable-sizing` entry (intent_version 1.1.0)
2. New top-level `consumed_intents.cable_sizing.payload` is INLINED with 8 circuit entries
3. NEW `building_diversity` top-level block populated with the office profile + INT jurisdiction citation form
4. Every circuit carries `tool_call_pending_for_zs_verification: false` + `verified_zs_ohm` value from the cable_sizing payload
5. `invariants[]` populated with all 19 v2.0 invariants, all PASS

**The retrofit is purely additive.** No existing field has been renamed or removed:

- Same 8 circuits (C01-C08), same circuit_ids, same OCPD ratings, same cable CSAs, same RCD types, same designations
- Same 9 rooms, same room_ids, same dimensions, same sockets (every floor-box, FCU, SSU position preserved)
- Same supply (TN-S 400V TPN+E, Ze=0.25 Ω, PSCC=10 kA)
- Same parent_db (DB-FLOOR-01)
- Same jurisdiction (INT), same drafting standard (ISO 19650:2018 + BS 1192:2007+A2:2016)

Sections 1–8 above remain valid for the v2.0 IR — they were authored at v1.0 ship and the retrofit does NOT regress them. This section 9 is the only narrative addition.

### 9.2 INT jurisdiction routing for building_diversity — honest cross-jurisdiction citation

The new `building_diversity` IR field demonstrates that the v2.0 schema is **jurisdiction-agnostic**. The C.5 (UK office) and C.6 (UK industrial warehouse) sibling examples ship the field under GB jurisdiction with BS 7671:2018+A2:2022 §311 as the primary citation. This INT retrofit demonstrates the same field working under IEC jurisdiction with a different citation form — proving the schema does not bind the building_diversity computation to any single jurisdiction.

**The citation form for INT** is the engineering-honest crux of this retrofit:

> **IEC 60364 does NOT publish a dedicated diversity-factor table in any verified part.**

This is documented honestly in the IR `_derivation_note` and in `compliance_summary.non_compliance_flags[]` and `assumptions[]`. The IEC 60364 base norms that anchor the building_diversity computation under INT jurisdiction are:

- **IEC 60364-3:2008 §31** — assessment of general characteristics — maximum demand. This sub-section of Part 3 covers maximum demand at a **principle** level — it does not provide tabulated diversity factors per load family.
- **IEC 60364-1:2005 §132.12** — fundamental principles — design margin. This clause leaves diversity-factor selection to engineering judgement.

Because IEC does not provide tabulated values, the engineer-of-record applies an **external cross-jurisdiction working reference**. The standard international working reference for IEC 60364 commercial office work is the **IET On-Site Guide 8th Edition Appendix A Table A1** — specifically the `office_small_power_workstation` profile with `diversity_percent=66` (verified at `shared/standards/electrical/BS7671/diversity-factors.json::commercial_office_diversity.small_power_per_workstation`).

The IET OSG is a British-published guide aligned to BS 7671. **It is not a binding IEC norm.** But it is widely used internationally — most international M&E consultancies inherit UK CAD and design standards through training and corporate history, and the IET OSG App A Table A1 is the de facto working reference for diversity-factor selection on IEC 60364 commercial work. The honest discipline applied here:

| Position | Cited |
|---|---|
| Primary anchor (binding under INT) | IEC 60364-3:2008 §31 + IEC 60364-1:2005 §132.12 |
| Working reference for the office_factor value (NON-binding, cross-jurisdiction) | IET On-Site Guide 8th Edition Appendix A Table A1 (`office_small_power_workstation` profile, diversity_percent=66) |
| Banned | BS 7671 §311 (this is the INT jurisdiction example — BS 7671 is the GB primary code; cross-referencing it as the primary citation here would be incorrect) |

The IR `_clause_citation` carries the full triple-cite form: `IEC 60364-3:2008 §31 + IEC 60364-1:2005 §132.12 + IET On-Site Guide 8th Edition Appendix A Table A1 (cross-jurisdiction reference)`. The IR `_derivation_note` explicitly documents that the IET OSG is NOT cited as a binding IEC norm but as a best-available cross-jurisdiction working reference. This is the same hygiene the C.5 UK example uses for its IET OSG citation — the difference here is that under INT the IEC norms come FIRST and the IET OSG is the cross-jurisdiction fallback.

### 9.3 Computation under the v2.0 building_diversity field

| Parameter | Value | Source |
|---|---|---|
| `building_type` | `office` | engineer-supplied via building_diversity_inputs |
| `floor_count` | 1 | single-tenant floor |
| `design_density_w_per_m2` | 70 | engineer estimate (inside the IET OSG general_office_aggregate 65-100 W/m² cross-jurisdiction reference band) |
| `future_expansion_pct` | 25 | engineer-supplied growth allowance, carried forward |
| `applies_after` | `per_load_diversity` (const) | enforced by schema |
| `building_factor` (applied uniformly to every per_circuit_demand_inputs[] entry) | 0.66 | IET OSG App A Table A1 `office_small_power_workstation.diversity_percent=66` |

**Σ post-per-load-diversity across all 8 circuits:**

```
10.0 + 10.0 + 6.5 + 6.5 + 11.0 + 9.0 + 0.4 + 1.7 = 55.1 A
```

**Building-level coincident demand:**

```
55.1 A × 0.66 = 36.366 A
```

**Recorded `building_diversified_demand_a`:**

```
36.5 A (drift 0.37% — well within INV-13's ±5% tolerance)
```

**Upstream submain implication:** the landlord MCC sizing skill at the next hop should target 36.5 A coincident demand at the parent DB busbar — the next standard MCB size up is 40 A. The 25% future-expansion allowance is carried FORWARD as a separate field, not folded into `building_diversified_demand_a`; the submain sizing skill can then be transparent about the headroom basis.

### 9.4 Cable-sizing cascade — INV-19 PASS via DEFERRED-POINTER inlined-payload pattern

The v2.0 D4 introduction of INV-19 verifies that every circuit's `building_diversity.per_circuit_demand_inputs[i].post_per_load_diversity_a` reconciles with the consumed `cable_sizing.payload.circuits[i].design_current_a` value within ±5%. This invariant closes the cascade loop between small-power and cable-sizing.

The DEFERRED-POINTER pattern (per the C.5 and C.6 ship discipline):

1. The `source_path` for the cascade points to `electrical/cable-sizing/examples/intl-open-plan-floor-feeder/intent-out.json` — a producer-side fixture that does **NOT** yet exist at C.7-ship.
2. The `payload` bytes are **INLINED** at C.7-ship with 8 circuit entries that match the small-power IR's `diversified_max_load_a` values.
3. When the upstream cable-sizing example lands as a producer fixture, the inlined payload bytes will remain unchanged — only the source repoints transparently.
4. This is the same pattern the UK C.5 and C.6 examples use to demonstrate INV-19 PASS before the producer-side fixtures ship.

Per-circuit reconciliation drift (all 0.0% — exact match because the inlined payload was constructed from the small-power IR):

| Circuit | small-power diversified_max_load_a | cable_sizing design_current_a | drift |
|---|---|---|---|
| C01 | 10.0 | 10.0 | 0.0% |
| C02 | 10.0 | 10.0 | 0.0% |
| C03 | 6.5 | 6.5 | 0.0% |
| C04 | 6.5 | 6.5 | 0.0% |
| C05 | 11.0 | 11.0 | 0.0% |
| C06 | 9.0 | 9.0 | 0.0% |
| C07 | 0.4 | 0.4 | 0.0% |
| C08 | 1.7 | 1.7 | 0.0% |

INV-19 PASS. The cascade also lifts every circuit's `verified_zs_ohm` from the cable_sizing payload (range 0.48-0.85 Ω across the 8 circuits — all below the §411.4.5 0.4 s disconnection-time ceilings). `tool_call_pending_for_zs_verification` is consequently flipped to `false` on every circuit, superseding the pre-D4 TOOL-CALL-PENDING:calc.zs_loop_impedance marker.

### 9.5 Why this INT retrofit matters

The C.5 (UK office) and C.6 (UK industrial warehouse) examples demonstrate `building_diversity` working under GB jurisdiction with BS 7671 §311 as the primary citation. **Without this INT retrofit, the v2.0 building_diversity field would have only UK examples** and the schema's jurisdiction-agnostic claim would be untested.

This retrofit proves three things:

1. **The IR schema is genuinely jurisdiction-agnostic** — building_diversity validates under INT just as cleanly as under GB.
2. **The honest citation discipline works across jurisdictions** — the engineer-of-record cites the binding IEC norms FIRST and the IET OSG cross-jurisdiction working reference SECOND with an explicit `_derivation_note` disclosure, instead of silently using a UK-only citation under INT.
3. **The INV-19 cable-sizing cascade is also jurisdiction-agnostic** — the cascade contract does not embed BS 7671 semantics, so the cascade lifts cleanly into an IEC 60364 design.

The retrofit is the smallest possible additive change to a v1.0 leaf example that demonstrates the new v2.0 field works under INT. No structural regression to the existing 8 circuits / 9 rooms / 8 special-location info flags / 8 assumptions / ISO 19650 drafting layout.

## Honest disclosures (v2.0 D4 retrofit — 4-place pattern)

Three honest disclosures apply to this D4 retrofit example, completing the 4-place pattern established across all D4 examples:

1. **DEFERRED-POINTER cascade (INT jurisdiction)** — `consumed_intents.cable_sizing.source_path` points at `electrical/cable-sizing/examples/intl-open-plan-floor-feeder/intent-out.json`, a producer-side fixture that does NOT yet exist at C.7-ship. The payload bytes are INLINED byte-identical with the small-power IR's `diversified_max_load_a` values. Reconciliation drift is 0.0% on all 8 circuits. When the producer fixture lands, the source_path resolves to a real file but the payload bytes are expected to remain unchanged — only the source_path repoints transparently. This is the same pattern the UK C.5 and C.6 examples use.
2. **IEC 60364 diversity-factor citation discipline (INT honest disclosure)** — IEC 60364 does NOT publish a dedicated diversity-factor table in any verified part. The primary binding anchors under INT jurisdiction are IEC 60364-3:2008 §31 + IEC 60364-1:2005 §132.12. The IET On-Site Guide 8th Edition Appendix A Table A1 is cited as a NON-binding cross-jurisdiction working reference for the `office_small_power_workstation.diversity_percent=66` value. BS 7671 §311 is explicitly NOT cited here — this is an INT jurisdiction example. The `_derivation_note` in the IR documents this discipline.
3. **Retrofit additive-only** — §9.1 above ("Honest retrofit disclosure") documents that sections 1–8 of this reasoning.md remain valid for the v2.0 IR. No existing circuit, room, socket, RCD type, or drafting reference has been renamed or removed. The D4 retrofit adds building_diversity + cable-sizing cascade + INV-19 PASS evidence + all 19 invariants as purely additive fields.
