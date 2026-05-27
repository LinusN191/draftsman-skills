# Reasoning — uk-mixed-use-lifts-and-ev

This example demonstrates Sprint D2.3 per-circuit `diversity_basis` across
**five distinct diversity rows** that previously did not coexist in any
single db-layout example: lifts, EV chargers, single AC, grouped AC, and
the existing sockets + lighting rows. The board is a realistic UK
mixed-use ground-floor sub-distribution board: 4-storey commercial ground
+ residential upper, 200 A TPN main feeding a 12-way Form 2b assembly with
9 ways used.

The walkthrough below explains each circuit's diversity decision, what
regulation/standard authorises it, and where the honest disclosures sit.

## 1. Why these load types

The example was constructed to exercise every diversity row that Sprint
D2.3 either added or tightened:

- **C01 lift motor** — the EN 81-20 §5.10 + BS 7671 Section 552 row,
  with no diversity (factor 1.00). Lifts are a regulation-driven hard
  rule per INV-15 Rule 3.
- **C02–C05 EV charge points** — the Reg 722 + IET CoP for EVCI 4th Ed
  §8.5 row, also factor 1.00 by regulation. Four EV charge points
  rotated through L1, L2, L3, L1 to keep per-phase loading balanced.
- **C06 AC single split** — engineer-declared single-compressor row
  (Section 552 motor-circuit rules applied by analogy, factor 1.00).
- **C07 AC multi-split group** — engineer-declared 100% largest + 75%
  remainder by analogy to BS 7671 Reg 552 motor diversity + industry
  practice (computed factor 0.81 for 4 × 3.5 kW).
- **C08 common-area lighting** — the IET OSG App A continuous-lighting
  row (factor 1.00).
- **C09 general sockets** — the IET OSG App A socket-outlet row (100%
  largest + 40% remainder, computed factor 0.50 for 6 × 1.0 kW).

Picking a ground-floor commercial common-area board lets all six load
types coexist on one DB without contrivance — the lift and EV chargers
serve the residential parking, the AC units serve the commercial ground
floor, and the sockets + lighting serve the common areas.

## 2. Lift diversity (EN 81-20 §5.10 + BS 7671 Section 552)

C01 is a single 3-phase lift motor + controller, 11 kW, fed through an
MCCB 32 A Curve D (the Curve D is required for the motor inrush —
typically 3–5× running current for the first 100 ms of a lift start).

**BS 7671 has no dedicated lift regulation.** The safety envelope for
lift electrical installations comes from **EN 81-20:2020 §5.10**
(electrical installation requirements for passenger and goods lifts).
The motor-circuit aspect — overcurrent protection, cable sizing, starter
characteristics — sits under **BS 7671:2018+A2:2022 Section 552**
(rotating machines). Together, EN 81-20 + Section 552 give the full
authorising basis for the factor-1.00 / no-diversity treatment:

```
diversity_basis = {
  load_type: "lift",
  factor_applied: 1.00,
  method: "no_diversity",
  citation: "EN 81-20:2020 §5.10 + BS 7671:2018+A2:2022 Section 552 …"
}
```

The engineering reason: lift starting transients dwarf the running
current; the cable + protective device must hold the starting current
plus the emergency / fire-mode duty cycle. Applying any diversity
downstream understates the cable + OCPD requirement and risks nuisance
trips or worse, undersized cable on a life-safety circuit.

A Type B RCD (300 mA sensitivity) is required because the lift VFD
produces smooth DC residual current that AC-only RCDs cannot detect.
The Type B requirement comes from **BS 7671 Reg 531.3.3** (RCD type
selection when smooth DC residual currents are present in the
installation), NOT from a Section 559 sub-clause — BS 7671 has no
Section 559 sub-rule for lifts.

For firefighters' lifts specifically, **BS EN 81-72** adds further
requirements (fire-rated supply, dual-source, dedicated rising main);
that example is not exercised here but the same factor-1.00 treatment
would apply.

## 3. EV diversity (Reg 722 + IET CoP for EVCI 4th Ed)

C02–C05 are four 7 kW Mode 3 Type 2 EV charge points. Each carries
`factor_applied: 1.00`, `method: "no_diversity"`, citing **BS 7671 Reg
722** (statutory) + the **IET Code of Practice for EV Charging
Equipment Installation (4th Ed) §8.5** (industry guidance — the
industry-standard reference for Reg 722 compliance).

