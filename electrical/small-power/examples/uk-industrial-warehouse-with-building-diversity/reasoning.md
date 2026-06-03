# Reasoning — uk-industrial-warehouse-with-building-diversity (C.6)

## Scope

Sprint D4 Phase C.6 example. UK 1200 m² single-occupant industrial
warehouse on Leeds Enterprise Park (single-tenant, single-storey;
modest manufacturing + finished-goods dispatch). The 1200 m² envelope
splits into a 950 m² warehouse floor (forklift movement + racking + 2
production-line bays), a 150 m² office partition adjacent to the
loading bay (8 admin workstations + kitchenette + WC), a 60 m² loading
bay (goods-in/out under a 4 m roller door), and a 40 m² plant alcove
(UPS-fed dispatch comms cabinet + DB-WH-01 distribution board).

PRIMARY purpose: exercise the v2.0 `building_diversity` IR field on
the **INDUSTRIAL** profile (BLD-02 — distinct from C.5's office
profile BLD-01) AND demonstrate the **DIV-NN EXCLUSION** discipline
from D1 (motor superposition) + D2.3 (lift coordination). The
industrial profile per the verified BS 7671 + IET OSG App A Table A1
standards file
(`shared/standards/electrical/BS7671/diversity-factors.json::industrial_diversity`)
applies diversity at the **SUBSTATION level** based on demand history
— NOT at individual motor circuit level. Motor circuits are sized at
100% FLC per the IET OSG App A `industrial_motor_duty` entry; lift
loads sit OUTSIDE the per-floor `building_diversity` scope per the
D2.3 lift-coordination rule (lifts compose separately via the
`office_lift_*` family at the upstream MCC hop).

## §1 — Jurisdiction + supply

- **GB** jurisdiction; BS 7671:2018+A2:2022 + IET On-Site Guide 8th
  Edition apply.
- Utility TN-S 400V TPN+E supply at the DB-WH-01 busbar with declared
  Ze=0.18 Ω and PSCC=16 kA. The 16 kA PSCC reflects a typical
  industrial-park supply (shorter mains feeder from the substation
  than the floor-submain commercial supply in C.5).
- §434.5.1 sets the short-circuit verification rule — all RCBOs Icu ≥
  16 kA via the BS EN 61009-1 product range.

## §2 — Circuit inventory (8 circuits)

| ID  | Topology         | OCPD                  | Cable                          | Load                                                      | In `applies_load_types[]`? |
| --- | ---------------- | --------------------- | ------------------------------ | --------------------------------------------------------- | -------------------------- |
| C01 | ring             | 32 A RCBO Type B + A  | 2.5 mm² T+E PVC (42 m)         | Office partition ring (8 BS 1363 doubles)                 | YES (office workstation)   |
| C02 | radial           | 20 A RCBO Type C + A  | 2.5 mm² T+E PVC (24 m)         | Kitchenette + 2 FCU spurs                                 | YES (office kitchenette)   |
| C03 | radial           | 20 A RCBO Type C + A  | 2.5 mm² T+E PVC (55 m)         | Warehouse high-bay + GP sockets                           | YES (industrial high-bay)  |
| C04 | dedicated_radial | 20 A RCBO Type C + B  | 2.5 mm² T+E PVC (18 m)         | Dispatch UPS comms cabinet                                | YES (industrial comms)     |
| C05 | dedicated_radial | 32 A RCBO Type D + A  | 4 mm² SWA XLPE (32 m, 5-core)  | Process motor M-01 (11 kW pillar drill)                   | **NO — EXCLUDED**          |
| C06 | dedicated_radial | 32 A RCBO Type D + A  | 4 mm² SWA XLPE (36 m, 5-core)  | Process motor M-02 (11 kW sheet-metal shear)              | **NO — EXCLUDED**          |
| C07 | dedicated_radial | 40 A RCBO Type D + B  | 6 mm² SWA XLPE (28 m, 5-core)  | Goods lift LF-01 (5-person 630 kg)                        | **NO — EXCLUDED**          |
| C08 | dedicated_radial | 32 A RCBO Type C + B  | 4 mm² SWA XLPE (22 m, 5-core)  | Forklift battery charging (3× BS EN 1175-2 chargers)      | YES (industrial charging)  |

