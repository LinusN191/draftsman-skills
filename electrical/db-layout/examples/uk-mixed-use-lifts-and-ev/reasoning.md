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

- **C01 lift motor** — the Reg 559 + WR9 + EN 81-20 row, with no
  diversity (factor 1.00). Lifts are a regulation-driven hard rule per
  INV-15 Rule 3.
- **C02–C05 EV charge points** — the Reg 722 + OZEV CoP §4.3 row, also
  factor 1.00 by regulation. Four EV charge points rotated through L1,
  L2, L3, L1 to keep per-phase loading balanced.
- **C06 AC single split** — the CIBSE TM50:2014 §4.2 row (single
  compressor at full demand, factor 1.00).
- **C07 AC multi-split group** — the CIBSE TM50:2014 Table 4.3 row
  (100% largest + 75% remainder, computed factor 0.81 for 4 × 3.5 kW).
- **C08 common-area lighting** — the IET OSG App A continuous-lighting
  row (factor 1.00).
- **C09 general sockets** — the IET OSG App A socket-outlet row (100%
  largest + 40% remainder, computed factor 0.55 for 6 × 1.5 kW).

Picking a ground-floor commercial common-area board lets all six load
types coexist on one DB without contrivance — the lift and EV chargers
serve the residential parking, the AC units serve the commercial ground
floor, and the sockets + lighting serve the common areas.

## 2. Lift diversity (Reg 559 + WR9 + EN 81-20)

C01 is a single 3-phase lift motor + controller, 11 kW, fed through an
MCCB 32 A Curve D (the Curve D is required for the motor inrush —
typically 3–5× running current for the first 100 ms of a lift start).
Per **BS 7671:2018+A2:2022 Reg 559** + the IET Wiring Matters issue WR9
guidance + **EN 81-20:2020 §5.10**, lift motors take their full demand
with no diversity:

```
diversity_basis = {
  load_type: "lift",
  factor_applied: 1.00,
  method: "no_diversity",
  citation: "BS 7671:2018+A2:2022 Reg 559 + IET WR9 + EN 81-20:2020 §5.10 …"
}
```

The engineering reason: lift starting transients dwarf the running
current; the cable + protective device must hold the starting current
plus the emergency / fire-mode duty cycle. Applying any diversity
downstream understates the cable + OCPD requirement and risks nuisance
trips or worse, undersized cable on a life-safety circuit. Type B RCD
(300 mA sensitivity) is required because the lift VFD produces DC
residual current that AC-only RCDs cannot detect (Reg 559.5 +
Reg 411.4.5).

## 3. EV diversity (Reg 722 + OZEV CoP + IET CoP for EVCI)

C02–C05 are four 7 kW Mode 3 Type 2 EV charge points. Each carries
`factor_applied: 1.00`, `method: "no_diversity"`, citing **BS 7671 Reg
722** (statutory) + the **OZEV Code of Practice for EV Charging
Equipment Installation §4.3** (industry guidance referenced by Reg 722)
+ the **IET CoP for EVCI 4th ed. §8.5** (industry guidance).

The engineering reason: EV charging is treated as continuous load — the
charge cycle holds full demand for typically 4–8 hours of an overnight
session. There is no statistical basis for derating four 7 kW charge
points to less than 28 kW total demand. The OZEV CoP §4.3 is explicit:
"EV charging equipment shall be considered as continuous load with no
diversity applied."

Each EV circuit needs a Type B RCD at 30 mA sensitivity because Mode 3
chargers may inject DC fault current onto the supply earth (Reg
722.531.3.101).

Phase allocation: rotated L1 → L2 → L3 → L1 across C02–C05 to keep the
per-phase neutral current within acceptable balance.

## 4. AC diversity (TM50 §4.2 single vs Table 4.3 grouped)

C06 is a **single** AC split unit at 5 kW. Per **CIBSE TM50:2014 §4.2**
+ **BS 7671 Reg 552**, a single compressor takes its full demand with no
diversity (factor 1.00). The reason: a single unit either runs or
doesn't — there's no second unit to apply statistical co-occurrence
against.