The engineering reason: EV charging is treated as continuous load — the
charge cycle holds full demand for typically 4–8 hours of an overnight
session. There is no statistical basis for derating four 7 kW charge
points to less than 28 kW total demand.

Each EV circuit needs a Type B RCD at 30 mA sensitivity because Mode 3
chargers may inject DC fault current onto the supply earth (Reg
722.531.3.101).

Phase allocation: rotated L1 → L2 → L3 → L1 across C02–C05 to keep the
per-phase neutral current within acceptable balance.

## 4. AC diversity (single compressor vs multi-split group)

C06 is a **single** AC split unit at 5 kW. Per **BS 7671 Section 552**
(motor circuits, applied by analogy for the compressor motor), a single
compressor takes its full demand with no diversity (factor 1.00). The
reason: a single unit either runs or doesn't — there's no second unit
to apply statistical co-occurrence against.

C07 is an AC **multi-split group** — 4 fan coils × 3.5 kW each, sharing
one outdoor condensing unit, totalling 14 kW connected. The applied
rule is **engineer-declared 100% largest + 75% remainder** by analogy to
**BS 7671 Reg 552 motor diversity** + IET OSG App A motor section +
industry practice. **No single authoritative pinpoint clause exists in
published UK guidance for multi-split AC diversity** — the engineer-of-
record must validate against the project-specific load profile.

```
demand = 3.5 + 0.75 × (14 - 3.5)
       = 3.5 + 0.75 × 10.5
       = 3.5 + 7.875
       = 11.375 kW

factor = 11.375 / 14 = 0.8125 ≈ 0.81
```

So `factor_applied: 0.81`, `method: "largest_plus_remainder_pct"`,
`method_params: {largest_pct: 100, remainder_pct: 75}`. INV-15 Rule 4
checks that the two percentages sum to a value in [100, 200] —
100 + 75 = 175, which is in range.

The engineering reason: multi-split installations rarely run all
indoor units at simultaneous full demand under typical building thermal
load profiles. The largest zone (kitchen / sun-facing meeting room)
might pull full demand while the others modulate down via the BMS or
thermostat setpoints.

## 5. Motor citation tightening (Reg 552.1.1)

Sprint D2.3 also tightened the existing motor row citations on the
backported examples. The previous prose was "BS 7671 motor section";
the new citation is explicit: **BS 7671:2018+A2:2022 Reg 552.1.1** for
single motors and **Reg 552 + IET OSG App A motor section** for motor
groups (100% largest + 50% remainder).

The lift example (C01) sits separately because EN 81-20 §5.10 (the lift
safety standard) plus BS 7671 Section 552 (motor circuit aspects)
together provide the citation — BS 7671 has no dedicated lift
regulation.

## 6. Honest disclosure — IET CoP for EVCI status

The **IET Code of Practice for EV Charging Equipment Installation**
(4th Ed, 2020; updated 5th Ed, 2023) is **industry guidance, not
statutory law**. It is published by the IET as the industry-standard
reference for EV charging equipment installation.

However, **BS 7671 Reg 722** IS statutory (BS 7671 is the UK national
wiring standard, given legal status via the Electricity at Work
Regulations 1989 + the Building Regulations Part P). Reg 722 is the
formal regulatory basis; the IET CoP for EVCI is the industry-standard
reference engineers consult to satisfy Reg 722.

Every EV circuit's `diversity_basis.citation` in this example cites
BOTH:

```
"BS 7671:2018+A2:2022 Reg 722 (statutory) + IET Code of Practice for EV Charging Equipment Installation (4th Ed) §8.5"
```

This distinguishes the statutory basis (Reg 722) from the industry
guidance (IET CoP for EVCI) per the
[[feedback-no-trim-non-consequential]] honest-disclosure rule. The
runtime reviewer who pulls this IR sees both sources and can decide how
much weight to give each.

## 7. Honest disclosure — AC group diversity has no pinpoint clause

The **100% largest + 75% remainder rule for multi-split AC groups** is
engineering practice without a single authoritative pinpoint clause in
published UK guidance. CIBSE Guide F (Energy Efficiency in Buildings)
discusses HVAC sizing in general terms, but does not pin the specific
100+75 numerical rule. The closest published anchor is **BS 7671
Section 552 motor diversity** applied by analogy.

