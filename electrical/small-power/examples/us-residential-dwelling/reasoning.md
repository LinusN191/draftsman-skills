# Reasoning — US Residential Dwelling (Single-Family, NEC 2023)

Project: `us-residential-dwelling-eg01`
Jurisdiction: US
Skill: `electrical/small-power` v1.0.0

This narrative walks the engineering decisions behind the IR output. Eight sections in fixed order, matching `output.json` → `rationale.sections[]`. All standards citations use the NEC 2023 / NFPA 70 form (`NEC 2023 Article XYZ`); BS 7671 and IEC 60364 are deliberately absent from the design narrative because the AHJ is United States.

---

## 1. Jurisdiction + Supply

**US — NEC 2023 (NFPA 70).** This is a single-family detached dwelling, ~160 m² (1700 ft²), single-story slab-on-grade, with a 200 A residential panelboard `MAIN-PANEL` at the service entrance.

**Supply:** 120/240 V split-phase TN-C-S. The utility transformer is a center-tapped single-phase distribution transformer; the center tap is the grounded conductor (neutral). At the service disconnect, the main bonding jumper bonds the grounded conductor to the equipment grounding system per NEC 2023 Article 250.24(B). All downstream branch circuits use a separate equipment grounding conductor (EGC) — so the system is functionally TN-S downstream of the bond, even though the supply between transformer and service is combined N+PE in the schema sense.

| Parameter | Value | Source |
|---|---|---|
| Service voltage (line-to-line) | 240 V | Utility |
| Service voltage (line-to-neutral) | 120 V | Utility |
| Earth-fault loop impedance Ze | 0.25 Ω | Utility-declared |
| Prospective short-circuit current PSCC | 10.0 kA | Utility-declared at MAIN-PANEL busbar |
| System type (schema enum) | TN-C-S | Closest analogue (see notes below) |
| Phase arrangement | single_phase_split | NEC 2023 Article 230 |
| Service disconnect / panelboard | 200 A, MAIN-PANEL | NEC 230.79 |