C07 is an AC **multi-split group** — 4 fan coils × 3.5 kW each, sharing
one outdoor condensing unit, totalling 14 kW connected. Per **CIBSE
TM50:2014 Table 4.3**, a multi-split group of N units may apply 100% of
the largest + 75% of the remainder:

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

The lift example (C01) sits separately because Reg 559 (lifts and
escalators) overrides Reg 552 for lift motors specifically — the
citation cites Reg 559 first.

## 6. Honest disclosure — OZEV CoP industry-guidance status

The **OZEV Code of Practice for EV Charging Equipment Installation** is
**industry guidance, not statutory law**. It was originally published by
the Office for Zero Emission Vehicles (a UK government office) as
guidance for the OLEV / EVHS grant schemes, and is now maintained as an
industry reference.

However, **BS 7671 Reg 722** IS statutory (BS 7671 is the UK national
wiring standard, given legal status via the Electricity at Work
Regulations 1989 + the Building Regulations Part P). Reg 722 explicitly
references the OZEV CoP as the engineering basis for EV charging
equipment installation.

Every EV circuit's `diversity_basis.citation` in this example cites BOTH:

```
"BS 7671:2018+A2:2022 Reg 722 + OZEV CoP §4.3 + IET CoP for EVCI 4th ed. §8.5 …"
```

This distinguishes the statutory basis (Reg 722) from the industry
guidance (OZEV CoP + IET CoP) per the
[[feedback-no-trim-non-consequential]] honest-disclosure rule. The
runtime reviewer who pulls this IR sees both sources and can decide how
much weight to give each.

## 7. Honest disclosure — CIBSE TM50:2014 paywall

**CIBSE TM50:2014** (the multi-split AC diversity table) is behind the
CIBSE publication paywall. The engineer-of-record cannot rely on an
unpublished reproduction of the table; they must purchase or have CIBSE
membership access.

The `diversity_basis.citation` on C07 (the multi-split AC group) cites
the table number explicitly:

```
"CIBSE TM50:2014 Table 4.3 — multi-split AC group: 100% largest + 75% remainder. …"
```

This lets the engineer-of-record verify the table content against the
published edition before signing off the design. INV-15 Rule 2 enforces
that the citation contains a recognisable clause marker (in this case
"Table") so the paywall disclosure remains machine-checkable across
every TM-cited circuit.

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
| C09 sockets | 6.000 kW | socket_general | 0.55 | largest_plus_remainder_pct {100, 40} | 3.300 kW |
| **Total** | **66.440 kW connected** | — | — | — | **62.115 kW demand** |

At 400 V TPN, 0.9 pf:

```
I = 62,115 / (sqrt(3) × 400 × 0.9)
  = 62,115 / 623.54
  ≈ 99.7 A
```

The 200 A TPN main provides **~50% headroom** — generous, but appropriate
for a mixed-use building where the residential parking may double in EV
charge points over the next 5 years (and where the OZEV CoP forbids
applying diversity to absorb that growth).

Per-phase loading (single-phase circuits only):

- L1: C02 + C05 + C09 = 7.36 + 7.36 + 1.5 ≈ 16.2 kW
- L2: C03 + C06 = 7.36 + 5.00 ≈ 12.4 kW
- L3: C04 + C08 = 7.36 + 2.00 ≈ 9.4 kW

Plus the 3-phase circuits (C01 lift + C07 AC group) distributing
balanced load across all three phases. The single-phase imbalance
between L1 (16.2) and L3 (9.4) is ~43% but is partially absorbed by the
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
  `factor_applied == 1.00` AND `method == "no_diversity"`.
- **Rule 4 PASS** — C07 AC group `method_params` sums to 100 + 75 = 175
  ∈ [100, 200]; C09 sockets `method_params` sums to 100 + 40 = 140 ∈
  [100, 200].