## §3 — Building diversity (NEW v2.0, INDUSTRIAL profile + DIV-NN exclusion)

### §3.1 — Profile resolution

Industrial profile resolved from the verified
`diversity-factors.json::industrial_diversity` entry:

```text
rule_of_thumb: Apply diversity at the SUBSTATION level based on
demand history, not at individual circuit level. Each motor or
process is sized at its own rating.
```

This rule is the engineering anchor for the DIV-NN exclusion below.

### §3.2 — `applies_load_types[]` manifest (5 in-scope families)

The `applies_load_types[]` array LISTS ONLY the 5 office-style +
industrial-non-motor + battery-charger + comms families:

1. `office_small_power_workstation` → C01 office partition ring
2. `office_lighting` → folded into C03 high-bay (notional)
3. `office_kitchenette` → C02 kitchenette
4. `industrial_high_bay_lighting` → C03 warehouse high-bay
5. `industrial_battery_charging` → C08 forklift charging
6. `industrial_comms_cabinet_ups` → C04 dispatch UPS

These 5 in-scope families receive the `building_factor = 0.70` per
the industrial profile.

### §3.3 — Excluded families (DIV-NN discipline)

The 3 EXCLUDED circuits NEVER appear in `applies_load_types[]`:

- **C05** (industrial_motor_duty, 11 kW pillar drill, 21.0 A FLC)
- **C06** (industrial_motor_duty, 11 kW sheet-metal shear, 21.0 A FLC)
- **C07** (office_lift_single, 14 kW goods lift, 24.0 A FLC)

Anchors for the exclusion:

| Excluded family       | Verified anchor                                                                                   |
| --------------------- | ------------------------------------------------------------------------------------------------- |
| industrial_motor_duty | `industrial_motor_duty.diversity_pct=100` + `industrial_diversity.rule_of_thumb` (substation level) |
| office_lift_single    | `office_lift_single.diversity_pct=100` + cross-skill DIV-NN lift coordination rule from D2.3      |

**CRITICAL: Banned-citation discipline held.** The D2.3 sprint caught
a Reg 559 misattribution for lift diversity scope (banned — sub-clause
not transcribed as a lift-diversity authority). Reg 559 covers
luminaires (luminaire installation requirements), banned for lift
diversity. The correct anchor for the lift exclusion is the IET OSG
App A Table A1 `office_lift_single.diversity_pct=100` entry + the
cross-skill DIV-NN lift coordination rule. **This example never cites
Reg 559 (banned per the C.6 task brief).**

### §3.4 — Arithmetic

```text
In-scope per_circuit_demand_inputs[]:
  C01:  18.5 A × 0.70 = 12.95 A
  C02:   9.6 A × 0.70 =  6.72 A
  C03:  19.6 A × 0.70 = 13.72 A
  C04:  14.4 A × 0.70 = 10.08 A
  C08:  22.5 A × 0.70 = 15.75 A
                ────────────────
Σ in-scope post = 84.6 A
× building_factor 0.70  = 59.22 A mathematical product
Recorded building_diversified_demand_a = 59.0 A
Drift = (59.22 − 59.0) / 59.22 = 0.37% < 5% → INV-13 sub-check 3 PASS

Excluded radials (algebraic add at upstream switchboard):
  C05 motor:  21.0 A
  C06 motor:  21.0 A
  C07 lift:   24.0 A
                  ───────
Σ excluded = 66.0 A

Submain target = 59.0 + 66.0 = 125.0 A
Next ascending standard MCB = 125 A
```

### §3.5 — `future_expansion_pct=30` carry-forward