**Schema note on system_type:** The schema enum exposes `TN-S`, `TN-C-S`, `TT`. US split-phase service is conventionally described as "service-entrance ground/neutral combined" upstream and separated downstream — the closest analogue is `TN-C-S` (combined upstream, separated at the consumer's neutral-ground bond). Documented as info-level mapping in `compliance_summary.assumptions[]`.

**OCPD interrupting rating (AIC):** NEC 2023 Article 110.9 requires every overcurrent device to have an interrupting rating ≥ the available fault current at its line terminals. PSCC=10 kA → every branch breaker selected with 10 kA AIC per UL 489. The AFCI / GFCI / dual-function product range from major US manufacturers is available at 10 kA AIC.

---

## 2. Circuit Topology

All 8 branch circuits are **radial**. The US NEC has no ring-final-circuit construct — `INV-04` (ring topology restricted to GB and KE) is satisfied trivially.

| Circuit | Topology | Rating | Purpose | NEC clause |
|---|---|---|---|---|
| C01 | radial | 20 A | Kitchen small appliance branch 1 | 210.52(B)(1) |
| C02 | radial | 20 A | Kitchen small appliance branch 2 | 210.52(B)(1) |
| C03 | radial | 15 A | General receptacles — living + bedrooms + hallway | 210.12(A) |
| C04 | dedicated_radial | 20 A | Bathroom GFCI | 210.8(A)(1) + 210.11(C)(3) |
| C05 | radial | 20 A | Garage GFCI | 210.8(A)(2) |
| C06 | radial | 20 A | Outdoor GFCI | 210.8(A)(3) |
| C07 | radial | 20 A | Basement GFCI | 210.8(A)(5) |
| C08 | dedicated_radial | 20 A | Laundry dedicated | 210.11(C)(2) + 210.8(A)(10) |

**Kitchen small-appliance branches (C01/C02):** NEC 2023 Article 210.52(B)(1) requires *at least two* 20 A small-appliance branch circuits to serve receptacles in the kitchen, pantry, breakfast room, and dining area. This design provides exactly two, with countertop receptacles split evenly (3 per branch).

**General-receptacle branch (C03):** Living room, two bedrooms, and the hallway are served by a single 15 A AFCI branch. This is the standard residential general-purpose branch — there is no per-room load study; the AFCI protection covers arcing-fault risk in walls and behind furniture per NEC 210.12(A).

**Dedicated bathroom branch (C04):** NEC 2023 Article 210.11(C)(3) requires a 20 A branch dedicated to bathroom receptacle outlets (no lighting or other outlets on the circuit). Combined with 210.8(A)(1) GFCI, the breaker is a 20 A GFCI device.

**Laundry dedicated branch (C08):** NEC 2023 Article 210.11(C)(2) requires an individual 20 A branch for laundry-area receptacle outlets. NEC 2023 Article 210.8(A)(10) adds GFCI protection for the laundry area itself.

**Garage / outdoor / basement (C05/C06/C07):** Each is a single 20 A GFCI radial. The NEC does not mandate a dedicated branch for these locations (unlike laundry/bathroom), but the engineer chose separate branches for selectivity and fault-isolation purposes — a 30 m² basement on the same branch as a 33 m² garage would otherwise force a single trip event to disable both.

---

## 3. Special Locations

The schema's `special_location` enum is IEC-derived: `[null, "bathroom_zone_1", "bathroom_zone_2", "bathroom_zone_3", "outdoor", "wet_area"]`. The US NEC frames GFCI requirements by *location category* rather than by IEC bathroom zones. This is a schema gap; the engineer maps pragmatically and documents the mapping as info-level non-compliance flags.

| US category | NEC clause | Schema mapping | Rationale |
|---|---|---|---|
| Bathroom | 210.8(A)(1) | `bathroom_zone_3` | Most permissive enum; US has no zone subdivision |
| Garage | 210.8(A)(2) | `null` + info-flag | No schema enum |
| Outdoor | 210.8(A)(3) | `outdoor` | Native match |
| Basement | 210.8(A)(5) | `null` + info-flag | No schema enum |
| Kitchen | 210.8(A)(6) | `null` | Not a special location in IEC sense |
| Laundry | 210.8(A)(10) | `null` + info-flag | No schema enum |

**Bathroom mapping (210.8(A)(1)):** The US bathroom is treated as a single GFCI-protected location — there is no zone 0 (inside the tub), zone 1 (above the tub), zone 2 (1 m from tub), zone 3 (further out) subdivision. All receptacles installed within 6 ft (1.8 m) of the outside edge of a bathtub or shower fall under 210.8(A)(1). Mapping to `bathroom_zone_3` (the most permissive IEC enum) communicates: "this is a bathroom but no zone-0/1/2 restrictions apply, GFCI is the controlling protection." The single bathroom receptacle is `NEMA_5_20_tamper_resistant_GFCI` at 1100 mm AFF above the vanity counter on dedicated branch C04.

**Outdoor mapping (210.8(A)(3)):** Maps cleanly to the schema `outdoor` enum. Two NEMA 5-20 TR-WR (tamper-resistant + weather-resistant) receptacles in IP66-rated enclosures with extra-duty in-use covers per NEC 2023 Article 406.9(B)(1). The IP66 rating in the schema is the closest analogue to the US NEMA 3R / 4 / 4X + UL 514D combination typical for in-use covers; documented as design-intent.

**Garage / basement / laundry → null + info-flag:** The schema does not encode US categories. GFCI requirements per NEC 210.8(A)(2), (5), (10) apply and are documented in `compliance_summary.non_compliance_flags[]` as info-level. A future schema v1.1 may add `garage`, `basement`, `laundry_area_us` enums.

**Tamper-resistant requirement (NEC 2023 Article 406.12):** *All* 15 A and 20 A 125 V receptacles in a dwelling unit must be listed tamper-resistant. The schema's `socket.type` field is a free-form string referencing the shared ontology; the engineer encodes `_tamper_resistant` (or `_tamper_resistant_GFCI` for the bathroom in-receptacle GFCI, or `_tamper_resistant_weather_resistant` for outdoor) in every receptacle type string. All 31 receptacles are tamper-resistant.

---

## 4. RCD Posture (US: GFCI + AFCI)

This section addresses a **schema enum mismatch** explicitly.

**Schema enum:**
```
rcd_posture ∈ [
  "type_a_30ma_per_§411_3_3",
  "type_b_30ma_per_§531_3_3",
  "no_rcd_with_documented_§411_exception"
]
```

**The mismatch:** US installations do not use IEC 60364 Type A residual-current devices. They use:

- **GFCI** (Ground Fault Circuit Interrupter): trips at 4–6 mA personnel-protection threshold per UL 943. Distinct from IEC §411.3.3 Type A 30 mA equipotential-protection RCDs.
- **AFCI** (Arc Fault Circuit Interrupter): trips on arc-signature detection per UL 1699. Not a residual-current device at all.
- **Combination AFCI+GFCI dual-function breakers**: provide both, in a single device.

A literal application of the schema enum would be wrong on two counts: (a) sensitivity is 4–6 mA, not 30 mA; (b) the citation is NEC, not IEC 60364 §411.3.3.

**Pragmatic mapping (recommended Option B from the task spec):**

| Circuit | Protection | Schema rcd_posture | Schema ocpd.rcd_type | Schema ocpd.rcd_sensitivity_ma |
|---|---|---|---|---|
| C01 | AFCI+GFCI dual | `type_a_30ma_per_§411_3_3` | `GFCI` | 10 |
| C02 | AFCI+GFCI dual | `type_a_30ma_per_§411_3_3` | `GFCI` | 10 |
| C03 | AFCI only | `no_rcd_with_documented_§411_exception` | — | — |
| C04 | GFCI | `type_a_30ma_per_§411_3_3` | `GFCI` | 10 |
| C05 | GFCI | `type_a_30ma_per_§411_3_3` | `GFCI` | 10 |
| C06 | GFCI | `type_a_30ma_per_§411_3_3` | `GFCI` | 10 |
| C07 | GFCI | `type_a_30ma_per_§411_3_3` | `GFCI` | 10 |
| C08 | GFCI | `type_a_30ma_per_§411_3_3` | `GFCI` | 10 |

For GFCI-protected circuits, the engineer sets `rcd_posture="type_a_30ma_per_§411_3_3"` as the least-bad enum, but populates `ocpd.rcd_type="GFCI"` (the schema *does* offer a GFCI enum on the `rcd_type` field) and `ocpd.rcd_sensitivity_ma=10` (the smallest schema enum, since 5 mA is not available). The mapping is honest about the gap and is documented in `compliance_summary.non_compliance_flags[]` as info-level.

For C03 (AFCI only, no GFCI required outside NEC 210.8 scope), the engineer uses `rcd_posture="no_rcd_with_documented_§411_exception"` with `rcd_exception_citation` text:

> "AFCI-only circuit per NEC 2023 Article 210.12(A); no GFCI required for general receptacles outside NEC 210.8 scope (US AFCI ≠ IEC §411.3.3 Type A RCD). US AFCI provides combination arc-fault protection per UL 1699 and is functionally distinct from IEC residual-current devices."

This is the most accurate available representation. A future schema v1.1 should add a `us_gfci_5ma_per_NEC_210_8` enum and a `us_afci_per_NEC_210_12` enum to remove the gap.

---

## 5. OCPD + Cable

**Branch breakers** (all 10 kA AIC per NEC 110.9 + UL 489):

| Circuit | Rating | Device type | Schema curve | Real US curve |
|---|---|---|---|---|
| C01 | 20 A | AFCI+GFCI dual | C | Thermal-magnetic, 5-10× inst. |
| C02 | 20 A | AFCI+GFCI dual | C | Thermal-magnetic, 5-10× inst. |
| C03 | 15 A | AFCI only | C | Thermal-magnetic, 5-10× inst. |
| C04 | 20 A | GFCI | C | Thermal-magnetic, 5-10× inst. |
| C05 | 20 A | GFCI | C | Thermal-magnetic, 5-10× inst. |
| C06 | 20 A | GFCI | C | Thermal-magnetic, 5-10× inst. |
| C07 | 20 A | GFCI | C | Thermal-magnetic, 5-10× inst. |
| C08 | 20 A | GFCI | C | Thermal-magnetic, 5-10× inst. |

US residential breakers do not use the IEC 60898-1 B/C/D curve nomenclature. They are thermal-magnetic with an instantaneous magnetic trip typically in the 5-10× In range — functionally similar to an IEC Type C. The schema enum `curve ∈ ["B", "C", "D"]` is mapped to `C` as the closest analogue.

**Cable selection** (all NM-B Type, copper, with bare-copper EGC, per NEC 2023 Article 334):

| Circuits | Conductor size | Ampacity (60 °C col., Table 310.16) | Small-conductor limit | Branch rating |
|---|---|---|---|---|
| C01, C02, C04, C05, C06, C07, C08 | 12 AWG Cu | 25 A | 20 A (per 240.4(D)(5)) | 20 A ✓ |
| C03 | 14 AWG Cu | 20 A | 15 A (per 240.4(D)(3)) | 15 A ✓ |

NEC 2023 Article 240.4(D) sets *small-conductor* rules that cap 14 AWG at 15 A and 12 AWG at 20 A regardless of the Table 310.16 ampacity. Both cable choices in this design hit those exact caps.

The schema's `cable.insulation` enum is `[PVC_70, XLPE_90, EPR]`. US NM-B has a 90 °C rated conductor (THHN-equivalent), but the cable assembly itself is rated 60 °C for terminations per NEC 334.80. `PVC_70` is the closest schema enum and is used to encode the 70 °C/60 °C thermoplastic family. A future schema v1.1 could add `NM_B_us` as an explicit enum.

**Cores=3** for every cable: hot (ungrounded) + neutral (grounded) + EGC (equipment grounding conductor, bare copper in NM-B). Standard US residential branch wiring.

**Cable lengths** are end-to-end estimates for radial branches (no ring-half accounting needed in US). Final routing will be coordinated with the `cable-containment` skill.

---

## 6. Diversity + Zs

**Diversity** per NEC 2023 Article 220.40-220.55 (dwelling-unit feeder/service load calculation):

| NEC clause | Description | Load value |
|---|---|---|
| 220.52(A) | Small-appliance branches | 1500 VA each × 2 = 3000 VA |
| 220.52(B) | Laundry branch | 1500 VA |
| 220.42 | General lighting + receptacles | 3 VA/ft² × 1700 ft² = 5100 VA |
| 220.42(A) | Demand factor | first 3000 VA @ 100%, remainder @ 35% |

Per-circuit `diversified_max_load_a` values are *design-stage* estimates with engineering judgement applied. For example, the two kitchen branches are sized 12 A and 10 A — comfortably below the 20 A breaker rating but realistic for simultaneous countertop appliance use (kettle + toaster + microwave non-coincident). The schema's `diversified_max_load_a` is informational; the actual load schedule is the work of the `calc.load_schedule` skill (not yet shipped — out of scope for small-power v1.0).

**Zs / ground-fault loop impedance:** Verification is deferred to the `calc.zs_loop_impedance` skill per `WI3` (worked-implementation pattern 3 — deferred tool call). The schema requirement is:

```json
"tool_call_pending_for_zs_verification": true  // on every circuit
"flags": ["TOOL-CALL-PENDING:calc.zs_loop_impedance", ...]
```

The US equivalent of BS 7671 §411.4.5 (Zs ≤ Uo/Ia for disconnection time) is NEC 2023 Article 250.4(A)(5) (effective ground-fault current path with low enough impedance to facilitate operation of overcurrent devices). NEC 110.10 adds the compatibility-with-fault-current requirement. Both citations appear in the `compliance_summary.non_compliance_flags[]` entry for the deferred Zs verification.

---

## 7. Compliance + Assumptions

**`compliant: true`** — the design satisfies NEC 2023 for all 8 branch circuits.

**Four info-level `non_compliance_flags[]`:**

1. Schema `special_location` enum gap for US categories (garage / basement / laundry) — documented mapping noted.
2. Schema `rcd_posture` IEC-derived → US GFCI/AFCI pragmatic mapping — documented.
3. NEC 2023 Article 406.12 tamper-resistant requirement satisfied (all 31 receptacles encode `tamper_resistant`).
4. Zs verification deferred to `calc.zs_loop_impedance` per WI3.

**Nine `assumptions[]`** (summary):

- Utility Ze=0.25 Ω and PSCC=10 kA declared, not yet site-measured (verification at first energization per NEC 110.24 field-marking).
- System type schema mapping (TN-C-S for US split-phase service).
- NM-B 12 AWG / 14 AWG cable assumed; PVC_70 schema insulation encodes US thermoplastic.
- Diversity per NEC 2023 Article 220.40-220.55.
- Outdoor receptacles in extra-duty in-use covers per NEC 406.9(B)(1); IP66 closest schema analogue.
- All branch breakers UL 489 / UL 943 / UL 1699 listed.
- Drafting follows AIA CAD Layer Guidelines 2007 (Arch_D, 1/4"=1' imperial scale).

---

## 8. Drafting References

**Sheet:** Arch_D (24"×36")
**Scale:** 1/4" = 1' (imperial)
**Drawing standard:** AIA CAD Layer Guidelines 2007

The AIA CAD Layer Guidelines 2007 is the US AEC industry convention for layered electrical drawings. Layer naming follows the **Discipline-MajorGroup-MinorGroup** pattern:

| Layer | Content |
|---|---|
| `E-POWR-RECP` | Receptacles (NEMA 5-15 TR / 5-20 TR symbols) |
| `E-POWR-CIRC` | Branch circuit polylines (home-runs to MAIN-PANEL) |
| `E-POWR-PANL` | Panelboard symbol + schedule callout |
| `E-POWR-NOTE` | GFCI / AFCI legend, in-use cover notes |
| `E-POWR-WIRE` | Wiring callouts (12 AWG / 14 AWG) |
| `E-ANNO-TEXT` | General annotation |
| `E-ANNO-DIMS` | Dimensions |

A 1700 ft² single-story floor plate fits comfortably on a single Arch_D sheet at 1/4"=1' with room for the panel schedule, GFCI/AFCI legend, and notes block. A future drafting-standards deferred sprint may revisit AIA / ISO 5457 / ISO 5455 layer naming alignment.

---

## Cross-references

- Skill: `electrical/small-power/SKILL.md`
- Schema (IR): `electrical/small-power/schemas/small-power-ir.schema.json`
- Schema (intent): `electrical/small-power/schemas/small-power-intent.schema.json`
- US NEC standards layer: `shared/standards/electrical/NFPA70/part7-special-locations.json`
- Companion examples: `uk-3bed-dwelling/`, `ke-nairobi-small-office/`, `intl-open-plan-floor/`

This is the **fourth jurisdictional example** in the small-power v1.0 sprint (Tasks 7-10): UK → KE → INT → US. All four examples share the same IR shape and schema; the engineering content varies with the AHJ.