The `diversity_basis.citation` on C07 (the multi-split AC group) flags
this uncertainty inline:

```
"BS 7671:2018+A2:2022 Reg 552 (motor diversity, by analogy) + IET OSG
App A motor section + industry practice — 100% largest + 75% remainder
for multi-split AC groups; no single CIBSE pinpoint clause verified,
engineer-of-record must validate against project load profile."
```

The engineer-of-record is therefore put on notice: validate the 100+75
rule against the project-specific multi-split system datasheet and the
expected thermal load profile before signing off. INV-15 Rule 2
enforces that the citation contains a recognisable clause marker (in
this case `§` and `Reg`) so the honest-disclosure remains machine-
checkable across every such circuit.

## 8. Board-level demand summary

Per-circuit diversity walk:

| Circuit | Load | Type | Factor | Method | Demand |
|---|---:|---|---:|---|---:|
| C01 lift | 11.000 kW | lift | 1.00 | no_diversity | 11.000 kW |
| C02 EV CP#1 | 7.360 kW | ev_charger | 1.00 | no_diversity | 7.360 kW |
| C03 EV CP#2 | 7.360 kW | ev_charger | 1.00 | no_diversity | 7.360 kW |
| C04 EV CP#3 | 7.360 kW | ev_charger | 1.00 | no_diversity | 7.360 kW |
| C05 EV CP#4 | 7.360 kW | ev_charger | 1.00 | no_diversity | 7.360 kW |
| C06 AC single | 5.000 kW | ac_single | 1.00 | no_diversity | 5.000 kW |
| C07 AC group | 14.000 kW | ac_group | 0.81 | largest_plus_remainder_pct {100, 75} | 11.375 kW |
| C08 lighting | 2.000 kW | lighting_continuous | 1.00 | no_diversity | 2.000 kW |
| C09 sockets | 6.000 kW | socket_general | 0.50 | largest_plus_remainder_pct {100, 40} | 3.000 kW |
| **Total** | **66.440 kW connected** | — | — | — | **61.815 kW demand** |

At 400 V TPN, 0.9 pf:

```
I = 61,815 / (sqrt(3) × 400 × 0.9)
  = 61,815 / 623.54
  ≈ 99.2 A
```

The 200 A TPN main provides **~50% headroom** — generous, but appropriate
for a mixed-use building where the residential parking may double in EV
charge points over the next 5 years (and where Reg 722 + the IET CoP
for EVCI forbid applying diversity to absorb that growth).

Per-phase loading (single-phase circuits only):

- L1: C02 + C05 + C09 = 7.36 + 7.36 + 1.0 ≈ 15.7 kW
- L2: C03 + C06 = 7.36 + 5.00 ≈ 12.4 kW
- L3: C04 + C08 = 7.36 + 2.00 ≈ 9.4 kW

Plus the 3-phase circuits (C01 lift + C07 AC group) distributing
balanced load across all three phases. The single-phase imbalance
between L1 (15.7) and L3 (9.4) is ~40% but is partially absorbed by the
3-phase contributions; net neutral current is well within the 200 A main
switch capacity and the 10mm² 5-core lift / 10mm² 5-core AC group
feeders.

## INV-15 acceptance trace

- **Rule 1 PASS** — All 9 circuits carry `diversity_basis` with valid
  `load_type` enum members + `factor_applied` ∈ [0.0, 1.0] +
  `method` enum members.
- **Rule 2 PASS** — All 9 citations are ≥20 chars and contain at least
  one of `Reg / § / Table / OSG / CoP / TM`.
- **Rule 3 PASS** — 1 lift + 4 EV chargers all have
  `factor_applied == 1.00` AND `method == "no_diversity"`. Lift cites
  EN 81-20 §5.10 + BS 7671 Section 552; EV circuits cite Reg 722 +
  IET CoP for EVCI 4th Ed §8.5.
- **Rule 4 PASS** — C07 AC group `method_params` sums to 100 + 75 = 175
  ∈ [100, 200]; C09 sockets `method_params` sums to 100 + 40 = 140 ∈
  [100, 200].