The 30% growth allowance is carried as a separate field on
`building_diversity.future_expansion_pct`, NOT folded into
`building_diversified_demand_a`. This keeps the upstream submain
sizing skill transparent about the headroom basis: the engineer-of-
record at the next hop can choose whether to apply the 30% factor at
the substain MCB sizing step OR at the upstream MCC busbar sizing
step, depending on the project's commissioning + future-fit-out plan.

## §4 — Cable-sizing cascade (INV-19)

### §4.1 — DEFERRED-POINTER pattern

`consumed_intents.cable_sizing.source_path` points at a producer-side
fixture that does NOT yet exist at C.6-ship:

```text
electrical/cable-sizing/examples/uk-warehouse-submain-wh01/intent-out.json
```

The `payload` is INLINED at C.6-ship with 8 circuit entries (one per
small-power IR circuit, INCLUDING the 3 EXCLUDED-from-building_diversity
motor + lift circuits). Honest 4-place disclosure of this pattern:

1. `input.json::_cascade_disclosure` — names the DEFERRED-POINTER pattern + the byte-identity promise
2. `output.json::compliance_summary.assumptions[]` — names the DEFERRED-POINTER pattern
3. `output.json::compliance_summary.non_compliance_flags[]` — info entry on INV-19 PASS
4. `output.json::rationale.sections[].decisions[]` — DEFERRED-POINTER decision block in the cable-sizing-cascade section

### §4.2 — INV-19 reconciliation (PASS on all 8 circuits)

INV-19 reconciles per-circuit demand vs cable_sizing payload across
all 8 circuits. The EXCLUDED-from-`building_diversity` discipline
applies ONLY to the `applies_load_types[]` manifest and the
`building_diversified_demand_a` aggregate — NOT to the per-circuit
cable-sizing cascade reconciliation.

| Circuit | small-power IR diversified_max_load_a | cable_sizing design_current_a | Drift |
| ------- | ------------------------------------- | ----------------------------- | ----- |
| C01     | 18.5                                  | 18.5                          | 0.0%  |
| C02     |  9.6                                  |  9.6                          | 0.0%  |
| C03     | 19.6                                  | 19.6                          | 0.0%  |
| C04     | 14.4                                  | 14.4                          | 0.0%  |
| C05     | 21.0                                  | 21.0                          | 0.0%  |
| C06     | 21.0                                  | 21.0                          | 0.0%  |
| C07     | 24.0                                  | 24.0                          | 0.0%  |
| C08     | 22.5                                  | 22.5                          | 0.0%  |

All 8 within ±5% tolerance. **INV-19 PASS.**

## §5 — RCD posture

5 of 8 circuits use Type A 30 mA per §411.3.3 (general socket-outlet +
motor radials — motors do not present DC-leakage that blinds Type A).
3 of 8 circuits use Type B 30 mA per §531.3.3:

- **C04** dispatch UPS comms (SMPS DC-leakage)
- **C07** goods lift (VFD smooth DC residual per BS EN 61800-5-1)
- **C08** forklift battery charging (SMPS charger DC-leakage)

## §6 — Compliance summary

`compliant=true`. 8 non_compliance_flags entries (ALL info severity —
no D-8 warning since the engineer's recorded 59.0 A reconciles within
±5% of the mathematical 59.22 A).

12 assumptions documented including:

- The DEFERRED-POINTER cable-sizing cascade pattern
- The future_expansion_pct=30 carry-forward separate-field discipline
- The banned-citation discipline holds (banned tokens listed in §8: Reg 559, §526.2, §433.2, OZEV, 3rd Edition — banned per task brief)
- The DIV-NN exclusion rationale citing IET OSG App A Table A1
  `industrial_motor_duty.diversity_pct=100` +
  `office_lift_single.diversity_pct=100` entries

## §7 — Invariants summary

All 19 INVs PASS:

- **INV-01..INV-04** — ring + RCD + topology — all PASS
- **INV-05** — room/circuit coverage — PASS
- **INV-06..INV-08** — curve + headroom + Zs — all PASS
- **INV-09..INV-11** — orphan check + drawing standard + cable-sizing cascade — all PASS
- **INV-12** — Part-7 zoning (N/A — no Part-7 rooms) — trivially PASS
- **INV-13** — `building_diversity` self-consistency (industrial profile, drift 0.37%) — **PASS**
- **INV-14** — Ring continuity (C01 endpoints + mcb_way_id consistent) — PASS
- **INV-15** — Per-circuit floor-area cross-check (N/A — floor_area_m2 not populated) — trivially PASS
- **INV-16** — OCPD-topology coordination — PASS on all 8 circuits
- **INV-17** — AMD 2 FCU spur modelling (N/A — kitchenette FCUs modelled at the room level) — trivially PASS
- **INV-18** — EV RCD selection (N/A — no EV charging) — trivially PASS
- **INV-19** — Cable-sizing cascade integration (8/8 circuits within ±5%) — **PASS**

## §8 — Banned-citation discipline (C.6 task brief)

The C.6 task brief explicitly bans the following citations:

| Banned token       | Reason                                                                                |
| ------------------ | ------------------------------------------------------------------------------------- |
| §526.2             | Sub-clause not transcribed in the verified BS 7671 file — only §526 top-level         |
| §433.2             | Sub-clause not transcribed in the verified file — use §433.1.1 instead                |
| OZEV               | banned — OZEV is the UK EV charging grant body, not a citation source                 |
| 3rd Edition (CoP)  | banned — use IET CoP for EV 4th Edition where EV citation needed                      |
| Reg 559            | banned — D2.3 lift-diversity misattribution catch (Reg 559 covers luminaires)         |

This example's banned-token grep returns **PASS** — banned tokens
appear ONLY in disambiguation contexts (e.g. "never cite Reg 559" /
"sub-clause not transcribed" / "banned per the C.6 task brief").

## §9 — Wiring to upstream submain skill

The upstream switchboard / submain sizing skill consumes this
example's `building_diversity` block AND adds the EXCLUDED motor +
lift currents ALGEBRAICALLY:

```text
Submain Ib_3ph = building_diversified_demand_a
                 + Σ(excluded motor + lift radials)
               = 59.0 + 21.0 + 21.0 + 24.0
               = 125.0 A
Next standard MCB = 125 A
```

The `future_expansion_pct=30` is carried as a separate field; the
upstream submain skill decides whether to fold it in at the submain
MCB sizing step OR carry it further up to the MCC busbar sizing step.

## §10 — Cross-skill cascade contract

This example demonstrates the **2-way cascade contract** between the
small-power skill (consumer) and:

1. **cable-sizing skill (producer)** — via `consumed_intents.cable_sizing.payload`
2. **upstream submain switchboard skill (consumer of small-power)** —
   via `building_diversity.building_diversified_demand_a` +
   `_excluded_circuit_inputs[]` algebraic sum

The DIV-NN exclusion discipline ensures the upstream submain skill
receives a clean separation of (a) the in-scope diversity-reduced
demand AND (b) the EXCLUDED motor + lift contributions that compose
algebraically, so the submain skill can apply its own substation-
level diversity (if any) without double-counting.

---

End of reasoning. C.6 PASS criteria:
- 4 files created
- output.json validates against IR schema (Draft-07)
- All 19 INVs PASS
- building_diversity block: profile=industrial + factor 0.70 + 5 in-scope load types
- DIV-NN exclusion discipline (motor + lift NOT in applies_load_types[], cited via IET OSG App A Table A1 + DIV-NN cross-skill rule)
- coincident_demand traceable (Σ × 0.70 = 59.22 A → 59.0 A recorded → algebraic add yields 125.0 A submain target)
- Banned-citation grep PASS (banned tokens only in disambiguation contexts; never cite as authority)
- Gates 326 → 328 (+2 new examples: input.json + output.json on disk; ).
